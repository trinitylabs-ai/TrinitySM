from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.contracts import (
    sha256_text,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.memory import (
    exact_memory_key,
)


def _provenance(arm: str, row: dict[str, Any]) -> dict[str, str]:
    return {
        "arm": arm,
        "source_lemma_id": str(row["lemma_id"]),
        "statement_sha256": sha256_text(str(row["statement"])),
        "proof_sha256": sha256_text(str(row["proof"])),
        "earliest_unresolved_transition_sha256": sha256_text(
            str(row["earliest_unresolved_transition"])
        ),
        "local_dependency_map_sha256": sha256_text(
            str(row["local_dependency_map"])
        ),
    }


def _insert_exact_only(
    *,
    shared: list[dict[str, Any]],
    sources: list[tuple[str, dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    exact = {exact_memory_key(row): row for row in shared}
    audit_log: list[dict[str, Any]] = []
    for arm, source in sources:
        if not bool(source.get("audit", {}).get("certified")):
            raise ValueError(
                f"uncertified lemma reached memory: {source.get('lemma_id')}"
            )
        provenance = _provenance(arm, source)
        key = exact_memory_key(source)
        if key in exact:
            exact[key].setdefault("sources", []).append(provenance)
            audit_log.append(
                {
                    "candidate": provenance,
                    "decision": "rejected_exact_duplicate",
                    "kept_source_lemma_id": exact[key]["lemma_id"],
                }
            )
            continue
        row = copy.deepcopy(source)
        row["sources"] = [provenance]
        shared.append(row)
        exact[key] = row
        audit_log.append(
            {
                "candidate": provenance,
                "decision": "inserted",
                "memory_size": len(shared),
            }
        )
    return shared, audit_log


def merge_shared_verified_exact(
    *,
    arm_results: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sources = [
        (str(arm_result["arm"]), source)
        for arm_result in arm_results
        for source in arm_result["verified"]
    ]
    shared, audit_log = _insert_exact_only(shared=[], sources=sources)
    write_json(
        output_dir / "audit.json",
        {
            "policy": "exact_dedup_only",
            "semantic_model_calls": 0,
            "insertions": audit_log,
        },
    )
    return shared, audit_log


def extend_shared_verified_exact(
    *,
    existing_verified: list[dict[str, Any]],
    salvage_verified: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    shared, audit_log = _insert_exact_only(
        shared=copy.deepcopy(existing_verified),
        sources=[("failure_salvage", source) for source in salvage_verified],
    )
    write_json(
        output_dir / "audit.json",
        {
            "policy": "exact_dedup_only",
            "semantic_model_calls": 0,
            "insertions": audit_log,
        },
    )
    return shared, audit_log


# Backward-compatible local alias for tests and callers created with the first v0.3.78
# draft. It is exact-only despite the historical function name.
extend_shared_verified = extend_shared_verified_exact
