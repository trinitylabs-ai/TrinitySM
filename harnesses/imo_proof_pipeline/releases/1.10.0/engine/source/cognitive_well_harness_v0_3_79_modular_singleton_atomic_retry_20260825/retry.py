from __future__ import annotations

import concurrent.futures
import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.lemma_proving import (
    prove_pairs,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.split_verifier import (
    make_gemma_verifier_runtime,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.memory import (
    extend_shared_verified_exact,
)
from cognitive_well_harness_v0_3_78_modular_failure_salvage_statement_only_20260825.prompts import (
    failure_salvage_user_prompt,
)
from . import HARNESS_VERSION
from .runtime import ResilientModelRuntime, recovery_profile
from .salvage import (
    EXPERIMENT_MASTER_SEED,
    _run_exact_v063_salvage_generation,
    failure_card_for_pair,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _hypothesis_index(claim_id: str) -> int:
    match = re.search(r"_H([1-9][0-9]*)$", claim_id)
    if match is None:
        raise ValueError(f"cannot recover hypothesis index from {claim_id}")
    return int(match.group(1)) - 1


def select_failed_decomposed_children(
    salvage_summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Select unresolved children only from prior multi-child decompositions."""
    cases = {str(row["case_name"]): row for row in salvage_summary["cases"]}
    provenance = dict(salvage_summary["provenance"])
    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for unresolved in salvage_summary["unresolved"]:
        claim_id = str(unresolved["claim_id"])
        source = provenance[claim_id]
        case = cases[str(source["case_name"])]
        hypotheses = list(case["record"]["hypotheses"])
        if case["record"]["decision"] != "DECOMPOSE" or len(hypotheses) <= 1:
            skipped.append(
                {
                    "claim_id": claim_id,
                    "reason": "parent_salvage_was_not_a_multi_child_decomposition",
                    "parent_decision": case["record"]["decision"],
                    "parent_child_count": len(hypotheses),
                }
            )
            continue
        index = _hypothesis_index(claim_id)
        if index >= len(hypotheses):
            raise ValueError(f"hypothesis index out of range for {claim_id}")
        hypothesis = hypotheses[index]
        selected.append(
            {
                "claim_id": claim_id,
                "parent_case_name": case["case_name"],
                "parent_source": case["source"],
                "parent_decision": case["record"]["decision"],
                "parent_child_count": len(hypotheses),
                "parent_hypothesis_index": index + 1,
                "hypothesis": hypothesis,
            }
        )
    return selected, skipped


def singleton_gate(record: dict[str, Any]) -> tuple[bool, str]:
    decision = str(record.get("decision") or "")
    count = len(record.get("hypotheses") or [])
    if decision == "DECOMPOSE":
        return False, "retry_decomposed_observe_only"
    if decision == "ABANDON":
        return False, "retry_abandoned"
    if decision != "REPAIR":
        return False, f"retry_decision_{decision or 'missing'}_not_admissible"
    if count != 1:
        return False, f"repair_returned_{count}_hypotheses_instead_of_exactly_one"
    return True, "accepted_single_repair"


def _retry_one(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    source_salvage_dir: Path,
    target: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    source_claim_id = str(target["claim_id"])
    source_pair = {
        "claim_id": source_claim_id,
        "positive": str(target["hypothesis"]["statement"]),
        "negative": str(target["hypothesis"]["exact_negation"]),
        "earliest_unresolved_transition": str(
            target["hypothesis"]["earliest_unresolved_transition"]
        ),
        "local_dependency_map": str(
            target["hypothesis"]["local_dependency_map"]
        ),
    }
    source_pair_dir = source_salvage_dir / "atomic_proof_generation" / source_claim_id
    wrapper = failure_card_for_pair(
        pair=source_pair,
        positive=read_json(source_pair_dir / "positive" / "result.json"),
        negative=read_json(source_pair_dir / "negative" / "result.json"),
        source_arm=str(target["parent_source"]["source_arm"]),
        round_number=int(target["parent_source"]["source_round"]),
    )
    if wrapper is None:
        raise ValueError(f"retry target unexpectedly certified: {source_claim_id}")
    failure_card = dict(wrapper["failure_card"])
    # Use the ordinary failure-salvage prompt unchanged. The model may naturally
    # choose REPAIR, DECOMPOSE, or ABANDON; the non-recursive admission policy is
    # enforced after observing the structured response.
    user_prompt = failure_salvage_user_prompt(
        problem=problem,
        candidate_proofs=candidate_proofs,
        failure_card=failure_card,
    )
    retry_case_name = "atomic_retry_" + re.sub(
        r"[^a-z0-9]+", "_", source_claim_id.lower()
    ).strip("_")
    destination = output_dir / "hypothesis_salvage" / retry_case_name
    try:
        record, generation = _run_exact_v063_salvage_generation(
            runtime=runtime,
            case_name=retry_case_name,
            user_prompt=user_prompt,
            destination=destination,
        )
    except RuntimeError as error:
        if not str(error).startswith("structured salvage recovery exhausted:"):
            raise
        result = {
            "schema": "cognitive-well-v079-singleton-atomic-retry-case-v1",
            "retry_depth": 1,
            "maximum_retry_depth": 1,
            "source_claim_id": source_claim_id,
            "source_parent_case_name": target["parent_case_name"],
            "source_parent_decision": target["parent_decision"],
            "source_parent_child_count": target["parent_child_count"],
            "failure_card": failure_card,
            "record": {
                "decision": "GENERATION_FAILED",
                "failure_interpretation": str(error),
                "hypotheses": [],
            },
            "singleton_gate": {
                "accepted": False,
                "reason": "structured_retry_generation_exhausted",
                "returned_hypothesis_count": 0,
            },
            "generation": {"error": str(error)},
            "further_retry_allowed": False,
        }
        write_json(destination / "result.json", result)
        return result
    accepted, gate_reason = singleton_gate(record)
    result = {
        "schema": "cognitive-well-v079-singleton-atomic-retry-case-v1",
        "retry_depth": 1,
        "maximum_retry_depth": 1,
        "source_claim_id": source_claim_id,
        "source_parent_case_name": target["parent_case_name"],
        "source_parent_decision": target["parent_decision"],
        "source_parent_child_count": target["parent_child_count"],
        "failure_card": failure_card,
        "record": record,
        "singleton_gate": {
            "accepted": accepted,
            "reason": gate_reason,
            "returned_hypothesis_count": len(record.get("hypotheses") or []),
        },
        "generation": generation["metadata"],
        "further_retry_allowed": False,
    }
    write_json(destination / "result.json", result)
    return result


def run_atomic_retry(
    *,
    source_run_dir: Path,
    input_path: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
) -> dict[str, Any]:
    source_salvage_dir = source_run_dir / "failure_guided_salvage"
    source_summary_path = source_salvage_dir / "summary.json"
    source_memory_path = source_run_dir / "shared_lemma_memory.json"
    source_summary = read_json(source_summary_path)
    source_memory = read_json(source_memory_path)
    run_input = read_json(input_path)
    problem = str(run_input["problem"])
    candidate_proofs = list(run_input["candidate_proofs"])
    selected, skipped = select_failed_decomposed_children(source_summary)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        {
            "schema": "cognitive-well-v079-singleton-atomic-retry-manifest-v1",
            "harness_version": HARNESS_VERSION,
            "created_at": utc_now(),
            "source_run_dir": str(source_run_dir.resolve()),
            "source_salvage_summary": str(source_summary_path.resolve()),
            "source_shared_memory": str(source_memory_path.resolve()),
            "input_path": str(input_path.resolve()),
            "selection_rule": (
                "unresolved_child_from_DECOMPOSE_parent_with_more_than_one_child"
            ),
            "retry_count_per_child": 1,
            "generation_prompt": "unchanged_v078_failure_salvage_prompt",
            "model_decisions_observed": ["REPAIR", "DECOMPOSE", "ABANDON"],
            "admitted_decision": "REPAIR",
            "admitted_hypothesis_count": 1,
            "decompose_policy": "observe_and_reject_without_proving",
            "abandon_policy": "reject_without_proving",
            "recursive_retry": False,
            "eligible_claim_ids": [row["claim_id"] for row in selected],
            "skipped": skipped,
            "hypothesis_generation": {
                "model": runtime_config.gemma_model,
                "endpoint": runtime_config.gemma_endpoint,
                "temperature": 0.4,
                "max_tokens": 32_768,
                "top_p": 0.95,
                "top_k": 64,
                "reasoning_effort": "max",
            },
            "paired_proving": {
                "model": runtime_config.gemma_model,
                "initial_temperature": 0.6,
                "repair_temperature": 0.2,
                "max_tokens": 32_768,
            },
            "split_verifier": {
                "model": runtime_config.gemma_model,
                "endpoint": salvage_verifier_endpoint.rstrip("/"),
                "alignment_calls": 2,
                "alignment_rule": "unanimous",
                "validity_calls": 1,
                "temperature": 0.1,
                "max_tokens": 32_768,
            },
            "memory_dedup": "exact_only",
            "semantic_dedup_model_calls": 0,
            "reference_solution_access": False,
            "gold_score_access": False,
        },
    )

    proof_runtime = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.qwen_model,
            master_seed=EXPERIMENT_MASTER_SEED,
        )
    )
    verifier_runtime = make_gemma_verifier_runtime(
        RuntimeConfig(
            gemma_endpoint=salvage_verifier_endpoint.rstrip("/"),
            qwen_endpoint=salvage_verifier_endpoint.rstrip("/"),
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.gemma_model,
            master_seed=EXPERIMENT_MASTER_SEED,
        )
    )
    write_json(
        output_dir / "status.json",
        {
            "state": "running",
            "stage": "singleton_atomic_child_retry_generation",
            "eligible_count": len(selected),
            "updated_at": utc_now(),
        },
    )
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, len(selected))
    ) as executor:
        retry_cases = list(
            executor.map(
                lambda target: _retry_one(
                    runtime=proof_runtime,
                    problem=problem,
                    candidate_proofs=candidate_proofs,
                    source_salvage_dir=source_salvage_dir,
                    target=target,
                    output_dir=output_dir,
                ),
                selected,
            )
        )

    accepted_cases = [
        row for row in retry_cases if row["singleton_gate"]["accepted"]
    ]
    pairs: list[dict[str, str]] = []
    provenance: dict[str, dict[str, Any]] = {}
    for case in accepted_cases:
        hypothesis = case["record"]["hypotheses"][0]
        claim_id = f"RETRY_{case['source_claim_id']}"
        pairs.append(
            {
                "claim_id": claim_id,
                "positive": str(hypothesis["statement"]),
                "negative": str(hypothesis["exact_negation"]),
                "earliest_unresolved_transition": str(
                    hypothesis["earliest_unresolved_transition"]
                ),
                "local_dependency_map": str(hypothesis["local_dependency_map"]),
            }
        )
        provenance[claim_id] = {
            "retry_depth": 1,
            "source_claim_id": case["source_claim_id"],
            "source_parent_case_name": case["source_parent_case_name"],
            "source_parent_child_count": case["source_parent_child_count"],
            "retry_decision": case["record"]["decision"],
            "relation_to_failed_hypothesis": hypothesis[
                "relation_to_failed_hypothesis"
            ],
            "further_retry_allowed": False,
        }

    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    if pairs:
        write_json(
            output_dir / "status.json",
            {
                "state": "running",
                "stage": "paired_proving_and_split_verification",
                "claim_count": len(pairs),
                "updated_at": utc_now(),
            },
        )
        verified, unresolved = prove_pairs(
            runtime=proof_runtime,
            verifier_runtime=verifier_runtime,
            problem=problem,
            pairs=pairs,
            output_dir=output_dir / "atomic_proof_generation",
        )
        for row in verified:
            row["atomic_retry_provenance"] = provenance[row["lemma_id"]]

    augmented, dedup_audit = extend_shared_verified_exact(
        existing_verified=list(source_memory["verified"]),
        salvage_verified=verified,
        output_dir=output_dir / "exact_memory_insertion",
    )
    write_json(
        output_dir / "augmented_shared_lemma_memory.json",
        {
            "schema": "cognitive-well-v079-augmented-shared-lemma-memory-v1",
            "source_verified_count": len(source_memory["verified"]),
            "retry_verified_before_dedup_count": len(verified),
            "final_verified_count": len(augmented),
            "verified": augmented,
            "unresolved": list(source_memory.get("unresolved") or []) + unresolved,
            "dedup_policy": "exact_only",
            "semantic_dedup_model_calls": 0,
        },
    )
    result = {
        "schema": "cognitive-well-v079-singleton-atomic-retry-result-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "eligible_count": len(selected),
        "eligible_claim_ids": [row["claim_id"] for row in selected],
        "skipped": skipped,
        "retry_generation_count": len(retry_cases),
        "singleton_accepted_count": len(accepted_cases),
        "singleton_rejected_count": len(retry_cases) - len(accepted_cases),
        "generated_hypothesis_count": len(pairs),
        "verified_count": len(verified),
        "unresolved_count": len(unresolved),
        "verified": verified,
        "unresolved": unresolved,
        "retry_cases": retry_cases,
        "provenance": provenance,
        "source_memory_count": len(source_memory["verified"]),
        "final_memory_count": len(augmented),
        "exact_dedup_audit": dedup_audit,
        "further_retry_allowed": False,
        "proof_writer_recovery_events": proof_runtime.recovery_events(),
        "verifier_recovery_events": verifier_runtime.recovery_events(),
        "recovery_profile": recovery_profile(),
    }
    write_json(output_dir / "result.json", result)
    write_json(
        output_dir / "status.json",
        {
            "state": "completed",
            "stage": "exact_memory_insertion",
            "eligible_count": len(selected),
            "verified_count": len(verified),
            "final_memory_count": len(augmented),
            "updated_at": utc_now(),
        },
    )
    return result
