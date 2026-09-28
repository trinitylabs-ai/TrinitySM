"""Lossless field parsing for saved Markdown audits; no mathematical repairs.

Annotations are retained in the response and in normalization records. They are
excluded from enum parsing, and cannot substitute for the theorem's explanation.
NONE is an explicit empty qualifications inventory. All v1 semantic checks and
the requirement for four independent valid approvals remain in force.
"""
import hashlib
import re

from . import progress_body_validation as original

VERSION = 'comparative-progress-audit-validation-v2-mechanical'
ACCEPT, KEEP = original.ACCEPT, original.KEEP
POLICY_ID = 'r2-r3-verified-progress-both-orders-v1'


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def normalize_fields(text):
    """Separate one explicit enum from a balanced parenthetical annotation.

    Do not infer a status from prose, map a foreign enum to another judgment,
    or silently choose among competing declarations.
    """
    records, canonical = [], []
    for line_number, line in enumerate(text.splitlines(), 1):
        plain = re.sub(r'^[-*]\s+', '', line.strip().replace('**', '').replace('`', ''))
        match = re.fullmatch(
            r'((?:Baseline|Candidate) completeness)\s*:\s*'
            r'(COMPLETE|INCOMPLETE|UNRESOLVED)\s+(\(.+\))', plain, re.I)
        if match:
            label, value, annotation = match.groups()
            # The value itself must already be one exact, uppercase enum.
            depth, balanced = 0, True
            for index, char in enumerate(annotation):
                depth += (char == '(') - (char == ')')
                if depth < 0 or (depth == 0 and index != len(annotation)-1):
                    balanced = False
            competing = re.search(r'\b(?:COMPLETE|INCOMPLETE|UNRESOLVED)\b', annotation)
            if value in ('COMPLETE', 'INCOMPLETE', 'UNRESOLVED') and balanced and depth == 0 and not competing:
                canonical.append(f'{label}: {value}')
                records.append({'rule': 'separate_completeness_annotation', 'line': line_number,
                                'field': label, 'declared_value': value,
                                'annotation': annotation, 'original_line': line})
                continue
        canonical.append(line)
    return '\n'.join(canonical), records


def validate_audit(text, case):
    canonical, normalizations = normalize_fields(text)
    parsed = original.validate_audit(canonical, case)
    errors = list(parsed['errors'])
    missing = 'Missing explanation in Qualifications and supplied repairs'
    if missing in errors and parsed['checks']['Qualifications and supplied repairs']['status'] == 'NONE':
        normalized = '\n'.join(re.sub(r'^[-*]\s+', '', line.strip().replace('**', '').replace('`', ''))
                               for line in canonical.splitlines())
        sections = re.findall(r'^##\s+Qualifications and supplied repairs\s*\n(.*?)(?=^##\s|\Z)',
                              normalized, re.M | re.S | re.I)
        if len(sections) == 1:
            body = re.sub(r'^Status\s*:.*$', '', sections[0], flags=re.M | re.I).strip()
            if body in ('', 'None', 'None.'):
                errors.remove(missing)
                normalizations.append({'rule': 'explicit_empty_qualifications_inventory',
                                       'section': 'Qualifications and supplied repairs',
                                       'declared_value': 'NONE', 'original_explanation': body})
    valid = not errors
    return {**parsed, 'validator_version': VERSION, 'valid': valid,
            'decision': parsed['model_decision'] if valid else KEEP,
            'errors': errors, 'normalizations': normalizations,
            'response_sha256': digest(text),
            'canonical_markdown_sha256': digest(canonical),
            'field_annotations': [r for r in normalizations if r['rule'] == 'separate_completeness_annotation'],
            'mechanical_validation_only': True}


def configure(module, directory):
    """Use for a future unstarted experiment with the same mathematical prompt."""
    from pathlib import Path
    module.HERE = Path(directory)
    module.POLICY_ID = POLICY_ID
    module.VERSION = VERSION
    module.validate_audit = validate_audit
    return module
