from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824 import (
    run as v063_terminal,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.split_verifier import (
    make_gemma_verifier_runtime,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.contracts import (
    ARMS,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.memory import (
    extend_shared_verified_exact,
    merge_shared_verified_exact,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.shared_leaf import (
    _extract_and_prove_arm,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.synthesis import (
    generate_statement_only_samples,
    generate_v072_arm_samples,
)

from . import HARNESS_VERSION
from .retry import read_json, run_atomic_retry
from .runtime import ResilientModelRuntime, recovery_profile
from .salvage import EXPERIMENT_MASTER_SEED, run_failure_guided_salvage


FRESH_EXTRACTION_SCHEDULE: tuple[dict[str, Any], ...] = (
    {"round": 2, "temperature": 0.4},
    {"round": 3, "temperature": 0.8},
)
MAX_FAILURE_SALVAGE_CASES = 4


def _status(output_dir: Path, stage: str, **values: Any) -> None:
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": stage, **values, "updated_at": utc_now()},
    )


def _manifest(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v079-full-leaf-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": run_input["problem_id"],
        "input_path": str(input_path.resolve()),
        "pipeline": [
            "fresh_original_and_diagnostic_extraction_t04_t08",
            "paired_proving_and_gemma_split_certification",
            "initial_exact_only_shared_memory",
            "v078_first_failure_salvage_and_atomic_certification",
            "first_salvage_exact_only_memory_insertion",
            "v079_failed_decomposed_child_singleton_retry",
            "retry_paired_proving_and_gemma_split_certification",
            "retry_exact_only_memory_insertion",
            "twelve_v072_synthesis_candidates",
            "four_v063_statement_only_synthesis_candidates",
        ],
        "extraction_schedule": list(FRESH_EXTRACTION_SCHEDULE),
        "first_failure_salvage": {
            "maximum_parent_cases": MAX_FAILURE_SALVAGE_CASES,
            "generation_temperature": 0.4,
            "maximum_children_per_parent": 3,
        },
        "atomic_child_retry": {
            "eligibility": (
                "failed_child_of_DECOMPOSE_parent_with_more_than_one_child"
            ),
            "maximum_retries_per_child": 1,
            "generation_prompt": "unchanged_v078_failure_salvage_prompt",
            "model_decisions_observed": ["REPAIR", "DECOMPOSE", "ABANDON"],
            "admitted_decision": "REPAIR",
            "admitted_hypothesis_count": 1,
            "decompose_policy": "observe_and_reject_without_proving",
            "abandon_policy": "reject_without_proving",
            "recursive_retry": False,
        },
        "proof_and_verification": {
            "model": runtime_config.gemma_model,
            "proof_temperature": 0.6,
            "proof_repair_temperature": 0.2,
            "split_verifier_temperature": 0.1,
            "alignment_calls": 2,
            "alignment_rule": "unanimous",
            "validity_calls": 1,
            "salvage_verifier_endpoint": salvage_verifier_endpoint.rstrip("/"),
        },
        "memory": {
            "dedup": "exact_only",
            "semantic_dedup": False,
            "semantic_dedup_model_calls": 0,
            "location_fields_retained": True,
        },
        "synthesis": {
            "v072_candidate_count": 12,
            "v072_routes": ["original", "diagnostic"],
            "v072_modes": ["evidence", "anchored", "location"],
            "v072_temperatures": [0.2, 0.4],
            "statement_only_candidate_count": 4,
            "statement_only_temperatures": {"0.2": 2, "0.4": 2},
            "final_split_verifier_gate": "skipped",
        },
        "runtime": {
            "gemma_model": runtime_config.gemma_model,
            "gemma_endpoint": runtime_config.gemma_endpoint,
            "qwen_model": runtime_config.qwen_model,
            "qwen_endpoint": runtime_config.qwen_endpoint,
            "master_seed": runtime_config.master_seed,
        },
        "reference_solution_access": False,
        "gold_score_access": False,
    }


def run_full_leaf(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    if runtime_config.gemma_model != v063_terminal.base.GEMMA_MODEL:
        raise ValueError("v0.3.79 full leaf requires the frozen Gemma4-31B model")
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        _manifest(
            run_input=run_input,
            input_path=input_path,
            runtime_config=runtime_config,
            salvage_verifier_endpoint=salvage_verifier_endpoint,
        ),
    )
    runtime = ResilientModelRuntime(runtime_config)
    verifier_runtime = make_gemma_verifier_runtime(runtime_config)
    salvage_proof_runtime = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.qwen_model,
            master_seed=EXPERIMENT_MASTER_SEED,
        )
    )
    salvage_verifier_runtime = make_gemma_verifier_runtime(
        RuntimeConfig(
            gemma_endpoint=salvage_verifier_endpoint.rstrip("/"),
            qwen_endpoint=salvage_verifier_endpoint.rstrip("/"),
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.gemma_model,
            master_seed=EXPERIMENT_MASTER_SEED,
        )
    )
    problem = str(run_input["problem"])
    candidate_proofs = list(run_input["candidate_proofs"])
    anchor_proof = str(
        next(row["proof"] for row in candidate_proofs if row["role"] == "anchor")
    )
    try:
        arm_results = [
            _extract_and_prove_arm(
                arm=arm,
                runtime=runtime,
                verifier_runtime=verifier_runtime,
                problem=problem,
                candidate_proofs=candidate_proofs,
                output_dir=output_dir,
                extraction_schedule=FRESH_EXTRACTION_SCHEDULE,
            )
            for arm in ARMS
        ]

        _status(output_dir, "initial_exact_memory_insertion")
        initial_verified, initial_audit = merge_shared_verified_exact(
            arm_results=arm_results,
            output_dir=output_dir / "initial_exact_dedup",
        )
        initial_unresolved = [
            {**row, "source_arm": arm_result["arm"]}
            for arm_result in arm_results
            for row in arm_result["unresolved"]
        ]
        write_json(
            output_dir / "initial_shared_lemma_memory.json",
            {
                "schema": "cognitive-well-v079-initial-shared-memory-v1",
                "verified": initial_verified,
                "unresolved": initial_unresolved,
                "dedup_policy": "exact_only",
            },
        )

        failure_cards = [
            card
            for arm_result in arm_results
            for card in arm_result["failure_cards"]
        ]
        _status(
            output_dir,
            "first_failure_salvage",
            eligible_failure_count=len(failure_cards),
        )
        salvage = run_failure_guided_salvage(
            runtime=salvage_proof_runtime,
            verifier_runtime=salvage_verifier_runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            failure_cards=failure_cards,
            output_dir=output_dir / "failure_guided_salvage",
            limit=MAX_FAILURE_SALVAGE_CASES,
        )
        first_shared, first_salvage_audit = extend_shared_verified_exact(
            existing_verified=initial_verified,
            salvage_verified=salvage["verified"],
            output_dir=output_dir / "salvage_exact_dedup",
        )
        first_unresolved = initial_unresolved + [
            {**row, "source_arm": "failure_salvage"}
            for row in salvage["unresolved"]
        ]
        write_json(
            output_dir / "shared_lemma_memory.json",
            {
                "schema": "cognitive-well-v079-pre-retry-shared-memory-v1",
                "verified": first_shared,
                "unresolved": first_unresolved,
                "dedup_policy": "exact_only",
                "semantic_dedup_model_calls": 0,
            },
        )

        _status(output_dir, "singleton_atomic_child_retry")
        retry = run_atomic_retry(
            source_run_dir=output_dir,
            input_path=input_path,
            output_dir=output_dir / "atomic_child_retry",
            runtime_config=runtime_config,
            salvage_verifier_endpoint=salvage_verifier_endpoint,
        )
        final_memory = read_json(
            output_dir / "atomic_child_retry" / "augmented_shared_lemma_memory.json"
        )
        shared_verified = list(final_memory["verified"])
        write_json(
            output_dir / "final_shared_lemma_memory.json",
            {
                **final_memory,
                "schema": "cognitive-well-v079-final-shared-memory-v1",
            },
        )

        candidates: list[dict[str, Any]] = []
        shared_labels: list[dict[str, str]] = []
        statement_only_candidates: list[dict[str, Any]] = []
        if shared_verified:
            for arm_result in arm_results:
                arm = str(arm_result["arm"])
                _status(
                    output_dir,
                    f"{arm}_v072_synthesis",
                    shared_verified_lemma_count=len(shared_verified),
                )
                labels, arm_candidates = generate_v072_arm_samples(
                    runtime=runtime,
                    arm=arm,
                    problem=problem,
                    verified=shared_verified,
                    anchor_proof=anchor_proof,
                    synthesis_instructions=str(run_input["synthesis_instructions"]),
                    gate_policy=run_input["gate"],
                    output_dir=output_dir / "arms" / arm / "synthesis",
                )
                if not shared_labels:
                    shared_labels = labels
                elif labels != shared_labels:
                    raise RuntimeError("shared labels changed between synthesis arms")
                arm_result["candidates"] = arm_candidates
                candidates.extend(arm_candidates)

            _status(output_dir, "statement_only_synthesis")
            terminal_labels, statement_only_candidates = generate_statement_only_samples(
                runtime=runtime,
                problem=problem,
                verified=shared_verified,
                gate_policy=run_input["gate"],
                output_dir=output_dir / "statement_only_terminal_synthesis",
            )
            if [row["statement"] for row in terminal_labels] != [
                row["statement"] for row in shared_labels
            ]:
                raise RuntimeError("statement-only lemma labels changed")
            candidates.extend(statement_only_candidates)
        else:
            for arm_result in arm_results:
                arm_result["candidates"] = []

        candidate_summaries = [
            {
                key: candidate[key]
                for key in (
                    "candidate_id",
                    "arm",
                    "family",
                    "temperature",
                    "replicate",
                    "proof_sha256",
                    "assembly",
                )
            }
            for candidate in candidates
        ]
        write_json(
            output_dir / "recovery_events.json",
            {
                "profile": recovery_profile(),
                "generation_runtime": runtime.recovery_events(),
                "gemma_verifier_runtime": verifier_runtime.recovery_events(),
                "salvage_proof_runtime": salvage_proof_runtime.recovery_events(),
                "salvage_verifier_runtime": salvage_verifier_runtime.recovery_events(),
            },
        )
        summary = {
            "schema": "cognitive-well-v079-full-leaf-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "problem_id": run_input["problem_id"],
            "fresh_extraction_rounds_per_arm": len(FRESH_EXTRACTION_SCHEDULE),
            "initial_shared_lemma_count": len(initial_verified),
            "first_failure_salvage": {
                "eligible_count": len(failure_cards),
                "selected_count": salvage["selected_failure_count"],
                "generated_hypothesis_count": salvage["generated_hypothesis_count"],
                "verified_count": len(salvage["verified"]),
                "unresolved_count": len(salvage["unresolved"]),
            },
            "atomic_child_retry": {
                "eligible_count": retry["eligible_count"],
                "singleton_accepted_count": retry["singleton_accepted_count"],
                "singleton_rejected_count": retry["singleton_rejected_count"],
                "verified_count": retry["verified_count"],
                "unresolved_count": retry["unresolved_count"],
                "further_retry_allowed": False,
            },
            "final_shared_lemma_count": len(shared_verified),
            "dedup_policy": "exact_only",
            "initial_exact_dedup_audit_count": len(initial_audit),
            "first_salvage_exact_dedup_audit_count": len(first_salvage_audit),
            "v072_synthesis_candidate_count": sum(
                len(row["candidates"]) for row in arm_results
            ),
            "statement_only_synthesis_candidate_count": len(
                statement_only_candidates
            ),
            "synthesis_candidate_count": len(candidates),
            "synthesis_candidates": candidate_summaries,
            "final_split_verifier_gate_run": False,
            "numeric_scoring": False,
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {
                "state": "completed",
                "stage": "synthesis_complete",
                "final_shared_lemma_count": len(shared_verified),
                "synthesis_candidate_count": len(candidates),
                "updated_at": utc_now(),
            },
        )
        return summary
    except Exception as error:
        write_json(
            output_dir / "status.json",
            {
                "state": "failed",
                "stage": "exception",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise
