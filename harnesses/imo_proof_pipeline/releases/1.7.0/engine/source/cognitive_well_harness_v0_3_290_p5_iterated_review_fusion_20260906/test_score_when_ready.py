from pathlib import Path

import pytest

from . import pipeline, score_when_ready as watcher


def test_unfinished_proof_is_not_submitted(tmp_path, monkeypatch):
    stage = watcher.stage_directory(tmp_path, "lane_a", "R1-C1")
    pipeline.write_json(stage / "summary.json", {"state": "running"})
    def forbidden(**kwargs):
        raise AssertionError("unfinished stage must not be validated/scored")
    monkeypatch.setattr(pipeline, "_terminal_r1_proofs", forbidden)
    assert watcher.ready_proof(tmp_path, "lane_a", "R1-C1", {}, {}) is None


def test_completed_lane_does_not_wait_for_other_lanes(tmp_path, monkeypatch):
    stage = watcher.stage_directory(tmp_path, "lane_a", "R1-C2")
    pipeline.write_json(stage / "summary.json", {"state": "completed"})
    proof = {"candidate_id": "lane_a", "proof_path": "/bound/proof.md", "proof_sha256": "hash"}
    def validate(**kwargs):
        assert kwargs["stage_dir"] == stage
        assert kwargs["expected_candidates"] == ("lane_a",)
        assert kwargs["allowed_root"] == tmp_path
        return [proof]
    monkeypatch.setattr(pipeline, "_terminal_r1_proofs", validate)
    assert watcher.ready_proof(
        tmp_path, "lane_a", "R1-C2", {"runtime": {"model_timeout_sec": 600}}, {}
    ) == proof


def test_only_one_proof_is_passed_to_skill_launcher():
    command = watcher.scoring_command(
        launcher=Path("/strict-skill/score.py"), proof=Path("/snapshot/proof.md"),
        output=Path("/scores/new"), problem_id="imo2026_p5", candidate="lane_a",
    )
    assert command[1] == "/strict-skill/score.py"
    assert command.count("--proof-task") == 1
    assert command[command.index("--proof-task") + 1] == "imo2026_p5:lane_a=/snapshot/proof.md"
    assert "--source-run" not in command
    assert "--policy-mode" not in command  # The strict skill, not the watcher, sets policy.


@pytest.mark.parametrize("checkpoint", ["R2", "R3"])
def test_new_run_cannot_score_removed_checkpoints(tmp_path, checkpoint):
    manifest = {"stage_order": list(pipeline.STAGE_ORDER)}
    with pytest.raises(ValueError, match="not scheduled"):
        watcher.ready_proof(tmp_path, "lane_a", checkpoint, manifest, {})


@pytest.mark.parametrize("checkpoint", ["R1-C0", "R1-C4", "invalid"])
def test_invalid_cycle_is_rejected(tmp_path, checkpoint):
    with pytest.raises(ValueError, match="unsupported checkpoint"):
        watcher.stage_directory(tmp_path, "lane_a", checkpoint)


def test_historical_scoring_is_read_only_and_manifest_bound(tmp_path, monkeypatch):
    manifest = {"stage_order": [*pipeline.STAGE_ORDER, "R2"],
                "runtime": {"model_timeout_sec": 600, "seed_namespace": "old"}}
    proof = {"candidate_id": "lane_a", "proof_path": "/bound/old.md", "proof_sha256": "hash"}
    stage = watcher.stage_directory(tmp_path, "lane_a", "R2")
    pipeline.write_json(stage / "summary.json", {"state": "completed"})
    monkeypatch.setattr(pipeline, "_second_checkpoint", lambda *args, **kw: {"proofs": [proof]})
    assert watcher.ready_proof(tmp_path, "lane_a", "R2", manifest, {("lane_a", "R1-C3"): proof}) == proof
