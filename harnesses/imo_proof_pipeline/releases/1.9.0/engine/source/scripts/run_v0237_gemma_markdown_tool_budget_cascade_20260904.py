#!/usr/bin/env python3
"""Markdown-native Gemma tool routing plus budget-forced global proof synthesis.

Every model-visible record uses fixed Markdown headings.  Tool arguments use a
small fenced S-expression DSL parsed fail-closed by ``v0236_markdown_protocol``.
The OpenAI-compatible HTTP transport and frozen exact executor necessarily use
in-memory mappings; neither representation is saved or shown to Gemma.  Persisted
prompts, responses, evidence, audits, manifests, and reports are Markdown or text.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json  # Only the loopback HTTP transport envelope; never a model-facing record.
import re
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_v0184_gemma_s1_bridge_budget_forcing_20260904 as v0184
import scripts.run_v0220_gemma_global_tool_budget_20260904 as v0220
import scripts.run_v0221_gemma_constrained_tool_router_budget_20260904 as v0221
import scripts.v0236_markdown_protocol as mdp


HARNESS_VERSION = "v0.3.237-gemma-markdown-retry-safe-global-resynthesis-20260904"
DEFAULT_CONFIG = ROOT / "configs/v0237_markdown_high_recall_cascade.md"
DEFAULT_PREREG = ROOT / "configs/v0237_markdown_router_preregistration.md"
DEFAULT_OUTPUT = ROOT / "runs/v0237_gemma_markdown_tool_budget_cascade_20260904"
SEED_NAMESPACE = "v0237-markdown-retry-safe"


AUDITOR_SYSTEM = """You are the skeptical pre-tool proof auditor in a generic
Olympiad solver. You receive only the original theorem and an untrusted initial
candidate. Snapshot the theorem-level goal and its proof obligations. Then extract
zero to three atomic, load-bearing claims or missing intermediate facts checkable by
safe exact arithmetic, algebra, finite enumeration, or a bounded exact polynomial
system.

Use high recall: include an unchecked exact computation when certifying it materially
supports the theorem. Do not invent its value. Do not list a conceptual or infinite
argument merely to force a call. You do not know evaluator labels or a reference
solution. Emit only this exact Markdown template, using one line per value:

# Theorem Goal

one-line goal

# Proof Obligations

- O1: first obligation
- O2: second obligation

# Checkable Claims

## C1
- Claim: atomic claim or missing fact
- Why load-bearing: connection to an obligation
- Desired exact fact: exact fact that should be returned

Continue sequentially through C3 at most. If there is no suitable claim, write NONE
alone under Checkable Claims. Do not use code fences, braces, JSON, or extra headings."""


MATCHER_SYSTEM = """You are a separate operation matcher in a generic Olympiad
solver. Match one immutable skeptical-auditor item to one allowlisted exact operation
or no tool. Choose CALL_TOOL only when an operation directly checks the desired fact
and materially supports the original proof. Choose NO_TOOL for conceptual, infinite,
routine, or unrepresentable facts. Do not broaden the claim or invent a result.

Emit only this exact Markdown template with one-line values:

# Decision

CALL_TOOL or NO_TOOL

# Operation

one allowlisted name, or none

# Immutable Claim

copy the desired exact fact exactly, or NONE

# Fit Rationale

one-line rationale

Do not use code fences, braces, JSON, or extra headings."""


COMPILER_SYSTEM = """You are a typed argument compiler. The operation and claim are
immutable. Derive every argument from the supplied problem, candidate, and records.
Emit only a # Tool Arguments heading and one fenced tool-args block in the selected
operation's line-oriented DSL. Never add prose, braces, JSON, code, paths, or a
claimed result. Mathematical expressions use only the supplied S-expression grammar."""


BRIDGE_SYSTEM = """You are the global proof-bridge planner. You receive the original
theorem, its pre-call obligation ledger, an untrusted initial proof, and immutable
validator-gated exact events written as Markdown facts. Map every event to a checked
lemma, downstream original obligations, and the original conclusion. Decide what
sound earlier reasoning to preserve and what gapped reasoning to replace. Plan one
standalone whole proof, never a local computation worksheet.

Emit only this exact Markdown structure:

# Event Bridges

## Event 1
- Checked lemma: one-line lemma justified by the returned facts
- Downstream obligations: O1; O2
- Connection to original conclusion: one-line connection

Include every supplied event exactly once.

# Preserve Reasoning

- one-line item

# Replace Reasoning

- one-line item

# Global Completion Plan

1. first proof step
2. second proof step

Use NONE for an empty Preserve or Replace section. Do not use code fences, braces,
JSON, or extra headings. Never invent a stronger fact than the returned Markdown."""


PROOF_AUDITOR_SYSTEM = """You are a gold-free theorem-level completion auditor.
Assess the submitted proof only against the original theorem, the pre-call obligation
ledger, and any verified exact-event Markdown. Check that it is one self-contained
whole proof, answers every requested output, uses every relevant verified fact
causally toward the conclusion, handles completeness and equality cases when needed,
and contains no process meta-language. Do not repair the proof.

Emit only this exact Markdown template:

# Whole-Proof Audit

- Whole proof: PASS or FAIL
- All original outputs answered: PASS or FAIL
- Verified results causally used: PASS or FAIL
- Completion and equality cases handled: PASS or FAIL
- Sound reasoning preserved or replaced: PASS or FAIL
- No meta or local worksheet: PASS or FAIL

# Issues

- one-line issue

