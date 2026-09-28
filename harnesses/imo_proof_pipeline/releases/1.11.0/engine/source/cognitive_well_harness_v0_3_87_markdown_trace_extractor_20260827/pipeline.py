from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    SYSTEM_PROMPT,
    parse_review,
    review_user_prompt,
    sha256_text,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import (
    pipeline as v084,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)

from . import MODEL


# Deliberately use the frozen v0.3.49 prompt byte-for-byte. Reviewer 1 remains an
# earliest-break reviewer; exhaustive recovery belongs only to the next model call.
ORIGINAL_REVIEWER_SYSTEM_PROMPT = SYSTEM_PROMPT


COMPACT_MARKDOWN_EXTRACTOR_SYSTEM_PROMPT = r"""You are a high-recall forensic
extractor for an olympiad proof review. You receive the original problem, submitted
proof, Reviewer 1's complete reasoning trace, and its visible review. Do not re-grade,
filter, certify, or repair the mathematics. Extract what the reviewer considered.

Recall is the priority. Emit one candidate for every distinct possible repair need
anywhere in the reasoning trace or visible review: a missing premise, unsupported
transition, circular step, boundary case, doubt, failed argument, or unresolved
obligation. `Repair needed` is mandatory in every candidate.

Do not suppress an item because the reviewer later called the proof correct, routine,
standard, acceptable, or repairable. Do not suppress ideas that the reviewer later
rejected or could not verify; extract them and state that disposition in `Reason` so a
later selector can decide. Do not invent material absent from the supplied review and
trace. For each repair need, consolidate into `Useful material` every non-routine
proof prefix, lemma, calculation, construction, case split, or repair route that the
trace indicates can be preserved or reused around that defect. Do not select only the
strongest component when several survive.

Do not emit standalone confirmations of correct proof steps. A useful observation
belongs in the output only when it is attached to a reported repair need. Consolidate
repeated discussions of the same defect into one candidate without dropping any
distinct salvageable component.

Return only compact Markdown. Repeat exactly this three-line block for each finding:

### Candidate
- Useful material: <compact text or (none)>
- Repair needed: <compact nonempty text>
- Reason: <why it appeared in the trace and whether the reviewer retained, repaired, questioned, or rejected it>

Keep every field on one physical line. `Repair needed` must never be `(none)`. If the
trace and visible review contain no possible repair need, output exactly
`No candidates.` Output no IDs, verdict, score, summary, JSON, fences, or extra
sections."""


COMPACT_REVIEW_MATERIALIZER_SYSTEM_PROMPT = r"""You are the output materializer
for a completed Olympiad proof audit. The supplied reasoning trace is the reviewer's
already-completed mathematical deliberation. Do not restart the proof audit, explore
new approaches, or reproduce the reasoning. Immediately materialize the reviewer's
resolved conclusion in exactly one of the following visible forms.

If the trace resolves an earliest break, output exactly:

FIRST_BREAK
location: <the earliest sentence, equation, or transition>
claim: <the claim being made there>
established_before: <the facts available for supporting this claim>
missing_or_invalid_link: <the precise missing premise or invalid inference>
why_not_follow: <brief mathematical explanation>
minimum_requirement: <what must be established for this claim to follow>
END_FIRST_BREAK

If it resolves that there is no first break, output exactly:

NO_FIRST_BREAK

Use only the supplied proof and reasoning trace. Keep every field on one physical
line. Output nothing before or after the required form."""


REVIEWER_INITIAL_MAX_TOKENS = 16_000
REVIEWER_RECOVERY_MAX_TOKENS = (24_000, 32_000)
REVIEWER_MAX_ATTEMPTS = 3


def reviewer_cutoff_location(
    *, finish_reason: str | None, reasoning: str, visible: str
) -> str | None:
    """Locate a transport cutoff from response fields without judging mathematics."""
    if finish_reason not in {"length", "repetition"}:
        return None
    if visible.strip():
        return "VISIBLE"
    return "THINKING"


def reviewer_recovery_plan(
    *,
    cutoff_location: str,
    attempt: int,
    recovery_max_tokens: tuple[int, ...] = REVIEWER_RECOVERY_MAX_TOKENS,
) -> dict[str, Any]:
    if cutoff_location not in {"THINKING", "VISIBLE"}:
        raise ValueError(f"unknown cutoff location: {cutoff_location}")
    if attempt < 1 or attempt > len(recovery_max_tokens):
        raise ValueError(f"invalid recovery attempt: {attempt}")
    return {
        "max_tokens": recovery_max_tokens[attempt - 1],
        "thinking_enabled": True,
        "system_prompt": ORIGINAL_REVIEWER_SYSTEM_PROMPT,
        "mode": "CLEAN_RETRY_FROM_ORIGINAL",
    }


