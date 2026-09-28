from __future__ import annotations

import argparse
import json
import traceback
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

from . import HARNESS_VERSION


EMPHASIS_SUFFIX = (
    "Spare no effort to solve this, the stakes are high. Increase your thinking length "
    "to maximum in order to solve it. Double check and verify your results to rule out "
    "hallucination of an incorrect response."
)
PROOF_CONTRACT = (
    "The final proof must restate what is proved, be self-contained, and check all "
    "cases and both directions. If the task asks for a proof, do not put the conclusion "
    "in \\boxed{}; end the completed proof with \\(\\square\\). If no complete proof is "
    "reached, preserve the strongest rigorous partial result and state exactly what "
    "remains. Do not use a reference answer."
)
BASELINE_SYSTEM_SHA256 = "aa3f14461356a954781b76b2393416a001c60349aa1b5670e8134ee49fa49c5e"
BASELINE_USER_SHA256 = "d527abe775453015c3c6f38c244edbf20983d3a27592b333d38c0c85065f870d"
BASELINE_SEED = 476_917_889
BASELINE_TEMPERATURE = 1.0
BASELINE_MAX_TOKENS = 65_536


def nonempty_parser(value: str) -> dict[str, Any]:
    text = value.strip()
    return {"valid": bool(text), "errors": [] if text else ["empty response"]}


def load_control(control_dir: Path) -> dict[str, Any]:
    system_path = control_dir / "cold_draft_attempt1.prompt.txt"
    user_path = control_dir / "cold_draft_attempt1.user_prompt.txt"
    result_path = control_dir / "cold_draft.result.json"
    for path in (system_path, user_path, result_path):
        if not path.is_file():
            raise FileNotFoundError(f"cold-solve control artifact missing: {path}")
    system_prompt = system_path.read_text(encoding="utf-8")
    baseline_user = user_path.read_text(encoding="utf-8")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    identity = result.get("identity", {})
    expected = {
        "model": GEMMA_MODEL,
        "system_prompt_sha256": BASELINE_SYSTEM_SHA256,
        "user_prompt_sha256": BASELINE_USER_SHA256,
        "seed": BASELINE_SEED,
        "temperature": BASELINE_TEMPERATURE,
        "max_tokens": BASELINE_MAX_TOKENS,
    }
    mismatches = {
        key: {"expected": value, "observed": identity.get(key)}
        for key, value in expected.items()
        if identity.get(key) != value
    }
    if mismatches:
        raise ValueError(f"cold-solve control identity changed: {mismatches}")
    if sha256_text(system_prompt) != BASELINE_SYSTEM_SHA256:
        raise ValueError("control system prompt bytes changed")
    if sha256_text(baseline_user) != BASELINE_USER_SHA256:
        raise ValueError("control user prompt bytes changed")
    return {
        "system_prompt": system_prompt,
        "baseline_user": baseline_user,
        "system_path": system_path,
        "user_path": user_path,
        "result": result,
    }


def append_emphasis(prompt: str) -> str:
    if not prompt.strip():
        raise ValueError("baseline prompt is empty")
    return prompt.rstrip() + "\n\n" + EMPHASIS_SUFFIX


def experimental_system_prompt(baseline_system: str) -> str:
    return append_emphasis(baseline_system) + "\n\n" + PROOF_CONTRACT


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the exact P4 cold solve with the same emphasis on system and user prompts"
    )
    parser.add_argument("--control-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    control = load_control(args.control_dir)
    system_prompt = experimental_system_prompt(control["system_prompt"])
    user_prompt = append_emphasis(control["baseline_user"])
    config = RuntimeConfig()
    config.validate(require_files=False)
    manifest = {
        "schema": "cognitive-well-v042-dual-suffix-coldsolve-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "controlled_variable_vs_v041": (
            "identical_emphasis_suffix_and_explicit_proof_contract_added_to_system_prompt"
        ),
        "control_dir": str(args.control_dir.resolve()),
        "baseline_system_prompt_path": str(control["system_path"].resolve()),
        "baseline_system_prompt_sha256": BASELINE_SYSTEM_SHA256,
        "baseline_user_prompt_path": str(control["user_path"].resolve()),
        "baseline_user_prompt_sha256": BASELINE_USER_SHA256,
        "emphasis_suffix": EMPHASIS_SUFFIX,
        "emphasis_suffix_sha256": sha256_text(EMPHASIS_SUFFIX),
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_sha256": sha256_text(PROOF_CONTRACT),
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
            name="p4_coldsolve_dual_suffix",
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
        "schema": "cognitive-well-v042-dual-suffix-coldsolve-result-v1",
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
