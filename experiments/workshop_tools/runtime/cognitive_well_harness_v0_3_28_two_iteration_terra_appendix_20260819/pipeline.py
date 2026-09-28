from __future__ import annotations

import concurrent.futures
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[1]
LEGACY_V027_DIR = (
    REPO_ROOT_FOR_IMPORT
    / "cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812"
)
EXPECTED_V027_SOURCE_SHA256 = (
    "972ae75257c45dcc4197a53d28f7ae5dcb98df7e21bb931d8cdaeee93127d90d"
)
if str(LEGACY_V027_DIR) not in sys.path:
    # v0.2.7 predates package-relative imports and imports `core`/`prompts`
    # directly. Keep that frozen source intact and provide its expected path.
    sys.path.insert(0, str(LEGACY_V027_DIR))

from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812 import (
    pipeline as v027,
)
from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812.core import (
    EXECUTION_DISCIPLINE,
    FAILED_LEMMA_SCREEN_SCHEMA,
    MODEL,
    sha256,
    utc_now,
    validate_grade,
    write_json,
)
from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812.prompts import (
    dialectic_solver as v027_dialectic_solver,
    inquisitorial_grader,
)

from . import prompts
from .contracts import (
    FINAL_CANDIDATE_FAMILIES,
    FRESH_CANDIDATES_PER_ITERATION,
    GUIDED_CANDIDATES_PER_ITERATION,
    HARNESS_VERSION,
    MAX_CHILD_DEPTH,
    MAX_NEW_CHILDREN_GLOBAL,
    MAX_CONJECTURE_ITERATIONS,
    PHASE_ONE_ROUTE_COUNT,
    TERRA_MODEL,
    TERRA_SUCCESS_CONFIRMATIONS,
    global_audit_passed,
    materialize_candidate,
    phase_one_route,
    select_top_two_per_phase_one_route,
    select_top_candidates,
    unanimous_terra_success,
    validate_fixed_profile,
)
from .terra_runtime import terra_json_call
from .verification import (
    PACKAGE_DIR,
    REPO_ROOT,
    ClaimNode,
    EndpointModelEngine,
    ensure_exact_negation,
    verify_claim,
)


GLOBAL_SCHEMA = PACKAGE_DIR / "schemas" / "terra_global.schema.json"
PHASE_ONE_TERRA_SCORE_SCHEMA = PACKAGE_DIR / "schemas" / "terra_phase_one_score.schema.json"
PHASE_ONE_DIVERSITY_SCHEMA = PACKAGE_DIR / "schemas" / "terra_phase_one_diversity.schema.json"
SCREEN_COVERAGE_RECOVERY_ATTEMPTS = 2


def source_tree_sha256(directory: Path) -> str:
    rows: list[str] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {relative}\n")
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest()


def assert_frozen_v027_base() -> dict[str, str]:
    actual = source_tree_sha256(LEGACY_V027_DIR)
    if actual != EXPECTED_V027_SOURCE_SHA256:
        raise RuntimeError(
            "frozen v0.2.7 source changed: "
            f"expected {EXPECTED_V027_SOURCE_SHA256}, got {actual}"
        )
    return {
        "component": "appendix-faithful-v0.2.7-dialectic-and-hypothesis-stages",
        "source_sha256": actual,
    }


def write_or_validate_manifest(path: Path, manifest: dict[str, Any]) -> None:
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved != manifest:
            raise RuntimeError("resume manifest differs from the v0.3.28 contract")
        return
    write_json(path, manifest)


def write_progress(output_dir: Path, stage: str, **details: Any) -> None:
    write_json(
        output_dir / "progress.json",
        {"state": "running", "stage": stage, "updated_at": utc_now(), **details},
    )


def stable_seed(master_seed: int, *values: str) -> int:
    material = f"{master_seed}:" + ":".join(values)
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:8], "big") or 1


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nearest_manifest(source_dir: Path) -> Path:
    for directory in (source_dir, *source_dir.parents):
        candidate = directory / "manifest.json"
        if candidate.exists():
            return candidate
        if directory == REPO_ROOT:
            break
    raise ValueError(f"no source run manifest found above {source_dir}")


def validate_phase_one_reuse(
    *,
    problem: str,
    source_dirs: tuple[Path, ...] | None,
    width: int,
    model: str,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
    parser_max_tokens: int,
) -> list[dict[str, Any]]:
    if source_dirs is None:
        return []
    if len(source_dirs) != PHASE_ONE_ROUTE_COUNT:
        raise ValueError(
            f"Phase-1 reuse requires exactly {PHASE_ONE_ROUTE_COUNT} routes"
        )
    expected_prompt_sha256 = sha256(
        v027_dialectic_solver(problem, None) + EXECUTION_DISCIPLINE
    )
    records: list[dict[str, Any]] = []
    for route_index, source_dir in enumerate(source_dirs, start=1):
        source_dir = source_dir.resolve()
        solutions_path = source_dir / "solutions.json"
        drafts_path = source_dir / "drafts.json"
        refined_path = source_dir / "refined.json"
        regrades_path = source_dir / "regrades.json"
        for path in (solutions_path, drafts_path, refined_path, regrades_path):
            if not path.is_file():
                raise ValueError(f"incomplete Phase-1 reuse source: missing {path}")
        solutions = json.loads(solutions_path.read_text(encoding="utf-8"))
        drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
        refined = json.loads(refined_path.read_text(encoding="utf-8"))
        regrades = json.loads(regrades_path.read_text(encoding="utf-8"))
        if not all(
            isinstance(rows, list) and len(rows) == width
            for rows in (solutions, drafts, refined, regrades)
        ):
            raise ValueError(
                f"Phase-1 reuse route {route_index} is not complete width {width}"
            )
        if any(row.get("context_supplied") is not False for row in solutions):
            raise ValueError("Phase-1 reuse source is not wholly zero-context")
        if any(not str(row.get("proof") or "").strip() for row in solutions):
            raise ValueError("Phase-1 reuse source contains an empty final proof")
        draft_responses = [row.get("response") or {} for row in drafts]
        if any(
            response.get("prompt_sha256") != expected_prompt_sha256
            for response in draft_responses
        ):
            raise ValueError(
                "Phase-1 reuse prompt identity differs from the current problem "
                "or frozen v0.2.7 zero-context protocol"
            )
        if any(response.get("model") != model for response in draft_responses):
            raise ValueError("Phase-1 reuse source used a different Gemma model")
        refined_by_index = {
            int(row["index"]): str(row["proof"]) for row in refined
        }
        for index, solution in enumerate(solutions):
            if str(solution["proof"]) != refined_by_index[index]:
                raise ValueError("Phase-1 solutions do not match refined artifacts")
        manifest_path = nearest_manifest(source_dir)
        source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if source_manifest.get("source_harness") != (
            "cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812"
        ):
            raise ValueError("Phase-1 reuse source is not the frozen v0.2.7 harness")
        if source_manifest.get("model") != model:
            raise ValueError("Phase-1 source manifest has a different model")
        parameters = source_manifest.get("algorithm_parameters") or {}
        if int(parameters.get("K", -1)) != width:
            raise ValueError("Phase-1 source manifest has a different width")
        token_limits = source_manifest.get("token_limits") or {}
        expected_limits = {
            "solver": solver_max_tokens,
            "grader": grader_max_tokens,
            "lazy": lazy_max_tokens,
            "parser": parser_max_tokens,
        }
        if token_limits != expected_limits:
            raise ValueError(
                f"Phase-1 source token profile differs: {token_limits} != {expected_limits}"
            )
        records.append(
            {
                "route": route_index,
                "source_dir": str(source_dir),
                "source_manifest": str(manifest_path.resolve()),
                "source_manifest_sha256": file_sha256(manifest_path),
                "solutions_sha256": file_sha256(solutions_path),
                "drafts_sha256": file_sha256(drafts_path),
                "refined_sha256": file_sha256(refined_path),
                "regrades_sha256": file_sha256(regrades_path),
                "candidate_count": len(solutions),
                "zero_context": True,
                "expected_prompt_sha256": expected_prompt_sha256,
                "source_master_seed": source_manifest.get("master_seed"),
            }
        )
    if len({row["source_manifest_sha256"] for row in records}) != 1:
        raise ValueError("Phase-1 reuse routes must come from the same source run")
    return records


