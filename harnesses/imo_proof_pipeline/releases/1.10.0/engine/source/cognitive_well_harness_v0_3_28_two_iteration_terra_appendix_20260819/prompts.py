from __future__ import annotations

import json
from typing import Any


FIREWALL = """Do not browse, search, retrieve, call tools, consult a gold answer or
reference solution, use a previous verifier verdict, or rely on remembered
problem-specific facts. Use only this packet and elementary logic/algebra. Do
not silently repair omissions."""


def phase_one_score_prompt(*, problem: str, candidate_id: str, proof: str) -> str:
    return f"""You are an independent olympiad proof scorer. {FIREWALL}

Score this one proof from scratch. You are not given and must not infer any
generator score or ranking, and you must not compare it with another proof.
Check the claimed answer, necessity, sufficiency, domains, case coverage, and
every load-bearing inference.

Separately assess its value as a seed for later hypothesis extraction. Credit
only mathematically coherent root characterizations, invariants, constructions,
or obstruction claims; do not reward an idea merely because the proof labels
it as a lemma. The hypothesis-seed assessment does not repair the proof and
does not increase its 0-7 correctness score. Use hypothesis_seed_value 0 when
there is no sound load-bearing structure, 1 for weak structure, 2 for a useful
partially sound idea, and 3 only when the root characterization is plausible
and at least one important load-bearing idea is sound.

Use the IMO 0-7 scale. A complete rigorous proof is 7. A genuine minor slip
whose correction uses only mathematics already present is 6. Score 5 is
disallowed. A gap requiring a new mathematical idea is a fallacy and caps the
score at 3. An incomplete or wrong answer cannot pass. Do not repair the proof.

PROBLEM:
{problem}

CANDIDATE ID: {candidate_id}
PROPOSED SOLUTION:
{proof}
"""


def phase_one_diversity_prompt(
    *,
    problem: str,
    finalist_packets: list[dict[str, Any]],
    eligible_anchor_ids: list[str],
) -> str:
    return f"""You are a proof-portfolio diversity adjudicator. {FIREWALL}

{len(finalist_packets)} finalists are supplied: two independently scored
proofs from each Phase-1 route. Select an ordered pair for joint hypothesis
extraction.

First choose ANCHOR CANDIDATE ID from ELIGIBLE TOP-SCORE ANCHORS. Every ID in
that list shares the highest independent Terra score among the four. If the
list contains a tie, choose the most mathematically sound and useful proof as
the anchor by directly comparing only those tied proofs.

Then choose a different SUPPLEMENT CANDIDATE ID from the other finalists. The
supplement should contribute the strongest complementary mathematical
strategy to the chosen anchor.

The primary objective is mathematical strategy complementarity: prefer a pair
whose root characterizations, invariants, constructions, or necessity and
sufficiency mechanisms expose different load-bearing ideas. Distinguish
substantive strategy diversity from different wording. Evaluate whether each
proof contains useful conjectural structure even when its written proof has a
gap. Individual proof correctness is a secondary quality floor. Do not repair
the proofs and do not author the hypotheses themselves.

You may use the supplied independent Terra score and first-break information.
No Gemma score is supplied. There is no mechanical one-per-route requirement:
route diversity matters only when it reflects substantive strategy diversity.

PROBLEM:
{problem}

ELIGIBLE TOP-SCORE ANCHORS:
{json.dumps(eligible_anchor_ids, ensure_ascii=False)}

FINALISTS:
{json.dumps(finalist_packets, ensure_ascii=False)}
"""


def side_audit_prompt(
    *,
    problem: str,
    claim_id: str,
    side: str,
    exact_claim: str,
    proof: str,
    dependency_statements: list[dict[str, Any]],
) -> str:
    return f"""You are a proof verifier, not a proof author. {FIREWALL}

Audit exactly one side in isolation. Return pass only if every load-bearing
step is supported and the exact claim is reached. Locate the earliest break.

PROBLEM:
{problem}

CLAIM ID: {claim_id}
SIDE: {side}
EXACT CLAIM:
{exact_claim}

ALLOWED VERIFIED DEPENDENCY STATEMENTS:
{json.dumps(dependency_statements, ensure_ascii=False)}

CANDIDATE PROOF:
{proof}
"""


