"""Model-free checks of unchanged-proof selection, audits and fail-closed evidence."""
import builtins
import hashlib
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harnesses.proof_selector import protocols, selector


def candidates():
    result = []
    for index in range(4):
        proof = f'\nOriginal proof-anchor-{index}: for real x, x² ≥ 0.  \n'
        result.append({'candidate_id': f'hidden_lane_{index}', 'proof': proof,
                       'proof_file_sha256': hashlib.sha256(proof.encode()).hexdigest(),
                       'selected_stage': f'hidden_stage_{index}'})
    return result


def fusion_record(verdict='ACCEPT_AS_WRITTEN', marker='fusion-evidence', wrong_label=False):
    protocol = protocols.fusion()
    header = 'FUSION_' + verdict
    schema = protocol.SCHEMAS[header]
    fields = {}
    for name in schema['fields']:
        if name == 'verdict':
            value = verdict
        elif name.startswith('reviewer_'):
            label = ('REVIEWER_MISSED_DEFECT' if name == 'reviewer_1_assessment'
                     and verdict in ('REPAIR_NEEDED', 'ACCEPT_WITH_ROUTINE_COMPLETION') else 'NO_DEFECT_REPORTED')
            if wrong_label and name == 'reviewer_1_assessment':
                label = 'DEFECT_REJECTED'
            value = label + ' | ' + marker
        elif name == 'repair_scope':
            value = 'LOCAL'
        else:
            value = marker
        fields[name] = value
    return '\n'.join([header] + [f'{key}: {value}' for key, value in fields.items()] + [schema['footer']])


def acceptance(verdict='CERTIFIED', marker='audit-evidence'):
    return ('# Fusion Acceptance Certification\nverdict: ' + verdict + '\n\n'
            '## Atomic Checks\n' + marker + '\n\n'
            '## First Invalid Step\n' + ('NONE' if verdict == 'CERTIFIED' else marker) + '\n\n'
            '## Missing Obligation\nNONE\n\n'
            '## Counterexample or Failure Witness\nNONE\n\n'
            '## Certification Summary\n' + marker + '\n\n'
            '# End Fusion Acceptance Certification')


def critique(verdict='SUPPORTED', marker='critique-evidence'):
    return '\n'.join(['CRITIQUE_AUDIT', f'verdict: {verdict}'] +
        [f'{key}: {marker}' for key in ('target', 'proof_evidence', 'independent_check', 'consequence')] +
        ['END_CRITIQUE_AUDIT'])


def comparison(winner='UNDECIDED', marker='comparison-evidence'):
    return '\n'.join(['PROOF_COMPARISON', f'winner: {winner}'] +
        [f'{key}: {marker}' for key in ('decisive_obligation', 'evidence_a', 'evidence_b', 'reason')] +
        ['END_PROOF_COMPARISON'])


def default_response(request):
    role = request['role']
    if role.startswith('reviewer_'):
        return {'reviewer_1': 'NO_FIRST_BREAK', 'reviewer_2': 'NO_ADVERSARIAL_BREAK',
                'reviewer_3': 'NO_UNCLOSED_OBLIGATION_FOUND'}[role]
    if role == 'fusion':
        return fusion_record()
    if role == 'acceptance':
        return acceptance()
    if role == 'critique':
        return critique()
    return comparison()


class FakeClient:
    def __init__(self, respond=default_response, native_usage=False):
        self.respond, self.requests = respond, []
        self.native_usage = native_usage

    def call(self, **request):
        self.requests.append(request)
        request['output_dir'].mkdir(parents=True, exist_ok=False)
        text = self.respond(request)
        # Engine must reparse the actual text rather than trusting this flag.
        return {'text': text, 'parsed': {'valid': True}, 'artifact_dir': str(request['output_dir']),
                'usage': ([{'attempt': 1, 'phase': 'thinking', 'usage': {'prompt_tokens': 2, 'completion_tokens': 3}},
                           {'attempt': 1, 'phase': 'answer', 'usage': {'prompt_tokens': 5, 'completion_tokens': 7}}]
                          if self.native_usage else {'prompt_tokens': 2, 'completion_tokens': 3}),
                'elapsed_seconds': .25, 'raw_thoughts': 'NEVER_FORWARD_RAW_THOUGHTS'}


def select(tmp_path, client=None, rows=None, **kwargs):
    return selector.select_problem(problem_id='secret_problem_id', problem='Prove x² ≥ 0 for real x.',
        candidates=rows or candidates(), client=client or FakeClient(), output_dir=tmp_path / 'selection',
        seed=12345, **kwargs)


