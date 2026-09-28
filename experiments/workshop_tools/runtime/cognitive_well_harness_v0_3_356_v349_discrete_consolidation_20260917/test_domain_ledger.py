import copy
import json

import pytest

from . import domain_ledger as ledger
from . import division_experiment as division
from . import division_fresh_audited as fresh
from . import division_audit_repair as recovery
from . import division_batch as batch
from .test_rational_division import FORMALIZATION, request, x, y
from .test_division_audit_repair import audit
from . import rational_division as tool


INPUTS = {"theorem.md": "Let x be a positive real number. Let y be nonzero.",
          "source_proof.md": "The proof divides by x. The branch is specified.",
          "detection.md": "Check the consequence.", "matcher.md": "polynomial_ideal_membership"}
FACT = "- pos :: POSITIVE :: (symbol x) :: theorem :: x be a positive real number :: x is the stated positive real quantity."


def draft(facts=FACT):
    return "# Decision\n\nCALL_TOOL\n\n"+FORMALIZATION.replace(
        "# Guard Program", "# Domain Ledger\n\n"+facts+"\n\n# Guard Program")


def parse(text):
    return division.parse_proposal(text,domain_inputs=INPUTS,require_domain_ledger=True)


def test_source_bound_compile_preserves_math_and_is_repeatable():
    old=division.parse_proposal("# Decision\nCALL_TOOL\n"+FORMALIZATION)
    new=parse(draft())
    assert new["arguments"] == old["arguments"]
    assert new["domain_compilation"]["authored_guard_program"] == old["guard_program"]
    assert new["domain_compilation"]["compiled_nonzero_facts"] == 1
    assert new["guard_program"]["source_nonzero"]["DL1"] == {"symbol":"x"}
    assert new == parse(draft())
    again=parse("# Decision\nCALL_TOOL\n"+new["normalized_markdown"])
    assert again["guard_program"] == new["guard_program"]
    assert again["canonical_formalization_sha256"] == new["canonical_formalization_sha256"]


@pytest.mark.parametrize("kind",["POSITIVE","NEGATIVE","NONZERO"])
def test_supported_implications_only(kind):
    parsed=parse(draft(FACT.replace("POSITIVE",kind)))
    assert parsed["domain_compilation"]["compiled_nonzero_facts"]==1
    # Text matching deliberately does NOT pretend to prove this semantic claim.
    assert parsed["domain_compilation"]["semantic_grounding"]=="MODEL_AUDIT_REQUIRED"


@pytest.mark.parametrize("kind",["NONNEGATIVE","NONPOSITIVE"])
def test_weak_inequality_never_becomes_nonzero(kind):
    with pytest.raises(ValueError,match="does not justify"):
        parse(draft(FACT.replace("POSITIVE",kind)))
    without_guards=draft(FACT.replace("POSITIVE",kind)).replace(
        "```guard-args\nprovenance_division = q1 :: (symbol x) :: (symbol x)\nsource_nonzero = nz1 :: (symbol x)\n```", "NONE")
    parsed=parse(without_guards)
    assert not parsed["guard_program"]["source_nonzero"]
    assert parsed["domain_compilation"]["retained_only_facts"]==1


def test_branch_retained_and_visible_to_audit():
    text=draft(FACT+"\n- branch :: RETAINED :: NONE :: proof :: The branch is specified. :: Branch must be checked independently.")
    parsed=parse(text)
    assert parsed["domain_compilation"]["compiled_nonzero_facts"]==1
    assert parsed["domain_compilation"]["retained_only_facts"]==1
    prompt=recovery.audit_prompt(INPUTS,text,domain_ledger_enabled=True)
    assert text in prompt and "branch: RETAINED -> retained_only" in prompt
    assert "NOT machine-certified" in prompt


@pytest.mark.parametrize("mutation,match",[
    (lambda s:s.replace("x be a positive real number", "unseen source statement"),"excerpt not found"),
    (lambda s:s.replace(":: theorem ::", ":: audit ::"),"unsupported"),
    (lambda s:s.replace("(symbol x)", "(symbol undeclared)",1),"undeclared"),
    (lambda s:s.replace("POSITIVE", "UNCONSTRAINED"),"unsupported"),
    (lambda s:s.replace("(symbol x)", "0",1),"false constant"),
    (lambda s:s.replace("POSITIVE", "RETAINED"),"requires expression NONE"),
    (lambda s:s+"\n"+s,"unique"),
])
def test_unsafe_or_unbound_facts_rejected(mutation,match):
    with pytest.raises(ValueError,match=match):
        parse(draft(mutation(FACT)))


