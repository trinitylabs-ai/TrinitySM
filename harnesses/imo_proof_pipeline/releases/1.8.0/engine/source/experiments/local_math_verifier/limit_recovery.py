"""One phase-aware recovery request for either token or wall-time limits."""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
import shutil
from typing import Any, Callable

from . import runtime as transport
from . import timeout_recovery as timeout

POLICY_ID = 'unified-limits-65536-450-one-retry-v1'
RECOVERY_MAX_TOKENS = 65_536
RECOVERY_TIMEOUT_SECONDS = 450
FALLBACK_SOURCE = 'pre_budget_forcing_limit_fallback'
ARTIFACT_SUFFIXES = ('.prompt.txt', '.user_prompt.txt', '.raw_response.json', '.reasoning.txt', '.metadata.json')


class LimitHit(RuntimeError):
    def __init__(self, partial: dict[str, Any], source: Path):
        super().__init__('output token limit reached')
        self.partial, self.source = partial, source


def save_evidence(error: Exception, current: dict[str, Any], directory: Path) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    trigger = 'length' if isinstance(error, LimitHit) else 'timeout'
    partial = getattr(error, 'partial', {'text': '', 'reasoning': ''})
    saved = directory / 'limited_response.json'
    original = (error.source if isinstance(error, LimitHit) else
                Path(error.evidence['partial_path']) if getattr(error, 'evidence', None) else None)
    if original is not None:
        shutil.copy2(original, saved)
    else:
        transport.write_json(saved, {'choices': [{'message': {'content': partial.get('text', ''),
            'reasoning': partial.get('reasoning', '')}, 'finish_reason': None}]})
    return {'trigger': trigger, 'response_path': str(saved.resolve()),
            'response_sha256': hashlib.sha256(saved.read_bytes()).hexdigest(),
            'config': asdict(current['config']),
            'transport_timeout_evidence': getattr(error, 'evidence', None)}


def run(call: Callable[..., dict[str, Any]], kwargs: dict[str, Any],
        primary: dict[str, Any] | None = None) -> dict[str, Any]:
    original = dict(kwargs)
    root, stage = Path(original['output_dir']), str(original['stage'])
    phase = 'budget_forcing' if primary is not None else 'primary'
    ledger = root / f'{stage}.limit_recovery' / phase
    current = dict(original)
    decisions: list[dict[str, Any]] = []
    retry = None
    for attempt in (0, 1):
        try:
            result = call(**current)
            if result.get('metadata', {}).get('finish_reason') == 'length':
                raise LimitHit(result, Path(current['output_dir']) / f'{stage}.raw_response.json')
        except (TimeoutError, LimitHit) as error:
            try:
                evidence = save_evidence(error, current, ledger / f'limit_{attempt}')
            except Exception as evidence_error:
                raise timeout.TimeoutRecoveryFailure('cannot record limit evidence; fail closed') from evidence_error
            cleaned, trimming = timeout.clean_timeout_result(getattr(error, 'partial', {'text': '', 'reasoning': ''}))
            row = {'attempt': attempt, 'evidence': evidence, 'trimming': trimming}
            decisions.append(row)
            # Recovery is terminal at either limit, regardless of repetition or phase.
            if attempt == 1:
                row['action'] = 'fail_closed'
                transport.write_json(ledger / 'decisions.json', decisions)
                raise timeout.TimeoutRecoveryFailure('recovery request hit a token or time limit; fail closed') from error
            if trimming['detected']:
                action, prefix = 'clean_prefix_retry', timeout.reusable(cleaned)
            elif phase == 'primary':
                action, prefix = 'fresh_primary_retry', ''
            elif timeout.primary_eligible(primary):
                row['action'] = 'primary_fallback'
                transport.write_json(ledger / 'decisions.json', decisions)
                result = copy.deepcopy(primary)
                result['metadata']['limit_recovery'] = {'policy': POLICY_ID, 'phase': phase,
                    'action': 'primary_fallback', 'repetition_detected': False, 'evidence': evidence}
                return result
            else:
                row['action'] = 'fail_closed'
                transport.write_json(ledger / 'decisions.json', decisions)
                raise timeout.TimeoutRecoveryFailure('budget forcing hit a limit without a completed eligible primary; fail closed') from error
            row['action'] = action
            transport.write_json(ledger / 'decisions.json', decisions)
            retry = {'policy': POLICY_ID, 'phase': phase, 'action': action,
                     'original_config': asdict(original['config']),
                     'retry_max_tokens': RECOVERY_MAX_TOKENS,
                     'retry_timeout_seconds': RECOVERY_TIMEOUT_SECONDS,
                     'prefix_sha256': timeout.sha(prefix), 'evidence': evidence}
            current = {**original, 'output_dir': ledger / 'retry_1',
                       'config': replace(original['config'], max_tokens=RECOVERY_MAX_TOKENS,
                                         timeout_seconds=RECOVERY_TIMEOUT_SECONDS),
                       'timeout_recovery_prefix': prefix or None}
            Path(current['output_dir']).mkdir(parents=True, exist_ok=False)
            continue
        except Exception as error:
            if attempt == 1:
                transport.write_json(ledger / 'failure.json', {'action': 'fail_closed', 'error': str(error)})
                raise timeout.TimeoutRecoveryFailure('recovery request failed; fail closed') from error
            raise
        if retry is not None:
            try:
                result['metadata']['limit_retry'] = retry
                result['metadata']['limit_recovery'] = retry
                for suffix in ARTIFACT_SUFFIXES:
                    source = Path(current['output_dir']) / (stage + suffix)
                    if source.is_file():
                        shutil.copy2(source, root / source.name)
                for key, suffix in (('system_prompt_path', '.prompt.txt'), ('user_prompt_path', '.user_prompt.txt'),
                                    ('response_path', '.raw_response.json'), ('reasoning_path', '.reasoning.txt')):
                    result['metadata'][key] = str((root / (stage + suffix)).resolve())
                transport.write_json(root / f'{stage}.metadata.json', result['metadata'])
            except Exception as evidence_error:
                raise timeout.TimeoutRecoveryFailure('cannot publish recovered response evidence; fail closed') from evidence_error
        return result
    raise AssertionError('unreachable recovery state')


