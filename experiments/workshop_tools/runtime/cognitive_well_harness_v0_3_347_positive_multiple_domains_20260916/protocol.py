from __future__ import annotations

import re
from typing import Any, Mapping

import scripts.v0236_markdown_protocol as mdp
from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    protocol as tool_protocol,
)


SEMANTIC_PREFIXES = (
    "- Formal source: ",
    "- Target meaning: ",
    "- Guard use: ",
    "- Proof consequence: ",
    "- Required conclusion: ",
)
IDENTITY_LABEL = re.compile(r"^I([1-9][0-9]*)$")
CONCLUSION_LABEL = re.compile(r"^C1$")
RELATION_LABEL = re.compile(r"^D[1-9][0-9]*$")
GUARD_LABEL = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
MAX_SEMANTIC_CHARS = 1_000
MAX_IDENTITIES = 12


def _render_ast(node: Any) -> str:
    if isinstance(node, bool):
        raise ValueError("cannot render Boolean as a polynomial expression")
    if isinstance(node, int):
        return str(node)
    if not isinstance(node, Mapping) or len(node) != 1:
        raise ValueError("cannot render malformed certificate AST")
    head, value = next(iter(node.items()))
    if head == "symbol":
        return f"(symbol {value})"
    if head == "rational":
        return f"(rational {value[0]} {value[1]})"
    if isinstance(value, list):
        return "(" + head + " " + " ".join(_render_ast(item) for item in value) + ")"
    return f"({head} {_render_ast(value)})"


def _parse_semantics(section: str) -> dict[str, str]:
    lines = section.splitlines()
    if len(lines) != len(SEMANTIC_PREFIXES):
        raise ValueError("Certificate Semantics must contain exactly five lines")
    result: dict[str, str] = {}
    for line, prefix in zip(lines, SEMANTIC_PREFIXES, strict=True):
        if not line.startswith(prefix):
            raise ValueError(f"semantic line must begin with {prefix!r}")
        value = line[len(prefix) :].strip()
        if not value or len(value) > MAX_SEMANTIC_CHARS:
            raise ValueError("semantic value is empty or too long")
        key = prefix[2:-2].lower().replace(" ", "_")
        result[key] = value
    if len(result["required_conclusion"]) > 160:
        raise ValueError("Required conclusion must be a short theorem substring")
    # Ordinary Markdown math wrappers do not change the requested mathematics.
    value = result["required_conclusion"]
    for left, right in (("$$", "$$"), ("$", "$"), (r"\(", r"\)"), (r"\[", r"\]")):
        if value.startswith(left) and value.endswith(right) and len(value) > len(left) + len(right):
            result["required_conclusion"] = value[len(left):-len(right)].strip()
            break
    return result


def _parse_identity(value: str, *, conclusion: bool = False) -> dict[str, Any]:
    parts = value.split(" :: ")
    if len(parts) != 3:
        raise ValueError("identity must use 'label :: left AST :: right AST'")
    label, left, right = parts
    pattern = CONCLUSION_LABEL if conclusion else IDENTITY_LABEL
    if pattern.fullmatch(label) is None:
        raise ValueError("invalid certificate identity label")
    return {
        "label": label,
        "left": mdp.expression_ast(
            tool_protocol._parse_sexpr_with_diagnostics(  # noqa: SLF001
                left, field=f"certificate {label} left"
            )
        ),
        "right": mdp.expression_ast(
            tool_protocol._parse_sexpr_with_diagnostics(  # noqa: SLF001
                right, field=f"certificate {label} right"
            )
        ),
    }


def _program_fields(section: str) -> dict[str, list[str]]:
    body = mdp.fenced_body(
        "# Certificate Program\n\n" + section,
        "certificate-args",
        "Certificate Program",
    )
    fields: dict[str, list[str]] = {}
    for line_number, line in enumerate(body.splitlines(), start=1):
        match = mdp.ARGUMENT_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid certificate-args line {line_number}")
        key, value = match.groups()
        fields.setdefault(key, []).append(value)
    expected = {"symbols", "relation", "identity", "conclusion", "guard"}
    if not expected <= set(fields) or set(fields) - expected - {"define", "zero"}:
        raise ValueError(
            f"certificate fields differ: expected {sorted(expected)}, "
            f"got {sorted(fields)}"
        )
    if len(fields["symbols"]) != 1 or len(fields["conclusion"]) != 1:
        raise ValueError("symbols and conclusion are scalar fields")
    return fields


