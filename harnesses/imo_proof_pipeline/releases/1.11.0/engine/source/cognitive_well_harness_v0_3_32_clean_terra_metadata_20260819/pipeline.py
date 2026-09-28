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
    pipeline as score_backend_pipeline,
)
from cognitive_well_harness_v0_3_31_external_hypothesis_metadata_20260819 import (
    pipeline as previous_pipeline,
)

from .contracts import (
    ARTIFACT_SCHEMA_VERSION,
    HARNESS_VERSION,
    PHASE_ONE_FINALIST_COUNT,
    PHASE_ONE_ROUTE_COUNT,
    PHASE_ONE_WIDTH,
    PROMOTION_PROFILE,
    TERRA_MODEL,
    validate_promoted_profile,
)


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
PAIRED_MATH_SCHEMA = PACKAGE_DIR / "schemas" / "terra_paired_math.schema.json"
EXACT_NEGATION_MATH_SCHEMA = (
    PACKAGE_DIR / "schemas" / "terra_exact_negation_math.schema.json"
)
CHILD_MATH_SCHEMA = PACKAGE_DIR / "schemas" / "terra_child_math.schema.json"
PHASE_ONE_DIVERSITY_INDEX_SCHEMA = (
    PACKAGE_DIR / "schemas" / "terra_phase_one_diversity_index.schema.json"
)
BASE_PACKAGE = (
    REPO_ROOT / "cognitive_well_harness_v0_3_31_external_hypothesis_metadata_20260819"
)
PINNED_BASE_FILES = (
    "__init__.py",
    "contracts.py",
    "pipeline.py",
    "run.py",
    "schemas/terra_side_math.schema.json",
)
EXPECTED_BASE_IMPLEMENTATION_SHA256 = (
    "5284a2bd11701a9fb8eb0a156783af6ad01c37082c46debc95bb1ae4eaea0e36"
)

PAIRED_MODEL_FIELDS = frozenset(
    {
        "claims_are_exact_negations",
        "positive_proof_relation",
        "negative_proof_relation",
        "first_inconsistency",
        "external_information_used",
    }
)
EXACT_NEGATION_MODEL_FIELDS = frozenset(
    {"exact_negation_valid", "first_issue", "external_information_used"}
)
CHILD_MODEL_FIELDS = frozenset(
    {
        "aligned_with_first_break",
        "load_bearing_for_parent_route",
        "strictly_narrower_than_parent",
        "independently_checkable",
        "exact_negation_valid",
        "verdict",
        "first_issue",
        "external_information_used",
    }
)


def base_implementation_sha256() -> str:
    digest = hashlib.sha256()
    for relative in PINNED_BASE_FILES:
        path = BASE_PACKAGE / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned v0.3.31 implementation file: {path}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def assert_frozen_base() -> dict[str, Any]:
    recursive_base = previous_pipeline.assert_frozen_base()
    observed = base_implementation_sha256()
    if observed != EXPECTED_BASE_IMPLEMENTATION_SHA256:
        raise RuntimeError(
            "v0.3.32 frozen v0.3.31 implementation changed: "
            f"expected {EXPECTED_BASE_IMPLEMENTATION_SHA256}, observed {observed}"
        )
    return {
        "package": BASE_PACKAGE.name,
        "sha256": observed,
        "files": list(PINNED_BASE_FILES),
        "recursive_base": recursive_base,
        "terra_routing_metadata_policy": {
            "phase_one_score_candidate_id": "external",
            "phase_one_selection_handles": "temporary_zero_based_indices",
            "phase_one_route_provenance": "not_model_visible",
            "paired_claim_id": "external",
            "exact_negation_claim_id": "external",
            "child_parent_and_obligation_ids": "external",
            "child_dependency_permission": "python_deterministic",
        },
    }


def phase_one_score_math_prompt(*, problem: str, proof: str) -> str:
    return f"""You are an independent olympiad proof scorer. {implementation_prompts.FIREWALL}

Score this one proof from scratch. You are not given and must not infer any
generator score or ranking, and you must not compare it with another proof.
Check the claimed answer, necessity, sufficiency, domains, case coverage, and
every load-bearing inference.

Separately assess its value as a seed for later hypothesis extraction. Credit
only mathematically coherent root characterizations, invariants, constructions,
or obstruction claims; do not reward an idea merely because the proof labels
it as a lemma. The hypothesis-seed assessment does not repair the proof and
does not increase its 0-7 correctness score. Use hypothesis_seed_value 0 when
there is no sound load-bearing structure, 1 for weak structure, 2 for a useful
partially sound idea, and 3 only when the root characterization is plausible
and at least one important load-bearing idea is sound.

Use the IMO 0-7 scale. A complete rigorous proof is 7. A genuine minor slip
whose correction uses only mathematics already present is 6. Score 5 is
disallowed. A gap requiring a new mathematical idea is a fallacy and caps the
score at 3. An incomplete or wrong answer cannot pass. Do not repair the proof.

PROBLEM:
{problem}

PROPOSED SOLUTION:
{proof}
"""


def phase_one_diversity_index_prompt(
    *,
    problem: str,
    finalist_packets: list[dict[str, Any]],
    eligible_anchor_indices: list[int],
) -> str:
    return f"""You are a proof-portfolio diversity adjudicator. {implementation_prompts.FIREWALL}

{len(finalist_packets)} finalists are supplied. Each has a temporary local index
used only to return your selection. Select an ordered pair for joint hypothesis
extraction.

First choose ANCHOR INDEX from ELIGIBLE TOP-SCORE ANCHOR INDICES. Those indices
share the highest independent Terra score. If there is a tie, choose the most
mathematically sound and useful proof by directly comparing only those proofs.

Then choose a different SUPPLEMENT INDEX from the other finalists. The
supplement should contribute the strongest complementary mathematical strategy
to the anchor.

Prefer substantive differences in root characterizations, invariants,
constructions, or necessity-and-sufficiency mechanisms over different wording.
Evaluate useful conjectural structure even when a written proof has a gap.
Individual proof correctness is a secondary quality floor. Do not repair the
proofs and do not author hypotheses.

You may use the supplied independent Terra score and first-break information.
No generator score or route provenance is supplied.

PROBLEM:
{problem}

ELIGIBLE TOP-SCORE ANCHOR INDICES:
{json.dumps(eligible_anchor_indices)}

FINALISTS:
{json.dumps(finalist_packets, ensure_ascii=False)}
"""


def paired_math_prompt(
    *,
    problem: str,
    positive: str,
    negative: str,
    positive_proof: str,
    negative_proof: str,
) -> str:
    return f"""You are a paired consistency arbiter. {implementation_prompts.FIREWALL}

Determine the logical relation of each supplied proof to the exact positive
and negative claims. Do not choose a side merely because both isolated calls
passed.

PROBLEM:
{problem}

POSITIVE CLAIM:
{positive}
NEGATIVE CLAIM:
{negative}
POSITIVE PROOF:
{positive_proof}
NEGATIVE PROOF:
{negative_proof}
"""


def exact_negation_math_prompt(
    *, problem: str, statement: str, exact_negation: str
) -> str:
    return f"""You are a logical-form gate, not a proof verifier or proof
author. {implementation_prompts.FIREWALL}

Check only whether NEGATIVE CLAIM is the exact logical negation of POSITIVE
CLAIM. Preserve every domain restriction and reverse all necessary
quantifiers/connectives. Do not assess whether either claim is mathematically
true and do not repair either claim. If invalid, identify the first logical
or quantifier mismatch.

PROBLEM (notation context only):
{problem}

POSITIVE CLAIM:
{statement}
NEGATIVE CLAIM:
{exact_negation}
"""


