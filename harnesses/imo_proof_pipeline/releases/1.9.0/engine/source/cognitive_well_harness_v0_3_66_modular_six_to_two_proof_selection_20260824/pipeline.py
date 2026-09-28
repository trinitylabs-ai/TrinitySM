from __future__ import annotations

import concurrent.futures
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    RuntimeConfig,
    REPETITION_DETECTION,
    write_json,
)

from . import HARNESS_VERSION
from .contracts import (
    PAIR_SELECTION_SCHEMA,
    TRACK_EVIDENCE_SCHEMA,
    sha256_text,
    validate_pair_selection,
    validate_track_evidence,
)
from .prompts import (
    SELECTOR_SYSTEM_PROMPT,
    TRACK_SYSTEM_PROMPT,
    selector_user_prompt,
    track_user_prompt,
)


TRACK_MAX_TOKENS = 16_000
SELECTOR_MAX_TOKENS = 24_000
STRUCTURED_MAX_ATTEMPTS = 2
TEMPERATURE = 0.2


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def status(output_dir: Path, **values: Any) -> None:
    write_json(output_dir / "status.json", {**values, "updated_at": utc_now()})


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def structured_with_attempts(
    *,
    runtime: ModelRuntime,
    prompt: str,
    user_prompt: str,
    output_dir: Path,
    stage_prefix: str,
    schema: dict[str, Any],
    max_tokens: int,
    seed_label: str,
    validator: Callable[[dict[str, Any]], None],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for attempt in range(STRUCTURED_MAX_ATTEMPTS):
        stage = f"{stage_prefix}_{attempt}"
        try:
            record, generation = runtime.structured(
                role="gemma",
                prompt=prompt,
                user_prompt=user_prompt,
                destination=output_dir,
                stage=stage,
                schema=schema,
                temperature=TEMPERATURE,
                max_tokens=max_tokens,
                seed_label=f"{seed_label}:{attempt}",
            )
            validator(record)
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": stage,
                    "status": "accepted",
                    "finish_reason": generation["metadata"].get("finish_reason"),
                }
            )
            return record, generation, attempts
        except Exception as error:
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": stage,
                    "status": "rejected",
                    "error": f"{type(error).__name__}: {error}",
                }
            )
    raise RuntimeError(f"structured generation exhausted attempts: {attempts}")


def audit_track(
    *,
    runtime: ModelRuntime,
    problem: str,
    track: dict[str, str],
    output_dir: Path,
) -> dict[str, Any]:
    destination = output_dir / "track_evidence" / track["track_id"]
    result_path = destination / "result.json"
    if result_path.exists():
        result = _load_json_object(result_path)
        validate_track_evidence(
            result["record"],
            expected_track_id=track["track_id"],
        )
        return result
    record, generation, attempts = structured_with_attempts(
        runtime=runtime,
        prompt=TRACK_SYSTEM_PROMPT,
        user_prompt=track_user_prompt(problem=problem, track=track),
        output_dir=destination,
        stage_prefix="track_evidence",
        schema=TRACK_EVIDENCE_SCHEMA,
        max_tokens=TRACK_MAX_TOKENS,
        seed_label=f"track:{track['track_id']}",
        validator=lambda value: validate_track_evidence(
            value,
            expected_track_id=track["track_id"],
        ),
    )
    result = {
        "schema": "cognitive-well-v0.3.66-track-evidence-v1",
        "track_id": track["track_id"],
        "record": record,
        "generation": generation["metadata"],
        "attempts": attempts,
        "source_sha256": {
            "original_proof": sha256_text(track["original_proof"]),
            "fusion_diagnostic": sha256_text(track["fusion_diagnostic"]),
            "resolver_change_record": sha256_text(track["resolver_change_record"]),
            "resolved_proof": sha256_text(track["resolved_proof"]),
        },
        "completed_at": utc_now(),
    }
    write_json(result_path, result)
    return result


def select_pair_and_roles(
    *,
    runtime: ModelRuntime,
    problem: str,
    track_results: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, Any]:
    destination = output_dir / "pair_selection"
    result_path = destination / "result.json"
    records = [row["record"] for row in track_results]
    track_ids = [str(row["track_id"]) for row in records]
    if result_path.exists():
        result = _load_json_object(result_path)
        validate_pair_selection(result["selection"], track_ids=track_ids)
        return result
    selection, generation, attempts = structured_with_attempts(
        runtime=runtime,
        prompt=SELECTOR_SYSTEM_PROMPT,
        user_prompt=selector_user_prompt(problem=problem, records=records),
        output_dir=destination,
        stage_prefix="pair_selection",
        schema=PAIR_SELECTION_SCHEMA,
        max_tokens=SELECTOR_MAX_TOKENS,
        seed_label="all-15-pairs-and-roles",
        validator=lambda value: validate_pair_selection(value, track_ids=track_ids),
    )
    result = {
        "schema": "cognitive-well-v0.3.66-pair-selection-v1",
        "selection": selection,
        "generation": generation["metadata"],
        "attempts": attempts,
        "completed_at": utc_now(),
    }
    write_json(result_path, result)
    return result


def selected_version_proof(track: dict[str, str], version: str) -> str:
    if version == "ORIGINAL":
        return track["original_proof"].strip()
    if version == "RESOLVED":
        return track["resolved_proof"].strip()
    raise ValueError(f"unsupported selected version: {version}")


