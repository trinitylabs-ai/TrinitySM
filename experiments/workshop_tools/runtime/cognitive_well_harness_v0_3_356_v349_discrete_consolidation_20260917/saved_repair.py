"""Bind a saved rejecting audit to its own draft before a generic repair replay."""
from pathlib import Path

from . import certificate, radical_resume_synthesis as resume
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import tool_purpose, validation

base = resume.base


def documents(source):
    core = source / "02_synthesis"
    lock = resume.read(core / "protocol_lock.json")["task"]
    result = {}
    for name, digest in lock["additional_documents_sha256"].items():
        if Path(name).name != name:
            raise ValueError("unsafe saved document name")
        text = (core / "input/additional" / name).read_text().strip()
        if base.sha256_text(text) != digest:
            raise ValueError("saved associated document changed")
        if name not in {tool_purpose.DETECTION_DOCUMENT, tool_purpose.MATCHER_DOCUMENT}:
            result[name] = text
    return result


def load(source, cycle, *, task, evidence, contract):
    core = source / "02_synthesis"
    lock = resume.read(core / "protocol_lock.json")
    expected_task = {"problem_id": task.problem_id,
        "theorem_sha256": base.sha256_text(task.theorem),
        "source_proof_sha256": base.sha256_text(task.source_proof),
        "additional_documents_sha256": {k: base.sha256_text(v) for k, v in task.additional_documents.items()}}
    if lock["task"] != expected_task:
        raise ValueError("repair task differs from the audited task")
    if (lock["evidence_sha256"] != base.sha256_text(evidence.markdown)
            or lock["appendix_sha256"] != base.sha256_text(evidence.appendix_markdown)):
        raise ValueError("repair certificate differs from the audited certificate")
    rows = [row for row in resume.read(core / "manifest.json")["cycles"] if row["cycle"] == cycle]
    if len(rows) != 1:
        raise ValueError("saved cycle is missing or ambiguous")
    row = rows[0]
    proof_path = core / f"02_rewrite/cycle_{cycle:02d}/terminal_proof.md"
    raw_path = proof_path.with_name("raw_with_marker.md")
    audit_path = core / f"04_audit/cycle_{cycle:02d}/audit.md"
    proof, raw, audit_text = (p.read_text().strip() for p in (proof_path, raw_path, audit_path))
    if validation.materialize_and_lint(raw, evidence, contract) != proof:
        raise ValueError("saved draft assembly changed")
    audit = tool_purpose.parse_proof_audit(audit_text,
        require_gap_closure=bool(lock["gap_closure_explanation_required"]))
    if audit != row["audit"] or audit["passed"] is not False or not audit["issues"]:
        raise ValueError("repair requires this draft's own rejecting audit")
    paths = [core / "protocol_lock.json", core / "manifest.json", proof_path, raw_path, audit_path]
    for label, text in (("rewrite", raw), ("audit", audit_text)):
        call = row[label + "_call"]
        metadata = call["metadata"]
        stage = "modular_exact_evidence_whole_proof_" + label
        certificate.validate_markdown_budget_forcing(call, expected_stage=stage,
            expected_model=metadata["model"], canonical_markdown=text,
            expected_timeout_sec=call["request_timeout_sec"])
        if label == "audit":
            directory = Path(metadata["user_prompt_path"]).parent
            prompt_path = directory / (stage + ".pre_budget_forcing.user_prompt.txt")
            prompt = prompt_path.read_text().strip()
            if base.sha256_text(prompt) != metadata["user_prompt_sha256"]:
                raise ValueError("saved audit input prompt changed")
            boundary = "# Submitted Replacement Proof\n\n"
            if prompt.count(boundary) != 1 or prompt.split(boundary, 1)[1].strip() != proof:
                raise ValueError("saved audit was not of this draft")
            paths.append(prompt_path)
    record = {"source": str(source), "cycle": cycle,
        "policy": "saved_draft_and_its_own_rejecting_model_audit",
        "new_formalization_calls": 0, "new_algebra_calls": 0,
        "source_artifacts": {str(p): base.sha256_file(p) for p in paths}}
    return proof, audit, record
