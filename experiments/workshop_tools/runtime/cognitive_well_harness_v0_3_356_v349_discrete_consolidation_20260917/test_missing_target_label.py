"""A missing bookkeeping label never changes a supplied target expression."""
import pytest
from . import geometry_normalization as normal, geometry_program as geometry
from .test_geometry_program import program


def test_unlabeled_target_gets_only_a_fresh_deterministic_label():
    body = ('symbols = normalized_target, normalized_target_1, z\n'
            'premise = h :: (gt z 0) :: z is positive\n'
            'target = (eq z 0)')
    raw = program(body)
    fixed, record = normal.normalize(raw)
    assert fixed == raw.replace('target = (eq', 'target = normalized_target_2 :: (eq')
    assert {r['rule'] for r in record['edits']} == {'missing_target_label'}
    assert normal.normalize(fixed)[1]['applied'] is False
    result = geometry.compile_program(raw, 'z is positive')
    expected = geometry.compile_program(fixed, 'z is positive')
    assert result['system'] == expected['system']
    assert result['report']['target_numerator'] == 'z'


@pytest.mark.parametrize('tail', [
    'target = (eq z)', 'target = (eq z 0) extra',
    'target = (gt z 0)', 'target = (eq z 0)\ntarget = second :: (eq z z)',
    'target = (eq z 0)\ndefine = later :: 0',
])
def test_ambiguous_or_invalid_target_is_not_labeled(tail):
    raw = program('symbols = z\n' + tail)
    assert normal.normalize(raw)[0] == raw
    with pytest.raises(ValueError):
        geometry.parse(raw, 'arbitrary source')
