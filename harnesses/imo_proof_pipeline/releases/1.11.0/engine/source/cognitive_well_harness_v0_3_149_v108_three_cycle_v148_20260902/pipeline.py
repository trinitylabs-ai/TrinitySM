from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import threading
import traceback
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827 import (
    run as v097,
)
from cognitive_well_harness_v0_3_140_clean_dual_trace_fusion_20260901.pipeline import (
    run_reviews,
)
from cognitive_well_harness_v0_3_148_review_trace_cumulative_synthesis_20260902.pipeline import (
    run_pipeline as run_v148,
)

from . import HARNESS_VERSION, REFINEMENT_CYCLE_COUNT


def _digest(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    v097.write_json(path, value)


def _write_status(output_dir: Path, *, state: str, stage: str, **extra: Any) -> None:
    _write_json(
        output_dir / "status.json",
        {
            "state": state,
            "stage": stage,
            "updated_at": v097.utc_now(),
            **extra,
        },
    )


def _validate_raw_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {str(row.get("candidate_id") or ""): row for row in rows}
    expected = list(v097.RAW_CANDIDATE_IDS)
    if set(by_id) != set(expected) or len(by_id) != len(rows):
        raise ValueError("raw/lazy phase does not contain the frozen four candidates")
    ordered: list[dict[str, Any]] = []
    for candidate_id in expected:
        row = by_id[candidate_id]
        proof_path = Path(str(row.get("checked_proof_path") or "")).resolve()
        if not proof_path.is_file():
            raise FileNotFoundError(proof_path)
        proof = proof_path.read_text(encoding="utf-8").strip()
        if not proof:
            raise ValueError(f"empty checked proof: {candidate_id}")
        recorded_hash = str(row.get("checked_proof_sha256") or "")
        actual_hash = v097.sha256_text(proof)
        if recorded_hash and recorded_hash != actual_hash:
            raise ValueError(f"checked proof hash drift: {candidate_id}")
        ordered.append(
            {
                **row,
                "candidate_id": candidate_id,
                "checked_proof_path": str(proof_path),
                "checked_proof_sha256": actual_hash,
            }
        )
    return ordered


def load_raw_lazy_source(
    *, source_run: Path, problem: dict[str, Any]
) -> tuple[dict[str, Any], Path]:
    source = source_run.resolve()
    candidates = (
        source / "result.json",
        source / "phase_1_raw_lazy" / "result.json",
        source / "01_raw_lazy_enhanced_resolve" / "phase_1_raw_lazy" / "result.json",
        source / "01_raw_lazy_four_proofs" / "result.json",
    )
    matches = [path for path in candidates if path.is_file()]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one raw-lazy result under {source}, found {matches}"
        )
    result_path = matches[0].resolve()
    result = _read_object(result_path)
    if result.get("state") != "completed" or "raw-lazy-result" not in str(
        result.get("schema") or ""
    ):
        raise ValueError(f"not a completed raw-lazy result: {result_path}")
    source_problem = dict(result.get("problem") or {})
    if str(source_problem.get("problem_id") or "") != str(problem["problem_id"]):
        raise ValueError("raw-lazy source problem identity drift")
    if str(source_problem.get("problem_sha256") or "") != str(problem["sha256"]):
        raise ValueError("raw-lazy source problem statement drift")
    result["results"] = _validate_raw_rows(list(result.get("results") or []))
    return result, result_path


