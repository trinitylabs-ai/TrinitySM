from __future__ import annotations

import concurrent.futures
import copy
import hashlib
import json
import re
import traceback
from pathlib import Path
from typing import Any

from .protocol import (
    parse_attack_line,
    parse_audit_line,
    parse_decision_tsv,
    render_decision_tsv,
    resolve_packet_decision,
)


HARNESS_VERSION = "v0.3.171-compact-whole-packet-ce-prescreen-20260903"
DEFAULT_MAX_CONCURRENCY = 8
DEFAULT_MAX_TOKENS = 32_768


ATTACK_PROMPT = """You are performing a cheap counterexample-first attack on one
complete unverified reasoning packet. Test the packet exactly as supplied; do not
split, summarize, rewrite, or improve it.

Try to find one explicit decisive reason that this PACKET is unsafe mathematical
evidence for refining the submitted proof. You are attacking the packet, not the
submitted proof. A valid challenge must contradict or invalidate a substantive
assertion made by the packet. It can be a concrete counterexample to the packet's
assertion, a false exact calculation inside the packet, an invalid witness proposed
by the packet, an unstated packet premise that fails in an explicit legal case, a
domain violation inside the packet, or a packet inference whose premises hold while
its conclusion fails.

Check the smallest legal cases, boundaries, equalities, signs, parity or residues,
simple symmetric and repeated configurations, and exact finite witnesses when they
apply. Do not challenge style, incompleteness alone, lack of proof alone, or a claim
merely because it looks suspicious. Do not use an illegal degenerate or limiting
object. If the packet identifies an error in the submitted proof and you confirm
that same error, the packet SURVIVES; agreement with the packet is not a challenge.
If the packet proposes a counterexample or defect, CHALLENGED requires showing that
the packet's proposed counterexample or defect diagnosis is itself false or invalid.

Return exactly one plain-text line with exactly three fields:
PACKET_ID | VERDICT | EXPLANATION

VERDICT must be SURVIVES or CHALLENGED. Use CHALLENGED only when the explanation
begins PACKET FLAW: and contains a complete explicit witness or decisive exact check
against the packet. SURVIVES means only that this bounded attack found no decisive
flaw in the packet; it does not certify the packet.
The explanation is mandatory, concise, and may not contain a pipe character.
Do not return JSON, Markdown, a code fence, a preface, or another line."""


