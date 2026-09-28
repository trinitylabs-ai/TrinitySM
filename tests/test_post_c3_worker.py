"""Offline post-C3 orchestration, source preservation and failure checks."""
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys
import threading
from types import ModuleType, SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.post_c3_completion import worker, prompts


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else (json.dumps(value) + '\n').encode())
    return path


def read(path):
    return json.loads(path.read_bytes())


@pytest.fixture
def job_file(tmp_path):
    root = tmp_path.resolve()
    claim = 'Prove x squared is nonnegative for all real x.'
    problem = {'problem_id': 'imo2026_p2', 'problem_number': 2, 'claim': claim,
               'problem_sha256': worker.frozen.digest(claim.encode())}
    candidates = []
    for cid in worker.CANDIDATES:
        data = f'\r\nOriginal C3 {cid}: a square is nonnegative.\r\n'.encode()
        path = write(root / 'inputs/imo2026_p2' / f'{cid}.md', data)
        candidates.append({'candidate_id': cid, 'proof_path': str(path),
            'proof_file_sha256': worker.frozen.digest(data), 'proof_sha256': worker.frozen.text_digest(data),
            'selected_stage': 'refinement_3'})
    manifest = write(root / 'inputs/manifest.json', {'schema': 'post-c3-inputs-v1', 'source_arm': 'B',
        'release_sha256': worker.frozen.digest((worker.RELEASE / 'release.json').read_bytes()),
        'archive_manifest_sha256': 'a' * 64, 'source_hashes': {},
        'problems': [{'problem': problem, 'candidates': candidates}]})
    return write(root / 'job.json', {'schema': 'post-c3-job-v1', 'dry_run': False, 'output_dir': str(root / 'output'),
        'processing_scope': 'all_saved_final_proofs',
        'source_arm': 'B', 'problem': problem, 'candidates': candidates,
        'runtime': {'gemma_endpoint': 'http://127.0.0.1:8030/v1', 'model_timeout_sec': 14400,
                    'workers': 4, 'seed_namespace': 'post-c3-completion:0:imo2026_p2'},
        'input_manifest_path': str(manifest), 'input_manifest_sha256': worker.frozen.digest(manifest.read_bytes())})


def change_stage(job_file, index, stage):
    job = read(job_file)
    job['candidates'][index]['selected_stage'] = stage
    path = Path(job['input_manifest_path'])
    manifest = read(path)
    manifest['problems'][0]['candidates'] = job['candidates']
    write(path, manifest)
    job['input_manifest_sha256'] = worker.frozen.digest(path.read_bytes())
    write(job_file, job)