def run_raw_lazy_phase(
    *,
    problem: dict[str, Any],
    output_dir: Path,
    gemma_endpoint: str,
) -> dict[str, Any]:
    """Run the frozen v108/v097 raw-lazy front end without its old reviewer phase."""

    destination = output_dir.resolve()
    result_path = destination / "result.json"
    if result_path.is_file():
        saved = _read_object(result_path)
        if saved.get("state") == "completed":
            saved["results"] = _validate_raw_rows(list(saved.get("results") or []))
            return saved

    destination.mkdir(parents=True, exist_ok=True)
    system_prompt, user_prompt, prompt_identity = v097.build_frozen_raw_prompts(
        problem
    )
    (destination / "cold_system_prompt.txt").write_text(
        system_prompt, encoding="utf-8"
    )
    (destination / "cold_user_prompt.txt").write_text(
        user_prompt, encoding="utf-8"
    )
    manifest = v097.phase_one_manifest(
        problem=problem,
        prompt_identity=prompt_identity,
        gpu0_gemma_endpoint=gemma_endpoint,
    )
    manifest["composite_parent_version"] = HARNESS_VERSION
    manifest["downstream_v097_enhanced_pipeline_enabled"] = False
    _write_json(destination / "manifest.json", manifest)

    runtime = v097.GPU0FourSlotStageRuntime(
        v097.RuntimeConfig(gemma_endpoint=gemma_endpoint)
    )
    status_lock = threading.Lock()
    total = len(v097.RAW_CANDIDATES)

    def phase_status(
        stage: str,
        completed: list[dict[str, Any]],
        failures: list[dict[str, str]],
    ) -> None:
        with status_lock:
            _write_json(
                destination / "status.json",
                {
                    "state": "running",
                    "stage": stage,
                    "completed_count": len(completed),
                    "failed": failures,
                    "total": total,
                    "device": "gpu0",
                    "updated_at": v097.utc_now(),
                },
            )

    source_rows = [
        {
            "problem_number": int(problem["problem_number"]),
            "candidate_id": str(spec["candidate_id"]),
            "problem": problem,
            "spec": dict(spec),
        }
        for spec in v097.RAW_CANDIDATES
    ]
    cold_rows = v097.run_parallel_stage(
        rows=source_rows,
        stage="raw_generation_batch_of_4",
        status_writer=phase_status,
        worker=lambda row: v097.run_cold_candidate(
            runtime=runtime,
            problem=row["problem"],
            output_dir=destination,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            spec=row["spec"],
        ),
    )
    lazy_rows = v097.run_parallel_stage(
        rows=cold_rows,
        stage="lazy_check_batch_of_4",
        status_writer=phase_status,
        worker=lambda row: v097.run_lazy_check(
            runtime=runtime,
            output_dir=destination / f"p{int(problem['problem_number'])}",
            row=row,
        ),
    )
    final_rows = v097.run_parallel_stage(
        rows=lazy_rows,
        stage="conditional_in_place_expansion_batch",
        status_writer=phase_status,
        worker=lambda row: {
            **v097.run_lazy_resolve(
                runtime=runtime,
                problem=str(problem["claim"]),
                output_dir=destination / f"p{int(problem['problem_number'])}",
                row=row,
            ),
            "problem_number": int(problem["problem_number"]),
            "problem_id": str(problem["problem_id"]),
        },
    )
    final_rows = _validate_raw_rows(final_rows)
    result = {
        **manifest,
        "schema": "cognitive-well-v0149-frozen-v108-raw-lazy-result-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "results": final_rows,
        "lazy_resolve_count": sum(
            bool(row["lazy_resolve_invoked"]) for row in final_rows
        ),
        "old_review_fusion_resolver_invoked": False,
        "completed_at": v097.utc_now(),
    }
    _write_json(result_path, result)
    _write_status(destination, state="completed", stage="raw_lazy_four_proofs")
    return result


def _candidate_record(
    *, candidate_id: str, proof_path: Path, cycle: int
) -> dict[str, Any]:
    source = proof_path.resolve()
    proof = source.read_text(encoding="utf-8").strip()
    if not proof:
        raise ValueError(f"empty input proof for {candidate_id} cycle {cycle}")
    return {
        "schema": "cognitive-well-v0149-v0148-candidate-adapter-v1",
        "candidate_id": candidate_id,
        "proof": proof,
        "proof_path": str(source),
        "proof_sha256": v097.sha256_text(proof),
        "refinement_cycle": cycle,
        "external_information_injection": False,
    }


def _normalized_text(value: str) -> str:
    return " ".join(value.split())


def _artifact_metrics(proof: str) -> dict[str, Any]:
    lines = proof.splitlines()
    words = re.findall(r"\S+", proof)
    paragraphs = [
        _normalized_text(value)
        for value in re.split(r"\n\s*\n", proof)
        if len(_normalized_text(value)) >= 30
    ]
    paragraph_positions: dict[str, list[int]] = {}
    for index, paragraph in enumerate(paragraphs, start=1):
        paragraph_positions.setdefault(paragraph, []).append(index)
    duplicate_paragraphs = [
        {"positions": positions, "text": paragraph}
        for paragraph, positions in paragraph_positions.items()
        if len(positions) > 1
    ]
    ngram_positions: dict[str, list[int]] = {}
    width = 12
    for index in range(max(0, len(words) - width + 1)):
        ngram = " ".join(words[index : index + width])
        ngram_positions.setdefault(ngram, []).append(index)
    repeated_ngrams = []
    for ngram, positions in ngram_positions.items():
        nonoverlapping: list[int] = []
        for position in positions:
            if not nonoverlapping or position - nonoverlapping[-1] >= width:
                nonoverlapping.append(position)
        if len(nonoverlapping) > 1:
            repeated_ngrams.append(
                {
                    "word_positions": nonoverlapping,
                    "text": ngram,
                    "sha256": v097.sha256_text(ngram),
                }
            )
    lazy_patterns = {
        "routine": r"\b(?:routine|routinely)\b",
        "straightforward": r"\bstraightforward\b",
        "clearly": r"\bclearly\b",
        "immediate": r"\b(?:immediate|immediately)\b",
        "after_simplification": r"\bafter (?:a )?(?:direct )?simplification\b",
        "one_obtains": r"\b(?:one|we) obtains?\b",
    }
    lower = proof.lower()
    tail = [line.strip() for line in lines if line.strip()][-8:]
    conclusion_like = [
        line
        for line in tail
        if re.search(r"\b(?:thus|hence|therefore|proves?|proved)\b", line.lower())
    ]
    transport_patterns = {
        "cw_block": r"<!--\s*CW_BLOCK",
        "start_block": r"START_BLOCK:",
        "end_block": r"END_BLOCK:",
        "trace_id": r"TRACE_ID:",
        "packet_id": r"\bR[12]TG[0-9]+\b",
    }
    return {
        "character_count": len(proof),
        "line_count": len(lines),
        "word_count": len(words),
        "paragraph_count": len(paragraphs),
        "exact_duplicate_paragraph_count": len(duplicate_paragraphs),
        "exact_duplicate_paragraphs": duplicate_paragraphs[:20],
        "repeated_12_word_span_count": len(repeated_ngrams),
        "repeated_12_word_spans": repeated_ngrams[:20],
        "lazy_connection_counts": {
            label: len(re.findall(pattern, lower))
            for label, pattern in lazy_patterns.items()
        },
        "ending_conclusion_like_line_count": len(conclusion_like),
        "ending_conclusion_like_lines": conclusion_like,
        "transport_marker_hits": {
            label: bool(re.search(pattern, proof))
            for label, pattern in transport_patterns.items()
        },
    }


