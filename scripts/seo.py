"""Page-specific metadata and linked structured data; no third-party packages."""
from html import escape
import json

DOMAIN = 'https://digitaltalha.com'
ARTICLE = '/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/'


def trail(path, metadata):
    crumbs = [('Home', '/')]
    if path == '/':
        return crumbs
    if metadata[path].get('service'):
        crumbs.append(('Services', '/services/'))
    if metadata[path].get('article'):
        crumbs.append(('Projects', '/blog/'))
    return crumbs + [(metadata[path]['label'], path)]


def breadcrumb(path, metadata):
    parts = []
    crumbs = trail(path, metadata)
    for index, (name, url) in enumerate(crumbs):
        label = escape(name)
        parts.append(f'<span aria-current="page">{label}</span>' if index == len(crumbs)-1
                     else f'<a href="{url}">{label}</a>')
    separator = ' <span aria-hidden="true">/</span> '
    return '<nav class="breadcrumb" aria-label="Breadcrumb">' + separator.join(parts) + '</nav>'


def structured_data(path, metadata):
    config = metadata[path]
    url = DOMAIN + path
    person_id, site_id = DOMAIN + '/#person', DOMAIN + '/#website'
    page_id = url + '#webpage'
    person = {
        '@type': 'Person', '@id': person_id, 'name': 'Talha Alam',
        'url': DOMAIN + '/about/', 'jobTitle': 'Freelance digital marketer',
        'image': DOMAIN + '/assets/talha-portrait.webp',
        'sameAs': ['https://www.instagram.com/_digitaltalha_/',
                   'https://www.linkedin.com/in/talha-alam-798st0/']
    }
    website = {
        '@type': 'WebSite', '@id': site_id, 'name': 'DigitalTalha',
        'alternateName': 'Digital Talha', 'url': DOMAIN + '/',
        'publisher': {'@id': person_id}, 'inLanguage': 'en-IN'
    }
    webpage = {
        '@type': config.get('type', 'WebPage'), '@id': page_id,
        'url': url, 'name': config['title'] + ' | DigitalTalha',
        'description': config['description'], 'isPartOf': {'@id': site_id},
        'inLanguage': 'en-IN'
    }
    graph = [person, website, webpage]
    if path != '/' and not config.get('noindex'):
        graph.append({
            '@type': 'BreadcrumbList', '@id': url + '#breadcrumb',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i+1, 'name': name, 'item': DOMAIN + route}
                for i, (name, route) in enumerate(trail(path, metadata))
            ]
        })
        webpage['breadcrumb'] = {'@id': url + '#breadcrumb'}
    if path in ['/', '/about/']:
        webpage['about'] = {'@id': person_id}
    if path == '/about/':
        webpage['mainEntity'] = {'@id': person_id}
    service_paths = [p for p, values in metadata.items() if values.get('service')]
    if config.get('service') or path == '/services/':
        for service_path in ([path] if config.get('service') else service_paths):
            service = metadata[service_path]
            graph.append({
                '@type': 'Service', '@id': DOMAIN + service_path + '#service',
                'name': service['service'], 'serviceType': service['service'],
                'url': DOMAIN + service_path, 'description': service['description'],
                'provider': {'@id': person_id},
                'areaServed': {'@type': 'Country', 'name': 'India'}
            })
        if config.get('service'):
            webpage['mainEntity'] = {'@id': url + '#service'}
        else:
            webpage['mainEntity'] = {
                '@type': 'ItemList', 'itemListElement': [
                    {'@type': 'ListItem', 'position': i+1,
                     'item': {'@id': DOMAIN + p + '#service'}}
                    for i, p in enumerate(service_paths)
                ]
            }
    if config.get('article'):
        graph.append({
            '@type': 'BlogPosting', '@id': url + '#article', 'url': url,
            'headline': 'Meta Lead Campaign — From Start to Finish',
            'description': config['description'], 'author': {'@id': person_id},
            'publisher': {'@id': person_id}, 'mainEntityOfPage': {'@id': page_id},
            'image': DOMAIN + '/assets/meta-campaign.webp', 'inLanguage': 'en-IN',
            'articleSection': 'Digital marketing practice projects'
        })
        webpage['mainEntity'] = {'@id': url + '#article'}
    if path == '/blog/':
        webpage['mainEntity'] = {
            '@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'url': DOMAIN + ARTICLE,
                 'name': 'Meta Lead Campaign — From Start to Finish'}
            ]
        }
    return json.dumps({'@context': 'https://schema.org', '@graph': graph},
                      ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


def head(path, metadata, noindex=False, staging=False):
    config = metadata[path]
    title = config['title'] + ' | DigitalTalha'
    description = config['description']
    url = DOMAIN + path
    robots = 'noindex, follow' if noindex or config.get('noindex') or staging else 'index, follow, max-image-preview:large'
    article = config.get('article')
    image = 'meta-campaign.webp' if article else 'service-characters.webp'
    width, height = (1200, 677) if article else (1881, 836)
    image_alt = 'UrbanFit Meta lead-generation practice campaign in Ads Manager' if article else 'Illustrations of Google Ads, Meta Ads and website creation services'
    e = lambda value: escape(str(value), quote=True)
    preload = ''
    if path == '/about/':
        preload = '<link rel="preload" as="image" href="/assets/talha-portrait.webp" fetchpriority="high">'
    elif path not in [ARTICLE, '/privacy-policy/', '/terms-conditions/', '/404/']:
        preload = '<link rel="preload" as="image" href="/assets/service-characters.webp" fetchpriority="high">'
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f8f7f3"><title>{e(title)}</title>
<meta name="description" content="{e(description)}"><meta name="robots" content="{robots}">
<link rel="canonical" href="{e(url)}"><meta name="author" content="Talha Alam">
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:site_name" content="DigitalTalha">
<meta property="og:locale" content="en_IN"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{DOMAIN}/assets/{image}"><meta property="og:image:type" content="image/webp">
<meta property="og:image:width" content="{width}"><meta property="og:image:height" content="{height}"><meta property="og:image:alt" content="{e(image_alt)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{DOMAIN}/assets/{image}"><meta name="twitter:image:alt" content="{e(image_alt)}">
<link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon-192.png"><link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{preload}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&amp;display=swap">
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/motion.css">
<script type="application/ld+json">{structured_data(path, metadata)}</script>
<script defer src="/assets/site.js"></script><script defer src="/assets/motion.js"></script>'''