Write NONE under Issues if empty. Do not use code fences, braces, JSON, or extra
headings. If no verified event exists, Verified results causally used is PASS as not
applicable. Never use a reference solution."""


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def stable_seed(master_seed: int, label: str) -> int:
    material = f"{SEED_NAMESPACE}:{master_seed}:{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


def require_loopback(endpoint: str) -> str:
    normalized = endpoint.rstrip("/")
    parsed = urllib.parse.urlparse(normalized)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("only a loopback model endpoint is allowed")
    if not parsed.path.endswith("/v1"):
        raise ValueError("model endpoint must end in /v1")
    return normalized


def transport_post(url: str, body: Mapping[str, Any], timeout: int) -> Mapping[str, Any]:
    """Use the endpoint's required transport encoding without persisting it."""

    request = urllib.request.Request(
        url,
        data=json.dumps(dict(body), ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer EMPTY", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"loopback HTTP {error.code}: {detail[:2000]}") from error
    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, Mapping):
        raise RuntimeError("loopback endpoint returned a non-mapping envelope")
    return parsed


def response_parts(raw: Mapping[str, Any]) -> tuple[str, str, str, Mapping[str, Any]]:
    choices = list(raw.get("choices") or [])
    if len(choices) != 1:
        raise RuntimeError("expected exactly one model choice")
    choice = choices[0]
    message = dict(choice.get("message") or {})
    content = str(message.get("content") or "").strip()
    reasoning = str(message.get("reasoning") or message.get("reasoning_content") or "").strip()
    finish = str(choice.get("finish_reason") or "")
    usage = raw.get("usage") if isinstance(raw.get("usage"), Mapping) else {}
    return content, reasoning, finish, usage


def metadata_markdown(
    *, stage: str, seed: int, finish: str, usage: Mapping[str, Any], latency: float
) -> str:
    selected = {
        "Stage": stage,
        "Seed": seed,
        "Finish reason": finish,
        "Prompt tokens": usage.get("prompt_tokens", "unknown"),
        "Completion tokens": usage.get("completion_tokens", "unknown"),
        "Latency seconds": f"{latency:.3f}",
        "Transport envelope persisted": "no",
        "Visible record format": "Markdown",
    }
    return mdp.render_key_values("Generation Metadata", selected)


def markdown_chat_call(
    *,
    endpoint: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    destination: Path,
    stage: str,
    temperature: float,
    thinking_budget: int,
    max_tokens: int,
    seed: int,
    timeout: int,
) -> tuple[str, str, str]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": max_tokens,
        "seed": seed,
        "chat_template_kwargs": {"enable_thinking": True},
        "thinking_token_budget": thinking_budget,
        "reasoning_effort": "max",
        "repetition_detection": {"min_pattern_size": 8, "max_pattern_size": 128, "min_count": 3},
    }
    mdp.write_text(destination / "system_prompt.md", system_prompt)
    mdp.write_text(destination / "user_prompt.md", user_prompt)
    started = time.perf_counter()
    raw = transport_post(endpoint + "/chat/completions", body, timeout)
    latency = time.perf_counter() - started
    content, reasoning, finish, usage = response_parts(raw)
    mdp.write_text(destination / "reasoning.txt", reasoning or "NO EXPOSED REASONING")
    mdp.write_text(destination / "response.md", content or "NO VISIBLE RESPONSE")
    mdp.write_text(
        destination / "metadata.md",
        metadata_markdown(
            stage=stage, seed=seed, finish=finish, usage=usage, latency=latency
        ),
    )
    return content, reasoning, finish


def run_markdown_attempts(
    *,
    endpoint: str,
    config: Mapping[str, Any],
    role: str,
    system_prompt: str,
    user_prompt: str,
    destination: Path,
    seed_label: str,
    parser: Callable[[str], Any],
) -> tuple[Any | None, list[dict[str, Any]], str | None]:
    attempts: list[dict[str, Any]] = []
    feedback = ""
    last_error: str | None = None
    for attempt_index in range(1, int(config[f"{role}_attempts"]) + 1):
        current_user = user_prompt
        if feedback:
            current_user += (
                "\n\n# Prior Strict Validation Failure\n\n"
                + feedback.replace("\n", " ")[:2000]
                + "\n\nThe prior response did not execute. Emit a complete replacement in the exact Markdown template."
            )
        call_dir = destination / f"attempt_{attempt_index:02d}"
        seed = stable_seed(int(config["master_seed"]), f"{seed_label}:{attempt_index}")
        try:
            content, _, finish = markdown_chat_call(
                endpoint=endpoint,
                model=str(config["model"]),
                system_prompt=system_prompt,
                user_prompt=current_user,
                destination=call_dir,
                stage=role,
                temperature=float(config[f"{role}_temperature"]),
                thinking_budget=int(config[f"{role}_thinking_token_budget"]),
                max_tokens=int(config[f"{role}_max_tokens"]),
                seed=seed,
                timeout=int(config["model_timeout_sec"]),
            )
            if finish in {"length", "repetition"} or not content:
                raise ValueError(f"unaccepted finish reason {finish!r} or empty response")
            parsed = parser(content)
            validation = "PASS"
            last_error = None
        except Exception as error:
            parsed = None
            validation = "FAIL"
            last_error = f"{type(error).__name__}: {error}"
        attempt = {
            "attempt": attempt_index,
            "seed": seed,
            "validation": validation,
            "error": last_error or "none",
        }
        attempts.append(attempt)
        mdp.write_text(
            call_dir / "validation.md",
            mdp.render_key_values(
                "Strict Markdown Validation",
                {
                    "Attempt": attempt_index,
                    "Result": validation,
                    "Failure": last_error or "none",
                },
            ),
        )
        if parsed is not None:
            return parsed, attempts, None
        feedback = last_error or "unknown strict Markdown validation failure"
    return None, attempts, last_error


def matcher_catalog(operations: Iterable[str]) -> str:
    descriptions = {
        "expand_and_compare": "compare two exact algebraic expressions after expansion",
        "factor_and_reexpand": "factor one exact polynomial and independently re-expand it",
        "simplify_identity": "check equality of two rational algebraic expressions",
        "solve_and_substitute": "solve bounded exact polynomial equations and substitute",
        "polynomial_root_filter": "find and filter all roots of one exact polynomial",
        "exact_modular_evaluation": "compute base to a nonnegative exponent modulo a positive modulus",
        "gcd": "compute the greatest common divisor of a finite integer list",
        "prime_factorization": "factor one nonzero integer",
        "determinant": "compute the exact determinant of a square integer matrix",
        "enumerate_finite_assignments": "exhaustively filter a bounded Cartesian product by exact constraints",
        "exact_branch_system": "solve a bounded exact polynomial system whose full encoding is already derivable",
    }
    return "\n".join(f"- {name}: {descriptions[name]}" for name in operations)


EXPRESSION_GRAMMAR = """Expression grammar inside a tool-args value:

- integer: 7 or -3
- variable: (symbol x)
- rational: (rational 2 3)
- arithmetic: (add e1 e2 ...), (mul e1 e2 ...), (sub e1 e2),
  (div e1 e2), (pow e integer), (neg e), or (abs e)

No other expression form is allowed."""


