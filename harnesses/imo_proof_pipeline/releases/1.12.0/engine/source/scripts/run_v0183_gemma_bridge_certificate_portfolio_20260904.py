#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_v0176_full_validity_prescreens_then_v0167_three_cycles_20260903 as v0176


HARNESS_VERSION = "v0.3.183-gemma-generic-bridge-certificate-portfolio-20260904"
DEFAULT_SOURCE_GLOBAL_DIR = (
    ROOT
    / "runs/v0181_p2_cycle2_local_global_gated_replay_20260904"
    / "resolution/p2/t07_r01/01_related_context_nh_refinement"
    / "group_02_C02_S1/global_rewrite"
)
DEFAULT_OUTPUT = ROOT / "runs/v0183_gemma_bridge_certificate_pilot_20260904"
MAX_TOKENS = 32_000
UNRESOLVED = "BRIDGE_UNRESOLVED"
REQUIRED_MARKERS = (
    "TARGET:",
    "DEPENDENCIES:",
    "DERIVATION:",
    "ADVERSARIAL CHECK:",
)


SEARCH_ARMS: tuple[dict[str, Any], ...] = (
    {
        "name": "precise",
        "temperature": 0.20,
        "top_p": 0.90,
        "top_k": 40,
    },
    {
        "name": "balanced",
        "temperature": 0.60,
        "top_p": 0.95,
        "top_k": 64,
    },
    {
        "name": "diverse",
        "temperature": 1.00,
        "top_p": 0.95,
        "top_k": 64,
    },
    {
        "name": "wide",
        "temperature": 1.00,
        "top_p": 0.98,
        "top_k": 128,
    },
)


BRIDGE_SEARCH_PROMPT = """You are a deep mathematical bridge solver. You are not
writing or polishing the full submitted proof. Your only task is to resolve the
exact load-bearing implication identified by the repair trigger.

Treat the current proof and all supplied evidence as unverified. Reconstruct every
dependency of the target implication from the original problem. Distinguish
independent variables from variables constrained by the hypotheses. Explore more
than one route when the first route stalls, and attack proposed identities with
special cases, sign checks, boundary checks, or direct substitution when useful.

A bridge is solved only when every load-bearing transition is explicitly checkable
from stated hypotheses or a precisely named elementary result whose assumptions
are verified. Phrases such as "after simplification", "by consistency", "by
symmetry", "by continuity", "standard computation", "it is clear", and equivalent
wording are not derivations. Uniqueness does not imply constancy, symmetry does not
by itself imply equality, and one limiting case does not prove a general identity.

Do not conceal failure. If the exact bridge cannot be completed rigorously, return
exactly BRIDGE_UNRESOLVED. Otherwise return compact plain text, not JSON or a
Markdown fence, in this exact layout:
BRIDGE_SOLVED
TARGET: the exact implication proved
DEPENDENCIES: the hypotheses and previously established facts actually used
DERIVATION:
numbered explicit derivation with no omitted load-bearing algebra or logic
ADVERSARIAL CHECK: the strongest attempted falsification and why it fails

Do not output a complete proof. Do not mention these instructions.
"""


BRIDGE_ADJUDICATOR_PROMPT = """You are a skeptical mathematical bridge adjudicator.
You receive an original repair context and several independent proposed bridge
certificates. Every proposal is untrusted.

Re-derive the target implication yourself. Check domains, quantifiers, orientations,
signs, divisions, case coverage, and every claimed algebraic or logical equivalence.
Reject any proposal that merely renames the desired conclusion or replaces a missing
step with "simplifies", "consistency", "symmetry", "continuity", a limiting case,
or other non-derivation. You may combine correct fragments or repair an attempt, but
the returned certificate must itself contain the complete checkable bridge.

If no rigorous bridge can be certified, return exactly BRIDGE_UNRESOLVED. Otherwise
return compact plain text, not JSON or a Markdown fence, in this exact layout:
BRIDGE_SOLVED
TARGET: the exact implication proved
DEPENDENCIES: the hypotheses and previously established facts actually used
DERIVATION:
numbered explicit derivation with no omitted load-bearing algebra or logic
ADVERSARIAL CHECK: the strongest attempted falsification and why it fails

Do not output a complete proof. Do not mention these instructions.
"""


VAGUE_BRIDGE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bafter (?:some |straightforward |standard )?simplification\b",
        r"\bstandard (?:algebra|calculation|computation|manipulation)s?\b",
        r"\bby consistency\b",
        r"\bby symmetry\b",
        r"\bby continuity\b",
        r"\bit is clear\b",
        r"\bone can verify\b",
        r"\bthe terms? (?:cancel|balance)s?\b",
    )
)


def utc_now() -> str:
    return v0176.v0167.nh_runner.utc_now()