def child_math_prompt(
    *,
    problem: str,
    parent_claim: str,
    failed_proof: str,
    audit: dict[str, Any],
    proposal: dict[str, Any],
) -> str:
    verifier_math = {
        key: value
        for key, value in audit.items()
        if key not in {"claim_id", "audited_side"}
    }
    child_math = {
        key: proposal[key]
        for key in ("statement", "exact_negation", "rationale")
    }
    return f"""You are a granularity gate, not a proof author. {implementation_prompts.FIREWALL}

Check whether the proposed child matches the first break, is load-bearing for
the attempted parent route, strictly narrower, independently checkable, and has
a valid exact negation. Do not improve or replace the child.

PROBLEM:
{problem}
PARENT CLAIM:
{parent_claim}
FAILED PROOF:
{failed_proof}
VERIFIER RESULT:
{json.dumps(verifier_math, ensure_ascii=False)}
PROPOSED CHILD:
{json.dumps(child_math, ensure_ascii=False)}
"""


def _paired_math_validator(result: dict[str, Any]) -> None:
    if set(result) != PAIRED_MODEL_FIELDS:
        raise ValueError("paired Terra audit returned routing or unknown fields")
    if result["external_information_used"] is not False:
        raise ValueError("Terra paired audit violated the information firewall")


def _exact_negation_math_validator(result: dict[str, Any]) -> None:
    if set(result) != EXACT_NEGATION_MODEL_FIELDS:
        raise ValueError("exact-negation audit returned routing or unknown fields")
    if result["external_information_used"] is not False:
        raise ValueError("Terra exact-negation gate violated the information firewall")
    if result["exact_negation_valid"] is True and result["first_issue"] is not None:
        raise ValueError("valid exact-negation gate contains an issue")
    if result["exact_negation_valid"] is False and not result["first_issue"]:
        raise ValueError("invalid exact-negation gate omitted its first issue")


def _child_math_validator(result: dict[str, Any]) -> None:
    if set(result) != CHILD_MODEL_FIELDS:
        raise ValueError("child Terra gate returned routing or deterministic fields")
    if result["external_information_used"] is not False:
        raise ValueError("Terra child gate violated the information firewall")
    criteria = (
        "aligned_with_first_break",
        "load_bearing_for_parent_route",
        "strictly_narrower_than_parent",
        "independently_checkable",
        "exact_negation_valid",
    )
    expected_pass = all(result[field] is True for field in criteria)
    if (result["verdict"] == "pass") != expected_pass:
        raise ValueError("Terra child verdict disagrees with mathematical criteria")


def bind_paired_metadata(
    *, claim_id: str, audit: dict[str, Any]
) -> dict[str, Any]:
    _paired_math_validator(audit)
    return {"claim_id": claim_id, **audit}


def bind_exact_negation_metadata(
    *, claim_id: str, audit: dict[str, Any]
) -> dict[str, Any]:
    _exact_negation_math_validator(audit)
    return {"claim_id": claim_id, **audit}


def bind_child_metadata(
    *, parent_id: str, child_id: str, audit: dict[str, Any]
) -> dict[str, Any]:
    _child_math_validator(audit)
    return {
        "obligation_id": child_id,
        "parent_claim_id": parent_id,
        **audit,
        "dependencies_allowed": True,
    }


def audit_pair_clean(
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
    allowed = implementation_verification.dependency_packet(
        dependencies, memory, proofs=False
    )

    def audit_side(side: str) -> tuple[str, dict[str, Any]]:
        exact_claim = node.statement if side == "positive" else node.exact_negation
        model_audit = terra_json_call(
            prompt=previous_pipeline.side_math_audit_prompt(
                problem=problem,
                exact_claim=exact_claim,
                proof=attempts[side]["proof"],
                dependency_statements=allowed,
            ),
            schema_path=previous_pipeline.SIDE_MATH_SCHEMA,
            call_root=call_root / "terra",
            stem=side,
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=previous_pipeline._side_math_validator,
        )
        return side, previous_pipeline.bind_side_metadata(
            claim_id=node.node_id, side=side, audit=model_audit
        )

    audits: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(audit_side, side) for side in ("positive", "negative")
        ]
        for future in concurrent.futures.as_completed(futures):
            side, result = future.result()
            audits[side] = result

    direction = implementation_verification.direction_from_verdicts(
        audits["positive"]["verdict"], audits["negative"]["verdict"]
    )
    paired = None
    if direction == "conflict":
        model_paired = terra_json_call(
            prompt=paired_math_prompt(
                problem=problem,
                positive=node.statement,
                negative=node.exact_negation,
                positive_proof=attempts["positive"]["proof"],
                negative_proof=attempts["negative"]["proof"],
            ),
            schema_path=PAIRED_MATH_SCHEMA,
            call_root=call_root / "terra",
            stem="paired",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=_paired_math_validator,
        )
        paired = bind_paired_metadata(claim_id=node.node_id, audit=model_paired)
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


