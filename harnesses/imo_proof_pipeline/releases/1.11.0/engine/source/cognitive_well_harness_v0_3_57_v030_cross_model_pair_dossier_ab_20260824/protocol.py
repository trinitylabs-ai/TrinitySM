from __future__ import annotations

import json
from typing import Any


REPETITION_DETECTION = {
    "min_pattern_size": 8,
    "max_pattern_size": 128,
    "min_count": 3,
}

HYPOTHESIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["conjectures", "negations", "proof"],
    "properties": {
        "conjectures": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 20},
        },
        "negations": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 20},
        },
        "proof": {"type": "string", "minLength": 20},
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

PROOF_AUDIT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "verdict",
        "earliest_break",
        "exact_claim_reached",
        "missing_obligations",
        "summary",
        "confidence",
    ],
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "INCONCLUSIVE"]},
        "earliest_break": {"type": ["string", "null"]},
        "exact_claim_reached": {"type": "boolean"},
        "missing_obligations": {
            "type": "array",
            "maxItems": 8,
            "items": {"type": "string", "minLength": 1},
        },
        "summary": {"type": "string", "minLength": 1},
        "confidence": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
    },
}


def parse_json_object(value: str) -> dict[str, Any]:
    text = value.strip()
    if text.startswith("```"):
        text = text[3:]
        if text.startswith("json") and (
            len(text) == 4 or text[4].isspace() or text[4] == "{"
        ):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    candidates = [text]
    if text.startswith("{{"):
        candidates.append(text[1:])
    errors: list[str] = []
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as error:
            errors.append(str(error))
            continue
        if isinstance(parsed, dict):
            return parsed
        errors.append("decoded value is not an object")
    raise ValueError("invalid JSON object: " + " | ".join(errors))


def normalize_hypothesis_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize only Gemma's singular-vs-array serialization slip."""

    if "proof" not in record and set(record) == {"conjectures", "negations", "proofs"}:
        proofs = record.get("proofs")
        if isinstance(proofs, list) and len(proofs) == 1 and isinstance(proofs[0], str):
            return {
                "conjectures": record["conjectures"],
                "negations": record["negations"],
                "proof": proofs[0],
            }
    return record


def qwen_verifier_system_prompt() -> str:
    return """You are an expert mathematical proof verifier in the relevant olympiad domain.
Thinking mode is on with maximal reasoning effort. Read the original problem, the exact
claim, and the entire candidate proof before judging it. Work through every load-bearing
step and all edge cases. Your sole task is certification or identification of the
earliest concrete break; do not rewrite the proof and do not solve a different claim.

PASS has one exact meaning: the supplied proof, as written, rigorously establishes the
exact claim with no missing non-routine step. FAIL requires a specific earliest invalid
inference, false assertion, or missing load-bearing justification. Use INCONCLUSIVE when
you cannot certify the proof but cannot isolate a concrete earliest defect. Finding no
defect is not proof that the claim is false, and refuting one attempted proof is not
refuting the claim. Return only the requested JSON record; never emit a numerical score."""


def qwen_negation_verifier_system_prompt() -> str:
    return """You are an expert olympiad mathematical logician. Thinking mode is on
with maximal reasoning effort. Judge only whether a proposed statement is the exact
logical negation of a supplied claim, preserving every definition, domain, quantifier,
and constraint. Do not judge mathematical truth and do not audit a proof. Return only
the requested JSON object with exactly `valid_exact_negation` and `first_issue`.
`first_issue` must be null when valid and a concrete string when invalid."""


def negation_audit_prompt(*, problem: str, claim: str, proposed_negation: str) -> str:
    return f"""Determine only whether PROPOSED NEGATION is logically true exactly when
CLAIM is false, with the same domain, quantifiers, and definitions. Do not judge whether
either statement is mathematically true. If invalid, identify the first logical issue.

PROBLEM:
{problem}

CLAIM:
{claim}

PROPOSED NEGATION:
{proposed_negation}
"""


def proof_audit_prompt(*, problem: str, claim: str, proof: str) -> str:
    return f"""Audit the candidate proof against exactly the supplied claim.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}

CANDIDATE PROOF:
{proof}
"""


def lemma_solver_prompt(*, problem: str, claim: str) -> str:
    return f"""You are an olympiad-level mathematical expert proving one isolated lemma.
Thinking mode is on with maximal reasoning effort. Produce a rigorous, self-contained
proof of the exact claim from the original problem alone. Check definitions, domains,
quantifiers, boundary cases, and every load-bearing inference. Do not assume the claim
merely because it was proposed. If it is false or you cannot complete a proof, preserve
the strongest valid partial argument and state the first unresolved gap.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}
"""


def lemma_repair_prompt(
    *, problem: str, claim: str, proof: str, audit: dict[str, Any]
) -> str:
    return f"""You are an olympiad-level mathematical expert revising an attempted lemma
proof. Thinking mode is on with maximal reasoning effort. Independently verify the audit,
then repair every valid issue. Return only a complete self-contained proof of the exact
claim. If the claim cannot be proved, state the strongest rigorous partial result and the
first remaining gap. Do not mention the review process.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}

CURRENT PROOF:
{proof}

NONAUTHORITATIVE QWEN AUDIT:
{json.dumps(audit, ensure_ascii=False)}
"""


def synthesis_prompt(
    *,
    family: str,
    problem: str,
    seeds: list[dict[str, str]],
    verified: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
) -> str:
    mode = (
        "Use the strongest valid chain from the anchor and splice in only rigorously "
        "needed complementary material."
        if family == "anchor_plus_evidence"
        else "Reconstruct the proof independently from the verified evidence, using the seed proofs only as untrusted leads."
    )
    return f"""You are an olympiad-level mathematical expert producing the final proof.
Thinking mode is on with maximal reasoning effort. {mode}

Every supplied seed and failed-proof diagnosis is nonauthoritative. Recheck it from the
problem. Verified lemmas may be used only with their exact statements and proofs. Repair
all gaps explicitly, including zero/boundary cases. Return one clean, self-contained,
reviewer-ready proof and the complete answer. Do not discuss candidates, dossiers,
reviewers, scores, or this workflow.

PROBLEM:
{problem}

SEED PROOFS:
{json.dumps(seeds, ensure_ascii=False)}

QWEN-CERTIFIED LEMMAS:
{json.dumps(verified, ensure_ascii=False)}

UNRESOLVED OR REFUTED PROOF ATTEMPTS:
{json.dumps(unresolved, ensure_ascii=False)}
"""


def final_repair_prompt(
    *, problem: str, proof: str, audit: dict[str, Any]
) -> str:
    return f"""You are an olympiad-level mathematical expert repairing a final proof.
Thinking mode is on with maximal reasoning effort. Independently check the audit and fix
every valid issue without referring to the audit. Return only a clean, self-contained
proof and complete answer. If the identified gap cannot be repaired, state the strongest
rigorous partial result and its first remaining gap rather than bluffing.

PROBLEM:
{problem}

CURRENT PROOF:
{proof}

NONAUTHORITATIVE QWEN AUDIT:
{json.dumps(audit, ensure_ascii=False)}
"""
