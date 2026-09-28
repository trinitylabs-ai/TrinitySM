from __future__ import annotations

from experiments.local_math_verifier.timeout_recovery import require_valid_fallback

import argparse
import hashlib
import json
import threading
import traceback
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
    utc_now,
    write_json,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.run import (
    CANDIDATE_ORDER,
    endpoint_models,
    merge_continuation,
)
from cognitive_well_harness_v0_3_53_fusion_20260823.protocol import (
    parse_fusion,
)
from cognitive_well_harness_v0_3_53_fusion_20260823.run import load_fusion_rows

from . import HARNESS_VERSION
from .protocol import SYSTEM_PROMPT, parse_resolution, resolver_user_prompt, sha256_text


MODEL_CONFIGS = {
    "qwen36": {
        "model": "Qwen/Qwen3.6-27B",
        "checkpoint_revision": "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9",
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 0,
        "max_model_len": 196_608,
        "default_gpu": 1,
        "default_endpoint": "http://127.0.0.1:8027/v1",
    },
    "gemma4": {
        "model": "google/gemma-4-31B-it",
        "checkpoint_revision": "842da3794eaa0b77d5f08bae87a17459d91ff475",
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "max_model_len": 262_144,
        "default_gpu": 0,
        "default_endpoint": "http://127.0.0.1:8020/v1",
    },
}
FUSION_RUN = Path(
    "runs/v053_fusion_all36_gemma4_bf16_mtp4_t04_gpu0_b4_16k_20260823_1748"
)
FUSION_SCHEMA = "cognitive-well-v053-fusion-result-v1"
FUSION_MODEL = "google/gemma-4-31B-it"
FUSION_TEMPERATURE = 0.4
FUSION_SYSTEM_PROMPT_SHA256 = (
    "df372d2903ed0c5df31b9801765c3efd1160ca2487a104b476bbc4438878ce67"
)
TEMPERATURES = (0.2, 0.4, 0.6)
PER_GPU_BATCH_SIZE = 4
MAX_OUTPUT_TOKENS = 32_000
CAP_RECOVERY_MAX_OUTPUT_TOKENS = 64_000
PROTOCOL_REPAIR_MAX_OUTPUT_TOKENS = 32_000
PROTOCOL_REPAIR_THINKING_BUDGET = 2_048
REASONING_EFFORT = "max"
TOP_P = 1.0
TOP_K = -1
RESULT_SCHEMA = "cognitive-well-v054-resolver-result-v1"
SUMMARY_SCHEMA = "cognitive-well-v054-resolver-summary-v1"
MANIFEST_SCHEMA = "cognitive-well-v054-resolver-manifest-v1"


def stable_seed(problem_number: int, candidate_id: str, proof_sha256: str) -> int:
    material = f"v054:resolver:p{problem_number}:{candidate_id}:{proof_sha256}".encode()
    value = int.from_bytes(hashlib.sha256(material).digest()[:4], "big")
    return value or 1


def _fusion_result_paths() -> list[Path]:
    return sorted((FUSION_RUN / "fusion" / "temperature_0_4").rglob("result.json"))


