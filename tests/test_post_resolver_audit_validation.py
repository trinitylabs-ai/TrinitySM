"""Regression cases for contradictory approvals and fail-closed audit handling."""
from copy import deepcopy

import pytest

from harnesses.post_resolver_audit.validation import ACCEPT, KEEP, select_candidate, validate_audit

CASE = {"baseline_sha256": "a" * 64, "candidate_sha256": "b" * 64,
        "changes": [{"id": "D001"}]}
TEXT = f"""Decision: ACCEPT_CANDIDATE
Baseline SHA256: {CASE['baseline_sha256']}
Candidate SHA256: {CASE['candidate_sha256']}
## Target obligation
Status: CLOSED
The target obligation follows from the displayed derivation.
## Preserved valid progress
Status: PRESERVED
The previously established intermediate result is retained.
## Theorem actually established
Status: SAME_SCOPE
All original domains and quantifiers are retained explicitly.
## Qualifications and supplied repairs
Status: NONE
## Changed dependencies
### D001
Status: VERIFIED
The changed identity follows from the displayed substitution.
## Decision basis
All required checks pass in the submitted candidate.
"""


def test_bare_none_needs_no_new_model_call_or_fabricated_explanation():
    result = validate_audit(TEXT, CASE)
    assert result['valid'] and result['decision'] == ACCEPT
    assert result['normalizations']


@pytest.mark.parametrize('old,new', [
    ('Status: NONE', 'Status: REQUIRED\nA missing derivation requires a repair before acceptance.'),
    ('Status: CLOSED', 'Status: OPEN'),
    ('Status: PRESERVED', 'Status: LOST'),
    ('Status: SAME_SCOPE', 'Status: WEAKENED'),
    ('Status: VERIFIED', 'Status: UNRESOLVED'),
])
def test_accept_cannot_override_reported_failure(old, new):
    result = validate_audit(TEXT.replace(old, new), CASE)
    assert result['model_decision'] == ACCEPT
    assert result['decision'] == KEEP and not result['valid']
    assert 'Acceptance conflicts with reported unresolved/failed checks' in result['errors']


@pytest.mark.parametrize('mutated', [
    TEXT.replace('### D001', '### D002'),
    TEXT + '\nDecision: KEEP_BASELINE\n',
    TEXT.replace('### D001', '### D001\nStatus: VERIFIED\nDuplicated block with sufficient explanation.\n### D001'),
    TEXT.replace('## Decision basis', '## Target obligation\nStatus: CLOSED\nDuplicated section has enough explanation.\n## Decision basis'),
    TEXT.replace('Status: NONE', 'Status: NONE\nStatus: REQUIRED'),
])
def test_binding_coverage_and_ambiguity_reject_approval(mutated):
    assert validate_audit(mutated, CASE)['decision'] == KEEP


def test_valid_rejection_is_not_a_protocol_error():
    text = TEXT.replace('ACCEPT_CANDIDATE', 'KEEP_BASELINE').replace('Status: CLOSED', 'Status: OPEN')
    result = validate_audit(text, CASE)
    assert result['valid'] and result['decision'] == KEEP


def pair():
    return [dict(validate_audit(TEXT, CASE), original_case_id='case', model_key='qwen', order=order)
            for order in ('forward', 'reverse')]


def test_missing_duplicate_wrong_pair_and_empty_votes_cannot_accept():
    votes = pair()
    for records in ([], votes[:1], [votes[0], votes[0]], votes + [votes[0]]):
        assert select_candidate('case', records, ('qwen',))['decision'] == KEEP
    wrong = deepcopy(votes)
    wrong[0]['original_case_id'] = 'another-case'
    assert select_candidate('case', wrong, ('qwen',))['decision'] == KEEP
    assert select_candidate('case', [], ())['decision'] == KEEP


def test_qwen_contradictory_forward_acceptance_blocks_two_order_adoption():
    votes = pair()
    assert select_candidate('case', votes, ('qwen',))['decision'] == ACCEPT
    failed = validate_audit(TEXT.replace('Status: NONE',
        'Status: REQUIRED\nThe reviewer supplied a repair missing from the submitted proof.'), CASE)
    votes[0].update(failed)
    assert votes[0]['model_decision'] == votes[1]['model_decision'] == ACCEPT
    assert select_candidate('case', votes, ('qwen',))['decision'] == KEEP


@pytest.mark.parametrize('text', [
    TEXT.replace('b' * 64, 'b' * 63),
    TEXT.replace('a' * 64, 'b' * 64),
    TEXT.replace('Baseline SHA256: ' + 'a' * 64 + '\n', ''),
    TEXT.replace('Candidate SHA256: ' + 'b' * 64 + '\n', ''),
    TEXT + '\nCandidate SHA256: typo\n',
])
def test_model_hash_echo_is_optional_and_diagnostic(text):
    result = validate_audit(text, CASE)
    assert result['valid'] and result['decision'] == ACCEPT
    assert result['warnings'] and result['hash_echo_is_authoritative'] is False


def test_actual_case_hash_metadata_still_must_be_valid():
    result = validate_audit(TEXT, {**CASE, 'candidate_sha256': 'invalid'})
    assert not result['valid'] and result['decision'] == KEEP
