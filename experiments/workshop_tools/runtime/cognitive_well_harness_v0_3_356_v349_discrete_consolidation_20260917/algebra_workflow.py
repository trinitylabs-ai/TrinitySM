"""Audited request -> checked algebra -> immediate appendix synthesis.

Backend ordering is deterministic, with no model calls between backends. A
radical export computes the explicit identity directly, avoiding a duplicate
positive-screen search. Consistency runs alongside certificate work and rewrite.
"""
from __future__ import annotations

from pathlib import Path

from . import backend_comparison as backends, division_experiment as division
from . import radical_packaging_trial as packaging, radical_resume_synthesis as resume
from . import appendix_synthesis, rewrite
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle, TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

ORDER = ("laurent", "laurent_guarded_radical", "guarded_radical", "division")
LEGACY_PREFIX = ("division", "guarded_radical")


def source_context(request_path, additional_documents=None):
    request, admission = backends.accepted_request(request_path)
    sample = request_path.parents[4]
    documents = {name: (sample / "input" / name).read_text().strip()
        for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md")}
    text = (request_path.parents[1] / "03_final_semantic_audit/input_formalization.md").read_text().strip()
    manifest = resume.read(sample / "manifest.json")
    parsed = division.parse_proposal(text, domain_inputs=documents,
        require_domain_ledger=manifest.get("domain_ledger_enabled", False))
    detection = resume.base.protocol.parse_detection(documents["detection.md"])
    matcher = resume.base._parse_matcher(documents["matcher.md"], detection["desired_exact_fact"])
    extra = dict(additional_documents or {})
    if set(extra) & {DETECTION_DOCUMENT, MATCHER_DOCUMENT}:
        raise ValueError("associated information cannot replace recorded model decisions")
    task = TaskInputs(manifest["problem_id"], documents["theorem.md"], documents["source_proof.md"],
        {DETECTION_DOCUMENT: documents["detection.md"], MATCHER_DOCUMENT: documents["matcher.md"], **extra})
    return request, admission, task, parsed, text, matcher


class DivisionProvider:
    """Replay the saved division witness; never trust its saved verdict alone."""
    provider_id = "checked_division_appendix_v1"

    def __init__(self, request_path, result_path):
        request, admission, _, _, _, matcher = source_context(request_path)
        checked = backends.division.replay(request, resume.read(result_path)["certificate"])
        if not checked["target_proved"]:
            raise ValueError("division certificate did not prove the original target")
        statement, presentation = resume.source_statement(request)
        if presentation["target_label_latex"] != checked["target_label_latex"]:
            raise ValueError("division appendix and main statement use different target labels")
        appendix = "# Appendix A — Proof of the algebraic lemma\n\n" + checked["markdown"]
        sample = request_path.parents[4]
        final = request_path.parents[1] / "03_final_semantic_audit"
        paths = {"request": request_path, "certificate": result_path, "sample_manifest": sample / "manifest.json"}
        paths.update({name: sample / "input" / name for name in
            ("theorem.md", "source_proof.md", "detection.md", "matcher.md")})
        paths.update({"audit_" + name: final / name for name in
            ("parser.json", "result.json", "input_formalization.md", "audit.md")})
        self.hashes = {key: resume.base.sha256_file(path) for key, path in paths.items()}
        self.bundle = EvidenceBundle(self.provider_id, "VERIFIED_SUPPORT", statement,
            {**presentation, "verified": True, "request_sha256": admission["request_sha256"],
             "appendix_sha256": resume.base.sha256_text(appendix),
             "certificate_derivation_supplied": True, "model_must_prove_inserted_lemma": False,
             "independent_source_consistency_check": "not_performed",
             "presentation_kind": "statement_with_verified_appendix", "source_artifact_sha256": self.hashes},
            {"operation": matcher["operation"], "claim": matcher["claim"], "decision": "PROVED",
             "backend": "guarded_division", "scope": "original_target_under_compiled_guards"},
            paths, appendix_markdown=appendix, appendix_in_rewriter_prompt=False)

    def materialize(self):
        if {key: resume.base.sha256_file(path) for key, path in self.bundle.source_artifacts.items()} != self.hashes:
            raise ValueError("division evidence source drift")
        return self.bundle


def rewrite_division(request_path, result_path, output, *, config, seed, documents):
    _, _, task, parsed, text, _ = source_context(request_path, documents)
    provider = DivisionProvider(request_path, result_path)
    return appendix_synthesis.run(task=task, provider=provider, formalization=text,
        bindings=parsed["bindings"], target_label=provider.bundle.verification["target_label_latex"],
        output=output / "02_synthesis", gemma=config.proof_writer(), qwen=config.qwen(), seed=seed)


def resume_prefix(source, request):
    """Reuse only completed non-proofs; this grants no mathematical evidence."""
    old_request, admission = backends.accepted_request(source / "request.json")
    saved = resume.read(source / "cascade_status.json")
    stages = saved.get("stages", [])
    if (old_request != request or saved.get("request_sha256") != admission["request_sha256"]
            or [row["stage"] for row in stages] != ["division", "guarded_radical"]
            or stages[0]["result"].get("verdict") != "INCONCLUSIVE"
            or stages[0]["result"].get("exact_verified") is not False
            or stages[1]["result"].get("state") != "not_certified"
            or stages[1]["result"].get("packaging_started")
            or stages[1]["result"].get("admission") != admission):
        raise ValueError("resume requires this accepted request's completed non-proving prefix")
    prior = stages[1]["result"]
    checks = prior.get("checks", {})
    if (checks.get("certificate", {}).get("verified") is True
            or any(row.get("state") in {"error", "failed_closed"} for row in checks.values())
            or prior != resume.read(source / "guarded_radical/result.json")):
        raise ValueError("saved radical result cannot be reused as a non-proving prefix")
    return stages


def execute(parsed, output, *, config, seed, documents, select, should_stop, resume_after_radical=None):
    """Called only after the existing same-draft parser + semantic admission."""
    output.mkdir(parents=True, exist_ok=False)
    request = {key: parsed[key] for key in ("arguments", "guard_program")}
    backends.write(output / "request.json", request)
    request_path = resume_after_radical / "request.json" if resume_after_radical else output / "request.json"
    _, admission = backends.accepted_request(request_path)
    status = {"state": "running", "backend_order": list(ORDER), "stages": [],
        "request_sha256": admission["request_sha256"], "exact_verified": False,
        "verdict": "INCONCLUSIVE", "feedback_backend": "checked algebra cascade"}
    if resume_after_radical:
        status.update(stages=resume_prefix(resume_after_radical, request),
            resumed_from=str(resume_after_radical), stage="laurent", reused_stages=list(LEGACY_PREFIX),
            backend_order=list(LEGACY_PREFIX) + ["laurent", "laurent_guarded_radical"])
        backends.write(output / "cascade_status.json", status)

    def record(stage, result):
        status["stages"].append({"stage": stage, "result": result})
        status.update(stage=stage)
        backends.write(output / "cascade_status.json", status)

    def radical_trial(preview, root):
        def on_ready(trial):
            return select(request_path, lambda: resume.run(trial, root / "rewrite", seed,
                no_time_limit=True, with_appendix=True, appendix_attach_only=True,
                additional_documents=documents, gemma=config.proof_writer(), qwen=config.qwen()))
        result = packaging.run(request_path, preview, root, timeout=config.algebra_timeout,
            memory=config.memory_mb, on_ready=on_ready)
        # Never release a result invalidated by a late consistency contradiction.
        if result.get("state") == "contradictory_source":
            raise ValueError("source consistency diagnostic found contradictory assumptions")
        if result.get("packaging_error"):
            raise RuntimeError(result["packaging_error"])
        for check in result.get("checks", {}).values():
            if check.get("state") in {"error", "failed_closed"}:
                raise RuntimeError("certificate check failed mechanically: " + str(check))
        if result.get("packaging_started"):
            status.update(exact_verified=True, verdict="VERIFIED_SUPPORT",
                          rewrite_result=result.get("packaging_result"), certified_trial=str(root))
        return result

    if not should_stop():
        preview_root = output / "laurent/preview"
        try:
            preview = backends.integration.bounded_preview_only(source_arguments=request["arguments"],
                candidate_arguments=request["arguments"], guard_program=request["guard_program"],
                output_dir=preview_root, timeout_sec=config.algebra_timeout, memory_mb=config.memory_mb)
        except backends.integration.LaurentInapplicableError as error:
            preview = {"state": "ineligible", "reason": str(error)}
        except TimeoutError as error:
            preview = {"state": "timeout", "reason": str(error)}
        record("laurent", preview)
        if preview.get("state") == "structural_preview_unvalidated":
            backends.bound_preview(preview_root, request)
            if not should_stop():
                record("laurent_guarded_radical", radical_trial(preview_root, output / "laurent_guarded_radical"))
        elif preview.get("state") in {"failed_closed", "error"}:
            raise RuntimeError("Laurent preprocessing failed mechanically: " + str(preview))
    if not status["exact_verified"] and not should_stop() and not resume_after_radical:
        record("guarded_radical", radical_trial(None, output / "guarded_radical"))
    if not status["exact_verified"] and not should_stop() and not resume_after_radical:
        last = division.invoke_tool(parsed, output / "division", timeout=config.division_timeout)
        record("division", last)
        if last.get("exact_verified"):
            # Re-expansion happens before the candidate can claim the synthesis slot.
            DivisionProvider(request_path, output / "division/result.json").materialize()
            result = select(request_path, lambda: rewrite_division(request_path,
                output / "division/result.json", output / "division_rewrite", config=config,
                seed=seed, documents=documents))
            status.update(exact_verified=True, verdict="VERIFIED_SUPPORT", rewrite_result=result)
    status.update(state="completed", reason="No backend produced a checked original-target certificate."
        if not status["exact_verified"] else "Original-target certificate verified; see separate proof audit.")
    backends.write(output / "result.json", status)
    return status
