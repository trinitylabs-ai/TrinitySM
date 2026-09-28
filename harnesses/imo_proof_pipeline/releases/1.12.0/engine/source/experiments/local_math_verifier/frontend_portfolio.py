"""Truthful terminal handoff for a frontend with independently failed lanes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA = "frontend-terminal-portfolio-v1"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def proof_hash(path):
    return hashlib.sha256(Path(path).read_text().strip().encode()).hexdigest()


def candidate_dir(root, number, candidate):
    return root / f"phase_1_raw_lazy/p{number}/candidates" / candidate


def save_failure(root, problem, source, failure):
    directory = candidate_dir(root, problem["problem_number"], source["candidate_id"])
    path = directory / "frontend_failure.json"
    proof = source.get("proof_path")
    if proof:
        if Path(proof).resolve() != (directory / "draft_proof.md").resolve():
            raise ValueError("Failed frontend draft path drift")
        if proof_hash(proof) != source["proof_sha256"]:
            raise ValueError("Failed frontend draft hash drift")
    record = {**failure, "state": "failed_closed", "problem_id": problem["problem_id"],
              "checkpoint": "raw_draft" if proof else "no_proof",
              "proof_path": proof, "proof_sha256": source.get("proof_sha256") if proof else None}
    write(path, record)
    return record


def finish(root, problem, ids, successful, failures):
    by_id = {row["candidate_id"]: row for row in successful}
    lanes = []
    for candidate in ids:
        directory = candidate_dir(root, problem["problem_number"], candidate)
        if candidate in by_id:
            result = by_id[candidate]
            row = {"candidate_id": candidate, "state": "ready", "checkpoint": "lazy_checked",
                   "source_proof_path": result["checked_proof_path"],
                   "source_proof_sha256": result["checked_proof_sha256"],
                   "source_result_path": str((directory / "result.json").resolve())}
        else:
            failure = failures[candidate]
            row = {"candidate_id": candidate, "state": "failed_closed", "checkpoint": failure["checkpoint"],
                   "source_proof_path": failure["proof_path"], "source_proof_sha256": failure["proof_sha256"],
                   "source_result_path": str((directory / "frontend_failure.json").resolve())}
        row["source_result_file_sha256"] = digest(row["source_result_path"])
        lanes.append(row)
    portfolio = {"schema": SCHEMA, "problem_id": problem["problem_id"],
                 "problem_number": problem["problem_number"], "problem_path": str(problem["path"]),
                 "problem_sha256": problem["sha256"], "lanes": lanes}
    path = root / "frontend_portfolio.json"
    write(path, portfolio)
    summary = {"state": "completed_with_failed_lanes", "terminal_checkpoint": "frontend_terminal",
               "problem_id": problem["problem_id"], "candidate_ids": list(ids),
               "candidate_count": len(ids), "completed_lane_count": len(successful),
               "failed_lanes": list(failures), "downstream_model_calls_performed": 0,
               "portfolio_path": str(path.resolve()), "portfolio_sha256": digest(path)}
    write(root / "phase_1_raw_lazy/result.json", {**summary, "results": successful, "failures": failures})
    write(root / "summary.json", summary)
    write(root / "status.json", {**summary, "stage": "done"})
    return summary


def load(root, number, expected_id=None):
    root = root.resolve()
    path = root / "frontend_portfolio.json"
    summary = read(root / "summary.json")
    if (summary.get("state") != "completed_with_failed_lanes"
            or summary.get("terminal_checkpoint") != "frontend_terminal"
            or Path(summary["portfolio_path"]).resolve() != path
            or summary["portfolio_sha256"] != digest(path)):
        raise ValueError("Frontend portfolio binding drift")
    data = read(path)
    problem_path = root / "input/problem.json"
    problem = read(problem_path)
    if (data.get("schema") != SCHEMA or data["problem_number"] != number
            or (expected_id is not None and data["problem_id"] != expected_id)
            or problem["problem_id"] != data["problem_id"] or problem["problem_number"] != number
            or Path(data["problem_path"]).resolve() != problem_path
            or hashlib.sha256(problem["claim"].strip().encode()).hexdigest() != data["problem_sha256"]):
        raise ValueError("Frontend problem identity drift")
    ids = [row["candidate_id"] for row in data["lanes"]]
    if len(ids) != 4 or len(set(ids)) != 4 or ids != summary["candidate_ids"]:
        raise ValueError("Frontend requires four unique allocated lanes")
    for row in data["lanes"]:
        directory = candidate_dir(root, number, row["candidate_id"])
        if not directory.resolve().is_relative_to(root):
            raise ValueError("Frontend candidate path drift")
        ready = row["state"] == "ready"
        expected_result = directory / ("result.json" if ready else "frontend_failure.json")
        if (row["state"] not in {"ready", "failed_closed"}
                or Path(row["source_result_path"]).resolve() != expected_result.resolve()
                or digest(expected_result) != row["source_result_file_sha256"]):
            raise ValueError("Frontend result binding drift")
        result = read(expected_result)
        if ready:
            proof, sha = result["checked_proof_path"], result["checked_proof_sha256"]
            checkpoint, filename = "lazy_checked", "checked_proof.md"
        else:
            if result.get("state") != "failed_closed" or result.get("candidate_id") != row["candidate_id"]:
                raise ValueError("Frontend failure identity drift")
            proof, sha = result["proof_path"], result["proof_sha256"]
            checkpoint, filename = ("raw_draft" if proof else "no_proof"), "draft_proof.md"
            row["source_failure"] = result
        if (row["checkpoint"] != checkpoint or row["source_proof_path"] != proof
                or row["source_proof_sha256"] != sha):
            raise ValueError("Frontend checkpoint binding drift")
        if proof and (Path(proof).resolve() != (directory / filename).resolve() or proof_hash(proof) != sha):
            raise ValueError("Frontend proof binding drift")
        if not proof and (ready or sha is not None):
            raise ValueError("Frontend missing proof is not a failed lane")
    return {**data, "proofs": data["lanes"]}
