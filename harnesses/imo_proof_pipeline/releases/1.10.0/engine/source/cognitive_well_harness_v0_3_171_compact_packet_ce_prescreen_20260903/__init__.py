"""Compact packet-level counterexample prescreen for v0167 NH inputs."""

from .pipeline import apply_packet_decisions, run_case_prescreen
from .protocol import (
    parse_attack_line,
    parse_audit_line,
    parse_decision_tsv,
    render_decision_tsv,
    resolve_packet_decision,
)

__all__ = [
    "apply_packet_decisions",
    "parse_attack_line",
    "parse_audit_line",
    "parse_decision_tsv",
    "render_decision_tsv",
    "resolve_packet_decision",
    "run_case_prescreen",
]