def anchor(request):
    return int(re.search(r'proof-anchor-(\d)', request['user']).group(1))


def round_number(request):
    return int(next(part.split('_')[1] for part in request['output_dir'].parts if part.startswith('round_')))


def test_four_independent_reviews_preserve_exact_proof_and_blind_metadata(tmp_path):
    rows, client = candidates(), FakeClient(native_usage=True)
    result = select(tmp_path, client, rows)
    assert result['state'] == 'completed' and result['selection_basis'] == 'audited_acceptance'
    assert len(result['assessments']) == 4 and len(result['comparisons']) == 3
    chosen = next(row for row in rows if row['candidate_id'] == result['selected_candidate_id'])
    output = tmp_path / 'selection'
    assert (output / 'selected_proof.md').read_bytes() == chosen['proof'].encode()
    assert result['selected_proof_sha256'] == chosen['proof_file_sha256']
    assert not result['proof_modified'] and not result['mathematical_correctness_verified']
    for assessed in result['assessments']:
        original = next(row for row in rows if row['candidate_id'] == assessed['candidate_id'])
        assert (output / assessed['proof_path']).read_bytes() == original['proof'].encode()
        assert len(assessed['rounds']) == 1
    for request in client.requests:
        prompts = request['system'] + request['user']
        assert not any(row['candidate_id'] in prompts or row['selected_stage'] in prompts for row in rows)
        assert 'secret_problem_id' not in prompts and 'NEVER_FORWARD_RAW_THOUGHTS' not in prompts
        assert request['continuation'] == protocols.CONTINUATIONS[request['role']]
        if request['role'].startswith('reviewer_'):
            assert request['system'] == protocols.reviewer(int(request['role'][-1])).SYSTEM_PROMPT
            assert 'fusion-evidence' not in request['user'] and 'audit-evidence' not in request['user']
        if request['role'] in ('comparison', 'arbitration'):
            assert 'proof-anchor-' not in prompts  # Only structured final evidence is compared.
    assert result['usage']['calls'] == 26
    assert result['usage']['physical_requests'] == 52
    assert result['usage']['tokens'] == {'prompt_tokens': 26 * 7, 'completion_tokens': 26 * 10}
    assert json.loads((output / 'selection.json').read_text()) == result


def test_routine_acceptance_is_not_confused_with_supported_repair(tmp_path):
    def response(request):
        if request['role'] == 'fusion':
            return fusion_record('ACCEPT_WITH_ROUTINE_COMPLETION' if anchor(request) == 2 else 'REPAIR_NEEDED')
        return default_response(request)
    client = FakeClient(response)
    result = select(tmp_path, client)
    assert result['selected_candidate_id'] == 'hidden_lane_2'
    assert result['selection_basis'] == 'audited_acceptance' and result['comparisons'] == []
    for assessed in result['assessments']:
        if assessed['candidate_id'] == 'hidden_lane_2':
            assert assessed['audited_acceptance'] and assessed['routine_completion_required']
        else:
            assert not assessed['audited_acceptance'] and assessed['final_verdict'] == 'REPAIR_NEEDED'
            assert assessed['assessment_state'] == 'audited_nonacceptance'
        assert assessed['proof_modified'] is False
    assert sum(call['role'] == 'critique' for call in client.requests) == 3


def test_rereview_uses_only_latest_structured_dispute_and_original_proof(tmp_path):
    def response(request):
        if request['role'] == 'fusion':
            return fusion_record(marker=f'FUSION_ROUND_{round_number(request)}')
        if request['role'] == 'acceptance' and anchor(request) == 0:
            number = round_number(request)
            return acceptance('CERTIFIED' if number == 3 else 'REJECTED', marker=f'AUDIT_ROUND_{number}')
        return default_response(request)
    client = FakeClient(response)
    result = select(tmp_path, client)
    changed = next(row for row in result['assessments'] if row['candidate_id'] == 'hidden_lane_0')
    assert len(changed['rounds']) == 3 and changed['audited_acceptance']
    for request in client.requests:
        if request['role'].startswith('reviewer_') and anchor(request) == 0:
            number = round_number(request)
            assert 'Original proof-anchor-0:' in request['user']
            if number > 1:
                assert f'FUSION_ROUND_{number - 1}' in request['user']
                assert f'AUDIT_ROUND_{number - 1}' in request['user']
            if number == 3:
                assert 'FUSION_ROUND_1' not in request['user'] and 'AUDIT_ROUND_1' not in request['user']
    assert len({row['reviews']['reviewer_1']['seed'] for row in changed['rounds']}) == 3


