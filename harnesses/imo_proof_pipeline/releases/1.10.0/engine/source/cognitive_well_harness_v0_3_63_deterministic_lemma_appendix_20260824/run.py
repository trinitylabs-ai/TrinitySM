from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823 import (
    protocol as reviewer1,
)
from cognitive_well_harness_v0_3_57_v030_cross_model_pair_dossier_ab_20260824 import (
    run_arm as base,
)
from cognitive_well_harness_v0_3_62_dynamic_terminal_composition_20260824 import (
    run as prior,
)
from cognitive_well_harness_v0_3_62_dynamic_terminal_composition_20260824.protocol import (
    load_dynamic_verified_arguments,
    sha256_text,
)
from experiments.local_math_verifier.runtime import (
    HTTPGenerationConfig,
    run_openai_chat_generation,
)

from . import HARNESS_VERSION
from .protocol import assemble_used_lemma_appendix, label_lemmas, main_proof_prompt


CONFIGURATIONS = (
    {"candidate_id": "t02_s1", "temperature": 0.2, "replicate": 1},
    {"candidate_id": "t02_s2", "temperature": 0.2, "replicate": 2},
    {"candidate_id": "t04_s1", "temperature": 0.4, "replicate": 1},
    {"candidate_id": "t04_s2", "temperature": 0.4, "replicate": 2},
)


def reviewer1_with_cap_retry(
    *, output_root: Path, problem: str, candidate: dict[str, Any]
) -> dict[str, Any]:
    initial = prior.run_reviewer1(
        output_root=output_root, problem=problem, candidate=candidate
    )
    if initial["review"]["valid"]:
        return initial
    candidate_id = str(candidate["candidate_id"])
    destination = output_root / "candidates" / candidate_id / "reviewer1"
    stage = "earliest_break_retry_24k"
    generated = base.saved_generation(destination, stage)
    if generated is None:
        generated = run_openai_chat_generation(
            endpoint=prior.QWEN_ENDPOINT,
            model=base.QWEN_MODEL,
            prompt=reviewer1.SYSTEM_PROMPT,
            user_prompt=reviewer1.review_user_prompt(
                problem=problem, proof=str(candidate["proof"])
            ),
            output_dir=destination,
            stage=stage,
            config=HTTPGenerationConfig(
                max_tokens=24_576,
                temperature=0.2,
                top_p=1.0,
                top_k=-1,
                seed=base.stable_seed(f"v063:{candidate_id}:reviewer1_retry_24k"),
                thinking_token_budget=None,
                reasoning_effort="max",
                repetition_detection=base.REPETITION_DETECTION,
                timeout_seconds=14_400,
            ),
        )
    parsed = reviewer1.parse_review(str(generated["text"]))
    result = {
        "candidate_id": candidate_id,
        "temperature": 0.2,
        "review": parsed,
        "generation": generated["metadata"],
        "cap_retry_invoked": True,
        "initial_review": initial["review"],
        "initial_generation": initial["generation"],
    }
    prior.write_json(destination / "result.json", result)
    return result


