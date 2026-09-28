from __future__ import annotations

import concurrent.futures
import copy
import hashlib
import json
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterator

from cognitive_well_harness_v0_3_32_clean_terra_metadata_20260819 import (
    pipeline as clean_terra_pipeline,
)
from cognitive_well_harness_v0_3_33_terra_structural_phase1_refinement_20260819 import (
    pipeline as previous_pipeline,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    verification as implementation_verification,
)

from .contracts import (
    ARTIFACT_SCHEMA_VERSION,
    GEMMA_MODEL,
    HARNESS_VERSION,
    PHASE_ONE_ROUTE_COUNT,
    PHASE_ONE_WIDTH,
    PROMOTION_PROFILE,
    TERRA_MODEL,
    PhaseOneFeedbackConfig,
    validate_promoted_profile,
)
from .cap_recovery import cap_recovering_gemma_text
from .feedback_runtime import PhaseOneFeedbackRuntime
from .protocol import (
    ThreeBlockMaterials,
    assert_frozen_prompts,
    sha256_text,
)


implementation_pipeline = previous_pipeline.implementation_pipeline
implementation_contracts = previous_pipeline.implementation_contracts
PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
BASE_PACKAGE = (
    REPO_ROOT
    / "cognitive_well_harness_v0_3_33_terra_structural_phase1_refinement_20260819"
)
PINNED_BASE_FILES = (
    "__init__.py",
    "contracts.py",
    "pipeline.py",
    "run.py",
    "schemas/terra_phase_one_refinement.schema.json",
    "schemas/terra_phase_one_final_score.schema.json",
    "schemas/terra_phase_one_anchor_tiebreak.schema.json",
    "schemas/terra_phase_one_supplement_comparison.schema.json",
)
EXPECTED_BASE_IMPLEMENTATION_SHA256 = (
    "3f3497095cbd759596ebf4300f2635ff3d55c67e5198164c9840b927c3ab8b18"
)


def base_implementation_sha256() -> str:
    digest = hashlib.sha256()
    for relative in PINNED_BASE_FILES:
        path = BASE_PACKAGE / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned v0.3.33 implementation file: {path}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def assert_frozen_base() -> dict[str, Any]:
    recursive_base = previous_pipeline.assert_frozen_base()
    observed = base_implementation_sha256()
    if observed != EXPECTED_BASE_IMPLEMENTATION_SHA256:
        raise RuntimeError(
            "v0.3.35 frozen v0.3.33 implementation changed: "
            f"expected {EXPECTED_BASE_IMPLEMENTATION_SHA256}, observed {observed}"
        )
    return {
        "package": BASE_PACKAGE.name,
        "sha256": observed,
        "files": list(PINNED_BASE_FILES),
        "recursive_base": recursive_base,
        "frozen_protocol_prompts": assert_frozen_prompts(),
        "phase_one_replacement": {
            "replaced_stage": "v0.3.33_terra_structural_draft_refinement",
            "draft_author": "phase1_route_gemma4_bf16_mtp4",
            "lazy_derivation_cleanup": "inherited_v0.3.33",
            "review_layout": "split_gptoss_three_slot",
            "local_critic": "OPC-R1-8B_complete_report",
            "whole_proof_grader": "gpt-oss_final_after_end_thinking",
            "adversarial_checker": "gpt-oss_reasoning_through_end_thinking",
            "diagnosis_fusion": "Qwen/Qwen3.6-27B",
            "repair_architect": "Qwen/Qwen3.6-27B",
            "proof_rewriter": "phase1_route_gemma4_bf16_mtp4",
            "proof_rewriter_model": GEMMA_MODEL,
            "gemma_service_profile": {
                "dtype": "bfloat16",
                "kv_cache_dtype": "bfloat16",
                "max_model_len": 262_144,
                "max_num_batched_tokens": 8_192,
                "max_num_seqs": 4,
                "gpu_memory_utilization": 0.95,
                "mtp_speculative_tokens": 4,
            },
            "gemma_draft_sampling": {
                "temperature": 1.0,
                "max_tokens": 65_536,
            },
            "gemma_lazy_check_sampling": {
                "temperature": 0.1,
                "max_tokens": 8_192,
            },
            "gemma_rewriter_sampling": {
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 64,
                "max_tokens": 65_536,
            },
            "cap_exhaustion_recovery": {
                "policy": "reuse_partial_then_continue_once_at_double_cap",
                "opc": [8_000, 16_000],
                "gptoss": [16_000, 32_000],
                "qwen": [12_000, 24_000],
                "gemma_draft_and_rewrite": [65_536, 131_072],
                "gemma_lazy_check": [8_192, 16_384],
            },
            "qwen_may_author_final_proof": False,
            "repair_call_policy": "only_when_fusion_status_required",
            "rewrite_call_policy": "only_after_valid_required_repair_handoff",
            "post_rewrite_grade_call": False,
            "authoritative_final_score": (
                "fresh_OPC_plus_split_GPTOSS_three_block_Qwen3.6_fusion"
            ),
            "authoritative_rank_fields": ["qwen_final_grade"],
            "hypothesis_seed_value": False,
            "terra_final_proof_scoring": False,
            "selection_comparisons": (
                "inherited_Terra_semantic_tiebreak_and_complementarity_only"
            ),
            "phase_two_and_three": "inherited_v0.3.33",
        },
    }