@pytest.mark.parametrize('audit_verdict', ['CHALLENGED', 'UNRESOLVED'])
def test_disputed_negative_assessment_rereviews_then_stays_explicitly_uncertain(tmp_path, audit_verdict):
    def response(request):
        if request['role'] == 'fusion':
            return fusion_record('REPAIR_NEEDED')
        if request['role'] == 'critique':
            return critique(audit_verdict)
        return default_response(request)
    result = select(tmp_path, FakeClient(response), max_rounds=2)
    assert result['selection_basis'] == 'best_effort_unverified'
    assert all(len(row['rounds']) == 2 and row['uncertain'] and not row['audited_acceptance']
               and row['assessment_state'] == 'unresolved' for row in result['assessments'])


def test_supported_negative_stops_without_fictional_repair_credit(tmp_path):
    def response(request):
        return fusion_record('REPAIR_NEEDED') if request['role'] == 'fusion' else default_response(request)
    result = select(tmp_path, FakeClient(response))
    assert result['selection_basis'] == 'best_effort_unverified'
    assert all(len(row['rounds']) == 1 and not row['audited_acceptance'] for row in result['assessments'])
    assert all(row['final_verdict'] == 'REPAIR_NEEDED' and not row['proof_modified'] for row in result['assessments'])


def test_inverted_comparison_order_is_mapped_before_agreement(tmp_path):
    def response(request):
        if request['role'] == 'comparison':
            return comparison('A' if request['model'] == 'gemma' else 'B')
        return default_response(request)
    result = select(tmp_path, FakeClient(response))
    assert result['selected_candidate_id'] == result['assessments'][0]['candidate_id']
    assert all(row['basis'] == 'independent_comparison_agreement' and row['arbitration'] is None
               for row in result['comparisons'])
    for pair in result['comparisons']:
        assert pair['decisions'][0]['order'] == [0, 1]
        assert pair['decisions'][1]['order'] == [1, 0]
        assert all(row['mapped_winner'] == 0 for row in pair['decisions'])


def test_disagreement_has_one_bounded_blinded_arbitration_and_explicit_tie(tmp_path):
    def response(request):
        if request['role'] == 'comparison':
            return comparison('A')  # Opposite physical candidates due to inversion.
        return default_response(request)
    client = FakeClient(response)
    result = select(tmp_path, client)
    assert sum(row['role'] == 'arbitration' for row in client.requests) == 3
    assert all(row['basis'] == 'seed_order_tie_no_quality_distinction' for row in result['comparisons'])
    assert result['selected_candidate_id'] == result['assessments'][0]['candidate_id']
    for request in client.requests:
        if request['role'] == 'arbitration':
            assert '"mapped_winner": "A"' in request['user']
            assert '"mapped_winner": "B"' in request['user']
            assert 'gemma' not in request['user'].lower() and 'qwen' not in request['user'].lower()


def test_blinded_seed_order_is_reproducible_independent_of_input_order(tmp_path):
    rows = candidates()
    first = select(tmp_path / 'one', rows=rows)
    second = select(tmp_path / 'two', rows=list(reversed(rows)))
    assert first['selected_candidate_id'] == second['selected_candidate_id']
    assert [r['candidate_id'] for r in first['assessments']] == [r['candidate_id'] for r in second['assessments']]
    assert first['assessments'][0]['rounds'][0]['reviews']['reviewer_1']['seed'] == second['assessments'][0]['rounds'][0]['reviews']['reviewer_1']['seed']


def test_identical_proofs_remain_four_original_candidates(tmp_path):
    rows = candidates()
    for row in rows[1:]:
        row.update(proof=rows[0]['proof'], proof_file_sha256=rows[0]['proof_file_sha256'])
    result = select(tmp_path, rows=rows)
    assert len(result['assessments']) == 4
    assert len({row['candidate_id'] for row in result['assessments']}) == 4
    assert result['selected_proof_sha256'] == rows[0]['proof_file_sha256']


