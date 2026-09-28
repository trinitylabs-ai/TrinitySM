from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import (
    pipeline as v084,
)
from cognitive_well_harness_v0_3_85_nvfp4_single_trace_resolver_20260827.pipeline import (
    TRACE_SELECTOR_SCHEMA,
    TRACE_SELECTOR_SYSTEM_PROMPT,
    _validate_selector_record,
    selector_user_prompt,
)

from . import MODEL


MARKDOWN_SELECTOR_SYSTEM_PROMPT = r"""You are a conservative olympiad proof
selector-resolver. Independently solve and check every supplied local obligation in
the context of the original problem and complete submitted proof. For each trace
candidate choose USE, REPAIR, or DISCARD with exactly the same meanings as in the
primary selector. A plausible route is not certification.

Return compact Markdown in this exact layout, with one section per supplied gap in
the same order:

## TG1
- Bucket: USE | REPAIR | DISCARD
- Certified argument: a complete checked local argument, or NONE for DISCARD
- Reason: one concise justification

After all gap sections, return:

## Summary
one concise sentence

Do not return JSON or fenced code. Do not omit a section.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Re-check every
load-bearing transition before returning the record."""


LOCAL_DECISION_MARKDOWN_SELECTOR_SYSTEM_PROMPT = (
    MARKDOWN_SELECTOR_SYSTEM_PROMPT
    + r"""

LOCAL DECISION BOUNDARY

Decide only the supplied source-bound local candidate. Do not solve the entire
original problem or derive a replacement final theorem. A rigorous counterexample
or obstruction to the submitted local claim is a complete corrected local argument
for REPAIR; explicitly state that the downstream theorem remains unproved. If the
local objection is not decisive, use DISCARD. Emit the required record promptly
after this local check."""
)


def parse_markdown_selector_record(
    value: str, packets: list[dict[str, str]]
) -> dict[str, Any]:
    text = value.strip()
    section_re = re.compile(
        r"(?ms)^##\s+(TG[0-9]+)\s*$\n(.*?)(?=^##\s+(?:TG[0-9]+|Summary)\s*$|\Z)"
    )
    decisions: list[dict[str, str]] = []
    for match in section_re.finditer(text):
        gap_id, body = match.group(1), match.group(2).strip()
        bucket_match = re.search(
            r"(?im)^\s*-\s*(?:\*\*)?Bucket(?:\*\*)?\s*:\s*`?(USE|REPAIR|DISCARD)`?\s*$",
            body,
        )
        argument_match = re.search(
            r"(?ims)^\s*-\s*(?:\*\*)?Certified argument(?:\*\*)?\s*:\s*(.*?)"
            r"(?=^\s*-\s*(?:\*\*)?Reason(?:\*\*)?\s*:)",
            body,
        )
        reason_match = re.search(
            r"(?ims)^\s*-\s*(?:\*\*)?Reason(?:\*\*)?\s*:\s*(.*?)\s*$",
            body,
        )
        if not (bucket_match and argument_match and reason_match):
            raise ValueError(f"incomplete Markdown selector section: {gap_id}")
        bucket = bucket_match.group(1).upper()
        argument = argument_match.group(1).strip()
        if argument.upper() == "NONE":
            argument = ""
        decisions.append(
            {
                "gap_id": gap_id,
                "bucket": bucket,
                "certified_argument": argument,
                "reason": reason_match.group(1).strip(),
            }
        )
    summary_match = re.search(r"(?ims)^##\s+Summary\s*$\n(.*?)\s*$", text)
    if not summary_match:
        raise ValueError("Markdown selector response lacks Summary")
    record = {"decisions": decisions, "summary": summary_match.group(1).strip()}
    _validate_selector_record(record=record, packets=packets)
    return record


def markdown_trace_packets(extraction: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "gap_id": f"TG{index}",
            "useful_material": str(candidate["useful_material"]),
            "repair_needed": str(candidate["repair_needed"]),
            "reason": str(candidate["reason"]),
        }
        for index, candidate in enumerate(extraction.get("candidates") or [], start=1)
    ]


