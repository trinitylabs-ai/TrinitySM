"""Generic exact execution for exhaustive and sign-partitioned systems."""

from __future__ import annotations

from typing import Any, Mapping

from ..expressions import to_sympy
from .base import backend_result, exact_value_latex
from .piecewise import sign_condition_holds


def _equations_hold(equations, solution: Mapping[Any, Any]) -> bool:
    import sympy as sp

    return all(sp.simplify(equation.subs(solution)) == 0 for equation in equations)


def _complete_solution(solution: Mapping[Any, Any], solve_for) -> bool:
    return all(symbol in solution for symbol in solve_for)


def _append_symbolically_unique(values: list[Any], value: Any) -> None:
    import sympy as sp

    if not any(sp.simplify(value - prior) == 0 for prior in values):
        values.append(value)


def solve_exact_branch_system(arguments: dict[str, Any]) -> dict[str, Any]:
    """Solve all declared branches and prove the declared partition complete."""

    import sympy as sp

    symbols = {
        name: sp.Symbol(name, real=True)
        for name in arguments["symbols"]
    }
    solve_for = [symbols[name] for name in arguments["solve_for"]]
    original_equations = [
        to_sympy(value, symbols) for value in arguments["original_equations"]
    ]
    output_expression = to_sympy(arguments["output_expression"], symbols)
    common_conditions = list(arguments.get("common_conditions") or [])
    partition = dict(arguments["partition"])
    partition_kind = str(partition["kind"])
    split_expression = (
        to_sympy(partition["expression"], symbols)
        if partition_kind == "sign"
        else None
    )
    branch_results: list[dict[str, Any]] = []
    union_outputs: list[Any] = []
    all_raw_solutions_complete = True

    for branch in arguments["branches"]:
        if partition_kind == "exhaustive_solutions":
            equations = list(original_equations)
            partition_condition = None
        else:
            equations = [
                to_sympy(value, symbols)
                for value in branch["equations"]
            ]
            partition_condition = {
                "relation": branch["partition_relation"],
                "expression": partition["expression"],
            }
        raw_solutions = sp.solve(equations, solve_for, dict=True)
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        for solution in raw_solutions:
            if not _complete_solution(solution, solve_for):
                all_raw_solutions_complete = False
                rejected.append(
                    {
                        "reason": "partial_solution",
                        "solution": {
                            str(key): str(sp.simplify(value))
                            for key, value in solution.items()
                        },
                    }
                )
                continue
            checks = {
                "partition": (
                    True
                    if partition_condition is None
                    else sign_condition_holds(
                        partition_condition, solution, symbols
                    )
                ),
                "common_conditions": all(
                    sign_condition_holds(condition, solution, symbols)
                    for condition in common_conditions
                ),
                "branch_conditions": all(
                    sign_condition_holds(condition, solution, symbols)
                    for condition in branch.get("conditions", [])
                ),
                "branch_equations": _equations_hold(equations, solution),
                "original_equations": _equations_hold(
                    original_equations, solution
                ),
            }
            if not all(checks.values()):
                rejected.append(
                    {
                        "reason": "predicate_or_substitution_rejection",
                        "solution": {
                            str(symbol): str(sp.simplify(solution[symbol]))
                            for symbol in solve_for
                        },
                        "checks": checks,
                    }
                )
                continue
            output = sp.cancel(sp.simplify(output_expression.subs(solution)))
            accepted.append(
                {
                    "solution": {
                        str(symbol): str(sp.simplify(solution[symbol]))
                        for symbol in solve_for
                    },
                    "output": str(output),
                    "output_latex": exact_value_latex(output),
                    "original_substitution_checks": [
                        str(sp.simplify(equation.subs(solution)))
                        for equation in original_equations
                    ],
                }
            )
            _append_symbolically_unique(union_outputs, output)
        branch_results.append(
            {
                "branch_id": branch["branch_id"],
                "partition_relation": branch.get("partition_relation"),
                "raw_solution_count": len(raw_solutions),
                "accepted_solutions": accepted,
                "rejected_solutions": rejected,
            }
        )

    boundary_solutions: list[dict[Any, Any]] = []
    if partition_kind == "sign":
        boundary_raw = sp.solve(
            [*original_equations, split_expression],
            solve_for,
            dict=True,
        )
        boundary_solutions = [
            solution
            for solution in boundary_raw
            if _complete_solution(solution, solve_for)
            and _equations_hold(original_equations, solution)
            and sp.simplify(split_expression.subs(solution)) == 0
            and all(
                sign_condition_holds(condition, solution, symbols)
                for condition in common_conditions
            )
        ]
        partition_complete = not boundary_solutions
    else:
        partition_complete = all_raw_solutions_complete

    union_latex = [exact_value_latex(value) for value in union_outputs]
    derived_answer = ",".join(f"${value}$" for value in union_latex)
    return backend_result(
        normalized_result={
            "partition_kind": partition_kind,
            "branches": branch_results,
            "union_outputs": [str(value) for value in union_outputs],
            "union_outputs_latex": union_latex,
            "boundary_solution_count": len(boundary_solutions),
            "branch_partition_complete": partition_complete,
        },
        certificate={
            "method": (
                "exact_exhaustive_solution_filter"
                if partition_kind == "exhaustive_solutions"
                else "exact_sign_partition"
            ),
            "all_raw_solutions_complete": all_raw_solutions_complete,
            "zero_boundary_unsatisfiable": (
                partition_complete if partition_kind == "sign" else None
            ),
            "boundary_solutions": [
                {
                    str(symbol): str(sp.simplify(solution[symbol]))
                    for symbol in solve_for
                }
                for solution in boundary_solutions
            ],
        },
        checked_claim=(
            "Every exact solution was classified by executable predicates, "
            "all accepted solutions satisfy the original equations, and the "
            "declared branch partition is complete."
        ),
        derived_answer=derived_answer or None,
    )
