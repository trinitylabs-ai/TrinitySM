from __future__ import annotations

import concurrent.futures
import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_2_7_failed_reasoning_memory_20260812.core import (
    MODEL,
    ModelEngine,
    write_json,
)

from . import prompts
from .contracts import MAX_CHILD_DEPTH, MAX_NEW_CHILDREN_GLOBAL
from .terra_runtime import read_json, terra_json_call


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
SCHEMA_DIR = PACKAGE_DIR / "schemas"
SIDE_SCHEMA = SCHEMA_DIR / "terra_side.schema.json"
PAIRED_SCHEMA = SCHEMA_DIR / "terra_paired.schema.json"
CHILD_SCHEMA = SCHEMA_DIR / "gemma_child.schema.json"
CHILD_GATE_SCHEMA = SCHEMA_DIR / "terra_child_gate.schema.json"
EXACT_NEGATION_GATE_SCHEMA = SCHEMA_DIR / "terra_exact_negation_gate.schema.json"
MAX_EXACT_NEGATION_REPAIRS = 2
MAX_EXACT_NEGATION_SERIALIZATION_ATTEMPTS = 2


class EndpointModelEngine(ModelEngine):
    """The frozen v0.2.7 engine with its one-port restriction relaxed."""

    def __init__(
        self,
        *,
        endpoint: str,
        model: str,
        master_seed: int,
        concurrency: int,
        raw_dir: Path,
    ) -> None:
        normalized = endpoint.rstrip("/")
        if normalized not in {
            "http://127.0.0.1:8020/v1",
            "http://127.0.0.1:8022/v1",
        }:
            raise ValueError(f"unsupported local Gemma endpoint: {endpoint}")
        if model != MODEL:
            raise ValueError(f"all Gemma roles must use {MODEL!r}")
        self.endpoint = normalized
        self.model = model
        self.master_seed = int(master_seed)
        self.concurrency = int(concurrency)
        self.raw_dir = raw_dir


@dataclass(frozen=True)
class ClaimNode:
    node_id: str
    statement: str
    exact_negation: str
    depth: int = 0
    parent_id: str | None = None
    dependency_ids: tuple[str, ...] = ()


RELATION_DIRECTION = {
    "proves_positive": "positive",
    "refutes_negative": "positive",
    "proves_negative": "negative",
    "refutes_positive": "negative",
    "unresolved": None,
}


def failed_memory_id(statement: str) -> str:
    normalized = " ".join(statement.split()).casefold()
    return "terra-failed-" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def attempted_proof_packet(attempt: dict[str, Any]) -> dict[str, Any]:
    return {
        side: {
            "proof": attempt["attempts"][side]["proof"],
            "terra_audit": attempt["audits"][side],
        }
        for side in ("positive", "negative")
    }


def direction_from_verdicts(positive: str, negative: str) -> str:
    if positive == "pass" and negative != "pass":
        return "positive_verified"
    if negative == "pass" and positive != "pass":
        return "negative_verified"
    if positive == "pass" and negative == "pass":
        return "conflict"
    return "unresolved"


def paired_direction(result: dict[str, Any]) -> str:
    if result.get("claims_are_exact_negations") is not True:
        return "unresolved"
    directions = {
        direction
        for field in ("positive_proof_relation", "negative_proof_relation")
        if (direction := RELATION_DIRECTION.get(str(result.get(field)))) is not None
    }
    if directions == {"positive"}:
        return "positive_verified"
    if directions == {"negative"}:
        return "negative_verified"
    return "unresolved"


def dependency_packet(
    dependency_ids: tuple[str, ...], memory: list[dict[str, Any]], *, proofs: bool
) -> list[dict[str, Any]]:
    indexed = {str(row["lemma_id"]): row for row in memory}
    packet: list[dict[str, Any]] = []
    for dependency_id in dependency_ids:
        if dependency_id not in indexed:
            raise ValueError(f"unknown verified dependency: {dependency_id}")
        row = indexed[dependency_id]
        item = {"lemma_id": dependency_id, "statement": row["statement"]}
        if proofs:
            item["proof"] = row["proof"]
        packet.append(item)
    return packet


