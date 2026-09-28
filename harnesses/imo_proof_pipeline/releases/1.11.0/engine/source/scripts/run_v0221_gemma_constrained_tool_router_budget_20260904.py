#!/usr/bin/env python3
"""Constrained Gemma tool routing followed by same-trace global proof repair.

This is the positive iteration after the v0220 negative experiment.  v0220's
tool offer was appended after Gemma had already closed its thought channel, so
the model simply emitted another proof and never produced a parseable request.
Here a separate, reference-free Gemma router emits a schema-constrained request.
Only that model-emitted request may be executed.  Its exact result is then
inserted into the *original* solver reasoning trace before semantic budget
forcing and a mandatory whole-proof rewrite.

The runner intentionally links to frozen v0220 initial calls.  This avoids a
new-sample confound: v0221 and every v0220 arm begin with byte-identical solver
reasoning and terminal candidates.  Reference solutions are neither loaded nor
sent by this program.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_v0220_gemma_global_tool_budget_20260904 as v0220
from cognitive_well_harness_v0_3_64_modular_two_proof_synthesis_20260824.model_runtime import (
    ModelRuntime,
    RuntimeConfig,
)
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.arguments import (
    validate_operation_arguments,
)
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.registry import (
    Capability,
    CapabilityRegistry,
    default_registry,
)
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.schemas import stable_hash


HARNESS_VERSION = "v0.3.221-gemma-constrained-tool-router-budget-20260904"
MANIFEST_SCHEMA = "cognitive-well-v0221-constrained-router-manifest-v1"
RESULT_SCHEMA = "cognitive-well-v0221-constrained-router-result-v1"
PROBLEM_SCHEMA = "cognitive-well-v0221-problem-result-v1"
SEED_NAMESPACE = "v0221"
MODEL = "google/gemma-4-31B-it"
DEFAULT_CONFIG = ROOT / "configs/v0221_constrained_tool_router_pilot.json"
DEFAULT_OUTPUT = ROOT / "runs/v0221_gemma_constrained_tool_router_pilot_20260904"
ROUTER_ACTIONS = ("call_tool", "no_tool")
NONE_OPERATION = "none"

# This is still a generic allowlist.  exact_branch_system is the frozen,
# independently recomputed polynomial/branch primitive; it is not a
# problem-specific certificate or template.
EXPOSED_OPERATIONS = v0220.EXPOSED_OPERATIONS + ("exact_branch_system",)
OPERATION_ARGUMENT_KEYS = {
    **v0220.OPERATION_ARGUMENT_KEYS,
    "exact_branch_system": frozenset(
        {
            "task",
            "symbols",
            "original_equations",
            "common_conditions",
            "partition",
            "branches",
            "solve_for",
            "output_expression",
            "aggregate",
        }
    ),
}


ROUTER_SYSTEM_PROMPT = r"""You are the tool-routing component of a generic
Olympiad proof solver. You receive only a problem and an untrusted initial proof.
Choose at most one exact, load-bearing computation that can repair or certify an
important step. Do not solve from a reference solution and do not invent tool
results. Your response is constrained JSON and is itself the tool request.

