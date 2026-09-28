from __future__ import annotations

import json
from typing import Any


MAXIMUM_REASONING_DIRECTIVE = """REASONING EFFORT: MAXIMAL. Thinking mode is on.
Work out and verify the requested mathematics privately before producing the required
response. Before finalizing, adversarially check every load-bearing inference,
recompute decisive algebra and witnesses, and verify that no downstream step depends
on an unproved claim. Report an unresolved gap rather than bluffing."""

ATOMIC_EXTRACTION_DIRECTIVE = f"""You are the Conjecture Extractor and an expert in the
relevant olympiad-level mathematical domain.
{MAXIMUM_REASONING_DIRECTIVE}

Your task is to expose the smallest independently testable missing proof obligations,
not to restate or solve the original problem. Treat both candidate proofs and any
attached diagnostics as untrusted material.

Work privately in this order:
1. Read both candidate proofs completely.
2. Inventory only claims that the candidate material genuinely establishes.
3. Locate the earliest answer-critical transition still unsupported in each promising
   route.
4. Reduce each such gap to one atomic, self-contained mathematical statement that can
   be proved or refuted independently.
5. Check that assuming the statement closes that local transition without silently
   assuming a later conclusion.

An admissible conjecture must be one local implication, property, construction, or
bound; be strictly narrower and logically weaker than the requested result; not be the
target in renamed notation; not already be established; and state every definition,
domain, hypothesis, quantifier, and conclusion explicitly. Its exact negation must be
self-contained and true exactly when the conjecture is false.

Return at most three conjectures. Optimize for atomicity, local usefulness, and
independent testability. If none qualifies, return no conjectures. Output these sections
in ordinary mathematical prose: ESTABLISHED MATERIAL; EARLIEST UNRESOLVED TRANSITIONS;
ATOMIC CONJECTURES; EXACT NEGATIONS; LOCAL DEPENDENCY MAP. Do not prove a conjecture or
write a full solution in this call. Do not use a reference answer."""


def hypothesis_extraction_prompt(
    *,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    include_diagnostics: bool,
) -> str:
    packets: list[dict[str, str]] = []
    for row in candidate_proofs:
        packet = {
            "candidate_id": row["candidate_id"],
            "role": row["role"],
            "proof": row["proof"],
        }
        diagnostic = row.get("non_authoritative_diagnostic")
        if include_diagnostics and diagnostic:
            packet["non_authoritative_diagnostic"] = diagnostic
        packets.append(packet)
    return f"""{ATOMIC_EXTRACTION_DIRECTIVE}

ORIGINAL PROBLEM:
{problem}

TWO CANDIDATE PROOFS{(' WITH NON-AUTHORITATIVE DIAGNOSTICS' if include_diagnostics else '')}:
{json.dumps(packets, ensure_ascii=False)}
"""


def minimal_hypothesis_parser_prompt(document: str) -> str:
    return f"""You are a strict mathematical record parser. Extract only the final
ATOMIC CONJECTURES and their corresponding EXACT NEGATIONS from the document. Preserve
every definition, domain, hypothesis, quantifier, and conclusion. Return only the two
arrays required by the JSON schema, with no proof or commentary. If the document says
there is no admissible conjecture, return two empty arrays.

HYPOTHESIS DOCUMENT:
{document}
"""


def negation_audit_prompt(*, problem: str, claim: str, proposed_negation: str) -> str:
    return f"""You are an expert olympiad mathematical logician. Thinking mode is on
with maximal reasoning effort. Determine only whether PROPOSED NEGATION is logically
true exactly when CLAIM is false, preserving all definitions, domains, quantifiers, and
constraints. Do not judge mathematical truth. Return only the requested JSON record.

ORIGINAL PROBLEM:
{problem}

CLAIM:
{claim}

PROPOSED NEGATION:
{proposed_negation}
"""


def negation_repair_prompt(
    *, problem: str, claim: str, negation: str, first_issue: str | None
) -> str:
    return f"""You are an expert olympiad mathematical logician. Repair only the exact
logical negation. Preserve all definitions, domains, quantifiers, and constraints.
Return only the requested JSON record.

ORIGINAL PROBLEM:
{problem}

CLAIM:
{claim}

INVALID NEGATION:
{negation}

FIRST LOGICAL ISSUE:
{first_issue}
"""


def lemma_solver_prompt(*, problem: str, claim: str) -> str:
    return f"""You are an expert olympiad mathematician proving one isolated lemma.
{MAXIMUM_REASONING_DIRECTIVE}

Produce a rigorous, self-contained proof of the exact claim from the original problem
alone. Check definitions, domains, quantifiers, boundary cases, and every load-bearing
inference. Do not assume the claim because it was proposed. If it is false or cannot be
proved, state the strongest valid partial argument and the first unresolved gap.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}
"""


