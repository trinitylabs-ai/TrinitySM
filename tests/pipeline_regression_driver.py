"""Run the real pipeline scheduling and proof-binding code with scripted stages."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import shutil
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
RELEASE = '1.12.0' if '--selection-upgrade-b' in sys.argv else '1.11.0' if '--voter-b' in sys.argv else ('1.9.0' if '--audited-b-1-9' in sys.argv else '1.10.0') if '--audited-b' in sys.argv else '1.8.0' if '--harness-b' in sys.argv else '1.7.0'
ENGINE = ROOT / 'harnesses/imo_proof_pipeline/releases' / RELEASE / 'engine/source'
sys.path.insert(0, str(ENGINE))
import pytest
from scripts import run_v263_v290 as runner
from pipeline_replay import install_refinement_replay, mock_frontend_calls


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(output, brief_verdict, recover=False):
    def no_network(*args, **kwargs):
        raise AssertionError('Regression tests must not make model or network calls')
    socket.socket.connect = no_network
    socket.create_connection = no_network
    public = load('regression_public', ROOT / 'harnesses/proof_workshop/pipeline.py')
    driver = load('regression_final_pass', public.continuation_driver(RELEASE))
    frontend, backend = runner.load_engines()
    patches = pytest.MonkeyPatch()
    if RELEASE in ('1.8.0', '1.9.0', '1.10.0', '1.11.0', '1.12.0'):
        from experiments.local_math_verifier import refinement_bf
        original_routes = refinement_bf.build_routes(backend)
        # Bind actual system prompts before stage functions become replay stubs.
        patches.setattr(refinement_bf, 'build_routes', lambda _: original_routes)
    frontend_calls = mock_frontend_calls(patches, frontend)
    gates, cycle_inputs, cycle_outputs = install_refinement_replay(patches, brief_verdict)
    patches.setattr(runner, 'check_servers', lambda _: None)
    pid = 'Regression-001'
    statement = {'problem_id': pid, 'problem': 'If x=0, prove x*x=0.'}
    statements = output.parent / 'statements'
    runner.write(statements / (pid + '.json'), statement)
    runtime = dict(problem_dir=str(statements), seed_namespace='workshop-regression',
                   raw_seed_offset=0, model_timeout_sec=600,
                   gemma_endpoint='http://127.0.0.1:8030/v1', qwen_endpoint='http://127.0.0.1:8027/v1')
    def core(command, **kwargs):
        output.mkdir()
        runner.write(output / 'harness_release.json', {
            'release_sha256': public.sha(public.IMPLEMENTATION / 'releases' / RELEASE / 'release.json'),
            'parameters': runtime,
            **({'final_selector': public.selector_policy.binding(RELEASE)} if '--qwen-selector' in sys.argv else {}),
        })
        public.selector_policy.prepare(output, ENGINE)
        runner.write(output / 'manifest.json', {'schema': runner.SCHEMA, 'dry_run': False,
                     'problems': [dict(statement, problem_number=1)], **runtime})
        runner.write(output / 'inputs' / (pid + '.json'), statement)
        result = runner.execute_problem(output, pid, dry_run=False)
        assert result['state'] == 'completed', result
        return 0
    original_load = driver.load
    def load_driver(name, path):
        module = original_load(name, path)
        if name == 'continuation_release':
            module.server_settings = lambda *a, **kw: {}
        return module
    driver.load = load_driver
    final_lock = threading.Lock()
    audit_calls = []
    selector_calls = []
    def final_process(command, **kwargs):
        if '--run-root' in command:
            from cross_lane_replay import response
            assert command[3] == str(output / 'selector_runtime/selector.py')
            def comparison(**kw):
                selector_calls.append(kw)
                return response(kw)
            public.selector_policy.module(output).run(Path(command[-1]), comparison)
            return 0
        if '-m' in command and command[command.index('-m')+1].endswith('cross_lane_voter.live'):
            from cross_lane_replay import response
            public.voter_module(RELEASE).run(Path(command[-1]), lambda **kw: response(kw))
            return 0
        if '-m' in command:
            from post_resolver_audit_replay import response
            def audit_call(**kw):
                audit_calls.append(kw)
                return response(kw, 'KEEP_BASELINE' if '--audit-veto' in sys.argv and 't10_r01' in str(kw['output_dir']) else 'ACCEPT_CANDIDATE')
            public.audit_module(RELEASE).run_job(Path(command[-1]), audit_call)
            return 0
        # Execute the actual driver in-process so the same scripted model-stage
        # fixtures apply. Real manifests, source binding and terminal replay run.
        argv = command[3:]
        parser = argparse.ArgumentParser()
        for option in ('release', 'problem-id', 'candidate-id', 'seed-namespace', 'gemma-endpoint', 'qwen-endpoint'):
            parser.add_argument('--' + option)
        for option in ('source-r1-root', 'problem-dir', 'output-dir'):
            parser.add_argument('--' + option, type=Path)
        for option in ('raw-seed-offset', 'model-timeout-sec'):
            parser.add_argument('--' + option, type=int)
        parser.add_argument('--execute-models', action='store_true')
        args = parser.parse_args(argv)
        args.dry_run = False
        args.then_v326 = False
        args.tool_harness_version = '0.3.326'
        args.v326_master_seed = 20260915
        # Live lanes have separate processes; this scripted replay shares modules.
        with final_lock:
            driver.run(args)
    patches.setattr(public, 'run_process', lambda command, **kw:
                    final_process(command, **kw) if kw.get('check') or '-m' in command or '--run-root' in command else core(command, **kw))
    code = public.main(['--release', RELEASE, '--problem-dir', str(statements), '--output-dir', str(output), '--execute-models'])
    assert code == 0, (output / 'final_results.json').read_text()
    assert len(frontend_calls) == 12
    assert len(gates) == 12
    assert {cycle for cycle, _, _ in gates} == {'R1-C1', 'R1-C2', 'R1-C3'}
    for cycle in (2, 3):
        assert cycle_inputs[cycle] == cycle_outputs[cycle - 1]
    result = json.loads((output / 'final_results.json').read_text())
    assert result['completed_proofs'] == 4
    assert result['terminal_stage'] == 'refinement_3'
    if RELEASE in ('1.9.0', '1.10.0', '1.11.0', '1.12.0'):
        assert len(audit_calls) == 16, len(audit_calls)
        assert {row['model'] for row in audit_calls} == set(public.audit_module(RELEASE).MODELS.values())
        assert all('post_resolver_audit' in row for row in result['lanes'])
        if '--audit-veto' in sys.argv:
            rejected = next(row for row in result['lanes'] if row['candidate_id'] == 't10_r01')
            assert rejected['selected_stage'] == 'refinement_2' and rejected['fallback_used']
        # Offline collection revalidates saved votes and never reruns models.
        patches.setattr(public, 'run_process', no_network)
        assert public.main(['--collect-only', '--output-dir', str(output)]) == 0
    if '--qwen-selector' in sys.argv:
        assert len(selector_calls) == 12
        assert all('qwen' in call['model'].lower() for call in selector_calls)
        assert result['winner_selection_policy'] == 'qwen_only_full_round_robin_seed_order_ties'
        assert len(result['problem_selections'][0]['vote_table']) == 12
    proof_hashes = {row['candidate_id']: row['sha256'] for row in result['lanes']}
    for row in result['lanes']:
        text = (output / row['proof']).read_text()
        assert all(f'Cycle {cycle} terminal marker' in text for cycle in range(1, int(row['selected_stage'][-1]) + 1))
        if row['selected_stage'] == 'refinement_2':
            assert 'Cycle 3 terminal marker' not in text
    prompts = {}
    for path in output.rglob('*.prompt.txt'):
        prompts[str(path.relative_to(output))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in output.rglob('*.user_prompt.txt'):
        prompts[str(path.relative_to(output))] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'schema': 'workshop-model-free-pipeline-regression-v1',
              'model_calls': 0, 'network_calls': 0, 'candidate_lanes': 4,
              'refinement_passes_per_lane': 3, 'audited_handoffs': len(gates),
              'proof_sha256': proof_hashes, 'prompt_sha256': dict(sorted(prompts.items()))}
    (output / 'regression_result.json').write_text(json.dumps(report, indent=2) + '\n')
    if recover:
        # Model calls have finished; simulate losing the queue between durable
        # per-lane completion and the portfolio checkpoint write.
        source = output / 'problems' / pid / '02_r1_cycles'
        ids = list(public.CANDIDATES)
        shutil.rmtree(output / 'proofs')
        for index, candidate in enumerate(ids[1:], 1):
            shutil.rmtree(output / 'finalization' / pid / candidate)
            for cycle in range(4 - index, 3):
                shutil.rmtree(source / 'lanes' / candidate / f'{cycle:02d}_r1_cycle_{cycle}')
        targets = public.read(source / 'score_targets.json')
        for checkpoint in targets['checkpoints']:
            checkpoint['proofs'] = [p for p in checkpoint['proofs'] if p['candidate_id'] == ids[0]]
        public.write(source / 'score_targets.json', targets)
        public.write(output / 'pipeline_execution.json', {'state': 'interrupted', 'returncode': 143,
                                                        'reason': 'Synthetic worker termination'})
        patches.setattr(public, 'run_process', no_network)
        assert public.main(['--collect-only', '--output-dir', str(output)]) == 1
        recovered = public.read(output / 'final_results.json')
        assert recovered['completed_proofs'] == 4, recovered
        assert [r['selected_stage'] for r in recovered['lanes']] == [
            'refinement_3', 'refinement_2', 'refinement_1', 'lazy_checked'], recovered
        for row in recovered['lanes']:
            assert public.sha(output / row['proof']) == row['sha256']
        # A repeat collection is idempotent and still performs no inference.
        before = (output / 'final_results.json').read_bytes()
        assert public.main(['--collect-only', '--output-dir', str(output)]) == 1
        assert (output / 'final_results.json').read_bytes() == before
    print(json.dumps({k: v for k, v in report.items() if not isinstance(v, dict)}))
    patches.undo()


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve(), sys.argv[2] if len(sys.argv) > 2 else 'CERTIFIED',
        recover='--recover' in sys.argv)
