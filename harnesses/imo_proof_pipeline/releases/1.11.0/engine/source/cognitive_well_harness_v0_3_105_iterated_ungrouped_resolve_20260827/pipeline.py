from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_89_conditional_gap_selector_20260827.pipeline import (
    run_gap_selector,
)
from cognitive_well_harness_v0_3_96_generic_enhanced_review_fusion_resolver_20260827.generic_adapters import (
    reviewer_1_failure_record,
)
from cognitive_well_harness_v0_3_98_batched_post_resolver_gate_20260827 import run as v098
from cognitive_well_harness_v0_3_99_semantic_obligation_grouping_20260827 import pipeline as v099
from cognitive_well_harness_v0_3_100_current_semantic_ledger_20260827 import pipeline as v100
from cognitive_well_harness_v0_3_103_p5_ungrouped_ledger_resolve_20260827 import pipeline as v103

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
ACTIVE_STATUSES = {"OPEN", "UNCLOSED"}
ARCHIVE_STATUSES = {"CLOSED", "UNSUPPORTED"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_within(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes the single-problem source root: {path}") from error
    return path


def problem_number(problem_id: str) -> int:
    match = re.search(r"(?:^|[_-])p([0-9]+)$", problem_id, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def result_reasoning(
    result: dict[str, Any], *, allowed_root: Path
) -> tuple[str, str]:
    metadata = result.get("generation") or {}
    path = require_within(
        allowed_root,
        Path(str(metadata.get("reasoning_path") or "")),
        "resolver reasoning",
    )
    if not path.is_file():
        raise ValueError(f"resolver reasoning is unavailable: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"resolver reasoning is empty: {path}")
    return text, str(path)


def load_cases(
    *, resolve_runs: list[Path], prior_gate_run: Path, source_root: Path | None = None
) -> list[dict[str, Any]]:
    prior_gate_run = prior_gate_run.resolve()
    problem_root = (source_root if source_root is not None else prior_gate_run.parent).resolve()
    require_within(problem_root, prior_gate_run, "prior gate run")
    gate_manifest = load_json(prior_gate_run / "manifest.json")
    gate_specs = {
        str(row["case_id"]): row for row in gate_manifest.get("cases") or []
    }
    cases: list[dict[str, Any]] = []
    for resolve_run in resolve_runs:
        resolve_run = require_within(
            problem_root, resolve_run, "resolve run"
        )
        manifest = load_json(resolve_run / "manifest.json")
        summary = load_json(resolve_run / "summary.json")
        if summary.get("state") != "completed":
            raise ValueError(f"resolve run is incomplete: {resolve_run}")
        if not str(manifest.get("schema") or "").startswith(
            "cognitive-well-v0103-ungrouped-ledger-resolve"
        ):
            raise ValueError(f"not a v0.3.103 ungrouped resolve run: {resolve_run}")
        for source in manifest.get("cases") or []:
            case_id = str(source["case_id"])
            gate_spec = gate_specs.get(case_id)
            if gate_spec is None:
                raise ValueError(f"prior gate has no case {case_id}")
            result_path = (
                resolve_run
                / "cases"
                / case_id
                / "gemma_ungrouped_ledger_resolve"
                / "result.json"
            ).resolve()
            result = load_json(result_path)
            proof_path = require_within(
                resolve_run,
                Path(str(result["resolved_proof_path"])),
                f"case {case_id} resolved proof",
            )
            proof = proof_path.read_text(encoding="utf-8").strip()
            proof_sha256 = v099.sha256_text(proof)
            if proof_sha256 != str(result["resolved_proof_sha256"]):
                raise ValueError(f"resolved proof hash mismatch: {case_id}")
            passthrough = str(result.get("state") or "") == "skipped_no_active_obligations"
            if passthrough:
                if int(result.get("mandatory_ungrouped_obligation_count", -1)) != 0:
                    raise ValueError(f"invalid no-active passthrough: {case_id}")
                reasoning, reasoning_path = "", None
            else:
                reasoning, reasoning_path = result_reasoning(
                    result, allowed_root=resolve_run
                )

            problem_path = require_within(
                problem_root,
                Path(str(gate_spec["problem_path"])),
                f"case {case_id} problem",
            )
            problem_payload = load_json(problem_path)
            problem = str(
                problem_payload.get("claim") or problem_payload.get("problem") or ""
            ).strip()
            if not problem:
                raise ValueError(f"empty problem: {problem_path}")
            if gate_spec.get("problem_sha256") != v099.sha256_text(problem):
                raise ValueError(f"source problem hash mismatch: {case_id}")

            ledger_path = (
                prior_gate_run.resolve()
                / "cases"
                / case_id
                / "updated_obligation_ledger.json"
            ).resolve()
            prior_ledger = load_json(ledger_path)
            entries = [dict(row) for row in prior_ledger.get("entries") or []]
            active = [
                dict(row)
                for row in entries
                if str(row.get("status") or "").upper() in ACTIVE_STATUSES
            ]
            archived = [
                dict(row)
                for row in entries
                if str(row.get("status") or "").upper() in ARCHIVE_STATUSES
            ]
            if len(active) + len(archived) != len(entries):
                raise ValueError(f"unknown prior-ledger status in {case_id}")
            cases.append(
                {
                    "case_id": case_id,
                    "gate_index": len(cases),
                    "proof_index": len(cases),
                    "problem_number": problem_number(str(source["problem_id"])),
                    "problem_id": str(source["problem_id"]),
                    "candidate_id": str(source["candidate_id"]),
                    "problem_path": str(problem_path),
                    "problem": problem,
                    "problem_sha256": v099.sha256_text(problem),
                    "proof_path": str(proof_path),
                    "proof": proof,
                    "proof_sha256": proof_sha256,
                    "resolver_outcome": "SECOND_RESOLVE_COMPLETED",
                    "resolver_result_path": str(result_path),
                    "resolver_result_sha256": v099.file_sha256(result_path),
                    "resolver_final": proof,
                    "resolver_reasoning": reasoning,
                    "resolver_reasoning_sha256": v099.sha256_text(reasoning),
                    "source_trace_handoff": reasoning_path,
                    "second_resolve_skipped_no_active_obligations": passthrough,
                    "source_fusion_result": None,
                    "obligations": active,
                    "prior_ledger": prior_ledger,
                    "prior_ledger_path": str(ledger_path),
                    "prior_entries": entries,
                    "prior_archived_entries": archived,
                    "source_resolve_run": str(resolve_run),
                }
            )
    identifiers = [row["case_id"] for row in cases]
    if not cases or len(identifiers) != len(set(identifiers)):
        raise ValueError("resolve runs must provide nonempty unique cases")
    return cases


def next_obligation_number(entries: list[dict[str, Any]]) -> int:
    numbers = []
    for entry in entries:
        match = re.fullmatch(r"OB([0-9]+)", str(entry.get("obligation_id") or ""))
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def build_iterated_ledger(case: dict[str, Any]) -> dict[str, Any]:
    decisions = {
        str(row["obligation_id"]): row
        for row in case["closure_result"].get("decisions") or []
    }
    entries = [dict(row) for row in case["prior_entries"]]
    by_id = {str(row["obligation_id"]): row for row in entries}
    by_digest = {str(row.get("sha256") or ""): row for row in entries}

    for obligation in case["obligations"]:
        obligation_id = str(obligation["obligation_id"])
        decision = decisions[obligation_id]
        entry = by_id[obligation_id]
        entry["status"] = str(decision["label"])
        entry["proof_location"] = str(decision["proof_location"])
        entry["status_reason"] = str(decision["reason"])
        history = list(entry.get("cycle_history") or [])
        history.append(
            {
                "cycle": 2,
                "input_proof_sha256": case["proof_sha256"],
                "status": str(decision["label"]),
                "proof_location": str(decision["proof_location"]),
                "reason": str(decision["reason"]),
            }
        )
        entry["cycle_history"] = history

    next_number = next_obligation_number(entries)
    for obligation in v098.post_resolver_obligations(case):
        existing = by_digest.get(str(obligation["sha256"]))
        if existing is not None:
            existing["status"] = "OPEN"
            sources = list(existing.get("post_resolver_sources") or [])
            if obligation["source"] not in sources:
                sources.append(obligation["source"])
            existing["post_resolver_sources"] = sources
            existing["status_reason"] = (
                "The same concrete defect was independently detected after the "
                "second resolution."
            )
            continue
        entry = {
            **obligation,
            "obligation_id": f"OB{next_number}",
            "phase": "post_second_resolver",
            "status": "OPEN",
            "proof_location": "(reported by post-second-Resolver audit)",
            "status_reason": obligation["defect"],
            "post_resolver_sources": [obligation["source"]],
            "cycle_history": [
                {
                    "cycle": 2,
                    "input_proof_sha256": case["proof_sha256"],
                    "status": "OPEN",
                    "reason": obligation["defect"],
                }
            ],
        }
        next_number += 1
        entries.append(entry)
        by_id[str(entry["obligation_id"])] = entry
        by_digest[str(entry["sha256"])] = entry

    active = [
        row
        for row in entries
        if str(row.get("status") or "").upper() in ACTIVE_STATUSES
    ]
    archived = [
        row
        for row in entries
        if str(row.get("status") or "").upper() in ARCHIVE_STATUSES
    ]
    if len(active) + len(archived) != len(entries):
        raise AssertionError("iterated ledger lost status coverage")
    return {
        "schema": "cognitive-well-v0105-iterated-obligation-ledger-v1",
        "case_id": case["case_id"],
        "cycle": 2,
        "proof_sha256": case["proof_sha256"],
        "prior_ledger_path": case["prior_ledger_path"],
        "prior_entry_count": len(case["prior_entries"]),
        "entry_count": len(entries),
        "active_count": len(active),
        "archived_count": len(archived),
        "semantic_grouping": False,
        "shared_problem_bank": False,
        "entries": entries,
        "active_obligations": active,
    }


def empty_closure(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v0105-empty-obligation-closure-v1",
        "state": "completed",
        "obligation_count": 0,
        "closed_count": 0,
        "unclosed_count": 0,
        "unsupported_count": 0,
        "decisions": [],
        "summary": "No inherited active obligations required rechecking.",
    }


def promote_unchanged_no_second_cycle(
    *, case: dict[str, Any], output_dir: Path
) -> None:
    """Promote a no-active-obligation proof without redundant re-auditing."""
    if not case.get("second_resolve_skipped_no_active_obligations"):
        raise ValueError(f"case is not an authorized passthrough: {case['case_id']}")
    if case.get("obligations"):
        raise ValueError(f"passthrough case has active obligations: {case['case_id']}")
    source_path = Path(str(case["proof_path"])).resolve()
    proof = source_path.read_text(encoding="utf-8").strip()
    if v099.sha256_text(proof) != str(case["proof_sha256"]):
        raise ValueError(f"passthrough proof hash drift: {case['case_id']}")
    lane = output_dir / "cases" / case["case_id"] / "promoted_unchanged"
    lane.mkdir(parents=True, exist_ok=True)
    proof_path = lane / "third_proof.md"
    proof_path.write_bytes(source_path.read_bytes())
    if v099.sha256_text(proof_path.read_text(encoding="utf-8").strip()) != str(
        case["proof_sha256"]
    ):
        raise AssertionError(f"promotion changed proof bytes: {case['case_id']}")

    prior_ledger = dict(case["prior_ledger"])
    entries = [dict(row) for row in prior_ledger.get("entries") or []]
    if any(str(row.get("status") or "").upper() in ACTIVE_STATUSES for row in entries):
        raise ValueError(f"passthrough prior ledger became active: {case['case_id']}")
    case["closure_result"] = empty_closure(case)
    case["updated_ledger"] = {
        **prior_ledger,
        "schema": "cognitive-well-v0105-unchanged-promotion-ledger-v1",
        "cycle": "skipped_no_second_resolve",
        "proof_sha256": case["proof_sha256"],
        "entry_count": len(entries),
        "active_count": 0,
        "entries": entries,
        "active_obligations": [],
    }
    case["gate"] = {
        "outcome": "NOT_RUN_NO_SECOND_RESOLVE",
        "reasons": [],
        "terminal_proof_status": "PROMOTED_UNCHANGED_FROM_POST_RESOLVER_PASS",
    }
    case["third_resolve"] = {
        "state": "promoted_unchanged_no_second_cycle",
        "resolved_proof_path": str(proof_path.resolve()),
        "resolved_proof_sha256": case["proof_sha256"],
    }
    write_json(lane / "updated_obligation_ledger.json", case["updated_ledger"])
    write_json(
        lane / "promotion.json",
        {
            "schema": "cognitive-well-v0105-unchanged-promotion-v1",
            "state": "completed",
            "completed_at": utc_now(),
            "case_id": case["case_id"],
            "source_proof_path": str(source_path),
            "source_proof_sha256": case["proof_sha256"],
            "third_proof_path": str(proof_path.resolve()),
            "third_proof_sha256": case["proof_sha256"],
            "model_call_count": 0,
            "second_audit_cycle_run": False,
            "third_resolve_run": False,
        },
    )


def audit_cases(
    *,
    cases: list[dict[str, Any]],
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    gemma_workers: int,
    qwen_workers: int,
    seed_namespace: str,
) -> None:
    jobs = [{"job_id": case["case_id"], "case": case} for case in cases]
    resolver_trace_jobs = [
        job for job in jobs if str(job["case"].get("resolver_reasoning") or "").strip()
    ]
    for job in jobs:
        if job not in resolver_trace_jobs:
            job["case"]["resolver_trace_real_gaps"] = []

    def gpu0_branch() -> None:
        write_json(output_dir / "status.json", {"state": "running", "stage": "resolver_trace_extraction_batch", "updated_at": utc_now()})

        def trace_extract(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "resolver_trace_gate"
            case["resolver_trace_extraction"] = v098.run_resolver_trace_extractor(
                case=case,
                endpoint=gemma_endpoint,
                output_dir=lane / "01_extraction",
                seed_namespace=seed_namespace,
            )

        v098.run_parallel(name="resolver_trace_extract", jobs=resolver_trace_jobs, workers=gemma_workers, task=trace_extract)
        write_json(output_dir / "status.json", {"state": "running", "stage": "resolver_trace_selector_batch", "updated_at": utc_now()})

        def trace_select(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "resolver_trace_gate"
            packets = v098.markdown_trace_packets(case["resolver_trace_extraction"])
            selector = run_gap_selector(
                problem=case["problem"],
                proof=case["proof"],
                packets=packets,
                endpoint=gemma_endpoint,
                output_dir=lane / "02_selector",
                seed=v098.stable_seed(f"{seed_namespace}:{case['case_id']}:resolver_trace_select"),
                seed_label=f"{seed_namespace}:{case['case_id']}:resolver_trace_select",
                model=GEMMA_MODEL,
            )
            case["resolver_trace_selector"] = selector
            case["resolver_trace_real_gaps"] = v098.trace_real_gaps(
                case["resolver_trace_extraction"], selector
            )

        v098.run_parallel(name="resolver_trace_select", jobs=resolver_trace_jobs, workers=gemma_workers, task=trace_select)
        write_json(output_dir / "status.json", {"state": "running", "stage": "fresh_reviewer_1_batch", "updated_at": utc_now()})

        def reviewer1(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits" / "reviewer_1"
            label = f"{seed_namespace}:{case['case_id']}:fresh_reviewer_1"
            result = v098.run_original_reviewer(
                problem=case["problem"],
                proof=case["proof"],
                endpoint=gemma_endpoint,
                output_dir=lane,
                seed=v098.stable_seed(label),
                seed_label=label,
                model=GEMMA_MODEL,
            )
            final = (lane / "final.txt").read_text(encoding="utf-8").strip()
            parsed = v098.parse_reviewer_1(final)
            case["fresh_reviewer_1"] = {
                "result": result,
                "final": final,
                "parsed": parsed,
                "reasoning": (lane / "reasoning.txt").read_text(encoding="utf-8").strip(),
            }

        v098.run_parallel(name="fresh_reviewer_1", jobs=jobs, workers=gemma_workers, task=reviewer1)
        success_jobs = [
            job
            for job in jobs
            if job["case"]["fresh_reviewer_1"]["parsed"]["outcome"] == "NO_FIRST_BREAK"
        ]
        for job in jobs:
            case = job["case"]
            if case["fresh_reviewer_1"]["parsed"]["outcome"] == "FIRST_BREAK":
                case["fresh_reviewer_1_effective_final"] = case["fresh_reviewer_1"]["final"]
                case["fresh_reviewer_1_effective_outcome"] = "FIRST_BREAK"
                case["fresh_reviewer_1_trace_real_gaps"] = []

        def r1_extract(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits" / "reviewer_1_enhancement"
            label = f"{seed_namespace}:{case['case_id']}:fresh_r1_trace_extract"
            case["fresh_r1_extraction"] = v098.run_compact_markdown_extractor(
                problem=case["problem"],
                proof=case["proof"],
                reasoning=case["fresh_reviewer_1"]["reasoning"],
                reviewer_final=case["fresh_reviewer_1"]["final"],
                endpoint=gemma_endpoint,
                output_dir=lane / "01_extraction",
                seed=v098.stable_seed(label),
                seed_label=label,
                model=GEMMA_MODEL,
            )

        write_json(output_dir / "status.json", {"state": "running", "stage": "conditional_fresh_r1_trace_extraction_batch", "updated_at": utc_now()})
        v098.run_parallel(name="fresh_r1_trace_extract", jobs=success_jobs, workers=gemma_workers, task=r1_extract)

        def r1_select(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits" / "reviewer_1_enhancement"
            packets = v098.markdown_trace_packets(case["fresh_r1_extraction"])
            selector = run_gap_selector(
                problem=case["problem"],
                proof=case["proof"],
                packets=packets,
                endpoint=gemma_endpoint,
                output_dir=lane / "02_selector",
                seed=v098.stable_seed(f"{seed_namespace}:{case['case_id']}:fresh_r1_trace_select"),
                seed_label=f"{seed_namespace}:{case['case_id']}:fresh_r1_trace_select",
                model=GEMMA_MODEL,
            )
            gaps = v098.trace_real_gaps(case["fresh_r1_extraction"], selector)
            case["fresh_r1_selector"] = selector
            case["fresh_reviewer_1_trace_real_gaps"] = gaps
            if gaps:
                case["fresh_reviewer_1_effective_final"] = reviewer_1_failure_record(gaps[0])
                case["fresh_reviewer_1_effective_outcome"] = "FIRST_BREAK"
            else:
                case["fresh_reviewer_1_effective_final"] = case["fresh_reviewer_1"]["final"]
                case["fresh_reviewer_1_effective_outcome"] = "NO_FIRST_BREAK"

        write_json(output_dir / "status.json", {"state": "running", "stage": "conditional_fresh_r1_selector_batch", "updated_at": utc_now()})
        v098.run_parallel(name="fresh_r1_trace_select", jobs=success_jobs, workers=gemma_workers, task=r1_select)

    def gpu1_branch() -> None:
        def reviewer2(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits"
            case["fresh_reviewer_2"] = v098.fresh_reviewer_2(
                case=case,
                endpoint=qwen_endpoint,
                output_dir=lane,
                seed_namespace=seed_namespace,
            )

        v098.run_parallel(name="fresh_reviewer_2", jobs=jobs, workers=qwen_workers, task=reviewer2)

    write_json(output_dir / "status.json", {"state": "running", "stage": "split_gpu_post_second_resolver_audits", "updated_at": utc_now()})
    with concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="v105-split-gpu") as pool:
        futures = [pool.submit(gpu0_branch), pool.submit(gpu1_branch)]
        for future in futures:
            future.result()

    write_json(output_dir / "status.json", {"state": "running", "stage": "obligation_closure_batch", "updated_at": utc_now()})

    def closure(job: dict[str, Any]) -> None:
        case = job["case"]
        lane = output_dir / "cases" / case["case_id"] / "obligation_closure"
        case["closure_result"] = (
            v098.run_obligation_closure(
                case=case,
                endpoint=gemma_endpoint,
                output_dir=lane,
                seed_namespace=seed_namespace,
            )
            if case["obligations"]
            else empty_closure(case)
        )
        case["updated_ledger"] = build_iterated_ledger(case)
        write_json(
            output_dir / "cases" / case["case_id"] / "updated_obligation_ledger.json",
            case["updated_ledger"],
        )
        case["gate"] = v098.gate_decision(case)
        write_json(
            output_dir / "cases" / case["case_id"] / "gate_result.json",
            {
                "schema": "cognitive-well-v0105-post-second-resolver-gate-result-v1",
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "resolver_trace_real_gaps": case["resolver_trace_real_gaps"],
                "fresh_reviewer_1_outcome": case["fresh_reviewer_1_effective_outcome"],
                "fresh_reviewer_1_trace_real_gaps": case["fresh_reviewer_1_trace_real_gaps"],
                "fresh_reviewer_2_outcome": case["fresh_reviewer_2"]["parsed"]["outcome"],
                "obligation_closure": case["closure_result"],
                "updated_obligation_ledger": case["updated_ledger"],
                **case["gate"],
                "completed_at": utc_now(),
            },
        )

    v098.run_parallel(name="obligation_closure", jobs=jobs, workers=gemma_workers, task=closure)


def resolve_cases(
    *,
    cases: list[dict[str, Any]],
    output_dir: Path,
    gemma_endpoint: str,
    resolve_workers: int,
    seed_namespace: str,
) -> None:
    jobs = [
        {"job_id": case["case_id"], "case": case}
        for case in cases
        if case["updated_ledger"]["active_obligations"]
    ]

    def resolve(job: dict[str, Any]) -> None:
        case = job["case"]
        resolver_case = case | {
            "active_entries": case["updated_ledger"]["active_obligations"],
            "archived_entries": [
                row
                for row in case["updated_ledger"]["entries"]
                if str(row.get("status") or "").upper() in ARCHIVE_STATUSES
            ],
        }
        case["third_resolve"] = v103.run_case(
            case=resolver_case,
            endpoint=gemma_endpoint,
            output_dir=output_dir / "cases" / case["case_id"] / "third_ungrouped_resolve",
            seed_namespace=seed_namespace,
        )

    v098.run_parallel(name="third_ungrouped_resolve", jobs=jobs, workers=resolve_workers, task=resolve)
    for case in cases:
        if "third_resolve" not in case:
            case["third_resolve"] = {
                "state": "skipped_no_active_obligations",
                "resolved_proof_path": case["proof_path"],
                "resolved_proof_sha256": case["proof_sha256"],
            }


def run(
    *,
    resolve_runs: list[Path],
    prior_gate_run: Path,
    output_dir: Path,
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT,
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT,
    gemma_workers: int = 4,
    qwen_workers: int = 4,
    resolve_workers: int = 2,
    seed_namespace: str = "v0105",
    dry_run: bool = False,
    source_root: Path | None = None,
) -> dict[str, Any]:
    if min(gemma_workers, qwen_workers, resolve_workers) < 1:
        raise ValueError("worker counts must be positive")
    cases = load_cases(resolve_runs=resolve_runs, prior_gate_run=prior_gate_run, source_root=source_root)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "cognitive-well-v0105-iterated-ungrouped-resolve-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_resolve_runs": [str(path.resolve()) for path in resolve_runs],
        "prior_gate_run": str(prior_gate_run.resolve()),
        "case_count": len(cases),
        "models": {"gemma": GEMMA_MODEL, "qwen": QWEN_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "qwen_endpoint": qwen_endpoint,
            "gemma_precision": "BF16",
            "gemma_mtp": 4,
            "reasoning_effort": "max",
            "gemma_audit_workers": gemma_workers,
            "qwen_workers": qwen_workers,
            "gemma_resolve_workers": resolve_workers,
        },
        "temperatures": {
            "resolver_trace_extractor": 0.1,
            "resolver_trace_selector": 0.1,
            "fresh_reviewer_1": 0.1,
            "fresh_reviewer_1_trace_gate": 0.1,
            "fresh_reviewer_2": 0.2,
            "obligation_closure": 0.1,
            "third_resolver": v103.TEMPERATURE,
        },
        "protocol": {
            "repeat_steps": [6, 7, 8, 9],
            "prior_active_obligations_rechecked": True,
            "prior_archived_obligations_preserved": True,
            "exact_deduplication": True,
            "semantic_grouping": False,
            "shared_problem_bank": False,
            "cross_proof_transfer": False,
            "problem_specific_prompting": False,
            "no_active_passthrough_skips_second_audit_cycle": True,
        },
        "cases": [
            {
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "second_proof_path": case["proof_path"],
                "second_proof_sha256": case["proof_sha256"],
                "prior_ledger_path": case["prior_ledger_path"],
                "prior_entry_count": len(case["prior_entries"]),
                "prior_active_count": len(case["obligations"]),
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    if dry_run:
        summary = {
            "schema": "cognitive-well-v0105-dry-run-summary-v1",
            "state": "dry_run_completed",
            "case_count": len(cases),
            "problems": sorted({case["problem_id"] for case in cases}),
            "prior_active_counts": {
                case["case_id"]: len(case["obligations"]) for case in cases
            },
            "planned_third_resolves_max": len(cases),
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(output_dir / "status.json", {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()})
        return summary

    cycle_cases = [
        case
        for case in cases
        if not case.get("second_resolve_skipped_no_active_obligations")
    ]
    passthrough_cases = [
        case
        for case in cases
        if case.get("second_resolve_skipped_no_active_obligations")
    ]
    for case in passthrough_cases:
        promote_unchanged_no_second_cycle(case=case, output_dir=output_dir)

    audit_cases(
        cases=cycle_cases,
        output_dir=output_dir,
        gemma_endpoint=gemma_endpoint.rstrip("/"),
        qwen_endpoint=qwen_endpoint.rstrip("/"),
        gemma_workers=gemma_workers,
        qwen_workers=qwen_workers,
        seed_namespace=seed_namespace,
    )
    write_json(output_dir / "status.json", {"state": "running", "stage": "third_ungrouped_resolve_batch", "updated_at": utc_now()})
    resolve_cases(
        cases=cycle_cases,
        output_dir=output_dir,
        gemma_endpoint=gemma_endpoint.rstrip("/"),
        resolve_workers=resolve_workers,
        seed_namespace=seed_namespace,
    )
    rows = [
        {
            "case_id": case["case_id"],
            "problem_id": case["problem_id"],
            "candidate_id": case["candidate_id"],
            "second_proof_path": case["proof_path"],
            "second_proof_sha256": case["proof_sha256"],
            "prior_ledger_entry_count": len(case["prior_entries"]),
            "prior_active_count": len(case["obligations"]),
            "closure_counts": {
                key: int(case["closure_result"].get(key) or 0)
                for key in ("closed_count", "unclosed_count", "unsupported_count")
            },
            "new_ledger_entry_count": int(case["updated_ledger"]["entry_count"]),
            "new_active_count": int(case["updated_ledger"]["active_count"]),
            "post_second_gate": case["gate"],
            "third_resolve_state": case["third_resolve"]["state"],
            "third_proof_path": case["third_resolve"]["resolved_proof_path"],
            "third_proof_sha256": case["third_resolve"]["resolved_proof_sha256"],
        }
        for case in cases
    ]
    summary = {
        "schema": "cognitive-well-v0105-iterated-ungrouped-resolve-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "case_count": len(rows),
        "third_resolve_count": sum(row["third_resolve_state"] == "completed" for row in rows),
        "unchanged_promotion_count": sum(
            row["third_resolve_state"] == "promoted_unchanged_no_second_cycle"
            for row in rows
        ),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "status.json", {"state": "completed", "stage": "done", "updated_at": utc_now()})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repeat post-Resolver audit, ledger update, and ungrouped full-proof resolve"
    )
    parser.add_argument("--source-resolve-run", action="append", type=Path, required=True)
    parser.add_argument("--prior-gate-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--gemma-workers", type=int, default=4)
    parser.add_argument("--qwen-workers", type=int, default=4)
    parser.add_argument("--resolve-workers", type=int, default=2)
    parser.add_argument("--seed-namespace", default="v0105")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(
        resolve_runs=args.source_resolve_run,
        prior_gate_run=args.prior_gate_run,
        output_dir=args.output_dir,
        gemma_endpoint=args.gemma_endpoint,
        qwen_endpoint=args.qwen_endpoint,
        gemma_workers=args.gemma_workers,
        qwen_workers=args.qwen_workers,
        resolve_workers=args.resolve_workers,
        seed_namespace=args.seed_namespace,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
