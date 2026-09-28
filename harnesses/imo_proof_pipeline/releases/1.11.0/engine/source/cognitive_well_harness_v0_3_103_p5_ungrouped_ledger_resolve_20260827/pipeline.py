from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import utc_now
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import pipeline as v084
from cognitive_well_harness_v0_3_99_semantic_obligation_grouping_20260827 import pipeline as v099
from cognitive_well_harness_v0_3_100_current_semantic_ledger_20260827 import pipeline as v100
from cognitive_well_harness_v0_3_101_shared_problem_ledger_resolve_20260827.pipeline import RESOLVER_SYSTEM_PROMPT

from . import GEMMA_MODEL, HARNESS_VERSION


DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
TEMPERATURE = 0.4
MAX_TOKENS = 32_768


def load_cases(source_run: Path, problem_id: str) -> list[dict[str, Any]]:
    source_run = source_run.resolve()
    manifest = v099.load_json(source_run / "manifest.json")
    summary = v099.load_json(source_run / "summary.json")
    if summary.get("state") != "completed" or not str(manifest.get("schema") or "").startswith("cognitive-well-v0100-"):
        raise ValueError("v0.3.103 requires a completed v0.3.100 run")
    upstream_cases = v099.load_source_cases(Path(str(manifest["source_run"])))
    cases: list[dict[str, Any]] = []
    for case in upstream_cases:
        if case["problem_id"] != problem_id:
            continue
        active, archived = v100.split_source_entries(case["entries"])
        if not active:
            raise ValueError(f"{case['case_id']} has no active obligations")
        cases.append(case | {"active_entries": active, "archived_entries": archived})
    if not cases:
        raise ValueError(f"no cases found for {problem_id}")
    return cases


