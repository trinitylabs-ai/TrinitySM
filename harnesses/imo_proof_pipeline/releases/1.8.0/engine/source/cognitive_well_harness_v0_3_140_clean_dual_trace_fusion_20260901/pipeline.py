from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823 import (
    run as reviewer_2,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823 import (
    run as reviewer_3,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
)
from cognitive_well_harness_v0_3_87_markdown_trace_extractor_20260827.pipeline import (
    run_original_reviewer,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


TRACE_TYPES = (
    "DERIVATION",
    "REPAIR_ROUTE",
    "DEFECT",
    "COUNTEREXAMPLE",
    "ABANDONED_ATTEMPT",
)
SELECTOR_DISPOSITIONS = (
    "FUSION_RELEVANT",
    "POSSIBLE_LEAD",
    "ROUTINE",
    "UNSUPPORTED",
)
TRACE_RELATIONS = ("EQUIVALENT", "DISTINCT", "UNCERTAIN")
FUSION_TRACE_DISPOSITIONS = (
    "VALIDATED_MATERIAL",
    "USEFUL_UNRESOLVED_LEAD",
    "REJECTED",
    "IRRELEVANT",
)
HANDOFF_DISPOSITIONS = {"VALIDATED_MATERIAL", "USEFUL_UNRESOLVED_LEAD"}
EXTERNAL_MARKERS = (
    "CODEX_SCORECARD",
    "codex grade",
    "codex score",
    "gold-informed",
    "strict scorer",
    "external scorer feedback",
)


TRACE_PACKET_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["packets"],
    "properties": {
        "packets": {
            "type": "array",
            "minItems": 0,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "trace_id",
                    "start_line",
                    "end_line",
                    "type",
                    "target",
                    "relevance_reason",
                ],
                "properties": {
                    "trace_id": {"type": "string", "minLength": 3},
                    "start_line": {"type": "integer", "minimum": 1},
                    "end_line": {"type": "integer", "minimum": 1},
                    "type": {"type": "string", "enum": list(TRACE_TYPES)},
                    "target": {"type": "string", "minLength": 1},
                    "relevance_reason": {"type": "string", "minLength": 1},
                },
            },
        }
    },
}


TRACE_SELECTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decisions", "selected_trace_ids"],
    "properties": {
        "decisions": {
            "type": "array",
            "minItems": 0,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "trace_id",
                    "disposition",
                    "relation_to_visible",
                    "reason",
                    "relation_reason",
                ],
                "properties": {
                    "trace_id": {"type": "string", "minLength": 4},
                    "disposition": {
                        "type": "string",
                        "enum": list(SELECTOR_DISPOSITIONS),
                    },
                    "relation_to_visible": {
                        "type": "string",
                        "enum": list(TRACE_RELATIONS),
                    },
                    "reason": {"type": "string", "minLength": 1},
                    "relation_reason": {"type": "string", "minLength": 1},
                },
            },
        },
        "selected_trace_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 8,
            "items": {"type": "string", "minLength": 4},
        },
    },
}


