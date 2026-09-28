import copy
import hashlib
import json

import pytest
import sympy as sp

from . import backend_comparison as comparison
from .test_rational_division import request, x, y


def test_guard_encoding_preserves_original_polynomials():
    req=request([x*y],x,(y,))
    before=copy.deepcopy(req)
    symbols,generators,target=comparison.guarded_membership_inputs(req)
    assert req==before
    assert generators[0][1]==x*y and target==x
    assert generators[-1][1]==1-symbols[-1]*y


@pytest.mark.parametrize("guarded,expected",[(False,"NONZERO"),(True,"PROVED")])
def test_real_singular_guarded_membership(guarded,expected):
    if not comparison.DEFAULT_BINARY.is_file():
        pytest.skip("local Singular unavailable")
    symbols,generators,target=comparison.guarded_membership_inputs(request([x*y],x,(y,) if guarded else ()))
    result=comparison.gaussian_backend.check(symbols=symbols,generators=generators,target=target,
        guards={},binary=comparison.DEFAULT_BINARY,timeout_sec=5,memory_mb=1024,radical=False)
    assert result["status"]=="COMPLETED",result
    assert result["markers"]["RESULT_ORDINARY"]==expected,result
    if guarded:
        assert result["certificate_reexpanded"]


def test_real_radical_screen_is_not_promoted(tmp_path):
    if not comparison.DEFAULT_BINARY.is_file():
        pytest.skip("local Singular unavailable")
    req=request([x*y],x,(y,))
    path=tmp_path/"input.json"
    comparison.write(path,req)
    row={"case":"toy","route":"guarded_radical","request_path":str(path),
         "request_sha256":comparison.division.exact_tools.stable_hash(req),"output":str(tmp_path/"screen")}
    result=comparison.task(row,comparison.DEFAULT_BINARY,5,1024)
    assert result["state"]=="completed",result
    assert result["markers"]["RESULT_RADICAL"]=="PROVED",result
    assert result["promotable"] is False and result["model_calls"]==0


def test_request_drift_rejected_before_backend(tmp_path):
    req=request([x*y],x)
    path=tmp_path/"input.json"
    comparison.write(path,req)
    with pytest.raises(ValueError,match="request changed"):
        comparison.task({"request_path":str(path),"request_sha256":"wrong","output":str(tmp_path/"out")},
            comparison.DEFAULT_BINARY,5,1024)


def saved_preview(root,req):
    def poly(expr):
        return {"terms":[{"powers":list(powers),"coefficient":{
            "real_numerator":int(value.p),"real_denominator":int(value.q),
            "imaginary_numerator":0,"imaginary_denominator":1}}
            for powers,value in sp.Poly(expr,x,y).terms()]}
    transform={"symbols":["x","y"],"generators":{"g":poly(x*y)},
        "target":poly(x),"guards":{"guard_y":poly(y)}}
    transform["transform_sha256"]=comparison.division.exact_tools.stable_hash(transform)
    comparison.write(root/"laurent_transform.json",transform)
    comparison.write(root/"typed_guard_binding.json",{"test_fixture":True})
    preview={"state":"structural_preview_unvalidated","promotable":False,
        "source_arguments_sha256":comparison.division.exact_tools.stable_hash(req["arguments"]),
        "candidate_arguments_sha256":comparison.division.exact_tools.stable_hash(req["arguments"]),
        "guard_program_sha256":comparison.division.exact_tools.stable_hash(req["guard_program"]),
        "transform_sha256":transform["transform_sha256"],"derived_profile":{"solver_symbol_count":2,"solver_generator_count":1},
        "artifact_sha256":{name:hashlib.sha256((root/name).read_bytes()).hexdigest()
            for name in ("laurent_transform.json","typed_guard_binding.json")}}
    comparison.write(root/"preview.json",preview)


def test_saved_laurent_radical_reuses_preview_and_all_guards(tmp_path,monkeypatch):
    if not comparison.DEFAULT_BINARY.is_file():
        pytest.skip("local Singular unavailable")
    req=request([x*y],x,(y,))
    source=tmp_path/"input.json"
    comparison.write(source,req)
    preview=tmp_path/"preview"
    saved_preview(preview,req)
    def forbidden(**kwargs):
        raise AssertionError("a bound saved preview must not be recomputed")
    monkeypatch.setattr(comparison.integration,"bounded_preview_only",forbidden)
    result=comparison.task({"case":"toy","route":"laurent_guarded_radical",
        "request_path":str(source),"request_sha256":comparison.division.exact_tools.stable_hash(req),
        "preview_path":str(preview),"output":str(tmp_path/"result")},comparison.DEFAULT_BINARY,5,1024)
    assert result["state"]=="completed",result
    assert result["markers"]["RESULT_RADICAL"]=="PROVED",result
    assert result["preview_reused"] and result["transformed_guard_count"]==1
    assert result["model_calls"]==0 and result["promotable"] is False
    assert result["certificate_reexpanded"] is False and result["source_consistency_checked"] is False
    unguarded=comparison.guarded_radical_check([x,y],[("g",x*y)],x,{},comparison.DEFAULT_BINARY,5,1024)
    assert unguarded["markers"]["RESULT_RADICAL"]=="NOT_PROVED"


@pytest.mark.parametrize("changed",["request","artifact","transform"])
def test_saved_preview_rejects_drift(tmp_path,changed):
    req=request([x*y],x,(y,))
    root=tmp_path/"preview"
    saved_preview(root,req)
    if changed=="request":
        req=request([x*y],y,(y,))
    elif changed=="artifact":
        comparison.write(root/"typed_guard_binding.json",{"changed":True})
    else:
        payload=json.loads((root/"laurent_transform.json").read_text())
        payload["symbols"][0]="changed"
        comparison.write(root/"laurent_transform.json",payload)
        preview=json.loads((root/"preview.json").read_text())
        preview["artifact_sha256"]["laurent_transform.json"]=hashlib.sha256((root/"laurent_transform.json").read_bytes()).hexdigest()
        comparison.write(root/"preview.json",preview)
    with pytest.raises(ValueError,match="binding changed"):
        comparison.bound_preview(root,req)


@pytest.mark.parametrize("parser,accepted",[("FAIL",True),("PASS",False)])
def test_comparison_rejects_unaccepted_inputs(tmp_path,parser,accepted):
    cycle=tmp_path/"sample/cycles/cycle"
    path=cycle/"03_execution/04_tool/request.json"
    final=cycle/"03_execution/03_final_semantic_audit"
    comparison.write(final/"parser.json",{"decision":parser})
    comparison.write(final/"result.json",{"accepted":accepted,"decision":"ACCEPT" if accepted else "REJECT"})
    with pytest.raises(ValueError,match="lacks parser and semantic acceptance"):
        comparison.accepted_request(path)