Select call_tool only when the arguments can be derived from the supplied problem
and candidate and the exact result will materially advance the proof. Select
no_tool when no operation fits; do not make an irrelevant call merely because a
tool exists. Never emit code, shell, paths, URLs, or prose outside the schema.
"""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def router_schema(operations: tuple[str, ...]) -> dict[str, Any]:
    """A vLLM-compatible strict envelope; arguments remain model-emitted JSON text."""

    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["action", "operation", "claim", "arguments_json", "fit_rationale"],
        "properties": {
            "action": {"type": "string", "enum": list(ROUTER_ACTIONS)},
            "operation": {
                "type": "string",
                "enum": [NONE_OPERATION, *operations],
            },
            "claim": {"type": "string", "maxLength": 4096},
            "arguments_json": {"type": "string", "minLength": 2, "maxLength": 30000},
            "fit_rationale": {"type": "string", "minLength": 1, "maxLength": 2000},
        },
    }


def tool_catalog(operations: tuple[str, ...]) -> str:
    summaries = {
        "expand_and_compare": 'arguments {"symbols":[...],"left":EXPR,"right":EXPR}',
        "factor_and_reexpand": 'arguments {"symbols":[...],"expression":EXPR}',
        "simplify_identity": 'arguments {"symbols":[...],"left":EXPR,"right":EXPR}',
        "solve_and_substitute": (
            'arguments {"symbols":[...],"equations":[EXPR,...],"solve_for":[...]}; '
            "every equation is an expression equal to zero"
        ),
        "polynomial_root_filter": (
            'arguments {"symbols":[...],"polynomial":EXPR,"variable":"x",'
            '"domain":"complex|real|positive|nonnegative|integer"}'
        ),
        "exact_modular_evaluation": (
            'arguments {"base":INTEGER,"exponent":NONNEGATIVE_INTEGER,"modulus":POSITIVE_INTEGER}'
        ),
        "gcd": 'arguments {"values":[INTEGER,INTEGER,...]}',
        "prime_factorization": 'arguments {"value":NONZERO_INTEGER}',
        "determinant": 'arguments {"matrix":[[INTEGER,...],...]}',
        "enumerate_finite_assignments": (
            'arguments {"domains":[[INTEGER,...],...],"constraints":[FINITE_EXPR,...]}; '
            'domain index i is referenced as {"var":i}; FINITE_EXPR supports integer '
            'nodes add/mul/sub/mod/pow/neg and Boolean nodes eq/ne/lt/le/gt/ge/and/or/not'
        ),
        "exact_branch_system": (
            'arguments {"task":"safe_identifier","symbols":[...],'
            '"original_equations":[EXPR,...],"common_conditions":'
            '[{"relation":"nonzero|positive|nonnegative","expression":EXPR},...],'
            '"partition":{"kind":"exhaustive_solutions"},"branches":'
            '[{"branch_id":"all_valid_roots","equations":[],"conditions":[]}],'
            '"solve_for":[every symbol once],"output_expression":EXPR,"aggregate":"union"}. '
            "Use this only for a bounded exact polynomial system with all exclusions encoded"
        ),
    }
    rows = "\n".join(f"- {name}: {summaries[name]}" for name in operations)
    return f"""AVAILABLE EXACT OPERATIONS
{rows}

EXPR is a safe recursive JSON AST. Leaves are integers, {{"symbol":"x"}}, or
{{"rational":[p,q]}}. Nodes are {{"add":[EXPR,...]}}, {{"mul":[EXPR,...]}},
{{"sub":[EXPR,EXPR]}}, {{"div":[EXPR,EXPR]}}, {{"pow":[EXPR,INTEGER]}},
{{"neg":EXPR}}, or {{"abs":EXPR}}. No functions, strings-as-expressions, or code.

The arguments_json field must be a JSON-encoded object matching exactly the chosen
operation. For no_tool, use operation "none", claim "", and arguments_json "{{}}".
"""


def router_user_prompt(
    problem: v0220.Problem, initial_candidate: str, operations: tuple[str, ...]
) -> str:
    return f"""PROBLEM ID: {problem.problem_id}

PROBLEM
{problem.statement}

INITIAL CANDIDATE (untrusted)
{initial_candidate.strip()}

{tool_catalog(operations)}

