"""Typed, deterministic tool support for the selective math harness.

The package intentionally exposes mathematical operations rather than an
arbitrary Python or shell execution interface.
"""

from .executor import ToolExecutor
from .policy import route_problem
from .registry import CapabilityRegistry, default_registry
from .schemas import (
    EvidenceStatus,
    RouteDecision,
    ToolSchemaError,
    operation_hash,
    validate_claim,
    validate_evidence,
    validate_route_decision,
    validate_tool_plan,
)

__all__ = [
    "CapabilityRegistry",
    "EvidenceStatus",
    "RouteDecision",
    "ToolExecutor",
    "ToolSchemaError",
    "default_registry",
    "operation_hash",
    "route_problem",
    "validate_claim",
    "validate_evidence",
    "validate_route_decision",
    "validate_tool_plan",
]
