from pathlib import Path

import pytest

from . import pipeline
from scripts import run_v097_p145_gold_informed_calibrated_codex_scores_20260827 as scorer


@pytest.mark.parametrize("number", [1, 2, 3, 4, 6])
def test_remaining_problem_saved_inputs_and_gold_bind_without_model_calls(tmp_path, number):
    try:
        root = tmp_path / f"p{number}"
        result = pipeline.run_pipeline(
            output_dir=root, input_checkpoint="lazy_checked", problem_number=number,
            enable_exact_evidence=False, dry_run=True,
        )
        assert result["state"] == "dry_run_completed", result
        assert result["model_calls_performed"] == 0
        manifest = pipeline.read_object(root / "manifest.json")
        assert manifest["problem_id"] == f"imo2026_p{number}"
        assert manifest["problem_number"] == number
        assert manifest["repair_brief_boundary"]["optional_exact_evidence"]["enabled_for_every_repair_brief_audit"] is False
        lanes = manifest["frozen_inputs"]["lanes"]
        tasks = scorer.explicit_proof_tasks(
            [(manifest["problem_id"], row["candidate_id"], Path(row["proof_path"])) for row in lanes],
            problem_root=scorer.PROBLEM_ROOT, reference_root=scorer.REFERENCE_ROOT,
        )
        assert len(tasks) == 4
        for task, lane in zip(tasks, lanes):
            assert task["reference"].strip()
            assert pipeline.sha256_text(task["problem"]) == manifest["frozen_inputs"]["problem_text_sha256"]
            assert task["proof_sha256"] == lane["proof_sha256"]
            assert Path(lane["source_proof_path"]).name == "checked_proof.md"
        cases = pipeline._case_manifest(
            problem_path=Path(manifest["frozen_inputs"]["problem_path"]), proofs=lanes,
            destination=root / "cycle1_cases.json", cycle=1,
        )
        assert all(row["problem_id"] == f"imo2026_p{number}" for row in pipeline.read_object(cases)["cases"])
    finally:
        pipeline.configure_problem_binding(
            problem_id=pipeline.v264.PROBLEM_ID, problem_number=5,
            problem_sha256=pipeline.v264.EXPECTED_PROBLEM_SHA256,
            candidate_ids=pipeline.v264.CANDIDATE_IDS,
        )