@pytest.fixture
def runtime(monkeypatch):
    state = {'calls': [], 'servers': [], 'verify_count': 0, 'reports': {}, 'failures': {},
             'check_barrier': None, 'expand_barrier': None, 'during': None, 'malformed': set(), 'contexts': []}
    policy = ModuleType('harnesses.post_c3_completion.policy')
    class PolicyError(RuntimeError):
        pass
    policy.PolicyError = PolicyError
    @contextmanager
    def install(bf, path, *, routes):
        state['contexts'].append(('enter', path.name, routes))
        state['active'] = True
        try:
            yield
        finally:
            state['active'] = False
            state['contexts'].append(('exit', path.name))
    policy.install = install
    monkeypatch.setitem(sys.modules, policy.__name__, policy)
    import harnesses.post_c3_completion as package
    monkeypatch.setattr(package, 'policy', policy, raising=False)
    module = ModuleType('offline_post_c3_frontend')
    module.lazy_phrasing = lambda proof: 'ORIGINAL LAZY\n' + proof
    state['original_lazy'] = module.lazy_phrasing
    module.lazy_in_place_expansion_prompt = lambda **kwargs: 'FROZEN EXPANSION\n' + json.dumps(kwargs, sort_keys=True)
    def expansion_parser(text):
        if not text.startswith('VALID ENVELOPE\n'):
            return {'valid': False, 'errors': ['malformed envelope']}
        return {'valid': True, 'proof': text.split('\n', 1)[1], 'conclusion_action': 'PRESERVE'}
    module.expansion_parser = expansion_parser
    monkeypatch.setitem(sys.modules, module.__name__, module)
    class Runtime:
        def __init__(self, config):
            self.config = config
            state['runtime'] = self
        def gemma_call(self, **kwargs):
            assert state['active']
            cid = kwargs['output_dir'].parent.name
            state['calls'].append(('expansion', cid, kwargs))
            assert kwargs['user_prompt'] == worker.EXPANSION_USER + '\n\n' + prompts.EXPANSION_GUIDANCE
            assert kwargs['max_tokens'] == 65536
            if state['expand_barrier']:
                state['expand_barrier'].wait(5)
            if ('expansion', cid) in state['failures']:
                raise state['failures'][('expansion', cid)]
            text = 'bad incomplete response' if cid in state['malformed'] else 'VALID ENVELOPE\nComplete expanded proof for ' + cid
            return {'text': text, 'parsed': expansion_parser(text), 'final_generation': {'config': {'max_tokens': 65536}}}
    def config(**kwargs):
        assert set(kwargs) == {'gemma_endpoint'}
        return SimpleNamespace(**kwargs, lazy_max_tokens=16384, solver_max_tokens=65536, protocol_attempts=2)
    def lazy_check(*, runtime, output_dir, row):
        assert state['active']
        cid = row['candidate_id']
        system = module.lazy_phrasing(row['proof'])
        assert system == prompts.lazy_phrasing(row['proof'])
        state['calls'].append(('lazy_check', cid, {'row': row, 'system': system, 'cap': runtime.config.lazy_max_tokens}))
        if state['check_barrier']:
            state['check_barrier'].wait(5)
        if state['during']:
            state['during'](cid)
        if ('lazy_check', cid) in state['failures']:
            raise state['failures'][('lazy_check', cid)]
        report = state['reports'].get(cid, 'NO_ISSUES')
        return {**row, 'lazy_report': report, 'lazy_report_sha256': worker.frozen.digest(report.encode()),
                'has_lazy_issues': report != 'NO_ISSUES', 'lazy_generation': {'text': report}}
    def lazy_resolve(*, runtime, problem, output_dir, row):
        assert row['has_lazy_issues']
        cid = row['candidate_id']
        generated = runtime.gemma_call(output_dir=output_dir / 'candidates' / cid / 'lazy_in_place_resolve',
            name='lazy_in_place_resolve', system_prompt=module.lazy_in_place_expansion_prompt(
                problem=problem, current_proof=row['proof'], local_gaps=row['lazy_report']),
            user_prompt=worker.EXPANSION_USER, max_tokens=runtime.config.solver_max_tokens)
        proof = generated['parsed'].get('proof', 'INVALID NATIVE OUTPUT')
        path = write(output_dir / 'candidates' / cid / 'checked_proof.md', (proof + '\n').encode())
        return {'candidate_id': cid, 'checked_proof_path': str(path),
                'checked_proof_sha256': worker.frozen.text_digest(path.read_bytes()),
                'conclusion_action': 'PRESERVE', 'expansion_generation': generated}
    lazy_check.__module__ = module.__name__
    lazy_resolve.__module__ = module.__name__
    frontend = SimpleNamespace(GPU0FourSlotStageRuntime=Runtime, RuntimeConfig=config,
        run_lazy_check=lazy_check, run_lazy_resolve=lazy_resolve)
    backend = SimpleNamespace(v108=SimpleNamespace(v097=frontend),
        v263=SimpleNamespace(parent=SimpleNamespace(_budget_forcing=object())))
    monkeypatch.setattr(worker.frozen, 'load_backend', lambda: backend)
    def verify():
        state['verify_count'] += 1
        return {'version': '1.7.0'}, {'servers': {'gemma': {'model': 'gemma'}, 'qwen': {'model': 'qwen'}}}
    def server(endpoint, expected):
        assert expected['model'] == 'gemma'
        state['servers'].append(endpoint)
        return {'model': 'gemma', 'pinned': True}
    launcher = SimpleNamespace(verify=verify, server_settings=server)
    monkeypatch.setattr(worker.frozen, 'load_release', lambda: (launcher, *verify()))
    state['module'], state['policy_error'] = module, PolicyError
    return state


