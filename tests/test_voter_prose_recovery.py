"""Missing comparison headings through new-run workers and bound collection."""
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from cross_lane_replay import response, sample
from test_public_reproduction import ROOT, load, pipeline
from test_stage_label_recovery import ENGINE, capture

recovery = load('prose_comparison_recovery', 'harnesses/cross_lane_voter/mechanical_recovery.py')
strict = load('prose_strict_validation', 'harnesses/cross_lane_voter/validation.py').strict_parse
EVIDENCE = ('The coordinate formula on Line 10 appears inconsistent at first. '
            'Checking the stated trigonometric identity shows the two expressions are equal; '
            'the apparent discrepancy is not an error. The reflection on Line 13 reverses '
            'the vertical coordinate and preserves the horizontal coordinate as required.\n'
            'The final dot product then vanishes by the identity already stated in the proof.')


def prose(label='A', section='B'):
    text = sample(label)
    before, body = text.split('## Proof ' + section + '\n', 1)
    # Replace only this proof section's two final fields.
    begin = body.index('Qualifications and supplied repairs:')
    end = body.index('\n## ', begin)
    return before + '## Proof ' + section + '\n' + body[:begin] + \
        'Qualifications and supplied repairs: ' + EVIDENCE + '\n' + body[end:]


@pytest.mark.parametrize('label', ['A', 'B'])
@pytest.mark.parametrize('section', ['A', 'B'])
@pytest.mark.parametrize('newline', ['\n', '\r\n'])
def test_prose_recovery_preserves_all_original_text_and_explicit_preference(label, section, newline):
    original = prose(label, section).replace('\n', newline)
    with pytest.raises(ValueError, match='Missing Decisive checks'):
        strict(original)
    normalized, receipt = recovery.restore_checks_label(original, strict)
    assert strict(normalized)['winner_label'] == label
    assert receipt['policy'] == recovery.PROSE_CHECKS_POLICY
    start, end = receipt['inserted_start_char'], receipt['inserted_end_char']
    assert normalized[:start] + normalized[end:] == original
    assert normalized[start:end] == 'Decisive checks:\n' + EVIDENCE.replace('\n', newline) + '\n\n'
    assert receipt['original_response_sha256'] == recovery.sha(original)
    assert receipt['normalized_response_sha256'] == recovery.sha(normalized)
    assert receipt['copied_evidence_sha256'] == recovery.sha(EVIDENCE.replace('\n', newline))
    assert receipt['model_calls'] == 0 and not receipt['new_mathematical_text']
    assert recovery.restore_checks_label(normalized, strict) == (normalized, None)


@pytest.mark.parametrize('text', [
    prose().replace('Line 13', 'Line 10'),
    prose().replace('Line 13', 'Line 0'),
    prose().replace('Line 13', 'Lines 13-2'),
    prose().replace('Line 13', 'Line 13x'),
    prose().replace(EVIDENCE, 'Line 10 and Line 13.'),
    prose().replace('Winner: A', 'Winner: A or B'),
    prose().replace('Winner: A', 'Winner: A\nWinner: B'),
    prose().replace('## Decision', 'Decisive checks:\n\n## Decision'),
    prose().replace('## Proof B', '## Proof A'),
    prose().replace(EVIDENCE, EVIDENCE + '\nQualifications and supplied repairs: NONE.'),
    prose().replace(EVIDENCE, EVIDENCE + '\n### Another comparison\nWinner: B'),
    '```markdown\n' + prose() + '\n```',
    prose().split('Reason:')[0],
])
def test_incomplete_or_ambiguous_prose_remains_invalid(text):
    with pytest.raises(ValueError):
        recovery.restore_checks_label(text, strict)


def test_new_snapshot_captures_comparison_code_and_old_runs_remain_strict(tmp_path):
    root = tmp_path/'run'
    capture(root)
    voter = pipeline.voter_module('1.12.0')
    # Import first, as a collector reading several runs would do.
    frozen = importlib.import_module(voter.__package__ + '.validation')
    for parse in (voter.parse, frozen.parse):
        with pytest.raises((ValueError, AssertionError)):
            parse(prose())
    for _ in range(2):
        with pipeline.runtime_policy.validation(root):
            for parse in (voter.parse, frozen.parse):
                parsed = parse(prose())
                assert parsed['winner_label'] == 'A'
                assert parsed['response_sha256'] == recovery.sha(prose())
        with pytest.raises((ValueError, AssertionError)):
            voter.parse(prose())
    assert not (root/'label_recoveries').exists(), 'Read-only collection wrote recovery files'
    captured = root/'label_runtime/comparison_recovery.py'
    assert captured.read_bytes() == (ROOT/'harnesses/cross_lane_voter/mechanical_recovery.py').read_bytes()
    with captured.open('a') as stream:
        stream.write('\n# tampered\n')
    with pytest.raises(ValueError, match='Captured label recovery code changed'):
        pipeline.runtime_policy.saved(root)


