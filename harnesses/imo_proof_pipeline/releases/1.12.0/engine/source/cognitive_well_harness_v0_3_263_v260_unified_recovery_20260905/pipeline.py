from __future__ import annotations

import ast
import hashlib
import json
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from cognitive_well_harness_v0_3_54_resolver_20260823 import run as resolver
from cognitive_well_harness_v0_3_105_iterated_ungrouped_resolve_20260827 import (
    pipeline as v105,
)
from cognitive_well_harness_v0_3_260_v258_bf32k_floor_20260905 import (
    pipeline as parent,
)


TERMINAL_STAGE = parent.TERMINAL_STAGE
EXPECTED_ORIGINAL_VALID_ERROR = (
    "ORIGINAL_PROOF_VALID requires fusion_assessment REJECTED"
)
ACCEPTING_FUSION_OUTCOME = "ACCEPT_AS_WRITTEN"
THIRD_RESOLVE_RETRY_DIRECTORY = "third_ungrouped_resolve_v0263_fresh_retry1"

_ORIGINAL_PARSE_RESOLUTION = resolver.parse_resolution
_ORIGINAL_RESOLVER_RUN_TASK = resolver.run_task
_ORIGINAL_THIRD_RESOLVE_CASE = v105.v103.run_case
_resolver_context = threading.local()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


@contextmanager
def resolver_fusion_context(outcome: str | None) -> Iterator[None]:
    """Bind the paired Fusion outcome to this resolver worker thread."""

    previous = getattr(_resolver_context, "fusion_outcome", None)
    _resolver_context.fusion_outcome = outcome
    try:
        yield
    finally:
        if previous is None:
            try:
                del _resolver_context.fusion_outcome
            except AttributeError:
                pass
        else:
            _resolver_context.fusion_outcome = previous


def parse_resolution_compat(report: str) -> dict[str, Any]:
    """Accept v0261's sole vocabulary mismatch only with an accepting Fusion."""

    parsed = _ORIGINAL_PARSE_RESOLUTION(report)
    if parsed.get("valid"):
        return parsed
    if (
        getattr(_resolver_context, "fusion_outcome", None)
        == ACCEPTING_FUSION_OUTCOME
        and parsed.get("outcome") == "ORIGINAL_PROOF_VALID"
        and parsed.get("errors") == [EXPECTED_ORIGINAL_VALID_ERROR]
        and (parsed.get("fields") or {}).get("fusion_assessment") == "VALIDATED"
    ):
        return {
            **parsed,
            "valid": True,
            "errors": [],
            "protocol_compatibility": {
                "version": "v0263",
                "source_recovery": "v0261",
                "kind": "accepting_fusion_original_valid_agreement",
                "paired_fusion_outcome": ACCEPTING_FUSION_OUTCOME,
                "model_text_unchanged": True,
            },
        }
    return parsed


def _paired_fusion_outcome(task: dict[str, Any]) -> str:
    declared = str(task.get("fusion_outcome") or "")
    parsed = resolver.parse_fusion(str(task.get("fusion_record") or ""))
    observed = str(parsed.get("outcome") or "")
    if not parsed.get("valid") or not declared or observed != declared:
        raise ValueError(
            "resolver task does not have one valid, identity-matched Fusion outcome"
        )
    return observed


def run_resolver_task_compat(
    *, output_dir: Path, task: dict[str, Any]
) -> dict[str, Any]:
    """Run one Resolver with the v0261 rule bound to its actual Fusion record."""

    outcome = _paired_fusion_outcome(task)
    with resolver_fusion_context(outcome):
        return _ORIGINAL_RESOLVER_RUN_TASK(output_dir=output_dir, task=task)


def _repetition_exhaustion_attempts(error: BaseException) -> list[dict[str, Any]] | None:
    prefix = "v0.3.79 text recovery exhausted: "
    message = str(error)
    if not isinstance(error, RuntimeError) or prefix not in message:
        return None
    try:
        value = ast.literal_eval(message.split(prefix, 1)[1])
    except (SyntaxError, ValueError):
        return None
    if not isinstance(value, list) or not value:
        return None
    attempts = [row for row in value if isinstance(row, dict)]
    if len(attempts) != len(value):
        return None
    if not all(
        row.get("finish_reason") == "repetition"
        and row.get("empty") is True
        and row.get("accepted") is False
        for row in attempts
    ):
        return None
    return attempts


def _load_completed_retry(retry_dir: Path) -> dict[str, Any] | None:
    result_path = retry_dir / "result.json"
    manifest_path = retry_dir / "v0263_repetition_recovery.json"
    if not result_path.is_file() and not manifest_path.is_file():
        return None
    if not result_path.is_file() or not manifest_path.is_file():
        raise RuntimeError(f"incomplete v0263 retry cache: {retry_dir}")
    result = _read_json(result_path)
    manifest = _read_json(manifest_path)
    if (
        result.get("state") != "completed"
        or manifest.get("state") != "completed"
        or manifest.get("retry_result_sha256") != _sha256_file(result_path)
    ):
        raise RuntimeError(f"invalid v0263 retry cache: {retry_dir}")
    return result


