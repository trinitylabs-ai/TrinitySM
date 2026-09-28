#!/usr/bin/env python3
"""Resume a saved accepting-Fusion format failure; immutable release + local adapter.

Preparation and producer replay are offline. Live stages never import grading.
"""
import argparse
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback
from acceptance_format import install, POLICY

CID = 't10_r02'
PID = 'imo2026_p4'


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def textsha(text): return hashlib.sha256(text.strip().encode()).hexdigest()
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n'); temp.replace(path)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module); return module


def setup(cfg):
    engine = Path(cfg['repo']) / 'harnesses/imo_proof_pipeline/releases/1.12.0/engine/source'
    release = engine.parents[1]
    launcher = load('recovery_frozen_release', release / 'launch.py')
    _, profile = launcher.verify()
    assert sha(release / 'release.json') == cfg['release_sha256']
    os.environ.update(PYTHONPATH=str(engine), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    sys.path.insert(0, str(engine)); os.chdir(engine)
    queue = load('recovery_frozen_queue', engine / 'scripts/run_v263_v290.py')
    _, backend = queue.load_engines()
    assert Path(backend.__file__).resolve().is_relative_to(engine)
    source = Path(cfg['source']) / 'generation/run/problems' / PID / '02_r1_cycles'
    original = read(source / 'manifest.json')
    backend.configure_problem_binding(problem_id=PID, problem_number=4,
        problem_sha256=original['frozen_inputs']['problem_text_sha256'], candidate_ids=tuple(original['candidate_ids']))
    return engine, launcher, profile, queue, backend, source, original


def prepare(cfg):
    engine, launcher, profile, queue, p, source, original = setup(cfg)
    out = Path(cfg['output']); gen = out / 'generation'
    gen.mkdir(parents=True, exist_ok=False)
    stage = source / 'lanes' / CID / '02_r1_cycle_2'
    source_case = stage / 'cases' / f'{PID}.{CID}'
    assert not list((source_case / 'resolver').glob('**/result.json'))
    manifest = read(stage / 'manifest.json'); spec = manifest['cases'][0]
    assert len(manifest['cases']) == 1 and spec['candidate_id'] == CID
    fusion_path, = (source_case / 'fusion').glob('**/result.json')
    fusion = read(fusion_path)
    gate_task = p._reconstruct_gate_task(fusion_result=fusion, spec=spec, case_dir=source_case, allowed_root=source)
    source_audit = source_case / 'fusion_acceptance_audit/audit_00'
    case = gen / 'r2/cases' / spec['case_id']
    inventory = {str(f): sha(f) for f in source.rglob('*') if f.is_file()}
    inventory.update({str(f): sha(f) for f in (Path(cfg['source']) / 'generation/run/proofs').rglob('*') if f.is_file()})
    write(out / 'control/source_hashes.json', inventory)

    def replay(**kwargs):
        assert kwargs['stage_name'] == 'audit_fusion_acceptance'
        dest = kwargs['output_dir']; shutil.copytree(source_audit, dest)
        attempts = []
        for directory in sorted(dest.glob('attempt_*')):
            validation = read(directory / 'validation.json')
            attempts.append(validation)
        last = sorted(dest.glob('attempt_*'))[-1]
        assert len(attempts) == 3 and all(r['state'] == 'rejected' for r in attempts)
        raw_path, = [f for f in last.glob('*.raw_response.json') if '.pre_budget_forcing.' not in f.name]
        text = read(raw_path)['choices'][0]['message']['content'].strip()
        parsed = kwargs['parser'](text)
        assert parsed['valid'] and parsed['verdict'] == 'CERTIFIED' and parsed['format_interpretation']['policy'] == POLICY
        original_validation = last / 'validation.original.json'
        shutil.copyfile(last / 'validation.json', original_validation)
        attempts[-1] = {**attempts[-1], 'state': 'accepted', 'errors': [],
            'mechanical_recovery': parsed['format_interpretation'],
            'original_validation_sha256': sha(original_validation), 'new_model_calls': 0}
        write(last / 'validation.json', attempts[-1])
        final = dest / 'audit_fusion_acceptance.final.md'; final.write_text(text + '\n')
        metadata_path, = [f for f in last.glob('*.metadata.json') if '.pre_budget_forcing.' not in f.name]
        result = {'token_policy': p.repair_boundary.token_policy_for(kwargs['model']),
            'text': text, 'parsed': parsed, 'metadata': read(metadata_path), 'attempts': attempts,
            'attempt_dir': str(last), 'final_path': str(final), 'final_sha256': textsha(text)}
        write(dest / 'call_result.json', result)
        return result

    runtime = original['runtime']
    with p.runtime_generation_policy(model_timeout_sec=runtime['model_timeout_sec']), p.inherited_component_caps(), install(p.repair_boundary):
        effective = p.repair_boundary.audit_fusion_before_resolver(lane=case, task=gate_task,
            source_result=fusion, qwen_endpoint=runtime['qwen_endpoint'], gemma_endpoint=runtime['gemma_endpoint'],
            cycle_key='R1-C2', model_timeout_sec=runtime['model_timeout_sec'], caller=replay, enable_exact_evidence=False)
        record = effective['fusion_acceptance_audit']
        p.repair_boundary.verify_gate_producer_history(record, allowed_root=gen, source_fusion=fusion['final'],
            effective_fusion=effective['final'], task=gate_task)
        assert effective['final'] == fusion['final']
        problem = case / 'input/problem.json'; proof = case / 'input/submitted_proof.md'
        p._stage_file(Path(spec['problem_path']), problem); p._stage_file(Path(spec['proof_path']), proof)
        new_spec = dict(spec, problem_path=str(problem), proof_path=str(proof))
        fusion_task = dict(fusion['task'], **gate_task, problem_path=str(problem), proof_path=str(proof))
        task = p.stage.build_resolver_task(case=new_spec, fusion_task=fusion_task, fusion_result=effective,
            case_dir=case, seed_namespace=manifest['seed_namespace'])
        task = p.bind_effective_fusion_task(task, fusion_result=effective, cycle_key='R1-C2')
        task['source_fusion_result_path'] = str(fusion_path)
        assert task['fusion_decision_gate']['state'] == 'CERTIFIED'
    job = {'case_dir': str(case), 'task': task, 'spec': new_spec, 'gate_task': gate_task,
        'source_fusion': str(fusion_path), 'effective_fusion': effective['_v290_effective_result_path'],
        'runtime': runtime, 'selector_runtime': read(Path(cfg['source']) / 'generation/run/harness_release.json')['parameters'],
        'problem_path': str(problem), 'source_original': original, 'policy': POLICY}
    write(gen / 'prepared.json', job)
    write(out / 'control/preflight.json', {'state': 'passed', 'model_calls': 0,
        'source_unchanged': all(sha(f) == digest for f, digest in inventory.items()),
        'producer_hashes_prompts_seeds_bf_replayed': True, 'verdict_unchanged': True,
        'frozen_release_unchanged': True, 'policy': POLICY, 'resolver_seed': task['seed'],
        'resolver_temperature': task['temperature'], 'resume_point': 'R2 resolver',
        'new_raw_lazy_r1_or_r2_review_fusion_calls': 0})


def verify_source(out):
    for path, digest in read(out / 'control/source_hashes.json').items():
        assert sha(path) == digest, 'Source changed: ' + path


def checkpoint(path, proof, stage, **details):
    record = {'candidate_id': CID, 'proof_path': str(proof), 'proof_sha256': textsha(Path(proof).read_text()),
              'selected_stage': stage, **details}
    write(path, record); return record


def run_module(engine, name, arguments):
    subprocess.run([sys.executable, '-u', '-B', '-m', name, *map(str, arguments)],
        cwd=engine, env=os.environ, stdin=subprocess.DEVNULL, check=True)


def execute(cfg, which):
    engine, launcher, profile, queue, p, source, original = setup(cfg)
    out = Path(cfg['output']); gen = out / 'generation'; verify_source(out)
    job = read(gen / 'prepared.json'); runtime = job['runtime']
    if which == 'servers':
        servers = {role: launcher.server_settings(runtime[role + '_endpoint'], expected) for role, expected in profile['servers'].items()}
        write(out / 'control/servers.json', servers); return
    if which == 'r2':
        if (gen / 'r2/terminal.json').exists(): return
        case = Path(job['case_dir']); task = job['task']; boundary = p.repair_boundary
        with queue.refinement_policy(p, gen / 'r2/refinement_bf'), p.runtime_generation_policy(model_timeout_sec=600), p.inherited_component_caps(), install(boundary):
            effective = read(job['effective_fusion']); fusion = read(job['source_fusion'])
            boundary.verify_gate_producer_history(effective['fusion_acceptance_audit'], allowed_root=gen,
                source_fusion=fusion['final'], effective_fusion=effective['final'], task=job['gate_task'])
            dest = p.stage.resolver.task_output_dir(case, task)
            if not (dest / 'result.json').exists():
                assert not dest.exists(), f'Interrupted resolver preserved: {dest}'
                p.stage.resolver.run_task(output_dir=case, task=task)
            result, parsed = p._verify_resolver_producer(resolver_result_path=dest / 'result.json', case_dir=case,
                allowed_root=gen, model_timeout_sec=600)
            if parsed['outcome'] == 'RESOLUTION_FAILED':
                checkpoint(gen / 'r2/terminal.json', task['proof_path'], 'refinement_1',
                           failure='R2 resolver returned RESOLUTION_FAILED', fallback_used=True)
                return
            proof = Path(task['proof_path']) if parsed['outcome'] == 'ORIGINAL_PROOF_VALID' else dest / 'resolved_proof.md'
            if parsed['outcome'] == 'RESOLVED_PROOF': assert proof.read_text().strip() == parsed['proof'].strip()
            p.stage.write_uncertified_trace_handoff(case=job['spec'], case_dir=case, resolver_task=task, resolver_result=result)
            checkpoint(gen / 'r2/terminal.json', proof, 'refinement_2', resolver_outcome=parsed['outcome'])
    elif which == 'r3':
        if (gen / 'r3/terminal.json').exists(): return
        r2 = read(gen / 'r2/terminal.json')
        if r2['selected_stage'] != 'refinement_2':
            write(gen / 'r3/terminal.json', {**r2, 'skipped': 'R2 did not complete'}); return
        driver = load('frozen_single_cycle', engine / 'scripts/continue_r1_audited.py')
        output = gen / 'r3'
        stage = output / 'lanes' / CID / '03_r1_cycle_3'
        try:
            with queue.refinement_policy(p, output / 'refinement_bf'), install(p.repair_boundary):
                if (stage / 'summary.json').exists() and read(stage / 'summary.json').get('state') == 'completed':
                    terminal = p._terminal_r1_proofs(stage_dir=stage, allowed_root=output, expected_candidates=(CID,), model_timeout_sec=600)[0]
                else:
                    assert not stage.exists(), 'Incomplete R3 preserved; refusing duplicate inference'
                    _, terminal = driver.run_cycle(p, output=output, candidate=CID, cycle=3, proof=r2,
                        problem=Path(job['problem_path']), runtime=runtime, exact_evidence=False)
            checkpoint(output / 'terminal.json', terminal['proof_path'], 'refinement_3')
        except Exception as exc:
            write(output / 'failure.json', {'error': str(exc), 'traceback': traceback.format_exc()})
            write(output / 'terminal.json', {**r2, 'fallback_used': True, 'failure': str(exc)})
    elif which == 'audit':
        if (gen / 'selected_lane.json').exists(): return
        r2 = read(gen / 'r2/terminal.json'); r3 = read(gen / 'r3/terminal.json')
        if r3['selected_stage'] != 'refinement_3':
            write(gen / 'selected_lane.json', r3); return
        from experiments.local_math_verifier.post_resolver_audit import live
        root = gen / 'post_resolver_audit' / CID
        pair = {'problem_id': PID, 'candidate_id': CID, 'problem': job['gate_task']['problem'],
            'baseline_path': r2['proof_path'], 'baseline_proof_sha256': r2['proof_sha256'],
            'candidate_path': r3['proof_path'], 'candidate_proof_sha256': r3['proof_sha256']}
        live.prepare(root, pair, job['selector_runtime'], cfg['release_sha256'])
        jobpath = root.parent / 'job.json'
        write(jobpath, {'policy_id': live.POLICY_ID, 'problem_id': PID, 'lane_roots': [str(root)], 'release_sha256': cfg['release_sha256']})
        run_module(engine, 'experiments.local_math_verifier.post_resolver_audit.live', ['--job', jobpath])
        selection = live.collect(root, Path(r2['proof_path']).read_bytes(), Path(r3['proof_path']).read_bytes(),
            cfg['release_sha256'], expected_case=pair, runtime=job['selector_runtime'])
        selected = r3 if selection['decision'] == 'ACCEPT_CANDIDATE' else r2
        write(gen / 'selected_lane.json', {**selected, 'post_resolver_audit': selection})
    elif which == 'vote':
        from experiments.local_math_verifier.cross_lane_voter import live
        native = Path(cfg['source']) / 'generation/run'; selected = read(gen / 'selected_lane.json')
        candidates = []
        for lane in read(native / 'final_results.json')['lanes']:
            row = selected if lane['candidate_id'] == CID else dict(lane, proof_path=str(native / lane['proof']))
            data = Path(row['proof_path']).read_bytes()
            assert textsha(data.decode()) == row['proof_sha256']
            published = out / 'proofs' / (row['candidate_id'] + '.md')
            published.parent.mkdir(parents=True, exist_ok=True)
            if published.exists(): assert published.read_bytes() == data
            else: published.write_bytes(data)
            candidates.append({**row, 'proof_path': str(published)})
        write(gen / 'portfolio.json', candidates)
        root = gen / 'cross_lane_voter'
        expected = {'problem_id': PID, 'problem': job['gate_task']['problem'], 'candidates': candidates,
                    'runtime': job['selector_runtime'], 'release_sha256': cfg['release_sha256']}
        live.prepare(root, **expected)
        run_module(engine, 'experiments.local_math_verifier.cross_lane_voter.live', ['--root', root])
        result = live.collect(root, expected=expected)
        assert result['state'] == 'completed', result
        write(gen / 'selection.json', result)
    verify_source(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('stage', choices=['prepare', 'servers', 'r2', 'r3', 'audit', 'vote'])
    args = parser.parse_args(); cfg = read(args.config)
    if args.stage == 'prepare': prepare(cfg)
    else: execute(cfg, args.stage)