def generate_candidate(
    *, output_root: Path, problem: str, lemmas: list[dict[str, str]], config: dict[str, Any]
) -> dict[str, Any]:
    candidate_id = str(config["candidate_id"])
    destination = output_root / "candidates" / candidate_id
    prompt = main_proof_prompt(problem=problem, lemmas=lemmas)
    generated = base.saved_generation(destination, "main_composition")
    if generated is None:
        generated = base.gemma_text(
            endpoint=prior.GEMMA_ENDPOINT,
            prompt=prompt,
            destination=destination,
            stage="main_composition",
            seed_label=f"v063:{candidate_id}:main_composition",
            temperature=float(config["temperature"]),
            max_tokens=32_768,
        )
    main_proof = str(generated["text"]).strip()
    assembly = assemble_used_lemma_appendix(main_proof=main_proof, lemmas=lemmas)
    combined = str(assembly["combined_proof"]).strip()
    result = {
        **config,
        "proof": combined,
        "proof_sha256": sha256_text(combined),
        "main_proof_sha256": sha256_text(main_proof),
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
    prior.write_json(destination / "composition_result.json", result)
    (destination / "main_proof.md").write_text(main_proof + "\n", encoding="utf-8")
    (destination / "proof_with_appendix.md").write_text(
        combined + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compose a main proof and append cited verified lemma bodies deterministically"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--verified-source",
        type=Path,
        default=prior.VERIFIED_SOURCE,
        help="round_summary.json containing the dynamically verified lemma memory",
    )
    args = parser.parse_args()
    output_root: Path = args.output_dir
    verified_source: Path = args.verified_source
    output_root.mkdir(parents=True, exist_ok=True)
    problem_id, problem = prior.load_problem()
    arguments = load_dynamic_verified_arguments(verified_source)
    lemmas = label_lemmas(arguments)
    dynamic_digest = sha256_text(json.dumps(lemmas, ensure_ascii=False, sort_keys=True))
    prior.write_json(
        output_root / "manifest.json",
        {
            "schema": "cognitive-well-v0.3.63-deterministic-lemma-appendix-manifest-v1",
            "created_at": prior.utc_now(),
            "harness_version": HARNESS_VERSION,
            "experiment": "main_proof_plus_deterministically_appended_used_lemma_bodies",
            "extraction_rerun": False,
            "lemma_content_hardcoded": False,
            "main_prompt_dynamic_fields": ["lemma_statement"],
            "main_prompt_excluded_fields": ["lemma_id", "proof", "qwen_audit"],
            "appendix_dynamic_fields": ["lemma_statement", "lemma_proof"],
            "appendix_selection": "exact_local_labels_cited_by_main_proof",
            "dynamic_verified_source": str(verified_source.resolve()),
            "dynamic_verified_source_sha256": hashlib.sha256(
                verified_source.read_bytes()
            ).hexdigest(),
            "dynamic_lemma_count": len(lemmas),
            "dynamic_lemmas_sha256": dynamic_digest,
            "local_labels": [row["label"] for row in lemmas],
            "constructive_model": {
                "model": base.GEMMA_MODEL,
                "dtype": "bfloat16",
                "mtp": 4,
                "endpoint": prior.GEMMA_ENDPOINT,
                "reasoning_effort": "max",
            },
            "reviewer_model": {
                "model": base.QWEN_MODEL,
                "role": "reviewer_1_earliest_break_non_scoring",
                "temperature": 0.2,
                "reasoning_effort": "max",
            },
            "codex_grader": {
                "model": prior.CODEX_MODEL,
                "reasoning_effort": prior.CODEX_REASONING_EFFORT,
                "blind_to_generation_and_qwen_metadata": True,
            },
            "configurations": CONFIGURATIONS,
            "terra_calls": 0,
            "gold_or_reference_accessed_by_composition": False,
        },
    )
    try:
        prior.write_json(
            output_root / "status.json",
            {"state": "running", "stage": "main_composition", "updated_at": prior.utc_now()},
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            candidates = list(
                executor.map(
                    lambda config: generate_candidate(
                        output_root=output_root,
                        problem=problem,
                        lemmas=lemmas,
                        config=config,
                    ),
                    CONFIGURATIONS,
                )
            )
        prior.write_json(
            output_root / "status.json",
            {"state": "running", "stage": "qwen_reviewer1", "candidate_count": 4, "updated_at": prior.utc_now()},
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            reviews = list(
                executor.map(
                    lambda candidate: reviewer1_with_cap_retry(
                        output_root=output_root, problem=problem, candidate=candidate
                    ),
                    candidates,
                )
            )
        prior.write_json(
            output_root / "status.json",
            {"state": "running", "stage": "codex_gold_scoring", "candidate_count": 4, "updated_at": prior.utc_now()},
        )
        reference = prior.REFERENCE_PATH.read_text(encoding="utf-8").strip()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            grades = list(
                executor.map(
                    lambda candidate: prior.codex_grade(
                        output_root=output_root,
                        problem_id=problem_id,
                        problem=problem,
                        reference=reference,
                        candidate=candidate,
                    ),
                    candidates,
                )
            )
        review_by_id = {row["candidate_id"]: row for row in reviews}
        grade_by_id = {row["candidate_id"]: row for row in grades}
        results = []
        for candidate in candidates:
            candidate_id = candidate["candidate_id"]
            results.append(
                {
                    "candidate_id": candidate_id,
                    "temperature": candidate["temperature"],
                    "replicate": candidate["replicate"],
                    "proof_sha256": candidate["proof_sha256"],
                    "assembly": candidate["assembly"],
                    "qwen_reviewer1": review_by_id[candidate_id]["review"],
                    "codex_grade": grade_by_id[candidate_id].get("grade"),
                    "codex_error": grade_by_id[candidate_id].get("error"),
                }
            )
        prior.write_json(
            output_root / "summary.json",
            {
                "schema": "cognitive-well-v0.3.63-deterministic-lemma-appendix-summary-v1",
                "state": "completed",
                "completed_at": prior.utc_now(),
                "harness_version": HARNESS_VERSION,
                "results": results,
                "terra_calls": 0,
            },
        )
        prior.write_json(
            output_root / "status.json",
            {"state": "completed", "stage": "codex_gold_scoring", "candidate_count": 4, "updated_at": prior.utc_now()},
        )
    except Exception as error:
        prior.write_json(
            output_root / "status.json",
            {
                "state": "failed",
                "stage": "exception",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": prior.utc_now(),
            },
        )
        raise


if __name__ == "__main__":
    main()
