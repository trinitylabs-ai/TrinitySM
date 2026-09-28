"""Capture Qwen-only final selection for new runs; replay each run's saved policy."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time
import types

POLICY = 'qwen-only-symmetric-obligation-audit-v1'
SOURCES = {'selector.py': Path(__file__),
           'comparison_recovery.py': Path(__file__).resolve().parents[1] / 'cross_lane_voter/mechanical_recovery.py'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def binding(release):
    if release == '1.12.0':
        return dict(policy=POLICY, models=['qwen'], files={name: sha(path) for name, path in SOURCES.items()})


def prepare(root, engine):
    bound = read(root / 'harness_release.json').get('final_selector')
    if bound is None:
        return
    if bound != binding('1.12.0'):
        raise ValueError('Final selector changed during preparation')
    directory = root / 'selector_runtime'
    directory.mkdir()
    for name, path in SOURCES.items():
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != bound['files'][name]:
            raise ValueError('Final selector changed during capture: ' + name)
        with (directory / name).open('xb') as handle:
            handle.write(data)
    with (root / 'selector_policy.json').open('x') as handle:
        json.dump(dict(binding=bound, engine=str(engine.resolve())), handle, indent=2)
        handle.write('\n')


def saved(root):
    root = Path(root).resolve()
    identity = read(root / 'harness_release.json')
    bound = identity.get('final_selector')
    if bound is None:
        if (root / 'selector_policy.json').exists() or (root / 'selector_runtime').exists():
            raise ValueError('Saved final selector binding was removed')
        return None
    record = read(root / 'selector_policy.json')
    if (record['binding'] != bound or bound['policy'] != POLICY
            or bound['models'] != ['qwen'] or set(bound['files']) != set(SOURCES)):
        raise ValueError('Final selector differs from saved run identity')
    for name, expected in bound['files'].items():
        path = root / 'selector_runtime' / name
        if path.is_symlink() or sha(path) != expected:
            raise ValueError('Captured final selector code changed: ' + name)
    engine = Path(record['engine']).resolve()
    if sha(engine.parents[1] / 'release.json') != identity['release_sha256']:
        raise ValueError('Final selector engine differs from saved release')
    return record


def module(root):
    """Load the captured adapter, never substitute the current checkout's policy."""
    record = saved(root)
    if record is None:
        return None
    path = Path(root).resolve() / 'selector_runtime/selector.py'
    name = 'workshop_saved_selector_' + hashlib.sha256(str(path).encode()).hexdigest()
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        sys.modules[name] = adapter
    return sys.modules[name].load(root)


def load(root, *, worker=False):
    record = saved(root)
    if record is None or sha(__file__) != record['binding']['files']['selector.py']:
        raise ValueError('Qwen selector requires its captured run policy')
    engine = Path(record['engine']).resolve()
    release = engine.parents[1]
    manifest = read(release / 'release.json')
    prefix = 'engine/source/experiments/local_math_verifier/'
    for name, expected in manifest['files'].items():
        if any(name.startswith(prefix + part + '/') for part in ('cross_lane_voter', 'post_resolver_audit')):
            if sha(release / name) != expected:
                raise ValueError('Frozen selection dependency changed: ' + name)
    if worker:
        # Transport adapters intercept this canonical import in GPU workers.
        # Only this dedicated selector process changes its voter configuration.
        voter = importlib.import_module('experiments.local_math_verifier.cross_lane_voter.live')
        configure(voter)
        return voter
    # A private module namespace prevents changes to the historical voter or to
    # the dual-model R2/R3 audit, including collectors used in the same process.
    name = 'workshop_qwen_' + hashlib.sha256((str(engine) + json.dumps(record['binding'], sort_keys=True)).encode()).hexdigest()
    if name not in sys.modules:
        package = types.ModuleType(name)
        package.__path__ = [str(engine / 'experiments/local_math_verifier')]
        sys.modules[name] = package
        voter = importlib.import_module(name + '.cross_lane_voter.live')
        configure(voter)
        # Preserve the existing collector's literal Winner: Proof A/B recovery.
        # Its implementation is captured with the selector instead of read from
        # the current checkout when a saved run is collected later.
        spec = importlib.util.spec_from_file_location(name + '_recovery',
            Path(root) / 'selector_runtime/comparison_recovery.py')
        recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recovery)
        voter.parse = recovery.with_explicit_winner_prefix(voter.parse)
    return sys.modules[name + '.cross_lane_voter.live']


