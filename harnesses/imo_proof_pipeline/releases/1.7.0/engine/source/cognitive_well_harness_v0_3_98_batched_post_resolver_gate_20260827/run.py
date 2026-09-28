from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from cognitive_well_harness_v0_3_49_reviewer1_temperature_ablation_20260823.protocol import (
    parse_review as parse_reviewer_1,
)
from cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823 import (
    run as reviewer_2,
)
from cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823.protocol import (
    parse_review as parse_reviewer_2,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.protocol import (
    parse_review as parse_reviewer_3,
)
from cognitive_well_harness_v0_3_53_fusion_20260823.protocol import (
    parse_fusion,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_84_trace_resolution_batch_20260827 import (
    pipeline as v084,
)
from cognitive_well_harness_v0_3_87_markdown_trace_extractor_20260827.pipeline import (
    parse_compact_markdown,
    run_compact_markdown_extractor,
    run_original_reviewer,
)
from cognitive_well_harness_v0_3_88_bf16_mtp4_trace_gate_selector_20260827.pipeline import (
    markdown_trace_packets,
)
from cognitive_well_harness_v0_3_89_conditional_gap_selector_20260827.pipeline import (
    run_gap_selector,
)
from cognitive_well_harness_v0_3_96_generic_enhanced_review_fusion_resolver_20260827.generic_adapters import (
    reviewer_1_failure_record,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8021/v1"
FRESH_REVIEWER_1_TEMPERATURE = 0.1
FRESH_REVIEWER_2_TEMPERATURE = 0.2
TRACE_TEMPERATURE = 0.1
OBLIGATION_CLOSURE_TEMPERATURE = 0.1


RESOLVER_TRACE_EXTRACTOR_SYSTEM_PROMPT = r"""You are a high-recall forensic
extractor for an olympiad proof Resolver. You receive the original problem, the
Resolver's terminal proof, its complete internal reasoning trace, and its visible
result. Do not re-grade, filter, certify, or repair the mathematics. Extract what the
Resolver itself left doubtful or unresolved.

Recall is the priority. Emit one candidate for every distinct possible repair need in
the reasoning trace or visible result: a missing premise, unsupported transition,
circular step, unjustified assumption, unavailable sequence or limit, failed route,
contradiction, boundary case, or unresolved obligation. `Repair needed` is mandatory.

Do not suppress an item because the Resolver later asserted that the proof was valid,
complete, continuous, connected, routine, or repaired. Do not suppress an abandoned
or rejected objection; state its later disposition in `Reason` so a conservative
selector can compare it against the terminal proof. Do not invent material absent
from the supplied trace and visible result. Consolidate repeated discussions of the
same issue, preserving all non-routine useful material around it.

Return only compact Markdown. Repeat exactly this block for every finding:

### Candidate
- Useful material: <compact text or (none)>
- Repair needed: <compact nonempty text>
- Reason: <why it appeared and whether the Resolver retained, repaired, questioned, assumed, or abandoned it>

Keep every field on one physical line. If there is no possible repair need, output
exactly `No candidates.` Output no IDs, verdict, score, JSON, fences, or extra
sections."""


RESOLVER_TRACE_MATERIALIZER_SYSTEM_PROMPT = r"""You are a compact record
materializer. The supplied model reasoning has already completed the forensic
extraction. Do not restart the audit, solve the problem, or add new mathematics.
Materialize every candidate identified in that preserved reasoning.

Return only compact Markdown. Repeat exactly this block for every finding:

### Candidate
- Useful material: <compact text or (none)>
- Repair needed: <compact nonempty text>
- Reason: <why it appeared and whether it was retained, repaired, questioned, assumed, or abandoned>

Keep every field on one physical line. If there is no possible repair need, output
exactly `No candidates.` Output no IDs, verdict, score, JSON, fences, or extra
sections."""


OBLIGATION_CLOSURE_SYSTEM_PROMPT = r"""You are a provenance-strict olympiad
proof-obligation auditor. You receive an original problem, a complete terminal proof,
and concrete obligations carried forward from earlier audits of its ancestor proof.

For every obligation, inspect only the submitted terminal proof and assign one label:

- CLOSED: the terminal proof explicitly supplies a mathematically valid argument that
  closes the obligation. Name the exact proof location. Do not credit an argument that
  exists only in your own reasoning.
- UNCLOSED: the obligation is mathematically relevant and load-bearing, but the
  terminal proof still omits it, assumes it, argues circularly, or replaces it with an
  equivalent unsupported assertion.
- UNSUPPORTED: the inherited objection itself is false, irrelevant to this terminal
  proof, or based on a demonstrably invalid premise.

An obligation is not CLOSED merely because you can see how to repair it. Do not add a
lemma, solve the missing case, rewrite the proof, or silently strengthen its premises.
Judge literal proof sufficiency and preserve source provenance. Re-check whether a
purported repair simply restates the old conclusion in new notation.

Return compact Markdown in exactly this form, once per supplied obligation and in the
same order:

## OB1
- Label: CLOSED | UNCLOSED | UNSUPPORTED
- Proof location: <exact location or (none)>
- Reason: <one concise mathematical explanation>

After all obligations return:

## Summary
<one concise sentence>

Keep each field on one physical line. Do not return JSON, fences, a repaired proof,
or extra sections.

HIGH-STAKES DELIBERATION REQUIREMENT

Spare no effort. Use the maximum reasoning effort available. Never complete a missing
argument privately and then credit the terminal proof with that completion."""


OBLIGATION_SECTION_RE = re.compile(
    r"(?ms)^##\s+(OB[0-9]+)\s*$\n(.*?)(?=^##\s+(?:OB[0-9]+|Summary)\s*$|\Z)"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_seed(label: str) -> int:
    value = int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:4], "big")
    return value or 1


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_within(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes the single-problem source root: {path}") from error
    return path


def authorized_terminal_proof_path(
    *,
    case_dir: Path,
    source_root: Path,
    original_proof_path: Path,
    handoff_proof_path: Path,
    resolver_outcome: str,
    case_id: str,
) -> Path:
    """Resolve the terminal proof without weakening single-problem containment.

    v0.3.96 stores a case-local resolved proof after a rewrite, but deliberately
    points back to the hash-bound ancestor proof when the Resolver returns
    ORIGINAL_PROOF_VALID.  The latter path is outside the individual case
    directory while remaining inside the same problem-only source root.
    """
    candidate = require_within(
        source_root,
        handoff_proof_path,
        f"case {case_id} terminal proof",
    )
    case_dir = case_dir.resolve()
    original_proof_path = original_proof_path.resolve()
    try:
        candidate.relative_to(case_dir)
    except ValueError as error:
        if resolver_outcome != "ORIGINAL_PROOF_VALID" or candidate != original_proof_path:
            raise ValueError(
                f"case {case_id} terminal proof is neither case-local nor the "
                f"authorized original proof: {candidate}"
            ) from error
    return candidate


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def one_file(root: Path, pattern: str) -> Path:
    paths = sorted(root.glob(pattern))
    if len(paths) != 1:
        raise ValueError(f"expected one {pattern!r} under {root}, found {len(paths)}")
    return paths[0].resolve()


def phase2_directory(source_run: Path) -> Path:
    source = source_run.resolve()
    if (source / "phase_2_v096" / "summary.json").is_file():
        return require_within(source, source / "phase_2_v096", "v0.3.96 phase")
    if (source / "summary.json").is_file() and (source / "cases").is_dir():
        return source
    raise ValueError(f"not a v0.3.96 output or v0.3.97 parent run: {source}")


def visible_result(payload: dict[str, Any], result_path: Path) -> str:
    value = str(payload.get("final") or "").strip()
    if value:
        return value
    for name in ("final.txt", "final.md"):
        candidate = result_path.parent / name
        if candidate.is_file() and candidate.read_text(encoding="utf-8").strip():
            return candidate.read_text(encoding="utf-8").strip()
    raise ValueError(f"result has no visible output: {result_path}")


def combined_trace(paths: list[Path]) -> str:
    chunks: list[str] = []
    seen: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        digest = sha256_text(text)
        if not text or digest in seen:
            continue
        seen.add(digest)
        chunks.append(text)
    return "\n\n[CONTINUATION]\n\n".join(chunks)


def saved_reasoning(directory: Path) -> str:
    return combined_trace(sorted(directory.glob("*.reasoning.txt")))


def review_obligation(role: str, final: str) -> dict[str, str] | None:
    parsers: dict[str, Callable[[str], dict[str, Any]]] = {
        "reviewer_1": parse_reviewer_1,
        "reviewer_2": parse_reviewer_2,
        "reviewer_3": parse_reviewer_3,
    }
    parsed = parsers[role](final)
    if not parsed["valid"]:
        raise ValueError(f"invalid effective {role} record: {parsed['errors']}")
    fields = parsed.get("fields") or {}
    outcome = str(parsed["outcome"])
    if role == "reviewer_1" and outcome == "FIRST_BREAK":
        return {
            "source": role,
            "target": str(fields.get("claim") or fields.get("location") or ""),
            "defect": str(fields.get("missing_or_invalid_link") or fields.get("why_not_follow") or ""),
            "minimum_requirement": str(fields.get("minimum_requirement") or ""),
        }
    if role == "reviewer_2" and outcome == "ADVERSARIAL_BREAK":
        return {
            "source": role,
            "target": str(fields.get("target_claim") or fields.get("location") or ""),
            "defect": str(fields.get("verification") or fields.get("why_decisive") or ""),
            "minimum_requirement": str(fields.get("minimum_requirement") or ""),
        }
    if role == "reviewer_3" and outcome == "CERTIFICATION_FAILURE":
        return {
            "source": role,
            "target": str(fields.get("critical_obligation") or ""),
            "defect": str(fields.get("why_completion_fails") or fields.get("impact_on_conclusion") or ""),
            "minimum_requirement": str(fields.get("minimum_required_lemma") or ""),
        }
    return None


def fusion_obligation(final: str) -> dict[str, str] | None:
    parsed = parse_fusion(final)
    if not parsed["valid"]:
        raise ValueError(f"invalid Fusion record: {parsed['errors']}")
    if parsed["outcome"] != "REPAIR_NEEDED":
        return None
    fields = parsed.get("fields") or {}
    return {
        "source": "fusion",
        "target": str(fields.get("failed_obligation") or fields.get("decisive_location") or ""),
        "defect": str(fields.get("independent_validation") or fields.get("impact_on_proof") or ""),
        "minimum_requirement": str(fields.get("resolver_brief") or ""),
    }


def exact_deduplicate_obligations(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        if not str(row.get("target") or "").strip():
            continue
        digest = sha256_text(
            normalize_space(str(row.get("target") or "")).lower()
            + "\n"
            + normalize_space(str(row.get("defect") or "")).lower()
            + "\n"
            + normalize_space(str(row.get("minimum_requirement") or "")).lower()
        )
        if digest in seen:
            continue
        seen.add(digest)
        unique.append({**row, "obligation_id": f"OB{len(unique) + 1}", "sha256": digest})
    return unique


def post_resolver_obligations(case: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for gap in case["resolver_trace_real_gaps"]:
        rows.append(
            {
                "source": "resolver_trace_selector",
                "target": gap["repair_needed"],
                "defect": gap["selector_reason"],
                "minimum_requirement": gap.get("useful_material") or "",
            }
        )

    if case["fresh_reviewer_1"]["parsed"]["outcome"] == "FIRST_BREAK":
        obligation = review_obligation("reviewer_1", case["fresh_reviewer_1"]["final"])
        if obligation is not None:
            rows.append({**obligation, "source": "post_resolver_reviewer_1"})
    else:
        for gap in case["fresh_reviewer_1_trace_real_gaps"]:
            rows.append(
                {
                    "source": "post_resolver_reviewer_1_trace_selector",
                    "target": gap["repair_needed"],
                    "defect": gap["selector_reason"],
                    "minimum_requirement": gap.get("useful_material") or "",
                }
            )

    if case["fresh_reviewer_2"]["parsed"]["outcome"] == "ADVERSARIAL_BREAK":
        obligation = review_obligation("reviewer_2", case["fresh_reviewer_2"]["final"])
        if obligation is not None:
            rows.append({**obligation, "source": "post_resolver_reviewer_2"})
    return exact_deduplicate_obligations(rows)


def build_updated_ledger(case: dict[str, Any]) -> dict[str, Any]:
    decisions = {
        row["obligation_id"]: row for row in case["closure_result"]["decisions"]
    }
    entries: list[dict[str, Any]] = []
    by_digest: dict[str, dict[str, Any]] = {}
    for obligation in case["obligations"]:
        decision = decisions[obligation["obligation_id"]]
        entry = {
            **obligation,
            "phase": "pre_resolver",
            "status": decision["label"],
            "proof_location": decision["proof_location"],
            "status_reason": decision["reason"],
            "post_resolver_sources": [],
        }
        entries.append(entry)
        by_digest[obligation["sha256"]] = entry

    for obligation in post_resolver_obligations(case):
        existing = by_digest.get(obligation["sha256"])
        if existing is not None:
            existing["status"] = "OPEN"
            existing["post_resolver_sources"].append(obligation["source"])
            existing["status_reason"] = (
                "The same concrete defect was independently detected after resolution."
            )
            continue
        entry = {
            **obligation,
            "obligation_id": f"OB{len(entries) + 1}",
            "phase": "post_resolver",
            "status": "OPEN",
            "proof_location": "(reported by post-Resolver audit)",
            "status_reason": obligation["defect"],
            "post_resolver_sources": [obligation["source"]],
        }
        entries.append(entry)
        by_digest[obligation["sha256"]] = entry

    active = [row for row in entries if row["status"] in {"UNCLOSED", "OPEN"}]
    return {
        "schema": "cognitive-well-v098-updated-obligation-ledger-v1",
        "case_id": case["case_id"],
        "proof_sha256": case["proof_sha256"],
        "entry_count": len(entries),
        "active_count": len(active),
        "entries": entries,
        "active_obligations": active,
    }


def load_case(
    phase2: Path, spec: dict[str, Any], row: dict[str, Any],
    *, source_root: Path | None = None,
) -> dict[str, Any]:
    phase2 = phase2.resolve()
    source_root = (source_root if source_root is not None else phase2.parent).resolve()
    require_within(source_root, phase2, "phase2 source")
    case_id = str(spec["case_id"])
    case_dir = require_within(phase2, phase2 / "cases" / case_id, f"case {case_id}")
    problem_path = require_within(
        source_root, Path(str(spec["problem_path"])), f"case {case_id} problem"
    )
    original_proof_path = require_within(
        source_root, Path(str(spec["proof_path"])), f"case {case_id} ancestor proof"
    )
    problem_payload = load_json(problem_path)
    problem = str(problem_payload.get("claim") or problem_payload.get("problem") or "").strip()
    if not problem:
        raise ValueError(f"empty problem: {problem_path}")

    handoff_path = (case_dir / "resolver_trace_handoff" / "handoff.json").resolve()
    handoff = load_json(handoff_path)
    resolver_result_path = require_within(
        case_dir,
        Path(str(handoff["resolver_result_path"])),
        f"case {case_id} resolver result",
    )
    resolver_result = load_json(resolver_result_path)
    resolver_final = visible_result(resolver_result, resolver_result_path)
    terminal_proof_path = authorized_terminal_proof_path(
        case_dir=case_dir,
        source_root=source_root,
        original_proof_path=original_proof_path,
        handoff_proof_path=Path(str(handoff["proof_path"])),
        resolver_outcome=str((resolver_result.get("parsed") or {}).get("outcome") or ""),
        case_id=case_id,
    )
    terminal_proof = terminal_proof_path.read_text(encoding="utf-8").strip()
    terminal_sha = sha256_text(terminal_proof)
    if handoff.get("proof_sha256") and str(handoff["proof_sha256"]) != terminal_sha:
        raise ValueError(f"terminal proof hash mismatch: {case_id}")
    trace_paths = [
        require_within(
            case_dir,
            Path(str(item["path"])),
            f"case {case_id} resolver trace",
        )
        for item in handoff.get("trace_files") or []
    ]
    resolver_reasoning = combined_trace(trace_paths)
    if not resolver_reasoning:
        raise ValueError(f"Resolver reasoning is unavailable: {case_id}")

    fusion_result_path = one_file(case_dir, "fusion/**/result.json")
    fusion_result = load_json(fusion_result_path)
    fusion_final = visible_result(fusion_result, fusion_result_path)
    effective_reviews: dict[str, str] = {}
    obligations: list[dict[str, str]] = []
    for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
        path = case_dir / f"effective_{role}.txt"
        final = path.read_text(encoding="utf-8").strip()
        effective_reviews[role] = final
        obligation = review_obligation(role, final)
        if obligation is not None:
            obligations.append(obligation)
    obligation = fusion_obligation(fusion_final)
    if obligation is not None:
        obligations.append(obligation)
    obligations = exact_deduplicate_obligations(obligations)

    return {
        "case_id": case_id,
        "proof_index": int(spec.get("proof_index", 0)),
        "problem_number": int(spec["problem_number"]),
        "problem_id": str(spec["problem_id"]),
        "candidate_id": str(spec["candidate_id"]),
        "problem_path": str(problem_path),
        "problem": problem,
        "problem_sha256": sha256_text(problem),
        "ancestor_proof_path": str(original_proof_path),
        "ancestor_proof_sha256": str(spec["proof_sha256"]),
        "proof_path": str(terminal_proof_path),
        "proof": terminal_proof,
        "proof_sha256": terminal_sha,
        "resolver_outcome": str(row["resolver_outcome"]),
        "resolver_result_path": str(resolver_result_path),
        "resolver_result_sha256": file_sha256(resolver_result_path),
        "resolver_final": resolver_final,
        "resolver_reasoning": resolver_reasoning,
        "resolver_reasoning_sha256": sha256_text(resolver_reasoning),
        "source_trace_handoff": str(handoff_path),
        "source_fusion_result": str(fusion_result_path),
        "source_fusion_final": fusion_final,
        "source_effective_reviews": effective_reviews,
        "obligations": obligations,
        "source_phase2": str(phase2),
    }


def load_source_runs(source_runs: list[Path]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for source in source_runs:
        phase2 = phase2_directory(source)
        manifest = load_json(phase2 / "manifest.json")
        summary = load_json(phase2 / "summary.json")
        specs = {str(item["case_id"]): item for item in manifest.get("cases") or []}
        for row in summary.get("rows") or []:
            case_id = str(row["case_id"])
            if case_id not in specs:
                raise ValueError(f"summary case absent from manifest: {case_id}")
            cases.append(load_case(phase2, specs[case_id], row))
    identifiers = [case["case_id"] for case in cases]
    if not cases or len(set(identifiers)) != len(identifiers):
        raise ValueError("source runs must provide nonempty, uniquely identified cases")
    for index, case in enumerate(cases):
        case["gate_index"] = index
    return cases


def run_parallel(
    *, name: str, jobs: list[dict[str, Any]], workers: int,
    task: Callable[[dict[str, Any]], None]
) -> None:
    errors: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, workers), thread_name_prefix=f"v098-{name}"
    ) as pool:
        pending = {pool.submit(task, job): job for job in jobs}
        for future in concurrent.futures.as_completed(pending):
            job = pending[future]
            job_id = str(job["job_id"])
            try:
                future.result()
                print(f"[{utc_now()}] {name}: {job_id} completed", flush=True)
            except Exception as error:
                errors[job_id] = f"{type(error).__name__}: {error}"
                print(f"[{utc_now()}] {name}: {job_id} failed: {errors[job_id]}", flush=True)
    if errors:
        raise RuntimeError(f"{name} failures: {json.dumps(errors, ensure_ascii=False)}")


def resolver_extractor_user_prompt(case: dict[str, Any]) -> str:
    return (
        "# RESOLVER TRACE EXTRACTION INPUT\n\n"
        "## ORIGINAL PROBLEM\n" + case["problem"]
        + "\n\n## TERMINAL PROOF\n" + case["proof"]
        + "\n\n## RESOLVER COMPLETE REASONING TRACE\n" + case["resolver_reasoning"]
        + "\n\n## RESOLVER VISIBLE RESULT\n" + case["resolver_final"]
        + "\n\nExtract every candidate now.\n"
    )


def run_resolver_trace_extractor(
    *, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    identity = {
        "problem_sha256": case["problem_sha256"],
        "proof_sha256": case["proof_sha256"],
        "reasoning_sha256": case["resolver_reasoning_sha256"],
        "prompt_sha256": sha256_text(RESOLVER_TRACE_EXTRACTOR_SYSTEM_PROMPT),
    }
    if result_path.is_file():
        saved = load_json(result_path)
        if saved.get("identity") == identity:
            return saved
    output_dir.mkdir(parents=True, exist_ok=True)
    label = f"{seed_namespace}:{case['case_id']}:resolver_trace_extract"
    runtime = v084.runtime_for(endpoint, stable_seed(label), GEMMA_MODEL)
    compact_materialized = False
    primary_recovery_error: str | None = None

    def materialize(preserved: str) -> dict[str, Any]:
        return runtime.text(
            role="gemma",
            prompt=RESOLVER_TRACE_MATERIALIZER_SYSTEM_PROMPT,
            user_prompt=(
                resolver_extractor_user_prompt(case).rstrip()
                + "\n\n## ALREADY-COMPLETED EXTRACTOR REASONING\n"
                + preserved
                + "\n\nMaterialize the compact record now.\n"
            ),
            destination=output_dir / "generation",
            stage="resolver_trace_compact_materialization",
            temperature=TRACE_TEMPERATURE,
            max_tokens=3_000,
            seed_label=label + ":compact_materialization",
            top_p=1.0,
            top_k=-1,
        )

    prior_reasoning_files = [
        path for path in sorted((output_dir / "generation").glob("*.reasoning.txt"))
        if path.read_text(encoding="utf-8").strip()
    ]
    if len(prior_reasoning_files) >= 3:
        compact_materialized = True
        primary_recovery_error = "resumed_after_prior_three-attempt_output_exhaustion"
        generated = materialize(saved_reasoning(output_dir / "generation"))
    else:
        try:
            generated = runtime.text(
                role="gemma",
                prompt=RESOLVER_TRACE_EXTRACTOR_SYSTEM_PROMPT,
                user_prompt=resolver_extractor_user_prompt(case),
                destination=output_dir / "generation",
                stage="resolver_trace_extraction",
                temperature=TRACE_TEMPERATURE,
                max_tokens=6_000,
                seed_label=label,
                top_p=1.0,
                top_k=-1,
            )
        except RuntimeError as primary_error:
            primary_recovery_error = f"{type(primary_error).__name__}: {primary_error}"
            preserved = saved_reasoning(output_dir / "generation")
            if not preserved:
                raise
            compact_materialized = True
            generated = materialize(preserved)
    final = str(generated["text"]).strip()
    format_retry = False
    try:
        candidates = parse_compact_markdown(final)
    except ValueError as primary_error:
        format_retry = True
        generated = runtime.text(
            role="gemma",
            prompt=(
                RESOLVER_TRACE_EXTRACTOR_SYSTEM_PROMPT
                + "\n\nFORMAT RETRY\nThe preceding response was not parseable. Repeat "
                "the extraction and return only the required compact Markdown blocks."
            ),
            user_prompt=resolver_extractor_user_prompt(case),
            destination=output_dir / "generation",
            stage="resolver_trace_extraction_format_retry",
            temperature=TRACE_TEMPERATURE,
            max_tokens=6_000,
            seed_label=label + ":format_retry",
            top_p=1.0,
            top_k=-1,
        )
        final = str(generated["text"]).strip()
        candidates = parse_compact_markdown(final)
        runtime._recovery_events.append(
            {
                "kind": "format_retry",
                "stage": "resolver_trace_extraction",
                "accepted": True,
                "prior_error": f"{type(primary_error).__name__}: {primary_error}",
                "attempts": [],
            }
        )
    (output_dir / "final.md").write_text(final + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v098-resolver-trace-extraction-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "identity": identity,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "compact_materialized_after_exhaustion": compact_materialized,
        "primary_recovery_error": primary_recovery_error,
        "format_retry": format_retry,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def closure_user_prompt(case: dict[str, Any]) -> str:
    blocks = []
    for obligation in case["obligations"]:
        blocks.append(
            "## " + obligation["obligation_id"]
            + "\n- Source: " + obligation["source"]
            + "\n- Target obligation: " + obligation["target"]
            + "\n- Reported defect: " + (obligation["defect"] or "(none)")
            + "\n- Minimum requirement: "
            + (obligation["minimum_requirement"] or "(none)")
        )
    return (
        "# OBLIGATION CLOSURE INPUT\n\n## ORIGINAL PROBLEM\n" + case["problem"]
        + "\n\n## TERMINAL PROOF\n" + case["proof"]
        + "\n\n## INHERITED OBLIGATIONS\n" + "\n\n".join(blocks)
        + "\n\nClassify every obligation now.\n"
    )


def parse_obligation_closure(value: str, obligations: list[dict[str, str]]) -> dict[str, Any]:
    text = value.strip()
    decisions: list[dict[str, str]] = []
    for match in OBLIGATION_SECTION_RE.finditer(text):
        obligation_id, body = match.group(1), match.group(2).strip()
        label_match = re.search(
            r"(?im)^- Label:\s*(CLOSED|UNCLOSED|UNSUPPORTED)\s*$", body
        )
        location_match = re.search(r"(?im)^- Proof location:\s*(.+?)\s*$", body)
        reason_match = re.search(r"(?im)^- Reason:\s*(.+?)\s*$", body)
        if not label_match or not location_match or not reason_match:
            raise ValueError(f"incomplete closure section: {obligation_id}")
        decisions.append(
            {
                "obligation_id": obligation_id,
                "label": label_match.group(1),
                "proof_location": location_match.group(1).strip(),
                "reason": reason_match.group(1).strip(),
            }
        )
    summary_match = re.search(r"(?ims)^##\s+Summary\s*$\n(.+?)\s*$", text)
    if not summary_match:
        raise ValueError("closure response lacks Summary")
    expected = [row["obligation_id"] for row in obligations]
    observed = [row["obligation_id"] for row in decisions]
    if expected != observed:
        raise ValueError(f"closure IDs/order mismatch: expected {expected}, got {observed}")
    return {"decisions": decisions, "summary": summary_match.group(1).strip()}


def run_obligation_closure(
    *, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    result_path = output_dir / "result.json"
    obligations_sha = sha256_text(
        json.dumps(case["obligations"], ensure_ascii=False, sort_keys=True)
    )
    identity = {
        "problem_sha256": case["problem_sha256"],
        "proof_sha256": case["proof_sha256"],
        "obligations_sha256": obligations_sha,
        "prompt_sha256": sha256_text(OBLIGATION_CLOSURE_SYSTEM_PROMPT),
    }
    if result_path.is_file():
        saved = load_json(result_path)
        if saved.get("identity") == identity:
            return saved
    output_dir.mkdir(parents=True, exist_ok=True)
    if not case["obligations"]:
        result = {
            "schema": "cognitive-well-v098-obligation-closure-result-v1",
            "state": "completed",
            "completed_at": utc_now(),
            "identity": identity,
            "model_call_count": 0,
            "obligation_count": 0,
            "closed_count": 0,
            "unclosed_count": 0,
            "unsupported_count": 0,
            "decisions": [],
            "summary": "No inherited obligations.",
            "generation": None,
        }
        write_json(result_path, result)
        return result
    label = f"{seed_namespace}:{case['case_id']}:obligation_closure"
    runtime = v084.runtime_for(endpoint, stable_seed(label), GEMMA_MODEL)
    generated = runtime.text(
        role="gemma",
        prompt=OBLIGATION_CLOSURE_SYSTEM_PROMPT,
        user_prompt=closure_user_prompt(case),
        destination=output_dir / "generation",
        stage="obligation_closure_audit",
        temperature=OBLIGATION_CLOSURE_TEMPERATURE,
        max_tokens=32_768,
        seed_label=label,
        top_p=1.0,
        top_k=-1,
    )
    final = str(generated["text"]).strip()
    format_retry = False
    try:
        parsed = parse_obligation_closure(final, case["obligations"])
    except ValueError as primary_error:
        format_retry = True
        generated = runtime.text(
            role="gemma",
            prompt=(
                OBLIGATION_CLOSURE_SYSTEM_PROMPT
                + "\n\nFORMAT RETRY\nThe preceding response was not parseable. Repeat "
                "the audit and return only the required obligation sections and Summary."
            ),
            user_prompt=closure_user_prompt(case),
            destination=output_dir / "generation",
            stage="obligation_closure_audit_format_retry",
            temperature=OBLIGATION_CLOSURE_TEMPERATURE,
            max_tokens=32_768,
            seed_label=label + ":format_retry",
            top_p=1.0,
            top_k=-1,
        )
        final = str(generated["text"]).strip()
        parsed = parse_obligation_closure(final, case["obligations"])
        runtime._recovery_events.append(
            {
                "kind": "format_retry",
                "stage": "obligation_closure_audit",
                "accepted": True,
                "prior_error": f"{type(primary_error).__name__}: {primary_error}",
                "attempts": [],
            }
        )
    (output_dir / "final.md").write_text(final + "\n", encoding="utf-8")
    labels = [row["label"] for row in parsed["decisions"]]
    result = {
        "schema": "cognitive-well-v098-obligation-closure-result-v1",
        "state": "completed",
        "completed_at": utc_now(),
        "identity": identity,
        "model_call_count": 1,
        "obligation_count": len(case["obligations"]),
        "closed_count": labels.count("CLOSED"),
        "unclosed_count": labels.count("UNCLOSED"),
        "unsupported_count": labels.count("UNSUPPORTED"),
        **parsed,
        "format_retry": format_retry,
        "generation": generated["metadata"],
        "runtime_recovery_events": runtime.recovery_events(),
    }
    write_json(result_path, result)
    return result


def common_review_task(case: dict[str, Any], *, endpoint: str, gpu: int) -> dict[str, Any]:
    return {
        key: case[key]
        for key in (
            "gate_index", "problem_number", "problem_id", "candidate_id",
            "problem_path", "problem_sha256", "proof_path", "proof_sha256",
            "problem", "proof",
        )
    } | {"proof_index": case["gate_index"], "endpoint": endpoint, "gpu": gpu}


def fresh_reviewer_2(
    *, case: dict[str, Any], endpoint: str, output_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    label = f"{seed_namespace}:{case['case_id']}:fresh_reviewer_2"
    task = common_review_task(case, endpoint=endpoint, gpu=1)
    task.update(
        {
            "seed": stable_seed(label),
            "temperature": FRESH_REVIEWER_2_TEMPERATURE,
            "temperature_label": "t02",
            "model_key": "qwen36",
            "model_name": QWEN_MODEL,
            "task_id": f"{case['case_id']}.post_resolver.reviewer2.t02",
        }
    )
    stage = output_dir / "fresh_reviewer_2_stage"
    result = reviewer_2.run_task(output_dir=stage, task=task)
    final = str(result.get("final") or "").strip()
    parsed = parse_reviewer_2(final)
    if not parsed["valid"]:
        raise ValueError(f"invalid fresh Reviewer 2 output: {parsed['errors']}")
    return {"result": result, "final": final, "parsed": parsed, "task": task}


def trace_real_gaps(extraction: dict[str, Any], selector: dict[str, Any]) -> list[dict[str, str]]:
    packets = markdown_trace_packets(extraction)
    by_id = {str(packet["gap_id"]): packet for packet in packets}
    result: list[dict[str, str]] = []
    for decision in selector.get("decisions") or []:
        if decision.get("label") != "REAL_GAP":
            continue
        packet = by_id[str(decision["gap_id"])]
        result.append(
            {
                "gap_id": str(packet["gap_id"]),
                "useful_material": str(packet.get("useful_material") or ""),
                "repair_needed": str(packet["repair_needed"]),
                "trace_reason": str(packet["reason"]),
                "selector_reason": str(decision["reason"]),
            }
        )
    return result


def gate_decision(case: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if case["resolver_trace_real_gaps"]:
        reasons.append("resolver_trace_real_gap")
    if case["fresh_reviewer_1_effective_outcome"] != "NO_FIRST_BREAK":
        reasons.append("fresh_reviewer_1_break")
    if case["fresh_reviewer_2"]["parsed"]["outcome"] != "NO_ADVERSARIAL_BREAK":
        reasons.append("fresh_reviewer_2_break")
    if int(case["closure_result"].get("unclosed_count") or 0) > 0:
        reasons.append("inherited_obligation_unclosed")
    return {
        "outcome": "PASS" if not reasons else "REJECTED",
        "reasons": reasons,
        "terminal_proof_status": "GATED_PASS" if not reasons else "QUARANTINED",
    }


def run(
    *, source_runs: list[Path], output_dir: Path, gemma_endpoint: str,
    qwen_endpoint: str, gemma_workers: int, qwen_workers: int,
    seed_namespace: str, dry_run: bool = False
) -> dict[str, Any]:
    if gemma_workers < 1 or qwen_workers < 1:
        raise ValueError("worker counts must be positive")
    cases = load_source_runs(source_runs)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    gemma_endpoint = gemma_endpoint.rstrip("/")
    qwen_endpoint = qwen_endpoint.rstrip("/")
    if not gemma_endpoint or not qwen_endpoint or gemma_endpoint == qwen_endpoint:
        raise ValueError("distinct nonempty Gemma and Qwen endpoints are required")

    manifest = {
        "schema": "cognitive-well-v098-batched-post-resolver-gate-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_runs": [str(path.resolve()) for path in source_runs],
        "case_count": len(cases),
        "models": {"gemma": GEMMA_MODEL, "qwen": QWEN_MODEL},
        "runtime": {
            "gemma_endpoint": gemma_endpoint,
            "gemma_dtype": "bfloat16",
            "gemma_mtp_speculative_tokens": 4,
            "qwen_endpoint": qwen_endpoint,
            "gemma_workers": gemma_workers,
            "qwen_workers": qwen_workers,
        },
        "temperatures": {
            "resolver_trace_extractor": TRACE_TEMPERATURE,
            "resolver_trace_selector": TRACE_TEMPERATURE,
            "fresh_reviewer_1": FRESH_REVIEWER_1_TEMPERATURE,
            "fresh_reviewer_1_trace_gate": TRACE_TEMPERATURE,
            "fresh_reviewer_2": FRESH_REVIEWER_2_TEMPERATURE,
            "obligation_closure": OBLIGATION_CLOSURE_TEMPERATURE,
        },
        "schedule": {
            "gpu0": "resolver_trace_extract_batch -> resolver_trace_selector_batch -> fresh_reviewer_1_batch -> conditional_r1_trace_extract_batch -> conditional_r1_selector_batch",
            "gpu1": "fresh_reviewer_2_batch concurrent with complete GPU0 branch",
            "barrier": "before obligation_closure_batch",
            "terminal_gate": "no selected resolver-trace REAL_GAP AND fresh R1 pass AND fresh Qwen pass AND zero UNCLOSED inherited obligations",
        },
        "problem_specific_prompting": False,
        "prompt_sha256": {
            "resolver_trace_extractor": sha256_text(RESOLVER_TRACE_EXTRACTOR_SYSTEM_PROMPT),
            "obligation_closure": sha256_text(OBLIGATION_CLOSURE_SYSTEM_PROMPT),
        },
        "cases": [
            {
                key: case[key]
                for key in (
                    "case_id", "problem_id", "candidate_id", "problem_path",
                    "problem_sha256", "proof_path", "proof_sha256",
                    "resolver_result_path", "resolver_result_sha256",
                    "source_trace_handoff", "source_fusion_result",
                )
            } | {"obligations": case["obligations"]}
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})

    if dry_run:
        summary = {
            "schema": "cognitive-well-v098-dry-run-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "case_count": len(cases),
            "planned_model_calls": {
                "resolver_trace_extractors": len(cases),
                "resolver_trace_selectors_max": len(cases),
                "fresh_reviewer_1": len(cases),
                "fresh_reviewer_1_trace_gate_max": 2 * len(cases),
                "fresh_reviewer_2": len(cases),
                "obligation_closure": sum(bool(case["obligations"]) for case in cases),
            },
            "obligation_counts": {
                case["case_id"]: len(case["obligations"]) for case in cases
            },
            "completed_at": utc_now(),
        }
        write_json(output_dir / "summary.json", summary)
        write_json(output_dir / "status.json", {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()})
        return summary

    jobs = [{"job_id": case["case_id"], "case": case} for case in cases]

    def gpu0_branch() -> None:
        write_json(output_dir / "status.json", {"state": "running", "stage": "resolver_trace_extraction_batch", "updated_at": utc_now()})

        def resolver_extract(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "resolver_trace_gate"
            case["resolver_trace_extraction"] = run_resolver_trace_extractor(
                case=case, endpoint=gemma_endpoint,
                output_dir=lane / "01_extraction", seed_namespace=seed_namespace,
            )

        run_parallel(name="resolver_trace_extract", jobs=jobs, workers=gemma_workers, task=resolver_extract)

        write_json(output_dir / "status.json", {"state": "running", "stage": "resolver_trace_selector_batch", "updated_at": utc_now()})

        def resolver_select(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "resolver_trace_gate"
            packets = markdown_trace_packets(case["resolver_trace_extraction"])
            selector = run_gap_selector(
                problem=case["problem"], proof=case["proof"], packets=packets,
                endpoint=gemma_endpoint, output_dir=lane / "02_selector",
                seed=stable_seed(f"{seed_namespace}:{case['case_id']}:resolver_trace_select"),
                seed_label=f"{seed_namespace}:{case['case_id']}:resolver_trace_select",
                model=GEMMA_MODEL,
            )
            case["resolver_trace_selector"] = selector
            case["resolver_trace_real_gaps"] = trace_real_gaps(
                case["resolver_trace_extraction"], selector
            )

        run_parallel(name="resolver_trace_select", jobs=jobs, workers=gemma_workers, task=resolver_select)

        write_json(output_dir / "status.json", {"state": "running", "stage": "fresh_reviewer_1_batch", "updated_at": utc_now()})

        def reviewer1(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits" / "reviewer_1"
            label = f"{seed_namespace}:{case['case_id']}:fresh_reviewer_1"
            result = run_original_reviewer(
                problem=case["problem"], proof=case["proof"], endpoint=gemma_endpoint,
                output_dir=lane, seed=stable_seed(label), seed_label=label,
                model=GEMMA_MODEL,
            )
            final = (lane / "final.txt").read_text(encoding="utf-8").strip()
            parsed = parse_reviewer_1(final)
            case["fresh_reviewer_1"] = {
                "result": result,
                "final": final,
                "parsed": parsed,
                "reasoning": (lane / "reasoning.txt").read_text(encoding="utf-8").strip(),
            }

        run_parallel(name="fresh_reviewer_1", jobs=jobs, workers=gemma_workers, task=reviewer1)

        r1_success_jobs = [
            job for job in jobs
            if job["case"]["fresh_reviewer_1"]["parsed"]["outcome"] == "NO_FIRST_BREAK"
        ]
        for job in jobs:
            case = job["case"]
            if case["fresh_reviewer_1"]["parsed"]["outcome"] == "FIRST_BREAK":
                case["fresh_reviewer_1_effective_final"] = case["fresh_reviewer_1"]["final"]
                case["fresh_reviewer_1_effective_outcome"] = "FIRST_BREAK"
                case["fresh_reviewer_1_trace_real_gaps"] = []

        def r1_extract(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits" / "reviewer_1_enhancement"
            label = f"{seed_namespace}:{case['case_id']}:fresh_r1_trace_extract"
            case["fresh_r1_extraction"] = run_compact_markdown_extractor(
                problem=case["problem"], proof=case["proof"],
                reasoning=case["fresh_reviewer_1"]["reasoning"],
                reviewer_final=case["fresh_reviewer_1"]["final"],
                endpoint=gemma_endpoint, output_dir=lane / "01_extraction",
                seed=stable_seed(label), seed_label=label, model=GEMMA_MODEL,
            )

        write_json(output_dir / "status.json", {"state": "running", "stage": "conditional_fresh_r1_trace_extraction_batch", "updated_at": utc_now()})
        run_parallel(name="fresh_r1_trace_extract", jobs=r1_success_jobs, workers=gemma_workers, task=r1_extract)

        def r1_select(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits" / "reviewer_1_enhancement"
            packets = markdown_trace_packets(case["fresh_r1_extraction"])
            selector = run_gap_selector(
                problem=case["problem"], proof=case["proof"], packets=packets,
                endpoint=gemma_endpoint, output_dir=lane / "02_selector",
                seed=stable_seed(f"{seed_namespace}:{case['case_id']}:fresh_r1_trace_select"),
                seed_label=f"{seed_namespace}:{case['case_id']}:fresh_r1_trace_select",
                model=GEMMA_MODEL,
            )
            gaps = trace_real_gaps(case["fresh_r1_extraction"], selector)
            case["fresh_r1_selector"] = selector
            case["fresh_reviewer_1_trace_real_gaps"] = gaps
            if gaps:
                case["fresh_reviewer_1_effective_final"] = reviewer_1_failure_record(gaps[0])
                case["fresh_reviewer_1_effective_outcome"] = "FIRST_BREAK"
            else:
                case["fresh_reviewer_1_effective_final"] = case["fresh_reviewer_1"]["final"]
                case["fresh_reviewer_1_effective_outcome"] = "NO_FIRST_BREAK"

        write_json(output_dir / "status.json", {"state": "running", "stage": "conditional_fresh_r1_selector_batch", "updated_at": utc_now()})
        run_parallel(name="fresh_r1_trace_select", jobs=r1_success_jobs, workers=gemma_workers, task=r1_select)

    def gpu1_branch() -> None:
        def reviewer2_call(job: dict[str, Any]) -> None:
            case = job["case"]
            lane = output_dir / "cases" / case["case_id"] / "fresh_audits"
            case["fresh_reviewer_2"] = fresh_reviewer_2(
                case=case, endpoint=qwen_endpoint, output_dir=lane,
                seed_namespace=seed_namespace,
            )

        run_parallel(name="fresh_reviewer_2", jobs=jobs, workers=qwen_workers, task=reviewer2_call)

    write_json(output_dir / "status.json", {"state": "running", "stage": "split_gpu_post_resolver_audits", "updated_at": utc_now()})
    with concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="v098-split-gpu") as pool:
        futures = [pool.submit(gpu0_branch), pool.submit(gpu1_branch)]
        for future in futures:
            future.result()

    write_json(output_dir / "status.json", {"state": "running", "stage": "obligation_closure_batch", "updated_at": utc_now()})

    def closure_call(job: dict[str, Any]) -> None:
        case = job["case"]
        lane = output_dir / "cases" / case["case_id"] / "obligation_closure"
        case["closure_result"] = run_obligation_closure(
            case=case, endpoint=gemma_endpoint, output_dir=lane,
            seed_namespace=seed_namespace,
        )
        case["updated_ledger"] = build_updated_ledger(case)
        write_json(
            output_dir / "cases" / case["case_id"] / "updated_obligation_ledger.json",
            case["updated_ledger"],
        )
        case["gate"] = gate_decision(case)
        write_json(
            output_dir / "cases" / case["case_id"] / "gate_result.json",
            {
                "schema": "cognitive-well-v098-post-resolver-gate-result-v1",
                "case_id": case["case_id"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "proof_path": case["proof_path"],
                "proof_sha256": case["proof_sha256"],
                "resolver_trace_real_gaps": case["resolver_trace_real_gaps"],
                "fresh_reviewer_1_outcome": case["fresh_reviewer_1_effective_outcome"],
                "fresh_reviewer_1_trace_real_gaps": case["fresh_reviewer_1_trace_real_gaps"],
                "fresh_reviewer_2_outcome": case["fresh_reviewer_2"]["parsed"]["outcome"],
                "obligation_closure": case["closure_result"],
                "updated_obligation_ledger": case["updated_ledger"],
                **case["gate"],
                "completed_at": utc_now(),
            },
        )

    run_parallel(name="obligation_closure", jobs=jobs, workers=gemma_workers, task=closure_call)

    rows = [
        {
            "case_id": case["case_id"],
            "problem_id": case["problem_id"],
            "candidate_id": case["candidate_id"],
            "proof_path": case["proof_path"],
            "proof_sha256": case["proof_sha256"],
            "resolver_outcome": case["resolver_outcome"],
            "resolver_trace_candidate_count": int(case["resolver_trace_extraction"]["candidate_count"]),
            "resolver_trace_real_gap_count": len(case["resolver_trace_real_gaps"]),
            "fresh_reviewer_1_outcome": case["fresh_reviewer_1_effective_outcome"],
            "fresh_reviewer_1_trace_real_gap_count": len(case["fresh_reviewer_1_trace_real_gaps"]),
            "fresh_reviewer_2_outcome": case["fresh_reviewer_2"]["parsed"]["outcome"],
            "inherited_obligation_count": len(case["obligations"]),
            "unclosed_obligation_count": int(case["closure_result"]["unclosed_count"]),
            "updated_ledger_entry_count": int(case["updated_ledger"]["entry_count"]),
            "active_obligation_count": int(case["updated_ledger"]["active_count"]),
            **case["gate"],
            "gate_result_path": str((output_dir / "cases" / case["case_id"] / "gate_result.json").resolve()),
        }
        for case in cases
    ]
    summary = {
        "schema": "cognitive-well-v098-batched-post-resolver-gate-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "case_count": len(rows),
        "pass_count": sum(row["outcome"] == "PASS" for row in rows),
        "rejected_count": sum(row["outcome"] == "REJECTED" for row in rows),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "status.json", {"state": "completed", "stage": "done", "updated_at": utc_now()})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batched Resolver-trace, fresh-audit, and obligation-closure gate"
    )
    parser.add_argument("--source-run", action="append", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default=DEFAULT_GEMMA_ENDPOINT)
    parser.add_argument("--qwen-endpoint", default=DEFAULT_QWEN_ENDPOINT)
    parser.add_argument("--gemma-workers", type=int, default=4)
    parser.add_argument("--qwen-workers", type=int, default=4)
    parser.add_argument("--seed-namespace", default="v098")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run(
        source_runs=args.source_run,
        output_dir=args.output_dir,
        gemma_endpoint=args.gemma_endpoint,
        qwen_endpoint=args.qwen_endpoint,
        gemma_workers=args.gemma_workers,
        qwen_workers=args.qwen_workers,
        seed_namespace=args.seed_namespace,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
