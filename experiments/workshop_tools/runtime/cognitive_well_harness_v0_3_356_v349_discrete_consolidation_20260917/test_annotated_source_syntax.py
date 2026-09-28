"""Generic source syntax is exact, bounded and never establishes entailment."""
import pytest

from . import source_binding as source, geometry_program as geometry
from . import geometry_normalization as normal
from .test_geometry_program import program


@pytest.mark.parametrize('slot', [
    '@source:S0002 "positive scalar"',
    '"positive scalar" @source:S0002',
    '@source:S0002 “positive scalar”',
])
def test_annotation_preserves_exact_offsets_and_both_bindings(slot):
    theorem = 'First line.\nLet z be a positive scalar.\nAnother line.'
    text, receipt = source.resolve(slot, theorem, label='h')
    assert text == 'positive scalar'
    assert theorem[receipt['start']:receipt['end']] == text
    assert receipt['reference'] == '@source:S0002'
    assert receipt['submitted'] == slot
    assert receipt['theorem_sha256'] == source.sha(theorem)


@pytest.mark.parametrize('slot', [
    '@source:S0001 "positive scalar"',  # Quote exists, but in another span.
    '@source:S9999 "positive scalar"',
    '@source:S0002 "strictly positive"',
    '@source:S0002 ""',
    '@source:S0002 "positive scalar" extra',
    '@source:S0002 positive scalar',
    '@source:S0002 "@source:S0002"',
])
def test_annotation_never_discards_invalid_component(slot):
    with pytest.raises(ValueError):
        source.resolve(slot, 'First line.\nLet z be a positive scalar.', label='h')


@pytest.mark.parametrize('suffix', [
    ' :: @source:S0001 "positive scalar"',
    ' :: "positive scalar" @source:S0001',
    ' :: "positive scalar" :: @source:S0001',
    ' :: @source:S0001 :: "positive scalar"',
    ' @source:S0001 "positive scalar"',
])
def test_variants_preserve_algebra_and_do_not_prove_false_target(suffix):
    theorem = 'Let z be a positive scalar.'
    body = 'symbols = z\npremise = h :: (gt z 0)'
    target = '\ntarget = t :: (eq z 0)'
    raw = program(body + suffix + target)
    canonical = program(body + ' :: positive scalar' + target)
    fixed, receipt = normal.normalize(raw)
    assert normal.normalize(fixed)[0] == fixed
    assert not normal.normalize(fixed)[1]['applied']
    lines = raw.splitlines()
    for edit in receipt['edits']:
        assert lines[edit['line'] - 1] == edit['before']
        lines[edit['line'] - 1] = edit['after']
    assert '\n'.join(lines) == fixed
    result = geometry.compile_program(raw, theorem)
    expected = geometry.compile_program(canonical, theorem)
    assert result['system'] == expected['system']
    assert result['report']['target_numerator'] == 'z'
    assert result['report']['source_semantics'] == 'MODEL_AUDIT_REQUIRED'


def test_invalid_quote_is_not_fixed_by_separator_normalization():
    raw = program('symbols = z\npremise = h :: (gt z 0) :: "invented" :: @source:S0001\ntarget = t :: (eq z 0)')
    with pytest.raises(ValueError, match='source excerpt not found'):
        geometry.parse(raw, 'Let z be a positive scalar.')
