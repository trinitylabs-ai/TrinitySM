"""Definitional lifting preserves algebra and cannot assume domain conditions."""
import json
from pathlib import Path

import pytest
import sympy as sp

from . import auxiliary_geometry as aux, geometry_program as compiler, geometry_workflow as workflow
from .test_geometry_program import program, decode


def evaluator(names=('x','y','z'), reserved=()):
    ev = compiler.AuxiliaryGeometryEvaluator(names)
    ev.initialize_auxiliaries(set(names)|set(reserved))
    return ev


def test_fresh_auxiliary_has_exact_triangular_equation_and_domain_obligation():
    ev = evaluator(reserved={'aux_value_1','aux_equation_1'})
    x,y,z = ev.algebra_symbols
    expression = ((x+y+z)**12)/(x-y)
    symbol = ev._lift_scalar(sp.cancel(expression))
    assert symbol not in {x,y,z} and str(symbol) != 'aux_value_1'
    label,equation = ev.auxiliary_equations[0]
    assert label != 'aux_equation_1'
    assert sp.cancel(equation.subs(symbol,expression)) == 0
    assert ev.auxiliary_rows[0]['earlier_symbols'] == ['x','y','z']
    assert ev.obligations and ev.obligations[-1]['_predicate'].residual == x-y
    assert ev._lift_scalar(sp.cancel(expression)) == symbol
    assert len(ev.auxiliary_rows) == 1


def test_auxiliaries_respect_the_existing_total_symbol_limit():
    ev = evaluator(tuple('x'+str(i) for i in range(16)))
    a,b,c = ev.algebra_symbols[:3]
    value = sp.expand((a+b+c)**12)
    assert ev._lift_scalar(value) == value
    assert ev.auxiliary_budget_exhausted and not ev.auxiliary_equations


def test_direct_success_does_not_invoke_the_fallback(monkeypatch):
    raw = program('symbols = x\ntarget = t :: (eq x x)')
    expected = compiler._compile_program(raw,'An arbitrary theorem.')
    monkeypatch.setattr(compiler.AuxiliaryGeometryEvaluator,'initialize_auxiliaries',lambda *a:pytest.fail('unexpected fallback'))
    assert compiler.compile_program(raw,'An arbitrary theorem.') == expected


def test_unrelated_parser_error_does_not_invoke_the_fallback(monkeypatch):
    monkeypatch.setattr(compiler.AuxiliaryGeometryEvaluator,'initialize_auxiliaries',lambda *a:pytest.fail('unexpected fallback'))
    with pytest.raises(ValueError):
        compiler.compile_program('Malformed draft.','An arbitrary theorem.')


@pytest.mark.parametrize('names',[('x','y','z'),('alpha','beta','gamma')])
def test_overflow_fallback_keeps_definition_equations_and_certifies(tmp_path,names,monkeypatch):
    # Exercise the real limit check at a smaller test budget; production keeps
    # 12,000 operations, which the saved-draft diagnostic separately exercises.
    monkeypatch.setattr(compiler.syntax,'MAX_EXPANDED_OPERATIONS',800)
    x,y,z = names
    raw = program(f'''symbols = {x}, {y}, {z}
define = H :: (pow (add {x} {y} {z}) 12)
define = K :: (pow H 2)
target = t :: (eq K (pow H 2))''')
    with pytest.raises(ValueError, match='expanded expression size limit'):
        compiler._compile_program(raw,'The stated identity is to be proved.')
    compiled = compiler.compile_program(raw,'The stated identity is to be proved.')
    report = compiled['report']['auxiliary_compilation']
    assert report['definitions'] and report['equations_excluded_from_guard_prover']
    assert len(compiled['system']['symbols']) <= 16
    symbols,equations,target,_ = decode(compiled['system'])
    assert len(equations) == len(report['definitions']) and target == 0
    # Use the real exact certificate backend on the new polynomial system.
    result = workflow.radical.export(compiled['system'],tmp_path/'certificate',timeout=10,memory=4096)
    assert result['verified']
    assert workflow.replay_certificate(compiled['system'],json.loads((tmp_path/'certificate/certificate.json').read_text()))['verified']


def test_lifted_rational_definition_does_not_prove_its_own_denominator(monkeypatch):
    monkeypatch.setattr(compiler.syntax,'MAX_EXPANDED_OPERATIONS',800)
    raw = program('''symbols = x, y, z
define = H :: (div (pow (add x y z) 12) (sub x y))
define = K :: (pow H 2)
target = t :: (eq K K)''')
    with pytest.raises(ValueError,match='unproved construction denominator'):
        compiler.compile_program(raw,'No nonzero condition is supplied.')


def test_missing_original_division_cannot_hide_behind_cancellation(monkeypatch):
    monkeypatch.setattr(compiler.syntax,'MAX_EXPANDED_OPERATIONS',800)
    raw = program('''symbols = x, y, z
define = H :: (pow (add x y z) 12)
define = canceled :: (div z z)
define = K :: (pow H 2)
target = t :: (eq K K)''')
    with pytest.raises(ValueError,match='unproved construction denominator'):
        compiler.compile_program(raw,'The cancellation has no nonzero justification.')


def test_auxiliary_equations_do_not_make_a_false_target_provable(tmp_path,monkeypatch):
    monkeypatch.setattr(compiler.syntax,'MAX_EXPANDED_OPERATIONS',800)
    raw = program('''symbols = x, y, z
define = H :: (pow (add x y z) 12)
define = K :: (pow H 2)
target = t :: (eq K 1)''')
    compiled = compiler.compile_program(raw,'There are no additional hypotheses.')
    assert compiled['report']['auxiliary_compilation']['definitions']
    symbols,equations,target,_ = decode(compiled['system'])
    # All-zero coordinates extend to all-zero auxiliaries: every defining
    # equation holds, while the proposed target residual is -1.
    assignment = dict.fromkeys(symbols,sp.Integer(0))
    assert all(eq.subs(assignment)==0 for _,eq in equations)
    assert target.subs(assignment) == -1
    assert not workflow.radical.export(compiled['system'],tmp_path/'false',timeout=5,memory=4096)['verified']
