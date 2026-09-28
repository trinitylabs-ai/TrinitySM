#!/usr/bin/env python3
"""Publish or verify final two-pass ProofBench evidence without inference."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import csv
import json
from pathlib import Path
import re
import tempfile

POLICY = 'imobench-proof-autograder-b5-v1'
DATASET = 'aa8b813dbd4068137e3d165e5da228f6e0e1cc85a91c37883e1791b954e43af0'
PROMPT = 'e71ec3a05b6fa906e27fa7f95dabe5f950786eafa921ba526afe7596af809b4c'
ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'docs/results/proofbench_b112_final_20260926'


def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def textsha(s): return hashlib.sha256(s.strip().encode()).hexdigest()
def put(root, name, data):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = data if isinstance(data, bytes) else (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode()
    if p.exists():
        assert p.read_bytes() == raw, 'Refusing to replace different evidence: ' + str(p)
    else:
        p.write_bytes(raw)
    return str(name)


def summaries(problems):
    groups = {}
    for group in ('Basic', 'Advanced', 'Combined'):
        all_rows = [p for p in problems if group == 'Combined' or p['problem_id'].startswith('PB-' + group)]
        full = [p for p in all_rows if all(r['mean'] is not None for r in p['lanes'])]
        selected = [p for p in all_rows if p['selected_mean'] is not None]
        groups[group] = dict(reported_problems=len(all_rows), fully_graded_problems=len(full),
            planned_problems=60 if group == 'Combined' else 30,
            missing_lanes=sum(not r['available'] for p in all_rows for r in p['lanes']),
            available_lanes=sum(r['available'] for p in all_rows for r in p['lanes']),
            average_score_sum=float(sum(
                sum(Fraction(sum(r['scores']), 2) for r in p['lanes'] if r['available']) /
                sum(r['available'] for r in p['lanes']) for p in all_rows)),
            oracle_at_4_score_sum=sum(p['oracle_at_4'] for p in all_rows), score_denominator=7 * len(all_rows),
            selected_score_sum=sum(p['selected_mean'] for p in selected),
            selected_score_denominator=7 * len(selected))
    return groups


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def portable_recovery(repair):
    """Keep replayable receipts without claiming an unpublished script binding."""
    if repair and repair['policy'] == 'missing-checks-heading-existing-inline-line-citations-v2':
        return {key: value for key, value in repair.items() if key != 'repair_script_sha256'}
    return repair


def recovery_verification():
    return dict(method='replay_original_response', command='python3 -B scripts/export_proofbench_final.py --verify',
        implementation='harnesses/cross_lane_voter/mechanical_recovery.py',
        note='The unpublished Advanced-003 repair script is not hash-bound in this export. '
             'Verification replays its recorded v2 operation from the original response, '
             'checks the receipt and reproduces the normalized response bytes.')


def normalize_response(text, repair):
    validation = module('final_vote_validation', ROOT / 'harnesses/imo_proof_pipeline/releases/1.12.0/engine/source/experiments/local_math_verifier/cross_lane_voter/validation.py')
    strict = validation.strict_parse
    if not repair:
        strict(text)
        return text
    policy = repair['policy']
    recovery = module('final_format_recovery', ROOT / 'harnesses/cross_lane_voter/mechanical_recovery.py')
    normalized, applied = recovery.recover_comparison(text, strict)
    assert applied and applied['policy'] == policy
    if policy == recovery.CHECKS_POLICY:
        assert 'repair_script_sha256' not in repair, 'Unresolvable repair script hash; use replay provenance'
        assert all(repair.get(key) == value for key, value in applied.items()), 'Recovery receipt differs from replay'
    return normalized


def export_selection(report, base, native, root, cfg, recovery, api):
    live, _, binding_check = api
    pid = report['problem_id']
    plans = list((native / 'cross_lane_voter' / pid).glob('*/audit_plan.json'))
    assert len(plans) == 1 and report['selection_state'] == 'completed'
    voter_root = plans[0].parent
    receipt_path = report.get('selection_recovery')
    receipt = read(receipt_path) if receipt_path else None
    retry = bool(receipt and receipt['policy'] == 'retry-connection-refused-comparisons-preserve-valid-votes-v1')
    if receipt:
        for path, digest in receipt['source_hashes'].items():
            assert sha(path) == digest, path
        assert receipt['additional_grading_calls'] == 0
        selection = read(receipt['selection_file'])
        if retry:
            voter_root = Path(receipt['selection_file']).parent
            assert len(receipt['retried_comparisons']) == len(receipt['valid_votes_retained']) == 12
            assert selection['summaries'] == live.collect(voter_root)['summaries']
        else:
            assert receipt['additional_model_calls'] == 0
    else:
        selection = live.collect(voter_root)
    _, vm, tasks = live.verify(voter_root)
    assert selection['state'] == 'completed'
    assert selection['summaries']['combined']['winner'] == report['selected_candidate']
    votes = []
    by_id = {t['case_id']: t for t in tasks}
    put(root, Path('votes') / pid / 'AUDIT_PROMPT.md', (voter_root / 'AUDIT_PROMPT.md').read_bytes())
    put(root, Path('votes') / pid / 'problem.md', (voter_root / 'problem.md').read_bytes())
    for vote in selection['vote_table']:
        case = vote['case_id']; task = by_id[case]
        assert vote['valid'] and vote['binding_verified']
        folder = Path('votes') / pid / case
        call_path = voter_root / 'cases' / case / 'audit/call_result.json'
        if call_path.exists():
            call = read(call_path)
            binding_check(voter_root, task, read(call_path.parent.parent / 'result.json'), call)
            text = call['text']
        else:
            assert receipt and vote.get('mechanical_recovery')
            # Revalidate saved fallback transport and request binding, offline.
            with tempfile.TemporaryDirectory(prefix='final-vote-binding-') as scratch:
                checked, record = recovery.saved_vote(voter_root, task, Path(scratch), api)
            assert checked['selected_candidate'] == vote['selected_candidate']
            text = (Path(receipt_path).parent / case / 'original_response.md').read_text()
        assert hashlib.sha256(text.encode()).hexdigest() == vote['response_sha256']
        published_repair = portable_recovery(vote.get('mechanical_recovery'))
        normalized = normalize_response(text, published_repair)
        if receipt and vote.get('mechanical_recovery'):
            assert normalized == (Path(receipt_path).parent / case / 'normalized_response.md').read_text()
        response = put(root, folder / 'response.md', text.encode())
        norm = response if normalized == text else put(root, folder / 'normalized_response.md', normalized.encode())
        source_input = voter_root / 'model_inputs' / case / 'audit_input.md'
        assert sha(source_input) == task['input_sha256']
        # Gemma and Qwen see the same immutable proof pair in each order.
        model_input = put(root, Path('votes') / pid / 'inputs' / (task['original_case_id'] + '_' + task['order'] + '.md'), source_input.read_bytes())
        votes.append({k: vote[k] for k in ('case_id', 'model_key', 'order', 'presentation_order',
            'selected_candidate', 'winner_label', 'response_sha256')} | dict(response=response,
            normalized_response=norm, input=model_input, input_sha256=task['input_sha256'],
            mechanical_recovery=published_repair))
    # Independently recompute coverage, tallies, tie order, and winner.
    assert live.summarize(vm, selection['vote_table'])['summaries'] == selection['summaries']
    return dict(state='completed', votes=votes, seed_derived_candidate_order=vm['seed_derived_candidate_order'],
        seed=vm['seed'], seed_namespace=vm['seed_namespace'],
        summaries=selection['summaries'], comparison_runtime=vm['comparison_runtime'],
        recovery_policy=receipt['policy'] if receipt else None,
        original_failure_preserved=bool(receipt), retried_comparisons=12 if retry else 0,
        source_selection_sha256=sha(receipt['selection_file']) if receipt else sha(voter_root / 'SELECTIONS.json'))


def previous_comparison(problems):
    source = ROOT / 'docs/public_release/score_snapshot.json'
    historical = read(source)
    rows = {(r['problem_id'], r['candidate']): r for r in historical['lanes']}
    groups = {}
    for group in ('Basic', 'Advanced', 'Combined'):
        selected = [p for p in problems if group == 'Combined' or group in p['problem_id']]
        average = Fraction()
        oracle = missing = 0
        for p in selected:
            values = []
            for lane in p['lanes']:
                row = rows[p['problem_id'], lane['candidate_id']]
                score = row.get('baseline', {}).get('score') if row['included'] else None
                missing += score is None
                if score is not None:
                    values.append(score)
            assert values
            average += Fraction(sum(values), len(values))
            oracle += max(values)
        groups[group] = dict(problems=len(selected), average_score_sum=float(average),
            oracle_at_4_score_sum=oracle, score_denominator=7*len(selected), missing_lanes=missing)
    return dict(source='docs/public_release/score_snapshot.json', source_sha256=sha(source),
        results_as_of=historical['results_as_of'], grading='one grade per available proof',
        missing_policy='exclude missing lanes from each problem mean; equal weight per problem',
        previous_selector_available=False, groups=groups)


def selection_accuracy(problems):
    misses = []
    severe = []
    for p in problems:
        if p['selected_mean'] < p['oracle_at_4']:
            misses.append(dict(problem_id=p['problem_id'], selected_candidate=p['selected_candidate'],
                selected_mean=p['selected_mean'], best_available=p['oracle_at_4']))
        if p['selected_mean'] <= 1 and p['oracle_at_4'] >= 6:
            severe.append(p['problem_id'])
    return dict(problems=len(problems), best_or_tied=len(problems)-len(misses),
        misses=misses, selected_low_over_high=severe)


def score_table(d):
    lines = ['| Set | Problems | Graded lanes | Average | Oracle@4 | Selector@1 |',
             '|---|---:|---:|---:|---:|---:|']
    for name, g in d['groups'].items():
        cells = [f"{100*g[k]/g['score_denominator']:.2f}%"
                 for k in ('average_score_sum', 'oracle_at_4_score_sum', 'selected_score_sum')]
        lines.append(f"| {name} | {g['reported_problems']} | {g['available_lanes']}/{4*g['reported_problems']} | " + ' | '.join(cells) + ' |')
    return '\n'.join(lines)


def readme_section(d):
    lines = ['| Set | Problems | Proofs | Average | Selector@1 | Oracle@4 |',
             '|---|---:|---:|---:|---:|---:|']
    for name in ('Basic', 'Advanced', 'Combined'):
        g = d['groups'][name]
        cells = [f"{100*g[key]/g[denominator]:.2f}%" for key, denominator in (
            ('average_score_sum', 'score_denominator'),
            ('selected_score_sum', 'selected_score_denominator'),
            ('oracle_at_4_score_sum', 'score_denominator'))]
        allocated = g['available_lanes'] + g['missing_lanes']
        lines.append(f"| {name} | {g['reported_problems']} | {g['available_lanes']}/{allocated} | " + ' | '.join(cells) + ' |')
    missing = d['groups']['Combined']['missing_lanes']
    number_words = ('Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
                    'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen',
                    'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen')
    count = number_words[missing] if missing < len(number_words) else str(missing)
    subject = 'proof is missing and is' if missing == 1 else 'proofs are missing and are'
    accuracy = d['selection_accuracy']
    severe = len(accuracy['selected_low_over_high'])
    choice = 'never chose a' if not severe else 'chose a'
    qualifier = '.' if not severe else f" on {severe} problem{'s' if severe != 1 else ''}."
    lines += ['',
        f'{count} {subject} left out of the averages. The selector chose a',
        f"best-scoring proof, or one tied with it, on {accuracy['best_or_tied']} of {accuracy['problems']} problems, and {choice}",
        '0–1 proof when a 6–7 proof was available' + qualifier, '',
        '[All lane scores and selected proofs](docs/results/proofbench_b112_final_20260926/README.md) ·',
        '[SCORECARD.json](docs/results/proofbench_b112_final_20260926/SCORECARD.json) ·',
        '[lanes.csv](docs/results/proofbench_b112_final_20260926/lanes.csv)']
    return '\n'.join(lines)


def generation_timing_annotation():
    return dict(field='problems[].generation_minutes', unit='minutes',
        clock='elapsed_wall_clock', includes_gpu_pause=True,
        comparable_across_problems=False, usable_as_compute_time=False,
        note='The recorded timer continued across the GPU pause for resumed problems, '
             'and interrupted runs retain their partial elapsed time. These values are '
             'not comparable per-problem compute durations; do not average them to '
             'estimate proof-generation cost. Active GPU time is not available in this export.')


def markdown(d):
    lines = ['# Final ProofBench B 1.12.0 — 26 September 2026', '',
        f"Run: `{d['run_id']}`. Frozen release `{d['release']}` (`{d['release_sha256']}`).", '',
        'All 60 selections are complete. There are 237 available proofs and 474 independent grading judgments. Three lanes remain missing; no fresh lane retries were launched.', '',
        'Scores use IMOBench B.5 and gpt-5.6-sol/xhigh. Each available proof has two independent grades; its reported score is their mean. Average first averages the available lanes within each problem, then weights all problems equally. Missing lanes remain null and are excluded from the lane count; the three affected problems each average three proofs. Oracle@4 is the best available grade; Selector@1 is the externally graded, model-selected proof. Selection has no grade or reference access.', '',
        score_table(d), '', '## Comparison with the previous run', '',
        'Both rows of each comparison include all 60 problems and exclude missing lanes from each problem’s average. The previous snapshot has one missing lane and one grade per available proof. The current snapshot has three missing lanes and two grades per available proof. Every problem has equal weight, including those with three available lanes. These are different runs, not a controlled ablation. Previous cross-lane selected scores are unavailable.', '',
        '| Set | Previous average | Current average | Previous oracle | Current oracle | Current selected |',
        '|---|---:|---:|---:|---:|---:|']
    for name, g in d['groups'].items():
        old = d['comparison']['groups'][name]
        values = [old['average_score_sum'], g['average_score_sum'], old['oracle_at_4_score_sum'], g['oracle_at_4_score_sum'], g['selected_score_sum']]
        lines.append('| '+name+' | '+' | '.join(f'{100*v/g["score_denominator"]:.2f}%' for v in values)+' |')
    lines += ['', 'This uses the same available-lane denominator as the historical README matrix. The historical data and table are preserved.', '',
        '## Every problem and its final selection', '',
        'Each lane cell shows grade pass 1 / pass 2. Missing means no submitted proof or grade, and is excluded from each problem’s lane average. All summary columns use the mean of the two grades per available proof.', '',
        '| Problem | t07_r01 | t07_r02 | t10_r01 | t10_r02 | Average | Oracle@4 | Selected lane | Selector@1 |',
        '|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for p in sorted(d['problems'], key=lambda p: ('Advanced' in p['problem_id'], p['problem_id'])):
        rows = {r['candidate_id']: r for r in p['lanes']}
        scores = [('/'.join(map(str, rows[c]['scores'])) if rows[c]['available'] else 'missing') for c in ('t07_r01', 't07_r02', 't10_r01', 't10_r02')]
        selected = rows[p['selected_candidate']]
        lines.append('| '+p['problem_id']+' | '+' | '.join(scores)+f" | {p['average']:g} | {p['oracle_at_4']:g} | [{p['selected_candidate']}]({selected['proof']}) | {p['selected_mean']:g} |")
    lines += ['', '## Selection recovery and quality', '',
        'The selector chose a best-scoring available proof or tie on 50/60 problems. No selected 0–1 proof displaced an available 6–7 proof. Four misses selected 6.5 over 7; six misses were entirely within 0–1.', '',
        'Basic-016: `Winner: Proof A` became `Winner: A` by deleting only the literal prefix. Advanced-003: the missing Decisive checks heading was restored by copying its existing line-cited checks verbatim; no mathematical text or winner was invented. Advanced-002: only the 12 Qwen comparisons that failed with connection refused were rerun; 12 valid Gemma votes were retained. Earlier saved-response formatting recoveries are also recorded per vote.', '',
        'The [comparison recovery guide](../../comparison_format_recovery.md) documents all three saved-response format policies. The Advanced-003 receipt does not claim a hash binding to an unpublished repair script: `--verify` replays the recorded v2 operation from the original response using the same implementation as the current recovery monitor, and checks the normalized bytes and receipt. Frozen historical v1 sources remain unchanged.', '',
        'Native failures and generation return codes are preserved in the scorecard. A completed final selection can use earlier eligible proofs where refinement failed. The three missing lanes failed before producing a proof. Advanced-003’s current selection is among three available proofs.', '',
        '## Generation timing', '',
        '`generation_minutes` is recorded elapsed wall-clock time, not active GPU compute time. The timer continued across the GPU pause for resumed problems; interrupted runs retain their partial elapsed time. These values are not comparable across problems and must not be averaged to estimate proof-generation cost. The scorecard records this limitation in `generation_timing`.', '',
        '## Portable evidence and verification', '',
        '[SCORECARD.json](SCORECARD.json) records each run, checkpoint, proof hash, both grades, every comparison, model/order presentation, deterministic tie order and source record hashes. [lanes.csv](lanes.csv) contains all 240 allocated lanes. `proofs/`, `grades/` and `votes/` contain the exact proof and response evidence; original external references remain outside the solver inputs.', '',
        '```bash', 'python3 -B scripts/export_proofbench_final.py --verify', '```', '',
        'Verification uses published files and the Python standard library; it makes no model, network or grading calls.', '']
    return '\n'.join(lines)


def write_csv(root, d):
    with (root / 'lanes.csv').open('w', newline='') as f:
        fields = ['problem_id', 'candidate_id', 'available', 'pass_1', 'pass_2', 'mean', 'aggregation_score', 'selected', 'selected_stage', 'proof']
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for p in sorted(d['problems'], key=lambda p: p['problem_id']):
            for r in p['lanes']:
                writer.writerow(dict(problem_id=p['problem_id'], candidate_id=r['candidate_id'], available=r['available'],
                    pass_1=r['scores'][0], pass_2=r['scores'][1], mean=r['mean'], aggregation_score=r['mean'],
                    selected=r['candidate_id']==p['selected_candidate'], selected_stage=r['selected_stage'], proof=r.get('proof')))


def export(suite, root):
    cfg = read(suite / 'config.json')
    aggregate = read(suite / 'reports/REPORT.json')
    spec = importlib.util.spec_from_file_location('progress_vote_recovery', ROOT / 'scripts/recover_proofbench_votes.py')
    recovery = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recovery)
    api = recovery.setup(cfg)
    live = api[0]
    jobs = {j['problem_id']: j for j in cfg['jobs']}
    records = []
    for report in aggregate['problems']:
        pid = report['problem_id']; base = Path(jobs[pid]['output'])
        manifest = read(base / 'manifest.json'); native = base / 'generation/run'
        identity = read(native / 'harness_release.json')
        assert identity['release_sha256'] == cfg['release_sha256']
        lanes = []
        for row in report['lanes']:
            cid = row['candidate_id']
            lane = {k: row.get(k) for k in ('candidate_id', 'selected_stage', 'fallback_used', 'state', 'scores', 'mean')}
            lane['available'] = not row.get('missing')
            lane['grades'] = []
            if lane['available']:
                source = Path(row['submitted_proof'])
                assert sha(source) == row['sha256'] and textsha(source.read_text()) == row['proof_sha256']
                lane.update(proof=put(root, Path('proofs') / pid / (cid + '.md'), source.read_bytes()),
                            proof_sha256=row['proof_sha256'])
                for repeat in (1, 2):
                    source_grade = base / 'grades' / f'{cid}_pass{repeat}.json'
                    g = read(source_grade)
                    assert (g['problem_id'], g['candidate_id'], g['pass_index']) == (pid, cid, repeat)
                    assert g['proof_sha256'] == lane['proof_sha256'] and g['state'] == 'completed'
                    assert g['model'] == 'gpt-5.6-sol' and g['reasoning_effort'] == 'xhigh'
                    assert g['policy_mode'] == POLICY and g['dataset_sha256'] == DATASET
                    assert g['prompt_template_sha256'] == PROMPT and g['isolation_verified']
                    evidence = Path(g['result_path']).parent
                    saved = read(evidence / 'result.json')
                    assert saved['grade'] == g['grade'] and saved['response_sha256'] == g['response_sha256']
                    assert textsha((evidence / 'proof.md').read_text()) == lane['proof_sha256']
                    isolation = read(evidence / 'isolation_audit.json')
                    assert isolation['tool_calls'] == 0 and isolation['completed_turns'] == 1
                    assert sha(evidence / 'grade.md') == g['response_sha256']
                    folder = Path('grades') / pid / f'{cid}_pass{repeat}'
                    raw = put(root, folder / 'response.md', (evidence / 'grade.md').read_bytes())
                    keys = ('problem_id', 'candidate_id', 'pass_index', 'grade', 'proof_sha256', 'problem_sha256',
                        'reference_sha256', 'guidelines_sha256', 'prompt_sha256', 'prompt_template_sha256',
                        'dataset_sha256', 'model', 'reasoning_effort', 'policy_mode', 'response_sha256',
                        'cache_key', 'isolation_verified', 'isolation_config_sha256')
                    exported = {k: g[k] for k in keys}
                    exported.update(response=raw, isolation_audit=isolation, source_record_sha256=sha(source_grade))
                    lane['grades'].append(put(root, folder / 'grade.json', exported))
            lanes.append(lane)
        selection = export_selection(report, base, native, root, cfg, recovery, api)
        selected = selection['summaries']['combined']['winner']
        available_scores = [r['mean'] for r in lanes if r['available']]
        records.append(dict(problem_id=pid, run_id=report['run_id'], lanes=lanes, selection=selection,
            selected_candidate=selected, selected_mean=report['selected_mean'], average=sum(available_scores)/len(available_scores),
            oracle_at_4=max(available_scores), generation_minutes=report['generation_minutes'],
            generation_returncode=manifest['generation_completion']['returncode'],
            source_manifest_sha256=sha(base / 'manifest.json'), source_report_sha256=sha(base / 'reports/REPORT.json')))
    result = dict(schema='proofbench-b112-final-v1', run_id=cfg['run_id'], snapshot_date='2026-09-26',
        quality='final_with_missing_lanes', release=cfg['release'], release_sha256=cfg['release_sha256'],
        policy=POLICY, model='gpt-5.6-sol', reasoning_effort='xhigh', dataset_sha256=DATASET,
        prompt_template_sha256=PROMPT, aggregation='mean of two grades per available proof; mean of available lanes per problem; all 60 problems weighted equally; missing lanes excluded from lane counts',
        generation_timing=generation_timing_annotation(),
        recovery_verification=recovery_verification(),
        generation_state='completed_with_failures', selection_state='completed', lane_retries_launched=False, planned_problems=60, planned_judgments=480,
        completed_judgments=sum(len(r['grades']) for p in records for r in p['lanes']),
        problems=records, groups=summaries(records), source_aggregate_sha256=sha(suite / 'reports/REPORT.json'))
    assert result['completed_judgments'] == aggregate['completed_judgments']
    result['comparison'] = previous_comparison(records)
    result['selection_accuracy'] = selection_accuracy(records)
    assert len(records) == 60 and result['completed_judgments'] == 474
    assert result['groups']['Combined']['missing_lanes'] == 3
    assert result['selection_accuracy']['best_or_tied'] == 50
    write_csv(root, result)
    result['artifacts'] = {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
    put(root, 'SCORECARD.json', result)
    verify(root)
    put(root, 'README.md', markdown(result).encode())
    return result


def verify(root):
    d = read(root / 'SCORECARD.json')
    assert d['schema'] == 'proofbench-b112-final-v1' and d['policy'] == POLICY
    assert d.get('generation_timing') == generation_timing_annotation()
    assert d.get('recovery_verification') == recovery_verification()
    assert d['release'] == '1.12.0'
    assert sha(ROOT / 'harnesses/imo_proof_pipeline/releases/1.12.0/release.json') == d['release_sha256']
    assert d['dataset_sha256'] == DATASET and d['prompt_template_sha256'] == PROMPT
    assert len({p['problem_id'] for p in d['problems']}) == len(d['problems'])
    for name, digest in d['artifacts'].items():
        p = (root / name).resolve()
        assert p.is_relative_to(root.resolve()) and sha(p) == digest, name
    count = 0
    for p in d['problems']:
        assert len(p['lanes']) == len({r['candidate_id'] for r in p['lanes']}) == 4
        for r in p['lanes']:
            if not r['available']:
                assert r['mean'] is None and r['scores'] == [None, None] and not r['grades']; continue
            assert r['proof'] in d['artifacts'] and textsha((root / r['proof']).read_text()) == r['proof_sha256']
            assert len(r['grades']) == 2
            for repeat, path in enumerate(r['grades'], 1):
                assert path in d['artifacts']; g = read(root / path)
                assert g['response'] in d['artifacts'] and sha(root / g['response']) == g['response_sha256']
                assert (g['problem_id'], g['candidate_id'], g['pass_index']) == (p['problem_id'], r['candidate_id'], repeat)
                assert g['proof_sha256'] == r['proof_sha256'] and g['grade']['score'] == r['scores'][repeat - 1]
                assert type(g['grade']['score']) is int and g['grade']['score'] in (0, 1, 6, 7)
                assert g['policy_mode'] == POLICY and g['dataset_sha256'] == DATASET and g['prompt_template_sha256'] == PROMPT
                assert g['model'] == d['model'] and g['reasoning_effort'] == d['reasoning_effort']
                assert g['isolation_verified'] and g['isolation_audit']['tool_calls'] == 0 and g['isolation_audit']['completed_turns'] == 1
                count += 1
            assert r['mean'] == sum(r['scores']) / 2
        values = [r['mean'] for r in p['lanes'] if r['available']]
        assert p['average'] == sum(values)/len(values)
        assert p['oracle_at_4'] == max(values)
        s = p['selection']
        assert s['state'] == 'completed'
        order = s['seed_derived_candidate_order']; votes = s['votes']; actual = set(); counts = Counter({c: 0 for c in order})
        assert len(order) == len(set(order)) and set(order) == {r['candidate_id'] for r in p['lanes'] if r['available']}
        available = {r['candidate_id']: r for r in p['lanes'] if r['available']}
        assert order == sorted(available, key=lambda cid: hashlib.sha256(json.dumps([
            s['seed'], p['problem_id'], sha(root / available[cid]['proof']), cid, 'blind_order'], ensure_ascii=False).encode()).hexdigest())
        pairs = {tuple(sorted(x)) for x in itertools.combinations(order, 2)}
        for v in votes:
            key = (tuple(sorted(v['presentation_order'])), v['model_key'], v['order'])
            assert key not in actual; actual.add(key)
            for name in ('input', 'response', 'normalized_response'): assert v[name] in d['artifacts']
            assert sha(root / v['response']) == v['response_sha256'] and sha(root / v['input']) == v['input_sha256']
            problem = (root / 'votes' / p['problem_id'] / 'problem.md').read_text()
            def numbered(cid):
                text = (root / available[cid]['proof']).read_text().strip()
                return '\n'.join(f'{i}: {line}' for i, line in enumerate(text.splitlines(), 1))
            a, b = v['presentation_order']
            expected_input = '# Problem\n\n' + problem.strip() + '\n\n# Proof A\n\n' + numbered(a) + '\n\n# Proof B\n\n' + numbered(b) + '\n'
            assert (root / v['input']).read_text() == expected_input
            assert v['winner_label'] in ('A', 'B')
            original = (root / v['response']).read_text()
            normalized = (root / v['normalized_response']).read_text()
            assert normalize_response(original, v['mechanical_recovery']) == normalized
            normalized = normalized.replace('**', '').replace('`', '')
            choices = re.findall(r'^\s*(?:[-*]\s*)?Winner\s*:\s*([AB])\s*[.]?\s*$', normalized, re.M | re.I)
            assert [c.upper() for c in choices] == [v['winner_label']]
            assert v['selected_candidate'] == v['presentation_order'][0 if v['winner_label'] == 'A' else 1]
            counts[v['selected_candidate']] += 1
        assert actual == {(pair, m, o) for pair in pairs for m in ('gemma', 'qwen') for o in ('forward', 'reverse')}
        for m in ('gemma', 'qwen', 'combined'):
            vv = [v for v in votes if m == 'combined' or v['model_key'] == m]
            tally = Counter({c: 0 for c in order}); tally.update(v['selected_candidate'] for v in vv)
            flips = 0; pairs_n = 0
            for pair in pairs:
                for model in (('gemma', 'qwen') if m == 'combined' else (m,)):
                    two = [v for v in vv if v['model_key'] == model and tuple(sorted(v['presentation_order'])) == pair]
                    assert len(two) == 2 and two[0]['presentation_order'] == list(reversed(two[1]['presentation_order']))
                    flips += two[0]['selected_candidate'] != two[1]['selected_candidate']; pairs_n += 1
            summary = s['summaries'][m]
            assert summary['complete'] and summary['votes'] == dict(tally) and summary['valid_calls'] == len(vv)
            assert summary['winner'] == max(order, key=lambda c: tally[c])
            assert summary['disagreeing_pairs'] == flips and summary['completed_order_pairs'] == pairs_n
            assert summary['order_disagreement_rate'] == flips / pairs_n
        assert p['selected_candidate'] == max(order, key=lambda c: counts[c])
        assert p['selected_mean'] == next(r['mean'] for r in p['lanes'] if r['candidate_id'] == p['selected_candidate'])
    assert count == d['completed_judgments'] and summaries(d['problems']) == d['groups']
    assert len(d['problems']) == 60 and count == 474
    assert d['comparison'] == previous_comparison(d['problems'])
    assert d['selection_accuracy'] == selection_accuracy(d['problems'])
    assert d['groups']['Combined']['missing_lanes'] == 3
    return d


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-suite', type=Path)
    parser.add_argument('--output-dir', type=Path, default=BUNDLE)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        data = verify(args.output_dir)
    else:
        if args.source_suite is None:
            parser.error('--source-suite is required for export')
        assert not args.output_dir.exists(), 'Use a fresh output directory'
        data = export(args.source_suite, args.output_dir)
    print(json.dumps(dict(state='verified', problems=len(data['problems']), judgments=data['completed_judgments'], groups=data['groups']), indent=2))
