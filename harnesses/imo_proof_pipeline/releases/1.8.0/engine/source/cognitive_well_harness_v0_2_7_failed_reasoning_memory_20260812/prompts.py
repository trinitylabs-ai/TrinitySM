"""Benchmark-neutral prompts implementing Appendix F roles.

These prompts preserve the functional instructions and multi-persona control
flow of the paper while using compact wording suitable for a local model.
"""

from __future__ import annotations

import json
from typing import Any


def dialectic_solver(problem: str, context: Any | None, feedback: str | None = None) -> str:
    materials = "None" if context in (None, [], {}) else json.dumps(context, ensure_ascii=False)
    feedback_text = "None" if not feedback else feedback
    return f"""You are the Dialectic Solver for a difficult olympiad problem. Thinking mode is on.

Use an internal council with these roles: a Classicist using established theorems,
a Visionary proposing connections, an Experimenter testing examples, Momus attacking
strategy, Veritas checking every deductive step, and a Chief Architect controlling the
process. Additional materials are unverified hints: any nonstandard lemma used from
them must be proved from scratch.

Run at most three global rounds.
1. Ideation: list materially different promising avenues, pre-mortem each for red
   herrings, and select an active strategy.
2. Dialectic loop: begin each round with a one-line poetic cognitive reset; draft or
   refine; reject and expand lazy phrases; let Momus discard a fatally flawed
   strategy; let Veritas flag invisible steps; switch strategy or repair until
   convergence or the round budget ends.
3. Synthesis: give a short discovery log and a clean reviewer-ready proof.

The final proof must restate what is proved, be self-contained, check all cases and
both directions, and finish with the exact short answer in \\boxed{{}}. If no complete
proof is reached, preserve the strongest rigorous partial result and say exactly what
remains. Do not use a reference answer.

PROBLEM:
{problem}

ADDITIONAL MATERIALS:
{materials}

EXTERNAL FEEDBACK FOR THIS DRAFT:
{feedback_text}
"""


def lazy_phrasing(proof: str) -> str:
    return f"""Thinking mode is on. Scan the proof for immediately obvious omitted
derivations or lazy phrases such as 'it is clear', 'one can show', 'well-known',
'standard argument', or an unexplained nontrivial simplification. List each exact
issue briefly. If there are absolutely no such issues, output exactly NO_ISSUES.

PROOF:
{proof}
"""


def inquisitorial_grader(problem: str, proof: str, additional: Any | None = None) -> str:
    materials = "None" if additional in (None, [], {}) else json.dumps(additional, ensure_ascii=False)
    return f"""You are the paper's simplified Council of Graders. Thinking mode is on.
Adopt a guilty-until-proven-innocent standard and run at most three short rounds.

The Inquisitor attacks line-by-line validity; the Architect checks global sufficiency
and magic steps; a Defender gives the strongest possible rebuttal; the Chief Grader
rules. Begin with an indictment. In each round perform a pre-mortem: assume the proof
looks correct but is false and identify a concrete edge case or logical failure. A
defense succeeds only if the gap is repairable using mathematics already written.

Classify remaining errors as slips or fallacies. A slip loses one point. A fallacy or
incomplete answer requiring new mathematics caps the score at 3. Score 7 only for a
complete rigorous proof with no unresolved gap; score 6 for a genuine minor slip;
use 2-4 for incomplete or substantially flawed work only when consistent with the
fallacy cap, and 0-1 for irrelevant work. Do not assign 5.

Write the concise grading forum and final verdict in ordinary plaintext, following
the appendix report style. End with exactly one separate terminal line of the form
FINAL_GRADE: N/7, where N is the score. Do not write anything after that line. Do
not use a reference solution.

PROBLEM OR STANDALONE CLAIM:
{problem}

SOLUTION:
{proof}

ADDITIONAL MATERIALS:
{materials}
"""


def refine(problem: str, proof: str, grade: dict[str, Any], context: Any | None) -> str:
    materials = "None" if context in (None, [], {}) else json.dumps(context, ensure_ascii=False)
    return f"""You are the Dialectic Solver refining one olympiad proof. Thinking mode is on.
Use the grader's indictment as questions to resolve, not as truth. Recheck the strategy
from the original problem, repair every valid slip or fallacy, and switch strategy if
the gap needs new mathematics. Additional materials are unverified unless reproved.
Return a complete, self-contained reviewer-ready proof with an exact \\boxed{{}} answer.
If completion is impossible, state the strongest rigorous partial result and the first
remaining gap. Do not mention a reference answer.

PROBLEM:
{problem}

CURRENT PROOF:
{proof}

GRADER FEEDBACK:
{json.dumps(grade, ensure_ascii=False)}

ADDITIONAL MATERIALS:
{materials}
"""