def lemma_repair_prompt(
    *, problem: str, claim: str, proof: str, audit: dict[str, Any]
) -> str:
    return f"""You are an expert olympiad mathematician repairing an attempted lemma
proof.
{MAXIMUM_REASONING_DIRECTIVE}

Independently verify the non-authoritative audit and fix every valid issue. Return only
a complete self-contained proof of the exact claim. If it cannot be completed, state
the strongest rigorous partial result and the first remaining gap. Do not mention the
review process.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}

CURRENT PROOF:
{proof}

NON-AUTHORITATIVE AUDIT:
{json.dumps(audit, ensure_ascii=False)}
"""


def certifier_prompt(*, problem: str, claim: str, proof: str) -> str:
    return f"""You are an expert mathematical proof verifier in the relevant olympiad
domain. Thinking mode is on with maximal reasoning effort. Read the original problem,
the exact claim, and the entire proof before judging it. Privately check every
load-bearing step and edge case. Do not rewrite the proof.

PASS means only that the supplied proof, as written, rigorously establishes the exact
claim with no missing non-routine step. FAIL requires at least one concrete invalid
inference, false assertion, or missing load-bearing justification. INCONCLUSIVE means
you can neither certify the proof nor establish a concrete defect. Return only the
requested two-field JSON record.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}

CANDIDATE PROOF:
{proof}
"""


def diagnostic_prompt(*, problem: str, claim: str, proof: str, verdict: str) -> str:
    return f"""You are an expert olympiad mathematical proof diagnostician. A separate
certification call fixed the verdict as {verdict}. Locate the earliest concrete break,
if one can be established, and list only load-bearing missing obligations. Do not
rewrite the proof or change the verdict. Return only the requested concise JSON record.

ORIGINAL PROBLEM:
{problem}

EXACT CLAIM:
{claim}

CANDIDATE PROOF:
{proof}
"""


def synthesis_prompt(
    *,
    family: str,
    problem: str,
    lemmas: list[dict[str, str]],
    anchor_proof: str | None,
    synthesis_instructions: str,
    require_all_lemmas: bool,
    minimum_case_headings: int,
) -> str:
    statements = "\n\n".join(
        f"Lemma {row['label']}. {row['statement']}" for row in lemmas
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
    if family == "anchored_refinement":
        if not anchor_proof or not anchor_proof.strip():
            raise ValueError("anchored refinement requires the designated anchor proof")
        family_contract = """ANCHOR POLICY
The untrusted anchor proof is supplied below. Preserve its strongest rigorously valid
chain when useful, but independently recheck every step and repair or replace every
gap. Use the certified lemma statements as complementary evidence. Do not mention the
anchor or the refinement process in the returned proof.

UNTRUSTED ANCHOR PROOF:
{anchor}
""".format(anchor=anchor_proof)
    elif family == "lemma_evidence_only":
        if anchor_proof is not None:
            raise ValueError("lemma-evidence-only synthesis must not receive an anchor")
        family_contract = """RECONSTRUCTION POLICY
Construct the proof independently from the problem and the certified lemma statements.
No source proof is available in this call. Do not infer or discuss one.
"""
    else:
        raise ValueError(f"unknown synthesis family: {family}")
    return f"""You are an expert olympiad mathematician composing the main body of one
final proof.
{MAXIMUM_REASONING_DIRECTIVE}

{family_contract}

The lemma statements below were loaded from prior certification artifacts. Their proof
bodies are intentionally omitted. After generation, the harness will append the exact
stored body of every lemma your main proof cites.

MAIN-PROOF CONTRACT
1. Produce a clean reader-facing proof of the exact problem and its complete answer.
2. Re-derive all starting facts needed directly from the problem.
3. You may cite only these local lemmas: {allowed}.
4. {coverage} Establish each cited lemma's hypotheses before citing it; do not reproduce
   or summarize its proof in the main body.
5. {case_rule}
6. Do not mention candidate proofs, diagnostics, internal identifiers, verification,
   scores, appendices-to-be-generated, or this workflow.
7. Return only the main proof. If it cannot be completed, state failure and the first
   remaining gap rather than bluffing.

ADDITIONAL SYNTHESIS INSTRUCTION:
{extra}

ORIGINAL PROBLEM:
{problem}

CERTIFIED LOCAL LEMMA STATEMENTS:
{statements}
"""