def compiler_contract(operation: str) -> str:
    contracts = {
        "expand_and_compare": """operation = expand_and_compare
symbols = x, y
left = one expression
right = one expression""",
        "factor_and_reexpand": """operation = factor_and_reexpand
symbols = x
expression = one expression""",
        "simplify_identity": """operation = simplify_identity
symbols = x, y
left = one expression
right = one expression""",
        "solve_and_substitute": """operation = solve_and_substitute
symbols = x, y
equation = one expression equal to zero
equation = another expression equal to zero
solve_for = x, y""",
        "polynomial_root_filter": """operation = polynomial_root_filter
symbols = x
polynomial = one expression equal to zero
variable = x
domain = complex or real or positive or nonnegative or integer""",
        "exact_modular_evaluation": """operation = exact_modular_evaluation
base = integer
exponent = nonnegative integer
modulus = positive integer""",
        "gcd": """operation = gcd
values = comma-separated integers""",
        "prime_factorization": """operation = prime_factorization
value = nonzero integer""",
        "determinant": """operation = determinant
row = comma-separated integer row
row = next integer row""",
        "enumerate_finite_assignments": """operation = enumerate_finite_assignments
domain_values = comma-separated integers for variable index zero
domain_values = comma-separated integers for variable index one
constraint = one finite Boolean S-expression
constraint = another finite Boolean S-expression

Finite expressions additionally allow (var index), (mod e1 e2), comparisons
(eq e1 e2), (ne e1 e2), (lt e1 e2), (le e1 e2), (gt e1 e2),
(ge e1 e2), and Boolean (and b1 b2 ...), (or b1 b2 ...), (not b).""",
        "exact_branch_system": """operation = exact_branch_system
task = safe_identifier
symbols = x, y
original_equation = expression equal to zero
common_condition = nonzero :: expression
partition = exhaustive_solutions
branch_id = all_valid_roots
solve_for = x, y
output_expression = one expression
aggregate = union

The Markdown DSL exposes only an exhaustive-solutions branch; do not select this
operation if a sign partition or host-invented encoding would be needed.""",
    }
    contract = contracts[operation]
    grammar = "" if operation in {"exact_modular_evaluation", "gcd", "prime_factorization", "determinant"} else "\n\n" + EXPRESSION_GRAMMAR
    return f"```tool-args\n{contract}\n```{grammar}"


def auditor_prompt(problem: v0220.Problem, candidate: str) -> str:
    return f"""# Original Problem

{problem.statement}

# Initial Candidate

{candidate.strip()}

Snapshot every theorem obligation. Surface at most three atomic exact facts. Do not
name an operation or guess a result."""


def matcher_prompt(
    problem: v0220.Problem,
    candidate: str,
    audit_item: Mapping[str, Any],
    operations: tuple[str, ...],
) -> str:
    item = (
        f"## {audit_item['claim_id']}\n"
        f"- Claim: {audit_item['claim']}\n"
        f"- Why load-bearing: {audit_item['why_load_bearing']}\n"
        f"- Desired exact fact: {audit_item['desired_exact_fact']}"
    )
    return f"""# Original Problem

{problem.statement}

# Initial Candidate

{candidate.strip()}

# Immutable Auditor Item

{item}

# Available Exact Operations

{matcher_catalog(operations)}

Copy the Desired exact fact exactly under Immutable Claim when choosing CALL_TOOL.
If no operation exactly fits, choose NO_TOOL."""


def compiler_prompt(
    problem: v0220.Problem,
    candidate: str,
    audit_item: Mapping[str, Any],
    matcher_record: Mapping[str, Any],
) -> str:
    return f"""# Original Problem

{problem.statement}

# Initial Candidate

{candidate.strip()}

# Immutable Auditor Item

- Claim ID: {audit_item['claim_id']}
- Desired exact fact: {audit_item['desired_exact_fact']}

# Immutable Matcher Record

{mdp.render_matcher(matcher_record)}

# Selected Tool-Arguments Contract

{compiler_contract(str(matcher_record['operation']))}

Replace every descriptive placeholder with values derived from the supplied material.
Repeat only fields shown as repeatable. Emit the exact Tool Arguments template."""


def source_link_markdown(problem: v0220.Problem, link: Mapping[str, Any]) -> str:
    return mdp.render_key_values(
        "Frozen Source Link",
        {
            "Problem ID": problem.problem_id,
            "Source run": link["source_run"],
            "Source reasoning SHA-256": link["source_reasoning_sha256"],
            "Source proof SHA-256": link["source_initial_proof_sha256"],
            "Source sampling seed": link["source_sampling_seed"],
            "All source integrity checks passed": link["all_integrity_checks_passed"],
            "Gold or reference supplied": "no",
        },
    )


def exact_event_from_execution(
    *,
    event_index: int,
    claim_id: str,
    claim: str,
    operation: str,
    arguments: Mapping[str, Any],
    execution: Mapping[str, Any],
) -> dict[str, Any]:
    result = execution["execution"]
    return {
        "event_index": event_index,
        "claim_id": claim_id,
        "claim": claim,
        "operation": operation,
        "arguments": dict(arguments),
        "validation_status": str(result.get("validation_status") or "unknown"),
        "evidence_status": str(result.get("evidence_status") or "unknown"),
        "normalized_result": result.get("normalized_result"),
        "certificate": result.get("certificate"),
        "operation_hash": result.get("operation_hash"),
        "executor_code_hash": result.get("executor_code_hash"),
        "validator_code_hash": result.get("validator_code_hash"),
    }


def immutable_matcher_parser(
    audit_item: Mapping[str, Any], operations: tuple[str, ...]
) -> Callable[[str], dict[str, Any]]:
    """Compose Markdown parsing with the immutable-claim semantic boundary."""

    def parse(text: str) -> dict[str, Any]:
        parsed = mdp.parse_matcher(text, operations)
        if (
            parsed["call_requested"]
            and parsed["claim"] != audit_item["desired_exact_fact"]
        ):
            raise ValueError("matcher changed the immutable desired exact fact")
        return parsed

    return parse


def frozen_compiler_parser(operation: str) -> Callable[[str], dict[str, Any]]:
    """Compose DSL parsing and frozen semantic argument validation per attempt."""

    def parse(text: str) -> dict[str, Any]:
        parsed = mdp.parse_tool_arguments(text, operation)
        return v0221.validate_operation_arguments(operation, parsed)

    return parse


