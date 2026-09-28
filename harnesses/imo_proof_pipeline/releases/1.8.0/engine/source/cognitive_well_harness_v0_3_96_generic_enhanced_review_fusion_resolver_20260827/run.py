from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
from copy import deepcopy
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
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823 import (
    run as reviewer_3,
)
from cognitive_well_harness_v0_3_51_reviewer3_certifier_20260823.protocol import (
    parse_review as parse_reviewer_3,
)
from cognitive_well_harness_v0_3_52_fusion_20260823.run import (
    stable_seed as fusion_seed,
)
from cognitive_well_harness_v0_3_53_fusion_20260823 import run as fusion
from cognitive_well_harness_v0_3_54_resolver_20260823 import run as resolver
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    write_json,
)
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.pipeline import (
    utc_now,
)
from cognitive_well_harness_v0_3_85_nvfp4_single_trace_resolver_20260827.pipeline import (
    sha256_text,
)
from cognitive_well_harness_v0_3_87_markdown_trace_extractor_20260827.pipeline import (
    run_compact_markdown_extractor,
    run_original_reviewer,
)
from cognitive_well_harness_v0_3_88_bf16_mtp4_trace_gate_selector_20260827.pipeline import (
    markdown_trace_packets,
)
from cognitive_well_harness_v0_3_89_conditional_gap_selector_20260827.pipeline import (
    run_gap_selector as run_v089_selector,
)
from cognitive_well_harness_v0_3_92_scope_matched_gap_selector_20260827.pipeline import (
    run_gap_selector as run_v092_selector,
)
from .generic_adapters import (
    reviewer_3_failure_record,
)
from .generic_adapters import (
    recover_role_label_only_fusion_result,
    reviewer_1_failure_record,
)

from . import GEMMA_MODEL, HARNESS_VERSION, QWEN_MODEL


ROOT = Path(__file__).resolve().parent.parent
FUSION_TEMPERATURE = 0.4
RESOLVER_TEMPERATURE = 0.4
REVIEWER_1_TEMPERATURE = 0.1
REVIEWER_2_TEMPERATURE = 0.2
REVIEWER_3_TEMPERATURE = 0.2
R1_SUCCESS = {"NO_FIRST_BREAK"}
R1_FAILURE = {"FIRST_BREAK"}
R3_SUCCESS = {"PROOF_CERTIFIED", "NO_UNCLOSED_OBLIGATION_FOUND"}
R3_FAILURE = {"CERTIFICATION_FAILURE"}
PARSERS: dict[str, Callable[[str], dict[str, Any]]] = {
    "reviewer_1": parse_reviewer_1,
    "reviewer_2": parse_reviewer_2,
    "reviewer_3": parse_reviewer_3,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_seed(label: str) -> int:
    value = int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:4], "big")
    return value or 1


def resolve_input_path(base: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else base / path).resolve()


