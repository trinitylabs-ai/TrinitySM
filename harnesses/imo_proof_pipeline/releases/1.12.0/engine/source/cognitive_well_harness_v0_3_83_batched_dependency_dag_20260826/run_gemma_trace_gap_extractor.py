from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    sha256_text,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    RuntimeConfig,
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)

from . import HARNESS_VERSION


TRACE_GAP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "original_verdict",
        "gaps",
        "trace_final_consistency",
        "summary",
    ],
    "properties": {
        "original_verdict": {
            "type": "string",
            "enum": ["FIRST_BREAK", "NO_FIRST_BREAK"],
        },
        "gaps": {
            "type": "array",
            "minItems": 0,
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "proof_location",
                    "claim",
                    "trace_evidence",
                    "missing_detail",
                    "later_trace_disposition",
                    "support_origin",
                    "recoverability",
                    "dependency_impact",
                    "report_even_if_final_pass",
                ],
                "properties": {
                    "proof_location": {"type": "string", "minLength": 1},
                    "claim": {"type": "string", "minLength": 1},
                    "trace_evidence": {"type": "string", "minLength": 1},
                    "missing_detail": {"type": "string", "minLength": 1},
                    "later_trace_disposition": {"type": "string", "minLength": 1},
                    "support_origin": {
                        "type": "string",
                        "enum": [
                            "CANDIDATE_EXPLICIT",
                            "ROUTINE_ELABORATION",
                            "REVIEWER_ADDED",
                            "UNRESOLVED",
                        ],
                    },
                    "recoverability": {
                        "type": "string",
                        "enum": [
                            "OBVIOUS",
                            "STANDARD_DIRECT",
                            "LOCAL_NONTRIVIAL",
                            "NEW_IDEA",
                            "UNKNOWN",
                        ],
                    },
                    "dependency_impact": {
                        "type": "string",
                        "enum": ["COSMETIC", "LOCAL", "LOAD_BEARING", "UNKNOWN"],
                    },
                    "report_even_if_final_pass": {"type": "boolean"},
                },
            },
        },
        "trace_final_consistency": {
            "type": "string",
            "enum": ["CONSISTENT", "GAP_SUPPRESSED_BY_FINAL", "NO_GAP_FOUND"],
        },
        "summary": {"type": "string", "minLength": 1},
    },
}


COMPACT_TRACE_GAP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["gaps", "summary"],
    "properties": {
        "gaps": {
            "type": "array",
            "minItems": 0,
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "proof_line_id",
                    "trace_line_id",
                    "claim",
                    "missing_detail",
                    "later_trace_disposition",
                    "support_origin",
                    "recoverability",
                    "dependency_impact",
                    "report_even_if_final_pass",
                ],
                "properties": {
                    "proof_line_id": {"type": "string", "pattern": "^P[0-9]{4}$"},
                    "trace_line_id": {"type": "string", "pattern": "^T[0-9]{4}$"},
                    "claim": {"type": "string", "minLength": 1},
                    "missing_detail": {"type": "string", "minLength": 1},
                    "later_trace_disposition": {"type": "string", "minLength": 1},
                    "support_origin": {
                        "type": "string",
                        "enum": [
                            "CANDIDATE_EXPLICIT",
                            "ROUTINE_ELABORATION",
                            "REVIEWER_ADDED",
                            "UNRESOLVED",
                        ],
                    },
                    "recoverability": {
                        "type": "string",
                        "enum": [
                            "OBVIOUS",
                            "STANDARD_DIRECT",
                            "LOCAL_NONTRIVIAL",
                            "NEW_IDEA",
                            "UNKNOWN",
                        ],
                    },
                    "dependency_impact": {
                        "type": "string",
                        "enum": ["COSMETIC", "LOCAL", "LOAD_BEARING", "UNKNOWN"],
                    },
                    "report_even_if_final_pass": {"type": "boolean"},
                },
            },
        },
        "summary": {"type": "string", "minLength": 1},
    },
}


