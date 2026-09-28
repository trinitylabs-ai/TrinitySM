from __future__ import annotations

import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import HARNESS_VERSION
from .contracts import ARMS, SYNTHESIS_CONFIGURATIONS, safe_name, sha256_text
from .extraction import extract_atomic_hypotheses
from .gate import evaluate_all
from .lemma_proving import prove_pairs, validate_and_repair_negations
from .model_runtime import ModelRuntime, RuntimeConfig, write_json
from .synthesis import generate_arm_samples


EXTRACTION_SCHEDULE = (
    {"round": 1, "temperature": 0.4},
    {"round": 2, "temperature": 0.8},
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def status(output_dir: Path, **values: Any) -> None:
    write_json(output_dir / "status.json", {**values, "updated_at": utc_now()})


def manifest(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    runtime_config: RuntimeConfig,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v0.3.64-modular-two-proof-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "pipeline": [
            "two_candidate_proofs",
            "fork_into_independent_original_and_diagnostic_arms",
            "per_arm_atomic_hypothesis_extraction",
            "per_arm_exact_negation_validation",
            "per_arm_lemma_proof_and_compact_certification",
            "four_synthesis_samples_per_arm",
            "lemma_evidence_only_vs_anchored_refinement",
            "deterministic_lemma_appendix",
            "structural_and_qwen_gate",
            "publish_all_passed_proofs",
        ],
        "input_path": str(input_path.resolve()),
        "problem_id": run_input["problem_id"],
        "problem_sha256": sha256_text(run_input["problem"]),
        "candidate_proofs": [
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof_sha256": sha256_text(row["proof"]),
                "diagnostic_supplied": bool(row.get("non_authoritative_diagnostic")),
            }
            for row in run_input["candidate_proofs"]
        ],
        "fixed_winning_configuration": {
            "constructive_model": runtime_config.gemma_model,
            "constructive_dtype": "bfloat16",
            "constructive_mtp": 4,
            "reasoning_effort": "max",
            "extraction_initial_temperature": 0.4,
            "extraction_fallback_temperature": 0.8,
            "fallback_condition": "zero certified lemmas after round 1",
            "parser_temperature": 0.1,
            "parser_schema": "minimal conjectures plus exact negations",
            "parser_attempts": 3,
            "deduplication_check": False,
            "lemma_proof_temperature": 0.6,
            "lemma_repair_temperature": 0.2,
            "verifier_model": runtime_config.qwen_model,
            "verifier_dtype": "bfloat16",
            "verifier_temperature": 0.2,
            "verifier_reasoning_effort": "max",
            "certification_schema": ["verdict", "exact_claim_reached"],
            "certification_attempts": 3,
        },
        "stochastic_synthesis_schedule": SYNTHESIS_CONFIGURATIONS,
        "arm_independence": {
            "arms": list(ARMS),
            "shared_lemmas": False,
            "shared_extraction_artifacts": False,
            "original_arm_diagnostics_exposed": False,
            "diagnostic_arm_diagnostics_exposed": True,
        },
        "synthesis_source_proof_policy": {
            "lemma_evidence_only": "no source proof",
            "anchored_refinement": "designated anchor proof only",
            "supplement_proof_exposed": False,
            "diagnostics_exposed": False,
        },
        "synthesis_receives_lemma_proof_bodies": False,
        "appendix_selection": "exact stored bodies of cited local lemmas",
        "gate_policy": run_input["gate"],
        "gemma_endpoint": runtime_config.gemma_endpoint,
        "qwen_endpoint": runtime_config.qwen_endpoint,
        "terra_calls": 0,
        "numeric_scoring": False,
        "reference_answer_accessed": False,
    }


