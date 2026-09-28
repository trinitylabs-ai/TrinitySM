"""Raw producer binding, isolated launch, and offline real-engine preflight."""
import hashlib
from pathlib import Path
import signal
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harnesses.block_local_completion import EXPERIMENT, PIPELINE_CONFIG, SCOPE, inputs, runner


@pytest.fixture
def source_run(tmp_path):
    root = tmp_path.resolve() / 'native_run'
    rows = []
    for number in (2, 3):
        pid = f'imo2026_p{number}'
        claim = f'Problem {number}: prove that a real square is nonnegative.'
        rows.append({'problem_id': pid, 'problem_number': number, 'problem': claim})
        inputs.write(root / 'inputs' / (pid + '.json'), {'problem_id': pid, 'problem': claim})
        phase = root / 'problems' / pid / '01_source' / f'p{number}/01_raw_lazy_enhanced_resolve'
        inputs.write(phase / 'input/problem.json', {'problem_id': pid, 'problem_number': number, 'claim': claim})
        specs = [{'candidate_id': cid, 'seed': i + 10, 'temperature': 1.0 if i < 2 else 0.7}
                 for i, cid in enumerate(inputs.CANDIDATES)]
        raw = phase / 'phase_1_raw_lazy'
        inputs.write(raw / 'manifest.json', {'schema': 'cognitive-well-v097-raw-lazy-manifest-v1',
            'problem': {'problem_id': pid, 'problem_number': number}, 'candidate_specs': specs})
        for spec in specs:
            cid = spec['candidate_id']
            directory = raw / f'p{number}/candidates' / cid
            directory.mkdir(parents=True)
            path = directory / 'draft_proof.md'
            proof = f'For lane {cid}, take a real number x.\n\nIts square is nonnegative.\n\nThis proves the claim.'
            path.write_bytes(('\n' + proof + '\n').encode())
            seed = int.from_bytes(hashlib.sha256(
                f'v048:p{number}:{cid}:{spec["seed"]}:cold_draft'.encode()).digest()[:4], 'big') or 1
            inputs.write(directory / 'cold_result.json', {'problem_id': pid, 'problem_number': number,
                **spec, 'seed': seed, 'base_portfolio_seed': spec['seed'], 'proof': proof,
                'proof_sha256': inputs.text_hash(path), 'proof_path': str(path), 'cold_generation': {'text': proof}})
            (directory / 'checked_proof.md').write_text('Later proof; must never enter this experiment.')
    inputs.write(root / 'harness_release.json', {'version': '1.7.0',
        'release_sha256': inputs.digest(inputs.RELEASE / 'release.json')})
    inputs.write(root / 'manifest.json', {'schema': 'v263_lazy_refined_to_v290_r1c2_queue_v1',
        'dry_run': False, 'problems': rows, 'seed_namespace': 'historical_seed'})
    inputs.write(root / 'grades/not_solver_input.json', {'score': 7})
    return root


def make_args(source, output, *extra):
    return runner.parser().parse_args(['run', '--source-run', str(source), '--output-dir', str(output), *extra])


def test_raw_receipts_are_used_without_later_results_or_grades(source_run, monkeypatch):
    original = Path.read_bytes
    opened = []
    def tracked(path):
        opened.append(str(path))
        assert '/grades/' not in str(path) and path.name != 'checked_proof.md'
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', tracked)
    bank = inputs.load_sources([source_run], ['imo2026_p3'])
    assert bank['source_arm'] == 'raw'
    assert len(bank['problems']) == 1
    assert all(c['selected_stage'] == 'raw' and c['proof_path'].endswith('/draft_proof.md')
               for c in bank['problems'][0]['candidates'])
    assert not any('/grades/' in p for p in opened)


@pytest.mark.parametrize('version', ['1.7.0', '1.8.0'])
def test_source_identity_records_both_pinned_releases(source_run, version):
    inputs.write(source_run / 'harness_release.json', {'version': version,
        'release_sha256': inputs.digest(inputs.RELEASE.parent / version / 'release.json')})
    bank = inputs.load_sources([source_run], ['imo2026_p2'])
    assert bank['problems'][0]['provenance']['source_release']['version'] == version


