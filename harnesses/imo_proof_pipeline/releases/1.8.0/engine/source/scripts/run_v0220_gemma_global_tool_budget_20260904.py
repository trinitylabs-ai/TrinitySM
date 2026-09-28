#!/usr/bin/env python3
"""Generic global Olympiad solving with same-trace budget forcing and exact tools.

The experimental unit is one fresh, reference-free Gemma solve.  Its exact initial
reasoning trace is then forked into three causally interpretable arms:

* ``baseline``: the first terminal answer, with no continuation;
* ``budget_only``: semantic same-trace continuations, with tools unavailable;
* ``tool_budget``: the same trace, with a strict model-emitted tool protocol,
  allowlisted local execution, result reinjection, and semantic continuations.

Every continued arm ends in a mandatory whole-proof rewrite.  The runner never
loads reference solutions and never executes model supplied code, paths, commands,
or URLs.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_v0183_gemma_bridge_certificate_portfolio_20260904 as v0183
import scripts.run_v0184_gemma_s1_bridge_budget_forcing_20260904 as v0184
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.arguments import (
    validate_operation_arguments,
)
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.executor import ToolExecutor
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.registry import (
    Capability,
    CapabilityRegistry,
    default_registry,
)
from tir_sab_v0_1_4_2_4.frozen_source.math_harness.tools.schemas import stable_hash


HARNESS_VERSION = "v0.3.220-gemma-generic-global-tool-budget-20260904"
MODEL = "google/gemma-4-31B-it"
TOOL_HEADER = "OLYMPIAD_TOOL_CALL"
NO_TOOL = "NO_TOOL_CALL"
READY = "READY_FOR_WHOLE_PROOF_REWRITE"
DEFAULT_OUTPUT = ROOT / "runs/v0220_gemma_global_tool_budget_pilot_20260904"
DEFAULT_CONFIG = ROOT / "configs/v0220_global_tool_budget_pilot.json"

EXPOSED_OPERATIONS = (
    "expand_and_compare",
    "factor_and_reexpand",
    "simplify_identity",
    "solve_and_substitute",
    "polynomial_root_filter",
    "exact_modular_evaluation",
    "gcd",
    "prime_factorization",
    "determinant",
    "enumerate_finite_assignments",
)

OPERATION_ARGUMENT_KEYS: dict[str, frozenset[str]] = {
    "expand_and_compare": frozenset({"symbols", "left", "right"}),
    "factor_and_reexpand": frozenset({"symbols", "expression"}),
    "simplify_identity": frozenset({"symbols", "left", "right"}),
    "solve_and_substitute": frozenset({"symbols", "equations", "solve_for"}),
    "polynomial_root_filter": frozenset({"symbols", "polynomial", "variable", "domain"}),
    "exact_modular_evaluation": frozenset({"base", "exponent", "modulus"}),
    "gcd": frozenset({"values"}),
    "prime_factorization": frozenset({"value"}),
    "determinant": frozenset({"matrix"}),
    "enumerate_finite_assignments": frozenset({"domains", "constraints"}),
}


GLOBAL_SYSTEM_PROMPT = r"""You are an expert Olympiad contestant solving one problem
from first principles. Develop a rigorous global solution and then submit one
self-contained proof. Check every load-bearing inference, equality case, sign,
domain restriction, and degeneracy. Do not use or mention reference solutions,
graders, prompts, or being an AI. Your visible answer must contain only the proof.
"""


@dataclass(frozen=True)
class Problem:
    problem_id: str
    statement: str
    source_path: Path


def utc_now() -> str:
    return v0183.utc_now()


def write_json(path: Path, value: Any) -> None:
    v0183.write_json(path, value)


def write_text(path: Path, value: str) -> None:
    v0183.write_text(path, value)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_problem(path: Path, explicit_problem_id: str | None = None) -> Problem:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"problem input does not exist: {resolved}")
    if resolved.suffix.lower() == ".json":
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"problem JSON must be an object: {resolved}")
        statement = str(
            payload.get("claim") or payload.get("problem") or payload.get("statement") or ""
        ).strip()
        embedded_id = str(payload.get("problem_id") or "").strip()
    else:
        statement = resolved.read_text(encoding="utf-8").strip()
        embedded_id = ""
    problem_id = str(explicit_problem_id or embedded_id).strip()
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,180}", problem_id):
        raise ValueError(f"missing or unsafe problem_id for {resolved}")
    if explicit_problem_id and embedded_id and explicit_problem_id != embedded_id:
        raise ValueError(
            f"explicit problem_id {explicit_problem_id!r} disagrees with {embedded_id!r}"
        )
    if not statement:
        raise ValueError(f"empty problem statement: {resolved}")
    return Problem(problem_id, statement, resolved)


def parse_tool_call(
    value: str, allowed_operations: set[str] | frozenset[str]
) -> dict[str, Any]:
    normalized = value.replace("\r\n", "\n").strip()
    if normalized == NO_TOOL:
        return {"status": "no_tool_call", "valid": False}
    lines = normalized.splitlines()
    if not lines or lines[0].strip() != TOOL_HEADER:
        return {
            "status": "malformed",
            "valid": False,
            "reason": f"missing exact {TOOL_HEADER} header",
        }
    raw_json = "\n".join(lines[1:]).strip()
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as error:
        return {
            "status": "malformed",
            "valid": False,
            "reason": f"invalid JSON: {error}",
        }
    if not isinstance(payload, dict):
        return {"status": "malformed", "valid": False, "reason": "payload is not an object"}
    if set(payload) != {"operation", "claim", "arguments"}:
        return {
            "status": "malformed",
            "valid": False,
            "reason": "payload keys must be exactly operation, claim, arguments",
            "payload": payload,
        }
    operation = str(payload.get("operation") or "")
    claim = str(payload.get("claim") or "").strip()
    arguments = payload.get("arguments")
    if operation not in allowed_operations:
        return {
            "status": "rejected",
            "valid": False,
            "reason": f"operation is not allowlisted: {operation}",
            "payload": payload,
        }
    if not claim or len(claim) > 4096:
        return {
            "status": "rejected",
            "valid": False,
            "reason": "claim must contain 1 through 4096 characters",
            "payload": payload,
        }
    if not isinstance(arguments, dict):
        return {
            "status": "rejected",
            "valid": False,
            "reason": "arguments must be an object",
            "payload": payload,
        }
    unexpected_arguments = sorted(set(arguments) - OPERATION_ARGUMENT_KEYS[operation])
    if unexpected_arguments:
        return {
            "status": "rejected",
            "valid": False,
            "reason": f"unexpected argument keys: {unexpected_arguments}",
            "payload": payload,
        }
    try:
        normalized_arguments = validate_operation_arguments(operation, arguments)
    except Exception as error:
        return {
            "status": "rejected",
            "valid": False,
            "reason": f"argument validation failed: {type(error).__name__}: {error}",
            "payload": payload,
        }
    canonical = {
        "operation": operation,
        "claim": claim,
        "arguments": normalized_arguments,
    }
    return {
        "status": "valid",
        "valid": True,
        "call": canonical,
        "call_sha256": stable_hash(canonical),
    }


def tool_protocol(operations: tuple[str, ...]) -> str:
    summaries = {
        "expand_and_compare": "exactly expand and compare two polynomial expressions",
        "factor_and_reexpand": "factor one exact expression and independently re-expand it",
        "simplify_identity": "compare two rational expressions by together/cancel",
        "solve_and_substitute": "solve bounded exact equations and substitute every solution",
        "polynomial_root_filter": "solve one polynomial and filter roots by a stated domain",
        "exact_modular_evaluation": "compute base^exponent mod modulus exactly",
        "gcd": "compute the exact gcd of a finite integer list",
        "prime_factorization": "factor one nonzero integer exactly",
        "determinant": "compute an exact square integer determinant",
        "enumerate_finite_assignments": "exhaust a bounded product of integer domains",
    }
    rendered = "\n".join(f"- {name}: {summaries[name]}" for name in operations)
    return f"""An external exact-math service is now available. Only these operations exist:
{rendered}