def audit_cycle_artifacts(
    *, input_proof: str, output_proof: str, v148_run_dir: Path
) -> dict[str, Any]:
    before = _artifact_metrics(input_proof)
    after = _artifact_metrics(output_proof)
    lazy_delta = {
        key: int(after["lazy_connection_counts"][key])
        - int(before["lazy_connection_counts"][key])
        for key in after["lazy_connection_counts"]
    }
    synthesis_summary_path = (
        v148_run_dir
        / "02_cumulative_synthesis_phase"
        / "06_synthesis_iterations"
        / "summary.json"
    )
    synthesis_summary = _read_object(synthesis_summary_path)
    patch_rows = [
        dict(row.get("patch_audit") or {})
        for row in synthesis_summary.get("iterations") or []
    ]
    patch_preservation = {
        "iteration_count": len(patch_rows),
        "all_prefixes_preserved": all(
            row.get("prefix_preserved_byte_for_byte") is True for row in patch_rows
        ),
        "all_suffixes_preserved": all(
            row.get("suffix_preserved_byte_for_byte") is True for row in patch_rows
        ),
    }
    deltas = {
        "character_count": after["character_count"] - before["character_count"],
        "line_count": after["line_count"] - before["line_count"],
        "word_count": after["word_count"] - before["word_count"],
        "exact_duplicate_paragraph_count": (
            after["exact_duplicate_paragraph_count"]
            - before["exact_duplicate_paragraph_count"]
        ),
        "repeated_12_word_span_count": (
            after["repeated_12_word_span_count"]
            - before["repeated_12_word_span_count"]
        ),
        "ending_conclusion_like_line_count": (
            after["ending_conclusion_like_line_count"]
            - before["ending_conclusion_like_line_count"]
        ),
        "lazy_connection_counts": lazy_delta,
    }
    reasons = []
    if any(after["transport_marker_hits"].values()):
        reasons.append("transport_marker_present")
    if deltas["exact_duplicate_paragraph_count"] > 0:
        reasons.append("new_exact_duplicate_paragraph")
    if deltas["repeated_12_word_span_count"] > 0:
        reasons.append("new_repeated_long_span")
    if deltas["ending_conclusion_like_line_count"] > 0:
        reasons.append("additional_conclusion_like_ending")
    if any(value > 0 for value in lazy_delta.values()):
        reasons.append("additional_lazy_connection_language")
    if before["word_count"] and after["word_count"] / before["word_count"] > 1.75:
        reasons.append("proof_word_count_growth_over_75_percent")
    if not patch_preservation["all_prefixes_preserved"]:
        reasons.append("patch_prefix_preservation_failure")
    if not patch_preservation["all_suffixes_preserved"]:
        reasons.append("patch_suffix_preservation_failure")
    return {
        "schema": "cognitive-well-v0149-cycle-artifact-audit-v1",
        "state": "completed",
        "mutation_performed": False,
        "before": before,
        "after": after,
        "deltas": deltas,
        "patch_preservation": patch_preservation,
        "requires_attention": bool(reasons),
        "attention_reasons": reasons,
        "semantic_equivalence_or_cleanup_attempted": False,
    }


