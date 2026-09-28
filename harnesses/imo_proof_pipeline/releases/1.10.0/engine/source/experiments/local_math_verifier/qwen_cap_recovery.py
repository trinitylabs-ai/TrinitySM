"""Bounded Qwen token-cap recovery, with evidence for every accepted exception."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

POLICY_ID = 'qwen-cap-65536-prefix-or-primary-v1'
INITIAL_MAX_TOKENS = 49_152
RECOVERY_MAX_TOKENS = 65_536
FALLBACK_SOURCE = 'pre_budget_forcing_token_cap_fallback'


def is_qwen(model: str) -> bool:
    return 'qwen' in model.casefold()


class TokenCapReached(RuntimeError):
    def __init__(self, result: dict[str, Any], evidence: dict[str, Any]):
        super().__init__('Qwen reached its output-token cap')
        self.partial, self.evidence = result, evidence


def capped(result: dict[str, Any], directory: Path, stage: str, phase: str) -> TokenCapReached:
    source = directory / f'{stage}.raw_response.json'
    saved = directory / f'{stage}.token_cap.{phase}.partial.json'
    shutil.copy2(source, saved)
    evidence = {'policy': POLICY_ID, 'state': 'length', 'response_path': str(saved.resolve()),
                'response_sha256': hashlib.sha256(saved.read_bytes()).hexdigest(),
                'max_tokens': result['metadata']['config']['max_tokens']}
    return TokenCapReached(result, evidence)


def cap_matches(config: Any, expected: int, metadata: dict[str, Any]) -> bool:
    if not isinstance(config, dict):
        return False
    if config.get('max_tokens') == expected:
        return True
    retry = metadata.get('qwen_cap_retry') or {}
    return (is_qwen(str(metadata.get('model') or ''))
            and config.get('max_tokens') == RECOVERY_MAX_TOKENS
            and retry.get('policy') == POLICY_ID
            and retry.get('original_max_tokens') == expected
            and retry.get('retry_max_tokens') == RECOVERY_MAX_TOKENS)


def read_evidence(evidence: dict[str, Any], directory: Path) -> dict[str, Any]:
    path = Path(evidence['response_path']).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError('Qwen cap evidence escaped generation directory')
    if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['response_sha256']:
        raise ValueError('Qwen cap evidence hash changed')
    raw = json.loads(path.read_text())
    choice = raw['choices'][0]
    if choice.get('finish_reason') != 'length':
        raise ValueError('Qwen cap evidence was not length-stopped')
    msg = choice['message']
    return {'text': str(msg.get('content') or '').strip(),
            'reasoning': str(msg.get('reasoning_content') or msg.get('reasoning') or '').strip()}


def verify_retry(metadata: dict[str, Any], directory: Path) -> None:
    from .timeout_recovery import clean_timeout_result, reusable, sha
    retry = metadata.get('qwen_cap_retry')
    if retry is None:
        return
    if (not is_qwen(str(metadata.get('model') or '')) or retry.get('policy') != POLICY_ID
            or retry.get('retry_max_tokens') != RECOVERY_MAX_TOKENS
            or metadata['config']['max_tokens'] != RECOVERY_MAX_TOKENS):
        raise ValueError('Qwen cap retry policy changed')
    evidence = retry['cap_evidence']
    if evidence['max_tokens'] != retry['original_max_tokens']:
        raise ValueError('Qwen cap retry original allowance changed')
    cleaned, detail = clean_timeout_result(read_evidence(evidence, directory))
    if not detail['detected'] or sha(reusable(cleaned)) != retry['prefix_sha256']:
        raise ValueError('Qwen cap retry prefix does not match the repeated output')


def policy_manifest() -> dict[str, Any]:
    return {'policy': POLICY_ID, 'initial_max_tokens': INITIAL_MAX_TOKENS,
            'recovery_max_tokens': RECOVERY_MAX_TOKENS, 'trigger': 'finish_reason=length',
            'max_repetition_retries': 1, 'shared_with_timeout_retries': True,
            'repetition_action': 'original_input_plus_clean_prefix',
            'no_repetition_action': 'completed_pre_budget_forcing_response_subject_to_stage_validation',
            'otherwise': 'fail_closed', 'wall_timeout_seconds': 600}