FUSION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "verdict",
        "reviewer_1_assessment",
        "reviewer_2_assessment",
        "reviewer_3_assessment",
        "decisive_location",
        "failed_obligation",
        "independent_validation",
        "impact_on_proof",
        "repair_scope",
        "resolver_brief",
        "preservable_material",
        "trace_dispositions",
    ],
    "properties": {
        "verdict": {
            "type": "string",
            "enum": [
                "ACCEPT_AS_WRITTEN",
                "ACCEPT_WITH_ROUTINE_COMPLETION",
                "REPAIR_NEEDED",
                "INCONCLUSIVE",
            ],
        },
        "reviewer_1_assessment": {"type": "string", "minLength": 1},
        "reviewer_2_assessment": {"type": "string", "minLength": 1},
        "reviewer_3_assessment": {"type": "string", "minLength": 1},
        "decisive_location": {"type": "string"},
        "failed_obligation": {"type": "string"},
        "independent_validation": {"type": "string", "minLength": 1},
        "impact_on_proof": {"type": "string", "minLength": 1},
        "repair_scope": {"type": "string", "enum": ["LOCAL", "STRUCTURAL"]},
        "resolver_brief": {"type": "string", "minLength": 1},
        "preservable_material": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "trace_dispositions": {
            "type": "array",
            "minItems": 0,
            "maxItems": 16,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["trace_id", "disposition", "reason"],
                "properties": {
                    "trace_id": {"type": "string", "minLength": 4},
                    "disposition": {
                        "type": "string",
                        "enum": list(FUSION_TRACE_DISPOSITIONS),
                    },
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_seed(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big") or 1


def stable_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_status(path: Path, *, state: str, stage: str, **extra: Any) -> None:
    write_json(path, {"state": state, "stage": stage, **extra, "updated_at": utc_now()})


def assert_no_external_material(value: str, *, label: str) -> None:
    lowered = value.lower()
    hits = [marker for marker in EXTERNAL_MARKERS if marker.lower() in lowered]
    if hits:
        raise ValueError(f"external-information leak guard rejected {label}: {hits}")


def problem_number(problem_id: str) -> int:
    match = re.search(r"(?:^|_)p(\d+)$", problem_id)
    return int(match.group(1)) if match else 0


def trace_chunks(trace: str, *, chunk_lines: int = 100) -> list[dict[str, Any]]:
    if chunk_lines < 40:
        raise ValueError("trace chunks must contain at least 40 lines")
    lines = trace.splitlines()
    return [
        {
            "first_line": start,
            "last_line": min(len(lines), start + chunk_lines - 1),
            "text": "\n".join(lines[start - 1 : start + chunk_lines - 1]),
        }
        for start in range(1, len(lines) + 1, chunk_lines)
    ]


def numbered_trace(trace: str, *, first_line: int) -> str:
    return "\n".join(
        f"L{index}: {line}"
        for index, line in enumerate(trace.splitlines(), start=first_line)
    )


def extraction_prompt(
    *, role_label: str, problem: str, proof: str, visible: str, trace: str, first_line: int
) -> str:
    return f"""You are a source-bound mathematical trace extractor.

The hidden trace below is unverified solver-internal work from the same {role_label}
call whose visible record is supplied. Identify only compact contiguous source-line
spans containing concrete mathematics that could materially help an independent
Fusion judge assess or repair the submitted proof: an explicit derivation, equation
system, counterexample, exact defect, or genuinely new repair route. Exclude
meta-commentary and repetition. An abandoned attempt may be selected only when its
failure itself constrains a repair.

Return line coordinates and short indexing metadata only. Do not quote, normalize,
correct, certify, or complete the source mathematics. Use local IDs TG1, TG2, ... in
source order. Select at most eight packets; each span must be at most 40 lines.

PROBLEM
{problem}

SUBMITTED PROOF
{proof}

VISIBLE {role_label} RECORD
{visible}

NUMBERED HIDDEN TRACE CHUNK
{numbered_trace(trace, first_line=first_line)}
"""


def validate_extraction(
    record: dict[str, Any], *, minimum_line: int, maximum_line: int
) -> list[dict[str, Any]]:
    packets = [dict(row) for row in record["packets"]]
    expected = [f"TG{index}" for index in range(1, len(packets) + 1)]
    if [str(row["trace_id"]) for row in packets] != expected:
        raise ValueError("local trace ID/order drift")
    previous_end = minimum_line - 1
    for row in packets:
        start, end = int(row["start_line"]), int(row["end_line"])
        if start < minimum_line or end > maximum_line or start > end:
            raise ValueError(f"invalid trace span {start}-{end}")
        if start <= previous_end:
            raise ValueError("trace packets overlap or are not in source order")
        previous_end = end

    # A model-selected span can cross the 40-line packet transport boundary by
    # a few lines even though its coordinates and ordering are otherwise valid.
    # Preserve the selection exactly by partitioning it into consecutive source
    # windows.  This changes packet boundaries only: no source line is dropped,
    # duplicated, summarized, or rewritten.
    normalized: list[dict[str, Any]] = []
    for row in packets:
        source_model_trace_id = str(row["trace_id"])
        start, end = int(row["start_line"]), int(row["end_line"])
        fragment_index = 0
        fragment_start = start
        while fragment_start <= end:
            fragment_index += 1
            fragment_end = min(fragment_start + 39, end)
            normalized.append(
                {
                    **row,
                    "source_model_trace_id": source_model_trace_id,
                    "transport_fragment_index": fragment_index,
                    "start_line": fragment_start,
                    "end_line": fragment_end,
                }
            )
            fragment_start = fragment_end + 1
    for index, row in enumerate(normalized, start=1):
        row["trace_id"] = f"TG{index}"
    return normalized


def bind_packets(
    *, role_key: str, trace: str, trace_path: Path, packets: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    prefixes = {
        "reviewer_1": "R1TG",
        "reviewer_2": "R2TG",
        "reviewer_3": "R3TG",
    }
    if role_key not in prefixes:
        raise ValueError(f"unsupported trace source role: {role_key}")
    prefix = prefixes[role_key]
    lines = trace.splitlines()
    ordered = sorted(
        (dict(row) for row in packets),
        key=lambda row: (int(row["start_line"]), int(row["end_line"])),
    )
    result: list[dict[str, Any]] = []
    previous_end = 0
    for index, row in enumerate(ordered, start=1):
        start, end = int(row["start_line"]), int(row["end_line"])
        if start <= previous_end:
            raise ValueError("cross-chunk trace packets overlap")
        exact = "\n".join(lines[start - 1 : end])
        result.append(
            {
                **row,
                "local_trace_id": row["trace_id"],
                "trace_id": f"{prefix}{index}",
                "source_role": role_key,
                "source_artifact_path": str(trace_path.resolve()),
                "source_line_range": f"{start}-{end}",
                "exact_source_text": exact,
                "exact_source_sha256": sha256_text(exact),
                "content_transformations": [],
                "verification_status": "UNVERIFIED",
            }
        )
        previous_end = end
    return result


def render_packets(packets: list[dict[str, Any]]) -> str:
    if not packets:
        return "(none)"
    return "\n\n".join(
        "\n".join(
            [
                f"TRACE ID: {row['trace_id']}",
                f"SOURCE ROLE: {row['source_role']}",
                f"SOURCE LINES: {row['source_line_range']}",
                f"EXTRACTOR TYPE: {row['type']}",
                f"EXTRACTOR TARGET: {row['target']}",
                "BEGIN EXACT UNVERIFIED SOURCE TEXT",
                str(row["exact_source_text"]),
                "END EXACT UNVERIFIED SOURCE TEXT",
            ]
        )
        for row in packets
    )


def selector_prompt(
    *, role_label: str, problem: str, proof: str, visible: str, packets: list[dict[str, Any]]
) -> str:
    return f"""You are an independent mathematical relevance and relation selector.

Select a minimal, nonredundant subset of source-bound {role_label} hidden-trace
packets that could materially help Fusion. Do not select multiple packets that make
the same mathematical argument; retain the most complete representative.

Every selected packet needs two independent judgments. disposition is one of:
- FUSION_RELEVANT: concrete mathematics directly evaluates or repairs an obligation.
- POSSIBLE_LEAD: a specific unestablished route worth exposing as unverified work.
- ROUTINE: no material information for Fusion.
- UNSUPPORTED: unusable or mathematically suspect.

relation_to_visible is one of:
- EQUIVALENT: no material claim, derivation, condition, or gap beyond the visible record.
- DISTINCT: at least one material item is absent from or conflicts with the visible record.
- UNCERTAIN: equivalence cannot be positively established.

Shared vocabulary or the same verdict does not establish equivalence. Detailed
repetition of an argument already present in the visible record is EQUIVALENT.
Selected packets must be FUSION_RELEVANT or POSSIBLE_LEAD. Return decisions only for
selected IDs in selected_trace_ids order. If no packet merits selection, return both
arrays empty. Relation does not certify mathematics. Fusion will independently
adjudicate every surviving packet.

PROBLEM
{problem}

SUBMITTED PROOF
{proof}

VISIBLE {role_label} RECORD — ALWAYS RETAINED
{visible}

SOURCE-BOUND {role_label} TRACE PACKETS
{render_packets(packets)}
"""


def validate_selection(
    record: dict[str, Any], packets: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid_ids = [str(row["trace_id"]) for row in packets]
    selected_ids = [str(value) for value in record["selected_trace_ids"]]
    decisions = [dict(row) for row in record["decisions"]]
    observed = [str(row["trace_id"]) for row in decisions]
    if observed != selected_ids:
        raise ValueError("selector decision/selected-ID drift")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("selector returned duplicate IDs")
    if [trace_id for trace_id in valid_ids if trace_id in selected_ids] != selected_ids:
        raise ValueError("selector IDs are unknown or not in source order")
    by_id = {str(row["trace_id"]): row for row in decisions}
    survivors: list[dict[str, Any]] = []
    for packet in packets:
        decision = by_id.get(str(packet["trace_id"]))
        if decision is None:
            continue
        if decision["disposition"] not in {"FUSION_RELEVANT", "POSSIBLE_LEAD"}:
            raise ValueError("selector retained a non-useful disposition")
        if decision["relation_to_visible"] == "EQUIVALENT":
            continue
        survivors.append({**packet, "selector_decision": decision})
    return decisions, survivors


def fusion_prompt(
    *,
    problem: str,
    proof: str,
    reviewer_1: str,
    reviewer_2: str,
    reviewer_3: str,
    r1_packets: list[dict[str, Any]],
    r2_packets: list[dict[str, Any]],
) -> str:
    return f"""You are the independent Fusion judge for one submitted Olympiad proof.

Resolve the three visible reviews against the original proof. Reviewer 1 and Reviewer
2 may additionally have source-bound hidden-trace supplements. Their exact text is
UNVERIFIED solver-internal work, not a premise or certified lemma. Independently
adjudicate every supplied trace ID:
- VALIDATED_MATERIAL: displayed mathematics was checked, sound, and useful.
- USEFUL_UNRESOLVED_LEAD: concrete and relevant but still requires derivation.
- REJECTED: wrong or misleading.
- IRRELEVANT: immaterial.

Return one trace disposition for every supplied ID, first Reviewer 1 then Reviewer 2,
in source order. If no trace is supplied, return an empty trace_dispositions array.
For REPAIR_NEEDED or INCONCLUSIVE, identify the first decisive obligation and provide
a compact repair brief. Any replacement proof must be complete and self-contained
from the original assumptions and may not cite a trace as authority.

PROBLEM
{problem}

SUBMITTED PROOF
{proof}

REVIEWER 1 VISIBLE RECORD
{reviewer_1}

REVIEWER 2 VISIBLE RECORD
{reviewer_2}

REVIEWER 3 VISIBLE RECORD
{reviewer_3}

SOURCE-BOUND REVIEWER 1 TRACE SUPPLEMENT
{render_packets(r1_packets)}

SOURCE-BOUND REVIEWER 2 TRACE SUPPLEMENT
{render_packets(r2_packets)}
"""


def validate_fusion_dispositions(
    record: dict[str, Any], packets: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    decisions = [dict(row) for row in record["trace_dispositions"]]
    expected = [str(row["trace_id"]) for row in packets]
    observed = [str(row["trace_id"]) for row in decisions]
    if observed != expected:
        raise ValueError(f"Fusion trace-ID/order drift: {observed} != {expected}")
    return decisions


def build_trace_handoff(
    packets: list[dict[str, Any]], dispositions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {str(row["trace_id"]): row for row in dispositions}
    handoff: list[dict[str, Any]] = []
    for packet in packets:
        decision = by_id[str(packet["trace_id"])]
        if decision["disposition"] not in HANDOFF_DISPOSITIONS:
            continue
        handoff.append(
            {
                "trace_id": packet["trace_id"],
                "source_role": packet["source_role"],
                "fusion_disposition": decision["disposition"],
                "fusion_reason": decision["reason"],
                "source_artifact_path": packet["source_artifact_path"],
                "source_line_range": packet["source_line_range"],
                "exact_source_text": packet["exact_source_text"],
                "exact_source_sha256": packet["exact_source_sha256"],
                "verification_status": (
                    "FUSION_VALIDATED"
                    if decision["disposition"] == "VALIDATED_MATERIAL"
                    else "UNVERIFIED_LEAD"
                ),
                "content_transformations": [],
                "usage_rule": (
                    "Re-derive self-containedly from the original assumptions; "
                    "do not cite the trace as authority."
                ),
            }
        )
    return handoff


def unique_nonempty(values: list[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def compact_brief(
    *, fusion: dict[str, Any], handoff: list[dict[str, Any]]
) -> dict[str, Any]:
    trace_material: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in handoff:
        digest = str(row["exact_source_sha256"])
        if digest in seen:
            continue
        seen.add(digest)
        trace_material.append(
            {
                "trace_id": str(row["trace_id"]),
                "source_role": str(row["source_role"]),
                "status": str(row["verification_status"]),
                "role": str(row["fusion_reason"]),
                "text": str(row["exact_source_text"]),
            }
        )
    verdict = str(fusion["verdict"])
    return {
        "route_state": (
            "FUSION_GUIDED_REPAIR"
            if verdict in {"REPAIR_NEEDED", "INCONCLUSIVE"}
            else "FUSION_GUIDED_RIGOROUS_REWRITE"
        ),
        "route_state_is_certification": False,
        "fusion_verdict": verdict,
        "failed_obligation": str(fusion.get("failed_obligation") or "").strip(),
        "preserve_after_rechecking": unique_nonempty(
            list(fusion.get("preservable_material") or [])
        ),
        "replacement_chain": unique_nonempty([fusion.get("resolver_brief")]),
        "forbidden_shortcuts": [
            "Do not assert the failed obligation, or an equivalent reformulation, "
            "without a complete derivation from the original assumptions.",
            "Do not cite a reviewer, Fusion record, or hidden trace as authority.",
        ],
        "trace_material": trace_material,
    }


def compact_synthesis_prompt(*, problem: str, proof: str, brief: dict[str, Any]) -> str:
    preserve = "\n".join(
        f"- {item}" for item in brief["preserve_after_rechecking"]
    ) or "- (none designated; independently recheck the proof)"
    chain = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(brief["replacement_chain"], start=1)
    ) or "1. Independently produce a rigorous complete proof."
    shortcuts = "\n".join(f"- {item}" for item in brief["forbidden_shortcuts"])
    trace_blocks = "\n\n".join(
        "\n".join(
            [
                f"TRACE {row['trace_id']} FROM {row['source_role']} — {row['status']}",
                f"ROLE: {row['role']}",
                str(row["text"]),
            ]
        )
        for row in brief["trace_material"]
    ) or "(none)"
    failed = brief["failed_obligation"] or "(no nonroutine failed obligation identified)"
    return f"""You are an expert Olympiad mathematician making one bounded attempt to
produce a rigorous complete proof. The supplied Fusion brief and trace material are
unverified solver-internal guidance, not premises or certificates. Re-derive every
used claim from the original problem. If completion is unavailable, give the
strongest rigorous partial result and state the exact first remaining gap. Never hide
a missing calculation behind phrases such as "after simplification". Return only the
proof.

ORIGINAL PROBLEM
{problem}

SUBMITTED PROOF TO RECHECK OR REPLACE
{proof}

FUSION VERDICT
{brief['fusion_verdict']}

FAILED OBLIGATION
{failed}

PRESERVE ONLY AFTER RECHECKING
{preserve}

PROPOSED REPLACEMENT CHAIN — UNVERIFIED
{chain}

FORBIDDEN SHORTCUTS
{shortcuts}

TRACE MATERIAL — EACH EXACT SOURCE SPAN APPEARS ONCE
{trace_blocks}
"""


def audit_compact_prompt(prompt: str, brief: dict[str, Any]) -> dict[str, Any]:
    occurrence_counts = {
        str(row["trace_id"]): prompt.count(str(row["text"]))
        for row in brief["trace_material"]
    }
    forbidden_payload_markers = (
        "source_artifact_path",
        "exact_source_sha256",
        "trace_material_handoff",
        "reviewer_1_assessment",
        "reviewer_2_assessment",
        "reviewer_3_assessment",
    )
    return {
        "trace_text_occurrence_counts": occurrence_counts,
        "every_trace_text_appears_exactly_once": all(
            count == 1 for count in occurrence_counts.values()
        ),
        "forbidden_payload_marker_hits": {
            marker: marker in prompt for marker in forbidden_payload_markers
        },
        "all_forbidden_payload_markers_absent": not any(
            marker in prompt for marker in forbidden_payload_markers
        ),
    }


def runtime_for(
    *, gemma_endpoint: str, qwen_endpoint: str, master_seed: int
) -> ResilientModelRuntime:
    return ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=gemma_endpoint.rstrip("/"),
            qwen_endpoint=qwen_endpoint.rstrip("/"),
            gemma_model=GEMMA_MODEL,
            qwen_model=QWEN_MODEL,
            master_seed=master_seed,
            reasoning_effort="max",
        )
    )


def review_task(
    *,
    problem_id: str,
    candidate_id: str,
    problem: str,
    proof: str,
    problem_path: Path,
    proof_path: Path,
    endpoint: str,
    gpu: int,
) -> dict[str, Any]:
    return {
        "proof_index": 0,
        "problem_number": problem_number(problem_id),
        "problem_id": problem_id,
        "candidate_id": candidate_id,
        "problem": problem,
        "problem_path": str(problem_path.resolve()),
        "problem_sha256": sha256_text(problem),
        "proof": proof,
        "proof_path": str(proof_path.resolve()),
        "proof_sha256": sha256_text(proof),
        "endpoint": endpoint.rstrip("/"),
        "gpu": gpu,
    }


def build_reviewer3_task(
    *,
    problem_id: str,
    candidate_id: str,
    problem: str,
    proof: str,
    problem_path: Path,
    proof_path: Path,
    gemma_endpoint: str,
    master_seed: int,
    seed_namespace: str,
) -> dict[str, Any]:
    label = f"{seed_namespace}:{problem_id}:{candidate_id}:reviewer_3"
    task = review_task(
        problem_id=problem_id,
        candidate_id=candidate_id,
        problem=problem,
        proof=proof,
        problem_path=problem_path,
        proof_path=proof_path,
        endpoint=gemma_endpoint,
        gpu=0,
    )
    task.update(
        {
            "seed": stable_seed(f"{master_seed}:{label}"),
            "temperature": 0.2,
            "temperature_label": "t02",
            "model_key": "gemma4",
            "model_name": GEMMA_MODEL,
            "task_id": f"{problem_id}.{candidate_id}.reviewer3.t02",
        }
    )
    return task


def run_reviews(
    *,
    problem_id: str,
    candidate_id: str,
    problem: str,
    proof: str,
    problem_path: Path,
    proof_path: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    reviewer1_initial_max_tokens: int = 16_000,
    reviewer1_recovery_max_tokens: tuple[int, ...] = (24_000, 32_000),
    reviewer1_vary_retry_seed: bool = False,
    reviewer1_protocol_repair_max_tokens: int = 12_000,
) -> dict[str, Any]:
    r1_dir = output_dir / "reviewer_1"
    r2_root = output_dir / "reviewer_2_stage"
    r3_root = output_dir / "reviewer_3_stage"
    r1_label = f"{seed_namespace}:{problem_id}:{candidate_id}:reviewer_1"
    r2_label = f"{seed_namespace}:{problem_id}:{candidate_id}:reviewer_2"

    r2_task = review_task(
        problem_id=problem_id,
        candidate_id=candidate_id,
        problem=problem,
        proof=proof,
        problem_path=problem_path,
        proof_path=proof_path,
        endpoint=qwen_endpoint,
        gpu=1,
    )
    r2_task.update(
        {
            "seed": stable_seed(f"{master_seed}:{r2_label}"),
            "temperature": 0.2,
            "temperature_label": "t02",
            "model_key": "qwen36",
            "model_name": QWEN_MODEL,
            "task_id": f"{problem_id}.{candidate_id}.reviewer2.t02",
        }
    )

    r3_task = build_reviewer3_task(
        problem_id=problem_id,
        candidate_id=candidate_id,
        problem=problem,
        proof=proof,
        problem_path=problem_path,
        proof_path=proof_path,
        gemma_endpoint=gemma_endpoint,
        master_seed=master_seed,
        seed_namespace=seed_namespace,
    )

    def run_r1() -> dict[str, Any]:
        return run_original_reviewer(
            problem=problem,
            proof=proof,
            endpoint=gemma_endpoint,
            output_dir=r1_dir,
            seed=stable_seed(f"{master_seed}:{r1_label}:master"),
            seed_label=r1_label,
            model=GEMMA_MODEL,
            initial_max_tokens=reviewer1_initial_max_tokens,
            recovery_max_tokens=reviewer1_recovery_max_tokens,
            vary_retry_seed=reviewer1_vary_retry_seed,
            protocol_repair_max_tokens=reviewer1_protocol_repair_max_tokens,
        )

    def run_r2() -> dict[str, Any]:
        return reviewer_2.run_task(output_dir=r2_root, task=r2_task)

    def run_r3() -> dict[str, Any]:
        return reviewer_3.run_task(output_dir=r3_root, task=r3_task)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        r1_future = executor.submit(run_r1)
        r2_future = executor.submit(run_r2)
        # Reviewer 3 shares Gemma with Reviewer 1. Start it as soon as Reviewer 1
        # releases that endpoint instead of idling until the independent Qwen
        # Reviewer 2 call completes.
        r1_result = r1_future.result()
        r3_future = executor.submit(run_r3)
        r2_result = r2_future.result()
        r3_result = r3_future.result()

    r2_dir = reviewer_2.task_output_dir(r2_root, r2_task)
    r3_dir = reviewer_3.task_output_dir(r3_root, r3_task)
    paths = {
        "reviewer_1": r1_dir,
        "reviewer_2": r2_dir,
        "reviewer_3": r3_dir,
    }
    visible = {
        role: (directory / "final.txt").read_text(encoding="utf-8").strip()
        for role, directory in paths.items()
    }
    r3_generation = r3_result.get("generation")
    r3_reasoning_value = (
        r3_generation.get("reasoning_path")
        if isinstance(r3_generation, dict)
        else None
    )
    r3_reasoning_path = Path(
        str(r3_reasoning_value or (r3_dir / "reviewer3.reasoning.txt"))
    )
    reasoning_paths = {
        "reviewer_1": r1_dir / "reasoning.txt",
        "reviewer_2": r2_dir / "reasoning.txt",
        "reviewer_3": r3_reasoning_path,
    }
    for role, path in reasoning_paths.items():
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise RuntimeError(f"{role} accepted reasoning trace is unavailable")
    if r1_result.get("reasoning_harvest_policy") != "accepted_transport_attempt_only":
        raise RuntimeError("Reviewer 1 accepted-attempt-only harvest policy is inactive")
    if r2_result.get("reasoning_harvest_policy") != "accepted_transport_attempt_only":
        raise RuntimeError("Reviewer 2 accepted-attempt-only harvest policy is inactive")
    return {
        "visible": visible,
        "reasoning_paths": {role: str(path.resolve()) for role, path in reasoning_paths.items()},
        "results": {
            "reviewer_1": r1_result,
            "reviewer_2": r2_result,
            "reviewer_3": r3_result,
        },
    }


def extract_role_trace(
    *,
    runtime: ResilientModelRuntime,
    role_key: str,
    problem: str,
    proof: str,
    visible: str,
    trace_path: Path,
    output_dir: Path,
    seed_label: str,
) -> list[dict[str, Any]]:
    role_labels = {
        "reviewer_1": "REVIEWER 1",
        "reviewer_2": "REVIEWER 2",
        "reviewer_3": "REVIEWER 3",
    }
    if role_key not in role_labels:
        raise ValueError(f"unsupported trace source role: {role_key}")
    role_label = role_labels[role_key]
    trace = trace_path.read_text(encoding="utf-8").strip()
    chunks = trace_chunks(trace)

    def extract(chunk: dict[str, Any]) -> dict[str, Any]:
        first, last = int(chunk["first_line"]), int(chunk["last_line"])
        prompt = extraction_prompt(
            role_label=role_label,
            problem=problem,
            proof=proof,
            visible=visible,
            trace=str(chunk["text"]),
            first_line=first,
        )
        record, generation = runtime.structured(
            role="gemma",
            prompt=prompt,
            destination=output_dir / f"chunk_{first:04d}_{last:04d}",
            stage=f"{role_key}_trace_extraction",
            schema=TRACE_PACKET_SCHEMA,
            temperature=0.1,
            max_tokens=8_192,
            seed_label=f"{seed_label}:{first}:{last}",
        )
        return {
            "packets": validate_extraction(
                record, minimum_line=first, maximum_line=last
            ),
            "generation": generation.get("metadata"),
            "first_line": first,
            "last_line": last,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        rows = list(executor.map(extract, chunks))
    packets = bind_packets(
        role_key=role_key,
        trace=trace,
        trace_path=trace_path,
        packets=[packet for row in rows for packet in row["packets"]],
    )
    write_json(
        output_dir / "bound_packets.json",
        {
            "source_role": role_key,
            "source_trace_path": str(trace_path.resolve()),
            "source_trace_sha256": sha256_file(trace_path),
            "chunk_count": len(chunks),
            "parallel_workers": 4,
            "packets": packets,
            "chunks": rows,
        },
    )
    return packets


def select_role_trace(
    *,
    runtime: ResilientModelRuntime,
    role_key: str,
    problem: str,
    proof: str,
    visible: str,
    packets: list[dict[str, Any]],
    output_dir: Path,
    seed_label: str,
) -> list[dict[str, Any]]:
    role_labels = {
        "reviewer_1": "REVIEWER 1",
        "reviewer_2": "REVIEWER 2",
        "reviewer_3": "REVIEWER 3",
    }
    if role_key not in role_labels:
        raise ValueError(f"unsupported trace source role: {role_key}")
    role_label = role_labels[role_key]
    current = packets
    pass_results: list[dict[str, Any]] = []
    for pass_index in (1,):
        if not current:
            break
        prompt = selector_prompt(
            role_label=role_label,
            problem=problem,
            proof=proof,
            visible=visible,
            packets=current,
        )
        record, generation = runtime.structured(
            role="qwen",
            prompt=prompt,
            destination=output_dir / f"pass_{pass_index}",
            stage=f"{role_key}_trace_selection_pass_{pass_index}",
            schema=TRACE_SELECTION_SCHEMA,
            temperature=0.1,
            max_tokens=12_288,
            seed_label=f"{seed_label}:pass:{pass_index}",
        )
        decisions, survivors = validate_selection(record, current)
        pass_results.append(
            {
                "pass": pass_index,
                "input_trace_ids": [row["trace_id"] for row in current],
                "decisions": decisions,
                "selected_trace_ids": [
                    str(value) for value in record["selected_trace_ids"]
                ],
                "distinct_or_uncertain_survivor_ids": [
                    row["trace_id"] for row in survivors
                ],
                "generation": generation.get("metadata"),
            }
        )
        current = survivors
        if len(current) <= 1:
            break
    write_json(
        output_dir / "selection.json",
        {
            "source_role": role_key,
            "bounded_pass_count": len(pass_results),
            "passes": pass_results,
            "final_trace_ids": [row["trace_id"] for row in current],
        },
    )
    return current


def run_pipeline(
    *,
    problem_json: Path,
    candidate_result: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    status_path = destination / "status.json"
    try:
        problem_path = problem_json.resolve()
        candidate_path = candidate_result.resolve()
        problem_record = read_object(problem_path)
        candidate = read_object(candidate_path)
        problem_id = str(problem_record.get("problem_id") or "").strip()
        problem = str(problem_record.get("claim") or "").strip()
        candidate_id = str(candidate.get("candidate_id") or "").strip()
        proof = str(candidate.get("proof") or "").strip()
        if not all((problem_id, problem, candidate_id, proof)):
            raise ValueError("problem_id, claim, candidate_id, and proof are required")
        assert_no_external_material(problem, label="problem")
        assert_no_external_material(proof, label="candidate proof")
        proof_source_path = Path(str(candidate.get("proof_path") or candidate_path))
        if not proof_source_path.is_absolute():
            proof_source_path = (candidate_path.parent / proof_source_path).resolve()

        source_contract = {
            "problem_json": str(problem_path),
            "problem_json_sha256": sha256_file(problem_path),
            "candidate_result": str(candidate_path),
            "candidate_result_sha256": sha256_file(candidate_path),
            "consumed_problem_fields": ["problem_id", "claim"],
            "consumed_candidate_fields": ["candidate_id", "proof", "proof_path"],
            "gemma_endpoint": gemma_endpoint.rstrip("/"),
            "qwen_endpoint": qwen_endpoint.rstrip("/"),
            "master_seed": master_seed,
            "seed_namespace": seed_namespace,
            "external_information_injection": False,
            "cross_problem_information_injection": False,
            "historical_problem_lookup": False,
        }
        input_sha256 = stable_digest(source_contract)
        summary_path = destination / "summary.json"
        if summary_path.is_file():
            saved = read_object(summary_path)
            if saved.get("input_sha256") != input_sha256:
                raise ValueError("refusing to reuse output directory after input drift")
            if saved.get("state") == "completed":
                return saved

        write_json(
            destination / "manifest.json",
            {
                "schema": "cognitive-well-v0140-clean-dual-trace-manifest-v1",
                "harness_version": HARNESS_VERSION,
                "created_at": utc_now(),
                "input_sha256": input_sha256,
                "source": source_contract,
                "models": {
                    "reviewer_1": GEMMA_MODEL,
                    "reviewer_2": QWEN_MODEL,
                    "reviewer_3": GEMMA_MODEL,
                    "trace_extractor": GEMMA_MODEL,
                    "trace_selector": QWEN_MODEL,
                    "fusion": GEMMA_MODEL,
                    "proof_synthesis": GEMMA_MODEL,
                },
                "policy": {
                    "reviewer_1_cutoff": "clean_same-seed_16k_to_24k_to_32k_then_fail_closed",
                    "reviewer_2_cutoff": "clean_same-seed_16k_to_24k_to_32k_then_fail_closed",
                    "trace_source": "accepted_transport_attempt_only",
                    "trace_selection": "one_bounded_minimal_relation_pass",
                    "visible_reviews_always_retained": True,
                    "fusion_trace_material_unverified": True,
                    "compact_handoff_deterministic": True,
                    "independent_external_scoring_in_solver": False,
                },
            },
        )
        write_json(
            destination / "leak_audit.json",
            {
                "state": "passed",
                "solver_inputs_are_current_problem_local": True,
                "accepted_hidden_traces_are_solver_internal": True,
                "gold_supplied": False,
                "codex_grades_supplied": False,
                "external_scorer_feedback_supplied": False,
                "cross_problem_information_supplied": False,
                "handcrafted_problem_specific_prompt_guidance": False,
                "unconsumed_candidate_fields_are_not_injected": True,
            },
        )
        if dry_run:
            result = {
                "schema": "cognitive-well-v0140-summary-v1",
                "harness_version": HARNESS_VERSION,
                "state": "dry_run_completed",
                "input_sha256": input_sha256,
                "problem_id": problem_id,
                "candidate_id": candidate_id,
            }
            write_json(summary_path, result)
            write_status(
                status_path, state="dry_run_completed", stage="source_and_leak_validation"
            )
            return result

        write_status(status_path, state="running", stage="fresh_reviews")
        reviews = run_reviews(
            problem_id=problem_id,
            candidate_id=candidate_id,
            problem=problem,
            proof=proof,
            problem_path=problem_path,
            proof_path=proof_source_path,
            output_dir=destination / "01_reviews",
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=seed_namespace,
        )
        write_json(destination / "01_reviews" / "summary.json", reviews)

        runtime = runtime_for(
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
        )
        raw_packets: dict[str, list[dict[str, Any]]] = {}
        selected_packets: dict[str, list[dict[str, Any]]] = {}
        for role_key in ("reviewer_1", "reviewer_2"):
            write_status(
                status_path, state="running", stage=f"{role_key}_accepted_trace_extraction"
            )
            role_root = destination / "02_trace_harvest" / role_key
            raw_packets[role_key] = extract_role_trace(
                runtime=runtime,
                role_key=role_key,
                problem=problem,
                proof=proof,
                visible=reviews["visible"][role_key],
                trace_path=Path(reviews["reasoning_paths"][role_key]),
                output_dir=role_root / "extraction",
                seed_label=f"{seed_namespace}:{problem_id}:{candidate_id}:{role_key}:extract",
            )
            write_status(
                status_path, state="running", stage=f"{role_key}_bounded_trace_selection"
            )
            selected_packets[role_key] = select_role_trace(
                runtime=runtime,
                role_key=role_key,
                problem=problem,
                proof=proof,
                visible=reviews["visible"][role_key],
                packets=raw_packets[role_key],
                output_dir=role_root / "selection",
                seed_label=f"{seed_namespace}:{problem_id}:{candidate_id}:{role_key}:select",
            )

        write_status(status_path, state="running", stage="dual_trace_aware_fusion")
        fusion_prompt_text = fusion_prompt(
            problem=problem,
            proof=proof,
            reviewer_1=reviews["visible"]["reviewer_1"],
            reviewer_2=reviews["visible"]["reviewer_2"],
            reviewer_3=reviews["visible"]["reviewer_3"],
            r1_packets=selected_packets["reviewer_1"],
            r2_packets=selected_packets["reviewer_2"],
        )
        fusion_dir = destination / "03_dual_trace_fusion"
        fusion_record, fusion_generation = runtime.structured(
            role="gemma",
            prompt=fusion_prompt_text,
            destination=fusion_dir,
            stage="dual_trace_aware_fusion",
            schema=FUSION_SCHEMA,
            temperature=0.1,
            max_tokens=16_384,
            seed_label=f"{seed_namespace}:{problem_id}:{candidate_id}:fusion",
        )
        all_selected = (
            selected_packets["reviewer_1"] + selected_packets["reviewer_2"]
        )
        fusion_dispositions = validate_fusion_dispositions(
            fusion_record, all_selected
        )
        handoff = build_trace_handoff(all_selected, fusion_dispositions)
        (fusion_dir / "fusion_input.txt").write_text(
            fusion_prompt_text, encoding="utf-8"
        )
        write_json(
            fusion_dir / "result.json",
            {
                "fusion": fusion_record,
                "trace_material_handoff": handoff,
                "generation": fusion_generation.get("metadata"),
            },
        )

        write_status(status_path, state="running", stage="deterministic_compact_handoff")
        brief = compact_brief(fusion=fusion_record, handoff=handoff)
        synthesis_prompt = compact_synthesis_prompt(
            problem=problem, proof=proof, brief=brief
        )
        prompt_audit = audit_compact_prompt(synthesis_prompt, brief)
        if not prompt_audit["every_trace_text_appears_exactly_once"]:
            raise ValueError("trace text was lost or duplicated in compact handoff")
        if not prompt_audit["all_forbidden_payload_markers_absent"]:
            raise ValueError("raw record payload leaked into compact handoff")
        compact_dir = destination / "04_deterministic_compact_handoff"
        write_json(compact_dir / "compact_brief.json", brief)
        (compact_dir / "proof_synthesis.prompt.txt").write_text(
            synthesis_prompt, encoding="utf-8"
        )
        write_json(compact_dir / "prompt_audit.json", prompt_audit)

        write_status(status_path, state="running", stage="proof_synthesis")
        generated = runtime.text(
            role="gemma",
            prompt=synthesis_prompt,
            destination=destination / "05_proof_synthesis",
            stage="dual_trace_fusion_proof_synthesis",
            temperature=0.4,
            max_tokens=32_768,
            seed_label=f"{seed_namespace}:{problem_id}:{candidate_id}:synthesis",
        )
        final_proof = str(generated["text"]).strip()
        if not final_proof:
            raise RuntimeError("proof synthesis returned empty text")
        proof_output_path = destination / "05_proof_synthesis" / "proof.md"
        proof_output_path.write_text(final_proof + "\n", encoding="utf-8")
        terminal = {
            "schema": "cognitive-well-v0140-terminal-proof-v1",
            "problem_id": problem_id,
            "candidate_id": candidate_id,
            "proof": final_proof,
            "proof_path": str(proof_output_path.resolve()),
            "proof_sha256": sha256_text(final_proof),
            "generation": generated.get("metadata"),
            "fusion_verdict": fusion_record["verdict"],
            "promotion_allowed_without_independent_audit": False,
        }
        write_json(destination / "06_result.json", terminal)
        summary = {
            "schema": "cognitive-well-v0140-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "input_sha256": input_sha256,
            "problem_id": problem_id,
            "candidate_id": candidate_id,
            "review_outcomes": {
                role: reviews["results"][role].get("parsed", {}).get("outcome")
                or reviews["results"][role].get("outcome")
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "raw_trace_packet_counts": {
                role: len(raw_packets[role]) for role in raw_packets
            },
            "selected_trace_ids": {
                role: [row["trace_id"] for row in selected_packets[role]]
                for role in selected_packets
            },
            "fusion_handoff_trace_ids": [row["trace_id"] for row in handoff],
            "fusion_verdict": fusion_record["verdict"],
            "proof_path": str(proof_output_path.resolve()),
            "promotion_allowed_without_independent_audit": False,
        }
        write_json(summary_path, summary)
        write_status(
            status_path,
            state="completed",
            stage="proof_synthesis",
            fusion_verdict=fusion_record["verdict"],
            proof_path=str(proof_output_path.resolve()),
            promotion_allowed_without_independent_audit=False,
        )
        return summary
    except Exception as error:
        write_status(
            status_path,
            state="failed_closed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise


__all__ = [
    "FUSION_SCHEMA",
    "TRACE_PACKET_SCHEMA",
    "TRACE_SELECTION_SCHEMA",
    "audit_compact_prompt",
    "bind_packets",
    "build_trace_handoff",
    "compact_brief",
    "compact_synthesis_prompt",
    "fusion_prompt",
    "run_pipeline",
    "selector_prompt",
    "validate_fusion_dispositions",
    "validate_selection",
]
