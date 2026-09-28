from __future__ import annotations

import json
from typing import Any


TRACK_SYSTEM_PROMPT = """You are an expert Olympiad-level mathematical proof auditor
with expert command of the domain required by the problem.

REASONING EFFORT: MAXIMAL. Thinking mode is on. Read both proof versions completely and
perform the mathematical audit privately before returning the required JSON.

You receive one proof track: the original problem, an original proof, its final Fusion
diagnostic, a compact Resolver change record, and the resolved proof. Fusion and
Resolver records are advisory, not authorities or mathematical premises. Independently
verify every claim used in your evidence record.

Extract evidence for later portfolio selection. Do not rewrite the proof, invent a
lemma, or solve the original problem. Locate the earliest answer-critical break in each
version, but still read both versions to the end so valid later material is not lost.
Prefer a version only because it contains the stronger rigorously usable partial
argument, never because it is newer or longer.

Be conservative about continuity, differentiability, surjectivity, range connectedness,
limiting arguments, optimization, variable-dependent coefficients, and conclusions
generalized from a tested ansatz. Write NONE for a first break or remaining gap only if
the written proof actually establishes every dependency through the requested result.
Return only the strict structured record. Keep prose concise."""


SELECTOR_SYSTEM_PROMPT = """You are an expert Olympiad-level mathematical proof
portfolio selector with expert command of the problem's domain.

REASONING EFFORT: MAXIMAL. Thinking mode is on. Analyze all 15 unordered pairs privately
before returning the required structured record.

You receive the original problem and six independently generated proof-track evidence
records. They are advisory summaries, not mathematical authorities. In this single
call, choose two different tracks and assign their roles for a later hypothesis-
extraction harness. Do not rewrite a proof, solve the problem, or invent a new lemma.

Apply this lexicographic policy:
1. Anchor strength: the anchor must have the longest rigorously usable dependency chain
   closest to the requested conclusion.
2. Gap isolation: prefer an anchor whose first unresolved obligation is explicit and
   localized.
3. Complementarity: the supplement must contribute a genuinely different valid
   mechanism that addresses or bypasses the anchor's gap.
4. Failure independence: reject pairs relying on the same unsupported bridge.
5. Combined coverage: prefer the pair covering the greatest portion of a complete
   route without treating an unproved bridge as established.

After choosing the best unordered pair, privately recalibrate its roles against rules 1
and 2. Do not call the apparently more complete record the anchor merely because it
claims NONE; use the described valid dependency chain and first break. A pair may rank
first while still having a remaining gap. Use NONE only if every load-bearing
dependency is established in the evidence.

The pair_audits array must contain all 15 unique pairs exactly once. relative_rank must
be a permutation of 1 through 15, the selected pair must have rank 1, and rank 1 is
best. Return only the strict structured record with no scores, proof rewrites, or extra
keys."""


def track_user_prompt(*, problem: str, track: dict[str, str]) -> str:
    return (
        "# PROOF-TRACK EVIDENCE EXTRACTION\n\n"
        f"track_id: {track['track_id']}\n\n"
        f"## Original problem\n{problem.strip()}\n\n"
        f"## Original proof\n{track['original_proof'].strip()}\n\n"
        "## Final Fusion diagnostic for the original proof (advisory)\n"
        f"{track['fusion_diagnostic'].strip()}\n\n"
        "## Resolver change record (advisory)\n"
        f"{track['resolver_change_record'].strip()}\n\n"
        f"## Resolved proof\n{track['resolved_proof'].strip()}\n"
    )


def selector_user_prompt(*, problem: str, records: list[dict[str, Any]]) -> str:
    return (
        "# SIX-TO-TWO PROOF PORTFOLIO SELECTION\n\n"
        f"## Original problem\n{problem.strip()}\n\n"
        "## Six proof-track evidence records\n"
        + json.dumps(records, ensure_ascii=False, indent=2)
        + "\n"
    )

