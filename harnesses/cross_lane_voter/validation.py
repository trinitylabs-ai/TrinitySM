"""Mechanical Markdown validation; never infer a missing preference."""
import hashlib
import re

def sha(data):
    return hashlib.sha256(data).hexdigest()

def strict_parse(text):
    # Formatting normalization only. Never infer a preference from prose.
    normalized = text.replace('\r\n', '\n').strip()
    normalized = re.sub(r'^```(?:markdown|md)?\s*\n(.*)\n```$', r'\1', normalized, flags=re.S)
    normalized = normalized.replace('**', '').replace('`', '')
    sections = {}
    heads = list(re.finditer(r'^#{1,4}\s+(Proof A|Proof B|Decision)\s*$', normalized, re.M | re.I))
    for index, head in enumerate(heads):
        key = head.group(1).lower()
        if key in sections:
            raise ValueError('Duplicate Markdown section: ' + key)
        end = heads[index + 1].start() if index + 1 < len(heads) else len(normalized)
        sections[key] = normalized[head.end():end].strip()
    for key in ('proof a', 'proof b', 'decision'):
        if not sections.get(key):
            raise ValueError('Missing nonempty section: ' + key)
    for key in ('proof a', 'proof b'):
        for field in ('Established theorem', 'Claim gap', 'Qualifications and supplied repairs', 'Decisive checks'):
            if not re.search(r'^\s*(?:[-*]\s*)?' + field + r'\s*:\s*\S', sections[key], re.M | re.I):
                raise ValueError(f'Missing {field} in {key}')
    winners = re.findall(r'^\s*(?:[-*]\s*)?Winner\s*:\s*([AB])\s*[.]?\s*$', sections['decision'], re.M | re.I)
    if len(winners) != 1 or len(re.findall(r'^\s*(?:[-*]\s*)?Winner\s*:', normalized, re.M | re.I)) != 1:
        raise ValueError('Expected exactly one unambiguous Winner: A or B')
    reason = re.search(r'^\s*(?:[-*]\s*)?Reason\s*:\s*(\S.*)', sections['decision'], re.M | re.I | re.S)
    if not reason:
        raise ValueError('Missing decision reason')
    return {'valid': True, 'winner_label': winners[0].upper(), 'reason': reason.group(1).strip(),
            'response_sha256': sha(text.encode()), 'normalized_sha256': sha(normalized.encode()),
            'validation_scope': 'format and request binding; no automatic mathematical correctness claim'}



def parse(text):
    from .mechanical_recovery import recover_comparison
    normalized, repair = recover_comparison(text, strict_parse)
    parsed = strict_parse(normalized)
    parsed['response_sha256'] = sha(text.encode())
    if repair:
        parsed['mechanical_recovery'] = repair
    return parsed
