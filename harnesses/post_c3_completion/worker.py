"""Apply one isolated lazy check and conditional completion to all saved final proofs."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
from urllib.parse import urlsplit

from harnesses.refinement_bf_ablation import worker as frozen

CANDIDATES = frozen.CANDIDATES
RELEASE = frozen.RELEASE
LAZY_STAGE = r'lazy_check_attempt[0-9]+(?:_bounded_cap_recovery)?'
EXPANSION_STAGE = r'lazy_in_place_resolve_attempt[0-9]+(?:_cap_continuation)?'
LAZY_USER = 'Scan the submitted proof now.'
EXPANSION_USER = 'Expand the current proof in place. Return only the required repair envelope.'


class IntegrityError(RuntimeError):
    """An input or completed artifact no longer matches its recorded identity."""


def require(condition, message):
    if not condition:
        raise IntegrityError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def seed_for(namespace, candidate_id):
    return int.from_bytes(hashlib.sha256(f'{namespace}:{candidate_id}'.encode()).digest()[:4], 'big') or 1


def stage_seed(candidate_seed, stage):
    return int.from_bytes(hashlib.sha256(f'v047:{candidate_seed}:{stage}'.encode()).digest()[:4], 'big') or 1


def validate_job(path):
    from . import inputs
    path = frozen.checked_path(str(Path(path).absolute()))
    data = path.read_bytes()
    job = json.loads(data)
    require(isinstance(job, dict) and job.get('schema') == 'post-c3-job-v1', 'Invalid post-C3 job schema')
    require(job.get('processing_scope') == 'all_saved_final_proofs',
            'This worker requires processing_scope=all_saved_final_proofs; create a fresh job')
    require(type(job.get('dry_run')) is bool, 'Job must specify dry_run')
    require(job.get('source_arm') in ('A', 'B'), 'Source arm must be A or B')
    manifest_path = frozen.checked_path(job.get('input_manifest_path'))
    bank = inputs.verify_manifest(manifest_path, expected_sha=job.get('input_manifest_sha256'))
    problem, candidates = job.get('problem'), job.get('candidates')
    matching = [row for row in bank['problems'] if row['problem'] == problem]
    require(bank.get('source_arm') == job['source_arm'] and len(matching) == 1 and
            matching[0]['candidates'] == candidates, 'Job differs from its bound input bank')
    require([row['candidate_id'] for row in candidates] == list(CANDIDATES), 'Expected four canonical lanes')
    runtime = job.get('runtime')
    require(isinstance(runtime, dict) and set(runtime) == {
        'gemma_endpoint', 'model_timeout_sec', 'workers', 'seed_namespace'}, 'Unexpected runtime fields')
    require(type(runtime['workers']) is int and runtime['workers'] == 4, 'Expected four workers')
    require(type(runtime['model_timeout_sec']) is int and runtime['model_timeout_sec'] == 14400,
            'The original frontend uses a 14400-second request timeout')
    require(isinstance(runtime['seed_namespace'], str) and bool(runtime['seed_namespace'].strip()), 'Empty seed namespace')
    url = urlsplit(runtime['gemma_endpoint'])
    require(url.scheme == 'http' and url.hostname in ('127.0.0.1', 'localhost', '::1') and
            url.path.rstrip('/') == '/v1' and not url.query and not url.fragment and not url.username,
            'Expected a local Gemma /v1 endpoint')
    output = frozen.checked_path(job.get('output_dir'))
    require(not output.exists() and not output.is_relative_to(RELEASE.parent)
            and not RELEASE.is_relative_to(output), 'Use a fresh output outside frozen releases')
    sources = {str(path): frozen.digest(data), str(manifest_path): job['input_manifest_sha256']}
    for candidate in candidates:
        proof_path = frozen.checked_path(candidate['proof_path'])
        proof = frozen.read_bound(proof_path, candidate['proof_file_sha256'])
        require(frozen.text_digest(proof) == candidate['proof_sha256'], 'Source proof text hash changed')
        sources[str(proof_path)] = frozen.digest(proof)
    return job, sources


def verify_sources(sources):
    try:
        frozen.verify_sources(sources)
    except Exception as error:
        raise IntegrityError(str(error)) from error


def route(role, pattern, system):
    return {'role': role, 'stage_pattern': pattern, 'prompt_sha256': frozen.digest(system.encode())}


def unique_routes(routes):
    return list({(r['role'], r['stage_pattern'], r['prompt_sha256']): r for r in routes}.values())


@contextmanager
def lazy_prompt_adapter(frontend):
    """Replace only the frontend's proof-scanning prompt in this process."""
    from . import prompts
    module = sys.modules[frontend.run_lazy_check.__module__]
    original = module.lazy_phrasing
    module.lazy_phrasing = prompts.lazy_phrasing
    try:
        yield
    finally:
        module.lazy_phrasing = original


@contextmanager
def expansion_prompt_adapter(runtime, systems):
    """Keep the frozen envelope prompt and add only user-level completion guidance."""
    from . import prompts, policy
    original = runtime.gemma_call
    had_instance_value = 'gemma_call' in runtime.__dict__
    saved_instance_value = runtime.__dict__.get('gemma_call')
    def call(**kwargs):
        if (kwargs.get('name') != 'lazy_in_place_resolve' or
                kwargs.get('system_prompt') not in systems or kwargs.get('user_prompt') != EXPANSION_USER):
            raise policy.PolicyError('Unexpected call reached the post-C3 expansion adapter')
        return original(**{**kwargs, 'user_prompt': EXPANSION_USER + '\n\n' + prompts.EXPANSION_GUIDANCE})
    runtime.gemma_call = call
    try:
        yield
    finally:
        if had_instance_value:
            runtime.gemma_call = saved_instance_value
        else:
            del runtime.gemma_call


def run_batch(ids, task, on_result, *, policy_error):
    """Drain in-flight calls before restoring shared prompt or BF contexts."""
    pool = ThreadPoolExecutor(max_workers=4)
    try:
        futures = {pool.submit(task, cid): cid for cid in ids}
        for future in as_completed(futures):
            cid = futures[future]
            try:
                value = future.result()
            except (IntegrityError, policy_error):
                raise
            except Exception as error:
                value = {'error': error}
            on_result(cid, value)
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    except BaseException:
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)


def export_lanes(output, lanes):
    exported = []
    for cid in CANDIDATES:
        lane = lanes[cid]
        data = lane['_proof_bytes']
        proof_path = output / 'proofs' / f'{cid}.md'
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_bytes(data)
        exported.append({key: value for key, value in lane.items() if not key.startswith('_')} | {
            'proof_path': str(proof_path), 'proof_file_sha256': frozen.digest(data),
            'proof_sha256': frozen.text_digest(data), 'changed': frozen.digest(data) != lane['source_proof_file_sha256']})
    return exported


def record_prompts(output, cid, name, system, user, cue):
    directory = output / 'prompts' / cid
    directory.mkdir(parents=True, exist_ok=True)
    for kind, value in (('system', system), ('user', user), ('continuation', cue)):
        (directory / f'{name}.{kind}.txt').write_text(value, encoding='utf-8')
    return {kind + '_sha256': frozen.digest(value.encode()) for kind, value in (
        ('system', system), ('user', user), ('continuation', cue))}


