from pathlib import Path

import pytest

from . import pipeline
from .resume_at_cycle_boundary import cycle_settled


@pytest.mark.parametrize("failed_lane", [False, True])
def test_resume_keeps_completed_proofs_and_disables_optional_calls(tmp_path, monkeypatch, failed_lane):
    root = tmp_path / "run"
    pipeline.run_pipeline(output_dir=root, dry_run=True, input_checkpoint="lazy_checked")
    manifest_bytes = (root / "manifest.json").read_bytes()
    manifest = pipeline.read_object(root / "manifest.json")
    proofs = {row["candidate_id"]: row for row in manifest["frozen_inputs"]["lanes"]}
    failed_id = pipeline.CANDIDATE_IDS[0] if failed_lane else None
    for candidate in pipeline.CANDIDATE_IDS:
        lane = root / "lanes" / candidate
        if candidate == failed_id:
            pipeline.write_json(lane / "failure.json", {
                "state": "failed_closed", "stage": "R1-C1", "error": "existing gate rejection",
            })
        else:
            pipeline.write_json(lane / "01_r1_cycle_1/summary.json", {"state": "completed"})
    checked, new_cycles = [], []
    def saved_terminal(**kwargs):
        candidate, = kwargs["expected_candidates"]
        assert kwargs["stage_dir"].name == "01_r1_cycle_1"
        checked.append(candidate)
        return [proofs[candidate]]
    def new_cycle(**kwargs):
        assert kwargs["output_dir"].name == "02_r1_cycle_2"
        assert pipeline._boundary_config()["enable_exact_evidence"] is False
        case, = pipeline.read_object(kwargs["cases_manifest"])["cases"]
        assert case["source_proof_sha256"] == proofs[case["candidate_id"]]["proof_sha256"]
        new_cycles.append(case["candidate_id"])
        raise RuntimeError("test stops before any model call")
    monkeypatch.setattr(pipeline, "_terminal_r1_proofs", saved_terminal)
    monkeypatch.setattr(pipeline.stage, "run", new_cycle)
    pipeline.run_pipeline(
        output_dir=root, input_checkpoint="lazy_checked", resume_after_cycle=1,
        enable_exact_evidence=False, authorize_model_calls=True,
    )
    expected = set(pipeline.CANDIDATE_IDS) - ({failed_id} if failed_id else set())
    assert set(checked) == set(new_cycles) == expected
    assert (root / "manifest.json").read_bytes() == manifest_bytes
    resumed = pipeline.read_object(root / "resume_after_cycle_1.json")
    assert resumed["repair_brief_boundary"]["optional_exact_evidence"]["enabled_for_every_repair_brief_audit"] is False


def test_disabled_boundary_does_not_change_required_gate(monkeypatch, tmp_path):
    seen = {}
    def gate(**kwargs):
        seen.update(kwargs)
        return {"state": "gate_called"}
    monkeypatch.setattr(pipeline.repair_boundary, "audit_fusion_before_resolver", gate)
    with pipeline.mandatory_repair_boundary(
        qwen_endpoint="http://qwen", gemma_endpoint="http://gemma", cycle_key="R1-C2",
        model_timeout_sec=600, enable_exact_evidence=False,
    ):
        result = pipeline._fusion_wrapper(lambda **kwargs: {"fusion": "unchanged"},
                                          output_dir=tmp_path, task={})
    assert result == {"state": "gate_called"}
    assert seen["enable_exact_evidence"] is False
    assert seen["source_result"] == {"fusion": "unchanged"}


def test_cycle_boundary_waits_for_every_lane_and_accepts_recorded_failure(tmp_path):
    candidates = ["a", "b"]
    pipeline.write_json(tmp_path / "lanes/a/01_r1_cycle_1/summary.json", {"state": "completed"})
    assert not cycle_settled(tmp_path, candidates, 1)
    pipeline.write_json(tmp_path / "lanes/b/failure.json", {"state": "failed_closed", "stage": "R1-C1"})
    assert cycle_settled(tmp_path, candidates, 1)
