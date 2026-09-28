"""Operation-specific declarative argument validation."""

from __future__ import annotations

import math
import re
from typing import Any, Mapping

from .expressions import validate_expression, validate_symbol_name
from .finite_expressions import validate_finite_expression


def _symbols(arguments: Mapping[str, Any]) -> list[str]:
    values = arguments.get("symbols", [])
    if (
        not isinstance(values, list)
        or len(values) > 32
        or not all(isinstance(value, str) for value in values)
    ):
        raise ValueError("symbols must be a list of at most 32 names")
    result = [validate_symbol_name(value) for value in values]
    if len(set(result)) != len(result):
        raise ValueError("symbols must be unique")
    return result


def _sign_condition(
    value: Any,
    *,
    allowed_symbols: frozenset[str],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("sign condition must be an object")
    relation = str(value.get("relation"))
    if relation not in {
        "positive",
        "negative",
        "nonnegative",
        "nonpositive",
        "zero",
        "nonzero",
    }:
        raise ValueError("sign condition relation is unsupported")
    return {
        "relation": relation,
        "expression": validate_expression(
            value.get("expression"),
            allowed_symbols=allowed_symbols,
        ),
    }


_NEWCLID_POINT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")
_NEWCLID_NUMERIC_TOKEN_RE = re.compile(r"^-?\d+(?:/\d+)?$")


def _newclid_token(value: Any, *, label: str) -> str:
    token = str(value)
    if not (
        _NEWCLID_POINT_RE.fullmatch(token)
        or _NEWCLID_NUMERIC_TOKEN_RE.fullmatch(token)
    ):
        raise ValueError(f"{label} is not a safe Newclid token")
    return token


def validate_operation_arguments(
    operation: str, arguments_value: Mapping[str, Any]
) -> dict[str, Any]:
    arguments = dict(arguments_value)
    claimed = arguments.pop("claimed_answer", None)
    if claimed is not None:
        claimed = str(claimed)
        if len(claimed) > 4096:
            raise ValueError("claimed_answer is too long")
    if operation in {
        "expand_and_compare",
        "simplify_identity",
        "factor_and_reexpand",
        "solve_and_substitute",
        "polynomial_root_filter",
    }:
        symbols = _symbols(arguments)
        allowed = frozenset(symbols)
        if operation in {"expand_and_compare", "simplify_identity"}:
            arguments["left"] = validate_expression(
                arguments["left"], allowed_symbols=allowed
            )
            arguments["right"] = validate_expression(
                arguments["right"], allowed_symbols=allowed
            )
        elif operation == "factor_and_reexpand":
            arguments["expression"] = validate_expression(
                arguments["expression"], allowed_symbols=allowed
            )
        elif operation == "solve_and_substitute":
            equations = arguments.get("equations")
            solve_for = arguments.get("solve_for")
            if (
                not isinstance(equations, list)
                or not 1 <= len(equations) <= 32
                or not isinstance(solve_for, list)
                or not 1 <= len(solve_for) <= len(symbols)
            ):
                raise ValueError("solve requires bounded equations and solve_for lists")
            arguments["equations"] = [
                validate_expression(value, allowed_symbols=allowed)
                for value in equations
            ]
            arguments["solve_for"] = [
                validate_symbol_name(value) for value in solve_for
            ]
            if any(value not in allowed for value in arguments["solve_for"]):
                raise ValueError("solve_for contains an unregistered symbol")
        else:
            variable = validate_symbol_name(arguments["variable"])
            if variable not in allowed:
                raise ValueError("polynomial variable is not registered")
            arguments["variable"] = variable
            arguments["polynomial"] = validate_expression(
                arguments["polynomial"], allowed_symbols=allowed
            )
            domain = str(arguments.get("domain", "real"))
            if domain not in {"complex", "real", "positive", "nonnegative", "integer"}:
                raise ValueError("unsupported root-filter domain")
            arguments["domain"] = domain
        arguments["symbols"] = symbols
    elif operation == "exact_modular_evaluation":
        arguments = {
            "base": int(arguments["base"]),
            "exponent": int(arguments["exponent"]),
            "modulus": int(arguments["modulus"]),
        }
        if arguments["exponent"] < 0:
            raise ValueError("exponent must be nonnegative")
        if not 2 <= arguments["modulus"] <= 10**12:
            raise ValueError("modulus is outside the supported range")
    elif operation == "gcd":
        values = arguments.get("values")
        if not isinstance(values, list) or not 2 <= len(values) <= 1024:
            raise ValueError("gcd values must contain 2 through 1024 integers")
        arguments = {"values": [int(value) for value in values]}
    elif operation == "prime_factorization":
        arguments = {"value": int(arguments["value"])}
        if arguments["value"] == 0:
            raise ValueError("zero has no prime factorization")
    elif operation == "determinant":
        matrix = arguments.get("matrix")
        if (
            not isinstance(matrix, list)
            or not matrix
            or len(matrix) > 64
            or any(
                not isinstance(row, list) or len(row) != len(matrix)
                for row in matrix
            )
            or any(
                not isinstance(value, int) or isinstance(value, bool)
                for row in matrix
                for value in row
            )
        ):
            raise ValueError("matrix must be a square integer matrix up to 64 by 64")
        arguments = {"matrix": matrix}
    elif operation == "algebraic_elimination_check":
        roots = arguments.get("fixed_roots")
        if (
            not isinstance(roots, list)
            or len(roots) != 3
            or any(not isinstance(value, int) or value <= 0 for value in roots)
            or len(set(roots)) != 3
        ):
            raise ValueError("fixed_roots must be three distinct positive integers")
        arguments = {
            "fixed_roots": roots,
            "variable": validate_symbol_name(arguments.get("variable", "k")),
        }
    elif operation == "rectangular_loop_exact_cover":
        arguments = {
            "rows": int(arguments["rows"]),
            "columns": int(arguments["columns"]),
            "loop_count": int(arguments["loop_count"]),
        }
        if not 2 <= arguments["rows"] <= 16 or not 2 <= arguments["columns"] <= 16:
            raise ValueError("rectangular-loop grid dimensions must be 2 through 16")
        if not 1 <= arguments["loop_count"] <= 16:
            raise ValueError("loop_count must be 1 through 16")
    elif operation in {
        "enumerate_finite_assignments",
        "modular_tuple_enumeration",
        "bounded_integer_solutions",
    }:
        domains_value = arguments.get("domains")
        constraints_value = arguments.get("constraints")
        if (
            not isinstance(domains_value, list)
            or not 1 <= len(domains_value) <= 32
            or not isinstance(constraints_value, list)
            or not 1 <= len(constraints_value) <= 64
        ):
            raise ValueError(
                "finite enumeration requires 1 through 32 domains and "
                "1 through 64 constraints"
            )
        domains: list[list[int]] = []
        assignment_space_size = 1
        for domain_value in domains_value:
            if (
                not isinstance(domain_value, list)
                or not 1 <= len(domain_value) <= 4096
                or any(
                    not isinstance(item, int) or isinstance(item, bool)
                    for item in domain_value
                )
            ):
                raise ValueError(
                    "each finite domain must be a nonempty bounded integer list"
                )
            domain = list(dict.fromkeys(domain_value))
            if len(domain) != len(domain_value):
                raise ValueError("finite domains must not contain duplicates")
            if any(abs(item) > 10**12 for item in domain):
                raise ValueError("finite domain integer is outside the supported range")
            assignment_space_size *= len(domain)
            if assignment_space_size > 1_000_000:
                raise ValueError("finite assignment space exceeds 1,000,000")
            domains.append(domain)
        constraints = [
            validate_finite_expression(value, variable_count=len(domains))
            for value in constraints_value
        ]
        arguments = {"domains": domains, "constraints": constraints}
    elif operation == "exact_integer_expression":
        output = str(arguments_value.get("output", "value"))
        if output not in {"value", "digit_sum", "residue"}:
            raise ValueError("unsupported exact integer output")
        arguments = {
            "expression": validate_finite_expression(
                arguments["expression"], variable_count=0
            ),
            "output": output,
        }
        modulus_value = arguments_value.get("modulus")
        if modulus_value is not None:
            modulus = int(modulus_value)
            if not 2 <= modulus <= 10**12:
                raise ValueError("modulus is outside the supported range")
            arguments["modulus"] = modulus
        if output == "residue" and "modulus" not in arguments:
            raise ValueError("residue output requires modulus")
    elif operation == "divisor_power_threshold":
        threshold = int(arguments["threshold"])
        max_n = int(arguments.get("max_n", 10_000))
        if not 1 <= threshold <= 10**12:
            raise ValueError("divisor threshold is outside the supported range")
        if not 1 <= max_n <= 100_000:
            raise ValueError("max_n is outside the supported range")
        arguments = {"threshold": threshold, "max_n": max_n}
    elif operation == "bitmask_dynamic_program":
        values_value = arguments.get("values")
        if (
            not isinstance(values_value, list)
            or not 1 <= len(values_value) <= 100_000
            or any(
                not isinstance(item, int) or isinstance(item, bool)
                for item in values_value
            )
        ):
            raise ValueError("values must be a nonempty bounded integer list")
        values = list(values_value)
        variable_count = int(arguments["variable_count"])
        power = int(arguments.get("power", 1))
        modulus = int(arguments["modulus"])
        target = int(arguments.get("target", 0))
        output_modulus_value = arguments.get("output_modulus")
        output_modulus = (
            None if output_modulus_value is None else int(output_modulus_value)
        )
        if not 1 <= variable_count <= 64:
            raise ValueError("variable_count must be 1 through 64")
        if not 0 <= power <= 64:
            raise ValueError("power must be 0 through 64")
        if not 2 <= modulus <= 100_000:
            raise ValueError("modulus must be 2 through 100,000")
        if variable_count * modulus * min(len(values), modulus) > 50_000_000:
            raise ValueError("residue dynamic-programming work budget is exceeded")
        if output_modulus is not None and not 2 <= output_modulus <= 10**12:
            raise ValueError("output_modulus is outside the supported range")
        if any(abs(item) > 10**12 for item in values):
            raise ValueError("value is outside the supported range")
        arguments = {
            "variable_count": variable_count,
            "values": values,
            "power": power,
            "modulus": modulus,
            "target": target,
        }
        if output_modulus is not None:
            arguments["output_modulus"] = output_modulus
    elif operation == "exact_cover_count":
        universe_size = int(arguments["universe_size"])
        selection_count = int(arguments["selection_count"])
        objects_value = arguments.get("objects")
        if not 1 <= universe_size <= 128:
            raise ValueError("universe_size must be 1 through 128")
        if (
            not isinstance(objects_value, list)
            or not 1 <= len(objects_value) <= 256
        ):
            raise ValueError("objects must contain 1 through 256 finite objects")
        objects: list[list[int]] = []
        seen: set[tuple[int, ...]] = set()
        for object_value in objects_value:
            if (
                not isinstance(object_value, list)
                or not object_value
                or any(
                    not isinstance(item, int) or isinstance(item, bool)
                    for item in object_value
                )
            ):
                raise ValueError("each exact-cover object must be a nonempty index list")
            normalized_object = tuple(sorted(set(object_value)))
            if len(normalized_object) != len(object_value):
                raise ValueError("exact-cover objects must not repeat an element")
            if normalized_object[0] < 0 or normalized_object[-1] >= universe_size:
                raise ValueError("exact-cover object index is outside the universe")
            if normalized_object in seen:
                raise ValueError("exact-cover objects must be unique")
            seen.add(normalized_object)
            objects.append(list(normalized_object))
        if not 1 <= selection_count <= len(objects):
            raise ValueError("selection_count is outside the object range")
        if math.comb(len(objects), selection_count) > 1_000_000:
            raise ValueError("independent exact-cover validation budget is exceeded")
        arguments = {
            "universe_size": universe_size,
            "objects": objects,
            "selection_count": selection_count,
        }
    elif operation == "exact_branch_system":
        task = validate_symbol_name(arguments.get("task"))
        symbols = _symbols(arguments)
        if not 1 <= len(symbols) <= 8:
            raise ValueError(
                "exact branch system requires one through eight symbols"
            )
        allowed = frozenset(symbols)
        original_equations_value = arguments.get("original_equations")
        common_conditions_value = arguments.get("common_conditions", [])
        branches_value = arguments.get("branches")
        solve_for_value = arguments.get("solve_for")
        partition_value = arguments.get("partition")
        if (
            not isinstance(original_equations_value, list)
            or not 1 <= len(original_equations_value) <= 16
            or not isinstance(common_conditions_value, list)
            or len(common_conditions_value) > 16
            or not isinstance(branches_value, list)
            or not 1 <= len(branches_value) <= 8
            or not isinstance(solve_for_value, list)
            or not solve_for_value
            or not isinstance(partition_value, Mapping)
        ):
            raise ValueError(
                "exact branch system requires bounded equations, "
                "conditions, branches, partition, and solve_for"
            )
        solve_for = [
            validate_symbol_name(value) for value in solve_for_value
        ]
        if (
            len(set(solve_for)) != len(solve_for)
            or set(solve_for) != set(symbols)
        ):
            raise ValueError(
                "exact branch solve_for must contain every symbol once"
            )
        partition_kind = str(partition_value.get("kind") or "")
        if partition_kind == "exhaustive_solutions":
            if len(branches_value) != 1:
                raise ValueError(
                    "exhaustive solution partition requires exactly one branch"
                )
            partition = {"kind": partition_kind}
        elif partition_kind == "sign":
            if (
                len(branches_value) != 2
                or str(partition_value.get("zero_policy"))
                != "prove_empty"
            ):
                raise ValueError(
                    "sign partition requires two branches and prove_empty "
                    "zero policy"
                )
            partition = {
                "kind": partition_kind,
                "expression": validate_expression(
                    partition_value.get("expression"),
                    allowed_symbols=allowed,
                ),
                "zero_policy": "prove_empty",
            }
        else:
            raise ValueError("exact branch partition kind is unsupported")

        branches: list[dict[str, Any]] = []
        branch_ids: set[str] = set()
        partition_relations: set[str] = set()
        for branch_value in branches_value:
            if not isinstance(branch_value, Mapping):
                raise ValueError("exact branch must be an object")
            branch_id = str(branch_value.get("branch_id") or "")
            equations_value = branch_value.get("equations", [])
            conditions_value = branch_value.get("conditions", [])
            if (
                not branch_id
                or branch_id in branch_ids
                or not isinstance(equations_value, list)
                or len(equations_value) > 16
                or not isinstance(conditions_value, list)
                or len(conditions_value) > 16
            ):
                raise ValueError("exact branch schema is invalid")
            branch_ids.add(branch_id)
            if partition_kind == "exhaustive_solutions":
                if equations_value:
                    raise ValueError(
                        "exhaustive branch cannot add equations that exclude "
                        "original solutions"
                    )
                partition_relation = None
            else:
                partition_relation = str(
                    branch_value.get("partition_relation") or ""
                )
                if (
                    partition_relation not in {"positive", "negative"}
                    or not equations_value
                ):
                    raise ValueError(
                        "sign branch requires a relation and equations"
                    )
                partition_relations.add(partition_relation)
            normalized_branch = {
                "branch_id": branch_id,
                "equations": [
                    validate_expression(value, allowed_symbols=allowed)
                    for value in equations_value
                ],
                "conditions": [
                    _sign_condition(value, allowed_symbols=allowed)
                    for value in conditions_value
                ],
            }
            if partition_relation is not None:
                normalized_branch["partition_relation"] = (
                    partition_relation
                )
            branches.append(normalized_branch)
        if (
            partition_kind == "sign"
            and partition_relations != {"positive", "negative"}
        ):
            raise ValueError(
                "sign partition must cover positive and negative branches"
            )
        if str(arguments.get("aggregate")) != "union":
            raise ValueError("exact branch aggregation must be union")
        arguments = {
            "task": task,
            "symbols": symbols,
            "original_equations": [
                validate_expression(value, allowed_symbols=allowed)
                for value in original_equations_value
            ],
            "common_conditions": [
                _sign_condition(value, allowed_symbols=allowed)
                for value in common_conditions_value
            ],
            "partition": partition,
            "branches": branches,
            "solve_for": solve_for,
            "output_expression": validate_expression(
                arguments.get("output_expression"),
                allowed_symbols=allowed,
            ),
            "aggregate": "union",
        }
    elif operation == "piecewise_branch_system":
        task = str(arguments.get("task") or "")
        if task != "rotated_parallelogram_complete":
            raise ValueError(
                "unsupported piecewise branch semantic task"
            )
        symbols = _symbols(arguments)
        allowed = frozenset(symbols)
        original_equations_value = arguments.get("original_equations")
        common_conditions_value = arguments.get("common_conditions", [])
        branches_value = arguments.get("branches")
        solve_for_value = arguments.get("solve_for")
        if (
            not isinstance(original_equations_value, list)
            or not 1 <= len(original_equations_value) <= 16
            or not isinstance(common_conditions_value, list)
            or len(common_conditions_value) > 16
            or not isinstance(branches_value, list)
            or len(branches_value) != 2
            or not isinstance(solve_for_value, list)
            or not solve_for_value
        ):
            raise ValueError(
                "piecewise branch system requires bounded equations, "
                "conditions, two branches, and solve_for"
            )
        solve_for = [
            validate_symbol_name(value) for value in solve_for_value
        ]
        if (
            len(set(solve_for)) != len(solve_for)
            or set(solve_for) != set(symbols)
        ):
            raise ValueError(
                "piecewise branch solve_for must contain every symbol once"
            )
        branches: list[dict[str, Any]] = []
        branch_ids: set[str] = set()
        split_relations: set[str] = set()
        for branch_value in branches_value:
            if not isinstance(branch_value, Mapping):
                raise ValueError("piecewise branch must be an object")
            branch_id = str(branch_value.get("branch_id") or "")
            split_relation = str(branch_value.get("split_relation") or "")
            equations_value = branch_value.get("equations")
            conditions_value = branch_value.get("conditions", [])
            if (
                not branch_id
                or branch_id in branch_ids
                or split_relation not in {"positive", "negative"}
                or not isinstance(equations_value, list)
                or not 1 <= len(equations_value) <= 16
                or not isinstance(conditions_value, list)
                or len(conditions_value) > 16
            ):
                raise ValueError("piecewise branch schema is invalid")
            branch_ids.add(branch_id)
            split_relations.add(split_relation)
            branches.append(
                {
                    "branch_id": branch_id,
                    "split_relation": split_relation,
                    "equations": [
                        validate_expression(value, allowed_symbols=allowed)
                        for value in equations_value
                    ],
                    "conditions": [
                        _sign_condition(value, allowed_symbols=allowed)
                        for value in conditions_value
                    ],
                }
            )
        if split_relations != {"positive", "negative"}:
            raise ValueError(
                "piecewise branches must cover positive and negative signs"
            )
        if str(arguments.get("aggregate")) != "union":
            raise ValueError("piecewise branch aggregation must be union")
        arguments = {
            "task": task,
            "symbols": symbols,
            "original_equations": [
                validate_expression(value, allowed_symbols=allowed)
                for value in original_equations_value
            ],
            "common_conditions": [
                _sign_condition(value, allowed_symbols=allowed)
                for value in common_conditions_value
            ],
            "split_expression": validate_expression(
                arguments.get("split_expression"),
                allowed_symbols=allowed,
            ),
            "branches": branches,
            "solve_for": solve_for,
            "output_expression": validate_expression(
                arguments.get("output_expression"),
                allowed_symbols=allowed,
            ),
            "aggregate": "union",
        }
    elif operation == "exact_equation_system":
        task = str(arguments.get("task"))
        if task == "base10_log_bilinear":
            arguments = {
                "task": task,
                "a": int(arguments["a"]),
                "b": int(arguments["b"]),
                "c": int(arguments["c"]),
            }
        elif task == "base2_log_trig_angles":
            arguments = {
                "task": task,
                "product_power_num": int(arguments["product_power_num"]),
                "product_power_den": int(arguments["product_power_den"]),
                "ratio_power_num": int(arguments["ratio_power_num"]),
                "ratio_power_den": int(arguments["ratio_power_den"]),
            }
            if (
                arguments["product_power_den"] == 0
                or arguments["ratio_power_den"] == 0
            ):
                raise ValueError("logarithmic powers require nonzero denominators")
        elif task == "single_base_exponential_rational":
            arguments = {
                "task": task,
                "base": int(arguments["base"]),
                "shift": int(arguments["shift"]),
                "reciprocal_numerator": int(arguments["reciprocal_numerator"]),
                "target_power": int(arguments["target_power"]),
            }
        elif task == "radical_log_pair":
            arguments = {
                "task": task,
                "root_sum": int(arguments["root_sum"]),
                "root_product": int(arguments["root_product"]),
            }
        elif task == "base10_log_power_linear":
            matrix = arguments.get("coefficient_matrix")
            rhs = arguments.get("rhs")
            if (
                not isinstance(matrix, list)
                or len(matrix) != 2
                or any(not isinstance(row, list) or len(row) != 2 for row in matrix)
                or not isinstance(rhs, list)
                or len(rhs) != 2
            ):
                raise ValueError("log-power system requires a 2x2 matrix and RHS")
            arguments = {
                "task": task,
                "coefficient_matrix": [
                    [int(value) for value in row] for row in matrix
                ],
                "rhs": [int(value) for value in rhs],
            }
        elif task == "mixed_base_exponential_quadratic":
            arguments = {
                "task": task,
                "left_base": int(arguments["left_base"]),
                "right_base": int(arguments["right_base"]),
                "left_shift": int(arguments["left_shift"]),
                "right_shift": int(arguments["right_shift"]),
            }
        elif task == "monotone_base10_log_cycle":
            offsets = arguments.get("offsets")
            if not isinstance(offsets, list) or len(offsets) != 3:
                raise ValueError("monotone log cycle requires three offsets")
            arguments = {"task": task, "offsets": [int(value) for value in offsets]}
        elif task == "polynomial_real_pair":
            arguments = {"task": task}
        else:
            raise ValueError(f"unsupported exact equation task: {task}")
    elif operation == "exact_number_theory":
        task = str(arguments.get("task"))
        if task == "cromulent_extrema":
            length = int(arguments["length"])
            if not 2 <= length <= 12:
                raise ValueError("cromulent length must be 2 through 12")
            arguments = {"task": task, "length": length}
        elif task == "double_factorial_divisors":
            target_n = int(arguments["target_n"])
            if not 1 <= target_n <= 100_000:
                raise ValueError("double-factorial target is outside the bound")
            arguments = {"task": task, "target_n": target_n}
        elif task == "lcm_divisor_filter":
            upper = int(arguments["upper"])
            exactly = int(arguments["divisible_by_exactly"])
            if not 2 <= upper <= 60 or not 0 <= exactly <= upper:
                raise ValueError("LCM divisor-filter arguments are outside the bound")
            arguments = {
                "task": task,
                "upper": upper,
                "divisible_by_exactly": exactly,
            }
        elif task == "modular_square_sum":
            arguments = {
                "task": task,
                "scale": int(arguments["scale"]),
                "upper": int(arguments["upper"]),
                "modulus": int(arguments["modulus"]),
            }
        elif task == "largest_distinct_digit_multiple":
            digits = int(arguments["digits"])
            modulus = int(arguments["modulus"])
            if not 1 <= digits <= 10 or not 2 <= modulus <= 10**6:
                raise ValueError("distinct-digit search arguments are outside the bound")
            arguments = {"task": task, "digits": digits, "modulus": modulus}
        elif task == "erased_digit_product":
            erased = arguments.get("erased_digits")
            if (
                not isinstance(erased, list)
                or not erased
                or any(not isinstance(value, int) or not 0 <= value <= 9 for value in erased)
            ):
                raise ValueError("erased digits must be a nonempty digit list")
            arguments = {
                "task": task,
                "upper": int(arguments["upper"]),
                "erased_digits": list(dict.fromkeys(erased)),
                "modulus": int(arguments["modulus"]),
            }
        else:
            raise ValueError(f"unsupported exact number-theory task: {task}")
        if "modulus" in arguments and not 2 <= int(arguments["modulus"]) <= 10**12:
            raise ValueError("modulus is outside the supported range")
    elif operation == "exact_finite_state":
        task = str(arguments.get("task"))
        if task == "greatest_digit_recurrence":
            arguments = {"task": task}
        elif task == "least_non_palindrome_sum":
            lower = int(arguments["lower"])
            if not 1 <= lower <= 1_000_000:
                raise ValueError("palindrome lower bound is outside the supported range")
            arguments = {"task": task, "lower": lower}
        elif task == "palindrome_contains_pattern":
            pattern = arguments.get("pattern")
            length = int(arguments["length"])
            alphabet_size = int(arguments["alphabet_size"])
            if (
                not isinstance(pattern, list)
                or not pattern
                or len(pattern) > length
                or not 2 <= alphabet_size <= 64
                or not 1 <= length <= 63
                or any(
                    not isinstance(value, int)
                    or not 0 <= value < alphabet_size
                    for value in pattern
                )
            ):
                raise ValueError("palindrome-pattern arguments are invalid")
            arguments = {
                "task": task,
                "alphabet_size": alphabet_size,
                "length": length,
                "pattern": pattern,
            }
        elif task == "permutation_signature":
            label = str(arguments["label"])
            window = int(arguments["window"])
            if (
                len(label) > 9
                or set(label) != {str(value) for value in range(1, len(label) + 1)}
                or not 2 <= window <= len(label)
            ):
                raise ValueError("permutation-signature arguments are invalid")
            arguments = {"task": task, "label": label, "window": window}
        elif task == "distinct_digit_sum_images":
            upper = int(arguments["upper"])
            if not 1 <= upper <= 1_000_000:
                raise ValueError("digit-sum image bound is outside the supported range")
            arguments = {"task": task, "upper": upper}
        elif task == "minimal_positive_recurrence":
            length = int(arguments["length"])
            if not 1 <= length <= 100_000:
                raise ValueError("recurrence length is outside the supported range")
            arguments = {"task": task, "length": length}
        else:
            raise ValueError(f"unsupported exact finite-state task: {task}")
    elif operation == "newclid_geometry_proof":
        from newclid.jgex.constructions import ALL_JGEX_CONSTRUCTIONS
        from newclid.predicates._index import PredicateType

        task = str(arguments.get("task") or "")
        if task != "prove_predicate":
            raise ValueError("unsupported Newclid geometry task")
        construction_names = {
            str(
                definition.name.value
                if hasattr(definition.name, "value")
                else definition.name
            )
            for definition in ALL_JGEX_CONSTRUCTIONS
            if not str(
                definition.name.value
                if hasattr(definition.name, "value")
                else definition.name
            ).startswith("test_")
        }
        predicate_names = {item.value for item in PredicateType}
        constructions_value = arguments.get("constructions")
        goals_value = arguments.get("goals")
        source_quotes_value = arguments.get("source_quotes", [])
        if (
            not isinstance(constructions_value, list)
            or not 1 <= len(constructions_value) <= 64
            or not isinstance(goals_value, list)
            or not 1 <= len(goals_value) <= 8
            or not isinstance(source_quotes_value, list)
            or len(source_quotes_value) > 32
            or not all(
                isinstance(value, str) and 0 < len(value) <= 2_000
                for value in source_quotes_value
            )
        ):
            raise ValueError(
                "Newclid requires bounded constructions, goals, and "
                "source quotes"
            )
        constructions: list[dict[str, Any]] = []
        known_points: set[str] = set()
        for index, construction_value in enumerate(constructions_value):
            if not isinstance(construction_value, Mapping):
                raise ValueError("Newclid construction must be an object")
            outputs_value = construction_value.get("outputs")
            arguments_list_value = construction_value.get("arguments")
            construction = str(
                construction_value.get("construction") or ""
            )
            if (
                construction not in construction_names
                or not isinstance(outputs_value, list)
                or not 1 <= len(outputs_value) <= 8
                or not isinstance(arguments_list_value, list)
                or not 1 <= len(arguments_list_value) <= 16
            ):
                raise ValueError(
                    f"Newclid construction {index} has an invalid shape"
                )
            outputs = [
                _newclid_token(value, label="Newclid output point")
                for value in outputs_value
            ]
            if (
                any(_NEWCLID_POINT_RE.fullmatch(value) is None for value in outputs)
                or len(set(outputs)) != len(outputs)
                or known_points.intersection(outputs)
            ):
                raise ValueError(
                    "Newclid output points must be new, unique identifiers"
                )
            tokens = [
                _newclid_token(value, label="Newclid construction argument")
                for value in arguments_list_value
            ]
            available_points = known_points.union(outputs)
            if any(
                _NEWCLID_POINT_RE.fullmatch(value)
                and value not in available_points
                for value in tokens
            ):
                raise ValueError(
                    "Newclid construction references an unknown point"
                )
            known_points.update(outputs)
            constructions.append(
                {
                    "outputs": outputs,
                    "construction": construction,
                    "arguments": tokens,
                }
            )
        goals: list[dict[str, Any]] = []
        for goal_value in goals_value:
            if not isinstance(goal_value, Mapping):
                raise ValueError("Newclid goal must be an object")
            predicate = str(goal_value.get("predicate") or "")
            goal_arguments_value = goal_value.get("arguments")
            if (
                predicate not in predicate_names
                or not isinstance(goal_arguments_value, list)
                or not 1 <= len(goal_arguments_value) <= 24
            ):
                raise ValueError("Newclid goal has an invalid shape")
            tokens = [
                _newclid_token(value, label="Newclid goal argument")
                for value in goal_arguments_value
            ]
            if any(
                _NEWCLID_POINT_RE.fullmatch(value)
                and value not in known_points
                for value in tokens
            ):
                raise ValueError("Newclid goal references an unknown point")
            goals.append({"predicate": predicate, "arguments": tokens})
        seed = int(arguments.get("seed", 0))
        if not 0 <= seed <= 2**31 - 1:
            raise ValueError("Newclid seed is outside the supported range")
        arguments = {
            "task": task,
            "constructions": constructions,
            "goals": goals,
            "source_quotes": list(source_quotes_value),
            "seed": seed,
        }
    elif operation == "exact_coordinate_geometry":
        task = str(arguments.get("task"))
        schemas = {
            "parabola_square_trapezoid": (
                "side",
                "root_left",
                "root_right",
                "target_area",
            ),
            "isosceles_coordinate_parameter": (),
            "overlapping_regular_hexagons": (
                "side",
                "fraction_num",
                "fraction_den",
            ),
            "hemisphere_five_marbles": ("radius",),
            "rotated_parallelogram_area": (),
            "regular_polygon_vector": ("sides", "target_vertex"),
            "square_incenter_distance": ("diagonal",),
            "intersecting_circles_area": ("ba", "bo", "bc"),
        }
        if task not in schemas:
            raise ValueError(f"unsupported exact coordinate-geometry task: {task}")
        arguments = {
            "task": task,
            **{field: int(arguments[field]) for field in schemas[task]},
        }
        if any(
            field.endswith("_den") and arguments[field] == 0
            for field in schemas[task]
        ):
            raise ValueError("geometry ratio denominator must be nonzero")
    else:
        raise ValueError(f"no argument schema for operation: {operation}")
    if claimed is not None:
        arguments["claimed_answer"] = claimed
    return arguments
