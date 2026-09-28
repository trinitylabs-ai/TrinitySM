"""Detached, bounded end-to-end proof portfolio with isolated external scoring.

The experiment configuration is data, not a theorem-specific harness adapter.
Scoring artifacts never enter model prompts. Completed case/score hashes allow
the controller to resume without regenerating or rescoring successful work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from .rewrite import write_record


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(config):
    required = {"problem_file", "proofs", "master_seed", "strict_skill_launcher", "pilot_score", "portfolio_minimum_score"}
    if not required <= set(config):
        raise ValueError("experiment configuration is incomplete")
    if config.get("entrypoint", "rewrite") not in {"rewrite", "proof_harness"}:
        raise ValueError("unsupported portfolio harness entrypoint")
    if not config["proofs"]:
        raise ValueError("proof portfolio is empty")
    labels = [row["label"] for row in config["proofs"]]
    if len(set(labels)) != len(labels) or any(not label.replace("_", "").isalnum() for label in labels):
        raise ValueError("case labels must be unique safe identifiers")
    paths = [Path(row["path"]).resolve() for row in config["proofs"]]
    if len(set(paths)) != len(paths) or len({digest(path) for path in paths}) != len(paths):
        raise ValueError("portfolio must contain distinct proof inputs")
    for path in [Path(config["problem_file"]), Path(config["strict_skill_launcher"]), *paths]:
        if not path.is_file():
            raise FileNotFoundError(path)
    if not 0 <= config["portfolio_minimum_score"] <= config["pilot_score"] <= 7:
        raise ValueError("invalid score thresholds")
    for flag in ("pilot_gate_enabled", "continue_on_case_failure"):
        if flag in config and not isinstance(config[flag], bool):
            raise ValueError(f"{flag} must be a boolean")


def wait_process(command, log, status_path, status, *, timeout_seconds):
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
        started = time.monotonic()
        while process.poll() is None:
            status.update(worker_pid=process.pid, heartbeat_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            write_record(status_path, status)
            if timeout_seconds is not None and time.monotonic() - started > timeout_seconds:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise TimeoutError("experiment stage exceeded its fixed wall-time budget")
            time.sleep(15)
        return process.returncode


def score_from_summary(root):
    summary = read(root / "summary.json")
    if summary.get("state") != "completed" or summary.get("policy_mode") != "strict":
        raise ValueError("score is not a completed strict-policy result")
    rows = summary.get("rows", summary.get("results", summary.get("candidates", [])))
    if isinstance(rows, dict):
        rows = list(rows.values())
    if len(rows) != 1:
        # Each isolated candidate owns its canonical detailed summary.
        candidates = list(root.glob("*/*/summary.json"))
        if len(candidates) != 1:
            raise ValueError("strict scorer did not produce one isolated candidate")
        row = read(candidates[0])
    else:
        row = rows[0]
    score = row.get("score", row.get("grade"))
    if isinstance(score, dict):
        score = score.get("score")
    if score is None and isinstance(row.get("parsed"), dict):
        score = row["parsed"].get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 7:
        raise ValueError("strict scoring has no valid integer score")
    return score, row


def packaged_result(root, result, source_proof):
    """Normalize the current packaged harness without weakening publication."""
    from .proof_harness import SCHEMA
    manifest = read(root / "manifest.json")
    if (result.get("schema") != SCHEMA or manifest.get("schema") != SCHEMA
            or manifest.get("preloaded_certificate") is not False or manifest.get("detection_from")):
        raise ValueError("portfolio requires fresh detection in the packaged harness")
    if any(digest(root / name) != expected for name, expected in manifest["input_artifacts"].items()):
        raise ValueError("packaged harness source artifact changed")
    if (root / "input/source_proof.md").read_text().strip() != source_proof.read_text().strip():
        raise ValueError("packaged harness used a different source proof")
    normalized = dict(result, problem_id=manifest["problem_id"], fresh_detection=True)
    if result.get("state") == "completed" and result.get("proof_audit_passed") is True:
        if result.get("outcome") != "REWRITTEN_AUDIT_PASS":
            raise ValueError("packaged publication has contradictory audit status")
        normalized.update(terminal_proof=result["rewritten_proof"],
                          terminal_proof_sha256=result["rewritten_proof_sha256"])
    else:
        normalized.update(state="failed_closed", error=result.get("error") or result.get("outcome")
                          or "no accepted tool-assisted rewrite")
    return normalized


def run(config_path, output):
    config = read(config_path)
    validate_config(config)
    entrypoint = config.get("entrypoint", "rewrite")
    output.mkdir(parents=True, exist_ok=True)
    binding = {"configuration_sha256": digest(config_path),
               "problem_sha256": digest(Path(config["problem_file"])),
               "proof_sha256": {row["label"]: digest(Path(row["path"])) for row in config["proofs"]}}
    binding_path = output / "input_binding.json"
    if binding_path.is_file() and read(binding_path) != binding:
        raise ValueError("experiment inputs changed; use a new output directory")
    write_record(binding_path, binding)
    status_path = output / "status.json"
    status = {"state": "running", "cases": [], "config": str(config_path.resolve()),
              "pilot_score_required": config["pilot_score"], "portfolio_minimum_score": config["portfolio_minimum_score"],
              "pilot_gate_enabled": config.get("pilot_gate_enabled", True),
              "continue_on_case_failure": config.get("continue_on_case_failure", False)}
    write_record(status_path, status)
    try:
        for index, case in enumerate(config["proofs"]):
            label = case["label"]
            case_root = output / label
            case_root.mkdir(exist_ok=True)
            rewrite_root = case_root / "rewrite"
            status.update(stage="end_to_end_rewrite", active_case=label)
            if not (rewrite_root / "result.json").is_file():
                if rewrite_root.exists():
                    raise RuntimeError("interrupted case retained for safe mechanical recovery; not overwritten")
                command = [sys.executable, "-B", "-u", "-m", __package__ + "." + entrypoint,
                    "--problem-file", str(Path(config["problem_file"]).resolve()),
                    "--proof-file", str(Path(case["path"]).resolve()), "--output-dir", str(rewrite_root.resolve()),
                    "--master-seed", str(config["master_seed"] + index * 10_000)]
                if entrypoint == "proof_harness":
                    command.append("--execute-models")
                for operation in config.get("excluded_operations", []):
                    command.extend(("--exclude-operation", operation))
                code = wait_process(command, case_root / "rewrite.log", status_path, status,
                                    timeout_seconds=None if entrypoint == "proof_harness" else 21_600)
                if code != 0 and not (rewrite_root / "result.json").is_file():
                    raise RuntimeError(f"case {label} did not complete; inspect its retained rewrite artifacts")
            result = read(rewrite_root / "result.json")
            if entrypoint == "proof_harness":
                result = packaged_result(rewrite_root, result, Path(case["path"]))
            if result.get("state") == "failed_closed":
                from .recovery import eligible_rejections
                if entrypoint == "rewrite" and eligible_rejections(rewrite_root):
                    recovery_root = case_root / "semantic_recovery_01"
                    status.update(stage="bounded_semantic_recovery")
                    if not (recovery_root / "result.json").is_file():
                        if recovery_root.exists():
                            raise RuntimeError("interrupted semantic recovery retained; no repeated audit sampling")
                        command = [sys.executable, "-B", "-u", "-m", __package__ + ".recovery",
                            "--source-run", str(rewrite_root.resolve()), "--output-dir", str(recovery_root.resolve()),
                            "--master-seed", str(config["master_seed"] + index * 10_000 + 5000)]
                        code = wait_process(command, case_root / "semantic_recovery.log", status_path, status, timeout_seconds=14_400)
                        if code != 0 and not (recovery_root / "result.json").is_file():
                            raise RuntimeError("semantic recovery failed mechanically; inspect its retained log")
                    rewrite_root = recovery_root
                    result = read(rewrite_root / "result.json")
                    if (result.get("state") == "failed_closed" and result.get("stage") == "verified_certificate_rendering"
                            and result.get("reused_case_certificate") is True):
                        resumed_root = recovery_root / "mechanical_synthesis_resume_01"
                        status.update(stage="resume_saved_certificate_synthesis")
                        if not (resumed_root / "result.json").is_file():
                            if resumed_root.exists():
                                raise RuntimeError("interrupted mechanical resume retained; no duplicate synthesis calls")
                            command = [sys.executable, "-B", "-u", "-m", __package__ + ".recovery",
                                "--resume-accepted-synthesis", "--source-run", str(recovery_root.resolve()),
                                "--output-dir", str(resumed_root.resolve()),
                                "--master-seed", str(config["master_seed"] + index * 10_000 + 5000)]
                            code = wait_process(command, case_root / "synthesis_resume.log", status_path, status, timeout_seconds=14_400)
                            if code != 0 and not (resumed_root / "result.json").is_file():
                                raise RuntimeError("saved-certificate resume failed; inspect its retained log")
                        rewrite_root = resumed_root
                        result = read(rewrite_root / "result.json")
                if result.get("state") != "completed":
                    status["cases"].append({"label": label, "state": "failed_closed", "score": None,
                        "result_root": str(rewrite_root.resolve()), "stage": result.get("stage"),
                        "error": result.get("error", "no promotable exact and semantically accepted formalization")})
                    write_record(status_path, status)
                    if config.get("continue_on_case_failure", False):
                        continue
                    status.update(state="needs_generic_refinement", stage="no_promoted_formalization",
                        error=result.get("error", "no promotable exact and semantically accepted formalization"))
                    break
            if result.get("state") != "completed" or result.get("fresh_detection") is not True:
                raise ValueError("case is not a completed fresh-detection-to-synthesis run")
            proof = Path(result["terminal_proof"]).resolve()
            if rewrite_root.resolve() not in proof.parents:
                raise ValueError("terminal proof escaped its case root")
            proof_hash = hashlib.sha256(proof.read_text(encoding="utf-8").strip().encode()).hexdigest()
            if proof_hash != result["terminal_proof_sha256"]:
                raise ValueError("terminal proof hash mismatch")
            score_root = case_root / "strict_score"
            status.update(stage="independent_strict_score")
            if not (score_root / "summary.json").is_file():
                if score_root.exists():
                    raise RuntimeError("interrupted strict-score artifacts retained; not overwritten or mixed")
                command = [sys.executable, str(Path(config["strict_skill_launcher"]).resolve()),
                    "--proof-task", f"{result['problem_id']}:{label}={proof}",
                    "--output-dir", str(score_root.resolve()), "--workers", "1",
                    "--model-output-format", "markdown"]
                code = wait_process(command, case_root / "strict_score.log", status_path, status, timeout_seconds=7800)
                if code != 0:
                    raise RuntimeError("isolated strict scoring failed")
            score, detail = score_from_summary(score_root)
            if detail.get("proof_sha256") != proof_hash or detail.get("problem_id") != result["problem_id"]:
                raise ValueError("strict result does not bind this submitted proof")
            record = {"label": label, "score": score, "proof": str(proof), "proof_sha256": proof_hash,
                      "score_root": str(score_root.resolve()), "strict_result": detail}
            status["cases"].append(record)
            write_record(status_path, status)
            if index == 0 and config.get("pilot_gate_enabled", True) and score < config["pilot_score"]:
                status.update(state="needs_generic_refinement", stage="pilot_gate_not_met")
                break
        else:
            best = max((row["score"] for row in status["cases"] if row["score"] is not None), default=None)
            status.update(state="completed" if best is not None and best >= config["portfolio_minimum_score"] else "needs_generic_refinement",
                          stage="finished", best_score=best, score_vector=[row["score"] for row in status["cases"]],
                          failed_cases=[row["label"] for row in status["cases"] if row["score"] is None])
    except Exception as error:
        status.update(state="needs_mechanical_review", error=f"{type(error).__name__}: {error}")
    write_record(status_path, status)
    write_record(output / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.config, args.output_dir.resolve())
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result["state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
