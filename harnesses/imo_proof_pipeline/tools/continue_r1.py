#!/usr/bin/env python3
"""Run one saved lane's next R1 cycle using the unchanged release implementation.

Called by the public complete-pipeline controller. This external
driver changes scheduling only. Source artifacts remain at their original paths;
only the verified statement and terminal proof are copied as new model inputs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(Path(path).read_text().strip().encode()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate_statement(statement, original):
    """Accept the two statement-only benchmark schemas without extra fields."""
    fields = set(statement)
    if fields not in ({'problem_id', 'claim'}, {'problem_id', 'problem'}):
        raise ValueError('Expected a statement-only benchmark input')
    claim = statement.get('claim', statement.get('problem'))
    if (statement['problem_id'] != original['problem_id']
            or not isinstance(claim, str) or not claim.strip()
            or claim != original['claim']):
        raise ValueError('Expected the same statement-only benchmark input')


def run_cycle(backend, *, output, candidate, cycle, proof, problem, runtime, exact_evidence):
    with backend.runtime_generation_policy(model_timeout_sec=runtime['model_timeout_sec']), \
            backend.inherited_component_caps(), backend.mandatory_repair_boundary(
                qwen_endpoint=runtime['qwen_endpoint'], gemma_endpoint=runtime['gemma_endpoint'],
                cycle_key=f'R1-C{cycle}', model_timeout_sec=runtime['model_timeout_sec'],
                enable_exact_evidence=exact_evidence):
        return backend.run_r1_cycle_lane(
            output_dir=output, candidate_id=candidate, cycle=cycle, source_proof=proof,
            problem_path=problem, gemma_endpoint=runtime['gemma_endpoint'],
            qwen_endpoint=runtime['qwen_endpoint'], seed_namespace=runtime['seed_namespace'],
            model_timeout_sec=runtime['model_timeout_sec'])


def run(args):
    if args.release != '1.7.0':
        raise ValueError('This continuation driver has been checked against release 1.7.0 only')
    release = ROOT / 'harnesses/imo_proof_pipeline/releases' / args.release
    launcher = load('continuation_release', release / 'launch.py')
    manifest, profile = launcher.verify()
    source = args.source_r1_root.resolve()
    output = args.output_dir.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f'Use a fresh output directory: {output}')
    original = read(source / 'manifest.json')
    identity_path = next(p / 'harness_release.json' for p in source.parents
                         if (p / 'harness_release.json').is_file())
    original_release = read(identity_path)
    if original_release['release_sha256'] != sha(release / 'release.json'):
        raise ValueError('Source checkpoint belongs to a different release')
    for key in ('seed_namespace', 'raw_seed_offset', 'model_timeout_sec', 'gemma_endpoint', 'qwen_endpoint'):
        if getattr(args, key) != original_release['parameters'][key]:
            raise ValueError(f'Continuation would change saved {key}')
    if args.problem_id != original['problem_id'] or args.candidate_id not in original['candidate_ids']:
        raise ValueError('Source problem/candidate selection mismatch')
    checkpoint = original['terminal_checkpoint']
    if checkpoint != 'R1-C2':
        raise ValueError('Expected a completed R1-C2 source')
    saved = next(c for c in read(source / 'score_targets.json')['checkpoints']
                 if c['checkpoint'] == checkpoint)
    source_stage = Path(saved['stage_dirs'][args.candidate_id]).resolve()
    if not source_stage.is_relative_to(source):
        raise ValueError('Source stage escapes its original run')
    engine = release / 'engine/source'
    os.environ.pop('PYTHONHOME', None)
    os.environ.update(PYTHONPATH=str(engine), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    os.chdir(engine)
    sys.path.insert(0, str(engine))
    queue = load('continuation_frozen_queue', engine / 'scripts/run_v263_v290.py')
    _, backend = queue.load_engines()
    if not Path(backend.__file__).resolve().is_relative_to(engine):
        raise ValueError('Imported backend is outside the frozen release')
    backend.configure_source_problem(Path(original['source_run']), original['problem_number'],
                                     expected_problem_id=args.problem_id)
    runtime = original['runtime']
    proof = backend._terminal_r1_proofs(stage_dir=source_stage, allowed_root=source,
        expected_candidates=(args.candidate_id,), model_timeout_sec=runtime['model_timeout_sec'])[0]
    expected = next(p for p in saved['proofs'] if p['candidate_id'] == args.candidate_id)
    if proof != expected or text_sha(proof['proof_path']) != proof['proof_sha256']:
        raise ValueError('Source terminal proof differs from its validated producer')
    original_problem = source / 'input/problem.json'
    if sha(original_problem) != original['frozen_inputs']['problem_file_sha256']:
        raise ValueError('Source problem changed')
    statement_path = args.problem_dir.resolve() / f'{args.problem_id}.json'
    statement = read(statement_path)
    validate_statement(statement, read(original_problem))
    servers = {} if args.dry_run else {role: launcher.server_settings(
        runtime[role + '_endpoint'], expected) for role, expected in profile['servers'].items()}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'input').mkdir()
    problem = output / 'input/problem.json'
    problem.write_bytes(original_problem.read_bytes())
    (output / 'input/statement.json').write_bytes(statement_path.read_bytes())
    proof_path = output / 'input' / f'{args.candidate_id}.R1-C2.md'
    proof_path.write_bytes(Path(proof['proof_path']).read_bytes())
    source_proof = {'candidate_id': args.candidate_id, 'proof_path': str(proof_path),
                    'proof_sha256': proof['proof_sha256']}
    exact = original['repair_brief_boundary']['optional_exact_evidence']['enabled_for_every_repair_brief_audit']
    continuation = {'schema': 'ipp-single-cycle-continuation-v1', 'release': manifest['version'],
        'release_sha256': sha(release / 'release.json'), 'driver_sha256': sha(__file__),
        'source_r1_root': str(source), 'source_manifest_sha256': sha(source / 'manifest.json'),
        'source_checkpoint': checkpoint, 'target_checkpoint': 'R1-C3',
        'problem_id': args.problem_id, 'candidate_id': args.candidate_id,
        'source_proof': proof, 'input_proof': source_proof, 'runtime': runtime,
        'transport_policy': original['transport_policy'], 'exact_evidence': exact,
        'verified_servers': servers,
        'started_at': datetime.now(timezone.utc).isoformat(), 'dry_run': args.dry_run}
    write(output / 'continuation.json', continuation)
    if args.dry_run:
        backend._case_manifest(problem_path=problem, proofs=[source_proof],
            destination=output / 'lanes' / args.candidate_id / 'input/r1_cycle_3_cases.json', cycle=3)
        write(output / 'status.json', {'state': 'preflight_passed', 'model_calls': 0})
        return
    write(output / 'status.json', {'state': 'running', 'stage': 'R1-C3'})
    stage, terminal = run_cycle(backend, output=output, candidate=args.candidate_id, cycle=3,
        proof=source_proof, problem=problem, runtime=runtime, exact_evidence=exact)
    write(output / 'score_targets.json', {'checkpoints': [{'checkpoint': 'R1-C3',
        'stage_dirs': {args.candidate_id: str(stage)}, 'proofs': [terminal],
        'strict_score_model_visible': False}]})
    write(output / 'terminal_proof.json', terminal)
    write(output / 'status.json', {'state': 'completed', 'stage': 'finished',
        'r1_c3_proof_sha256': terminal['proof_sha256'],
        'completed_at': datetime.now(timezone.utc).isoformat()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('release', 'problem-id', 'candidate-id', 'seed-namespace', 'gemma-endpoint', 'qwen-endpoint'):
        parser.add_argument('--' + name, required=True)
    for name in ('source-r1-root', 'problem-dir', 'output-dir'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--raw-seed-offset', type=int, required=True)
    parser.add_argument('--model-timeout-sec', type=int, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--execute-models', action='store_true')
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()
    existed = args.output_dir.exists()
    try:
        run(args)
    except Exception as error:
        if not existed and (args.output_dir / 'continuation.json').is_file():
            write(args.output_dir / 'failure.json', {'type': type(error).__name__, 'error': str(error)})
            write(args.output_dir / 'status.json', {'state': 'failed', 'error': str(error)})
        raise


if __name__ == '__main__':
    main()
