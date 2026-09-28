#!/usr/bin/env python3
"""Select an immutable IMO Proof Pipeline release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--release', default='1.12.0')
    parser.add_argument('--list-releases', action='store_true')
    args, remaining = parser.parse_known_args()
    registry = json.loads((ROOT / 'releases/index.json').read_text())
    if args.list_releases:
        print('\n'.join(sorted(registry['releases'], key=lambda version: tuple(map(int, version.split('.'))))))
        return
    if not re.fullmatch(r'\d+\.\d+\.\d+', args.release):
        parser.error('Release must be an explicit semantic version, such as 1.0.0')
    expected = registry['releases'].get(args.release)
    if expected is None:
        parser.error(f'Unknown release: {args.release}')
    release = ROOT / 'releases' / args.release
    manifest = release / 'release.json'
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != expected:
        raise ValueError('Registered release manifest changed')
    lock = json.loads(manifest.read_text())
    if hashlib.sha256((release / 'launch.py').read_bytes()).hexdigest() != lock['files']['launch.py']:
        raise ValueError('Registered release launcher changed')
    os.execv(sys.executable, [sys.executable, '-B', str(release / 'launch.py'), *remaining])


if __name__ == '__main__':
    main()