def phase_one_source_request(*, problem: str, proof: str) -> str:
    return (
        implementation_pipeline.inquisitorial_grader(problem, proof, None)
        + implementation_pipeline.EXECUTION_DISCIPLINE
    )


def phase_one_grading_rubric(source_request: str) -> str:
    marker = "\nPROBLEM OR STANDALONE CLAIM:\n"
    if source_request.count(marker) != 1:
        raise ValueError("Phase-1 grading source has an ambiguous problem boundary")
    rubric = source_request.split(marker, 1)[0].strip()
    if not rubric or "Do not assign 5" not in rubric:
        raise ValueError("Phase-1 grading rubric extraction failed")
    return rubric


def _review_rows_from_disk(
    *, path: Path, checked: list[dict[str, Any]], problem: str
) -> list[dict[str, Any]] | None:
    if not path.is_file():
        return None
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != len(checked):
        return None
    expected_by_index = {
        int(row["index"]): sha256_text(str(row["proof"])) for row in checked
    }
    for row in rows:
        index = int(row.get("index", -1))
        identity = row.get("identity") or {}
        if (
            identity.get("problem_sha256") != sha256_text(problem)
            or identity.get("candidate_proof_sha256")
            != expected_by_index.get(index)
            or row.get("review_layout") != "split_gptoss_three_slot"
        ):
            return None
    return rows