AUDIT_PROMPT = """You are independently validating one proposed challenge to one
complete unverified reasoning packet. Recompute the decisive mathematics. You are
validating an attack on the packet, not an attack on the submitted proof. A valid
challenge must identify a substantive assertion or proposed witness in the packet
and give an explicit legal case or exact check showing that packet assertion or
witness is false or invalid. If the proposed challenge merely repeats, supports, or
confirms the packet's criticism of the submitted proof, return INVALID_CHALLENGE.
Also reject challenges based only on style, incompleteness, suspicion, an unstated
interpretation, an illegal degenerate case, or an attack on a different claim.

Return exactly one plain-text line with exactly three fields:
PACKET_ID | VERDICT | EXPLANATION

VERDICT must be VALID_CHALLENGE or INVALID_CHALLENGE. For VALID_CHALLENGE the
explanation must begin PACKET CLAIM FALSE: and state exactly which packet assertion
is false. The explanation is mandatory and concise. Do not return JSON, Markdown, a
code fence, a preface, or another line."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def safe_component(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    if not normalized:
        raise ValueError(f"unsafe empty path component derived from {value!r}")
    return normalized


def effective_generation_role(requested_role: str, metadata: dict[str, Any]) -> str:
    attempts = metadata.get("v071_recovery_attempts")
    if isinstance(attempts, list):
        accepted = [
            row
            for row in attempts
            if isinstance(row, dict)
            and str(row.get("status") or "").startswith("accepted")
        ]
        if accepted and str(accepted[-1].get("phase") or "") == "qwen_fallback":
            return "qwen"
    return requested_role


def collect_nh_packets(case: dict[str, Any]) -> list[dict[str, Any]]:
    """Return each whole NH packet once, preserving first group/order occurrence."""
    rows: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for group in case.get("groups") or []:
        group_id = str(group.get("group_id") or "")
        for packet in group.get("nh_packets") or []:
            packet_copy = copy.deepcopy(dict(packet))
            packet_id = str(packet_copy.get("trace_id") or "").strip()
            source_text = str(packet_copy.get("exact_source_text") or "")
            if not packet_id or not source_text.strip():
                raise ValueError("NH packet is missing trace_id or exact_source_text")
            recorded_hash = str(packet_copy.get("exact_source_sha256") or "")
            if recorded_hash and recorded_hash != sha256_text(source_text):
                raise ValueError(f"NH packet source hash drift: {packet_id}")
            existing = by_id.get(packet_id)
            if existing is not None:
                if existing["source_sha256"] != sha256_text(source_text):
                    raise ValueError(f"duplicate NH packet has source drift: {packet_id}")
                if group_id not in existing["group_ids"]:
                    existing["group_ids"].append(group_id)
                continue
            row = {
                "packet_id": packet_id,
                "packet": packet_copy,
                "source_text": source_text,
                "source_sha256": sha256_text(source_text),
                "group_ids": [group_id],
            }
            by_id[packet_id] = row
            rows.append(row)
    return rows


def attack_user_prompt(*, case: dict[str, Any], packet_row: dict[str, Any]) -> str:
    packet = packet_row["packet"]
    packet_id = packet_row["packet_id"]
    target_units = ",".join(str(v) for v in packet.get("target_unit_ids") or [])
    return f"""ORIGINAL PROBLEM
{str(case['problem']).strip()}

SUBMITTED PROOF
{str(case['proof']).strip()}

PACKET ID
{packet_id}

PACKET TYPE
{str(packet.get('type') or 'UNSPECIFIED')}

TARGET LEMMA UNITS
{target_units or 'UNSPECIFIED'}

COMPLETE PACKET TEXT
{packet_row['source_text']}

Return the required one-line verdict for {packet_id}."""


def audit_user_prompt(
    *, case: dict[str, Any], packet_row: dict[str, Any], attack: dict[str, str]
) -> str:
    packet = packet_row["packet"]
    packet_id = packet_row["packet_id"]
    return f"""ORIGINAL PROBLEM
{str(case['problem']).strip()}

SUBMITTED PROOF
{str(case['proof']).strip()}

PACKET ID
{packet_id}

PACKET TYPE
{str(packet.get('type') or 'UNSPECIFIED')}

COMPLETE PACKET TEXT
{packet_row['source_text']}

PROPOSED CHALLENGE
{attack['explanation']}

