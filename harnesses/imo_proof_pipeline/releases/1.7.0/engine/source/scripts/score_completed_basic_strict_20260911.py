"""Grade saved terminal Basic portfolios once and maintain a separate strict report."""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
QUEUE = REPO / "runs/basic002_030_v263_v290_run01"
ADDITIONAL_RUNS = []
OUTPUT = REPO / "runs/basic_strict_incremental_20260911"
GOLD = Path("/srv/datasets/imobench/proofbench_v2.csv")
GOLD_HASH = "aa8b813dbd4068137e3d165e5da228f6e0e1cc85a91c37883e1791b954e43af0"
POLICY = "1a8c5d02a7bd84a53ad011cf889ceaaca7ff94166536565bda49082649781ecf"
CANDIDATES = ("t10_r01", "t10_r02", "t07_r01", "t07_r02")
TERMINAL = {"completed", "completed_with_failed_lanes", "failed_closed"}
HASH_FIELDS = ("problem_sha256", "reference_sha256", "proof_sha256")
LAUNCHER = Path("/home/user/.codex/skills/strict-gold-informed-olympiad-scorer/scripts/score.py")


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text())


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def key(row):
    return (row["problem_id"], *(row[name] for name in HASH_FIELDS))


def inventory():
    """Successful scores are reusable; every manifest also reserves its tasks."""
    cached, claimed = {}, set()
    manifests = sorted((REPO / "runs").glob("basic*strict_scores*/manifest.json"))
    manifests += sorted(OUTPUT.glob("batches/*/scores/manifest.json"))
    for path in manifests:
        manifest = read(path)
        if manifest.get("policy_mode") != "strict":
            continue
        if (manifest.get("policy_sha256"), manifest.get("model"), manifest.get("reasoning_effort")) != (POLICY, "gpt-5.6-sol", "xhigh"):
            raise ValueError(f"Different existing strict policy/model; review before scoring: {path}")
        for task in manifest["tasks"]:
            claimed.add(key(task))
            result_path = path.parent / f"p{task['problem_number']}" / task["candidate_id"] / "summary.json"
            if not result_path.exists():
                continue
            result = read(result_path)
            if result.get("state") != "completed" or result.get("errors"):
                continue
            assert key(result) == key(task)
            assert result["policy_sha256"] == POLICY
            cached.setdefault(key(result), []).append((result, result_path))
    return cached, claimed


def collect(cached, claimed):
    assert hashlib.sha256(GOLD.read_bytes()).hexdigest() == GOLD_HASH
    with GOLD.open() as stream:
        gold = {row["Problem ID"]: row for row in csv.DictReader(stream)}
    rows, pending, new_keys = [], [], set()
    for number in range(1, 31):
        problem_id = f"PB-Basic-{number:03d}"
        base = REPO / "runs/basic001_v263_v290_run01" if number == 1 else QUEUE
        source = base / "problems" / problem_id / "summary.json"
        for extra in ADDITIONAL_RUNS:
            candidate = extra / "problems" / problem_id / "summary.json"
            if candidate.is_file() and read(candidate).get("state") in TERMINAL:
                source = candidate
        if not source.exists():
            continue
        summary = read(source)
        if summary.get("state") not in TERMINAL:
            continue
        if summary["state"] == "failed_closed":
            from scripts.run_v263_v290 import validate_failed_portfolio
            validate_failed_portfolio(source.parent, problem_id)
        problem = read(REPO / "data/imo_proofbench_basic_problem_only" / f"{problem_id}.json")["problem"].strip()
        assert problem == gold[problem_id]["Problem"].strip()
        reference = gold[problem_id]["Solution"].strip()
        for candidate in CANDIDATES:
            lane = summary["lanes"][candidate]
            if lane["current_proof"] is None:
                assert lane["state"] == "failed_closed" and not lane["checkpoints"]
                rows.append({"problem_number": number, "problem_id": problem_id, "candidate_id": candidate,
                             "last_checkpoint": "no_proof", "lane_state": lane["state"],
                             "portfolio_state": summary["state"], "unscorable": "no_saved_proof"})
                continue
            current, checkpoint = lane["current_proof"], lane["checkpoints"][-1]
            proof_path = Path(current["proof_path"])
            proof = proof_path.read_text().strip()
            assert sha(proof) == current["proof_sha256"] == checkpoint["proof_sha256"]
            row = {
                "problem_number": number, "problem_id": problem_id, "candidate_id": candidate,
                "problem_sha256": sha(problem), "reference_sha256": sha(reference), "proof_sha256": sha(proof),
                "source_summary": str(source), "source_summary_sha256": sha(source.read_text()),
                "source_proof": str(proof_path), "last_checkpoint": checkpoint["checkpoint"],
                "lane_state": lane["state"],
                "portfolio_state": summary["state"],
            }
            matches = cached.get(key(row), [])
            if matches:
                result, result_path = next(((r, p) for r, p in matches if r["candidate_id"] == candidate), matches[0])
                row.update(grade=result["grade"], score_summary=str(result_path), scored_candidate_id=result["candidate_id"])
            elif key(row) not in claimed and key(row) not in new_keys:
                pending.append((row.copy(), problem, reference, proof))
                new_keys.add(key(row))
            rows.append(row)
    return rows, pending


