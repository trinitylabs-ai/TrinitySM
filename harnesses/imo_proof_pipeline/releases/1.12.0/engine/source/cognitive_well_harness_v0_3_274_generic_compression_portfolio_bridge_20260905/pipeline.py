from __future__ import annotations

import hashlib
import json
import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

# Importing v0260 installs mandatory one-step budget forcing and its 32k floor
# before this module captures the shared transport function.
from cognitive_well_harness_v0_3_260_v258_bf32k_floor_20260905 import (  # noqa: F401
    pipeline as v0260,
)
from experiments.local_math_verifier import runtime as transport

import scripts.run_v0220_gemma_global_tool_budget_20260904 as v0220
import scripts.run_v0221_gemma_constrained_tool_router_budget_20260904 as v0221
import scripts.run_v0237_gemma_markdown_tool_budget_cascade_20260904 as v0237
import scripts.v0236_markdown_protocol as mdp

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION
from . import exact_tools, protocol


TOKEN_CAPS = (32_768, 49_152, 65_536)
MAX_REJECTED_MARKDOWN_CHARS = 48_000
_UNFORCED_GENERATION = v0260._budget_forcing._ORIGINAL
DEFAULT_GEMMA_MODEL = "google/gemma-4-31B-it"
DEFAULT_QWEN_MODEL = "Qwen/Qwen3.6-27B"
COMPRESSION_ARM_TEMPERATURES = (
    ("t10", 0.10),
    ("t15", 0.15),
    ("t20", 0.20),
    ("t25", 0.25),
    ("t30", 0.30),
    ("t35", 0.35),
    ("t40", 0.40),
    ("t45", 0.45),
)


def formalization_schedule_records() -> list[dict[str, Any]]:
    return [
        {"label": label, "temperature": temperature}
        for label, temperature in COMPRESSION_ARM_TEMPERATURES
    ]


def formalization_schedule_sha256() -> str:
    return exact_tools.stable_hash(formalization_schedule_records())


@dataclass(frozen=True)
class Role:
    endpoint: str
    model: str
    temperature: float
    reasoning_effort: str | None


DETECTOR_SYSTEM = """You are a skeptical, problem-agnostic post-Resolver proof-gap
detector. Inspect the original theorem and the complete submitted proof. Select at
most one highest-impact load-bearing step for which exact external evidence could
materially improve a whole-proof rewrite.

The host supplies lexical nominations such as “it can be shown”, “the constraints
force”, “simplifies to”, “ensures that”, “one checks”, “after calculation”,
“similarly”, “clearly”, and related compression language. These are only search
hints. A phrase is not a defect by itself. CALL_TOOL only if the omitted or suspect
step is central, its inputs can be formalized from the theorem and proof, and an
exact result could support or falsify it. You may target a missing derivation, a
possibly false universal/intermediate assertion, an equality or identity, an
equation system, case completeness, or exact arithmetic. Prefer counterexample
search when falsification would be more informative than attempted certification.

Emit only this exact Markdown template with one paragraph per section:

# Decision

CALL_TOOL or NO_TOOL

# Load-Bearing Gap

precise submitted-proof step, or NONE

# Trigger Evidence

quote or locate the relevant proof span, or NONE

# Evidence Task

CERTIFY_DERIVATION, SEARCH_COUNTEREXAMPLE, CHECK_EQUALITY, SOLVE_EQUATIONS,
COMPLETE_CASES, EXACT_ARITHMETIC, or NONE

# Desired Exact Fact

neutral fact to compute without guessing the result, or NONE

# Downstream Obligation

how that fact reaches the original conclusion, or NONE

Do not name a tool operation, invent a tool result, use JSON, or add headings."""


MATCHER_SYSTEM = """You are a problem-agnostic exact-operation matcher. Match the
immutable detected evidence task to exactly one allowlisted operation, or NO_TOOL.
Choose an operation only when it can directly return the requested evidence from a
formalization derived from the supplied theorem and proof. Counterexample searches
must be exhaustive over a valid finite or exact algebraic domain; numerical samples
cannot certify a universal claim. Prefer polynomial_ideal_membership for proving a
target polynomial consequence of several polynomial constraints, simplify_identity
for one rational identity, expand_and_compare for a direct polynomial equality,
and exact_branch_system or enumerate_finite_assignments for exhaustive solving.

Emit only the strict # Decision, # Operation, # Immutable Claim, # Fit Rationale
Markdown template. Copy the desired exact fact byte-for-byte as Immutable Claim for
CALL_TOOL. Do not compile arguments or invent results."""


COMPILER_SYSTEM = """You are a problem-agnostic semantic compressor and typed-argument
compiler. Derive a minimal sufficient exact request only from the original theorem
and submitted proof. Do not use a reference solution or invent a mathematical
assumption. Do not mechanically transcribe every variable and relation in the proof.

First compress the formal system without weakening the requested implication:
- substitute away purely definitional variables;
- choose derived invariants or exact rational/coordinate parameters when their
  derivation and inverse use are justified by the supplied proof;
- clear denominators only while recording their nonzero and sign conditions;
- remove equations not needed for the target, duplicates, scalar multiples, and
  normalization variables that can be eliminated exactly;
- preserve enough information to derive every retained constraint from the original
  hypotheses and to translate the formal target back to the detected gap.

For polynomial ideal membership, actively seek a substantially smaller sufficient
system. Eight or fewer symbols and four or fewer generators are preferred when this
is mathematically sound; these are tractability goals, never permission to discard a
needed hypothesis. State the exact compression/substitution map and why the reduced
system still suffices. Then emit the selected operation's fenced tool-args DSL. Do
not claim a result.

For a proof-derived equation, Source basis must identify how it follows from the
original hypotheses or displayed prior equations. Target meaning must state the
logical equivalence or sufficient implication between the formal target and the
detected gap. Record every denominator, sign, domain, degeneracy, and branch
condition. If no sound smaller encoding can be obtained, retain the necessary
system and say so. If no sound encoding at all exists, emit syntactically invalid
output so the stage fails closed."""


SEMANTIC_AUDITOR_SYSTEM = """You are an independent semantic-compression auditor. Check
the proposed typed exact request against only the original theorem and submitted
proof. The exact backend will validate formal computation but cannot know whether
the model encoded the right mathematics, so reject any invented generator, symbol,
domain restriction, target equivalence, or omitted branch. Reject a request whose
result would not materially affect the proof rewrite. Verify every substitution in
the Compression map, verify that the Sufficiency argument preserves the direction
needed by the theorem, and reject avoidable definitional variables, duplicate or
irrelevant generators, or an uncompressed transcription when a proof-derived exact
elimination is available. Tractability never overrides semantic equivalence. Do not
repair the reduction.

Emit only:

# Decision

ACCEPT or REJECT

# Checks

- Every formal symbol is bound to the supplied proof: PASS or FAIL
- Every input equation or value is derived without invention: PASS or FAIL
- The formal target is equivalent to the detected proof gap: PASS or FAIL
- All domain, denominator, and branch conditions are recorded: PASS or FAIL
- The compression map is exact and preserves the needed implication: PASS or FAIL
- No avoidable definitional symbol or redundant generator remains: PASS or FAIL
- The requested result can materially change the proof rewrite: PASS or FAIL

# Issues

NONE, or one-line bullets. ACCEPT requires all PASS and NONE."""


