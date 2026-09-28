from __future__ import annotations

import concurrent.futures
import hashlib
import json
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_57_v030_cross_model_pair_dossier_ab_20260824 import (
    run_arm as base,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "runs/v063_failed_lemma_salvage_surgical_20260825"
GEMMA_ENDPOINT = "http://127.0.0.1:8020/v1"

CASE_PATHS = {
    "refuted": ROOT / (
        "runs/v063_p5_full_replay_triplicate_to_candidates_20260825/r2/"
        "hypothesis_round_1/lemma_verification/R1H1"
    ),
    "proof_failed": ROOT / (
        "runs/v061_atomic_hypothesis_p5_full_replay_20260825/diagnostic/"
        "hypothesis_round_1/lemma_verification/R1H1"
    ),
    "verifier_conflict": ROOT / (
        "runs/v063_p5_full_replay_triplicate_to_candidates_20260825/r1/"
        "hypothesis_round_1/lemma_verification/R1H1"
    ),
}

EXPECTED_STATUS = {
    "refuted": "REFUTED",
    "proof_failed": "PROOF_FAILED",
    "verifier_conflict": "VERIFIER_CONFLICT",
}

SALVAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decision", "failure_interpretation", "hypotheses"],
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["REPAIR", "DECOMPOSE", "ABANDON"],
        },
        "failure_interpretation": {"type": "string", "minLength": 20},
        "hypotheses": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "statement",
                    "exact_negation",
                    "relation_to_failed_hypothesis",
                    "earliest_unresolved_transition",
                    "local_dependency_map",
                ],
                "properties": {
                    "statement": {"type": "string", "minLength": 20},
                    "exact_negation": {"type": "string", "minLength": 20},
                    "relation_to_failed_hypothesis": {
                        "type": "string",
                        "minLength": 20,
                    },
                    "earliest_unresolved_transition": {
                        "type": "string",
                        "minLength": 20,
                    },
                    "local_dependency_map": {
                        "type": "string",
                        "minLength": 20,
                    },
                },
            },
        },
    },
}

SYSTEM_PROMPT = """You are a failure-guided hypothesis salvager for difficult
mathematical proofs. Thinking mode is on with maximal reasoning effort.

You receive an original problem, one or more untrusted proof attempts, and a compact
record for one previously proposed hypothesis. Recheck all mathematical content; the
failure status and audits are routing evidence, not substitutes for proof.

Choose exactly one action:
- REPAIR: make the smallest principled change to the hypothesis that directly resolves
  the recorded failure and remains derivable from the original problem.
- DECOMPOSE: replace the hypothesis by smaller independently testable obligations that
  isolate its load-bearing steps.
- ABANDON: leave that semantic route and extract an adjacent missing obligation from
  the supplied proof.

Status-specific rules:
- REFUTED: do not repeat a semantically equivalent statement. A repaired statement
  must explicitly block the certified counterexample using a premise motivated by the
  original problem, or the route must be decomposed/abandoned.
- PROOF_FAILED: do not infer that the statement is false. Isolate the earliest missing
  justification into atomic obligations.
- VERIFIER_CONFLICT: first determine what each proof actually proves. Do not assume
  either certification is aligned. Produce an unambiguous smaller theorem or a
  discriminator that resolves the conflict.

Every returned hypothesis must be self-contained, strictly weaker than the original
problem, independently provable or refutable, and paired with its exact logical
negation. Do not write a final solution. Do not encode problem-specific constants or
structures unless they occur in the supplied mathematical material. Return only the
requested JSON record."""