Return the single best strict router record now. The fit_rationale must identify
how the requested result connects to a specific proof obligation. Do not include
or infer any reference solution."""


def parse_router_record(
    record: Mapping[str, Any], allowed_operations: set[str] | frozenset[str]
) -> dict[str, Any]:
    expected = {"action", "operation", "claim", "arguments_json", "fit_rationale"}
    if set(record) != expected:
        return {
            "status": "malformed",
            "valid": False,
            "reason": f"router keys must be exactly {sorted(expected)}",
        }
    action = str(record.get("action") or "")
    operation = str(record.get("operation") or "")
    claim = str(record.get("claim") or "").strip()
    arguments_json = str(record.get("arguments_json") or "")
    fit_rationale = str(record.get("fit_rationale") or "").strip()
    if action not in ROUTER_ACTIONS:
        return {"status": "malformed", "valid": False, "reason": "invalid action"}
    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError as error:
        return {
            "status": "malformed",
            "valid": False,
            "reason": f"arguments_json is invalid JSON: {error}",
        }
    if not isinstance(arguments, dict):
        return {
            "status": "malformed",
            "valid": False,
            "reason": "arguments_json must decode to an object",
        }
    if action == "no_tool":
        if operation != NONE_OPERATION or claim or arguments:
            return {
                "status": "rejected",
                "valid": False,
                "reason": "no_tool requires operation none, empty claim, and empty arguments",
            }
        return {
            "status": "no_tool_call",
            "valid": True,
            "call_requested": False,
            "fit_rationale": fit_rationale,
            "model_record": dict(record),
        }
    if operation not in allowed_operations:
        return {
            "status": "rejected",
            "valid": False,
            "reason": f"operation is not allowlisted: {operation}",
        }
    if not claim or len(claim) > 4096:
        return {
            "status": "rejected",
            "valid": False,
            "reason": "call_tool requires a nonempty bounded claim",
        }
    unexpected = sorted(set(arguments) - OPERATION_ARGUMENT_KEYS[operation])
    if unexpected:
        return {
            "status": "rejected",
            "valid": False,
            "reason": f"unexpected argument keys: {unexpected}",
        }
    try:
        normalized_arguments = validate_operation_arguments(operation, arguments)
    except Exception as error:
        return {
            "status": "rejected",
            "valid": False,
            "reason": f"argument validation failed: {type(error).__name__}: {error}",
        }
    call = {
        "operation": operation,
        "claim": claim,
        "arguments": normalized_arguments,
    }
    return {
        "status": "valid_tool_call",
        "valid": True,
        "call_requested": True,
        "call": call,
        "call_sha256": stable_hash(call),
        "fit_rationale": fit_rationale,
        "model_record": dict(record),
    }


def build_registry(operations: tuple[str, ...]) -> CapabilityRegistry:
    base = default_registry()
    capabilities: list[Capability] = []
    for operation in operations:
        if operation not in EXPOSED_OPERATIONS:
            raise ValueError(f"operation is not approved by v0221: {operation}")
        capabilities.append(base.get(operation))
    return CapabilityRegistry(tuple(capabilities))


def load_linked_source(
    source_run: Path, problem_id: str
) -> tuple[v0220.Problem, dict[str, Any], dict[str, Any]]:
    problem_dir = source_run / problem_id
    input_path = problem_dir / "input/problem.json"
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    statement = str(payload.get("statement") or "").strip()
    if str(payload.get("problem_id") or "") != problem_id or not statement:
        raise ValueError(f"invalid linked problem input for {problem_id}")
    original_source_path = Path(str(payload.get("source_path") or input_path)).resolve()
    problem = v0220.Problem(problem_id, statement, original_source_path)
    source_dir = problem_dir / "shared_initial/model_call"
    source = v0220.source_from_initial(source_dir, "global_solve")
    shared = json.loads(
        (problem_dir / "shared_initial/summary.json").read_text(encoding="utf-8")
    )
    checks = {
        "problem_statement_sha256_matches": sha256_text(statement)
        == str(payload.get("statement_sha256") or ""),
        "reasoning_sha256_matches": sha256_text(str(source["reasoning"]))
        == str(shared.get("reasoning_sha256") or ""),
        "initial_proof_sha256_matches": sha256_text(str(source["content"]))
        == str(shared.get("initial_proof_sha256") or ""),
        "model_is_gemma": str(source["model"]) == MODEL,
        "linked_input_declares_no_gold": payload.get("gold_or_reference_included") is False,
    }
    if not all(checks.values()):
        raise ValueError(f"linked source integrity failed for {problem_id}: {checks}")
    link = {
        "source_run": str(source_run.resolve()),
        "source_problem_dir": str(problem_dir.resolve()),
        "source_call_dir": str(source_dir.resolve()),
        "source_problem_input": str(input_path.resolve()),
        "source_reasoning_sha256": sha256_text(str(source["reasoning"])),
        "source_initial_proof_sha256": sha256_text(str(source["content"])),
        "source_sampling_seed": int(source["seed"]),
        "reuse_rationale": (
            f"frozen initial call from {source_run.name} reused to preserve the exact "
            "causal fork and avoid a new-sample confound"
        ),
        "integrity_checks": checks,
        "all_integrity_checks_passed": all(checks.values()),
    }
    return problem, source, link


def run_router(
    *,
    problem: v0220.Problem,
    source: Mapping[str, Any],
    problem_dir: Path,
    config: Mapping[str, Any],
    endpoint: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    operations = tuple(str(value) for value in config["allowed_tools"])
    schema = router_schema(operations)
    runtime = ModelRuntime(
        RuntimeConfig(
            gemma_endpoint=endpoint.rstrip("/"),
            qwen_endpoint="http://127.0.0.1:1/v1",
            gemma_model=str(config.get("model", MODEL)),
            qwen_model="unused",
            master_seed=int(config["master_seed"]),
            thinking_token_budget=None,
            reasoning_effort="max",
        )
    )
    attempts: list[dict[str, Any]] = []
    prior_feedback = ""
    parsed: dict[str, Any] | None = None
    for attempt_index in range(1, int(config["router_attempts"]) + 1):
        destination = problem_dir / "router" / f"attempt_{attempt_index:02d}"
        system_prompt = ROUTER_SYSTEM_PROMPT
        user_prompt = router_user_prompt(problem, str(source["content"]), operations)
        if prior_feedback:
            user_prompt += (
                "\n\nSTRICT VALIDATION FEEDBACK FROM THE PRIOR ROUTER RECORD\n"
                + prior_feedback
                + "\nRegenerate the complete record. Do not claim the prior call executed."
            )
        record, generation = runtime.structured(
            role="gemma",
            prompt=system_prompt,
            user_prompt=user_prompt,
            destination=destination,
            stage="tool_router",
            schema=schema,
            temperature=float(config["router_temperature"]),
            max_tokens=int(config["router_max_tokens"]),
            seed_label=f"{SEED_NAMESPACE}:router:{problem.problem_id}:attempt:{attempt_index}",
            use_explicit_guided_json=False,
        )
        parsed = parse_router_record(record, frozenset(operations))
        raw_record = canonical_json(record)
        attempt = {
            "attempt_index": attempt_index,
            "model": str(config.get("model", MODEL)),
            "role": "gemma_constrained_tool_router",
            "response_format": "strict_json_schema",
            "schema_sha256": sha256_text(canonical_json(schema)),
            "system_prompt_sha256": sha256_text(system_prompt),
            "user_prompt_sha256": sha256_text(user_prompt),
            "model_emitted_record": record,
            "model_emitted_record_sha256": sha256_text(raw_record),
            "parse": parsed,
            "generation_metadata": generation.get("metadata"),
            "input_scope": ["problem", "v0220_initial_candidate", "generic_tool_catalog"],
            "gold_or_reference_supplied": False,
        }
        v0220.write_json(destination / "model_emitted_record.json", record)
        v0220.write_json(destination / "router_validation.json", parsed)
        v0220.write_json(destination / "provenance.json", attempt)
        attempts.append(attempt)
        if parsed.get("valid"):
            return parsed, attempts
        prior_feedback = str(parsed.get("reason") or "invalid router record")
    assert parsed is not None
    return parsed, attempts


def injection_cue(
    *,
    problem: v0220.Problem,
    initial_candidate: str,
    router_parse: Mapping[str, Any],
    event: Mapping[str, Any] | None,
    round_index: int,
) -> str:
    if event is not None:
        evidence = f"""MODEL-EMITTED ROUTER CALL
{json.dumps(event['model_call'], ensure_ascii=False, sort_keys=True)}

EXACT VALIDATOR-GATED RESULT
{json.dumps(event['execution'], ensure_ascii=False, sort_keys=True)}"""
    else:
        evidence = f"""The separate Gemma router emitted no executable tool call.
ROUTER DECISION
{json.dumps(dict(router_parse), ensure_ascii=False, sort_keys=True)}
Do not pretend that a tool ran."""
    return f"""Wait. Keep thinking; use viable intermediate results to bridge the major
gap in the global solve of {problem.problem_id}. This is semantic budget-forcing
round {round_index} inside the original solver thought trace.

ORIGINAL PROBLEM
{problem.statement}

INITIAL CANDIDATE (untrusted)
{initial_candidate.strip()}

{evidence}

Audit the central argument. Use an exact result only for the mathematical claim it
actually establishes, derive its inputs from the hypotheses, and reconnect it to
the theorem. Repair false assumptions rather than polishing them. Close the thought
channel with a substantially improved complete proof; output only that proof."""


def compact_generation(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in {"content", "accumulated_reasoning", "bridge_parse", "forcing_cue"}
    }


def run_problem(
    *,
    source_run: Path,
    problem_id: str,
    destination: Path,
    config: Mapping[str, Any],
    endpoint: str,
) -> dict[str, Any]:
    problem, source, source_link = load_linked_source(source_run, problem_id)
    problem_dir = destination / problem_id
    v0220.write_json(
        problem_dir / "input/problem.json",
        {
            "problem_id": problem.problem_id,
            "statement": problem.statement,
            "source_path": str(problem.source_path),
            "statement_sha256": sha256_text(problem.statement),
            "gold_or_reference_included": False,
        },
    )
    v0220.write_json(problem_dir / "source_link.json", source_link)
    router_parse, router_attempts = run_router(
        problem=problem,
        source=source,
        problem_dir=problem_dir,
        config=config,
        endpoint=endpoint,
    )

    operations = tuple(str(value) for value in config["allowed_tools"])
    event: dict[str, Any] | None = None
    if router_parse.get("valid") and router_parse.get("call_requested"):
        execution = v0220.execute_model_call(
            parsed={
                "valid": True,
                "call": router_parse["call"],
                "call_sha256": router_parse["call_sha256"],
            },
            problem=problem,
            run_id=destination.name,
            event_index=1,
            registry=build_registry(operations),
            timeout_sec=int(config["tool_timeout_sec"]),
            memory_mb=int(config["tool_memory_mb"]),
        )
        event = {
            "event_index": 1,
            "provenance": "separate_gemma_router_emitted_validated_then_orchestrator_executed",
            "router_attempt_index": len(router_attempts),
            "model_call": router_parse["call"],
            "model_call_sha256": router_parse["call_sha256"],
            "fit_rationale": router_parse.get("fit_rationale"),
            "validation": {"valid": True, "allowlisted": True},
            "orchestrator_plan": execution["plan"],
            "execution": execution["execution"],
        }
        event_dir = problem_dir / "tool_events/event_01"
        v0220.write_json(event_dir / "model_call.json", router_parse["call"])
        v0220.write_json(event_dir / "orchestrator_plan.json", execution["plan"])
        v0220.write_json(event_dir / "raw_evidence.json", execution["evidence"])
        v0220.write_json(event_dir / "result.json", event)

    accumulated = str(source["reasoning"])
    latest_visible = str(source["content"])
    generations: list[dict[str, Any]] = []
    for round_index in range(1, int(config["budget_rounds"]) + 1):
        cue = injection_cue(
            problem=problem,
            initial_candidate=str(source["content"]),
            router_parse=router_parse,
            event=event,
            round_index=round_index,
        )
        row = v0220.v0184.run_forcing_step(
            endpoint=endpoint,
            destination=problem_dir / "same_trace",
            step=round_index,
            source=dict(source),
            accumulated_reasoning=accumulated,
            max_tokens=int(config["continuation_max_tokens"]),
            temperature=float(source["temperature"]),
            top_p=float(source["top_p"]),
            top_k=int(source["top_k"]),
            timeout_seconds=int(config["model_timeout_sec"]),
            cue=cue,
        )
        accumulated = str(row["accumulated_reasoning"])
        if str(row["content"]).strip():
            latest_visible = str(row["content"]).strip()
        generations.append(compact_generation(row))

    proof_cue = v0220.whole_proof_cue(
        problem,
        str(source["content"]),
        latest_visible,
        [event] if event is not None else [],
        "constrained_router_tool_budget",
    )
    final = v0220.v0184.run_forcing_step(
        endpoint=endpoint,
        destination=problem_dir / "same_trace",
        step=int(config["budget_rounds"]) + 1,
        source=dict(source),
        accumulated_reasoning=accumulated,
        max_tokens=int(config["rewrite_max_tokens"]),
        temperature=float(source["temperature"]),
        top_p=float(source["top_p"]),
        top_k=int(source["top_k"]),
        timeout_seconds=int(config["model_timeout_sec"]),
        cue=proof_cue,
    )
    proof = str(final["content"]).strip() or latest_visible
    generations.append(compact_generation(final))
    summary = v0220.persist_terminal(
        problem_dir,
        proof,
        {
            "schema": PROBLEM_SCHEMA,
            "state": "completed",
            "problem_id": problem.problem_id,
            "arm": "constrained_router_tool_budget",
            "linked_source": source_link,
            "router_model": str(config.get("model", MODEL)),
            "router_separate_from_solver_trace": True,
            "router_input_scope": [
                "problem",
                "v0220_initial_candidate",
                "generic_tool_catalog",
            ],
            "router_response_format": "strict_json_schema",
            "router_attempts": router_attempts,
            "router_parse": router_parse,
            "model_emitted_valid_tool_call_count": int(event is not None),
            "validated_tool_result_count": int(
                event is not None
                and event["execution"].get("validation_status") == "passed"
            ),
            "tool_events": [event] if event is not None else [],
            "same_original_solver_trace": True,
            "same_trace_semantic_budget_forcing": True,
            "mandatory_whole_proof_rewrite": True,
            "generations": generations,
            "gold_or_reference_supplied_to_router_or_solver": False,
        },
    )
    v0220.write_json(problem_dir / "result.json", summary)
    return summary


def validate_config(value: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(value)
    required = {
        "source_run",
        "problem_ids",
        "model",
        "master_seed",
        "router_temperature",
        "router_max_tokens",
        "router_attempts",
        "budget_rounds",
        "continuation_max_tokens",
        "rewrite_max_tokens",
        "allowed_tools",
        "tool_timeout_sec",
        "tool_memory_mb",
        "model_timeout_sec",
        "max_workers",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"config missing fields: {missing}")
    ids = [str(value) for value in config["problem_ids"]]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("problem_ids must be nonempty and distinct")
    if any(re.fullmatch(r"[A-Za-z0-9_.:-]{1,180}", value) is None for value in ids):
        raise ValueError("unsafe problem_id")
    operations = tuple(str(value) for value in config["allowed_tools"])
    if not operations or len(operations) != len(set(operations)):
        raise ValueError("allowed_tools must be nonempty and distinct")
    build_registry(operations)
    if not 1 <= int(config["router_attempts"]) <= 3:
        raise ValueError("router_attempts must be 1 through 3")
    if not 1 <= int(config["budget_rounds"]) <= 3:
        raise ValueError("budget_rounds must be 1 through 3")
    if not 1 <= int(config["max_workers"]) <= 4:
        raise ValueError("max_workers must be 1 through 4")
    if not 1 <= int(config["tool_timeout_sec"]) <= 120:
        raise ValueError("tool_timeout_sec must be 1 through 120")
    if not 32 <= int(config["tool_memory_mb"]) <= 2048:
        raise ValueError("tool_memory_mb must be 32 through 2048")
    for name in ("router_max_tokens", "continuation_max_tokens", "rewrite_max_tokens"):
        if not 1 <= int(config[name]) <= 64000:
            raise ValueError(f"{name} must be 1 through 64000")
    return config


def artifact_integrity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for row in rows:
        path = Path(str(row["terminal_proof"]))
        actual = sha256_text(path.read_text(encoding="utf-8").strip())
        checks.append(
            {
                "problem_id": row["problem_id"],
                "path": str(path),
                "expected_sha256": row["terminal_proof_sha256"],
                "actual_sha256": actual,
                "valid": actual == row["terminal_proof_sha256"],
            }
        )
    return {
        "checked_terminal_artifacts": len(checks),
        "all_valid": all(check["valid"] for check in checks),
        "checks": checks,
    }


def prompt_no_gold_audit(destination: Path) -> dict[str, Any]:
    """Inspect only model-bound prompt/request artifacts; never load a gold file."""

    forbidden = ("REFERENCE SOLUTION:", "math_harness_references/", "Q1_solution.txt", "Q2_solution.txt", "Q5_solution.txt")
    findings: list[dict[str, Any]] = []
    checked: list[str] = []
    for path in sorted(destination.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith((".prompt.txt", ".user_prompt.txt")):
            text = path.read_text(encoding="utf-8", errors="replace")
        elif path.name == "request.json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            text = str(payload.get("prompt") or "")
        else:
            continue
        checked.append(str(path.resolve()))
        for token in forbidden:
            if token in text:
                findings.append({"path": str(path.resolve()), "forbidden_token": token})
    return {
        "scope": "all persisted model-bound prompt and raw-completion request artifacts",
        "gold_files_loaded_by_runner": False,
        "checked_artifact_count": len(checked),
        "forbidden_tokens": list(forbidden),
        "findings": findings,
        "passed": not findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    config = validate_config(json.loads(config_path.read_text(encoding="utf-8")))
    source_run = (ROOT / str(config["source_run"])).resolve()
    problem_ids = [str(value) for value in config["problem_ids"]]
    source_links = {
        problem_id: load_linked_source(source_run, problem_id)[2]
        for problem_id in problem_ids
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "config_path": str(config_path),
        "config_sha256": sha256_text(canonical_json(config)),
        "source_run": str(source_run),
        "problem_ids": problem_ids,
        "source_links": source_links,
        "model": str(config.get("model", MODEL)),
        "endpoint": args.endpoint,
        "router": "separate Gemma call with strict JSON-schema output",
        "router_input_scope": [
            "problem",
            "v0220_initial_candidate",
            "generic_tool_catalog",
        ],
        "tool_call_credit_policy": "only strict valid model-emitted router calls",
        "execution_policy": (
            "allowlisted frozen local operations in a timeout/memory-limited child; "
            "no model code, path, command, URL, or network-capable operation"
        ),
        "same_original_solver_trace": True,
        "semantic_budget_forcing": True,
        "mandatory_whole_proof_rewrite": True,
        "gold_reference_supplied_to_gemma": False,
        "gold_reference_loaded_by_runner": False,
        "allowed_tools": list(config["allowed_tools"]),
        "config": config,
    }
    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    destination = args.output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=False)
    v0220.write_json(destination / "manifest.json", {**manifest, "created_at": v0220.utc_now()})
    v0220.write_json(
        destination / "status.json",
        {"state": "running", "stage": "constrained_router_and_generation", "updated_at": v0220.utc_now()},
    )
    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(int(config["max_workers"]), len(problem_ids))
        ) as executor:
            futures = {
                executor.submit(
                    run_problem,
                    source_run=source_run,
                    problem_id=problem_id,
                    destination=destination,
                    config=config,
                    endpoint=args.endpoint,
                ): problem_id
                for problem_id in problem_ids
            }
            by_id = {
                futures[future]: future.result()
                for future in concurrent.futures.as_completed(futures)
            }
        rows = [by_id[problem_id] for problem_id in problem_ids]
        integrity = artifact_integrity(rows)
        no_gold = prompt_no_gold_audit(destination)
        if not integrity["all_valid"]:
            raise RuntimeError("terminal artifact integrity failed")
        if not no_gold["passed"]:
            raise RuntimeError("model-bound prompt no-gold audit failed")
        valid_calls = sum(int(row["model_emitted_valid_tool_call_count"]) for row in rows)
        validated_results = sum(int(row["validated_tool_result_count"]) for row in rows)
        result = {
            "schema": RESULT_SCHEMA,
            "state": "completed",
            "harness_version": HARNESS_VERSION,
            "problem_ids": problem_ids,
            "problem_count": len(rows),
            "rows": rows,
            "model_emitted_valid_tool_call_count": valid_calls,
            "validated_tool_result_count": validated_results,
            "problems_with_valid_model_tool_call": sum(
                int(row["model_emitted_valid_tool_call_count"] > 0) for row in rows
            ),
            "conditional_on_call_problem_ids": [
                row["problem_id"]
                for row in rows
                if row["model_emitted_valid_tool_call_count"] > 0
            ],
            "intent_to_treat_problem_ids": problem_ids,
            "artifact_integrity": integrity,
            "no_gold_prompt_audit": no_gold,
            "completed_at": v0220.utc_now(),
        }
        v0220.write_json(destination / "result.json", result)
        v0220.write_json(destination / "summary.json", result)
        v0220.write_json(
            destination / "status.json",
            {"state": "completed", "stage": "integrity_and_no_gold_audited", "updated_at": v0220.utc_now()},
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        v0220.write_json(
            destination / "status.json",
            {
                "state": "failed_closed",
                "stage": "mechanical_failure",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": v0220.utc_now(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
