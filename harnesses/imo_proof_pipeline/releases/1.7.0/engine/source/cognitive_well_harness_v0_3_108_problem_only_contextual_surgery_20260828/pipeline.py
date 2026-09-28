from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
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
from cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827 import (
    run as v097,
)
from cognitive_well_harness_v0_3_98_batched_post_resolver_gate_20260827 import (
    run as v098,
)
from cognitive_well_harness_v0_3_99_semantic_obligation_grouping_20260827 import (
    pipeline as v099,
)
from cognitive_well_harness_v0_3_100_current_semantic_ledger_20260827 import (
    pipeline as v100,
)
from cognitive_well_harness_v0_3_103_p5_ungrouped_ledger_resolve_20260827 import (
    pipeline as v103,
)
from cognitive_well_harness_v0_3_105_iterated_ungrouped_resolve_20260827 import (
    pipeline as v105,
)
from cognitive_well_harness_v0_3_106_fresh_seed_audit_memory_bridge_20260828 import (
    run as v106,
)
from cognitive_well_harness_v0_3_107_enhanced_reviews_step9_terminal_20260828 import (
    pipeline as v107,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


STAGES = {
    "raw": "01_raw_lazy_enhanced_resolve",
    "gate": "02_post_resolver_audit_ledger",
    "second": "03_ungrouped_ledger_second_resolve",
    "third": "04_iterated_audit_ledger_third_resolve",
    "selection": "05_two_seed_selection",
    "seed_audit": "06_fresh_seed_audits",
    "memory": "07_lemma_memory_contextual_surgery",
}
EXECUTION_STAGES = (
    "raw_generation",
    "post_resolver_audit",
    "second_resolve",
    "third_resolve",
    "two_proof_selection",
    "seed_audit",
    "hypothesis_extraction",
    "novelty_gate",
    "lemma_certification",
    "proof_synthesis",
    "pre_refinement_audit",
    "proof_refinement",
    "post_refinement_audit",
    "contextual_surgical_repair",
)
SEED_COUNT = 2
SEED_SELECTION_POLICY = "highest_raw_temperature_then_frozen_replication_order"


class RequestedStop(Exception):
    def __init__(self, *, position: str, stage: str, completed: list[str]) -> None:
        super().__init__(f"requested stop {position} {stage}")
        self.position = position
        self.stage = stage
        self.completed = list(completed)


class BoundaryController:
    def __init__(
        self,
        *,
        output_dir: Path,
        stop_before: str | None,
        stop_after: str | None,
    ) -> None:
        if stop_before is not None and stop_before not in EXECUTION_STAGES:
            raise ValueError(f"unknown stop-before stage: {stop_before}")
        if stop_after is not None and stop_after not in EXECUTION_STAGES:
            raise ValueError(f"unknown stop-after stage: {stop_after}")
        if stop_before is not None and stop_after is not None:
            raise ValueError("stop_before and stop_after are mutually exclusive")
        self.output_dir = output_dir
        self.stop_before = stop_before
        self.stop_after = stop_after
        self.completed: list[str] = []

    def before(self, stage: str) -> None:
        if stage not in EXECUTION_STAGES:
            raise ValueError(f"unknown execution stage: {stage}")
        write_status(
            self.output_dir,
            stage,
            requested_stop_before=self.stop_before,
            requested_stop_after=self.stop_after,
            completed_stages=list(self.completed),
        )
        if self.stop_before == stage:
            raise RequestedStop(
                position="before", stage=stage, completed=self.completed
            )

    def complete(self, stage: str) -> None:
        if stage not in self.completed:
            self.completed.append(stage)
        if self.stop_after == stage:
            raise RequestedStop(
                position="after", stage=stage, completed=self.completed
            )


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_within(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes the single-problem source root: {path}") from error
    return path


FORBIDDEN_EXTERNAL_KEY_FRAGMENTS = (
    "codex",
    "score",
    "grade",
    "gold",
    "reference",
    "external",
    "cross_problem",
)


def reject_external_annotations(value: Any, *, location: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if any(token in normalized for token in FORBIDDEN_EXTERNAL_KEY_FRAGMENTS):
                raise ValueError(
                    f"forbidden external annotation key in solver input at {location}.{key}"
                )
            reject_external_annotations(child, location=f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_external_annotations(child, location=f"{location}[{index}]")


def validate_seed_state(
    state: dict[str, Any], *, problem_root: Path, expected_problem_id: str
) -> dict[str, Any]:
    reject_external_annotations(state, location="seed_state")
    if str(state.get("problem_id") or "") != expected_problem_id:
        raise ValueError("seed-state problem identity drift")
    candidates = state.get("candidate_proofs")
    if not isinstance(candidates, list) or len(candidates) != SEED_COUNT:
        raise ValueError("seed state must contain exactly two candidates")
    for row in candidates:
        if not isinstance(row, dict):
            raise ValueError("seed state contains a non-object candidate")
        proof_path = str(row.get("proof_path") or "")
        if proof_path.startswith("inline:"):
            raise ValueError("v0.3.108 seed proofs must be hash-frozen files")
        require_within(
            problem_root,
            Path(proof_path),
            f"seed proof {row.get('candidate_id') or '<missing>'}",
        )
    return state


def completed_summary(path: Path) -> dict[str, Any] | None:
    summary_path = path / "summary.json"
    if not summary_path.is_file():
        return None
    summary = read_object(summary_path)
    return summary if summary.get("state") == "completed" else None


def problem_number_from_id(problem_id: str) -> int:
    match = re.search(r"(?:^|[_-])p([0-9]+)$", problem_id, re.IGNORECASE)
    if match is None:
        raise ValueError(
            "problem_number is required when problem_id does not end in P<number>"
        )
    return int(match.group(1))


def stage_paths(output_dir: Path) -> dict[str, Path]:
    return {name: output_dir / relative for name, relative in STAGES.items()}


def write_status(output_dir: Path, stage: str, **extra: Any) -> None:
    write_json(
        output_dir / "status.json",
        {
            "state": "running",
            "stage": stage,
            "updated_at": utc_now(),
            **extra,
        },
    )


def build_manifest(
    *,
    problem_file: Path,
    problem_id: str,
    problem_number: int,
    gemma_endpoint: str,
    qwen_endpoint: str,
    salvage_verifier_endpoint: str,
    gemma_workers: int,
    qwen_workers: int,
    resolve_workers: int,
    seed_workers: int,
    master_seed: int,
    seed_namespace: str,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v0108-problem-only-contextual-surgery-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "input_contract": "problem_statement_only",
        "problem_file": str(problem_file.resolve()),
        "problem_file_sha256": file_sha256(problem_file.resolve()),
        "problem_id": problem_id,
        "problem_number": problem_number,
        "models": {"gemma": GEMMA_MODEL, "qwen": QWEN_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "qwen_endpoint": qwen_endpoint,
            "salvage_verifier_endpoint": salvage_verifier_endpoint,
            "gemma_precision": "BF16",
            "gemma_mtp_speculative_tokens": 4,
            "gemma_reasoning_effort": "max",
            "gemma_workers": gemma_workers,
            "qwen_workers": qwen_workers,
            "resolve_workers": resolve_workers,
            "seed_workers": seed_workers,
            "master_seed": master_seed,
            "seed_namespace": seed_namespace,
        },
        "stage_directories": dict(STAGES),
        "execution_stage_order": list(EXECUTION_STAGES),
        "control_contract": {
            "stop_before": list(EXECUTION_STAGES),
            "stop_after": list(EXECUTION_STAGES),
            "resume": "rerun_with_same_output_directory",
            "completed_model_calls_reused": True,
            "controls_do_not_change_mathematical_prompts": True,
        },
        "protocol": {
            "raw_candidates": ["t10_r01", "t10_r02", "t07_r01", "t07_r02"],
            "raw_temperatures": [1.0, 1.0, 0.7, 0.7],
            "raw_lazy_review_parent": "0.3.97",
            "post_resolver_gate_parent": "0.3.98",
            "semantic_obligation_grouping": False,
            "ungrouped_records_preserved_individually": True,
            "second_resolve_parent_prompt": "0.3.103/0.3.101",
            "third_resolve_parent": "0.3.105",
            "seed_count": SEED_COUNT,
            "seed_selection_policy": SEED_SELECTION_POLICY,
            "seed_selection_model_calls": 0,
            "seed_selection_uses_scores": False,
            "seed_audit_parent": "0.3.106",
            "memory_contextual_parent": "0.3.107",
            "step_5_trace_enhanced_reviews": True,
            "step_7_trace_enhanced_reviews": True,
            "dynamic_literal_audit": "disabled_non_authoritative",
            "terminal_boundary": "after_contextual_surgical_repair_step_9",
            "step_10_memory_commit": False,
            "step_11_selection": False,
            "iteration_2": False,
        },
        "problem_specific_prompting": False,
        "problem_specific_prompt_logic": False,
        "reference_solution_access": False,
        "gold_score_access": False,
        "codex_feedback_access": False,
        "cross_problem_transfer": False,
        "problem_only_schema_enforced": True,
        "runtime_cross_problem_artifact_reads": False,
        "problem_blindness": {
            "one_problem_per_process": True,
            "sibling_problem_artifact_reads": False,
            "cross_problem_memory": False,
            "queue_order_affects_solver_seed": False,
        },
    }


def validate_or_write_manifest(output_dir: Path, manifest: dict[str, Any]) -> None:
    path = output_dir / "manifest.json"
    if not path.is_file():
        write_json(path, manifest)
        return
    existing = read_object(path)
    immutable = (
        "schema",
        "harness_version",
        "problem_file_sha256",
        "problem_id",
        "problem_number",
        "models",
    )
    drift = [key for key in immutable if existing.get(key) != manifest.get(key)]
    for key in (
        "gemma_endpoint",
        "qwen_endpoint",
        "salvage_verifier_endpoint",
        "gemma_precision",
        "gemma_mtp_speculative_tokens",
        "gemma_reasoning_effort",
        "master_seed",
        "seed_namespace",
    ):
        if (existing.get("runtime") or {}).get(key) != (
            manifest.get("runtime") or {}
        ).get(key):
            drift.append(f"runtime.{key}")
    if drift:
        raise ValueError(f"resume manifest drift in fields: {drift}")


def _direct_ungrouped_cases(
    *, source_run: Path, problem_id: str
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for case in v099.load_source_cases(source_run):
        if str(case["problem_id"]) != problem_id:
            continue
        active, archived = v100.split_source_entries(case["entries"])
        cases.append(
            {
                **case,
                "active_entries": active,
                "archived_entries": archived,
            }
        )
    if not cases:
        raise ValueError(f"post-resolver ledger has no cases for {problem_id}")
    return cases


def run_direct_ungrouped_resolve(
    *,
    source_run: Path,
    output_dir: Path,
    problem_id: str,
    gemma_endpoint: str,
    workers: int,
    seed_namespace: str,
) -> dict[str, Any]:
    """Consume v0.3.98 ledgers directly; no semantic grouping model call."""
    saved = completed_summary(output_dir)
    if saved is not None:
        return saved
    if workers < 1:
        raise ValueError("resolve workers must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = _direct_ungrouped_cases(source_run=source_run, problem_id=problem_id)
    manifest = {
        # v0.3.105 deliberately accepts this frozen schema prefix.
        "schema": "cognitive-well-v0103-ungrouped-ledger-resolve-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_run": str(source_run.resolve()),
        "problem_id": problem_id,
        "model": GEMMA_MODEL,
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "workers": workers,
            "precision": "BF16",
            "mtp": 4,
            "reasoning_effort": "max",
        },
        "temperature": v103.TEMPERATURE,
        "max_tokens": v103.MAX_TOKENS,
        "protocol": {
            "direct_v098_ledger_input": True,
            "semantic_grouping": False,
            "shared_problem_bank": False,
            "cross_proof_transfer": False,
            "active_records_preserved_individually": True,
            "closed_and_unsupported_excluded": True,
            "problem_specific_prompting": False,
        },
        "cases": [
            {
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "active_ungrouped_obligation_count": len(case["active_entries"]),
                "archived_obligation_count": len(case["archived_entries"]),
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "ungrouped_resolve", "updated_at": utc_now()},
    )

    def resolve(case: dict[str, Any]) -> dict[str, Any]:
        if not case["active_entries"]:
            return materialize_no_active_passthrough(
                case=case,
                output_dir=(
                    output_dir
                    / "cases"
                    / str(case["case_id"])
                    / "gemma_ungrouped_ledger_resolve"
                ),
            )
        return v103.run_case(
            case=case,
            endpoint=gemma_endpoint,
            output_dir=(
                output_dir
                / "cases"
                / str(case["case_id"])
                / "gemma_ungrouped_ledger_resolve"
            ),
            seed_namespace=seed_namespace,
        )

    results: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers, thread_name_prefix="v0108-ungrouped-resolve"
    ) as pool:
        pending = {pool.submit(resolve, case): case for case in cases}
        for future in concurrent.futures.as_completed(pending):
            case = pending[future]
            case_id = str(case["case_id"])
            try:
                results[case_id] = future.result()
            except Exception as error:
                errors[case_id] = f"{type(error).__name__}: {error}"
            write_json(output_dir / "errors.json", errors)
            write_json(
                output_dir / "status.json",
                {
                    "state": "running",
                    "stage": "ungrouped_resolve",
                    "completed_count": len(results),
                    "failed_count": len(errors),
                    "total": len(cases),
                    "updated_at": utc_now(),
                },
            )
    if errors:
        raise RuntimeError(f"ungrouped resolve failures: {errors}")

    rows = []
    for case in cases:
        result = results[str(case["case_id"])]
        rows.append(
            {
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "resolved_proof_path": result["resolved_proof_path"],
                "resolved_proof_sha256": result["resolved_proof_sha256"],
                "active_ungrouped_obligation_count": len(case["active_entries"]),
                "archived_obligation_count": len(case["archived_entries"]),
            }
        )
    summary = {
        "schema": "cognitive-well-v0103-ungrouped-ledger-resolve-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "problem_id": problem_id,
        "case_count": len(rows),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "status.json",
        {"state": "completed", "stage": "done", "updated_at": utc_now()},
    )
    return summary


def materialize_no_active_passthrough(
    *, case: dict[str, Any], output_dir: Path
) -> dict[str, Any]:
    """Materialize an audited proof unchanged when there is nothing to repair."""
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return read_object(result_path)
    if case.get("active_entries"):
        raise ValueError(f"passthrough case still has active obligations: {case['case_id']}")
    source_path = Path(str(case["proof_path"])).resolve()
    proof = source_path.read_text(encoding="utf-8").strip()
    proof_sha256 = text_sha256(proof)
    if proof_sha256 != str(case["proof_sha256"]):
        raise ValueError(f"passthrough proof hash drift: {case['case_id']}")
    output_dir.mkdir(parents=True, exist_ok=True)
    proof_path = output_dir / "resolved_proof.md"
    proof_path.write_bytes(source_path.read_bytes())
    if text_sha256(proof_path.read_text(encoding="utf-8").strip()) != proof_sha256:
        raise AssertionError(f"passthrough copy changed proof: {case['case_id']}")
    result = {
        "schema": "cognitive-well-v0108-no-active-obligations-passthrough-v1",
        "harness_version": HARNESS_VERSION,
        "state": "skipped_no_active_obligations",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "problem_id": case["problem_id"],
        "candidate_id": case["candidate_id"],
        "source_proof_path": str(source_path),
        "source_proof_sha256": proof_sha256,
        "mandatory_ungrouped_obligation_count": 0,
        "archived_obligation_count": len(case["archived_entries"]),
        "resolved_proof_path": str(proof_path.resolve()),
        "resolved_proof_sha256": proof_sha256,
        "generation": None,
        "runtime_recovery_events": [],
    }
    write_json(result_path, result)
    return result


def select_two_seed_proofs(
    *, third_resolve_dir: Path, output_dir: Path, problem_id: str
) -> dict[str, Any]:
    saved = completed_summary(output_dir)
    if saved is not None:
        return saved
    summary = read_object(third_resolve_dir / "summary.json")
    if summary.get("state") != "completed":
        raise ValueError("third-resolve stage is not completed")
    rows = [
        dict(row)
        for row in summary.get("rows") or []
        if str(row.get("problem_id")) == problem_id
    ]
    by_id = {str(row["candidate_id"]): row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("third-resolve rows contain duplicate candidate IDs")
    spec_by_id = {
        str(spec["candidate_id"]): (float(spec["temperature"]), index)
        for index, spec in enumerate(v097.RAW_CANDIDATES)
    }
    missing = sorted(set(spec_by_id) - set(by_id))
    if missing:
        raise ValueError(f"third-resolve portfolio lacks candidates: {missing}")
    ranked = sorted(
        rows,
        key=lambda row: (
            -spec_by_id[str(row["candidate_id"])][0],
            spec_by_id[str(row["candidate_id"])][1],
        ),
    )
    selected = []
    for rank, row in enumerate(ranked[:SEED_COUNT], start=1):
        proof_path = require_within(
            third_resolve_dir,
            Path(str(row["third_proof_path"])),
            f"third proof {row['candidate_id']}",
        )
        proof = proof_path.read_text(encoding="utf-8").strip()
        proof_sha256 = text_sha256(proof)
        if proof_sha256 != str(row["third_proof_sha256"]):
            raise ValueError(f"third proof hash drift: {row['candidate_id']}")
        selected.append(
            {
                "rank": rank,
                "candidate_id": str(row["candidate_id"]),
                "raw_temperature": spec_by_id[str(row["candidate_id"])][0],
                "proof_path": str(proof_path),
                "proof_sha256": proof_sha256,
                "third_resolve_state": row["third_resolve_state"],
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "cognitive-well-v0108-two-seed-selection-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "problem_id": problem_id,
        "policy": SEED_SELECTION_POLICY,
        "model_call_count": 0,
        "uses_reviews": False,
        "uses_scores": False,
        "uses_gold_or_reference": False,
        "selected": selected,
    }
    write_json(output_dir / "selection.json", result)
    write_json(output_dir / "summary.json", result)
    return result


def _memory_status(output_dir: Path, stage: str) -> None:
    write_json(
        output_dir / "status.json",
        {
            "state": "running",
            "stage": stage,
            "iteration": 1,
            "updated_at": utc_now(),
        },
    )


def _checkpoint(output_dir: Path, name: str, value: dict[str, Any]) -> None:
    write_json(output_dir / "checkpoints" / f"{name}.json", value)


def _saved_checkpoint(output_dir: Path, name: str) -> dict[str, Any] | None:
    path = output_dir / "checkpoints" / f"{name}.json"
    return read_object(path) if path.is_file() else None


def run_controlled_memory_pipeline(
    *,
    initial_state: dict[str, Any],
    source_run_dir: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
    seed_namespace: str,
    controller: BoundaryController,
) -> dict[str, Any]:
    """Run v0.3.107 through Step 9 with resumable substage boundaries."""
    saved = completed_summary(output_dir)
    if saved is not None:
        return saved
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    memory_manifest = v107.build_manifest(
        initial_state=initial_state,
        source_run_dir=source_run_dir,
        runtime_config=runtime_config,
        salvage_verifier_endpoint=salvage_verifier_endpoint,
    )
    memory_manifest["checkpoint_contract"] = {
        "controlled_by": HARNESS_VERSION,
        "stages": list(EXECUTION_STAGES[6:]),
        "resume": "load_checkpoint_before_reissuing_model_calls",
    }
    if not manifest_path.is_file():
        write_json(manifest_path, memory_manifest)
    write_json(output_dir / "initial_state.json", initial_state)

    problem_id = str(initial_state["problem_id"])
    problem = str(initial_state["problem"])
    run_input = {"problem_id": problem_id, "problem": problem}
    candidate_proofs = list(initial_state["candidate_proofs"])
    iteration_dir = output_dir / "iteration_1"

    controller.before("hypothesis_extraction")
    runtime = v107.ResilientModelRuntime(runtime_config)
    verifier_runtime = v107.make_gemma_verifier_runtime(
        RuntimeConfig(
            gemma_endpoint=salvage_verifier_endpoint.rstrip("/"),
            qwen_endpoint=salvage_verifier_endpoint.rstrip("/"),
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.gemma_model,
            master_seed=runtime_config.master_seed,
        )
    )
    context_certified: list[dict[str, Any]] = []
    provisional: list[dict[str, Any]] = []
    failed_memory: list[dict[str, Any]] = []

    _memory_status(output_dir, "01_hypothesis_extraction_batch")
    saved_stage = _saved_checkpoint(output_dir, "01_hypothesis_extraction")
    if saved_stage is None:
        extracted = v107.v082.run_extraction(
            runtime=runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            context_certified_memory=context_certified,
            provisional_memory=provisional,
            failed_memory=failed_memory,
            iteration=1,
            output_dir=iteration_dir / "01_hypothesis_extraction",
        )
        _checkpoint(
            output_dir, "01_hypothesis_extraction", {"extracted": extracted}
        )
    else:
        extracted = list(saved_stage["extracted"])
    controller.complete("hypothesis_extraction")

    controller.before("novelty_gate")
    _memory_status(output_dir, "02_novelty_vote_batch")
    saved_stage = _saved_checkpoint(output_dir, "02_novelty_gate")
    if saved_stage is None:
        accepted, novelty_audit = v107.v083_batch.novelty_gate_batched(
            runtime=runtime,
            extraction_results=extracted,
            certified_memory=v107.v082.combined_memory(
                context_certified, provisional
            ),
            failed_memory=failed_memory,
            iteration=1,
            output_dir=iteration_dir / "02_novelty_gate",
        )
        _checkpoint(
            output_dir,
            "02_novelty_gate",
            {"accepted": accepted, "novelty_audit": novelty_audit},
        )
    else:
        accepted = list(saved_stage["accepted"])
        novelty_audit = list(saved_stage["novelty_audit"])
    controller.complete("novelty_gate")

    controller.before("lemma_certification")
    _memory_status(output_dir, "03_certification_waves")
    saved_stage = _saved_checkpoint(output_dir, "03_lemma_certification")
    if saved_stage is None:
        preliminary, failed_memory, certification = (
            v107.v083_batch.run_certification_and_memory_batched(
                proof_runtime=runtime,
                verifier_runtime=verifier_runtime,
                runtime_config=runtime_config,
                salvage_verifier_endpoint=salvage_verifier_endpoint,
                problem=problem,
                candidate_proofs=candidate_proofs,
                accepted_hypotheses=accepted,
                certified_memory=v107.v082.combined_memory(
                    context_certified, provisional
                ),
                failed_memory=failed_memory,
                iteration=1,
                output_dir=iteration_dir / "03_preliminary_certification",
            )
        )
        context_certified, provisional = v107.v082.partition_preliminary_memory(
            previous_context_certified=context_certified,
            preliminary_rows=preliminary,
        )
        _checkpoint(
            output_dir,
            "03_lemma_certification",
            {
                "preliminary": preliminary,
                "failed_memory": failed_memory,
                "certification": certification,
                "context_certified": context_certified,
                "provisional": provisional,
            },
        )
    else:
        preliminary = list(saved_stage["preliminary"])
        failed_memory = list(saved_stage["failed_memory"])
        certification = dict(saved_stage["certification"])
        context_certified = list(saved_stage["context_certified"])
        provisional = list(saved_stage["provisional"])
    controller.complete("lemma_certification")

    controller.before("proof_synthesis")
    _memory_status(output_dir, "04_six_candidate_synthesis_batch")
    saved_stage = _saved_checkpoint(output_dir, "04_proof_synthesis")
    if saved_stage is None:
        synthesized = v107.v082.run_synthesis(
            runtime=runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            context_certified_memory=context_certified,
            provisional_memory=provisional,
            iteration=1,
            output_dir=iteration_dir / "04_synthesis",
        )
        _checkpoint(output_dir, "04_proof_synthesis", {"candidates": synthesized})
    else:
        synthesized = list(saved_stage["candidates"])
    controller.complete("proof_synthesis")

    controller.before("pre_refinement_audit")
    _memory_status(output_dir, "05_trace_enhanced_full_proof_audit")
    saved_stage = _saved_checkpoint(output_dir, "05_pre_refinement_audit")
    if saved_stage is None:
        pre_audited = v107.run_enhanced_review_fusion_dag(
            run_input=run_input,
            candidates=synthesized,
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            output_dir=iteration_dir / "05_pre_refinement_audit",
            seed_namespace=f"{seed_namespace}:step5",
        )
        _checkpoint(
            output_dir, "05_pre_refinement_audit", {"candidates": pre_audited}
        )
    else:
        pre_audited = list(saved_stage["candidates"])
    controller.complete("pre_refinement_audit")

    controller.before("proof_refinement")
    _memory_status(output_dir, "06_refinement_batch")
    saved_stage = _saved_checkpoint(output_dir, "06_proof_refinement")
    if saved_stage is None:
        refined = v107.v081.run_refinement(
            runtime=runtime,
            problem=problem,
            audited_candidates=pre_audited,
            iteration=1,
            output_dir=iteration_dir / "06_refinement",
        )
        refined = v107.v082.rebind_memory_dependencies(
            candidates=refined,
            context_certified=context_certified,
            provisional=provisional,
        )
        _checkpoint(output_dir, "06_proof_refinement", {"candidates": refined})
    else:
        refined = list(saved_stage["candidates"])
    controller.complete("proof_refinement")

    controller.before("post_refinement_audit")
    _memory_status(output_dir, "07_trace_enhanced_fresh_full_proof_audit")
    saved_stage = _saved_checkpoint(output_dir, "07_post_refinement_audit")
    if saved_stage is None:
        post_audited = v107.run_enhanced_review_fusion_dag(
            run_input=run_input,
            candidates=refined,
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            output_dir=iteration_dir / "07_post_refinement_audit",
            seed_namespace=f"{seed_namespace}:step7",
        )
        _checkpoint(
            output_dir, "07_post_refinement_audit", {"candidates": post_audited}
        )
    else:
        post_audited = list(saved_stage["candidates"])
    controller.complete("post_refinement_audit")

    controller.before("contextual_surgical_repair")
    write_json(
        iteration_dir / "08_dynamic_literal_audit" / "SKIPPED.json",
        {
            "status": "SKIPPED_NON_AUTHORITATIVE",
            "reason": "fragile_quote_binding_transport",
            "input_candidate_count": len(post_audited),
            "affects_step_9_routing": False,
        },
    )
    _memory_status(
        output_dir,
        "09_contextual_repair_from_step_7_stop_before_memory_transaction",
    )
    saved_stage = _saved_checkpoint(output_dir, "09_contextual_surgical_repair")
    if saved_stage is None:
        final_candidates, contextual_feedback = (
            v107.run_contextual_repairs_step8_disabled(
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
        )
        _checkpoint(
            output_dir,
            "09_contextual_surgical_repair",
            {
                "final_candidates": final_candidates,
                "contextual_feedback": contextual_feedback,
            },
        )
    else:
        final_candidates = list(saved_stage["final_candidates"])
        contextual_feedback = dict(saved_stage["contextual_feedback"])

    summary = {
        "schema": "cognitive-well-v0108-controlled-memory-step9-summary-v1",
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
        "step_8_literal_outcomes": {
            "SKIPPED_NON_AUTHORITATIVE": len(post_audited)
        },
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
    controller.complete("contextual_surgical_repair")
    return summary


def stopped_summary(
    *,
    output_dir: Path,
    problem_id: str,
    problem_number: int,
    stop: RequestedStop,
) -> dict[str, Any]:
    stage_index = EXECUTION_STAGES.index(stop.stage)
    next_stage = (
        stop.stage
        if stop.position == "before"
        else (
            EXECUTION_STAGES[stage_index + 1]
            if stage_index + 1 < len(EXECUTION_STAGES)
            else None
        )
    )
    summary = {
        "schema": "cognitive-well-v0108-controlled-stop-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "stopped_at_boundary",
        "stopped_at": utc_now(),
        "problem_id": problem_id,
        "problem_number": problem_number,
        "position": stop.position,
        "stage": stop.stage,
        "next_stage": next_stage,
        "completed_stages": stop.completed,
        "resume": "rerun the same command and output directory without this stop, or choose a later stop boundary",
        "stage_directories": dict(STAGES),
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "status.json",
        {
            "state": "stopped_at_boundary",
            "stage": stop.stage,
            "position": stop.position,
            "next_stage": next_stage,
            "completed_stages": stop.completed,
            "updated_at": utc_now(),
        },
    )
    return summary


def run_pipeline(
    *,
    problem_file: Path,
    problem_id: str,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    salvage_verifier_endpoint: str | None = None,
    problem_number: int | None = None,
    gemma_workers: int = 4,
    qwen_workers: int = 4,
    resolve_workers: int = 2,
    seed_workers: int = 2,
    master_seed: int = 20260828,
    seed_namespace: str = "v0108",
    stop_before: str | None = None,
    stop_after: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    problem_file = problem_file.resolve()
    if not problem_file.is_file():
        raise FileNotFoundError(problem_file)
    # Fail before any resume artifact or model endpoint is consulted if the input
    # envelope contains a reference, score, feedback, history, or any other side
    # channel beyond the statement identity fields.
    problem_payload = v097.validate_problem_only_source(problem_file)
    problem_id = problem_id.strip()
    if not problem_id:
        raise ValueError("problem_id must be nonempty")
    problem_number = problem_number or problem_number_from_id(problem_id)
    declared_problem_id = str(problem_payload.get("problem_id") or "").strip()
    if declared_problem_id and declared_problem_id != problem_id:
        raise ValueError("problem_id does not match the problem-only input")
    declared_problem_number = problem_payload.get("problem_number")
    if declared_problem_number is not None and int(declared_problem_number) != problem_number:
        raise ValueError("problem_number does not match the problem-only input")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    gemma_endpoint = gemma_endpoint.rstrip("/")
    qwen_endpoint = qwen_endpoint.rstrip("/")
    salvage_verifier_endpoint = (salvage_verifier_endpoint or gemma_endpoint).rstrip(
        "/"
    )
    if not gemma_endpoint or not qwen_endpoint or gemma_endpoint == qwen_endpoint:
        raise ValueError("distinct nonempty Gemma and Qwen endpoints are required")
    if min(gemma_workers, qwen_workers, resolve_workers, seed_workers) < 1:
        raise ValueError("all worker counts must be positive")
    controller = BoundaryController(
        output_dir=output_dir,
        stop_before=stop_before,
        stop_after=stop_after,
    )
    paths = stage_paths(output_dir)
    manifest = build_manifest(
        problem_file=problem_file,
        problem_id=problem_id,
        problem_number=problem_number,
        gemma_endpoint=gemma_endpoint,
        qwen_endpoint=qwen_endpoint,
        salvage_verifier_endpoint=salvage_verifier_endpoint,
        gemma_workers=gemma_workers,
        qwen_workers=qwen_workers,
        resolve_workers=resolve_workers,
        seed_workers=seed_workers,
        master_seed=master_seed,
        seed_namespace=seed_namespace,
    )
    validate_or_write_manifest(output_dir, manifest)

    finished = completed_summary(output_dir)
    if finished is not None:
        return finished

    if dry_run:
        summary = {
            "schema": "cognitive-well-v0108-dry-run-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "completed_at": utc_now(),
            "problem_id": problem_id,
            "stage_directories": dict(STAGES),
            "execution_stage_order": list(EXECUTION_STAGES),
            "requested_stop_before": stop_before,
            "requested_stop_after": stop_after,
            "seed_selection_policy": SEED_SELECTION_POLICY,
            "semantic_grouping": False,
            "dynamic_literal_audit": "disabled_non_authoritative",
            "terminal_boundary": "after_step_9",
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()},
        )
        return summary

    try:
        controller.before("raw_generation")
        raw = completed_summary(paths["raw"]) or v097.run(
            problem_file=problem_file,
            output_dir=paths["raw"],
            gpu0_gemma_endpoint=gemma_endpoint,
            gpu1_qwen_endpoint=qwen_endpoint,
            seed_namespace=f"{seed_namespace}:raw",
            problem_id=problem_id,
            problem_number=problem_number,
        )
        controller.complete("raw_generation")

        controller.before("post_resolver_audit")
        gate = completed_summary(paths["gate"]) or v098.run(
            source_runs=[paths["raw"]],
            output_dir=paths["gate"],
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            gemma_workers=gemma_workers,
            qwen_workers=qwen_workers,
            seed_namespace=f"{seed_namespace}:gate",
        )
        controller.complete("post_resolver_audit")

        controller.before("second_resolve")
        second = run_direct_ungrouped_resolve(
            source_run=paths["gate"],
            output_dir=paths["second"],
            problem_id=problem_id,
            gemma_endpoint=gemma_endpoint,
            workers=resolve_workers,
            seed_namespace=f"{seed_namespace}:second",
        )
        controller.complete("second_resolve")

        controller.before("third_resolve")
        third = completed_summary(paths["third"]) or v105.run(
            resolve_runs=[paths["second"]],
            prior_gate_run=paths["gate"],
            output_dir=paths["third"],
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            gemma_workers=gemma_workers,
            qwen_workers=qwen_workers,
            resolve_workers=resolve_workers,
            seed_namespace=f"{seed_namespace}:third",
        )
        controller.complete("third_resolve")

        controller.before("two_proof_selection")
        selection = select_two_seed_proofs(
            third_resolve_dir=paths["third"],
            output_dir=paths["selection"],
            problem_id=problem_id,
        )
        candidates = [
            (str(row["candidate_id"]), Path(str(row["proof_path"])))
            for row in selection["selected"]
        ]
        controller.complete("two_proof_selection")

        controller.before("seed_audit")
        normalized_problem_path = paths["raw"] / "input" / "problem.json"
        seed_summary = completed_summary(paths["seed_audit"])
        initial_state_path = paths["seed_audit"] / "initial_state.json"
        if seed_summary is None:
            initial_state_path = v106.prepare_seed_state(
                problem_path=normalized_problem_path,
                problem_id=problem_id,
                candidates=candidates,
                output_dir=paths["seed_audit"],
                gemma_endpoint=gemma_endpoint,
                qwen_endpoint=qwen_endpoint,
                workers=seed_workers,
                seed_namespace=f"{seed_namespace}:seed_audit",
                allowed_source_root=output_dir,
            )
            seed_summary = read_object(paths["seed_audit"] / "summary.json")
        controller.complete("seed_audit")

        initial_state = validate_seed_state(
            v107.load_initial_state(initial_state_path),
            problem_root=output_dir,
            expected_problem_id=problem_id,
        )
        memory = completed_summary(paths["memory"]) or run_controlled_memory_pipeline(
            initial_state=initial_state,
            source_run_dir=paths["seed_audit"],
            output_dir=paths["memory"],
            runtime_config=RuntimeConfig(
                gemma_endpoint=gemma_endpoint,
                qwen_endpoint=qwen_endpoint,
                gemma_model=GEMMA_MODEL,
                qwen_model=QWEN_MODEL,
                master_seed=master_seed,
            ),
            salvage_verifier_endpoint=salvage_verifier_endpoint,
            seed_namespace=seed_namespace,
            controller=controller,
        )

        summary = {
            "schema": "cognitive-well-v0108-problem-only-contextual-surgery-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "problem_id": problem_id,
            "problem_number": problem_number,
            "seed_selection": selection,
            "terminal_boundary": "after_contextual_surgical_repair_step_9",
            "terminal_candidates": list(memory.get("final_candidates") or []),
            "stages": {
                "raw": raw.get("schema"),
                "gate": gate.get("schema"),
                "second": second.get("schema"),
                "third": third.get("schema"),
                "seed_audit": seed_summary.get("schema"),
                "memory": memory.get("schema"),
            },
            "problem_specific_prompting": False,
            "reference_solution_access": False,
            "gold_score_access": False,
            "codex_feedback_access": False,
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {"state": "completed", "stage": "done", "updated_at": utc_now()},
        )
        return summary
    except RequestedStop as stop:
        return stopped_summary(
            output_dir=output_dir,
            problem_id=problem_id,
            problem_number=problem_number,
            stop=stop,
        )
    except Exception as error:
        write_json(
            output_dir / "status.json",
            {
                "state": "failed",
                "stage": "pipeline_exception",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise


__all__ = [
    "EXECUTION_STAGES",
    "SEED_SELECTION_POLICY",
    "STAGES",
    "build_manifest",
    "run_direct_ungrouped_resolve",
    "run_pipeline",
    "select_two_seed_proofs",
    "stage_paths",
]
