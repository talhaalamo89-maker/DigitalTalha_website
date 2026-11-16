"""Build and validate either a production or SITE_NOINDEX preview artifact."""
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
preview = os.environ.get('SITE_NOINDEX', '').lower() in ('1', 'true', 'yes')
commands = [
    ['npm', 'run', 'build'],
    ['python3', 'scripts/check.py'],
    ['python3', 'scripts/check-seo.py'] + (['--staging'] if preview else []),
    ['python3', 'scripts/check-services.py'],
    ['node', 'scripts/check-interactions.mjs'],
    ['python3', 'cloudflare/prepare.py'],
]
for command in commands:
    subprocess.run(command, cwd=ROOT, check=True)
