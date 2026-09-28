#!/usr/bin/env python3
"""Offline, resumable vote recovery and reporting for a pinned ProofBench suite.

No HTTP/model/grader invocation. Native outputs, source manifests and frozen
release files are read-only. A detached monitor can recover subsequent cases.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import time
import traceback


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
REPO = HERE if (HERE / 'harnesses').exists() else HERE.parent
recovery = load_module('vote_format_recovery', REPO / 'harnesses/cross_lane_voter/mechanical_recovery.py')


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def exact(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Recovery artifact changed: ' + str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(data)
        tmp = Path(stream.name)
    tmp.replace(path)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def setup(config):
    source = Path(config['repo']) / 'harnesses/imo_proof_pipeline/releases' / config['release'] / 'engine/source'
    sys.path.insert(0, str(source))
    from experiments.local_math_verifier.cross_lane_voter import live, validation
    from experiments.local_math_verifier.post_resolver_audit.bindings import verify_audit_binding
    return live, validation, verify_audit_binding


def saved_vote(root, task, destination, api):
    live, validation, binding_check = api
    folder = root / 'cases' / task['case_id']
    original = read(folder / 'result.json')
    require(not original.get('valid'), 'Refusing to replace an already valid native vote')
    if (folder / 'audit/call_result.json').exists():
        return saved_canonical_vote(root, task, destination, api)
    fallback = folder / 'audit/deadline_fallback'
    metadata_path = fallback / 'answer_only/answer_only_completion.metadata.json'
    raw_path = fallback / 'answer_only/answer_only_completion.raw_response.json'
    failure_path = fallback / 'failure.json'
    require('Duplicate Markdown section:' in read(failure_path)['error'], 'Not the duplicated-comparison failure')
    metadata, raw = read(metadata_path), read(raw_path)
    require(metadata['finish_reason'] == 'stop', 'Transport did not finish normally')
    require(len(raw['choices']) == 1 and raw['choices'][0]['finish_reason'] == 'stop', 'Incomplete or ambiguous transport')
    require(raw['id'] == metadata['response_id'] and raw['model'] == metadata['model'], 'Transport identity mismatch')
    require(Path(metadata['response_path']).resolve() == raw_path.resolve(), 'Transport response path mismatch')
    message = raw['choices'][0]['message']
    require(message['role'] == 'assistant' and not message.get('tool_calls'), 'Unexpected response type')
    text = message['content']
    require(isinstance(text, str) and bool(text.strip()), 'Empty response')
    normalized, repair = recovery.recover_final_comparison(text, validation.strict_parse)
    require(repair is not None, 'Response does not need this recovery rule')
    parsed = validation.strict_parse(normalized)
    # Keep full original response for unchanged transport-binding verification.
    final_path = destination / task['case_id'] / 'original_response.md'
    exact(final_path, text.encode())
    call = {'text': text, 'metadata': metadata, 'final_path': str(final_path),
            'final_sha256': recovery.sha(text)}
    result = {**original, 'audit_sha256': call['final_sha256']}
    verified = binding_check(root, task, result, call)
    sources = dict(verified['source_hashes'])
    sources.pop(str(final_path))
    for path in (folder / 'result.json', metadata_path, raw_path, failure_path):
        sources[str(path)] = digest(path)
    vote = {k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order', 'presentation_order')}
    vote.update(parsed, response_sha256=call['final_sha256'], binding_verified=True,
                selected_candidate=task['presentation_order'][0 if parsed['winner_label'] == 'A' else 1],
                elapsed_seconds=original.get('elapsed_seconds'), mechanical_recovery=repair,
                timeout_fallback={'action': 'reuse_saved_answer_only_continuation_offline'})
    record = {'policy': recovery.POLICY, 'source_root': str(root), 'task': task,
              'original_failure': original, 'binding': verified['binding'],
              'source_hashes': sources, 'transport_response_sha256': digest(raw_path),
              'recovery': repair, 'vote': vote, 'additional_model_calls': 0}
    exact(final_path.with_name('normalized_response.md'), normalized.encode())
    exact(final_path.with_name('receipt.json'), encoded(record))
    return vote, record


def saved_canonical_vote(root, task, destination, api):
    _, validation, binding_check = api
    folder = root / 'cases' / task['case_id']
    call_path = folder / 'audit/call_result.json'
    original, call = read(folder / 'result.json'), read(call_path)
    require(not original.get('valid'), 'Cannot replace valid vote')
    verified = binding_check(root, task, original, call)
    metadata = call['metadata']
    raw_path = Path(metadata['response_path'])
    raw = read(raw_path)
    require(metadata['finish_reason'] == 'stop' and len(raw['choices']) == 1 and
            raw['choices'][0]['finish_reason'] == 'stop', 'Incomplete transport')
    require(raw['id'] == metadata['response_id'] and raw['model'] == metadata['model'], 'Transport identity mismatch')
    require(raw['choices'][0]['message']['content'] == call['text'], 'Raw transport differs from canonical response')
    normalized, repair = recovery.recover_comparison(call['text'], validation.strict_parse)
    require(repair is not None, 'No applicable mechanical repair')
    parsed = validation.strict_parse(normalized)
    sources = dict(verified['source_hashes'])
    for path in (call_path, raw_path, folder / 'result.json'):
        sources[str(path)] = digest(path)
    vote = {k: task[k] for k in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order', 'presentation_order')}
    vote.update(parsed, response_sha256=call['final_sha256'], binding_verified=True,
                selected_candidate=task['presentation_order'][0 if parsed['winner_label'] == 'A' else 1],
                elapsed_seconds=original.get('elapsed_seconds'), mechanical_recovery=repair,
                timeout_fallback=metadata.get('comparison_timeout_policy'))
    record = {'policy': repair['policy'], 'source_root': str(root), 'task': task,
              'original_failure': original, 'binding': verified['binding'],
              'source_hashes': sources, 'transport_response_sha256': digest(raw_path),
              'recovery': repair, 'vote': vote, 'additional_model_calls': 0}
    d = destination / task['case_id']
    exact(d / 'original_response.md', call['text'].encode())
    exact(d / 'normalized_response.md', normalized.encode())
    exact(d / 'receipt.json', encoded(record))
    return vote, record


def recover_problem(config, job, api, write=False):
    live, _, _ = api
    base = Path(job['output'])
    manifest_path = base / 'manifest.json'
    report_path = base / 'reports/REPORT.json'
    if not manifest_path.exists() or not report_path.exists():
        return {'state': 'waiting_for_completed_generation_and_grading'}
    manifest = read(manifest_path)
    if manifest.get('selection', {}).get('state') == 'completed':
        return {'state': 'native_selection_complete'}
    require((base / 'generation/completion.json').exists(), 'Generation still running')
    report = read(report_path)
    if report['quality'] != 'graded':
        return {'state': 'waiting_for_grading'}
    roots = list((base / 'generation/run/cross_lane_voter' / job['problem_id']).glob('*/audit_plan.json'))
    require(len(roots) == 1, 'Expected exactly one bound voter plan')
    root = roots[0].parent
    _, voter_manifest, tasks = live.verify(root)
    votes = [live.verified_vote(root, task) for task in tasks]
    failed = [i for i, vote in enumerate(votes) if not vote['valid']]
    require(bool(failed), 'Native selection incomplete without invalid calls')
    slug = ('explicit_comparison_format_v2' if any(
        (root / 'cases' / tasks[i]['case_id'] / 'audit/call_result.json').exists() for i in failed)
        else 'unique_final_comparison_v1')
    output = base / 'selection_recovery' / slug
    with tempfile.TemporaryDirectory(prefix='vote-recovery-') as scratch:
        destination = output if write else Path(scratch)
        records = []
        for i in failed:
            vote, record = saved_vote(root, tasks[i], destination, api)
            votes[i] = vote
            records.append(record)
        selection = live.summarize(voter_manifest, votes)
        require(selection['state'] == 'completed', 'Some votes remain unresolved')
        winner = selection['summaries']['combined']['winner']
        selection['selected_candidate'] = winner
        policies = sorted({r['policy'] for r in records})
        policy = policies[0] if len(policies) == 1 else policies
        selection['mechanical_recovery_policy'] = policy
        selection['native_selection_unchanged'] = True
        if not write:
            return {'state': 'recoverable', 'winner': winner, 'summaries': selection['summaries']}
        # Selection is now fixed. Only the reporting phase reads existing grades.
        lane = next(row for row in manifest['lanes'] if row['candidate_id'] == winner)
        proof = Path(lane['submitted_proof'])
        require(digest(proof) == lane['sha256'], 'Published winning proof hash mismatch')
        require((root / 'proofs' / (winner + '.md')).read_bytes() == proof.read_bytes(), 'Winner differs from voted proof')
        source_hashes = {str(p): digest(p) for p in [manifest_path, base / 'generation/completion.json',
                         base / 'generation/run/final_results.json', *sorted((base / 'grades').glob('*.json')),
                         *sorted((base / 'proofs' / job['problem_id']).glob('*.md'))]}
        for record in records:
            source_hashes.update(record['source_hashes'])
        receipt = {'policy': policy, 'problem_id': job['problem_id'], 'state': 'completed',
                   'source_hashes': source_hashes, 'selection_file': str(output / 'SELECTIONS.json'),
                   'selected_candidate': winner, 'selected_proof': str(output / 'selected.md'),
                   'selected_proof_sha256': digest(proof), 'recovered_cases': [r['task']['case_id'] for r in records],
                   'additional_model_calls': 0, 'additional_grading_calls': 0,
                   'native_generation_returncode': manifest['generation_completion']['returncode'],
                   'original_native_failure_preserved': True}
        exact(output / 'selected.md', proof.read_bytes())
        exact(output / 'SELECTIONS.json', encoded(selection))
        exact(output / 'receipt.json', encoded(receipt))
        live.report(output, selection)
        backup = output / 'original_reports'
        for p in (report_path, report_path.with_suffix('.md')):
            if not (backup / p.name).exists():
                exact(backup / p.name, p.read_bytes())
        selected_row = next(r for r in report['lanes'] if r['candidate_id'] == winner)
        # Verify grades instead of trusting only a possibly stale derived report.
        scores = [read(base / 'grades' / f'{winner}_pass{i}.json')['grade']['score'] for i in (1, 2)]
        require(selected_row['scores'] == scores, 'Report scores differ from saved grades')
        updated = copy.deepcopy(report)
        updated.update(selected_candidate=winner, selected_mean=sum(scores) / 2, selection_state='completed',
                       selection_recovery=str(output / 'receipt.json'),
                       comparison_summaries=selection['summaries'],
                       original_generation_status=manifest['generation_completion'])
        atomic(report_path, encoded(updated))
        old_md = (backup / 'REPORT.md').read_text()
        import re
        md = re.sub(r'selected: [^\n]*\.', f'selected: {updated["selected_mean"]} ({winner}).', old_md, count=1)
        md += ('\nSelection recovered offline from the saved response; original native failure retained. '
               'No extra model or grading calls.\n\n[Full recovered vote table and order disagreement]'
               f'(../selection_recovery/{slug}/REPORT.md) · '
               f'[Recovery provenance](../selection_recovery/{slug}/receipt.json)\n')
        atomic(report_path.with_suffix('.md'), md.encode())
        for path, expected in source_hashes.items():
            require(digest(path) == expected, 'Original evidence changed: ' + path)
        return {'state': 'recovered', 'winner': winner, 'scores': scores, 'summaries': selection['summaries'],
                'receipt': str(output / 'receipt.json')}


def run_once(config, api, wanted=None, write=False):
    results = {}
    changed = False
    for job in config['jobs']:
        if wanted and job['problem_id'] not in wanted:
            continue
        try:
            report = Path(job['output']) / 'reports/REPORT.json'
            before = digest(report) if report.exists() else None
            results[job['problem_id']] = recover_problem(config, job, api, write)
            changed |= write and before != (digest(report) if report.exists() else None)
        except Exception as error:
            results[job['problem_id']] = {'state': 'recovery_rejected', 'error': f'{type(error).__name__}: {error}'}
    if write and changed:
        controller = load_module('proofbench_report_functions', Path(config['output']) / 'controller.py')
        controller.verify_pins(config)
        backup = Path(config['output']) / 'vote_recovery/original_aggregate_reports'
        for name, out in [('all', config['output']), *config['group_outputs'].items()]:
            for suffix in ('json', 'md'):
                src = Path(out) / 'reports' / ('REPORT.' + suffix)
                dst = backup / name / src.name
                if src.exists() and not dst.exists():
                    exact(dst, src.read_bytes())
        controller.aggregate(config)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--problem-id', action='append')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    # Enforce offline operation even if an imported helper changes in the future.
    def offline(*args, **kwargs):
        raise RuntimeError('Network/model access forbidden in offline vote recovery')
    socket.socket = offline
    socket.create_connection = offline
    config = read(args.config)
    controller = load_module('proofbench_report_functions', Path(config['output']) / 'controller.py')
    controller.verify_pins(config)
    api = setup(config)
    control = Path(config['output']) / 'vote_recovery'
    if not args.watch:
        result = run_once(config, api, args.problem_id, args.write)
        print(json.dumps(result, indent=2), flush=True)
        return 1 if any(r['state'] == 'recovery_rejected' for r in result.values()) else 0
    require(args.write, '--watch requires --write')
    import fcntl
    control.mkdir(exist_ok=True)
    lock = (control / 'monitor.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    last = None
    try:
        while True:
            results = run_once(config, api, args.problem_id, True)
            state = read(Path(config['output']) / 'status.json')
            cmdline = Path(f'/proc/{state["pid"]}/cmdline')
            expected_controller = Path(state.get('controller_path') or (Path(config['output']) / 'controller.py'))
            alive = cmdline.exists() and str(expected_controller).encode() in cmdline.read_bytes()
            status = {'state': 'watching' if alive else 'completed', 'pid': os.getpid(),
                      'updated_at': datetime.now(timezone.utc).isoformat(),
                      'policy': recovery.POLICY, 'results': results,
                      'supported_policies': [recovery.POLICY, recovery.PREFIX_POLICY],
                      'additional_model_calls': 0, 'additional_grading_calls': 0}
            atomic(control / 'status.json', encoded(status))
            if results != last:
                print(json.dumps(status), flush=True)
                last = results
            if not alive:
                return 0
            time.sleep(30)
    except BaseException:
        atomic(control / 'failure.txt', traceback.format_exc().encode())
        raise


if __name__ == '__main__':
    raise SystemExit(main())