def materialize_downstream_input(
    *,
    run_input: dict[str, Any],
    selection: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    tracks = {row["track_id"]: row for row in run_input["tracks"]}
    candidates: list[dict[str, str]] = []
    selected_manifest: list[dict[str, str]] = []
    for role in ("anchor", "supplement"):
        selected = selection[role]
        track = tracks[selected["track_id"]]
        proof = selected_version_proof(track, selected["version"])
        candidates.append(
            {
                "candidate_id": track["track_id"],
                "role": role,
                "proof": proof,
                "non_authoritative_diagnostic": track["fusion_diagnostic"].strip(),
            }
        )
        proof_path = output_dir / "selected_proofs" / f"{role}.md"
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(proof + "\n", encoding="utf-8")
        selected_manifest.append(
            {
                "role": role,
                "track_id": track["track_id"],
                "version": selected["version"],
                "proof_sha256": sha256_text(proof),
                "proof_path": str(proof_path.resolve()),
            }
        )
    downstream = {
        "problem_id": run_input["problem_id"],
        "problem": run_input["problem"],
        "candidate_proofs": candidates,
        "synthesis_instructions": run_input["synthesis_instructions"],
        "gate": run_input["gate"],
    }
    write_json(output_dir / "selected_pair_input.json", downstream)
    write_json(
        output_dir / "selected_proofs" / "manifest.json",
        {"selected": selected_manifest},
    )
    return {"downstream_input": downstream, "selected_manifest": selected_manifest}


def build_manifest(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    runtime_config: RuntimeConfig,
    batch_size: int,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v0.3.66-modular-six-to-two-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": run_input["problem_id"],
        "problem_sha256": sha256_text(run_input["problem"]),
        "input_path": str(input_path.resolve()),
        "track_count": 6,
        "pair_count": 15,
        "topology": [
            "six_parallel_track_evidence_calls",
            "one_pair_selection_and_role_assignment_call",
            "deterministic_v065_input_materialization",
        ],
        "model": {
            "name": runtime_config.gemma_model,
            "endpoint": runtime_config.gemma_endpoint,
            "dtype": "bfloat16",
            "mtp": 4,
            "temperature": TEMPERATURE,
            "top_p": 1.0,
            "top_k": -1,
            "reasoning_effort": "max",
            "track_max_tokens": TRACK_MAX_TOKENS,
            "selector_max_tokens": SELECTOR_MAX_TOKENS,
            "batch_size": batch_size,
            "repetition_detection": REPETITION_DETECTION,
        },
        "tracks": [
            {
                "track_id": row["track_id"],
                "original_proof_sha256": sha256_text(row["original_proof"]),
                "fusion_diagnostic_sha256": sha256_text(row["fusion_diagnostic"]),
                "resolver_change_record_sha256": sha256_text(row["resolver_change_record"]),
                "resolved_proof_sha256": sha256_text(row["resolved_proof"]),
            }
            for row in run_input["tracks"]
        ],
        "structured_max_attempts": STRUCTURED_MAX_ATTEMPTS,
        "gold_scores_exposed": False,
        "reference_solution_exposed": False,
        "terra_calls": 0,
        "codex_calls": 0,
        "qwen_calls": 0,
    }


def run_pipeline(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    batch_size: int = 4,
) -> dict[str, Any]:
    if not 1 <= batch_size <= 4:
        raise ValueError("batch_size must be between 1 and 4")
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        build_manifest(
            run_input=run_input,
            input_path=input_path,
            runtime_config=runtime_config,
            batch_size=batch_size,
        ),
    )
    runtime = ModelRuntime(runtime_config)
    problem = str(run_input["problem"])
    tracks = list(run_input["tracks"])
    try:
        status(
            output_dir,
            state="running",
            stage="track_evidence",
            completed=[],
            total=6,
        )
        track_results: list[dict[str, Any]] = []
        completed: list[str] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            future_map = {
                executor.submit(
                    audit_track,
                    runtime=runtime,
                    problem=problem,
                    track=track,
                    output_dir=output_dir,
                ): track
                for track in tracks
            }
            for future in concurrent.futures.as_completed(future_map):
                track = future_map[future]
                track_results.append(future.result())
                completed.append(track["track_id"])
                status(
                    output_dir,
                    state="running",
                    stage="track_evidence",
                    completed=sorted(completed),
                    total=6,
                )
        order = {row["track_id"]: index for index, row in enumerate(tracks)}
        track_results.sort(key=lambda row: order[row["track_id"]])
        write_json(
            output_dir / "track_evidence_records.json",
            [row["record"] for row in track_results],
        )

        status(
            output_dir,
            state="running",
            stage="pair_selection_and_role_assignment",
            completed=sorted(completed),
            total=6,
        )
        selector_result = select_pair_and_roles(
            runtime=runtime,
            problem=problem,
            track_results=track_results,
            output_dir=output_dir,
        )
        materialized = materialize_downstream_input(
            run_input=run_input,
            selection=selector_result["selection"],
            output_dir=output_dir,
        )
        summary = {
            "schema": "cognitive-well-v0.3.66-modular-six-to-two-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "problem_id": run_input["problem_id"],
            "track_count": 6,
            "pair_count": 15,
            "selection": selector_result["selection"],
            "selected": materialized["selected_manifest"],
            "downstream_input_path": str(
                (output_dir / "selected_pair_input.json").resolve()
            ),
            "terra_calls": 0,
            "codex_calls": 0,
            "qwen_calls": 0,
        }
        write_json(output_dir / "summary.json", summary)
        status(
            output_dir,
            state="completed",
            stage="materialize_selected_pair",
            completed=sorted(completed),
            total=6,
            summary_path=str((output_dir / "summary.json").resolve()),
        )
        return summary
    except Exception as error:
        status(
            output_dir,
            state="failed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise

