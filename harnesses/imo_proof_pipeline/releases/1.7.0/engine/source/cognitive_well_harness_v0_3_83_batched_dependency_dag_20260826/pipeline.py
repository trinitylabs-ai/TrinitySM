from __future__ import annotations

import traceback
from collections import Counter
from pathlib import Path
from typing import Any

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
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
    recovery_profile,
)
from cognitive_well_harness_v0_3_81_iterative_dual_memory_loop_20260825 import (
    pipeline as v081,
)
from cognitive_well_harness_v0_3_82_contextual_surgical_memory_20260826 import (
    pipeline as v082,
)

from . import HARNESS_VERSION
from .batching import (
    attach_dynamic_literal_audits_resilient,
    batching_matrix,
    novelty_gate_batched,
    run_certification_and_memory_batched,
    run_contextual_memory_feedback_batched,
    run_review_fusion_dag,
)


ITERATION_COUNT = v082.ITERATION_COUNT
EXTRACTION_SCHEDULE = v082.EXTRACTION_SCHEDULE
SYNTHESIS_CONFIGS = v082.SYNTHESIS_CONFIGS
load_initial_state = v082.load_initial_state


def _status(output_dir: Path, stage: str, **values: Any) -> None:
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": stage, **values, "updated_at": utc_now()},
    )


