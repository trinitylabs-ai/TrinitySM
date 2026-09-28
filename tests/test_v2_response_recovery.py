"""Recover malformed exports without choosing among scores or weakening isolation."""
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def recovery(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'scripts'))
    return importlib.import_module('v2_response_recovery')


@pytest.fixture
def runner():
    def validate(value):
        if not isinstance(value, dict) or type(value.get('score')) is not int or not 0 <= value['score'] <= 7:
            raise ValueError('Malformed grade')
        return value
    return SimpleNamespace(validate_grade=validate)


def transcript(tmp_path, messages, extra=()):
    events = [dict(attempt=1, returncode=0)]
    events += [dict(type='item.completed', item=dict(type='agent_message', text=text)) for text in messages]
    events += list(extra) + [dict(type='turn.completed')]
    path = tmp_path / 'codex.jsonl'
    path.write_text('\n'.join(json.dumps(event) for event in events))
    return path


def test_recovers_single_complete_grade_after_truncated_message(recovery, runner, tmp_path):
    path = transcript(tmp_path, ['{"score": 7, "reason": "truncated', '{"score": 3}'])
    grade, selection = recovery.first_valid_response(path, runner)
    assert grade == {'score': 3}
    assert selection['selected_attempt'] == 1
    assert selection['selected_message_index'] == 1
    assert selection['rejected_message_count'] == 1
    assert selection['recovery'] == 'single_complete_grade_in_one_isolated_turn'


@pytest.mark.parametrize('messages', [
    ['{"score": 3}', '{"score": 7}'],
    ['{"score": 7}', '{"score": 3}'],
    ['{"score": 3}', '{"score": 3}'],
    ['{"score": 3'],
])
def test_rejects_multiple_complete_grades_or_no_complete_grade(recovery, runner, tmp_path, messages):
    with pytest.raises(ValueError, match='No valid isolated response'):
        recovery.first_valid_response(transcript(tmp_path, messages), runner)


@pytest.mark.parametrize('extra', [
    [dict(type='item.completed', item=dict(type='command_execution'))],
    [dict(type='turn.completed')],
])
def test_recovery_preserves_isolation_requirement(recovery, runner, tmp_path, extra):
    with pytest.raises(ValueError, match='No valid isolated response'):
        recovery.first_valid_response(transcript(tmp_path, ['{"score": 3}'], extra), runner)


def test_malformed_response_does_not_block_other_exports(recovery, tmp_path):
    exported = []
    def export(study, bindings, output, runner):
        if bindings[0]['unit_id'] == 'bad':
            raise ValueError('No valid isolated response; this proof remains ungraded')
        exported.extend(bindings)
    bindings = [dict(unit_id=uid, candidate_id=uid, repeat=1) for uid in ['bad', 'good']]
    failures = {}
    recovery.export_cases(SimpleNamespace(export_batch=export), {}, bindings, tmp_path, None, failures)
    assert exported == [bindings[1]]
    assert list(failures.values()) == [dict(unit_id='bad', repeat=1,
        reason='No valid isolated response; this proof remains ungraded')]


def test_unrelated_integrity_errors_still_stop_export(recovery, tmp_path):
    def export(*args):
        raise ValueError('Frozen input changed')
    with pytest.raises(ValueError, match='Frozen input changed'):
        recovery.export_cases(SimpleNamespace(export_batch=export), {},
            [dict(unit_id='a', candidate_id='a', repeat=1)], tmp_path, None, {})