def test_parallel_checks_then_conditional_expansion_once(job_file, runtime):
    runtime['check_barrier'] = threading.Barrier(4)
    runtime['expand_barrier'] = threading.Barrier(2)
    for cid in worker.CANDIDATES[:2]:
        runtime['reports'][cid] = 'The exact implication at step 3 is missing.'
    source_bytes = {c['candidate_id']: Path(c['proof_path']).read_bytes() for c in read(job_file)['candidates']}
    result = worker.run(job_file, execute_models=True)
    assert result['state'] == 'completed'
    assert [role for role, _, _ in runtime['calls']] == ['lazy_check'] * 4 + ['expansion'] * 2
    for lane in result['lanes']:
        cid = lane['candidate_id']
        if cid in worker.CANDIDATES[:2]:
            assert lane['operation'] == 'expanded' and lane['changed']
            assert Path(lane['proof_path']).read_text().startswith('Complete expanded proof')
        else:
            assert lane['operation'] == 'no_issues' and not lane['changed']
            assert Path(lane['proof_path']).read_bytes() == source_bytes[cid]
        assert Path(lane['source_proof_path']).read_bytes() == source_bytes[cid]
        assert lane['elapsed_seconds'] >= 0
    assert len(runtime['servers']) == 1 and runtime['verify_count'] >= 2
    assert runtime['module'].lazy_phrasing is runtime['original_lazy']
    assert 'gemma_call' not in runtime['runtime'].__dict__
    assert not result['grading_performed'] and not result['mathematically_verified']


@pytest.mark.parametrize('stage', ['raw', 'lazy_checked', 'refinement_1', 'refinement_2'])
def test_earlier_final_checkpoint_is_checked_and_no_issues_preserves_bytes(job_file, runtime, stage):
    change_stage(job_file, 0, stage)
    result = worker.run(job_file, execute_models=True)
    lane = result['lanes'][0]
    assert result['processing_scope'] == 'all_saved_final_proofs'
    assert lane['source_stage'] == stage
    assert lane['operation'] == 'no_issues' and lane['failure'] is None and not lane['changed']
    assert [(role, cid) for role, cid, _ in runtime['calls']].count(('lazy_check', worker.CANDIDATES[0])) == 1
    assert len(runtime['calls']) == 4
    assert Path(lane['proof_path']).read_bytes() == Path(lane['source_proof_path']).read_bytes()


def test_c1_final_proof_is_expanded_when_new_lazy_check_finds_issues(job_file, runtime):
    change_stage(job_file, 0, 'refinement_1')
    cid = worker.CANDIDATES[0]
    source_bytes = Path(read(job_file)['candidates'][0]['proof_path']).read_bytes()
    runtime['reports'][cid] = 'The exact implication at step 3 is missing.'
    result = worker.run(job_file, execute_models=True)
    lane = result['lanes'][0]
    assert lane['source_stage'] == 'refinement_1' and lane['operation'] == 'expanded' and lane['changed']
    assert [role for role, candidate, _ in runtime['calls'] if candidate == cid] == ['lazy_check', 'expansion']
    assert Path(lane['proof_path']).read_text().startswith('Complete expanded proof')
    assert Path(lane['source_proof_path']).read_bytes() == source_bytes


