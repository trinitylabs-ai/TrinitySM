from __future__ import annotations

import json
from pathlib import Path

import pytest

from cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905 import pipeline
from cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905.consolidate import (
    build_consolidation,
)


ORIGINAL_VALIDATED = """ORIGINAL_PROOF_VALID
fusion_assessment: VALIDATED
validation_basis: The submitted proof is complete and the accepting audit agrees.
END_ORIGINAL_PROOF_VALID"""

ORIGINAL_REJECTED = """ORIGINAL_PROOF_VALID
fusion_assessment: REJECTED
validation_basis: The submitted proof is complete and the alleged defect is absent.
END_ORIGINAL_PROOF_VALID"""

ACCEPTING_FUSION = """FUSION_ACCEPT_AS_WRITTEN
verdict: ACCEPT_AS_WRITTEN
reviewer_1_assessment: NO_DEFECT_REPORTED | No defect was found.
reviewer_2_assessment: NO_DEFECT_REPORTED | No defect was found.
reviewer_3_assessment: NO_DEFECT_REPORTED | No defect was found.
independent_acceptance_basis: Every load-bearing implication was checked.
literal_completeness_check: The submitted proof needs no completion.
END_FUSION_ACCEPT_AS_WRITTEN"""


def repetition_error(*, finish_reason: str = "repetition") -> RuntimeError:
    attempts = [
        {
            "attempt": attempt,
            "stage": f"resolve_{attempt}",
            "finish_reason": finish_reason,
            "empty": True,
            "accepted": False,
            "error": "empty final content",
            "repetition_detection_preserved": True,
        }
        for attempt in range(3)
    ]
    return RuntimeError(f"v0.3.79 text recovery exhausted: {attempts}")


def test_original_v0261_shape_fails_without_accepting_fusion_context() -> None:
    parsed = pipeline.parse_resolution_compat(ORIGINAL_VALIDATED)
    assert parsed["valid"] is False
    assert parsed["errors"] == [pipeline.EXPECTED_ORIGINAL_VALID_ERROR]


def test_original_v0261_shape_is_accepted_with_accepting_fusion_context() -> None:
    with pipeline.resolver_fusion_context("ACCEPT_AS_WRITTEN"):
        parsed = pipeline.parse_resolution_compat(ORIGINAL_VALIDATED)
    assert parsed["valid"] is True
    assert parsed["errors"] == []
    assert parsed["protocol_compatibility"]["source_recovery"] == "v0261"
    assert parsed["final"] == ORIGINAL_VALIDATED


def test_original_v0261_shape_fails_with_nonaccepting_fusion_context() -> None:
    with pipeline.resolver_fusion_context("REPAIR_NEEDED"):
        parsed = pipeline.parse_resolution_compat(ORIGINAL_VALIDATED)
    assert parsed["valid"] is False


def test_already_valid_original_record_is_unchanged() -> None:
    with pipeline.resolver_fusion_context("ACCEPT_AS_WRITTEN"):
        parsed = pipeline.parse_resolution_compat(ORIGINAL_REJECTED)
    assert parsed["valid"] is True
    assert "protocol_compatibility" not in parsed


def test_paired_fusion_outcome_is_identity_checked() -> None:
    task = {
        "fusion_outcome": "ACCEPT_AS_WRITTEN",
        "fusion_record": ACCEPTING_FUSION,
    }
    assert pipeline._paired_fusion_outcome(task) == "ACCEPT_AS_WRITTEN"
    task["fusion_outcome"] = "REPAIR_NEEDED"
    with pytest.raises(ValueError, match="identity-matched Fusion outcome"):
        pipeline._paired_fusion_outcome(task)


def test_repetition_exhaustion_classifier_is_fail_closed() -> None:
    attempts = pipeline._repetition_exhaustion_attempts(repetition_error())
    assert attempts is not None and len(attempts) == 3
    assert pipeline._repetition_exhaustion_attempts(repetition_error(finish_reason="length")) is None
    assert pipeline._repetition_exhaustion_attempts(RuntimeError("transport failed")) is None
    assert pipeline._repetition_exhaustion_attempts(ValueError(str(repetition_error()))) is None