def run_claim(
    *,
    problem: v0220.Problem,
    source: Mapping[str, Any],
    audit_item: Mapping[str, Any],
    claim_dir: Path,
    config: Mapping[str, Any],
    endpoint: str,
    registry: Any,
    run_id: str,
    event_index: int,
) -> dict[str, Any]:
    operations = tuple(str(row) for row in config["allowed_tool"])
    matcher, _, matcher_error = run_markdown_attempts(
        endpoint=endpoint,
        config=config,
        role="matcher",
        system_prompt=MATCHER_SYSTEM,
        user_prompt=matcher_prompt(problem, str(source["content"]), audit_item, operations),
        destination=claim_dir / "matcher",
        seed_label=f"matcher:{problem.problem_id}:{audit_item['claim_id']}",
        parser=immutable_matcher_parser(audit_item, operations),
    )
    if matcher is None:
        return {"event": None, "matched_call": False, "error": matcher_error or "matcher failed"}
    mdp.write_text(claim_dir / "matcher_record.md", mdp.render_matcher(matcher))
    if not matcher["call_requested"]:
        return {
            "event": None,
            "matched_call": False,
            "typed_call": False,
            "error": None,
            "operation": "none",
        }
    operation = str(matcher["operation"])
    compiler, _, compiler_error = run_markdown_attempts(
        endpoint=endpoint,
        config=config,
        role="compiler",
        system_prompt=COMPILER_SYSTEM,
        user_prompt=compiler_prompt(
            problem, str(source["content"]), audit_item, matcher
        ),
        destination=claim_dir / "compiler",
        seed_label=f"compiler:{problem.problem_id}:{audit_item['claim_id']}:{operation}",
        parser=frozen_compiler_parser(operation),
    )
    if compiler is None:
        return {
            "event": None,
            "matched_call": True,
            "typed_call": False,
            "operation": operation,
            "error": compiler_error or "compiler failed",
        }
    normalized = compiler
    model_call = {
        "operation": operation,
        "claim": matcher["claim"],
        "arguments": normalized,
    }
    argument_facts = "\n".join(
        f"- {path}: {value}"
        for path, value in mdp.flatten_facts(normalized, "arguments")
    )
    model_call_markdown = (
        "# Model-Authored Tool Call\n\n"
        f"- Operation: {operation}\n"
        f"- Claim: {matcher['claim']}\n\n"
        "## Parsed Typed Arguments\n\n"
        + argument_facts
    )
    mdp.write_text(claim_dir / "model_call.md", model_call_markdown)
    call_hash = mdp.sha256_text(model_call_markdown)
    try:
        execution = v0220.execute_model_call(
            parsed={"valid": True, "call": model_call, "call_sha256": call_hash},
            problem=problem,
            run_id=run_id,
            event_index=event_index,
            registry=registry,
            timeout_sec=int(config["tool_timeout_sec"]),
            memory_mb=int(config["tool_memory_mb"]),
        )
    except Exception as error:
        message = f"exact execution failed closed: {type(error).__name__}: {error}"
        mdp.write_text(claim_dir / "failure.md", f"# Claim Pipeline Failure\n\n{message}")
        return {
            "event": None,
            "matched_call": True,
            "typed_call": True,
            "operation": operation,
            "error": message,
        }
    event = exact_event_from_execution(
        event_index=event_index,
        claim_id=str(audit_item["claim_id"]),
        claim=str(matcher["claim"]),
        operation=operation,
        arguments=normalized,
        execution=execution,
    )
    mdp.write_text(claim_dir / "execution_result.md", mdp.render_execution_event(event))
    mdp.write_text(
        claim_dir / "execution_provenance.md",
        mdp.render_key_values(
            "Execution Provenance",
            {
                "Model-authored auditor item": "yes",
                "Model-authored matcher selection": "yes",
                "Model-authored typed arguments": "yes",
                "Host mathematical repair": "no",
                "Validation status": event["validation_status"],
                "Evidence status": event["evidence_status"],
                "Operation hash": event["operation_hash"],
                "Executor code hash": event["executor_code_hash"],
                "Validator code hash": event["validator_code_hash"],
                "Network-capable model operation": "no",
            },
        ),
    )
    verified = event["validation_status"] == "passed" and event["evidence_status"] == "verified"
    return {
        "event": event if verified else None,
        "raw_event": event,
        "matched_call": True,
        "typed_call": True,
        "operation": operation,
        "error": None if verified else "execution did not produce validator-gated evidence",
    }


def events_markdown(events: list[Mapping[str, Any]]) -> str:
    if not events:
        return "# Verified Exact Events\n\nNONE"
    return "# Verified Exact Events\n\n" + "\n\n".join(
        mdp.render_execution_event(event) for event in events
    )


def bridge_prompt(
    problem: v0220.Problem,
    source: Mapping[str, Any],
    auditor: Mapping[str, Any],
    events: list[Mapping[str, Any]],
) -> str:
    return f"""# Original Problem

{problem.statement}

# Pre-Call Theorem Ledger

{mdp.render_auditor(auditor)}

# Initial Candidate

{str(source['content']).strip()}

{events_markdown(events)}

Map every exact event back through the original obligations to the theorem-level
conclusion. A local verified calculation is only an intermediate lemma."""


def synthesis_cue(
    *,
    problem: v0220.Problem,
    source: Mapping[str, Any],
    auditor: Mapping[str, Any],
    events: list[Mapping[str, Any]],
    bridge: Mapping[str, Any] | None,
    prior_proof: str,
    prior_audit: Mapping[str, Any] | None,
) -> str:
    evidence = events_markdown(events)
    bridge_text = "# Global Bridge Map\n\nNONE" if bridge is None else mdp.render_bridge(bridge)
    audit_text = "" if prior_audit is None else "\n\n" + mdp.render_proof_audit(prior_audit)
    return f"""Wait. Scope back to the whole original theorem, not merely the local
claim. Continue inside the original solver thought trace and write a single complete
replacement proof from the original hypotheses to every requested conclusion.

# Original Problem

{problem.statement}

# Pre-Call Theorem Ledger

{mdp.render_auditor(auditor)}

# Original Initial Candidate

{str(source['content']).strip()}

# Current Whole-Proof Attempt

{prior_proof.strip()}

{evidence}

{bridge_text}{audit_text}

Use each exact event only for what its returned Markdown facts establish and make
every relevant one a causal lemma before the conclusion. Preserve sound reasoning;
replace gaps. Answer all original outputs, completeness claims, converses, and
equality cases. Output no local worksheet and no discussion of tools, validators,
prompts, traces, audits, or the process. Close the thought channel and output only one
standalone whole proof in normal mathematical Markdown."""


def proof_audit_prompt(
    *,
    problem: v0220.Problem,
    auditor: Mapping[str, Any],
    events: list[Mapping[str, Any]],
    bridge: Mapping[str, Any] | None,
    proof: str,
) -> str:
    bridge_text = "# Global Bridge Map\n\nNONE" if bridge is None else mdp.render_bridge(bridge)
    return f"""# Original Problem

{problem.statement}

# Pre-Call Theorem Ledger

{mdp.render_auditor(auditor)}

{events_markdown(events)}

{bridge_text}

# Submitted Terminal Proof

{proof.strip()}

Audit at theorem level. A local calculation without the original conclusion is not a
whole proof."""


