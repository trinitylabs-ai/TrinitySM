from pathlib import Path

import pytest

from . import pipeline


def test_explicit_source_root_accepts_shared_input_but_keeps_default_boundary(tmp_path, monkeypatch):
    root = tmp_path / "experiment"
    stage = root / "lanes/candidate/cycle"
    problem = root / "input/problem.json"
    ancestor = root / "input/proof.md"
    spec = {"case_id": "generic.candidate", "problem_path": str(problem),
            "proof_path": str(ancestor)}
    reached = []
    def stop_before_artifact_loading(path):
        reached.append(path)
        raise RuntimeError("test reached contained inputs")
    monkeypatch.setattr(pipeline.v108.v098, "load_json", stop_before_artifact_loading)
    with pytest.raises(ValueError, match="escapes"):
        pipeline.v108.v098.load_case(stage, spec, {})
    with pytest.raises(RuntimeError, match="contained inputs"):
        pipeline.v108.v098.load_case(stage, spec, {}, source_root=root)
    assert reached == [problem]
    spec["problem_path"] = str(tmp_path / "outside.json")
    with pytest.raises(ValueError, match="escapes"):
        pipeline.v108.v098.load_case(stage, spec, {}, source_root=root)


def test_explicit_source_root_rejects_external_stage(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        pipeline.v108.v098.load_case(tmp_path / "outside", {}, {}, source_root=tmp_path / "run")


@pytest.mark.parametrize("rejected_cycle", [None, 1, 2, 3])
def test_resume_after_cycle3_only_reconciles_r1_proofs(tmp_path, monkeypatch, rejected_cycle):
    root = tmp_path / "run"
    pipeline.run_pipeline(output_dir=root, dry_run=True, input_checkpoint="lazy_checked")
    manifest_bytes = (root / "manifest.json").read_bytes()
    proofs = {r["candidate_id"]: r for r in pipeline.read_object(root / "manifest.json")["frozen_inputs"]["lanes"]}
    rejected = pipeline.CANDIDATE_IDS[0] if rejected_cycle else None
    pipeline.write_json(root / "resume_after_cycle_3.json", {"prior": True})
    pipeline.write_json(root / "mechanical_resume_after_cycle_3/preserved.json", {"prior": True})
    for candidate in pipeline.CANDIDATE_IDS:
        lane = root / "lanes" / candidate
        for cycle in range(1, 4):
            if candidate != rejected or cycle < rejected_cycle:
                pipeline.write_json(lane / f"{cycle:02d}_r1_cycle_{cycle}/summary.json", {"state": "completed"})
        if candidate == rejected:
            pipeline.write_json(lane / "failure.json", {
                "state": "failed_closed", "stage": f"R1-C{rejected_cycle}",
                "error": "model gate rejection",
            })
    checked = []
    def terminal(**kwargs):
        candidate, = kwargs["expected_candidates"]
        checked.append((candidate, kwargs["stage_dir"].name))
        return [proofs[candidate]]
    def forbidden(**kwargs):
        raise AssertionError("completed C3 resume must not run any model stage")
    monkeypatch.setattr(pipeline, "_terminal_r1_proofs", terminal)
    monkeypatch.setattr(pipeline.stage, "run", forbidden)
    monkeypatch.setattr(pipeline.v108.v098, "run", forbidden)
    monkeypatch.setattr(pipeline.v108, "run_direct_ungrouped_resolve", forbidden)
    monkeypatch.setattr(pipeline.v108.v105, "run", forbidden)
    result = pipeline.run_pipeline(
        output_dir=root, input_checkpoint="lazy_checked", resume_after_cycle=3,
        enable_exact_evidence=False, authorize_model_calls=True,
    )
    assert len(checked) == (12 if rejected is None else 9 + rejected_cycle - 1)
    assert result["state"] == ("completed" if rejected is None else "completed_with_failed_lanes")
    assert result["completed_lane_count"] == (4 if rejected is None else 3)
    assert [row["checkpoint"] for row in result["checkpoints"]] == ["baseline", *pipeline.STAGE_ORDER]
    assert (root / "manifest.json").read_bytes() == manifest_bytes
    assert pipeline.read_object(root / "resume_after_cycle_3.json") == {"prior": True}
    assert pipeline.read_object(root / "resume_after_cycle_3_attempt_02.json")["terminal_checkpoint"] == "R1-C3"
    assert (root / "mechanical_resume_after_cycle_3_attempt_02").is_dir()
    if rejected:
        assert pipeline.read_object(root / "lanes" / rejected / "failure.json")["error"] == "model gate rejection"
    for candidate, lane in result["lanes"].items():
        if candidate != rejected:
            assert lane["current_proof"] == proofs[candidate]
            assert pipeline.read_object(root / "lanes" / candidate / "status.json")["stage"] == "R1-C3"


@pytest.mark.parametrize("historical_stage", ["04_post_r1_cycle3_audit_ledger", "05_resolver2", "06_resolver3"])
def test_historical_downstream_artifacts_are_never_overwritten(tmp_path, historical_stage):
    root = tmp_path / "run"
    pipeline.run_pipeline(output_dir=root, dry_run=True, input_checkpoint="lazy_checked")
    candidate = pipeline.CANDIDATE_IDS[0]
    artifact = root / "lanes" / candidate / historical_stage / "summary.json"
    pipeline.write_json(artifact, {"state": "completed", "historical": True})
    before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="historical downstream work is read-only"):
        pipeline.run_pipeline(
            output_dir=root, input_checkpoint="lazy_checked", resume_after_cycle=3,
            authorize_model_calls=True,
        )
    after = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
    assert after == before
