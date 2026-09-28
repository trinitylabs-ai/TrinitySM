from __future__ import annotations

import concurrent.futures
import re
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    validate_schema,
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
from cognitive_well_harness_v0_3_142_support_aware_trace_handoff_20260901.pipeline import (
    TRACE_LANES,
    load_source,
    packet_lane,
)

from . import HARNESS_VERSION


def trace_id_occurrence_count(text: str, trace_id: str) -> int:
    """Count a transport trace ID as a complete token, never as an ID prefix."""
    pattern = rf"(?<![A-Za-z0-9_]){re.escape(trace_id)}(?![A-Za-z0-9_])"
    return len(re.findall(pattern, text))


def contains_trace_id(text: str, trace_id: str) -> bool:
    return trace_id_occurrence_count(text, trace_id) > 0


VISIBLE_FUSION_SCHEMA: dict[str, Any] = {
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
    },
}


TRACE_DEDUP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "duplicate_groups",
        "proof_redundant_ids",
        "selected_trace_ids",
    ],
    "properties": {
        "duplicate_groups": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["representative_id", "duplicate_ids"],
                "properties": {
                    "representative_id": {"type": "string", "minLength": 4},
                    "duplicate_ids": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 4},
                    },
                },
            },
        },
        "selected_trace_ids": {
            "type": "array",
            "items": {"type": "string", "minLength": 4},
        },
        "proof_redundant_ids": {
            "type": "array",
            "items": {"type": "string", "minLength": 4},
        },
    },
}


def public_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": str(packet["trace_id"]),
        "source_role": str(packet["source_role"]),
        "lane": packet_lane(packet),
        "type": str(packet["type"]),
        "target": str(packet["target"]),
        "text": str(packet["exact_source_text"]),
        "content_transformations": [],
        "verification_status": "UNVERIFIED_TRACING_MEMORY",
    }


def visible_fusion_prompt(
    *, problem: str, proof: str, visible: dict[str, str]
) -> str:
    return f"""You are the independent visible-review Fusion judge for one Olympiad proof.

Resolve the three visible reviews against the original submitted proof. You receive
no hidden reasoning traces, tracing memory, external assessment, or certified
lemma. Independently recheck every material claim. For REPAIR_NEEDED or
INCONCLUSIVE, identify the first decisive obligation and provide a compact repair
brief. Any replacement proof must be complete and self-contained from the original
assumptions.

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
"""


VISIBLE_FUSION_MARKDOWN_SECTIONS = (
    "DECISIVE_LOCATION",
    "FAILED_OBLIGATION",
    "IMPACT_ON_PROOF",
    "RESOLVER_BRIEF",
    "PRESERVABLE_MATERIAL",
    "REVIEWER_1_ASSESSMENT",
    "REVIEWER_2_ASSESSMENT",
    "REVIEWER_3_ASSESSMENT",
    "INDEPENDENT_VALIDATION",
)


def visible_fusion_markdown_prompt(
    *, problem: str, proof: str, visible: dict[str, str]
) -> str:
    return f"""You are the independent visible-review Fusion judge for one Olympiad proof.

Resolve the three visible reviews against the original submitted proof. You receive
no hidden reasoning traces, tracing memory, external assessment, or certified
lemma. Independently recheck every material claim. For REPAIR_NEEDED or
INCONCLUSIVE, identify the first decisive obligation and provide a compact repair
brief. Any replacement proof must be complete and self-contained from the original
assumptions.

Return exactly the following fixed-header Markdown record. Put the two control
lines first. Keep every section header on its own line and in the displayed order.
Use one or more `- ` bullets under PRESERVABLE_MATERIAL, or `(none)`. Do not use a
Markdown code fence. No closing marker is required.

VERDICT: ACCEPT_AS_WRITTEN | ACCEPT_WITH_ROUTINE_COMPLETION | REPAIR_NEEDED | INCONCLUSIVE
REPAIR_SCOPE: LOCAL | STRUCTURAL
DECISIVE_LOCATION:
text
FAILED_OBLIGATION:
text
IMPACT_ON_PROOF:
text
RESOLVER_BRIEF:
text
PRESERVABLE_MATERIAL:
- item
REVIEWER_1_ASSESSMENT:
text
REVIEWER_2_ASSESSMENT:
text
REVIEWER_3_ASSESSMENT:
text
INDEPENDENT_VALIDATION:
text

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
"""


def parse_visible_fusion_markdown(
    value: str, *, finish_reason: str | None
) -> dict[str, Any]:
    if finish_reason != "stop":
        raise ValueError(
            "visible Fusion Markdown requires natural stop; "
            f"observed {finish_reason or 'unknown'}"
        )
    text = value.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline < 0:
            raise ValueError("visible Fusion contains only a Markdown fence")
        text = text[first_newline + 1 :].lstrip()
    if text.endswith("```"):
        text = text[:-3].rstrip()
    # Fixed-header Markdown is a transport, not mathematical content.  Models
    # occasionally emit ``HEADER: value`` instead of putting ``value`` on the
    # following line, or decorate a header with Markdown heading/bold syntax.
    # Canonicalize only recognized headers and preserve the attached value
    # verbatim.  Unknown, missing, duplicated, or reordered sections still fail
    # closed in the ordered-section parser below.
    recognized_headers = (
        "VERDICT",
        "REPAIR_SCOPE",
        *VISIBLE_FUSION_MARKDOWN_SECTIONS,
    )
    header_pattern = re.compile(
        r"^(?:#{1,6}\s+)?(?:\*\*)?("
        + "|".join(re.escape(header) for header in recognized_headers)
        + r")(?:\*\*\s*:|:\s*\*\*|:)\s*(.*)$"
    )
    lines: list[str] = []
    for original_line in text.splitlines():
        stripped = original_line.strip()
        match = header_pattern.fullmatch(stripped)
        if match is None:
            lines.append(original_line)
            continue
        header, attached_value = match.groups()
        if header in {"VERDICT", "REPAIR_SCOPE"}:
            lines.append(f"{header}: {attached_value}".rstrip())
            continue
        lines.append(f"{header}:")
        if attached_value:
            lines.append(attached_value)
    if len(lines) < 4 or not lines[0].startswith("VERDICT:"):
        raise ValueError("visible Fusion is missing the VERDICT control line")
    if not lines[1].startswith("REPAIR_SCOPE:"):
        raise ValueError("visible Fusion is missing the REPAIR_SCOPE control line")
    verdict = lines[0].split(":", 1)[1].strip()
    repair_scope = lines[1].split(":", 1)[1].strip()

    positions: dict[str, int] = {}
    cursor = 2
    for section in VISIBLE_FUSION_MARKDOWN_SECTIONS:
        marker = f"{section}:"
        try:
            position = next(
                index
                for index in range(cursor, len(lines))
                if lines[index].strip() == marker
            )
        except StopIteration as error:
            raise ValueError(
                f"visible Fusion is missing ordered section {section}"
            ) from error
        positions[section] = position
        cursor = position + 1

    section_values: dict[str, str] = {}
    for index, section in enumerate(VISIBLE_FUSION_MARKDOWN_SECTIONS):
        start = positions[section] + 1
        end = (
            positions[VISIBLE_FUSION_MARKDOWN_SECTIONS[index + 1]]
            if index + 1 < len(VISIBLE_FUSION_MARKDOWN_SECTIONS)
            else len(lines)
        )
        section_values[section] = "\n".join(lines[start:end]).strip()

    preservable_text = section_values["PRESERVABLE_MATERIAL"]
    if preservable_text == "(none)":
        preservable: list[str] = []
    else:
        preservable_lines = [
            line.strip() for line in preservable_text.splitlines() if line.strip()
        ]
        if not preservable_lines or any(
            not line.startswith("- ") or not line[2:].strip()
            for line in preservable_lines
        ):
            raise ValueError("PRESERVABLE_MATERIAL must contain bullets or (none)")
        preservable = [line[2:].strip() for line in preservable_lines]

    record = {
        "verdict": verdict,
        "reviewer_1_assessment": section_values["REVIEWER_1_ASSESSMENT"],
        "reviewer_2_assessment": section_values["REVIEWER_2_ASSESSMENT"],
        "reviewer_3_assessment": section_values["REVIEWER_3_ASSESSMENT"],
        "decisive_location": section_values["DECISIVE_LOCATION"],
        "failed_obligation": section_values["FAILED_OBLIGATION"],
        "independent_validation": section_values["INDEPENDENT_VALIDATION"],
        "impact_on_proof": section_values["IMPACT_ON_PROOF"],
        "repair_scope": repair_scope,
        "resolver_brief": section_values["RESOLVER_BRIEF"],
        "preservable_material": preservable,
    }
    validate_schema(record, VISIBLE_FUSION_SCHEMA)
    return record


def render_memory_packets(packets: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        "\n".join(
            [
                f"TRACE_ID: {packet['trace_id']}",
                f"SOURCE_ROLE: {packet['source_role']}",
                f"LANE: {packet_lane(packet)}",
                f"EXTRACTED_TYPE: {packet['type']}",
                f"TARGET: {packet['target']}",
                "EXACT_SOURCE_TEXT:",
                str(packet["exact_source_text"]),
            ]
        )
        for packet in packets
    ) or "(none)"


