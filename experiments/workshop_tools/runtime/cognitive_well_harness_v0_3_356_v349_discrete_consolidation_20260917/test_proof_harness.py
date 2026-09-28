"""Wiring tests use synthetic mathematics and no GPU or external grader."""
from dataclasses import replace
from pathlib import Path

import pytest

from . import proof_harness as harness, algebra_workflow as workflow, appendix_synthesis
from . import radical_resume_synthesis as resume, radical_certificate as radical
from .test_division_audit_repair import audit
from .test_domain_ledger import draft, INPUTS
from .test_appendix import fixture
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import pipeline as core, tool_purpose


def sources(tmp_path):
    problem, proof = tmp_path / "problem.json", tmp_path / "proof.md"
    harness.rewrite.write_record(problem, {"problem_id": "synthetic", "statement": INPUTS["theorem.md"],
                                         "reference_solution": "MUST_NOT_APPEAR_IN_PROMPTS"})
    harness.base.write_text(proof, INPUTS["source_proof.md"])
    return problem, proof


def decisions(proof, requested=True, operation="polynomial_ideal_membership"):
    if not requested:
        return "# Decision\n\nNO_TOOL\n\n" + "\n\n".join(
            f"# {name}\n\nNONE" for name in ("Load-Bearing Gap", "Trigger Evidence", "Evidence Task",
                                              "Desired Exact Fact", "Downstream Obligation"))
    claim = "Prove the requested algebraic consequence."
    detection = f"# Decision\n\nCALL_TOOL\n\n# Load-Bearing Gap\n\nThe identity needs a derivation.\n\n# Trigger Evidence\n\n{proof}\n\n# Evidence Task\n\nCERTIFY_DERIVATION\n\n# Desired Exact Fact\n\n{claim}\n\n# Downstream Obligation\n\nComplete the proof."
    matcher = f"# Decision\n\nCALL_TOOL\n\n# Operation\n\n{operation}\n\n# Immutable Claim\n\n{claim}\n\n# Fit Rationale\n\nThe target is algebraic."
    return detection, matcher


def test_preflight_is_offline_and_strips_reference_fields(tmp_path, monkeypatch):
    problem, proof = sources(tmp_path)
    monkeypatch.setattr(harness, "acquire", lambda *a, **k: pytest.fail("preflight called a model"))
    out = tmp_path / "run"
    result = harness.run(problem_file=problem, proof_file=proof, output=out)
    assert result["state"] == "prepared"
    assert result["max_logical_model_stages"] == 58
    assert result["final_qwen_revision"] and result["max_final_revision_cycles"] == 1
    assert "reference_solution" not in (out / "input/problem.json").read_text()
    assert not result["appendix_in_rewriter_prompt"]
    with pytest.raises(FileExistsError):
        harness.run(problem_file=problem, proof_file=proof, output=out)


@pytest.mark.parametrize("decision", ["CALL_TOOL", "NO_TOOL"])
def test_matcher_template_matches_existing_parser_and_preserves_choice(tmp_path, decision):
    problem, proof = sources(tmp_path)
    out = tmp_path / "run"
    harness.run(problem_file=problem, proof_file=proof, output=out)
    detection, _ = decisions(proof.read_text().strip())
    claim = harness.acquisition.protocol.parse_detection(detection)["desired_exact_fact"]
    call_template = harness.MATCHER_RESPONSE_TEMPLATE.split("If your decision is CALL_TOOL:\n", 1)[1]
    call_template, no_tool_template = call_template.split("If your decision is NO_TOOL:\n", 1)
    text = call_template if decision == "CALL_TOOL" else no_tool_template
    text = (text.replace("<exactly one operation from the supplied allowlist>", "polynomial_ideal_membership")
            .replace("<copy the supplied desired exact fact byte-for-byte>", claim)
            .replace("<one paragraph explaining why the operation fits>", "The requested consequence is algebraic.")
            .replace("<one paragraph explaining why no allowed operation fits>", "The requested task needs a new argument."))
    stages = []

    def call(**kw):
        stages.append(kw["stage"])
        if kw["stage"] == "direct_laurent_gap_detection":
            assert kw["system_prompt"] == harness.base.DETECTOR_SYSTEM
            response = detection
        else:
            allowed = harness.matcher_operations(())
            assert kw["system_prompt"] == harness.matcher_system(allowed) + harness.MATCHER_RESPONSE_TEMPLATE
            response = text
        return response, kw["parser"](response), {}

    result = harness.acquire(out, config=harness.Config(), seed=1, documents={}, caller=call)
    assert result["decision"] == decision
    assert stages == ["direct_laurent_gap_detection", "direct_laurent_operation_matcher"]
    if decision == "CALL_TOOL":
        assert result["record"]["claim"] == claim


