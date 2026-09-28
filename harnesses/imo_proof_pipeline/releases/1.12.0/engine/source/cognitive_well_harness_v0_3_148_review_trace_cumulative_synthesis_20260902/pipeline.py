from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_140_clean_dual_trace_fusion_20260901 import (
    GEMMA_MODEL,
    QWEN_MODEL,
)
from cognitive_well_harness_v0_3_140_clean_dual_trace_fusion_20260901.pipeline import (
    assert_no_external_material,
    extract_role_trace,
    read_object,
    run_reviews,
    runtime_for,
    sha256_file,
    stable_digest,
    utc_now,
    write_json,
    write_status,
)
from cognitive_well_harness_v0_3_147_cumulative_patch_synthesis_20260901.pipeline import (
    run as run_cumulative_synthesis,
)

from . import HARNESS_VERSION


def _load_inputs(
    *, problem_json: Path, candidate_result: Path
) -> dict[str, Any]:
    problem_path = problem_json.resolve()
    candidate_path = candidate_result.resolve()
    problem_record = read_object(problem_path)
    candidate = read_object(candidate_path)
    problem_id = str(problem_record.get("problem_id") or "").strip()
    problem = str(problem_record.get("claim") or "").strip()
    candidate_id = str(candidate.get("candidate_id") or "").strip()
    proof = str(candidate.get("proof") or "").strip()
    if not all((problem_id, problem, candidate_id, proof)):
        raise ValueError("problem_id, claim, candidate_id, and proof are required")
    assert_no_external_material(problem, label="problem")
    assert_no_external_material(proof, label="candidate proof")
    proof_source_path = Path(str(candidate.get("proof_path") or candidate_path))
    if not proof_source_path.is_absolute():
        proof_source_path = (candidate_path.parent / proof_source_path).resolve()
    return {
        "problem_path": problem_path,
        "candidate_path": candidate_path,
        "problem_id": problem_id,
        "problem": problem,
        "candidate_id": candidate_id,
        "proof": proof,
        "proof_source_path": proof_source_path,
    }


def _source_contract(
    *,
    inputs: dict[str, Any],
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
) -> dict[str, Any]:
    return {
        "problem_json": str(inputs["problem_path"]),
        "problem_json_sha256": sha256_file(inputs["problem_path"]),
        "candidate_result": str(inputs["candidate_path"]),
        "candidate_result_sha256": sha256_file(inputs["candidate_path"]),
        "consumed_problem_fields": ["problem_id", "claim"],
        "consumed_candidate_fields": ["candidate_id", "proof", "proof_path"],
        "gemma_endpoint": gemma_endpoint.rstrip("/"),
        "qwen_endpoint": qwen_endpoint.rstrip("/"),
        "master_seed": master_seed,
        "seed_namespace": seed_namespace,
        "external_information_injection": False,
        "cross_problem_information_injection": False,
        "historical_problem_lookup": False,
    }