def test_missing_domain_is_parser_feedback_even_if_semantically_accepted():
    result=fresh.inspect_draft("# Decision\nCALL_TOOL\n"+FORMALIZATION,
        domain_inputs=INPUTS,require_domain_ledger=True)
    assert not result["parser_valid"] and "requires Domain Ledger" in result["parser_feedback"]
    with pytest.raises(ValueError,match="bound original"):
        division.parse_proposal(draft())
    assert not parse("# Decision\nNO_TOOL\n# Reason\nCannot justify this domain.")["call_requested"]


def test_nonzero_product_covers_factors_but_not_extra_symbols():
    req=request([x*y],x)
    authored={"provenance_divisions":{"divide":{"numerator":1,"denominator":{"symbol":"x"}}},"source_nonzero":{}}
    facts="- product :: NONZERO :: (mul (symbol x) (symbol y)) :: theorem :: Let y be nonzero. :: Product is nonzero by the stated hypotheses."
    program,report=ledger.compile_ledger(facts,req["arguments"],authored,INPUTS)
    assert report["compiled_nonzero_facts"]==1
    authored["source_nonzero"]["unjustified"]={"symbol":"z"}
    with pytest.raises(ValueError,match="does not justify"):
        ledger.compile_ledger(facts,req["arguments"],authored,INPUTS)


def test_compiled_guard_changes_toy_tool_result_soundly():
    req=request([x*y],x)
    assert tool.solve(req)["verdict"]=="INCONCLUSIVE"
    fact="- nz :: NONZERO :: (symbol y) :: theorem :: Let y be nonzero. :: y is stated nonzero."
    req["guard_program"],_=ledger.compile_ledger(fact,req["arguments"],req["guard_program"],INPUTS)
    result=tool.solve(req)
    assert result["verdict"]=="VERIFIED_SUPPORT" and result["certificate_verified"]


@pytest.mark.parametrize("accepted",[True,False])
def test_full_gemma_gate_uses_compilation_without_extra_calls(tmp_path,monkeypatch,accepted):
    for name,text in INPUTS.items():
        fresh.pipeline.base.write_text(tmp_path/"input"/name,text)
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    calls=[]
    tools=[]
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        assert kwargs["role"].model==fresh.pipeline.base.DEFAULT_GEMMA_MODEL
        if kwargs["stage"]==recovery.AUDIT_STAGE:
            assert "Domain Coverage Audit" in kwargs["user_prompt"]
            assert "positive_implies_nonzero" in kwargs["user_prompt"]
            text=audit(accepted)
        else:
            text=draft()
        return text,kwargs["parser"](text),{}
    def invoke(parsed,destination):
        tools.append(parsed)
        assert parsed["domain_compilation"]["source_bound"]
        assert "DL1" in parsed["guard_program"]["source_nonzero"]
        return {"verdict":"VERIFIED_SUPPORT","exact_verified":True}
    result=fresh.execute(tmp_path,{"domain_ledger_enabled":True},"contract",1,
        cycles=1,caller=caller,tool=invoke)
    assert result["state"]=="completed",result
    assert len(calls)==2 and len(tools)==int(accepted)
    assert result["cycles"][0]["compiled_nonzero_facts"]==1


def test_batch_flag_and_no_stale_summary(tmp_path):
    trial={"label":"sample_01","output":str(tmp_path),"seed":123,
           "verdict":"VERIFIED_SUPPORT","exact_verified":True}
    assert "--domain-ledger" in batch.child_command(tmp_path,trial,"gemma",domain_ledger=True)
    assert "--domain-ledger" not in batch.child_command(tmp_path,trial,"gemma")
    row=batch.summarize(trial,None)
    assert "verdict" not in row and "exact_verified" not in row


def test_tampered_compilation_cannot_reach_worker(tmp_path):
    parsed=copy.deepcopy(parse(draft()))
    parsed["guard_program"]["source_nonzero"]["extra"]={"symbol":"x"}
    with pytest.raises(ValueError,match="binding mismatch"):
        division.invoke_tool(parsed,tmp_path/"tool")
    assert not (tmp_path/"tool/request.json").exists()


@pytest.mark.parametrize("value",[-0.1,1.1,float("nan"),float("inf")])
def test_temperature_validation(value):
    with pytest.raises(ValueError,match="temperature"):
        division.validate_temperature(value)