def test_missing_matcher_decision_remains_rejected():
    text = "# Decision\n# Operation: polynomial_ideal_membership\n# Immutable Claim: x=x\n# Fit Rationale: Algebra."
    with pytest.raises(ValueError, match="empty section 'Decision'"):
        harness.base._parse_matcher(text, "x=x")


def test_cli_config_bounds_and_reserved_documents(tmp_path):
    for config in (harness.Config(workers=9), harness.Config(cycles=4), harness.Config(batch_size=0),
                   harness.Config(proof_rewriter="unknown")):
        with pytest.raises(ValueError):
            config.validate()
    problem, proof = sources(tmp_path)
    reserved = tmp_path / "tool_detection.md"
    harness.base.write_text(reserved, "Cannot override a model decision.")
    with pytest.raises(ValueError, match="reserved"):
        harness.run(problem_file=problem, proof_file=proof, output=tmp_path / "out", associated=[reserved])


def test_writer_switch_does_not_change_other_roles_or_legacy_configs():
    config = harness.Config()
    assert config.proof_writer().model == config.qwen().model
    assert config.proof_writer().temperature == .2 and config.qwen().temperature == .1
    assert config.gemma().model == harness.base.DEFAULT_GEMMA_MODEL
    assert harness.Config.from_saved({}).proof_rewriter == "gemma"
    assert harness.Config.from_saved({"proof_rewriter": "qwen"}).proof_rewriter == "qwen"
    assert harness.Config().shared_lane_feedback is True
    assert harness.Config.from_saved({}).shared_lane_feedback is False
    assert harness.Config.from_saved({'shared_lane_feedback':True}).shared_lane_feedback is True
    with pytest.raises(ValueError,match='boolean'):
        harness.Config(shared_lane_feedback='yes').validate()


def test_certified_resume_uses_selected_writer(tmp_path, monkeypatch):
    calls = []
    def saved_run(*args, **kw):
        calls.append(kw)
        return {"state": "failed_closed"}
    monkeypatch.setattr(harness.resume, "run", saved_run)
    harness.resume_certified(tmp_path / "certificate", tmp_path / "out", seed=7)
    assert calls[0]["gemma"].model == calls[0]["qwen"].model == harness.base.DEFAULT_QWEN_MODEL
    assert calls[0]["gemma"].temperature == .2 and calls[0]["qwen"].temperature == .1
    assert calls[0]["appendix_attach_only"] and calls[0]["no_time_limit"]


def test_detection_decline_is_not_overridden(tmp_path, monkeypatch):
    problem, proof = sources(tmp_path)
    events = []
    class Calls:
        def __init__(self, *a, **k): pass
        def __call__(self, **kw):
            events.append(kw["stage"])
            text = decisions("", requested=False)
            return text, kw["parser"](text), {}
    monkeypatch.setattr(harness.rewrite, "BudgetedCalls", Calls)
    result = harness.run(problem_file=problem, proof_file=proof, output=tmp_path / "run", execute_models=True)
    assert result["outcome"] == "NO_TOOL", result
    assert len(events) == 1 and not result["proof_audit_passed"]
    assert not (tmp_path / "run/rewritten_proof.md").exists()


