from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "xhigh"
CONTRACT_PATH = Path(__file__).resolve()
SCHEMA = CONTRACT_PATH.with_name("grade_schema.json")

CALIBRATED_POLICY = r"""Use an Olympiad-coordination grading policy rather than a
formal-proof or strict missing-line policy.

Judge correctness, completeness, clarity, and how much mathematical work is required
to repair an omission. Keep these two axes separate:

1. dependency_impact: whether later conclusions depend on the step;
2. repair_complexity: whether repair is none, a direct/routine elaboration of the
   candidate's explicit strategy, a localized nontrivial addition, or a genuinely new
   idea.

A load-bearing omission is not automatically a major error. A concise solution may
receive full credit when the omitted detail is a direct, standard, essentially unique
elaboration of objects and a mechanism already present in the submission. Give 6 for
a genuine minor gap that is locally repairable without changing the strategy. Give 5
for a substantive localized gap whose repair is nontrivial but preserves the central
strategy. Reserve scores 0--4 for major gaps, false decisive claims, missing central
ideas, or incorrect answers.

Use this scale:
- 7: complete and correct by normal Olympiad standards; acceptable terseness allowed.
- 6: correct strategy and conclusion, with one minor/local repairable gap.
- 5: mostly correct, but with a substantive localized gap.
- 3--4: major central gap or serious invalid step, despite meaningful progress.
- 1--2: limited correct progress.
- 0: no meaningful progress.

Do not lower a score merely because you can expand a terse argument into several
sentences. Ask whether that expansion introduces a new mathematical idea or only makes
an already signposted mechanism explicit. Conversely, do not excuse a false inference
or a missing idea merely because some repair exists."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def validate_grade(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("grade must be a JSON object")
    required = {
        "score",
        "verdict",
        "answer_supported",
        "dependency_impact",
        "repair_complexity",
        "olympiad_treatment",
        "first_issue",
        "summary",
        "strengths",
        "errors",
    }
    if set(value) != required:
        raise ValueError(f"grade keys differ from the external contract: {sorted(value)}")
    result = dict(value)
    score = int(result["score"])
    if not 0 <= score <= 7:
        raise ValueError("score must be in 0..7")
    verdict = str(result["verdict"])
    dependency = str(result["dependency_impact"])
    repair = str(result["repair_complexity"])
    treatment = str(result["olympiad_treatment"])
    strengths = result["strengths"]
    errors = result["errors"]
    if not isinstance(result["answer_supported"], bool):
        raise ValueError("answer_supported must be boolean")
    if not isinstance(strengths, list) or not all(
        isinstance(item, str) and item.strip() for item in strengths
    ):
        raise ValueError("strengths must be a list of nonempty strings")
    if not isinstance(errors, list):
        raise ValueError("errors must be a list")
    for error in errors:
        if not isinstance(error, dict) or set(error) != {"severity", "description"}:
            raise ValueError("each error must contain severity and description only")
        if error["severity"] not in {"cosmetic", "minor", "substantial", "major"}:
            raise ValueError("invalid error severity")
        if not isinstance(error["description"], str) or not error["description"].strip():
            raise ValueError("error descriptions must be nonempty")
    consistent = (
        score == 7
        and verdict == "pass"
        and bool(result["answer_supported"])
        and dependency == "none"
        and repair == "none"
        and treatment == "full_credit"
        and not errors
    ) or (
        score == 6
        and verdict == "minor_gap"
        and bool(result["answer_supported"])
        and repair == "routine_direct"
        and treatment == "minor_deduction"
    ) or (
        score == 5
        and verdict == "substantial_gap"
        and repair == "local_nontrivial"
        and treatment == "partial_credit"
    ) or (
        score <= 4
        and verdict in {"substantial_gap", "major_gap", "incorrect"}
        and treatment in {"partial_credit", "major_deduction"}
    )
    result["score"] = score
    result["contract_consistent"] = consistent
    result["full_credit"] = consistent and score == 7
    return result
