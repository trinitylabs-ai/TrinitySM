from __future__ import annotations

import re
from typing import Any


HARNESS_VERSION = (
    "full-cold-start-v0.3.28-r9-four-route-hypothesis-aware-phase1-over-v0.2.7"
)
TERRA_MODEL = "gpt-5.6-terra"
PHASE_ONE_ROUTE_COUNT = 4
MAX_CONJECTURE_ITERATIONS = 2
GUIDED_CANDIDATES_PER_ITERATION = 3
FRESH_CANDIDATES_PER_ITERATION = 1
TERRA_SUCCESS_CONFIRMATIONS = 3
MAX_CHILD_DEPTH = 2
MAX_NEW_CHILDREN_GLOBAL = 6
FINAL_CANDIDATE_FAMILIES = ("incumbent_plus_evidence", "evidence_only")

LEMMA_ID_PATTERN = r"I[12]\.H[1-3](?:\.C[1-9][0-9]*)*"
LEMMA_CITATION = re.compile(rf"\bLemma\s+({LEMMA_ID_PATTERN})\b")
LEMMA_TOKEN = re.compile(rf"\b{LEMMA_ID_PATTERN}\b")


def validate_fixed_profile(
    *,
    max_conjecture_iterations: int,
    guided_candidates: int,
    fresh_candidates: int,
    terra_confirmations: int,
) -> None:
    expected = {
        "max_conjecture_iterations": MAX_CONJECTURE_ITERATIONS,
        "guided_candidates": GUIDED_CANDIDATES_PER_ITERATION,
        "fresh_candidates": FRESH_CANDIDATES_PER_ITERATION,
        "terra_confirmations": TERRA_SUCCESS_CONFIRMATIONS,
    }
    actual = {
        "max_conjecture_iterations": int(max_conjecture_iterations),
        "guided_candidates": int(guided_candidates),
        "fresh_candidates": int(fresh_candidates),
        "terra_confirmations": int(terra_confirmations),
    }
    if actual != expected:
        raise ValueError(f"v0.3.28 fixed profile mismatch: {actual} != {expected}")


