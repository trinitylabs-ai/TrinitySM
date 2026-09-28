"""Run block-local raw-proof repair, one audit, and at most one resolve."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from . import VERSION, EXPERIMENT, SCOPE, TERMINAL_STAGES, strategy_config, inputs
from harnesses.refinement_bf_ablation.runner import stop_child

ROOT = Path(__file__).resolve().parents[2]


def now():
    return datetime.now(timezone.utc).isoformat()


def code_hashes():
    files = list(Path(__file__).parent.glob('*.py')) + [ROOT / 'scripts/run_block_local_completion.py']
    files += list((ROOT / 'harnesses/refinement_bf_ablation').glob('*.py'))
    files += list((ROOT / 'harnesses/post_c3_completion').glob('*.py'))
    return {str(path): inputs.digest(path) for path in sorted(files)}


def create_plan(args):
    inputs.require(0 <= args.seed <= 0xffffffff, 'Seed must be uint32')
    inputs.require(args.repair_temperature in (0.7, 0.4), 'Repair temperature must be 0.7 or 0.4')
    pipeline_config = strategy_config(args.strategy)
    inputs.require(args.strategy != 'original' or args.repair_temperature == 0.4,
                   'The original-harness control uses expansion temperature 0.4')
    output = args.output_dir.absolute()
    inputs.require(not output.exists() and not any(p.is_symlink() for p in (output, *output.parents)),
                   'Use a fresh, non-symlink --output-dir')
    output = output.resolve()
    for source in args.source_run:
        source = source.resolve()
        inputs.require(not output.is_relative_to(source) and not source.is_relative_to(output),
                       'Keep output separate from every native source run')
    inputs.require(not output.is_relative_to(inputs.RELEASE.parent)
                   and not inputs.RELEASE.is_relative_to(output), 'Output overlaps frozen releases')
    bank = inputs.load_sources(args.source_run,
        [f'imo2026_p{i}' for i in range(1, 7)] if args.all else args.problem_id)
    output.mkdir(parents=True, exist_ok=False)
    manifest_path = inputs.snapshot(bank, output / 'inputs')
    frozen = inputs.verify_manifest(manifest_path)
    jobs = []
    for row in frozen['problems']:
        pid = row['problem']['problem_id']
        job_path = output / 'jobs' / f'{pid}.json'
        directory = output / 'problems' / pid
        job = {'schema': 'block-local-job-v1', 'dry_run': not args.execute_models,
               'source_arm': 'raw', 'processing_scope': SCOPE, 'experiment': EXPERIMENT,
               'strategy': args.strategy, 'pipeline_config': pipeline_config,
               'output_dir': str(directory),
               'problem': row['problem'], 'candidates': row['candidates'],
               'runtime': {'gemma_endpoint': args.gemma_endpoint, 'qwen_endpoint': args.qwen_endpoint, 'workers': 4,
                           'repair_temperature': args.repair_temperature,
                           'model_timeout_sec': 14400, 'seed_namespace': f'block-local-raw:{args.seed}:{pid}'},
               'input_manifest_path': str(manifest_path), 'input_manifest_sha256': inputs.digest(manifest_path)}
        inputs.write(job_path, job)
        jobs.append({'problem_id': pid, 'job_path': str(job_path), 'job_sha256': inputs.digest(job_path),
                     'output_dir': str(directory), 'log_path': str(output / 'logs' / (pid + '.log'))})
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout.strip()
    plan = {'schema': 'block-local-plan-v1', 'version': VERSION, 'experiment': EXPERIMENT,
            'created_at': now(), 'dry_run': not args.execute_models, 'source_arm': 'raw',
            'source_runs': [str(p.resolve()) for p in args.source_run], 'processing_scope': SCOPE,
            'strategy': args.strategy, 'pipeline_config': pipeline_config,
            'repair_temperature': args.repair_temperature,
            'input_manifest_path': str(manifest_path), 'input_manifest_sha256': inputs.digest(manifest_path),
            'git_commit': commit, 'code_hashes': code_hashes(), 'seed': args.seed,
            'problem_count': len(frozen['problems']),
            'raw_candidates': sum(len(row['candidates']) for row in frozen['problems']),
            'bf_mode': 'original_chat_preserved_reasoning_and_answer',
            'terminal_stage': TERMINAL_STAGES[args.strategy], 'refinements_enabled': False,
            'baseline_policy': 'Grade the same raw drafts and repaired outputs separately twice; do not use final B grades',
            'jobs': jobs}
    path = output / 'plan.json'
    inputs.write(path, plan)
    return path


class Interrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum
        super().__init__(f'Interrupted by signal {signum}')


def run_plan(path, *, defer_reporting=False):
    path = Path(path).resolve()
    plan = inputs.read(path)
    plan_sha = inputs.digest(path)
    status_path = path.parent / 'status.json'
    status = {'schema': 'block-local-status-v1', 'state': 'running', 'dry_run': plan['dry_run'],
              'started_at': now(), 'plan_sha256': plan_sha, 'outcomes': []}
    tick, child = time.monotonic(), None
    def interrupt(signum, frame):
        raise Interrupted(signum)
    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    inputs.write(status_path, status)
    try:
        for job in plan['jobs']:
            inputs.require(inputs.digest(path) == plan_sha, 'Experiment plan changed')
            inputs.verify_sources(plan['code_hashes'])
            inputs.verify_manifest(plan['input_manifest_path'], plan['input_manifest_sha256'])
            inputs.require(inputs.digest(job['job_path']) == job['job_sha256'], 'Worker job changed')
            log_path = Path(job['log_path'])
            log_path.parent.mkdir(parents=True, exist_ok=True)
            module = 'original_worker' if plan['strategy'] == 'original' else 'worker'
            command = [sys.executable, '-u', '-B', '-m', f'harnesses.block_local_completion.{module}', '--job', job['job_path']]
            if not plan['dry_run']:
                command.append('--execute-models')
            pid = job['problem_id']
            print(f"{now()} {pid}: starting {plan['strategy']} repair at {plan['repair_temperature']}; log={log_path}", flush=True)
            status['active'] = {'problem_id': pid, 'log_path': str(log_path)}
            inputs.write(status_path, status)
            with log_path.open('x', encoding='utf-8') as log:
                child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUNBUFFERED': '1', 'PYTHONNOUSERSITE': '1'})
                while True:
                    try:
                        rc = child.wait(timeout=60)
                        break
                    except subprocess.TimeoutExpired:
                        state_path = Path(job['output_dir']) / 'status.json'
                        state = inputs.read(state_path) if state_path.exists() else {}
                        print(f"{now()} {pid}: {state.get('stage', state.get('state', 'starting'))}", flush=True)
            child = None
            inputs.verify_sources(plan['code_hashes'])
            summary_path = Path(job['output_dir']) / 'summary.json'
            summary = inputs.read(summary_path) if summary_path.exists() else {}
            status['outcomes'].append({'problem_id': pid, 'returncode': rc,
                'state': summary.get('state', 'missing_summary'), 'summary_path': str(summary_path),
                'summary_sha256': inputs.digest(summary_path) if summary_path.exists() else None})
            inputs.write(status_path, status)
            allowed = ('preflight_passed',) if plan['dry_run'] else ('completed', 'completed_with_fallbacks')
            inputs.require(rc == 0 and summary.get('state') in allowed, f'{pid} failed; see {log_path}')
            print(f"{now()} {pid}: {summary['state']}; elapsed={summary['elapsed_seconds']:.1f}s", flush=True)
        inputs.verify_manifest(plan['input_manifest_path'], plan['input_manifest_sha256'])
        if not defer_reporting:
            from .report import export_grading, write_report
            if not plan['dry_run']:
                export_grading(path)
            write_report(path)
        status['state'] = 'preflight_passed' if plan['dry_run'] else 'completed'
    except BaseException as error:
        status.update(state='interrupted' if isinstance(error, KeyboardInterrupt) else 'failed',
                      error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if child is not None:
            for sig in previous:
                signal.signal(sig, signal.SIG_IGN)
            stop_child(child)
        status.update(finished_at=now(), elapsed_seconds=time.monotonic() - tick)
        status.pop('active', None)
        inputs.write(status_path, status)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return status


def _run_arguments(run, *, paired=False):
    run.add_argument('--source-run', type=Path, action='append', required=True,
                     help='Native generation/run directory containing original raw producer receipts; repeat for split runs')
    selection = run.add_mutually_exclusive_group(required=True)
    selection.add_argument('--problem-id', action='append', help='Repeat to select problems')
    selection.add_argument('--all', action='store_true', help='All six IMO problems; require four saved raw proofs per problem')
    run.add_argument('--output-dir', type=Path, required=True)
    run.add_argument('--gemma-endpoint', default='http://127.0.0.1:8030/v1')
    run.add_argument('--qwen-endpoint', default='http://127.0.0.1:8027/v1')
    run.add_argument('--seed', type=int, default=0, help='New raw block-repair stage seed namespace (uint32)')
    run.add_argument('--execute-models', action='store_true')
    if not paired:
        run.add_argument('--repair-temperature', type=float, choices=(0.7, 0.4), default=0.7,
                         help='Expansion and resolve temperature, including BF (default: 0.7)')
        run.add_argument('--strategy', choices=('block', 'original'), default='block',
                         help='Original control preserves old lazy/expansion prompts; requires temperature 0.4')


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    _run_arguments(sub.add_parser('run', help='One temperature; defaults to offline preflight.'))
    _run_arguments(sub.add_parser('compare', help='Same raw inputs: block 0.7, block 0.4, original 0.4; batch 4.'), paired=True)
    report = sub.add_parser('report', help='Compare saved raw drafts and repaired proofs using separate two-pass grades')
    report.add_argument('--plan', type=Path, required=True)
    report.add_argument('--grades', type=Path)
    paired_report = sub.add_parser('compare-report', help='Compare three conditions with shared raw grades')
    paired_report.add_argument('--plan', type=Path, required=True)
    paired_report.add_argument('--grades', type=Path)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command in ('report', 'compare-report'):
            if args.command == 'compare-report':
                from .paired_report import write_report
            else:
                from .report import write_report
            print(write_report(args.plan.resolve(), args.grades.resolve() if args.grades else None))
        elif args.command == 'compare':
            from . import paired_runner
            path = paired_runner.create_plan(args)
            print(f'Comparison plan: {path}\nOrder: block 0.7, block 0.4, original 0.4; workers: 4 per stage', flush=True)
            paired_runner.run_plan(path)
            print(f'Results: {path.parent}', flush=True)
        else:
            plan = create_plan(args)
            print(f"Plan: {plan}\nMode: {'live models' if args.execute_models else 'offline dry run'}", flush=True)
            counts = inputs.read(plan)
            print(f"Source: saved raw drafts; candidates: {counts['raw_candidates']}; "
                  f"problems: {counts['problem_count']}; no refinements", flush=True)
            run_plan(plan)
            print(f'Results: {plan.parent}', flush=True)
        return 0
    except Interrupted as error:
        print(str(error), file=sys.stderr)
        return 128 + error.signum
    except KeyboardInterrupt:
        return 130
    except (ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
