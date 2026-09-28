from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from cognitive_well_harness_v0_3_36_p4_dual_block_replay_snapshot_20260822.cold_prompts import (
    dialectic_solver,
    lazy_phrasing,
)
from experiments.local_math_verifier.runtime import utc_now, write_json

from .protocol import (
    FUSION_SYSTEM_PROMPT,
    REWRITER_SYSTEM_PROMPT,
    rewriter_user_prompt,
    sha256_text,
)
from .runtime import RuntimeConfig, StageRuntime


def derived_seed(master_seed: int, replication: int, stage: str) -> int:
    material = f"v037:{master_seed}:{replication}:{stage}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def nonempty_parser(value: str) -> dict[str, Any]:
    errors = [] if value.strip() else ["generation is empty"]
    return {"valid": not errors, "errors": errors}


def run_replication(
    *,
    problem: str,
    replication: int,
    master_seed: int,
    output_dir: Path,
    runtime: StageRuntime,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Cold Stage 1, followed by exactly one Stage-2 review/fusion/rewrite."""

    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / "result.json"
    if final_path.is_file():
        return json.loads(final_path.read_text(encoding="utf-8"))

    def announce(stage: str) -> None:
        write_json(
            output_dir / "status.json",
            {"state": "running", "stage": stage, "updated_at": utc_now()},
        )
        if progress:
            progress(stage)

    # Stage 1: no critics and no fusion.
    stage1_dir = output_dir / "stage1_cold_generation"
    announce("stage1_draft")
    draft = runtime.gemma_call(
        output_dir=stage1_dir / "draft",
        name="cold_draft",
        system_prompt=dialectic_solver(problem, None),
        user_prompt="Solve the stated problem from scratch using no outside materials.",
        seed=derived_seed(master_seed, replication, "stage1_draft"),
        temperature=1.0,
        max_tokens=runtime.config.solver_max_tokens,
        parser=nonempty_parser,
    )
    draft_proof = str(draft["text"]).strip()

    announce("stage1_lazy_check")
    lazy = runtime.gemma_call(
        output_dir=stage1_dir / "lazy_check",
        name="lazy_check",
        system_prompt=lazy_phrasing(draft_proof),
        user_prompt="Scan the submitted proof now.",
        seed=derived_seed(master_seed, replication, "stage1_lazy_check"),
        temperature=0.1,
        max_tokens=runtime.config.lazy_max_tokens,
        parser=nonempty_parser,
    )
    lazy_report = str(lazy["text"]).strip()
    if lazy_report == "NO_ISSUES":
        checked_proof = draft_proof
        explicit = None
        explicit_called = False
    else:
        announce("stage1_explicit_resolve")
        explicit = runtime.gemma_call(
            output_dir=stage1_dir / "explicit_resolve",
            name="explicit_resolve",
            system_prompt=dialectic_solver(
                problem,
                None,
                feedback=(
                    "Derive explicitly and repair every valid issue in this scan:\n"
                    + lazy_report
                ),
            ),
            user_prompt="Re-solve the problem and return the complete repaired proof.",
            seed=derived_seed(master_seed, replication, "stage1_explicit_resolve"),
            temperature=1.0,
            max_tokens=runtime.config.solver_max_tokens,
            parser=nonempty_parser,
        )
        checked_proof = str(explicit["text"]).strip()
        explicit_called = True
    (stage1_dir / "checked_proof.md").write_text(
        checked_proof + "\n", encoding="utf-8"
    )
    write_json(
        stage1_dir / "summary.json",
        {
            "stage": 1,
            "scope": "cold_draft_lazy_check_optional_explicit_resolve",
            "draft_sha256": sha256_text(draft_proof),
            "lazy_report_sha256": sha256_text(lazy_report),
            "explicit_resolve_called": explicit_called,
            "checked_proof_sha256": sha256_text(checked_proof),
            "reference_solution_access": False,
        },
    )

    # Stage 2: exactly two final review blocks, Gemma fusion, Gemma rewrite.
    stage2_dir = output_dir / "stage2_review_fusion_rewrite"
    announce("stage2_opc_review")
    # Runtime executes the two isolated reviewers serially. GPT-OSS reasoning is
    # retained on disk but only its final block enters TwoBlockMaterials.
    materials = runtime.two_block_reviews(
        problem=problem,
        proof=checked_proof,
        output_dir=stage2_dir / "reviews",
        seed=derived_seed(master_seed, replication, "stage2_reviewers"),
    )

    announce("stage2_gemma_fusion")
    fusion = runtime.fuse_two_blocks(
        materials=materials,
        system_prompt=FUSION_SYSTEM_PROMPT,
        output_dir=stage2_dir / "fusion",
        seed=derived_seed(master_seed, replication, "stage2_gemma_fusion"),
    )

    announce("stage2_gemma_rewrite")
    rewrite_user = rewriter_user_prompt(
        materials=materials, fusion_report=str(fusion["text"]), stage=2
    )
    rewrite = runtime.gemma_call(
        output_dir=stage2_dir / "rewrite",
        name="gemma_proof_rewrite",
        system_prompt=REWRITER_SYSTEM_PROMPT,
        user_prompt=rewrite_user,
        seed=derived_seed(master_seed, replication, "stage2_gemma_rewrite"),
        temperature=0.2,
        max_tokens=runtime.config.rewrite_max_tokens,
        parser=nonempty_parser,
    )
    final_proof = str(rewrite["text"]).strip()
    (stage2_dir / "rewritten_proof.md").write_text(
        final_proof + "\n", encoding="utf-8"
    )

    result = {
        "schema": "cognitive-well-v037-stage12-replication-v1",
        "replication": replication,
        "master_seed": master_seed,
        "input_scope": "problem_statement_only",
        "stage1": {
            "explicit_resolve_called": explicit_called,
            "checked_proof_sha256": sha256_text(checked_proof),
        },
        "stage2": {
            "review_block_count": 2,
            "review_blocks": ["opc_final", "gptoss_final"],
            "gptoss_reasoning_in_fusion": False,
            "reviewers_may_score": False,
            "fusion": fusion["parsed"],
            "fusion_sha256": sha256_text(str(fusion["text"])),
            "rewritten_proof_sha256": sha256_text(final_proof),
        },
        "final_proof": final_proof,
        "reference_solution_access": False,
        "completed_at": utc_now(),
    }
    write_json(final_path, result)
    write_json(
        output_dir / "status.json",
        {"state": "completed", "stage": "stage2_gemma_rewrite", "updated_at": utc_now()},
    )
    if progress:
        progress("completed")
    return result


def run_stage2_from_checked_proof(
    *,
    problem: str,
    checked_proof: str,
    replication: int,
    master_seed: int,
    output_dir: Path,
    runtime: StageRuntime,
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Rerun only Stage 2 while preserving a frozen Stage-1 proof."""

    checked_proof = checked_proof.strip()
    if not checked_proof:
        raise ValueError("Stage-2 redo requires a nonempty checked proof")
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / "result.json"
    if final_path.is_file():
        return json.loads(final_path.read_text(encoding="utf-8"))

    def announce(stage: str) -> None:
        write_json(
            output_dir / "status.json",
            {"state": "running", "stage": stage, "updated_at": utc_now()},
        )
        if progress:
            progress(stage)

    (output_dir / "stage1_checked_proof_input.md").write_text(
        checked_proof + "\n", encoding="utf-8"
    )
    write_json(
        output_dir / "stage1_input_identity.json",
        {
            "checked_proof_sha256": sha256_text(checked_proof),
            "source": "frozen_prior_stage1_checked_proof",
        },
    )

    announce("stage2_opc_review")
    materials = runtime.two_block_reviews(
        problem=problem,
        proof=checked_proof,
        output_dir=output_dir / "reviews",
        seed=derived_seed(master_seed, replication, "stage2_reviewers"),
    )
    announce("stage2_gemma_fusion")
    fusion = runtime.fuse_two_blocks(
        materials=materials,
        system_prompt=FUSION_SYSTEM_PROMPT,
        output_dir=output_dir / "fusion",
        seed=derived_seed(master_seed, replication, "stage2_gemma_fusion"),
    )
    announce("stage2_gemma_rewrite")
    rewrite = runtime.gemma_call(
        output_dir=output_dir / "rewrite",
        name="gemma_proof_rewrite",
        system_prompt=REWRITER_SYSTEM_PROMPT,
        user_prompt=rewriter_user_prompt(
            materials=materials, fusion_report=str(fusion["text"]), stage=2
        ),
        seed=derived_seed(master_seed, replication, "stage2_gemma_rewrite"),
        temperature=0.2,
        max_tokens=runtime.config.rewrite_max_tokens,
        parser=nonempty_parser,
    )
    final_proof = str(rewrite["text"]).strip()
    (output_dir / "rewritten_proof.md").write_text(
        final_proof + "\n", encoding="utf-8"
    )
    result = {
        "schema": "cognitive-well-v037-stage2-only-redo-v1",
        "replication": replication,
        "master_seed": master_seed,
        "stage1_checked_proof_sha256": sha256_text(checked_proof),
        "review_block_count": 2,
        "review_blocks": ["opc_final", "gptoss_final"],
        "gptoss_reasoning_in_fusion": False,
        "reviewers_may_score": False,
        "fusion": fusion["parsed"],
        "fusion_sha256": sha256_text(str(fusion["text"])),
        "final_proof": final_proof,
        "final_proof_sha256": sha256_text(final_proof),
        "reference_solution_access": False,
        "completed_at": utc_now(),
    }
    write_json(final_path, result)
    write_json(
        output_dir / "status.json",
        {"state": "completed", "stage": "stage2_gemma_rewrite", "updated_at": utc_now()},
    )
    if progress:
        progress("completed")
    return result


def run_replications(
    *,
    problem: str,
    replications: int,
    master_seed: int,
    output_dir: Path,
    config: RuntimeConfig,
    progress: Callable[[int, str], None] | None = None,
) -> list[dict[str, Any]]:
    if replications < 1:
        raise ValueError("replications must be positive")
    runtime = StageRuntime(config)
    results = []
    # Serial orchestration makes the one-GPU stochastic trajectory explicit and
    # avoids inter-replication scheduling as an uncontrolled variable.
    for replication in range(1, replications + 1):
        results.append(
            run_replication(
                problem=problem,
                replication=replication,
                master_seed=master_seed,
                output_dir=output_dir / f"replication_{replication:02d}",
                runtime=runtime,
                progress=(
                    (lambda stage, index=replication: progress(index, stage))
                    if progress
                    else None
                ),
            )
        )
    return results
