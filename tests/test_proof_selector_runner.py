"""Offline input integrity and standalone proof-selector orchestration."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from harnesses.proof_selector import inputs, runner


RUN_ID = 'completed_suite'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else
                     (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    return path


def read(path):
    return json.loads(path.read_bytes())


def edit(path, change):
    value = read(path)
    change(value)
    write(path, value)


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def forbidden(*args, **kwargs):
    pytest.fail('Unexpected model or client call')


@pytest.fixture
def completed_suite(tmp_path, monkeypatch):
    root = (tmp_path / 'repository').resolve()
    jobs, outcomes = [], []
    for benchmark, count in inputs.GROUPS.items():
        ids = ([f'imo2026_p{i}' for i in range(1, count + 1)] if benchmark == 'imo2026'
               else [f'PB-{benchmark.rsplit("/", 1)[1].title()}-{i:03}' for i in range(1, count + 1)])
        base = root / 'benchmarks' / benchmark
        experiment = base / 'results' / RUN_ID
        run = experiment / 'generation/run'
        rows, lanes = [], []
        for pid in ids:
            problem = write(base / 'problems' / f'{pid}.json', {
                'problem_id': pid, 'claim': f'Prove x² ≥ 0 for real x: {pid}.',
                'reference': 'REFERENCE MUST NOT REACH THE SELECTOR',
                'review': 'PRIOR REVIEW MUST NOT REACH THE SELECTOR', 'score': 7})
            rows.append({'problem_id': pid, 'path': str(problem.relative_to(base)),
                         'sha256': sha(problem.read_bytes())})
            for cid in sorted(inputs.CANDIDATES):
                fallback = pid == 'imo2026_p1' and cid == 't07_r01'
                stage = 'lazy_checked' if fallback else 'refinement_3'
                proof_bytes = f'\r\nProof {pid}/{cid}: x² ≥ 0.\r\n  Unchanged ending. \r\n'.encode('utf-8')
                producer = write(run / 'problems' / pid / stage / cid / 'proof.txt', proof_bytes)
                receipt = write(producer.with_name('completion.json'), {
                    'state': 'completed', 'problem_id': pid, 'candidate_id': cid,
                    'stage': stage, 'returncode': 0})
                proof = write(run / 'proofs' / pid / f'{cid}.md', proof_bytes)
                lanes.append({'problem_id': pid, 'candidate_id': cid, 'proof_available': True,
                              'state': 'completed_with_fallback' if fallback else 'completed',
                              'selected_stage': stage, 'proof': str(proof.relative_to(run)),
                              'producer': str(producer.relative_to(run)),
                              'completion_record': str(receipt.relative_to(run)),
                              'sha256': sha(proof_bytes), 'proof_sha256': sha(proof_bytes.strip())})
        catalog = write(base / 'catalog.json', {'generation_inputs': {'files': rows}})
        jobs.append({'benchmark': benchmark, 'problem_ids': ids, 'inputs': rows,
                     'catalog_sha256': sha(catalog.read_bytes())})
        outcomes.append({'benchmark': benchmark, 'returncode': 0})
        write(experiment / 'experiment.json', {'run_id': RUN_ID, 'benchmark': benchmark, 'state': 'completed'})
        write(experiment / 'generation/completion.json', {'worker_exited': True, 'returncode': 0})
        write(run / 'final_results.json', {
            'state': 'completed_with_fallbacks' if benchmark == 'imo2026' else 'completed',
            'execution': {'state': 'completed', 'returncode': 0}, 'lanes': lanes})
    suite_dir = root / '.workshop/runs' / RUN_ID
    write(suite_dir / 'plan.json', {'schema': 'workshop-sampled-suite-v1', 'run_id': RUN_ID,
          'problem_count': 12, 'candidates_per_problem': 4, 'sample_seed': 1729,
          'generation_seed': 271828, 'jobs': jobs})
    write(suite_dir / 'status.json', {'state': 'completed', 'outcomes': outcomes})
    monkeypatch.setattr(runner, 'ROOT', root)
    # Relocating only fixture data should not relocate the installed selector code.
    monkeypatch.setattr(runner, 'code_identity', lambda: {'version': 'test', 'files': {}, 'protocols': {}})
    monkeypatch.setattr(runner, 'NativeBFClient', forbidden)
    return root


@pytest.fixture
def standalone(tmp_path, monkeypatch):
    root = (tmp_path / 'standalone').resolve()
    problems = []
    for pid in ['standalone-A', 'standalone-B']:
        statement = write(root / f'{pid}.json', {
            'problem_id': pid, 'statement': f'  Prove the statement for {pid}: x² ≥ 0.  ',
            'reference_solution': 'SECRET REFERENCE CONTENT', 'previous_grade': 7})
        candidates = []
        for index, cid in enumerate(['alice', 'custom-2', 'v3.lane', 'fourth_proof']):
            raw = f'\r\n  Candidate {index} for {pid}: 한글 x² ≥ 0.\r\nSecond line.  \r\n'.encode('utf-8')
            proof = write(root / pid / f'{cid}.md', raw)
            candidates.append({'candidate_id': cid, 'proof_path': str(proof.relative_to(root)),
                               'proof_file_sha256': sha(raw), 'selected_stage': 'provided_final'})
        problems.append({'problem_id': pid, 'problem_path': statement.name,
                         'problem_file_sha256': sha(statement.read_bytes()), 'candidates': candidates})
    manifest = write(root / 'manifest.json', {'schema': 'proof-selector-input-v1',
                                             'run_id': 'standalone-bank', 'problems': problems})
    monkeypatch.setattr(runner, 'code_identity', lambda: {'version': 'test', 'files': {}, 'protocols': {}})
    monkeypatch.setattr(runner, 'NativeBFClient', forbidden)
    return manifest


def experiment(root, benchmark='imo2026'):
    return root / 'benchmarks' / benchmark / 'results' / RUN_ID


def first_lane(root):
    run = experiment(root) / 'generation/run'
    return run, read(run / 'final_results.json')['lanes'][0]


def valid_selection(**kwargs):
    candidate = kwargs['candidates'][1]
    result = {'state': 'completed', 'selected_candidate_id': candidate['candidate_id'],
              'selected_proof_sha256': candidate['proof_file_sha256'],
              'selection_basis': 'best_effort_unverified', 'elapsed_seconds': 1.25}
    write(kwargs['output_dir'] / 'selection.json', result)
    return result


def test_complete_suite_preserves_all_final_lanes_and_fallback_bytes(completed_suite):
    original = snapshot(completed_suite)
    loaded = inputs.load_suite(completed_suite, RUN_ID)
    assert loaded['input_kind'] == 'completed_sampled_suite'
    assert loaded['sample_seed'] == 1729 and loaded['generation_seed'] == 271828
    assert len(loaded['problems']) == 12
    assert sum(len(problem['candidates']) for problem in loaded['problems']) == 48
    assert {problem['benchmark'] for problem in loaded['problems']} == set(inputs.GROUPS)
    for problem in loaded['problems']:
        assert 'REFERENCE' not in problem['problem'] and 'REVIEW' not in problem['problem']
        assert {c['candidate_id'] for c in problem['candidates']} == inputs.CANDIDATES
        for candidate in problem['candidates']:
            raw = Path(candidate['proof_path']).read_bytes()
            assert candidate['proof'].encode('utf-8') == raw
            assert candidate['proof_file_sha256'] == sha(raw)
    fallback = next(c for c in loaded['problems'][0]['candidates'] if c['candidate_id'] == 't07_r01')
    assert fallback['selected_stage'] == 'lazy_checked'
    inputs.verify_sources(loaded)
    assert snapshot(completed_suite) == original


@pytest.mark.parametrize('target', ['statement', 'proof', 'producer'])
def test_tampered_suite_input_fails_before_client_construction(completed_suite, target, capsys):
    run, row = first_lane(completed_suite)
    path = (completed_suite / 'benchmarks/imo2026/problems/imo2026_p1.json'
            if target == 'statement' else run / row[target])
    path.write_bytes(path.read_bytes() + b'changed')
    assert runner.main(['--run-id', RUN_ID, '--selection-id', 'bad-input']) == 1
    assert 'Selection failed: ValueError:' in capsys.readouterr().err
    assert not (completed_suite / '.workshop/selections').exists()


@pytest.mark.parametrize('damage', ['suite', 'worker', 'experiment', 'final', 'lane'])
def test_incomplete_generation_is_rejected(completed_suite, damage):
    exp = experiment(completed_suite)
    if damage == 'suite':
        edit(completed_suite / '.workshop/runs' / RUN_ID / 'status.json',
             lambda value: value.update(state='running'))
    elif damage == 'worker':
        edit(exp / 'generation/completion.json', lambda value: value.update(returncode=1))
    elif damage == 'experiment':
        edit(exp / 'experiment.json', lambda value: value.update(state='running'))
    elif damage == 'final':
        edit(exp / 'generation/run/final_results.json', lambda value: value.update(state='failed'))
    else:
        edit(exp / 'generation/run/final_results.json', lambda value: value['lanes'].pop())
    with pytest.raises(ValueError):
        inputs.load_suite(completed_suite, RUN_ID)


@pytest.mark.parametrize('target', ['proof', 'producer', 'completion_record'])
def test_suite_rejects_symlink_inputs_even_when_bytes_match(completed_suite, target):
    run, row = first_lane(completed_suite)
    path = run / row[target]
    replacement = path.with_name('same-bytes' + path.suffix)
    path.rename(replacement)
    path.symlink_to(replacement)
    with pytest.raises(ValueError, match='Symlink'):
        inputs.load_suite(completed_suite, RUN_ID)


def test_problem_filter_is_applied_only_after_whole_suite_validation(completed_suite):
    final = experiment(completed_suite, 'imo-proofbench/advanced') / 'generation/run/final_results.json'
    edit(final, lambda value: value['lanes'].pop())
    with pytest.raises(ValueError, match='coverage'):
        inputs.load_suite(completed_suite, RUN_ID, requested=['imo2026_p1'])


def test_standalone_manifest_supports_arbitrary_ids_and_exact_utf8_crlf(standalone):
    loaded = inputs.load_manifest(standalone)
    assert loaded['input_kind'] == 'standalone_manifest'
    assert len(loaded['problems']) == 2
    for problem in loaded['problems']:
        assert 'SECRET REFERENCE' not in problem['problem']
        assert problem['problem'].startswith('Prove the statement')
        assert [c['candidate_id'] for c in problem['candidates']] == [
            'alice', 'custom-2', 'v3.lane', 'fourth_proof']
        for candidate in problem['candidates']:
            assert candidate['proof'].encode('utf-8') == Path(candidate['proof_path']).read_bytes()
            assert '\r\n' in candidate['proof'] and '한글' in candidate['proof']
            assert candidate['proof_file_sha256'] == sha(candidate['proof'].encode('utf-8'))


@pytest.mark.parametrize('duplicate', ['problem', 'candidate'])
def test_standalone_duplicate_ids_are_rejected(standalone, duplicate):
    manifest = read(standalone)
    if duplicate == 'problem':
        manifest['problems'].append(manifest['problems'][0])
    else:
        candidates = manifest['problems'][0]['candidates']
        candidates[1]['candidate_id'] = candidates[0]['candidate_id']
    write(standalone, manifest)
    with pytest.raises(ValueError, match='[Dd]uplicate'):
        inputs.load_manifest(standalone)


@pytest.mark.parametrize('path_kind', ['escape', 'symlink'])
def test_standalone_rejects_escaped_or_symlinked_proofs(standalone, path_kind):
    manifest = read(standalone)
    candidate = manifest['problems'][0]['candidates'][0]
    original = standalone.parent / candidate['proof_path']
    if path_kind == 'escape':
        external = write(standalone.parent.parent / 'external.md', original.read_bytes())
        candidate['proof_path'] = '../' + external.name
    else:
        destination = original.with_name('original.md')
        original.rename(destination)
        original.symlink_to(destination)
    write(standalone, manifest)
    with pytest.raises(ValueError, match='escapes|Symlink'):
        inputs.load_manifest(standalone)


def test_manifest_filter_does_not_hide_other_corrupt_inputs(standalone):
    manifest = read(standalone)
    path = standalone.parent / manifest['problems'][1]['candidates'][0]['proof_path']
    path.write_bytes(b'Tampered proof')
    with pytest.raises(ValueError, match='hash mismatch'):
        inputs.load_manifest(standalone, requested=['standalone-A'])


@pytest.mark.parametrize('requested', [['missing'], ['standalone-A', 'standalone-A']])
def test_manifest_rejects_invalid_requested_problem_ids(standalone, requested):
    with pytest.raises(ValueError, match='Unknown|Duplicate'):
        inputs.load_manifest(standalone, requested=requested)


def test_dry_run_validates_suite_without_writes_or_client_calls(completed_suite, capsys):
    original = snapshot(completed_suite)
    assert runner.main(['--run-id', RUN_ID, '--selection-id', 'dry-test', '--dry-run',
                        '--problem-id', 'imo2026_p1', '--selection-seed', '0']) == 0
    report = json.loads(capsys.readouterr().out)
    assert report['dry_run'] is True and report['selection_seed'] == 0
    assert report['problem_ids'] == ['imo2026_p1']
    assert report['bf_policy'] == runner.POLICY
    assert report['configuration']['bf_extensions'] == 1
    assert report['configuration']['thinking_budget'] == 65536
    assert report['configuration']['answer_max_tokens'] == 8192
    assert 'gemma_max_tokens' not in report['configuration']
    assert 'qwen_max_tokens' not in report['configuration']
    assert snapshot(completed_suite) == original


def test_standalone_cli_dry_run_records_random_zero_without_writes(standalone, tmp_path, monkeypatch, capsys):
    original = snapshot(standalone.parent)
    draws = []
    monkeypatch.setattr(runner.secrets, 'randbits', lambda bits: draws.append(bits) or 0)
    output = tmp_path / 'selection'
    assert runner.main(['--input-manifest', str(standalone), '--output-dir', str(output),
                        '--random-selection-seed', '--dry-run']) == 0
    assert json.loads(capsys.readouterr().out)['selection_seed'] == 0
    assert draws == [32]
    assert not output.exists()
    assert snapshot(standalone.parent) == original


@pytest.mark.parametrize('options,extensions', [([], 1), (['--bf-extensions', '0'], 0)])
def test_cli_records_native_bf_policy_and_token_budgets_in_plan(
        standalone, tmp_path, monkeypatch, options, extensions):
    from harnesses.proof_selector.client import POLICY
    configurations = []
    monkeypatch.setattr(runner, 'NativeBFClient', lambda **kw: configurations.append(kw) or object())
    monkeypatch.setattr(runner, 'select_problem', valid_selection)
    output = tmp_path.resolve() / 'selection'
    assert runner.main(['--input-manifest', str(standalone), '--output-dir', str(output),
                        '--problem-id', 'standalone-A', *options]) == 0
    assert len(configurations) == 1
    plan = read(output / 'plan.json')
    assert plan['bf_policy'] == POLICY
    assert plan['configuration'] == configurations[0]
    assert plan['configuration']['bf_extensions'] == extensions
    assert plan['configuration']['thinking_budget'] == 65536
    assert plan['configuration']['answer_max_tokens'] == 8192
    assert 'gemma_max_tokens' not in plan['configuration'] and 'qwen_max_tokens' not in plan['configuration']


@pytest.mark.parametrize('option', ['--gemma-max-tokens', '--qwen-max-tokens'])
def test_cli_rejects_obsolete_chat_bf_options_before_loading_inputs(monkeypatch, capsys, option):
    monkeypatch.setattr(inputs, 'load_manifest', forbidden)
    with pytest.raises(SystemExit) as error:
        runner.main(['--input-manifest', 'unused.json', option, '100'])
    assert error.value.code == 2
    assert 'unrecognized arguments:' in capsys.readouterr().err


def test_execution_exports_byte_identical_candidates_and_does_not_modify_sources(
        standalone, tmp_path, monkeypatch):
    loaded = inputs.load_manifest(standalone)
    original = snapshot(standalone.parent)
    calls = []

    def select(**kwargs):
        calls.append(kwargs)
        assert 'SECRET REFERENCE' not in kwargs['problem']
        assert kwargs['seed'] == 1729 and kwargs['max_rounds'] == 2
        return valid_selection(**kwargs)

    monkeypatch.setattr(runner, 'select_problem', select)
    output = tmp_path.resolve() / 'selection'
    state = runner.execute(loaded, output, object(), seed=1729, max_rounds=2,
                           configuration={'offline_test': True})
    assert state['state'] == 'completed' and len(calls) == 2
    saved = read(output / 'status.json')
    assert saved['state'] == 'completed' and len(saved['outcomes']) == 2
    plan = read(output / 'plan.json')
    assert plan['external_grading'] is plan['proof_modification'] is False
    assert plan['inputs']['source_hashes'] == loaded['source_hashes']
    assert plan['configuration'] == {'offline_test': True}
    assert all('problem' not in problem for problem in plan['inputs']['problems'])
    assert all('proof' not in candidate for problem in plan['inputs']['problems']
               for candidate in problem['candidates'])
    for problem, outcome in zip(loaded['problems'], saved['outcomes']):
        directory = output / 'problems' / problem['problem_id']
        selected = next(c for c in problem['candidates'] if c['candidate_id'] == outcome['selected_candidate_id'])
        assert (directory / 'selected_proof.md').read_bytes() == Path(selected['proof_path']).read_bytes()
        assert sha((directory / 'selected_proof.md').read_bytes()) == outcome['selected_proof_sha256']
        assert read(directory / 'selection.json')['selected_proof_sha256'] == outcome['selected_proof_sha256']
        for candidate in problem['candidates']:
            assert (directory / 'inputs' / (candidate['candidate_id'] + '.md')).read_bytes() == Path(candidate['proof_path']).read_bytes()
    assert 'State: **completed**' in (output / 'REPORT.md').read_text()
    assert snapshot(standalone.parent) == original


@pytest.mark.parametrize('occupied', ['directory', 'symlink'])
def test_output_collision_rejected_before_selector_and_preserves_existing_data(
        standalone, tmp_path, monkeypatch, occupied):
    loaded = inputs.load_manifest(standalone)
    output = tmp_path.resolve() / 'occupied'
    original = write(tmp_path.resolve() / 'old-selection/keep.txt', b'Keep old evidence')
    if occupied == 'directory':
        output.mkdir()
        write(output / 'keep.txt', original.read_bytes())
    else:
        output.symlink_to(original.parent, target_is_directory=True)
    before = snapshot(original.parent)
    monkeypatch.setattr(runner, 'select_problem', forbidden)
    with pytest.raises(ValueError, match='already exists'):
        runner.execute(loaded, output, object(), seed=0, max_rounds=1)
    assert snapshot(original.parent) == before


def test_changed_source_before_execution_fails_without_output(standalone, tmp_path, monkeypatch):
    loaded = inputs.load_manifest(standalone)
    Path(loaded['problems'][0]['candidates'][0]['proof_path']).write_bytes(b'Changed after load')
    output = tmp_path.resolve() / 'selection'
    monkeypatch.setattr(runner, 'select_problem', forbidden)
    with pytest.raises(ValueError, match='source changed'):
        runner.execute(loaded, output, object(), seed=0, max_rounds=1)
    assert not output.exists()


@pytest.mark.parametrize('failure', ['hash', 'source_drift', 'interrupt', 'error'])
def test_execution_failure_never_labels_partial_suite_success(standalone, tmp_path, monkeypatch, failure):
    loaded = inputs.load_manifest(standalone)
    output = tmp_path.resolve() / 'selection'
    calls = []

    def select(**kwargs):
        calls.append(kwargs['problem_id'])
        if len(calls) == 1:
            return valid_selection(**kwargs)
        if failure == 'interrupt':
            raise runner.SelectionInterrupted(signal.SIGTERM)
        if failure == 'error':
            raise RuntimeError('Synthetic model failure')
        result = valid_selection(**kwargs)
        if failure == 'hash':
            result['selected_proof_sha256'] = '0' * 64
        else:
            Path(kwargs['candidates'][0]['proof_path']).write_bytes(b'Changed while selecting')
        return result

    monkeypatch.setattr(runner, 'select_problem', select)
    expected_error = (runner.SelectionInterrupted if failure == 'interrupt' else
                      RuntimeError if failure == 'error' else ValueError)
    with pytest.raises(expected_error):
        runner.execute(loaded, output, object(), seed=0, max_rounds=1)
    status = read(output / 'status.json')
    expected_state = 'interrupted' if failure == 'interrupt' else 'failed'
    assert status['state'] == expected_state
    assert [row['state'] for row in status['outcomes']] == ['completed', expected_state]
    assert len(calls) == 2 and 'active_problem' not in status
    assert 'finished_at' in status
    assert not (output / 'problems/standalone-B/selected_proof.md').exists()
    report = (output / 'REPORT.md').read_text()
    assert f'State: **{expected_state}**' in report and 'State: **completed**' not in report


def test_cli_interrupt_restores_signal_handlers_and_returns_signal_status(standalone, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'NativeBFClient', lambda **kw: object())
    monkeypatch.setattr(runner, 'select_problem', lambda **kw: (_ for _ in ()).throw(
        runner.SelectionInterrupted(signal.SIGTERM)))
    previous = {s: signal.getsignal(s) for s in [signal.SIGINT, signal.SIGTERM]}
    output = tmp_path.resolve() / 'selection'
    assert runner.main(['--input-manifest', str(standalone), '--output-dir', str(output)]) == 143
    assert read(output / 'status.json')['state'] == 'interrupted'
    for signum, handler in previous.items():
        assert signal.getsignal(signum) == handler


def test_cli_help_imports_no_legacy_runtime_or_process_monkeypatches():
    code = '''import runpy, sys, urllib.request
before_open = urllib.request.urlopen
before_argv = sys.argv
sys.argv = ['select_proofs.py', '--help']
try:
    runpy.run_path('scripts/select_proofs.py', run_name='__main__')
except SystemExit as error:
    assert error.code == 0
assert not [name for name in sys.modules if name.startswith('cognitive_well_harness')]
assert not [name for name in sys.modules if name.startswith('harnesses.proof_workshop')]
assert not [name for name in sys.modules if name.startswith('harnesses.imo_proof_pipeline')]
assert urllib.request.urlopen is before_open
print('ISOLATED_SELECTOR_IMPORT_OK')
'''
    result = subprocess.run([sys.executable, '-B', '-c', code], cwd=REPO,
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert '--input-manifest' in result.stdout and '--random-selection-seed' in result.stdout
    assert 'ISOLATED_SELECTOR_IMPORT_OK' in result.stdout


@pytest.mark.skipif(sys.platform != 'darwin', reason='macOS /tmp is the trusted /private/tmp alias')
def test_manifest_accepts_macos_tmp_alias_without_accepting_manifest_symlink(standalone):
    with tempfile.TemporaryDirectory(prefix='selector-manifest-', dir='/private/tmp') as directory:
        canonical = Path(directory)
        shutil.copytree(standalone.parent, canonical / 'bank')
        alias = Path('/tmp') / canonical.name / 'bank/manifest.json'
        loaded = inputs.load_manifest(alias)
        assert loaded['run_id'] == 'standalone-bank'
        assert len(loaded['problems']) == 2
        inputs.verify_sources(loaded)
        symlink = alias.with_name('linked-manifest.json')
        symlink.symlink_to(alias)
        with pytest.raises(ValueError, match='Symlink'):
            inputs.load_manifest(symlink)


def test_parent_symlink_drift_during_selection_fails_closed(standalone, tmp_path, monkeypatch):
    loaded = inputs.load_manifest(standalone)
    output = tmp_path.resolve() / 'selection'
    calls = []

    def select(**kwargs):
        calls.append(kwargs['problem_id'])
        parent = Path(kwargs['candidates'][0]['proof_path']).parent
        moved = tmp_path.resolve() / 'moved-proof-directory'
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
        return valid_selection(**kwargs)

    monkeypatch.setattr(runner, 'select_problem', select)
    with pytest.raises(ValueError, match='source changed'):
        runner.execute(loaded, output, object(), seed=0, max_rounds=1)
    assert calls == ['standalone-A']
    state = read(output / 'status.json')
    assert state['state'] == 'failed'
    assert state['outcomes'] == [{'problem_id': 'standalone-A', 'state': 'failed'}]
    assert not (output / 'problems/standalone-A/selected_proof.md').exists()


def test_real_runner_engine_and_native_bf_client_select_four_proofs_end_to_end(
        standalone, tmp_path, monkeypatch):
    """Exercise actual HTTP when allowed, otherwise replace only the transport seam."""
    import errno
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading

    from harnesses.proof_selector import protocols
    from harnesses.proof_selector.client import NativeBFClient, MARKERS

    # Share exact tokenization and protocol-response builders with their focused
    # tests; no client.call, engine, protocol parser, or runner is replaced here.
    def fixtures(name, filename):
        spec = importlib.util.spec_from_file_location(name, REPO / 'tests' / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    native_fixtures = fixtures('selector_integration_native_fixtures', 'test_proof_selector_client.py')
    engine_fixtures = fixtures('selector_integration_engine_fixtures', 'test_proof_selector.py')
    systems = {protocols.reviewer(i).SYSTEM_PROMPT: f'reviewer_{i}' for i in (1, 2, 3)}
    systems.update({protocols.fusion().SYSTEM_PROMPT: 'fusion',
                    protocols.ACCEPTANCE_SYSTEM: 'acceptance',
                    protocols.COMPARE_SYSTEM: 'comparison'})

    class VLLM(native_fixtures.Server):
        def __init__(self):
            super().__init__([])
            self.roles = []
            self.phase = None

        def post(self, url, payload):
            if url.endswith('/tokenize') and 'messages' in payload:
                self.role = systems[payload['messages'][0]['content']]
                self.roles.append(self.role)
                self.phase = 0
                assert 'SECRET REFERENCE CONTENT' not in payload['messages'][1]['content']
            if url.endswith('/v1/completions'):
                family = 'gemma' if 'gemma' in payload['model'] else 'qwen'
                if self.phase < 2:
                    answer = ('First independent thought.' if self.phase == 0 else
                              'Continue checking the obligation.') + MARKERS[family]['end']
                else:
                    assert self.phase == 2
                    answer = engine_fixtures.default_response({'role': self.role}) + MARKERS[family]['turn_end']
                self.outputs.append((answer, 'stop'))
                self.phase += 1
            return super().post(url, payload)

    backend = VLLM()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                body = backend.post('http://127.0.0.1' + self.path, payload).encode('utf-8')
                self.send_response(200)
            except Exception as error:
                body = json.dumps({'error': f'{type(error).__name__}: {error}'}).encode('utf-8')
                self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *unused):
            pass

    server, thread = None, None
    try:
        try:
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        except OSError as error:
            if error.errno not in (errno.EACCES, errno.EPERM):
                raise
        endpoint = f'http://127.0.0.1:{server.server_port}/v1' if server else 'http://127.0.0.1:8030/v1'
        if server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
        client = NativeBFClient(gemma_endpoint=endpoint, qwen_endpoint=endpoint,
                                thinking_budget=200, answer_max_tokens=8192,
                                max_input_tokens=100000, max_continuation_input_tokens=120000,
                                attempts=1, bf_extensions=1)
        if server is None:
            monkeypatch.setattr(client, '_http_post', backend.post)
        loaded = inputs.load_manifest(standalone, requested=['standalone-A'])
        original = snapshot(standalone.parent)
        output = tmp_path.resolve() / 'native-selection'
        state = runner.execute(loaded, output, client, seed=0, max_rounds=1)
    finally:
        if server:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    assert state['state'] == 'completed'
    directory = output / 'problems/standalone-A'
    selected = read(directory / 'selection.json')
    assert selected['state'] == 'completed' and selected['selection_basis'] == 'audited_acceptance'
    assert len(selected['assessments']) == 4 and len(selected['comparisons']) == 3
    assert all(a['audited_acceptance'] for a in selected['assessments'])
    assert selected['mathematical_correctness_verified'] is selected['proof_modified'] is False
    assert selected['usage']['calls'] == 26 and selected['usage']['physical_requests'] == 78
    assert all(backend.roles.count(role) == 4 for role in ['reviewer_1', 'reviewer_2', 'reviewer_3', 'fusion', 'acceptance'])
    assert backend.roles.count('comparison') == 6
    candidate = next(c for c in loaded['problems'][0]['candidates']
                     if c['candidate_id'] == selected['selected_candidate_id'])
    assert (directory / 'selected_proof.md').read_bytes() == Path(candidate['proof_path']).read_bytes()
    assert sha((directory / 'selected_proof.md').read_bytes()) == selected['selected_proof_sha256']
    assert snapshot(standalone.parent) == original
    results = list(directory.rglob('result.json'))
    assert len(results) == 26
    for path in results:
        result = read(path)
        assert result['parsed']['valid'] is True
        assert result['policy'] == runner.POLICY
        assert result['actual_bf_extensions'] == 1 and len(result['usage']) == 3
        assert (path.parent / 'attempt_1/tokenizer_provenance.json').is_file()
    assert len(backend.completions) == 78
    for index, role in enumerate(backend.roles):
        initial, continued, answer = backend.completions[index * 3:index * 3 + 3]
        family = 'gemma' if 'gemma' in initial['model'] else 'qwen'
        start = backend.decode(initial['prompt'])
        middle = backend.decode(continued['prompt'])
        final = backend.decode(answer['prompt'])
        assert start.endswith(MARKERS[family]['open'])
        assert middle == start + 'First independent thought.\n\n' + protocols.CONTINUATIONS[role].strip() + '\n'
        assert final == middle + 'Continue checking the obligation.' + MARKERS[family]['end'] + '\n\n'
        assert len({request['seed'] for request in [initial, continued, answer]}) == 3


@pytest.fixture
def published_bank(tmp_path):
    root = (tmp_path / 'published-repository').resolve()
    public = root / 'docs/public_release'
    base = root / 'benchmarks/imo2026'
    statements, lanes = [], []
    for number in range(1, 7):
        pid = f'imo2026_p{number}'
        statement = write(base / 'problems' / f'{pid}.json', {
            'problem_id': pid, 'claim': f'Prove the statement {pid}: x² ≥ 0.',
            'reference_solution': 'SECRET PUBLISHED REFERENCE'})
        statements.append({'problem_id': pid, 'path': str(statement.relative_to(base)),
                           'sha256': sha(statement.read_bytes())})
        for cid in sorted(inputs.CANDIDATES):
            raw = f'\r\nPublished proof {pid}/{cid}: 한글 x² ≥ 0.\r\n'.encode('utf-8')
            proof = write(public / 'evidence/proofs' / f'{sha(raw)}.md', raw)
            fallback = number == 1 and cid == 't10_r02'
            lanes.append({'benchmark': 'IMO 2026', 'problem_id': pid, 'candidate': cid,
                          'included': True, 'c3_generation_state': 'IGNORED_GENERATION_METADATA',
                          'baseline': {'checkpoint': 'R1-C1' if fallback else 'R1-C3',
                                       'proof': str(proof.relative_to(public)),
                                       'proof_sha256': sha(raw), 'score': 'SECRET PUBLISHED SCORE',
                                       'grade': 'evidence/grades/DO_NOT_OPEN.json'},
                          'with_tools': {'proof': '/DO_NOT_OPEN_TOOL_PROOF',
                                         'score': 'SECRET TOOL SCORE'}})
    write(base / 'catalog.json', {'benchmark_id': 'imo2026',
          'generation_inputs': {'statement_only': True, 'count': 6, 'files': list(reversed(statements))}})
    lanes.reverse()
    lanes.append({'benchmark': 'Advanced', 'problem_id': 'ignored', 'candidate': 'invalid',
                  'baseline': None})
    write(public / 'score_snapshot.json', {'schema': 'public-release-evaluation-snapshot-v5',
          'lanes': lanes, 'grading_schemes': 'SECRET GRADING METADATA',
          'source_reports': [{'path': '/DO_NOT_OPEN_SOURCE_REPORT'}]})
    return root


def test_actual_published_imo_bank_loads_only_statements_and_24_baseline_proofs(monkeypatch):
    original_read = Path.read_bytes
    seen = set()
    public = REPO / 'docs/public_release'
    problem_dir = REPO / 'benchmarks/imo2026/problems'
    allowed_files = {public / 'score_snapshot.json', REPO / 'benchmarks/imo2026/catalog.json'}

    def allowed_read(path):
        assert path in allowed_files or path.parent in {public / 'evidence/proofs', problem_dir}, path
        seen.add(path)
        return original_read(path)

    monkeypatch.setattr(Path, 'read_bytes', allowed_read)
    loaded = inputs.load_published_imo(REPO)
    assert loaded['run_id'] == loaded['input_kind'] == 'published_imo2026_baseline'
    assert [p['problem_id'] for p in loaded['problems']] == [f'imo2026_p{i}' for i in range(1, 7)]
    candidates = [c for p in loaded['problems'] for c in p['candidates']]
    assert len(candidates) == 24
    assert sum(c['selected_stage'] == 'refinement_3' for c in candidates) == 22
    assert sum(c['selected_stage'] == 'refinement_1' for c in candidates) == 2
    for candidate in candidates:
        assert set(candidate) == {'candidate_id', 'proof', 'proof_path', 'proof_file_sha256', 'selected_stage'}
        assert sha(candidate['proof'].encode('utf-8')) == candidate['proof_file_sha256']
    assert set(loaded['source_hashes']) == {str(path) for path in seen}
    inputs.verify_sources(loaded)


def test_published_bank_ignores_scores_tools_and_grades_and_orders_inputs_stably(published_bank):
    before = snapshot(published_bank)
    loaded = inputs.load_published_imo(published_bank)
    assert [p['problem_id'] for p in loaded['problems']] == [f'imo2026_p{i}' for i in range(1, 7)]
    for problem in loaded['problems']:
        assert [c['candidate_id'] for c in problem['candidates']] == sorted(inputs.CANDIDATES)
        assert 'SECRET' not in problem['problem']
        for candidate in problem['candidates']:
            assert candidate['proof'].encode('utf-8') == Path(candidate['proof_path']).read_bytes()
            assert '\r\n' in candidate['proof']
    assert 'SECRET' not in json.dumps(loaded)
    fallback = next(c for c in loaded['problems'][0]['candidates'] if c['candidate_id'] == 't10_r02')
    assert fallback['selected_stage'] == 'refinement_1'
    assert snapshot(published_bank) == before


@pytest.mark.parametrize('damage', ['missing_lane', 'duplicate_lane', 'wrong_stage', 'catalog_duplicate',
                                   'statement_hash', 'proof_bytes', 'proof_escape', 'proof_symlink'])
def test_published_bank_rejects_partial_or_tampered_inputs_before_filtering(published_bank, damage):
    public = published_bank / 'docs/public_release'
    snapshot_path = public / 'score_snapshot.json'
    data = read(snapshot_path)
    # Damage P6 while requesting only P1; no incomplete input may be hidden by filtering.
    lane = next(row for row in data['lanes'] if row['problem_id'] == 'imo2026_p6')
    baseline = lane['baseline']
    if damage == 'missing_lane':
        data['lanes'].remove(lane)
    elif damage == 'duplicate_lane':
        another = next(row for row in data['lanes'] if row['problem_id'] == 'imo2026_p6' and row is not lane)
        lane['candidate'] = another['candidate']
    elif damage == 'wrong_stage':
        baseline['checkpoint'] = 'tool_rewrite'
    elif damage == 'catalog_duplicate':
        catalog_path = published_bank / 'benchmarks/imo2026/catalog.json'
        catalog = read(catalog_path)
        rows = catalog['generation_inputs']['files']
        rows[0]['problem_id'] = rows[1]['problem_id']
        write(catalog_path, catalog)
    elif damage == 'statement_hash':
        path = published_bank / 'benchmarks/imo2026/problems/imo2026_p6.json'
        path.write_bytes(path.read_bytes() + b' ')
    elif damage == 'proof_bytes':
        (public / baseline['proof']).write_bytes(b'Tampered baseline proof')
    elif damage == 'proof_escape':
        external = write(public / 'evidence/grades/disguised.md', (public / baseline['proof']).read_bytes())
        baseline['proof'] = str(external.relative_to(public))
    elif damage == 'proof_symlink':
        path = public / baseline['proof']
        moved = path.with_name('moved-' + path.name)
        path.rename(moved)
        path.symlink_to(moved)
    write(snapshot_path, data)
    with pytest.raises(ValueError):
        inputs.load_published_imo(published_bank, requested=['imo2026_p1'])
