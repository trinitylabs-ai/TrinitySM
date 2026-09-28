#!/usr/bin/env python3
"""Obtain externally hosted IMO grading references; never called by generation.

Only `download` makes network requests. This utility grants no rights to upstream
content, including redistribution or transmission to a hosted grading service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/public_release/grading/imo2026_reference_sources.json'
CACHE = ROOT / '.workshop/external-references/mechmath-imo2026'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_path(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Invalid reference destination: {relative}')
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Reference destination escapes repository: {relative}')
    if any(part.is_symlink() for part in [path, *path.parents] if part != root.parent):
        raise ValueError(f'Reference destination contains a symlink: {relative}')
    return path


def require_hash(data, expected, label):
    if digest(data) != expected:
        raise ValueError(f'Hash mismatch for {label}; existing files were not replaced')
    return data


def extracted_forms(pdf, row):
    require_hash(pdf.read_bytes(), row['pdf_sha256'], pdf.name)
    result = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw = require_hash(result.stdout, row['extracted_sha256'], 'PDF text extraction')
    stripped = raw.decode('utf-8').strip().encode('utf-8')
    require_hash(stripped, row['reference_sha256'], 'normalized grading reference')
    return {'pdftotext_layout': raw, 'strip': stripped}


def fetch_pdf(row, destination):
    if destination.exists():
        require_hash(destination.read_bytes(), row['pdf_sha256'], destination.name)
        return
    request = urllib.request.Request(row['download_url'], headers={'User-Agent': 'ProofWorkshop-reference-download'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    require_hash(data, row['pdf_sha256'], destination.name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Publish the cache entry only after the whole response passes its hash check.
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
        tmp.write(data)
        temp_path = Path(tmp.name)
    temp_path.replace(destination)


def prepare(manifest, root, cache, download=False):
    pending = []
    for row in manifest['references']:
        pdf = cache / (row['problem_id'] + '.pdf')
        if download:
            fetch_pdf(row, pdf)
        if not pdf.is_file():
            raise FileNotFoundError('References are external. Read NOTICE §3b, then run '
                                    '`python3 scripts/prepare_imo_references.py download`.')
        forms = extracted_forms(pdf, row)
        for item in row['local_grading_inputs']:
            path = checked_path(root, item['path'])
            data = require_hash(forms[item['format']], item['sha256'], item['path'])
            if path.exists():
                require_hash(path.read_bytes(), item['sha256'], item['path'])
            pending.append((path, data))
    # Validate every input before restoring any historical grading path.
    for path, data in pending:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return len(pending)


def verify(manifest, root):
    total = 0
    for row in manifest['references']:
        for item in row['local_grading_inputs']:
            path = checked_path(root, item['path'])
            if not path.is_file():
                raise FileNotFoundError(f'External reference missing: {item["path"]}. '
                                        'Run scripts/prepare_imo_references.py download first.')
            require_hash(path.read_bytes(), item['sha256'], item['path'])
            total += 1
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['download', 'prepare', 'verify'],
                        help='download from upstream and restore inputs; prepare from local cache; or verify only')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    if args.action == 'download':
        print('MechMath solution license: not specified. Download is directly from upstream. '
              'This project grants no redistribution or hosted-grader transmission rights. See NOTICE §3b.')
    try:
        count = (verify(manifest, ROOT) if args.action == 'verify' else
                 prepare(manifest, ROOT, CACHE, download=args.action == 'download'))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Verified {count} local grading inputs for six source references. No grader was started.')


if __name__ == '__main__':
    main()
