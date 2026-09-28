from __future__ import annotations

import concurrent.futures
import json
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_140_clean_dual_trace_fusion_20260901.pipeline import (
    GEMMA_MODEL,
    QWEN_MODEL,
    assert_no_external_material,
    read_object,
    runtime_for,
    sha256_file,
    sha256_text,
    write_status,
)

from . import HARNESS_VERSION


TRACE_LANES = ("DIAGNOSTIC", "DERIVATION", "REPAIR_ROUTE")
TRACE_VALIDITIES = ("VERIFIED", "PLAUSIBLE", "REFUTED")
REPAIR_COMPLETENESS = ("COMPLETE", "PARTIAL", "NONE")
SELECTOR_DISPOSITIONS = (
    "KEEP",
    "DROP_EQUIVALENT",
    "DROP_IRRELEVANT",
    "DROP_UNSOUND",
)


LANE_SELECTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decisions", "selected_by_lane"],
    "properties": {
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["trace_id", "lane", "disposition", "reason"],
                "properties": {
                    "trace_id": {"type": "string", "minLength": 4},
                    "lane": {"type": "string", "enum": list(TRACE_LANES)},
                    "disposition": {
                        "type": "string",
                        "enum": list(SELECTOR_DISPOSITIONS),
                    },
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
        "selected_by_lane": {
            "type": "object",
            "additionalProperties": False,
            "required": list(TRACE_LANES),
            "properties": {
                lane: {
                    "type": "array",
                    "items": {"type": "string", "minLength": 4},
                }
                for lane in TRACE_LANES
            },
        },
    },
}


TYPED_FUSION_SCHEMA: dict[str, Any] = {
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
        "trace_assessments",
        "route_support",
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
        "trace_assessments": {
            "type": "array",
            "minItems": 0,
            "maxItems": 32,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "trace_id",
                    "validity",
                    "role",
                    "repair_completeness",
                    "reason",
                ],
                "properties": {
                    "trace_id": {"type": "string", "minLength": 4},
                    "validity": {
                        "type": "string",
                        "enum": list(TRACE_VALIDITIES),
                    },
                    "role": {"type": "string", "enum": list(TRACE_LANES)},
                    "repair_completeness": {
                        "type": "string",
                        "enum": list(REPAIR_COMPLETENESS),
                    },
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
        "route_support": {
            "type": "array",
            "minItems": 0,
            "maxItems": 16,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["route_id", "support_ids", "missing_bridge"],
                "properties": {
                    "route_id": {"type": "string", "minLength": 4},
                    "support_ids": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 4},
                    },
                    "missing_bridge": {"type": "string"},
                },
            },
        },
    },
}


ROUTE_COMPLETION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["status", "derivation", "first_unresolved_step"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["COMPLETED", "UNRESOLVED", "REFUTED"],
        },
        "derivation": {"type": "string"},
        "first_unresolved_step": {"type": "string"},
    },
}


def packet_lane(packet: dict[str, Any]) -> str:
    packet_type = str(packet.get("type") or "")
    if packet_type == "REPAIR_ROUTE":
        return "REPAIR_ROUTE"
    if packet_type == "DERIVATION":
        return "DERIVATION"
    if packet_type in {"COUNTEREXAMPLE", "DEFECT"}:
        return "DIAGNOSTIC"
    raise ValueError(f"unsupported trace type: {packet_type}")


def render_lane_packets(packets: list[dict[str, Any]]) -> str:
    if not packets:
        return "(none)"
    blocks = []
    for packet in packets:
        blocks.append(
            "\n".join(
                [
                    f"TRACE_ID: {packet['trace_id']}",
                    f"ASSIGNED_LANE: {packet_lane(packet)}",
                    f"EXTRACTED_TYPE: {packet['type']}",
                    f"TARGET: {packet['target']}",
                    "EXACT_SOURCE_TEXT:",
                    str(packet["exact_source_text"]),
                ]
            )
        )
    return "\n\n".join(blocks)


def lane_selector_prompt(
    *,
    role_label: str,
    problem: str,
    proof: str,
    visible: str,
    packets: list[dict[str, Any]],
) -> str:
    return f"""You are a trace selector for {role_label} on one Olympiad proof.

The visible review is canonical and always retained. The hidden packets below are
unverified supplements. Each packet already has a deterministic lane derived from
its extracted type. Do not compare packets across lanes and do not let strength in
one lane eliminate a packet from another lane.

Within each lane only, retain the smallest nonredundant subset that adds concrete
mathematical information beyond the visible review. Return a decision for every
packet in source order. A retained ID must have disposition KEEP and must remain in
its assigned lane. Use DROP_UNSOUND only for a definite mathematical error, not
merely because a route is unfinished.

The three lanes are:
- DIAGNOSTIC: locates, attacks, or demonstrates a gap.
- DERIVATION: performs an explicit intermediate calculation.
- REPAIR_ROUTE: proposes a constructive route toward closing a gap.

PROBLEM
{problem}

SUBMITTED PROOF
{proof}

VISIBLE {role_label} REVIEW — ALWAYS RETAINED
{visible}

SOURCE-BOUND TRACE PACKETS
{render_lane_packets(packets)}
"""