def ensure_exact_negation_clean(
    *,
    problem: str,
    node: implementation_verification.ClaimNode,
    engine: implementation_verification.EndpointModelEngine,
    call_root: Path,
    terra_model: str,
    max_tokens: int,
    initial_gate: dict[str, Any] | None = None,
) -> tuple[implementation_verification.ClaimNode, dict[str, Any]]:
    current = node
    attempts: list[dict[str, Any]] = []
    gate = initial_gate
    for repair_index in range(implementation_verification.MAX_EXACT_NEGATION_REPAIRS + 1):
        if gate is None:
            model_gate = terra_json_call(
                prompt=exact_negation_math_prompt(
                    problem=problem,
                    statement=current.statement,
                    exact_negation=current.exact_negation,
                ),
                schema_path=EXACT_NEGATION_MATH_SCHEMA,
                call_root=call_root,
                stem=f"terra_exact_negation_gate_{repair_index}",
                model=terra_model,
                repo_root=REPO_ROOT,
                validator=_exact_negation_math_validator,
            )
            gate = bind_exact_negation_metadata(
                claim_id=current.node_id, audit=model_gate
            )
        attempts.append(
            {
                "repair_index": repair_index,
                "exact_negation": current.exact_negation,
                "gate": gate,
            }
        )
        if gate["exact_negation_valid"] is True:
            record = {
                "claim_id": node.node_id,
                "accepted": True,
                "repairs_used": repair_index,
                "attempts": attempts,
                "final_exact_negation": current.exact_negation,
            }
            implementation_verification.write_json(
                call_root / "exact_negation_summary.json", record
            )
            return current, record
        if repair_index >= implementation_verification.MAX_EXACT_NEGATION_REPAIRS:
            break
        repaired = implementation_verification.generate_exact_negation_repair(
            problem=problem,
            node=current,
            gate=gate,
            engine=engine,
            call_root=call_root,
            repair_index=repair_index + 1,
            max_tokens=max_tokens,
        )
        current = implementation_verification.ClaimNode(
            node_id=current.node_id,
            statement=current.statement,
            exact_negation=repaired,
            depth=current.depth,
            parent_id=current.parent_id,
            dependency_ids=current.dependency_ids,
        )
        gate = None
    record = {
        "claim_id": node.node_id,
        "accepted": False,
        "repairs_used": implementation_verification.MAX_EXACT_NEGATION_REPAIRS,
        "attempts": attempts,
        "final_exact_negation": current.exact_negation,
    }
    implementation_verification.write_json(
        call_root / "exact_negation_summary.json", record
    )
    raise RuntimeError(
        f"exact-negation repair exhausted for {node.node_id}; proof generation blocked"
    )


def _run_child_math_gate(
    *,
    problem: str,
    parent: implementation_verification.ClaimNode,
    child_id: str,
    failed_attempt: dict[str, Any],
    proposal: dict[str, Any],
    call_root: Path,
    stem: str,
    terra_model: str,
) -> dict[str, Any]:
    model_gate = terra_json_call(
        prompt=child_math_prompt(
            problem=problem,
            parent_claim=parent.statement,
            failed_proof=failed_attempt["attempts"]["positive"]["proof"],
            audit=failed_attempt["audits"]["positive"],
            proposal=proposal,
        ),
        schema_path=CHILD_MATH_SCHEMA,
        call_root=call_root,
        stem=stem,
        model=terra_model,
        repo_root=REPO_ROOT,
        validator=_child_math_validator,
    )
    return bind_child_metadata(
        parent_id=parent.node_id, child_id=child_id, audit=model_gate
    )


