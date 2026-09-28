from __future__ import annotations

import argparse
import hashlib
import json
import threading
import traceback
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
    utc_now,
    write_json,
)

from . import HARNESS_VERSION
from .protocol import SYSTEM_PROMPT, parse_review, review_user_prompt, sha256_text


MODEL_CONFIGS = {
    "qwen36": {
        "model": "Qwen/Qwen3.6-27B",
        "checkpoint_revision": "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9",
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 0,
    },
    "gemma4": {
        "model": "google/gemma-4-31B-it",
        "checkpoint_revision": "842da3794eaa0b77d5f08bae87a17459d91ff475",
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
    },
}
TEMPERATURES = (0.2, 0.4)
CANDIDATE_ORDER = (
    "t10_r01",
    "t10_r02",
    "t10_r03",
    "t10_r04",
    "t07_r01",
    "t07_r02",
)
PROBLEM_ORDER = (1, 2, 3, 4, 5, 6)
PER_GPU_BATCH_SIZE = 4
MAX_OUTPUT_TOKENS = 12_000
CAP_RECOVERY_MAX_OUTPUT_TOKENS = 24_000
TOP_P = 1.0
TOP_K = -1
PROBLEM_ROOT = Path("math_harness_inputs/imo2026_p4_p2_v0313_20260815")
P12356_RUN = Path("runs/v048_imo2026_p12356_six_lazy_20260823_021215")
P4_RUN = Path("runs/v048_imo2026_p4_six_lazy_20260823_083927")
DEFAULT_ENDPOINTS = {
    0: "http://127.0.0.1:8026/v1",
    1: "http://127.0.0.1:8027/v1",
}


def stable_seed(problem_number: int, candidate_id: str, proof_sha256: str) -> int:
    material = (
        f"v049:reviewer1:p{problem_number}:{candidate_id}:{proof_sha256}"
    ).encode("utf-8")
    value = int.from_bytes(hashlib.sha256(material).digest()[:4], "big")
    return value or 1


def merge_continuation(partial: str, continuation: str) -> str:
    partial, continuation = partial.strip(), continuation.strip()
    if not partial:
        return continuation
    if not continuation:
        return partial
    maximum = min(len(partial), len(continuation), 8_192)
    for size in range(maximum, 31, -1):
        if partial[-size:] == continuation[:size]:
            return partial + continuation[size:]
    return partial + ("" if partial.endswith((" ", "\n")) else "\n") + continuation


def source_run(problem_number: int) -> Path:
    return P4_RUN if problem_number == 4 else P12356_RUN


def load_proofs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for problem_number in PROBLEM_ORDER:
        problem_path = PROBLEM_ROOT / f"imo2026_p{problem_number}.json"
        payload = json.loads(problem_path.read_text(encoding="utf-8"))
        problem = str(payload.get("claim") or "").strip()
        if payload.get("problem_id") != f"imo2026_p{problem_number}" or not problem:
            raise ValueError(f"invalid problem payload: {problem_path}")
        for candidate_id in CANDIDATE_ORDER:
            proof_path = (
                source_run(problem_number)
                / f"p{problem_number}"
                / "candidates"
                / candidate_id
                / "checked_proof.md"
            )
            proof = proof_path.read_text(encoding="utf-8").strip()
            if not proof:
                raise ValueError(f"empty proof: {proof_path}")
            proof_sha = sha256_text(proof)
            rows.append(
                {
                    "proof_index": len(rows),
                    "problem_number": problem_number,
                    "problem_id": f"imo2026_p{problem_number}",
                    "candidate_id": candidate_id,
                    "problem": problem,
                    "problem_path": str(problem_path.resolve()),
                    "problem_sha256": sha256_text(problem),
                    "proof": proof,
                    "proof_path": str(proof_path.resolve()),
                    "proof_sha256": proof_sha,
                    "seed": stable_seed(problem_number, candidate_id, proof_sha),
                }
            )
    if len(rows) != 36:
        raise RuntimeError(f"expected 36 proofs, found {len(rows)}")
    return rows


