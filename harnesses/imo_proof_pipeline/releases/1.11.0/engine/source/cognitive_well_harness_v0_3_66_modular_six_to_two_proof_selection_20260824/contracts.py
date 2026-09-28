from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    DEFAULT_GATE,
)


INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["problem_id", "problem", "tracks"],
    "properties": {
        "problem_id": {"type": "string", "minLength": 1},
        "problem": {"type": "string", "minLength": 20},
        "tracks": {
            "type": "array",
            "minItems": 6,
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "track_id",
                    "original_proof",
                    "fusion_diagnostic",
                    "resolver_change_record",
                    "resolved_proof",
                ],
                "properties": {
                    "track_id": {
                        "type": "string",
                        "minLength": 1,
                        "pattern": "^[A-Za-z0-9_.-]+$",
                    },
                    "original_proof": {"type": "string", "minLength": 20},
                    "fusion_diagnostic": {"type": "string", "minLength": 1},
                    "resolver_change_record": {"type": "string", "minLength": 1},
                    "resolved_proof": {"type": "string", "minLength": 20},
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

TRACK_EVIDENCE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "track_id",
        "preferred_version",
        "strategy_summary",
        "usable_established_material",
        "longest_valid_chain",
        "strongest_usable_lemma",
        "original_first_break",
        "resolved_first_break",
        "resolver_change_assessment",
        "distinctive_mechanisms",
        "root_distance",
        "remaining_gap",
    ],
    "properties": {
        "track_id": {
            "type": "string",
            "minLength": 1,
            "pattern": "^[A-Za-z0-9_.-]+$",
        },
        "preferred_version": {"type": "string", "enum": ["ORIGINAL", "RESOLVED"]},
        "strategy_summary": {"type": "string", "minLength": 1, "maxLength": 1600},
        "usable_established_material": {
            "type": "array",
            "minItems": 1,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 1200},
        },
        "longest_valid_chain": {
            "type": "array",
            "minItems": 1,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 1200},
        },
        "strongest_usable_lemma": {"type": "string", "minLength": 1, "maxLength": 1600},
        "original_first_break": {"type": "string", "minLength": 1, "maxLength": 1600},
        "resolved_first_break": {"type": "string", "minLength": 1, "maxLength": 1600},
        "resolver_change_assessment": {"type": "string", "minLength": 1, "maxLength": 1600},
        "distinctive_mechanisms": {
            "type": "array",
            "minItems": 1,
            "maxItems": 8,
            "items": {"type": "string", "minLength": 1, "maxLength": 800},
        },
        "root_distance": {"type": "string", "minLength": 1, "maxLength": 1600},
        "remaining_gap": {"type": "string", "minLength": 1, "maxLength": 1600},
    },
}

PAIR_SELECTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "anchor",
        "supplement",
        "pair_audits",
        "pair_audit",
        "selection_confidence",
    ],
    "properties": {
        "anchor": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "track_id",
                "version",
                "strongest_usable_argument",
                "first_unresolved_gap",
                "selection_reason",
            ],
            "properties": {
                "track_id": {
                    "type": "string",
                    "minLength": 1,
                    "pattern": "^[A-Za-z0-9_.-]+$",
                },
                "version": {"type": "string", "enum": ["ORIGINAL", "RESOLVED"]},
                "strongest_usable_argument": {"type": "string", "minLength": 1, "maxLength": 1600},
                "first_unresolved_gap": {"type": "string", "minLength": 1, "maxLength": 1600},
                "selection_reason": {"type": "string", "minLength": 1, "maxLength": 1600},
            },
        },
        "supplement": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "track_id",
                "version",
                "complementary_argument",
                "anchor_gap_addressed",
                "selection_reason",
            ],
            "properties": {
                "track_id": {
                    "type": "string",
                    "minLength": 1,
                    "pattern": "^[A-Za-z0-9_.-]+$",
                },
                "version": {"type": "string", "enum": ["ORIGINAL", "RESOLVED"]},
                "complementary_argument": {"type": "string", "minLength": 1, "maxLength": 1600},
                "anchor_gap_addressed": {"type": "string", "minLength": 1, "maxLength": 1600},
                "selection_reason": {"type": "string", "minLength": 1, "maxLength": 1600},
            },
        },
        "pair_audits": {
            "type": "array",
            "minItems": 15,
            "maxItems": 15,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "track_ids",
                    "combined_coverage",
                    "complementarity",
                    "shared_failure_risk",
                    "relative_rank",
                ],
                "properties": {
                    "track_ids": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {
                            "type": "string",
                            "minLength": 1,
                            "pattern": "^[A-Za-z0-9_.-]+$",
                        },
                    },
                    "combined_coverage": {"type": "string", "minLength": 1, "maxLength": 800},
                    "complementarity": {"type": "string", "minLength": 1, "maxLength": 800},
                    "shared_failure_risk": {"type": "string", "minLength": 1, "maxLength": 800},
                    "relative_rank": {"type": "integer", "minimum": 1, "maximum": 15},
                },
            },
        },
        "pair_audit": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "combined_proof_coverage",
                "shared_failure_risk",
                "remaining_gap",
            ],
            "properties": {
                "combined_proof_coverage": {"type": "string", "minLength": 1, "maxLength": 1600},
                "shared_failure_risk": {"type": "string", "minLength": 1, "maxLength": 1600},
                "remaining_gap": {"type": "string", "minLength": 1, "maxLength": 1600},
            },
        },
        "selection_confidence": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
    },
}


def validate_schema(value: Any, schema: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda row: list(row.path),
    )
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"schema error at {location}: {errors[0].message}")


def load_run_input(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_schema(value, INPUT_SCHEMA)
    track_ids = [row["track_id"] for row in value["tracks"]]
    if len(track_ids) != len(set(track_ids)):
        raise ValueError("all six track_id values must be unique")
    result = dict(value)
    result["gate"] = {**DEFAULT_GATE, **value.get("gate", {})}
    result.setdefault("synthesis_instructions", "")
    return result


def validate_track_evidence(record: dict[str, Any], *, expected_track_id: str) -> None:
    validate_schema(record, TRACK_EVIDENCE_SCHEMA)
    if record["track_id"] != expected_track_id:
        raise ValueError("track evidence record changed its supplied track_id")


def validate_pair_selection(record: dict[str, Any], *, track_ids: list[str]) -> None:
    validate_schema(record, PAIR_SELECTION_SCHEMA)
    expected_ids = set(track_ids)
    chosen = {record["anchor"]["track_id"], record["supplement"]["track_id"]}
    if len(chosen) != 2 or not chosen <= expected_ids:
        raise ValueError("anchor and supplement must be different supplied tracks")
    expected_pairs = {tuple(sorted(pair)) for pair in combinations(track_ids, 2)}
    observed_pairs = {
        tuple(sorted(row["track_ids"])) for row in record["pair_audits"]
    }
    if observed_pairs != expected_pairs:
        raise ValueError("pair_audits must cover all 15 unordered pairs exactly once")
    ranks = sorted(row["relative_rank"] for row in record["pair_audits"])
    if ranks != list(range(1, 16)):
        raise ValueError("relative_rank must be a permutation of 1 through 15")
    top_pair = next(
        tuple(sorted(row["track_ids"]))
        for row in record["pair_audits"]
        if row["relative_rank"] == 1
    )
    if top_pair != tuple(sorted(chosen)):
        raise ValueError("the selected anchor/supplement pair must have relative_rank 1")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