def run(job_path, *, execute_models=False):
    from . import policy, prompts
    job, sources = validate_job(job_path)
    require(job['dry_run'] != bool(execute_models), 'Live jobs require --execute-models; dry runs must omit it')
    launcher, release_manifest, profile = frozen.load_release()
    backend = frozen.load_backend()
    frontend = backend.v108.v097
    runtime = frontend.GPU0FourSlotStageRuntime(frontend.RuntimeConfig(gemma_endpoint=job['runtime']['gemma_endpoint']))
    require((runtime.config.lazy_max_tokens, runtime.config.solver_max_tokens, runtime.config.protocol_attempts)
            == (16384, 65536, 2), 'Frozen frontend cap/recovery configuration changed')
    original_expansion = sys.modules[frontend.run_lazy_resolve.__module__]
    bf = backend.v263.parent._budget_forcing
    servers = {} if job['dry_run'] else {'gemma': launcher.server_settings(
        job['runtime']['gemma_endpoint'], profile['servers']['gemma'])}
    verify_sources(sources)
    output = frozen.checked_path(job['output_dir'])
    output.mkdir(parents=True, exist_ok=False)
    began = time.monotonic()
    problem = job['problem']
    summary = {'schema': 'post-c3-result-v1', 'problem_id': problem['problem_id'], 'source_arm': job['source_arm'],
        'processing_scope': job['processing_scope'],
        'job_sha256': sources[str(frozen.checked_path(str(Path(job_path).absolute())))],
        'input_manifest_path': job['input_manifest_path'], 'input_manifest_sha256': job['input_manifest_sha256'],
        'runtime': job['runtime'], 'dry_run': job['dry_run'], 'state': 'running', 'started_at': now(),
        'release_identity': {'release': release_manifest['version'],
            'release_sha256': frozen.digest((RELEASE / 'release.json').read_bytes()), 'verified_servers': servers},
        'elapsed_seconds': 0.0, 'lanes': [], 'grading_performed': False, 'mathematically_verified': False,
        'pipeline': 'saved_final_proof_then_one_lazy_check_then_at_most_one_conditional_expansion',
        'budget_forcing': 'original_chat_reasoning_and_response_full_replacement'}
    lanes, rows, timings = {}, {}, {}
    try:
        frozen.write(output / 'job.json', job)
        frozen.write(output / 'input/problem.json', {'problem_id': problem['problem_id'], 'claim': problem['claim'].strip()})
        for candidate in job['candidates']:
            cid = candidate['candidate_id']
            data = frozen.read_bound(candidate['proof_path'], candidate['proof_file_sha256'])
            snapshot = output / 'input' / f'{cid}.md'
            snapshot.write_bytes(data)
            seed = seed_for(job['runtime']['seed_namespace'], cid)
            lanes[cid] = {'candidate_id': cid, 'source_stage': candidate['selected_stage'],
                'source_proof_path': candidate['proof_path'], 'source_proof_file_sha256': candidate['proof_file_sha256'],
                'operation': 'preflight_only',
                'failure': None, 'elapsed_seconds': 0.0, '_proof_bytes': data,
                'seeds': {'candidate': seed, 'lazy_check': stage_seed(seed, 'lazy_check'),
                          'expansion': stage_seed(seed, 'lazy_in_place_resolve')}}
            rows[cid] = {'candidate_id': cid, 'proof': snapshot.read_text(encoding='utf-8').strip(),
                'proof_sha256': candidate['proof_sha256'], 'seed': seed, 'temperature': 1.0 if cid.startswith('t10') else 0.7}
        eligible = list(CANDIDATES)
        lazy_systems = {cid: prompts.lazy_phrasing(rows[cid]['proof']) for cid in eligible}
        lazy_routes = unique_routes(route('lazy_check', LAZY_STAGE, system) for system in lazy_systems.values())
        for cid in eligible:
            lanes[cid]['lazy_prompt'] = record_prompts(output, cid, 'lazy_check', lazy_systems[cid], LAZY_USER, prompts.LAZY_CONTINUATION)
        frozen.write(output / 'lazy_routes.json', lazy_routes)
        summary['lanes'] = export_lanes(output, lanes)
        frozen.write(output / 'status.json', summary)
        if job['dry_run']:
            summary.update(state='preflight_passed', model_calls=0)
        else:
            scans = {}
            def completed(cid, value, phase):
                lanes[cid]['elapsed_seconds'] += time.monotonic() - timings[cid]
                if 'error' in value:
                    error = value['error']
                    lanes[cid].update(operation='failed', failure={'stage': phase,
                        'error_type': type(error).__name__, 'error': str(error), 'at': now()})
                    print(f'{now()} {cid}: {phase} failed; retaining original source proof', flush=True)
                elif phase == 'lazy_check':
                    scan = value['scan']
                    scans[cid] = scan
                    lanes[cid].update(lazy_report=scan['lazy_report'], lazy_report_sha256=scan['lazy_report_sha256'],
                        has_lazy_issues=scan['has_lazy_issues'], native_lazy_generation=scan['lazy_generation'])
                    lanes[cid]['operation'] = 'no_issues' if not scan['has_lazy_issues'] else 'awaiting_expansion'
                    print(f"{now()} {cid}: lazy check completed; issues={scan['has_lazy_issues']}", flush=True)
                else:
                    lanes[cid].update(operation='expanded', _proof_bytes=value['proof_bytes'],
                        conclusion_action=value['result']['conclusion_action'], native_expansion=value['result'])
                    print(f'{now()} {cid}: one expansion completed', flush=True)
                summary['lanes'] = export_lanes(output, lanes)
                frozen.write(output / 'status.json', summary)
            if eligible:
                summary['stage'] = 'lazy_check'
                frozen.write(output / 'status.json', summary)
                def check(cid):
                    timings[cid] = time.monotonic()
                    verify_sources(sources)
                    scan = frontend.run_lazy_check(runtime=runtime, output_dir=output / 'run', row=dict(rows[cid]))
                    report = str(scan['lazy_report']).strip()
                    require(report and scan['candidate_id'] == cid and scan['proof_sha256'] == rows[cid]['proof_sha256'],
                            'Lazy output lost its source identity')
                    require(scan['lazy_report_sha256'] == frozen.digest(report.encode()) and
                            scan['has_lazy_issues'] is (report != 'NO_ISSUES'), 'Lazy report identity changed')
                    return {'scan': scan}
                with lazy_prompt_adapter(frontend), policy.install(bf, output / 'lazy_continuations.jsonl', routes=lazy_routes):
                    run_batch(eligible, check, lambda cid, value: completed(cid, value, 'lazy_check'), policy_error=policy.PolicyError)
            verify_sources(sources)
            expanding = [cid for cid in eligible if cid in scans and scans[cid]['has_lazy_issues']]
            expansion_systems = {cid: original_expansion.lazy_in_place_expansion_prompt(
                problem=problem['claim'].strip(), current_proof=rows[cid]['proof'], local_gaps=scans[cid]['lazy_report'])
                for cid in expanding}
            expansion_routes = unique_routes(route('expansion', EXPANSION_STAGE, system) for system in expansion_systems.values())
            for cid in expanding:
                lanes[cid]['expansion_prompt'] = record_prompts(output, cid, 'expansion', expansion_systems[cid],
                    EXPANSION_USER + '\n\n' + prompts.EXPANSION_GUIDANCE, prompts.EXPANSION_CONTINUATION)
            frozen.write(output / 'expansion_routes.json', expansion_routes)
            if expanding:
                summary['stage'] = 'conditional_expansion'
                frozen.write(output / 'status.json', summary)
                def expand(cid):
                    timings[cid] = time.monotonic()
                    verify_sources(sources)
                    result = frontend.run_lazy_resolve(runtime=runtime, problem=problem['claim'].strip(),
                        output_dir=output / 'run', row=scans[cid])
                    generation = result.get('expansion_generation')
                    if not isinstance(generation, dict) or not isinstance(generation.get('text'), str):
                        raise ValueError('Expansion has no complete generated envelope')
                    parsed = original_expansion.expansion_parser(generation['text'])
                    if not parsed.get('valid') or not str(parsed.get('proof') or '').strip():
                        raise ValueError('Expansion did not return a valid complete proof envelope')
                    proof_path = frozen.checked_path(result['checked_proof_path'])
                    require(proof_path.is_relative_to(output / 'run') and result['candidate_id'] == cid,
                            'Expansion output escaped its run or lane')
                    data = proof_path.read_bytes()
                    expected = frozen.digest(str(parsed['proof']).strip().encode())
                    require(frozen.text_digest(data) == expected == result['checked_proof_sha256'] and
                            result['conclusion_action'] == parsed['conclusion_action'], 'Expansion proof differs from parsed envelope')
                    return {'result': result, 'proof_bytes': data}
                with expansion_prompt_adapter(runtime, set(expansion_systems.values())), \
                        policy.install(bf, output / 'expansion_continuations.jsonl', routes=expansion_routes):
                    run_batch(expanding, expand, lambda cid, value: completed(cid, value, 'expansion'), policy_error=policy.PolicyError)
            summary['state'] = 'completed_with_fallbacks' if any(lane['failure'] for lane in lanes.values()) else 'completed'
            summary['stage'] = 'finished'
        summary['lanes'] = export_lanes(output, lanes)
        verify_sources(sources)
    except BaseException as error:
        summary.update(state='interrupted' if isinstance(error, KeyboardInterrupt) else 'failed',
                       error=f'{type(error).__name__}: {error}')
        raise
    finally:
        summary.update(finished_at=now(), elapsed_seconds=time.monotonic() - began)
        try:
            verify_sources(sources)
            launcher.verify()
        except Exception as error:
            summary.update(state='failed', integrity_error=f'{type(error).__name__}: {error}')
            frozen.write(output / 'summary.json', summary)
            frozen.write(output / 'status.json', summary)
            raise
        frozen.write(output / 'summary.json', summary)
        frozen.write(output / 'status.json', summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True, type=Path)
    parser.add_argument('--execute-models', action='store_true')
    args = parser.parse_args(argv)
    def interrupt(signum, frame):
        raise frozen.Interrupted(signum)
    old = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        run(args.job, execute_models=args.execute_models)
        return 0
    except frozen.Interrupted as error:
        print(str(error), file=sys.stderr, flush=True)
        os._exit(128 + error.signum)
    except KeyboardInterrupt:
        os._exit(130)
    except Exception as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    finally:
        for sig, handler in old.items():
            signal.signal(sig, handler)


if __name__ == '__main__':
    raise SystemExit(main())
