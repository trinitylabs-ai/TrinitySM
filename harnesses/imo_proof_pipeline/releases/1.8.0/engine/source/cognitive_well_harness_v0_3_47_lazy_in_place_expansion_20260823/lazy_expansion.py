from __future__ import annotations

import copy
import hashlib
import json
import re
import threading
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_35_cap_continuation_recovery_20260822 import (
    pipeline as v035_pipeline,
)

from .contracts import LAZY_RESOLVE_TEMPERATURE
from .numeric_classification import numeric_classification_equivalence


PACKAGE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = PACKAGE_DIR / "prompts/lazy_in_place_proof_expansion_v1_20260823.md"
EXPECTED_PROMPT_SHA256 = (
    "205d804d5572c9b0b5ee756e29ba949a6e7754036d21b6fd8109cf4ccd50cc52"
)
AUDIT_BEGIN = "BEGIN_REPAIR_AUDIT"
AUDIT_END = "END_REPAIR_AUDIT"
PROOF_BEGIN = "BEGIN_REPAIRED_PROOF"
PROOF_END = "END_REPAIRED_PROOF"
ALLOWED_CHANGE_BASES = {"CONCRETE_COUNTEREXAMPLE", "RIGOROUS_DERIVATION"}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def prompt_sha256() -> str:
    return sha256_text(PROMPT_PATH.read_text(encoding="utf-8"))


def assert_frozen_prompt() -> str:
    observed = prompt_sha256()
    if observed != EXPECTED_PROMPT_SHA256:
        raise RuntimeError(
            "lazy in-place expansion prompt changed: "
            f"expected {EXPECTED_PROMPT_SHA256}, observed {observed}"
        )
    return observed


def lazy_in_place_expansion_prompt(
    *, problem: str, current_proof: str, local_gaps: str
) -> str:
    assert_frozen_prompt()
    values = {
        "{{PROBLEM}}": problem.strip(),
        "{{CURRENT_PROOF}}": current_proof.strip(),
        "{{LOCAL_GAPS}}": local_gaps.strip(),
    }
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    for marker, value in values.items():
        if prompt.count(marker) != 1:
            raise RuntimeError(f"prompt marker is missing or ambiguous: {marker}")
        prompt = prompt.replace(marker, value)
    return prompt


def _audit_field(audit: str, name: str, *, multiline: bool = False) -> str:
    if multiline:
        pattern = rf"(?ms)^{re.escape(name)}:\s*(.*)\Z"
    else:
        pattern = rf"(?m)^{re.escape(name)}:\s*(.+?)\s*$"
    matches = re.findall(pattern, audit)
    if len(matches) != 1:
        raise ValueError(f"repair envelope must contain exactly one {name} field")
    return str(matches[0]).strip()