def load_resolver_rows() -> list[dict[str, Any]]:
    originals = {
        (int(row["problem_number"]), str(row["candidate_id"])): row
        for row in load_fusion_rows()
    }
    paths = _fusion_result_paths()
    if len(paths) != 36:
        raise ValueError(f"expected 36 frozen fusion results, found {len(paths)}")
    selected: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for path in paths:
        raw_text = path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        if payload.get("schema") != FUSION_SCHEMA:
            raise ValueError(f"wrong fusion schema: {path}")
        task = payload.get("task") or {}
        identity = payload.get("identity") or {}
        key = (int(task["problem_number"]), str(task["candidate_id"]))
        if key in seen or key not in originals:
            raise ValueError(f"duplicate or unknown fusion task: {key}")
        seen.add(key)
        if identity.get("model") != FUSION_MODEL:
            raise ValueError(f"wrong frozen fusion model for {key}")
        if float(task.get("temperature")) != FUSION_TEMPERATURE:
            raise ValueError(f"wrong frozen fusion temperature for {key}")
        if identity.get("system_prompt_sha256") != FUSION_SYSTEM_PROMPT_SHA256:
            raise ValueError(f"wrong frozen fusion prompt for {key}")
        original = originals[key]
        if task.get("proof_sha256") != original["proof_sha256"]:
            raise ValueError(f"fusion/original proof hash mismatch for {key}")
        final = str(payload.get("final") or "").strip()
        parsed = parse_fusion(final)
        if not parsed["valid"]:
            raise ValueError(f"invalid frozen fusion result for {key}: {parsed['errors']}")
        if parsed["outcome"] != "REPAIR_NEEDED":
            continue
        selected.append(
            {
                **original,
                "fusion_record": final,
                "fusion_record_sha256": sha256_text(final),
                "fusion_result_path": str(path.resolve()),
                "fusion_result_sha256": sha256_text(raw_text),
                "fusion_outcome": parsed["outcome"],
                "seed": stable_seed(key[0], key[1], original["proof_sha256"]),
            }
        )
    if len(seen) != 36 or len(selected) != 29:
        raise ValueError(
            f"frozen fusion scope changed: seen={len(seen)}, repairs={len(selected)}"
        )
    selected.sort(
        key=lambda row: (
            int(row["problem_number"]),
            CANDIDATE_ORDER.index(str(row["candidate_id"])),
        )
    )
    return selected


def build_tasks(
    rows: list[dict[str, Any]],
    *,
    model_key: str,
    gpu: int,
    endpoint: str,
    temperatures: tuple[float, ...] = TEMPERATURES,
) -> list[dict[str, Any]]:
    if model_key not in MODEL_CONFIGS:
        raise ValueError(f"unknown model key: {model_key}")
    if gpu not in (0, 1):
        raise ValueError("gpu must be 0 or 1")
    model_name = str(MODEL_CONFIGS[model_key]["model"])
    if (
        not temperatures
        or len(set(temperatures)) != len(temperatures)
        or any(value not in TEMPERATURES for value in temperatures)
    ):
        raise ValueError(f"temperatures must be a unique nonempty subset of {TEMPERATURES}")
    tasks = []
    for temperature in temperatures:
        temperature_label = f"t{int(round(temperature * 10)):02d}"
        for row in rows:
            tasks.append(
                {
                    **row,
                    "temperature": temperature,
                    "temperature_label": temperature_label,
                    "gpu": gpu,
                    "endpoint": endpoint,
                    "model_key": model_key,
                    "model_name": model_name,
                    "task_id": (
                        f"p{row['problem_number']}.{row['candidate_id']}."
                        f"{temperature_label}"
                    ),
                }
            )
    expected = 29 * len(temperatures)
    if len(tasks) != expected or len({task["task_id"] for task in tasks}) != expected:
        raise ValueError("each resolver temperature arm must contain 29 unique tasks")
    for temperature in temperatures:
        arm = [task for task in tasks if task["temperature"] == temperature]
        if len(arm) != 29:
            raise ValueError(f"temperature {temperature} does not contain 29 tasks")
    seeds: dict[tuple[int, str], set[int]] = {}
    for task in tasks:
        key = (int(task["problem_number"]), str(task["candidate_id"]))
        seeds.setdefault(key, set()).add(int(task["seed"]))
    if any(len(values) != 1 for values in seeds.values()):
        raise ValueError("temperature arms must use matched per-proof seeds")
    return tasks


def select_task_ids(
    tasks: list[dict[str, Any]], requested_task_ids: list[str] | None
) -> list[dict[str, Any]]:
    if not requested_task_ids:
        return tasks
    if len(requested_task_ids) != len(set(requested_task_ids)):
        raise ValueError("--task-id values must be unique")
    requested = set(requested_task_ids)
    available = {str(task["task_id"]) for task in tasks}
    unknown = sorted(requested - available)
    if unknown:
        raise ValueError(f"unknown or out-of-temperature --task-id values: {unknown}")
    by_id = {str(task["task_id"]): task for task in tasks}
    selected = [by_id[task_id] for task_id in requested_task_ids]
    if len(selected) != len(requested):
        raise RuntimeError("task selection count is inconsistent")
    return selected


def task_output_dir(output_dir: Path, task: dict[str, Any]) -> Path:
    return (
        output_dir
        / "resolver"
        / f"temperature_{str(task['temperature']).replace('.', '_')}"
        / f"gpu{task['gpu']}"
        / f"p{task['problem_number']}"
        / str(task["candidate_id"])
    )