def materialize_phase_one_reuse(
    *,
    source_dirs: tuple[Path, ...],
    reuse_records: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    for route_index, source_dir in enumerate(source_dirs, start=1):
        source_path = source_dir.resolve() / "solutions.json"
        destination = output_dir / f"route_{route_index}" / "zero_context"
        write_json(
            destination / "solutions.json",
            json.loads(source_path.read_text(encoding="utf-8")),
        )
        write_json(destination / "phase_one_reuse.json", reuse_records[route_index - 1])


def _global_validator(result: dict[str, Any]) -> None:
    if result["external_information_used"] is not False:
        raise ValueError("Terra global audit violated the information firewall")
    if result["verdict"] == "pass" and not global_audit_passed(result):
        raise ValueError("passing Terra global audit contains a failed criterion")


def _phase_one_terra_score_validator(result: dict[str, Any]) -> None:
    if result["external_information_used"] is not False:
        raise ValueError("Terra Phase-1 scorer violated the information firewall")
    score = int(result["score"])
    verdict = str(result["verdict"])
    errors = list(result["errors"])
    if score == 7:
        consistent = (
            verdict == "pass"
            and result["answer_supported"] is True
            and result["complete"] is True
            and result["requires_new_math"] is False
            and result["first_break"] is None
            and not errors
        )
    elif score == 6:
        consistent = (
            verdict == "minor_slip"
            and result["answer_supported"] is True
            and result["requires_new_math"] is False
            and result["first_break"] is not None
            and bool(errors)
        )
    else:
        consistent = (
            score in {0, 1, 2, 3, 4}
            and verdict in {"fallacy", "incomplete"}
            and result["complete"] is False
            and result["first_break"] is not None
            and bool(errors)
        )
    if not consistent:
        raise ValueError("internally inconsistent Terra Phase-1 score")
    seed_value = int(result["hypothesis_seed_value"])
    sound_ideas = list(result["sound_load_bearing_ideas"])
    if seed_value == 3 and (
        result["root_characterization_plausible"] is not True or not sound_ideas
    ):
        raise ValueError(
            "maximum hypothesis-seed value requires a plausible root and sound idea"
        )
    if seed_value == 0 and sound_ideas:
        raise ValueError("zero hypothesis-seed value cannot list sound ideas")


def score_phase_one_candidates_with_terra(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> list[dict[str, Any]]:
    """Score every Phase-1 proof independently; never expose Gemma grades."""

    def score(candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate["candidate_id"])
        terra_score = terra_json_call(
            prompt=prompts.phase_one_score_prompt(
                problem=problem,
                candidate_id=candidate_id,
                proof=str(candidate["assembled_proof"]),
            ),
            schema_path=PHASE_ONE_TERRA_SCORE_SCHEMA,
            call_root=output_dir / candidate_id,
            stem="score",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=_phase_one_terra_score_validator,
        )
        return {**candidate, "phase_one_terra_score": terra_score}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        scored = list(executor.map(score, candidates))
    write_json(
        output_dir / "summary.json",
        {
            "scorer": terra_model,
            "independent_stateless_calls": True,
            "gemma_grades_visible": False,
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "phase_one_route": row.get("phase_one_route"),
                    "score": row["phase_one_terra_score"]["score"],
                    "verdict": row["phase_one_terra_score"]["verdict"],
                    "hypothesis_seed_value": row["phase_one_terra_score"][
                        "hypothesis_seed_value"
                    ],
                    "root_characterization_plausible": row[
                        "phase_one_terra_score"
                    ]["root_characterization_plausible"],
                }
                for row in scored
            ],
        },
    )
    return scored


