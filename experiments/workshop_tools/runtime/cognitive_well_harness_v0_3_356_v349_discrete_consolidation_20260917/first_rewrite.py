"""Reusable bounded first-rewrite profile for already verified same-case evidence.

Input: an adapter holding the original theorem/proof, recorded tool purpose,
verified evidence provider, and model-authored semantic contract.
Output: the submitted rewritten proof, Qwen audit, and verification provenance.
Independent scoring stays outside this module and never conditions synthesis.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import prompts, tool_purpose, validation
from . import pipeline


PROFILE_ID = "generic_explicit_first_rewrite_v1"


def prepare(adapter):
    """Freeze the single-cycle contract without altering any mathematical input."""
    evidence = validation.validate_evidence(adapter.evidence_provider.materialize())
    if not tool_purpose.has_tool_purpose(adapter.task):
        raise ValueError("explicit first rewrite requires recorded detector and matcher")
    tool_purpose.purpose_records(adapter.task, evidence)
    prepared = replace(adapter, contract=replace(adapter.contract, max_cycles=1))
    user = prompts.rewrite_prompt(task=prepared.task, evidence=evidence,
        contract=prepared.contract, previous_proof=None, prior_audit=None)
    system = prompts.rewriter_system(prepared.contract)
    record = {
        "profile": PROFILE_ID, "max_rewrite_cycles": 1, "maximum_model_stages": 2,
        "original_proof_sha256": pipeline.base.sha256_text(prepared.task.source_proof),
        "theorem_sha256": pipeline.base.sha256_text(prepared.task.theorem),
        "evidence_sha256": pipeline.base.sha256_text(evidence.markdown),
        "contract_sha256": pipeline.synthesis_pipeline._canonical_sha(prepared.contract.lock_record()),
        "first_rewrite_user_prompt_sha256": pipeline.base.sha256_text(user),
        "first_rewrite_system_prompt_sha256": pipeline.base.sha256_text(system),
        "rewrite_prompt_characters": len(user) + len(system),
        "prior_rewrites_supplied": False, "prior_audits_or_grades_supplied": False,
        "source_location_policy": "unique_verbatim_detector_quote_no_new_gap_selection",
        "connection_policy": "update_explicit_block_then_derive_incoming_and_outgoing_connections",
        "audit_policy": "original_proof_then_tool_purpose_then_replacement_last_with_gap_closure",
        "new_formalization_calls": 0, "new_singular_calls": 0,
        "new_certificate_author_calls": 0, "json_model_output": False,
    }
    return prepared, record


def run(*, adapter, output_dir, master_seed, prior_model_stages=0,
        gemma=None, qwen=None, model_call=None):
    """Run one first Gemma rewrite and one Qwen audit; never retry a rejection."""
    from .rewrite import BudgetedCalls, assert_generic_boundary, write_record
    assert_generic_boundary()
    if (isinstance(prior_model_stages, bool) or not isinstance(prior_model_stages, int)
            or not 0 <= prior_model_stages <= 22):
        raise ValueError("first rewrite and audit must fit within the 24-stage case budget")
    prepared, record = prepare(adapter)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    gemma = gemma or pipeline.base.Role("http://127.0.0.1:8030/v1", pipeline.base.DEFAULT_GEMMA_MODEL, 0.2, "max")
    qwen = qwen or pipeline.base.Role("http://127.0.0.1:8027/v1", pipeline.base.DEFAULT_QWEN_MODEL, 0.1, None)
    record.update(state="running", problem_id=prepared.task.problem_id, prior_model_stages=prior_model_stages,
        master_seed=master_seed, gemma_temperature=gemma.temperature, qwen_temperature=qwen.temperature)
    write_record(output_dir / "profile.json", record)
    write_record(output_dir / "status.json", {**record, "stage": "first_gemma_rewrite"})
    caller = model_call or BudgetedCalls(output_dir / "model_budget.json", max_stages=2)
    def call(**kwargs):
        stage = "qwen_whole_proof_audit" if kwargs["stage"].endswith("_audit") else "first_gemma_rewrite"
        write_record(output_dir / "status.json", {**record, "stage": stage})
        return caller(**kwargs)
    root = output_dir / "02_synthesis"
    try:
        try:
            result = pipeline.synthesis_pipeline.run(adapter=prepared, output_dir=root,
                gemma=gemma, qwen=qwen, master_seed=master_seed, model_call=call)
        except RuntimeError as error:
            failure = root / "failure.json"
            if str(error) != "no proof passed the locked Qwen decision rule" or not failure.is_file():
                raise
            import json
            result = json.loads(failure.read_text(encoding="utf-8"))
        forcing = pipeline._verify_synthesis_budget_forcing(synthesis_root=root,
            synthesis=result, gemma=gemma, qwen=qwen)
        submitted = root / "02_rewrite/cycle_01/terminal_proof.md"
        record.update(state=result["state"], stage="finished", synthesis_result=result,
            synthesis_budget_forcing=forcing, submitted_proof=str(submitted),
            submitted_proof_sha256=pipeline.base.sha256_text(submitted.read_text(encoding="utf-8").strip()),
            proof_audit_passed=result["cycles"][0]["audit"]["passed"])
        if result["state"] == "completed":
            record.update(terminal_proof=result["terminal_proof"], terminal_proof_sha256=result["terminal_proof_sha256"])
    except Exception as error:
        record.update(state="failed_closed", error=f"{type(error).__name__}: {error}")
    write_record(output_dir / "status.json", record)
    write_record(output_dir / "result.json", record)
    return record