def test_menu_exclusion_reuses_detection_but_leaves_new_choice_to_model(tmp_path, monkeypatch):
    problem, proof = sources(tmp_path)
    old, out = tmp_path / "old", tmp_path / "new"
    harness.run(problem_file=problem, proof_file=proof, output=old)
    detection, matcher = decisions(proof.read_text().strip(), operation="rational_identity")
    root = old / "01_acquisition"
    harness.base.write_text(root / "01_detection/detection.md", detection)
    harness.rewrite.write_record(root / "model_budget.json", {"calls": [{
        "stage": "direct_laurent_gap_detection", "state": "completed", "attempt": 1, "cap": 32768}]})
    harness.rewrite.write_record(root / "01_detection/model/attempt_01_cap_32768/direct_laurent_gap_detection.metadata.json",
        {"config": {"timeout_seconds": 600}})
    checked = []
    monkeypatch.setattr(harness.fresh.certificate, "validate_markdown_budget_forcing",
        lambda call, **kw: checked.append(kw["canonical_markdown"]))
    events = []
    class Calls:
        def __init__(self, *a, **k): assert k["max_stages"] == 1
        def __call__(self, **kw):
            events.append(kw["stage"])
            assert kw["stage"].endswith("operation_matcher")
            assert "expand_and_compare" not in kw["system_prompt"] + kw["user_prompt"]
            assert "simplify_identity" not in kw["system_prompt"] + kw["user_prompt"]
            assert "exact_geometry" not in kw["system_prompt"] + kw["user_prompt"]
            assert "rational_identity" in kw["user_prompt"]
            return matcher, kw["parser"](matcher), {}
    monkeypatch.setattr(harness.rewrite, "BudgetedCalls", Calls)
    from . import geometry_workflow
    routes = []
    def track(*args, **kw):
        routes.append(kw['matcher']['operation'])
        return {'state': 'completed', 'exact_verified': False}
    monkeypatch.setattr(geometry_workflow, 'run_track', track)
    result = harness.run(problem_file=problem, proof_file=proof, output=out, execute_models=True,
        detection_from=old, config=harness.Config(batch_size=1, workers=1,
            excluded_operations=("simplify_identity", "expand_and_compare", "exact_geometry")))
    assert len(events) == 1 and checked
    assert result["acquisition"]["record"]["operation"] == "rational_identity"
    assert routes == ['rational_identity']
    assert result["outcome"] == "NO_CERTIFIED_REWRITE"  # an allowed choice reaches its executor
    assert (out / "01_acquisition/01_detection/detection.md").read_text().strip() == detection.strip()
    manifest = harness.resume.read(out / "01_acquisition/manifest.json")
    assert "expand_and_compare" not in manifest["allowed_matcher_operations"]
    harness.base.write_text(old / "input/source_proof.md", "changed proof")
    with pytest.raises(ValueError, match="input drift"):
        harness.reuse_detection(old, out)


