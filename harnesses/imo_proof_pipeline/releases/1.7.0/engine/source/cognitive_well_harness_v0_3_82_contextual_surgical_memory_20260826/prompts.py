from __future__ import annotations

import json
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.prompts import (
    ATOMIC_EXTRACTION_DIRECTIVE,
    MAXIMUM_REASONING_DIRECTIVE,
)

from .contracts import CONTEXT_CERTIFIED, PROVISIONAL


def _memory_view(rows: list[dict[str, Any]], *, include_proof: bool, include_location: bool) -> list[dict[str, Any]]:
    view: list[dict[str, Any]] = []
    for row in rows:
        record: dict[str, Any] = {
            "label": row.get("label"),
            "memory_tier": row["memory_tier"],
            "statement": row["statement"],
        }
        if include_proof:
            record["stored_proof_body"] = row["proof"]
        if include_location:
            record["earliest_unresolved_transition"] = row[
                "earliest_unresolved_transition"
            ]
            record["local_dependency_map"] = row["local_dependency_map"]
        view.append(record)
    return view


def iterative_extraction_prompt(
    *,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    context_certified_memory: list[dict[str, Any]],
    provisional_memory: list[dict[str, Any]],
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
            "memory_tier": CONTEXT_CERTIFIED,
            "statement": row["statement"],
            "earliest_unresolved_transition": row[
                "earliest_unresolved_transition"
            ],
            "local_dependency_map": row["local_dependency_map"],
        }
        for row in context_certified_memory
    ]
    provisional = [
        {
            "memory_tier": PROVISIONAL,
            "statement": row["statement"],
            "earliest_unresolved_transition": row[
                "earliest_unresolved_transition"
            ],
            "local_dependency_map": row["local_dependency_map"],
        }
        for row in provisional_memory
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

ITERATIVE TWO-TIER MEMORY POLICY
Context-certified records survived contextual use and whole-proof auditing. They are
established reusable material. Provisional records passed preliminary paired proving
and a split verifier only. They are untrusted leads, not premises. Do not propose an
equivalent statement from either tier again; instead use the record to locate the next
unsupported transition. Failed-memory records are historical evidence, never premises.

The Qwen and Fusion records attached to a proof retain separate provenance. Fusion is
downstream of the three reviewers and is not an independent vote. Anchor each report
to its own literal proof location before using it.

ORIGINAL PROBLEM:
{problem}

TWO PROOF SEEDS WITH AUDITS:
{json.dumps(proof_packets, ensure_ascii=False, indent=2)}

CONTEXT-CERTIFIED MEMORY:
{json.dumps(certified, ensure_ascii=False, indent=2)}

PROVISIONAL MEMORY:
{json.dumps(provisional, ensure_ascii=False, indent=2)}

FAILED/QUARANTINED MEMORY:
{json.dumps(failed, ensure_ascii=False, indent=2)}
"""


def synthesis_prompt(
    *, mode: str, problem: str, lemmas: list[dict[str, Any]], anchor_proof: str | None
) -> str:
    include_proof = mode in {"evidence_only", "evidence_location"}
    include_location = mode in {"location_aware", "evidence_location"}
    records = _memory_view(
        lemmas, include_proof=include_proof, include_location=include_location
    )
    if mode == "statement_only":
        policy = "Only tier-labeled statements are supplied; no bodies, routing fields, or parent proof."
    elif mode == "evidence_only":
        policy = "Tier-labeled statements and complete stored bodies are supplied; no routing fields or parent proof."
    elif mode == "anchored":
        policy = "Tier-labeled statements and one untrusted parent proof are supplied; no stored lemma bodies."
    elif mode == "location_aware":
        policy = "Tier-labeled statements and non-authoritative routing fields are supplied; no bodies or parent proof."
    elif mode == "evidence_location":
        policy = "Tier-labeled statements, complete stored bodies, and routing fields are supplied; no parent proof."
    else:
        raise ValueError(f"unknown synthesis mode: {mode}")
    anchor_block = (
        f"\n\nUNTRUSTED PARENT PROOF:\n{anchor_proof}" if anchor_proof else ""
    )
    return f"""You are an expert Olympiad mathematician composing one complete proof.
{MAXIMUM_REASONING_DIRECTIVE}

SYNTHESIS MODE: {mode}
{policy}

Context-certified lemmas may be cited only after their hypotheses are established.
Provisional lemmas are untrusted evidence: do not cite their preliminary certification
as authority and independently establish every load-bearing use. The harness records
exact proof-to-lemma dependencies and may append stored bodies, but an appended body
does not make an invalid inference valid.

Write a clean, self-contained proof of the exact problem, including exhaustive cases
and the converse. Do not mention memories, audits, scores, or this workflow. If a
completion is unavailable, state the strongest rigorous partial result and first gap.
Return only the proof.

ORIGINAL PROBLEM:
{problem}

TIER-LABELED LEMMA VIEW:
{json.dumps(records, ensure_ascii=False, indent=2)}{anchor_block}
"""


def qwen_repair_spec_prompt(
    *,
    problem: str,
    proof: str,
    implicated_lemmas: list[dict[str, Any]],
    qwen_packet: dict[str, Any],
    fusion_packet: dict[str, Any],
    body_replay_records: list[dict[str, Any]],
) -> str:
    return f"""You are producing a surgical repair specification for one complete
Olympiad proof. {MAXIMUM_REASONING_DIRECTIVE}

Do not write the replacement proof. Verify the raw Reviewer-2 Qwen record and the
downstream Fusion adjudication against the literal proof. They are separate provenance
blocks, not independent votes. Identify the smallest logically closed region that must
change, including implicated lemma bodies or interfaces, their application, and all
downstream dependencies. Treat every implicated lemma as untrusted. Preserve material
only after checking it. If no rigorous route is supported, choose NO_SUPPORTED_REPAIR.
Return only the required JSON. Do not use external solutions, scores, or
problem-specific workflow rules.

ORIGINAL PROBLEM:
{problem}

TAINTED COMPLETE PROOF:
{proof}

IMPLICATED LEMMA RECORDS:
{json.dumps(implicated_lemmas, ensure_ascii=False, indent=2)}

RAW REVIEWER-2 QWEN RECORD:
{json.dumps(qwen_packet, ensure_ascii=False, indent=2)}

DOWNSTREAM FUSION ADJUDICATION:
{json.dumps(fusion_packet, ensure_ascii=False, indent=2)}

STORED-BODY REPLAY RECORDS:
{json.dumps(body_replay_records, ensure_ascii=False, indent=2)}
"""


def contextual_rewrite_prompt(
    *,
    problem: str,
    proof: str,
    implicated_lemmas: list[dict[str, Any]],
    repair_spec: dict[str, Any],
    qwen_packet: dict[str, Any],
    fusion_packet: dict[str, Any],
    prior_attempt_feedback: dict[str, Any] | None,
) -> str:
    feedback = (
        "\n\nPRIOR CONTEXTUAL-REPAIR AUDIT FEEDBACK:\n"
        + json.dumps(prior_attempt_feedback, ensure_ascii=False, indent=2)
        if prior_attempt_feedback
        else ""
    )
    return f"""You are an expert Olympiad mathematician surgically repairing one
complete proof. {MAXIMUM_REASONING_DIRECTIVE}

Treat the proof as one mathematical object. The implicated lemmas are untrusted.
Repair the complete affected region in context: preceding hypotheses, lemma body or
replacement route, application, and downstream conclusions. You may repair the same
statement, revise its interface and its use, inline it, or eliminate it. Verify both
feedback blocks independently before using them.

Return one complete replacement proof from the beginning, not a patch. It must be
self-contained and must not mention reviewers, memories, repair, or this workflow. If
completion is impossible, state the strongest rigorous partial result and first gap.
Return only the replacement proof.

ORIGINAL PROBLEM:
{problem}

COMPLETE PROOF TO REPLACE:
{proof}

IMPLICATED LEMMA RECORDS:
{json.dumps(implicated_lemmas, ensure_ascii=False, indent=2)}

QWEN SURGICAL SPECIFICATION:
{json.dumps(repair_spec, ensure_ascii=False, indent=2)}

RAW REVIEWER-2 QWEN RECORD:
{json.dumps(qwen_packet, ensure_ascii=False, indent=2)}

DOWNSTREAM FUSION ADJUDICATION:
{json.dumps(fusion_packet, ensure_ascii=False, indent=2)}{feedback}

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Do not finalize merely because a plausible or familiar argument has
been found.
"""


def audit_anchor_extraction_prompt(*, problem: str, proof: str) -> str:
    return f"""You are a proof-structure extractor, not a proof judge.
{MAXIMUM_REASONING_DIRECTIVE}

Read the complete proof and extract up to 24 load-bearing passages in proof order.
For each, copy an exact quote and record the mathematical claim, introduced objects
and their declared domains, required prior facts, invoked operation or result, and the
downstream conclusion depending on it. Do not decide whether a passage is valid, do
not repair it, and do not invent proof-specific checks from external knowledge. Return
only the required JSON.

ORIGINAL PROBLEM:
{problem}

COMPLETE PROOF:
{proof}
"""


def literal_anchor_audit_prompt(
    *, problem: str, proof: str, anchors: list[dict[str, Any]]
) -> str:
    return f"""You are a fresh literal-entailment auditor.
{MAXIMUM_REASONING_DIRECTIVE}

Verify each extracted claim exactly as written from its declared objects and listed
prerequisites. Do not silently add intended restrictions, missing hypotheses,
intermediate arguments, or charitable reinterpretations. The anchors are priorities,
not permission to ignore the rest of the complete proof. Return LITERAL_FAILURE at
the earliest literal break, otherwise PASS. For PASS, leave the failed-anchor and
failure-location fields empty and explain why no literal break survives. Return only
the required JSON.

ORIGINAL PROBLEM:
{problem}

COMPLETE PROOF:
{proof}

DYNAMIC PROOF-SPECIFIC AUDIT ANCHORS:
{json.dumps(anchors, ensure_ascii=False, indent=2)}
"""


def memory_disposition_prompt(
    *, proof: str, quarantined_lemmas: list[dict[str, Any]]
) -> str:
    return f"""You are extracting, not generating, a reusable lemma revision from an
already accepted complete proof. Do not repair, paraphrase, strengthen, or complete
anything.

Return EXACT_SELF_CONTAINED_REVISION only if the accepted proof literally contains a
self-contained local lemma statement and a complete proof passage that can be copied
exactly and that genuinely replaces the mathematical role of at least one quarantined
record. Copy both fields verbatim from the proof. The whole target theorem is not a
replacement merely because it implies the old lemma. Otherwise return
NO_REUSABLE_LEMMA with empty quote fields. Routing fields may describe where the exact
excerpt was used but cannot add mathematical content. Return only the required JSON.

QUARANTINED LEMMA RECORDS:
{json.dumps(quarantined_lemmas, ensure_ascii=False, indent=2)}

ACCEPTED COMPLETE PROOF:
{proof}
"""