def build_manifest(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    manifest = v082.build_manifest(
        initial_state=initial_state,
        source_run_dir=source_run_dir,
        runtime_config=runtime_config,
        salvage_verifier_endpoint=salvage_verifier_endpoint,
    )
    manifest.update(
        {
            "schema": "cognitive-well-v083-batched-dependency-dag-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "execution_policy": batching_matrix(),
            "cross_gpu_schedule": {
                "gpu_0": "Gemma4-31B BF16 MTP4",
                "gpu_1": "Qwen3.6-27B BF16",
                "review_dag": (
                    "R1/Gemma and R2/Qwen launch together; R3/Gemma starts "
                    "when R1 releases GPU0; Fusion is a Gemma batch after all reviews"
                ),
            },
            "nominal_architecture_changes_only": True,
            "nominal_prompt_changes_from_v082": (
                "Step 8 anchor extraction is capped at six, prioritizes "
                "proof-critical dependency transitions, and emits only exact_quote, "
                "local_claim, required_support, and downstream_dependency"
            ),
            "dynamic_literal_anchor_cap": 6,
            "dynamic_literal_anchor_minimum_bound": 4,
            "conditional_anchor_contract_retry": (
                "one generic exact-substring retry after deterministic binding failure"
            ),
            "anchor_transport_binding": (
                "exact or unique formatting-equivalent match; canonical matches are "
                "replaced by verbatim proof spans before Qwen literal audit"
            ),
            "step8_guided_decoding": "vLLM structured_outputs.json",
            "model_temperature_changes_from_v082": False,
        }
    )
    return manifest


def run_pipeline(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        build_manifest(
            initial_state=initial_state,
            source_run_dir=source_run_dir,
            runtime_config=runtime_config,
            salvage_verifier_endpoint=salvage_verifier_endpoint,
        ),
    )
    write_json(output_dir / "initial_state.json", initial_state)
    runtime = ResilientModelRuntime(runtime_config)
    verifier_runtime = make_gemma_verifier_runtime(
        RuntimeConfig(
            gemma_endpoint=salvage_verifier_endpoint.rstrip("/"),
            qwen_endpoint=salvage_verifier_endpoint.rstrip("/"),
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.gemma_model,
            master_seed=runtime_config.master_seed,
        )
    )
    problem_id = str(initial_state["problem_id"])
    problem = str(initial_state["problem"])
    run_input = {"problem_id": problem_id, "problem": problem}
    current_proofs = list(initial_state["candidate_proofs"])
    context_certified: list[dict[str, Any]] = []
    provisional: list[dict[str, Any]] = []
    failed_memory: list[dict[str, Any]] = []
    iteration_summaries: list[dict[str, Any]] = []
    try:
        for iteration in range(1, ITERATION_COUNT + 1):
            iteration_dir = output_dir / f"iteration_{iteration}"
            _status(output_dir, "01_hypothesis_extraction_batch", iteration=iteration)
            extracted = v082.run_extraction(
                runtime=runtime,
                problem=problem,
                candidate_proofs=current_proofs,
                context_certified_memory=context_certified,
                provisional_memory=provisional,
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "01_hypothesis_extraction",
            )

            _status(output_dir, "02_novelty_vote_batch", iteration=iteration)
            accepted, novelty_audit = novelty_gate_batched(
                runtime=runtime,
                extraction_results=extracted,
                certified_memory=v082.combined_memory(
                    context_certified, provisional
                ),
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "02_novelty_gate",
            )

            _status(output_dir, "03_certification_waves", iteration=iteration)
            preliminary, failed_memory, certification = (
                run_certification_and_memory_batched(
                    proof_runtime=runtime,
                    verifier_runtime=verifier_runtime,
                    runtime_config=runtime_config,
                    salvage_verifier_endpoint=salvage_verifier_endpoint,
                    problem=problem,
                    candidate_proofs=current_proofs,
                    accepted_hypotheses=accepted,
                    certified_memory=v082.combined_memory(
                        context_certified, provisional
                    ),
                    failed_memory=failed_memory,
                    iteration=iteration,
                    output_dir=iteration_dir / "03_preliminary_certification",
                )
            )
            context_certified, provisional = v082.partition_preliminary_memory(
                previous_context_certified=context_certified,
                preliminary_rows=preliminary,
            )

            _status(output_dir, "04_six_candidate_synthesis_batch", iteration=iteration)
            synthesized = v082.run_synthesis(
                runtime=runtime,
                problem=problem,
                candidate_proofs=current_proofs,
                context_certified_memory=context_certified,
                provisional_memory=provisional,
                iteration=iteration,
                output_dir=iteration_dir / "04_synthesis",
            )

            _status(output_dir, "05_first_review_dependency_dag", iteration=iteration)
            pre_audited = run_review_fusion_dag(
                run_input=run_input,
                candidates=synthesized,
                gemma_endpoint=runtime_config.gemma_endpoint,
                qwen_endpoint=runtime_config.qwen_endpoint,
                output_dir=iteration_dir / "05_pre_refinement_audit",
            )

            _status(output_dir, "06_refinement_batch", iteration=iteration)
            refined = v081.run_refinement(
                runtime=runtime,
                problem=problem,
                audited_candidates=pre_audited,
                iteration=iteration,
                output_dir=iteration_dir / "06_refinement",
            )
            refined = v082.rebind_memory_dependencies(
                candidates=refined,
                context_certified=context_certified,
                provisional=provisional,
            )

            _status(output_dir, "07_fresh_review_dependency_dag", iteration=iteration)
            post_audited = run_review_fusion_dag(
                run_input=run_input,
                candidates=refined,
                gemma_endpoint=runtime_config.gemma_endpoint,
                qwen_endpoint=runtime_config.qwen_endpoint,
                output_dir=iteration_dir / "07_post_refinement_audit",
            )

            _status(output_dir, "08_dynamic_literal_candidate_pipelines", iteration=iteration)
            literal_audited = attach_dynamic_literal_audits_resilient(
                runtime=runtime,
                problem=problem,
                candidates=post_audited,
                output_dir=iteration_dir / "08_dynamic_literal_audit",
            )

            _status(output_dir, "09_contextual_repair_batches", iteration=iteration)
            (
                context_certified,
                provisional,
                failed_memory,
                final_candidates,
                contextual_feedback,
            ) = run_contextual_memory_feedback_batched(
                runtime=runtime,
                problem_id=problem_id,
                problem=problem,
                candidates=literal_audited,
                context_certified=context_certified,
                provisional=provisional,
                failed_memory=failed_memory,
                iteration=iteration,
                output_dir=iteration_dir / "09_contextual_memory_feedback",
            )

            _status(output_dir, "11_track_audit_batch_and_selection", iteration=iteration)
            current_proofs, selection = v081.run_selection(
                runtime=runtime,
                problem=problem,
                post_audited_candidates=final_candidates,
                output_dir=iteration_dir / "11_selection",
            )
            iteration_summary = {
                "iteration": iteration,
                "extracted_hypothesis_count": sum(
                    len(row["record"]["hypotheses"]) for row in extracted
                ),
                "novelty_accepted_count": len(accepted),
                "novelty_rejected_count": len(novelty_audit) - len(accepted),
                "certification": certification,
                "context_certified_memory_count": len(context_certified),
                "provisional_memory_count": len(provisional),
                "failed_memory_count": len(failed_memory),
                "pre_fusion_outcomes": dict(
                    Counter(str(row["fusion_outcome"]) for row in pre_audited)
                ),
                "post_fusion_outcomes": dict(
                    Counter(str(row["fusion_outcome"]) for row in post_audited)
                ),
                "dynamic_literal_outcomes": dict(
                    Counter(
                        str(row["dynamic_literal_audit"]["literal_audit"]["verdict"])
                        for row in literal_audited
                    )
                ),
                "contextual_feedback": contextual_feedback,
                "selection": selection,
            }
            write_json(iteration_dir / "summary.json", iteration_summary)
            write_json(
                iteration_dir / "memory_snapshot.json",
                {
                    "context_certified": context_certified,
                    "provisional": provisional,
                    "failed": failed_memory,
                },
            )
            iteration_summaries.append(iteration_summary)

        summary = {
            "schema": "cognitive-well-v083-batched-dependency-dag-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "iteration_count": ITERATION_COUNT,
            "context_certified_memory_count": len(context_certified),
            "provisional_memory_count": len(provisional),
            "failed_memory_count": len(failed_memory),
            "final_selected_proofs": [
                {
                    "candidate_id": row["candidate_id"],
                    "role": row["role"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "qwen_outcome": row["qwen_outcome"],
                    "fusion_outcome": row["fusion_outcome"],
                    "contextual_repair_status": row.get(
                        "contextual_repair_status"
                    ),
                }
                for row in current_proofs
            ],
            "execution_policy": batching_matrix(),
            "iterations": iteration_summaries,
            "proof_runtime_recovery_events": runtime.recovery_events(),
            "verifier_runtime_recovery_events": verifier_runtime.recovery_events(),
        }
        write_json(
            output_dir / "final_context_certified_memory.json",
            {"context_certified": context_certified},
        )
        write_json(
            output_dir / "final_provisional_memory.json",
            {"provisional": provisional},
        )
        write_json(output_dir / "final_failed_memory.json", {"failed": failed_memory})
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {
                "state": "completed",
                "stage": "two_iteration_batched_dependency_loop_complete",
                "context_certified_memory_count": len(context_certified),
                "provisional_memory_count": len(provisional),
                "failed_memory_count": len(failed_memory),
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


__all__ = [
    "EXTRACTION_SCHEDULE",
    "SYNTHESIS_CONFIGS",
    "build_manifest",
    "load_initial_state",
    "run_pipeline",
]