@pytest.mark.parametrize("recovery", [None, "resume", "qwen_override", "input_drift", "already_called"])
def test_new_harness_from_detection_through_parser_audit_and_real_division(tmp_path, monkeypatch, recovery):
    problem, proof = sources(tmp_path)
    detection, matcher = decisions(proof.read_text().strip())
    events, admissions = [], []
    monkeypatch.setattr(harness.fresh.certificate, "validate_markdown_budget_forcing", lambda *a, **k: None)
    class Calls:
        def __init__(self, *a, **k): pass
        def __call__(self, **kw):
            stage = kw["stage"]
            events.append(stage)
            assert "MUST_NOT_APPEAR_IN_PROMPTS" not in kw["user_prompt"]
            if stage.endswith("gap_detection"):
                text = detection
            elif stage.endswith("operation_matcher"):
                text = matcher
            elif stage == harness.fresh.recovery.AUDIT_STAGE:
                assert "# Exact Tool Feedback" not in kw["user_prompt"]
                text = audit(True)
            else:
                assert "radical membership" in kw["system_prompt"]
                assert "division only" not in kw["user_prompt"]
                text = draft()
            return text, kw["parser"](text), {}
    monkeypatch.setattr(harness.rewrite, "BudgetedCalls", Calls)
    def rewrite_division(request_path, result_path, output, **kw):
        expected_writer = "qwen" if recovery == "qwen_override" and admissions else "gemma"
        assert kw["config"].proof_rewriter == expected_writer
        request, admission, task, parsed, text, _ = workflow.source_context(request_path)
        admissions.append(admission)
        bundle = workflow.DivisionProvider(request_path, result_path).materialize()
        assert not bundle.appendix_in_rewriter_prompt and bundle.verification["verified"]
        assert "remainder is zero" in bundle.appendix_markdown
        if recovery and len(admissions) == 1:
            error = "explicit update requires one unique verbatim detector trigger in the original proof"
            harness.rewrite.write_record(output / "02_synthesis/manifest.json", {
                "state": "failed_closed", "cycles": [], "error": "ValueError: " + error})
            raise ValueError(error)
        final = output / "02_synthesis/terminal_proof.md"
        assembled = "Synthetic main proof.\n\n" + bundle.markdown + "\n\n" + bundle.appendix_markdown
        harness.base.write_text(final, assembled)
        return {"state": "completed", "synthesis": {"proof_audit_passed": True,
            "terminal_proof": str(final), "terminal_proof_sha256": harness.base.sha256_text(assembled)}}
    monkeypatch.setattr(workflow, "rewrite_division", rewrite_division)
    monkeypatch.setattr(workflow.backends.integration, "bounded_preview_only", lambda **k: {"state": "ineligible"})
    monkeypatch.setattr(workflow.packaging, "run", lambda *a, **k:
        {"state": "not_certified", "checks": {"certificate": {"verified": False}}})
    result = harness.run(problem_file=problem, proof_file=proof, output=tmp_path / "run", seed=42,
        config=harness.Config(batch_size=2, workers=1, proof_rewriter="gemma"), execute_models=True)
    if recovery:
        from . import resume_selected_division
        assert result["outcome"] == "CERTIFIED_LEMMA_REWRITE_NOT_ACCEPTED"
        source = tmp_path / "run"
        old_hashes = {p: harness.base.sha256_file(p) for p in source.rglob("*") if p.is_file()}
        if recovery == "input_drift":
            harness.base.write_text(source / "input/source_proof.md", "Different source")
        elif recovery == "already_called":
            request = Path(harness.resume.read(source / "selection.json")["request_path"])
            harness.base.write_text(request.parent / "division_rewrite/model/old.prompt.txt", "Prior model call")
        if recovery not in {"resume", "qwen_override"}:
            with pytest.raises(ValueError, match="input drift|before any rewrite call"):
                resume_selected_division.run(source, tmp_path / "resumed")
            assert len(events) == 4 and len(admissions) == 1
            return
        result = resume_selected_division.run(source, tmp_path / "resumed",
            proof_rewriter="qwen" if recovery == "qwen_override" else None)
        if recovery == "qwen_override":
            assert result["model_role_override"] == {"proof_rewriter": {"from": "gemma", "to": "qwen"}}
        assert result["new_solver_searches"] == result["new_formalization_calls"] == 0
        assert result["certificate_replayed"]
        sample_seed = harness.resume.read(source / "02_formalizations/sample_01/status.json")["master_seed"]
        assert result["master_seed"] == sample_seed
        assert {p: harness.base.sha256_file(p) for p in old_hashes} == old_hashes
    assert result["outcome"] == "REWRITTEN_AUDIT_PASS", result
    assert len(events) == 4 and len(admissions) == (2 if recovery else 1)
    assert admissions[0]["parser"] == "PASS" and admissions[0]["semantic"] == "ACCEPT"
    if not recovery:
        assert any(row["state"] == "superseded_by_verified_candidate" for row in result["samples"])
    assert result["strict_score"] is None
    saved = Path(result["rewritten_proof"]).read_text()
    assert saved.count("# Appendix A") == 1


def test_no_false_publication_and_hash_binding(tmp_path):
    result = harness.publish(tmp_path / "failed", {"state": "completed", "selected": {
        "result": {"state": "completed", "synthesis": {"proof_audit_passed": False}}}})
    assert result["state"] == "failed_closed" and not result["proof_audit_passed"]
    proof = tmp_path / "changed.md"
    harness.base.write_text(proof, "changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        harness.publish(tmp_path / "mismatch", {"selected": {"result": {"state": "completed", "synthesis": {
            "proof_audit_passed": True, "terminal_proof": str(proof), "terminal_proof_sha256": "wrong"}}}})


