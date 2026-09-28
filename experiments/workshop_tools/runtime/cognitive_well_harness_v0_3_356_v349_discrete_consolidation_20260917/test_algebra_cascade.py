import pytest

from . import algebra_cascade as cascade
from .test_rational_division import request,x,y


@pytest.mark.parametrize("winner,expected",[
    ("division",["laurent","laurent_guarded_radical","guarded_radical","division","verify:division","rewrite"]),
    ("guarded_radical",["laurent","laurent_guarded_radical","guarded_radical","verify:guarded_radical","rewrite"]),
    ("laurent_guarded_radical",["laurent","laurent_guarded_radical","verify:laurent_guarded_radical","rewrite"]),
    (None,["laurent","laurent_guarded_radical","guarded_radical","division"]),
])
def test_order_and_immediate_verified_handoff(tmp_path,winner,expected):
    req=request([x*y],x,(y,))
    digest=cascade.backends.division.exact_tools.stable_hash(req)
    calls=[]
    def step(name):
        def run(current,path,*unused):
            assert current==req
            calls.append(name)
            return {"outcome":"PROVED" if name==winner else "TIMEOUT"}
        return run
    def radical(current,path,preview):
        return step("guarded_radical" if preview is None else "laurent_guarded_radical")(current,path)
    def laurent(current,path):
        calls.append("laurent")
        return {"outcome":"REDUCED","request_sha256":digest}
    def verify(current,stage,result,preview,path):
        calls.append("verify:"+stage)
        return {"verified":True,"request_sha256":digest,"scope":"original_target","laurent_lift_verified":preview is not None}
    def rewrite(current,verified,path):
        calls.append("rewrite")
        assert verified["verified"]
        return {"proof":"model-authored output fixture"}
    result=cascade.execute(req,tmp_path/"run",admission={"parser":"PASS","semantic":"ACCEPT","request_sha256":digest},
        operations=cascade.Operations(step("division"),radical,laurent,verify,rewrite))
    assert calls==expected
    assert result["state"]=="completed",result
    assert result["exact_verified"]==(winner is not None)


@pytest.mark.parametrize("parser,semantic",[("FAIL","ACCEPT"),("PASS","REJECT")])
def test_gate_rejection_precedes_every_tool(tmp_path,parser,semantic):
    req=request([x*y],x)
    never=lambda *a:pytest.fail("no backend should be called")
    with pytest.raises(ValueError,match="requires parser and semantic"):
        cascade.execute(req,tmp_path/"run",admission={"parser":parser,"semantic":semantic,
            "request_sha256":cascade.backends.division.exact_tools.stable_hash(req)},
            operations=cascade.Operations(never,never,never,never,never))


def test_unavailable_laurent_and_bare_positive_never_rewrite(tmp_path):
    req=request([x*y],x)
    digest=cascade.backends.division.exact_tools.stable_hash(req)
    calls=[]
    def radical(*args):
        calls.append("radical")
        return {"outcome":"PROVED"}
    operations=cascade.Operations(lambda *a:{"outcome":"TIMEOUT"},radical,
        lambda *a:{"outcome":"UNAVAILABLE"},lambda *a:{"verified":False,"state":"certificate_timeout"},
        lambda *a:pytest.fail("a screen alone cannot start rewriting"))
    result=cascade.execute(req,tmp_path/"run",admission={"parser":"PASS","semantic":"ACCEPT","request_sha256":digest},operations=operations)
    assert calls==["radical"] and result["state"]=="completed"
    assert result["verdict"]=="CERTIFICATION_REQUIRED" and result["proof_rewrite_started"] is False


def test_mismatched_verified_certificate_fails_closed(tmp_path):
    req=request([x*y],x)
    digest=cascade.backends.division.exact_tools.stable_hash(req)
    never=lambda *a:pytest.fail("must stop before later stages")
    result=cascade.execute(req,tmp_path/"run",admission={"parser":"PASS","semantic":"ACCEPT","request_sha256":digest},
        operations=cascade.Operations(lambda *a:{"outcome":"PROVED"},lambda *a:{"outcome":"TIMEOUT"},
            lambda *a:{"outcome":"UNAVAILABLE"},
            lambda *a:{"verified":True,"request_sha256":"changed","scope":"original_target"},never))
    assert result["state"]=="failed_closed" and not result["proof_rewrite_started"]


def test_laurent_positive_requires_source_lift_before_rewrite(tmp_path):
    req=request([x*y],x)
    digest=cascade.backends.division.exact_tools.stable_hash(req)
    never=lambda *a:pytest.fail("invalid Laurent evidence must stop before fallback or rewriting")
    result=cascade.execute(req,tmp_path/"run",
        admission={"parser":"PASS","semantic":"ACCEPT","request_sha256":digest},
        operations=cascade.Operations(never,lambda *a:{"outcome":"PROVED"},
            lambda *a:{"outcome":"REDUCED","request_sha256":digest},
            lambda *a:{"verified":True,"request_sha256":digest,"scope":"original_target",
                       "laurent_lift_verified":False},never))
    assert result["state"]=="failed_closed" and not result["proof_rewrite_started"]
