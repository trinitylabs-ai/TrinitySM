"""Resume only unsynthesized Cycle-1 repair-brief rejections; score each output.

The source run is read-only. Reviews, Fusion, audits and brief rewrites are reused
after provenance replay. This invokes the existing Resolver, not a new prompt.
"""
from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
import subprocess
import traceback

from . import HARNESS_REVISION, pipeline as p, repair_boundary as boundary


def verify_generation_inputs(problem_path: Path, proof_path: Path, binding: dict) -> None:
    """Bind only the submitted inputs; never open a scorer or reference corpus."""
    problem = str(p.read_object(problem_path).get("claim") or "").strip()
    proof = proof_path.read_text(encoding="utf-8").strip()
    if (not problem or not proof
            or p.sha256_text(problem) != binding["problem_sha256"]
            or p.sha256_text(proof) != binding["proof_sha256"]):
        raise ValueError("generation problem/proof binding mismatch")


def prepare_source(root: Path, output: Path) -> list[dict]:
    root, output = root.resolve(), output.resolve()
    if root == output or root in output.parents or output in root.parents:
        raise ValueError("resumed output must be separate from the immutable source run")
    manifest = p.read_object(root / "manifest.json")
    first_stage = root / "lanes" / manifest["candidate_ids"][0] / "01_r1_cycle_1/manifest.json"
    problem_number = p.read_object(first_stage)["cases"][0]["problem_number"]
    if manifest.get("problem_number", problem_number) != problem_number:
        raise ValueError("source problem number mismatch")
    p.configure_problem_binding(
        problem_id=manifest["problem_id"], problem_number=problem_number,
        problem_sha256=manifest["frozen_inputs"]["problem_text_sha256"],
        candidate_ids=tuple(manifest["candidate_ids"]),
    )
    jobs = []
    for candidate in manifest["candidate_ids"]:
        stage_dir = root / "lanes" / candidate / "01_r1_cycle_1"
        source_case = stage_dir / "cases" / f"{manifest['problem_id']}.{candidate}"
        gate_path = source_case / "fusion_repair_brief_audit_rewrite/result.json"
        if not gate_path.is_file():
            continue
        gate = p.read_object(gate_path)
        if gate.get("state") != "failed_closed" or gate.get("certified_round") is not None:
            continue
        if (source_case / "resolver_trace_handoff/handoff.json").exists() or any(
            (source_case / "resolver").glob("**/result.json")
        ):
            raise ValueError(f"refusing to regenerate a completed Resolver: {source_case}")
        if gate.get("cycle_key") != "R1-C1":
            raise ValueError("saved gate is not Cycle 1")
        specs = p.read_object(stage_dir / "manifest.json")["cases"]
        if len(specs) != 1 or specs[0]["candidate_id"] != candidate:
            raise ValueError("saved case identity mismatch")
        spec = specs[0]
        matches = list((source_case / "fusion").glob("**/result.json"))
        if len(matches) != 1:
            raise ValueError("expected exactly one original Fusion result")
        source_result = p.read_object(matches[0])
        gate_task = p._reconstruct_gate_task(
            fusion_result=source_result, spec=spec, case_dir=source_case, allowed_root=root,
        )
        case_dir = output / "cases" / spec["case_id"]
        effective = boundary.reuse_rejected_brief(
            source_gate=gate_path, source_result=source_result, task=gate_task,
            source_case_dir=source_case,
            destination=case_dir / "fusion_repair_brief_audit_rewrite",
        )
        problem_path = case_dir / "input/problem.json"
        proof_path = case_dir / "input/submitted_proof.md"
        p._stage_file(Path(spec["problem_path"]), problem_path)
        p._stage_file(Path(spec["proof_path"]), proof_path)
        case = dict(spec, problem_path=str(problem_path), proof_path=str(proof_path))
        fusion_task = dict(source_result["task"], **gate_task)
        fusion_task.update(problem_path=str(problem_path), proof_path=str(proof_path))
        seed_namespace = p.read_object(stage_dir / "manifest.json")["seed_namespace"]
        task = p.stage.build_resolver_task(
            case=case, fusion_task=fusion_task, fusion_result=effective,
            case_dir=case_dir, seed_namespace=seed_namespace,
        )
        task = p.bind_effective_fusion_task(task, fusion_result=effective, cycle_key="R1-C1")
        task["source_fusion_result_path"] = str(matches[0].resolve())
        if task["fusion_decision_gate"]["state"] != "REJECTED":
            raise ValueError("rejected brief was relabeled as certified")
        verify_generation_inputs(problem_path, proof_path, spec)
        job = {
            "case_id": spec["case_id"], "candidate_id": candidate,
            "problem_id": spec["problem_id"], "case_dir": str(case_dir),
            "source_root": str(root), "source_gate_path": str(gate_path),
            "source_gate_sha256": p.file_sha256(gate_path),
            "source_manifest_sha256": p.file_sha256(root / "manifest.json"),
            "source_proof_sha256": spec["proof_sha256"],
            "problem_sha256": spec["problem_sha256"],
            "harness_revision": HARNESS_REVISION,
            "generation_reference_reads": False,
            "certification": "REJECTED", "checkpoint": "R1-C1",
            "task": task, "model_timeout_sec": manifest["runtime"]["model_timeout_sec"],
        }
        p.write_json(case_dir / "source_binding.json", {
            key: value for key, value in job.items() if key != "task"
        })
        p.write_json(case_dir / "resolver_task.json", p.stage.resolver.public_task(task))
        jobs.append(job)
    return jobs


