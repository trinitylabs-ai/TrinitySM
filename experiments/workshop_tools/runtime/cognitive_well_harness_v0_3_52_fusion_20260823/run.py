from __future__ import annotations

import argparse
import hashlib
import json
import re
import threading
import traceback
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
    utc_now,
    write_json,
)

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    parse_review as parse_reviewer_1,
)
from cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823.protocol import (
    parse_review as parse_reviewer_2,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.protocol import (
    SUCCESS_TOKEN as REVIEWER_3_SUCCESS_TOKEN,
    parse_review as parse_reviewer_3,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.run import (
    CANDIDATE_ORDER,
    PROBLEM_ORDER,
    endpoint_models,
    load_proofs,
    merge_continuation,
)

from . import HARNESS_VERSION
from .protocol import SYSTEM_PROMPT, fusion_user_prompt, parse_fusion, sha256_text


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

TEMPERATURES = (0.2, 0.4)
PER_GPU_BATCH_SIZE = 4
MAX_OUTPUT_TOKENS = 16_000
CAP_RECOVERY_MAX_OUTPUT_TOKENS = 32_000
TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS = 4_000
TERMINAL_RECOVERY_THINKING_BUDGET = 1_024
REASONING_EFFORT = "max"
TOP_P = 1.0
TOP_K = -1
RESULT_SCHEMA = "cognitive-well-v052-fusion-result-v1"
SUMMARY_SCHEMA = "cognitive-well-v052-fusion-summary-v1"
MANIFEST_SCHEMA = "cognitive-well-v052-fusion-manifest-v1"
PERMITTED_RECORD_NAMES = (
    "FUSION_ACCEPT, FUSION_REWRITE_REQUIRED, or FUSION_INCONCLUSIVE"
)
SEED_POLICY = (
    "matched sha256(v052,fusion,problem,candidate,proof) across models and temperatures"
)

REVIEWER_1_ROOT = Path(
    "runs/v049_reviewer1_temp02_temp04_all36_gemma4_bf16_mtp4_2gpu_b4_12k_20260823_1016"
)
REVIEWER_2_ROOT = Path(
    "runs/v050_reviewer2_adversarial_all36_qwen36_t02_gpu1_b4_12k_20260823_1053"
)
REVIEWER_3_ROOT = Path(
    "runs/v051_reviewer3_certifier_all36_gemma4_bf16_mtp4_t02_gpu0_b4_16k_20260823_1302"
)

REVIEWER_SELECTION = {
    "reviewer_1": {
        "root": REVIEWER_1_ROOT,
        "temperature_dir": "temperature_0_4",
        "model": "google/gemma-4-31B-it",
        "temperature": 0.4,
        "parser": parse_reviewer_1,
        "role": "earliest-break locator",
    },
    "reviewer_2": {
        "root": REVIEWER_2_ROOT,
        "temperature_dir": "temperature_0_2",
        "model": "Qwen/Qwen3.6-27B",
        "temperature": 0.2,
        "parser": parse_reviewer_2,
        "role": "adversarial falsifier",
    },
    "reviewer_3": {
        "root": REVIEWER_3_ROOT,
        "temperature_dir": "temperature_0_2",
        "model": "google/gemma-4-31B-it",
        "temperature": 0.2,
        "parser": parse_reviewer_3,
        "role": "charitable certifier",
    },
}


def stable_seed(problem_number: int, candidate_id: str, proof_sha256: str) -> int:
    material = f"v052:fusion:p{problem_number}:{candidate_id}:{proof_sha256}".encode()
    value = int.from_bytes(hashlib.sha256(material).digest()[:4], "big")
    return value or 1


def _load_selected_reviewer(
    *,
    name: str,
    root: Path,
    temperature_dir: str,
    model: str,
    temperature: float,
    parser: Callable[[str], dict[str, Any]],
) -> dict[tuple[int, str], dict[str, Any]]:
    review_root = root / "reviews" / temperature_dir
    if not review_root.is_dir():
        raise FileNotFoundError(f"missing selected {name} root: {review_root}")
    rows: dict[tuple[int, str], dict[str, Any]] = {}
    for path in review_root.rglob("result.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        task = payload.get("task") or {}
        key = (int(task["problem_number"]), str(task["candidate_id"]))
        if key in rows:
            raise ValueError(f"duplicate selected {name} result for {key}")
        if task.get("model_name") != model:
            raise ValueError(f"wrong {name} model for {key}: {task.get('model_name')}")
        if float(task.get("temperature")) != temperature:
            raise ValueError(f"wrong {name} temperature for {key}")
        final = str(payload.get("final") or "").strip()
        parsed = parser(final)
        if not parsed["valid"]:
            raise ValueError(f"invalid selected {name} record for {key}: {parsed['errors']}")
        rows[key] = {
            "final": final,
            "final_sha256": sha256_text(final),
            "proof_sha256": str(task["proof_sha256"]),
            "source_result_path": str(path.resolve()),
            "source_result_sha256": sha256_text(path.read_text(encoding="utf-8")),
            "model": model,
            "temperature": temperature,
            "outcome": parsed["outcome"],
        }
    if len(rows) != 36:
        raise ValueError(f"expected 36 selected {name} records, found {len(rows)}")
    return rows


def load_fusion_rows() -> list[dict[str, Any]]:
    selected: dict[str, dict[tuple[int, str], dict[str, Any]]] = {}
    for name, config in REVIEWER_SELECTION.items():
        selected[name] = _load_selected_reviewer(
            name=name,
            root=config["root"],
            temperature_dir=str(config["temperature_dir"]),
            model=str(config["model"]),
            temperature=float(config["temperature"]),
            parser=config["parser"],
        )

    rows = load_proofs()
    for row in rows:
        key = (int(row["problem_number"]), str(row["candidate_id"]))
        records = {name: selected[name][key] for name in REVIEWER_SELECTION}
        for name, record in records.items():
            if record["proof_sha256"] != row["proof_sha256"]:
                raise ValueError(f"{name} proof hash mismatch for {key}")
        reviewer_3_final = records["reviewer_3"]["final"]
        reviewer_3_was_legacy = reviewer_3_final == "PROOF_CERTIFIED"
        if reviewer_3_was_legacy:
            reviewer_3_final = REVIEWER_3_SUCCESS_TOKEN
        row["reviewer_1"] = records["reviewer_1"]["final"]
        row["reviewer_2"] = records["reviewer_2"]["final"]
        row["reviewer_3"] = reviewer_3_final
        row["reviewer_sources"] = {
            name: {
                key_name: value
                for key_name, value in record.items()
                if key_name != "final"
            }
            for name, record in records.items()
        }
        row["reviewer_sources"]["reviewer_3"][
            "legacy_success_token_normalized"
        ] = reviewer_3_was_legacy
        row["reviewer_sources"]["reviewer_3"][
            "fusion_record_sha256"
        ] = sha256_text(reviewer_3_final)
        row["seed"] = stable_seed(
            int(row["problem_number"]), str(row["candidate_id"]), row["proof_sha256"]
        )
    return rows


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
    model_name = str(MODEL_CONFIGS[model_key]["model"])
    tasks: list[dict[str, Any]] = []
    if not temperatures or any(value not in TEMPERATURES for value in temperatures):
        raise ValueError(f"temperatures must be a nonempty subset of {TEMPERATURES}")
    if len(set(temperatures)) != len(temperatures):
        raise ValueError("temperatures must be unique")
    for temperature in temperatures:
        label = f"t{int(round(temperature * 10)):02d}"
        for row in rows:
            tasks.append(
                {
                    **row,
                    "temperature": temperature,
                    "temperature_label": label,
                    "gpu": gpu,
                    "endpoint": endpoint,
                    "model_key": model_key,
                    "model_name": model_name,
                    "task_id": f"p{row['problem_number']}.{row['candidate_id']}.{label}",
                }
            )
    validate_tasks(tasks)
    return tasks


def validate_tasks(tasks: list[dict[str, Any]]) -> None:
    temperatures = {float(row["temperature"]) for row in tasks}
    expected_count = 36 * len(temperatures)
    if (
        not temperatures
        or not temperatures.issubset(set(TEMPERATURES))
        or len(tasks) != expected_count
        or len({row["task_id"] for row in tasks}) != expected_count
    ):
        raise ValueError("each selected model-temperature arm must contain 36 tasks")
    for temperature in temperatures:
        arm = [row for row in tasks if row["temperature"] == temperature]
        keys = {(row["problem_number"], row["candidate_id"]) for row in arm}
        if len(arm) != 36 or len(keys) != 36:
            raise ValueError(f"temperature {temperature} does not contain 36 proofs")
    seeds: dict[tuple[int, str], set[int]] = {}
    for row in tasks:
        key = (int(row["problem_number"]), str(row["candidate_id"]))
        seeds.setdefault(key, set()).add(int(row["seed"]))
    if any(len(values) != 1 for values in seeds.values()):
        raise ValueError("temperature pair must use matched per-proof seeds")


def task_output_dir(output_dir: Path, task: dict[str, Any]) -> Path:
    return (
        output_dir
        / "fusion"
        / f"temperature_{str(task['temperature']).replace('.', '_')}"
        / f"gpu{task['gpu']}"
        / f"p{task['problem_number']}"
        / str(task["candidate_id"])
    )


def public_task(task: dict[str, Any]) -> dict[str, Any]:
    hidden = {
        "problem",
        "proof",
        "reviewer_1",
        "reviewer_2",
        "reviewer_3",
        "_reuse_result_path",
    }
    return {key: value for key, value in task.items() if key not in hidden}


def parse_task_output(value: str, task: dict[str, Any]) -> dict[str, Any]:
    del task
    return parse_fusion(value)


def _reusable_reasoning(reasoning_parts: list[str], final: str) -> str:
    parts = [
        "[Preserved model-native reasoning]\n" + part
        for part in reasoning_parts
        if part
    ]
    if final:
        parts.append("[Preserved final response fragment]\n" + final)
    return "\n\n".join(parts)


_ASSESSMENT_CONSTRAINT_ERROR = re.compile(
    r"^reviewer_[123]_assessment label \S+ is incompatible with source outcome "
    r"\S+; allowed: \[[^\n]+\]$"
)


def _assessment_constraint_repair_instruction(
    errors: list[str],
) -> str | None:
    """Build a transport-only repair prompt for source-label mismatches."""
    if not errors or any(
        not _ASSESSMENT_CONSTRAINT_ERROR.fullmatch(error) for error in errors
    ):
        return None
    diagnostics = "\n".join(f"- {error}" for error in errors)
    return (
        "Do not perform additional mathematics and do not change the completed "
        "adjudication. Preserve the verdict and every mathematical explanation. "
        "Correct only reviewer assessment labels that conflict with the formal "
        "source report type, choosing a compatible label from the allowed set in "
        "each deterministic parser diagnostic below. If a source report alleged a "
        "defect that your adjudication rejected, express that as the compatible "
        "rejected-defect label rather than as no defect having been reported. "
        "Then re-emit exactly one permitted fusion record and output nothing else.\n"
        "Parser diagnostics:\n"
        f"{diagnostics}"
    )


def run_task(*, output_dir: Path, task: dict[str, Any]) -> dict[str, Any]:
    destination = task_output_dir(output_dir, task)
    destination.mkdir(parents=True, exist_ok=True)
    user_prompt = fusion_user_prompt(
        problem=task["problem"],
        proof=task["proof"],
        reviewer_1=task["reviewer_1"],
        reviewer_2=task["reviewer_2"],
        reviewer_3=task["reviewer_3"],
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
        saved = json.loads(reusable_path.read_text(encoding="utf-8"))
        parsed = parse_task_output(str(saved.get("final") or ""), task)
        if saved.get("identity") == identity and parsed["valid"]:
            normalized = str(parsed["normalized_final"])
            reused = {
                **saved,
                "final": normalized,
                "final_sha256": sha256_text(normalized),
                "parsed": parse_task_output(normalized, task),
                "response_source": (
                    "saved" if reusable_path == saved_path else "reused_from_parent"
                ),
            }
            if reusable_path != saved_path:
                write_json(saved_path, reused)
                (destination / "final.txt").write_text(
                    normalized + "\n", encoding="utf-8"
                )
            return reused

    generated = run_openai_chat_generation(
        endpoint=str(task["endpoint"]),
        model=str(task["model_name"]),
        prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_dir=destination,
        stage="fusion",
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
            raise RuntimeError("fusion hit its cap without reusable output")
        continued = run_openai_chat_generation(
            endpoint=str(task["endpoint"]),
            model=str(task["model_name"]),
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            prior_generation=reusable,
            continuation_instruction=(
                "Continue the same private fusion adjudication from the preserved "
                "reasoning. Do not restart. Finish all checks and emit exactly one "
                f"permitted {PERMITTED_RECORD_NAMES} record."
            ),
            output_dir=destination,
            stage="fusion_cap_continuation",
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
            if parse_task_output(continuation, task)["valid"]
            else merge_continuation(final, continuation)
        )
        continuation_reasoning = str(continued.get("reasoning") or "").strip()
        reasoning_parts.append(continuation_reasoning)
        final_generation = continued["metadata"]
        recovery = {
            "triggered": True,
            "primary_max_output_tokens": MAX_OUTPUT_TOKENS,
            "recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
            "reusable_sha256": sha256_text(reusable),
            "continuation_sha256": sha256_text(continuation),
            "recovery_generation": continued["metadata"],
        }
        if continued["metadata"].get("finish_reason") == "length":
            terminal_reusable = _reusable_reasoning(reasoning_parts, final)
            terminal = run_openai_chat_generation(
                endpoint=str(task["endpoint"]),
                model=str(task["model_name"]),
                prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                prior_generation=terminal_reusable,
                continuation_instruction=(
                    "The private fusion adjudication is complete. Do no additional "
                    "analysis. Emit exactly one permitted fusion record now."
                ),
                output_dir=destination,
                stage="fusion_terminal_recovery",
                config=HTTPGenerationConfig(
                    max_tokens=TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS,
                    temperature=float(task["temperature"]),
                    top_p=TOP_P,
                    top_k=TOP_K,
                    seed=(int(task["seed"]) + 2_000_006) & 0xFFFFFFFF,
                    thinking_token_budget=TERMINAL_RECOVERY_THINKING_BUDGET,
                    reasoning_effort=None,
                    timeout_seconds=14_400,
                ),
            )
            terminal_text = str(terminal["text"]).strip()
            final = (
                terminal_text
                if parse_task_output(terminal_text, task)["valid"]
                else merge_continuation(final, terminal_text)
            )
            reasoning_parts.append(str(terminal.get("reasoning") or "").strip())
            final_generation = terminal["metadata"]
            recovery["terminal_recovery"] = {
                "triggered": True,
                "generation": terminal["metadata"],
            }
            if terminal["metadata"].get("finish_reason") == "length":
                raise RuntimeError("fusion exhausted terminal recovery token cap")

    parsed = parse_task_output(final, task)
    if not parsed["valid"]:
        repair_reusable = _reusable_reasoning(reasoning_parts, final)
        if not repair_reusable:
            raise ValueError(f"invalid fusion output: {parsed['errors']}")
        repaired = run_openai_chat_generation(
            endpoint=str(task["endpoint"]),
            model=str(task["model_name"]),
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            prior_generation=repair_reusable,
            continuation_instruction=(
                "Do not perform additional mathematics. Convert the completed "
                "adjudication into exactly one permitted fusion record and output "
                "nothing else."
            ),
            output_dir=destination,
            stage="fusion_protocol_repair",
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
        final = str(repaired["text"]).strip()
        reasoning_parts.append(str(repaired.get("reasoning") or "").strip())
        final_generation = repaired["metadata"]
        recovery["protocol_repair"] = {
            "triggered": True,
            "generation": repaired["metadata"],
        }
        parsed = parse_task_output(final, task)
    if not parsed["valid"]:
        constraint_instruction = _assessment_constraint_repair_instruction(
            list(parsed["errors"])
        )
        if constraint_instruction is not None:
            constrained = run_openai_chat_generation(
                endpoint=str(task["endpoint"]),
                model=str(task["model_name"]),
                prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                prior_generation=_reusable_reasoning(reasoning_parts, final),
                continuation_instruction=constraint_instruction,
                output_dir=destination,
                stage="fusion_assessment_constraint_repair",
                config=HTTPGenerationConfig(
                    max_tokens=TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS,
                    temperature=float(task["temperature"]),
                    top_p=TOP_P,
                    top_k=TOP_K,
                    seed=(int(task["seed"]) + 4_000_012) & 0xFFFFFFFF,
                    thinking_token_budget=TERMINAL_RECOVERY_THINKING_BUDGET,
                    reasoning_effort=None,
                    timeout_seconds=14_400,
                ),
            )
            final = str(constrained["text"]).strip()
            reasoning_parts.append(str(constrained.get("reasoning") or "").strip())
            final_generation = constrained["metadata"]
            recovery["assessment_constraint_repair"] = {
                "triggered": True,
                "input_errors": list(parsed["errors"]),
                "generation": constrained["metadata"],
            }
            parsed = parse_task_output(final, task)
    if not parsed["valid"]:
        raise ValueError(f"invalid fusion output after repair: {parsed['errors']}")

    model_final_before_normalization = final
    normalized_final = str(parsed["normalized_final"])
    normalization_applied = normalized_final != final
    if normalization_applied:
        final = normalized_final
        parsed = parse_task_output(final, task)
        if not parsed["valid"]:
            raise RuntimeError("internal fusion final normalization produced invalid output")

    reasoning = "\n\n[CONTINUATION]\n\n".join(
        part for part in reasoning_parts if part
    )
    result = {
        "schema": RESULT_SCHEMA,
        "identity": identity,
        "task": public_task(task),
        "final": final,
        "final_sha256": sha256_text(final),
        "final_normalization": {
            "applied": normalization_applied,
            "model_final_sha256": sha256_text(model_final_before_normalization),
            "policy": "role-specific no-defect token -> NO_DEFECT_REPORTED",
        },
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
    by_temperature = {}
    temperatures = sorted({float(row["task"]["temperature"]) for row in ordered})
    for temperature in temperatures:
        arm = [row for row in ordered if row["task"]["temperature"] == temperature]
        by_temperature[str(temperature)] = {
            "count": len(arm),
            "format_valid_count": sum(row["parsed"]["valid"] for row in arm),
            "thinking_observed_count": sum(bool(row["thinking_observed"]) for row in arm),
            "outcomes": dict(Counter(row["parsed"]["outcome"] for row in arm)),
            "recovery_count": sum(bool(row["recovery"].get("triggered")) for row in arm),
        }
    return {
        "schema": SUMMARY_SCHEMA,
        "state": "completed",
        "completed_at": utc_now(),
        "output_dir": str(output_dir.resolve()),
        "model_key": ordered[0]["task"]["model_key"],
        "model": ordered[0]["task"]["model_name"],
        "result_count": len(ordered),
        "by_temperature": by_temperature,
        "results": ordered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run two-temperature three-reviewer proof fusion over all 36 proofs"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--fusion-model", choices=tuple(MODEL_CONFIGS), required=True)
    parser.add_argument("--gpu-index", type=int, choices=(0, 1))
    parser.add_argument("--endpoint")
    parser.add_argument(
        "--temperatures",
        type=float,
        nargs="+",
        choices=TEMPERATURES,
        default=list(TEMPERATURES),
    )
    parser.add_argument("--reuse-results-from", type=Path)
    parser.add_argument("--batch-size", type=int, default=PER_GPU_BATCH_SIZE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.batch_size != PER_GPU_BATCH_SIZE:
        raise ValueError(f"this frozen experiment requires batch size {PER_GPU_BATCH_SIZE}")

    config = MODEL_CONFIGS[args.fusion_model]
    gpu = int(args.gpu_index if args.gpu_index is not None else config["default_gpu"])
    endpoint = str(args.endpoint or config["default_endpoint"]).rstrip("/")
    temperatures = tuple(float(value) for value in args.temperatures)
    rows = load_fusion_rows()
    tasks = build_tasks(
        rows,
        model_key=args.fusion_model,
        gpu=gpu,
        endpoint=endpoint,
        temperatures=temperatures,
    )
    if args.reuse_results_from:
        reuse_root = args.reuse_results_from.resolve()
        for task in tasks:
            task["_reuse_result_path"] = str(
                task_output_dir(reuse_root, task) / "result.json"
            )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reviewer_sources = {
        name: {
            "role": selection["role"],
            "root": str(selection["root"].resolve()),
            "model": selection["model"],
            "temperature": selection["temperature"],
        }
        for name, selection in REVIEWER_SELECTION.items()
    }
    manifest_identity = {
        "harness_version": HARNESS_VERSION,
        "model_key": args.fusion_model,
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
        "fusion_call_count": len(tasks),
        "proof_count": len(rows),
        "seed_policy": SEED_POLICY,
        "reviewer_input_policy": (
            "original problem and proof once; only each selected reviewer's final "
            "structured record; no private reasoning, raw response, or reviewer system prompt"
        ),
        "reviewer_3_legacy_success_normalization": (
            "PROOF_CERTIFIED -> NO_UNCLOSED_OBLIGATION_FOUND in fusion input only"
        ),
        "reference_solution_access_during_fusion": False,
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
                "reviewer_sources": reviewer_sources,
                "tasks": [public_task(task) for task in tasks],
            },
        )
        (args.output_dir / "fusion_system_prompt.txt").write_text(
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
                "stage": "three_reviewer_fusion",
                "completed": [row["task"]["task_id"] for row in completed],
                "failed": failures,
                "completed_count": len(completed),
                "total": len(tasks),
                "by_temperature_completed": {
                    str(temperature): sum(
                        row["task"]["temperature"] == temperature for row in completed
                    )
                    for temperature in temperatures
                },
                "gpu": gpu,
                "updated_at": utc_now(),
            },
        )

    write_status()
    executor = ThreadPoolExecutor(
        max_workers=PER_GPU_BATCH_SIZE,
        thread_name_prefix=f"fusion-gpu{gpu}",
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
        raise RuntimeError(f"{len(failures)} fusion calls failed")
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
