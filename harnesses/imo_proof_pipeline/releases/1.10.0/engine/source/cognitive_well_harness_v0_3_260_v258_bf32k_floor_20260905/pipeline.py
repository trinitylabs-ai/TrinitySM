from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from cognitive_well_harness_v0_3_258_v108_third_resolve_lazy16k_20260904 import (
    pipeline as parent,
)


TERMINAL_STAGE = parent.TERMINAL_STAGE
BUDGET_FORCING_MIN_MAX_TOKENS = 32_768
_v257 = parent.parent
_budget_forcing = _v257.budget_forcing
_PARENT_CONTINUATION_CONFIG = _budget_forcing.continuation_config
_PARENT_BUILD_UPGRADE_MANIFEST = _v257.build_upgrade_manifest


def continuation_config_32k(*, output_dir: Path, stage: str, config: Any) -> Any:
    """Keep same-trace forcing, but never give its continuation less than 32k."""
    configured = _PARENT_CONTINUATION_CONFIG(
        output_dir=output_dir, stage=stage, config=config
    )
    return replace(
        configured,
        max_tokens=max(
            int(getattr(configured, "max_tokens")),
            BUDGET_FORCING_MIN_MAX_TOKENS,
        ),
    )


def build_upgrade_manifest_32k(**kwargs: Any) -> dict[str, Any]:
    manifest = _PARENT_BUILD_UPGRADE_MANIFEST(**kwargs)
    budget = dict(manifest["budget_forcing"])
    budget["same_token_cap"] = False
    budget["continuation_token_policy"] = "max(primary_cap, 32768)"
    budget["continuation_min_max_tokens"] = BUDGET_FORCING_MIN_MAX_TOKENS
    manifest["budget_forcing"] = budget
    return manifest


# The v0257 transport resolves these module globals at call time.  This patch is
# process-local: already-running P1/P2 workers keep their previously loaded code,
# while future v0260 problem subprocesses receive the new continuation floor.
_budget_forcing.continuation_config = continuation_config_32k
_v257.build_upgrade_manifest = build_upgrade_manifest_32k


def _write_policy_manifest(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "v0260_budget_forcing_32k_policy.json"
    expected = {
        "schema": "cognitive-well-v0260-budget-forcing-32k-policy-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "terminal_stage": TERMINAL_STAGE,
        "budget_forcing_same_trace": True,
        "budget_forcing_min_max_tokens": BUDGET_FORCING_MIN_MAX_TOKENS,
        "primary_call_caps_changed": False,
        "raw_proof_generation_primary_max_tokens": 65_536,
        "raw_temperature_transition": "1.0 -> 0.7",
        "ordinary_lazy_cap_recovery": "fresh 16k -> fresh 32k",
    }
    if path.is_file():
        if json.loads(path.read_text(encoding="utf-8")) != expected:
            raise ValueError("v0260 policy manifest drift")
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
        "budget_forcing_min_max_tokens": BUDGET_FORCING_MIN_MAX_TOKENS,
    }