def phase_one_qwen_feedback_solve(
    *,
    problem: str,
    context: Any,
    count: int,
    engine: Any,
    stage_dir: Path,
    stage_name: str,
    feedback_runtime: PhaseOneFeedbackRuntime,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
) -> list[dict[str, Any]]:
    """Gemma draft -> three reviews -> Qwen feedback -> Gemma rewrite."""

    del grader_max_tokens
    if context not in (None, [], {}):
        raise ValueError("Phase 1 requires zero context; refusing to discard materials")
    stage_dir.mkdir(parents=True, exist_ok=True)
    final_path = stage_dir / "solutions.json"
    if final_path.exists():
        return json.loads(final_path.read_text(encoding="utf-8"))

    v027 = implementation_pipeline.v027

    def make_drafts() -> list[dict[str, Any]]:
        def one(index: int) -> dict[str, Any]:
            response = engine.text(
                prompt=previous_pipeline.phase_one_solver_prompt(problem=problem),
                namespace=f"{v027.safe_key(stage_name)}_draft",
                index=index,
                temperature=1.0,
                max_tokens=solver_max_tokens,
            )
            return {"index": index, "proof": response["final"], "response": response}

        return v027.parallel_map(one, range(count), engine.concurrency)

    drafts = v027.load_or_compute(stage_dir / "drafts.json", make_drafts)

    def check_lazy() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            response = engine.text(
                prompt=v027.lazy_phrasing(str(row["proof"])),
                namespace=f"{v027.safe_key(stage_name)}_lazy",
                index=index,
                temperature=0.1,
                max_tokens=lazy_max_tokens,
            )
            report = response["final"].strip()
            return {
                "index": index,
                "report": report,
                "has_lazy_phrasing": report != "NO_ISSUES",
                "response": response,
            }

        return v027.parallel_map(one, drafts, engine.concurrency)

    lazy_rows = v027.load_or_compute(stage_dir / "lazy_checks.json", check_lazy)
    lazy_by_index = {int(row["index"]): row for row in lazy_rows}

    def repair_lazy() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            lazy = lazy_by_index[index]
            if not lazy["has_lazy_phrasing"]:
                return {
                    "index": index,
                    "proof": row["proof"],
                    "re_solved": False,
                    "lazy_report": lazy["report"],
                }
            response = engine.text(
                prompt=previous_pipeline.phase_one_solver_prompt(
                    problem=problem,
                    feedback=(
                        "Derive explicitly. Repair every issue in this report:\n"
                        + lazy["report"]
                    ),
                ),
                namespace=f"{v027.safe_key(stage_name)}_explicit_resolve",
                index=index,
                temperature=1.0,
                max_tokens=solver_max_tokens,
            )
            return {
                "index": index,
                "proof": response["final"],
                "re_solved": True,
                "lazy_report": lazy["report"],
                "response": response,
            }

        return v027.parallel_map(one, drafts, engine.concurrency)

    checked = v027.load_or_compute(stage_dir / "checked_drafts.json", repair_lazy)

    reviews_path = stage_dir / "three_block_reviews.json"
    review_rows = _review_rows_from_disk(
        path=reviews_path, checked=checked, problem=problem
    )
    if review_rows is None:
        def review_one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            proof = str(row["proof"])
            source_request = phase_one_source_request(problem=problem, proof=proof)
            grading_rubric = phase_one_grading_rubric(source_request)
            call_dir = stage_dir / "three_block_feedback" / f"candidate_{index + 1}"
            generated = feedback_runtime.generate_three_block_reviews(
                problem=problem,
                proof=proof,
                grading_rubric=grading_rubric,
                source_prompt=source_request,
                output_dir=call_dir / "independent_reviews",
                seed=engine.seed(f"{stage_name}_reviewers", index),
            )
            return {
                "index": index,
                "materials": asdict(generated["materials"]),
                "identity": generated["identity"],
                "component_metadata": generated["component_metadata"],
                "review_layout": "split_gptoss_three_slot",
                "artifact_dir": str(call_dir.resolve()),
            }

        review_rows = v027.parallel_map(review_one, checked, engine.concurrency)
        implementation_pipeline.write_json(reviews_path, review_rows)
    review_by_index = {int(row["index"]): row for row in review_rows}

    def fuse_all() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            review = review_by_index[index]
            materials = ThreeBlockMaterials(**review["materials"])
            call_dir = Path(review["artifact_dir"])
            fusion = feedback_runtime.fuse(
                materials=materials,
                output_dir=call_dir,
                seed=(engine.seed(f"{stage_name}_qwen_fusion", index)),
            )
            return {
                "index": index,
                "report": fusion["report"],
                "parsed": fusion["parsed"],
                "metadata": fusion["metadata"],
                "artifact_dir": review["artifact_dir"],
            }

        return v027.parallel_map(one, checked, engine.concurrency)

    fusion_rows = fuse_all()
    implementation_pipeline.write_json(
        stage_dir / "qwen_fusion_diagnoses.json", fusion_rows
    )
    fusion_by_index = {int(row["index"]): row for row in fusion_rows}

    def resolve_conditionally() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            review = review_by_index[index]
            materials = ThreeBlockMaterials(**review["materials"])
            fusion = fusion_by_index[index]
            parsed = fusion["parsed"]
            status = parsed["repair_status"]
            if status == "NOT REQUIRED":
                return {
                    "index": index,
                    "proof": row["proof"],
                    "refinement_mode": "preserve_qwen_no_repair",
                    "refinement_invoked": False,
                    "repair": None,
                    "rewrite": None,
                }
            if status != "REQUIRED":
                raise RuntimeError(f"unexpected Qwen repair status: {status!r}")
            accepted_ids = list(parsed["accepted_defect_ids"])
            call_dir = Path(review["artifact_dir"])
            repair = feedback_runtime.propose_repair(
                materials=materials,
                diagnosis=str(fusion["report"]),
                accepted_ids=accepted_ids,
                output_dir=call_dir,
                seed=(
                    engine.seed(f"{stage_name}_qwen_repair", index) ^ 0x5A17C0DE
                )
                & 0xFFFFFFFF,
            )
            rewrite = feedback_runtime.rewrite_with_gemma(
                materials=materials,
                diagnosis=str(fusion["report"]),
                repair=str(repair["report"]),
                engine=engine,
                output_dir=call_dir,
                seed=(
                    engine.seed(f"{stage_name}_gemma_rewriter", index) ^ 0xA11CE5ED
                )
                & 0xFFFFFFFF,
                max_tokens=solver_max_tokens,
            )
            return {
                "index": index,
                "proof": rewrite["proof"],
                "refinement_mode": "qwen36_feedback_gemma4_rewrite",
                "refinement_invoked": True,
                "repair": repair,
                "rewrite": rewrite,
            }

        return v027.parallel_map(one, checked, engine.concurrency)

    resolved = resolve_conditionally()
    implementation_pipeline.write_json(
        stage_dir / "conditionally_rewritten.json", resolved
    )
    checked_by_index = {int(row["index"]): row for row in checked}
    solutions: list[dict[str, Any]] = []
    for row in sorted(resolved, key=lambda item: int(item["index"])):
        index = int(row["index"])
        fusion = fusion_by_index[index]
        repair = row["repair"]
        solutions.append(
            {
                "solution_id": f"{stage_name}.s{index + 1}",
                "proof": row["proof"],
                "refinement_mode": row["refinement_mode"],
                "refinement_invoked": row["refinement_invoked"],
                "post_refinement_score_only_regrade": False,
                "qwen_fusion_diagnosis": fusion["parsed"],
                "qwen_fusion_report_sha256": sha256_text(str(fusion["report"])),
                "qwen_repair_proposal": repair["parsed"] if repair else None,
                "qwen_repair_report_sha256": (
                    sha256_text(str(repair["report"])) if repair else None
                ),
                "proof_rewriter": (
                    "phase1_route_gemma4_bf16_mtp4"
                    if row["refinement_invoked"]
                    else None
                ),
                "review_layout": "split_gptoss_three_slot",
                "feedback_artifact_dir": review_by_index[index]["artifact_dir"],
                "review_identity": review_by_index[index]["identity"],
                "lazy_report": checked_by_index[index]["lazy_report"],
                "lazy_re_solved": checked_by_index[index]["re_solved"],
                "context_supplied": False,
            }
        )
    implementation_pipeline.write_json(final_path, solutions)
    return solutions