TRACE_GAP_SYSTEM_PROMPT = r"""You are a forensic extractor for a mathematical
proof-review reasoning trace. Do not re-grade or repair the submitted proof. Extract
every missing justification, unsupported transition, explicit doubt, or incomplete
argument that the reviewer noticed anywhere in its private reasoning, regardless of
the reviewer's final verdict.

Search the full trace, including passages later followed by words such as "correct",
"solid", "standard", or "brief". A later reviewer-created derivation does not erase
the earlier omission. Record who supplied the eventual support:

- CANDIDATE_EXPLICIT: the submitted proof itself later supplies the missing link.
- ROUTINE_ELABORATION: only immediate algebra or a directly invoked standard fact was
  expanded; no new multi-step support was introduced.
- REVIEWER_ADDED: the trace introduces a construction, sequence, lemma, iteration,
  limit, case argument, or other multi-step justification absent from the proof.
- UNRESOLVED: the trace never establishes the missing link.

For each gap, `proof_location` must be a literal contiguous substring of the submitted
proof, and `trace_evidence` must be a literal contiguous substring of the raw reasoning
trace. Do not paraphrase either field. `later_trace_disposition` should explain whether
the trace repaired, dismissed, or retained the concern. Set `report_even_if_final_pass`
to true for REVIEWER_ADDED or UNRESOLVED support.

If at least one reportable gap exists but the original verdict is NO_FIRST_BREAK, set
trace_final_consistency to GAP_SUPPRESSED_BY_FINAL. Return only the schema-conforming
JSON object."""


def trace_gap_user_prompt(
    *, problem: str, proof: str, reasoning: str, reviewer_final: str
) -> str:
    values = tuple(
        value.strip() for value in (problem, proof, reasoning, reviewer_final)
    )
    if not all(values):
        raise ValueError("problem, proof, reasoning, and reviewer final must be nonempty")
    return (
        "# FORENSIC TRACE INPUT\n\n"
        "## PROBLEM\n"
        + values[0]
        + "\n\n## SUBMITTED PROOF\n"
        + values[1]
        + "\n\n## REVIEWER 1 RAW REASONING TRACE\n"
        + values[2]
        + "\n\n## REVIEWER 1 FINAL VERDICT\n"
        + values[3]
        + "\n"
    )


def indexed_nonempty_lines(value: str, prefix: str) -> tuple[str, dict[str, str]]:
    if len(prefix) != 1 or not prefix.isalpha():
        raise ValueError("line prefix must be one alphabetic character")
    records: dict[str, str] = {}
    rendered: list[str] = []
    for line_number, line in enumerate(value.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        line_id = f"{prefix.upper()}{line_number:04d}"
        records[line_id] = text
        rendered.append(f"[{line_id}] {text}")
    if not records:
        raise ValueError("cannot index an empty source")
    return "\n".join(rendered), records


def compact_trace_gap_user_prompt(
    *, problem: str, proof: str, reasoning: str, reviewer_final: str
) -> tuple[str, dict[str, str], dict[str, str]]:
    indexed_proof, proof_lines = indexed_nonempty_lines(proof, "P")
    indexed_trace, trace_lines = indexed_nonempty_lines(reasoning, "T")
    prompt = (
        "# COMPACT FORENSIC RETRY AFTER SERIALIZATION FAILURE\n\n"
        "The original forensic request remains unchanged. Its mathematical analysis "
        "completed, but its JSON finalization failed. Return compact records using only "
        "the immutable source-line IDs below. Do not copy source text into the JSON. "
        "A later reviewer-created derivation does not erase an earlier omission. Any "
        "new construction, sequence, iteration, lemma, or case argument introduced by "
        "the reviewer rather than the candidate is REVIEWER_ADDED and must be reported "
        "even when the final verdict passes. Merely writing out direct algebra or a "
        "standard limit is ROUTINE_ELABORATION, even if it takes several displayed "
        "lines. Dependency impact is separate from repair difficulty: use LOAD_BEARING "
        "whenever the downstream conclusion relies on the claim.\n\n"
        "## PROBLEM\n"
        + problem.strip()
        + "\n\n## INDEXED SUBMITTED PROOF\n"
        + indexed_proof
        + "\n\n## INDEXED REVIEWER 1 RAW REASONING TRACE\n"
        + indexed_trace
        + "\n\n## REVIEWER 1 FINAL VERDICT\n"
        + reviewer_final.strip()
        + "\n"
    )
    return prompt, proof_lines, trace_lines


def materialize_compact_record(
    *,
    compact: dict[str, Any],
    proof_lines: dict[str, str],
    trace_lines: dict[str, str],
    reviewer_final: str,
) -> dict[str, Any]:
    gaps: list[dict[str, Any]] = []
    for index, gap in enumerate(compact["gaps"], start=1):
        proof_id = str(gap["proof_line_id"])
        trace_id = str(gap["trace_line_id"])
        if proof_id not in proof_lines:
            raise ValueError(f"compact gap {index} has an unknown proof line id")
        if trace_id not in trace_lines:
            raise ValueError(f"compact gap {index} has an unknown trace line id")
        gaps.append(
            {
                "proof_location": proof_lines[proof_id],
                "claim": gap["claim"],
                "trace_evidence": trace_lines[trace_id],
                "missing_detail": gap["missing_detail"],
                "later_trace_disposition": gap["later_trace_disposition"],
                "support_origin": gap["support_origin"],
                "recoverability": gap["recoverability"],
                "dependency_impact": gap["dependency_impact"],
                "report_even_if_final_pass": gap["report_even_if_final_pass"],
            }
        )
    original_verdict = (
        "NO_FIRST_BREAK"
        if reviewer_final.strip() == "NO_FIRST_BREAK"
        else "FIRST_BREAK"
    )
    reportable = [gap for gap in gaps if gap["report_even_if_final_pass"]]
    consistency = (
        "GAP_SUPPRESSED_BY_FINAL"
        if original_verdict == "NO_FIRST_BREAK" and reportable
        else ("NO_GAP_FOUND" if not gaps else "CONSISTENT")
    )
    return {
        "original_verdict": original_verdict,
        "gaps": gaps,
        "trace_final_consistency": consistency,
        "summary": compact["summary"],
    }


def validate_source_binding(
    *, record: dict[str, Any], proof: str, reasoning: str, reviewer_final: str
) -> list[dict[str, Any]]:
    expected_verdict = (
        "NO_FIRST_BREAK"
        if reviewer_final.strip() == "NO_FIRST_BREAK"
        else "FIRST_BREAK"
    )
    if record["original_verdict"] != expected_verdict:
        raise ValueError("extractor changed the original reviewer verdict")
    bound: list[dict[str, Any]] = []
    for index, gap in enumerate(record["gaps"], start=1):
        proof_location = str(gap["proof_location"])
        trace_evidence = str(gap["trace_evidence"])
        if proof_location not in proof:
            raise ValueError(f"gap {index} proof_location is not source-bound")
        if trace_evidence not in reasoning:
            raise ValueError(f"gap {index} trace_evidence is not source-bound")
        expected_report = gap["support_origin"] in {
            "REVIEWER_ADDED",
            "UNRESOLVED",
        }
        if bool(gap["report_even_if_final_pass"]) != expected_report:
            raise ValueError(f"gap {index} report flag contradicts support origin")
        bound.append({"gap_id": f"TG{index}", **gap})
    reportable = [gap for gap in bound if gap["report_even_if_final_pass"]]
    expected_consistency = (
        "GAP_SUPPRESSED_BY_FINAL"
        if expected_verdict == "NO_FIRST_BREAK" and reportable
        else ("NO_GAP_FOUND" if not bound else "CONSISTENT")
    )
    if record["trace_final_consistency"] != expected_consistency:
        raise ValueError("trace-final consistency does not match bound gap records")
    return bound


def _read_problem(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    problem = str(payload.get("problem") or payload.get("claim") or "").strip()
    if not problem:
        raise ValueError(f"problem field is empty: {path}")
    return problem


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gemma forensic extraction of gaps noticed in Reviewer 1 reasoning"
    )
    parser.add_argument("--problem-json", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--reasoning", type=Path, required=True)
    parser.add_argument("--reviewer-final", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8020/v1")
    parser.add_argument("--master-seed", type=int, default=20260826)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="reuse a failed primary generation and continue with compact recovery",
    )
    parser.add_argument(
        "--compact-only",
        action="store_true",
        help="skip the original call and run only compact recovery after a known failure",
    )
    args = parser.parse_args()

    if not 0.0 <= args.temperature <= 2.0:
        raise ValueError("temperature must be between 0 and 2")
    if args.output_dir.exists() and any(args.output_dir.iterdir()) and not args.resume:
        raise ValueError(f"output directory must be new or empty: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    problem = _read_problem(args.problem_json)
    proof = args.proof.read_text(encoding="utf-8").strip()
    reasoning = args.reasoning.read_text(encoding="utf-8").strip()
    reviewer_final = args.reviewer_final.read_text(encoding="utf-8").strip()
    user_prompt = trace_gap_user_prompt(
        problem=problem,
        proof=proof,
        reasoning=reasoning,
        reviewer_final=reviewer_final,
    )
    manifest = {
        "schema": "cognitive-well-v083-gemma-trace-gap-extractor-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "model": "google/gemma-4-31B-it",
        "temperature": args.temperature,
        "max_tokens": 12_000,
        "reasoning_effort": "max",
        "guided_decoding": "structured_outputs.json",
        "proof_path": str(args.proof.resolve()),
        "proof_sha256": sha256_text(proof),
        "reasoning_path": str(args.reasoning.resolve()),
        "reasoning_sha256": sha256_text(reasoning),
        "reviewer_final_path": str(args.reviewer_final.resolve()),
        "reviewer_final_sha256": sha256_text(reviewer_final),
        "system_prompt_sha256": sha256_text(TRACE_GAP_SYSTEM_PROMPT),
        "user_prompt_sha256": sha256_text(user_prompt),
    }
    write_json(args.output_dir / "manifest.json", manifest)
    write_json(
        args.output_dir / "status.json",
        {"state": "running", "stage": "trace_gap_extraction", "updated_at": utc_now()},
    )
    runtime = ModelRuntime(
        RuntimeConfig(
            gemma_endpoint=args.gemma_endpoint.rstrip("/"),
            qwen_endpoint=args.gemma_endpoint.rstrip("/"),
            master_seed=args.master_seed,
        )
    )
    primary_error: str | None = None
    recovery_mode = "primary"
    try:
        if args.compact_only:
            raise ValueError("primary generation previously failed; compact-only requested")
        record, generated = runtime.structured(
            role="gemma",
            prompt=TRACE_GAP_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            destination=args.output_dir / "generation",
            stage="trace_gap_extraction",
            schema=TRACE_GAP_SCHEMA,
            temperature=args.temperature,
            max_tokens=12_000,
            seed_label="v083:p5:reviewer1:trace_gap_extraction",
            use_explicit_guided_json=True,
        )
    except (KeyError, TypeError, ValueError) as error:
        primary_error = f"{type(error).__name__}: {error}"
        recovery_mode = "compact_line_id_retry"
        compact_prompt, proof_lines, trace_lines = compact_trace_gap_user_prompt(
            problem=problem,
            proof=proof,
            reasoning=reasoning,
            reviewer_final=reviewer_final,
        )
        compact, generated = runtime.structured(
            role="gemma",
            prompt=TRACE_GAP_SYSTEM_PROMPT,
            user_prompt=compact_prompt,
            destination=args.output_dir / "compact_recovery_v2",
            stage="trace_gap_extraction_compact_v2",
            schema=COMPACT_TRACE_GAP_SCHEMA,
            temperature=args.temperature,
            max_tokens=8_000,
            seed_label="v083:p5:reviewer1:trace_gap_extraction:compact_retry:v2",
            use_explicit_guided_json=False,
        )
        record = materialize_compact_record(
            compact=compact,
            proof_lines=proof_lines,
            trace_lines=trace_lines,
            reviewer_final=reviewer_final,
        )
    gaps = validate_source_binding(
        record=record,
        proof=proof,
        reasoning=reasoning,
        reviewer_final=reviewer_final,
    )
    reportable = [gap for gap in gaps if gap["report_even_if_final_pass"]]
    result = {
        "schema": "cognitive-well-v083-gemma-trace-gap-extractor-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "original_verdict": record["original_verdict"],
        "trace_final_consistency": record["trace_final_consistency"],
        "gap_count": len(gaps),
        "reportable_gap_count": len(reportable),
        "gaps": gaps,
        "summary": record["summary"],
        "recovery_mode": recovery_mode,
        "primary_error": primary_error,
        "generation": generated["metadata"],
    }
    write_json(args.output_dir / "result.json", result)
    write_json(
        args.output_dir / "status.json",
        {
            "state": "completed",
            "stage": "trace_gap_extraction",
            "gap_count": len(gaps),
            "reportable_gap_count": len(reportable),
            "trace_final_consistency": record["trace_final_consistency"],
            "updated_at": result["completed_at"],
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
