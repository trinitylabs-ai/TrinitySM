"""Generic saved-draft recovery must preserve the exact problem and obligations."""
import pytest

from . import geometry_normalization as normal, geometry_program as geometry
from .test_geometry_program import BODY, THEOREM, program


def replay_edits(raw, record):
    lines = raw.splitlines()
    for edit in record['edits']:
        assert lines[edit['line']-1] == edit['before']
        lines[edit['line']-1] = edit['after']
    return '\n'.join(lines)


def test_interleaved_premise_reordering_preserves_compiled_system_and_every_line():
    lines = BODY.splitlines()
    premise = next(line for line in lines if line.startswith('premise = interior'))
    lines.remove(premise)
    lines.insert(1, premise)
    # Combine independent repairs to exercise the ordered edit ledger.
    raw = program('\n'.join(lines).replace('define = A ::', 'define A ::'))
    fixed, record = normal.normalize(raw)
    assert fixed == program(BODY)
    assert replay_edits(raw, record) == fixed
    assert normal.normalize(fixed)[1]['applied'] is False
    parsed = geometry.parse(raw, THEOREM)
    expected = geometry.parse(program(BODY), THEOREM)
    parsed.pop('normalization'); expected.pop('normalization')
    assert parsed == expected
    compiled = geometry.compile_program(raw, THEOREM)
    canonical = geometry.compile_program(program(BODY), THEOREM)
    compiled['report'].pop('normalization'); canonical['report'].pop('normalization')
    assert compiled == canonical


@pytest.mark.parametrize('source', ['@source:S0001', '"@source:S0001"', "'@source:S0001'", '`@source:S0001`'])
def test_missing_separator_before_explicit_source_id_preserves_source_and_expression(source):
    body = f'symbols = x\npremise = positive :: (gt x 0) {source}\ntarget = false_claim :: (eq x 0)'
    raw = program(body)
    fixed, record = normal.normalize(raw)
    assert fixed == raw.replace(f'(gt x 0) {source}', f'(gt x 0) :: {source}')
    assert replay_edits(raw, record) == fixed
    assert normal.normalize(fixed)[1]['applied'] is False
    parsed = geometry.parse(raw, 'The scalar is positive.')
    assert parsed['premises'][0][1] == ['gt', 'x', 0]
    assert parsed['target'][1] == ['eq', 'x', 0]


def test_optional_target_source_is_validated_and_never_becomes_a_premise():
    body = 'symbols = x\ntarget = conclusion :: (eq x 0)'
    raw = program(body + ' :: @source:S0001')
    theorem = 'The conclusion is to be proved.'
    plain = geometry.compile_program(program(body), theorem)
    bound = geometry.compile_program(raw, theorem)
    assert bound['system'] == plain['system']
    assert bound['report']['target_numerator'] == 'x'
    parsed = geometry.parse(raw, theorem)
    assert parsed['premises'] == [] and len(parsed['source_bindings']) == 1
    for bad in ['@source:S9999', 'invented source quote']:
        with pytest.raises(ValueError):
            geometry.parse(program(body+' :: '+bad), theorem)


@pytest.mark.parametrize('body', [
    'symbols = x\npremise = h :: (eq x 0) :: known\ndefine = D :: E\ndefine = E :: x\ntarget = t :: (eq D 0)',
    'symbols = x\npremise = h :: (eq x 0) :: known\ndefine = D :: E\ndefine = E :: D\ntarget = t :: (eq D 0)',
    'symbols = x\npremise = h :: (eq x 0) :: known\ndefine = x :: 0\ntarget = t :: (eq x 0)',
    'symbols = x\npremise = h :: (eq x 0) :: known\ndefine = D :: x\ndefine = D :: 0\ntarget = t :: (eq D 0)',
    'symbols = x\ntarget = t :: (eq x 0)\ndefine = D :: x',
    'symbols = x\npremise = h :: (eq x 0) @source:S0001 extra\ntarget = t :: (eq x 0)',
    'symbols = x\npremise = h :: (eq x 0 @source:S0001\ntarget = t :: (eq x 0)',
    'symbols = x\nretain = h :: extra :: ambiguous :: @source:S0001 :: explanation\ntarget = t :: (eq x 0)',
])
def test_ambiguous_records_and_binding_changes_are_not_repaired(body):
    raw = program(body)
    fixed, record = normal.normalize(raw)
    assert fixed == raw and not record['applied']
    with pytest.raises(ValueError):
        geometry.parse(raw, 'known')


def test_size_and_symbol_limits_are_not_relaxed():
    names = ', '.join('x'+str(i) for i in range(17))
    with pytest.raises(ValueError, match='1..16 symbols'):
        geometry.parse(program('symbols = '+names+'\ntarget = t :: (eq x0 x0)'), 'known')


def test_error_distinguishes_wrong_arity_from_duplicate_label():
    with pytest.raises(ValueError, match='retain field requires 3'):
        geometry.parse(program('symbols = x\nretain = h :: extra :: ambiguous :: @source:S0001 :: reason\ntarget = t :: (eq x x)'), 'known')
    with pytest.raises(ValueError, match='duplicate symbol or field label: x'):
        geometry.parse(program('symbols = x\ndefine = x :: 0\ntarget = t :: (eq x x)'), 'known')