def extract_child_clean(
    *,
    problem: str,
    parent: implementation_verification.ClaimNode,
    dependencies: tuple[str, ...],
    failed_attempt: dict[str, Any],
    child_id: str,
    engine: implementation_verification.EndpointModelEngine,
    call_root: Path,
    terra_model: str,
    max_tokens: int,
) -> tuple[implementation_verification.ClaimNode | None, dict[str, Any]]:
    result = engine.structured(
        prompt=implementation_prompts.child_extraction_prompt(
            problem=problem,
            parent_id=parent.node_id,
            parent_claim=parent.statement,
            child_id=child_id,
            failed_proof=failed_attempt["attempts"]["positive"]["proof"],
            audit=failed_attempt["audits"]["positive"],
            allowed_dependency_ids=list(dependencies),
        ),
        namespace=f"{parent.node_id}_{child_id}_extract",
        schema_name="gemma_minimal_child",
        schema=implementation_verification.read_json(
            implementation_verification.CHILD_SCHEMA
        ),
        max_tokens=min(max_tokens, 32_768),
        temperature=0.2,
    )["parsed"]
    if result["obligation_id"] != child_id or result["parent_claim_id"] != parent.node_id:
        raise ValueError("Gemma changed child or parent identity")
    if result["statement"].strip() == parent.statement.strip():
        raise ValueError("Gemma repeated the parent as its child")
    dependencies_allowed = set(result["dependency_ids"]).issubset(set(dependencies))
    if not dependencies_allowed:
        raise ValueError("Gemma introduced an undeclared child dependency")

    gate = _run_child_math_gate(
        problem=problem,
        parent=parent,
        child_id=child_id,
        failed_attempt=failed_attempt,
        proposal=result,
        call_root=call_root,
        stem="terra_gate",
        terra_model=terra_model,
    )
    record: dict[str, Any] = {
        "proposal": result,
        "python_dependencies_allowed": dependencies_allowed,
        "gate": gate,
    }
    non_negation_gate_fields = (
        "aligned_with_first_break",
        "load_bearing_for_parent_route",
        "strictly_narrower_than_parent",
        "independently_checkable",
        "dependencies_allowed",
    )
    if (
        gate["verdict"] == "fail"
        and gate["exact_negation_valid"] is False
        and all(gate[field] is True for field in non_negation_gate_fields)
    ):
        repaired_node, negation_record = ensure_exact_negation_clean(
            problem=problem,
            node=implementation_verification.ClaimNode(
                node_id=child_id,
                statement=result["statement"],
                exact_negation=result["exact_negation"],
                depth=parent.depth + 1,
                parent_id=parent.node_id,
                dependency_ids=tuple(result["dependency_ids"]),
            ),
            engine=engine,
            call_root=call_root / "exact_negation_repair",
            terra_model=terra_model,
            max_tokens=max_tokens,
            initial_gate=gate,
        )
        result = {**result, "exact_negation": repaired_node.exact_negation}
        gate = _run_child_math_gate(
            problem=problem,
            parent=parent,
            child_id=child_id,
            failed_attempt=failed_attempt,
            proposal=result,
            call_root=call_root,
            stem="terra_gate_after_negation_repair",
            terra_model=terra_model,
        )
        record.update(
            {
                "exact_negation_repair": negation_record,
                "repaired_proposal": result,
                "repaired_gate": gate,
            }
        )
    implementation_verification.write_json(call_root / "summary.json", record)
    if gate["verdict"] != "pass":
        return None, record
    return (
        implementation_verification.ClaimNode(
            node_id=child_id,
            statement=result["statement"],
            exact_negation=result["exact_negation"],
            depth=parent.depth + 1,
            parent_id=parent.node_id,
            dependency_ids=tuple(result["dependency_ids"]),
        ),
        record,
    )


