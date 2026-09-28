#!/usr/bin/env python3
"""Separate strict-v2 evaluator adapter; never imported by the solver.

Reuses the archived strict scorer's prompt, task binding, schema, and batch
execution. Changes only the policy, Rule C contract, and evaluator isolation.
Use --generic-task-manifest with hash-bound problem/reference/proof triples.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "benchmarks/imo2026/results/p2_t07_r02_v356_consolidated_20260917T071542Z/grading/strict_config"
POLICY = ROOT / "docs/public_release/grading/strict_olympiad_policy_v2.txt"
POLICY_SHA256 = "d1c93550ca49f52a35fe4c0eb0b1ccca9534e9112d928002667e404c367de4e4"
INSTRUCTIONS = ROOT / "docs/public_release/grading/evaluator_instructions.txt"
ARCHIVE_HASHES = {
    "runner.py": "f9df6f07c15b0189e483a23a141412ce9e09b6e5b5ed70a4012130e2cc61eeb3",
    "contract.py": "bae2836fe5e498b23b8607a4a330fa878b195f5d99e980c418a2f4aecf6566d4",
    "grade_schema.json": "6c731fb4b521bebf050866086e958d343988a318f8f4118640d8bfef93dc4302",
}
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


def isolation_arguments():
    roots = [Path.home() / ".codex/skills", Path.home() / ".agents/skills",
             Path("/etc/codex/skills"), Path.home() / ".codex/plugins/cache"]
    paths = sorted({str(p.resolve()) for root in roots if root.exists()
                    for p in root.rglob("SKILL.md")})
    disabled = "[" + ",".join("{path=" + json.dumps(p) + ",enabled=false}" for p in paths) + "]"
    return [part for k, v in ISOLATION_CONFIG.items()
            for part in ("--config", k + "=" + json.dumps(v))] + [
        "--config", "skills.config=" + disabled,
        "--config", "model_instructions_file=" + json.dumps(str(INSTRUCTIONS)),
    ]


def validate_trace(text):
    kinds, turns = set(), 0
    for line in text.splitlines():
        if "ERROR codex_core::tools::router" in line:
            raise ValueError("Evaluator attempted an unavailable tool")
        try:
            event = json.loads(line)
        except ValueError:
            continue
        turns += event.get("type") == "turn.completed"
        item = event.get("item", {})
        if item.get("type") == "error" and item.get("message", "").startswith(
                "Code Mode is unavailable because code-mode host is disabled."):
            continue
        if item.get("type"):
            kinds.add(item["type"])
    if kinds - {"agent_message", "reasoning"} or turns != 1 or "agent_message" not in kinds:
        raise ValueError(f"Evaluator isolation failure: item types={sorted(kinds)}, turns={turns}")
    return {"tool_calls": 0, "completed_turns": turns, "item_types": sorted(kinds)}


def isolated_run(command, **kwargs):
    if command[:2] != ["codex", "exec"] or command[-1] != "-":
        raise ValueError("Unexpected evaluator command")
    result = subprocess.run(command[:-1] + isolation_arguments() + ["-"], **kwargs)
    if result.returncode == 0:
        validate_trace(result.stdout)
    return result


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prepare_runner():
    for name, expected in ARCHIVE_HASHES.items():
        if hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Archived scorer changed: {name}")
    contract = load_module("scripts.external_olympiad_scorer.contract", ARCHIVE / "contract.py")
    runner = load_module("workshop_strict_v2_runner", ARCHIVE / "runner.py")
    original_validate = contract.validate_grade

    def validate_v2(value):
        result = original_validate(value)
        if (result["score"] == 5 and result["verdict"] == "substantial_gap"
                and result["repair_complexity"] == "routine_direct"
                and result["olympiad_treatment"] == "partial_credit"):
            result["contract_consistent"] = True
        if (result["score"] == 7 and result["verdict"] == "pass"
                and result["answer_supported"] and result["dependency_impact"] == "none"
                and result["repair_complexity"] in {"none", "routine_direct"}
                and result["olympiad_treatment"] == "full_credit"
                and all(e["severity"] == "cosmetic" for e in result["errors"])):
            # Rule C's deletion-test exception may leave an explicitly recorded
            # cosmetic issue without requiring a mathematical repair.
            result["contract_consistent"] = True
            result["full_credit"] = True
        if not result["contract_consistent"]:
            raise ValueError("Inconsistent score metadata in evaluator response")
        return result

    runner.validate_grade = validate_v2
    runner.STRICT_POLICY = POLICY.read_text(encoding="utf-8").strip()
    if hashlib.sha256(runner.STRICT_POLICY.encode()).hexdigest() != POLICY_SHA256:
        raise ValueError("Strict v2 policy hash mismatch")
    runner.subprocess = SimpleNamespace(run=isolated_run, PIPE=subprocess.PIPE, STDOUT=subprocess.STDOUT)
    original_run_one = runner.run_one

    def run_one(task, output_dir, *args, **kwargs):
        result = original_run_one(task, output_dir, *args, **kwargs)
        case = output_dir / f"p{task['problem_number']}" / task["candidate_id"]
        if result["state"] == "completed":
            # Each successful process was audited before its grade was accepted.
            runner.write_json(case / "isolation_audit.json", {
                "tool_calls": 0, "successful_processes_audited": True,
                "policy_version": "strict-olympiad-v2",
                "evaluator_instructions_sha256": hashlib.sha256(INSTRUCTIONS.read_bytes()).hexdigest(),
            })
        return result

    runner.run_one = run_one
    return runner


if __name__ == "__main__":
    # A v2 invocation cannot silently select the archived calibrated policy.
    sys.argv.extend(["--policy-mode", "strict"])
    prepare_runner().main()
