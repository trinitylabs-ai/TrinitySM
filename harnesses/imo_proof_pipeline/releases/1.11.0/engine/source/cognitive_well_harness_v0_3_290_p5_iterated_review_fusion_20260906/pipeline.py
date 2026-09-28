from __future__ import annotations

from experiments.local_math_verifier import timeout_recovery as timeout_policy

import copy
import hashlib
import json
import re
import shutil
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Iterator

from cognitive_well_harness_v0_3_325_single_model_problem_pipeline_20260909 import runtime as single_model

from cognitive_well_harness_v0_3_263_v260_unified_recovery_20260905 import (
    pipeline as v263,
)
from cognitive_well_harness_v0_3_264_p5_resolver1_v263_recycle_20260905 import (
    pipeline as v264,
)
from cognitive_well_harness_v0_3_108_problem_only_contextual_surgery_20260828 import (
    pipeline as v108,
)
from experiments.local_math_verifier import runtime as transport
from experiments.local_math_verifier import frontend_portfolio

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from . import repair_boundary


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_RUN = v264.DEFAULT_SOURCE_RUN
DEFAULT_GEMMA_ENDPOINT = "http://127.0.0.1:8030/v1"
DEFAULT_QWEN_ENDPOINT = "http://127.0.0.1:8027/v1"
DEFAULT_SEED_NAMESPACE = "v0290:p5:iterated_review_fusion"
DEFAULT_MODEL_TIMEOUT_SEC = 600
R1_CYCLE_COUNT = 2
STAGE_ORDER = tuple(f"R1-C{cycle}" for cycle in range(1, R1_CYCLE_COUNT + 1))
TERMINAL_CHECKPOINT = STAGE_ORDER[-1]
PIPELINE_POLICY = "r1_two_cycles_terminal_v1"
PROBLEM_ID = v264.PROBLEM_ID
PROBLEM_NUMBER = v264.PROBLEM_NUMBER
CANDIDATE_IDS = v264.CANDIDATE_IDS
EXPECTED_PROBLEM_SHA256 = v264.EXPECTED_PROBLEM_SHA256


def configure_problem_binding(
    *, problem_id: str, problem_number: int, problem_sha256: str,
    candidate_ids: tuple[str, ...],
) -> None:
    """Bind one problem per process before any lane workers are started.

    This changes artifact identity only, never prompts or mathematical policy.
    Separate processes are required for simultaneous different problems.
    """
    global PROBLEM_ID, PROBLEM_NUMBER, EXPECTED_PROBLEM_SHA256, CANDIDATE_IDS
    if (not re.fullmatch(r"[A-Za-z0-9_-]+", problem_id) or problem_number < 1
            or not re.fullmatch(r"[0-9a-f]{64}", problem_sha256)
            or len(candidate_ids) != 4 or len(set(candidate_ids)) != 4
            or any(not re.fullmatch(r"[A-Za-z0-9_-]+", item) for item in candidate_ids)):
        raise ValueError("invalid problem/portfolio binding")
    PROBLEM_ID, PROBLEM_NUMBER = problem_id, problem_number
    EXPECTED_PROBLEM_SHA256, CANDIDATE_IDS = problem_sha256, candidate_ids


def configure_source_problem(
    source_run: Path, problem_number: int, *, expected_problem_id: str | None = None,
) -> None:
    phase_root = source_run / f"p{problem_number}/01_raw_lazy_enhanced_resolve"
    if (phase_root / "frontend_portfolio.json").is_file():
        partial = frontend_portfolio.load(
            phase_root, problem_number, expected_problem_id or f"imo2026_p{problem_number}")
        configure_problem_binding(
            problem_id=partial["problem_id"], problem_number=problem_number,
            problem_sha256=partial["problem_sha256"],
            candidate_ids=tuple(row["candidate_id"] for row in partial["proofs"]))
        return
    source = read_object(phase_root / "phase_2_v096/manifest.json")
    rows = source["cases"]
    identities = {(row["problem_id"], row["problem_sha256"]) for row in rows}
    if len(identities) != 1:
        raise ValueError("source portfolio does not share one problem")
    problem_id, digest = next(iter(identities))
    if problem_id != (expected_problem_id if expected_problem_id is not None else f"imo2026_p{problem_number}"):
        raise ValueError("source portfolio problem selector mismatch")
    if expected_problem_id is not None:
        payload = read_object(phase_root / "input/problem.json")
        if (payload.get("problem_id") != problem_id
                or payload.get("problem_number") != problem_number
                or any(row.get("problem_number") != problem_number for row in rows)):
            raise ValueError("source problem envelope/portfolio identity mismatch")
    configure_problem_binding(
        problem_id=problem_id, problem_number=problem_number, problem_sha256=digest,
        candidate_ids=tuple(row["candidate_id"] for row in rows),
    )

stage = v263.parent.parent.parent.v108.v097.enhanced_pipeline

_PATCH_LOCK = threading.RLock()
_BOUNDARY_CONFIG: dict[str, Any] | None = None


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _unused_resume_path(path: Path) -> Path:
    """Keep earlier recovery journals intact when another boundary needs repair."""
    index = 2
    candidate = path
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}_attempt_{index:02d}{path.suffix}")
        index += 1
    return candidate