def report(rows):
    problems = sorted({row["problem_number"] for row in rows})
    vectors, best = {}, {}
    for number in problems:
        group = [row for row in rows if row["problem_number"] == number]
        scores = [row.get("grade", {}).get("score") for row in group]
        vectors[str(number)] = scores
        if all("grade" in r or r.get("unscorable") for r in group) and any(score is not None for score in scores):
            best[str(number)] = max(score for score in scores if score is not None)
    failed = sorted({r["problem_number"] for r in rows if r["portfolio_state"] == "failed_closed"})
    payload = {"updated_at": now(), "model": "gpt-5.6-sol", "reasoning_effort": "xhigh", "policy_mode": "strict",
               "policy_sha256": POLICY, "completed_portfolios": len(problems), "scored_proofs": sum("grade" in r for r in rows),
               "terminal_portfolios": len(problems), "pipeline_completed_portfolios": len(problems) - len(failed), "failed_portfolios": failed,
               "total_proofs": sum(not r.get("unscorable") for r in rows),
               "lanes_without_proofs": sum(bool(r.get("unscorable")) for r in rows), "score_vectors": vectors, "per_problem_best": best,
               "sum_per_problem_best": sum(best.values()), "fully_scored_problems": len(best), "rows": rows}
    write(OUTPUT / "summary.json", payload)
    lines = ["# Strict scores for terminal IMOBench Basic portfolios", "",
             "Four last saved proofs per finished or failed portfolio. Earlier checkpoints from failed lanes are explicitly labeled below.", "",
             f"Pipeline-completed portfolios: {len(problems) - len(failed)}. Portfolios with all lanes failed: {failed or 'none'}.", "",
             f"Model: gpt-5.6-sol; reasoning: xhigh; strict policy SHA-256: `{POLICY}`.", "",
             f"Coverage: {payload['scored_proofs']}/{payload['total_proofs']} available proofs. Best-score sum: {sum(best.values())}/{7 * len(best)} over {len(best)} fully scored problems.", "",
             "Existing matching scores are reused. Pipeline reviews and provenance are excluded from grader inputs.", "",
             "| Problem | t10_r01 | t10_r02 | t07_r01 | t07_r02 | Best |", "|---|---:|---:|---:|---:|---:|"]
    for number in problems:
        scores = vectors[str(number)]
        group = [r for r in rows if r["problem_number"] == number]
        lines.append(f"| {number} | " + " | ".join("no proof" if r.get("unscorable") else "pending" if s is None else str(s) for r, s in zip(group, scores)) + f" | {best.get(str(number), 'pending')} |")
    lines += ["", "## Every proof and its first mathematical defect", ""]
    for row in rows:
        grade = row.get("grade")
        detail = "No saved proof to grade." if row.get("unscorable") else "Pending score."
        if grade:
            defect = str(grade.get("first_issue") or grade.get("summary") or "NONE")
            detail = f"**{grade['score']}/7**, {grade['verdict']}. " + ("No defect identified." if grade["score"] == 7 else defect)
            detail += f" [Grading artifact]({row['score_summary']})."
        lines.append(f"- P{row['problem_number']} {row['candidate_id']} ({row['last_checkpoint']}, {row['lane_state']}): {detail}")
    (OUTPUT / "report.md").write_text("\n".join(lines) + "\n")
    return payload


