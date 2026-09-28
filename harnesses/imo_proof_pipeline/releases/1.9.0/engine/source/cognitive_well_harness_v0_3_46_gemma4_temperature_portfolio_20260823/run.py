from __future__ import annotations

import argparse
import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.runtime import utc_now, write_json

from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.runtime import (
    GEMMA_MODEL,
    RuntimeConfig,
    StageRuntime,
)
from cognitive_well_harness_v0_3_38_qwen36_three_persona_review_fusion_20260822.protocol import (
    sha256_text,
)
from cognitive_well_harness_v0_3_42_gemma4_dual_prompt_max_thinking_coldsolve_20260823.run import (
    BASELINE_MAX_TOKENS,
    BASELINE_SYSTEM_SHA256,
    BASELINE_USER_SHA256,
    load_control,
    nonempty_parser,
)
from cognitive_well_harness_v0_3_45_gemma4_high_stakes_no_checklist_coldsolve_20260823.run import (
    experimental_prompts,
)

from . import HARNESS_VERSION


MASTER_SEED = 2_026_082_301
CANDIDATES: tuple[dict[str, Any], ...] = (
    {"candidate_id": "t10_r01", "temperature": 1.0, "seed": 2_360_094_352},
    {"candidate_id": "t10_r02", "temperature": 1.0, "seed": 2_367_214_500},
    {"candidate_id": "t10_r03", "temperature": 1.0, "seed": 2_771_038_377},
    {"candidate_id": "t10_r04", "temperature": 1.0, "seed": 1_724_547_137},
    {"candidate_id": "t07_r01", "temperature": 0.7, "seed": 3_233_582_896},
    {"candidate_id": "t07_r02", "temperature": 0.7, "seed": 220_229_344},
)
MAX_CONCURRENT_CANDIDATES = 4


def run_candidate(
    *,
    output_dir: Path,
    system_prompt: str,
    user_prompt: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    candidate_id = str(spec["candidate_id"])
    candidate_dir = output_dir / "candidates" / candidate_id
    candidate_dir.mkdir(parents=True, exist_ok=True)
    generated = StageRuntime(RuntimeConfig()).gemma_call(
        output_dir=candidate_dir / "generation",
        name="p4_coldsolve",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        seed=int(spec["seed"]),
        temperature=float(spec["temperature"]),
        max_tokens=BASELINE_MAX_TOKENS,
        parser=nonempty_parser,
    )
    proof = str(generated["text"]).strip()
    (candidate_dir / "proof.md").write_text(proof + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v046-candidate-result-v1",
        **spec,
        "model": GEMMA_MODEL,
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": BASELINE_MAX_TOKENS,
        "cap_recovery_max_tokens": BASELINE_MAX_TOKENS * 2,
        "thinking_template_enabled": True,
        "finish_reason": generated["final_generation"].get("finish_reason"),
        "generation": generated["generation"],
        "final_generation": generated["final_generation"],
        "cap_recovery": generated["cap_recovery"],
        "prior_errors": generated["prior_errors"],
        "proof_sha256": sha256_text(proof),
        "proof_path": str((candidate_dir / "proof.md").resolve()),
        "completed_at": utc_now(),
    }
    write_json(candidate_dir / "result.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the six-candidate P4 portfolio")
    parser.add_argument("--control-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    control = load_control(args.control_dir)
    system_prompt, user_prompt = experimental_prompts(control["system_prompt"])
    RuntimeConfig().validate(require_files=False)
    manifest = {
        "schema": "cognitive-well-v046-temperature-portfolio-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "control_dir": str(args.control_dir.resolve()),
        "baseline_system_prompt_sha256": BASELINE_SYSTEM_SHA256,
        "baseline_user_prompt_sha256": BASELINE_USER_SHA256,
        "experimental_system_prompt_sha256": sha256_text(system_prompt),
        "experimental_user_prompt_sha256": sha256_text(user_prompt),
        "model": GEMMA_MODEL,
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "thinking_template_enabled": True,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": BASELINE_MAX_TOKENS,
        "cap_recovery_max_tokens": BASELINE_MAX_TOKENS * 2,
        "master_seed": MASTER_SEED,
        "seed_derivation": "python random.Random(master_seed).getrandbits(32), frozen",
        "candidates": list(CANDIDATES),
        "max_concurrent_candidates": MAX_CONCURRENT_CANDIDATES,
        "endpoint": RuntimeConfig().gemma_endpoint,
        "reference_solution_access": False,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    (args.output_dir / "experimental_system_prompt.txt").write_text(
        system_prompt, encoding="utf-8"
    )
    (args.output_dir / "experimental_user_prompt.txt").write_text(
        user_prompt, encoding="utf-8"
    )

    lock = threading.Lock()
    completed_ids: list[str] = []
    failures: list[dict[str, str]] = []

    def update_status(state: str) -> None:
        with lock:
            write_json(
                args.output_dir / "status.json",
                {
                    "state": state,
                    "stage": "six_candidate_generation",
                    "completed": sorted(completed_ids),
                    "failed": failures,
                    "total": len(CANDIDATES),
                    "updated_at": utc_now(),
                },
            )

    update_status("running")
    if not args.quiet:
        print(json.dumps({"state": "running", "total": len(CANDIDATES)}), flush=True)

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CANDIDATES) as executor:
        futures = {
            executor.submit(
                run_candidate,
                output_dir=args.output_dir,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                spec=dict(spec),
            ): dict(spec)
            for spec in CANDIDATES
        }
        for future in as_completed(futures):
            spec = futures[future]
            candidate_id = str(spec["candidate_id"])
            try:
                result = future.result()
            except Exception as error:
                failures.append(
                    {
                        "candidate_id": candidate_id,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            else:
                results.append(result)
                completed_ids.append(candidate_id)
                if not args.quiet:
                    print(
                        json.dumps(
                            {
                                "candidate_id": candidate_id,
                                "state": "completed",
                                "temperature": spec["temperature"],
                                "seed": spec["seed"],
                            }
                        ),
                        flush=True,
                    )
            update_status("running")

    results.sort(key=lambda item: str(item["candidate_id"]))
    summary = {
        **manifest,
        "schema": "cognitive-well-v046-temperature-portfolio-result-v1",
        "results": results,
        "failures": failures,
        "completed_at": utc_now(),
    }
    write_json(args.output_dir / "result.json", summary)
    final_state = "completed" if not failures else "completed_with_failures"
    update_status(final_state)
    if not args.quiet:
        print(
            json.dumps(
                {
                    "state": final_state,
                    "completed": len(results),
                    "failed": len(failures),
                },
                indent=2,
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
