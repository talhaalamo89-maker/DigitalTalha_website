"""Package built files for the versioned Hostinger layout; never deploy them."""
from pathlib import Path
import argparse
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', required=True, help='Matching hidden directory in root.htaccess')
args = parser.parse_args()
if not re.fullmatch(r'\.digitaltalha-release-[a-z0-9-]+', args.release):
    parser.error('Use a name such as .digitaltalha-release-20261108')
if args.release not in (ROOT / 'deployment/root.htaccess').read_text():
    parser.error('Update deployment/root.htaccess to the chosen release first')
source = ROOT / 'dist'
if not (source / 'api/enquiry.php').is_file():
    parser.error('Build the website first')
if '<meta name="robots" content="noindex' in (source / 'index.html').read_text():
    parser.error('Rebuild without SITE_NOINDEX for production')
settings = (source / '.htaccess').read_text()
if 'ErrorDocument 404 /404.html' not in settings:
    parser.error('Review the changed error-document settings before packaging')
output = ROOT / 'deployment/packages' / (args.release.lstrip('.') + '.zip')
output.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(source.rglob('*')):
        if not file.is_file():
            continue
        relative = file.relative_to(source).as_posix()
        if relative == '.htaccess':
            archive.writestr(relative, settings.replace('ErrorDocument 404 /404.html', f'ErrorDocument 404 /{args.release}/404.html'))
        else:
            archive.write(file, relative)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    count = len(archive.namelist())
print(f'{output}\n{count} files\nSHA-256 {hashlib.sha256(output.read_bytes()).hexdigest()}')
