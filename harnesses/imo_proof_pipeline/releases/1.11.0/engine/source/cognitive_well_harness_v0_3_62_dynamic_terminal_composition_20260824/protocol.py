from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


MAXIMUM_REASONING_DIRECTIVE = """REASONING EFFORT: MAXIMAL. Thinking mode is on.
Work out and verify the final proof privately before producing the required response.

Before finalizing, adversarially verify the proof from beginning to end. Recompute
decisive algebra, inequalities, limiting arguments, and case coverage. Ensure that no
downstream step depends on a false or unproved claim. If you cannot construct and
verify a complete proof after maximal effort, report failure rather than bluffing."""


FORBIDDEN_FINAL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("internal_lemma_id", re.compile(r"\bR\d+H\d+\b", re.IGNORECASE)),
    ("internal_lemma_reference", re.compile(r"\blemma\s+R\d+", re.IGNORECASE)),
    ("verified_argument_reference", re.compile(r"\bverified argument\b", re.IGNORECASE)),
    ("supplied_argument_reference", re.compile(r"\bsupplied argument\b", re.IGNORECASE)),
    ("workflow_reference", re.compile(r"\b(?:dossier|reviewer|workflow|pipeline)\b", re.IGNORECASE)),
)

CASE_HEADING_RE = re.compile(
    r"(?im)^\s*(?:#{1,6}\s*)?(?:\*{0,2})case\s+(?:\d+|[A-Z]|I{1,3}|IV|V)\b"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_dynamic_verified_arguments(round_summary_path: Path) -> list[dict[str, str]]:
    payload = json.loads(round_summary_path.read_text(encoding="utf-8"))
    arguments: list[dict[str, str]] = []
    for row in payload.get("verified") or []:
        statement = str(row.get("statement") or "").strip()
        proof = str(row.get("proof") or "").strip()
        if not statement or not proof:
            raise ValueError("every verified record must contain a statement and proof")
        arguments.append({"statement": statement, "proof": proof})
    if not arguments:
        raise ValueError("no verified arguments found in the source artifact")
    return arguments


def render_dynamic_arguments(arguments: list[dict[str, str]]) -> str:
    blocks: list[str] = []
    for position, argument in enumerate(arguments, start=1):
        blocks.append(
            f"ARGUMENT {position}\n"
            f"Statement:\n{argument['statement']}\n\n"
            f"Proof draft:\n{argument['proof']}"
        )
    return "\n\n".join(blocks)


def terminal_composition_prompt(
    *, problem: str, arguments: list[dict[str, str]]
) -> str:
    evidence = render_dynamic_arguments(arguments)
    return f"""You are an expert olympiad mathematician composing one final proof.
{MAXIMUM_REASONING_DIRECTIVE}

The mathematical argument records below were loaded dynamically from a previous
verification artifact. They are not reference answers and their proof drafts may
contain repairable slips. Recheck them independently against the problem before use.

COMPOSITION CONTRACT
1. Produce one clean, reader-facing, self-contained proof of the exact problem.
2. Re-derive all starting facts needed from the problem itself.
3. Use every dynamically supplied argument where its hypotheses apply. Do not merely
   cite or paraphrase an argument: reproduce all mathematics needed by the final proof.
4. Read the hypotheses of all supplied arguments, identify the alternatives needed to
   apply them, and organize the final proof under explicit CASE 1, CASE 2, ... headings.
   Prove that the cases are exhaustive and complete every branch.
5. Correct any sign, inequality-direction, endpoint, continuity, or limiting slip found
   in a proof draft before incorporating it.
6. The final proof must not mention argument numbers, supplied or verified arguments,
   record identifiers, candidates, reviewers, dossiers, scores, or this workflow. It
   must remain valid if this prompt and all source artifacts are deleted.
7. Avoid unsupported bridge phrases such as "the modulus forces", "similarly", or
   "clearly" at a decisive step. State the actual inference.
8. Return only the final proof and complete answer. If a complete proof cannot be
   verified, state failure and the first remaining gap rather than presenting a partial
   proof as complete.

ORIGINAL PROBLEM:
{problem}

DYNAMICALLY LOADED MATHEMATICAL ARGUMENTS ({len(arguments)} records):
{evidence}
"""


def deterministic_composition_gate(proof: str) -> dict[str, Any]:
    violations = [
        name for name, pattern in FORBIDDEN_FINAL_PATTERNS if pattern.search(proof)
    ]
    case_heading_count = len(CASE_HEADING_RE.findall(proof))
    if case_heading_count < 2:
        violations.append("fewer_than_two_explicit_case_headings")
    return {
        "passed": not violations,
        "violations": violations,
        "case_heading_count": case_heading_count,
    }

