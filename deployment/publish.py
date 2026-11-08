"""Send reviewed bundles through the restricted, host-key-pinned SSH channel."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.request

from release import digest, require


def current_main():
    request = urllib.request.Request('https://api.github.com/repos/talhaalamo89-maker/DigitalTalha_website/branches/main', headers={'Authorization':'Bearer ' + os.environ['GH_TOKEN'], 'Accept':'application/vnd.github+json', 'User-Agent':'DigitalTalhaDeployment'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)['commit']['sha']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action', choices=['publish','rollback'], default='publish')
    args = parser.parse_args()
    require(os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Only main can deploy')
    require(current_main() == os.environ['GITHUB_SHA'], 'A newer main commit exists; this run will not deploy')
    with tempfile.TemporaryDirectory(prefix='digitaltalha-access-') as folder:
        key, hosts = Path(folder)/'key', Path(folder)/'known_hosts'
        key.write_text(os.environ.pop('DIGITALTALHA_DEPLOY_KEY'))
        key.chmod(0o600)
        hosts.write_text(os.environ.pop('DIGITALTALHA_KNOWN_HOSTS'))
        require(re.fullmatch(r'[A-Za-z0-9.-]+', os.environ['DIGITALTALHA_SSH_HOST']), 'Invalid SSH host')
        require(re.fullmatch(r'[a-z_][a-z0-9_-]*', os.environ['DIGITALTALHA_SSH_USER']), 'Invalid SSH user')
        require(os.environ['DIGITALTALHA_SSH_PORT'].isdigit(), 'Invalid SSH port')
        options = ['ssh','-T','-i',str(key),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(hosts),'-o','ConnectTimeout=15','-o','ServerAliveInterval=20','-o','ServerAliveCountMax=6','-p',os.environ['DIGITALTALHA_SSH_PORT'],os.environ['DIGITALTALHA_SSH_USER']+'@'+os.environ['DIGITALTALHA_SSH_HOST']]

        def command(action, target, payload=b''):
            words = [action,target] + ([digest(payload)] if action == 'deploy' else [])
            result = subprocess.run(options + [' '.join(words)], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=660)
            output = result.stdout.decode().strip()
            if result.returncode and action == 'deploy':
                # A second connection recovers a journal left by an uncatchable interruption.
                subprocess.run(options + ['status ' + target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            require(result.returncode == 0, 'Deployment stopped: ' + output + ' ' + result.stderr.decode()[-500:])
            report = json.loads(output)
            print(json.dumps({'target':target, **report}))
            return report

        if args.action == 'rollback':
            command('rollback','production')
        else:
            command('deploy','staging',Path('bundles/staging.zip').read_bytes())
            require(current_main() == os.environ['GITHUB_SHA'], 'A newer change arrived; production is left unchanged')
            command('deploy','production',Path('bundles/production.zip').read_bytes())


if __name__ == '__main__':
    main()