def _side_validator(result: dict[str, Any], node: ClaimNode, side: str) -> None:
    if result["claim_id"] != node.node_id or result["audited_side"] != side:
        raise ValueError("Terra changed claim identity or side")
    if result["external_information_used"] is not False:
        raise ValueError("Terra side audit violated the information firewall")
    if result["verdict"] == "pass" and (
        result["exact_claim_reached"] is not True
        or result["first_break"] is not None
        or result["missing_obligations"]
    ):
        raise ValueError("passing side audit contains a failed criterion")


def generate_pair(
    *,
    problem: str,
    node: ClaimNode,
    dependencies: tuple[str, ...],
    memory: list[dict[str, Any]],
    engines: tuple[EndpointModelEngine, EndpointModelEngine],
    namespace: str,
    max_tokens: int,
    previous: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    packet = dependency_packet(dependencies, memory, proofs=True)

    def generate(side_index: int, side: str) -> tuple[str, dict[str, Any]]:
        exact_claim = node.statement if side == "positive" else node.exact_negation
        if previous is None:
            prompt = prompts.proof_attempt_prompt(
                problem=problem,
                claim_id=node.node_id,
                side=side,
                exact_claim=exact_claim,
                dependencies=packet,
            )
        else:
            prompt = prompts.repair_attempt_prompt(
                problem=problem,
                claim_id=node.node_id,
                side=side,
                exact_claim=exact_claim,
                previous_proof=previous["attempts"][side]["proof"],
                audit=previous["audits"][side],
                dependencies=packet,
            )
        response = engines[side_index].text(
            prompt=prompt,
            namespace=f"{namespace}_{side}",
            max_tokens=max_tokens,
            temperature=0.6 if previous is not None else 1.0,
        )
        return side, {
            "node_id": node.node_id,
            "side": side,
            "exact_claim": exact_claim,
            "proof": response["final"],
            "dependency_ids": list(dependencies),
        }

    attempts: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(generate, index, side)
            for index, side in enumerate(("positive", "negative"))
        ]
        for future in concurrent.futures.as_completed(futures):
            side, result = future.result()
            attempts[side] = result
    return attempts


def audit_pair(
    *,
    problem: str,
    node: ClaimNode,
    dependencies: tuple[str, ...],
    memory: list[dict[str, Any]],
    attempts: dict[str, dict[str, Any]],
    call_root: Path,
    terra_model: str,
    mode: str,
) -> dict[str, Any]:
    allowed = dependency_packet(dependencies, memory, proofs=False)

    def audit(side: str) -> tuple[str, dict[str, Any]]:
        exact_claim = node.statement if side == "positive" else node.exact_negation
        result = terra_json_call(
            prompt=prompts.side_audit_prompt(
                problem=problem,
                claim_id=node.node_id,
                side=side,
                exact_claim=exact_claim,
                proof=attempts[side]["proof"],
                dependency_statements=allowed,
            ),
            schema_path=SIDE_SCHEMA,
            call_root=call_root / "terra",
            stem=side,
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=lambda value: _side_validator(value, node, side),
        )
        return side, result

    audits: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(audit, side) for side in ("positive", "negative")]
        for future in concurrent.futures.as_completed(futures):
            side, result = future.result()
            audits[side] = result
    direction = direction_from_verdicts(
        audits["positive"]["verdict"], audits["negative"]["verdict"]
    )
    paired = None
    if direction == "conflict":
        paired = terra_json_call(
            prompt=prompts.paired_prompt(
                problem=problem,
                claim_id=node.node_id,
                positive=node.statement,
                negative=node.exact_negation,
                positive_proof=attempts["positive"]["proof"],
                negative_proof=attempts["negative"]["proof"],
            ),
            schema_path=PAIRED_SCHEMA,
            call_root=call_root / "terra",
            stem="paired",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=lambda value: _paired_validator(value, node),
        )
        direction = paired_direction(paired)
    result = {
        "node": asdict(node),
        "mode": mode,
        "dependency_ids": list(dependencies),
        "attempts": attempts,
        "audits": audits,
        "paired_audit": paired,
        "final_direction": direction,
    }
    write_json(call_root / "summary.json", result)
    return result


