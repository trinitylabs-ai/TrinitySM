import pytest

from . import division_fresh_audited as fresh
from . import division_audit_repair as recovery
from . import division_batch as batch
from .test_division_audit_repair import audit, write_inputs
from .test_rational_division import FORMALIZATION


@pytest.mark.parametrize("initial_valid,first_accept,final_accept,expected_calls,expected_tools",[
    (True,True,False,2,1),
    (True,False,True,4,1),
    (True,False,False,4,0),
    (False,True,True,3,1),
    (False,False,False,3,0),
])
def test_gemma_only_fresh_workflow(tmp_path,monkeypatch,initial_valid,first_accept,final_accept,
                                  expected_calls,expected_tools):
    write_inputs(tmp_path)
    valid="# Decision\nCALL_TOOL\n"+FORMALIZATION
    invalid=valid.replace("```guard-args\n", "",1).replace(
        "\n```\n\n# Tool Arguments", "\n\n# Tool Arguments",1)
    draft=valid if initial_valid else invalid
    stages=[]
    tool_calls=[]
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        stage=kwargs["stage"]
        stages.append(stage)
        assert kwargs["role"].model==fresh.pipeline.base.DEFAULT_GEMMA_MODEL
        assert kwargs["role"].endpoint=="http://127.0.0.1:8030/v1"
        if stage==fresh.division.STAGE:
            assert kwargs["user_prompt"]=="Fresh original contract"
            response=draft
        elif stage==recovery.AUDIT_STAGE:
            current=draft if recovery.REPAIR_STAGE not in stages else valid
            assert current in kwargs["user_prompt"]
            assert "Independent Semantic Audit of That Draft" not in kwargs["user_prompt"]
            assert audit(first_accept) not in kwargs["user_prompt"]
            response=audit(first_accept if recovery.REPAIR_STAGE not in stages else final_accept)
        elif stage==recovery.REPAIR_STAGE:
            if initial_valid:
                assert audit(first_accept) in kwargs["user_prompt"]
            else:
                assert "No semantic audit was run" in kwargs["user_prompt"]
                assert audit(first_accept) not in kwargs["user_prompt"]
            assert "Deterministic Parser Feedback" in kwargs["user_prompt"]
            response=valid
        else:
            raise AssertionError("Unexpected extra model stage")
        return response,kwargs["parser"](response),{}
    def tool(parsed,output):
        tool_calls.append(parsed)
        return {"verdict":"VERIFIED_SUPPORT","exact_verified":True}
    result=fresh.execute(tmp_path,{},"Fresh original contract",1,cycles=2,caller=caller,tool=tool)
    assert result["state"]=="completed",result
    assert len(stages)==expected_calls and len(tool_calls)==expected_tools
    assert result["tool_invocations"]==expected_tools
    if expected_calls==2:
        assert stages==[fresh.division.STAGE,recovery.AUDIT_STAGE]


def test_fresh_model_decline_skips_audit_and_tool(tmp_path,monkeypatch):
    write_inputs(tmp_path)
    stages=[]
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        stages.append(kwargs["stage"])
        text="# Decision\nNO_TOOL\n# Reason\nNo justified encoding."
        return text,kwargs["parser"](text),{}
    result=fresh.execute(tmp_path,{},"contract",1,caller=caller)
    assert result["stage"]=="model_declined_tool" and result["tool_invocations"]==0
    assert stages==[fresh.division.STAGE]


def test_reusing_audit_for_different_text_fails(tmp_path,monkeypatch):
    write_inputs(tmp_path)
    text="# Decision\nCALL_TOOL\n"+FORMALIZATION
    with pytest.raises(ValueError,match="different formalization"):
        recovery.audit_repaired_and_call(tmp_path,{},text,1,caller=None,tool=None,
            auditor="gemma",completed_audit=(audit(True),{},"different draft"))


