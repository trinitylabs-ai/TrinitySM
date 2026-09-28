import copy
import json
import pytest
import sympy as sp

from . import real_branches as real, radical_certificate as radical


def system(equations,target,conditions=(),guards=()):
    variables=set(target.free_symbols)
    for e in equations:variables |= e.free_symbols
    for relation,value in conditions:variables |= value.free_symbols
    for value in guards:variables |= value.free_symbols
    symbols=sorted(variables,key=str) or [sp.Symbol('x',real=True)]
    value=radical.system_payload(symbols,[(f'E{i}',e) for i,e in enumerate(equations)],target,{f'G{i}':g for i,g in enumerate(guards)})
    value['real_conditions']=[{'label':f'C{i}','relation':r,'polynomial':radical.laurent._payload(v,symbols)} for i,(r,v) in enumerate(conditions)]
    return value


x,y,z=sp.symbols('x y z',real=True)


@pytest.mark.parametrize('equations,target,conditions',[
    ([x*x-y*y],x-y,[('gt',x),('gt',y)]),
    ([x*x-y*y],x+y,[('gt',x),('gt',-y)]),
    ([x*x-1],x-1,[('gt',x)]),
    ([(x-1)*(x+2)],x-1,[('ge',x)]),
    ([x*x+y*y],x,[]),
    ([2*(x-y)**2+3*z*z],x-y,[]),
    ([x*x-y*y,z-x-y],x-y,[('gt',x),('gt',y)]),
    ([x*x*(x-2)],x-2,[('ne',x)]),
    ([(x-y)*(x+y),y-z],x-z,[('gt',x),('gt',y)]),
    ([x-y],x-y,[]),
])
def test_exact_real_consequences(equations,target,conditions):
    request=system(equations,target,conditions)
    result=real.solve(request)
    assert result['verified'],result
    assert real.replay(request,result['certificate'])['verified']
    markdown,rendering=real.render(request,result['certificate'])
    assert rendering['real_branch_derivation_supplied']
    assert 'real numbers' in markdown and '\\[' in markdown


@pytest.mark.parametrize('equations,target,conditions',[
    ([x*x-y*y],x-y,[]),
    ([x*x-y*y],x-y,[('gt',x)]),
    ([x*x-1],x-1,[('ne',x)]),
    ([x*y],x,[('ge',y)]),
    ([x*x+y*y-1],x,[]),
    ([x-y],x+y,[('gt',x),('gt',y)]),
])
def test_false_or_unresolved_consequence_not_certified(equations,target,conditions):
    result=real.solve(system(equations,target,conditions))
    assert not result['verified'] and result['verdict']=='INCONCLUSIVE'
    assert 'certificate' not in result


def example():
    request=system([x*x-y*y],x-y,[('gt',x),('gt',y)])
    result=real.solve(request)
    assert result['verified']
    assert result['certificate']['tree']['kind']=='split'
    return request,result['certificate']


def test_replay_independent_of_discovery(monkeypatch):
    request,certificate=example()
    def forbidden(*args,**kwargs):raise AssertionError('search used in replay')
    monkeypatch.setattr(sp,'factor_list',forbidden)
    monkeypatch.setattr(sp,'reduced',forbidden)
    monkeypatch.setattr(real.Search,'node',forbidden)
    assert real.replay(request,certificate)['verified']


@pytest.mark.parametrize('change',[
    lambda c:c['tree']['children'].pop(),
    lambda c:c['tree'].__setitem__('coefficient','2'),
    lambda c:c['tree']['factors'][0].__setitem__('exponent',2),
    lambda c:c['tree']['children'][0].__setitem__('multipliers',[]),
    lambda c:c['tree']['children'][1]['combination'][0].__setitem__('weight','-1'),
    lambda c:c['tree']['children'][1]['combination'][0].__setitem__('index',999),
    lambda c:c['tree']['children'][1].__setitem__('kind','unknown'),
    lambda c:c.__setitem__('system_sha256','changed'),
])
def test_tampered_branch_certificate_rejected(change):
    request,certificate=example()
    broken=copy.deepcopy(certificate);change(broken)
    with pytest.raises(ValueError):real.replay(request,broken)


def test_missing_or_weakened_sign_binding_rejected():
    request,certificate=example()
    for index in range(2):
        changed=copy.deepcopy(request)
        changed['real_conditions'][index]['relation']='ge'
        with pytest.raises(ValueError,match='binding'):real.replay(changed,certificate)
    changed=copy.deepcopy(request);changed['real_conditions']=[]
    with pytest.raises(ValueError,match='binding'):real.replay(changed,certificate)


def test_weak_zero_sum_cannot_close_branch_even_with_rebound_hash():
    request,certificate=example()
    changed=copy.deepcopy(request)
    for row in changed['real_conditions']:row['relation']='ge'
    rebound=copy.deepcopy(certificate)
    rebound['system_sha256']=radical.backends.division.exact_tools.stable_hash(changed)
    with pytest.raises(ValueError,match='weak zero'):real.replay(changed,rebound)


def test_complex_coefficients_rejected():
    request=system([x],x)
    request['target']['terms'][0]['coefficient']['imaginary_numerator']=1
    with pytest.raises(ValueError,match='rational'):real.solve(request)


def test_bound_returns_inconclusive(monkeypatch):
    monkeypatch.setattr(real,'MAX_NODES',1)
    result=real.solve(system([x*x-y*y],x-y,[('gt',x),('gt',y)]))
    assert not result['verified']


def test_squares_certificate_tampering_rejected():
    request=system([x*x+y*y],x)
    result=real.solve(request);certificate=copy.deepcopy(result['certificate'])
    assert certificate['tree']['kind']=='squares'
    certificate['tree']['decomposition']['squares'][0]['weight']='-1'
    with pytest.raises(ValueError):real.replay(request,certificate)


def test_render_includes_all_cases_and_source_signs():
    request,certificate=example()
    text,_=real.render(request,certificate)
    assert 'Case 1' in text and 'Case 2' in text
    assert text.count('>0')>=2
    assert 'contradict' in text


def test_repeat_deterministic():
    request=system([x*x-y*y],x-y,[('gt',x),('gt',y)])
    assert real.solve(request)==real.solve(request)


def test_replay_survives_json_key_sorting():
    request=system([x-y,y-z],x-z,guards=[x,y])
    request['generators']=dict(zip(['Z','A'],request['generators'].values()))
    result=real.solve(request)
    sorted_request=json.loads(json.dumps(request,sort_keys=True))
    assert result['verified']
    assert real.replay(sorted_request,result['certificate'])['verified']
    assert result==real.solve(sorted_request)