COMPACT_INSTRUCTION = (
    "Return exactly one complete compact JSON object on one line. Do not use Markdown "
    "fences or blank lines. Emit every required field, close the object, and stop."
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def saved_generation(destination: Path, stage: str) -> dict[str, Any] | None:
    response_path = destination / f"{stage}.raw_response.json"
    metadata_path = destination / f"{stage}.metadata.json"
    if not response_path.is_file() or not metadata_path.is_file():
        return None
    response = read_json(response_path)
    choices = response.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message") or {}
    return {
        "text": str(message.get("content") or ""),
        "metadata": read_json(metadata_path),
    }


def parse_salvage_record(text: str) -> dict[str, Any]:
    record = base.parse_json_object(text)
    base.validate_schema(record, SALVAGE_SCHEMA)
    return record


def audit_signal(result: dict[str, Any]) -> dict[str, Any]:
    audit = result.get("audit") or {}
    return {
        "side": result.get("side"),
        "claim": result.get("claim"),
        "certified": bool(result.get("certified")),
        "earliest_break": audit.get("earliest_break"),
        "missing_obligations": audit.get("missing_obligations") or [],
        "summary": audit.get("summary"),
        "proof": result.get("proof") if result.get("certified") else None,
    }


def build_failure_card(case_name: str) -> dict[str, Any]:
    case_path = CASE_PATHS[case_name]
    positive = read_json(case_path / "positive/result.json")
    negative = read_json(case_path / "negative/result.json")
    positive_certified = bool(positive.get("certified"))
    negative_certified = bool(negative.get("certified"))
    derived_status = (
        "VERIFIER_CONFLICT"
        if positive_certified and negative_certified
        else "REFUTED"
        if negative_certified and not positive_certified
        else "PROOF_FAILED"
        if not positive_certified and not negative_certified
        else "VERIFIED"
    )
    if derived_status != EXPECTED_STATUS[case_name]:
        raise ValueError(
            f"{case_name}: expected {EXPECTED_STATUS[case_name]}, got {derived_status}"
        )
    return {
        "status": derived_status,
        "failed_hypothesis": positive["claim"],
        "exact_negation": negative["claim"],
        "positive_signal": audit_signal(positive),
        "negative_signal": audit_signal(negative),
    }


def run_case(
    *,
    case_name: str,
    problem: str,
    proof_attempts: list[dict[str, str]],
) -> dict[str, Any]:
    destination = OUTPUT_ROOT / case_name
    destination.mkdir(parents=True, exist_ok=True)
    result_path = destination / "result.json"
    if result_path.is_file():
        return read_json(result_path)

    failure_card = build_failure_card(case_name)
    user_prompt = (
        "ORIGINAL PROBLEM:\n"
        + problem
        + "\n\nORIGINAL PROOF ATTEMPTS:\n"
        + json.dumps(proof_attempts, ensure_ascii=False)
        + "\n\nFAILED-HYPOTHESIS MEMORY CARD:\n"
        + json.dumps(failure_card, ensure_ascii=False)
        + "\n\nRepair, decompose, or abandon this hypothesis route now."
    )
    stage = "failure_guided_salvage"
    generated = saved_generation(destination, stage)
    if generated is None:
        generated = run_openai_chat_generation(
            endpoint=GEMMA_ENDPOINT,
            model=base.GEMMA_MODEL,
            prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_dir=destination,
            stage=stage,
            config=HTTPGenerationConfig(
                max_tokens=32_768,
                temperature=0.4,
                top_p=0.95,
                top_k=64,
                seed=base.stable_seed(f"v063:failure_guided_salvage:{case_name}"),
                thinking_token_budget=None,
                reasoning_effort="max",
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"failure_guided_salvage_{case_name}",
                        "strict": True,
                        "schema": SALVAGE_SCHEMA,
                    },
                },
                repetition_detection=base.REPETITION_DETECTION,
                timeout_seconds=14_400,
            ),
        )

    attempts: list[dict[str, Any]] = []
    partial = str(generated["text"])
    try:
        record = parse_salvage_record(partial)
        attempts.append(
            {
                "phase": "original",
                "status": "accepted",
                "finish_reason": generated["metadata"].get("finish_reason"),
            }
        )
    except Exception as original_error:
        attempts.append(
            {
                "phase": "original",
                "status": "rejected",
                "finish_reason": generated["metadata"].get("finish_reason"),
                "error": f"{type(original_error).__name__}: {original_error}",
            }
        )
        prior_error = attempts[-1]["error"]
        record = None
        for phase in ("compact", "repair_1"):
            recovery_stage = f"{stage}_{phase}"
            if phase == "compact":
                recovery_user_prompt = user_prompt.rstrip() + "\n\n" + COMPACT_INSTRUCTION
            else:
                recovery_user_prompt = (
                    user_prompt.rstrip()
                    + "\n\nTRANSPORT RECOVERY: Regenerate the entire record from scratch. "
                    + "Do not append to the prior response or reproduce a repeated suffix. "
                    + "Preserve correct mathematical content only. Prior error: "
                    + prior_error
                    + "\n\nPRIOR INCOMPLETE RESPONSE:\n"
                    + partial.rstrip()[-12_000:]
                    + "\n\n"
                    + COMPACT_INSTRUCTION
                )
            recovered = saved_generation(destination, recovery_stage)
            if recovered is None:
                recovered = run_openai_chat_generation(
                    endpoint=GEMMA_ENDPOINT,
                    model=base.GEMMA_MODEL,
                    prompt=SYSTEM_PROMPT,
                    user_prompt=recovery_user_prompt,
                    output_dir=destination,
                    stage=recovery_stage,
                    config=HTTPGenerationConfig(
                        max_tokens=16_384,
                        temperature=0.4,
                        top_p=0.95,
                        top_k=64,
                        seed=base.stable_seed(
                            f"v063:failure_guided_salvage:{case_name}:{phase}"
                        ),
                        thinking_token_budget=None,
                        reasoning_effort="max",
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": f"failure_guided_salvage_{case_name}_{phase}",
                                "strict": True,
                                "schema": SALVAGE_SCHEMA,
                            },
                        },
                        repetition_detection=base.REPETITION_DETECTION,
                        timeout_seconds=14_400,
                    ),
                )
            partial = str(recovered["text"])
            try:
                record = parse_salvage_record(partial)
                attempts.append(
                    {
                        "phase": phase,
                        "status": "accepted",
                        "finish_reason": recovered["metadata"].get("finish_reason"),
                    }
                )
                generated = recovered
                break
            except Exception as recovery_error:
                prior_error = f"{type(recovery_error).__name__}: {recovery_error}"
                attempts.append(
                    {
                        "phase": phase,
                        "status": "rejected",
                        "finish_reason": recovered["metadata"].get("finish_reason"),
                        "error": prior_error,
                    }
                )
        if record is None:
            raise RuntimeError(f"structured salvage recovery exhausted: {attempts}")

    generation_metadata = dict(generated["metadata"])
    generation_metadata["salvage_recovery_attempts"] = attempts
    result = {
        "schema": "cognitive-well-failure-guided-salvage-surgical-v1",
        "case_name": case_name,
        "failure_card": failure_card,
        "record": record,
        "generation": generation_metadata,
    }
    base.write_json(result_path, result)
    return result


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    problem, seeds = base.load_inputs()
    proof_attempts = [
        {
            "solution_id": row["solution_id"],
            "role": row["role"],
            "proof": row["proof"],
        }
        for row in seeds
    ]
    base.write_json(
        OUTPUT_ROOT / "manifest.json",
        {
            "schema": "cognitive-well-failure-guided-salvage-surgical-manifest-v1",
            "created_at": base.utc_now(),
            "model": base.GEMMA_MODEL,
            "temperature": 0.4,
            "reasoning_effort": "max",
            "problem_sha256": hashlib.sha256(problem.encode()).hexdigest(),
            "statuses": list(EXPECTED_STATUS.values()),
            "generic_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
            "gold_or_reference_accessed": False,
        },
    )
    base.status(
        OUTPUT_ROOT,
        state="running",
        stage="failure_guided_salvage",
        case_count=len(CASE_PATHS),
    )
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(
                executor.map(
                    lambda case_name: run_case(
                        case_name=case_name,
                        problem=problem,
                        proof_attempts=proof_attempts,
                    ),
                    CASE_PATHS,
                )
            )
        summary = {
            "schema": "cognitive-well-failure-guided-salvage-surgical-summary-v1",
            "state": "completed",
            "completed_at": base.utc_now(),
            "results": [
                {
                    "case_name": row["case_name"],
                    "status": row["failure_card"]["status"],
                    "decision": row["record"]["decision"],
                    "hypothesis_count": len(row["record"]["hypotheses"]),
                }
                for row in results
            ],
        }
        base.write_json(OUTPUT_ROOT / "summary.json", summary)
        base.status(
            OUTPUT_ROOT,
            state="completed",
            stage="failure_guided_salvage",
            case_count=len(results),
        )
    except Exception as error:
        base.status(
            OUTPUT_ROOT,
            state="failed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise


if __name__ == "__main__":
    main()
