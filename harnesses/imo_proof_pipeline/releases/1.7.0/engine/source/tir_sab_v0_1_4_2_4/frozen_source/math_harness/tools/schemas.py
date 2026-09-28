"""Strict schemas and stable hashes for selective tool execution."""

from __future__ import annotations

import hashlib
import json
import math
import re
from enum import Enum
from typing import Any, Mapping


class ToolSchemaError(ValueError):
    """A tool-facing artifact failed strict validation."""


class RouteDecision(str, Enum):
    SKIP = "skip"
    CALL = "call"
    UNSUPPORTED = "unsupported"


class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    REFUTED = "refuted"
    UNKNOWN = "unknown"


_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,180}$")
_FORBIDDEN_KEYS = {
    "code",
    "source_code",
    "python",
    "shell",
    "command",
    "cmd",
    "path",
    "file",
    "url",
    "uri",
    "expected_answer",
    "reference_answer",
    "answer_key",
}
_URL_RE = re.compile(r"(?:https?|ftp|file)://", re.IGNORECASE)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ToolSchemaError(f"{label} must be an object")
    return value


def _require_id(value: Any, label: str) -> str:
    text = str(value)
    if not _ID_RE.fullmatch(text):
        raise ToolSchemaError(f"{label} is not a safe identifier: {value!r}")
    return text


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ToolSchemaError(f"{label} must be a list of strings")
    return list(value)


