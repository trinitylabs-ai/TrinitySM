"""Completeness, branches, original domains, endpoints and exact replay."""
import copy
import json
from pathlib import Path

import pytest
import sympy as sp

from . import root_classification as roots, root_workflow as workflow, proof_harness as harness, matched_tools


def program(body, bindings='The variable, expression and interval are those in the source claim.'):
    return '# Decision\n\nCALL_TOOL\n\n# Semantic Bindings\n\n'+bindings+'\n\n# Root Program\n\n```root-args\n'+body+'\n```'


def body(expression, *, mode='roots', interval='(open -2 2)', variable='z'):
    return f'variable = {variable}\ninterval = {interval}\nmode = {mode}\n'+('function' if mode == 'stationary_points' else 'expression')+' = '+expression


@pytest.mark.parametrize('name', ['z', 'parameter'])
def test_complete_extrema_and_sign_cells_are_independent_of_variable_name(name):
    text = program(body(f'(sub (pow {name} 3) (mul 3 {name}))', mode='stationary_points', variable=name))
    result = roots.compute(text)
    assert [r['root']['exact'] for r in result['roots']] == ['-1', '1']
    assert [r['classification'] for r in result['roots']] == ['local_maximum', 'local_minimum']
    assert [r['sign'] for r in result['sign_cells']] == [1, -1, 1]
    assert not result['numerical_tolerance_used']
    assert roots.compute(text) == result


def test_squaring_does_not_admit_the_negative_square_root_branch():
    text = program(body('(sub (sqrt (add z 1)) z)', interval='(open -1 3)'))
    result = roots.compute(text)
    assert result['root_count'] == 1
    checks = result['root_isolation']['branch_checks']
    assert len(checks) == 2 and sum(r['accepted_original_branch'] for r in checks) == 1
    assert result['roots'][0]['root']['sturm_root_count'] == 1
    assert result == roots.compute(text)


def test_even_multiplicity_stationary_point_is_not_an_extremum():
    result = roots.compute(program(body('(pow z 3)', mode='stationary_points')))
    assert result['root_count'] == 1
    assert result['roots'][0]['classification'] == 'stationary_no_extremum'


def test_double_zero_radical_coefficients_are_retained():
    result = roots.compute(program(body('(mul (sub z 1) (add (sqrt (add z 3)) 2))')))
    assert result['root_count'] == 1 and result['roots'][0]['root']['exact'] == '1'


@pytest.mark.parametrize('interval, expected', [('(open 0 1)', 0), ('(closed 0 1)', 2), ('(left_open 0 1)', 1), ('(right_open 0 1)', 1)])
def test_exact_interval_endpoint_inclusion(interval, expected):
    result = roots.compute(program(body('(mul z (sub z 1))', interval=interval)))
    assert result['root_count'] == expected


def test_algebraic_coefficients_and_endpoint_equalities():
    result = roots.compute(program(body('(sub (mul 2 (pow z 2)) 1)', interval='(closed 0 (div 1 (sqrt 2)))')))
    assert result['root_count'] == 1
    assert result['roots'][0]['classification'] == 'boundary_root'


@pytest.mark.parametrize('expression, interval', [
    ('(div (mul z (sub z 1)) z)', '(open -2 2)'),
    ('(div 1 (sub z 1))', '(open 0 2)'),
    ('(sqrt z)', '(open -1 2)'),
    ('(sqrt z)', '(closed 0 2)'),
    ('(div (sub z 1) (sub (sqrt (add z 1)) z))', '(open 0 3)'),
])
def test_invalid_original_domains_are_never_silently_dropped(expression, interval):
    with pytest.raises(ValueError):
        roots.compute(program(body(expression, interval=interval)))


def test_singular_open_endpoint_is_allowed():
    result = roots.compute(program(body('(div (sub z 1) z)', interval='(open 0 2)')))
    assert result['root_count'] == 1


@pytest.mark.parametrize('expression', ['(add (sqrt (add z 3)) (sqrt (add z 4)))', '(sin z)', '(pow z 999)', '(add z undeclared)', '(sqrt (sqrt (add z 3)))'])
def test_unsupported_inputs_fail_closed(expression):
    with pytest.raises(ValueError):
        roots.compile_program(program(body(expression)))


def test_exact_replay_rejects_tampered_root_or_sign():
    text = program(body('(sub (pow z 2) 1)'))
    result = roots.compute(text)
    modified = copy.deepcopy(result)
    modified['roots'].pop()
    with pytest.raises(ValueError, match='replay differs'):
        workflow.replay(text, modified, harness.Config())


def test_public_executor_runs_the_advertised_operation(tmp_path):
    text = '```root-args\n'+body('(sub (pow z 2) 1)')+'\n```'
    result = matched_tools.run(operation=roots.OPERATION, arguments_markdown=text, output=tmp_path/'tool')
    assert result['verdict'] == 'ROOT_CLASSIFICATION_VERIFIED'
    assert result['root_result']['root_count'] == 2
    assert matched_tools.replay(operation=roots.OPERATION, arguments_markdown=text, saved_result=result) == result


def test_zero_continuum_does_not_become_an_empty_finite_root_set():
    with pytest.raises(ValueError, match='identically zero'):
        roots.compute(program(body('(sub z z)')))


def test_runtime_has_no_problem_specific_formulas_or_paths():
    for module in (roots, workflow):
        text = Path(module.__file__).read_text()
        for forbidden in ['PB-Basic-', 'PB-Advanced-', 'imo2026', 't10_r01', 'benchmarks/', '419904', '7776']:
            assert forbidden not in text
