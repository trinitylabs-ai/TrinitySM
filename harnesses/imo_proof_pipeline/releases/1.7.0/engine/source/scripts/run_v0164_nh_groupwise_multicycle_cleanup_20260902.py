from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import re
import sys
import threading
import traceback
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
)
from cognitive_well_harness_v0_3_140_clean_dual_trace_fusion_20260901.pipeline import (
    GEMMA_MODEL,
    QWEN_MODEL,
)
from cognitive_well_harness_v0_3_150_cleanup_gate_20260902.cleanup import (
    run_cleanup_gate,
)
from cognitive_well_harness_v0_3_149_v108_three_cycle_v148_20260902.pipeline import (
    _artifact_metrics,
)


HARNESS_VERSION = "v0.3.165-nh-max10-groupwise-multicycle-cleanup-20260902"
DEFAULT_OUTPUT = REPO_ROOT / "runs/v0165_nh_max10_three_cycle_cleanup_20260902"
DEFAULT_CASES: dict[str, Path] = {
    "p1:t07_r02": REPO_ROOT
    / "runs/v0162_binary_novelty_fourproof_20260902/p1/t07_r02",
    "p1:t10_r01": REPO_ROOT
    / "runs/v0162_binary_novelty_fourproof_20260902/p1/t10_r01",
    "p2:t10_r01": REPO_ROOT
    / "runs/v0162_binary_novelty_fourproof_20260902/p2/t10_r01",
    "p2:t10_r02": REPO_ROOT
    / "runs/v0162_binary_novelty_fourproof_20260902/p2/t10_r02",
    "p3:t07_r02": REPO_ROOT
    / "runs/v0162_binary_novelty_p3_t07_high_budget_recovery_20260902/p3/t07_r02",
    "p3:t10_r01": REPO_ROOT
    / "runs/v0162_binary_novelty_p3_t10_high_budget_repair_20260902/p3/t10_r01",
    "p4:t07_r02": REPO_ROOT
    / "runs/v0162_binary_novelty_p4_p6_oneproof_20260902/p4/t07_r02",
    "p5:t07_r02": REPO_ROOT
    / "runs/v0162_binary_novelty_p4_p6_oneproof_20260902/p5/t07_r02",
}
DEFAULT_SELECTED_CASE_KEYS = (
    "p1:t07_r02",
    "p2:t10_r02",
    "p3:t10_r01",
    "p4:t07_r02",
    "p5:t07_r02",
)
TRACE_ID_PATTERN = re.compile(r"\bR[123]TG\d+\b", flags=re.IGNORECASE)
TRANSPORT_MARKERS = ("<!-- CW_BLOCK", "START_BLOCK:", "END_BLOCK:")
MAX_EDITS_PER_GROUP = 6
MAX_EDITED_LINE_FRACTION = 0.65
MAX_NH_PACKETS_PER_CALL = 10


