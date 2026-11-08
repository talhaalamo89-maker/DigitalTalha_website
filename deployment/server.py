"""Installed privately on Hostinger; restricted SSH command, not a public endpoint."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import io
import json
import os
import re
import shutil
import signal
import sys
import tempfile
import time

from release import MAX_ARCHIVE, VERSIONED_ASSET, digest, inspect_bundle, require, verify_site


def save(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + '.new')
    with temporary.open('w') as file:
        json.dump(data, file, indent=2)
        file.flush()
        os.fsync(file.fileno())
    os.chmod(str(temporary), 0o600)
    os.replace(str(temporary), str(path))


def switch(path, text):
    temporary = path.with_name('.digitaltalha-routing-ready')
    with temporary.open('w') as file:
        file.write(text)
        file.flush()
        os.fsync(file.fileno())
    os.chmod(str(temporary), 0o644)
    os.replace(str(temporary), str(path))


def load_state(home, target):
    path = home / (target['mode'] + '.json')
    require(path.is_file(), 'Server deployment state has not been initialized')
    state = json.loads(path.read_text())
    # An interrupted transfer never changes routing. An interrupted activation is recovered.
    if state.get('pending'):
        rollback = state['pending']['before']
        current = (Path(target['root']) / '.htaccess').read_text()
        require(digest(current.encode()) in (digest(rollback['routing'].encode()), state['pending']['new_routing_sha256']), 'Routing drift during recovery; manual review required')
        switch(Path(target['root']) / '.htaccess', rollback['routing'])
        state['active'] = rollback
        state['pending'] = None
        state['last_result'] = 'recovered interrupted activation'
        save(path, state)
    return state


def activate(home, target, bundle, expected_digest, verify=verify_site):
    require(digest(bundle) == expected_digest, 'Transfer integrity check failed')
    root = Path(target['root'])
    state_path = home / (target['mode'] + '.json')
    state = load_state(home, target)
    before = state['active']
    require(digest((root / '.htaccess').read_bytes()) == digest(before['routing'].encode()), 'Live routing changed; refusing overwrite')
    require(shutil.disk_usage(str(root)).free > 150 * 1024 * 1024, 'Insufficient free space; live site left unchanged')
    with tempfile.TemporaryDirectory(prefix='incoming-', dir=str(home)) as folder:
        archive = Path(folder) / 'release.zip'
        archive.write_bytes(bundle)
        manifest, files = inspect_bundle(archive, target)
        destination = root / manifest['release']
        if before['manifest']['release'] == manifest['release']:
            require(before['manifest'] == manifest, 'Release identifier reused with different contents')
            return {'result':'already active', 'release':manifest['release']}
        require(not destination.exists(), 'Release destination already exists')
        prepared = Path(folder) / 'release'
        prepared.mkdir(mode=0o755)
        for name, data in files.items():
            file = prepared / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
            os.chmod(str(file), 0o644)
        # Keep recent immutable URLs working for visitors who loaded the previous HTML.
        old_assets = root / before['manifest']['release'] / 'assets'
        if old_assets.is_dir():
            for asset in old_assets.rglob('*'):
                if asset.is_file() and not asset.is_symlink() and VERSIONED_ASSET.fullmatch(asset.name) and asset.stat().st_mtime > time.time() - 35 * 86400:
                    name = asset.relative_to(old_assets)
                    destination_asset = prepared / 'assets' / name
                    if not destination_asset.exists():
                        destination_asset.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(asset), str(destination_asset))
        for directory, folders, names in os.walk(str(prepared)):
            os.chmod(directory, 0o755)
        routing = target['root_template'].replace('.digitaltalha-release-20261108', manifest['release'])
        require(routing != target['root_template'], 'Root dispatcher template did not select the release')
        protected = {name: (root / name).stat().st_ino for name in target.get('preserve_folders', [])}
        os.replace(str(prepared), str(destination))
        active = {'routing':routing, 'manifest':manifest}
        state['pending'] = {'before':before, 'new_routing_sha256':digest(routing.encode())}
        save(state_path, state)
        try:
            switch(root / '.htaccess', routing)
            failure = None
            for attempt in range(3):
                try:
                    checks = verify(target, manifest)
                    failure = None
                    break
                except Exception as error:
                    failure = error
                    if attempt < 2:
                        time.sleep(2)
            if failure:
                raise failure
            require(all((root / name).stat().st_ino == inode for name,inode in protected.items()), 'Preserved directory changed')
            state['previous'] = before
            state['active'] = active
            state['pending'] = None
            state['last_result'] = 'deployed and verified'
            state['verified_at'] = datetime.now(timezone.utc).isoformat()
            save(state_path, state)
            return {'result':state['last_result'], 'release':manifest['release'], 'commit':manifest['commit'], 'checks':len(checks)}
        except BaseException:
            switch(root / '.htaccess', before['routing'])
            state['active'] = before
            state['pending'] = None
            state['last_result'] = 'deployment failed; previous routing restored'
            save(state_path, state)
            # Independently verify restoration; preserve its failure for the operator.
            verify(target, before['manifest'])
            raise


def rollback(home, target, verify=verify_site):
    path = home / (target['mode'] + '.json')
    state = load_state(home, target)
    require(state.get('previous'), 'No previous automated release is available')
    require(digest((Path(target['root']) / '.htaccess').read_bytes()) == digest(state['active']['routing'].encode()), 'Live routing changed; refusing overwrite')
    previous = state['previous']
    switch(Path(target['root']) / '.htaccess', previous['routing'])
    state['active'], state['previous'], state['pending'] = previous, None, None
    state['last_result'] = 'rolled back'
    save(path, state)
    checks = verify(target, previous['manifest'])
    return {'result':'rolled back and verified', 'release':previous['manifest']['release'], 'checks':len(checks)}


def main():
    os.umask(0o077)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Deployment interrupted; restoring previous routing')
    signal.signal(signal.SIGALRM, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    home = Path(__file__).resolve().parent
    config = json.loads((home / 'config.json').read_text())
    words = os.environ.get('SSH_ORIGINAL_COMMAND','').split()
    require(len(words) in (2,3) and words[0] in ('status','deploy','rollback') and words[1] in config, 'This key permits website deployment commands only')
    action, mode = words[:2]
    require((action == 'deploy' and len(words) == 3 and re.fullmatch(r'[a-f0-9]{64}', words[2])) or (action != 'deploy' and len(words) == 2), 'Invalid deployment command')
    with (home / 'deploy.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        target = config[mode]
        if action == 'deploy':
            signal.alarm(600)
            data = sys.stdin.buffer.read(MAX_ARCHIVE + 1)
            require(len(data) <= MAX_ARCHIVE, 'Archive too large')
            result = activate(home, target, data, words[2])
        elif action == 'rollback':
            result = rollback(home, target)
        else:
            state = load_state(home, target)
            result = {'result':state.get('last_result'), 'release':state['active']['manifest']['release'], 'commit':state['active']['manifest'].get('commit')}
        with (home / 'history.jsonl').open('a') as log:
            log.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(), 'target':mode, 'result':result}) + '\n')
        print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        print(json.dumps({'error':str(error)}))
        sys.exit(1)