def test_formalizer_temperature_does_not_change_auditor(tmp_path,monkeypatch):
    for name,text in INPUTS.items():
        fresh.pipeline.base.write_text(tmp_path/"input"/name,text)
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    temps=[]
    def caller(**kwargs):
        temps.append(kwargs["role"].temperature)
        text=audit(False) if kwargs["stage"]==recovery.AUDIT_STAGE else draft()
        return text,kwargs["parser"](text),{}
    result=fresh.execute(tmp_path,{"domain_ledger_enabled":True,"model":{"temperature":0.4}},
        "contract",1,cycles=2,caller=caller,tool=lambda *a:pytest.fail("audit rejected"))
    assert result["state"]=="completed",result
    assert temps==[0.4,0.1,0.4,0.1]
    trial={"label":"sample_01","output":str(tmp_path),"seed":123,"formalizer_temperature":0.4}
    command=batch.child_command(tmp_path,trial,"gemma",domain_ledger=True)
    assert command[command.index("--formalizer-temperature")+1]=="0.4"


@pytest.mark.parametrize("state,failures,allowed",[("completed",0,True),("completed",1,False),("failed_closed",0,False)])
def test_comparison_wait_has_mechanical_failure_gate(tmp_path,state,failures,allowed):
    previous=tmp_path/"previous"
    fresh.rewrite.write_record(previous/"manifest.json",{})
    fresh.rewrite.write_record(previous/"status.json",{"state":state,"failed_workers":failures})
    if allowed:
        batch.wait_for_batch(previous,tmp_path/"comparison")
    else:
        with pytest.raises(RuntimeError,match="mechanical"):
            batch.wait_for_batch(previous,tmp_path/"comparison")
    assert not (tmp_path/"comparison").exists()
    queue=json.loads((tmp_path/"comparison.queue.json").read_text())
    assert queue["state"] == ("ready" if allowed else "blocked")
    assert not queue["prior_model_artifacts_supplied"]


def test_bare_declared_leaves_normalize_without_changing_expression():
    typed=parse(draft())
    bare=parse(draft(FACT.replace("(symbol x)","x")))
    assert bare["guard_program"]==typed["guard_program"]
    assert bare["domain_compilation"]["surface_normalization"]["declared_symbol_leaves"]==1
    parenthesized=parse(draft(FACT.replace("(symbol x)","(x)")))
    assert parenthesized["guard_program"]==typed["guard_program"]
    assert parenthesized["domain_compilation"]["surface_normalization"]["parenthesized_declared_symbols"]==1


def test_parenthesized_symbols_across_fields_preserve_canonical_math_and_guards():
    typed=parse(draft())
    text=draft().replace("(symbol x)","(x)")
    parsed=parse(text)
    assert parsed["arguments"]==typed["arguments"]
    assert parsed["guard_program"]==typed["guard_program"]
    # The ledger's original surface text remains part of the saved formalization;
    # equal mathematics does not imply identical source-document hashes.
    assert parsed["canonical_formalization_sha256"]==parse(text)["canonical_formalization_sha256"]
    assert ":: (x) ::" in parsed["normalized_markdown"]
    assert parsed["domain_compilation"]["surface_normalization"]["parenthesized_declared_symbols"]==1
    assert parsed["surface_normalization"]["guard_program"]["parenthesized_declared_symbols"]==3
    assert parsed["deterministic_normalization"]["replacements"]["parenthesized_declared_symbols"]==2
    assert parsed["domain_compilation"]["semantic_grounding"]=="MODEL_AUDIT_REQUIRED"
    assert text==draft().replace("(symbol x)","(x)")  # original model output stays intact


@pytest.mark.parametrize("accepted",[True,False])
def test_parenthesized_symbols_still_require_semantic_acceptance_before_tools(tmp_path,monkeypatch,accepted):
    for name,text in INPUTS.items():
        fresh.pipeline.base.write_text(tmp_path/"input"/name,text)
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    calls=[]
    tools=[]
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        text=audit(accepted) if kwargs["stage"]==recovery.AUDIT_STAGE else draft().replace("(symbol x)","(x)")
        return text,kwargs["parser"](text),{}
    result=fresh.execute(tmp_path,{"domain_ledger_enabled":True},"generic contract",1,
        cycles=1,caller=caller,tool=lambda *args: tools.append(args) or {"verdict":"VERIFIED_SUPPORT","exact_verified":True})
    assert result["state"]=="completed",result
    assert len(calls)==2 and len(tools)==int(accepted)
    assert result["audit_calls_skipped"]==0


def test_source_feedback_reports_all_copy_mismatches_without_filling_facts():
    facts=FACT.replace("x be a positive real number","first invented excerpt")+"\n"+FACT.replace(
        "- pos ::","- second ::").replace("x be a positive real number","second invented excerpt")
    with pytest.raises(ValueError) as error:
        parse(draft(facts))
    assert "pos: source excerpt not found" in str(error.value)
    assert "second: source excerpt not found" in str(error.value)
