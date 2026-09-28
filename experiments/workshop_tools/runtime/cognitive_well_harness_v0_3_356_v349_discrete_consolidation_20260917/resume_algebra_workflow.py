"""Resume mechanically failed Laurent stages, retaining all model decisions."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import threading

from . import proof_harness as harness, algebra_workflow as workflow


def run(source, output, samples):
    source, output = source.resolve(), output.resolve()
    manifest = harness.resume.read(source / "manifest.json")
    if manifest.get("schema") != harness.SCHEMA:
        raise ValueError("source is not a packaged proof harness")
    config = harness.Config.from_saved(manifest["config"])
    config.validate()
    if not samples or len(samples) != len(set(samples)):
        raise ValueError("choose distinct saved sample names")
    documents = harness.input_context.load_saved(source, manifest)
    paths = [source / "manifest.json", *(source / name for name in manifest["input_artifacts"])]
    jobs = []
    for name in samples:
        if name not in {f"sample_{i:02d}" for i in range(1, config.batch_size + 1)}:
            raise ValueError("invalid sample name")
        sample = source / "02_formalizations" / name
        state = harness.resume.read(sample / "status.json")
        if state.get("state") != "failed_closed" or state.get("error") != "RuntimeError: Laurent preview child exited 1":
            raise ValueError("sample is not stopped at the diagnosed Laurent child-exit failure: " + name)
        cycle = sample / "cycles" / f"cycle_{state['cycle']:02d}"
        tool = cycle / "03_execution/04_tool"
        request, admission, task, parsed, text, matcher = workflow.source_context(tool / "request.json", documents)
        problem = harness.acquisition.v0220.load_problem(source / "input/problem.json")
        if (task.source_proof.strip() != (source / "input/source_proof.md").read_text().strip()
                or task.theorem.strip() != problem.statement.strip() or task.problem_id != problem.problem_id):
            raise ValueError("accepted request binds another problem or proof")
        workflow.resume_prefix(tool, request)
        jobs.append((name, tool, parsed, state["master_seed"]))
        paths += [sample / "manifest.json", sample / "status.json", tool / "request.json",
                  tool / "cascade_status.json", tool / "guarded_radical/result.json"]
        paths += [p for p in (sample / "input").rglob("*") if p.is_file()]
        paths += [p for p in (cycle / "03_execution/03_final_semantic_audit").rglob("*") if p.is_file()]
    frozen = {str(path): harness.base.sha256_file(path) for path in paths}

    def validate():
        if {str(path): harness.base.sha256_file(path) for path in paths} != frozen:
            raise ValueError("frozen recovery inputs changed")

    output.mkdir(parents=True, exist_ok=False)
    status = {"schema": "generic-laurent-mechanical-resume-v1", "state": "running", "stage": "laurent",
        "source_run": str(source), "source_artifacts": frozen, "sample_names": samples,
        "new_detection_calls": 0, "new_matcher_calls": 0, "new_formalization_calls": 0,
        "new_semantic_audit_calls": 0, "reused_stages": list(workflow.LEGACY_PREFIX),
        "samples": [], "config": manifest["config"]}
    harness.rewrite.write_record(output / "manifest.json", status)
    harness.rewrite.write_record(output / "status.json", status)
    stop, lock = threading.Event(), threading.Lock()

    def select(request_path, operation):
        with lock:
            if stop.is_set():
                return {"state": "superseded_by_verified_candidate"}
            validate()
            stop.set()
            status.update(stage="proof_synthesis", selected={"request_path": str(request_path), "state": "running"})
            harness.rewrite.write_record(output / "status.json", status)
        result = operation()
        with lock:
            status["selected"].update(state=result["state"], result=result)
            harness.rewrite.write_record(output / "status.json", status)
        return result

    def track(job):
        name, tool, parsed, seed = job
        try:
            validate()
            result = workflow.execute(parsed, output / name, config=config, seed=seed,
                documents=documents, select=select, should_stop=stop.is_set, resume_after_radical=tool)
            validate()
            return {"sample": name, **result}
        except Exception as error:
            return {"sample": name, "state": "failed_closed", "error": f"{type(error).__name__}: {error}"}

    with ThreadPoolExecutor(max_workers=min(config.workers, len(jobs))) as pool:
        for future in as_completed([pool.submit(track, job) for job in jobs]):
            row = future.result()
            with lock:
                status["samples"].append(row)
                if row["state"] == "failed_closed" and status.get("selected"):
                    selected_path = status["selected"]["request_path"]
                    if f"/{row['sample']}/" in selected_path:
                        status["selected"]["result"] = {"state": "failed_closed"}
                harness.rewrite.write_record(output / "status.json", status)
    validate()
    status.update(state="failed_closed" if any(row["state"] == "failed_closed" for row in status["samples"]) else "completed")
    return harness.publish(output, status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample", action="append", required=True)
    args = parser.parse_args()
    result = run(args.source_run, args.output_dir, args.sample)
    print(f"{result['state']}: {result.get('outcome')}")
    return int(result["state"] == "failed_closed")


if __name__ == "__main__":
    raise SystemExit(main())
