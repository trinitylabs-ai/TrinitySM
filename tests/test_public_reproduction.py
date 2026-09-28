"""Public orchestration and local-serving contracts, without model calls."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pipeline = load('workshop_pipeline', 'harnesses/proof_workshop/pipeline.py')
serve = load('workshop_serve', 'scripts/serve_models.py')
reproduce = load('workshop_reproduce', 'scripts/reproduce.py')


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


@pytest.mark.parametrize('model', ('gemma', 'qwen'))
def test_serving_pins_profile_and_offline_model_loading(tmp_path, model):
    command, environment, checkpoints = serve.plan(model, tmp_path, 0)
    catalog = json.loads((ROOT / 'configs/workshop_models.json').read_text())
    assert checkpoints[0].name == catalog['models'][model]['revision']
    spec = json.loads(command[command.index('--speculative-config') + 1])
    assert spec['method'] == 'mtp' and spec['num_speculative_tokens'] == 4
    assert command[command.index('--dtype') + 1] == 'bfloat16'
    assert command[command.index('--host') + 1] == '127.0.0.1'
    assert environment['HF_HUB_OFFLINE'] == environment['TRANSFORMERS_OFFLINE'] == '1'
    assert len(checkpoints) == (2 if model == 'gemma' else 1)
    if model == 'gemma':
        assert Path(spec['model']).name == catalog['models']['gemma_assistant']['revision']


def test_offline_report_only_invokes_saved_evidence_verifier(monkeypatch):
    calls = []
    monkeypatch.setattr(reproduce.subprocess, 'run', lambda command, **kw: calls.append(command))
    reproduce.offline()
    assert calls == [[sys.executable, '-B', str(ROOT / 'docs/public_release/verify_scores.py')]]


@pytest.mark.parametrize('seed', (None, 0, 123456789, 0xFFFFFFFF))
def test_generation_seed_forwarding_preserves_default_when_omitted(tmp_path, monkeypatch, seed):
    solver = tmp_path / 'python'
    solver.touch()
    args = SimpleNamespace(run_id='seed-check', solver_python=solver,
                           benchmark='imo-proofbench/basic', problem_id=['PB-Basic-001'],
                           release='1.7.0', dry_run=True)
    if seed is not None:
        args.generation_seed = seed
    calls = []
    monkeypatch.setattr(reproduce.subprocess, 'run', lambda command, **kw: calls.append(command))
    reproduce.generate(args)
    expected = [str(solver.resolve()), '-B', str(ROOT / 'benchmarks/run_experiment.py'),
                '--benchmark', args.benchmark, '--run-id', args.run_id, '--release', args.release,
                '--solver-python', str(solver.resolve()), '--gemma-port', '8030', '--qwen-port', '8027']
    if seed is not None:
        expected += ['--raw-seed-offset', str(seed), '--seed-namespace', f'workshop-generation:{seed}']
    expected += ['--problem-id', 'PB-Basic-001', '--dry-run']
    assert calls == [expected]


def test_generation_preserves_virtual_environment_interpreter_symlink(tmp_path, monkeypatch):
    base_python = tmp_path / 'base-python'
    base_python.touch()
    solver = tmp_path / '.venv-solver/bin/python'
    solver.parent.mkdir(parents=True)
    solver.symlink_to(base_python)
    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(run_id='venv-check', solver_python=Path('.venv-solver/bin/python'),
                           benchmark='imo-proofbench/basic', problem_id=None,
                           release='1.7.0', dry_run=True)
    calls = []
    monkeypatch.setattr(reproduce.subprocess, 'run', lambda command, **kw: calls.append(command))
    reproduce.generate(args)
    assert len(calls) == 1
    command = calls[0]
    assert command[0] == str(solver)
    assert command[command.index('--solver-python') + 1] == str(solver)
    assert str(base_python) not in command


def test_random_generation_seed_drawn_once_and_shared_across_benchmarks(tmp_path, monkeypatch, capsys):
    solver = tmp_path / 'python'
    solver.touch()
    args = SimpleNamespace(run_id='random-check', solver_python=solver,
                           benchmark='all', problem_id=None, release='1.7.0',
                           dry_run=True, generation_seed=None, random_generation_seed=True)
    draws = []
    def random_seed(bits):
        draws.append(bits)
        return 3456789012
    monkeypatch.setattr(reproduce.secrets, 'randbits', random_seed)
    calls = []
    monkeypatch.setattr(reproduce.subprocess, 'run', lambda command, **kw: calls.append(command))
    reproduce.generate(args)
    assert draws == [32]
    assert len(calls) == len(reproduce.BENCHMARKS)
    for command, group in zip(calls, reproduce.BENCHMARKS):
        assert command[command.index('--benchmark') + 1] == group
        assert command[command.index('--raw-seed-offset') + 1] == '3456789012'
        assert command[command.index('--seed-namespace') + 1] == 'workshop-generation:3456789012'
    assert 'Generation seed: 3456789012' in capsys.readouterr().out


@pytest.mark.parametrize('seed', ('-1', '4294967296', 'not-an-integer'))
def test_cli_rejects_invalid_generation_seed_before_execution(monkeypatch, capsys, seed):
    monkeypatch.setattr(sys, 'argv', ['reproduce.py', 'generate', '--generation-seed', seed])
    monkeypatch.setattr(reproduce, 'generate', lambda *a: pytest.fail('Generation started'))
    with pytest.raises(SystemExit) as error:
        reproduce.main()
    assert error.value.code == 2
    assert 'Generation seed must be an integer from 0 to 4294967295' in capsys.readouterr().err


@pytest.mark.parametrize('mode', ([], ['report']))
@pytest.mark.parametrize('options', (['--generation-seed', '0'], ['--random-generation-seed']))
def test_cli_rejects_generation_seed_options_in_report_mode(monkeypatch, capsys, mode, options):
    monkeypatch.setattr(sys, 'argv', ['reproduce.py', *mode, *options])
    monkeypatch.setattr(reproduce, 'offline', lambda: pytest.fail('Offline verification started'))
    with pytest.raises(SystemExit) as error:
        reproduce.main()
    assert error.value.code == 2
    assert 'Generation options require generate mode' in capsys.readouterr().err


def test_cli_rejects_explicit_and_random_generation_seed_together(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['reproduce.py', 'generate', '--generation-seed', '0',
                                   '--random-generation-seed'])
    monkeypatch.setattr(reproduce, 'generate', lambda *a: pytest.fail('Generation started'))
    with pytest.raises(SystemExit) as error:
        reproduce.main()
    assert error.value.code == 2
    assert 'not allowed with argument --generation-seed' in capsys.readouterr().err


@pytest.mark.parametrize('dry,core_code,expected_final', [(False, 0, True), (True, 0, False), (False, 1, True), (True, 1, False)])
def test_complete_run_collects_after_failure_without_starting_more_models(tmp_path, monkeypatch, dry, core_code, expected_final):
    output = tmp_path / 'run'
    def core(command, **kwargs):
        output.mkdir()
        assert '--release' in command and command[command.index('--release') + 1] == '1.12.0'
        return core_code
    monkeypatch.setattr(pipeline, 'run_process', core)
    called = []
    monkeypatch.setattr(pipeline, 'finalize', lambda *a, **kw: called.append(kw) or 0)
    code = pipeline.main(['--output-dir', str(output), '--problem-dir', str(tmp_path),
                          '--dry-run' if dry else '--execute-models'])
    assert bool(called) == expected_final
    assert code == core_code
    if called:
        assert called[0]['execute'] == (core_code == 0)
        assert called[0]['execution']['returncode'] == core_code
    if dry and not core_code:
        receipt = json.loads((output / 'full_pipeline_preflight.json').read_text())
        assert receipt['model_calls'] == 0 and receipt['terminal_stage'] == 'refinement_3'


@pytest.mark.parametrize('failure', (False, True))
def test_final_proof_exports_second_pass_when_third_pass_fails(tmp_path, monkeypatch, failure):
    source = tmp_path / 'problems/synthetic/02_r1_cycles'
    candidates = ['a', 'b', 'c', 'd']
    write(source / 'manifest.json', {'problem_id': 'synthetic', 'candidate_ids': candidates})
    proofs = []
    for candidate in candidates:
        path = source / (candidate + '.md')
        path.write_text('Completed second-pass proof for ' + candidate)
        proofs.append({'candidate_id': candidate, 'proof_path': str(path), 'proof_sha256': pipeline.proof_hash(path)})
    write(source / 'score_targets.json', {'checkpoints': [{'checkpoint': 'R1-C2', 'proofs': proofs}]})
    def finish(run_root, source, candidate, problem_id, release, python):
        if failure and candidate == 'd':
            raise ValueError('Third pass did not complete')
        proof = tmp_path / 'finalization/synthetic' / candidate / 'proof.md'
        proof.parent.mkdir(parents=True)
        proof.write_text('Completed third-pass proof for ' + candidate)
        return {'candidate_id': candidate, 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
    monkeypatch.setattr(pipeline, 'finish_lane', finish)
    assert pipeline.finalize(tmp_path, '1.7.0') == 0
    result = json.loads((tmp_path / 'final_results.json').read_text())
    assert result['completed_proofs'] == 4
    assert result['project_name'] == 'TrinitySM'
    assert result['project_version'] == '0.1.0-rc.1'
    assert result['implementation_release'] == '1.7.0'
    assert result['fully_refined_proofs'] == 4 - int(failure)
    assert result['fallback_proofs'] == int(failure)
    assert result['state'] == ('completed_with_fallbacks' if failure else 'completed')
    assert result['terminal_stage'] == 'refinement_3'
    assert result['experimental_tools'] is result['external_grading'] is False
    assert (tmp_path / 'proofs/synthetic/d.md').exists()
    if failure:
        row = next(row for row in result['lanes'] if row['candidate_id'] == 'd')
        assert row['state'] == 'completed_with_fallback' and row['selected_stage'] == 'refinement_2'
        assert row['interruption']['stage'] == 'refinement_3'
        assert 'Third pass did not complete' in row['interruption']['reason']
    for row in result['lanes']:
        if row['state'] == 'completed':
            assert pipeline.sha(tmp_path / row['proof']) == row['sha256']


def test_changed_source_is_rejected_before_finalization_calls(tmp_path, monkeypatch):
    source = tmp_path / 'source'
    proof = tmp_path / 'proof.md'
    proof.write_text('original')
    saved = {'candidate_id': 'a', 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
    write(tmp_path / 'harness_release.json', {'parameters': {}})
    write(source / 'score_targets.json', {'checkpoints': [{'checkpoint': 'R1-C2', 'proofs': [saved]}]})
    proof.write_text('changed')
    monkeypatch.setattr(pipeline, 'run_process', lambda *a, **kw: pytest.fail('Model process started'))
    with pytest.raises(ValueError, match='Source proof changed'):
        pipeline.finish_lane(tmp_path, source, 'a', 'synthetic', '1.7.0', sys.executable)


def test_final_pass_command_and_completed_resume_keep_source_binding(tmp_path, monkeypatch):
    source = tmp_path / 'source'
    proof = tmp_path / 'source-proof.md'
    proof.write_text('Proof after the preceding pass.')
    saved = {'candidate_id': 'a', 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}
    runtime = dict(problem_dir=str(tmp_path / 'statements'), seed_namespace='synthetic',
                   raw_seed_offset=0, model_timeout_sec=600,
                   gemma_endpoint='http://127.0.0.1:8030/v1', qwen_endpoint='http://127.0.0.1:8027/v1')
    identity = {'parameters': runtime, 'release_sha256': 'a' * 64}
    write(tmp_path / 'harness_release.json', identity)
    write(source / 'manifest.json', {'runtime': runtime})
    write(source / 'score_targets.json', {'checkpoints': [{'checkpoint': 'R1-C2', 'proofs': [saved]}]})
    called = []
    output = tmp_path / 'finalization/synthetic/a'
    def run(command, **kwargs):
        called.append(command)
        assert '--execute-models' in command
        assert '--then-v326' not in command and '--then-tool-harness' not in command
        assert command[command.index('--source-r1-root') + 1] == str(source)
        assert command[command.index('--seed-namespace') + 1] == runtime['seed_namespace']
        staged = output / 'input.md'
        staged.parent.mkdir(parents=True)
        staged.write_bytes(proof.read_bytes())
        terminal = output / 'final.md'
        terminal.write_text('Completed final-pass proof.')
        write(output / 'terminal_proof.json', {'candidate_id': 'a', 'proof_path': str(terminal),
                                              'proof_sha256': pipeline.proof_hash(terminal)})
        write(output / 'status.json', {'state': 'completed'})
        write(output / 'continuation.json', {
            'source_manifest_sha256': pipeline.sha(source / 'manifest.json'),
            'release_sha256': identity['release_sha256'],
            'driver_sha256': pipeline.sha(pipeline.IMPLEMENTATION / 'tools/continue_r1.py'),
            'problem_id': 'synthetic', 'candidate_id': 'a', 'target_checkpoint': 'R1-C3',
            'source_proof': saved, 'runtime': runtime,
            'input_proof': dict(saved, proof_path=str(staged)),
        })
    monkeypatch.setattr(pipeline, 'run_process', run)
    first = pipeline.finish_lane(tmp_path, source, 'a', 'synthetic', '1.7.0', sys.executable)
    assert pipeline.finish_lane(tmp_path, source, 'a', 'synthetic', '1.7.0', sys.executable) == first
    assert len(called) == 1
    (output / 'input.md').write_text('Changed staged input.')
    with pytest.raises(ValueError, match='input proof changed'):
        pipeline.finish_lane(tmp_path, source, 'a', 'synthetic', '1.7.0', sys.executable)
    assert len(called) == 1
