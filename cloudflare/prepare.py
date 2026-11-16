"""Adapt an already checked static build without changing the Hostinger builder."""
from pathlib import Path
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
# Keep published WordPress media and ownership files at their original URLs.
# This directory contains only reviewed public files, never a full uploads export.
legacy = ROOT / 'cloudflare/legacy-public'
if legacy.is_dir():
    shutil.copytree(legacy, OUT, dirs_exist_ok=True)
preview = os.environ.get('SITE_NOINDEX', '').lower() in ('1', 'true', 'yes')
routes = sorted('/' + p.parent.relative_to(OUT).as_posix().strip('./') + '/'
                for p in OUT.rglob('index.html'))
routes = ['/' if p == '//' else p for p in routes]
source = (ROOT / 'cloudflare/worker.mjs').read_text()
source = source.replace('/* BUILD_CONFIG */',
                        f'const BUILD_PREVIEW = {json.dumps(preview)};\nconst PAGE_ROUTES = new Set({json.dumps(routes)});')
(OUT / '_worker.js').write_text(source)
(OUT / '_routes.json').write_text(json.dumps({
    'version': 1, 'include': ['/*'], 'exclude': ['/assets/*', '/favicon.ico']
}, indent=2) + '\n')
headers = '''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
/DigitalTalha-preview.html
  X-Robots-Tag: noindex, follow
'''
if preview:
    headers += '/*\n  X-Robots-Tag: noindex, follow\n'
(OUT / '_headers').write_text(headers)
# All redirects live in the Worker: Pages _redirects cannot match query strings
# and is not applied to Function responses.
for path in OUT.rglob('*'):
    if path.is_file() and (path.name == '.htaccess' or path.suffix.lower() == '.php'):
        path.unlink()
shutil.rmtree(OUT / 'api', ignore_errors=True)
assert (OUT / '404.html').is_file()
print(f'Cloudflare {"preview" if preview else "production"} output ready: {OUT}')