def paired_prompt(
    *, problem: str, claim_id: str, positive: str, negative: str,
    positive_proof: str, negative_proof: str,
) -> str:
    return f"""You are a paired consistency arbiter. {FIREWALL}

Determine the logical relation of each supplied proof to the exact positive
and negative claims. Do not choose a side merely because both isolated calls
passed.

PROBLEM:
{problem}

CLAIM ID: {claim_id}
POSITIVE CLAIM:
{positive}
NEGATIVE CLAIM:
{negative}
POSITIVE PROOF:
{positive_proof}
NEGATIVE PROOF:
{negative_proof}
"""


def proof_attempt_prompt(
    *, problem: str, claim_id: str, side: str, exact_claim: str,
    dependencies: list[dict[str, Any]],
) -> str:
    return f"""Prove the exact assigned claim. Thinking mode is on. Use only
the problem and verified dependencies below. Return a complete standalone
mathematical proof, with no JSON wrapper and no discussion of the opposite
side.

PROBLEM:
{problem}

CLAIM ID: {claim_id}
SIDE: {side}
EXACT CLAIM:
{exact_claim}

VERIFIED DEPENDENCIES, INCLUDING PROOFS:
{json.dumps(dependencies, ensure_ascii=False)}
"""


def repair_attempt_prompt(
    *, problem: str, claim_id: str, side: str, exact_claim: str,
    previous_proof: str, audit: dict[str, Any],
    dependencies: list[dict[str, Any]],
) -> str:
    return f"""Repair one proof of the unchanged exact claim. Thinking mode is
on. Address the verifier's first break without changing sides or strengthening
the claim. Return only a complete replacement proof.

PROBLEM:
{problem}
CLAIM ID: {claim_id}
SIDE: {side}
EXACT CLAIM:
{exact_claim}
VERIFIED DEPENDENCIES, INCLUDING PROOFS:
{json.dumps(dependencies, ensure_ascii=False)}
PREVIOUS PROOF:
{previous_proof}
SAME-SIDE VERIFIER RESULT:
{json.dumps(audit, ensure_ascii=False)}
"""


def child_extraction_prompt(
    *, problem: str, parent_id: str, parent_claim: str, child_id: str,
    failed_proof: str, audit: dict[str, Any], allowed_dependency_ids: list[str],
) -> str:
    return f"""Identify exactly one minimal proof obligation needed at the
first failed step. Thinking mode is on. You author the child; the verifier will
only gate it. The child must be strictly narrower than its parent,
independently checkable, and must include an exact logical negation. Do not
solve the child.

PROBLEM:
{problem}
PARENT ID: {parent_id}
PARENT CLAIM:
{parent_claim}
REQUIRED CHILD ID: {child_id}
ALLOWED DEPENDENCY IDS:
{json.dumps(allowed_dependency_ids)}
FAILED PARENT PROOF:
{failed_proof}
SAME-SIDE VERIFIER RESULT:
{json.dumps(audit, ensure_ascii=False)}
"""


def exact_negation_gate_prompt(
    *, problem: str, claim_id: str, statement: str, exact_negation: str,
) -> str:
    return f"""You are a logical-form gate, not a proof verifier or proof
author. {FIREWALL}

Check only whether NEGATIVE CLAIM is the exact logical negation of POSITIVE
CLAIM. Preserve every domain restriction and reverse all necessary
quantifiers/connectives. Do not assess whether either claim is mathematically
true and do not repair either claim. If invalid, identify the first logical
or quantifier mismatch.

PROBLEM (notation context only):
{problem}

CLAIM ID: {claim_id}
POSITIVE CLAIM:
{statement}
NEGATIVE CLAIM:
{exact_negation}
"""


