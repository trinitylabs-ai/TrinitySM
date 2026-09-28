"""Offline checks for independent four-lane refinement experiment workers."""
from contextlib import contextmanager
import json
from pathlib import Path
import signal
import subprocess
import sys
import threading
from types import ModuleType, SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.refinement_bf_ablation import worker


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else (json.dumps(value) + '\n').encode())
    return path


def read(path):
    return json.loads(path.read_bytes())


@pytest.fixture
def job_file(tmp_path):
    root = tmp_path.resolve()
    statement = 'Prove that x² ≥ 0 for every real number x.'
    problem = {'problem_id': 'imo2026_p2', 'problem_number': 2, 'claim': statement,
               'problem_sha256': worker.digest(statement.encode())}
    candidates = []
    for cid in worker.CANDIDATES:
        data = f'\r\nSource {cid}: x² ≥ 0.\r\n'.encode()
        path = write(root / 'inputs' / problem['problem_id'] / f'{cid}.md', data)
        candidates.append({'candidate_id': cid, 'proof_path': str(path),
                           'proof_file_sha256': worker.digest(data), 'proof_sha256': worker.text_digest(data)})
    manifest = write(root / 'inputs/manifest.json', {'schema': 'refinement-bf-inputs-v1',
        'release_sha256': worker.digest((worker.RELEASE / 'release.json').read_bytes()),
        'problems': [{'problem': problem, 'candidates': candidates, 'provenance': {'source_run': 'fixture'}}]})
    job = {'schema': 'refinement-bf-job-v1', 'variant': 'role_specific', 'dry_run': False,
           'output_dir': str(root / 'arm'), 'pair_seed': 42, 'pair_id': 'imo2026_p2__seed42',
           'problem': problem, 'candidates': candidates,
           'runtime': {'gemma_endpoint': 'http://127.0.0.1:8030/v1', 'qwen_endpoint': 'http://127.0.0.1:8027/v1',
                       'model_timeout_sec': 600, 'seed_namespace': 'paired:42', 'workers': 4},
           'input_manifest_path': str(manifest), 'input_manifest_sha256': worker.digest(manifest.read_bytes())}
    return write(root / 'job.json', job)


@pytest.fixture
def runtime(monkeypatch, tmp_path):
    log = {'model_calls': [], 'verified': 0, 'servers': [], 'contexts': [], 'failures': {},
           'barrier': None, 'during_call': None, 'active': {}}
    class PolicyError(RuntimeError):
        pass
    policy = ModuleType('harnesses.refinement_bf_ablation.policy')
    policy.PolicyError = PolicyError
    @contextmanager
    def installed(module, variant, path, *, routes):
        log['contexts'].append(('policy', 'enter'))
        try:
            yield
        finally:
            log['contexts'].append(('policy', 'exit'))
    policy.install = installed
    monkeypatch.setitem(sys.modules, policy.__name__, policy)
    import harnesses.refinement_bf_ablation as package
    monkeypatch.setattr(package, 'policy', policy, raising=False)
    release = tmp_path / 'release'
    write(release / 'release.json', {'version': '1.7.0'})
    monkeypatch.setattr(worker, 'RELEASE', release)
    # RELEASE.parent protection intentionally remains in validation; put the
    # fake release under a separate releases/ tree from the fixture output.
    release = tmp_path / 'frozen/releases/1.7.0'
    write(release / 'release.json', {'version': '1.7.0'})
    monkeypatch.setattr(worker, 'RELEASE', release)
    def verify():
        log['verified'] += 1
        return {'version': '1.7.0'}, {'servers': {'gemma': {'model': 'gemma'}, 'qwen': {'model': 'qwen'}}}
    def server_settings(endpoint, expected):
        log['servers'].append(endpoint)
        return {'model': expected['model'], 'pinned': True}
    launcher = SimpleNamespace(verify=verify, server_settings=server_settings)
    monkeypatch.setattr(worker, 'load_release', lambda: (launcher, *verify()))
    @contextmanager
    def context(name, **kwargs):
        assert not log['active'].get(name)
        log['active'][name] = 1
        log['contexts'].append((name, 'enter', kwargs))
        try:
            yield
        finally:
            log['active'][name] = 0
            log['contexts'].append((name, 'exit', kwargs))
    def run_cycle(**kwargs):
        assert log['active'] == {'runtime': 1, 'caps': 1, 'boundary': 1}
        assert kwargs['problem_path'].is_relative_to(kwargs['output_dir'])
        assert Path(kwargs['source_proof']['proof_path']).is_relative_to(kwargs['output_dir'])
        cid, cycle = kwargs['candidate_id'], kwargs['cycle']
        log['model_calls'].append((cid, cycle, kwargs['seed_namespace']))
        if log['barrier'] is not None:
            log['barrier'].wait(timeout=5)
        if log['during_call']:
            log['during_call'](kwargs)
        error = log['failures'].get((cid, cycle))
        if error:
            raise error
        source = Path(kwargs['source_proof']['proof_path']).read_bytes()
        stage = kwargs['output_dir'] / 'lanes' / cid / f'{cycle:02}_r1_cycle_{cycle}'
        data = source + f'\nrefinement {cycle}\n'.encode()
        path = write(stage / 'proof.md', data)
        return stage, {'candidate_id': cid, 'proof_path': str(path), 'proof_sha256': worker.text_digest(data)}
    backend = SimpleNamespace(v263=SimpleNamespace(parent=SimpleNamespace(_budget_forcing=object())),
        configure_problem_binding=lambda **kwargs: log.update(binding=kwargs),
        runtime_generation_policy=lambda **kwargs: context('runtime', **kwargs),
        inherited_component_caps=lambda: context('caps'),
        mandatory_repair_boundary=lambda **kwargs: context('boundary', **kwargs), run_r1_cycle_lane=run_cycle,
        _case_manifest=lambda **kwargs: write(kwargs['destination'], {'cycle': kwargs['cycle']}))
    monkeypatch.setattr(worker, 'load_backend', lambda: backend)
    monkeypatch.setattr(worker, 'build_routes', lambda backend: ())
    log['policy_error'] = PolicyError
    return log


