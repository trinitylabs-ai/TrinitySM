"""Prepare a final model revision without changing any mathematical content."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import validation
from . import rewrite

POLICY = "checked_appendix_final_qwen_revision_v1"
CURRENT_DRAFT_DOCUMENT = "current_main_proof_to_revise.md"
INSTRUCTION = (
    "User-requested revision of the current main proof below. Treat it as your working draft, "
    "not as a certified argument. The original source proof above remains comparison context. "
    "Write one complete standalone replacement, preserving valid necessary calculations and explicitly "
    "deriving every connection between the theorem, the fixed lemma hypotheses and guards, and the conclusion. "
    "Do not merely rephrase assertions of equivalence. No prior audit or grading feedback is supplied. "
    "Keep the immutable insertion marker exactly once. The unchanged appendix is attached automatically; "
    "do not reproduce or reconstruct its body."
)


def prepare(*, task, evidence, contract, synthesis):
    """Remove only the exact frozen appendix/block; require a lossless round trip."""
    if CURRENT_DRAFT_DOCUMENT in task.additional_documents:
        raise ValueError("reserved final-revision document already exists")
    if synthesis.get("state") != "completed" or synthesis.get("proof_audit_passed") is not True:
        raise ValueError("final revision requires an accepted initial rewrite")
    if not evidence.appendix_markdown or evidence.appendix_in_rewriter_prompt:
        raise ValueError("final revision requires a checked attach-only appendix")
    path = Path(synthesis["terminal_proof"])
    proof = path.read_text().strip()
    digest = rewrite.pipeline.base.sha256_text(proof)
    if digest != synthesis["terminal_proof_sha256"]:
        raise ValueError("initial rewrite proof hash mismatch")
    suffix = "\n\n" + evidence.appendix_markdown
    if not proof.endswith(suffix) or proof.count(evidence.appendix_markdown) != 1:
        raise ValueError("initial rewrite lacks the unique unchanged appendix suffix")
    main = proof[:-len(suffix)]
    if main.count(evidence.markdown) != 1 or contract.evidence_marker in main:
        raise ValueError("initial rewrite lacks a unique immutable lemma")
    raw = main.replace(evidence.markdown, contract.evidence_marker, 1)
    if validation.materialize_and_lint(raw, evidence, contract) != proof:
        raise ValueError("final revision main-proof extraction is not lossless")
    document = INSTRUCTION + "\n\n" + raw
    revised_task = replace(task, additional_documents={
        **task.additional_documents, CURRENT_DRAFT_DOCUMENT: document})
    return revised_task, {
        "policy": POLICY, "state": "prepared", "max_revision_cycles": 1,
        "input_proof": str(path), "input_proof_sha256": digest,
        "current_main_proof_sha256": rewrite.pipeline.base.sha256_text(raw),
        "current_main_proof_characters": len(raw),
        "revision_document_sha256": rewrite.pipeline.base.sha256_text(document),
        "appendix_sha256": rewrite.pipeline.base.sha256_text(evidence.appendix_markdown),
        "appendix_in_rewriter_prompt": False, "supply_prior_grading": False,
        "supply_prior_proof_audit": False, "new_formalization_calls": 0,
        "new_singular_calls": 0,
    }