def build_terminal_obligation_ledger(
    *,
    problem_id: str,
    candidate_id: str,
    proof_path: Path,
    reviews: dict[str, Any],
) -> dict[str, Any]:
    """Deterministically materialize visible terminal-review failures."""

    proof = proof_path.read_text(encoding="utf-8").strip()
    specifications = {
        "reviewer_1": {
            "failure": "FIRST_BREAK",
            "target": ("claim", "location"),
            "defect": ("missing_or_invalid_link", "why_not_follow"),
            "minimum": ("minimum_requirement",),
        },
        "reviewer_2": {
            "failure": "ADVERSARIAL_BREAK",
            "target": ("target_claim", "location"),
            "defect": ("attack_type", "witness", "verification", "why_decisive"),
            "minimum": ("minimum_requirement",),
        },
        "reviewer_3": {
            "failure": "CERTIFICATION_FAILURE",
            "target": ("critical_obligation",),
            "defect": ("why_completion_fails", "impact_on_conclusion"),
            "minimum": ("minimum_required_lemma",),
        },
    }
    materialized: list[dict[str, Any]] = []
    for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
        result = dict(reviews["results"][role])
        parsed = dict(result.get("parsed") or {})
        outcome = str(parsed.get("outcome") or result.get("outcome") or "")
        spec = specifications[role]
        if outcome != spec["failure"]:
            continue
        fields = dict(parsed.get("fields") or {})

        def joined(keys: tuple[str, ...]) -> str:
            return " | ".join(
                _normalized_text(str(fields[key]))
                for key in keys
                if str(fields.get(key) or "").strip()
            )

        target = joined(spec["target"])
        defect = joined(spec["defect"])
        minimum = joined(spec["minimum"])
        if not target and not defect:
            raise ValueError(f"{role} failure has no ledger obligation")
        signature = _digest(
            {
                "target": target,
                "defect": defect,
                "minimum_requirement": minimum,
            }
        )
        materialized.append(
            {
                "source": f"terminal_{role}",
                "source_outcome": outcome,
                "status": "ACTIVE",
                "target": target,
                "defect": defect,
                "minimum_requirement": minimum,
                "visible_review_sha256": v097.sha256_text(
                    str(reviews["visible"][role]).strip()
                ),
                "signature_sha256": signature,
            }
        )

    unique: list[dict[str, Any]] = []
    by_signature: dict[str, dict[str, Any]] = {}
    for row in materialized:
        signature = str(row["signature_sha256"])
        existing = by_signature.get(signature)
        if existing is not None:
            existing["exact_duplicate_sources_removed"].append(row["source"])
            continue
        entry = {
            **row,
            "obligation_id": f"OB{len(unique) + 1}",
            "exact_duplicate_sources_removed": [],
        }
        by_signature[signature] = entry
        unique.append(entry)
    return {
        "schema": "cognitive-well-v0149-terminal-obligation-ledger-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "problem_id": problem_id,
        "candidate_id": candidate_id,
        "proof_path": str(proof_path.resolve()),
        "proof_sha256": v097.sha256_text(proof),
        "construction": "deterministic_from_visible_terminal_review_failures",
        "semantic_merge_performed": False,
        "model_call_during_ledger_construction": False,
        "entry_count": len(unique),
        "active_count": len(unique),
        "entries": unique,
        "outcome": "AUDIT_PASS" if not unique else "UNRESOLVED_OBLIGATIONS",
        "promotion_allowed_without_independent_audit": False,
        "completed_at": v097.utc_now(),
    }


