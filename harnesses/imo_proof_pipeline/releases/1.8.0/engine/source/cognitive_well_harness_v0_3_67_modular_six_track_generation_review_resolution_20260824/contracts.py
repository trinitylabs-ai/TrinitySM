from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cognitive_well_harness_v0_3_46_gemma4_temperature_portfolio_20260823.run import (
    CANDIDATES as FROZEN_CANDIDATES,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.contracts import (
    DEFAULT_GATE,
)


INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["problem_id", "problem"],
    "properties": {
        "problem_id": {
            "type": "string",
            "minLength": 1,
            "pattern": "^[A-Za-z0-9_.-]+$",
        },
        "problem": {"type": "string", "minLength": 20},
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

CANDIDATES: tuple[dict[str, Any], ...] = tuple(
    dict(row) for row in FROZEN_CANDIDATES
)
CANDIDATE_IDS = tuple(str(row["candidate_id"]) for row in CANDIDATES)

# The production choices recovered from the v0.3.48--54 experiments. These are
# asserted by tests and recorded verbatim in each run manifest.
PROFILE: dict[str, Any] = {
    "cold_generation": {
        "model": "google/gemma-4-31B-it",
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "candidate_allocation": {"temperature_1.0": 4, "temperature_0.7": 2},
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": 65_536,
        "cap_recovery_max_tokens": 131_072,
        "thinking_enabled": True,
        "max_concurrent": 4,
    },
    "lazy_check": {
        "model": "google/gemma-4-31B-it",
        "temperature": 0.1,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": 8_192,
    },
    "lazy_in_place_expansion": {
        "model": "google/gemma-4-31B-it",
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": 65_536,
        "cap_recovery_max_tokens": 131_072,
        "routing": "only_when_lazy_report_is_not_NO_ISSUES",
    },
    "reviewer_1": {
        "role": "earliest-break locator",
        "model": "google/gemma-4-31B-it",
        "temperature": 0.4,
        "top_p": 1.0,
        "top_k": -1,
        "max_tokens": 12_000,
        "cap_recovery_max_tokens": 24_000,
    },
    "reviewer_2": {
        "role": "adversarial falsifier",
        "model": "Qwen/Qwen3.6-27B",
        "temperature": 0.2,
        "top_p": 1.0,
        "top_k": -1,
        "max_tokens": 12_000,
        "cap_recovery_max_tokens": 24_000,
    },
    "reviewer_3": {
        "role": "charitable certifier",
        "model": "google/gemma-4-31B-it",
        "temperature": 0.2,
        "top_p": 1.0,
        "top_k": -1,
        "reasoning_effort": "max",
        "max_tokens": 16_000,
        "cap_recovery_max_tokens": 32_000,
    },
    "fusion": {
        "model": "google/gemma-4-31B-it",
        "temperature": 0.4,
        "top_p": 1.0,
        "top_k": -1,
        "reasoning_effort": "max",
        "max_tokens": 16_000,
        "cap_recovery_max_tokens": 32_000,
    },
    "resolver": {
        "model": "google/gemma-4-31B-it",
        "temperature": 0.4,
        "top_p": 1.0,
        "top_k": -1,
        "reasoning_effort": "max",
        "max_tokens": 32_000,
        "cap_recovery_max_tokens": 64_000,
        "routing": "fusion_outcome_equals_REPAIR_NEEDED",
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
    result = dict(value)
    result["problem_id"] = str(result["problem_id"]).strip()
    result["problem"] = str(result["problem"]).strip()
    result["synthesis_instructions"] = str(
        result.get("synthesis_instructions") or ""
    )
    result["gate"] = {**DEFAULT_GATE, **value.get("gate", {})}
    return result

