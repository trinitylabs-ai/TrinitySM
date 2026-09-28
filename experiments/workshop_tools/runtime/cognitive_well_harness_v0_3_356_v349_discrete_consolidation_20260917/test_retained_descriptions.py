"""Extra retained descriptions remain audit context, never algebraic facts."""
import pytest

from . import geometry_program as compiler
from .test_geometry_program import program

THEOREM = 'The boundary condition remains part of the theorem.'


@pytest.mark.parametrize('description', ['A boundary restriction', '(ne x 0)', 'x = 0', 'Unknown words and punctuation: a, b!'])
@pytest.mark.parametrize('source', ['@source:S0001', 'The boundary condition'])
def test_description_is_preserved_without_changing_the_algebra(description, source):
    prefix = 'symbols = x\n'
    suffix = '\ntarget = t :: (eq x x)'
    old = compiler.compile_program(program(prefix+'retain = note :: '+source+' :: Boundary retained.'+suffix), THEOREM)
    new = compiler.compile_program(program(prefix+'retain = note :: '+description+' :: '+source+' :: Boundary retained.'+suffix), THEOREM)
    assert old['system'] == new['system']
    assert old['report']['source_bindings'] == new['report']['source_bindings']
    row = dict(new['report']['retained'][0])
    assert row.pop('description') == description
    assert row == old['report']['retained'][0]
    assert new['report']['source_semantics_verified'] is False


def test_retained_nonzero_claim_cannot_discharge_a_denominator():
    raw = program('''symbols = x, y
retain = note :: (ne x 0) :: @source:S0001 :: The denominator is nonzero.
premise = relation :: (eq (div y x) 0) :: @source:S0001
target = t :: (eq y 0)''')
    with pytest.raises(ValueError, match='unproved rational premise denominator'):
        compiler.compile_program(raw, THEOREM)


def test_extra_description_does_not_bypass_source_binding():
    raw = program('''symbols = x
retain = note :: An explanation :: @source:S9999 :: Not algebra.
target = t :: (eq x x)''')
    with pytest.raises(ValueError, match='source'):
        compiler.parse(raw, THEOREM)


def test_structural_definition_order_accepts_both_retained_forms():
    raw = program('''symbols = x
retain = first :: A boundary description :: @source:S0001 :: Not encoded.
define = twice :: (mul 2 x)
retain = second :: @source:S0001 :: Another retained condition.
target = t :: (eq twice (mul 2 x))''')
    compiled = compiler.compile_program(raw, THEOREM)
    assert any(row['rule']=='stable_definition_order' for row in compiled['report']['normalization']['edits'])
    assert len(compiled['report']['retained']) == 2


def test_five_fields_remain_ambiguous_and_rejected():
    raw = program('''symbols = x
retain = note :: description :: extra :: @source:S0001 :: Not encoded.
target = t :: (eq x x)''')
    with pytest.raises(ValueError, match='3 or 4 nonempty'):
        compiler.parse(raw, THEOREM)


def test_ordinary_norm_is_not_silently_changed_to_squared_length():
    raw = program('''symbols = x
define = length :: (norm (point x 1))
target = t :: (eq length length)''')
    with pytest.raises(ValueError, match='norm2 is squared length and is not interchangeable'):
        compiler.compile_program(raw, THEOREM)
    squared = compiler.compile_program(raw.replace('(norm ', '(norm2 '), THEOREM)
    assert squared['call_requested']
