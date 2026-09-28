from __future__ import annotations

import json
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.prompts import (
    ATOMIC_EXTRACTION_DIRECTIVE,
    MAXIMUM_REASONING_DIRECTIVE,
)


def iterative_extraction_prompt(
    *,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
) -> str:
    proof_packets = [
        {
            "candidate_id": row["candidate_id"],
            "role": row["role"],
            "proof": row["proof"],
            "qwen_defect_packet": row["qwen_defect_packet"],
            "fusion_defect_packet": row["fusion_defect_packet"],
        }
        for row in candidate_proofs
    ]
    certified = [
        {
            "statement": row["statement"],
            "earliest_unresolved_transition": row[
                "earliest_unresolved_transition"
            ],
            "local_dependency_map": row["local_dependency_map"],
        }
        for row in certified_memory
    ]
    failed = [
        {
            "failed_id": row["failed_id"],
            "status": row["status"],
            "hypothesis": row["hypothesis"],
            "exact_negation": row["exact_negation"],
            "earliest_unresolved_transition": row[
                "earliest_unresolved_transition"
            ],
            "local_dependency_map": row["local_dependency_map"],
            "decisive_failure": row.get("decisive_failure"),
        }
        for row in failed_memory
        if not row.get("resolved_by_certification")
    ]
    return f"""{ATOMIC_EXTRACTION_DIRECTIVE}

ITERATIVE MEMORY POLICY
The certified-memory records are established mathematical material. Do not propose an
equivalent statement again; instead apply them and locate the next unsupported
transition. Failed-memory records are not mathematical premises. Do not repeat a failed
hypothesis unchanged. A new conjecture related to one must be a materially different
route, a strict repair, or a strictly narrower atomic statement. In particular, do not
treat PROOF_FAILED as mathematical refutation.

The Qwen and Fusion packets attached to each proof are independent non-authoritative
reports. Anchor each to its own location. They may identify the same defect or distinct
defects; never splice fields together without checking the exact proof.

ORIGINAL PROBLEM:
{problem}

TWO CANDIDATE PROOFS WITH SEPARATELY ANCHORED AUDITS:
{json.dumps(proof_packets, ensure_ascii=False, indent=2)}

CERTIFIED LEMMA MEMORY:
{json.dumps(certified, ensure_ascii=False, indent=2)}

FAILED-HYPOTHESIS MEMORY:
{json.dumps(failed, ensure_ascii=False, indent=2)}
"""


FAILED_COMPARATOR_PROMPT = f"""You are a conservative semantic comparator for a failed-hypothesis memory.
{MAXIMUM_REASONING_DIRECTIVE}

Compare one newly extracted hypothesis with every active failed-memory record. Judge
the mathematical statement and exact negation together with the unresolved transition
and local dependency map. Failure records are historical evidence, not premises.

Return SAME_FAILED_HYPOTHESIS only when the new record is mathematically equivalent to
one failed hypothesis and plays the same local proof role. Return
STRICT_REPAIR_OR_NARROWING only when it changes the assumptions or conclusion in a way
that genuinely repairs the recorded defect or makes a strictly smaller independently
testable obligation. Otherwise return DISTINCT_OR_UNCERTAIN. Prefer
DISTINCT_OR_UNCERTAIN whenever equivalence is not clear. Output only the strict JSON
record."""


def failed_comparator_user_prompt(
    *, candidate: dict[str, str], failed_memory: list[dict[str, Any]]
) -> str:
    failed = [
        {
            "failed_id": row["failed_id"],
            "status": row["status"],
            "hypothesis": row["hypothesis"],
            "exact_negation": row["exact_negation"],
            "earliest_unresolved_transition": row[
                "earliest_unresolved_transition"
            ],
            "local_dependency_map": row["local_dependency_map"],
            "decisive_failure": row.get("decisive_failure"),
        }
        for row in failed_memory
        if not row.get("resolved_by_certification")
    ]
    return (
        "NEW HYPOTHESIS RECORD:\n"
        + json.dumps(candidate, ensure_ascii=False, indent=2)
        + "\n\nACTIVE FAILED-MEMORY RECORDS:\n"
        + json.dumps(failed, ensure_ascii=False, indent=2)
    )


