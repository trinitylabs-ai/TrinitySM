"""Deterministic gates for Markdown replacement audits; no model or grade access."""
from __future__ import annotations

import hashlib
import re

ACCEPT = "ACCEPT_CANDIDATE"
KEEP = "KEEP_BASELINE"
VERSION = "post-resolver-mechanical-validation-v2"


def validate_audit(text: str, case: dict) -> dict:
    """Validate the audit record, not the mathematics it describes.

    An invalid record cannot authorize replacement. The caller must separately
    bind the supplied case metadata to the actual proof and response bytes.
    """
    errors, normalizations = [], []
    expected_ids = [item["id"] for item in case["changes"]]
    if not expected_ids or len(set(expected_ids)) != len(expected_ids):
        errors.append("Invalid expected changed-block IDs")
    for key in ("baseline_sha256", "candidate_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", case[key]):
            errors.append("Invalid expected " + key)
    # Only the parser's copy is normalized; the original response is preserved.
    lines = [re.sub(r"^[-*]\s+", "", line.strip().replace("**", "").replace("`", ""))
             for line in text.splitlines()]
    normalized = "\n".join(lines)

    def field(name, body=normalized):
        values = re.findall(r"^" + re.escape(name) + r"\s*:\s*(.*?)\s*$", body, re.M | re.I)
        if len(values) != 1:
            errors.append("Expected exactly one " + name)
            return None
        return values[0]

    decision = field("Decision")
    if decision not in (ACCEPT, KEEP):
        errors.append("Invalid decision")
    # Model-echoed hashes are diagnostic only. Actual proof/request/response
    # identity is verified by bindings.verify_audit_binding before adoption.
    reported_hashes, warnings = {}, []
    for key, name in (("baseline_sha256", "Baseline SHA256"), ("candidate_sha256", "Candidate SHA256")):
        values = re.findall(r"^" + re.escape(name) + r"\s*:\s*(.*?)\s*$", normalized, re.M | re.I)
        reported_hashes[key] = values
        if values != [case[key]]:
            warnings.append(name + " echo is missing, malformed or mismatched; excluded from verdict validation")
    sections = {}
    for match in re.finditer(r"^##\s+([^\n]+)\n(.*?)(?=^##\s|\Z)", normalized, re.M | re.S):
        name, body = match.groups()
        name = name.lower().strip()
        if name in sections:
            errors.append("Duplicate section: " + name)
        sections[name] = body.strip()
    checks = {}
    for name, allowed, accepting in (
        ("Target obligation", ("CLOSED", "OPEN", "UNRESOLVED"), "CLOSED"),
        ("Preserved valid progress", ("PRESERVED", "LOST", "UNRESOLVED"), "PRESERVED"),
        ("Theorem actually established", ("SAME_SCOPE", "WEAKENED", "UNRESOLVED"), "SAME_SCOPE"),
        ("Qualifications and supplied repairs", ("NONE", "REQUIRED", "UNRESOLVED"), "NONE"),
    ):
        body = sections.get(name.lower(), "")
        status = field("Status", body)
        explanation = re.sub(r"^Status\s*:.*$", "", body, flags=re.M | re.I).strip()
        if status not in allowed:
            errors.append("Invalid status in " + name)
        bare_none = name == "Qualifications and supplied repairs" and status == "NONE" and not explanation
        if bare_none:
            normalizations.append("Bare Status: NONE is an explicit no-repairs declaration")
        elif len(explanation) < 12:
            errors.append("Missing explanation in " + name)
        checks[name] = {"status": status, "permits_acceptance": status == accepting}
    changes = {}
    for match in re.finditer(r"^###\s+(D\d+)\s*\n(.*?)(?=^###\s|\Z)",
                             sections.get("changed dependencies", ""), re.M | re.S):
        ident, body = match.groups()
        if ident in changes:
            errors.append("Duplicate change ID " + ident)
        status = field("Status", body)
        if status not in ("VERIFIED", "INVALID", "UNRESOLVED"):
            errors.append("Invalid change status " + ident)
        if len(re.sub(r"^Status\s*:.*$", "", body, flags=re.M | re.I).strip()) < 12:
            errors.append("Missing verification for " + ident)
        changes[ident] = status
    if set(changes) != set(expected_ids):
        errors.append("Changed-block coverage mismatch")
    if len(sections.get("decision basis", "")) < 12:
        errors.append("Missing decision basis")
    permits = all(check["permits_acceptance"] for check in checks.values()) and all(
        status == "VERIFIED" for status in changes.values())
    if decision == ACCEPT and not permits:
        errors.append("Acceptance conflicts with reported unresolved/failed checks")
    return {
        "validator_version": VERSION, "valid": not errors,
        "model_decision": decision, "decision": decision if not errors else KEEP,
        "checks": checks, "changes": changes, "errors": errors,
        "normalizations": normalizations, "warnings": warnings,
        "reported_hashes": reported_hashes, "hash_echo_is_authoritative": False,
        "response_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "normalized_markdown_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
        "mechanical_validation_only": True,
    }


def select_candidate(case_id: str, audits: list[dict], models: tuple[str, ...]) -> dict:
    """Require exactly both independent orders for every requested model."""
    expected = {(model, order) for model in models for order in ("forward", "reverse")}
    actual = [(audit["model_key"], audit["order"]) for audit in audits]
    covered = (bool(models) and len(set(models)) == len(models)
               and len(actual) == len(expected) and set(actual) == expected
               and all(audit["original_case_id"] == case_id for audit in audits))
    approvals = sum(audit["valid"] and audit["decision"] == ACCEPT for audit in audits)
    return {
        "decision": ACCEPT if covered and approvals == len(expected) else KEEP,
        "candidate_approvals": approvals, "required_approvals": len(expected),
        "audit_coverage_valid": covered,
    }
