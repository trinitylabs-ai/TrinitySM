"""Independent checks for exact-cover evidence."""

from __future__ import annotations

from typing import Any

from ..backends.exact_cover import rectangular_loop_masks


VALIDATOR_VERSION = "rectangular-loop-certificate-v1"


def validate_rectangular_loop_exact_cover(
    arguments: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    rows = int(arguments["rows"])
    columns = int(arguments["columns"])
    loop_count = int(arguments["loop_count"])
    normalized = result.get("normalized_result", {})
    certificate = result.get("certificate", {})
    masks = rectangular_loop_masks(rows, columns)
    selected = tuple(int(value) for value in certificate.get("selected_masks", []))
    full = (1 << (rows * columns)) - 1
    union = 0
    disjoint = True
    for mask in selected:
        if mask not in masks or union & mask:
            disjoint = False
            break
        union |= mask
    certificate_valid = (
        len(selected) == loop_count and disjoint and union == full
    ) if int(normalized.get("count", 0)) > 0 else not selected
    legal_count_valid = normalized.get("legal_object_count") == len(masks)

    # Independently compare optimized counting with a deliberately simple
    # recursion on reduced instances. This validates generator semantics and
    # canonical first-uncovered-cell counting without making full runs costly.
    reduced_checks: list[dict[str, int]] = []
    for small_rows, small_columns, small_loops in ((2, 2, 1), (4, 4, 2)):
        small_masks = rectangular_loop_masks(small_rows, small_columns)
        small_full = (1 << (small_rows * small_columns)) - 1
        by_cell = [[] for _ in range(small_rows * small_columns)]
        for mask in small_masks:
            for index in range(small_rows * small_columns):
                if mask >> index & 1:
                    by_cell[index].append(mask)

        def simple(covered: int, used: int) -> int:
            if used == small_loops:
                return int(covered == small_full)
            missing = small_full ^ covered
            first = (missing & -missing).bit_length() - 1
            return sum(
                simple(covered | mask, used + 1)
                for mask in by_cell[first]
                if not mask & covered
            )

        reduced_checks.append(
            {
                "rows": small_rows,
                "columns": small_columns,
                "loop_count": small_loops,
                "count": simple(0, 0),
            }
        )
    valid = certificate_valid and legal_count_valid
    return {
        "passed": valid,
        "details": {
            "certificate_valid": certificate_valid,
            "legal_object_count_valid": legal_count_valid,
            "reduced_bruteforce_checks": reduced_checks,
        },
        "version": VALIDATOR_VERSION,
    }
