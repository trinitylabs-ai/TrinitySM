from __future__ import annotations

import hashlib
import json
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    load_run_input as load_leaf_input,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_66_modular_six_to_two_proof_selection_20260824.contracts import (
    load_run_input as load_v066_input,
)
from cognitive_well_harness_v0_3_67_modular_six_track_generation_review_resolution_20260824 import (
    pipeline as v067,
)
from cognitive_well_harness_v0_3_70_modular_post_v067_compact_json_cleanup_20260824.recovery import (
    run_recovered_v066,
)

from . import HARNESS_VERSION
from .full_leaf import FRESH_EXTRACTION_SCHEDULE, run_full_leaf


def child_paths(output_dir: Path) -> dict[str, Path]:
    v067_dir = output_dir / "tree" / "01_v067_six_track_generation"
    v066_dir = v067_dir / "children" / "02_v066_compact_recovery_selection"
    leaf_dir = v066_dir / "children" / "03_v079_singleton_atomic_retry_leaf"
    return {"v067": v067_dir, "v066": v066_dir, "leaf": leaf_dir}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_completed(path: Path, stage: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{stage} did not emit {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("state") != "completed":
        raise RuntimeError(f"{stage} did not complete: {path}")
    return value


def _status(
    output_dir: Path,
    *,
    state: str,
    active_node: str,
    completed_nodes: list[str],
    **values: Any,
) -> None:
    write_json(
        output_dir / "status.json",
        {
            "state": state,
            "active_node": active_node,
            "completed_nodes": completed_nodes,
            **values,
            "updated_at": utc_now(),
        },
    )


def planned_tree(output_dir: Path) -> dict[str, Any]:
    paths = child_paths(output_dir)
    return {
        "root": "v079_problem_only",
        "nodes": [
            {
                "id": "v067",
                "path": str(paths["v067"].resolve()),
                "role": "fresh_six_track_generation_review_fusion_resolution",
            },
            {
                "id": "v066_recovered",
                "path": str(paths["v066"].resolve()),
                "role": "six_to_two_anchor_supplement_selection",
            },
            {
                "id": "v079_leaf",
                "path": str(paths["leaf"].resolve()),
                "role": "fresh_lemma_memory_salvage_retry_and_synthesis",
            },
        ],
        "edges": [
            {"from": "problem", "to": "v067", "artifact": "problem_statement"},
            {"from": "v067", "to": "v066_recovered", "artifact": "v066_input.json"},
            {
                "from": "v066_recovered",
                "to": "v079_leaf",
                "artifact": "selected_pair_input.json",
            },
        ],
    }


def run_problem_only_pipeline(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    gemma_endpoint: str,
    salvage_verifier_endpoint: str,
    qwen_endpoint: str,
    master_seed: int = 20260825,
    selection_batch_size: int = 4,
) -> dict[str, Any]:
    if not 1 <= selection_batch_size <= 4:
        raise ValueError("selection_batch_size must be between 1 and 4")
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = child_paths(output_dir)
    runtime_config = RuntimeConfig(
        gemma_endpoint=gemma_endpoint.rstrip("/"),
        qwen_endpoint=qwen_endpoint.rstrip("/"),
        master_seed=master_seed,
    )
    tree = planned_tree(output_dir)
    write_json(
        output_dir / "manifest.json",
        {
            "schema": "cognitive-well-v079-problem-only-full-pipeline-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": utc_now(),
            "problem_id": run_input["problem_id"],
            "input_path": str(input_path.resolve()),
            "input_scope": "problem_statement_synthesis_instructions_and_gate_only",
            "preselected_proofs_supplied": False,
            "reused_generation_artifacts": False,
            "tree": tree,
            "upstream": {
                "six_track_harness": "frozen_v0.3.67",
                "selection_harness": "v0.3.70_compact_recovery_of_v0.3.66",
                "selection_semantics_changed": False,
            },
            "leaf": {
                "harness": HARNESS_VERSION,
                "fresh_extraction_schedule": list(FRESH_EXTRACTION_SCHEDULE),
                "final_split_verifier_gate": "skipped",
            },
            "runtime": {
                "gemma_endpoint": runtime_config.gemma_endpoint,
                "salvage_verifier_endpoint": salvage_verifier_endpoint.rstrip("/"),
                "qwen_endpoint": runtime_config.qwen_endpoint,
                "gemma_model": runtime_config.gemma_model,
                "qwen_model": runtime_config.qwen_model,
                "master_seed": master_seed,
                "selection_batch_size": selection_batch_size,
            },
            "reference_solution_access": False,
            "gold_score_access": False,
        },
    )
    completed: list[str] = []
    active = "v067_fresh_six_track_generation"
    try:
        _status(
            output_dir,
            state="running",
            active_node=active,
            completed_nodes=completed,
        )
        v067.run_pipeline(
            run_input=run_input,
            input_path=input_path,
            output_dir=paths["v067"],
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
        )
        v067_summary = _read_completed(paths["v067"] / "summary.json", "v0.3.67")
        v066_input_path = paths["v067"] / "v066_input.json"
        v066_input = load_v066_input(v066_input_path)
        completed.append("v067_fresh_six_track_generation")

        active = "v066_compact_recovery_selection"
        _status(
            output_dir,
            state="running",
            active_node=active,
            completed_nodes=completed,
        )
        run_recovered_v066(
            run_input=v066_input,
            input_path=v066_input_path,
            output_dir=paths["v066"],
            runtime_config=runtime_config,
            batch_size=selection_batch_size,
        )
        v066_summary = _read_completed(paths["v066"] / "summary.json", "v0.3.66 recovery")
        leaf_input_path = paths["v066"] / "selected_pair_input.json"
        leaf_input = load_leaf_input(leaf_input_path)
        completed.append("v066_compact_recovery_selection")

        active = "v079_fresh_lemma_leaf"
        _status(
            output_dir,
            state="running",
            active_node=active,
            completed_nodes=completed,
        )
        leaf_summary = run_full_leaf(
            run_input=leaf_input,
            input_path=leaf_input_path,
            output_dir=paths["leaf"],
            runtime_config=runtime_config,
            salvage_verifier_endpoint=salvage_verifier_endpoint,
        )
        completed.append("v079_fresh_lemma_leaf")
        summary = {
            "schema": "cognitive-well-v079-problem-only-full-pipeline-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "problem_id": run_input["problem_id"],
            "completed_nodes": completed,
            "six_track_count": int(v067_summary["candidate_count"]),
            "selected": list(v066_summary["selected"]),
            "selected_pair_input_path": str(leaf_input_path.resolve()),
            "selected_pair_input_sha256": _sha256_file(leaf_input_path),
            "final_shared_lemma_count": leaf_summary["final_shared_lemma_count"],
            "first_failure_salvage": leaf_summary["first_failure_salvage"],
            "atomic_child_retry": leaf_summary["atomic_child_retry"],
            "synthesis_candidate_count": leaf_summary["synthesis_candidate_count"],
            "leaf_summary_path": str((paths["leaf"] / "summary.json").resolve()),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "final_outputs.json",
            {
                "schema": "cognitive-well-v079-problem-only-final-outputs-v1",
                "problem_id": run_input["problem_id"],
                "synthesis_candidate_count": leaf_summary["synthesis_candidate_count"],
                "synthesis_candidates": leaf_summary["synthesis_candidates"],
                "final_shared_memory_path": str(
                    (paths["leaf"] / "final_shared_lemma_memory.json").resolve()
                ),
            },
        )
        _status(
            output_dir,
            state="completed",
            active_node="complete",
            completed_nodes=completed,
            synthesis_candidate_count=leaf_summary["synthesis_candidate_count"],
        )
        return summary
    except Exception as error:
        _status(
            output_dir,
            state="failed",
            active_node=active,
            completed_nodes=completed,
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise
