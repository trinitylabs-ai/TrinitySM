#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import copy
import json
import sys
import threading
import traceback
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import scripts.run_v0167_fusion_nh_cap6_three_full_cycles_20260902 as v0167
from cognitive_well_harness_v0_3_174_fusion_full_validity_prescreen_20260903.fusion import (
    FUSION_ATTACK_PROMPT,
    FUSION_AUDITOR_PROMPT,
    HARNESS_VERSION as FUSION_PRESCREEN_VERSION,
    run_fusion_prescreen,
)
import cognitive_well_harness_v0_3_175_reasoning_full_validity_prescreen_20260903.pipeline as reasoning


HARNESS_VERSION = (
    "v0.3.176-full-validity-prescreens-then-v0167-three-cycles-20260903"
)
DEFAULT_OUTPUT = (
    ROOT / "runs/v0176_full_validity_prescreens_then_v0167_three_cycles_20260903"
)
DEFAULT_PRESCREEN_MAX_TOKENS = 32_768
DEFAULT_GEMMA_PRESCREEN_CONCURRENCY = 8
DEFAULT_QWEN_PRESCREEN_CONCURRENCY = 8
DEFAULT_CASE_KEYS = tuple(
    sorted(
        v0167.DEFAULT_CASES,
        key=lambda key: (int(key.split(":", 1)[0][1:]), key.split(":", 1)[1]),
    )
)
SHARD_CASE_KEYS = {
    "all": DEFAULT_CASE_KEYS,
    "a": tuple(
        key for key in DEFAULT_CASE_KEYS if int(key.split(":", 1)[0][1:]) <= 3
    ),
    "b": tuple(
        key for key in DEFAULT_CASE_KEYS if int(key.split(":", 1)[0][1:]) >= 4
    ),
}


def select_case_keys(
    *, explicit: list[str] | None, shard: str, problem: str | None
) -> list[str]:
    selectors = int(bool(explicit)) + int(shard != "all") + int(problem is not None)
    if selectors > 1:
        raise ValueError(
            "use only one selector: explicit --case values, --shard a/b, or --problem"
        )
    if explicit:
        return list(explicit)
    if problem is not None:
        return [key for key in DEFAULT_CASE_KEYS if key.startswith(f"{problem}:")]
    return list(SHARD_CASE_KEYS[shard])


def write_status(destination: Path, *, state: str, stage: str, **extra: Any) -> None:
    v0167.nh_runner.write_json(
        destination / "status.json",
        {
            "state": state,
            "stage": stage,
            **extra,
            "updated_at": v0167.nh_runner.utc_now(),
        },
    )


class RoleLimitedRuntime:
    """Apply independent request caps to Gemma and Qwen model calls."""

    def __init__(
        self, runtime: Any, *, gemma_concurrency: int, qwen_concurrency: int
    ) -> None:
        if gemma_concurrency < 1 or qwen_concurrency < 1:
            raise ValueError("role concurrency limits must be positive")
        self.runtime = runtime
        self.limits = {
            "gemma": gemma_concurrency,
            "qwen": qwen_concurrency,
        }
        self._semaphores = {
            role: threading.BoundedSemaphore(limit)
            for role, limit in self.limits.items()
        }

    def text(self, **kwargs: Any) -> dict[str, Any]:
        role = str(kwargs.get("role") or "")
        if role not in self._semaphores:
            raise ValueError(f"unsupported runtime role: {role}")
        with self._semaphores[role]:
            return self.runtime.text(**kwargs)