BRIDGE_SYSTEM = """You are a problem-agnostic post-tool proof-bridge planner. The
typed request has passed an independent semantic audit and the exact result is now
available. Build the complete logical bridge from original hypotheses to formal
inputs, from the returned result to the detected gap, and from that gap to the
original theorem. Respect result polarity: a counterexample invalidates the tested
step and requires replacing it; a proved identity supports only the encoded target;
an exact solution set requires domain and completeness handling. Never turn a
negative or inconclusive result into positive evidence. Expand the compression map
inside the proof plan: derive every retained generator, translate the exact target
back to the original mathematical quantity, and explicitly justify every multiplier
or denominator used to clear or cancel factors. Preserve decisive exact certificate
data in an inspectable mathematical lemma instead of replacing it by a claim that a
calculation was performed.

Emit only:

# Tool Verdict

VERIFIED_SUPPORT, COUNTEREXAMPLE_FOUND, EXACT_SOLUTION_SET, or NO_USABLE_RESULT

# Checked Mathematical Statement

one paragraph

# Proof Gap Replaced

one paragraph

# Hypothesis-to-Tool Binding

- one step, or NONE

# Tool-to-Conclusion Bridge

- one step, or NONE

# Domain and Branch Closure

- one step, or NONE

# Whole-Proof Rewrite Plan

1. first step
2. next step

Do not use JSON or add headings."""


BRIDGE_AUDITOR_SYSTEM = """You are an independent, gold-free proof-bridge auditor.
Check the proposed bridge against the original theorem, Resolver proof, accepted
formal reduction, and exact result. Reject polarity reversal, unproved semantic
bindings, hidden cancellation/branch assumptions, or a merely local worksheet.
Do not repair the bridge.

Emit only:

# Decision

ACCEPT or REJECT

# Checks

- Tool verdict matches the returned exact result: PASS or FAIL
- Formal inputs are connected to original hypotheses: PASS or FAIL
- Returned facts bridge the detected gap with correct polarity: PASS or FAIL
- The compression map is unfolded back into the proof: PASS or FAIL
- The exact target is identified with the original theorem quantity: PASS or FAIL
- Every cleared or cancelled factor is justified: PASS or FAIL
- Decisive certificate data remains directly inspectable: PASS or FAIL
- Domain, denominator, and branch obligations are closed: PASS or FAIL
- Plan reconstructs the whole proof rather than a local patch: PASS or FAIL

# Issues

NONE, or one-line bullets. ACCEPT requires all PASS and NONE."""


REWRITER_SYSTEM = """You are an expert Olympiad proof author. Reconstruct one
complete, standalone proof of the original theorem using the supplied Resolver proof
as an untrusted scaffold and the accepted exact-result bridge as corrective evidence.
Do not merely append a certificate or patch one sentence. Derive the formal inputs
inside the mathematical proof, state the checked fact as a lemma or calculation,
use it with exactly the returned polarity, and carry it to every requested
conclusion. Handle denominators, signs, domains, degeneracies, equality cases, and
complete branches. Explicitly unfold the accepted compression map, derive every
generator from the theorem, identify the formal target with the original proof
quantity, and justify all factor cancellation. Reproduce the decisive checkable
certificate data supplied in the exact result; never substitute “by computation”,
“after simplification”, or an unexplained black-box assertion for it. If the result
is a counterexample to the old step, remove that step and replace the route. Output
only normal mathematical Markdown. Never mention tools, prompts, detectors,
compilers, audits, traces, scaffolds, or model process."""


PROOF_AUDITOR_SYSTEM = """You are a skeptical, gold-free Olympiad jury. Audit the
submitted replacement proof against the original theorem and the accepted exact
bridge. Check the entire proof, not just the former gap. A formal certificate is not
enough unless its inputs are derived and its conclusion is used correctly. Do not
repair the proof.

Emit only:

# Decision

PASS or FAIL

# Checks

- The original theorem is fully answered: PASS or FAIL
- The detected load-bearing gap is actually bridged: PASS or FAIL
- The exact result is used with the correct logical polarity: PASS or FAIL
- All formal variables and equations are derived in the proof: PASS or FAIL
- The formal target is explicitly translated back to the theorem quantity: PASS or FAIL
- Every cleared or cancelled factor is justified: PASS or FAIL
- Decisive exact certificate data remains directly inspectable: PASS or FAIL
- All domain, denominator, equality, and branch cases are handled: PASS or FAIL
- No process or tool meta-language appears: PASS or FAIL

# Issues

NONE, or one-line bullets. PASS requires all checks PASS and NONE."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n").rstrip() + "\n", encoding="utf-8")


def stable_seed(master_seed: int, label: str) -> int:
    material = f"v0274:{master_seed}:{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:4], "big") or 1


COMPRESSION_RANKING_FIELDS = (
    "solver_symbol_count",
    "solver_generator_count",
    "maximum_total_degree",
    "total_monomial_count",
    "argument_ast_nodes",
)


def compression_ranking_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    """Rank only semantically accepted rows; compactness breaks no semantic tie."""

    if row.get("state") != "accepted":
        raise ValueError("only semantically accepted compression rows may be ranked")
    profile = row["request_profile"]
    return tuple(int(profile[field]) for field in COMPRESSION_RANKING_FIELDS) + (
        str(profile["canonical_argument_hash"]),
    )


def _parser_feedback(history: list[Mapping[str, str]]) -> str:
    """Render all prior validation failures for a cumulative repair call."""

    blocks: list[str] = []
    for index, failure in enumerate(history, start=1):
        rejected_markdown = failure["rejected_markdown"]
        rejected = rejected_markdown
        truncation_note = "NONE"
        if len(rejected) > MAX_REJECTED_MARKDOWN_CHARS:
            rejected = rejected[:MAX_REJECTED_MARKDOWN_CHARS]
            truncation_note = (
                f"TRUNCATED after {MAX_REJECTED_MARKDOWN_CHARS} characters; "
                f"full SHA-256: {sha256_text(rejected_markdown)}"
            )
        blocks.append(
            f"""## Failure {index}

### Exact Rejection

{failure['error']}

### Rejected Markdown Truncation

{truncation_note}

### Rejected Markdown {index}

<BEGIN_REJECTED_MARKDOWN_{index}>
{rejected}
<END_REJECTED_MARKDOWN_{index}>"""
        )
    return """# Accumulated Strict Parser Feedback

Every failure below remains active. Correct all of them simultaneously and preserve every
valid correction made by later attempts. Re-check every line against the original contract.
Return a complete replacement in the original requested Markdown template; do not merely
describe the corrections.

""" + "\n\n".join(blocks)


def _model_call(
    *,
    role: Role,
    system_prompt: str,
    user_prompt: str,
    destination: Path,
    stage: str,
    master_seed: int,
    parser: Callable[[str], Any],
    initial_feedback: list[Mapping[str, str]] | None = None,
    request_timeout_sec: int | None = 600,
    thinking_token_budget: int | None = None,
    token_caps: tuple[int, ...] | None = None,
    prompt_character_limit: int | None = None,
    feedback_history_limit: int | None = None,
) -> tuple[str, Any, dict[str, Any]]:
    """32k primary+replacement, then feedback-driven fresh 48k/64k recovery."""

    errors: list[dict[str, Any]] = []
    feedback_history = [dict(item) for item in (initial_feedback or [])]
    caps = TOKEN_CAPS if token_caps is None else token_caps
    if not caps or any(cap not in TOKEN_CAPS for cap in caps):
        raise ValueError("model token caps must be a nonempty subset of the existing caps")
    for attempt, cap in enumerate(caps, start=1):
        call_dir = destination / f"attempt_{attempt:02d}_cap_{cap}"
        call_dir.mkdir(parents=True, exist_ok=False)
        attempt_user_prompt = user_prompt
        if feedback_history:
            feedback = _parser_feedback(feedback_history if feedback_history_limit is None else feedback_history[-feedback_history_limit:])
            attempt_user_prompt = f"{user_prompt.rstrip()}\n\n{feedback}"
            write_text(call_dir / f"{stage}.retry_feedback.md", feedback)
        text = ""
        try:
            if prompt_character_limit is not None and len(system_prompt) + len(attempt_user_prompt) > prompt_character_limit:
                raise ValueError("model prompt exceeds the configured character budget; input was not truncated")
            result = transport.run_openai_chat_generation(
                endpoint=role.endpoint,
                model=role.model,
                prompt=system_prompt,
                user_prompt=attempt_user_prompt,
                output_dir=call_dir,
                stage=stage,
                config=transport.HTTPGenerationConfig(
                    max_tokens=cap,
                    temperature=role.temperature,
                    top_p=0.95,
                    top_k=64,
                    seed=stable_seed(master_seed, f"{stage}:{attempt}:{cap}"),
                    thinking_token_budget=thinking_token_budget,
                    reasoning_effort=role.reasoning_effort,
                    thinking_enabled=True,
                    timeout_seconds=request_timeout_sec,
                ),
            )
            text = str(result.get("text") or "").strip()
            metadata = dict(result.get("metadata") or {})
            finish = str(metadata.get("finish_reason") or "")
            if not text or finish in {"length", "repetition"}:
                raise ValueError(f"unaccepted {finish=!r} or empty Markdown")
            parsed = parser(text)
            write_text(call_dir / f"{stage}.validation.md", "# Validation\n\nPASS")
            return text, parsed, {
                "attempt": attempt,
                "cap": cap,
                "parser_feedback_supplied": bool(feedback_history),
                "parser_feedback_count": len(feedback_history),
                "metadata": metadata,
                "request_timeout_sec": request_timeout_sec,
            }
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            errors.append({"attempt": attempt, "cap": cap, "error": message})
            write_text(
                call_dir / f"{stage}.validation.md",
                f"# Validation\n\nFAIL\n\n# Error\n\n{message}",
            )
            # Only response-validation failures have a rejected response that the
            # model can usefully repair. Transport failures retry without inventing
            # model feedback.
            if text:
                feedback_history.append(
                    {"error": message, "rejected_markdown": text}
                )
    raise RuntimeError(f"{stage} exhausted bounded token-cap recovery {caps}: {errors}")


def _compact_validation_feedback(errors: list[str]) -> str:
    return """# Compact Strict Validation History

Every listed constraint remains active. Return a complete corrected replacement.

""" + "\n".join(f"- {message}" for message in errors)


def _compiler_model_call(
    *,
    role: Role,
    system_prompt: str,
    user_prompt: str,
    destination: Path,
    stage: str,
    master_seed: int,
    parser: Callable[[str], Any],
    request_timeout_sec: int = 600,
) -> tuple[str, Any, dict[str, Any]]:
    """Parse each primary first; budget-force only a rejected compiler response."""

    errors: list[str] = []
    feedback_errors: list[str] = []
    for attempt, cap in enumerate(TOKEN_CAPS, start=1):
        attempt_dir = destination / f"attempt_{attempt:02d}_cap_{cap}"
        attempt_dir.mkdir(parents=True, exist_ok=False)
        attempt_prompt = user_prompt
        if feedback_errors:
            compact = _compact_validation_feedback(feedback_errors)
            attempt_prompt = f"{user_prompt.rstrip()}\n\n{compact}"
            write_text(attempt_dir / f"{stage}.compact_feedback.md", compact)
        config = transport.HTTPGenerationConfig(
            max_tokens=cap,
            temperature=role.temperature,
            top_p=0.95,
            top_k=64,
            seed=stable_seed(master_seed, f"{stage}:primary:{attempt}:{cap}"),
            thinking_token_budget=None,
            reasoning_effort=role.reasoning_effort,
            thinking_enabled=True,
            timeout_seconds=request_timeout_sec,
        )
        primary_dir = attempt_dir / "primary"
        primary_dir.mkdir(parents=True, exist_ok=False)
        primary_text = ""
        try:
            primary = _UNFORCED_GENERATION(
                endpoint=role.endpoint,
                model=role.model,
                prompt=system_prompt,
                user_prompt=attempt_prompt,
                output_dir=primary_dir,
                stage=stage,
                config=config,
            )
            primary_text = str(primary.get("text") or "").strip()
            primary_metadata = dict(primary.get("metadata") or {})
            finish = str(primary_metadata.get("finish_reason") or "")
            if not primary_text or finish in {"length", "repetition"}:
                raise ValueError(f"unaccepted {finish=!r} or empty Markdown")
            parsed = parser(primary_text)
            write_text(primary_dir / f"{stage}.validation.md", "# Validation\n\nPASS")
            policy = {
                "policy": "primary_parse_before_conditional_budget_forcing",
                "primary_parser_passed": True,
                "replacement_called": False,
                "cap": cap,
            }
            write_json(attempt_dir / "conditional_budget_forcing.json", policy)
            return primary_text, parsed, {
                "attempt": attempt,
                "cap": cap,
                "canonical_source": "primary",
                "conditional_budget_forcing": policy,
                "metadata": primary_metadata,
                "request_timeout_sec": request_timeout_sec,
            }
        except Exception as error:
            primary_error = f"{type(error).__name__}: {error}"
            errors.append(primary_error)
            if primary_text:
                feedback_errors.append(primary_error)
            write_text(
                primary_dir / f"{stage}.validation.md",
                f"# Validation\n\nFAIL\n\n# Error\n\n{primary_error}",
            )
        if not primary_text:
            continue

        replacement_dir = attempt_dir / "replacement"
        replacement_dir.mkdir(parents=True, exist_ok=False)
        replacement_text = ""
        replacement_cue = (
            "The prior compiler response failed strict validation with: "
            f"{primary_error}. Return a complete corrected replacement satisfying "
            "the original contract and every compact validation constraint."
        )
        try:
            replacement = _UNFORCED_GENERATION(
                endpoint=role.endpoint,
                model=role.model,
                prompt=system_prompt,
                user_prompt=attempt_prompt,
                output_dir=replacement_dir,
                stage=stage,
                config=transport.HTTPGenerationConfig(
                    **{
                        **asdict(config),
                        "seed": stable_seed(
                            master_seed, f"{stage}:replacement:{attempt}:{cap}"
                        ),
                    }
                ),
                prior_generation=primary_text,
                continuation_instruction=replacement_cue,
            )
            replacement_text = str(replacement.get("text") or "").strip()
            replacement_metadata = dict(replacement.get("metadata") or {})
            finish = str(replacement_metadata.get("finish_reason") or "")
            if not replacement_text or finish in {"length", "repetition"}:
                raise ValueError(f"unaccepted {finish=!r} or empty Markdown")
            parsed = parser(replacement_text)
            write_text(replacement_dir / f"{stage}.validation.md", "# Validation\n\nPASS")
            policy = {
                "policy": "primary_parse_before_conditional_budget_forcing",
                "primary_parser_passed": False,
                "primary_error": primary_error,
                "replacement_called": True,
                "replacement_parser_passed": True,
                "cap": cap,
            }
            write_json(attempt_dir / "conditional_budget_forcing.json", policy)
            return replacement_text, parsed, {
                "attempt": attempt,
                "cap": cap,
                "canonical_source": "replacement",
                "conditional_budget_forcing": policy,
                "metadata": replacement_metadata,
                "request_timeout_sec": request_timeout_sec,
            }
        except Exception as error:
            replacement_error = f"{type(error).__name__}: {error}"
            errors.append(replacement_error)
            if replacement_text:
                feedback_errors.append(replacement_error)
            write_text(
                replacement_dir / f"{stage}.validation.md",
                f"# Validation\n\nFAIL\n\n# Error\n\n{replacement_error}",
            )
            write_json(
                attempt_dir / "conditional_budget_forcing.json",
                {
                    "policy": "primary_parse_before_conditional_budget_forcing",
                    "primary_parser_passed": False,
                    "primary_error": primary_error,
                    "replacement_called": True,
                    "replacement_parser_passed": False,
                    "replacement_error": replacement_error,
                    "cap": cap,
                },
            )
    raise RuntimeError(f"{stage} exhausted conditional 32k/48k/64k recovery: {errors}")


def _matcher_operations(
    excluded_operations: tuple[str, ...] = (),
) -> tuple[str, ...]:
    excluded = tuple(dict.fromkeys(excluded_operations))
    unknown = sorted(set(excluded) - set(exact_tools.EXPOSED_OPERATIONS))
    if unknown:
        raise ValueError(f"cannot exclude unknown matcher operations: {unknown}")
    allowed = tuple(
        operation
        for operation in exact_tools.EXPOSED_OPERATIONS
        if operation not in excluded
    )
    if not allowed:
        raise ValueError("matcher operation ablation cannot exclude every operation")
    return allowed


def matcher_system(allowed_operations: tuple[str, ...]) -> str:
    """Render matcher guidance without naming operations outside its allowlist."""

    if tuple(allowed_operations) == tuple(exact_tools.EXPOSED_OPERATIONS):
        return MATCHER_SYSTEM
    guidance: list[str] = []
    if "polynomial_ideal_membership" in allowed_operations:
        guidance.append(
            "polynomial_ideal_membership for proving a target polynomial consequence "
            "of several polynomial constraints"
        )
    if "simplify_identity" in allowed_operations:
        guidance.append("simplify_identity for one rational identity")
    if "expand_and_compare" in allowed_operations:
        guidance.append("expand_and_compare for a direct polynomial equality")
    exhaustive = [
        operation
        for operation in ("exact_branch_system", "enumerate_finite_assignments")
        if operation in allowed_operations
    ]
    if exhaustive:
        guidance.append(" or ".join(exhaustive) + " for exhaustive solving")
    preference = (
        " Prefer " + ", ".join(guidance) + "." if guidance else ""
    )
    return (
        "You are a problem-agnostic exact-operation matcher. Match the\n"
        "immutable detected evidence task to exactly one allowlisted operation, or NO_TOOL.\n"
        "Choose an operation only when it can directly return the requested evidence from a\n"
        "formalization derived from the supplied theorem and proof. Counterexample searches\n"
        "must be exhaustive over a valid finite or exact algebraic domain; numerical samples\n"
        "cannot certify a universal claim."
        + preference
        + "\n\nEmit only the strict # Decision, # Operation, # Immutable Claim, # Fit Rationale\n"
        "Markdown template. Copy the desired exact fact byte-for-byte as Immutable Claim for\n"
        "CALL_TOOL. Do not compile arguments or invent results."
    )


def operation_catalog(
    allowed_operations: tuple[str, ...] | None = None,
) -> str:
    descriptions = {
        "polynomial_ideal_membership": (
            "prove whether a target polynomial is an exact consequence of several "
            "polynomial constraints and return original-generator multipliers"
        ),
        "expand_and_compare": "compare two polynomial expressions after exact expansion",
        "factor_and_reexpand": "factor a polynomial and verify it by exact re-expansion",
        "simplify_identity": "check an exact rational algebraic identity",
        "solve_and_substitute": "solve bounded exact equations and substitute all solutions",
        "polynomial_root_filter": "find every polynomial root satisfying an exact domain",
        "exact_modular_evaluation": "compute an exact modular power",
        "gcd": "compute an exact finite integer gcd",
        "prime_factorization": "factor a nonzero integer exactly",
        "determinant": "compute an exact square integer determinant",
        "enumerate_finite_assignments": "exhaustively search a finite Cartesian domain",
        "exact_branch_system": "solve a bounded exact polynomial system exhaustively",
    }
    operations = (
        tuple(exact_tools.EXPOSED_OPERATIONS)
        if allowed_operations is None
        else tuple(allowed_operations)
    )
    return "\n".join(f"- {name}: {descriptions[name]}" for name in operations)


IDEAL_CONTRACT = """```tool-args
operation = polynomial_ideal_membership
symbols = x, y
generator = D1 :: one polynomial S-expression equal to zero
generator = D2 :: another polynomial S-expression equal to zero
target = the target polynomial S-expression to prove zero
```

