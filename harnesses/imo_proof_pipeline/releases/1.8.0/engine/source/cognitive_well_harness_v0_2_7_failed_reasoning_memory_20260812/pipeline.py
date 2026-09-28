from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from core import (
    COMBINER_SCHEMA,
    CONJECTURE_SCHEMA,
    FAILED_LEMMA_SCREEN_SCHEMA,
    GRADE_SCHEMA,
    ModelEngine,
    load_or_compute,
    mean_grade,
    parallel_map,
    validate_grade,
    write_json,
)
from prompts import (
    answer_combiner,
    conjecture_extractor,
    conjecture_parser,
    dialectic_solver,
    failed_lemma_screen,
    inquisitorial_grader,
    lazy_phrasing,
    refine,
    standalone_solver,
)


FAILED_STATUS_PRIORITY = {
    "unproved": 1,
    "grader_conflict": 2,
    "refuted": 3,
}


def safe_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def solution_rank(solution: dict[str, Any]) -> tuple[Any, ...]:
    grade = solution.get("grade") or {}
    return (
        int(grade.get("effective_score", grade.get("score") or 0)),
        -len(grade.get("errors") or []),
        len(str(solution.get("proof") or "")),
        hashlib.sha256(str(solution.get("proof") or "").encode("utf-8")).hexdigest(),
    )


def best(solutions: list[dict[str, Any]]) -> dict[str, Any]:
    if not solutions:
        raise ValueError("solution memory is empty")
    return max(solutions, key=solution_rank)


