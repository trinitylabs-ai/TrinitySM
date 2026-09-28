from __future__ import annotations

import argparse
import hashlib
import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from experiments.local_math_verifier.runtime import utc_now, write_json

from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.pipeline import (
    nonempty_parser,
)
from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.runtime import (
    GEMMA_MODEL,
    RuntimeConfig,
    StageRuntime,
)
from cognitive_well_harness_v0_3_42_gemma4_dual_prompt_max_thinking_coldsolve_20260823.run import (
    BASELINE_MAX_TOKENS,
    load_control,
)
from cognitive_well_harness_v0_3_45_gemma4_high_stakes_no_checklist_coldsolve_20260823.run import (
    experimental_prompts,
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

from . import HARNESS_VERSION


DEFAULT_PROBLEMS = (1, 2, 3, 5, 6)
SUPPORTED_PROBLEMS = (1, 2, 3, 4, 5, 6)
MAX_WORKERS = 10
MAX_ACTIVE_GEMMA_SEQUENCES = 4
CONTROL_DIR = Path(
    "runs/v037_p4_one_rep_20260822_2313/replication_01/"
    "stage1_cold_generation/draft"
)
PROBLEM_ROOT = Path("math_harness_inputs/imo2026_p4_p2_v0313_20260815")


class FourSlotStageRuntime(StageRuntime):
    """Use all four active sequences exposed by the BF16/MTP4 service."""

    def __init__(self, config: RuntimeConfig) -> None:
        super().__init__(config)
        self._gemma_slots = threading.BoundedSemaphore(MAX_ACTIVE_GEMMA_SEQUENCES)


def stable_seed(problem_number: int, candidate_id: str, base_seed: int) -> int:
    material = (
        f"v048:p{problem_number}:{candidate_id}:{base_seed}:cold_draft"
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def load_problem(problem_number: int) -> dict[str, Any]:
    path = PROBLEM_ROOT / f"imo2026_p{problem_number}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    claim = str(data.get("claim") or "").strip()
    problem_id = str(data.get("problem_id") or "").strip()
    if not claim or problem_id != f"imo2026_p{problem_number}":
        raise ValueError(f"invalid problem payload: {path}")
    return {
        "problem_number": problem_number,
        "problem_id": problem_id,
        "claim": claim,
        "path": path,
        "sha256": sha256_text(claim),
    }


def generalized_prompts(problems: list[dict[str, Any]]) -> tuple[str, dict[int, str]]:
    control = load_control(CONTROL_DIR)
    system_prompt, p4_user_prompt = experimental_prompts(control["system_prompt"])
    p4 = load_problem(4)
    if p4_user_prompt.count(p4["claim"]) != 1:
        raise ValueError("the frozen P4 user prompt has an ambiguous problem block")
    static_prefix, static_suffix = p4_user_prompt.split(str(p4["claim"]), 1)
    user_prompts = {
        int(row["problem_number"]): static_prefix + str(row["claim"]) + static_suffix
        for row in problems
    }
    for row in problems:
        number = int(row["problem_number"])
        target = str(row["claim"])
        prompt = user_prompts[number]
        if prompt.count(target) != 1:
            raise ValueError(f"P{number} user prompt has an ambiguous problem block")
        observed_prefix, observed_suffix = prompt.split(target, 1)
        if observed_prefix != static_prefix or observed_suffix != static_suffix:
            raise RuntimeError(
                f"P{number} cold prompt changed outside the problem-statement bytes"
            )
        if observed_prefix + str(p4["claim"]) + observed_suffix != p4_user_prompt:
            raise RuntimeError(f"P{number} cold prompt cannot reconstruct the control")
    return system_prompt, user_prompts


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
    seed = stable_seed(problem_number, candidate_id, int(spec["seed"]))
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
            status_writer(stage, completed, failures)
    if failures:
        raise RuntimeError(f"{stage} failures: {failures}")
    completed.sort(
        key=lambda row: (int(row["problem_number"]), str(row["candidate_id"]))
    )
    return completed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run six-candidate cold/lazy/expansion portfolios for IMO problems"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--problems", type=int, nargs="+", default=list(DEFAULT_PROBLEMS)
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    problem_numbers = tuple(args.problems)
    if len(set(problem_numbers)) != len(problem_numbers):
        raise ValueError("problem numbers must be unique")
    if not problem_numbers or any(
        number not in SUPPORTED_PROBLEMS for number in problem_numbers
    ):
        raise ValueError(f"problems must be selected from {SUPPORTED_PROBLEMS}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    problems = [load_problem(number) for number in problem_numbers]
    problem_by_number = {int(row["problem_number"]): row for row in problems}
    system_prompt, user_prompts = generalized_prompts(problems)
    control = load_control(CONTROL_DIR)
    control_system_prompt, control_user_prompt = experimental_prompts(
        control["system_prompt"]
    )
    p4_claim = str(load_problem(4)["claim"])
    cold_static_prefix, cold_static_suffix = control_user_prompt.split(p4_claim, 1)
    if system_prompt != control_system_prompt:
        raise RuntimeError("generalized system prompt differs from the frozen control")
    config = RuntimeConfig()
    config.validate(require_files=False)
    runtime = FourSlotStageRuntime(config)
    total = len(problems) * len(CANDIDATES)
    manifest = {
        "schema": "cognitive-well-v048-multi-problem-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problems": [
            {
                "problem_number": row["problem_number"],
                "problem_id": row["problem_id"],
                "problem_path": str(Path(row["path"]).resolve()),
                "problem_sha256": row["sha256"],
                "user_prompt_sha256": sha256_text(
                    user_prompts[int(row["problem_number"])]
                ),
            }
            for row in problems
        ],
        "candidate_allocation_per_problem": {
            "temperature_1.0": 4,
            "temperature_0.7": 2,
        },
        "candidate_count_per_problem": len(CANDIDATES),
        "total_candidate_count": total,
        "candidate_specs": [
            {
                **spec,
                "per_problem_seed_policy": "sha256(v048, problem, candidate, base_seed)",
            }
            for spec in CANDIDATES
        ],
        "system_prompt_sha256": sha256_text(system_prompt),
        "cold_prompt_control": {
            "control_problem": 4,
            "only_variable_region": "problem_statement",
            "system_prompt_byte_identical": True,
            "user_static_prefix_sha256": sha256_text(cold_static_prefix),
            "user_static_suffix_sha256": sha256_text(cold_static_suffix),
            "additional_materials_unchanged": True,
            "external_feedback_unchanged": True,
            "high_stakes_reminder_unchanged": True,
        },
        "model": GEMMA_MODEL,
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "max_active_gemma_sequences": MAX_ACTIVE_GEMMA_SEQUENCES,
        "thinking_template_enabled": True,
        "top_p": 0.95,
        "top_k": 64,
        "cold_max_tokens": BASELINE_MAX_TOKENS,
        "cold_cap_recovery_max_tokens": BASELINE_MAX_TOKENS * 2,
        "lazy_check_temperature": 0.1,
        "lazy_check_max_tokens": config.lazy_max_tokens,
        "lazy_resolve_temperature": LAZY_RESOLVE_TEMPERATURE,
        "lazy_resolve_max_tokens": config.solver_max_tokens,
        "lazy_resolve_cap_recovery_max_tokens": config.solver_max_tokens * 2,
        "lazy_resolve_prompt_sha256": EXPECTED_PROMPT_SHA256,
        "reference_solution_access_during_generation": False,
        "gold_scoring_is_separate_post_generation_stage": True,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    (args.output_dir / "cold_system_prompt.txt").write_text(
        system_prompt, encoding="utf-8"
    )
    for number, prompt in user_prompts.items():
        problem_dir = args.output_dir / f"p{number}"
        problem_dir.mkdir(parents=True, exist_ok=True)
        (problem_dir / "cold_user_prompt.txt").write_text(prompt, encoding="utf-8")

    lock = threading.Lock()

    def status_writer(
        stage: str,
        completed: list[dict[str, Any]],
        failures: list[dict[str, str]],
    ) -> None:
        counts = {
            str(number): sum(
                int(row["problem_number"]) == number for row in completed
            )
            for number in problem_numbers
        }
        with lock:
            write_json(
                args.output_dir / "status.json",
                {
                    "state": "running",
                    "stage": stage,
                    "completed_count": len(completed),
                    "completed_per_problem": counts,
                    "failed": failures,
                    "total": total,
                    "updated_at": utc_now(),
                },
            )

    source_rows = [
        {
            "problem_number": int(problem["problem_number"]),
            "candidate_id": str(spec["candidate_id"]),
            "problem": problem,
            "spec": dict(spec),
        }
        for problem in problems
        for spec in CANDIDATES
    ]
    try:
        cold_rows = run_parallel_stage(
            rows=source_rows,
            stage="cold_generation",
            status_writer=status_writer,
            worker=lambda row: run_cold_candidate(
                runtime=runtime,
                problem=row["problem"],
                output_dir=args.output_dir,
                system_prompt=system_prompt,
                user_prompt=user_prompts[int(row["problem_number"])],
                spec=row["spec"],
            ),
        )
        lazy_rows = run_parallel_stage(
            rows=cold_rows,
            stage="lazy_check",
            status_writer=status_writer,
            worker=lambda row: {
                **run_lazy_check(
                    runtime=runtime,
                    output_dir=args.output_dir / f"p{int(row['problem_number'])}",
                    row=row,
                ),
                "problem_number": int(row["problem_number"]),
                "problem_id": row["problem_id"],
            },
        )
        final_rows = run_parallel_stage(
            rows=lazy_rows,
            stage="lazy_in_place_resolve",
            status_writer=status_writer,
            worker=lambda row: {
                **run_lazy_resolve(
                    runtime=runtime,
                    problem=str(problem_by_number[int(row["problem_number"])]["claim"]),
                    output_dir=args.output_dir / f"p{int(row['problem_number'])}",
                    row=row,
                ),
                "problem_number": int(row["problem_number"]),
                "problem_id": row["problem_id"],
            },
        )
    except Exception as error:
        write_json(
            args.output_dir / "status.json",
            {
                "state": "failed",
                "stage": "generation_pipeline",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise

    per_problem: dict[str, Any] = {}
    for number in problem_numbers:
        rows = [row for row in final_rows if int(row["problem_number"]) == number]
        if len(rows) != len(CANDIDATES):
            raise RuntimeError(f"P{number} produced {len(rows)} final candidates")
        summary = {
            "schema": "cognitive-well-v048-problem-result-v1",
            "problem_number": number,
            "problem_id": problem_by_number[number]["problem_id"],
            "candidate_count": len(rows),
            "results": rows,
            "completed_at": utc_now(),
        }
        write_json(args.output_dir / f"p{number}" / "result.json", summary)
        per_problem[str(number)] = {
            "candidate_count": len(rows),
            "lazy_resolve_count": sum(row["lazy_resolve_invoked"] for row in rows),
            "conclusion_change_count": sum(
                row["conclusion_action"] == "CHANGE" for row in rows
            ),
        }
    result = {
        **manifest,
        "schema": "cognitive-well-v048-multi-problem-result-v1",
        "state": "completed",
        "per_problem": per_problem,
        "completed_at": utc_now(),
    }
    write_json(args.output_dir / "result.json", result)
    write_json(
        args.output_dir / "status.json",
        {
            "state": "completed",
            "stage": "lazy_in_place_resolve",
            "completed_count": len(final_rows),
            "completed_per_problem": {
                str(number): len(CANDIDATES) for number in problem_numbers
            },
            "failed": [],
            "total": total,
            "updated_at": utc_now(),
        },
    )
    if not args.quiet:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