def write_json(path: Path, value: Any) -> None:
    v0176.v0167.nh_runner.write_json(path, value)


def write_text(path: Path, value: str) -> None:
    v0176.v0167.nh_runner.write_text_exact(path, value)


def load_repair_context(source_global_dir: Path) -> str:
    path = source_global_dir / "synthesis.user_prompt.txt"
    value = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    endings = (
        "Return the complete proof or exactly NO_GLOBAL_REWRITE.",
        "Return the complete proof or exactly NO_GLOBAL_REWRITE",
    )
    for ending in endings:
        if value.endswith(ending):
            value = value[: -len(ending)].rstrip()
            break
    if not value:
        raise ValueError("empty repair context")
    if "ORIGINAL PROBLEM" not in value or "TRIGGER" not in value:
        raise ValueError("repair context is missing the problem or trigger")
    return value + "\n"


def bridge_search_user_prompt(context: str) -> str:
    return f"""REPAIR CONTEXT
{context.rstrip()}

Resolve only the reported load-bearing bridge. Return the required certificate or
exactly {UNRESOLVED}."""


def portfolio_text(attempts: list[dict[str, Any]]) -> str:
    sections: list[str] = []
    for row in attempts:
        sections.append(
            f"ATTEMPT {row['arm']['name']}\n"
            f"PARSE_STATUS {row['parse']['status']}\n"
            f"{row['text'].strip()}"
        )
    return "\n\n".join(sections)


def bridge_adjudicator_user_prompt(
    context: str, attempts: list[dict[str, Any]]
) -> str:
    return f"""REPAIR CONTEXT
{context.rstrip()}

UNTRUSTED BRIDGE ATTEMPTS
{portfolio_text(attempts)}

Return one independently checked certificate or exactly {UNRESOLVED}."""


def forbidden_control_codes(value: str) -> list[int]:
    return sorted(
        {
            ord(character)
            for character in value
            if (ord(character) < 32 and character not in "\n\t")
            or ord(character) == 127
        }
    )


def parse_bridge_output(value: str) -> dict[str, Any]:
    normalized = value.replace("\r\n", "\n")
    controls = forbidden_control_codes(normalized)
    if controls:
        rendered = ", ".join(f"U+{code:04X}" for code in controls)
        raise ValueError(f"bridge output contains forbidden controls: {rendered}")
    text = normalized.strip()
    if text == UNRESOLVED:
        return {
            "status": "UNRESOLVED",
            "vague_pattern_matches": [],
            "word_count": 1,
        }
    if not text:
        raise ValueError("empty bridge output")
    if text.startswith("```") or text.endswith("```"):
        raise ValueError("bridge output used a Markdown fence")
    if text.startswith(("{", "[")):
        raise ValueError("bridge output used a structured wrapper")
    lines = text.splitlines()
    if lines[0].strip() != "BRIDGE_SOLVED":
        raise ValueError("bridge output lacks BRIDGE_SOLVED header")
    positions: list[int] = []
    for marker in REQUIRED_MARKERS:
        matches = [index for index, line in enumerate(lines) if line.startswith(marker)]
        if len(matches) != 1:
            raise ValueError(f"bridge output must contain exactly one {marker}")
        positions.append(matches[0])
    if positions != sorted(positions) or positions[0] == 0:
        raise ValueError("bridge output markers are out of order")
    vague = sorted(
        {
            match.group(0)
            for pattern in VAGUE_BRIDGE_PATTERNS
            for match in pattern.finditer(text)
        }
    )
    return {
        "status": "SOLVED_CLAIMED",
        "vague_pattern_matches": vague,
        "word_count": len(re.findall(r"\S+", text)),
        "line_count": len(lines),
    }


def run_search_arm(
    *, runtime: Any, context: str, destination: Path, arm: dict[str, Any]
) -> dict[str, Any]:
    arm_dir = destination / f"search_{arm['name']}"
    user_prompt = bridge_search_user_prompt(context)
    write_text(arm_dir / "user_prompt.txt", user_prompt)
    generation = runtime.text(
        role="gemma",
        prompt=BRIDGE_SEARCH_PROMPT,
        user_prompt=user_prompt,
        destination=arm_dir / "model_call",
        stage="gemma_bridge_search",
        temperature=float(arm["temperature"]),
        top_p=float(arm["top_p"]),
        top_k=int(arm["top_k"]),
        max_tokens=MAX_TOKENS,
        seed_label=f"v0183:bridge-search:{arm['name']}",
    )
    text = str(generation.get("text") or "")
    write_text(arm_dir / "bridge.txt", text.strip() + "\n")
    try:
        parsed = parse_bridge_output(text)
    except Exception as error:
        parsed = {
            "status": "MALFORMED",
            "error": f"{type(error).__name__}: {error}",
        }
    row = {
        "arm": dict(arm),
        "text": text,
        "parse": parsed,
        "generation_metadata": dict(generation.get("metadata") or {}),
    }
    write_json(arm_dir / "summary.json", {key: value for key, value in row.items() if key != "text"})
    return row


