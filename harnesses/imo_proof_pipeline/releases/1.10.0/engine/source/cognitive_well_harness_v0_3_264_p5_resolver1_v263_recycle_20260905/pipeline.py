from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905 import (
    pipeline as parent,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_RUN = (
    REPO_ROOT / "runs/v0257_v108_six_problem_bf_temp_transition_20260904"
)
SOURCE_PHASE_2 = Path("p5/01_raw_lazy_enhanced_resolve/phase_2_v096")
PROBLEM_ID = "imo2026_p5"
PROBLEM_NUMBER = 5
CANDIDATE_IDS = ("t10_r01", "t10_r02", "t07_r01", "t07_r02")
EXPECTED_PROBLEM_SHA256 = (
    "f298ac63a0c7bbca176888c0ed48a1da2fedb09f7609c042dfbb9540bde8231e"
)
EXPECTED_RESOLVER1_PROOF_SHA256 = {
    "t10_r01": "99f6145c16b387196178029323489f257854c98c14ec099d68fa8bfbc8105bb1",
    "t10_r02": "03a30170a1d693bf6d661316cde0b520a181b40c78d5d9ed54a66d345a17630c",
    "t07_r01": "bc236c60b92f2dc8d4fc7954ab01adae0b2ceb7ef08c84fcb2613f1d664194a8",
    "t07_r02": "c93c3bf3c682e7dd7398f131ff99441380ebe20587221f1211d40f8b2ae811bd",
}
DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
DEFAULT_SEED_NAMESPACE = "v0264:p5:resolver1_recycle"
QWEN_REVIEWER2_MAX_TOKENS = 32_768
QWEN_REVIEWER2_RECOVERY_TOKENS = (49_152, 65_536)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _write_immutable_json(path: Path, value: dict[str, Any]) -> None:
    if path.is_file():
        if _read_json(path) != value:
            raise ValueError(f"immutable manifest drift: {path}")
        return
    _write_json(path, value)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _text_file_sha256(path: Path) -> str:
    return _text_sha256(path.read_text(encoding="utf-8").strip())


def _require_within(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes {root}: {path}") from error
    return path


def _single_path(paths: list[Path], label: str) -> Path:
    if len(paths) != 1:
        raise ValueError(f"expected one {label}, found {len(paths)}")
    return paths[0].resolve()


def _effective_stage() -> tuple[Any, Any]:
    """Resolve the review stage through v0263, never as a standalone contract."""

    if parent.HARNESS_VERSION != PARENT_HARNESS_VERSION:
        raise RuntimeError("v0263 parent identity drift")
    v260 = parent.parent
    v258 = v260.parent
    v257 = v258.parent
    v097 = v257.v108.v097
    stage = v097.enhanced_pipeline
    # v0264's sole explicit sampling override. The user selected a 32k default
    # with 48k and 64k clean-restart rungs for the adversarial reviewer. Since
    # v0260 forces every physical call and uses max(primary_cap, 32k), the
    # corresponding replacement caps are also 32k, 48k, and 64k.
    stage.reviewer_2.MAX_OUTPUT_TOKENS = QWEN_REVIEWER2_MAX_TOKENS
    stage.reviewer_2.CAP_RECOVERY_MAX_OUTPUT_TOKENS = (
        QWEN_REVIEWER2_RECOVERY_TOKENS[0]
    )
    stage.reviewer_2.FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS = (
        QWEN_REVIEWER2_RECOVERY_TOKENS[1]
    )
    if stage.resolver.parse_resolution is not parent.parse_resolution_compat:
        raise RuntimeError("v0263 Resolver parser compatibility is not installed")
    if stage.resolver.run_task is not parent.run_resolver_task_compat:
        raise RuntimeError("v0263 Fusion-bound Resolver worker is not installed")
    if v260._budget_forcing.continuation_config is not v260.continuation_config_32k:
        raise RuntimeError("v0260 32k budget-forcing continuation is not installed")
    if parent.v105.resolve_cases is not parent.resolve_cases_v263:
        raise RuntimeError("v0263 third-resolver recovery is not installed")
    return stage, v097


def effective_contract() -> dict[str, Any]:
    stage, v097 = _effective_stage()
    return {
        "authority": "cognitive-well-v0.3.263",
        "parent_harness_version": parent.HARNESS_VERSION,
        "v263_entrypoint_module": parent.__name__,
        "v263_entrypoint_sha256": _file_sha256(Path(parent.__file__).resolve()),
        "v263_raw_stage_owner": v097.__name__,
        "v263_raw_stage_owner_sha256": _file_sha256(Path(v097.__file__).resolve()),
        "inherited_implementation_module": stage.__name__,
        "inherited_implementation_sha256": _file_sha256(
            Path(stage.__file__).resolve()
        ),
        "contract_note": (
            "The inherited implementation schema is provenance only; v0.3.263 "
            "is the selected and asserted runtime contract."
        ),
        "schedule": {
            "gemma_branch": "Reviewer1 batch, then Reviewer3 batch",
            "qwen_branch": "Reviewer2 batch concurrent with the Gemma branch",
            "barrier_before_fusion": True,
            "after_barrier": "Fusion batch, then full-proof Resolver batch",
        },
        "temperatures": {
            "reviewer_1": stage.REVIEWER_1_TEMPERATURE,
            "reviewer_2": stage.REVIEWER_2_TEMPERATURE,
            "reviewer_3": stage.REVIEWER_3_TEMPERATURE,
            "trace_extractor": 0.1,
            "gap_selectors": 0.1,
            "fusion": stage.FUSION_TEMPERATURE,
            "resolver": stage.RESOLVER_TEMPERATURE,
        },
        "models": {"gemma": stage.GEMMA_MODEL, "qwen": stage.QWEN_MODEL},
        "applicable_recoveries": {
            "v0260_same_trace_continuation_min_tokens": 32_768,
            "v0261_accepting_fusion_resolver_vocabulary": True,
            "v0262_third_resolver_repetition_retry": False,
            "v0262_nonapplicability_reason": (
                "This recycle ends at Resolver-1 and does not invoke the third resolver."
            ),
        },
        "explicit_v0264_sampling_override": {
            "scope": "Qwen adversarial Reviewer 2 only",
            "primary_max_tokens": QWEN_REVIEWER2_MAX_TOKENS,
            "clean_recovery_max_tokens": list(QWEN_REVIEWER2_RECOVERY_TOKENS),
            "budget_forcing_replacement_caps": [32_768, 49_152, 65_536],
            "temperatures_changed": False,
            "prompts_changed": False,
            "seed_policy_changed": False,
        },
    }


def resolve_source_portfolio(source_run: Path) -> dict[str, Any]:
    source_run = source_run.resolve()
    phase_2 = _require_within(source_run, source_run / SOURCE_PHASE_2, "phase 2")
    summary_path = phase_2 / "summary.json"
    summary = _read_json(summary_path)
    if summary.get("state") != "completed" or int(summary.get("case_count") or 0) != 4:
        raise ValueError("source Resolver-1 stage is not a completed four-case run")
    rows = summary.get("rows")
    if not isinstance(rows, list):
        raise ValueError("source Resolver-1 summary rows are missing")
    by_id = {str(row.get("candidate_id")): row for row in rows if isinstance(row, dict)}
    if tuple(candidate for candidate in CANDIDATE_IDS if candidate not in by_id):
        raise ValueError("source Resolver-1 portfolio is incomplete")
    if set(by_id) != set(CANDIDATE_IDS):
        raise ValueError("source Resolver-1 portfolio identity drift")

    portfolio: list[dict[str, Any]] = []
    problem_paths: set[Path] = set()
    for index, candidate_id in enumerate(CANDIDATE_IDS):
        row = by_id[candidate_id]
        case_id = f"{PROBLEM_ID}.{candidate_id}"
        if row.get("case_id") != case_id or row.get("problem_id") != PROBLEM_ID:
            raise ValueError(f"source identity drift: {candidate_id}")
        handoff_path = _require_within(
            source_run,
            Path(str(row.get("resolver_trace_handoff") or "")),
            f"{candidate_id} Resolver-1 handoff",
        )
        handoff = _read_json(handoff_path)
        if (
            handoff.get("status") != "UNCERTIFIED_TRACE"
            or handoff.get("case_id") != case_id
            or handoff.get("candidate_id") != candidate_id
            or handoff.get("resolver_outcome") != row.get("resolver_outcome")
        ):
            raise ValueError(f"source Resolver-1 handoff drift: {candidate_id}")
        proof_path = _require_within(
            source_run,
            Path(str(handoff.get("proof_path") or "")),
            f"{candidate_id} Resolver-1 proof",
        )
        proof_sha256 = _text_file_sha256(proof_path)
        if (
            proof_sha256 != str(handoff.get("proof_sha256") or "")
            or proof_sha256 != EXPECTED_RESOLVER1_PROOF_SHA256[candidate_id]
        ):
            raise ValueError(f"source Resolver-1 proof hash drift: {candidate_id}")
        resolver_result_path = _require_within(
            source_run,
            Path(str(handoff.get("resolver_result_path") or "")),
            f"{candidate_id} Resolver-1 result",
        )
        if _file_sha256(resolver_result_path) != str(
            handoff.get("resolver_result_sha256") or ""
        ):
            raise ValueError(f"source Resolver-1 result hash drift: {candidate_id}")
        resolver_result = _read_json(resolver_result_path)
        task = resolver_result.get("task")
        if not isinstance(task, dict):
            raise ValueError(f"source Resolver-1 task missing: {candidate_id}")
        problem_path = _require_within(
            source_run,
            Path(str(task.get("problem_path") or "")),
            f"{candidate_id} problem",
        )
        if str(task.get("problem_sha256") or "") != EXPECTED_PROBLEM_SHA256:
            raise ValueError(f"source problem hash drift: {candidate_id}")
        problem_paths.add(problem_path)
        portfolio.append(
            {
                "proof_index": index,
                "case_id": case_id,
                "problem_id": PROBLEM_ID,
                "problem_number": PROBLEM_NUMBER,
                "candidate_id": candidate_id,
                "resolver1_outcome": row["resolver_outcome"],
                "source_proof_path": str(proof_path),
                "source_proof_sha256": proof_sha256,
                "source_resolver_result_path": str(resolver_result_path),
                "source_resolver_result_file_sha256": _file_sha256(
                    resolver_result_path
                ),
                "source_handoff_path": str(handoff_path),
                "source_handoff_file_sha256": _file_sha256(handoff_path),
            }
        )
    if len(problem_paths) != 1:
        raise ValueError("source Resolver-1 tasks do not share one problem artifact")
    problem_path = next(iter(problem_paths))
    problem_payload = _read_json(problem_path)
    problem = str(problem_payload.get("claim") or "").strip()
    if _text_sha256(problem) != EXPECTED_PROBLEM_SHA256:
        raise ValueError("source problem text hash drift")
    return {
        "source_run": str(source_run),
        "source_phase_2": str(phase_2),
        "source_summary_path": str(summary_path.resolve()),
        "source_summary_file_sha256": _file_sha256(summary_path),
        "problem_path": str(problem_path),
        "problem_sha256": EXPECTED_PROBLEM_SHA256,
        "proofs": portfolio,
    }


def _stage_file(
    source: Path,
    destination: Path,
    *,
    expected_text_sha256: str | None = None,
) -> None:
    source = source.resolve()
    if (
        expected_text_sha256 is not None
        and _text_file_sha256(source) != expected_text_sha256
    ):
        raise ValueError(f"source text hash drift before staging: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file():
        if _file_sha256(destination) != _file_sha256(source):
            raise ValueError(f"staged input drift: {destination}")
    else:
        shutil.copyfile(source, destination)
    if (
        expected_text_sha256 is not None
        and _text_file_sha256(destination) != expected_text_sha256
    ):
        raise ValueError(f"staged text hash drift: {destination}")


def stage_inputs(
    *, source: dict[str, Any], output_dir: Path
) -> tuple[Path, list[dict[str, Any]]]:
    input_dir = output_dir / "input"
    staged_problem = input_dir / "problem.json"
    _stage_file(Path(source["problem_path"]), staged_problem)
    staged_problem_payload = _read_json(staged_problem)
    staged_problem_text = str(staged_problem_payload.get("claim") or "").strip()
    if _text_sha256(staged_problem_text) != source["problem_sha256"]:
        raise ValueError("staged problem claim hash drift")
    cases: list[dict[str, Any]] = []
    for row in source["proofs"]:
        candidate_id = str(row["candidate_id"])
        staged_proof = input_dir / "resolver1_proofs" / f"{candidate_id}.md"
        _stage_file(
            Path(row["source_proof_path"]),
            staged_proof,
            expected_text_sha256=str(row["source_proof_sha256"]),
        )
        cases.append(
            {
                "case_id": row["case_id"],
                "mode": "fresh",
                "proof_index": row["proof_index"],
                "problem_path": str(staged_problem.resolve()),
                "proof_path": str(staged_proof.resolve()),
                "problem_number": PROBLEM_NUMBER,
                "problem_id": PROBLEM_ID,
                "candidate_id": candidate_id,
            }
        )
    cases_path = input_dir / "v263_raw_stage_cases.json"
    _write_immutable_json(
        cases_path,
        {
            # This is the inherited component's input adapter schema, not the
            # authority chosen for the experiment.
            "schema": "cognitive-well-v096-cases-v1",
            "source_harness_version": HARNESS_VERSION,
            "contract_authority": PARENT_HARNESS_VERSION,
            "cases": cases,
        },
    )
    return cases_path, cases


def _artifact_call(result_path: Path) -> dict[str, Any]:
    value = _read_json(result_path)
    task = value.get("task") if isinstance(value.get("task"), dict) else {}
    parsed = value.get("parsed") if isinstance(value.get("parsed"), dict) else {}
    generation = (
        value.get("final_generation")
        if isinstance(value.get("final_generation"), dict)
        else value.get("generation")
    )
    generation = generation if isinstance(generation, dict) else {}
    forcing = generation.get("v0257_budget_forcing")
    return {
        "result_path": str(result_path.resolve()),
        "result_file_sha256": _file_sha256(result_path),
        "model": task.get("model_name") or generation.get("model"),
        "endpoint": task.get("endpoint") or generation.get("endpoint"),
        "temperature": task.get("temperature"),
        "seed": task.get("seed"),
        "response_source": value.get("response_source"),
        "outcome": parsed.get("outcome"),
        "finish_reason": generation.get("finish_reason"),
        "budget_forcing_observed": isinstance(forcing, dict),
        "canonical_response": (
            forcing.get("canonical_source", "forced_same_trace_replacement") if isinstance(forcing, dict) else "primary"
        ),
        "prompt_sha256": generation.get("prompt_sha256"),
        "user_prompt_sha256": generation.get("user_prompt_sha256"),
    }


def build_inspection(output_dir: Path) -> dict[str, Any]:
    stage_dir = output_dir / "01_v263_review_fusion_resolver"
    summary = _read_json(stage_dir / "summary.json")
    if summary.get("state") != "completed":
        raise ValueError("cannot inspect an incomplete recycle stage")
    summary_rows = {
        str(row["candidate_id"]): row for row in summary.get("rows") or []
    }
    rows: list[dict[str, Any]] = []
    new_proofs: list[dict[str, Any]] = []
    for candidate_id in CANDIDATE_IDS:
        case_id = f"{PROBLEM_ID}.{candidate_id}"
        lane = stage_dir / "cases" / case_id
        review_paths = {
            "reviewer_1": lane / "reviews/reviewer_1/result.json",
            "reviewer_2": _single_path(
                list((lane / "reviews/reviewer_2_stage").rglob("result.json")),
                f"{case_id} Reviewer2 result",
            ),
            "reviewer_3": _single_path(
                list((lane / "reviews/reviewer_3_stage").rglob("result.json")),
                f"{case_id} Reviewer3 result",
            ),
        }
        fusion_path = _single_path(
            list((lane / "fusion").rglob("result.json")), f"{case_id} Fusion result"
        )
        resolver_path = _single_path(
            list((lane / "resolver").rglob("result.json")),
            f"{case_id} Resolver result",
        )
        handoff_path = lane / "resolver_trace_handoff/handoff.json"
        handoff = _read_json(handoff_path)
        proof_path = _require_within(
            output_dir,
            Path(str(handoff.get("proof_path") or "")),
            f"{case_id} recycled proof",
        )
        proof_sha256 = _text_file_sha256(proof_path)
        if proof_sha256 != str(handoff.get("proof_sha256") or ""):
            raise ValueError(f"recycled proof hash drift: {candidate_id}")
        row_summary = summary_rows[candidate_id]
        reviews: dict[str, Any] = {}
        for role, result_path in review_paths.items():
            effective_path = lane / f"effective_{role}.txt"
            route_path = lane / "enhancements" / role / "route.json"
            reviews[role] = {
                **_artifact_call(result_path),
                "effective_final_path": str(effective_path.resolve()),
                "effective_final_sha256": _text_file_sha256(effective_path),
                "effective_outcome": row_summary["reviewer_outcomes"][role][
                    "effective"
                ],
                "enhancement_route": row_summary["reviewer_outcomes"][role]["route"],
                "enhancement_record_path": (
                    str(route_path.resolve()) if route_path.is_file() else None
                ),
            }
        fusion_call = _artifact_call(fusion_path)
        resolver_call = _artifact_call(resolver_path)
        rows.append(
            {
                "case_id": case_id,
                "candidate_id": candidate_id,
                "input_proof_path": str(
                    (output_dir / "input/resolver1_proofs" / f"{candidate_id}.md").resolve()
                ),
                "input_proof_sha256": EXPECTED_RESOLVER1_PROOF_SHA256[candidate_id],
                "reviews": reviews,
                "fusion": fusion_call,
                "resolver": resolver_call,
                "output_proof_path": str(proof_path),
                "output_proof_sha256": proof_sha256,
                "resolver_trace_handoff_path": str(handoff_path.resolve()),
                "resolver_trace_status": handoff.get("status"),
            }
        )
        new_proofs.append(
            {
                "case_id": case_id,
                "candidate_id": candidate_id,
                "resolver_outcome": resolver_call["outcome"],
                "proof_path": str(proof_path),
                "proof_sha256": proof_sha256,
            }
        )
    report = {
        "schema": "cognitive-well-v0264-p5-resolver1-recycle-inspection-v1",
        "harness_version": HARNESS_VERSION,
        "contract_authority": PARENT_HARNESS_VERSION,
        "state": "completed",
        "purpose": "visible Reviewer -> Fusion -> Resolver handoff trace",
        "semantic_judgment_included": False,
        "rows": rows,
        "new_proofs": new_proofs,
    }
    _write_json(output_dir / "inspection.json", report)
    return report


def run_pipeline(
    *,
    output_dir: Path,
    source_run: Path = DEFAULT_SOURCE_RUN,
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT,
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT,
    workers_per_endpoint: int = 4,
    seed_namespace: str = DEFAULT_SEED_NAMESPACE,
    dry_run: bool = False,
    authorize_model_calls: bool = False,
) -> dict[str, Any]:
    if workers_per_endpoint < 1:
        raise ValueError("workers_per_endpoint must be positive")
    if not dry_run and not authorize_model_calls:
        raise PermissionError(
            "model execution requires explicit authorize_model_calls=True"
        )
    output_dir = output_dir.resolve()
    source_run = source_run.resolve()
    if output_dir == source_run or source_run in output_dir.parents:
        raise ValueError("output directory must not overlap the source run")
    output_dir.mkdir(parents=True, exist_ok=True)
    stage, _ = _effective_stage()
    source = resolve_source_portfolio(source_run)
    cases_path, cases = stage_inputs(source=source, output_dir=output_dir)
    contract = effective_contract()
    manifest = {
        "schema": "cognitive-well-v0264-p5-resolver1-v263-recycle-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "experiment": (
            "four P5 Resolver-1 proofs become a fresh input portfolio for the "
            "v0.3.263 three-review/Fusion/full-proof-Resolver boundary"
        ),
        "source": source,
        "staged_cases": cases,
        "effective_contract": contract,
        "runtime": {
            "gemma_endpoint": gemma_endpoint.rstrip("/"),
            "qwen_endpoint": qwen_endpoint.rstrip("/"),
            "workers_per_endpoint": workers_per_endpoint,
            "seed_namespace": seed_namespace,
        },
        "generation_inputs_exclude": [
            "reference_solution",
            "gold_score",
            "Codex_feedback",
            "v0139_proof",
        ],
        "post_resolver_audit_inside_this_cycle": False,
        "post_resolver_note": (
            "This run intentionally reproduces the v263 raw-stage boundary exactly; "
            "the new proofs are inspected and scored after the cycle."
        ),
        "qwen_reviewer2_token_policy": contract[
            "explicit_v0264_sampling_override"
        ],
    }
    _write_immutable_json(output_dir / "manifest.json", manifest)
    stage_dir = output_dir / "01_v263_review_fusion_resolver"
    downstream = stage.run(
        cases_manifest=cases_path,
        output_dir=stage_dir,
        gemma_endpoints=[gemma_endpoint.rstrip("/")],
        qwen_endpoint=qwen_endpoint.rstrip("/"),
        workers_per_endpoint=workers_per_endpoint,
        seed_namespace=seed_namespace,
        dry_run=dry_run,
        allowed_input_root=output_dir,
    )
    if dry_run:
        result = {
            "schema": "cognitive-well-v0264-p5-resolver1-recycle-dry-run-v1",
            "harness_version": HARNESS_VERSION,
            "parent_harness_version": PARENT_HARNESS_VERSION,
            "state": "dry_run_completed",
            "case_count": len(cases),
            "candidate_ids": list(CANDIDATE_IDS),
            "model_calls_performed": 0,
            "contract_authority": contract["authority"],
            "downstream": downstream,
        }
    else:
        inspection = build_inspection(output_dir)
        result = {
            "schema": "cognitive-well-v0264-p5-resolver1-recycle-summary-v1",
            "harness_version": HARNESS_VERSION,
            "parent_harness_version": PARENT_HARNESS_VERSION,
            "state": "completed",
            "case_count": len(cases),
            "candidate_ids": list(CANDIDATE_IDS),
            "contract_authority": contract["authority"],
            "downstream": downstream,
            "inspection_path": str((output_dir / "inspection.json").resolve()),
            "new_proofs": inspection["new_proofs"],
        }
    _write_json(output_dir / "summary.json", result)
    return result


__all__ = [
    "CANDIDATE_IDS",
    "DEFAULT_SOURCE_RUN",
    "EXPECTED_RESOLVER1_PROOF_SHA256",
    "build_inspection",
    "effective_contract",
    "resolve_source_portfolio",
    "run_pipeline",
    "stage_inputs",
]
