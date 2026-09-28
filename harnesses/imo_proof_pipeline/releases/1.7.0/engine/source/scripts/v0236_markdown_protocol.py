"""Strict Markdown records and typed argument DSL for the v0236 experiment.

No function in this module parses or emits JSON.  Python mappings are internal
values used to call the frozen exact executor after the model-authored Markdown
record passes deterministic validation.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")
CONFIG_KEY = re.compile(r"^[a-z][a-z0-9_]*$")
ARGUMENT_LINE = re.compile(r"^([a-z][a-z0-9_]*) = (.+)$")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n").rstrip() + "\n", encoding="utf-8")


def fenced_body(markdown: str, language: str, heading: str) -> str:
    pattern = re.compile(
        rf"\A# {re.escape(heading)}\n\n```{re.escape(language)}\n(?P<body>[\s\S]*?)\n```\s*\Z"
    )
    match = pattern.fullmatch(markdown.replace("\r\n", "\n").strip())
    if match is None:
        raise ValueError(f"expected one {language} fence under heading {heading!r}")
    return match.group("body")


def parse_config(markdown: str) -> dict[str, Any]:
    body = fenced_body(markdown, "experiment-config", "Experiment Configuration")
    repeated = {"problem_id", "allowed_tool"}
    values: dict[str, Any] = {key: [] for key in repeated}
    for line_number, line in enumerate(body.splitlines(), start=1):
        match = ARGUMENT_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid configuration line {line_number}")
        key, raw = match.groups()
        if CONFIG_KEY.fullmatch(key) is None:
            raise ValueError(f"invalid configuration key {key!r}")
        if key in repeated:
            values[key].append(raw)
        elif key in values:
            raise ValueError(f"duplicate scalar configuration key {key!r}")
        else:
            values[key] = raw
    integer_keys = {
        "master_seed",
        "auditor_thinking_token_budget",
        "auditor_max_tokens",
        "auditor_attempts",
        "matcher_thinking_token_budget",
        "matcher_max_tokens",
        "matcher_attempts",
        "compiler_thinking_token_budget",
        "compiler_max_tokens",
        "compiler_attempts",
        "bridge_thinking_token_budget",
        "bridge_max_tokens",
        "bridge_attempts",
        "proof_audit_thinking_token_budget",
        "proof_audit_max_tokens",
        "proof_audit_attempts",
        "budget_rounds",
        "continuation_max_tokens",
        "rewrite_max_tokens",
        "max_audit_claims",
        "tool_timeout_sec",
        "tool_memory_mb",
        "model_timeout_sec",
        "max_workers",
    }
    float_keys = {
        "auditor_temperature",
        "matcher_temperature",
        "compiler_temperature",
        "bridge_temperature",
        "proof_audit_temperature",
    }
    for key in integer_keys:
        if key not in values or re.fullmatch(r"[0-9]+", str(values[key])) is None:
            raise ValueError(f"missing or invalid integer configuration {key!r}")
        values[key] = int(values[key])
    for key in float_keys:
        if key not in values:
            raise ValueError(f"missing float configuration {key!r}")
        values[key] = float(values[key])
    required_strings = {"source_run", "model"}
    if not required_strings <= set(values):
        raise ValueError("missing source_run or model")
    if len(values["problem_id"]) < 8 or len(set(values["problem_id"])) != len(values["problem_id"]):
        raise ValueError("problem_id entries must contain at least eight unique IDs")
    if not values["allowed_tool"] or len(set(values["allowed_tool"])) != len(values["allowed_tool"]):
        raise ValueError("allowed_tool entries must be unique and nonempty")
    return values


def exact_sections(markdown: str, headings: list[str]) -> dict[str, str]:
    text = markdown.replace("\r\n", "\n").strip()
    # Treat ``# Heading: value`` as a surface-format variant of the existing
    # two-line section form.  Only caller-declared headings are eligible, and
    # fenced blocks are left byte-for-byte untouched.  All ordering,
    # duplication, nonempty-content, and downstream semantic checks remain in
    # force after this mechanical canonicalization.
    heading_set = set(headings)
    normalized_lines: list[str] = []
    inside_fence = False
    inline_heading = re.compile(r"^# ([^:\n]+):[ \t]*(.*)$")
    for line in text.splitlines():
        if line.startswith("```"):
            inside_fence = not inside_fence
        match = None if inside_fence else inline_heading.fullmatch(line)
        if match is not None and match.group(1) in heading_set:
            normalized_lines.extend((f"# {match.group(1)}", "", match.group(2)))
        else:
            normalized_lines.append(line)
    text = "\n".join(normalized_lines).strip()
    positions: list[tuple[int, str]] = []
    for heading in headings:
        marker = f"# {heading}\n"
        found = text.find(marker)
        if found < 0:
            raise ValueError(f"missing heading {heading!r}")
        if text.find(marker, found + 1) >= 0:
            raise ValueError(f"duplicate heading {heading!r}")
        positions.append((found, heading))
    if [heading for _, heading in sorted(positions)] != headings:
        raise ValueError("headings are out of order")
    if positions[0][0] != 0:
        raise ValueError("text before first heading")
    result: dict[str, str] = {}
    for index, (start, heading) in enumerate(positions):
        content_start = start + len(f"# {heading}\n")
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        content = text[content_start:end].strip()
        if not content:
            raise ValueError(f"empty section {heading!r}")
        result[heading] = content
    return result


def parse_prefixed_list(section: str, prefix: str | None = None) -> list[str]:
    rows: list[str] = []
    for line in section.splitlines():
        if not line.startswith("- "):
            raise ValueError("list line must begin with '- '")
        value = line[2:].strip()
        if prefix is not None:
            marker = prefix + ":"
            if not value.startswith(marker):
                raise ValueError(f"list item must begin with {marker!r}")
            value = value[len(marker) :].strip()
        if not value:
            raise ValueError("empty list item")
        rows.append(value)
    return rows


def parse_auditor(markdown: str, max_claims: int = 3) -> dict[str, Any]:
    sections = exact_sections(
        markdown, ["Theorem Goal", "Proof Obligations", "Checkable Claims"]
    )
    goal = sections["Theorem Goal"]
    if "\n" in goal:
        raise ValueError("theorem goal must be one paragraph")
    obligations: list[str] = []
    for index, line in enumerate(sections["Proof Obligations"].splitlines(), start=1):
        marker = f"- O{index}: "
        if not line.startswith(marker) or not line[len(marker) :].strip():
            raise ValueError("obligations must be sequential O1, O2, ... list items")
        obligations.append(line[len(marker) :].strip())
    claims_text = sections["Checkable Claims"]
    if claims_text == "NONE":
        claims: list[dict[str, str]] = []
    else:
        claims = []
        blocks = re.split(r"(?m)^## C([1-3])\n", claims_text)
        if blocks[0].strip():
            raise ValueError("text before first claim")
        if len(blocks) % 2 != 1:
            raise ValueError("malformed claim blocks")
        for position in range(1, len(blocks), 2):
            claim_number = blocks[position]
            expected = str(len(claims) + 1)
            if claim_number != expected:
                raise ValueError("claims must be sequential C1, C2, C3")
            lines = blocks[position + 1].strip().splitlines()
            prefixes = ("- Claim: ", "- Why load-bearing: ", "- Desired exact fact: ")
            if len(lines) != len(prefixes) or any(
                not line.startswith(prefix) or not line[len(prefix) :].strip()
                for line, prefix in zip(lines, prefixes)
            ):
                raise ValueError("claim block fields are malformed")
            claims.append(
                {
                    "claim_id": f"C{claim_number}",
                    "claim": lines[0][len(prefixes[0]) :].strip(),
                    "why_load_bearing": lines[1][len(prefixes[1]) :].strip(),
                    "desired_exact_fact": lines[2][len(prefixes[2]) :].strip(),
                }
            )
    if len(claims) > max_claims:
        raise ValueError("too many checkable claims")
    return {"theorem_goal": goal, "proof_obligations": obligations, "claims": claims}


def render_auditor(record: Mapping[str, Any]) -> str:
    obligations = "\n".join(
        f"- O{index}: {value}"
        for index, value in enumerate(record["proof_obligations"], start=1)
    )
    claims = record["claims"]
    claims_text = "NONE" if not claims else "\n".join(
        "\n".join(
            (
                f"## {row['claim_id']}",
                f"- Claim: {row['claim']}",
                f"- Why load-bearing: {row['why_load_bearing']}",
                f"- Desired exact fact: {row['desired_exact_fact']}",
            )
        )
        for row in claims
    )
    return (
        f"# Theorem Goal\n\n{record['theorem_goal']}\n\n"
        f"# Proof Obligations\n\n{obligations}\n\n"
        f"# Checkable Claims\n\n{claims_text}"
    )


def parse_matcher(markdown: str, operations: Iterable[str]) -> dict[str, Any]:
    sections = exact_sections(
        markdown, ["Decision", "Operation", "Immutable Claim", "Fit Rationale"]
    )
    decision = sections["Decision"]
    operation = sections["Operation"]
    claim = sections["Immutable Claim"]
    rationale = sections["Fit Rationale"]
    if any("\n" in value for value in (decision, operation, claim, rationale)):
        raise ValueError("matcher sections must each be one paragraph")
    allowed = frozenset(operations)
    if decision == "NO_TOOL":
        if operation != "none" or claim != "NONE":
            raise ValueError("NO_TOOL requires operation 'none' and claim 'NONE'")
        call_requested = False
    elif decision == "CALL_TOOL":
        if operation not in allowed or claim == "NONE":
            raise ValueError("CALL_TOOL operation or claim is invalid")
        call_requested = True
    else:
        raise ValueError("decision must be CALL_TOOL or NO_TOOL")
    return {
        "decision": decision,
        "operation": operation,
        "claim": "" if claim == "NONE" else claim,
        "fit_rationale": rationale,
        "call_requested": call_requested,
    }


def render_matcher(record: Mapping[str, Any]) -> str:
    claim = str(record.get("claim") or "NONE")
    return (
        f"# Decision\n\n{record['decision']}\n\n"
        f"# Operation\n\n{record['operation']}\n\n"
        f"# Immutable Claim\n\n{claim}\n\n"
        f"# Fit Rationale\n\n{record['fit_rationale']}"
    )


def tokenize_sexpr(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    token_pattern = re.compile(r"\s*(\(|\)|-?[0-9]+|[A-Za-z_][A-Za-z0-9_]*)")
    while index < len(text):
        match = token_pattern.match(text, index)
        if match is None:
            raise ValueError(f"invalid expression token near {text[index:index + 20]!r}")
        tokens.append(match.group(1))
        index = match.end()
    if not tokens:
        raise ValueError("empty expression")
    return tokens


def parse_sexpr(text: str) -> Any:
    tokens = tokenize_sexpr(text)
    position = 0

    def consume() -> Any:
        nonlocal position
        if position >= len(tokens):
            raise ValueError("unexpected end of expression")
        token = tokens[position]
        position += 1
        if token == "(":
            result: list[Any] = []
            while True:
                if position >= len(tokens):
                    raise ValueError("unclosed expression")
                if tokens[position] == ")":
                    position += 1
                    if not result:
                        raise ValueError("empty expression list")
                    return result
                result.append(consume())
        if token == ")":
            raise ValueError("unexpected closing parenthesis")
        return int(token) if re.fullmatch(r"-?[0-9]+", token) else token

    parsed = consume()
    if position != len(tokens):
        raise ValueError("trailing expression tokens")
    return parsed


def expression_ast(node: Any, *, finite: bool = False) -> Any:
    if isinstance(node, int):
        return node
    if not isinstance(node, list) or not node or not isinstance(node[0], str):
        raise ValueError("expression must be an integer or parenthesized form")
    head = node[0]
    args = node[1:]
    if head == "symbol" and len(args) == 1 and isinstance(args[0], str) and IDENTIFIER.fullmatch(args[0]):
        return {"symbol": args[0]}
    if head == "rational" and len(args) == 2 and all(isinstance(value, int) for value in args):
        return {"rational": list(args)}
    if finite and head == "var" and len(args) == 1 and isinstance(args[0], int):
        return {"var": args[0]}
    variadic = {"add", "mul"} | ({"and", "or"} if finite else set())
    binary = {"sub", "div", "pow"} | (
        {"mod", "eq", "ne", "lt", "le", "gt", "ge"} if finite else set()
    )
    unary = {"neg", "abs"} | ({"not"} if finite else set())
    if head in variadic and len(args) >= 2:
        return {head: [expression_ast(value, finite=finite) for value in args]}
    if head in binary and len(args) == 2:
        return {head: [expression_ast(value, finite=finite) for value in args]}
    if head in unary and len(args) == 1:
        return {head: expression_ast(args[0], finite=finite)}
    raise ValueError(f"unsupported expression form {head!r} with arity {len(args)}")


def parse_integer_list(value: str) -> list[int]:
    parts = [part.strip() for part in value.split(",")]
    if not parts or any(re.fullmatch(r"-?[0-9]+", part) is None for part in parts):
        raise ValueError("expected a comma-separated integer list")
    return [int(part) for part in parts]


def parse_symbol_list(value: str) -> list[str]:
    parts = [part.strip() for part in value.split(",")]
    if not parts or any(IDENTIFIER.fullmatch(part) is None for part in parts):
        raise ValueError("expected a comma-separated symbol list")
    if len(parts) != len(set(parts)):
        raise ValueError("symbols must be unique")
    return parts


def argument_multimap(markdown: str) -> dict[str, list[str]]:
    body = fenced_body(markdown, "tool-args", "Tool Arguments")
    fields: dict[str, list[str]] = {}
    for line_number, line in enumerate(body.splitlines(), start=1):
        match = ARGUMENT_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid tool-args line {line_number}")
        key, value = match.groups()
        fields.setdefault(key, []).append(value)
    return fields


def require_fields(
    fields: Mapping[str, list[str]],
    *,
    scalar: Iterable[str],
    repeated: Iterable[str] = (),
) -> None:
    scalar_set = set(scalar)
    repeated_set = set(repeated)
    if set(fields) != scalar_set | repeated_set:
        raise ValueError(
            f"tool argument fields differ: expected {sorted(scalar_set | repeated_set)}, got {sorted(fields)}"
        )
    if any(len(fields[key]) != 1 for key in scalar_set):
        raise ValueError("scalar tool argument repeated")
    if any(not fields[key] for key in repeated_set):
        raise ValueError("repeated tool argument missing")


def parse_condition(value: str) -> dict[str, Any]:
    if " :: " not in value:
        raise ValueError("condition must use 'relation :: expression'")
    relation, expression = value.split(" :: ", 1)
    if relation not in {"nonzero", "positive", "negative", "nonnegative"}:
        raise ValueError("unsupported condition relation")
    return {"relation": relation, "expression": expression_ast(parse_sexpr(expression))}


def parse_tool_arguments(markdown: str, expected_operation: str) -> dict[str, Any]:
    fields = argument_multimap(markdown)
    if fields.get("operation") != [expected_operation]:
        raise ValueError("compiler operation does not match immutable matcher selection")
    if expected_operation in {"expand_and_compare", "simplify_identity"}:
        require_fields(fields, scalar=("operation", "symbols", "left", "right"))
        return {
            "symbols": parse_symbol_list(fields["symbols"][0]),
            "left": expression_ast(parse_sexpr(fields["left"][0])),
            "right": expression_ast(parse_sexpr(fields["right"][0])),
        }
    if expected_operation == "factor_and_reexpand":
        require_fields(fields, scalar=("operation", "symbols", "expression"))
        return {
            "symbols": parse_symbol_list(fields["symbols"][0]),
            "expression": expression_ast(parse_sexpr(fields["expression"][0])),
        }
    if expected_operation == "solve_and_substitute":
        require_fields(
            fields,
            scalar=("operation", "symbols", "solve_for"),
            repeated=("equation",),
        )
        return {
            "symbols": parse_symbol_list(fields["symbols"][0]),
            "equations": [expression_ast(parse_sexpr(value)) for value in fields["equation"]],
            "solve_for": parse_symbol_list(fields["solve_for"][0]),
        }
    if expected_operation == "polynomial_root_filter":
        require_fields(
            fields,
            scalar=("operation", "symbols", "polynomial", "variable", "domain"),
        )
        domain = fields["domain"][0]
        if domain not in {"complex", "real", "positive", "nonnegative", "integer"}:
            raise ValueError("unsupported polynomial root domain")
        variable = fields["variable"][0]
        if IDENTIFIER.fullmatch(variable) is None:
            raise ValueError("invalid polynomial variable")
        return {
            "symbols": parse_symbol_list(fields["symbols"][0]),
            "polynomial": expression_ast(parse_sexpr(fields["polynomial"][0])),
            "variable": variable,
            "domain": domain,
        }
    if expected_operation == "exact_modular_evaluation":
        require_fields(fields, scalar=("operation", "base", "exponent", "modulus"))
        values = {
            key: int(fields[key][0])
            for key in ("base", "exponent", "modulus")
            if re.fullmatch(r"-?[0-9]+", fields[key][0])
        }
        if set(values) != {"base", "exponent", "modulus"}:
            raise ValueError("modular arguments must be integers")
        return values
    if expected_operation == "gcd":
        require_fields(fields, scalar=("operation", "values"))
        return {"values": parse_integer_list(fields["values"][0])}
    if expected_operation == "prime_factorization":
        require_fields(fields, scalar=("operation", "value"))
        if re.fullmatch(r"-?[0-9]+", fields["value"][0]) is None:
            raise ValueError("factorization value must be an integer")
        return {"value": int(fields["value"][0])}
    if expected_operation == "determinant":
        require_fields(fields, scalar=("operation",), repeated=("row",))
        return {"matrix": [parse_integer_list(value) for value in fields["row"]]}
    if expected_operation == "enumerate_finite_assignments":
        require_fields(
            fields,
            scalar=("operation",),
            repeated=("domain_values", "constraint"),
        )
        return {
            "domains": [parse_integer_list(value) for value in fields["domain_values"]],
            "constraints": [
                expression_ast(parse_sexpr(value), finite=True)
                for value in fields["constraint"]
            ],
        }
    if expected_operation == "exact_branch_system":
        scalar_fields = {
            "operation",
            "task",
            "symbols",
            "partition",
            "branch_id",
            "solve_for",
            "output_expression",
            "aggregate",
        }
        required_fields = scalar_fields | {"original_equation"}
        allowed_fields = required_fields | {"common_condition"}
        if not required_fields <= set(fields) or not set(fields) <= allowed_fields:
            raise ValueError("exact branch fields are missing or unexpected")
        if any(len(fields[key]) != 1 for key in scalar_fields):
            raise ValueError("exact branch scalar field repeated")
        if fields["partition"][0] != "exhaustive_solutions":
            raise ValueError("Markdown DSL supports only exhaustive_solutions partition")
        if fields["aggregate"][0] != "union":
            raise ValueError("exact branch aggregate must be union")
        task = fields["task"][0]
        branch_id = fields["branch_id"][0]
        if IDENTIFIER.fullmatch(task) is None or IDENTIFIER.fullmatch(branch_id) is None:
            raise ValueError("invalid task or branch identifier")
        common = [parse_condition(value) for value in fields.get("common_condition", [])]
        extra_fields = set(fields) - {
            "operation",
            "task",
            "symbols",
            "original_equation",
            "common_condition",
            "partition",
            "branch_id",
            "solve_for",
            "output_expression",
            "aggregate",
        }
        if extra_fields:
            raise ValueError(f"unexpected exact branch fields: {sorted(extra_fields)}")
        return {
            "task": task,
            "symbols": parse_symbol_list(fields["symbols"][0]),
            "original_equations": [
                expression_ast(parse_sexpr(value)) for value in fields["original_equation"]
            ],
            "common_conditions": common,
            "partition": {"kind": "exhaustive_solutions"},
            "branches": [{"branch_id": branch_id, "equations": [], "conditions": []}],
            "solve_for": parse_symbol_list(fields["solve_for"][0]),
            "output_expression": expression_ast(parse_sexpr(fields["output_expression"][0])),
            "aggregate": "union",
        }
    raise ValueError(f"unsupported Markdown compiler operation {expected_operation!r}")


AUDIT_LABELS = (
    "Whole proof",
    "All original outputs answered",
    "Verified results causally used",
    "Completion and equality cases handled",
    "Sound reasoning preserved or replaced",
    "No meta or local worksheet",
)


def parse_proof_audit(markdown: str) -> dict[str, Any]:
    sections = exact_sections(markdown, ["Whole-Proof Audit", "Issues"])
    lines = sections["Whole-Proof Audit"].splitlines()
    if len(lines) != len(AUDIT_LABELS):
        raise ValueError("wrong number of proof audit fields")
    result: dict[str, Any] = {}
    for line, label in zip(lines, AUDIT_LABELS):
        marker = f"- {label}: "
        if not line.startswith(marker):
            raise ValueError(f"missing audit field {label!r}")
        verdict = line[len(marker) :]
        if verdict not in {"PASS", "FAIL"}:
            raise ValueError("audit verdict must be PASS or FAIL")
        result[label] = verdict == "PASS"
    issues_section = sections["Issues"]
    result["issues"] = [] if issues_section == "NONE" else parse_prefixed_list(issues_section)
    result["passed"] = all(result[label] for label in AUDIT_LABELS)
    return result


def render_proof_audit(record: Mapping[str, Any]) -> str:
    verdicts = "\n".join(
        f"- {label}: {'PASS' if record[label] else 'FAIL'}" for label in AUDIT_LABELS
    )
    issues = record.get("issues") or []
    issue_text = "NONE" if not issues else "\n".join(f"- {issue}" for issue in issues)
    return f"# Whole-Proof Audit\n\n{verdicts}\n\n# Issues\n\n{issue_text}"


def parse_bridge(markdown: str, event_indexes: list[int]) -> dict[str, Any]:
    sections = exact_sections(
        markdown,
        ["Event Bridges", "Preserve Reasoning", "Replace Reasoning", "Global Completion Plan"],
    )
    bridge_text = sections["Event Bridges"]
    blocks = re.split(r"(?m)^## Event ([1-9][0-9]*)\n", bridge_text)
    if blocks[0].strip() or len(blocks) % 2 != 1:
        raise ValueError("malformed event bridge blocks")
    bridges: list[dict[str, Any]] = []
    for position in range(1, len(blocks), 2):
        event_index = int(blocks[position])
        lines = blocks[position + 1].strip().splitlines()
        prefixes = (
            "- Checked lemma: ",
            "- Downstream obligations: ",
            "- Connection to original conclusion: ",
        )
        if len(lines) != len(prefixes) or any(
            not line.startswith(prefix) or not line[len(prefix) :].strip()
            for line, prefix in zip(lines, prefixes)
        ):
            raise ValueError("malformed bridge fields")
        downstream = [
            part.strip() for part in lines[1][len(prefixes[1]) :].split(";") if part.strip()
        ]
        if not downstream:
            raise ValueError("bridge has no downstream obligation")
        bridges.append(
            {
                "event_index": event_index,
                "checked_lemma": lines[0][len(prefixes[0]) :].strip(),
                "downstream_obligations": downstream,
                "connection_to_original_conclusion": lines[2][len(prefixes[2]) :].strip(),
            }
        )
    if sorted(row["event_index"] for row in bridges) != sorted(event_indexes):
        raise ValueError("bridge does not cover every event exactly once")

    def optional_list(name: str) -> list[str]:
        value = sections[name]
        return [] if value == "NONE" else parse_prefixed_list(value)

    plan_lines = sections["Global Completion Plan"].splitlines()
    plan: list[str] = []
    for index, line in enumerate(plan_lines, start=1):
        marker = f"{index}. "
        if not line.startswith(marker) or not line[len(marker) :].strip():
            raise ValueError("completion plan must be a sequential numbered list")
        plan.append(line[len(marker) :].strip())
    return {
        "bridges": bridges,
        "preserve_reasoning": optional_list("Preserve Reasoning"),
        "replace_reasoning": optional_list("Replace Reasoning"),
        "global_completion_plan": plan,
    }


def render_bridge(record: Mapping[str, Any]) -> str:
    bridge_text = "\n".join(
        "\n".join(
            (
                f"## Event {row['event_index']}",
                f"- Checked lemma: {row['checked_lemma']}",
                "- Downstream obligations: " + "; ".join(row["downstream_obligations"]),
                "- Connection to original conclusion: " + row["connection_to_original_conclusion"],
            )
        )
        for row in record["bridges"]
    )

    def bullets(values: Iterable[str]) -> str:
        rows = list(values)
        return "NONE" if not rows else "\n".join(f"- {row}" for row in rows)

    plan = "\n".join(
        f"{index}. {row}" for index, row in enumerate(record["global_completion_plan"], start=1)
    )
    return (
        f"# Event Bridges\n\n{bridge_text}\n\n"
        f"# Preserve Reasoning\n\n{bullets(record['preserve_reasoning'])}\n\n"
        f"# Replace Reasoning\n\n{bullets(record['replace_reasoning'])}\n\n"
        f"# Global Completion Plan\n\n{plan}"
    )


def scalar_text(value: Any) -> str:
    if value is None:
        return "none"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value).replace("\n", " ").strip()


def flatten_facts(value: Any, prefix: str = "fact") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        if not value:
            rows.append((prefix, "empty mapping"))
        for key in sorted(value, key=str):
            rows.extend(flatten_facts(value[key], f"{prefix}.{key}"))
    elif isinstance(value, (list, tuple)):
        if not value:
            rows.append((prefix, "empty list"))
        for index, item in enumerate(value, start=1):
            rows.extend(flatten_facts(item, f"{prefix}[{index}]"))
    else:
        rows.append((prefix, scalar_text(value)))
    return rows


def render_execution_event(event: Mapping[str, Any]) -> str:
    facts: list[tuple[str, str]] = []
    facts.extend(flatten_facts(event.get("normalized_result"), "result"))
    facts.extend(flatten_facts(event.get("certificate"), "certificate"))
    fact_text = "\n".join(f"- {path}: {value}" for path, value in facts)
    return (
        f"# Verified Exact Event {event['event_index']}\n\n"
        f"## Requested Claim\n\n{event['claim']}\n\n"
        f"## Operation\n\n{event['operation']}\n\n"
        f"## Validation\n\n{event['validation_status']}\n\n"
        f"## Returned Facts\n\n{fact_text}"
    )


def render_key_values(heading: str, values: Mapping[str, Any]) -> str:
    rows = "\n".join(f"- {key}: {scalar_text(value)}" for key, value in values.items())
    return f"# {heading}\n\n{rows}"


def hash_manifest(root: Path, *, exclude_names: frozenset[str] = frozenset()) -> str:
    rows: list[str] = ["# Artifact Hash Manifest", ""]
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        if path.name in exclude_names:
            continue
        relative = path.relative_to(root)
        digest = sha256_text(path.read_text(encoding="utf-8"))
        rows.append(f"- `{relative}`: `{digest}`")
    return "\n".join(rows)
