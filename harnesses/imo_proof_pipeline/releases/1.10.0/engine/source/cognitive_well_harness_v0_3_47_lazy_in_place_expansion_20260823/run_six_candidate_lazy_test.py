from __future__ import annotations

import argparse
import hashlib
import json
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from experiments.local_math_verifier.runtime import utc_now, write_json

from cognitive_well_harness_v0_3_36_p4_dual_block_replay_snapshot_20260822.cold_prompts import (
    lazy_phrasing,
)
from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.pipeline import (
    nonempty_parser,
)
from cognitive_well_harness_v0_3_37_bf16_gemma_two_block_stage12_20260822.runtime import (
    GEMMA_MODEL,
    RuntimeConfig,
    StageRuntime,
)
from cognitive_well_harness_v0_3_46_gemma4_temperature_portfolio_20260823.run import (
    CANDIDATES,
)

from . import HARNESS_VERSION
from .contracts import LAZY_RESOLVE_TEMPERATURE
from .lazy_expansion import (
    EXPECTED_PROMPT_SHA256,
    lazy_in_place_expansion_prompt,
    parse_lazy_expansion_output,
    sha256_text,
)


MAX_CONCURRENT = 4


def derived_seed(candidate_seed: int, stage: str) -> int:
    material = f"v047:{candidate_seed}:{stage}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def expansion_parser(value: str) -> dict[str, Any]:
    try:
        return parse_lazy_expansion_output(value)
    except ValueError as error:
        return {"valid": False, "errors": [str(error)]}


