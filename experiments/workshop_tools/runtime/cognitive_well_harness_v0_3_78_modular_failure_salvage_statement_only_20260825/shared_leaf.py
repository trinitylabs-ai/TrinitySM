from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.extraction import (
    extract_atomic_hypotheses,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.gate import (
    evaluate_all,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.lemma_proving import (
    prove_pairs,
    validate_and_repair_negations,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.runtime import (
    ResilientModelRuntime,
    recovery_profile,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.split_verifier import (
    make_gemma_verifier_runtime,
)
from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824 import (
    run as v063_terminal,
)

from . import HARNESS_VERSION
from .contracts import (
    ARMS,
    EXTRACTION_SCHEDULE,
    MAX_FAILURE_SALVAGE_CASES,
    STATEMENT_ONLY_CONFIGURATIONS,
    V072_SYNTHESIS_CONFIGURATIONS,
    safe_name,
    sha256_text,
)
from .memory import extend_shared_verified_exact, merge_shared_verified_exact
from .salvage import (
    EXPERIMENT_MASTER_SEED,
    failure_card_for_pair,
    run_failure_guided_salvage,
)
from .synthesis import (
    generate_statement_only_samples,
    generate_v072_arm_samples,
)


def status(output_dir: Path, **values: Any) -> None:
    write_json(output_dir / "status.json", {**values, "updated_at": utc_now()})


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_and_prove_arm(
    *,
    arm: str,
    runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    output_dir: Path,
    extraction_schedule: tuple[dict[str, Any], ...] = EXTRACTION_SCHEDULE,
) -> dict[str, Any]:
    arm_dir = output_dir / "arms" / arm
    round_results: list[dict[str, Any]] = []
    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    failure_cards: list[dict[str, Any]] = []
    for schedule in extraction_schedule:
        round_number = int(schedule["round"])
        round_dir = arm_dir / f"round_{round_number}"
        status(
            output_dir,
            state="running",
            stage=f"{arm}:unconditional_hypothesis_extraction_round_{round_number}",
            arm=arm,
            temperature=schedule["temperature"],
        )
        extraction = extract_atomic_hypotheses(
            runtime=runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            arm=arm,
            temperature=float(schedule["temperature"]),
            round_number=round_number,
            output_dir=round_dir / "extraction",
        )
        pairs = validate_and_repair_negations(
            runtime=runtime,
            problem=problem,
            hypotheses=extraction["record"],
            arm=arm,
            round_number=round_number,
            output_dir=round_dir / "negation_validation",
        )
        status(
            output_dir,
            state="running",
            stage=f"{arm}:split_verified_lemma_proving_round_{round_number}",
            arm=arm,
            hypothesis_count=len(pairs),
        )
        round_verified, round_unresolved = prove_pairs(
            runtime=runtime,
            verifier_runtime=verifier_runtime,
            problem=problem,
            pairs=pairs,
            output_dir=round_dir / "lemma_proving",
        )
        verified.extend(round_verified)
        unresolved.extend(round_unresolved)
        round_failure_cards: list[dict[str, Any]] = []
        for pair in pairs:
            pair_dir = round_dir / "lemma_proving" / pair["claim_id"]
            card = failure_card_for_pair(
                pair=pair,
                positive=_read_json(pair_dir / "positive" / "result.json"),
                negative=_read_json(pair_dir / "negative" / "result.json"),
                source_arm=arm,
                round_number=round_number,
            )
            if card is not None:
                round_failure_cards.append(card)
        failure_cards.extend(round_failure_cards)
        result = {
            "arm": arm,
            "round": round_number,
            "temperature": schedule["temperature"],
            "diagnostics_exposed": arm == "diagnostic",
            "hypothesis_count": len(pairs),
            "verified_lemma_count": len(round_verified),
            "unresolved_count": len(round_unresolved),
            "failure_salvage_eligible_count": len(round_failure_cards),
        }
        round_results.append(result)
        write_json(round_dir / "summary.json", result)
    return {
        "arm": arm,
        "diagnostics_exposed": arm == "diagnostic",
        "rounds": round_results,
        "verified": verified,
        "unresolved": unresolved,
        "failure_cards": failure_cards,
    }


def _leaf_manifest(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str = "http://127.0.0.1:8021/v1",
    extraction_schedule: tuple[dict[str, Any], ...] = EXTRACTION_SCHEDULE,
    extraction_provenance: dict[str, Any] | None = None,
    run_final_gate: bool = True,
) -> dict[str, Any]:
    pipeline = [
        "configured_unconditional_extractions_per_arm",
        "paired_claim_and_negation_proving",
        "gemma_split_claim_alignment_and_mathematical_validity",
        "initial_location_preserving_exact_dedup_memory_insertion",
        "exact_v063_failure_guided_repair_or_atomic_decomposition_pass",
        "exact_experimental_paired_atomic_proving_and_split_verification",
        "exact_dedup_salvage_memory_insertion",
        "preserved_v072_twelve_candidate_three_family_synthesis",
        "exact_v063_four_candidate_statement_only_terminal_synthesis",
    ]
    if run_final_gate:
        pipeline.append("structural_and_gemma_split_final_gate")
    return {
        "schema": "cognitive-well-v078-failure-salvage-statement-only-leaf-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "problem_id": run_input["problem_id"],
        "input_path": str(input_path.resolve()),
        "pipeline": pipeline,
        "features": {
            "v072_generation_verification_and_synthesis_preserved": True,
            "v072_semantic_dedup_preserved": False,
            "shared_certified_lemma_memory": True,
            "initial_memory_materialized_before_salvage": True,
            "failure_guided_salvage": True,
            "maximum_failure_salvage_cases": MAX_FAILURE_SALVAGE_CASES,
            "salvage_actions": ["REPAIR", "DECOMPOSE", "ABANDON"],
            "salvage_positive_and_negative_atomic_proving": True,
            "recursive_parent_child_repair": False,
            "location_fields_in_memory": True,
            "exact_memory_dedup": True,
            "semantic_memory_dedup": False,
            "semantic_dedup_model_calls": 0,
            "final_split_verifier_gate": run_final_gate,
            "statement_only_terminal_prompt": (
                "exact_v063_experimental_main_proof_prompt"
            ),
            "statement_only_dynamic_prompt_fields": [
                "problem",
                "certified_lemma_statement",
            ],
            "statement_only_excluded_prompt_fields": [
                "source_candidate_proof",
                "failed_lemma_proof",
                "certified_lemma_proof",
                "earliest_unresolved_transition",
                "local_dependency_map",
                "synthesis_instructions",
            ],
            "statement_only_appendix": "exact_v063_cited_lemma_body_assembly",
            "coverage_based_iteration": False,
            "citation_use_repair": False,
        },
        "extraction_schedule": list(extraction_schedule),
        "extraction_provenance": extraction_provenance,
        "v072_synthesis_schedule": V072_SYNTHESIS_CONFIGURATIONS,
        "statement_only_synthesis_schedule": STATEMENT_ONLY_CONFIGURATIONS,
        "failure_salvage_exact_replica": {
            "source_generation_script": (
                "v0.3.63 run_failure_guided_salvage_surgical"
            ),
            "source_proof_verification_script": (
                "v0.3.63 run_failure_guided_salvage_proof_verification"
            ),
            "selected_statuses": [
                "REFUTED",
                "PROOF_FAILED",
                "VERIFIER_CONFLICT",
            ],
            "maximum_one_case_per_status": False,
            "selection_policy": "all_eligible_cards_up_to_limit_collision_free",
            "model": v063_terminal.base.GEMMA_MODEL,
            "model_revision": v063_terminal.base.GEMMA_REVISION,
            "dtype": "bfloat16",
            "server_side_mtp": 4,
            "writer_endpoint": runtime_config.gemma_endpoint,
            "verifier_endpoint": salvage_verifier_endpoint,
            "hypothesis_prompt": "exact_v063_SYSTEM_PROMPT",
            "hypothesis_user_prompt_layout": "exact_v063_run_case_layout",
            "hypothesis_schema": "exact_v063_SALVAGE_SCHEMA",
            "hypothesis_temperature": 0.4,
            "hypothesis_max_tokens": 32_768,
            "hypothesis_top_p": 0.95,
            "hypothesis_top_k": 64,
            "hypothesis_reasoning_effort": "max",
            "hypothesis_recovery_phases": ["compact", "repair_1"],
            "hypothesis_recovery_max_tokens": 16_384,
            "cross_model_salvage_fallback": False,
            "hypothesis_seed_labels": [
                "v063:failure_guided_salvage:refuted",
                "v063:failure_guided_salvage:proof_failed",
                "v063:failure_guided_salvage:verifier_conflict",
            ],
            "proof_writer_initial_temperature": 0.6,
            "proof_writer_repair_temperature": 0.2,
            "proof_writer_max_tokens": 32_768,
            "proof_writer_top_p": 0.95,
            "proof_writer_top_k": 64,
            "proof_writer_reasoning_effort": "max",
            "proof_side_parallel_workers": 2,
            "split_verifier_alignment_calls": 2,
            "split_verifier_alignment_rule": "unanimous",
            "split_verifier_validity_calls": 1,
            "split_verifier_temperature": 0.1,
            "split_verifier_max_tokens": 32_768,
            "split_verifier_top_p": 1.0,
            "split_verifier_top_k": -1,
            "split_verifier_reasoning_effort": "max",
            "proof_and_verifier_master_seed": EXPERIMENT_MASTER_SEED,
            "repetition_detection": {
                "min_pattern_size": 8,
                "max_pattern_size": 128,
                "min_count": 3,
            },
            "timeout_seconds": 14_400,
        },
        "statement_only_exact_replica": {
            "source_harness": "0.3.63-deterministic-lemma-appendix",
            "model": v063_terminal.base.GEMMA_MODEL,
            "dtype": "bfloat16",
            "server_side_mtp": 4,
            "endpoint": runtime_config.gemma_endpoint,
            "generation_helper": (
                "v0.3.57 run_arm.gemma_text as called by "
                "v0.3.63 run.generate_candidate"
            ),
            "stage": "main_composition",
            "user_prompt": "Execute the requested mathematical task now.",
            "max_tokens": 32_768,
            "top_p": 0.95,
            "top_k": 64,
            "thinking_token_budget": None,
            "reasoning_effort": "max",
            "repetition_detection": {
                "min_pattern_size": 8,
                "max_pattern_size": 128,
                "min_count": 3,
            },
            "timeout_seconds": 14_400,
            "seed_labels": [
                f"v063:{row['candidate_id']}:main_composition"
                for row in STATEMENT_ONLY_CONFIGURATIONS
            ],
            "parallel_workers": 4,
            "transport_recovery_wrapper": False,
            "prompt_function": "v0.3.63 protocol.main_proof_prompt",
            "appendix_function": "v0.3.63 protocol.assemble_used_lemma_appendix",
        },
        "synthesis_counts": {
            "v072_per_arm": 6,
            "v072_overall": 12,
            "statement_only_shared": 4,
            "overall": 16,
        },
        "gate_policy": run_input["gate"],
        "verifier": {
            "model": runtime_config.gemma_model,
            "temperature": 0.1,
            "max_tokens": 32_768,
            "alignment_calls": 2,
            "alignment_requirement": "unanimous",
            "mathematical_validity_calls_after_alignment": 1,
            "assigned_claim_required_at_final_gate": True,
            "opposite_claim_salvaged_for_lemma_memory": True,
            "all_recovery_roles_resolve_to_same_model": True,
        },
        "recovery_profile": recovery_profile(),
        "runtime": {
            "gemma_model": runtime_config.gemma_model,
            "qwen_model": runtime_config.qwen_model,
            "gemma_endpoint": runtime_config.gemma_endpoint,
            "qwen_endpoint": runtime_config.qwen_endpoint,
            "master_seed": runtime_config.master_seed,
        },
        "reference_solution_access": False,
        "gold_score_access": False,
    }


def run_shared_leaf(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str = "http://127.0.0.1:8021/v1",
    extraction_schedule: tuple[dict[str, Any], ...] | None = None,
    extraction_provenance: dict[str, Any] | None = None,
    run_final_gate: bool = True,
) -> dict[str, Any]:
    if runtime_config.gemma_model != v063_terminal.base.GEMMA_MODEL:
        raise ValueError(
            "exact statement-only replica requires "
            f"{v063_terminal.base.GEMMA_MODEL}, got {runtime_config.gemma_model}"
        )
    active_extraction_schedule = tuple(extraction_schedule or EXTRACTION_SCHEDULE)
    if not active_extraction_schedule:
        raise ValueError("extraction schedule must not be empty")
    round_numbers = [int(row["round"]) for row in active_extraction_schedule]
    if len(round_numbers) != len(set(round_numbers)):
        raise ValueError("extraction schedule round numbers must be unique")
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        _leaf_manifest(
            run_input=run_input,
            input_path=input_path,
            runtime_config=runtime_config,
            salvage_verifier_endpoint=salvage_verifier_endpoint,
            extraction_schedule=active_extraction_schedule,
            extraction_provenance=extraction_provenance,
            run_final_gate=run_final_gate,
        ),
    )
    runtime = ResilientModelRuntime(runtime_config)
    verifier_runtime = make_gemma_verifier_runtime(runtime_config)
    salvage_proof_runtime = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=runtime_config.gemma_endpoint,
            qwen_endpoint=runtime_config.qwen_endpoint,
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.qwen_model,
            master_seed=EXPERIMENT_MASTER_SEED,
        )
    )
    salvage_verifier_runtime = make_gemma_verifier_runtime(
        RuntimeConfig(
            gemma_endpoint=salvage_verifier_endpoint.rstrip("/"),
            qwen_endpoint=salvage_verifier_endpoint.rstrip("/"),
            gemma_model=runtime_config.gemma_model,
            qwen_model=runtime_config.gemma_model,
            master_seed=EXPERIMENT_MASTER_SEED,
        )
    )
    problem = str(run_input["problem"])
    candidate_proofs = list(run_input["candidate_proofs"])
    anchor_proof = str(
        next(row["proof"] for row in candidate_proofs if row["role"] == "anchor")
    )
    try:
        arm_results = [
            _extract_and_prove_arm(
                arm=arm,
                runtime=runtime,
                verifier_runtime=verifier_runtime,
                problem=problem,
                candidate_proofs=candidate_proofs,
                output_dir=output_dir,
                extraction_schedule=active_extraction_schedule,
            )
            for arm in ARMS
        ]

        status(output_dir, state="running", stage="initial_exact_memory_insertion")
        initial_verified, initial_dedup_audit = merge_shared_verified_exact(
            arm_results=arm_results,
            output_dir=output_dir / "initial_exact_dedup",
        )
        initial_unresolved = [
            {**row, "source_arm": arm_result["arm"]}
            for arm_result in arm_results
            for row in arm_result["unresolved"]
        ]
        write_json(
            output_dir / "initial_shared_lemma_memory.json",
            {
                "schema": "cognitive-well-v078-initial-shared-lemma-memory-v1",
                "verified": initial_verified,
                "unresolved": initial_unresolved,
                "dedup_policy": "exact_only",
                "exact_dedup_audit_path": str(
                    (output_dir / "initial_exact_dedup" / "audit.json").resolve()
                ),
            },
        )

        failure_cards = [
            row for arm_result in arm_results for row in arm_result["failure_cards"]
        ]
        status(
            output_dir,
            state="running",
            stage="bounded_failure_guided_salvage",
            initial_shared_lemma_count=len(initial_verified),
            eligible_failure_count=len(failure_cards),
            maximum_selected_failures=MAX_FAILURE_SALVAGE_CASES,
        )
        salvage = run_failure_guided_salvage(
            runtime=salvage_proof_runtime,
            verifier_runtime=salvage_verifier_runtime,
            problem=problem,
            candidate_proofs=candidate_proofs,
            failure_cards=failure_cards,
            output_dir=output_dir / "failure_guided_salvage",
        )

        status(
            output_dir,
            state="running",
            stage="salvage_exact_memory_insertion",
            salvage_verified_lemma_count=len(salvage["verified"]),
        )
        shared_verified, salvage_dedup_audit = extend_shared_verified_exact(
            existing_verified=initial_verified,
            salvage_verified=salvage["verified"],
            output_dir=output_dir / "salvage_exact_dedup",
        )
        shared_unresolved = initial_unresolved + [
            {**row, "source_arm": "failure_salvage"}
            for row in salvage["unresolved"]
        ]
        write_json(
            output_dir / "shared_lemma_memory.json",
            {
                "schema": "cognitive-well-v078-augmented-shared-lemma-memory-v1",
                "initial_verified_count": len(initial_verified),
                "salvage_verified_before_dedup_count": len(salvage["verified"]),
                "final_verified_count": len(shared_verified),
                "verified": shared_verified,
                "unresolved": shared_unresolved,
                "dedup_policy": "exact_only",
                "semantic_dedup_model_calls": 0,
                "initial_exact_dedup_audit_path": str(
                    (output_dir / "initial_exact_dedup" / "audit.json").resolve()
                ),
                "salvage_exact_dedup_audit_path": str(
                    (output_dir / "salvage_exact_dedup" / "audit.json").resolve()
                ),
            },
        )

        candidates: list[dict[str, Any]] = []
        shared_labels: list[dict[str, str]] = []
        statement_only_candidates: list[dict[str, Any]] = []
        if shared_verified:
            for arm_result in arm_results:
                arm = str(arm_result["arm"])
                status(
                    output_dir,
                    state="running",
                    stage=f"{arm}:preserved_v072_synthesis",
                    arm=arm,
                    shared_verified_lemma_count=len(shared_verified),
                )
                labels, arm_candidates = generate_v072_arm_samples(
                    runtime=runtime,
                    arm=arm,
                    problem=problem,
                    verified=shared_verified,
                    anchor_proof=anchor_proof,
                    synthesis_instructions=str(run_input["synthesis_instructions"]),
                    gate_policy=run_input["gate"],
                    output_dir=output_dir / "arms" / arm / "synthesis",
                )
                if not shared_labels:
                    shared_labels = labels
                elif labels != shared_labels:
                    raise RuntimeError("shared lemma labels changed between synthesis arms")
                arm_result["lemmas"] = labels
                arm_result["candidates"] = arm_candidates
                candidates.extend(arm_candidates)

            status(
                output_dir,
                state="running",
                stage="exact_v063_statement_only_terminal_synthesis",
                shared_verified_lemma_count=len(shared_verified),
                synthesis_candidate_count=4,
            )
            terminal_labels, statement_only_candidates = (
                generate_statement_only_samples(
                    runtime=runtime,
                    problem=problem,
                    verified=shared_verified,
                    gate_policy=run_input["gate"],
                    output_dir=output_dir / "statement_only_terminal_synthesis",
                )
            )
            terminal_core = [
                {key: row[key] for key in ("label", "statement", "proof")}
                for row in terminal_labels
            ]
            shared_core = [
                {key: row[key] for key in ("label", "statement", "proof")}
                for row in shared_labels
            ]
            if terminal_core != shared_core:
                raise RuntimeError(
                    "shared lemma labels changed in statement-only terminal synthesis"
                )
            candidates.extend(statement_only_candidates)
        else:
            for arm_result in arm_results:
                arm_result["lemmas"] = []
                arm_result["candidates"] = []

        for arm_result in arm_results:
            write_json(
                output_dir / "arms" / str(arm_result["arm"]) / "summary.json",
                {
                    "arm": arm_result["arm"],
                    "diagnostics_exposed": arm_result["diagnostics_exposed"],
                    "rounds": arm_result["rounds"],
                    "unconditional_extraction_round_count": len(
                        arm_result["rounds"]
                    ),
                    "local_verified_lemma_count": len(arm_result["verified"]),
                    "local_unresolved_count": len(arm_result["unresolved"]),
                    "failure_salvage_eligible_count": len(
                        arm_result["failure_cards"]
                    ),
                    "shared_synthesis_lemma_count": len(arm_result["lemmas"]),
                    "synthesis_candidate_count": len(arm_result["candidates"]),
                },
            )

        gate_results = []
        if candidates and run_final_gate:
            status(
                output_dir,
                state="running",
                stage="candidate_split_verifier_gate",
                synthesis_candidate_count=len(candidates),
            )
            gate_results = evaluate_all(
                verifier_runtime=verifier_runtime,
                problem=problem,
                candidates=candidates,
                gate_policy=run_input["gate"],
                output_dir=output_dir / "gate",
            )
        gate_by_id = {row["candidate_id"]: row for row in gate_results}
        passed_dir = output_dir / "passed_proofs"
        passed_dir.mkdir(parents=True, exist_ok=True)
        passed: list[dict[str, Any]] = []
        candidate_summaries: list[dict[str, Any]] = []
        for candidate in candidates:
            gate_result = gate_by_id.get(str(candidate["candidate_id"]))
            candidate_summaries.append(
                {
                    key: candidate[key]
                    for key in (
                        "candidate_id",
                        "arm",
                        "family",
                        "temperature",
                        "replicate",
                        "proof_sha256",
                        "assembly",
                    )
                }
                | {"gate": gate_result}
            )
            if gate_result is not None and gate_result["passed"]:
                destination = passed_dir / f"{safe_name(str(candidate['candidate_id']))}.md"
                destination.write_text(
                    str(candidate["proof"]).rstrip() + "\n", encoding="utf-8"
                )
                passed.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "arm": candidate["arm"],
                        "family": candidate["family"],
                        "temperature": candidate["temperature"],
                        "proof_sha256": candidate["proof_sha256"],
                        "path": str(destination.resolve()),
                    }
                )
        write_json(passed_dir / "manifest.json", {"passed_proofs": passed})

        main_recovery = runtime.recovery_events()
        verifier_recovery = verifier_runtime.recovery_events()
        salvage_proof_recovery = salvage_proof_runtime.recovery_events()
        salvage_verifier_recovery = salvage_verifier_runtime.recovery_events()
        write_json(
            output_dir / "recovery_events.json",
            {
                "profile": recovery_profile(),
                "generation_runtime": main_recovery,
                "gemma_verifier_runtime": verifier_recovery,
                "salvage_proof_runtime": salvage_proof_recovery,
                "salvage_verifier_runtime": salvage_verifier_recovery,
            },
        )
        summary = {
            "schema": "cognitive-well-v078-failure-salvage-statement-only-leaf-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "problem_id": run_input["problem_id"],
            "arms": [
                {
                    "arm": row["arm"],
                    "rounds": row["rounds"],
                    "local_verified_lemma_count": len(row["verified"]),
                    "local_unresolved_count": len(row["unresolved"]),
                    "failure_salvage_eligible_count": len(row["failure_cards"]),
                    "synthesis_candidate_count": len(row["candidates"]),
                }
                for row in arm_results
            ],
            "initial_shared_lemma_count": len(initial_verified),
            "failure_salvage": {
                "eligible_count": len(failure_cards),
                "selected_count": salvage["selected_failure_count"],
                "generated_hypothesis_count": salvage[
                    "generated_hypothesis_count"
                ],
                "verified_before_dedup_count": len(salvage["verified"]),
                "unresolved_count": len(salvage["unresolved"]),
            },
            "shared_lemma_count": len(shared_verified),
            "dedup_policy": "exact_only",
            "semantic_dedup_model_calls": 0,
            "initial_exact_dedup_audit_entry_count": len(initial_dedup_audit),
            "salvage_exact_dedup_audit_entry_count": len(salvage_dedup_audit),
            "shared_lemmas": [
                {
                    "label": row["label"],
                    "source_lemma_id": row["source_lemma_id"],
                    "statement_sha256": sha256_text(row["statement"]),
                    "proof_sha256": sha256_text(row["proof"]),
                    "earliest_unresolved_transition": row[
                        "earliest_unresolved_transition"
                    ],
                    "local_dependency_map": row["local_dependency_map"],
                }
                for row in shared_labels
            ],
            "v072_synthesis_candidate_count": sum(
                len(row["candidates"]) for row in arm_results
            ),
            "statement_only_synthesis_candidate_count": len(
                statement_only_candidates
            ),
            "synthesis_candidate_count": len(candidates),
            "synthesis_candidates": candidate_summaries,
            "final_split_verifier_gate_run": run_final_gate,
            "final_split_verifier_gate_skipped": not run_final_gate,
            "passed_proof_count": len(passed),
            "passed_proofs": passed,
            "recovery": {
                "generation_boundary_count": len(main_recovery),
                "verifier_boundary_count": len(verifier_recovery),
                "salvage_proof_boundary_count": len(salvage_proof_recovery),
                "salvage_verifier_boundary_count": len(salvage_verifier_recovery),
            },
            "terra_calls": 0,
            "numeric_scoring": False,
        }
        write_json(output_dir / "summary.json", summary)
        status(
            output_dir,
            state="completed",
            stage="publish_passed_proofs",
            initial_shared_lemma_count=len(initial_verified),
            shared_lemma_count=len(shared_verified),
            synthesis_candidate_count=len(candidates),
            passed_proof_count=len(passed),
        )
        return summary
    except Exception as error:
        write_json(
            output_dir / "recovery_events.json",
            {
                "profile": recovery_profile(),
                "generation_runtime": runtime.recovery_events(),
                "gemma_verifier_runtime": verifier_runtime.recovery_events(),
                "salvage_proof_runtime": salvage_proof_runtime.recovery_events(),
                "salvage_verifier_runtime": salvage_verifier_runtime.recovery_events(),
            },
        )
        status(
            output_dir,
            state="failed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise
