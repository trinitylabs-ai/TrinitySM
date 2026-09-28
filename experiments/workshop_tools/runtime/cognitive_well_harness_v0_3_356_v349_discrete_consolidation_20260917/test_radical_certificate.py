import copy
import json

import pytest
import sympy as sp

from . import radical_certificate as radical

x,y=sp.symbols("x y")


@pytest.mark.parametrize("equations,target,guards",[
    ([("equation",x*x)],x,{}),
    ([("equation",x*y)],x,{"nonzero_y":y}),
])
def test_real_radical_witness_replay_and_markdown(tmp_path,equations,target,guards):
    if not radical.backends.DEFAULT_BINARY.is_file():
        pytest.skip("Singular unavailable")
    system=radical.system_payload([x,y],equations,target,guards)
    result=radical.export(system,tmp_path/"certificate",timeout=5,memory=1024)
    assert result["verified"],result
    certificate=json.loads((tmp_path/"certificate/certificate.json").read_text())
    assert radical.replay(system,certificate)["verified"]
    markdown,verified=radical.render(system,certificate)
    assert verified["verified"] and "contradiction" in markdown and "Exact expansion" in markdown
    changed=copy.deepcopy(certificate)
    changed["multipliers"]=[radical.laurent._payload(sp.Integer(0),radical.augmented(system)[0]) for _ in changed["multipliers"]]
    with pytest.raises(ValueError,match="re-expansion"):
        radical.replay(system,changed)
    changed_system=radical.system_payload([x,y],equations,x+y,guards)
    with pytest.raises(ValueError,match="binding"):
        radical.replay(changed_system,certificate)


def test_nonguarded_false_consequence_not_certified(tmp_path):
    if not radical.backends.DEFAULT_BINARY.is_file():
        pytest.skip("Singular unavailable")
    system=radical.system_payload([x,y],[("equation",x*y)],x,{})
    result=radical.export(system,tmp_path/"certificate",timeout=5,memory=1024)
    assert result["verified"] is False and result["state"]=="certificate_not_proved"


def test_inverse_names_do_not_collide():
    a,b=sp.symbols("guard_inverse target_inverse")
    system=radical.system_payload([a,b],[("g",a*a)],a,{})
    symbols,_=radical.augmented(system)
    assert len(set(symbols))==4 and symbols[:2]==[a,b]


def test_zero_guard_rejected():
    system=radical.system_payload([x,y],[("g",x*x)],x,{"bad":sp.Integer(0)})
    with pytest.raises(ValueError,match="zero"):
        radical.augmented(system)