def memory_by_id(memory: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in memory:
        lemma_id = str(row.get("lemma_id") or "")
        if not re.fullmatch(LEMMA_ID_PATTERN, lemma_id):
            raise ValueError(f"invalid lemma_id: {lemma_id!r}")
        if lemma_id in indexed:
            raise ValueError(f"duplicate lemma_id: {lemma_id}")
        if row.get("direction") != "positive_verified":
            raise ValueError(f"non-positive evidence may not enter memory: {lemma_id}")
        if not str(row.get("statement") or "").strip() or not str(
            row.get("proof") or ""
        ).strip():
            raise ValueError(f"empty verified evidence: {lemma_id}")
        indexed[lemma_id] = row
    for lemma_id, row in indexed.items():
        dependencies = [str(value) for value in row.get("dependency_ids") or []]
        if len(dependencies) != len(set(dependencies)):
            raise ValueError(f"duplicate dependency in {lemma_id}")
        missing = [value for value in dependencies if value not in indexed]
        if missing:
            raise ValueError(f"unknown dependencies for {lemma_id}: {missing}")
    return indexed


def body_citations(body: str, memory: list[dict[str, Any]]) -> list[str]:
    indexed = memory_by_id(memory)
    citations = list(dict.fromkeys(LEMMA_CITATION.findall(body)))
    unknown = [value for value in citations if value not in indexed]
    if unknown:
        raise ValueError(f"body cites unknown verified lemmas: {unknown}")
    stripped = LEMMA_CITATION.sub("", body)
    bare = [value for value in LEMMA_TOKEN.findall(stripped) if value in indexed]
    if bare:
        raise ValueError(f"lemma IDs must use exact 'Lemma <id>' citation syntax: {bare}")
    return citations


def dependency_closure(
    cited_ids: list[str], memory: list[dict[str, Any]]
) -> list[str]:
    indexed = memory_by_id(memory)
    ordered: list[str] = []
    permanent: set[str] = set()
    active: set[str] = set()

    def visit(lemma_id: str) -> None:
        if lemma_id in permanent:
            return
        if lemma_id in active:
            raise ValueError(f"cyclic verified-memory dependency at {lemma_id}")
        active.add(lemma_id)
        for dependency_id in indexed[lemma_id].get("dependency_ids") or []:
            visit(str(dependency_id))
        active.remove(lemma_id)
        permanent.add(lemma_id)
        ordered.append(lemma_id)

    for cited_id in cited_ids:
        visit(cited_id)
    return ordered


def deterministic_appendices(
    body: str, memory: list[dict[str, Any]]
) -> tuple[list[str], list[dict[str, Any]]]:
    cited = body_citations(body, memory)
    indexed = memory_by_id(memory)
    closure = dependency_closure(cited, memory)
    appendices = [
        {
            "lemma_id": lemma_id,
            "statement": indexed[lemma_id]["statement"],
            "proof": indexed[lemma_id]["proof"],
            "dependency_ids": list(indexed[lemma_id].get("dependency_ids") or []),
            "direction": "positive_verified",
            "source": indexed[lemma_id].get("source"),
        }
        for lemma_id in closure
    ]
    return cited, appendices


def assemble_submission(body: str, appendices: list[dict[str, Any]]) -> str:
    parts = [body.strip()]
    if appendices:
        parts.append("Appendix: proofs of cited lemmas and their dependencies")
        for row in appendices:
            parts.append(
                f"Lemma {row['lemma_id']}. {row['statement']}\n\n"
                f"Proof. {str(row['proof']).strip()}\n\n"
                f"End of proof of Lemma {row['lemma_id']}."
            )
    return "\n\n".join(parts).strip()


def materialize_candidate(
    *, candidate_id: str, body: str, memory: list[dict[str, Any]], family: str
) -> dict[str, Any]:
    if not body.strip():
        raise ValueError("candidate body is empty")
    cited, appendices = deterministic_appendices(body, memory)
    return {
        "candidate_id": candidate_id,
        "family": family,
        "body": body,
        "cited_lemma_ids": cited,
        "appended_lemma_ids": [row["lemma_id"] for row in appendices],
        "lemma_appendices": appendices,
        "appendix_assembly": "deterministic_exact_copy_with_dependency_closure",
        "assembled_proof": assemble_submission(body, appendices),
    }


def global_audit_passed(audit: dict[str, Any] | None) -> bool:
    audit = audit or {}
    return bool(
        audit.get("verdict") == "pass"
        and audit.get("answer_supported") is True
        and audit.get("exact_problem_solved") is True
        and audit.get("proof_complete") is True
        and audit.get("first_break") is None
        and audit.get("repair_instruction") is None
        and audit.get("external_information_used") is False
    )


def unanimous_terra_success(audits: list[dict[str, Any]]) -> bool:
    return len(audits) == TERRA_SUCCESS_CONFIRMATIONS and all(
        global_audit_passed(row) for row in audits
    )


def candidate_rank(candidate: dict[str, Any]) -> tuple[int, int, float, str]:
    confirmed = int(bool(candidate.get("terra_unanimously_confirmed")))
    screened = int(global_audit_passed(candidate.get("final_global_audit")))
    grade = candidate.get("grade") or {}
    internal = grade.get("effective_score", grade.get("score", -1))
    numeric = float(internal) if isinstance(internal, (int, float)) else -1.0
    return confirmed, screened, numeric, str(candidate.get("candidate_id") or "")


def select_top_candidates(
    candidates: list[dict[str, Any]], count: int
) -> list[dict[str, Any]]:
    return sorted(candidates, key=candidate_rank, reverse=True)[:count]


def phase_one_route(candidate: dict[str, Any]) -> int | None:
    explicit = candidate.get("phase_one_route")
    if isinstance(explicit, int) and explicit > 0:
        return explicit
    match = re.fullmatch(
        r"phase1\.r([1-9][0-9]*)\..+", str(candidate.get("candidate_id") or "")
    )
    return int(match.group(1)) if match else None


def phase_one_terra_rank(
    candidate: dict[str, Any],
) -> tuple[int, int, int, int, int, str]:
    terra_score = candidate.get("phase_one_terra_score")
    if not isinstance(terra_score, dict):
        raise ValueError(
            f"Phase-1 candidate lacks a Terra score: {candidate.get('candidate_id')}"
        )
    score = terra_score.get("score")
    if score not in {0, 1, 2, 3, 4, 6, 7}:
        raise ValueError(
            f"invalid Terra score for {candidate.get('candidate_id')}: {score!r}"
        )
    return (
        int(score),
        int(terra_score.get("hypothesis_seed_value", 0)),
        int(bool(terra_score.get("root_characterization_plausible"))),
        int(bool(terra_score.get("answer_supported"))),
        int(bool(terra_score.get("complete"))),
        str(candidate.get("candidate_id") or ""),
    )


def select_route_balanced_phase_one_candidates(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Select the best Phase-1 seed from each of the two independent routes."""

    by_route: dict[int, list[dict[str, Any]]] = {
        route: [] for route in range(1, PHASE_ONE_ROUTE_COUNT + 1)
    }
    for candidate in candidates:
        route = phase_one_route(candidate)
        if route in by_route:
            by_route[route].append(candidate)
    missing = [route for route, rows in by_route.items() if not rows]
    if missing:
        raise ValueError(f"missing Phase-1 candidates for routes: {missing}")
    return [
        sorted(by_route[route], key=phase_one_terra_rank, reverse=True)[0]
        for route in range(1, PHASE_ONE_ROUTE_COUNT + 1)
    ]


def select_top_two_per_phase_one_route(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Retain two Terra-ranked finalists from each independent Phase-1 route."""

    by_route: dict[int, list[dict[str, Any]]] = {
        route: [] for route in range(1, PHASE_ONE_ROUTE_COUNT + 1)
    }
    for candidate in candidates:
        route = phase_one_route(candidate)
        if route in by_route:
            by_route[route].append(candidate)
    incomplete = [route for route, rows in by_route.items() if len(rows) < 2]
    if incomplete:
        raise ValueError(
            f"fewer than two Phase-1 candidates for routes: {incomplete}"
        )
    finalists: list[dict[str, Any]] = []
    for route in range(1, PHASE_ONE_ROUTE_COUNT + 1):
        finalists.extend(
            sorted(by_route[route], key=phase_one_terra_rank, reverse=True)[:2]
        )
    return finalists