def test_third_resolver_repetition_gets_one_fresh_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[Path, str]] = []

    def fake_run_case(**kwargs: object) -> dict[str, object]:
        output_dir = Path(kwargs["output_dir"])
        seed_namespace = str(kwargs["seed_namespace"])
        calls.append((output_dir, seed_namespace))
        if len(calls) == 1:
            raise repetition_error()
        output_dir.mkdir(parents=True, exist_ok=True)
        result = {
            "schema": "test-result",
            "state": "completed",
            "case_id": "imo2026_p3.t07_r01",
            "resolved_proof_path": str((output_dir / "resolved_proof.md").resolve()),
            "resolved_proof_sha256": "abc",
        }
        (output_dir / "resolved_proof.md").write_text("proof\n", encoding="utf-8")
        (output_dir / "result.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        return result

    monkeypatch.setattr(pipeline, "_ORIGINAL_THIRD_RESOLVE_CASE", fake_run_case)
    primary = tmp_path / "case" / "third_ungrouped_resolve"
    result = pipeline.run_third_resolve_case(
        case={"case_id": "imo2026_p3.t07_r01"},
        endpoint="http://127.0.0.1:8030/v1",
        output_dir=primary,
        seed_namespace="v0263:p3:third",
    )
    assert result["state"] == "completed"
    assert calls[0] == (primary, "v0263:p3:third")
    retry = primary.parent / pipeline.THIRD_RESOLVE_RETRY_DIRECTORY
    assert calls[1] == (retry, "v0263:p3:third:v0263:fresh_retry1")
    manifest = json.loads(
        (retry / "v0263_repetition_recovery.json").read_text(encoding="utf-8")
    )
    assert manifest["failed_trace_continued"] is False
    assert manifest["failed_attempt_count"] == 3
    assert manifest["budget_forcing_continuation_min_tokens"] == 32_768

    # A resumed call uses the hash-checked retry result without another model call.
    resumed = pipeline.run_third_resolve_case(
        case={"case_id": "imo2026_p3.t07_r01"},
        endpoint="http://127.0.0.1:8030/v1",
        output_dir=primary,
        seed_namespace="v0263:p3:third",
    )
    assert resumed == result
    assert len(calls) == 2


def test_third_resolver_nonrepetition_failure_is_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def fake_run_case(**kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        raise RuntimeError("transport failed")

    monkeypatch.setattr(pipeline, "_ORIGINAL_THIRD_RESOLVE_CASE", fake_run_case)
    with pytest.raises(RuntimeError, match="transport failed"):
        pipeline.run_third_resolve_case(
            case={"case_id": "imo2026_p3.t07_r01"},
            endpoint="http://127.0.0.1:8030/v1",
            output_dir=tmp_path / "case" / "third_ungrouped_resolve",
            seed_namespace="v0263:p3:third",
        )
    assert calls == 1


def test_policy_manifest_is_immutable(tmp_path: Path) -> None:
    pipeline._write_policy_manifest(tmp_path)
    path = tmp_path / "v0263_unified_recovery_policy.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["parent_harness_version"] == "0.3.260"
    assert value["v0261_protocol_compatibility"]["model_text_modified"] is False
    assert value["v0262_repetition_recovery"]["scope"] == "third resolver only"
    pipeline._write_policy_manifest(tmp_path)
    value["v0262_repetition_recovery"]["retry_count"] = 2
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="policy manifest drift"):
        pipeline._write_policy_manifest(tmp_path)


def test_parent_modules_use_v0263_patches() -> None:
    assert pipeline.resolver.parse_resolution is pipeline.parse_resolution_compat
    assert pipeline.resolver.run_task is pipeline.run_resolver_task_compat
    assert pipeline.v105.resolve_cases is pipeline.resolve_cases_v263


def test_completed_v0261_v0262_artifacts_form_one_v0263_record() -> None:
    repo = Path(__file__).resolve().parent.parent
    run_root = repo / "runs/v0257_v108_six_problem_bf_temp_transition_20260904"
    value = build_consolidation(run_root)
    assert value["state"] == "completed"
    assert value["scope"] == ["imo2026_p3", "imo2026_p5"]
    assert len(value["recoveries"]["p3_v0262"]["final_proofs"]) == 4
    assert len(value["recoveries"]["p5_v0261"]["final_proofs"]) == 4
    assert value["proof_artifacts_modified"] is False
    assert value["model_calls_performed_by_consolidation"] == 0

