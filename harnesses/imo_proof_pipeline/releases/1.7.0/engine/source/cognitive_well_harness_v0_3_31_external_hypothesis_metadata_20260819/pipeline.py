from __future__ import annotations

import concurrent.futures
import hashlib
import json
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterator

from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812.core import MODEL
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    pipeline as implementation_pipeline,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    prompts as implementation_prompts,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819 import (
    verification as implementation_verification,
)
from cognitive_well_harness_v0_3_28_two_iteration_terra_appendix_20260819.terra_runtime import (
    terra_json_call,
)
from cognitive_well_harness_v0_3_30_terra_score_backend_20260819 import (
    pipeline as base_pipeline,
)

from .contracts import (
    ARTIFACT_SCHEMA_VERSION,
    HARNESS_VERSION,
    PHASE_ONE_WIDTH,
    PROMOTION_PROFILE,
    SIDE_AUDIT_EXTERNAL_FIELDS,
    SIDE_AUDIT_MODEL_FIELDS,
    TERRA_MODEL,
    validate_promoted_profile,
)


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
SIDE_MATH_SCHEMA = PACKAGE_DIR / "schemas" / "terra_side_math.schema.json"
BASE_PACKAGE = REPO_ROOT / "cognitive_well_harness_v0_3_30_terra_score_backend_20260819"
PINNED_BASE_FILES = (
    "__init__.py",
    "contracts.py",
    "pipeline.py",
    "run.py",
    "schemas/terra_score.schema.json",
)
EXPECTED_BASE_IMPLEMENTATION_SHA256 = (
    "fc0c431593cada4edbbc6499580eeb97a4b35ec5d24b73f8e4db436978cd696c"
)


def base_implementation_sha256() -> str:
    digest = hashlib.sha256()
    for relative in PINNED_BASE_FILES:
        path = BASE_PACKAGE / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned v0.3.30 implementation file: {path}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def assert_frozen_base() -> dict[str, Any]:
    recursive_base = base_pipeline.assert_frozen_base()
    observed = base_implementation_sha256()
    if observed != EXPECTED_BASE_IMPLEMENTATION_SHA256:
        raise RuntimeError(
            "v0.3.31 frozen v0.3.30 implementation changed: "
            f"expected {EXPECTED_BASE_IMPLEMENTATION_SHA256}, observed {observed}"
        )
    return {
        "package": BASE_PACKAGE.name,
        "sha256": observed,
        "files": list(PINNED_BASE_FILES),
        "recursive_base": recursive_base,
        "hypothesis_side_audit_contract": {
            "model_input_metadata": [],
            "externally_bound_metadata": sorted(SIDE_AUDIT_EXTERNAL_FIELDS),
            "model_output_fields": sorted(SIDE_AUDIT_MODEL_FIELDS),
        },
    }


def side_math_audit_prompt(
    *,
    problem: str,
    exact_claim: str,
    proof: str,
    dependency_statements: list[dict[str, Any]],
) -> str:
    """Build the mathematical packet without orchestration metadata."""

    return f"""You are a proof verifier, not a proof author. {implementation_prompts.FIREWALL}

Audit the candidate proof against exactly the supplied claim in isolation. Return
pass only if every load-bearing step is supported and the exact claim is reached.
Locate the earliest break.

PROBLEM:
{problem}

EXACT CLAIM:
{exact_claim}

ALLOWED VERIFIED DEPENDENCY STATEMENTS:
{json.dumps(dependency_statements, ensure_ascii=False)}

CANDIDATE PROOF:
{proof}
"""


def _side_math_validator(result: dict[str, Any]) -> None:
    if set(result) != SIDE_AUDIT_MODEL_FIELDS:
        raise ValueError("Terra side audit returned orchestration or unknown fields")
    if result["external_information_used"] is not False:
        raise ValueError("Terra side audit violated the information firewall")
    if result["verdict"] == "pass" and (
        result["exact_claim_reached"] is not True
        or result["first_break"] is not None
        or result["missing_obligations"]
    ):
        raise ValueError("passing side audit contains a failed criterion")


def bind_side_metadata(
    *, claim_id: str, side: str, audit: dict[str, Any]
) -> dict[str, Any]:
    """Attach deterministic routing metadata after the model call."""

    if side not in {"positive", "negative"}:
        raise ValueError(f"invalid audited side: {side!r}")
    _side_math_validator(audit)
    return {"claim_id": claim_id, "audited_side": side, **audit}


def audit_pair_with_external_metadata(
    *,
    problem: str,
    node: implementation_verification.ClaimNode,
    dependencies: tuple[str, ...],
    memory: list[dict[str, Any]],
    attempts: dict[str, dict[str, Any]],
    call_root: Path,
    terra_model: str,
    mode: str,
) -> dict[str, Any]:
    """Audit both sides while keeping claim identity outside Terra calls."""

    allowed = implementation_verification.dependency_packet(
        dependencies, memory, proofs=False
    )

    def audit(side: str) -> tuple[str, dict[str, Any]]:
        exact_claim = node.statement if side == "positive" else node.exact_negation
        model_audit = terra_json_call(
            prompt=side_math_audit_prompt(
                problem=problem,
                exact_claim=exact_claim,
                proof=attempts[side]["proof"],
                dependency_statements=allowed,
            ),
            schema_path=SIDE_MATH_SCHEMA,
            call_root=call_root / "terra",
            stem=side,
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=_side_math_validator,
        )
        return side, bind_side_metadata(
            claim_id=node.node_id, side=side, audit=model_audit
        )

    audits: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(audit, side) for side in ("positive", "negative")]
        for future in concurrent.futures.as_completed(futures):
            side, result = future.result()
            audits[side] = result

    direction = implementation_verification.direction_from_verdicts(
        audits["positive"]["verdict"], audits["negative"]["verdict"]
    )
    paired = None
    if direction == "conflict":
        paired = terra_json_call(
            prompt=implementation_prompts.paired_prompt(
                problem=problem,
                claim_id=node.node_id,
                positive=node.statement,
                negative=node.exact_negation,
                positive_proof=attempts["positive"]["proof"],
                negative_proof=attempts["negative"]["proof"],
            ),
            schema_path=implementation_verification.PAIRED_SCHEMA,
            call_root=call_root / "terra",
            stem="paired",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=lambda value: implementation_verification._paired_validator(
                value, node
            ),
        )
        direction = implementation_verification.paired_direction(paired)

    result = {
        "node": asdict(node),
        "mode": mode,
        "dependency_ids": list(dependencies),
        "attempts": attempts,
        "audits": audits,
        "paired_audit": paired,
        "final_direction": direction,
    }
    implementation_verification.write_json(call_root / "summary.json", result)
    return result


@contextmanager
def external_metadata_backend(scoring_model: str) -> Iterator[None]:
    """Install v0.3.30 scoring plus metadata-free hypothesis side audits."""

    original_audit_pair = implementation_verification.audit_pair
    implementation_verification.audit_pair = audit_pair_with_external_metadata
    try:
        with base_pipeline.terra_scoring_backend(scoring_model):
            yield
    finally:
        implementation_verification.audit_pair = original_audit_pair


def run_harness(**kwargs: Any) -> dict[str, Any]:
    validate_promoted_profile()
    frozen_base = assert_frozen_base()
    requested_width = int(kwargs.pop("phase_one_width", PHASE_ONE_WIDTH))
    if requested_width != PHASE_ONE_WIDTH:
        raise ValueError("v0.3.31 fixes Phase-1 width at four candidates per route")
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
            "v0.3.31 disallows untyped route reuse; use a typed Phase-1 "
            "continuation from this harness"
        )
    scoring_model = str(kwargs.get("terra_model", TERRA_MODEL))
    output_dir = Path(kwargs["output_dir"])
    with external_metadata_backend(scoring_model):
        result = implementation_pipeline.run_harness(
            **kwargs,
            phase_one_width=PHASE_ONE_WIDTH,
            harness_version=HARNESS_VERSION,
            artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
            promotion_profile=PROMOTION_PROFILE,
            promotion_base=frozen_base,
        )
    base_pipeline.assert_score_only_grade_artifacts(output_dir)
    return result
