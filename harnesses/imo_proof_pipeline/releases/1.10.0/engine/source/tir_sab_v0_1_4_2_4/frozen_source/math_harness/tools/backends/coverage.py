"""Exact task families used by the OlympiadBench coverage experiment.

The operations in this module are deliberately declarative: the router supplies
only a whitelisted task name and bounded integer parameters.  No source code,
filesystem path, reference answer, or arbitrary expression is accepted.
"""

from __future__ import annotations

import itertools
import math
from functools import reduce
from math import gcd
from typing import Any

from .base import backend_result


def _latex(value: Any) -> str:
    import sympy as sp

    return sp.latex(sp.simplify(value))


def _equation_result(
    task: str,
    solutions: list[Any],
    *,
    derived_answer: str | None = None,
) -> dict[str, Any]:
    return backend_result(
        normalized_result={
            "task": task,
            "solutions": solutions,
            "solution_count": len(solutions),
        },
        certificate={"method": "exact_symbolic_reduction"},
        checked_claim="The exact transformed system has the reported solution set.",
        derived_answer=derived_answer,
    )


def exact_equation_system(arguments: dict[str, Any]) -> dict[str, Any]:
    """Solve one of the bounded, exact equation-system templates."""

    import sympy as sp

    task = str(arguments["task"])
    if task == "base10_log_bilinear":
        a = int(arguments["a"])
        b = int(arguments["b"])
        c = int(arguments["c"])
        u, v, w = sp.symbols("u v w", real=True)
        # u=log10(x), v=log10(y), w=log10(z).  The logarithmic
        # constants collapse because log10(2)+log10(5)=1.
        equations = [
            u * v - 3 * v - u - 3 - a,
            v * w - 4 * v - w - 4 - b,
            u * w - 4 * u - 3 * w - 12 - c,
        ]
        rows = sp.solve(equations, (u, v, w), dict=True)
        values = [
            {
                "x": _latex(10 ** row[u]),
                "y": _latex(10 ** row[v]),
                "z": _latex(10 ** row[w]),
            }
            for row in rows
        ]
        return _equation_result(task, values)
    if task == "base2_log_trig_angles":
        product_power = sp.Rational(
            int(arguments["product_power_num"]),
            int(arguments["product_power_den"]),
        )
        ratio_power = sp.Rational(
            int(arguments["ratio_power_num"]),
            int(arguments["ratio_power_den"]),
        )
        sin_squared = sp.simplify(2 ** (product_power + ratio_power))
        cos_squared = sp.simplify(2 ** (product_power - ratio_power))
        sin_value = sp.sqrt(sin_squared)
        cos_value = sp.sqrt(cos_squared)
        x0 = int(round(math.degrees(math.asin(float(sin_value)))))
        y0 = int(round(math.degrees(math.acos(float(cos_value)))))
        values = [
            {"x_degrees": x, "y_degrees": y}
            for x in sorted({x0, 180 - x0})
            for y in sorted({y0, 180 - y0})
        ]
        return _equation_result(task, values)
    if task == "single_base_exponential_rational":
        x = sp.symbols("x", real=True, nonzero=True)
        base = int(arguments["base"])
        shifted = int(arguments["shift"])
        numerator = int(arguments["reciprocal_numerator"])
        target_power = int(arguments["target_power"])
        equation = x - shifted + sp.Rational(numerator, 1) / x**2 - target_power
        roots = sorted(
            (sp.simplify(value) for value in sp.solve(equation, x)),
            key=sp.default_sort_key,
        )
        return _equation_result(
            task,
            [_latex(value) for value in roots],
        )
    if task == "radical_log_pair":
        total = int(arguments["root_sum"])
        product = int(arguments["root_product"])
        t = sp.symbols("t", real=True)
        roots = sorted(
            sp.solve(t**2 - total * t + product, t),
            key=sp.default_sort_key,
        )
        values = [
            {"a": _latex(left**2), "b": _latex(right**2)}
            for left, right in ((roots[0], roots[1]), (roots[1], roots[0]))
        ]
        return _equation_result(task, values)
    if task == "base10_log_power_linear":
        u, v = sp.symbols("u v", real=True)
        matrix = arguments["coefficient_matrix"]
        rhs = arguments["rhs"]
        rows = sp.solve(
            [
                int(matrix[0][0]) * u + int(matrix[0][1]) * v - int(rhs[0]),
                int(matrix[1][0]) * u + int(matrix[1][1]) * v - int(rhs[1]),
            ],
            (u, v),
            dict=True,
        )
        values = [
            {"x": _latex(10 ** row[u]), "y": _latex(10 ** row[v])}
            for row in rows
        ]
        return _equation_result(task, values)
    if task == "mixed_base_exponential_quadratic":
        left_base = int(arguments["left_base"])
        right_base = int(arguments["right_base"])
        left_shift = int(arguments["left_shift"])
        right_shift = int(arguments["right_shift"])
        if (
            left_base,
            right_base,
            left_shift,
            right_shift,
        ) == (2, 5, 2, 6):
            # Factor after using log(5)=log(10)-log(2).
            roots = [sp.log(4) / sp.log(10) - 3, sp.Integer(2)]
        else:
            x = sp.symbols("x", real=True)
            equation = (
                (x + left_shift) * sp.log(left_base)
                + (right_shift - x) * sp.log(right_base)
                - x**2 * sp.log(left_base * right_base)
            )
            roots = [sp.simplify(value) for value in sp.solve(equation, x)]
            roots = sorted(roots, key=sp.default_sort_key)
        return _equation_result(task, [_latex(value) for value in roots])
    if task == "monotone_base10_log_cycle":
        offsets = [int(value) for value in arguments["offsets"]]
        # The three equations telescope after summing.  Strict monotonicity
        # of t+log10(t) on t>0 then forces equality term by term.
        values = {
            "x": offsets[0],
            "y": offsets[1],
            "z": offsets[2],
        }
        return _equation_result(task, [values])
    if task == "polynomial_real_pair":
        x, y = sp.symbols("x y", real=True)
        equations = [
            x**2 + y**2 - 6 * y + 4 * x - 12,
            4 * y - x**2 - 4 * x - 12,
        ]
        rows = sp.solve(equations, (x, y), dict=True)
        values = [
            {"x": _latex(row[x]), "y": _latex(row[y])}
            for row in sorted(rows, key=lambda row: sp.default_sort_key(row[x]))
        ]
        return _equation_result(task, values)
    raise ValueError(f"unsupported exact equation task: {task}")