@pytest.mark.parametrize('scope', [None, 'only_c3'])
@pytest.mark.parametrize('dry_run', [False, True])
def test_old_or_different_processing_scope_is_rejected_before_model_access(job_file, runtime, scope, dry_run):
    job = read(job_file)
    job['dry_run'] = dry_run
    if scope is None:
        job.pop('processing_scope')
    else:
        job['processing_scope'] = scope
    write(job_file, job)
    with pytest.raises(worker.IntegrityError, match='processing_scope=all_saved_final_proofs'):
        worker.run(job_file, execute_models=not dry_run)
    assert not runtime['servers'] and not runtime['calls']
    assert not Path(job['output_dir']).exists()


def test_identical_proofs_share_one_route_but_keep_independent_lane_calls(job_file, runtime):
    job = read(job_file)
    first, second = job['candidates'][:2]
    Path(second['proof_path']).write_bytes(Path(first['proof_path']).read_bytes())
    second.update(proof_file_sha256=first['proof_file_sha256'], proof_sha256=first['proof_sha256'])
    manifest_path = Path(job['input_manifest_path'])
    manifest = read(manifest_path)
    manifest['problems'][0]['candidates'] = job['candidates']
    write(manifest_path, manifest)
    job['input_manifest_sha256'] = worker.frozen.digest(manifest_path.read_bytes())
    write(job_file, job)
    result = worker.run(job_file, execute_models=True)
    assert len(runtime['calls']) == 4
    assert len(read(Path(job['output_dir']) / 'lazy_routes.json')) == 3
    assert len({lane['seeds']['lazy_check'] for lane in result['lanes']}) == 4
    assert result['stage'] == 'finished'


@pytest.mark.parametrize('phase', ['lazy_check', 'expansion'])
def test_model_failure_retains_original_c3_and_is_not_no_issues(job_file, runtime, phase):
    cid = worker.CANDIDATES[0]
    runtime['reports'][cid] = 'Missing derivation.'
    runtime['failures'][(phase, cid)] = RuntimeError('model request failed')
    result = worker.run(job_file, execute_models=True)
    lane = result['lanes'][0]
    assert result['state'] == 'completed_with_fallbacks'
    assert lane['operation'] == 'failed' and lane['failure']['stage'] == phase and not lane['changed']
    assert Path(lane['proof_path']).read_bytes() == Path(lane['source_proof_path']).read_bytes()


def test_malformed_envelope_never_becomes_final_proof(job_file, runtime):
    cid = worker.CANDIDATES[0]
    runtime['reports'][cid] = 'Missing derivation.'
    runtime['malformed'].add(cid)
    result = worker.run(job_file, execute_models=True)
    lane = result['lanes'][0]
    assert lane['operation'] == 'failed' and 'valid complete proof envelope' in lane['failure']['error']
    assert not lane['changed']


def test_no_issues_requires_exact_sentinel(job_file, runtime):
    runtime['reports'][worker.CANDIDATES[0]] = 'NO_ISSUES\nBut the last implication is missing.'
    result = worker.run(job_file, execute_models=True)
    assert result['lanes'][0]['operation'] == 'expanded'


def test_dry_run_has_no_server_or_model_calls(job_file, runtime):
    job = read(job_file)
    job['dry_run'] = True
    write(job_file, job)
    result = worker.run(job_file)
    assert result['state'] == 'preflight_passed' and result['model_calls'] == 0
    assert not runtime['servers'] and not runtime['calls']
    assert all(lane['operation'] == 'preflight_only' and not lane['changed'] for lane in result['lanes'])


@pytest.mark.parametrize('dry,execute', [(True, True), (False, False)])
def test_double_opt_in(job_file, runtime, dry, execute):
    job = read(job_file)
    job['dry_run'] = dry
    write(job_file, job)
    with pytest.raises(worker.IntegrityError, match='Live jobs require'):
        worker.run(job_file, execute_models=execute)
    assert not runtime['servers'] and not runtime['calls']