def _reject_unsafe_payload(value: Any, *, path: str = "arguments") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in _FORBIDDEN_KEYS:
                raise ToolSchemaError(f"{path}.{key_text} is forbidden")
            _reject_unsafe_payload(item, path=f"{path}.{key_text}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_unsafe_payload(item, path=f"{path}[{index}]")
    elif isinstance(value, str):
        if _URL_RE.search(value):
            raise ToolSchemaError(f"{path} contains a network or file URL")
        if "\x00" in value:
            raise ToolSchemaError(f"{path} contains a NUL byte")
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise ToolSchemaError(f"{path} contains unsupported type {type(value).__name__}")
    if isinstance(value, float) and not math.isfinite(value):
        raise ToolSchemaError(f"{path} contains a non-finite number")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def answers_equivalent(left: Any, right: Any) -> bool:
    r"""Compare exact-tool answers after presentation-only normalization.

    Tool backends commonly insert spaces in LaTeX (for example ``548 \pi``)
    while model extraction stores the same expression as ``548\pi``.  Those
    forms must not create a false exact refutation.  This deliberately performs
    only conservative formatting normalization; it is not a symbolic solver.
    """

    if left is None or right is None:
        return left is right

    def normalize(value: Any) -> str:
        text = str(value).strip()
        text = re.sub(r"(?i)^\s*ANSWER:\s*", "", text).strip()
        text = text.replace("\u2212", "-").replace("\u2013", "-").replace(
            "\u2014", "-"
        )
        text = text.replace(r"\left", "").replace(r"\right", "")
        text = text.replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
        text = re.sub(r"\s+", "", text)
        return text.rstrip(".,")

    return normalize(left) == normalize(right)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def validate_claim(value: Mapping[str, Any]) -> dict[str, Any]:
    claim = dict(_require_mapping(value, "claim"))
    required = {
        "run_id",
        "problem_id",
        "claim_id",
        "node_ids",
        "source_spans",
        "claim_type",
        "statement",
        "normalized_arguments",
        "assumptions",
        "criticality",
        "derivation_family",
    }
    missing = sorted(required - claim.keys())
    if missing:
        raise ToolSchemaError(f"claim is missing fields: {missing}")
    for field in ("run_id", "problem_id", "claim_id"):
        claim[field] = _require_id(claim[field], field)
    claim["node_ids"] = [
        _require_id(item, "node_id")
        for item in _require_string_list(claim["node_ids"], "node_ids")
    ]
    if not isinstance(claim["source_spans"], list):
        raise ToolSchemaError("source_spans must be a list")
    if not isinstance(claim["statement"], str) or not claim["statement"].strip():
        raise ToolSchemaError("statement must be non-empty")
    if claim["criticality"] not in {"answer_changing", "supporting"}:
        raise ToolSchemaError("criticality must be answer_changing or supporting")
    _require_id(claim["claim_type"], "claim_type")
    _require_id(claim["derivation_family"], "derivation_family")
    _reject_unsafe_payload(claim["normalized_arguments"])
    _reject_unsafe_payload(claim["assumptions"])
    return claim


def validate_route_decision(value: Mapping[str, Any]) -> dict[str, Any]:
    route = dict(_require_mapping(value, "route decision"))
    required = {
        "run_id",
        "problem_id",
        "route_stage",
        "decision",
        "risk_score",
        "reason_codes",
        "critical_claim_ids",
        "planned_operations",
    }
    missing = sorted(required - route.keys())
    if missing:
        raise ToolSchemaError(f"route decision is missing fields: {missing}")
    route["run_id"] = _require_id(route["run_id"], "run_id")
    route["problem_id"] = _require_id(route["problem_id"], "problem_id")
    if route["route_stage"] not in {"route1", "route2", "audit"}:
        raise ToolSchemaError("route_stage must be route1, route2, or audit")
    try:
        route["decision"] = RouteDecision(str(route["decision"])).value
    except ValueError as exc:
        raise ToolSchemaError("decision must be skip, call, or unsupported") from exc
    score = route["risk_score"]
    if not isinstance(score, (int, float)) or not 0 <= float(score) <= 1:
        raise ToolSchemaError("risk_score must be between zero and one")
    route["risk_score"] = float(score)
    route["reason_codes"] = _require_string_list(
        route["reason_codes"], "reason_codes"
    )
    route["critical_claim_ids"] = _require_string_list(
        route["critical_claim_ids"], "critical_claim_ids"
    )
    route["planned_operations"] = _require_string_list(
        route["planned_operations"], "planned_operations"
    )
    return route


def validate_tool_plan(
    value: Mapping[str, Any],
    *,
    registered_operations: set[str] | frozenset[str],
    max_timeout_sec: int = 120,
    max_memory_limit_mb: int = 2048,
) -> dict[str, Any]:
    plan = dict(_require_mapping(value, "tool plan"))
    required = {
        "run_id",
        "problem_id",
        "claim_id",
        "operation",
        "arguments",
        "assumptions",
        "backend_capability",
        "timeout_sec",
        "memory_limit_mb",
        "validator",
    }
    missing = sorted(required - plan.keys())
    if missing:
        raise ToolSchemaError(f"tool plan is missing fields: {missing}")
    for field in ("run_id", "problem_id", "claim_id"):
        plan[field] = _require_id(plan[field], field)
    operation = _require_id(plan["operation"], "operation")
    if operation not in registered_operations:
        raise ToolSchemaError(f"unregistered operation: {operation}")
    _require_id(plan["backend_capability"], "backend_capability")
    _require_id(plan["validator"], "validator")
    timeout = plan["timeout_sec"]
    memory = plan["memory_limit_mb"]
    if not isinstance(timeout, int) or not 1 <= timeout <= max_timeout_sec:
        raise ToolSchemaError(
            f"timeout_sec must be an integer from 1 through {max_timeout_sec}"
        )
    if not isinstance(memory, int) or not 32 <= memory <= max_memory_limit_mb:
        raise ToolSchemaError(
            "memory_limit_mb must be an integer from 32 through "
            f"{max_memory_limit_mb}"
        )
    _reject_unsafe_payload(plan["arguments"])
    _reject_unsafe_payload(plan["assumptions"])
    return plan


def operation_hash(plan: Mapping[str, Any], *, backend_version: str, validator_version: str) -> str:
    arguments = dict(plan.get("arguments") or {})
    # ``claimed_answer`` affects the candidate/evidence relation, not the
    # mathematical operation. Excluding it allows Route 2 to reuse Route 1's
    # exact result when the candidate answer changes.
    arguments.pop("claimed_answer", None)
    return stable_hash(
        {
            "operation": plan.get("operation"),
            "arguments": arguments,
            "assumptions": plan.get("assumptions"),
            "backend_capability": plan.get("backend_capability"),
            "backend_version": backend_version,
            "validator": plan.get("validator"),
            "validator_version": validator_version,
        }
    )


def validate_evidence(value: Mapping[str, Any]) -> dict[str, Any]:
    evidence = dict(_require_mapping(value, "tool evidence"))
    required = {
        "run_id",
        "problem_id",
        "claim_id",
        "status",
        "checked_claim",
        "normalized_result",
        "certificate",
        "counterexample",
        "backend",
        "backend_version",
        "operation_hash",
        "executor_code_hash",
        "validator_code_hash",
        "runtime_sec",
        "validation_status",
    }
    missing = sorted(required - evidence.keys())
    if missing:
        raise ToolSchemaError(f"tool evidence is missing fields: {missing}")
    for field in ("run_id", "problem_id", "claim_id"):
        evidence[field] = _require_id(evidence[field], field)
    try:
        evidence["status"] = EvidenceStatus(str(evidence["status"])).value
    except ValueError as exc:
        raise ToolSchemaError(
            "status must be verified, refuted, or unknown"
        ) from exc
    if evidence["validation_status"] not in {"passed", "failed", "not_run"}:
        raise ToolSchemaError("invalid validation_status")
    if (
        evidence["status"] != EvidenceStatus.UNKNOWN.value
        and evidence["validation_status"] != "passed"
    ):
        raise ToolSchemaError("positive or refuting evidence requires passed validation")
    if not isinstance(evidence["runtime_sec"], (int, float)) or float(
        evidence["runtime_sec"]
    ) < 0:
        raise ToolSchemaError("runtime_sec must be non-negative")
    for field in ("operation_hash", "executor_code_hash", "validator_code_hash"):
        text = str(evidence[field])
        if not re.fullmatch(r"[0-9a-f]{64}", text):
            raise ToolSchemaError(f"{field} must be a SHA-256 hex digest")
    _reject_unsafe_payload(evidence["normalized_result"], path="normalized_result")
    _reject_unsafe_payload(evidence["certificate"], path="certificate")
    _reject_unsafe_payload(evidence["counterexample"], path="counterexample")
    return evidence
