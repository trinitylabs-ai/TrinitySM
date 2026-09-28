from __future__ import annotations

import argparse
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
from cognitive_well_harness_v0_3_99_semantic_obligation_grouping_20260827 import (
    pipeline as v099,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
GEMMA_TEMPERATURE = 0.1
QWEN_TEMPERATURE = 0.1
ARCHIVE_STATUSES = {"CLOSED", "UNSUPPORTED"}
ACTIVE_STATUSES = {"OPEN", "UNCLOSED"}


CURRENT_GROUP_PROPOSAL_SYSTEM_PROMPT = r"""You are a conservative semantic
organizer of the current unresolved obligations in an olympiad proof ledger.

Every supplied entry has already been normalized to the terminal proof. Its
`current_issue` and `current_proof_location` are authoritative. Historical defect
wording and resolved objections have intentionally been withheld. Group entries only
when they identify the same current failed mathematical obligation in the same
logical scope and one localized repair would close every member.

Use the original problem and complete terminal proof only to interpret the current
issues. Do not solve, repair, re-grade, close, or discard an entry. Do not merge merely
because two issues concern the same theorem, section, object, technique, or downstream
conclusion. Keep a cause and a consequence separate when their repairs differ.

A concrete counterexample may join the general obligation it witnesses; label it
WITNESS. A broader report may join only when its current repair target is genuinely
the same; label it BROADER. Use SAME for equivalent reports. If one current_issue
explicitly contains multiple independent unresolved components, it may appear in
multiple groups and every such appearance must be COMPOUND_COMPONENT. Otherwise each
entry appears exactly once.

Return only compact Markdown. Repeat this exact block until every supplied obligation
ID is covered:

## Group
- Canonical obligation: <one atomic current obligation>
- Proof location: <the affected terminal-proof span or interface>
- Logical scope: <the assumptions and conclusion governed by this obligation>
- Minimum repair: <one repair that would close every member>
- Members: OB1:SAME, OB2:WITNESS
- Reason: <why these current reports have one repair target>

Use only supplied obligation IDs and relation labels SAME, WITNESS, BROADER, or
COMPOUND_COMPONENT. Keep each field on one physical line. Do not return JSON, fences,
scores, verdicts, or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Prefer separate singleton groups over a speculative merge."""


CURRENT_GROUP_AUDIT_SYSTEM_PROMPT = r"""You are the independent global auditor of
proposed semantic groups for current olympiad proof obligations. The original problem,
terminal proof, normalized current issues, and every proposed group are supplied.

For each proposal, decide whether one localized repair closes every member in the
same logical scope. You may KEEP it or SPLIT it into a complete partition. You may not
move different source entries between proposals, merge distinct proposals, drop an
entry, alter a status, solve the proof, or repair the mathematics.

Also compare proposals globally when the same source ID occurs in more than one group
as COMPOUND_COMPONENT. If a later partition repeats the same current component already
represented by an earlier proposal, mark it REDUNDANT_WITH the earliest such proposal.
Use REDUNDANT_WITH only when the two proposals share that source ID. Keep both when
they represent genuinely independent current components.

Return only compact Markdown, one block per proposal in supplied order:

## PG1
- Decision: KEEP
- Partitions: OB1, OB2
- Dispositions: KEEP
- Reason: <why one repair suffices>

or

## PG2
- Decision: SPLIT
- Partitions: OB3 || OB4
- Dispositions: KEEP || REDUNDANT_WITH PG1
- Reason: <why repairs differ and why any repeated component is redundant>

Every member must occur exactly once in its proposal partitions. KEEP has one
partition; SPLIT has at least two. Dispositions correspond one-for-one with partitions.
A REDUNDANT_WITH target must be an earlier proposal sharing at least one member ID.
Do not return JSON, fences, scores, verdicts, or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. When equivalence is uncertain, split and keep."""


AUDIT_BLOCK_RE = re.compile(
    r"(?ms)^##\s+(PG[0-9]+)\s*$\n(.*?)(?=^##\s+PG[0-9]+\s*$|\Z)"
)
REDUNDANT_RE = re.compile(r"^REDUNDANT_WITH\s+(PG[0-9]+)$")


def normalized_status(entry: dict[str, Any]) -> str:
    return str(entry.get("status") or "UNKNOWN").strip().upper()


def is_archived(entry: dict[str, Any]) -> bool:
    return normalized_status(entry) in ARCHIVE_STATUSES


def current_issue(entry: dict[str, Any]) -> tuple[str, str]:
    reason = v099.normalize_space(entry.get("status_reason") or "")
    if reason:
        return reason, "status_reason"
    defect = v099.normalize_space(entry.get("defect") or "")
    if defect:
        return defect, "historical_defect_fallback"
    raise ValueError(f"{entry.get('obligation_id')} has no current issue text")


def current_entry_packet(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for entry in entries:
        if is_archived(entry):
            raise ValueError("archived entry leaked into current issue packet")
        issue, basis = current_issue(entry)
        packets.append(
            {
                "obligation_id": str(entry["obligation_id"]),
                "source": entry.get("source"),
                "phase": entry.get("phase"),
                "status": normalized_status(entry),
                "current_issue": issue,
                "current_issue_basis": basis,
                "current_proof_location": v099.normalize_space(
                    entry.get("proof_location") or "(unspecified)"
                ),
            }
        )
    return packets


def split_source_entries(
    entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    active = [dict(entry) for entry in entries if not is_archived(entry)]
    archived = [dict(entry) for entry in entries if is_archived(entry)]
    if len(active) + len(archived) != len(entries):
        raise AssertionError("source entry split lost coverage")
    return active, archived


def proposal_user_prompt(
    *, problem: str, proof: str, entries: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE TERMINAL PROOF\n\n"
        + proof.strip()
        + "\n\n# CURRENT UNRESOLVED OBLIGATIONS\n\n"
        + json.dumps(current_entry_packet(entries), ensure_ascii=False, indent=2)
        + "\n\nGroup every current obligation now.\n"
    )


def audit_user_prompt(
    *,
    problem: str,
    proof: str,
    entries: list[dict[str, Any]],
    proposal_groups: list[dict[str, Any]],
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE TERMINAL PROOF\n\n"
        + proof.strip()
        + "\n\n# CURRENT UNRESOLVED OBLIGATIONS\n\n"
        + json.dumps(current_entry_packet(entries), ensure_ascii=False, indent=2)
        + "\n\n# ALL GEMMA PROPOSED GROUPS\n\n"
        + json.dumps(proposal_groups, ensure_ascii=False, indent=2)
        + "\n\nAudit every proposal and repeated compound component now.\n"
    )


def parse_dispositions(value: str) -> list[dict[str, str | None]]:
    rows: list[dict[str, str | None]] = []
    for raw in value.split("||"):
        token = v099.normalize_space(raw).upper()
        if token == "KEEP":
            rows.append({"disposition": "KEEP", "target": None})
            continue
        match = REDUNDANT_RE.fullmatch(token)
        if not match:
            raise ValueError(f"invalid partition disposition: {raw!r}")
        rows.append({"disposition": "REDUNDANT_WITH", "target": match.group(1)})
    if not rows:
        raise ValueError("audit has no dispositions")
    return rows


def validate_global_audit(
    *, audits: list[dict[str, Any]], proposal_groups: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    expected_ids = [str(group["proposal_group_id"]) for group in proposal_groups]
    actual_ids = [str(row["proposal_group_id"]) for row in audits]
    if actual_ids != expected_ids:
        raise ValueError(
            f"audit IDs/order changed: expected {expected_ids}, got {actual_ids}"
        )
    proposals = {
        str(group["proposal_group_id"]): {
            str(member["obligation_id"]) for member in group["members"]
        }
        for group in proposal_groups
    }
    proposal_order = {proposal_id: index for index, proposal_id in enumerate(expected_ids)}
    for audit in audits:
        proposal_id = str(audit["proposal_group_id"])
        partitions = audit["partitions"]
        dispositions = audit["dispositions"]
        expected_members = proposals[proposal_id]
        flattened = [item for partition in partitions for item in partition]
        if len(flattened) != len(set(flattened)) or set(flattened) != expected_members:
            raise ValueError(f"{proposal_id} is not an exact member partition")
        if audit["decision"] == "KEEP":
            if len(partitions) != 1:
                raise ValueError("KEEP must have one complete partition")
        elif len(partitions) < 2:
            raise ValueError("SPLIT must have at least two partitions")
        if len(dispositions) != len(partitions):
            raise ValueError(f"{proposal_id} dispositions do not align with partitions")
        for partition, disposition in zip(partitions, dispositions, strict=True):
            if disposition["disposition"] == "KEEP":
                continue
            target = str(disposition["target"])
            if target not in proposals:
                raise ValueError(f"{proposal_id} cites unknown redundancy target {target}")
            if proposal_order[target] >= proposal_order[proposal_id]:
                raise ValueError(
                    f"{proposal_id} redundancy target must be an earlier proposal"
                )
            if not (set(partition) & proposals[target]):
                raise ValueError(
                    f"{proposal_id} redundancy target {target} shares no source member"
                )
    kept_ids = {
        obligation_id
        for audit in audits
        for partition, disposition in zip(
            audit["partitions"], audit["dispositions"], strict=True
        )
        if disposition["disposition"] == "KEEP"
        for obligation_id in partition
    }
    expected_source_ids = set().union(*proposals.values()) if proposals else set()
    if kept_ids != expected_source_ids:
        missing = sorted(expected_source_ids - kept_ids)
        raise ValueError(f"redundancy dispositions removed source coverage: {missing}")
    return audits


def parse_global_audit(
    *, text: str, proposal_groups: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    required = {"decision", "partitions", "dispositions", "reason"}
    audits: list[dict[str, Any]] = []
    for proposal_id, body in AUDIT_BLOCK_RE.findall(text.strip()):
        fields = v099.parse_fields(body)
        if set(fields) != required:
            raise ValueError(
                f"audit fields differ: expected {sorted(required)}, got {sorted(fields)}"
            )
        decision = fields["decision"].upper()
        if decision not in {"KEEP", "SPLIT"}:
            raise ValueError(f"invalid audit decision: {decision}")
        audits.append(
            {
                "proposal_group_id": proposal_id,
                "decision": decision,
                "partitions": v099.parse_partition_list(fields["partitions"]),
                "dispositions": parse_dispositions(fields["dispositions"]),
                "reason": fields["reason"],
            }
        )
    if not audits:
        raise ValueError("no global audit blocks parsed")
    return validate_global_audit(audits=audits, proposal_groups=proposal_groups)


def run_gemma_proposal(
    *, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return v099.load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt = proposal_user_prompt(
        problem=case["problem"], proof=case["proof"], entries=case["active_entries"]
    )
    identity = v099.sha256_text(CURRENT_GROUP_PROPOSAL_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{case['case_id']}:current_group_proposal:{identity}"
    runtime = v084.runtime_for(endpoint, v099.stable_seed(label), GEMMA_MODEL)
    generated = runtime.text(
        role="gemma",
        prompt=CURRENT_GROUP_PROPOSAL_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"current_group_proposal_{identity}",
        temperature=GEMMA_TEMPERATURE,
        max_tokens=8_000,
        seed_label=label,
    )
    raw = str(generated["text"])
    recovery_mode = "primary"
    primary_error: str | None = None
    try:
        groups = v099.parse_group_proposal(
            text=raw, source_entries=case["active_entries"]
        )
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "format_retry"
        retry = runtime.text(
            role="gemma",
            prompt=CURRENT_GROUP_PROPOSAL_SYSTEM_PROMPT,
            user_prompt=v099._format_retry_prompt(
                task_prompt=prompt, malformed=raw, error=error
            ),
            destination=output_dir / "format_retry",
            stage=f"current_group_proposal_format_retry_{identity}",
            temperature=GEMMA_TEMPERATURE,
            max_tokens=6_000,
            seed_label=label + ":format_retry",
        )
        generated = retry
        groups = v099.parse_group_proposal(
            text=str(retry["text"]), source_entries=case["active_entries"]
        )
    result = {
        "schema": "cognitive-well-v0100-current-group-proposal-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "identity_sha256": v099.sha256_text(
            CURRENT_GROUP_PROPOSAL_SYSTEM_PROMPT + prompt
        ),
        "proposal_group_count": len(groups),
        "proposal_groups": groups,
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run_qwen_audit(
    *, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return v099.load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    proposals = case["proposal"]["proposal_groups"]
    prompt = audit_user_prompt(
        problem=case["problem"],
        proof=case["proof"],
        entries=case["active_entries"],
        proposal_groups=proposals,
    )
    identity = v099.sha256_text(CURRENT_GROUP_AUDIT_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{case['case_id']}:current_group_audit:{identity}"
    runtime = v084.runtime_for(endpoint, v099.stable_seed(label), QWEN_MODEL)
    generated = runtime.text(
        role="qwen",
        prompt=CURRENT_GROUP_AUDIT_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"current_group_audit_{identity}",
        temperature=QWEN_TEMPERATURE,
        max_tokens=6_000,
        seed_label=label,
    )
    raw = str(generated["text"])
    recovery_mode = "primary"
    primary_error: str | None = None
    try:
        audits = parse_global_audit(text=raw, proposal_groups=proposals)
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "format_retry"
        retry = runtime.text(
            role="qwen",
            prompt=CURRENT_GROUP_AUDIT_SYSTEM_PROMPT,
            user_prompt=v099._format_retry_prompt(
                task_prompt=prompt, malformed=raw, error=error
            ),
            destination=output_dir / "format_retry",
            stage=f"current_group_audit_format_retry_{identity}",
            temperature=QWEN_TEMPERATURE,
            max_tokens=4_000,
            seed_label=label + ":format_retry",
        )
        generated = retry
        audits = parse_global_audit(
            text=str(retry["text"]), proposal_groups=proposals
        )
    result = {
        "schema": "cognitive-well-v0100-current-group-audit-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "identity_sha256": v099.sha256_text(CURRENT_GROUP_AUDIT_SYSTEM_PROMPT + prompt),
        "audit_count": len(audits),
        "audits": audits,
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def representative_from_partition(
    *, partition: list[str], active_by_id: dict[str, dict[str, Any]]
) -> dict[str, str]:
    packets = {
        str(row["obligation_id"]): row
        for row in current_entry_packet(
            [active_by_id[obligation_id] for obligation_id in partition]
        )
    }
    representative = max(
        (packets[obligation_id] for obligation_id in partition),
        key=lambda row: (
            len(str(row["current_issue"])), str(row["obligation_id"])
        ),
    )
    locations = sorted(
        {str(packets[obligation_id]["current_proof_location"]) for obligation_id in partition}
    )
    issue = str(representative["current_issue"])
    return {
        "canonical_obligation": issue,
        "proof_location": " | ".join(locations),
        "logical_scope": "Current terminal-proof obligation represented by the cited members.",
        "minimum_repair": "Resolve the stated current issue at the cited proof location.",
    }


def build_archive(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        status = normalized_status(entry)
        if status not in ARCHIVE_STATUSES:
            raise ValueError("active entry leaked into archive")
        rows.append(
            {
                "archive_id": f"AR{index}",
                "obligation_id": str(entry["obligation_id"]),
                "disposition": status,
                "disposition_reason": v099.normalize_space(
                    entry.get("status_reason") or "(unspecified)"
                ),
                "proof_location": v099.normalize_space(
                    entry.get("proof_location") or "(unspecified)"
                ),
                "source": entry.get("source"),
                "phase": entry.get("phase"),
                "source_sha256": entry.get("sha256"),
                "historical_target": entry.get("target"),
                "historical_defect": entry.get("defect"),
                "historical_minimum_requirement": entry.get("minimum_requirement"),
            }
        )
    return rows


def materialize_current_ledger(case: dict[str, Any]) -> dict[str, Any]:
    active_entries = case["active_entries"]
    archived_entries = case["archived_entries"]
    active_by_id = {str(row["obligation_id"]): row for row in active_entries}
    proposals = case["proposal"]["proposal_groups"]
    audit_by_id = {
        str(row["proposal_group_id"]): row for row in case["audit"]["audits"]
    }
    groups: list[dict[str, Any]] = []
    redundancy_links: list[dict[str, Any]] = []
    for proposal in proposals:
        proposal_id = str(proposal["proposal_group_id"])
        audit = audit_by_id[proposal_id]
        relation_by_id = {
            str(member["obligation_id"]): str(member["relation"])
            for member in proposal["members"]
        }
        for partition_index, (partition, disposition) in enumerate(
            zip(audit["partitions"], audit["dispositions"], strict=True), start=1
        ):
            if disposition["disposition"] == "REDUNDANT_WITH":
                redundancy_links.append(
                    {
                        "source_proposal_group_id": proposal_id,
                        "source_partition_index": partition_index,
                        "members": partition,
                        "redundant_with_proposal_group_id": disposition["target"],
                        "audit_reason": audit["reason"],
                    }
                )
                continue
            complete = set(partition) == set(relation_by_id)
            if complete:
                canonical = {
                    key: proposal[key]
                    for key in (
                        "canonical_obligation",
                        "proof_location",
                        "logical_scope",
                        "minimum_repair",
                    )
                }
            else:
                canonical = representative_from_partition(
                    partition=partition, active_by_id=active_by_id
                )
            groups.append(
                {
                    "semantic_group_id": f"CG{len(groups) + 1}",
                    "source_proposal_group_id": proposal_id,
                    "source_partition_index": partition_index,
                    "audit_decision": audit["decision"],
                    **canonical,
                    "status": "ACTIVE_UNKNOWN"
                    if any(normalized_status(active_by_id[item]) not in ACTIVE_STATUSES for item in partition)
                    else "ACTIVE",
                    "member_count": len(partition),
                    "members": [
                        {
                            "obligation_id": obligation_id,
                            "relation": relation_by_id[obligation_id],
                            "source": active_by_id[obligation_id].get("source"),
                            "phase": active_by_id[obligation_id].get("phase"),
                            "source_status": normalized_status(active_by_id[obligation_id]),
                            "current_issue": current_issue(active_by_id[obligation_id])[0],
                            "current_proof_location": v099.normalize_space(
                                active_by_id[obligation_id].get("proof_location")
                                or "(unspecified)"
                            ),
                            "source_sha256": active_by_id[obligation_id].get("sha256"),
                        }
                        for obligation_id in partition
                    ],
                    "proposal_reason": proposal["reason"],
                    "audit_reason": audit["reason"],
                }
            )
    occurrences: dict[str, list[tuple[int, int]]] = {
        obligation_id: [] for obligation_id in active_by_id
    }
    for group_index, group in enumerate(groups):
        for member_index, member in enumerate(group["members"]):
            occurrences[str(member["obligation_id"])].append(
                (group_index, member_index)
            )
    missing = sorted(key for key, refs in occurrences.items() if not refs)
    if missing:
        raise ValueError(f"materialized current groups lost source coverage: {missing}")
    for obligation_id, refs in occurrences.items():
        for component_index, (group_index, member_index) in enumerate(refs, start=1):
            member = groups[group_index]["members"][member_index]
            member["component_id"] = (
                obligation_id if len(refs) == 1 else f"{obligation_id}.C{component_index}"
            )
            member["component_status"] = groups[group_index]["status"]
            member["component_current_obligation"] = groups[group_index][
                "canonical_obligation"
            ]
    archive = build_archive(archived_entries)
    source_ids = {str(row["obligation_id"]) for row in case["entries"]}
    active_ids = set(active_by_id)
    archive_ids = {str(row["obligation_id"]) for row in archived_entries}
    if active_ids & archive_ids or active_ids | archive_ids != source_ids:
        raise AssertionError("active/archive partitions are not an exact source partition")
    if any(
        member["source_status"] in ARCHIVE_STATUSES
        for group in groups
        for member in group["members"]
    ):
        raise AssertionError("archived status reactivated in current representative ledger")
    return {
        "schema": "cognitive-well-v0100-current-semantic-ledger-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "case_id": case["case_id"],
        "problem_id": case["problem_id"],
        "candidate_id": case["candidate_id"],
        "proof_path": case["proof_path"],
        "proof_sha256": case["proof_sha256"],
        "source_ledger_path": case["ledger_path"],
        "source_ledger_sha256": case["ledger_sha256"],
        "non_destructive_view": True,
        "source_entry_count": len(case["entries"]),
        "current_source_entry_count": len(active_entries),
        "archived_source_entry_count": len(archived_entries),
        "proposal_group_count": len(proposals),
        "current_representative_group_count": len(groups),
        "current_reduction_count": len(active_entries) - len(groups),
        "current_reduction_ratio": round(1 - len(groups) / len(active_entries), 6)
        if active_entries
        else 0.0,
        "current_representative_ledger": groups,
        "cross_group_redundancy_links": redundancy_links,
        "archival_ledger": archive,
        "source_entries": case["entries"],
    }


def run(
    *,
    source_run: Path,
    output_dir: Path,
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT,
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT,
    gemma_workers: int = 2,
    qwen_workers: int = 4,
    seed_namespace: str = "v0100",
    dry_run: bool = False,
) -> dict[str, Any]:
    source_run = source_run.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = v099.load_source_cases(source_run)
    for case in cases:
        case["active_entries"], case["archived_entries"] = split_source_entries(
            case["entries"]
        )
        if not case["active_entries"]:
            raise ValueError(f"{case['case_id']} has no current obligations to group")
    manifest = {
        "schema": "cognitive-well-v0100-current-semantic-ledger-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_run": str(source_run),
        "source_run_manifest_sha256": v099.file_sha256(source_run / "manifest.json"),
        "models": {"proposal": GEMMA_MODEL, "global_audit": QWEN_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "qwen_endpoint": qwen_endpoint,
            "gemma_workers": gemma_workers,
            "qwen_workers": qwen_workers,
            "reasoning_effort": "max",
        },
        "temperatures": {
            "gemma_current_group_proposal": GEMMA_TEMPERATURE,
            "qwen_global_group_audit": QWEN_TEMPERATURE,
        },
        "protocol": {
            "model_calls_per_candidate": 2,
            "grouping_basis": "status_reason_plus_proof_location",
            "historical_defect_in_model_prompt": False,
            "closed_and_unsupported_archived_before_grouping": True,
            "qwen_can_merge_distinct_proposals": False,
            "qwen_can_remove_repeated_compound_component": True,
            "compound_components_receive_independent_ids_and_statuses": True,
            "source_entries_are_immutable": True,
        },
        "problem_specific_prompting": False,
        "prompt_sha256": {
            "current_group_proposal": v099.sha256_text(
                CURRENT_GROUP_PROPOSAL_SYSTEM_PROMPT
            ),
            "current_group_audit": v099.sha256_text(CURRENT_GROUP_AUDIT_SYSTEM_PROMPT),
        },
        "cases": [
            {
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "ledger_path": case["ledger_path"],
                "ledger_sha256": case["ledger_sha256"],
                "source_entry_count": len(case["entries"]),
                "current_source_entry_count": len(case["active_entries"]),
                "archived_source_entry_count": len(case["archived_entries"]),
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    if dry_run:
        summary = {
            "schema": "cognitive-well-v0100-current-semantic-ledger-dry-run-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "case_count": len(cases),
            "source_entry_count": sum(len(case["entries"]) for case in cases),
            "current_source_entry_count": sum(
                len(case["active_entries"]) for case in cases
            ),
            "archived_source_entry_count": sum(
                len(case["archived_entries"]) for case in cases
            ),
            "planned_model_calls": {
                "gemma_current_group_proposals": len(cases),
                "qwen_global_group_audits": len(cases),
                "normal_total": 2 * len(cases),
            },
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(
            output_dir / "status.json",
            {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()},
        )
        return summary

    jobs = [{"case_id": case["case_id"], "case": case} for case in cases]
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "gemma_current_group_batch", "updated_at": utc_now()},
    )

    def proposal_task(job: dict[str, Any]) -> None:
        case = job["case"]
        case["proposal"] = run_gemma_proposal(
            case=case,
            endpoint=gemma_endpoint,
            output_dir=output_dir
            / "cases"
            / case["case_id"]
            / "01_gemma_current_group_proposal",
            seed_namespace=seed_namespace,
        )

    v099.run_parallel(
        name="gemma-current-proposal",
        jobs=jobs,
        workers=gemma_workers,
        task=proposal_task,
    )
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "qwen_global_group_audit_batch", "updated_at": utc_now()},
    )

    def audit_task(job: dict[str, Any]) -> None:
        case = job["case"]
        case_dir = output_dir / "cases" / case["case_id"]
        case["audit"] = run_qwen_audit(
            case=case,
            endpoint=qwen_endpoint,
            output_dir=case_dir / "02_qwen_global_group_audit",
            seed_namespace=seed_namespace,
        )
        case["current_ledger"] = materialize_current_ledger(case)
        write_json(
            case_dir / "current_semantic_obligation_ledger.json",
            case["current_ledger"],
        )

    v099.run_parallel(
        name="qwen-global-audit", jobs=jobs, workers=qwen_workers, task=audit_task
    )
    rows = [
        {
            "case_id": case["case_id"],
            "problem_id": case["problem_id"],
            "candidate_id": case["candidate_id"],
            "source_entry_count": case["current_ledger"]["source_entry_count"],
            "current_source_entry_count": case["current_ledger"][
                "current_source_entry_count"
            ],
            "archived_source_entry_count": case["current_ledger"][
                "archived_source_entry_count"
            ],
            "proposal_group_count": case["current_ledger"]["proposal_group_count"],
            "current_representative_group_count": case["current_ledger"][
                "current_representative_group_count"
            ],
            "current_reduction_count": case["current_ledger"][
                "current_reduction_count"
            ],
            "redundancy_link_count": len(
                case["current_ledger"]["cross_group_redundancy_links"]
            ),
            "ledger_path": str(
                (
                    output_dir
                    / "cases"
                    / case["case_id"]
                    / "current_semantic_obligation_ledger.json"
                ).resolve()
            ),
        }
        for case in cases
    ]
    summary = {
        "schema": "cognitive-well-v0100-current-semantic-ledger-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "case_count": len(cases),
        "source_entry_count": sum(row["source_entry_count"] for row in rows),
        "current_source_entry_count": sum(
            row["current_source_entry_count"] for row in rows
        ),
        "archived_source_entry_count": sum(
            row["archived_source_entry_count"] for row in rows
        ),
        "proposal_group_count": sum(row["proposal_group_count"] for row in rows),
        "current_representative_group_count": sum(
            row["current_representative_group_count"] for row in rows
        ),
        "current_reduction_count": sum(row["current_reduction_count"] for row in rows),
        "redundancy_link_count": sum(row["redundancy_link_count"] for row in rows),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "status.json",
        {"state": "completed", "stage": "done", "updated_at": utc_now()},
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Current-state semantic obligation ledger with separate archive"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--gemma-workers", type=int, default=2)
    parser.add_argument("--qwen-workers", type=int, default=4)
    parser.add_argument("--seed-namespace", default="v0100")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(
        source_run=args.source_run,
        output_dir=args.output_dir,
        gemma_endpoint=args.gemma_endpoint,
        qwen_endpoint=args.qwen_endpoint,
        gemma_workers=args.gemma_workers,
        qwen_workers=args.qwen_workers,
        seed_namespace=args.seed_namespace,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
