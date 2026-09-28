import pytest

from . import pipeline as p
from . import recover_review_lane as recovery


def fixture(tmp_path):
    root = tmp_path / "run"
    p.run_pipeline(output_dir=root, input_checkpoint="lazy_checked", dry_run=True)
    candidate = p.CANDIDATE_IDS[-1]
    lane = root / "lanes" / candidate
    p.write_json(root / "status.json", {"state": "running", "stage": "R1-C2",
                                           "active_lanes": list(p.CANDIDATE_IDS[:-1])})
    p.write_json(lane / "failure.json", {
        "state": "failed_closed", "stage": "R1-C1",
        "error": "RuntimeError: fresh_reviewer_2 failures: TimeoutError: timed out",
    })
    p.write_json(lane / "01_r1_cycle_1/status.json", {"stage": "fresh_reviews"})
    return root, candidate


def test_review_lane_recovery_uses_same_cycles_without_other_lane_or_root_writes(tmp_path, monkeypatch):
    root, candidate = fixture(tmp_path)
    before = (root / "status.json").read_bytes()
    other = root / "lanes" / p.CANDIDATE_IDS[0] / "untouched.json"
    p.write_json(other, {"keep": True})
    seen = []
    def same_cycle(**kwargs):
        assert kwargs["candidate_id"] == candidate
        assert kwargs["output_dir"] == root
        assert p._boundary_config()["enable_exact_evidence"] is False
        seen.append(kwargs["cycle"])
        return root / "unused", kwargs["source_proof"]
    monkeypatch.setattr(p, "run_r1_cycle_lane", same_cycle)
    recovery.recover(root=root, candidate=candidate)
    assert seen == [1, 2, 3]
    assert (root / "status.json").read_bytes() == before
    assert p.read_object(other) == {"keep": True}
    journal = root / "lanes" / candidate / "mechanical_review_recovery"
    assert (journal / "failure.json").is_file()
    assert p.read_object(journal / "status.json")["state"] == "completed"


def test_review_lane_recovery_refuses_model_gate_rejection(tmp_path):
    root, candidate = fixture(tmp_path)
    p.write_json(root / "lanes" / candidate / "failure.json", {
        "state": "failed_closed", "stage": "R1-C1", "error": "RepairBriefCertificationError: rejected",
    })
    with pytest.raises(ValueError, match="recorded Reviewer2 timeout"):
        recovery.recovery_inputs(root, candidate)