def select_top(solutions: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    return sorted(solutions, key=solution_rank, reverse=True)[:count]


def failed_memory_id(claim: str) -> str:
    normalized = " ".join(str(claim).split()).casefold()
    return "failed-" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def concise_grade_evidence(grade: dict[str, Any], limit: int = 1800) -> str:
    errors = []
    for row in grade.get("errors") or []:
        description = str(row.get("description") or "").strip()
        rejection = str(row.get("defense_rejected_because") or "").strip()
        if description or rejection:
            errors.append(" — ".join(part for part in [description, rejection] if part))
    value = " | ".join(errors)
    if not value or value.startswith("See the complete plaintext grading report"):
        value = str(grade.get("coroners_report") or grade.get("raw_report") or "").strip()
    return value[:limit]


def grade_reasoning_failure(grade: dict[str, Any], *, side: str) -> dict[str, Any]:
    """Compress one grader report into a failed proof step without new inference."""

    errors = list(grade.get("errors") or [])
    first = errors[0] if errors else {}
    unsupported = str(first.get("description") or "").strip()
    if not unsupported:
        unsupported = concise_grade_evidence(grade)
    missing = str(first.get("defense_rejected_because") or "").strip()
    if not missing:
        questions = [str(value).strip() for value in grade.get("scaffolding_questions") or []]
        missing = " | ".join(value for value in questions if value)
    progress = [str(value).strip() for value in grade.get("strengths") or []]
    return {
        "side": side,
        "established_progress": [value[:1000] for value in progress if value][:6],
        "unsupported_inference": unsupported[:1800],
        "missing_evidence": missing[:1800],
        "reuse_policy": (
            "Do not use this inference as a premise. Prove the missing implication explicitly "
            "or derive the target without depending on it."
        ),
    }


def build_failed_lemma_memory(
    *,
    hypotheses: dict[str, Any],
    proven: list[dict[str, Any]],
    failed: list[dict[str, Any]],
    source_iteration: str,
) -> list[dict[str, Any]]:
    """Convert verification outcomes into compact, typed negative progress.

    A failed proof is not evidence that a claim is false.  Only a validated proof
    of the exact supplied negation creates a ``refuted`` record.
    """

    conjectures = list(hypotheses.get("conjectures") or [])
    negations = list(hypotheses.get("negations") or [])
    records: list[dict[str, Any]] = []
    for row in proven:
        if row.get("side") != "negative":
            continue
        index = int(row["source_index"])
        claim = str(conjectures[index])
        records.append(
            {
                "memory_id": failed_memory_id(claim),
                "candidate_claim": claim,
                "exact_negation": str(negations[index]),
                "status": "refuted",
                "failure_reason": "The exact supplied negation was independently proved and met the verification threshold.",
                "evidence": concise_grade_evidence(row.get("grade") or {}),
                "evidence_proof_sha256": hashlib.sha256(
                    str(row.get("proof") or "").encode("utf-8")
                ).hexdigest(),
                "source_iteration": source_iteration,
                "source_index": index,
                "reconsideration_rule": "Do not reuse an equivalent claim unless its statement removes the refutation.",
                "reasoning_failures": [
                    {
                        "side": "candidate_claim",
                        "established_progress": [],
                        "unsupported_inference": claim,
                        "missing_evidence": "The certified proof of the exact negation must be defeated under the original constraints.",
                        "reuse_policy": "Do not assume this claim or any consequence that requires it unless the refutation is removed.",
                    }
                ],
            }
        )
    for row in failed:
        index = int(row["source_index"])
        positive_grade = row["positive"].get("grade") or {}
        negative_grade = row["negative"].get("grade") or {}
        threshold = int(row["threshold"])
        positive_pass = bool(positive_grade.get("valid_scale")) and int(
            positive_grade.get("score", -1)
        ) >= threshold
        negative_pass = bool(negative_grade.get("valid_scale")) and int(
            negative_grade.get("score", -1)
        ) >= threshold
        status = "grader_conflict" if positive_pass and negative_pass else "unproved"
        reason = (
            "Both the claim and its exact negation were graded above threshold; the evidence is inconsistent."
            if status == "grader_conflict"
            else "Neither the claim nor its exact negation was proved above threshold. This is lack of proof, not a refutation."
        )
        claim = str(conjectures[index])
        records.append(
            {
                "memory_id": failed_memory_id(claim),
                "candidate_claim": claim,
                "exact_negation": str(negations[index]),
                "status": status,
                "failure_reason": reason,
                "evidence": {
                    "positive": concise_grade_evidence(positive_grade),
                    "negative": concise_grade_evidence(negative_grade),
                },
                "evidence_proof_sha256": {
                    "positive": hashlib.sha256(
                        str(row["positive"].get("proof") or "").encode("utf-8")
                    ).hexdigest(),
                    "negative": hashlib.sha256(
                        str(row["negative"].get("proof") or "").encode("utf-8")
                    ).hexdigest(),
                },
                "source_iteration": source_iteration,
                "source_index": index,
                "reconsideration_rule": (
                    "Do not treat either side as established; require a statement-level repair or new decisive evidence."
                    if status == "grader_conflict"
                    else "Do not repeat the same claim unchanged; permit a statement-level repair that addresses the recorded proof gap."
                ),
                "reasoning_failures": [
                    grade_reasoning_failure(positive_grade, side="candidate_claim"),
                    grade_reasoning_failure(negative_grade, side="exact_negation"),
                ],
            }
        )
    return records


def merge_failed_lemma_memory(
    current: list[dict[str, Any]],
    additions: list[dict[str, Any]],
    *,
    limit: int = 18,
) -> list[dict[str, Any]]:
    """Exact-deduplicate memory, retaining the strongest available status."""

    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for row in [*current, *additions]:
        memory_id = str(row["memory_id"])
        if memory_id not in merged:
            order.append(memory_id)
            merged[memory_id] = row
            continue
        old = merged[memory_id]
        if FAILED_STATUS_PRIORITY[str(row["status"])] >= FAILED_STATUS_PRIORITY[str(old["status"])]:
            merged[memory_id] = row
    # Keep refutations first, then the most recent unresolved records. The cap
    # bounds prompt growth but never silently drops a certified refutation.
    refuted = [merged[key] for key in order if merged[key]["status"] == "refuted"]
    unresolved = [merged[key] for key in order if merged[key]["status"] != "refuted"]
    room = max(limit - len(refuted), 0)
    return [*refuted, *unresolved[-room:]] if room else refuted


def screen_hypotheses_against_failed_memory(
    *,
    problem: str,
    hypotheses: dict[str, Any],
    failed_lemma_memory: list[dict[str, Any]],
    engine: ModelEngine,
    stage_dir: Path,
    stage_name: str,
    parser_max_tokens: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    conjectures = list(hypotheses.get("conjectures") or [])
    negations = list(hypotheses.get("negations") or [])
    if not conjectures or not failed_lemma_memory:
        return hypotheses, []
    audit_path = stage_dir / f"{safe_key(stage_name)}_failed_memory_screen.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    else:
        audit = engine.structured(
            prompt=failed_lemma_screen(
                problem,
                conjectures,
                str(hypotheses.get("proof") or ""),
                failed_lemma_memory,
            ),
            namespace=f"{safe_key(stage_name)}_failed_memory_screen",
            schema_name="failed_lemma_screen",
            schema=FAILED_LEMMA_SCREEN_SCHEMA,
            max_tokens=parser_max_tokens,
            temperature=0.1,
        )["parsed"]
        write_json(audit_path, audit)
    decisions = list(audit.get("decisions") or [])
    expected = list(range(len(conjectures)))
    observed = [int(row.get("candidate_index", -1)) for row in decisions]
    if observed != expected:
        raise ValueError(
            f"failed-lemma screen must cover candidates in order: expected {expected}, got {observed}"
        )
    accepted_indexes = [
        int(row["candidate_index"])
        for row in decisions
        if row["verdict"] in {"new", "repaired"}
    ]
    rejected = [row for row in decisions if row["verdict"] not in {"new", "repaired"}]
    screened = {
        **hypotheses,
        "conjectures": [conjectures[index] for index in accepted_indexes],
        "negations": [negations[index] for index in accepted_indexes],
        "failed_memory_screen": decisions,
        "screened_out_count": len(rejected),
    }
    return screened, rejected


def dialectic_solve(
    *,
    problem: str,
    context: Any,
    count: int,
    engine: ModelEngine,
    stage_dir: Path,
    stage_name: str,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
) -> list[dict[str, Any]]:
    """Appendix Algorithm 2, with each orchestrator step as a separate call."""

    stage_dir.mkdir(parents=True, exist_ok=True)
    final_path = stage_dir / "solutions.json"
    if final_path.exists():
        return json.loads(final_path.read_text(encoding="utf-8"))

    def make_drafts() -> list[dict[str, Any]]:
        def one(index: int) -> dict[str, Any]:
            response = engine.text(
                prompt=dialectic_solver(problem, context),
                namespace=f"{safe_key(stage_name)}_draft",
                index=index,
                temperature=1.0,
                max_tokens=solver_max_tokens,
            )
            return {"index": index, "proof": response["final"], "response": response}

        return parallel_map(one, range(count), engine.concurrency)

    drafts = load_or_compute(stage_dir / "drafts.json", make_drafts)

    def check_lazy() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            response = engine.text(
                prompt=lazy_phrasing(str(row["proof"])),
                namespace=f"{safe_key(stage_name)}_lazy",
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

        return parallel_map(one, drafts, engine.concurrency)

    lazy_rows = load_or_compute(stage_dir / "lazy_checks.json", check_lazy)
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
                prompt=dialectic_solver(
                    problem,
                    context,
                    feedback="Derive explicitly. Repair every issue in this report:\n" + lazy["report"],
                ),
                namespace=f"{safe_key(stage_name)}_explicit_resolve",
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

        return parallel_map(one, drafts, engine.concurrency)

    checked = load_or_compute(stage_dir / "checked_drafts.json", repair_lazy)

    def initial_grading() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            response = engine.grade(
                prompt=inquisitorial_grader(problem, str(row["proof"]), context),
                namespace=f"{safe_key(stage_name)}_grade",
                index=index,
                temperature=0.1,
                max_tokens=grader_max_tokens,
            )
            return {"index": index, "grade": validate_grade(response["parsed"]), "response": response["response"]}

        return parallel_map(one, checked, engine.concurrency)

    grades = load_or_compute(stage_dir / "initial_grades.json", initial_grading)
    grade_by_index = {int(row["index"]): row["grade"] for row in grades}

    def refine_all() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            response = engine.text(
                prompt=refine(problem, str(row["proof"]), grade_by_index[index], context),
                namespace=f"{safe_key(stage_name)}_refine",
                index=index,
                temperature=1.0,
                max_tokens=solver_max_tokens,
            )
            return {"index": index, "proof": response["final"], "response": response}

        return parallel_map(one, checked, engine.concurrency)

    refined = load_or_compute(stage_dir / "refined.json", refine_all)

    def regrade_all() -> list[dict[str, Any]]:
        def one(row: dict[str, Any]) -> dict[str, Any]:
            index = int(row["index"])
            response = engine.grade(
                prompt=inquisitorial_grader(problem, str(row["proof"]), context),
                namespace=f"{safe_key(stage_name)}_regrade",
                index=index,
                temperature=0.1,
                max_tokens=grader_max_tokens,
            )
            return {"index": index, "grade": validate_grade(response["parsed"]), "response": response["response"]}

        return parallel_map(one, refined, engine.concurrency)

    regrades = load_or_compute(stage_dir / "regrades.json", regrade_all)
    regrade_by_index = {int(row["index"]): row["grade"] for row in regrades}
    checked_by_index = {int(row["index"]): row for row in checked}
    solutions = [
        {
            "solution_id": f"{stage_name}.s{int(row['index']) + 1}",
            "proof": row["proof"],
            "grade": regrade_by_index[int(row["index"])],
            "pre_refinement_grade": grade_by_index[int(row["index"])],
            "lazy_report": checked_by_index[int(row["index"])]["lazy_report"],
            "lazy_re_solved": checked_by_index[int(row["index"])]["re_solved"],
            "context_supplied": context not in (None, [], {}),
        }
        for row in sorted(refined, key=lambda item: int(item["index"]))
    ]
    write_json(final_path, solutions)
    return solutions


def independent_grades(
    *,
    problem: str,
    solution: dict[str, Any],
    repetitions: int,
    engine: ModelEngine,
    stage_dir: Path,
    stage_name: str,
    grader_max_tokens: int,
) -> list[dict[str, Any]]:
    path = stage_dir / f"{safe_key(stage_name)}.json"

    def compute() -> list[dict[str, Any]]:
        def one(index: int) -> dict[str, Any]:
            response = engine.grade(
                prompt=inquisitorial_grader(problem, str(solution["proof"]), None),
                namespace=f"{safe_key(stage_name)}_independent_grade",
                index=index,
                temperature=0.1,
                max_tokens=grader_max_tokens,
            )
            return validate_grade(response["parsed"])

        return parallel_map(one, range(repetitions), engine.concurrency)

    return load_or_compute(path, compute)


def verified_success(
    *,
    problem: str,
    solutions: list[dict[str, Any]],
    repetitions: int,
    engine: ModelEngine,
    stage_dir: Path,
    stage_name: str,
    grader_max_tokens: int,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    audits: list[dict[str, Any]] = []
    for position, solution in enumerate(select_top(solutions, len(solutions))):
        if not bool(solution["grade"].get("perfect")):
            continue
        grades = independent_grades(
            problem=problem,
            solution=solution,
            repetitions=repetitions,
            engine=engine,
            stage_dir=stage_dir,
            stage_name=f"{stage_name}_{position}",
            grader_max_tokens=grader_max_tokens,
        )
        audit = {
            "solution_id": solution["solution_id"],
            "grades": grades,
            "all_perfect": len(grades) == repetitions and all(row["perfect"] for row in grades),
        }
        audits.append(audit)
        if audit["all_perfect"]:
            return solution, audits
    return None, audits


def extract_hypotheses(
    *,
    problem: str,
    seed_solutions: list[dict[str, Any]],
    lemma_memory: list[dict[str, Any]],
    failed_lemma_memory: list[dict[str, Any]],
    failure_context: list[dict[str, Any]],
    engine: ModelEngine,
    stage_dir: Path,
    stage_name: str,
    solver_max_tokens: int,
    parser_max_tokens: int,
) -> dict[str, Any]:
    final_path = stage_dir / f"{safe_key(stage_name)}_parsed.json"
    if final_path.exists():
        return json.loads(final_path.read_text(encoding="utf-8"))
    raw = engine.text(
        prompt=conjecture_extractor(
            problem,
            seed_solutions,
            lemma_memory,
            failed_lemma_memory,
            failure_context,
        ),
        namespace=f"{safe_key(stage_name)}_extractor",
        max_tokens=solver_max_tokens,
        temperature=1.0,
    )
    write_json(stage_dir / f"{safe_key(stage_name)}_document.json", raw)
    parsed = engine.structured(
        prompt=conjecture_parser(raw["final"]),
        namespace=f"{safe_key(stage_name)}_parser",
        schema_name="conjecture_parser",
        schema=CONJECTURE_SCHEMA,
        max_tokens=parser_max_tokens,
        temperature=0.1,
    )["parsed"]
    conjectures = list(parsed.get("conjectures") or [])
    negations = list(parsed.get("negations") or [])
    if len(conjectures) != len(negations) or len(conjectures) > 3:
        parsed = {"conjectures": [], "negations": [], "proof": parsed.get("proof", ""), "parser_rejected": True}
    elif any(not str(item).strip() for item in conjectures + negations):
        parsed = {"conjectures": [], "negations": [], "proof": parsed.get("proof", ""), "parser_rejected": True}
    else:
        parsed["parser_rejected"] = False
    write_json(final_path, parsed)
    return parsed


def verify_hypotheses(
    *,
    hypotheses: dict[str, Any],
    threshold: int,
    engine: ModelEngine,
    stage_dir: Path,
    stage_name: str,
    solver_max_tokens: int,
    grader_max_tokens: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    final_path = stage_dir / f"{safe_key(stage_name)}_result.json"
    if final_path.exists():
        value = json.loads(final_path.read_text(encoding="utf-8"))
        return value["proven"], value["failed"]
    pairs = list(zip(hypotheses.get("conjectures") or [], hypotheses.get("negations") or []))

    def solve_pair(item: tuple[int, tuple[str, str]]) -> dict[str, Any]:
        index, (positive, negative) = item
        sides = [("positive", positive), ("negative", negative)]

        def solve_side(side_item: tuple[str, str]) -> dict[str, Any]:
            side, claim = side_item
            response = engine.text(
                prompt=standalone_solver(claim),
                namespace=f"{safe_key(stage_name)}_{index}_{side}_solve",
                max_tokens=solver_max_tokens,
                temperature=1.0,
            )
            grade_response = engine.grade(
                prompt=inquisitorial_grader(claim, response["final"], None),
                namespace=f"{safe_key(stage_name)}_{index}_{side}_grade",
                max_tokens=grader_max_tokens,
                temperature=0.1,
            )
            return {
                "side": side,
                "claim": claim,
                "proof": response["final"],
                "grade": validate_grade(grade_response["parsed"]),
            }

        results = parallel_map(solve_side, sides, min(engine.concurrency, 2))
        return {"index": index, "positive": results[0], "negative": results[1]}

    pair_results = [solve_pair(item) for item in enumerate(pairs)]
    proven: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    for row in pair_results:
        positive_pass = (
            bool(row["positive"]["grade"].get("valid_scale"))
            and int(row["positive"]["grade"]["score"]) >= threshold
        )
        negative_pass = (
            bool(row["negative"]["grade"].get("valid_scale"))
            and int(row["negative"]["grade"]["score"]) >= threshold
        )
        if positive_pass != negative_pass:
            chosen = row["positive"] if positive_pass else row["negative"]
            proven.append(
                {
                    "source_index": row["index"],
                    "side": chosen["side"],
                    "claim": chosen["claim"],
                    "proof": chosen["proof"],
                    "grade": chosen["grade"],
                    "threshold": threshold,
                }
            )
        else:
            failed.append(
                {
                    "source_index": row["index"],
                    "status": "ambiguous",
                    "positive": row["positive"],
                    "negative": row["negative"],
                    "threshold": threshold,
                }
            )
    write_json(final_path, {"proven": proven, "failed": failed, "pair_results": pair_results})
    return proven, failed


def memory_augmented_dialectic(
    *,
    problem: str,
    engine: ModelEngine,
    pipeline_dir: Path,
    width: int,
    initial_iterations: int,
    conjecture_iterations: int,
    success_repetitions: int,
    threshold: int,
    enhancement_threshold: int,
    solver_max_tokens: int,
    grader_max_tokens: int,
    lazy_max_tokens: int,
    parser_max_tokens: int,
    initial_failed_lemma_memory: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Appendix Algorithm 1."""

    final_path = pipeline_dir / "pipeline_result.json"
    if final_path.exists():
        return json.loads(final_path.read_text(encoding="utf-8"))
    solution_memory: list[dict[str, Any]] = []
    lemma_memory: list[dict[str, Any]] = []
    failed_lemma_memory: list[dict[str, Any]] = list(initial_failed_lemma_memory or [])
    failure_context: list[dict[str, Any]] = []
    phase_log: list[dict[str, Any]] = []

    for iteration in range(initial_iterations):
        if iteration == 0 or not solution_memory:
            generated = dialectic_solve(
                problem=problem,
                context=None,
                count=width,
                engine=engine,
                stage_dir=pipeline_dir / f"phase1_iteration{iteration + 1}" / "zero_context",
                stage_name=f"p1_i{iteration + 1}_zero",
                solver_max_tokens=solver_max_tokens,
                grader_max_tokens=grader_max_tokens,
                lazy_max_tokens=lazy_max_tokens,
            )
        else:
            generated = dialectic_solve(
                problem=problem,
                context=None,
                count=1,
                engine=engine,
                stage_dir=pipeline_dir / f"phase1_iteration{iteration + 1}" / "zero_context",
                stage_name=f"p1_i{iteration + 1}_zero",
                solver_max_tokens=solver_max_tokens,
                grader_max_tokens=grader_max_tokens,
                lazy_max_tokens=lazy_max_tokens,
            )
            ranked = select_top(solution_memory, max(width - 1, 1))
            for branch in range(width - 1):
                source = ranked[min(branch, len(ranked) - 1)]
                generated.extend(
                    dialectic_solve(
                        problem=problem,
                        context={"prior_solution": source},
                        count=1,
                        engine=engine,
                        stage_dir=pipeline_dir / f"phase1_iteration{iteration + 1}" / f"guided_{branch + 1}",
                        stage_name=f"p1_i{iteration + 1}_guided{branch + 1}",
                        solver_max_tokens=solver_max_tokens,
                        grader_max_tokens=grader_max_tokens,
                        lazy_max_tokens=lazy_max_tokens,
                    )
                )
        solution_memory.extend(generated)
        verified, audits = verified_success(
            problem=problem,
            solutions=solution_memory,
            repetitions=success_repetitions,
            engine=engine,
            stage_dir=pipeline_dir / f"phase1_iteration{iteration + 1}" / "success_checks",
            stage_name=f"p1_i{iteration + 1}",
            grader_max_tokens=grader_max_tokens,
        )
        phase_log.append({"phase": 1, "iteration": iteration + 1, "generated": len(generated), "audits": audits})
        if verified is not None:
            result = {
                "termination": "phase1_verified_success",
                "solution": verified,
                "solution_memory": solution_memory,
                "lemma_memory": lemma_memory,
                "failed_lemma_memory": failed_lemma_memory,
                "failure_context": failure_context,
                "phase_log": phase_log,
            }
            write_json(final_path, result)
            return result

    for iteration in range(conjecture_iterations):
        iteration_dir = pipeline_dir / f"conjecture_iteration{iteration + 1}"
        seeds = select_top(solution_memory, 2)
        hypotheses = extract_hypotheses(
            problem=problem,
            seed_solutions=seeds,
            lemma_memory=lemma_memory,
            failed_lemma_memory=failed_lemma_memory,
            failure_context=failure_context,
            engine=engine,
            stage_dir=iteration_dir,
            stage_name=f"ci{iteration + 1}_hypotheses",
            solver_max_tokens=solver_max_tokens,
            parser_max_tokens=parser_max_tokens,
        )
        hypotheses, screened_out = screen_hypotheses_against_failed_memory(
            problem=problem,
            hypotheses=hypotheses,
            failed_lemma_memory=failed_lemma_memory,
            engine=engine,
            stage_dir=iteration_dir,
            stage_name=f"ci{iteration + 1}_hypotheses",
            parser_max_tokens=parser_max_tokens,
        )
        new_lemmas, new_failures = verify_hypotheses(
            hypotheses=hypotheses,
            threshold=threshold,
            engine=engine,
            stage_dir=iteration_dir,
            stage_name=f"ci{iteration + 1}_verify",
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
        )
        failed_lemma_memory = merge_failed_lemma_memory(
            failed_lemma_memory,
            build_failed_lemma_memory(
                hypotheses=hypotheses,
                proven=new_lemmas,
                failed=new_failures,
                source_iteration=f"conjecture_iteration{iteration + 1}",
            ),
        )
        lemma_memory.extend(new_lemmas)
        failure_context.extend(new_failures)
        context = {
            "verified_lemma_memory": lemma_memory,
            "failed_lemma_memory": failed_lemma_memory,
            "best_prior_solution": best(solution_memory),
            "partial_hypothesis_progress": new_failures,
        }
        guided = dialectic_solve(
            problem=problem,
            context=context,
            count=width - 1,
            engine=engine,
            stage_dir=iteration_dir / "guided",
            stage_name=f"ci{iteration + 1}_guided",
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )
        fresh = dialectic_solve(
            problem=problem,
            context=None,
            count=1,
            engine=engine,
            stage_dir=iteration_dir / "fresh",
            stage_name=f"ci{iteration + 1}_fresh",
            solver_max_tokens=solver_max_tokens,
            grader_max_tokens=grader_max_tokens,
            lazy_max_tokens=lazy_max_tokens,
        )
        final_group = guided + fresh
        solution_memory.extend(final_group)
        verified, audits = verified_success(
            problem=problem,
            solutions=final_group,
            repetitions=success_repetitions,
            engine=engine,
            stage_dir=iteration_dir / "success_checks",
            stage_name=f"ci{iteration + 1}",
            grader_max_tokens=grader_max_tokens,
        )
        phase_log.append(
            {
                "phase": "2+3",
                "iteration": iteration + 1,
                "hypothesis_count": len(hypotheses.get("conjectures") or []),
                "new_lemma_count": len(new_lemmas),
                "new_failure_count": len(new_failures),
                "screened_failed_lemma_count": len(screened_out),
                "failed_lemma_memory_count": len(failed_lemma_memory),
                "audits": audits,
            }
        )
        if verified is not None:
            result = {
                "termination": "phase3_verified_success",
                "solution": verified,
                "solution_memory": solution_memory,
                "lemma_memory": lemma_memory,
                "failed_lemma_memory": failed_lemma_memory,
                "failure_context": failure_context,
                "phase_log": phase_log,
            }
            write_json(final_path, result)
            return result

    phase4_dir = pipeline_dir / "phase4_post_enhancement"
    incumbent = best(solution_memory)
    incumbent_grades = independent_grades(
        problem=problem,
        solution=incumbent,
        repetitions=success_repetitions,
        engine=engine,
        stage_dir=phase4_dir,
        stage_name="incumbent_check",
        grader_max_tokens=grader_max_tokens,
    )
    if all(row["perfect"] for row in incumbent_grades):
        result = {
            "termination": "phase4_incumbent_all_perfect",
            "solution": incumbent,
            "solution_memory": solution_memory,
            "lemma_memory": lemma_memory,
            "failed_lemma_memory": failed_lemma_memory,
            "failure_context": failure_context,
            "phase_log": phase_log,
            "phase4": {"incumbent_grades": incumbent_grades},
        }
        write_json(final_path, result)
        return result

    gaps = extract_hypotheses(
        problem=problem,
        seed_solutions=[{"solution": incumbent, "independent_grades": incumbent_grades}],
        lemma_memory=lemma_memory,
        failed_lemma_memory=failed_lemma_memory,
        failure_context=failure_context,
        engine=engine,
        stage_dir=phase4_dir,
        stage_name="phase4_gaps",
        solver_max_tokens=solver_max_tokens,
        parser_max_tokens=parser_max_tokens,
    )
    gaps, phase4_screened_out = screen_hypotheses_against_failed_memory(
        problem=problem,
        hypotheses=gaps,
        failed_lemma_memory=failed_lemma_memory,
        engine=engine,
        stage_dir=phase4_dir,
        stage_name="phase4_gaps",
        parser_max_tokens=parser_max_tokens,
    )
    fixes, failed_fixes = verify_hypotheses(
        hypotheses=gaps,
        threshold=enhancement_threshold,
        engine=engine,
        stage_dir=phase4_dir,
        stage_name="phase4_verify",
        solver_max_tokens=solver_max_tokens,
        grader_max_tokens=grader_max_tokens,
    )
    failed_lemma_memory = merge_failed_lemma_memory(
        failed_lemma_memory,
        build_failed_lemma_memory(
            hypotheses=gaps,
            proven=fixes,
            failed=failed_fixes,
            source_iteration="phase4_post_enhancement",
        ),
    )
    better_group = dialectic_solve(
        problem=problem,
        context={
            "verified_fixes": fixes,
            "failed_or_partial_fixes": failed_fixes,
            "failed_lemma_memory": failed_lemma_memory,
        },
        count=width,
        engine=engine,
        stage_dir=phase4_dir / "better",
        stage_name="phase4_better",
        solver_max_tokens=solver_max_tokens,
        grader_max_tokens=grader_max_tokens,
        lazy_max_tokens=lazy_max_tokens,
    )
    better_grade_map: dict[str, list[dict[str, Any]]] = {}
    for index, candidate in enumerate(better_group):
        better_grade_map[candidate["solution_id"]] = independent_grades(
            problem=problem,
            solution=candidate,
            repetitions=success_repetitions,
            engine=engine,
            stage_dir=phase4_dir / "better_checks",
            stage_name=f"candidate_{index}",
            grader_max_tokens=grader_max_tokens,
        )
    better_candidate = max(
        better_group,
        key=lambda item: (
            mean_grade(better_grade_map[item["solution_id"]]),
            solution_rank(item),
        ),
    )
    better_mean = mean_grade(better_grade_map[better_candidate["solution_id"]])
    incumbent_mean = mean_grade(incumbent_grades)
    chosen = better_candidate if better_mean > incumbent_mean else incumbent
    result = {
        "termination": "phase4_mean_grade_comparison",
        "solution": chosen,
        "solution_memory": solution_memory + better_group,
        "lemma_memory": lemma_memory + fixes,
        "failed_lemma_memory": failed_lemma_memory,
        "failure_context": failure_context + failed_fixes,
        "phase_log": phase_log,
        "phase4": {
            "incumbent": incumbent,
            "incumbent_grades": incumbent_grades,
            "incumbent_mean": incumbent_mean,
            "gaps": gaps,
            "fixes": fixes,
            "failed_fixes": failed_fixes,
            "screened_failed_lemmas": phase4_screened_out,
            "better_group": better_group,
            "better_grade_map": better_grade_map,
            "better_candidate": better_candidate,
            "better_mean": better_mean,
        },
    }
    write_json(final_path, result)
    return result


def parallel_runs(
    *,
    problem: str,
    engine_factory: Any,
    output_dir: Path,
    run_count: int,
    pipeline_kwargs: dict[str, Any],
) -> dict[str, Any]:
    """Appendix Algorithm 4. On one GPU, complete runs are sequential."""

    results: list[dict[str, Any]] = []
    shared_failed_lemma_memory: list[dict[str, Any]] = []
    for index in range(run_count):
        engine = engine_factory(index)
        result = memory_augmented_dialectic(
            problem=problem,
            engine=engine,
            pipeline_dir=output_dir / f"pipeline_{index + 1}",
            initial_failed_lemma_memory=shared_failed_lemma_memory,
            **pipeline_kwargs,
        )
        results.append(result)
        shared_failed_lemma_memory = merge_failed_lemma_memory(
            shared_failed_lemma_memory,
            list(result.get("failed_lemma_memory") or []),
        )
    if len(results) == 1:
        return {
            "run_count": 1,
            "decision": "A",
            "selected": results[0],
            "runs": results,
            "shared_failed_lemma_memory": shared_failed_lemma_memory,
        }
    first, second = results[0], results[1]
    combiner_engine = engine_factory(10_000)
    combined = combiner_engine.structured(
        prompt=answer_combiner(
            problem,
            str(first["solution"]["proof"]),
            str(second["solution"]["proof"]),
            [first.get("phase_log"), second.get("phase_log")],
        ),
        namespace="algorithm4_answer_combiner",
        schema_name="answer_combiner",
        schema=COMBINER_SCHEMA,
        max_tokens=32_768,
        temperature=0.1,
    )["parsed"]
    chosen_index = 0 if combined["decision"] == "A" else 1
    return {
        "run_count": 2,
        "decision": combined["decision"],
        "combiner": combined,
        "selected": results[chosen_index],
        "runs": results,
        "shared_failed_lemma_memory": shared_failed_lemma_memory,
    }