def locate_parent_result(reuse_root: Path, task: dict[str, Any]) -> Path | None:
    exact = task_output_dir(reuse_root, task) / "result.json"
    if exact.is_file():
        return exact
    temperature_dir = (
        reuse_root
        / "resolver"
        / f"temperature_{str(task['temperature']).replace('.', '_')}"
    )
    matches = sorted(
        temperature_dir.glob(
            f"gpu*/p{task['problem_number']}/{task['candidate_id']}/result.json"
        )
    )
    if len(matches) > 1:
        raise RuntimeError(
            f"ambiguous reusable results for {task['task_id']}: {matches}"
        )
    return matches[0] if matches else None


def public_task(task: dict[str, Any]) -> dict[str, Any]:
    hidden = {"problem", "proof", "fusion_record", "_reuse_result_path"}
    return {key: value for key, value in task.items() if key not in hidden}


def relocation_reuse_identity_matches(
    saved_identity: Any, current_identity: dict[str, Any]
) -> bool:
    """Allow reuse across GPUs/endpoints without weakening mathematical identity."""
    if not isinstance(saved_identity, dict):
        return False
    transport_fields = {"gpu", "endpoint"}
    saved_core = {
        key: value for key, value in saved_identity.items() if key not in transport_fields
    }
    current_core = {
        key: value for key, value in current_identity.items() if key not in transport_fields
    }
    return saved_core == current_core


def _reusable_reasoning(reasoning_parts: list[str], final: str) -> str:
    parts = [
        "[Preserved model-native reasoning]\n" + part
        for part in reasoning_parts
        if part
    ]
    if final:
        parts.append("[Preserved final response fragment]\n" + final)
    return "\n\n".join(parts)


