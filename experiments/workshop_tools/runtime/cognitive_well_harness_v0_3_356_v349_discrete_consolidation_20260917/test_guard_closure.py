import copy
import json
import sympy as sp
import pytest
from . import guard_closure as closure, geometry_program as compiler, geometry_workflow as workflow
from .test_geometry_program import program


@pytest.mark.parametrize('names',[('x','y'),('alpha','beta')])
@pytest.mark.parametrize('sign',[1,-1])
def test_sum_requires_replayed_strict_sign_and_survives_renaming(names,sign):
    x,y=sp.symbols(names)
    facts=[(sign*x*y,True,'strict_product')]
    rows=closure.derive([x,y],[x,y],facts,[])
    wanted=x+sign*y
    row=next(r for v,r in rows if sp.expand(v-wanted)==0)
    assert closure.replay(wanted,[x,y],facts,[],row['proof'])
    tampered=copy.deepcopy(row['proof']);tampered['weight']='-1'
    with pytest.raises(ValueError):closure.replay(wanted,[x,y],facts,[],tampered)
    with pytest.raises(ValueError):closure.replay(wanted,[x,y],[(sign*x*y,False,'strict_product')],[],row['proof'])


def test_individual_nonzero_or_weak_product_is_insufficient():
    x,y=sp.symbols('x y')
    assert closure.derive([x,y],[x,y],[],[(x,'first'),(y,'second')])==[]
    assert closure.derive([x,y],[x,y],[(x*y,False,'weak')],[])==[]


def test_new_guard_closes_real_certificate_without_inventing_premises(tmp_path):
    body='''symbols = a, b, z
premise positive :: (gt (mul a b) 0) :: The product is positive
premise equation :: (eq (mul (add a b) z) 0) :: the product with z vanishes
target conclusion :: (eq z 0)'''
    compiled=compiler.compile_program(program(body),'The product is positive and the product with z vanishes.')
    rows=compiled['report']['guard_derivations']
    assert any(r['origin']=='strict_same_sign_sum' and r['expression']=='a + b' for r in rows.values())
    result=workflow.certificate_search(compiled,tmp_path/'search',timeout=10,memory=2048)
    assert result['exact_verified'],result
    root=__import__('pathlib').Path(result['certificate_root'])
    assert workflow.replay_certificate(json.loads((root/'system.json').read_text()),
                                       json.loads((root/'certificate.json').read_text()))['verified']


def test_sparse_portfolio_covers_late_guards():
    x=sp.Symbol('x')
    system=workflow.radical.system_payload([x],[('relation',x)],x,
                                         {f'G{i}':x+i for i in range(9)})
    subsets=compiler.guard_subsets(system)
    assert ('G0','G8') in subsets and ('G7','G8') in subsets
    assert len(subsets)==len(set(subsets))
