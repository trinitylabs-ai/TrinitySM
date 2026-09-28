from __future__ import annotations

import concurrent.futures
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    contracts as implementation_contracts,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    pipeline as implementation_pipeline,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    prompts as implementation_prompts,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819.terra_runtime import (
    terra_json_call,
)
from cognitive_well_harness_v0_3_32_clean_terra_metadata_20260819 import (
    pipeline as previous_pipeline,
)

from .contracts import (
    ARTIFACT_SCHEMA_VERSION,
    HARNESS_VERSION,
    PHASE_ONE_ROUTE_COUNT,
    PHASE_ONE_WIDTH,
    PROMOTION_PROFILE,
    TERRA_MODEL,
    validate_promoted_profile,
)


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
PHASE_ONE_REFINEMENT_SCHEMA = (
    PACKAGE_DIR / "schemas" / "terra_phase_one_refinement.schema.json"
)
PHASE_ONE_FINAL_SCORE_SCHEMA = (
    PACKAGE_DIR / "schemas" / "terra_phase_one_final_score.schema.json"
)
PHASE_ONE_ANCHOR_TIEBREAK_SCHEMA = (
    PACKAGE_DIR / "schemas" / "terra_phase_one_anchor_tiebreak.schema.json"
)
PHASE_ONE_SUPPLEMENT_COMPARISON_SCHEMA = (
    PACKAGE_DIR / "schemas" / "terra_phase_one_supplement_comparison.schema.json"
)
BASE_PACKAGE = (
    REPO_ROOT / "cognitive_well_harness_v0_3_32_clean_terra_metadata_20260819"
)
PINNED_BASE_FILES = (
    "__init__.py",
    "contracts.py",
    "pipeline.py",
    "run.py",
    "schemas/terra_paired_math.schema.json",
    "schemas/terra_exact_negation_math.schema.json",
    "schemas/terra_child_math.schema.json",
    "schemas/terra_phase_one_diversity_index.schema.json",
)
EXPECTED_BASE_IMPLEMENTATION_SHA256 = (
    "7b29821f4ddebcf4d0b75aa96fcfd17a0fa7c7d54b11fa64041f45d69d6e6aeb"
)
PHASE_ONE_REFINEMENT_FIELDS = frozenset(
    {
        "score",
        "verdict",
        "first_break",
        "global_strategy_status",
        "independent_later_breaks",
        "requires_new_math",
        "external_information_used",
    }
)
PHASE_ONE_FINAL_SCORE_FIELDS = frozenset({"score", "hypothesis_seed_value"})
PHASE_ONE_ANCHOR_TIEBREAK_FIELDS = frozenset({"anchor_index"})
PHASE_ONE_COMPLEMENTARITY_AXES = (
    "different_root_characterization",
    "different_invariant",
    "alternative_construction",
    "supplies_missing_necessity_or_sufficiency",
    "sound_lemma_absent_from_anchor",
)
PHASE_ONE_SUPPLEMENT_COMPARISON_FIELDS = frozenset(PHASE_ONE_COMPLEMENTARITY_AXES)


def base_implementation_sha256() -> str:
    digest = hashlib.sha256()
    for relative in PINNED_BASE_FILES:
        path = BASE_PACKAGE / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned v0.3.32 implementation file: {path}")
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
            "v0.3.33 frozen v0.3.32 implementation changed: "
            f"expected {EXPECTED_BASE_IMPLEMENTATION_SHA256}, observed {observed}"
        )
    return {
        "package": BASE_PACKAGE.name,
        "sha256": observed,
        "files": list(PINNED_BASE_FILES),
        "recursive_base": recursive_base,
        "phase_one_refinement_contract": {
            "draft_auditor": TERRA_MODEL,
            "repair_author": "gemma4",
            "repair_modes": ["preserve", "local_repair", "strategy_rebuild"],
            "post_refinement_score_only_regrade": False,
            "phase_one_legacy_grade_adapter": False,
            "authoritative_final_score": "phase_one_terra_score",
            "anchor_primary_rank": ["score", "hypothesis_seed_value"],
            "anchor_exact_tie_policy": "isolated_terra_semantic_comparison",
            "anchor_tiebreak_model_output_fields": ["anchor_index"],
            "supplement_selection": (
                "python_ranked_independent_terra_binary_comparisons"
            ),
            "supplement_independent_model_calls": 7,
            "supplement_correctness_floor": [6, 7],
            "supplement_no_pass_fallback": "highest_remaining_correctness_score",
            "supplement_model_output_fields": list(PHASE_ONE_COMPLEMENTARITY_AXES),
            "supplement_binary_axes": list(PHASE_ONE_COMPLEMENTARITY_AXES),
            "gemma_empty_prompt_sections": False,
            "phase_two_and_three_grading": "inherited_unchanged",
        },
    }


def phase_one_refinement_prompt(*, problem: str, proof: str) -> str:
    return f"""You are an independent olympiad proof auditor. {implementation_prompts.FIREWALL}

Analyze the entire proposed proof, not just its first visible flaw. Check the exact
answer, domains, cases, necessity, sufficiency, and every load-bearing inference.

Report the earliest causal break as first_break. After locating it, continue auditing
the whole proof. Report at most two later breaks, and only when they are logically
independent of the first break rather than downstream consequences of it.

Classify the global strategy:
- sound: the overall route is valid and any defect is local;
- salvageable: independently sound components remain useful, but the organization or
  missing bridges require substantial revision;
- invalid: the main route cannot establish the requested result and should be replaced.

Set requires_new_math true exactly when correction requires a genuinely new lemma,
construction, case argument, invariant, or other mathematical idea not already
established in the proof. Do not write a repaired proof and do not prescribe repair
steps.

Use the IMO 0-7 scale. A complete rigorous proof is 7. A genuine minor slip whose
correction uses only mathematics already present is 6. Score 5 is disallowed. A gap
requiring a new mathematical idea is a fallacy and caps the score at 3. An incomplete
or wrong answer cannot pass.

PROBLEM:
{problem}

PROPOSED SOLUTION:
{proof}
"""