def score_phase_one_candidates_clean(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> list[dict[str, Any]]:
    def score(candidate: dict[str, Any]) -> dict[str, Any]:
        candidate_id = str(candidate["candidate_id"])
        terra_score = terra_json_call(
            prompt=phase_one_score_math_prompt(
                problem=problem, proof=str(candidate["assembled_proof"])
            ),
            schema_path=implementation_pipeline.PHASE_ONE_TERRA_SCORE_SCHEMA,
            call_root=output_dir / candidate_id,
            stem="score",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=implementation_pipeline._phase_one_terra_score_validator,
        )
        return {**candidate, "phase_one_terra_score": terra_score}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        scored = list(executor.map(score, candidates))
    implementation_pipeline.write_json(
        output_dir / "summary.json",
        {
            "scorer": terra_model,
            "independent_stateless_calls": True,
            "candidate_identity_model_visible": False,
            "gemma_grades_visible": False,
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "phase_one_route": row.get("phase_one_route"),
                    "score": row["phase_one_terra_score"]["score"],
                    "verdict": row["phase_one_terra_score"]["verdict"],
                    "hypothesis_seed_value": row["phase_one_terra_score"][
                        "hypothesis_seed_value"
                    ],
                    "root_characterization_plausible": row[
                        "phase_one_terra_score"
                    ]["root_characterization_plausible"],
                }
                for row in scored
            ],
        },
    )
    return scored


def select_diversified_phase_one_candidates_clean(
    *,
    problem: str,
    candidates: list[dict[str, Any]],
    output_dir: Path,
    terra_model: str,
) -> dict[str, Any]:
    finalists = implementation_pipeline.select_top_two_per_phase_one_route(candidates)
    if len(finalists) != PHASE_ONE_FINALIST_COUNT:
        raise ValueError("Phase-1 diversity selector requires exactly eight finalists")
    highest_score = max(
        int(row["phase_one_terra_score"]["score"]) for row in finalists
    )
    eligible_anchor_indices = [
        index
        for index, row in enumerate(finalists)
        if int(row["phase_one_terra_score"]["score"]) == highest_score
    ]
    packets = [
        {
            "candidate_index": index,
            "independent_terra_score": {
                key: row["phase_one_terra_score"].get(key)
                for key in (
                    "score",
                    "verdict",
                    "answer_supported",
                    "complete",
                    "first_break",
                    "summary",
                    "root_characterization_plausible",
                    "hypothesis_seed_value",
                    "sound_load_bearing_ideas",
                )
            },
            "proof": row["assembled_proof"],
        }
        for index, row in enumerate(finalists)
    ]

    def validate(result: dict[str, Any]) -> None:
        if result["external_information_used"] is not False:
            raise ValueError("Terra diversity selector violated the firewall")
        anchor_index = int(result["anchor_index"])
        supplement_index = int(result["supplement_index"])
        if anchor_index == supplement_index:
            raise ValueError("Terra selector must choose a distinct supplement")
        valid_indices = set(range(len(finalists)))
        if anchor_index not in valid_indices or supplement_index not in valid_indices:
            raise ValueError("Terra diversity selector chose an invalid index")
        if anchor_index not in eligible_anchor_indices:
            raise ValueError("Terra selector chose an anchor below the highest score")
        assessment_indices = [
            int(row["candidate_index"]) for row in result["candidate_assessments"]
        ]
        if (
            len(assessment_indices) != len(finalists)
            or len(set(assessment_indices)) != len(finalists)
            or set(assessment_indices) != valid_indices
        ):
            raise ValueError(
                "Terra diversity selector must assess every finalist exactly once"
            )
        if not result["complementarity_axes"]:
            raise ValueError("Terra diversity selector supplied no substantive axis")

    model_audit = terra_json_call(
        prompt=phase_one_diversity_index_prompt(
            problem=problem,
            finalist_packets=packets,
            eligible_anchor_indices=eligible_anchor_indices,
        ),
        schema_path=PHASE_ONE_DIVERSITY_INDEX_SCHEMA,
        call_root=output_dir,
        stem="selection",
        model=terra_model,
        repo_root=REPO_ROOT,
        validator=validate,
    )
    anchor_index = int(model_audit["anchor_index"])
    supplement_index = int(model_audit["supplement_index"])
    bound_assessments = []
    for assessment in model_audit["candidate_assessments"]:
        index = int(assessment["candidate_index"])
        bound_assessments.append(
            {
                "candidate_id": finalists[index]["candidate_id"],
                **{
                    key: value
                    for key, value in assessment.items()
                    if key != "candidate_index"
                },
            }
        )
    audit = {
        "anchor_candidate_id": finalists[anchor_index]["candidate_id"],
        "supplement_candidate_id": finalists[supplement_index]["candidate_id"],
        "candidate_assessments": bound_assessments,
        "anchor_rationale": model_audit["anchor_rationale"],
        "supplement_rationale": model_audit["supplement_rationale"],
        "complementarity_axes": model_audit["complementarity_axes"],
        "external_information_used": model_audit["external_information_used"],
    }
    implementation_pipeline.write_json(output_dir / "selection_bound.json", audit)
    return {
        "finalists": finalists,
        "eligible_anchor_ids": [
            str(finalists[index]["candidate_id"])
            for index in eligible_anchor_indices
        ],
        "selected": [finalists[anchor_index], finalists[supplement_index]],
        "audit": audit,
    }


