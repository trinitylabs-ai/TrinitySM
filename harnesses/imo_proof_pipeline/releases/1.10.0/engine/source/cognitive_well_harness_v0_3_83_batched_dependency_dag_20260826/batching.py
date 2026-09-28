from __future__ import annotations

import concurrent.futures
import copy
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, TypeVar

from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_67_modular_six_track_generation_review_resolution_20260824 import (
    pipeline as v067,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.contracts import (
    NEGATION_AUDIT_SCHEMA,
    NEGATION_REPAIR_SCHEMA,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.lemma_proving import (
    prove_pairs,
)
from cognitive_well_harness_v0_3_72_modular_location_aware_split_verifier_20260824.prompts import (
    negation_audit_prompt,
    negation_repair_prompt,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.retry import (
    read_json,
    run_atomic_retry,
)
from cognitive_well_harness_v0_3_79_modular_singleton_atomic_retry_20260825.runtime import (
    ResilientModelRuntime,
)
from cognitive_well_harness_v0_3_81_iterative_dual_memory_loop_20260825 import (
    pipeline as v081,
)
from cognitive_well_harness_v0_3_82_contextual_surgical_memory_20260826 import (
    pipeline as v082,
)
from cognitive_well_harness_v0_3_82_contextual_surgical_memory_20260826.contracts import (
    LITERAL_AUDIT_SCHEMA,
    MAX_CONTEXTUAL_REWRITES,
    MEMORY_DISPOSITION_SCHEMA,
    QWEN_REPAIR_SPEC_SCHEMA,
)
from cognitive_well_harness_v0_3_82_contextual_surgical_memory_20260826.prompts import (
    audit_anchor_extraction_prompt,
    contextual_rewrite_prompt,
    literal_anchor_audit_prompt,
    memory_disposition_prompt,
    qwen_repair_spec_prompt,
)


GEMMA_BATCH = 4
QWEN_BATCH = 4
PROOF_SIDE_BATCH = 2
SYNTHESIS_BATCH = 6
MAX_DYNAMIC_LITERAL_ANCHORS = 6
MIN_BOUND_DYNAMIC_LITERAL_ANCHORS = 4

V083_AUDIT_ANCHOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["anchors"],
    "properties": {
        "anchors": {
            "type": "array",
            "minItems": MIN_BOUND_DYNAMIC_LITERAL_ANCHORS,
            "maxItems": MAX_DYNAMIC_LITERAL_ANCHORS,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "exact_quote",
                    "local_claim",
                    "required_support",
                    "downstream_dependency",
                ],
                "properties": {
                    "exact_quote": {"type": "string", "minLength": 3},
                    "local_claim": {"type": "string", "minLength": 3},
                    "required_support": {"type": "string", "minLength": 1},
                    "downstream_dependency": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
            },
        }
    },
}

T = TypeVar("T")


def prioritized_audit_anchor_extraction_prompt(*, problem: str, proof: str) -> str:
    """Use a lean, dependency-prioritized four-field anchor contract."""
    source = audit_anchor_extraction_prompt(problem=problem, proof=proof)
    old_count = (
        "Read the complete proof and extract up to 24 load-bearing passages in proof order."
    )
    new = f"""Read the complete proof and extract at most {MAX_DYNAMIC_LITERAL_ANCHORS} load-bearing
passages in proof order. Prioritize transitions whose failure would invalidate the
final conclusion, especially unproved bridges between established facts and a
downstream claim. Omit routine consequences when a more load-bearing passage is
available."""
    old_fields = """For each, copy an exact quote and record the mathematical claim, introduced objects
and their declared domains, required prior facts, invoked operation or result, and the
downstream conclusion depending on it."""
    new_fields = """For each passage return only these four fields: exact_quote, local_claim,
required_support, and downstream_dependency. exact_quote must be a contiguous
byte-for-byte substring of COMPLETE PROOF, preserving the original LaTeX delimiters,
backslashes, spacing, and punctuation."""
    if old_count not in source or old_fields not in source:
        raise RuntimeError("v0.3.82 anchor prompt contract changed unexpectedly")
    return source.replace(old_count, new, 1).replace(old_fields, new_fields, 1)


def validate_prioritized_anchor_records(
    proof: str, anchors: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    """Bind quotes exactly or by a unique formatting-only canonical match.

    Canonical binding tolerates transport differences in whitespace, math
    delimiters, and equivalent LaTeX/Unicode spellings.  It never fuzzy-matches
    words or mathematical operators.  A successful canonical match is replaced
    by the corresponding verbatim span from ``proof`` before downstream use.
    """
    aligned = [dict(anchor) for anchor in anchors]
    errors: list[str] = []
    bindings: list[dict[str, Any]] = []
    proof_tokens = _canonical_transport_tokens(proof)
    proof_values = [token[0] for token in proof_tokens]
    for index, anchor in enumerate(aligned, start=1):
        quote = str(anchor.get("exact_quote", ""))
        exact_occurrences = proof.count(quote) if quote else 0
        if exact_occurrences == 1:
            start = proof.index(quote)
            bindings.append(
                {
                    "anchor_id": f"A{index}",
                    "mode": "EXACT",
                    "source_start": start,
                    "source_end": start + len(quote),
                }
            )
            continue

        quote_tokens = _canonical_transport_tokens(quote)
        quote_values = [token[0] for token in quote_tokens]
        while quote_values and quote_values[-1] in {".", ",", ";", ":"}:
            quote_values.pop()
        occurrences: list[int] = []
        if quote_values:
            width = len(quote_values)
            occurrences = [
                offset
                for offset in range(len(proof_values) - width + 1)
                if proof_values[offset : offset + width] == quote_values
            ]
        if len(occurrences) != 1:
            reason = "not_found" if not occurrences else "ambiguous"
            errors.append(f"quote_not_canonically_unique:A{index}:{reason}")
            bindings.append(
                {
                    "anchor_id": f"A{index}",
                    "mode": "FAILED",
                    "reason": reason,
                    "canonical_occurrences": len(occurrences),
                }
            )
            continue

        token_offset = occurrences[0]
        source_start = proof_tokens[token_offset][1]
        source_end = proof_tokens[token_offset + len(quote_values) - 1][2]
        source_start, source_end = _include_adjacent_math_delimiters(
            proof, source_start, source_end
        )
        transported = quote.rstrip()
        if (
            transported
            and transported[-1] in ".,;:"
            and proof.startswith(transported[-1], source_end)
        ):
            source_end += 1
        aligned[index - 1]["exact_quote"] = proof[source_start:source_end]
        bindings.append(
            {
                "anchor_id": f"A{index}",
                "mode": "CANONICAL_UNIQUE",
                "source_start": source_start,
                "source_end": source_end,
            }
        )
    return aligned, errors, bindings


_LATEX_COMMAND_ALIASES = {
    "ge": ">=",
    "geq": ">=",
    "geqslant": ">=",
    "le": "<=",
    "leq": "<=",
    "leqslant": "<=",
    "ne": "!=",
    "neq": "!=",
    "in": "in",
    "notin": "notin",
    "to": "->",
    "rightarrow": "->",
    "longrightarrow": "->",
    "implies": "=>",
    "Rightarrow": "=>",
    "iff": "<=>",
    "Leftrightarrow": "<=>",
    "infty": "infinity",
    "sqrt": "sqrt",
    "frac": "frac",
    "approx": "approx",
    "cdot": "*",
    "times": "*",
}
_LATEX_FORMATTING_COMMANDS = {
    "left",
    "right",
    "big",
    "Big",
    "bigl",
    "bigr",
    "quad",
    "qquad",
}
_LATEX_WRAPPER_COMMANDS = {"mathbb", "mathbf", "mathrm", "text", "operatorname"}
_UNICODE_TRANSPORT_ALIASES = {
    "≥": ">=",
    "≤": "<=",
    "≠": "!=",
    "∈": "in",
    "∉": "notin",
    "→": "->",
    "⇒": "=>",
    "⇔": "<=>",
    "∞": "infinity",
    "√": "sqrt",
    "≈": "approx",
    "·": "*",
    "×": "*",
    "−": "-",
    "δ": "delta",
    "ε": "epsilon",
    "θ": "theta",
    "φ": "phi",
    "π": "pi",
}
_PLAIN_WORD_ALIASES = {
    "infinity": "infinity",
    "sqrt": "sqrt",
    "frac": "frac",
    "notin": "notin",
    "implies": "=>",
    "approx": "approx",
}


def _matching_brace(text: str, opening: int) -> int | None:
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _canonical_transport_tokens(
    text: str, *, base_offset: int = 0
) -> list[tuple[str, int, int]]:
    """Tokenize without normalizing mathematical content or prose wording."""
    tokens: list[tuple[str, int, int]] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character.isspace() or character in {"$", "~"}:
            index += 1
            continue
        if text.startswith((r"\(", r"\)", r"\[", r"\]"), index):
            index += 2
            continue
        if character == "\\":
            command_match = re.match(r"\\([A-Za-z]+)", text[index:])
            if command_match:
                command = command_match.group(1)
                command_end = index + len(command_match.group(0))
                if (
                    command in _LATEX_WRAPPER_COMMANDS
                    and command_end < len(text)
                    and text[command_end] == "{"
                ):
                    closing = _matching_brace(text, command_end)
                    if closing is not None:
                        tokens.extend(
                            _canonical_transport_tokens(
                                text[command_end + 1 : closing],
                                base_offset=base_offset + command_end + 1,
                            )
                        )
                        index = closing + 1
                        continue
                if command not in _LATEX_FORMATTING_COMMANDS:
                    tokens.append(
                        (
                            _LATEX_COMMAND_ALIASES.get(command, command),
                            base_offset + index,
                            base_offset + command_end,
                        )
                    )
                index = command_end
                continue
            if index + 1 < len(text) and text[index + 1] in "{},;! ":
                if text[index + 1] in "{}":
                    tokens.append(
                        (
                            "(" if text[index + 1] == "{" else ")",
                            base_offset + index,
                            base_offset + index + 2,
                        )
                    )
                index += 2
                continue
        matched_operator = next(
            (
                operator
                for operator in ("<=>", ">=", "<=", "!=", "->", "=>")
                if text.startswith(operator, index)
            ),
            None,
        )
        if matched_operator is not None:
            tokens.append(
                (
                    matched_operator,
                    base_offset + index,
                    base_offset + index + len(matched_operator),
                )
            )
            index += len(matched_operator)
            continue
        if character in _UNICODE_TRANSPORT_ALIASES:
            tokens.append(
                (
                    _UNICODE_TRANSPORT_ALIASES[character],
                    base_offset + index,
                    base_offset + index + 1,
                )
            )
            index += 1
            continue
        if character == "{":
            closing = _matching_brace(text, index)
            if closing is not None:
                inner = text[index + 1 : closing]
                if re.fullmatch(r"[A-Za-z]+", inner):
                    value = _LATEX_COMMAND_ALIASES.get(
                        inner, _PLAIN_WORD_ALIASES.get(inner, inner)
                    )
                    tokens.append(
                        (
                            value,
                            base_offset + index,
                            base_offset + closing + 1,
                        )
                    )
                    index = closing + 1
                    continue
        word_match = re.match(r"[A-Za-z]+", text[index:])
        if word_match:
            word = word_match.group(0)
            tokens.append(
                (
                    _PLAIN_WORD_ALIASES.get(word, word),
                    base_offset + index,
                    base_offset + index + len(word),
                )
            )
            index += len(word)
            continue
        number_match = re.match(r"\d+(?:\.\d+)?", text[index:])
        if number_match:
            number = number_match.group(0)
            tokens.append(
                (
                    number,
                    base_offset + index,
                    base_offset + index + len(number),
                )
            )
            index += len(number)
            continue
        value = "(" if character in "{[(" else ")" if character in "}])" else character
        tokens.append((value, base_offset + index, base_offset + index + 1))
        index += 1

    # Braces around a simple square-root argument are a pure LaTeX transport
    # choice: \sqrt{x}, sqrt(x), and √x carry the same token sequence.
    compacted: list[tuple[str, int, int]] = []
    index = 0
    while index < len(tokens):
        if (
            tokens[index][0] == "sqrt"
            and index + 3 < len(tokens)
            and tokens[index + 1][0] == "("
        ):
            closing = index + 2
            while closing < len(tokens) and tokens[closing][0] != ")":
                closing += 1
            inside = [token[0] for token in tokens[index + 2 : closing]]
            if closing < len(tokens) and inside and all(
                token.isalnum() or token in {"_", "^"} for token in inside
            ):
                compacted.append(tokens[index])
                compacted.extend(tokens[index + 2 : closing])
                index = closing + 1
                continue
        compacted.append(tokens[index])
        index += 1
    return compacted


def _include_adjacent_math_delimiters(
    proof: str, source_start: int, source_end: int
) -> tuple[int, int]:
    for delimiter in ("$$", "$", r"\(", r"\["):
        opening = source_start - len(delimiter)
        if opening >= 0 and proof[opening:source_start] == delimiter:
            source_start = opening
            break
    for delimiter in ("$$", "$", r"\)", r"\]"):
        if proof.startswith(delimiter, source_end):
            source_end += len(delimiter)
            break
    return source_start, source_end


def _parallel_map(
    worker: Callable[[T], Any], rows: list[T], *, max_workers: int
) -> list[Any]:
    if not rows:
        return []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(max_workers, len(rows))
    ) as executor:
        return list(executor.map(worker, rows))


def batching_matrix() -> dict[int, dict[str, Any]]:
    """Machine-readable execution policy for all eleven stages."""
    return {
        1: {
            "policy": "batch",
            "model": "gemma",
            "width": 3,
            "barrier": "all extraction rounds before novelty",
        },
        2: {
            "policy": "flattened_vote_batch",
            "model": "qwen",
            "width": QWEN_BATCH,
            "barrier": "two votes grouped per hypothesis before decision",
        },
        3: {
            "policy": "wave_dag",
            "models": ["qwen", "gemma"],
            "width": {"qwen": QWEN_BATCH, "gemma": GEMMA_BATCH},
            "barrier": "audit -> conditional repair -> re-audit; paired certification remains bounded",
        },
        4: {
            "policy": "batch",
            "model": "gemma",
            "width": SYNTHESIS_BATCH,
            "barrier": "all candidates consume one immutable memory snapshot",
        },
        5: {
            "policy": "cross_gpu_review_dag",
            "width": {"gemma": GEMMA_BATCH, "qwen": QWEN_BATCH},
            "barrier": "fusion waits for R1+R2+R3 per proof",
        },
        6: {
            "policy": "batch",
            "model": "gemma",
            "width": SYNTHESIS_BATCH,
            "barrier": "each rewrite consumes immutable audit packets",
        },
        7: {
            "policy": "cross_gpu_review_dag",
            "width": {"gemma": GEMMA_BATCH, "qwen": QWEN_BATCH},
            "barrier": "fusion waits for fresh R1+R2+R3 per proof",
        },
        8: {
            "policy": "candidate_pipelines",
            "width": {"gemma": SYNTHESIS_BATCH, "qwen": QWEN_BATCH},
            "barrier": "literal audit waits for that proof's extracted anchors",
        },
        9: {
            "policy": "batched_repair_rounds",
            "width": {"gemma": GEMMA_BATCH, "qwen": QWEN_BATCH},
            "barrier": "attribution -> replay -> specification -> rewrite -> fresh gates",
        },
        10: {
            "policy": "parallel_proposals_serial_commit",
            "model": "qwen",
            "width": QWEN_BATCH,
            "barrier": "deterministic supersession arbitration and atomic commit",
        },
        11: {
            "policy": "batched_track_audit_then_single_selection",
            "model": "gemma",
            "width": GEMMA_BATCH,
            "barrier": "pair selection waits for every track audit",
        },
    }


def novelty_gate_batched(
    *,
    runtime: ResilientModelRuntime,
    extraction_results: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Flatten all independent failed-memory votes into one Qwen batch."""
    candidates: list[dict[str, Any]] = []
    for extraction in extraction_results:
        for hypothesis_index, hypothesis in enumerate(
            extraction["record"]["hypotheses"], start=1
        ):
            candidates.append(
                {
                    **hypothesis,
                    "source_round": extraction["round"],
                    "source_temperature": extraction["temperature"],
                    "source_hypothesis_index": hypothesis_index,
                }
            )

    certified_statements = {
        v081.normalized(str(row["statement"])) for row in certified_memory
    }
    active_failed = [
        row for row in failed_memory if not row.get("resolved_by_certification")
    ]
    failed_exact = {
        v081._failure_exact_key(row): row for row in active_failed
    }
    early: dict[int, dict[str, Any]] = {}
    pending: list[tuple[int, dict[str, Any]]] = []
    for index, candidate in enumerate(candidates, start=1):
        if v081.normalized(str(candidate["conjecture"])) in certified_statements:
            early[index] = {
                "candidate": candidate,
                "decision": "reject_exact_certified_statement",
            }
            continue
        exact_failure = failed_exact.get(v081._hypothesis_exact_key(candidate))
        if exact_failure is not None:
            early[index] = {
                "candidate": candidate,
                "decision": "reject_exact_failed_duplicate",
                "matched_failed_id": exact_failure["failed_id"],
            }
            continue
        pending.append((index, candidate))

    jobs = [
        (index, candidate, vote)
        for index, candidate in pending
        for vote in (1, 2)
    ] if active_failed else []

    def compare(job: tuple[int, dict[str, Any], int]) -> dict[str, Any]:
        index, candidate, vote = job
        record, generation = runtime.structured(
            role="qwen",
            prompt=v081.FAILED_COMPARATOR_PROMPT,
            user_prompt=v081.failed_comparator_user_prompt(
                candidate=candidate, failed_memory=active_failed
            ),
            destination=output_dir / f"candidate_{index}" / f"comparison_{vote}",
            stage="failed_semantic_comparison",
            schema=v081.FAILED_COMPARATOR_SCHEMA,
            temperature=0.1,
            max_tokens=16_384,
            seed_label=f"v083:i{iteration}:failed_compare:{index}:{vote}",
        )
        return {
            "candidate_index": index,
            "vote": vote,
            "record": record,
            "generation": generation["metadata"],
        }

    vote_rows = _parallel_map(compare, jobs, max_workers=QWEN_BATCH)
    votes_by_candidate: dict[int, list[dict[str, Any]]] = {}
    for row in vote_rows:
        votes_by_candidate.setdefault(int(row["candidate_index"]), []).append(row)
    for rows in votes_by_candidate.values():
        rows.sort(key=lambda row: int(row["vote"]))

    accepted: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    pending_by_index = dict(pending)
    for index, candidate in enumerate(candidates, start=1):
        if index in early:
            audit.append(early[index])
            continue
        if not active_failed:
            accepted.append(candidate)
            audit.append(
                {"candidate": candidate, "decision": "accepted", "semantic": None}
            )
            continue
        calls = votes_by_candidate.get(index, [])
        if len(calls) != 2:
            raise RuntimeError(f"semantic comparison vote count != 2 for candidate {index}")
        classifications = [
            str(row["record"]["classification"]) for row in calls
        ]
        reject = classifications == ["SAME_FAILED_HYPOTHESIS"] * 2
        semantic = {
            "calls": calls,
            "unanimous_semantic_duplicate": reject,
            "decision": (
                "reject_semantic_failed_duplicate" if reject else "allow"
            ),
        }
        if reject:
            audit.append({"candidate": pending_by_index[index], **semantic})
        else:
            accepted.append(candidate)
            audit.append(
                {"candidate": candidate, "decision": "accepted", "semantic": semantic}
            )
    write_json(output_dir / "audit.json", audit)
    write_json(
        output_dir / "batch_summary.json",
        {
            "candidate_count": len(candidates),
            "semantic_vote_job_count": len(jobs),
            "qwen_batch_width": QWEN_BATCH,
            "accepted_count": len(accepted),
        },
    )
    return accepted, audit


def validate_and_repair_negations_batched(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    hypotheses: dict[str, Any],
    arm: str,
    round_number: int,
    output_dir: Path,
) -> list[dict[str, str]]:
    """Audit, conditionally repair, and re-audit negations in three waves."""
    items: list[dict[str, Any]] = []
    for index, hypothesis in enumerate(hypotheses["hypotheses"], start=1):
        items.append(
            {
                "index": index,
                "claim_id": f"R{round_number}H{index}_{arm}",
                "claim": str(hypothesis["conjecture"]),
                "negation": str(hypothesis["exact_negation"]),
                "earliest_unresolved_transition": str(
                    hypothesis["earliest_unresolved_transition"]
                ),
                "local_dependency_map": str(hypothesis["local_dependency_map"]),
            }
        )

    def audit_item(payload: tuple[dict[str, Any], int]) -> dict[str, Any]:
        item, wave = payload
        audit, generation = runtime.structured(
            role="qwen",
            prompt=negation_audit_prompt(
                problem=problem,
                claim=item["claim"],
                proposed_negation=item["negation"],
            ),
            destination=output_dir / item["claim_id"],
            stage=f"negation_audit_{wave}",
            schema=NEGATION_AUDIT_SCHEMA,
            temperature=0.2,
            max_tokens=8_192,
            seed_label=f"v083:{item['claim_id']}:negation:audit:{wave}",
        )
        return {"item": item, "audit": audit, "generation": generation["metadata"]}

    initial = _parallel_map(
        audit_item, [(item, 0) for item in items], max_workers=QWEN_BATCH
    )
    invalid = [row for row in initial if not row["audit"]["valid_exact_negation"]]

    def repair_item(row: dict[str, Any]) -> dict[str, Any]:
        item = copy.deepcopy(row["item"])
        repair, generation = runtime.structured(
            role="gemma",
            prompt=negation_repair_prompt(
                problem=problem,
                claim=item["claim"],
                negation=item["negation"],
                first_issue=row["audit"]["first_issue"],
            ),
            destination=output_dir / item["claim_id"],
            stage="negation_repair",
            schema=NEGATION_REPAIR_SCHEMA,
            temperature=0.1,
            max_tokens=8_192,
            seed_label=f"v083:{item['claim_id']}:negation:repair",
        )
        item["negation"] = str(repair["exact_negation"])
        return {"item": item, "repair": repair, "generation": generation["metadata"]}

    repaired = _parallel_map(repair_item, invalid, max_workers=GEMMA_BATCH)
    reaudited = _parallel_map(
        audit_item,
        [(row["item"], 1) for row in repaired],
        max_workers=QWEN_BATCH,
    )
    final_by_id = {row["item"]["claim_id"]: row for row in initial}
    for row in reaudited:
        final_by_id[row["item"]["claim_id"]] = row

    pairs: list[dict[str, str]] = []
    for original in items:
        row = final_by_id[original["claim_id"]]
        item = row["item"]
        if not row["audit"]["valid_exact_negation"]:
            raise RuntimeError(
                f"exact negation was not certified for {item['claim_id']}"
            )
        pair = {
            "claim_id": str(item["claim_id"]),
            "positive": str(item["claim"]),
            "negative": str(item["negation"]),
            "earliest_unresolved_transition": str(
                item["earliest_unresolved_transition"]
            ),
            "local_dependency_map": str(item["local_dependency_map"]),
        }
        write_json(
            output_dir / item["claim_id"] / "result.json",
            {**pair, "audit": row["audit"]},
        )
        pairs.append(pair)
    write_json(
        output_dir / "batch_summary.json",
        {
            "pair_count": len(pairs),
            "initial_qwen_audits": len(initial),
            "conditional_gemma_repairs": len(repaired),
            "qwen_reaudits": len(reaudited),
        },
    )
    return pairs


def run_review_fusion_dag(
    *,
    run_input: dict[str, Any],
    candidates: list[dict[str, Any]],
    gemma_endpoint: str,
    qwen_endpoint: str,
    output_dir: Path,
) -> list[dict[str, Any]]:
    """Run R1 and R2 together, start R3 when R1 releases Gemma, then batch Fusion."""
    proof_rows: list[dict[str, Any]] = []
    for proof_index, candidate in enumerate(candidates):
        proof_rows.append(
            {
                "proof_index": proof_index,
                "problem_number": v067.problem_number_for_artifacts(run_input),
                "problem_id": run_input["problem_id"],
                "candidate_id": candidate["candidate_id"],
                "problem": run_input["problem"],
                "problem_sha256": v081.sha256_text(str(run_input["problem"])),
                "proof": candidate["proof"],
                "proof_path": candidate["proof_path"],
                "proof_sha256": candidate["proof_sha256"],
                "source_temperature": 0.4,
            }
        )

    reviewer_modules = {
        "reviewer_1": v067.reviewer_1,
        "reviewer_2": v067.reviewer_2,
        "reviewer_3": v067.reviewer_3,
    }

    def run_reviewer(reviewer_name: str) -> dict[str, dict[str, Any]]:
        module = reviewer_modules[reviewer_name]
        tasks = [
            v067.build_review_task(
                run_input=run_input,
                row=row,
                reviewer_name=reviewer_name,
                gemma_endpoint=gemma_endpoint,
                qwen_endpoint=qwen_endpoint,
            )
            for row in proof_rows
        ]
        results = v067._parallel_stage(
            output_dir=output_dir / "_batch_status" / reviewer_name,
            stage=reviewer_name,
            rows=tasks,
            identity=lambda row: str(row["candidate_id"]),
            worker=lambda task: module.run_task(
                output_dir=output_dir / reviewer_name, task=task
            ),
        )
        return {str(row["task"]["candidate_id"]): row for row in results}

    # R1/Gemma and R2/Qwen start together.  Once R1 releases GPU 0, R3/Gemma
    # begins even if the longer Qwen branch is still active.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as scheduler:
        reviewer_1_future = scheduler.submit(run_reviewer, "reviewer_1")
        reviewer_2_future = scheduler.submit(run_reviewer, "reviewer_2")
        reviewer_1 = reviewer_1_future.result()
        reviewer_3_future = scheduler.submit(run_reviewer, "reviewer_3")
        reviewer_2 = reviewer_2_future.result()
        reviewer_3 = reviewer_3_future.result()
    review_results = {
        "reviewer_1": reviewer_1,
        "reviewer_2": reviewer_2,
        "reviewer_3": reviewer_3,
    }

    fusion_tasks: list[dict[str, Any]] = []
    for row in proof_rows:
        candidate_id = str(row["candidate_id"])
        fusion_tasks.append(
            v067.build_fusion_task(
                run_input=run_input,
                row=row,
                reviews={
                    name: review_results[name][candidate_id]
                    for name in ("reviewer_1", "reviewer_2", "reviewer_3")
                },
                gemma_endpoint=gemma_endpoint,
            )
        )
    fusion_rows = v067._parallel_stage(
        output_dir=output_dir / "_batch_status" / "fusion",
        stage="fusion",
        rows=fusion_tasks,
        identity=lambda row: str(row["candidate_id"]),
        worker=lambda task: v067.fusion.run_task(
            output_dir=output_dir / "fusion_stage", task=task
        ),
    )
    fusion_results = {
        str(row["task"]["candidate_id"]): row for row in fusion_rows
    }
    source_by_id = {str(row["candidate_id"]): row for row in candidates}
    audited: list[dict[str, Any]] = []
    for proof_row in proof_rows:
        candidate_id = str(proof_row["candidate_id"])
        qwen_result = reviewer_2[candidate_id]
        fusion_result = fusion_results[candidate_id]
        audited.append(
            {
                **source_by_id[candidate_id],
                "qwen_defect_packet": v081._audit_packet(qwen_result),
                "fusion_defect_packet": v081._audit_packet(fusion_result),
                "qwen_final": qwen_result["final"],
                "fusion_final": fusion_result["final"],
                "qwen_outcome": qwen_result["parsed"]["outcome"],
                "fusion_outcome": fusion_result["parsed"]["outcome"],
                "review_outcomes": {
                    name: review_results[name][candidate_id]["parsed"]["outcome"]
                    for name in ("reviewer_1", "reviewer_2", "reviewer_3")
                },
            }
        )

    write_json(
        output_dir / "schedule.json",
        {
            "policy": "R1_Gemma_and_R2_Qwen_concurrent_then_R3_Gemma_then_Fusion_batch",
            "candidate_count": len(candidates),
            "review_batch_width": GEMMA_BATCH,
            "qwen_batch_width": QWEN_BATCH,
            "fusion_batch_width": GEMMA_BATCH,
        },
    )
    write_json(
        output_dir / "summary.json",
        {
            "candidate_count": len(audited),
            "reviewer_outcomes": {
                name: dict(
                    Counter(
                        str(row["parsed"]["outcome"])
                        for row in review_results[name].values()
                    )
                )
                for name in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "fusion_outcomes": dict(
                Counter(str(row["fusion_outcome"]) for row in audited)
            ),
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                    "review_outcomes": row["review_outcomes"],
                    "qwen_outcome": row["qwen_outcome"],
                    "fusion_outcome": row["fusion_outcome"],
                }
                for row in audited
            ],
        },
    )
    return audited


def _guided_structured_with_transport_waves(
    *,
    runtime: ResilientModelRuntime,
    role: str,
    prompt: str,
    destination: Path,
    stage: str,
    schema: dict[str, Any],
    temperature: float,
    max_tokens: int,
    seed_label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Use vLLM's explicit guided-JSON field with bounded fresh recovery."""
    failures: list[str] = []
    for wave in range(4):
        wave_stage = stage if wave == 0 else f"{stage}_guided_transport_w{wave}"
        wave_seed = seed_label if wave == 0 else f"{seed_label}:guided:{wave}"
        try:
            record, generation = runtime.structured(
                role=role,
                prompt=prompt,
                destination=destination,
                stage=wave_stage,
                schema=schema,
                temperature=temperature,
                max_tokens=max_tokens,
                seed_label=wave_seed,
                use_explicit_guided_json=True,
            )
            metadata = dict(generation["metadata"])
            metadata["v083_guided_decoding"] = {
                "request_field": "structured_outputs.json",
                "accepted_wave": wave,
                "prior_failures": failures,
                "schema_constrained": True,
            }
            return record, {**generation, "metadata": metadata}
        except RuntimeError as error:
            failures.append(f"wave_{wave}: {error}")
    raise RuntimeError(
        f"v0.3.83 guided structured transport exhausted for {stage}: {failures}"
    )


def run_dynamic_literal_audit_resilient(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    proof: str,
    candidate_id: str,
    attempt: int,
    output_dir: Path,
) -> dict[str, Any]:
    """Retry only malformed non-literal anchor extraction; never weaken binding."""
    destination = output_dir / f"attempt_{attempt}"
    anchor_attempts: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    anchor_bindings: list[dict[str, Any]] = []
    extraction_errors: list[str] = []
    binding_warnings: list[str] = []
    rejected_anchors: list[dict[str, Any]] = []
    target_anchor_count: int | None = None
    accepted_by_span: dict[
        tuple[int, int], tuple[dict[str, Any], dict[str, Any]]
    ] = {}
    accepted_generation: dict[str, Any] | None = None
    base_prompt = prioritized_audit_anchor_extraction_prompt(
        problem=problem, proof=proof
    )
    for wave in (0, 1):
        retry_directive = ""
        if wave:
            retry_directive = f"""

EXACT-QUOTE TRANSPORT RETRY
The preceding anchor record failed deterministic source binding:
{extraction_errors}

Return replacements only for the rejected records below, in the same order. Do not
repeat records whose quotes already bound successfully.

REJECTED RECORDS:
{json.dumps(rejected_anchors, ensure_ascii=False, indent=2)}

Every replacement exact_quote must be copied as a
contiguous byte-for-byte substring of COMPLETE PROOF, including its original LaTeX
delimiters, backslashes, spacing, and punctuation. Do not replace LaTeX with Unicode,
remove dollar signs, normalize whitespace, or insert ellipses. Shorten a quote if
necessary, but do not paraphrase it.
"""
        wave_schema = copy.deepcopy(V083_AUDIT_ANCHOR_SCHEMA)
        if wave:
            wave_schema["properties"]["anchors"]["minItems"] = 1
            wave_schema["properties"]["anchors"]["maxItems"] = max(
                len(rejected_anchors), 1
            )
        record, generation = _guided_structured_with_transport_waves(
            runtime=runtime,
            role="gemma",
            prompt=base_prompt + retry_directive,
            destination=destination / f"01_anchor_extraction_wave_{wave}",
            stage=f"audit_anchors_{wave}",
            schema=wave_schema,
            temperature=0.1,
            max_tokens=8_192,
            seed_label=f"v083:literal:{candidate_id}:{attempt}:anchors:{wave}",
        )
        raw_anchors = list(record["anchors"])
        if target_anchor_count is None:
            target_anchor_count = len(raw_anchors)
        aligned_wave, wave_errors, wave_bindings = (
            validate_prioritized_anchor_records(proof, raw_anchors)
        )
        rejected_anchors = []
        for raw_anchor, aligned_anchor, binding in zip(
            raw_anchors, aligned_wave, wave_bindings, strict=True
        ):
            if binding["mode"] == "FAILED":
                rejected_anchors.append(raw_anchor)
                continue
            span = (int(binding["source_start"]), int(binding["source_end"]))
            accepted_by_span.setdefault(span, (aligned_anchor, binding))
        ordered = sorted(
            accepted_by_span.values(),
            key=lambda item: (
                int(item[1]["source_start"]),
                int(item[1]["source_end"]),
            ),
        )[:target_anchor_count]
        anchors = [item[0] for item in ordered]
        anchor_bindings = [
            {**item[1], "anchor_id": f"A{index}"}
            for index, item in enumerate(ordered, start=1)
        ]
        unresolved_count = max(target_anchor_count - len(anchors), 0)
        extraction_errors = []
        if unresolved_count:
            extraction_errors = [
                f"unresolved_source_bound_anchors:{unresolved_count}"
            ] + wave_errors
        anchor_attempts.append(
            {
                "wave": wave,
                "returned_anchor_count": len(raw_anchors),
                "accepted_total_after_wave": len(anchors),
                "target_anchor_count": target_anchor_count,
                "deterministic_errors": wave_errors,
                "bindings": wave_bindings,
                "generation": generation["metadata"],
            }
        )
        accepted_generation = generation["metadata"]
        if not extraction_errors:
            break

    if extraction_errors and len(anchors) >= MIN_BOUND_DYNAMIC_LITERAL_ANCHORS:
        binding_warnings = list(extraction_errors)
        extraction_errors = []

    if extraction_errors:
        literal = {
            "verdict": "LITERAL_FAILURE",
            "earliest_failed_anchor_id": "ANCHOR_EXTRACTION_INVALID",
            "exact_location": "dynamic audit-anchor extraction",
            "failed_obligation": (
                "Every exact_quote must bind uniquely to unchanged source content."
            ),
            "verification": " | ".join(extraction_errors),
        }
        literal_generation: dict[str, Any] = {
            "source": "deterministic_exact_or_canonical_binding_after_retry"
        }
    else:
        # The extractor emits only the user-selected mathematical fields.  Add
        # ephemeral deterministic labels solely so Qwen can name the earliest
        # failing anchor in its existing response contract.
        labeled_anchors = [
            {"anchor_id": f"A{index}", **anchor}
            for index, anchor in enumerate(anchors, start=1)
        ]
        literal, generation = _guided_structured_with_transport_waves(
            runtime=runtime,
            role="qwen",
            prompt=literal_anchor_audit_prompt(
                problem=problem, proof=proof, anchors=labeled_anchors
            ),
            destination=destination / "02_literal_verification",
            stage="literal_audit",
            schema=LITERAL_AUDIT_SCHEMA,
            temperature=0.1,
            max_tokens=16_384,
            seed_label=f"v083:literal:{candidate_id}:{attempt}:verify",
        )
        literal_generation = generation["metadata"]
    result = {
        "proof_sha256": v081.sha256_text(proof),
        "anchors": anchors,
        "anchor_bindings": anchor_bindings,
        "anchor_extraction_errors": extraction_errors,
        "anchor_binding_warnings": binding_warnings,
        "minimum_bound_anchor_count": MIN_BOUND_DYNAMIC_LITERAL_ANCHORS,
        "anchor_extraction_attempts": anchor_attempts,
        "audit_status": (
            "AUDIT_UNAVAILABLE" if extraction_errors else "COMPLETED"
        ),
        "eligible_for_defect_routing": not extraction_errors,
        "literal_audit": literal,
        "literal_pass": literal["verdict"] == "PASS" and not extraction_errors,
        "anchor_generation": accepted_generation,
        "literal_generation": literal_generation,
    }
    write_json(destination / "result.json", result)
    return result


def attach_dynamic_literal_audits_resilient(
    *,
    runtime: ResilientModelRuntime,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
) -> list[dict[str, Any]]:
    def audit(source: dict[str, Any]) -> dict[str, Any]:
        row = copy.deepcopy(source)
        row["dynamic_literal_audit"] = run_dynamic_literal_audit_resilient(
            runtime=runtime,
            problem=problem,
            proof=str(row["proof"]),
            candidate_id=str(row["candidate_id"]),
            attempt=0,
            output_dir=output_dir / v081._safe_component(str(row["candidate_id"])),
        )
        return row

    rows = _parallel_map(audit, candidates, max_workers=SYNTHESIS_BATCH)
    write_json(
        output_dir / "summary.json",
        {
            "candidate_count": len(rows),
            "literal_pass_count": sum(
                bool(row["dynamic_literal_audit"]["literal_pass"]) for row in rows
            ),
            "proof_hash_bound_anchors": True,
            "anchor_exact_quote_retry_limit": 1,
            "static_problem_specific_checklist": False,
        },
    )
    return rows


def run_certification_and_memory_batched(
    *,
    proof_runtime: ResilientModelRuntime,
    verifier_runtime: ResilientModelRuntime,
    runtime_config: RuntimeConfig,
    salvage_verifier_endpoint: str,
    problem: str,
    candidate_proofs: list[dict[str, Any]],
    accepted_hypotheses: list[dict[str, Any]],
    certified_memory: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """v0.3.81 certification with batched negation-validation waves."""
    pairs = validate_and_repair_negations_batched(
        runtime=proof_runtime,
        problem=problem,
        hypotheses={
            "hypotheses": [
                {
                    key: row[key]
                    for key in (
                        "conjecture",
                        "exact_negation",
                        "earliest_unresolved_transition",
                        "local_dependency_map",
                    )
                }
                for row in accepted_hypotheses
            ]
        },
        arm=f"iteration_{iteration}",
        round_number=iteration,
        output_dir=output_dir / "negation_validation",
    )
    initial_verified, initial_unresolved = prove_pairs(
        runtime=proof_runtime,
        verifier_runtime=verifier_runtime,
        problem=problem,
        pairs=pairs,
        output_dir=output_dir / "initial_lemma_proving",
    )
    failure_cards: list[dict[str, Any]] = []
    failed_additions: list[dict[str, Any]] = []
    for pair in pairs:
        pair_dir = output_dir / "initial_lemma_proving" / pair["claim_id"]
        wrapper = v081.failure_card_for_pair(
            pair=pair,
            positive=read_json(pair_dir / "positive" / "result.json"),
            negative=read_json(pair_dir / "negative" / "result.json"),
            source_arm=f"iteration_{iteration}",
            round_number=iteration,
        )
        if wrapper is not None:
            failure_cards.append(wrapper)
            failed_additions.append(
                v081._failed_record_from_card(
                    card=wrapper, pair=pair, iteration=iteration
                )
            )

    memory_after_initial, initial_insert_audit = v081.extend_shared_verified_exact(
        existing_verified=certified_memory,
        salvage_verified=initial_verified,
        output_dir=output_dir / "initial_exact_memory_insertion",
    )
    salvage = v081.run_failure_guided_salvage_resilient(
        runtime=proof_runtime,
        verifier_runtime=verifier_runtime,
        problem=problem,
        candidate_proofs=[
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof": row["proof"],
            }
            for row in candidate_proofs
        ],
        failure_cards=failure_cards,
        output_dir=output_dir / "failure_guided_salvage",
        limit=len(failure_cards),
    )
    memory_after_salvage, salvage_insert_audit = v081.extend_shared_verified_exact(
        existing_verified=memory_after_initial,
        salvage_verified=list(salvage["verified"]),
        output_dir=output_dir / "salvage_exact_memory_insertion",
    )
    write_json(
        output_dir / "shared_lemma_memory.json",
        {
            "verified": memory_after_salvage,
            "unresolved": initial_unresolved + salvage["unresolved"],
        },
    )
    iteration_input = {
        "problem_id": "iterative_problem",
        "problem": problem,
        "candidate_proofs": [
            {
                "candidate_id": row["candidate_id"],
                "role": row["role"],
                "proof": row["proof"],
            }
            for row in candidate_proofs
        ],
    }
    input_path = output_dir / "iteration_input.json"
    write_json(input_path, iteration_input)
    retry = run_atomic_retry(
        source_run_dir=output_dir,
        input_path=input_path,
        output_dir=output_dir / "atomic_child_retry",
        runtime_config=runtime_config,
        salvage_verifier_endpoint=salvage_verifier_endpoint,
    )
    final_memory_payload = read_json(
        output_dir / "atomic_child_retry" / "augmented_shared_lemma_memory.json"
    )
    final_certified = list(final_memory_payload["verified"])

    salvage_verified = {row["lemma_id"]: row for row in salvage["verified"]}
    salvage_unresolved = {row["claim_id"]: row for row in salvage["unresolved"]}
    for claim_id, provenance in salvage["provenance"].items():
        case = next(
            row
            for row in salvage["cases"]
            if row["case_name"] == provenance["case_name"]
        )
        index_match = re.search(r"_H([1-9][0-9]*)$", claim_id)
        if index_match is None:
            continue
        hypothesis = case["record"]["hypotheses"][int(index_match.group(1)) - 1]
        verified_row = salvage_verified.get(claim_id)
        if verified_row is not None and verified_row["direction"] == "positive":
            continue
        unresolved = salvage_unresolved.get(claim_id)
        status = (
            "REFUTED"
            if verified_row is not None
            else "VERIFIER_CONFLICT"
            if unresolved and unresolved["status"] == "logical_conflict"
            else "PROOF_FAILED"
        )
        failed_additions.append(
            {
                "failed_id": f"I{iteration}:SALVAGE:{claim_id}",
                "iteration": iteration,
                "source_claim_id": claim_id,
                "status": status,
                "hypothesis": str(hypothesis["statement"]),
                "exact_negation": str(hypothesis["exact_negation"]),
                "earliest_unresolved_transition": str(
                    hypothesis["earliest_unresolved_transition"]
                ),
                "local_dependency_map": str(hypothesis["local_dependency_map"]),
                "decisive_failure": str(unresolved or status),
                "parent_failed_id": f"I{iteration}:{provenance['source_claim_id']}",
                "resolved_by_certification": False,
            }
        )

    final_failed, failed_insert_audit = v081._insert_failed_exact(
        failed_memory, failed_additions
    )
    certified_statements = {
        v081.normalized(str(row["statement"])) for row in final_certified
    }
    for row in final_failed:
        if v081.normalized(str(row["hypothesis"])) in certified_statements:
            row["resolved_by_certification"] = True
            row["resolved_iteration"] = iteration
    summary = {
        "accepted_hypothesis_count": len(accepted_hypotheses),
        "pair_count": len(pairs),
        "initial_verified_count": len(initial_verified),
        "initial_unresolved_count": len(initial_unresolved),
        "salvage_failure_count": len(failure_cards),
        "salvage_generated_count": salvage["generated_hypothesis_count"],
        "salvage_verified_count": len(salvage["verified"]),
        "retry_verified_count": retry["verified_count"],
        "certified_memory_count": len(final_certified),
        "failed_memory_count": len(final_failed),
        "initial_insert_audit": initial_insert_audit,
        "salvage_insert_audit": salvage_insert_audit,
        "failed_insert_audit": failed_insert_audit,
        "batched_negation_validation": True,
        "proof_side_outer_batch": PROOF_SIDE_BATCH,
    }
    write_json(output_dir / "certification_summary.json", summary)
    write_json(output_dir / "certified_memory.json", {"verified": final_certified})
    write_json(output_dir / "failed_memory.json", {"failed": final_failed})
    return final_certified, final_failed, summary


def run_contextual_memory_feedback_batched(
    *,
    runtime: ResilientModelRuntime,
    problem_id: str,
    problem: str,
    candidates: list[dict[str, Any]],
    context_certified: list[dict[str, Any]],
    provisional: list[dict[str, Any]],
    failed_memory: list[dict[str, Any]],
    iteration: int,
    output_dir: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    """Batch step 9 repair waves and step 10 disposition proposals."""
    memory = v082.combined_memory(context_certified, provisional)
    tainted, challenges, quarantined_by_label, attribution = (
        v082.run_attribution_and_quarantine(
            runtime=runtime,
            problem=problem,
            candidates=candidates,
            memory=memory,
            iteration=iteration,
            output_dir=output_dir / "01_attribution_and_quarantine",
        )
    )
    memory_by_id = {str(row["lemma_id"]): row for row in memory}
    states: dict[str, dict[str, Any]] = {}
    completed: dict[str, dict[str, Any]] = {}
    repairable: list[dict[str, Any]] = []
    for source in tainted:
        candidate_id = str(source["candidate_id"])
        if not v082.candidate_requires_contextual_repair(source):
            completed[candidate_id] = {
                **copy.deepcopy(source),
                "contextual_repair_status": "NOT_REQUIRED",
            }
            continue
        implicated, replay = v082._candidate_implicated_lemmas(
            candidate=source,
            memory_by_id=memory_by_id,
            challenges_by_lemma=challenges,
        )
        qwen_packet, fusion_packet = v082._separate_feedback_packets(source)
        state = {
            "candidate": source,
            "implicated": implicated,
            "replay": replay,
            "qwen_packet": qwen_packet,
            "fusion_packet": fusion_packet,
            "attempts": [],
            "prior_feedback": None,
        }
        states[candidate_id] = state
        repairable.append(state)

    def specify(state: dict[str, Any]) -> dict[str, Any]:
        candidate = state["candidate"]
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir
            / "02_contextual_full_proof_repair"
            / v081._safe_component(candidate_id)
            / "01_qwen_repair_specification"
        )
        record, generation = v081._structured_with_v081_transport_waves(
            runtime=runtime,
            role="qwen",
            prompt=qwen_repair_spec_prompt(
                problem=problem,
                proof=str(candidate["proof"]),
                implicated_lemmas=state["implicated"],
                qwen_packet=state["qwen_packet"],
                fusion_packet=state["fusion_packet"],
                body_replay_records=state["replay"],
            ),
            destination=destination,
            stage="repair_specification",
            schema=QWEN_REPAIR_SPEC_SCHEMA,
            temperature=0.1,
            max_tokens=16_384,
            seed_label=f"v083:i{iteration}:context_spec:{candidate_id}",
        )
        state["repair_spec"] = record
        state["repair_spec_generation"] = generation["metadata"]
        return state

    repairable = _parallel_map(specify, repairable, max_workers=QWEN_BATCH)
    active: list[dict[str, Any]] = []
    for state in repairable:
        candidate = state["candidate"]
        candidate_id = str(candidate["candidate_id"])
        if state["repair_spec"]["lemma_interface_action"] == "NO_SUPPORTED_REPAIR":
            completed[candidate_id] = {
                **candidate,
                "contextual_repair_status": "NO_SUPPORTED_REPAIR",
                "contextual_repair_specification": state["repair_spec"],
                "contextual_repair_specification_generation": state[
                    "repair_spec_generation"
                ],
                "contextual_repair_attempts": [],
                "contextual_repair_implicated_lemma_ids": [
                    str(row["lemma_id"]) for row in state["implicated"]
                ],
            }
        else:
            active.append(state)

    context_rows = [
        row for row in memory if row.get("memory_tier") == "context_certified"
    ]
    provisional_rows = [
        row for row in memory if row.get("memory_tier") == "provisional"
    ]
    for attempt in range(1, MAX_CONTEXTUAL_REWRITES + 1):
        if not active:
            break
        attempt_root = output_dir / "02_contextual_full_proof_repair" / f"attempt_{attempt}"

        def rewrite(state: dict[str, Any]) -> dict[str, Any]:
            candidate = state["candidate"]
            candidate_id = str(candidate["candidate_id"])
            destination = attempt_root / "candidates" / v081._safe_component(candidate_id)
            generated = runtime.text(
                role="gemma",
                prompt=contextual_rewrite_prompt(
                    problem=problem,
                    proof=str(candidate["proof"]),
                    implicated_lemmas=state["implicated"],
                    repair_spec=state["repair_spec"],
                    qwen_packet=state["qwen_packet"],
                    fusion_packet=state["fusion_packet"],
                    prior_attempt_feedback=state["prior_feedback"],
                ),
                destination=destination / "generation",
                stage="complete_replacement_proof",
                temperature=0.4,
                max_tokens=32_768,
                seed_label=(
                    f"v083:i{iteration}:context_rewrite:{candidate_id}:{attempt}"
                ),
            )
            proof = str(generated["text"]).strip()
            proof_path = destination / "complete_replacement_proof.md"
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            proof_path.write_text(proof + "\n", encoding="utf-8")
            replacement = v082._rewrite_candidate_record(
                source=candidate,
                proof=proof,
                proof_path=proof_path,
                generation=generated["metadata"],
                attempt=attempt,
            )
            replacement = v082.rebind_memory_dependencies(
                candidates=[replacement],
                context_certified=context_rows,
                provisional=provisional_rows,
            )[0]
            return {"state": state, "replacement": replacement}

        rewritten = _parallel_map(rewrite, active, max_workers=GEMMA_BATCH)
        replacements = [row["replacement"] for row in rewritten]
        audited = run_review_fusion_dag(
            run_input={"problem_id": problem_id, "problem": problem},
            candidates=replacements,
            gemma_endpoint=runtime.config.gemma_endpoint,
            qwen_endpoint=runtime.config.qwen_endpoint,
            output_dir=attempt_root / "03_full_proof_review_fusion",
        )
        literal_audited = attach_dynamic_literal_audits_resilient(
            runtime=runtime,
            problem=problem,
            candidates=audited,
            output_dir=attempt_root / "04_dynamic_literal_gate",
        )
        audited_by_id = {
            str(row["candidate_id"]): row for row in literal_audited
        }
        next_active: list[dict[str, Any]] = []
        for state in active:
            candidate_id = str(state["candidate"]["candidate_id"])
            audited_candidate = audited_by_id[candidate_id]
            literal = audited_candidate["dynamic_literal_audit"]
            reviewer_pass = v082.strict_whole_proof_pass(audited_candidate)
            full_pass = reviewer_pass and bool(literal["literal_pass"])
            attempt_record = {
                "attempt": attempt,
                "proof_path": audited_candidate["proof_path"],
                "proof_sha256": audited_candidate["proof_sha256"],
                "review_outcomes": audited_candidate["review_outcomes"],
                "qwen_outcome": audited_candidate["qwen_outcome"],
                "fusion_outcome": audited_candidate["fusion_outcome"],
                "reviewer_fusion_pass": reviewer_pass,
                "literal_pass": literal["literal_pass"],
                "literal_audit_status": literal.get("audit_status", "COMPLETED"),
                "accepted": full_pass,
            }
            state["attempts"].append(attempt_record)
            if full_pass:
                result = {
                    **audited_candidate,
                    "contextual_repair_status": "ACCEPTED",
                    "contextual_repair_specification": state["repair_spec"],
                    "contextual_repair_specification_generation": state[
                        "repair_spec_generation"
                    ],
                    "contextual_repair_attempts": state["attempts"],
                    "contextual_repair_implicated_lemma_ids": [
                        str(row["lemma_id"]) for row in state["implicated"]
                    ],
                }
                if result.get("memory_invalidation"):
                    result["resolved_memory_invalidation"] = result.pop(
                        "memory_invalidation"
                    )
                completed[candidate_id] = result
            elif (
                reviewer_pass
                and str(literal.get("audit_status") or "COMPLETED")
                == "AUDIT_UNAVAILABLE"
            ):
                completed[candidate_id] = {
                    **audited_candidate,
                    "contextual_repair_status": "AUDIT_UNAVAILABLE",
                    "contextual_repair_specification": state["repair_spec"],
                    "contextual_repair_specification_generation": state[
                        "repair_spec_generation"
                    ],
                    "contextual_repair_attempts": state["attempts"],
                    "contextual_repair_implicated_lemma_ids": [
                        str(row["lemma_id"]) for row in state["implicated"]
                    ],
                }
            else:
                state["prior_feedback"] = {
                    "reviewer_2_qwen": audited_candidate["qwen_defect_packet"],
                    "fusion": audited_candidate["fusion_defect_packet"],
                    "dynamic_literal": (
                        literal["literal_audit"]
                        if str(literal.get("audit_status") or "COMPLETED")
                        == "COMPLETED"
                        else {}
                    ),
                }
                next_active.append(state)
        active = next_active

    for state in active:
        candidate = state["candidate"]
        candidate_id = str(candidate["candidate_id"])
        completed[candidate_id] = {
            **candidate,
            "contextual_repair_status": "FAILED",
            "contextual_repair_specification": state["repair_spec"],
            "contextual_repair_specification_generation": state[
                "repair_spec_generation"
            ],
            "contextual_repair_attempts": state["attempts"],
            "contextual_repair_implicated_lemma_ids": [
                str(row["lemma_id"]) for row in state["implicated"]
            ],
        }

    repaired_candidates = [completed[str(row["candidate_id"])] for row in tainted]
    for row in repaired_candidates:
        destination = (
            output_dir
            / "02_contextual_full_proof_repair"
            / v081._safe_component(str(row["candidate_id"]))
        )
        write_json(destination / "result.json", row)

    quarantined_ids = {str(row["lemma_id"]) for row in quarantined_by_label.values()}
    disposition_jobs: list[dict[str, Any]] = []
    for order, candidate in enumerate(repaired_candidates):
        if candidate.get("contextual_repair_status") != "ACCEPTED":
            continue
        implicated_ids = {
            str(value)
            for value in candidate.get("contextual_repair_implicated_lemma_ids", [])
        }.intersection(quarantined_ids)
        if implicated_ids:
            disposition_jobs.append(
                {
                    "order": order,
                    "candidate": candidate,
                    "implicated_ids": implicated_ids,
                }
            )

    def propose_disposition(job: dict[str, Any]) -> dict[str, Any]:
        candidate = job["candidate"]
        candidate_id = str(candidate["candidate_id"])
        destination = (
            output_dir / "03_atomic_memory_disposition" / v081._safe_component(candidate_id)
        )
        disposition, generation = v081._structured_with_v081_transport_waves(
            runtime=runtime,
            role="qwen",
            prompt=memory_disposition_prompt(
                proof=str(candidate["proof"]),
                quarantined_lemmas=[
                    {
                        "lemma_id": lemma_id,
                        "statement": memory_by_id[lemma_id]["statement"],
                        "earliest_unresolved_transition": memory_by_id[lemma_id][
                            "earliest_unresolved_transition"
                        ],
                        "local_dependency_map": memory_by_id[lemma_id][
                            "local_dependency_map"
                        ],
                    }
                    for lemma_id in sorted(job["implicated_ids"])
                ],
            ),
            destination=destination,
            stage="exact_memory_disposition",
            schema=MEMORY_DISPOSITION_SCHEMA,
            temperature=0.1,
            max_tokens=8_192,
            seed_label=f"v083:i{iteration}:memory_disposition:{candidate_id}",
        )
        return {**job, "disposition": disposition, "generation": generation["metadata"]}

    proposals = _parallel_map(
        propose_disposition, disposition_jobs, max_workers=QWEN_BATCH
    )
    proposals.sort(key=lambda row: int(row["order"]))
    accepted_revisions: list[dict[str, Any]] = []
    disposition_audit: list[dict[str, Any]] = []
    claimed_supersessions: set[str] = set()
    for proposal in proposals:
        candidate = proposal["candidate"]
        candidate_id = str(candidate["candidate_id"])
        disposition = proposal["disposition"]
        implicated_ids = proposal["implicated_ids"]
        errors = v082.validate_memory_disposition(
            disposition=disposition,
            proof=str(candidate["proof"]),
            quarantined_ids=implicated_ids,
        )
        requested = {
            str(value) for value in disposition.get("supersedes_lemma_ids", [])
        }
        if requested.intersection(claimed_supersessions):
            errors.append("supersession_already_claimed_by_prior_accepted_revision")
        accepted = (
            disposition["decision"] == "EXACT_SELF_CONTAINED_REVISION" and not errors
        )
        audit_row = {
            "candidate_id": candidate_id,
            "proof_sha256": candidate["proof_sha256"],
            "disposition": disposition,
            "deterministic_errors": errors,
            "accepted_into_context_memory": accepted,
            "generation": proposal["generation"],
        }
        disposition_audit.append(audit_row)
        destination = (
            output_dir / "03_atomic_memory_disposition" / v081._safe_component(candidate_id)
        )
        write_json(destination / "result.json", audit_row)
        if not accepted:
            continue
        statement = str(disposition["statement_exact_quote"])
        lemma_proof = str(disposition["proof_exact_quote"])
        digest = v081.sha256_text(statement + "\n\n" + lemma_proof)[:16]
        accepted_revisions.append(
            {
                "lemma_id": f"CTX_I{iteration}_{digest}",
                "statement": statement,
                "proof": lemma_proof,
                "earliest_unresolved_transition": str(
                    disposition["earliest_unresolved_transition"]
                ),
                "local_dependency_map": str(disposition["local_dependency_map"]),
                "direction": "positive",
                "context_certified": True,
                "source_candidate_id": candidate_id,
                "source_full_proof_sha256": str(candidate["proof_sha256"]),
                "supersedes_lemma_ids": sorted(requested),
                "memory_revision_iteration": iteration,
                "self_containment_reason": str(
                    disposition["self_containment_reason"]
                ),
            }
        )
        claimed_supersessions.update(requested)

    new_context, new_provisional, new_failed, transaction = (
        v082.commit_contextual_memory_transaction(
            context_certified=context_certified,
            provisional=provisional,
            failed_memory=failed_memory,
            quarantined_ids=quarantined_ids,
            challenges_by_lemma=challenges,
            accepted_revisions=accepted_revisions,
            iteration=iteration,
        )
    )
    summary = {
        "attribution": attribution,
        "contextual_repair_outcomes": dict(
            Counter(
                str(row.get("contextual_repair_status"))
                for row in repaired_candidates
            )
        ),
        "contextual_rewrite_limit": MAX_CONTEXTUAL_REWRITES,
        "repair_specifications_batched": True,
        "rewrite_attempts_batched_by_round": True,
        "fresh_review_dag_per_attempt_batch": True,
        "memory_disposition_proposals_batched": True,
        "memory_disposition_commit_serial": True,
        "memory_dispositions": disposition_audit,
        "transaction": transaction,
        "accepted_proof_without_reusable_lemma_is_allowed": True,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "04_memory_snapshot.json",
        {
            "context_certified": new_context,
            "provisional": new_provisional,
            "failed": new_failed,
        },
    )
    return new_context, new_provisional, new_failed, repaired_candidates, summary