def phase_one_final_score_prompt(*, problem: str, proof: str) -> str:
    return f"""You are an independent olympiad proof scorer. {implementation_prompts.FIREWALL}

Evaluate this final proof from scratch. You are not given and must not infer any
candidate identity, route, prior audit, generator grade, or ranking. Check the exact
answer, necessity, sufficiency, domains, case coverage, and every load-bearing
inference.

Return a correctness score and a separate hypothesis-seed value. Use the IMO 0-7
scale for correctness: a complete rigorous proof is 7; a genuine minor slip whose
correction uses only mathematics already present is 6; score 5 is disallowed; a gap
requiring a new mathematical idea is a fallacy and caps the score at 3; an incomplete
or wrong answer cannot pass.

The hypothesis-seed value must not increase the correctness score. Use 0 when there
is no sound load-bearing structure, 1 for weak structure, 2 for a useful partially
sound idea, and 3 only when the root characterization is plausible and at least one
important load-bearing idea is sound.

Do not repair the proof and do not return a verdict, critique, first break, summary,
error list, proof, repair instruction, candidate metadata, or firewall metadata.

PROBLEM:
{problem}

FINAL PROOF:
{proof}
"""


def phase_one_solver_prompt(*, problem: str, feedback: str | None = None) -> str:
    """Preserve the frozen solver instructions while removing empty Phase-1 blocks."""

    prompt = implementation_pipeline.v027.dialectic_solver(
        problem, None, feedback=feedback
    )
    empty_materials = "\n\nADDITIONAL MATERIALS:\nNone"
    if empty_materials not in prompt:
        raise RuntimeError("frozen Phase-1 solver prompt changed its materials block")
    prompt = prompt.replace(empty_materials, "", 1)
    if not feedback:
        empty_feedback = "\n\nEXTERNAL FEEDBACK FOR THIS DRAFT:\nNone"
        if empty_feedback not in prompt:
            raise RuntimeError("frozen Phase-1 solver prompt changed its feedback block")
        prompt = prompt.replace(empty_feedback, "", 1)
    return prompt


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_phase_one_refinement_audit(result: dict[str, Any]) -> None:
    if set(result) != PHASE_ONE_REFINEMENT_FIELDS:
        raise ValueError("Terra Phase-1 refinement audit has unexpected fields")
    if result["external_information_used"] is not False:
        raise ValueError("Terra Phase-1 refinement audit violated the firewall")

    score = int(result["score"])
    verdict = str(result["verdict"])
    first_break = result["first_break"]
    strategy = str(result["global_strategy_status"])
    later_breaks = list(result["independent_later_breaks"])
    requires_new_math = result["requires_new_math"] is True

    if score not in {0, 1, 2, 3, 4, 6, 7}:
        raise ValueError(f"invalid Terra Phase-1 refinement score: {score!r}")
    if any(not _nonempty_text(value) for value in later_breaks):
        raise ValueError("independent later breaks must be nonempty")
    if len(later_breaks) != len(set(value.strip() for value in later_breaks)):
        raise ValueError("independent later breaks must be distinct")

    if score == 7:
        consistent = (
            verdict == "pass"
            and first_break is None
            and strategy == "sound"
            and not later_breaks
            and not requires_new_math
        )
    elif score == 6:
        consistent = (
            verdict == "minor_slip"
            and _nonempty_text(first_break)
            and strategy != "invalid"
            and not requires_new_math
        )
    else:
        consistent = (
            verdict in {"substantive_gap", "incorrect"}
            and _nonempty_text(first_break)
        )
    if not consistent:
        raise ValueError("internally inconsistent Terra Phase-1 refinement audit")
    if requires_new_math and score > 3:
        raise ValueError("new mathematics is a fallacy and caps the score at 3")
    if strategy == "invalid" and not requires_new_math:
        raise ValueError("an invalid global strategy must require new mathematics")


def validate_phase_one_final_score(result: dict[str, Any]) -> None:
    if set(result) != PHASE_ONE_FINAL_SCORE_FIELDS:
        raise ValueError("Terra Phase-1 final scorer must return exactly two fields")
    score = result["score"]
    if not isinstance(score, int) or isinstance(score, bool):
        raise ValueError("Terra Phase-1 final score must be an integer")
    if score not in {0, 1, 2, 3, 4, 6, 7}:
        raise ValueError(f"invalid Terra Phase-1 final score: {result['score']!r}")
    seed_value = result["hypothesis_seed_value"]
    if not isinstance(seed_value, int) or isinstance(seed_value, bool):
        raise ValueError("hypothesis-seed value must be an integer")
    if not 0 <= seed_value <= 3:
        raise ValueError("hypothesis-seed value must be between zero and three")


def phase_one_refinement_mode(audit: dict[str, Any]) -> str:
    validate_phase_one_refinement_audit(audit)
    if audit["verdict"] == "pass":
        return "preserve"
    if audit["requires_new_math"] is True or audit["global_strategy_status"] == "invalid":
        return "strategy_rebuild"
    return "local_repair"


def strategy_directive(global_strategy_status: str) -> str:
    directives = {
        "sound": (
            "The overall method appears viable. Preserve it unless your independent "
            "rechecking disproves it."
        ),
        "salvageable": (
            "Retain only independently justified components. Reorganize the argument "
            "and add the necessary logical bridges."
        ),
        "invalid": (
            "Do not patch the current route. Construct a new strategy, reusing only "
            "facts that you independently establish."
        ),
    }
    try:
        return directives[global_strategy_status]
    except KeyError as error:
        raise ValueError(f"unknown global strategy status: {global_strategy_status!r}") from error