PATCH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["action", "edits", "verification_summary"],
    "properties": {
        "action": {"type": "string", "enum": ["REPLACE", "NO_CHANGE"]},
        "edits": {
            "type": "array",
            "maxItems": MAX_EDITS_PER_GROUP,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["start_line", "end_line", "replacement"],
                "properties": {
                    "start_line": {"type": "integer", "minimum": 1},
                    "end_line": {"type": "integer", "minimum": 1},
                    "replacement": {"type": "string"},
                },
            },
        },
        "verification_summary": {"type": "string"},
    },
}


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(encoded)


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_text_exact(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(value.encode("utf-8"))
    temporary.replace(path)


def indexed_proof(proof: str) -> str:
    lines = proof.splitlines()
    return "\n".join(
        f"L{index:03d}: {line}" for index, line in enumerate(lines, start=1)
    )


def case_key_parts(case_key: str) -> tuple[str, str]:
    match = re.fullmatch(r"p([1-9]\d*):([A-Za-z0-9_-]+)", case_key)
    if match is None:
        raise ValueError(f"invalid case key: {case_key}")
    return f"p{match.group(1)}", match.group(2)


def validate_source_hash(path: Path, expected: str, *, label: str) -> None:
    actual = file_sha256(path)
    if actual != expected:
        raise ValueError(f"{label} hash drift: expected {expected}, got {actual}")


def load_case(case_key: str, label_dir: Path) -> dict[str, Any]:
    label_root = label_dir.resolve()
    manifest_path = label_root / "manifest.json"
    result_path = label_root / "result.json"
    manifest = read_object(manifest_path)
    result = read_object(result_path)
    if result.get("state") != "completed":
        raise ValueError(f"novelty labeling is not completed: {result_path}")
    source = dict(manifest.get("source") or {})
    problem_path = Path(str(source["problem_json"])).resolve()
    proof_path = Path(str(source["proof"])).resolve()
    lemma_index_path = Path(str(source["lemma_index"])).resolve()
    validate_source_hash(
        problem_path, str(source["problem_json_sha256"]), label="problem"
    )
    validate_source_hash(proof_path, str(source["proof_sha256"]), label="proof")
    validate_source_hash(
        lemma_index_path, str(source["lemma_index_sha256"]), label="lemma index"
    )
    problem_record = read_object(problem_path)
    problem = str(problem_record.get("claim") or "").strip()
    if not problem:
        raise ValueError(f"empty problem statement: {problem_path}")
    proof = proof_path.read_bytes().decode("utf-8")
    if not proof.strip():
        raise ValueError(f"empty proof: {proof_path}")
    lemma_index = read_object(lemma_index_path)
    units_by_id = {
        str(row["unit_id"]): dict(row) for row in lemma_index.get("units") or []
    }

    groups: list[dict[str, Any]] = []
    seen_group_ids: set[str] = set()
    for coarse in result.get("groups") or []:
        coarse_id = str(coarse["coarse_group_id"])
        for subgroup in coarse.get("subgroups") or []:
            local_id = str(subgroup["local_subgroup_id"])
            group_id = f"{coarse_id}.{local_id}"
            if group_id in seen_group_ids:
                raise ValueError(f"duplicate final group ID: {case_key}:{group_id}")
            seen_group_ids.add(group_id)
            ordered = [dict(row) for row in subgroup.get("ordered_packets") or []]
            nh_packets = [
                dict(row["packet"])
                for row in ordered
                if row.get("novelty_class") == "N"
                and row.get("checkability_tier") == "H"
            ]
            target_unit_ids: list[str] = []
            for row in ordered:
                packet = dict(row.get("packet") or {})
                for unit_id in packet.get("target_unit_ids") or []:
                    unit_id = str(unit_id)
                    if unit_id not in target_unit_ids:
                        target_unit_ids.append(unit_id)
            unit_hints = [units_by_id[unit_id] for unit_id in target_unit_ids if unit_id in units_by_id]
            groups.append(
                {
                    "group_id": group_id,
                    "coarse_group_id": coarse_id,
                    "local_subgroup_id": local_id,
                    "purpose": str(subgroup.get("purpose") or "").strip(),
                    "target_unit_ids": target_unit_ids,
                    "unit_hints": unit_hints,
                    "nh_packets": nh_packets,
                    "all_packet_count": len(ordered),
                }
            )
    if not groups:
        raise ValueError(f"no final groups in label result: {result_path}")
    p_key, candidate_id = case_key_parts(case_key)
    return {
        "case_key": case_key,
        "problem_key": p_key,
        "problem_id": str(problem_record.get("problem_id") or p_key),
        "candidate_id": candidate_id,
        "label_dir": str(label_root),
        "label_manifest_path": str(manifest_path),
        "label_manifest_sha256": file_sha256(manifest_path),
        "label_result_path": str(result_path),
        "label_result_sha256": file_sha256(result_path),
        "problem_path": str(problem_path),
        "problem_sha256": file_sha256(problem_path),
        "problem": problem,
        "proof_path": str(proof_path),
        "proof_sha256": file_sha256(proof_path),
        "proof": proof,
        "lemma_index_path": str(lemma_index_path),
        "lemma_index_sha256": file_sha256(lemma_index_path),
        "groups": groups,
    }


def render_unit_hints(group: dict[str, Any]) -> str:
    hints = []
    for unit in group["unit_hints"]:
        hints.append(
            f"- {unit['unit_id']} | {unit.get('kind', 'UNKNOWN')} | original "
            f"{unit.get('start_block', '?')}-{unit.get('end_block', '?')}: "
            f"{unit.get('says', '(no structural summary)')}"
        )
    return "\n".join(hints) if hints else "- (no routed unit hint)"


def render_nh_packets(group: dict[str, Any]) -> str:
    sections = []
    for index, packet in enumerate(group["nh_packets"], start=1):
        sections.append(
            f"### NH suggestion {index}\n"
            f"TYPE: {packet.get('type', 'UNKNOWN')}\n"
            f"TARGET HINT: {packet.get('target', '(none)')}\n"
            f"WHY ROUTED HERE: {packet.get('relevance_reason', '(none)')}\n"
            f"UNVERIFIED TRACE EXCERPT:\n{packet.get('exact_source_text', '')}"
        )
    if not sections:
        return (
            "(none; inspect the group purpose and current proof independently. "
            "Do not infer any hidden packet content.)"
        )
    return "\n\n".join(sections)


def group_patch_prompt(
    *, problem: str, proof: str, group: dict[str, Any], cycle: int
) -> str:
    return f"""You are conservatively refining one submitted Olympiad proof, one
mathematical repair group at a time. This is cumulative refinement cycle {cycle}.
This call is NH sub-batch {group.get('batch_index', 1)} of
{group.get('batch_count', 1)} for the current parent group. Later sub-batches see
the cumulative result of earlier sub-batches.

The current group can cover several lemma units and several non-adjacent passages.
Treat the group atomically: propose all mutually dependent edits together, or
return NO_CHANGE. You may propose at most {MAX_EDITS_PER_GROUP} disjoint contiguous
line replacements. Every byte outside those ranges will be preserved mechanically.
Do not make unrelated stylistic changes.

Every NH suggestion below is UNVERIFIED. N means only potentially novel and H
means only directly checkable; neither label means correct. Independently derive
every adopted claim from the original problem. Reject misleading, contradictory,
heuristic, or incomplete suggestions. If the current proof cannot be made strictly
more rigorous with a justified local change, return NO_CHANGE. Never weaken a sound
argument, invent a bridge, cite a suggestion, mention packets or reviewers, expose
line IDs in replacement text, or replace the entire proof.

Return one JSON object matching the supplied schema. For NO_CHANGE, set edits to
[] and briefly state why in verification_summary. For REPLACE, each edit names an
inclusive range of current line IDs and supplies the complete replacement passage
for exactly that range. Ranges must be disjoint and ordered. A replacement must be
self-contained relative to the unchanged surrounding proof. verification_summary
must concisely state what was independently checked; do not provide private
chain-of-thought.

ORIGINAL PROBLEM
{problem}

BLOCK-INDEXED CURRENT CUMULATIVE PROOF
{indexed_proof(proof)}

CURRENT GROUP PURPOSE
{group['purpose']}

ROUTED LEMMA-UNIT HINTS FROM THE ORIGINAL PROOF STRUCTURE
These are navigation hints, not verified mathematical facts. Current line numbers
above are authoritative because earlier cycles may have shifted the proof.
{render_unit_hints(group)}

NH-ONLY UNVERIFIED SUGGESTIONS
{render_nh_packets(group)}
"""


def prompt_audit(prompt: str, group: dict[str, Any]) -> dict[str, Any]:
    included = [str(row.get("exact_source_text") or "") for row in group["nh_packets"]]
    return {
        "fusion_supplied": False,
        "group_id_supplied_to_model": False,
        "group_purpose_supplied": group["purpose"] in prompt,
        "nh_packet_count": len(included),
        "nh_exact_text_occurrence_counts": [prompt.count(value) for value in included],
        "all_nh_exact_texts_supplied_once": all(prompt.count(value) == 1 for value in included),
        "non_nh_packet_text_supplied": False,
        "labels_are_explicitly_unverified": "Every NH suggestion below is UNVERIFIED" in prompt,
        "current_proof_sha256": sha256_text(group["_proof_for_audit"]),
    }


def normalize_and_validate_edits(
    *, proof: str, record: dict[str, Any]
) -> list[dict[str, Any]]:
    action = str(record.get("action") or "")
    raw_edits = [dict(row) for row in record.get("edits") or []]
    if action == "NO_CHANGE":
        if raw_edits:
            raise ValueError("NO_CHANGE must have no edits")
        return []
    if action != "REPLACE" or not raw_edits:
        raise ValueError("REPLACE must have at least one edit")
    if len(raw_edits) > MAX_EDITS_PER_GROUP:
        raise ValueError("too many edits")
    physical_lines = proof.splitlines(keepends=True)
    line_count = len(physical_lines)
    if not line_count:
        raise ValueError("cannot patch an empty proof")
    edits: list[dict[str, Any]] = []
    previous_end = 0
    replaced_line_count = 0
    for row in raw_edits:
        start = int(row["start_line"])
        end = int(row["end_line"])
        replacement = str(row["replacement"]).replace("\r\n", "\n").strip("\n")
        if not (1 <= start <= end <= line_count):
            raise ValueError(f"invalid edit range {start}-{end} for {line_count} lines")
        if start <= previous_end:
            raise ValueError("edits overlap or are not ordered")
        if not replacement.strip():
            raise ValueError("group refinement may not delete a passage")
        if TRACE_ID_PATTERN.search(replacement):
            raise ValueError("replacement leaked a trace packet ID")
        if any(marker in replacement for marker in TRANSPORT_MARKERS):
            raise ValueError("replacement leaked a transport marker")
        old_span = "".join(physical_lines[start - 1 : end])
        old_words = len(re.findall(r"\S+", old_span))
        replacement_words = len(re.findall(r"\S+", replacement))
        if replacement_words > max(240, old_words * 4 + 120):
            raise ValueError("replacement expands its local span excessively")
        edits.append(
            {
                "start_line": start,
                "end_line": end,
                "replacement": replacement,
                "old_span_sha256": sha256_text(old_span),
            }
        )
        previous_end = end
        replaced_line_count += end - start + 1
    if replaced_line_count >= line_count:
        raise ValueError("edits collectively replace the entire proof")
    if replaced_line_count > math.ceil(line_count * MAX_EDITED_LINE_FRACTION):
        raise ValueError("edits cover too much of the proof for a local group pass")
    return edits


def apply_atomic_edits(
    *, proof: str, edits: list[dict[str, Any]]
) -> tuple[str, dict[str, Any]]:
    if not edits:
        return proof, {
            "contract": "ATOMIC_MULTI_SPAN_REPLACEMENT_OR_NOOP",
            "edit_count": 0,
            "input_proof_sha256": sha256_text(proof),
            "output_proof_sha256": sha256_text(proof),
            "byte_identical_noop": True,
            "all_unedited_bytes_preserved": True,
        }
    lines = proof.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    updated = proof
    edit_audits: list[dict[str, Any]] = []
    for row in reversed(edits):
        start = int(row["start_line"])
        end = int(row["end_line"])
        start_offset = offsets[start - 1]
        end_offset = offsets[end]
        prefix = proof[:start_offset]
        old_span = proof[start_offset:end_offset]
        suffix = proof[end_offset:]
        replacement = str(row["replacement"])
        if (suffix or old_span.endswith(("\n", "\r"))) and not replacement.endswith(
            ("\n", "\r")
        ):
            replacement += "\n"
        if updated[:start_offset] != prefix:
            raise ValueError("a later edit unexpectedly changed an earlier prefix")
        current_suffix_start = end_offset
        current_old_span = updated[start_offset:current_suffix_start]
        if current_old_span != old_span:
            raise ValueError("atomic edit source span drift")
        updated = updated[:start_offset] + replacement + updated[current_suffix_start:]
        edit_audits.append(
            {
                "start_line": start,
                "end_line": end,
                "start_byte": start_offset,
                "end_byte": end_offset,
                "prefix_sha256": sha256_text(prefix),
                "old_span_sha256": sha256_text(old_span),
                "replacement_sha256": sha256_text(replacement),
                "suffix_sha256": sha256_text(suffix),
            }
        )
    # Reconstruct independently in ascending order to prove that only the named
    # spans changed. This also covers every unchanged gap between disjoint edits.
    parts: list[str] = []
    cursor = 0
    preserved_segments: list[dict[str, Any]] = []
    for row in edits:
        start_offset = offsets[int(row["start_line"]) - 1]
        end_offset = offsets[int(row["end_line"])]
        unchanged = proof[cursor:start_offset]
        parts.append(unchanged)
        preserved_segments.append(
            {
                "start_byte": cursor,
                "end_byte": start_offset,
                "sha256": sha256_text(unchanged),
            }
        )
        replacement = str(row["replacement"])
        old_span = proof[start_offset:end_offset]
        suffix_exists = end_offset < len(proof)
        if (suffix_exists or old_span.endswith(("\n", "\r"))) and not replacement.endswith(
            ("\n", "\r")
        ):
            replacement += "\n"
        parts.append(replacement)
        cursor = end_offset
    unchanged = proof[cursor:]
    parts.append(unchanged)
    preserved_segments.append(
        {"start_byte": cursor, "end_byte": len(proof), "sha256": sha256_text(unchanged)}
    )
    reconstructed = "".join(parts)
    if reconstructed != updated:
        raise ValueError("multi-span patch reconstruction mismatch")
    audit = {
        "contract": "ATOMIC_MULTI_SPAN_REPLACEMENT_OR_NOOP",
        "application_order": "descending_source_offset",
        "edit_count": len(edits),
        "input_proof_sha256": sha256_text(proof),
        "output_proof_sha256": sha256_text(updated),
        "byte_identical_noop": updated == proof,
        "all_unedited_bytes_preserved": True,
        "preserved_segments": preserved_segments,
        "edits": list(reversed(edit_audits)),
    }
    return updated, audit


def deterministic_artifact_audit(
    *, original_proof: str, refined_proof: str, stage_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    before = _artifact_metrics(original_proof)
    after = _artifact_metrics(refined_proof)
    lazy_delta = {
        key: int(after["lazy_connection_counts"][key])
        - int(before["lazy_connection_counts"][key])
        for key in after["lazy_connection_counts"]
    }
    deltas = {
        "character_count": int(after["character_count"])
        - int(before["character_count"]),
        "line_count": int(after["line_count"]) - int(before["line_count"]),
        "word_count": int(after["word_count"]) - int(before["word_count"]),
        "exact_duplicate_paragraph_count": int(
            after["exact_duplicate_paragraph_count"]
        )
        - int(before["exact_duplicate_paragraph_count"]),
        "repeated_12_word_span_count": int(after["repeated_12_word_span_count"])
        - int(before["repeated_12_word_span_count"]),
        "ending_conclusion_like_line_count": int(
            after["ending_conclusion_like_line_count"]
        )
        - int(before["ending_conclusion_like_line_count"]),
        "lazy_connection_counts": lazy_delta,
    }
    reasons: list[str] = []
    if any(after["transport_marker_hits"].values()):
        reasons.append("transport_marker_present")
    if deltas["exact_duplicate_paragraph_count"] > 0:
        reasons.append("new_exact_duplicate_paragraph")
    if deltas["repeated_12_word_span_count"] > 0:
        reasons.append("new_repeated_long_span")
    if deltas["ending_conclusion_like_line_count"] > 0:
        reasons.append("additional_conclusion_like_ending")
    if any(value > 0 for value in lazy_delta.values()):
        reasons.append("additional_lazy_connection_language")
    if before["word_count"] and after["word_count"] / before["word_count"] > 1.75:
        reasons.append("proof_word_count_growth_over_75_percent")
    if not all(bool(row["all_unedited_bytes_preserved"]) for row in stage_rows):
        reasons.append("patch_byte_preservation_failure")
    cleanup_reasons = {
        "new_exact_duplicate_paragraph",
        "new_repeated_long_span",
        "additional_conclusion_like_ending",
        "additional_lazy_connection_language",
        "proof_word_count_growth_over_75_percent",
    }
    return {
        "schema": "cognitive-well-v0165-deterministic-artifact-audit-v1",
        "state": "completed",
        "mutation_performed": False,
        "comparison_scope": "original_proof_to_post_cycle_pre_cleanup_proof",
        "before": before,
        "after": after,
        "deltas": deltas,
        "group_patch_preservation": {
            "stage_count": len(stage_rows),
            "all_unedited_bytes_preserved": all(
                bool(row["all_unedited_bytes_preserved"]) for row in stage_rows
            ),
        },
        "requires_attention": bool(reasons),
        "attention_reasons": reasons,
        "cleanup_triggered": bool(set(reasons) & cleanup_reasons),
        "cleanup_trigger_reasons": sorted(set(reasons) & cleanup_reasons),
        "semantic_equivalence_or_cleanup_attempted": False,
        "completed_at": utc_now(),
    }


def stage_input_digest(
    *, proof: str, group: dict[str, Any], cycle: int, max_tokens: int
) -> str:
    return stable_digest(
        {
            "harness_version": HARNESS_VERSION,
            "cycle": cycle,
            "group_id": group["group_id"],
            "purpose": group["purpose"],
            "target_unit_ids": group["target_unit_ids"],
            "batch_index": int(group.get("batch_index", 1)),
            "batch_count": int(group.get("batch_count", 1)),
            "nh_packet_sha256s": [
                str(row.get("exact_source_sha256") or sha256_text(str(row.get("exact_source_text") or "")))
                for row in group["nh_packets"]
            ],
            "input_proof_sha256": sha256_text(proof),
            "max_tokens": max_tokens,
        }
    )


def run_group_stage(
    *,
    runtime: ResilientModelRuntime,
    case: dict[str, Any],
    group: dict[str, Any],
    proof: str,
    cycle: int,
    group_index: int,
    stage_dir: Path,
    max_tokens: int,
    seed_namespace: str,
    retry_failed: bool,
) -> tuple[str, dict[str, Any]]:
    digest = stage_input_digest(
        proof=proof, group=group, cycle=cycle, max_tokens=max_tokens
    )
    summary_path = stage_dir / "summary.json"
    output_path = stage_dir / "proof.md"
    if summary_path.is_file():
        saved = read_object(summary_path)
        if saved.get("input_sha256") != digest:
            raise ValueError(f"refusing stage reuse after input drift: {stage_dir}")
        if saved.get("state") == "completed" and not (
            retry_failed and str(saved.get("outcome", "")).startswith("FAILED_CLOSED")
        ):
            output = output_path.read_bytes().decode("utf-8")
            if sha256_text(output) != saved.get("output_proof_sha256"):
                raise ValueError(f"saved stage proof hash drift: {output_path}")
            return output, saved

    stage_dir.mkdir(parents=True, exist_ok=True)
    prompt_group = dict(group)
    prompt_group["_proof_for_audit"] = proof
    prompt = group_patch_prompt(
        problem=case["problem"], proof=proof, group=prompt_group, cycle=cycle
    )
    audit = prompt_audit(prompt, prompt_group)
    if not audit["all_nh_exact_texts_supplied_once"]:
        raise ValueError("NH prompt inclusion audit failed")
    write_text_exact(stage_dir / "prompt.txt", prompt)
    write_json(stage_dir / "prompt_audit.json", audit)
    write_json(
        stage_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0165-group-stage-manifest-v1",
            "created_at": utc_now(),
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "group_index": group_index,
            "group_id": group["group_id"],
            "batch_index": int(group.get("batch_index", 1)),
            "batch_count": int(group.get("batch_count", 1)),
            "parent_nh_packet_count": int(
                group.get("parent_nh_packet_count", len(group["nh_packets"]))
            ),
            "purpose": group["purpose"],
            "target_unit_ids": group["target_unit_ids"],
            "nh_packet_count": len(group["nh_packets"]),
            "all_packet_count": group["all_packet_count"],
            "input_proof_sha256": sha256_text(proof),
            "policy": {
                "fusion_supplied": False,
                "nh_packet_text_only": True,
                "all_packets_unverified": True,
                "sub_batch_atomicity": "all_edits_or_no_edits",
                "maximum_disjoint_edits": MAX_EDITS_PER_GROUP,
                "unmodified_bytes_preserved": True,
                "fail_closed_to_input_proof": True,
            },
        },
    )
    try:
        record, generation = runtime.structured(
            role="gemma",
            prompt=prompt,
            destination=stage_dir / "model_call",
            stage="group_patch",
            schema=PATCH_SCHEMA,
            temperature=0.1,
            max_tokens=max_tokens,
            seed_label=(
                f"{seed_namespace}:{case['case_key']}:cycle-{cycle}:"
                f"group-{group_index}:{group['group_id']}:"
                f"batch-{group.get('batch_index', 1)}-of-{group.get('batch_count', 1)}"
            ),
            user_prompt="Return the conservative atomic group patch JSON now.",
        )
        edits = normalize_and_validate_edits(proof=proof, record=record)
        output, patch_audit = apply_atomic_edits(proof=proof, edits=edits)
        outcome = "NO_CHANGE" if not edits or output == proof else "APPLIED"
        write_json(stage_dir / "model_record.json", record)
        write_json(stage_dir / "patch_audit.json", patch_audit)
        summary = {
            "schema": "cognitive-well-v0165-group-stage-summary-v1",
            "state": "completed",
            "outcome": outcome,
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "group_index": group_index,
            "group_id": group["group_id"],
            "batch_index": int(group.get("batch_index", 1)),
            "batch_count": int(group.get("batch_count", 1)),
            "parent_nh_packet_count": int(
                group.get("parent_nh_packet_count", len(group["nh_packets"]))
            ),
            "nh_packet_count": len(group["nh_packets"]),
            "edit_count": len(edits),
            "input_proof_sha256": sha256_text(proof),
            "output_proof_sha256": sha256_text(output),
            "all_unedited_bytes_preserved": patch_audit["all_unedited_bytes_preserved"],
            "generation_metadata": generation.get("metadata"),
            "completed_at": utc_now(),
        }
    except Exception as error:
        output = proof
        summary = {
            "schema": "cognitive-well-v0165-group-stage-summary-v1",
            "state": "completed",
            "outcome": "FAILED_CLOSED_TO_INPUT_PROOF",
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "group_index": group_index,
            "group_id": group["group_id"],
            "batch_index": int(group.get("batch_index", 1)),
            "batch_count": int(group.get("batch_count", 1)),
            "parent_nh_packet_count": int(
                group.get("parent_nh_packet_count", len(group["nh_packets"]))
            ),
            "nh_packet_count": len(group["nh_packets"]),
            "edit_count": 0,
            "input_proof_sha256": sha256_text(proof),
            "output_proof_sha256": sha256_text(proof),
            "all_unedited_bytes_preserved": True,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
            "completed_at": utc_now(),
        }
    write_text_exact(output_path, output)
    write_json(summary_path, summary)
    return output, summary


def record_no_evidence_group_pass(
    *,
    case: dict[str, Any],
    group: dict[str, Any],
    proof: str,
    cycle: int,
    group_index: int,
    stage_dir: Path,
    max_tokens: int,
) -> tuple[str, dict[str, Any]]:
    """Record an exact no-op for a group with no NH evidence."""

    digest = stage_input_digest(
        proof=proof, group=group, cycle=cycle, max_tokens=max_tokens
    )
    stage_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        stage_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0165-no-evidence-group-pass-manifest-v1",
            "created_at": utc_now(),
            "input_sha256": digest,
            "case_key": case["case_key"],
            "cycle": cycle,
            "group_index": group_index,
            "group_id": group["group_id"],
            "purpose": group["purpose"],
            "nh_packet_count": 0,
            "model_call_performed": False,
            "decision": "SKIP_BECAUSE_GROUP_HAS_NO_NH_EVIDENCE",
            "prior_model_artifacts_in_this_directory_are_excluded": True,
        },
    )
    audit = {
        "contract": "DETERMINISTIC_NO_EVIDENCE_PASSTHROUGH",
        "edit_count": 0,
        "input_proof_sha256": sha256_text(proof),
        "output_proof_sha256": sha256_text(proof),
        "byte_identical_noop": True,
        "all_unedited_bytes_preserved": True,
        "model_call_performed": False,
    }
    write_json(stage_dir / "patch_audit.json", audit)
    write_text_exact(stage_dir / "proof.md", proof)
    summary = {
        "schema": "cognitive-well-v0165-group-stage-summary-v1",
        "state": "completed",
        "outcome": "SKIPPED_GROUP_HAS_NO_NH_EVIDENCE",
        "input_sha256": digest,
        "case_key": case["case_key"],
        "cycle": cycle,
        "group_index": group_index,
        "group_id": group["group_id"],
        "nh_packet_count": 0,
        "edit_count": 0,
        "model_call_performed": False,
        "input_proof_sha256": sha256_text(proof),
        "output_proof_sha256": sha256_text(proof),
        "all_unedited_bytes_preserved": True,
        "completed_at": utc_now(),
    }
    write_json(stage_dir / "summary.json", summary)
    return proof, summary


