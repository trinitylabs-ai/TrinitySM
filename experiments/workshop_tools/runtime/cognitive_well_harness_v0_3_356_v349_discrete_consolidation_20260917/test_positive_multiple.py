"""Synthetic source facts; no benchmark data or saved proof formulas."""
import copy

import pytest
import sympy as sp

from . import positive_multiple as rule
from . import geometry_program as geometry
from .test_geometry_program import program


def setup(names='m x y', sign=1, weak=False):
    m, x, y = sp.symbols(names, real=True)
    signs = geometry.Signs([m, x, y])
    signs.nonzeros.append((m, 'known_factor'))
    signs.fact(sign*m*x, not weak, 'first')
    signs.fact(sign*m*y, not weak, 'second')
    return signs, (m, x, y)


@pytest.mark.parametrize('names', ['m x y', 'scale alpha beta'])
@pytest.mark.parametrize('sign', [1, -1])
def test_nonzero_without_assuming_an_orientation(names, sign):
    signs, (m, x, y) = setup(names, sign)
    target = x + y
    assert signs.positive(target) is None
    assert signs.positive(-target) is None
    result = signs.nonzero(target)
    assert result['rule'] == 'factor_of_positive_multiple'
    assert rule.replay(result['identity'], target, [m, x, y], signs.facts)
    assert signs.nonzero(target**2)


@pytest.mark.parametrize('second_strict', [False, True])
def test_positive_weighted_combination_tracks_strictness(second_strict):
    m, x, y = sp.symbols('m x y', real=True)
    facts = [(m*x, True, 'first'), (m*y, second_strict, 'second')]
    proof = rule.Prover([m, x, y]).prove(x/2+3*y/7, facts, [(m, 'candidate')])
    assert rule.replay(proof, x/2+3*y/7, [m, x, y], facts)


def test_weak_product_and_individual_nonzeros_are_insufficient():
    signs, (m, x, y) = setup(weak=True)
    assert signs.nonzero(x+y) is None
    signs.nonzeros.extend([(x, 'x_nonzero'), (y, 'y_nonzero')])
    # x=1, y=-1, m=0 would violate m!=0, but weak products alone allow
    # x=y=0. Individual nonzeros alone permit x=-y with no sign facts.
    uncorrelated = geometry.Signs([m, x, y])
    uncorrelated.nonzeros.extend(signs.nonzeros)
    assert uncorrelated.nonzero(x+y) is None
    assert signs.nonzero(sp.Integer(0)) is None


@pytest.mark.parametrize('mutation', ['target', 'multiplier', 'weight', 'strict', 'label', 'source'])
def test_tampered_receipt_rejected(mutation):
    signs, (m, x, y) = setup()
    receipt = signs.nonzero(x+y)['identity']
    changed = copy.deepcopy(receipt)
    if mutation == 'target':
        changed['target'] = rule.codec.encode(x-y, [m, x, y])
    elif mutation == 'multiplier':
        changed['multiplier'] = rule.codec.encode(-m, [m, x, y])
    elif mutation == 'weight':
        changed['sources'][0]['weight'] = '-1'
    elif mutation == 'strict':
        changed['sources'][0]['strict'] = False
    elif mutation == 'label':
        changed['sources'][0]['label'] = 'invented'
    else:
        changed['sources'][0]['expression'] = rule.codec.encode(m*(x+1), [m, x, y])
    with pytest.raises(ValueError):
        rule.replay(changed, x+y, [m, x, y], signs.facts)


def test_removed_or_weakened_source_cannot_replay():
    signs, (m, x, y) = setup()
    receipt = signs.nonzero(x+y)['identity']
    for changed in [signs.facts[:1], [(p, False, label) for p, _, label in signs.facts]]:
        with pytest.raises(ValueError):
            rule.replay(receipt, x+y, [m, x, y], changed)


def test_cache_tracks_new_or_removed_admitted_facts():
    signs, (m, x, y) = setup(weak=True)
    prover = signs.positive_multiple_prover
    assert prover.prove(x+y, signs.facts, signs.nonzeros) is None
    signs.fact(m*x, True, 'new_strict')
    receipt = prover.prove(x+y, signs.facts, signs.nonzeros)
    assert rule.replay(receipt, x+y, [m, x, y], signs.facts)
    signs.facts.pop()
    assert prover.prove(x+y, signs.facts, signs.nonzeros) is None


def test_bounded_search_declines_large_polynomial():
    m, x, y = sp.symbols('m x y', real=True)
    assert rule.Prover([m, x, y]).prove(x**20+y, [(m*x**20, True, 'a'),
        (m*y, True, 'b')], [(m, 'candidate')]) is None


def test_rational_domain_recovered_from_existing_premises():
    theorem = 'The parameter is nonzero. Both products are positive.'
    body = '''symbols = m, x, y
premise = factor :: (ne m 0) :: The parameter is nonzero.
premise = first :: (gt (mul m x) 0) :: Both products are positive.
premise = second :: (gt (mul m y) 0) :: Both products are positive.
target = identity :: (eq (div (add x y) (add x y)) 1)'''
    compiled = geometry.compile_program(program(body), theorem)
    obligations = compiled['report']['construction_obligations']
    assert any(row['proof']['rule'] == 'factor_of_positive_multiple' for row in obligations)
    assert compiled == geometry.compile_program(program(body), theorem)
    # Without the strict source facts, the cancellation is not admissible.
    with pytest.raises(ValueError, match='unproved construction denominator'):
        geometry.compile_program(program(body.replace('(gt (mul m x) 0)', '(ge (mul m x) 0)')
                                             .replace('(gt (mul m y) 0)', '(ge (mul m y) 0)')), theorem)


def test_pending_rational_premises_cannot_bootstrap_domain():
    theorem = 'The parameter is nonzero. Both quotients are positive.'
    body = '''symbols = m, x, y
premise = factor :: (ne m 0) :: The parameter is nonzero.
premise = first :: (gt (div (mul m x) (add x y)) 0) :: Both quotients are positive.
premise = second :: (gt (div (mul m y) (add x y)) 0) :: Both quotients are positive.
target = identity :: (eq x x)'''
    with pytest.raises(ValueError, match='unproved source comparison domain'):
        geometry.compile_program(program(body), theorem)