def _render_later_break_section(values: list[str]) -> str:
    if not values:
        return ""
    bullets = "\n".join(f"- {value}" for value in values)
    return f"\n\nOTHER LOGICALLY INDEPENDENT CHALLENGES:\n{bullets}"


def phase_one_local_repair_prompt(
    *, problem: str, proof: str, audit: dict[str, Any]
) -> str:
    return f"""Solve the original problem rigorously and return one complete,
standalone proof. An independent auditor raised the challenges below. They are
unverified challenges, not established facts: check each one yourself and reject any
criticism that is mathematically mistaken.

Keep the repair focused while ensuring the entire final proof is valid.
{strategy_directive(str(audit["global_strategy_status"]))}

EARLIEST CAUSAL CHALLENGE:
{audit["first_break"]}{_render_later_break_section(list(audit["independent_later_breaks"]))}

PROBLEM:
{problem}

CURRENT PROOF:
{proof}
"""


def phase_one_strategy_rebuild_prompt(
    *, problem: str, proof: str, audit: dict[str, Any]
) -> str:
    return f"""Solve the original problem rigorously and return one complete,
standalone proof. An independent auditor raised the challenges below. They are
unverified challenges, not established facts: check each one yourself and reject any
criticism that is mathematically mistaken.

Derive whatever additional mathematics is actually needed or replace the approach.
{strategy_directive(str(audit["global_strategy_status"]))}

EARLIEST CAUSAL CHALLENGE:
{audit["first_break"]}{_render_later_break_section(list(audit["independent_later_breaks"]))}

PROBLEM:
{problem}

CURRENT PROOF:
{proof}
"""


