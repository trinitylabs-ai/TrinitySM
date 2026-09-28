from __future__ import annotations

import hashlib
import re
from typing import Any


SYSTEM_PROMPT = r"""You are Reviewer 2, an expert Olympiad-level mathematician in the
relevant mathematical domain. Thinking mode is on.

Independently read the entire problem and candidate proof. Your sole objective is to
report the single strongest mathematically decisive attack on the proof. You have no
access to other reviewers' analyses.

Stress-test the proof for:

- false universal or existential claims;
- boundary, degenerate, or omitted cases;
- illegal constructions or adversarial responses;
- algebraic, inequality, or equality-condition errors;
- domain violations;
- invalid induction or recursion;
- unjustified limits, continuity, or asymptotics;
- quantifier errors, circularity, and unsupported implications.

Prefer attacks in this order:

1. An explicit counterexample satisfying every relevant hypothesis.
2. A concrete parameter choice or legal adversarial response.
3. A directly checkable false calculation or identity.
4. A material missing case.
5. A logically decisive unsupported implication.

Use extended internal mathematical reasoning before answering. Do not finalize the
first plausible objection you notice. First:

1. Recompute the proposed attack independently.
2. Check every hypothesis, domain restriction, and legality condition.
3. Try to refute the attack or repair the challenged step using material already
   established in the proof.
4. Confirm that the defect invalidates a required part of the submitted proof.

Report the attack only if it survives all four checks. If several attacks survive,
select the most concrete, independently verifiable, and damaging one; proof order is
not the selection criterion.

Do not grade, score, rewrite, or repair the proof. Do not report stylistic issues,
multiple objections, preliminary reasoning, or material outside the required record.
Do not use an external solution unless it appears in the allowed established
material.

If no mathematically valid attack survives verification, output exactly:

NO_ADVERSARIAL_BREAK

Otherwise, output exactly:

ADVERSARIAL_BREAK
location: <exact quotation or unambiguous location in the candidate proof>
target_claim: <precise claim being attacked>
attack_type: <COUNTEREXAMPLE | ILLEGAL_CONSTRUCTION | FALSE_CALCULATION | MISSING_CASE | QUANTIFIER_FAILURE | CIRCULARITY | UNSUPPORTED_IMPLICATION>
witness: <explicit counterexample, parameter choice, legal adversarial response, or concise logical obstruction>
verification: <check that the witness satisfies the hypotheses and defeats the target claim>
why_decisive: <how the defect invalidates a required part of the proof>
minimum_requirement: <what must be proved or ruled out for the attack to fail>
END_ADVERSARIAL_BREAK

Keep every field on one physical line. Return only the required output. Perform all
analysis privately."""


ADVERSARIAL_BREAK_RE = re.compile(
    r"\AADVERSARIAL_BREAK\n"
    r"location: ([^\n]+)\n"
    r"target_claim: ([^\n]+)\n"
    r"attack_type: (COUNTEREXAMPLE|ILLEGAL_CONSTRUCTION|FALSE_CALCULATION|MISSING_CASE|QUANTIFIER_FAILURE|CIRCULARITY|UNSUPPORTED_IMPLICATION)\n"
    r"witness: ([^\n]+)\n"
    r"verification: ([^\n]+)\n"
    r"why_decisive: ([^\n]+)\n"
    r"minimum_requirement: ([^\n]+)\n"
    r"END_ADVERSARIAL_BREAK\Z"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def review_user_prompt(*, problem: str, proof: str) -> str:
    problem = problem.strip()
    proof = proof.strip()
    if not problem or not proof:
        raise ValueError("problem and proof must both be nonempty")
    return (
        "# REVIEW INPUT\n\n"
        "## OLYMPIAD PROBLEM\n"
        f"{problem}\n\n"
        "## CANDIDATE PROOF\n"
        f"{proof}\n\n"
        "## ALLOWED ESTABLISHED MATERIAL\n"
        "No external solution or grading information is supplied. Use only the "
        "problem statement, the submitted proof, and valid standard Olympiad-level "
        "mathematics.\n"
    )


def parse_review(value: str) -> dict[str, Any]:
    text = value.strip()
    if text == "NO_ADVERSARIAL_BREAK":
        return {
            "valid": True,
            "errors": [],
            "outcome": "NO_ADVERSARIAL_BREAK",
            "fields": None,
            "final": text,
        }
    match = ADVERSARIAL_BREAK_RE.fullmatch(text)
    if match is None:
        return {
            "valid": False,
            "errors": [
                "output is not the exact ADVERSARIAL_BREAK or "
                "NO_ADVERSARIAL_BREAK form"
            ],
            "outcome": None,
            "fields": None,
            "final": text,
        }
    names = (
        "location",
        "target_claim",
        "attack_type",
        "witness",
        "verification",
        "why_decisive",
        "minimum_requirement",
    )
    fields = {name: field.strip() for name, field in zip(names, match.groups())}
    errors = []
    for name, field in fields.items():
        inserted_lemma_location = name == "location" and re.fullmatch(
            r"<!--\s*LEMMA_UNIT\s+U\d{3}\s*\|\s*[A-Z_]+\s*\|\s*"
            r"L\d{3}(?:-L\d{3})?\s*-->",
            field,
        )
        if not field or (
            field.startswith("<")
            and field.endswith(">")
            and inserted_lemma_location is None
        ):
            errors.append(f"{name} was left empty or as a placeholder")
    return {
        "valid": not errors,
        "errors": errors,
        "outcome": "ADVERSARIAL_BREAK",
        "fields": fields,
        "final": text,
    }
