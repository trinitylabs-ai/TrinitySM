from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import threading
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.lemma_proving import (
    compact_certify,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.prompts import (
    MAXIMUM_REASONING_DIRECTIVE,
)

from .full_pipeline import child_paths
from .retry import read_json
from .run_gemma_repair_qwen_rejected_full_body_4 import (
    GEMMA_MODEL,
    QWEN_MODEL,
    REPAIR_MAX_TOKENS,
    REPAIR_TEMPERATURE,
)
from .runtime import ResilientModelRuntime, recovery_profile


QWEN_FIELDS = ("location", "witness", "verification")
FUSION_FIELDS = (
    "decisive_location",
    "failed_obligation",
    "preservable_material",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parsed_fields(path: Path, names: tuple[str, ...]) -> dict[str, str]:
    result = read_json(path)
    fields = result.get("parsed", {}).get("fields", {})
    selected = {name: str(fields.get(name, "")).strip() for name in names}
    missing = [name for name, value in selected.items() if not value]
    if missing:
        raise RuntimeError(f"missing fields {missing} in {path}")
    return selected


def one_result_path(root: Path, candidate_id: str) -> Path:
    matches = sorted(root.glob(f"**/p5/{candidate_id}/result.json"))
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one result for {candidate_id} below {root}, got {len(matches)}"
        )
    return matches[0]


def enriched_resolver_prompt(
    *,
    problem: str,
    submitted_proof: str,
    qwen_feedback: dict[str, str],
    fusion_feedback: dict[str, str],
) -> str:
    feedback = {
        "qwen_defect_packet": qwen_feedback,
        "fusion_defect_packet": fusion_feedback,
    }
    return f"""You are the Dialectic Solver resolving one difficult olympiad proof. Thinking mode is on.
{MAXIMUM_REASONING_DIRECTIVE}

Use an internal council with these roles: a Classicist using established theorems,
a Visionary proposing alternate routes, an Experimenter testing edge cases, Momus
attacking the strategy, Veritas checking every deductive step, and a Chief Architect
controlling the process. Run at most three internal rounds: diagnose, attempt repair,
then adversarially verify the repaired argument. If the identified route cannot be
completed rigorously, switch strategy rather than restating the disputed step.

The two feedback packets are non-authoritative and must initially be treated as
independent reports. First anchor each packet to its own stated location in the exact
submitted proof. Determine whether they identify the same defect or two distinct
defects; do not merge fields across packets merely because their wording is related.
If they are the same defect, use the reports as complementary evidence. If they are
distinct, repair both independently. Use Qwen's witness and verification to reproduce
its failure. Discharge Fusion's failed_obligation at Fusion's decisive_location. Retain
Fusion's preservable_material only after independently checking it, and discard or
reprove anything invalidated by either repair.

Write a complete replacement proof from the beginning. It must be self-contained and
prove the exact original problem, including exhaustive cases and the converse when
required. Integrate every necessary lemma proof directly. Do not mention reviewers,
feedback, stored lemmas, candidate proofs, or this workflow. Recheck quantifiers,
inequality directions, iteration domains, limiting arguments, and boundary or mixed
cases. If no rigorous completion is found, state the strongest rigorous partial result
and the first remaining mathematical gap instead of bluffing.

Return only the replacement proof.

ORIGINAL PROBLEM:
{problem}

EXACT PROOF TO RESOLVE:
{submitted_proof}

ENRICHED FEEDBACK PACKET:
{json.dumps(feedback, ensure_ascii=False, indent=2)}

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort on this problem. Use the maximum reasoning effort available before
producing the final response. Do not finalize merely because a plausible answer or
familiar pattern has been found.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve the two Fusion-rejected proofs with exact Qwen and Fusion fields"
        )
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8020/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--master-seed", type=int, default=20260825)
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument(
        "--output-name", default="dual_packet_high_stakes_resolver_2"
    )
    args = parser.parse_args()

    root_dir: Path = args.run_dir
    leaf_dir = child_paths(root_dir)["leaf"]
    run_input = read_json(leaf_dir.parent.parent / "selected_pair_input.json")
    problem = str(run_input["problem"])

    review_root = root_dir / "three_review_fusion_recheck_repaired_4"
    review_summary_path = review_root / "summary.json"
    review_summary = read_json(review_summary_path)
    selected = [
        row
        for row in review_summary["candidates"]
        if row["fusion_outcome"] == "REPAIR_NEEDED"
    ]
    if len(selected) != 2:
        raise RuntimeError(
            f"expected exactly two Fusion REPAIR_NEEDED proofs, got {len(selected)}"
        )

    output_dir = root_dir / args.output_name
    output_dir.mkdir(parents=True, exist_ok=True)
    status_path = root_dir / f"{args.output_name}_status.json"

    gemma_runtime = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=args.gemma_endpoint.rstrip("/"),
            qwen_endpoint=args.qwen_endpoint.rstrip("/"),
            gemma_model=GEMMA_MODEL,
            qwen_model=QWEN_MODEL,
            master_seed=args.master_seed,
        )
    )
    qwen_runtime = ResilientModelRuntime(
        RuntimeConfig(
            gemma_endpoint=args.qwen_endpoint.rstrip("/"),
            qwen_endpoint=args.qwen_endpoint.rstrip("/"),
            gemma_model=QWEN_MODEL,
            qwen_model=QWEN_MODEL,
            master_seed=args.master_seed,
        )
    )

    write_json(
        output_dir / "manifest.json",
        {
            "schema": "cognitive-well-v079-dual-packet-high-stakes-resolver-2-manifest-v2",
            "created_at": utc_now(),
            "source_review_summary": str(review_summary_path.resolve()),
            "source_filter": "fusion_REPAIR_NEEDED_only",
            "candidate_count": len(selected),
            "generator": {
                "model": GEMMA_MODEL,
                "endpoint": args.gemma_endpoint.rstrip("/"),
                "server_precision": "BF16",
                "server_mtp": 4,
                "reasoning_effort": "max",
                "temperature": REPAIR_TEMPERATURE,
                "max_tokens": REPAIR_MAX_TOKENS,
                "samples_per_source": 1,
                "output_contract": "complete_replacement_proof",
                "dialectic_round_cap": 3,
            },
            "feedback_payload": {
                "qwen": list(QWEN_FIELDS),
                "fusion": list(FUSION_FIELDS),
                "packet_relation_policy": (
                    "anchor_separately_then_classify_same_or_distinct_and_repair_all"
                ),
            },
            "intentionally_excluded": [
                "qwen_prior_verdict",
                "qwen_minimum_requirement",
                "fusion_resolver_brief",
                "reference_solution",
                "codex_grades",
            ],
            "source_proof_alignment": "sha256_checked_against_three_review_summary",
            "problem_specific_prompt_logic": False,
            "reaudit": {
                "model": QWEN_MODEL,
                "gate": "v0.3.64_qwen_compact_certify",
                "reference_solution_visible": False,
                "resolver_prompt_visible": False,
            },
        },
    )

    lock = threading.Lock()
    resolved_count = 0
    reaudit_count = 0

    def status(stage: str) -> None:
        write_json(
            status_path,
            {
                "state": "running",
                "stage": stage,
                "candidate_count": len(selected),
                "resolved_count": resolved_count,
                "reaudit_count": reaudit_count,
                "updated_at": utc_now(),
            },
        )

    status("enriched_high_stakes_resolution")

    def resolve_one(source: dict[str, Any]) -> dict[str, Any]:
        nonlocal resolved_count
        candidate_id = str(source["candidate_id"])
        proof_path = Path(str(source["proof_path"]))
        proof = proof_path.read_text(encoding="utf-8").strip()
        proof_sha256 = sha256_text(proof)
        expected_sha256 = str(source["proof_sha256"])
        if proof_sha256 != expected_sha256:
            raise RuntimeError(
                f"source proof hash mismatch for {candidate_id}: "
                f"{proof_sha256} != {expected_sha256}"
            )

        qwen_path = one_result_path(review_root / "reviewer_2", candidate_id)
        fusion_path = one_result_path(review_root / "fusion_stage", candidate_id)
        qwen_feedback = parsed_fields(qwen_path, QWEN_FIELDS)
        fusion_feedback = parsed_fields(fusion_path, FUSION_FIELDS)

        destination = output_dir / "candidates" / candidate_id
        packet = {
            "candidate_id": candidate_id,
            "source_proof_path": str(proof_path.resolve()),
            "source_proof_sha256": expected_sha256,
            "qwen_result_path": str(qwen_path.resolve()),
            "fusion_result_path": str(fusion_path.resolve()),
            "qwen": qwen_feedback,
            "fusion": fusion_feedback,
        }
        destination.mkdir(parents=True, exist_ok=True)
        write_json(destination / "enriched_feedback_packet.json", packet)
        prompt = enriched_resolver_prompt(
            problem=problem,
            submitted_proof=proof,
            qwen_feedback=qwen_feedback,
            fusion_feedback=fusion_feedback,
        )
        (destination / "resolver_prompt.txt").write_text(prompt, encoding="utf-8")
        seed_label = f"enriched_high_stakes_resolver:{candidate_id}"
        generated = gemma_runtime.text(
            role="gemma",
            prompt=prompt,
            destination=destination / "generation",
            stage="enriched_high_stakes_resolution",
            temperature=REPAIR_TEMPERATURE,
            max_tokens=REPAIR_MAX_TOKENS,
            seed_label=seed_label,
        )
        resolved_proof = str(generated["text"]).strip()
        if not resolved_proof:
            raise RuntimeError(f"empty resolver output for {candidate_id}")
        resolved_path = destination / "resolved_proof.md"
        resolved_path.write_text(resolved_proof + "\n", encoding="utf-8")
        result = {
            **packet,
            "temperature": REPAIR_TEMPERATURE,
            "seed_label": seed_label,
            "generation": generated["metadata"],
            "resolved_proof_path": str(resolved_path.resolve()),
        }
        write_json(destination / "resolution_result.json", result)
        with lock:
            resolved_count += 1
            status("enriched_high_stakes_resolution")
        return {**result, "proof": resolved_proof}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        resolutions = list(executor.map(resolve_one, selected))

    status("qwen_reaudit")

    def audit_one(resolution: dict[str, Any]) -> dict[str, Any]:
        nonlocal reaudit_count
        candidate_id = str(resolution["candidate_id"])
        audit = compact_certify(
            runtime=qwen_runtime,
            problem=problem,
            claim=problem,
            proof=str(resolution["proof"]),
            output_dir=output_dir / "candidates" / candidate_id / "qwen_reaudit",
            stage_prefix="enriched_resolved_proof",
            seed_label=f"qwen_reaudit_enriched_resolver:{candidate_id}",
        )
        result = {
            key: resolution[key]
            for key in (
                "candidate_id",
                "source_proof_path",
                "source_proof_sha256",
                "qwen_result_path",
                "fusion_result_path",
                "qwen",
                "fusion",
                "temperature",
                "seed_label",
                "generation",
                "resolved_proof_path",
            )
        } | {
            "qwen_reaudit": {
                "verdict": audit["verdict"],
                "exact_claim_reached": audit["exact_claim_reached"],
                "certified": audit["certified"],
                "certification_source": audit["certification_source"],
                "diagnostic": audit["diagnostic"],
                "diagnostic_error": audit["diagnostic_error"],
                "certification_attempts": audit["certification_attempts"],
            },
        }
        write_json(
            output_dir / "candidates" / candidate_id / "qwen_reaudit_result.json",
            result,
        )
        with lock:
            reaudit_count += 1
            status("qwen_reaudit")
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        results = list(executor.map(audit_one, resolutions))

    verdict_counts: dict[str, int] = {}
    for result in results:
        verdict = str(result["qwen_reaudit"]["verdict"])
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    summary = {
        "schema": "cognitive-well-v079-dual-packet-high-stakes-resolver-2-summary-v2",
        "state": "completed",
        "completed_at": utc_now(),
        "candidate_count": len(results),
        "qwen_reaudit_verdict_counts": verdict_counts,
        "qwen_reaudit_certified_count": sum(
            bool(row["qwen_reaudit"]["certified"]) for row in results
        ),
        "results": results,
        "gemma_recovery_profile": recovery_profile(),
        "gemma_recovery_events": gemma_runtime.recovery_events(),
        "qwen_recovery_events": qwen_runtime.recovery_events(),
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        status_path,
        {
            "state": "completed",
            "stage": "complete",
            "candidate_count": len(results),
            "resolved_count": len(results),
            "reaudit_count": len(results),
            "qwen_reaudit_verdict_counts": verdict_counts,
            "qwen_reaudit_certified_count": summary["qwen_reaudit_certified_count"],
            "updated_at": utc_now(),
        },
    )


if __name__ == "__main__":
    main()