def forcing_call(
    *,
    endpoint: str,
    source: Mapping[str, Any],
    accumulated_reasoning: str,
    cue: str,
    destination: Path,
    max_tokens: int,
    seed: int,
    timeout: int,
) -> dict[str, Any]:
    raw_prompt = v0184.forced_reasoning_prompt(
        str(source["system_prompt"]),
        str(source["user_prompt"]),
        accumulated_reasoning,
        cue,
    )
    body = v0184.build_completion_request(
        model=str(source["model"]),
        raw_prompt=raw_prompt,
        max_tokens=max_tokens,
        seed=seed,
        temperature=float(source["temperature"]),
        top_p=float(source["top_p"]),
        top_k=int(source["top_k"]),
    )
    started = time.perf_counter()
    raw = transport_post(endpoint + "/completions", body, timeout)
    elapsed = time.perf_counter() - started
    completion, finish, usage = v0184.extract_completion(dict(raw))
    parsed = v0184.parse_raw_continuation(completion)
    new_reasoning = str(parsed["reasoning"])
    content = str(parsed["content"]).strip()
    next_accumulated = v0184.append_forced_reasoning(accumulated_reasoning, new_reasoning, cue)
    mdp.write_text(destination / "forcing_cue.md", cue)
    mdp.write_text(destination / "raw_continuation.txt", completion or "NO CONTINUATION")
    mdp.write_text(destination / "new_reasoning.txt", new_reasoning or "NO NEW REASONING")
    mdp.write_text(destination / "candidate_proof.md", content or "NO VISIBLE PROOF")
    mdp.write_text(
        destination / "metadata.md",
        mdp.render_key_values(
            "Same-Trace Budget-Forcing Metadata",
            {
                "Seed": seed,
                "Finish reason": finish,
                "Prompt tokens": usage.get("prompt_tokens", "unknown"),
                "Completion tokens": usage.get("completion_tokens", "unknown"),
                "Latency seconds": f"{elapsed:.3f}",
                "Thought channel closed": parsed["thought_channel_closed"],
                "Turn closed": parsed["turn_closed"],
                "Visible proof characters": len(content),
                "Transport envelope persisted": "no",
            },
        ),
    )
    accepted = bool(content) and finish not in {"length", "repetition"} and bool(
        parsed["thought_channel_closed"]
    )
    return {
        "content": content,
        "accumulated_reasoning": next_accumulated,
        "finish_reason": finish,
        "accepted": accepted,
    }


def transport_terminal_checks(proof: str) -> dict[str, bool]:
    lowered = proof.lower()
    return {
        "nonempty": bool(proof.strip()),
        "substantial_length": len(proof.strip()) >= 800,
        "has_mathematical_relation": any(token in proof for token in ("=", "<", ">", "\\")),
        "no_process_meta_language": not any(
            re.search(rf"\b{word}\b", lowered)
            for word in ("router", "validator", "prompt", "worksheet")
        ),
    }


def run_budget_only(
    *,
    problem: v0220.Problem,
    source: Mapping[str, Any],
    destination: Path,
    config: Mapping[str, Any],
    endpoint: str,
) -> dict[str, Any]:
    cue = f"""Wait. Keep thinking; use viable intermediate results to bridge the major
gap in the global solve of {problem.problem_id}. External tools are unavailable in
this arm. Audit the candidate, derive missing central lemmas rather than asserting
them, and close the thought channel with one stronger complete proof of the original
problem. Output only the replacement proof in normal mathematical Markdown.

# Current Candidate

{str(source['content']).strip()}"""
    generation = forcing_call(
        endpoint=endpoint,
        source=source,
        accumulated_reasoning=str(source["reasoning"]),
        cue=cue,
        destination=destination / "round_01",
        max_tokens=int(config["continuation_max_tokens"]),
        seed=stable_seed(int(config["master_seed"]), f"budget-only:{problem.problem_id}"),
        timeout=int(config["model_timeout_sec"]),
    )
    proof = generation["content"] if generation["accepted"] else str(source["content"])
    mdp.write_text(destination / "terminal_proof.md", proof)
    return {
        "accepted_rewrite": generation["accepted"],
        "proof_sha256": mdp.sha256_text(proof.strip()),
    }


