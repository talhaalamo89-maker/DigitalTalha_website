"""Check a noindex preview in Wrangler or on a deployed Pages URL."""
import json
import sys
import urllib.error
import urllib.request

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

base = sys.argv[1].rstrip('/')
opener = urllib.request.build_opener(NoRedirect)
opener.addheaders = [('User-Agent', 'DigitalTalha-Migration-Check/1.0 (+https://digitaltalha.com/)')]
results = []
paths = [('/', 200), ('/about/', 200), ('/about', 301),
         ('/about/index.html', 301), ('/projects/', 301),
         ('/projects/glisan-akbari-hospital/', 200),
         ('/?p=454&utm_source=test', 301), ('/wp-sitemap.xml', 301),
         ('/does-not-exist/', 404), ('/api/enquiry.php', 405),
         ('/api/other.php', 404), ('/.htaccess', 404), ('/sitemap.xml', 200)]
for path, wanted in paths:
    try:
        response = opener.open(base + path, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    body = response.read().decode('utf8', 'replace')
    row = {'path': path, 'status': response.status,
           'location': response.headers.get('Location'),
           'robots': response.headers.get('X-Robots-Tag')}
    results.append(row)
    assert response.status == wanted, row
    assert response.headers.get('X-Robots-Tag') == 'noindex, follow', row
    assert response.headers.get('X-Content-Type-Options') == 'nosniff', row
    if path == '/sitemap.xml':
        assert '<loc>' not in body
    if path == '/projects/glisan-akbari-hospital/':
        assert 'Glisan' in body
    if path.startswith('/?p='):
        assert row['location'] == base + '/about/?utm_source=test', row
print(json.dumps(results, indent=2))
