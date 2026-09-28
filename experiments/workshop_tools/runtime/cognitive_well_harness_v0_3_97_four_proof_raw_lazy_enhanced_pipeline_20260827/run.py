from __future__ import annotations

import argparse
import hashlib
import json
import re
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from experiments.local_math_verifier.runtime import utc_now, write_json

from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.runtime import (
    GEMMA_MODEL,
    RuntimeConfig,
    StageRuntime,
)
from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.pipeline import (
    nonempty_parser,
)
from cognitive_well_harness_v0_3_42_gemma4_dual_prompt_max_thinking_coldsolve_20260823.run import (
    BASELINE_MAX_TOKENS,
)
from cognitive_well_harness_v0_3_46_gemma4_temperature_portfolio_20260823.run import (
    CANDIDATES,
)
from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.contracts import (
    LAZY_RESOLVE_TEMPERATURE,
)
from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.lazy_expansion import (
    EXPECTED_PROMPT_SHA256,
    sha256_text,
)
from cognitive_well_harness_v0_3_47_lazy_in_place_expansion_20260823.run_six_candidate_lazy_test import (
    run_lazy_check,
    run_lazy_resolve,
)
from cognitive_well_harness_v0_3_96_generic_enhanced_review_fusion_resolver_20260827 import (
    run as enhanced_pipeline,
)

from . import HARNESS_VERSION


RAW_CANDIDATE_IDS = ("t10_r01", "t10_r02", "t07_r01", "t07_r02")
RAW_CANDIDATES = tuple(
    next(spec for spec in CANDIDATES if spec["candidate_id"] == candidate_id)
    for candidate_id in RAW_CANDIDATE_IDS
)
RAW_BATCH_SIZE = 4
REVIEW_BATCH_SIZE = 4
MAX_WORKERS = 10
DEFAULT_GPU0_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_GPU1_QWEN_ENDPOINT = "http://127.0.0.1:8021/v1"
GPU0_GEMMA_PROFILE = {
    "model": GEMMA_MODEL,
    "dtype": "bfloat16",
    "mtp_speculative_tokens": 4,
}

# These are the byte-identical, problem-neutral prompt regions previously recovered
# at runtime from a P4 control run.  Keeping them here removes every cross-problem
# artifact read from the four-proof generation path.
FROZEN_SYSTEM_PROMPT = """You are the Dialectic Solver for a difficult olympiad problem. Thinking mode is on.

Use an internal council with these roles: a Classicist using established theorems,
a Visionary proposing connections, an Experimenter testing examples, Momus attacking
strategy, Veritas checking every deductive step, and a Chief Architect controlling the
process. Additional materials are unverified hints: any nonstandard lemma used from
them must be proved from scratch.

Run at most three global rounds.
1. Ideation: list materially different promising avenues, pre-mortem each for red
   herrings, and select an active strategy.
2. Dialectic loop: begin each round with a one-line poetic cognitive reset; draft or
   refine; reject and expand lazy phrases; let Momus discard a fatally flawed
   strategy; let Veritas flag invisible steps; switch strategy or repair until
   convergence or the round budget ends.
3. Synthesis: give a short discovery log and a clean reviewer-ready proof.

The final proof must restate what is proved, be self-contained, and check all cases and both directions. If the task asks for a proof, do not put the conclusion in \\boxed{}; end the completed proof with \\(\\square\\). If no complete proof is reached, preserve the strongest rigorous partial result and state exactly what remains. Do not use a reference answer.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort on this problem. Use the maximum reasoning effort available before producing the final response. Do not finalize merely because a plausible answer or familiar pattern has been found."""
FROZEN_USER_PREFIX = "Solve the stated problem from scratch using no outside materials.\n\nPROBLEM:\n"
FROZEN_USER_SUFFIX = """

ADDITIONAL MATERIALS:
None

EXTERNAL FEEDBACK FOR THIS DRAFT:
None

Apply the high-stakes deliberation requirement. Do not finalize until the independent verification pass is complete."""
PROBLEM_ONLY_JSON_KEYS = frozenset({"claim", "problem", "problem_id", "problem_number"})


