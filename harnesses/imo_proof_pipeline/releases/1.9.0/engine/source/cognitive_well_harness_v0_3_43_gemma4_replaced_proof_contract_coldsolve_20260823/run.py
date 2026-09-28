from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

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
    BASELINE_SEED,
    BASELINE_SYSTEM_SHA256,
    BASELINE_TEMPERATURE,
    BASELINE_USER_SHA256,
    EMPHASIS_SUFFIX,
    PROOF_CONTRACT,
    load_control,
    nonempty_parser,
)

from . import HARNESS_VERSION


ORIGINAL_PROOF_PARAGRAPH = (
    "The final proof must restate what is proved, be self-contained, check all cases and\n"
    "both directions, and finish with the exact short answer in \\boxed{}. If no complete\n"
    "proof is reached, preserve the strongest rigorous partial result and say exactly what\n"
    "remains. Do not use a reference answer."
)
USER_OPENING = "Solve the stated problem from scratch using no outside materials."


def experimental_prompts(baseline_system: str) -> tuple[str, str]:
    count = baseline_system.count(ORIGINAL_PROOF_PARAGRAPH)
    if count != 1:
        raise ValueError(
            f"expected exactly one original proof paragraph, observed {count}"
        )
    replaced = baseline_system.replace(
        ORIGINAL_PROOF_PARAGRAPH,
        PROOF_CONTRACT,
        1,
    )
    separator = "\n\nPROBLEM:\n"
    if replaced.count(separator) != 1:
        raise ValueError("expected exactly one PROBLEM block in the baseline system prompt")
    system_prompt, problem_tail = replaced.split(separator, 1)
    system_prompt = system_prompt.rstrip()
    user_prompt = (
        USER_OPENING
        + "\n\nPROBLEM:\n"
        + problem_tail.rstrip()
        + "\n\n"
        + EMPHASIS_SUFFIX
    )
    return system_prompt, user_prompt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run P4 after replacing the original proof paragraph in place"
    )
    parser.add_argument("--control-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    control = load_control(args.control_dir)
    system_prompt, user_prompt = experimental_prompts(control["system_prompt"])
    config = RuntimeConfig()
    config.validate(require_files=False)

    manifest = {
        "schema": "cognitive-well-v043-replaced-proof-contract-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "controlled_change": (
            "replace original boxed-proof paragraph in place; keep behavior in the "
            "system message; move PROBLEM, ADDITIONAL MATERIALS, EXTERNAL FEEDBACK, "
            "and maximum-effort emphasis into the user message"
        ),
        "control_dir": str(args.control_dir.resolve()),
        "baseline_system_prompt_path": str(control["system_path"].resolve()),
        "baseline_system_prompt_sha256": BASELINE_SYSTEM_SHA256,
        "baseline_user_prompt_path": str(control["user_path"].resolve()),
        "baseline_user_prompt_sha256": BASELINE_USER_SHA256,
        "removed_proof_paragraph": ORIGINAL_PROOF_PARAGRAPH,
        "removed_proof_paragraph_sha256": sha256_text(ORIGINAL_PROOF_PARAGRAPH),
        "replacement_proof_contract": PROOF_CONTRACT,
        "replacement_proof_contract_sha256": sha256_text(PROOF_CONTRACT),
        "baseline_user_prompt_disposition": (
            "opening sentence retained before the relocated problem/materials/feedback block"
        ),
        "user_opening": USER_OPENING,
        "user_opening_sha256": sha256_text(USER_OPENING),
        "emphasis_suffix": EMPHASIS_SUFFIX,
        "emphasis_suffix_sha256": sha256_text(EMPHASIS_SUFFIX),
        "experimental_system_prompt_sha256": sha256_text(system_prompt),
        "experimental_user_prompt_sha256": sha256_text(user_prompt),
        "model": GEMMA_MODEL,
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "seed": BASELINE_SEED,
        "temperature": BASELINE_TEMPERATURE,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": BASELINE_MAX_TOKENS,
        "cap_recovery_max_tokens": BASELINE_MAX_TOKENS * 2,
        "thinking_template_enabled": True,
        "thinking_token_budget": None,
        "reasoning_effort": None,
        "input_scope": "P4 problem statement only",
        "reference_solution_access": False,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    (args.output_dir / "experimental_system_prompt.txt").write_text(
        system_prompt, encoding="utf-8"
    )
    (args.output_dir / "experimental_user_prompt.txt").write_text(
        user_prompt, encoding="utf-8"
    )
    write_json(
        args.output_dir / "status.json",
        {"state": "running", "stage": "gemma4_p4_coldsolve", "updated_at": utc_now()},
    )
    if not args.quiet:
        print(json.dumps({"state": "running", "stage": "gemma4_p4_coldsolve"}), flush=True)

    try:
        generated = StageRuntime(config).gemma_call(
            output_dir=args.output_dir / "generation",
            name="p4_coldsolve_replaced_proof_contract",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            seed=BASELINE_SEED,
            temperature=BASELINE_TEMPERATURE,
            max_tokens=BASELINE_MAX_TOKENS,
            parser=nonempty_parser,
        )
    except Exception as error:
        write_json(
            args.output_dir / "status.json",
            {
                "state": "failed",
                "stage": "gemma4_p4_coldsolve",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise

    proof = str(generated["text"]).strip()
    (args.output_dir / "proof.md").write_text(proof + "\n", encoding="utf-8")
    reasoning_path = Path(generated["generation"]["reasoning_path"])
    reasoning = (
        reasoning_path.read_text(encoding="utf-8").strip()
        if reasoning_path.is_file()
        else ""
    )
    result = {
        **manifest,
        "schema": "cognitive-well-v043-replaced-proof-contract-result-v1",
        "finish_reason": generated["final_generation"].get("finish_reason"),
        "generation": generated["generation"],
        "final_generation": generated["final_generation"],
        "thinking_observed": bool(reasoning),
        "reasoning_path": str(reasoning_path.resolve()),
        "reasoning_sha256": sha256_text(reasoning),
        "cap_recovery": generated["cap_recovery"],
        "prior_errors": generated["prior_errors"],
        "proof_sha256": sha256_text(proof),
        "proof": proof,
        "completed_at": utc_now(),
    }
    write_json(args.output_dir / "result.json", result)
    write_json(
        args.output_dir / "status.json",
        {"state": "completed", "stage": "gemma4_p4_coldsolve", "updated_at": utc_now()},
    )
    if not args.quiet:
        print(json.dumps({"state": "completed", "proof_sha256": result["proof_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