def run_cascade(
    *,
    problem: v0220.Problem,
    source: Mapping[str, Any],
    destination: Path,
    config: Mapping[str, Any],
    endpoint: str,
    run_id: str,
) -> dict[str, Any]:
    operations = tuple(str(row) for row in config["allowed_tool"])
    registry = v0221.build_registry(operations)
    auditor, _, auditor_error = run_markdown_attempts(
        endpoint=endpoint,
        config=config,
        role="auditor",
        system_prompt=AUDITOR_SYSTEM,
        user_prompt=auditor_prompt(problem, str(source["content"])),
        destination=destination / "pre_call_auditor",
        seed_label=f"auditor:{problem.problem_id}",
        parser=lambda text: mdp.parse_auditor(text, int(config["max_audit_claims"])),
    )
    if auditor is None:
        auditor = {
            "theorem_goal": problem.statement.replace("\n", " "),
            "proof_obligations": ["Prove every conclusion requested in the original theorem."],
            "claims": [],
        }
        mdp.write_text(
            destination / "auditor_failure.md",
            f"# Auditor Failure\n\n{auditor_error or 'unknown failure'}",
        )
        auditor_valid = False
    else:
        auditor_valid = True
        mdp.write_text(destination / "pre_call_snapshot.md", mdp.render_auditor(auditor))
    claim_rows: list[dict[str, Any]] = []
    next_event_index = 1
    for audit_item in auditor["claims"]:
        row = run_claim(
            problem=problem,
            source=source,
            audit_item=audit_item,
            claim_dir=destination / "claims" / str(audit_item["claim_id"]),
            config=config,
            endpoint=endpoint,
            registry=registry,
            run_id=run_id,
            event_index=next_event_index,
        )
        claim_rows.append(row)
        if row.get("event") is not None:
            next_event_index += 1
    events = [row["event"] for row in claim_rows if row.get("event") is not None]
    bridge: Mapping[str, Any] | None = None
    bridge_error: str | None = None
    if events:
        bridge, _, bridge_error = run_markdown_attempts(
            endpoint=endpoint,
            config=config,
            role="bridge",
            system_prompt=BRIDGE_SYSTEM,
            user_prompt=bridge_prompt(problem, source, auditor, events),
            destination=destination / "global_bridge",
            seed_label=f"bridge:{problem.problem_id}",
            parser=lambda text: mdp.parse_bridge(
                text, [int(event["event_index"]) for event in events]
            ),
        )
        if bridge is not None:
            mdp.write_text(destination / "global_bridge_map.md", mdp.render_bridge(bridge))
        else:
            mdp.write_text(
                destination / "bridge_failure.md",
                f"# Global Bridge Failure\n\n{bridge_error or 'unknown failure'}",
            )
    injected_events = events if bridge is not None else []
    accumulated = str(source["reasoning"])
    latest = str(source["content"])
    latest_audit: Mapping[str, Any] | None = None
    accepted_rewrite = False
    proof_audit_error: str | None = None
    for rewrite_index in (1, 2):
        cue = synthesis_cue(
            problem=problem,
            source=source,
            auditor=auditor,
            events=injected_events,
            bridge=bridge,
            prior_proof=latest,
            prior_audit=latest_audit,
        )
        generation = forcing_call(
            endpoint=endpoint,
            source=source,
            accumulated_reasoning=accumulated,
            cue=cue,
            destination=destination / "same_trace" / f"rewrite_{rewrite_index:02d}",
            max_tokens=int(
                config["continuation_max_tokens"]
                if rewrite_index == 1
                else config["rewrite_max_tokens"]
            ),
            seed=stable_seed(
                int(config["master_seed"]), f"rewrite:{problem.problem_id}:{rewrite_index}"
            ),
            timeout=int(config["model_timeout_sec"]),
        )
        accumulated = str(generation["accumulated_reasoning"])
        if generation["accepted"]:
            latest = str(generation["content"])
            accepted_rewrite = True
        latest_audit, _, proof_audit_error = run_markdown_attempts(
            endpoint=endpoint,
            config=config,
            role="proof_audit",
            system_prompt=PROOF_AUDITOR_SYSTEM,
            user_prompt=proof_audit_prompt(
                problem=problem,
                auditor=auditor,
                events=injected_events,
                bridge=bridge,
                proof=latest,
            ),
            destination=destination / f"global_proof_audit_{rewrite_index:02d}",
            seed_label=f"proof-audit:{problem.problem_id}:{rewrite_index}",
            parser=mdp.parse_proof_audit,
        )
        if latest_audit is not None:
            mdp.write_text(
                destination / f"global_proof_audit_{rewrite_index:02d}.md",
                mdp.render_proof_audit(latest_audit),
            )
        if latest_audit is not None and latest_audit["passed"]:
            break
    terminal_checks = transport_terminal_checks(latest)
    initial_hash = mdp.sha256_text(str(source["content"]).strip())
    terminal_hash = mdp.sha256_text(latest.strip())
    bridge_indexes = sorted(
        int(row["event_index"]) for row in (bridge or {}).get("bridges", [])
    )
    event_indexes = sorted(int(event["event_index"]) for event in events)
    global_checks = {
        **terminal_checks,
        "accepted_whole_rewrite_generated": accepted_rewrite,
        "whole_rewrite_differs_from_initial": terminal_hash != initial_hash,
        "bridge_covers_every_verified_event": bridge_indexes == event_indexes,
        "every_verified_event_injected": len(injected_events) == len(events),
        "gold_free_semantic_audit_passed": bool(latest_audit and latest_audit["passed"]),
    }
    global_terminal_passed = all(global_checks.values())
    gate_required = bool(events)
    gate_checks = {
        "verified_event_exists": bool(events),
        "global_bridge_authored": bridge is not None,
        "bridge_covers_every_verified_event": global_checks[
            "bridge_covers_every_verified_event"
        ],
        "every_verified_event_injected": global_checks["every_verified_event_injected"],
        "accepted_whole_rewrite_generated": accepted_rewrite,
        "whole_rewrite_differs_from_initial": global_checks[
            "whole_rewrite_differs_from_initial"
        ],
        "semantic_whole_proof_audit_passed": global_checks[
            "gold_free_semantic_audit_passed"
        ],
        "terminal_artifact_accepted": global_terminal_passed,
    }
    gate_passed = all(gate_checks.values()) if gate_required else True
    mdp.write_text(destination / "terminal_proof.md", latest)
    mdp.write_text(
        destination / "global_terminal_audit.md",
        mdp.render_key_values(
            "Global Terminal Audit",
            {key.replace("_", " ").title(): value for key, value in global_checks.items()}
            | {"Passed": global_terminal_passed},
        ),
    )
    mdp.write_text(
        destination / "global_resynthesis_gate.md",
        mdp.render_key_values(
            "Hard Global Resynthesis Gate",
            {
                "Required": gate_required,
                **{key.replace("_", " ").title(): value for key, value in gate_checks.items()},
                "Passed": gate_passed,
                "Policy": "A verified local fact is accepted only inside a distinct audited whole proof.",
            },
        ),
    )
    return {
        "auditor_valid": auditor_valid,
        "audit_claim_count": len(auditor["claims"]),
        "matched_call_count": sum(bool(row.get("matched_call")) for row in claim_rows),
        "typed_call_count": sum(bool(row.get("typed_call")) for row in claim_rows),
        "validated_call_count": len(events),
        "operations": [str(event["operation"]) for event in events],
        "bridge_success": bridge is not None,
        "global_terminal_passed": global_terminal_passed,
        "gate_required": gate_required,
        "gate_passed": gate_passed,
        "proof_sha256": terminal_hash,
        "proof_audit_error": proof_audit_error,
        "claim_errors": [str(row["error"]) for row in claim_rows if row.get("error")],
    }


def run_problem(
    *,
    source_run: Path,
    problem_id: str,
    destination: Path,
    config: Mapping[str, Any],
    endpoint: str,
) -> dict[str, Any]:
    problem, source, link = v0221.load_linked_source(source_run, problem_id)
    problem_dir = destination / problem_id
    mdp.write_text(problem_dir / "problem.md", f"# Original Problem\n\n{problem.statement}")
    mdp.write_text(problem_dir / "source_link.md", source_link_markdown(problem, link))
    mdp.write_text(problem_dir / "baseline/terminal_proof.md", str(source["content"]))
    budget = run_budget_only(
        problem=problem,
        source=source,
        destination=problem_dir / "budget_only",
        config=config,
        endpoint=endpoint,
    )
    cascade = run_cascade(
        problem=problem,
        source=source,
        destination=problem_dir / "markdown_tool_budget",
        config=config,
        endpoint=endpoint,
        run_id=destination.name,
    )
    row = {
        "problem_id": problem_id,
        "baseline_sha256": mdp.sha256_text(str(source["content"]).strip()),
        "budget_only": budget,
        "cascade": cascade,
    }
    mdp.write_text(
        problem_dir / "result.md",
        mdp.render_key_values(
            "Problem Result",
            {
                "Problem ID": problem_id,
                "Baseline proof SHA-256": row["baseline_sha256"],
                "Budget-only proof SHA-256": budget["proof_sha256"],
                "Markdown tool-budget proof SHA-256": cascade["proof_sha256"],
                "Auditor valid": cascade["auditor_valid"],
                "Audit claim count": cascade["audit_claim_count"],
                "Matched call count": cascade["matched_call_count"],
                "Typed call count": cascade["typed_call_count"],
                "Validated call count": cascade["validated_call_count"],
                "Validated operations": ", ".join(cascade["operations"]) or "none",
                "Global bridge success": cascade["bridge_success"],
                "Global terminal audit passed": cascade["global_terminal_passed"],
                "Hard resynthesis gate required": cascade["gate_required"],
                "Hard resynthesis gate passed": cascade["gate_passed"],
                "Proof scoring performed": "no",
            },
        ),
    )
    return row


