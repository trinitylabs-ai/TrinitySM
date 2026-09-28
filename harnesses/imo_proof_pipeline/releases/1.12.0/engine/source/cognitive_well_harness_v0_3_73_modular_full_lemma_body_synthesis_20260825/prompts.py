from __future__ import annotations

import json

from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.prompts import (  # noqa: F401
    ALIGNMENT_PROMPT,
    MAXIMUM_REASONING_DIRECTIVE,
    PROMPT_REVISION,
    VALIDITY_PROMPT,
    alignment_user_prompt,
    hypothesis_extraction_prompt,
    lemma_repair_prompt,
    lemma_solver_prompt,
    legacy_synthesis_prompt,
    location_aware_synthesis_prompt,
    location_hypothesis_parser_prompt,
    negation_audit_prompt,
    negation_repair_prompt,
    semantic_dedup_prompt,
    validity_user_prompt,
)


def full_lemma_body_synthesis_prompt(
    *,
    problem: str,
    lemmas: list[dict[str, str]],
    candidate_proofs: list[dict[str, str]],
    synthesis_instructions: str,
    require_all_lemmas: bool,
    minimum_case_headings: int,
) -> str:
    records = "\n\n".join(
        f"Lemma {row['label']}. {row['statement']}\n"
        f"Certified proof body:\n{row['proof']}\n"
        f"Earliest unresolved transition: {row['earliest_unresolved_transition']}\n"
        f"Local dependency map: {row['local_dependency_map']}"
        for row in lemmas
    )
    proof_packets = [
        {
            "candidate_id": str(row["candidate_id"]),
            "role": str(row["role"]),
            "proof": str(row["proof"]),
        }
        for row in candidate_proofs
    ]
    allowed = ", ".join(f"Lemma {row['label']}" for row in lemmas)
    coverage = (
        "Cite every listed lemma at the precise point where it is used."
        if require_all_lemmas
        else "Cite only the listed lemmas that are genuinely needed."
    )
    case_rule = (
        f"Use at least {minimum_case_headings} explicit CASE headings and prove that "
        "the cases are exhaustive."
        if minimum_case_headings
        else "Use an explicit case split only when the mathematics requires one."
    )
    extra = synthesis_instructions.strip() or "No additional problem-specific instruction."
    return f"""You are an expert olympiad mathematician composing the main body of one
final proof.
{MAXIMUM_REASONING_DIRECTIVE}

FULL-LEMMA-BODY FUSION POLICY
Each local lemma below is supplied with its complete certified proof body and two
non-authoritative routing fields. Use the body to understand the lemma's exact
hypotheses, mechanism, and valid insertion point. The two selected candidate proofs are
also supplied as untrusted source material. Preserve their strongest rigorously valid
chains when useful, but independently recheck every step and repair or replace every gap.

The harness will append the exact stored proof body of every cited lemma, so cite a lemma
at its point of use without copying or summarizing its proof into the main body.

MAIN-PROOF CONTRACT
1. Produce a clean reader-facing proof of the exact problem and its complete answer.
2. Re-derive all starting facts needed directly from the problem.
3. You may cite only these local lemmas: {allowed}.
4. {coverage} Establish each cited lemma's hypotheses before citing it.
5. {case_rule}
6. Do not mention candidate proofs, diagnostics, internal identifiers, verification,
   scores, stored metadata, or this workflow.
7. Return only the main proof. If it cannot be completed, state failure and the first
   remaining gap rather than bluffing.

ADDITIONAL SYNTHESIS INSTRUCTION:
{extra}

ORIGINAL PROBLEM:
{problem}

TWO UNTRUSTED CANDIDATE PROOFS:
{json.dumps(proof_packets, ensure_ascii=False)}

CERTIFIED LOCAL LEMMAS WITH COMPLETE PROOF BODIES AND ROUTING HINTS:
{records}
"""
