#!/usr/bin/env python3
"""Independent IMOBench grading with the published prompt and official guidelines."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
POLICY = "imobench-proof-autograder-b5-v1"
TERMINAL = {"completed", "completed_with_failed_lanes", "failed_closed"}
CATEGORIES = {0: "Incorrect", 1: "Partial", 6: "Almost", 7: "Correct"}
TEXT_FIELDS = ("problem", "reference", "guidelines", "proof")
CANDIDATES = ("t10_r01", "t10_r02", "t07_r01", "t07_r02")
STOP = threading.Event()
CHILDREN = set()
CHILD_LOCK = threading.Lock()
ISOLATION_CONFIG = {
    "suppress_unstable_features_warning": True,
    "features.skip_host_skill_discovery": True,
    "features.skill_search": False,
    "features.plugins": False,
    "features.remote_plugin": False,
    "features.apps": False,
    "features.shell_tool": False,
    "features.unified_exec": False,
    "features.code_mode": False,
    "features.code_mode_host": False,
    "features.multi_agent": False,
    "features.multi_agent_v2": False,
    "features.browser_use": False,
    "features.computer_use": False,
    "features.image_generation": False,
    "features.view_image": False,
    "features.memories": False,
    "features.hooks": False,
    "features.sleep_tool": False,
    "features.goals": False,
    "tools.view_image": False,
    "tools.web_search": False,
    "web_search": "disabled",
    "project_doc_max_bytes": 0,
}
DISABLED_SKILL_PATHS = sorted({str(p.resolve()) for root in
    [Path.home() / ".codex/skills", Path.home() / ".agents/skills", Path("/etc/codex/skills"),
     Path.home() / ".codex/plugins/cache"] if root.exists() for p in root.rglob("SKILL.md")})


def isolation_arguments():
    overrides = [arg for key, value in ISOLATION_CONFIG.items()
                 for arg in ["--config", key + "=" + json.dumps(value)]]
    disabled = "[" + ",".join("{path=" + json.dumps(p) + ",enabled=false}" for p in DISABLED_SKILL_PATHS) + "]"
    return overrides + ["--config", "skills.config=" + disabled,
                        "--config", "model_instructions_file=" + json.dumps(str(SKILL / "references/evaluator_instructions.txt"))]


def validate_trace(path):
    item_types = set()
    completed_turns = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if "ERROR codex_core::tools::router" in line:
            raise ValueError("Grader isolation violation: attempted unavailable tool")
        try:
            event = json.loads(line)
        except ValueError:
            continue  # CLI diagnostics may precede the JSON event stream.
        if event.get("type") == "turn.completed":
            completed_turns += 1
        kind = event.get("item", {}).get("type")
        if kind == "error" and event["item"].get("message", "").startswith("Code Mode is unavailable because code-mode host is disabled."):
            continue  # Startup diagnostic, not a model action.
        if kind:
            item_types.add(kind)
    if item_types - {"agent_message", "reasoning"}:
        raise ValueError(f"Grader isolation violation: unexpected tool/item types {sorted(item_types)}")
    if completed_turns != 1 or "agent_message" not in item_types:
        raise ValueError("Missing complete independent grading turn in event log")
    return {"tool_calls": 0, "completed_turns": completed_turns, "item_types": sorted(item_types)}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def resolve(base, value):
    path = Path(value).expanduser()
    return (base / path if not path.is_absolute() else path).resolve()


def template_and_source():
    text = (SKILL / "references/proof_autograder_prompt.txt").read_text(encoding="utf-8")
    source = read(SKILL / "references/source.json")
    if sha(text) != source["prompt_sha256"]:
        raise ValueError("Published prompt hash mismatch")
    return text, source


def dataset_rows(path, expected_hash):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_hash:
        raise ValueError(f"Dataset hash mismatch: {digest}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = {}
    for row in rows:
        pid = row["Problem ID"].strip()
        if pid in result:
            raise ValueError(f"Duplicate dataset problem: {pid}")
        values = {"problem": row["Problem"].strip(), "reference": row["Solution"].strip(),
                  "guidelines": row["Grading guidelines"].strip()}
        if not all(values.values()):
            raise ValueError(f"Empty official scoring input for {pid}")
        result[pid] = values
    return result, digest


def portfolio_bindings(path):
    summary = read(path)
    if summary.get("state") not in TERMINAL:
        return []
    bindings = []
    for candidate, lane in summary["lanes"].items():
        current = lane.get("current_proof")
        bindings.append({"problem_id": summary["problem_id"], "candidate_id": candidate,
                         "source_summary": str(path.resolve()), "source_summary_sha256": sha(path.read_text()),
                         "proof_path": current["proof_path"] if current else None,
                         "proof_sha256": current["proof_sha256"] if current else None})
    return bindings


def source_bindings(args):
    selected = {}
    for path in args.source_report:
        for row in read(path)["rows"]:
            selected[(row["problem_id"], row["candidate_id"])] = (row, path.parent)
    for root in args.source_run:
        paths = [root / "summary.json"] if (root / "summary.json").is_file() else sorted(root.glob("problems/*/summary.json"))
        for path in paths:
            for row in portfolio_bindings(path):
                selected[(row["problem_id"], row["candidate_id"])] = (row, path.parent)
    for path in args.task_manifest:
        seen = set()
        for row in read(path)["tasks"]:
            key = row["problem_id"], row["candidate_id"]
            if key in seen:
                raise ValueError(f"Duplicate explicit task: {key}")
            seen.add(key)
            selected[key] = (row, path.parent)
    if args.problem_id:
        selected = {k: v for k, v in selected.items() if k[0] in args.problem_id}
    if not selected:
        raise ValueError("No selected terminal proofs or explicit tasks")
    return selected


def bind(row, base, dataset):
    pid, cid = row["problem_id"], row["candidate_id"]
    if not re.fullmatch(r"PB-(?:Basic|Advanced)-\d{3}", pid) or not re.fullmatch(r"[A-Za-z0-9_.-]+", cid) or cid in {".", ".."}:
        raise ValueError("Unsafe problem or candidate identifier")
    task = {"problem_id": pid, "candidate_id": cid, **dataset[pid], "selection": "explicit"}
    proof_value = row.get("proof_path") or row.get("source_proof")
    expected = dict(row.get("expected_hashes", {}))
    expected.update({f + "_sha256": row[f + "_sha256"] for f in TEXT_FIELDS if row.get(f + "_sha256")})
    if row.get("source_summary"):
        path = resolve(base, row["source_summary"])
        summary_text = path.read_text(encoding="utf-8")
        if row.get("source_summary_sha256") and sha(summary_text) != row["source_summary_sha256"]:
            raise ValueError(f"Source summary hash mismatch: {path}")
        summary = json.loads(summary_text)
        if summary.get("state") not in TERMINAL or summary["problem_id"] != pid:
            raise ValueError(f"Source portfolio is unfinished or mismatched: {path}")
        lane = summary["lanes"][cid]
        current = lane.get("current_proof")
        task.update(source_summary=str(path), source_summary_sha256=sha(summary_text),
                    selection="terminal_saved_proof", portfolio_state=summary["state"], lane_state=lane["state"])
        if current is None:
            if lane.get("checkpoints") or lane["state"] != "failed_closed" or proof_value:
                raise ValueError(f"Inconsistent missing proof: {pid}/{cid}")
            task.update(unscorable="no_saved_proof", last_checkpoint="no_proof")
            return task
        if not proof_value or resolve(base, proof_value) != Path(current["proof_path"]).resolve():
            raise ValueError(f"Selected proof differs from terminal proof: {pid}/{cid}")
        checkpoint = lane["checkpoints"][-1]
        if current["proof_sha256"] != checkpoint["proof_sha256"] or expected.get("proof_sha256", current["proof_sha256"]) != current["proof_sha256"]:
            raise ValueError(f"Terminal/checkpoint hash mismatch: {pid}/{cid}")
        expected["proof_sha256"] = current["proof_sha256"]
        task["last_checkpoint"] = checkpoint["checkpoint"]
    if not proof_value:
        raise ValueError(f"No proof bound for {pid}/{cid}")
    path = resolve(base, proof_value)
    task.update(source_proof=str(path), proof=path.read_text(encoding="utf-8").strip())
    if not task["proof"]:
        raise ValueError(f"Empty proof: {pid}/{cid}")
    for field in TEXT_FIELDS:
        key = field + "_sha256"
        task[key] = sha(task[field])
        if key in expected and expected[key] != task[key]:
            raise ValueError(f"{key} mismatch for {pid}/{cid}")
    unknown = set(expected) - {field + "_sha256" for field in TEXT_FIELDS}
    if unknown:
        raise ValueError(f"Unrecognized expected hashes: {unknown}")
    return task


def public(task):
    return {k: v for k, v in task.items() if k not in TEXT_FIELDS}


def make_prompt(template, task):
    mapping = {"problem_statement": task["problem"], "solution": task["reference"],
               "guidelines": task["guidelines"], "student_answer": task["proof"]}
    return re.sub(r"\{(problem_statement|solution|guidelines|student_answer)\}", lambda m: mapping[m[1]], template)


def parse_grade(text):
    matches = re.findall(r"<points>\s*([0167])\s+out\s+of\s+7\s*</points>", text)
    if len(matches) != 1 or text.count("<points>") != 1 or text.count("</points>") != 1:
        raise ValueError("Expected exactly one published-format score in {0,1,6,7}")
    score = int(matches[0])
    return {"score": score, "category": CATEGORIES[score]}


def verify_sources(task):
    if sha(Path(task["source_proof"]).read_text(encoding="utf-8").strip()) != task["proof_sha256"]:
        raise ValueError("Source proof changed during grading")
    if task.get("source_summary") and sha(Path(task["source_summary"]).read_text(encoding="utf-8")) != task["source_summary_sha256"]:
        raise ValueError("Source summary changed during grading")


def cache_identity(task, config):
    identity = {**config, "problem_id": task["problem_id"], **{f + "_sha256": task[f + "_sha256"] for f in TEXT_FIELDS}}
    return sha(json.dumps(identity, sort_keys=True))


def valid_cached(path, expected_key):
    result = read(path)
    if result.get("schema") != POLICY + "-result" or result.get("state") != "completed" or result.get("cache_key") != expected_key:
        return None
    text = (path.parent / "grade.md").read_text(encoding="utf-8")
    if sha(text) != result["response_sha256"] or parse_grade(text) != result["grade"]:
        raise ValueError(f"Corrupt cached grade: {path}")
    audit = read(path.parent / "isolation_audit.json")
    if audit.get("tool_calls") != 0 or audit.get("completed_turns") != 1:
        raise ValueError(f"Cached grade lacks verified isolation: {path}")
    return result


def terminate_children(signum=None, frame=None):
    STOP.set()
    with CHILD_LOCK:
        for child in list(CHILDREN):
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass


def execute_model(prompt, case, args):
    errors = []
    for attempt in range(1, args.max_attempts + 1):
        if STOP.is_set():
            break
        with tempfile.TemporaryDirectory(prefix="imobench_grade_") as tmp:
            last = Path(tmp) / "last_message.md"
            command = [args.codex_bin, "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
                       "--skip-git-repo-check", "--sandbox", "read-only", "--model", args.model,
                       "--config", f'model_reasoning_effort="{args.reasoning_effort}"', *isolation_arguments(),
                       "--output-last-message", str(last), "--json", "--color", "never", "--cd", tmp, "-"]
            write(case / f"attempt_{attempt}.json", {"started_at": now(), "command": command})
            try:
                with (case / f"attempt_{attempt}.jsonl").open("w", encoding="utf-8") as log:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                                               text=True, start_new_session=True)
                    with CHILD_LOCK:
                        CHILDREN.add(process)
                    try:
                        process.communicate(input=prompt, timeout=args.timeout_sec)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                        raise
                    finally:
                        with CHILD_LOCK:
                            CHILDREN.discard(process)
                if process.returncode != 0 or not last.is_file():
                    raise RuntimeError(f"Codex returncode={process.returncode}; final message exists={last.exists()}")
                audit = validate_trace(case / f"attempt_{attempt}.jsonl")
                write(case / "isolation_audit.json", audit)
                response = last.read_text(encoding="utf-8")
                (case / f"grade_attempt_{attempt}.md").write_text(response, encoding="utf-8")
                grade = parse_grade(response)
                (case / "grade.md").write_text(response, encoding="utf-8")
                return grade, sha(response), errors
            except Exception as error:
                errors.append(f"attempt {attempt}: {type(error).__name__}: {error}")
    raise RuntimeError("; ".join(errors) or "Cancelled before grading")


def grade_one(task, output, config, template, args, cached_path=None):
    case = output / "cases" / task["problem_id"] / task["candidate_id"]
    case.mkdir(parents=True, exist_ok=True)
    result = {"schema": POLICY + "-result", **public(task), **config, "state": "running", "started_at": now()}
    try:
        verify_sources(task)
        prompt = make_prompt(template, task)
        result["prompt_sha256"] = sha(prompt)
        for field in TEXT_FIELDS:
            (case / (field + ".md")).write_text(task[field] + "\n", encoding="utf-8")
        (case / "prompt.txt").write_text(prompt, encoding="utf-8")
        write(case / "manifest.json", result)
        if cached_path:
            cached = valid_cached(cached_path, task["cache_key"])
            if cached is None:
                raise ValueError("Invalid requested cache entry")
            shutil.copy2(cached_path.parent / "grade.md", case / "grade.md")
            shutil.copy2(cached_path.parent / "isolation_audit.json", case / "isolation_audit.json")
            result.update(grade=cached["grade"], response_sha256=cached["response_sha256"],
                          reused_from=str(cached_path), failed_attempts=[], new_model_call=False)
        else:
            grade, response_sha, failures = execute_model(prompt, case, args)
            result.update(grade=grade, response_sha256=response_sha, failed_attempts=failures, new_model_call=True)
        verify_sources(task)
        result.update(state="completed", source_artifacts_unchanged=True, isolation_verified=True)
    except Exception as error:
        result.update(state="failed", grade=None, error=f"{type(error).__name__}: {error}")
    result["completed_at"] = now()
    write(case / "result.json", result)
    return result


def report(output, tasks, results, config, state):
    rows = []
    for task in tasks:
        key = task["problem_id"], task["candidate_id"]
        row = {**public(task), **results.get(key, {"state": "unscorable" if task.get("unscorable") else "pending"})}
        row["result_path"] = str(output / "cases" / key[0] / key[1] / "result.json")
        rows.append(row)
    groups = {}
    for row in rows:
        groups.setdefault(row["problem_id"], []).append(row)
    best = {pid: max(r["grade"]["score"] for r in group if r.get("grade")) for pid, group in groups.items()
            if all(r["state"] in {"completed", "unscorable"} for r in group) and any(r.get("grade") for r in group)}
    completed = sum(r["state"] == "completed" for r in rows)
    failed = sum(r["state"] == "failed" for r in rows)
    unscorable = sum(r["state"] == "unscorable" for r in rows)
    status = {"state": state, "updated_at": now(), "completed_count": completed, "failed_count": failed,
              "unscorable_count": unscorable, "total": len(rows), "fully_scored_problems": len(best)}
    payload = {**status, **config, "per_problem_best": best, "sum_per_problem_best": sum(best.values()),
               "best_score_denominator": 7 * len(best), "problems_with_full_credit": sum(v == 7 for v in best.values()),
               "new_graded_proofs": sum(r.get("new_model_call", False) and r["state"] == "completed" for r in rows),
               "reused_proofs": sum(bool(r.get("reused_from")) for r in rows),
               "failed_attempts_in_successful_tasks": sum(len(r.get("failed_attempts", [])) for r in rows), "rows": rows}
    write(output / "summary.json", payload)
    write(output / "status.json", status)
    candidates = sorted({r["candidate_id"] for r in rows}, key=lambda c: (CANDIDATES.index(c) if c in CANDIDATES else len(CANDIDATES), c))
    lines = ["# IMOBench scoring with official per-problem guidelines", "",
             f"Grader: {config['model']}; effort: {config['reasoning_effort']}; allowed scores: 0, 1, 6, 7.", "",
             f"Coverage: {completed}/{len(rows) - unscorable} saved proofs; grading failures: {failed}; lanes without proofs: {unscorable}.", "",
             f"Sum of per-problem best scores: {sum(best.values())}/{7 * len(best)} across {len(best)} fully scored portfolios.",
             "The best column selects the maximum across the displayed candidates; it is not a single-submission benchmark score.", "",
             "| Problem | " + " | ".join(candidates) + " | Best |",
             "|---|" + "---:|" * (len(candidates) + 1)]
    for pid, group in groups.items():
        by_candidate = {r["candidate_id"]: r for r in group}
        values = []
        for cid in candidates:
            r = by_candidate.get(cid, {})
            values.append(str(r["grade"]["score"]) if r.get("grade") else r.get("state", "—"))
        lines.append(f"| {pid} | " + " | ".join(values) + f" | {best.get(pid, 'pending')} |")
    lines += ["", f"Prompt SHA-256: `{config['prompt_template_sha256']}`.",
              f"Official dataset SHA-256: `{config['dataset_sha256']}`.", "",
              "Published rubric: https://arxiv.org/html/2511.01846v1#A2.SS5", "", "## Individual grading reports", ""]
    for r in rows:
        label = f"{r['grade']['score']}/7 — {r['grade']['category']}" if r.get("grade") else r["state"]
        response = Path(r["result_path"]).parent / "grade.md"
        lines.append(f"- {r['problem_id']} {r['candidate_id']} ({r.get('last_checkpoint', 'explicit')}): **{label}**. [Grading report]({response}).")
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def run(args):
    template, source = template_and_source()
    dataset, dataset_hash = dataset_rows(args.dataset, args.dataset_sha256 or source["dataset_sha256"])
    config = {"policy_mode": POLICY, "prompt_template_sha256": sha(template), "dataset_sha256": dataset_hash,
              "model": args.model, "reasoning_effort": args.reasoning_effort,
              "isolation_config_sha256": sha(json.dumps(ISOLATION_CONFIG, sort_keys=True)),
              "disabled_skill_paths_sha256": sha(json.dumps(DISABLED_SKILL_PATHS)),
              "evaluator_instructions_sha256": sha((SKILL / "references/evaluator_instructions.txt").read_text())}
    tasks = [bind(row, base, dataset) for row, base in source_bindings(args).values()]
    tasks.sort(key=lambda t: (t["problem_id"], CANDIDATES.index(t["candidate_id"]) if t["candidate_id"] in CANDIDATES else 4, t["candidate_id"]))
    for task in tasks:
        if not task.get("unscorable"):
            task["cache_key"] = cache_identity(task, config)
    fingerprint = sha(json.dumps({"config": config, "tasks": [public(t) for t in tasks]}, sort_keys=True))
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()) and not args.resume:
        raise ValueError("Use a new empty output directory or --resume")
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (output / "manifest.json").exists():
            if read(output / "manifest.json")["fingerprint"] != fingerprint:
                raise ValueError("Resume input selection, source hashes or grading configuration changed")
        else:
            write(output / "manifest.json", {"schema": POLICY + "-manifest", "created_at": now(), **config,
                                             "fingerprint": fingerprint, "workers": args.workers,
                                             "runner_sha256": sha(Path(__file__).read_text()),
                                             "specific_guidelines_supplied": True, "pipeline_reviews_supplied": False,
                                             "prior_grades_supplied": False, "tasks": [public(t) for t in tasks]})
            shutil.copy2(SKILL / "references/proof_autograder_prompt.txt", output / "prompt_template.txt")
            write(output / "prompt_source.json", source)
        if args.dry_run:
            for task in tasks:
                if task.get("unscorable"):
                    continue
                case = output / "cases" / task["problem_id"] / task["candidate_id"]
                case.mkdir(parents=True, exist_ok=True)
                (case / "prompt.txt").write_text(make_prompt(template, task), encoding="utf-8")
            payload = report(output, tasks, {}, config, "dry_run")
            print(json.dumps({"state": "dry_run", "tasks": len(tasks), "unique_proofs": len({t.get('cache_key') for t in tasks if not t.get('unscorable')}), "output": str(output)}), flush=True)
            return payload
        cache = {}
        for root in args.cache_dir:
            for path in sorted(root.glob("cases/*/*/result.json")):
                result = read(path)
                if result.get("state") == "completed" and result.get("schema") == POLICY + "-result":
                    cache.setdefault(result["cache_key"], path)
        results, groups = {}, {}
        for task in tasks:
            if task.get("unscorable"):
                continue
            key = task["problem_id"], task["candidate_id"]
            path = output / "cases" / key[0] / key[1] / "result.json"
            if path.exists():
                result = valid_cached(path, task["cache_key"])
                if result:
                    verify_sources(task)
                    results[key] = result
                    cache[task["cache_key"]] = path
                    continue
                if read(path).get("state") == "completed":
                    raise ValueError(f"Completed result has mismatched grading identity: {path}")
                if not args.retry_failed:
                    results[key] = read(path)
                    continue
                history = path.parent / ("previous_failure_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
                history.mkdir()
                for old in list(path.parent.iterdir()):
                    if old.is_file():
                        shutil.move(str(old), history / old.name)
            groups.setdefault(task["cache_key"], []).append(task)
        report(output, tasks, results, config, "running")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(grade_one, group[0], output, config, template, args, cache.get(ck)): group for ck, group in groups.items()}
            for future in concurrent.futures.as_completed(futures):
                group = futures[future]
                result = future.result()
                key = group[0]["problem_id"], group[0]["candidate_id"]
                results[key] = result
                for task in group[1:]:
                    if result["state"] == "completed":
                        path = output / "cases" / key[0] / key[1] / "result.json"
                        duplicate = grade_one(task, output, config, template, args, path)
                    else:
                        duplicate = {**public(task), "state": "failed", "grade": None, "error": "Identical proof's grading failed"}
                        write(output / "cases" / task["problem_id"] / task["candidate_id"] / "result.json", duplicate)
                    results[task["problem_id"], task["candidate_id"]] = duplicate
                payload = report(output, tasks, results, config, "running")
                print(json.dumps({"time": now(), "problem": key[0], "candidate": key[1], "state": result['state'],
                                  "grade": result.get('grade'), "completed": payload['completed_count'], "total": len(tasks)}), flush=True)
        state = "completed_with_failures" if any(r["state"] == "failed" for r in results.values()) else "completed"
        return report(output, tasks, results, config, state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-report", type=Path, action="append", default=[])
    parser.add_argument("--source-run", type=Path, action="append", default=[])
    parser.add_argument("--task-manifest", type=Path, action="append", default=[])
    parser.add_argument("--problem-id", action="append", default=[])
    parser.add_argument("--dataset", type=Path, default=Path("/srv/datasets/imobench/proofbench_v2.csv"))
    parser.add_argument("--dataset-sha256")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, action="append", default=[])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="xhigh")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--max-attempts", type=int, choices=[1, 2], default=2)
    parser.add_argument("--timeout-sec", type=int, default=1200)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.timeout_sec < 1:
        parser.error("workers and timeout must be positive")
    if args.retry_failed and not args.resume:
        parser.error("--retry-failed requires --resume")
    signal.signal(signal.SIGINT, terminate_children)
    signal.signal(signal.SIGTERM, terminate_children)
    payload = run(args)
    raise SystemExit(0 if payload["state"] in {"completed", "dry_run"} else 1)


if __name__ == "__main__":
    main()
