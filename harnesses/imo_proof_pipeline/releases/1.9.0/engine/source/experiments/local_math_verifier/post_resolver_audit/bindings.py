"""Verify harness-owned identities without trusting model-echoed identifiers."""
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_audit_binding(root, task, result, call):
    """Raise on altered proofs, inputs, prompts, or a misbound saved response.

    Model-authored SHA256 fields never participate. These checks validate the
    saved transport record and its harness-generated request metadata.
    """
    root = Path(root)
    evidence = {}

    def require(ok, reason):
        if not ok:
            raise ValueError(reason)

    def bound(path, expected=None):
        path = Path(path)
        data = path.read_bytes()
        actual = digest(data)
        require(expected is None or actual == expected, 'Hash mismatch: ' + str(path))
        evidence[str(path)] = actual
        return data

    cfg = json.loads(bound(root / 'config.json'))
    for name in ('manifest.json', 'audit_plan.json', 'AUDIT_PROMPT.md'):
        require(name in cfg['pins'], 'Missing source pin: ' + name)
        bound(root / name, cfg['pins'][name])
    manifest = json.loads((root / 'manifest.json').read_text())
    plan = json.loads((root / 'audit_plan.json').read_text())
    require(task in plan['audits'], 'Task absent from bound audit plan')
    case = next(c for c in manifest['cases'] if c['case_id'] == task['original_case_id'])
    require(task['changes'] == case['changes'], 'Changed-block binding mismatch')
    for item in (case, task):
        folder = root / 'model_inputs' / item['case_id']
        for name, expected in item['files'].items():
            bound(folder / name, expected)
        for role in ('baseline', 'candidate'):
            require(item[role + '_sha256'] == case[role + '_sha256'] == item['files'][role + '.md'],
                    'Proof role binding mismatch: ' + role)
    prompt = bound(root / 'AUDIT_PROMPT.md', cfg['pins']['AUDIT_PROMPT.md'])
    user_input = bound(root / 'model_inputs' / task['case_id'] / 'audit_input.md', task['input_sha256'])
    binding = digest(json.dumps(task, sort_keys=True).encode() + prompt)
    require(result['binding'] == binding, 'Result request binding mismatch')
    for key in ('case_id', 'original_case_id', 'problem_id', 'model_key', 'order'):
        require(result[key] == task[key], 'Result task identity mismatch: ' + key)
    text_hash = digest(call['text'].encode())
    require(text_hash == call['final_sha256'] == result['audit_sha256'], 'Response content hash mismatch')
    metadata = call['metadata']
    require(metadata['prompt_sha256'] == digest(prompt), 'Transport system prompt mismatch')
    require(metadata['user_prompt_sha256'] == digest(user_input), 'Transport user prompt mismatch')
    require(metadata['model'] == cfg['auditors'][task['model_key']]['model'], 'Transport model mismatch')
    require(bound(metadata['system_prompt_path']) == prompt, 'Saved system prompt mismatch')
    require(bound(metadata['user_prompt_path']) == user_input, 'Saved user prompt mismatch')
    final = bound(call['final_path']).decode()
    # The writer appends an outer newline to the saved final Markdown artifact.
    require(final.strip() == call['text'].strip(), 'Saved final response mismatch')
    bf = metadata.get('v0257_budget_forcing', {})
    if bf.get('canonical_text_sha256'):
        require(bf['canonical_text_sha256'] == text_hash, 'BF canonical response mismatch')
    return {'verified': True, 'binding': binding, 'response_sha256': text_hash,
            'model_hash_echo_used': False, 'source_hashes': evidence}