def split_nh_batches(group: dict[str, Any]) -> list[dict[str, Any]]:
    packets = list(group["nh_packets"])
    if not packets:
        return []
    batch_count = math.ceil(len(packets) / MAX_NH_PACKETS_PER_CALL)
    batches = []
    for batch_index, start in enumerate(
        range(0, len(packets), MAX_NH_PACKETS_PER_CALL), start=1
    ):
        batches.append(
            {
                **group,
                "nh_packets": packets[start : start + MAX_NH_PACKETS_PER_CALL],
                "batch_index": batch_index,
                "batch_count": batch_count,
                "parent_nh_packet_count": len(packets),
            }
        )
    if sum(len(batch["nh_packets"]) for batch in batches) != len(packets):
        raise ValueError("NH batching dropped a packet")
    original_ids = [str(packet["trace_id"]) for packet in packets]
    batched_ids = [
        str(packet["trace_id"])
        for batch in batches
        for packet in batch["nh_packets"]
    ]
    if batched_ids != original_ids or len(batched_ids) != len(set(batched_ids)):
        raise ValueError("NH batching changed order or packet multiplicity")
    if any(len(batch["nh_packets"]) > MAX_NH_PACKETS_PER_CALL for batch in batches):
        raise ValueError("NH batching exceeded the per-call cap")
    return batches


