from __future__ import annotations

import argparse
import hashlib
import json
import threading
import traceback
import urllib.request
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
MAX_OUTPUT_TOKENS = 16_000
CAP_RECOVERY_MAX_OUTPUT_TOKENS = 24_000
FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS = 32_000
RETRY_ON_OUTPUT_CAP = True
CUTOFF_FINISH_REASONS = {"length", "repetition"}
TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS = 4_000
TERMINAL_RECOVERY_THINKING_BUDGET = 1_024
TOP_P = 1.0
TOP_K = -1
PROBLEM_ROOT = Path("math_harness_inputs/imo2026_p4_p2_v0313_20260815")
P12356_RUN = Path("runs/v048_imo2026_p12356_six_lazy_20260823_021215")
P4_RUN = Path("runs/v048_imo2026_p4_six_lazy_20260823_083927")
DEFAULT_ENDPOINTS = {0: "http://127.0.0.1:8020/v1", 1: "http://127.0.0.1:8027/v1"}


def stable_seed(problem_number: int, candidate_id: str, proof_sha256: str) -> int:
    material = (
        f"v050:reviewer2:p{problem_number}:{candidate_id}:{proof_sha256}"
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


def build_tasks(
    rows: list[dict[str, Any]], *, gpu: int = 0, temperature: float = 0.2
) -> list[dict[str, Any]]:
    if gpu not in (0, 1):
        raise ValueError(f"gpu must be 0 or 1, got {gpu}")
    if temperature not in TEMPERATURES:
        raise ValueError(f"temperature must be one of {TEMPERATURES}, got {temperature}")
    tasks: list[dict[str, Any]] = []
    for row in rows:
        label = f"t{int(round(temperature * 10)):02d}"
        tasks.append(
            {
                **row,
                "temperature": temperature,
                "temperature_label": label,
                "gpu": gpu,
                "endpoint": DEFAULT_ENDPOINTS[gpu],
                "task_id": f"p{row['problem_number']}.{row['candidate_id']}.{label}",
            }
        )
    validate_assignment(tasks)
    return tasks


def validate_assignment(tasks: list[dict[str, Any]]) -> None:
    if len(tasks) != 36 or len({row["task_id"] for row in tasks}) != 36:
        raise ValueError("the experiment must contain exactly 36 unique tasks")
    if len({row["temperature"] for row in tasks}) != 1:
        raise ValueError("one model arm must use exactly one temperature")
    if next(iter({row["temperature"] for row in tasks})) not in TEMPERATURES:
        raise ValueError(f"temperature must be one of {TEMPERATURES}")
    if len({row["gpu"] for row in tasks}) != 1:
        raise ValueError("one model arm must use exactly one GPU")
    if len({(row["problem_number"], row["candidate_id"]) for row in tasks}) != 36:
        raise ValueError("every proof must appear exactly once")


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
        "cap_recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS if RETRY_ON_OUTPUT_CAP else None,
        "final_cap_recovery_max_output_tokens": FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS if RETRY_ON_OUTPUT_CAP else None,
        "cap_recovery_policy": "clean_restart_same_prompt_same_seed" if RETRY_ON_OUTPUT_CAP else "stop_on_output_cap",
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
        stage="reviewer2",
        config=primary_config,
    )
    accepted_generation = generated
    primary_finish = generated["metadata"].get("finish_reason")
    cap_recovery: dict[str, Any] = {
        "triggered": False,
        "policy": identity["cap_recovery_policy"],
    }
    if primary_finish in CUTOFF_FINISH_REASONS:
        if not RETRY_ON_OUTPUT_CAP:
            write_json(destination / "cap_failure.json", {
                "identity": identity,
                "state": "output_cap_reached",
                "finish_reason": primary_finish,
                "generation": generated["metadata"],
                "retry_performed": False,
            })
            raise RuntimeError(
                f"Reviewer 2 reached output boundary {primary_finish} at cap "
                f"{MAX_OUTPUT_TOKENS}; token-cap retries are disabled"
            )
        recovery_attempts: list[dict[str, Any]] = []
        recovery_finish = primary_finish
        for retry_number, retry_cap in enumerate(
            (
                CAP_RECOVERY_MAX_OUTPUT_TOKENS,
                FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS,
            ),
            start=1,
        ):
            recovery = run_openai_chat_generation(
                endpoint=str(task["endpoint"]),
                model=str(task["model_name"]),
                prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                output_dir=destination,
                stage=f"reviewer2_clean_{retry_cap // 1000}k_retry_{retry_number}",
                config=HTTPGenerationConfig(
                    max_tokens=retry_cap,
                    temperature=float(task["temperature"]),
                    top_p=TOP_P,
                    top_k=TOP_K,
                    seed=int(task["seed"]),
                    thinking_token_budget=None,
                    reasoning_effort=None,
                    timeout_seconds=14_400,
                ),
            )
            accepted_generation = recovery
            recovery_finish = recovery["metadata"].get("finish_reason")
            recovery_attempts.append(
                {
                    "retry_number": retry_number,
                    "max_output_tokens": retry_cap,
                    "finish_reason": recovery_finish,
                    "generation": recovery["metadata"],
                }
            )
            if recovery_finish not in CUTOFF_FINISH_REASONS:
                break

        last_recovery = recovery_attempts[-1]
        cap_recovery = {
            "triggered": True,
            "policy": "clean_restart_same_prompt_same_seed",
            "primary_max_output_tokens": MAX_OUTPUT_TOKENS,
            "recovery_max_output_tokens": last_recovery["max_output_tokens"],
            "primary_finish_reason": primary_finish,
            "recovery_finish_reason": recovery_finish,
            "reused_partial_generation": False,
            "prior_reasoning_supplied": False,
            "prior_visible_supplied": False,
            "same_system_prompt": True,
            "same_user_prompt": True,
            "same_seed": True,
            "recovery_generation": last_recovery["generation"],
            "recovery_attempts": recovery_attempts,
        }
        if recovery_finish in CUTOFF_FINISH_REASONS:
            raise RuntimeError(
                "Reviewer 2 clean 32k retry also ended at an output boundary"
            )

    final = str(accepted_generation["text"]).strip()
    accepted_reasoning = str(accepted_generation.get("reasoning") or "").strip()
    reasoning_parts = [accepted_reasoning]
    final_generation = accepted_generation["metadata"]
    parsed = parse_review(final)
    if not parsed["valid"]:
        repair_parts = [
            "[Preserved private reasoning]\n" + part
            for part in reasoning_parts
            if part
        ]
        if final:
            repair_parts.append("[Malformed final response]\n" + final)
        repair_reusable = "\n\n".join(repair_parts)
        if not repair_reusable:
            raise ValueError(f"invalid Reviewer 2 output: {parsed['errors']}")
        protocol_repair = run_openai_chat_generation(
            endpoint=str(task["endpoint"]),
            model=str(task["model_name"]),
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            prior_generation=repair_reusable,
            continuation_instruction=(
                "Do not perform any additional mathematical analysis. Convert your "
                "completed audit into exactly one permitted final form now. Output "
                "only one ADVERSARIAL_BREAK record, or exactly "
                "NO_ADVERSARIAL_BREAK."
            ),
            output_dir=destination,
            stage="reviewer2_protocol_repair",
            config=HTTPGenerationConfig(
                max_tokens=TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS,
                temperature=float(task["temperature"]),
                top_p=TOP_P,
                top_k=TOP_K,
                seed=(int(task["seed"]) + 3_000_009) & 0xFFFFFFFF,
                thinking_token_budget=TERMINAL_RECOVERY_THINKING_BUDGET,
                reasoning_effort=None,
                timeout_seconds=14_400,
            ),
        )
        final = str(protocol_repair["text"]).strip()
        if (not RETRY_ON_OUTPUT_CAP
                and protocol_repair["metadata"].get("finish_reason") in CUTOFF_FINISH_REASONS):
            write_json(destination / "cap_failure.json", {
                "identity": identity,
                "state": "output_cap_reached",
                "generation": protocol_repair["metadata"],
                "retry_performed": False,
            })
            raise RuntimeError("Reviewer 2 protocol repair reached its output cap; token-cap retries are disabled")
        reasoning_parts.append(str(protocol_repair.get("reasoning") or "").strip())
        final_generation = protocol_repair["metadata"]
        cap_recovery["protocol_repair"] = {
            "triggered": True,
            "max_output_tokens": TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS,
            "thinking_token_budget": TERMINAL_RECOVERY_THINKING_BUDGET,
            "reusable_sha256": sha256_text(repair_reusable),
            "generation": protocol_repair["metadata"],
        }
        parsed = parse_review(final)
    if not parsed["valid"]:
        raise ValueError(f"invalid Reviewer 2 output: {parsed['errors']}")
    reasoning = accepted_reasoning
    result = {
        "schema": "cognitive-well-v050-reviewer2-result-v1",
        "identity": identity,
        "task": public_task(task),
        "final": final,
        "final_sha256": sha256_text(final),
        "parsed": parsed,
        "thinking_requested": True,
        "thinking_observed": bool(reasoning),
        "reasoning_sha256": sha256_text(reasoning),
        "reasoning_harvest_policy": "accepted_transport_attempt_only",
        "generation": generated["metadata"],
        "final_generation": final_generation,
        "cap_recovery": cap_recovery,
        "response_source": "live",
        "completed_at": utc_now(),
    }
    write_json(saved_path, result)
    (destination / "final.txt").write_text(final + "\n", encoding="utf-8")
    (destination / "reasoning.txt").write_text(reasoning + "\n", encoding="utf-8")
    return result