To call it, close the thought channel and emit exactly:
{TOOL_HEADER}
{{"operation":"OPERATION","claim":"the precise claim being checked","arguments":{{...}}}}

The JSON must contain exactly those three keys. Never emit Python, shell, paths, or
URLs. Algebraic expressions use a safe recursive AST: integers, {{"symbol":"x"}},
{{"rational":[p,q]}}, and one-key nodes add/mul/sub/div/pow/neg/abs. Examples:
- simplify_identity: {{"symbols":["x"],"left":{{"div":[{{"sub":[{{"pow":[{{"symbol":"x"}},2]}},1]}},{{"sub":[{{"symbol":"x"}},1]}}]}},"right":{{"add":[{{"symbol":"x"}},1]}}}}
- solve_and_substitute: {{"symbols":["x"],"equations":[{{"sub":[{{"pow":[{{"symbol":"x"}},2]}},4]}}],"solve_for":["x"]}}
- polynomial_root_filter adds "variable" and "domain" (complex/real/positive/nonnegative/integer).
- gcd: {{"values":[12,18]}}; prime_factorization: {{"value":2026}};
  exact_modular_evaluation: {{"base":2,"exponent":100,"modulus":101}};
  determinant: {{"matrix":[[1,2],[3,4]]}}.

Use a tool only for a concrete load-bearing computation. If none fits, emit exactly
{NO_TOOL}."""


def initial_user_prompt(problem: Problem) -> str:
    return f"""PROBLEM ID: {problem.problem_id}

