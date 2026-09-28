from __future__ import annotations

import json
import fcntl
from argparse import Namespace
from pathlib import Path

import pytest

from scripts import run_v263_v290 as runner


def problem(directory, problem_id="Example-001", **extra):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{problem_id}.json"
    runner.write(path, {"problem_id": problem_id, "problem": "Prove the stated assertion.", **extra})
    return path


@pytest.mark.parametrize("key", ["Solution", "reference_solution", "Grading guidelines", "Short Answer", "feedback"])
def test_rejects_auxiliary_fields(tmp_path, key):
    problem(tmp_path, **{key: "SENTINEL_DO_NOT_SEND"})
    with pytest.raises(ValueError, match="exactly ID and statement"):
        runner.collect_problems(tmp_path, None, None)


def test_stable_number_before_filter(tmp_path):
    problem(tmp_path, "Example-001")
    problem(tmp_path, "Example-002")
    selected = runner.collect_problems(tmp_path, ["Example-002"], None)
    assert selected[0]["problem_number"] == 2
    assert selected[0]["problem_id"] == "Example-002"


def test_duplicate_ids_fail(tmp_path):
    path = problem(tmp_path)
    runner.write(tmp_path / "duplicate.json", runner.read(path))
    with pytest.raises(ValueError, match="duplicate IDs"):
        runner.collect_problems(tmp_path, None, None)


def test_unknown_selected_problem_fails(tmp_path):
    problem(tmp_path)
    with pytest.raises(ValueError, match="unknown problem"):
        runner.collect_problems(tmp_path, ["Missing"], None)


@pytest.fixture
def engines(monkeypatch):
    frontend, backend = runner.load_engines()
    for key in ("PROBLEM_ID", "PROBLEM_NUMBER", "EXPECTED_PROBLEM_SHA256", "CANDIDATE_IDS"):
        monkeypatch.setattr(backend, key, getattr(backend, key))
    return frontend, backend


def mock_frontend_calls(monkeypatch, frontend):
    """Keep real orchestration, manifests and handoff; replace only model stages."""
    calls = []

    def cold(**kwargs):
        spec, claim = kwargs["spec"], kwargs["problem"]
        calls.append(("cold", spec["candidate_id"]))
        return {"candidate_id": spec["candidate_id"], "problem_id": claim["problem_id"],
                "problem_number": claim["problem_number"], "proof": "Original mock proof."}

    def check(**kwargs):
        row = kwargs["row"]
        calls.append(("check", row["candidate_id"]))
        return {**row, "has_lazy_issues": row["candidate_id"] == "t10_r01"}

    def refine(**kwargs):
        row = kwargs["row"]
        calls.append(("refine", row["candidate_id"]))
        path = kwargs["output_dir"] / "candidates" / row["candidate_id"] / "checked_proof.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "Refined mock proof." if row["has_lazy_issues"] else row["proof"]
        path.write_text(text + "\n", encoding="utf-8")
        result = {**row, "checked_proof_path": str(path.resolve()),
                  "checked_proof_sha256": frontend.sha256_text(text),
                  "lazy_resolve_invoked": row["has_lazy_issues"]}
        runner.write(path.parent / "result.json", result)
        return result

    monkeypatch.setattr(frontend, "run_cold_candidate", cold)
    monkeypatch.setattr(frontend, "run_lazy_check", check)
    monkeypatch.setattr(frontend, "run_lazy_resolve", refine)
    # Any accidental non-dry-run downstream invocation fails before inference.
    monkeypatch.setattr(frontend.enhanced_pipeline, "run_fresh_reviews",
                        lambda **_: pytest.fail("frontend must not run reviews"))
    return calls


def prepared_source(tmp_path, engines, monkeypatch):
    frontend, backend = engines
    calls = mock_frontend_calls(monkeypatch, frontend)
    source = tmp_path / "source"
    phase = source / "p1/01_raw_lazy_enhanced_resolve"
    original = problem(tmp_path / "inputs")
    summary = frontend.run(
        problem_file=original, output_dir=phase, problem_number=1,
        gpu0_gemma_endpoint="http://gemma.example/v1",
        gpu1_qwen_endpoint="http://qwen.example/v1",
        seed_namespace="test", stop_after_lazy=True,
    )
    return source, phase, calls, summary


def test_stop_after_refinement_has_no_frontend_review_calls(tmp_path, engines, monkeypatch):
    source, phase, calls, summary = prepared_source(tmp_path, engines, monkeypatch)
    assert summary["state"] == "completed"
    assert summary["terminal_checkpoint"] == "lazy_checked"
    assert summary["downstream_model_calls_performed"] == 0
    assert [name for name, _ in calls] == ["cold"] * 4 + ["check"] * 4 + ["refine"] * 4
    assert runner.read(phase / "phase_1_raw_lazy/result.json")["lazy_resolve_count"] == 1
    assert runner.read(phase / "phase_2_v096/summary.json")["state"] == "dry_run_completed"
    manifest = runner.read(phase / "manifest.json")
    assert manifest["device_roles"]["gpu1"]["stages"] == []


def test_real_generic_handoff_to_v290_dry_run(tmp_path, engines, monkeypatch):
    source, phase, calls, summary = prepared_source(tmp_path, engines, monkeypatch)
    _, backend = engines
    result = backend.run_pipeline(
        source_run=source, output_dir=tmp_path / "backend", input_checkpoint="lazy_checked",
        source_problem_id="Example-001", problem_number=1, dry_run=True,
        enable_exact_evidence=False,
    )
    assert result["state"] == "dry_run_completed", result
    assert [row["checkpoint"] for row in result["checkpoints"]] == ["baseline", "R1-C1", "R1-C2"]
    baseline = result["checkpoints"][0]["proofs"]
    refined = next(row for row in baseline if row["candidate_id"] == "t10_r01")
    assert Path(refined["proof_path"]).read_text().strip() == "Refined mock proof."
    manifest = runner.read(tmp_path / "backend/manifest.json")
    assert manifest["problem_id"] == "Example-001"


def test_legacy_default_does_not_silently_accept_new_dataset(tmp_path, engines, monkeypatch):
    source, _, _, _ = prepared_source(tmp_path, engines, monkeypatch)
    with pytest.raises(ValueError, match="selector mismatch"):
        engines[1].configure_source_problem(source, 1)


def test_generic_identity_mismatch_rejected(tmp_path, engines, monkeypatch):
    source, _, _, _ = prepared_source(tmp_path, engines, monkeypatch)
    with pytest.raises(ValueError, match="selector mismatch"):
        engines[1].configure_source_problem(source, 1, expected_problem_id="Different-002")


def test_generic_envelope_number_mismatch_rejected(tmp_path, engines, monkeypatch):
    source, phase, _, _ = prepared_source(tmp_path, engines, monkeypatch)
    path = phase / "input/problem.json"
    runner.write(path, {**runner.read(path), "problem_number": 2})
    with pytest.raises(ValueError, match="envelope/portfolio"):
        engines[1].configure_source_problem(source, 1, expected_problem_id="Example-001")


def test_statement_or_proof_drift_rejected(tmp_path, engines, monkeypatch):
    source, phase, _, _ = prepared_source(tmp_path, engines, monkeypatch)
    _, backend = engines
    backend.configure_source_problem(source, 1, expected_problem_id="Example-001")
    path = phase / "phase_1_raw_lazy/p1/candidates/t10_r01/checked_proof.md"
    path.write_text("Altered proof.", encoding="utf-8")
    with pytest.raises(ValueError, match="proof binding drift"):
        backend._lazy_checked_portfolio(source)


def test_budget_forcing_temperature_policy(engines, tmp_path):
    from experiments.local_math_verifier.runtime import HTTPGenerationConfig
    _, backend = engines
    forcing = backend.v263.parent._budget_forcing
    base = HTTPGenerationConfig(max_tokens=65536, temperature=1.0)
    reduced = forcing.continuation_config(
        output_dir=tmp_path / "cold_generation", stage="cold_draft_attempt1", config=base,
    )
    assert reduced.temperature == 0.7
    assert reduced.max_tokens == 65536
    lazy = forcing.continuation_config(
        output_dir=tmp_path / "lazy_check", stage="lazy_check_attempt1",
        config=HTTPGenerationConfig(max_tokens=16384, temperature=0.1),
    )
    assert lazy.temperature == 0.1
    assert lazy.max_tokens == 32768