def run_case(
    *,
    runtime: ResilientModelRuntime,
    case: dict[str, Any],
    output_root: Path,
    cycles: int,
    max_tokens: int,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    retry_failed: bool,
) -> dict[str, Any]:
    case_dir = output_root / "cases" / case["problem_key"] / case["candidate_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        case_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0165-case-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": utc_now(),
            "case_key": case["case_key"],
            "problem_path": case["problem_path"],
            "problem_sha256": case["problem_sha256"],
            "original_proof_path": case["proof_path"],
            "original_proof_sha256": case["proof_sha256"],
            "label_result_path": case["label_result_path"],
            "label_result_sha256": case["label_result_sha256"],
            "lemma_index_path": case["lemma_index_path"],
            "lemma_index_sha256": case["lemma_index_sha256"],
            "cycle_count": cycles,
            "group_count": len(case["groups"]),
            "nh_packet_count": sum(len(group["nh_packets"]) for group in case["groups"]),
            "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
            "group_subpass_count_per_cycle": sum(
                max(
                    1,
                    math.ceil(
                        len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL
                    ),
                )
                for group in case["groups"]
            ),
            "fusion_stage": None,
            "schedule": "cycles_outer_groups_inner_cumulative",
            "zero_nh_group_policy": "deterministic_byte_identical_passthrough_without_model_call",
        },
    )
    proof = str(case["proof"])
    stage_rows: list[dict[str, Any]] = []
    subpasses_per_cycle = sum(
        max(1, math.ceil(len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL))
        for group in case["groups"]
    )
    total_stages = cycles * subpasses_per_cycle
    entire_proof_has_no_nh_evidence = not any(
        group["nh_packets"] for group in case["groups"]
    )
    completed = 0
    for cycle in range(1, cycles + 1):
        cycle_dir = case_dir / f"cycle_{cycle:02d}"
        cycle_input_sha256 = sha256_text(proof)
        cycle_rows = []
        for group_index, group in enumerate(case["groups"], start=1):
            write_json(
                case_dir / "status.json",
                {
                    "state": "running",
                    "stage": "groupwise_refinement",
                    "case_key": case["case_key"],
                    "cycle": cycle,
                    "group_index": group_index,
                    "group_count": len(case["groups"]),
                    "completed_group_subpasses": completed,
                    "total_group_subpasses": total_stages,
                    "updated_at": utc_now(),
                },
            )
            stage_dir = cycle_dir / f"group_{group_index:02d}_{group['group_id'].replace('.', '_')}"
            if not group["nh_packets"]:
                proof, row = record_no_evidence_group_pass(
                    case=case,
                    group=group,
                    proof=proof,
                    cycle=cycle,
                    group_index=group_index,
                    stage_dir=stage_dir,
                    max_tokens=max_tokens,
                )
                completed += 1
                stage_rows.append(row)
                group_row = row
            else:
                group_input_sha256 = sha256_text(proof)
                batch_rows: list[dict[str, Any]] = []
                batches = split_nh_batches(group)
                for batch in batches:
                    batch_index = int(batch["batch_index"])
                    write_json(
                        case_dir / "status.json",
                        {
                            "state": "running",
                            "stage": "groupwise_refinement",
                            "case_key": case["case_key"],
                            "cycle": cycle,
                            "group_index": group_index,
                            "group_count": len(case["groups"]),
                            "batch_index": batch_index,
                            "batch_count": len(batches),
                            "completed_group_subpasses": completed,
                            "total_group_subpasses": total_stages,
                            "updated_at": utc_now(),
                        },
                    )
                    batch_dir = (
                        stage_dir
                        if len(batches) == 1
                        else stage_dir
                        / "batches"
                        / f"batch_{batch_index:02d}_of_{len(batches):02d}"
                    )
                    proof, batch_row = run_group_stage(
                        runtime=runtime,
                        case=case,
                        group=batch,
                        proof=proof,
                        cycle=cycle,
                        group_index=group_index,
                        stage_dir=batch_dir,
                        max_tokens=max_tokens,
                        seed_namespace=seed_namespace,
                        retry_failed=retry_failed,
                    )
                    completed += 1
                    batch_rows.append(batch_row)
                    stage_rows.append(batch_row)
                failed_batch_count = sum(
                    str(batch_row["outcome"]).startswith("FAILED_CLOSED")
                    for batch_row in batch_rows
                )
                applied_batch_count = sum(
                    batch_row["outcome"] == "APPLIED" for batch_row in batch_rows
                )
                group_outcome = (
                    "APPLIED"
                    if applied_batch_count
                    else (
                        "FAILED_CLOSED_TO_INPUT_PROOF"
                        if failed_batch_count == len(batch_rows)
                        else "NO_CHANGE"
                    )
                )
                group_row = {
                    "schema": "cognitive-well-v0165-parent-group-summary-v1",
                    "state": "completed",
                    "outcome": group_outcome,
                    "case_key": case["case_key"],
                    "cycle": cycle,
                    "group_index": group_index,
                    "group_id": group["group_id"],
                    "nh_packet_count": len(group["nh_packets"]),
                    "batch_count": len(batch_rows),
                    "batch_packet_counts": [
                        int(batch_row["nh_packet_count"]) for batch_row in batch_rows
                    ],
                    "model_call_performed": True,
                    "model_call_count": len(batch_rows),
                    "applied_batch_count": applied_batch_count,
                    "failed_closed_batch_count": failed_batch_count,
                    "edit_count": sum(int(batch_row["edit_count"]) for batch_row in batch_rows),
                    "input_proof_sha256": group_input_sha256,
                    "output_proof_sha256": sha256_text(proof),
                    "all_unedited_bytes_preserved": all(
                        bool(batch_row["all_unedited_bytes_preserved"])
                        for batch_row in batch_rows
                    ),
                    "batches": batch_rows,
                    "completed_at": utc_now(),
                }
                if len(batches) > 1:
                    write_text_exact(stage_dir / "proof.md", proof)
                    write_json(stage_dir / "summary.json", group_row)
            cycle_rows.append(group_row)
        write_text_exact(cycle_dir / "proof.md", proof)
        write_json(
            cycle_dir / "summary.json",
            {
                "schema": "cognitive-well-v0165-cycle-summary-v1",
                "state": "completed",
                "case_key": case["case_key"],
                "cycle": cycle,
                "input_proof_sha256": cycle_input_sha256,
                "output_proof_sha256": sha256_text(proof),
                "groups": cycle_rows,
                "applied_count": sum(row["outcome"] == "APPLIED" for row in cycle_rows),
                "no_change_count": sum(row["outcome"] == "NO_CHANGE" for row in cycle_rows),
                "skipped_no_evidence_count": sum(
                    row["outcome"]
                    == "SKIPPED_GROUP_HAS_NO_NH_EVIDENCE"
                    for row in cycle_rows
                ),
                "failed_closed_count": sum(
                    int(
                        row.get(
                            "failed_closed_batch_count",
                            str(row["outcome"]).startswith("FAILED_CLOSED"),
                        )
                    )
                    for row in cycle_rows
                ),
                "all_unedited_bytes_preserved": all(
                    bool(row["all_unedited_bytes_preserved"]) for row in cycle_rows
                ),
                "completed_at": utc_now(),
            },
        )

    precleanup_path = case_dir / "pre_cleanup_proof.md"
    write_text_exact(precleanup_path, proof)
    audit_path = case_dir / "pre_cleanup_artifact_audit.json"
    artifact_audit = deterministic_artifact_audit(
        original_proof=str(case["proof"]),
        refined_proof=proof,
        stage_rows=stage_rows,
    )
    artifact_audit["packet_material_supplied_to_cleanup"] = False
    artifact_audit["fusion_material_supplied_to_cleanup"] = False
    write_json(audit_path, artifact_audit)
    write_json(
        case_dir / "status.json",
        {
            "state": "running",
            "stage": "final_deletion_only_cleanup",
            "case_key": case["case_key"],
            "completed_group_subpasses": completed,
            "total_group_subpasses": total_stages,
            "updated_at": utc_now(),
        },
    )
    cleanup = run_cleanup_gate(
        problem=case["problem"],
        problem_id=case["problem_id"],
        candidate_id=case["candidate_id"],
        cycle=cycles,
        proof_path=precleanup_path,
        artifact_audit_path=audit_path,
        output_dir=case_dir / "final_cleanup_deterministic_v0165",
        gemma_endpoint=gemma_endpoint,
        qwen_endpoint=qwen_endpoint,
        master_seed=master_seed,
        seed_namespace=f"{seed_namespace}:{case['case_key']}:final-cleanup",
        force=False,
    )
    final_path = Path(str(cleanup["proof_path"])).resolve()
    final_proof = final_path.read_text(encoding="utf-8")
    result = {
        "schema": "cognitive-well-v0165-case-result-v1",
        "state": "completed",
        "case_key": case["case_key"],
        "cycles": cycles,
        "group_count": len(case["groups"]),
        "scheduled_group_pass_count": cycles * len(case["groups"]),
        "group_subpass_count": len(stage_rows),
        "group_call_count": len(stage_rows),
        "group_model_call_count": sum(
            row.get("model_call_performed", True) is not False for row in stage_rows
        ),
        "entire_proof_had_no_nh_evidence": entire_proof_has_no_nh_evidence,
        "applied_count": sum(row["outcome"] == "APPLIED" for row in stage_rows),
        "no_change_count": sum(row["outcome"] == "NO_CHANGE" for row in stage_rows),
        "failed_closed_count": sum(
            str(row["outcome"]).startswith("FAILED_CLOSED") for row in stage_rows
        ),
        "all_group_passes_preserved_unedited_bytes": all(
            bool(row["all_unedited_bytes_preserved"]) for row in stage_rows
        ),
        "original_proof_path": case["proof_path"],
        "original_proof_sha256": case["proof_sha256"],
        "pre_cleanup_proof_path": str(precleanup_path.resolve()),
        "pre_cleanup_proof_sha256": sha256_text(proof),
        "cleanup_outcome": cleanup["outcome"],
        "artifact_cleanup_triggered": artifact_audit["cleanup_triggered"],
        "artifact_cleanup_trigger_reasons": artifact_audit[
            "cleanup_trigger_reasons"
        ],
        "cleanup_accepted": bool(cleanup.get("cleanup_accepted")),
        "cleanup_summary_path": str(
            (case_dir / "final_cleanup_deterministic_v0165/summary.json").resolve()
        ),
        "final_proof_path": str(final_path),
        "final_proof_sha256": sha256_text(final_proof.strip()),
        "completed_at": utc_now(),
    }
    write_json(case_dir / "result.json", result)
    write_json(
        case_dir / "status.json",
        {
            "state": "completed",
            "stage": "done",
            "case_key": case["case_key"],
            "completed_group_subpasses": completed,
            "total_group_subpasses": total_stages,
            "cleanup_outcome": cleanup["outcome"],
            "updated_at": utc_now(),
        },
    )
    return result