def run_third_resolve_case(
    *,
    case: dict[str, Any],
    endpoint: str,
    output_dir: Path,
    seed_namespace: str,
) -> dict[str, Any]:
    """Run one third resolver and fresh-retry only repetition-only exhaustion."""

    retry_dir = output_dir.parent / THIRD_RESOLVE_RETRY_DIRECTORY
    cached = _load_completed_retry(retry_dir)
    if cached is not None:
        return cached
    try:
        return _ORIGINAL_THIRD_RESOLVE_CASE(
            case=case,
            endpoint=endpoint,
            output_dir=output_dir,
            seed_namespace=seed_namespace,
        )
    except RuntimeError as error:
        attempts = _repetition_exhaustion_attempts(error)
        if attempts is None:
            raise
        fresh_namespace = f"{seed_namespace}:v0263:fresh_retry1"
        result = _ORIGINAL_THIRD_RESOLVE_CASE(
            case=case,
            endpoint=endpoint,
            output_dir=retry_dir,
            seed_namespace=fresh_namespace,
        )
        if result.get("state") != "completed":
            raise RuntimeError(
                f"v0263 fresh third-resolver retry did not complete: {result.get('state')}"
            )
        result_path = retry_dir / "result.json"
        v105.write_json(
            retry_dir / "v0263_repetition_recovery.json",
            {
                "schema": "cognitive-well-v0263-third-resolve-repetition-recovery-v1",
                "harness_version": HARNESS_VERSION,
                "state": "completed",
                "case_id": str(case["case_id"]),
                "source_recovery": "v0262",
                "trigger": "all inherited v0.3.79 attempts ended empty at repetition",
                "failed_attempt_count": len(attempts),
                "failed_trace_continued": False,
                "retry_policy": "one fresh full-task restart",
                "fresh_seed_namespace": fresh_namespace,
                "budget_forcing_continuation_min_tokens": 32_768,
                "retry_result_path": str(result_path.resolve()),
                "retry_result_sha256": _sha256_file(result_path),
            },
        )
        return result


def resolve_cases_v263(
    *,
    cases: list[dict[str, Any]],
    output_dir: Path,
    gemma_endpoint: str,
    resolve_workers: int,
    seed_namespace: str,
) -> None:
    """v0.3.105 third resolution with the guarded v0262 fresh retry."""

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
                if str(row.get("status") or "").upper() in v105.ARCHIVE_STATUSES
            ],
        }
        lane = output_dir / "cases" / case["case_id"]
        case["third_resolve"] = run_third_resolve_case(
            case=resolver_case,
            endpoint=gemma_endpoint,
            output_dir=lane / "third_ungrouped_resolve",
            seed_namespace=seed_namespace,
        )

    v105.v098.run_parallel(
        name="third_ungrouped_resolve",
        jobs=jobs,
        workers=resolve_workers,
        task=resolve,
    )
    for case in cases:
        if "third_resolve" not in case:
            case["third_resolve"] = {
                "state": "skipped_no_active_obligations",
                "resolved_proof_path": case["proof_path"],
                "resolved_proof_sha256": case["proof_sha256"],
            }


# All patched symbols are resolved by their parent modules at call time. Resolver
# compatibility is thread-local, so parallel cases cannot inherit another case's
# Fusion outcome. The third-resolve patch does not affect the second resolver.
resolver.parse_resolution = parse_resolution_compat
resolver.run_task = run_resolver_task_compat
v105.resolve_cases = resolve_cases_v263


def _write_policy_manifest(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "v0263_unified_recovery_policy.json"
    expected = {
        "schema": "cognitive-well-v0263-unified-recovery-policy-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "terminal_stage": TERMINAL_STAGE,
        "inherited_v0260_budget_forcing_min_max_tokens": 32_768,
        "v0261_protocol_compatibility": {
            "scope": "ORIGINAL_PROOF_VALID with VALIDATED only",
            "required_paired_fusion_outcome": ACCEPTING_FUSION_OUTCOME,
            "model_text_modified": False,
            "all_other_parse_errors_fail_closed": True,
        },
        "v0262_repetition_recovery": {
            "scope": "third resolver only",
            "trigger": "all v0.3.79 recovery attempts are empty repetition endings",
            "retry_count": 1,
            "failed_trace_continued": False,
            "fresh_seed_namespace": True,
            "all_other_errors_fail_closed": True,
        },
        "reference_solution_access": False,
        "gold_score_access": False,
        "codex_feedback_access": False,
    }
    if path.is_file():
        if _read_json(path) != expected:
            raise ValueError("v0263 unified-recovery policy manifest drift")
        return
    path.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")


def run_pipeline(**kwargs: Any) -> dict[str, Any]:
    output_dir = Path(kwargs["output_dir"]).resolve()
    _write_policy_manifest(output_dir)
    result = parent.run_pipeline(**kwargs)
    return {
        **result,
        "upgrade_harness_version": HARNESS_VERSION,
        "upgrade_parent_harness_version": PARENT_HARNESS_VERSION,
        "resolver_protocol_compatibility": "guarded_v0261",
        "third_resolve_repetition_recovery": "guarded_v0262",
    }