def _paired_validator(result: dict[str, Any], node: ClaimNode) -> None:
    if result["claim_id"] != node.node_id:
        raise ValueError("Terra paired audit changed claim_id")
    if result["external_information_used"] is not False:
        raise ValueError("Terra paired audit violated the information firewall")


def run_ladder(
    *,
    problem: str,
    node: ClaimNode,
    dependencies: tuple[str, ...],
    memory: list[dict[str, Any]],
    engines: tuple[EndpointModelEngine, EndpointModelEngine],
    stage_root: Path,
    terra_model: str,
    max_tokens: int,
    round_index: int,
) -> dict[str, Any]:
    stages: list[dict[str, Any]] = []

    initial_attempts = generate_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        engines=engines,
        namespace=f"{node.node_id}_r{round_index}_initial",
        max_tokens=max_tokens,
    )
    initial = audit_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        attempts=initial_attempts,
        call_root=stage_root / node.node_id / f"round_{round_index}" / "initial",
        terra_model=terra_model,
        mode="initial_proof",
    )
    stages.append(initial)
    if initial["final_direction"] in {"positive_verified", "negative_verified"}:
        return {"stages": stages, "final_attempt": initial}

    repair_attempts = generate_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        engines=engines,
        namespace=f"{node.node_id}_r{round_index}_initial_repair",
        max_tokens=max_tokens,
        previous=initial,
    )
    repair = audit_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        attempts=repair_attempts,
        call_root=stage_root / node.node_id / f"round_{round_index}" / "initial_repair",
        terra_model=terra_model,
        mode="repair_initial_proof",
    )
    stages.append(repair)
    if repair["final_direction"] in {"positive_verified", "negative_verified"}:
        return {"stages": stages, "final_attempt": repair}

    fresh_attempts = generate_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        engines=engines,
        namespace=f"{node.node_id}_r{round_index}_fresh",
        max_tokens=max_tokens,
    )
    fresh = audit_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        attempts=fresh_attempts,
        call_root=stage_root / node.node_id / f"round_{round_index}" / "fresh",
        terra_model=terra_model,
        mode="fresh_proof",
    )
    stages.append(fresh)
    if fresh["final_direction"] in {"positive_verified", "negative_verified"}:
        return {"stages": stages, "final_attempt": fresh}

    fresh_repair_attempts = generate_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        engines=engines,
        namespace=f"{node.node_id}_r{round_index}_fresh_repair",
        max_tokens=max_tokens,
        previous=fresh,
    )
    fresh_repair = audit_pair(
        problem=problem,
        node=node,
        dependencies=dependencies,
        memory=memory,
        attempts=fresh_repair_attempts,
        call_root=stage_root / node.node_id / f"round_{round_index}" / "fresh_repair",
        terra_model=terra_model,
        mode="repair_fresh_proof",
    )
    stages.append(fresh_repair)
    return {"stages": stages, "final_attempt": fresh_repair}


