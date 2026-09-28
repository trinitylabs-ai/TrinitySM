from __future__ import annotations

import argparse
import concurrent.futures
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
from .runtime import ResilientModelRuntime, recovery_profile


GEMMA_MODEL = "google/gemma-4-31B-it"
QWEN_MODEL = "Qwen/Qwen3.6-27B"
REPAIR_TEMPERATURE = 0.4
REPAIR_MAX_TOKENS = 32_768


def repair_prompt(
    *, problem: str, submitted_proof: str, diagnostic: dict[str, Any]
) -> str:
    return f"""You are an expert olympiad mathematician repairing one submitted proof.
{MAXIMUM_REASONING_DIRECTIVE}

The verifier report below is non-authoritative but identifies a suspected earliest
load-bearing failure and missing obligations. Check it carefully against the proof.
Repair every validly identified issue, then independently audit the rest of the proof
for downstream gaps exposed by the repair. Do not preserve an argument merely because
it appeared in the submission.

Write a complete replacement proof from the beginning. It must be self-contained and
prove the exact original problem, including exhaustive cases and the converse when
required. Integrate every necessary lemma proof directly; do not cite appendix labels,
stored lemmas, candidate proofs, diagnostics, verification, or this workflow. Recheck
quantifiers, inequality directions, iteration domains, limiting arguments, and boundary
or mixed cases. If a rigorous completion cannot be found, explicitly state the first
remaining mathematical gap instead of bluffing.

Return only the replacement proof.

ORIGINAL PROBLEM:
{problem}

SUBMITTED PROOF TO REPLACE:
{submitted_proof}

QWEN VERIFIER REPORT:
{json.dumps(diagnostic, ensure_ascii=False, indent=2)}

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort on this problem. Use the maximum reasoning effort available before
producing the final response. Do not finalize merely because a plausible answer or
familiar pattern has been found.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repair the four Qwen-rejected full-body proofs with Gemma4-31B"
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8020/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--master-seed", type=int, default=20260825)
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()

    root_dir: Path = args.run_dir
    leaf_dir = child_paths(root_dir)["leaf"]
    run_input = read_json(leaf_dir.parent.parent / "selected_pair_input.json")
    problem = str(run_input["problem"])
    audit_path = root_dir / "qwen_terminal_audit_full_body_12_summary.json"
    audit_summary = read_json(audit_path)
    rejected = [row for row in audit_summary["results"] if row["verdict"] == "FAIL"]
    if len(rejected) != 4:
        raise RuntimeError(f"expected exactly four Qwen-rejected proofs, got {len(rejected)}")

    output_dir = root_dir / "gemma_repair_qwen_rejected_full_body_4"
    output_dir.mkdir(parents=True, exist_ok=True)
    status_path = root_dir / "gemma_repair_qwen_rejected_full_body_4_status.json"
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
            "schema": "cognitive-well-v079-gemma-qwen-guided-full-body-repair-4-manifest-v1",
            "created_at": utc_now(),
            "source_qwen_audit": str(audit_path.resolve()),
            "source_candidate_count": len(rejected),
            "source_filter": "qwen_verdict_FAIL_only",
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
            },
            "feedback_payload": [
                "earliest_break",
                "missing_obligations",
                "summary",
            ],
            "reaudit": {
                "model": QWEN_MODEL,
                "gate": "v0.3.64_qwen_compact_certify",
                "reference_solution_visible": False,
                "prior_verdict_visible": False,
                "repair_prompt_visible": False,
            },
            "reference_solution_visible_to_generator": False,
            "codex_grades_visible_to_generator": False,
            "problem_specific_prompt_logic": False,
        },
    )
    lock = threading.Lock()
    repair_completed = 0
    reaudit_completed = 0

    def status(stage: str) -> None:
        write_json(
            status_path,
            {
                "state": "running",
                "stage": stage,
                "candidate_count": len(rejected),
                "repair_completed_count": repair_completed,
                "reaudit_completed_count": reaudit_completed,
                "updated_at": utc_now(),
            },
        )

    status("gemma_repair")

    def repair_one(source: dict[str, Any]) -> dict[str, Any]:
        nonlocal repair_completed
        candidate_id = str(source["candidate_id"])
        destination = output_dir / "candidates" / candidate_id
        submitted_proof = Path(str(source["source_path"])).read_text(
            encoding="utf-8"
        ).strip()
        generated = gemma_runtime.text(
            role="gemma",
            prompt=repair_prompt(
                problem=problem,
                submitted_proof=submitted_proof,
                diagnostic=dict(source["diagnostic"]),
            ),
            destination=destination,
            stage="gemma_repair",
            temperature=REPAIR_TEMPERATURE,
            max_tokens=REPAIR_MAX_TOKENS,
            seed_label=f"qwen_guided_full_body_repair:{candidate_id}",
        )
        proof = str(generated["text"]).strip()
        if not proof:
            raise RuntimeError(f"empty Gemma repair for {candidate_id}")
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "repaired_proof.md").write_text(proof + "\n", encoding="utf-8")
        result = {
            "candidate_id": candidate_id,
            "source_path": source["source_path"],
            "source_proof_sha256": source["proof_sha256"],
            "source_qwen_diagnostic": source["diagnostic"],
            "temperature": REPAIR_TEMPERATURE,
            "seed_label": f"qwen_guided_full_body_repair:{candidate_id}",
            "generation": generated["metadata"],
            "repaired_proof_path": str((destination / "repaired_proof.md").resolve()),
        }
        write_json(destination / "repair_result.json", result)
        with lock:
            repair_completed += 1
            status("gemma_repair")
        return {**result, "proof": proof}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        repairs = list(executor.map(repair_one, rejected))

    status("qwen_reaudit")

    def reaudit_one(repair: dict[str, Any]) -> dict[str, Any]:
        nonlocal reaudit_completed
        candidate_id = str(repair["candidate_id"])
        audit = compact_certify(
            runtime=qwen_runtime,
            problem=problem,
            claim=problem,
            proof=str(repair["proof"]),
            output_dir=output_dir / "candidates" / candidate_id / "qwen_reaudit",
            stage_prefix="repaired_proof",
            seed_label=f"qwen_reaudit_repaired_full_body:{candidate_id}",
        )
        result = {
            key: repair[key]
            for key in (
                "candidate_id",
                "source_path",
                "source_proof_sha256",
                "source_qwen_diagnostic",
                "temperature",
                "seed_label",
                "generation",
                "repaired_proof_path",
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
            reaudit_completed += 1
            status("qwen_reaudit")
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        results = list(executor.map(reaudit_one, repairs))

    verdict_counts: dict[str, int] = {}
    for result in results:
        verdict = str(result["qwen_reaudit"]["verdict"])
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    summary = {
        "schema": "cognitive-well-v079-gemma-qwen-guided-full-body-repair-4-summary-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "candidate_count": len(results),
        "repair_model": GEMMA_MODEL,
        "repair_temperature": REPAIR_TEMPERATURE,
        "repair_reasoning_effort": "max",
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
            "repair_completed_count": len(results),
            "reaudit_completed_count": len(results),
            "qwen_reaudit_verdict_counts": verdict_counts,
            "qwen_reaudit_certified_count": summary["qwen_reaudit_certified_count"],
            "updated_at": utc_now(),
        },
    )


if __name__ == "__main__":
    main()