Use integer leaves, (symbol x), (rational p q), (add ...), (mul ...),
(sub left right), (pow expression nonnegative_integer), and (neg expression).
No division, functions, inequalities, implicit products, or undeclared symbols."""


def compiler_contract(operation: str) -> str:
    if operation == exact_tools.IDEAL_OPERATION:
        return IDEAL_CONTRACT
    return v0237.compiler_contract(operation)


def _parse_matcher(
    text: str,
    desired: str,
    allowed_operations: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    operations = (
        tuple(exact_tools.EXPOSED_OPERATIONS)
        if allowed_operations is None
        else tuple(allowed_operations)
    )
    normalized_text, normalization = protocol.normalize_matcher(
        text, allowed_operations=operations
    )
    parsed = mdp.parse_matcher(normalized_text, operations)
    if parsed["call_requested"] and parsed["claim"] != desired:
        raise ValueError("matcher changed the immutable desired exact fact")
    parsed["normalized_markdown"] = normalized_text
    parsed["deterministic_normalization"] = normalization
    return parsed


def _parse_compilation(text: str, operation: str) -> dict[str, Any]:
    normalized_text, normalization = protocol.normalize_compilation(text, operation)
    compiled = protocol.parse_compilation(normalized_text, operation)
    if operation == exact_tools.IDEAL_OPERATION:
        exact_tools.validate_ideal_arguments(compiled["arguments"])
    else:
        compiled["arguments"] = v0221.validate_operation_arguments(
            operation, compiled["arguments"]
        )
    compiled["normalized_markdown"] = normalized_text
    compiled["deterministic_normalization_applied"] = normalized_text != text
    compiled["deterministic_normalization"] = normalization
    return compiled


def _terminal_proof(text: str) -> str:
    proof = text.replace("\r\n", "\n").strip()
    if len(proof) < 800:
        raise ValueError("replacement proof is too short")
    if proof.startswith("```"):
        raise ValueError("replacement proof must not be wrapped in a code fence")
    lowered = proof.casefold()
    forbidden = ("tool result", "compiler", "detector", "audit record", "prompt", "scaffold")
    if any(token in lowered for token in forbidden):
        raise ValueError("replacement proof contains process meta-language")
    if not any(token in proof for token in ("=", "<", ">", "\\")):
        raise ValueError("replacement proof contains no mathematical relation")
    return proof


def detection_prompt(problem: v0220.Problem, proof: str, hits: list[dict[str, Any]]) -> str:
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Deterministic Compression-Phrase Nominations

{protocol.render_candidates(hits)}

The nominations are incomplete and nonbinding. Inspect the whole proof, including
unflagged equations, and select only the single highest-impact exactly checkable gap."""


def matcher_prompt(
    problem: v0220.Problem,
    proof: str,
    detection: Mapping[str, Any],
    allowed_operations: tuple[str, ...] | None = None,
) -> str:
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Immutable Detected Gap

- Evidence task: {detection['evidence_task']}
- Desired exact fact: {detection['desired_exact_fact']}
- Downstream obligation: {detection['downstream_obligation']}

# Allowlisted Exact Operations

{operation_catalog(allowed_operations)}

Match the immutable desired exact fact without changing it."""


def compilation_prompt(
    problem: v0220.Problem,
    proof: str,
    detection: Mapping[str, Any],
    matcher: Mapping[str, Any],
    prior_audit: Mapping[str, Any] | None,
) -> str:
    feedback = ""
    if prior_audit is not None:
        feedback = "\n\n# Prior Reduction-Audit Issues\n\n" + "\n".join(
            f"- {issue}" for issue in prior_audit["issues"]
        )
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Immutable Evidence Request

- Gap: {detection['gap']}
- Evidence task: {detection['evidence_task']}
- Desired exact fact: {detection['desired_exact_fact']}
- Selected operation: {matcher['operation']}

# Required Output

# Semantic Bindings

- Source basis: one-line derivation source
- Target meaning: one-line equivalence to the detected gap
- Domain and branch conditions: one-line complete conditions
- Compression map: one-line substitutions, eliminations, and retained invariants, or IDENTITY if none
- Sufficiency argument: one-line reason the reduced request preserves the implication needed by the proof
- Rewrite consequence: one-line effect of each possible result

# Tool Arguments

{compiler_contract(str(matcher['operation']))}{feedback}

Emit the two top-level sections exactly. The contract's Tool Arguments heading is
illustrative; include it only once in your output."""