def test_batch_has_eight_independent_gemma_trials(tmp_path):
    rows=batch.trials(tmp_path,1234,8)
    assert len({row["seed"] for row in rows})==8
    assert len({row["output"] for row in rows})==8
    assert batch.trials(tmp_path,1234,8)==rows
    for row in rows:
        command=batch.child_command(tmp_path/"source",row,"gemma")
        assert command[command.index("--auditor")+1]=="gemma"
        assert command[command.index("--master-seed")+1]==str(row["seed"])
        assert command[command.index("--cycles")+1]=="3"
        assert "--previous-run" not in command
    with pytest.raises(ValueError):
        batch.trials(tmp_path,1234,9)


def test_dead_worker_is_not_reported_running(tmp_path):
    trial=batch.trials(tmp_path,1,1)[0]
    recovery.rewrite.write_record(tmp_path/"sample_01/status.json",{"state":"running","stage":"audit"})
    assert batch.summarize(trial,None)["state"]=="running"
    assert batch.summarize(trial,1)["state"]=="failed_closed"


@pytest.mark.parametrize("third_accept",[True,False])
def test_exactly_three_cycles_with_only_latest_feedback(tmp_path,monkeypatch,third_accept):
    write_inputs(tmp_path)
    text="# Decision\nCALL_TOOL\n"+FORMALIZATION
    calls=[]
    tools=[]
    reviews=[audit(False).replace("not justified.","not justified. ISSUE_CYCLE_1"),
             audit(False).replace("not justified.","not justified. ISSUE_CYCLE_2"),audit(third_accept)]
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        index=(len(calls)-1)//2
        if kwargs["stage"]==recovery.AUDIT_STAGE:
            assert "ISSUE_CYCLE" not in kwargs["user_prompt"]
            answer=reviews[index]
        else:
            if index:
                assert f"ISSUE_CYCLE_{index}" in kwargs["user_prompt"]
            if index==2:
                assert "ISSUE_CYCLE_1" not in kwargs["user_prompt"]
            answer=text
        return answer,kwargs["parser"](answer),{}
    def tool(parsed,output):
        tools.append(parsed)
        return {"verdict":"INCONCLUSIVE","exact_verified":False}
    result=fresh.execute(tmp_path,{},"Original contract",1,caller=caller,tool=tool)
    assert len(calls)==6 and result["completed_cycles"]==3
    assert len(tools)==int(third_accept)
    assert result["state"]=="completed"
    assert result["stage"]==("finished" if third_accept else "cycle_limit_rejected")


@pytest.mark.parametrize("last_proved",[True,False])
def test_tool_feedback_at_every_cycle(tmp_path,monkeypatch,last_proved):
    write_inputs(tmp_path)
    text="# Decision\nCALL_TOOL\n"+FORMALIZATION
    calls=[]
    executions=[]
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        if kwargs["stage"]==recovery.AUDIT_STAGE:
            assert "Exact Tool Feedback" not in kwargs["user_prompt"]
            assert "INCONCLUSIVE" not in kwargs["user_prompt"]
            answer=audit(True)
        else:
            if len(calls)>1:
                assert "Exact Tool Feedback" in kwargs["user_prompt"]
                assert "INCONCLUSIVE" in kwargs["user_prompt"]
            answer=text
        return answer,kwargs["parser"](answer),{}
    def tool(parsed,output):
        executions.append(output)
        proved=last_proved and len(executions)==3
        return {"verdict":"VERIFIED_SUPPORT" if proved else "INCONCLUSIVE","exact_verified":proved}
    result=fresh.execute(tmp_path,{},"Original contract",1,caller=caller,tool=tool)
    assert result["state"]=="completed" and result["completed_cycles"]==3
    assert len(calls)==6 and len(set(executions))==3 and result["tool_invocations"]==3
    assert result["exact_verified"]==last_proved


