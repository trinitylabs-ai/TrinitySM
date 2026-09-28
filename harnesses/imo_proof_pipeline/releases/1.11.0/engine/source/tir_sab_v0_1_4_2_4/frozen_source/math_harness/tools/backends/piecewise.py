"""Bounded exact execution for explicit sign-partitioned equation systems."""

from __future__ import annotations

from typing import Any, Mapping

from ..expressions import to_sympy
from .base import backend_result, exact_value_latex


def sign_condition_holds(
    condition: Mapping[str, Any],
    solution: Mapping[Any, Any],
    symbols: Mapping[str, Any],
) -> bool:
    import sympy as sp

    value = sp.simplify(
        to_sympy(condition["expression"], symbols).subs(solution)
    )
    relation = str(condition["relation"])
    if relation == "zero":
        return value == 0
    if relation == "nonzero":
        return value.is_zero is False
    if relation == "positive":
        return value.is_positive is True
    if relation == "negative":
        return value.is_negative is True
    if relation == "nonnegative":
        return value.is_nonnegative is True
    if relation == "nonpositive":
        return value.is_nonpositive is True
    raise ValueError(f"unsupported sign relation: {relation}")


def _equations_hold(equations, solution: Mapping[Any, Any]) -> bool:
    import sympy as sp

    return all(sp.simplify(equation.subs(solution)) == 0 for equation in equations)


def _complete_solution(solution: Mapping[Any, Any], solve_for) -> bool:
    return all(symbol in solution for symbol in solve_for)


def solve_piecewise_branch_system(arguments: dict[str, Any]) -> dict[str, Any]:
    """Solve two explicit sign branches and prove the zero boundary empty."""

    import sympy as sp

    symbols = {
        name: sp.Symbol(name, real=True)
        for name in arguments["symbols"]
    }
    solve_for = [symbols[name] for name in arguments["solve_for"]]
    original_equations = [
        to_sympy(value, symbols) for value in arguments["original_equations"]
    ]
    split_expression = to_sympy(arguments["split_expression"], symbols)
    output_expression = to_sympy(arguments["output_expression"], symbols)
    common_conditions = list(arguments.get("common_conditions") or [])
    branch_results: list[dict[str, Any]] = []
    union_outputs: list[Any] = []

    for branch in arguments["branches"]:
        equations = [
            to_sympy(value, symbols) for value in branch["equations"]
        ]
        raw_solutions = sp.solve(equations, solve_for, dict=True)
        accepted: list[dict[str, Any]] = []
        for solution in raw_solutions:
            if not _complete_solution(solution, solve_for):
                continue
            split_condition = {
                "relation": branch["split_relation"],
                "expression": arguments["split_expression"],
            }
            if not sign_condition_holds(split_condition, solution, symbols):
                continue
            if not all(
                sign_condition_holds(condition, solution, symbols)
                for condition in common_conditions
            ):
                continue
            if not all(
                sign_condition_holds(condition, solution, symbols)
                for condition in branch.get("conditions", [])
            ):
                continue
            if not _equations_hold(equations, solution):
                continue
            if not _equations_hold(original_equations, solution):
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
            if output not in union_outputs:
                union_outputs.append(output)
        branch_results.append(
            {
                "branch_id": branch["branch_id"],
                "split_relation": branch["split_relation"],
                "raw_solution_count": len(raw_solutions),
                "accepted_solutions": accepted,
            }
        )

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
    union_latex = [exact_value_latex(value) for value in union_outputs]
    derived_answer = ",".join(f"${value}$" for value in union_latex)
    return backend_result(
        normalized_result={
            "branches": branch_results,
            "union_outputs": [str(value) for value in union_outputs],
            "union_outputs_latex": union_latex,
            "boundary_solution_count": len(boundary_solutions),
            "branch_partition_complete": partition_complete,
        },
        certificate={
            "method": "explicit_sign_partition_and_exact_substitution",
            "split_expression": str(split_expression),
            "covered_signs": [
                str(branch["split_relation"])
                for branch in arguments["branches"]
            ],
            "zero_boundary_unsatisfiable": partition_complete,
            "boundary_solutions": [
                {
                    str(symbol): str(sp.simplify(solution[symbol]))
                    for symbol in solve_for
                }
                for solution in boundary_solutions
            ],
        },
        checked_claim=(
            "Every sign branch was solved exactly, every solution satisfies "
            "the unsplit equations, and the excluded zero boundary is empty."
        ),
        derived_answer=derived_answer or None,
    )
