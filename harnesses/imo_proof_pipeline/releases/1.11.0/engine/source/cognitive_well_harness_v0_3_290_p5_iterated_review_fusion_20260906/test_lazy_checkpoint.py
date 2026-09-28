from pathlib import Path

import pytest

from . import pipeline


def test_lazy_checked_dry_run_binds_all_four_saved_proofs(tmp_path: Path) -> None:
    output_dir = tmp_path / "lazy_dry"
    result = pipeline.run_pipeline(
        output_dir=output_dir, input_checkpoint="lazy_checked", dry_run=True
    )
    assert result["state"] == "dry_run_completed"
    assert result["model_calls_performed"] == 0
    manifest = pipeline.read_object(output_dir / "manifest.json")
    assert manifest["input_checkpoint"] == "lazy_checked"
    assert manifest["repair_brief_boundary"]["mandatory_every_r1_cycle"]
    lanes = manifest["frozen_inputs"]["lanes"]
    assert [row["candidate_id"] for row in lanes] == list(pipeline.CANDIDATE_IDS)
    for row in lanes:
        source = Path(row["source_proof_path"])
        assert source.name == "checked_proof.md"
        staged = Path(row["proof_path"])
        assert staged.parent.name == "lazy_checked_baseline"
        assert staged.read_bytes() == source.read_bytes()
        assert row["proof_sha256"] == row["source_proof_sha256"]
    cases_path = pipeline._case_manifest(
        problem_path=Path(manifest["frozen_inputs"]["problem_path"]),
        proofs=lanes, destination=tmp_path / "cycle1.json", cycle=1,
    )
    assert [row["source_proof_sha256"] for row in pipeline.read_object(cases_path)["cases"]] == [
        row["proof_sha256"] for row in lanes
    ]


@pytest.mark.parametrize("drift", ["proof_hash", "duplicate_lane"])
def test_lazy_checked_rejects_source_binding_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, drift: str
) -> None:
    original_read = pipeline.read_object

    def read_with_drift(path: Path) -> dict:
        value = original_read(path)
        if path.name == "manifest.json" and path.parent.name == "phase_2_v096":
            if drift == "proof_hash":
                value["cases"][0]["proof_sha256"] = "0" * 64
            else:
                value["cases"][1] = dict(value["cases"][0])
        return value

    monkeypatch.setattr(pipeline, "read_object", read_with_drift)
    result = pipeline.run_pipeline(
        output_dir=tmp_path / "bad", input_checkpoint="lazy_checked", dry_run=True
    )
    assert result["state"] == "failed_closed"
    assert result["stage"] == "input_binding"
