"""Recover a missing checks label using existing line-cited evidence, offline only.

Original solver artifacts, model responses, prompts, and frozen parsers are never
modified. Every derived vote remains bound to its original transport response.
"""
import copy
import hashlib
import json
from pathlib import Path
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def exact(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, f'Recovery artifact drift: {path}'
    else:
        with path.open('xb') as stream:
            stream.write(data)


def freeze(path, value):
    exact(path, (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode())


def restore_checks_label(text, strict_parse):
    try:
        strict_parse(text)
    except ValueError as error:
        match = re.fullmatch(r'Missing Decisive checks in (proof [ab])', str(error))
        if not match:
            raise
        section = match.group(1)
    else:
        return text, None
    # Keep every original character. Copy only existing, explicitly line-cited
    # checks from the qualifications field into its omitted sibling field.
    heads = list(re.finditer(r'^#{1,4}\s+(Proof A|Proof B|Decision)\s*$', text, re.M | re.I))
    assert len(heads) == 3 and len({h.group(1).lower() for h in heads}) == 3
    index = next(i for i, h in enumerate(heads) if h.group(1).lower() == section)
    start = heads[index].end()
    end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
    body = text[start:end]
    assert not re.search(r'Decisive\s+checks', body, re.I), 'Present-but-empty checks are not a missing-label case'
    field = re.search(r'^Qualifications and supplied repairs:[ \t]*\n(?P<evidence>.+)\Z', body.strip(), re.M | re.S)
    assert field, 'No separate existing qualifications evidence to copy'
    evidence = field.group('evidence').strip()
    bullets = re.split(r'(?m)(?=^- )', evidence)
    bullets = [b.strip() for b in bullets if b.strip()]
    assert len(bullets) >= 2, 'Need multiple explicit line-referenced checks'
    assert all(re.match(r'^- Lines?\s+\d+(?:[–-]\d+)?\s*:', b) for b in bullets), 'Evidence must already identify proof lines'
    assert all(len(b) >= 80 for b in bullets), 'Empty or token-only evidence cannot be reconstructed'
    addition = 'Decisive checks:\n' + evidence + '\n\n'
    normalized = text[:end] + addition + text[end:]
    parsed = strict_parse(normalized)
    # The strict parser validates all original obligations and one explicit
    # Winner. No preference is inferred from prose or external grades.
    assert normalized[:end] == text[:end] and normalized[end + len(addition):] == text[end:]
    return normalized, {'policy': 'missing-decisive-checks-label-existing-line-citations-v1',
            'section': section, 'source_field': 'Qualifications and supplied repairs',
            'operation': 'Copy the existing line-cited evidence verbatim under the omitted Decisive checks label',
            'copied_evidence_sha256': sha(evidence.encode()), 'original_response_sha256': sha(text.encode()),
            'normalized_response_sha256': sha(normalized.encode()), 'winner_label': parsed['winner_label'],
            'model_calls': 0, 'new_mathematical_text': False}