def require_within(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes the single-problem source root: {path}") from error
    return path


def public_identity(payload: dict[str, Any]) -> dict[str, Any]:
    task = payload.get("task")
    if isinstance(task, dict):
        return dict(task)
    identity = payload.get("identity")
    return dict(identity) if isinstance(identity, dict) else {}


def review_final(result_path: Path, payload: dict[str, Any]) -> str:
    final = str(payload.get("final") or "").strip()
    if final:
        return final
    for name in ("final.txt", "final.md"):
        path = result_path.parent / name
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            return path.read_text(encoding="utf-8").strip()
    raise ValueError(f"review artifact has no visible final: {result_path}")


def reasoning_paths(result_path: Path, payload: dict[str, Any]) -> list[Path]:
    if payload.get("reasoning_harvest_policy") == "accepted_transport_attempt_only":
        accepted = (result_path.parent / "reasoning.txt").resolve()
        if not accepted.is_file() or not accepted.read_text(encoding="utf-8").strip():
            raise ValueError(
                "accepted-attempt-only review lacks its canonical reasoning.txt"
            )
        return [accepted]
    candidates: list[Path] = []
    for key in ("generation", "final_generation"):
        metadata = payload.get(key)
        if not isinstance(metadata, dict):
            continue
        value = metadata.get("reasoning_path")
        if value:
            path = Path(str(value))
            candidates.append(path if path.is_absolute() else (ROOT / path))
    for name in (
        "reasoning.txt",
        "reviewer1.reasoning.txt",
        "reviewer2.reasoning.txt",
        "reviewer3.reasoning.txt",
    ):
        candidates.append(result_path.parent / name)
    candidates.extend(sorted(result_path.parent.glob("*.reasoning.txt")))
    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        path = candidate.resolve()
        if path in seen or not path.is_file():
            continue
        if not path.read_text(encoding="utf-8").strip():
            continue
        seen.add(path)
        unique.append(path)
    return unique


def combined_reasoning(paths: list[Path]) -> str:
    chunks: list[str] = []
    seen: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        digest = sha256_text(text)
        if digest in seen:
            continue
        seen.add(digest)
        chunks.append(text)
    return "\n\n[CONTINUATION]\n\n".join(chunks).strip()


def load_review_artifact(
    *, role: str, result_path: Path, proof_sha256: str, problem_sha256: str
) -> dict[str, Any]:
    payload = load_json(result_path)
    final = review_final(result_path, payload)
    parsed = PARSERS[role](final)
    if not parsed["valid"]:
        raise ValueError(f"invalid {role} protocol in {result_path}: {parsed['errors']}")
    identity = public_identity(payload)
    for key, expected in (
        ("proof_sha256", proof_sha256),
        ("problem_sha256", problem_sha256),
    ):
        observed = identity.get(key)
        if observed is not None and str(observed) != expected:
            raise ValueError(f"{role} {key} mismatch in {result_path}")
    paths = reasoning_paths(result_path, payload)
    return {
        "role": role,
        "result_path": str(result_path.resolve()),
        "result_sha256": file_sha256(result_path),
        "payload": payload,
        "identity": identity,
        "final": final,
        "final_sha256": sha256_text(final),
        "parsed": parsed,
        "outcome": parsed["outcome"],
        "reasoning_paths": [str(path) for path in paths],
        "model": identity.get("model") or identity.get("model_name"),
        "temperature": identity.get("temperature"),
    }


def problem_number_from(problem_id: str) -> int:
    match = re.search(r"(?:^|[_-])p([0-9]+)$", problem_id, re.IGNORECASE)
    if match is None:
        raise ValueError(f"problem_number is required for problem_id={problem_id!r}")
    return int(match.group(1))


def prepare_case(
    spec: dict[str, Any],
    *,
    index: int,
    manifest_dir: Path,
    allowed_input_root: Path | None,
) -> dict[str, Any]:
    mode = str(spec.get("mode") or "fresh")
    if mode not in {"fresh", "replay"}:
        raise ValueError(f"case {index}: mode must be fresh or replay")
    case_id = str(spec.get("case_id") or f"case_{index:03d}")
    problem_path = resolve_input_path(manifest_dir, str(spec["problem_path"]))
    proof_path = resolve_input_path(manifest_dir, str(spec["proof_path"]))
    if allowed_input_root is not None:
        problem_path = require_within(
            allowed_input_root, problem_path, f"case {case_id} problem"
        )
        proof_path = require_within(
            allowed_input_root, proof_path, f"case {case_id} proof"
        )
    problem_payload = load_json(problem_path)
    problem = str(problem_payload.get("claim") or "").strip()
    proof = proof_path.read_text(encoding="utf-8").strip()
    if not problem or not proof:
        raise ValueError(f"{case_id}: problem and proof must be nonempty")
    problem_id = str(spec.get("problem_id") or problem_payload.get("problem_id") or "")
    if not problem_id:
        raise ValueError(f"{case_id}: problem_id is required")
    problem_number = int(
        spec.get("problem_number") or problem_number_from(problem_id)
    )
    candidate_id = str(spec.get("candidate_id") or "").strip()
    if not candidate_id:
        raise ValueError(f"{case_id}: candidate_id is required")
    case = {
        "case_id": case_id,
        "mode": mode,
        "proof_index": int(spec.get("proof_index", index)),
        "problem_number": problem_number,
        "problem_id": problem_id,
        "candidate_id": candidate_id,
        "problem_path": str(problem_path),
        "problem": problem,
        "problem_sha256": sha256_text(problem),
        "proof_path": str(proof_path),
        "proof": proof,
        "proof_sha256": sha256_text(proof),
        "reviews": {},
    }
    if mode == "replay":
        for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
            key = f"{role}_result"
            if key not in spec:
                raise ValueError(f"{case_id}: replay mode requires {key}")
            result_path = resolve_input_path(manifest_dir, str(spec[key]))
            if allowed_input_root is not None:
                result_path = require_within(
                    allowed_input_root,
                    result_path,
                    f"case {case_id} {role} result",
                )
            case["reviews"][role] = load_review_artifact(
                role=role,
                result_path=result_path,
                proof_sha256=case["proof_sha256"],
                problem_sha256=case["problem_sha256"],
            )
    return case


def load_cases(
    manifest_path: Path, *, allowed_input_root: Path | None = None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = manifest_path.resolve()
    if allowed_input_root is not None:
        allowed_input_root = allowed_input_root.resolve()
        require_within(allowed_input_root, manifest_path, "cases manifest")
    manifest = load_json(manifest_path)
    specs = manifest.get("cases")
    if not isinstance(specs, list) or not specs:
        raise ValueError("cases manifest must contain a nonempty cases list")
    cases = [
        prepare_case(
            spec,
            index=index,
            manifest_dir=manifest_path.parent,
            allowed_input_root=allowed_input_root,
        )
        for index, spec in enumerate(specs)
    ]
    identifiers = [case["case_id"] for case in cases]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("case_id values must be unique")
    return manifest, cases


def run_parallel(
    *, name: str, jobs: list[dict[str, Any]], max_workers: int, task: Callable[[dict[str, Any]], Any]
) -> None:
    errors: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, max_workers), thread_name_prefix=f"v096-{name}"
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


def common_review_task(case: dict[str, Any], *, endpoint: str, gpu: int) -> dict[str, Any]:
    return {
        key: case[key]
        for key in (
            "proof_index",
            "problem_number",
            "problem_id",
            "candidate_id",
            "problem_path",
            "problem_sha256",
            "proof_path",
            "proof_sha256",
            "problem",
            "proof",
        )
    } | {"endpoint": endpoint, "gpu": gpu}


def run_fresh_reviews(
    *,
    cases: list[dict[str, Any]],
    output_dir: Path,
    gemma_endpoints: list[str],
    qwen_endpoint: str,
    workers_per_endpoint: int,
    seed_namespace: str,
) -> None:
    jobs_by_role: dict[str, list[dict[str, Any]]] = {
        "reviewer_1": [],
        "reviewer_2": [],
        "reviewer_3": [],
    }
    fresh = [case for case in cases if case["mode"] == "fresh"]
    for index, case in enumerate(fresh):
        gpu = index % len(gemma_endpoints)
        for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
            jobs_by_role[role].append(
                {
                    "job_id": f"{case['case_id']}.{role}",
                    "case": case,
                    "role": role,
                    "gpu": gpu,
                    "qwen_gpu": 1,
                    "gemma_endpoint": gemma_endpoints[gpu],
                    "qwen_endpoint": qwen_endpoint,
                }
            )

    def task(job: dict[str, Any]) -> None:
        case = job["case"]
        role = job["role"]
        case_dir = output_dir / "cases" / case["case_id"] / "reviews"
        label = f"{seed_namespace}:{case['case_id']}:{role}"
        if role == "reviewer_1":
            destination = case_dir / "reviewer_1"
            run_original_reviewer(
                problem=case["problem"],
                proof=case["proof"],
                endpoint=job["gemma_endpoint"],
                output_dir=destination,
                seed=stable_seed(label),
                seed_label=label,
                model=GEMMA_MODEL,
            )
            result_path = destination / "result.json"
        elif role == "reviewer_2":
            review_task = common_review_task(
                case, endpoint=job["qwen_endpoint"], gpu=int(job["qwen_gpu"])
            )
            review_task.update(
                {
                    "seed": stable_seed(label),
                    "temperature": REVIEWER_2_TEMPERATURE,
                    "temperature_label": "t02",
                    "model_key": "qwen36",
                    "model_name": QWEN_MODEL,
                    "task_id": f"{case['case_id']}.reviewer2.t02",
                }
            )
            stage = case_dir / "reviewer_2_stage"
            reviewer_2.run_task(output_dir=stage, task=review_task)
            result_path = reviewer_2.task_output_dir(stage, review_task) / "result.json"
        else:
            review_task = common_review_task(
                case, endpoint=job["gemma_endpoint"], gpu=int(job["gpu"])
            )
            review_task.update(
                {
                    "seed": stable_seed(label),
                    "temperature": REVIEWER_3_TEMPERATURE,
                    "temperature_label": "t02",
                    "model_key": "gemma4",
                    "model_name": GEMMA_MODEL,
                    "task_id": f"{case['case_id']}.reviewer3.t02",
                }
            )
            stage = case_dir / "reviewer_3_stage"
            reviewer_3.run_task(output_dir=stage, task=review_task)
            result_path = reviewer_3.task_output_dir(stage, review_task) / "result.json"
        artifact = load_review_artifact(
            role=role,
            result_path=result_path,
            proof_sha256=case["proof_sha256"],
            problem_sha256=case["problem_sha256"],
        )
        if role == "reviewer_1":
            artifact["identity"] = {
                key: case[key]
                for key in (
                    "proof_index",
                    "problem_number",
                    "problem_id",
                    "candidate_id",
                    "problem_path",
                    "problem_sha256",
                    "proof_path",
                    "proof_sha256",
                )
            } | {
                "model": GEMMA_MODEL,
                "temperature": REVIEWER_1_TEMPERATURE,
                "endpoint": job["gemma_endpoint"],
                "gpu": int(job["gpu"]),
            }
            artifact["model"] = GEMMA_MODEL
            artifact["temperature"] = REVIEWER_1_TEMPERATURE
        case["reviews"][role] = artifact

    def gemma_branch() -> None:
        # Reviewer 3 deliberately begins only after the complete Reviewer 1 wave.
        # This bounds Gemma memory pressure and implements the frozen split-GPU
        # schedule used by the v0.3.97 parent harness.
        run_parallel(
            name="fresh_reviewer_1",
            jobs=jobs_by_role["reviewer_1"],
            max_workers=len(gemma_endpoints) * workers_per_endpoint,
            task=task,
        )
        run_parallel(
            name="fresh_reviewer_3",
            jobs=jobs_by_role["reviewer_3"],
            max_workers=len(gemma_endpoints) * workers_per_endpoint,
            task=task,
        )

    def qwen_branch() -> None:
        run_parallel(
            name="fresh_reviewer_2",
            jobs=jobs_by_role["reviewer_2"],
            max_workers=workers_per_endpoint,
            task=task,
        )

    # Qwen Reviewer 2 runs concurrently with the sequential Gemma R1 -> R3
    # branch. Fusion is launched only after both futures complete.
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=2, thread_name_prefix="v096-split-review"
    ) as pool:
        pending = [pool.submit(gemma_branch), pool.submit(qwen_branch)]
        for future in pending:
            future.result()


