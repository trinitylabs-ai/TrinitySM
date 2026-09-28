from pathlib import Path

import pytest

from . import repair_boundary as b
from .test_harness import ScriptedCaller, audit_markdown, rewrite_markdown, source_result, task


def rejected_outputs():
    return [audit_markdown("REJECTED"), rewrite_markdown("First replacement."),
            audit_markdown("REJECTED"), rewrite_markdown("Second replacement."),
            audit_markdown("REJECTED")]


def test_saved_rejection_reused_without_source_changes(tmp_path: Path):
    source = tmp_path / "source"
    result = b.audit_repair_and_reaudit(
        lane=source, task=task(), source_result=source_result(),
        qwen_endpoint="qwen", gemma_endpoint="gemma", cycle_key="R1-C1",
        caller=ScriptedCaller(rejected_outputs()),
    )
    gate = source / "fusion_repair_brief_audit_rewrite/result.json"
    legacy = dict(result["repair_brief_audit_rewrite"], state="failed_closed")
    legacy.pop("certification")
    legacy.pop("synthesis_policy")
    b.write_json(gate, legacy)
    before = {str(path): b.file_sha256(path) for path in source.rglob("*") if path.is_file()}
    resumed = b.reuse_rejected_brief(
        source_gate=gate, source_result=source_result(), task=task(),
        source_case_dir=source, destination=tmp_path / "resumed",
    )
    assert resumed["final"] == result["final"]
    assert resumed["repair_brief_audit_rewrite"]["certification"] == "REJECTED"
    assert before == {str(path): b.file_sha256(path) for path in source.rglob("*") if path.is_file()}
    with pytest.raises(FileExistsError):
        b.reuse_rejected_brief(
            source_gate=gate, source_result=source_result(), task=task(),
            source_case_dir=source, destination=tmp_path / "resumed",
        )
    corrupted = dict(legacy, effective_fusion_sha256="0" * 64)
    b.write_json(gate, corrupted)
    with pytest.raises(ValueError, match="effective text/hash"):
        b.reuse_rejected_brief(
            source_gate=gate, source_result=source_result(), task=task(),
            source_case_dir=source, destination=tmp_path / "corrupted",
        )
    assert not (tmp_path / "corrupted").exists()


def test_transport_failure_does_not_authorize_synthesis(tmp_path: Path):
    def broken(**kwargs):
        raise TimeoutError("transport failure, not a mathematical rejection")

    with pytest.raises(TimeoutError):
        b.audit_repair_and_reaudit(
            lane=tmp_path, task=task(), source_result=source_result(),
            qwen_endpoint="qwen", gemma_endpoint="gemma", cycle_key="R1-C1", caller=broken,
        )
    assert not (tmp_path / "fusion_repair_brief_audit_rewrite/effective_fusion_result.json").exists()