def run_one_arm(
    *,
    arm: str,
    runtime: ModelRuntime,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    anchor_proof: str,
    synthesis_instructions: str,
    gate_policy: dict[str, Any],
    output_dir: Path,
    status_dir: Path,
) -> dict[str, Any]:
    arm_dir = output_dir / "arms" / arm
    round_results: list[dict[str, Any]] = []
    verified: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for schedule in EXTRACTION_SCHEDULE:
        round_number = int(schedule["round"])
        if round_number == 2 and verified:
            break
        round_dir = arm_dir / f"round_{round_number}"
        status(
            status_dir,
            state="running",
            stage=f"{arm}:hypothesis_extraction_round_{round_number}",
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
        status(
            status_dir,
            state="running",
            stage=f"{arm}:lemma_proving_round_{round_number}",
            arm=arm,
            hypothesis_count=len(extraction["record"]["conjectures"]),
        )
        pairs = validate_and_repair_negations(
            runtime=runtime,
            problem=problem,
            hypotheses=extraction["record"],
            arm=arm,
            round_number=round_number,
            output_dir=round_dir / "negation_validation",
        )
        round_verified, round_unresolved = prove_pairs(
            runtime=runtime,
            problem=problem,
            pairs=pairs,
            output_dir=round_dir / "lemma_proving",
        )
        verified.extend(round_verified)
        unresolved.extend(round_unresolved)
        round_result = {
            "arm": arm,
            "round": round_number,
            "temperature": schedule["temperature"],
            "diagnostics_exposed": arm == "diagnostic",
            "hypothesis_count": len(pairs),
            "verified_lemma_count": len(round_verified),
            "unresolved_count": len(round_unresolved),
        }
        round_results.append(round_result)
        write_json(round_dir / "summary.json", round_result)

    lemmas: list[dict[str, str]] = []
    candidates: list[dict[str, Any]] = []
    if verified:
        status(
            status_dir,
            state="running",
            stage=f"{arm}:four_sample_synthesis",
            arm=arm,
            verified_lemma_count=len(verified),
        )
        lemmas, candidates = generate_arm_samples(
            runtime=runtime,
            arm=arm,
            problem=problem,
            verified=verified,
            anchor_proof=anchor_proof,
            synthesis_instructions=synthesis_instructions,
            gate_policy=gate_policy,
            output_dir=arm_dir / "synthesis",
        )

    result = {
        "arm": arm,
        "diagnostics_exposed": arm == "diagnostic",
        "rounds": round_results,
        "fallback_triggered": len(round_results) == 2,
        "verified": verified,
        "unresolved": unresolved,
        "lemmas": lemmas,
        "candidates": candidates,
    }
    write_json(
        arm_dir / "summary.json",
        {
            "arm": arm,
            "diagnostics_exposed": result["diagnostics_exposed"],
            "rounds": round_results,
            "fallback_triggered": result["fallback_triggered"],
            "verified_lemma_count": len(verified),
            "unresolved_count": len(unresolved),
            "synthesis_candidate_count": len(candidates),
        },
    )
    return result


def run_pipeline(
    *,
    run_input: dict[str, Any],
    input_path: Path,
    output_dir: Path,
    runtime_config: RuntimeConfig,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "manifest.json",
        manifest(
            run_input=run_input,
            input_path=input_path,
            runtime_config=runtime_config,
        ),
    )
    runtime = ModelRuntime(runtime_config)
    problem = str(run_input["problem"])
    candidate_proofs = list(run_input["candidate_proofs"])
    anchor_proof = str(
        next(row["proof"] for row in candidate_proofs if row["role"] == "anchor")
    )
    try:
        arm_results = [
            run_one_arm(
                arm=arm,
                runtime=runtime,
                problem=problem,
                candidate_proofs=candidate_proofs,
                anchor_proof=anchor_proof,
                synthesis_instructions=str(run_input["synthesis_instructions"]),
                gate_policy=run_input["gate"],
                output_dir=output_dir,
                status_dir=output_dir,
            )
            for arm in ARMS
        ]
        candidates = [
            candidate
            for arm_result in arm_results
            for candidate in arm_result["candidates"]
        ]
        gate_results: list[dict[str, Any]] = []
        if candidates:
            status(
                output_dir,
                state="running",
                stage="candidate_gate",
                structurally_passing=sum(
                    row["assembly"]["structural_gate"]["passed"] for row in candidates
                ),
            )
            gate_results = evaluate_all(
                runtime=runtime,
                problem=problem,
                candidates=candidates,
                gate_policy=run_input["gate"],
                output_dir=output_dir / "gate",
            )

        gate_by_id = {row["candidate_id"]: row for row in gate_results}
        passed_dir = output_dir / "passed_proofs"
        passed_dir.mkdir(parents=True, exist_ok=True)
        passed: list[dict[str, Any]] = []
        for candidate in candidates:
            candidate_id = str(candidate["candidate_id"])
            gate_result = gate_by_id[candidate_id]
            if not gate_result["passed"]:
                continue
            filename = f"{safe_name(candidate_id)}.md"
            destination = passed_dir / filename
            destination.write_text(str(candidate["proof"]).rstrip() + "\n", encoding="utf-8")
            passed.append(
                {
                    "candidate_id": candidate_id,
                    "arm": candidate["arm"],
                    "family": candidate["family"],
                    "temperature": candidate["temperature"],
                    "replicate": candidate["replicate"],
                    "proof_sha256": candidate["proof_sha256"],
                    "path": str(destination.resolve()),
                }
            )
        write_json(passed_dir / "manifest.json", {"passed_proofs": passed})

        candidate_summaries = []
        for candidate in candidates:
            candidate_id = str(candidate["candidate_id"])
            candidate_summaries.append(
                {
                    "candidate_id": candidate_id,
                    "arm": candidate["arm"],
                    "family": candidate["family"],
                    "temperature": candidate["temperature"],
                    "replicate": candidate["replicate"],
                    "proof_sha256": candidate["proof_sha256"],
                    "assembly": candidate["assembly"],
                    "gate": gate_by_id[candidate_id],
                }
            )
        summary = {
            "schema": "cognitive-well-v0.3.64-modular-two-proof-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "completed_at": utc_now(),
            "problem_id": run_input["problem_id"],
            "arms": [
                {
                    "arm": row["arm"],
                    "diagnostics_exposed": row["diagnostics_exposed"],
                    "rounds": row["rounds"],
                    "fallback_triggered": row["fallback_triggered"],
                    "verified_lemma_count": len(row["verified"]),
                    "unresolved_count": len(row["unresolved"]),
                    "local_lemmas": [
                        {
                            "label": lemma["label"],
                            "source_lemma_id": lemma["source_lemma_id"],
                            "statement_sha256": sha256_text(lemma["statement"]),
                            "proof_sha256": sha256_text(lemma["proof"]),
                        }
                        for lemma in row["lemmas"]
                    ],
                    "synthesis_candidate_count": len(row["candidates"]),
                }
                for row in arm_results
            ],
            "synthesis_candidates": candidate_summaries,
            "passed_proof_count": len(passed),
            "passed_proofs": passed,
            "terra_calls": 0,
            "numeric_scoring": False,
        }
        write_json(output_dir / "summary.json", summary)
        status(
            output_dir,
            state="completed",
            stage="publish_passed_proofs",
            synthesis_candidate_count=len(candidates),
            passed_proof_count=len(passed),
        )
        return summary
    except Exception as error:
        status(
            output_dir,
            state="failed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise
