"""Gold-free recovery preparation on synthetic submitted inputs only."""
import subprocess
import sys
from pathlib import Path

import pytest

from . import pipeline as p, resume_rejected_synthesis as recovery


def inputs(tmp_path):
    problem, proof = tmp_path / "problem.json", tmp_path / "proof.md"
    claim, body = "If x=0, prove x*x=0.", "Multiplying x=0 by x gives the conclusion."
    p.write_json(problem, {"claim": claim, "problem_id": "synthetic"})
    proof.write_text(body)
    return problem, proof, {"problem_sha256": p.sha256_text(claim), "proof_sha256": p.sha256_text(body)}


def test_recovery_import_does_not_require_scorer():
    program = '''import sys, importlib.abc
blocked = "scripts.run_v097_p145_gold_informed_calibrated_codex_scores_20260827"
class NoScorer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == blocked:
            raise AssertionError("generation imported scorer")
sys.meta_path.insert(0, NoScorer())
from cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 import resume_rejected_synthesis
assert blocked not in sys.modules
'''
    result = subprocess.run([sys.executable, "-B", "-c", program], cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("mutation", [None, "problem", "proof"])
def test_binding_reads_only_submitted_inputs(tmp_path, monkeypatch, mutation):
    problem, proof, binding = inputs(tmp_path)
    if mutation == "problem":
        p.write_json(problem, {"claim": "A changed theorem."})
    elif mutation == "proof":
        proof.write_text("A changed proof.")
    original = Path.read_text
    seen = []
    def read(path, *a, **kw):
        assert path in {problem, proof}, "reference or unrelated input opened"
        seen.append(path)
        return original(path, *a, **kw)
    monkeypatch.setattr(Path, "read_text", read)
    if mutation:
        with pytest.raises(ValueError, match="binding mismatch"):
            recovery.verify_generation_inputs(problem, proof, binding)
    else:
        recovery.verify_generation_inputs(problem, proof, binding)
    assert set(seen) == {problem, proof}


def test_prepare_source_uses_bound_inputs_without_gold_loader(tmp_path, monkeypatch):
    root, output = tmp_path / "source", tmp_path / "recovery"
    root.mkdir()
    problem, proof, binding = inputs(root)
    candidates = ("sample_a", "sample_b", "sample_c", "sample_d")
    stage = root / "lanes/sample_a/01_r1_cycle_1"
    case = stage / "cases/synthetic.sample_a"
    spec = {**binding, "problem_id": "synthetic", "candidate_id": "sample_a", "problem_number": 1,
            "case_id": "synthetic.sample_a", "problem_path": str(problem), "proof_path": str(proof)}
    p.write_json(root / "manifest.json", {"problem_id": "synthetic", "problem_number": 1,
        "candidate_ids": candidates, "frozen_inputs": {"problem_text_sha256": binding["problem_sha256"]},
        "runtime": {"model_timeout_sec": 600}})
    p.write_json(stage / "manifest.json", {"cases": [spec], "seed_namespace": "synthetic"})
    p.write_json(case / "fusion_repair_brief_audit_rewrite/result.json", {
        "state": "failed_closed", "certified_round": None, "cycle_key": "R1-C1"})
    p.write_json(case / "fusion/producer/result.json", {"task": {}})
    monkeypatch.setattr(p, "configure_problem_binding", lambda **kw: None)
    monkeypatch.setattr(p, "_reconstruct_gate_task", lambda **kw: {})
    monkeypatch.setattr(recovery.boundary, "reuse_rejected_brief", lambda **kw: {})
    monkeypatch.setattr(p.stage, "build_resolver_task", lambda **kw: {
        "problem_path": kw["case"]["problem_path"], "proof_path": kw["case"]["proof_path"],
        "fusion_decision_gate": {"state": "REJECTED"}})
    monkeypatch.setattr(p, "bind_effective_fusion_task", lambda task, **kw: task)
    monkeypatch.setattr(p.stage.resolver, "public_task", lambda task: task)
    jobs = recovery.prepare_source(root, output)
    assert len(jobs) == 1 and jobs[0]["generation_reference_reads"] is False
    assert jobs[0]["problem_sha256"] == binding["problem_sha256"]
    # A post-preflight mutation is rejected before a synthesis model can run.
    staged = Path(jobs[0]["task"]["proof_path"])
    staged.write_text("Changed after preparation.")
    monkeypatch.setattr(p.stage.resolver, "run_task", lambda **kw: pytest.fail("model called on changed inputs"))
    with pytest.raises(ValueError, match="binding mismatch"):
        recovery.synthesize(jobs[0], output)
