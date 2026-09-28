from __future__ import annotations

import concurrent.futures
import json
from pathlib import Path
from typing import Any

from .contracts import (
    CERTIFICATION_SCHEMA,
    DIAGNOSTIC_SCHEMA,
    NEGATION_AUDIT_SCHEMA,
    NEGATION_REPAIR_SCHEMA,
)
from .model_runtime import ModelRuntime, write_json
from .prompts import (
    certifier_prompt,
    diagnostic_prompt,
    lemma_repair_prompt,
    lemma_solver_prompt,
    negation_audit_prompt,
    negation_repair_prompt,
)


CERTIFICATION_MAX_ATTEMPTS = 3


def certification_is_consistent(record: dict[str, Any]) -> bool:
    if record["verdict"] == "PASS":
        return record["exact_claim_reached"] is True
    return record["exact_claim_reached"] is False


def compact_certify(
    *,
    runtime: ModelRuntime,
    problem: str,
    claim: str,
    proof: str,
    output_dir: Path,
    stage_prefix: str,
    seed_label: str,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    certification: dict[str, Any] | None = None
    certification_generation: dict[str, Any] | None = None
    for attempt in range(CERTIFICATION_MAX_ATTEMPTS):
        stage = f"{stage_prefix}_certification_{attempt}"
        try:
            candidate, generated = runtime.structured(
                role="qwen",
                prompt=certifier_prompt(problem=problem, claim=claim, proof=proof),
                destination=output_dir,
                stage=stage,
                schema=CERTIFICATION_SCHEMA,
                temperature=0.2,
                max_tokens=16_384,
                seed_label=f"{seed_label}:certification:{attempt}",
            )
            if not certification_is_consistent(candidate):
                raise ValueError(f"inconsistent certification: {candidate}")
            certification = candidate
            certification_generation = generated
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": stage,
                    "status": "accepted",
                    "finish_reason": generated["metadata"].get("finish_reason"),
                }
            )
            break
        except Exception as error:
            attempts.append(
                {
                    "attempt": attempt,
                    "stage": stage,
                    "status": "rejected",
                    "error": f"{type(error).__name__}: {error}",
                }
            )

    fallback = certification is None
    if certification is None:
        certification = {"verdict": "INCONCLUSIVE", "exact_claim_reached": False}

    diagnostic: dict[str, Any] | None = None
    diagnostic_generation: dict[str, Any] | None = None
    diagnostic_error: str | None = None
    if certification["verdict"] != "PASS" and not fallback:
        try:
            diagnostic, diagnostic_generation = runtime.structured(
                role="qwen",
                prompt=diagnostic_prompt(
                    problem=problem,
                    claim=claim,
                    proof=proof,
                    verdict=str(certification["verdict"]),
                ),
                destination=output_dir,
                stage=f"{stage_prefix}_diagnostic",
                schema=DIAGNOSTIC_SCHEMA,
                temperature=0.2,
                max_tokens=16_384,
                seed_label=f"{seed_label}:diagnostic",
            )
        except Exception as error:
            diagnostic_error = f"{type(error).__name__}: {error}"

    result = {
        **certification,
        "certified": certification["verdict"] == "PASS",
        "certification_source": "fallback" if fallback else "model",
        "certification_attempts": attempts,
        "certification_generation": (
            certification_generation["metadata"]
            if certification_generation is not None
            else None
        ),
        "diagnostic": diagnostic,
        "diagnostic_generation": (
            diagnostic_generation["metadata"]
            if diagnostic_generation is not None
            else None
        ),
        "diagnostic_error": diagnostic_error,
    }
    write_json(output_dir / f"{stage_prefix}_result.json", result)
    return result


def validate_and_repair_negations(
    *,
    runtime: ModelRuntime,
    problem: str,
    hypotheses: dict[str, Any],
    arm: str,
    round_number: int,
    output_dir: Path,
) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for index, (claim, negation) in enumerate(
        zip(hypotheses["conjectures"], hypotheses["negations"]),
        start=1,
    ):
        claim_id = f"R{round_number}H{index}_{arm}"
        destination = output_dir / claim_id
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
            seed_label=f"{claim_id}:negation:audit:0",
        )
        final_negation = negation
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
                seed_label=f"{claim_id}:negation:repair",
            )
            final_negation = str(repair["exact_negation"])
            audit, _ = runtime.structured(
                role="qwen",
                prompt=negation_audit_prompt(
                    problem=problem,
                    claim=claim,
                    proposed_negation=final_negation,
                ),
                destination=destination,
                stage="negation_audit_1",
                schema=NEGATION_AUDIT_SCHEMA,
                temperature=0.2,
                max_tokens=8_192,
                seed_label=f"{claim_id}:negation:audit:1",
            )
        if not audit["valid_exact_negation"]:
            raise RuntimeError(f"exact negation was not certified for {claim_id}")
        pair = {
            "claim_id": claim_id,
            "positive": str(claim),
            "negative": str(final_negation),
        }
        write_json(destination / "result.json", {**pair, "audit": audit})
        pairs.append(pair)
    return pairs


def prove_side(
    *,
    runtime: ModelRuntime,
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
        seed_label=f"{pair['claim_id']}:{side}:proof:0",
    )
    proof = str(generated["text"]).strip()
    audit = compact_certify(
        runtime=runtime,
        problem=problem,
        claim=claim,
        proof=proof,
        output_dir=destination,
        stage_prefix="audit_0",
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
            seed_label=f"{pair['claim_id']}:{side}:proof:1",
        )
        proof = str(repaired["text"]).strip()
        final_generation = repaired
        audit = compact_certify(
            runtime=runtime,
            problem=problem,
            claim=claim,
            proof=proof,
            output_dir=destination,
            stage_prefix="audit_1",
            seed_label=f"{pair['claim_id']}:{side}:audit:1",
        )
    result = {
        "claim_id": pair["claim_id"],
        "side": side,
        "claim": claim,
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
    runtime: ModelRuntime,
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
        certified_sides = [
            side for side in ("positive", "negative") if sides[side]["certified"]
        ]
        if len(certified_sides) == 1:
            side = certified_sides[0]
            verified.append(
                {
                    "lemma_id": pair["claim_id"],
                    "direction": side,
                    "statement": pair[side],
                    "proof": sides[side]["proof"],
                    "audit": sides[side]["audit"],
                }
            )
        else:
            unresolved.append(
                {
                    "claim_id": pair["claim_id"],
                    "status": "conflict" if len(certified_sides) == 2 else "unresolved",
                    "positive_audit": sides["positive"]["audit"],
                    "negative_audit": sides["negative"]["audit"],
                }
            )
    write_json(
        output_dir / "summary.json",
        {"verified": verified, "unresolved": unresolved},
    )
    return verified, unresolved