def test_dry_run_never_checks_servers_or_calls_models(tmp_path, engines, monkeypatch):
    row = {"problem_id": "Example-001", "problem": "Prove the stated assertion.", "problem_number": 1}
    runner.write(tmp_path / "manifest.json", {
        "schema": runner.SCHEMA, "dry_run": True, "problems": [row],
        "gemma_endpoint": "http://unreachable-gemma.example/v1",
        "qwen_endpoint": "http://unreachable-qwen.example/v1", "seed_namespace": "test",
    })
    runner.write(tmp_path / "inputs/Example-001.json", {key: row[key] for key in ("problem_id", "problem")})
    monkeypatch.setattr(runner, "check_servers", lambda _: pytest.fail("dry run contacted servers"))
    monkeypatch.setattr(engines[0], "run_cold_candidate", lambda **_: pytest.fail("dry run generated proof"))
    monkeypatch.setattr(engines[1], "run_pipeline", lambda **_: pytest.fail("dry run invented backend proofs"))
    result = runner.execute_problem(tmp_path, "Example-001", dry_run=True)
    assert result["model_calls_performed"] == 0
    assert not (tmp_path / "problems/Example-001/02_r1_cycles").exists()


def test_worker_runs_v290_exactly_two_cycles_after_lazy_refinement(tmp_path, engines, monkeypatch):
    frontend, backend = engines
    frontend_calls = mock_frontend_calls(monkeypatch, frontend)
    row = {"problem_id": "Example-001", "problem": "Prove the stated assertion.", "problem_number": 1}
    runner.write(tmp_path / "manifest.json", {
        "schema": runner.SCHEMA, "dry_run": False, "problems": [row],
        "gemma_endpoint": "http://gemma.example/v1", "qwen_endpoint": "http://qwen.example/v1",
        "seed_namespace": "test", "model_timeout_sec": 600,
    })
    runner.write(tmp_path / "inputs/Example-001.json", {key: row[key] for key in ("problem_id", "problem")})
    monkeypatch.setattr(runner, "check_servers", lambda _: None)
    cycle_calls = []

    def cycle(**kwargs):
        assert len(frontend_calls) == 12
        cycle_calls.append((kwargs["cycle"], kwargs["candidate_id"]))
        source = kwargs["source_proof"]
        if kwargs["cycle"] == 1 and kwargs["candidate_id"] == "t10_r01":
            assert Path(source["proof_path"]).read_text().strip() == "Refined mock proof."
        root = kwargs["output_dir"] / "lanes" / kwargs["candidate_id"] / f"cycle{kwargs['cycle']}"
        root.mkdir(parents=True, exist_ok=True)
        path = root / "proof.md"
        text = f"Mock cycle {kwargs['cycle']} proof."
        path.write_text(text + "\n", encoding="utf-8")
        return root, {"candidate_id": kwargs["candidate_id"], "proof_path": str(path),
                      "proof_sha256": backend.sha256_text(text)}

    monkeypatch.setattr(backend, "run_r1_cycle_lane", cycle)
    result = runner.execute_problem(tmp_path, "Example-001", dry_run=False)
    assert result["state"] == "completed", result
    assert result["terminal_checkpoint"] == "R1-C2"
    assert result["completed_lane_count"] == 4
    assert [cycle for cycle, _ in cycle_calls] == [1] * 4 + [2] * 4
    assert result["checkpoints"][-1]["checkpoint"] == "R1-C2"
    assert all(Path(lane["current_proof"]["proof_path"]).read_text().strip() == "Mock cycle 2 proof."
               for lane in result["lanes"].values())
    assert not list(tmp_path.rglob("*cycle3*"))
    targets = runner.read(tmp_path / "problems/Example-001/02_r1_cycles/score_targets.json")
    assert [row["checkpoint"] for row in targets["checkpoints"]] == ["baseline", "R1-C1", "R1-C2"]
    # Resuming the completed problem must return the same proof without model calls.
    monkeypatch.setattr(backend, "run_r1_cycle_lane", lambda **_: pytest.fail("completed worker resumed inference"))
    assert runner.execute_problem(tmp_path, "Example-001", dry_run=False) == result
    policy = runner.read(tmp_path / "problems/Example-001/execution_policy.json")
    assert policy["qwen_max_output_tokens"] == 49152
    assert policy["qwen_retry_on_output_cap"] is True
    assert policy['limit_recovery']['models'] == ['gemma', 'qwen']
    assert policy['limit_recovery']['recovery_max_tokens'] == 65536
    assert policy['limit_recovery']['recovery_timeout_seconds'] == 450
    assert policy['limit_recovery']['recovery_hits_either_limit'] == 'fail_closed_without_retry_or_fallback' 
    assert policy["qwen_mandatory_budget_forcing"] is True