def summarize(results: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    ordered = sorted(
        results,
        key=lambda row: (
            int(row["task"]["problem_number"]),
            CANDIDATE_ORDER.index(str(row["task"]["candidate_id"])),
        ),
    )
    outcomes = Counter(row["parsed"]["outcome"] for row in ordered)
    completion_tokens = []
    for row in ordered:
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
    gpu = int(ordered[0]["task"]["gpu"])
    return {
        "schema": "cognitive-well-v050-reviewer2-summary-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "output_dir": str(output_dir.resolve()),
        "model_key": ordered[0]["task"]["model_key"],
        "model": ordered[0]["task"]["model_name"],
        "result_count": len(ordered),
        "format_valid_count": sum(row["parsed"]["valid"] for row in ordered),
        "thinking_observed_count": sum(bool(row["thinking_observed"]) for row in ordered),
        "temperature": float(ordered[0]["task"]["temperature"]),
        "gpu": gpu,
        "outcomes": dict(outcomes),
        "cap_recovery_count": sum(
            bool(row.get("cap_recovery", {}).get("triggered")) for row in ordered
        ),
        "mean_completion_tokens": sum(completion_tokens) / len(completion_tokens),
        "by_problem": {
            str(problem_number): {
                "count": sum(
                    row["task"]["problem_number"] == problem_number for row in ordered
                ),
                "outcomes": dict(
                    Counter(
                        row["parsed"]["outcome"]
                        for row in ordered
                        if row["task"]["problem_number"] == problem_number
                    )
                ),
            }
            for problem_number in PROBLEM_ORDER
        },
        "results": ordered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Reviewer 2 at temperature 0.2 or 0.4 over all 36 proofs"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--reviewer-model",
        choices=tuple(MODEL_CONFIGS),
        default="qwen36",
    )
    parser.add_argument("--gpu-index", type=int, choices=(0, 1), required=True)
    parser.add_argument("--endpoint")
    parser.add_argument("--temperature", type=float, choices=TEMPERATURES, default=0.2)
    parser.add_argument("--batch-size", type=int, default=PER_GPU_BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.batch_size != PER_GPU_BATCH_SIZE:
        raise ValueError(f"this frozen experiment requires batch size {PER_GPU_BATCH_SIZE}")
    gpu = int(args.gpu_index)
    endpoint = str(args.endpoint or DEFAULT_ENDPOINTS[gpu]).rstrip("/")
    model_config = MODEL_CONFIGS[args.reviewer_model]
    model_name = str(model_config["model"])
    rows = load_proofs()
    tasks = build_tasks(rows, gpu=gpu, temperature=float(args.temperature))
    for task in tasks:
        task["endpoint"] = endpoint
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
        "temperature": float(args.temperature),
        "top_p": TOP_P,
        "top_k": TOP_K,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "cap_recovery": {
            "enabled": RETRY_ON_OUTPUT_CAP,
            "max_output_tokens": [
                CAP_RECOVERY_MAX_OUTPUT_TOKENS,
                FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS,
            ] if RETRY_ON_OUTPUT_CAP else [],
            "policy": ("clean restart from identical prompts with identical seed"
                       if RETRY_ON_OUTPUT_CAP else "stop_on_output_cap"),
            "reused_partial_generation": False,
            "fail_closed_after_final_retry_cutoff": True,
        },
        "thinking_enabled": True,
        "batch_size_per_gpu": PER_GPU_BATCH_SIZE,
        "global_concurrency": PER_GPU_BATCH_SIZE,
        "gpu": gpu,
        "endpoint": endpoint,
        "system_prompt_sha256": sha256_text(SYSTEM_PROMPT),
        "review_count": len(tasks),
        "proof_count": len(rows),
        "reference_solution_access_during_review": False,
        "assignment_policy": "all 36 proofs on the selected model GPU",
        "seed_policy": "sha256(v050, reviewer2, problem, candidate, proof_sha256)",
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
                "schema": "cognitive-well-v050-reviewer2-manifest-v1",
                "created_at": utc_now(),
                "identity": manifest_identity,
                "sources": {
                    "p12356_run": str(P12356_RUN.resolve()),
                    "p4_run": str(P4_RUN.resolve()),
                },
                "tasks": [public_task(task) for task in tasks],
            },
        )
        (args.output_dir / "reviewer2_system_prompt.txt").write_text(
            SYSTEM_PROMPT + "\n", encoding="utf-8"
        )
    if args.dry_run:
        print(json.dumps(manifest_identity, indent=2))
        return

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
                "stage": "reviewer2_adversarial",
                "completed": [row["task"]["task_id"] for row in completed],
                "failed": failures,
                "completed_count": len(completed),
                "total": len(tasks),
                "gpu": gpu,
                "temperature": float(args.temperature),
                "updated_at": utc_now(),
            },
        )

    write_status()
    executor = ThreadPoolExecutor(
        max_workers=PER_GPU_BATCH_SIZE,
        thread_name_prefix=f"reviewer2-gpu{gpu}",
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
        raise RuntimeError(f"{len(failures)} Reviewer 2 calls failed")
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
