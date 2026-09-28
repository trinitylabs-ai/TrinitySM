import json

import pytest

from . import division_audit_repair as recovery
from .test_rational_division import FORMALIZATION


def audit(accept):
    checks="\n".join(f"- {label}: {'PASS' if accept else 'FAIL'}"
                     for label in recovery.formal.POST_SINGULAR_CHECKS)
    return f"# Decision\n\n{'ACCEPT' if accept else 'REJECT'}\n\n# Checks\n\n{checks}\n\n# Issues\n\n"+(
        "NONE" if accept else "- The claimed correspondence is not justified.")


def write_inputs(output):
    inputs={name:name for name in ("theorem.md","source_proof.md","detection.md","matcher.md")}
    for name,text in inputs.items():
        recovery.pipeline.base.write_text(output/"input"/name,text)
    return inputs


@pytest.mark.parametrize("accept",[True,False])
@pytest.mark.parametrize("final_accept",[True,False])
@pytest.mark.parametrize("decision",["CALL_TOOL","NO_TOOL","INVALID"])
def test_final_semantic_gate_controls_tool(tmp_path,monkeypatch,accept,final_accept,decision):
    stages=[]
    invocations=[]
    source="# Decision\nCALL_TOOL\n"+FORMALIZATION.replace("```guard-args\n", "",1).replace(
        "\n```\n\n# Tool Arguments", "\n\n# Tool Arguments",1)
    review=audit(accept)
    final_review=audit(final_accept)
    repair={"CALL_TOOL":"# Decision\nCALL_TOOL\n"+FORMALIZATION,
            "NO_TOOL":"# Decision\nNO_TOOL\n# Reason\nNo justified encoding.",
            "INVALID":"broken draft"}[decision]
    monkeypatch.setattr(recovery.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)

    def caller(**kwargs):
        stages.append(kwargs["stage"])
        if len(stages)==1:
            assert source in kwargs["user_prompt"]
            assert "operator mathematical diagnosis is supplied" in kwargs["system_prompt"]
            text=review
        elif len(stages)==2:
            assert review in kwargs["user_prompt"]
            assert source in kwargs["user_prompt"]
            assert "expected one guard-args fence" in kwargs["user_prompt"]
            text=repair
        else:
            assert kwargs["stage"]==recovery.FINAL_AUDIT_STAGE
            assert repair in kwargs["user_prompt"]
            assert review not in kwargs["user_prompt"]
            assert "Deterministic Parser Feedback" not in kwargs["user_prompt"]
            text=final_review
        return text,kwargs["parser"](text),{}

    def tool(parsed,output):
        invocations.append(parsed)
        return {"verdict":"VERIFIED_SUPPORT","exact_verified":True}

    status={"semantic_certified":False,"promoted":False,"repaired_semantics":"NOT_REAUDITED"}
    inputs=write_inputs(tmp_path)
    result=recovery.execute_stages(tmp_path,status,source,"Original contract",
        recovery.audit_prompt(inputs,source),
        1,caller=caller,tool=tool)
    assert stages==[recovery.AUDIT_STAGE,recovery.REPAIR_STAGE]+(
        [recovery.FINAL_AUDIT_STAGE] if decision=="CALL_TOOL" else [])
    assert result["semantic_audit"]==("ACCEPT" if accept else "REJECT")
    assert result["semantic_certified"]==(decision=="CALL_TOOL" and final_accept)
    assert not result["promoted"]
    assert len(invocations)==(decision=="CALL_TOOL" and final_accept)
    assert result["tool_invocations"]==len(invocations)
    assert result["state"]==("failed_closed" if decision=="INVALID" else "completed")
    assert (tmp_path/"01_semantic_audit/audit.md").read_text().strip()==review
    if decision=="CALL_TOOL":
        assert result["tool_gate"]==("PASS" if final_accept else "REJECT")
        final_record=json.loads((tmp_path/"03_final_semantic_audit/result.json").read_text())
        assert final_record["formalization_sha256"]==recovery.pipeline.base.sha256_text(repair)
        assert not final_record["exact_result_supplied"]