def run_v0167(
    *,
    filtered_cases: dict[str, dict[str, Any]],
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    fusion_max_tokens: int,
    nh_max_tokens: int,
    thinking_token_budget: int | None,
    max_concurrency: int,
    master_seed: int,
    seed_namespace: str,
    retry_failed: bool,
) -> None:
    selected_keys = list(filtered_cases)
    original_load_case = v0167.load_case

    def load_filtered(case_key: str) -> dict[str, Any]:
        if case_key not in filtered_cases:
            raise ValueError(f"missing prescreened case: {case_key}")
        return copy.deepcopy(filtered_cases[case_key])

    argv = [
        str(Path(v0167.__file__).resolve()),
        "--output-dir",
        str(output_dir.resolve()),
        "--gemma-endpoint",
        gemma_endpoint,
        "--qwen-endpoint",
        qwen_endpoint,
        "--fusion-max-tokens",
        str(fusion_max_tokens),
        "--nh-max-tokens",
        str(nh_max_tokens),
        "--max-concurrency",
        str(max_concurrency),
        "--master-seed",
        str(master_seed),
        "--seed-namespace",
        f"{seed_namespace}:v0167-three-cycles",
    ]
    if thinking_token_budget is not None:
        argv.extend(("--thinking-token-budget", str(thinking_token_budget)))
    if retry_failed:
        argv.append("--retry-failed")
    for case_key in selected_keys:
        argv.extend(("--case", case_key))

    saved_argv = sys.argv
    try:
        v0167.load_case = load_filtered
        sys.argv = argv
        v0167.main()
    finally:
        sys.argv = saved_argv
        v0167.load_case = original_load_case


def _meaningful_proof_alarm(explanation: str) -> str | None:
    alarm = reasoning.extract_proof_alarm(explanation)
    if alarm is None:
        return None
    normalized = alarm.strip().rstrip(".")
    if not normalized or normalized.upper() == "NONE":
        return None
    if normalized.upper().startswith("SAME AS PACKET FLAW"):
        return None
    return alarm.strip()


