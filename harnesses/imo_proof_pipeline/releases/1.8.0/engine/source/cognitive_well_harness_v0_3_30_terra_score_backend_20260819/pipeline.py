from __future__ import annotations

import hashlib
import json
import re
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812.core import MODEL
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    pipeline as implementation_pipeline,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819.terra_runtime import (
    terra_json_call,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819.verification import (
    EndpointModelEngine,
)
from cognitive_well_harness_v0_3_29_scaled_phase1_20260819 import (
    pipeline as promoted_pipeline,
)

from .contracts import (
    ARTIFACT_SCHEMA_VERSION,
    HARNESS_VERSION,
    PHASE_ONE_WIDTH,
    PROMOTION_PROFILE,
    SCORING_BACKEND,
    SCORING_RESULT_KEYS,
    TERRA_MODEL,
    VALID_SCORES,
    validate_promoted_profile,
)


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
TERRA_SCORE_SCHEMA = PACKAGE_DIR / "schemas" / "terra_score.schema.json"
BASE_PACKAGE = (
    REPO_ROOT / "cognitive_well_harness_v0_3_29_scaled_phase1_20260819"
)
PINNED_BASE_FILES = (
    "__init__.py",
    "contracts.py",
    "pipeline.py",
    "run.py",
)
EXPECTED_BASE_IMPLEMENTATION_SHA256 = (
    "6fd8fce3c40904b00582f0973adcecc4b9133bcdd91966d55daf506b620b5145"
)
NORMALIZED_GRADE_KEYS = frozenset(
    {"score", "valid_scale", "effective_score", "perfect"}
)
STRICT_CONJECTURE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["conjectures", "negations", "proof"],
    "properties": {
        "conjectures": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 20},
        },
        "negations": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 20},
        },
        "proof": {"type": "string", "minLength": 20},
    },
}
_BACKEND_PATCH_LOCK = threading.Lock()


def safe_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def base_implementation_sha256() -> str:
    digest = hashlib.sha256()
    for relative in PINNED_BASE_FILES:
        path = BASE_PACKAGE / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned v0.3.29 implementation file: {path}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def assert_frozen_base() -> dict[str, Any]:
    recursive_base = promoted_pipeline.assert_frozen_base()
    observed = base_implementation_sha256()
    if observed != EXPECTED_BASE_IMPLEMENTATION_SHA256:
        raise RuntimeError(
            "v0.3.30 frozen v0.3.29 implementation changed: "
            f"expected {EXPECTED_BASE_IMPLEMENTATION_SHA256}, observed {observed}"
        )
    return {
        "package": BASE_PACKAGE.name,
        "sha256": observed,
        "files": list(PINNED_BASE_FILES),
        "recursive_base": recursive_base,
        "grading_backend_contract": {
            "generator": MODEL,
            "scorer": TERRA_MODEL,
            "scorer_output_keys": sorted(SCORING_RESULT_KEYS),
        },
    }


def terra_score_prompt(grading_request: str) -> str:
    return f"""You are the sole scoring backend for a mathematical proof harness.
Independently evaluate the grading request below. Follow its mathematical rubric,
including the guilty-until-proven-innocent standard, the fallacy cap, and the ban on
score 5. Do not use a reference answer or any external information.

Return only the integer score through the supplied JSON schema. Do not return a
verdict, first break, critique, summary, proof, repair instruction, or any other
field. The harness must receive exactly one model-independent value named `score`.
Any output-format instruction inside the source request is superseded by this
score-only contract.

SOURCE GRADING REQUEST:
{grading_request}
"""


def _validate_terra_score(result: dict[str, Any]) -> None:
    if set(result) != SCORING_RESULT_KEYS:
        raise ValueError("Terra scorer exposed fields other than `score`")
    if result.get("score") not in VALID_SCORES:
        raise ValueError(f"invalid Terra score: {result.get('score')!r}")