def run_phase_one_qwen_feedback(
    *,
    problem: str,
    engines: tuple[Any, ...],
    output_dir: Path,
    width: int,
    feedback_runtime: PhaseOneFeedbackRuntime,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
    reuse_source_dirs: tuple[Path, ...] | None = None,
    reuse_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if reuse_source_dirs is not None:
        if not reuse_records or len(reuse_records) != PHASE_ONE_ROUTE_COUNT:
            raise ValueError(
                f"validated reuse records are required for all {PHASE_ONE_ROUTE_COUNT} routes"
            )
        implementation_pipeline.materialize_phase_one_reuse(
            source_dirs=reuse_source_dirs,
            reuse_records=reuse_records,
            output_dir=output_dir,
        )
    if len(engines) != PHASE_ONE_ROUTE_COUNT:
        raise ValueError(
            f"Phase 1 requires {PHASE_ONE_ROUTE_COUNT} route-specific engines"
        )

    def run_route(index: int) -> list[dict[str, Any]]:
        return phase_one_qwen_feedback_solve(
            problem=problem,
            context=None,
            count=width,
            engine=engines[index],
            stage_dir=output_dir / f"route_{index + 1}" / "zero_context",
            stage_name=f"phase1_route{index + 1}",
            feedback_runtime=feedback_runtime,
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        routes = list(executor.map(run_route, range(PHASE_ONE_ROUTE_COUNT)))
    if any(len(rows) != width for rows in routes):
        raise RuntimeError(
            f"Phase 1 did not return width-four output on all {PHASE_ONE_ROUTE_COUNT} routes"
        )

    merged: list[dict[str, Any]] = []
    for route_index, rows in enumerate(routes, start=1):
        for row in rows:
            merged.append(
                {
                    **row,
                    "candidate_id": f"phase1.r{route_index}.{row['solution_id']}",
                    "phase_one_route": route_index,
                    "family": "phase1_zero_context",
                    "body": row["proof"],
                    "assembled_proof": row["proof"],
                    "terra_screen_passed": False,
                    "terra_unanimously_confirmed": False,
                }
            )
    implementation_pipeline.write_json(output_dir / "merged_candidates.json", merged)
    return merged


def stable_feedback_seed(master_seed: int, namespace: str) -> int:
    material = f"{master_seed}:{namespace}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def validate_phase_one_qwen_final_score(value: dict[str, Any]) -> None:
    if set(value) != {"score"}:
        raise ValueError("Qwen final-proof score must contain exactly score")
    score = value["score"]
    if isinstance(score, bool) or not isinstance(score, int):
        raise ValueError("Qwen final-proof score must be an integer")
    if score not in {0, 1, 2, 3, 4, 6, 7}:
        raise ValueError("Qwen final-proof score must use the IMO scale without 5")


def qwen_final_score(candidate: dict[str, Any]) -> int:
    value = candidate.get("phase_one_qwen_final_score")
    if not isinstance(value, dict):
        raise ValueError(
            "Phase-1 candidate lacks its Qwen final-proof score: "
            f"{candidate.get('candidate_id')}"
        )
    validate_phase_one_qwen_final_score(value)
    return int(value["score"])


def phase_one_qwen_rank(candidate: dict[str, Any]) -> tuple[int, str]:
    return qwen_final_score(candidate), str(candidate.get("candidate_id") or "")


def phase_one_qwen_runtime_rank(
    candidate: dict[str, Any],
) -> tuple[int, int, float, str]:
    return (
        int(bool(candidate.get("terra_unanimously_confirmed"))),
        int(
            implementation_contracts.global_audit_passed(
                candidate.get("final_global_audit")
            )
        ),
        float(qwen_final_score(candidate)),
        str(candidate.get("candidate_id") or ""),
    )


def score_phase_one_candidates_with_qwen_feedback(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
    feedback_runtime: PhaseOneFeedbackRuntime,
    master_seed: int,
) -> list[dict[str, Any]]:
    """Freshly re-review every final proof; Terra is not a scorer here."""

    del terra_model
    # v0.3.28 supplies a legacy path named terra_scoring. Keep the inherited
    # orchestrator untouched while placing the new artifacts under a truthful
    # backend-specific directory.
    if output_dir.name == "terra_scoring":
        output_dir = output_dir.parent / "qwen_final_scoring"

    def score(candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate["candidate_id"])
        proof = str(candidate["assembled_proof"])
        candidate_dir = output_dir / candidate_id
        source_request = phase_one_source_request(problem=problem, proof=proof)
        rubric = phase_one_grading_rubric(source_request)
        reviewed = feedback_runtime.generate_three_block_reviews(
            problem=problem,
            proof=proof,
            grading_rubric=rubric,
            source_prompt=source_request,
            output_dir=candidate_dir / "independent_reviews",
            seed=stable_feedback_seed(
                master_seed, f"phase1-final-review:{candidate_id}"
            ),
        )
        fusion = feedback_runtime.fuse(
            materials=reviewed["materials"],
            output_dir=candidate_dir,
            seed=stable_feedback_seed(
                master_seed, f"phase1-final-qwen-fusion:{candidate_id}"
            ),
        )
        parsed = fusion["parsed"]
        score_value = {"score": int(parsed["score"])}
        validate_phase_one_qwen_final_score(score_value)
        implementation_pipeline.write_json(candidate_dir / "score.json", score_value)
        return {
            **candidate,
            "phase_one_qwen_final_score": score_value,
            "phase_one_qwen_final_verdict": parsed["verdict"],
            "phase_one_qwen_final_diagnosis_sha256": sha256_text(
                str(fusion["report"])
            ),
            "phase_one_qwen_final_review_identity": reviewed["identity"],
            "phase_one_qwen_final_artifact_dir": str(candidate_dir.resolve()),
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        scored = list(executor.map(score, candidates))
    implementation_pipeline.write_json(
        output_dir / "summary.json",
        {
            "scorer": feedback_runtime.config.qwen_model,
            "scoring_pipeline": "OPC_plus_split_GPTOSS_three_block_Qwen3.6_fusion",
            "independent_final_proof_reviews": True,
            "review_layout": "split_gptoss_three_slot",
            "candidate_identity_model_visible": False,
            "gemma_grades_visible": False,
            "terra_scoring_calls": 0,
            "hypothesis_seed_value_present": False,
            "model_output_fields_used_for_ranking": ["score"],
            "authoritative_score_field": "phase_one_qwen_final_score",
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "phase_one_route": row.get("phase_one_route"),
                    "score": row["phase_one_qwen_final_score"]["score"],
                }
                for row in scored
            ],
        },
    )
    return scored


def select_top_two_per_phase_one_route_qwen(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_route: dict[int, list[dict[str, Any]]] = {
        route: [] for route in range(1, PHASE_ONE_ROUTE_COUNT + 1)
    }
    for candidate in candidates:
        route = implementation_pipeline.phase_one_route(candidate)
        if route in by_route:
            by_route[route].append(candidate)
    incomplete = [route for route, rows in by_route.items() if len(rows) < 2]
    if incomplete:
        raise ValueError(f"fewer than two Phase-1 candidates for routes: {incomplete}")
    finalists: list[dict[str, Any]] = []
    for route in range(1, PHASE_ONE_ROUTE_COUNT + 1):
        finalists.extend(
            sorted(by_route[route], key=phase_one_qwen_rank, reverse=True)[:2]
        )
    return finalists


def qwen_quality_anchor_prompt(
    *, problem: str, tied_packets: list[dict[str, Any]]
) -> str:
    return f"""You are an olympiad proof anchor adjudicator. {previous_pipeline.implementation_prompts.FIREWALL}

The supplied proofs received exactly the same independent Qwen final-proof grade.
Select the mathematically strongest proof. Each proof has a temporary local index.

Compare complete proof quality in this order: logical soundness and completeness;
strength of the central characterization; coverage of both directions and boundary
cases; and clarity only as the final mathematical tiebreak. Do not repair a proof,
author hypotheses, or prefer wording over substance. Return only the temporary
anchor index required by the schema.

PROBLEM:
{problem}

EXACTLY SCORE-TIED PROOFS:
{json.dumps(tied_packets, ensure_ascii=False)}
"""


def select_qwen_quality_anchor(
    *,
    problem: str,
    finalists: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    best_score = max(qwen_final_score(row) for row in finalists)
    tied_indices = [
        index
        for index, row in enumerate(finalists)
        if qwen_final_score(row) == best_score
    ]
    comparison_invoked = len(tied_indices) > 1
    if comparison_invoked:
        packets = [
            {
                "candidate_index": local_index,
                "proof": finalists[finalist_index]["assembled_proof"],
            }
            for local_index, finalist_index in enumerate(tied_indices)
        ]

        def validate(result: dict[str, Any]) -> None:
            previous_pipeline.validate_phase_one_anchor_tiebreak(
                result, tied_count=len(tied_indices)
            )

        choice = previous_pipeline.terra_json_call(
            prompt=qwen_quality_anchor_prompt(problem=problem, tied_packets=packets),
            schema_path=previous_pipeline.PHASE_ONE_ANCHOR_TIEBREAK_SCHEMA,
            call_root=output_dir,
            stem="anchor_tiebreak",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=validate,
        )
        anchor_index = tied_indices[int(choice["anchor_index"])]
        mode = "semantic_tiebreak_after_equal_qwen_grade"
        rationale = (
            "The highest Qwen final-proof grade was tied, so an isolated semantic "
            "comparison selected the strongest anchor."
        )
    else:
        anchor_index = tied_indices[0]
        mode = "unique_highest_qwen_grade"
        rationale = "Unique highest Qwen final-proof grade."
    audit = {
        "mode": mode,
        "rank_fields": ["qwen_final_grade"],
        "score": best_score,
        "tied_candidate_ids": [
            str(finalists[index]["candidate_id"]) for index in tied_indices
        ],
        "selected_candidate_id": str(finalists[anchor_index]["candidate_id"]),
        "semantic_comparison_invoked": comparison_invoked,
        "semantic_comparison_model": terra_model if comparison_invoked else None,
        "model_output_fields": ["anchor_index"] if comparison_invoked else [],
    }
    implementation_pipeline.write_json(
        output_dir / "anchor_selection_bound.json", audit
    )
    return {"anchor_index": anchor_index, "rationale": rationale, "audit": audit}


def select_qwen_quality_supplement(
    *,
    finalists: list[dict[str, Any]],
    anchor_index: int,
    model_audit: dict[str, Any],
) -> dict[str, Any]:
    previous_pipeline.validate_phase_one_supplement_matrix(
        model_audit,
        finalist_count=len(finalists),
        anchor_index=anchor_index,
    )
    assessment_by_index = {
        int(row["candidate_index"]): row
        for row in model_audit["candidate_assessments"]
    }
    alternatives = sorted(assessment_by_index)
    eligible = [
        index for index in alternatives if qwen_final_score(finalists[index]) in (6, 7)
    ]
    if eligible:
        eligibility_mode = "qwen_score_6_or_7_correctness_floor"
    else:
        highest = max(qwen_final_score(finalists[index]) for index in alternatives)
        eligible = [
            index
            for index in alternatives
            if qwen_final_score(finalists[index]) == highest
        ]
        eligibility_mode = "highest_remaining_qwen_score_fallback"

    def rank(index: int) -> tuple[int, int, int]:
        return (
            previous_pipeline.phase_one_complementarity_score(
                assessment_by_index[index]
            ),
            qwen_final_score(finalists[index]),
            -index,
        )

    supplement_index = max(eligible, key=rank)
    assessment = assessment_by_index[supplement_index]
    return {
        "supplement_index": supplement_index,
        "eligibility_mode": eligibility_mode,
        "eligible_indices": eligible,
        "complementarity_score": (
            previous_pipeline.phase_one_complementarity_score(assessment)
        ),
        "positive_axes": [
            axis
            for axis in previous_pipeline.PHASE_ONE_COMPLEMENTARITY_AXES
            if int(assessment[axis]) == 1
        ],
        "assessment_by_index": assessment_by_index,
    }


def select_diversified_phase_one_candidates_qwen(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    finalists = select_top_two_per_phase_one_route_qwen(candidates)
    expected_count = PHASE_ONE_ROUTE_COUNT * 2
    if len(finalists) != expected_count:
        raise ValueError(
            f"Phase-1 selector requires exactly {expected_count} finalists"
        )
    anchor = select_qwen_quality_anchor(
        problem=problem,
        finalists=finalists,
        output_dir=output_dir,
        terra_model=terra_model,
    )
    anchor_index = int(anchor["anchor_index"])
    model_audit = previous_pipeline.run_phase_one_supplement_comparisons(
        problem=problem,
        finalists=finalists,
        anchor_index=anchor_index,
        output_dir=output_dir,
        terra_model=terra_model,
    )
    supplement = select_qwen_quality_supplement(
        finalists=finalists,
        anchor_index=anchor_index,
        model_audit=model_audit,
    )
    supplement_index = int(supplement["supplement_index"])
    bound_assessments = []
    for index, finalist in enumerate(finalists):
        if index == anchor_index:
            values = {
                axis: 0 for axis in previous_pipeline.PHASE_ONE_COMPLEMENTARITY_AXES
            }
            source = "fixed_anchor_baseline"
        else:
            values = supplement["assessment_by_index"][index]
            source = "terra_binary_comparison"
        bound_assessments.append(
            {
                "candidate_id": finalist["candidate_id"],
                **{
                    axis: int(values[axis])
                    for axis in previous_pipeline.PHASE_ONE_COMPLEMENTARITY_AXES
                },
                "complementarity_score": sum(
                    int(values[axis])
                    for axis in previous_pipeline.PHASE_ONE_COMPLEMENTARITY_AXES
                ),
                "assessment_source": source,
            }
        )
    highest_score = max(qwen_final_score(row) for row in finalists)
    eligible_anchor_ids = [
        str(row["candidate_id"])
        for row in finalists
        if qwen_final_score(row) == highest_score
    ]
    audit = {
        "anchor_candidate_id": finalists[anchor_index]["candidate_id"],
        "supplement_candidate_id": finalists[supplement_index]["candidate_id"],
        "candidate_assessments": bound_assessments,
        "anchor_rationale": anchor["rationale"],
        "anchor_selection": anchor["audit"],
        "supplement_selection": {
            "policy": "binary_complementarity_with_qwen_correctness_floor",
            "binary_axes": list(previous_pipeline.PHASE_ONE_COMPLEMENTARITY_AXES),
            "eligibility_mode": supplement["eligibility_mode"],
            "eligible_candidate_ids": [
                str(finalists[index]["candidate_id"])
                for index in supplement["eligible_indices"]
            ],
            "rank_fields": [
                "complementarity_score",
                "qwen_final_grade",
                "stable_local_index",
            ],
            "selected_candidate_id": finalists[supplement_index]["candidate_id"],
            "selected_complementarity_score": supplement["complementarity_score"],
            "independent_model_calls": len(finalists) - 1,
            "candidate_identity_model_visible": False,
            "model_output_fields": list(
                previous_pipeline.PHASE_ONE_COMPLEMENTARITY_AXES
            ),
        },
        "complementarity_axes": supplement["positive_axes"],
        "external_information_used": False,
    }
    implementation_pipeline.write_json(output_dir / "selection_bound.json", audit)
    return {
        "finalists": finalists,
        "eligible_anchor_ids": eligible_anchor_ids,
        "selected": [finalists[anchor_index], finalists[supplement_index]],
        "audit": audit,
    }


def extract_iteration_hypotheses_qwen(
    *, original_extract_iteration: Any, **kwargs: Any
) -> dict[str, Any]:
    qwen_by_id = {
        str(row.get("candidate_id") or ""): dict(row["phase_one_qwen_final_score"])
        for row in kwargs.get("pool") or []
        if isinstance(row.get("phase_one_qwen_final_score"), dict)
    }
    original_extract = implementation_pipeline.v027.extract_hypotheses

    def qwen_seed_extract(**extract_kwargs: Any) -> dict[str, Any]:
        seeds = []
        for seed in extract_kwargs.get("seed_solutions") or []:
            candidate_id = str(seed.get("solution_id") or "")
            qwen_score = qwen_by_id.get(candidate_id)
            if qwen_score is None:
                seeds.append(seed)
            else:
                seeds.append(
                    {
                        **{key: value for key, value in seed.items() if key != "grade"},
                        "phase_one_qwen_final_score": qwen_score,
                    }
                )
        return original_extract(**{**extract_kwargs, "seed_solutions": seeds})

    implementation_pipeline.v027.extract_hypotheses = qwen_seed_extract
    try:
        result = original_extract_iteration(**kwargs)
    finally:
        implementation_pipeline.v027.extract_hypotheses = original_extract

    iteration = int(kwargs.get("iteration", 0))
    if iteration == 1:
        selection_path = Path(kwargs["output_dir"]) / "iteration1_seed_selection.json"
        if selection_path.is_file():
            selection = json.loads(selection_path.read_text(encoding="utf-8"))
            selected_ids = [str(value) for value in selection.get("candidate_ids") or []]
            selection.pop("terra_scores", None)
            selection["qwen_final_grades"] = [
                qwen_by_id.get(candidate_id, {}).get("score")
                for candidate_id in selected_ids
            ]
            selection["policy"] = "qwen_best_anchor_then_diversified_supplement"
            implementation_pipeline.write_json(selection_path, selection)
    return result


@contextmanager
def qwen_feedback_phase_one_backend(
    *,
    scoring_model: str,
    feedback_runtime: PhaseOneFeedbackRuntime,
    master_seed: int,
) -> Iterator[None]:
    """Replace v0.3.33's refinement and final-proof scoring boundaries."""

    base_extract_iteration = implementation_pipeline.extract_iteration_hypotheses
    with previous_pipeline.structural_phase_one_backend(scoring_model):
        original_pipeline_model = implementation_pipeline.MODEL
        original_verification_model = implementation_verification.MODEL
        original_run_phase_one = implementation_pipeline.run_phase_one
        original_score_phase_one = (
            implementation_pipeline.score_phase_one_candidates_with_terra
        )
        original_diversity = (
            implementation_pipeline.select_diversified_phase_one_candidates
        )
        original_top_two = implementation_pipeline.select_top_two_per_phase_one_route
        original_candidate_rank = implementation_contracts.candidate_rank
        original_extract_iteration = implementation_pipeline.extract_iteration_hypotheses
        original_manifest_writer = implementation_pipeline.write_or_validate_manifest
        original_write_progress = implementation_pipeline.write_progress
        original_engine_text = implementation_verification.EndpointModelEngine.text

        def bound_run_phase_one(**kwargs: Any) -> list[dict[str, Any]]:
            return run_phase_one_qwen_feedback(
                **kwargs,
                feedback_runtime=feedback_runtime,
            )

        def bound_score_phase_one(**kwargs: Any) -> list[dict[str, Any]]:
            return score_phase_one_candidates_with_qwen_feedback(
                **kwargs,
                feedback_runtime=feedback_runtime,
                master_seed=master_seed,
            )

        def bound_candidate_rank(
            candidate: dict[str, Any],
        ) -> tuple[int, int, float, str]:
            if isinstance(candidate.get("phase_one_qwen_final_score"), dict):
                return phase_one_qwen_runtime_rank(candidate)
            return original_candidate_rank(candidate)

        def bound_extract_iteration(**kwargs: Any) -> dict[str, Any]:
            return extract_iteration_hypotheses_qwen(
                original_extract_iteration=base_extract_iteration,
                **kwargs,
            )

        def bound_manifest_writer(path: Path, manifest: dict[str, Any]) -> None:
            updated = copy.deepcopy(manifest)
            updated["phase_two_initial_seed_selection"] = (
                "qwen_top_two_per_route_then_best_anchor_plus_diversified_supplement"
            )
            updated["phase_two_initial_seed_scorer"] = {
                "model": feedback_runtime.config.qwen_model,
                "pipeline": "OPC_plus_split_GPTOSS_three_block_Qwen3.6_fusion",
                "scale": "IMO_0_7_without_5",
                "independent_fresh_review_per_final_proof": True,
                "hypothesis_seed_value": False,
                "gemma_grades_visible": False,
                "terra_scoring_calls": 0,
            }
            updated["phase_one_final_proof_scoring"] = {
                "authoritative_score_field": "phase_one_qwen_final_score",
                "rank_fields": ["qwen_final_grade"],
                "artifact_directory": "phase1/qwen_final_scoring",
            }
            original_manifest_writer(path, updated)

        def bound_write_progress(
            output_dir: Path, stage: str, **details: Any
        ) -> None:
            if stage == "phase1_independent_terra_scoring":
                stage = "phase1_independent_three_block_qwen_final_scoring"
            original_write_progress(output_dir, stage, **details)

        implementation_pipeline.MODEL = GEMMA_MODEL
        implementation_verification.MODEL = GEMMA_MODEL
        implementation_verification.EndpointModelEngine.text = (
            cap_recovering_gemma_text
        )
        implementation_pipeline.run_phase_one = bound_run_phase_one
        implementation_pipeline.score_phase_one_candidates_with_terra = (
            bound_score_phase_one
        )
        implementation_pipeline.select_diversified_phase_one_candidates = (
            select_diversified_phase_one_candidates_qwen
        )
        implementation_pipeline.select_top_two_per_phase_one_route = (
            select_top_two_per_phase_one_route_qwen
        )
        implementation_contracts.candidate_rank = bound_candidate_rank
        implementation_pipeline.extract_iteration_hypotheses = bound_extract_iteration
        implementation_pipeline.write_or_validate_manifest = bound_manifest_writer
        implementation_pipeline.write_progress = bound_write_progress
        try:
            yield
        finally:
            implementation_verification.EndpointModelEngine.text = (
                original_engine_text
            )
            implementation_verification.MODEL = original_verification_model
            implementation_pipeline.MODEL = original_pipeline_model
            implementation_pipeline.write_progress = original_write_progress
            implementation_pipeline.write_or_validate_manifest = (
                original_manifest_writer
            )
            implementation_pipeline.extract_iteration_hypotheses = (
                original_extract_iteration
            )
            implementation_contracts.candidate_rank = original_candidate_rank
            implementation_pipeline.select_top_two_per_phase_one_route = (
                original_top_two
            )
            implementation_pipeline.select_diversified_phase_one_candidates = (
                original_diversity
            )
            implementation_pipeline.score_phase_one_candidates_with_terra = (
                original_score_phase_one
            )
            implementation_pipeline.run_phase_one = original_run_phase_one


def run_harness(**kwargs: Any) -> dict[str, Any]:
    validate_promoted_profile()
    frozen_base = assert_frozen_base()
    requested_width = int(kwargs.pop("phase_one_width", PHASE_ONE_WIDTH))
    if requested_width != PHASE_ONE_WIDTH:
        raise ValueError("v0.3.35 fixes Phase-1 width at four candidates per route")
    forbidden = {
        "harness_version",
        "artifact_schema_version",
        "promotion_profile",
        "promotion_base",
    } & set(kwargs)
    if forbidden:
        raise ValueError(
            "promoted identity fields are not caller-configurable: "
            + ", ".join(sorted(forbidden))
        )
    if kwargs.get("phase_one_reuse_dirs") is not None:
        raise ValueError(
            "v0.3.35 disallows untyped route reuse; use a typed Phase-1 "
            "continuation from this harness"
        )
    if str(kwargs.get("model") or "") != GEMMA_MODEL:
        raise ValueError(
            f"v0.3.35 fixes the Phase-1 solver/rewriter to {GEMMA_MODEL!r} "
            "served as BF16 with MTP4"
        )
    normalized_endpoints = tuple(
        str(value).rstrip("/") for value in kwargs.get("endpoints") or ()
    )
    if normalized_endpoints != (
        "http://127.0.0.1:8020/v1",
        "http://127.0.0.1:8020/v1",
    ):
        raise ValueError(
            "v0.3.35 fixes both logical Gemma slots to the BF16/MTP4 service "
            "at http://127.0.0.1:8020/v1"
        )
    if int(kwargs.get("solver_max_tokens", 0)) != 65_536:
        raise ValueError("v0.3.35 fixes Gemma draft/rewrite max_tokens at 65536")
    if int(kwargs.get("lazy_max_tokens", 0)) != 8_192:
        raise ValueError("v0.3.35 fixes the Gemma lazy-check max_tokens at 8192")

    config_fields = {
        "qwen_endpoint",
        "qwen_model",
        "reviewer_cuda_device",
        "llama_binary",
        "opc_model",
        "gptoss_model",
        "reviewer_ctx_size",
        "opc_predict",
        "gptoss_predict",
        "gptoss_retry_reasoning_budget",
        "qwen_fusion_max_tokens",
        "qwen_repair_max_tokens",
        "qwen_repair_recovery_max_tokens",
        "qwen_concurrency",
        "protocol_attempts",
    }
    config_kwargs = {
        key: kwargs.pop(key) for key in list(kwargs) if key in config_fields
    }
    feedback_config = PhaseOneFeedbackConfig(**config_kwargs)
    if kwargs.get("continue_from_phase_one_selection") is not None:
        raise ValueError(
            "v0.3.35 Phase-1 continuation is not accepted because the inherited "
            "loader expects the removed Terra score object"
        )
    feedback_config.validate(require_files=True)
    feedback_runtime = PhaseOneFeedbackRuntime(feedback_config)
    promotion_base = {
        **frozen_base,
        "phase_one_feedback_runtime": feedback_config.manifest(),
    }
    scoring_model = str(kwargs.get("terra_model", TERRA_MODEL))
    output_dir = Path(kwargs["output_dir"])
    with qwen_feedback_phase_one_backend(
        scoring_model=scoring_model,
        feedback_runtime=feedback_runtime,
        master_seed=int(kwargs["master_seed"]),
    ):
        result = implementation_pipeline.run_harness(
            **kwargs,
            phase_one_width=PHASE_ONE_WIDTH,
            harness_version=HARNESS_VERSION,
            artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
            promotion_profile=PROMOTION_PROFILE,
            promotion_base=promotion_base,
        )
    clean_terra_pipeline.score_backend_pipeline.assert_score_only_grade_artifacts(
        output_dir
    )
    return result
