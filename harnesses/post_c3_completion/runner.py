"""Run one lazy check and conditional expansion on every saved final proof."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from . import VERSION, inputs
from harnesses.refinement_bf_ablation.runner import stop_child

ROOT = Path(__file__).resolve().parents[2]


def now():
    return datetime.now(timezone.utc).isoformat()


def code_hashes():
    files = list(Path(__file__).parent.glob('*.py')) + [ROOT / 'scripts/run_post_c3_completion.py']
    files += [ROOT / 'harnesses/refinement_bf_ablation' / (name + '.py') for name in ('inputs', 'worker', 'runner')]
    return {str(path): inputs.digest(path) for path in sorted(files)}


def create_plan(args):
    inputs.require(0 <= args.seed <= 0xffffffff, 'Seed must be uint32')
    output = args.output_dir.absolute()
    inputs.require(not output.exists() and not any(p.is_symlink() for p in (output, *output.parents)),
                   'Use a fresh, non-symlink --output-dir')
    output = output.resolve()
    archive = args.archive.resolve()
    inputs.require(not output.is_relative_to(archive) and not archive.is_relative_to(output),
                   'Keep experiment output separate from its source archive')
    inputs.require(not output.is_relative_to(inputs.RELEASE.parent)
                   and not inputs.RELEASE.is_relative_to(output), 'Output overlaps frozen releases')
    bank = inputs.load_archive(args.archive, None if args.all else args.problem_id, source_arm=args.source_arm)
    output.mkdir(parents=True, exist_ok=False)
    manifest_path = inputs.snapshot(bank, output / 'inputs')
    frozen = inputs.verify_manifest(manifest_path)
    jobs = []
    for row in frozen['problems']:
        pid = row['problem']['problem_id']
        job_path = output / 'jobs' / f'{pid}.json'
        directory = output / 'problems' / pid
        job = {'schema': 'post-c3-job-v1', 'dry_run': not args.execute_models,
               'source_arm': args.source_arm, 'processing_scope': 'all_saved_final_proofs',
               'output_dir': str(directory),
               'problem': row['problem'], 'candidates': row['candidates'],
               'runtime': {'gemma_endpoint': args.gemma_endpoint, 'workers': 4,
                           'model_timeout_sec': 14400, 'seed_namespace': f'post-c3-completion:{args.seed}:{pid}'},
               'input_manifest_path': str(manifest_path), 'input_manifest_sha256': inputs.digest(manifest_path)}
        inputs.write(job_path, job)
        jobs.append({'problem_id': pid, 'job_path': str(job_path), 'job_sha256': inputs.digest(job_path),
                     'output_dir': str(directory), 'log_path': str(output / 'logs' / (pid + '.log'))})
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout.strip()
    plan = {'schema': 'post-c3-plan-v1', 'version': VERSION, 'created_at': now(),
            'dry_run': not args.execute_models, 'source_archive': str(archive), 'source_arm': args.source_arm,
            'archive_manifest_sha256': frozen['archive_manifest_sha256'],
            'input_manifest_path': str(manifest_path), 'input_manifest_sha256': inputs.digest(manifest_path),
            'git_commit': commit, 'code_hashes': code_hashes(), 'seed': args.seed,
            'problem_count': len(frozen['problems']), 'processing_scope': 'all_saved_final_proofs',
            'final_candidates': sum(len(row['candidates']) for row in frozen['problems']),
            'c3_candidates': sum(c['selected_stage'] == 'refinement_3'
                for row in frozen['problems'] for c in row['candidates']),
            'earlier_stage_final_candidates': sum(c['selected_stage'] != 'refinement_3'
                for row in frozen['problems'] for c in row['candidates']),
            'bf_mode': 'original_chat_preserved_reasoning_and_answer', 'max_completion_passes': 1,
            'baseline_policy': 'Reuse source proofs and saved grades; never regenerate or regrade them',
            'jobs': jobs}
    path = output / 'plan.json'
    inputs.write(path, plan)
    return path


class Interrupted(KeyboardInterrupt):
    def __init__(self, signum):
        self.signum = signum
        super().__init__(f'Interrupted by signal {signum}')


def run_plan(path):
    path = Path(path).resolve()
    plan = inputs.read(path)
    plan_sha = inputs.digest(path)
    status_path = path.parent / 'status.json'
    status = {'schema': 'post-c3-status-v1', 'state': 'running', 'dry_run': plan['dry_run'],
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
            command = [sys.executable, '-u', '-B', '-m', 'harnesses.post_c3_completion.worker', '--job', job['job_path']]
            if not plan['dry_run']:
                command.append('--execute-models')
            pid = job['problem_id']
            print(f'{now()} {pid}: starting final-proof completion; log={log_path}', flush=True)
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


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    run = sub.add_parser('run', help='Default: offline preflight. Add --execute-models for generation.')
    run.add_argument('--archive', type=Path, default=inputs.DEFAULT_ARCHIVE)
    run.add_argument('--source-arm', choices=('B',), default='B')
    selection = run.add_mutually_exclusive_group(required=True)
    selection.add_argument('--problem-id', action='append', help='Repeat to select problems')
    selection.add_argument('--all', action='store_true', help='All six IMO problems; every saved final proof, including earlier-stage fallbacks')
    run.add_argument('--output-dir', type=Path, required=True)
    run.add_argument('--gemma-endpoint', default='http://127.0.0.1:8030/v1')
    run.add_argument('--seed', type=int, default=0, help='New final-proof completion seed namespace (uint32)')
    run.add_argument('--execute-models', action='store_true')
    report = sub.add_parser('report', help='Reuse baseline grades and optionally import changed-proof grades')
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
            plan = create_plan(args)
            print(f"Plan: {plan}\nMode: {'live models' if args.execute_models else 'offline dry run'}", flush=True)
            counts = inputs.read(plan)
            print(f"Source: {counts['source_arm']}; final proofs to check: {counts['final_candidates']}; "
                  f"from C3: {counts['c3_candidates']}; "
                  f"from earlier stages: {counts['earlier_stage_final_candidates']}", flush=True)
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
