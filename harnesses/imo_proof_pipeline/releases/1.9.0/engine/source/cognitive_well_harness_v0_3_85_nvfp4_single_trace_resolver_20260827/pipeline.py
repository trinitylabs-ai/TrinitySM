from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import utc_now
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import pipeline as v084

from . import MODEL


TRACE_SELECTOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decisions", "summary"],
    "properties": {
        "decisions": {
            "type": "array",
            "minItems": 0,
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["gap_id", "bucket", "certified_argument", "reason"],
                "properties": {
                    "gap_id": {"type": "string", "pattern": "^TG[0-9]+$"},
                    "bucket": {
                        "type": "string",
                        "enum": ["USE", "REPAIR", "DISCARD"],
                    },
                    "certified_argument": {"type": "string"},
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
        "summary": {"type": "string", "minLength": 1},
    },
}


TRACE_SELECTOR_SYSTEM_PROMPT = r"""You are a conservative olympiad proof
selector-resolver. Solve every supplied local obligation in the context of the
original problem and the complete submitted proof, then explicitly place each
source-bound reviewer-trace candidate into exactly one bucket:

- USE: the trace itself supplies a mathematically valid, non-routine argument that is
  absent from the submitted proof and needed downstream.
- REPAIR: the trace identifies a genuine gap, but its proposed argument is absent,
  invalid, or incomplete; you can construct a rigorous replacement now.
- DISCARD: the trace is false, circular, uncertain, irrelevant, redundant, already
  explicit in the proof, or merely routine elaboration.

For USE, `certified_argument` must contain a self-contained, rigorously checked version
of the trace argument. For REPAIR, it must contain the complete corrected local
argument you constructed. For DISCARD, it must be the empty string. A plausible route
is not certification. Do not credit a trace with mathematics you supplied: if you had
to replace a defective trace argument, use REPAIR rather than USE.

Return one decision for every supplied gap_id, in the same order, and only the required
JSON object.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Re-check every
load-bearing transition before returning the record."""


CERTIFIED_PROOF_RESOLVER_SYSTEM_PROMPT = r"""You are a rigorous olympiad proof
resolver. Rewrite the submitted proof as one complete, self-contained solution to the
original problem.

You receive only selector-certified local arguments. Each packet is marked USE when a
reviewer-trace argument was certified, or REPAIR when the selector constructed and
certified a corrected argument. Integrate these certified arguments at their bound
proof locations and update every affected downstream dependency.

No raw reviewer reasoning or discarded material is present. Do not invent additional
assumptions, silently strengthen a claim, or cite this packet as authority. Preserve
all correct material, notation, and LaTeX as closely as possible. Return only the
complete replacement proof. It must not mention traces, reviewers, buckets,
certification, diagnostics, models, or this workflow.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Do not finalize merely
because a familiar argument or plausible conclusion has been found. Re-check every
load-bearing transition before returning the proof."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def trace_packets(extraction: dict[str, Any]) -> list[dict[str, Any]]:
    """Retain all source-bound extractor records for three-bucket selection."""
    return [
        {
            key: str(gap[key])
            for key in (
                "gap_id",
                "proof_location",
                "claim",
                "trace_evidence",
                "missing_detail",
                "support_origin",
                "dependency_impact",
            )
        }
        for gap in extraction.get("gaps") or []
    ]


def selector_user_prompt(
    *, problem: str, proof: str, packets: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE SUBMITTED PROOF\n\n"
        + proof.strip()
        + "\n\n# SOURCE-BOUND REVIEWER-TRACE CANDIDATES\n\n"
        + json.dumps(packets, ensure_ascii=False, indent=2)
        + "\n\nSolve and categorize every trace candidate now.\n"
    )


def _reasoning_from_generation(generated: dict[str, Any], generation_dir: Path) -> str:
    reasoning = str(generated.get("reasoning") or "").strip()
    if reasoning:
        return reasoning
    paths = sorted(generation_dir.glob("*.reasoning.txt"))
    if not paths:
        raise RuntimeError("resolver completed without an observable reasoning trace")
    return "\n\n".join(
        path.read_text(encoding="utf-8").strip() for path in paths
    ).strip()


def _validate_selector_record(
    *, record: dict[str, Any], packets: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    expected = [str(packet["gap_id"]) for packet in packets]
    actual = [str(row["gap_id"]) for row in record["decisions"]]
    if actual != expected:
        raise ValueError(
            f"selector changed trace IDs/order: expected {expected}, got {actual}"
        )
    decisions: list[dict[str, Any]] = []
    for row in record["decisions"]:
        bucket = str(row["bucket"])
        argument = str(row["certified_argument"]).strip()
        if bucket in {"USE", "REPAIR"} and not argument:
            raise ValueError(f"{row['gap_id']} lacks its certified argument")
        if bucket == "DISCARD" and argument:
            raise ValueError(f"{row['gap_id']} attached material to DISCARD")
        decisions.append({**row, "certified_argument": argument})
    return decisions


def run_trace_selector(
    *, problem: str, proof: str, packets: list[dict[str, Any]], endpoint: str,
    output_dir: Path, seed: int, seed_label: str,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    if not packets:
        result = {
            "schema": "cognitive-well-v085-trace-selector-result-v1",
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
    runtime = v084.runtime_for(endpoint, seed, MODEL)
    record, generated = runtime.structured(
        role="gemma",
        prompt=TRACE_SELECTOR_SYSTEM_PROMPT,
        user_prompt=selector_user_prompt(problem=problem, proof=proof, packets=packets),
        destination=output_dir / "generation",
        stage="trace_selector_resolution",
        schema=TRACE_SELECTOR_SCHEMA,
        temperature=0.2,
        max_tokens=32_768,
        seed_label=seed_label,
        use_explicit_guided_json=True,
    )
    decisions = _validate_selector_record(record=record, packets=packets)
    result = {
        "schema": "cognitive-well-v085-trace-selector-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "selector_call_count": 1,
        "packet_count": len(packets),
        "use_count": sum(row["bucket"] == "USE" for row in decisions),
        "repair_count": sum(row["bucket"] == "REPAIR" for row in decisions),
        "discard_count": sum(row["bucket"] == "DISCARD" for row in decisions),
        "decisions": decisions,
        "summary": record["summary"],
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def certified_trace_packets(
    *, trace_candidates: list[dict[str, Any]], decisions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    candidates = {str(row["gap_id"]): row for row in trace_candidates}
    certified: list[dict[str, Any]] = []
    for decision in decisions:
        if decision["bucket"] == "DISCARD":
            continue
        source = candidates[str(decision["gap_id"])]
        certified.append(
            {
                "gap_id": str(decision["gap_id"]),
                "bucket": str(decision["bucket"]),
                "proof_location": str(source["proof_location"]),
                "claim": str(source["claim"]),
                "certified_argument": str(decision["certified_argument"]),
                "dependency_impact": str(source["dependency_impact"]),
            }
        )
    return certified


def certified_resolver_user_prompt(
    *, problem: str, proof: str, certified: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE PROOF TO RESOLVE\n\n"
        + proof.strip()
        + "\n\n# SELECTOR-CERTIFIED ARGUMENTS ONLY\n\n"
        + json.dumps(certified, ensure_ascii=False, indent=2)
        + "\n\nReturn the complete resolved proof now.\n"
    )


def run_certified_proof_resolution(
    *, problem: str, proof: str, certified: list[dict[str, Any]], endpoint: str,
    output_dir: Path, seed: int, seed_label: str,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    proof_path = output_dir / "complete_proof.md"
    if not certified:
        proof_path.write_text(proof.rstrip() + "\n", encoding="utf-8")
        result = {
            "schema": "cognitive-well-v085-certified-resolution-result-v1",
            "state": "completed",
            "completed_at": utc_now(),
            "action": "UNCHANGED_NO_CERTIFIED_TRACE_MATERIAL",
            "resolver_call_count": 0,
            "certified_packet_count": 0,
            "proof_changed": False,
            "proof_path": str(proof_path.resolve()),
            "generation": None,
            "runtime_recovery_events": [],
        }
        write_json(result_path, result)
        return result
    runtime = v084.runtime_for(endpoint, seed, MODEL)
    generation_dir = output_dir / "generation"
    generated = runtime.text(
        role="gemma",
        prompt=CERTIFIED_PROOF_RESOLVER_SYSTEM_PROMPT,
        user_prompt=certified_resolver_user_prompt(
            problem=problem, proof=proof, certified=certified
        ),
        destination=generation_dir,
        stage="certified_proof_resolution",
        temperature=0.1,
        max_tokens=32_768,
        seed_label=seed_label,
        top_p=1.0,
        top_k=-1,
    )
    replacement = str(generated["text"]).strip()
    if not replacement:
        raise RuntimeError("certified proof resolver produced an empty proof")
    reasoning = _reasoning_from_generation(generated, generation_dir)
    proof_path.write_text(replacement + "\n", encoding="utf-8")
    (output_dir / "reasoning.txt").write_text(reasoning + "\n", encoding="utf-8")
    write_json(output_dir / "certified_trace_packets.json", {"packets": certified})
    result = {
        "schema": "cognitive-well-v085-certified-resolution-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "action": "RESOLVER_CALLED",
        "resolver_call_count": 1,
        "certified_packet_count": len(certified),
        "source_proof_sha256": sha256_text(proof.strip()),
        "output_proof_sha256": sha256_text(replacement),
        "proof_changed": replacement != proof.strip(),
        "proof_path": str(proof_path.resolve()),
        "reasoning_sha256": sha256_text(reasoning),
        "reasoning_observed": True,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_source_trace_extraction(**kwargs: Any) -> dict[str, Any]:
    return v084.run_trace_extraction(**kwargs, model=MODEL)


def run_diagnostic_reviewer(**kwargs: Any) -> dict[str, Any]:
    return v084.run_post_review(**kwargs, model=MODEL)


def run_diagnostic_trace_extraction(**kwargs: Any) -> dict[str, Any]:
    return v084.run_trace_extraction(**kwargs, model=MODEL)


__all__ = [
    "CERTIFIED_PROOF_RESOLVER_SYSTEM_PROMPT",
    "TRACE_SELECTOR_SCHEMA",
    "TRACE_SELECTOR_SYSTEM_PROMPT",
    "certified_resolver_user_prompt",
    "certified_trace_packets",
    "run_diagnostic_reviewer",
    "run_diagnostic_trace_extraction",
    "run_certified_proof_resolution",
    "run_source_trace_extraction",
    "run_trace_selector",
    "selector_user_prompt",
    "trace_packets",
]