def _require_child(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes {root}: {path}") from error
    return path


def _stage_file(source: Path, destination: Path) -> None:
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if file_sha256(source) != file_sha256(destination):
        raise RuntimeError(f"staged file hash mismatch: {destination}")


def _replace_loaded_aliases(
    original: Callable[..., Any], replacement: Callable[..., Any]
) -> list[tuple[Any, str]]:
    changed: list[tuple[Any, str]] = []
    for module_name, module in sorted(sys.modules.items()):
        if module is None:
            continue
        if not (
            module_name == "experiments.local_math_verifier.runtime"
            or module_name.startswith("cognitive_well_harness_")
        ):
            continue
        for name, value in list(vars(module).items()):
            if value is original:
                setattr(module, name, replacement)
                changed.append((module, name))
    return changed


@contextmanager
def runtime_generation_policy(
    *, model_timeout_sec: int = DEFAULT_MODEL_TIMEOUT_SEC
) -> Iterator[None]:
    """Apply Qwen's fixed 49k cap, Gemma's 32k floor, and role deadlines."""

    if not 30 <= model_timeout_sec <= 14_400:
        raise ValueError("model timeout must be between 30 and 14400 seconds")
    with _PATCH_LOCK:
        original = transport.run_openai_chat_generation

        def governed(**kwargs: Any) -> dict[str, Any]:
            config = kwargs.get("config")
            if config is None:
                raise ValueError("generation call has no HTTPGenerationConfig")
            kwargs = dict(kwargs)
            timeout = model_timeout_sec
            if (kwargs.get("model") == repair_boundary.QWEN_MODEL
                    and str(kwargs.get("stage", "")).startswith("reviewer2")):
                timeout = max(timeout, 2400)
            kwargs["config"] = replace(
                config,
                max_tokens=(repair_boundary.QWEN_MAX_OUTPUT_TOKENS
                            if kwargs.get("model") == repair_boundary.QWEN_MODEL
                            else min(65_536, max(32_768, int(getattr(config, "max_tokens"))))),
                timeout_seconds=timeout,
            )
            return original(**kwargs)

        changed = _replace_loaded_aliases(original, governed)
        transport.run_openai_chat_generation = governed
        try:
            yield
        finally:
            for module, name in reversed(changed):
                if getattr(module, name, None) is governed:
                    setattr(module, name, original)
            if transport.run_openai_chat_generation is governed:
                transport.run_openai_chat_generation = original


@contextmanager
def inherited_component_caps() -> Iterator[None]:
    """Keep Gemma's recovery rungs; give Qwen 49k initially, with physical cap recovery."""

    callables = (
        stage.run_original_reviewer,
        stage.run_compact_markdown_extractor,
        stage.run_v089_selector,
        stage.run_v092_selector,
        stage.reviewer_2.run_task,
        stage.reviewer_3.run_task,
        stage.fusion.run_task,
        v263._ORIGINAL_RESOLVER_RUN_TASK,
    )
    modules = tuple(
        dict.fromkeys(sys.modules[function.__module__] for function in callables)
    )
    saved: list[tuple[Any, str, Any]] = []
    for module in modules:
        if hasattr(module, "REVIEWER_INITIAL_MAX_TOKENS"):
            saved.append(
                (module, "REVIEWER_INITIAL_MAX_TOKENS", module.REVIEWER_INITIAL_MAX_TOKENS)
            )
            module.REVIEWER_INITIAL_MAX_TOKENS = 32_768
        if hasattr(module, "REVIEWER_RECOVERY_MAX_TOKENS"):
            saved.append(
                (
                    module,
                    "REVIEWER_RECOVERY_MAX_TOKENS",
                    module.REVIEWER_RECOVERY_MAX_TOKENS,
                )
            )
            module.REVIEWER_RECOVERY_MAX_TOKENS = (65_536, 65_536)
        for name, value in (
            ("MAX_OUTPUT_TOKENS", 32_768),
            ("CAP_RECOVERY_MAX_OUTPUT_TOKENS", 65_536),
            ("FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS", 65_536),
        ):
            if hasattr(module, name):
                saved.append((module, name, getattr(module, name)))
                setattr(module, name, value)
    reviewer2_module = sys.modules[stage.reviewer_2.run_task.__module__]
    for name, value in (
        ("MAX_OUTPUT_TOKENS", repair_boundary.QWEN_MAX_OUTPUT_TOKENS),
        ("TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS", repair_boundary.QWEN_MAX_OUTPUT_TOKENS),
        ("CAP_RECOVERY_MAX_OUTPUT_TOKENS", repair_boundary.QWEN_MAX_OUTPUT_TOKENS),
        ("RETRY_ON_OUTPUT_CAP", False),
    ):
        saved.append((reviewer2_module, name, getattr(reviewer2_module, name)))
        setattr(reviewer2_module, name, value)
    try:
        yield
    finally:
        for module, name, value in reversed(saved):
            setattr(module, name, value)


def _boundary_config() -> dict[str, Any]:
    value = _BOUNDARY_CONFIG
    if not isinstance(value, dict):
        raise RuntimeError("v0290 repair boundary context is not installed")
    return value


def _fusion_wrapper(original: Callable[..., dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    result = original(**kwargs)
    config = _boundary_config()
    return repair_boundary.audit_fusion_before_resolver(
        lane=Path(kwargs["output_dir"]).resolve(),
        task=kwargs["task"],
        source_result=result,
        qwen_endpoint=str(config["qwen_endpoint"]),
        gemma_endpoint=str(config["gemma_endpoint"]),
        cycle_key=str(config["cycle_key"]),
        model_timeout_sec=int(config["model_timeout_sec"]),
        enable_exact_evidence=bool(config["enable_exact_evidence"]),
    )


def _resolver_task_wrapper(
    original: Callable[..., dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    task = original(**kwargs)
    return bind_effective_fusion_task(
        task, fusion_result=kwargs["fusion_result"], cycle_key=_boundary_config()["cycle_key"]
    )


def bind_effective_fusion_task(
    task: dict[str, Any], *, fusion_result: dict[str, Any], cycle_key: str,
) -> dict[str, Any]:
    effective = fusion_result.get("_v290_effective_result_path")
    if effective:
        brief_gate = repair_boundary.boundary_record_from_effective(fusion_result)
        task["source_fusion_result_path"] = task["fusion_result_path"]
        task["fusion_result_path"] = str(Path(effective).resolve())
        task["fusion_decision_gate"] = {
            "required": True,
            "state": repair_boundary.repair_brief_disposition(brief_gate) if brief_gate else "CERTIFIED",
            "synthesis_allowed": True,
            "cycle_key": cycle_key,
        }
    return task


@contextmanager
def mandatory_repair_boundary(
    *,
    qwen_endpoint: str,
    gemma_endpoint: str,
    cycle_key: str,
    model_timeout_sec: int,
    enable_exact_evidence: bool = True,
) -> Iterator[None]:
    """Intercept every Fusion result before the unchanged Resolver."""

    global _BOUNDARY_CONFIG
    with _PATCH_LOCK:
        original_fusion = stage.fusion.run_task
        original_builder = stage.build_resolver_task
        previous = _BOUNDARY_CONFIG
        _BOUNDARY_CONFIG = {
            "qwen_endpoint": qwen_endpoint.rstrip("/"),
            "gemma_endpoint": gemma_endpoint.rstrip("/"),
            "cycle_key": cycle_key,
            "model_timeout_sec": model_timeout_sec,
            "enable_exact_evidence": enable_exact_evidence,
        }
        stage.fusion.run_task = lambda **kwargs: _fusion_wrapper(
            original_fusion, **kwargs
        )
        stage.build_resolver_task = lambda **kwargs: _resolver_task_wrapper(
            original_builder, **kwargs
        )
        try:
            yield
        finally:
            stage.fusion.run_task = original_fusion
            stage.build_resolver_task = original_builder
            _BOUNDARY_CONFIG = previous


@contextmanager
def effective_fusion_post_r1_loader(*, source_root: Path | None = None) -> Iterator[None]:
    """Make canonical v098 consume the certified Fusion seen by Resolver.

    The immutable pre-gate Fusion remains in place.  This process-local adapter
    replaces only the Fusion fields returned by v098's loader, after replaying
    the effective path and text hash from the bound Resolver task.
    """

    with _PATCH_LOCK:
        original = v108.v098.load_case

        def governed(phase2: Path, spec: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
            if source_root is None:
                case = original(phase2, spec, row)
            else:
                # A multi-lane run shares immutable inputs above the lane root.
                # Keep containment within the explicitly bound experiment root.
                _require_child(source_root, phase2, "post-R1 source stage")
                case = original(phase2, spec, row, source_root=source_root)
                if case["problem_sha256"] != spec["problem_sha256"]:
                    raise ValueError("post-R1 source problem hash drift")
                if sha256_text(Path(case["ancestor_proof_path"]).read_text(encoding="utf-8").strip()) != spec["proof_sha256"]:
                    raise ValueError("post-R1 source ancestor proof hash drift")
            case_id = str(case["case_id"])
            case_dir = Path(phase2).resolve() / "cases" / case_id
            resolver_result_path = _require_child(
                case_dir,
                Path(str(case["resolver_result_path"])),
                f"{case_id} Resolver result",
            )
            resolver_result = read_object(resolver_result_path)
            resolver_task = resolver_result.get("task")
            if not isinstance(resolver_task, dict):
                raise ValueError(f"missing bound Resolver task: {case_id}")
            source_path = _require_child(
                case_dir,
                Path(str(resolver_task.get("source_fusion_result_path") or "")),
                f"{case_id} immutable Fusion",
            )
            if Path(str(case["source_fusion_result"])).resolve() != source_path:
                raise ValueError(f"canonical v098 immutable Fusion drift: {case_id}")
            effective_path = _require_child(
                case_dir,
                Path(str(resolver_task.get("fusion_result_path") or "")),
                f"{case_id} effective Fusion",
            )
            effective_result = read_object(effective_path)
            effective_final = v108.v098.visible_result(effective_result, effective_path)
            effective_hash = sha256_text(effective_final)
            if effective_hash != str(resolver_task.get("fusion_record_sha256") or ""):
                raise ValueError(f"effective Fusion/Resolver binding drift: {case_id}")
            obligations = [
                item
                for item in case.get("obligations") or []
                if str(item.get("source") or "") != "fusion"
            ]
            obligation = v108.v098.fusion_obligation(effective_final)
            if obligation is not None:
                obligations.append(obligation)
            case["source_fusion_result"] = str(effective_path)
            case["source_fusion_final"] = effective_final
            case["obligations"] = v108.v098.exact_deduplicate_obligations(obligations)
            return case

        v108.v098.load_case = governed
        try:
            yield
        finally:
            if v108.v098.load_case is governed:
                v108.v098.load_case = original


def _case_manifest(
    *,
    problem_path: Path,
    proofs: list[dict[str, Any]],
    destination: Path,
    cycle: int,
) -> Path:
    cases = []
    by_id = {str(row["candidate_id"]): row for row in proofs}
    if len(by_id) != len(proofs) or not by_id or not set(by_id) <= set(CANDIDATE_IDS):
        raise ValueError("proof portfolio has duplicate, empty, or non-frozen candidates")
    for candidate_id in CANDIDATE_IDS:
        if candidate_id not in by_id:
            continue
        row = by_id[candidate_id]
        proof_path = Path(str(row["proof_path"])).resolve()
        proof = proof_path.read_text(encoding="utf-8").strip()
        proof_hash = sha256_text(proof)
        if proof_hash != str(row["proof_sha256"]):
            raise ValueError(f"source proof hash drift: {candidate_id}")
        cases.append(
            {
                "case_id": f"{PROBLEM_ID}.{candidate_id}",
                "mode": "fresh",
                "proof_index": CANDIDATE_IDS.index(candidate_id),
                "problem_path": str(problem_path.resolve()),
                "proof_path": str(proof_path),
                "problem_number": PROBLEM_NUMBER,
                "problem_id": PROBLEM_ID,
                "candidate_id": candidate_id,
                "v0290_cycle": cycle,
                "source_proof_sha256": proof_hash,
            }
        )
    value = {
        "schema": "cognitive-well-v0290-r1-cycle-cases-v1",
        "harness_version": HARNESS_VERSION,
        "contract_authority": PARENT_HARNESS_VERSION,
        "cycle": cycle,
        "cases": cases,
    }
    write_json(destination, value)
    return destination.resolve()


def run_r1_cycle_lane(
    *, output_dir: Path, candidate_id: str, cycle: int, source_proof: dict[str, Any],
    problem_path: Path, gemma_endpoint: str, qwen_endpoint: str,
    seed_namespace: str, model_timeout_sec: int,
) -> tuple[Path, dict[str, Any]]:
    """One existing R1 cycle; shared by the portfolio and mechanical recovery."""
    lane_root = output_dir / "lanes" / candidate_id
    cycle_dir = lane_root / f"{cycle:02d}_r1_cycle_{cycle}"
    if cycle_dir.exists():
        saved_cases = read_object(cycle_dir / "manifest.json")["cases"]
        if (len(saved_cases) != 1 or saved_cases[0]["candidate_id"] != candidate_id
                or saved_cases[0]["proof_sha256"] != source_proof["proof_sha256"]
                or saved_cases[0]["problem_sha256"] != EXPECTED_PROBLEM_SHA256):
            raise ValueError("saved reviews do not bind to the resumed proof")
    cases_path = _case_manifest(
        problem_path=problem_path, proofs=[source_proof],
        destination=lane_root / "input" / f"r1_cycle_{cycle}_cases.json", cycle=cycle,
    )
    stage.run(
        cases_manifest=cases_path, output_dir=cycle_dir,
        gemma_endpoints=[gemma_endpoint.rstrip("/")], qwen_endpoint=qwen_endpoint.rstrip("/"),
        workers_per_endpoint=1, seed_namespace=f"{seed_namespace}:{candidate_id}:r1_cycle_{cycle}",
        dry_run=False, allowed_input_root=output_dir,
    )
    terminal = _terminal_r1_proofs(
        stage_dir=cycle_dir, allowed_root=output_dir, expected_candidates=(candidate_id,),
        model_timeout_sec=model_timeout_sec,
    )[0]
    return cycle_dir, terminal


def _lazy_checked_portfolio(source_run: Path) -> dict[str, Any]:
    """Reuse the saved lazy-check outputs bound by the original review manifest."""
    source_run = source_run.resolve()
    phase_root = source_run / f"p{PROBLEM_NUMBER}/01_raw_lazy_enhanced_resolve"
    if (phase_root / "frontend_portfolio.json").is_file():
        partial = frontend_portfolio.load(phase_root, PROBLEM_NUMBER, PROBLEM_ID)
        if (partial["problem_sha256"] != EXPECTED_PROBLEM_SHA256
                or tuple(row["candidate_id"] for row in partial["proofs"]) != CANDIDATE_IDS):
            raise ValueError("Frontend portfolio identity drift")
        return partial
    manifest_path = phase_root / "phase_2_v096/manifest.json"
    manifest = read_object(manifest_path)
    cases_path = _require_child(
        source_run, Path(str(manifest["source_manifest_path"])), "lazy case manifest"
    )
    if cases_path != (phase_root / "phase_2_v096_cases.json").resolve():
        raise ValueError("lazy case manifest path drift")
    if file_sha256(cases_path) != manifest["source_manifest_sha256"]:
        raise ValueError("lazy case manifest hash drift")
    frozen_rows = manifest["cases"]
    input_rows = read_object(cases_path)["cases"]
    for rows in (frozen_rows, input_rows):
        if len(rows) != len(CANDIDATE_IDS) or {
            row["candidate_id"] for row in rows
        } != set(CANDIDATE_IDS):
            raise ValueError("lazy checked portfolio must contain all four unique lanes")
    by_id = {row["candidate_id"]: row for row in frozen_rows}
    input_by_id = {row["candidate_id"]: row for row in input_rows}
    problem_path = (phase_root / "input/problem.json").resolve()
    if sha256_text(str(read_object(problem_path).get("claim") or "").strip()) != EXPECTED_PROBLEM_SHA256:
        raise ValueError("lazy checked problem text hash drift")
    proofs = []
    for candidate_id in CANDIDATE_IDS:
        row = by_id[candidate_id]
        original = input_by_id[candidate_id]
        candidate_dir = phase_root / f"phase_1_raw_lazy/p{PROBLEM_NUMBER}/candidates" / candidate_id
        proof_path = _require_child(
            source_run, candidate_dir / "checked_proof.md", "lazy checked proof"
        )
        for bound_row in (row, original):
            if (
                bound_row.get("case_id") != f"{PROBLEM_ID}.{candidate_id}"
                or bound_row.get("problem_id") != PROBLEM_ID
                or Path(str(bound_row["proof_path"])).resolve() != proof_path
                or Path(str(bound_row["problem_path"])).resolve() != problem_path
            ):
                raise ValueError(f"lazy checked input identity/path drift: {candidate_id}")
        result_path = candidate_dir / "result.json"
        result = read_object(result_path)
        proof_hash = sha256_text(proof_path.read_text(encoding="utf-8").strip())
        if (
            row.get("problem_sha256") != EXPECTED_PROBLEM_SHA256
            or result.get("candidate_id") != candidate_id
            or Path(str(result["checked_proof_path"])).resolve() != proof_path
            or proof_hash != row.get("proof_sha256")
            or proof_hash != result.get("checked_proof_sha256")
        ):
            raise ValueError(f"lazy checked proof binding drift: {candidate_id}")
        proofs.append({
            "candidate_id": candidate_id,
            "source_proof_path": str(proof_path),
            "source_proof_sha256": proof_hash,
            "source_result_path": str(result_path.resolve()),
            "source_result_file_sha256": file_sha256(result_path),
        })
    return {"problem_path": str(problem_path), "proofs": proofs}


def _initial_inputs(
    *, source_run: Path, output_dir: Path, input_checkpoint: str = "resolver1"
) -> tuple[Path, list[dict[str, Any]]]:
    if input_checkpoint == "resolver1":
        source = v264.resolve_source_portfolio(source_run)
    elif input_checkpoint == "lazy_checked":
        source = _lazy_checked_portfolio(source_run)
    else:
        raise ValueError(f"unknown input checkpoint: {input_checkpoint}")
    input_dir = output_dir / "input"
    problem_path = input_dir / "problem.json"
    _stage_file(Path(source["problem_path"]), problem_path)
    proofs: list[dict[str, Any]] = []
    for row in source["proofs"]:
        candidate_id = str(row["candidate_id"])
        checkpoint = row.get("checkpoint", input_checkpoint)
        if row.get("source_failure") and not row.get("source_proof_path"):
            proofs.append({"candidate_id": candidate_id, "proof_path": None, "proof_sha256": None,
                           "source_checkpoint": checkpoint, "source_failure": row["source_failure"]})
            continue
        destination = input_dir / f"{checkpoint}_baseline" / f"{candidate_id}.md"
        _stage_file(Path(row["source_proof_path"]), destination)
        proof_hash = sha256_text(destination.read_text(encoding="utf-8").strip())
        if proof_hash != row["source_proof_sha256"]:
            raise ValueError(f"staged baseline proof drift: {candidate_id}")
        proofs.append(
            {
                "candidate_id": candidate_id,
                "proof_path": str(destination.resolve()),
                "proof_sha256": proof_hash,
                "source_proof_path": row["source_proof_path"],
                "source_proof_sha256": row["source_proof_sha256"],
                **({"source_failure": row["source_failure"], "source_checkpoint": checkpoint}
                   if row.get("source_failure") else {}),
            }
        )
    return problem_path.resolve(), proofs


def _raw_response_text(path: Path) -> str:
    raw = read_object(path)
    choices = raw.get("choices")
    message = (
        choices[0].get("message")
        if isinstance(choices, list)
        and len(choices) == 1
        and isinstance(choices[0], dict)
        else None
    )
    if not isinstance(message, dict):
        raise ValueError(f"model response is not one assistant message: {path}")
    return str(message.get("content") or "").strip()


def _verify_generation_producer(
    generation: dict[str, Any],
    *,
    allowed_root: Path,
    expected_model: str,
    expected_stage: str,
    expected_seed: int,
    expected_cap: int,
    expected_timeout_sec: int,
    expected_system_prompt: str,
    expected_user_prompt: str,
) -> str:
    """Replay one canonical mandatory-forcing generation from immutable inputs."""

    config = generation.get("config")
    forcing = generation.get("v0257_budget_forcing")
    unforced=single_model.active()
    expected_model=single_model.effective_model(expected_model)
    if (
        generation.get("model") != expected_model
        or generation.get("stage") != expected_stage
        or not isinstance(config, dict)
        or not repair_boundary.limit_policy.cap_matches(config, expected_cap, generation)
        or not repair_boundary.limit_policy.timeout_matches(config, expected_timeout_sec, generation)
        or int(config.get("seed") or -1) != expected_seed
        or (not unforced and (not isinstance(forcing, dict)
        or forcing.get("model") != expected_model
        or forcing.get("stage") != expected_stage
        or not timeout_policy.canonical_allowed(forcing)))
    ):
        raise ValueError(f"generation producer policy changed: {expected_stage}")
    prompt_path = _require_child(
        allowed_root,
        Path(str(generation.get("system_prompt_path") or "")),
        f"{expected_stage} system prompt",
    )
    user_prompt_path = _require_child(
        allowed_root,
        Path(str(generation.get("user_prompt_path") or "")),
        f"{expected_stage} user prompt",
    )
    response_path = _require_child(
        allowed_root,
        Path(str(generation.get("response_path") or "")),
        f"{expected_stage} response",
    )
    if prompt_path.read_text(encoding="utf-8") != expected_system_prompt:
        raise ValueError(f"{expected_stage} system prompt content changed")
    if user_prompt_path.read_text(encoding="utf-8") != expected_user_prompt:
        raise ValueError(f"{expected_stage} user prompt content changed")
    if generation.get("prompt_sha256") != sha256_text(expected_system_prompt):
        raise ValueError(f"{expected_stage} system prompt hash changed")
    if generation.get("user_prompt_sha256") != sha256_text(expected_user_prompt):
        raise ValueError(f"{expected_stage} user prompt hash changed")
    metadata_path = response_path.parent / f"{expected_stage}.metadata.json"
    budget_path = response_path.parent / f"{expected_stage}.budget_forcing.json"
    persisted_metadata = read_object(
        _require_child(allowed_root, metadata_path, "generation metadata")
    )
    timeout_policy.verify_fallback_artifacts(persisted_metadata, response_path.parent, expected_stage)
    embedded_canonical = {
        key: value
        for key, value in generation.items()
        if key != "v079_recovery_attempts"
    }
    if persisted_metadata != embedded_canonical:
        raise ValueError(f"{expected_stage} embedded/persisted metadata changed")
    if unforced:
        text=_raw_response_text(response_path)
        event=single_model.validate_unforced(generation,text)
        policy_path=_require_child(allowed_root,response_path.parent/f"{expected_stage}.generation_policy.json","unforced generation policy")
        if read_object(policy_path)!=event or budget_path.exists():
            raise ValueError("unforced producer event changed or unexpected forcing event exists")
        return text
    budget = read_object(
        _require_child(allowed_root, budget_path, "generation budget-forcing event")
    )
    text = _raw_response_text(response_path)
    text_hash = sha256_text(text)
    for event in (forcing, budget):
        if (
            event.get("model") != expected_model
            or event.get("stage") != expected_stage
            or not timeout_policy.canonical_allowed(event)
            or timeout_policy.canonical_hash(event) != text_hash
        ):
            raise ValueError(f"{expected_stage} forced-response binding changed")
    for name in ("original_config", "forced_config"):
        persisted = budget.get(name)
        if (
            not isinstance(persisted, dict)
            or not repair_boundary.limit_policy.cap_matches(persisted, expected_cap, generation)
            or not repair_boundary.limit_policy.timeout_matches(persisted, expected_timeout_sec, generation)
            or int(persisted.get("seed") or -1) != expected_seed
        ):
            raise ValueError(f"{expected_stage} {name} changed")
    return text


def _verify_resilient_ungrouped_generation(
    generation: dict[str, Any],
    *,
    allowed_root: Path,
    base_stage: str,
    base_seed_label: str,
    master_seed: int,
    model_timeout_sec: int,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Replay v0.3.79's exact full-replacement recovery, including its seed/prompt."""

    attempts = generation.get("v079_recovery_attempts")
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= 3:
        raise ValueError("ungrouped v079 recovery ledger changed")
    terminal_index = len(attempts) - 1
    for index, row in enumerate(attempts):
        expected_stage = base_stage if index == 0 else f"{base_stage}_replacement_{index}"
        if (
            not isinstance(row, dict)
            or int(row.get("attempt", -1)) != index
            or row.get("stage") != expected_stage
            or row.get("repetition_detection_preserved") is not True
            or bool(row.get("accepted")) is (index != terminal_index)
        ):
            raise ValueError("ungrouped v079 attempt history changed")
    terminal_stage = str(attempts[-1]["stage"])
    if generation.get("stage") != terminal_stage:
        raise ValueError("ungrouped v079 terminal stage changed")
    terminal_seed_label = (
        base_seed_label
        if terminal_index == 0
        else f"v079:{base_seed_label}:replacement:{terminal_index}"
    )
    runtime = v108.v103.v084.runtime_for(
        "http://127.0.0.1:1", master_seed, repair_boundary.GEMMA_MODEL
    )
    expected_seed = runtime.stable_seed(terminal_seed_label)
    effective_system = system_prompt
    if terminal_index:
        previous_stage = str(attempts[-2]["stage"])
        previous_path = (
            Path(str(generation.get("response_path") or "")).resolve().parent
            / f"{previous_stage}.raw_response.json"
        )
        partial = _raw_response_text(previous_path) if previous_path.is_file() else ""
        effective_system = (
            system_prompt.rstrip()
            + "\n\nTRANSPORT RECOVERY: The preceding response was empty or ended "
            + "at a repetition or length boundary. Produce a complete replacement "
            + "from the beginning. Do not continue or reproduce the repeated suffix. "
            + "Preserve correct task content only.\n\nPRIOR INCOMPLETE RESPONSE:\n"
            + partial.rstrip()[-12_000:]
        )
    return _verify_generation_producer(
        generation,
        allowed_root=allowed_root,
        expected_model=repair_boundary.GEMMA_MODEL,
        expected_stage=terminal_stage,
        expected_seed=expected_seed,
        expected_cap=32_768,
        expected_timeout_sec=model_timeout_sec,
        expected_system_prompt=effective_system,
        expected_user_prompt=user_prompt,
    )


def _verify_resolver_producer(
    *,
    resolver_result_path: Path,
    case_dir: Path,
    allowed_root: Path,
    model_timeout_sec: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    resolver_result = read_object(resolver_result_path)
    final = str(resolver_result.get("final") or "").strip()
    if not final or sha256_text(final) != str(resolver_result.get("final_sha256") or ""):
        raise ValueError("Resolver final text/hash changed")
    task = resolver_result.get("task")
    if not isinstance(task, dict):
        raise ValueError("Resolver task is missing")
    if resolver_result.get("response_source") != "live":
        raise ValueError("Resolver result is not a fresh live result")
    problem_path = _require_child(
        allowed_root,
        Path(str(task.get("problem_path") or "")),
        "Resolver problem",
    )
    proof_path = _require_child(
        allowed_root,
        Path(str(task.get("proof_path") or "")),
        "Resolver submitted proof",
    )
    fusion_path = _require_child(
        case_dir,
        Path(str(task.get("fusion_result_path") or "")),
        "Resolver effective Fusion",
    )
    problem_payload = read_object(problem_path)
    problem = str(problem_payload.get("claim") or "").strip()
    proof = proof_path.read_text(encoding="utf-8").strip()
    fusion = str(read_object(fusion_path).get("final") or "").strip()
    if (
        sha256_text(problem) != str(task.get("problem_sha256") or "")
        or sha256_text(proof) != str(task.get("proof_sha256") or "")
        or sha256_text(fusion) != str(task.get("fusion_record_sha256") or "")
    ):
        raise ValueError("Resolver immutable mathematical inputs changed")
    fusion_parsed = stage.resolver.parse_fusion(fusion)
    if not fusion_parsed.get("valid"):
        raise ValueError("Resolver effective Fusion is invalid")

    def parse_record(value: str) -> dict[str, Any]:
        with v263.resolver_fusion_context(str(fusion_parsed.get("outcome") or "")):
            return stage.resolver.parse_resolution(value)

    parsed = parse_record(final)
    if not parsed.get("valid") or parsed != resolver_result.get("parsed"):
        raise ValueError("Resolver parsed result changed")
    system_prompt = stage.resolver.SYSTEM_PROMPT
    user_prompt = stage.resolver.resolver_user_prompt(
        problem=problem, proof=proof, fusion_record=fusion
    )
    seed = int(task.get("seed") or -1)
    identity = resolver_result.get("identity")
    if (
        seed < 0
        or not isinstance(identity, dict)
        or identity.get("system_prompt_sha256") != sha256_text(system_prompt)
        or identity.get("user_prompt_sha256") != sha256_text(user_prompt)
        or int(identity.get("max_output_tokens") or 0) != 32_768
        or int(identity.get("cap_recovery_max_output_tokens") or 0) != 65_536
    ):
        raise ValueError("Resolver frozen identity changed")
    primary = resolver_result.get("generation")
    if not isinstance(primary, dict):
        raise ValueError("Resolver primary producer metadata is missing")
    primary_text = _verify_generation_producer(
        primary,
        allowed_root=case_dir,
        expected_model=repair_boundary.GEMMA_MODEL,
        expected_stage="resolver",
        expected_seed=seed,
        expected_cap=32_768,
        expected_timeout_sec=model_timeout_sec,
        expected_system_prompt=system_prompt,
        expected_user_prompt=user_prompt,
    )
    recovery = resolver_result.get("recovery")
    if not isinstance(recovery, dict):
        raise ValueError("Resolver recovery ledger is missing")
    cap_triggered = primary.get("finish_reason") == "length"
    if recovery.get("triggered") is not cap_triggered:
        raise ValueError("Resolver cap-continuation trigger changed")
    cleanup = primary.get("cap_repetition_cleanup") or {}
    if cap_triggered and cleanup.get("detected"):
        primary_text = (primary_text[:cleanup["kept_characters"]].strip()
                        if cleanup["channel"] == "text" else "")
    candidate = primary_text
    terminal_generation = primary
    if cap_triggered:
        continuation = recovery.get("continuation_generation")
        if (
            not isinstance(continuation, dict)
            or int(recovery.get("primary_max_output_tokens") or 0) != 32_768
            or int(recovery.get("recovery_max_output_tokens") or 0) != 65_536
        ):
            raise ValueError("Resolver continuation producer is missing")
        continuation_text = _verify_generation_producer(
            continuation,
            allowed_root=case_dir,
            expected_model=repair_boundary.GEMMA_MODEL,
            expected_stage="resolver_cap_continuation",
            expected_seed=(seed + 1_000_003) & 0xFFFFFFFF,
            expected_cap=65_536,
            expected_timeout_sec=model_timeout_sec,
            expected_system_prompt=system_prompt,
            expected_user_prompt=user_prompt,
        )
        if continuation.get("finish_reason") == "length":
            raise ValueError("completed Resolver exhausted its continuation cap")
        candidate = (
            continuation_text
            if parse_record(continuation_text).get("valid")
            else stage.resolver.merge_continuation(primary_text, continuation_text)
        )
        terminal_generation = continuation
    elif "continuation_generation" in recovery:
        raise ValueError("Resolver has an untriggered continuation producer")
    protocol = recovery.get("protocol_repair")
    candidate_valid = bool(parse_record(candidate).get("valid"))
    if candidate_valid and protocol is not None:
        raise ValueError("Resolver ran protocol repair on a valid record")
    if not candidate_valid:
        if not isinstance(protocol, dict) or protocol.get("triggered") is not True:
            raise ValueError("Resolver invalid record lacks protocol repair")
        if protocol.get("initial_errors") != parse_record(candidate).get("errors"):
            raise ValueError("Resolver protocol-repair trigger errors changed")
        repair_generation = protocol.get("generation")
        if not isinstance(repair_generation, dict):
            raise ValueError("Resolver protocol-repair producer is missing")
        candidate = _verify_generation_producer(
            repair_generation,
            allowed_root=case_dir,
            expected_model=repair_boundary.GEMMA_MODEL,
            expected_stage="resolver_protocol_repair",
            expected_seed=(seed + 3_000_009) & 0xFFFFFFFF,
            expected_cap=32_768,
            expected_timeout_sec=model_timeout_sec,
            expected_system_prompt=system_prompt,
            expected_user_prompt=user_prompt,
        )
        terminal_generation = repair_generation
    if candidate != final:
        raise ValueError("Resolver producer chain does not reconstruct terminal final")
    if resolver_result.get("final_generation") != terminal_generation:
        raise ValueError("Resolver final_generation does not identify terminal producer")
    return resolver_result, parsed


def _reconstruct_gate_task(
    *,
    fusion_result: dict[str, Any],
    spec: dict[str, Any],
    case_dir: Path,
    allowed_root: Path,
) -> dict[str, Any]:
    """Rebuild the exact Fusion-boundary packet from immutable R1 artifacts."""

    source_task = fusion_result.get("task")
    if not isinstance(source_task, dict):
        raise ValueError("source Fusion task metadata is missing")
    source_final = str(fusion_result.get("final") or "").strip()
    source_parsed = stage.resolver.parse_fusion(source_final)
    if (
        not source_parsed.get("valid")
        or source_parsed != fusion_result.get("parsed")
        or sha256_text(source_final) != str(fusion_result.get("final_sha256") or "")
    ):
        raise ValueError("source Fusion terminal artifact changed")
    problem_path = _require_child(
        allowed_root, Path(str(spec.get("problem_path") or "")), "R1 problem"
    )
    proof_path = _require_child(
        allowed_root, Path(str(spec.get("proof_path") or "")), "R1 submitted proof"
    )
    problem = str(read_object(problem_path).get("claim") or "").strip()
    proof = proof_path.read_text(encoding="utf-8").strip()
    if (
        sha256_text(problem) != EXPECTED_PROBLEM_SHA256
        or sha256_text(proof) != str(spec.get("proof_sha256") or "")
        or source_task.get("problem_id") != PROBLEM_ID
        or source_task.get("candidate_id") != spec.get("candidate_id")
        or source_task.get("problem_sha256") != sha256_text(problem)
        or source_task.get("proof_sha256") != sha256_text(proof)
    ):
        raise ValueError("source Fusion mathematical identity changed")
    reviewer_sources = source_task.get("reviewer_sources")
    if not isinstance(reviewer_sources, dict):
        raise ValueError("source Fusion reviewer provenance is missing")
    task = {
        "problem": problem,
        "proof": proof,
        "proof_sha256": sha256_text(proof),
        "task_id": str(source_task.get("task_id") or ""),
        "candidate_id": str(spec.get("candidate_id") or ""),
    }
    if task["task_id"] != f"{PROBLEM_ID}.{task['candidate_id']}.fusion.t04":
        raise ValueError("source Fusion task id changed")
    for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
        reviewer_path = _require_child(
            case_dir, case_dir / f"effective_{role}.txt", f"effective {role}"
        )
        reviewer = reviewer_path.read_text(encoding="utf-8").strip()
        provenance = reviewer_sources.get(role)
        if (
            not reviewer
            or not isinstance(provenance, dict)
            or sha256_text(reviewer) != str(provenance.get("final_sha256") or "")
            or str(provenance.get("proof_sha256") or "") != sha256_text(proof)
        ):
            raise ValueError(f"source Fusion {role} input changed")
        task[role] = reviewer
    return task


def _terminal_r1_proofs(
    *,
    stage_dir: Path,
    allowed_root: Path,
    expected_candidates: tuple[str, ...],
    model_timeout_sec: int,
) -> list[dict[str, Any]]:
    summary = read_object(stage_dir / "summary.json")
    manifest = read_object(stage_dir / "manifest.json")
    if summary.get("state") != "completed":
        raise ValueError(f"R1 cycle did not complete: {stage_dir}")
    specs = {str(row["candidate_id"]): row for row in manifest.get("cases") or []}
    rows = {str(row["candidate_id"]): row for row in summary.get("rows") or []}
    if set(specs) != set(expected_candidates) or set(rows) != set(expected_candidates):
        raise ValueError("R1 terminal portfolio identity drift")
    proofs: list[dict[str, Any]] = []
    for candidate_id in expected_candidates:
        case_id = f"{PROBLEM_ID}.{candidate_id}"
        row = rows[candidate_id]
        if row.get("case_id") not in {None, case_id}:
            raise ValueError(f"R1 summary case identity drift: {candidate_id}")
        spec = specs[candidate_id]
        if (
            spec.get("case_id") != case_id
            or spec.get("problem_id") != PROBLEM_ID
            or spec.get("candidate_id") != candidate_id
        ):
            raise ValueError(f"R1 manifest case identity drift: {candidate_id}")
        case_dir = stage_dir / "cases" / case_id
        handoff_path = _require_child(
            case_dir,
            Path(str(row["resolver_trace_handoff"])),
            f"{candidate_id} trace handoff",
        )
        handoff = read_object(handoff_path)
        resolver_result_path = _require_child(
            case_dir,
            Path(str(handoff["resolver_result_path"])),
            f"{candidate_id} resolver result",
        )
        if file_sha256(resolver_result_path) != str(
            handoff.get("resolver_result_sha256") or ""
        ):
            raise ValueError(f"resolver result file hash drift: {candidate_id}")
        resolver_result, resolver_parsed = _verify_resolver_producer(
            resolver_result_path=resolver_result_path,
            case_dir=case_dir,
            allowed_root=allowed_root,
            model_timeout_sec=model_timeout_sec,
        )
        resolver_task = resolver_result.get("task")
        if not isinstance(resolver_task, dict):
            raise ValueError(f"missing bound Resolver task: {candidate_id}")
        if (
            resolver_task.get("problem_id") != PROBLEM_ID
            or resolver_task.get("candidate_id") != candidate_id
            or str(resolver_task.get("problem_sha256") or "")
            != EXPECTED_PROBLEM_SHA256
            or str(resolver_task.get("proof_sha256") or "")
            != str(spec.get("proof_sha256") or "")
        ):
            raise ValueError(f"Resolver task source identity drift: {candidate_id}")
        resolver_outcome = str(resolver_parsed.get("outcome") or "")
        if (
            not resolver_parsed.get("valid")
            or resolver_outcome != str(handoff.get("resolver_outcome") or "")
            or resolver_outcome != str(row.get("resolver_outcome") or "")
        ):
            raise ValueError(f"Resolver outcome drift: {candidate_id}")
        proof_path = v108.v098.authorized_terminal_proof_path(
            case_dir=case_dir,
            source_root=allowed_root,
            original_proof_path=Path(str(spec["proof_path"])),
            handoff_proof_path=Path(str(handoff["proof_path"])),
            resolver_outcome=str(row.get("resolver_outcome") or ""),
            case_id=case_id,
        )
        proof_hash = sha256_text(proof_path.read_text(encoding="utf-8").strip())
        if proof_hash != handoff.get("proof_sha256"):
            raise ValueError(f"terminal proof hash drift: {candidate_id}")
        if resolver_outcome == "RESOLVED_PROOF" and str(
            resolver_parsed.get("proof") or ""
        ).strip() != proof_path.read_text(encoding="utf-8").strip():
            raise ValueError(f"Resolver parsed proof/artifact drift: {candidate_id}")
        fusion_result_path = _require_child(
            case_dir / "fusion",
            Path(str(resolver_task.get("source_fusion_result_path") or "")),
            f"{candidate_id} source Fusion result",
        )
        if not fusion_result_path.is_file():
            raise FileNotFoundError(fusion_result_path)
        fusion_result = read_object(fusion_result_path)
        fusion_outcome = str((fusion_result.get("parsed") or {}).get("outcome") or "")
        repair_gate_path = (
            stage_dir
            / "cases"
            / f"{PROBLEM_ID}.{candidate_id}"
            / "fusion_repair_brief_audit_rewrite/result.json"
        )
        acceptance_gate_path = (
            stage_dir
            / "cases"
            / f"{PROBLEM_ID}.{candidate_id}"
            / "fusion_acceptance_audit/result.json"
        )
        if fusion_outcome == "REPAIR_NEEDED":
            if not repair_gate_path.is_file():
                raise ValueError(f"missing mandatory repair-brief gate: {candidate_id}")
            gate = read_object(repair_gate_path)
            repair_boundary.repair_brief_disposition(gate)
            effective_gate_path = repair_gate_path.parent / "effective_fusion_result.json"
            effective_hash = str(gate.get("effective_fusion_sha256") or "")
        elif fusion_outcome in {
            "ACCEPT_AS_WRITTEN",
            "ACCEPT_WITH_ROUTINE_COMPLETION",
        }:
            if not acceptance_gate_path.is_file():
                raise ValueError(f"missing mandatory acceptance gate: {candidate_id}")
            gate = read_object(acceptance_gate_path)
            if gate.get("state") != "completed":
                raise ValueError(f"uncertified accepting Fusion reached Resolver: {candidate_id}")
            if (
                gate.get("certified_acceptance_round") is None
                and not isinstance(gate.get("repair_brief_gate"), dict)
            ):
                raise ValueError(f"acceptance gate has no certified route: {candidate_id}")
            effective_gate_path = acceptance_gate_path.parent / "effective_fusion_result.json"
            effective_hash = str(gate.get("effective_fusion_sha256") or "")
        else:
            raise ValueError(
                f"unsupported Fusion outcome reached Resolver: {candidate_id}: {fusion_outcome}"
            )
        if str(gate.get("source_fusion_sha256") or "") != sha256_text(
            str(fusion_result.get("final") or "").strip()
        ):
            raise ValueError(f"Fusion gate source hash drift: {candidate_id}")
        effective_gate = read_object(
            _require_child(stage_dir, effective_gate_path, f"{candidate_id} effective Fusion")
        )
        effective_final = str(effective_gate.get("final") or "").strip()
        if sha256_text(effective_final) != effective_hash:
            raise ValueError(f"effective Fusion hash drift: {candidate_id}")
        gate_task = _reconstruct_gate_task(
            fusion_result=fusion_result,
            spec=spec,
            case_dir=case_dir,
            allowed_root=allowed_root,
        )
        repair_boundary.verify_gate_producer_history(
            gate,
            allowed_root=case_dir,
            source_fusion=str(fusion_result.get("final") or ""),
            effective_fusion=effective_final,
            task=gate_task,
        )
        if str(resolver_task.get("fusion_result_path") or "") != str(
            effective_gate_path.resolve()
        ):
            raise ValueError(f"Resolver did not consume gated Fusion path: {candidate_id}")
        if str(resolver_task.get("fusion_record_sha256") or "") != effective_hash:
            raise ValueError(f"Resolver did not consume gated Fusion text: {candidate_id}")
        proofs.append(
            {
                "candidate_id": candidate_id,
                "proof_path": str(proof_path),
                "proof_sha256": proof_hash,
                "resolver_outcome": row.get("resolver_outcome"),
                "fusion_outcome": fusion_outcome,
                "repair_brief_gate_path": (
                    str(repair_gate_path.resolve()) if repair_gate_path.is_file() else None
                ),
                "acceptance_gate_path": (
                    str(acceptance_gate_path.resolve())
                    if acceptance_gate_path.is_file()
                    else None
                ),
            }
        )
    return proofs


def _r1_checkpoint(
    *, cycle: int, stage_dir: Path, proofs: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "checkpoint": f"R1-C{cycle}",
        "stage_dir": str(stage_dir.resolve()),
        "proofs": [dict(row) for row in proofs],
        "strict_score_model_visible": False,
    }


def _proof_identity(row: dict[str, Any], *, allowed_root: Path, label: str) -> tuple[Path, str]:
    path = _require_child(
        allowed_root, Path(str(row.get("proof_path") or "")), f"{label} proof"
    )
    proof = path.read_text(encoding="utf-8").strip()
    digest = sha256_text(proof)
    if digest != str(row.get("proof_sha256") or ""):
        raise ValueError(f"{label} proof hash changed")
    return path, digest


def _verify_ungrouped_result(
    *,
    result_path: Path,
    stage_root: Path,
    allowed_root: Path,
    case: dict[str, Any],
    expected_source: dict[str, Any],
    seed_namespace: str,
    model_timeout_sec: int,
) -> tuple[Path, str]:
    result_path = _require_child(stage_root, result_path, "ungrouped result")
    result = read_object(result_path)
    case_id = str(case["case_id"])
    candidate_id = str(case["candidate_id"])
    source_path, source_hash = _proof_identity(
        expected_source, allowed_root=allowed_root, label="upstream"
    )
    if (
        result.get("case_id") != case_id
        or result.get("problem_id") != PROBLEM_ID
        or result.get("candidate_id") != candidate_id
        or Path(str(result.get("source_proof_path") or "")).resolve()
        != source_path.resolve()
        or str(result.get("source_proof_sha256") or "") != source_hash
        or Path(str(case.get("proof_path") or "")).resolve() != source_path.resolve()
        or str(case.get("proof_sha256") or "") != source_hash
    ):
        raise ValueError(f"ungrouped source identity changed: {candidate_id}")
    proof_path = _require_child(
        stage_root,
        Path(str(result.get("resolved_proof_path") or "")),
        f"{candidate_id} ungrouped proof",
    )
    proof = proof_path.read_text(encoding="utf-8").strip()
    proof_hash = sha256_text(proof)
    if proof_hash != str(result.get("resolved_proof_sha256") or ""):
        raise ValueError(f"ungrouped output proof changed: {candidate_id}")
    state = str(result.get("state") or "")
    if state == "skipped_no_active_obligations":
        if (
            case.get("active_entries")
            or result.get("generation") is not None
            or result.get("runtime_recovery_events") != []
            or int(result.get("mandatory_ungrouped_obligation_count", -1)) != 0
            or proof_hash != source_hash
            or proof_path.read_bytes() != source_path.read_bytes()
        ):
            raise ValueError(f"invalid ungrouped unchanged route: {candidate_id}")
        return proof_path, proof_hash
    if state != "completed" or not case.get("active_entries"):
        raise ValueError(f"invalid ungrouped generated route: {candidate_id}")
    if (
        result.get("schema") != "cognitive-well-v0103-ungrouped-ledger-resolve-v1"
        or float(result.get("temperature", -1)) != v108.v103.TEMPERATURE
        or int(result.get("max_tokens") or 0) != 32_768
        or
        int(result.get("mandatory_ungrouped_obligation_count", -1))
        != len(case["active_entries"])
        or int(result.get("archived_obligation_count", -1))
        != len(case["archived_entries"])
    ):
        raise ValueError(f"ungrouped obligation counts changed: {candidate_id}")
    system_prompt = v108.v103.RESOLVER_SYSTEM_PROMPT
    user_prompt = v108.v103.resolver_user_prompt(case)
    identity = sha256_text(system_prompt + user_prompt)[:12]
    stage_name = f"ungrouped_current_ledger_complete_proof_resolve_{identity}"
    label = f"{seed_namespace}:{case_id}:ungrouped_resolve:{identity}"
    master_seed = v108.v103.v099.stable_seed(label)
    generation = result.get("generation")
    if not isinstance(generation, dict):
        raise ValueError(f"ungrouped generation metadata is missing: {candidate_id}")
    raw_text = _verify_resilient_ungrouped_generation(
        generation,
        allowed_root=stage_root,
        base_stage=stage_name,
        base_seed_label=label,
        master_seed=master_seed,
        model_timeout_sec=model_timeout_sec,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    if raw_text != proof:
        raise ValueError(f"ungrouped producer/output proof changed: {candidate_id}")
    events = result.get("runtime_recovery_events")
    attempts = generation.get("v079_recovery_attempts")
    if (
        not isinstance(events, list)
        or len(events) != 1
        or events[0].get("kind") != "text"
        or events[0].get("stage") != stage_name
        or events[0].get("accepted") is not True
        or events[0].get("attempts") != attempts
    ):
        raise ValueError(f"ungrouped recovery event changed: {candidate_id}")
    return proof_path, proof_hash


def _validate_saved_post_r1_gate(
    *, gate_dir: Path, source_dir: Path, source_root: Path, expected_source: dict[str, Any],
    loader_is_bound: bool = False, require_completed: bool = True,
) -> None:
    manifest = read_object(gate_dir / "manifest.json")
    summary = read_object(gate_dir / "summary.json") if (gate_dir / "summary.json").is_file() else {}
    if ((require_completed and summary.get("state") != "completed")
            or manifest.get("source_runs") != [str(source_dir.resolve())]):
        raise ValueError("saved post-R1 gate is incomplete or has a different source")
    if loader_is_bound:
        case, = v108.v098.load_source_runs([source_dir])
    else:
        with effective_fusion_post_r1_loader(source_root=source_root):
            case, = v108.v098.load_source_runs([source_dir])
    spec, = manifest["cases"]
    for key in ("case_id", "problem_id", "candidate_id", "problem_path", "problem_sha256",
                "proof_path", "proof_sha256", "resolver_result_path", "resolver_result_sha256",
                "source_trace_handoff", "source_fusion_result", "obligations"):
        if spec.get(key) != case.get(key):
            raise ValueError(f"saved post-R1 gate source drift: {key}")
    for key in ("candidate_id", "proof_path", "proof_sha256"):
        if case[key] != expected_source[key]:
            raise ValueError(f"saved post-R1 gate proof drift: {key}")
    if not require_completed:
        return
    row, = summary["rows"]
    if any(row[key] != case[key] for key in ("candidate_id", "proof_path", "proof_sha256")):
        raise ValueError("saved post-R1 gate summary proof drift")
    case_dir = gate_dir / "cases" / case["case_id"]
    result = read_object(case_dir / "gate_result.json")
    ledger = read_object(case_dir / "updated_obligation_ledger.json")
    if (result.get("proof_sha256") != case["proof_sha256"]
            or result.get("outcome") != row.get("outcome")
            or ledger.get("proof_sha256") != case["proof_sha256"]
            or result.get("updated_obligation_ledger") != ledger):
        raise ValueError("saved post-R1 gate result/ledger drift")


def _second_checkpoint(
    second_dir: Path,
    *,
    allowed_root: Path,
    expected_candidates: tuple[str, ...],
    expected_sources: list[dict[str, Any]],
    source_run: Path,
    seed_namespace: str,
    model_timeout_sec: int,
) -> dict[str, Any]:
    summary = read_object(second_dir / "summary.json")
    manifest = read_object(second_dir / "manifest.json")
    if summary.get("state") != "completed":
        raise ValueError(f"R2 did not complete: {second_dir}")
    source_run = source_run.resolve()
    if (
        manifest.get("schema")
        != "cognitive-well-v0103-ungrouped-ledger-resolve-manifest-v1"
        or Path(str(manifest.get("source_run") or "")).resolve() != source_run
        or manifest.get("problem_id") != PROBLEM_ID
        or manifest.get("model") != repair_boundary.GEMMA_MODEL
        or float(manifest.get("temperature", -1)) != v108.v103.TEMPERATURE
        or int(manifest.get("max_tokens") or 0) != 32_768
    ):
        raise ValueError("R2 manifest policy changed")
    source_rows = summary.get("rows") or []
    by_id = {str(row.get("candidate_id")): row for row in source_rows}
    if len(by_id) != len(source_rows) or set(by_id) != set(expected_candidates):
        raise ValueError("R2 terminal portfolio identity drift")
    sources = {str(row["candidate_id"]): row for row in expected_sources}
    specs = {str(row["candidate_id"]): row for row in manifest.get("cases") or []}
    cases = {
        str(row["candidate_id"]): row
        for row in v108._direct_ungrouped_cases(
            source_run=source_run, problem_id=PROBLEM_ID
        )
    }
    if set(sources) != set(expected_candidates) or set(specs) != set(expected_candidates):
        raise ValueError("R2 source/manifest portfolio identity drift")
    if set(cases) != set(expected_candidates):
        raise ValueError("R2 reconstructed source cases changed")
    rows = []
    for candidate_id in expected_candidates:
        row = by_id[candidate_id]
        if row.get("case_id") not in {None, f"{PROBLEM_ID}.{candidate_id}"}:
            raise ValueError(f"R2 case identity drift: {candidate_id}")
        spec = specs[candidate_id]
        source_path, source_hash = _proof_identity(
            sources[candidate_id], allowed_root=allowed_root, label=f"{candidate_id} R1"
        )
        if (
            spec.get("case_id") != f"{PROBLEM_ID}.{candidate_id}"
            or spec.get("problem_id") != PROBLEM_ID
            or Path(str(spec.get("proof_path") or "")).resolve() != source_path
            or str(spec.get("proof_sha256") or "") != source_hash
        ):
            raise ValueError(f"R2 manifest case changed: {candidate_id}")
        result_path = (
            second_dir
            / "cases"
            / f"{PROBLEM_ID}.{candidate_id}"
            / "gemma_ungrouped_ledger_resolve"
            / "result.json"
        )
        proof_path, proof_hash = _verify_ungrouped_result(
            result_path=result_path,
            stage_root=second_dir,
            allowed_root=allowed_root,
            case=cases[candidate_id],
            expected_source=sources[candidate_id],
            seed_namespace=seed_namespace,
            model_timeout_sec=model_timeout_sec,
        )
        if (
            Path(str(row.get("resolved_proof_path") or "")).resolve() != proof_path
            or str(row.get("resolved_proof_sha256") or "") != proof_hash
        ):
            raise ValueError(f"R2 summary/result proof drift: {candidate_id}")
        rows.append(
            {
                "candidate_id": candidate_id,
                "proof_path": str(proof_path),
                "proof_sha256": proof_hash,
            }
        )
    return {"checkpoint": "R2", "stage_dir": str(second_dir), "proofs": rows}


def _third_checkpoint(
    third_dir: Path,
    *,
    allowed_root: Path,
    expected_candidates: tuple[str, ...],
    expected_sources: list[dict[str, Any]],
    resolve_run: Path,
    prior_gate_run: Path,
    seed_namespace: str,
    model_timeout_sec: int,
) -> dict[str, Any]:
    summary = read_object(third_dir / "summary.json")
    manifest = read_object(third_dir / "manifest.json")
    if summary.get("state") != "completed":
        raise ValueError(f"R3 did not complete: {third_dir}")
    if (
        manifest.get("schema")
        != "cognitive-well-v0105-iterated-ungrouped-resolve-manifest-v1"
        or [Path(str(path)).resolve() for path in manifest.get("source_resolve_runs") or []]
        != [resolve_run.resolve()]
        or Path(str(manifest.get("prior_gate_run") or "")).resolve()
        != prior_gate_run.resolve()
        or (manifest.get("models") or {}).get("gemma")
        != repair_boundary.GEMMA_MODEL
    ):
        raise ValueError("R3 manifest policy changed")
    source_rows = summary.get("rows") or []
    by_id = {str(row.get("candidate_id")): row for row in source_rows}
    if len(by_id) != len(source_rows) or set(by_id) != set(expected_candidates):
        raise ValueError("R3 terminal portfolio identity drift")
    sources = {str(row["candidate_id"]): row for row in expected_sources}
    specs = {str(row["candidate_id"]): row for row in manifest.get("cases") or []}
    reconstructed = {
        str(row["candidate_id"]): row
        for row in v108.v105.load_cases(
            resolve_runs=[resolve_run], prior_gate_run=prior_gate_run, source_root=allowed_root
        )
    }
    if set(sources) != set(expected_candidates) or set(specs) != set(expected_candidates):
        raise ValueError("R3 source/manifest portfolio identity drift")
    if set(reconstructed) != set(expected_candidates):
        raise ValueError("R3 reconstructed source cases changed")
    rows = []
    for candidate_id in expected_candidates:
        row = by_id[candidate_id]
        if row.get("case_id") not in {None, f"{PROBLEM_ID}.{candidate_id}"}:
            raise ValueError(f"R3 case identity drift: {candidate_id}")
        state = str(row.get("third_resolve_state") or "")
        if state not in {
            "completed",
            "promoted_unchanged_no_second_cycle",
            "skipped_no_active_obligations",
        }:
            raise ValueError(f"R3 terminal state invalid: {candidate_id}: {state}")
        source_path, source_hash = _proof_identity(
            sources[candidate_id], allowed_root=allowed_root, label=f"{candidate_id} R2"
        )
        spec = specs[candidate_id]
        if (
            spec.get("case_id") != f"{PROBLEM_ID}.{candidate_id}"
            or spec.get("problem_id") != PROBLEM_ID
            or Path(str(spec.get("second_proof_path") or "")).resolve() != source_path
            or str(spec.get("second_proof_sha256") or "") != source_hash
            or Path(str(row.get("second_proof_path") or "")).resolve() != source_path
            or str(row.get("second_proof_sha256") or "") != source_hash
        ):
            raise ValueError(f"R3 upstream source identity changed: {candidate_id}")
        if state == "completed":
            case = reconstructed[candidate_id]
            ledger_path = _require_child(
                third_dir,
                third_dir
                / "cases"
                / f"{PROBLEM_ID}.{candidate_id}"
                / "updated_obligation_ledger.json",
                f"{candidate_id} updated ledger",
            )
            ledger = read_object(ledger_path)
            active = list(ledger.get("active_obligations") or [])
            entries = list(ledger.get("entries") or [])
            resolver_case = case | {
                "active_entries": active,
                "archived_entries": [
                    item
                    for item in entries
                    if str(item.get("status") or "").upper()
                    in v108.v105.ARCHIVE_STATUSES
                ],
            }
            primary_result = (
                third_dir
                / "cases"
                / f"{PROBLEM_ID}.{candidate_id}"
                / "third_ungrouped_resolve"
                / "result.json"
            )
            retry_result = (
                primary_result.parent.parent
                / v263.THIRD_RESOLVE_RETRY_DIRECTORY
                / "result.json"
            )
            if primary_result.is_file() == retry_result.is_file():
                raise ValueError(f"R3 generated route is ambiguous: {candidate_id}")
            result_path = primary_result if primary_result.is_file() else retry_result
            effective_seed_namespace = seed_namespace
            if result_path == retry_result:
                recovery_path = retry_result.parent / "v0263_repetition_recovery.json"
                recovery = read_object(recovery_path)
                if (
                    recovery.get("state") != "completed"
                    or recovery.get("case_id") != f"{PROBLEM_ID}.{candidate_id}"
                    or recovery.get("retry_result_sha256") != file_sha256(retry_result)
                    or recovery.get("fresh_seed_namespace")
                    != f"{seed_namespace}:v0263:fresh_retry1"
                ):
                    raise ValueError(f"R3 fresh retry provenance changed: {candidate_id}")
                effective_seed_namespace = str(recovery["fresh_seed_namespace"])
            proof_path, proof_hash = _verify_ungrouped_result(
                result_path=result_path,
                stage_root=third_dir,
                allowed_root=allowed_root,
                case=resolver_case,
                expected_source=sources[candidate_id],
                seed_namespace=effective_seed_namespace,
                model_timeout_sec=model_timeout_sec,
            )
        else:
            proof_path = _require_child(
                (
                    third_dir
                    if state == "promoted_unchanged_no_second_cycle"
                    else allowed_root
                ),
                Path(str(row.get("third_proof_path") or "")),
                f"{candidate_id} R3 unchanged proof",
            )
            proof_hash = sha256_text(proof_path.read_text(encoding="utf-8").strip())
            if (
                proof_hash != source_hash
                or proof_path.read_bytes() != source_path.read_bytes()
            ):
                raise ValueError(f"R3 unchanged route changed proof: {candidate_id}")
            if state == "promoted_unchanged_no_second_cycle":
                promotion = read_object(
                    third_dir
                    / "cases"
                    / f"{PROBLEM_ID}.{candidate_id}"
                    / "promoted_unchanged"
                    / "promotion.json"
                )
                if (
                    promotion.get("state") != "completed"
                    or Path(str(promotion.get("source_proof_path") or "")).resolve()
                    != source_path
                    or promotion.get("source_proof_sha256") != source_hash
                    or Path(str(promotion.get("third_proof_path") or "")).resolve()
                    != proof_path
                    or promotion.get("third_proof_sha256") != proof_hash
                    or int(promotion.get("model_call_count", -1)) != 0
                ):
                    raise ValueError(f"R3 unchanged promotion changed: {candidate_id}")
            else:
                ledger = read_object(
                    third_dir
                    / "cases"
                    / f"{PROBLEM_ID}.{candidate_id}"
                    / "updated_obligation_ledger.json"
                )
                primary_result = (
                    third_dir
                    / "cases"
                    / f"{PROBLEM_ID}.{candidate_id}"
                    / "third_ungrouped_resolve/result.json"
                )
                retry_result = (
                    primary_result.parent.parent
                    / v263.THIRD_RESOLVE_RETRY_DIRECTORY
                    / "result.json"
                )
                if (
                    ledger.get("active_obligations")
                    or int(ledger.get("active_count") or 0) != 0
                    or primary_result.exists()
                    or retry_result.exists()
                ):
                    raise ValueError(f"R3 skipped-no-active route changed: {candidate_id}")
        if (
            Path(str(row.get("third_proof_path") or "")).resolve() != proof_path
            or str(row.get("third_proof_sha256") or "") != proof_hash
        ):
            raise ValueError(f"R3 summary/result proof drift: {candidate_id}")
        rows.append(
            {
                "candidate_id": candidate_id,
                "proof_path": str(proof_path),
                "proof_sha256": proof_hash,
                "third_resolve_state": state,
            }
        )
    return {"checkpoint": "R3", "stage_dir": str(third_dir), "proofs": rows}


def build_manifest(
    *,
    source_run: Path,
    output_dir: Path,
    gemma_endpoint: str,
    qwen_endpoint: str,
    workers_per_endpoint: int,
    resolve_workers: int,
    seed_namespace: str,
    model_timeout_sec: int,
    input_checkpoint: str = "resolver1",
    enable_exact_evidence: bool = True,
) -> dict[str, Any]:
    return {
        "schema": "cognitive-well-v0290-p5-iterated-review-fusion-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "problem_id": PROBLEM_ID,
        "problem_number": PROBLEM_NUMBER,
        "source_run": str(source_run.resolve()),
        "input_checkpoint": input_checkpoint,
        "output_dir": str(output_dir.resolve()),
        "candidate_ids": list(CANDIDATE_IDS),
        "r1_cycle_count": R1_CYCLE_COUNT,
        "pipeline_policy": PIPELINE_POLICY,
        "stage_order": list(STAGE_ORDER),
        "terminal_checkpoint": TERMINAL_CHECKPOINT,
        "runtime": {
            "gemma_endpoint": gemma_endpoint.rstrip("/"),
            "qwen_endpoint": qwen_endpoint.rstrip("/"),
            "workers_per_endpoint": workers_per_endpoint,
            "resolve_workers": resolve_workers,
            "seed_namespace": seed_namespace,
            "model_timeout_sec": model_timeout_sec,
        },
        "transport_policy": {"reviewer2_http_timeout_floor_sec": 2400,
                             "qwen_token_policy": repair_boundary.QWEN_TOKEN_POLICY,
                             "qwen_max_output_tokens": repair_boundary.QWEN_MAX_OUTPUT_TOKENS,
                             "qwen_retry_on_output_cap": True,
                             "limit_recovery": repair_boundary.limit_policy.policy_manifest(),
                             "single_model":single_model.CURRENT.model if single_model.active() else None,
                             "budget_forcing":not single_model.active(),
                             "reasoning_effort":single_model.CURRENT.reasoning_effort if single_model.active() else None},
        "repair_brief_boundary": {
            "mandatory_every_r1_cycle": True,
            "accepting_fusion_audit_mandatory": True,
            "rejected_acceptance_returns_to_fusion": True,
            "max_acceptance_reconsiderations": (
                repair_boundary.MAX_ACCEPTANCE_RECONSIDERATIONS
            ),
            "audit_model": single_model.effective_model(repair_boundary.QWEN_MODEL),
            "rewrite_model": single_model.effective_model(repair_boundary.GEMMA_MODEL),
            "audit_original_then_every_rewrite": True,
            "max_rewrite_rounds": repair_boundary.MAX_REWRITE_ROUNDS,
            "token_caps": list(repair_boundary.TOKEN_CAPS),
            "qwen_token_policy": repair_boundary.QWEN_TOKEN_POLICY,
            "output_format": "Markdown",
            "mutation": "replace exactly resolver_brief only",
            "uncertified_route": repair_boundary.UNCERTIFIED_SYNTHESIS_POLICY,
            "optional_exact_evidence": {
                "enabled_for_every_repair_brief_audit": enable_exact_evidence,
                "operation_policy": "generic allowlist only",
                "no_tool_or_failure": "contained; audit continues without evidence",
                "finite_no_witness_is_global_proof": False,
            },
        },
        "parallel_lanes": workers_per_endpoint,
        "model_inputs_exclude": [
            "reference_solution",
            "v0139_proof",
            "strict_score",
            "Codex_feedback",
            "human_repair_brief_audit",
        ],
        "strict_scoring": {
            "inside_model_pipeline": False,
            "targets_written_after_each_checkpoint": True,
            "scores_must_not_control_selection_or_stopping": True,
        },
    }


def run_pipeline(
    *,
    output_dir: Path,
    source_run: Path = DEFAULT_SOURCE_RUN,
    input_checkpoint: str = "resolver1",
    gemma_endpoint: str = DEFAULT_GEMMA_ENDPOINT,
    qwen_endpoint: str = DEFAULT_QWEN_ENDPOINT,
    workers_per_endpoint: int = 4,
    resolve_workers: int = 2,
    seed_namespace: str = DEFAULT_SEED_NAMESPACE,
    model_timeout_sec: int = DEFAULT_MODEL_TIMEOUT_SEC,
    dry_run: bool = False,
    authorize_model_calls: bool = False,
    enable_exact_evidence: bool = True,
    resume_after_cycle: int = 0,
    problem_number: int = 5,
    resume_fresh_reviews: bool = False,
    source_problem_id: str | None = None,
) -> dict[str, Any]:
    if min(workers_per_endpoint, resolve_workers) < 1:
        raise ValueError("worker counts must be positive")
    if not dry_run and not authorize_model_calls:
        raise PermissionError("model execution requires authorize_model_calls=True")
    output_dir = output_dir.resolve()
    source_run = source_run.resolve()
    resuming = bool(resume_after_cycle or resume_fresh_reviews)
    if resume_after_cycle not in range(R1_CYCLE_COUNT + 1):
        raise ValueError("resume checkpoint must be a completed R1 cycle")
    if output_dir.exists() and not resuming:
        raise FileExistsError(f"fresh output root already exists: {output_dir}")
    if source_run == output_dir or source_run in output_dir.parents:
        raise ValueError("output directory overlaps source run")
    binding_error = None
    try:
        if input_checkpoint == "lazy_checked":
            if source_problem_id is None:
                configure_source_problem(source_run, problem_number)
            else:
                configure_source_problem(source_run, problem_number, expected_problem_id=source_problem_id)
        elif source_problem_id is not None:
            raise ValueError("explicit source problem ID requires the lazy_checked checkpoint")
        elif problem_number != 5:
            raise ValueError("non-P5 runs must select the lazy_checked input checkpoint")
        else:
            configure_problem_binding(
                problem_id=v264.PROBLEM_ID, problem_number=v264.PROBLEM_NUMBER,
                problem_sha256=v264.EXPECTED_PROBLEM_SHA256, candidate_ids=v264.CANDIDATE_IDS,
            )
    except Exception as error:
        if resuming:
            raise
        binding_error = error
    previous_manifest = None
    if resuming:
        previous_manifest = read_object(output_dir / "manifest.json")
        requested = build_manifest(
            source_run=source_run, output_dir=output_dir,
            gemma_endpoint=gemma_endpoint, qwen_endpoint=qwen_endpoint,
            workers_per_endpoint=workers_per_endpoint, resolve_workers=resolve_workers,
            seed_namespace=seed_namespace, model_timeout_sec=model_timeout_sec,
            input_checkpoint=input_checkpoint, enable_exact_evidence=enable_exact_evidence,
        )
        for key in ("source_run", "output_dir", "problem_id", "candidate_ids", "runtime", "input_checkpoint",
                    "pipeline_policy", "r1_cycle_count", "terminal_checkpoint"):
            if previous_manifest.get(key) != requested[key]:
                raise ValueError(f"resume changes frozen configuration: {key}")
        for candidate_id in CANDIDATE_IDS:
            lane_root = output_dir / "lanes" / candidate_id
            for cycle in range(resume_after_cycle + 1, R1_CYCLE_COUNT + 1):
                partial = lane_root / f"{cycle:02d}_r1_cycle_{cycle}"
                if partial.exists() and resume_fresh_reviews and cycle == resume_after_cycle + 1:
                    partial_status = read_object(partial / "status.json")
                    if partial_status.get("stage") != "fresh_reviews":
                        raise ValueError("partial resume is restricted to interrupted fresh reviews")
                    if any((partial / "cases").glob("*/fusion*")):
                        raise ValueError("partial resume must not repeat Fusion or its gate")
                    continue
                if partial.exists():
                    raise ValueError("resume would overwrite a later cycle; preserve it first")
            if any((lane_root / name).exists() for name in (
                "04_post_r1_cycle3_audit_ledger", "05_resolver2", "06_resolver3"
            )):
                raise ValueError("historical downstream work is read-only; use a fresh output run")
    else:
        output_dir.mkdir(parents=True, exist_ok=False)
    try:
        if binding_error is not None:
            raise binding_error
        if previous_manifest is None:
            problem_path, current_proofs = _initial_inputs(
                source_run=source_run, output_dir=output_dir,
                input_checkpoint=input_checkpoint,
            )
        else:
            frozen = previous_manifest["frozen_inputs"]
            problem_path = _require_child(output_dir, Path(frozen["problem_path"]), "problem")
            if file_sha256(problem_path) != frozen["problem_file_sha256"]:
                raise ValueError("resume problem file hash drift")
            current_proofs = copy.deepcopy(frozen["lanes"])
            if tuple(row["candidate_id"] for row in current_proofs) != CANDIDATE_IDS:
                raise ValueError("resume baseline portfolio drift")
            for row in current_proofs:
                if row.get("proof_path"):
                    _proof_identity(row, allowed_root=output_dir, label="resume baseline")
                elif not row.get("source_failure"):
                    raise ValueError("Missing active baseline proof")
            if input_checkpoint == "lazy_checked":
                live = _lazy_checked_portfolio(source_run)
                failures = {row["candidate_id"]: row.get("source_failure") for row in live["proofs"]}
                if any(row.get("source_failure") != failures[row["candidate_id"]] for row in current_proofs):
                    raise ValueError("Resume frontend failure provenance drift")
            if resume_fresh_reviews or resume_after_cycle == R1_CYCLE_COUNT:
                archive = _unused_resume_path(output_dir / f"mechanical_resume_after_cycle_{resume_after_cycle}")
                archive.mkdir(exist_ok=False)
                paths = [output_dir / name for name in ("failure.json", "summary.json", "status.json")]
                for candidate_id in CANDIDATE_IDS:
                    lane_root = output_dir / "lanes" / candidate_id
                    failure_path = lane_root / "failure.json"
                    if failure_path.is_file():
                        failure = read_object(failure_path)
                        if failure.get("stage") == f"R1-C{resume_after_cycle + 1}":
                            partial = lane_root / f"{resume_after_cycle + 1:02d}_r1_cycle_{resume_after_cycle + 1}"
                            if read_object(partial / "status.json").get("stage") != "fresh_reviews":
                                raise ValueError("refusing to clear a non-review failure")
                            paths.extend([failure_path, lane_root / "status.json"])
                moved = []
                for path in paths:
                    if path.is_file():
                        destination = archive / path.relative_to(output_dir)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        path.rename(destination)
                        moved.append(str(destination))
                write_json(archive / "preserved_records.json", {"paths": moved})
    except Exception as error:
        failure = {
            "state": "failed_closed",
            "stage": "input_binding",
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        write_json(output_dir / "failure.json", failure)
        write_json(output_dir / "status.json", failure)
        return failure
    try:
        manifest = build_manifest(
            source_run=source_run,
            output_dir=output_dir,
            gemma_endpoint=gemma_endpoint,
            qwen_endpoint=qwen_endpoint,
            workers_per_endpoint=workers_per_endpoint,
            resolve_workers=resolve_workers,
            seed_namespace=seed_namespace,
            model_timeout_sec=model_timeout_sec,
            input_checkpoint=input_checkpoint,
            enable_exact_evidence=enable_exact_evidence,
        )
        problem_payload = read_object(problem_path)
        problem_text = str(problem_payload.get("claim") or "").strip()
        if sha256_text(problem_text) != EXPECTED_PROBLEM_SHA256:
            raise ValueError("staged problem text hash drift")
        manifest["frozen_inputs"] = {
            "problem_path": str(problem_path),
            "problem_text_sha256": sha256_text(problem_text),
            "problem_file_sha256": file_sha256(problem_path),
            "lanes": copy.deepcopy(current_proofs),
        }
        if previous_manifest is None:
            write_json(output_dir / "manifest.json", manifest)
        else:
            # Preserve the original manifest: earlier cycles used its policy.
            manifest["resume_after_cycle"] = resume_after_cycle
            manifest["resume_fresh_reviews"] = resume_fresh_reviews
            manifest["previous_manifest_sha256"] = file_sha256(output_dir / "manifest.json")
            resume_path = _unused_resume_path(output_dir / f"resume_after_cycle_{resume_after_cycle}.json")
            write_json(resume_path, manifest)
        write_json(
            output_dir / "status.json",
            {"state": "dry_run" if dry_run else "running"},
        )
    except Exception as error:
        failure = {
            "state": "failed_closed",
            "stage": "input_binding",
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        write_json(output_dir / "failure.json", failure)
        write_json(output_dir / "status.json", failure)
        return failure

    baseline = {
        "checkpoint": "baseline",
        "proofs": [copy.deepcopy(row) for row in current_proofs if row.get("proof_path")],
    }
    if dry_run:
        planned = [baseline] + [
            {"checkpoint": f"R1-C{cycle}"} for cycle in range(1, R1_CYCLE_COUNT + 1)
        ]
        summary = {
            "schema": "cognitive-well-v0290-p5-iterated-review-fusion-dry-run-v1",
            "state": "dry_run_completed",
            "model_calls_performed": 0,
            "checkpoints": planned,
        }
        write_json(output_dir / "score_targets.json", {"checkpoints": planned})
        write_json(output_dir / "summary.json", summary)
        write_json(output_dir / "status.json", {"state": "dry_run_completed"})
        return summary

    checkpoints = [baseline]
    lane_records = {
        str(row["candidate_id"]): {
            "candidate_id": str(row["candidate_id"]),
            "state": "failed_closed" if row.get("source_failure") else "active",
            "failure": row.get("source_failure"),
            "current_proof": dict(row) if row.get("proof_path") else None,
            "checkpoints": [
                {
                    "checkpoint": row.get("source_checkpoint", "baseline"),
                    "proof_path": row["proof_path"],
                    "proof_sha256": row["proof_sha256"],
                }
            ] if row.get("proof_path") else [],
        }
        for row in current_proofs
    }
    for candidate_id, lane in lane_records.items():
        if lane["failure"]:
            lane_root = output_dir / "lanes" / candidate_id
            write_json(lane_root / "failure.json", lane["failure"])
            write_json(lane_root / "status.json", lane["failure"])

    def fail_lane(candidate_id: str, stage_name: str, error: BaseException) -> None:
        lane = lane_records[candidate_id]
        lane["state"] = "failed_closed"
        lane["failure"] = {
            "stage": stage_name,
            "error": f"{type(error).__name__}: {error}",
        }
        lane_root = output_dir / "lanes" / candidate_id
        failure_record = {"state": "failed_closed", **lane["failure"]}
        write_json(lane_root / "failure.json", failure_record)
        write_json(lane_root / "status.json", failure_record)

    try:
        for cycle in range(1, resume_after_cycle + 1):
            proofs, stage_dirs = [], {}
            for candidate_id in CANDIDATE_IDS:
                lane = lane_records[candidate_id]
                if lane["state"] != "active":
                    continue
                lane_root = output_dir / "lanes" / candidate_id
                stage_dir = lane_root / f"{cycle:02d}_r1_cycle_{cycle}"
                summary_path = stage_dir / "summary.json"
                summary = read_object(summary_path) if summary_path.is_file() else {}
                if summary.get("state") == "completed":
                    terminal = _terminal_r1_proofs(
                        stage_dir=stage_dir, allowed_root=output_dir,
                        expected_candidates=(candidate_id,), model_timeout_sec=model_timeout_sec,
                    )[0]
                    lane["current_proof"] = terminal
                    lane["checkpoints"].append({
                        "checkpoint": f"R1-C{cycle}", "stage_dir": str(stage_dir),
                        "proof_path": terminal["proof_path"], "proof_sha256": terminal["proof_sha256"],
                    })
                    proofs.append(terminal)
                    stage_dirs[candidate_id] = str(stage_dir)
                else:
                    failure = read_object(lane_root / "failure.json")
                    if failure.get("state") != "failed_closed" or failure.get("stage") != f"R1-C{cycle}":
                        raise ValueError(f"resume cycle is not terminal: {candidate_id} C{cycle}")
                    lane["state"] = "failed_closed"
                    lane["failure"] = failure
            checkpoints.append({
                "checkpoint": f"R1-C{cycle}", "stage_dirs": stage_dirs, "proofs": proofs,
                "failed_lanes": [key for key, lane in lane_records.items() if lane["state"] == "failed_closed"],
                "strict_score_model_visible": False,
            })
        with runtime_generation_policy(
            model_timeout_sec=model_timeout_sec
        ), inherited_component_caps():
            for cycle in range(resume_after_cycle + 1, R1_CYCLE_COUNT + 1):
                cycle_key = f"R1-C{cycle}"
                active_ids = [
                    candidate_id
                    for candidate_id in CANDIDATE_IDS
                    if lane_records[candidate_id]["state"] == "active"
                ]
                write_json(
                    output_dir / "status.json",
                    {"state": "running", "stage": cycle_key, "active_lanes": active_ids},
                )

                def run_r1_lane(candidate_id: str) -> tuple[Path, dict[str, Any]]:
                    return run_r1_cycle_lane(
                        output_dir=output_dir, candidate_id=candidate_id, cycle=cycle,
                        source_proof=dict(lane_records[candidate_id]["current_proof"]),
                        problem_path=problem_path, gemma_endpoint=gemma_endpoint,
                        qwen_endpoint=qwen_endpoint, seed_namespace=seed_namespace,
                        model_timeout_sec=model_timeout_sec,
                    )

                completed: dict[str, tuple[Path, dict[str, Any]]] = {}
                with mandatory_repair_boundary(
                    qwen_endpoint=qwen_endpoint,
                    gemma_endpoint=gemma_endpoint,
                    cycle_key=cycle_key,
                    model_timeout_sec=model_timeout_sec,
                    enable_exact_evidence=enable_exact_evidence,
                ):
                    with ThreadPoolExecutor(
                        max_workers=min(len(active_ids), workers_per_endpoint) or 1,
                        thread_name_prefix=f"v0290-{cycle_key}",
                    ) as executor:
                        futures = {
                            executor.submit(run_r1_lane, candidate_id): candidate_id
                            for candidate_id in active_ids
                        }
                        for future in as_completed(futures):
                            candidate_id = futures[future]
                            try:
                                completed[candidate_id] = future.result()
                            except Exception as error:
                                fail_lane(candidate_id, cycle_key, error)
                cycle_proofs: list[dict[str, Any]] = []
                stage_dirs: dict[str, str] = {}
                for candidate_id in CANDIDATE_IDS:
                    if candidate_id not in completed:
                        continue
                    cycle_dir, terminal = completed[candidate_id]
                    lane_records[candidate_id]["current_proof"] = terminal
                    lane_records[candidate_id]["checkpoints"].append(
                        {
                            "checkpoint": cycle_key,
                            "stage_dir": str(cycle_dir),
                            "proof_path": terminal["proof_path"],
                            "proof_sha256": terminal["proof_sha256"],
                        }
                    )
                    cycle_proofs.append(terminal)
                    stage_dirs[candidate_id] = str(cycle_dir)
                checkpoints.append(
                    {
                        "checkpoint": cycle_key,
                        "stage_dirs": stage_dirs,
                        "proofs": cycle_proofs,
                        "failed_lanes": [
                            candidate_id
                            for candidate_id in CANDIDATE_IDS
                            if lane_records[candidate_id]["state"] == "failed_closed"
                        ],
                        "strict_score_model_visible": False,
                    }
                )
                write_json(
                    output_dir / "score_targets.json", {"checkpoints": checkpoints}
                )

            # R1-C2 is the terminal proof-generation checkpoint. No post-R1
            # audit ledger or later Resolver is executed.
            for candidate_id in CANDIDATE_IDS:
                lane = lane_records[candidate_id]
                if lane["state"] == "active":
                    lane["state"] = "completed"
                    write_json(output_dir / "lanes" / candidate_id / "status.json", {
                        "state": "completed", "stage": TERMINAL_CHECKPOINT,
                        "proof_path": lane["current_proof"]["proof_path"],
                        "proof_sha256": lane["current_proof"]["proof_sha256"],
                    })
            write_json(output_dir / "score_targets.json", {"checkpoints": checkpoints})
    except Exception as error:
        failure = {
            "state": "failed_closed",
            "stage": "orchestrator",
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        write_json(output_dir / "failure.json", failure)
        write_json(output_dir / "status.json", failure)
        return failure

    completed_lane_count = sum(
        lane["state"] == "completed" for lane in lane_records.values()
    )
    terminal_state = (
        "completed"
        if completed_lane_count == len(CANDIDATE_IDS)
        else "completed_with_failed_lanes"
        if completed_lane_count
        else "failed_closed"
    )
    summary = {
        "schema": "cognitive-well-v0290-p5-iterated-review-fusion-summary-v1",
        "state": terminal_state,
        "pipeline_policy": PIPELINE_POLICY,
        "terminal_checkpoint": TERMINAL_CHECKPOINT,
        "problem_id": PROBLEM_ID,
        "candidate_ids": list(CANDIDATE_IDS),
        "checkpoints": checkpoints,
        "score_targets_path": str((output_dir / "score_targets.json").resolve()),
        "lanes": lane_records,
        "completed_lane_count": completed_lane_count,
        "failed_lane_count": len(CANDIDATE_IDS) - completed_lane_count,
        "model_decision_calls_by_codex": 0,
        "manual_selection": False,
    }
    write_json(output_dir / "summary.json", summary)
    if terminal_state == "failed_closed":
        failure = {
            "state": "failed_closed",
            "stage": "all_lanes",
            "error": "all four problem lanes failed closed",
            "lane_failures": {
                candidate_id: lane_records[candidate_id]["failure"]
                for candidate_id in CANDIDATE_IDS
            },
        }
        write_json(output_dir / "failure.json", failure)
        write_json(output_dir / "status.json", failure)
    else:
        write_json(output_dir / "status.json", {"state": terminal_state, "stage": "done"})
    return summary


__all__ = [
    "CANDIDATE_IDS",
    "DEFAULT_MODEL_TIMEOUT_SEC",
    "DEFAULT_SOURCE_RUN",
    "R1_CYCLE_COUNT",
    "STAGE_ORDER",
    "TERMINAL_CHECKPOINT",
    "PIPELINE_POLICY",
    "build_manifest",
    "inherited_component_caps",
    "mandatory_repair_boundary",
    "run_pipeline",
    "runtime_generation_policy",
]