def _latest_valid_markdown_generation(
    *, destination: Path, stage: str, packets: list[dict[str, str]]
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Load the newest valid visible result, including runtime replacements.

    The shared runtime stores a repetition-stopped primary response alongside
    ``_replacement_N`` responses.  Its generic cache loader only looks at the
    primary filename, which can hide a later successful replacement on resume.
    Selection is mathematical only when a visible record parses and validates.
    """

    raw_paths = [destination / f"{stage}.raw_response.json"]
    raw_paths.extend(sorted(destination.glob(f"{stage}_replacement_*.raw_response.json")))
    for raw_path in reversed(raw_paths):
        metadata_path = raw_path.with_name(
            raw_path.name.replace(".raw_response.json", ".metadata.json")
        )
        if not metadata_path.is_file():
            continue
        try:
            response = json.loads(raw_path.read_text(encoding="utf-8"))
            text = str(response["choices"][0]["message"].get("content") or "")
            record = parse_markdown_selector_record(text, packets)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
        return record, {"text": text, "metadata": metadata}
    return None


def run_markdown_trace_selector(
    *,
    problem: str,
    proof: str,
    packets: list[dict[str, str]],
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
    if not packets:
        result = {
            "schema": "cognitive-well-v088-markdown-trace-selector-result-v1",
            "state": "completed",
            "completed_at": utc_now(),
            "selector_call_count": 0,
            "packet_count": 0,
            "use_count": 0,
            "repair_count": 0,
            "discard_count": 0,
            "decisions": [],
            "summary": "No extracted trace candidates required selection.",
            "generation": None,
            "runtime_recovery_events": [],
        }
        write_json(result_path, result)
        return result

    runtime = v084.runtime_for(endpoint, seed, model)
    user_prompt = selector_user_prompt(problem=problem, proof=proof, packets=packets)
    terminal_recovery: dict[str, Any] | None = None
    selector_call_count = 1
    try:
        record, generated = runtime.structured(
            role="gemma",
            prompt=TRACE_SELECTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=output_dir / "generation",
            stage="markdown_trace_selector",
            schema=TRACE_SELECTOR_SCHEMA,
            temperature=0.1,
            max_tokens=32_768,
            seed_label=seed_label,
            use_explicit_guided_json=True,
        )
        decisions = _validate_selector_record(record=record, packets=packets)
    except Exception as primary_error:
        # A structured response can occasionally hit the repetition stop before it
        # emits any visible JSON. Keep the nominal request unchanged, then make one
        # fresh-seed, non-guided Markdown attempt so transport recovery cannot turn a
        # mechanical empty response into a mathematical decision.
        retry_runtime = v084.runtime_for(endpoint, seed + 1_000_003, model)
        try:
            generated = retry_runtime.text(
                role="gemma",
                prompt=MARKDOWN_SELECTOR_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                destination=output_dir / "generation",
                stage="markdown_trace_selector_markdown_fallback",
                temperature=0.1,
                max_tokens=32_768,
                seed_label=f"{seed_label}:markdown_fresh_seed",
                top_p=1.0,
                top_k=-1,
            )
            record = parse_markdown_selector_record(str(generated["text"]), packets)
            decisions = _validate_selector_record(record=record, packets=packets)
            terminal_recovery = {
                "kind": "fresh_seed_compact_markdown",
                "primary_error": f"{type(primary_error).__name__}: {primary_error}",
                "repetition_detection_preserved": True,
                "accepted": True,
            }
            runtime = retry_runtime
        except Exception as markdown_error:
            # If one multi-obligation response itself repeats, preserve the same
            # proof-level task but classify each already-independent source packet in
            # a separate call. This is a batching recovery, not a semantic vote.
            decisions = []
            singleton_metadata: list[dict[str, Any]] = []
            singleton_events: list[dict[str, Any]] = []
            summaries: list[str] = []
            for index, packet in enumerate(packets, start=1):
                singleton_runtime = v084.runtime_for(
                    endpoint, seed + 2_000_003 + index, model
                )
                singleton_prompt = selector_user_prompt(
                    problem=problem, proof=proof, packets=[packet]
                )
                generation_dir = output_dir / "generation"
                singleton_stage = (
                    "markdown_trace_selector_markdown_singleton_"
                    + str(packet["gap_id"])
                )
                cached_singleton = _latest_valid_markdown_generation(
                    destination=generation_dir,
                    stage=singleton_stage,
                    packets=[packet],
                )
                try:
                    if cached_singleton is not None:
                        singleton_record, singleton_generated = cached_singleton
                    else:
                        singleton_generated = singleton_runtime.text(
                            role="gemma",
                            prompt=MARKDOWN_SELECTOR_SYSTEM_PROMPT,
                            user_prompt=singleton_prompt,
                            destination=generation_dir,
                            stage=singleton_stage,
                            temperature=0.1,
                            max_tokens=32_768,
                            seed_label=(
                                f"{seed_label}:markdown_singleton:{packet['gap_id']}"
                            ),
                            top_p=1.0,
                            top_k=-1,
                        )
                        singleton_record = parse_markdown_selector_record(
                            str(singleton_generated["text"]), [packet]
                        )
                except Exception as singleton_error:
                    local_runtime = v084.runtime_for(
                        endpoint, seed + 3_000_003 + index, model
                    )
                    local_stage = (
                        "markdown_trace_selector_local_decision_"
                        + str(packet["gap_id"])
                    )
                    cached_local = _latest_valid_markdown_generation(
                        destination=generation_dir,
                        stage=local_stage,
                        packets=[packet],
                    )
                    if cached_local is not None:
                        singleton_record, singleton_generated = cached_local
                    else:
                        singleton_generated = local_runtime.text(
                            role="gemma",
                            prompt=LOCAL_DECISION_MARKDOWN_SELECTOR_SYSTEM_PROMPT,
                            user_prompt=singleton_prompt,
                            destination=generation_dir,
                            stage=local_stage,
                            temperature=0.1,
                            max_tokens=32_768,
                            seed_label=(
                                f"{seed_label}:local_decision:{packet['gap_id']}"
                            ),
                            top_p=1.0,
                            top_k=-1,
                        )
                        singleton_record = parse_markdown_selector_record(
                            str(singleton_generated["text"]), [packet]
                        )
                    singleton_events.append(
                        {
                            "kind": "local_decision_boundary",
                            "stage": str(packet["gap_id"]),
                            "accepted": True,
                            "prior_error": (
                                f"{type(singleton_error).__name__}: {singleton_error}"
                            ),
                            "attempts": [],
                        }
                    )
                decisions.extend(
                    _validate_selector_record(
                        record=singleton_record, packets=[packet]
                    )
                )
                summaries.append(str(singleton_record["summary"]))
                singleton_metadata.append(singleton_generated["metadata"])
                singleton_events.extend(singleton_runtime.recovery_events())
            record = {
                "decisions": decisions,
                "summary": " ".join(summaries),
            }
            generated = {
                "metadata": {
                    "stage": "markdown_trace_selector_markdown_singleton_batch",
                    "subgenerations": singleton_metadata,
                }
            }
            selector_call_count = len(packets)
            terminal_recovery = {
                "kind": "fresh_seed_compact_markdown_singletons",
                "primary_error": f"{type(primary_error).__name__}: {primary_error}",
                "full_markdown_error": (
                    f"{type(markdown_error).__name__}: {markdown_error}"
                ),
                "repetition_detection_preserved": True,
                "accepted": True,
                "singleton_count": len(packets),
            }
            runtime = retry_runtime
            runtime._recovery_events.extend(singleton_events)
    result = {
        "schema": "cognitive-well-v088-markdown-trace-selector-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "selector_call_count": selector_call_count,
        "packet_count": len(packets),
        "use_count": sum(row["bucket"] == "USE" for row in decisions),
        "repair_count": sum(row["bucket"] == "REPAIR" for row in decisions),
        "discard_count": sum(row["bucket"] == "DISCARD" for row in decisions),
        "decisions": decisions,
        "summary": str(record["summary"]),
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
        "terminal_recovery": terminal_recovery,
    }
    write_json(result_path, result)
    return result


__all__ = [
    "markdown_trace_packets",
    "parse_markdown_selector_record",
    "run_markdown_trace_selector",
]
