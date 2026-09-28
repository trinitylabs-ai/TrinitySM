from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol


USABLE_EVIDENCE_VERDICTS = frozenset(
    {"VERIFIED_SUPPORT", "COUNTEREXAMPLE_FOUND", "EXACT_SOLUTION_SET"}
)


@dataclass(frozen=True)
class TaskInputs:
    problem_id: str
    theorem: str
    source_proof: str
    additional_documents: Mapping[str, str]


@dataclass(frozen=True)
class EvidenceBundle:
    provider_id: str
    verdict: str
    markdown: str
    verification: Mapping[str, Any]
    tool_record: Mapping[str, Any]
    source_artifacts: Mapping[str, Path]
    appendix_markdown: str = ""
    appendix_in_rewriter_prompt: bool = True


class EvidenceProvider(Protocol):
    provider_id: str

    def materialize(self) -> EvidenceBundle:
        """Acquire or replay exact evidence and return a checked readable form."""


@dataclass(frozen=True)
class LiteralRequirement:
    label: str
    alternatives: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.label or not self.alternatives or any(
            not item for item in self.alternatives
        ):
            raise ValueError("literal requirement must have a label and alternatives")


@dataclass(frozen=True)
class SynthesisContract:
    evidence_marker: str
    rewrite_requirements: tuple[str, ...]
    literal_requirements: tuple[LiteralRequirement, ...]
    conclusion_alternatives: tuple[str, ...]
    auditor_focus: str
    max_cycles: int = 3
    semantic_conclusion_only: bool = False

    def __post_init__(self) -> None:
        if not self.evidence_marker.strip() or any(
            character.isspace() for character in self.evidence_marker
        ):
            raise ValueError("evidence marker must be one nonempty token")
        if not self.rewrite_requirements:
            raise ValueError("rewrite requirements cannot be empty")
        if not self.literal_requirements and not self.semantic_conclusion_only:
            raise ValueError("literal requirements cannot be empty")
        if not self.conclusion_alternatives and not self.semantic_conclusion_only:
            raise ValueError("conclusion alternatives cannot be empty")
        if not self.auditor_focus.strip():
            raise ValueError("auditor focus cannot be empty")
        if self.max_cycles < 1:
            raise ValueError("max_cycles must be positive")
        labels = [item.label for item in self.literal_requirements]
        if len(labels) != len(set(labels)):
            raise ValueError("literal requirement labels must be unique")

    def lock_record(self) -> dict[str, Any]:
        return {
            "evidence_marker": self.evidence_marker,
            "rewrite_requirements": list(self.rewrite_requirements),
            "literal_requirements": [
                {"label": row.label, "alternatives": list(row.alternatives)}
                for row in self.literal_requirements
            ],
            "conclusion_alternatives": list(self.conclusion_alternatives),
            "auditor_focus": self.auditor_focus,
            "max_cycles": self.max_cycles,
            "semantic_conclusion_only": self.semantic_conclusion_only,
        }


@dataclass(frozen=True)
class SynthesisAdapter:
    adapter_id: str
    task: TaskInputs
    evidence_provider: EvidenceProvider
    contract: SynthesisContract

    def __post_init__(self) -> None:
        if not self.adapter_id.strip():
            raise ValueError("adapter_id cannot be empty")
        if not self.task.problem_id.strip():
            raise ValueError("problem_id cannot be empty")
        if not self.task.theorem.strip() or not self.task.source_proof.strip():
            raise ValueError("theorem and source proof cannot be empty")
