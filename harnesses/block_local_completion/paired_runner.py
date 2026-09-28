"""Freeze and run block 0.7, block 0.4, then original full-proof repair 0.4."""
from __future__ import annotations

import argparse
from pathlib import Path
import signal
import time

from . import EXPERIMENT, SCOPE, VERSION, inputs, runner

SCHEMA = 'block-local-paired-plan-v1'
ARMS = (('t07', 0.7, 'block'), ('t04', 0.4, 'block'), ('original_t04', 0.4, 'original'))


def _bank_identity(bank):
    """Snapshot paths differ; every source byte and its provenance must agree."""
    return {**bank, 'problems': [
        {**row, 'candidates': [
            {key: value for key, value in candidate.items() if key != 'proof_path'}
            for candidate in row['candidates']]}
        for row in bank['problems']]}


def _job_identity(job):
    return {key: value for key, value in {
        **job,
        'candidates': [{key: value for key, value in c.items() if key != 'proof_path'}
                       for c in job['candidates']],
        'runtime': {key: value for key, value in job['runtime'].items()
                    if key != 'repair_temperature'},
    }.items() if key not in ('output_dir', 'input_manifest_path', 'input_manifest_sha256',
                            'strategy', 'pipeline_config')}


def verify_pair(plan):
    """Validate every frozen condition before permitting any model calls."""
    inputs.require(plan.get('schema') == SCHEMA and plan.get('experiment') == EXPERIMENT
                   and plan.get('processing_scope') == SCOPE and plan.get('source_arm') == 'raw',
                   'Unsupported paired experiment')
    inputs.require(type(plan.get('seed')) is int and 0 <= plan['seed'] <= 0xffffffff
                   and type(plan.get('dry_run')) is bool, 'Invalid paired seed or execution mode')
    inputs.require(plan.get('repair_temperatures') == [0.7, 0.4, 0.4]
                   and [(a.get('label'), a.get('repair_temperature'), a.get('strategy'))
                        for a in plan['arms']] == list(ARMS),
                   'Matched conditions must run block 0.7, block 0.4, then original 0.4')
    inputs.verify_sources(plan['code_hashes'])
    reference_bank, reference_jobs, reference_config = None, None, None
    for arm in plan['arms']:
        strategy = arm['strategy']
        expected_config = runner.strategy_config(strategy)
        expected_terminal = runner.TERMINAL_STAGES[strategy]
        path = Path(arm['plan_path'])
        inputs.require(path.is_absolute() and inputs.digest(path) == arm['plan_sha256'], 'Child plan changed')
        child = inputs.read(path)
        inputs.require(child.get('schema') == 'block-local-plan-v1'
                       and child.get('seed') == plan['seed'] and child.get('dry_run') is plan['dry_run']
                       and child.get('strategy') == strategy
                       and child.get('pipeline_config') == expected_config
                       and child.get('terminal_stage') == expected_terminal
                       and child.get('repair_temperature') == arm['repair_temperature']
                       and child.get('code_hashes') == plan['code_hashes'], 'Child arm configuration changed')
        bank = inputs.verify_manifest(child['input_manifest_path'], child['input_manifest_sha256'])
        inputs.verify_sources(bank['source_hashes'])
        config = {key: child[key] for key in (
            'version', 'experiment', 'source_arm', 'processing_scope', 'source_runs',
            'git_commit', 'bf_mode', 'refinements_enabled', 'baseline_policy', 'problem_count', 'raw_candidates')}
        jobs = []
        inputs.require(len(child['jobs']) == len(bank['problems']), 'Child job count differs from input bank')
        for entry, row in zip(child['jobs'], bank['problems']):
            inputs.require(inputs.digest(entry['job_path']) == entry['job_sha256'], 'Worker job changed')
            job = inputs.read(entry['job_path'])
            runtime = job.get('runtime', {})
            inputs.require(entry['problem_id'] == row['problem']['problem_id']
                           and job.get('problem') == row['problem'] and job.get('candidates') == row['candidates']
                           and job.get('input_manifest_path') == child['input_manifest_path']
                           and job.get('input_manifest_sha256') == child['input_manifest_sha256']
                           and job.get('dry_run') is plan['dry_run']
                           and job.get('strategy') == strategy
                           and job.get('pipeline_config') == expected_config
                           and runtime.get('workers') == 4
                           and runtime.get('seed_namespace') == f"block-local-raw:{plan['seed']}:{entry['problem_id']}"
                           and runtime.get('repair_temperature') == arm['repair_temperature'],
                           'Child job does not preserve the matched four-lane input and seed')
            jobs.append(_job_identity(job))
        identity = _bank_identity(bank)
        if reference_bank is None:
            reference_bank, reference_jobs, reference_config = identity, jobs, config
        else:
            inputs.require(identity == reference_bank, 'Paired arms have different raw inputs or provenance')
            inputs.require(jobs == reference_jobs, 'Paired jobs differ beyond repair temperature and strategy')
            inputs.require(config == reference_config, 'Paired plans differ beyond repair temperature and strategy')
        inputs.require(child['problem_count'] == plan['problem_count']
                       and child['raw_candidates'] == plan['raw_candidates']
                       and child['source_runs'] == plan['source_runs'], 'Paired counts or source runs differ')