def configure(voter):
    if voter.POLICY_ID == POLICY:
        return
    voter.MODELS = {'qwen': voter.MODELS['qwen']}
    voter.MODEL_WORKERS = {'qwen': voter.MODEL_WORKERS['qwen']}
    voter.POLICY_ID = POLICY
    original_specification = voter.specification

    def specification(*args):
        contents, cfg, manifest, tasks = original_specification(*args)
        manifest['voting_models'] = ['qwen']
        manifest['comparison_runtime'].update(calls_per_model=len(tasks),
            workers_total=sum(voter.MODEL_WORKERS.values()))
        contents['manifest.json'] = voter.encoded(manifest)
        cfg['pins']['manifest.json'] = voter.digest(contents['manifest.json'])
        contents['config.json'] = voter.encoded(cfg)
        return contents, cfg, manifest, tasks

    def summarize(manifest, votes):
        ordered = manifest['seed_derived_candidate_order']
        expected = 2 * len(manifest['cases'])
        expected_ids = {f"{case['case_id']}_qwen_{order}"
                        for case in manifest['cases'] for order in ('forward', 'reverse')}
        valid = [v for v in votes if v.get('valid') and v.get('model_key') == 'qwen'
                 and v.get('case_id') in expected_ids and v.get('selected_candidate') in ordered]
        complete = (len(votes) == len(valid) == expected
                    and {v['case_id'] for v in valid} == expected_ids)
        counts = {cid: sum(v['selected_candidate'] == cid for v in valid) for cid in ordered}
        pairs = [[v for v in valid if v['original_case_id'] == case['case_id']]
                 for case in manifest['cases']]
        pairs = [p for p in pairs if len(p) == 2 and {v['order'] for v in p} == {'forward', 'reverse'}]
        disagreements = sum(p[0]['selected_candidate'] != p[1]['selected_candidate'] for p in pairs)
        summary = dict(complete=complete, valid_calls=len(valid), expected_calls=expected,
            votes=counts, winner=max(ordered, key=lambda c: counts[c]) if complete else None,
            completed_order_pairs=len(pairs), disagreeing_pairs=disagreements,
            order_disagreement_rate=disagreements / len(pairs) if pairs else None)
        return dict(policy_id=POLICY, problem_id=manifest['problem_id'], grade_access=False,
            voting_models=['qwen'], seed_derived_candidate_order=ordered,
            comparison_runtime=manifest['comparison_runtime'],
            summaries={'qwen': summary, 'combined': dict(summary)}, vote_table=votes,
            state='completed' if complete else 'incomplete')

    def report(root, selection):
        summary = selection['summaries']['qwen']
        lines = ['# Final proof selection: Qwen only', '',
                 f"Winner: {summary['winner'] or 'UNRESOLVED'}. Valid comparisons: "
                 f"{summary['valid_calls']}/{summary['expected_calls']}.", '',
                 '| Lane | Qwen votes |', '|---|---:|']
        for cid in selection['seed_derived_candidate_order']:
            lines.append(f"| {cid} | {summary['votes'][cid]} |")
        lines += ['', '| Order | Proof A | Proof B | Winner | Valid |', '|---|---|---|---|---|']
        for vote in selection['vote_table']:
            a, b = vote['presentation_order']
            lines.append(f"| {vote['order']} | {a} | {b} | {vote['selected_candidate']} | {vote['valid']} |")
        lines += ['', 'Ties follow the recorded seed-derived candidate order.',
                  'The combined summary is a compatibility alias for the Qwen tally.', '']
        for vote in selection['vote_table']:
            if vote.get('timeout_fallback'):
                lines.append(f"- {vote['case_id']}: {vote['timeout_fallback']['action']}")
        voter.write(Path(root) / 'SELECTIONS.json', selection)
        (Path(root) / 'REPORT.md').write_text('\n'.join(lines) + '\n')

    def run(root, caller):
        root = Path(root)
        _, _, tasks = voter.verify(root)
        if (root / 'status.json').exists() and voter.read(root / 'status.json').get('state') == 'completed':
            selection = voter.collect(root)
            selection['observed_runtime'] = voter.read(root / 'status.json')
            report(root, selection)
            return selection
        began, lock = time.monotonic(), threading.Lock()
        workers = voter.MODEL_WORKERS['qwen']
        status = dict(state='running', total_calls=len(tasks), completed_calls=0,
            workers_total=workers, workers_per_model={'qwen': workers},
            active_per_model={'qwen': 0}, max_concurrency_per_model={'qwen': 0}, max_concurrency_observed=0)

        def monitored(task):
            def measured_call(**kwargs):
                with lock:
                    status['active_per_model']['qwen'] += 1
                    peak = max(status['max_concurrency_observed'], status['active_per_model']['qwen'])
                    status['max_concurrency_observed'] = status['max_concurrency_per_model']['qwen'] = peak
                    voter.write(root / 'status.json', status)
                try:
                    return caller(**kwargs)
                finally:
                    with lock:
                        status['active_per_model']['qwen'] -= 1
                        voter.write(root / 'status.json', status)
            try:
                return voter.execute(root, task, measured_call)
            finally:
                with lock:
                    status['completed_calls'] += 1
                    voter.write(root / 'status.json', status)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(monitored, task) for task in tasks]
            for future in as_completed(futures):
                future.result()
        selection = voter.collect(root)
        status.update(state=selection['state'], elapsed_seconds=time.monotonic() - began,
                      valid_calls=selection['summaries']['qwen']['valid_calls'])
        selection['observed_runtime'] = status
        report(root, selection)
        voter.write(root / 'status.json', status)
        return selection

    voter.specification, voter.summarize, voter.report, voter.run = specification, summarize, report, run


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run this experiment\'s captured Qwen final selector.')
    parser.add_argument('--run-root', required=True, type=Path)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args()
    if not args.root.resolve().is_relative_to(args.run_root.resolve() / 'cross_lane_voter'):
        parser.error('Comparison directory must belong to the saved run')
    voter = load(args.run_root, worker=True)
    sys.argv = [sys.argv[0], '--root', str(args.root)]
    raise SystemExit(voter.main())