Return the required one-line independent verdict for {packet_id}."""


def _decision_checkpoint(
    *, packet_dir: Path, packet_id: str, input_sha256: str
) -> dict[str, str] | None:
    digest_path = packet_dir / "input.sha256"
    decision_path = packet_dir / "decision.tsv"
    if not digest_path.is_file() and not decision_path.is_file():
        return None
    if decision_path.is_file() and not digest_path.is_file():
        raise ValueError(f"incomplete packet prescreen checkpoint: {packet_dir}")
    if digest_path.read_text(encoding="utf-8").strip() != input_sha256:
        raise ValueError(f"packet prescreen checkpoint input drift: {packet_dir}")
    if not decision_path.is_file():
        return None
    rows = parse_decision_tsv(decision_path.read_text(encoding="utf-8"))
    if len(rows) != 1 or rows[0]["packet_id"] != packet_id:
        raise ValueError(f"invalid packet prescreen checkpoint decision: {packet_dir}")
    return rows[0]


def run_packet_prescreen(
    *,
    runtime: Any,
    case: dict[str, Any],
    packet_row: dict[str, Any],
    output_dir: Path,
    max_tokens: int,
    seed_namespace: str,
) -> dict[str, str]:
    packet_id = str(packet_row["packet_id"])
    packet_dir = output_dir / "packets" / safe_component(packet_id)
    digest = stable_digest(
        {
            "harness_version": HARNESS_VERSION,
            "case_key": case["case_key"],
            "problem_sha256": sha256_text(str(case["problem"])),
            "proof_sha256": sha256_text(str(case["proof"])),
            "packet_id": packet_id,
            "packet_source_sha256": packet_row["source_sha256"],
            "attack_prompt_sha256": sha256_text(ATTACK_PROMPT),
            "audit_prompt_sha256": sha256_text(AUDIT_PROMPT),
            "max_tokens": max_tokens,
            "seed_namespace": seed_namespace,
        }
    )
    saved = _decision_checkpoint(
        packet_dir=packet_dir, packet_id=packet_id, input_sha256=digest
    )
    if saved is not None:
        return saved

    write_text(packet_dir / "input.sha256", digest + "\n")
    attack_prompt = attack_user_prompt(case=case, packet_row=packet_row)
    attack_packet_section = f"COMPLETE PACKET TEXT\n{packet_row['source_text']}\n\n"
    if attack_prompt.count(attack_packet_section) != 1:
        raise ValueError(f"whole packet was not supplied exactly once: {packet_id}")
    write_text(packet_dir / "attack.user_prompt.txt", attack_prompt)

    attack: dict[str, str] | None = None
    audit: dict[str, str] | None = None
    independent_audit = False
    mechanical_explanation: str | None = None
    try:
        generation = runtime.text(
            role="gemma",
            prompt=ATTACK_PROMPT,
            user_prompt=attack_prompt,
            destination=packet_dir / "attack_model_call",
            stage="whole_packet_counterexample_attack",
            temperature=0.2,
            max_tokens=max_tokens,
            seed_label=f"{seed_namespace}:{case['case_key']}:{packet_id}:attack",
        )
        attack_text = str(generation.get("text") or "")
        write_text(packet_dir / "attack.verdict.txt", attack_text.strip() + "\n")
        attack = parse_attack_line(attack_text, expected_packet_id=packet_id)
        attack_role = effective_generation_role(
            "gemma", dict(generation.get("metadata") or {})
        )
    except Exception as error:
        write_text(packet_dir / "attack.error.txt", traceback.format_exc())
        mechanical_explanation = (
            f"Attack failed mechanically ({type(error).__name__}); "
            "no independently validated challenge."
        )
        attack_role = "unknown"

    if attack is not None and attack["verdict"] == "CHALLENGED":
        requested_audit_role = "qwen" if attack_role == "gemma" else "gemma"
        audit_prompt = audit_user_prompt(
            case=case, packet_row=packet_row, attack=attack
        )
        audit_packet_section = f"COMPLETE PACKET TEXT\n{packet_row['source_text']}\n\n"
        if audit_prompt.count(audit_packet_section) != 1:
            raise ValueError(f"whole audit packet was not supplied exactly once: {packet_id}")
        write_text(packet_dir / "audit.user_prompt.txt", audit_prompt)
        try:
            generation = runtime.text(
                role=requested_audit_role,
                prompt=AUDIT_PROMPT,
                user_prompt=audit_prompt,
                destination=packet_dir / "audit_model_call",
                stage="whole_packet_challenge_audit",
                temperature=0.1,
                max_tokens=max_tokens,
                seed_label=f"{seed_namespace}:{case['case_key']}:{packet_id}:audit",
            )
            audit_text = str(generation.get("text") or "")
            write_text(packet_dir / "audit.verdict.txt", audit_text.strip() + "\n")
            audit = parse_audit_line(audit_text, expected_packet_id=packet_id)
            audit_role = effective_generation_role(
                requested_audit_role, dict(generation.get("metadata") or {})
            )
            independent_audit = audit_role != attack_role
        except Exception as error:
            write_text(packet_dir / "audit.error.txt", traceback.format_exc())
            mechanical_explanation = (
                f"Challenge audit failed mechanically ({type(error).__name__}); "
                "packet remains active."
            )

    decision = resolve_packet_decision(
        packet_id=packet_id,
        attack=attack,
        audit=audit,
        independent_audit=independent_audit,
        mechanical_explanation=mechanical_explanation,
    )
    write_text(packet_dir / "decision.tsv", render_decision_tsv([decision]))
    return decision


def run_case_prescreen(
    *,
    runtime: Any,
    case: dict[str, Any],
    output_root: Path,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    seed_namespace: str = "v0171:compact-packet-ce1",
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    packet_rows = collect_nh_packets(case)
    case_dir = (
        output_root
        / safe_component(str(case["problem_key"]))
        / safe_component(str(case["candidate_id"]))
    )
    decisions_by_id: dict[str, dict[str, str]] = {}

    def work(packet_row: dict[str, Any]) -> dict[str, str]:
        return run_packet_prescreen(
            runtime=runtime,
            case=case,
            packet_row=packet_row,
            output_dir=case_dir,
            max_tokens=max_tokens,
            seed_namespace=seed_namespace,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = {executor.submit(work, row): row["packet_id"] for row in packet_rows}
        for future in concurrent.futures.as_completed(futures):
            decision = future.result()
            decisions_by_id[decision["packet_id"]] = decision

    decisions = [decisions_by_id[row["packet_id"]] for row in packet_rows]
    write_text(case_dir / "packet_status.tsv", render_decision_tsv(decisions))
    filtered = apply_packet_decisions(
        case,
        decisions,
        decision_path=case_dir / "packet_status.tsv",
        max_concurrency=max_concurrency,
    )
    return filtered, decisions


def apply_packet_decisions(
    case: dict[str, Any],
    decisions: list[dict[str, str]],
    *,
    decision_path: Path | None = None,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> dict[str, Any]:
    source_rows = collect_nh_packets(case)
    expected_ids = [row["packet_id"] for row in source_rows]
    decision_by_id = {str(row["packet_id"]): row for row in decisions}
    if len(decision_by_id) != len(decisions):
        raise ValueError("packet decisions contain duplicate IDs")
    if set(decision_by_id) != set(expected_ids):
        missing = sorted(set(expected_ids).difference(decision_by_id))
        outside = sorted(set(decision_by_id).difference(expected_ids))
        raise ValueError(
            f"packet decisions are not an exact NH partition: missing={missing}, outside={outside}"
        )
    filtered = copy.deepcopy(case)
    for group in filtered.get("groups") or []:
        active_packets = []
        for packet in group.get("nh_packets") or []:
            packet_id = str(packet["trace_id"])
            decision = decision_by_id[packet_id]
            if decision["status"] == "ACTIVE":
                active_packets.append(packet)
            elif decision["status"] == "INACTIVE":
                pass
            else:
                raise ValueError(f"unsupported packet decision status: {decision['status']}")
        group["nh_packets"] = active_packets
        group["ce1_active_packet_count"] = len(active_packets)
    # The normal routing contract partitions packets, but report unique counts so
    # duplicated provenance can never inflate the prescreen audit.
    unique_active = sum(row["status"] == "ACTIVE" for row in decisions)
    unique_inactive = sum(row["status"] == "INACTIVE" for row in decisions)
    filtered["nh_packet_prescreen"] = {
        "harness_version": HARNESS_VERSION,
        "policy": "whole_packet_deactivate_only_after_independent_valid_challenge",
        "input_packet_count": len(expected_ids),
        "active_packet_count": unique_active,
        "inactive_packet_count": unique_inactive,
        "decision_path": str(decision_path.resolve()) if decision_path else None,
        "max_concurrency": max_concurrency,
        "whole_packet_text_preserved": True,
        "atomicization": False,
        "model_output_format": "plain_text_three_fields",
    }
    return filtered
