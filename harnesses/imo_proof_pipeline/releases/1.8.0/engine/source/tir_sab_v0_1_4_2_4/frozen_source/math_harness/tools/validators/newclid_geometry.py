"""Independent validation for Newclid geometry-proof evidence."""

from __future__ import annotations

import hashlib
from typing import Any


VALIDATOR_VERSION = "newclid-geometry-proof-validator-v1"


def _jgex_program(arguments: dict[str, Any]) -> str:
    clauses = []
    for construction in arguments["constructions"]:
        clauses.append(
            " ".join(
                [
                    *construction["outputs"],
                    "=",
                    construction["construction"],
                    *construction["arguments"],
                ]
            )
        )
    goals = [
        " ".join([goal["predicate"], *goal["arguments"]])
        for goal in arguments["goals"]
    ]
    return "; ".join(clauses) + " ? " + "; ".join(goals)


def validate_newclid_geometry_proof(
    arguments: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Re-prove the goals with Newclid's Python matcher and used rules only."""

    from newclid import GeometricSolverBuilder
    from newclid.all_rules import ALL_RULES
    from newclid.api import PythonDefault
    from newclid.jgex.problem_builder import JGEXProblemBuilder

    normalized = dict(result.get("normalized_result") or {})
    certificate = dict(result.get("certificate") or {})
    program = _jgex_program(arguments)
    proof = str(certificate.get("proof") or "")
    proof_digest_matches = (
        hashlib.sha256(proof.encode("utf-8")).hexdigest()
        == normalized.get("proof_digest")
    )
    used_rule_ids = normalized.get("used_rule_ids")
    known_rules = {rule.id: rule for rule in ALL_RULES}
    rule_ids_valid = bool(
        isinstance(used_rule_ids, list)
        and all(
            isinstance(rule_id, str) and rule_id in known_rules
            for rule_id in used_rule_ids
        )
    )
    independent_proved = False
    independent_goals: list[str] = []
    independent_error: str | None = None
    if rule_ids_valid:
        try:
            problem = (
                JGEXProblemBuilder(rng=int(arguments["seed"]) + 1)
                .with_problem_from_txt(program, "math_harness_validation")
                .build()
            )
            independent_goals = [str(goal) for goal in problem.goals]
            solver = (
                GeometricSolverBuilder(
                    rng=int(arguments["seed"]) + 1,
                    api_default=PythonDefault(use_sympy_ar=False),
                )
                .with_rules([known_rules[rule_id] for rule_id in used_rule_ids])
                .build(problem)
            )
            independent_proved = bool(solver.run())
        except Exception as exc:
            independent_error = f"{type(exc).__name__}: {exc}"
    expected_goals = [
        " ".join([goal["predicate"], *goal["arguments"]])
        for goal in arguments["goals"]
    ]
    goals_match = bool(
        normalized.get("goals") == expected_goals
        and len(independent_goals) == len(expected_goals)
    )
    passed = bool(
        normalized.get("proved") is True
        and independent_proved
        and goals_match
        and rule_ids_valid
        and proof_digest_matches
        and certificate.get("jgex_program") == program
    )
    return {
        "passed": passed,
        "details": {
            "independent_proved": independent_proved,
            "independent_goals": independent_goals,
            "used_rule_ids_valid": rule_ids_valid,
            "proof_digest_matches": proof_digest_matches,
            "program_matches": certificate.get("jgex_program") == program,
            "independent_error": independent_error,
        },
        "version": VALIDATOR_VERSION,
    }
