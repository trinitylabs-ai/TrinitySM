"""Newclid-backed proof of typed plane-geometry predicates."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import os
import re
import sys
from pathlib import Path
from typing import Any

from .base import backend_result


BACKEND_VERSION = "newclid-geometry-proof-v1"
_RULE_ID_RE = re.compile(r"=\((r\d+)\s")


def _jgex_program(arguments: dict[str, Any]) -> str:
    clauses = []
    for construction in arguments["constructions"]:
        outputs = " ".join(construction["outputs"])
        payload = " ".join(
            [
                construction["construction"],
                *construction["arguments"],
            ]
        )
        clauses.append(f"{outputs} = {payload}")
    goals = [
        " ".join([goal["predicate"], *goal["arguments"]])
        for goal in arguments["goals"]
    ]
    return "; ".join(clauses) + " ? " + "; ".join(goals)


def _yuclid_api_default() -> Any:
    """Load Yuclid while honoring the current Python environment's scripts."""

    scripts_dir = str(Path(sys.executable).parent)
    previous_path = os.environ.get("PATH", "")
    os.environ["PATH"] = (
        scripts_dir
        if not previous_path
        else scripts_dir + os.pathsep + previous_path
    )
    try:
        module = importlib.import_module("py_yuclid.api_default")
    finally:
        os.environ["PATH"] = previous_path
    return module.HEDefault()


def prove_newclid_geometry(arguments: dict[str, Any]) -> dict[str, Any]:
    """Prove formal geometry goals using Newclid's full registered rule set."""

    from newclid import GeometricSolverBuilder
    from newclid.jgex.problem_builder import JGEXProblemBuilder

    program = _jgex_program(arguments)
    seed = int(arguments["seed"])
    problem = (
        JGEXProblemBuilder(rng=seed)
        .with_problem_from_txt(program, "math_harness_geometry")
        .build()
    )
    solver = GeometricSolverBuilder(
        rng=seed,
        api_default=_yuclid_api_default(),
    ).build(problem)
    proved = bool(solver.run())
    proof = solver.proof()
    # Preserve the caller's typed orientation. Newclid may canonicalize
    # symmetric predicates such as congruent segment pairs differently for
    # different numerical construction witnesses.
    goals = [
        " ".join([goal["predicate"], *goal["arguments"]])
        for goal in arguments["goals"]
    ]
    used_rule_ids = sorted(set(_RULE_ID_RE.findall(proof)))
    proof_digest = hashlib.sha256(proof.encode("utf-8")).hexdigest()
    return backend_result(
        normalized_result={
            "proved": proved,
            "goals": goals,
            "used_rule_ids": used_rule_ids,
            "proof_digest": proof_digest,
        },
        certificate={
            "engine": "newclid_yuclid",
            "newclid_version": importlib.metadata.version("newclid"),
            "yuclid_version": importlib.metadata.version("py-yuclid"),
            "jgex_program": program,
            "proof": proof,
            "source_quotes": list(arguments.get("source_quotes") or []),
        },
        checked_claim=(
            "The formal plane-geometry goals follow from the declared "
            "construction predicates under Newclid's deduction rules."
        ),
    )
