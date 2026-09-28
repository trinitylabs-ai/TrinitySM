"""Portable paired-study evidence from synthetic completed runs, without model calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
try:
    SPEC = importlib.util.spec_from_file_location(
        'workshop_archive_suite', REPO / 'scripts/archive_sampled_suite.py')
    archive = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(archive)
finally:
    sys.path.pop(0)

RUN_ID = 'synthetic_suite'
SEED = 271828
NAMESPACE = f'workshop-generation:{SEED}'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else
                     (json.dumps(value, indent=2) + '\n').encode())
    return path


def edit(path, mutate):
    value = json.loads(path.read_text())
    mutate(value)
    write(path, value)


@pytest.fixture
def completed_suite(tmp_path, monkeypatch):
    root = tmp_path / 'source'
    jobs, outcomes = [], []
    for benchmark, count in archive.GROUPS.items():
        ids = [f'p{i}' for i in range(1, count + 1)]
        experiment = root / 'benchmarks' / benchmark / 'results' / RUN_ID
        run = experiment / 'generation/run'
        jobs.append({'benchmark': benchmark, 'problem_ids': ids,
                     'console_log': str(experiment / 'generation/console.log')})
        outcomes.append({'benchmark': benchmark, 'returncode': 0})
        write(experiment / 'experiment.json', {'run_id': RUN_ID, 'benchmark': benchmark,
                                               'state': 'completed'})
        write(experiment / 'generation/completion.json', {'worker_exited': True, 'returncode': 0})
        settings = {'seed_namespace': NAMESPACE, 'raw_seed_offset': SEED}
        write(run / 'manifest.json', dict(settings, problems=[{'problem_id': p} for p in ids]))
        write(run / 'harness_release.json', {'parameters': settings})
        finals = []
        for pid in ids:
            baseline = run / 'problems' / pid / '02_r1_cycles'
            problem = write(baseline / 'input/problem.json', {'claim': f'Prove synthetic claim {pid}.'})
            lanes = []
            for candidate in sorted(archive.CANDIDATES):
                initial_bytes = f'\n Initial proof {pid}/{candidate}: x² ≥ 0.  \n'.encode()
                final_bytes = f'\n Final proof {pid}/{candidate}: therefore x² ≥ 0. \n'.encode()
                source = write(run / 'problems' / pid / '01_raw_lazy' / f'{candidate}.txt', initial_bytes)
                initial = write(baseline / 'input' / f'{candidate}.txt', initial_bytes)
                producer = write(baseline / 'c3' / candidate / 'proof.txt', final_bytes)
                final = write(run / 'proofs' / f'{pid}_{candidate}.txt', final_bytes)
                completion = write(baseline / 'c3' / candidate / 'completion.json', {'state': 'completed'})
                lanes.append({'candidate_id': candidate, 'proof_path': str(initial),
                              'proof_sha256': sha(initial_bytes.strip()), 'source_proof_path': str(source),
                              'source_proof_sha256': sha(initial_bytes.strip()), 'source_checkpoint': 'expanded'})
                finals.append({'problem_id': pid, 'candidate_id': candidate,
                               'proof_available': True, 'state': 'completed', 'selected_stage': 'refinement_3',
                               'proof': final.relative_to(run).as_posix(),
                               'producer': producer.relative_to(run).as_posix(),
                               'completion_record': completion.relative_to(run).as_posix(),
                               'sha256': sha(final_bytes), 'proof_sha256': sha(final_bytes.strip())})
            write(baseline / 'manifest.json', {'problem_id': pid, 'candidate_ids': sorted(archive.CANDIDATES),
                  'input_checkpoint': 'lazy_checked', 'runtime': {'seed_namespace': f'{NAMESPACE}:{pid}:r1'},
                  'frozen_inputs': {'problem_path': str(problem), 'problem_file_sha256': sha(problem.read_bytes()),
                                    'problem_text_sha256': sha(f'Prove synthetic claim {pid}.'.encode()), 'lanes': lanes}})
        write(run / 'final_results.json', {'state': 'completed', 'execution': {'state': 'completed', 'returncode': 0},
                                         'lanes': finals})
        trace = {'system_prompt': 'Check every inequality.\nPreserve the statement.',
                 'user_prompt': 'Review x² ≥ 0 without assuming x > 0.',
                 'response': {'content': 'The argument is incomplete.\nHandle x = 0.',
                              'reasoning_content': 'Consider the equality case.'},
                 'reviewer': 'qwen', 'decision': 'repair', 'usage': {'total_tokens': 317},
                 'elapsed_s': 1.25, 'source_path': str(run / 'problems/p1/02_r1_cycles/input/t10_r01.txt')}
        write(run / 'review.json', trace)
        write(run / 'request.jsonl', (json.dumps(trace) + '\n').encode())
        write(run / 'repair_brief.txt', b'Treat the equality case explicitly.\n')
        write(run / 'stage_result.json', {
            'stage': 'refinement_3', 'result': {'proof_path': str(run / 'proofs/p1_t10_r01.txt')},
            'model_response': {'analysis': 'Keep the equality case.', 'final': 'The proof follows.'}})
        model = root / '.models/gemma'
        environment = ('# Environment\n\n'
                       f'Model: `{model}`\n'
                       f'Speculative config: {{"model": "{model}-assistant", "num_speculative_tokens": 4}}\n')
        write(experiment / 'ENVIRONMENT.md', environment.encode())
        for launcher in ('launch.sh', 'launch_gemma.sh', 'launch_qwen.sh'):
            write(experiment / launcher, f'#!/bin/sh\nexec "{root}/.venv-serving/bin/vllm" serve "{model}"\n'.encode())
        for name in ('worker.log', 'engine.events.jsonl', 'runtime_logs/requests.json',
                     'worker.pid', 'engine.lock', 'weights.safetensors', 'grading/reference.txt', '.env'):
            write(experiment / name, b'not evidence\n')
    suite = root / '.workshop/runs' / RUN_ID
    write(suite / 'plan.json', {'schema': 'workshop-sampled-suite-v1', 'run_id': RUN_ID,
          'problem_count': 12, 'candidates_per_problem': 4, 'sample_seed': 1729,
          'generation_seed': SEED, 'seed_namespace': NAMESPACE, 'raw_seed_offset': SEED, 'jobs': jobs})
    write(suite / 'status.json', {'state': 'completed', 'outcomes': outcomes})
    monkeypatch.setattr(archive, 'ROOT', root)
    monkeypatch.setattr(archive.audit, 'external_reference_identities', lambda: (set(), set(), set()))
    return root


def first_run(root):
    return root / 'benchmarks/imo2026/results' / RUN_ID / 'generation/run'


def fallback_problem(run, stage, *, remove_baseline=False):
    """Model a finished problem whose four submissions use an earlier checkpoint."""
    receipt = json.loads((run / 'final_results.json').read_text())
    receipt['state'] = 'completed_with_fallbacks'
    for row in receipt['lanes']:
        if row['problem_id'] != 'p1':
            continue
        candidate = row['candidate_id']
        data = f'\nSaved {stage} proof for {candidate}: x² ≥ 0.  \n'.encode()
        producer = write(run / 'problems/p1/saved_checkpoints' / stage / f'{candidate}.md', data)
        completion = write(producer.with_suffix('.json'), {'state': 'completed', 'stage': stage})
        write(run / row['proof'], data)
        row.update(state='completed_with_fallback', selected_stage=stage,
                   producer=producer.relative_to(run).as_posix(),
                   completion_record=completion.relative_to(run).as_posix(),
                   sha256=sha(data), proof_sha256=sha(data.strip()),
                   fallback={'reason': 'Synthetic later-stage request failure'})
    write(run / 'final_results.json', receipt)
    if remove_baseline:
        shutil.rmtree(run / 'problems/p1/02_r1_cycles')


def test_nested_native_metadata_paths_are_normalized_without_touching_model_text(completed_suite):
    path = str(completed_suite / 'model-or-artifact')
    value = {'problem': {'problem_path': path, 'claim': 'Preserve this claim.'},
             'reviewer_1': {'result_path': path, 'final': 'Preserve this review.'},
             'stage_dirs': {'t10_r01': path}, 'reasoning_paths': [path],
             'prefix': path, 'python': path, 'source_fusion_result': path}
    public = archive.redact_json(value)
    logical = '${SOURCE_REPO}/model-or-artifact'
    assert public['problem'] == {'problem_path': logical, 'claim': 'Preserve this claim.'}
    assert public['reviewer_1'] == {'result_path': logical, 'final': 'Preserve this review.'}
    assert public['stage_dirs'] == {'t10_r01': logical}
    assert public['reasoning_paths'] == [logical]
    assert all(public[key] == logical for key in ('prefix', 'python', 'source_fusion_result'))


def test_archive_retains_all_semantic_evidence_and_portable_pair_bindings(completed_suite, tmp_path):
    source = first_run(completed_suite)
    original_review = json.loads((source / 'review.json').read_text())
    destination = archive.archive(RUN_ID)
    manifest = archive.verify(destination)
    assert len(manifest['paired_inputs']) == 48
    assert manifest['generation_seed'] == SEED
    assert manifest['sample_seed'] == 1729
    assert manifest['external_grading'] is False
    records = {r['path']: r for r in manifest['files']}
    review_name = 'artifacts/imo2026/generation/run/review.json'
    review = json.loads((destination / review_name).read_text())
    assert {k: v for k, v in review.items() if k != 'source_path'} == {
        k: v for k, v in original_review.items() if k != 'source_path'}
    assert review['source_path'].startswith('${SOURCE_REPO}/')
    assert records[review_name]['source_sha256'] == sha((source / 'review.json').read_bytes())
    assert records[review_name]['archived_sha256'] == sha((destination / review_name).read_bytes())
    assert records[review_name]['source_sha256'] != records[review_name]['archived_sha256']
    assert records[review_name]['transformation'] == 'machine_metadata_normalized'
    request = json.loads((destination / 'artifacts/imo2026/generation/run/request.jsonl').read_text())
    assert request == review
    assert (destination / 'artifacts/imo2026/generation/run/repair_brief.txt').read_bytes() == b'Treat the equality case explicitly.\n'
    result = json.loads((destination / 'artifacts/imo2026/generation/run/stage_result.json').read_text())
    assert result['stage'] == 'refinement_3'
    assert result['result']['proof_path'].startswith('${SOURCE_REPO}/')
    assert result['model_response'] == {'analysis': 'Keep the equality case.', 'final': 'The proof follows.'}
    for name in ('ENVIRONMENT.md', 'launch.sh', 'launch_gemma.sh', 'launch_qwen.sh'):
        archived_name = f'artifacts/imo2026/{name}'
        source_bytes = (source.parent.parent / name).read_bytes()
        expected = source_bytes.replace(str(completed_suite).encode(), b'${SOURCE_REPO}')
        assert (destination / archived_name).read_bytes() == expected
        assert records[archived_name]['source_sha256'] == sha(source_bytes)
        assert records[archived_name]['archived_sha256'] == sha(expected)
        assert records[archived_name]['transformation'] == 'machine_metadata_normalized'
    for row in manifest['paired_inputs']:
        for prefix in ('input', 'final'):
            name = row[prefix + '_proof']
            record = records[name]
            original = completed_suite / record['source_path']
            assert (destination / name).read_bytes() == original.read_bytes()
            assert record['source_sha256'] == record['archived_sha256'] == row[prefix + '_sha256']
            assert sha(original.read_bytes().strip()) == row[prefix + '_proof_sha256']
            assert record['transformation'] == 'unchanged'
    omitted = {Path(r['source_path']).name for r in manifest['excluded']}
    assert {'worker.log', 'engine.events.jsonl', 'requests.json', 'worker.pid', 'engine.lock',
            'weights.safetensors', 'reference.txt', '.env'} <= omitted
    moved = tmp_path / 'published_elsewhere'
    shutil.move(str(destination), moved)
    shutil.rmtree(completed_suite)
    assert archive.verify(moved)['paired_inputs'] == manifest['paired_inputs']


def test_dry_run_writes_nothing_and_existing_archive_is_not_overwritten(completed_suite):
    before = {p.relative_to(completed_suite) for p in completed_suite.rglob('*')}
    destination = archive.archive(RUN_ID, dry_run=True)
    assert not destination.exists()
    assert before == {p.relative_to(completed_suite) for p in completed_suite.rglob('*')}
    archive.archive(RUN_ID)
    with pytest.raises(ValueError, match='already exists'):
        archive.archive(RUN_ID)


@pytest.mark.parametrize('stage', ['refinement_2', 'refinement_1', 'lazy_checked', 'raw'])
def test_completed_fallback_submissions_keep_existing_pair_bindings(completed_suite, stage):
    fallback_problem(first_run(completed_suite), stage)
    destination = archive.archive(RUN_ID)
    manifest = archive.verify(destination)
    assert len(manifest['paired_inputs']) == 48 and manifest['unpaired_finals'] == []
    assert manifest['submitted_proofs'] == 48 and manifest['fully_refined_proofs'] == 44
    selected = [row for row in manifest['paired_inputs']
                if row['benchmark'] == 'imo2026' and row['problem_id'] == 'p1']
    assert len(selected) == 4
    assert all(row['selected_stage'] == stage and row['final_state'] == 'completed_with_fallback'
               for row in selected)
    for row in selected:
        data = (destination / row['final_proof']).read_bytes()
        assert data == (first_run(completed_suite) / 'proofs' / f"p1_{row['candidate_id']}.txt").read_bytes()
        assert sha(data) == row['final_sha256']
    assert '4 use an earlier completed stage' in (destination / 'README.md').read_text()


@pytest.mark.parametrize('stage', ['lazy_checked', 'raw'])
def test_early_submissions_without_a_baseline_are_archived_as_unpaired(completed_suite, tmp_path, stage):
    run = first_run(completed_suite)
    fallback_problem(run, stage, remove_baseline=True)
    destination = archive.archive(RUN_ID)
    manifest = archive.verify(destination)
    assert len(manifest['paired_inputs']) == 44 and len(manifest['unpaired_finals']) == 4
    assert manifest['submitted_proofs'] == 48 and manifest['fully_refined_proofs'] == 44
    for row in manifest['unpaired_finals']:
        assert row['reason'] == 'pre_qwen_manifest_unavailable'
        assert row['selected_stage'] == stage and 'input_proof' not in row
        assert (destination / row['final_proof']).read_bytes() == (
            run / 'proofs' / f"p1_{row['candidate_id']}.txt").read_bytes()
    assert 'binds 44 exact pre-Qwen inputs' in (destination / 'README.md').read_text()
    moved = tmp_path / 'portable_fallbacks'
    shutil.move(str(destination), moved)
    shutil.rmtree(completed_suite)
    assert archive.verify(moved)['unpaired_finals'] == manifest['unpaired_finals']
    edit(moved / 'archive_manifest.json',
         lambda d: d['unpaired_finals'][0].update(final_proof_sha256='0' * 64))
    with pytest.raises(ValueError, match='proof hash mismatch'):
        archive.verify(moved)


def test_recorded_missing_lane_input_does_not_invent_a_pair(completed_suite):
    run = first_run(completed_suite)
    fallback_problem(run, 'raw')
    baseline = run / 'problems/p1/02_r1_cycles/manifest.json'
    edit(baseline, lambda d: d['frozen_inputs']['lanes'][0].update(
        proof_path=None, proof_sha256=None, source_failure='Initial generation failed'))
    manifest = archive.verify(archive.archive(RUN_ID))
    assert len(manifest['paired_inputs']) == 47 and len(manifest['unpaired_finals']) == 1
    assert manifest['unpaired_finals'][0]['reason'] == 'pre_qwen_input_unavailable_after_source_failure'


def test_lazy_submission_after_partial_refinement_startup_has_no_invented_pair(completed_suite):
    run = first_run(completed_suite)
    fallback_problem(run, 'lazy_checked')
    baseline = run / 'problems/p1/02_r1_cycles'
    (baseline / 'manifest.json').unlink()
    partial = write(baseline / 'startup.json', {'state': 'failed', 'step': 'stage_initial_inputs'})
    destination = archive.archive(RUN_ID)
    manifest = archive.verify(destination)
    assert len(manifest['paired_inputs']) == 44 and len(manifest['unpaired_finals']) == 4
    assert all(row['reason'] == 'pre_qwen_manifest_unavailable' for row in manifest['unpaired_finals'])
    assert (destination / 'artifacts/imo2026/generation/run/problems/p1/02_r1_cycles/startup.json').read_bytes() == partial.read_bytes()
    assert (destination / 'artifacts/imo2026/generation/run/problems/p1/02_r1_cycles/input').is_dir()


def test_runtime_fallback_diagnostics_are_portable_without_redacting_model_feedback(completed_suite):
    run = first_run(completed_suite)
    fallback_problem(run, 'refinement_2')
    private_path = str(Path('/home') / 'researcher' / 'missing-result.json')
    message = f'FileNotFoundError: {private_path}'
    edit(run / 'final_results.json', lambda d: d['lanes'][0].update(interruption={'reason': message}))
    write(run / 'problem_sequence.json', {'state': 'completed_with_fallbacks', 'lane_errors': {'p1/t10_r01': message},
          'problems': [{'elapsed_seconds': 17.5, 'worker_error': message, 'lanes': [{'error': message}]}]})
    destination = archive.archive(RUN_ID)
    trace = json.loads((destination / 'artifacts/imo2026/generation/run/problem_sequence.json').read_text())
    expected = 'FileNotFoundError: /home/user/missing-result.json'
    assert trace['lane_errors']['p1/t10_r01'] == expected
    assert trace['problems'][0] == {'elapsed_seconds': 17.5, 'worker_error': expected, 'lanes': [{'error': expected}]}
    feedback = write(run / 'review.json', {'reason': message})
    assert archive.public_bytes(feedback, feedback.read_bytes(), set()) == feedback.read_bytes()


@pytest.mark.parametrize('failure', ['malformed_manifest', 'changed_input', 'missing_input', 'unrecorded_failure'])
def test_early_fallback_does_not_hide_a_corrupted_existing_baseline(completed_suite, failure):
    run = first_run(completed_suite)
    fallback_problem(run, 'raw')
    baseline = run / 'problems/p1/02_r1_cycles'
    if failure == 'malformed_manifest':
        (baseline / 'manifest.json').write_text('{broken JSON')
    elif failure == 'unrecorded_failure':
        edit(baseline / 'manifest.json', lambda d: d['frozen_inputs']['lanes'][0].update(proof_path=None))
    else:
        proof = next((baseline / 'input').glob('*.txt'))
        if failure == 'missing_input':
            proof.unlink()
        else:
            proof.write_bytes(b'Changed initial proof.')
    with pytest.raises(ValueError):
        archive.archive(RUN_ID)


@pytest.mark.parametrize('stage', ['refinement_1', 'refinement_2'])
def test_refined_submission_cannot_claim_an_absent_common_baseline(completed_suite, stage):
    fallback_problem(first_run(completed_suite), stage, remove_baseline=True)
    with pytest.raises(ValueError, match='No pre-Qwen input for refined final'):
        archive.archive(RUN_ID)


@pytest.mark.parametrize('state', ['failed', 'interrupted'])
def test_fallback_policy_does_not_accept_failed_or_interrupted_execution(completed_suite, state):
    run = first_run(completed_suite)
    fallback_problem(run, 'refinement_2')
    edit(run / 'final_results.json', lambda d: d['execution'].update(state=state))
    with pytest.raises(ValueError, match='did not complete submission export'):
        archive.archive(RUN_ID)


@pytest.mark.parametrize('failure', ['running', 'live_worker', 'incomplete_lane', 'wrong_seed', 'hash_mismatch'])
def test_rejects_incomplete_or_inconsistent_sources(completed_suite, failure):
    run = first_run(completed_suite)
    if failure == 'running':
        edit(completed_suite / '.workshop/runs' / RUN_ID / 'status.json', lambda d: d.update(state='running'))
    elif failure == 'live_worker':
        edit(run.parent / 'completion.json', lambda d: d.update(worker_exited=False))
    elif failure == 'incomplete_lane':
        edit(run / 'final_results.json', lambda d: d['lanes'][0].update(selected_stage='refinement_2'))
    elif failure == 'wrong_seed':
        edit(run / 'manifest.json', lambda d: d.update(raw_seed_offset=SEED + 1))
    else:
        proof = next((run / 'proofs').glob('*.txt'))
        proof.write_bytes(proof.read_bytes() + b'Changed.')
    with pytest.raises(ValueError):
        archive.archive(RUN_ID)
    assert not (completed_suite / 'benchmarks/reports' / (RUN_ID + '_full_trace')).exists()


@pytest.mark.parametrize('kind', ['credential', 'symlink'])
def test_rejects_sensitive_or_escaping_artifact_without_partial_export(completed_suite, tmp_path, kind):
    if kind == 'credential':
        write(first_run(completed_suite) / 'response.json', {'content': 'ghp_' + 'x' * 32})
    else:
        outside = write(tmp_path / 'outside.txt', b'outside\n')
        (first_run(completed_suite) / 'escape.txt').symlink_to(outside)
    with pytest.raises(ValueError, match='Credential|Symlink'):
        archive.archive(RUN_ID)
    assert not (completed_suite / 'benchmarks/reports' / (RUN_ID + '_full_trace')).exists()
    assert not list((completed_suite / '.workshop').glob('.*_archive_*'))


def test_child_rejects_parent_traversal(tmp_path):
    inside = tmp_path / 'bundle'
    inside.mkdir()
    write(tmp_path / 'outside.txt', b'outside\n')
    with pytest.raises(ValueError):
        archive.child(inside / '../outside.txt', inside)


@pytest.mark.parametrize('field', ['final', 'fusion_record', 'parsed', 'analysis', 'unknown_model_text'])
def test_semantic_model_fields_are_preserved_then_private_content_blocks_publication(completed_suite, field):
    private_path = str(Path('/home') / 'researcher' / 'private-draft.txt')
    content = (f'Consider the candidate at {private_path}.' if field in ('final', 'analysis', 'unknown_model_text')
               else {'path': private_path, 'conclusion': 'Inspect this argument.'})
    payload = {field: content, 'source_path': private_path}
    artifact = write(first_run(completed_suite) / 'model_result.json', payload)
    transformed = json.loads(archive.public_bytes(artifact, artifact.read_bytes(), set()))
    assert transformed[field] == content
    assert transformed['source_path'] == str(Path('/home/user') / 'private-draft.txt')
    with pytest.raises(ValueError, match='personal_home'):
        archive.archive(RUN_ID)
    assert not (completed_suite / 'benchmarks/reports' / (RUN_ID + '_full_trace')).exists()


@pytest.mark.parametrize('tamper', ['changed', 'unexpected', 'missing', 'pair_binding'])
def test_portable_verification_detects_tampering(completed_suite, tamper):
    destination = archive.archive(RUN_ID)
    manifest_path = destination / 'archive_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    proof = destination / manifest['paired_inputs'][0]['input_proof']
    if tamper == 'changed':
        proof.write_bytes(b'Altered proof.')
    elif tamper == 'unexpected':
        write(destination / 'extra.txt', b'Unlisted.')
    elif tamper == 'missing':
        proof.unlink()
    else:
        edit(manifest_path, lambda d: d['paired_inputs'][0].update(input_proof_sha256='0' * 64))
    with pytest.raises(ValueError):
        archive.verify(destination)