def ungrouped_packet(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packets = v100.current_entry_packet(entries)
    if len(packets) != len(entries):
        raise AssertionError("ungrouped packet changed cardinality")
    return packets


def resolver_user_prompt(case: dict[str, Any]) -> str:
    return (
        "# ORIGINAL PROBLEM\n\n"
        + case["problem"].strip()
        + "\n\n# SUBMITTED PROOF TO REPLACE\n\n"
        + case["proof"].strip()
        + "\n\n# MANDATORY UNGROUPED CURRENT-PROOF OBLIGATIONS\n\n"
        + json.dumps(ungrouped_packet(case["active_entries"]), ensure_ascii=False, indent=2)
        + "\n\n# OPTIONAL CROSS-PROOF WARNINGS OR ALTERNATIVE ROUTES\n\n[]"
        + "\n\nEvery mandatory record is a distinct preserved audit report. Independently verify it; do not collapse or ignore a record merely because another report is related. Write the complete replacement proof now.\n"
    )


def run_case(*, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    if result_path.is_file():
        return v099.load_json(result_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt = resolver_user_prompt(case)
    identity = v099.sha256_text(RESOLVER_SYSTEM_PROMPT + prompt)[:12]
    label = f"{seed_namespace}:{case['case_id']}:ungrouped_resolve:{identity}"
    runtime = v084.runtime_for(endpoint, v099.stable_seed(label), GEMMA_MODEL)
    generated = runtime.text(
        role="gemma",
        prompt=RESOLVER_SYSTEM_PROMPT,
        user_prompt=prompt,
        destination=output_dir / "generation",
        stage=f"ungrouped_current_ledger_complete_proof_resolve_{identity}",
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        seed_label=label,
    )
    proof = str(generated["text"]).strip()
    if not proof:
        raise ValueError(f"empty resolver output for {case['case_id']}")
    proof_path = output_dir / "resolved_proof.md"
    proof_path.write_text(proof + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v0103-ungrouped-ledger-resolve-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "case_id": case["case_id"],
        "problem_id": case["problem_id"],
        "candidate_id": case["candidate_id"],
        "source_proof_path": case["proof_path"],
        "source_proof_sha256": case["proof_sha256"],
        "mandatory_ungrouped_obligation_count": len(case["active_entries"]),
        "archived_obligation_count": len(case["archived_entries"]),
        "resolved_proof_path": str(proof_path.resolve()),
        "resolved_proof_sha256": v099.sha256_text(proof),
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def run(*, source_run: Path, output_dir: Path, problem_id: str, gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT, workers: int = 2, seed_namespace: str = "v0103", dry_run: bool = False) -> dict[str, Any]:
    if workers < 1:
        raise ValueError("workers must be positive")
    source_run = source_run.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases(source_run, problem_id)
    manifest = {
        "schema": "cognitive-well-v0103-ungrouped-ledger-resolve-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_run": str(source_run),
        "source_manifest_sha256": v099.file_sha256(source_run / "manifest.json"),
        "problem_id": problem_id,
        "model": GEMMA_MODEL,
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "workers": workers,
            "precision": "BF16",
            "mtp": 4,
            "reasoning_effort": "max",
        },
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "protocol": {
            "semantic_grouping": False,
            "shared_problem_bank": False,
            "cross_proof_optional_groups": False,
            "active_records_preserved_individually": True,
            "closed_and_unsupported_excluded": True,
            "resolver_system_prompt_identical_to_v0.3.101": True,
            "problem_specific_prompting": False,
            "post_resolver_audit": False,
        },
        "resolver_system_prompt_sha256": v099.sha256_text(RESOLVER_SYSTEM_PROMPT),
        "case_count": len(cases),
        "cases": [
            {
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "active_ungrouped_obligation_count": len(case["active_entries"]),
                "archived_obligation_count": len(case["archived_entries"]),
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    if dry_run:
        summary = {
            "schema": "cognitive-well-v0103-dry-run-v1",
            "state": "dry_run_completed",
            "problem_id": problem_id,
            "case_count": len(cases),
            "active_ungrouped_obligation_count": sum(len(case["active_entries"]) for case in cases),
            "per_candidate_counts": {case["candidate_id"]: len(case["active_entries"]) for case in cases},
            "planned_gemma_calls": len(cases),
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        return summary
    write_json(output_dir / "status.json", {"state": "running", "stage": "gemma_ungrouped_ledger_resolve_batch", "updated_at": utc_now()})
    jobs = [{"case_id": case["case_id"], "case": case} for case in cases]

    def task(job: dict[str, Any]) -> None:
        case = job["case"]
        case["resolve"] = run_case(
            case=case,
            endpoint=gemma_endpoint,
            output_dir=output_dir / "cases" / case["case_id"] / "gemma_ungrouped_ledger_resolve",
            seed_namespace=seed_namespace,
        )

    v099.run_parallel(name="ungrouped-resolve", jobs=jobs, workers=workers, task=task)
    rows = [
        {
            "case_id": case["case_id"],
            "problem_id": case["problem_id"],
            "candidate_id": case["candidate_id"],
            "mandatory_ungrouped_obligation_count": case["resolve"]["mandatory_ungrouped_obligation_count"],
            "resolved_proof_path": case["resolve"]["resolved_proof_path"],
            "resolved_proof_sha256": case["resolve"]["resolved_proof_sha256"],
        }
        for case in cases
    ]
    summary = {
        "schema": "cognitive-well-v0103-ungrouped-ledger-resolve-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "problem_id": problem_id,
        "candidate_count": len(cases),
        "active_ungrouped_obligation_count": sum(row["mandatory_ungrouped_obligation_count"] for row in rows),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "status.json", {"state": "completed", "stage": "done", "updated_at": utc_now()})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="P5 ungrouped current-ledger resolver ablation")
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--problem-id", required=True)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--seed-namespace", default="v0103")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(source_run=args.source_run, output_dir=args.output_dir, problem_id=args.problem_id, gemma_endpoint=args.gemma_endpoint, workers=args.workers, seed_namespace=args.seed_namespace, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