@pytest.mark.parametrize('field,value', [('proof', 'Different proof'), ('seed', 1),
                                      ('proof_path', '/elsewhere/draft_proof.md')])
def test_changed_raw_receipt_rejected(source_run, field, value):
    path = next((source_run / 'problems/imo2026_p2').rglob('cold_result.json'))
    receipt = inputs.read(path)
    receipt[field] = value
    inputs.write(path, receipt)
    with pytest.raises(ValueError):
        inputs.load_sources([source_run], ['imo2026_p2'])


def test_historical_source_requires_exact_pinned_identity(source_run):
    (version, digest), upstream = next(iter(inputs.HISTORICAL_SOURCE_RELEASES.items()))
    identity = {'version': version, 'release_sha256': digest, 'upstream': upstream}
    inputs.write(source_run / 'harness_release.json', identity)
    bank = inputs.load_sources([source_run], ['imo2026_p2'])
    assert bank['problems'][0]['provenance']['source_release'] == identity
    for changed in ({**identity, 'release_sha256': '0' * 64},
                    {**identity, 'upstream': {**upstream, 'freeze_sha256': '0' * 64}}):
        inputs.write(source_run / 'harness_release.json', changed)
        with pytest.raises(ValueError, match='Source release identity changed'):
            inputs.load_sources([source_run], ['imo2026_p2'])


def test_missing_raw_proof_does_not_substitute_checked_proof(source_run):
    next((source_run / 'problems/imo2026_p2').rglob('draft_proof.md')).unlink()
    with pytest.raises(ValueError, match='Missing'):
        inputs.load_sources([source_run], ['imo2026_p2'])


def test_snapshot_preserves_bytes_and_rejects_later_stage(source_run, tmp_path):
    bank = inputs.load_sources([source_run], ['imo2026_p2'])
    path = inputs.snapshot(bank, tmp_path.resolve() / 'inputs')
    frozen = inputs.verify_manifest(path)
    assert [Path(c['proof_path']).read_bytes() for c in bank['problems'][0]['candidates']] == [
        Path(c['proof_path']).read_bytes() for c in frozen['problems'][0]['candidates']]
    frozen['problems'][0]['candidates'][0]['selected_stage'] = 'refinement_3'
    inputs.write(path, frozen)
    with pytest.raises(ValueError, match='Only raw'):
        inputs.verify_manifest(path)


def test_plan_is_raw_only_explicit_dry_run_and_no_refinements(source_run, tmp_path):
    output = tmp_path.resolve() / 'experiment'
    plan_path = runner.create_plan(make_args(source_run, output, '--problem-id', 'imo2026_p2'))
    plan = inputs.read(plan_path)
    job = inputs.read(plan['jobs'][0]['job_path'])
    assert plan['experiment'] == job['experiment'] == EXPERIMENT
    assert plan['strategy'] == job['strategy'] == 'block'
    assert plan['processing_scope'] == job['processing_scope'] == SCOPE
    assert plan['pipeline_config'] == job['pipeline_config'] == PIPELINE_CONFIG
    assert plan['dry_run'] is job['dry_run'] is True
    assert plan['refinements_enabled'] is False
    assert plan['raw_candidates'] == 4
    assert job['runtime']['seed_namespace'] == 'block-local-raw:0:imo2026_p2'
    assert job['runtime']['qwen_endpoint'] == 'http://127.0.0.1:8027/v1'
    assert plan['repair_temperature'] == job['runtime']['repair_temperature'] == 0.7
    with pytest.raises(ValueError, match='fresh'):
        runner.create_plan(make_args(source_run, output, '--problem-id', 'imo2026_p2'))


def test_no_selection_or_ambiguous_sources_rejected(source_run, tmp_path):
    with pytest.raises(SystemExit):
        make_args(source_run, tmp_path / 'out')
    with pytest.raises(ValueError, match='Duplicate source run'):
        inputs.load_sources([source_run, source_run], ['imo2026_p2'])
    with pytest.raises(ValueError, match='not found'):
        inputs.load_sources([source_run], ['imo2026_p6'])
    with pytest.raises(ValueError, match='separate'):
        runner.create_plan(make_args(source_run, source_run / 'new-output', '--problem-id', 'imo2026_p2'))


def test_real_engine_preflight_does_not_generate_or_grade(source_run, tmp_path):
    output = tmp_path.resolve() / 'dryrun'
    result = subprocess.run([sys.executable, '-B', str(runner.ROOT / 'scripts/run_block_local_completion.py'),
        'run', '--source-run', str(source_run), '--problem-id', 'imo2026_p2', '--problem-id', 'imo2026_p3',
        '--output-dir', str(output)], cwd=runner.ROOT, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    state = inputs.read(output / 'status.json')
    assert state['state'] == 'preflight_passed' and len(state['outcomes']) == 2
    summaries = [inputs.read(row['summary_path']) for row in state['outcomes']]
    assert all(s['model_calls'] == 0 and len(s['lanes']) == 4 for s in summaries)
    assert all(lane['source_stage'] == 'raw' and lane['operation'] == 'preflight_only'
               for s in summaries for lane in s['lanes'])
    assert (output / 'REPORT.md').exists() and not (output / 'grading').exists()


def test_interrupt_stops_owned_worker_only(source_run, tmp_path, monkeypatch):
    plan_path = runner.create_plan(make_args(source_run, tmp_path.resolve() / 'interrupted', '--problem-id', 'imo2026_p2'))
    stopped = []
    class Child:
        pid = 123456
        def __init__(self, *args, **kwargs):
            assert kwargs['start_new_session'] is True
        def wait(self, timeout=None):
            raise runner.Interrupted(signal.SIGTERM)
    monkeypatch.setattr(runner.subprocess, 'Popen', Child)
    monkeypatch.setattr(runner, 'stop_child', lambda child: stopped.append(child.pid))
    with pytest.raises(runner.Interrupted):
        runner.run_plan(plan_path)
    assert stopped == [123456]
    assert inputs.read(plan_path.parent / 'status.json')['state'] == 'interrupted'


def test_low_temperature_single_run_is_recorded(source_run, tmp_path):
    path = runner.create_plan(make_args(source_run, tmp_path.resolve() / 'low', '--problem-id', 'imo2026_p2',
                                      '--repair-temperature', '0.4'))
    plan = inputs.read(path)
    assert plan['repair_temperature'] == 0.4
    assert inputs.read(plan['jobs'][0]['job_path'])['runtime']['repair_temperature'] == 0.4


def test_real_paired_preflight_runs_three_conditions_without_models(source_run, tmp_path):
    output = tmp_path.resolve() / 'paired'
    result = subprocess.run([sys.executable, '-B', str(runner.ROOT / 'scripts/run_block_local_completion.py'),
        'compare', '--source-run', str(source_run), '--problem-id', 'imo2026_p2', '--output-dir', str(output)],
        cwd=runner.ROOT, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    plan = inputs.read(output / 'pair_plan.json')
    assert [arm['repair_temperature'] for arm in plan['arms']] == [0.7, 0.4, 0.4]
    assert [arm['strategy'] for arm in plan['arms']] == ['block', 'block', 'original']
    assert inputs.read(output / 'paired_status.json')['state'] == 'preflight_passed'
    for arm in plan['arms']:
        child = inputs.read(arm['plan_path'])
        job = inputs.read(child['jobs'][0]['job_path'])
        summary = inputs.read(Path(job['output_dir']) / 'summary.json')
        assert job['runtime']['workers'] == 4
        assert job['runtime']['repair_temperature'] == arm['repair_temperature']
        assert summary['model_calls'] == 0
    assert not (output / 'grading').exists()
