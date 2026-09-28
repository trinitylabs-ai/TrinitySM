import fcntl
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('split_raw', Path(__file__).with_name('split_run.py'))
split = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(split)
h = split.harness


@pytest.fixture
def source(tmp_path, monkeypatch):
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    for number in range(1, 5):
        h.write(inputs / f'{number}.json', {'problem_id': f'PB-Basic-{number:03d}', 'problem': f'Problem {number}'})
    calls, checks = [], []
    server = {'pid': 1, 'process_start_ticks': '1', 'argv_sha256': 'same'}

    def verify(endpoint):
        checks.append(endpoint)
        if len(checks) > 1:
            raise ValueError('Stop fixture after first complete problem')
        return server

    def model(url, request=None, timeout=15):
        calls.append(request)
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': 'Preserved raw proof.'}}]}

    monkeypatch.setattr(h, 'verify_server', verify)
    monkeypatch.setattr(h, 'http_json', model)
    root = tmp_path / 'source'
    args = h.parse_args(['--problem-dir', str(inputs), '--output-dir', str(root), '--execute-models'])
    with pytest.raises(ValueError, match='Stop fixture'):
        h.run(args)
    assert len(calls) == 4
    monkeypatch.setattr(h, 'verify_server', lambda endpoint: server)
    return root, tmp_path / 'split', calls


def test_split_preserves_requests_results_and_complete_coverage(source):
    origin, output, calls = source
    original_hashes = {p: split.digest(p) for p in origin.glob('problems/*/candidates/*/result.json')}
    result = split.prepare(origin, output, 'http://127.0.0.1:8031/v1')
    assert result['total'] == 16 and result['finished'] == 4 and result['imported_candidates'] == 4
    manifest = h.read(output / 'split_manifest.json')
    assert manifest['shards'][0]['problem_ids'] == ['PB-Basic-001', 'PB-Basic-002']
    assert manifest['shards'][1]['problem_ids'] == ['PB-Basic-003', 'PB-Basic-004']
    assert len(calls) == 4  # Preparation makes no model calls.
    for path, digest in original_hashes.items():
        assert split.digest(path) == digest
    for shard in manifest['shards']:
        path = Path(shard['output_dir'])
        staged = h.read(path / 'summary.json')
        for row in staged['rows']:
            original_request = origin / 'problems' / row['problem_id'] / 'candidates' / row['candidate_id'] / 'request.json'
            assert h.read(row['request_path']) == h.read(original_request)
        h.run(h.parse_args(shard['command'][4:]))
    assert len(calls) == 16  # Each of the 16 requested drafts was generated once.
    complete = split.aggregate(output)
    assert complete['state'] == 'completed' and complete['proofs_saved'] == 16
    assert complete['counts'] == {'completed': 16}
    assert h.read(origin / 'status.json')['state'] == 'continued_in_dual_gpu_run'


def test_reject_running_source_and_duplicate_split(source):
    origin, output, calls = source
    with (origin / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            split.prepare(origin, output, 'http://127.0.0.1:8031/v1')
    split.prepare(origin, output, 'http://127.0.0.1:8031/v1')
    with pytest.raises(ValueError, match='already prepared'):
        split.prepare(origin, output, 'http://127.0.0.1:8031/v1')
    assert len(calls) == 4


def test_reject_changed_payload_before_import(source):
    origin, output, calls = source
    path = origin / 'problems/PB-Basic-001/candidates/t10_r01/request.json'
    request = h.read(path)
    request['max_tokens'] += 1
    h.write(path, request)
    with pytest.raises(ValueError, match='changed the generation payload'):
        split.prepare(origin, output, 'http://127.0.0.1:8031/v1')
    assert len(calls) == 4