def validate_lane_selection(
    record: dict[str, Any], packets: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    decisions = [dict(row) for row in record["decisions"]]
    expected_ids = [str(packet["trace_id"]) for packet in packets]
    observed_ids = [str(row["trace_id"]) for row in decisions]
    if observed_ids != expected_ids:
        raise ValueError(f"lane selector trace-ID/order drift: {observed_ids}")
    by_id = {str(packet["trace_id"]): packet for packet in packets}
    decision_by_id = {str(row["trace_id"]): row for row in decisions}
    for decision in decisions:
        expected_lane = packet_lane(by_id[str(decision["trace_id"])])
        if decision["lane"] != expected_lane:
            raise ValueError("lane selector changed a deterministic lane")

    selected_record = record["selected_by_lane"]
    selected: dict[str, list[dict[str, Any]]] = {lane: [] for lane in TRACE_LANES}
    seen: set[str] = set()
    for lane in TRACE_LANES:
        ids = [str(value) for value in selected_record[lane]]
        source_order = [
            trace_id
            for trace_id in expected_ids
            if packet_lane(by_id[trace_id]) == lane and trace_id in ids
        ]
        if source_order != ids or len(ids) != len(set(ids)):
            raise ValueError(f"{lane} selected IDs are unknown, duplicated, or reordered")
        for trace_id in ids:
            if trace_id in seen:
                raise ValueError("a trace was selected into multiple lanes")
            decision = decision_by_id[trace_id]
            if decision["disposition"] != "KEEP":
                raise ValueError("selected trace does not have KEEP disposition")
            selected[lane].append(
                {
                    **by_id[trace_id],
                    "assigned_lane": lane,
                    "lane_selector_decision": decision,
                }
            )
            seen.add(trace_id)
    if {
        str(row["trace_id"])
        for row in decisions
        if row["disposition"] == "KEEP"
    } != seen:
        raise ValueError("KEEP decisions and selected lane IDs disagree")
    return decisions, selected


def typed_fusion_prompt(
    *,
    problem: str,
    proof: str,
    visible: dict[str, str],
    packets: list[dict[str, Any]],
) -> str:
    return f"""You are the independent typed Fusion judge for one Olympiad proof.

Resolve the three visible reviews against the original proof. Hidden trace packets
are UNVERIFIED solver-internal work. Every packet has a preassigned functional role.
Repeat that role exactly and independently assess two different axes:

VALIDITY
- VERIFIED: every substantive displayed claim in the exact span is sound and
  adequately supported by an explicit derivation from the original assumptions.
- PLAUSIBLE: relevant and not refuted, but an asserted relation or required
  derivation remains missing.
- REFUTED: mathematically wrong or misleading.

REPAIR COMPLETENESS
- COMPLETE: the exact span itself explicitly derives the targeted repair bridge
  self-containedly from the original assumptions.
- PARTIAL: it gives concrete progress or a route but leaves any bridge, equation,
  existence condition, or implication unproved.
- NONE: it diagnoses a gap without advancing a repair.

A qualitative statement that parameters "must satisfy a condition," that objects
are "constrained," or that an identity "should follow" is PARTIAL, not COMPLETE.
Do not mark an unfinished REPAIR_ROUTE as VERIFIED merely because its local idea is
reasonable. Return one assessment per supplied trace ID in source order.

Also return one route_support row for every supplied REPAIR_ROUTE, in source order.
support_ids must be the smallest source-ordered list of DERIVATION trace IDs whose
displayed mathematics is both VERIFIED and genuinely needed to use that route.
Exclude derivations that merely repeat mathematics already explicit in the
submitted proof. Do not use diagnostics or another route as support. missing_bridge
must name the first mathematical implication still absent from the route plus its
support; use the empty string only when that material already gives a complete
bridge. A refuted route must have no support IDs.

For REPAIR_NEEDED or INCONCLUSIVE, identify the first decisive obligation and give
a compact repair brief. Any replacement proof must be complete and self-contained
from the original assumptions and may not cite a trace as authority.

PROBLEM
{problem}

SUBMITTED PROOF
{proof}

REVIEWER 1 VISIBLE RECORD
{visible['reviewer_1']}

REVIEWER 2 VISIBLE RECORD
{visible['reviewer_2']}

REVIEWER 3 VISIBLE RECORD
{visible['reviewer_3']}

LANE-PRESERVED TRACE PACKETS
{render_lane_packets(packets)}
"""


def validate_and_canonicalize_assessments(
    record: dict[str, Any], packets: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw = [dict(row) for row in record["trace_assessments"]]
    expected_ids = [str(packet["trace_id"]) for packet in packets]
    observed_ids = [str(row["trace_id"]) for row in raw]
    if observed_ids != expected_ids:
        raise ValueError(f"typed Fusion trace-ID/order drift: {observed_ids}")
    by_id = {str(packet["trace_id"]): packet for packet in packets}
    canonical: list[dict[str, Any]] = []
    for assessment in raw:
        trace_id = str(assessment["trace_id"])
        expected_role = packet_lane(by_id[trace_id])
        row = dict(assessment)
        changes: list[str] = []
        if row["role"] != expected_role:
            row["role"] = expected_role
            changes.append("role_reset_from_source_packet")
        if row["role"] == "DIAGNOSTIC" and row["repair_completeness"] != "NONE":
            row["repair_completeness"] = "NONE"
            changes.append("diagnostic_repair_completeness_forced_to_none")
        if (
            row["role"] == "REPAIR_ROUTE"
            and row["repair_completeness"] != "COMPLETE"
            and row["validity"] == "VERIFIED"
        ):
            row["validity"] = "PLAUSIBLE"
            changes.append("incomplete_repair_route_cannot_be_verified")
        row["deterministic_canonicalization"] = changes
        canonical.append(row)
    return raw, canonical


def validate_route_support(
    record: dict[str, Any],
    packets: list[dict[str, Any]],
    assessments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = [dict(row) for row in record["route_support"]]
    packet_by_id = {str(packet["trace_id"]): packet for packet in packets}
    assessment_by_id = {str(row["trace_id"]): row for row in assessments}
    source_ids = [str(packet["trace_id"]) for packet in packets]
    source_position = {trace_id: index for index, trace_id in enumerate(source_ids)}
    expected_route_ids = [
        trace_id
        for trace_id in source_ids
        if packet_lane(packet_by_id[trace_id]) == "REPAIR_ROUTE"
    ]
    observed_route_ids = [str(row["route_id"]) for row in rows]
    if observed_route_ids != expected_route_ids:
        raise ValueError(
            f"typed Fusion route-support ID/order drift: {observed_route_ids}"
        )

    for row in rows:
        route_id = str(row["route_id"])
        support_ids = [str(value) for value in row["support_ids"]]
        if len(support_ids) != len(set(support_ids)):
            raise ValueError(f"duplicate support IDs for {route_id}")
        if any(value not in packet_by_id for value in support_ids):
            raise ValueError(f"unknown support ID for {route_id}")
        if support_ids != sorted(support_ids, key=source_position.__getitem__):
            raise ValueError(f"support IDs are not in source order for {route_id}")

        route_assessment = assessment_by_id[route_id]
        if route_assessment["validity"] == "REFUTED" and support_ids:
            raise ValueError(f"refuted route {route_id} retained support")
        for support_id in support_ids:
            support_assessment = assessment_by_id[support_id]
            if support_assessment["role"] != "DERIVATION":
                raise ValueError(f"non-derivation support {support_id} for {route_id}")
            if support_assessment["validity"] != "VERIFIED":
                raise ValueError(f"unverified support {support_id} for {route_id}")

        support_texts = [
            str(packet_by_id[support_id]["exact_source_text"]).strip()
            for support_id in support_ids
        ]
        if len(support_texts) != len(set(support_texts)):
            raise ValueError(f"exact-duplicate support retained for {route_id}")

        incomplete = (
            route_assessment["validity"] != "REFUTED"
            and route_assessment["repair_completeness"] != "COMPLETE"
        )
        if incomplete and not str(row["missing_bridge"]).strip():
            raise ValueError(f"partial route {route_id} has no missing bridge")
        row["route_id"] = route_id
        row["support_ids"] = support_ids
        row["missing_bridge"] = str(row["missing_bridge"]).strip()
    return rows


def build_typed_handoff(
    packets: list[dict[str, Any]],
    assessments: list[dict[str, Any]],
    route_support: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {str(row["trace_id"]): row for row in assessments}
    route_support_by_id = {
        str(row["route_id"]): row for row in route_support
    }
    support_for: dict[str, list[str]] = {}
    for row in route_support:
        for support_id in row["support_ids"]:
            support_for.setdefault(str(support_id), []).append(str(row["route_id"]))
    handoff: list[dict[str, Any]] = []
    for packet in packets:
        trace_id = str(packet["trace_id"])
        assessment = by_id[trace_id]
        is_complete_route = (
            assessment["role"] == "REPAIR_ROUTE"
            and assessment["validity"] == "VERIFIED"
            and assessment["repair_completeness"] == "COMPLETE"
        )
        is_verified_support = trace_id in support_for
        if assessment["validity"] == "REFUTED":
            continue
        if assessment["role"] != "REPAIR_ROUTE" and not is_verified_support:
            continue
        if assessment["validity"] == "VERIFIED" and not (
            is_complete_route or is_verified_support
        ):
            continue
        if is_complete_route:
            status = "VERIFIED_COMPLETE_REPAIR"
        elif is_verified_support:
            status = "VERIFIED_ROUTE_SUPPORT"
        elif assessment["role"] == "REPAIR_ROUTE":
            status = "UNVERIFIED_PARTIAL_REPAIR_ROUTE"
        else:
            status = "UNVERIFIED_MATERIAL"
        route_record = route_support_by_id.get(trace_id)
        handoff.append(
            {
                "trace_id": packet["trace_id"],
                "source_role": packet["source_role"],
                "role": assessment["role"],
                "validity": assessment["validity"],
                "repair_completeness": assessment["repair_completeness"],
                "status": status,
                "assessment_reason": assessment["reason"],
                "supports_route_ids": support_for.get(trace_id, []),
                "support_ids": (
                    list(route_record["support_ids"]) if route_record else []
                ),
                "missing_bridge": (
                    str(route_record["missing_bridge"]) if route_record else ""
                ),
                "text": packet["exact_source_text"],
            }
        )
    return handoff


def route_completion_prompt(
    *,
    problem: str,
    proof: str,
    route: dict[str, Any],
    support: list[dict[str, Any]],
) -> str:
    support_text = "\n\n".join(
        f"SUPPORT {row['trace_id']} — VERIFIED LOCAL DERIVATION\n{row['text']}"
        for row in support
    ) or "(none)"
    return f"""Attempt one bounded completion of a missing bridge in an Olympiad proof.

Use only the original problem assumptions and mathematics explicitly rederived in
your response. The submitted proof, route, and support are solver-internal aids,
not authorities. Do not solve a different claim. Do not call a qualitative idea a
completion. Return COMPLETED only if the requested bridge is displayed as an
explicit, self-contained derivation. Otherwise return UNRESOLVED with the first
remaining step, or REFUTED if the proposed route is mathematically invalid.

Use exactly this Markdown transport, with the two control lines first:

STATUS: COMPLETED | UNRESOLVED | REFUTED
FIRST_UNRESOLVED_STEP: NONE | one concise mathematical obligation

DERIVATION:
Only the new bridge calculation; do not restate the surrounding proof.

Do not use a Markdown code fence. No closing marker is required.

ORIGINAL PROBLEM
{problem}

SUBMITTED PROOF CONTEXT
{proof}

PROPOSED ROUTE — UNVERIFIED
{route['text']}

VERIFIED SUPPORT SELECTED FOR THIS ROUTE
{support_text}

MISSING BRIDGE TO DERIVE
{route['missing_bridge']}
"""


def parse_route_completion_markdown(
    value: str,
    *,
    finish_reason: str | None,
    fallback_unresolved_step: str,
) -> dict[str, Any]:
    text = value.strip()
    changes: list[str] = []
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline < 0:
            raise ValueError("route completion contains only a Markdown fence")
        text = text[first_newline + 1 :].lstrip()
        changes.append("leading_markdown_fence_removed")
    if text.endswith("```"):
        text = text[:-3].rstrip()
        changes.append("trailing_markdown_fence_removed")

    lines = text.splitlines()
    if len(lines) < 4 or not lines[0].startswith("STATUS:"):
        raise ValueError("route completion is missing the STATUS header")
    if not lines[1].startswith("FIRST_UNRESOLVED_STEP:"):
        raise ValueError("route completion is missing the unresolved-step header")
    try:
        derivation_index = next(
            index for index, line in enumerate(lines[2:], start=2)
            if line.strip() == "DERIVATION:"
        )
    except StopIteration as error:
        raise ValueError("route completion is missing the DERIVATION header") from error

    status = lines[0].split(":", 1)[1].strip()
    if status not in {"COMPLETED", "UNRESOLVED", "REFUTED"}:
        raise ValueError(f"unsupported route-completion status: {status}")
    unresolved = lines[1].split(":", 1)[1].strip()
    if unresolved.upper() == "NONE":
        unresolved = ""
    derivation = "\n".join(lines[derivation_index + 1 :]).strip()
    if not derivation:
        raise ValueError("route completion has an empty derivation body")

    if finish_reason in {"repetition", "length"}:
        status = "UNRESOLVED"
        unresolved = fallback_unresolved_step.strip()
        changes.append(f"{finish_reason}_truncation_forced_unresolved")
    elif status == "COMPLETED" and unresolved:
        status = "UNRESOLVED"
        changes.append("completed_with_unresolved_step_forced_unresolved")
    elif status in {"UNRESOLVED", "REFUTED"} and not unresolved:
        unresolved = fallback_unresolved_step.strip()
        changes.append("missing_unresolved_step_filled_from_route")

    canonical = validate_route_completion(
        {
            "status": status,
            "derivation": derivation,
            "first_unresolved_step": unresolved,
        }
    )
    canonical["deterministic_canonicalization"] = (
        changes + canonical["deterministic_canonicalization"]
    )
    return canonical


def validate_route_completion(record: dict[str, Any]) -> dict[str, Any]:
    row = dict(record)
    row["derivation"] = str(row["derivation"]).strip()
    row["first_unresolved_step"] = str(row["first_unresolved_step"]).strip()
    changes: list[str] = []
    if row["status"] == "COMPLETED" and (
        len(row["derivation"]) < 80 or row["first_unresolved_step"]
    ):
        row["status"] = "UNRESOLVED"
        if not row["first_unresolved_step"]:
            row["first_unresolved_step"] = (
                "The completion record did not contain a sufficiently explicit "
                "self-contained derivation."
            )
        changes.append("unsupported_completion_downgraded")
    if row["status"] in {"UNRESOLVED", "REFUTED"} and not row[
        "first_unresolved_step"
    ]:
        raise ValueError("non-completed route has no audited stopping point")
    row["deterministic_canonicalization"] = changes
    return row


def canonicalize_truncated_completion_prefix(
    value: str,
    *,
    finish_reason: str | None,
    fallback_unresolved_step: str,
) -> tuple[dict[str, Any], list[str]] | None:
    text = value.strip()
    changes: list[str] = []
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline < 0:
            return None
        text = text[first_newline + 1 :].lstrip()
        changes.append("leading_markdown_fence_removed")
    if text.endswith("```"):
        text = text[:-3].rstrip()
        changes.append("trailing_markdown_fence_removed")
    if '"first_unresolved_step"' in text:
        return None
    if not text.rstrip().endswith('"'):
        return None
    text = text.rstrip() + ', "first_unresolved_step": ""}'
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict) or set(parsed) != {"status", "derivation", "first_unresolved_step"}:
        return None
    if parsed["status"] not in {"COMPLETED", "UNRESOLVED", "REFUTED"}:
        return None
    if not isinstance(parsed["derivation"], str):
        return None
    changes.extend(
        [
            "missing_terminal_field_filled",
            "missing_terminal_object_brace_filled",
        ]
    )
    parsed["status"] = "UNRESOLVED"
    parsed["first_unresolved_step"] = fallback_unresolved_step.strip()
    changes.append("truncated_completion_forced_unresolved")
    if finish_reason in {"repetition", "length"}:
        changes.append(f"{finish_reason}_boundary_recorded")
    return parsed, changes


def recover_same_run_route_completion(
    completion_dir: Path,
    *,
    base_stage: str,
    fallback_unresolved_step: str,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    stems = (
        base_stage,
        f"{base_stage}_compact",
        f"{base_stage}_repair_1",
        f"{base_stage}_repair_2",
        f"{base_stage}_qwen_fallback",
    )
    for stem in stems:
        raw_path = completion_dir / f"{stem}.raw_response.json"
        metadata_path = completion_dir / f"{stem}.metadata.json"
        if not raw_path.is_file() or not metadata_path.is_file():
            continue
        raw = read_object(raw_path)
        metadata = read_object(metadata_path)
        try:
            content = str(raw["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError):
            continue
        recovered = canonicalize_truncated_completion_prefix(
            content,
            finish_reason=str(metadata.get("finish_reason") or "") or None,
            fallback_unresolved_step=fallback_unresolved_step,
        )
        if recovered is None:
            continue
        record, changes = recovered
        canonical = validate_route_completion(record)
        canonical["deterministic_canonicalization"] = (
            changes + canonical["deterministic_canonicalization"]
        )
        return canonical, {
            **metadata,
            "resume_source": str(raw_path),
            "resumed_same_run_artifact": True,
            "v0142_truncated_prefix_recovery": changes,
        }
    return None


def typed_compact_brief(
    *,
    fusion: dict[str, Any],
    handoff: list[dict[str, Any]],
    route_completions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "route_state": (
            "DIRECT_ACCEPT"
            if fusion["verdict"] in {"ACCEPT_AS_WRITTEN", "ACCEPT_WITH_ROUTINE_COMPLETION"}
            else "FUSION_GUIDED_REPAIR"
        ),
        "route_state_is_certification": False,
        "fusion_verdict": fusion["verdict"],
        "failed_obligation": fusion["failed_obligation"],
        "preserve_after_rechecking": fusion["preservable_material"],
        "replacement_chain": [fusion["resolver_brief"]],
        "forbidden_shortcuts": [
            "Do not assert the failed obligation, or an equivalent reformulation, without a complete derivation from the original assumptions.",
            "Do not cite a reviewer, Fusion record, or hidden trace as authority.",
            "A PARTIAL repair route is a search direction, not an established lemma.",
            "Diagnostic evidence cannot serve as a constructive proof bridge.",
        ],
        "trace_material": handoff,
        "route_completions": list(route_completions or []),
    }


def typed_synthesis_prompt(*, problem: str, proof: str, brief: dict[str, Any]) -> str:
    def lane_text(lane: str) -> str:
        rows = [row for row in brief["trace_material"] if row["role"] == lane]
        if not rows:
            return "(none)"
        blocks = []
        for row in rows:
            lines = [
                    f"TRACE {row['trace_id']}",
                    f"VALIDITY: {row['validity']}",
                    f"REPAIR_COMPLETENESS: {row['repair_completeness']}",
                    f"STATUS: {row['status']}",
                    f"ROLE_NOTE: {row['assessment_reason']}",
            ]
            if row.get("supports_route_ids"):
                lines.append(
                    "SUPPORTS_ROUTES: " + ", ".join(row["supports_route_ids"])
                )
            if row.get("support_ids"):
                lines.append("SUPPORT_IDS: " + ", ".join(row["support_ids"]))
            if row.get("missing_bridge"):
                lines.append("MISSING_BRIDGE: " + str(row["missing_bridge"]))
            lines.extend(["EXACT_TEXT:", str(row["text"])])
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)

    def completion_text() -> str:
        rows = brief.get("route_completions") or []
        if not rows:
            return "(none)"
        blocks = []
        for row in rows:
            lines = [
                f"ROUTE {row['route_id']}",
                f"COMPLETION_STATUS: {row['status']}",
            ]
            if row.get("derivation"):
                lines.extend(["UNVERIFIED_COMPLETION_DERIVATION:", row["derivation"]])
            if row.get("first_unresolved_step"):
                lines.append(
                    "FIRST_UNRESOLVED_STEP: " + row["first_unresolved_step"]
                )
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)

    failed = brief["failed_obligation"] or "(none identified)"
    preserve = "\n".join(f"- {value}" for value in brief["preserve_after_rechecking"])
    chain = "\n".join(f"- {value}" for value in brief["replacement_chain"])
    shortcuts = "\n".join(f"- {value}" for value in brief["forbidden_shortcuts"])
    return f"""Write one complete, self-contained Olympiad proof from the original assumptions.

The submitted proof may be reused only after rechecking. The trace lanes are
solver-internal aids, not authorities. A PARTIAL REPAIR_ROUTE must be completed by
an explicit derivation before its conclusion can be used. Diagnostic material only
describes failure and cannot close a proof obligation.

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

DIAGNOSTIC TRACE LANE — NOT A CONSTRUCTIVE BRIDGE
{lane_text('DIAGNOSTIC')}

DERIVATION TRACE LANE
{lane_text('DERIVATION')}

REPAIR ROUTE TRACE LANE — COMPLETE EVERY PARTIAL ROUTE BEFORE USE
{lane_text('REPAIR_ROUTE')}

BOUNDED ROUTE-COMPLETION ATTEMPTS — RECHECK; NEVER CITE AS AUTHORITY
{completion_text()}
"""


def audit_typed_prompt(prompt: str, brief: dict[str, Any]) -> dict[str, Any]:
    counts = {
        str(row["trace_id"]): prompt.count(str(row["text"]))
        for row in brief["trace_material"]
    }
    forbidden = (
        "source_artifact_path",
        "exact_source_sha256",
        "codex_grade",
        "gold_solution",
    )
    return {
        "trace_text_occurrence_counts": counts,
        "every_trace_text_appears_exactly_once": all(
            count == 1 for count in counts.values()
        ),
        "forbidden_payload_marker_hits": {
            marker: marker in prompt for marker in forbidden
        },
        "all_forbidden_payload_markers_absent": not any(
            marker in prompt for marker in forbidden
        ),
    }


def load_source(source_run: Path) -> dict[str, Any]:
    source = source_run.resolve()
    summary = read_object(source / "summary.json")
    if summary.get("state") != "completed":
        raise ValueError("source run is not completed")
    manifest = read_object(source / "manifest.json")
    contract = manifest.get("source")
    if not isinstance(contract, dict):
        raise ValueError("source manifest has no source contract")
    problem_path = Path(str(contract["problem_json"])).resolve()
    candidate_path = Path(str(contract["candidate_result"])).resolve()
    if sha256_file(problem_path) != contract.get("problem_json_sha256"):
        raise ValueError("problem source drift")
    if sha256_file(candidate_path) != contract.get("candidate_result_sha256"):
        raise ValueError("candidate source drift")
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
    reviews = read_object(source / "01_reviews" / "summary.json")
    visible = reviews.get("visible")
    if not isinstance(visible, dict):
        raise ValueError("source visible reviews are absent")
    packet_roles = ["reviewer_1", "reviewer_2"]
    reviewer_3_packets = (
        source
        / "02_trace_harvest"
        / "reviewer_3"
        / "extraction"
        / "bound_packets.json"
    )
    if reviewer_3_packets.is_file():
        packet_roles.append("reviewer_3")
    packets = {
        role: read_object(
            source
            / "02_trace_harvest"
            / role
            / "extraction"
            / "bound_packets.json"
        )["packets"]
        for role in packet_roles
    }
    return {
        "source": source,
        "contract": contract,
        "problem_id": problem_id,
        "problem": problem,
        "candidate_id": candidate_id,
        "proof": proof,
        "visible": {role: str(visible[role]) for role in visible},
        "packets": packets,
    }


def load_same_run_fusion_record(
    fusion_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    accepted_path = fusion_dir / "accepted_record.json"
    if accepted_path.is_file():
        return read_object(accepted_path), {
            "resume_source": str(accepted_path),
            "resumed_same_run_artifact": True,
        }
    stems = (
        "typed_trace_fusion_qwen_fallback",
        "typed_trace_fusion_repair_2",
        "typed_trace_fusion_repair_1",
        "typed_trace_fusion_compact",
        "typed_trace_fusion",
    )
    required = set(TYPED_FUSION_SCHEMA["required"])
    for stem in stems:
        raw_path = fusion_dir / f"{stem}.raw_response.json"
        if not raw_path.is_file():
            continue
        raw = read_object(raw_path)
        try:
            content = raw["choices"][0]["message"]["content"]
            record = json.loads(str(content))
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict) or not required.issubset(record):
            continue
        metadata_path = fusion_dir / f"{stem}.metadata.json"
        metadata = read_object(metadata_path) if metadata_path.is_file() else {}
        write_json(accepted_path, record)
        return record, {
            **metadata,
            "resume_source": str(raw_path),
            "resumed_same_run_artifact": True,
        }
    return None


def run(*, source_run: Path, output_dir: Path) -> dict[str, Any]:
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    status_path = destination / "status.json"
    try:
        source = load_source(source_run)
        contract = source["contract"]
        master_seed = int(contract["master_seed"])
        seed_namespace = f"{contract['seed_namespace']}:v0142"
        runtime = runtime_for(
            gemma_endpoint=str(contract["gemma_endpoint"]),
            qwen_endpoint=str(contract["qwen_endpoint"]),
            master_seed=master_seed,
        )
        # Route completion uses an intentionally non-structured transport.  The
        # fixed leading headers can be parsed even when the derivation body is
        # cut short, while a non-natural stop is still forced to UNRESOLVED.
        completion_runtime = ModelRuntime(runtime.config)
        write_json(
            destination / "manifest.json",
            {
                "schema": "cognitive-well-v0142-support-aware-handoff-manifest-v1",
                "harness_version": HARNESS_VERSION,
                "created_at": utc_now(),
                "source_run": str(source["source"]),
                "source_manifest_sha256": sha256_file(
                    source["source"] / "manifest.json"
                ),
                "problem_id": source["problem_id"],
                "candidate_id": source["candidate_id"],
                "models": {
                    "lane_selector": QWEN_MODEL,
                    "typed_fusion": GEMMA_MODEL,
                    "route_completion": GEMMA_MODEL,
                    "proof_synthesis": GEMMA_MODEL,
                },
                "policy": {
                    "selector_passes": 1,
                    "cross_lane_elimination": False,
                    "trace_axes": ["validity", "role", "repair_completeness"],
                    "partial_repair_route_can_be_verified": False,
                    "verified_packets_in_synthesis_handoff": "route_support_only",
                    "standalone_diagnostics_in_synthesis_handoff": False,
                    "standalone_plausible_derivations_in_synthesis_handoff": False,
                    "route_support_requires_verified_derivation": True,
                    "partial_route_requires_missing_bridge": True,
                    "bounded_route_completion_enabled": True,
                    "route_completion_transport": "fixed_header_markdown",
                    "route_completion_retries": 0,
                    "non_natural_completion_forced_unresolved": True,
                    "closure_auditor_enabled": False,
                },
                "external_information_injection": False,
                "cross_problem_information_injection": False,
                "codex_grades_supplied": False,
                "handcrafted_problem_specific_guidance": False,
            },
        )
        write_json(
            destination / "leak_audit.json",
            {
                "state": "passed",
                "solver_inputs_are_current_problem_local": True,
                "source_reviews_and_traces_are_solver_internal": True,
                "gold_supplied": False,
                "codex_grades_supplied": False,
                "external_scorer_feedback_supplied": False,
                "cross_problem_information_supplied": False,
                "handcrafted_problem_specific_prompt_guidance": False,
            },
        )

        write_status(status_path, state="running", stage="lane_preserving_selection")

        def select(role: str) -> dict[str, Any]:
            selection_dir = destination / "02_lane_selection" / role
            result_path = selection_dir / "result.json"
            if result_path.is_file():
                existing = read_object(result_path)
                replay_record = {
                    "decisions": existing["decisions"],
                    "selected_by_lane": existing["selected_trace_ids_by_lane"],
                }
                decisions, selected = validate_lane_selection(
                    replay_record, source["packets"][role]
                )
                return {
                    "decisions": decisions,
                    "selected": selected,
                    "resumed_same_run_artifact": True,
                }
            role_label = "REVIEWER 1" if role == "reviewer_1" else "REVIEWER 2"
            prompt = lane_selector_prompt(
                role_label=role_label,
                problem=source["problem"],
                proof=source["proof"],
                visible=source["visible"][role],
                packets=source["packets"][role],
            )
            record, generation = runtime.structured(
                role="qwen",
                prompt=prompt,
                destination=selection_dir,
                stage=f"{role}_lane_selection",
                schema=LANE_SELECTION_SCHEMA,
                temperature=0.1,
                max_tokens=16_384,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:{role}:lane-select"
                ),
            )
            decisions, selected = validate_lane_selection(
                record, source["packets"][role]
            )
            write_json(
                result_path,
                {
                    "decisions": decisions,
                    "selected_trace_ids_by_lane": {
                        lane: [packet["trace_id"] for packet in packets]
                        for lane, packets in selected.items()
                    },
                    "selected_packets_by_lane": selected,
                    "generation": generation.get("metadata"),
                },
            )
            return {
                "decisions": decisions,
                "selected": selected,
                "resumed_same_run_artifact": False,
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                role: executor.submit(select, role)
                for role in ("reviewer_1", "reviewer_2")
            }
            selections = {role: future.result() for role, future in futures.items()}

        selected_packets: list[dict[str, Any]] = []
        for lane in TRACE_LANES:
            for role in ("reviewer_1", "reviewer_2"):
                selected_packets.extend(selections[role]["selected"][lane])

        write_status(status_path, state="running", stage="typed_fusion")
        prompt = typed_fusion_prompt(
            problem=source["problem"],
            proof=source["proof"],
            visible=source["visible"],
            packets=selected_packets,
        )
        fusion_dir = destination / "03_typed_fusion"
        resumed_fusion = load_same_run_fusion_record(fusion_dir)
        if resumed_fusion is None:
            fusion, generation = runtime.structured(
                role="gemma",
                prompt=prompt,
                destination=fusion_dir,
                stage="typed_trace_fusion",
                schema=TYPED_FUSION_SCHEMA,
                temperature=0.1,
                max_tokens=18_432,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:typed-fusion"
                ),
            )
            write_json(fusion_dir / "accepted_record.json", fusion)
        else:
            fusion, resumed_metadata = resumed_fusion
            generation = {"metadata": resumed_metadata}
        raw_assessments, assessments = validate_and_canonicalize_assessments(
            fusion, selected_packets
        )
        route_support = validate_route_support(
            fusion, selected_packets, assessments
        )
        handoff = build_typed_handoff(
            selected_packets, assessments, route_support
        )
        (fusion_dir / "fusion_input.txt").write_text(prompt, encoding="utf-8")
        write_json(
            fusion_dir / "result.json",
            {
                "fusion": fusion,
                "raw_trace_assessments": raw_assessments,
                "canonical_trace_assessments": assessments,
                "route_support": route_support,
                "typed_trace_handoff": handoff,
                "generation": generation.get("metadata"),
            },
        )

        write_status(status_path, state="running", stage="route_completion")
        handoff_by_id = {str(row["trace_id"]): row for row in handoff}
        partial_routes = [
            row
            for row in handoff
            if row["role"] == "REPAIR_ROUTE"
            and row["repair_completeness"] != "COMPLETE"
            and row["missing_bridge"]
        ]

        def complete_route(route: dict[str, Any]) -> dict[str, Any]:
            support = [
                handoff_by_id[support_id]
                for support_id in route["support_ids"]
            ]
            completion_prompt = route_completion_prompt(
                problem=source["problem"],
                proof=source["proof"],
                route=route,
                support=support,
            )
            completion_dir = (
                destination
                / "04_route_completion_markdown"
                / str(route["trace_id"])
            )
            result_path = completion_dir / "result.json"
            if result_path.is_file():
                return read_object(result_path)
            base_stage = f"{route['trace_id']}_route_completion_markdown"
            completion_generation = completion_runtime.text(
                role="gemma",
                prompt=completion_prompt,
                destination=completion_dir,
                stage=base_stage,
                temperature=0.1,
                max_tokens=16_384,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:{route['trace_id']}:"
                    "route-completion-markdown"
                ),
                user_prompt="Return the fixed-header Markdown record now.",
            )
            completion_metadata = dict(
                completion_generation.get("metadata") or {}
            )
            canonical = parse_route_completion_markdown(
                str(completion_generation.get("text") or ""),
                finish_reason=(
                    str(completion_metadata.get("finish_reason"))
                    if completion_metadata.get("finish_reason") is not None
                    else None
                ),
                fallback_unresolved_step=str(route["missing_bridge"]),
            )
            result = {
                "route_id": str(route["trace_id"]),
                "support_ids": list(route["support_ids"]),
                "missing_bridge": str(route["missing_bridge"]),
                **canonical,
                "generation": completion_generation.get("metadata"),
            }
            write_json(result_path, result)
            return result

        route_completions: list[dict[str, Any]] = []
        if partial_routes:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(2, len(partial_routes))
            ) as executor:
                completion_futures = [
                    executor.submit(complete_route, route)
                    for route in partial_routes
                ]
                route_completions = [
                    future.result() for future in completion_futures
                ]

        write_status(status_path, state="running", stage="typed_compaction")
        brief = typed_compact_brief(
            fusion=fusion,
            handoff=handoff,
            route_completions=route_completions,
        )
        synthesis_prompt = typed_synthesis_prompt(
            problem=source["problem"], proof=source["proof"], brief=brief
        )
        audit = audit_typed_prompt(synthesis_prompt, brief)
        if not audit["every_trace_text_appears_exactly_once"]:
            raise ValueError("typed trace text was lost or duplicated")
        if not audit["all_forbidden_payload_markers_absent"]:
            raise ValueError("forbidden payload marker leaked into typed prompt")
        compact_dir = destination / "05_typed_compact_handoff"
        write_json(compact_dir / "compact_brief.json", brief)
        write_json(compact_dir / "prompt_audit.json", audit)
        (compact_dir / "proof_synthesis.prompt.txt").write_text(
            synthesis_prompt, encoding="utf-8"
        )

        completed_route_ids = [
            row["route_id"]
            for row in route_completions
            if row["status"] == "COMPLETED"
        ]
        if partial_routes and not completed_route_ids:
            summary = {
                "schema": "cognitive-well-v0142-summary-v1",
                "harness_version": HARNESS_VERSION,
                "state": "completed",
                "outcome": "UNRESOLVED_ROUTE_COMPLETION",
                "completed_at": utc_now(),
                "problem_id": source["problem_id"],
                "candidate_id": source["candidate_id"],
                "selected_trace_ids_by_lane": {
                    role: {
                        lane: [
                            packet["trace_id"]
                            for packet in selections[role]["selected"][lane]
                        ]
                        for lane in TRACE_LANES
                    }
                    for role in ("reviewer_1", "reviewer_2")
                },
                "canonical_trace_assessments": assessments,
                "route_support": route_support,
                "handoff_trace_ids": [row["trace_id"] for row in handoff],
                "route_completions": route_completions,
                "fusion_verdict": fusion["verdict"],
                "proof_path": None,
                "promotion_allowed_without_independent_audit": False,
            }
            write_json(destination / "summary.json", summary)
            write_status(
                status_path,
                state="completed",
                stage="route_completion",
                outcome="UNRESOLVED_ROUTE_COMPLETION",
                promotion_allowed_without_independent_audit=False,
            )
            return summary

        write_status(status_path, state="running", stage="proof_synthesis")
        generated = runtime.text(
            role="gemma",
            prompt=synthesis_prompt,
            destination=destination / "06_proof_synthesis",
            stage="typed_trace_proof_synthesis",
            temperature=0.4,
            max_tokens=32_768,
            seed_label=(
                f"{seed_namespace}:{source['problem_id']}:"
                f"{source['candidate_id']}:synthesis"
            ),
        )
        proof_text = str(generated["text"]).strip()
        if not proof_text:
            raise RuntimeError("typed trace proof synthesis returned empty text")
        proof_path = destination / "06_proof_synthesis" / "proof.md"
        proof_path.write_text(proof_text + "\n", encoding="utf-8")
        write_json(
            destination / "07_result.json",
            {
                "schema": "cognitive-well-v0142-terminal-proof-v1",
                "problem_id": source["problem_id"],
                "candidate_id": source["candidate_id"],
                "proof": proof_text,
                "proof_path": str(proof_path),
                "proof_sha256": sha256_text(proof_text),
                "generation": generated.get("metadata"),
                "fusion_verdict": fusion["verdict"],
                "promotion_allowed_without_independent_audit": False,
            },
        )
        summary = {
            "schema": "cognitive-well-v0142-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": "PROOF_SYNTHESIZED",
            "completed_at": utc_now(),
            "problem_id": source["problem_id"],
            "candidate_id": source["candidate_id"],
            "selected_trace_ids_by_lane": {
                role: {
                    lane: [
                        packet["trace_id"]
                        for packet in selections[role]["selected"][lane]
                    ]
                    for lane in TRACE_LANES
                }
                for role in ("reviewer_1", "reviewer_2")
            },
            "canonical_trace_assessments": assessments,
            "route_support": route_support,
            "handoff_trace_ids": [row["trace_id"] for row in handoff],
            "route_completions": route_completions,
            "fusion_verdict": fusion["verdict"],
            "proof_path": str(proof_path),
            "promotion_allowed_without_independent_audit": False,
        }
        write_json(destination / "summary.json", summary)
        write_status(
            status_path,
            state="completed",
            stage="proof_synthesis",
            fusion_verdict=fusion["verdict"],
            proof_path=str(proof_path),
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
    "LANE_SELECTION_SCHEMA",
    "ROUTE_COMPLETION_SCHEMA",
    "TYPED_FUSION_SCHEMA",
    "audit_typed_prompt",
    "build_typed_handoff",
    "canonicalize_truncated_completion_prefix",
    "lane_selector_prompt",
    "load_same_run_fusion_record",
    "packet_lane",
    "parse_route_completion_markdown",
    "route_completion_prompt",
    "recover_same_run_route_completion",
    "run",
    "typed_compact_brief",
    "typed_fusion_prompt",
    "typed_synthesis_prompt",
    "validate_and_canonicalize_assessments",
    "validate_lane_selection",
    "validate_route_completion",
    "validate_route_support",
]