def test_four_lanes_are_batched_through_three_cycles(job_file, runtime):
    runtime['barrier'] = threading.Barrier(4)
    before = {str(p): p.read_bytes() for p in job_file.parent.joinpath('inputs').rglob('*') if p.is_file()}
    result = worker.run(job_file, execute_models=True)
    assert result['state'] == 'completed'
    assert len(runtime['model_calls']) == 12
    assert all(seed == 'paired:42' for _, _, seed in runtime['model_calls'])
    assert all(lane['selected_stage'] == 'refinement_3' and len(lane['checkpoints']) == 3 for lane in result['lanes'])
    assert len([row for row in runtime['contexts'] if row[:2] == ('runtime', 'enter')]) == 1
    boundaries = [row for row in runtime['contexts'] if row[:2] == ('boundary', 'enter')]
    assert len(boundaries) == 3 and all(row[2]['enable_exact_evidence'] is False for row in boundaries)
    assert runtime['binding']['candidate_ids'] == worker.CANDIDATES
    assert all(Path(path).read_bytes() == data for path, data in before.items())
    assert runtime['verified'] >= 2 and len(runtime['servers']) == 2
    assert not result['grading_performed'] and not result['mathematically_verified']


@pytest.mark.parametrize('cycle,expected', [(1, 'lazy_checked'), (2, 'refinement_1'), (3, 'refinement_2')])
def test_one_lane_falls_back_without_stopping_other_lanes(job_file, runtime, cycle, expected):
    cid = worker.CANDIDATES[0]
    runtime['failures'][(cid, cycle)] = RuntimeError('synthetic model failure')
    result = worker.run(job_file, execute_models=True)
    assert result['state'] == 'completed_with_fallbacks'
    rows = {row['candidate_id']: row for row in result['lanes']}
    assert rows[cid]['selected_stage'] == expected
    assert rows[cid]['failure']['stage'] == f'refinement_{cycle}'
    assert len([row for row in runtime['model_calls'] if row[0] == cid]) == cycle
    assert all(rows[other]['selected_stage'] == 'refinement_3' for other in worker.CANDIDATES[1:])
    if cycle == 1:
        source = read(job_file)['candidates'][0]['proof_path']
        assert Path(rows[cid]['proof_path']).read_bytes() == Path(source).read_bytes()


def test_dry_run_never_checks_servers_or_generates(job_file, runtime):
    job = read(job_file)
    job['dry_run'] = True
    write(job_file, job)
    result = worker.run(job_file)
    assert result['state'] == 'preflight_passed' and result['model_calls'] == 0
    assert runtime['servers'] == runtime['model_calls'] == []
    assert all(row['selected_stage'] == 'lazy_checked' for row in result['lanes'])


@pytest.mark.parametrize('dry_run,execute', [(False, False), (True, True)])
def test_double_opt_in_is_required_before_model_access(job_file, runtime, dry_run, execute):
    job = read(job_file)
    job['dry_run'] = dry_run
    write(job_file, job)
    with pytest.raises(ValueError, match='Live jobs require'):
        worker.run(job_file, execute_models=execute)
    assert runtime['servers'] == runtime['model_calls'] == []
    assert not Path(job['output_dir']).exists()


def test_source_hash_drift_is_rejected_before_server_access(job_file, runtime):
    job = read(job_file)
    Path(job['candidates'][0]['proof_path']).write_text('modified')
    with pytest.raises(ValueError, match='binding changed'):
        worker.run(job_file, execute_models=True)
    assert not runtime['servers'] and not Path(job['output_dir']).exists()


def test_job_cannot_substitute_a_problem_outside_manifest(job_file, runtime):
    job = read(job_file)
    job['problem']['claim'] = 'Other problem'
    job['problem']['problem_sha256'] = worker.digest(b'Other problem')
    write(job_file, job)
    with pytest.raises(ValueError, match='differs from bound input manifest'):
        worker.run(job_file, execute_models=True)
    assert not runtime['servers']


