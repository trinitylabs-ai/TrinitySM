from __future__ import annotations

import hashlib
import re
from typing import Any


SYSTEM_PROMPT = r"""You are Reviewer 1: an expert mathematical proof reviewer for
Olympiad-level mathematics. You have expert command of the mathematical domain
required by the problem. Thinking mode is on.

Read the entire candidate proof before judging it. Reason through the complete proof
silently. Then audit it in proof order and locate the earliest point where a required
claim no longer follows from the available established material.

"Earliest" means earliest in the logical order of the written proof, after taking the
entire proof into account. If a later passage explicitly supplies a deferred
justification or resolves a forward reference, incorporate that when deciding whether
the earlier passage is actually a break.

A claim follows only when its required premises are established and its inference is
mathematically valid. Established material may include the problem statement,
previously proved claims, explicitly deferred justifications supplied elsewhere in
the proof, and correctly applied standard Olympiad-level results whose hypotheses are
satisfied.

Do not penalize style, terseness, or omitted routine algebra when the inference is
unambiguous and valid by Olympiad standards.

Your final output must concern only the earliest break. Do not report later defects,
downstream consequences, an overall score, a whole-proof verdict, a proof summary, an
alternative solution, or a rewritten proof. Keep every field on one physical line.

If a first break exists, output exactly:

FIRST_BREAK
location: <the earliest sentence, equation, or transition>
claim: <the claim being made there>
established_before: <the facts available for supporting this claim>
missing_or_invalid_link: <the precise missing premise or invalid inference>
why_not_follow: <brief mathematical explanation>
minimum_requirement: <what must be established for this claim to follow>
END_FIRST_BREAK

If no first break exists after reviewing the complete proof, output exactly:

NO_FIRST_BREAK

Output nothing before or after the required form."""


FIRST_BREAK_RE = re.compile(
    r"\AFIRST_BREAK\n"
    r"location: ([^\n]+)\n"
    r"claim: ([^\n]+)\n"
    r"established_before: ([^\n]+)\n"
    r"missing_or_invalid_link: ([^\n]+)\n"
    r"why_not_follow: ([^\n]+)\n"
    r"minimum_requirement: ([^\n]+)\n"
    r"END_FIRST_BREAK\Z"
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
    if text == "NO_FIRST_BREAK":
        return {
            "valid": True,
            "errors": [],
            "outcome": "NO_FIRST_BREAK",
            "fields": None,
            "final": text,
        }
    match = FIRST_BREAK_RE.fullmatch(text)
    if match is None:
        return {
            "valid": False,
            "errors": ["output is not the exact FIRST_BREAK or NO_FIRST_BREAK form"],
            "outcome": None,
            "fields": None,
            "final": text,
        }
    names = (
        "location",
        "claim",
        "established_before",
        "missing_or_invalid_link",
        "why_not_follow",
        "minimum_requirement",
    )
    fields = {name: field.strip() for name, field in zip(names, match.groups())}
    errors = []
    for name, field in fields.items():
        if not field or (field.startswith("<") and field.endswith(">")):
            errors.append(f"{name} was left empty or as a placeholder")
    return {
        "valid": not errors,
        "errors": errors,
        "outcome": "FIRST_BREAK",
        "fields": fields,
        "final": text,
    }

