#!/usr/bin/env python3
"""Scan tracked release files without printing matched private values."""
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PERSONAL_HOME = re.compile('/' + r'home/(?!user(?:/|\b))[^/\s"\x27]+')
EMAIL = re.compile(r'(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])')
IPV4 = re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])')
NETWORKS = [ipaddress.ip_network((10 << 24, 8)),
            ipaddress.ip_network(((172 << 24) + (16 << 16), 12)),
            ipaddress.ip_network(((192 << 24) + (168 << 16), 16)),
            ipaddress.ip_network(((100 << 24) + (64 << 16), 10))]
TOKEN = re.compile(r'\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|AIza[0-9A-Za-z_-]{30,}|xox[baprs]-[A-Za-z0-9-]{16,})\b')
PRIVATE_KEY = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')
LOG_DIR = re.compile(r'(?:logs?|.*[_-]logs?)', re.I)
LOG_FILE = re.compile(r'(?:.*\.log(?:\..*)?|.*\.(?:stdout|stderr|transcript)\.txt|.*[._]events\.jsonl|runtime_logs.*\.gz)$', re.I)
WEIGHTS = {'.safetensors', '.gguf', '.ckpt', '.pth', '.pt', '.onnx', '.bin'}
REFERENCE_SOURCES = ROOT / 'docs/public_release/grading/imo2026_reference_sources.json'


def external_reference_identities():
    sources = json.loads(REFERENCE_SOURCES.read_text())['references']
    hashes, blobs, paths = set(), set(), set()
    for row in sources:
        hashes.update(row[k] for k in ['pdf_sha256', 'extracted_sha256', 'reference_sha256'])
        blobs.update(row['known_git_blob_ids'])
        for item in row['local_grading_inputs']:
            hashes.add(item['sha256'])
            paths.add(item['path'])
    return hashes, blobs, paths


def inspect_external_reference(name, data, hashes, paths):
    if (name in paths or name.startswith('.workshop/external-references/')
            or hashlib.sha256(data).hexdigest() in hashes):
        return ['external_reference_body']
    try:
        normalized = data.decode('utf-8').strip().encode('utf-8')
    except UnicodeDecodeError:
        return []
    return ['external_reference_body'] if hashlib.sha256(normalized).hexdigest() in hashes else []


def reference_history(blobs):
    objects = subprocess.check_output(['git', 'rev-list', '--objects', 'HEAD'], cwd=ROOT).decode().splitlines()
    return [line for line in objects if line.split(' ', 1)[0] in blobs]


def inspect(name, text):
    reasons = []
    for label, pattern in [('personal_home', PERSONAL_HOME), ('email', EMAIL), ('provider_token', TOKEN), ('private_key', PRIVATE_KEY)]:
        if pattern.search(text):
            reasons.append(label)
    for match in IPV4.finditer(text):
        try:
            address = ipaddress.ip_address(match.group())
        except ValueError:
            continue
        if any(address in network for network in NETWORKS):
            reasons.append('internal_address')
            break
    path = Path(name)
    if any(LOG_DIR.fullmatch(part) for part in path.parts[:-1]) or LOG_FILE.fullmatch(path.name):
        reasons.append('runtime_log')
    if path.suffix in WEIGHTS:
        reasons.append('model_or_binary_weights')
    return reasons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true', help='also reject known reference bodies in current branch history')
    args = parser.parse_args()
    hashes, blobs, external_paths = external_reference_identities()
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    findings = []
    checked = 0
    for name in filter(None, paths):
        path = ROOT / name
        if not path.exists() and not path.is_symlink():
            continue  # A pending deletion is absent from the release working tree.
        data = str(path.readlink()).encode() if path.is_symlink() else path.read_bytes()
        checked += 1
        reasons = inspect(name, data.decode('utf-8', errors='replace'))
        reasons.extend(inspect_external_reference(name, data, hashes, external_paths))
        if reasons:
            findings.append((name, reasons))
    for name, reasons in findings:
        print(name + ': ' + ', '.join(reasons))
    print(f'Checked {checked} tracked files; flagged {len(findings)} files. Matched values are never printed.')
    historical = reference_history(blobs) if args.history else []
    for item in historical:
        print('historical_external_reference: ' + item)
    if args.history:
        print(f'Known external-reference bodies reachable from HEAD: {len(historical)}. '
              'Deleting current files alone does not remove Git history.')
    raise SystemExit(bool(findings or historical))


if __name__ == '__main__':
    main()
