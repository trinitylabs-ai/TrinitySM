from __future__ import annotations

import copy
import json
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
)
from cognitive_well_harness_v0_3_81_iterative_dual_memory_loop_20260825 import (
    pipeline as v081,
)
from cognitive_well_harness_v0_3_82_contextual_surgical_memory_20260826 import (
    pipeline as v082,
)
from cognitive_well_harness_v0_3_83_batched_dependency_dag_20260826 import (
    batching as v083_batch,
)
from cognitive_well_harness_v0_3_83_batched_dependency_dag_20260826 import (
    pipeline as v083,
)

from . import HARNESS_VERSION
from .enhanced_audit import run_enhanced_review_fusion_dag


load_initial_state = v082.load_initial_state


def _skipped_dynamic_literal_audit(**_: Any) -> dict[str, Any]:
    """Non-authoritative replacement for the fragile quote-binding gate."""
    return {
        "audit_status": "SKIPPED_NON_AUTHORITATIVE",
        "eligible_for_defect_routing": False,
        "literal_pass": True,
        "anchors": [],
        "anchor_extraction_errors": [],
        "literal_audit": {
            "verdict": "SKIPPED_NON_AUTHORITATIVE",
            "failed_obligation": "",
        },
    }


def run_contextual_repairs_step8_disabled(**kwargs: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run Step 9 with every dynamic-literal call removed from its control path."""
    reuse_root_value = kwargs.pop("reuse_candidate_results_from", None)
    reuse_root = Path(reuse_root_value) if reuse_root_value is not None else None
    original = v082.run_dynamic_literal_audit
    original_repair = v082.run_contextual_repair_candidate

    def repair_with_checkpoint(**repair_kwargs: Any) -> dict[str, Any]:
        candidate_id = str(repair_kwargs["candidate"]["candidate_id"])
        result_path = reuse_root / candidate_id / "result.json" if reuse_root else None
        if result_path is not None and result_path.is_file():
            cached = json.loads(result_path.read_text(encoding="utf-8"))
            if not isinstance(cached, dict):
                raise ValueError(f"cached contextual result is not an object: {result_path}")
            if str(cached.get("candidate_id") or "") != candidate_id:
                raise ValueError(f"cached candidate binding mismatch: {result_path}")
            status_value = str(cached.get("contextual_repair_status") or "")
            if status_value == "AUDIT_UNAVAILABLE":
                raise ValueError(
                    f"refusing to reuse literal-gate-dependent result: {result_path}"
                )
            result = copy.deepcopy(cached)
            result["contextual_repair_reused_from"] = str(result_path.resolve())
            return result
        return original_repair(**repair_kwargs)

    v082.run_dynamic_literal_audit = _skipped_dynamic_literal_audit
    v082.run_contextual_repair_candidate = repair_with_checkpoint
    try:
        return v082.run_contextual_repairs_without_commit(**kwargs)
    finally:
        v082.run_dynamic_literal_audit = original
        v082.run_contextual_repair_candidate = original_repair


def status(output_dir: Path, stage: str) -> None:
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": stage, "iteration": 1, "updated_at": utc_now()},
    )


def build_manifest(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    manifest = v083.build_manifest(
        initial_state=initial_state,
        source_run_dir=source_run_dir,
        runtime_config=runtime_config,
        salvage_verifier_endpoint=salvage_verifier_endpoint,
    )
    manifest.update(
        {
            "schema": "cognitive-well-v0107-enhanced-reviews-step9-terminal-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "iteration_count": 1,
            "stopping_boundary": "after_step_9_before_step_10",
            "step_5_reviewer_1_enhancement": "0.3.89",
            "step_5_reviewer_3_enhancement": "0.3.92",
            "step_7_reviewer_1_enhancement": "0.3.89",
            "step_7_reviewer_3_enhancement": "0.3.92",
            "step_8_dynamic_literal_audit": "disabled_non_authoritative",
            "step_9_input": "trace_enhanced_step_7_candidates",
            "step_10_memory_transaction": False,
            "step_11_selection": False,
            "second_iteration": False,
            "problem_specific_prompting": False,
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
    candidate_proofs = list(initial_state["candidate_proofs"])
    context_certified: list[dict[str, Any]] = []
    provisional: list[dict[str, Any]] = []
    failed_memory: list[dict[str, Any]] = []
    iteration_dir = output_dir / "iteration_1"
    try:
        status(output_dir, "01_hypothesis_extraction_batch")
        extracted = v082.run_extraction(
            runtime=runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            context_certified_memory=context_certified,
            provisional_memory=provisional,
            failed_memory=failed_memory,
            iteration=1,
            output_dir=iteration_dir / "01_hypothesis_extraction",
        )

        status(output_dir, "02_novelty_vote_batch")
        accepted, novelty_audit = v083_batch.novelty_gate_batched(
            runtime=runtime,
            extraction_results=extracted,
            certified_memory=v082.combined_memory(context_certified, provisional),
            failed_memory=failed_memory,
            iteration=1,
            output_dir=iteration_dir / "02_novelty_gate",
        )

        status(output_dir, "03_certification_waves")
        preliminary, failed_memory, certification = (
            v083_batch.run_certification_and_memory_batched(
                proof_runtime=runtime,
                verifier_runtime=verifier_runtime,
                runtime_config=runtime_config,
                salvage_verifier_endpoint=salvage_verifier_endpoint,
                problem=problem,
                candidate_proofs=candidate_proofs,
                accepted_hypotheses=accepted,
                certified_memory=v082.combined_memory(context_certified, provisional),
                failed_memory=failed_memory,
                iteration=1,
                output_dir=iteration_dir / "03_preliminary_certification",
            )
        )
        context_certified, provisional = v082.partition_preliminary_memory(
            previous_context_certified=context_certified,
            preliminary_rows=preliminary,
        )

        status(output_dir, "04_six_candidate_synthesis_batch")
        synthesized = v082.run_synthesis(
            runtime=runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            context_certified_memory=context_certified,
            provisional_memory=provisional,
            iteration=1,
            output_dir=iteration_dir / "04_synthesis",
        )

        status(output_dir, "05_trace_enhanced_full_proof_audit")
        pre_audited = run_enhanced_review_fusion_dag(
            run_input=run_input,
            candidates=synthesized,
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            output_dir=iteration_dir / "05_pre_refinement_audit",
            seed_namespace="v0107:step5",
        )

        status(output_dir, "06_refinement_batch")
        refined = v081.run_refinement(
            runtime=runtime,
            problem=problem,
            audited_candidates=pre_audited,
            iteration=1,
            output_dir=iteration_dir / "06_refinement",
        )
        refined = v082.rebind_memory_dependencies(
            candidates=refined,
            context_certified=context_certified,
            provisional=provisional,
        )

        status(output_dir, "07_trace_enhanced_fresh_full_proof_audit")
        post_audited = run_enhanced_review_fusion_dag(
            run_input=run_input,
            candidates=refined,
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            output_dir=iteration_dir / "07_post_refinement_audit",
            seed_namespace="v0107:step7",
        )

        # Dynamic literal-anchor extraction is deliberately outside the control
        # path.  Quote binding is a fragile transport heuristic: a binding
        # failure does not establish a mathematical defect and must not affect
        # contextual repair.  Step 9 consumes the trace-enhanced whole-proof
        # audits from Step 7 directly.
        write_json(
            iteration_dir / "08_dynamic_literal_audit" / "SKIPPED.json",
            {
                "status": "SKIPPED_NON_AUTHORITATIVE",
                "reason": "fragile_quote_binding_transport",
                "input_candidate_count": len(post_audited),
                "affects_step_9_routing": False,
            },
        )

        status(output_dir, "09_contextual_repair_from_step_7_stop_before_memory_transaction")
        final_candidates, contextual_feedback = run_contextual_repairs_step8_disabled(
            runtime=runtime,
            problem_id=problem_id,
            problem=problem,
            candidates=post_audited,
            context_certified=context_certified,
            provisional=provisional,
            failed_memory=failed_memory,
            iteration=1,
            output_dir=iteration_dir / "09_contextual_memory_feedback",
        )

        summary = {
            "schema": "cognitive-well-v0107-enhanced-reviews-step9-terminal-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "stopping_boundary": "after_step_9_before_step_10",
            "extracted_hypothesis_count": sum(
                len(row["record"]["hypotheses"]) for row in extracted
            ),
            "novelty_accepted_count": len(accepted),
            "novelty_rejected_count": len(novelty_audit) - len(accepted),
            "certification": certification,
            "context_certified_memory_count_before_step_10": len(context_certified),
            "provisional_memory_count_before_step_10": len(provisional),
            "failed_memory_count_before_step_10": len(failed_memory),
            "step_5_fusion_outcomes": dict(
                Counter(str(row["fusion_outcome"]) for row in pre_audited)
            ),
            "step_7_fusion_outcomes": dict(
                Counter(str(row["fusion_outcome"]) for row in post_audited)
            ),
            "step_8_literal_outcomes": {"SKIPPED_NON_AUTHORITATIVE": len(post_audited)},
            "step_9_contextual_feedback": contextual_feedback,
            "final_candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "contextual_repair_status": row.get("contextual_repair_status"),
                }
                for row in final_candidates
            ],
            "step_10_memory_transaction_performed": False,
            "step_11_selection_performed": False,
            "second_iteration_performed": False,
            "proof_runtime_recovery_events": runtime.recovery_events(),
            "verifier_runtime_recovery_events": verifier_runtime.recovery_events(),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "memory_snapshot_before_step_10.json",
            {
                "context_certified": context_certified,
                "provisional": provisional,
                "failed": failed_memory,
            },
        )
        write_json(
            output_dir / "status.json",
            {
                "state": "completed",
                "stage": "stopped_after_step_9_before_step_10",
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
