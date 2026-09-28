"""Raw-decision audit policy with bound transport and diagnostic body checks."""
import re
from . import progress_diagnostics as body
from .legacy_validation import select_candidate

ACCEPT, KEEP = body.ACCEPT, body.KEEP
VERSION = 'bound-raw-unanimous-validation-v1'
POLICY_ID = 'r2-r3-bound-raw-unanimous-4of4-v1'

def validate_audit(text, case):
    parsed = body.validate_audit(text, case)
    # The original parser requires exactly one explicit, supported Decision.
    errors = []
    if parsed['model_decision'] not in (ACCEPT, KEEP):
        errors.append('Missing, duplicate, or ambiguous Decision')
    for key in ('baseline_sha256', 'candidate_sha256'):
        if not re.fullmatch(r'[0-9a-f]{64}', str(case.get(key, ''))):
            errors.append('Invalid harness-owned proof identity: ' + key)
    ids = [c.get('id') for c in case.get('changes', [])]
    if not ids or any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
        errors.append('Invalid expected change identifiers')
    valid = not errors
    return {**parsed, 'validator_version': VERSION, 'valid': valid,
            'decision': parsed['model_decision'] if valid else KEEP,
            'errors': errors,
            'body_validation_valid': parsed['valid'], 'body_validation_errors': parsed['errors'],
            'body_validation_policy': body.VERSION}