def load_completed_phase_one_selection(
    *,
    problem: str,
    source_dir: Path,
    model: str,
    terra_model: str,
    master_seed: int,
    expected_harness_version: str = HARNESS_VERSION,
    expected_promotion_profile: str | None = None,
    expected_promotion_base: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Load only the allowlisted, gold-free artifacts of a completed selection."""

    source_dir = source_dir.resolve()
    manifest_path = source_dir / "manifest.json"
    status_path = source_dir / "status.json"
    candidates_path = source_dir / "phase1" / "merged_candidates.json"
    score_summary_path = source_dir / "phase1" / "terra_scoring" / "summary.json"
    selection_path = source_dir / "phase_one_selection_result.json"
    required = (
        manifest_path,
        status_path,
        candidates_path,
        score_summary_path,
        selection_path,
    )
    for path in required:
        if not path.is_file():
            raise ValueError(f"incomplete Phase-1 selection source: missing {path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    score_summary = json.loads(score_summary_path.read_text(encoding="utf-8"))
    selection_result = json.loads(selection_path.read_text(encoding="utf-8"))
    expected_problem_hash = hashlib.sha256(problem.encode("utf-8")).hexdigest()
    if manifest.get("harness_version") != expected_harness_version:
        raise ValueError("Phase-1 selection source uses a different harness version")
    if expected_promotion_profile is not None and manifest.get(
        "promotion_profile"
    ) != expected_promotion_profile:
        raise ValueError("Phase-1 selection source uses a different promotion profile")
    if expected_promotion_base is not None and manifest.get(
        "promotion_base"
    ) != expected_promotion_base:
        raise ValueError("Phase-1 selection source uses a different frozen promotion base")
    if manifest.get("problem_sha256") != expected_problem_hash:
        raise ValueError("Phase-1 selection source is for a different problem")
    if manifest.get("model") != model or manifest.get("terra_model") != terra_model:
        raise ValueError("Phase-1 selection source uses a different model profile")
    if int(manifest.get("master_seed", -1)) != int(master_seed):
        raise ValueError("Phase-1 selection source uses a different master seed")
    if manifest.get("stop_after_phase_one_selection") is not True:
        raise ValueError("source was not created by the Phase-1 selection boundary")
    if manifest.get("gold_or_reference_accessed") is not False:
        raise ValueError("Phase-1 source manifest violates the information firewall")
    if manifest.get("tir_enabled") is not False:
        raise ValueError("Phase-1 source unexpectedly enabled TIR")
    if status.get("state") != "completed" or status.get("stage") != "phase1_selection":
        raise ValueError("Phase-1 selection source did not complete cleanly")
    if selection_result.get("stopped_before_hypothesis_extraction") is not True:
        raise ValueError("Phase-1 source crossed the hypothesis-extraction boundary")
    if selection_result.get("gold_or_reference_accessed") is not False:
        raise ValueError("Phase-1 selection result violates the information firewall")
    if selection_result.get("tir_used") is not False:
        raise ValueError("Phase-1 selection result unexpectedly used TIR")
    if expected_promotion_profile is not None and selection_result.get(
        "promotion_profile"
    ) != expected_promotion_profile:
        raise ValueError("Phase-1 selection result uses a different promotion profile")
    if expected_promotion_base is not None and selection_result.get(
        "promotion_base"
    ) != expected_promotion_base:
        raise ValueError("Phase-1 selection result uses a different promotion base")
    if score_summary.get("scorer") != terra_model:
        raise ValueError("Phase-1 score summary uses a different Terra model")
    if score_summary.get("independent_stateless_calls") is not True:
        raise ValueError("Phase-1 scores were not independently generated")
    if score_summary.get("gemma_grades_visible") is not False:
        raise ValueError("Phase-1 Terra scorer saw Gemma grades")

    raw_candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    expected_count = PHASE_ONE_ROUTE_COUNT * 4
    if not isinstance(raw_candidates, list) or len(raw_candidates) != expected_count:
        raise ValueError(
            f"Phase-1 selection source must contain {expected_count} candidates"
        )
    candidate_ids = [str(row.get("candidate_id") or "") for row in raw_candidates]
    if len(set(candidate_ids)) != expected_count or any(not value for value in candidate_ids):
        raise ValueError("Phase-1 source has missing or duplicate candidate IDs")
    route_counts = {
        route: sum(phase_one_route(row) == route for row in raw_candidates)
        for route in range(1, PHASE_ONE_ROUTE_COUNT + 1)
    }
    if any(count != 4 for count in route_counts.values()):
        raise ValueError(f"Phase-1 source route inventory is invalid: {route_counts}")

    scored: list[dict[str, Any]] = []
    score_hashes: dict[str, str] = {}
    for candidate in raw_candidates:
        candidate_id = str(candidate["candidate_id"])
        if not str(candidate.get("assembled_proof") or "").strip():
            raise ValueError(f"Phase-1 candidate has an empty proof: {candidate_id}")
        score_path = (
            source_dir
            / "phase1"
            / "terra_scoring"
            / candidate_id
            / "score.json"
        )
        if not score_path.is_file():
            raise ValueError(f"Phase-1 candidate lacks a Terra score: {candidate_id}")
        terra_score = json.loads(score_path.read_text(encoding="utf-8"))
        _phase_one_terra_score_validator(terra_score)
        scored.append({**candidate, "phase_one_terra_score": terra_score})
        score_hashes[candidate_id] = file_sha256(score_path)

    summary_rows = list(score_summary.get("candidates") or [])
    if [str(row.get("candidate_id") or "") for row in summary_rows] != candidate_ids:
        raise ValueError("Phase-1 score summary candidate order differs from the pool")
    by_id = {str(row["candidate_id"]): row for row in scored}
    for row in summary_rows:
        candidate_id = str(row["candidate_id"])
        score = by_id[candidate_id]["phase_one_terra_score"]
        if int(row.get("score", -1)) != int(score["score"]):
            raise ValueError(f"Phase-1 score summary mismatch for {candidate_id}")

    finalists = select_top_two_per_phase_one_route(scored)
    finalist_ids = [str(row["candidate_id"]) for row in finalists]
    if list(selection_result.get("finalist_candidate_ids") or []) != finalist_ids:
        raise ValueError("saved Phase-1 finalists differ from deterministic selection")
    highest_score = max(int(row["phase_one_terra_score"]["score"]) for row in finalists)
    eligible_ids = [
        str(row["candidate_id"])
        for row in finalists
        if int(row["phase_one_terra_score"]["score"]) == highest_score
    ]
    if list(selection_result.get("eligible_anchor_candidate_ids") or []) != eligible_ids:
        raise ValueError("saved Phase-1 anchor eligibility differs from the scores")
    selected_ids = [str(value) for value in selection_result.get("selected_candidate_ids") or []]
    if len(selected_ids) != 2 or len(set(selected_ids)) != 2:
        raise ValueError("Phase-1 continuation requires exactly two selected proofs")
    if any(value not in finalist_ids for value in selected_ids):
        raise ValueError("Phase-1 selection contains a non-finalist")
    audit = selection_result.get("selection_audit") or {}
    if audit.get("external_information_used") is not False:
        raise ValueError("Phase-1 selection audit violated the information firewall")
    if str(audit.get("anchor_candidate_id") or "") != selected_ids[0]:
        raise ValueError("saved Phase-1 anchor differs from its audit")
    if str(audit.get("supplement_candidate_id") or "") != selected_ids[1]:
        raise ValueError("saved Phase-1 supplement differs from its audit")
    if selected_ids[0] not in eligible_ids:
        raise ValueError("saved Phase-1 anchor is below the highest Terra score")
    assessment_ids = [
        str(row.get("candidate_id") or "")
        for row in audit.get("candidate_assessments") or []
    ]
    if len(assessment_ids) != len(finalist_ids) or set(assessment_ids) != set(
        finalist_ids
    ):
        raise ValueError("saved Phase-1 audit did not assess every finalist exactly once")

    selection = {
        "finalists": finalists,
        "eligible_anchor_ids": eligible_ids,
        "selected": [by_id[value] for value in selected_ids],
        "audit": audit,
    }
    source_record = {
        "source_dir": str(source_dir),
        "manifest_sha256": file_sha256(manifest_path),
        "status_sha256": file_sha256(status_path),
        "merged_candidates_sha256": file_sha256(candidates_path),
        "score_summary_sha256": file_sha256(score_summary_path),
        "selection_result_sha256": file_sha256(selection_path),
        "score_sha256_by_candidate_id": score_hashes,
        "candidate_count": len(scored),
        "selected_candidate_ids": selected_ids,
        "allowlisted_files_only": True,
        "gold_or_reference_accessed": False,
        "tir_used": False,
    }
    return {"pool": scored, "selection": selection, "source_record": source_record}


def select_diversified_phase_one_candidates(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    """Keep two finalists per route, then choose an anchor and complement."""

    finalists = select_top_two_per_phase_one_route(candidates)
    finalist_ids = [str(row["candidate_id"]) for row in finalists]
    finalist_routes = {
        str(row["candidate_id"]): phase_one_route(row) for row in finalists
    }
    highest_score = max(int(row["phase_one_terra_score"]["score"]) for row in finalists)
    eligible_anchor_ids = [
        str(row["candidate_id"])
        for row in finalists
        if int(row["phase_one_terra_score"]["score"]) == highest_score
    ]
    packets = [
        {
            "candidate_id": row["candidate_id"],
            "phase_one_route": phase_one_route(row),
            "independent_terra_score": {
                key: row["phase_one_terra_score"].get(key)
                for key in (
                    "score",
                    "verdict",
                    "answer_supported",
                    "complete",
                    "first_break",
                    "summary",
                    "root_characterization_plausible",
                    "hypothesis_seed_value",
                    "sound_load_bearing_ideas",
                )
            },
            "proof": row["assembled_proof"],
        }
        for row in finalists
    ]

    def validate(result: dict[str, Any]) -> None:
        if result["external_information_used"] is not False:
            raise ValueError("Terra diversity selector violated the firewall")
        anchor_id = str(result["anchor_candidate_id"])
        supplement_id = str(result["supplement_candidate_id"])
        selected_ids = [anchor_id, supplement_id]
        if len(set(selected_ids)) != 2:
            raise ValueError("Terra selector must choose a distinct supplement")
        if any(value not in finalist_routes for value in selected_ids):
            raise ValueError("Terra diversity selector chose a non-finalist")
        if anchor_id not in eligible_anchor_ids:
            raise ValueError("Terra selector chose an anchor below the highest score")
        assessment_ids = [
            str(row["candidate_id"]) for row in result["candidate_assessments"]
        ]
        if len(assessment_ids) != len(finalist_ids) or set(assessment_ids) != set(
            finalist_ids
        ):
            raise ValueError("Terra diversity selector must assess every finalist once")
        if len(assessment_ids) != len(set(assessment_ids)):
            raise ValueError("Terra diversity selector duplicated an assessment")
        if not result["complementarity_axes"]:
            raise ValueError("Terra diversity selector supplied no substantive axis")

    audit = terra_json_call(
        prompt=prompts.phase_one_diversity_prompt(
            problem=problem,
            finalist_packets=packets,
            eligible_anchor_ids=eligible_anchor_ids,
        ),
        schema_path=PHASE_ONE_DIVERSITY_SCHEMA,
        call_root=output_dir,
        stem="selection",
        model=terra_model,
        repo_root=REPO_ROOT,
        validator=validate,
    )
    by_id = {str(row["candidate_id"]): row for row in finalists}
    selected = [
        by_id[str(audit["anchor_candidate_id"])],
        by_id[str(audit["supplement_candidate_id"])],
    ]
    return {
        "finalists": finalists,
        "eligible_anchor_ids": eligible_anchor_ids,
        "selected": selected,
        "audit": audit,
    }


def global_audit(
    *,
    problem: str,
    candidate: dict[str, Any],
    call_root: Path,
    stem: str,
    terra_model: str,
) -> dict[str, Any]:
    return terra_json_call(
        prompt=prompts.global_audit_prompt(
            problem=problem, assembled_proof=candidate["assembled_proof"]
        ),
        schema_path=GLOBAL_SCHEMA,
        call_root=call_root,
        stem=stem,
        model=terra_model,
        repo_root=REPO_ROOT,
        validator=_global_validator,
    )


def structured_body(
    *,
    engine: EndpointModelEngine,
    prompt: str,
    candidate_id: str,
    namespace: str,
    max_tokens: int,
) -> str:
    result = engine.text(
        prompt=prompt,
        namespace=namespace,
        max_tokens=max_tokens,
        temperature=0.6,
    )
    body = str(result["final"]).strip()
    if not body:
        raise ValueError("Gemma returned an empty candidate body")
    if body.startswith("```") and body.endswith("```"):
        raise ValueError("Gemma wrapped the candidate body in a Markdown code fence")
    return body


def regrade_candidate(
    *,
    problem: str,
    candidate: dict[str, Any],
    engine: EndpointModelEngine,
    namespace: str,
    max_tokens: int,
) -> dict[str, Any]:
    response = engine.grade(
        prompt=inquisitorial_grader(problem, candidate["assembled_proof"], None),
        namespace=namespace,
        max_tokens=max_tokens,
        temperature=0.1,
    )
    return validate_grade(response["parsed"])


def finalize_body(
    *,
    problem: str,
    candidate_id: str,
    family: str,
    body: str,
    memory: list[dict[str, Any]],
    repair_memory: list[dict[str, Any]] | None,
    inherited_grade: dict[str, Any] | None,
    engine: EndpointModelEngine,
    output_dir: Path,
    terra_model: str,
    max_tokens: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    initial = materialize_candidate(
        candidate_id=candidate_id, body=body, memory=memory, family=family
    )
    initial_audit = global_audit(
        problem=problem,
        candidate=initial,
        call_root=output_dir / "round_0",
        stem="global",
        terra_model=terra_model,
    )
    repaired = None
    final = initial
    final_audit = initial_audit
    if not global_audit_passed(initial_audit):
        repaired_body = structured_body(
            engine=engine,
            prompt=prompts.body_repair_prompt(
                problem=problem,
                candidate_id=candidate_id,
                family=family,
                body=initial["body"],
                appendices=initial["lemma_appendices"],
                audit=initial_audit,
                memory=repair_memory,
            ),
            candidate_id=candidate_id,
            namespace=f"{candidate_id}_body_repair",
            max_tokens=max_tokens,
        )
        repaired = materialize_candidate(
            candidate_id=candidate_id,
            body=repaired_body,
            memory=memory,
            family=family,
        )
        final = repaired
        final_audit = global_audit(
            problem=problem,
            candidate=final,
            call_root=output_dir / "round_1",
            stem="global",
            terra_model=terra_model,
        )
    grade = inherited_grade
    if repaired is not None or grade is None:
        grade = regrade_candidate(
            problem=problem,
            candidate=final,
            engine=engine,
            namespace=f"{candidate_id}_post_terra_rank_grade",
            max_tokens=max_tokens,
        )
    result = {
        **final,
        "grade": grade,
        "initial_candidate": initial,
        "initial_global_audit": initial_audit,
        "repair_invoked": repaired is not None,
        "repaired_candidate": repaired,
        "final_global_audit": final_audit,
        "terra_screen_passed": global_audit_passed(final_audit),
        "terra_confirmation_audits": [],
        "terra_unanimously_confirmed": False,
    }
    write_json(output_dir / "finalized_candidate.json", result)
    return result


def confirm_candidate(
    *,
    problem: str,
    candidate: dict[str, Any],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    if not candidate["terra_screen_passed"]:
        return candidate

    def confirm(index: int) -> dict[str, Any]:
        return global_audit(
            problem=problem,
            candidate=candidate,
            call_root=output_dir / "confirmations",
            stem=f"confirmation_{index + 1}",
            terra_model=terra_model,
        )

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=TERRA_SUCCESS_CONFIRMATIONS
    ) as executor:
        audits = list(executor.map(confirm, range(TERRA_SUCCESS_CONFIRMATIONS)))
    result = {
        **candidate,
        "terra_confirmation_audits": audits,
        "terra_unanimously_confirmed": unanimous_terra_success(audits),
    }
    write_json(output_dir / "finalized_candidate.json", result)
    return result


def confirm_ranked_until_success(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_root: Path,
    terra_model: str,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    by_id = {row["candidate_id"]: row for row in candidates}
    confirmed = None
    for candidate in select_top_candidates(candidates, len(candidates)):
        if not candidate["terra_screen_passed"]:
            continue
        checked = confirm_candidate(
            problem=problem,
            candidate=candidate,
            output_dir=output_root / candidate["candidate_id"],
            terra_model=terra_model,
        )
        by_id[candidate["candidate_id"]] = checked
        if checked["terra_unanimously_confirmed"]:
            confirmed = checked
            break
    return confirmed, [by_id[row["candidate_id"]] for row in candidates]


def run_phase_one(
    *,
    problem: str,
    engines: tuple[EndpointModelEngine, ...],
    output_dir: Path,
    width: int,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
    reuse_source_dirs: tuple[Path, ...] | None = None,
    reuse_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if reuse_source_dirs is not None:
        if not reuse_records or len(reuse_records) != PHASE_ONE_ROUTE_COUNT:
            raise ValueError(
                f"validated reuse records are required for all {PHASE_ONE_ROUTE_COUNT} routes"
            )
        materialize_phase_one_reuse(
            source_dirs=reuse_source_dirs,
            reuse_records=reuse_records,
            output_dir=output_dir,
        )

    def run_route(index: int) -> list[dict[str, Any]]:
        return v027.dialectic_solve(
            problem=problem,
            context=None,
            count=width,
            engine=engines[index],
            stage_dir=output_dir / f"route_{index + 1}" / "zero_context",
            stage_name=f"phase1_route{index + 1}",
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )

    if len(engines) != PHASE_ONE_ROUTE_COUNT:
        raise ValueError(
            f"Phase 1 requires {PHASE_ONE_ROUTE_COUNT} route-specific engines"
        )
    # Routes alternate endpoints. With two workers, each endpoint receives one
    # route at a time; the second pair starts as the first pair completes.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        routes = list(executor.map(run_route, range(PHASE_ONE_ROUTE_COUNT)))
    if any(len(rows) != width for rows in routes):
        raise RuntimeError(
            f"Phase 1 did not return width-four output on all {PHASE_ONE_ROUTE_COUNT} routes"
        )
    merged: list[dict[str, Any]] = []
    for route_index, rows in enumerate(routes, start=1):
        for row in rows:
            merged.append(
                {
                    **row,
                    "candidate_id": f"phase1.r{route_index}.{row['solution_id']}",
                    "phase_one_route": route_index,
                    "family": "phase1_zero_context",
                    "body": row["proof"],
                    "assembled_proof": row["proof"],
                    "terra_screen_passed": False,
                    "terra_unanimously_confirmed": False,
                }
            )
    write_json(output_dir / "merged_candidates.json", merged)
    return merged


def extract_iteration_hypotheses(
    *,
    problem: str,
    iteration: int,
    pool: list[dict[str, Any]],
    memory: list[dict[str, Any]],
    ledger: list[dict[str, Any]],
    engine: EndpointModelEngine,
    output_dir: Path,
    terra_model: str,
    solver_max_tokens: int,
    parser_max_tokens: int,
    completed_phase_one_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if iteration == 1:
        two_stage = (
            completed_phase_one_selection
            if completed_phase_one_selection is not None
            else select_diversified_phase_one_candidates(
                problem=problem,
                candidates=pool,
                output_dir=output_dir / "terra_diversity_selection",
                terra_model=terra_model,
            )
        )
        top = two_stage["selected"]
        finalists = two_stage["finalists"]
        eligible_anchor_ids = two_stage["eligible_anchor_ids"]
        diversity_audit = two_stage["audit"]
        selection_policy = (
            "validated_completed_phase_one_anchor_plus_supplement"
            if completed_phase_one_selection is not None
            else "terra_best_anchor_then_diversified_supplement"
        )
    else:
        top = select_top_candidates(pool, 2)
        finalists = []
        eligible_anchor_ids = []
        diversity_audit = None
        selection_policy = "global_top_two"
    write_json(
        output_dir / f"iteration{iteration}_seed_selection.json",
        {
            "policy": selection_policy,
            "finalist_candidate_ids": [row["candidate_id"] for row in finalists],
            "eligible_anchor_candidate_ids": eligible_anchor_ids,
            "candidate_ids": [row["candidate_id"] for row in top],
            "phase_one_routes": [row.get("phase_one_route") for row in top],
            "terra_scores": [
                (row.get("phase_one_terra_score") or {}).get("score") for row in top
            ],
            "diversity_audit": diversity_audit,
        },
    )
    seeds = [
        {
            "solution_id": row["candidate_id"],
            "proof": row["assembled_proof"],
            "grade": row.get("grade") or {},
        }
        for row in top
    ]
    extracted = v027.extract_hypotheses(
        problem=problem,
        seed_solutions=seeds,
        lemma_memory=memory,
        failed_lemma_memory=ledger,
        failure_context=ledger,
        engine=engine,
        stage_dir=output_dir,
        stage_name=f"iteration{iteration}_joint_hypotheses",
        solver_max_tokens=solver_max_tokens,
        parser_max_tokens=parser_max_tokens,
    )
    screened, screened_out = screen_hypotheses_with_coverage_recovery(
        problem=problem,
        hypotheses=extracted,
        failed_lemma_memory=ledger,
        engine=engine,
        stage_dir=output_dir,
        stage_name=f"iteration{iteration}_joint_hypotheses",
        parser_max_tokens=parser_max_tokens,
    )
    screened["screened_out"] = screened_out
    conjectures = list(screened.get("conjectures") or [])
    negations = list(screened.get("negations") or [])
    if len(conjectures) != len(negations) or len(conjectures) > 3:
        raise ValueError("joint extractor violated the at-most-three paired contract")
    return screened


def screen_hypotheses_with_coverage_recovery(
    *,
    problem: str,
    hypotheses: dict[str, Any],
    failed_lemma_memory: list[dict[str, Any]],
    engine: EndpointModelEngine,
    stage_dir: Path,
    stage_name: str,
    parser_max_tokens: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Preserve v0.2.7 screening, recovering only incomplete decision coverage."""

    try:
        return v027.screen_hypotheses_against_failed_memory(
            problem=problem,
            hypotheses=hypotheses,
            failed_lemma_memory=failed_lemma_memory,
            engine=engine,
            stage_dir=stage_dir,
            stage_name=stage_name,
            parser_max_tokens=parser_max_tokens,
        )
    except ValueError as error:
        initial_error = str(error)
        if not initial_error.startswith(
            "failed-lemma screen must cover candidates in order"
        ):
            raise

    conjectures = list(hypotheses.get("conjectures") or [])
    expected = list(range(len(conjectures)))
    if not conjectures or not failed_lemma_memory:
        raise RuntimeError("screen coverage recovery was invoked without screen inputs")
    schema = copy.deepcopy(FAILED_LEMMA_SCREEN_SCHEMA)
    decisions_schema = schema["properties"]["decisions"]
    decisions_schema["minItems"] = len(conjectures)
    decisions_schema["maxItems"] = len(conjectures)
    errors = [f"initial: {initial_error}"]
    recovery_rows: list[dict[str, Any]] = []
    stage_dir.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, SCREEN_COVERAGE_RECOVERY_ATTEMPTS + 1):
        audit_path = stage_dir / f"{stage_name}_coverage_retry_{attempt}.json"
        try:
            if audit_path.exists():
                audit = json.loads(audit_path.read_text(encoding="utf-8"))
            else:
                prompt = v027.failed_lemma_screen(
                    problem,
                    conjectures,
                    str(hypotheses.get("proof") or ""),
                    failed_lemma_memory,
                )
                prompt += (
                    "\n\nRECOVERY OUTPUT CONTRACT: The previous structured response "
                    f"did not cover all candidates. Return exactly {len(expected)} "
                    "decisions, in order, with candidate_index equal to "
                    f"{expected}. Do not omit a candidate even when uncertain."
                )
                audit = engine.structured(
                    prompt=prompt,
                    namespace=f"{stage_name}_coverage_retry_{attempt}",
                    schema_name=f"failed_lemma_screen_exact_{len(expected)}",
                    schema=schema,
                    max_tokens=parser_max_tokens,
                    temperature=0.1,
                )["parsed"]
                write_json(audit_path, audit)
            decisions = list(audit.get("decisions") or [])
            observed = [int(row.get("candidate_index", -1)) for row in decisions]
            if observed != expected:
                raise ValueError(f"expected candidate indices {expected}, got {observed}")
            accepted_indexes = [
                int(row["candidate_index"])
                for row in decisions
                if row["verdict"] in {"new", "repaired"}
            ]
            rejected = [
                row
                for row in decisions
                if row["verdict"] not in {"new", "repaired"}
            ]
            screened = {
                **hypotheses,
                "conjectures": [
                    conjectures[index] for index in accepted_indexes
                ],
                "negations": [
                    list(hypotheses.get("negations") or [])[index]
                    for index in accepted_indexes
                ],
                "failed_memory_screen": decisions,
                "screened_out_count": len(rejected),
                "coverage_recovery_attempt": attempt,
            }
            recovery_rows.append(
                {"attempt": attempt, "accepted": True, "observed": observed}
            )
            write_json(
                stage_dir / f"{stage_name}_coverage_recovery_summary.json",
                {
                    "initial_error": initial_error,
                    "attempts": recovery_rows,
                    "accepted_attempt": attempt,
                    "mathematical_policy_changed": False,
                },
            )
            return screened, rejected
        except Exception as error:
            message = f"attempt {attempt}: {type(error).__name__}: {error}"
            errors.append(message)
            recovery_rows.append(
                {"attempt": attempt, "accepted": False, "error": message}
            )

    write_json(
        stage_dir / f"{stage_name}_coverage_recovery_summary.json",
        {
            "initial_error": initial_error,
            "attempts": recovery_rows,
            "accepted_attempt": None,
            "mathematical_policy_changed": False,
        },
    )
    raise RuntimeError("failed-memory screen recovery exhausted: " + " | ".join(errors))


