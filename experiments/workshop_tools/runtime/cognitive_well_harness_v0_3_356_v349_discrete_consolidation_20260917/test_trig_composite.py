import copy

import pytest
import sympy as sp

from . import composite_identity as tool, trig_formalization as formal, trig_experiment as experiment
from .test_rational_division import request, x, y, z

INPUTS = {"theorem.md": "Let t be a real angle and x a real number.",
          "source_proof.md": "Assume x is nonzero and sin(t) is nonzero.",
          "detection.md": "untrusted detector", "matcher.md": "untrusted matcher"}


def draft(body, ledger="NONE", angles="t", scalars="x"):
    return f"""# Decision

CALL_TOOL

# Semantic Bindings

- Symbols and target refer to the supplied assumptions.

# Domain Ledger

{ledger}

# Trig Input

```trig-args
angles = {angles}
scalars = {scalars}
{body}
```
"""


def test_native_trig_parser_compiler_and_real_composite():
    text = draft("equation = E1 :: x :: (sin t)\ntarget = (add (pow x 2) (pow (cos t) 2)) :: 1")
    parsed = formal.parse(text, INPUTS)
    assert parsed["angles"] == ["t"]
    assert len(parsed["compilation"]["request"]["arguments"]["symbols"]) == 3
    assert parsed["compilation"]["target_solving_performed"] is False
    solved = tool.solve(parsed["compilation"]["request"], max_checks=12, stage_seconds=5)
    assert solved["verified"], solved
    assert tool.replay(parsed["compilation"]["request"], solved["certificate"])["verified"]
    assert solved["model_calls"] == solved["singular_calls"] == solved["laurent_calls"] == 0


def test_angle_addition_and_ordered_angle_definition_are_preserved():
    parsed = formal.parse(draft("define = u :: (add t (div pi 2))\nequation = E1 :: x :: (sin u)\ntarget = x :: (cos t)"), INPUTS)
    result = tool.solve(parsed["compilation"]["request"], max_checks=8, stage_seconds=5)
    assert result["verified"]
    assert parsed["definitions"][0]["expression"][0] == "add"


def test_cancellation_cannot_erase_a_missing_denominator_guard():
    text = draft("equation = E1 :: (sin t) :: (sin t)\ntarget = (div x x) :: 1")
    with pytest.raises(ValueError, match="missing nonzero.*x"):
        formal.parse(text, INPUTS)
    ledger = "- gx :: NONZERO :: x :: proof :: x is nonzero :: Explicit source assumption."
    assert formal.parse(draft("equation = E1 :: (sin t) :: (sin t)\ntarget = (div x x) :: 1", ledger), INPUTS)["call_requested"]


def test_cotangent_domain_and_source_excerpts():
    body = "equation = E1 :: x :: (cot t)\ntarget = (mul x (sin t)) :: (cos t)"
    with pytest.raises(ValueError, match="denominator"):
        formal.parse(draft(body), INPUTS)
    ledger = "- gt :: NONZERO :: (sin t) :: proof :: sin(t) is nonzero :: Explicit source assumption."
    parsed = formal.parse(draft(body, ledger), INPUTS)
    assert "sin(t)" in parsed["compilation"]["required_nonzero_expressions"]
    with pytest.raises(ValueError, match="excerpt not found"):
        formal.parse(draft(body, ledger.replace("sin(t) is nonzero", "invented assumption")), INPUTS)