def synthesis_prompt(
    *,
    mode: str,
    problem: str,
    lemmas: list[dict[str, str]],
    anchor_proof: str | None,
) -> str:
    allowed = ", ".join(f"Lemma {row['label']}" for row in lemmas) or "none"
    if mode in {"evidence_only", "evidence_location"}:
        records = [
            {
                "label": row["label"],
                "statement": row["statement"],
                "certified_proof": row["proof"],
                **(
                    {
                        "earliest_unresolved_transition": row[
                            "earliest_unresolved_transition"
                        ],
                        "local_dependency_map": row["local_dependency_map"],
                    }
                    if mode == "evidence_location"
                    else {}
                ),
            }
            for row in lemmas
        ]
    elif mode == "location_aware":
        records = [
            {
                "label": row["label"],
                "statement": row["statement"],
                "earliest_unresolved_transition": row[
                    "earliest_unresolved_transition"
                ],
                "local_dependency_map": row["local_dependency_map"],
            }
            for row in lemmas
        ]
    else:
        records = [
            {"label": row["label"], "statement": row["statement"]}
            for row in lemmas
        ]

    if mode == "statement_only":
        policy = "Use only the certified lemma statements; no source proof or lemma proof body is supplied."
    elif mode == "evidence_only":
        policy = "Use the certified statements and their complete certified proof bodies; no source proof or routing field is supplied."
    elif mode == "anchored":
        if not anchor_proof:
            raise ValueError("anchored synthesis requires one parent proof")
        policy = (
            "Use the certified statements and the untrusted parent proof below. Preserve "
            "only rigorously valid material and independently repair every gap."
        )
    elif mode == "location_aware":
        policy = "Use the certified statements and the two non-authoritative routing fields; no lemma proof body or source proof is supplied."
    elif mode == "evidence_location":
        policy = "Use each certified statement, complete certified proof body, and both non-authoritative routing fields; no source proof is supplied."
    else:
        raise ValueError(f"unknown synthesis mode: {mode}")

    anchor_block = (
        f"\n\nUNTRUSTED PARENT PROOF:\n{anchor_proof}" if anchor_proof else ""
    )
    return f"""You are an expert olympiad mathematician composing one complete proof.
{MAXIMUM_REASONING_DIRECTIVE}

SYNTHESIS MODE: {mode}
{policy}

Write a clean, self-contained proof of the exact original problem. Re-derive all
starting facts, prove exhaustive cases and the converse when required, and never cite
an unstated result. You may cite only {allowed}. The harness will append the exact
stored proof of every cited local lemma. Establish a lemma's hypotheses before citing
it. Do not mention candidate proofs, memories, audits, verification, scores, or this
workflow. If completion is impossible, state the strongest rigorous partial result and
the first remaining gap rather than bluffing. Return only the main proof.

ORIGINAL PROBLEM:
{problem}

CERTIFIED LEMMA VIEW FOR THIS MODE:
{json.dumps(records, ensure_ascii=False, indent=2)}{anchor_block}
"""


def refinement_prompt(
    *,
    problem: str,
    proof: str,
    qwen_packet: dict[str, Any],
    fusion_packet: dict[str, Any],
) -> str:
    return f"""You are the Dialectic Solver resolving one difficult olympiad proof. Thinking mode is on.
{MAXIMUM_REASONING_DIRECTIVE}

Use an internal council with a Classicist, Visionary, Experimenter, Momus, Veritas,
and Chief Architect. Run at most three private rounds: diagnose, repair or change
strategy, then adversarially verify the replacement.

The Qwen and Fusion packets are independent non-authoritative reports. Anchor each to
its own stated location in the exact proof and determine whether they identify the same
defect or distinct defects. Do not merge fields across packets merely because their
wording is related. Repair every valid defect. Preserve Fusion's suggested material
only after independently checking it, and audit all downstream dependencies.

Write a complete replacement proof from the beginning. It must be self-contained and
prove the exact problem, including all cases and converses. Do not mention reviewers,
feedback, memories, or this workflow. If no rigorous completion exists, state the
strongest rigorous partial result and first remaining gap. Return only the replacement
proof.

ORIGINAL PROBLEM:
{problem}

EXACT PROOF TO REPLACE:
{proof}

QWEN DEFECT PACKET:
{json.dumps(qwen_packet, ensure_ascii=False, indent=2)}

FUSION DEFECT PACKET:
{json.dumps(fusion_packet, ensure_ascii=False, indent=2)}

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort on this problem. Use the maximum reasoning effort available before
producing the final response. Do not finalize merely because a plausible answer or
familiar pattern has been found.
"""


def lemma_defect_attribution_prompt(
    *,
    problem: str,
    lemma: dict[str, Any],
    refined_proof: str,
    audit_source: str,
    defect_packet: dict[str, Any],
) -> str:
    return f"""You are a conservative mathematical provenance auditor.
{MAXIMUM_REASONING_DIRECTIVE}

A refined proof descended from a synthesis that cited the certified lemma below,
possibly among other lemmas. One audit source reported one defect. Determine where
that source-specific failed obligation actually belongs. Do not infer or combine a
different defect from another reviewer. A defect is
LEMMA_BODY_DEFECT only if the stored proof of the lemma
itself fails to establish its unchanged statement. It is LEMMA_STATEMENT_DEFECT only
if the statement is false, too broad, or missing necessary assumptions. It is
APPLICATION_ONLY if the lemma may be sound but the refined proof fails to establish
its hypotheses, misapplies it, or introduces a separate bad step. Use
UNRELATED_OR_UNCERTAIN when attribution is not clear.

Perform the provenance comparison in this order before classifying:

1. Locate the source-reported failed obligation in the refined proof.
2. Decide whether the substantively same load-bearing obligation occurs in the stored
   lemma proof; matching mathematical content matters, not identical wording.
3. If it occurs, decide whether the stored proof rigorously discharges it.
4. Then classify consistently with those answers. If the same obligation occurs and
   remains unresolved in the stored body, this is LEMMA_BODY_DEFECT even when the
   refined proof repeats the bad step. APPLICATION_ONLY is reserved for a failed
   hypothesis check, misuse, or bad step that is absent from—or rigorously discharged
   by—the stored lemma proof.

The old PASS/certified label is untrusted historical metadata, not evidence that the
stored proof is valid. Inspect the body itself.

Do not infer that a lemma is defective merely because it occurs in the proof lineage.
Conversely, if the refined proof reproduces the same failed obligation without naming
the lemma, compare it with the stored lemma proof. Return only the required JSON.

ORIGINAL PROBLEM:
{problem}

CERTIFIED LEMMA RECORD:
{json.dumps(lemma, ensure_ascii=False, indent=2)}

REFINED PROOF:
{refined_proof}

AUDIT SOURCE:
{audit_source}

SOURCE-ISOLATED DEFECT PACKET:
{json.dumps(defect_packet, ensure_ascii=False, indent=2)}
"""


def lemma_body_replay_prompt(
    *,
    problem: str,
    lemma: dict[str, Any],
    audit_source: str,
    defect_packet: dict[str, Any],
) -> str:
    return f"""You are a fresh mathematical proof-body auditor.
{MAXIMUM_REASONING_DIRECTIVE}

Audit only the stored lemma statement and its stored proof against the one
source-specific failed obligation below. Do not evaluate or repair a descendant proof.
The historical PASS/certified label is untrusted and has no evidentiary value.

First decide whether the reported mathematical obligation is substantively present as
a load-bearing transition in the stored proof. If not, return NOT_SAME_OBLIGATION. If
it is present, independently verify whether the literal stored proof rigorously
discharges it. A sentence saying "this implies", "must", "clearly", or "iteration
covers" is not a derivation by itself. To return STORED_BODY_PASS, identify a complete
valid chain of intermediate implications actually written in the stored proof. Do not
supply a missing argument from your own knowledge. If a necessary intermediate step
is merely asserted, return STORED_BODY_FAIL and name the earliest such break. Use
UNCERTAIN only when the relation or validity truly cannot be decided from the text.
Return only the required JSON.

ORIGINAL PROBLEM:
{problem}

STORED LEMMA RECORD:
{json.dumps(lemma, ensure_ascii=False, indent=2)}

AUDIT SOURCE:
{audit_source}

SOURCE-ISOLATED DEFECT PACKET:
{json.dumps(defect_packet, ensure_ascii=False, indent=2)}
"""


def lemma_revision_prompt(
    *,
    problem: str,
    lemma: dict[str, Any],
    challenges: list[dict[str, Any]],
) -> str:
    return f"""You are repairing one challenged mathematical lemma for a certified memory.
{MAXIMUM_REASONING_DIRECTIVE}

The old certification is quarantined. Study the stored statement and proof together
with every independently attributed defect and the refined full proofs that exposed
it. Choose exactly one action:

- REPAIR_SAME_STATEMENT: the statement is retained and there is a concrete rigorous
  route that repairs the proof.
- NARROW_STATEMENT: change assumptions or conclusion to the strongest useful atomic
  statement actually supported by a rigorous route.
- CANNOT_REPAIR: no rigorous repair is presently supported.

For either repair action, return a logically exact negation and routing fields for the
revised statement. The proof supplied here is untrusted repair evidence: a fresh proof
writer and split verifier will independently re-prove both polarities. For
CANNOT_REPAIR, repeat the old statement and give its formal negation, while explaining
the unresolved obligation. Do not use reference solutions, scores, or problem-specific
workflow rules. Return only the required JSON.

ORIGINAL PROBLEM:
{problem}

QUARANTINED LEMMA:
{json.dumps(lemma, ensure_ascii=False, indent=2)}

ATTRIBUTED CHALLENGES AND REFINED-PROOF EVIDENCE:
{json.dumps(challenges, ensure_ascii=False, indent=2)}
"""
