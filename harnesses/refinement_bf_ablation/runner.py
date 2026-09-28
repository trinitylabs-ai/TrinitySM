"""Plan and run a paired, isolated experiment on chat extended reasoning continuation wording."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from . import VERSION, inputs, policy

ROOT = Path(__file__).resolve().parents[2]
VARIANTS = ('original', 'role_specific')


def now():
    return datetime.now(timezone.utc).isoformat()


def source_hashes():
    paths = sorted(Path(__file__).parent.glob('*.py'))
    paths.append(ROOT / 'scripts/run_refinement_bf_ablation.py')
    return {str(path): inputs.digest(path) for path in paths}


def create_plan(args):
    """Freeze shared inputs before starting either arm. No inference here."""
    seeds = args.pair_seed or [0]
    inputs.require(len(set(seeds)) == len(seeds) and all(0 <= seed <= 0xffffffff for seed in seeds),
                   'Use distinct uint32 --pair-seed values')
    inputs.require(args.source_run and args.problem_id, 'Specify --source-run and --problem-id')
    output = args.output_dir.absolute()
    inputs.require(not output.exists() and not output.is_symlink()
                   and all(not p.is_symlink() for p in output.parents), 'Use a fresh, non-symlink --output-dir')
    output = output.resolve()
    inputs.require(not output.is_relative_to(inputs.RELEASE.parent)
                   and not inputs.RELEASE.is_relative_to(output), 'Output overlaps frozen releases')
    for source in args.source_run:
        source = source.resolve()
        inputs.require(not output.is_relative_to(source) and not source.is_relative_to(output),
                       'Keep experiment output separate from source runs')
    bank = inputs.load_sources(args.source_run, args.problem_id)
    output.mkdir(parents=True, exist_ok=False)
    manifest = inputs.snapshot_inputs(bank, output / 'inputs')
    frozen = inputs.verify_manifest(manifest)
    pairs = []
    # Alternate AB/BA; seed determines the first order. With an odd number of
    # pairs, one order necessarily occurs once more than the other.
    first = int(hashlib.sha256(str(seeds[0]).encode()).hexdigest(), 16) % 2
    for seed in seeds:
        for row in frozen['problems']:
            problem, candidates = row['problem'], row['candidates']
            pid = problem['problem_id']
            pair_id = f'{pid}__seed{seed}'
            order = list(VARIANTS if (len(pairs) + first) % 2 == 0 else reversed(VARIANTS))
            arms = {}
            runtime = {'gemma_endpoint': args.gemma_endpoint, 'qwen_endpoint': args.qwen_endpoint,
                       'model_timeout_sec': args.model_timeout_sec, 'workers': 4,
                       'seed_namespace': f'refinement-bf-ablation:{seed}:{pid}:r1'}
            for variant in VARIANTS:
                job_path = output / 'jobs' / f'{pair_id}__{variant}.json'
                arm_output = output / 'pairs' / pair_id / variant
                log_path = output / 'logs' / f'{pair_id}__{variant}.log'
                job = {'schema': 'refinement-bf-job-v1', 'variant': variant,
                       'output_dir': str(arm_output), 'problem': problem, 'candidates': candidates,
                       'runtime': runtime, 'input_manifest_path': str(manifest),
                       'input_manifest_sha256': inputs.digest(manifest), 'pair_seed': seed,
                       'pair_id': pair_id, 'dry_run': not args.execute_models}
                inputs.write(job_path, job)
                arms[variant] = {'job_path': str(job_path), 'job_sha256': inputs.digest(job_path),
                                 'output_dir': str(arm_output), 'log_path': str(log_path)}
            pairs.append({'pair_id': pair_id, 'problem_id': pid, 'pair_seed': seed,
                          'arm_order': order, 'arms': arms})
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True,
                            capture_output=True, check=True).stdout.strip()
    plan = {'schema': 'refinement-bf-plan-v1', 'version': VERSION, 'created_at': now(),
            'dry_run': not args.execute_models, 'git_commit': commit,
            'source_hashes': source_hashes(), 'release_sha256': frozen['release_sha256'],
            'input_manifest_path': str(manifest), 'input_manifest_sha256': inputs.digest(manifest),
            'policy_id': policy.POLICY_ID, 'role_specific_cues': policy.ROLE_SPECIFIC_CUES,
            'contrast': 'Original chat extended reasoning versus role-specific chat extended reasoning; original seed derivation retained',
            'primary_metric': 'For each problem: mean of four proof scores, each averaged over two grading passes',
            'final_proof_policy': 'Last completed proof per lane: refinement_3, refinement_2, refinement_1, lazy_checked',
            'pairs': pairs}
    path = output / 'plan.json'
    inputs.write(path, plan)
    return path


class Interrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum
        super().__init__(f'Interrupted by signal {signum}')


def stop_child(child):
    """Signal only the process group created by this runner, then reap it."""
    if child.poll() is not None:
        return
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait()


def run_plan(path):
    path = Path(path).resolve()
    plan_sha = inputs.digest(path)
    plan = inputs.read(path)
    status_path = path.parent / 'status.json'
    status = {'schema': 'refinement-bf-status-v1', 'state': 'running', 'dry_run': plan['dry_run'],
              'started_at': now(), 'outcomes': [], 'plan_sha256': plan_sha}
    began, child = time.monotonic(), None
    inputs.write(status_path, status)
    def interrupt(signum, frame):
        raise Interrupted(signum)
    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        for pair in plan['pairs']:
            for variant in pair['arm_order']:
                inputs.require(inputs.digest(path) == plan_sha, 'Experiment plan changed')
                inputs.verify_sources(plan['source_hashes'])
                inputs.verify_manifest(plan['input_manifest_path'], plan['input_manifest_sha256'])
                arm = pair['arms'][variant]
                inputs.require(inputs.digest(arm['job_path']) == arm['job_sha256'], 'Arm job changed')
                log_path = Path(arm['log_path'])
                log_path.parent.mkdir(parents=True, exist_ok=True)
                command = [sys.executable, '-u', '-B', '-m', 'harnesses.refinement_bf_ablation.worker',
                           '--job', arm['job_path']]
                if not plan['dry_run']:
                    command.append('--execute-models')
                label = pair['pair_id'] + ' / ' + variant
                print(f'{now()} starting {label}; log={log_path}', flush=True)
                status['active'] = {'pair_id': pair['pair_id'], 'variant': variant, 'log_path': str(log_path)}
                inputs.write(status_path, status)
                with log_path.open('x', encoding='utf-8') as log:
                    child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUNBUFFERED': '1', 'PYTHONNOUSERSITE': '1'})
                    while True:
                        try:
                            returncode = child.wait(timeout=60)
                            break
                        except subprocess.TimeoutExpired:
                            state_path = Path(arm['output_dir']) / 'status.json'
                            state = inputs.read(state_path) if state_path.exists() else {}
                            print(f"{now()} {label}: {state.get('stage', state.get('state', 'starting'))}", flush=True)
                child = None
                inputs.verify_sources(plan['source_hashes'])
                summary_path = Path(arm['output_dir']) / 'summary.json'
                summary = inputs.read(summary_path) if summary_path.exists() else {}
                status['outcomes'].append({'pair_id': pair['pair_id'], 'variant': variant,
                    'returncode': returncode, 'state': summary.get('state', 'missing_summary'),
                    'summary_path': str(summary_path), 'summary_sha256': inputs.digest(summary_path) if summary_path.exists() else None})
                inputs.write(status_path, status)
                expected = ('preflight_passed',) if plan['dry_run'] else ('completed', 'completed_with_fallbacks')
                inputs.require(returncode == 0 and summary.get('state') in expected, f'Arm failed: {label}; see {log_path}')
                print(f"{now()} completed {label}; state={summary['state']}; elapsed={summary['elapsed_seconds']:.1f}s", flush=True)
        inputs.verify_manifest(plan['input_manifest_path'], plan['input_manifest_sha256'])
        from .report import export_grading, write_report
        if not plan['dry_run']:
            export_grading(path)
        write_report(path)
        status.update(state='preflight_passed' if plan['dry_run'] else 'completed')
    except BaseException as error:
        status.update(state='interrupted' if isinstance(error, KeyboardInterrupt) else 'failed',
                      error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if child is not None:
            # Ignore repeated terminal signals while reaping our child group.
            for sig in previous:
                signal.signal(sig, signal.SIG_IGN)
            stop_child(child)
        status.update(finished_at=now(), elapsed_seconds=time.monotonic() - began)
        status.pop('active', None)
        inputs.write(status_path, status)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return status


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='command', required=True)
    run = commands.add_parser('run', help='Snapshot inputs and run A/B; default: offline dry run')
    run.add_argument('--source-run', type=Path, action='append', required=True)
    run.add_argument('--problem-id', action='append', required=True)
    run.add_argument('--pair-seed', type=int, action='append', help='Paired seed-policy namespace; repeat for multiple seeds (default: 0)')
    run.add_argument('--output-dir', type=Path, required=True)
    run.add_argument('--gemma-endpoint', default='http://127.0.0.1:8030/v1')
    run.add_argument('--qwen-endpoint', default='http://127.0.0.1:8027/v1')
    run.add_argument('--model-timeout-sec', type=int, default=600)
    run.add_argument('--execute-models', action='store_true', help='Run inference on existing pinned local model servers')
    report = commands.add_parser('report', help='Validate results and optionally import two-pass grades')
    report.add_argument('--plan', type=Path, required=True)
    report.add_argument('--grades', type=Path)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'report':
            from .report import write_report
            print(write_report(args.plan.resolve(), args.grades.resolve() if args.grades else None))
        else:
            path = create_plan(args)
            print(f"Plan: {path}\nMode: {'live models' if args.execute_models else 'offline dry run'}", flush=True)
            run_plan(path)
            print(f'Results: {path.parent}', flush=True)
        return 0
    except Interrupted as error:
        print(str(error), file=sys.stderr)
        return 128 + error.signum
    except KeyboardInterrupt:
        return 130
    except (ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