def cap_matches(config: Any, expected: int, metadata: dict[str, Any]) -> bool:
    if not isinstance(config, dict):
        return False
    retry = metadata.get('limit_retry') or {}
    return config.get('max_tokens') == expected or (
        config.get('max_tokens') == RECOVERY_MAX_TOKENS and retry.get('policy') == POLICY_ID
        and retry.get('original_config', {}).get('max_tokens') == expected)


def timeout_matches(config: dict[str, Any], expected: int, metadata: dict[str, Any]) -> bool:
    retry = metadata.get('limit_retry') or {}
    return config.get('timeout_seconds') == expected or (
        config.get('timeout_seconds') == RECOVERY_TIMEOUT_SECONDS and retry.get('policy') == POLICY_ID
        and retry.get('original_config', {}).get('timeout_seconds') == expected)


def read_evidence(evidence: dict[str, Any], directory: Path) -> dict[str, Any]:
    path = Path(evidence['response_path']).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError('limit evidence escaped generation directory')
    if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['response_sha256']:
        raise ValueError('limit evidence hash changed')
    choice = json.loads(path.read_text())['choices'][0]
    if evidence['trigger'] not in ('length', 'timeout'):
        raise ValueError('unknown limit trigger')
    if evidence['trigger'] == 'length' and choice.get('finish_reason') != 'length':
        raise ValueError('length evidence was not token capped')
    msg = choice['message']
    # Length responses have been normalized by the HTTP transport; timeout deltas have not.
    result = {'text': str(msg.get('content') or ''),
              'reasoning': str(msg.get('reasoning_content') or msg.get('reasoning') or '')}
    return {k: v.strip() for k, v in result.items()} if evidence['trigger'] == 'length' else result


def verify_retry(metadata: dict[str, Any], directory: Path) -> None:
    retry = metadata.get('limit_retry')
    if retry is None:
        return
    if (retry.get('policy') != POLICY_ID or retry.get('phase') not in ('primary', 'budget_forcing')
            or retry.get('retry_max_tokens') != RECOVERY_MAX_TOKENS
            or retry.get('retry_timeout_seconds') != RECOVERY_TIMEOUT_SECONDS):
        raise ValueError('limit retry policy changed')
    expected = {**retry['original_config'], 'max_tokens': RECOVERY_MAX_TOKENS,
                'timeout_seconds': RECOVERY_TIMEOUT_SECONDS}
    if metadata['config'] != expected or retry['evidence']['config'] != retry['original_config']:
        raise ValueError('limit retry sampling or allowance changed')
    cleaned, detail = timeout.clean_timeout_result(read_evidence(retry['evidence'], directory))
    if retry['action'] == 'clean_prefix_retry':
        if not detail['detected'] or timeout.sha(timeout.reusable(cleaned)) != retry['prefix_sha256']:
            raise ValueError('limit retry prefix does not match the repeated output')
    elif retry['action'] == 'fresh_primary_retry':
        if retry['phase'] != 'primary' or detail['detected'] or retry['prefix_sha256'] != timeout.sha(''):
            raise ValueError('fresh primary retry policy changed')
    else:
        raise ValueError('unknown limit retry action')


def policy_manifest() -> dict[str, Any]:
    return {'policy': POLICY_ID, 'models': ['gemma', 'qwen'], 'triggers': ['length', 'timeout'],
            'recovery_max_tokens': RECOVERY_MAX_TOKENS, 'recovery_timeout_seconds': RECOVERY_TIMEOUT_SECONDS,
            'max_recovery_requests_per_physical_request': 1,
            'repetition': 'original_input_plus_clean_prefix',
            'nonrepetition_primary': 'fresh_original_input_only',
            'nonrepetition_budget_forcing': 'completed_valid_primary_else_fail_closed',
            'recovery_hits_either_limit': 'fail_closed_without_retry_or_fallback',
            'seed_and_sampling': 'preserve_original', 'early_live_stopper': False}
