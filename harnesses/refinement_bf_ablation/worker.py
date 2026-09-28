"""Run one isolated, hash-bound refinement continuation experiment arm.

Each invocation is a new process. The frozen solver is imported read-only and
its original three refinement cycles are used without changing their prompts,
seeds, sampling, recovery, or final-proof fallback policy.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import signal
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'harnesses/imo_proof_pipeline/releases/1.7.0'
CANDIDATES = ('t10_r01', 't10_r02', 't07_r01', 't07_r02')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text_digest(data):
    return digest(io.StringIO(data.decode('utf-8'), newline=None).read().strip().encode('utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def checked_path(value):
    require(isinstance(value, str) and Path(value).is_absolute(), 'Expected an absolute path')
    path = Path(value)
    # /tmp and /var are operating-system aliases on macOS; user-created links
    # elsewhere are forbidden, including links inserted after preflight.
    require(not any(p.is_symlink() for p in (path, *path.parents)
                    if str(p) not in ('/tmp', '/var')), f'Symlink in path: {path}')
    return path.resolve()


def read_bound(path, expected):
    path = checked_path(str(path))
    require(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid SHA-256')
    data = path.read_bytes()
    require(digest(data) == expected, f'Input hash mismatch: {path}')
    return data


def validate_job(path):
    from . import inputs
    path = checked_path(str(Path(path).absolute()))
    raw = path.read_bytes()
    job = json.loads(raw)
    require(isinstance(job, dict) and job.get('schema') == 'refinement-bf-job-v1', 'Unsupported job schema')
    require(job.get('variant') in ('original', 'role_specific'), 'Unknown cue variant')
    require(type(job.get('dry_run')) is bool, 'Job must declare dry_run')
    problem = job.get('problem')
    require(isinstance(problem, dict) and set(problem) == {
        'problem_id', 'problem_number', 'claim', 'problem_sha256'}, 'Expected statement-only problem')
    require(isinstance(problem['problem_id'], str) and
            re.fullmatch('[A-Za-z0-9_-]+', problem['problem_id']), 'Invalid problem ID')
    require(type(problem['problem_number']) is int and problem['problem_number'] > 0, 'Invalid problem number')
    require(isinstance(problem['claim'], str) and bool(problem['claim'].strip()), 'Empty statement')
    require(digest(problem['claim'].strip().encode('utf-8')) == problem['problem_sha256'], 'Statement hash mismatch')
    require(type(job.get('pair_seed')) is int and 0 <= job['pair_seed'] <= 0xffffffff, 'Invalid pair seed')
    require(job.get('pair_id') == f"{problem['problem_id']}__seed{job['pair_seed']}", 'Pair identity mismatch')
    runtime = job.get('runtime')
    require(isinstance(runtime, dict) and set(runtime) == {
        'gemma_endpoint', 'qwen_endpoint', 'model_timeout_sec', 'seed_namespace', 'workers'}, 'Invalid runtime fields')
    require(type(runtime['workers']) is int and runtime['workers'] == 4, 'Expected four lane workers')
    require(type(runtime['model_timeout_sec']) is int and 30 <= runtime['model_timeout_sec'] <= 14400,
            'Invalid model timeout')
    require(isinstance(runtime['seed_namespace'], str) and bool(runtime['seed_namespace'].strip()), 'Empty seed namespace')
    for role in ('gemma', 'qwen'):
        url = urlsplit(runtime[role + '_endpoint'])
        require(url.scheme == 'http' and url.hostname in ('localhost', '127.0.0.1', '::1') and
                url.path.rstrip('/') == '/v1' and not url.query and not url.fragment and not url.username,
                'Expected a local /v1 model endpoint')
    require(runtime['gemma_endpoint'].rstrip('/') != runtime['qwen_endpoint'].rstrip('/'), 'Model endpoints must differ')
    manifest_path = checked_path(job.get('input_manifest_path'))
    manifest_bytes = read_bound(manifest_path, job.get('input_manifest_sha256'))
    manifest = inputs.verify_manifest(manifest_path, expected_sha=job['input_manifest_sha256'])
    matches = [row for row in manifest.get('problems', []) if row.get('problem') == problem]
    require(len(matches) == 1 and matches[0].get('candidates') == job.get('candidates'), 'Job differs from bound input manifest')
    candidates = job.get('candidates')
    require(isinstance(candidates, list) and len(candidates) == 4, 'Expected four source proofs')
    require({row.get('candidate_id') for row in candidates} == set(CANDIDATES), 'Expected the canonical four lanes')
    sources = {str(path): digest(raw), str(manifest_path): digest(manifest_bytes)}
    for candidate in candidates:
        require(set(candidate) == {'candidate_id', 'proof_path', 'proof_file_sha256', 'proof_sha256'}, 'Unexpected source-proof fields')
        proof_path = checked_path(candidate['proof_path'])
        require(proof_path.is_relative_to(manifest_path.parent), 'Proof snapshot escapes input manifest directory')
        proof = read_bound(proof_path, candidate['proof_file_sha256'])
        require(proof.decode('utf-8').strip() and text_digest(proof) == candidate['proof_sha256'], 'Proof text hash mismatch')
        sources[str(proof_path)] = digest(proof)
    output = checked_path(job.get('output_dir'))
    require(not output.is_relative_to(RELEASE.parent) and not RELEASE.is_relative_to(output), 'Output overlaps frozen releases')
    require(not output.exists(), 'Use a fresh arm output directory')
    return job, sources


def verify_sources(sources):
    for path, expected in sources.items():
        read_bound(path, expected)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_release():
    sys.dont_write_bytecode = True
    launcher = load_module('refinement_ablation_frozen_release', RELEASE / 'launch.py')
    manifest, profile = launcher.verify()
    return launcher, manifest, profile


def load_backend():
    sys.dont_write_bytecode = True
    engine = RELEASE / 'engine/source'
    sys.path.insert(0, str(engine))
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    queue = load_module('refinement_ablation_frozen_queue', engine / 'scripts/run_v263_v290.py')
    _, backend = queue.load_engines()
    require(Path(backend.__file__).resolve().is_relative_to(engine), 'Backend imported outside frozen release')
    return backend


def build_routes(backend):
    """Bind the cue policy to the actual frozen role prompts, including recovery."""
    from . import policy
    stage, boundary = backend.stage, backend.repair_boundary
    module = lambda function: sys.modules[function.__module__]
    r1, r2, r3 = (module(stage.run_original_reviewer), module(stage.reviewer_2.run_task),
                  module(stage.reviewer_3.run_task))
    fusion = module(stage.fusion.run_task)
    resolver = module(backend.v263._ORIGINAL_RESOLVER_RUN_TASK)
    gap1, gap3 = module(stage.run_v089_selector), module(stage.run_v092_selector)
    specs = [
        ('reviewer_1', r'original_reviewer1(?:_clean_[0-9]+k_retry_[0-9]+|_protocol_repair)?', r1.ORIGINAL_REVIEWER_SYSTEM_PROMPT),
        ('reviewer_2', r'reviewer2(?:_clean_[0-9]+k_retry_[0-9]+|_protocol_repair)?', r2.SYSTEM_PROMPT),
        ('reviewer_3', r'reviewer3(?:_cap_continuation|_terminal_recovery|_protocol_repair)?', r3.SYSTEM_PROMPT),
        ('fusion', r'fusion(?:_cap_continuation|_terminal_recovery|_protocol_repair|_assessment_constraint_repair)?', fusion.SYSTEM_PROMPT),
        ('resolver', r'resolver(?:_cap_continuation|_protocol_repair)?', resolver.SYSTEM_PROMPT),
        ('acceptance', r'audit_fusion_acceptance_cap_[0-9]+', boundary.ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT),
        ('fusion', r'reconsider_fusion_cap_[0-9]+', stage.fusion.SYSTEM_PROMPT + boundary.FUSION_RECONSIDERATION_SUFFIX),
        ('repair_brief_audit', r'audit_repair_brief_cap_[0-9]+', boundary.brief_stage.CERTIFIER_SYSTEM_PROMPT),
        ('repair_brief_rewrite', r'rewrite_repair_brief_cap_[0-9]+', boundary.brief_stage.REWRITER_SYSTEM_PROMPT),
        ('auxiliary', r'compact_markdown_trace_extraction', r1.COMPACT_MARKDOWN_EXTRACTOR_SYSTEM_PROMPT),
        ('auxiliary', r'gap_selector', gap1.GAP_SELECTOR_SYSTEM_PROMPT),
        ('auxiliary', r'gap_selector_format_retry', gap1.FORMAT_RETRY_SYSTEM_PROMPT),
        ('auxiliary', r'scope_matched_gap_selector', gap3.GAP_SELECTOR_SYSTEM_PROMPT),
        ('auxiliary', r'scope_matched_gap_selector_format_retry', gap3.FORMAT_RETRY_SYSTEM_PROMPT),
    ]
    return tuple(policy.make_route(*spec) for spec in specs)


class Interrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum
        super().__init__(f'Interrupted by signal {signum}')


def export_lanes(output, lanes):
    rows = []
    for cid in CANDIDATES:
        lane = lanes[cid]
        proof = Path(lane['source']['proof_path']).read_bytes()
        require(text_digest(proof) == lane['source']['proof_sha256'], 'Completed checkpoint changed')
        path = output / 'proofs' / f'{cid}.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(proof)
        rows.append({'candidate_id': cid, 'selected_stage': lane['selected_stage'],
                     'proof_path': str(path), 'proof_file_sha256': digest(proof),
                     'proof_sha256': text_digest(proof), 'failure': lane['failure'],
                     'checkpoints': lane['checkpoints'], 'elapsed_seconds': lane['elapsed_seconds']})
    return rows


def run(path, *, execute_models=False):
    from . import policy
    job, sources = validate_job(path)
    require(job['dry_run'] != bool(execute_models), 'Live jobs require --execute-models; dry runs must omit it')
    launcher, release_manifest, profile = load_release()
    backend = load_backend()
    problem, runtime = job['problem'], job['runtime']
    backend.configure_problem_binding(problem_id=problem['problem_id'], problem_number=problem['problem_number'],
        problem_sha256=problem['problem_sha256'], candidate_ids=CANDIDATES)
    routes = build_routes(backend)
    bf_module = backend.v263.parent._budget_forcing
    servers = {} if job['dry_run'] else {role: launcher.server_settings(runtime[role + '_endpoint'], expected)
        for role, expected in profile['servers'].items()}
    verify_sources(sources)
    output = checked_path(job['output_dir'])
    output.mkdir(parents=True, exist_ok=False)
    started, began = now(), time.monotonic()
    identity = {'release': release_manifest['version'], 'release_sha256': digest((RELEASE / 'release.json').read_bytes()),
                'upstream': release_manifest.get('upstream'), 'verified_servers': servers}
    summary = {'schema': 'refinement-bf-arm-v1', 'state': 'running', 'variant': job['variant'],
               'problem_id': problem['problem_id'], 'pair_seed': job['pair_seed'], 'pair_id': job['pair_id'],
               'input_manifest_path': job['input_manifest_path'], 'input_manifest_sha256': job['input_manifest_sha256'],
               'job_sha256': sources[str(checked_path(str(Path(path).absolute())))],
               'runtime': runtime, 'release_identity': identity, 'started_at': started,
               'lanes': [], 'elapsed_seconds': 0.0, 'optional_exact_evidence': False,
               'mathematically_verified': False, 'grading_performed': False}
    lanes = {}
    try:
        write(output / 'job.json', job)
        write(output / 'routes.json', [asdict(route) for route in routes])
        problem_path = output / 'run/input/problem.json'
        write(problem_path, {'problem_id': problem['problem_id'], 'claim': problem['claim'].strip()})
        for candidate in job['candidates']:
            cid = candidate['candidate_id']
            proof = read_bound(candidate['proof_path'], candidate['proof_file_sha256'])
            snapshot = output / 'run/input' / f'{cid}.lazy_checked.md'
            snapshot.write_bytes(proof)
            source = {'candidate_id': cid, 'proof_path': str(snapshot), 'proof_sha256': candidate['proof_sha256']}
            lanes[cid] = {'source': source, 'selected_stage': 'lazy_checked', 'failure': None,
                         'elapsed_seconds': 0.0, 'checkpoints': []}
        write(output / 'status.json', summary)
        if job['dry_run']:
            for cid in CANDIDATES:
                backend._case_manifest(problem_path=problem_path, proofs=[lanes[cid]['source']],
                    destination=output / 'run/lanes' / cid / 'input/r1_cycle_1_cases.json', cycle=1)
            summary.update(state='preflight_passed', model_calls=0)
        else:
            with policy.install(bf_module, job['variant'], output / 'continuations.jsonl', routes=routes), \
                    backend.runtime_generation_policy(model_timeout_sec=runtime['model_timeout_sec']), \
                    backend.inherited_component_caps():
                for cycle in range(1, 4):
                    active = [cid for cid in CANDIDATES if lanes[cid]['failure'] is None]
                    if not active:
                        break
                    verify_sources(sources)
                    print(f"{now()} {problem['problem_id']} {job['variant']}: refinement_{cycle}; lanes={','.join(active)}", flush=True)
                    summary.update(stage=f'refinement_{cycle}', active_lanes=active)
                    write(output / 'status.json', summary)
                    # These contexts patch shared module aliases. Install them
                    # once around all workers, never independently per lane.
                    with backend.mandatory_repair_boundary(qwen_endpoint=runtime['qwen_endpoint'],
                            gemma_endpoint=runtime['gemma_endpoint'], cycle_key=f'R1-C{cycle}',
                            model_timeout_sec=runtime['model_timeout_sec'], enable_exact_evidence=False):
                        def task(cid):
                            tick = time.monotonic()
                            try:
                                stage, terminal = backend.run_r1_cycle_lane(output_dir=output / 'run',
                                    candidate_id=cid, cycle=cycle, source_proof=dict(lanes[cid]['source']),
                                    problem_path=problem_path, gemma_endpoint=runtime['gemma_endpoint'],
                                    qwen_endpoint=runtime['qwen_endpoint'], seed_namespace=runtime['seed_namespace'],
                                    model_timeout_sec=runtime['model_timeout_sec'])
                                proof_path = checked_path(terminal['proof_path'])
                                require(proof_path.is_relative_to(output / 'run') and terminal['candidate_id'] == cid,
                                        'Terminal proof escaped lane identity or run')
                                require(text_digest(proof_path.read_bytes()) == terminal['proof_sha256'], 'Terminal proof hash mismatch')
                                return {'terminal': terminal, 'stage_dir': str(stage), 'elapsed_seconds': time.monotonic() - tick}
                            except Exception as error:
                                return {'error': error, 'elapsed_seconds': time.monotonic() - tick}
                        pool = ThreadPoolExecutor(max_workers=4)
                        try:
                            futures = {pool.submit(task, cid): cid for cid in active}
                            for future in as_completed(futures):
                                cid, result = futures[future], future.result()
                                lane = lanes[cid]
                                lane['elapsed_seconds'] += result['elapsed_seconds']
                                if 'error' in result:
                                    error = result['error']
                                    if isinstance(error, getattr(policy, 'PolicyError', ())):
                                        raise error
                                    lane['failure'] = {'stage': f'refinement_{cycle}', 'error_type': type(error).__name__,
                                                       'error': str(error), 'at': now()}
                                    print(f"{now()} {cid}: refinement_{cycle} failed; fallback={lane['selected_stage']}", flush=True)
                                else:
                                    lane['source'] = result['terminal']
                                    lane['selected_stage'] = f'refinement_{cycle}'
                                    lane['checkpoints'].append({'stage': lane['selected_stage'], 'stage_dir': result['stage_dir'],
                                        'proof_path': result['terminal']['proof_path'], 'proof_sha256': result['terminal']['proof_sha256'],
                                        'elapsed_seconds': result['elapsed_seconds']})
                                    print(f"{now()} {cid}: {lane['selected_stage']} completed; elapsed={result['elapsed_seconds']:.1f}s", flush=True)
                                summary['lanes'] = export_lanes(output, lanes)
                                write(output / 'status.json', summary)
                        except KeyboardInterrupt:
                            # Do not wait through long model deadlines before
                            # recording an interruption. The process entry point
                            # exits after the durable interrupted summary.
                            pool.shutdown(wait=False, cancel_futures=True)
                            raise
                        except BaseException:
                            # In-flight lanes still reference the shared policy
                            # and solver aliases. Drain them before any enclosing
                            # context restores those aliases after a fatal error.
                            pool.shutdown(wait=True, cancel_futures=True)
                            raise
                        else:
                            pool.shutdown(wait=True)
            summary['state'] = 'completed_with_fallbacks' if any(lane['failure'] for lane in lanes.values()) else 'completed'
        summary['lanes'] = export_lanes(output, lanes)
        verify_sources(sources)
        launcher.verify()
    except BaseException as error:
        summary['state'] = 'interrupted' if isinstance(error, KeyboardInterrupt) else 'failed'
        summary['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        summary.update(finished_at=now(), elapsed_seconds=time.monotonic() - began)
        try:
            verify_sources(sources)
            launcher.verify()
        except Exception as error:
            summary.update(state='failed', integrity_error=f'{type(error).__name__}: {error}')
            write(output / 'status.json', summary)
            write(output / 'summary.json', summary)
            raise
        write(output / 'status.json', summary)
        write(output / 'summary.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True, type=Path)
    parser.add_argument('--execute-models', action='store_true')
    args = parser.parse_args(argv)
    def interrupt(signum, frame):
        raise Interrupted(signum)
    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        run(args.job, execute_models=args.execute_models)
        return 0
    except Interrupted as error:
        print(str(error), file=sys.stderr, flush=True)
        # Python normally joins non-daemon executor threads at exit. This
        # process owns all of them, so terminate after run() persisted status.
        os._exit(128 + error.signum)
    except KeyboardInterrupt:
        # Covers direct KeyboardInterrupt as well as our signal-specific type.
        # Returning would let Python join any remaining model-call threads.
        os._exit(130)
    except Exception as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


if __name__ == '__main__':
    raise SystemExit(main())
