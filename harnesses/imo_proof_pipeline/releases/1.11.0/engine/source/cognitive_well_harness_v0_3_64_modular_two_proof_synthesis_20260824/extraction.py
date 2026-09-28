from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import MINIMAL_HYPOTHESIS_SCHEMA
from .model_runtime import ModelRuntime, parse_json_object, write_json
from .prompts import hypothesis_extraction_prompt, minimal_hypothesis_parser_prompt


PARSER_TEMPERATURE = 0.1
PARSER_MAX_ATTEMPTS = 3


def extract_atomic_hypotheses(
    *,
    runtime: ModelRuntime,
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
        seed_label=f"extraction:{arm}:r{round_number}:document",
    )
    document = str(generated["text"]).strip()

    record: dict[str, Any] | None = None
    parser_generation: dict[str, Any] | None = None
    parser_attempts: list[dict[str, Any]] = []
    for attempt in range(PARSER_MAX_ATTEMPTS):
        stage = f"minimal_parser_{attempt}"
        try:
            record, parser_generation = runtime.structured(
                role="gemma",
                prompt=minimal_hypothesis_parser_prompt(document),
                destination=output_dir,
                stage=stage,
                schema=MINIMAL_HYPOTHESIS_SCHEMA,
                temperature=PARSER_TEMPERATURE,
                max_tokens=4_096,
                seed_label=f"extraction:{arm}:r{round_number}:parser:{attempt}",
            )
            if len(record["conjectures"]) != len(record["negations"]):
                raise ValueError("conjecture and negation counts differ")
            parser_attempts.append(
                {
                    "attempt": attempt,
                    "stage": stage,
                    "status": "accepted",
                    "finish_reason": parser_generation["metadata"].get("finish_reason"),
                }
            )
            break
        except Exception as error:
            # A cached provider response can still be recoverable after deterministic
            # control-character repair in parse_json_object. Keep the record small and
            # retry the parser, never the mathematical document, when it is not.
            parser_attempts.append(
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
        raise RuntimeError(f"minimal parser exhausted attempts: {parser_attempts}")

    result = {
        "arm": arm,
        "round": round_number,
        "diagnostics_exposed": arm == "diagnostic",
        "temperature": temperature,
        "parser_temperature": PARSER_TEMPERATURE,
        "parser_schema": "conjectures_and_exact_negations_only",
        "parser_attempts": parser_attempts,
        "deduplication_check": False,
        "document": document,
        "record": record,
        "document_generation": generated["metadata"],
        "parser_generation": parser_generation["metadata"],
    }
    write_json(result_path, result)
    return result


def load_minimal_record(path: Path) -> dict[str, Any]:
    """Small deterministic helper for inspecting or replaying parser artifacts."""

    return parse_json_object(path.read_text(encoding="utf-8"))
