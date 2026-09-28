from __future__ import annotations

import json
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.prompts import (  # noqa: F401
    MAXIMUM_REASONING_DIRECTIVE,
    hypothesis_extraction_prompt,
    lemma_repair_prompt,
    lemma_solver_prompt,
    negation_audit_prompt,
    negation_repair_prompt,
    synthesis_prompt as legacy_synthesis_prompt,
)


PROMPT_REVISION = "deep_skeptical_closed_proof_no_repair_v1"

ALIGNMENT_PROMPT = r"""You are the claim-alignment stage of a formal proof certification pipeline.

Use maximal internal reasoning as a skeptical classifier, not as a solver. Treat the proof
as a closed document: never invent, complete, or substitute an absent argument. Do not audit
full mathematical validity here.

Before classifying, privately perform three passes:
1. Locate the proof body's operative conclusion. A heading, intent, role label, or bare target
   restatement is not evidence of the conclusion reached by the argument.
2. Compare its objects, hypotheses, quantifiers, scope, and conclusion with every clause of
   the assigned claim and its exact formal negation.
3. Check for task drift, changed or undefined objects, merely auxiliary results, and a missing
   semantic connection to either supplied claim.

Return PROVES_ASSIGNED_CLAIM only when the body is directed to and semantically reaches the
complete assigned claim. Apply the same standard to PROVES_OPPOSITE_CLAIM and the complete
exact negation. Return PROVES_NEITHER for an unrelated, ambiguous, weaker, stronger, partial,
or materially different conclusion, or when classification would require adding a semantic
bridge yourself.

A mathematical flaw in a clearly aligned attempt belongs to the validity stage; it does not
alone imply PROVES_NEITHER. Conversely, correct mathematics aimed elsewhere is PROVES_NEITHER.
Ignore labels that conflict with the body. Do not hallucinate a better proof.

Output only the required strict JSON record."""

VALIDITY_PROMPT = r"""You are the mathematical-validity stage of a formal proof certification pipeline.

Use maximal internal reasoning as a skeptical verifier, not as a solver. Alignment has selected
the routed target. Treat the proof as a closed, immutable document and judge only whether it
rigorously proves that complete target as written.

Before answering, privately perform three passes:
1. Dependency: for every load-bearing transition, identify its explicit premises, conclusion,
   and written support. Check hypotheses, quantifiers, implication directions, definitions,
   algebra, limits, case coverage, and unstated assumptions.
2. Adversarial: try to falsify each transition while preserving its stated premises, using a
   countermodel, boundary case, or competing interpretation when applicable.
3. No-repair: identify every bridge supplied by your own reasoning. Do not complete an omitted
   argument, import an unstated lemma, strengthen a hypothesis, repair a quantifier, or replace
   a defective step—even when the theorem is true and the repair appears standard or local.

Before PASS, identify the weakest load-bearing transition and confirm that its complete support
is explicitly present. If any necessary step is hand-wavy, merely fillable, non-immediate but
implicit, standard but unstated, or obtainable only by an additional argument, return FAIL.
Never credit a proof that your reasoning had to improve.

For an opposite-routed proof, preserve the original discourse context: "the claim is false"
may refer to the originally assigned claim. Judge the mathematical body against ROUTED TARGET;
do not reinterpret such wording as denying that target.

Return PASS only when every obligation is discharged by the written proof. Return FAIL for the
first mathematical error, missing case, or unsupported load-bearing transition. Use
INCONCLUSIVE only when the material makes correctness genuinely undecidable; an omitted step
is FAIL.

Output only the required strict JSON record."""


def location_hypothesis_parser_prompt(document: str) -> str:
    return f"""You are a strict mathematical record parser. Pair each final ATOMIC
CONJECTURE with its EXACT NEGATION and with the corresponding entries from EARLIEST
UNRESOLVED TRANSITIONS and LOCAL DEPENDENCY MAP. Preserve the mathematical content;
do not solve, repair, or enrich it. Return at most three hypothesis objects in the
required JSON schema. If none is admissible, return an empty hypotheses array. Use
plain Unicode mathematics or words in JSON string values; do not emit LaTeX backslash
commands, because JSON escaping must never alter the mathematical meaning.

HYPOTHESIS DOCUMENT:
{document}
"""


