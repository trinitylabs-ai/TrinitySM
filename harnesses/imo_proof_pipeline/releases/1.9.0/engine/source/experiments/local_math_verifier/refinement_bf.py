"""Frozen Harness B: role-specific refinement cues, original chat BF transport."""
from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from experiments.local_math_verifier import refinement_bf_policy as policy


def manifest():
    return dict(harness_variant='B', policy_id=policy.POLICY_ID,
        bf_mode='original_chat_preserved_reasoning_and_answer',
        role_specific_cues=policy.ROLE_SPECIFIC_CUES,
        cue_sha256={role:hashlib.sha256(cue.encode()).hexdigest() for role,cue in policy.ROLE_SPECIFIC_CUES.items()},
        scope='refinement_1_refinement_2_refinement_3', draft_policy='unchanged',
        auxiliary_policy='original_generic_cue', unknown_routes='fail_closed')


def build_routes(backend):
    """Bind the cue policy to the actual frozen role prompts, including recovery."""
    from experiments.local_math_verifier import refinement_bf_policy as policy
    stage, boundary = backend.stage, backend.repair_boundary
    module = lambda function: sys.modules[function.__module__]
    r1, r2, r3 = (module(stage.run_original_reviewer), module(stage.reviewer_2.run_task),
                  module(stage.reviewer_3.run_task))
    fusion = module(stage.fusion.run_task)
    resolver = module(backend.v263._ORIGINAL_RESOLVER_RUN_TASK)
    gap1, gap3 = module(stage.run_v089_selector), module(stage.run_v092_selector)
    specs = [
        ('reviewer_1', r'original_reviewer1(?:_clean_[0-9]+k_retry_[0-9]+|_protocol_repair)?', r1.ORIGINAL_REVIEWER_SYSTEM_PROMPT),
        ('reviewer_2', r'reviewer2(?:_clean_[0-9]+k_retry_[0-9]+|_protocol_repair)?', r2.SYSTEM_PROMPT),
        ('reviewer_3', r'reviewer3(?:_cap_continuation|_terminal_recovery|_protocol_repair)?', r3.SYSTEM_PROMPT),
        ('fusion', r'fusion(?:_cap_continuation|_terminal_recovery|_protocol_repair|_assessment_constraint_repair)?', fusion.SYSTEM_PROMPT),
        ('resolver', r'resolver(?:_cap_continuation|_protocol_repair)?', resolver.SYSTEM_PROMPT),
        ('acceptance', r'audit_fusion_acceptance_cap_[0-9]+', boundary.ACCEPTANCE_CERTIFIER_SYSTEM_PROMPT),
        ('fusion', r'reconsider_fusion_cap_[0-9]+', stage.fusion.SYSTEM_PROMPT + boundary.FUSION_RECONSIDERATION_SUFFIX),
        ('repair_brief_audit', r'audit_repair_brief_cap_[0-9]+', boundary.brief_stage.CERTIFIER_SYSTEM_PROMPT),
        ('repair_brief_rewrite', r'rewrite_repair_brief_cap_[0-9]+', boundary.brief_stage.REWRITER_SYSTEM_PROMPT),
        ('auxiliary', r'compact_markdown_trace_extraction', r1.COMPACT_MARKDOWN_EXTRACTOR_SYSTEM_PROMPT),
        ('auxiliary', r'gap_selector', gap1.GAP_SELECTOR_SYSTEM_PROMPT),
        ('auxiliary', r'gap_selector_format_retry', gap1.FORMAT_RETRY_SYSTEM_PROMPT),
        ('auxiliary', r'scope_matched_gap_selector', gap3.GAP_SELECTOR_SYSTEM_PROMPT),
        ('auxiliary', r'scope_matched_gap_selector_format_retry', gap3.FORMAT_RETRY_SYSTEM_PROMPT),
    ]
    return tuple(policy.make_route(*spec) for spec in specs)


@contextmanager
def refinement_policy(backend, directory):
    """Install once around every lane in a refinement worker, then restore."""
    directory=Path(directory)
    routes=build_routes(backend)
    directory.mkdir(parents=True,exist_ok=True)
    payload=dict(manifest(),routes=[asdict(route) for route in routes])
    path=directory/'policy.json'
    if path.exists():
        raise FileExistsError('Existing Harness B policy receipt; refusing partial replay')
    path.write_text(json.dumps(payload,indent=2)+'\n')
    with policy.install(backend.v263.parent._budget_forcing,policy.ROLE_SPECIFIC,
                        directory/'continuations.jsonl',routes=routes):
        yield
