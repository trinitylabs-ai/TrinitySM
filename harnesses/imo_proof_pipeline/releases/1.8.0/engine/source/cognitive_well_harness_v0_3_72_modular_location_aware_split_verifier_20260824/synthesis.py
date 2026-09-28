from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import write_json
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.synthesis import assemble_proof

from .contracts import SYNTHESIS_CONFIGURATIONS, sha256_text
from .prompts import legacy_synthesis_prompt, location_aware_synthesis_prompt
from .runtime import ResilientModelRuntime


LOCAL_LABELS = tuple(chr(ord("A") + index) for index in range(26))


def label_verified_lemmas(verified: list[dict[str, Any]]) -> list[dict[str, str]]:
    if len(verified) > len(LOCAL_LABELS):
        raise ValueError("too many verified lemmas for local labels")
    return [
        {
            "label": LOCAL_LABELS[index],
            "source_lemma_id": str(row["lemma_id"]),
            "statement": str(row["statement"]),
            "proof": str(row["proof"]),
            "earliest_unresolved_transition": str(
                row["earliest_unresolved_transition"]
            ),
            "local_dependency_map": str(row["local_dependency_map"]),
        }
        for index, row in enumerate(verified)
    ]


def synthesis_prompt_for_config(
    *,
    config: dict[str, Any],
    problem: str,
    lemmas: list[dict[str, str]],
    anchor_proof: str,
    synthesis_instructions: str,
    gate_policy: dict[str, Any],
) -> str:
    family = str(config["family"])
    if family == "location_aware":
        return location_aware_synthesis_prompt(
            problem=problem,
            lemmas=lemmas,
            synthesis_instructions=synthesis_instructions,
            require_all_lemmas=bool(gate_policy["require_all_verified_lemmas"]),
            minimum_case_headings=int(gate_policy["minimum_case_headings"]),
        )
    return legacy_synthesis_prompt(
        family=family,
        problem=problem,
        lemmas=lemmas,
        anchor_proof=anchor_proof if family == "anchored_refinement" else None,
        synthesis_instructions=synthesis_instructions,
        require_all_lemmas=bool(gate_policy["require_all_verified_lemmas"]),
        minimum_case_headings=int(gate_policy["minimum_case_headings"]),
    )


def generate_one(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    lemmas: list[dict[str, str]],
    anchor_proof: str,
    synthesis_instructions: str,
    gate_policy: dict[str, Any],
    config: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    candidate_id = str(config["candidate_id"])
    destination = output_dir / candidate_id
    prompt = synthesis_prompt_for_config(
        config=config,
        problem=problem,
        lemmas=lemmas,
        anchor_proof=anchor_proof,
        synthesis_instructions=synthesis_instructions,
        gate_policy=gate_policy,
    )
    generated = runtime.text(
        role="gemma",
        prompt=prompt,
        destination=destination,
        stage="main_proof",
        temperature=float(config["temperature"]),
        max_tokens=32_768,
        seed_label=f"v072:synthesis:{candidate_id}",
    )
    main_proof = str(generated["text"]).strip()
    assembly = assemble_proof(
        main_proof=main_proof,
        lemmas=lemmas,
        gate_policy=gate_policy,
    )
    combined = str(assembly["combined_proof"]).strip()
    result = {
        **config,
        "main_proof_sha256": sha256_text(main_proof),
        "proof_sha256": sha256_text(combined),
        "assembly": {
            key: assembly[key]
            for key in (
                "allowed_labels",
                "used_labels",
                "unused_labels",
                "unknown_labels",
                "appended_labels",
                "case_heading_count",
                "structural_gate",
            )
        },
        "generation": generated["metadata"],
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "main_proof.md").write_text(main_proof + "\n", encoding="utf-8")
    (destination / "proof_with_appendix.md").write_text(combined + "\n", encoding="utf-8")
    write_json(destination / "synthesis_result.json", result)
    return {**result, "proof": combined}


def generate_arm_samples(
    *,
    runtime: ResilientModelRuntime,
    arm: str,
    problem: str,
    verified: list[dict[str, Any]],
    anchor_proof: str,
    synthesis_instructions: str,
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    lemmas = label_verified_lemmas(verified)
    configurations = tuple(row for row in SYNTHESIS_CONFIGURATIONS if row["arm"] == arm)
    if len(configurations) != 6:
        raise RuntimeError(f"arm {arm!r} must have exactly six synthesis samples")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        candidates = list(
            executor.map(
                lambda config: generate_one(
                    runtime=runtime,
                    problem=problem,
                    lemmas=lemmas,
                    anchor_proof=anchor_proof,
                    synthesis_instructions=synthesis_instructions,
                    gate_policy=gate_policy,
                    config=config,
                    output_dir=output_dir,
                ),
                configurations,
            )
        )
    return lemmas, candidates