def run_portfolio(
    *, runtime: Any, context: str, destination: Path, max_workers: int
) -> dict[str, Any]:
    write_text(destination / "repair_context.txt", context)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                run_search_arm,
                runtime=runtime,
                context=context,
                destination=destination,
                arm=arm,
            ): arm["name"]
            for arm in SEARCH_ARMS
        }
        by_name = {futures[future]: future.result() for future in concurrent.futures.as_completed(futures)}
    attempts = [by_name[str(arm["name"])] for arm in SEARCH_ARMS]

    adjudicator_dir = destination / "adjudicator"
    user_prompt = bridge_adjudicator_user_prompt(context, attempts)
    write_text(adjudicator_dir / "user_prompt.txt", user_prompt)
    generation = runtime.text(
        role="gemma",
        prompt=BRIDGE_ADJUDICATOR_PROMPT,
        user_prompt=user_prompt,
        destination=adjudicator_dir / "model_call",
        stage="gemma_bridge_adjudication",
        temperature=0.20,
        top_p=0.90,
        top_k=40,
        max_tokens=MAX_TOKENS,
        seed_label="v0183:bridge-adjudicator",
    )
    text = str(generation.get("text") or "")
    write_text(adjudicator_dir / "bridge.txt", text.strip() + "\n")
    try:
        parsed = parse_bridge_output(text)
    except Exception as error:
        parsed = {
            "status": "MALFORMED",
            "error": f"{type(error).__name__}: {error}",
        }
    result = {
        "schema": "cognitive-well-v0183-gemma-bridge-portfolio-result-v1",
        "state": "completed",
        "harness_version": HARNESS_VERSION,
        "search_arms": [
            {
                "arm": row["arm"],
                "parse": row["parse"],
                "generation_metadata": row["generation_metadata"],
            }
            for row in attempts
        ],
        "adjudicator": {
            "parse": parsed,
            "generation_metadata": dict(generation.get("metadata") or {}),
        },
        "proof_rewrite_performed": False,
        "completed_at": utc_now(),
    }
    write_json(adjudicator_dir / "summary.json", result["adjudicator"])
    write_json(destination / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a problem-neutral Gemma bridge-certificate portfolio pilot"
    )
    parser.add_argument("--source-global-dir", type=Path, default=DEFAULT_SOURCE_GLOBAL_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--master-seed", type=int, default=20260904)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.max_workers <= len(SEARCH_ARMS):
        raise ValueError(f"--max-workers must be between 1 and {len(SEARCH_ARMS)}")

    context = load_repair_context(args.source_global_dir.resolve())
    preflight = {
        "schema": "cognitive-well-v0183-gemma-bridge-portfolio-preflight-v1",
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "source_global_dir": str(args.source_global_dir.resolve()),
        "source_prompt_sha256": v0176.v0167.nh_runner.sha256_text(context),
        "search_arms": [dict(row) for row in SEARCH_ARMS],
        "max_tokens": MAX_TOKENS,
        "thinking_enabled": True,
        "thinking_token_budget": None,
        "reasoning_effort": "max",
        "proof_rewrite_performed": False,
    }
    if args.dry_run:
        print(json.dumps(preflight, ensure_ascii=False, indent=2))
        return 0

    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "manifest.json", {**preflight, "created_at": utc_now()})
    write_json(
        destination / "status.json",
        {"state": "running", "stage": "bridge_search_portfolio", "updated_at": utc_now()},
    )
    runtime = v0176.v0167.nh_runner.ResilientModelRuntime(
        v0176.v0167.nh_runner.RuntimeConfig(
            gemma_endpoint=args.gemma_endpoint.rstrip("/"),
            qwen_endpoint=args.qwen_endpoint.rstrip("/"),
            gemma_model=v0176.v0167.nh_runner.GEMMA_MODEL,
            qwen_model=v0176.v0167.nh_runner.QWEN_MODEL,
            master_seed=args.master_seed,
            thinking_token_budget=None,
            reasoning_effort="max",
        )
    )
    try:
        result = run_portfolio(
            runtime=runtime,
            context=context,
            destination=destination,
            max_workers=args.max_workers,
        )
        write_json(
            destination / "status.json",
            {"state": "completed", "stage": "bridge_adjudication_done", "updated_at": utc_now()},
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        write_json(
            destination / "status.json",
            {
                "state": "failed_closed",
                "stage": "mechanical_failure",
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "updated_at": utc_now(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