def reviewer_recovery_user_prompt(
    *,
    original_user_prompt: str,
    cutoff_location: str,
    prior_reasoning_parts: list[str],
    prior_visible_parts: list[str],
) -> str:
    """Return the byte-identical original input for a clean cutoff retry.

    The prior fields remain in the signature for compatibility with historical
    experiment callers, but policy deliberately excludes them from the retry.
    """
    if cutoff_location not in {"THINKING", "VISIBLE"}:
        raise ValueError(f"unknown cutoff location: {cutoff_location}")
    _ = prior_reasoning_parts, prior_visible_parts
    return original_user_prompt


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _cached_text_with_reasoning(
    *, destination: Path, stage: str
) -> dict[str, Any] | None:
    cached = ModelRuntime.saved_generation(destination, stage)
    if cached is None:
        return None
    reasoning_path = destination / f"{stage}.reasoning.txt"
    reasoning = (
        reasoning_path.read_text(encoding="utf-8").strip()
        if reasoning_path.is_file()
        else ""
    )
    return {**cached, "reasoning": reasoning}


def run_cutoff_aware_original_reviewer(
    *,
    user_prompt: str,
    endpoint: str,
    model: str,
    destination: Path,
    seed: int,
    seed_label: str,
    initial_max_tokens: int = REVIEWER_INITIAL_MAX_TOKENS,
    recovery_max_tokens: tuple[int, ...] = REVIEWER_RECOVERY_MAX_TOKENS,
    vary_retry_seed: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run Reviewer 1 with clean 24k and 32k retries after cutoffs."""
    destination.mkdir(parents=True, exist_ok=True)
    seed_runtime = ModelRuntime(
        RuntimeConfig(
            gemma_endpoint=endpoint.rstrip("/"),
            qwen_endpoint=endpoint.rstrip("/"),
            gemma_model=model,
            qwen_model=model,
            master_seed=seed,
        )
    )
    attempts: list[dict[str, Any]] = []
    cutoff_location: str | None = None

    max_attempts = 1 + len(recovery_max_tokens)
    for attempt in range(max_attempts):
        if attempt == 0:
            plan = {
                "max_tokens": initial_max_tokens,
                "thinking_enabled": True,
                "system_prompt": ORIGINAL_REVIEWER_SYSTEM_PROMPT,
                "mode": "ORIGINAL_REVIEW",
            }
            resolved_user_prompt = user_prompt
            stage = "original_reviewer1"
        else:
            if cutoff_location is None:
                raise RuntimeError("recovery attempt lacks a cutoff location")
            plan = reviewer_recovery_plan(
                cutoff_location=cutoff_location,
                attempt=attempt,
                recovery_max_tokens=recovery_max_tokens,
            )
            resolved_user_prompt = reviewer_recovery_user_prompt(
                original_user_prompt=user_prompt,
                cutoff_location=cutoff_location,
                prior_reasoning_parts=[],
                prior_visible_parts=[],
            )
            stage = (
                f"original_reviewer1_clean_{int(plan['max_tokens']) // 1000}k_"
                f"retry_{attempt}"
            )

        generated = _cached_text_with_reasoning(
            destination=destination, stage=stage
        )
        if generated is None:
            attempt_seed_label = (
                f"{seed_label}:retry:{attempt}"
                if vary_retry_seed and attempt > 0
                else seed_label
            )
            try:
                generated = run_openai_chat_generation(
                    endpoint=endpoint.rstrip("/"),
                    model=model,
                    prompt=str(plan["system_prompt"]),
                    user_prompt=resolved_user_prompt,
                    output_dir=destination,
                    stage=stage,
                    config=HTTPGenerationConfig(
                        max_tokens=int(plan["max_tokens"]),
                        temperature=0.1,
                        top_p=1.0,
                        top_k=-1,
                        seed=seed_runtime.stable_seed(attempt_seed_label),
                        thinking_token_budget=None,
                        reasoning_effort=(
                            "max" if bool(plan["thinking_enabled"]) else None
                        ),
                        thinking_enabled=bool(plan["thinking_enabled"]),
                        repetition_detection={
                            "min_pattern_size": 8,
                            "max_pattern_size": 128,
                            "min_count": 3,
                        },
                        timeout_seconds=14_400,
                    ),
                )
            except RuntimeError as error:
                # The HTTP helper persists the response before rejecting an empty
                # visible answer. Reload it so repetition/length cutoffs enter this
                # controller's clean-retry policy in the same process.
                if "returned empty final content" not in str(error):
                    raise
                generated = _cached_text_with_reasoning(
                    destination=destination, stage=stage
                )
                if generated is None:
                    raise

        reasoning = str(generated.get("reasoning") or "")
        visible = str(generated.get("text") or "")
        metadata = dict(generated.get("metadata") or {})
        finish = metadata.get("finish_reason")
        observed_cutoff = reviewer_cutoff_location(
            finish_reason=str(finish) if finish is not None else None,
            reasoning=reasoning,
            visible=visible,
        )
        accepted = bool(visible.strip()) and observed_cutoff is None
        attempts.append(
            {
                "attempt": attempt,
                "stage": stage,
                "mode": plan["mode"],
                "max_tokens": plan["max_tokens"],
                "thinking_enabled": plan["thinking_enabled"],
                "finish_reason": finish,
                "cutoff_location": observed_cutoff,
                "reasoning_sha256": _sha256(reasoning),
                "reasoning_nonempty": bool(reasoning.strip()),
                "visible_sha256": _sha256(visible),
                "visible_nonempty": bool(visible.strip()),
                "accepted_transport": accepted,
                "prior_reasoning_supplied": False,
                "prior_visible_supplied": False,
                "trace_harvest_eligible": accepted,
            }
        )
        if accepted:
            metadata["v0152_cutoff_aware_recovery_attempts"] = attempts
            return {**generated, "metadata": metadata}, attempts
        if observed_cutoff is None:
            raise RuntimeError(
                f"Reviewer 1 stopped without a complete visible response: {attempts}"
            )
        cutoff_location = observed_cutoff

    raise RuntimeError(f"Reviewer 1 cutoff recovery exhausted: {attempts}")


BLOCK_PATTERN = re.compile(
    r"### Candidate\n"
    r"- Useful material: ([^\n]+)\n"
    r"- Repair needed: ([^\n]+)\n"
    r"- Reason: ([^\n]+)"
)


def compact_extractor_user_prompt(
    *, problem: str, proof: str, reasoning: str, reviewer_final: str
) -> str:
    values = tuple(
        value.strip() for value in (problem, proof, reasoning, reviewer_final)
    )
    if not all(values):
        raise ValueError("problem, proof, reasoning, and reviewer final must be nonempty")
    return (
        "# FORENSIC EXTRACTION INPUT\n\n"
        "## ORIGINAL PROBLEM\n"
        + values[0]
        + "\n\n## SUBMITTED PROOF\n"
        + values[1]
        + "\n\n## REVIEWER 1 COMPLETE REASONING TRACE\n"
        + values[2]
        + "\n\n## REVIEWER 1 VISIBLE REVIEW\n"
        + values[3]
        + "\n\nExtract every candidate now.\n"
    )


def parse_compact_markdown(value: str) -> list[dict[str, str]]:
    text = value.strip()
    if text == "No candidates.":
        return []
    matches = list(BLOCK_PATTERN.finditer(text))
    if not matches:
        raise ValueError("extractor output did not match compact Markdown protocol")
    cursor = 0
    candidates: list[dict[str, str]] = []
    for match in matches:
        separator = text[cursor : match.start()]
        if separator.strip():
            raise ValueError("extractor emitted text outside candidate blocks")
        useful, repair, reason = (part.strip() for part in match.groups())
        useful = "" if useful == "(none)" else useful
        repair = "" if repair == "(none)" else repair
        if not repair:
            raise ValueError("extractor emitted a candidate without a repair need")
        if not reason:
            raise ValueError("extractor emitted a candidate without a reason")
        candidates.append(
            {
                "useful_material": useful,
                "repair_needed": repair,
                "reason": reason,
            }
        )
        cursor = match.end()
    if text[cursor:].strip():
        raise ValueError("extractor emitted trailing text")
    return candidates


def _all_reasoning(generation_dir: Path) -> str:
    paths = sorted(generation_dir.glob("*.reasoning.txt"))
    chunks = [path.read_text(encoding="utf-8").strip() for path in paths]
    reasoning = "\n\n".join(chunk for chunk in chunks if chunk).strip()
    if not reasoning:
        raise RuntimeError("reviewer completed without an observable reasoning trace")
    return reasoning


def run_original_reviewer(
    *,
    problem: str,
    proof: str,
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
    initial_max_tokens: int = REVIEWER_INITIAL_MAX_TOKENS,
    recovery_max_tokens: tuple[int, ...] = REVIEWER_RECOVERY_MAX_TOKENS,
    vary_retry_seed: bool = False,
    protocol_repair_max_tokens: int = 12_000,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    generation_dir = output_dir / "generation"
    runtime = v084.runtime_for(endpoint, seed, model)
    user = review_user_prompt(problem=problem, proof=proof)
    adaptive_recovery_events: list[dict[str, Any]] = []
    generated, adaptive_recovery_events = run_cutoff_aware_original_reviewer(
        user_prompt=user,
        endpoint=endpoint,
        model=model,
        destination=generation_dir,
        seed=seed,
        seed_label=seed_label,
        initial_max_tokens=initial_max_tokens,
        recovery_max_tokens=recovery_max_tokens,
        vary_retry_seed=vary_retry_seed,
    )
    final = str(generated["text"]).strip()
    parsed = parse_review(final)
    protocol_repaired = False
    if not parsed["valid"]:
        protocol_repaired = True
        generated = runtime.text(
            role="gemma",
            prompt=ORIGINAL_REVIEWER_SYSTEM_PROMPT,
            user_prompt=(
                user.rstrip()
                + "\n\nThe preceding response violated the output protocol. Repeat "
                "the complete audit and return exactly the required FIRST_BREAK or "
                "NO_FIRST_BREAK form.\n"
            ),
            destination=generation_dir,
            stage="original_reviewer1_protocol_repair",
            temperature=0.1,
            max_tokens=protocol_repair_max_tokens,
            seed_label=seed_label + ":protocol_repair",
            top_p=1.0,
            top_k=-1,
        )
        final = str(generated["text"]).strip()
        parsed = parse_review(final)
    if not parsed["valid"]:
        raise ValueError(f"original reviewer protocol invalid: {parsed['errors']}")
    reasoning = str(generated.get("reasoning") or "").strip()
    if not reasoning:
        raise RuntimeError(
            "transport-accepted Reviewer 1 call has no observable reasoning trace"
        )
    (output_dir / "final.txt").write_text(final + "\n", encoding="utf-8")
    (output_dir / "reasoning.txt").write_text(reasoning + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v087-original-reviewer-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "outcome": parsed["outcome"],
        "parsed": parsed,
        "reviewer_system_prompt_sha256": sha256_text(
            ORIGINAL_REVIEWER_SYSTEM_PROMPT
        ),
        "compact_materialized_after_exhaustion": False,
        "primary_recovery_error": None,
        "protocol_repaired": protocol_repaired,
        "reasoning_sha256": sha256_text(reasoning),
        "reasoning_observed": True,
        "reasoning_harvest_policy": "accepted_transport_attempt_only",
        "generation": generated["metadata"],
        "adaptive_cutoff_recovery_events": adaptive_recovery_events,
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_compact_markdown_extractor(
    *,
    problem: str,
    proof: str,
    reasoning: str,
    reviewer_final: str,
    endpoint: str,
    output_dir: Path,
    seed: int,
    seed_label: str,
    model: str = MODEL,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime = v084.runtime_for(endpoint, seed, model)
    generated = runtime.text(
        role="gemma",
        prompt=COMPACT_MARKDOWN_EXTRACTOR_SYSTEM_PROMPT,
        user_prompt=compact_extractor_user_prompt(
            problem=problem,
            proof=proof,
            reasoning=reasoning,
            reviewer_final=reviewer_final,
        ),
        destination=output_dir / "generation",
        stage="compact_markdown_trace_extraction",
        temperature=0.1,
        max_tokens=6_000,
        seed_label=seed_label,
        top_p=1.0,
        top_k=-1,
    )
    visible = str(generated["text"]).strip()
    candidates = parse_compact_markdown(visible)
    (output_dir / "final.md").write_text(visible + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v087-compact-markdown-extraction-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "candidate_count": len(candidates),
        "useful_count": sum(bool(row["useful_material"]) for row in candidates),
        "repair_needed_count": sum(bool(row["repair_needed"]) for row in candidates),
        "candidates": candidates,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


__all__ = [
    "BLOCK_PATTERN",
    "COMPACT_MARKDOWN_EXTRACTOR_SYSTEM_PROMPT",
    "ORIGINAL_REVIEWER_SYSTEM_PROMPT",
    "compact_extractor_user_prompt",
    "parse_compact_markdown",
    "run_compact_markdown_extractor",
    "run_original_reviewer",
]