def run_task(*, output_dir: Path, task: dict[str, Any]) -> dict[str, Any]:
    destination = task_output_dir(output_dir, task)
    destination.mkdir(parents=True, exist_ok=True)
    user_prompt = resolver_user_prompt(
        problem=task["problem"],
        proof=task["proof"],
        fusion_record=task["fusion_record"],
    )
    identity = {
        **public_task(task),
        "model": task["model_name"],
        "system_prompt_sha256": sha256_text(SYSTEM_PROMPT),
        "user_prompt_sha256": sha256_text(user_prompt),
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "cap_recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "thinking_enabled": True,
        "reasoning_effort": REASONING_EFFORT,
    }
    saved_path = destination / "result.json"
    reusable_paths = [saved_path]
    if task.get("_reuse_result_path"):
        reusable_paths.append(Path(str(task["_reuse_result_path"])))
    for reusable_path in reusable_paths:
        if not reusable_path.is_file():
            continue
        saved_text = reusable_path.read_text(encoding="utf-8")
        saved = json.loads(saved_text)
        parsed = parse_resolution(str(saved.get("final") or ""))
        is_parent_reuse = reusable_path != saved_path
        identity_matches = (
            relocation_reuse_identity_matches(saved.get("identity"), identity)
            if is_parent_reuse
            else saved.get("identity") == identity
        )
        if identity_matches and parsed["valid"]:
            reused = {
                **saved,
                "parsed": parsed,
                "identity": identity,
                "task": public_task(task),
                "response_source": (
                    "reused_from_parent" if is_parent_reuse else "saved"
                ),
            }
            if is_parent_reuse:
                reused["reuse_provenance"] = {
                    "source_result_path": str(reusable_path.resolve()),
                    "source_result_sha256": sha256_text(saved_text),
                    "source_gpu": saved.get("identity", {}).get("gpu"),
                    "source_endpoint": saved.get("identity", {}).get("endpoint"),
                    "destination_gpu": identity.get("gpu"),
                    "destination_endpoint": identity.get("endpoint"),
                    "transport_fields_ignored_for_identity": ["endpoint", "gpu"],
                }
                write_json(saved_path, reused)
                (destination / "final.txt").write_text(
                    str(saved["final"]).strip() + "\n", encoding="utf-8"
                )
                if parsed["outcome"] == "RESOLVED_PROOF":
                    (destination / "resolved_proof.md").write_text(
                        str(parsed["proof"]).strip() + "\n", encoding="utf-8"
                    )
            return reused

    generated = run_openai_chat_generation(
        endpoint=str(task["endpoint"]),
        model=str(task["model_name"]),
        prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_dir=destination,
        stage="resolver",
        config=HTTPGenerationConfig(
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=float(task["temperature"]),
            top_p=TOP_P,
            top_k=TOP_K,
            seed=int(task["seed"]),
            thinking_token_budget=None,
            reasoning_effort=REASONING_EFFORT,
            timeout_seconds=14_400,
        ),
    )
    final = str(generated["text"]).strip()
    reasoning_parts = [str(generated.get("reasoning") or "").strip()]
    final_generation = generated["metadata"]
    recovery: dict[str, Any] = {"triggered": False}

    if generated["metadata"].get("finish_reason") == "length":
        reusable = _reusable_reasoning(reasoning_parts, final)
        if not reusable:
            raise RuntimeError("resolver hit its cap without reusable output")
        continued = run_openai_chat_generation(
            endpoint=str(task["endpoint"]),
            model=str(task["model_name"]),
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            prior_generation=reusable,
            continuation_instruction=(
                "Continue the same private resolution from the preserved work. Do "
                "not restart. Finish the rigorous proof and emit exactly one complete "
                "permitted Resolver record."
            ),
            output_dir=destination,
            stage="resolver_cap_continuation",
            config=HTTPGenerationConfig(
                max_tokens=CAP_RECOVERY_MAX_OUTPUT_TOKENS,
                temperature=float(task["temperature"]),
                top_p=TOP_P,
                top_k=TOP_K,
                seed=(int(task["seed"]) + 1_000_003) & 0xFFFFFFFF,
                thinking_token_budget=None,
                reasoning_effort=REASONING_EFFORT,
                timeout_seconds=14_400,
            ),
        )
        continuation = str(continued["text"]).strip()
        final = (
            continuation
            if parse_resolution(continuation)["valid"]
            else merge_continuation(final, continuation)
        )
        reasoning_parts.append(str(continued.get("reasoning") or "").strip())
        final_generation = continued["metadata"]
        recovery = {
            "triggered": True,
            "primary_max_output_tokens": MAX_OUTPUT_TOKENS,
            "recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
            "continuation_generation": continued["metadata"],
        }
        if continued["metadata"].get("finish_reason") == "length":
            raise RuntimeError("resolver exhausted continuation token cap")

    parsed = parse_resolution(final)
    require_valid_fallback(final_generation, parsed)
    if not parsed["valid"]:
        reusable = _reusable_reasoning(reasoning_parts, final)
        if not reusable:
            raise ValueError(f"invalid resolver output: {parsed['errors']}")
        repaired = run_openai_chat_generation(
            endpoint=str(task["endpoint"]),
            model=str(task["model_name"]),
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            prior_generation=reusable,
            continuation_instruction=(
                "The mathematical work is complete. Do no new mathematics. Emit the "
                "complete result as exactly one permitted Resolver record, including "
                "the entire standalone proof when the outcome is RESOLVED_PROOF."
            ),
            output_dir=destination,
            stage="resolver_protocol_repair",
            config=HTTPGenerationConfig(
                max_tokens=PROTOCOL_REPAIR_MAX_OUTPUT_TOKENS,
                temperature=float(task["temperature"]),
                top_p=TOP_P,
                top_k=TOP_K,
                seed=(int(task["seed"]) + 3_000_009) & 0xFFFFFFFF,
                thinking_token_budget=PROTOCOL_REPAIR_THINKING_BUDGET,
                reasoning_effort=None,
                timeout_seconds=14_400,
            ),
        )
        final = str(repaired["text"]).strip()
        reasoning_parts.append(str(repaired.get("reasoning") or "").strip())
        final_generation = repaired["metadata"]
        recovery["protocol_repair"] = {
            "triggered": True,
            "generation": repaired["metadata"],
            "initial_errors": parsed["errors"],
        }
        parsed = parse_resolution(final)
        require_valid_fallback(final_generation, parsed)
    if not parsed["valid"]:
        raise ValueError(f"invalid resolver output after repair: {parsed['errors']}")

    reasoning = "\n\n[CONTINUATION]\n\n".join(
        part for part in reasoning_parts if part
    )
    result = {
        "schema": RESULT_SCHEMA,
        "identity": identity,
        "task": public_task(task),
        "final": final,
        "final_sha256": sha256_text(final),
        "parsed": parsed,
        "thinking_requested": True,
        "thinking_observed": bool(reasoning),
        "reasoning_sha256": sha256_text(reasoning),
        "generation": generated["metadata"],
        "final_generation": final_generation,
        "recovery": recovery,
        "response_source": "live",
        "completed_at": utc_now(),
    }
    write_json(saved_path, result)
    (destination / "final.txt").write_text(final + "\n", encoding="utf-8")
    if parsed["outcome"] == "RESOLVED_PROOF":
        (destination / "resolved_proof.md").write_text(
            str(parsed["proof"]).strip() + "\n", encoding="utf-8"
        )
    return result


