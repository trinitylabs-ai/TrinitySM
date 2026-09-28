"""Independent validation for exact sign-partitioned equation systems."""

from __future__ import annotations

from typing import Any, Mapping

from ..expressions import to_sympy


VALIDATOR_VERSION = "piecewise-branch-validator-v1"


def _condition_holds(
    condition: Mapping[str, Any],
    solution: Mapping[Any, Any],
    symbols: Mapping[str, Any],
) -> bool:
    import sympy as sp

    value = sp.simplify(
        to_sympy(condition["expression"], symbols).subs(solution)
    )
    relation = str(condition["relation"])
    predicates = {
        "zero": value == 0,
        "nonzero": value.is_zero is False,
        "positive": value.is_positive is True,
        "negative": value.is_negative is True,
        "nonnegative": value.is_nonnegative is True,
        "nonpositive": value.is_nonpositive is True,
    }
    if relation not in predicates:
        raise ValueError(f"unsupported sign relation: {relation}")
    return bool(predicates[relation])


def _equations_hold(equations, solution: Mapping[Any, Any]) -> bool:
    import sympy as sp

    return all(sp.simplify(equation.subs(solution)) == 0 for equation in equations)


def _canonical_branch_outputs(
    arguments: Mapping[str, Any],
    branch: Mapping[str, Any],
    *,
    symbols: Mapping[str, Any],
    solve_for: list[Any],
    original_equations: list[Any],
    split_expression: Any,
    output_expression: Any,
) -> tuple[list[str], int]:
    import sympy as sp

    equations = [
        to_sympy(value, symbols) for value in branch["equations"]
    ]
    raw_solutions = sp.solve(equations, solve_for, dict=True)
    outputs: list[Any] = []
    for solution in raw_solutions:
        if not all(symbol in solution for symbol in solve_for):
            continue
        split_condition = {
            "relation": branch["split_relation"],
            "expression": arguments["split_expression"],
        }
        if not _condition_holds(split_condition, solution, symbols):
            continue
        if not all(
            _condition_holds(condition, solution, symbols)
            for condition in arguments.get("common_conditions", [])
        ):
            continue
        if not all(
            _condition_holds(condition, solution, symbols)
            for condition in branch.get("conditions", [])
        ):
            continue
        if not _equations_hold(equations, solution):
            continue
        if not _equations_hold(original_equations, solution):
            continue
        output = sp.cancel(sp.simplify(output_expression.subs(solution)))
        if not any(sp.simplify(output - prior) == 0 for prior in outputs):
            outputs.append(output)
    return [str(value) for value in outputs], len(raw_solutions)


def validate_piecewise_branch_system(
    arguments: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Re-solve every branch and the omitted zero boundary independently."""

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
    independent_branches: list[dict[str, Any]] = []
    independent_union: list[Any] = []

    for branch in arguments["branches"]:
        output_strings, raw_count = _canonical_branch_outputs(
            arguments,
            branch,
            symbols=symbols,
            solve_for=solve_for,
            original_equations=original_equations,
            split_expression=split_expression,
            output_expression=output_expression,
        )
        outputs = [sp.sympify(value) for value in output_strings]
        independent_branches.append(
            {
                "branch_id": branch["branch_id"],
                "split_relation": branch["split_relation"],
                "raw_solution_count": raw_count,
                "outputs": output_strings,
            }
        )
        for output in outputs:
            if not any(
                sp.simplify(output - prior) == 0
                for prior in independent_union
            ):
                independent_union.append(output)

    boundary_raw = sp.solve(
        [*original_equations, split_expression],
        solve_for,
        dict=True,
    )
    boundary_solutions = [
        solution
        for solution in boundary_raw
        if all(symbol in solution for symbol in solve_for)
        and _equations_hold(original_equations, solution)
        and sp.simplify(split_expression.subs(solution)) == 0
        and all(
            _condition_holds(condition, solution, symbols)
            for condition in arguments.get("common_conditions", [])
        )
    ]

    normalized = dict(result.get("normalized_result") or {})
    reported_branches = normalized.get("branches")
    branch_shape_matches = (
        isinstance(reported_branches, list)
        and len(reported_branches) == len(independent_branches)
    )
    branch_outputs_match = branch_shape_matches
    if branch_shape_matches:
        for expected, reported in zip(independent_branches, reported_branches):
            reported_outputs = [
                str(item.get("output"))
                for item in reported.get("accepted_solutions", [])
                if isinstance(item, Mapping)
            ]
            if (
                reported.get("branch_id") != expected["branch_id"]
                or reported.get("split_relation") != expected["split_relation"]
                or reported.get("raw_solution_count")
                != expected["raw_solution_count"]
                or reported_outputs != expected["outputs"]
            ):
                branch_outputs_match = False
                break

    expected_union = [str(value) for value in independent_union]
    union_matches = normalized.get("union_outputs") == expected_union
    boundary_matches = (
        normalized.get("boundary_solution_count") == len(boundary_solutions)
        and normalized.get("branch_partition_complete")
        is (len(boundary_solutions) == 0)
    )
    nonempty_branches = all(
        bool(branch["outputs"]) for branch in independent_branches
    )
    passed = (
        branch_outputs_match
        and union_matches
        and boundary_matches
        and not boundary_solutions
        and nonempty_branches
    )
    return {
        "passed": bool(passed),
        "details": {
            "independent_branches": independent_branches,
            "independent_union_outputs": expected_union,
            "independent_boundary_solution_count": len(boundary_solutions),
            "branch_outputs_match": branch_outputs_match,
            "union_matches": union_matches,
            "boundary_matches": boundary_matches,
            "every_branch_nonempty": nonempty_branches,
        },
        "version": VALIDATOR_VERSION,
    }