def build_tasks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for row in rows:
        for temperature_index, temperature in enumerate(TEMPERATURES):
            gpu = (int(row["proof_index"]) + temperature_index) % 2
            label = f"t{int(round(temperature * 10)):02d}"
            tasks.append(
                {
                    **row,
                    "temperature": temperature,
                    "temperature_label": label,
                    "gpu": gpu,
                    "endpoint": DEFAULT_ENDPOINTS[gpu],
                    "task_id": (
                        f"p{row['problem_number']}.{row['candidate_id']}.{label}"
                    ),
                }
            )
    validate_assignment(tasks)
    return tasks


def validate_assignment(tasks: list[dict[str, Any]]) -> None:
    if len(tasks) != 72 or len({row["task_id"] for row in tasks}) != 72:
        raise ValueError("the experiment must contain exactly 72 unique tasks")
    counts = Counter((row["gpu"], row["temperature"]) for row in tasks)
    expected = {
        (0, 0.2): 18,
        (0, 0.4): 18,
        (1, 0.2): 18,
        (1, 0.4): 18,
    }
    if counts != expected:
        raise ValueError(f"unbalanced GPU/temperature assignment: {counts}")
    paired: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        paired[(int(task["problem_number"]), str(task["candidate_id"]))].append(task)
    for key, pair in paired.items():
        if len(pair) != 2 or {row["gpu"] for row in pair} != {0, 1}:
            raise ValueError(f"temperature pair is not crossed across GPUs: {key}")
        if len({row["seed"] for row in pair}) != 1:
            raise ValueError(f"temperature pair does not share one seed: {key}")


def endpoint_models(endpoint: str) -> list[str]:
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/models",
        headers={"Authorization": "Bearer EMPTY"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [str(row.get("id")) for row in payload.get("data") or []]


def task_output_dir(output_dir: Path, task: dict[str, Any]) -> Path:
    return (
        output_dir
        / "reviews"
        / f"temperature_{str(task['temperature']).replace('.', '_')}"
        / f"gpu{task['gpu']}"
        / f"p{task['problem_number']}"
        / str(task["candidate_id"])
    )


def public_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in task.items()
        if key not in {"problem", "proof"}
    }