def synthesize(job: dict, output: Path) -> dict:
    case_dir, task = Path(job["case_dir"]), job["task"]
    if p.file_sha256(Path(job["source_gate_path"])) != job["source_gate_sha256"]:
        raise ValueError("original gate changed after preparation")
    verify_generation_inputs(Path(task["problem_path"]), Path(task["proof_path"]), {
        "problem_sha256": job["problem_sha256"], "proof_sha256": job["source_proof_sha256"],
    })
    result = p.stage.resolver.run_task(output_dir=case_dir, task=task)
    destination = p.stage.resolver.task_output_dir(case_dir, task)
    _, parsed = p._verify_resolver_producer(
        resolver_result_path=destination / "result.json", case_dir=case_dir,
        allowed_root=output, model_timeout_sec=job["model_timeout_sec"],
    )
    outcome = parsed["outcome"]
    record = {"case_id": job["case_id"], "resolver_outcome": outcome,
              "brief_certification": "REJECTED", "state": "synthesized"}
    if outcome == "RESOLUTION_FAILED":
        record.update(state="resolution_failed", score_state="no_submitted_proof")
    else:
        proof_path = (Path(task["proof_path"]) if outcome == "ORIGINAL_PROOF_VALID"
                      else destination / "resolved_proof.md")
        text = proof_path.read_text().strip()
        if outcome == "RESOLVED_PROOF" and text != str(parsed["proof"]).strip():
            raise ValueError("Resolver proof/parsed output drift")
        record.update(proof_path=str(proof_path), proof_sha256=p.sha256_text(text))
    p.write_json(case_dir / "synthesis_result.json", record)
    return record


def strict_score(job: dict, record: dict, output: Path, launcher: Path) -> dict:
    # Scorer code is needed only after a proof has been produced. Generation
    # preparation must work even when the reference corpus is unavailable.
    from . import score_when_ready

    score_root = output / "strict_scores" / job["case_id"]
    score_root.mkdir(parents=True, exist_ok=False)
    snapshot = score_root / "submitted_proof.md"
    p._stage_file(Path(record["proof_path"]), snapshot)
    if p.sha256_text(snapshot.read_text().strip()) != record["proof_sha256"]:
        raise ValueError("strict scoring snapshot drift")
    p.write_json(score_root / "source_binding.json", record)
    command = score_when_ready.scoring_command(
        launcher=launcher, proof=snapshot, output=score_root / "score",
        problem_id=job["problem_id"], candidate=job["candidate_id"],
    )
    with (score_root / "launcher.log").open("w") as log:
        finished = subprocess.run(command, cwd=p.REPO_ROOT, stdout=log, stderr=subprocess.STDOUT)
    if finished.returncode:
        raise RuntimeError(f"strict scorer exited {finished.returncode}: {score_root}")
    summary = p.read_object(score_root / "score/summary.json")
    if (summary.get("state") != "completed" or summary.get("policy_mode") != "strict"
            or summary.get("reasoning_effort") != "xhigh"
            or summary.get("model") != score_when_ready.scorer.MODEL
            or len(summary.get("rows", [])) != 1
            or summary["rows"][0]["proof_sha256"] != record["proof_sha256"]):
        raise ValueError("strict grading identity/policy mismatch")
    return dict(record, state="completed", score_state="completed",
                score_summary=str(score_root / "score/summary.json"),
                grade=summary["rows"][0]["grade"], policy_sha256=summary["policy_sha256"])


