"""Offline orchestration checks against complete synthetic 6+3+3 generation evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
try:
    SPEC = importlib.util.spec_from_file_location(
        'workshop_grade_sampled_suite', REPO / 'scripts/grade_sampled_suite.py')
    grader = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(grader)
finally:
    sys.path.pop(0)

RUN_ID = 'synthetic_suite'
GRADING_ID = 'offline_grading'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else
                     (json.dumps(value, indent=2) + '\n').encode())
    return path


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def edit(path, change):
    value = read(path)
    change(value)
    write(path, value)


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def forbidden(*args, **kwargs):
    pytest.fail('Offline suite grading attempted an external call')


@pytest.fixture
def completed_suite(tmp_path, monkeypatch):
    root = tmp_path / 'repository'
    jobs, outcomes, refs = [], [], {'imo': {}, 'dataset': {}}
    for benchmark, count in grader.GROUPS.items():
        ids = ([f'imo2026_p{i}' for i in range(1, count + 1)] if benchmark == 'imo2026'
               else [f'PB-{benchmark.rsplit("/", 1)[1].title()}-{i:03d}' for i in range(1, count + 1)])
        base = root / 'benchmarks' / benchmark
        experiment = base / 'results' / RUN_ID
        run = experiment / 'generation/run'
        inputs, finals, timings = [], [], []
        for number, pid in enumerate(ids, 1):
            claim = f'Prove the synthetic claim for {pid}: x² ≥ 0.'
            problem = write(base / 'problems' / f'{pid}.json', {'problem_id': pid, 'claim': claim})
            inputs.append({'problem_id': pid, 'path': str(problem.relative_to(base)),
                           'sha256': sha(problem.read_bytes())})
            if benchmark == 'imo2026':
                reference = write(root / 'external' / f'{pid}.txt', f'OFFICIAL_REFERENCE {pid}\n'.encode())
                refs['imo'][pid] = {'path': str(reference), 'sha256': sha(reference.read_bytes().strip())}
            else:
                refs['dataset'][pid] = {'problem': claim, 'reference': f'OFFICIAL_REFERENCE {pid}',
                                        'guidelines': f'OFFICIAL_GUIDELINES {pid}'}
            timings.append({'problem_id': pid, 'elapsed_seconds': number * 60,
                            'resumed': number == 2})
            for candidate in grader.CANDIDATES:
                fallback = pid == 'imo2026_p1' and candidate == grader.CANDIDATES[0]
                stage = 'raw' if fallback else 'refinement_3'
                data = f'\n FINAL {pid}/{candidate}/{stage}: x² ≥ 0.  \n'.encode()
                producer = write(run / 'problems' / pid / stage / candidate / 'proof.txt', data)
                receipt = write(producer.with_name('completion.json'),
                                {'state': 'completed', 'problem_id': pid, 'candidate_id': candidate,
                                 'stage': stage, 'returncode': 0})
                proof = write(run / 'proofs' / pid / f'{candidate}.md', data)
                finals.append({'problem_id': pid, 'candidate_id': candidate, 'proof_available': True,
                               'state': 'completed_with_fallback' if fallback else 'completed',
                               'selected_stage': stage, 'proof': str(proof.relative_to(run)),
                               'producer': str(producer.relative_to(run)),
                               'completion_record': str(receipt.relative_to(run)),
                               'sha256': sha(data), 'proof_sha256': sha(data.strip())})
        catalog = write(base / 'catalog.json', {'generation_inputs': {'files': inputs}})
        jobs.append({'benchmark': benchmark, 'problem_ids': ids, 'inputs': inputs,
                     'catalog_sha256': sha(catalog.read_bytes())})
        outcomes.append({'benchmark': benchmark, 'returncode': 0})
        write(experiment / 'experiment.json', {'run_id': RUN_ID, 'benchmark': benchmark, 'state': 'completed'})
        write(experiment / 'generation/completion.json', {'worker_exited': True, 'returncode': 0})
        write(run / 'final_results.json', {'state': 'completed_with_fallbacks' if benchmark == 'imo2026' else 'completed',
                                         'execution': {'state': 'completed', 'returncode': 0}, 'lanes': finals})
        write(run / 'problem_sequence.json', {'state': 'completed', 'problems': timings})
        write(run / 'pipeline_review.json', {'content': 'PRIVATE_GENERATION_REVIEW_DO_NOT_GRADE'})
    suite_dir = root / '.workshop/runs' / RUN_ID
    write(suite_dir / 'plan.json', {'schema': 'workshop-sampled-suite-v1', 'run_id': RUN_ID,
          'problem_count': 12, 'candidates_per_problem': 4, 'sample_seed': 1729,
          'generation_seed': 271828, 'seed_namespace': 'workshop-generation:271828', 'jobs': jobs})
    write(suite_dir / 'status.json', {'state': 'completed', 'outcomes': outcomes})
    dataset = write(root / 'external/dataset.csv', b'SYNTHETIC_OFFICIAL_DATASET\n')
    refs.update(dataset_path=str(dataset), dataset_sha256=sha(dataset.read_bytes()),
                b5_prompt_sha256=sha(b'SYNTHETIC_B5_PROMPT'))
    calls, indexes = [], []

    def mock_references(path, download=False):
        calls.append((path, download))
        return refs

    monkeypatch.setattr(grader, 'ROOT', root)
    monkeypatch.setattr(grader, 'references', mock_references)
    monkeypatch.setattr(grader, 'run_command', forbidden)
    monkeypatch.setattr(grader, 'refresh_index', lambda job, run_id: indexes.append((job['benchmark'], run_id)))
    monkeypatch.setattr(grader.shutil, 'which', lambda name: '/offline/codex' if name == 'codex' else None)
    monkeypatch.setattr(grader.urllib.request, 'urlopen', forbidden)
    monkeypatch.setattr(grader.subprocess, 'Popen', forbidden)
    return SimpleNamespace(root=root, refs=refs, reference_calls=calls, indexes=indexes, jobs=jobs,
                           suite_dir=suite_dir, original=snapshot(root))


def arguments(fixture, *extra):
    return ['--run-id', RUN_ID, '--grading-id', GRADING_ID,
            '--dataset', fixture.refs['dataset_path'], '--workers', '2', *extra]


def report_dir(fixture):
    return fixture.root / 'benchmarks/reports' / f'{RUN_ID}_grading' / GRADING_ID


def experiment(fixture, benchmark='imo2026'):
    return fixture.root / 'benchmarks' / benchmark / 'results' / RUN_ID


def install_fake_grader(monkeypatch, fixture, corrupt=None, after_call=None, tie=False):
    """Produce adapter-native summaries and individual isolation audits, without subprocesses."""
    calls = []

    def run(command, log_path):
        strict = '--generic-task-manifest' in command
        flag = '--generic-task-manifest' if strict else '--task-manifest'
        tasks = read(Path(command[command.index(flag) + 1]))['tasks']
        output = Path(command[command.index('--output-dir') + 1])
        number = int(output.name.rsplit('_', 1)[1])
        benchmark = ('imo2026' if strict else
                     'imo-proofbench/basic' if tasks[0]['problem_id'].startswith('PB-Basic-')
                     else 'imo-proofbench/advanced')
        assert command[command.index('--workers') + 1] == '2'
        assert command[command.index('--reasoning-effort') + 1] == 'xhigh'
        assert Path(command[3]).name == ('score_imo_v2.py' if strict else 'score_proofbench.py')
        rows = []
        for task in tasks:
            pid, cid = task['problem_id'], task['candidate_id']
            index = grader.CANDIDATES.index(cid)
            assert sha(Path(task['proof_path']).read_bytes().strip()) == task['expected_hashes']['proof_sha256']
            assert 'grading/work' in task['proof_path']
            assert 'PRIVATE_GENERATION_REVIEW' not in json.dumps(task)
            if strict:
                problem_number = int(pid.rsplit('p', 1)[1])
                assert task['problem_number'] == problem_number
                assert sha(Path(task['reference_path']).read_bytes().strip()) == task['expected_hashes']['reference_sha256']
                scores = ([0, 1, 2, 3] if problem_number == 1 else [4, 5, 6, 7]) if number == 1 or tie else (
                    [7, 7, 6, 6] if problem_number == 1 else [0, 1, 2, 3])
                row = dict(task['expected_hashes'], problem_id=pid, candidate_id=cid, state='completed',
                           grade={'score': scores[index]}, grader=grader.MODEL, reasoning_effort=grader.EFFORT,
                           policy_mode='strict', policy_sha256=grader.score_imo_v2.POLICY_SHA256)
                case = output / f'p{problem_number}' / cid
                result_name = 'summary.json'
                audit = {'tool_calls': 0, 'successful_processes_audited': True, 'completed_turns': 1}
            else:
                assert command[command.index('--model') + 1] == 'gpt-5.6-sol'
                assert command[command.index('--dataset') + 1] == fixture.refs['dataset_path']
                assert '--cache-dir' not in command
                assert not any(argument.startswith('--cache-dir=') for argument in command)
                problem_number = int(pid.rsplit('-', 1)[1])
                scores = ([0, 0, 0, 0] if problem_number == 1 else [6, 6, 7, 7]) if number == 1 or tie else (
                    [6, 6, 7, 7] if problem_number == 1 else [0, 0, 1, 1])
                score = scores[index]
                response = f'Synthetic assessment. <points>{score} out of 7</points>\n'
                row = dict(task['expected_hashes'], problem_id=pid, candidate_id=cid, state='completed',
                           grade={'score': score, 'category': {0: 'Incorrect', 1: 'Partial', 6: 'Almost', 7: 'Correct'}[score]},
                           response_sha256=sha(response.encode()), model=grader.MODEL, reasoning_effort=grader.EFFORT,
                           policy_mode='imobench-proof-autograder-b5-v1',
                           prompt_template_sha256=fixture.refs['b5_prompt_sha256'],
                           dataset_sha256=fixture.refs['dataset_sha256'])
                case = output / 'cases' / pid / cid
                result_name = 'result.json'
                audit = {'tool_calls': 0, 'completed_turns': 1}
                write(case / 'grade.md', response.encode())
            write(case / result_name, row)
            write(case / 'isolation_audit.json', audit)
            rows.append(row)
        write(output / 'summary.json', {'state': 'completed', 'rows': rows})
        write(log_path, b'Offline synthetic evaluator completed.\n')
        calls.append({'benchmark': benchmark, 'pass': number, 'tasks': tasks, 'output': output,
                      'command': list(command)})
        if corrupt:
            corrupt(calls[-1])
        if after_call:
            after_call(calls[-1])
        return 0

    monkeypatch.setattr(grader, 'run_command', run)
    return calls


def assert_no_result_directories(fixture):
    assert not (fixture.root / 'benchmarks/reports').exists()
    for benchmark in grader.GROUPS:
        for name in ('grading', 'grades', 'proofs'):
            assert not (experiment(fixture, benchmark) / name).exists()


def test_main_grades_all_48_final_lanes_twice_and_reports_proof_means(completed_suite, monkeypatch):
    fixture = completed_suite
    calls = install_fake_grader(monkeypatch, fixture)
    assert grader.main(arguments(fixture)) == 0
    summary = read(report_dir(fixture) / 'summary.json')
    assert summary['state'] == 'completed'
    assert summary['proofbench_passes'] == 2
    assert read(report_dir(fixture) / 'manifest.json')['proofbench_passes'] == 2
    assert [(c['benchmark'], c['pass'], len(c['tasks'])) for c in calls] == [
        ('imo2026', 1, 24), ('imo2026', 2, 24), ('imo-proofbench/basic', 1, 12),
        ('imo-proofbench/basic', 2, 12), ('imo-proofbench/advanced', 1, 12),
        ('imo-proofbench/advanced', 2, 12)]
    assert len({call['output'] for call in calls}) == 6
    assert sum(len(call['tasks']) for call in calls) == 96
    imo = summary['jobs'][0]
    assert imo['aggregation'] == 'mean_of_two_grades_per_proof'
    assert 'selected_pass' not in imo
    assert [p['metrics']['average_points'] for p in imo['passes']] == [29, 14]
    assert imo['metrics']['average_points'] == 21.5
    assert imo['metrics']['oracle_at_4_points'] == 29.5
    # The best lane can change across passes: average-of-oracles would be 30.
    assert sum(p['metrics']['oracle_at_4_points'] for p in imo['passes']) / 2 == 30
    first_problem = imo['metrics']['problems'][0]
    assert first_problem['average'] == 4
    assert list(first_problem['scores'].values()) == [3.5, 4, 4, 4.5]
    assert first_problem['fallback_lanes'] == 1 and first_problem['fully_refined_lanes'] == 3
    assert first_problem['elapsed_seconds'] == 60
    assert imo['metrics']['problems'][1]['resumed'] is True
    assert sum(len(j['passes'][0]['rows']) for j in summary['jobs']) == 48
    assert sum(len(p['rows']) for j in summary['jobs'] for p in j['passes']) == 96
    copied = []
    for job in summary['jobs']:
        assert [p['pass'] for p in job['passes']] == [1, 2]
        if job['benchmark'] != 'imo2026':
            assert job['aggregation'] == 'mean_of_two_grades_per_proof'
            assert 'selected_pass' not in job
            assert [p['metrics']['average_points'] for p in job['passes']] == [13, 7.5]
            assert job['metrics']['average_points'] == 10.25
            assert job['metrics']['oracle_at_4_points'] == 11.5
            assert [p['average'] for p in job['metrics']['problems']] == [3.25, 3.5, 3.5]
            first, second = [call for call in calls if call['benchmark'] == job['benchmark']]
            assert first['output'].parent == second['output'].parent
            assert (first['output'].name, second['output'].name) == ('pass_1', 'pass_2')
            assert first['tasks'] == second['tasks']
        exp = experiment(fixture, job['benchmark'])
        manifest = read(exp / 'manifest.json')['grading_runs'][GRADING_ID]
        assert manifest['grades_sha256'] == sha((exp / manifest['grades']).read_bytes())
        for evidence in manifest['grading_evidence']:
            assert sha((exp / evidence['path']).read_bytes()) == evidence['sha256']
        for row in manifest['proofs']:
            path = exp / row['path']
            assert sha(path.read_bytes()) == row['sha256']
            assert sha(path.read_bytes().strip()) == row['proof_sha256']
            copied.append(path)
        for row in [row for batch in job['passes'] for row in batch['rows']]:
            assert row['proof_sha256'] == sha((fixture.root / row['proof_path']).read_bytes().strip())
            assert row['model'] == 'gpt-5.6-sol' and row['reasoning_effort'] == 'xhigh'
            assert sha((fixture.root / row['native_result']).read_bytes()) == row['native_result_sha256']
            if job['benchmark'] != 'imo2026':
                assert sha((fixture.root / row['explanation']).read_bytes()) == row['response_sha256']
    assert len(copied) == 48
    assert fixture.indexes == [(benchmark, RUN_ID) for benchmark in grader.GROUPS]
    after = snapshot(fixture.root)
    assert all(after[path] == data for path, data in fixture.original.items())
    assert {p for p in after if '/generation/' in p} == {p for p in fixture.original if '/generation/' in p}
    report = (report_dir(fixture) / 'REPORT.md').read_text()
    assert '| imo2026 | Mean of 2 grades | 21.5/42 | 29.5/42 |' in report
    assert '| imo-proofbench/basic | Mean of 2 grades | 10.25/21 | 11.5/21 |' in report
    assert '| imo-proofbench/advanced | Mean of 2 grades | 10.25/21 | 11.5/21 |' in report
    assert 'resumed segment' in report


def test_identical_passes_retain_both_and_report_the_same_scores(completed_suite, monkeypatch):
    install_fake_grader(monkeypatch, completed_suite, tie=True)
    assert grader.main(arguments(completed_suite)) == 0
    jobs = read(report_dir(completed_suite) / 'summary.json')['jobs']
    assert all(job['aggregation'] == 'mean_of_two_grades_per_proof' for job in jobs)
    assert all(job['metrics'] == job['passes'][0]['metrics'] == job['passes'][1]['metrics'] for job in jobs)
    assert [p['metrics']['average_points'] for p in jobs[0]['passes']] == [29, 29]
    for job in jobs[1:]:
        assert [p['metrics']['average_points'] for p in job['passes']] == [13, 13]


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'changed_proof'])
def test_mean_aggregation_rejects_unmatched_proof_portfolios(mutation):
    first = [dict(problem_id='p1', candidate_id=cid, proof_file_sha256=cid,
                  proof_sha256=cid, selected_stage='refinement_3', grade={'score': index})
             for index, cid in enumerate(grader.CANDIDATES)]
    second = [dict(row) for row in first]
    if mutation == 'missing': second.pop()
    elif mutation == 'duplicate': second.append(second[0])
    else: second[0]['proof_file_sha256'] = 'different proof'
    with pytest.raises(ValueError):
        grader.mean_grade_metrics([first, second])


def test_imo_pass_override_does_not_reduce_two_proofbench_passes(completed_suite, monkeypatch):
    calls = install_fake_grader(monkeypatch, completed_suite)
    assert grader.main(arguments(completed_suite, '--imo-passes', '1')) == 0
    summary = read(report_dir(completed_suite) / 'summary.json')
    assert summary['imo_passes'] == 1 and summary['proofbench_passes'] == 2
    assert [(call['benchmark'], call['pass']) for call in calls] == [
        ('imo2026', 1), ('imo-proofbench/basic', 1), ('imo-proofbench/basic', 2),
        ('imo-proofbench/advanced', 1), ('imo-proofbench/advanced', 2)]
    assert [len(job['passes']) for job in summary['jobs']] == [1, 2, 2]
    assert summary['jobs'][0]['aggregation'] == 'single_grading_pass'
    assert summary['jobs'][0]['metrics'] == summary['jobs'][0]['passes'][0]['metrics']
    assert 'Single-pass diagnostic' in (report_dir(completed_suite) / 'REPORT.md').read_text()


def test_cli_dry_run_validates_without_outputs_cli_or_external_calls(completed_suite, monkeypatch, capsys):
    fixture = completed_suite
    monkeypatch.setattr(grader.shutil, 'which', forbidden)
    assert grader.main(arguments(fixture, '--dry-run')) == 0
    assert 'Proofs: 48; IMO passes: 2; B.5 passes: 2' in capsys.readouterr().out
    assert fixture.reference_calls == [(Path(fixture.refs['dataset_path']), False)]
    assert not fixture.indexes
    assert snapshot(fixture.root) == fixture.original
    assert_no_result_directories(fixture)


@pytest.mark.parametrize('stage', ['raw', 'lazy_checked', 'refinement_1', 'refinement_2'])
def test_completed_fallback_checkpoint_is_eligible(completed_suite, stage):
    path = experiment(completed_suite) / 'generation/run/final_results.json'
    edit(path, lambda value: value['lanes'][0].update(selected_stage=stage))
    suite = grader.inspect_suite(RUN_ID)
    selected = suite['jobs'][0]['rows'][0]
    assert selected['selected_stage'] == stage and selected['fallback_used'] is True


@pytest.mark.parametrize('problem', ['status', 'worker', 'final_execution', 'coverage', 'missing_receipt',
                                    'producer', 'proof_hash', 'catalog'])
def test_incomplete_or_inconsistent_generation_rejected_before_any_output(completed_suite, problem):
    fixture = completed_suite
    run = experiment(fixture) / 'generation/run'
    finals = run / 'final_results.json'
    first = read(finals)['lanes'][0]
    if problem == 'status':
        edit(fixture.suite_dir / 'status.json', lambda v: v.update(state='running'))
    elif problem == 'worker':
        edit(experiment(fixture) / 'generation/completion.json', lambda v: v.update(worker_exited=False))
    elif problem == 'final_execution':
        edit(finals, lambda v: v['execution'].update(state='running'))
    elif problem == 'coverage':
        edit(finals, lambda v: v['lanes'].pop())
    elif problem == 'missing_receipt':
        (run / first['completion_record']).unlink()
    elif problem == 'producer':
        (run / first['producer']).write_bytes(b'NOT THE EXPORTED PROOF')
    elif problem == 'proof_hash':
        edit(finals, lambda v: v['lanes'][0].update(proof_sha256='0' * 64))
    elif problem == 'catalog':
        (fixture.root / 'benchmarks/imo2026/catalog.json').write_bytes(b'{}')
    before = snapshot(fixture.root)
    with pytest.raises(SystemExit) as error:
        grader.main(arguments(fixture))
    assert error.value.code == 2
    assert not fixture.reference_calls
    assert snapshot(fixture.root) == before
    assert_no_result_directories(fixture)


@pytest.mark.parametrize('benchmark', ['imo2026', 'imo-proofbench/basic'])
@pytest.mark.parametrize('defect', ['missing_grade', 'missing_lane', 'invalid_score', 'boolean_score',
                                   'hash_mismatch', 'bad_isolation', 'case_mismatch'])
def test_invalid_grading_evidence_is_not_published(completed_suite, monkeypatch, benchmark, defect):
    def corrupt(call):
        if call['benchmark'] != benchmark or call['pass'] != 1:
            return
        output = call['output']
        summary = read(output / 'summary.json')
        row = summary['rows'][0]
        strict = benchmark == 'imo2026'
        case = (output / 'p1' / row['candidate_id'] if strict else
                output / 'cases' / row['problem_id'] / row['candidate_id'])
        if defect == 'missing_grade':
            row.pop('grade')
        elif defect == 'missing_lane':
            summary['rows'].pop()
        elif defect == 'invalid_score':
            row['grade']['score'] = 8 if strict else 2
        elif defect == 'boolean_score':
            row['grade']['score'] = True
        elif defect == 'hash_mismatch':
            row['proof_sha256'] = 'f' * 64
        elif defect == 'bad_isolation':
            edit(case / 'isolation_audit.json', lambda v: v.update(tool_calls=1))
        elif defect == 'case_mismatch':
            edit(case / ('summary.json' if strict else 'result.json'), lambda v: v.update(grade={'score': 7}))
        write(output / 'summary.json', summary)

    install_fake_grader(monkeypatch, completed_suite, corrupt=corrupt)
    assert grader.main(arguments(completed_suite)) == 1
    summary = read(report_dir(completed_suite) / 'summary.json')
    assert summary['state'] == 'failed'
    result = next(job for job in summary['jobs'] if job['benchmark'] == benchmark)
    assert result['state'] == 'failed' and result['errors'][0]['pass'] == 1
    expected_error = {'missing_grade': 'Missing or invalid score', 'missing_lane': 'coverage',
                      'invalid_score': 'Missing or invalid score', 'boolean_score': 'Missing or invalid score',
                      'hash_mismatch': 'Grade input hash mismatch', 'bad_isolation': 'isolation',
                      'case_mismatch': 'summary differs'}[defect]
    assert expected_error in result['errors'][0]['error']
    assert all(job['state'] == 'completed' for job in summary['jobs'] if job['benchmark'] != benchmark)
    assert completed_suite.indexes == [(name, RUN_ID) for name in grader.GROUPS if name != benchmark]
    assert 'metrics' not in result and 'selected_pass' not in result
    exp = experiment(completed_suite, benchmark)
    assert not (exp / 'grades' / GRADING_ID).exists()
    assert not (exp / 'proofs' / GRADING_ID).exists()
    assert all((completed_suite.root / path).read_bytes() == data
               for path, data in completed_suite.original.items())


def test_generation_changed_during_grading_fails_before_publication(completed_suite, monkeypatch):
    source = experiment(completed_suite) / 'generation/run/final_results.json'

    def mutate_generation(call):
        if call['benchmark'] == 'imo2026' and call['pass'] == 1:
            edit(source, lambda v: v.update(unexpected_mutation=True))

    calls = install_fake_grader(monkeypatch, completed_suite, after_call=mutate_generation)
    with pytest.raises(SystemExit) as error:
        grader.main(arguments(completed_suite))
    assert error.value.code == 2
    summary = read(report_dir(completed_suite) / 'summary.json')
    assert summary['state'] == 'failed' and 'Input hash mismatch' in summary['error']
    assert {c['benchmark'] for c in calls} == {'imo2026'}
    assert not (experiment(completed_suite) / 'grades' / GRADING_ID).exists()
    assert not (experiment(completed_suite) / 'proofs' / GRADING_ID).exists()


@pytest.mark.parametrize('update_hash', [False, True])
def test_b5_explanation_must_match_both_saved_hash_and_score(completed_suite, monkeypatch, update_hash):
    def corrupt(call):
        if call['benchmark'] != 'imo-proofbench/basic':
            return
        output = call['output']
        summary = read(output / 'summary.json')
        row = summary['rows'][0]
        case = output / 'cases' / row['problem_id'] / row['candidate_id']
        response = b'Changed assessment. <points>7 out of 7</points>\n'
        write(case / 'grade.md', response)
        if update_hash:
            row['response_sha256'] = sha(response)
            edit(case / 'result.json', lambda value: value.update(response_sha256=sha(response)))
            write(output / 'summary.json', summary)

    install_fake_grader(monkeypatch, completed_suite, corrupt=corrupt)
    assert grader.main(arguments(completed_suite)) == 1
    summary = read(report_dir(completed_suite) / 'summary.json')
    result = next(job for job in summary['jobs'] if job['benchmark'] == 'imo-proofbench/basic')
    assert result['state'] == 'failed'
    assert 'explanation differs' in result['errors'][0]['error']
    assert not (experiment(completed_suite, 'imo-proofbench/basic') / 'grades' / GRADING_ID).exists()


def test_duplicate_grading_id_refused_without_overwriting_or_new_calls(completed_suite, monkeypatch):
    calls = install_fake_grader(monkeypatch, completed_suite)
    assert grader.main(arguments(completed_suite)) == 0
    before = snapshot(completed_suite.root)
    count = len(calls)
    with pytest.raises(SystemExit) as error:
        grader.main(arguments(completed_suite))
    assert error.value.code == 2
    assert len(calls) == count and len(completed_suite.reference_calls) == 1
    assert snapshot(completed_suite.root) == before


def test_reference_statement_mismatch_stops_before_grading_or_outputs(completed_suite):
    completed_suite.refs['dataset']['PB-Basic-001']['problem'] = 'Different official statement'
    with pytest.raises(SystemExit) as error:
        grader.main(arguments(completed_suite))
    assert error.value.code == 2
    assert_no_result_directories(completed_suite)
