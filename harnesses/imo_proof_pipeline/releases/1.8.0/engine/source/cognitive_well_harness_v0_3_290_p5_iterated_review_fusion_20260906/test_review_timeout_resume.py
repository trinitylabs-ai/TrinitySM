from . import pipeline
from . import queue_problems


def test_qwen_fixed_cap_with_existing_role_deadlines(monkeypatch, tmp_path):
    seen = []
    def raw(**kwargs):
        seen.append(kwargs["config"])
        return {"text": "ok", "metadata": {}}
    monkeypatch.setattr(pipeline.transport, "run_openai_chat_generation", raw)
    config = pipeline.transport.HTTPGenerationConfig(
        max_tokens=32768, temperature=0.2, top_p=1, top_k=-1, seed=17,
        thinking_token_budget=None, reasoning_effort=None, timeout_seconds=600,
    )
    with pipeline.runtime_generation_policy(model_timeout_sec=600):
        for name in ("reviewer2", "audit_repair_brief"):
            pipeline.transport.run_openai_chat_generation(
                model=pipeline.repair_boundary.QWEN_MODEL, stage=name, config=config,
                endpoint="unused", prompt="unchanged", user_prompt="unchanged", output_dir=tmp_path,
            )
    assert [row.timeout_seconds for row in seen] == [2400, 600]
    assert all(row.seed == 17 and row.max_tokens == 49152 and row.temperature == 0.2 for row in seen)


def test_all_lanes_timeout_does_not_release_queue(tmp_path):
    pipeline.write_json(tmp_path / "status.json", {
        "state": "failed_closed", "stage": "all_lanes",
        "lane_failures": {"lane": {"stage": "R1-C3", "error": "TimeoutError: timed out"}},
    })
    assert not queue_problems.pipeline_finished(tmp_path)


def test_interrupted_fresh_reviews_keep_saved_artifacts(tmp_path, monkeypatch):
    root = tmp_path / "run"
    pipeline.run_pipeline(output_dir=root, input_checkpoint="lazy_checked", dry_run=True)
    manifest = pipeline.read_object(root / "manifest.json")
    for row in manifest["frozen_inputs"]["lanes"]:
        stage = root / "lanes" / row["candidate_id"] / "01_r1_cycle_1"
        pipeline.write_json(stage / "status.json", {"state": "running", "stage": "fresh_reviews"})
        pipeline.write_json(stage / "manifest.json", {"cases": [{
            "candidate_id": row["candidate_id"], "proof_sha256": row["proof_sha256"],
            "problem_sha256": manifest["frozen_inputs"]["problem_text_sha256"],
        }]})
        pipeline.write_json(stage / "saved_review_marker.json", {"keep": True})
    observed = []
    def stage_run(**kwargs):
        stage = kwargs["output_dir"]
        assert pipeline.read_object(stage / "saved_review_marker.json") == {"keep": True}
        observed.append(stage)
        raise RuntimeError("test stops before a model call")
    monkeypatch.setattr(pipeline.stage, "run", stage_run)
    pipeline.run_pipeline(output_dir=root, input_checkpoint="lazy_checked",
                          resume_fresh_reviews=True, authorize_model_calls=True,
                          enable_exact_evidence=False)
    assert len(observed) == 4
    assert (root / "mechanical_resume_after_cycle_0/status.json").is_file()
    assert pipeline.read_object(root / "resume_after_cycle_0.json")["resume_fresh_reviews"] is True