def run(roots: list[Path], output: Path, launcher: Path, execute: bool) -> None:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    jobs = []
    for root in roots:
        jobs.extend(prepare_source(root, output))
    if not jobs or len({job["case_id"] for job in jobs}) != len(jobs):
        raise ValueError("empty or duplicate recovery portfolio")
    timeouts = {job["model_timeout_sec"] for job in jobs}
    if len(timeouts) != 1:
        raise ValueError("one run must share the existing HTTP timeout policy")
    manifest = {
        "source_runs": [str(root.resolve()) for root in roots],
        "candidate_ids": [job["case_id"] for job in jobs],
        "checkpoint": "R1-C1", "synthesis_policy": boundary.UNCERTIFIED_SYNTHESIS_POLICY,
        "source_runs_modified": False, "fresh_reviews": False,
        "fresh_fusion_or_brief_calls": False, "model_prompts_changed": False,
        "budget_forcing": "inherited_mandatory", "model_output_format": "Markdown",
        "optional_tools": False, "workers": 4, "strict_scores_model_visible": False,
        "harness_revision": HARNESS_REVISION, "generation_reference_reads": False,
    }
    p.write_json(output / "manifest.json", manifest)
    records = {job["case_id"]: {"state": "queued", "brief_certification": "REJECTED"} for job in jobs}

    def status(state: str) -> None:
        temp = output / "status.json.tmp"
        p.write_json(temp, {"state": state, "records": records})
        temp.replace(output / "status.json")

    if not execute:
        status("prepared")
        print("Prepared", list(records), flush=True)
        return
    status("running")
    with p.runtime_generation_policy(model_timeout_sec=next(iter(timeouts))), p.inherited_component_caps():
        with ThreadPoolExecutor(max_workers=4) as model_pool, ThreadPoolExecutor(max_workers=4) as score_pool:
            pending = {model_pool.submit(synthesize, job, output): ("synthesis", job) for job in jobs}
            while pending:
                done, _ = wait(pending, timeout=15, return_when=FIRST_COMPLETED)
                for future in done:
                    kind, job = pending.pop(future)
                    key = job["case_id"]
                    try:
                        result = future.result()
                        records[key] = result
                        if kind == "synthesis" and result.get("proof_path"):
                            records[key]["score_state"] = "running"
                            pending[score_pool.submit(strict_score, job, dict(result), output, launcher)] = ("score", job)
                    except Exception as error:
                        records[key] = dict(records[key], state="failed", failed_stage=kind,
                                            error=f"{type(error).__name__}: {error}")
                        (Path(job["case_dir"]) / f"{kind}_error.txt").write_text(traceback.format_exc())
                    print(key, kind, records[key]["state"], flush=True)
                status("running")
    state = "completed_with_failures" if any(row["state"] != "completed" for row in records.values()) else "completed"
    status(state)
    p.write_json(output / "summary.json", {"state": state, "records": records})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skill-launcher", type=Path, required=True)
    parser.add_argument("--execute-models", action="store_true")
    args = parser.parse_args()
    run(args.run_root, args.output_dir, args.skill_launcher.resolve(), args.execute_models)


if __name__ == "__main__":
    main()
