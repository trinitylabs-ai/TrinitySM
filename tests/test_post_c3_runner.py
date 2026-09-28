"""Offline source binding and real frozen-engine preflight for final-proof completion."""
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.post_c3_completion import inputs, runner


def args(output, *extra):
    return runner.parser().parse_args(['run', '--output-dir', str(output), *extra])


def test_published_b_input_has_no_model_visible_scores_and_preserves_c1(monkeypatch):
    read = inputs.read
    opened = []
    def tracked(path):
        opened.append(str(path))
        assert '/grades/' not in str(path) and '/grading/' not in str(path)
        return read(path)
    monkeypatch.setattr(inputs, 'read', tracked)
    bank = inputs.load_archive(inputs.DEFAULT_ARCHIVE, None)
    assert bank['source_arm'] == 'B'
    assert len(bank['problems']) == 6
    assert sum(c['selected_stage'] == 'refinement_3' for row in bank['problems'] for c in row['candidates']) == 23
    p3 = next(row for row in bank['problems'] if row['problem']['problem_id'] == 'imo2026_p3')
    assert sum(c['selected_stage'] == 'refinement_1' for c in p3['candidates']) == 1
    serialized = json.dumps(bank['problems'])
    assert 'score' not in serialized and 'first_issue' not in serialized and 'reference' not in serialized
    assert all(set(row['problem']) == {'problem_id', 'problem_number', 'claim', 'problem_sha256'} for row in bank['problems'])


def test_exact_bytes_snapshot_and_tamper_detection(tmp_path):
    bank = inputs.load_archive(inputs.DEFAULT_ARCHIVE, ['imo2026_p4'])
    path = inputs.snapshot(bank, tmp_path.resolve() / 'inputs')
    frozen = inputs.verify_manifest(path, inputs.digest(path))
    for old, new in zip(bank['problems'][0]['candidates'], frozen['problems'][0]['candidates']):
        assert Path(old['proof_path']).read_bytes() == Path(new['proof_path']).read_bytes()
    proof = Path(frozen['problems'][0]['candidates'][0]['proof_path'])
    proof.write_text('Tampered')
    with pytest.raises(ValueError, match='binding changed'):
        inputs.verify_manifest(path)


def test_reject_published_proof_drift(tmp_path):
    archive = tmp_path.resolve() / 'archive'
    shutil.copytree(inputs.DEFAULT_ARCHIVE, archive)
    (archive / 'proofs/B/imo2026_p4/t10_r01.md').write_text('Changed source')
    with pytest.raises(ValueError, match='Published file changed'):
        inputs.load_archive(archive, ['imo2026_p4'])


def test_source_selection_is_explicit_and_unique(tmp_path):
    with pytest.raises(SystemExit):
        args(tmp_path / 'output')
    with pytest.raises(SystemExit):
        args(tmp_path / 'output', '--all', '--source-arm', 'A')
    with pytest.raises(ValueError, match='unique'):
        inputs.load_archive(inputs.DEFAULT_ARCHIVE, ['imo2026_p4', 'imo2026_p4'])
    with pytest.raises(ValueError, match='known'):
        inputs.load_archive(inputs.DEFAULT_ARCHIVE, ['imo2026_p7'])


def test_plan_defaults_to_dry_run_b_new_seed_recorded(tmp_path):
    output = tmp_path.resolve() / 'plan'
    path = runner.create_plan(args(output, '--problem-id', 'imo2026_p4'))
    plan = inputs.read(path)
    job = inputs.read(plan['jobs'][0]['job_path'])
    assert plan['source_arm'] == job['source_arm'] == 'B'
    assert plan['dry_run'] is job['dry_run'] is True
    assert job['runtime']['seed_namespace'] == 'post-c3-completion:0:imo2026_p4'
    assert job['runtime']['model_timeout_sec'] == 14400
    assert 'qwen_endpoint' not in job['runtime']
    assert plan['max_completion_passes'] == 1
    assert plan['processing_scope'] == job['processing_scope'] == 'all_saved_final_proofs'
    assert plan['final_candidates'] == plan['c3_candidates'] == 4
    assert plan['earlier_stage_final_candidates'] == 0
    with pytest.raises(ValueError, match='fresh'):
        runner.create_plan(args(output, '--problem-id', 'imo2026_p4'))


def test_output_must_not_overlap_archive(tmp_path):
    with pytest.raises(ValueError, match='separate'):
        runner.create_plan(args(inputs.DEFAULT_ARCHIVE / 'new-output', '--problem-id', 'imo2026_p4'))


def test_real_engine_preflight_has_no_model_calls_or_grading(tmp_path):
    output = tmp_path.resolve() / 'dryrun'
    result = subprocess.run([sys.executable, '-B', str(runner.ROOT / 'scripts/run_post_c3_completion.py'),
        'run', '--problem-id', 'imo2026_p3', '--problem-id', 'imo2026_p4', '--output-dir', str(output)],
        cwd=runner.ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    status = inputs.read(output / 'status.json')
    assert status['state'] == 'preflight_passed'
    assert len(status['outcomes']) == 2
    summaries = [inputs.read(Path(row['summary_path'])) for row in status['outcomes']]
    assert all(row['model_calls'] == 0 and len(row['lanes']) == 4 for row in summaries)
    assert all(row['processing_scope'] == 'all_saved_final_proofs' for row in summaries)
    assert all(lane['operation'] == 'preflight_only' for row in summaries for lane in row['lanes'])
    assert sum(lane['source_stage'] == 'refinement_1' for row in summaries for lane in row['lanes']) == 1
    plan = inputs.read(output / 'plan.json')
    assert plan['final_candidates'] == 8
    assert plan['c3_candidates'] == 7 and plan['earlier_stage_final_candidates'] == 1
    assert (output / 'REPORT.md').exists()
    assert not (output / 'grading').exists()


def test_interruption_terminates_only_owned_child_and_records(tmp_path, monkeypatch):
    path = runner.create_plan(args(tmp_path.resolve() / 'interrupt', '--problem-id', 'imo2026_p4'))
    stopped = []
    class Child:
        pid = 345678
        def __init__(self, *args, **kwargs):
            assert kwargs['start_new_session'] is True
        def wait(self, timeout=None):
            raise runner.Interrupted(signal.SIGTERM)
    monkeypatch.setattr(runner.subprocess, 'Popen', Child)
    monkeypatch.setattr(runner, 'stop_child', lambda child: stopped.append(child.pid))
    with pytest.raises(runner.Interrupted):
        runner.run_plan(path)
    assert stopped == [345678]
    assert inputs.read(path.parent / 'status.json')['state'] == 'interrupted'
