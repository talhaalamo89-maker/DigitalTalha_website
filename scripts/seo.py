"""Page-specific metadata and linked structured data; no third-party packages."""
from html import escape
from cms_content import asset_info, asset_path, load_services, read_json
import json

DOMAIN = 'https://digitaltalha.com'
ARTICLE = '/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/'
PROFILE = read_json('pages/profile.json')
PROJECT = read_json('hospital-project.json')
PORTRAIT_SRC = asset_path(PROFILE['image'])
PORTRAIT_VARIANTS = (240, 420, 680)
PORTRAIT_SRCSET = ', '.join(
    [f'/assets/talha-portrait-{width}.webp {width}w' for width in PORTRAIT_VARIANTS]
    + [f'{PORTRAIT_SRC} 900w']
) if PORTRAIT_SRC == '/assets/talha-portrait.webp' else ''
PORTRAIT_SIZES = {
    '/': '(max-width: 600px) 110px, 370px',
    '/about/': '(max-width: 380px) calc(100vw - 40px), 340px',
}
SERVICE_IMAGES = {service['route']: asset_path(service['image']) for service in load_services().values()}
POPPINS = 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&amp;display='


def trail(path, metadata):
    crumbs = [('Home', '/')]
    if path == '/':
        return crumbs
    if metadata[path].get('service'):
        crumbs.append(('Services', '/services/'))
    if metadata[path].get('article') or metadata[path].get('project'):
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
        'image': DOMAIN + PORTRAIT_SRC,
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
                'areaServed': ({'@type': 'City', 'name': service['area_served']}
                               if service.get('area_served') else {'@type': 'Country', 'name': 'India'})
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
            'headline': config['headline'],
            'description': config['description'], 'author': {'@id': person_id},
            'publisher': {'@id': person_id}, 'mainEntityOfPage': {'@id': page_id},
            'image': DOMAIN + asset_path(config.get('image') or ('service-characters.webp' if config.get('blog_post') else 'meta-campaign.webp')), 'inLanguage': 'en-IN',
            'articleSection': 'Digital marketing' if config.get('blog_post') else 'Digital marketing practice projects',
            'datePublished': config['date_published']
        })
        webpage['mainEntity'] = {'@id': url + '#article'}
    if config.get('project'):
        graph.append({
            '@type': 'CreativeWork', '@id': url + '#project', 'url': url,
            'name': config['title'], 'description': config['description'],
            'creator': {'@id': person_id}, 'mainEntityOfPage': {'@id': page_id},
            'image': DOMAIN + asset_path(config.get('image') or PROJECT['desktop']['file']), 'inLanguage': 'en-IN',
            'genre': 'Website project',
            'isBasedOn': {'@type': 'WebSite', 'url': config['project_url']}
        })
        webpage['mainEntity'] = {'@id': url + '#project'}
    if path == '/blog/':
        projects = [(p, c) for p, c in metadata.items() if c.get('project')]
        projects += [(p, c) for p, c in metadata.items() if c.get('article')]
        webpage['mainEntity'] = {
            '@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': i+1, 'url': DOMAIN + route,
                 'name': values['title']} for i, (route, values) in enumerate(projects)
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
    legacy_article = article and not config.get('blog_post')
    default_image = 'meta-campaign.webp' if legacy_article else 'service-characters.webp'
    image, width, height, mime = asset_info(config.get('image') or default_image)
    if config.get('image') and not (config.get('image_alt') or '').strip():
        raise ValueError(f'{path}: add alt text for the social sharing image')
    image_alt = config.get('image_alt') or ('UrbanFit Meta lead-generation practice campaign in Ads Manager' if legacy_article else 'Illustrations of Google Ads, Meta Ads and website creation services')
    e = lambda value: escape(str(value), quote=True)
    preload = ''
    if path in PORTRAIT_SIZES and PORTRAIT_SRCSET:
        preload = (f'<link rel="preload" as="image" imagesrcset="{PORTRAIT_SRCSET}" '
                   f'imagesizes="{PORTRAIT_SIZES[path]}" fetchpriority="high">')
    elif path in PORTRAIT_SIZES:
        preload = f'<link rel="preload" as="image" href="{PORTRAIT_SRC}" fetchpriority="high">'
    elif config.get('service'):
        # Service art is the LCP candidate even when the social card uses a different image.
        preload = f'<link rel="preload" as="image" href="{e(SERVICE_IMAGES[path])}" fetchpriority="high">'
    published = f'<meta property="article:published_time" content="{e(config['date_published'])}">' if article else ''
    # A late font swap moves the homepage portrait when the hero text rewraps.
    if path == '/':
        fonts = f'<link rel="stylesheet" href="{POPPINS}optional">'
    else:
        fonts = f'''<link rel="stylesheet" href="{POPPINS}swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="{POPPINS}swap"></noscript>'''
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f8f7f3"><title>{e(title)}</title>
<meta name="description" content="{e(description)}"><meta name="robots" content="{robots}">
<link rel="canonical" href="{e(url)}"><meta name="author" content="Talha Alam">
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:site_name" content="DigitalTalha">
<meta property="og:locale" content="en_IN"><meta property="og:title" content="{e(title)}">{published}
<meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{DOMAIN}{image}"><meta property="og:image:type" content="{mime}">
<meta property="og:image:width" content="{width}"><meta property="og:image:height" content="{height}"><meta property="og:image:alt" content="{e(image_alt)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{DOMAIN}{image}"><meta name="twitter:image:alt" content="{e(image_alt)}">
<link rel="icon" href="/assets/favicon-192.png" type="image/png" sizes="192x192"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" sizes="any">
<link rel="apple-touch-icon" href="/assets/favicon-192.png"><link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{preload}
<link rel="stylesheet" href="/assets/site.css">
{fonts}
<script type="application/ld+json">{structured_data(path, metadata)}</script>
<script defer src="/assets/site.js"></script>'''