def forward_inactive_packet_proof_alarms(
    *,
    source_case: dict[str, Any],
    filtered_case: dict[str, Any],
    decisions: list[dict[str, str]],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Forward only independent alarms whose source packet was deactivated.

    The unsafe packet body stays removed.  Each surviving alarm is explicitly
    marked unverified so the existing v0167 group refiner must check it before
    making an edit.
    """
    result = copy.deepcopy(filtered_case)
    source_by_id: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for group in source_case.get("groups") or []:
        for packet in group.get("nh_packets") or []:
            packet_id = str(packet["trace_id"])
            if packet_id in source_by_id:
                raise ValueError(f"duplicate packet ID while routing alarms: {packet_id}")
            source_by_id[packet_id] = (group, packet)

    result_group_by_id = {
        str(group["group_id"]): group for group in result.get("groups") or []
    }
    forwarded: list[dict[str, str]] = []
    for decision in decisions:
        if decision["status"] != "INACTIVE":
            continue
        alarm = _meaningful_proof_alarm(str(decision.get("explanation") or ""))
        if alarm is None:
            continue
        packet_id = str(decision["packet_id"])
        if packet_id not in source_by_id:
            raise ValueError(f"proof alarm source packet is missing: {packet_id}")
        source_group, source_packet = source_by_id[packet_id]
        group_id = str(source_group["group_id"])
        target_group = result_group_by_id[group_id]
        alarm_id = f"PRESCREEN_ALARM_{packet_id}"
        if any(
            str(packet.get("trace_id")) == alarm_id
            for packet in target_group.get("nh_packets") or []
        ):
            raise ValueError(f"duplicate forwarded proof alarm ID: {alarm_id}")
        alarm_text = (
            "PRESCREEN_PROOF_ALARM\n"
            f"SOURCE_PACKET_ID: {packet_id}\n"
            "SOURCE_PACKET_STATUS: INACTIVE\n"
            "STATUS: UNVERIFIED; independently check this alarm before editing.\n"
            f"ALARM: {alarm}\n"
            "END_PRESCREEN_PROOF_ALARM"
        )
        target_group.setdefault("nh_packets", []).append(
            {
                "trace_id": alarm_id,
                "type": "DEFECT",
                "target": "Independent proof defect found while rejecting a packet",
                "relevance_reason": (
                    "The invalid source packet was removed, but its independently "
                    "reported proof alarm may still identify a repairable defect."
                ),
                "target_unit_ids": list(source_packet.get("target_unit_ids") or []),
                "exact_source_text": alarm_text,
                "exact_source_sha256": reasoning.sha256_text(alarm_text),
                "source_packet_id": packet_id,
                "source_packet_status": "INACTIVE",
                "prescreen_generated_proof_alarm": True,
            }
        )
        forwarded.append(
            {
                "case_key": str(source_case["case_key"]),
                "group_id": group_id,
                "source_packet_id": packet_id,
                "alarm_packet_id": alarm_id,
                "alarm": alarm,
            }
        )

    metadata = result.setdefault("nh_packet_full_validity_prescreen", {})
    metadata["inactive_packet_proof_alarm_policy"] = (
        "forward_as_separate_unverified_group_evidence_without_source_packet_body"
    )
    metadata["forwarded_inactive_packet_proof_alarm_count"] = len(forwarded)
    metadata["forwarded_inactive_packet_proof_alarms"] = forwarded
    return result, forwarded


def run_fusion_prescreens(
    *,
    runtime: Any,
    cases: dict[str, dict[str, Any]],
    output_root: Path,
    max_tokens: int,
    max_concurrency: int,
    seed_namespace: str,
    attacker_role: str,
    auditor_role: str,
    progress: Callable[[list[dict[str, str]]], None] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    filtered_by_key: dict[str, dict[str, Any]] = {}
    rows_by_key: dict[str, dict[str, str]] = {}
    lock = threading.Lock()

    def work(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        return run_fusion_prescreen(
            runtime=runtime,
            case=case,
            output_root=output_root,
            max_tokens=max_tokens,
            seed_namespace=seed_namespace,
            attacker_role=attacker_role,
            auditor_role=auditor_role,
        )

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(max_concurrency, len(cases))
    ) as executor:
        futures = {
            executor.submit(work, case): case_key for case_key, case in cases.items()
        }
        for future in concurrent.futures.as_completed(futures):
            case_key = futures[future]
            filtered, decision = future.result()
            row = {
                "case_key": case_key,
                "status": decision["status"],
                "explanation": decision["explanation"],
            }
            with lock:
                filtered_by_key[case_key] = filtered
                rows_by_key[case_key] = row
                if progress is not None:
                    progress([rows_by_key[key] for key in cases if key in rows_by_key])

    return (
        {key: filtered_by_key[key] for key in cases},
        [rows_by_key[key] for key in cases],
    )


def run_reasoning_prescreens(
    *,
    runtime: Any,
    cases: dict[str, dict[str, Any]],
    output_root: Path,
    max_tokens: int,
    max_concurrency: int,
    seed_namespace: str,
    attacker_role: str,
    auditor_role: str,
    attacker_temperature: float,
    auditor_temperature: float,
    progress: Callable[[int, int], None] | None = None,
) -> tuple[
    dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]
]:
    packet_rows_by_key = {
        key: reasoning.collect_nh_packets(case) for key, case in cases.items()
    }
    total_packets = sum(len(rows) for rows in packet_rows_by_key.values())
    decisions_by_key: dict[str, dict[str, dict[str, str]]] = {
        key: {} for key in cases
    }
    completed = 0
    lock = threading.Lock()

    def work(
        case_key: str, case: dict[str, Any], packet_row: dict[str, Any]
    ) -> dict[str, str]:
        case_output = (
            output_root / str(case["problem_key"]) / str(case["candidate_id"])
        )
        return reasoning.run_packet_prescreen(
            runtime=runtime,
            case=case,
            packet_row=packet_row,
            output_dir=case_output,
            max_tokens=max_tokens,
            seed_namespace=seed_namespace,
            attacker_role=attacker_role,
            auditor_role=auditor_role,
            attacker_temperature=attacker_temperature,
            auditor_temperature=auditor_temperature,
        )

    jobs = [
        (case_key, case, packet_row)
        for case_key, case in cases.items()
        for packet_row in packet_rows_by_key[case_key]
    ]
    if jobs:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(max_concurrency, len(jobs))
        ) as executor:
            futures = {
                executor.submit(work, case_key, case, packet_row): (
                    case_key,
                    str(packet_row["packet_id"]),
                )
                for case_key, case, packet_row in jobs
            }
            for future in concurrent.futures.as_completed(futures):
                case_key, packet_id = futures[future]
                decision = future.result()
                with lock:
                    decisions_by_key[case_key][packet_id] = decision
                    completed += 1
                    if progress is not None:
                        progress(completed, total_packets)

    filtered_cases: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    all_forwarded_alarms: list[dict[str, str]] = []
    for case_key, case in cases.items():
        packet_rows = packet_rows_by_key[case_key]
        decisions = [
            decisions_by_key[case_key][str(packet_row["packet_id"])]
            for packet_row in packet_rows
        ]
        case_output = (
            output_root / str(case["problem_key"]) / str(case["candidate_id"])
        )
        decision_path = case_output / "packet_status.tsv"
        reasoning.write_text(
            decision_path, reasoning.render_decision_tsv(decisions)
        )
        filtered = reasoning.apply_packet_decisions(
            case,
            decisions,
            decision_path=decision_path,
            max_concurrency=max_concurrency,
        )
        filtered, forwarded = forward_inactive_packet_proof_alarms(
            source_case=case,
            filtered_case=filtered,
            decisions=decisions,
        )
        filtered_cases[case_key] = filtered
        all_forwarded_alarms.extend(forwarded)
        active = sum(decision["status"] == "ACTIVE" for decision in decisions)
        rows.append(
            {
                "case_key": case_key,
                "input_packets": len(decisions),
                "active_packets": active,
                "inactive_packets": len(decisions) - active,
                "forwarded_inactive_packet_proof_alarms": len(forwarded),
                "downstream_evidence_packets": sum(
                    len(group.get("nh_packets") or [])
                    for group in filtered.get("groups") or []
                ),
            }
        )
    return filtered_cases, rows, all_forwarded_alarms


def dry_run_payload(
    *,
    cases: dict[str, dict[str, Any]],
    gemma_prescreen_concurrency: int,
    qwen_prescreen_concurrency: int,
    refinement_concurrency: int,
) -> dict[str, Any]:
    preflight = v0167.dry_run(list(cases.values()))
    packet_counts = {
        key: len(reasoning.collect_nh_packets(case)) for key, case in cases.items()
    }
    fusion_packet_count = sum(case.get("fusion") is not None for case in cases.values())
    return {
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "version_lineage": {
            "portfolio_completion_supervisor": "v0.3.168",
            "three_cycle_core": v0167.HARNESS_VERSION,
            "prior_integration_scaffold": "v0.3.172",
            "fusion_prescreen": FUSION_PRESCREEN_VERSION,
            "reasoning_prescreen": reasoning.HARNESS_VERSION,
        },
        "case_keys": list(cases),
        "case_count": len(cases),
        "fusion_packet_count": fusion_packet_count,
        "reasoning_packet_counts": packet_counts,
        "reasoning_packet_count": sum(packet_counts.values()),
        "prescreen_role_concurrency": {
            "gemma": gemma_prescreen_concurrency,
            "qwen": qwen_prescreen_concurrency,
        },
        "prescreen_worker_concurrency": (
            gemma_prescreen_concurrency + qwen_prescreen_concurrency
        ),
        "refinement_proof_concurrency": refinement_concurrency,
        "stage_schedule": [
            "fusion_two_call_full_validity_prescreen",
            "reasoning_packet_two_call_full_validity_prescreen",
            "three_cycles_each_of_filtered_fusion_then_filtered_reasoning_then_cleanup",
        ],
        "v0167_preflight": preflight,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run validated v0174/v0175 packet prescreens, then the unchanged "
            "v0167 three-cycle Fusion/NH/cleanup refinement pipeline"
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case", action="append", dest="case_keys")
    parser.add_argument(
        "--shard",
        choices=("all", "a", "b"),
        default="all",
        help="v0168 portfolio shard: a=P1-P3, b=P4-P5, all=both",
    )
    parser.add_argument(
        "--problem",
        choices=tuple(f"p{number}" for number in range(1, 6)),
        help="run all four frozen proofs for one problem",
    )
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--master-seed", type=int, default=20260903)
    parser.add_argument(
        "--seed-namespace",
        default="v0176:full-validity-prescreens-then-v0167-three-cycles",
    )
    parser.add_argument(
        "--prescreen-max-tokens", type=int, default=DEFAULT_PRESCREEN_MAX_TOKENS
    )
    parser.add_argument("--prescreen-thinking-token-budget", type=int, default=None)
    parser.add_argument(
        "--gemma-prescreen-concurrency",
        type=int,
        default=DEFAULT_GEMMA_PRESCREEN_CONCURRENCY,
    )
    parser.add_argument(
        "--qwen-prescreen-concurrency",
        type=int,
        default=DEFAULT_QWEN_PRESCREEN_CONCURRENCY,
    )
    parser.add_argument(
        "--fusion-attacker-role", choices=("gemma", "qwen"), default="gemma"
    )
    parser.add_argument(
        "--fusion-auditor-role", choices=("gemma", "qwen"), default="qwen"
    )
    parser.add_argument(
        "--reasoning-attacker-role", choices=("gemma", "qwen"), default="gemma"
    )
    parser.add_argument(
        "--reasoning-auditor-role", choices=("gemma", "qwen"), default="gemma"
    )
    parser.add_argument("--reasoning-attacker-temperature", type=float, default=0.2)
    parser.add_argument("--reasoning-auditor-temperature", type=float, default=0.1)
    parser.add_argument("--fusion-max-tokens", type=int, default=32_000)
    parser.add_argument("--nh-max-tokens", type=int, default=24_000)
    parser.add_argument(
        "--refinement-thinking-token-budget", type=int, default=16_384
    )
    parser.add_argument(
        "--v0167-max-concurrency",
        type=int,
        default=None,
        help=(
            "parallel proof chains in the three-cycle resolver; defaults to all "
            "selected proofs, capped by the Gemma concurrency"
        ),
    )
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    selected_keys = select_case_keys(
        explicit=args.case_keys,
        shard=args.shard,
        problem=args.problem,
    )
    if len(selected_keys) != len(set(selected_keys)):
        raise ValueError("--case values must be unique")
    unknown = sorted(set(selected_keys).difference(v0167.DEFAULT_CASES))
    if unknown:
        raise ValueError(f"unknown case keys: {unknown}")
    refinement_concurrency = args.v0167_max_concurrency or min(
        len(selected_keys), args.gemma_prescreen_concurrency
    )
    if min(
        args.gemma_prescreen_concurrency,
        args.qwen_prescreen_concurrency,
        refinement_concurrency,
    ) < 1:
        raise ValueError("concurrency values must be positive")
    if min(
        args.prescreen_max_tokens, args.fusion_max_tokens, args.nh_max_tokens
    ) < 1:
        raise ValueError("token budgets must be positive")
    if min(
        args.reasoning_attacker_temperature, args.reasoning_auditor_temperature
    ) < 0:
        raise ValueError("temperatures must be nonnegative")

    original_cases = {
        key: v0167.load_case(key) for key in selected_keys
    }
    validation = dry_run_payload(
        cases=original_cases,
        gemma_prescreen_concurrency=args.gemma_prescreen_concurrency,
        qwen_prescreen_concurrency=args.qwen_prescreen_concurrency,
        refinement_concurrency=refinement_concurrency,
    )
    if args.dry_run:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 0

    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "cognitive-well-v0176-portfolio-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": v0167.nh_runner.utc_now(),
        "implementation_path": str(Path(__file__).resolve()),
        "implementation_sha256": v0167.nh_runner.file_sha256(Path(__file__).resolve()),
        **validation,
        "state": "configured",
        "source_portfolio": (
            "v0168-completed-labels-and-four-proofs-per-problem-p1-through-p5"
        ),
        "portfolio_selection": (
            f"problem:{args.problem}"
            if args.problem is not None
            else "explicit_cases"
            if args.case_keys
            else f"shard:{args.shard}"
        ),
        "prescreen": {
            "max_tokens": args.prescreen_max_tokens,
            "thinking_token_budget": args.prescreen_thinking_token_budget,
            "role_concurrency": {
                "gemma": args.gemma_prescreen_concurrency,
                "qwen": args.qwen_prescreen_concurrency,
            },
            "worker_concurrency": (
                args.gemma_prescreen_concurrency
                + args.qwen_prescreen_concurrency
            ),
            "logical_calls_per_present_packet": 2,
            "atomicization": False,
            "model_output": "one_plain_text_line_three_fields_no_json_or_markdown",
            "fusion": {
                "harness_version": FUSION_PRESCREEN_VERSION,
                "attacker_role": args.fusion_attacker_role,
                "auditor_role": args.fusion_auditor_role,
                "attacker_temperature": 0.2,
                "auditor_temperature": 0.1,
                "attacker_prompt_sha256": reasoning.sha256_text(FUSION_ATTACK_PROMPT),
                "auditor_prompt_sha256": reasoning.sha256_text(FUSION_AUDITOR_PROMPT),
                "no_packet": "skip_without_model_call",
            },
            "reasoning": {
                "harness_version": reasoning.HARNESS_VERSION,
                "attacker_role": args.reasoning_attacker_role,
                "auditor_role": args.reasoning_auditor_role,
                "attacker_temperature": args.reasoning_attacker_temperature,
                "auditor_temperature": args.reasoning_auditor_temperature,
                "attacker_prompt_sha256": reasoning.sha256_text(
                    reasoning.REASONING_ATTACK_PROMPT
                ),
                "auditor_prompt_sha256": reasoning.sha256_text(
                    reasoning.REASONING_AUDITOR_PROMPT
                ),
                "numbered_reference_guard": reasoning.NUMBERED_REFERENCE_GUARD_VERSION,
                "quantifier_witness_guard": reasoning.QUANTIFIER_WITNESS_GUARD_VERSION,
                "sequence_legality_guard": reasoning.SEQUENCE_LEGALITY_GUARD_VERSION,
                "inactive_packet_proof_alarm": (
                    "forward_only_alarm_as_unverified_same_group_evidence"
                ),
            },
        },
        "refinement": {
            "harness_version": v0167.HARNESS_VERSION,
            "cycle_count": v0167.TOTAL_CYCLES,
            "cycle_schedule": "FILTERED_FUSION_THEN_FILTERED_REASONING_THEN_CLEANUP",
            "maximum_reasoning_packets_per_call": v0167.MAX_NH_PACKETS_PER_CALL,
            "fusion_max_tokens": args.fusion_max_tokens,
            "nh_max_tokens": args.nh_max_tokens,
            "thinking_token_budget": args.refinement_thinking_token_budget,
            "max_concurrency": refinement_concurrency,
        },
        "master_seed": args.master_seed,
        "seed_namespace": args.seed_namespace,
    }
    v0167.nh_runner.write_json(destination / "manifest.json", manifest)

    base_runtime = v0167.nh_runner.ResilientModelRuntime(
        v0167.nh_runner.RuntimeConfig(
            gemma_endpoint=args.gemma_endpoint.rstrip("/"),
            qwen_endpoint=args.qwen_endpoint.rstrip("/"),
            gemma_model=v0167.nh_runner.GEMMA_MODEL,
            qwen_model=v0167.nh_runner.QWEN_MODEL,
            master_seed=args.master_seed,
            thinking_token_budget=args.prescreen_thinking_token_budget,
            reasoning_effort="max",
        )
    )
    runtime = RoleLimitedRuntime(
        base_runtime,
        gemma_concurrency=args.gemma_prescreen_concurrency,
        qwen_concurrency=args.qwen_prescreen_concurrency,
    )
    prescreen_worker_concurrency = (
        args.gemma_prescreen_concurrency + args.qwen_prescreen_concurrency
    )

    try:
        write_status(
            destination,
            state="running",
            stage="fusion_full_validity_prescreen",
            completed_cases=0,
            case_count=len(original_cases),
        )

        def fusion_progress(rows: list[dict[str, str]]) -> None:
            write_status(
                destination,
                state="running",
                stage="fusion_full_validity_prescreen",
                completed_cases=len(rows),
                case_count=len(original_cases),
                active=sum(row["status"] == "ACTIVE" for row in rows),
                inactive=sum(row["status"] == "INACTIVE" for row in rows),
                skipped=sum(
                    row["status"] == "SKIPPED_NO_PACKET" for row in rows
                ),
            )

        fusion_filtered, fusion_rows = run_fusion_prescreens(
            runtime=runtime,
            cases=original_cases,
            output_root=destination / "01_fusion_full_validity_prescreen",
            max_tokens=args.prescreen_max_tokens,
            max_concurrency=prescreen_worker_concurrency,
            seed_namespace=f"{args.seed_namespace}:fusion",
            attacker_role=args.fusion_attacker_role,
            auditor_role=args.fusion_auditor_role,
            progress=fusion_progress,
        )
        v0167.nh_runner.write_json(
            destination / "01_fusion_full_validity_prescreen/summary.json",
            {
                "schema": "cognitive-well-v0176-fusion-prescreen-summary-v1",
                "rows": fusion_rows,
                "active": sum(row["status"] == "ACTIVE" for row in fusion_rows),
                "inactive": sum(
                    row["status"] == "INACTIVE" for row in fusion_rows
                ),
                "skipped": sum(
                    row["status"] == "SKIPPED_NO_PACKET"
                    for row in fusion_rows
                ),
                "completed_at": v0167.nh_runner.utc_now(),
            },
        )

        total_reasoning_packets = sum(
            len(reasoning.collect_nh_packets(case))
            for case in fusion_filtered.values()
        )

        def reasoning_progress(completed: int, total: int) -> None:
            write_status(
                destination,
                state="running",
                stage="reasoning_full_validity_prescreen",
                completed_packets=completed,
                packet_count=total,
                case_count=len(original_cases),
            )

        write_status(
            destination,
            state="running",
            stage="reasoning_full_validity_prescreen",
            completed_packets=0,
            packet_count=total_reasoning_packets,
            case_count=len(original_cases),
        )
        filtered_cases, reasoning_rows, forwarded_alarms = run_reasoning_prescreens(
            runtime=runtime,
            cases=fusion_filtered,
            output_root=destination / "02_reasoning_full_validity_prescreen",
            max_tokens=args.prescreen_max_tokens,
            max_concurrency=prescreen_worker_concurrency,
            seed_namespace=f"{args.seed_namespace}:reasoning",
            attacker_role=args.reasoning_attacker_role,
            auditor_role=args.reasoning_auditor_role,
            attacker_temperature=args.reasoning_attacker_temperature,
            auditor_temperature=args.reasoning_auditor_temperature,
            progress=reasoning_progress,
        )
        filtered_validation = v0167.dry_run(list(filtered_cases.values()))
        v0167.nh_runner.write_json(
            destination / "02_reasoning_full_validity_prescreen/summary.json",
            {
                "schema": "cognitive-well-v0176-reasoning-prescreen-summary-v1",
                "rows": reasoning_rows,
                "input_packets": sum(row["input_packets"] for row in reasoning_rows),
                "active_packets": sum(row["active_packets"] for row in reasoning_rows),
                "inactive_packets": sum(
                    row["inactive_packets"] for row in reasoning_rows
                ),
                "forwarded_inactive_packet_proof_alarm_count": len(
                    forwarded_alarms
                ),
                "forwarded_inactive_packet_proof_alarms": forwarded_alarms,
                "filtered_v0167_preflight": filtered_validation,
                "completed_at": v0167.nh_runner.utc_now(),
            },
        )

        write_status(
            destination,
            state="running",
            stage="v0167_three_cycles",
            completed_fusion_prescreen_cases=len(fusion_rows),
            completed_reasoning_prescreen_packets=sum(
                row["input_packets"] for row in reasoning_rows
            ),
            forwarded_inactive_packet_proof_alarm_count=len(forwarded_alarms),
            case_count=len(original_cases),
        )
        run_v0167(
            filtered_cases=filtered_cases,
            output_dir=destination / "03_v0167_three_cycles",
            gemma_endpoint=args.gemma_endpoint,
            qwen_endpoint=args.qwen_endpoint,
            fusion_max_tokens=args.fusion_max_tokens,
            nh_max_tokens=args.nh_max_tokens,
            thinking_token_budget=args.refinement_thinking_token_budget,
            max_concurrency=refinement_concurrency,
            master_seed=args.master_seed,
            seed_namespace=args.seed_namespace,
            retry_failed=args.retry_failed,
        )
        downstream_path = destination / "03_v0167_three_cycles/result.json"
        downstream = v0167.nh_runner.read_object(downstream_path)
        state = str(downstream.get("state") or "completed_with_failures")
        result = {
            "schema": "cognitive-well-v0176-portfolio-result-v1",
            "harness_version": HARNESS_VERSION,
            "state": state,
            "case_count": len(original_cases),
            "fusion_prescreen_rows": fusion_rows,
            "reasoning_prescreen_rows": reasoning_rows,
            "forwarded_inactive_packet_proof_alarm_count": len(forwarded_alarms),
            "filtered_v0167_preflight": filtered_validation,
            "v0167_result_path": str(downstream_path.resolve()),
            "v0167_result_sha256": v0167.nh_runner.file_sha256(downstream_path),
            "completed_at": v0167.nh_runner.utc_now(),
        }
        v0167.nh_runner.write_json(destination / "result.json", result)
        write_status(
            destination,
            state=state,
            stage="done",
            case_count=len(original_cases),
            forwarded_inactive_packet_proof_alarm_count=len(forwarded_alarms),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if state == "completed" else 1
    except Exception as error:
        write_status(
            destination,
            state="failed_closed",
            stage="mechanical_failure_requires_resume",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