def extract_child(
    *,
    problem: str,
    parent: ClaimNode,
    dependencies: tuple[str, ...],
    failed_attempt: dict[str, Any],
    child_id: str,
    engine: EndpointModelEngine,
    call_root: Path,
    terra_model: str,
    max_tokens: int,
) -> tuple[ClaimNode | None, dict[str, Any]]:
    result = engine.structured(
        prompt=prompts.child_extraction_prompt(
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
        schema=read_json(CHILD_SCHEMA),
        max_tokens=min(max_tokens, 32_768),
        temperature=0.2,
    )["parsed"]
    if result["obligation_id"] != child_id or result["parent_claim_id"] != parent.node_id:
        raise ValueError("Gemma changed child or parent identity")
    if result["statement"].strip() == parent.statement.strip():
        raise ValueError("Gemma repeated the parent as its child")
    if not set(result["dependency_ids"]).issubset(set(dependencies)):
        raise ValueError("Gemma introduced an undeclared child dependency")
    gate = terra_json_call(
        prompt=prompts.child_gate_prompt(
            problem=problem,
            parent_id=parent.node_id,
            parent_claim=parent.statement,
            failed_proof=failed_attempt["attempts"]["positive"]["proof"],
            audit=failed_attempt["audits"]["positive"],
            proposal=result,
            allowed_dependency_ids=list(dependencies),
        ),
        schema_path=CHILD_GATE_SCHEMA,
        call_root=call_root,
        stem="terra_gate",
        model=terra_model,
        repo_root=REPO_ROOT,
        validator=lambda value: _child_gate_validator(value, parent, child_id),
    )
    record: dict[str, Any] = {"proposal": result, "gate": gate}
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
        repaired_node, negation_record = ensure_exact_negation(
            problem=problem,
            node=ClaimNode(
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
        gate = terra_json_call(
            prompt=prompts.child_gate_prompt(
                problem=problem,
                parent_id=parent.node_id,
                parent_claim=parent.statement,
                failed_proof=failed_attempt["attempts"]["positive"]["proof"],
                audit=failed_attempt["audits"]["positive"],
                proposal=result,
                allowed_dependency_ids=list(dependencies),
            ),
            schema_path=CHILD_GATE_SCHEMA,
            call_root=call_root,
            stem="terra_gate_after_negation_repair",
            model=terra_model,
            repo_root=REPO_ROOT,
            validator=lambda value: _child_gate_validator(value, parent, child_id),
        )
        record.update(
            {
                "exact_negation_repair": negation_record,
                "repaired_proposal": result,
                "repaired_gate": gate,
            }
        )
    write_json(call_root / "summary.json", record)
    if gate["verdict"] != "pass":
        return None, record
    return (
        ClaimNode(
            node_id=child_id,
            statement=result["statement"],
            exact_negation=result["exact_negation"],
            depth=parent.depth + 1,
            parent_id=parent.node_id,
            dependency_ids=tuple(result["dependency_ids"]),
        ),
        record,
    )


def _child_gate_validator(
    result: dict[str, Any], parent: ClaimNode, child_id: str
) -> None:
    if result["obligation_id"] != child_id or result["parent_claim_id"] != parent.node_id:
        raise ValueError("Terra changed child or parent identity")
    if result["external_information_used"] is not False:
        raise ValueError("Terra child gate violated the information firewall")
    fields = (
        "aligned_with_first_break",
        "load_bearing_for_parent_route",
        "strictly_narrower_than_parent",
        "independently_checkable",
        "exact_negation_valid",
        "dependencies_allowed",
    )
    expected_pass = all(result[field] is True for field in fields)
    if (result["verdict"] == "pass") != expected_pass:
        raise ValueError("Terra child verdict disagrees with its criteria")


def _exact_negation_gate_validator(
    result: dict[str, Any], node: ClaimNode,
) -> None:
    if result["claim_id"] != node.node_id:
        raise ValueError("Terra exact-negation gate changed claim identity")
    if result["external_information_used"] is not False:
        raise ValueError("Terra exact-negation gate violated the information firewall")
    if result["exact_negation_valid"] is True and result["first_issue"] is not None:
        raise ValueError("valid exact-negation gate contains an issue")
    if result["exact_negation_valid"] is False and not result["first_issue"]:
        raise ValueError("invalid exact-negation gate omitted its first issue")


def parse_exact_negation_marker(output: str) -> str:
    matches = re.findall(r"(?im)^\s*EXACT_NEGATION\s*:\s*(\S.*)\s*$", output)
    if not matches:
        raise ValueError("Gemma negation repair omitted the EXACT_NEGATION marker")
    candidate = matches[-1].strip()
    if candidate.startswith(("{", "[")):
        raise ValueError("Gemma negation repair returned structured data")
    return candidate


def generate_exact_negation_repair(
    *,
    problem: str,
    node: ClaimNode,
    gate: dict[str, Any],
    engine: EndpointModelEngine,
    call_root: Path,
    repair_index: int,
    max_tokens: int,
) -> str:
    attempts: list[dict[str, Any]] = []
    prompt = prompts.exact_negation_repair_prompt(
        problem=problem,
        claim_id=node.node_id,
        statement=node.statement,
        exact_negation=node.exact_negation,
        gate=gate,
    )
    for serialization_attempt in range(
        1, MAX_EXACT_NEGATION_SERIALIZATION_ATTEMPTS + 1
    ):
        response = engine.text(
            prompt=prompt,
            namespace=(
                f"{node.node_id}_exact_negation_repair_{repair_index}"
                f"_plain_{serialization_attempt}"
            ),
            max_tokens=min(max_tokens, 8_192),
            temperature=0.1,
        )
        try:
            exact_negation = parse_exact_negation_marker(response["final"])
        except ValueError as error:
            attempts.append(
                {
                    "serialization_attempt": serialization_attempt,
                    "accepted": False,
                    "error": str(error),
                    "final": response["final"],
                }
            )
            continue
        attempts.append(
            {
                "serialization_attempt": serialization_attempt,
                "accepted": True,
                "exact_negation": exact_negation,
            }
        )
        write_json(
            call_root / f"gemma_exact_negation_repair_{repair_index}.json",
            {"accepted": True, "attempts": attempts},
        )
        return exact_negation
    write_json(
        call_root / f"gemma_exact_negation_repair_{repair_index}.json",
        {"accepted": False, "attempts": attempts},
    )
    raise RuntimeError(
        f"plain-text exact-negation repair exhausted for {node.node_id}"
    )


def ensure_exact_negation(
    *,
    problem: str,
    node: ClaimNode,
    engine: EndpointModelEngine,
    call_root: Path,
    terra_model: str,
    max_tokens: int,
    initial_gate: dict[str, Any] | None = None,
) -> tuple[ClaimNode, dict[str, Any]]:
    """Fail closed unless Gemma's negation passes a fresh Terra logic gate."""

    current = node
    attempts: list[dict[str, Any]] = []
    gate = initial_gate
    for repair_index in range(MAX_EXACT_NEGATION_REPAIRS + 1):
        if gate is None:
            gate = terra_json_call(
                prompt=prompts.exact_negation_gate_prompt(
                    problem=problem,
                    claim_id=current.node_id,
                    statement=current.statement,
                    exact_negation=current.exact_negation,
                ),
                schema_path=EXACT_NEGATION_GATE_SCHEMA,
                call_root=call_root,
                stem=f"terra_exact_negation_gate_{repair_index}",
                model=terra_model,
                repo_root=REPO_ROOT,
                validator=lambda value: _exact_negation_gate_validator(value, current),
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
            write_json(call_root / "exact_negation_summary.json", record)
            return current, record
        if repair_index >= MAX_EXACT_NEGATION_REPAIRS:
            break
        repaired = generate_exact_negation_repair(
            problem=problem,
            node=current,
            gate=gate,
            engine=engine,
            call_root=call_root,
            repair_index=repair_index + 1,
            max_tokens=max_tokens,
        )
        current = ClaimNode(
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
        "repairs_used": MAX_EXACT_NEGATION_REPAIRS,
        "attempts": attempts,
        "final_exact_negation": current.exact_negation,
    }
    write_json(call_root / "exact_negation_summary.json", record)
    raise RuntimeError(
        f"exact-negation repair exhausted for {node.node_id}; proof generation blocked"
    )


def admit_positive(
    *,
    memory: list[dict[str, Any]],
    node: ClaimNode,
    dependencies: tuple[str, ...],
    attempt: dict[str, Any],
) -> dict[str, Any]:
    if any(row["lemma_id"] == node.node_id for row in memory):
        return next(row for row in memory if row["lemma_id"] == node.node_id)
    row = {
        "lemma_id": node.node_id,
        "statement": node.statement,
        "direction": "positive_verified",
        "proof": attempt["attempts"]["positive"]["proof"],
        "dependency_ids": list(dependencies),
        "source": attempt["mode"],
    }
    memory.append(row)
    return row


def verify_claim(
    *,
    problem: str,
    node: ClaimNode,
    memory: list[dict[str, Any]],
    ledger: list[dict[str, Any]],
    engines: tuple[EndpointModelEngine, EndpointModelEngine],
    stage_root: Path,
    terra_model: str,
    max_tokens: int,
    child_budget: dict[str, int],
) -> dict[str, Any]:
    dependencies = tuple(node.dependency_ids)
    history: list[dict[str, Any]] = []
    round_index = 0
    while True:
        ladder = run_ladder(
            problem=problem,
            node=node,
            dependencies=dependencies,
            memory=memory,
            engines=engines,
            stage_root=stage_root,
            terra_model=terra_model,
            max_tokens=max_tokens,
            round_index=round_index,
        )
        history.append(ladder)
        final_attempt = ladder["final_attempt"]
        direction = final_attempt["final_direction"]
        if direction == "positive_verified":
            admitted = admit_positive(
                memory=memory,
                node=node,
                dependencies=dependencies,
                attempt=final_attempt,
            )
            return {"node": asdict(node), "status": direction, "admitted": admitted, "history": history}
        if direction == "negative_verified":
            row = {
                "memory_id": failed_memory_id(node.statement),
                "lemma_id": node.node_id,
                "candidate_claim": node.statement,
                "exact_negation": node.exact_negation,
                "status": "refuted",
                "negative_proof": final_attempt["attempts"]["negative"]["proof"],
                "attempted_proofs": attempted_proof_packet(final_attempt),
                "failure_reason": (
                    "The exact supplied negation passed an isolated Terra audit "
                    "while the positive side did not."
                ),
                "reasoning_failures": [
                    {
                        "side": "candidate_claim",
                        "unsupported_inference": final_attempt["audits"]["positive"][
                            "first_break"
                        ],
                    }
                ],
                "source": final_attempt["mode"],
            }
            ledger.append(row)
            return {"node": asdict(node), "status": direction, "history": history}
        if node.depth >= MAX_CHILD_DEPTH:
            reason = "maximum_child_depth_reached"
            break
        if child_budget["used"] >= MAX_NEW_CHILDREN_GLOBAL:
            reason = "global_child_budget_reached"
            break
        child_budget["used"] += 1
        child_id = f"{node.node_id}.C{child_budget['used']}"
        child, record = extract_child(
            problem=problem,
            parent=node,
            dependencies=dependencies,
            failed_attempt=final_attempt,
            child_id=child_id,
            engine=engines[0],
            call_root=stage_root / node.node_id / "children" / child_id,
            terra_model=terra_model,
            max_tokens=max_tokens,
        )
        if child is None:
            reason = f"child_gate_failed:{child_id}"
            break
        child_result = verify_claim(
            problem=problem,
            node=child,
            memory=memory,
            ledger=ledger,
            engines=engines,
            stage_root=stage_root,
            terra_model=terra_model,
            max_tokens=max_tokens,
            child_budget=child_budget,
        )
        if child_result["status"] != "positive_verified":
            reason = f"child_not_positive_verified:{child_id}"
            break
        if child_id not in dependencies:
            dependencies = (*dependencies, child_id)
        round_index += 1

    last = history[-1]["final_attempt"]
    ledger_row = {
        "memory_id": failed_memory_id(node.statement),
        "lemma_id": node.node_id,
        "candidate_claim": node.statement,
        "exact_negation": node.exact_negation,
        "status": "unresolved",
        "reason": reason,
        "failure_reason": (
            "Neither the exact positive claim nor its exact negation passed the "
            "Terra verification ladder. This is lack of proof, not a refutation."
        ),
        "last_positive_first_break": last["audits"]["positive"]["first_break"],
        "attempted_proofs": attempted_proof_packet(last),
        "reasoning_failures": [
            {
                "side": side,
                "unsupported_inference": last["audits"][side]["first_break"],
                "missing_obligations": last["audits"][side]["missing_obligations"],
            }
            for side in ("positive", "negative")
        ],
    }
    ledger.append(ledger_row)
    return {"node": asdict(node), "status": "unresolved", "reason": reason, "history": history}
