#!/usr/bin/env python3
"""Two-server queue without extended reasoning: Advanced, IMO and Basic reruns."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def make_plan(output, endpoints):
    if len(endpoints) != 2 or len(set(endpoints)) != 2:
        raise ValueError("Supply two distinct local Gemma endpoints")
    jobs = []
    for benchmark, prefix, count in (("imo-proofbench/advanced", "PB-Advanced-", 30),
                                     ("imo2026", "imo2026_p", 6)):
        for i in range(1, count + 1):
            pid = prefix + (f"{i:03}" if benchmark.startswith("imo-") else str(i))
            jobs.append(dict(benchmark=benchmark, problem_id=pid, raw_seed_offset=0))
    for pid in ("PB-Basic-009", "PB-Basic-026"):
        path = ROOT / "benchmarks/imo-proofbench/basic/results/pipeline_raw_bf/generation/records" / pid / "queue_manifest.json"
        manifest = json.loads(path.read_text())
        jobs.append(dict(benchmark="imo-proofbench/basic", problem_id=pid,
                         raw_seed_offset=manifest["raw_seed_offset"],
                         seed_source=path.relative_to(ROOT).as_posix(),
                         seed_source_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for i, job in enumerate(jobs):
        job.update(worker=i % 2, endpoint=endpoints[i % 2],
                   output_dir=str(output / "problems" / job["problem_id"]))
    return dict(schema="workshop-raw-ablation-queue-v1", budget_forcing=False,
                requests_per_candidate=1, candidates_per_problem=4,
                problem_count=len(jobs), planned_requests=len(jobs) * 4, jobs=jobs)


def command(job, execute):
    args = [sys.executable, "-B", str(ROOT / "scripts/generate_raw.py"),
            "--benchmark", job["benchmark"], "--problem-id", job["problem_id"],
            "--output-dir", job["output_dir"], "--endpoint", job["endpoint"],
            "--raw-seed-offset", str(job["raw_seed_offset"]), "--resume"]
    return args + (["--execute-models"] if execute else [])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--endpoints", nargs=2,
                        default=["http://127.0.0.1:8030/v1", "http://127.0.0.1:8031/v1"])
    parser.add_argument("--execute-models", action="store_true")
    args = parser.parse_args(argv)
    output = args.output_dir.expanduser().resolve()
    plan = make_plan(output, args.endpoints)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "plan.json"
    if path.exists() and json.loads(path.read_text()) != plan:
        raise ValueError("Saved ablation plan differs; use a new output directory")
    path.write_text(json.dumps(plan, indent=2) + "\n")
    # Prepare every request before either GPU starts generation.
    for job in plan["jobs"]:
        subprocess.run(command(job, False), check=True, cwd=ROOT)
    if not args.execute_models:
        print(f"Prepared {plan['problem_count']} problems / {plan['planned_requests']} requests; no model calls.")
        return 0

    def worker(index):
        outcomes = []
        for job in plan["jobs"]:
            if job["worker"] != index:
                continue
            result = subprocess.run(command(job, True), cwd=ROOT)
            outcomes.append(dict(problem_id=job["problem_id"], returncode=result.returncode))
            (output / f"worker_{index}.json").write_text(json.dumps(outcomes, indent=2) + "\n")
            if result.returncode not in (0, 2):
                break  # Stop this worker on configuration/server/integrity failures.
        return outcomes

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(worker, range(2)))
    flat = [r for batch in outcomes for r in batch]
    completed = len(flat) == plan["problem_count"] and all(r["returncode"] == 0 for r in flat)
    (output / "queue_result.json").write_text(json.dumps(dict(
        state="completed" if completed else "completed_with_issues", outcomes=flat), indent=2) + "\n")
    return 0 if completed else 2


if __name__ == "__main__":
    raise SystemExit(main())
