from __future__ import annotations

import json
from typing import Any

from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825 import (
    salvage as v078_salvage,
)


_STRICT_PARSE = v078_salvage.v063_salvage.parse_salvage_record


def _strip_json_fence(text: str) -> str:
    value = text.strip()
    if not value.startswith("```"):
        return value
    value = value[3:]
    if value.startswith("json") and (
        len(value) == 4 or value[4].isspace() or value[4] == "{"
    ):
        value = value[4:]
    value = value.strip()
    if value.endswith("```"):
        value = value[:-3].strip()
    return value


def _close_truncated_json_object(text: str) -> str | None:
    """Append only missing terminal brackets; never alter JSON content."""
    value = _strip_json_fence(text)
    start = value.find("{")
    if start < 0:
        return None
    value = value[start:]
    stack: list[str] = []
    in_string = False
    escaped = False
    for character in value:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "{":
            stack.append("}")
        elif character == "[":
            stack.append("]")
        elif character in ("}", "]"):
            if not stack or stack[-1] != character:
                return None
            stack.pop()
    if in_string or not stack:
        return None
    return value + "".join(reversed(stack))


def _unwrap_redundant_decision_envelope(record: Any) -> Any:
    if not isinstance(record, dict) or set(record) != {"decision"}:
        return record
    nested = record.get("decision")
    if not isinstance(nested, dict):
        return record
    required = {"decision", "failure_interpretation", "hypotheses"}
    return nested if required.issubset(nested) else record


def _repair_exact_terminal_single_quote(text: str) -> str | None:
    """Repair one observed terminal quote typo without rewriting JSON content."""
    value = _strip_json_fence(text)
    bad_suffix = '"local_dependency_map": "None\'}]}'
    if not value.endswith(bad_suffix):
        return None
    good_suffix = '"local_dependency_map": "None"}]}'
    return value[: -len(bad_suffix)] + good_suffix


def parse_salvage_record_with_transport_normalization(text: str) -> dict[str, Any]:
    """Preserve strict parsing, with a narrow deterministic transport fallback."""
    try:
        return _STRICT_PARSE(text)
    except Exception as strict_error:
        candidates = [
            _repair_exact_terminal_single_quote(text),
            _close_truncated_json_object(text),
        ]
        for candidate in candidates:
            if candidate is None:
                continue
            try:
                decoded = json.loads(candidate)
                normalized = _unwrap_redundant_decision_envelope(decoded)
                return _STRICT_PARSE(json.dumps(normalized, ensure_ascii=False))
            except Exception:
                continue
        raise strict_error


# The v0.3.78 implementation resolves this parser through its imported v0.3.63
# module at call time. Override it only in the v0.3.79 process; no frozen parent
# source or generation configuration is changed.
v078_salvage.v063_salvage.parse_salvage_record = (
    parse_salvage_record_with_transport_normalization
)

EXPERIMENT_MASTER_SEED = v078_salvage.EXPERIMENT_MASTER_SEED
failure_card_for_pair = v078_salvage.failure_card_for_pair
run_failure_guided_salvage = v078_salvage.run_failure_guided_salvage
_run_exact_v063_salvage_generation = v078_salvage._run_exact_v063_salvage_generation