def real_gap_packets(
    extraction: dict[str, Any], selector: dict[str, Any]
) -> list[dict[str, str]]:
    packets = markdown_trace_packets(extraction)
    by_id = {str(packet["gap_id"]): packet for packet in packets}
    selected: list[dict[str, str]] = []
    for decision in selector.get("decisions") or []:
        if decision.get("label") != "REAL_GAP":
            continue
        packet = by_id.get(str(decision.get("gap_id")))
        if packet is None:
            raise ValueError("selector referenced an unknown trace packet")
        selected.append(
            {
                "gap_id": str(packet["gap_id"]),
                "useful_material": str(packet.get("useful_material") or ""),
                "repair_needed": str(packet["repair_needed"]),
                "trace_reason": str(packet["reason"]),
                "selector_reason": str(decision["reason"]),
            }
        )
    return selected


def enhancement_needed(role: str, outcome: str) -> bool:
    if role == "reviewer_1":
        if outcome in R1_FAILURE:
            return False
        if outcome in R1_SUCCESS:
            return True
    elif role == "reviewer_3":
        if outcome in R3_FAILURE:
            return False
        if outcome in R3_SUCCESS:
            return True
    raise ValueError(f"unsupported {role} outcome: {outcome}")


def run_enhancements(
    *,
    cases: list[dict[str, Any]],
    output_dir: Path,
    gemma_endpoints: list[str],
    workers_per_endpoint: int,
    seed_namespace: str,
) -> None:
    jobs: list[dict[str, Any]] = []
    for case in cases:
        for role in ("reviewer_1", "reviewer_3"):
            review = case["reviews"][role]
            if not enhancement_needed(role, str(review["outcome"])):
                review["enhancement"] = {
                    "version": "0.3.89" if role == "reviewer_1" else "0.3.92",
                    "route": "retain_visible_defect",
                    "model_call_count": 0,
                    "selected_real_gaps": [],
                }
                review["effective_final"] = review["final"]
                review["effective_outcome"] = review["outcome"]
                continue
            paths = [Path(path) for path in review["reasoning_paths"]]
            reasoning = combined_reasoning(paths)
            if not reasoning:
                raise RuntimeError(
                    f"{case['case_id']} {role} succeeded without an observable reasoning trace"
                )
            jobs.append(
                {
                    "job_id": f"{case['case_id']}.{role}",
                    "case": case,
                    "role": role,
                    "review": review,
                    "reasoning": reasoning,
                }
            )

    for index, job in enumerate(jobs):
        gpu = index % len(gemma_endpoints)
        job["gpu"] = gpu
        job["endpoint"] = gemma_endpoints[gpu]

    def task(job: dict[str, Any]) -> None:
        case = job["case"]
        role = job["role"]
        review = job["review"]
        destination = output_dir / "cases" / case["case_id"] / "enhancements" / role
        extraction = run_compact_markdown_extractor(
            problem=case["problem"],
            proof=case["proof"],
            reasoning=job["reasoning"],
            reviewer_final=review["final"],
            endpoint=job["endpoint"],
            output_dir=destination / "01_trace_extraction",
            seed=stable_seed(f"{seed_namespace}:{job['job_id']}:extract"),
            seed_label=f"{seed_namespace}:{job['job_id']}:extract",
            model=GEMMA_MODEL,
        )
        packets = markdown_trace_packets(extraction)
        selector_fn = run_v089_selector if role == "reviewer_1" else run_v092_selector
        selector = selector_fn(
            problem=case["problem"],
            proof=case["proof"],
            packets=packets,
            endpoint=job["endpoint"],
            output_dir=destination / "02_selector",
            seed=stable_seed(f"{seed_namespace}:{job['job_id']}:selector"),
            seed_label=f"{seed_namespace}:{job['job_id']}:selector",
            model=GEMMA_MODEL,
        )
        gaps = real_gap_packets(extraction, selector)
        if gaps:
            injected = gaps[0]
            effective_final = (
                reviewer_1_failure_record(injected)
                if role == "reviewer_1"
                else reviewer_3_failure_record(injected)
            )
            effective_outcome = (
                "FIRST_BREAK" if role == "reviewer_1" else "CERTIFICATION_FAILURE"
            )
            route = "selected_real_gap_injected"
        else:
            injected = None
            effective_final = review["final"]
            effective_outcome = review["outcome"]
            route = "no_real_gap_selected"
        review["enhancement"] = {
            "version": "0.3.89" if role == "reviewer_1" else "0.3.92",
            "route": route,
            "model_call_count": int(extraction.get("generation") is not None)
            + int(selector.get("model_call_count") or 0),
            "trace_candidate_count": len(packets),
            "selected_real_gaps": gaps,
            "fusion_injected_gap": injected,
            "extraction_path": str((destination / "01_trace_extraction/result.json").resolve()),
            "selector_path": str((destination / "02_selector/result.json").resolve()),
        }
        review["effective_final"] = effective_final
        review["effective_outcome"] = effective_outcome
        write_json(destination / "route.json", review["enhancement"])

    run_parallel(
        name="reviewer_enhancements",
        jobs=jobs,
        max_workers=len(gemma_endpoints) * workers_per_endpoint,
        task=task,
    )


