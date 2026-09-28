from __future__ import annotations

import hashlib
import json
import re
import traceback
from pathlib import Path
from typing import Any, Callable, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    pipeline as base,
    protocol,
)

from . import HARNESS_VERSION
from .contracts import EvidenceBundle, SynthesisAdapter
from . import prompts, validation, tool_purpose


ModelCall = Callable[..., tuple[str, Any, dict[str, Any]]]
SAFE_DOCUMENT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_sha(value: Any) -> str:
    serialized = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return _sha(serialized)


def _artifact_records(bundle: EvidenceBundle) -> dict[str, Any]:
    return {
        label: {
            "path": str(path.resolve()),
            "sha256": base.sha256_file(path),
        }
        for label, path in sorted(bundle.source_artifacts.items())
    }


def validate_adapter(adapter: SynthesisAdapter) -> dict[str, Any]:
    """Run the adapter's deterministic evidence checks without model inference."""

    evidence = validation.validate_evidence(adapter.evidence_provider.materialize())
    tool_purpose.purpose_records(adapter.task, evidence)
    contract_record = adapter.contract.lock_record()
    return {
        "schema": "v0287-modular-adapter-validation-v1",
        "validated": True,
        "adapter_id": adapter.adapter_id,
        "problem_id": adapter.task.problem_id,
        "provider_id": evidence.provider_id,
        "verdict": evidence.verdict,
        "evidence_sha256": _sha(evidence.markdown),
        "appendix_sha256": _sha(evidence.appendix_markdown) if evidence.appendix_markdown else None,
        "appendix_in_rewriter_prompt": evidence.appendix_in_rewriter_prompt,
        "verification_sha256": _canonical_sha(evidence.verification),
        "contract_sha256": _canonical_sha(contract_record),
        "source_artifacts": _artifact_records(evidence),
    }


def _write_inputs(output_dir: Path, adapter: SynthesisAdapter) -> None:
    base.write_text(output_dir / "input/original_theorem.md", adapter.task.theorem)
    base.write_text(output_dir / "input/source_proof.md", adapter.task.source_proof)
    for name, value in sorted(adapter.task.additional_documents.items()):
        if SAFE_DOCUMENT_NAME.fullmatch(name) is None or Path(name).name != name:
            raise ValueError(f"unsafe additional input document name: {name!r}")
        base.write_text(output_dir / "input/additional" / name, value)


def _validate_input_document_names(adapter: SynthesisAdapter) -> None:
    for name in adapter.task.additional_documents:
        if SAFE_DOCUMENT_NAME.fullmatch(name) is None or Path(name).name != name:
            raise ValueError(f"unsafe additional input document name: {name!r}")


