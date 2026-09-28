"""Recover one complete grade from an isolated turn containing a truncated message."""
import json

from score_imo_v2 import validate_trace


def first_valid_response(path, runner):
    attempts = []
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            event = {}
        if 'attempt' in event and 'returncode' in event:
            attempts.append(dict(header=event, lines=[]))
        elif attempts:
            attempts[-1]['lines'].append(line)
    rejected, failures = 0, []
    for attempt in attempts:
        header = attempt['header']
        if header['returncode'] != 0:
            rejected += 1
            failures.append(dict(attempt=header['attempt'], returncode=header['returncode'],
                                 reason='model_capacity' if any('Selected model is at capacity.' in x for x in attempt['lines'])
                                 else 'process_failure'))
            continue
        try:
            validate_trace('\n'.join(attempt['lines']))
            messages = []
            for line in attempt['lines']:
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get('type') == 'item.completed' and event.get('item', {}).get('type') == 'agent_message':
                    messages.append(event['item']['text'])
            valid = []
            for index, message in enumerate(messages):
                try:
                    valid.append((index, runner.validate_grade(json.loads(message))))
                except (ValueError, KeyError, TypeError):
                    continue
            # Multiple complete grades are ambiguous; never choose by score.
            if len(valid) != 1:
                raise ValueError('Expected exactly one complete structured grade')
            index, grade = valid[0]
        except (ValueError, AssertionError, KeyError):
            rejected += 1
            continue
        selection = dict(selected_attempt=header['attempt'], total_attempts=len(attempts),
                         rejected_attempts_before_selection=rejected, failed_process_attempts=failures,
                         unselected_later_attempts=len(attempts)-header['attempt'])
        if len(messages) != 1:
            selection.update(message_count=len(messages), selected_message_index=index,
                             rejected_message_count=len(messages)-1,
                             recovery='single_complete_grade_in_one_isolated_turn')
        return grade, selection
    raise ValueError('No valid isolated response; this proof remains ungraded')


def export_cases(original, study, bindings, output, runner, failures):
    """Leave malformed responses ungraded without blocking unrelated completed cases."""
    for item in bindings:
        key = str(output / item['candidate_id'])
        try:
            original.export_batch(study, [item], output, runner)
        except ValueError as error:
            if str(error) != 'No valid isolated response; this proof remains ungraded':
                raise
            failures[key] = dict(unit_id=item['unit_id'], repeat=item['repeat'], reason=str(error))