def exact_negation_repair_prompt(
    *, problem: str, claim_id: str, statement: str, exact_negation: str,
    gate: dict[str, Any],
) -> str:
    return f"""Correct only the exact logical negation. Thinking mode is on.
Do not solve, strengthen, weaken, or rewrite the positive claim. Preserve all
domains and reverse the necessary quantifiers/connectives. Do not return JSON
or Markdown. End with exactly one single-line marker in this form:
EXACT_NEGATION: corrected claim
Write the claim in plain English with Unicode mathematical symbols if needed.
Do not use LaTeX, dollar delimiters, or any backslash character.

PROBLEM (notation context only):
{problem}

CLAIM ID: {claim_id}
UNCHANGED POSITIVE CLAIM:
{statement}
INVALID NEGATION:
{exact_negation}
LOGICAL-FORM GATE RESULT:
{json.dumps(gate, ensure_ascii=False)}
"""


def child_gate_prompt(
    *, problem: str, parent_id: str, parent_claim: str,
    failed_proof: str, audit: dict[str, Any], proposal: dict[str, Any],
    allowed_dependency_ids: list[str],
) -> str:
    return f"""You are a granularity gate, not a proof author. {FIREWALL}

Check whether the proposed child matches the first break, is load-bearing for
the attempted parent route, strictly narrower, independently checkable, has a
valid exact negation, and uses only allowed dependencies. Do not improve or
replace it.

PROBLEM:
{problem}
PARENT ID: {parent_id}
PARENT CLAIM:
{parent_claim}
ALLOWED DEPENDENCY IDS:
{json.dumps(allowed_dependency_ids)}
FAILED PROOF:
{failed_proof}
VERIFIER RESULT:
{json.dumps(audit, ensure_ascii=False)}
PROPOSED CHILD:
{json.dumps(proposal, ensure_ascii=False)}
"""


def global_audit_prompt(*, problem: str, assembled_proof: str) -> str:
    return f"""You are a proof verifier, not a proof author. {FIREWALL}

Audit the body and appendices as one standalone olympiad submission. A body
citation is supported only by the lemma statement and proof included in this
submission. Check the exact answer, every case, all logical bridges, and
finite termination where relevant. Return pass only for a complete proof.

PROBLEM:
{problem}

COMPLETE SUBMISSION:
{assembled_proof}
"""


def body_synthesis_prompt(
    *, problem: str, candidate_id: str, family: str,
    memory: list[dict[str, Any]], ledger: list[dict[str, Any]],
    incumbent_proof: str | None,
) -> str:
    return f"""Write only the main body of a complete olympiad solution.
Thinking mode is on. Do not use external information or a reference answer.

PROBLEM:
{problem}
CANDIDATE ID: {candidate_id}
FAMILY: {family}
INCUMBENT PROOF:
{incumbent_proof if incumbent_proof is not None else 'NOT SUPPLIED.'}
VERIFIED LEMMA MEMORY:
{json.dumps(memory, ensure_ascii=False)}
UNRESOLVED/FAILED LEDGER (NOT FACTS):
{json.dumps(ledger, ensure_ascii=False)}

You may cite verified evidence only with its exact visible syntax `Lemma
<lemma_id>`. The harness will deterministically append exact stored proofs,
including dependency closure. Do not write an appendix. Return only the main
proof body as plain text, with no JSON wrapper or Markdown code fence.
"""


def body_repair_prompt(
    *, problem: str, candidate_id: str, family: str, body: str,
    appendices: list[dict[str, Any]], audit: dict[str, Any],
    memory: list[dict[str, Any]] | None,
) -> str:
    return f"""Rewrite only the main proof body once. Thinking mode is on.
Address the global verifier's first break. Do not author or modify appendices;
the harness will reattach exact verified proofs based on citations.

PROBLEM:
{problem}
CANDIDATE ID: {candidate_id}
FAMILY: {family}
CURRENT BODY:
{body}
CURRENT DETERMINISTIC APPENDICES:
{json.dumps(appendices, ensure_ascii=False)}
VERIFIED MEMORY AVAILABLE TO THIS FAMILY:
{json.dumps(memory or [], ensure_ascii=False)}
GLOBAL VERIFIER RESULT:
{json.dumps(audit, ensure_ascii=False)}

Use exact `Lemma <lemma_id>` citations for any verified lemma used. Return only
the repaired main body as plain text, with no JSON wrapper or Markdown code
fence. Do not write an appendix.
"""