@pytest.mark.parametrize('failure', ['hash', 'duplicate', 'three', 'invalid_fusion', 'wrong_assessment', 'infrastructure'])
def test_any_candidate_or_execution_failure_leaves_no_selected_subset(tmp_path, failure):
    rows = candidates()
    count = {'fusion': 0}
    def response(request):
        if request['role'] == 'fusion':
            count['fusion'] += 1
            if count['fusion'] == 2:
                if failure == 'invalid_fusion':
                    return 'not a fusion record'
                if failure == 'wrong_assessment':
                    return fusion_record(wrong_label=True)
                if failure == 'infrastructure':
                    raise TimeoutError('BF transport failure')
        return default_response(request)
    if failure == 'hash':
        rows[0]['proof_file_sha256'] = '0' * 64
    elif failure == 'duplicate':
        rows[1]['candidate_id'] = rows[0]['candidate_id']
    elif failure == 'three':
        rows.pop()
    with pytest.raises((ValueError, TimeoutError)):
        select(tmp_path, FakeClient(response), rows)
    output = tmp_path / 'selection'
    assert not (output / 'selection.json').exists() and not (output / 'selected_proof.md').exists()
    status = json.loads((output / 'status.json').read_text())
    assert status['state'] == 'failed' and status['selection_completed'] is False
    assert 'selected_candidate_id' not in status


def test_output_cannot_overwrite_an_existing_selection(tmp_path):
    select(tmp_path)
    path = tmp_path / 'selection/selection.json'
    before = path.read_bytes()
    with pytest.raises(ValueError, match='fresh directory'):
        select(tmp_path)
    assert path.read_bytes() == before


def test_progress_is_flushed_and_records_active_call_without_printing_proofs(tmp_path, monkeypatch, capsys):
    flushed = []
    original_print = builtins.print
    def printing(*args, **kwargs):
        flushed.append(kwargs.get('flush'))
        return original_print(*args, **kwargs)
    monkeypatch.setattr(builtins, 'print', printing)
    observed = []
    def response(request):
        status = json.loads((tmp_path / 'selection/status.json').read_text())
        assert status['state'] == 'running' and not status['selection_completed']
        active = status['active_call']
        assert active['state'] == 'running' and active['role'] == request['role']
        assert active['model'] == request['model']
        assert (tmp_path / 'selection' / active['artifact_dir']) == request['output_dir']
        observed.append(active)
        return default_response(request)
    result = select(tmp_path, FakeClient(response))
    output = capsys.readouterr().out
    assert 'candidates/candidate_01/round_01/reviewer_1: started model=gemma' in output
    assert 'completed outcome=NO_FIRST_BREAK elapsed=' in output
    assert 'comparisons/pair_01/qwen: started model=qwen' in output
    assert 'completed selection_basis=audited_acceptance elapsed=' in output
    assert 'proof-anchor-' not in output and 'fusion-evidence' not in output and 'audit-evidence' not in output
    assert 'NEVER_FORWARD_RAW_THOUGHTS' not in output and 'Prove x²' not in output
    assert len(observed) == result['usage']['calls']
    assert flushed and all(flushed)


class SignalInterrupt(KeyboardInterrupt):
    signum = 15


@pytest.mark.parametrize('interruption,expected_code', [(KeyboardInterrupt(), 130), (SystemExit(143), 143),
                                                       (SignalInterrupt(), 143)])
def test_interruption_after_all_assessments_preserves_evidence_but_selects_nothing(tmp_path, capsys,
                                                                                interruption, expected_code):
    def response(request):
        if request['role'] == 'comparison':
            raise interruption
        return default_response(request)
    with pytest.raises(type(interruption)):
        select(tmp_path, FakeClient(response))
    root = tmp_path / 'selection'
    status = json.loads((root / 'status.json').read_text())
    assert status['state'] == 'interrupted' and status['exit_code'] == expected_code
    assert status['selection_completed'] is False and 'selected_candidate_id' not in status
    assert len(list((root / 'candidates').glob('*/assessment.json'))) == 4
    assert not (root / 'selection.json').exists() and not (root / 'selected_proof.md').exists()
    output = capsys.readouterr().out
    assert 'comparisons/pair_01/gemma: interrupted' in output
    assert 'interrupted; no proof selected' in output


def test_late_comparison_parse_failure_is_not_a_tie_or_partial_selection(tmp_path):
    def response(request):
        if request['role'] == 'comparison' and request['model'] == 'qwen':
            return 'The candidates look equally good.'
        return default_response(request)
    with pytest.raises(ValueError, match='invalid final protocol record'):
        select(tmp_path, FakeClient(response))
    root = tmp_path / 'selection'
    assert json.loads((root / 'status.json').read_text())['state'] == 'failed'
    assert len(list((root / 'candidates').glob('*/assessment.json'))) == 4
    assert not (root / 'selection.json').exists() and not (root / 'selected_proof.md').exists()