def tracing_memory_selector_prompt(
    *, problem: str, proof: str, lane: str, packets: list[dict[str, Any]]
) -> str:
    return f"""Deduplicate one lane of an unverified, solver-internal tracing memory.

Only two removal operations are allowed:
1. Put a packet in proof_redundant_ids when its entire mathematical contribution is
   already explicit in the submitted proof. This includes a diagnosis that merely
   repeats or points at an assertion or transition already visible in the proof and
   adds no new counterexample, precise defect, derivation, equation, or constraint.
2. Merge remaining packets only when they make the same mathematical contribution
   in the same functional role, allowing notation-level paraphrase.

Apply proof redundancy before trace-to-trace deduplication. Do not otherwise judge
correctness, importance, relevance, completeness, or usefulness. A wrong,
abandoned, or incomplete argument must survive if it is mathematically distinct
from the submitted proof and the other packets. Related, compatible, or sequential
steps are not duplicates.

For each duplicate group, choose its earliest packet in the supplied source order
as representative_id. Put every later equivalent packet in duplicate_ids. Every
source packet must occur exactly once: in proof_redundant_ids, in
selected_trace_ids, or as a duplicate_id. Both ID arrays must be in source order.
Do not rewrite packet text.

PROBLEM
{problem}

SUBMITTED PROOF
{proof}

TRACING-MEMORY LANE: {lane}
{render_memory_packets(packets)}
"""


def canonicalize_trace_dedup_record(
    record: dict[str, Any], packets: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[str]]:
    """Canonicalize transport-only duplicate-group defects before validation."""

    expected_ids = [str(packet["trace_id"]) for packet in packets]
    expected = set(expected_ids)
    selected_ids = [str(value) for value in record["selected_trace_ids"]]
    proof_redundant_ids = [
        str(value) for value in record["proof_redundant_ids"]
    ]
    redundant = set(proof_redundant_ids)
    retained_groups: list[dict[str, Any]] = []
    changes: list[str] = []
    for raw_group in record["duplicate_groups"]:
        representative = str(raw_group["representative_id"])
        raw_duplicate_ids = [str(value) for value in raw_group["duplicate_ids"]]
        duplicate_ids = list(dict.fromkeys(raw_duplicate_ids))
        if duplicate_ids != raw_duplicate_ids:
            changes.append("repeated_duplicate_id_collapsed:" + representative)
        if not duplicate_ids and representative in selected_ids:
            changes.append("empty_duplicate_group_removed:" + representative)
            continue
        if (
            representative in redundant
            and representative not in selected_ids
            and all(trace_id in expected for trace_id in duplicate_ids)
            and not (set(duplicate_ids) & set(selected_ids))
        ):
            redundant.update(duplicate_ids)
            changes.append(
                "proof_redundant_representative_group_collapsed:"
                + representative
            )
            continue
        retained_groups.append(
            {
                "representative_id": representative,
                "duplicate_ids": duplicate_ids,
            }
        )
    canonical = {
        **record,
        "duplicate_groups": retained_groups,
        "proof_redundant_ids": [
            trace_id for trace_id in expected_ids if trace_id in redundant
        ],
        "selected_trace_ids": selected_ids,
    }
    return canonical, changes