def phase_one_dialectic_solve(
    *,
    problem: str,
    context: Any,
    count: int,
    engine: Any,
    stage_dir: Path,
    stage_name: str,
    terra_model: str,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
) -> list[dict[str, Any]]:
    """Phase-1-only dialectic with one pre-repair structural Terra audit."""

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
                prompt=phase_one_solver_prompt(problem=problem),
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
                prompt=phase_one_solver_prompt(
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

    def audit_checked() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            audit = terra_json_call(
                prompt=phase_one_refinement_prompt(
                    problem=problem, proof=str(row["proof"])
                ),
                schema_path=PHASE_ONE_REFINEMENT_SCHEMA,
                call_root=(
                    stage_dir
                    / "terra_refinement_audits"
                    / f"candidate_{index + 1}"
                ),
                stem="audit",
                model=terra_model,
                repo_root=REPO_ROOT,
                validator=validate_phase_one_refinement_audit,
            )
            return {"index": index, "audit": audit}

        return v027.parallel_map(one, checked, engine.concurrency)

    audits = v027.load_or_compute(
        stage_dir / "initial_structural_audits.json", audit_checked
    )
    audit_by_index = {int(row["index"]): row["audit"] for row in audits}

    def refine_conditionally() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            audit = audit_by_index[index]
            mode = phase_one_refinement_mode(audit)
            if mode == "preserve":
                return {
                    "index": index,
                    "proof": row["proof"],
                    "refinement_mode": mode,
                    "refinement_invoked": False,
                }
            prompt_builder = (
                phase_one_local_repair_prompt
                if mode == "local_repair"
                else phase_one_strategy_rebuild_prompt
            )
            response = engine.text(
                prompt=prompt_builder(
                    problem=problem, proof=str(row["proof"]), audit=audit
                ),
                namespace=f"{v027.safe_key(stage_name)}_{mode}",
                index=index,
                temperature=1.0,
                max_tokens=solver_max_tokens,
            )
            return {
                "index": index,
                "proof": response["final"],
                "refinement_mode": mode,
                "refinement_invoked": True,
                "response": response,
            }

        return v027.parallel_map(one, checked, engine.concurrency)

    refined = v027.load_or_compute(
        stage_dir / "conditionally_refined.json", refine_conditionally
    )
    checked_by_index = {int(row["index"]): row for row in checked}
    solutions = [
        {
            "solution_id": f"{stage_name}.s{int(row['index']) + 1}",
            "proof": row["proof"],
            "pre_refinement_audit": audit_by_index[int(row["index"])],
            "refinement_mode": row["refinement_mode"],
            "refinement_invoked": row["refinement_invoked"],
            "post_refinement_score_only_regrade": False,
            "lazy_report": checked_by_index[int(row["index"])]["lazy_report"],
            "lazy_re_solved": checked_by_index[int(row["index"])]["re_solved"],
            "context_supplied": context not in (None, [], {}),
        }
        for row in sorted(refined, key=lambda item: int(item["index"]))
    ]
    implementation_pipeline.write_json(final_path, solutions)
    return solutions


def run_phase_one_structural(
    *,
    problem: str,
    engines: tuple[Any, ...],
    output_dir: Path,
    width: int,
    terra_model: str,
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

    def run_route(index: int) -> list[dict[str, Any]]:
        return phase_one_dialectic_solve(
            problem=problem,
            context=None,
            count=width,
            engine=engines[index],
            stage_dir=output_dir / f"route_{index + 1}" / "zero_context",
            stage_name=f"phase1_route{index + 1}",
            terra_model=terra_model,
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )

    if len(engines) != PHASE_ONE_ROUTE_COUNT:
        raise ValueError(
            f"Phase 1 requires {PHASE_ONE_ROUTE_COUNT} route-specific engines"
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


def phase_one_compact_rank(candidate: dict[str, Any]) -> tuple[int, int, str]:
    terra_score = candidate.get("phase_one_terra_score")
    if not isinstance(terra_score, dict):
        raise ValueError(
            f"Phase-1 candidate lacks a compact Terra score: {candidate.get('candidate_id')}"
        )
    validate_phase_one_final_score(terra_score)
    return (
        int(terra_score["score"]),
        int(terra_score["hypothesis_seed_value"]),
        str(candidate.get("candidate_id") or ""),
    )


def phase_one_runtime_rank(candidate: dict[str, Any]) -> tuple[int, int, float, str]:
    score, _, candidate_id = phase_one_compact_rank(candidate)
    return (
        int(bool(candidate.get("terra_unanimously_confirmed"))),
        int(
            implementation_contracts.global_audit_passed(
                candidate.get("final_global_audit")
            )
        ),
        float(score),
        candidate_id,
    )


def select_top_two_per_phase_one_route_compact(
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
            sorted(by_route[route], key=phase_one_compact_rank, reverse=True)[:2]
        )
    return finalists


def score_phase_one_candidates_authoritatively(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> list[dict[str, Any]]:
    def score(candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate["candidate_id"])
        terra_score = terra_json_call(
            prompt=phase_one_final_score_prompt(
                problem=problem, proof=str(candidate["assembled_proof"])
            ),
            schema_path=PHASE_ONE_FINAL_SCORE_SCHEMA,
            call_root=output_dir / candidate_id,
            stem="score",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=validate_phase_one_final_score,
        )
        return {**candidate, "phase_one_terra_score": terra_score}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        scored = list(executor.map(score, candidates))

    implementation_pipeline.write_json(
        output_dir / "summary.json",
        {
            "scorer": terra_model,
            "independent_stateless_calls": True,
            "candidate_identity_model_visible": False,
            "gemma_grades_visible": False,
            "model_output_fields": sorted(PHASE_ONE_FINAL_SCORE_FIELDS),
            "post_refinement_score_only_regrade": False,
            "phase_one_legacy_grade_adapter": False,
            "authoritative_score_field": "phase_one_terra_score",
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "phase_one_route": row.get("phase_one_route"),
                    "score": row["phase_one_terra_score"]["score"],
                    "hypothesis_seed_value": row["phase_one_terra_score"][
                        "hypothesis_seed_value"
                    ],
                }
                for row in scored
            ],
        },
    )
    return scored


def phase_one_anchor_rank(candidate: dict[str, Any]) -> tuple[int, int]:
    score, seed_value, _ = phase_one_compact_rank(candidate)
    return score, seed_value


def phase_one_anchor_tiebreak_prompt(
    *,
    problem: str,
    tied_packets: list[dict[str, Any]],
) -> str:
    return f"""You are an olympiad proof anchor adjudicator. {implementation_prompts.FIREWALL}

The supplied proofs have exactly the same independent correctness score and exactly
the same hypothesis-seed assessment. Select the semantically strongest anchor. Each
proof has a temporary local index used only to return your selection.

Compare the complete proof structures using this priority order:
1. logical soundness and completeness;
2. strength of the central necessity-and-sufficiency or root characterization;
3. reusability of load-bearing ideas for later hypothesis extraction;
4. clarity, only as the final mathematical tiebreak.

Audit the whole proof rather than stopping at the first visible flaw. Do not repair a
proof, author hypotheses, or prefer wording differences over mathematical substance.
Return only the temporary anchor index required by the schema.

PROBLEM:
{problem}

EXACTLY TIED PROOFS:
{json.dumps(tied_packets, ensure_ascii=False)}
"""


def validate_phase_one_anchor_tiebreak(
    result: dict[str, Any], *, tied_count: int
) -> None:
    if set(result) != PHASE_ONE_ANCHOR_TIEBREAK_FIELDS:
        raise ValueError("Terra anchor tiebreak returned unexpected fields")
    index = result["anchor_index"]
    if isinstance(index, bool) or not isinstance(index, int):
        raise ValueError("Terra anchor tiebreak index must be an integer")
    if index < 0 or index >= tied_count:
        raise ValueError("Terra anchor tiebreak chose an invalid index")


def select_phase_one_anchor_compact(
    *,
    problem: str,
    finalists: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    if not finalists:
        raise ValueError("Phase-1 anchor selection requires finalists")
    best_rank = max(phase_one_anchor_rank(row) for row in finalists)
    tied_finalist_indices = [
        index
        for index, row in enumerate(finalists)
        if phase_one_anchor_rank(row) == best_rank
    ]
    terra_invoked = len(tied_finalist_indices) > 1
    if terra_invoked:
        tied_packets = [
            {
                "candidate_index": local_index,
                "proof": finalists[finalist_index]["assembled_proof"],
            }
            for local_index, finalist_index in enumerate(tied_finalist_indices)
        ]

        def validate(result: dict[str, Any]) -> None:
            validate_phase_one_anchor_tiebreak(
                result, tied_count=len(tied_finalist_indices)
            )

        model_choice = terra_json_call(
            prompt=phase_one_anchor_tiebreak_prompt(
                problem=problem,
                tied_packets=tied_packets,
            ),
            schema_path=PHASE_ONE_ANCHOR_TIEBREAK_SCHEMA,
            call_root=output_dir,
            stem="anchor_tiebreak",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=validate,
        )
        chosen_local_index = int(model_choice["anchor_index"])
        anchor_index = tied_finalist_indices[chosen_local_index]
        mode = "terra_semantic_exact_tiebreak"
        rationale = (
            "Highest compact (score, hypothesis_seed_value) rank; an exact tie "
            "was resolved by an isolated Terra semantic proof comparison."
        )
    else:
        anchor_index = tied_finalist_indices[0]
        mode = "deterministic_compact_rank"
        rationale = "Unique highest compact (score, hypothesis_seed_value) rank."

    tied_candidate_ids = [
        str(finalists[index]["candidate_id"]) for index in tied_finalist_indices
    ]
    selected_candidate_id = str(finalists[anchor_index]["candidate_id"])
    audit = {
        "mode": mode,
        "rank_fields": ["score", "hypothesis_seed_value"],
        "score": best_rank[0],
        "hypothesis_seed_value": best_rank[1],
        "tied_candidate_ids": tied_candidate_ids,
        "selected_candidate_id": selected_candidate_id,
        "terra_call_invoked": terra_invoked,
        "model_output_fields": ["anchor_index"] if terra_invoked else [],
    }
    implementation_pipeline.write_json(
        output_dir / "anchor_selection_bound.json", audit
    )
    return {
        "anchor_index": anchor_index,
        "tied_finalist_indices": tied_finalist_indices,
        "rationale": rationale,
        "audit": audit,
    }


def phase_one_supplement_comparison_prompt(
    *,
    problem: str,
    anchor_proof: str,
    alternative_proof: str,
) -> str:
    return f"""You are a proof-portfolio complementarity auditor. {implementation_prompts.FIREWALL}

One fixed anchor proof and one alternative proof are supplied. Compare only this pair.
Do not select, replace, or rank proofs.

Assign exactly 0 or 1 on each of these five axes:
- different_root_characterization: 1 only for a genuinely different, mathematically
  substantive root or exact characterization;
- different_invariant: 1 only for a distinct invariant used in a load-bearing way;
- alternative_construction: 1 only for a substantively different construction;
- supplies_missing_necessity_or_sufficiency: 1 only when the anchor lacks the mechanism
  and the alternative soundly supplies it;
- sound_lemma_absent_from_anchor: 1 only for a sound, reusable, load-bearing lemma that
  is absent from the anchor.

A value of 1 requires all three conditions: the feature is absent from the anchor, the
alternative actually establishes and uses it, and it is mathematically sound and
load-bearing. Mere mention, different notation, exposition, or downstream restatement
scores 0. Audit the complete proof structures. Do not repair proofs or author
hypotheses. Return only the five binary values required by the schema.

PROBLEM:
{problem}

FIXED ANCHOR PROOF:
{anchor_proof}

ALTERNATIVE PROOF:
{alternative_proof}
"""


def validate_phase_one_supplement_comparison(result: dict[str, Any]) -> None:
    if set(result) != PHASE_ONE_SUPPLEMENT_COMPARISON_FIELDS:
        raise ValueError("Terra supplement comparison returned unexpected fields")
    for axis in PHASE_ONE_COMPLEMENTARITY_AXES:
        value = result[axis]
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value not in (0, 1)
        ):
            raise ValueError("Terra supplement comparison values must be integer 0 or 1")


def run_phase_one_supplement_comparisons(
    *,
    problem: str,
    finalists: list[dict[str, Any]],
    anchor_index: int,
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    alternative_indices = [
        index for index in range(len(finalists)) if index != anchor_index
    ]
    if not alternative_indices:
        raise ValueError("Phase-1 supplement comparison requires an alternative")
    anchor_proof = str(finalists[anchor_index]["assembled_proof"])

    def compare(index: int) -> dict[str, Any]:
        result = terra_json_call(
            prompt=phase_one_supplement_comparison_prompt(
                problem=problem,
                anchor_proof=anchor_proof,
                alternative_proof=str(finalists[index]["assembled_proof"]),
            ),
            schema_path=PHASE_ONE_SUPPLEMENT_COMPARISON_SCHEMA,
            call_root=output_dir / "supplement_comparisons" / f"alternative_{index}",
            stem="comparison",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=validate_phase_one_supplement_comparison,
        )
        return {
            "candidate_index": index,
            **{axis: int(result[axis]) for axis in PHASE_ONE_COMPLEMENTARITY_AXES},
        }

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(4, len(alternative_indices))
    ) as executor:
        assessments = list(executor.map(compare, alternative_indices))
    return {"candidate_assessments": assessments}


def validate_phase_one_supplement_matrix(
    result: dict[str, Any], *, finalist_count: int, anchor_index: int
) -> None:
    if set(result) != {"candidate_assessments"}:
        raise ValueError("bound supplement matrix returned unexpected fields")
    assessments = result["candidate_assessments"]
    if not isinstance(assessments, list):
        raise ValueError("Terra supplement assessments must be a list")
    expected_indices = set(range(finalist_count)) - {anchor_index}
    observed_indices: list[int] = []
    expected_fields = {"candidate_index", *PHASE_ONE_COMPLEMENTARITY_AXES}
    for assessment in assessments:
        if not isinstance(assessment, dict) or set(assessment) != expected_fields:
            raise ValueError("Terra supplement assessment fields are invalid")
        candidate_index = assessment["candidate_index"]
        if isinstance(candidate_index, bool) or not isinstance(candidate_index, int):
            raise ValueError("Terra supplement candidate index must be an integer")
        observed_indices.append(candidate_index)
        for axis in PHASE_ONE_COMPLEMENTARITY_AXES:
            value = assessment[axis]
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value not in (0, 1)
            ):
                raise ValueError("Terra supplement axes must be integer 0 or 1")
    if (
        len(observed_indices) != len(expected_indices)
        or len(set(observed_indices)) != len(expected_indices)
        or set(observed_indices) != expected_indices
    ):
        raise ValueError(
            "Terra supplement audit must assess every non-anchor finalist exactly once"
        )


def phase_one_complementarity_score(assessment: dict[str, Any]) -> int:
    return sum(int(assessment[axis]) for axis in PHASE_ONE_COMPLEMENTARITY_AXES)


def select_phase_one_supplement_from_matrix(
    *,
    finalists: list[dict[str, Any]],
    anchor_index: int,
    model_audit: dict[str, Any],
) -> dict[str, Any]:
    validate_phase_one_supplement_matrix(
        model_audit,
        finalist_count=len(finalists),
        anchor_index=anchor_index,
    )
    assessment_by_index = {
        int(row["candidate_index"]): row
        for row in model_audit["candidate_assessments"]
    }
    alternative_indices = sorted(assessment_by_index)
    passing_indices = [
        index
        for index in alternative_indices
        if phase_one_anchor_rank(finalists[index])[0] in (6, 7)
    ]
    if passing_indices:
        eligible_indices = passing_indices
        eligibility_mode = "score_6_or_7_correctness_floor"
    else:
        highest_remaining_score = max(
            phase_one_anchor_rank(finalists[index])[0]
            for index in alternative_indices
        )
        eligible_indices = [
            index
            for index in alternative_indices
            if phase_one_anchor_rank(finalists[index])[0] == highest_remaining_score
        ]
        eligibility_mode = "highest_remaining_score_fallback"

    def supplement_rank(index: int) -> tuple[int, int, int, int]:
        score, seed_value = phase_one_anchor_rank(finalists[index])
        return (
            phase_one_complementarity_score(assessment_by_index[index]),
            score,
            seed_value,
            -index,
        )

    supplement_index = max(eligible_indices, key=supplement_rank)
    selected_assessment = assessment_by_index[supplement_index]
    return {
        "supplement_index": supplement_index,
        "eligibility_mode": eligibility_mode,
        "eligible_indices": eligible_indices,
        "complementarity_score": phase_one_complementarity_score(
            selected_assessment
        ),
        "positive_axes": [
            axis
            for axis in PHASE_ONE_COMPLEMENTARITY_AXES
            if int(selected_assessment[axis]) == 1
        ],
        "assessment_by_index": assessment_by_index,
    }


def select_diversified_phase_one_candidates_compact(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    finalists = select_top_two_per_phase_one_route_compact(candidates)
    expected_count = PHASE_ONE_ROUTE_COUNT * 2
    if len(finalists) != expected_count:
        raise ValueError(
            f"Phase-1 diversity selector requires exactly {expected_count} finalists"
        )
    anchor_selection = select_phase_one_anchor_compact(
        problem=problem,
        finalists=finalists,
        output_dir=output_dir,
        terra_model=terra_model,
    )
    anchor_index = int(anchor_selection["anchor_index"])
    highest_score = max(
        int(row["phase_one_terra_score"]["score"]) for row in finalists
    )
    eligible_anchor_indices = [
        index
        for index, row in enumerate(finalists)
        if int(row["phase_one_terra_score"]["score"]) == highest_score
    ]
    model_audit = run_phase_one_supplement_comparisons(
        problem=problem,
        finalists=finalists,
        anchor_index=anchor_index,
        output_dir=output_dir,
        terra_model=terra_model,
    )
    supplement_selection = select_phase_one_supplement_from_matrix(
        finalists=finalists,
        anchor_index=anchor_index,
        model_audit=model_audit,
    )
    supplement_index = int(supplement_selection["supplement_index"])
    bound_assessments = []
    for index, finalist in enumerate(finalists):
        if index == anchor_index:
            assessment = {
                axis: 0 for axis in PHASE_ONE_COMPLEMENTARITY_AXES
            }
            assessment_source = "fixed_anchor_baseline"
        else:
            assessment = supplement_selection["assessment_by_index"][index]
            assessment_source = "terra_binary_comparison"
        bound_assessments.append(
            {
                "candidate_id": finalist["candidate_id"],
                **{
                    axis: int(assessment[axis])
                    for axis in PHASE_ONE_COMPLEMENTARITY_AXES
                },
                "complementarity_score": sum(
                    int(assessment[axis])
                    for axis in PHASE_ONE_COMPLEMENTARITY_AXES
                ),
                "assessment_source": assessment_source,
            }
        )
    eligible_candidate_ids = [
        str(finalists[index]["candidate_id"])
        for index in supplement_selection["eligible_indices"]
    ]
    audit = {
        "anchor_candidate_id": finalists[anchor_index]["candidate_id"],
        "supplement_candidate_id": finalists[supplement_index]["candidate_id"],
        "candidate_assessments": bound_assessments,
        "anchor_rationale": anchor_selection["rationale"],
        "anchor_selection": anchor_selection["audit"],
        "supplement_selection": {
            "policy": "binary_complementarity_sum_with_correctness_floor",
            "binary_axes": list(PHASE_ONE_COMPLEMENTARITY_AXES),
            "eligibility_mode": supplement_selection["eligibility_mode"],
            "eligible_candidate_ids": eligible_candidate_ids,
            "rank_fields": [
                "complementarity_score",
                "score",
                "hypothesis_seed_value",
                "stable_local_index",
            ],
            "selected_candidate_id": finalists[supplement_index]["candidate_id"],
            "selected_complementarity_score": supplement_selection[
                "complementarity_score"
            ],
            "independent_model_calls": len(finalists) - 1,
            "candidate_identity_model_visible": False,
            "model_output_fields": list(PHASE_ONE_COMPLEMENTARITY_AXES),
        },
        "complementarity_axes": supplement_selection["positive_axes"],
        "external_information_used": False,
    }
    implementation_pipeline.write_json(output_dir / "selection_bound.json", audit)
    return {
        "finalists": finalists,
        "eligible_anchor_ids": [
            str(finalists[index]["candidate_id"])
            for index in eligible_anchor_indices
        ],
        "selected": [finalists[anchor_index], finalists[supplement_index]],
        "audit": audit,
    }


def validate_loaded_phase_one_anchor_selection(loaded: dict[str, Any]) -> None:
    selection = loaded.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("completed Phase-1 selection is missing")
    finalists = selection.get("finalists")
    selected = selection.get("selected")
    if not isinstance(finalists, list) or not finalists:
        raise ValueError("completed Phase-1 selection has no finalists")
    if not isinstance(selected, list) or len(selected) != 2:
        raise ValueError("completed Phase-1 selection must contain two proofs")

    best_rank = max(phase_one_anchor_rank(row) for row in finalists)
    tied_candidate_ids = [
        str(row.get("candidate_id") or "")
        for row in finalists
        if phase_one_anchor_rank(row) == best_rank
    ]
    selected_anchor_id = str(selected[0].get("candidate_id") or "")
    if selected_anchor_id not in tied_candidate_ids:
        raise ValueError(
            "saved Phase-1 anchor is below the best compact score/seed rank"
        )

    audit = selection.get("audit")
    anchor_audit = audit.get("anchor_selection") if isinstance(audit, dict) else None
    if not isinstance(anchor_audit, dict):
        raise ValueError("saved Phase-1 selection lacks its anchor audit")
    expected_tie = len(tied_candidate_ids) > 1
    expected_mode = (
        "terra_semantic_exact_tiebreak"
        if expected_tie
        else "deterministic_compact_rank"
    )
    if anchor_audit.get("mode") != expected_mode:
        raise ValueError("saved Phase-1 anchor mode differs from the compact rank")
    if anchor_audit.get("rank_fields") != ["score", "hypothesis_seed_value"]:
        raise ValueError("saved Phase-1 anchor rank fields are invalid")
    if int(anchor_audit.get("score", -1)) != best_rank[0] or int(
        anchor_audit.get("hypothesis_seed_value", -1)
    ) != best_rank[1]:
        raise ValueError("saved Phase-1 anchor rank values differ from the scores")
    if anchor_audit.get("tied_candidate_ids") != tied_candidate_ids:
        raise ValueError("saved Phase-1 anchor tie set differs from the scores")
    if anchor_audit.get("selected_candidate_id") != selected_anchor_id:
        raise ValueError("saved Phase-1 anchor differs from its anchor audit")
    if anchor_audit.get("terra_call_invoked") is not expected_tie:
        raise ValueError("saved Phase-1 anchor Terra-call status is invalid")
    expected_model_fields = ["anchor_index"] if expected_tie else []
    if anchor_audit.get("model_output_fields") != expected_model_fields:
        raise ValueError("saved Phase-1 anchor model fields are invalid")

    finalist_ids = [str(row.get("candidate_id") or "") for row in finalists]
    anchor_index = finalist_ids.index(selected_anchor_id)
    assessment_rows = audit.get("candidate_assessments")
    if not isinstance(assessment_rows, list):
        raise ValueError("saved Phase-1 selection lacks complementarity assessments")
    expected_bound_fields = {
        "candidate_id",
        *PHASE_ONE_COMPLEMENTARITY_AXES,
        "complementarity_score",
        "assessment_source",
    }
    assessment_by_id: dict[str, dict[str, Any]] = {}
    for row in assessment_rows:
        if not isinstance(row, dict) or set(row) != expected_bound_fields:
            raise ValueError("saved Phase-1 complementarity fields are invalid")
        candidate_id = str(row.get("candidate_id") or "")
        if candidate_id in assessment_by_id:
            raise ValueError("saved Phase-1 complementarity IDs are duplicated")
        assessment_by_id[candidate_id] = row
    if set(assessment_by_id) != set(finalist_ids):
        raise ValueError("saved Phase-1 complementarity IDs differ from finalists")

    raw_assessments = []
    for index, candidate_id in enumerate(finalist_ids):
        row = assessment_by_id[candidate_id]
        for axis in PHASE_ONE_COMPLEMENTARITY_AXES:
            value = row[axis]
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value not in (0, 1)
            ):
                raise ValueError("saved Phase-1 complementarity axes are invalid")
        observed_sum = sum(int(row[axis]) for axis in PHASE_ONE_COMPLEMENTARITY_AXES)
        if row["complementarity_score"] != observed_sum:
            raise ValueError("saved Phase-1 complementarity sum is invalid")
        if index == anchor_index:
            if row["assessment_source"] != "fixed_anchor_baseline" or observed_sum != 0:
                raise ValueError("saved Phase-1 anchor baseline is invalid")
            continue
        if row["assessment_source"] != "terra_binary_comparison":
            raise ValueError("saved Phase-1 complementarity source is invalid")
        raw_assessments.append(
            {
                "candidate_index": index,
                **{axis: row[axis] for axis in PHASE_ONE_COMPLEMENTARITY_AXES},
            }
        )

    expected_supplement = select_phase_one_supplement_from_matrix(
        finalists=finalists,
        anchor_index=anchor_index,
        model_audit={"candidate_assessments": raw_assessments},
    )
    selected_supplement_id = str(selected[1].get("candidate_id") or "")
    expected_supplement_id = finalist_ids[
        int(expected_supplement["supplement_index"])
    ]
    if selected_supplement_id != expected_supplement_id:
        raise ValueError("saved Phase-1 supplement differs from deterministic ranking")

    supplement_audit = audit.get("supplement_selection")
    if not isinstance(supplement_audit, dict):
        raise ValueError("saved Phase-1 selection lacks its supplement audit")
    expected_eligible_ids = [
        finalist_ids[index] for index in expected_supplement["eligible_indices"]
    ]
    expected_supplement_audit = {
        "policy": "binary_complementarity_sum_with_correctness_floor",
        "binary_axes": list(PHASE_ONE_COMPLEMENTARITY_AXES),
        "eligibility_mode": expected_supplement["eligibility_mode"],
        "eligible_candidate_ids": expected_eligible_ids,
        "rank_fields": [
            "complementarity_score",
            "score",
            "hypothesis_seed_value",
            "stable_local_index",
        ],
        "selected_candidate_id": expected_supplement_id,
        "selected_complementarity_score": expected_supplement[
            "complementarity_score"
        ],
        "independent_model_calls": len(finalists) - 1,
        "candidate_identity_model_visible": False,
        "model_output_fields": list(PHASE_ONE_COMPLEMENTARITY_AXES),
    }
    if supplement_audit != expected_supplement_audit:
        raise ValueError("saved Phase-1 supplement audit differs from deterministic ranking")
    if audit.get("complementarity_axes") != expected_supplement["positive_axes"]:
        raise ValueError("saved Phase-1 positive complementarity axes are invalid")
    if audit.get("external_information_used") is not False:
        raise ValueError("saved Phase-1 selection violated the information firewall")


def load_completed_phase_one_selection_with_anchor_validation(
    *, original_loader: Any, **kwargs: Any
) -> dict[str, Any]:
    loaded = original_loader(**kwargs)
    validate_loaded_phase_one_anchor_selection(loaded)
    return loaded


def extract_iteration_hypotheses_compact(
    *, original_extract_iteration: Any, **kwargs: Any
) -> dict[str, Any]:
    """Expose compact Phase-1 assessments to Gemma without a legacy grade object."""

    compact_by_id: dict[str, dict[str, Any]] = {}
    for candidate in kwargs.get("pool") or []:
        terra_score = candidate.get("phase_one_terra_score")
        if not isinstance(terra_score, dict):
            continue
        validate_phase_one_final_score(terra_score)
        compact_by_id[str(candidate.get("candidate_id") or "")] = dict(terra_score)

    original_v027_extract = implementation_pipeline.v027.extract_hypotheses

    def compact_seed_extract(**extract_kwargs: Any) -> dict[str, Any]:
        rewritten = []
        for seed in extract_kwargs.get("seed_solutions") or []:
            candidate_id = str(seed.get("solution_id") or "")
            compact_score = compact_by_id.get(candidate_id)
            if compact_score is None:
                rewritten.append(seed)
                continue
            rewritten.append(
                {
                    **{key: value for key, value in seed.items() if key != "grade"},
                    "phase_one_terra_score": compact_score,
                }
            )
        return original_v027_extract(
            **{**extract_kwargs, "seed_solutions": rewritten}
        )

    implementation_pipeline.v027.extract_hypotheses = compact_seed_extract
    try:
        return original_extract_iteration(**kwargs)
    finally:
        implementation_pipeline.v027.extract_hypotheses = original_v027_extract


@contextmanager
def structural_phase_one_backend(scoring_model: str) -> Iterator[None]:
    """Install the new dialectic only at the Phase-1 orchestration boundary."""

    with previous_pipeline.clean_terra_metadata_backend(scoring_model):
        original_run_phase_one = implementation_pipeline.run_phase_one
        original_score_phase_one = (
            implementation_pipeline.score_phase_one_candidates_with_terra
        )
        original_diversity = (
            implementation_pipeline.select_diversified_phase_one_candidates
        )
        original_top_two_per_route = (
            implementation_pipeline.select_top_two_per_phase_one_route
        )
        original_phase_one_validator = implementation_pipeline._phase_one_terra_score_validator
        original_candidate_rank = implementation_contracts.candidate_rank
        original_extract_iteration = implementation_pipeline.extract_iteration_hypotheses
        original_load_completed_selection = (
            implementation_pipeline.load_completed_phase_one_selection
        )

        def bound_run_phase_one(**kwargs: Any) -> list[dict[str, Any]]:
            return run_phase_one_structural(
                **kwargs,
                terra_model=scoring_model,
            )

        def bound_candidate_rank(candidate: dict[str, Any]) -> tuple[int, int, float, str]:
            if isinstance(candidate.get("phase_one_terra_score"), dict):
                return phase_one_runtime_rank(candidate)
            return original_candidate_rank(candidate)

        def bound_extract_iteration(**kwargs: Any) -> dict[str, Any]:
            return extract_iteration_hypotheses_compact(
                original_extract_iteration=original_extract_iteration,
                **kwargs,
            )

        def bound_load_completed_selection(**kwargs: Any) -> dict[str, Any]:
            return load_completed_phase_one_selection_with_anchor_validation(
                original_loader=original_load_completed_selection,
                **kwargs,
            )

        implementation_pipeline.run_phase_one = bound_run_phase_one
        implementation_pipeline.score_phase_one_candidates_with_terra = (
            score_phase_one_candidates_authoritatively
        )
        implementation_pipeline.select_diversified_phase_one_candidates = (
            select_diversified_phase_one_candidates_compact
        )
        implementation_pipeline.select_top_two_per_phase_one_route = (
            select_top_two_per_phase_one_route_compact
        )
        implementation_pipeline._phase_one_terra_score_validator = (
            validate_phase_one_final_score
        )
        implementation_contracts.candidate_rank = bound_candidate_rank
        implementation_pipeline.extract_iteration_hypotheses = bound_extract_iteration
        implementation_pipeline.load_completed_phase_one_selection = (
            bound_load_completed_selection
        )
        try:
            yield
        finally:
            implementation_pipeline.load_completed_phase_one_selection = (
                original_load_completed_selection
            )
            implementation_pipeline.extract_iteration_hypotheses = (
                original_extract_iteration
            )
            implementation_contracts.candidate_rank = original_candidate_rank
            implementation_pipeline._phase_one_terra_score_validator = (
                original_phase_one_validator
            )
            implementation_pipeline.select_diversified_phase_one_candidates = (
                original_diversity
            )
            implementation_pipeline.select_top_two_per_phase_one_route = (
                original_top_two_per_route
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
        raise ValueError("v0.3.33 fixes Phase-1 width at four candidates per route")
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
            "v0.3.33 disallows untyped route reuse; use a typed Phase-1 "
            "continuation from this harness"
        )
    scoring_model = str(kwargs.get("terra_model", TERRA_MODEL))
    output_dir = Path(kwargs["output_dir"])
    with structural_phase_one_backend(scoring_model):
        result = implementation_pipeline.run_harness(
            **kwargs,
            phase_one_width=PHASE_ONE_WIDTH,
            harness_version=HARNESS_VERSION,
            artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
            promotion_profile=PROMOTION_PROFILE,
            promotion_base=frozen_base,
        )
    previous_pipeline.score_backend_pipeline.assert_score_only_grade_artifacts(
        output_dir
    )
    return result
