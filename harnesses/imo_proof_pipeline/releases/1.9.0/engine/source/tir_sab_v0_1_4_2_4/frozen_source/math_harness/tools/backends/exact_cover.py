"""Deterministic exact-cover operations implemented with integer bitmasks."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from .base import backend_result


def rectangular_loop_masks(rows: int, columns: int) -> tuple[int, ...]:
    if not 2 <= rows <= 16 or not 2 <= columns <= 16:
        raise ValueError("rectangular-loop grids must be between 2 and 16 per side")
    masks: list[int] = []
    for height in range(2, rows + 1):
        for width in range(2, columns + 1):
            for top in range(rows - height + 1):
                for left in range(columns - width + 1):
                    mask = 0
                    for row in range(top, top + height):
                        for column in range(left, left + width):
                            if (
                                row in (top, top + height - 1)
                                or column in (left, left + width - 1)
                            ):
                                mask |= 1 << (row * columns + column)
                    masks.append(mask)
    return tuple(masks)


def _decode_mask(mask: int, columns: int) -> list[list[int]]:
    cells: list[list[int]] = []
    index = 0
    while mask:
        if mask & 1:
            cells.append([index // columns, index % columns])
        mask >>= 1
        index += 1
    return cells


def rectangular_loop_exact_cover(arguments: dict[str, Any]) -> dict[str, Any]:
    rows = int(arguments["rows"])
    columns = int(arguments["columns"])
    object_count = int(arguments["loop_count"])
    if not 1 <= object_count <= 16:
        raise ValueError("loop_count must be between 1 and 16")
    masks = rectangular_loop_masks(rows, columns)
    cell_count = rows * columns
    full = (1 << cell_count) - 1
    by_cell: list[list[int]] = [[] for _ in range(cell_count)]
    for mask in masks:
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            by_cell[index].append(mask)
            remaining ^= bit

    calls = 0
    first_solution: tuple[int, ...] | None = None

    @lru_cache(maxsize=None)
    def count(covered: int, used: int) -> int:
        nonlocal calls, first_solution
        calls += 1
        if used == object_count:
            return int(covered == full)
        remaining_cells = cell_count - covered.bit_count()
        slots = object_count - used
        if remaining_cells < 4 * slots:
            return 0
        missing = full ^ covered
        first = (missing & -missing).bit_length() - 1
        total = 0
        for mask in by_cell[first]:
            if mask & covered:
                continue
            subtotal = count(covered | mask, used + 1)
            if subtotal and first_solution is None and used == 0:
                # The complete certificate is recovered deterministically below.
                first_solution = (mask,)
            total += subtotal
        return total

    total = count(0, 0)

    def recover(covered: int, used: int) -> tuple[int, ...]:
        if used == object_count:
            return () if covered == full else ()
        missing = full ^ covered
        first = (missing & -missing).bit_length() - 1
        for mask in by_cell[first]:
            if not (mask & covered) and count(covered | mask, used + 1):
                return (mask, *recover(covered | mask, used + 1))
        return ()

    solution = recover(0, 0) if total else ()
    certificate = {
        "universe_size": cell_count,
        "legal_object_count": len(masks),
        "selected_masks": [str(mask) for mask in solution],
        "selected_cells": [_decode_mask(mask, columns) for mask in solution],
        "state_count": calls,
        "cache_hits": count.cache_info().hits,
    }
    checked = (
        f"Count partitions of a {rows} by {columns} cell grid into exactly "
        f"{object_count} rectangular cell loops."
    )
    return backend_result(
        normalized_result={
            "count": total,
            "rows": rows,
            "columns": columns,
            "loop_count": object_count,
            "legal_object_count": len(masks),
        },
        certificate=certificate,
        checked_claim=checked,
        derived_answer=str(total),
    )
