#!/usr/bin/env python3
"""Split a drained raw-generation run into two disjoint GPU queues."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import shlex
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('raw_harness', HERE / 'run.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(source, output, endpoint1):
    source, output = source.resolve(), output.resolve()
    if (output / 'split_manifest.json').exists():
        raise ValueError('This split is already prepared; resume its individual shards')
    # The original client's thread pool must have drained before importing files.
    with (source / '.lock').open('a') as source_lock:
        fcntl.flock(source_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        original = harness.read(source / 'manifest.json')
        config = original['config']
        if original['schema'] != harness.SCHEMA or config['runner_sha256'] != digest(HERE / 'run.py'):
            raise ValueError('Source run does not use this frozen raw harness')
        if config['budget_forcing'] or config['mtp_speculative_tokens'] != 4:
            raise ValueError('Unexpected source generation policy')
        problems = original['problems']
        midpoint = (len(problems) + 1) // 2
        if midpoint == len(problems):
            raise ValueError('At least two problems are needed for a split')
        endpoint1 = harness.endpoint_url(endpoint1)
        if endpoint1 == config['endpoint']:
            raise ValueError('The two queues require distinct endpoints')
        shards, imported, source_results = [], [], {}
        output.mkdir(parents=True, exist_ok=True)
        for name in ('status.json', 'summary.json'):
            shutil.copy2(source / name, output / ('source_before_split_' + name))
        # Retain original numbering even if the source selection was a subset.
        input_dir = output / 'numbering_inputs'
        input_dir.mkdir(exist_ok=True)
        maximum = max(p['problem_number'] for p in problems)
        by_number = {p['problem_number']: p for p in problems}
        if len(by_number) != len(problems):
            raise ValueError('Source problem numbers are not unique')
        # This migration expects the complete directory selection, as in Basic 1–30.
        if sorted(by_number) != list(range(1, maximum + 1)):
            raise ValueError('Split the full numbered source queue to preserve seed identities')
        for problem in problems:
            harness.write(input_dir / f"{problem['problem_id']}.json",
                          {'problem_id': problem['problem_id'], 'problem': problem['problem']})
        for gpu, assigned, endpoint in [(0, problems[:midpoint], config['endpoint']),
                                        (1, problems[midpoint:], endpoint1)]:
            shard = output / f'gpu{gpu}'
            command = [sys.executable, '-u', '-B', str(HERE / 'run.py'),
                '--problem-dir', str(input_dir), '--output-dir', str(shard), '--endpoint', endpoint,
                '--max-tokens', str(config['max_tokens']), '--timeout-sec', str(config['timeout_sec']),
                '--raw-seed-offset', str(config['raw_seed_offset'])]
            for problem in assigned:
                command += ['--problem-id', problem['problem_id']]
            args = harness.parse_args(command[4:])
            staged = harness.run(args)
            for task in staged['rows']:
                pid, cid = task['problem_id'], task['candidate_id']
                target = Path(task['result_path']).parent
                origin = source / 'problems' / pid / 'candidates' / cid
                request = harness.read(target / 'request.json')
                if request != harness.read(origin / 'request.json'):
                    raise ValueError(f'Split changed the generation payload: {pid}/{cid}')
                key = harness.sha(json.dumps(request, sort_keys=True))
                cached = harness.cached_result(origin, key)
                if cached is None:
                    continue
                source_results[pid, cid] = cached
                original_result_hash = digest(origin / 'result.json')
                shutil.copytree(origin, target, dirs_exist_ok=True)
                copied = dict(cached, imported_from=str(origin / 'result.json'),
                              imported_result_file_sha256=original_result_hash)
                if copied.get('proof_path'):
                    copied['proof_path'] = str(target / 'draft_proof.md')
                    assert digest(target / 'draft_proof.md') == digest(origin / 'draft_proof.md')
                harness.write(target / 'result.json', copied)
                assert harness.cached_result(target, key)
                imported.append({'problem_id': pid, 'candidate_id': cid, 'state': copied['state'],
                    'source_result': str(origin / 'result.json'), 'source_result_file_sha256': original_result_hash,
                    'destination_result': str(target / 'result.json'), 'proof_sha256': copied.get('proof_sha256')})
            # Refresh shard summaries using imported results, without network calls.
            args.resume = True
            harness.run(args)
            command += ['--resume', '--execute-models']
            launch = shard / 'launch.sh'
            launch.write_text('#!/bin/bash\nset -euo pipefail\nexec ' + shlex.join(command)
                              + ' >> ' + shlex.quote(str(shard / 'worker.log')) + ' 2>&1\n')
            shards.append({'gpu': gpu, 'endpoint': endpoint, 'output_dir': str(shard),
                'problem_ids': [p['problem_id'] for p in assigned], 'command': command, 'launch_script': str(launch)})
        ids = [pid for shard in shards for pid in shard['problem_ids']]
        assert len(ids) == len(set(ids)) == len(problems)
        manifest = {'schema': 'gemma4-raw-no-bf-dual-gpu-v1', 'created_at': harness.now(),
            'source_run': str(source), 'source_manifest_sha256': digest(source / 'manifest.json'),
            'runner_sha256': config['runner_sha256'], 'generation_config': config,
            'budget_forcing': False, 'mtp_speculative_tokens': 4, 'total_problems': len(problems),
            'total_proofs': len(problems) * 4, 'shards': shards, 'imported': imported,
            'all_generation_requests_identical_to_source': True}
        harness.write(output / 'split_manifest.json', manifest)
        previous = harness.read(source / 'summary.json')
        tasks = [{k: row[k] for k in ('problem_id', 'problem_number', 'candidate_id', 'checkpoint', 'request_path', 'result_path')}
                 for row in previous['rows']]
        harness.summarize(source, tasks, source_results, 'continued_in_dual_gpu_run')
        harness.write(source / 'continuation.json', {'output_dir': str(output), 'at': harness.now(),
            'split_manifest': str(output / 'split_manifest.json'), 'imported_candidates': len(imported)})
    return aggregate(output)


def aggregate(output):
    manifest = harness.read(output / 'split_manifest.json')
    rows, shards = [], []
    for shard in manifest['shards']:
        summary = harness.read(Path(shard['output_dir']) / 'summary.json')
        expected = {(pid, cid) for pid in shard['problem_ids'] for cid, _, _ in harness.CANDIDATES}
        actual = {(r['problem_id'], r['candidate_id']) for r in summary['rows']}
        if expected != actual or len(summary['rows']) != len(expected):
            raise ValueError('Shard coverage changed')
        rows += [dict(r, gpu=shard['gpu'], endpoint=shard['endpoint']) for r in summary['rows']]
        shards.append({'gpu': shard['gpu'], 'state': summary['state'],
            'active_problem': summary['active_problem'], 'finished': summary['finished'], 'total': summary['total']})
    keys = {(r['problem_id'], r['candidate_id']) for r in rows}
    assert len(keys) == len(rows) == manifest['total_proofs']
    terminal = all(s['state'] in {'completed', 'completed_with_issues'} for s in shards)
    state = ('completed' if all(r['state'] == 'completed' for r in rows) else 'completed_with_issues') if terminal else 'running'
    value = {'schema': manifest['schema'], 'state': state, 'updated_at': harness.now(),
        'total': len(rows), 'finished': sum(r['state'] != 'pending' for r in rows),
        'counts': dict(Counter(r['state'] for r in rows)), 'proofs_saved': sum(bool(r.get('proof_path')) for r in rows),
        'budget_forcing': False, 'mtp_speculative_tokens': 4,
        'imported_candidates': len(manifest['imported']), 'shards': shards, 'rows': rows}
    harness.write(output / 'summary.json', value)
    harness.write(output / 'status.json', {k: v for k, v in value.items() if k != 'rows'})
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-run', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--gpu1-endpoint', default='http://127.0.0.1:8031/v1')
    parser.add_argument('--monitor', action='store_true')
    args = parser.parse_args()
    if args.source_run:
        value = prepare(args.source_run, args.output_dir, args.gpu1_endpoint)
        print(json.dumps({k: v for k, v in value.items() if k != 'rows'}), flush=True)
    if args.monitor:
        previous = None
        while True:
            value = aggregate(args.output_dir)
            signature = value['finished'], value['state'], tuple(s['active_problem'] for s in value['shards'])
            if signature != previous:
                print(json.dumps({k: v for k, v in value.items() if k != 'rows'}), flush=True)
                previous = signature
            if value['state'] in {'completed', 'completed_with_issues'}:
                break
            time.sleep(15)


if __name__ == '__main__':
    main()