{problem.statement}

Solve the entire problem. Return one coherent, self-contained Olympiad proof."""


def budget_cue(problem: Problem, prior_visible: str, round_index: int) -> str:
    return f"""Wait. Keep thinking; use viable intermediate results to bridge the major
gap in the global solve of {problem.problem_id}. External tools are unavailable in
this arm. Audit the current candidate below, derive any missing central lemma rather
than asserting it, and close the thought channel with a stronger complete proof.

CURRENT CANDIDATE (untrusted)
{prior_visible.strip()}

This is semantic budget-forcing round {round_index}. Output only the replacement proof."""


def tool_offer_cue(problem: Problem, initial_visible: str, operations: tuple[str, ...]) -> str:
    return f"""Wait. Keep thinking; use viable intermediate results to bridge the major
gap in the global solve of {problem.problem_id}. Audit the candidate and identify one
load-bearing calculation whose exact result would materially advance the proof.

CURRENT CANDIDATE (untrusted)
{initial_visible.strip()}

{tool_protocol(operations)}"""


def tool_result_cue(event: Mapping[str, Any], next_round: int) -> str:
    return f"""Wait. The model-emitted request was executed by the allowlisted local
exact-math service. Do not infer more than the returned fields establish.

MODEL TOOL CALL
{json.dumps(event['model_call'], ensure_ascii=False, sort_keys=True)}

VALIDATED EXECUTION RESULT
{json.dumps(event['execution'], ensure_ascii=False, sort_keys=True)}

Keep thinking; use this viable intermediate result to bridge the major gap in the
global proof. If another concrete exact computation is essential, emit another
strict {TOOL_HEADER} call. Otherwise emit exactly {READY}. This is tool round
{next_round}."""


def tool_repair_cue(reason: str, operations: tuple[str, ...]) -> str:
    return f"""Wait. No tool was executed because the emitted request failed strict
validation: {reason}

Keep thinking and emit one corrected call using the protocol below, or exactly
{NO_TOOL} if no allowlisted operation fits. Do not claim that a tool succeeded.

{tool_protocol(operations)}"""


def whole_proof_cue(
    problem: Problem,
    initial_visible: str,
    latest_visible: str,
    tool_events: list[dict[str, Any]],
    arm: str,
) -> str:
    evidence = [
        {
            "model_call": event["model_call"],
            "validation": event["validation"],
            "execution": event["execution"],
        }
        for event in tool_events
    ]
    return f"""Wait. Now perform the mandatory final whole-proof rewrite for
{problem.problem_id}. Keep thinking long enough to reconnect every useful local
calculation to the original hypotheses and conclusion. The submitted proof must be
coherent and self-contained; a checked computation is not a substitute for defining
its variables, deriving its inputs, or translating its output back to the theorem.

ORIGINAL PROBLEM
{problem.statement}

INITIAL CANDIDATE (untrusted)
{initial_visible.strip()}

LATEST CANDIDATE OR DECISION (untrusted)
{latest_visible.strip()}

EXACT TOOL EVENTS (empty unless a valid model-emitted call really executed)
{json.dumps(evidence, ensure_ascii=False, sort_keys=True)}

