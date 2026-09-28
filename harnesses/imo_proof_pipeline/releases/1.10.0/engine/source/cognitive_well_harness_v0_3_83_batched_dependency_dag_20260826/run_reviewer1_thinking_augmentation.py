from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
    utc_now,
    write_json,
)
from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    SYSTEM_PROMPT,
    parse_review,
    review_user_prompt,
    sha256_text,
)
from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.run import (
    CAP_RECOVERY_MAX_OUTPUT_TOKENS,
    MAX_OUTPUT_TOKENS,
    TOP_K,
    TOP_P,
    merge_continuation,
)

from . import HARNESS_VERSION


MODEL = "google/gemma-4-31B-it"
PROMPT_VARIANTS = ("original", "remove_terseness", "narrow_terseness")
TERSE_ALLOWANCE = (
    "Do not penalize style, terseness, or omitted routine algebra when the inference is\n"
    "unambiguous and valid by Olympiad standards."
)
NARROW_TERSE_ALLOWANCE = """Do not penalize concise presentation or omitted routine algebra when the missing
detail is a direct and essentially unique elaboration of an argument explicitly
present in the proof.

Terseness does not excuse a missing load-bearing construction, auxiliary lemma,
iteration, case analysis, limiting argument, or theorem application. If you must
introduce such reasoning yourself to justify the candidate's transition, treat that
transition as a first break, even when your added reasoning successfully repairs it."""


def reviewer1_system_prompt(variant: str) -> str:
    if variant not in PROMPT_VARIANTS:
        raise ValueError(f"unknown Reviewer 1 prompt variant: {variant}")
    if SYSTEM_PROMPT.count(TERSE_ALLOWANCE) != 1:
        raise RuntimeError("Reviewer 1 terseness allowance drifted")
    if variant == "original":
        return SYSTEM_PROMPT
    replacement = "" if variant == "remove_terseness" else NARROW_TERSE_ALLOWANCE
    return SYSTEM_PROMPT.replace(TERSE_ALLOWANCE, replacement)


def augmented_review_user_prompt(
    *, problem: str, proof: str, reasoning_summary: str | None
) -> str:
    prompt = review_user_prompt(problem=problem, proof=proof)
    if reasoning_summary is None:
        return prompt
    summary = reasoning_summary.strip()
    if not summary:
        raise ValueError("reasoning summary must not be empty")
    return (
        prompt.rstrip()
        + "\n\n# PRIOR REVIEWER-1 REASONING SUMMARY\n\n"
        "This is advisory context distilled from an earlier private reasoning trace. "
        "It is not an established verdict and may contain mistakes. Independently "
        "verify it against the problem and candidate proof. Preserve valid progress, "
        "do not repeat any reasoning explicitly marked invalid, and still return only "
        "the exact Reviewer 1 protocol form required by the system prompt.\n\n"
        + summary
        + "\n"
    )


def stable_seed(*, proof_sha256: str, temperature: float) -> int:
    material = f"v083:reviewer1-thinking-augmentation:{proof_sha256}:t{temperature:g}"
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:4], "big") or 1


def _read_problem(path: Path) -> str:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    problem = str(payload.get("problem") or payload.get("claim") or "").strip()
    if not problem:
        raise ValueError(f"problem field is empty: {path}")
    return problem


