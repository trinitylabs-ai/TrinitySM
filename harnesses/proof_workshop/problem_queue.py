#!/usr/bin/env python3
"""Schedule each problem through C3 using the unchanged, verified engine workers."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pipeline


def interrupted_exit(code):
    if code < 0:
        return 128 - code
    return code if code in (130, 143) else None


class ProblemInterrupted(Exception):
    def __init__(self, returncode):
        self.returncode = returncode
        super().__init__(f'Problem process interrupted (exit {returncode})')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verified_engine(version):
    if version not in pipeline.SUPPORTED_RELEASES:
        raise ValueError('Unsupported implementation release')
    release = pipeline.IMPLEMENTATION / 'releases' / version
    registry = pipeline.read(release.parent / 'index.json')['releases']
    if pipeline.sha(release / 'release.json') != registry[version]:
        raise ValueError('Registered release manifest changed')
    manifest = pipeline.read(release / 'release.json')
    if pipeline.sha(release / 'launch.py') != manifest['files']['launch.py']:
        raise ValueError('Registered release launcher changed')
    launcher = load('workshop_sequence_release', release / 'launch.py')
    manifest, profile = launcher.verify()
    queue = load('workshop_sequence_engine', release / 'engine/source/scripts/run_v263_v290.py')
    return release, launcher, manifest, profile, queue


def run_worker(queue, root, row, *, dry_run):
    problem_id = row['problem_id']
    destination = root / 'problems' / problem_id
    destination.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, '-B', str(Path(queue.__file__).resolve()),
               '--output-dir', str(root), '--_worker', problem_id,
               '--dry-run' if dry_run else '--execute-models']
    environment = dict(os.environ)
    environment.pop('PYTHONHOME', None)
    environment.update(PYTHONPATH=str(queue.REPO), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    environment = pipeline.runtime_policy.environment(root, environment)
    with (destination / 'worker.log').open('a') as log:
        child = subprocess.Popen(command, cwd=queue.REPO, env=environment,
                                 stdout=log, stderr=subprocess.STDOUT)
        try:
            while True:
                try:
                    return child.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    queue.report(f'{problem_id}: {queue.progress(root, row)}')
        except BaseException:
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
            raise


def finish_problem(root, problem_id, version):
    source = root / 'problems' / problem_id / '02_r1_cycles'
    # An earlier failed lane can coexist with valid C2 checkpoints for others.
    # Only the latter are eligible for another inference stage.
    issues = []
    targets = pipeline.optional_record(source / 'score_targets.json', issues)
    if not targets:
        return ({f'{problem_id}/{candidate}': f'Cannot read C2 checkpoint: {issues}'
                 for candidate in pipeline.CANDIDATES} if issues else {})
    manifest = pipeline.read(source / 'manifest.json')
    rows = [proof for checkpoint in targets['checkpoints']
            if checkpoint['checkpoint'] == 'R1-C2' for proof in checkpoint['proofs']]
    available = {proof['candidate_id'] for proof in rows}
    candidates = manifest['candidate_ids']
    if not set(candidates) <= set(pipeline.CANDIDATES) or not available <= set(candidates):
        raise ValueError('Unexpected candidate in the completed C2 portfolio')

    def finish(candidate):
        try:
            proofs = [row for row in rows if row['candidate_id'] == candidate]
            if len(proofs) != 1:
                raise ValueError('Duplicate completed C2 checkpoint')
            pipeline.bound_proof(proofs[0], candidate, source)
            pipeline.finish_lane(root, source, candidate, problem_id, version, sys.executable)
            return candidate, None, None
        except Exception as error:
            stopped = (interrupted_exit(error.returncode)
                       if isinstance(error, subprocess.CalledProcessError) else None)
            return candidate, f'{type(error).__name__}: {error}', stopped

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(finish, [c for c in candidates if c in available]))
    for _, _, stopped in outcomes:
        if stopped is not None:
            raise ProblemInterrupted(stopped)
    errors = {f'{problem_id}/{candidate}': error for candidate, error, _ in outcomes if error}
    if version in pipeline.AUDITED_RELEASES:
        pipeline.write(root / 'status.json', {'state': 'running', 'problem_id': problem_id, 'stage': 'post_resolver_audit'})
        try:
            pipeline.run_post_resolver_audit(root, problem_id, version, sys.executable)
        except subprocess.CalledProcessError as error:
            stopped = interrupted_exit(error.returncode)
            if stopped is not None:
                raise ProblemInterrupted(stopped) from error
            for candidate in available:
                errors.setdefault(f'{problem_id}/{candidate}', f'Audit worker failed: {error}; retain R2')
    return errors


def run_sequence(args, version, queue):
    root = args.output_dir
    manifest = queue.freeze_queue(args)
    skipped = set(args.skip_failed_problem or [])
    if skipped and (not args.resume or not skipped <= {r['problem_id'] for r in manifest['problems']}):
        raise ValueError('Failed-problem skips require resume and IDs in the frozen queue')
    for problem_id in skipped:
        queue.validate_failed_portfolio(root / 'problems' / problem_id, problem_id)
    sequence = {'schema': 'workshop-problem-sequence-v1',
                'scheduling_policy': pipeline.SCHEDULING_POLICY,
                'scheduler_sha256': pipeline.sha(Path(__file__)),
                'state': 'running', 'inference_finished': False,
                'attempted_problems': [], 'completed_problems': [],
                'problems': [], 'lane_errors': {}}

    def progress(**values):
        sequence.update(values)
        pipeline.write(root / 'problem_sequence.json', sequence)

    for index, row in enumerate(manifest['problems'], 1):
        problem_id = row['problem_id']
        started = time.monotonic()
        problem = {'problem_id': problem_id, 'started_at': datetime.now(timezone.utc).isoformat(),
                   'resumed': bool(getattr(args, 'sequence_resumed', False)),
                   'worker_returncode': 0, 'state': 'running', 'lanes': []}
        sequence['problems'].append(problem)
        sequence['attempted_problems'].append(problem_id)
        progress(problem_id=problem_id, index=index, total=len(manifest['problems']), stage='draft_through_R1-C2')
        summary = root / 'problems' / problem_id / 'summary.json'
        discovery_issues = []
        prior = pipeline.optional_record(summary, discovery_issues)
        errors, worker_error, stopped = {}, None, None
        if problem_id in skipped:
            worker_error = 'Preserving a validated failed portfolio without further inference'
            queue.report(f'{problem_id}: {worker_error}')
        elif prior.get('state') not in queue.TERMINAL_STATES:
            pipeline.write(root / 'status.json', {'state': 'running', 'problem_id': problem_id,
                                                  'index': index, 'total': len(manifest['problems'])})
            queue.report(f'{problem_id}: starting {index}/{len(manifest["problems"])} through R1-C3')
            code = run_worker(queue, root, row, dry_run=args.dry_run)
            problem['worker_returncode'] = code
            stopped = interrupted_exit(code)
            if code:
                worker_error = f'Worker exited with status {code}; preserving completed lanes'
                queue.report(f'{problem_id}: {worker_error}')
        else:
            queue.report(f'{problem_id}: reusing completed inner-engine work')
        if not args.dry_run and stopped is None and problem_id not in skipped:
            progress(stage='R1-C3')
            pipeline.write(root / 'status.json', {'state': 'running', 'problem_id': problem_id,
                                                  'stage': 'R1-C3', 'index': index,
                                                  'total': len(manifest['problems'])})
            queue.report(f'{problem_id}: finishing R1-C3 before the next problem')
            try:
                errors = finish_problem(root, problem_id, version)
            except ProblemInterrupted as error:
                stopped = error.returncode
                worker_error = str(error)
            except Exception as error:
                worker_error = f'{type(error).__name__}: {error}'
        if not args.dry_run and stopped is None and version in pipeline.VOTER_RELEASES and problem_id not in skipped:
            progress(stage='cross_lane_voter')
            pipeline.write(root / 'status.json', {'state': 'running', 'problem_id': problem_id, 'stage': 'cross_lane_voter'})
            try:
                problem['cross_lane_voter'] = pipeline.cross_lane_selection(root, problem_id, version, execute=True)
            except subprocess.CalledProcessError as error:
                stopped = interrupted_exit(error.returncode)
                problem['cross_lane_voter'] = {'state': 'unavailable', 'reason': str(error)}
            except Exception as error:
                problem['cross_lane_voter'] = {'state': 'unavailable', 'reason': f'{type(error).__name__}: {error}'}
        if not args.dry_run:
            for candidate in pipeline.CANDIDATES:
                key = f'{problem_id}/{candidate}'
                issues = list(discovery_issues)
                error = errors.get(key)
                try:
                    selected = pipeline.collect_lane(root, problem_id, candidate, issues)
                except Exception as failure:
                    selected = None
                    issues.append({'reason': f'{type(failure).__name__}: {failure}'})
                lane = {'candidate_id': candidate, 'proof_available': selected is not None}
                if selected:
                    lane.update({name: selected[name] for name in
                                 ('selected_stage', 'proof_path', 'proof_sha256', 'completion_record')})
                    if 'post_resolver_audit' in selected:
                        lane['post_resolver_audit'] = selected['post_resolver_audit']
                        if selected['post_resolver_audit']['decision'] != 'ACCEPT_CANDIDATE':
                            error = error or 'Post-resolver audit retained R2'
                if not selected or selected['selected_stage'] != 'refinement_3':
                    error = error or worker_error
                if error or not selected or selected['selected_stage'] != 'refinement_3':
                    error = error or ('No completed proof' if not selected else
                                      f'Using last completed {selected["selected_stage"]} proof')
                    lane['error'] = error
                    sequence['lane_errors'][key] = error
                if issues:
                    lane['recovery_issues'] = issues
                problem['lanes'].append(lane)
        missing = any(not lane['proof_available'] for lane in problem['lanes'])
        if not args.dry_run and version in pipeline.VOTER_RELEASES:
            missing = missing or problem.get('cross_lane_voter', {}).get('state') != 'completed'
        fallback = any(lane['proof_available'] and lane['selected_stage'] != 'refinement_3'
                       for lane in problem['lanes'])
        if worker_error:
            problem['worker_error'] = worker_error
        problem.update(completed_at=datetime.now(timezone.utc).isoformat(),
                       elapsed_seconds=time.monotonic() - started,
                       state='interrupted' if stopped else 'missing_proofs' if missing else
                             'completed_with_fallbacks' if fallback else 'completed')
        if stopped:
            progress(state='interrupted', error=worker_error, returncode=stopped)
            pipeline.write(root / 'status.json', {'state': 'interrupted', 'problem_id': problem_id,
                                                 'returncode': stopped})
            return stopped
        if args.dry_run and problem['worker_returncode']:
            progress(state='failed', returncode=problem['worker_returncode'])
            return problem['worker_returncode']
        if not missing:
            sequence['completed_problems'].append(problem_id)
        progress(stage='preflight_complete' if args.dry_run else 'proofs_collected')
        queue.report(f'{problem_id}: {problem["state"]}; elapsed={problem["elapsed_seconds"]:.1f}s; continuing queue')
    missing = any(p['state'] == 'missing_proofs' for p in sequence['problems'])
    state = ('dry_run_completed' if args.dry_run else 'failed' if missing else
             'completed_with_fallbacks' if any(p['state'] == 'completed_with_fallbacks'
                                              for p in sequence['problems']) else 'completed')
    progress(state=state, inference_finished=not args.dry_run, returncode=1 if missing else 0)
    pipeline.write(root / 'status.json', {'state': state, 'problem_count': len(sequence['problems']),
                                          'missing_proofs': sum(not lane['proof_available']
                                              for p in sequence['problems'] for lane in p['lanes'])})
    return 1 if missing else 0


def main(argv=None):
    selector = argparse.ArgumentParser(add_help=False)
    selector.add_argument('--release', default='1.7.0')
    selected, remaining = selector.parse_known_args(argv)
    release, launcher, manifest, profile, queue = verified_engine(selected.release)
    parser = launcher.options(profile)
    args = parser.parse_args(remaining)
    if not args.problem_dir or not args.output_dir or not (args.dry_run or args.execute_models):
        parser.error('Provide --problem-dir, --output-dir, and --dry-run or --execute-models')
    root = args.output_dir.resolve()
    args.output_dir = root
    if root.is_relative_to(release.parent.resolve()) or release.resolve().is_relative_to(root):
        raise ValueError('Run output must be outside the versioned releases')
    if args.resume:
        if not (root / 'harness_release.json').is_file():
            raise ValueError('This is not a run created by this composite release')
    elif root.exists():
        raise FileExistsError(f'Use a new output directory: {root}')
    parameters = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()
                  if key not in ('resume', 'skip_failed_problem', 'verify', 'version', 'output_dir')}
    parameters['problem_dir'] = str(args.problem_dir.resolve())
    identity = {'schema': 'imo-proof-pipeline-run-v1', 'name': manifest['name'], 'version': manifest['version'],
                'release_sha256': pipeline.sha(release / 'release.json'), 'upstream': manifest['upstream'],
                'profile_sha256': manifest['files']['profile.json'], 'parameters': parameters}
    # A resumed run uses its captured policy, never the current checkout's code.
    policy = (pipeline.read(root / 'harness_release.json').get('label_recovery') if args.resume
              else pipeline.runtime_policy.binding(selected.release))
    if policy is not None:
        identity['label_recovery'] = policy
    selector = (pipeline.read(root / 'harness_release.json').get('final_selector') if args.resume
                else pipeline.selector_policy.binding(selected.release))
    if selector is not None:
        identity['final_selector'] = selector
    if args.resume and pipeline.read(root / 'harness_release.json') != identity:
        raise ValueError('Resume changes release or run configuration')
    if args.resume:
        pipeline.runtime_policy.saved(root)
        pipeline.selector_policy.saved(root)
    queue.collect_problems(args.problem_dir, args.problem_id, args.limit)
    if args.skip_failed_problem and not args.resume:
        raise ValueError('--skip-failed-problem requires --resume')
    observed = {} if args.dry_run else {
        role: launcher.server_settings(getattr(args, role + '_endpoint'), expected)
        for role, expected in profile['servers'].items()}
    root.mkdir(parents=True, exist_ok=args.resume)
    with ExitStack() as locks:
        for name in ('.composite.lock', 'queue.lock'):
            lock = locks.enter_context((root / name).open('a'))
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        queue.freeze_queue(args)
        if not args.resume:
            pipeline.write(root / 'harness_release.json', identity)
            pipeline.runtime_policy.prepare(root, release / 'engine/source')
            pipeline.selector_policy.prepare(root, release / 'engine/source')
        record = root / f'composite_launch_{len(list(root.glob("composite_launch_*.json"))):03d}.json'
        with record.open('x') as handle:
            json.dump({'command': [sys.executable, '-B', str(Path(__file__)), *(argv or sys.argv[1:])],
                       'cwd': str(pipeline.ROOT), 'python': sys.executable, 'python_version': sys.version,
                       'verified_servers': observed, 'scheduling_policy': pipeline.SCHEDULING_POLICY,
                       'scheduler_sha256': pipeline.sha(Path(__file__))}, handle, indent=2)
            handle.write('\n')
        # The full queue identity is fixed once. Each worker retains the original
        # problem ordinal, source paths, runtime settings and seed derivation.
        args.sequence_resumed = args.resume
        args.resume = True
        return run_sequence(args, selected.release, queue)


if __name__ == '__main__':
    raise SystemExit(main())
