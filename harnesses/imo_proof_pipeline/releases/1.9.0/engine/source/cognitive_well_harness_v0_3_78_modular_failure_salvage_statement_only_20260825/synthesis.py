from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824.protocol import (
    assemble_used_lemma_appendix,
    label_lemmas as v063_label_lemmas,
)
from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824 import (
    run as v063_terminal,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.runtime import (
    ResilientModelRuntime,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.synthesis import (
    generate_arm_samples as generate_v072_arm_samples,
)

from .contracts import STATEMENT_ONLY_CONFIGURATIONS
from .prompts import statement_only_synthesis_prompt


def statement_only_gate_policy(gate_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        **gate_policy,
        "require_all_verified_lemmas": False,
        "minimum_cited_lemmas": 1,
        "minimum_case_headings": 0,
    }


def _generate_one(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    lemmas: list[dict[str, str]],
    gate_policy: dict[str, Any],
    config: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    candidate_id = str(config["candidate_id"])
    destination = output_dir / "candidates" / candidate_id
    prompt = statement_only_synthesis_prompt(problem=problem, lemmas=lemmas)
    generated = v063_terminal.base.saved_generation(destination, "main_composition")
    if generated is None:
        generated = v063_terminal.base.gemma_text(
            endpoint=runtime.config.gemma_endpoint,
            prompt=prompt,
            destination=destination,
            stage="main_composition",
            seed_label=f"v063:{candidate_id}:main_composition",
            temperature=float(config["temperature"]),
            max_tokens=32_768,
        )
    main_proof = str(generated["text"]).strip()
    effective_policy = statement_only_gate_policy(gate_policy)
    experiment_assembly = assemble_used_lemma_appendix(
        main_proof=main_proof, lemmas=lemmas
    )
    admission_violations = []
    if not main_proof:
        admission_violations.append("empty_main_proof")
    if experiment_assembly["unknown_labels"]:
        admission_violations.append("unknown_local_lemma_reference")
    if "internal_record_identifier" in experiment_assembly["gate"]["violations"]:
        admission_violations.append("internal_record_identifier")
    if not experiment_assembly["used_labels"]:
        admission_violations.append("too_few_certified_lemmas_cited")
    assembly = {
        **experiment_assembly,
        "experiment_gate": experiment_assembly["gate"],
        "structural_gate": {
            "passed": not admission_violations,
            "violations": admission_violations,
        },
    }
    combined = str(assembly["combined_proof"]).strip()
    exact_experiment_result = {
        **config,
        "proof": combined,
        "proof_sha256": v063_terminal.sha256_text(combined),
        "main_proof_sha256": v063_terminal.sha256_text(main_proof),
        "dynamic_lemma_count": len(lemmas),
        "assembly": {
            key: assembly[key]
            for key in (
                "allowed_labels",
                "used_labels",
                "unused_labels",
                "unknown_labels",
                "appended_labels",
                "case_heading_count",
                "gate",
            )
        },
        "generation": generated["metadata"],
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "main_proof.md").write_text(main_proof + "\n", encoding="utf-8")
    (destination / "proof_with_appendix.md").write_text(
        combined + "\n", encoding="utf-8"
    )
    v063_terminal.prior.write_json(
        destination / "composition_result.json", exact_experiment_result
    )
    pipeline_result = {
        **exact_experiment_result,
        "arm": "shared",
        "family": "certified_statement_only",
        "prompt_payload": "problem_and_certified_lemma_statements_only",
        "source_proofs_visible": False,
        "location_fields_visible": False,
        "lemma_proof_bodies_visible": False,
        "additional_synthesis_instructions_visible": False,
        "effective_gate_policy": effective_policy,
        "assembly": {
            **exact_experiment_result["assembly"],
            "experiment_gate": exact_experiment_result["assembly"]["gate"],
            "structural_gate": assembly["structural_gate"],
        },
    }
    write_json(destination / "pipeline_candidate.json", pipeline_result)
    return pipeline_result


def generate_statement_only_samples(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    verified: list[dict[str, Any]],
    gate_policy: dict[str, Any],
    output_dir: Path,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    lemmas = v063_label_lemmas(
        [
            {
                "statement": str(row["statement"]),
                "proof": str(row["proof"]),
            }
            for row in verified
        ]
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        candidates = list(
            executor.map(
                lambda config: _generate_one(
                    runtime=runtime,
                    problem=problem,
                    lemmas=lemmas,
                    gate_policy=gate_policy,
                    config=config,
                    output_dir=output_dir,
                ),
                STATEMENT_ONLY_CONFIGURATIONS,
            )
        )
    return lemmas, candidates


__all__ = [
    "generate_statement_only_samples",
    "generate_v072_arm_samples",
    "statement_only_gate_policy",
]
