"""Clearing source equalities cannot discard an original domain condition."""
import pytest
import sympy as sp

from . import geometry_program as geometry, geometry_workflow as workflow
from .test_geometry_program import program, decode


THEOREM = 'The denominator is nonzero. The two fractions are equal.'
BODY = '''symbols = x, y, d
premise = guard :: (ne d 0) :: The denominator is nonzero.
premise = relation :: (eq (div x d) y) :: The two fractions are equal.
target = conclusion :: (eq x (mul d y))'''


def test_rational_equality_and_certificate_are_independently_replayable(tmp_path):
    compiled = geometry.compile_program(program(BODY), THEOREM)
    rows = compiled['report']['rational_premise_encodings']
    assert len(rows) == 1 and rows[0]['identity_checked'] and rows[0]['denominator_proof']
    assert rows[0]['label'] == 'relation' and rows[0]['denominator'] == 'd'
    symbols, equations, target, _ = decode(compiled['system'])
    x, y, d = symbols
    assert any(sp.expand(equation-(x-d*y)) == 0 or sp.expand(equation+(x-d*y)) == 0 for _, equation in equations)
    result = workflow.certificate_search(compiled, tmp_path/'certificate', timeout=20, memory=4096)
    assert result['exact_verified']
    import json
    from pathlib import Path
    path = Path(result['certificate_root'])
    assert workflow.replay_certificate(json.loads((path/'system.json').read_text()),
        json.loads((path/'certificate.json').read_text()))['verified']
    assert compiled['report']['source_semantics_verified'] is False


def test_guard_can_follow_the_equality_without_using_the_cleared_equation():
    lines = BODY.splitlines()
    lines[1], lines[2] = lines[2], lines[1]
    a = geometry.compile_program(program(BODY), THEOREM)
    b = geometry.compile_program(program('\n'.join(lines)), THEOREM)
    assert a['system'] == b['system']
    assert a['report']['rational_premise_encodings'] == b['report']['rational_premise_encodings']


@pytest.mark.parametrize('expression', ['(div x d)', '(div (sub d 1) d)'])
def test_missing_nonzero_condition_is_not_assumed(expression):
    raw = program('symbols = x, d\npremise = relation :: (eq '+expression+' 0) :: The two fractions are equal.\ntarget = t :: (eq x x)')
    with pytest.raises(ValueError, match='unproved rational premise denominator'):
        geometry.compile_program(raw, THEOREM)


def test_canceled_original_denominator_is_still_required():
    body = 'symbols = d\npremise = relation :: (eq (div d d) 1) :: The two fractions are equal.\ntarget = t :: (eq d d)'
    with pytest.raises(ValueError, match='unproved construction denominator'):
        geometry.compile_program(program(body), THEOREM)
    guarded = body.replace('premise = relation', 'premise = guard :: (ne d 0) :: The denominator is nonzero.\npremise = relation')
    compiled = geometry.compile_program(program(guarded), THEOREM)
    assert compiled['report']['rational_premise_encodings'] == []
    assert any(o['expression']=='d' for o in compiled['report']['construction_obligations'])


def test_common_denominator_requires_both_original_factors():
    body = '''symbols = x, y, d, e
premise = d_guard :: (ne d 0) :: The denominator is nonzero.
premise = e_guard :: (ne e 0) :: The denominator is nonzero.
premise = relation :: (eq (div x d) (div y e)) :: The two fractions are equal.
target = conclusion :: (eq (mul x e) (mul y d))'''
    compiled = geometry.compile_program(program(body), THEOREM)
    assert compiled['report']['rational_premise_encodings'][0]['denominator_proof']
    with pytest.raises(ValueError, match='unproved rational premise denominator'):
        geometry.compile_program(program(body.replace('premise = e_guard :: (ne e 0) :: The denominator is nonzero.\n','')), THEOREM)


def test_false_goal_does_not_become_a_verified_identity(tmp_path):
    wrong = BODY.replace('(eq x (mul d y))', '(eq x (add (mul d y) 1))')
    compiled = geometry.compile_program(program(wrong), THEOREM)
    assert not workflow.certificate_search(compiled, tmp_path/'wrong', timeout=10, memory=4096)['exact_verified']


def test_inequalities_preserve_denominator_sign():
    bad = BODY.replace('(eq (div x d) y)', '(gt (div x d) y)')
    compiled = geometry.compile_program(program(bad), THEOREM)
    row = compiled['report']['rational_premise_encodings'][0]
    assert row['relation'] == 'gt' and row['denominator_proof']
    assert row['polynomial_comparison'] == '-d**2*y + d*x'
    assert compiled['report']['equations'] == {'identity': '0'}
