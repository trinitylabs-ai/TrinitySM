from __future__ import annotations

import concurrent.futures
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824 import (
    run_failure_guided_salvage_surgical as v063_salvage,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.lemma_proving import (
    prove_pairs,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.runtime import (
    ResilientModelRuntime,
)
from experiments.local_math_verifier.runtime import HTTPGenerationConfig

from .contracts import FAILURE_SALVAGE_SCHEMA, MAX_FAILURE_SALVAGE_CASES
from .prompts import FAILURE_SALVAGE_SYSTEM_PROMPT, failure_salvage_user_prompt


FAILURE_STATUS_ORDER = ("REFUTED", "PROOF_FAILED", "VERIFIER_CONFLICT")
EXPERIMENT_MASTER_SEED = 20260825


def _experimental_signal(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize a v0.3.72 result to the exact v0.3.63 failure-card shape."""
    audit = result.get("audit") or {}
    return {
        "side": result.get("side"),
        "claim": result.get("claim") or result.get("assigned_claim"),
        "certified": bool(result.get("certified")),
        "earliest_break": audit.get("earliest_break"),
        "missing_obligations": audit.get("missing_obligations") or [],
        "summary": audit.get("summary"),
        "proof": result.get("proof") if result.get("certified") else None,
    }


def failure_card_for_pair(
    *,
    pair: dict[str, str],
    positive: dict[str, Any],
    negative: dict[str, Any],
    source_arm: str,
    round_number: int,
) -> dict[str, Any] | None:
    certified = [row for row in (positive, negative) if row.get("certified")]
    polarities = {str(row.get("certified_polarity")) for row in certified}
    if polarities == {"positive"}:
        return None
    if polarities == {"negative"}:
        status = "REFUTED"
    elif polarities == {"positive", "negative"}:
        status = "VERIFIER_CONFLICT"
    elif not polarities:
        status = "PROOF_FAILED"
    else:
        raise ValueError(
            f"unsupported certified polarity set for {pair['claim_id']}: {polarities}"
        )
    # `failure_card` is deliberately byte-structure compatible with the surgical
    # experiment. Pipeline provenance stays outside it and is therefore absent from
    # the model prompt.
    failure_card = {
        "status": status,
        "failed_hypothesis": pair["positive"],
        "exact_negation": pair["negative"],
        "positive_signal": _experimental_signal(positive),
        "negative_signal": _experimental_signal(negative),
    }
    return {
        "status": status,
        "case_name": status.lower(),
        "source_claim_id": pair["claim_id"],
        "source_arm": source_arm,
        "source_round": round_number,
        "failure_card": failure_card,
    }


def select_failure_cards(
    cards: list[dict[str, Any]], limit: int = MAX_FAILURE_SALVAGE_CASES
) -> list[dict[str, Any]]:
    """Select every eligible card up to the cap, with collision-free case names."""
    if limit < 0:
        raise ValueError("failure salvage limit must be nonnegative")
    selected: list[dict[str, Any]] = []
    for status in FAILURE_STATUS_ORDER:
        status_cards = [row for row in cards if row["status"] == status]
        for status_index, card in enumerate(status_cards, start=1):
            selected_card = dict(card)
            base_case_name = status.lower()
            if status_index == 1:
                # Preserve the exact v0.3.63 path and seeds for the first route case.
                case_name = base_case_name
            else:
                source = str(
                    card.get("source_claim_id") or card.get("id") or status_index
                )
                source_slug = re.sub(r"[^a-z0-9]+", "_", source.lower()).strip("_")
                case_name = f"{base_case_name}_{source_slug}"
            selected_card["case_name"] = case_name
            selected.append(selected_card)
            if len(selected) == limit:
                return selected
    return selected


def _run_exact_v063_salvage_generation(
    *,
    runtime: ResilientModelRuntime,
    case_name: str,
    user_prompt: str,
    destination: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Exact generation and recovery boundary from the successful experiment."""
    if runtime.config.gemma_model != v063_salvage.base.GEMMA_MODEL:
        raise ValueError(
            "exact salvage replica requires "
            f"{v063_salvage.base.GEMMA_MODEL}, got {runtime.config.gemma_model}"
        )
    destination.mkdir(parents=True, exist_ok=True)
    stage = "failure_guided_salvage"
    generated = v063_salvage.saved_generation(destination, stage)
    if generated is None:
        generated = v063_salvage.run_openai_chat_generation(
            endpoint=runtime.config.gemma_endpoint,
            model=v063_salvage.base.GEMMA_MODEL,
            prompt=FAILURE_SALVAGE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_dir=destination,
            stage=stage,
            config=HTTPGenerationConfig(
                max_tokens=32_768,
                temperature=0.4,
                top_p=0.95,
                top_k=64,
                seed=v063_salvage.base.stable_seed(
                    f"v063:failure_guided_salvage:{case_name}"
                ),
                thinking_token_budget=None,
                reasoning_effort="max",
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"failure_guided_salvage_{case_name}",
                        "strict": True,
                        "schema": FAILURE_SALVAGE_SCHEMA,
                    },
                },
                repetition_detection=v063_salvage.base.REPETITION_DETECTION,
                timeout_seconds=14_400,
            ),
        )

    attempts: list[dict[str, Any]] = []
    partial = str(generated["text"])
    try:
        record = v063_salvage.parse_salvage_record(partial)
        attempts.append(
            {
                "phase": "original",
                "status": "accepted",
                "finish_reason": generated["metadata"].get("finish_reason"),
            }
        )
    except Exception as original_error:
        attempts.append(
            {
                "phase": "original",
                "status": "rejected",
                "finish_reason": generated["metadata"].get("finish_reason"),
                "error": f"{type(original_error).__name__}: {original_error}",
            }
        )
        prior_error = attempts[-1]["error"]
        record = None
        for phase in ("compact", "repair_1"):
            recovery_stage = f"{stage}_{phase}"
            if phase == "compact":
                recovery_user_prompt = (
                    user_prompt.rstrip()
                    + "\n\n"
                    + v063_salvage.COMPACT_INSTRUCTION
                )
            else:
                recovery_user_prompt = (
                    user_prompt.rstrip()
                    + "\n\nTRANSPORT RECOVERY: Regenerate the entire record from scratch. "
                    + "Do not append to the prior response or reproduce a repeated suffix. "
                    + "Preserve correct mathematical content only. Prior error: "
                    + prior_error
                    + "\n\nPRIOR INCOMPLETE RESPONSE:\n"
                    + partial.rstrip()[-12_000:]
                    + "\n\n"
                    + v063_salvage.COMPACT_INSTRUCTION
                )
            recovered = v063_salvage.saved_generation(destination, recovery_stage)
            if recovered is None:
                recovered = v063_salvage.run_openai_chat_generation(
                    endpoint=runtime.config.gemma_endpoint,
                    model=v063_salvage.base.GEMMA_MODEL,
                    prompt=FAILURE_SALVAGE_SYSTEM_PROMPT,
                    user_prompt=recovery_user_prompt,
                    output_dir=destination,
                    stage=recovery_stage,
                    config=HTTPGenerationConfig(
                        max_tokens=16_384,
                        temperature=0.4,
                        top_p=0.95,
                        top_k=64,
                        seed=v063_salvage.base.stable_seed(
                            f"v063:failure_guided_salvage:{case_name}:{phase}"
                        ),
                        thinking_token_budget=None,
                        reasoning_effort="max",
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": (
                                    f"failure_guided_salvage_{case_name}_{phase}"
                                ),
                                "strict": True,
                                "schema": FAILURE_SALVAGE_SCHEMA,
                            },
                        },
                        repetition_detection=v063_salvage.base.REPETITION_DETECTION,
                        timeout_seconds=14_400,
                    ),
                )
            partial = str(recovered["text"])
            try:
                record = v063_salvage.parse_salvage_record(partial)
                attempts.append(
                    {
                        "phase": phase,
                        "status": "accepted",
                        "finish_reason": recovered["metadata"].get("finish_reason"),
                    }
                )
                generated = recovered
                break
            except Exception as recovery_error:
                prior_error = f"{type(recovery_error).__name__}: {recovery_error}"
                attempts.append(
                    {
                        "phase": phase,
                        "status": "rejected",
                        "finish_reason": recovered["metadata"].get("finish_reason"),
                        "error": prior_error,
                    }
                )
        if record is None:
            raise RuntimeError(f"structured salvage recovery exhausted: {attempts}")

    generation_metadata = dict(generated["metadata"])
    generation_metadata["salvage_recovery_attempts"] = attempts
    return record, {"text": str(generated["text"]), "metadata": generation_metadata}