def reviewer_source_metadata(review: dict[str, Any]) -> dict[str, Any]:
    enhancement = deepcopy(review.get("enhancement") or {})
    return {
        "source_result_path": review["result_path"],
        "source_result_sha256": review["result_sha256"],
        "proof_sha256": review["identity"].get("proof_sha256"),
        "model": review.get("model"),
        "temperature": review.get("temperature"),
        "original_outcome": review["outcome"],
        "outcome": review.get("effective_outcome", review["outcome"]),
        "original_final_sha256": review["final_sha256"],
        "final_sha256": sha256_text(
            str(review.get("effective_final") or review["final"])
        ),
        "enhancement": enhancement,
    }


def build_fusion_task(
    case: dict[str, Any], *, endpoint: str, gpu: int, seed_namespace: str
) -> dict[str, Any]:
    task = {
        key: case[key]
        for key in (
            "proof_index",
            "problem_number",
            "problem_id",
            "candidate_id",
            "problem_path",
            "problem_sha256",
            "proof_path",
            "proof_sha256",
            "problem",
            "proof",
        )
    }
    for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
        review = case["reviews"][role]
        task[role] = str(review.get("effective_final") or review["final"])
    task.update(
        {
            "reviewer_sources": {
                role: reviewer_source_metadata(case["reviews"][role])
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
            "seed": fusion_seed(
                case["problem_number"],
                f"{seed_namespace}:{case['candidate_id']}",
                case["proof_sha256"],
            ),
            "temperature": FUSION_TEMPERATURE,
            "temperature_label": "t04",
            "gpu": gpu,
            "endpoint": endpoint,
            "model_key": "gemma4",
            "model_name": GEMMA_MODEL,
            "task_id": f"{case['case_id']}.fusion.t04",
        }
    )
    return task


def build_resolver_task(
    *, case: dict[str, Any], fusion_task: dict[str, Any], fusion_result: dict[str, Any],
    case_dir: Path, seed_namespace: str
) -> dict[str, Any]:
    task = {
        key: fusion_task[key]
        for key in (
            "proof_index",
            "problem_number",
            "problem_id",
            "candidate_id",
            "problem_path",
            "problem_sha256",
            "proof_path",
            "proof_sha256",
            "problem",
            "proof",
        )
    }
    task.update(
        {
            "fusion_record": str(fusion_result["final"]),
            "fusion_record_sha256": sha256_text(str(fusion_result["final"])),
            "fusion_outcome": fusion_result["parsed"]["outcome"],
            "fusion_result_path": str(
                (fusion.task_output_dir(case_dir, fusion_task) / "result.json").resolve()
            ),
            "seed": resolver.stable_seed(
                case["problem_number"],
                f"{seed_namespace}:{case['candidate_id']}",
                case["proof_sha256"],
            ),
            "temperature": RESOLVER_TEMPERATURE,
            "temperature_label": "t04",
            "gpu": fusion_task["gpu"],
            "endpoint": fusion_task["endpoint"],
            "model_key": "gemma4",
            "model_name": GEMMA_MODEL,
            "task_id": f"{case['case_id']}.resolver.t04",
        }
    )
    return task


def write_uncertified_trace_handoff(
    *, case: dict[str, Any], case_dir: Path, resolver_task: dict[str, Any],
    resolver_result: dict[str, Any]
) -> dict[str, Any]:
    destination = resolver.task_output_dir(case_dir, resolver_task)
    paths = sorted(destination.glob("*.reasoning.txt"))
    trace_files = [
        {
            "path": str(path.resolve()),
            "file_sha256": file_sha256(path),
            "text_sha256": sha256_text(path.read_text(encoding="utf-8").strip()),
            "bytes": path.stat().st_size,
        }
        for path in paths
        if path.read_text(encoding="utf-8").strip()
    ]
    proof_path = destination / "resolved_proof.md"
    if resolver_result["parsed"]["outcome"] == "ORIGINAL_PROOF_VALID":
        proof_path = Path(case["proof_path"])
    handoff = {
        "schema": "cognitive-well-v096-uncertified-resolver-trace-handoff-v1",
        "created_at": utc_now(),
        "case_id": case["case_id"],
        "problem_id": case["problem_id"],
        "candidate_id": case["candidate_id"],
        "status": "UNCERTIFIED_TRACE",
        "intended_consumer": "later_hypothesis_extraction_pipeline",
        "trace_files": trace_files,
        "reasoning_observed": bool(trace_files),
        "resolver_result_path": str((destination / "result.json").resolve()),
        "resolver_result_sha256": file_sha256(destination / "result.json"),
        "resolver_outcome": resolver_result["parsed"]["outcome"],
        "proof_path": str(proof_path.resolve()),
        "proof_sha256": (
            sha256_text(proof_path.read_text(encoding="utf-8").strip())
            if proof_path.is_file()
            else None
        ),
        "consumer_contract": {
            "mathematical_status": "unverified exploratory material",
            "may_contain_errors_or_abandoned_routes": True,
            "audit_inside_v096": False,
            "trace_extraction_inside_v096": False,
            "conservative_selection_inside_v096": False,
            "promotion_to_certified_memory": False,
            "required_later_flow": [
                "post_generation_audit",
                "trace_extraction",
                "conservative_selection",
                "hypothesis_extraction",
                "independent_hypothesis_certification",
            ],
        },
    }
    handoff_dir = case_dir / "resolver_trace_handoff"
    write_json(handoff_dir / "handoff.json", handoff)
    return handoff


def run(
    *,
    cases_manifest: Path,
    output_dir: Path,
    gemma_endpoints: list[str],
    qwen_endpoint: str | None,
    workers_per_endpoint: int,
    seed_namespace: str,
    dry_run: bool,
    allowed_input_root: Path | None = None,
) -> dict[str, Any]:
    if not gemma_endpoints or workers_per_endpoint < 1:
        raise ValueError("at least one Gemma endpoint and one worker are required")
    source_manifest, cases = load_cases(
        cases_manifest, allowed_input_root=allowed_input_root
    )
    if any(case["mode"] == "fresh" for case in cases) and not qwen_endpoint and not dry_run:
        raise ValueError("fresh mode requires --qwen-endpoint")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "cognitive-well-v096-generic-enhanced-review-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_manifest_path": str(cases_manifest.resolve()),
        "source_manifest_sha256": file_sha256(cases_manifest.resolve()),
        "source_manifest_schema": source_manifest.get("schema"),
        "case_count": len(cases),
        "modes": {mode: sum(case["mode"] == mode for case in cases) for mode in ("fresh", "replay")},
        "models": {"gemma": GEMMA_MODEL, "qwen": QWEN_MODEL},
        "gemma_runtime_profile": {
            "model": GEMMA_MODEL,
            "dtype": "bfloat16",
            "mtp_speculative_tokens": 4,
            "applies_to": [
                "reviewer_1",
                "reviewer_3",
                "reviewer_1_trace_enhancement",
                "reviewer_3_trace_enhancement",
                "fusion",
                "resolver",
            ],
            "single_shared_endpoint": len(gemma_endpoints) == 1,
        },
        "components": {
            "reviewer_1_enhancement": "0.3.89",
            "reviewer_2": "0.3.50",
            "reviewer_3_enhancement": "0.3.92",
            "fusion": "0.3.53",
            "resolver": "0.3.54",
        },
        "temperatures": {
            "reviewer_1": REVIEWER_1_TEMPERATURE,
            "reviewer_2": REVIEWER_2_TEMPERATURE,
            "reviewer_3": REVIEWER_3_TEMPERATURE,
            "trace_extractor": 0.1,
            "gap_selectors": 0.1,
            "fusion": FUSION_TEMPERATURE,
            "resolver": RESOLVER_TEMPERATURE,
        },
        "gemma_endpoints": gemma_endpoints,
        "qwen_endpoint": qwen_endpoint,
        "device_roles": {
            "gpu0": [
                "reviewer_1",
                "reviewer_3",
                "reviewer_1_trace_enhancement",
                "reviewer_3_trace_enhancement",
                "fusion",
                "resolver",
            ],
            "gpu1": ["reviewer_2"],
        },
        "fresh_review_schedule": {
            "gpu0": "reviewer_1_batch_then_reviewer_3_batch",
            "gpu1": "reviewer_2_batch_concurrent_with_entire_gpu0_review_branch",
            "barrier_before_fusion": True,
        },
        "workers_per_endpoint": workers_per_endpoint,
        "seed_namespace": seed_namespace,
        "problem_specific_prompting": False,
        "resolver_trace_policy": "store_only_as_UNCERTIFIED_TRACE",
        "cases": [
            {
                key: case[key]
                for key in (
                    "case_id", "mode", "problem_number", "problem_id", "candidate_id",
                    "problem_path", "problem_sha256", "proof_path", "proof_sha256"
                )
            }
            for case in cases
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "errors.json", {})
    if dry_run:
        result = {
            "schema": "cognitive-well-v096-dry-run-summary-v1",
            "harness_version": HARNESS_VERSION,
            "state": "dry_run_completed",
            "completed_at": utc_now(),
            "case_count": len(cases),
            "fresh_review_call_count": 3 * sum(case["mode"] == "fresh" for case in cases),
            "replay_outcomes": {
                case["case_id"]: {
                    role: case["reviews"][role]["outcome"]
                    for role in case["reviews"]
                }
                for case in cases
                if case["mode"] == "replay"
            },
            "resolver_trace_policy": "store_only_as_UNCERTIFIED_TRACE",
        }
        write_json(output_dir / "summary.json", result)
        write_json(output_dir / "status.json", {"state": "dry_run_completed", "stage": "done", "updated_at": utc_now()})
        return result

    write_json(output_dir / "status.json", {"state": "running", "stage": "fresh_reviews", "updated_at": utc_now()})
    run_fresh_reviews(
        cases=cases,
        output_dir=output_dir,
        gemma_endpoints=gemma_endpoints,
        qwen_endpoint=str(qwen_endpoint),
        workers_per_endpoint=workers_per_endpoint,
        seed_namespace=seed_namespace,
    )
    write_json(output_dir / "status.json", {"state": "running", "stage": "conditional_reviewer_enhancement", "updated_at": utc_now()})
    run_enhancements(
        cases=cases,
        output_dir=output_dir,
        gemma_endpoints=gemma_endpoints,
        workers_per_endpoint=workers_per_endpoint,
        seed_namespace=seed_namespace,
    )

    for index, case in enumerate(cases):
        gpu = index % len(gemma_endpoints)
        case["fusion_task"] = build_fusion_task(
            case,
            endpoint=gemma_endpoints[gpu],
            gpu=gpu,
            seed_namespace=seed_namespace,
        )
        lane = output_dir / "cases" / case["case_id"]
        lane.mkdir(parents=True, exist_ok=True)
        for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
            (lane / f"effective_{role}.txt").write_text(
                str(case["fusion_task"][role]).strip() + "\n", encoding="utf-8"
            )

    write_json(output_dir / "status.json", {"state": "running", "stage": "batched_fusion_t04", "updated_at": utc_now()})
    fusion_jobs = [{"job_id": case["case_id"], "case": case} for case in cases]

    def fusion_call(job: dict[str, Any]) -> None:
        case = job["case"]
        lane = output_dir / "cases" / case["case_id"]
        task = case["fusion_task"]
        try:
            result = fusion.run_task(output_dir=lane, task=task)
        except ValueError:
            result = recover_role_label_only_fusion_result(lane, task)
            if result is None:
                raise
        case["fusion_result"] = result

    run_parallel(
        name="fusion_t04",
        jobs=fusion_jobs,
        max_workers=len(gemma_endpoints) * workers_per_endpoint,
        task=fusion_call,
    )

    for case in cases:
        lane = output_dir / "cases" / case["case_id"]
        case["resolver_task"] = build_resolver_task(
            case=case,
            fusion_task=case["fusion_task"],
            fusion_result=case["fusion_result"],
            case_dir=lane,
            seed_namespace=seed_namespace,
        )

    write_json(output_dir / "status.json", {"state": "running", "stage": "batched_resolver_t04", "updated_at": utc_now()})
    resolver_jobs = [{"job_id": case["case_id"], "case": case} for case in cases]

    def resolver_call(job: dict[str, Any]) -> None:
        case = job["case"]
        lane = output_dir / "cases" / case["case_id"]
        result = resolver.run_task(output_dir=lane, task=case["resolver_task"])
        case["resolver_result"] = result
        case["trace_handoff"] = write_uncertified_trace_handoff(
            case=case,
            case_dir=lane,
            resolver_task=case["resolver_task"],
            resolver_result=result,
        )

    run_parallel(
        name="resolver_t04",
        jobs=resolver_jobs,
        max_workers=len(gemma_endpoints) * workers_per_endpoint,
        task=resolver_call,
    )

    rows = []
    for case in cases:
        rows.append(
            {
                "case_id": case["case_id"],
                "mode": case["mode"],
                "problem_id": case["problem_id"],
                "candidate_id": case["candidate_id"],
                "reviewer_outcomes": {
                    role: {
                        "original": case["reviews"][role]["outcome"],
                        "effective": case["reviews"][role].get(
                            "effective_outcome", case["reviews"][role]["outcome"]
                        ),
                        "route": (case["reviews"][role].get("enhancement") or {}).get("route"),
                    }
                    for role in ("reviewer_1", "reviewer_2", "reviewer_3")
                },
                "fusion_outcome": case["fusion_result"]["parsed"]["outcome"],
                "resolver_outcome": case["resolver_result"]["parsed"]["outcome"],
                "resolved_proof_sha256": case["resolver_result"]["parsed"].get("proof_sha256"),
                "resolver_trace_handoff": str(
                    (output_dir / "cases" / case["case_id"] / "resolver_trace_handoff/handoff.json").resolve()
                ),
                "resolver_trace_status": "UNCERTIFIED_TRACE",
            }
        )
    summary = {
        "schema": "cognitive-well-v096-generic-enhanced-review-summary-v1",
        "harness_version": HARNESS_VERSION,
        "state": "completed",
        "completed_at": utc_now(),
        "case_count": len(rows),
        "rows": rows,
    }
    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "status.json", {"state": "completed", "stage": "done", "updated_at": utc_now()})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generic enhanced Reviewer 1/3 -> Fusion -> Resolver harness"
    )
    parser.add_argument("--cases-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", action="append", default=[])
    parser.add_argument("--qwen-endpoint")
    parser.add_argument("--workers-per-endpoint", type=int, default=2)
    parser.add_argument("--seed-namespace", default="v096")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    endpoints = args.gemma_endpoint or [
        "http://127.0.0.1:8030/v1",
        "http://127.0.0.1:8032/v1",
    ]
    result = run(
        cases_manifest=args.cases_manifest,
        output_dir=args.output_dir,
        gemma_endpoints=[endpoint.rstrip("/") for endpoint in endpoints],
        qwen_endpoint=args.qwen_endpoint.rstrip("/") if args.qwen_endpoint else None,
        workers_per_endpoint=args.workers_per_endpoint,
        seed_namespace=args.seed_namespace,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