class GPU0FourSlotStageRuntime(StageRuntime):
    """The frozen v0.3.48 Gemma runtime with four slots and a named GPU 0 endpoint."""

    def __init__(self, config: RuntimeConfig) -> None:
        # RuntimeConfig.validate() freezes an old port. The inherited generation
        # method itself is endpoint-agnostic, so v0.3.97 validates the model and
        # binds the explicitly named GPU 0 endpoint here.
        if config.gemma_model != GEMMA_MODEL:
            raise ValueError(f"GPU 0 must serve {GEMMA_MODEL}")
        if not config.gemma_endpoint.strip():
            raise ValueError("GPU 0 Gemma endpoint must be nonempty")
        self.config = config
        self._gemma_slots = threading.BoundedSemaphore(RAW_BATCH_SIZE)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_candidate_specs(seed_offset: int = 0) -> tuple[dict[str, Any], ...]:
    """A recorded attempt offset changes random streams, never task prompts."""
    if not isinstance(seed_offset, int) or not 0 <= seed_offset <= 0xFFFFFFFF:
        raise ValueError("raw seed offset must be a uint32")
    return tuple({**spec, "seed": (int(spec["seed"]) + seed_offset) & 0xFFFFFFFF}
                 for spec in RAW_CANDIDATES)


def stable_raw_seed(problem_number: int, candidate_id: str, base_seed: int) -> int:
    """Preserve the frozen v0.3.48 seed policy without importing its P4 driver."""
    material = (
        f"v048:p{problem_number}:{candidate_id}:{base_seed}:cold_draft"
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def run_cold_candidate(
    *,
    runtime: StageRuntime,
    problem: dict[str, Any],
    output_dir: Path,
    system_prompt: str,
    user_prompt: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    problem_number = int(problem["problem_number"])
    candidate_id = str(spec["candidate_id"])
    seed = stable_raw_seed(problem_number, candidate_id, int(spec["seed"]))
    candidate_dir = output_dir / f"p{problem_number}" / "candidates" / candidate_id
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
        "problem_number": problem_number,
        "problem_id": problem["problem_id"],
        "candidate_id": candidate_id,
        "temperature": float(spec["temperature"]),
        "seed": seed,
        "base_portfolio_seed": int(spec["seed"]),
        "proof": proof,
        "proof_sha256": sha256_text(proof),
        "proof_path": str(proof_path.resolve()),
        "cold_generation": generated,
    }
    write_json(candidate_dir / "cold_result.json", result)
    return result


def run_parallel_stage(
    *,
    rows: list[dict[str, Any]],
    worker: Callable[[dict[str, Any]], dict[str, Any]],
    stage: str,
    status_writer: Callable[[str, list[dict[str, Any]], list[dict[str, str]]], None],
    failure_handler: Callable | None = None,
) -> list[dict[str, Any]]:
    completed: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    status_writer(stage, completed, failures)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(worker, row): row for row in rows}
        for future in as_completed(futures):
            source = futures[future]
            try:
                completed.append(future.result())
            except Exception as error:
                failures.append(
                    {
                        "problem_number": str(source["problem_number"]),
                        "candidate_id": str(source["candidate_id"]),
                        "stage": stage,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
                if failure_handler is not None:
                    failure_handler(source, failures[-1])
            status_writer(stage, completed, failures)
    if failures and failure_handler is None:
        raise RuntimeError(f"{stage} failures: {failures}")
    completed.sort(
        key=lambda row: (int(row["problem_number"]), str(row["candidate_id"]))
    )
    return completed


def inferred_problem_number(problem_id: str) -> int:
    match = re.search(r"(?:^|[_-])p([0-9]+)$", problem_id, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def validate_problem_only_source(source_path: Path) -> dict[str, Any]:
    """Read only the statement envelope and reject any auxiliary input channel."""
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if source_path.suffix.lower() != ".json":
        return {"claim": source_path.read_text(encoding="utf-8").strip()}
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"problem-only JSON must be an object: {source_path}")
    unexpected = sorted(set(payload) - PROBLEM_ONLY_JSON_KEYS)
    if unexpected:
        raise ValueError(
            "problem-only JSON contains auxiliary fields: " + ", ".join(unexpected)
        )
    statement_fields = [key for key in ("claim", "problem") if key in payload]
    if len(statement_fields) != 1:
        raise ValueError("problem-only JSON requires exactly one of claim or problem")
    if not isinstance(payload[statement_fields[0]], str):
        raise ValueError("problem statement must be a string")
    if "problem_id" in payload and not isinstance(payload["problem_id"], str):
        raise ValueError("problem_id must be a string")
    if "problem_number" in payload and not isinstance(payload["problem_number"], int):
        raise ValueError("problem_number must be an integer")
    return payload


def normalize_problem_input(
    *,
    source_path: Path,
    output_dir: Path,
    problem_id_override: str | None = None,
    problem_number_override: int | None = None,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    payload = validate_problem_only_source(source_path)
    if source_path.suffix.lower() == ".json":
        claim = str(payload.get("claim") or payload.get("problem") or "").strip()
        source_problem_id = str(payload.get("problem_id") or "").strip()
        source_problem_number = payload.get("problem_number")
    else:
        claim = str(payload["claim"]).strip()
        source_problem_id = ""
        source_problem_number = None
    if not claim:
        raise ValueError(f"problem statement is empty: {source_path}")
    problem_id = str(problem_id_override or source_problem_id or source_path.stem).strip()
    if not problem_id:
        raise ValueError("problem_id is required")
    if problem_id_override is not None and source_problem_id and problem_id != source_problem_id:
        raise ValueError("problem_id override does not match the problem-only source")
    if problem_number_override is not None:
        problem_number = int(problem_number_override)
    elif source_problem_number is not None:
        problem_number = int(source_problem_number)
    else:
        problem_number = inferred_problem_number(problem_id)
    if (
        problem_number_override is not None
        and source_problem_number is not None
        and problem_number != int(source_problem_number)
    ):
        raise ValueError("problem_number override does not match the problem-only source")
    if problem_number < 0:
        raise ValueError("problem_number must be nonnegative")
    normalized = {
        "schema": "cognitive-well-v097-normalized-problem-v1",
        "problem_id": problem_id,
        "problem_number": problem_number,
        "claim": claim,
        "source_path": str(source_path),
        "source_sha256": file_sha256(source_path),
    }
    normalized_path = output_dir / "input" / "problem.json"
    write_json(normalized_path, normalized)
    return {
        "problem_number": problem_number,
        "problem_id": problem_id,
        "claim": claim,
        "path": normalized_path.resolve(),
        "sha256": sha256_text(claim),
        "source_path": source_path,
        "source_sha256": normalized["source_sha256"],
    }


def build_frozen_raw_prompts(problem: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    system_prompt = FROZEN_SYSTEM_PROMPT
    user_prompt = FROZEN_USER_PREFIX + str(problem["claim"]) + FROZEN_USER_SUFFIX
    if user_prompt.count(str(problem["claim"])) != 1:
        raise ValueError("problem statement occurs ambiguously in the frozen prompt")
    return system_prompt, user_prompt, {
        "control_dir": None,
        "prompt_source": "version_owned_problem_neutral_constants",
        "runtime_cross_problem_artifact_reads": False,
        "system_prompt_sha256": sha256_text(system_prompt),
        "user_prompt_sha256": sha256_text(user_prompt),
        "only_variable_region": "problem_statement",
    }


def phase_one_manifest(
    *,
    problem: dict[str, Any],
    prompt_identity: dict[str, Any],
    gpu0_gemma_endpoint: str,
    raw_seed_offset: int = 0,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v097-raw-lazy-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem": {
            "problem_number": problem["problem_number"],
            "problem_id": problem["problem_id"],
            "problem_path": str(Path(problem["path"]).resolve()),
            "problem_sha256": problem["sha256"],
        },
        "candidate_allocation": {"temperature_1.0": 2, "temperature_0.7": 2},
        "candidate_count": len(RAW_CANDIDATES),
        **({"raw_seed_offset": raw_seed_offset} if raw_seed_offset else {}),
        "candidate_specs": [
            {
                **dict(spec),
                "seed_policy": "frozen_v048_sha256_problem_candidate_base_seed",
            }
            for spec in raw_candidate_specs(raw_seed_offset)
        ],
        "raw_generation": {
            "device": "gpu0",
            "endpoint": gpu0_gemma_endpoint,
            **GPU0_GEMMA_PROFILE,
            "max_reasoning": True,
            "batch_size": RAW_BATCH_SIZE,
            "top_p": 0.95,
            "top_k": 64,
            "max_tokens": BASELINE_MAX_TOKENS,
            "cap_recovery_max_tokens": BASELINE_MAX_TOKENS * 2,
        },
        "lazy_check": {
            "device": "gpu0",
            "temperature": 0.1,
            "max_tokens": 8_192,
            "unconditional": True,
        },
        "conditional_in_place_expansion": {
            "device": "gpu0",
            "temperature": LAZY_RESOLVE_TEMPERATURE,
            "max_tokens": 65_536,
            "cap_recovery_max_tokens": 131_072,
            "only_when_lazy_check_reports_an_issue": True,
            "prompt_sha256": EXPECTED_PROMPT_SHA256,
        },
        "prompt_identity": prompt_identity,
        "reference_solution_access": False,
        "problem_specific_prompting": False,
    }


def build_v096_cases_manifest(
    *, problem: dict[str, Any], final_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    by_id = {str(row["candidate_id"]): row for row in final_rows}
    if set(by_id) != set(RAW_CANDIDATE_IDS):
        raise ValueError(
            f"checked candidates differ from the four-proof allocation: {sorted(by_id)}"
        )
    return {
        "schema": "cognitive-well-v096-cases-v1",
        "source_harness_version": HARNESS_VERSION,
        "cases": [
            {
                "case_id": f"{problem['problem_id']}.{candidate_id}",
                "mode": "fresh",
                "proof_index": index,
                "problem_path": str(Path(problem["path"]).resolve()),
                "proof_path": str(Path(by_id[candidate_id]["checked_proof_path"]).resolve()),
                "problem_number": int(problem["problem_number"]),
                "problem_id": str(problem["problem_id"]),
                "candidate_id": candidate_id,
            }
            for index, candidate_id in enumerate(RAW_CANDIDATE_IDS)
        ],
    }


def run(
    *,
    problem_file: Path,
    output_dir: Path,
    gpu0_gemma_endpoint: str,
    gpu1_qwen_endpoint: str,
    seed_namespace: str,
    problem_id: str | None = None,
    problem_number: int | None = None,
    dry_run: bool = False,
    stop_after_lazy: bool = False,
    continue_failed_lanes: bool = False,
    raw_seed_offset: int = 0,
) -> dict[str, Any]:
    if continue_failed_lanes and not stop_after_lazy:
        raise ValueError("Partial frontend handoff requires stop_after_lazy")
    specs = raw_candidate_specs(raw_seed_offset)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    gpu0_gemma_endpoint = gpu0_gemma_endpoint.rstrip("/")
    gpu1_qwen_endpoint = gpu1_qwen_endpoint.rstrip("/")
    if not gpu0_gemma_endpoint or not gpu1_qwen_endpoint:
        raise ValueError("both explicitly named GPU endpoints are required")
    if gpu0_gemma_endpoint == gpu1_qwen_endpoint:
        raise ValueError("GPU 0 Gemma and GPU 1 Qwen endpoints must be distinct")

    problem = normalize_problem_input(
        source_path=problem_file,
        output_dir=output_dir,
        problem_id_override=problem_id,
        problem_number_override=problem_number,
    )
    system_prompt, user_prompt, prompt_identity = build_frozen_raw_prompts(problem)
    phase_one_dir = output_dir / "phase_1_raw_lazy"
    phase_one_dir.mkdir(parents=True, exist_ok=True)
    (phase_one_dir / "cold_system_prompt.txt").write_text(system_prompt, encoding="utf-8")
    (phase_one_dir / "cold_user_prompt.txt").write_text(user_prompt, encoding="utf-8")
    raw_manifest = phase_one_manifest(
        problem=problem,
        prompt_identity=prompt_identity,
        gpu0_gemma_endpoint=gpu0_gemma_endpoint, raw_seed_offset=raw_seed_offset,
    )
    write_json(phase_one_dir / "manifest.json", raw_manifest)
    parent_manifest = {
        "schema": "cognitive-well-v097-end-to-end-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_path": str(Path(problem["path"]).resolve()),
        "problem_id": problem["problem_id"],
        "problem_number": problem["problem_number"],
        "device_roles": {
            "gpu0": {
                "endpoint": gpu0_gemma_endpoint,
                **GPU0_GEMMA_PROFILE,
                "stages": [
                    "raw_generation",
                    "lazy_check",
                    "conditional_in_place_expansion",
                    "reviewer_1",
                    "reviewer_3",
                    "reviewer_1_trace_enhancement",
                    "reviewer_3_trace_enhancement",
                    "fusion",
                    "resolver",
                ],
            },
            "gpu1": {
                "endpoint": gpu1_qwen_endpoint,
                "model": "Qwen/Qwen3.6-27B",
                "stages": ["reviewer_2"],
            },
        },
        "review_schedule": {
            "gpu0": "reviewer_1_batch_of_4_then_reviewer_3_batch_of_4",
            "gpu1": "reviewer_2_batch_of_4_concurrent_with_gpu0_review_branch",
            "barrier_before_fusion": True,
        },
        "gemma_profile_policy": "one GPU 0 endpoint and one immutable profile for every Gemma stage",
        "problem_specific_prompting": False,
    }
    if stop_after_lazy:
        parent_manifest["terminal_checkpoint"] = "lazy_checked"
        parent_manifest["downstream_manifest_only"] = True
        parent_manifest["device_roles"]["gpu0"]["stages"] = [
            "raw_generation", "lazy_check", "conditional_in_place_expansion",
        ]
        parent_manifest["device_roles"]["gpu1"]["stages"] = []
    write_json(output_dir / "manifest.json", parent_manifest)

    if dry_run:
        summary = {
            "schema": "cognitive-well-v097-dry-run-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "candidate_ids": list(RAW_CANDIDATE_IDS),
            "candidate_temperatures": [float(row["temperature"]) for row in RAW_CANDIDATES],
            "review_schedule": parent_manifest["review_schedule"],
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()},
        )
        return summary

    config = RuntimeConfig(gemma_endpoint=gpu0_gemma_endpoint)
    runtime = GPU0FourSlotStageRuntime(config)
    status_lock = threading.Lock()
    total = len(RAW_CANDIDATES)

    def phase_one_status(
        stage: str,
        completed: list[dict[str, Any]],
        failures: list[dict[str, str]],
    ) -> None:
        payload = {
            "state": "running",
            "stage": stage,
            "completed_count": len(completed),
            "failed": failures,
            "total": total,
            "device": "gpu0",
            "updated_at": utc_now(),
        }
        with status_lock:
            write_json(phase_one_dir / "status.json", payload)
            write_json(output_dir / "status.json", {**payload, "phase": "phase_1_raw_lazy"})

    source_rows = [
        {
            "problem_number": int(problem["problem_number"]),
            "candidate_id": str(spec["candidate_id"]),
            "problem": problem,
            "spec": dict(spec),
        }
        for spec in specs
    ]
    from experiments.local_math_verifier import frontend_portfolio
    failed_lanes = {}

    def retain_failure(source, failure):
        failed_lanes[source["candidate_id"]] = frontend_portfolio.save_failure(
            output_dir, problem, source, failure)

    # Persisted lane failures are terminal. Never replay them on a frontend resume.
    if continue_failed_lanes:
        for row in source_rows:
            path = frontend_portfolio.candidate_dir(
                output_dir, problem["problem_number"], row["candidate_id"]) / "frontend_failure.json"
            if path.is_file():
                failed_lanes[row["candidate_id"]] = frontend_portfolio.read(path)
        source_rows = [row for row in source_rows if row["candidate_id"] not in failed_lanes]
    failure_handler = retain_failure if continue_failed_lanes else None
    try:
        cold_rows = run_parallel_stage(
            rows=source_rows,
            stage="raw_generation_batch_of_4",
            status_writer=phase_one_status,
            failure_handler=failure_handler,
            worker=lambda row: run_cold_candidate(
                runtime=runtime,
                problem=row["problem"],
                output_dir=phase_one_dir,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                spec=row["spec"],
            ),
        )
        lazy_rows = run_parallel_stage(
            rows=cold_rows,
            stage="lazy_check_batch_of_4",
            status_writer=phase_one_status,
            failure_handler=failure_handler,
            worker=lambda row: run_lazy_check(
                runtime=runtime,
                output_dir=phase_one_dir / f"p{int(problem['problem_number'])}",
                row=row,
            ),
        )
        final_rows = run_parallel_stage(
            rows=lazy_rows,
            stage="conditional_in_place_expansion_batch",
            status_writer=phase_one_status,
            failure_handler=failure_handler,
            worker=lambda row: {
                **run_lazy_resolve(
                    runtime=runtime,
                    problem=str(problem["claim"]),
                    output_dir=phase_one_dir / f"p{int(problem['problem_number'])}",
                    row=row,
                ),
                "problem_number": int(problem["problem_number"]),
                "problem_id": str(problem["problem_id"]),
            },
        )
        if failed_lanes:
            summary = frontend_portfolio.finish(output_dir, problem, RAW_CANDIDATE_IDS, final_rows, failed_lanes)
            frontend_portfolio.load(output_dir, problem["problem_number"], problem["problem_id"])
            return summary
        cases_manifest = build_v096_cases_manifest(problem=problem, final_rows=final_rows)
        cases_path = output_dir / "phase_2_v096_cases.json"
        write_json(cases_path, cases_manifest)
        write_json(
            output_dir / "status.json",
            {
                "state": "running",
                "phase": "phase_2_input_preparation" if stop_after_lazy else "phase_2_enhanced_reviews_fusion_resolver",
                "stage": "prepare_manifest_only" if stop_after_lazy else "split_gpu_reviews",
                "updated_at": utc_now(),
            },
        )
        downstream = enhanced_pipeline.run(
            cases_manifest=cases_path,
            output_dir=output_dir / "phase_2_v096",
            gemma_endpoints=[gpu0_gemma_endpoint],
            qwen_endpoint=gpu1_qwen_endpoint,
            workers_per_endpoint=REVIEW_BATCH_SIZE,
            seed_namespace=seed_namespace,
            dry_run=stop_after_lazy,
            allowed_input_root=output_dir,
        )
    except Exception as error:
        write_json(
            output_dir / "status.json",
            {
                "state": "failed",
                "stage": "end_to_end_pipeline",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise

    phase_one_result = {
        **raw_manifest,
        "schema": "cognitive-well-v097-raw-lazy-result-v1",
        "state": "completed",
        "results": final_rows,
        "lazy_resolve_count": sum(bool(row["lazy_resolve_invoked"]) for row in final_rows),
        "completed_at": utc_now(),
    }
    write_json(phase_one_dir / "result.json", phase_one_result)
    summary = {
        "schema": "cognitive-well-v097-end-to-end-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "problem_id": problem["problem_id"],
        "candidate_count": len(final_rows),
        "candidate_ids": list(RAW_CANDIDATE_IDS),
        "phase_1_result_path": str((phase_one_dir / "result.json").resolve()),
        "phase_2_summary_path": str((output_dir / "phase_2_v096" / "summary.json").resolve()),
        "phase_2": downstream,
        "completed_at": utc_now(),
    }
    if stop_after_lazy:
        summary["terminal_checkpoint"] = "lazy_checked"
        summary["downstream_model_calls_performed"] = 0
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "status.json",
        {"state": "completed", "stage": "done", "updated_at": utc_now()},
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Four raw/lazy proofs -> enhanced three-review/Fusion/Resolver pipeline"
    )
    parser.add_argument("--problem-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--problem-id")
    parser.add_argument("--problem-number", type=int)
    parser.add_argument("--gpu0-gemma-endpoint", default=DEFAULT_GPU0_GEMMA_ENDPOINT)
    parser.add_argument("--gpu1-qwen-endpoint", default=DEFAULT_GPU1_QWEN_ENDPOINT)
    parser.add_argument("--seed-namespace", default="v097")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(
        problem_file=args.problem_file,
        output_dir=args.output_dir,
        gpu0_gemma_endpoint=args.gpu0_gemma_endpoint,
        gpu1_qwen_endpoint=args.gpu1_qwen_endpoint,
        seed_namespace=args.seed_namespace,
        problem_id=args.problem_id,
        problem_number=args.problem_number,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