@pytest.mark.parametrize("final_response",[audit(True),audit(False),"malformed audit"])
def test_saved_repair_needs_only_one_audit(tmp_path,monkeypatch,final_response):
    write_inputs(tmp_path)
    draft="# Decision\nCALL_TOOL\n"+FORMALIZATION
    stages=[]
    invocations=[]
    monkeypatch.setattr(recovery.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    # A previous exact result is deliberately present but must not reach Qwen.
    recovery.rewrite.write_record(tmp_path/"03_tool/result.json",{"secret":"PRIOR_TOOL_OUTCOME_SENTINEL"})
    def caller(**kwargs):
        stages.append(kwargs["stage"])
        assert draft in kwargs["user_prompt"]
        assert "PRIOR_TOOL_OUTCOME_SENTINEL" not in kwargs["user_prompt"]
        return final_response,kwargs["parser"](final_response),{}
    def tool(parsed,output):
        invocations.append(parsed)
        return {"verdict":"INCONCLUSIVE","exact_verified":False}
    result=recovery.execute_saved_repair(tmp_path,{},draft,1,caller=caller,tool=tool)
    assert stages==[recovery.FINAL_AUDIT_STAGE]
    assert len(invocations)==(final_response==audit(True))
    assert result["tool_invocations"]==len(invocations)
    assert result["state"]==("failed_closed" if final_response=="malformed audit" else "completed")


def test_saved_invalid_repair_never_calls_models_or_tool(tmp_path):
    def forbidden(**kwargs):
        raise AssertionError("must not run")
    result=recovery.execute_saved_repair(tmp_path,{},"invalid formalization",1,
                                         caller=forbidden,tool=forbidden)
    assert result["state"]=="failed_closed" and result["tool_invocations"]==0
    assert "ValueError" in result["error"]


def test_repair_hash_drift_is_rejected(tmp_path,monkeypatch):
    draft="# Decision\nCALL_TOOL\n"+FORMALIZATION
    recovery.pipeline.base.write_text(tmp_path/"02_repair/model_output.md",draft)
    recovery.rewrite.write_record(tmp_path/"02_repair/call.json",{"expected_text":draft})
    def validate(call,**kwargs):
        assert kwargs["expected_stage"]==recovery.REPAIR_STAGE
        if call["expected_text"]!=kwargs["canonical_markdown"]:
            raise ValueError("canonical repair hash mismatch")
    monkeypatch.setattr(recovery.certificate,"validate_markdown_budget_forcing",validate)
    assert recovery.saved_repair(tmp_path)[0]==draft
    recovery.pipeline.base.write_text(tmp_path/"02_repair/model_output.md",draft.replace("x", "y"))
    with pytest.raises(ValueError,match="canonical repair hash"):
        recovery.saved_repair(tmp_path)


def test_failed_audit_does_not_trigger_repair_or_tool(tmp_path):
    stages=[]
    def caller(**kwargs):
        stages.append(kwargs["stage"])
        raise ValueError("invalid audit output")
    def forbidden(*args):
        raise AssertionError("tool must not run")
    result=recovery.execute_stages(tmp_path,{},"draft","contract","audit prompt",1,
        caller=caller,tool=forbidden)
    assert stages==[recovery.AUDIT_STAGE]
    assert result["state"]=="failed_closed"
    assert result["tool_invocations"]==0


def test_latest_draft_is_order_selected_and_hash_checked(tmp_path,monkeypatch):
    for attempt in (1,2):
        root=tmp_path/f"01_formalization/model/attempt_{attempt:02}_cap_49152"
        root.mkdir(parents=True)
        stem=root/recovery.division.STAGE
        stem.with_suffix(".raw_response.json").write_text(json.dumps({
            "choices":[{"message":{"content":f"draft {attempt}"}}]}))
        stem.with_suffix(".metadata.json").write_text(json.dumps({
            "config":{"max_tokens":49152,"timeout_seconds":600}}))
    checked=[]
    def validate(call,**kwargs):
        checked.append(kwargs["canonical_markdown"])
    monkeypatch.setattr(recovery.certificate,"validate_markdown_budget_forcing",validate)
    text,binding=recovery.latest_draft(tmp_path)
    assert text=="draft 2" and binding["attempt"]==2 and checked==["draft 2"]
    def reject(*args,**kwargs):
        raise ValueError("canonical hash mismatch")
    monkeypatch.setattr(recovery.certificate,"validate_markdown_budget_forcing",reject)
    with pytest.raises(ValueError,match="canonical hash"):
        recovery.latest_draft(tmp_path)


def test_tool_worker_runs_on_generic_fixture(tmp_path):
    parsed=recovery.division.parse_proposal("# Decision\nCALL_TOOL\n"+FORMALIZATION)
    result=recovery.division.invoke_tool(parsed,tmp_path/"tool")
    assert result["verdict"]=="VERIFIED_SUPPORT"
    assert result["exact_verified"]