def summarize(results: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    ordered = sorted(
        results,
        key=lambda row: (
            float(row["task"]["temperature"]),
            int(row["task"]["problem_number"]),
            CANDIDATE_ORDER.index(str(row["task"]["candidate_id"])),
        ),
    )
    by_temperature: dict[str, Any] = {}
    for temperature in sorted({float(row["task"]["temperature"]) for row in ordered}):
        arm = [row for row in ordered if row["task"]["temperature"] == temperature]
        by_temperature[str(temperature)] = {
            "result_count": len(arm),
            "format_valid_count": sum(row["parsed"]["valid"] for row in arm),
            "thinking_observed_count": sum(bool(row["thinking_observed"]) for row in arm),
            "outcomes": dict(Counter(row["parsed"]["outcome"] for row in arm)),
            "resolution_modes": dict(
                Counter(
                    row["parsed"]["fields"].get("resolution_mode")
                    for row in arm
                    if row["parsed"]["outcome"] == "RESOLVED_PROOF"
                )
            ),
            "recovery_count": sum(bool(row["recovery"].get("triggered")) for row in arm),
        }
    return {
        "schema": SUMMARY_SCHEMA,
        "state": "completed",
        "completed_at": utc_now(),
        "output_dir": str(output_dir.resolve()),
        "model_key": ordered[0]["task"]["model_key"],
        "model": ordered[0]["task"]["model_name"],
        "temperatures": sorted(
            {float(row["task"]["temperature"]) for row in ordered}
        ),
        "result_count": len(ordered),
        "by_temperature": by_temperature,
        "results": ordered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve the 29 REPAIR_NEEDED outputs from frozen v0.3.53 fusion"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resolver-model", choices=tuple(MODEL_CONFIGS), required=True)
    parser.add_argument("--gpu-index", type=int, choices=(0, 1))
    parser.add_argument("--endpoint")
    parser.add_argument(
        "--temperatures",
        type=float,
        nargs="+",
        choices=TEMPERATURES,
        default=list(TEMPERATURES),
    )
    parser.add_argument("--batch-size", type=int, default=PER_GPU_BATCH_SIZE)
    parser.add_argument("--reuse-results-from", type=Path)
    parser.add_argument(
        "--task-id",
        nargs="+",
        help="Run only these exact frozen task IDs (for example p5.t07_r01.t04)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.batch_size != PER_GPU_BATCH_SIZE:
        raise ValueError(f"this frozen experiment requires batch size {PER_GPU_BATCH_SIZE}")

    config = MODEL_CONFIGS[args.resolver_model]
    gpu = int(args.gpu_index if args.gpu_index is not None else config["default_gpu"])
    endpoint = str(args.endpoint or config["default_endpoint"]).rstrip("/")
    rows = load_resolver_rows()
    temperatures = tuple(float(value) for value in args.temperatures)
    tasks = build_tasks(
        rows,
        model_key=args.resolver_model,
        gpu=gpu,
        endpoint=endpoint,
        temperatures=temperatures,
    )
    tasks = select_task_ids(tasks, args.task_id)
    if args.reuse_results_from:
        reuse_root = args.reuse_results_from.resolve()
        for task in tasks:
            reusable = locate_parent_result(reuse_root, task)
            if reusable is not None:
                task["_reuse_result_path"] = str(reusable)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest_identity = {
        "harness_version": HARNESS_VERSION,
        "model_key": args.resolver_model,
        "model": config["model"],
        "model_checkpoint_revision": config["checkpoint_revision"],
        "dtype": config["dtype"],
        "mtp_speculative_tokens": config["mtp_speculative_tokens"],
        "max_model_len": config["max_model_len"],
        "temperatures": list(temperatures),
        "top_p": TOP_P,
        "top_k": TOP_K,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "cap_recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        "thinking_enabled": True,
        "reasoning_effort": REASONING_EFFORT,
        "batch_size_per_gpu": PER_GPU_BATCH_SIZE,
        "global_concurrency": PER_GPU_BATCH_SIZE,
        "gpu": gpu,
        "endpoint": endpoint,
        "system_prompt_sha256": sha256_text(SYSTEM_PROMPT),
        "resolver_call_count": len(tasks),
        "selected_task_ids": [str(task["task_id"]) for task in tasks],
        "selected_fusion_run": str(FUSION_RUN.resolve()),
        "selected_fusion_model": FUSION_MODEL,
        "selected_fusion_temperature": FUSION_TEMPERATURE,
        "selected_fusion_system_prompt_sha256": FUSION_SYSTEM_PROMPT_SHA256,
        "selection_policy": (
            "explicit frozen task-ID subset"
            if args.task_id
            else "only the 29 frozen v0.3.53 REPAIR_NEEDED records"
        ),
        "input_policy": (
            "original problem and submitted proof once; only final v0.3.53 fusion "
            "record; no reviewer records, reviewer prompts, fusion reasoning, or raw response"
        ),
        "reference_solution_access_during_resolution": False,
        "seed_policy": (
            "matched sha256(v054,resolver,problem,candidate,proof) across models "
            "and temperatures"
        ),
        "reuse_results_from": (
            str(args.reuse_results_from.resolve()) if args.reuse_results_from else None
        ),
    }
    manifest_path = args.output_dir / "manifest.json"
    if manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("identity") != manifest_identity:
            raise ValueError("refusing to reuse output directory with another identity")
    else:
        write_json(
            manifest_path,
            {
                "schema": MANIFEST_SCHEMA,
                "created_at": utc_now(),
                "identity": manifest_identity,
                "tasks": [public_task(task) for task in tasks],
            },
        )
        (args.output_dir / "resolver_system_prompt.txt").write_text(
            SYSTEM_PROMPT + "\n", encoding="utf-8"
        )
    if args.dry_run:
        print(json.dumps(manifest_identity, indent=2))
        return

    models = endpoint_models(endpoint)
    if config["model"] not in models:
        raise RuntimeError(f"endpoint {endpoint} does not serve {config['model']}: {models}")

    completed: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    lock = threading.Lock()

    def write_status(state: str = "running") -> None:
        write_json(
            args.output_dir / "status.json",
            {
                "state": state,
                "stage": "resolver",
                "completed": [row["task"]["task_id"] for row in completed],
                "failed": failures,
                "completed_count": len(completed),
                "total": len(tasks),
                "outcomes": dict(Counter(row["parsed"]["outcome"] for row in completed)),
                "gpu": gpu,
                "updated_at": utc_now(),
            },
        )

    write_status()
    executor = ThreadPoolExecutor(
        max_workers=PER_GPU_BATCH_SIZE, thread_name_prefix=f"resolver-gpu{gpu}"
    )
    futures: dict[Future[dict[str, Any]], dict[str, Any]] = {}
    try:
        for task in tasks:
            futures[executor.submit(run_task, output_dir=args.output_dir, task=task)] = task
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                with lock:
                    completed.append(result)
                    write_status()
                if not args.quiet:
                    print(f"{task['task_id']} gpu{gpu} {result['parsed']['outcome']}")
            except Exception as error:
                failure = {
                    "task_id": task["task_id"],
                    "error": f"{type(error).__name__}: {error}",
                    "traceback": traceback.format_exc(),
                }
                with lock:
                    failures.append(failure)
                    write_status()
    finally:
        executor.shutdown(wait=True)

    if failures:
        write_status("failed")
        raise RuntimeError(f"{len(failures)} resolver calls failed")
    summary = summarize(completed, args.output_dir)
    write_json(args.output_dir / "summary.json", summary)
    write_status("completed")


if __name__ == "__main__":
    main()
