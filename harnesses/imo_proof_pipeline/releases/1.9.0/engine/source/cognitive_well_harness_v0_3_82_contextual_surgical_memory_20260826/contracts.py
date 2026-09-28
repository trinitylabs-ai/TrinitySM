from __future__ import annotations

from typing import Any


CONTEXT_CERTIFIED = "context_certified"
PROVISIONAL = "provisional"
MEMORY_TIERS = frozenset({CONTEXT_CERTIFIED, PROVISIONAL})

STRICT_REVIEW_OUTCOMES = {
    "reviewer_1": "NO_FIRST_BREAK",
    "reviewer_2": "NO_ADVERSARIAL_BREAK",
    "reviewer_3": "NO_UNCLOSED_OBLIGATION_FOUND",
}
STRICT_FUSION_OUTCOME = "ACCEPT_AS_WRITTEN"
MAX_CONTEXTUAL_REWRITES = 2


QWEN_REPAIR_SPEC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "decisive_location",
        "verified_failure",
        "preservable_material",
        "required_replacement_chain",
        "lemma_interface_action",
        "lemma_revision_requirement",
        "downstream_reintegration_requirements",
        "forbidden_shortcuts",
    ],
    "properties": {
        "decisive_location": {"type": "string", "minLength": 10},
        "verified_failure": {"type": "string", "minLength": 10},
        "preservable_material": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 3},
        },
        "required_replacement_chain": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 3},
        },
        "lemma_interface_action": {
            "type": "string",
            "enum": [
                "REPAIR_SAME_STATEMENT_IN_CONTEXT",
                "REVISE_STATEMENT_AND_APPLICATION",
                "INLINE_OR_ELIMINATE_LEMMA",
                "NO_SUPPORTED_REPAIR",
            ],
        },
        "lemma_revision_requirement": {"type": "string", "minLength": 10},
        "downstream_reintegration_requirements": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 3},
        },
        "forbidden_shortcuts": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 3},
        },
    },
}


AUDIT_ANCHOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["anchors"],
    "properties": {
        "anchors": {
            "type": "array",
            "minItems": 1,
            "maxItems": 24,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "anchor_id",
                    "exact_quote",
                    "mathematical_claim",
                    "objects_and_declared_domains",
                    "required_prior_facts",
                    "invoked_operation_or_result",
                    "downstream_conclusion",
                ],
                "properties": {
                    "anchor_id": {"type": "string", "minLength": 1},
                    "exact_quote": {"type": "string", "minLength": 3},
                    "mathematical_claim": {"type": "string", "minLength": 3},
                    "objects_and_declared_domains": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                    "required_prior_facts": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                    },
                    "invoked_operation_or_result": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "downstream_conclusion": {"type": "string", "minLength": 1},
                },
            },
        }
    },
}


LITERAL_AUDIT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "verdict",
        "earliest_failed_anchor_id",
        "exact_location",
        "failed_obligation",
        "verification",
    ],
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "LITERAL_FAILURE"]},
        "earliest_failed_anchor_id": {"type": "string"},
        "exact_location": {"type": "string"},
        "failed_obligation": {"type": "string"},
        "verification": {"type": "string", "minLength": 1},
    },
}


MEMORY_DISPOSITION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "decision",
        "supersedes_lemma_ids",
        "statement_exact_quote",
        "proof_exact_quote",
        "earliest_unresolved_transition",
        "local_dependency_map",
        "self_containment_reason",
    ],
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["NO_REUSABLE_LEMMA", "EXACT_SELF_CONTAINED_REVISION"],
        },
        "supersedes_lemma_ids": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "statement_exact_quote": {"type": "string"},
        "proof_exact_quote": {"type": "string"},
        "earliest_unresolved_transition": {"type": "string"},
        "local_dependency_map": {"type": "string"},
        "self_containment_reason": {"type": "string", "minLength": 1},
    },
}

