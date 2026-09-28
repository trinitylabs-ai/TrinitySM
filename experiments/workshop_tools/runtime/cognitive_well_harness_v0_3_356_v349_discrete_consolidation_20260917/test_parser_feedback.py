import copy

import pytest

from . import parser_feedback as feedback
from . import division_fresh_audited as fresh
from .test_domain_ledger import draft, FACT, INPUTS, parse
from .test_division_audit_repair import audit


def test_ambiguous_symbol_call_does_not_mutate_or_admit_draft():
    text=draft(FACT.replace("(symbol x)","(x 1)"))
    before=str(text)
    result=fresh.inspect_draft(text,domain_inputs=INPUTS,require_domain_ledger=True)
    assert not result["parser_valid"]
    issue=result["parser_diagnostics"]["issues"][0]
    assert issue["field"]=="Domain Ledger / pos / expression"
    assert "(x 1)" in text.splitlines()[issue["line"]-1]
    assert "arity 1" in result["parser_feedback"]
    assert text==before
    with pytest.raises(ValueError):
        parse(text)
    assert parse(text.replace(":: (x 1) ::",":: (symbol x) ::"))["call_requested"]


def test_collects_independent_quote_expression_and_target_errors():
    facts=FACT.replace("(symbol x)","(x 1)").replace("x be a positive real number","a fabricated source phrase")
    text=draft(facts).replace("target = ","target = ) ")
    result=fresh.inspect_draft(text,domain_inputs=INPUTS,require_domain_ledger=True)
    codes={issue["code"] for issue in result["parser_diagnostics"]["issues"]}
    assert {"source_excerpt","expression_syntax","parentheses"}<=codes
    assert "No replacement source is selected" in result["parser_feedback"]
    assert not result["parser_valid"]


def test_declared_symbols_only_get_exact_leaf_suggestion():
    text=draft(FACT.replace("(symbol x)","(unknown)"))
    result=fresh.inspect_draft(text,domain_inputs=INPUTS,require_domain_ledger=True)
    assert "Use (symbol unknown)" not in result["parser_feedback"]
    assert not result["parser_valid"]


def test_fence_and_symbol_list_locations():
    text=draft().replace("symbols = x", "symbols = [x]").replace("```guard-args","```text")
    report=feedback.diagnose(text,"parser rejected",inputs=INPUTS)
    assert {"symbol_list","fence"}<={row["code"] for row in report["issues"]}
    assert all(row["line"]>0 for row in report["issues"])


def test_ambiguous_grouping_never_gets_mathematical_repair():
    text=draft(FACT.replace("(symbol x)","(sub x y x)"))
    report=feedback.diagnose(text,"bad operator",inputs=INPUTS)
    assert "arity 3" in report["feedback"]
    assert "likely intended" not in report["feedback"]
    assert report["read_only"] is True


def test_valid_parser_policy_is_unchanged():
    text=draft()
    result=fresh.inspect_draft(text,domain_inputs=INPUTS,require_domain_ledger=True)
    assert result["parser_valid"]
    assert result["proposal"]==parse(text)
    assert "parser_diagnostics" not in result


def test_feedback_is_bounded_and_deterministic():
    facts="\n".join(FACT.replace("- pos",f"- fact{i}").replace("(symbol x)","(x 1)") for i in range(100))
    text=draft(facts)
    a=feedback.diagnose(text,"bad"*1000,inputs=INPUTS)
    assert a==feedback.diagnose(text,"bad"*1000,inputs=INPUTS)
    assert len(a["issues"])<=feedback.MAX_ISSUES
    assert len(a["feedback"])<=feedback.MAX_FEEDBACK_CHARACTERS
    assert "incomplete" in a["feedback"]


def test_rich_feedback_reaches_next_author_without_auditor(tmp_path,monkeypatch):
    for name,text in INPUTS.items():
        fresh.pipeline.base.write_text(tmp_path/"input"/name,text)
    stages=[]
    invalid=draft(FACT.replace("(symbol x)","(x 1)"))
    monkeypatch.setattr(fresh.certificate,"validate_markdown_budget_forcing",lambda *a,**kw:None)
    def caller(**kwargs):
        stages.append(kwargs["stage"])
        if len(stages)==1:
            text=invalid
        elif len(stages)==2:
            assert kwargs["stage"]==fresh.recovery.REPAIR_STAGE
            assert "arity 1" in kwargs["user_prompt"]
            assert "Domain Ledger / pos / expression" in kwargs["user_prompt"]
            assert "No semantic audit was run" in kwargs["user_prompt"]
            text=draft()
        else:
            assert kwargs["stage"]==fresh.recovery.AUDIT_STAGE
            text=audit(True)
        return text,kwargs["parser"](text),{}
    result=fresh.execute(tmp_path,{"domain_ledger_enabled":True},"Generic original contract",1,
        cycles=2,caller=caller,tool=lambda *a:{"verdict":"VERIFIED_SUPPORT","exact_verified":True})
    assert result["state"]=="completed",result
    assert len(stages)==3 and result["audit_calls_skipped"]==1 and result["tool_invocations"]==1