def run_task(*, output_dir: Path, task: dict[str, Any]) -> dict[str, Any]:
    destination = task_output_dir(output_dir, task)
    destination.mkdir(parents=True, exist_ok=True)
    user_prompt = review_user_prompt(problem=task["problem"], proof=task["proof"])
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
    }
    saved_path = destination / "result.json"
    if saved_path.is_file():
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        parsed = parse_review(str(saved.get("final") or ""))
        if saved.get("identity") == identity and parsed["valid"]:
            return {**saved, "response_source": "saved"}

    primary_config = HTTPGenerationConfig(
        max_tokens=MAX_OUTPUT_TOKENS,
        temperature=float(task["temperature"]),
        top_p=TOP_P,
        top_k=TOP_K,
        seed=int(task["seed"]),
        thinking_token_budget=None,
        reasoning_effort=None,
        timeout_seconds=14_400,
    )
    generated = run_openai_chat_generation(
        endpoint=str(task["endpoint"]),
        model=str(task["model_name"]),
        prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_dir=destination,
        stage="reviewer1",
        config=primary_config,
    )
    final = str(generated["text"]).strip()
    reasoning_parts = [str(generated.get("reasoning") or "").strip()]
    final_generation = generated["metadata"]
    cap_recovery: dict[str, Any] = {"triggered": False}
    if generated["metadata"].get("finish_reason") == "length":
        reusable_parts = []
        if reasoning_parts[0]:
            reusable_parts.append(
                "[Preserved model-native reasoning]\n" + reasoning_parts[0]
            )
        if final:
            reusable_parts.append("[Preserved final response fragment]\n" + final)
        reusable = "\n\n".join(reusable_parts)
        if not reusable:
            raise RuntimeError("review hit its primary cap without reusable output")
        recovery = run_openai_chat_generation(
            endpoint=str(task["endpoint"]),
            model=str(task["model_name"]),
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            prior_generation=reusable,
            continuation_instruction=(
                "Continue the same private proof audit from the preserved reasoning. "
                "Do not restart. Finish the reasoning and then emit exactly the required "
                "FIRST_BREAK or NO_FIRST_BREAK final form."
            ),
            output_dir=destination,
            stage="reviewer1_cap_continuation",
            config=HTTPGenerationConfig(
                max_tokens=CAP_RECOVERY_MAX_OUTPUT_TOKENS,
                temperature=float(task["temperature"]),
                top_p=TOP_P,
                top_k=TOP_K,
                seed=(int(task["seed"]) + 1_000_003) & 0xFFFFFFFF,
                thinking_token_budget=None,
                reasoning_effort=None,
                timeout_seconds=14_400,
            ),
        )
        continuation = str(recovery["text"]).strip()
        # A model may restart and emit a complete protocol record even when asked
        # to continue. Prefer that self-contained valid record; concatenating it
        # to a truncated protocol prefix would create two FIRST_BREAK headers.
        continuation_parsed = parse_review(continuation)
        if continuation_parsed["valid"]:
            final = continuation
        else:
            final = merge_continuation(final, continuation)
        reasoning_parts.append(str(recovery.get("reasoning") or "").strip())
        final_generation = recovery["metadata"]
        cap_recovery = {
            "triggered": True,
            "primary_max_output_tokens": MAX_OUTPUT_TOKENS,
            "recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
            "reused_partial_generation": True,
            "reusable_sha256": sha256_text(reusable),
            "continuation_sha256": sha256_text(continuation),
            "recovery_generation": recovery["metadata"],
        }
        if recovery["metadata"].get("finish_reason") == "length":
            raise RuntimeError("review exhausted both primary and recovery token caps")
    parsed = parse_review(final)
    if not parsed["valid"]:
        raise ValueError(f"invalid Reviewer 1 output: {parsed['errors']}")
    reasoning = "\n\n[CAP CONTINUATION]\n\n".join(
        part for part in reasoning_parts if part
    )
    result = {
        "schema": "cognitive-well-v049-reviewer1-result-v1",
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
        "cap_recovery": cap_recovery,
        "response_source": "live",
        "completed_at": utc_now(),
    }
    write_json(saved_path, result)
    (destination / "final.txt").write_text(final + "\n", encoding="utf-8")
    return result


