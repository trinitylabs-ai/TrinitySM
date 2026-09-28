from __future__ import annotations

import re
from typing import Any, Iterable


PACKET_ID = re.compile(r"[A-Za-z0-9_-]+")
ATTACK_VERDICTS = frozenset({"SURVIVES", "CHALLENGED"})
AUDIT_VERDICTS = frozenset({"VALID_CHALLENGE", "INVALID_CHALLENGE"})
FINAL_STATUSES = frozenset({"ACTIVE", "INACTIVE"})
DECISION_HEADER = "packet_id\tstatus\texplanation"
MAX_EXPLANATION_CHARS = 2_400


def _single_plain_line(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("model returned an empty verdict")
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) == 2 and lines[0] == "PACKET_ID | VERDICT | EXPLANATION":
        stripped = lines[1]
    elif len(lines) != 1:
        raise ValueError("verdict must occupy exactly one physical line")
    if stripped.startswith("```") or stripped.endswith("```"):
        raise ValueError("Markdown fences are not allowed")
    if stripped.startswith("{") or stripped.startswith("["):
        raise ValueError("JSON output is not allowed")
    return stripped


def _parse_verdict_line(
    text: str, *, expected_packet_id: str, allowed_verdicts: frozenset[str]
) -> dict[str, str]:
    line = _single_plain_line(text)
    # Split only the two protocol delimiters. Mathematical explanations often
    # contain a set-builder bar such as {x | g(x)=a}; that bar is content, not a
    # fourth transport field.
    fields = line.split(" | ", 2)
    if len(fields) != 3:
        raise ValueError(
            "verdict must contain exactly PACKET_ID | VERDICT | EXPLANATION"
        )
    packet_id, verdict, explanation = (field.strip() for field in fields)
    if PACKET_ID.fullmatch(packet_id) is None:
        raise ValueError(f"invalid packet ID: {packet_id!r}")
    if packet_id != expected_packet_id:
        raise ValueError(
            f"verdict packet mismatch: expected {expected_packet_id}, got {packet_id}"
        )
    if verdict not in allowed_verdicts:
        raise ValueError(f"unsupported verdict: {verdict!r}")
    if not explanation:
        raise ValueError("verdict explanation must be nonempty")
    if len(explanation) > MAX_EXPLANATION_CHARS:
        raise ValueError("verdict explanation exceeds the compact output bound")
    if verdict == "CHALLENGED" and not explanation.startswith("PACKET FLAW:"):
        raise ValueError("CHALLENGED explanation must begin PACKET FLAW:")
    if verdict == "VALID_CHALLENGE" and not explanation.startswith(
        "PACKET CLAIM FALSE:"
    ):
        raise ValueError(
            "VALID_CHALLENGE explanation must begin PACKET CLAIM FALSE:"
        )
    return {
        "packet_id": packet_id,
        "verdict": verdict,
        "explanation": explanation,
    }


def parse_attack_line(text: str, *, expected_packet_id: str) -> dict[str, str]:
    return _parse_verdict_line(
        text,
        expected_packet_id=expected_packet_id,
        allowed_verdicts=ATTACK_VERDICTS,
    )


def parse_audit_line(text: str, *, expected_packet_id: str) -> dict[str, str]:
    return _parse_verdict_line(
        text,
        expected_packet_id=expected_packet_id,
        allowed_verdicts=AUDIT_VERDICTS,
    )


def resolve_packet_decision(
    *,
    packet_id: str,
    attack: dict[str, str] | None,
    audit: dict[str, str] | None,
    independent_audit: bool,
    mechanical_explanation: str | None = None,
) -> dict[str, str]:
    """Deactivate only after a valid independently produced challenge."""
    if attack is None:
        explanation = mechanical_explanation or (
            "Attack unavailable; no independently validated challenge."
        )
        return {"packet_id": packet_id, "status": "ACTIVE", "explanation": explanation}
    if attack["packet_id"] != packet_id:
        raise ValueError("attack decision belongs to another packet")
    if attack["verdict"] == "SURVIVES":
        return {
            "packet_id": packet_id,
            "status": "ACTIVE",
            "explanation": attack["explanation"],
        }
    if audit is None:
        explanation = mechanical_explanation or (
            "Challenge was not independently validated; packet remains active."
        )
        return {"packet_id": packet_id, "status": "ACTIVE", "explanation": explanation}
    if audit["packet_id"] != packet_id:
        raise ValueError("audit decision belongs to another packet")
    if audit["verdict"] == "VALID_CHALLENGE" and independent_audit:
        return {
            "packet_id": packet_id,
            "status": "INACTIVE",
            "explanation": audit["explanation"],
        }
    if not independent_audit:
        return {
            "packet_id": packet_id,
            "status": "ACTIVE",
            "explanation": (
                "Challenge lacked a different effective-model audit; packet remains active."
            ),
        }
    return {
        "packet_id": packet_id,
        "status": "ACTIVE",
        "explanation": audit["explanation"],
    }


def _clean_tsv_field(value: Any) -> str:
    return re.sub(r"[\t\r\n]+", " ", str(value)).strip()


def render_decision_tsv(rows: Iterable[dict[str, Any]]) -> str:
    lines = [DECISION_HEADER]
    seen: set[str] = set()
    for row in rows:
        packet_id = _clean_tsv_field(row.get("packet_id", ""))
        status = _clean_tsv_field(row.get("status", ""))
        explanation = _clean_tsv_field(row.get("explanation", ""))
        if PACKET_ID.fullmatch(packet_id) is None:
            raise ValueError(f"invalid packet ID in decision: {packet_id!r}")
        if packet_id in seen:
            raise ValueError(f"duplicate packet decision: {packet_id}")
        if status not in FINAL_STATUSES:
            raise ValueError(f"invalid packet status: {status!r}")
        if not explanation:
            raise ValueError("packet decision explanation must be nonempty")
        seen.add(packet_id)
        lines.append(f"{packet_id}\t{status}\t{explanation}")
    return "\n".join(lines) + "\n"


def parse_decision_tsv(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    if not lines or lines[0] != DECISION_HEADER:
        raise ValueError("invalid packet decision TSV header")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in lines[1:]:
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != 3:
            raise ValueError("packet decision TSV rows must have exactly three fields")
        packet_id, status, explanation = fields
        if PACKET_ID.fullmatch(packet_id) is None:
            raise ValueError(f"invalid packet ID in TSV: {packet_id!r}")
        if packet_id in seen:
            raise ValueError(f"duplicate packet ID in TSV: {packet_id}")
        if status not in FINAL_STATUSES:
            raise ValueError(f"invalid packet status in TSV: {status!r}")
        if not explanation.strip():
            raise ValueError("packet decision TSV explanation must be nonempty")
        seen.add(packet_id)
        rows.append(
            {
                "packet_id": packet_id,
                "status": status,
                "explanation": explanation.strip(),
            }
        )
    return rows
