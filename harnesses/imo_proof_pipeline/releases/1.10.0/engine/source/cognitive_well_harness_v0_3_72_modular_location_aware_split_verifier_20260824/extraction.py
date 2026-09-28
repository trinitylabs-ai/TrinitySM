from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json

from .contracts import LOCATION_HYPOTHESIS_SCHEMA
from .prompts import hypothesis_extraction_prompt, location_hypothesis_parser_prompt
from .runtime import ResilientModelRuntime


PARSER_TEMPERATURE = 0.1
PARSER_MAX_ATTEMPTS = 3

_SECTION_HEADING = re.compile(
    r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?"
    r"(ESTABLISHED MATERIAL|EARLIEST UNRESOLVED TRANSITIONS|ATOMIC CONJECTURES|"
    r"EXACT NEGATIONS|LOCAL DEPENDENCY MAP)(?:\*\*)?\s*$"
)
_NUMBERED_ENTRY = re.compile(r"(?m)^\s*\d+[.)]\s+")


def _section_map(document: str) -> dict[str, str]:
    matches = list(_SECTION_HEADING.finditer(document))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(document)
        sections[match.group(1)] = document[match.end() : end].strip()
    return sections


def _entries(value: str) -> list[str]:
    text = value.strip()
    if not text or re.fullmatch(r"(?is)(?:none|no admissible conjectures?)[.!]?", text):
        return []
    starts = list(_NUMBERED_ENTRY.finditer(text))
    if not starts:
        return [text]
    return [
        text[match.end() : (starts[index + 1].start() if index + 1 < len(starts) else len(text))].strip()
        for index, match in enumerate(starts)
    ]


def deterministic_location_record(document: str) -> dict[str, Any] | None:
    """Parse the required prose sections without rewriting mathematical notation."""
    sections = _section_map(document)
    required = (
        "EARLIEST UNRESOLVED TRANSITIONS",
        "ATOMIC CONJECTURES",
        "EXACT NEGATIONS",
        "LOCAL DEPENDENCY MAP",
    )
    if any(name not in sections for name in required):
        return None
    conjectures = _entries(sections["ATOMIC CONJECTURES"])
    negations = _entries(sections["EXACT NEGATIONS"])
    transitions = _entries(sections["EARLIEST UNRESOLVED TRANSITIONS"])
    dependencies = _entries(sections["LOCAL DEPENDENCY MAP"])
    if not (
        len(conjectures)
        == len(negations)
        == len(transitions)
        == len(dependencies)
        <= 3
    ):
        return None
    return {
        "hypotheses": [
            {
                "conjecture": conjectures[index],
                "exact_negation": negations[index],
                "earliest_unresolved_transition": transitions[index],
                "local_dependency_map": dependencies[index],
            }
            for index in range(len(conjectures))
        ]
    }


def extract_atomic_hypotheses(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    arm: str,
    temperature: float,
    round_number: int,
    output_dir: Path,
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.exists():
        return json.loads(result_path.read_text(encoding="utf-8"))
    generated = runtime.text(
        role="gemma",
        prompt=hypothesis_extraction_prompt(
            problem=problem,
            candidate_proofs=candidate_proofs,
            include_diagnostics=arm == "diagnostic",
        ),
        destination=output_dir,
        stage="hypothesis_document",
        temperature=temperature,
        max_tokens=32_768,
        seed_label=f"v072:extraction:{arm}:r{round_number}:document",
    )
    document = str(generated["text"]).strip()
    record = deterministic_location_record(document)
    parser_generation = None
    attempts: list[dict[str, Any]] = []
    if record is not None:
        from .contracts import validate_schema

        validate_schema(record, LOCATION_HYPOTHESIS_SCHEMA)
        attempts.append(
            {
                "attempt": 0,
                "stage": "deterministic_section_parser",
                "status": "accepted",
            }
        )
        parser_generation = {"metadata": {"source": "deterministic_section_parser"}}
    for attempt in range(PARSER_MAX_ATTEMPTS) if record is None else ():
        stage = f"location_parser_{attempt}"
        try:
            record, parser_generation = runtime.structured(
                role="gemma",
                prompt=location_hypothesis_parser_prompt(document),
                destination=output_dir,
                stage=stage,
                schema=LOCATION_HYPOTHESIS_SCHEMA,
                temperature=PARSER_TEMPERATURE,
                max_tokens=8_192,
                seed_label=f"v072:extraction:{arm}:r{round_number}:parser:{attempt}",
            )
            attempts.append({"attempt": attempt, "stage": stage, "status": "accepted"})
            break
        except Exception as error:
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": stage,
                    "status": "rejected",
                    "error": f"{type(error).__name__}: {error}",
                }
            )
            record = None
            parser_generation = None
    if record is None or parser_generation is None:
        raise RuntimeError(f"location parser exhausted attempts: {attempts}")
    result = {
        "arm": arm,
        "round": round_number,
        "temperature": temperature,
        "diagnostics_exposed": arm == "diagnostic",
        "parser_temperature": PARSER_TEMPERATURE,
        "parser_schema": "paired_hypotheses_with_two_location_fields",
        "parser_policy": "deterministic_exact_section_parser_then_model_fallback",
        "parser_attempts": attempts,
        "document": document,
        "record": record,
        "document_generation": generated["metadata"],
        "parser_generation": parser_generation["metadata"],
    }
    write_json(result_path, result)
    return result
