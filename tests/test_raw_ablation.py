"""Raw ablation request and queue checks; no model/server calls."""
import ast
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


raw = load("generate_raw")
queue = load("run_raw_ablation")
serve = load("serve_models")


def test_prompts_are_identical_to_the_current_draft_constants():
    source = ROOT / "harnesses/imo_proof_pipeline/releases/1.7.0/engine/source/cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827/run.py"
    constants = {}
    for node in ast.parse(source.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("FROZEN_"):
                    constants[target.id] = ast.literal_eval(node.value)
    prompts = raw.load_runner().prompts()
    for filename, name in (("system.txt", "FROZEN_SYSTEM_PROMPT"),
                           ("user_prefix.txt", "FROZEN_USER_PREFIX"),
                           ("user_suffix.txt", "FROZEN_USER_SUFFIX")):
        assert prompts[filename] == constants[name]


@pytest.mark.parametrize("benchmark,pid,number", [
    ("imo-proofbench/basic", "PB-Basic-009", 9),
    ("imo-proofbench/advanced", "PB-Advanced-030", 30),
    ("imo2026", "imo2026_p6", 6),
])
def test_official_raw_preflight_makes_four_single_turn_requests(tmp_path, monkeypatch, benchmark, pid, number):
    runner = raw.load_runner()
    monkeypatch.setattr(runner, "http_json", lambda *a, **k: pytest.fail("Network call"))
    monkeypatch.setattr(raw, "load_runner", lambda: runner)
    assert raw.main(["--benchmark", benchmark, "--problem-id", pid,
                     "--output-dir", str(tmp_path)]) == 0
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["total"] == 4 and summary["budget_forcing"] is False
    requests = [json.loads(p.read_text()) for p in tmp_path.glob("problems/*/candidates/*/request.json")]
    assert sorted(r["temperature"] for r in requests) == [0.7, 0.7, 1.0, 1.0]
    for request in requests:
        assert [m["role"] for m in request["messages"]] == ["system", "user"]
        assert request["max_tokens"] == 65536 and request["n"] == 1
        assert request["ignore_eos"] is False and request["min_tokens"] == 0
        assert request["chat_template_kwargs"] == {"enable_thinking": True}
        assert "tools" not in request and "thinking_token_budget" not in request
    assert {r["problem_number"] for r in summary["rows"]} == {number}


def test_two_gpu_queue_covers_all_requested_problems_with_matching_basic_seeds(tmp_path):
    plan = queue.make_plan(tmp_path, ["http://127.0.0.1:8030/v1", "http://127.0.0.1:8031/v1"])
    assert plan["problem_count"] == 38 and plan["planned_requests"] == 152
    jobs = plan["jobs"]
    assert len({r["problem_id"] for r in jobs}) == 38
    assert [sum(r["worker"] == i for r in jobs) for i in (0, 1)] == [19, 19]
    runner = raw.load_runner()
    for job in jobs[-2:]:
        manifest = json.loads((ROOT / job["seed_source"]).with_name("frontend_manifest.json").read_text())
        number = int(job["problem_id"].rsplit("-", 1)[1])
        recorded = {r["candidate_id"]: r["seed"] for r in manifest["candidate_specs"]}
        for cid, _, base in runner.CANDIDATES:
            assert runner.stable_seed(number, cid, base, job["raw_seed_offset"]) == runner.stable_seed(number, cid, recorded[cid], 0)
        assert "--execute-models" not in queue.command(job, False)
        assert "--execute-models" in queue.command(job, True)


def test_second_gemma_server_uses_separate_gpu_and_port(tmp_path):
    command, environment, _ = serve.plan("gemma", tmp_path, 1, port=8031)
    assert command[command.index("--port") + 1] == "8031"
    assert environment["CUDA_VISIBLE_DEVICES"] == "1"
    assert json.loads(command[command.index("--speculative-config") + 1])["num_speculative_tokens"] == 4
