"""Relative signs must follow from exact strict facts, including both orientations."""
import copy
import json

import pytest
import sympy as sp

from . import relative_sign as signs, geometry_program as geometry
from .test_geometry_program import program


@pytest.mark.parametrize('direction',[1,-1])
def test_relative_sign_without_any_absolute_orientation(direction):
    a,b,c=variables=sp.symbols('a b c',real=True)
    facts=[(a*b,True,'first'),(direction*b*c,True,'second')]
    proof=signs.prove(a*c,variables,facts,[])
    proof=json.loads(json.dumps(proof))
    assert proof['sign']==direction
    assert signs.replay(a*c,variables,facts,[],proof)==direction
    assert signs.prove(a,variables,facts,[]) is None
    for values in [(2,3,5),(-2,-3,-5)]:
        assignment=dict(zip(variables,(values[0],values[1],direction*values[2])))
        assert all(expr.subs(assignment)>0 for expr,_,_ in facts)
        assert sp.sign((a*c).subs(assignment))==direction


def test_higher_arity_and_even_factors_replay_through_rational_square():
    a,b,c,d,q=variables=sp.symbols('a b c d q',real=True)
    facts=[(-2*a*b*c*q**2,True,'many_factors'),(sp.Rational(3,7)*c*d,True,'second')]
    proof=signs.prove(a*b*d,variables,facts,[])
    assert proof['sign']==-1 and signs.replay(a*b*d,variables,facts,[],proof)==-1
    assert any(r['exponent']<0 for r in proof['ratio_factors'])


def test_weak_or_missing_nonzero_facts_cannot_establish_strict_orientation():
    a,b=variables=sp.symbols('a b',real=True)
    assert signs.prove(a*b,variables,[(a*b,False,'weak')],[]) is None
    assert signs.prove(a**2,variables,[],[]) is None
    assert signs.prove(a**2,variables,[],[(a,'nonzero')])['sign']==1
    assert signs.prove(-a**2,variables,[],[(a,'nonzero')])['sign']==-1
    assert signs.prove(sp.Integer(0),variables,[],[(a,'nonzero')]) is None


@pytest.mark.parametrize('change',[
    lambda p:p.update(sign=-p['sign']),
    lambda p:p.update(expression='unbound expression'),
    lambda p:p.update(nonzero_proofs=[]),
    lambda p:p['nonzero_proofs'][0].update(multiplier='0'),
    lambda p:p['nonzero_proofs'][0].update(source_expression='unbound source'),
    lambda p:p['strict_sources'][0].update(source='different source'),
    lambda p:p.update(ratio_coefficient='100'),
    lambda p:p.update(positive_source_indices=[999]),
])
def test_receipt_tampering_is_rejected(change):
    a,b,c=variables=sp.symbols('a b c',real=True)
    facts=[(a*b,True,'first'),(b*c,True,'second')]
    proof=signs.prove(a*c,variables,facts,[]);change(proof)
    with pytest.raises(ValueError):signs.replay(a*c,variables,facts,[],proof)


def test_changed_source_strictness_cannot_reuse_sign_proof():
    a,b,c=variables=sp.symbols('a b c',real=True)
    facts=[(a*b,True,'first'),(b*c,True,'second')]
    proof=signs.prove(a*c,variables,facts,[])
    facts[0]=(a*b,False,'first')
    with pytest.raises(ValueError):signs.replay(a*c,variables,facts,[],proof)


def test_search_bound_and_inconsistent_strict_facts(monkeypatch):
    a,b=variables=sp.symbols('a b',real=True)
    with pytest.raises(ValueError,match='inconsistent'):
        signs.prove(a*b,variables,[(-a**2,True,'impossible')],[])
    monkeypatch.setattr(signs,'MAX_FACTORS',1)
    assert signs.prove(a*b,variables,[(a*b,True,'given')],[]) is None


def test_fast_constant_ratio_check_matches_rational_cancellation():
    x,y=sp.symbols('x y',real=True)
    engine=geometry.Signs([x,y])
    expressions=[sp.Integer(0),sp.Integer(1),x,y,x+y,x-y,x*y,x*x+y*y,
                 (x+y)*(x-y),sp.Rational(2,3)*x+sp.Rational(4,3)*y,1/(x+y)]
    for top in expressions:
        for bottom in expressions[1:]:
            for scale in [sp.Integer(-3),sp.Rational(2,7),sp.Integer(1)]:
                expected=sp.cancel(scale*top/bottom)
                expected=expected if expected.is_Rational else None
                assert engine.rational_multiple(scale*top,bottom)==expected


@pytest.mark.parametrize('reverse',[False,True])
@pytest.mark.parametrize('transformed',[False,True])
def test_geometry_uses_relative_orientation_under_reflection_and_translation(reverse,transformed):
    coords=('(point 3 -2)','(point 3 -1)','(point (sub 3 h) -2)') if transformed else (
        '(point 0 0)','(point 1 0)','(point 0 h)')
    first='A B P' if reverse else 'P B A'
    body='symbols = h, p, q, r, s\n'
    body+='\n'.join('define = '+name+' :: '+value for name,value in zip(['A','B','C'],coords))+'\n'
    body+='define = P :: (point p q)\ndefine = Q :: (point r s)\n'
    body+='premise = interiorP :: (inside P A B C) :: @source:S0001\n'
    body+='premise = interiorQ :: (inside Q A B C) :: @source:S0001\n'
    body+='premise = angles :: (angle_equal '+first+' Q B A) :: @source:S0001\n'
    body+='target = same :: (eq h h)'
    theorem='Both points lie strictly inside the triangle, and the indicated ordinary angles are equal.'
    compiled=geometry.compile_program(program(body),theorem)
    angle=compiled['report']['angle_encodings'][0]
    assert angle['method']=='relative_signed_cotangent'
    assert angle['orientation_proofs'][0]['sign']==(-1 if reverse else 1)
    # Removing one interior constraint leaves the other angle's sign unknown.
    without=body.replace('premise = interiorQ :: (inside Q A B C) :: @source:S0001\n','')
    weaker=geometry.compile_program(program(without),theorem)
    assert weaker['report']['angle_encodings'][0]['method']=='squared_cosine_necessary_condition'
