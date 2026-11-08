"""Build and verify bounded release bundles. Never send a valid enquiry."""
from pathlib import Path, PurePosixPath
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit, parse_qsl
import argparse
import hashlib
import json
import re
import stat
import zipfile

MAX_ARCHIVE = 20 * 1024 * 1024
MAX_CONTENT = 50 * 1024 * 1024
RELEASE = re.compile(r'\.digitaltalha-release-[a-f0-9]{12}-[0-9]{1,14}-[0-9]{1,4}')
SHORTLINKS = {'454':'/about/', '456':'/contact/', '458':'/terms-conditions/', '460':'/privacy-policy/', '484':'/services/', '504':'/blog/', '605':'/google-ads/', '607':'/meta-ads/', '782':'/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def package(root, mode, commit, run, output):
    require(re.fullmatch(r'[a-f0-9]{40}', commit), 'Invalid commit')
    release = '.digitaltalha-release-' + commit[:12] + '-' + run
    require(RELEASE.fullmatch(release), 'Invalid run identifier')
    root = Path(root)
    files = {}
    for file in sorted((root / 'dist').rglob('*')):
        require(not file.is_symlink(), 'Symlinks are not deployable')
        if file.is_file():
            name = file.relative_to(root / 'dist').as_posix()
            data = file.read_bytes()
            if name == '.htaccess':
                data = data.replace(b'ErrorDocument 404 /404.html', ('ErrorDocument 404 /' + release + '/404.html').encode())
            files[name] = data
    # A changed asset gets a new URL, so existing visitors do not retain stale CSS/JS.
    def version_asset(match):
        name = match[2].lstrip('/')
        require(name in files, 'Missing local asset: ' + name)
        return match[1] + '="' + match[2] + '?v=' + digest(files[name])[:16] + '"'
    for name,data in list(files.items()):
        if name.endswith('.html'):
            files[name] = re.sub(r'(src|href)="(/assets/[^"?#]+)"', version_asset, data.decode()).encode()
    home = files['index.html'].decode()
    require(('content="noindex' in home) == (mode == 'staging'), 'Wrong build indexing mode')
    require(('GTM-NMMW3MLB' in home) == (mode == 'production'), 'Wrong build tracking mode')
    manifest = {'schema':1, 'commit':commit, 'release':release, 'mode':mode,
                'pages':json.loads((root / 'content/seo.json').read_text()),
                'files':{name:{'sha256':digest(data), 'size':len(data)} for name,data in files.items()}}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json', json.dumps(manifest, sort_keys=True))
        for name,data in files.items():
            archive.writestr('site/' + name, data)
    return manifest


def inspect_bundle(path, target):
    require(Path(path).stat().st_size <= MAX_ARCHIVE, 'Archive too large')
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [item.filename for item in entries]
        require(len(names) <= 1001 and len(names) == len(set(names)), 'Duplicate/excess archive entries')
        require(sum(item.file_size for item in entries) <= MAX_CONTENT, 'Expanded archive too large')
        for item in entries:
            parts = PurePosixPath(item.filename).parts
            require(not item.filename.startswith('/') and '..' not in parts and '\\' not in item.filename, 'Unsafe archive path')
            require(PurePosixPath(item.filename).as_posix() == item.filename, 'Noncanonical archive path')
            require(not stat.S_ISLNK(item.external_attr >> 16), 'Symlink in archive')
            require(not item.flag_bits & 1 and item.file_size <= 10 * 1024 * 1024, 'Unsupported archive entry')
        require('manifest.json' in names and archive.getinfo('manifest.json').file_size < 200000, 'Missing/oversized manifest')
        manifest = json.loads(archive.read('manifest.json'))
        require(manifest.get('schema') == 1 and manifest.get('mode') == target['mode'], 'Wrong release target')
        require(re.fullmatch(r'[a-f0-9]{40}', manifest.get('commit','')), 'Invalid commit')
        require(RELEASE.fullmatch(manifest.get('release','')), 'Invalid release name')
        require(manifest['release'].startswith('.digitaltalha-release-' + manifest['commit'][:12] + '-'), 'Commit/release mismatch')
        files = manifest['files']
        require(set(names) == {'manifest.json'} | {'site/' + name for name in files}, 'Archive/manifest mismatch')
        require({'.htaccess','index.html','404.html','api/enquiry.php','robots.txt','sitemap.xml'} <= set(files), 'Incomplete release')
        contents = {}
        for name,info in files.items():
            require(name == '.htaccess' or (re.fullmatch(r'[A-Za-z0-9_./-]+', name) and all(not part.startswith('.') for part in PurePosixPath(name).parts)), 'Unsupported file name')
            require(name == '.htaccess' or Path(name).suffix.lower() in {'.html','.css','.js','.json','.xml','.txt','.webp','.png','.jpg','.jpeg','.ico','.svg','.woff','.woff2','.ttf','.otf','.php'}, 'Unsupported file type')
            require(Path(name).suffix.lower() != '.php' or name == 'api/enquiry.php', 'Unexpected executable file')
            data = archive.read('site/' + name)
            require(len(data) == info['size'] and digest(data) == info['sha256'], 'File integrity mismatch: ' + name)
            contents[name] = data
        # A CI key cannot introduce arbitrary server code or Apache directives.
        require(digest(contents['api/enquiry.php']) == target['php_sha256'], 'PHP changed: manual review is required')
        settings = target['release_htaccess'].replace('ErrorDocument 404 /404.html', 'ErrorDocument 404 /' + manifest['release'] + '/404.html')
        require(contents['.htaccess'] == settings.encode(), 'Server rules changed: manual review is required')
        require(isinstance(manifest.get('pages'), dict) and 1 <= len(manifest['pages']) <= 100, 'Invalid page inventory')
        for route in manifest['pages']:
            require(route.startswith('/') and '..' not in route and re.fullmatch(r'/[a-z0-9/-]*', route), 'Invalid page route')
            file = 'index.html' if route == '/' else route.strip('/') + '/index.html'
            require(file in contents, 'Missing primary page')
        return manifest, contents


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def verify_site(target, manifest):
    origin = target['origin']
    mode = target['mode']
    opener = build_opener(NoRedirect)
    checks = []

    def request(path, data=None, extra=None, cache=True):
        separator = '&' if '?' in path else '?'
        url = origin + path + (separator + '__deploy=' + manifest['release'] if cache else '')
        req = Request(url, data=data, headers={'User-Agent':'DigitalTalhaDeployment/1.0', 'Cache-Control':'no-cache', **(extra or {})})
        try:
            response = opener.open(req, timeout=15)
        except HTTPError as error:
            response = error
        with response:
            status, headers, body = response.status, {k.lower():v for k,v in response.headers.items()}, response.read(MAX_CONTENT)
        checks.append({'path':path, 'status':status})
        return status, headers, body

    for route, metadata in manifest['pages'].items():
        status, headers, body = request(route)
        file = 'index.html' if route == '/' else route.strip('/') + '/index.html'
        require(status == 200 and digest(body) == manifest['files'][file]['sha256'], 'Page content check failed: ' + route)
        text = body.decode()
        require('<link rel="canonical" href="https://digitaltalha.com' + route + '"' in text, 'Canonical check failed')
        require(('content="noindex' in text) == bool(mode == 'staging' or metadata.get('noindex')), 'Indexing metadata check failed')
        require(('noindex' in headers.get('x-robots-tag','').lower()) == (mode == 'staging'), 'Indexing header check failed')
        require(('GTM-NMMW3MLB' in text) == (mode == 'production'), 'Tracking mode check failed')
    for name, info in manifest['files'].items():
        if name.startswith('assets/') or name in ('robots.txt','sitemap.xml'):
            status, headers, body = request('/' + name)
            require(status == 200 and digest(body) == info['sha256'], 'Asset check failed: ' + name)
    aliases = {'/resources/':'/blog/', '/category/meta-ads/':'/blog/', '/about-us/':'/about/', '/contact-us/':'/contact/', '/service/':'/services/', '/projects/':'/blog/', '/sitemap_index.xml':'/sitemap.xml', '/wp-sitemap.xml':'/sitemap.xml'}
    for path, destination in aliases.items():
        status, headers, body = request(path + '?utm_source=deployment', cache=False)
        require(status == 301 and headers.get('location') == origin + destination + '?utm_source=deployment', 'Legacy redirect check failed: ' + path)
    for key, destination in SHORTLINKS.items():
        status, headers, body = request('/?p=' + key + '&utm_source=deployment', cache=False)
        location = urlsplit(headers.get('location',''))
        require(status == 301 and location.path == destination and parse_qsl(location.query) == [('utm_source','deployment')], 'Shortlink check failed')
    status, headers, body = request('/deployment-probe-not-a-page/')
    require(status == 404 and digest(body) == manifest['files']['404.html']['sha256'], 'Custom 404 check failed')
    status, headers, body = request('/' + manifest['release'] + '/')
    require(status in (403,404), 'Internal release must not be public')
    status, headers, body = request('/api/enquiry.php')
    require(status == 405 and headers.get('allow') == 'POST' and json.loads(body)['ok'] is False, 'PHP execution check failed')
    for fields, request_origin, expected in [({},origin,422), ({'company_url':'https://bot.invalid/'},origin,400), ({},'https://foreign.invalid',403)]:
        status, headers, body = request('/api/enquiry.php', urlencode(fields).encode(), {'Content-Type':'application/x-www-form-urlencoded', 'Origin':request_origin}, cache=False)
        require(status == expected and json.loads(body)['ok'] is False, 'PHP validation check failed')
    for url in target.get('preserved_urls', []):
        with build_opener().open(Request(url, headers={'User-Agent':'DigitalTalhaDeployment/1.0'}), timeout=15) as response:
            require(response.status == 200, 'Preserved application check failed')
        checks.append({'preserved_url':url, 'status':200})
    if mode == 'production':
        for base in ['http://digitaltalha.com', 'http://www.digitaltalha.com', 'https://www.digitaltalha.com']:
            with build_opener().open(Request(base + '/contact/?utm_source=deployment', headers={'User-Agent':'DigitalTalhaDeployment/1.0'}), timeout=15) as response:
                require(response.status == 200 and response.url == origin + '/contact/?utm_source=deployment', 'Canonical HTTPS redirect check failed')
            checks.append({'canonical_origin':base, 'status':200})
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['production','staging'], required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--run', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    manifest = package(Path(__file__).resolve().parents[1], args.mode, args.commit, args.run, args.output)
    print('Packaged ' + args.mode + ': ' + str(len(manifest['files'])) + ' files')
