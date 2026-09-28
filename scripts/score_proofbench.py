#!/usr/bin/env python3
"""Grade explicit ProofBench submissions with the frozen B.5 evaluator.

Supply --dataset with the official, hash-pinned proofbench_v2.csv and
--task-manifest with {"tasks": [{"problem_id": "PB-Basic-029",
"candidate_id": "t10_r01", "proof_path": "proof.md", "expected_hashes":
{"proof_sha256": "..."}}]}. Proof paths are relative to their manifest;
text hashes cover stripped UTF-8 text. A top-level proof_sha256 also works.

The archived runner writes summary.json (rows with state, grade.score,
grade.category, and result_path), status.json, report.md, and per-submission
cases/<problem_id>/<candidate_id>/ artifacts. It accepts only 0, 1, 6, or 7.
--dry-run validates all bindings and writes prompts without invoking Codex.
This entrypoint never downloads references or starts generation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import signal

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/grading/scorer"
ARCHIVE_HASHES = {
    "scripts/score.py": "ff0ec706ca68604bda672f0aca7d7390c757d888366b605c1e22a1b8c14b52ab",
    "references/proof_autograder_prompt.txt": "e71ec3a05b6fa906e27fa7f95dabe5f950786eafa921ba526afe7596af809b4c",
    "references/source.json": "9a8b8c2038248b6dadafbf4476548431f7db9913111ddd74865a03b6575be8bb",
    "references/evaluator_instructions.txt": "015e67bb885a2531c0aa51431d404c9d479d6676a024dca2a24df0a332f2587c",
}
DATASET_SHA256 = "aa8b813dbd4068137e3d165e5da228f6e0e1cc85a91c37883e1791b954e43af0"


def prepare_runner():
    """Load the unchanged archived runner only after verifying its inputs."""
    contents = {}
    for relative, expected in ARCHIVE_HASHES.items():
        data = (ARCHIVE / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Archived B.5 scorer changed: {relative}")
        contents[relative] = data
    source = json.loads(contents["references/source.json"])
    if source["dataset_sha256"] != DATASET_SHA256:
        raise ValueError("Frozen B.5 dataset identity changed")
    path = ARCHIVE / "scripts/score.py"
    spec = importlib.util.spec_from_file_location("workshop_proofbench_b5_runner", path)
    runner = importlib.util.module_from_spec(spec)
    # Execute exactly the bytes just verified, without creating archive pyc files.
    exec(compile(contents["scripts/score.py"], str(path), "exec"), runner.__dict__)
    return runner


def validate_manifests(paths):
    """Reject ambiguous bindings before the archived runner selects any task."""
    seen = set()
    hash_fields = {f"{name}_sha256" for name in ("problem", "reference", "guidelines", "proof")}
    for path in paths:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        tasks = manifest.get("tasks") if isinstance(manifest, dict) else None
        if not isinstance(tasks, list) or not tasks:
            raise ValueError(f"Task manifest needs a nonempty tasks list: {path}")
        for row in tasks:
            if not isinstance(row, dict):
                raise ValueError(f"Task must be an object: {path}")
            pid, cid = row.get("problem_id"), row.get("candidate_id")
            if not isinstance(pid, str) or not re.fullmatch(r"PB-(?:Basic|Advanced)-\d{3}", pid):
                raise ValueError(f"Invalid ProofBench problem_id: {pid!r}")
            if (not isinstance(cid, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", cid)
                    or cid in {".", ".."}):
                raise ValueError(f"Unsafe candidate_id: {cid!r}")
            if (pid, cid) in seen:
                raise ValueError(f"Duplicate explicit task: {pid}/{cid}")
            seen.add((pid, cid))
            if not isinstance(row.get("proof_path"), str) or not row["proof_path"].strip():
                raise ValueError(f"Task requires proof_path: {pid}/{cid}")
            expected = row.get("expected_hashes", {})
            if not isinstance(expected, dict) or set(expected) - hash_fields:
                raise ValueError(f"Invalid expected_hashes: {pid}/{cid}")
            combined = dict(expected)
            for field in hash_fields:
                if field in row:
                    if field in combined and combined[field] != row[field]:
                        raise ValueError(f"Conflicting {field}: {pid}/{cid}")
                    combined[field] = row[field]
            if "proof_sha256" not in combined:
                raise ValueError(f"Task requires proof_sha256: {pid}/{cid}")
            for field, digest in combined.items():
                if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                    raise ValueError(f"Invalid {field}: {pid}/{cid}")


def preflight(args, runner):
    """Validate every selected proof and official input before any grader call."""
    validate_manifests(args.task_manifest)
    _, source = runner.template_and_source()
    dataset, _ = runner.dataset_rows(args.dataset, source["dataset_sha256"])
    for row, base in runner.source_bindings(args).values():
        if row["problem_id"] not in dataset:
            raise ValueError(f"Problem is absent from the official dataset: {row['problem_id']}")
        runner.bind(row, base, dataset)
    if not args.dry_run and shutil.which(args.codex_bin) is None:
        raise ValueError(f"Codex executable not found: {args.codex_bin}; use --codex-bin")


def parser():
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--task-manifest", type=Path, action="append", required=True)
    result.add_argument("--dataset", type=Path, required=True, help="Official CSV; its frozen source hash is required")
    result.add_argument("--output-dir", type=Path, required=True)
    result.add_argument("--cache-dir", type=Path, action="append", default=[])
    result.add_argument("--workers", type=int, default=4)
    result.add_argument("--model", default="gpt-5.6-sol")
    result.add_argument("--reasoning-effort", default="xhigh")
    result.add_argument("--codex-bin", default="codex")
    result.add_argument("--max-attempts", type=int, choices=[1, 2], default=2)
    result.add_argument("--timeout-sec", type=int, default=1200)
    result.add_argument("--dry-run", action="store_true")
    result.add_argument("--resume", action="store_true")
    result.add_argument("--retry-failed", action="store_true")
    # Bind only the explicit submissions supplied by the suite orchestrator.
    result.set_defaults(source_report=[], source_run=[], problem_id=[], dataset_sha256=DATASET_SHA256)
    return result


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    if args.workers < 1 or args.timeout_sec < 1:
        cli.error("workers and timeout must be positive")
    if args.retry_failed and not args.resume:
        cli.error("--retry-failed requires --resume")
    if not args.model.strip() or not args.reasoning_effort.strip():
        cli.error("model and reasoning effort must be nonempty")
    try:
        runner = prepare_runner()
        preflight(args, runner)
        previous = {sig: signal.signal(sig, runner.terminate_children) for sig in (signal.SIGINT, signal.SIGTERM)}
        try:
            payload = runner.run(args)
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    except (OSError, ValueError) as error:
        cli.exit(1, f"{error}\n")
    return 0 if payload["state"] in {"completed", "dry_run"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
