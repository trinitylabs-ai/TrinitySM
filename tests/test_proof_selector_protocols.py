"""Selector adapters retain the frozen parser's mathematical safeguards."""
import pytest

from test_proof_selector import acceptance
from harnesses.proof_selector import protocols


@pytest.mark.parametrize('verdict', ['certified', 'Certified', 'rejected', 'Rejected'])
def test_noncanonical_acceptance_verdict_is_retried_as_format_failure(verdict):
    record = acceptance(verdict)
    parsed = protocols.parse_acceptance(record)
    assert parsed['valid'] is False
    assert 'Use uppercase CERTIFIED or REJECTED' in parsed['errors']


def test_uppercase_acceptance_keeps_existing_defect_checks():
    assert protocols.parse_acceptance(acceptance())['valid'] is True
    assert protocols.parse_acceptance(acceptance('REJECTED'))['valid'] is True
    record = acceptance().replace('## First Invalid Step\nNONE',
                                  '## First Invalid Step\nA necessary implication is false.')
    assert protocols.parse_acceptance(record)['valid'] is False