@contextmanager
def clean_terra_metadata_backend(scoring_model: str) -> Iterator[None]:
    with previous_pipeline.external_metadata_backend(scoring_model):
        original_pipeline_exact = implementation_pipeline.ensure_exact_negation
        original_verification_exact = implementation_verification.ensure_exact_negation
        original_audit_pair = implementation_verification.audit_pair
        original_extract_child = implementation_verification.extract_child
        original_phase_one_score = (
            implementation_pipeline.score_phase_one_candidates_with_terra
        )
        original_diversity = (
            implementation_pipeline.select_diversified_phase_one_candidates
        )
        implementation_pipeline.ensure_exact_negation = ensure_exact_negation_clean
        implementation_verification.ensure_exact_negation = ensure_exact_negation_clean
        implementation_verification.audit_pair = audit_pair_clean
        implementation_verification.extract_child = extract_child_clean
        implementation_pipeline.score_phase_one_candidates_with_terra = (
            score_phase_one_candidates_clean
        )
        implementation_pipeline.select_diversified_phase_one_candidates = (
            select_diversified_phase_one_candidates_clean
        )
        try:
            yield
        finally:
            implementation_pipeline.select_diversified_phase_one_candidates = (
                original_diversity
            )
            implementation_pipeline.score_phase_one_candidates_with_terra = (
                original_phase_one_score
            )
            implementation_verification.extract_child = original_extract_child
            implementation_verification.audit_pair = original_audit_pair
            implementation_verification.ensure_exact_negation = (
                original_verification_exact
            )
            implementation_pipeline.ensure_exact_negation = original_pipeline_exact


def run_harness(**kwargs: Any) -> dict[str, Any]:
    validate_promoted_profile()
    frozen_base = assert_frozen_base()
    requested_width = int(kwargs.pop("phase_one_width", PHASE_ONE_WIDTH))
    if requested_width != PHASE_ONE_WIDTH:
        raise ValueError("v0.3.32 fixes Phase-1 width at four candidates per route")
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
            "v0.3.32 disallows untyped route reuse; use a typed Phase-1 "
            "continuation from this harness"
        )
    scoring_model = str(kwargs.get("terra_model", TERRA_MODEL))
    output_dir = Path(kwargs["output_dir"])
    with clean_terra_metadata_backend(scoring_model):
        result = implementation_pipeline.run_harness(
            **kwargs,
            phase_one_width=PHASE_ONE_WIDTH,
            harness_version=HARNESS_VERSION,
            artifact_schema_version=ARTIFACT_SCHEMA_VERSION,
            promotion_profile=PROMOTION_PROFILE,
            promotion_base=frozen_base,
        )
    score_backend_pipeline.assert_score_only_grade_artifacts(output_dir)
    return result