def test_shared_appendix_synthesis_matches_successful_prompt_policy(tmp_path, monkeypatch):
    evidence, contract, task = fixture(tmp_path)
    task = replace(task, additional_documents={"fusion_packet.md": "UNTRUSTED_FUSION_PACKET",
                                               "other_context.md": "OTHER_ASSOCIATED_INPUT"})
    evidence = replace(evidence, appendix_in_rewriter_prompt=False)
    class Provider:
        def materialize(self): return evidence
    monkeypatch.setattr(harness.rewrite.pipeline, "_verify_synthesis_budget_forcing", lambda **k: {})
    prompts = []
    def calls(**kw):
        prompts.append(kw)
        assert kw["request_timeout_sec"] is None
        if kw["stage"].endswith("rewrite"):
            assert "UNTRUSTED_FUSION_PACKET" not in kw["user_prompt"]
            assert evidence.appendix_markdown not in kw["user_prompt"]
            assert resume.ATTACH_ONLY_POLICY in kw["system_prompt"]
            text = "Apply the lemma proved in Appendix A.\n\n" + contract.evidence_marker + "\n\nThus x-y=0."
        else:
            assert "UNTRUSTED_FUSION_PACKET" in kw["user_prompt"]
            assert evidence.appendix_markdown in kw["user_prompt"]
            assert resume.APPENDIX_POLICY in kw["system_prompt"]
            text = "# Decision\n\nPASS\n\n# Checks\n\n" + "\n".join(
                "- " + name + ": PASS" for name in core.protocol.PROOF_AUDIT_CHECKS) + "\n\n# Issues\n\nNONE"
        return text, kw["parser"](text), {}
    result = appendix_synthesis.run(task=task, provider=Provider(), formalization="Frozen model input.",
        bindings={}, target_label="T", output=tmp_path / "run", gemma=harness.Config().gemma(),
        qwen=harness.Config().qwen(), seed=1, model_call=calls)
    assert result["state"] == "completed" and len(prompts) == 4
    assert all("Frozen model input." in kw["user_prompt"] for kw in prompts)
    assert all("OTHER_ASSOCIATED_INPUT" in kw["user_prompt"] for kw in prompts)
    policy = resume.read(tmp_path / "run/02_rewrite/cycle_01/context_policy.json")
    assert policy["first_proof_rewrite"]
    assert policy["omitted_document_sha256"] == {
        "fusion_packet.md": harness.base.sha256_text("UNTRUSTED_FUSION_PACKET")}
    assert (tmp_path / "run/input/additional/fusion_packet.md").is_file()


def test_fusion_first_rewrite_ablation_does_not_change_later_repair_context(tmp_path, monkeypatch):
    evidence, contract, task = fixture(tmp_path)
    evidence = replace(evidence, appendix_in_rewriter_prompt=False)
    task = replace(task, additional_documents={"fusion_packet.md": "UNTRUSTED_FUSION_PACKET"})
    class Provider:
        def materialize(self): return evidence
    monkeypatch.setattr(harness.rewrite.pipeline, "_verify_synthesis_budget_forcing", lambda **k: {})
    writers, audits = [], []
    def calls(**kw):
        if kw["stage"].endswith("rewrite"):
            writers.append(kw["user_prompt"])
            text = "Apply the following lemma.\n" + contract.evidence_marker + "\nThus the conclusion follows."
        else:
            audits.append(kw["user_prompt"])
            passed = len(audits) == 2
            text = "# Decision\n\n" + ("PASS" if passed else "FAIL") + "\n\n# Checks\n\n" + "\n".join(
                f"- {name}: {'PASS' if passed or index else 'FAIL'}"
                for index, name in enumerate(core.protocol.PROOF_AUDIT_CHECKS))
            text += "\n\n# Issues\n\n" + ("NONE" if passed else "- Derive the lemma's hypotheses explicitly.")
        return text, kw["parser"](text), {}
    result = appendix_synthesis.run(task=task, provider=Provider(), formalization="Frozen model input.",
        bindings={}, target_label="T", output=tmp_path / "run", gemma=harness.Config().gemma(),
        qwen=harness.Config().qwen(), seed=1, model_call=calls, max_cycles=2,
        final_qwen_revision=False)
    assert result["state"] == "completed" and len(writers) == len(audits) == 2
    assert "UNTRUSTED_FUSION_PACKET" not in writers[0]
    assert "UNTRUSTED_FUSION_PACKET" in writers[1]
    assert all("UNTRUSTED_FUSION_PACKET" in prompt for prompt in audits)


