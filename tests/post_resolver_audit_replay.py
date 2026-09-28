"""Scripted audit transport with real request/response binding artifacts."""
import hashlib
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def response(kwargs, decision='ACCEPT_CANDIDATE', invalid=False):
    folder = Path(kwargs['output_dir'])
    root = next(parent for parent in folder.parents if (parent / 'audit_plan.json').is_file())
    task_id = next(parent.name for parent in folder.parents if parent.parent.name == 'cases')
    task = next(t for t in json.loads((root / 'audit_plan.json').read_text())['audits'] if t['case_id'] == task_id)
    changes = ''.join(f"\n### {c['id']}\nStatus: VERIFIED\nThe changed implication follows from the explicitly written computation.\n" for c in task['changes'])
    text = f'''# Replacement Audit
Decision: {decision}
Baseline SHA256: intentionally not authoritative
Candidate SHA256: intentionally not authoritative

## Target obligation
Status: CLOSED
The stated obligation is discharged by the supplied derivation.

## Changed dependencies
{changes}
## Preserved valid progress
Status: PRESERVED
The preliminary identities remain available in the candidate.

## Theorem actually established
Status: SAME_SCOPE
The original domain and all quantifiers are preserved explicitly.

## Qualifications and supplied repairs
Status: {'REQUIRED' if invalid else 'NONE'}
{'A missing lemma still needs a substantive proof.' if invalid else ''}

## Decision basis
The checks above determine the replacement decision.
'''
    system, user = folder / 'system.md', folder / 'user.md'
    system.write_text(kwargs['system_prompt']); user.write_text(kwargs['user_prompt'])
    final = folder / 'final.md'; final.write_text(text + '\n')
    metadata = {'model': kwargs['model'], 'prompt_sha256': sha(system.read_bytes()),
                'user_prompt_sha256': sha(user.read_bytes()), 'system_prompt_path': str(system),
                'user_prompt_path': str(user), 'config': {'temperature': kwargs['temperature']}}
    return {'text': text, 'final_path': str(final), 'final_sha256': sha(text.encode()), 'metadata': metadata}