def test_timeout_cannot_silently_change_original_frontend(job_file, runtime):
    job = read(job_file)
    job['runtime']['model_timeout_sec'] = 600
    write(job_file, job)
    with pytest.raises(worker.IntegrityError, match='14400'):
        worker.run(job_file, execute_models=True)
    assert not runtime['servers']


def test_input_drift_rejected_before_model_access(job_file, runtime):
    Path(read(job_file)['candidates'][0]['proof_path']).write_text('Changed proof')
    with pytest.raises(ValueError, match='binding changed'):
        worker.run(job_file, execute_models=True)
    assert not runtime['servers']


def test_drift_during_model_call_fails_whole_run(job_file, runtime):
    job = read(job_file)
    def change(cid):
        if cid == worker.CANDIDATES[0]:
            Path(job['candidates'][0]['proof_path']).write_text('Modified source')
    runtime['during'] = change
    with pytest.raises(worker.IntegrityError):
        worker.run(job_file, execute_models=True)
    assert read(Path(job['output_dir']) / 'summary.json')['state'] == 'failed'


def test_policy_guard_failure_is_fatal(job_file, runtime):
    runtime['failures'][('lazy_check', worker.CANDIDATES[0])] = runtime['policy_error']('Unknown prompt')
    with pytest.raises(runtime['policy_error'], match='Unknown prompt'):
        worker.run(job_file, execute_models=True)
    assert read(Path(read(job_file)['output_dir']) / 'summary.json')['state'] == 'failed'
    assert runtime['module'].lazy_phrasing is runtime['original_lazy']


def test_batch_fatal_error_drains_other_lane_before_return():
    class PolicyError(RuntimeError):
        pass
    entered, released, failed = threading.Event(), threading.Event(), threading.Event()
    def task(cid):
        if cid == 'first':
            assert entered.wait(5)
            failed.set()
            raise PolicyError('guard')
        entered.set()
        assert released.wait(5)
        return {}
    errors = []
    def run():
        try:
            worker.run_batch(['first', 'second'], task, lambda *args: None, policy_error=PolicyError)
        except BaseException as error:
            errors.append(error)
    thread = threading.Thread(target=run)
    thread.start()
    try:
        assert failed.wait(5)
        assert thread.is_alive()
    finally:
        released.set()
        thread.join(5)
    assert not thread.is_alive() and len(errors) == 1 and isinstance(errors[0], PolicyError)


def test_interrupt_does_not_join_lingering_threads():
    script = '''
import threading
from harnesses.post_c3_completion import worker
threading.Thread(target=threading.Event().wait, daemon=False).start()
def stop(*args, **kwargs):
    raise KeyboardInterrupt()
worker.run = stop
raise SystemExit(worker.main(['--job', '/unused/offline-job.json']))
'''
    result = subprocess.run([sys.executable, '-B', '-c', script], cwd=Path(__file__).resolve().parents[1],
                            timeout=5, capture_output=True, text=True)
    assert result.returncode == 130, result.stderr


