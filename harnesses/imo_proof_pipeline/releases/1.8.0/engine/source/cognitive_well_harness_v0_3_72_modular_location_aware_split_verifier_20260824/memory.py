from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json

from .contracts import SEMANTIC_DEDUP_SCHEMA, sha256_text
from .prompts import semantic_dedup_prompt
from .runtime import ResilientModelRuntime


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def exact_memory_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        normalized(str(row["statement"])),
        normalized(str(row["proof"])),
        normalized(str(row["earliest_unresolved_transition"])),
        normalized(str(row["local_dependency_map"])),
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
        "local_dependency_map_sha256": sha256_text(str(row["local_dependency_map"])),
    }


def merge_shared_verified(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    arm_results: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    shared: list[dict[str, Any]] = []
    exact: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    audit_log: list[dict[str, Any]] = []
    insertion_number = 0
    for arm_result in arm_results:
        arm = str(arm_result["arm"])
        for source in arm_result["verified"]:
            if not bool(source.get("audit", {}).get("certified")):
                raise ValueError(
                    f"uncertified lemma reached shared memory: {source.get('lemma_id')}"
                )
            insertion_number += 1
            provenance = _provenance(arm, source)
            key = exact_memory_key(source)
            if key in exact:
                exact[key]["sources"].append(provenance)
                audit_log.append(
                    {
                        "candidate": provenance,
                        "decision": "rejected_exact_duplicate",
                        "kept_source_lemma_id": exact[key]["lemma_id"],
                    }
                )
                continue
            duplicate = None
            for memory_index, existing in enumerate(shared, start=1):
                destination = output_dir / f"insertion_{insertion_number}" / f"against_{memory_index}"
                decision, generation = runtime.structured(
                    role="gemma",
                    prompt=semantic_dedup_prompt(
                        problem=problem,
                        existing=existing,
                        candidate=source,
                    ),
                    destination=destination,
                    stage="semantic_dedup",
                    schema=SEMANTIC_DEDUP_SCHEMA,
                    temperature=0.1,
                    max_tokens=16_384,
                    seed_label=(
                        f"v072:semantic_dedup:{insertion_number}:{memory_index}"
                    ),
                )
                audit_log.append(
                    {
                        "candidate": provenance,
                        "compared_with": str(existing["lemma_id"]),
                        "equivalent": bool(decision["equivalent"]),
                        "generation": generation["metadata"],
                    }
                )
                if decision["equivalent"]:
                    duplicate = existing
                    break
            if duplicate is not None:
                duplicate["sources"].append(provenance)
                audit_log[-1]["decision"] = "rejected_semantic_duplicate"
                audit_log[-1]["kept_source_lemma_id"] = duplicate["lemma_id"]
                continue
            row = dict(source)
            row["sources"] = [provenance]
            shared.append(row)
            exact[key] = row
            audit_log.append(
                {"candidate": provenance, "decision": "inserted", "memory_size": len(shared)}
            )
    write_json(output_dir / "audit.json", {"insertions": audit_log})
    return shared, audit_log
