"""Independent validation for generic exact branch systems."""

from __future__ import annotations

from typing import Any, Mapping

from ..expressions import to_sympy


VALIDATOR_VERSION = "exact-branch-system-validator-v1"


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


def _append_unique(values: list[Any], value: Any) -> None:
    import sympy as sp

    if not any(sp.simplify(value - prior) == 0 for prior in values):
        values.append(value)


def validate_exact_branch_system(
    arguments: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Independently enumerate branches, filters, and any zero boundary."""

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
    independent_branches: list[dict[str, Any]] = []
    independent_union: list[Any] = []
    all_raw_complete = True

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
        outputs: list[Any] = []
        accepted_solution_strings: list[dict[str, str]] = []
        rejected_count = 0
        for solution in raw_solutions:
            if not all(symbol in solution for symbol in solve_for):
                all_raw_complete = False
                rejected_count += 1
                continue
            valid = (
                (
                    partition_condition is None
                    or _condition_holds(
                        partition_condition, solution, symbols
                    )
                )
                and all(
                    _condition_holds(condition, solution, symbols)
                    for condition in common_conditions
                )
                and all(
                    _condition_holds(condition, solution, symbols)
                    for condition in branch.get("conditions", [])
                )
                and _equations_hold(equations, solution)
                and _equations_hold(original_equations, solution)
            )
            if not valid:
                rejected_count += 1
                continue
            output = sp.cancel(sp.simplify(output_expression.subs(solution)))
            _append_unique(outputs, output)
            _append_unique(independent_union, output)
            accepted_solution_strings.append(
                {
                    str(symbol): str(sp.simplify(solution[symbol]))
                    for symbol in solve_for
                }
            )
        independent_branches.append(
            {
                "branch_id": branch["branch_id"],
                "partition_relation": branch.get("partition_relation"),
                "raw_solution_count": len(raw_solutions),
                "accepted_solutions": accepted_solution_strings,
                "outputs": [str(value) for value in outputs],
                "rejected_solution_count": rejected_count,
            }
        )

    boundary_solutions: list[dict[Any, Any]] = []
    if partition_kind == "sign":
        split_expression = to_sympy(partition["expression"], symbols)
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
                for condition in common_conditions
            )
        ]
        independent_complete = not boundary_solutions
    else:
        independent_complete = all_raw_complete

    normalized = dict(result.get("normalized_result") or {})
    reported_branches = normalized.get("branches")
    branches_match = (
        isinstance(reported_branches, list)
        and len(reported_branches) == len(independent_branches)
    )
    if branches_match:
        for expected, reported in zip(independent_branches, reported_branches):
            reported_outputs = [
                str(item.get("output"))
                for item in reported.get("accepted_solutions", [])
                if isinstance(item, Mapping)
            ]
            reported_solution_strings = [
                dict(item.get("solution") or {})
                for item in reported.get("accepted_solutions", [])
                if isinstance(item, Mapping)
            ]
            if (
                reported.get("branch_id") != expected["branch_id"]
                or reported.get("partition_relation")
                != expected["partition_relation"]
                or reported.get("raw_solution_count")
                != expected["raw_solution_count"]
                or reported_outputs != expected["outputs"]
                or reported_solution_strings
                != expected["accepted_solutions"]
                or len(reported.get("rejected_solutions", []))
                != expected["rejected_solution_count"]
            ):
                branches_match = False
                break

    expected_union = [str(value) for value in independent_union]
    union_matches = normalized.get("union_outputs") == expected_union
    completeness_matches = (
        normalized.get("partition_kind") == partition_kind
        and normalized.get("boundary_solution_count")
        == len(boundary_solutions)
        and normalized.get("branch_partition_complete")
        is independent_complete
    )
    every_output_nonempty = bool(independent_union)
    passed = (
        branches_match
        and union_matches
        and completeness_matches
        and independent_complete
        and every_output_nonempty
    )
    return {
        "passed": bool(passed),
        "details": {
            "independent_branches": independent_branches,
            "independent_union_outputs": expected_union,
            "independent_boundary_solution_count": len(boundary_solutions),
            "independent_partition_complete": independent_complete,
            "branches_match": branches_match,
            "union_matches": union_matches,
            "completeness_matches": completeness_matches,
            "output_nonempty": every_output_nonempty,
        },
        "version": VALIDATOR_VERSION,
    }
