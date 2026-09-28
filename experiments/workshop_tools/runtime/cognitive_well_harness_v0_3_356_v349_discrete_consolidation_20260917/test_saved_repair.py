from dataclasses import replace

import pytest

from . import saved_repair as saved, certificate
from .test_appendix import fixture
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import pipeline, validation, tool_purpose


@pytest.fixture
def checkpoint(tmp_path):
    evidence, contract, task = fixture(tmp_path)
    source = tmp_path / "source"
    core = source / "02_synthesis"
    raw = "Apply the following lemma.\n" + contract.evidence_marker + "\nThus the theorem holds."
    proof = validation.materialize_and_lint(raw, evidence, contract)
    audit_text = "# Decision\n\nFAIL\n\n# Checks\n\n" + "\n".join(
        f"- {label}: {'FAIL' if index == 0 else 'PASS'}" for index, label in enumerate(pipeline.protocol.PROOF_AUDIT_CHECKS))
    audit_text += '\n\n# Issues\n\n- Derive the inputs of the lemma.'
    audit = tool_purpose.parse_proof_audit(audit_text, require_gap_closure=False)
    lock = {"task": {"problem_id": task.problem_id, "theorem_sha256": saved.base.sha256_text(task.theorem),
        "source_proof_sha256": saved.base.sha256_text(task.source_proof), "additional_documents_sha256": {}},
        "evidence_sha256": saved.base.sha256_text(evidence.markdown),
        "appendix_sha256": saved.base.sha256_text(evidence.appendix_markdown),
        "gap_closure_explanation_required": False}
    row = {"cycle": 1, "audit": audit}
    for label, text in (("rewrite", raw), ("audit", audit_text)):
        stage = "modular_exact_evidence_whole_proof_" + label
        prompt = "# Submitted Replacement Proof\n\n" + proof
        prompt_path = core / (stage + ".pre_budget_forcing.user_prompt.txt")
        saved.base.write_text(prompt_path, prompt)
        forcing = {"schema": certificate.EXPECTED_BUDGET_FORCING_SCHEMA,
            "policy": certificate.EXPECTED_BUDGET_FORCING_POLICY, "stage": stage, "model": "fake",
            "structured": False, "canonical_artifacts_are_forced_response": True,
            "forced_text_sha256": saved.base.sha256_text(text), "cue": "Continue.",
            "cue_sha256": saved.base.sha256_text("Continue.")}
        row[label + "_call"] = {"attempt": 1, "cap": saved.base.TOKEN_CAPS[0], "request_timeout_sec": None,
            "metadata": {"model": "fake", "user_prompt_path": str(prompt_path),
                "user_prompt_sha256": saved.base.sha256_text(prompt),
                "v0257_budget_forcing": forcing, "config": {"timeout_seconds": None}}}
    for name, value in (("protocol_lock.json", lock), ("manifest.json", {"cycles": [row]})):
        saved.base.write_json(core / name, value)
    for name, value in (("02_rewrite/cycle_01/terminal_proof.md", proof),
            ("02_rewrite/cycle_01/raw_with_marker.md", raw), ("04_audit/cycle_01/audit.md", audit_text)):
        saved.base.write_text(core / name, value)
    return source, task, evidence, contract, proof, audit


def load(checkpoint):
    source, task, evidence, contract, *_ = checkpoint
    return saved.load(source, 1, task=task, evidence=evidence, contract=contract)


def test_saved_checkpoint_binds_draft_audit_and_provenance(checkpoint):
    proof, audit, record = load(checkpoint)
    assert proof == checkpoint[4] and audit == checkpoint[5]
    assert record["new_algebra_calls"] == record["new_formalization_calls"] == 0


@pytest.mark.parametrize("name", ["02_rewrite/cycle_01/terminal_proof.md",
    "04_audit/cycle_01/audit.md", "modular_exact_evidence_whole_proof_audit.pre_budget_forcing.user_prompt.txt"])
def test_changed_draft_audit_or_audit_input_rejected(checkpoint, name):
    path = checkpoint[0] / "02_synthesis" / name
    saved.base.write_text(path, path.read_text().strip() + "\nChanged content.")
    with pytest.raises(ValueError):
        load(checkpoint)


def test_other_task_or_certificate_rejected(checkpoint):
    source, task, evidence, contract, *_ = checkpoint
    for changed_task, changed_evidence in ((replace(task, theorem="Different theorem"), evidence),
            (task, replace(evidence, markdown="Different lemma"))):
        with pytest.raises(ValueError, match="differs"):
            saved.load(source, 1, task=changed_task, evidence=changed_evidence, contract=contract)


def test_passing_audit_cannot_be_recast_as_repair(checkpoint):
    path = checkpoint[0] / "02_synthesis/manifest.json"
    manifest = saved.resume.read(path)
    manifest["cycles"][0]["audit"]["passed"] = True
    saved.base.write_json(path, manifest)
    with pytest.raises(ValueError, match="rejecting audit"):
        load(checkpoint)


def test_canonical_output_binding_cannot_be_omitted(checkpoint):
    path = checkpoint[0] / "02_synthesis/manifest.json"
    manifest = saved.resume.read(path)
    manifest["cycles"][0]["audit_call"]["metadata"]["v0257_budget_forcing"]["forced_text_sha256"] = "wrong"
    saved.base.write_json(path, manifest)
    with pytest.raises(ValueError, match="canonical forced response"):
        load(checkpoint)
