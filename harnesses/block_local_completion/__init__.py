"""Isolated raw-proof block repair, followed by one audit/resolve pass."""

VERSION = '0.1.0'
EXPERIMENT = 'block_local_completion_v1'
SCOPE = 'all_saved_raw_proofs'
PIPELINE_CONFIG = {'neighbor_blocks': 1, 'max_audit_passes': 1, 'max_resolve_passes': 1}
ORIGINAL_PIPELINE_CONFIG = {'neighbor_blocks': 0, 'max_audit_passes': 0, 'max_resolve_passes': 0}
TERMINAL_STAGES = {'block': 'block_audit_or_one_resolve', 'original': 'original_lazy_expansion'}


def strategy_config(strategy):
    if strategy == 'block':
        return dict(PIPELINE_CONFIG)
    if strategy == 'original':
        return dict(ORIGINAL_PIPELINE_CONFIG)
    raise ValueError('Unknown repair strategy')