def test_actual_frozen_frontend_and_bf_with_offline_physical_transport(job_file):
    # A separate process isolates all real frozen-module globals from the unit
    # fixtures. Only physical HTTP inference and /proc serving checks are fake.
    script = r'''
from dataclasses import asdict
import json
from pathlib import Path
import sys
import threading
from harnesses.post_c3_completion import worker, prompts

job_path = Path(sys.argv[1])
real_load_release = worker.frozen.load_release
def load_release():
    launcher, manifest, profile = real_load_release()
    def server(endpoint, expected):
        assert expected['model'] == 'google/gemma-4-31B-it'
        return {'offline_test': True, 'model': expected['model']}
    launcher.server_settings = server
    return launcher, manifest, profile
worker.frozen.load_release = load_release
backend = worker.frozen.load_backend()
bf = backend.v263.parent._budget_forcing
calls, lock = [], threading.Lock()
proof = 'For every real x, x squared is nonnegative because the product of two equal real numbers is nonnegative.'
envelope = ('BEGIN_REPAIR_AUDIT\nCONCLUSION_ACTION: PRESERVE\n'
    'ORIGINAL_CLASSIFICATION: x squared is nonnegative\n'
    'REPAIRED_CLASSIFICATION: x squared is nonnegative\n'
    'CHANGE_BASIS: NONE\nCHANGE_JUSTIFICATION: NONE\nEND_REPAIR_AUDIT\n'
    'BEGIN_REPAIRED_PROOF\n' + proof + '\nEND_REPAIRED_PROOF')
def physical(**kwargs):
    root, stage = Path(kwargs['output_dir']), kwargs['stage']
    root.mkdir(parents=True, exist_ok=True)
    cid = root.parent.name
    forced = bool(kwargs.get('continuation_instruction'))
    is_lazy = stage.startswith('lazy_check')
    if forced:
        assert '[Preserved reasoning]' in kwargs['prior_generation']
        assert '[Preserved response]' in kwargs['prior_generation']
        assert 'PRIMARY REASONING' in kwargs['prior_generation']
        assert 'PRIMARY RESPONSE' in kwargs['prior_generation']
        expected = prompts.LAZY_CONTINUATION if is_lazy else prompts.EXPANSION_CONTINUATION
        assert kwargs['continuation_instruction'] == expected
        text = ('Missing exact derivation.' if cid == 't10_r01' else 'NO_ISSUES') if is_lazy else envelope
    else:
        text = 'PRIMARY RESPONSE'
    if not is_lazy:
        assert kwargs['user_prompt'].endswith(prompts.EXPANSION_GUIDANCE)
        assert 'BEGIN_REPAIR_AUDIT' in kwargs['prompt']
    config = asdict(kwargs['config'])
    assert config['timeout_seconds'] == 14400
    assert config['top_p'] == 0.95 and config['top_k'] == 64
    assert config['max_tokens'] == (32768 if forced else 16384) if is_lazy else config['max_tokens'] == 65536
    with lock:
        calls.append({'cid': cid, 'stage': stage, 'forced': forced, 'config': config})
    reasoning = 'PRIMARY REASONING' if not forced else 'FORCED REASONING'
    metadata = {'stage': stage, 'model': kwargs['model'], 'config': config, 'finish_reason': 'stop'}
    raw = {'choices': [{'finish_reason': 'stop', 'message': {'content': text, 'reasoning_content': reasoning}}]}
    for suffix, data in (('.raw_response.json', json.dumps(raw)), ('.metadata.json', json.dumps(metadata)),
            ('.prompt.txt', kwargs['prompt']), ('.user_prompt.txt', kwargs['user_prompt']), ('.reasoning.txt', reasoning)):
        (root / (stage + suffix)).write_text(data)
    return {'text': text, 'reasoning': reasoning, 'metadata': metadata}
bf._ORIGINAL = physical
result = worker.run(job_path, execute_models=True)
assert result['state'] == 'completed', result
assert len(calls) == 10, calls
assert sum(c['forced'] for c in calls) == 5
assert result['lanes'][0]['operation'] == 'expanded'
assert Path(result['lanes'][0]['proof_path']).read_text().strip() == proof
assert all(lane['operation'] == 'no_issues' for lane in result['lanes'][1:])
output = Path(json.loads(job_path.read_text())['output_dir'])
events = [json.loads(line) for name in ('lazy_continuations.jsonl', 'expansion_continuations.jsonl')
          for line in (output / name).read_text().splitlines()]
assert len(events) == 5
print('actual frontend and chat BF: 4 checks, 1 expansion, 10 physical calls; no HTTP')
'''
    result = subprocess.run([sys.executable, '-B', '-c', script, str(job_file)],
        cwd=Path(__file__).resolve().parents[1], timeout=20, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + '\n' + result.stderr
    assert '10 physical calls; no HTTP' in result.stdout