def conjecture_extractor(
    problem: str,
    seed_solutions: list[dict[str, Any]],
    lemma_memory: list[dict[str, Any]],
    failed_lemma_memory: list[dict[str, Any]],
    failure_context: list[dict[str, Any]],
) -> str:
    return f"""You are the paper's Conjecture Extractor. Thinking mode is on.
Internally run three rounds among a Formalist, Strategist, Defender, and Chief
Architect. Critique each candidate, let the Defender rebut, then refine the critique.
For each surviving gap the Strategist must first try standard deduction. Only if that
fails may the council state a conjecture.

Consolidate to at most the three most load-bearing self-contained conjectures. Use as
few as possible. Each conjecture and its negation must independently restate every
definition, domain, quantifier, and constraint; the negation must be true exactly when
the conjecture is false. Ignore hopeless proofs needing too many fixes.

The FAILED LEMMA MEMORY is authoritative negative progress for this problem. Do not
repeat or paraphrase a refuted lemma. Do not resubmit an unproved lemma unless the new
statement itself repairs the recorded failure or materially changes the proof
obligation. A grader conflict is unresolved evidence, not a theorem. If a repaired
statement is proposed, make the repair explicit in the statement rather than merely
promising a different proof later.

The memory also records failed reasoning steps. Do not change only the conclusion
while reusing an unsupported implication. For every proposed conjecture, work in one
of two directions: derive a precise structural fact forward from the original
definitions, or formulate the smallest missing implication needed by the current
proof. The proof assuming the conjectures must expose exactly how each conjecture is
used. Make the surviving conjectures materially distinct in their logical
dependencies, not merely their wording.

Then synthesize one rigorous proof of the original problem which is complete if the
listed conjectures are assumed. Do not prove the conjectures in this call and do not
use a reference answer.

Output these sections: GRADING SUMMARY; LIST OF CONJECTURES; NEGATIONS OF
CONJECTURES; RIGOROUS PROOF ASSUMING CONJECTURES.

PROBLEM:
{problem}

CANDIDATE SOLUTIONS AND GRADES:
{json.dumps(seed_solutions, ensure_ascii=False)}

LEMMA MEMORY:
{json.dumps(lemma_memory, ensure_ascii=False)}

FAILED LEMMA MEMORY:
{json.dumps(failed_lemma_memory, ensure_ascii=False)}

FAILURE CONTEXT:
{json.dumps(failure_context, ensure_ascii=False)}
"""


def failed_lemma_screen(
    problem: str,
    conjectures: list[str],
    assumed_proof: str,
    failed_lemma_memory: list[dict[str, Any]],
) -> str:
    return f"""You are a strict semantic duplicate screen for mathematical lemmas.
Thinking mode is on only to compare logical dependencies accurately. Use no reference
answer. Compare each new candidate with the failed-lemma memory for this same problem.

Judge mathematical equivalence and dependence, not shared wording. Mark a candidate
`equivalent_refuted` when it entails or merely paraphrases a refuted lemma without
removing the counterexample. Mark it `equivalent_unproved` when it repeats an unproved
claim without changing the statement in a way that resolves the recorded gap. Mark it
`equivalent_grader_conflict` when it repeats a claim whose evidence is internally
inconsistent. Mark `repaired` only when the candidate statement itself adds, removes,
or sharpens conditions that explicitly address every matched failure. Otherwise mark
`new`.

Also inspect how each conjecture is used in the supplied proof. Mark
`reuses_failed_reasoning` when a candidate or its use depends on an unsupported
inference recorded in memory without proving the missing implication. Treat that
unsupported implication as the repeated object even when the candidate conclusion
or notation changes. Compare the
new candidates with one another. If two candidates play the same logical role with
the same premises and unsupported bridge, retain the more precise and independently
testable representative and mark the other `sibling_duplicate`. Different wording or
different final constants are not logical diversity.

Return exactly one decision for every candidate index, in index order. Never reject a
candidate merely because it uses the same elementary notation or broad field.

PROBLEM:
{problem}

CANDIDATES:
{json.dumps(conjectures, ensure_ascii=False)}

PROOF ASSUMING THE CANDIDATES:
{assumed_proof}

FAILED LEMMA MEMORY:
{json.dumps(failed_lemma_memory, ensure_ascii=False)}
"""


def conjecture_parser(document: str) -> str:
    return f"""You are the paper's Conjecture Parser. Thinking mode is on only to
ensure accurate logical extraction. Parse the document into the requested JSON.
Extract each complete conjecture, its corresponding complete self-contained exact
negation, and the rigorous proof assuming them. The two arrays must have equal length.
Remove section headers from statements. If none exist, return empty arrays. Do not
change, prove, or improve the mathematics.

DOCUMENT:
{document}
"""


def standalone_solver(claim: str) -> str:
    return f"""You are a fresh Dialectic Solver given one standalone mathematical
claim and no parent context. Thinking mode is on. Test examples, consider materially
different strategies, and produce a rigorous self-contained proof. Do not infer an
original problem or use a reference answer. If the claim cannot be proved, preserve
the strongest valid partial result and identify the first gap.

CLAIM:
{claim}
"""


def answer_combiner(problem: str, solution_a: str, solution_b: str, history: Any) -> str:
    return f"""You are the paper's Council of Solution Evaluators. Thinking mode is on.
Compare two final solutions using at most two rounds. The Inquisitor and Architect
indict both; separate advocates defend A and B; the Chief Evaluator performs a
pre-mortem for each and rules. Correctness is paramount, then rigor, completeness,
and clarity. Additional history is unverified context. Return only the requested JSON
and do not use a reference solution.

PROBLEM:
{problem}

SOLUTION A:
{solution_a}

SOLUTION B:
{solution_b}

ADDITIONAL HISTORY:
{json.dumps(history, ensure_ascii=False)}
"""