def main() -> None:
    parser = argparse.ArgumentParser(
        description="One exact Reviewer 1 call with optional prior-reasoning augmentation"
    )
    parser.add_argument("--problem-json", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reasoning-summary", type=Path)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--prompt-variant", choices=PROMPT_VARIANTS, default="original")
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8020/v1")
    args = parser.parse_args()

    if not 0.0 <= args.temperature <= 2.0:
        raise ValueError("temperature must be between 0 and 2")
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise ValueError(f"output directory must be new or empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    problem = _read_problem(args.problem_json)
    proof = args.proof.read_text(encoding="utf-8").strip()
    if not proof:
        raise ValueError(f"proof is empty: {args.proof}")
    reasoning_summary = (
        args.reasoning_summary.read_text(encoding="utf-8")
        if args.reasoning_summary is not None
        else None
    )
    user_prompt = augmented_review_user_prompt(
        problem=problem,
        proof=proof,
        reasoning_summary=reasoning_summary,
    )
    system_prompt = reviewer1_system_prompt(args.prompt_variant)
    proof_sha = sha256_text(proof)
    seed = stable_seed(proof_sha256=proof_sha, temperature=args.temperature)
    manifest = {
        "schema": "cognitive-well-v083-reviewer1-thinking-augmentation-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "model": MODEL,
        "temperature": args.temperature,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "cap_recovery_max_output_tokens": CAP_RECOVERY_MAX_OUTPUT_TOKENS,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "thinking_enabled": True,
        "prompt_variant": args.prompt_variant,
        "reviewer1_system_prompt_sha256": sha256_text(system_prompt),
        "user_prompt_sha256": sha256_text(user_prompt),
        "proof_path": str(args.proof.resolve()),
        "proof_sha256": proof_sha,
        "reasoning_summary_path": (
            str(args.reasoning_summary.resolve())
            if args.reasoning_summary is not None
            else None
        ),
        "reasoning_summary_sha256": (
            sha256_text(reasoning_summary.strip())
            if reasoning_summary is not None
            else None
        ),
        "seed": seed,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    write_json(
        args.output_dir / "status.json",
        {"state": "running", "stage": "reviewer_1", "updated_at": utc_now()},
    )
    generation_dir = args.output_dir / "generation"
    generation_dir.mkdir(parents=True, exist_ok=True)

    primary = run_openai_chat_generation(
        endpoint=args.gemma_endpoint.rstrip("/"),
        model=MODEL,
        prompt=system_prompt,
        user_prompt=user_prompt,
        output_dir=generation_dir,
        stage="reviewer1",
        config=HTTPGenerationConfig(
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=args.temperature,
            top_p=TOP_P,
            top_k=TOP_K,
            seed=seed,
            thinking_token_budget=None,
            reasoning_effort=None,
            timeout_seconds=14_400,
        ),
    )
    final = str(primary["text"]).strip()
    reasoning_parts = [str(primary.get("reasoning") or "").strip()]
    recovery: dict[str, Any] | None = None
    if primary["metadata"].get("finish_reason") == "length":
        reusable = "\n\n".join(
            part
            for part in (
                "[Preserved model-native reasoning]\n" + reasoning_parts[0]
                if reasoning_parts[0]
                else "",
                "[Preserved final response fragment]\n" + final if final else "",
            )
            if part
        )
        recovery = run_openai_chat_generation(
            endpoint=args.gemma_endpoint.rstrip("/"),
            model=MODEL,
            prompt=system_prompt,
            user_prompt=user_prompt,
            prior_generation=reusable,
            continuation_instruction=(
                "Continue the same private proof audit. Do not restart. Finish and "
                "emit exactly the required FIRST_BREAK or NO_FIRST_BREAK form."
            ),
            output_dir=generation_dir,
            stage="reviewer1_cap_continuation",
            config=HTTPGenerationConfig(
                max_tokens=CAP_RECOVERY_MAX_OUTPUT_TOKENS,
                temperature=args.temperature,
                top_p=TOP_P,
                top_k=TOP_K,
                seed=(seed + 1_000_003) & 0xFFFFFFFF,
                thinking_token_budget=None,
                reasoning_effort=None,
                timeout_seconds=14_400,
            ),
        )
        recovery_final = str(recovery["text"]).strip()
        parsed_recovery = parse_review(recovery_final)
        final = (
            recovery_final
            if parsed_recovery["valid"]
            else merge_continuation(final, recovery_final)
        )
        reasoning_parts.append(str(recovery.get("reasoning") or "").strip())

    parsed = parse_review(final)
    if not parsed["valid"]:
        raise ValueError(f"invalid Reviewer 1 output: {parsed['errors']}")
    reasoning = "\n\n[CAP CONTINUATION]\n\n".join(
        part for part in reasoning_parts if part
    )
    (args.output_dir / "final.txt").write_text(final + "\n", encoding="utf-8")
    (args.output_dir / "reasoning.txt").write_text(reasoning + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v083-reviewer1-thinking-augmentation-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "parsed": parsed,
        "final": final,
        "final_sha256": sha256_text(final),
        "reasoning_sha256": sha256_text(reasoning),
        "thinking_observed": bool(reasoning),
        "generation": primary["metadata"],
        "cap_recovery": recovery["metadata"] if recovery is not None else None,
    }
    write_json(args.output_dir / "result.json", result)
    write_json(
        args.output_dir / "status.json",
        {
            "state": "completed",
            "stage": "reviewer_1",
            "outcome": parsed["outcome"],
            "updated_at": result["completed_at"],
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
