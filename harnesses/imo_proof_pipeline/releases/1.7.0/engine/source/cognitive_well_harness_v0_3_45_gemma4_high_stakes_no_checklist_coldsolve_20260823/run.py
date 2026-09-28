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
    PROOF_CONTRACT,
    load_control,
    nonempty_parser,
)
from cognitive_well_harness_v0_3_44_gemma4_high_stakes_gate_coldsolve_20260823.run import (
    HIGH_STAKES_GATE,
    USER_REMINDER,
    experimental_prompts as v044_prompts,
)

from . import HARNESS_VERSION


FINALIZATION_CHECKLIST = """Before finalizing:
1. Develop and compare materially different approaches.
2. Actively search for counterexamples to every claimed classification.
3. Verify all constructions are geometrically admissible.
4. Prove both necessity and sufficiency, including boundary and exceptional cases.
5. Perform a separate final audit in which every substantive claim is checked against the original problem.
6. If that audit finds an unresolved gap, do not present the result as a completed proof. Preserve the strongest rigorous partial result and state the gap exactly."""

HIGH_STAKES_PREAMBLE = HIGH_STAKES_GATE.replace(
    "\n\n" + FINALIZATION_CHECKLIST,
    "",
)


def experimental_prompts(baseline_system: str) -> tuple[str, str]:
    system_prompt, user_prompt = v044_prompts(baseline_system)
    checklist_with_spacing = "\n\n" + FINALIZATION_CHECKLIST
    if system_prompt.count(checklist_with_spacing) != 1:
        raise ValueError("expected exactly one finalization checklist in v0.3.44 prompt")
    system_prompt = system_prompt.replace(checklist_with_spacing, "", 1)
    if system_prompt.count(HIGH_STAKES_PREAMBLE) != 1:
        raise ValueError("expected exactly one retained high-stakes preamble")
    system_prompt = system_prompt.replace(HIGH_STAKES_PREAMBLE + "\n\n", "", 1)
    system_prompt = system_prompt.rstrip() + "\n\n" + HIGH_STAKES_PREAMBLE
    return system_prompt, user_prompt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run P4 with the high-stakes preamble and no numbered checklist"
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
        "schema": "cognitive-well-v045-high-stakes-no-checklist-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "controlled_change_vs_v044": (
            "remove the Before finalizing heading and its six-item checklist, then "
            "move the retained high-stakes preamble to the absolute system-prompt end"
        ),
        "control_dir": str(args.control_dir.resolve()),
        "baseline_system_prompt_path": str(control["system_path"].resolve()),
        "baseline_system_prompt_sha256": BASELINE_SYSTEM_SHA256,
        "baseline_user_prompt_path": str(control["user_path"].resolve()),
        "baseline_user_prompt_sha256": BASELINE_USER_SHA256,
        "removed_finalization_checklist": FINALIZATION_CHECKLIST,
        "removed_finalization_checklist_sha256": sha256_text(FINALIZATION_CHECKLIST),
        "retained_high_stakes_gate_without_checklist": HIGH_STAKES_PREAMBLE,
        "user_reminder": USER_REMINDER,
        "proof_contract": PROOF_CONTRACT,
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
            name="p4_coldsolve_high_stakes_no_checklist",
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
        "schema": "cognitive-well-v045-high-stakes-no-checklist-result-v1",
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