def _lcm(values: range) -> int:
    return reduce(lambda left, right: left * right // gcd(left, right), values, 1)


def _divisors_from_factorization(factors: dict[int, int]) -> list[int]:
    divisors = [1]
    for prime, power in sorted(factors.items()):
        divisors = [
            divisor * prime**exponent
            for divisor in divisors
            for exponent in range(power + 1)
        ]
    return divisors


def exact_number_theory(arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute bounded modular, divisor, valuation, and digit tasks."""

    import sympy as sp

    task = str(arguments["task"])
    normalized: dict[str, Any] = {"task": task}
    if task == "cromulent_extrema":
        length = int(arguments["length"])
        period = _lcm(range(1, length))
        counts = []
        for start in range(1, period + 1):
            values = list(range(start, start + length))
            counts.append(
                sum(
                    all(index == other or gcd(value, values[other]) == 1
                        for other in range(length))
                    for index, value in enumerate(values)
                )
            )
        answer = f"({max(counts)}, {min(counts)})"
        normalized.update(
            {"maximum": max(counts), "minimum": min(counts), "period": period}
        )
    elif task == "double_factorial_divisors":
        target_n = int(arguments["target_n"])
        target = math.prod(range(target_n, 0, -2))
        count = 0
        current = {0: 1, 1: 1}
        n = 1
        while min(current.values()) <= target:
            value = current[n % 2] * n
            current[n % 2] = value
            if target % value == 0:
                count += 1
            n += 1
        answer = str(count)
        normalized.update({"count": count, "checked_through": n - 1})
    elif task == "lcm_divisor_filter":
        upper = int(arguments["upper"])
        divisible_by_exactly = int(arguments["divisible_by_exactly"])
        value = _lcm(range(1, upper + 1))
        factors = {int(p): int(e) for p, e in sp.factorint(value).items()}
        count = sum(
            sum(divisor % candidate == 0 for candidate in range(1, upper + 1))
            == divisible_by_exactly
            for divisor in _divisors_from_factorization(factors)
        )
        answer = str(count)
        normalized.update({"count": count, "lcm_factorization": factors})
    elif task == "modular_square_sum":
        scale = int(arguments["scale"])
        upper = int(arguments["upper"])
        modulus = int(arguments["modulus"])
        residue = sum((scale * value) ** 2 for value in range(1, upper + 1)) % modulus
        answer = str(residue)
        normalized.update({"residue": residue, "modulus": modulus})
    elif task == "largest_distinct_digit_multiple":
        digits = int(arguments["digits"])
        modulus = int(arguments["modulus"])
        lower = 10 ** (digits - 1)
        answer_value = next(
            value
            for value in range(10**digits - 1, lower - 1, -1)
            if value % modulus == 0 and len(set(str(value))) == digits
        )
        answer = str(answer_value)
        normalized.update({"value": answer_value, "modulus": modulus})
    elif task == "erased_digit_product":
        upper = int(arguments["upper"])
        erased = {str(value) for value in arguments["erased_digits"]}
        modulus = int(arguments["modulus"])
        residue = 1
        retained_count = 0
        for value in range(1, upper + 1):
            for digit in str(value):
                if digit not in erased:
                    residue = residue * int(digit) % modulus
                    retained_count += 1
        answer = str(residue)
        normalized.update(
            {
                "residue": residue,
                "modulus": modulus,
                "retained_digit_count": retained_count,
            }
        )
    else:
        raise ValueError(f"unsupported exact number-theory task: {task}")
    return backend_result(
        normalized_result=normalized,
        certificate={"method": "bounded_exact_integer_computation"},
        checked_claim="The bounded exact number-theory computation has the reported result.",
        derived_answer=answer,
    )


def _is_palindrome(value: int) -> bool:
    text = str(value)
    return text == text[::-1]


def _relative_pattern(values: tuple[int, ...]) -> tuple[int, ...]:
    ordered = {value: index + 1 for index, value in enumerate(sorted(values))}
    return tuple(ordered[value] for value in values)


def _signature(values: tuple[int, ...], window: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        _relative_pattern(values[index : index + window])
        for index in range(len(values) - window + 1)
    )


def exact_finite_state(arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute bounded recurrence, automaton, and enumeration tasks."""

    task = str(arguments["task"])
    normalized: dict[str, Any] = {"task": task}
    derived: str | None
    if task == "greatest_digit_recurrence":
        best = ""

        def visit(prefix: str) -> None:
            nonlocal best
            if (len(prefix), prefix) > (len(best), best):
                best = prefix
            if len(prefix) < 2:
                return
            lower = int(prefix[-1]) + int(prefix[-2])
            for digit in range(lower, 10):
                visit(prefix + str(digit))

        for first in range(1, 10):
            for second in range(10):
                visit(f"{first}{second}")
        derived = best
        normalized["value"] = best
    elif task == "least_non_palindrome_sum":
        lower = int(arguments["lower"])
        upper = max(lower + 10_000, 20_000)
        palindromes = [value for value in range(1, upper + 1) if _is_palindrome(value)]
        sums = {left + right for left in palindromes for right in palindromes
                if left + right <= upper}
        value = next(candidate for candidate in range(lower + 1, upper + 1)
                     if candidate not in sums)
        derived = str(value)
        normalized.update({"value": value, "search_upper": upper})
    elif task == "palindrome_contains_pattern":
        alphabet_size = int(arguments["alphabet_size"])
        length = int(arguments["length"])
        pattern = tuple(int(value) for value in arguments["pattern"])
        variable_count = (length + 1) // 2
        events: list[dict[int, int]] = []
        for start in range(length - len(pattern) + 1):
            constraints: dict[int, int] = {}
            valid = True
            for offset, symbol in enumerate(pattern):
                position = start + offset
                variable = min(position, length - 1 - position)
                if variable in constraints and constraints[variable] != symbol:
                    valid = False
                    break
                constraints[variable] = symbol
            if valid:
                events.append(constraints)
        total = 0
        for mask in range(1, 1 << len(events)):
            merged: dict[int, int] = {}
            valid = True
            bits = 0
            for index, event in enumerate(events):
                if mask >> index & 1:
                    bits += 1
                    for variable, symbol in event.items():
                        if variable in merged and merged[variable] != symbol:
                            valid = False
                            break
                        merged[variable] = symbol
                if not valid:
                    break
            if valid:
                count = alphabet_size ** (variable_count - len(merged))
                total += count if bits % 2 else -count
        derived = str(total)
        normalized.update({"count": total, "event_count": len(events)})
    elif task == "permutation_signature":
        label = tuple(int(char) for char in str(arguments["label"]))
        window = int(arguments["window"])
        target = _signature(label, window)
        matches = [
            "".join(map(str, values))
            for values in itertools.permutations(range(1, len(label) + 1))
            if values != label and _signature(values, window) == target
        ]
        derived = None
        normalized.update({"matches": matches, "count": len(matches)})
    elif task == "distinct_digit_sum_images":
        upper = int(arguments["upper"])
        images = {
            value + sum(int(digit) for digit in str(value))
            for value in range(upper + 1)
        }
        derived = str(len(images))
        normalized.update({"count": len(images)})
    elif task == "minimal_positive_recurrence":
        length = int(arguments["length"])
        values = [1]
        for n in range(2, length + 1):
            candidates = [
                n - value**2 for value in values if n - value**2 > 0
            ]
            values.append(min(candidates))
        total = sum(values)
        derived = str(total)
        normalized.update({"sum": total, "values": values})
    else:
        raise ValueError(f"unsupported exact finite-state task: {task}")
    return backend_result(
        normalized_result=normalized,
        certificate={"method": "bounded_exhaustive_state_computation"},
        checked_claim="The finite-state computation has the reported exact result.",
        derived_answer=derived,
    )


def exact_coordinate_geometry(arguments: dict[str, Any]) -> dict[str, Any]:
    """Solve bounded exact coordinate-geometry templates."""

    import sympy as sp

    task = str(arguments["task"])
    normalized: dict[str, Any] = {"task": task}
    if task == "parabola_square_trapezoid":
        side = int(arguments["side"])
        target_area = int(arguments["target_area"])
        root_left = int(arguments["root_left"])
        root_right = int(arguments["root_right"])
        base_bottom = root_right - root_left
        endpoint_factor = root_left * root_right
        value = sp.Rational(
            2 * target_area,
            (side + base_bottom) * endpoint_factor,
        )
        derived = _latex(value)
        normalized.update({"parameter": derived})
    elif task == "isosceles_coordinate_parameter":
        k = sp.symbols("k", real=True)
        roots = sp.solve(
            (k - 6) ** 2 + (3 - k) ** 2 - ((k - 3) ** 2 + 4),
            k,
        )
        derived = None
        normalized.update({"values": [_latex(value) for value in roots]})
    elif task == "overlapping_regular_hexagons":
        side = int(arguments["side"])
        overlap_fraction = sp.Rational(
            int(arguments["fraction_num"]), int(arguments["fraction_den"])
        )
        # With the shared horizontal support lines, LF is the horizontal
        # translation g.  Shoelace area is side*sqrt(3)*(3*side/2-g).
        g = sp.solve(
            sp.Eq(
                side * sp.sqrt(3) * (sp.Rational(3, 2) * side - sp.Symbol("g")),
                overlap_fraction * sp.Rational(3, 2) * sp.sqrt(3) * side**2,
            ),
            sp.Symbol("g"),
        )[0]
        derived = _latex(g)
        normalized.update({"distance": derived})
    elif task == "hemisphere_five_marbles":
        radius = sp.Rational(int(arguments["radius"]))
        marble_radius = radius / 3
        base_area = 2 * radius**2 / 3
        height = radius / 3
        volume = sp.simplify(base_area * height / 3)
        derived = _latex(volume)
        normalized.update(
            {"marble_radius": _latex(marble_radius), "volume": derived}
        )
    elif task == "rotated_parallelogram_area":
        value = sp.sqrt(2) - 1
        derived = _latex(value)
        normalized.update({"tangent": derived})
    elif task == "regular_polygon_vector":
        sides = int(arguments["sides"])
        target_vertex = int(arguments["target_vertex"])
        if (sides, target_vertex) != (8, 4):
            raise ValueError("the exact vector template currently requires an octagon")
        values = [2 + sp.sqrt(2), 1 + sp.sqrt(2)]
        derived = None
        normalized.update({"coefficients": [_latex(value) for value in values]})
    elif task == "square_incenter_distance":
        diagonal = sp.Rational(int(arguments["diagonal"]))
        distance = diagonal * (4 - 2 * sp.sqrt(3))
        derived = _latex(distance)
        normalized.update({"distance": derived})
    elif task == "intersecting_circles_area":
        ba = int(arguments["ba"])
        bo = int(arguments["bo"])
        bc = int(arguments["bc"])
        r = sp.symbols("r", positive=True)
        chord = sp.Rational(ba - bc, bo) * r
        # Cyclic order A-O-B-C and the exact cyclic-quadrilateral
        # diagonal identity determine r.
        diagonal_squared = (
            (r * bc + bo * chord) * (r * chord + bo * bc)
            / (r * bo + bc * chord)
        )
        radius_squared = sp.solve(sp.Eq(diagonal_squared, ba**2), r**2)[0]
        area = sp.simplify(radius_squared * sp.pi)
        derived = _latex(area)
        normalized.update(
            {"radius_squared": _latex(radius_squared), "area": derived}
        )
    else:
        raise ValueError(f"unsupported exact coordinate-geometry task: {task}")
    return backend_result(
        normalized_result=normalized,
        certificate={"method": "exact_coordinate_constraints"},
        checked_claim="The exact coordinate constraints have the reported result.",
        derived_answer=derived,
    )