@pytest.mark.parametrize('single_gpu', [False, True])
def test_actual_timeout_continuation_uses_new_run_policy_without_extra_calls(tmp_path, single_gpu):
    environment = capture(tmp_path/'run')
    if single_gpu:
        import os
        environment.update(GPU0_BULK_URL='http://127.0.0.1:1', GPU0_BULK_ENGINE=str(ENGINE))
        environment['PYTHONPATH'] = str(ROOT/'harnesses/single_gpu/client_compat') + os.pathsep + environment['PYTHONPATH']
    result = subprocess.run([sys.executable, '-B', str(ROOT/'tests/selection_timeout_driver.py'),
        '--prose-recovery'], input=prose(), text=True, capture_output=True, env=environment, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'prose_continuation' in json.loads(result.stdout)['checks']


def test_public_collection_recovers_bound_prose_and_rejects_tampering(tmp_path, monkeypatch):
    root = tmp_path/'run'
    capture(root)
    voter = pipeline.voter_module('1.12.0')
    candidates = {}
    for cid in pipeline.CANDIDATES:
        proof = root/'proofs'/(cid+'.md');proof.parent.mkdir(exist_ok=True)
        proof.write_text('Submitted proof from '+cid+'.\n')
        candidates[cid] = dict(candidate_id=cid, selected_stage='refinement_2',
            proof_path=str(proof), proof_sha256=pipeline.proof_hash(proof))
    runtime = dict(raw_seed_offset=0, seed_namespace=voter.DEFAULT_NAMESPACE, model_timeout_sec=600,
        gemma_endpoint='http://127.0.0.1:8030/v1', qwen_endpoint='http://127.0.0.1:8027/v1')
    identity = pipeline.read(root/'harness_release.json');identity['parameters'] = runtime
    pipeline.write(root/'harness_release.json', identity)
    monkeypatch.setattr(pipeline, 'collect_lane', lambda _root, _pid, cid, _issues: candidates[cid])
    monkeypatch.setattr(pipeline, 'voter_problem', lambda *_: 'Prove the claim.')
    before, calls = {}, []
    case_id = 'pair_02_qwen_forward'

    def worker(command, **kwargs):
        assert kwargs['env']['WORKSHOP_LABEL_RECOVERY'] == str(root/'label_recovery.json')
        directory = Path(command[-1])

        def call(**kw):
            calls.append(kw)
            saved = response(kw)
            if case_id in str(kw['output_dir']):
                saved['text'] = prose()
                saved['final_sha256'] = voter.digest(saved['text'].encode())
                Path(saved['final_path']).write_text(saved['text'])
            return saved

        # Reproduce the original parser's failure; the real controller must
        # replay the captured rule when collecting bound responses.
        result = voter.run(directory, call)
        assert result['summaries']['combined']['valid_calls'] == 23
        before.update({f:f.read_bytes() for f in directory.rglob('*') if f.is_file()})
        return 2

    monkeypatch.setattr(pipeline, 'run_process', worker)
    selection = pipeline.cross_lane_selection(root, 'P', '1.12.0', execute=True)
    assert len(calls) == 24 and selection['state'] == 'completed'
    assert selection['summaries']['combined']['valid_calls'] == 24
    repaired = next(v for v in selection['vote_table'] if v['case_id'] == case_id)
    assert repaired['binding_verified'] and repaired['mechanical_recovery']['model_calls'] == 0
    for path, data in before.items():
        if path.name not in ('SELECTIONS.json', 'REPORT.md'):
            assert path.read_bytes() == data
    monkeypatch.setattr(pipeline, 'run_process', lambda *a, **kw: pytest.fail('Repeated inference'))
    assert pipeline.cross_lane_selection(root, 'P', '1.12.0', execute=False) == selection
    path = root/selection['artifact_directory']/'cases'/case_id/'audit/call_result.json'
    call = pipeline.read(path);call['text'] += '\nChanged response'
    pipeline.write(path, call)
    assert pipeline.cross_lane_selection(root, 'P', '1.12.0', execute=False)['state'] == 'incomplete'