def test_direct_radical_appendix_replays_without_laurent(tmp_path, monkeypatch):
    # A nilpotent equation needs radical membership, not ordinary membership.
    import sympy as sp
    x = sp.Symbol("x")
    system = radical.system_payload([x], [("E", x*x)], x, {})
    trial = tmp_path / "trial"
    verified = radical.export(system, trial / "certificate/identity", timeout=5, memory=1024)
    assert verified["verified"]
    sample = tmp_path / "sample"
    request_path = sample / "cycles/cycle_01/03_execution/04_tool/request.json"
    request = {"arguments": {"symbols": ["x"], "generators": {"E": {"pow": [{"symbol": "x"}, 2]}},
                             "target": {"symbol": "x"}},
               "guard_program": {"source_nonzero": {}, "provenance_divisions": {}}}
    admission = {"request_sha256": resume.stable_hash(request)}
    for path in (request_path, trial / "request.json", trial / "manifest.json", sample / "manifest.json"):
        harness.rewrite.write_record(path, request)
    for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md"):
        harness.base.write_text(sample / "input" / name, "Synthetic source")
    for name in ("parser.json", "result.json", "input_formalization.md", "audit.md"):
        harness.base.write_text(request_path.parents[1] / "03_final_semantic_audit" / name, "Synthetic acceptance")
    monkeypatch.setattr(resume, "saved_inputs", lambda *a: (request_path, None, request, admission, None, system))
    resume.render_saved(trial, tmp_path / "render", with_appendix=True)
    record = resume.read(tmp_path / "render/saved_lemma_verification.json")
    assert record["coefficient_tables_reparsed"] and not record["laurent_lift_verified"]
    assert "contradiction" in (tmp_path / "render/saved_appendix.md").read_text()
    copied = resume.reuse_appendix(trial, tmp_path / "render", tmp_path / "reused")
    assert copied["verified"]
    assert (tmp_path / "render/saved_appendix.md").read_bytes() == (tmp_path / "reused/saved_appendix.md").read_bytes()


@pytest.mark.parametrize("winner,preview_available,expected", [
    ("guarded_radical", True, ["laurent", "laurent_guarded_radical", "guarded_radical", "rewrite"]),
    ("laurent_guarded_radical", True, ["laurent", "laurent_guarded_radical", "rewrite"]),
    (None, True, ["laurent", "laurent_guarded_radical", "guarded_radical", "division"]),
    (None, False, ["laurent", "guarded_radical", "division"]),
])
def test_production_cascade_order_with_isolated_backends(tmp_path, monkeypatch, winner, preview_available, expected):
    parsed = harness.fresh.division.parse_proposal(draft(), domain_inputs=INPUTS, require_domain_ledger=True)
    events = []
    monkeypatch.setattr(workflow.backends, "accepted_request", lambda path: (
        resume.read(path), {"request_sha256": resume.stable_hash(resume.read(path))}))
    monkeypatch.setattr(workflow.division, "invoke_tool", lambda *a, **k: events.append("division") or
        {"exact_verified": False, "verdict": "INCONCLUSIVE"})
    def packaging(request_path, preview_path, root, **kw):
        stage = "laurent_guarded_radical" if preview_path else "guarded_radical"
        events.append(stage)
        if stage == winner:
            return {"state": "ready_for_packaging", "packaging_started": True,
                    "packaging_result": kw["on_ready"](root), "checks": {"certificate": {"verified": True}}}
        return {"state": "not_certified", "checks": {"certificate": {"state": "certificate_timeout"}}}
    monkeypatch.setattr(workflow.packaging, "run", packaging)
    monkeypatch.setattr(workflow.backends.integration, "bounded_preview_only", lambda **k:
        events.append("laurent") or {"state": "structural_preview_unvalidated" if preview_available else "ineligible"})
    monkeypatch.setattr(workflow.backends, "bound_preview", lambda *a: None)
    def synthesize(*args, **kw):
        assert kw["gemma"].model == kw["qwen"].model == harness.base.DEFAULT_QWEN_MODEL
        assert kw["gemma"].temperature == .2
        events.append("rewrite")
        return {"state": "completed"}
    monkeypatch.setattr(workflow.resume, "run", synthesize)
    result = workflow.execute(parsed, tmp_path / "tool", config=harness.Config(), seed=1, documents={},
        select=lambda request, operation: operation(), should_stop=lambda: False)
    assert events == expected
    assert result["exact_verified"] == bool(winner)


def test_division_display_names_do_not_shadow_source_variables():
    import sympy as sp
    from cognitive_well_harness_v0_3_275_generic_audited_ledger_compression_20260905.transformation_validation import _polynomial_ast
    names = ["T", "N", "D", "E_1", "E1"]
    t, n, d, e1, e2 = sp.symbols(" ".join(names))
    request = {"arguments": {"symbols": names, "generators": {"D": _polynomial_ast(t-n-d, names)},
                             "target": _polynomial_ast(t-n-d, names)},
               "guard_program": {"source_nonzero": {}, "provenance_divisions": {}}}
    result = workflow.backends.division.solve(request)
    checked = workflow.backends.division.replay(request, result["certificate"])
    assert checked["target_label_latex"] != "T" and checked["target_proved"]
    assert checked["target_label_latex"] == resume.source_statement(request)[1]["target_label_latex"]
