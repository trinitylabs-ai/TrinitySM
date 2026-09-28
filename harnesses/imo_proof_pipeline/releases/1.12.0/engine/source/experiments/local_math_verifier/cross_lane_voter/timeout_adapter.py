"""Experiment-only 600s logical deadline; saved initial answer or one completion.

The frozen engine and its ordinary BF remain unchanged. No timeout can enter
the inherited fresh-retry branch. Each thread owns its own deadline and trace.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path
import hashlib
import json
import time

from experiments.local_math_verifier import limit_recovery as limits
from experiments.local_math_verifier import timeout_recovery as timeout

POLICY = 'logical-600s-initial-else-one-answer-only-120s-v1'
LIMIT = 600
ANSWER_SECONDS = 120
ANSWER_TOKENS = 8192
CUE = (
    'The time limit for analysis has been reached. Use the preserved reasoning '
    'and response above to produce your final answer now. Do not restart the '
    'analysis or perform further extended reasoning. Return one complete '
    'Markdown proof comparison in the system prompt format, with both proof '
    'audits and exactly one Winner: A or Winner: B and a brief reason. '
    'Keep qualifications and uncertainty explicit; do not invent checks.'
)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


class Deadline(timeout.TimeoutRecoveryFailure):
    pass


def parsed_answer(text, parser, repair):
    try:
        return parser(text), None
    except ValueError:
        normalized, detail = repair(text, parser)
        parsed = parser(normalized)
        parsed['response_sha256'] = sha(text)
        return parsed, detail


@contextmanager
def install(bf, original_caller, parser, repair, *, clock=time.monotonic):
    active = ContextVar('comparison_deadline', default=None)
    original_timeout_call = bf._timeout_call
    raw = bf._ORIGINAL

    def guarded(kwargs, primary=None):
        state = active.get()
        if state is None:
            return original_timeout_call(kwargs, primary=primary)

        def request(**current):
            remaining = state['deadline'] - clock()
            if remaining <= 0:
                state['expired'] = True
                raise Deadline('logical comparison deadline reached')
            current = {**current, 'config': replace(current['config'], timeout_seconds=remaining)}
            first = state.get('initial') is None
            if first:
                state['initial_kwargs'] = dict(current)
            try:
                generated = raw(**current)
            except TimeoutError as error:
                state['expired'] = True
                state['timeout_evidence'] = getattr(error, 'evidence', None)
                if first:
                    partial = deepcopy(getattr(error, 'partial', {'text': '', 'reasoning': ''}))
                    stage, dest = current['stage'], Path(current['output_dir'])
                    partial['metadata'] = dict(model=current['model'], endpoint=current['endpoint'],
                        prompt_sha256=sha(current['prompt']), user_prompt_sha256=sha(current['user_prompt']),
                        system_prompt_path=str((dest / (stage + '.prompt.txt')).resolve()),
                        user_prompt_path=str((dest / (stage + '.user_prompt.txt')).resolve()),
                        config=asdict(current['config']), finish_reason='timeout',
                        transport='saved-partial-from-openai-compatible-loopback-http',
                        timeout_evidence=state['timeout_evidence'])
                    state['initial'] = partial
                # Terminal subclass bypasses all inherited fresh timeout retries.
                raise Deadline('logical comparison deadline reached') from error
            if first:
                state['initial'] = deepcopy(generated)
            if clock() >= state['deadline']:
                state['expired'] = True
                raise Deadline('logical comparison deadline reached after transport return')
            return generated

        return limits.run(request, kwargs, primary=primary)

    def fallback(state, arguments):
        directory = Path(arguments['output_dir']) / 'deadline_fallback'
        directory.mkdir(parents=True, exist_ok=False)
        initial = state.get('initial') or {'text': '', 'reasoning': ''}
        write(directory / 'initial_response.json', initial)
        original = state.get('initial_kwargs')
        receipt = dict(policy=POLICY, logical_limit_seconds=LIMIT,
            elapsed_before_fallback=clock() - state['started'],
            initial_response_sha256=hashlib.sha256((directory / 'initial_response.json').read_bytes()).hexdigest(),
            initial_text_sha256=sha(str(initial.get('text') or '')),
            initial_reasoning_sha256=sha(str(initial.get('reasoning') or '')),
            timeout_evidence=state.get('timeout_evidence'), fresh_retries_after_timeout=0,
            max_answer_only_continuations=1, answer_only_timeout_seconds=ANSWER_SECONDS,
            answer_only_max_tokens=ANSWER_TOKENS, thinking_enabled=False)
        text = str(initial.get('text') or '').strip()
        try:
            parsed, repair_record = parsed_answer(text, parser, repair)
        except (ValueError, AssertionError):
            # Never derive a winner from prose or from the reasoning channel.
            prior = timeout.reusable(initial)
            if not prior or original is None:
                write(directory / 'failure.json', {**receipt, 'error': 'No preserved trace; fresh retry prohibited'})
                raise Deadline('No saved trace available for the one authorized continuation')
            cfg = replace(original['config'], max_tokens=ANSWER_TOKENS, timeout_seconds=ANSWER_SECONDS,
                          thinking_enabled=False, thinking_token_budget=None, reasoning_effort=None)
            answer_dir = directory / 'answer_only'
            answer_dir.mkdir(exist_ok=False)
            request = {**original, 'config': cfg, 'output_dir': answer_dir,
                       'stage': 'answer_only_completion', 'prior_generation': prior,
                       'continuation_instruction': CUE}
            request.pop('timeout_recovery_prefix', None)
            receipt.update(action='one_answer_only_continuation', prior_sha256=sha(prior),
                           continuation_config=asdict(cfg), cue_sha256=sha(CUE))
            write(directory / 'continuation_started.json', receipt)
            try:
                generated = raw(**request)  # Raw transport: no BF, no retry.
                text = str(generated.get('text') or '').strip()
                if generated.get('metadata', {}).get('finish_reason') == 'length':
                    raise ValueError('Answer-only response exhausted its token cap')
                parsed, repair_record = parsed_answer(text, parser, repair)
            except Exception as error:
                write(directory / 'failure.json', {**receipt, 'error': f'{type(error).__name__}: {error}'})
                raise Deadline('The one answer-only continuation failed; outputs preserved') from error
        else:
            receipt.update(action='use_initial_answer')
            generated = initial
        receipt.update(final_sha256=sha(text), elapsed_seconds=clock() - state['started'],
                       mechanical_recovery=repair_record)
        write(directory / 'decision.json', receipt)
        metadata = deepcopy(generated.get('metadata') or {})
        metadata['comparison_timeout_policy'] = receipt
        final = Path(arguments['output_dir']) / (arguments['stage_name'] + '.final.md')
        with final.open('x') as f:
            f.write(text + '\n')
        result = dict(text=text, parsed=parsed, metadata=metadata, final_path=str(final.resolve()),
                      final_sha256=sha(text), attempt_dir=str(directory.resolve()),
                      attempts=[receipt], token_policy=POLICY)
        write(Path(arguments['output_dir']) / 'call_result.json', result)
        return result

    def caller(**arguments):
        started = clock()
        state = dict(started=started, deadline=started + LIMIT, expired=False)
        token = active.set(state)
        root = Path(arguments['output_dir'])
        write(root / 'logical_timeout_policy.json', dict(policy=POLICY, logical_limit_seconds=LIMIT,
             answer_only_max_tokens=ANSWER_TOKENS, answer_only_timeout_seconds=ANSWER_SECONDS,
             no_fresh_retry_after_timeout=True, thinking_enabled_for_answer_only=False))
        try:
            try:
                return original_caller(**arguments)
            except timeout.TimeoutRecoveryFailure:
                if not state['expired']:
                    raise
                return fallback(state, arguments)
        finally:
            active.reset(token)

    bf._timeout_call = guarded
    try:
        yield caller
    finally:
        bf._timeout_call = original_timeout_call