def test_output_collision_is_rejected_before_calls(job_file, runtime):
    output = Path(read(job_file)['output_dir'])
    output.mkdir()
    marker = write(output / 'old.json', {'untouched': True})
    with pytest.raises(ValueError, match='fresh arm'):
        worker.run(job_file, execute_models=True)
    assert read(marker) == {'untouched': True} and not runtime['servers']


def test_policy_guard_failure_is_fatal_not_lane_fallback(job_file, runtime):
    runtime['failures'][(worker.CANDIDATES[0], 1)] = runtime['policy_error']('Unknown role')
    with pytest.raises(runtime['policy_error'], match='Unknown role'):
        worker.run(job_file, execute_models=True)
    summary = read(Path(read(job_file)['output_dir']) / 'summary.json')
    assert summary['state'] == 'failed'


def test_fatal_policy_error_keeps_contexts_until_other_lane_finishes(job_file, runtime, monkeypatch):
    other_started, release_other, shutdown_started = threading.Event(), threading.Event(), threading.Event()
    original_pool = worker.ThreadPoolExecutor
    class ObservedPool(original_pool):
        def shutdown(self, wait=True, *, cancel_futures=False):
            runtime['shutdown_wait'] = wait
            shutdown_started.set()
            return super().shutdown(wait=wait, cancel_futures=cancel_futures)
    monkeypatch.setattr(worker, 'ThreadPoolExecutor', ObservedPool)
    def controlled_call(kwargs):
        cid = kwargs['candidate_id']
        if cid == worker.CANDIDATES[0]:
            assert other_started.wait(5)
            raise runtime['policy_error']('fatal guard')
        if cid == worker.CANDIDATES[1]:
            other_started.set()
            assert release_other.wait(5)
            assert runtime['active'] == {'runtime': 1, 'caps': 1, 'boundary': 1}
            assert ('policy', 'exit') not in runtime['contexts']
    runtime['during_call'] = controlled_call
    errors = []
    def arm():
        try:
            worker.run(job_file, execute_models=True)
        except BaseException as error:
            errors.append(error)
    thread = threading.Thread(target=arm)
    thread.start()
    try:
        assert shutdown_started.wait(5)
        assert runtime['shutdown_wait'] is True
        assert runtime['active'] == {'runtime': 1, 'caps': 1, 'boundary': 1}
        assert ('policy', 'exit') not in runtime['contexts']
        assert thread.is_alive()
    finally:
        release_other.set()
        thread.join(5)
    assert not thread.is_alive()
    assert len(errors) == 1 and isinstance(errors[0], runtime['policy_error'])
    assert runtime['active'] == {'runtime': 0, 'caps': 0, 'boundary': 0}
    assert ('policy', 'exit') in runtime['contexts']
    assert read(Path(read(job_file)['output_dir']) / 'summary.json')['state'] == 'failed'


def test_direct_keyboard_interrupt_does_not_join_lingering_model_thread():
    script = '''
import threading
from harnesses.refinement_bf_ablation import worker
threading.Thread(target=threading.Event().wait, daemon=False).start()
def interrupted(*args, **kwargs):
    raise KeyboardInterrupt()
worker.run = interrupted
raise SystemExit(worker.main(['--job', '/unused/offline-job.json']))
'''
    result = subprocess.run([sys.executable, '-B', '-c', script],
        cwd=Path(__file__).resolve().parents[1], timeout=5, capture_output=True, text=True)
    assert result.returncode == 130, result.stderr


def test_source_changed_during_run_fails_integrity(job_file, runtime):
    job = read(job_file)
    once = threading.Event()
    def change(kwargs):
        if not once.is_set():
            once.set()
            Path(job['candidates'][0]['proof_path']).write_text('source drift')
    runtime['during_call'] = change
    with pytest.raises(ValueError, match='hash mismatch'):
        worker.run(job_file, execute_models=True)
    summary = read(Path(job['output_dir']) / 'summary.json')
    assert summary['state'] == 'failed' and 'integrity_error' in summary


def test_keyboard_interrupt_is_persisted(job_file, runtime):
    def interrupt(kwargs):
        if kwargs['candidate_id'] == worker.CANDIDATES[0]:
            raise worker.Interrupted(signal.SIGTERM)
    runtime['during_call'] = interrupt
    with pytest.raises(worker.Interrupted):
        worker.run(job_file, execute_models=True)
    summary = read(Path(read(job_file)['output_dir']) / 'summary.json')
    assert summary['state'] == 'interrupted'


def test_source_symlink_rejected_even_with_same_hash(job_file, runtime):
    job = read(job_file)
    source = Path(job['candidates'][0]['proof_path'])
    target = source.with_name('target.md')
    source.rename(target)
    source.symlink_to(target)
    with pytest.raises(ValueError, match='symlink'):
        worker.run(job_file, execute_models=True)
    assert not runtime['servers']
