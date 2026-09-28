"""Synthetic algebra and geometry; no benchmark formulas or fixtures."""
import copy
import json
import pytest
import sympy as sp
from . import sum_of_squares as sos, geometry_program as geometry


@pytest.mark.parametrize('order',[(0,1,2),(2,1,0),(1,0,2)])
@pytest.mark.parametrize('offset',[-7,0,5])
def test_exact_quadratic_completion_and_json_replay(order, offset):
    variables=sp.symbols('u v w',real=True)
    u,v,w=variables
    expression=sp.expand(3*(2*u-v+offset)**2+sp.Rational(2,7)*(v+4*w-1)**2+11)
    symbols=[variables[i] for i in order]
    receipt=sos.quadratic(expression,symbols)
    assert receipt is not None
    assert sos.replay(json.loads(json.dumps(receipt)),expression,symbols)
    signs=geometry.Signs(symbols)
    assert signs.positive(expression)


@pytest.mark.parametrize('expression',['u**2-v**2','u*v','u**2+v','u**2-1','-u**2','u+1'])
def test_indefinite_and_unbounded_forms_rejected(expression):
    u,v=sp.symbols('u v',real=True)
    value=sp.sympify(expression,locals={'u':u,'v':v})
    assert sos.quadratic(value,[u,v]) is None
    assert geometry.Signs([u,v]).nonzero(value) is None


def test_nonnegative_is_not_strict_even_with_nonzero_coordinates():
    u,v=sp.symbols('u v',real=True)
    signs=geometry.Signs([u,v])
    signs.fact(u,True,'first_positive')
    signs.fact(v,True,'second_positive')
    value=sp.expand((3*u-2*v)**2)
    assert signs.positive(value,weak=True)
    assert signs.nonzero(value) is None
    signs.nonzeros.append((3*u-2*v,'distinct_scaled_coordinates'))
    signs.memo.clear()
    assert signs.nonzero(value)


def test_source_nonzero_square_and_missing_strictness():
    u,v,w=sp.symbols('u v w',real=True)
    value=sp.expand(5*u*u+2*(3*v-w)**2)
    signs=geometry.Signs([u,v,w])
    signs.fact(u,False,'weak')
    assert signs.positive(value,weak=True)
    assert signs.nonzero(value) is None
    signs.nonzeros.append((u,'nonzero'))
    signs.memo.clear()
    receipt=signs.nonzero(value)
    assert receipt and receipt['proof']['rule']=='checked_sum_of_squares'


def test_norm_preservation_for_higher_degree_rational_components():
    u,v,w=sp.symbols('u v w',real=True)
    parts=((u*u+1)/w,(u*v-v*v+2)/w)
    receipt=sos.rational_norm(parts,[u,v,w])
    value=sos.decode(receipt['target'],[u,v,w])
    assert sos.replay(receipt,value,[u,v,w])
    signs=geometry.Signs([u,v,w]);signs.add_norm(parts)
    assert signs.nonzero(value)
    # A positive numerator never makes a rational component denominator nonzero.
    assert signs.nonzero(w) is None


def test_cancelled_norm_factors_require_strict_square_evidence():
    u,v=sp.symbols('u v',real=True)
    signs=geometry.Signs([u,v]);signs.add_norm((u*v,u*v*v))
    value=u*u*v*v*(1+v*v)
    assert signs.positive(value,weak=True)
    assert signs.nonzero(value) is None
    signs.nonzeros.extend([(u,'u_nonzero'),(v,'v_nonzero')]);signs.memo.clear()
    assert signs.nonzero(value)
    assert signs.nonzero(1+v*v)
    json.loads(json.dumps(signs.nonzero(value)))
    json.loads(json.dumps(signs.positive(value,weak=True)))


@pytest.mark.parametrize('mutation',['weight','form','target','symbols','negative','float','powers'])
def test_tampered_square_certificates_rejected(mutation):
    u,v=sp.symbols('u v',real=True);value=(u+2*v-3)**2+5*v*v+1
    original=sos.quadratic(value,[u,v]);receipt=copy.deepcopy(original)
    if mutation=='weight':receipt['squares'][0]['weight']='13'
    elif mutation=='form':receipt['squares'][0]['form'][0]['coefficient']='19'
    elif mutation=='target':receipt['target'][0]['coefficient']='27'
    elif mutation=='symbols':receipt['symbols'].reverse()
    elif mutation=='negative':receipt['squares'][0]['weight']='-1'
    elif mutation=='float':receipt['squares'][0]['weight']='0.5'
    else:receipt['squares'][0]['form'][0]['powers'][0]=True
    with pytest.raises(ValueError):sos.replay(receipt,value,[u,v])


def test_replay_does_not_run_discovery(monkeypatch):
    u,v=sp.symbols('u v',real=True);value=2*(u-v+5)**2+3*v*v+7
    receipt=sos.quadratic(value,[u,v])
    def forbidden(*args):raise AssertionError('discovery invoked during replay')
    monkeypatch.setattr(sos,'quadratic',forbidden)
    assert sos.replay(receipt,value,[u,v])


def test_bounds_fail_closed():
    u,v=sp.symbols('u v',real=True)
    assert sos.quadratic(u**4+v**4,[u,v]) is None
    assert sos.rational_norm((u**20,v),[u,v]) is None
    assert sos.quadratic(u*u,sp.symbols('a:18',real=True)) is None


def test_constructed_projection_domain_keeps_square_structure():
    theorem='The vertical coordinate is positive.'
    body='''symbols = h, t
define = A :: (point 0 h)
define = B :: (point (sub (mul 3 t) 7) 0)
define = P :: (point 4 2)
define = F :: (foot P A B)
premise = height :: (gt h 0) :: The vertical coordinate is positive.
target = perpendicular :: (eq (dot (vsub P F) (vsub B A)) 0)'''
    text='# Decision\nCALL_TOOL\n\n# Semantic Bindings\nUse the stated coordinates.\n\n# Geometry Program\n```geometry-args\n'+body+'\n```'
    result=geometry.compile_program(text,theorem)
    assert result['report']['target_numerator']=='0'
    assert result['report']['construction_obligations']
    assert 'checked_sum_of_squares' in json.dumps(result['report'])
    weak=text.replace('(gt h 0)','(ge h 0)')
    with pytest.raises(ValueError,match='unproved construction denominator'):
        geometry.compile_program(weak,theorem)


def test_strict_source_plus_squares_and_unoriented_nonzero_factor():
    u,v,w=sp.symbols('u v w',real=True)
    signs=geometry.Signs([u,v,w])
    signs.fact(u*u-v*w,True,'strict_bound')
    signs.nonzeros.append((v-w,'distinct'))
    value=sp.expand(2*(u*u-v*w)+(u+w)**2)
    assert signs.positive(value)['rule']=='source_plus_checked_squares'
    assert signs.nonzero((v-w)*value)
    json.loads(json.dumps(signs.nonzero((v-w)**2*value)))
    assert signs.positive((v-w)*value) is None


def test_weak_source_plus_squares_does_not_imply_nonzero():
    u,v=sp.symbols('u v',real=True)
    signs=geometry.Signs([u,v]);signs.fact(u-v,False,'weak')
    value=sp.expand(2*(u-v)+(u+v)**2)
    assert signs.positive(value,weak=True)
    assert signs.nonzero(value) is None
    assert signs.nonzero((u-v)*value) is None