def semantic_audit_prompt(
    problem: v0220.Problem,
    proof: str,
    detection_text: str,
    matcher_text: str,
    compilation_text: str,
    request_profile: Mapping[str, Any] | None = None,
) -> str:
    profile = "NONE"
    if request_profile is not None:
        profile = "\n".join(
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in request_profile.items()
        )
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Detection

{detection_text}

# Operation Match

{matcher_text}

# Proposed Semantic Reduction and Typed Request

{compilation_text}

# Deterministic Request Profile

{profile}

Audit literal mathematical correspondence. Exact formal correctness alone is not
enough. The profile reports only mechanically safe reductions; audit whether further
proof-derived semantic compression is both available and necessary."""


def bridge_prompt(
    problem: v0220.Problem,
    proof: str,
    detection_text: str,
    compilation_text: str,
    audit_text: str,
    event_text: str,
    prior_audit: Mapping[str, Any] | None,
) -> str:
    feedback = ""
    if prior_audit is not None:
        feedback = "\n\n# Prior Bridge-Audit Issues\n\n" + "\n".join(
            f"- {issue}" for issue in prior_audit["issues"]
        )
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Detected Gap

{detection_text}

# Accepted Semantic Reduction

{compilation_text}

# Reduction Audit

{audit_text}

{event_text}{feedback}

Build a mathematically explicit bridge and a whole-proof rewrite plan. Do not exceed
what the exact result establishes."""


def bridge_audit_prompt(
    problem: v0220.Problem,
    proof: str,
    compilation_text: str,
    event_text: str,
    bridge_text: str,
) -> str:
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Accepted Formal Reduction

{compilation_text}

{event_text}

# Proposed Proof Bridge

{bridge_text}

Audit the bridge without supplying a replacement."""


def rewrite_prompt(
    problem: v0220.Problem,
    original_proof: str,
    compilation_text: str,
    event_text: str,
    bridge_text: str,
    current_proof: str,
    prior_audit: Mapping[str, Any] | None,
) -> str:
    feedback = ""
    if prior_audit is not None:
        feedback = "\n\n# Prior Jury Issues To Repair\n\n" + "\n".join(
            f"- {issue}" for issue in prior_audit["issues"]
        )
    return f"""# Original Theorem

{problem.statement}

# Untrusted Resolver-1 Proof

{original_proof}

# Current Replacement Attempt

{current_proof}

# Accepted Formal Reduction

{compilation_text}

{event_text}

# Accepted Proof Bridge

{bridge_text}{feedback}

Output one complete replacement proof only. The exact result must causally bridge the
gap; do not merely cite or append it."""


def proof_audit_prompt(
    problem: v0220.Problem,
    compilation_text: str,
    event_text: str,
    bridge_text: str,
    proof: str,
) -> str:
    return f"""# Original Theorem

{problem.statement}

# Accepted Formal Reduction

{compilation_text}

{event_text}

# Accepted Proof Bridge

{bridge_text}

# Submitted Replacement Proof

{proof}