def generate_iteration_portfolio(
    *,
    problem: str,
    iteration: int,
    pool: list[dict[str, Any]],
    memory: list[dict[str, Any]],
    ledger: list[dict[str, Any]],
    engines: tuple[EndpointModelEngine, EndpointModelEngine],
    output_dir: Path,
    terra_model: str,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
) -> list[dict[str, Any]]:
    incumbent = select_top_candidates(pool, 1)[0]
    guided_context = {
        "verified_lemma_memory": memory,
        "failed_lemma_memory": ledger,
        "partial_hypothesis_progress": ledger,
        "best_prior_solution": {
            "candidate_id": incumbent["candidate_id"],
            "proof": incumbent["assembled_proof"],
        },
        "citation_policy": (
            "When using verified memory, cite it exactly as `Lemma <lemma_id>`. "
            "Do not write an appendix; the harness attaches exact proofs."
        ),
    }

    def guided() -> list[dict[str, Any]]:
        return v027.dialectic_solve(
            problem=problem,
            context=guided_context,
            count=GUIDED_CANDIDATES_PER_ITERATION,
            engine=engines[0],
            stage_dir=output_dir / "guided",
            stage_name=f"iteration{iteration}_guided",
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )

    def fresh() -> list[dict[str, Any]]:
        return v027.dialectic_solve(
            problem=problem,
            context=None,
            count=FRESH_CANDIDATES_PER_ITERATION,
            engine=engines[1],
            stage_dir=output_dir / "fresh",
            stage_name=f"iteration{iteration}_fresh",
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        guided_future = executor.submit(guided)
        fresh_future = executor.submit(fresh)
        groups = {
            "guided": guided_future.result(),
            "fresh": fresh_future.result(),
        }
    finalized: list[dict[str, Any]] = []
    for family, rows in groups.items():
        for position, row in enumerate(rows, start=1):
            candidate_id = f"I{iteration}.{family}.{position}"
            available_memory = memory if family == "guided" else []
            finalized.append(
                finalize_body(
                    problem=problem,
                    candidate_id=candidate_id,
                    family=family,
                    body=row["proof"],
                    memory=available_memory,
                    repair_memory=available_memory,
                    inherited_grade=row.get("grade"),
                    engine=engines[0] if family == "guided" else engines[1],
                    output_dir=output_dir / "finalized" / candidate_id,
                    terra_model=terra_model,
                    max_tokens=solver_max_tokens,
                )
            )
    if sum(row["family"] == "guided" for row in finalized) != 3:
        raise RuntimeError("iteration did not produce exactly three guided candidates")
    if sum(row["family"] == "fresh" for row in finalized) != 1:
        raise RuntimeError("iteration did not produce exactly one fresh candidate")
    write_json(output_dir / "portfolio.json", finalized)
    return finalized


def terminal_synthesis(
    *,
    problem: str,
    pool: list[dict[str, Any]],
    memory: list[dict[str, Any]],
    ledger: list[dict[str, Any]],
    engines: tuple[EndpointModelEngine, EndpointModelEngine],
    output_dir: Path,
    terra_model: str,
    max_tokens: int,
) -> list[dict[str, Any]]:
    incumbent = select_top_candidates(pool, 1)[0]

    def generate(index: int, family: str) -> dict[str, Any]:
        candidate_id = f"terminal.{family}"
        prior = incumbent["assembled_proof"] if family == "incumbent_plus_evidence" else None
        body = structured_body(
            engine=engines[index],
            prompt=prompts.body_synthesis_prompt(
                problem=problem,
                candidate_id=candidate_id,
                family=family,
                memory=memory,
                ledger=ledger,
                incumbent_proof=prior,
            ),
            candidate_id=candidate_id,
            namespace=f"terminal_{family}_synthesis",
            max_tokens=max_tokens,
        )
        return finalize_body(
            problem=problem,
            candidate_id=candidate_id,
            family=family,
            body=body,
            memory=memory,
            repair_memory=memory,
            inherited_grade=None,
            engine=engines[index],
            output_dir=output_dir / family,
            terra_model=terra_model,
            max_tokens=max_tokens,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(generate, index, family)
            for index, family in enumerate(FINAL_CANDIDATE_FAMILIES)
        ]
        candidates = [future.result() for future in futures]
    confirmed: list[dict[str, Any]] = []
    for candidate in candidates:
        confirmed.append(
            confirm_candidate(
                problem=problem,
                candidate=candidate,
                output_dir=output_dir / candidate["family"],
                terra_model=terra_model,
            )
        )
    write_json(output_dir / "terminal_candidates.json", confirmed)
    return confirmed


def run_harness(
    *,
    problem: str,
    output_dir: Path,
    endpoints: tuple[str, str],
    model: str = MODEL,
    terra_model: str = TERRA_MODEL,
    master_seed: int,
    phase_one_width: int = 4,
    solver_max_tokens: int = 65_536,
    grader_max_tokens: int = 65_536,
    lazy_max_tokens: int = 8_192,
    parser_max_tokens: int = 16_384,
    max_conjecture_iterations: int = MAX_CONJECTURE_ITERATIONS,
    guided_candidates: int = GUIDED_CANDIDATES_PER_ITERATION,
    fresh_candidates: int = FRESH_CANDIDATES_PER_ITERATION,
    terra_confirmations: int = TERRA_SUCCESS_CONFIRMATIONS,
    phase_one_reuse_dirs: tuple[Path, ...] | None = None,
    stop_after_phase_one_selection: bool = False,
    continue_from_phase_one_selection: Path | None = None,
    harness_version: str = HARNESS_VERSION,
    artifact_schema_version: str = "v0.3.28",
    promotion_profile: str | None = None,
    promotion_base: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_fixed_profile(
        max_conjecture_iterations=max_conjecture_iterations,
        guided_candidates=guided_candidates,
        fresh_candidates=fresh_candidates,
        terra_confirmations=terra_confirmations,
    )
    if phase_one_width != 4:
        raise ValueError("v0.3.28 preserves v0.2.7 Phase-1 width 4")
    if model != MODEL:
        raise ValueError(f"Gemma model must remain {MODEL!r}")
    if terra_model != TERRA_MODEL:
        raise ValueError(f"Terra verifier must remain {TERRA_MODEL!r}")
    if not harness_version.strip():
        raise ValueError("harness_version must be nonempty")
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", artifact_schema_version):
        raise ValueError(
            "artifact_schema_version must have the form vMAJOR.MINOR.PATCH"
        )
    if continue_from_phase_one_selection is not None and phase_one_reuse_dirs is not None:
        raise ValueError(
            "completed Phase-1 continuation and zero-context route reuse are exclusive"
        )
    if continue_from_phase_one_selection is not None and stop_after_phase_one_selection:
        raise ValueError("a Phase-1 continuation cannot stop at the same boundary")
    frozen_v027 = assert_frozen_v027_base()
    completed_phase_one = (
        load_completed_phase_one_selection(
            problem=problem,
            source_dir=continue_from_phase_one_selection,
            model=model,
            terra_model=terra_model,
            master_seed=master_seed,
            expected_harness_version=harness_version,
            expected_promotion_profile=promotion_profile,
            expected_promotion_base=promotion_base,
        )
        if continue_from_phase_one_selection is not None
        else None
    )
    phase_one_reuse = (
        []
        if completed_phase_one is not None
        else validate_phase_one_reuse(
            problem=problem,
            source_dirs=phase_one_reuse_dirs,
            width=phase_one_width,
            model=model,
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
            parser_max_tokens=parser_max_tokens,
        )
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    engines = (
        EndpointModelEngine(
            endpoint=endpoints[0],
            model=model,
            master_seed=stable_seed(master_seed, "gpu0"),
            concurrency=2,
            raw_dir=output_dir / "raw" / "gpu0",
        ),
        EndpointModelEngine(
            endpoint=endpoints[1],
            model=model,
            master_seed=stable_seed(master_seed, "gpu1"),
            concurrency=2,
            raw_dir=output_dir / "raw" / "gpu1",
        ),
    )
    phase_one_engines = tuple(
        EndpointModelEngine(
            endpoint=endpoints[(route - 1) % 2],
            model=model,
            master_seed=stable_seed(master_seed, f"phase1-route-{route}"),
            concurrency=2,
            raw_dir=output_dir / "raw" / "phase1" / f"route_{route}",
        )
        for route in range(1, PHASE_ONE_ROUTE_COUNT + 1)
    )
    manifest = {
        "schema": f"cognitive-well-{artifact_schema_version}-manifest-v1",
        "harness_version": harness_version,
        "frozen_v027_base": frozen_v027,
        "problem_sha256": hashlib.sha256(problem.encode("utf-8")).hexdigest(),
        "model": model,
        "terra_model": terra_model,
        "endpoints": list(endpoints),
        "master_seed": master_seed,
        "max_conjecture_iterations": 2,
        "guided_candidates_per_iteration": 3,
        "fresh_candidates_per_iteration": 1,
        "terra_success_confirmations": 3,
        "maximum_child_depth": MAX_CHILD_DEPTH,
        "maximum_new_children_global": MAX_NEW_CHILDREN_GLOBAL,
        "exact_negation_preflight": {
            "enabled": True,
            "maximum_gemma_repairs": 2,
            "child_full_gate_repeated_after_repair": True,
        },
        "terra_cache_identity_policy": "immutable_request_hash_variant",
        "gemma_exact_negation_repair_format": "plaintext_exact_negation_marker",
        "gemma_body_generation_format": "plaintext_no_json",
        "phase_one_width_per_route": phase_one_width,
        "phase_one_route_count": PHASE_ONE_ROUTE_COUNT,
        "phase_one_candidate_count": PHASE_ONE_ROUTE_COUNT * phase_one_width,
        "phase_one_route_scheduling": "two_endpoints_round_robin_two_worker_waves",
        "phase_two_initial_seed_selection": (
            "terra_top_two_per_route_then_best_anchor_plus_diversified_supplement"
        ),
        "phase_two_initial_seed_scorer": {
            "model": terra_model,
            "scale": "IMO_0_7_without_5",
            "independent_stateless_call_per_candidate": True,
            "gemma_grades_visible": False,
            "maximum_parallel_calls": 4,
        },
        "phase_two_diversity_selector": {
            "model": terra_model,
            "finalist_count_per_route": 2,
            "selected_count": 2,
            "anchor_criterion": "highest_independent_terra_score",
            "top_score_tie_resolution": "terra_direct_comparison",
            "supplement_criterion": "mathematical_strategy_complementarity",
            "requires_one_candidate_per_route": False,
            "gemma_grades_visible": False,
        },
        "phase_one_reuse_enabled": bool(phase_one_reuse),
        "phase_one_reuse": phase_one_reuse,
        "completed_phase_one_continuation_enabled": completed_phase_one is not None,
        "completed_phase_one_continuation": (
            completed_phase_one["source_record"]
            if completed_phase_one is not None
            else None
        ),
        "stop_after_phase_one_selection": stop_after_phase_one_selection,
        "token_limits": {
            "solver": solver_max_tokens,
            "grader": grader_max_tokens,
            "lazy": lazy_max_tokens,
            "parser": parser_max_tokens,
        },
        "gold_or_reference_accessed": False,
        "tir_enabled": False,
    }
    if promotion_profile is not None:
        manifest["promotion_profile"] = promotion_profile
    if promotion_base is not None:
        manifest["promotion_base"] = promotion_base
    write_or_validate_manifest(output_dir / "manifest.json", manifest)

    completed_phase_one_selection = None
    if completed_phase_one is not None:
        pool = list(completed_phase_one["pool"])
        completed_phase_one_selection = completed_phase_one["selection"]
        phase_one_candidate_count = len(pool)
        write_progress(
            output_dir,
            "validated_phase1_selection_continuation",
            phase_one_candidate_count=phase_one_candidate_count,
            selected_candidate_ids=[
                row["candidate_id"]
                for row in completed_phase_one_selection["selected"]
            ],
        )
    else:
        write_progress(output_dir, "phase1_zero_context")
        pool = run_phase_one(
            problem=problem,
            engines=phase_one_engines,
            output_dir=output_dir / "phase1",
            width=phase_one_width,
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
            reuse_source_dirs=phase_one_reuse_dirs,
            reuse_records=phase_one_reuse,
        )
        write_progress(
            output_dir,
            "phase1_independent_terra_scoring",
            phase_one_candidate_count=len(pool),
        )
        pool = score_phase_one_candidates_with_terra(
            problem=problem,
            candidates=pool,
            output_dir=output_dir / "phase1" / "terra_scoring",
            terra_model=terra_model,
        )
        phase_one_candidate_count = len(pool)
        if phase_one_candidate_count != PHASE_ONE_ROUTE_COUNT * phase_one_width:
            raise RuntimeError(
                f"Phase 1 produced {phase_one_candidate_count} candidates; expected "
                f"{PHASE_ONE_ROUTE_COUNT * phase_one_width}"
            )
        if stop_after_phase_one_selection:
            selection = select_diversified_phase_one_candidates(
                problem=problem,
                candidates=pool,
                output_dir=output_dir / "phase1" / "terra_diversity_selection",
                terra_model=terra_model,
            )
            result = {
                "schema": (
                    f"cognitive-well-{artifact_schema_version}-"
                    "phase1-selection-result-v1"
                ),
                "harness_version": harness_version,
                "phase_one_candidate_count": phase_one_candidate_count,
                "finalist_candidate_ids": [
                    row["candidate_id"] for row in selection["finalists"]
                ],
                "eligible_anchor_candidate_ids": selection["eligible_anchor_ids"],
                "selected_candidate_ids": [
                    row["candidate_id"] for row in selection["selected"]
                ],
                "selection_audit": selection["audit"],
                "stopped_before_hypothesis_extraction": True,
                "gold_or_reference_accessed": False,
                "tir_used": False,
            }
            if promotion_profile is not None:
                result["promotion_profile"] = promotion_profile
            if promotion_base is not None:
                result["promotion_base"] = promotion_base
            write_json(output_dir / "phase_one_selection_result.json", result)
            write_progress(
                output_dir,
                "phase1_selection_complete",
                phase_one_candidate_count=phase_one_candidate_count,
                selected_candidate_ids=result["selected_candidate_ids"],
            )
            return result
    memory: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    child_budget = {"used": 0}
    iteration_results: list[dict[str, Any]] = []
    early_stop = None

    for iteration in range(1, MAX_CONJECTURE_ITERATIONS + 1):
        iteration_root = output_dir / f"conjecture_iteration_{iteration}"
        write_progress(
            output_dir,
            "joint_hypothesis_extraction",
            iteration=iteration,
            pool_candidate_count=len(pool),
            verified_memory_count=len(memory),
            ledger_count=len(ledger),
        )
        hypotheses = extract_iteration_hypotheses(
            problem=problem,
            iteration=iteration,
            pool=pool,
            memory=memory,
            ledger=ledger,
            engine=engines[(iteration - 1) % 2],
            output_dir=iteration_root / "hypotheses",
            terra_model=terra_model,
            solver_max_tokens=solver_max_tokens,
            parser_max_tokens=parser_max_tokens,
            completed_phase_one_selection=(
                completed_phase_one_selection if iteration == 1 else None
            ),
        )
        verification_results: list[dict[str, Any]] = []
        hypothesis_pair_validations: list[dict[str, Any]] = []
        validated_negations: list[str] = []
        for index, (statement, negation) in enumerate(
            zip(hypotheses.get("conjectures") or [], hypotheses.get("negations") or []),
            start=1,
        ):
            write_progress(
                output_dir,
                "terra_hypothesis_verification",
                iteration=iteration,
                hypothesis_index=index,
                hypothesis_count=len(hypotheses.get("conjectures") or []),
                verified_memory_count=len(memory),
                ledger_count=len(ledger),
            )
            node = ClaimNode(
                node_id=f"I{iteration}.H{index}",
                statement=str(statement),
                exact_negation=str(negation),
            )
            node, pair_validation = ensure_exact_negation(
                problem=problem,
                node=node,
                engine=engines[(iteration - 1) % 2],
                call_root=(
                    iteration_root
                    / "hypotheses"
                    / "exact_negation_preflight"
                    / node.node_id
                ),
                terra_model=terra_model,
                max_tokens=parser_max_tokens,
            )
            validated_negations.append(node.exact_negation)
            hypothesis_pair_validations.append(pair_validation)
            verification_results.append(
                verify_claim(
                    problem=problem,
                    node=node,
                    memory=memory,
                    ledger=ledger,
                    engines=engines,
                    stage_root=iteration_root / "verification",
                    terra_model=terra_model,
                    max_tokens=solver_max_tokens,
                    child_budget=child_budget,
                )
            )
        hypotheses["original_negations"] = list(hypotheses.get("negations") or [])
        hypotheses["negations"] = validated_negations
        hypotheses["exact_negation_preflight"] = hypothesis_pair_validations
        write_progress(
            output_dir,
            "three_guided_plus_one_fresh_portfolio",
            iteration=iteration,
            verified_memory_count=len(memory),
            ledger_count=len(ledger),
            new_children_used=child_budget["used"],
        )
        portfolio = generate_iteration_portfolio(
            problem=problem,
            iteration=iteration,
            pool=pool,
            memory=memory,
            ledger=ledger,
            engines=engines,
            output_dir=iteration_root / "portfolio",
            terra_model=terra_model,
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )
        confirmed, portfolio = confirm_ranked_until_success(
            problem=problem,
            candidates=portfolio,
            output_root=iteration_root / "portfolio" / "finalized",
            terra_model=terra_model,
        )
        write_json(iteration_root / "portfolio" / "portfolio.json", portfolio)
        pool.extend(portfolio)
        iteration_result = {
            "iteration": iteration,
            "hypotheses": hypotheses,
            "verification_results": verification_results,
            "verified_memory_count": len(memory),
            "ledger_count": len(ledger),
            "portfolio_candidate_ids": [row["candidate_id"] for row in portfolio],
            "unanimously_confirmed_candidate_id": (
                confirmed["candidate_id"] if confirmed is not None else None
            ),
        }
        iteration_results.append(iteration_result)
        write_json(iteration_root / "iteration_result.json", iteration_result)
        if iteration == 1 and confirmed is not None:
            early_stop = {
                "after_iteration": 1,
                "reason": "three_unanimous_fresh_terra_global_passes",
                "candidate_id": confirmed["candidate_id"],
            }
            break

    write_progress(
        output_dir,
        "terminal_two_candidate_synthesis",
        iterations_completed=len(iteration_results),
        verified_memory_count=len(memory),
        ledger_count=len(ledger),
        new_children_used=child_budget["used"],
    )
    terminal = terminal_synthesis(
        problem=problem,
        pool=pool,
        memory=memory,
        ledger=ledger,
        engines=engines,
        output_dir=output_dir / "terminal_synthesis",
        terra_model=terra_model,
        max_tokens=solver_max_tokens,
    )
    passed = any(row["terra_unanimously_confirmed"] for row in terminal)
    result = {
        "schema": f"cognitive-well-{artifact_schema_version}-result-v1",
        "harness_version": harness_version,
        "frozen_v027_base": frozen_v027,
        "passed": passed,
        "iterations_completed": len(iteration_results),
        "phase_one_candidate_count": phase_one_candidate_count,
        "phase_one_reused": bool(phase_one_reuse or completed_phase_one),
        "phase_one_reuse": phase_one_reuse,
        "completed_phase_one_continuation": (
            completed_phase_one["source_record"]
            if completed_phase_one is not None
            else None
        ),
        "new_children_used": child_budget["used"],
        "early_stop": early_stop,
        "iteration_results": iteration_results,
        "verified_memory": memory,
        "failed_or_unresolved_ledger": ledger,
        "terminal_candidates": terminal,
        "final_candidate_count": len(terminal),
        "gold_or_reference_accessed": False,
        "tir_used": False,
    }
    if promotion_profile is not None:
        result["promotion_profile"] = promotion_profile
    if promotion_base is not None:
        result["promotion_base"] = promotion_base
    write_json(output_dir / "full_harness_result.json", result)
    write_json(
        output_dir / "progress.json",
        {
            "state": "completed",
            "stage": "completed",
            "passed": passed,
            "iterations_completed": len(iteration_results),
            "final_candidate_count": len(terminal),
            "updated_at": utc_now(),
        },
    )
    return result
