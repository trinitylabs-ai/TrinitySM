#!/usr/bin/env python3
"""Publish a new immutable composite release from a verified frozen engine."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import re
import shutil
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def verified_engine(source):
    freeze = json.loads((source / 'freeze.json').read_text())
    expected = set(freeze['files']) | {'freeze.json', 'SHA256SUMS'}
    entries = list(source.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Frozen engine contains a symbolic link')
    actual = {str(p.relative_to(source)) for p in entries if p.is_file()}
    if actual != expected:
        raise ValueError('Frozen engine has missing or unlisted files')
    for name, digest in freeze['files'].items():
        p = source / name
        if p.is_symlink() or not p.resolve().is_relative_to(source.resolve()) or sha(p) != digest:
            raise ValueError(f'Frozen engine file changed: {name}')
    return freeze


def publish(source, profile_path, version, bump, notes, root=ROOT):
    with (root / '.publish.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _publish(source, profile_path, version, bump, notes, root)


def _publish(source, profile_path, version, bump, notes, root):
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Use a numeric MAJOR.MINOR.PATCH version')
    if not notes.strip():
        raise ValueError('Release notes are required')
    directory = root / 'releases'
    directory.mkdir(exist_ok=True)
    index_path = directory / 'index.json'
    index = json.loads(index_path.read_text()) if index_path.exists() else {'name': 'IMO Proof Pipeline', 'releases': {}}
    destination = directory / version
    if version in index['releases'] or destination.exists():
        raise FileExistsError('Published versions cannot be overwritten')
    previous = None
    if index['releases']:
        old_version = max(index['releases'], key=lambda x: tuple(map(int, x.split('.'))))
        old_path = directory / old_version / 'release.json'
        if sha(old_path) != index['releases'][old_version]:
            raise ValueError('Previous registered release changed')
        previous = json.loads(old_path.read_text())
        major, minor, patch = map(int, old_version.split('.'))
        expected = {'major': (major + 1, 0, 0), 'minor': (major, minor + 1, 0), 'patch': (major, minor, patch + 1)}
        if tuple(map(int, version.split('.'))) != expected.get(bump):
            raise ValueError('Version does not match the requested increment')
    elif version != '1.0.0' or bump != 'initial':
        raise ValueError('The first release must be 1.0.0 with --bump initial')
    freeze = verified_engine(source)
    profile = json.loads(profile_path.read_text())
    if profile['name'] != 'IMO Proof Pipeline' or profile['components'] != {'frontend': '0.3.263', 'backend': '0.3.290+goldfree.1'}:
        raise ValueError('This publisher supports the v263/v290 composite')
    if not (source / 'source/scripts/run_v263_v290.py').is_file():
        raise ValueError('Frozen engine lacks the original composite entry point')
    # Solver/source/prompt/schema, profile and launcher changes require at least
    # a minor version. Patch releases can adjust release metadata/packaging only.
    behavior = {k: v for k, v in freeze['files'].items() if k.startswith('source/')}
    behavior.update({'profile': sha(profile_path), 'launcher': sha(root / 'tools/launch_template.py')})
    fingerprint = hashlib.sha256(json.dumps(behavior, sort_keys=True).encode()).hexdigest()
    if previous and bump == 'patch' and fingerprint != previous['behavior_sha256']:
        raise ValueError('Solver, prompt, profile or launcher changes require a minor/major version')
    destination.mkdir()
    try:
        shutil.copytree(source, destination / 'engine')
        shutil.copy2(profile_path, destination / 'profile.json')
        shutil.copy2(root / 'tools/launch_template.py', destination / 'launch.py')
        files = {str(p.relative_to(destination)): sha(p) for p in sorted(destination.rglob('*')) if p.is_file()}
        manifest = {'schema': 'imo-proof-pipeline-release-v1', 'name': 'IMO Proof Pipeline', 'version': version,
                    'created_at': datetime.now(timezone.utc).isoformat(), 'bump': bump,
                    'previous_release_sha256': index['releases'].get(previous['version']) if previous else None,
                    'upstream': {'release_id': freeze['release_id'], 'freeze_sha256': sha(source / 'freeze.json'),
                                 'frontend': '0.3.263', 'backend': '0.3.290+goldfree.1'},
                    'behavior_sha256': fingerprint, 'notes': notes.strip(), 'files': files}
        write(destination / 'release.json', manifest)
        index['releases'][version] = sha(destination / 'release.json')
        temporary = index_path.with_suffix('.tmp')
        write(temporary, index)
        temporary.replace(index_path)
    except BaseException:
        # Keep failed staging for inspection; never register a partial release.
        raise
    return {'version': version, 'release_sha256': index['releases'][version], 'files': len(files), 'directory': str(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-release', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--bump', choices=('initial', 'patch', 'minor', 'major'), required=True)
    parser.add_argument('--notes-file', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(publish(args.source_release.resolve(), args.profile, args.version, args.bump,
                             args.notes_file.read_text()), indent=2))


if __name__ == '__main__':
    main()