def load_problem(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    problem = str(data.get("problem") or "").strip()
    if not problem:
        raise ValueError(f"problem JSON has no nonempty problem field: {path}")
    return problem


def load_source_proofs(source_dir: Path) -> list[dict[str, Any]]:
    portfolio = json.loads((source_dir / "result.json").read_text(encoding="utf-8"))
    by_id = {str(row["candidate_id"]): row for row in portfolio["results"]}
    rows: list[dict[str, Any]] = []
    for spec in CANDIDATES:
        candidate_id = str(spec["candidate_id"])
        if candidate_id not in by_id:
            raise ValueError(f"source portfolio is missing {candidate_id}")
        proof_path = source_dir / "candidates" / candidate_id / "proof.md"
        proof = proof_path.read_text(encoding="utf-8").strip()
        if not proof:
            raise ValueError(f"source proof is empty: {proof_path}")
        rows.append(
            {
                **spec,
                "proof": proof,
                "proof_sha256": sha256_text(proof),
                "proof_path": str(proof_path.resolve()),
            }
        )
    return rows


def run_lazy_check(
    *, runtime: StageRuntime, output_dir: Path, row: dict[str, Any]
) -> dict[str, Any]:
    candidate_id = str(row["candidate_id"])
    generated = runtime.gemma_call(
        output_dir=output_dir / "candidates" / candidate_id / "lazy_check",
        name="lazy_check",
        system_prompt=lazy_phrasing(str(row["proof"])),
        user_prompt="Scan the submitted proof now.",
        seed=derived_seed(int(row["seed"]), "lazy_check"),
        temperature=0.1,
        max_tokens=runtime.config.lazy_max_tokens,
        parser=nonempty_parser,
    )
    report = str(generated["text"]).strip()
    return {
        **row,
        "lazy_report": report,
        "lazy_report_sha256": sha256_text(report),
        "has_lazy_issues": report != "NO_ISSUES",
        "lazy_generation": generated,
    }


def run_lazy_resolve(
    *,
    runtime: StageRuntime,
    problem: str,
    output_dir: Path,
    row: dict[str, Any],
) -> dict[str, Any]:
    candidate_id = str(row["candidate_id"])
    candidate_dir = output_dir / "candidates" / candidate_id
    ancestor = str(row["proof"])
    if not row["has_lazy_issues"]:
        checked = ancestor
        action = "NOT_INVOKED_NO_ISSUES"
        expansion = None
        change_candidates: list[dict[str, Any]] = []
    else:
        expansion = runtime.gemma_call(
            output_dir=candidate_dir / "lazy_in_place_resolve",
            name="lazy_in_place_resolve",
            system_prompt=lazy_in_place_expansion_prompt(
                problem=problem,
                current_proof=ancestor,
                local_gaps=str(row["lazy_report"]),
            ),
            user_prompt=(
                "Expand the current proof in place. Return only the required repair envelope."
            ),
            seed=derived_seed(int(row["seed"]), "lazy_in_place_resolve"),
            temperature=LAZY_RESOLVE_TEMPERATURE,
            max_tokens=runtime.config.solver_max_tokens,
            parser=expansion_parser,
        )
        parsed = dict(expansion["parsed"])
        checked = str(parsed["proof"]).strip()
        action = str(parsed["conclusion_action"])
        change_candidates = []
        if action == "CHANGE":
            ancestor_path = candidate_dir / "ancestor_proof.md"
            descendant_path = candidate_dir / "changed_descendant_proof.md"
            ancestor_path.write_text(ancestor + "\n", encoding="utf-8")
            descendant_path.write_text(checked + "\n", encoding="utf-8")
            change_candidates = [
                {
                    "candidate_id": f"{candidate_id}.lazy_ancestor",
                    "variant": "ancestor",
                    "proof_sha256": sha256_text(ancestor),
                    "proof_path": str(ancestor_path.resolve()),
                },
                {
                    "candidate_id": f"{candidate_id}.lazy_changed_descendant",
                    "variant": "changed_descendant",
                    "proof_sha256": sha256_text(checked),
                    "proof_path": str(descendant_path.resolve()),
                },
            ]
    checked_path = candidate_dir / "checked_proof.md"
    checked_path.parent.mkdir(parents=True, exist_ok=True)
    checked_path.write_text(checked + "\n", encoding="utf-8")
    result = {
        "schema": "cognitive-well-v047-six-candidate-lazy-result-v1",
        "candidate_id": candidate_id,
        "draft_temperature": row["temperature"],
        "draft_seed": row["seed"],
        "draft_proof_sha256": row["proof_sha256"],
        "lazy_report": row["lazy_report"],
        "lazy_report_sha256": row["lazy_report_sha256"],
        "has_lazy_issues": row["has_lazy_issues"],
        "lazy_resolve_invoked": expansion is not None,
        "lazy_resolve_temperature": (
            LAZY_RESOLVE_TEMPERATURE if expansion is not None else None
        ),
        "conclusion_action": action,
        "checked_proof_sha256": sha256_text(checked),
        "checked_proof_path": str(checked_path.resolve()),
        "change_candidates": change_candidates,
        "expansion_generation": expansion,
        "completed_at": utc_now(),
    }
    write_json(candidate_dir / "result.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply lazy scan and conclusion-preserving expansion to six Gemma drafts"
    )
    parser.add_argument("--source-portfolio", type=Path, required=True)
    parser.add_argument("--problem-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    problem = load_problem(args.problem_json)
    sources = load_source_proofs(args.source_portfolio)
    config = RuntimeConfig()
    config.validate(require_files=False)
    runtime = StageRuntime(config)
    manifest = {
        "schema": "cognitive-well-v047-six-candidate-lazy-manifest-v1",
        "harness_version": HARNESS_VERSION,
        "created_at": utc_now(),
        "source_portfolio": str(args.source_portfolio.resolve()),
        "source_generation_reused": True,
        "problem_sha256": sha256_text(problem),
        "candidate_allocation": {"temperature_1.0": 4, "temperature_0.7": 2},
        "candidate_ids": [row["candidate_id"] for row in sources],
        "lazy_check_temperature": 0.1,
        "lazy_check_max_tokens": config.lazy_max_tokens,
        "lazy_resolve_temperature": LAZY_RESOLVE_TEMPERATURE,
        "lazy_resolve_max_tokens": config.solver_max_tokens,
        "lazy_resolve_cap_recovery_max_tokens": config.solver_max_tokens * 2,
        "lazy_resolve_prompt_sha256": EXPECTED_PROMPT_SHA256,
        "model": GEMMA_MODEL,
        "dtype": "bfloat16",
        "mtp_speculative_tokens": 4,
        "top_p": 0.95,
        "top_k": 64,
        "reference_solution_access": False,
    }
    write_json(args.output_dir / "manifest.json", manifest)
    lock = threading.Lock()

    def status(stage: str, completed: list[str], failures: list[dict[str, str]]) -> None:
        with lock:
            write_json(
                args.output_dir / "status.json",
                {
                    "state": "running",
                    "stage": stage,
                    "completed": sorted(completed),
                    "failed": failures,
                    "total": len(sources),
                    "updated_at": utc_now(),
                },
            )

    checked_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    completed: list[str] = []
    status("lazy_check", completed, failures)
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {
            executor.submit(
                run_lazy_check,
                runtime=runtime,
                output_dir=args.output_dir,
                row=row,
            ): row
            for row in sources
        }
        for future in as_completed(futures):
            row = futures[future]
            candidate_id = str(row["candidate_id"])
            try:
                checked_rows.append(future.result())
            except Exception as error:
                failures.append(
                    {
                        "candidate_id": candidate_id,
                        "stage": "lazy_check",
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            else:
                completed.append(candidate_id)
            status("lazy_check", completed, failures)
    if failures:
        raise RuntimeError(f"lazy checks failed: {failures}")

    results: list[dict[str, Any]] = []
    completed = []
    status("lazy_in_place_resolve", completed, failures)
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {
            executor.submit(
                run_lazy_resolve,
                runtime=runtime,
                problem=problem,
                output_dir=args.output_dir,
                row=row,
            ): row
            for row in checked_rows
        }
        for future in as_completed(futures):
            row = futures[future]
            candidate_id = str(row["candidate_id"])
            try:
                results.append(future.result())
            except Exception as error:
                failures.append(
                    {
                        "candidate_id": candidate_id,
                        "stage": "lazy_in_place_resolve",
                        "error": f"{type(error).__name__}: {error}",
                        "traceback": traceback.format_exc(),
                    }
                )
            else:
                completed.append(candidate_id)
            status("lazy_in_place_resolve", completed, failures)
    results.sort(key=lambda row: str(row["candidate_id"]))
    final_state = "completed" if not failures else "completed_with_failures"
    write_json(
        args.output_dir / "result.json",
        {
            **manifest,
            "schema": "cognitive-well-v047-six-candidate-lazy-summary-v1",
            "results": results,
            "failures": failures,
            "completed_at": utc_now(),
        },
    )
    write_json(
        args.output_dir / "status.json",
        {
            "state": final_state,
            "stage": "lazy_in_place_resolve",
            "completed": [row["candidate_id"] for row in results],
            "failed": failures,
            "total": len(sources),
            "updated_at": utc_now(),
        },
    )
    if not args.quiet:
        print(
            json.dumps(
                {
                    "state": final_state,
                    "completed": len(results),
                    "failed": len(failures),
                    "resolved": sum(row["lazy_resolve_invoked"] for row in results),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