def test_resume_rejects_changed_input_snapshot(tmp_path):
    inputs = tmp_path / "input"
    problem(inputs)
    output = tmp_path / "out"
    args = Namespace(problem_dir=inputs, problem_id=None, limit=None, output_dir=output,
                     gemma_endpoint="http://gemma/v1", qwen_endpoint="http://qwen/v1",
                     seed_namespace="test", model_timeout_sec=600, dry_run=True, resume=False)
    runner.freeze_queue(args)
    args.resume = True
    runner.freeze_queue(args)
    path = output / "inputs/Example-001.json"
    runner.write(path, {**runner.read(path), "problem": "Altered statement."})
    with pytest.raises(ValueError, match="snapshot changed"):
        runner.freeze_queue(args)


def test_worker_lock_prevents_duplicate_inference(tmp_path):
    root = tmp_path / "problems/Example-001"
    root.mkdir(parents=True)
    with (root / "worker.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            runner.execute_problem(tmp_path, "Example-001", dry_run=False)


def exhausted_portfolio(root, problem_id="Example-001"):
    lanes = {}
    for candidate in ("t10_r01", "t10_r02", "t07_r01", "t07_r02"):
        proof = root / "proofs" / f"{candidate}.md"
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text("Saved proof.\n")
        bound = {"proof_path": str(proof), "proof_sha256": runner.hashlib.sha256(b"Saved proof.").hexdigest()}
        lanes[candidate] = {"state": "failed_closed", "current_proof": bound, "checkpoints": [bound]}
        runner.write(root / "02_r1_cycles/lanes" / candidate / "failure.json", {"state": "failed_closed"})
    summary = {"problem_id": problem_id, "state": "failed_closed", "completed_lane_count": 0,
               "failed_lane_count": 4, "lanes": lanes}
    runner.write(root / "summary.json", summary)
    return summary


@pytest.mark.parametrize("damage", ["proof", "outside", "live_lane", "count", "empty"])
def test_failed_skip_rejects_unbound_or_live_portfolio(tmp_path, damage):
    root = tmp_path / "problem"
    summary = exhausted_portfolio(root)
    lane = summary["lanes"]["t10_r01"]
    if damage == "proof":
        Path(lane["current_proof"]["proof_path"]).write_text("Changed proof.")
    elif damage == "outside":
        outside = tmp_path / "outside.md"
        outside.write_text("Saved proof.\n")
        lane["current_proof"]["proof_path"] = str(outside)
    elif damage == "live_lane":
        lane["state"] = "running"
    elif damage == "count":
        summary["failed_lane_count"] = 3
    else:
        Path(lane["current_proof"]["proof_path"]).write_text("")
        lane["current_proof"]["proof_sha256"] = runner.hashlib.sha256(b"").hexdigest()
    runner.write(root / "summary.json", summary)
    with pytest.raises(ValueError):
        runner.validate_failed_portfolio(root, "Example-001")


def test_explicit_failed_skip_preserves_proofs_and_still_pauses_on_next_failure(tmp_path, monkeypatch):
    root = tmp_path / "problems/Example-001"
    exhausted_portfolio(root)
    saved = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    manifest = {"problems": [{"problem_id": "Example-001"}, {"problem_id": "Example-002"}]}
    monkeypatch.setattr(runner, "freeze_queue", lambda _: manifest)
    launched = []

    class Child:
        def __init__(self, command, **kwargs):
            launched.append(command[command.index("--_worker") + 1])

        def wait(self, timeout):
            return 1

    monkeypatch.setattr(runner.subprocess, "Popen", Child)
    args = Namespace(output_dir=tmp_path, resume=True, dry_run=False, skip_failed_problem=["Example-001"])
    assert runner.run_queue(args) == 1
    assert launched == ["Example-002"]
    assert runner.read(tmp_path / "status.json")["state"] == "paused_on_failure"
    assert all(p.read_bytes() == content for p, content in saved.items())


@pytest.mark.parametrize("failed_stage", ["cold", "check", "refine"])
def test_frontend_failure_continues_survivors_without_promoting_failed_proof(tmp_path, engines, monkeypatch, failed_stage):
    from experiments.local_math_verifier import frontend_portfolio
    frontend, backend = engines
    calls = mock_frontend_calls(monkeypatch, frontend)
    old_cold, old_check, old_refine = frontend.run_cold_candidate, frontend.run_lazy_check, frontend.run_lazy_resolve
    failed = "t10_r02"

    def cold(**kw):
        if failed_stage == "cold" and kw["spec"]["candidate_id"] == failed:
            raise RuntimeError("synthetic raw failure")
        row = old_cold(**kw)
        path = kw["output_dir"] / f"p{row['problem_number']}/candidates" / row["candidate_id"] / "draft_proof.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(row["proof"] + "\n")
        return {**row, "proof_path": str(path.resolve()), "proof_sha256": frontend.sha256_text(row["proof"])}

    def check(**kw):
        if failed_stage == "check" and kw["row"]["candidate_id"] == failed:
            raise RuntimeError("synthetic checker failure")
        return old_check(**kw)

    def refine(**kw):
        if failed_stage == "refine" and kw["row"]["candidate_id"] == failed:
            raise RuntimeError("synthetic expansion failure")
        return old_refine(**kw)

    monkeypatch.setattr(frontend, "run_cold_candidate", cold)
    monkeypatch.setattr(frontend, "run_lazy_check", check)
    monkeypatch.setattr(frontend, "run_lazy_resolve", refine)
    source = tmp_path / "source"
    phase = source / "p1/01_raw_lazy_enhanced_resolve"
    args = dict(problem_file=problem(tmp_path / "inputs"), output_dir=phase, problem_number=1,
                gpu0_gemma_endpoint="http://gemma.example/v1", gpu1_qwen_endpoint="http://qwen.example/v1",
                seed_namespace="test", stop_after_lazy=True, continue_failed_lanes=True)
    summary = frontend.run(**args)
    assert summary["state"] == "completed_with_failed_lanes"
    assert summary["completed_lane_count"] == 3
    assert not (phase / f"phase_1_raw_lazy/p1/candidates/{failed}/checked_proof.md").exists()
    first = frontend_portfolio.load(phase, 1, "Example-001")
    failed_row = next(r for r in first["proofs"] if r["candidate_id"] == failed)
    assert failed_row["checkpoint"] == ("no_proof" if failed_stage == "cold" else "raw_draft")
    before = len([r for r in calls if r[1] == failed])
    frontend.run(**args)
    assert len([r for r in calls if r[1] == failed]) == before
    cycle_calls = []

    def cycle(**kw):
        assert kw["candidate_id"] != failed
        cycle_calls.append((kw["cycle"], kw["candidate_id"]))
        return kw["output_dir"] / "mock_cycle", kw["source_proof"]

    monkeypatch.setattr(backend, "run_r1_cycle_lane", cycle)
    result = backend.run_pipeline(source_run=source, output_dir=tmp_path / "backend",
        input_checkpoint="lazy_checked", source_problem_id="Example-001", problem_number=1,
        authorize_model_calls=True, enable_exact_evidence=False)
    assert result["state"] == "completed_with_failed_lanes", result
    assert len(cycle_calls) == 6
    assert [c for c, _ in cycle_calls] == [1] * 3 + [2] * 3
    lane = result["lanes"][failed]
    assert lane["state"] == "failed_closed"
    if failed_stage == "cold":
        assert lane["current_proof"] is None and lane["checkpoints"] == []
    else:
        assert lane["checkpoints"][-1]["checkpoint"] == "raw_draft"
        assert Path(lane["current_proof"]["proof_path"]).read_text().strip() == "Original mock proof."
        Path(failed_row["source_proof_path"]).write_text("tampered")
        with pytest.raises(ValueError, match="proof binding drift"):
            frontend_portfolio.load(phase, 1, "Example-001")


def test_fresh_attempt_offset_changes_real_raw_call_seeds_only(tmp_path, engines):
    frontend, _ = engines
    captures = []
    class Runtime:
        def gemma_call(self, **kwargs):
            kwargs['output_dir'].mkdir(parents=True, exist_ok=True)
            captures.append({k:v for k,v in kwargs.items() if k not in {'output_dir','parser'}})
            return {'text':'Synthetic proof.'}
    original = tuple(dict(s) for s in frontend.RAW_CANDIDATES)
    for offset in (0, 1000003):
        spec = frontend.raw_candidate_specs(offset)[0]
        frontend.run_cold_candidate(runtime=Runtime(), problem={'problem_number':1,'problem_id':'Example-001'},
            output_dir=tmp_path/str(offset), system_prompt='Generic system prompt.', user_prompt='Generic statement.', spec=spec)
    assert captures[0]['seed'] != captures[1]['seed']
    assert {k:v for k,v in captures[0].items() if k!='seed'} == {k:v for k,v in captures[1].items() if k!='seed'}
    assert tuple(frontend.RAW_CANDIDATES) == original
    assert frontend.raw_candidate_specs() == original


def test_raw_seed_offset_is_frozen_for_resume(tmp_path):
    inputs=tmp_path/'inputs'
    problem(inputs)
    output=tmp_path/'out'
    args=Namespace(problem_dir=inputs,problem_id=None,limit=None,output_dir=output,
        gemma_endpoint='http://gemma/v1',qwen_endpoint='http://qwen/v1',seed_namespace='fresh',
        model_timeout_sec=600,dry_run=True,resume=False,raw_seed_offset=1000003)
    runner.freeze_queue(args)
    args.resume=True
    runner.freeze_queue(args)
    from scripts.relaunch_v263_v290 import resume_args
    manifest=runner.read(output/'manifest.json')
    assert manifest['raw_seed_offset']==1000003
    args.raw_seed_offset=0
    with pytest.raises(ValueError,match='frozen inputs'):
        runner.freeze_queue(args)


def test_backend_rejects_resume_after_omitted_cycle(tmp_path, engines):
    with pytest.raises(ValueError, match="completed R1 cycle"):
        engines[1].run_pipeline(source_run=tmp_path / "source", output_dir=tmp_path / "out",
                               resume_after_cycle=3, dry_run=True)


@pytest.mark.parametrize("resume_cycle", [1, 2])
def test_backend_resume_never_runs_omitted_cycle(tmp_path, engines, monkeypatch, resume_cycle):
    source, _, _, _ = prepared_source(tmp_path, engines, monkeypatch)
    backend = engines[1]
    output = tmp_path / "backend"
    args = dict(source_run=source, output_dir=output, input_checkpoint="lazy_checked",
                source_problem_id="Example-001", problem_number=1, enable_exact_evidence=False)
    backend.run_pipeline(**args, dry_run=True)
    manifest = runner.read(output / "manifest.json")
    proofs = {row["candidate_id"]: row for row in manifest["frozen_inputs"]["lanes"]}
    for candidate in backend.CANDIDATE_IDS:
        for cycle in range(1, resume_cycle + 1):
            runner.write(output / "lanes" / candidate / f"{cycle:02d}_r1_cycle_{cycle}" / "summary.json",
                         {"state": "completed"})
    def saved(**kwargs):
        return [proofs[kwargs["expected_candidates"][0]]]
    calls = []
    def new_cycle(**kwargs):
        calls.append(kwargs["cycle"])
        return output / "mock_cycle", kwargs["source_proof"]
    monkeypatch.setattr(backend, "_terminal_r1_proofs", saved)
    monkeypatch.setattr(backend, "run_r1_cycle_lane", new_cycle)
    result = backend.run_pipeline(**args, resume_after_cycle=resume_cycle, authorize_model_calls=True)
    assert result["state"] == "completed", result
    assert result["terminal_checkpoint"] == "R1-C2"
    assert calls == ([2] * 4 if resume_cycle == 1 else [])
    assert not list(output.rglob("*cycle_3*"))


def test_resume_rejects_different_terminal_policy(tmp_path, engines, monkeypatch):
    source, _, _, _ = prepared_source(tmp_path, engines, monkeypatch)
    backend = engines[1]
    args = dict(source_run=source, output_dir=tmp_path / "backend", input_checkpoint="lazy_checked",
                source_problem_id="Example-001", problem_number=1, enable_exact_evidence=False)
    backend.run_pipeline(**args, dry_run=True)
    path = args["output_dir"] / "manifest.json"
    manifest = runner.read(path)
    manifest["pipeline_policy"] = "r1_three_cycles_terminal_v1"
    runner.write(path, manifest)
    with pytest.raises(ValueError, match="frozen configuration: pipeline_policy"):
        backend.run_pipeline(**args, dry_run=True, resume_after_cycle=1)