def score_pending(pending):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    batch = OUTPUT / "batches" / stamp
    inputs = batch / "inputs"
    inputs.mkdir(parents=True)
    tasks, provenance = [], []
    for row, problem, reference, proof in pending:
        prefix = f"p{row['problem_number']}"
        task = {name: row[name] for name in ("problem_number", "problem_id", "candidate_id")}
        task.update(problem_path=f"{prefix}/problem.json", reference_path=f"{prefix}/reference.md",
                    proof_path=f"{prefix}/proofs/{row['candidate_id']}.md", expected_hashes={name: row[name] for name in HASH_FIELDS})
        write(inputs / task["problem_path"], {"problem_id": row["problem_id"], "problem": problem})
        for field, content in (("reference_path", reference), ("proof_path", proof)):
            path = inputs / task[field]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content + "\n")
        tasks.append(task)
        provenance.append(row)
    write(inputs / "tasks.json", {"schema": "gold-informed-generic-proof-task-manifest-v1", "tasks": tasks})
    write(batch / "selection_provenance.json", {"gold_dataset": str(GOLD), "gold_dataset_sha256": GOLD_HASH, "proofs": provenance})
    command = [sys.executable, "-u", "-B", str(LAUNCHER), "--generic-task-manifest", str(inputs / "tasks.json"),
               "--output-dir", str(batch / "scores"), "--workers", "4", "--model-output-format", "markdown"]
    write(OUTPUT / "status.json", {"state": "scoring", "updated_at": now(), "new_proof_count": len(tasks), "active_score_directory": str(batch / "scores")})
    print(json.dumps({"event": "launch", "time": now(), "new_proofs": len(tasks), "batch": str(batch)}), flush=True)
    with (batch / "worker.log").open("w") as log:
        result = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode or read(batch / "scores/summary.json").get("failures"):
        raise RuntimeError(f"Strict batch failed; successful grades are preserved and no batch is automatically rescored: {batch}")


def main():
    global ADDITIONAL_RUNS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only validation and pending counts; launch no calls.")
    parser.add_argument("--additional-run", type=Path, action="append", default=[], help="Use completed portfolios from this run; reuse all existing proof-hash scores")
    parser.add_argument("--watch-queue", type=Path, default=QUEUE)
    parser.add_argument("--history-root", type=Path, help="Preserve previous and new attempt matrices under this experiment root")
    args = parser.parse_args()
    ADDITIONAL_RUNS = [path.resolve() for path in args.additional_run]
    if args.check:
        rows, pending = collect(*inventory())
        print(json.dumps({"completed_portfolios": len(rows) // 4, "cached_scores": sum("grade" in r for r in rows), "new_proofs": len(pending)}))
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "watcher.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            while True:
                rows, pending = collect(*inventory())
                result = report(rows)
                if args.history_root:
                    from scripts.report_basic_attempts import report_history
                    report_history(args.history_root.resolve(), rows)
                if pending:
                    score_pending(pending)
                    continue
                queue_state = read(args.watch_queue / "status.json").get("state")
                complete = False  # A later rerun may still be queued after all 30 IDs have scores.
                if queue_state in {"completed", "completed_with_failed_lanes"}:
                    complete = result["scored_proofs"] == result["total_proofs"]
                state = "completed" if complete else "waiting_for_completed_problems"
                write(OUTPUT / "status.json", {"state": state, "updated_at": now(), "queue_state": queue_state,
                                              "scored_proofs": result["scored_proofs"], "completed_portfolios": result["completed_portfolios"]})
                if complete or queue_state in {"paused_on_failure", "stopped", "stopped_by_user", "failed_closed"}:
                    return
                time.sleep(30)
        except Exception as error:
            write(OUTPUT / "status.json", {"state": "failed", "updated_at": now(), "error": f"{type(error).__name__}: {error}"})
            raise


if __name__ == "__main__":
    main()