def test_resume_keeps_cycle_and_tool_count(tmp_path,monkeypatch):
    write_inputs(tmp_path)
    text="# Decision\nCALL_TOOL\n"+FORMALIZATION
    calls=[]
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        if kwargs["stage"]==recovery.REPAIR_STAGE:
            assert kwargs["user_prompt"]=="Saved draft plus exact tool feedback"
        answer=audit(True) if kwargs["stage"]==recovery.AUDIT_STAGE else text
        return answer,kwargs["parser"](answer),{}
    result=fresh.execute(tmp_path,{"tool_invocations":1,"cycles":[{"cycle":1},{"cycle":2}]},
        "Original contract",1,start_cycle=3,initial_user="Saved draft plus exact tool feedback",caller=caller,
        tool=lambda *args:{"verdict":"INCONCLUSIVE","exact_verified":False})
    assert calls==[recovery.REPAIR_STAGE,recovery.AUDIT_STAGE]
    assert len(result["cycles"])==3 and result["tool_invocations"]==2


def test_only_inconclusive_with_unused_cycles_is_resumable():
    from .division_tool_feedback_resume import eligible
    row={"state":"completed","stage":"finished","verdict":"INCONCLUSIVE",
         "exact_verified":False,"cycle":2,"cycle_limit":3}
    assert eligible(row)
    assert not eligible({**row,"cycle":3})
    assert not eligible({**row,"state":"running"})
    assert not eligible({**row,"exact_verified":True})
    assert not eligible({**row,"stage":"cycle_limit_rejected"})


def test_three_parser_failures_skip_all_audits_and_tools(tmp_path,monkeypatch):
    write_inputs(tmp_path)
    calls=[]
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        assert kwargs["stage"]!=recovery.AUDIT_STAGE
        if len(calls)>1:
            assert f"INVALID_DRAFT_{len(calls)-1}" in kwargs["user_prompt"]
            assert "No semantic audit was run" in kwargs["user_prompt"]
        if len(calls)==3:
            assert "INVALID_DRAFT_1" not in kwargs["user_prompt"]
        text=f"INVALID_DRAFT_{len(calls)}"
        return text,kwargs["parser"](text),{}
    result=fresh.execute(tmp_path,{},"contract",1,caller=caller,
        tool=lambda *a:pytest.fail("invalid draft must not execute"))
    assert result["state"]=="completed" and result["completed_cycles"]==3
    assert result["audit_calls_skipped"]==3 and result["tool_invocations"]==0
    assert len(calls)==3
    assert len(list(tmp_path.glob("cycles/*/02_audit/skipped.json")))==3
    assert not list(tmp_path.glob("cycles/*/02_audit/audit.md"))


def test_parser_failure_drops_prior_semantic_feedback(tmp_path,monkeypatch):
    write_inputs(tmp_path)
    valid="# Decision\nCALL_TOOL\n"+FORMALIZATION
    review=audit(False).replace("not justified.","not justified. OLD_AUDIT_SENTINEL")
    author_calls=0
    audit_calls=0
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    def caller(**kwargs):
        nonlocal author_calls,audit_calls
        if kwargs["stage"]==recovery.AUDIT_STAGE:
            audit_calls+=1
            assert "OLD_AUDIT_SENTINEL" not in kwargs["user_prompt"]
            text=review if audit_calls==1 else audit(True)
        else:
            author_calls+=1
            if author_calls==2:
                assert "OLD_AUDIT_SENTINEL" in kwargs["user_prompt"]
            if author_calls==3:
                assert "OLD_AUDIT_SENTINEL" not in kwargs["user_prompt"]
                assert "No semantic audit was run" in kwargs["user_prompt"]
            text="invalid second draft" if author_calls==2 else valid
        return text,kwargs["parser"](text),{}
    result=fresh.execute(tmp_path,{},"contract",1,caller=caller,
        tool=lambda *a:{"verdict":"VERIFIED_SUPPORT","exact_verified":True})
    assert result["exact_verified"] and result["tool_invocations"]==1
    assert author_calls==3 and audit_calls==2 and result["audit_calls_skipped"]==1