def parse_certificate(markdown: str) -> dict[str, Any]:
    """Parse one strict Markdown certificate proposal; JSON is never accepted."""

    sections = mdp.exact_sections(
        markdown, ["Certificate Semantics", "Certificate Program"]
    )
    semantics = _parse_semantics(sections["Certificate Semantics"])
    fields = _program_fields(sections["Certificate Program"])
    symbols = mdp.parse_symbol_list(fields["symbols"][0])

    relation_labels = fields["relation"]
    if (
        not relation_labels
        or any(RELATION_LABEL.fullmatch(item) is None for item in relation_labels)
        or len(relation_labels) != len(set(relation_labels))
    ):
        raise ValueError("relations must be unique D<number> labels")

    raw_identities = fields["identity"]
    if raw_identities == ["NONE"]:
        identities: list[dict[str, Any]] = []
    else:
        if "NONE" in raw_identities or len(raw_identities) > MAX_IDENTITIES:
            raise ValueError("identity list is malformed or exceeds the limit")
        identities = [_parse_identity(item) for item in raw_identities]
        expected_labels = [f"I{index}" for index in range(1, len(identities) + 1)]
        if [item["label"] for item in identities] != expected_labels:
            raise ValueError("identity labels must be consecutive I1, I2, ...")

    raw_guards = fields["guard"]
    if raw_guards == ["NONE"]:
        guards: list[str] = []
    else:
        if (
            "NONE" in raw_guards
            or any(GUARD_LABEL.fullmatch(item) is None for item in raw_guards)
            or len(raw_guards) != len(set(raw_guards))
        ):
            raise ValueError("guard list must contain unique identifiers or NONE")
        guards = raw_guards

    definitions = []
    for value in fields.get("define", []):
        parts = value.split(" :: ")
        if len(parts) != 2 or GUARD_LABEL.fullmatch(parts[0]) is None:
            raise ValueError("define requires name :: polynomial AST")
        definitions.append({"label": parts[0], "value": mdp.expression_ast(
            tool_protocol._parse_sexpr_with_diagnostics(parts[1], field="definition")
        )})
    zeros = []
    for value in fields.get("zero", []):
        parts = value.split(" :: ")
        if len(parts) != 4 or re.fullmatch(r"Z[1-9][0-9]*|C1", parts[0]) is None:
            raise ValueError("zero requires Z<number> or C1 :: value :: nonzero scale :: combination")
        zeros.append({"label": parts[0], **{
            field: mdp.expression_ast(tool_protocol._parse_sexpr_with_diagnostics(
                text, field=f"zero {parts[0]} {field}"))
            for field, text in zip(("value", "scale", "combination"), parts[1:], strict=True)
        }})
    if len(definitions) > 40 or len(zeros) > 24:
        raise ValueError("certificate exceeds definition/derivation limits")
    return {
        "schema": "cognitive-well-v0324-model-certificate-program-v1",
        "semantics": semantics,
        "symbols": symbols,
        "relations": relation_labels,
        "identities": identities,
        "conclusion": _parse_identity(fields["conclusion"][0], conclusion=True),
        "guards": guards,
        "definitions": definitions,
        "zeros": zeros,
    }


def render_program(program: Mapping[str, Any]) -> str:
    """Canonical model-protocol rendering used only by tests and fixtures."""

    semantics = program["semantics"]
    semantic_lines = "\n".join(
        prefix + str(semantics[prefix[2:-2].lower().replace(" ", "_")])
        for prefix in SEMANTIC_PREFIXES
    )
    rows = ["symbols = " + ", ".join(program["symbols"])]
    rows.extend("relation = " + item for item in program["relations"])
    rows.extend("define = " + item["label"] + " :: " + _render_ast(item["value"])
                for item in program.get("definitions", []))
    identities = program["identities"]
    if not identities:
        rows.append("identity = NONE")
    else:
        rows.extend(
            "identity = "
            + item["label"]
            + " :: "
            + _render_ast(item["left"])
            + " :: "
            + _render_ast(item["right"])
            for item in identities
        )
    conclusion = program["conclusion"]
    rows.append(
        "conclusion = "
        + conclusion["label"]
        + " :: "
        + _render_ast(conclusion["left"])
        + " :: "
        + _render_ast(conclusion["right"])
    )
    guards = program["guards"]
    rows.extend("zero = " + item["label"] + " :: " + " :: ".join(
        _render_ast(item[field]) for field in ("value", "scale", "combination"))
        for item in program.get("zeros", []))
    rows.extend("guard = " + item for item in guards or ["NONE"])
    return (
        "# Certificate Semantics\n\n"
        + semantic_lines
        + "\n\n# Certificate Program\n\n```certificate-args\n"
        + "\n".join(rows)
        + "\n```"
    )
