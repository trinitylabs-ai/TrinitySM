from __future__ import annotations

import json
from typing import Any

from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824.protocol import (
    main_proof_prompt as v063_experimental_main_proof_prompt,
)
from cognitive_well_harness_v0_3_63_deterministic_lemma_appendix_20260824.run_failure_guided_salvage_surgical import (
    SYSTEM_PROMPT as V063_FAILURE_SALVAGE_SYSTEM_PROMPT,
)


FAILURE_SALVAGE_SYSTEM_PROMPT = V063_FAILURE_SALVAGE_SYSTEM_PROMPT


def failure_salvage_user_prompt(
    *,
    problem: str,
    candidate_proofs: list[dict[str, str]],
    failure_card: dict[str, Any],
) -> str:
    proof_packet = [
        {
            "solution_id": str(row.get("solution_id") or row["candidate_id"]),
            "role": str(row["role"]),
            "proof": str(row["proof"]),
        }
        for row in candidate_proofs
    ]
    return (
        "ORIGINAL PROBLEM:\n"
        + problem
        + "\n\nORIGINAL PROOF ATTEMPTS:\n"
        + json.dumps(proof_packet, ensure_ascii=False)
        + "\n\nFAILED-HYPOTHESIS MEMORY CARD:\n"
        + json.dumps(failure_card, ensure_ascii=False)
        + "\n\nRepair, decompose, or abandon this hypothesis route now."
    )


def statement_only_synthesis_prompt(
    *, problem: str, lemmas: list[dict[str, str]]
) -> str:
    return v063_experimental_main_proof_prompt(problem=problem, lemmas=lemmas)
