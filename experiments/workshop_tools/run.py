#!/usr/bin/env python3
"""Explicit entry point for the current experimental Workshop Tools runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / 'runtime'
PACKAGE = 'cognitive_well_harness_v0_3_356_v349_discrete_consolidation_20260917'


def verify():
    inventory = json.loads((HERE / 'runtime_inventory.json').read_text())
    expected = {row['path']: row['sha256'] for row in inventory['files']}
    actual = {str(p.relative_to(RUNTIME)) for p in RUNTIME.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and '.tools' not in p.parts}
    if actual != set(expected):
        raise ValueError('Experimental runtime has missing or unlisted files')
    for name, digest in expected.items():
        path = RUNTIME / name
        if (path.is_symlink() or not path.resolve().is_relative_to(RUNTIME)
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise ValueError('Experimental runtime changed: ' + name)
    return len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--resume-selected-certificate-from', type=Path)
    options, remaining = parser.parse_known_args()
    count = verify()
    if options.verify:
        if remaining or options.resume_selected_certificate_from:
            parser.error('--verify is a standalone integrity check')
        print(f'Verified {count} experimental runtime files.')
        return
    module = 'proof_harness'
    if options.resume_selected_certificate_from:
        module = 'selected_resume'
        remaining += ['--source-run', str(options.resume_selected_certificate_from.resolve())]
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(RUNTIME))
    sys.argv = [str(Path(__file__)), *remaining]
    runpy.run_module(PACKAGE + '.' + module, run_name='__main__')


if __name__ == '__main__':
    main()