Audit the proof as submitted, without a reference solution and without repairing it."""


def build_preflight(
    *,
    problem_file: Path,
    proof_file: Path,
    output_dir: Path,
    detector: Role,
    compiler: Role,
    auditor: Role,
    rewriter: Role,
    master_seed: int,
    exact_tool_timeout_sec: int,
    exact_tool_memory_mb: int,
    certificate_cache_dir: Path | None,
    reuse_detection_matcher_from: Path | None,
    excluded_matcher_operations: tuple[str, ...] = (),
    model_request_timeout_sec: int = 600,
) -> dict[str, Any]:
    if not 30 <= model_request_timeout_sec <= 14_400:
        raise ValueError("model-request timeout must be between 30 and 14400 seconds")
    if not 1 <= exact_tool_timeout_sec <= exact_tools.MAX_IDEAL_TIMEOUT_SEC:
        raise ValueError(
            "exact-tool timeout must be between 1 and "
            f"{exact_tools.MAX_IDEAL_TIMEOUT_SEC} seconds"
        )
    if not 256 <= exact_tool_memory_mb <= 8192:
        raise ValueError("exact-tool memory must be between 256 and 8192 MB")
    problem = v0220.load_problem(problem_file)
    proof_path = proof_file.resolve()
    if not proof_path.is_file():
        raise FileNotFoundError(proof_path)
    proof = proof_path.read_text(encoding="utf-8").strip()
    if not proof:
        raise ValueError("Resolver-1 proof is empty")
    hits = protocol.compression_candidates(proof)
    allowed_matcher_operations = _matcher_operations(excluded_matcher_operations)
    return {
        "schema": "cognitive-well-v0274-generic-compression-portfolio-bridge-preflight-v1",
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "boundary": "immediately_after_resolver1",
        "problem_id": problem.problem_id,
        "problem_file": str(problem.source_path),
        "problem_file_sha256": sha256_file(problem.source_path),
        "resolver1_proof": str(proof_path),
        "resolver1_proof_sha256": sha256_text(proof),
        "output_dir": str(output_dir.resolve()),
        "compression_phrase_nomination_count": len(hits),
        "compression_phrase_nominations": hits,
        "operations": list(exact_tools.EXPOSED_OPERATIONS),
        "matcher_allowed_operations": list(allowed_matcher_operations),
        "matcher_excluded_operations": list(
            operation
            for operation in exact_tools.EXPOSED_OPERATIONS
            if operation not in allowed_matcher_operations
        ),
        "matcher_operation_ablation_policy": (
            "remove_from_prompt_guidance_catalog_and_parser_allowlist_without_"
            "relabel_or_resampling"
        ),
        "evidence_tasks": sorted(protocol.EVIDENCE_TASKS),
        "roles": {
            "detector_and_matcher": asdict(detector),
            "compiler": asdict(compiler),
            "semantic_and_bridge_auditor": asdict(auditor),
            "bridge_and_rewriter": asdict(rewriter),
        },
        "budget_forcing": {
            "mandatory_full_replacement_per_model_call": True,
            "default_cap": TOKEN_CAPS[0],
            "fresh_recovery_caps": list(TOKEN_CAPS[1:]),
            "fresh_retries_receive_exact_parser_failure": True,
            "fresh_retries_receive_rejected_markdown": True,
            "parser_feedback_is_cumulative": True,
            "per_http_request_timeout_sec": model_request_timeout_sec,
            "transport_timeout_retries_at_next_fresh_cap": True,
        },
        "model_output_format": "Markdown",
        "tool_arguments_format": "fenced line-oriented S-expression DSL",
        "detection_matcher_reuse": (
            None
            if reuse_detection_matcher_from is None
            else str(reuse_detection_matcher_from.resolve())
        ),
        "compression_portfolio": {
            "candidate_count": len(COMPRESSION_ARM_TEMPERATURES),
            "concurrent_compiler_calls": True,
            "independent_concurrent_audits": True,
            "arms": [
                {"label": label, "temperature": temperature}
                for label, temperature in COMPRESSION_ARM_TEMPERATURES
            ],
            "formalization_schedule_sha256": formalization_schedule_sha256(),
            "semantic_acceptance_precedes_size_ranking": True,
            "ranking": [
                "solver_symbol_count",
                "solver_generator_count",
                "maximum_total_degree",
                "total_monomial_count",
                "argument_ast_nodes",
                "canonical_argument_hash",
            ],
        },
        "exact_tool_policy": {
            "cpu_only": True,
            "timeout_sec": exact_tool_timeout_sec,
            "memory_mb": exact_tool_memory_mb,
            "verified_certificate_cache": certificate_cache_dir is not None,
            "certificate_cache_dir": (
                None if certificate_cache_dir is None else str(certificate_cache_dir.resolve())
            ),
            "cache_replay_requires_exact_reexpansion": True,
            "deterministic_lossless_reductions": [
                "remove unused formal symbols",
                "remove zero generators",
                "remove duplicate or QQ-proportional generators",
            ],
        },
        "genericity_guards": {
            "problem_specific_phrases_in_prompts": False,
            "preselected_operation": False,
            "preloaded_ledger_or_certificate": False,
            "problem_specific_compression_rule": False,
            "reference_solution_access": False,
            "gold_score_access": False,
            "codex_feedback_access": False,
        },
        "causal_policy": (
            "accepted semantic reduction -> exact execution -> accepted bridge -> whole-proof rewrite"
        ),
        "counterexample_policy": (
            "exact counterexamples invalidate the tested step and must drive route replacement"
        ),
    }


def run_after_resolver1(
    *,
    problem_file: Path,
    proof_file: Path,
    output_dir: Path,
    detector: Role,
    compiler: Role,
    auditor: Role,
    rewriter: Role,
    master_seed: int = 20260905,
    exact_tool_timeout_sec: int = exact_tools.DEFAULT_IDEAL_TIMEOUT_SEC,
    exact_tool_memory_mb: int = exact_tools.DEFAULT_IDEAL_MEMORY_MB,
    certificate_cache_dir: Path | None = exact_tools.DEFAULT_CERTIFICATE_CACHE_DIR,
    reuse_detection_matcher_from: Path | None = None,
    excluded_matcher_operations: tuple[str, ...] = (),
    stop_after_accepted_request: bool = False,
    model_request_timeout_sec: int = 600,
    dry_run: bool = False,
) -> dict[str, Any]:
    preflight = build_preflight(
        problem_file=problem_file,
        proof_file=proof_file,
        output_dir=output_dir,
        detector=detector,
        compiler=compiler,
        auditor=auditor,
        rewriter=rewriter,
        master_seed=master_seed,
        exact_tool_timeout_sec=exact_tool_timeout_sec,
        exact_tool_memory_mb=exact_tool_memory_mb,
        certificate_cache_dir=certificate_cache_dir,
        reuse_detection_matcher_from=reuse_detection_matcher_from,
        excluded_matcher_operations=excluded_matcher_operations,
        model_request_timeout_sec=model_request_timeout_sec,
    )
    preflight["stop_after_accepted_request"] = stop_after_accepted_request
    if dry_run:
        return preflight

    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "manifest.json", {**preflight, "state": "running"})
    problem = v0220.load_problem(problem_file)
    allowed_matcher_operations = _matcher_operations(excluded_matcher_operations)
    proof = proof_file.resolve().read_text(encoding="utf-8").strip()
    write_text(destination / "input/original_theorem.md", "# Original Theorem\n\n" + problem.statement)
    write_text(destination / "input/resolver1_proof.md", proof)
    write_text(
        destination / "01_detection/compression_phrase_nominations.md",
        "# Compression-Phrase Nominations\n\n"
        + protocol.render_candidates(preflight["compression_phrase_nominations"]),
    )
    try:
        if reuse_detection_matcher_from is None:
            detection_text, detection, detection_call = _model_call(
                role=detector,
                system_prompt=DETECTOR_SYSTEM,
                user_prompt=detection_prompt(
                    problem, proof, preflight["compression_phrase_nominations"]
                ),
                destination=destination / "01_detection/model",
                stage="post_resolver_gap_detection",
                master_seed=master_seed,
                parser=protocol.parse_detection,
                request_timeout_sec=model_request_timeout_sec,
            )
        else:
            reuse_root = reuse_detection_matcher_from.resolve()
            reuse_manifest = json.loads(
                (reuse_root / "manifest.json").read_text(encoding="utf-8")
            )
            if reuse_manifest.get("problem_file_sha256") != preflight["problem_file_sha256"]:
                raise ValueError("reused detection has a different theorem hash")
            if reuse_manifest.get("resolver1_proof_sha256") != preflight["resolver1_proof_sha256"]:
                raise ValueError("reused detection has a different Resolver-1 proof hash")
            detection_text = (
                reuse_root / "01_detection/detection.md"
            ).read_text(encoding="utf-8").strip()
            detection = protocol.parse_detection(detection_text)
            detection_call = {
                "reused": True,
                "source_run": str(reuse_root),
                "artifact_sha256": sha256_text(detection_text),
            }
        write_text(destination / "01_detection/detection.md", detection_text)
        if not detection["call_requested"]:
            result = {
                "schema": "cognitive-well-v0274-generic-compression-portfolio-bridge-result-v1",
                "state": "completed_no_tool",
                "terminal_proof": str(proof_file.resolve()),
                "terminal_proof_sha256": sha256_text(proof),
                "detection_call": detection_call,
                "tool_executed": False,
                "proof_rewritten": False,
                "model_request_timeout_sec": model_request_timeout_sec,
            }
            write_json(destination / "result.json", result)
            write_json(
                destination / "manifest.json",
                {**preflight, "state": "completed_no_tool"},
            )
            return result

        if reuse_detection_matcher_from is None:
            matcher_raw_text, matcher, matcher_call = _model_call(
                role=detector,
                system_prompt=matcher_system(allowed_matcher_operations),
                user_prompt=matcher_prompt(
                    problem, proof, detection, allowed_matcher_operations
                ),
                destination=destination / "02_matcher/model",
                stage="exact_operation_matcher",
                master_seed=master_seed,
                parser=lambda text: _parse_matcher(
                    text,
                    detection["desired_exact_fact"],
                    allowed_matcher_operations,
                ),
                request_timeout_sec=model_request_timeout_sec,
            )
            matcher = dict(matcher)
            matcher_text = str(matcher.pop("normalized_markdown"))
            matcher_normalization = dict(
                matcher.pop("deterministic_normalization")
            )
            matcher_call = {
                **dict(matcher_call),
                "artifact_sha256": sha256_text(matcher_text),
                "deterministic_normalization": matcher_normalization,
            }
            write_text(destination / "02_matcher/matcher_raw.md", matcher_raw_text)
            write_json(
                destination / "02_matcher/deterministic_normalization.json",
                matcher_normalization,
            )
        else:
            reuse_root = reuse_detection_matcher_from.resolve()
            matcher_text = (
                reuse_root / "02_matcher/matcher.md"
            ).read_text(encoding="utf-8").strip()
            matcher = _parse_matcher(
                matcher_text,
                detection["desired_exact_fact"],
                allowed_matcher_operations,
            )
            matcher = dict(matcher)
            matcher_text = str(matcher.pop("normalized_markdown"))
            matcher_normalization = dict(
                matcher.pop("deterministic_normalization")
            )
            matcher_call = {
                "reused": True,
                "source_run": str(reuse_root),
                "artifact_sha256": sha256_text(matcher_text),
                "deterministic_normalization": matcher_normalization,
            }
        write_text(destination / "02_matcher/matcher.md", matcher_text)
        if not matcher["call_requested"]:
            result = {
                "schema": "cognitive-well-v0274-generic-compression-portfolio-bridge-result-v1",
                "state": "completed_no_matching_tool",
                "terminal_proof": str(proof_file.resolve()),
                "terminal_proof_sha256": sha256_text(proof),
                "detection_call": detection_call,
                "matcher_call": matcher_call,
                "tool_executed": False,
                "proof_rewritten": False,
                "model_request_timeout_sec": model_request_timeout_sec,
            }
            write_json(destination / "result.json", result)
            write_json(
                destination / "manifest.json",
                {**preflight, "state": "completed_no_matching_tool"},
            )
            return result

        portfolio_root = destination / "03_compression_portfolio"

        def compile_arm(label: str, temperature: float) -> dict[str, Any]:
            arm_root = portfolio_root / label
            arm_role = Role(
                endpoint=compiler.endpoint,
                model=compiler.model,
                temperature=temperature,
                reasoning_effort=compiler.reasoning_effort,
            )
            try:
                raw_text, parsed, call = _compiler_model_call(
                    role=arm_role,
                    system_prompt=COMPILER_SYSTEM,
                    user_prompt=compilation_prompt(
                        problem, proof, detection, matcher, None
                    ),
                    destination=arm_root / "compiler/model",
                    stage="semantic_tool_argument_compilation",
                    master_seed=stable_seed(master_seed, f"compiler:{label}"),
                    parser=lambda text: _parse_compilation(
                        text, str(matcher["operation"])
                    ),
                    request_timeout_sec=model_request_timeout_sec,
                )
                parsed = dict(parsed)
                normalized_text = str(parsed.pop("normalized_markdown"))
                normalization = dict(parsed["deterministic_normalization"])
                profile = (
                    exact_tools.ideal_request_profile(parsed["arguments"])
                    if matcher["operation"] == exact_tools.IDEAL_OPERATION
                    else {
                        "solver_symbol_count": 0,
                        "solver_generator_count": 0,
                        "maximum_total_degree": 0,
                        "total_monomial_count": 0,
                        "argument_ast_nodes": 0,
                        "canonical_argument_hash": exact_tools.stable_hash(
                            parsed["arguments"]
                        ),
                    }
                )
                write_text(arm_root / "compiler/compiler_raw.md", raw_text)
                write_text(arm_root / "compiler/compilation.md", normalized_text)
                write_json(
                    arm_root / "compiler/deterministic_normalization.json",
                    normalization,
                )
                write_json(arm_root / "compiler/request_profile.json", profile)
                call = {
                    **dict(call),
                    "deterministic_normalization": normalization,
                }
                return {
                    "label": label,
                    "temperature": temperature,
                    "state": "compiled",
                    "compilation_text": normalized_text,
                    "compilation": parsed,
                    "compilation_call": call,
                    "request_profile": profile,
                }
            except Exception as error:
                failure = {
                    "label": label,
                    "temperature": temperature,
                    "state": "compiler_failed",
                    "error": f"{type(error).__name__}: {error}",
                }
                write_json(arm_root / "compiler/failure.json", failure)
                return failure

        compiler_rows: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=len(COMPRESSION_ARM_TEMPERATURES)) as executor:
            futures = {
                executor.submit(compile_arm, label, temperature): label
                for label, temperature in COMPRESSION_ARM_TEMPERATURES
            }
            for future in as_completed(futures):
                compiler_rows.append(future.result())
        compiler_rows.sort(key=lambda row: str(row["label"]))
        compiled_rows = [row for row in compiler_rows if row["state"] == "compiled"]
        if not compiled_rows:
            raise RuntimeError("all eight semantic-compression compiler arms failed")

        def audit_arm(row: Mapping[str, Any]) -> dict[str, Any]:
            label = str(row["label"])
            arm_root = portfolio_root / label
            try:
                audit_text, audit, audit_call = _model_call(
                    role=auditor,
                    system_prompt=SEMANTIC_AUDITOR_SYSTEM,
                    user_prompt=semantic_audit_prompt(
                        problem,
                        proof,
                        detection_text,
                        matcher_text,
                        str(row["compilation_text"]),
                        row["request_profile"],
                    ),
                    destination=arm_root / "semantic_audit/model",
                    stage="semantic_reduction_audit",
                    master_seed=stable_seed(master_seed, f"auditor:{label}"),
                    parser=protocol.parse_semantic_audit,
                    request_timeout_sec=model_request_timeout_sec,
                )
                write_text(arm_root / "semantic_audit/audit.md", audit_text)
                return {
                    **dict(row),
                    "state": "accepted" if audit["accepted"] else "rejected",
                    "reduction_audit_text": audit_text,
                    "reduction_audit": audit,
                    "reduction_audit_call": audit_call,
                }
            except Exception as error:
                failure = {
                    **dict(row),
                    "state": "audit_failed",
                    "audit_error": f"{type(error).__name__}: {error}",
                }
                write_json(arm_root / "semantic_audit/failure.json", {
                    "label": label,
                    "state": "audit_failed",
                    "error": failure["audit_error"],
                })
                return failure

        audited_rows: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=len(compiled_rows)) as executor:
            futures = {executor.submit(audit_arm, row): row["label"] for row in compiled_rows}
            for future in as_completed(futures):
                audited_rows.append(future.result())
        audited_rows.sort(key=lambda row: str(row["label"]))
        accepted_rows = [row for row in audited_rows if row["state"] == "accepted"]
        if not accepted_rows:
            raise RuntimeError("all compiled compression candidates failed semantic audit")

        selected = min(accepted_rows, key=compression_ranking_key)
        selection_rows = [
            {
                "label": row["label"],
                "temperature": row["temperature"],
                "state": row["state"],
                "request_profile": row.get("request_profile"),
                "audit_decision": (
                    row.get("reduction_audit", {}).get("decision")
                    if isinstance(row.get("reduction_audit"), Mapping)
                    else None
                ),
                "compiler_error": row.get("error"),
                "audit_error": row.get("audit_error"),
            }
            for row in audited_rows
        ]
        for row in compiler_rows:
            if row["state"] != "compiled":
                selection_rows.append({
                    "label": row["label"],
                    "temperature": row["temperature"],
                    "state": row["state"],
                    "compiler_error": row.get("error"),
                })
        selection_rows.sort(key=lambda row: str(row["label"]))
        write_json(
            portfolio_root / "selection.json",
            {
                "formalization_schedule": formalization_schedule_records(),
                "formalization_schedule_sha256": formalization_schedule_sha256(),
                "candidate_count": len(COMPRESSION_ARM_TEMPERATURES),
                "compiled_count": len(compiled_rows),
                "accepted_count": len(accepted_rows),
                "ranking_fields": list(COMPRESSION_RANKING_FIELDS)
                + ["canonical_argument_hash"],
                "selected_label": selected["label"],
                "selected_profile": selected["request_profile"],
                "rows": selection_rows,
            },
        )
        compilation_text = str(selected["compilation_text"])
        compilation: Mapping[str, Any] = selected["compilation"]
        compilation_call: Mapping[str, Any] = selected["compilation_call"]
        request_profile: Mapping[str, Any] = selected["request_profile"]
        reduction_audit_text = str(selected["reduction_audit_text"])
        reduction_audit: Mapping[str, Any] = selected["reduction_audit"]
        reduction_audit_call: Mapping[str, Any] = selected["reduction_audit_call"]
        write_text(portfolio_root / "selected/compilation.md", compilation_text)
        write_text(portfolio_root / "selected/audit.md", reduction_audit_text)
        write_json(portfolio_root / "selected/request_profile.json", request_profile)

        if stop_after_accepted_request:
            result = {
                "schema": (
                    "cognitive-well-v0274-generic-compression-portfolio-"
                    "acquisition-result-v1"
                ),
                "state": "accepted_request_ready",
                "problem_id": problem.problem_id,
                "selected_evidence_task": detection["evidence_task"],
                "selected_operation": matcher["operation"],
                "tool_executed": False,
                "proof_rewritten": False,
                "model_request_timeout_sec": model_request_timeout_sec,
                "terminal_proof": str(proof_file.resolve()),
                "terminal_proof_sha256": sha256_text(proof),
                "accepted_request": str(
                    (portfolio_root / "selected/compilation.md").resolve()
                ),
                "accepted_request_sha256": sha256_text(compilation_text),
                "accepted_audit": str(
                    (portfolio_root / "selected/audit.md").resolve()
                ),
                "accepted_audit_sha256": sha256_text(reduction_audit_text),
                "accepted_profile": str(
                    (portfolio_root / "selected/request_profile.json").resolve()
                ),
                "accepted_profile_sha256": sha256_file(
                    portfolio_root / "selected/request_profile.json"
                ),
                "request_profile": request_profile,
                "compression_portfolio": {
                    "formalization_schedule": formalization_schedule_records(),
                    "formalization_schedule_sha256": formalization_schedule_sha256(),
                    "candidate_count": len(COMPRESSION_ARM_TEMPERATURES),
                    "compiled_count": len(compiled_rows),
                    "accepted_count": len(accepted_rows),
                    "selected_label": selected["label"],
                },
                "reduction_audit_accepted": reduction_audit["accepted"],
                "calls": {
                    "detection": detection_call,
                    "matcher": matcher_call,
                    "compilation": compilation_call,
                    "reduction_audit": reduction_audit_call,
                },
            }
            write_json(destination / "result.json", result)
            write_json(
                destination / "manifest.json",
                {**preflight, "state": "accepted_request_ready"},
            )
            return result

        event = exact_tools.execute(
            operation=str(matcher["operation"]),
            arguments=compilation["arguments"],
            claim=str(matcher["claim"]),
            problem=problem,
            run_id=destination.name,
            exact_tool_timeout_sec=exact_tool_timeout_sec,
            exact_tool_memory_mb=exact_tool_memory_mb,
            certificate_cache_dir=certificate_cache_dir,
        )
        event_text = exact_tools.render_event(event)
        write_text(destination / "05_exact_tool/tool_call.md", compilation_text)
        write_text(destination / "05_exact_tool/tool_result.md", event_text)
        if event["validation_status"] != "passed" or event["evidence_status"] != "verified":
            raise RuntimeError("exact execution did not return validator-gated evidence")
        target_evidence_verification = exact_tools.verify_target_evidence_event(event)

        bridge_text = ""
        bridge: Mapping[str, Any] | None = None
        bridge_call: Mapping[str, Any] | None = None
        bridge_audit_text = ""
        bridge_audit: Mapping[str, Any] | None = None
        bridge_audit_call: Mapping[str, Any] | None = None
        prior_bridge_audit: Mapping[str, Any] | None = None
        for cycle in (1, 2, 3):
            bridge_text, bridge, bridge_call = _model_call(
                role=rewriter,
                system_prompt=BRIDGE_SYSTEM,
                user_prompt=bridge_prompt(
                    problem,
                    proof,
                    detection_text,
                    compilation_text,
                    reduction_audit_text,
                    event_text,
                    prior_bridge_audit,
                ),
                destination=destination / f"06_bridge/cycle_{cycle:02d}/model",
                stage="post_tool_bridge",
                master_seed=master_seed + cycle,
                parser=protocol.parse_bridge,
                request_timeout_sec=model_request_timeout_sec,
            )
            write_text(destination / f"06_bridge/cycle_{cycle:02d}/bridge.md", bridge_text)
            bridge_audit_text, bridge_audit, bridge_audit_call = _model_call(
                role=auditor,
                system_prompt=BRIDGE_AUDITOR_SYSTEM,
                user_prompt=bridge_audit_prompt(
                    problem, proof, compilation_text, event_text, bridge_text
                ),
                destination=destination / f"07_bridge_audit/cycle_{cycle:02d}/model",
                stage="post_tool_bridge_audit",
                master_seed=master_seed + cycle,
                parser=protocol.parse_bridge_audit,
                request_timeout_sec=model_request_timeout_sec,
            )
            write_text(
                destination / f"07_bridge_audit/cycle_{cycle:02d}/audit.md",
                bridge_audit_text,
            )
            if bridge_audit["accepted"]:
                break
            prior_bridge_audit = bridge_audit
        if not bridge or not bridge_audit or not bridge_audit["accepted"]:
            raise RuntimeError("post-tool bridge remained rejected after three cycles")
        if bridge["verdict"] == "NO_USABLE_RESULT":
            raise RuntimeError("exact result produced no usable proof bridge")

        current_proof = proof
        proof_call: Mapping[str, Any] | None = None
        proof_audit_text = ""
        proof_audit: Mapping[str, Any] | None = None
        proof_audit_call: Mapping[str, Any] | None = None
        prior_proof_audit: Mapping[str, Any] | None = None
        for cycle in (1, 2, 3):
            current_proof, _, proof_call = _model_call(
                role=rewriter,
                system_prompt=REWRITER_SYSTEM,
                user_prompt=rewrite_prompt(
                    problem,
                    proof,
                    compilation_text,
                    event_text,
                    bridge_text,
                    current_proof,
                    prior_proof_audit,
                ),
                destination=destination / f"08_proof_rewrite/cycle_{cycle:02d}/model",
                stage="tool_driven_whole_proof_rewrite",
                master_seed=master_seed + cycle,
                parser=_terminal_proof,
                request_timeout_sec=model_request_timeout_sec,
            )
            write_text(
                destination / f"08_proof_rewrite/cycle_{cycle:02d}/terminal_proof.md",
                current_proof,
            )
            proof_audit_text, proof_audit, proof_audit_call = _model_call(
                role=auditor,
                system_prompt=PROOF_AUDITOR_SYSTEM,
                user_prompt=proof_audit_prompt(
                    problem, compilation_text, event_text, bridge_text, current_proof
                ),
                destination=destination / f"09_proof_audit/cycle_{cycle:02d}/model",
                stage="tool_driven_proof_audit",
                master_seed=master_seed + cycle,
                parser=protocol.parse_proof_audit,
                request_timeout_sec=model_request_timeout_sec,
            )
            write_text(
                destination / f"09_proof_audit/cycle_{cycle:02d}/audit.md",
                proof_audit_text,
            )
            if proof_audit["passed"]:
                break
            prior_proof_audit = proof_audit

        terminal_path = destination / "terminal_proof.md"
        write_text(terminal_path, current_proof)
        result = {
            "schema": "cognitive-well-v0274-generic-compression-portfolio-bridge-result-v1",
            "state": "completed",
            "problem_id": problem.problem_id,
            "selected_evidence_task": detection["evidence_task"],
            "selected_operation": matcher["operation"],
            "tool_executed": True,
            "tool_validation_status": event["validation_status"],
            "tool_evidence_status": event["evidence_status"],
            "target_evidence_verification": target_evidence_verification,
            "exact_tool_timeout_sec": exact_tool_timeout_sec,
            "exact_tool_memory_mb": exact_tool_memory_mb,
            "request_profile": request_profile,
            "compression_portfolio": {
                "formalization_schedule": formalization_schedule_records(),
                "formalization_schedule_sha256": formalization_schedule_sha256(),
                "candidate_count": len(COMPRESSION_ARM_TEMPERATURES),
                "compiled_count": len(compiled_rows),
                "accepted_count": len(accepted_rows),
                "selected_label": selected["label"],
            },
            "tool_cache": (
                event.get("normalized_result", {}).get("cache")
                if isinstance(event.get("normalized_result"), Mapping)
                else None
            ),
            "reduction_audit_accepted": reduction_audit["accepted"],
            "bridge_audit_accepted": bridge_audit["accepted"],
            "proof_rewritten": True,
            "proof_audit_passed": bool(proof_audit and proof_audit["passed"]),
            "model_request_timeout_sec": model_request_timeout_sec,
            "terminal_proof": str(terminal_path.resolve()),
            "terminal_proof_sha256": sha256_text(current_proof),
            "calls": {
                "detection": detection_call,
                "matcher": matcher_call,
                "compilation": compilation_call,
                "reduction_audit": reduction_audit_call,
                "bridge": bridge_call,
                "bridge_audit": bridge_audit_call,
                "proof_rewrite": proof_call,
                "proof_audit": proof_audit_call,
            },
        }
        write_json(destination / "result.json", result)
        write_json(destination / "manifest.json", {**preflight, "state": "completed"})
        return result
    except Exception as error:
        failure = {
            "schema": "cognitive-well-v0274-generic-compression-portfolio-bridge-failure-v1",
            "state": "failed_closed",
            "error": f"{type(error).__name__}: {error}",
            "model_request_timeout_sec": model_request_timeout_sec,
            "traceback": traceback.format_exc(),
        }
        write_json(destination / "failure.json", failure)
        write_json(destination / "manifest.json", {**preflight, "state": "failed_closed"})
        raise
