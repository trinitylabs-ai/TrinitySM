from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ARMS = ("original", "diagnostic")
SYNTHESIS_FAMILIES = ("lemma_evidence_only", "anchored_refinement")

SYNTHESIS_CONFIGURATIONS: tuple[dict[str, Any], ...] = (
    {
        "candidate_id": "original_evidence_t02",
        "arm": "original",
        "family": "lemma_evidence_only",
        "temperature": 0.2,
        "replicate": 1,
    },
    {
        "candidate_id": "original_evidence_t04",
        "arm": "original",
        "family": "lemma_evidence_only",
        "temperature": 0.4,
        "replicate": 1,
    },
    {
        "candidate_id": "original_anchored_t02",
        "arm": "original",
        "family": "anchored_refinement",
        "temperature": 0.2,
        "replicate": 1,
    },
    {
        "candidate_id": "original_anchored_t04",
        "arm": "original",
        "family": "anchored_refinement",
        "temperature": 0.4,
        "replicate": 1,
    },
    {
        "candidate_id": "diagnostic_evidence_t02",
        "arm": "diagnostic",
        "family": "lemma_evidence_only",
        "temperature": 0.2,
        "replicate": 1,
    },
    {
        "candidate_id": "diagnostic_evidence_t04",
        "arm": "diagnostic",
        "family": "lemma_evidence_only",
        "temperature": 0.4,
        "replicate": 1,
    },
    {
        "candidate_id": "diagnostic_anchored_t02",
        "arm": "diagnostic",
        "family": "anchored_refinement",
        "temperature": 0.2,
        "replicate": 1,
    },
    {
        "candidate_id": "diagnostic_anchored_t04",
        "arm": "diagnostic",
        "family": "anchored_refinement",
        "temperature": 0.4,
        "replicate": 1,
    },
)

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["problem_id", "problem", "candidate_proofs"],
    "properties": {
        "problem_id": {"type": "string", "minLength": 1},
        "problem": {"type": "string", "minLength": 20},
        "candidate_proofs": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "candidate_id",
                    "role",
                    "proof",
                    "non_authoritative_diagnostic",
                ],
                "properties": {
                    "candidate_id": {"type": "string", "minLength": 1},
                    "role": {
                        "type": "string",
                        "enum": ["anchor", "supplement"],
                    },
                    "proof": {"type": "string", "minLength": 20},
                    "non_authoritative_diagnostic": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
            },
        },
        "synthesis_instructions": {"type": "string"},
        "gate": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "require_all_verified_lemmas": {"type": "boolean"},
                "minimum_cited_lemmas": {"type": "integer", "minimum": 0},
                "minimum_case_headings": {"type": "integer", "minimum": 0},
                "require_qwen_certification": {"type": "boolean"},
            },
        },
    },
}

MINIMAL_HYPOTHESIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["conjectures", "negations"],
    "properties": {
        "conjectures": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 20},
        },
        "negations": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 20},
        },
    },
}

NEGATION_AUDIT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["valid_exact_negation", "first_issue"],
    "properties": {
        "valid_exact_negation": {"type": "boolean"},
        "first_issue": {"type": ["string", "null"]},
    },
}

NEGATION_REPAIR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["exact_negation"],
    "properties": {"exact_negation": {"type": "string", "minLength": 20}},
}

CERTIFICATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict", "exact_claim_reached"],
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "INCONCLUSIVE"]},
        "exact_claim_reached": {"type": "boolean"},
    },
}

DIAGNOSTIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["earliest_break", "missing_obligations", "summary"],
    "properties": {
        "earliest_break": {"type": ["string", "null"], "maxLength": 1200},
        "missing_obligations": {
            "type": "array",
            "maxItems": 4,
            "items": {"type": "string", "minLength": 1, "maxLength": 600},
        },
        "summary": {"type": "string", "minLength": 1, "maxLength": 1200},
    },
}

DEFAULT_GATE: dict[str, Any] = {
    "require_all_verified_lemmas": True,
    "minimum_cited_lemmas": 1,
    "minimum_case_headings": 0,
    "require_qwen_certification": True,
}


def validate_schema(value: Any, schema: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda row: list(row.path),
    )
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"schema error at {location}: {errors[0].message}")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return normalized or "artifact"


def load_run_input(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_schema(value, INPUT_SCHEMA)
    ids = [row["candidate_id"] for row in value["candidate_proofs"]]
    if len(ids) != len(set(ids)):
        raise ValueError("candidate_id values must be unique")
    roles = [row["role"] for row in value["candidate_proofs"]]
    if sorted(roles) != ["anchor", "supplement"]:
        raise ValueError("candidate proofs must contain one anchor and one supplement")
    if any(
        not str(row.get("non_authoritative_diagnostic") or "").strip()
        for row in value["candidate_proofs"]
    ):
        raise ValueError(
            "each candidate proof needs a diagnostic for the independent diagnostic arm"
        )
    result = dict(value)
    result["gate"] = {**DEFAULT_GATE, **value.get("gate", {})}
    result.setdefault("synthesis_instructions", "")
    return result