@pytest.mark.parametrize("left,right", [('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’")])
def test_source_excerpt_presentation_quotes_preserve_the_compiled_request(left, right):
    body = "equation = E1 :: x :: (cot t)\ntarget = (mul x (sin t)) :: (cos t)"
    excerpt = "sin(t) is nonzero"
    ledger = f"- gt :: NONZERO :: (sin t) :: proof :: {excerpt} :: Explicit source assumption."
    plain = formal.parse(draft(body, ledger), INPUTS)
    quoted = formal.parse(draft(body, ledger.replace(excerpt, left + excerpt + right)), INPUTS)
    assert quoted == plain
    assert quoted["domain_facts"][0]["excerpt"] == excerpt


@pytest.mark.parametrize("excerpt", [
    '"invented assumption"', '"sin(t) is zero"', '""', "''", "“ ”", "   ",
    '"sin(t) is nonzero', '“sin(t) is nonzero"', '"\'sin(t) is nonzero\'"',
])
def test_source_excerpt_normalization_does_not_accept_missing_or_empty_text(excerpt):
    body = "equation = E1 :: x :: (cot t)\ntarget = (mul x (sin t)) :: (cos t)"
    ledger = f"- gt :: NONZERO :: (sin t) :: proof :: {excerpt} :: Explicit source assumption."
    with pytest.raises(ValueError, match="excerpt not found"):
        formal.parse(draft(body, ledger), INPUTS)


def test_source_excerpt_normalization_preserves_literal_quotes_and_latex():
    literal = '"a quoted assumption"'
    assert formal.source_bound_excerpt(literal, "Use " + literal + ".") == literal
    assert formal.source_bound_excerpt("'x' is nonzero", "Assume 'x' is nonzero.") == "'x' is nonzero"
    latex = r"\sin(\phi + \psi)"
    assert formal.source_bound_excerpt('"' + latex + '"', latex) == latex
    assert formal.source_bound_excerpt('"' + latex[1:] + '"', "sin(phi + psi)") is None
    assert formal.source_bound_excerpt('" sin(t)  is nonzero "', "sin(t) is nonzero") == "sin(t)  is nonzero"


def test_quoted_excerpts_do_not_bypass_source_selection_or_domain_checks():
    body = "equation = E1 :: x :: (cot t)\ntarget = (mul x (sin t)) :: (cos t)"
    ledger = '- gt :: NONZERO :: (sin t) :: theorem :: "sin(t) is nonzero" :: Explicit source assumption.'
    with pytest.raises(ValueError, match="excerpt not found in theorem"):
        formal.parse(draft(body, ledger), INPUTS)
    ledger = '- gx :: NONZERO :: x :: proof :: "x is nonzero" :: Explicit source assumption.'
    with pytest.raises(ValueError, match="missing nonzero.*sin"):
        formal.parse(draft(body, ledger), INPUTS)


@pytest.mark.parametrize("expression", ["(sin x)", "(sin (mul t t))", "(sin (div t 2))", "(eval t)", "(symbol missing)"])
def test_unsupported_or_unbound_expressions_fail_closed(expression):
    with pytest.raises(ValueError):
        formal.parse(draft(f"equation = E1 :: x :: (sin t)\ntarget = {expression} :: 0"), INPUTS)


@pytest.mark.parametrize("equations,target,guards,expected", [
    ([x*y], x, (), False),
    ([x*y], x, (y,), True),
    ([(x-y)**2], x-y, (), True),
    ([x*x-y*y], x-y, (), False),
    ([x-y,y*y-z], x*x-z, (), True),
])
def test_exact_composite_admission_and_factor_rules(equations, target, guards, expected):
    req = request(equations, target, guards)
    first = tool.solve(req, max_checks=12, max_depth=2, stage_seconds=5)
    second = tool.solve(req, max_checks=12, max_depth=2, stage_seconds=5)
    assert first["verified"] is expected
    assert [(r["policy"], r["depth"], r["outcome"]) for r in first["checks"]] == [
        (r["policy"], r["depth"], r["outcome"]) for r in second["checks"]]
    if expected:
        assert first["certificate"] == second["certificate"]
        changed = copy.deepcopy(first["certificate"])
        changed["factor_trace"][0]["coefficient"] = 99
        with pytest.raises(ValueError, match="factorization"):
            tool.replay(req, changed)


def test_false_constant_domain_fact_and_json_are_rejected():
    ledger = "- bad :: POSITIVE :: -1 :: proof :: x is nonzero :: Deliberately invalid."
    with pytest.raises(ValueError, match="false constant"):
        formal.parse(draft("equation = E1 :: x :: (sin t)\ntarget = x :: (sin t)", ledger), INPUTS)
    with pytest.raises(ValueError):
        formal.parse('{"decision":"CALL_TOOL"}', INPUTS)


def test_audit_parser_is_not_accepting_repaired_or_inconsistent_verdicts():
    checks = "\n".join(f"- {label}: PASS" for label in experiment.CHECKS)
    audit = f"# Decision\n\nACCEPT\n\n# Checks\n\n{checks}\n\n# Issues\n\nNONE"
    assert experiment.audit_parse(audit)["accepted"]
    with pytest.raises(ValueError, match="disagrees"):
        experiment.audit_parse(audit.replace("Issues\n\nNONE", "Issues\n\n- Missing derivation."))


def test_inspection_returns_parser_feedback_without_running_a_solver(monkeypatch):
    monkeypatch.setattr(tool, "solve", lambda *a, **k: pytest.fail("parser must not run proof search"))
    text = draft("equation = E1 :: x :: (cot t)\ntarget = x :: (cot t)")
    report = experiment.inspect(text, INPUTS)
    assert report["parser_valid"] is False and "denominator" in report["feedback"]


@pytest.mark.parametrize("mode", ["parser_failure", "audit_reject", "accepted_then_feedback"])
def test_model_gates_and_tool_feedback(tmp_path, monkeypatch, mode):
    source = tmp_path / "source"
    for name, value in INPUTS.items():
        experiment.base.write_text(source / "input" / name, value)
    # Model transport is mocked only here; production validates BF provenance.
    monkeypatch.setattr(experiment.certificate, "validate_markdown_budget_forcing", lambda *a, **k: None)
    calls = []
    author_count = 0
    valid = draft("equation = E1 :: x :: (sin t)\ntarget = x :: (sin t)")

    def caller(**kwargs):
        nonlocal author_count
        stage = kwargs["stage"]
        calls.append(stage)
        if stage == "native_trig_formalization":
            author_count += 1
            if author_count == 2:
                assert "Tool feedback" in kwargs["user_prompt"]
                text = "# Decision\n\nNO_TOOL\n\n# Reason\n\nNo faithful alternative."
            else:
                text = "malformed" if mode == "parser_failure" else valid
        else:
            decision = "REJECT" if mode == "audit_reject" else "ACCEPT"
            check = "FAIL" if mode == "audit_reject" else "PASS"
            checks = "\n".join(f"- {label}: {check}" for label in experiment.CHECKS)
            issues = "- A source connection is missing." if mode == "audit_reject" else "NONE"
            text = f"# Decision\n\n{decision}\n\n# Checks\n\n{checks}\n\n# Issues\n\n{issues}"
        text = text.strip()
        return text, kwargs["parser"](text), {}

    def execute_tool(root):
        assert mode == "accepted_then_feedback", "tool ran despite a failed gate"
        assert experiment.load_admitted(root)["call_requested"]
        return {"verdict": "INCONCLUSIVE", "verified": False, "reason": "bounded test result"}

    result = experiment.run(source, tmp_path / "run", 17,
        cycles=2 if mode == "accepted_then_feedback" else 1, caller=caller, tool=execute_tool)
    assert result["state"] == "completed", result
    if mode == "parser_failure":
        assert calls == ["native_trig_formalization"]
        assert result["cycles"][0]["semantic_audit"] == "SKIPPED_PARSER_FAIL"
    elif mode == "audit_reject":
        assert result["tool_invocations"] == 0
    else:
        assert result["tool_invocations"] == 1
        assert result["stage"] == "model_declined_tool"


@pytest.mark.parametrize("mode", ["reject_then_prove", "inconclusive_then_prove", "parser_fail_then_prove", "first_proves", "both_rejected"])
def test_saved_cycles_resume_at_audit_and_stop_at_first_verified(tmp_path, monkeypatch, mode):
    source = tmp_path / "source"
    for name, value in INPUTS.items():
        experiment.base.write_text(source / "input" / name, value)
    experiment.artifacts.write(source / "manifest.json", {
        "input_sha256": {name: experiment.base.sha256_text(value) for name, value in INPUTS.items()}})
    originals = {}
    for number in (2, 3):
        text = draft("equation = E1 :: x :: (sin t)\ntarget = x :: (sin t)").strip()
        if number == 2 and mode == "parser_fail_then_prove":
            text = "malformed"
        originals[number] = text
        saved = source / "cycles" / f"cycle_{number:02d}"
        experiment.base.write_text(saved / "formalization.md", text)
        experiment.artifacts.write(saved / "formalizer/call.json", {"saved": number})
    monkeypatch.setattr(experiment.certificate, "validate_markdown_budget_forcing", lambda *a, **k: None)
    calls, executions = [], []

    def caller(**kwargs):
        assert kwargs["stage"] == "native_trig_semantic_audit", "resume must not generate formalizations"
        calls.append(kwargs["stage"])
        reject = mode == "both_rejected" or (mode == "reject_then_prove" and len(calls) == 1)
        verdict, check, issues = ("REJECT", "FAIL", "- Missing justification.") if reject else ("ACCEPT", "PASS", "NONE")
        checks = "\n".join(f"- {label}: {check}" for label in experiment.CHECKS)
        text = f"# Decision\n\n{verdict}\n\n# Checks\n\n{checks}\n\n# Issues\n\n{issues}"
        return text, kwargs["parser"](text), {}

    def execute(root):
        assert experiment.load_admitted(root)["call_requested"]
        executions.append(root)
        proved = mode != "inconclusive_then_prove" or len(executions) == 2
        return {"verdict": "PROVED" if proved else "INCONCLUSIVE", "verified": proved}

    output = tmp_path / "recovered"
    result = experiment.run(source, output, 17, saved_cycles=[2, 3], caller=caller, tool=execute)
    assert result["state"] == "completed", result
    assert result["fresh_formalization_calls"] == 0 and result["max_model_stages"] == 2
    if mode == "both_rejected":
        assert result["stage"] == "saved_candidates_exhausted" and not executions
    else:
        assert result["stage"] == "verified_native_trig_target"
        assert result["selected_cycle"] == (1 if mode == "first_proves" else 2)
    assert len(executions) == (0 if mode == "both_rejected" else 2 if mode == "inconclusive_then_prove" else 1)
    assert len(calls) == (1 if mode in {"first_proves", "parser_fail_then_prove"} else 2)
    for number, text in originals.items():
        assert (source / "cycles" / f"cycle_{number:02d}" / "formalization.md").read_text().strip() == text


def test_saved_cycle_recovery_rejects_changed_source_before_model_calls(tmp_path):
    source = tmp_path / "source"
    for name, value in INPUTS.items():
        experiment.base.write_text(source / "input" / name, value)
    experiment.artifacts.write(source / "manifest.json", {"input_sha256": {name: "wrong" for name in INPUTS}})
    with pytest.raises(ValueError, match="source input changed"):
        experiment.run(source, tmp_path / "recovered", 17, saved_cycles=[2],
                       caller=lambda **k: pytest.fail("changed source reached a model"))
