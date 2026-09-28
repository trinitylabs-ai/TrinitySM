import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import environment_capture as capture
import run_experiment as runner


@pytest.mark.parametrize('run_id', ['../other', '/tmp/other', 'a/b', '.', 'x;echo bad'])
def test_run_id_cannot_escape_benchmark(run_id):
    with pytest.raises(ValueError):
        runner.destination('imo2026', run_id)


def test_secret_redaction_preserves_generation_flags():
    args = ['vllm', '--api-key', 'secret', '--hf-token=secret2', '--max-num-batched-tokens', '8192',
            'https://user:password@localhost/model?token=secret3']
    saved = capture.sanitize_argv(args)
    text = ' '.join(saved)
    assert all(secret not in text for secret in ('secret', 'password'))
    assert '--max-num-batched-tokens' in saved and '8192' in saved


def test_index_binds_outputs_but_excludes_active_generation_and_grader_work(tmp_path):
    capture.write(tmp_path / 'experiment.json', {'run_id': 'example'})
    for rel in ['proofs/proof.md', 'grades/score.json', 'verification/audit.json',
                'generation/run/active_proof.md', 'grading/work/active_request.json']:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{}')
    (tmp_path / 'original_artifacts').symlink_to(tmp_path / 'generation/run', target_is_directory=True)
    runner.index_artifacts(tmp_path)
    rows = [json.loads(x) for x in (tmp_path / 'artifact_index.jsonl').read_text().splitlines()]
    assert all(x['run_id'] == 'example' for x in rows)
    assert {'proof', 'score', 'verification'} <= {x['kind'] for x in rows}
    assert all('active_' not in x['path'] and not x['path'].startswith('original_artifacts') for x in rows)
    assert all(x['sha256'] == hashlib.sha256((tmp_path / x['path']).read_bytes()).hexdigest() for x in rows)
    runner.index_artifacts(tmp_path, generation_finished=True)
    rows = [json.loads(x) for x in (tmp_path / 'artifact_index.jsonl').read_text().splitlines()]
    assert any(x['path'] == 'generation/run/active_proof.md' for x in rows)
    assert not any(x['path'].startswith('grading/work/') for x in rows)


def test_snapshot_failure_prevents_solver_start(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    monkeypatch.setattr(runner.subprocess, 'run', lambda *a, **k: None)
    def fail_snapshot(*a, **k):
        raise RuntimeError('Missing server metadata')
    monkeypatch.setattr(runner, 'capture', fail_snapshot)
    def forbidden_start(*a, **k):
        pytest.fail('Solver started without a snapshot')
    monkeypatch.setattr(runner.subprocess, 'Popen', forbidden_start)
    monkeypatch.setattr(sys, 'argv', ['run_experiment.py', '--benchmark', 'imo2026', '--run-id', 'blocked', '--execute-models'])
    with pytest.raises(RuntimeError, match='Missing server metadata'):
        runner.main()
    p = tmp_path / 'benchmarks/imo2026/results/blocked'
    assert json.loads((p / 'experiment.json').read_text())['state'] == 'snapshot_failed'
    assert not (p / 'generation/run').exists()


def test_existing_run_is_not_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    monkeypatch.setattr(runner.subprocess, 'run', lambda *a, **k: None)
    p = runner.destination('imo2026', 'existing')
    p.mkdir(parents=True)
    sentinel = p / 'experiment.json'
    sentinel.write_text('{"run_id":"existing"}')
    monkeypatch.setattr(sys, 'argv', ['run_experiment.py', '--benchmark', 'imo2026', '--run-id', 'existing', '--dry-run'])
    with pytest.raises(FileExistsError):
        runner.main()
    assert sentinel.read_text() == '{"run_id":"existing"}'
