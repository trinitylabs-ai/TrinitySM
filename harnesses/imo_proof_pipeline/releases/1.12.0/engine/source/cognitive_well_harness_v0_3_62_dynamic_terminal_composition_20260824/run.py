from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823 import (
    protocol as reviewer1,
)
from cognitive_well_harness_v0_3_57_v030_cross_model_pair_dossier_ab_20260824 import (
    run_arm as base,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)
from scripts import run_imo2026_p1_p4_cutoff_gold_codex_audit_20260817 as gold_grader

from . import HARNESS_VERSION
from .protocol import (
    deterministic_composition_gate,
    load_dynamic_verified_arguments,
    sha256_text,
    terminal_composition_prompt,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUN = ROOT / "runs/v061_atomic_hypothesis_p5_pair_dossier_ab_20260824"
VERIFIED_SOURCE = (
    SOURCE_RUN
    / "diagnostic/hypothesis_round_1/round_summary.json"
)
PROBLEM_PATH = ROOT / "math_harness_inputs/imo2026_p4_p2_v0313_20260815/imo2026_p5.json"
REFERENCE_PATH = ROOT / "math_harness_references/imo2026_mechmath_20260817/Q5_solution.txt"
CODEX_SCHEMA = ROOT / (
    "cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812/"
    "codex_grade_schema.json"
)
GEMMA_ENDPOINT = "http://127.0.0.1:8020/v1"
QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
CODEX_MODEL = "gpt-5.6-sol"
CODEX_REASONING_EFFORT = "xhigh"
CONFIGURATIONS = (
    {"candidate_id": "t02_s1", "temperature": 0.2, "replicate": 1},
    {"candidate_id": "t02_s2", "temperature": 0.2, "replicate": 2},
    {"candidate_id": "t04_s1", "temperature": 0.4, "replicate": 1},
    {"candidate_id": "t04_s2", "temperature": 0.4, "replicate": 2},
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def load_problem() -> tuple[str, str]:
    payload = read_json(PROBLEM_PATH)
    return str(payload["problem_id"]), str(payload["claim"])


def generate_candidate(
    *, output_root: Path, problem: str, arguments: list[dict[str, str]], config: dict[str, Any]
) -> dict[str, Any]:
    candidate_id = str(config["candidate_id"])
    destination = output_root / "candidates" / candidate_id
    prompt = terminal_composition_prompt(problem=problem, arguments=arguments)
    generated = base.saved_generation(destination, "composition")
    if generated is None:
        generated = base.gemma_text(
            endpoint=GEMMA_ENDPOINT,
            prompt=prompt,
            destination=destination,
            stage="composition",
            seed_label=f"v062:{candidate_id}:composition",
            temperature=float(config["temperature"]),
            max_tokens=32_768,
        )
    proof = str(generated["text"]).strip()
    gate = deterministic_composition_gate(proof)
    result = {
        **config,
        "proof": proof,
        "proof_sha256": sha256_text(proof),
        "dynamic_argument_count": len(arguments),
        "dynamic_arguments_sha256": sha256_text(
            json.dumps(arguments, ensure_ascii=False, sort_keys=True)
        ),
        "deterministic_gate": gate,
        "generation": generated["metadata"],
    }
    write_json(destination / "composition_result.json", result)
    (destination / "proof.md").write_text(proof + "\n", encoding="utf-8")
    return result


def run_reviewer1(
    *, output_root: Path, problem: str, candidate: dict[str, Any]
) -> dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    destination = output_root / "candidates" / candidate_id / "reviewer1"
    destination.mkdir(parents=True, exist_ok=True)
    generated = base.saved_generation(destination, "earliest_break")
    if generated is None:
        generated = run_openai_chat_generation(
            endpoint=QWEN_ENDPOINT,
            model=base.QWEN_MODEL,
            prompt=reviewer1.SYSTEM_PROMPT,
            user_prompt=reviewer1.review_user_prompt(
                problem=problem, proof=str(candidate["proof"])
            ),
            output_dir=destination,
            stage="earliest_break",
            config=HTTPGenerationConfig(
                max_tokens=12_288,
                temperature=0.2,
                top_p=1.0,
                top_k=-1,
                seed=base.stable_seed(f"v062:{candidate_id}:reviewer1"),
                thinking_token_budget=None,
                reasoning_effort="max",
                repetition_detection=base.REPETITION_DETECTION,
                timeout_seconds=14_400,
            ),
        )
    parsed = reviewer1.parse_review(str(generated["text"]))
    result = {
        "candidate_id": candidate_id,
        "temperature": 0.2,
        "review": parsed,
        "generation": generated["metadata"],
    }
    write_json(destination / "result.json", result)
    return result


def codex_grade(
    *, output_root: Path, problem_id: str, problem: str, reference: str, candidate: dict[str, Any]
) -> dict[str, Any]:
    candidate_id = str(candidate["candidate_id"])
    destination = output_root / "candidates" / candidate_id / "codex_gold"
    final_path = destination / "grade.json"
    if final_path.is_file():
        saved = read_json(final_path)
        if saved.get("grade"):
            return saved
    destination.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix=f"v062_{candidate_id}_gold_sol_xhigh_") as isolated:
        isolated_dir = Path(isolated)
        last_message = isolated_dir / "last_message.json"
        grader_candidate = {
            "problem": problem,
            "gold_reference": reference,
            "stage": "terminal composition",
            "candidate_id": "anonymous",
            "proof": candidate["proof"],
        }
        for attempt in range(1, 3):
            command = [
                "codex",
                "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--model",
                CODEX_MODEL,
                "--config",
                f'model_reasoning_effort="{CODEX_REASONING_EFFORT}"',
                "--output-schema",
                str(CODEX_SCHEMA),
                "--output-last-message",
                str(last_message),
                "--json",
                "--color",
                "never",
                "--cd",
                str(isolated_dir),
                "-",
            ]
            completed = subprocess.run(
                command,
                input=gold_grader.prompt(grader_candidate),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=7_200,
                check=False,
            )
            with (destination / "codex.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "attempt": attempt,
                            "returncode": completed.returncode,
                            "model": CODEX_MODEL,
                            "reasoning_effort": CODEX_REASONING_EFFORT,
                        }
                    )
                    + "\n"
                )
                handle.write(completed.stdout)
                if completed.stdout and not completed.stdout.endswith("\n"):
                    handle.write("\n")
            if completed.returncode != 0 or not last_message.is_file():
                failures.append(f"attempt {attempt}: returncode={completed.returncode}")
                continue
            try:
                grade = gold_grader.validate_grade(read_json(last_message))
            except Exception as error:
                failures.append(f"attempt {attempt}: {type(error).__name__}: {error}")
                continue
            record = {
                "schema": "gold-informed-codex-math-grade-v1",
                "created_at": utc_now(),
                "grader": CODEX_MODEL,
                "reasoning_effort": CODEX_REASONING_EFFORT,
                "reference_informed": True,
                "generation_or_qwen_metadata_visible": False,
                "problem_id": problem_id,
                "candidate_id": candidate_id,
                "proof_sha256": candidate["proof_sha256"],
                "grade": grade,
                "attempt": attempt,
            }
            write_json(final_path, record)
            return record
    record = {
        "schema": "gold-informed-codex-math-grade-v1",
        "created_at": utc_now(),
        "grader": CODEX_MODEL,
        "candidate_id": candidate_id,
        "proof_sha256": candidate["proof_sha256"],
        "error": " | ".join(failures),
    }
    write_json(final_path, record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay diagnostic terminal composition with dynamically loaded lemmas"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output_root: Path = args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)
    problem_id, problem = load_problem()
    arguments = load_dynamic_verified_arguments(VERIFIED_SOURCE)
    dynamic_digest = sha256_text(json.dumps(arguments, ensure_ascii=False, sort_keys=True))
    write_json(
        output_root / "manifest.json",
        {
            "schema": "cognitive-well-v0.3.62-dynamic-terminal-composition-manifest-v1",
            "created_at": utc_now(),
            "harness_version": HARNESS_VERSION,
            "experiment": "diagnostic_terminal_composition_only",
            "extraction_rerun": False,
            "resolver_rerun": False,
            "lemma_content_hardcoded": False,
            "dynamic_verified_source": str(VERIFIED_SOURCE.resolve()),
            "dynamic_verified_source_sha256": hashlib.sha256(
                VERIFIED_SOURCE.read_bytes()
            ).hexdigest(),
            "dynamic_argument_count": len(arguments),
            "dynamic_arguments_sha256": dynamic_digest,
            "dynamic_argument_fields_inserted": ["statement", "proof"],
            "dynamic_argument_fields_excluded": [
                "lemma_id",
                "direction",
                "qwen_audit",
                "extraction_round",
            ],
            "constructive_model": {
                "model": base.GEMMA_MODEL,
                "dtype": "bfloat16",
                "mtp": 4,
                "endpoint": GEMMA_ENDPOINT,
                "reasoning_effort": "max",
            },
            "reviewer_model": {
                "model": base.QWEN_MODEL,
                "dtype": "bfloat16",
                "endpoint": QWEN_ENDPOINT,
                "role": "reviewer_1_earliest_break_non_scoring",
                "temperature": 0.2,
                "reasoning_effort": "max",
            },
            "codex_grader": {
                "model": CODEX_MODEL,
                "reasoning_effort": CODEX_REASONING_EFFORT,
                "blind_to_generation_and_qwen_metadata": True,
            },
            "configurations": CONFIGURATIONS,
            "terra_calls": 0,
            "gold_or_reference_accessed_by_composition": False,
        },
    )
    try:
        write_json(output_root / "status.json", {"state": "running", "stage": "composition", "updated_at": utc_now()})
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            candidates = list(
                executor.map(
                    lambda config: generate_candidate(
                        output_root=output_root,
                        problem=problem,
                        arguments=arguments,
                        config=config,
                    ),
                    CONFIGURATIONS,
                )
            )
        write_json(output_root / "status.json", {"state": "running", "stage": "qwen_reviewer1", "candidate_count": len(candidates), "updated_at": utc_now()})
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            reviews = list(
                executor.map(
                    lambda candidate: run_reviewer1(
                        output_root=output_root, problem=problem, candidate=candidate
                    ),
                    candidates,
                )
            )
        write_json(output_root / "status.json", {"state": "running", "stage": "codex_gold_scoring", "candidate_count": len(candidates), "updated_at": utc_now()})
        reference = REFERENCE_PATH.read_text(encoding="utf-8").strip()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            grades = list(
                executor.map(
                    lambda candidate: codex_grade(
                        output_root=output_root,
                        problem_id=problem_id,
                        problem=problem,
                        reference=reference,
                        candidate=candidate,
                    ),
                    candidates,
                )
            )
        review_by_id = {row["candidate_id"]: row for row in reviews}
        grade_by_id = {row["candidate_id"]: row for row in grades}
        results = []
        for candidate in candidates:
            candidate_id = candidate["candidate_id"]
            results.append(
                {
                    key: candidate[key]
                    for key in (
                        "candidate_id",
                        "temperature",
                        "replicate",
                        "proof_sha256",
                        "deterministic_gate",
                    )
                }
                | {
                    "qwen_reviewer1": review_by_id[candidate_id]["review"],
                    "codex_grade": grade_by_id[candidate_id].get("grade"),
                    "codex_error": grade_by_id[candidate_id].get("error"),
                }
            )
        write_json(
            output_root / "summary.json",
            {
                "schema": "cognitive-well-v0.3.62-dynamic-terminal-composition-summary-v1",
                "state": "completed",
                "completed_at": utc_now(),
                "harness_version": HARNESS_VERSION,
                "results": results,
                "terra_calls": 0,
            },
        )
        write_json(
            output_root / "status.json",
            {
                "state": "completed",
                "stage": "codex_gold_scoring",
                "candidate_count": len(candidates),
                "updated_at": utc_now(),
            },
        )
    except Exception as error:
        write_json(
            output_root / "status.json",
            {
                "state": "failed",
                "stage": "exception",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise


if __name__ == "__main__":
    main()