def parse_preregistration(markdown: str) -> tuple[dict[str, set[str]], set[str]]:
    positive: dict[str, set[str]] = {}
    negative: set[str] = set()
    section = ""
    for line in markdown.splitlines():
        if line == "## Expected-Call Problems":
            section = "positive"
            continue
        if line == "## Expected-No-Call Problems":
            section = "negative"
            continue
        if line.startswith("## ") and section:
            section = ""
        if section == "positive" and line.startswith("- "):
            problem_id, operations = line[2:].split(": ", 1)
            positive[problem_id] = {part.strip() for part in operations.split(" or ")}
        elif section == "negative" and line.startswith("- "):
            negative.add(line[2:].strip())
    return positive, negative


def evaluation_report(
    rows: list[Mapping[str, Any]], preregistration: str
) -> tuple[str, dict[str, Any]]:
    positive, negative = parse_preregistration(preregistration)
    by_id = {str(row["problem_id"]): row for row in rows}
    positive_hits = [
        problem_id
        for problem_id, accepted in positive.items()
        if set(by_id[problem_id]["cascade"]["operations"]) & accepted
    ]
    negative_false_calls = [
        problem_id
        for problem_id in negative
        if int(by_id[problem_id]["cascade"]["validated_call_count"]) > 0
    ]
    called = [
        str(row["problem_id"])
        for row in rows
        if int(row["cascade"]["validated_call_count"]) > 0
    ]
    called_gate_pass = [
        problem_id for problem_id in called if bool(by_id[problem_id]["cascade"]["gate_passed"])
    ]
    typed_calls = sum(int(row["cascade"]["typed_call_count"]) for row in rows)
    validated_calls = sum(int(row["cascade"]["validated_call_count"]) for row in rows)
    metrics = {
        "trigger_recall_numerator": len(positive_hits),
        "trigger_recall_denominator": len(positive),
        "no_tool_specificity_numerator": len(negative) - len(negative_false_calls),
        "no_tool_specificity_denominator": len(negative),
        "false_positive_numerator": len(negative_false_calls),
        "false_positive_denominator": len(negative),
        "called_problem_count": len(called),
        "global_resynthesis_gate_pass_count": len(called_gate_pass),
        "typed_call_count": typed_calls,
        "validated_call_count": validated_calls,
    }
    lines = [
        "# Preregistered Routing and Resynthesis Report",
        "",
        "## Metrics",
        "",
        f"- Trigger recall: {len(positive_hits)}/{len(positive)}",
        f"- No-tool specificity: {len(negative) - len(negative_false_calls)}/{len(negative)}",
        f"- False-positive rate: {len(negative_false_calls)}/{len(negative)}",
        f"- Valid execution rate: {validated_calls}/{typed_calls}",
        f"- Called problems passing hard global-resynthesis gate: {len(called_gate_pass)}/{len(called)}",
        "- External proof scoring: not run",
        "",
        "## Positive Hits",
        "",
        *(f"- {problem_id}" for problem_id in positive_hits),
        "",
        "## Negative False Calls",
        "",
        *(f"- {problem_id}" for problem_id in negative_false_calls),
        "",
        "## Interpretation Boundary",
        "",
        "Successful routing and the global-resynthesis gate are mechanism metrics, not an independent correctness score. Proof recovery remains unclaimed until separately authorized scoring is performed.",
    ]
    if not positive_hits:
        lines.insert(lines.index("## Negative False Calls") - 1, "- NONE")
    if not negative_false_calls:
        lines.insert(lines.index("## Interpretation Boundary") - 1, "- NONE")
    return "\n".join(lines), metrics


def validate_config(config: Mapping[str, Any]) -> None:
    operations = tuple(str(row) for row in config["allowed_tool"])
    v0221.build_registry(operations)
    for required in (
        "max_audit_claims",
        "max_workers",
        "model_timeout_sec",
        "tool_timeout_sec",
        "tool_memory_mb",
    ):
        if int(config[required]) <= 0:
            raise ValueError(f"configuration {required} must be positive")
    if int(config["max_audit_claims"]) != 3:
        raise ValueError("max_audit_claims must be three")
    if not 1 <= int(config["max_workers"]) <= 4:
        raise ValueError("max_workers must be one through four")
    for role in ("auditor", "matcher", "compiler", "bridge", "proof_audit"):
        if not 1 <= int(config[f"{role}_attempts"]) <= 3:
            raise ValueError(f"{role} attempts out of range")


def status_markdown(state: str, stage: str, error: str = "none") -> str:
    return mdp.render_key_values(
        "Run Status",
        {"State": state, "Stage": stage, "Error": error, "Updated at": utc_now()},
    )


