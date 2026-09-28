import ast
import importlib.util
import json
import threading
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('raw_no_bf', Path(__file__).with_name('run.py'))
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    problems = tmp_path / 'problems'
    problems.mkdir()
    for number in (1, 2):
        harness.write(problems / f'{number}.json', {'problem_id': f'PB-Basic-{number:03d}', 'problem': f'Prove test statement {number}.'})
    calls = []
    lock = threading.Lock()
    server = {'pid': 123, 'process_start_ticks': '456', 'argv_sha256': 'frozen',
              'speculative_config': {'method': 'mtp', 'num_speculative_tokens': 4}}
    monkeypatch.setattr(harness, 'verify_server', lambda endpoint: dict(server))

    def request(url, payload=None, timeout=15):
        assert url.endswith('/chat/completions')
        with lock:
            calls.append(payload)
        return {'id': 'test', 'choices': [{'finish_reason': 'stop', 'message': {
            'content': 'A completed proof.', 'reasoning_content': 'Private reasoning.'}}],
            'usage': {'completion_tokens': 123}}

    monkeypatch.setattr(harness, 'http_json', request)
    args = harness.parse_args(['--problem-dir', str(problems), '--output-dir', str(tmp_path / 'output'), '--execute-models'])
    return args, calls, server


def test_frozen_prompts_and_seed_match_original_without_importing_runtime():
    original = harness.REPO / 'cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827/run.py'
    constants = {}
    for node in ast.parse(original.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith('FROZEN_'):
                    constants[target.id] = ast.literal_eval(node.value)
    prompts = harness.prompts()
    assert prompts['system.txt'] == constants['FROZEN_SYSTEM_PROMPT']
    assert prompts['user_prefix.txt'] == constants['FROZEN_USER_PREFIX']
    assert prompts['user_suffix.txt'] == constants['FROZEN_USER_SUFFIX']
    assert harness.stable_seed(1, 't10_r01', 2360094352, 0) == 3329703009
    assert harness.stable_seed(9, 't10_r01', 2360094352, 1592974400) == 3015135398


def test_exactly_four_requests_per_problem_and_resume_does_not_regenerate(setup):
    args, calls, _ = setup
    result = harness.run(args)
    assert result['state'] == 'completed' and result['proofs_saved'] == 8
    assert len(calls) == 8
    for problem in ('1', '2'):
        batch = [c for c in calls if f'statement {problem}.' in c['messages'][1]['content']]
        assert sorted(c['temperature'] for c in batch) == [0.7, 0.7, 1.0, 1.0]
        assert len({c['seed'] for c in batch}) == 4
    for call in calls:
        assert [m['role'] for m in call['messages']] == ['system', 'user']
        assert call['model'] == harness.MODEL
        assert call['n'] == 1 and call['max_tokens'] == 65536
        assert call['chat_template_kwargs'] == {'enable_thinking': True}
        assert call['min_tokens'] == 0 and call['ignore_eos'] is False
        assert 'thinking_token_budget' not in call and 'tools' not in call
        assert call['top_p'] == 0.95 and call['top_k'] == 64
    args.resume = True
    assert harness.run(args)['state'] == 'completed'
    assert len(calls) == 8


def test_truncation_reasoning_only_and_failure_do_not_trigger_retries(setup, monkeypatch):
    args, calls, _ = setup
    first = harness.collect_problems(args.problem_dir, [])[0]
    seeds = [harness.stable_seed(1, cid, base, 0) for cid, _, base in harness.CANDIDATES]

    def request(url, payload=None, timeout=15):
        calls.append(payload)
        seed = payload['seed']
        if seed == seeds[0]:
            message, finish = {'content': 'An unfinished proof', 'reasoning': 'Thinking'}, 'length'
        elif seed == seeds[1]:
            message, finish = {'content': None, 'reasoning_content': 'Reasoning only'}, 'length'
        elif seed == seeds[2]:
            message, finish = {'content': None, 'reasoning': 'Natural stop without final answer'}, 'stop'
        elif seed == seeds[3]:
            raise TimeoutError('Simulated request timeout')
        else:
            message, finish = {'content': 'Second problem still runs'}, 'stop'
        return {'choices': [{'message': message, 'finish_reason': finish}]}

    monkeypatch.setattr(harness, 'http_json', request)
    result = harness.run(args)
    assert len(calls) == 8
    assert result['counts'] == {'truncated': 2, 'reasoning_only': 1, 'failed': 1, 'completed': 4}
    by_id = {r['candidate_id']: r for r in result['rows'] if r['problem_id'] == first['problem_id']}
    assert by_id['t10_r01']['proof_path']
    assert by_id['t10_r02']['proof_path'] is None
    assert by_id['t07_r01']['proof_path'] is None
    assert all(r['generation_requests'] == 1 and r['continuation_requests'] == 0 for r in result['rows'])
    args.resume = True
    harness.run(args)
    assert len(calls) == 8


def test_dry_run_has_no_network_calls_and_preserves_filtered_seeds(setup, monkeypatch):
    args, calls, _ = setup
    monkeypatch.setattr(harness, 'verify_server', lambda endpoint: pytest.fail('dry run contacted server'))
    args.execute_models = False
    args.problem_id = ['PB-Basic-002']
    result = harness.run(args)
    assert result['state'] == 'dry_run' and not calls
    request = harness.read(args.output_dir / 'problems/PB-Basic-002/candidates/t10_r01/request.json')
    assert request['seed'] == harness.stable_seed(2, 't10_r01', 2360094352, 0)


def test_reject_extra_inputs_and_resume_drift(setup):
    args, calls, _ = setup
    path = args.problem_dir / '1.json'
    original = harness.read(path)
    harness.write(path, dict(original, reference='must never be sent'))
    with pytest.raises(ValueError, match='only problem_id'):
        harness.run(args)
    assert not calls
    harness.write(path, original)
    harness.run(args)
    args.resume = True
    args.max_tokens = 32768
    with pytest.raises(ValueError, match='Resume changed'):
        harness.run(args)
    assert len(calls) == 8


def test_interrupted_request_is_not_reissued_and_corruption_is_rejected(setup):
    args, calls, _ = setup
    args.execute_models = False
    harness.run(args)
    case = args.output_dir / 'problems/PB-Basic-001/candidates/t10_r01'
    payload = harness.read(case / 'request.json')
    harness.write(case / 'request_started.json', {'request_sha256': harness.sha(json.dumps(payload, sort_keys=True)), 'generation_requests': 1})
    args.resume = True
    args.execute_models = True
    result = harness.run(args)
    assert len(calls) == 7 and result['counts']['interrupted'] == 1
    completed = next(r for r in result['rows'] if r['state'] == 'completed')
    Path(completed['proof_path']).write_text('Changed proof')
    with pytest.raises(ValueError, match='Saved proof changed'):
        harness.run(args)
    assert len(calls) == 7


def test_resume_recovers_saved_response_without_new_request(setup):
    args, calls, _ = setup
    args.execute_models = False
    harness.run(args)
    case = args.output_dir / 'problems/PB-Basic-001/candidates/t10_r01'
    payload = harness.read(case / 'request.json')
    harness.write(case / 'request_started.json', {'request_sha256': harness.sha(json.dumps(payload, sort_keys=True)), 'generation_requests': 1})
    harness.write(case / 'raw_response.json', {'choices': [{'finish_reason': 'stop', 'message': {'content': 'Already generated proof.'}}]})
    args.resume = True
    args.execute_models = True
    result = harness.run(args)
    assert len(calls) == 7 and result['counts'] == {'completed': 8}
    recovered = harness.read(case / 'result.json')
    assert recovered['recovered_from_saved_response']
    assert (case / 'draft_proof.md').read_text().strip() == 'Already generated proof.'


@pytest.mark.parametrize('speculative', [None, {'method': 'mtp', 'num_speculative_tokens': 0},
    {'method': 'mtp', 'num_speculative_tokens': 3}, {'method': 'ngram', 'num_speculative_tokens': 4}])
def test_reject_server_without_mtp4(speculative):
    argv = ['vllm', 'serve', harness.MODEL, '--dtype', 'bfloat16', '--reasoning-parser', 'gemma4']
    if speculative is not None:
        argv += ['--speculative-config', json.dumps(speculative)]
    with pytest.raises(ValueError, match='num_speculative_tokens=4'):
        harness.validate_server_arguments(argv)


def test_actual_listening_process_is_verified(tmp_path, monkeypatch):
    proc = tmp_path / 'proc'
    (proc / 'net').mkdir(parents=True)
    (proc / '123/fd').mkdir(parents=True)
    (proc / 'net/tcp').write_text('header\n0: 0100007F:1F5E 00000000:0000 0A 0 0 0 0 0 98765\n')
    argv = ['vllm', 'serve', harness.MODEL, '--port', '8030', '--dtype', 'bfloat16',
            '--reasoning-parser', 'gemma4', '--speculative-config', '{"method":"mtp","num_speculative_tokens":4}']
    (proc / '123/cmdline').write_bytes(('\0'.join(argv) + '\0').encode())
    (proc / '123/stat').write_text('123 (vllm) ' + ' '.join(['0'] * 19 + ['456']))
    (proc / '123/fd/3').symlink_to('socket:[98765]')
    monkeypatch.setattr(harness, 'http_json', lambda *a, **kw: {'data': [{'id': harness.MODEL}]})
    result = harness.verify_server('http://127.0.0.1:8030/v1', proc)
    assert result['pid'] == 123 and result['process_start_ticks'] == '456'
    (proc / '123/fd/3').unlink()
    with pytest.raises(ValueError, match='Cannot verify'):
        harness.verify_server('http://127.0.0.1:8030/v1', proc)


def test_wrong_server_prevents_generation(setup, monkeypatch):
    args, calls, _ = setup
    def reject(endpoint):
        raise ValueError('MTP configuration mismatch')
    monkeypatch.setattr(harness, 'verify_server', reject)
    with pytest.raises(ValueError, match='MTP configuration mismatch'):
        harness.run(args)
    assert calls == []
    assert harness.read(args.output_dir / 'status.json')['state'] == 'failed_server_verification'