def _salvage_one(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    selected_case: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    case_name = str(selected_case["case_name"])
    destination = output_dir / case_name
    failure_card = dict(selected_case["failure_card"])
    user_prompt = failure_salvage_user_prompt(
        problem=problem,
        candidate_proofs=candidate_proofs,
        failure_card=failure_card,
    )
    record, generation = _run_exact_v063_salvage_generation(
        runtime=runtime,
        case_name=case_name,
        user_prompt=user_prompt,
        destination=destination,
    )
    source = {
        key: selected_case[key]
        for key in ("source_claim_id", "source_arm", "source_round")
    }
    result = {
        "schema": "cognitive-well-failure-guided-salvage-surgical-v1",
        "case_name": case_name,
        "source": source,
        "failure_card": failure_card,
        "record": record,
        "generation": generation["metadata"],
    }
    write_json(destination / "result.json", result)
    return result


def run_failure_guided_salvage(
    *,
    runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    failure_cards: list[dict[str, Any]],
    output_dir: Path,
    limit: int = MAX_FAILURE_SALVAGE_CASES,
) -> dict[str, Any]:
    selected = select_failure_cards(failure_cards, limit=limit)
    if not selected:
        result = {
            "selected_failure_count": 0,
            "generated_hypothesis_count": 0,
            "verified": [],
            "unresolved": [],
            "cases": [],
            "provenance": {},
        }
        write_json(output_dir / "summary.json", result)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected)) as executor:
        cases = list(
            executor.map(
                lambda selected_case: _salvage_one(
                    runtime=runtime,
                    problem=problem,
                    candidate_proofs=candidate_proofs,
                    selected_case=selected_case,
                    output_dir=output_dir / "hypothesis_salvage",
                ),
                selected,
            )
        )

    pairs: list[dict[str, str]] = []
    provenance: dict[str, dict[str, Any]] = {}
    for case in cases:
        source = case["source"]
        status = str(case["failure_card"]["status"])
        for hypothesis_index, hypothesis in enumerate(
            case["record"]["hypotheses"], start=1
        ):
            # Preserve the exact experimental identifier for the first case on a
            # status route, while namespacing additional same-status cases so their
            # proof artifacts and deterministic seeds cannot collide.
            if case["case_name"] == status.lower():
                claim_prefix = status
            else:
                source_fragment = re.sub(
                    r"[^A-Za-z0-9_]+", "_", str(source["source_claim_id"])
                ).strip("_")
                claim_prefix = f"{status}_{source_fragment}"
            claim_id = f"{claim_prefix}_H{hypothesis_index}"
            pairs.append(
                {
                    "claim_id": claim_id,
                    "positive": str(hypothesis["statement"]),
                    "negative": str(hypothesis["exact_negation"]),
                    "earliest_unresolved_transition": str(
                        hypothesis["earliest_unresolved_transition"]
                    ),
                    "local_dependency_map": str(
                        hypothesis["local_dependency_map"]
                    ),
                }
            )
            provenance[claim_id] = {
                "case_name": case["case_name"],
                "source_claim_id": source["source_claim_id"],
                "source_status": status,
                "source_arm": source["source_arm"],
                "source_round": source["source_round"],
                "salvage_decision": case["record"]["decision"],
                "relation_to_failed_hypothesis": hypothesis[
                    "relation_to_failed_hypothesis"
                ],
            }

    # `prove_pairs` is the same imported v0.3.72 function used by the successful
    # experiment: t=.6 initial proof, t=.2 repair, two concurrent sides, then the
    # two-call unanimous alignment + one-call validity split verifier.
    verified, unresolved = prove_pairs(
        runtime=runtime,
        verifier_runtime=verifier_runtime,
        problem=problem,
        pairs=pairs,
        output_dir=output_dir / "atomic_proof_generation",
    )
    for row in verified:
        row["failure_salvage_provenance"] = provenance[row["lemma_id"]]
    result = {
        "selected_failure_count": len(selected),
        "selected_failures": selected,
        "generated_hypothesis_count": len(pairs),
        "verified": verified,
        "unresolved": unresolved,
        "cases": cases,
        "provenance": provenance,
    }
    write_json(output_dir / "summary.json", result)
    return result