def dry_run(cases: list[dict[str, Any]]) -> dict[str, Any]:
    synthetic = "alpha\nbeta\ngamma\ndelta\n"
    edits = normalize_and_validate_edits(
        proof=synthetic,
        record={
            "action": "REPLACE",
            "edits": [
                {"start_line": 2, "end_line": 2, "replacement": "BETA"},
                {"start_line": 4, "end_line": 4, "replacement": "DELTA"},
            ],
            "verification_summary": "contract test",
        },
    )
    updated, audit = apply_atomic_edits(proof=synthetic, edits=edits)
    if updated != "alpha\nBETA\ngamma\nDELTA\n":
        raise ValueError("atomic multi-span contract test failed")
    rows = []
    for case in cases:
        for group in case["groups"]:
            for batch in split_nh_batches(group):
                prompt_group = dict(batch)
                prompt_group["_proof_for_audit"] = case["proof"]
                prompt = group_patch_prompt(
                    problem=case["problem"],
                    proof=case["proof"],
                    group=prompt_group,
                    cycle=1,
                )
                audit_row = prompt_audit(prompt, prompt_group)
                if not audit_row["all_nh_exact_texts_supplied_once"]:
                    raise ValueError(
                        f"NH prompt audit failed: {case['case_key']}:"
                        f"{group['group_id']}:batch-{batch['batch_index']}"
                    )
        rows.append(
            {
                "case_key": case["case_key"],
                "group_count": len(case["groups"]),
                "nh_packet_count": sum(len(group["nh_packets"]) for group in case["groups"]),
                "zero_nh_group_count": sum(not group["nh_packets"] for group in case["groups"]),
                "group_subpass_count_per_cycle": sum(
                    max(
                        1,
                        math.ceil(
                            len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL
                        ),
                    )
                    for group in case["groups"]
                ),
                "model_call_count_per_cycle": sum(
                    math.ceil(
                        len(group["nh_packets"]) / MAX_NH_PACKETS_PER_CALL
                    )
                    for group in case["groups"]
                    if group["nh_packets"]
                ),
            }
        )
    return {
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "case_count": len(cases),
        "group_count": sum(row["group_count"] for row in rows),
        "group_subpass_count_per_cycle": sum(
            row["group_subpass_count_per_cycle"] for row in rows
        ),
        "model_call_count_per_cycle": sum(
            row["model_call_count_per_cycle"] for row in rows
        ),
        "nh_packet_count": sum(row["nh_packet_count"] for row in rows),
        "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
        "atomic_multi_span_contract": audit,
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run NH-only atomic groupwise proof refinement and final cleanup"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=24_000)
    parser.add_argument("--thinking-token-budget", type=int, default=16_384)
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--master-seed", type=int, default=20260902)
    parser.add_argument("--seed-namespace", default="v0165:nh-max10-groupwise")
    parser.add_argument("--case", action="append", dest="case_keys")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.cycles < 1:
        raise ValueError("cycles must be positive")
    if args.max_concurrency < 1:
        raise ValueError("max concurrency must be positive")
    selected_keys = args.case_keys or list(DEFAULT_SELECTED_CASE_KEYS)
    unknown = sorted(set(selected_keys).difference(DEFAULT_CASES))
    if unknown:
        raise ValueError(f"unknown case keys: {unknown}")
    cases = [load_case(key, DEFAULT_CASES[key]) for key in selected_keys]
    validation = dry_run(cases)
    if args.dry_run:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return

    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    write_json(output_root / "preflight.json", validation)
    write_json(
        output_root / "manifest.json",
        {
            "schema": "cognitive-well-v0165-portfolio-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": utc_now(),
            "implementation_path": str(Path(__file__).resolve()),
            "implementation_sha256": file_sha256(Path(__file__).resolve()),
            "case_keys": selected_keys,
            "cycles": args.cycles,
            "group_count_per_cycle": validation["group_count"],
            "group_subpass_count_per_cycle": validation[
                "group_subpass_count_per_cycle"
            ],
            "total_group_subpasses": validation["group_subpass_count_per_cycle"]
            * args.cycles,
            "planned_group_model_calls": validation["model_call_count_per_cycle"]
            * args.cycles,
            "nh_packet_count_per_cycle": validation["nh_packet_count"],
            "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
            "gemma_endpoint": args.gemma_endpoint,
            "qwen_endpoint": args.qwen_endpoint,
            "gemma_model": GEMMA_MODEL,
            "qwen_model": QWEN_MODEL,
            "max_tokens": args.max_tokens,
            "thinking_token_budget": args.thinking_token_budget,
            "max_concurrency": args.max_concurrency,
            "master_seed": args.master_seed,
            "policy": {
                "fusion_guided_refinement": False,
                "packet_selection": "NH_ONLY",
                "all_packet_claims_unverified": True,
                "purpose_only_refinement": False,
                "zero_nh_group": "deterministic_passthrough_without_model_call",
                "large_nh_group_batching": "stable_existing_order_contiguous_chunks",
                "maximum_nh_packets_per_model_call": MAX_NH_PACKETS_PER_CALL,
                "every_nh_packet_consumed_exactly_once_per_cycle": True,
                "group_can_patch_multiple_lemma_units": True,
                "each_nh_sub_batch_edit_set_is_atomic": True,
                "all_unedited_bytes_preserved": True,
                "group_failure_fails_closed_to_input_proof": True,
                "cleanup": "deterministically_triggered_deletion_only_with_independent_preservation_audit",
            },
        },
    )
    runtime = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=args.gemma_endpoint.rstrip("/"),
            qwen_endpoint=args.qwen_endpoint.rstrip("/"),
            gemma_model=GEMMA_MODEL,
            qwen_model=QWEN_MODEL,
            master_seed=args.master_seed,
            thinking_token_budget=args.thinking_token_budget,
            reasoning_effort="max",
        )
    )
    status_lock = threading.Lock()
    completed_keys: list[str] = []
    failures: list[dict[str, str]] = []

    def root_status(stage: str) -> None:
        with status_lock:
            write_json(
                output_root / "status.json",
                {
                    "state": "running",
                    "stage": stage,
                    "completed_case_keys": sorted(completed_keys),
                    "completed_case_count": len(completed_keys),
                    "failed_cases": list(failures),
                    "case_count": len(cases),
                    "total_group_subpasses": validation[
                        "group_subpass_count_per_cycle"
                    ]
                    * args.cycles,
                    "planned_group_model_calls": validation[
                        "model_call_count_per_cycle"
                    ]
                    * args.cycles,
                    "updated_at": utc_now(),
                },
            )

    root_status("groupwise_refinement")
    results_by_key: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(args.max_concurrency, len(cases))
    ) as executor:
        futures = {
            executor.submit(
                run_case,
                runtime=runtime,
                case=case,
                output_root=output_root,
                cycles=args.cycles,
                max_tokens=args.max_tokens,
                gemma_endpoint=args.gemma_endpoint,
                qwen_endpoint=args.qwen_endpoint,
                master_seed=args.master_seed,
                seed_namespace=args.seed_namespace,
                retry_failed=args.retry_failed,
            ): case["case_key"]
            for case in cases
        }
        for future in concurrent.futures.as_completed(futures):
            case_key = futures[future]
            try:
                results_by_key[case_key] = future.result()
                completed_keys.append(case_key)
            except Exception as error:
                failures.append(
                    {
                        "case_key": case_key,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            root_status("groupwise_refinement")
    ordered_results = [results_by_key[key] for key in selected_keys if key in results_by_key]
    result = {
        "schema": "cognitive-well-v0165-portfolio-result-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed" if not failures else "completed_with_failures",
        "case_count": len(cases),
        "completed_case_count": len(ordered_results),
        "failed_cases": failures,
        "results": ordered_results,
        "total_group_calls": sum(row["group_call_count"] for row in ordered_results),
        "total_group_model_calls": sum(
            row["group_model_call_count"] for row in ordered_results
        ),
        "total_applied": sum(row["applied_count"] for row in ordered_results),
        "total_no_change": sum(row["no_change_count"] for row in ordered_results),
        "total_failed_closed": sum(row["failed_closed_count"] for row in ordered_results),
        "all_group_passes_preserved_unedited_bytes": all(
            row["all_group_passes_preserved_unedited_bytes"] for row in ordered_results
        ),
        "completed_at": utc_now(),
    }
    write_json(output_root / "result.json", result)
    write_json(
        output_root / "status.json",
        {
            "state": result["state"],
            "stage": "done",
            "completed_case_keys": [row["case_key"] for row in ordered_results],
            "completed_case_count": len(ordered_results),
            "failed_cases": failures,
            "case_count": len(cases),
            "total_group_calls": result["total_group_calls"],
            "updated_at": utc_now(),
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