def validate_trace_dedup(
    record: dict[str, Any], packets: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    expected_ids = [str(packet["trace_id"]) for packet in packets]
    index = {trace_id: offset for offset, trace_id in enumerate(expected_ids)}
    selected_ids = [str(value) for value in record["selected_trace_ids"]]
    if selected_ids != [trace_id for trace_id in expected_ids if trace_id in selected_ids]:
        raise ValueError("trace-memory selected IDs are unknown, duplicated, or reordered")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("trace-memory selected IDs contain duplicates")
    proof_redundant_ids = [
        str(value) for value in record["proof_redundant_ids"]
    ]
    if proof_redundant_ids != [
        trace_id for trace_id in expected_ids if trace_id in proof_redundant_ids
    ]:
        raise ValueError("proof-redundant trace IDs are unknown or reordered")
    if len(proof_redundant_ids) != len(set(proof_redundant_ids)):
        raise ValueError("proof-redundant trace IDs contain duplicates")
    if set(selected_ids) & set(proof_redundant_ids):
        raise ValueError("a proof-redundant trace was also selected")

    normalized_groups: list[dict[str, Any]] = []
    duplicate_owner: dict[str, str] = {}
    prior_representative_index = -1
    for raw_group in record["duplicate_groups"]:
        representative = str(raw_group["representative_id"])
        duplicate_ids = [str(value) for value in raw_group["duplicate_ids"]]
        if representative not in index or representative not in selected_ids:
            raise ValueError("duplicate representative is not a selected source ID")
        if not duplicate_ids or len(duplicate_ids) != len(set(duplicate_ids)):
            raise ValueError("duplicate group must contain unique duplicate IDs")
        if index[representative] <= prior_representative_index:
            raise ValueError("duplicate groups are not in representative source order")
        prior_representative_index = index[representative]
        if duplicate_ids != [
            trace_id for trace_id in expected_ids if trace_id in duplicate_ids
        ]:
            raise ValueError("duplicate IDs are unknown or reordered")
        for duplicate_id in duplicate_ids:
            if duplicate_id in selected_ids:
                raise ValueError("a duplicate ID was also selected")
            if duplicate_id in proof_redundant_ids:
                raise ValueError("a duplicate ID was also proof-redundant")
            if index[duplicate_id] <= index[representative]:
                raise ValueError("representative is not the earliest group member")
            if duplicate_id in duplicate_owner:
                raise ValueError("a trace belongs to multiple duplicate groups")
            duplicate_owner[duplicate_id] = representative
        normalized_groups.append(
            {
                "representative_id": representative,
                "duplicate_ids": duplicate_ids,
            }
        )

    if (
        set(selected_ids)
        | set(proof_redundant_ids)
        | set(duplicate_owner)
        != set(expected_ids)
    ):
        raise ValueError("trace-memory dedup omitted a source packet")
    if (
        set(selected_ids) & set(duplicate_owner)
        or set(proof_redundant_ids) & set(duplicate_owner)
    ):
        raise ValueError("trace-memory dedup coverage overlaps")

    by_id = {str(packet["trace_id"]): packet for packet in packets}
    group_by_representative = {
        row["representative_id"]: row["duplicate_ids"] for row in normalized_groups
    }
    selected = [
        {
            **public_packet(by_id[trace_id]),
            "duplicate_ids_removed": group_by_representative.get(trace_id, []),
        }
        for trace_id in selected_ids
    ]
    return normalized_groups, proof_redundant_ids, selected


def build_separate_handoff(
    *, fusion: dict[str, Any], selected_memory: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "fusion_channel": {
            "source": "VISIBLE_REVIEWS_ONLY",
            "verdict": str(fusion["verdict"]),
            "failed_obligation": str(fusion["failed_obligation"]),
            "preserve_after_rechecking": list(fusion["preservable_material"]),
            "resolver_brief": str(fusion["resolver_brief"]),
            "independent_validation": str(fusion["independent_validation"]),
        },
        "tracing_memory_channel": {
            "source": "HIDDEN_TRACES_PROOF_REDUNDANCY_FILTERED_AND_DEDUPLICATED",
            "fusion_saw_this_channel": False,
            "selector_operations": [
                "REMOVE_CONTENT_ALREADY_EXPLICIT_IN_SUBMITTED_PROOF",
                "EXACT_OR_SEMANTIC_TRACE_DEDUPLICATION",
            ],
            "verification_status": "UNVERIFIED",
            "entries": selected_memory,
        },
    }


def render_selected_memory(entries: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for lane in TRACE_LANES:
        lane_entries = [entry for entry in entries if entry["lane"] == lane]
        lane_body = "\n\n".join(
            "\n".join(
                [
                    (
                        '<a id="trace-'
                        + re.sub(
                            r"[^a-z0-9-]+",
                            "-",
                            str(entry["trace_id"]).lower(),
                        ).strip("-")
                        + '"></a>'
                    ),
                    f"TRACE {entry['trace_id']} FROM {entry['source_role']}",
                    f"TYPE: {entry['type']}",
                    f"TARGET: {entry['target']}",
                    "UNVERIFIED EXACT TEXT:",
                    str(entry["text"]),
                ]
            )
            for entry in lane_entries
        ) or "(none)"
        blocks.append(f"{lane} MEMORY\n{lane_body}")
    return "\n\n".join(blocks)


def _attention_anchor(proof: str, decisive_location: str) -> tuple[int, str, str]:
    decisive = decisive_location.strip()
    if decisive and decisive in proof:
        end = proof.index(decisive) + len(decisive)
        return end, decisive, "exact_fusion_decisive_location"

    query_tokens = set(re.findall(r"[A-Za-z0-9]+", decisive.lower()))
    best: tuple[float, int, str] | None = None
    offset = 0
    for line in proof.splitlines(keepends=True):
        visible_line = line.rstrip("\r\n")
        line_tokens = set(re.findall(r"[A-Za-z0-9]+", visible_line.lower()))
        score = (
            len(query_tokens & line_tokens) / len(query_tokens)
            if query_tokens
            else 0.0
        )
        candidate = (score, offset + len(visible_line), visible_line)
        if best is None or candidate[0] > best[0]:
            best = candidate
        offset += len(line)
    if best is not None and best[0] >= 0.35:
        return best[1], best[2], "deterministic_token_overlap"
    return len(proof), "(end of submitted proof)", "end_of_proof_fallback"


def annotate_proof_with_tracing_memory(
    *,
    proof: str,
    decisive_location: str,
    selected_memory: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    ids_by_lane = {
        lane: [
            str(entry["trace_id"])
            for entry in selected_memory
            if entry["lane"] == lane
        ]
        for lane in TRACE_LANES
    }
    anchor_end, anchor_text, anchor_method = _attention_anchor(
        proof, decisive_location
    )

    selected_ids = [str(entry["trace_id"]) for entry in selected_memory]
    links = ", ".join(
        (
            f"[{trace_id}](#trace-"
            + re.sub(r"[^a-z0-9-]+", "-", trace_id.lower()).strip("-")
            + ")"
        )
        for trace_id in selected_ids
    ) or "(none)"

    block = "\n".join(
        [
            "<!-- CW_TRACE_ATTENTION_START -->",
            f"> **Tracing-memory packets:** {links}",
            "<!-- CW_TRACE_ATTENTION_END -->",
        ]
    )
    insertion = "\n\n" + block
    annotated = proof[:anchor_end] + insertion + proof[anchor_end:]
    reconstructed = (
        annotated[:anchor_end]
        + annotated[anchor_end + len(insertion) :]
    )
    annotation_slice = annotated[anchor_end : anchor_end + len(insertion)]
    packet_text_hits = {
        str(entry["trace_id"]): str(entry["text"]) in annotation_slice
        for entry in selected_memory
    }
    audit = {
        "anchor_method": anchor_method,
        "anchor_text": anchor_text,
        "anchor_end_offset": anchor_end,
        "selected_trace_ids_by_lane": ids_by_lane,
        "selected_trace_ids": selected_ids,
        "every_selected_id_appears_once_in_annotation": all(
            trace_id_occurrence_count(annotation_slice, trace_id) == 1
            for trace_id in selected_ids
        ),
        "packet_text_hits_inside_annotation": packet_text_hits,
        "annotation_contains_no_packet_text": not any(packet_text_hits.values()),
        "removing_annotation_reconstructs_original_exactly": reconstructed == proof,
        "original_proof_sha256": sha256_text(proof),
        "reconstructed_proof_sha256": sha256_text(reconstructed),
        "annotated_proof_sha256": sha256_text(annotated),
        "annotation_start_marker_count": annotated.count(
            "<!-- CW_TRACE_ATTENTION_START -->"
        ),
        "annotation_end_marker_count": annotated.count(
            "<!-- CW_TRACE_ATTENTION_END -->"
        ),
    }
    if not audit["every_selected_id_appears_once_in_annotation"]:
        raise ValueError("inline tracing annotation lost or duplicated a selected ID")
    if not audit["annotation_contains_no_packet_text"]:
        raise ValueError("inline tracing annotation duplicated packet text")
    if not audit["removing_annotation_reconstructs_original_exactly"]:
        raise ValueError("inline tracing annotation changed the submitted proof")
    if (
        audit["annotation_start_marker_count"] != 1
        or audit["annotation_end_marker_count"] != 1
    ):
        raise ValueError("inline tracing annotation markers are not unique")
    return annotated, audit


def synthesis_prompt(
    *, problem: str, proof: str, handoff: dict[str, Any]
) -> tuple[str, str]:
    fusion = handoff["fusion_channel"]
    preserve = "\n".join(
        f"- {value}" for value in fusion["preserve_after_rechecking"]
    ) or "- (none)"
    memory_text = render_selected_memory(
        handoff["tracing_memory_channel"]["entries"]
    )
    prompt = f"""Write one complete, self-contained Olympiad proof from the original assumptions.

The two guidance channels below are separate and unverified. Visible-review Fusion
never saw the tracing memory. The tracing-memory selector performed duplication
removal and removed content already explicit in the submitted proof; it performed
no correctness or usefulness filtering. Inclusion does not imply correctness.

Treat tracing memory as a reference notebook. It intentionally contains different
kinds of potentially useful material: counterexamples and defect analyses that can
expose traps, intermediate derivations that can supply calculations, and repair
routes that can suggest a strategy. Digest all entries, decide independently which
ones help this proof, and freely ignore the rest. Counterexamples and diagnostics
guide what must be avoided or repaired; they are not constructive proof steps.
Recheck and re-derive every adopted mathematical claim from the original
assumptions, and never cite either channel as authority.

GLOBAL INSTRUCTION FOR MARKED PROOF SECTIONS
Whenever a `Tracing-memory packets` line appears, the immediately preceding proof
passage is the marked target. Inspect the linked packet IDs in the separate
tracing-memory reference, digest their counterexamples, derivations, or repair
ideas, and independently choose what helps. Rewrite the marked passage with every
nontrivial mathematical transition explicitly derived from the original
assumptions. The links are navigation, not evidence: do not assume a linked packet
is correct and do not cite it in the proof. If the marked passage cannot be fully
repaired, state its exact first unresolved step instead of presenting a complete
proof. Do not copy the annotation line into the final proof.

If a complete proof is unavailable, state the exact first remaining gap instead of
hiding it behind phrases such as "after simplification" or "it follows".

ORIGINAL PROBLEM
{problem}

SUBMITTED PROOF TO RECHECK OR REPLACE
{proof}

VISIBLE-ONLY FUSION CHANNEL
VERDICT: {fusion['verdict']}
FAILED OBLIGATION: {fusion['failed_obligation'] or '(none identified)'}
INDEPENDENT VALIDATION: {fusion['independent_validation']}
RESOLVER BRIEF: {fusion['resolver_brief']}
PRESERVE ONLY AFTER RECHECKING:
{preserve}

SEPARATE TRACING-MEMORY REFERENCE — DEDUPLICATED, NOT VERIFIED
{memory_text}
"""
    return prompt, memory_text


def fusion_only_synthesis_prompt(
    *, problem: str, proof: str, fusion: dict[str, Any]
) -> str:
    preserve = "\n".join(
        f"- {value}" for value in fusion["preservable_material"]
    ) or "- (none)"
    return f"""Produce one rigorous, self-contained Olympiad proof using the original
assumptions. This first synthesis iteration receives only the visible-review Fusion
brief; it receives no hidden tracing-memory packet.

Independently recheck the submitted proof. Explicitly derive every nontrivial
transition needed to resolve Fusion's failed obligation. Do not replace algebra or
geometry with phrases such as "this forces", "after simplification", "similarly",
or "it follows". If the obligation cannot be fully derived, state its exact first
unresolved step instead of claiming a complete proof. Return only the proof or the
rigorous partial proof with that unresolved step.

ORIGINAL PROBLEM
{problem}

SUBMITTED PROOF TO RECHECK OR REPLACE
{proof}

VISIBLE-ONLY FUSION BRIEF
VERDICT: {fusion['verdict']}
FAILED OBLIGATION: {fusion['failed_obligation'] or '(none identified)'}
INDEPENDENT VALIDATION: {fusion['independent_validation']}
RESOLVER BRIEF: {fusion['resolver_brief']}
PRESERVE ONLY AFTER RECHECKING:
{preserve}
"""


def trace_batch_synthesis_prompt(
    *, problem: str, annotated_proof: str, entries: list[dict[str, Any]]
) -> tuple[str, str]:
    if not entries or len(entries) > 4:
        raise ValueError("a trace synthesis batch must contain one to four packets")
    memory_text = render_selected_memory(entries)
    prompt = f"""Rigorously refine the current Olympiad proof using one small tracing-memory
batch. This call receives exactly the packet IDs linked in the annotated proof and
no other tracing-memory packet. It receives no Fusion brief.

GLOBAL INSTRUCTION FOR MARKED PROOF SECTIONS
The immediately preceding proof passage at a `Tracing-memory packets` line is the
target of this refinement. Follow the packet-ID links into the batch reference,
digest the counterexamples, calculations, or repair ideas, and independently choose
what helps. Rewrite the marked passage with every nontrivial transition explicitly
derived from the original assumptions. Links and packets are unverified navigation,
not evidence: do not cite them or assume they are correct. Do not use phrases such
as "this forces", "after simplification", "similarly", or "it follows" in place of
the missing mathematics. If the marked passage cannot be fully repaired, state its
exact first unresolved step rather than claiming a complete proof. Remove the
annotation line from the returned proof.

ORIGINAL PROBLEM
{problem}

CURRENT PROOF WITH PACKET LINKS
{annotated_proof}

TRACING-MEMORY BATCH — ONLY THE LINKED PACKETS, ALL UNVERIFIED
{memory_text}
"""
    return prompt, memory_text


def canonicalize_generated_proof(value: str) -> tuple[str, list[str]]:
    text = value.strip()
    changes: list[str] = []
    cleaned, count = re.subn(
        r"\n*<!-- CW_TRACE_ATTENTION_START -->.*?"
        r"<!-- CW_TRACE_ATTENTION_END -->\n*",
        "\n",
        text,
        flags=re.DOTALL,
    )
    if count:
        text = cleaned.strip()
        changes.append("inline_attention_block_removed")
    lines = text.splitlines()
    filtered = [
        line
        for line in lines
        if not line.strip().startswith("> **Tracing-memory packets:**")
    ]
    if len(filtered) != len(lines):
        text = "\n".join(filtered).strip()
        changes.append("orphan_attention_link_line_removed")
    if not text:
        raise ValueError("proof became empty after annotation canonicalization")
    return text, changes


PATCH_HEADER_PATTERN = re.compile(
    r"\ASTART_BLOCK:\s*(L\d{3,})\s*\n"
    r"END_BLOCK:\s*(L\d{3,})\s*\n"
    r"REPLACEMENT:\s*\n(?P<replacement>[\s\S]+)\Z"
)


def proof_line_blocks(proof: str) -> list[dict[str, Any]]:
    if not proof:
        raise ValueError("cannot block-index an empty proof")
    physical_lines = proof.splitlines(keepends=True)
    if not physical_lines:
        physical_lines = [proof]
    return [
        {
            "block_id": f"L{index:03d}",
            "index": index - 1,
            "text": line.rstrip("\r\n"),
            "serialized": line,
        }
        for index, line in enumerate(physical_lines, start=1)
    ]


def proof_block_for_offset(proof: str, offset: int) -> str:
    blocks = proof_line_blocks(proof)
    cursor = 0
    for block in blocks:
        cursor += len(str(block["serialized"]))
        if offset <= cursor:
            return str(block["block_id"])
    return str(blocks[-1]["block_id"])


def render_block_indexed_proof(
    *,
    proof: str,
    anchor_end_offset: int | None,
    packet_ids: list[str],
    anchor_block_id: str | None = None,
    target_start_block_id: str | None = None,
    target_end_block_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    blocks = proof_line_blocks(proof)
    block_ids = [str(block["block_id"]) for block in blocks]
    if anchor_block_id is None:
        if anchor_end_offset is None:
            raise ValueError("a proof-block anchor is required")
        anchor_block_id = proof_block_for_offset(proof, anchor_end_offset)
    if anchor_block_id not in block_ids:
        raise ValueError("the carried proof-block anchor does not exist")
    target_start_block_id = target_start_block_id or anchor_block_id
    target_end_block_id = target_end_block_id or anchor_block_id
    if (
        target_start_block_id not in block_ids
        or target_end_block_id not in block_ids
    ):
        raise ValueError("the carried proof-block target range does not exist")
    if block_ids.index(target_start_block_id) > block_ids.index(target_end_block_id):
        raise ValueError("the carried proof-block target range is reversed")
    links = ", ".join(
        (
            f"[{trace_id}](#trace-"
            + re.sub(r"[^a-z0-9-]+", "-", trace_id.lower()).strip("-")
            + ")"
        )
        for trace_id in packet_ids
    )
    rendered: list[str] = []
    for block in blocks:
        block_id = str(block["block_id"])
        text = str(block["text"])
        rendered.extend([f"<!-- CW_BLOCK {block_id} -->", text])
        if block_id == anchor_block_id:
            rendered.append(
                (
                    f"> **Tracing-memory packets:** {links} — target range "
                    f"{target_start_block_id}–{target_end_block_id}"
                    if packet_ids
                    else "> **Visible-Fusion target block.**"
                )
            )
    audit = {
        "block_count": len(blocks),
        "block_ids": block_ids,
        "anchor_block_id": anchor_block_id,
        "target_start_block_id": target_start_block_id,
        "target_end_block_id": target_end_block_id,
        "packet_ids": packet_ids,
        "annotation_ids_match_packet_ids": all(
            trace_id_occurrence_count("\n".join(rendered), trace_id) == 1
            for trace_id in packet_ids
        ),
        "original_proof_sha256": sha256_text(proof),
    }
    if not audit["annotation_ids_match_packet_ids"]:
        raise ValueError("block-indexed proof annotation packet-ID drift")
    return "\n".join(rendered), audit


def parse_localized_patch_markdown(value: str) -> dict[str, Any]:
    text = value.strip().replace("\r\n", "\n")
    if text.startswith("```") or text.endswith("```"):
        raise ValueError("localized patch must not use a Markdown code fence")
    match = PATCH_HEADER_PATTERN.fullmatch(text)
    if match is None:
        raise ValueError("localized patch does not match the fixed-header contract")
    replacement = match.group("replacement").strip()
    if not replacement:
        raise ValueError("localized patch replacement is empty")
    if "<!-- CW_BLOCK " in replacement:
        raise ValueError("localized patch copied proof block markers")
    if "> **Tracing-memory packets:**" in replacement:
        raise ValueError("localized patch copied the packet annotation")
    block_reference_pattern = re.compile(
        (
            r"\s+(?:from|in|at)\s+\(?L\d{3,}\)?"
            r"(?:\s*(?:,|and)\s*\(?L\d{3,}\)?)*"
            r"(?![A-Za-z0-9_])(?P<punct>[,:]?)"
        ),
        flags=re.IGNORECASE,
    )

    def remove_block_reference(match: re.Match[str]) -> str:
        punctuation = match.group("punct")
        prefix = replacement[: match.start()].rstrip()
        if punctuation and prefix and prefix[-1] not in ".!?;:":
            return punctuation
        return ""

    replacement, removed_block_references = block_reference_pattern.subn(
        remove_block_reference, replacement
    )
    if re.search(r"\bL\d{3,}\b", replacement):
        raise ValueError("localized patch retained a proof block reference")
    return {
        "start_block": match.group(1),
        "end_block": match.group(2),
        "replacement": replacement,
        "deterministic_canonicalization": (
            ["proof_block_reference_removed"]
            if removed_block_references
            else []
        ),
    }


def apply_localized_patch(
    *,
    proof: str,
    patch: dict[str, Any],
    required_anchor_block: str,
    forbidden_trace_ids: list[str],
    required_target_start_block: str | None = None,
    required_target_end_block: str | None = None,
) -> tuple[str, dict[str, Any]]:
    blocks = proof_line_blocks(proof)
    by_id = {str(block["block_id"]): block for block in blocks}
    start_id = str(patch["start_block"])
    end_id = str(patch["end_block"])
    if start_id not in by_id or end_id not in by_id:
        raise ValueError("localized patch references a missing proof block")
    if required_anchor_block not in by_id:
        raise ValueError("localized patch anchor block is missing")
    start_index = int(by_id[start_id]["index"])
    end_index = int(by_id[end_id]["index"])
    target_start_id = required_target_start_block or required_anchor_block
    target_end_id = required_target_end_block or required_anchor_block
    if target_start_id not in by_id or target_end_id not in by_id:
        raise ValueError("localized patch target range is missing")
    target_start_index = int(by_id[target_start_id]["index"])
    target_end_index = int(by_id[target_end_id]["index"])
    if target_start_index > target_end_index:
        raise ValueError("localized patch target range is reversed")
    requested_start_id = start_id
    requested_end_id = end_id
    adjacent_anchor_range_expansion: str | None = None
    if start_index > end_index:
        raise ValueError("localized patch block range is reversed")
    overlaps_target = not (
        end_index < target_start_index or start_index > target_end_index
    )
    if not overlaps_target:
        if start_index == target_end_index + 1:
            start_index = target_end_index
            start_id = target_end_id
            adjacent_anchor_range_expansion = "PREPEND_MARKED_ANCHOR"
        elif end_index == target_start_index - 1:
            end_index = target_start_index
            end_id = target_start_id
            adjacent_anchor_range_expansion = "APPEND_MARKED_ANCHOR"
        else:
            raise ValueError(
                "localized patch does not contain or adjoin the marked target block"
            )
    if start_index == 0 and end_index == len(blocks) - 1:
        raise ValueError("localized patch may not replace the entire proof")

    replacement = str(patch["replacement"]).strip()
    trace_id_hits = {
        trace_id: contains_trace_id(replacement, trace_id)
        for trace_id in forbidden_trace_ids
    }
    if any(trace_id_hits.values()):
        raise ValueError("localized patch cited a tracing-memory packet ID")

    prefix = "".join(str(block["serialized"]) for block in blocks[:start_index])
    old_span = "".join(
        str(block["serialized"])
        for block in blocks[start_index : end_index + 1]
    )
    suffix = "".join(
        str(block["serialized"]) for block in blocks[end_index + 1 :]
    )
    serialized_replacement = replacement
    if suffix and not serialized_replacement.endswith(("\n", "\r")):
        serialized_replacement += "\n"
    updated = prefix + serialized_replacement + suffix
    if not updated:
        raise ValueError("localized patch produced an empty proof")
    replacement_line_count = len(
        serialized_replacement.splitlines(keepends=True)
    )
    output_replacement_start_block = f"L{start_index + 1:03d}"
    output_replacement_end_block = (
        f"L{start_index + replacement_line_count:03d}"
    )
    audit = {
        "contract": "CONTIGUOUS_BLOCK_REPLACEMENT",
        "requested_start_block": requested_start_id,
        "requested_end_block": requested_end_id,
        "start_block": start_id,
        "end_block": end_id,
        "adjacent_anchor_range_expansion": adjacent_anchor_range_expansion,
        "required_anchor_block": required_anchor_block,
        "required_target_start_block": target_start_id,
        "required_target_end_block": target_end_id,
        "edited_block_count": end_index - start_index + 1,
        "total_input_block_count": len(blocks),
        "entire_proof_replacement": False,
        "input_proof_sha256": sha256_text(proof),
        "prefix_sha256": sha256_text(prefix),
        "old_span_sha256": sha256_text(old_span),
        "replacement_sha256": sha256_text(replacement),
        "replacement_line_count": replacement_line_count,
        "output_replacement_start_block": output_replacement_start_block,
        "output_replacement_end_block": output_replacement_end_block,
        "suffix_sha256": sha256_text(suffix),
        "output_proof_sha256": sha256_text(updated),
        "prefix_preserved_byte_for_byte": updated.startswith(prefix),
        "suffix_preserved_byte_for_byte": updated.endswith(suffix),
        "forbidden_trace_id_hits": trace_id_hits,
    }
    if not audit["prefix_preserved_byte_for_byte"]:
        raise ValueError("localized patch changed the preserved prefix")
    if not audit["suffix_preserved_byte_for_byte"]:
        raise ValueError("localized patch changed the preserved suffix")
    return updated, audit


def fusion_only_patch_prompt(
    *, problem: str, proof: str, fusion: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    anchor_end, anchor_text, anchor_method = _attention_anchor(
        proof, str(fusion["decisive_location"])
    )
    indexed_proof, block_audit = render_block_indexed_proof(
        proof=proof, anchor_end_offset=anchor_end, packet_ids=[]
    )
    preserve = "\n".join(
        f"- {value}" for value in fusion["preservable_material"]
    ) or "- (none)"
    prompt = f"""Return one localized replacement for the current Olympiad proof.
This first synthesis call receives only the visible-review Fusion brief and no
tracing-memory packet. Preserve all sound proof material outside the smallest
contiguous block range needed to repair or rigorously expose the marked failure.

Return exactly this fixed-header Markdown record, without a code fence or any text
before START_BLOCK:

START_BLOCK: Lnnn
END_BLOCK: Lnnn
REPLACEMENT:
replacement proof passage

START_BLOCK and END_BLOCK must name an existing contiguous range in the indexed
proof and that range must contain the `Visible-Fusion target block`. Do not replace
the entire proof. REPLACEMENT must be self-contained relative to the preserved
prefix and suffix, contain no block markers, and explicitly derive every adopted
nontrivial step. If the failed obligation cannot be closed, replace the unsupported
claim with its exact first unresolved step.

ORIGINAL PROBLEM
{problem}

BLOCK-INDEXED CURRENT PROOF
{indexed_proof}

VISIBLE-ONLY FUSION BRIEF
VERDICT: {fusion['verdict']}
FAILED OBLIGATION: {fusion['failed_obligation'] or '(none identified)'}
INDEPENDENT VALIDATION: {fusion['independent_validation']}
RESOLVER BRIEF: {fusion['resolver_brief']}
PRESERVE ONLY AFTER RECHECKING:
{preserve}
"""
    return prompt, {
        **block_audit,
        "anchor_text": anchor_text,
        "anchor_method": anchor_method,
    }


def trace_batch_patch_prompt(
    *,
    problem: str,
    proof: str,
    decisive_location: str,
    entries: list[dict[str, Any]],
    carried_target_block_id: str | None = None,
    carried_target_start_block_id: str | None = None,
    carried_target_end_block_id: str | None = None,
) -> tuple[str, str, dict[str, Any]]:
    if not entries or len(entries) > 4:
        raise ValueError("a trace patch batch must contain one to four packets")
    packet_ids = [str(entry["trace_id"]) for entry in entries]
    if carried_target_block_id is None:
        anchor_end, anchor_text, anchor_method = _attention_anchor(
            proof, decisive_location
        )
    else:
        anchor_end = None
        blocks_by_id = {
            str(block["block_id"]): block for block in proof_line_blocks(proof)
        }
        if carried_target_block_id not in blocks_by_id:
            raise ValueError("the carried cumulative target block is missing")
        anchor_text = str(blocks_by_id[carried_target_block_id]["text"])
        anchor_method = "carried_forward_patch_target"
    indexed_proof, block_audit = render_block_indexed_proof(
        proof=proof,
        anchor_end_offset=anchor_end,
        packet_ids=packet_ids,
        anchor_block_id=carried_target_block_id,
        target_start_block_id=carried_target_start_block_id,
        target_end_block_id=carried_target_end_block_id,
    )
    memory_text = render_selected_memory(entries)
    prompt = f"""Return one localized replacement for the current Olympiad proof using
exactly the linked tracing-memory batch. No Fusion brief is supplied to this call.
Preserve the cumulative proof outside the smallest contiguous block range needed
to refine the marked passage.

Return exactly this fixed-header Markdown record, without a code fence or any text
before START_BLOCK:

START_BLOCK: Lnnn
END_BLOCK: Lnnn
REPLACEMENT:
replacement proof passage

START_BLOCK and END_BLOCK must name an existing contiguous range in the indexed
proof and that range must overlap the target range displayed by the
`Tracing-memory packets` annotation. Do not replace the entire proof. Digest the
linked counterexamples, derivations, and repair routes, but independently rederive
anything used from the original assumptions. REPLACEMENT must contain no packet
IDs, packet citations, annotation, or block markers. If no complete local repair is
available, preserve all established progress and state the exact first unresolved
step.

ORIGINAL PROBLEM
{problem}

BLOCK-INDEXED CUMULATIVE PROOF
{indexed_proof}

TRACING-MEMORY BATCH — ONLY THE LINKED PACKETS, ALL UNVERIFIED
{memory_text}
"""
    return prompt, memory_text, {
        **block_audit,
        "anchor_text": anchor_text,
        "anchor_method": anchor_method,
    }


def load_same_run_text_generation(
    *, destination: Path, stage: str, prompt: str
) -> dict[str, Any] | None:
    response_path = destination / f"{stage}.raw_response.json"
    metadata_path = destination / f"{stage}.metadata.json"
    if not response_path.is_file() or not metadata_path.is_file():
        return None
    metadata = read_object(metadata_path)
    if str(metadata.get("prompt_sha256") or "") != sha256_text(prompt):
        return None
    response = read_object(response_path)
    try:
        message = response["choices"][0]["message"]
        text = message["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("same-run text-generation artifact is malformed") from error
    if not isinstance(text, str) or not text.strip():
        raise ValueError("same-run text-generation artifact has empty content")
    return {
        "text": text,
        "metadata": metadata,
        "resumed_same_run_artifact": True,
    }


def audit_visible_fusion_prompt(
    prompt: str, packets: list[dict[str, Any]]
) -> dict[str, Any]:
    trace_id_hits = {
        str(packet["trace_id"]): str(packet["trace_id"]) in prompt
        for packet in packets
    }
    return {
        "fusion_input_channels": [
            "original_problem",
            "submitted_proof",
            "reviewer_1_visible",
            "reviewer_2_visible",
            "reviewer_3_visible",
        ],
        "tracing_memory_argument_provided": False,
        "trace_id_hits": trace_id_hits,
        "all_trace_ids_absent": not any(trace_id_hits.values()),
        "trace_section_marker_absent": "TRACE_ID:" not in prompt,
    }


def run(
    *,
    source_run: Path,
    output_dir: Path,
    visible_fusion_transport: str = "json",
    harness_version: str = HARNESS_VERSION,
    inline_trace_annotations: bool = False,
    iterative_synthesis_batch_size: int | None = None,
    fusion_only_first_synthesis: bool = False,
    localized_patch_synthesis: bool = False,
) -> dict[str, Any]:
    if visible_fusion_transport not in {"json", "fixed_header_markdown"}:
        raise ValueError("unsupported visible Fusion transport")
    if iterative_synthesis_batch_size is not None:
        if not 1 <= iterative_synthesis_batch_size <= 4:
            raise ValueError("iterative synthesis batch size must be between 1 and 4")
        if not fusion_only_first_synthesis:
            raise ValueError("iterative synthesis requires a Fusion-only first call")
        if not inline_trace_annotations:
            raise ValueError("iterative trace synthesis requires inline annotations")
    if localized_patch_synthesis and iterative_synthesis_batch_size is None:
        raise ValueError("localized patch synthesis requires iterative synthesis")
    version_tag = f"0{harness_version.rsplit('.', 1)[1]}"
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    status_path = destination / "status.json"
    try:
        source = load_source(source_run)
        contract = source["contract"]
        master_seed = int(contract["master_seed"])
        seed_namespace = f"{contract['seed_namespace']}:v{version_tag}"
        runtime = runtime_for(
            gemma_endpoint=str(contract["gemma_endpoint"]),
            qwen_endpoint=str(contract["qwen_endpoint"]),
            master_seed=master_seed,
        )
        raw_packets = [
            packet
            for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            if role in source["packets"]
            for packet in source["packets"][role]
        ]
        trace_ids = [str(packet["trace_id"]) for packet in raw_packets]
        if len(trace_ids) != len(set(trace_ids)):
            raise ValueError("tracing-memory source IDs are not globally unique")
        for packet in raw_packets:
            assert_no_external_material(
                str(packet["exact_source_text"]),
                label=f"trace packet {packet['trace_id']}",
            )

        write_json(
            destination / "manifest.json",
            {
                "schema": (
                    f"cognitive-well-v{version_tag}-separate-tracing-memory-"
                    "manifest-v1"
                ),
                "harness_version": harness_version,
                "created_at": utc_now(),
                "source_run": str(source["source"]),
                "source_manifest_sha256": sha256_file(
                    source["source"] / "manifest.json"
                ),
                "problem_id": source["problem_id"],
                "candidate_id": source["candidate_id"],
                "models": {
                    "visible_only_fusion": GEMMA_MODEL,
                    "tracing_memory_dedup_selector": QWEN_MODEL,
                    "proof_synthesis": GEMMA_MODEL,
                },
                "policy": {
                    "fusion_trace_access": False,
                    "fusion_visible_review_access": True,
                    "visible_fusion_transport": visible_fusion_transport,
                    "inline_trace_annotations_for_synthesis": (
                        inline_trace_annotations
                    ),
                    "fusion_receives_annotated_proof": False,
                    "selector_receives_annotated_proof": False,
                    "fusion_only_first_synthesis": fusion_only_first_synthesis,
                    "iterative_synthesis_batch_size": iterative_synthesis_batch_size,
                    "later_synthesis_receives_fusion": False,
                    "packet_batch_order": "selected_memory_order",
                    "localized_patch_synthesis": localized_patch_synthesis,
                    "cumulative_proof_state": localized_patch_synthesis,
                    "preserved_prefix_suffix_byte_audit": (
                        localized_patch_synthesis
                    ),
                    "tracing_memory_contains_all_source_packets_before_dedup": True,
                    "selector_visible_review_access": False,
                    "selector_fusion_access": False,
                    "selector_filtering_operations": [
                        "remove_material_already_explicit_in_submitted_proof",
                        "exact_or_semantic_trace_deduplication",
                    ],
                    "cross_lane_deduplication": False,
                    "tracing_memory_verification_status": "UNVERIFIED",
                    "route_completion_enabled": False,
                    "promotion_allowed_without_independent_audit": False,
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

        write_status(status_path, state="running", stage="raw_tracing_memory")
        write_json(
            destination / "01_tracing_memory" / "raw_memory.json",
            {
                "verification_status": "UNVERIFIED",
                "content_transformations": [],
                "packet_count": len(raw_packets),
                "packets": raw_packets,
            },
        )

        write_status(status_path, state="running", stage="visible_only_fusion")
        fusion_prompt = (
            visible_fusion_markdown_prompt(
                problem=source["problem"],
                proof=source["proof"],
                visible=source["visible"],
            )
            if visible_fusion_transport == "fixed_header_markdown"
            else visible_fusion_prompt(
                problem=source["problem"],
                proof=source["proof"],
                visible=source["visible"],
            )
        )
        fusion_audit = audit_visible_fusion_prompt(fusion_prompt, raw_packets)
        if not fusion_audit["all_trace_ids_absent"]:
            raise ValueError("tracing-memory ID leaked into visible-only Fusion")
        if not fusion_audit["trace_section_marker_absent"]:
            raise ValueError("tracing-memory section leaked into visible-only Fusion")
        fusion_dir = destination / "02_visible_only_fusion"
        if visible_fusion_transport == "fixed_header_markdown":
            fusion_generation = ModelRuntime(runtime.config).text(
                role="gemma",
                prompt=fusion_prompt,
                destination=fusion_dir,
                stage="visible_only_fusion_markdown",
                temperature=0.1,
                max_tokens=18_432,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:visible-only-fusion-markdown"
                ),
                user_prompt="Return the fixed-header Markdown Fusion record now.",
            )
            fusion_metadata = dict(fusion_generation.get("metadata") or {})
            fusion = parse_visible_fusion_markdown(
                str(fusion_generation.get("text") or ""),
                finish_reason=(
                    str(fusion_metadata.get("finish_reason"))
                    if fusion_metadata.get("finish_reason") is not None
                    else None
                ),
            )
        else:
            fusion, fusion_generation = runtime.structured(
                role="gemma",
                prompt=fusion_prompt,
                destination=fusion_dir,
                stage="visible_only_fusion",
                schema=VISIBLE_FUSION_SCHEMA,
                temperature=0.1,
                max_tokens=18_432,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:visible-only-fusion"
                ),
            )
        (fusion_dir / "fusion_input.txt").write_text(fusion_prompt, encoding="utf-8")
        write_json(fusion_dir / "prompt_audit.json", fusion_audit)
        write_json(
            fusion_dir / "result.json",
            {"fusion": fusion, "generation": fusion_generation.get("metadata")},
        )

        write_status(status_path, state="running", stage="tracing_memory_dedup")

        def select_lane(lane: str) -> dict[str, Any]:
            lane_packets = [
                packet for packet in raw_packets if packet_lane(packet) == lane
            ]
            lane_dir = destination / "03_tracing_memory_dedup" / lane.lower()
            result_path = lane_dir / "result.json"
            if result_path.is_file():
                existing = read_object(result_path)
                groups, proof_redundant_ids, selected = validate_trace_dedup(
                    existing, lane_packets
                )
                return {
                    "lane": lane,
                    "duplicate_groups": groups,
                    "proof_redundant_ids": proof_redundant_ids,
                    "selected": selected,
                    "generation": existing.get("generation"),
                    "resumed_same_run_artifact": True,
                }
            prompt = tracing_memory_selector_prompt(
                problem=source["problem"],
                proof=source["proof"],
                lane=lane,
                packets=lane_packets,
            )
            record, generation = runtime.structured(
                role="qwen",
                prompt=prompt,
                destination=lane_dir,
                stage=f"{lane.lower()}_tracing_memory_dedup",
                schema=TRACE_DEDUP_SCHEMA,
                temperature=0.1,
                max_tokens=12_288,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:{lane}:trace-memory-dedup"
                ),
            )
            record, deterministic_canonicalization = (
                canonicalize_trace_dedup_record(record, lane_packets)
            )
            groups, proof_redundant_ids, selected = validate_trace_dedup(
                record, lane_packets
            )
            result = {
                "duplicate_groups": groups,
                "proof_redundant_ids": proof_redundant_ids,
                "selected_trace_ids": [entry["trace_id"] for entry in selected],
                "selected_entries": selected,
                "deterministic_canonicalization": deterministic_canonicalization,
                "generation": generation.get("metadata"),
            }
            write_json(result_path, result)
            return {
                "lane": lane,
                "duplicate_groups": groups,
                "proof_redundant_ids": proof_redundant_ids,
                "selected": selected,
                "generation": generation.get("metadata"),
                "resumed_same_run_artifact": False,
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                lane: executor.submit(select_lane, lane) for lane in TRACE_LANES
            }
            lane_results = {
                lane: futures[lane].result() for lane in TRACE_LANES
            }
        selected_memory = [
            entry
            for lane in TRACE_LANES
            for entry in lane_results[lane]["selected"]
        ]
        selected_memory_record = {
            "verification_status": "UNVERIFIED",
            "selector_operations": [
                "REMOVE_PROOF_REDUNDANCY",
                "DEDUPLICATE_TRACING_MEMORY",
            ],
            "raw_packet_count": len(raw_packets),
            "selected_packet_count": len(selected_memory),
            "selected_count_by_lane": {
                lane: len(lane_results[lane]["selected"]) for lane in TRACE_LANES
            },
            "duplicate_groups_by_lane": {
                lane: lane_results[lane]["duplicate_groups"] for lane in TRACE_LANES
            },
            "proof_redundant_ids_by_lane": {
                lane: lane_results[lane]["proof_redundant_ids"]
                for lane in TRACE_LANES
            },
            "entries": selected_memory,
        }
        write_json(
            destination / "04_selected_tracing_memory" / "memory.json",
            selected_memory_record,
        )

        write_status(status_path, state="running", stage="separate_handoff")
        handoff = build_separate_handoff(
            fusion=fusion, selected_memory=selected_memory
        )
        handoff_dir = destination / "05_separate_handoff"
        write_json(handoff_dir / "handoff.json", handoff)
        iteration_records: list[dict[str, Any]] = []
        packet_batches: list[list[str]] = []
        if iterative_synthesis_batch_size is not None:
            batches = [
                selected_memory[index : index + iterative_synthesis_batch_size]
                for index in range(
                    0, len(selected_memory), iterative_synthesis_batch_size
                )
            ]
            packet_batches = [
                [str(entry["trace_id"]) for entry in batch] for batch in batches
            ]
            flattened_batch_ids = [
                trace_id for batch_ids in packet_batches for trace_id in batch_ids
            ]
            selected_ids = [str(entry["trace_id"]) for entry in selected_memory]
            schedule_audit = {
                "first_iteration_input": "VISIBLE_FUSION_ONLY",
                "later_iterations_receive_fusion": False,
                "packet_batch_size_limit": iterative_synthesis_batch_size,
                "packet_batches": packet_batches,
                "all_batches_have_at_most_limit": all(
                    1 <= len(batch) <= iterative_synthesis_batch_size
                    for batch in packet_batches
                ),
                "every_selected_packet_assigned_once": (
                    flattened_batch_ids == selected_ids
                ),
            }
            if not schedule_audit["all_batches_have_at_most_limit"]:
                raise ValueError("an iterative synthesis batch exceeds its limit")
            if not schedule_audit["every_selected_packet_assigned_once"]:
                raise ValueError("iterative synthesis packet assignment drift")
            write_json(handoff_dir / "iteration_schedule.json", schedule_audit)

            total_iterations = 1 + len(batches)
            current_proof = source["proof"]
            iteration_root = destination / "06_synthesis_iterations"
            write_status(
                status_path,
                state="running",
                stage="proof_synthesis_iteration",
                iteration=1,
                total_iterations=total_iterations,
                packet_ids=[],
            )
            first_dir = iteration_root / "iteration_01_fusion"
            first_dir.mkdir(parents=True, exist_ok=True)
            first_block_audit: dict[str, Any] | None = None
            if localized_patch_synthesis:
                first_prompt, first_block_audit = fusion_only_patch_prompt(
                    problem=source["problem"],
                    proof=current_proof,
                    fusion=fusion,
                )
            else:
                first_prompt = fusion_only_synthesis_prompt(
                    problem=source["problem"], proof=current_proof, fusion=fusion
                )
            first_prompt_audit = audit_visible_fusion_prompt(
                first_prompt, raw_packets
            )
            first_prompt_audit["localized_patch_synthesis"] = (
                localized_patch_synthesis
            )
            first_prompt_audit["block_audit"] = first_block_audit
            if not first_prompt_audit["all_trace_ids_absent"]:
                raise ValueError(
                    "tracing-memory ID leaked into Fusion-only synthesis"
                )
            if not first_prompt_audit["trace_section_marker_absent"]:
                raise ValueError(
                    "tracing-memory section leaked into Fusion-only synthesis"
                )
            (first_dir / "proof_synthesis.prompt.txt").write_text(
                first_prompt, encoding="utf-8"
            )
            if localized_patch_synthesis:
                (first_dir / "cumulative_input_proof.md").write_text(
                    current_proof + "\n", encoding="utf-8"
                )
            write_json(first_dir / "prompt_audit.json", first_prompt_audit)
            first_generated = load_same_run_text_generation(
                destination=first_dir,
                stage="iteration_01_fusion_synthesis",
                prompt=first_prompt,
            )
            if first_generated is None:
                first_generated = runtime.text(
                    role="gemma",
                    prompt=first_prompt,
                    destination=first_dir,
                    stage="iteration_01_fusion_synthesis",
                    temperature=0.4,
                    max_tokens=32_768,
                    seed_label=(
                        f"{seed_namespace}:{source['problem_id']}:"
                        f"{source['candidate_id']}:iteration-01-fusion"
                    ),
                )
            first_patch_audit: dict[str, Any] | None = None
            first_patch: dict[str, Any] | None = None
            cumulative_target_block_id: str | None = None
            cumulative_target_start_block_id: str | None = None
            cumulative_target_end_block_id: str | None = None
            if localized_patch_synthesis:
                if first_block_audit is None:
                    raise ValueError("Fusion patch block audit is missing")
                first_patch = parse_localized_patch_markdown(
                    str(first_generated["text"])
                )
                current_proof, first_patch_audit = apply_localized_patch(
                    proof=current_proof,
                    patch=first_patch,
                    required_anchor_block=str(
                        first_block_audit["anchor_block_id"]
                    ),
                    forbidden_trace_ids=trace_ids,
                )
                changes = []
                write_json(first_dir / "localized_patch.json", first_patch)
                write_json(first_dir / "patch_audit.json", first_patch_audit)
                cumulative_target_block_id = str(
                    first_patch_audit["output_replacement_end_block"]
                )
                cumulative_target_start_block_id = str(
                    first_patch_audit["output_replacement_start_block"]
                )
                cumulative_target_end_block_id = str(
                    first_patch_audit["output_replacement_end_block"]
                )
            else:
                current_proof, changes = canonicalize_generated_proof(
                    str(first_generated["text"])
                )
            first_proof_path = first_dir / "proof.md"
            first_proof_path.write_text(current_proof + "\n", encoding="utf-8")
            iteration_records.append(
                {
                    "iteration": 1,
                    "mode": "VISIBLE_FUSION_ONLY",
                    "packet_ids": [],
                    "proof_path": str(first_proof_path),
                    "proof_sha256": sha256_text(current_proof),
                    "localized_patch": first_patch,
                    "patch_audit": first_patch_audit,
                    "deterministic_canonicalization": changes,
                    "generation": first_generated.get("metadata"),
                    "resumed_same_run_generation": bool(
                        first_generated.get("resumed_same_run_artifact")
                    ),
                }
            )
            generated = first_generated
            proof_path = first_proof_path

            for batch_index, batch in enumerate(batches, start=2):
                packet_ids = [str(entry["trace_id"]) for entry in batch]
                write_status(
                    status_path,
                    state="running",
                    stage="proof_synthesis_iteration",
                    iteration=batch_index,
                    total_iterations=total_iterations,
                    packet_ids=packet_ids,
                )
                iteration_dir = (
                    iteration_root
                    / f"iteration_{batch_index:02d}_trace_batch"
                )
                iteration_dir.mkdir(parents=True, exist_ok=True)
                if localized_patch_synthesis:
                    (
                        batch_prompt,
                        batch_memory_text,
                        batch_annotation_audit,
                    ) = trace_batch_patch_prompt(
                        proof=current_proof,
                        problem=source["problem"],
                        decisive_location=str(fusion["decisive_location"]),
                        entries=batch,
                        carried_target_block_id=cumulative_target_block_id,
                        carried_target_start_block_id=(
                            cumulative_target_start_block_id
                        ),
                        carried_target_end_block_id=(
                            cumulative_target_end_block_id
                        ),
                    )
                    annotated_proof = ""
                    annotation_ids = list(
                        batch_annotation_audit["packet_ids"]
                    )
                else:
                    annotated_proof, batch_annotation_audit = (
                        annotate_proof_with_tracing_memory(
                            proof=current_proof,
                            decisive_location=str(fusion["decisive_location"]),
                            selected_memory=batch,
                        )
                    )
                    annotation_ids = list(
                        batch_annotation_audit["selected_trace_ids"]
                    )
                    batch_prompt, batch_memory_text = trace_batch_synthesis_prompt(
                        problem=source["problem"],
                        annotated_proof=annotated_proof,
                        entries=batch,
                    )
                if annotation_ids != packet_ids:
                    raise ValueError("iteration annotation packet-ID drift")
                batch_prompt_audit = {
                    "packet_ids": packet_ids,
                    "packet_count": len(packet_ids),
                    "packet_count_at_most_four": len(packet_ids) <= 4,
                    "only_this_batch_is_directly_supplied": True,
                    "fusion_brief_supplied": False,
                    "localized_patch_synthesis": localized_patch_synthesis,
                    "annotation_ids_match_batch": annotation_ids == packet_ids,
                    "batch_memory_payload_occurrences": batch_prompt.count(
                        batch_memory_text
                    ),
                    "batch_memory_payload_appears_exactly_once": (
                        batch_prompt.count(batch_memory_text) == 1
                    ),
                    "nonbatch_trace_id_hits": {
                        trace_id: contains_trace_id(batch_prompt, trace_id)
                        for trace_id in selected_ids
                        if trace_id not in packet_ids
                    },
                }
                if not batch_prompt_audit[
                    "batch_memory_payload_appears_exactly_once"
                ]:
                    raise ValueError("iteration tracing-memory payload drift")
                if any(batch_prompt_audit["nonbatch_trace_id_hits"].values()):
                    raise ValueError(
                        "nonbatch tracing-memory ID leaked into synthesis prompt"
                    )
                if localized_patch_synthesis:
                    (iteration_dir / "cumulative_input_proof.md").write_text(
                        current_proof + "\n", encoding="utf-8"
                    )
                else:
                    (iteration_dir / "annotated_input_proof.md").write_text(
                        annotated_proof + "\n", encoding="utf-8"
                    )
                write_json(
                    iteration_dir / "annotation_audit.json",
                    batch_annotation_audit,
                )
                write_json(
                    iteration_dir / "packet_memory.json",
                    {"entries": batch},
                )
                write_json(
                    iteration_dir / "prompt_audit.json", batch_prompt_audit
                )
                batch_stage = (
                    f"iteration_{batch_index:02d}_trace_batch_synthesis"
                )
                batch_generated = load_same_run_text_generation(
                    destination=iteration_dir,
                    stage=batch_stage,
                    prompt=batch_prompt,
                )
                if batch_generated is None:
                    batch_generated = runtime.text(
                        role="gemma",
                        prompt=batch_prompt,
                        destination=iteration_dir,
                        stage=batch_stage,
                        temperature=0.4,
                        max_tokens=32_768,
                        seed_label=(
                            f"{seed_namespace}:{source['problem_id']}:"
                            f"{source['candidate_id']}:"
                            f"iteration-{batch_index:02d}:"
                            + "-".join(packet_ids)
                        ),
                    )
                batch_patch_audit: dict[str, Any] | None = None
                batch_patch: dict[str, Any] | None = None
                if localized_patch_synthesis:
                    batch_patch = parse_localized_patch_markdown(
                        str(batch_generated["text"])
                    )
                    current_proof, batch_patch_audit = apply_localized_patch(
                        proof=current_proof,
                        patch=batch_patch,
                        required_anchor_block=str(
                            batch_annotation_audit["anchor_block_id"]
                        ),
                        forbidden_trace_ids=trace_ids,
                        required_target_start_block=str(
                            batch_annotation_audit["target_start_block_id"]
                        ),
                        required_target_end_block=str(
                            batch_annotation_audit["target_end_block_id"]
                        ),
                    )
                    changes = []
                    write_json(
                        iteration_dir / "localized_patch.json", batch_patch
                    )
                    write_json(
                        iteration_dir / "patch_audit.json", batch_patch_audit
                    )
                    cumulative_target_block_id = str(
                        batch_patch_audit["output_replacement_end_block"]
                    )
                    cumulative_target_start_block_id = str(
                        batch_patch_audit["output_replacement_start_block"]
                    )
                    cumulative_target_end_block_id = str(
                        batch_patch_audit["output_replacement_end_block"]
                    )
                else:
                    current_proof, changes = canonicalize_generated_proof(
                        str(batch_generated["text"])
                    )
                batch_proof_path = iteration_dir / "proof.md"
                batch_proof_path.write_text(
                    current_proof + "\n", encoding="utf-8"
                )
                iteration_records.append(
                    {
                        "iteration": batch_index,
                        "mode": "TRACE_PACKET_BATCH",
                        "packet_ids": packet_ids,
                        "proof_path": str(batch_proof_path),
                        "proof_sha256": sha256_text(current_proof),
                        "annotation_audit": batch_annotation_audit,
                        "prompt_audit": batch_prompt_audit,
                        "localized_patch": batch_patch,
                        "patch_audit": batch_patch_audit,
                        "deterministic_canonicalization": changes,
                        "generation": batch_generated.get("metadata"),
                        "resumed_same_run_generation": bool(
                            batch_generated.get("resumed_same_run_artifact")
                        ),
                    }
                )
                generated = batch_generated
                proof_path = batch_proof_path
            proof_text = current_proof
            prompt_audit = {
                **schedule_audit,
                "iteration_count": len(iteration_records),
            }
            write_json(iteration_root / "summary.json", {
                "iterations": iteration_records,
                "schedule_audit": schedule_audit,
                "final_proof_path": str(proof_path),
            })
            write_json(handoff_dir / "prompt_audit.json", prompt_audit)
        else:
            proof_for_synthesis = source["proof"]
            annotation_audit: dict[str, Any] | None = None
            if inline_trace_annotations:
                proof_for_synthesis, annotation_audit = (
                    annotate_proof_with_tracing_memory(
                        proof=source["proof"],
                        decisive_location=str(fusion["decisive_location"]),
                        selected_memory=selected_memory,
                    )
                )
                (handoff_dir / "annotated_proof.md").write_text(
                    proof_for_synthesis + "\n", encoding="utf-8"
                )
                write_json(handoff_dir / "annotation_audit.json", annotation_audit)
            proof_prompt, memory_text = synthesis_prompt(
                problem=source["problem"],
                proof=proof_for_synthesis,
                handoff=handoff,
            )
            prompt_audit = {
                "fusion_and_tracing_memory_are_separate_sections": True,
                "fusion_saw_tracing_memory": False,
                "inline_trace_annotations_enabled": inline_trace_annotations,
                "annotation_audit": annotation_audit,
                "selected_memory_payload_occurrences": proof_prompt.count(memory_text),
                "selected_memory_payload_appears_exactly_once": (
                    proof_prompt.count(memory_text) == 1
                ),
                "selected_trace_ids": [
                    entry["trace_id"] for entry in selected_memory
                ],
                "external_marker_hits": {
                    marker: marker in proof_prompt.lower()
                    for marker in (
                        "codex score",
                        "codex grade",
                        "gold-informed",
                        "external scorer feedback",
                    )
                },
            }
            if not prompt_audit["selected_memory_payload_appears_exactly_once"]:
                raise ValueError(
                    "selected tracing-memory payload was lost or duplicated"
                )
            if any(prompt_audit["external_marker_hits"].values()):
                raise ValueError("external marker leaked into synthesis prompt")
            (handoff_dir / "proof_synthesis.prompt.txt").write_text(
                proof_prompt, encoding="utf-8"
            )
            write_json(handoff_dir / "prompt_audit.json", prompt_audit)

            write_status(status_path, state="running", stage="proof_synthesis")
            generated = runtime.text(
                role="gemma",
                prompt=proof_prompt,
                destination=destination / "06_proof_synthesis",
                stage="separate_tracing_memory_proof_synthesis",
                temperature=0.4,
                max_tokens=32_768,
                seed_label=(
                    f"{seed_namespace}:{source['problem_id']}:"
                    f"{source['candidate_id']}:synthesis"
                ),
            )
            proof_text, changes = canonicalize_generated_proof(
                str(generated["text"])
            )
            proof_path = destination / "06_proof_synthesis" / "proof.md"
            proof_path.write_text(proof_text + "\n", encoding="utf-8")
            iteration_records = [
                {
                    "iteration": 1,
                    "mode": "SINGLE_PASS",
                    "packet_ids": [
                        str(entry["trace_id"]) for entry in selected_memory
                    ],
                    "proof_path": str(proof_path),
                    "proof_sha256": sha256_text(proof_text),
                    "deterministic_canonicalization": changes,
                    "generation": generated.get("metadata"),
                }
            ]
        write_json(
            destination / "07_result.json",
            {
                "schema": f"cognitive-well-v{version_tag}-terminal-proof-v1",
                "problem_id": source["problem_id"],
                "candidate_id": source["candidate_id"],
                "proof": proof_text,
                "proof_path": str(proof_path),
                "proof_sha256": sha256_text(proof_text),
                "generation": generated.get("metadata"),
                "fusion_verdict": fusion["verdict"],
                "tracing_memory_packet_count": len(selected_memory),
                "synthesis_iteration_count": len(iteration_records),
                "packet_batches": packet_batches,
                "synthesis_iterations": iteration_records,
                "localized_patch_synthesis": localized_patch_synthesis,
                "promotion_allowed_without_independent_audit": False,
            },
        )
        summary = {
            "schema": f"cognitive-well-v{version_tag}-summary-v1",
            "harness_version": harness_version,
            "state": "completed",
            "outcome": "PROOF_SYNTHESIZED",
            "completed_at": utc_now(),
            "problem_id": source["problem_id"],
            "candidate_id": source["candidate_id"],
            "fusion_verdict": fusion["verdict"],
            "raw_tracing_memory_packet_count": len(raw_packets),
            "selected_tracing_memory_packet_count": len(selected_memory),
            "selected_count_by_lane": selected_memory_record[
                "selected_count_by_lane"
            ],
            "inline_trace_annotations_enabled": inline_trace_annotations,
            "synthesis_iteration_count": len(iteration_records),
            "packet_batches": packet_batches,
            "localized_patch_synthesis": localized_patch_synthesis,
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
    "TRACE_DEDUP_SCHEMA",
    "VISIBLE_FUSION_SCHEMA",
    "audit_visible_fusion_prompt",
    "annotate_proof_with_tracing_memory",
    "apply_localized_patch",
    "build_separate_handoff",
    "canonicalize_generated_proof",
    "fusion_only_patch_prompt",
    "load_same_run_text_generation",
    "fusion_only_synthesis_prompt",
    "parse_visible_fusion_markdown",
    "public_packet",
    "parse_localized_patch_markdown",
    "proof_line_blocks",
    "render_selected_memory",
    "run",
    "synthesis_prompt",
    "trace_batch_patch_prompt",
    "trace_batch_synthesis_prompt",
    "tracing_memory_selector_prompt",
    "validate_trace_dedup",
    "visible_fusion_prompt",
    "visible_fusion_markdown_prompt",
]