def run_terminal_audit_and_ledger(
    *,
    problem: dict[str, Any],
    terminal_candidates: list[dict[str, Any]],
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    candidate_workers: int,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    summary_path = destination / "summary.json"
    if summary_path.is_file():
        saved = _read_object(summary_path)
        if saved.get("state") == "completed":
            return saved
    destination.mkdir(parents=True, exist_ok=True)
    by_id = {str(row["candidate_id"]): row for row in terminal_candidates}
    if set(by_id) != set(v097.RAW_CANDIDATE_IDS):
        raise ValueError("terminal audit did not receive the frozen four candidates")
    rows_by_id: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, str]] = []
    status_lock = threading.Lock()

    def audit_one(candidate_id: str) -> dict[str, Any]:
        candidate = by_id[candidate_id]
        candidate_root = destination / "candidates" / candidate_id
        proof_path = Path(str(candidate["proof_path"])).resolve()
        proof = proof_path.read_text(encoding="utf-8").strip()
        proof_sha256 = v097.sha256_text(proof)
        ledger_path = candidate_root / "02_obligation_ledger.json"
        reviews_path = candidate_root / "01_reviews" / "summary.json"
        if ledger_path.is_file() and reviews_path.is_file():
            ledger = _read_object(ledger_path)
            if ledger.get("proof_sha256") != proof_sha256:
                raise ValueError(f"terminal audit proof drift: {candidate_id}")
            reviews = _read_object(reviews_path)
        else:
            reviews = run_reviews(
                problem_id=str(problem["problem_id"]),
                candidate_id=candidate_id,
                problem=str(problem["claim"]),
                proof=proof,
                problem_path=Path(problem["path"]),
                proof_path=proof_path,
                output_dir=candidate_root / "01_reviews",
                gemma_endpoint=gemma_endpoint,
                qwen_endpoint=qwen_endpoint,
                master_seed=master_seed,
                seed_namespace=f"{seed_namespace}:terminal-audit:{candidate_id}",
            )
            _write_json(reviews_path, reviews)
            ledger = build_terminal_obligation_ledger(
                problem_id=str(problem["problem_id"]),
                candidate_id=candidate_id,
                proof_path=proof_path,
                reviews=reviews,
            )
            _write_json(ledger_path, ledger)
        return {
            "candidate_id": candidate_id,
            "proof_path": str(proof_path),
            "proof_sha256": proof_sha256,
            "review_outcomes": {
                role: (
                    reviews["results"][role].get("parsed", {}).get("outcome")
                    or reviews["results"][role].get("outcome")
                )
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "ledger_path": str(ledger_path.resolve()),
            "active_obligation_count": int(ledger["active_count"]),
            "outcome": ledger["outcome"],
        }

    _write_status(
        destination,
        state="running",
        stage="terminal_three_review_audit",
        completed_count=0,
        total=4,
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=candidate_workers) as executor:
        futures = {
            executor.submit(audit_one, candidate_id): candidate_id
            for candidate_id in v097.RAW_CANDIDATE_IDS
        }
        for future in concurrent.futures.as_completed(futures):
            candidate_id = futures[future]
            try:
                rows_by_id[candidate_id] = future.result()
                with status_lock:
                    _write_status(
                        destination,
                        state="running",
                        stage="terminal_three_review_audit",
                        completed_count=len(rows_by_id),
                        total=4,
                    )
            except Exception as error:
                failures.append(
                    {
                        "candidate_id": candidate_id,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
    if failures:
        _write_status(
            destination,
            state="failed_closed",
            stage="terminal_three_review_audit",
            failures=failures,
        )
        raise RuntimeError(f"terminal audit failures: {failures}")
    rows = [rows_by_id[candidate_id] for candidate_id in v097.RAW_CANDIDATE_IDS]
    summary = {
        "schema": "cognitive-well-v0149-terminal-audit-ledger-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "problem_id": problem["problem_id"],
        "candidate_count": 4,
        "audit_timing": "after_v0148_cycle_3_only",
        "additional_resolve_triggered": False,
        "total_active_obligation_count": sum(
            int(row["active_obligation_count"]) for row in rows
        ),
        "pass_count": sum(row["outcome"] == "AUDIT_PASS" for row in rows),
        "rows": rows,
        "completed_at": v097.utc_now(),
    }
    _write_json(summary_path, summary)
    _write_status(
        destination,
        state="completed",
        stage="terminal_obligation_ledger",
        total_active_obligation_count=summary["total_active_obligation_count"],
        pass_count=summary["pass_count"],
    )
    return summary


def run_v148_cycle(
    *,
    cycle: int,
    sources: list[dict[str, Any]],
    problem_json: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    master_seed: int,
    seed_namespace: str,
    candidate_workers: int,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    summary_path = destination / "summary.json"
    if summary_path.is_file():
        saved = _read_object(summary_path)
        if saved.get("state") == "completed":
            rows = list(saved.get("candidates") or [])
            if [str(row["candidate_id"]) for row in rows] != list(
                v097.RAW_CANDIDATE_IDS
            ):
                raise ValueError(f"cycle {cycle} candidate order drift")
            for row in rows:
                proof_path = Path(str(row["proof_path"])).resolve()
                proof = proof_path.read_text(encoding="utf-8").strip()
                if v097.sha256_text(proof) != str(row["proof_sha256"]):
                    raise ValueError(
                        f"cycle {cycle} proof hash drift: {row['candidate_id']}"
                    )
            return saved

    destination.mkdir(parents=True, exist_ok=True)
    by_id = {str(row["candidate_id"]): row for row in sources}
    if set(by_id) != set(v097.RAW_CANDIDATE_IDS):
        raise ValueError(f"cycle {cycle} did not receive the frozen four candidates")
    status_lock = threading.Lock()
    completed_ids: list[str] = []

    def run_one(candidate_id: str) -> dict[str, Any]:
        source = by_id[candidate_id]
        candidate_root = destination / "candidates" / candidate_id
        adapter_path = candidate_root / "input_candidate.json"
        adapter = _candidate_record(
            candidate_id=candidate_id,
            proof_path=Path(str(source["proof_path"])),
            cycle=cycle,
        )
        _write_json(adapter_path, adapter)
        v148_dir = candidate_root / "v0148"
        child = run_v148(
            problem_json=problem_json,
            candidate_result=adapter_path,
            output_dir=v148_dir,
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=(
                f"{seed_namespace}:cycle-{cycle:02d}:{candidate_id}"
            ),
            dry_run=False,
        )
        if child.get("state") != "completed":
            raise RuntimeError(f"v148 did not complete for cycle {cycle} {candidate_id}")
        result = _read_object(v148_dir / "03_result.json")
        output_proof = Path(str(result["proof_path"])).read_text(
            encoding="utf-8"
        ).strip()
        artifact_audit = audit_cycle_artifacts(
            input_proof=str(adapter["proof"]),
            output_proof=output_proof,
            v148_run_dir=v148_dir,
        )
        artifact_audit_path = candidate_root / "cycle_artifact_audit.json"
        _write_json(artifact_audit_path, artifact_audit)
        row = {
            "candidate_id": candidate_id,
            "cycle": cycle,
            "input_proof_path": adapter["proof_path"],
            "input_proof_sha256": adapter["proof_sha256"],
            "v148_run_dir": str(v148_dir),
            "proof_path": str(Path(str(result["proof_path"])).resolve()),
            "proof_sha256": str(result["proof_sha256"]),
            "fusion_verdict": result["fusion_verdict"],
            "tracing_memory_packet_count": result[
                "tracing_memory_packet_count"
            ],
            "synthesis_iteration_count": result["synthesis_iteration_count"],
            "packet_batches": result["packet_batches"],
            "artifact_audit_path": str(artifact_audit_path.resolve()),
            "artifact_requires_attention": artifact_audit["requires_attention"],
            "artifact_attention_reasons": artifact_audit["attention_reasons"],
        }
        with status_lock:
            completed_ids.append(candidate_id)
            _write_status(
                destination,
                state="running",
                stage="v0148_candidate_batch",
                cycle=cycle,
                completed_candidate_ids=sorted(completed_ids),
                completed_count=len(completed_ids),
                total=4,
            )
        return row

    _write_status(
        destination,
        state="running",
        stage="v0148_candidate_batch",
        cycle=cycle,
        completed_candidate_ids=[],
        completed_count=0,
        total=4,
    )
    failures: list[dict[str, str]] = []
    rows_by_id: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=candidate_workers
    ) as executor:
        futures = {
            executor.submit(run_one, candidate_id): candidate_id
            for candidate_id in v097.RAW_CANDIDATE_IDS
        }
        for future in concurrent.futures.as_completed(futures):
            candidate_id = futures[future]
            try:
                rows_by_id[candidate_id] = future.result()
            except Exception as error:
                failures.append(
                    {
                        "candidate_id": candidate_id,
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
    if failures:
        _write_status(
            destination,
            state="failed_closed",
            stage="v0148_candidate_batch",
            cycle=cycle,
            failures=failures,
        )
        raise RuntimeError(f"v148 cycle {cycle} failures: {failures}")
    ordered = [rows_by_id[candidate_id] for candidate_id in v097.RAW_CANDIDATE_IDS]
    summary = {
        "schema": "cognitive-well-v0149-v0148-cycle-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "cycle": cycle,
        "candidate_count": 4,
        "candidate_order": list(v097.RAW_CANDIDATE_IDS),
        "candidates": ordered,
        "artifact_attention_candidate_count": sum(
            bool(row["artifact_requires_attention"]) for row in ordered
        ),
        "artifact_cleanup_performed": False,
        "completed_at": v097.utc_now(),
    }
    _write_json(summary_path, summary)
    _write_status(
        destination,
        state="completed",
        stage="v0148_cycle",
        cycle=cycle,
        completed_candidate_ids=list(v097.RAW_CANDIDATE_IDS),
    )
    return summary


def run_pipeline(
    *,
    problem_file: Path,
    problem_id: str,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    problem_number: int | None = None,
    candidate_workers: int = 4,
    master_seed: int = 20260902,
    seed_namespace: str = "v0149",
    raw_lazy_source_run: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    gemma_endpoint = gemma_endpoint.rstrip("/")
    qwen_endpoint = qwen_endpoint.rstrip("/")
    if not gemma_endpoint or not qwen_endpoint or gemma_endpoint == qwen_endpoint:
        raise ValueError("distinct nonempty Gemma and Qwen endpoints are required")
    if not 1 <= candidate_workers <= 4:
        raise ValueError("candidate_workers must be between one and four")

    problem = v097.normalize_problem_input(
        source_path=problem_file,
        output_dir=destination / "00_problem",
        problem_id_override=problem_id,
        problem_number_override=problem_number,
    )
    raw_source_result_path: Path | None = None
    if raw_lazy_source_run is not None:
        _, raw_source_result_path = load_raw_lazy_source(
            source_run=raw_lazy_source_run, problem=problem
        )
    run_input = {
        "problem_source_path": str(Path(problem["source_path"]).resolve()),
        "problem_source_sha256": problem["source_sha256"],
        "problem_id": problem["problem_id"],
        "problem_number": problem["problem_number"],
        "gemma_endpoint": gemma_endpoint,
        "qwen_endpoint": qwen_endpoint,
        "candidate_workers": candidate_workers,
        "master_seed": master_seed,
        "seed_namespace": seed_namespace,
        "raw_front_end": "frozen_v108_v097_raw_lazy",
        "refinement_module": "v0.3.148",
        "refinement_cycle_count": REFINEMENT_CYCLE_COUNT,
        "raw_lazy_source_run": (
            str(raw_lazy_source_run.resolve()) if raw_lazy_source_run else None
        ),
        "raw_lazy_source_result": (
            str(raw_source_result_path) if raw_source_result_path else None
        ),
        "raw_lazy_source_result_sha256": (
            v097.file_sha256(raw_source_result_path)
            if raw_source_result_path is not None
            else None
        ),
        "external_information_injection": False,
        "cross_problem_information_injection": False,
        "historical_problem_lookup": False,
    }
    input_sha256 = _digest(run_input)
    summary_path = destination / "summary.json"
    if summary_path.is_file():
        saved = _read_object(summary_path)
        if saved.get("input_sha256") != input_sha256:
            raise ValueError("refusing to reuse v149 output after input drift")
        if saved.get("state") in {"completed", "dry_run_completed"}:
            return saved

    manifest = {
        "schema": "cognitive-well-v0149-three-cycle-v0148-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": v097.utc_now(),
        "input_sha256": input_sha256,
        "source": run_input,
        "pipeline": {
            "raw_candidate_ids": list(v097.RAW_CANDIDATE_IDS),
            "raw_candidate_temperatures": [
                float(row["temperature"]) for row in v097.RAW_CANDIDATES
            ],
            "raw_lazy_generator": "frozen_v108_v097_front_end",
            "raw_lazy_resume_supported": True,
            "refinement_cycles": REFINEMENT_CYCLE_COUNT,
            "refinement_module_each_cycle": "v0.3.148",
            "cycle_output_becomes_next_cycle_input": True,
            "post_cycle_artifact_audit": "deterministic_non_mutating",
            "automatic_semantic_cleanup_between_cycles": False,
            "old_v097_enhanced_review_fusion_resolver": False,
            "old_v108_post_resolver_obligation_ledger": False,
            "old_v108_second_resolve": False,
            "old_v108_third_resolve": False,
            "old_v108_two_proof_selection": False,
            "old_v108_lemma_memory_pipeline": False,
            "terminal_three_review_audit_after_cycle_3": True,
            "terminal_obligation_ledger": True,
            "terminal_ledger_triggers_additional_resolve": False,
            "external_scoring": "outside_solver_only",
        },
        "information_contract": {
            "same_problem_solver_artifacts_only": True,
            "gold_solution_access": False,
            "codex_grade_access": False,
            "external_scorer_feedback_access": False,
            "cross_problem_information_access": False,
            "historical_problem_artifact_access": False,
            "problem_specific_prompt_or_patch": False,
        },
    }
    manifest_path = destination / "manifest.json"
    if manifest_path.is_file():
        if _read_object(manifest_path).get("input_sha256") != input_sha256:
            raise ValueError("v149 manifest input drift")
    else:
        _write_json(manifest_path, manifest)
    _write_json(
        destination / "leak_audit.json",
        {
            "state": "passed",
            "problem_statement_is_only_external_mathematical_input": True,
            "solver_internal_same_problem_chaining_only": True,
            "gold_supplied": False,
            "codex_grades_supplied": False,
            "external_scorer_feedback_supplied": False,
            "cross_problem_information_supplied": False,
            "historical_problem_material_supplied": False,
            "problem_specific_guidance_supplied": False,
        },
    )

    if dry_run:
        summary = {
            "schema": "cognitive-well-v0149-dry-run-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "input_sha256": input_sha256,
            "problem_id": problem["problem_id"],
            "candidate_ids": list(v097.RAW_CANDIDATE_IDS),
            "refinement_cycle_count": REFINEMENT_CYCLE_COUNT,
            "v148_candidate_run_count": 4 * REFINEMENT_CYCLE_COUNT,
        }
        _write_json(summary_path, summary)
        _write_status(destination, state="dry_run_completed", stage="validation")
        return summary

    try:
        if raw_lazy_source_run is None:
            _write_status(destination, state="running", stage="raw_lazy_four_proofs")
            raw = run_raw_lazy_phase(
                problem=problem,
                output_dir=destination / "01_raw_lazy_four_proofs",
                gemma_endpoint=gemma_endpoint,
            )
        else:
            _write_status(
                destination, state="running", stage="raw_lazy_source_import"
            )
            raw, imported_result_path = load_raw_lazy_source(
                source_run=raw_lazy_source_run, problem=problem
            )
            _write_json(
                destination / "01_raw_lazy_source_import.json",
                {
                    "schema": "cognitive-well-v0149-raw-lazy-source-import-v1",
                    "state": "completed",
                    "source_run": str(raw_lazy_source_run.resolve()),
                    "source_result_path": str(imported_result_path),
                    "source_result_sha256": v097.file_sha256(imported_result_path),
                    "problem_id": problem["problem_id"],
                    "candidate_ids": list(v097.RAW_CANDIDATE_IDS),
                    "model_calls": 0,
                },
            )
        sources = [
            {
                "candidate_id": row["candidate_id"],
                "proof_path": row["checked_proof_path"],
                "proof_sha256": row["checked_proof_sha256"],
            }
            for row in raw["results"]
        ]
        cycle_summaries: list[dict[str, Any]] = []
        for cycle in range(1, REFINEMENT_CYCLE_COUNT + 1):
            _write_status(
                destination,
                state="running",
                stage="v0148_refinement_cycle",
                cycle=cycle,
                total_cycles=REFINEMENT_CYCLE_COUNT,
            )
            cycle_summary = run_v148_cycle(
                cycle=cycle,
                sources=sources,
                problem_json=Path(problem["path"]),
                output_dir=(
                    destination / "02_v0148_cycles" / f"cycle_{cycle:02d}"
                ),
                gemma_endpoint=gemma_endpoint,
                qwen_endpoint=qwen_endpoint,
                master_seed=master_seed,
                seed_namespace=seed_namespace,
                candidate_workers=candidate_workers,
            )
            cycle_summaries.append(cycle_summary)
            sources = [
                {
                    "candidate_id": row["candidate_id"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                }
                for row in cycle_summary["candidates"]
            ]

        portfolio_dir = destination / "03_terminal_four_proof_portfolio"
        terminal_rows: list[dict[str, Any]] = []
        for source in sources:
            candidate_id = str(source["candidate_id"])
            source_path = Path(str(source["proof_path"])).resolve()
            proof = source_path.read_text(encoding="utf-8").strip()
            candidate_dir = portfolio_dir / "candidates" / candidate_id
            proof_path = candidate_dir / "proof.md"
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            proof_path.write_text(proof + "\n", encoding="utf-8")
            result = {
                "schema": "cognitive-well-v0149-terminal-candidate-v1",
                "candidate_id": candidate_id,
                "proof": proof,
                "proof_path": str(proof_path.resolve()),
                "proof_sha256": v097.sha256_text(proof),
                "source_v148_proof_path": str(source_path),
                "refinement_cycles_completed": REFINEMENT_CYCLE_COUNT,
                "promotion_allowed_without_independent_audit": False,
            }
            _write_json(candidate_dir / "candidate_result.json", result)
            terminal_rows.append(result)
        portfolio = {
            "schema": "cognitive-well-v0149-terminal-four-proof-portfolio-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "problem_id": problem["problem_id"],
            "candidate_count": 4,
            "candidate_order": list(v097.RAW_CANDIDATE_IDS),
            "candidates": terminal_rows,
            "promotion_allowed_without_independent_audit": False,
            "completed_at": v097.utc_now(),
        }
        _write_json(portfolio_dir / "summary.json", portfolio)
        _write_status(
            destination,
            state="running",
            stage="terminal_audit_and_obligation_ledger",
        )
        terminal_audit = run_terminal_audit_and_ledger(
            problem=problem,
            terminal_candidates=terminal_rows,
            output_dir=destination / "04_terminal_audit_ledger",
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            master_seed=master_seed,
            seed_namespace=seed_namespace,
            candidate_workers=candidate_workers,
        )
        summary = {
            "schema": "cognitive-well-v0149-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "completed",
            "outcome": "FOUR_PROOFS_REFINED_THROUGH_THREE_V148_CYCLES",
            "completed_at": v097.utc_now(),
            "input_sha256": input_sha256,
            "problem_id": problem["problem_id"],
            "candidate_count": 4,
            "refinement_cycle_count": REFINEMENT_CYCLE_COUNT,
            "v148_candidate_run_count": 4 * REFINEMENT_CYCLE_COUNT,
            "cycle_summaries": [
                str(
                    destination
                    / "02_v0148_cycles"
                    / f"cycle_{cycle:02d}"
                    / "summary.json"
                )
                for cycle in range(1, REFINEMENT_CYCLE_COUNT + 1)
            ],
            "artifact_attention_candidate_counts_by_cycle": [
                int(row["artifact_attention_candidate_count"])
                for row in cycle_summaries
            ],
            "automatic_semantic_cleanup_between_cycles": False,
            "terminal_portfolio_path": str(
                (portfolio_dir / "summary.json").resolve()
            ),
            "terminal_candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                }
                for row in terminal_rows
            ],
            "terminal_audit_ledger_path": str(
                (destination / "04_terminal_audit_ledger" / "summary.json").resolve()
            ),
            "terminal_audit_pass_count": terminal_audit["pass_count"],
            "terminal_active_obligation_count": terminal_audit[
                "total_active_obligation_count"
            ],
            "additional_resolve_after_terminal_audit": False,
            "external_scoring_performed": False,
            "promotion_allowed_without_independent_audit": False,
        }
        _write_json(summary_path, summary)
        _write_status(
            destination,
            state="completed",
            stage="terminal_four_proof_portfolio",
            terminal_portfolio_path=summary["terminal_portfolio_path"],
            external_scoring_performed=False,
        )
        return summary
    except Exception as error:
        _write_status(
            destination,
            state="failed_closed",
            stage="exception",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
        )
        raise


__all__ = [
    "audit_cycle_artifacts",
    "build_terminal_obligation_ledger",
    "load_raw_lazy_source",
    "run_pipeline",
    "run_raw_lazy_phase",
    "run_terminal_audit_and_ledger",
    "run_v148_cycle",
]
