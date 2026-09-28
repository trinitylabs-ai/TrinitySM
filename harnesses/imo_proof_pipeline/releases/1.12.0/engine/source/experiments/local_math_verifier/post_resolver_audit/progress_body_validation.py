"""Mechanical consistency of comparative audits, separate from mathematical truth."""
import hashlib
import re

VERSION = 'comparative-progress-audit-validation-v1'
ACCEPT, KEEP = 'ACCEPT_CANDIDATE', 'KEEP_BASELINE'


def validate_audit(text, case):
    errors, normalizations = [], []
    lines = [re.sub(r'^[-*]\s+', '', line.strip().replace('**', '').replace('`', ''))
             for line in text.splitlines()]
    normalized = '\n'.join(lines)

    def field(name, body=normalized):
        values = re.findall(r'^' + re.escape(name) + r'\s*:\s*(.*?)\s*$', body, re.M | re.I)
        if len(values) != 1:
            errors.append('Expected exactly one ' + name)
            return None
        return values[0]

    decision = field('Decision')
    if decision not in (ACCEPT, KEEP):
        errors.append('Invalid decision')
    ids = [x['id'] for x in case['changes']]
    if not ids or len(ids) != len(set(ids)):
        errors.append('Invalid expected changed-block IDs')
    for key in ('baseline_sha256', 'candidate_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', case[key]):
            errors.append('Invalid harness-owned proof identity')
    sections = {}
    for match in re.finditer(r'^##\s+([^\n]+)\n(.*?)(?=^##\s|\Z)', normalized, re.M | re.S):
        name, body = match.groups()
        name = name.lower().strip()
        if name in sections:
            errors.append('Duplicate section ' + name)
        sections[name] = body.strip()
    checks = {}
    for name, allowed, accepting in (
        ('Target obligation', ('CLOSED', 'IMPROVED', 'UNCHANGED', 'REGRESSED', 'UNRESOLVED'), ('CLOSED', 'IMPROVED')),
        ('Preserved valid progress', ('PRESERVED', 'LOST', 'UNRESOLVED'), ('PRESERVED',)),
        ('Theorem actually established', ('COMPLETE_SAME_SCOPE', 'PARTIAL_STRONGER', 'PARTIAL_SAME', 'WEAKENED', 'UNRESOLVED'), ('COMPLETE_SAME_SCOPE', 'PARTIAL_STRONGER')),
        ('Qualifications and supplied repairs', ('NONE', 'INHERITED_GAPS_ONLY', 'NEW_REPAIR_REQUIRED', 'UNRESOLVED'), ('NONE', 'INHERITED_GAPS_ONLY')),
    ):
        body = sections.get(name.lower(), '')
        status = field('Status', body)
        explanation = re.sub(r'^(?:Status|Baseline completeness|Candidate completeness)\s*:.*$', '', body, flags=re.M | re.I).strip()
        if status not in allowed:
            errors.append('Invalid status in ' + name)
        if len(explanation) < 12:
            errors.append('Missing explanation in ' + name)
        checks[name] = {'status': status, 'permits_acceptance': status in accepting}
    scope = sections.get('theorem actually established', '')
    completeness = {role: field(role.title() + ' completeness', scope) for role in ('baseline', 'candidate')}
    if any(v not in ('COMPLETE', 'INCOMPLETE', 'UNRESOLVED') for v in completeness.values()):
        errors.append('Invalid completeness declaration')
    changes = {}
    for match in re.finditer(r'^###\s+(D\d+)\s*\n(.*?)(?=^###\s|\Z)', sections.get('changed dependencies', ''), re.M | re.S):
        ident, body = match.groups()
        if ident in changes:
            errors.append('Duplicate change ID ' + ident)
        status = field('Status', body)
        if status not in ('VERIFIED', 'INHERITED_GAP', 'INVALID', 'UNRESOLVED'):
            errors.append('Invalid change status ' + ident)
        if len(re.sub(r'^Status\s*:.*$', '', body, flags=re.M | re.I).strip()) < 12:
            errors.append('Missing changed-block verification ' + ident)
        changes[ident] = status
    if set(changes) != set(ids):
        errors.append('Changed-block coverage mismatch')
    if len(sections.get('decision basis', '')) < 12:
        errors.append('Missing decision basis')
    if checks['Theorem actually established']['status'] == 'COMPLETE_SAME_SCOPE' and completeness['candidate'] != 'COMPLETE':
        errors.append('Complete theorem conflicts with candidate completeness')
    if checks['Theorem actually established']['status'] == 'PARTIAL_STRONGER' and completeness['candidate'] != 'INCOMPLETE':
        errors.append('Partial theorem conflicts with candidate completeness')
    if checks['Qualifications and supplied repairs']['status'] == 'INHERITED_GAPS_ONLY' and completeness['candidate'] == 'COMPLETE':
        errors.append('Inherited gaps conflict with completeness claim')
    permits = all(x['permits_acceptance'] for x in checks.values()) and all(
        x in ('VERIFIED', 'INHERITED_GAP') for x in changes.values())
    if decision == ACCEPT and completeness['baseline'] == 'COMPLETE' and completeness['candidate'] != 'COMPLETE':
        errors.append('A complete baseline cannot be replaced with an incomplete candidate')
    if decision == ACCEPT and not permits:
        errors.append('Acceptance conflicts with comparative checks')
    return {'validator_version': VERSION, 'valid': not errors, 'model_decision': decision,
            'decision': decision if not errors else KEEP, 'checks': checks, 'changes': changes,
            'completeness': completeness, 'errors': errors, 'normalizations': normalizations,
            'warnings': [], 'hash_echo_is_authoritative': False,
            'response_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'normalized_markdown_sha256': hashlib.sha256(normalized.encode()).hexdigest(),
            'mechanical_validation_only': True}


def configure(module, directory):
    from pathlib import Path
    module.HERE = Path(directory)
    module.POLICY_ID = 'r2-r3-verified-progress-both-orders-v1'
    module.VERSION = VERSION
    module.validate_audit = validate_audit
    return module