def _normalized_classification(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def parse_lazy_expansion_output(raw: str) -> dict[str, Any]:
    text = raw.strip()
    for marker in (AUDIT_BEGIN, AUDIT_END, PROOF_BEGIN, PROOF_END):
        if text.count(marker) != 1:
            raise ValueError(f"repair envelope must contain exactly one {marker}")
    audit_begin = text.index(AUDIT_BEGIN) + len(AUDIT_BEGIN)
    audit_end = text.index(AUDIT_END)
    proof_begin = text.index(PROOF_BEGIN) + len(PROOF_BEGIN)
    proof_end = text.index(PROOF_END)
    if not (audit_begin < audit_end < proof_begin < proof_end):
        raise ValueError("repair envelope sections are out of order")
    if text[: text.index(AUDIT_BEGIN)].strip() or text[proof_end + len(PROOF_END) :].strip():
        raise ValueError("repair envelope contains text outside its required markers")

    audit = text[audit_begin:audit_end].strip()
    proof = text[proof_begin:proof_end].strip()
    if not proof:
        raise ValueError("repaired proof is empty")
    action = _audit_field(audit, "CONCLUSION_ACTION").upper()
    original = _audit_field(audit, "ORIGINAL_CLASSIFICATION")
    repaired = _audit_field(audit, "REPAIRED_CLASSIFICATION")
    basis = _audit_field(audit, "CHANGE_BASIS").upper()
    justification = _audit_field(audit, "CHANGE_JUSTIFICATION", multiline=True)
    if action not in {"PRESERVE", "CHANGE"}:
        raise ValueError(f"invalid CONCLUSION_ACTION: {action!r}")

    same = _normalized_classification(original) == _normalized_classification(repaired)
    equivalence = None
    if not same:
        equivalence = numeric_classification_equivalence(original, repaired)
        same = equivalence is not None
    if action == "PRESERVE":
        if not same:
            raise ValueError(
                "PRESERVE requires identical normalized original and repaired classifications"
            )
        if basis != "NONE":
            raise ValueError("PRESERVE requires CHANGE_BASIS: NONE")
        if justification.upper() != "NONE":
            raise ValueError("PRESERVE requires CHANGE_JUSTIFICATION: NONE")
    else:
        if same:
            raise ValueError("CHANGE requires distinct original and repaired classifications")
        if basis not in ALLOWED_CHANGE_BASES:
            raise ValueError(
                "CHANGE requires CONCRETE_COUNTEREXAMPLE or RIGOROUS_DERIVATION"
            )
        if justification.upper() == "NONE" or len(justification.split()) < 8:
            raise ValueError("CHANGE requires a substantive explicit justification")

    return {
        "valid": True,
        "conclusion_action": action,
        "original_classification": original,
        "repaired_classification": repaired,
        "change_basis": basis,
        "change_justification": justification,
        "proof": proof,
        "raw_sha256": sha256_text(text),
        **({"classification_equivalence": equivalence} if equivalence is not None else {}),
    }


class LazyInPlaceExpansionEngine:
    """Intercept only v0.3.35's lazy re-solve and turn it into local editing."""

    def __init__(
        self,
        *,
        engine: Any,
        problem: str,
        stage_dir: Path,
        stage_name: str,
    ) -> None:
        self._engine = engine
        self._problem = problem
        self._stage_dir = stage_dir
        self._stage_name = stage_name
        self._lock = threading.Lock()
        self._proofs: dict[int, str] = {}
        self._reports: dict[int, str] = {}
        self._load_cached_inputs()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._engine, name)

    def _load_cached_inputs(self) -> None:
        for filename, target, field in (
            ("drafts.json", self._proofs, "proof"),
            ("lazy_checks.json", self._reports, "report"),
        ):
            path = self._stage_dir / filename
            if not path.is_file():
                continue
            rows = json.loads(path.read_text(encoding="utf-8"))
            for row in rows:
                target[int(row["index"])] = str(row[field])

    def _remember(self, target: dict[int, str], index: int, value: str) -> None:
        with self._lock:
            target[index] = value

    def _lookup(self, target: dict[int, str], index: int, label: str) -> str:
        with self._lock:
            value = target.get(index)
        if value is None:
            self._load_cached_inputs()
            with self._lock:
                value = target.get(index)
        if value is None:
            raise RuntimeError(f"missing cached {label} for lazy expansion index {index}")
        return value

    def _write_artifact(
        self,
        *,
        index: int,
        current_proof: str,
        raw_output: str,
        parsed: dict[str, Any] | None,
        error: str | None,
        live_proof: str,
    ) -> None:
        output_dir = self._stage_dir / "lazy_in_place_expansion" / f"candidate_{index + 1}"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "ancestor_proof.md").write_text(
            current_proof.rstrip() + "\n", encoding="utf-8"
        )
        (output_dir / "raw_response.md").write_text(
            raw_output.rstrip() + "\n", encoding="utf-8"
        )
        candidates = [
            {
                "candidate_id": f"{self._stage_name}.s{index + 1}.lazy_ancestor",
                "variant": "ancestor",
                "proof_sha256": sha256_text(current_proof),
                "proof_path": str((output_dir / "ancestor_proof.md").resolve()),
            }
        ]
        if parsed is not None:
            (output_dir / "expanded_proof.md").write_text(
                str(parsed["proof"]).rstrip() + "\n", encoding="utf-8"
            )
            if parsed["conclusion_action"] == "CHANGE":
                candidates.append(
                    {
                        "candidate_id": (
                            f"{self._stage_name}.s{index + 1}.lazy_changed_descendant"
                        ),
                        "variant": "changed_descendant",
                        "proof_sha256": sha256_text(str(parsed["proof"])),
                        "proof_path": str((output_dir / "expanded_proof.md").resolve()),
                    }
                )
        v035_pipeline.implementation_pipeline.write_json(
            output_dir / "audit.json",
            {
                "schema": "cognitive-well-v047-lazy-expansion-audit-v1",
                "prompt_sha256": EXPECTED_PROMPT_SHA256,
                "temperature": LAZY_RESOLVE_TEMPERATURE,
                "accepted": parsed is not None,
                "protocol_error": error,
                "conclusion_action": (
                    parsed["conclusion_action"] if parsed is not None else None
                ),
                "original_classification": (
                    parsed["original_classification"] if parsed is not None else None
                ),
                "repaired_classification": (
                    parsed["repaired_classification"] if parsed is not None else None
                ),
                "change_basis": parsed["change_basis"] if parsed is not None else None,
                "change_justification": (
                    parsed["change_justification"] if parsed is not None else None
                ),
                "live_proof_sha256": sha256_text(live_proof),
                "change_candidates": (
                    candidates
                    if parsed is not None and parsed["conclusion_action"] == "CHANGE"
                    else []
                ),
                "ancestor_provenance": candidates[0],
            },
        )

    def text(self, **kwargs: Any) -> dict[str, Any]:
        namespace = str(kwargs.get("namespace") or "")
        index = int(kwargs.get("index", 0))
        if namespace.endswith("_draft"):
            response = self._engine.text(**kwargs)
            self._remember(self._proofs, index, str(response["final"]))
            return response
        if namespace.endswith("_lazy"):
            response = self._engine.text(**kwargs)
            self._remember(self._reports, index, str(response["final"]).strip())
            return response
        if not namespace.endswith("_explicit_resolve"):
            return self._engine.text(**kwargs)

        current_proof = self._lookup(self._proofs, index, "current proof")
        local_gaps = self._lookup(self._reports, index, "lazy report")
        call_kwargs = dict(kwargs)
        call_kwargs["prompt"] = lazy_in_place_expansion_prompt(
            problem=self._problem,
            current_proof=current_proof,
            local_gaps=local_gaps,
        )
        call_kwargs["temperature"] = LAZY_RESOLVE_TEMPERATURE
        response = self._engine.text(**call_kwargs)
        raw_output = str(response["final"])
        parsed: dict[str, Any] | None
        error: str | None
        try:
            parsed = parse_lazy_expansion_output(raw_output)
        except ValueError as exc:
            parsed = None
            error = f"{type(exc).__name__}: {exc}"
            live_proof = current_proof
        else:
            error = None
            live_proof = str(parsed["proof"])
        self._write_artifact(
            index=index,
            current_proof=current_proof,
            raw_output=raw_output,
            parsed=parsed,
            error=error,
            live_proof=live_proof,
        )
        rewritten = copy.deepcopy(response)
        rewritten["final"] = live_proof
        rewritten["lazy_in_place_expansion"] = {
            "accepted": parsed is not None,
            "protocol_error": error,
            "conclusion_action": (
                parsed["conclusion_action"] if parsed is not None else None
            ),
            "temperature": LAZY_RESOLVE_TEMPERATURE,
            "raw_output_sha256": sha256_text(raw_output),
            "live_proof_sha256": sha256_text(live_proof),
        }
        return rewritten
