from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from . import budget_forcing


# Patch the shared transport before loading v108's inherited import graph.
budget_forcing.install()

from cognitive_well_harness_v0_3_108_problem_only_contextual_surgery_20260828 import (  # noqa: E402
    pipeline as v108,
)


EXECUTION_STAGES = v108.EXECUTION_STAGES
TERMINAL_STAGE = "third_resolve"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_upgrade_manifest(
    *,
    problem_file: Path,
    problem_id: str,
    problem_number: int | None,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v0257-v0108-third-resolve-budget-forcing-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "problem_file": str(problem_file.resolve()),
        "problem_file_sha256": _sha256_file(problem_file.resolve()),
        "problem_id": problem_id,
        "problem_number": problem_number,
        "gemma_endpoint": gemma_endpoint.rstrip("/"),
        "qwen_endpoint": qwen_endpoint.rstrip("/"),
        "master_seed": master_seed,
        "seed_namespace": seed_namespace,
        "terminal_stage": TERMINAL_STAGE,
        "post_third_resolve_stages_enabled": False,
        "budget_forcing": {
            "scope": "every Gemma and Qwen transport call through third_resolve",
            "rounds_per_transport_call": 1,
            "same_model": True,
            "same_token_cap": True,
            "same_schema_constraint": True,
            "temperature_policy": {
                "raw_generation_primary_temperature_1_0": {
                    "primary": 1.0,
                    "continuation": 0.7,
                },
                "all_other_calls": "same_as_primary",
            },
            "full_replacement": True,
            "first_response_preserved": True,
            "forced_response_is_canonical": True,
            "text_cue_sha256": hashlib.sha256(
                budget_forcing.TEXT_CONTINUATION.encode("utf-8")
            ).hexdigest(),
            "structured_cue_sha256": hashlib.sha256(
                budget_forcing.STRUCTURED_CONTINUATION.encode("utf-8")
            ).hexdigest(),
        },
        "reference_solution_access": False,
        "gold_score_access": False,
        "codex_feedback_access": False,
    }


def validate_or_write_upgrade_manifest(path: Path, manifest: dict[str, Any]) -> None:
    if not path.is_file():
        _write_json(path, manifest)
        return
    existing = json.loads(path.read_text(encoding="utf-8"))
    immutable = (
        "schema",
        "harness_version",
        "parent_harness_version",
        "problem_file_sha256",
        "problem_id",
        "problem_number",
        "gemma_endpoint",
        "qwen_endpoint",
        "master_seed",
        "seed_namespace",
        "terminal_stage",
        "budget_forcing",
    )
    drift = [key for key in immutable if existing.get(key) != manifest.get(key)]
    if drift:
        raise ValueError(f"v0257 resume manifest drift: {drift}")


def _budget_forcing_summary(output_dir: Path) -> dict[str, Any]:
    event_paths = sorted(output_dir.rglob("*.budget_forcing.json"))
    events = [json.loads(path.read_text(encoding="utf-8")) for path in event_paths]
    targeted = [
        event
        for event in events
        if budget_forcing.is_target_model(str(event.get("model") or ""))
    ]
    transitions = [
        event for event in targeted if event.get("raw_temperature_transition_applied") is True
    ]
    stale = budget_forcing.audit_loaded_aliases()
    return {
        "schema": "cognitive-well-v0257-all-call-budget-forcing-audit-v1",
        "harness_version": HARNESS_VERSION,
        "event_count": len(events),
        "targeted_event_count": len(targeted),
        "models": sorted({str(event.get("model")) for event in targeted}),
        "structured_event_count": sum(bool(event.get("structured")) for event in targeted),
        "text_event_count": sum(not bool(event.get("structured")) for event in targeted),
        "raw_temperature_transition_count": len(transitions),
        "raw_temperature_transitions_valid": all(
            event.get("primary_temperature") == 1.0
            and event.get("forced_temperature") == 0.7
            for event in transitions
        ),
        "all_forced_responses_canonical": bool(targeted)
        and all(
            event.get("canonical_artifacts_are_forced_response") is True
            for event in targeted
        ),
        "stale_loaded_transport_aliases": stale,
        "transport_alias_audit_pass": not stale,
        "terminal_stage": TERMINAL_STAGE,
    }


def run_pipeline(**kwargs: Any) -> dict[str, Any]:
    requested_stop_before = kwargs.get("stop_before")
    requested_stop_after = kwargs.get("stop_after")
    if requested_stop_before is not None:
        raise ValueError("v0257 fixes its terminal boundary after third_resolve")
    if requested_stop_after not in (None, TERMINAL_STAGE):
        raise ValueError("v0257 fixes its terminal boundary after third_resolve")
    kwargs["stop_before"] = None
    kwargs["stop_after"] = TERMINAL_STAGE
    output_dir = Path(kwargs["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    problem_file = Path(kwargs["problem_file"]).resolve()
    manifest = build_upgrade_manifest(
        problem_file=problem_file,
        problem_id=str(kwargs["problem_id"]),
        problem_number=kwargs.get("problem_number"),
        gemma_endpoint=str(kwargs["gemma_endpoint"]),
        qwen_endpoint=str(kwargs["qwen_endpoint"]),
        master_seed=int(kwargs.get("master_seed", 20260904)),
        seed_namespace=str(kwargs.get("seed_namespace", "v0257")),
    )
    validate_or_write_upgrade_manifest(
        output_dir / "v0257_budget_forcing_manifest.json", manifest
    )
    try:
        result = v108.run_pipeline(**kwargs)
        return {
            **result,
            "upgrade_harness_version": HARNESS_VERSION,
            "upgrade_terminal_stage": TERMINAL_STAGE,
        }
    finally:
        _write_json(
            output_dir / "v0257_budget_forcing_audit.json",
            _budget_forcing_summary(output_dir),
        )

