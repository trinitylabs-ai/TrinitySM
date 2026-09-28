from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import threading
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Callable, TypeVar

from experiments.local_math_verifier.runtime import utc_now, write_json

from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.runtime import (
    GEMMA_MODEL,
    RuntimeConfig,
    StageRuntime,
)
from cognitive_well_harness_v0_3_42_gemma4_dual_prompt_max_thinking_coldsolve_20260823.run import (
    BASELINE_MAX_TOKENS,
    load_control,
    nonempty_parser,
)
from cognitive_well_harness_v0_3_45_gemma4_high_stakes_no_checklist_coldsolve_20260823.run import (
    experimental_prompts,
)
from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.contracts import (
    LAZY_RESOLVE_TEMPERATURE,
)
from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.run_six_candidate_lazy_test import (
    run_lazy_check,
    run_lazy_resolve,
)
from cognitive_well_harness_v0_3_48_multi_problem_six_candidate_20260823.run import (
    CONTROL_DIR,
    load_problem as load_frozen_problem,
    stable_seed as v048_stable_seed,
)
from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823 import (
    run as reviewer_1,
)
from cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823 import (
    run as reviewer_2,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823 import (
    run as reviewer_3,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.protocol import (
    SUCCESS_TOKEN as REVIEWER_3_SUCCESS_TOKEN,
)
from cognitive_well_harness_v0_3_53_fusion_20260823 import run as fusion
from cognitive_well_harness_v0_3_54_resolver_20260823 import run as resolver
from cognitive_well_harness_v0_3_66_modular_six_to_two_proof_selection_20260824.contracts import (
    load_run_input as load_v066_input,
)

from . import HARNESS_VERSION
from .contracts import CANDIDATES, CANDIDATE_IDS, PROFILE
from .snapshot import assert_frozen_upstream


MAX_CONCURRENT = 4
GENERIC_PROBLEM_NUMBER = 0
QWEN_MODEL = "Qwen/Qwen3.6-27B"
T = TypeVar("T")


class FourSlotStageRuntime(StageRuntime):
    """Match the four active BF16/MTP4 sequences used by v0.3.48."""

    def __init__(self, config: RuntimeConfig) -> None:
        super().__init__(config)
        self._gemma_slots = threading.BoundedSemaphore(MAX_CONCURRENT)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def assert_profile_consistency() -> dict[str, Any]:
    """Prove that the packaged profile matches the imported frozen implementations."""
    runtime = RuntimeConfig()
    checks = {
        "cold_max_tokens": BASELINE_MAX_TOKENS == PROFILE["cold_generation"]["max_tokens"],
        "lazy_max_tokens": runtime.lazy_max_tokens == PROFILE["lazy_check"]["max_tokens"],
        "lazy_resolve_temperature": (
            LAZY_RESOLVE_TEMPERATURE
            == PROFILE["lazy_in_place_expansion"]["temperature"]
        ),
        "lazy_resolve_max_tokens": (
            runtime.solver_max_tokens
            == PROFILE["lazy_in_place_expansion"]["max_tokens"]
        ),
        "reviewer_1_tokens": (
            reviewer_1.MAX_OUTPUT_TOKENS,
            reviewer_1.CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        )
        == (
            PROFILE["reviewer_1"]["max_tokens"],
            PROFILE["reviewer_1"]["cap_recovery_max_tokens"],
        ),
        "reviewer_2_tokens": (
            reviewer_2.MAX_OUTPUT_TOKENS,
            reviewer_2.CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        )
        == (
            PROFILE["reviewer_2"]["max_tokens"],
            PROFILE["reviewer_2"]["cap_recovery_max_tokens"],
        ),
        "reviewer_3_tokens": (
            reviewer_3.MAX_OUTPUT_TOKENS,
            reviewer_3.CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        )
        == (
            PROFILE["reviewer_3"]["max_tokens"],
            PROFILE["reviewer_3"]["cap_recovery_max_tokens"],
        ),
        "fusion_tokens": (
            fusion._base.MAX_OUTPUT_TOKENS,
            fusion._base.CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        )
        == (
            PROFILE["fusion"]["max_tokens"],
            PROFILE["fusion"]["cap_recovery_max_tokens"],
        ),
        "resolver_tokens": (
            resolver.MAX_OUTPUT_TOKENS,
            resolver.CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        )
        == (
            PROFILE["resolver"]["max_tokens"],
            PROFILE["resolver"]["cap_recovery_max_tokens"],
        ),
        "fusion_reviewer_selection": {
            name: (row["model"], row["temperature"])
            for name, row in fusion.REVIEWER_SELECTION.items()
        }
        == {
            "reviewer_1": ("google/gemma-4-31B-it", 0.4),
            "reviewer_2": ("Qwen/Qwen3.6-27B", 0.2),
            "reviewer_3": ("google/gemma-4-31B-it", 0.2),
        },
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"packaged profile drifted from frozen upstream: {failed}")
    return checks


def _generic_seed(
    *, problem_id: str, problem_sha256: str, stage: str, candidate_id: str, salt: str
) -> int:
    material = (
        f"v067:{problem_id}:{problem_sha256}:{stage}:{candidate_id}:{salt}"
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def frozen_problem_number(run_input: dict[str, Any]) -> int | None:
    """Return the historical number only when identity and statement both match."""
    match = re.fullmatch(r"imo2026_p([1-6])", str(run_input["problem_id"]))
    if not match:
        return None
    number = int(match.group(1))
    try:
        frozen = load_frozen_problem(number)
    except (FileNotFoundError, ValueError):
        return None
    if str(frozen["claim"]).strip() != str(run_input["problem"]).strip():
        return None
    return number


def problem_number_for_artifacts(run_input: dict[str, Any]) -> int:
    return frozen_problem_number(run_input) or GENERIC_PROBLEM_NUMBER


def cold_seed(run_input: dict[str, Any], spec: dict[str, Any]) -> int:
    number = frozen_problem_number(run_input)
    if number is not None:
        return v048_stable_seed(
            number, str(spec["candidate_id"]), int(spec["seed"])
        )
    return _generic_seed(
        problem_id=str(run_input["problem_id"]),
        problem_sha256=sha256_text(str(run_input["problem"])),
        stage="cold_draft",
        candidate_id=str(spec["candidate_id"]),
        salt=str(spec["seed"]),
    )


def downstream_seed(
    run_input: dict[str, Any], *, stage: str, candidate_id: str, proof_sha256: str
) -> int:
    number = frozen_problem_number(run_input)
    if number is not None:
        if stage == "reviewer_1":
            return reviewer_1.stable_seed(number, candidate_id, proof_sha256)
        if stage == "reviewer_2":
            return reviewer_2.stable_seed(number, candidate_id, proof_sha256)
        if stage == "reviewer_3":
            return reviewer_3.stable_seed(number, candidate_id, proof_sha256)
        if stage == "fusion":
            material = f"v052:fusion:p{number}:{candidate_id}:{proof_sha256}"
            return int.from_bytes(hashlib.sha256(material.encode()).digest()[:4], "big") or 1
        if stage == "resolver":
            return resolver.stable_seed(number, candidate_id, proof_sha256)
        raise ValueError(f"unsupported stage: {stage}")
    return _generic_seed(
        problem_id=str(run_input["problem_id"]),
        problem_sha256=sha256_text(str(run_input["problem"])),
        stage=stage,
        candidate_id=candidate_id,
        salt=proof_sha256,
    )


def generalized_cold_prompts(problem: str) -> tuple[str, str, dict[str, Any]]:
    control = load_control(CONTROL_DIR)
    system_prompt, p4_user_prompt = experimental_prompts(control["system_prompt"])
    p4_claim = str(load_frozen_problem(4)["claim"])
    if p4_user_prompt.count(p4_claim) != 1:
        raise RuntimeError("frozen cold prompt has an ambiguous P4 problem block")
    prefix, suffix = p4_user_prompt.split(p4_claim, 1)
    user_prompt = prefix + problem.strip() + suffix
    if user_prompt.count(problem.strip()) != 1:
        raise ValueError("problem statement is ambiguous inside the cold user prompt")
    return system_prompt, user_prompt, {
        "control_problem": 4,
        "only_variable_region": "problem_statement",
        "system_prompt_sha256": sha256_text(system_prompt),
        "user_prompt_sha256": sha256_text(user_prompt),
        "user_static_prefix_sha256": sha256_text(prefix),
        "user_static_suffix_sha256": sha256_text(suffix),
    }


def _status(output_dir: Path, *, state: str, stage: str, **values: Any) -> None:
    write_json(
        output_dir / "status.json",
        {
            "state": state,
            "stage": stage,
            **values,
            "updated_at": utc_now(),
        },
    )


def _parallel_stage(
    *,
    output_dir: Path,
    stage: str,
    rows: list[T],
    identity: Callable[[T], str],
    worker: Callable[[T], dict[str, Any]],
) -> list[dict[str, Any]]:
    completed: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    lock = threading.Lock()
    _status(
        output_dir,
        state="running",
        stage=stage,
        completed=[],
        failed=[],
        total=len(rows),
    )
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(MAX_CONCURRENT, max(1, len(rows)))
    ) as executor:
        futures = {executor.submit(worker, row): row for row in rows}
        for future in concurrent.futures.as_completed(futures):
            source = futures[future]
            row_id = identity(source)
            try:
                completed.append(future.result())
            except Exception as error:
                failures.append(
                    {
                        "id": row_id,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            with lock:
                _status(
                    output_dir,
                    state="running",
                    stage=stage,
                    completed=sorted(
                        identity(row) if not isinstance(row, dict) else str(
                            (row.get("task") or {}).get("candidate_id")
                            or row.get("candidate_id")
                            or row.get("track_id")
                            or "completed"
                        )
                        for row in completed
                    ),
                    failed=failures,
                    total=len(rows),
                )
    if failures:
        raise RuntimeError(f"{stage} failed: {failures}")
    return completed


def run_cold_candidate(
    *,
    runtime: StageRuntime,
    run_input: dict[str, Any],
    output_dir: Path,
    system_prompt: str,
    user_prompt: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    candidate_id = str(spec["candidate_id"])
    seed = cold_seed(run_input, spec)
    candidate_dir = output_dir / "generation" / "candidates" / candidate_id
    candidate_dir.mkdir(parents=True, exist_ok=True)
    generated = runtime.gemma_call(
        output_dir=candidate_dir / "cold_generation",
        name="cold_draft",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        seed=seed,
        temperature=float(spec["temperature"]),
        max_tokens=BASELINE_MAX_TOKENS,
        parser=nonempty_parser,
    )
    proof = str(generated["text"]).strip()
    proof_path = candidate_dir / "draft_proof.md"
    proof_path.write_text(proof + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v067-cold-candidate-v1",
        "problem_id": run_input["problem_id"],
        "problem_number": problem_number_for_artifacts(run_input),
        "candidate_id": candidate_id,
        "temperature": float(spec["temperature"]),
        "seed": seed,
        "base_portfolio_seed": int(spec["seed"]),
        "proof": proof,
        "proof_sha256": sha256_text(proof),
        "proof_path": str(proof_path.resolve()),
        "cold_generation": generated,
        "completed_at": utc_now(),
    }
    write_json(candidate_dir / "cold_result.json", result)
    return result


def _proof_rows(
    run_input: dict[str, Any], checked_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {str(row["candidate_id"]): row for row in checked_rows}
    if set(by_id) != set(CANDIDATE_IDS):
        raise ValueError("checked proof set does not contain the frozen six candidates")
    rows: list[dict[str, Any]] = []
    for proof_index, candidate_id in enumerate(CANDIDATE_IDS):
        checked = by_id[candidate_id]
        proof_path = Path(str(checked["checked_proof_path"]))
        proof = proof_path.read_text(encoding="utf-8").strip()
        proof_sha = sha256_text(proof)
        if proof_sha != checked["checked_proof_sha256"]:
            raise ValueError(f"checked proof hash mismatch for {candidate_id}")
        rows.append(
            {
                "proof_index": proof_index,
                "problem_number": problem_number_for_artifacts(run_input),
                "problem_id": run_input["problem_id"],
                "candidate_id": candidate_id,
                "problem": run_input["problem"],
                "problem_sha256": sha256_text(run_input["problem"]),
                "proof": proof,
                "proof_path": str(proof_path.resolve()),
                "proof_sha256": proof_sha,
                "source_temperature": float(checked["draft_temperature"]),
            }
        )
    return rows


def build_review_task(
    *,
    run_input: dict[str, Any],
    row: dict[str, Any],
    reviewer_name: str,
    gemma_endpoint: str,
    qwen_endpoint: str,
) -> dict[str, Any]:
    configs = {
        "reviewer_1": (reviewer_1, "gemma4", GEMMA_MODEL, 0.4, 0, gemma_endpoint),
        "reviewer_2": (reviewer_2, "qwen36", QWEN_MODEL, 0.2, 1, qwen_endpoint),
        "reviewer_3": (reviewer_3, "gemma4", GEMMA_MODEL, 0.2, 0, gemma_endpoint),
    }
    if reviewer_name not in configs:
        raise ValueError(f"unknown reviewer: {reviewer_name}")
    _module, model_key, model_name, temperature, gpu, endpoint = configs[reviewer_name]
    label = f"t{int(round(temperature * 10)):02d}"
    candidate_id = str(row["candidate_id"])
    return {
        **row,
        "seed": downstream_seed(
            run_input,
            stage=reviewer_name,
            candidate_id=candidate_id,
            proof_sha256=str(row["proof_sha256"]),
        ),
        "temperature": temperature,
        "temperature_label": label,
        "gpu": gpu,
        "endpoint": endpoint.rstrip("/"),
        "model_key": model_key,
        "model_name": model_name,
        "task_id": f"{run_input['problem_id']}.{candidate_id}.{label}",
    }


def build_fusion_task(
    *,
    run_input: dict[str, Any],
    row: dict[str, Any],
    reviews: dict[str, dict[str, Any]],
    gemma_endpoint: str,
) -> dict[str, Any]:
    candidate_id = str(row["candidate_id"])
    finals = {name: str(result["final"]).strip() for name, result in reviews.items()}
    if finals["reviewer_3"] == "PROOF_CERTIFIED":
        finals["reviewer_3"] = REVIEWER_3_SUCCESS_TOKEN
    sources = {
        name: {
            "outcome": str(result["parsed"]["outcome"]),
            "model": str(result["identity"]["model"]),
            "temperature": float(result["task"]["temperature"]),
            "final_sha256": sha256_text(finals[name]),
        }
        for name, result in reviews.items()
    }
    return {
        **row,
        "reviewer_1": finals["reviewer_1"],
        "reviewer_2": finals["reviewer_2"],
        "reviewer_3": finals["reviewer_3"],
        "reviewer_sources": sources,
        "seed": downstream_seed(
            run_input,
            stage="fusion",
            candidate_id=candidate_id,
            proof_sha256=str(row["proof_sha256"]),
        ),
        "temperature": 0.4,
        "temperature_label": "t04",
        "gpu": 0,
        "endpoint": gemma_endpoint.rstrip("/"),
        "model_key": "gemma4",
        "model_name": GEMMA_MODEL,
        "task_id": f"{run_input['problem_id']}.{candidate_id}.t04",
    }


def build_resolver_task(
    *,
    run_input: dict[str, Any],
    row: dict[str, Any],
    fusion_result: dict[str, Any],
    fusion_result_path: Path,
    gemma_endpoint: str,
) -> dict[str, Any]:
    if fusion_result["parsed"]["outcome"] != "REPAIR_NEEDED":
        raise ValueError("Resolver may be invoked only for REPAIR_NEEDED")
    candidate_id = str(row["candidate_id"])
    fusion_record = str(fusion_result["final"]).strip()
    return {
        **row,
        "fusion_record": fusion_record,
        "fusion_record_sha256": sha256_text(fusion_record),
        "fusion_result_path": str(fusion_result_path.resolve()),
        "fusion_result_sha256": sha256_text(
            fusion_result_path.read_text(encoding="utf-8")
        ),
        "fusion_outcome": "REPAIR_NEEDED",
        "seed": downstream_seed(
            run_input,
            stage="resolver",
            candidate_id=candidate_id,
            proof_sha256=str(row["proof_sha256"]),
        ),
        "temperature": 0.4,
        "temperature_label": "t04",
        "gpu": 0,
        "endpoint": gemma_endpoint.rstrip("/"),
        "model_key": "gemma4",
        "model_name": GEMMA_MODEL,
        "task_id": f"{run_input['problem_id']}.{candidate_id}.t04",
    }


def compact_resolver_change(parsed: dict[str, Any]) -> str:
    fields = dict(parsed.get("fields") or {})
    outcome = str(parsed.get("outcome") or "UNKNOWN")
    if outcome == "RESOLVED_PROOF":
        mode = fields.get("resolution_mode") or "UNKNOWN"
        assessment = fields.get("fusion_assessment") or "UNKNOWN"
        summary = fields.get("change_summary") or "NONE"
    elif outcome == "ORIGINAL_PROOF_VALID":
        mode = "PASSTHROUGH_ORIGINAL_VALID"
        assessment = fields.get("fusion_assessment") or "REJECTED"
        summary = fields.get("validation_basis") or "Resolver validated the original proof."
    else:
        mode = fields.get("attempted_mode") or "RESOLUTION_FAILED"
        assessment = fields.get("fusion_assessment") or "UNRESOLVED"
        pieces = [
            fields.get("blocking_obligation"),
            fields.get("why_unresolved"),
            fields.get("useful_partial_result"),
        ]
        summary = " | ".join(str(piece) for piece in pieces if piece) or "Resolution failed."
    return "\n".join(
        [
            f"outcome: {outcome}",
            f"resolution_mode: {mode}",
            f"fusion_assessment: {assessment}",
            f"change_summary: {summary}",
        ]
    )


def passthrough_change_record(fusion_outcome: str) -> str:
    return "\n".join(
        [
            "outcome: NOT_INVOKED",
            "resolution_mode: PASSTHROUGH",
            f"fusion_assessment: {fusion_outcome}",
            (
                "change_summary: Resolver was not invoked because Fusion did not "
                "return REPAIR_NEEDED; the checked proof is preserved byte-for-byte."
            ),
        ]
    )


def materialize_v066_input(
    *,
    run_input: dict[str, Any],
    proof_rows: list[dict[str, Any]],
    fusion_results: dict[str, dict[str, Any]],
    resolver_results: dict[str, dict[str, Any]],
    output_dir: Path,
) -> dict[str, Any]:
    tracks: list[dict[str, str]] = []
    manifests: list[dict[str, Any]] = []
    by_id = {str(row["candidate_id"]): row for row in proof_rows}
    for candidate_id in CANDIDATE_IDS:
        row = by_id[candidate_id]
        original = str(row["proof"]).strip()
        fusion_result = fusion_results[candidate_id]
        fusion_record = str(fusion_result["final"]).strip()
        fusion_outcome = str(fusion_result["parsed"]["outcome"])
        resolver_result = resolver_results.get(candidate_id)
        if fusion_outcome == "REPAIR_NEEDED":
            if resolver_result is None:
                raise RuntimeError(f"missing required Resolver result for {candidate_id}")
            parsed = dict(resolver_result["parsed"])
            if parsed["outcome"] == "RESOLVED_PROOF":
                resolved = str(parsed["proof"]).strip()
            else:
                # ORIGINAL_PROOF_VALID and RESOLUTION_FAILED are explicit, honest
                # pass-throughs. v0.3.66 can still prefer the ORIGINAL version.
                resolved = original
            change_record = compact_resolver_change(parsed)
            resolver_policy = str(parsed["outcome"])
        else:
            if resolver_result is not None:
                raise RuntimeError(
                    f"Resolver result exists for non-REPAIR_NEEDED track {candidate_id}"
                )
            resolved = original
            change_record = passthrough_change_record(fusion_outcome)
            resolver_policy = "NOT_INVOKED"
        track = {
            "track_id": candidate_id,
            "original_proof": original,
            "fusion_diagnostic": fusion_record,
            "resolver_change_record": change_record,
            "resolved_proof": resolved,
        }
        tracks.append(track)
        track_dir = output_dir / "tracks" / candidate_id
        track_dir.mkdir(parents=True, exist_ok=True)
        (track_dir / "original_proof.md").write_text(original + "\n", encoding="utf-8")
        (track_dir / "fusion_diagnostic.txt").write_text(
            fusion_record + "\n", encoding="utf-8"
        )
        (track_dir / "resolver_change_record.txt").write_text(
            change_record + "\n", encoding="utf-8"
        )
        (track_dir / "resolved_proof.md").write_text(resolved + "\n", encoding="utf-8")
        manifests.append(
            {
                "track_id": candidate_id,
                "source_temperature": row["source_temperature"],
                "fusion_outcome": fusion_outcome,
                "resolver_policy": resolver_policy,
                "original_proof_sha256": sha256_text(original),
                "fusion_diagnostic_sha256": sha256_text(fusion_record),
                "resolver_change_record_sha256": sha256_text(change_record),
                "resolved_proof_sha256": sha256_text(resolved),
            }
        )
    downstream = {
        "problem_id": run_input["problem_id"],
        "problem": run_input["problem"],
        "tracks": tracks,
        "synthesis_instructions": run_input["synthesis_instructions"],
        "gate": run_input["gate"],
    }
    downstream_path = output_dir / "v066_input.json"
    write_json(downstream_path, downstream)
    # Validate with the actual consumer, including its merged gate defaults.
    load_v066_input(downstream_path)
    write_json(output_dir / "tracks" / "manifest.json", {"tracks": manifests})
    return {
        "downstream_input": downstream,
        "downstream_input_path": str(downstream_path.resolve()),
        "track_manifest": manifests,
    }


def run_pipeline(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    gemma_endpoint: str = "http://127.0.0.1:8020/v1",
    qwen_endpoint: str = "http://127.0.0.1:8027/v1",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = assert_frozen_upstream()
    profile_consistency = assert_profile_consistency()
    system_prompt, user_prompt, prompt_manifest = generalized_cold_prompts(
        str(run_input["problem"])
    )
    runtime_config = RuntimeConfig(gemma_endpoint=gemma_endpoint.rstrip("/"))
    runtime_config.validate(require_files=False)
    runtime = FourSlotStageRuntime(runtime_config)
    manifest = {
        "schema": "cognitive-well-v067-modular-six-track-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "input_path": str(input_path.resolve()),
        "problem_id": run_input["problem_id"],
        "problem_sha256": sha256_text(run_input["problem"]),
        "historical_problem_number": frozen_problem_number(run_input),
        "profile": PROFILE,
        "candidate_specs": list(CANDIDATES),
        "prompt": prompt_manifest,
        "endpoints": {
            "gemma": gemma_endpoint.rstrip("/"),
            "qwen": qwen_endpoint.rstrip("/"),
        },
        "topology": [
            "six_cold_drafts",
            "six_lazy_checks",
            "conditional_lazy_in_place_expansion",
            "three_independent_reviews_per_checked_proof",
            "strict_four_way_fusion",
            "resolver_only_for_REPAIR_NEEDED",
            "deterministic_v066_input_materialization",
        ],
        "seed_policy": (
            "historical v0.3.48-v0.3.54 seeds when an IMO 2026 identity and statement "
            "match; otherwise sha256(v067,problem,stage,candidate,proof)"
        ),
        "reference_solution_access": False,
        "gold_score_access": False,
        "frozen_upstream": snapshot,
        "profile_consistency": profile_consistency,
    }
    write_json(output_dir / "manifest.json", manifest)
    (output_dir / "cold_system_prompt.txt").write_text(
        system_prompt, encoding="utf-8"
    )
    (output_dir / "cold_user_prompt.txt").write_text(user_prompt, encoding="utf-8")

    try:
        specs = [dict(row) for row in CANDIDATES]
        cold_rows = _parallel_stage(
            output_dir=output_dir,
            stage="cold_generation",
            rows=specs,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda spec: run_cold_candidate(
                runtime=runtime,
                run_input=run_input,
                output_dir=output_dir,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                spec=spec,
            ),
        )
        cold_rows.sort(key=lambda row: CANDIDATE_IDS.index(str(row["candidate_id"])))
        lazy_rows = _parallel_stage(
            output_dir=output_dir,
            stage="lazy_check",
            rows=cold_rows,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda row: run_lazy_check(
                runtime=runtime,
                output_dir=output_dir / "generation",
                row=row,
            ),
        )
        checked_rows = _parallel_stage(
            output_dir=output_dir,
            stage="lazy_in_place_expansion",
            rows=lazy_rows,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda row: run_lazy_resolve(
                runtime=runtime,
                problem=str(run_input["problem"]),
                output_dir=output_dir / "generation",
                row=row,
            ),
        )
        proof_rows = _proof_rows(run_input, checked_rows)

        review_results: dict[str, dict[str, dict[str, Any]]] = {}
        for reviewer_name, module in (
            ("reviewer_1", reviewer_1),
            ("reviewer_2", reviewer_2),
            ("reviewer_3", reviewer_3),
        ):
            tasks = [
                build_review_task(
                    run_input=run_input,
                    row=row,
                    reviewer_name=reviewer_name,
                    gemma_endpoint=gemma_endpoint,
                    qwen_endpoint=qwen_endpoint,
                )
                for row in proof_rows
            ]
            results = _parallel_stage(
                output_dir=output_dir,
                stage=reviewer_name,
                rows=tasks,
                identity=lambda row: str(row["candidate_id"]),
                worker=lambda task, module=module, reviewer_name=reviewer_name: module.run_task(
                    output_dir=output_dir / reviewer_name,
                    task=task,
                ),
            )
            review_results[reviewer_name] = {
                str(result["task"]["candidate_id"]): result for result in results
            }

        fusion_tasks = []
        for row in proof_rows:
            candidate_id = str(row["candidate_id"])
            fusion_tasks.append(
                build_fusion_task(
                    run_input=run_input,
                    row=row,
                    reviews={
                        name: review_results[name][candidate_id]
                        for name in ("reviewer_1", "reviewer_2", "reviewer_3")
                    },
                    gemma_endpoint=gemma_endpoint,
                )
            )
        fusion_rows = _parallel_stage(
            output_dir=output_dir,
            stage="fusion",
            rows=fusion_tasks,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda task: fusion.run_task(
                output_dir=output_dir / "fusion_stage", task=task
            ),
        )
        fusion_results = {
            str(result["task"]["candidate_id"]): result for result in fusion_rows
        }

        proof_by_id = {str(row["candidate_id"]): row for row in proof_rows}
        fusion_task_by_id = {
            str(task["candidate_id"]): task for task in fusion_tasks
        }
        resolver_tasks = []
        for candidate_id in CANDIDATE_IDS:
            result = fusion_results[candidate_id]
            if result["parsed"]["outcome"] != "REPAIR_NEEDED":
                continue
            source_task = fusion_task_by_id[candidate_id]
            fusion_path = (
                fusion.task_output_dir(output_dir / "fusion_stage", source_task)
                / "result.json"
            )
            resolver_tasks.append(
                build_resolver_task(
                    run_input=run_input,
                    row=proof_by_id[candidate_id],
                    fusion_result=result,
                    fusion_result_path=fusion_path,
                    gemma_endpoint=gemma_endpoint,
                )
            )
        resolver_rows = _parallel_stage(
            output_dir=output_dir,
            stage="resolver",
            rows=resolver_tasks,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda task: resolver.run_task(
                output_dir=output_dir / "resolver_stage", task=task
            ),
        )
        resolver_results = {
            str(result["task"]["candidate_id"]): result for result in resolver_rows
        }
        materialized = materialize_v066_input(
            run_input=run_input,
            proof_rows=proof_rows,
            fusion_results=fusion_results,
            resolver_results=resolver_results,
            output_dir=output_dir,
        )
        fusion_counts = Counter(
            str(result["parsed"]["outcome"]) for result in fusion_results.values()
        )
        resolver_counts = Counter(
            str(result["parsed"]["outcome"]) for result in resolver_results.values()
        )
        summary = {
            "schema": "cognitive-well-v067-modular-six-track-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "problem_id": run_input["problem_id"],
            "candidate_count": len(proof_rows),
            "review_call_count": len(proof_rows) * 3,
            "fusion_outcomes": dict(fusion_counts),
            "resolver_invocation_count": len(resolver_tasks),
            "resolver_outcomes": dict(resolver_counts),
            "v066_input_path": materialized["downstream_input_path"],
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        _status(
            output_dir,
            state="completed",
            stage="v066_input_materialized",
            summary_path=str((output_dir / "summary.json").resolve()),
            v066_input_path=materialized["downstream_input_path"],
        )
        return summary
    except Exception as error:
        _status(
            output_dir,
            state="failed",
            stage="pipeline",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise
