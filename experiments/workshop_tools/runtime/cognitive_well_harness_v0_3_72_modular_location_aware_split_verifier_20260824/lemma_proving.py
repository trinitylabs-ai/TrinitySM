from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json

from .contracts import NEGATION_AUDIT_SCHEMA, NEGATION_REPAIR_SCHEMA
from .prompts import (
    lemma_repair_prompt,
    lemma_solver_prompt,
    negation_audit_prompt,
    negation_repair_prompt,
)
from .runtime import ResilientModelRuntime
from .split_verifier import split_certify


def validate_and_repair_negations(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    hypotheses: dict[str, Any],
    arm: str,
    round_number: int,
    output_dir: Path,
) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for index, hypothesis in enumerate(hypotheses["hypotheses"], start=1):
        claim_id = f"R{round_number}H{index}_{arm}"
        destination = output_dir / claim_id
        claim = str(hypothesis["conjecture"])
        negation = str(hypothesis["exact_negation"])
        audit, _ = runtime.structured(
            role="qwen",
            prompt=negation_audit_prompt(
                problem=problem,
                claim=claim,
                proposed_negation=negation,
            ),
            destination=destination,
            stage="negation_audit_0",
            schema=NEGATION_AUDIT_SCHEMA,
            temperature=0.2,
            max_tokens=8_192,
            seed_label=f"v072:{claim_id}:negation:audit:0",
        )
        if not audit["valid_exact_negation"]:
            repair, _ = runtime.structured(
                role="gemma",
                prompt=negation_repair_prompt(
                    problem=problem,
                    claim=claim,
                    negation=negation,
                    first_issue=audit["first_issue"],
                ),
                destination=destination,
                stage="negation_repair",
                schema=NEGATION_REPAIR_SCHEMA,
                temperature=0.1,
                max_tokens=8_192,
                seed_label=f"v072:{claim_id}:negation:repair",
            )
            negation = str(repair["exact_negation"])
            audit, _ = runtime.structured(
                role="qwen",
                prompt=negation_audit_prompt(
                    problem=problem,
                    claim=claim,
                    proposed_negation=negation,
                ),
                destination=destination,
                stage="negation_audit_1",
                schema=NEGATION_AUDIT_SCHEMA,
                temperature=0.2,
                max_tokens=8_192,
                seed_label=f"v072:{claim_id}:negation:audit:1",
            )
        if not audit["valid_exact_negation"]:
            raise RuntimeError(f"exact negation was not certified for {claim_id}")
        pair = {
            "claim_id": claim_id,
            "positive": claim,
            "negative": negation,
            "earliest_unresolved_transition": str(
                hypothesis["earliest_unresolved_transition"]
            ),
            "local_dependency_map": str(hypothesis["local_dependency_map"]),
        }
        write_json(destination / "result.json", {**pair, "audit": audit})
        pairs.append(pair)
    return pairs


def prove_side(
    *,
    runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    pair: dict[str, str],
    side: str,
    output_dir: Path,
) -> dict[str, Any]:
    claim = pair[side]
    destination = output_dir / pair["claim_id"] / side
    generated = runtime.text(
        role="gemma",
        prompt=lemma_solver_prompt(problem=problem, claim=claim),
        destination=destination,
        stage="proof_0",
        temperature=0.6,
        max_tokens=32_768,
        seed_label=f"v072:{pair['claim_id']}:{side}:proof:0",
    )
    proof = str(generated["text"]).strip()
    audit = split_certify(
        runtime=verifier_runtime,
        problem=problem,
        assigned_claim=claim,
        proof=proof,
        output_dir=destination / "audit_0",
        seed_label=f"{pair['claim_id']}:{side}:audit:0",
    )
    repair_invoked = not audit["certified"]
    final_generation = generated
    if repair_invoked:
        repaired = runtime.text(
            role="gemma",
            prompt=lemma_repair_prompt(
                problem=problem,
                claim=claim,
                proof=proof,
                audit=audit,
            ),
            destination=destination,
            stage="proof_1_repair",
            temperature=0.2,
            max_tokens=32_768,
            seed_label=f"v072:{pair['claim_id']}:{side}:proof:1",
        )
        proof = str(repaired["text"]).strip()
        final_generation = repaired
        audit = split_certify(
            runtime=verifier_runtime,
            problem=problem,
            assigned_claim=claim,
            proof=proof,
            output_dir=destination / "audit_1",
            seed_label=f"{pair['claim_id']}:{side}:audit:1",
        )
    polarity = None
    if audit["certified"]:
        proves_assigned = audit["routed_target"] == "assigned_claim"
        polarity = side if proves_assigned else (
            "negative" if side == "positive" else "positive"
        )
    result = {
        "claim_id": pair["claim_id"],
        "side": side,
        "assigned_claim": claim,
        "certified_statement": audit.get("routed_claim"),
        "certified_polarity": polarity,
        "proof": proof,
        "certified": audit["certified"],
        "audit": audit,
        "repair_invoked": repair_invoked,
        "generation": final_generation["metadata"],
    }
    write_json(destination / "result.json", result)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "proof.md").write_text(proof + "\n", encoding="utf-8")
    return result


def prove_pairs(
    *,
    runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    pairs: list[dict[str, str]],
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    jobs = [(pair, side) for pair in pairs for side in ("positive", "negative")]
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                prove_side,
                runtime=runtime,
                verifier_runtime=verifier_runtime,
                problem=problem,
                pair=pair,
                side=side,
                output_dir=output_dir,
            )
            for pair, side in jobs
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    by_pair: dict[str, dict[str, dict[str, Any]]] = {}
    for row in results:
        by_pair.setdefault(row["claim_id"], {})[row["side"]] = row
    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for pair in pairs:
        sides = by_pair[pair["claim_id"]]
        certified = [
            sides[side]
            for side in ("positive", "negative")
            if sides[side]["certified"]
        ]
        polarities = {str(row["certified_polarity"]) for row in certified}
        if polarities == {"positive", "negative"}:
            unresolved.append(
                {
                    "claim_id": pair["claim_id"],
                    "status": "logical_conflict",
                    "positive_audit": sides["positive"]["audit"],
                    "negative_audit": sides["negative"]["audit"],
                }
            )
            continue
        if not certified:
            unresolved.append(
                {
                    "claim_id": pair["claim_id"],
                    "status": "unresolved",
                    "positive_audit": sides["positive"]["audit"],
                    "negative_audit": sides["negative"]["audit"],
                }
            )
            continue
        # Both attempts can independently establish the same polarity (for example,
        # one assigned route and one opposite-route salvage). A hypothesis contributes
        # at most one memory lemma; prefer a proof aligned to its assigned side.
        row = sorted(
            certified,
            key=lambda item: (
                item["audit"]["routed_target"] != "assigned_claim",
                item["side"] != "positive",
            ),
        )[0]
        verified.append(
            {
                "lemma_id": pair["claim_id"],
                "direction": row["certified_polarity"],
                "statement": str(row["certified_statement"]),
                "proof": row["proof"],
                "earliest_unresolved_transition": pair[
                    "earliest_unresolved_transition"
                ],
                "local_dependency_map": pair["local_dependency_map"],
                "audit": row["audit"],
            }
        )
    write_json(output_dir / "summary.json", {"verified": verified, "unresolved": unresolved})
    return verified, unresolved
