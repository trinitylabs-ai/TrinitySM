from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION


OUTPUT_NAME = "v0263_unified_recovery_consolidation.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_text(encoding="utf-8").strip().encode("utf-8")
    ).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def relative_record(root: Path, path: Path) -> dict[str, str]:
    path = path.resolve()
    return {
        "path": str(path.relative_to(root)),
        "sha256": file_sha256(path),
    }


def validated_final_proofs(
    *, run_root: Path, summary: dict[str, Any]
) -> list[dict[str, str]]:
    rows = list(summary.get("rows") or [])
    if len(rows) != 4:
        raise ValueError("a consolidated terminal summary must contain four cases")
    proofs: list[dict[str, str]] = []
    for row in rows:
        state = str(row.get("third_resolve_state") or "")
        if state not in {"completed", "promoted_unchanged_no_second_cycle"}:
            raise ValueError(f"nonterminal third-resolver row: {row.get('case_id')}")
        path = Path(str(row["third_proof_path"])).resolve()
        try:
            relative = path.relative_to(run_root)
        except ValueError as error:
            raise ValueError(f"terminal proof escapes the source run: {path}") from error
        if not path.is_file() or text_sha256(path) != str(row["third_proof_sha256"]):
            raise ValueError(f"terminal proof hash mismatch: {path}")
        proofs.append(
            {
                "case_id": str(row["case_id"]),
                "candidate_id": str(row["candidate_id"]),
                "state": state,
                "path": str(relative),
                "text_sha256": str(row["third_proof_sha256"]),
            }
        )
    return proofs


def build_consolidation(run_root: Path) -> dict[str, Any]:
    run_root = run_root.resolve()
    p3 = run_root / "p3"
    p5 = run_root / "p5"
    p3_policy_path = p3 / "v0260_budget_forcing_32k_policy.json"
    p5_policy_path = p5 / "v0260_budget_forcing_32k_policy.json"
    p3_recovery_path = p3 / "v0262_p3_r3_retry_manifest.json"
    p5_recovery_path = p5 / "v0261_original_valid_protocol_compatibility.json"
    p3_summary_path = p3 / "04_iterated_audit_ledger_third_resolve/summary.json"
    p5_summary_path = p5 / "04_iterated_audit_ledger_third_resolve/summary.json"

    p3_policy = read_object(p3_policy_path)
    p5_policy = read_object(p5_policy_path)
    for problem, policy in (("P3", p3_policy), ("P5", p5_policy)):
        if (
            policy.get("harness_version") != "0.3.260"
            or policy.get("budget_forcing_min_max_tokens") != 32_768
            or policy.get("budget_forcing_same_trace") is not True
        ):
            raise ValueError(f"{problem} does not carry the sealed v0260 policy")

    p5_recovery = read_object(p5_recovery_path)
    if (
        p5_recovery.get("schema")
        != "cognitive-well-v0261-original-valid-protocol-compatibility-v1"
        or p5_recovery.get("fusion_outcome") != "ACCEPT_AS_WRITTEN"
        or p5_recovery.get("accepted_model_outcome") != "ORIGINAL_PROOF_VALID"
        or p5_recovery.get("accepted_model_fusion_assessment") != "VALIDATED"
        or p5_recovery.get("model_text_unchanged") is not True
        or p5_recovery.get("mathematical_verdict_host_modified") is not False
        or p5_recovery.get("all_other_parse_errors_fail_closed") is not True
    ):
        raise ValueError("P5 does not satisfy the sealed v0261 compatibility rule")

    p3_recovery = read_object(p3_recovery_path)
    retry_result = Path(str(p3_recovery.get("retry_result_path") or "")).resolve()
    if (
        p3_recovery.get("schema")
        != "cognitive-well-v0262-p3-r3-repetition-retry-manifest-v1"
        or p3_recovery.get("target_case") != "imo2026_p3.t07_r01"
        or p3_recovery.get("failed_trace_continued") is not False
        or p3_recovery.get("budget_forcing_continuation_min_tokens") != 32_768
        or not retry_result.is_file()
        or p3_recovery.get("retry_result_sha256") != file_sha256(retry_result)
    ):
        raise ValueError("P3 does not satisfy the sealed v0262 repetition retry")

    p3_summary = read_object(p3_summary_path)
    p5_summary = read_object(p5_summary_path)
    if (
        p3_summary.get("state") != "completed"
        or p3_summary.get("case_count") != 4
        or p3_summary.get("third_resolve_count") != 4
    ):
        raise ValueError("P3 terminal summary is incomplete")
    if (
        p5_summary.get("state") != "completed"
        or p5_summary.get("case_count") != 4
        or p5_summary.get("third_resolve_count") != 3
        or p5_summary.get("unchanged_promotion_count") != 1
    ):
        raise ValueError("P5 terminal summary is incomplete")

    return {
        "schema": "cognitive-well-v0263-unified-recovery-consolidation-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "state": "completed",
        "source_run": str(run_root),
        "scope": ["imo2026_p3", "imo2026_p5"],
        "inherited_v0260_budget_forcing_min_max_tokens": 32_768,
        "recoveries": {
            "p5_v0261": {
                "kind": "accepting-fusion resolver vocabulary compatibility",
                "record": relative_record(run_root, p5_recovery_path),
                "terminal_summary": relative_record(run_root, p5_summary_path),
                "final_proofs": validated_final_proofs(
                    run_root=run_root, summary=p5_summary
                ),
            },
            "p3_v0262": {
                "kind": "fresh third-resolver repetition retry",
                "record": relative_record(run_root, p3_recovery_path),
                "terminal_summary": relative_record(run_root, p3_summary_path),
                "final_proofs": validated_final_proofs(
                    run_root=run_root, summary=p3_summary
                ),
            },
        },
        "historical_top_level_status_modified": False,
        "proof_artifacts_modified": False,
        "model_calls_performed_by_consolidation": 0,
        "canonical_interpretation": (
            "P3 and P5 terminal proof portfolios are complete under v0260; "
            "their v0261 and v0262 recovery provenance is unified by v0263."
        ),
    }


def consolidate(run_root: Path) -> Path:
    run_root = run_root.resolve()
    output_path = run_root / OUTPUT_NAME
    expected = build_consolidation(run_root)
    if output_path.is_file():
        if read_object(output_path) != expected:
            raise ValueError("v0263 consolidation record drift")
        return output_path
    output_path.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seal existing v0261/v0262 recoveries as one v0263 record"
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        result = build_consolidation(args.run_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(consolidate(args.run_root))


if __name__ == "__main__":
    main()