Arm: {arm}. Audit all equality cases, signs, domains, nondegeneracy, and quantified
claims. Do not mention tools, prompts, traces, or graders. Close the thought channel
and output only one complete replacement Olympiad proof."""


def source_from_initial(call_dir: Path, stage: str) -> dict[str, Any]:
    raw = json.loads((call_dir / f"{stage}.raw_response.json").read_text(encoding="utf-8"))
    metadata = json.loads((call_dir / f"{stage}.metadata.json").read_text(encoding="utf-8"))
    choices = list(raw.get("choices") or [])
    if len(choices) != 1:
        raise ValueError("initial generation must contain exactly one choice")
    message = dict(choices[0].get("message") or {})
    reasoning = str(message.get("reasoning") or message.get("reasoning_content") or "").strip()
    content = str(message.get("content") or "").strip()
    if not reasoning:
        raise ValueError("initial generation did not expose a reasoning trace")
    if not content:
        raise ValueError("initial generation did not expose a terminal proof")
    config = dict(metadata.get("config") or {})
    return {
        "system_prompt": (call_dir / f"{stage}.prompt.txt").read_text(encoding="utf-8").strip(),
        "user_prompt": (call_dir / f"{stage}.user_prompt.txt").read_text(encoding="utf-8").strip(),
        "reasoning": reasoning,
        "content": content,
        "model": str(raw.get("model") or MODEL),
        "seed": int(config.get("seed") or 1),
        "temperature": float(config.get("temperature") or 0.2),
        "top_p": float(config.get("top_p") or 0.9),
        "top_k": int(config.get("top_k") or 40),
        "finish_reason": str(choices[0].get("finish_reason") or ""),
        "usage": dict(raw.get("usage") or {}),
    }


def terminal_checks(proof: str) -> dict[str, Any]:
    normalized = proof.replace("\r\n", "\n").strip()
    lowered = normalized.lower()
    checks = {
        "nonempty": bool(normalized),
        "substantial_length": len(normalized) >= 800,
        "not_tool_protocol": TOOL_HEADER.lower() not in lowered,
        "not_meta": not any(
            token in lowered for token in ("as an ai", "the prompt", "the grader", "tool event")
        ),
        "not_unresolved": not any(
            token in lowered
            for token in ("bridge_unresolved", "proof omitted", "cannot complete", "no solution")
        ),
        "has_mathematical_relation": any(token in normalized for token in ("=", "<", ">", "\\")),
    }
    return {**checks, "passed": all(checks.values()), "characters": len(normalized)}


def build_registry(operations: tuple[str, ...]) -> CapabilityRegistry:
    base = default_registry()
    capabilities: list[Capability] = []
    for operation in operations:
        if operation not in EXPOSED_OPERATIONS:
            raise ValueError(f"operation is not approved by this harness: {operation}")
        capabilities.append(base.get(operation))
    return CapabilityRegistry(tuple(capabilities))


def execute_model_call(
    *,
    parsed: Mapping[str, Any],
    problem: Problem,
    run_id: str,
    event_index: int,
    registry: CapabilityRegistry,
    timeout_sec: int,
    memory_mb: int,
) -> dict[str, Any]:
    if not parsed.get("valid"):
        raise ValueError("cannot execute an invalid tool call")
    call = dict(parsed["call"])
    capability = registry.get(str(call["operation"]))
    plan = {
        "run_id": run_id,
        "problem_id": problem.problem_id,
        "claim_id": f"model_call_{event_index:02d}",
        "operation": call["operation"],
        "arguments": call["arguments"],
        "assumptions": [],
        "backend_capability": capability.backend_capability,
        "timeout_sec": timeout_sec,
        "memory_limit_mb": memory_mb,
        "validator": capability.validator_name,
    }
    started = time.monotonic()
    evidence = ToolExecutor(
        registry, max_timeout_sec=timeout_sec, max_memory_limit_mb=memory_mb
    ).execute(plan, checked_claim=str(call["claim"]))
    elapsed = time.monotonic() - started
    execution = {
        "state": "completed" if evidence.get("validation_status") == "passed" else "failed_closed",
        "operation": call["operation"],
        "validation_status": evidence.get("validation_status"),
        "evidence_status": evidence.get("status"),
        "claim_match_status": "not_semantically_validated",
        "claim_match_note": (
            "The exact validator recomputes the requested operation. It does not judge "
            "whether the model's free-text claim accurately describes that result."
        ),
        "normalized_result": evidence.get("normalized_result"),
        "certificate": evidence.get("certificate"),
        "counterexample": evidence.get("counterexample"),
        "operation_hash": evidence.get("operation_hash"),
        "executor_code_hash": evidence.get("executor_code_hash"),
        "validator_code_hash": evidence.get("validator_code_hash"),
        "backend": evidence.get("backend"),
        "backend_version": evidence.get("backend_version"),
        "validator": evidence.get("validator"),
        "validator_version": evidence.get("validator_version"),
        "runtime_sec": evidence.get("runtime_sec"),
        "orchestrator_elapsed_sec": elapsed,
        "stdout": "",
        "stderr": "",
        "timeout": (evidence.get("certificate") or {}).get("failure", {}).get("reason") == "timeout",
        "network_policy": "no network-capable operation or model-supplied code is exposed",
    }
    return {"plan": plan, "evidence": evidence, "execution": execution}


def compact_generation(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in {"content", "accumulated_reasoning", "bridge_parse", "forcing_cue"}
    }


def run_initial(
    *, problem: Problem, problem_dir: Path, config: Mapping[str, Any], endpoint: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    runtime = v0183.v0176.v0167.nh_runner.ResilientModelRuntime(
        v0183.v0176.v0167.nh_runner.RuntimeConfig(
            gemma_endpoint=endpoint.rstrip("/"),
            qwen_endpoint=str(config.get("qwen_endpoint", "http://127.0.0.1:8027/v1")),
            gemma_model=str(config.get("model", MODEL)),
            qwen_model="Qwen/Qwen3.6-27B",
            master_seed=int(config["master_seed"]),
            thinking_token_budget=None,
            reasoning_effort="max",
        )
    )
    call_dir = problem_dir / "shared_initial/model_call"
    stage = "global_solve"
    generation = runtime.text(
        role="gemma",
        prompt=GLOBAL_SYSTEM_PROMPT,
        user_prompt=initial_user_prompt(problem),
        destination=call_dir,
        stage=stage,
        temperature=float(config["sampling"]["temperature"]),
        top_p=float(config["sampling"]["top_p"]),
        top_k=int(config["sampling"]["top_k"]),
        max_tokens=int(config["initial_max_tokens"]),
        seed_label=f"v0220:shared-initial:{problem.problem_id}",
    )
    source = source_from_initial(call_dir, stage)
    write_text(problem_dir / "shared_initial/terminal_proof.txt", source["content"] + "\n")
    shared = {
        "problem_id": problem.problem_id,
        "system_prompt_sha256": sha256_text(source["system_prompt"]),
        "user_prompt_sha256": sha256_text(source["user_prompt"]),
        "reasoning_sha256": sha256_text(source["reasoning"]),
        "initial_proof_sha256": sha256_text(source["content"]),
        "sampling_seed": source["seed"],
        "sampling": {
            "temperature": source["temperature"],
            "top_p": source["top_p"],
            "top_k": source["top_k"],
        },
        "generation_metadata": generation.get("metadata"),
        "terminal_checks": terminal_checks(source["content"]),
    }
    write_json(problem_dir / "shared_initial/summary.json", shared)
    return source, shared


def persist_terminal(arm_dir: Path, proof: str, provenance: Mapping[str, Any]) -> dict[str, Any]:
    normalized = proof.replace("\r\n", "\n").strip()
    terminal_path = arm_dir / "terminal_proof.txt"
    write_text(terminal_path, normalized + "\n")
    checks = terminal_checks(normalized)
    summary = {
        **dict(provenance),
        "terminal_proof": str(terminal_path.resolve()),
        "terminal_proof_sha256": sha256_text(normalized),
        "terminal_checks": checks,
    }
    write_json(arm_dir / "summary.json", summary)
    return summary


def run_budget_arm(
    *, problem: Problem, source: Mapping[str, Any], problem_dir: Path,
    config: Mapping[str, Any], endpoint: str
) -> dict[str, Any]:
    arm_dir = problem_dir / "budget_only"
    accumulated = str(source["reasoning"])
    visible = str(source["content"])
    generations: list[dict[str, Any]] = []
    step = 1
    for round_index in range(1, int(config["budget_rounds"]) + 1):
        cue = budget_cue(problem, visible, round_index)
        row = v0184.run_forcing_step(
            endpoint=endpoint, destination=arm_dir / "trace", step=step,
            source=dict(source), accumulated_reasoning=accumulated,
            max_tokens=int(config["continuation_max_tokens"]),
            temperature=float(source["temperature"]), top_p=float(source["top_p"]),
            top_k=int(source["top_k"]), timeout_seconds=int(config["model_timeout_sec"]),
            cue=cue,
        )
        accumulated = str(row["accumulated_reasoning"])
        if str(row["content"]).strip():
            visible = str(row["content"])
        generations.append(compact_generation(row))
        step += 1
    cue = whole_proof_cue(problem, str(source["content"]), visible, [], "budget_only")
    final = v0184.run_forcing_step(
        endpoint=endpoint, destination=arm_dir / "trace", step=step,
        source=dict(source), accumulated_reasoning=accumulated,
        max_tokens=int(config["rewrite_max_tokens"]),
        temperature=float(source["temperature"]), top_p=float(source["top_p"]),
        top_k=int(source["top_k"]), timeout_seconds=int(config["model_timeout_sec"]),
        cue=cue,
    )
    proof = str(final["content"]).strip() or visible
    generations.append(compact_generation(final))
    return persist_terminal(arm_dir, proof, {
        "schema": "cognitive-well-v0220-arm-result-v1", "state": "completed",
        "arm": "budget_only", "same_initial_trace": True,
        "same_trace_budget_forcing": True, "external_tools_available": False,
        "mandatory_whole_proof_rewrite": True, "generations": generations,
        "tool_events": [], "model_emitted_valid_tool_call_count": 0,
    })


def run_tool_arm(
    *, problem: Problem, source: Mapping[str, Any], problem_dir: Path,
    config: Mapping[str, Any], endpoint: str, run_id: str
) -> dict[str, Any]:
    arm_dir = problem_dir / "tool_budget"
    operations = tuple(str(value) for value in config["allowed_tools"])
    registry = build_registry(operations)
    accumulated = str(source["reasoning"])
    latest_visible = str(source["content"])
    generations: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    rejected_calls: list[dict[str, Any]] = []
    step = 1
    cue = tool_offer_cue(problem, latest_visible, operations)
    row = v0184.run_forcing_step(
        endpoint=endpoint, destination=arm_dir / "trace", step=step,
        source=dict(source), accumulated_reasoning=accumulated,
        max_tokens=int(config["continuation_max_tokens"]),
        temperature=float(source["temperature"]), top_p=float(source["top_p"]),
        top_k=int(source["top_k"]), timeout_seconds=int(config["model_timeout_sec"]),
        cue=cue,
    )
    accumulated = str(row["accumulated_reasoning"])
    pending = str(row["content"]).strip()
    generations.append(compact_generation(row))
    step += 1
    repair_used = False
    while len(events) < int(config["max_tool_rounds"]):
        parsed = parse_tool_call(pending, frozenset(operations))
        parse_dir = arm_dir / "model_calls" / f"event_{len(events) + len(rejected_calls) + 1:02d}"
        write_text(parse_dir / "model_emitted_call.txt", pending + ("\n" if pending else ""))
        write_json(parse_dir / "validation.json", parsed)
        if not parsed.get("valid"):
            if parsed.get("status") in {"malformed", "rejected"}:
                rejected_calls.append(parsed)
                if not repair_used:
                    repair_used = True
                    cue = tool_repair_cue(str(parsed.get("reason")), operations)
                    row = v0184.run_forcing_step(
                        endpoint=endpoint, destination=arm_dir / "trace", step=step,
                        source=dict(source), accumulated_reasoning=accumulated,
                        max_tokens=int(config["continuation_max_tokens"]),
                        temperature=float(source["temperature"]), top_p=float(source["top_p"]),
                        top_k=int(source["top_k"]),
                        timeout_seconds=int(config["model_timeout_sec"]), cue=cue,
                    )
                    accumulated = str(row["accumulated_reasoning"])
                    pending = str(row["content"]).strip()
                    generations.append(compact_generation(row))
                    step += 1
                    continue
            if pending and pending not in {NO_TOOL, READY}:
                latest_visible = pending
            break
        execution = execute_model_call(
            parsed=parsed, problem=problem, run_id=run_id, event_index=len(events) + 1,
            registry=registry, timeout_sec=int(config["tool_timeout_sec"]),
            memory_mb=int(config["tool_memory_mb"]),
        )
        event = {
            "event_index": len(events) + 1,
            "provenance": "model_emitted_validated_then_orchestrator_executed",
            "model_call": parsed["call"],
            "model_call_sha256": parsed["call_sha256"],
            "validation": {"valid": True, "allowlisted": True},
            "orchestrator_plan": execution["plan"],
            "execution": execution["execution"],
        }
        event_dir = arm_dir / "tool_events" / f"event_{len(events) + 1:02d}"
        write_json(event_dir / "model_call.json", parsed["call"])
        write_json(event_dir / "orchestrator_plan.json", execution["plan"])
        write_json(event_dir / "raw_evidence.json", execution["evidence"])
        write_json(event_dir / "result.json", event)
        events.append(event)
        cue = tool_result_cue(event, len(events) + 1)
        row = v0184.run_forcing_step(
            endpoint=endpoint, destination=arm_dir / "trace", step=step,
            source=dict(source), accumulated_reasoning=accumulated,
            max_tokens=int(config["continuation_max_tokens"]),
            temperature=float(source["temperature"]), top_p=float(source["top_p"]),
            top_k=int(source["top_k"]), timeout_seconds=int(config["model_timeout_sec"]),
            cue=cue,
        )
        accumulated = str(row["accumulated_reasoning"])
        pending = str(row["content"]).strip()
        generations.append(compact_generation(row))
        step += 1
        if pending == READY:
            break
    if pending and pending not in {NO_TOOL, READY} and not pending.startswith(TOOL_HEADER):
        latest_visible = pending
    cue = whole_proof_cue(problem, str(source["content"]), latest_visible, events, "tool_budget")
    final = v0184.run_forcing_step(
        endpoint=endpoint, destination=arm_dir / "trace", step=step,
        source=dict(source), accumulated_reasoning=accumulated,
        max_tokens=int(config["rewrite_max_tokens"]),
        temperature=float(source["temperature"]), top_p=float(source["top_p"]),
        top_k=int(source["top_k"]), timeout_seconds=int(config["model_timeout_sec"]),
        cue=cue,
    )
    proof = str(final["content"]).strip() or latest_visible
    generations.append(compact_generation(final))
    return persist_terminal(arm_dir, proof, {
        "schema": "cognitive-well-v0220-arm-result-v1", "state": "completed",
        "arm": "tool_budget", "same_initial_trace": True,
        "same_trace_budget_forcing": True, "external_tools_available": True,
        "mandatory_whole_proof_rewrite": True, "generations": generations,
        "tool_events": events, "rejected_model_calls": rejected_calls,
        "model_emitted_valid_tool_call_count": len(events),
        "validated_tool_result_count": sum(
            event["execution"].get("validation_status") == "passed" for event in events
        ),
    })


def run_problem(
    *, problem: Problem, destination: Path, config: Mapping[str, Any], endpoint: str
) -> dict[str, Any]:
    problem_dir = destination / problem.problem_id
    write_json(problem_dir / "input/problem.json", {
        "problem_id": problem.problem_id, "statement": problem.statement,
        "source_path": str(problem.source_path), "statement_sha256": sha256_text(problem.statement),
        "gold_or_reference_included": False,
    })
    source, shared = run_initial(
        problem=problem, problem_dir=problem_dir, config=config, endpoint=endpoint
    )
    baseline = persist_terminal(problem_dir / "baseline", str(source["content"]), {
        "schema": "cognitive-well-v0220-arm-result-v1", "state": "completed",
        "arm": "baseline", "same_initial_trace": True,
        "same_trace_budget_forcing": False, "external_tools_available": False,
        "mandatory_whole_proof_rewrite": False, "generations": [], "tool_events": [],
        "model_emitted_valid_tool_call_count": 0,
    })
    budget = run_budget_arm(
        problem=problem, source=source, problem_dir=problem_dir, config=config, endpoint=endpoint
    )
    tool = run_tool_arm(
        problem=problem, source=source, problem_dir=problem_dir, config=config,
        endpoint=endpoint, run_id=destination.name,
    )
    result = {
        "problem_id": problem.problem_id,
        "shared_initial": shared,
        "causal_invariant": {
            "identical_initial_prompt": True,
            "identical_initial_sampling_seed": True,
            "identical_initial_reasoning_sha256": shared["reasoning_sha256"],
            "fork_point": "after first terminal proof",
        },
        "arms": {"baseline": baseline, "budget_only": budget, "tool_budget": tool},
    }
    write_json(problem_dir / "result.json", result)
    return result


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(payload)
    required = {
        "problems", "master_seed", "sampling", "initial_max_tokens",
        "continuation_max_tokens", "rewrite_max_tokens", "budget_rounds",
        "max_tool_rounds", "allowed_tools", "tool_timeout_sec", "tool_memory_mb",
        "model_timeout_sec", "max_workers",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"config is missing fields: {missing}")
    if not isinstance(config["problems"], list) or not config["problems"]:
        raise ValueError("config.problems must be a nonempty list")
    operations = tuple(str(value) for value in config["allowed_tools"])
    if not operations or len(operations) != len(set(operations)):
        raise ValueError("allowed_tools must contain distinct operations")
    build_registry(operations)
    if not 1 <= int(config["budget_rounds"]) <= 4:
        raise ValueError("budget_rounds must be 1 through 4")
    if not 1 <= int(config["max_tool_rounds"]) <= 4:
        raise ValueError("max_tool_rounds must be 1 through 4")
    if not 1 <= int(config["max_workers"]) <= 4:
        raise ValueError("max_workers must be 1 through 4")
    if not 1 <= int(config["tool_timeout_sec"]) <= 120:
        raise ValueError("tool_timeout_sec must be 1 through 120")
    if not 32 <= int(config["tool_memory_mb"]) <= 2048:
        raise ValueError("tool_memory_mb must be 32 through 2048")
    for field in ("initial_max_tokens", "continuation_max_tokens", "rewrite_max_tokens"):
        if not 1 <= int(config[field]) <= 64_000:
            raise ValueError(f"{field} must be 1 through 64000")
    return config


def artifact_integrity(destination: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for row in rows:
        for arm_name, arm in row["arms"].items():
            path = Path(str(arm["terminal_proof"]))
            text = path.read_text(encoding="utf-8").strip()
            actual = sha256_text(text)
            checks.append({
                "problem_id": row["problem_id"], "arm": arm_name,
                "path": str(path), "expected_sha256": arm["terminal_proof_sha256"],
                "actual_sha256": actual, "valid": actual == arm["terminal_proof_sha256"],
            })
    return {
        "checked_terminal_artifacts": len(checks),
        "all_valid": all(item["valid"] for item in checks),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--problem", type=Path, action="append", default=[])
    parser.add_argument("--problem-id", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    config = validate_config(json.loads(config_path.read_text(encoding="utf-8")))
    if args.problem:
        if args.problem_id and len(args.problem_id) != len(args.problem):
            raise ValueError("repeat --problem-id once per --problem, or omit for JSON inputs")
        problems = [
            load_problem(path, args.problem_id[index] if args.problem_id else None)
            for index, path in enumerate(args.problem)
        ]
    else:
        problems = [
            load_problem(
                ROOT / str(item["path"]),
                str(item.get("problem_id") or "") or None,
            )
            for item in config["problems"]
        ]
    if len({problem.problem_id for problem in problems}) != len(problems):
        raise ValueError("problem IDs must be unique")
    manifest = {
        "schema": "cognitive-well-v0220-global-tool-budget-manifest-v1",
        "state": "validated", "harness_version": HARNESS_VERSION,
        "config_path": str(config_path), "config_sha256": sha256_text(
            json.dumps(config, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        ),
        "problem_ids": [problem.problem_id for problem in problems],
        "problem_sources": [str(problem.source_path) for problem in problems],
        "model": str(config.get("model", MODEL)), "endpoint": args.endpoint,
        "arms": ["baseline", "budget_only", "tool_budget"],
        "shared_initial_solve_across_arms": True,
        "gold_reference_supplied_to_gemma": False,
        "tool_call_credit_policy": "only strict valid model-emitted calls",
        "tool_execution_policy": "allowlisted structured local operations only; no code, paths, URLs, shell, or network capability",
        "allowed_tools": list(config["allowed_tools"]),
        "semantic_budget_forcing": True,
        "mandatory_whole_proof_rewrite_for_continued_arms": True,
        "config": config,
    }
    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    destination = args.output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "manifest.json", {**manifest, "created_at": utc_now()})
    write_json(destination / "status.json", {
        "state": "running", "stage": "multi_problem_generation", "updated_at": utc_now()
    })
    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(int(config["max_workers"]), len(problems))
        ) as executor:
            futures = {
                executor.submit(
                    run_problem, problem=problem, destination=destination,
                    config=config, endpoint=args.endpoint,
                ): problem.problem_id
                for problem in problems
            }
            by_id = {
                futures[future]: future.result()
                for future in concurrent.futures.as_completed(futures)
            }
        rows = [by_id[problem.problem_id] for problem in problems]
        integrity = artifact_integrity(destination, rows)
        if not integrity["all_valid"]:
            raise RuntimeError("terminal artifact hash integrity failed")
        valid_calls = sum(
            row["arms"]["tool_budget"]["model_emitted_valid_tool_call_count"]
            for row in rows
        )
        tool_problem_count = sum(
            row["arms"]["tool_budget"]["model_emitted_valid_tool_call_count"] > 0
            for row in rows
        )
        result = {
            "schema": "cognitive-well-v0220-global-tool-budget-result-v1",
            "state": "completed", "harness_version": HARNESS_VERSION,
            "problems": rows, "problem_count": len(rows),
            "model_emitted_valid_tool_call_count": valid_calls,
            "problems_with_valid_model_tool_call": tool_problem_count,
            "conditional_on_call_problem_ids": [
                row["problem_id"] for row in rows
                if row["arms"]["tool_budget"]["model_emitted_valid_tool_call_count"] > 0
            ],
            "intent_to_treat_problem_ids": [row["problem_id"] for row in rows],
            "artifact_integrity": integrity, "completed_at": utc_now(),
        }
        write_json(destination / "result.json", result)
        write_json(destination / "summary.json", result)
        write_json(destination / "status.json", {
            "state": "completed", "stage": "terminal_artifacts_validated", "updated_at": utc_now()
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        write_json(destination / "status.json", {
            "state": "failed_closed", "stage": "mechanical_failure",
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(), "updated_at": utc_now(),
        })
        raise


if __name__ == "__main__":
    raise SystemExit(main())