def run_review_trace_phase(
    *,
    problem_json: Path,
    candidate_result: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
) -> dict[str, Any]:
    """Run only the validated v0.3.140 review and raw-trace-harvest boundary."""

    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    status_path = destination / "status.json"
    try:
        inputs = _load_inputs(
            problem_json=problem_json, candidate_result=candidate_result
        )
        contract = _source_contract(
            inputs=inputs,
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=seed_namespace,
        )
        input_sha256 = stable_digest(contract)
        summary_path = destination / "summary.json"
        if summary_path.is_file():
            saved = read_object(summary_path)
            if saved.get("input_sha256") != input_sha256:
                raise ValueError(
                    "refusing to reuse review/trace output after input drift"
                )
            if saved.get("state") == "completed":
                return saved

        write_json(
            destination / "manifest.json",
            {
                "schema": "cognitive-well-v0148-review-trace-source-manifest-v1",
                "harness_version": HARNESS_VERSION,
                "created_at": utc_now(),
                "input_sha256": input_sha256,
                "source": contract,
                "models": {
                    "reviewer_1": GEMMA_MODEL,
                    "reviewer_2": QWEN_MODEL,
                    "reviewer_3": GEMMA_MODEL,
                    "trace_extractor": GEMMA_MODEL,
                },
                "policy": {
                    "review_implementation": "frozen_v0.3.140",
                    "reviewer_1_cutoff": (
                        "clean_same-seed_16k_to_24k_to_32k_then_fail_closed"
                    ),
                    "reviewer_2_cutoff": (
                        "clean_same-seed_16k_to_24k_to_32k_then_fail_closed"
                    ),
                    "trace_source": "accepted_transport_attempt_only",
                    "stop_boundary": "raw_source_bound_trace_packets",
                    "obsolete_v0140_trace_selection_skipped": True,
                    "obsolete_v0140_fusion_skipped": True,
                    "obsolete_v0140_synthesis_skipped": True,
                    "independent_external_scoring_in_solver": False,
                },
            },
        )
        write_json(
            destination / "leak_audit.json",
            {
                "state": "passed",
                "solver_inputs_are_current_problem_local": True,
                "accepted_hidden_traces_are_solver_internal": True,
                "gold_supplied": False,
                "codex_grades_supplied": False,
                "external_scorer_feedback_supplied": False,
                "cross_problem_information_supplied": False,
                "historical_problem_material_supplied": False,
                "handcrafted_problem_specific_prompt_guidance": False,
                "unconsumed_candidate_fields_are_not_injected": True,
            },
        )

        write_status(status_path, state="running", stage="fresh_reviews")
        reviews = run_reviews(
            problem_id=inputs["problem_id"],
            candidate_id=inputs["candidate_id"],
            problem=inputs["problem"],
            proof=inputs["proof"],
            problem_path=inputs["problem_path"],
            proof_path=inputs["proof_source_path"],
            output_dir=destination / "01_reviews",
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=seed_namespace,
        )
        write_json(destination / "01_reviews" / "summary.json", reviews)

        runtime = runtime_for(
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
        )
        raw_packets: dict[str, list[dict[str, Any]]] = {}
        for role_key in ("reviewer_1", "reviewer_2", "reviewer_3"):
            write_status(
                status_path,
                state="running",
                stage=f"{role_key}_accepted_trace_extraction",
            )
            raw_packets[role_key] = extract_role_trace(
                runtime=runtime,
                role_key=role_key,
                problem=inputs["problem"],
                proof=inputs["proof"],
                visible=reviews["visible"][role_key],
                trace_path=Path(reviews["reasoning_paths"][role_key]),
                output_dir=(
                    destination / "02_trace_harvest" / role_key / "extraction"
                ),
                seed_label=(
                    f"{seed_namespace}:{inputs['problem_id']}:"
                    f"{inputs['candidate_id']}:{role_key}:extract"
                ),
            )

        summary = {
            "schema": "cognitive-well-v0148-review-trace-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": "REVIEWS_AND_RAW_TRACES_READY",
            "completed_at": utc_now(),
            "input_sha256": input_sha256,
            "problem_id": inputs["problem_id"],
            "candidate_id": inputs["candidate_id"],
            "review_outcomes": {
                role: reviews["results"][role].get("parsed", {}).get("outcome")
                or reviews["results"][role].get("outcome")
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "raw_trace_packet_counts": {
                role: len(raw_packets[role]) for role in raw_packets
            },
            "downstream_selection_performed": False,
            "downstream_fusion_performed": False,
            "downstream_synthesis_performed": False,
        }
        write_json(summary_path, summary)
        write_status(
            status_path,
            state="completed",
            stage="raw_trace_harvest",
            raw_trace_packet_counts=summary["raw_trace_packet_counts"],
        )
        return summary
    except Exception as error:
        write_status(
            status_path,
            state="failed_closed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise


def _completed_cumulative_phase(
    *, phase_dir: Path, source_run: Path
) -> dict[str, Any] | None:
    summary_path = phase_dir / "summary.json"
    manifest_path = phase_dir / "manifest.json"
    if not summary_path.is_file() or not manifest_path.is_file():
        return None
    summary = read_object(summary_path)
    manifest = read_object(manifest_path)
    if summary.get("state") != "completed":
        return None
    if Path(str(manifest.get("source_run") or "")).resolve() != source_run.resolve():
        raise ValueError("completed cumulative phase points to a different source run")
    if manifest.get("source_manifest_sha256") != sha256_file(
        source_run / "manifest.json"
    ):
        raise ValueError("completed cumulative phase source manifest drift")
    return summary


def run_pipeline(
    *,
    problem_json: Path,
    candidate_result: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    status_path = destination / "status.json"
    try:
        inputs = _load_inputs(
            problem_json=problem_json, candidate_result=candidate_result
        )
        contract = _source_contract(
            inputs=inputs,
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=seed_namespace,
        )
        input_sha256 = stable_digest(contract)
        summary_path = destination / "summary.json"
        if summary_path.is_file():
            saved = read_object(summary_path)
            if saved.get("input_sha256") != input_sha256:
                raise ValueError("refusing to reuse composite output after input drift")
            if saved.get("state") in {"completed", "dry_run_completed"}:
                return saved

        write_json(
            destination / "manifest.json",
            {
                "schema": "cognitive-well-v0148-composite-manifest-v1",
                "harness_version": HARNESS_VERSION,
                "created_at": utc_now(),
                "input_sha256": input_sha256,
                "source": contract,
                "phases": [
                    {
                        "phase": "review_and_raw_trace_harvest",
                        "implementation": "v0.3.140_review_logic_only",
                        "output_dir": "01_review_trace_phase",
                    },
                    {
                        "phase": "visible_fusion_trace_selection_cumulative_synthesis",
                        "implementation": "v0.3.147",
                        "output_dir": "02_cumulative_synthesis_phase",
                    },
                ],
                "policy": {
                    "visible_fusion_is_trace_blind": True,
                    "tracing_memory_is_unverified": True,
                    "later_synthesis_calls_receive_no_fusion": True,
                    "maximum_trace_packets_per_later_call": 4,
                    "cumulative_deterministic_local_patch_splicing": True,
                    "preserved_prefix_suffix_byte_audit": True,
                    "promotion_allowed_without_independent_audit": False,
                },
            },
        )
        write_json(
            destination / "leak_audit.json",
            {
                "state": "passed",
                "problem_blindness": "current_problem_only",
                "solver_internal_material_only": True,
                "gold_supplied": False,
                "codex_grades_supplied": False,
                "external_scorer_feedback_supplied": False,
                "cross_problem_information_supplied": False,
                "historical_problem_material_supplied": False,
                "problem_specific_prompt_or_patch_supplied": False,
                "phase_2_source_is_exact_phase_1_artifact": True,
            },
        )

        if dry_run:
            summary = {
                "schema": "cognitive-well-v0148-composite-summary-v1",
                "harness_version": HARNESS_VERSION,
                "state": "dry_run_completed",
                "input_sha256": input_sha256,
                "problem_id": inputs["problem_id"],
                "candidate_id": inputs["candidate_id"],
                "validated_phases": 2,
            }
            write_json(summary_path, summary)
            write_status(
                status_path,
                state="dry_run_completed",
                stage="source_contract_and_leak_validation",
            )
            return summary

        review_trace_dir = destination / "01_review_trace_phase"
        synthesis_dir = destination / "02_cumulative_synthesis_phase"
        phase_seed_namespace = f"{seed_namespace}:v0148-review-trace"
        write_status(
            status_path, state="running", stage="review_and_raw_trace_harvest"
        )
        phase_1 = run_review_trace_phase(
            problem_json=problem_json,
            candidate_result=candidate_result,
            output_dir=review_trace_dir,
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=phase_seed_namespace,
        )
        if phase_1.get("state") != "completed":
            raise RuntimeError("review/trace phase did not complete")

        write_status(
            status_path,
            state="running",
            stage="visible_fusion_trace_selection_cumulative_synthesis",
        )
        phase_2 = _completed_cumulative_phase(
            phase_dir=synthesis_dir, source_run=review_trace_dir
        )
        if phase_2 is None:
            phase_2 = run_cumulative_synthesis(
                source_run=review_trace_dir, output_dir=synthesis_dir
            )
        if phase_2.get("state") != "completed":
            raise RuntimeError("cumulative synthesis phase did not complete")

        phase_2_result = read_object(synthesis_dir / "07_result.json")
        result = {
            "schema": "cognitive-well-v0148-terminal-proof-v1",
            "harness_version": HARNESS_VERSION,
            "problem_id": inputs["problem_id"],
            "candidate_id": inputs["candidate_id"],
            "proof": phase_2_result["proof"],
            "proof_path": phase_2_result["proof_path"],
            "proof_sha256": phase_2_result["proof_sha256"],
            "review_trace_phase": str(review_trace_dir),
            "cumulative_synthesis_phase": str(synthesis_dir),
            "fusion_verdict": phase_2_result["fusion_verdict"],
            "tracing_memory_packet_count": phase_2_result[
                "tracing_memory_packet_count"
            ],
            "synthesis_iteration_count": phase_2_result[
                "synthesis_iteration_count"
            ],
            "packet_batches": phase_2_result["packet_batches"],
            "promotion_allowed_without_independent_audit": False,
        }
        write_json(destination / "03_result.json", result)
        summary = {
            "schema": "cognitive-well-v0148-composite-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": "CUMULATIVE_PROOF_SYNTHESIZED",
            "completed_at": utc_now(),
            "input_sha256": input_sha256,
            "problem_id": inputs["problem_id"],
            "candidate_id": inputs["candidate_id"],
            "phase_1_outcome": phase_1["outcome"],
            "phase_2_outcome": phase_2["outcome"],
            "raw_trace_packet_counts": phase_1["raw_trace_packet_counts"],
            "selected_tracing_memory_packet_count": phase_2[
                "selected_tracing_memory_packet_count"
            ],
            "synthesis_iteration_count": phase_2["synthesis_iteration_count"],
            "packet_batches": phase_2["packet_batches"],
            "proof_path": result["proof_path"],
            "proof_sha256": result["proof_sha256"],
            "promotion_allowed_without_independent_audit": False,
        }
        write_json(summary_path, summary)
        write_status(
            status_path,
            state="completed",
            stage="cumulative_proof_synthesis",
            proof_path=result["proof_path"],
            proof_sha256=result["proof_sha256"],
            promotion_allowed_without_independent_audit=False,
        )
        return summary
    except Exception as error:
        write_status(
            status_path,
            state="failed_closed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise


__all__ = ["run_pipeline", "run_review_trace_phase"]