def summarize(results: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    ordered = sorted(
        results,
        key=lambda row: (
            int(row["task"]["problem_number"]),
            CANDIDATE_ORDER.index(str(row["task"]["candidate_id"])),
            float(row["task"]["temperature"]),
        ),
    )
    by_temperature: dict[str, Any] = {}
    for temperature in TEMPERATURES:
        subset = [row for row in ordered if row["task"]["temperature"] == temperature]
        outcomes = Counter(row["parsed"]["outcome"] for row in subset)
        completion_tokens = []
        for row in subset:
            primary_tokens = int(
                row["generation"].get("usage", {}).get("completion_tokens") or 0
            )
            recovery_tokens = int(
                row.get("cap_recovery", {})
                .get("recovery_generation", {})
                .get("usage", {})
                .get("completion_tokens")
                or 0
            )
            completion_tokens.append(primary_tokens + recovery_tokens)
        by_temperature[str(temperature)] = {
            "count": len(subset),
            "outcomes": dict(outcomes),
            "thinking_observed_count": sum(bool(row["thinking_observed"]) for row in subset),
            "cap_recovery_count": sum(
                bool(row.get("cap_recovery", {}).get("triggered")) for row in subset
            ),
            "mean_completion_tokens": sum(completion_tokens) / len(completion_tokens),
        }
    by_gpu = {
        str(gpu): {
            "count": sum(row["task"]["gpu"] == gpu for row in ordered),
            "temperature_0.2_count": sum(
                row["task"]["gpu"] == gpu and row["task"]["temperature"] == 0.2
                for row in ordered
            ),
            "temperature_0.4_count": sum(
                row["task"]["gpu"] == gpu and row["task"]["temperature"] == 0.4
                for row in ordered
            ),
        }
        for gpu in (0, 1)
    }
    pairs = []
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in ordered:
        grouped[
            (int(row["task"]["problem_number"]), str(row["task"]["candidate_id"]))
        ].append(row)
    for (problem_number, candidate_id), pair in sorted(grouped.items()):
        by_temp = {float(row["task"]["temperature"]): row for row in pair}
        low, high = by_temp[0.2], by_temp[0.4]
        low_fields = low["parsed"].get("fields") or {}
        high_fields = high["parsed"].get("fields") or {}
        pairs.append(
            {
                "problem_number": problem_number,
                "candidate_id": candidate_id,
                "same_outcome": low["parsed"]["outcome"] == high["parsed"]["outcome"],
                "same_location_text": low_fields.get("location") == high_fields.get("location"),
                "exact_final_match": low["final"] == high["final"],
            }
        )
    return {
        "schema": "cognitive-well-v049-reviewer1-temperature-summary-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "output_dir": str(output_dir.resolve()),
        "model_key": ordered[0]["task"]["model_key"],
        "model": ordered[0]["task"]["model_name"],
        "result_count": len(ordered),
        "format_valid_count": sum(row["parsed"]["valid"] for row in ordered),
        "thinking_observed_count": sum(bool(row["thinking_observed"]) for row in ordered),
        "by_temperature": by_temperature,
        "by_gpu": by_gpu,
        "pair_agreement": {
            "pair_count": len(pairs),
            "same_outcome_count": sum(row["same_outcome"] for row in pairs),
            "same_location_text_count": sum(row["same_location_text"] for row in pairs),
            "exact_final_match_count": sum(row["exact_final_match"] for row in pairs),
            "pairs": pairs,
        },
        "results": ordered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Reviewer 1 at temperatures 0.2 and 0.4 over all 36 proofs"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--reviewer-model",
        choices=tuple(MODEL_CONFIGS),
        default="qwen36",
    )
    parser.add_argument("--endpoint-gpu0", default=DEFAULT_ENDPOINTS[0])
    parser.add_argument("--endpoint-gpu1", default=DEFAULT_ENDPOINTS[1])
    parser.add_argument("--batch-size", type=int, default=PER_GPU_BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.batch_size != PER_GPU_BATCH_SIZE:
        raise ValueError(f"this frozen experiment requires batch size {PER_GPU_BATCH_SIZE}")
    endpoints = {0: args.endpoint_gpu0.rstrip("/"), 1: args.endpoint_gpu1.rstrip("/")}
    model_config = MODEL_CONFIGS[args.reviewer_model]
    model_name = str(model_config["model"])
    rows = load_proofs()
    tasks = build_tasks(rows)
    for task in tasks:
        task["endpoint"] = endpoints[int(task["gpu"])]
        task["model_key"] = args.reviewer_model
        task["model_name"] = model_name
    validate_assignment(tasks)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_identity = {
        "harness_version": HARNESS_VERSION,
        "model_key": args.reviewer_model,
        "model": model_name,
        "model_checkpoint_revision": model_config["checkpoint_revision"],
        "dtype": model_config["dtype"],
        "mtp_speculative_tokens": model_config["mtp_speculative_tokens"],
        "temperatures": list(TEMPERATURES),
        "top_p": TOP_P,
        "top_k": TOP_K,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "cap_recovery": {
            "enabled": True,
            "max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
            "policy": "reuse primary reasoning/final fragment once and continue",
        },
        "thinking_enabled": True,
        "batch_size_per_gpu": PER_GPU_BATCH_SIZE,
        "global_concurrency": PER_GPU_BATCH_SIZE * 2,
        "endpoints": {str(gpu): endpoint for gpu, endpoint in endpoints.items()},
        "system_prompt_sha256": sha256_text(SYSTEM_PROMPT),
        "review_count": len(tasks),
        "proof_count": len(rows),
        "reference_solution_access_during_review": False,
        "assignment_policy": (
            "gpu=(proof_index+temperature_index)%2; every proof pair crossed; "
            "18 calls per temperature per GPU"
        ),
        "seed_policy": (
            "sha256(v049, reviewer1, problem, candidate, proof_sha256); "
            "same seed for the two temperatures"
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
                "schema": "cognitive-well-v049-reviewer1-temperature-manifest-v1",
                "created_at": utc_now(),
                "identity": manifest_identity,
                "sources": {
                    "p12356_run": str(P12356_RUN.resolve()),
                    "p4_run": str(P4_RUN.resolve()),
                },
                "tasks": [public_task(task) for task in tasks],
            },
        )
        (args.output_dir / "reviewer1_system_prompt.txt").write_text(
            SYSTEM_PROMPT + "\n", encoding="utf-8"
        )
    if args.dry_run:
        print(json.dumps(manifest_identity, indent=2))
        return

    for gpu, endpoint in endpoints.items():
        models = endpoint_models(endpoint)
        if model_name not in models:
            raise RuntimeError(
                f"GPU{gpu} endpoint {endpoint} does not serve {model_name}: {models}"
            )

    completed: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    lock = threading.Lock()

    def write_status() -> None:
        write_json(
            args.output_dir / "status.json",
            {
                "state": "running",
                "stage": "reviewer1_temperature_ablation",
                "completed": [row["task"]["task_id"] for row in completed],
                "failed": failures,
                "completed_count": len(completed),
                "total": len(tasks),
                "by_gpu_completed": {
                    str(gpu): sum(row["task"]["gpu"] == gpu for row in completed)
                    for gpu in (0, 1)
                },
                "by_temperature_completed": {
                    str(temperature): sum(
                        row["task"]["temperature"] == temperature for row in completed
                    )
                    for temperature in TEMPERATURES
                },
                "updated_at": utc_now(),
            },
        )

    write_status()
    executors = {
        gpu: ThreadPoolExecutor(
            max_workers=PER_GPU_BATCH_SIZE,
            thread_name_prefix=f"reviewer1-gpu{gpu}",
        )
        for gpu in (0, 1)
    }
    futures: dict[Future[dict[str, Any]], dict[str, Any]] = {}
    try:
        for task in tasks:
            gpu = int(task["gpu"])
            futures[executors[gpu].submit(run_task, output_dir=args.output_dir, task=task)] = task
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                with lock:
                    completed.append(result)
                    write_status()
                if not args.quiet:
                    print(
                        f"{task['task_id']} gpu{task['gpu']} "
                        f"{result['parsed']['outcome']}"
                    )
            except Exception as error:
                failure = {
                    "task_id": task["task_id"],
                    "gpu": task["gpu"],
                    "temperature": task["temperature"],
                    "error": f"{type(error).__name__}: {error}",
                    "traceback": traceback.format_exc(),
                }
                with lock:
                    failures.append(failure)
                    write_status()
    finally:
        for executor in executors.values():
            executor.shutdown(wait=True)

    if failures:
        write_json(
            args.output_dir / "status.json",
            {
                "state": "failed",
                "completed_count": len(completed),
                "total": len(tasks),
                "failed": failures,
                "updated_at": utc_now(),
            },
        )
        raise RuntimeError(f"{len(failures)} Reviewer 1 calls failed")
    summary = summarize(completed, args.output_dir)
    write_json(args.output_dir / "summary.json", summary)
    write_json(
        args.output_dir / "status.json",
        {
            "state": "completed",
            "completed_count": len(completed),
            "total": len(tasks),
            "failed": [],
            "summary_path": str((args.output_dir / "summary.json").resolve()),
            "updated_at": utc_now(),
        },
    )


if __name__ == "__main__":
    main()