def protocol_artifact_audit(destination: Path) -> str:
    persisted_json = sorted(path for path in destination.rglob("*.json") if path.is_file())
    prompt_paths = sorted(
        path
        for path in destination.rglob("*")
        if path.is_file()
        and path.name in {"system_prompt.md", "user_prompt.md", "forcing_cue.md"}
    )
    forbidden_prereg_markers = (
        "## Expected-Call Problems",
        "## Expected-No-Call Problems",
        "## Implicit Target Criterion",
        "Trigger recall:",
    )
    leaked: list[Path] = []
    for path in prompt_paths:
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in forbidden_prereg_markers):
            leaked.append(path)
    if persisted_json or leaked:
        raise RuntimeError(
            "Markdown protocol artifact audit failed: "
            f"JSON files={len(persisted_json)}, preregistration prompt leaks={len(leaked)}"
        )
    prompt_rows = "\n".join(
        f"- `{path.relative_to(destination)}`: `{mdp.sha256_text(path.read_text(encoding='utf-8'))}`"
        for path in prompt_paths
    )
    return (
        "# Markdown Protocol and No-Gold Audit\n\n"
        "- Persisted JSON artifacts: 0\n"
        f"- Gemma-facing prompt artifacts checked: {len(prompt_paths)}\n"
        "- Evaluator-preregistration markers found in Gemma prompts: 0\n"
        "- Reference or gold solution files loaded by cascade: 0\n"
        "- Model-visible executor representation: flattened Markdown facts only\n"
        "- Internal loopback transport envelope persisted: no\n"
        "- Internal exact-executor mapping injected directly: no\n"
        "- Audit passed: yes\n\n"
        "## Prompt Hashes\n\n"
        + (prompt_rows or "- NONE")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--preregistration", type=Path, default=DEFAULT_PREREG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    endpoint = require_loopback(args.endpoint)
    config_path = args.config.expanduser().resolve()
    prereg_path = args.preregistration.expanduser().resolve()
    config_text = config_path.read_text(encoding="utf-8")
    prereg_text = prereg_path.read_text(encoding="utf-8")
    config = mdp.parse_config(config_text)
    validate_config(config)
    source_run = (ROOT / str(config["source_run"])).resolve()
    problem_ids = [str(row) for row in config["problem_id"]]
    source_status = json.loads((source_run / "status.json").read_text(encoding="utf-8"))
    if source_status.get("state") != "completed":
        raise RuntimeError("source run is not sealed completed")
    source_links = {
        problem_id: v0221.load_linked_source(source_run, problem_id)[2]
        for problem_id in problem_ids
    }
    source_hash_material = "\n".join(
        f"{problem_id} {source_links[problem_id]['source_reasoning_sha256']} {source_links[problem_id]['source_initial_proof_sha256']}"
        for problem_id in problem_ids
    )
    preflight = mdp.render_key_values(
        "Markdown Cascade Preflight",
        {
            "Harness version": HARNESS_VERSION,
            "Source run": source_run,
            "Problem count": len(problem_ids),
            "Problems": ", ".join(problem_ids),
            "Allowed tools": ", ".join(str(row) for row in config["allowed_tool"]),
            "Configuration SHA-256": mdp.sha256_text(config_text),
            "Preregistration SHA-256": mdp.sha256_text(prereg_text),
            "Sealed source-link aggregate SHA-256": mdp.sha256_text(source_hash_material),
            "All eight source-link integrity checks passed": all(
                bool(link["all_integrity_checks_passed"])
                for link in source_links.values()
            ),
            "Gemma-visible protocol": "strict Markdown headings and fenced tool-args DSL",
            "Gemma-visible JSON": "none",
            "Persisted JSON artifacts": "none",
            "Internal transport mapping": "required by loopback OpenAI-compatible API and never persisted or injected",
            "Internal executor mapping": "required by frozen exact executor and rendered to Markdown facts before injection",
            "Gold or reference loaded": "no",
            "External proof scoring authorized": "no",
        },
    )
    if args.dry_run:
        print(preflight)
        return 0
    destination = args.output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=False)
    mdp.write_text(destination / "preflight.md", preflight)
    mdp.write_text(destination / "frozen_config.md", config_text)
    mdp.write_text(destination / "frozen_preregistration.md", prereg_text)
    mdp.write_text(destination / "status.md", status_markdown("running", "Markdown cascade"))
    try:
        rows: list[dict[str, Any]] = []
        failures: list[tuple[str, str]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(config["max_workers"])) as pool:
            pending = {
                pool.submit(
                    run_problem,
                    source_run=source_run,
                    problem_id=problem_id,
                    destination=destination,
                    config=config,
                    endpoint=endpoint,
                ): problem_id
                for problem_id in problem_ids
            }
            by_id: dict[str, dict[str, Any]] = {}
            for future in concurrent.futures.as_completed(pending):
                problem_id = pending[future]
                try:
                    by_id[problem_id] = future.result()
                except Exception as error:
                    message = f"{type(error).__name__}: {error}"
                    failures.append((problem_id, message))
                    mdp.write_text(
                        destination / problem_id / "failure.md",
                        f"# Failed-Closed Problem Pipeline\n\n- Problem ID: {problem_id}\n- Error: {message}\n\n```text\n{traceback.format_exc()}\n```",
                    )
            rows = [by_id[problem_id] for problem_id in problem_ids if problem_id in by_id]
        if failures:
            failure_lines = "\n".join(f"- {problem_id}: {message}" for problem_id, message in failures)
            mdp.write_text(
                destination / "failure_summary.md",
                f"# Failed-Closed Problem Pipelines\n\n{failure_lines}",
            )
            raise RuntimeError(f"{len(failures)} problem pipelines failed closed")
        report, metrics = evaluation_report(rows, prereg_text)
        mdp.write_text(destination / "evaluation_report.md", report)
        mdp.write_text(
            destination / "protocol_no_gold_audit.md",
            protocol_artifact_audit(destination),
        )
        mdp.write_text(
            destination / "summary.md",
            mdp.render_key_values(
                "Experiment Summary",
                {
                    "State": "completed",
                    "Problem count": len(rows),
                    "Auditor valid snapshots": sum(row["cascade"]["auditor_valid"] for row in rows),
                    "Audit claims": sum(int(row["cascade"]["audit_claim_count"]) for row in rows),
                    "Matched calls": sum(int(row["cascade"]["matched_call_count"]) for row in rows),
                    "Typed calls": metrics["typed_call_count"],
                    "Validator-passed calls": sum(int(row["cascade"]["validated_call_count"]) for row in rows),
                    "Trigger recall": f"{metrics['trigger_recall_numerator']}/{metrics['trigger_recall_denominator']}",
                    "No-tool specificity": f"{metrics['no_tool_specificity_numerator']}/{metrics['no_tool_specificity_denominator']}",
                    "Called problems passing global gate": f"{metrics['global_resynthesis_gate_pass_count']}/{metrics['called_problem_count']}",
                    "Prompt no-gold audit": "passed by construction and recorded source hashes",
                    "External proof scoring": "not run",
                    "Completed at": utc_now(),
                },
            ),
        )
        mdp.write_text(
            destination / "artifact_hashes.md",
            mdp.hash_manifest(
                destination,
                exclude_names=frozenset({"artifact_hashes.md", "status.md"}),
            ),
        )
        mdp.write_text(
            destination / "status.md",
            status_markdown("completed", "Markdown artifacts hashed and preregistered metrics reported"),
        )
        print((destination / "summary.md").read_text(encoding="utf-8"))
        return 0
    except Exception as error:
        mdp.write_text(
            destination / "status.md",
            status_markdown("failed_closed", "mechanical or per-problem failure", f"{type(error).__name__}: {error}"),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