def create_plan(args):
    inputs.require(type(args.seed) is int and 0 <= args.seed <= 0xffffffff, 'Seed must be uint32')
    output = Path(args.output_dir).absolute()
    inputs.require(not output.exists() and not any(p.is_symlink() for p in (output, *output.parents)),
                   'Use a fresh, non-symlink --output-dir')
    output = output.resolve()
    for source in args.source_run:
        source = Path(source).resolve()
        inputs.require(not output.is_relative_to(source) and not source.is_relative_to(output),
                       'Keep output separate from every native source run')
    inputs.require(not output.is_relative_to(inputs.RELEASE.parent)
                   and not inputs.RELEASE.is_relative_to(output), 'Output overlaps frozen releases')
    # Every condition is completely frozen before this function returns a runnable plan.
    arms = []
    for label, temperature, strategy in ARMS:
        child_args = argparse.Namespace(**vars(args))
        child_args.output_dir = output / label
        child_args.repair_temperature = temperature
        child_args.strategy = strategy
        child_path = runner.create_plan(child_args)
        arms.append({'label': label, 'repair_temperature': temperature, 'strategy': strategy,
                     'plan_path': str(child_path), 'plan_sha256': inputs.digest(child_path)})
    first = inputs.read(arms[0]['plan_path'])
    plan = {'schema': SCHEMA, 'version': VERSION, 'experiment': EXPERIMENT,
            'processing_scope': SCOPE, 'source_arm': 'raw', 'created_at': runner.now(),
            'dry_run': not args.execute_models, 'seed': args.seed, 'repair_temperatures': [0.7, 0.4, 0.4],
            'arms': arms, 'code_hashes': runner.code_hashes(), 'source_runs': first['source_runs'],
            'problem_count': first['problem_count'], 'raw_candidates': first['raw_candidates']}
    verify_pair(plan)
    path = output / 'pair_plan.json'
    inputs.write(path, plan)
    return path


def run_plan(path):
    path = Path(path).resolve()
    plan = inputs.read(path)
    plan_sha = inputs.digest(path)
    status_path = path.parent / 'paired_status.json'
    inputs.require(not status_path.exists(), 'Paired experiment already started; use a fresh output directory')
    verify_pair(plan)
    for arm in plan['arms']:
        inputs.require(not (Path(arm['plan_path']).parent / 'status.json').exists(),
                       'A child arm already started; use a fresh paired experiment')
    status = {'schema': 'block-local-paired-status-v1', 'state': 'running', 'dry_run': plan['dry_run'],
              'started_at': runner.now(), 'plan_sha256': plan_sha, 'outcomes': []}
    tick = time.monotonic()

    def interrupt(signum, frame):
        raise runner.Interrupted(signum)

    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
    inputs.write(status_path, status)
    try:
        for arm in plan['arms']:
            inputs.require(inputs.digest(path) == plan_sha, 'Paired plan changed')
            verify_pair(plan)
            child_path = Path(arm['plan_path'])
            child_status_path = child_path.parent / 'status.json'
            started, arm_tick = runner.now(), time.monotonic()
            status['active'] = {'label': arm['label'], 'repair_temperature': arm['repair_temperature'],
                                'strategy': arm['strategy'],
                                'plan_path': str(child_path), 'status_path': str(child_status_path)}
            inputs.write(status_path, status)
            print(f"{runner.now()} {arm['label']}: starting all selected problems with {arm['strategy']} "
                  f"repair at temperature "
                  f"{arm['repair_temperature']}", flush=True)
            try:
                result = runner.run_plan(child_path, defer_reporting=True)
            except BaseException as error:
                result = {'state': 'interrupted' if isinstance(error, KeyboardInterrupt) else 'failed'}
                raise
            finally:
                outcome = {**status['active'], 'state': result['state'], 'started_at': started,
                           'finished_at': runner.now(), 'elapsed_seconds': time.monotonic() - arm_tick,
                           'status_sha256': inputs.digest(child_status_path) if child_status_path.exists() else None}
                status['outcomes'].append(outcome)
                inputs.write(status_path, status)
            expected = 'preflight_passed' if plan['dry_run'] else 'completed'
            inputs.require(result['state'] == expected, f"{arm['label']} did not finish successfully")
        inputs.require(inputs.digest(path) == plan_sha, 'Paired plan changed')
        verify_pair(plan)
        from .paired_report import export_grading, write_report
        if not plan['dry_run']:
            export_grading(path)
        write_report(path)
        status['state'] = 'preflight_passed' if plan['dry_run'] else 'completed'
    except BaseException as error:
        status.update(state='interrupted' if isinstance(error, KeyboardInterrupt) else 'failed',
                      error=f'{type(error).__name__}: {error}')
        raise
    finally:
        status.update(finished_at=runner.now(), elapsed_seconds=time.monotonic() - tick)
        status.pop('active', None)
        inputs.write(status_path, status)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return status