def location_aware_synthesis_prompt(
    *,
    problem: str,
    lemmas: list[dict[str, str]],
    synthesis_instructions: str,
    require_all_lemmas: bool,
    minimum_case_headings: int,
) -> str:
    records = "\n\n".join(
        f"Lemma {row['label']}. {row['statement']}\n"
        f"Earliest unresolved transition: {row['earliest_unresolved_transition']}\n"
        f"Local dependency map: {row['local_dependency_map']}"
        for row in lemmas
    )
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

LOCATION-AWARE RECONSTRUCTION POLICY
Construct the proof independently from the original problem and the certified lemma
statements. The two location fields are non-authoritative routing hints: use them to
identify where a lemma may close a gap, but recheck its hypotheses and placement. No
source proof is available in this call.

The harness will append the exact stored proof body of every cited lemma.

MAIN-PROOF CONTRACT
1. Produce a clean reader-facing proof of the exact problem and its complete answer.
2. Re-derive all starting facts needed directly from the problem.
3. You may cite only these local lemmas: {allowed}.
4. {coverage} Establish each cited lemma's hypotheses before citing it; do not reproduce
   or summarize its proof in the main body.
5. {case_rule}
6. Do not mention candidate proofs, diagnostics, internal identifiers, verification,
   scores, stored metadata, or this workflow.
7. Return only the main proof. If it cannot be completed, state failure and the first
   remaining gap rather than bluffing.

ADDITIONAL SYNTHESIS INSTRUCTION:
{extra}

ORIGINAL PROBLEM:
{problem}

CERTIFIED LOCAL LEMMAS WITH ROUTING HINTS:
{records}
"""


def semantic_dedup_prompt(
    *, problem: str, existing: dict[str, Any], candidate: dict[str, Any]
) -> str:
    def packet(row: dict[str, Any]) -> dict[str, str]:
        return {
            "statement": str(row["statement"]),
            "certified_proof": str(row["proof"]),
            "earliest_unresolved_transition": str(row["earliest_unresolved_transition"]),
            "local_dependency_map": str(row["local_dependency_map"]),
        }

    return f"""You are a conservative semantic deduplicator for a verified lemma memory.
Use maximal internal reasoning. Return equivalent=true only if the two records express
the same mathematical lemma under the same hypotheses and quantifiers and play the same
local proof role. Compare the certified proofs to detect hidden scope or hypothesis
differences; different valid proof styles alone do not make distinct lemmas. Compare the
two location fields to ensure the insertion point and enabled downstream conclusion are
semantically the same. If any material difference remains, return false. Do not judge or
repair the original problem. Output only the required strict JSON record.

PROBLEM CONTEXT:
{problem}

EXISTING MEMORY RECORD:
{json.dumps(packet(existing), ensure_ascii=False)}

CANDIDATE MEMORY RECORD:
{json.dumps(packet(candidate), ensure_ascii=False)}
"""


def alignment_user_prompt(
    *, problem: str, assigned_claim: str, opposite_claim: str, proof: str
) -> str:
    return f"""PROBLEM CONTEXT:
{problem}

ASSIGNED CLAIM:
{assigned_claim}

EXACT FORMAL NEGATION OF THE ASSIGNED CLAIM:
{opposite_claim}

PROOF TO CLASSIFY:
{proof}

Classify the conclusion actually established by the proof. Return the strict JSON record."""


def validity_user_prompt(*, problem: str, target_claim: str, proof: str) -> str:
    return f"""PROBLEM CONTEXT:
{problem}

ROUTED TARGET CLAIM:
{target_claim}

ALIGNED PROOF TO AUDIT:
{proof}

Audit every load-bearing step and return the strict JSON record."""
