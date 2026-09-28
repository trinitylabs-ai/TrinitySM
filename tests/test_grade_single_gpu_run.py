"""Use actual grading orchestration with synthetic single-GPU completion evidence."""
from pathlib import Path
import importlib
import shutil
import sys

import pytest
from test_grade_sampled_suite import (
    completed_suite, grader, install_fake_grader, read, write, sha, snapshot, edit,
    RUN_ID, GRADING_ID,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
import grade_single_gpu_run as adapter
from cross_lane_replay import response
from test_public_reproduction import pipeline


@pytest.fixture
def single_run(completed_suite, monkeypatch):
    fixture = completed_suite
    root = fixture.root
    monkeypatch.setattr(adapter, 'ROOT', root)
    monkeypatch.setattr(adapter, 'grading', grader)
    jobs, states, baselines = [], [], []
    release = 'a' * 64
    parameters = dict(raw_seed_offset=0, seed_namespace='v263-v290:problem-only', model_timeout_sec=600)
    for group in fixture.jobs:
        benchmark = group['benchmark']
        base = root / 'benchmarks' / benchmark
        original = base / 'results' / RUN_ID
        for pid in group['problem_ids'][:2]:
            child_id = RUN_ID + '_' + pid
            experiment = base / 'results' / child_id
            shutil.copytree(original, experiment)
            run = experiment / 'generation/run'
            final = read(run / 'final_results.json')
            final['lanes'] = [r for r in final['lanes'] if r['problem_id'] == pid]
            final.update(implementation_release='1.12.0', implementation_sha256=release)
            winner = final['lanes'][0]
            proof = write(run / 'selection/proof.md', (run / winner['proof']).read_bytes())
            final['problem_selections'] = [dict(problem_id=pid, state='completed', selected_candidate=winner['candidate_id'],
                proof='selection/proof.md', sha256=sha(proof.read_bytes()))]
            write(run / 'final_results.json', final)
            write(run / 'harness_release.json', dict(release_sha256=release, parameters=parameters))
            write(experiment / 'experiment.json', dict(run_id=child_id, benchmark=benchmark, state='completed'))
            write(experiment / 'generation/completion.json', dict(worker_exited=True, returncode=0, wall_seconds=120))
            problem_input = next(x for x in group['inputs'] if x['problem_id'] == pid)
            jobs.append(dict(problem_id=pid, benchmark=benchmark, run_id=child_id, input_sha256=problem_input['sha256'],
                command=['python', '--execute-models'], output=str(experiment), final_results=str(run / 'final_results.json')))
            states.append(dict(problem_id=pid, returncode=0, final_results=str(run / 'final_results.json')))
            baselines.append(dict(problem_id=pid, selected_candidate=winner['candidate_id'], lanes=[
                dict(candidate_id=r['candidate_id'], proof_sha256=r['proof_sha256'], selected_stage=r['selected_stage'],
                     available=True, scores=[1, 1]) for r in final['lanes']]))
    baseline = write(root / 'docs/baseline.json', dict(problems=baselines))
    study = write(root / adapter.STUDY, dict(release='1.12.0', release_sha256=release,
        winner_selection_policy=adapter.QWEN_POLICY,
        generation_parameters=parameters, baselines=[dict(path='docs/baseline.json', sha256=sha(baseline.read_bytes()))]))
    directory = root / '.workshop/single_gpu' / RUN_ID
    write(directory / 'plan.json', dict(schema='workshop-single-gpu-run-v1', run_id=RUN_ID, release='1.12.0',
          release_sha256=release, candidates_per_problem=4, problem_count=len(jobs), jobs=jobs))
    write(directory / 'status.json', dict(state='completed', jobs=states))
    fixture.single_jobs = jobs
    fixture.directory = directory
    fixture.study = study
    fixture.baseline = baseline
    fixture.original = snapshot(root)
    return fixture


def args(fixture, *extra):
    return ['--run-id', RUN_ID, '--grading-id', GRADING_ID, '--workers', '2',
            '--dataset', fixture.refs['dataset_path'], *extra]


def test_dry_run_binds_actual_jobs_without_grading_or_output(single_run):
    fixture = single_run
    assert adapter.main(args(fixture, '--dry-run')) == 0
    assert snapshot(fixture.root) == fixture.original
    suite = adapter.inspect_run(RUN_ID)
    assert len(suite['jobs']) == 6 and sum(len(j['rows']) for j in suite['jobs']) == 24
    assert all(j['matches_baseline_generation_parameters'] for j in suite['jobs'])


def test_two_pass_grading_keeps_inputs_and_indexes_each_child_run(single_run, monkeypatch):
    fixture = single_run
    calls = install_fake_grader(monkeypatch, fixture)
    before = adapter.inspect_run(RUN_ID)
    assert adapter.main(args(fixture)) == 0
    assert len(calls) == 12
    assert fixture.indexes == [(j['benchmark'], j['run_id']) for j in fixture.single_jobs]
    grader.verify_sources(before)
    destination = fixture.root / 'benchmarks/reports' / (RUN_ID + '_reproduction') / GRADING_ID
    result = read(destination / 'summary.json')
    assert result['state'] == 'completed' and len(result['comparisons']) == 6
    first = result['comparisons'][0]
    assert first['current']['oracle_at_4'] == 4.5
    assert first['current']['selector_at_1'] == 3.5  # The saved winner, not the oracle.
    assert first['baseline_selection_policy'] == adapter.QWEN_POLICY
    assert first['selection_policy'] == adapter.LEGACY_POLICY
    assert first['matches_baseline_selection_policy'] is False
    assert 'Qwen-only → Gemma+Qwen' in (destination / 'REPORT.md').read_text()
    assert len(first['lanes']) == 4 and all(len(r['scores']) == 2 for r in first['lanes'])
    with pytest.raises(SystemExit):
        adapter.main(args(fixture))  # No overwrite or accidental second grading run.
    assert len(calls) == 12


@pytest.mark.parametrize('damage', ['running', 'failed_job', 'duplicate', 'wrong_seed', 'proof', 'winner', 'selector_policy'])
def test_invalid_inputs_fail_before_reference_download_or_paid_calls(single_run, damage):
    fixture = single_run
    job = fixture.single_jobs[0]
    run = Path(job['output']) / 'generation/run'
    if damage == 'running':
        edit(fixture.directory / 'status.json', lambda d: d.update(state='running'))
    elif damage == 'failed_job':
        edit(fixture.directory / 'status.json', lambda d: d['jobs'][0].update(returncode=1))
    elif damage == 'duplicate':
        edit(fixture.directory / 'plan.json', lambda d: d['jobs'].__setitem__(1, d['jobs'][0]))
    elif damage == 'wrong_seed':
        edit(run / 'harness_release.json', lambda d: d['parameters'].update(raw_seed_offset=123))
    elif damage == 'proof':
        final = read(run / 'final_results.json')
        (run / final['lanes'][0]['proof']).write_text('tampered')
    elif damage == 'selector_policy':
        edit(run / 'final_results.json', lambda d: d.update(winner_selection_policy=adapter.QWEN_POLICY))
    else:
        edit(run / 'final_results.json', lambda d: d['problem_selections'][0].update(selected_candidate=grader.CANDIDATES[1]))
    with pytest.raises(SystemExit):
        adapter.main(args(fixture, '--download-references'))
    assert not fixture.reference_calls


def test_qwen_run_and_baseline_report_matching_policies(single_run, monkeypatch):
    fixture = single_run
    for job in fixture.single_jobs:
        run = Path(job['output']) / 'generation/run'
        edit(run / 'harness_release.json', lambda d: d.update(final_selector=pipeline.selector_policy.binding('1.12.0')))
        edit(run / 'final_results.json', lambda d: d.update(winner_selection_policy=adapter.QWEN_POLICY))
    install_fake_grader(monkeypatch, fixture)
    assert adapter.main(args(fixture)) == 0
    destination = fixture.root / 'benchmarks/reports' / (RUN_ID + '_reproduction') / GRADING_ID
    summary = read(destination / 'summary.json')
    assert summary['baseline_selection_policy'] == adapter.QWEN_POLICY
    assert all(p['matches_baseline_selection_policy'] for p in summary['comparisons'])
    assert 'Qwen-only → Qwen-only' in (destination / 'REPORT.md').read_text()


def test_published_qwen_baseline_compares_identical_evidence_without_selection_gain():
    study = read(REPO / adapter.STUDY)
    assert study['winner_selection_policy'] == adapter.QWEN_POLICY
    assert len(study['baselines']) == 1
    record = study['baselines'][0]
    source = REPO / record['path']
    assert sha(source.read_bytes()) == record['sha256']
    document = read(source)
    assert document['schema'] == 'qwen-saved-vote-selection-v1'
    assert len(document['problems']) == 66
    for problem in document['problems']:
        lanes = [lane for lane in problem['lanes'] if lane['available']]
        job = dict(problem_id=problem['problem_id'], benchmark=problem['group'], baseline=problem,
            baseline_selection_policy=study['winner_selection_policy'], selection_policy=adapter.QWEN_POLICY,
            selected_candidate=problem['selected_candidate'], generation_parameters=study['generation_parameters'],
            original_returncode=0, selection_recovery=None, matches_baseline_generation_parameters=True,
            rows=[dict(lane, fallback_used=lane['selected_stage'] != 'refinement_3', elapsed_seconds=0)
                  for lane in lanes])
        grades = dict(passes=[dict(rows=[dict(candidate_id=lane['candidate_id'],
                                             grade=dict(score=lane['scores'][i])) for lane in lanes])
                              for i in range(2)])
        result = adapter.compare(job, grades)
        assert result['previous'] == result['current']
        assert set(result['delta'].values()) == {0}
        assert all(lane['same_proof_text'] and lane['delta'] == 0 for lane in result['lanes'])
        assert result['matches_baseline_selection_policy'] is True
        if problem['problem_id'] == 'PB-Basic-013':
            assert result['previous']['selector_at_1'] == result['current']['selector_at_1'] == 7
            assert result['previous_selected_candidate'] == result['selected_candidate'] == 't07_r01'


def test_arbitrary_subset_and_explicit_seed_are_reported_honestly(single_run):
    fixture = single_run
    plan = read(fixture.directory / 'plan.json')
    plan['jobs'] = plan['jobs'][:1]
    plan.update(problem_count=1, generation_seed=19)
    plan['jobs'][0]['command'] += ['--raw-seed-offset', '19', '--seed-namespace', 'workshop-generation:19']
    write(fixture.directory / 'plan.json', plan)
    edit(fixture.directory / 'status.json', lambda d: d.update(jobs=d['jobs'][:1]))
    edit(Path(plan['jobs'][0]['output']) / 'generation/run/harness_release.json',
         lambda d: d['parameters'].update(raw_seed_offset=19, seed_namespace='workshop-generation:19'))
    suite = adapter.inspect_run(RUN_ID)
    assert len(suite['jobs']) == 1 and suite['generation_seed'] == 19
    assert not suite['jobs'][0]['matches_baseline_generation_parameters']


def test_missing_baseline_lane_is_not_filled_with_zero(single_run, monkeypatch):
    fixture = single_run
    edit(fixture.baseline, lambda d: d['problems'][0]['lanes'][1].update(available=False, scores=None))
    edit(fixture.study, lambda d: d['baselines'][0].update(sha256=sha(fixture.baseline.read_bytes())))
    install_fake_grader(monkeypatch, fixture)
    assert adapter.main(args(fixture)) == 0
    result = read(fixture.root / 'benchmarks/reports' / (RUN_ID + '_reproduction') / GRADING_ID / 'summary.json')
    first = result['comparisons'][0]
    assert first['previous_available_lanes'] == 3 and first['previous']['average'] == 1
    missing = next(r for r in first['lanes'] if r['previous_scores'] is None)
    assert missing['previous_mean'] is None and missing['delta'] is None


@pytest.fixture
def recovered_run(single_run, monkeypatch):
    """Actual frozen voter artifacts: 23/24 before, 24/24 after offline parsing."""
    fixture = single_run
    job = fixture.single_jobs[0]
    pid, experiment = job['problem_id'], Path(job['output'])
    run = experiment / 'generation/run'
    final = read(run / 'final_results.json')
    runtime = read(run / 'harness_release.json')
    runtime['parameters'].update(gemma_endpoint='http://127.0.0.1:8030/v1', qwen_endpoint='http://127.0.0.1:8027/v1')
    write(run / 'harness_release.json', runtime)
    claim = read(fixture.root / 'benchmarks/imo2026/problems' / (pid + '.json'))['claim']
    candidates = [dict(candidate_id=x['candidate_id'], selected_stage=x['selected_stage'],
                       proof_path=str(run / x['producer']), proof_sha256=x['proof_sha256']) for x in final['lanes']]
    voter = pipeline.voter_module('1.12.0')
    directory = run / 'cross_lane_voter' / pid / 'saved-portfolio'
    _, _, tasks = voter.prepare(directory, pid, claim, candidates, runtime['parameters'], runtime['release_sha256'])
    frozen = importlib.import_module(voter.__package__ + '.validation').parse
    calls = []
    def caller(**kw):
        calls.append(kw)
        return response(kw, 'Proof A' if 'pair_06_gemma_reverse' in str(kw['output_dir']) else 'A')
    with monkeypatch.context() as child:
        child.setattr(voter, 'parse', frozen)
        for task in tasks:
            voter.execute(directory, task, caller)
        old = voter.collect(directory)
    old['artifact_directory'] = str(directory.relative_to(run))
    assert old['summaries']['combined']['valid_calls'] == 23
    fresh = voter.collect(directory)
    winner = fresh['summaries']['combined']['winner']
    selected_lane = next(x for x in final['lanes'] if x['candidate_id'] == winner)
    selected = write(directory / 'selected_proof.md', (run / selected_lane['proof']).read_bytes())
    fresh.update(artifact_directory=old['artifact_directory'], selected_candidate=winner,
                 selected_stage=selected_lane['selected_stage'], proof=str(selected.relative_to(run)), sha256=sha(selected.read_bytes()))
    old_lanes = [dict(candidate_id=x['candidate_id'], proof_available=True, selected_stage=x['selected_stage'],
                      proof_sha256=x['proof_sha256'], proof_path=str(run / x['producer']),
                      completion_record=str(run / x['completion_record'])) for x in final['lanes']]
    write(run / 'problem_sequence.json', dict(inference_finished=True, state='failed', returncode=1,
          problems=[dict(problem_id=pid, state='missing_proofs', worker_returncode=0, lanes=old_lanes, cross_lane_voter=old)]))
    final.update(state='completed_with_failures', execution=dict(state='failed', returncode=1), problem_selections=[fresh])
    for lane in final['lanes']:
        if lane['selected_stage'] != 'refinement_3':
            lane['state'] = 'failed'
    write(run / 'final_results.json', final)
    write(run / 'pipeline_execution.json', final['execution'])
    edit(experiment / 'experiment.json', lambda d: d.update(state='failed_or_interrupted'))
    edit(experiment / 'generation/completion.json', lambda d: d.update(returncode=1))
    status = read(fixture.directory / 'status.json')
    status.update(state='completed_with_failures')
    status['jobs'][0]['returncode'] = 1
    write(fixture.directory / 'status.json', status)
    assert len(calls) == 24
    monkeypatch.setattr(voter, 'execute', lambda *a, **kw: pytest.fail('Recovery made an inference call'))
    monkeypatch.setattr(voter, 'prepare', lambda *a, **kw: pytest.fail('Recovery rewrote its inputs'))
    fixture.recovered_root, fixture.voter_root = run, directory
    fixture.original = snapshot(fixture.root)
    return fixture


def test_recovered_selection_requires_opt_in_and_dry_run_changes_nothing(recovered_run):
    fixture = recovered_run
    with pytest.raises(SystemExit):
        adapter.main(args(fixture, '--dry-run'))
    assert not fixture.reference_calls
    assert adapter.main(args(fixture, '--allow-recovered-selection', '--dry-run')) == 0
    assert snapshot(fixture.root) == fixture.original
    suite = adapter.inspect_run(RUN_ID, True)
    recovery = suite['jobs'][0]['selection_recovery']
    assert suite['original_generation_state'] == 'completed_with_failures'
    assert recovery['original_returncode'] == 1 and recovery['model_calls'] == 0
    assert recovery['cases'][0]['case_id'] == 'pair_06_gemma_reverse'
    assert recovery['original_combined']['valid_calls'] == 23
    assert recovery['recovered_combined']['valid_calls'] == 24
    assert all(j['selection_recovery'] is None for j in suite['jobs'][1:])
    # Every original response/binding remains pinned during asynchronous grading.
    raw = fixture.voter_root / 'cases/pair_06_gemma_reverse/audit/final.md'
    raw.write_text(raw.read_text() + 'tampered')
    with pytest.raises(ValueError, match='Input hash mismatch'):
        grader.verify_sources(suite)


def test_recovered_grading_retains_failures_and_uses_two_new_passes(recovered_run, monkeypatch):
    fixture = recovered_run
    calls = install_fake_grader(monkeypatch, fixture)
    assert adapter.main(args(fixture, '--allow-recovered-selection')) == 0
    assert len(calls) == 12  # Two passes for each of six problems, four proofs each.
    after = snapshot(fixture.root)
    assert all(after[path] == data for path, data in fixture.original.items())
    destination = fixture.root / 'benchmarks/reports' / (RUN_ID + '_reproduction') / GRADING_ID
    summary = read(destination / 'summary.json')
    assert summary['state'] == 'completed' and len(summary['comparisons']) == 6
    assert summary['original_generation_state'] == 'completed_with_failures'
    assert summary['comparisons'][0]['original_returncode'] == 1
    assert summary['selection_recoveries'][0]['problem_id'] == 'imo2026_p1'
    assert 'original exit 1 retained' in (destination / 'REPORT.md').read_text()
    assert 'not a clean end-to-end generation pass' in (destination / 'REPORT.md').read_text()


def test_finished_worker_with_eligible_fallback_retains_its_error(recovered_run):
    # The normal pipeline also accepts completed earlier-stage proofs after a
    # refinement fails. A recovered selector must preserve that same policy.
    fixture = recovered_run
    edit(fixture.recovered_root / 'problem_sequence.json',
         lambda d: d['problems'][0].update(worker_returncode=1, worker_error='Worker exited; preserving completed lanes'))
    suite = adapter.inspect_run(RUN_ID, True)
    recovery = suite['jobs'][0]['selection_recovery']
    assert recovery['original_worker_returncode'] == 1
    assert recovery['original_worker_error'] == 'Worker exited; preserving completed lanes'
    assert any(r['fallback_used'] for r in suite['jobs'][0]['rows'])


@pytest.mark.parametrize('damage', [
    'running', 'interrupted', 'another_failed_job', 'missing_proof', 'worker_interrupted',
    'unfinished_inference', 'changed_stage', 'changed_producer', 'response', 'transport',
    'prompt', 'tally', 'old_tally', 'old_valid_vote', 'old_error', 'missing_receipt',
])
def test_recovery_never_bypasses_unrelated_failures_or_bindings(recovered_run, damage):
    fixture = recovered_run
    run, voter = fixture.recovered_root, fixture.voter_root
    if damage in ('running', 'interrupted'):
        edit(fixture.directory / 'status.json', lambda d: d.update(state=damage))
    elif damage == 'another_failed_job':
        edit(fixture.directory / 'status.json', lambda d: d['jobs'][1].update(returncode=1))
    elif damage == 'missing_proof':
        edit(run / 'final_results.json', lambda d: d['lanes'][0].update(proof_available=False))
    elif damage == 'worker_interrupted':
        edit(run / 'problem_sequence.json', lambda d: d['problems'][0].update(worker_returncode=143))
    elif damage == 'unfinished_inference':
        edit(run / 'problem_sequence.json', lambda d: d.update(inference_finished=False))
    elif damage in ('changed_stage', 'changed_producer'):
        key, value = ('selected_stage', 'lazy_checked') if damage == 'changed_stage' else ('proof_path', str(run / 'different.md'))
        edit(run / 'problem_sequence.json', lambda d: d['problems'][0]['lanes'][0].update({key: value}))
    elif damage in ('response', 'transport'):
        def corrupt(d):
            if damage == 'response':
                d['text'] = d['text'].replace('Winner: Proof A', 'Winner: Proof B')
            else:
                d['metadata']['model'] = 'another-model'
        edit(voter / 'cases/pair_06_gemma_reverse/audit/call_result.json', corrupt)
    elif damage == 'prompt':
        (voter / 'AUDIT_PROMPT.md').write_text('different prompt')
    elif damage == 'tally':
        edit(run / 'final_results.json', lambda d: d['problem_selections'][0]['summaries']['combined'].update(valid_calls=23))
    elif damage == 'old_tally':
        edit(run / 'problem_sequence.json', lambda d: d['problems'][0]['cross_lane_voter']['summaries']['combined'].update(valid_calls=24))
    elif damage in ('old_valid_vote', 'old_error'):
        def corrupt_old(d):
            votes = d['problems'][0]['cross_lane_voter']['vote_table']
            if damage == 'old_valid_vote':
                next(v for v in votes if v['valid'])['response_sha256'] = 'f' * 64
            else:
                next(v for v in votes if not v['valid'])['error'] = 'ConnectionError: request failed'
        edit(run / 'problem_sequence.json', corrupt_old)
    else:
        (voter / 'cases/pair_06_gemma_reverse/result.json').unlink()
    before = snapshot(fixture.root)
    with pytest.raises(SystemExit):
        adapter.main(args(fixture, '--allow-recovered-selection', '--download-references'))
    assert not fixture.reference_calls
    assert snapshot(fixture.root) == before