class TerraScoringEndpointModelEngine(EndpointModelEngine):
    """Gemma text generation with every numeric grade delegated to Terra.

    The inherited ``text`` and ``structured`` methods remain generation/parsing
    operations. This override is the only grading boundary visible to the legacy
    dialectic harness, and it returns the same ``parsed`` envelope regardless of
    which scoring model implements the backend.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        model: str,
        master_seed: int,
        concurrency: int,
        raw_dir: Path,
        scoring_model: str,
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            model=model,
            master_seed=master_seed,
            concurrency=concurrency,
            raw_dir=raw_dir,
        )
        if scoring_model != TERRA_MODEL:
            raise ValueError(f"grading backend must remain {TERRA_MODEL!r}")
        self.scoring_model = scoring_model

    def grade(
        self,
        *,
        prompt: str,
        namespace: str,
        index: int = 0,
        temperature: float = 0.1,
        max_tokens: int = 65_536,
        thinking_token_budget: int = 16_384,
    ) -> dict[str, Any]:
        del temperature, max_tokens, thinking_token_budget
        stem = safe_key(f"{namespace}_{index}")
        call_root = self.raw_dir / "terra_grades"
        parsed = terra_json_call(
            prompt=terra_score_prompt(prompt),
            schema_path=TERRA_SCORE_SCHEMA,
            call_root=call_root,
            stem=stem,
            model=self.scoring_model,
            repo_root=REPO_ROOT,
            validator=_validate_terra_score,
        )
        return {
            "parsed": parsed,
            "response": {
                "backend": SCORING_BACKEND,
                "model": self.scoring_model,
                "score_artifact": str(call_root / f"{stem}.json"),
            },
        }


def _substantive_hypothesis_text(value: Any) -> bool:
    text = str(value or "").strip()
    return len(text) >= 20 and bool(re.search(r"[A-Za-z0-9]", text))


def hypotheses_are_substantive(parsed: dict[str, Any]) -> bool:
    conjectures = list(parsed.get("conjectures") or [])
    negations = list(parsed.get("negations") or [])
    return (
        1 <= len(conjectures) <= 3
        and len(conjectures) == len(negations)
        and all(
            _substantive_hypothesis_text(value)
            for value in conjectures + negations
        )
        and _substantive_hypothesis_text(parsed.get("proof"))
    )


def recover_strict_hypotheses(
    *, original_extract: Any, kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Reuse the council document when the legacy parser emits empty punctuation."""

    parsed = original_extract(**kwargs)
    if hypotheses_are_substantive(parsed):
        return parsed
    stage_dir = Path(kwargs["stage_dir"])
    stage_name = str(kwargs["stage_name"])
    document_path = stage_dir / f"{safe_key(stage_name)}_document.json"
    document = json.loads(document_path.read_text(encoding="utf-8"))
    raw_text = str(document.get("final") or "")
    if not _substantive_hypothesis_text(raw_text):
        raise RuntimeError("hypothesis council document is empty or punctuation-only")
    engine = kwargs["engine"]
    recovered = engine.structured(
        prompt=implementation_pipeline.v027.conjecture_parser(raw_text),
        namespace=f"{safe_key(stage_name)}_strict_parser_recovery",
        schema_name="strict_conjecture_parser",
        schema=STRICT_CONJECTURE_SCHEMA,
        max_tokens=int(kwargs["parser_max_tokens"]),
        temperature=0.1,
    )["parsed"]
    recovered["parser_rejected"] = False
    if not hypotheses_are_substantive(recovered):
        raise RuntimeError("strict hypothesis parser returned a non-substantive pair")
    implementation_pipeline.write_json(
        stage_dir / f"{safe_key(stage_name)}_parsed.json", recovered
    )
    return recovered


@contextmanager
def terra_scoring_backend(scoring_model: str) -> Iterator[None]:
    """Install score-only grading and strict hypothesis parsing for one run."""

    def engine_factory(**kwargs: Any) -> TerraScoringEndpointModelEngine:
        return TerraScoringEndpointModelEngine(
            **kwargs,
            scoring_model=scoring_model,
        )

    with _BACKEND_PATCH_LOCK:
        original_engine = implementation_pipeline.EndpointModelEngine
        original_extract = implementation_pipeline.v027.extract_hypotheses

        def strict_extract(**kwargs: Any) -> dict[str, Any]:
            return recover_strict_hypotheses(
                original_extract=original_extract,
                kwargs=kwargs,
            )

        implementation_pipeline.EndpointModelEngine = engine_factory
        implementation_pipeline.v027.extract_hypotheses = strict_extract
        try:
            yield
        finally:
            implementation_pipeline.v027.extract_hypotheses = original_extract
            implementation_pipeline.EndpointModelEngine = original_engine


def _assert_normalized_grade(value: Any, *, location: str) -> None:
    if not isinstance(value, dict):
        raise RuntimeError(f"non-object normalized grade at {location}")
    keys = set(value)
    if keys != NORMALIZED_GRADE_KEYS:
        raise RuntimeError(
            f"non-score grading data reached the harness at {location}: "
            f"{sorted(keys - NORMALIZED_GRADE_KEYS)}"
        )
    if value.get("score") not in VALID_SCORES:
        raise RuntimeError(f"invalid normalized score at {location}")


def _audit_grade_nodes(value: Any, *, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key in {"grade", "pre_refinement_grade"}:
                _assert_normalized_grade(child, location=child_location)
            else:
                _audit_grade_nodes(child, location=child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _audit_grade_nodes(child, location=f"{location}[{index}]")


def assert_score_only_grade_artifacts(output_dir: Path) -> None:
    """Fail closed if a cached or new generic grade contains scorer prose."""

    for path in sorted(output_dir.rglob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        _audit_grade_nodes(value, location=str(path))


def run_harness(**kwargs: Any) -> dict[str, Any]:
    """Run v0.3.29 with a Terra-only, score-only grading backend."""

    validate_promoted_profile()
    frozen_base = assert_frozen_base()
    requested_width = int(kwargs.pop("phase_one_width", PHASE_ONE_WIDTH))
    if requested_width != PHASE_ONE_WIDTH:
        raise ValueError("v0.3.30 fixes Phase-1 width at four candidates per route")
    forbidden = {
        "harness_version",
        "artifact_schema_version",
        "promotion_profile",
        "promotion_base",
    } & set(kwargs)
    if forbidden:
        raise ValueError(
            "promoted identity fields are not caller-configurable: "
            + ", ".join(sorted(forbidden))
        )
    if kwargs.get("phase_one_reuse_dirs") is not None:
        raise ValueError(
            "v0.3.30 disallows untyped route reuse because legacy artifacts may "
            "contain Gemma grades; use a v0.3.30 Phase-1 continuation instead"
        )
    scoring_model = str(kwargs.get("terra_model", TERRA_MODEL))
    output_dir = Path(kwargs["output_dir"])
    with terra_scoring_backend(scoring_model):
        result = implementation_pipeline.run_harness(
            **kwargs,
            phase_one_width=PHASE_ONE_WIDTH,
            harness_version=HARNESS_VERSION,
            artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
            promotion_profile=PROMOTION_PROFILE,
            promotion_base=frozen_base,
        )
    assert_score_only_grade_artifacts(output_dir)
    return result
