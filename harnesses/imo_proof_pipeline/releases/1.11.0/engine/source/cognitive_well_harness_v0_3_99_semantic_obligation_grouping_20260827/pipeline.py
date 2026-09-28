from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import (
    pipeline as v084,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
GEMMA_TEMPERATURE = 0.1
QWEN_TEMPERATURE = 0.1
MEMBER_RELATIONS = {"SAME", "WITNESS", "BROADER", "COMPOUND_COMPONENT"}
ACTIVE_SOURCE_STATUSES = {"OPEN", "UNCLOSED"}
RESOLVED_SOURCE_STATUSES = {"CLOSED", "UNSUPPORTED"}


GROUP_PROPOSAL_SYSTEM_PROMPT = r"""You are a conservative semantic organizer of
an olympiad proof-obligation ledger. The supplied ledger entries are immutable audit
evidence. Group entries only when they identify the same failed mathematical
obligation in the same logical scope and one localized repair would close all of
them.

Use the original problem and complete proof to interpret wording, references, and
proof location. Do not solve, repair, re-grade, discard, or change the status of an
entry. Do not merge merely because two defects concern the same theorem, section,
object, technique, or downstream conclusion. Keep separate a cause and a consequence
when they require different repairs.

A concrete counterexample or boundary case may join the general obligation it
witnesses; label it WITNESS. A broader phrasing may join only when its minimum repair
is genuinely the same; label it BROADER. Use SAME for equivalent reports. If one
source entry explicitly contains several independent defects, it may appear in more
than one group and every such appearance must be COMPOUND_COMPONENT. Otherwise each
entry appears exactly once.

Return only compact Markdown. Repeat this exact block until every supplied obligation
ID is covered:

## Group
- Canonical obligation: <one atomic failed obligation>
- Proof location: <the affected proof span or interface>
- Logical scope: <the assumptions and conclusion governed by this obligation>
- Minimum repair: <one repair that would close every member>
- Members: OB1:SAME, OB2:WITNESS
- Reason: <why these reports have one repair target>

Use only supplied obligation IDs and relation labels SAME, WITNESS, BROADER, or
COMPOUND_COMPONENT. Keep each field on one physical line. Do not return JSON, fences,
scores, verdicts, or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Prefer separate singleton groups over a speculative merge."""


GROUP_AUDIT_SYSTEM_PROMPT = r"""You are an independent, conservative auditor of
proposed semantic groups in an olympiad proof-obligation ledger. The original ledger
entries are immutable. For each proposed group, decide whether one localized repair
really closes every member in the same logical scope.

You may KEEP a proposal or SPLIT it into a complete partition of its members. You may
not move members between proposal groups, merge across proposals, drop an entry, add
an entry, alter a source status, solve the proof, or repair the mathematics. Split
whenever reports require distinct arguments, concern distinct quantifier/case scopes,
or merely form a cause-and-consequence chain. A specific witness may remain with the
general defect it directly demonstrates.

Return only compact Markdown, one block for every proposal in the supplied order:

## PG1
- Decision: KEEP
- Partitions: OB1, OB2
- Reason: <why one repair suffices>

or

## PG1
- Decision: SPLIT
- Partitions: OB1, OB2 || OB3
- Reason: <why the repairs differ>

Every proposal member must occur exactly once in its partitions. KEEP has exactly one
partition containing the whole proposal. SPLIT has at least two nonempty partitions.
Do not return JSON, fences, scores, verdicts, or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. When equivalence is uncertain, split."""


PROPOSAL_BLOCK_RE = re.compile(
    r"(?ms)^##\s+Group\s*$\n(.*?)(?=^##\s+Group\s*$|\Z)"
)
AUDIT_BLOCK_RE = re.compile(
    r"(?ms)^##\s+(PG[0-9]+)\s*$\n(.*?)(?=^##\s+PG[0-9]+\s*$|\Z)"
)
FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_seed(label: str) -> int:
    value = int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:4], "big")
    return value or 1


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def normalize_space(value: str) -> str:
    return " ".join(str(value).split())


def parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        match = FIELD_RE.match(line)
        if not match:
            raise ValueError(f"invalid compact Markdown field: {line!r}")
        key = normalize_space(match.group(1)).lower().replace(" ", "_")
        if key in fields:
            raise ValueError(f"duplicate field: {key}")
        value = match.group(2).strip()
        if not value:
            raise ValueError(f"empty field: {key}")
        fields[key] = value
    return fields


def parse_member_list(value: str) -> list[dict[str, str]]:
    members: list[dict[str, str]] = []
    for raw in value.split(","):
        token = raw.strip()
        if not token:
            continue
        if ":" not in token:
            raise ValueError(f"member lacks relation: {token!r}")
        obligation_id, relation = [part.strip() for part in token.rsplit(":", 1)]
        relation = relation.upper()
        if not re.fullmatch(r"OB[0-9]+", obligation_id):
            raise ValueError(f"invalid obligation ID: {obligation_id!r}")
        if relation not in MEMBER_RELATIONS:
            raise ValueError(f"invalid member relation: {relation!r}")
        members.append({"obligation_id": obligation_id, "relation": relation})
    if not members:
        raise ValueError("group has no members")
    ids = [row["obligation_id"] for row in members]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate member inside group: {ids}")
    return members


def validate_proposal_groups(
    *, groups: list[dict[str, Any]], source_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    expected = [str(row["obligation_id"]) for row in source_entries]
    if len(expected) != len(set(expected)):
        raise ValueError("source ledger has duplicate obligation IDs")
    expected_set = set(expected)
    occurrences: dict[str, list[str]] = {obligation_id: [] for obligation_id in expected}
    member_sets: set[tuple[str, ...]] = set()
    for index, group in enumerate(groups, start=1):
        group["proposal_group_id"] = f"PG{index}"
        member_ids = [str(row["obligation_id"]) for row in group["members"]]
        unknown = sorted(set(member_ids) - expected_set)
        if unknown:
            raise ValueError(f"PG{index} contains unknown IDs: {unknown}")
        key = tuple(sorted(member_ids))
        if key in member_sets:
            raise ValueError(f"duplicate proposal member set: {key}")
        member_sets.add(key)
        for member in group["members"]:
            occurrences[str(member["obligation_id"])].append(str(member["relation"]))
    missing = [obligation_id for obligation_id, refs in occurrences.items() if not refs]
    if missing:
        raise ValueError(f"proposal omitted source IDs: {missing}")
    for obligation_id, relations in occurrences.items():
        if len(relations) > 1 and any(
            relation != "COMPOUND_COMPONENT" for relation in relations
        ):
            raise ValueError(
                f"multiply grouped {obligation_id} must use COMPOUND_COMPONENT everywhere"
            )
    if len(groups) > 2 * len(source_entries):
        raise ValueError("proposal has implausibly many groups")
    return groups


def parse_group_proposal(
    *, text: str, source_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    required = {
        "canonical_obligation",
        "proof_location",
        "logical_scope",
        "minimum_repair",
        "members",
        "reason",
    }
    groups: list[dict[str, Any]] = []
    for body in PROPOSAL_BLOCK_RE.findall(text.strip()):
        fields = parse_fields(body)
        if set(fields) != required:
            raise ValueError(
                f"proposal fields differ: expected {sorted(required)}, got {sorted(fields)}"
            )
        groups.append(
            {
                key: value for key, value in fields.items() if key != "members"
            }
            | {"members": parse_member_list(fields["members"])}
        )
    if not groups:
        raise ValueError("no semantic proposal groups parsed")
    return validate_proposal_groups(groups=groups, source_entries=source_entries)


def parse_partition_list(value: str) -> list[list[str]]:
    partitions: list[list[str]] = []
    for raw_partition in value.split("||"):
        ids = [token.strip() for token in raw_partition.split(",") if token.strip()]
        if not ids:
            raise ValueError("empty audit partition")
        if any(not re.fullmatch(r"OB[0-9]+", item) for item in ids):
            raise ValueError(f"invalid audit partition: {ids}")
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate member in audit partition: {ids}")
        partitions.append(ids)
    return partitions


def validate_group_audit(
    *, audits: list[dict[str, Any]], proposal_groups: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    expected_ids = [str(group["proposal_group_id"]) for group in proposal_groups]
    actual_ids = [str(row["proposal_group_id"]) for row in audits]
    if actual_ids != expected_ids:
        raise ValueError(
            f"audit proposal IDs/order changed: expected {expected_ids}, got {actual_ids}"
        )
    for audit, proposal in zip(audits, proposal_groups, strict=True):
        expected = [str(row["obligation_id"]) for row in proposal["members"]]
        flattened = [item for partition in audit["partitions"] for item in partition]
        if len(flattened) != len(set(flattened)):
            raise ValueError(f"{audit['proposal_group_id']} repeats a member")
        if set(flattened) != set(expected):
            raise ValueError(
                f"{audit['proposal_group_id']} partitions are not an exact member partition"
            )
        if audit["decision"] == "KEEP":
            if len(audit["partitions"]) != 1 or set(flattened) != set(expected):
                raise ValueError("KEEP must preserve the complete proposal as one group")
        elif len(audit["partitions"]) < 2:
            raise ValueError("SPLIT must create at least two partitions")
    return audits


def parse_group_audit(
    *, text: str, proposal_groups: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    required = {"decision", "partitions", "reason"}
    audits: list[dict[str, Any]] = []
    for proposal_id, body in AUDIT_BLOCK_RE.findall(text.strip()):
        fields = parse_fields(body)
        if set(fields) != required:
            raise ValueError(
                f"audit fields differ: expected {sorted(required)}, got {sorted(fields)}"
            )
        decision = fields["decision"].upper()
        if decision not in {"KEEP", "SPLIT"}:
            raise ValueError(f"invalid audit decision: {decision!r}")
        audits.append(
            {
                "proposal_group_id": proposal_id,
                "decision": decision,
                "partitions": parse_partition_list(fields["partitions"]),
                "reason": fields["reason"],
            }
        )
    if not audits:
        raise ValueError("no semantic audit blocks parsed")
    return validate_group_audit(audits=audits, proposal_groups=proposal_groups)


def source_entry_packet(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "obligation_id",
        "source",
        "phase",
        "status",
        "target",
        "defect",
        "minimum_requirement",
        "proof_location",
        "status_reason",
    )
    return [{key: row.get(key) for key in keys} for row in entries]


def proposal_user_prompt(
    *, problem: str, proof: str, entries: list[dict[str, Any]]
) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + problem.strip()
        + "\n\n# COMPLETE TERMINAL PROOF\n\n"
        + proof.strip()
        + "\n\n# IMMUTABLE OBLIGATION LEDGER\n\n"
        + json.dumps(source_entry_packet(entries), ensure_ascii=False, indent=2)
        + "\n\nGroup the obligations now.\n"
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
        + "\n\n# IMMUTABLE OBLIGATION LEDGER\n\n"
        + json.dumps(source_entry_packet(entries), ensure_ascii=False, indent=2)
        + "\n\n# GEMMA PROPOSED GROUPS\n\n"
        + json.dumps(proposal_groups, ensure_ascii=False, indent=2)
        + "\n\nAudit every proposed group now.\n"
    )


def load_problem(path: Path) -> str:
    payload = load_json(path)
    for key in ("claim", "problem", "statement", "text"):
        value = str(payload.get(key) or "").strip()
        if value:
            return value
    raise ValueError(f"problem JSON has no supported statement field: {path}")


def load_source_cases(source_run: Path) -> list[dict[str, Any]]:
    source_run = source_run.resolve()
    manifest_path = source_run / "manifest.json"
    summary_path = source_run / "summary.json"
    if not manifest_path.is_file() or not summary_path.is_file():
        raise ValueError(f"source run lacks manifest/summary: {source_run}")
    manifest = load_json(manifest_path)
    summary = load_json(summary_path)
    if summary.get("state") != "completed":
        raise ValueError(f"source run is not completed: {source_run}")
    if not str(manifest.get("schema") or "").startswith("cognitive-well-v098-"):
        raise ValueError("v0.3.99 currently consumes a completed v0.3.98 ledger")
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in manifest.get("cases") or []:
        case_id = str(raw.get("case_id") or "").strip()
        if not case_id or case_id in seen:
            raise ValueError(f"missing or duplicate source case_id: {case_id!r}")
        seen.add(case_id)
        problem_path = Path(str(raw["problem_path"])).resolve()
        proof_path = Path(str(raw["proof_path"])).resolve()
        ledger_path = source_run / "cases" / case_id / "updated_obligation_ledger.json"
        for path in (problem_path, proof_path, ledger_path):
            if not path.is_file():
                raise FileNotFoundError(path)
        proof = proof_path.read_text(encoding="utf-8").strip()
        # v0.3.98 binds proofs after trimming transport-only leading/trailing
        # whitespace, rather than hashing the raw Markdown file bytes.
        if sha256_text(proof) != str(raw["proof_sha256"]):
            raise ValueError(f"proof hash drift for {case_id}")
        ledger = load_json(ledger_path)
        entries = [dict(row) for row in ledger.get("entries") or []]
        if len(entries) != int(ledger.get("entry_count", -1)):
            raise ValueError(f"invalid updated ledger cardinality for {case_id}")
        active_entries = [dict(row) for row in ledger.get("active_obligations") or []]
        if len(active_entries) != int(ledger.get("active_count", -1)):
            raise ValueError(f"invalid active-ledger cardinality for {case_id}")
        if any(row not in entries for row in active_entries):
            raise ValueError(f"active ledger is not a subset of entries for {case_id}")
        if str(ledger.get("proof_sha256")) != str(raw["proof_sha256"]):
            raise ValueError(f"ledger/proof binding mismatch for {case_id}")
        cases.append(
            {
                "case_id": case_id,
                "problem_id": str(raw["problem_id"]),
                "candidate_id": str(raw["candidate_id"]),
                "problem_path": str(problem_path),
                "problem": load_problem(problem_path),
                "proof_path": str(proof_path),
                "proof": proof,
                "proof_sha256": str(raw["proof_sha256"]),
                "ledger_path": str(ledger_path.resolve()),
                "ledger_sha256": file_sha256(ledger_path),
                "source_ledger": ledger,
                "entries": entries,
            }
        )
    if not cases:
        raise ValueError("source run has no cases")
    return cases


def run_parallel(
    *, name: str, jobs: list[dict[str, Any]], workers: int, task: Callable[[dict[str, Any]], None]
) -> None:
    errors: list[tuple[str, BaseException]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, workers), thread_name_prefix=f"v099-{name}"
    ) as pool:
        futures = {pool.submit(task, job): str(job["case_id"]) for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except BaseException as error:
                errors.append((futures[future], error))
    if errors:
        detail = "; ".join(
            f"{case_id}: {type(error).__name__}: {error}" for case_id, error in errors
        )
        raise RuntimeError(f"{name} batch failed: {detail}")


def _format_retry_prompt(*, task_prompt: str, malformed: str, error: Exception) -> str:
    return (
        task_prompt
        + "\n\n# MALFORMED PREVIOUS RESPONSE\n\n"
        + malformed
        + "\n\n# FORMAT ERROR\n\n"
        + f"{type(error).__name__}: {error}"
        + "\n\nReturn the complete corrected compact Markdown record only. Preserve the "
        "mathematical classifications unless needed to satisfy the stated invariants.\n"
    )


def run_gemma_proposal(
    *, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt = proposal_user_prompt(
        problem=case["problem"], proof=case["proof"], entries=case["entries"]
    )
    identity = sha256_text(GROUP_PROPOSAL_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{case['case_id']}:semantic_group_proposal:{identity}"
    runtime = v084.runtime_for(endpoint, stable_seed(label), GEMMA_MODEL)
    generated = runtime.text(
        role="gemma",
        prompt=GROUP_PROPOSAL_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"semantic_group_proposal_{identity}",
        temperature=GEMMA_TEMPERATURE,
        max_tokens=8_000,
        seed_label=label,
    )
    raw = str(generated["text"])
    recovery_mode = "primary"
    primary_error: str | None = None
    try:
        groups = parse_group_proposal(text=raw, source_entries=case["entries"])
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "format_retry"
        retry = runtime.text(
            role="gemma",
            prompt=GROUP_PROPOSAL_SYSTEM_PROMPT,
            user_prompt=_format_retry_prompt(
                task_prompt=prompt, malformed=raw, error=error
            ),
            destination=output_dir / "format_retry",
            stage=f"semantic_group_proposal_format_retry_{identity}",
            temperature=GEMMA_TEMPERATURE,
            max_tokens=6_000,
            seed_label=label + ":format_retry",
        )
        generated = retry
        raw = str(retry["text"])
        groups = parse_group_proposal(text=raw, source_entries=case["entries"])
    result = {
        "schema": "cognitive-well-v099-semantic-group-proposal-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "identity_sha256": sha256_text(GROUP_PROPOSAL_SYSTEM_PROMPT + prompt),
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
        return load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    proposals = case["proposal"]["proposal_groups"]
    prompt = audit_user_prompt(
        problem=case["problem"],
        proof=case["proof"],
        entries=case["entries"],
        proposal_groups=proposals,
    )
    identity = sha256_text(GROUP_AUDIT_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{case['case_id']}:semantic_group_audit:{identity}"
    runtime = v084.runtime_for(endpoint, stable_seed(label), QWEN_MODEL)
    generated = runtime.text(
        role="qwen",
        prompt=GROUP_AUDIT_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"semantic_group_audit_{identity}",
        temperature=QWEN_TEMPERATURE,
        max_tokens=6_000,
        seed_label=label,
    )
    raw = str(generated["text"])
    recovery_mode = "primary"
    primary_error: str | None = None
    try:
        audits = parse_group_audit(text=raw, proposal_groups=proposals)
    except Exception as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "format_retry"
        retry = runtime.text(
            role="qwen",
            prompt=GROUP_AUDIT_SYSTEM_PROMPT,
            user_prompt=_format_retry_prompt(
                task_prompt=prompt, malformed=raw, error=error
            ),
            destination=output_dir / "format_retry",
            stage=f"semantic_group_audit_format_retry_{identity}",
            temperature=QWEN_TEMPERATURE,
            max_tokens=4_000,
            seed_label=label + ":format_retry",
        )
        generated = retry
        raw = str(retry["text"])
        audits = parse_group_audit(text=raw, proposal_groups=proposals)
    result = {
        "schema": "cognitive-well-v099-semantic-group-audit-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "identity_sha256": sha256_text(GROUP_AUDIT_SYSTEM_PROMPT + prompt),
        "audit_count": len(audits),
        "audits": audits,
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def group_status(members: list[dict[str, Any]]) -> str:
    statuses = {str(member.get("status") or "UNKNOWN").upper() for member in members}
    if statuses & ACTIVE_SOURCE_STATUSES:
        return "ACTIVE"
    if statuses == {"CLOSED"}:
        return "CLOSED"
    if statuses == {"UNSUPPORTED"}:
        return "UNSUPPORTED"
    if statuses and statuses <= RESOLVED_SOURCE_STATUSES:
        return "MIXED_RESOLVED"
    return "ACTIVE_UNKNOWN"


def _representative_entry(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        entries,
        key=lambda row: (
            len(normalize_space(row.get("minimum_requirement") or "")),
            len(normalize_space(row.get("target") or "")),
            str(row.get("obligation_id") or ""),
        ),
    )


def materialize_semantic_ledger(case: dict[str, Any]) -> dict[str, Any]:
    entries = case["entries"]
    entry_by_id = {str(row["obligation_id"]): row for row in entries}
    proposals = case["proposal"]["proposal_groups"]
    proposal_by_id = {str(row["proposal_group_id"]): row for row in proposals}
    audit_by_id = {
        str(row["proposal_group_id"]): row for row in case["audit"]["audits"]
    }
    groups: list[dict[str, Any]] = []
    for proposal in proposals:
        proposal_id = str(proposal["proposal_group_id"])
        audit = audit_by_id[proposal_id]
        relation_by_id = {
            str(row["obligation_id"]): str(row["relation"])
            for row in proposal["members"]
        }
        for partition_index, partition in enumerate(audit["partitions"], start=1):
            member_entries = [entry_by_id[obligation_id] for obligation_id in partition]
            complete_proposal = set(partition) == set(relation_by_id)
            if complete_proposal:
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
                representative = _representative_entry(member_entries)
                locations = sorted(
                    {
                        normalize_space(row.get("proof_location") or "(unspecified)")
                        for row in member_entries
                    }
                )
                canonical = {
                    "canonical_obligation": normalize_space(
                        representative.get("target")
                        or representative.get("minimum_requirement")
                        or representative.get("defect")
                    ),
                    "proof_location": " | ".join(locations),
                    "logical_scope": normalize_space(
                        representative.get("target") or representative.get("defect")
                    ),
                    "minimum_repair": normalize_space(
                        representative.get("minimum_requirement")
                        or representative.get("defect")
                    ),
                }
            members = [
                {
                    "obligation_id": obligation_id,
                    "relation": relation_by_id[obligation_id],
                    "source": entry_by_id[obligation_id].get("source"),
                    "phase": entry_by_id[obligation_id].get("phase"),
                    "source_status": entry_by_id[obligation_id].get("status"),
                    "source_sha256": entry_by_id[obligation_id].get("sha256"),
                }
                for obligation_id in partition
            ]
            groups.append(
                {
                    "semantic_group_id": f"SG{len(groups) + 1}",
                    "source_proposal_group_id": proposal_id,
                    "source_partition_index": partition_index,
                    "audit_decision": audit["decision"],
                    **canonical,
                    "status": group_status(member_entries),
                    "member_count": len(members),
                    "members": members,
                    "proposal_reason": proposal["reason"],
                    "audit_reason": audit["reason"],
                }
            )
    source_ids = {str(row["obligation_id"]) for row in entries}
    grouped_ids = {
        str(member["obligation_id"])
        for group in groups
        for member in group["members"]
    }
    if grouped_ids != source_ids:
        raise AssertionError("materialized semantic groups lost source coverage")
    active_groups = [
        group for group in groups if group["status"] in {"ACTIVE", "ACTIVE_UNKNOWN"}
    ]
    active_entries = [
        row for row in entries if str(row.get("status") or "").upper() in ACTIVE_SOURCE_STATUSES
    ]
    return {
        "schema": "cognitive-well-v099-semantic-grouped-obligation-ledger-v1",
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
        "source_entry_count": len(entries),
        "source_active_entry_count": len(active_entries),
        "proposal_group_count": len(proposals),
        "final_group_count": len(groups),
        "active_group_count": len(active_groups),
        "all_entry_reduction_count": len(entries) - len(groups),
        "active_reduction_count": len(active_entries) - len(active_groups),
        "all_entry_reduction_ratio": round(1 - len(groups) / len(entries), 6),
        "active_reduction_ratio": (
            round(1 - len(active_groups) / len(active_entries), 6)
            if active_entries
            else 0.0
        ),
        "semantic_groups": groups,
        "active_semantic_groups": active_groups,
        "source_entries": entries,
    }


def run(
    *,
    source_run: Path,
    output_dir: Path,
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT,
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT,
    gemma_workers: int = 2,
    qwen_workers: int = 4,
    seed_namespace: str = "v099",
    dry_run: bool = False,
) -> dict[str, Any]:
    source_run = source_run.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_source_cases(source_run)
    manifest = {
        "schema": "cognitive-well-v099-semantic-grouping-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_run": str(source_run),
        "source_run_manifest_sha256": file_sha256(source_run / "manifest.json"),
        "models": {"proposal": GEMMA_MODEL, "audit": QWEN_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "qwen_endpoint": qwen_endpoint,
            "gemma_workers": gemma_workers,
            "qwen_workers": qwen_workers,
            "reasoning_effort": "max",
        },
        "temperatures": {
            "gemma_group_proposal": GEMMA_TEMPERATURE,
            "qwen_split_only_audit": QWEN_TEMPERATURE,
        },
        "protocol": {
            "merge_requires_two_model_agreement": True,
            "qwen_can_merge_across_proposals": False,
            "source_entries_are_immutable": True,
            "grouping_is_non_destructive_view": True,
            "unknown_or_unresolved_status_is_active": True,
        },
        "problem_specific_prompting": False,
        "prompt_sha256": {
            "group_proposal": sha256_text(GROUP_PROPOSAL_SYSTEM_PROMPT),
            "group_audit": sha256_text(GROUP_AUDIT_SYSTEM_PROMPT),
        },
        "cases": [
            {
                key: case[key]
                for key in (
                    "case_id",
                    "problem_id",
                    "candidate_id",
                    "problem_path",
                    "proof_path",
                    "proof_sha256",
                    "ledger_path",
                    "ledger_sha256",
                )
            }
            | {"source_entry_count": len(case["entries"])}
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    if dry_run:
        summary = {
            "schema": "cognitive-well-v099-semantic-grouping-dry-run-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "case_count": len(cases),
            "source_entry_count": sum(len(case["entries"]) for case in cases),
            "planned_model_calls": {
                "gemma_group_proposals": len(cases),
                "qwen_split_only_audits": len(cases),
                "format_retries_max": 2 * len(cases),
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
        {"state": "running", "stage": "gemma_group_proposal_batch", "updated_at": utc_now()},
    )

    def proposal_task(job: dict[str, Any]) -> None:
        case = job["case"]
        case_dir = output_dir / "cases" / case["case_id"]
        case["proposal"] = run_gemma_proposal(
            case=case,
            endpoint=gemma_endpoint,
            output_dir=case_dir / "01_gemma_group_proposal",
            seed_namespace=seed_namespace,
        )

    run_parallel(
        name="gemma-proposal", jobs=jobs, workers=gemma_workers, task=proposal_task
    )
    write_json(
        output_dir / "status.json",
        {"state": "running", "stage": "qwen_split_only_audit_batch", "updated_at": utc_now()},
    )

    def audit_task(job: dict[str, Any]) -> None:
        case = job["case"]
        case_dir = output_dir / "cases" / case["case_id"]
        case["audit"] = run_qwen_audit(
            case=case,
            endpoint=qwen_endpoint,
            output_dir=case_dir / "02_qwen_split_only_audit",
            seed_namespace=seed_namespace,
        )
        case["semantic_ledger"] = materialize_semantic_ledger(case)
        write_json(
            case_dir / "semantic_grouped_obligation_ledger.json",
            case["semantic_ledger"],
        )

    run_parallel(name="qwen-audit", jobs=jobs, workers=qwen_workers, task=audit_task)
    rows = [
        {
            "case_id": case["case_id"],
            "problem_id": case["problem_id"],
            "candidate_id": case["candidate_id"],
            "source_entry_count": case["semantic_ledger"]["source_entry_count"],
            "source_active_entry_count": case["semantic_ledger"][
                "source_active_entry_count"
            ],
            "proposal_group_count": case["semantic_ledger"]["proposal_group_count"],
            "final_group_count": case["semantic_ledger"]["final_group_count"],
            "active_group_count": case["semantic_ledger"]["active_group_count"],
            "all_entry_reduction_count": case["semantic_ledger"][
                "all_entry_reduction_count"
            ],
            "active_reduction_count": case["semantic_ledger"][
                "active_reduction_count"
            ],
            "ledger_path": str(
                (
                    output_dir
                    / "cases"
                    / case["case_id"]
                    / "semantic_grouped_obligation_ledger.json"
                ).resolve()
            ),
        }
        for case in cases
    ]
    summary = {
        "schema": "cognitive-well-v099-semantic-grouping-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "case_count": len(cases),
        "source_entry_count": sum(row["source_entry_count"] for row in rows),
        "source_active_entry_count": sum(
            row["source_active_entry_count"] for row in rows
        ),
        "proposal_group_count": sum(row["proposal_group_count"] for row in rows),
        "final_group_count": sum(row["final_group_count"] for row in rows),
        "active_group_count": sum(row["active_group_count"] for row in rows),
        "all_entry_reduction_count": sum(
            row["all_entry_reduction_count"] for row in rows
        ),
        "active_reduction_count": sum(row["active_reduction_count"] for row in rows),
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
        description="Conservative two-model semantic grouping for final obligation ledgers"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--gemma-workers", type=int, default=2)
    parser.add_argument("--qwen-workers", type=int, default=4)
    parser.add_argument("--seed-namespace", default="v099")
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
