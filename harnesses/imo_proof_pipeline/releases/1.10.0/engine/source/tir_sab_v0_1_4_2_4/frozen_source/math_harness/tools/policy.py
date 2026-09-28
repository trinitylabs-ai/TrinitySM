"""Conservative selective routing and declarative operation planning."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping, Sequence

from .schemas import RouteDecision, stable_hash, validate_route_decision


def _dominant_answer(candidates: Sequence[Mapping[str, Any]]) -> tuple[str | None, int]:
    counts = Counter(
        str(item["extracted_answer"])
        for item in candidates
        if item.get("extracted_answer") is not None
    )
    if not counts:
        return None, 0
    answer, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return answer, count


def _problem_plans(
    *,
    run_id: str,
    problem_id: str,
    problem: str,
    claim_id: str,
    claimed_answer: str | None,
) -> list[dict[str, Any]]:
    plans: list[dict[str, Any]] = []

    compact = (
        problem.replace("$", "")
        .replace("\\left", "")
        .replace("\\right", "")
        .replace("\\(", "")
        .replace("\\)", "")
        .replace("\\[", "")
        .replace("\\]", "")
    )
    numeric_roots = [int(value) for value in re.findall(r"\(x-(\d+)\)", compact)]
    has_variable_root = bool(re.search(r"\(x-k\)", compact))
    if (
        len(numeric_roots) == 3
        and has_variable_root
        and "minimum at exactly two" in problem
    ):
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "algebraic_elimination_check",
                "arguments": {
                    "fixed_roots": numeric_roots,
                    "variable": "k",
                    "claimed_answer": claimed_answer,
                },
                "assumptions": ["k is positive", "the two minimizers are positive"],
                "backend_capability": "sympy_exact",
                "timeout_sec": 10,
                "memory_limit_mb": 512,
                "validator": "equal_minima_certificate_v1",
            }
        )
    dimensions = [
        (int(first), int(second))
        for first, second in re.findall(
            r"(\d+)\s*(?:\\times|×|x)\s*(\d+)", problem, flags=re.I
        )
    ]
    loop_matches = re.findall(
        r"partition\s+(?:a|the)\b.*?\binto\s+\$?\s*(\d+)\s*\$?\s+cell loops",
        problem,
        re.I | re.S,
    )
    lower_problem = problem.lower()
    if (
        dimensions
        and loop_matches
        and "cell loop" in lower_problem
        and ("rectangle" in lower_problem or "rectangular" in lower_problem)
    ):
        rows, columns = max(dimensions, key=lambda item: item[0] * item[1])
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "rectangular_loop_exact_cover",
                "arguments": {
                    "rows": rows,
                    "columns": columns,
                    "loop_count": int(loop_matches[-1]),
                    "claimed_answer": claimed_answer,
                },
                "assumptions": [
                    "loops are unordered",
                    "each grid cell belongs to exactly one loop",
                ],
                "backend_capability": "exact_cover_bitmask",
                "timeout_sec": 30,
                "memory_limit_mb": 1024,
                "validator": "rectangular_loop_certificate_v1",
            }
        )
    power_bound = re.search(
        r"(?:\\leq|<=)\s*(\d+)\s*\^\s*(\d+)", compact
    )
    divisibility_power = re.search(
        r"multiple\s+of\s+\$?\s*(\d+)\s*\^\s*(\d+)",
        compact,
        re.I,
    )
    output_modulus = re.search(
        r"remainder\s+when\b.*?\bdivided\s+by\s+\$?\s*(\d+)",
        compact,
        re.I | re.S,
    )
    if (
        "ordered triples of positive integers" in lower_problem
        and power_bound
        and divisibility_power
        and output_modulus
        and len(re.findall(r"\b[a-z]\s*\^\s*3\b", compact)) >= 3
    ):
        bound_base, bound_power = map(int, power_bound.groups())
        modulus_base, modulus_power = map(int, divisibility_power.groups())
        bound = pow(bound_base, bound_power)
        modulus = pow(modulus_base, modulus_power)
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "bitmask_dynamic_program",
                "arguments": {
                    "variable_count": 3,
                    "values": list(range(1, bound + 1)),
                    "power": 3,
                    "modulus": modulus,
                    "target": 0,
                    "output_modulus": int(output_modulus.group(1)),
                    "claimed_answer": claimed_answer,
                },
                "assumptions": [
                    "the triples are ordered",
                    "each variable ranges over every integer from 1 through "
                    f"{bound}",
                ],
                "backend_capability": "finite_residue_dp",
                "timeout_sec": 30,
                "memory_limit_mb": 1024,
                "validator": "residue_dp_validator_v1",
            }
        )

    tuple_match = re.search(r"ordered\s+(\d+)-tuples", lower_problem)
    no_space = re.sub(r"\s", "", problem)
    if tuple_match:
        tuple_count = int(tuple_match.group(1))
    else:
        tuple_count = 0
    cyclic_terms = [
        f"a_{index + 1}a_{(index + 1) % tuple_count + 1}"
        f"a_{(index + 3) % tuple_count + 1}"
        for index in range(tuple_count)
    ]
    tuple_domain_match = re.search(
        r"\\\{((?:-?\d+,)*-?\d+)\\\}", no_space
    )
    tuple_domain = (
        [int(value) for value in tuple_domain_match.group(1).split(",")]
        if tuple_domain_match
        else []
    )
    tuple_moduli = [
        int(value)
        for value in re.findall(
            r"multiple\s+of\s+\$?\s*(\d+)", problem, re.I
        )
    ]
    if (
        1 <= tuple_count <= 12
        and all(term in no_space for term in cyclic_terms)
        and tuple_domain
        and len(tuple_domain) <= 32
        and len(tuple_domain) == len(set(tuple_domain))
        and len(tuple_moduli) >= 2
        and len(set(tuple_moduli)) == 1
        and tuple_moduli[0] >= 2
    ):
        modulus = tuple_moduli[0]
        variables = [{"var": index} for index in range(tuple_count)]
        cubic_terms = [
            {
                "mul": [
                    {"var": index},
                    {"var": (index + 1) % tuple_count},
                    {"var": (index + 3) % tuple_count},
                ]
            }
            for index in range(tuple_count)
        ]
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "modular_tuple_enumeration",
                "arguments": {
                    "domains": [tuple_domain for _ in range(tuple_count)],
                    "constraints": [
                        {"eq": [{"mod": [{"add": variables}, modulus]}, 0]},
                        {"eq": [{"mod": [{"add": cubic_terms}, modulus]}, 0]},
                    ],
                    "claimed_answer": claimed_answer,
                },
                "assumptions": [
                    "tuple positions are ordered",
                    "the two displayed divisibility conditions are interpreted "
                    f"modulo {modulus}",
                ],
                "backend_capability": "finite_enumeration",
                "timeout_sec": 10,
                "memory_limit_mb": 512,
                "validator": "modular_tuple_validator_v1",
            }
        )

    # Generic bounded two-variable integer equations, including currency
    # systems where the statement supplies a total and two integral prices.
    currency = re.search(
        r"paid\s+a\s+total\s+of\b.*?(\d+).*?"
        r"cost\b.*?(\d+).*?cost\b.*?(\d+)",
        problem,
        re.I | re.S,
    )
    if currency:
        total, first_cost, second_cost = map(int, currency.groups())
        first_max = total // first_cost
        second_max = total // second_cost
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "bounded_integer_solutions",
                "arguments": {
                    "domains": [
                        list(range(first_max + 1)),
                        list(range(second_max + 1)),
                    ],
                    "constraints": [
                        {
                            "eq": [
                                {
                                    "add": [
                                        {"mul": [first_cost, {"var": 0}]},
                                        {"mul": [second_cost, {"var": 1}]},
                                    ]
                                },
                                total,
                            ]
                        }
                    ],
                    "claimed_answer": claimed_answer,
                },
                "assumptions": [
                    "item counts are nonnegative integers",
                    "the two displayed prices account for the full total",
                ],
                "backend_capability": "finite_enumeration",
                "timeout_sec": 10,
                "memory_limit_mb": 512,
                "validator": "bounded_integer_solutions_validator_v1",
            }
        )

    quadratic_pair = re.search(
        r"Suppose\s+that\s+\$?a=(\d+)\$?\s+and\s+\$?b=(\d+)\$?.*?"
        r"K\^\{?2\}?\+(\d+)\s*L\^\{?2\}?"
        r"=a\^\{?2\}?\+b\^\{?2\}?\-a\s*b",
        compact,
        re.I | re.S,
    )
    if quadratic_pair:
        a_value, b_value, coefficient = map(int, quadratic_pair.groups())
        target = a_value * a_value + b_value * b_value - a_value * b_value
        bound = int(target**0.5) + 1
        domain = list(range(-bound, bound + 1))
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "bounded_integer_solutions",
                "arguments": {
                    "domains": [domain, domain],
                    "constraints": [
                        {
                            "eq": [
                                {
                                    "add": [
                                        {"pow": [{"var": 0}, 2]},
                                        {
                                            "mul": [
                                                coefficient,
                                                {"pow": [{"var": 1}, 2]},
                                            ]
                                        },
                                    ]
                                },
                                target,
                            ]
                        }
                    ],
                    "claimed_answer": claimed_answer,
                },
                "assumptions": ["K and L range over all integers"],
                "backend_capability": "finite_enumeration",
                "timeout_sec": 10,
                "memory_limit_mb": 512,
                "validator": "bounded_integer_solutions_validator_v1",
            }
        )

    digit_expression = re.search(
        r"sum\s+of\s+the\s+digits.*?"
        r"\\left\((\d+)\^\{(\d+)\}\+(\d+)\\right\)\^\{(\d+)\}",
        problem,
        re.I | re.S,
    )
    if digit_expression:
        base, inner_power, addend, outer_power = map(
            int, digit_expression.groups()
        )
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "exact_integer_expression",
                "arguments": {
                    "expression": {
                        "pow": [
                            {
                                "add": [
                                    {"pow": [base, inner_power]},
                                    addend,
                                ]
                            },
                            outer_power,
                        ]
                    },
                    "output": "digit_sum",
                    "claimed_answer": claimed_answer,
                },
                "assumptions": ["digit sum is taken in base 10"],
                "backend_capability": "safe_integer_ast",
                "timeout_sec": 10,
                "memory_limit_mb": 256,
                "validator": "exact_integer_expression_validator_v1",
            }
        )

    divisor_threshold = re.search(
        r"smallest\s+positive\s+integer\s+\$?n\$?\s+such\s+that\s+"
        r"\$?n\^\{n\}\$?\s+has\s+at\s+least\s+([\d,]+)\s+positive\s+divisors",
        problem,
        re.I,
    )
    if divisor_threshold:
        threshold = int(divisor_threshold.group(1).replace(",", ""))
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "divisor_power_threshold",
                "arguments": {
                    "threshold": threshold,
                    "max_n": 10_000,
                    "claimed_answer": claimed_answer,
                },
                "assumptions": ["n is a positive integer"],
                "backend_capability": "exact_integer_search",
                "timeout_sec": 30,
                "memory_limit_mb": 512,
                "validator": "divisor_power_threshold_validator_v1",
            }
        )

    shifted_power_equation = re.fullmatch(
        r"Determineallrealvaluesofxforwhich"
        r"\(x([+-]\d+)\)\^\{(\d+)\}="
        r"\((\d*)x([+-]\d+)\)\^\{(\d+)\}\\?\\?\\?.*",
        re.sub(r"\s+|\$", "", problem),
        re.I,
    )
    if shifted_power_equation:
        left_shift, left_power, coefficient_text, right_shift, right_power = (
            shifted_power_equation.groups()
        )
        coefficient = int(coefficient_text or "1")
        symbol = {"symbol": "x"}
        plans.append(
            {
                "run_id": run_id,
                "problem_id": problem_id,
                "claim_id": claim_id,
                "operation": "polynomial_root_filter",
                "arguments": {
                    "symbols": ["x"],
                    "variable": "x",
                    "polynomial": {
                        "sub": [
                            {
                                "pow": [
                                    {"add": [symbol, int(left_shift)]},
                                    int(left_power),
                                ]
                            },
                            {
                                "pow": [
                                    {
                                        "add": [
                                            {"mul": [coefficient, symbol]},
                                            int(right_shift),
                                        ]
                                    },
                                    int(right_power),
                                ]
                            },
                        ]
                    },
                    "domain": "real",
                    "claimed_answer": claimed_answer,
                },
                "assumptions": ["x is real"],
                "backend_capability": "sympy_exact",
                "timeout_sec": 10,
                "memory_limit_mb": 512,
                "validator": "polynomial_root_filter_validator_v1",
            }
        )

    return plans


def route_problem(
    *,
    run_id: str,
    problem_id: str,
    problem: str,
    candidates: Sequence[Mapping[str, Any]],
    claims: Sequence[Mapping[str, Any]],
    reviews: Mapping[Any, Mapping[str, Any]],
    route_stage: str = "route1",
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return a deterministic route decision and typed plans for one problem."""

    dominant, dominant_count = _dominant_answer(candidates)
    answers = {
        str(item["extracted_answer"])
        for item in candidates
        if item.get("extracted_answer") is not None
    }
    reason_codes: set[str] = set()
    if len(answers) > 1:
        reason_codes.add("answer_disagreement")
    if len(answers) > 1 and any(
        sum(str(item.get("extracted_answer")) == answer for item in candidates) == 1
        for answer in answers
    ):
        reason_codes.add("sparse_minority_answer")
    claim_types = {str(item.get("claim_type")) for item in claims}
    for claim_type, reason in (
        ("algebraic_elimination", "unsupported_answer_changing_algebra"),
        ("recurrence_completeness", "exhaustiveness_claim"),
        ("finite_enumeration", "finite_state_space"),
        ("geometry_incidence", "unchecked_geometry_incidence"),
    ):
        if claim_type in claim_types:
            reason_codes.add(reason)
    strategies: set[str] = set()
    verifier_verdicts: set[str] = set()
    for candidate in candidates:
        key = (problem_id, str(candidate.get("node_id")))
        review_record = reviews.get(key, reviews.get(candidate.get("node_id"), {}))
        review = review_record.get("normalized_review", review_record)
        if isinstance(review, Mapping):
            if review.get("strategy_family"):
                strategies.add(str(review["strategy_family"]))
            if review.get("verdict"):
                verifier_verdicts.add(str(review["verdict"]))
    if len(verifier_verdicts) > 1:
        reason_codes.add("verifier_disagreement")
    if route_stage == "route2" and any(
        bool((item.get("answer_transition") or {}).get("changed"))
        for item in candidates
    ):
        reason_codes.add("changed_final_answer")
    if (
        len(candidates) >= 2
        and dominant_count == len(candidates)
        and len(strategies) <= 1
    ):
        reason_codes.add("unanimous_shared_derivation_risk")

    if claims:
        claim_id = str(claims[0]["claim_id"])
    else:
        claim_id = f"c_{stable_hash([problem_id, 'problem-level-exact-check'])[:16]}"
    plans = _problem_plans(
        run_id=run_id,
        problem_id=problem_id,
        problem=problem,
        claim_id=claim_id,
        claimed_answer=dominant,
    )
    if plans:
        reason_codes.add("supported_exact_operation")
        decision = RouteDecision.CALL
    elif reason_codes:
        decision = RouteDecision.UNSUPPORTED
    else:
        sufficiently_supported = (
            len(candidates) > 0
            and dominant_count / len(candidates) >= 0.75
            and len(strategies) >= 2
        )
        decision = RouteDecision.SKIP if sufficiently_supported else RouteDecision.UNSUPPORTED
        if not sufficiently_supported:
            reason_codes.add("insufficient_independent_support")
    risk = min(
        1.0,
        0.10
        + 0.15 * len(reason_codes)
        + (0.20 if "unanimous_shared_derivation_risk" in reason_codes else 0.0),
    )
    route = validate_route_decision(
        {
            "run_id": run_id,
            "problem_id": problem_id,
            "route_stage": route_stage,
            "decision": decision.value,
            "risk_score": risk,
            "reason_codes": sorted(reason_codes),
            "critical_claim_ids": sorted(
                {str(item["claim_id"]) for item in claims}
            ),
            "planned_operations": [str(item["operation"]) for item in plans],
        }
    )
    return route, plans
