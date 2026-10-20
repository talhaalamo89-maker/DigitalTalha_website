"""Validate production metadata, schema links, crawlability and preview isolation."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
DOMAIN = 'https://digitaltalha.com'
CONFIG = json.loads((ROOT / 'content/seo.json').read_text())
STAGING = '--staging' in sys.argv


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.canonicals = []
        self.schemas = []
        self.schema_text = None
        self.title = ''
        self.in_title = False
        self.images = []
        self.links = []
        self.crumb_labels = []
        self.in_crumb = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            key = attrs.get('name', attrs.get('property'))
            self.meta.setdefault(key, []).append(attrs.get('content', ''))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.schema_text = ''
        if tag == 'title':
            self.in_title = True
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag == 'nav' and attrs.get('aria-label') == 'Breadcrumb':
            self.in_crumb = True

    def handle_data(self, data):
        if self.schema_text is not None:
            self.schema_text += data
        if self.in_title:
            self.title += data
        if self.in_crumb:
            self.crumb_labels.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.schema_text is not None:
            self.schemas.append(json.loads(self.schema_text))
            self.schema_text = None
        if tag == 'title':
            self.in_title = False
        if tag == 'nav':
            self.in_crumb = False


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


pages = {}
for route, config in CONFIG.items():
    source = (DIST / route.strip('/') / 'index.html').read_text()
    page = Page(source)
    pages[route] = page
    assert page.title == config['title'] + ' | DigitalTalha', (route, 'title')
    assert page.canonicals == [DOMAIN + route], (route, 'canonical')
    required = ['description', 'robots', 'og:title', 'og:description', 'og:url',
                'og:type', 'og:site_name', 'og:image', 'og:image:alt',
                'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
    for key in required:
        assert len(page.meta.get(key, [])) == 1, (route, key)
    assert page.meta['description'] == [config['description']], route
    assert page.meta['og:title'] == [page.title], route
    assert page.meta['og:description'] == page.meta['description'], route
    assert page.meta['twitter:description'] == page.meta['description'], route
    assert page.meta['og:url'] == [DOMAIN + route], route
    assert 80 <= len(config['description']) <= 180, (route, 'description length')
    assert ('noindex' in page.meta['robots'][0]) == bool(STAGING or config.get('noindex')), route
    for image in page.images:
        assert 'alt' in image, (route, 'missing image alt')
        assert image.get('width') and image.get('height'), (route, 'image dimensions')
    assert len(page.schemas) == 1, route
    nodes = page.schemas[0]['@graph']
    all_nodes = list(walk(nodes))
    ids = {node['@id'] for node in all_nodes if '@id' in node and len(node) > 1}
    for node in all_nodes:
        if '@id' in node and len(node) == 1:
            assert node['@id'] in ids, (route, 'unresolved schema reference', node)
        assert not any(key in node for key in ['aggregateRating', 'review', 'datePublished', 'dateModified']), (route, 'unverified facts')
    page_node = next(node for node in nodes if node.get('@id') == DOMAIN + route + '#webpage')
    assert page_node['url'] == DOMAIN + route, route
    assert page_node['description'] == config['description'], route
    if config.get('service'):
        assert any(node.get('@type') == 'Service' and node['name'] == config['service'] for node in nodes), route
    if config.get('article'):
        assert any(node.get('@type') == 'BlogPosting' for node in nodes), route
    if route != '/' and not config.get('noindex'):
        crumb = next(node for node in nodes if node.get('@type') == 'BreadcrumbList')
        visible = ' '.join(page.crumb_labels)
        assert crumb['itemListElement'][-1]['item'] == DOMAIN + route, route
        for entry in crumb['itemListElement']:
            assert entry['name'] in visible, (route, 'breadcrumb mismatch')
    social = urlsplit(page.meta['og:image'][0])
    assert social.netloc == 'digitaltalha.com' and (DIST / social.path.lstrip('/')).is_file(), route

for field in ['title', 'description']:
    values = [config[field] for config in CONFIG.values()]
    assert all(count == 1 for count in Counter(values).values()), ('duplicate', field)

root = ET.parse(DIST / 'sitemap.xml').getroot()
urls = [item.text for item in root.findall('{*}url/{*}loc')]
expected = [] if STAGING else [DOMAIN+p for p, c in CONFIG.items() if not c.get('noindex')]
assert sorted(urls) == sorted(expected) and len(set(urls)) == len(urls), 'sitemap'
for url in urls:
    route = urlsplit(url).path
    assert pages[route].canonicals == [url] and 'noindex' not in pages[route].meta['robots'][0], url
    if route != '/':
        assert any(route in p.links for p in pages.values()), ('orphan page', route)
robots = (DIST / 'robots.txt').read_text()
assert 'Disallow: /\n' not in robots and 'Disallow: /api/' in robots, 'robots'
assert ('Sitemap: '+DOMAIN+'/sitemap.xml' in robots) != STAGING, 'staging sitemap'
for alias, target in {'about-us':'about', 'contact-us':'contact', 'service':'services', 'projects':'blog'}.items():
    document = Page((DIST/alias/'index.html').read_text())
    assert document.canonicals == [DOMAIN+'/'+target+'/'], alias
    assert 'noindex' in document.meta['robots'][0], alias

preview = Page((ROOT / 'DigitalTalha-preview.html').read_text())
assert preview.meta['robots'] == ['noindex, follow'], 'preview must not be indexed'
assert '@import' not in (ROOT/'assets/site.css').read_text(), 'avoid font stylesheet request chain'
assert (DIST/'assets/service-characters.webp').stat().st_size < 350000, 'artwork budget'
print(f'PASS: {len(pages)} pages; unique metadata, canonical URLs, linked JSON-LD, breadcrumbs, sitemap, crawl rules, image attributes and preview noindex ({"staging" if STAGING else "production"}).')