def run(
    *,
    adapter: SynthesisAdapter,
    output_dir: Path,
    gemma: base.Role,
    qwen: base.Role,
    master_seed: int,
    model_call: ModelCall = base._model_call,  # noqa: SLF001
    initial_proof: str | None = None,
    initial_audit: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute the frozen first-Qwen-PASS exact-evidence synthesis protocol."""

    output_dir = output_dir.resolve()
    _validate_input_document_names(adapter)
    evidence = validation.validate_evidence(adapter.evidence_provider.materialize())
    if (initial_proof is None) != (initial_audit is None):
        raise ValueError("repair resume requires both the saved proof and its audit")
    if initial_proof is not None:
        if initial_audit.get("passed") is not False or not initial_audit.get("issues"):
            raise ValueError("repair resume requires a rejecting audit with issues")
        raw_initial = initial_proof
        if evidence.appendix_markdown:
            if not raw_initial.endswith(evidence.appendix_markdown):
                raise ValueError("repair input does not end in the immutable appendix")
            raw_initial = raw_initial[:-len(evidence.appendix_markdown)].rstrip()
        raw_initial = raw_initial.replace(evidence.markdown, adapter.contract.evidence_marker)
        if validation.materialize_and_lint(raw_initial, evidence, adapter.contract) != initial_proof:
            raise ValueError("repair input is not a valid assembled proof for this evidence")
    purpose = tool_purpose.purpose_records(adapter.task, evidence)
    rewrite_system = prompts.rewriter_system(adapter.contract)
    audit_system = prompts.auditor_system(adapter.contract, task=adapter.task)
    contract_record = adapter.contract.lock_record()
    source_artifacts = _artifact_records(evidence)
    task_lock = {
        "problem_id": adapter.task.problem_id,
        "theorem_sha256": _sha(adapter.task.theorem),
        "source_proof_sha256": _sha(adapter.task.source_proof),
        "additional_documents_sha256": {
            name: _sha(value)
            for name, value in sorted(adapter.task.additional_documents.items())
        },
    }
    protocol_lock = {
        "schema": "v0287-modular-exact-proof-protocol-lock-v1",
        "operator_interventions": 0,
        "manual_candidate_selection": False,
        "decision_authority": "qwen_proof_audit_pass_only",
        "selection_policy": "first_passing_cycle",
        "failure_policy": (
            f"fail_closed_after_{adapter.contract.max_cycles}_automatic_cycles"
        ),
        "proof_candidate_policy": "one_model_candidate_per_cycle",
        "proof_rewriter_model": gemma.model,
        "proof_auditor_model": qwen.model,
        "audit_context_policy": "untrusted_original_source_and_current_replacement",
        "audit_repair_policy": "qwen_restoration_feedback_then_model_rewrite_and_reaudit",
        "tool_purpose_supplied": purpose is not None,
        "gap_closure_explanation_required": purpose is not None,
        "explicit_update_source_policy": tool_purpose.EXPLICIT_SOURCE_POLICY if purpose is not None else "not_available",
        "connection_derivation_order": "update_block_then_derive_surrounding_connections",
        "current_draft_repair_policy": prompts.repair_targeting.VERSION,
        "repair_targeting_code_sha256": base.sha256_file(Path(prompts.repair_targeting.__file__).resolve()),
        "initial_repair_proof_sha256": _sha(initial_proof) if initial_proof is not None else None,
        "initial_repair_audit_sha256": _canonical_sha(initial_audit) if initial_audit is not None else None,
        "token_caps": list(base.TOKEN_CAPS),
        "budget_forcing": "mandatory_for_gemma_and_qwen",
        "adapter_id": adapter.adapter_id,
        "task": task_lock,
        "provider_id": evidence.provider_id,
        "evidence_verdict": evidence.verdict,
        "evidence_sha256": _sha(evidence.markdown),
        "appendix_sha256": _sha(evidence.appendix_markdown) if evidence.appendix_markdown else None,
        "appendix_in_rewriter_prompt": evidence.appendix_in_rewriter_prompt,
        "verification_sha256": _canonical_sha(evidence.verification),
        "contract_sha256": _canonical_sha(contract_record),
        "rewriter_system_sha256": _sha(rewrite_system),
        "auditor_system_sha256": _sha(audit_system),
        "core_prompts_sha256": base.sha256_file(Path(prompts.__file__).resolve()),
        "tool_purpose_policy_sha256": base.sha256_file(Path(tool_purpose.__file__).resolve()),
        "core_validation_sha256": base.sha256_file(
            Path(validation.__file__).resolve()
        ),
    }
    preflight = {
        "schema": "v0287-modular-exact-evidence-proof-synthesis-v1",
        "harness_version": HARNESS_VERSION,
        "state": "running",
        "adapter_id": adapter.adapter_id,
        "problem_id": adapter.task.problem_id,
        "source_proof_sha256": task_lock["source_proof_sha256"],
        "codex_model_calls": 0,
        "gemma_model": gemma.model,
        "proof_rewriter_model": gemma.model,
        "proof_auditor_model": qwen.model,
        "qwen_model": qwen.model,
        "stage_order": [
            "evidence_provider_materialization",
            "model_whole_proof_rewrite",
            "deterministic_contract_lint",
            "qwen_whole_proof_audit",
        ],
        "protocol_lock": protocol_lock,
    }

    output_dir.mkdir(parents=True, exist_ok=False)
    base.write_json(output_dir / "manifest.json", preflight)
    base.write_json(output_dir / "protocol_lock.json", protocol_lock)
    base.write_json(output_dir / "contract.json", contract_record)
    _write_inputs(output_dir, adapter)
    if initial_proof is not None:
        base.write_text(output_dir / "input/repair_initial_proof.md", initial_proof)
        base.write_json(output_dir / "input/repair_initial_audit.json", dict(initial_audit))
    base.write_text(output_dir / "01_evidence/evidence.md", evidence.markdown)
    if evidence.appendix_markdown:
        base.write_text(output_dir / "01_evidence/appendix.md", evidence.appendix_markdown)
    base.write_json(output_dir / "01_evidence/verification.json", evidence.verification)
    base.write_json(output_dir / "01_evidence/tool_record.json", evidence.tool_record)
    base.write_json(output_dir / "01_evidence/source_artifacts.json", source_artifacts)

    current_proof: str | None = initial_proof
    raw_rewrite = ""
    prior_audit: Mapping[str, Any] | None = initial_audit
    audit: Mapping[str, Any] | None = None
    selected_cycle: int | None = None
    cycle_records: list[dict[str, Any]] = []
    try:
        for cycle in range(1, adapter.contract.max_cycles + 1):
            _, targeting = prompts.repair_context(current_proof, evidence, adapter.contract, prior_audit)
            base.write_json(output_dir / f"02_rewrite/cycle_{cycle:02d}/repair_targeting.json", targeting)
            raw_rewrite, current_proof, rewrite_call = model_call(
                role=gemma,
                system_prompt=rewrite_system,
                user_prompt=prompts.rewrite_prompt(
                    task=adapter.task,
                    evidence=evidence,
                    contract=adapter.contract,
                    previous_proof=current_proof,
                    prior_audit=prior_audit,
                ),
                destination=output_dir / f"02_rewrite/cycle_{cycle:02d}/model",
                stage="modular_exact_evidence_whole_proof_rewrite",
                master_seed=master_seed + 100 + cycle,
                parser=lambda text: validation.materialize_and_lint(
                    text, evidence, adapter.contract
                ),
            )
            lint = validation.lint_report(
                raw_rewrite, evidence, adapter.contract
            )
            base.write_text(
                output_dir / f"02_rewrite/cycle_{cycle:02d}/raw_with_marker.md",
                raw_rewrite,
            )
            base.write_text(
                output_dir / f"02_rewrite/cycle_{cycle:02d}/terminal_proof.md",
                current_proof,
            )
            base.write_json(
                output_dir / f"03_lint/cycle_{cycle:02d}/lint.json", lint
            )

            audit_text, audit, audit_call = model_call(
                role=qwen,
                system_prompt=audit_system,
                user_prompt=prompts.audit_prompt(
                    task=adapter.task, evidence=evidence, proof=current_proof
                ),
                destination=output_dir / f"04_audit/cycle_{cycle:02d}/model",
                stage="modular_exact_evidence_whole_proof_audit",
                master_seed=master_seed + 200 + cycle,
                parser=lambda text: tool_purpose.parse_proof_audit(text, require_gap_closure=purpose is not None),
            )
            base.write_text(
                output_dir / f"04_audit/cycle_{cycle:02d}/audit.md", audit_text
            )
            cycle_records.append(
                {
                    "cycle": cycle,
                    "rewrite_call": rewrite_call,
                    "lint": lint,
                    "audit": dict(audit),
                    "audit_call": audit_call,
                    "passed": bool(audit["passed"]),
                }
            )
            if audit["passed"]:
                selected_cycle = cycle
                break
            prior_audit = audit

        if selected_cycle is None or current_proof is None or audit is None:
            raise RuntimeError("no proof passed the locked Qwen decision rule")

        terminal_path = output_dir / "terminal_proof.md"
        base.write_text(terminal_path, current_proof)
        result = {
            **preflight,
            "state": "completed",
            "operator_interventions": 0,
            "selected_cycle": selected_cycle,
            "selection_reason": "first_cycle_with_qwen_proof_audit_pass",
            "proof_audit_passed": True,
            "terminal_proof": str(terminal_path),
            "terminal_proof_sha256": base.sha256_text(current_proof),
            "cycles": cycle_records,
        }
        base.write_json(output_dir / "result.json", result)
        base.write_json(output_dir / "manifest.json", result)
        return result
    except Exception as error:
        failure = {
            **preflight,
            "state": "failed_closed",
            "operator_interventions": 0,
            "cycles": cycle_records,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        base.write_json(output_dir / "failure.json", failure)
        base.write_json(output_dir / "manifest.json", failure)
        raise
