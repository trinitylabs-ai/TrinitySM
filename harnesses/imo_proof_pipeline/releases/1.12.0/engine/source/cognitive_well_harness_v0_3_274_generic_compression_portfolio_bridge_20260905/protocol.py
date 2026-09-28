from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

import scripts.v0236_markdown_protocol as mdp


EVIDENCE_TASKS = frozenset(
    {
        "CERTIFY_DERIVATION",
        "SEARCH_COUNTEREXAMPLE",
        "CHECK_EQUALITY",
        "SOLVE_EQUATIONS",
        "COMPLETE_CASES",
        "EXACT_ARITHMETIC",
    }
)


def _parse_sexpr_with_diagnostics(text: str, *, field: str) -> Any:
    try:
        return mdp.parse_sexpr(text)
    except ValueError as error:
        if str(error) != "trailing expression tokens":
            raise ValueError(f"{field} expression invalid: {error}") from error

        depth = 0
        first_complete: int | None = None
        first_unmatched_close: int | None = None
        for offset, character in enumerate(text):
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0 and first_complete is None:
                    first_complete = offset
                if depth < 0 and first_unmatched_close is None:
                    first_unmatched_close = offset
        trailing_start: int | None = None
        if first_complete is not None:
            for offset in range(first_complete + 1, len(text)):
                if not text[offset].isspace():
                    trailing_start = offset
                    break
        def marked_word_context(offset: int | None, marker: str, radius: int = 12) -> str:
            if offset is None:
                return "UNAVAILABLE"
            marked = text[:offset] + f" {marker} " + text[offset:]
            words = marked.split()
            marker_index = words.index(marker)
            return " ".join(
                words[max(0, marker_index - radius) : marker_index + radius + 1]
            )

        boundary_offset = (
            trailing_start
            if trailing_start is not None
            else first_complete + 1 if first_complete is not None else None
        )
        details = [
            "trailing expression tokens",
            f"field={field}",
            "top_level_boundary_context="
            + repr(marked_word_context(boundary_offset, "<<TRAILING_TOKENS_BEGIN>>")),
            f"final_parenthesis_balance={depth}",
            "unmatched_closing_parenthesis_context="
            + repr(
                marked_word_context(
                    first_unmatched_close,
                    "<<UNMATCHED_CLOSING_PARENTHESIS>>",
                )
            ),
        ]
        raise ValueError("; ".join(details)) from error

# These patterns nominate spans for semantic inspection. They never decide that a
# proof is wrong and never trigger execution on their own.
COMPRESSION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "unsupported_showing",
        re.compile(
            r"\b(?:it\s+(?:can\s+be|is)\s+|one\s+(?:can|may)\s+)"
            r"(?:readily\s+|easily\s+|directly\s+)?"
            r"(?:shown?|checked?|verified|seen)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hidden_calculation",
        re.compile(
            r"\b(?:after|upon|by)\s+(?:a\s+|some\s+)?"
            r"(?:straightforward\s+|direct\s+|routine\s+|simple\s+|lengthy\s+)?"
            r"(?:calculation|computation|simplification|algebra|manipulation)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "simplification_jump",
        re.compile(
            r"\b(?:the\s+expression\s+)?simplif(?:y|ies|ied|ication)"
            r"(?:\s+(?:directly|immediately))?\s+(?:to|gives?|yields?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "constraint_force",
        re.compile(
            r"\b(?:these|the|those|above|preceding|previous)\s+"
            r"(?:constraints?|relations?|equations?|identities|conditions?)\s+"
            r"(?:force|imply|give|yield|ensure|show)(?:s)?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "bare_causal_bridge",
        re.compile(
            r"\b(?:forces?|implies?|ensures?|yields?|shows?|gives?)\s+that\b",
            re.IGNORECASE,
        ),
    ),
    (
        "omitted_details",
        re.compile(
            r"\b(?:details?\s+(?:are\s+)?omitted|we\s+omit\s+the\s+details?|"
            r"it\s+remains\s+to\s+(?:check|show|verify))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "analogy_shortcut",
        re.compile(
            r"\b(?:similarly|analogously|by\s+symmetry|by\s+analogy|by\s+consistency|"
            r"following\s+the\s+same\s+(?:logic|argument|calculation))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unsupported_implication",
        re.compile(
            r"\b(?:this|the\s+(?:claim|result|conclusion))\s+"
            r"(?:now\s+)?follows\s+(?:at\s+once\s+)?from\b",
            re.IGNORECASE,
        ),
    ),
    (
        "asserted_obviousness",
        re.compile(r"\b(?:clearly|obviously|evidently|readily)\b", re.IGNORECASE),
    ),
    (
        "conclusion_shortcut",
        re.compile(
            r"\b(?:hence|thus|therefore)\s+(?:the\s+)?"
            r"(?:claim|result|conclusion|desired\s+(?:result|identity|equality))\b",
            re.IGNORECASE,
        ),
    ),
)


def compression_candidates(proof: str, *, limit: int = 24) -> list[dict[str, Any]]:
    """Return deterministic semantic-audit hints around proof-compression phrases."""

    text = proof.replace("\r\n", "\n")
    hits: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for label, pattern in COMPRESSION_PATTERNS:
        for match in pattern.finditer(text):
            key = (match.start(), match.end())
            if key in seen:
                continue
            seen.add(key)
            previous_break = text.rfind("\n\n", 0, match.start())
            paragraph_start = 0 if previous_break < 0 else previous_break + 2
            paragraph_end = text.find("\n\n", match.end())
            if paragraph_end < 0:
                paragraph_end = len(text)
            if paragraph_end - paragraph_start > 1200:
                context_start = max(paragraph_start, match.start() - 450)
                context_end = min(paragraph_end, match.end() + 700)
            else:
                context_start, context_end = paragraph_start, paragraph_end
            context = re.sub(r"\s+", " ", text[context_start:context_end]).strip()
            hits.append(
                {
                    "kind": label,
                    "phrase": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "context": context,
                }
            )
    hits.sort(key=lambda row: (int(row["start"]), int(row["end"]), str(row["kind"])))
    return hits[:limit]


def render_candidates(hits: Iterable[Mapping[str, Any]]) -> str:
    rows = list(hits)
    if not rows:
        return "NONE"
    return "\n".join(
        f"- H{index} [{row['kind']} at characters {row['start']}--{row['end']}]: "
        f"{row['context']}"
        for index, row in enumerate(rows, start=1)
    )


def parse_detection(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(
        markdown,
        [
            "Decision",
            "Load-Bearing Gap",
            "Trigger Evidence",
            "Evidence Task",
            "Desired Exact Fact",
            "Downstream Obligation",
        ],
    )
    if any("\n" in sections[name] for name in sections):
        raise ValueError("every detection section must contain one paragraph")
    decision = sections["Decision"]
    task = sections["Evidence Task"]
    if decision == "NO_TOOL":
        if any(
            sections[name] != "NONE"
            for name in (
                "Load-Bearing Gap",
                "Trigger Evidence",
                "Evidence Task",
                "Desired Exact Fact",
                "Downstream Obligation",
            )
        ):
            raise ValueError("NO_TOOL requires NONE in every remaining section")
        return {"call_requested": False, "decision": decision}
    if decision != "CALL_TOOL":
        raise ValueError("Decision must be CALL_TOOL or NO_TOOL")
    if task not in EVIDENCE_TASKS:
        raise ValueError("unknown Evidence Task")
    for name in (
        "Load-Bearing Gap",
        "Trigger Evidence",
        "Desired Exact Fact",
        "Downstream Obligation",
    ):
        if sections[name] == "NONE":
            raise ValueError(f"CALL_TOOL requires a nonempty {name}")
    return {
        "call_requested": True,
        "decision": decision,
        "gap": sections["Load-Bearing Gap"],
        "trigger_evidence": sections["Trigger Evidence"],
        "evidence_task": task,
        "desired_exact_fact": sections["Desired Exact Fact"],
        "downstream_obligation": sections["Downstream Obligation"],
    }


def normalize_matcher(
    markdown: str, *, allowed_operations: Iterable[str]
) -> tuple[str, dict[str, Any]]:
    """Canonicalize only mechanically determined matcher sentinel fields.

    A CALL_TOOL record is returned byte-for-byte.  For an exact NO_TOOL decision,
    the operation and immutable claim have only one valid representation under the
    frozen protocol, so noncanonical placeholder content can be removed without a
    mathematical choice.  When an otherwise complete record puts the exact valid,
    non-none allowlisted Operation token in Decision as well as Operation, that
    duplicated routing token has the single protocol spelling CALL_TOOL.  The
    operation, claim, and rationale are preserved verbatim after section parsing,
    and the existing strict parser remains the final acceptance gate.
    """

    before_sha256 = mdp.sha256_text(markdown)
    sections = mdp.exact_sections(
        markdown,
        ["Decision", "Operation", "Immutable Claim", "Fit Rationale"],
    )
    replacements = {
        "no_tool_operation_placeholders": 0,
        "no_tool_claim_placeholders": 0,
        "operation_decision_aliases": 0,
        "canonical_container_renderings": 0,
    }
    normalized = markdown
    if sections["Decision"] == "NO_TOOL":
        if sections["Operation"] != "none":
            replacements["no_tool_operation_placeholders"] = 1
        if sections["Immutable Claim"] != "NONE":
            replacements["no_tool_claim_placeholders"] = 1
        normalized = mdp.render_matcher(
            {
                "decision": "NO_TOOL",
                "operation": "none",
                "claim": "",
                "fit_rationale": sections["Fit Rationale"],
            }
        )
        if normalized != markdown:
            replacements["canonical_container_renderings"] = 1
    elif (
        sections["Decision"] == sections["Operation"]
        and sections["Operation"] != "none"
        and sections["Operation"] in frozenset(allowed_operations)
        and sections["Immutable Claim"] != "NONE"
    ):
        replacements["operation_decision_aliases"] = 1
        normalized = mdp.render_matcher(
            {
                "decision": "CALL_TOOL",
                "operation": sections["Operation"],
                "claim": sections["Immutable Claim"],
                "fit_rationale": sections["Fit Rationale"],
            }
        )
        if normalized != markdown:
            replacements["canonical_container_renderings"] = 1

    rewrite_labels = {
        "no_tool_operation_placeholders": "no_tool_operation_placeholder",
        "no_tool_claim_placeholders": "no_tool_claim_placeholder",
        "operation_decision_aliases": "allowlisted_operation_as_call_tool_decision",
        "canonical_container_renderings": "canonical_matcher_markdown_container",
    }
    return normalized, {
        "schema": "cognitive-well-v0274-matcher-normalization-v1",
        "applied": normalized != markdown,
        "before_sha256": before_sha256,
        "after_sha256": mdp.sha256_text(normalized),
        "replacements": replacements,
        "applied_rewrite_kinds": [
            rewrite_labels[key]
            for key, count in replacements.items()
            if count
        ],
        "allowed_rewrites": [
            "when Decision is exactly NO_TOOL: Operation -> none",
            "when Decision is exactly NO_TOOL: Immutable Claim -> NONE",
            (
                "when Decision exactly equals the same valid non-none allowlisted "
                "Operation and Immutable Claim is non-NONE: Decision -> CALL_TOOL"
            ),
            "canonical matcher Markdown headings/container rendering",
        ],
    }


def parse_ideal_membership_arguments(markdown: str) -> dict[str, Any]:
    fields = mdp.argument_multimap(markdown)
    mdp.require_fields(
        fields,
        scalar=("operation", "symbols", "target"),
        repeated=("generator",),
    )
    if fields["operation"] != ["polynomial_ideal_membership"]:
        raise ValueError("wrong ideal-membership operation")
    symbols = mdp.parse_symbol_list(fields["symbols"][0])
    generators: dict[str, Any] = {}
    for raw in fields["generator"]:
        if " :: " not in raw:
            raise ValueError("generator must use 'D<number> :: expression'")
        label, expression = raw.split(" :: ", 1)
        if re.fullmatch(r"D[1-9][0-9]*", label) is None or label in generators:
            raise ValueError("generator labels must be unique D<number> values")
        node = _parse_sexpr_with_diagnostics(expression, field=f"generator {label}")
        generators[label] = mdp.expression_ast(node)
    return {
        "symbols": symbols,
        "generators": generators,
        "target": mdp.expression_ast(
            _parse_sexpr_with_diagnostics(fields["target"][0], field="target")
        ),
    }


# Reserve all expression heads accepted by mdp.expression_ast (including finite
# expressions), plus the existing integer alias. A malformed operator must never
# become a variable merely because the model also declared that name.
EXPRESSION_HEADS = frozenset({
    "symbol", "integer", "rational", "var", "add", "mul", "sub", "div",
    "pow", "neg", "abs", "and", "or", "mod", "eq", "ne", "lt", "le",
    "gt", "ge", "not",
})


def _normalize_expression_leaves(
    node: Any,
    symbols: set[str],
    replacements: dict[str, int],
) -> Any:
    """Canonicalize unambiguous surface aliases in an existing S-expression.

    Declared bare leaves, singleton ``(name)`` variable forms with nonreserved
    names, and the explicitly typed ``(integer n)`` spelling are eligible.
    The operator tree is otherwise preserved exactly;
    malformed expressions and undeclared leaves remain malformed and are rejected
    by the existing strict parser after normalization.
    """

    if isinstance(node, (int, str)):
        if isinstance(node, str) and node in symbols:
            replacements["declared_symbol_leaves"] += 1
            return ["symbol", node]
        return node
    if not isinstance(node, list) or not node:
        return node
    if (len(node) == 1 and isinstance(node[0], str)
            and node[0] in symbols and node[0] not in EXPRESSION_HEADS
            and mdp.IDENTIFIER.fullmatch(node[0])):
        # Add this counter only when used, preserving historical replay records
        # for already-canonical drafts and the earlier supported aliases.
        key = "parenthesized_declared_symbols"
        replacements[key] = replacements.get(key, 0) + 1
        return ["symbol", node[0]]
    if node[0] == "symbol":
        return node
    if (
        node[0] == "integer"
        and len(node) == 2
        and isinstance(node[1], int)
    ):
        replacements["typed_integer_literals"] += 1
        return node[1]
    return [
        node[0],
        *(
            _normalize_expression_leaves(value, symbols, replacements)
            for value in node[1:]
        ),
    ]


def _render_sexpr(node: Any) -> str:
    if isinstance(node, list):
        return "(" + " ".join(_render_sexpr(value) for value in node) + ")"
    return str(node)


def _normalize_ideal_membership_compilation(
    markdown: str,
) -> tuple[str, dict[str, int]]:
    """Repair only labels and unambiguous expression aliases."""

    sections = mdp.exact_sections(markdown, ["Semantic Bindings", "Tool Arguments"])
    argument_markdown = "# Tool Arguments\n\n" + sections["Tool Arguments"]
    fields = mdp.argument_multimap(argument_markdown)
    mdp.require_fields(
        fields,
        scalar=("operation", "symbols", "target"),
        repeated=("generator",),
    )
    if fields["operation"] != ["polynomial_ideal_membership"]:
        raise ValueError("wrong ideal-membership operation")
    symbol_names = mdp.parse_symbol_list(fields["symbols"][0])
    symbols = set(symbol_names)
    replacements = {
        "declared_symbol_leaves": 0,
        "typed_integer_literals": 0,
        "ideal_generator_labels": 0,
        "canonical_container_renderings": 0,
    }

    normalized_generators: list[str] = []
    for index, raw in enumerate(fields["generator"], start=1):
        canonical_label = f"D{index}"
        original_label = raw.split("::", 1)[0].strip() if "::" in raw else None
        if original_label != canonical_label:
            replacements["ideal_generator_labels"] += 1
        expression = raw.split("::", 1)[1].strip() if "::" in raw else raw
        node = _normalize_expression_leaves(
            _parse_sexpr_with_diagnostics(expression, field=f"generator {index}"),
            symbols,
            replacements,
        )
        normalized_generators.append(f"generator = D{index} :: {_render_sexpr(node)}")
    target = _render_sexpr(
        _normalize_expression_leaves(
            _parse_sexpr_with_diagnostics(fields["target"][0], field="target"),
            symbols,
            replacements,
        )
    )
    tool_lines = [
        "operation = polynomial_ideal_membership",
        "symbols = " + ", ".join(symbol_names),
        *normalized_generators,
        "target = " + target,
    ]
    normalized = (
        "# Semantic Bindings\n\n"
        + sections["Semantic Bindings"]
        + "\n\n# Tool Arguments\n\n```tool-args\n"
        + "\n".join(tool_lines)
        + "\n```"
    )
    return normalized, replacements


def normalize_ideal_membership_compilation(markdown: str) -> str:
    """Repair only labels and unambiguous expression aliases."""

    normalized, _ = _normalize_ideal_membership_compilation(markdown)
    return normalized


_EXPRESSION_FIELDS: dict[str, frozenset[str]] = {
    "expand_and_compare": frozenset({"left", "right"}),
    "simplify_identity": frozenset({"left", "right"}),
    "factor_and_reexpand": frozenset({"expression"}),
    "solve_and_substitute": frozenset({"equation"}),
    "polynomial_root_filter": frozenset({"polynomial"}),
    "exact_branch_system": frozenset(
        {"original_equation", "output_expression"}
    ),
}


def _normalize_algebraic_compilation(
    markdown: str,
    operation: str,
) -> tuple[str, dict[str, int]]:
    """Normalize declared leaves without repairing expression structure."""

    expression_fields = _EXPRESSION_FIELDS.get(operation)
    replacements = {
        "declared_symbol_leaves": 0,
        "typed_integer_literals": 0,
        "ideal_generator_labels": 0,
        "canonical_container_renderings": 0,
    }
    if expression_fields is None:
        return markdown, replacements

    sections = mdp.exact_sections(markdown, ["Semantic Bindings", "Tool Arguments"])
    argument_markdown = "# Tool Arguments\n\n" + sections["Tool Arguments"]
    body = mdp.fenced_body(argument_markdown, "tool-args", "Tool Arguments")
    fields = mdp.argument_multimap(argument_markdown)
    if fields.get("operation") != [operation]:
        raise ValueError("compiler operation does not match immutable matcher selection")
    if len(fields.get("symbols", [])) != 1:
        raise ValueError("algebraic normalization requires one symbols field")
    symbol_names = mdp.parse_symbol_list(fields["symbols"][0])
    symbols = set(symbol_names)

    normalized_lines: list[str] = []
    for line_number, line in enumerate(body.splitlines(), start=1):
        match = mdp.ARGUMENT_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid tool-args line {line_number}")
        key, value = match.groups()
        if key in expression_fields:
            node = _parse_sexpr_with_diagnostics(value, field=key)
            value = _render_sexpr(
                _normalize_expression_leaves(node, symbols, replacements)
            )
        elif key == "common_condition" and operation == "exact_branch_system":
            if " :: " not in value:
                raise ValueError("condition must use 'relation :: expression'")
            relation, expression = value.split(" :: ", 1)
            node = _parse_sexpr_with_diagnostics(
                expression,
                field="common_condition",
            )
            value = relation + " :: " + _render_sexpr(
                _normalize_expression_leaves(node, symbols, replacements)
            )
        normalized_lines.append(f"{key} = {value}")

    normalized = (
        "# Semantic Bindings\n\n"
        + sections["Semantic Bindings"]
        + "\n\n# Tool Arguments\n\n```tool-args\n"
        + "\n".join(normalized_lines)
        + "\n```"
    )
    return normalized, replacements


def normalize_compilation(
    markdown: str,
    operation: str,
) -> tuple[str, dict[str, Any]]:
    """Return canonical Markdown plus an auditable mechanical rewrite record."""

    if operation == "polynomial_ideal_membership":
        normalized, replacements = _normalize_ideal_membership_compilation(markdown)
    else:
        normalized, replacements = _normalize_algebraic_compilation(
            markdown,
            operation,
        )
    if normalized != markdown:
        replacements["canonical_container_renderings"] = 1
    rewrite_labels = {
        "declared_symbol_leaves": "declared_bare_symbol_leaf",
        "parenthesized_declared_symbols": "parenthesized_declared_symbol_leaf",
        "typed_integer_literals": "typed_integer_literal",
        "ideal_generator_labels": "ideal_generator_label",
        "canonical_container_renderings": "canonical_compiler_markdown_container",
    }
    return normalized, {
        "schema": "cognitive-well-v0274-deterministic-normalization-v1",
        "applied": normalized != markdown,
        "before_sha256": mdp.sha256_text(markdown),
        "after_sha256": mdp.sha256_text(normalized),
        "replacements": replacements,
        "applied_rewrite_kinds": [
            rewrite_labels[key]
            for key, count in replacements.items()
            if count
        ],
        "allowed_rewrites": [
            "declared bare symbol leaf -> (symbol identifier)",
            "(integer n) -> integer literal n",
            "ideal generator label -> sequential D<number>",
            "canonical compiler Markdown headings/fence/argument rendering",
        ] + (["singleton (declared_nonreserved_identifier) -> (symbol identifier)"]
             if replacements.get("parenthesized_declared_symbols") else []),
    }


def parse_compilation(markdown: str, operation: str) -> dict[str, Any]:
    sections = mdp.exact_sections(markdown, ["Semantic Bindings", "Tool Arguments"])
    lines = sections["Semantic Bindings"].splitlines()
    prefixes = (
        "- Source basis: ",
        "- Target meaning: ",
        "- Domain and branch conditions: ",
        "- Compression map: ",
        "- Sufficiency argument: ",
        "- Rewrite consequence: ",
    )
    if len(lines) != len(prefixes) or any(
        not line.startswith(prefix) or not line[len(prefix) :].strip()
        for line, prefix in zip(lines, prefixes)
    ):
        raise ValueError("Semantic Bindings must contain the six exact fields")
    argument_markdown = "# Tool Arguments\n\n" + sections["Tool Arguments"]
    if operation == "polynomial_ideal_membership":
        arguments = parse_ideal_membership_arguments(argument_markdown)
    else:
        arguments = mdp.parse_tool_arguments(argument_markdown, operation)
    return {
        "bindings": {
            "source_basis": lines[0][len(prefixes[0]) :].strip(),
            "target_meaning": lines[1][len(prefixes[1]) :].strip(),
            "domain_and_branch_conditions": lines[2][len(prefixes[2]) :].strip(),
            "compression_map": lines[3][len(prefixes[3]) :].strip(),
            "sufficiency_argument": lines[4][len(prefixes[4]) :].strip(),
            "rewrite_consequence": lines[5][len(prefixes[5]) :].strip(),
        },
        "arguments": arguments,
        "argument_markdown": argument_markdown,
    }


AUDIT_CHECKS = (
    "Every formal symbol is bound to the supplied proof",
    "Every input equation or value is derived without invention",
    "The formal target is equivalent to the detected proof gap",
    "All domain, denominator, and branch conditions are recorded",
    "The compression map is exact and preserves the needed implication",
    "No avoidable definitional symbol or redundant generator remains",
    "The requested result can materially change the proof rewrite",
)


def parse_semantic_audit(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(markdown, ["Decision", "Checks", "Issues"])
    decision = sections["Decision"]
    if decision not in {"ACCEPT", "REJECT"}:
        raise ValueError("semantic audit decision must be ACCEPT or REJECT")
    lines = sections["Checks"].splitlines()
    if len(lines) != len(AUDIT_CHECKS):
        raise ValueError("wrong semantic audit check count")
    checks: dict[str, bool] = {}
    for label, line in zip(AUDIT_CHECKS, lines):
        prefix = f"- {label}: "
        if not line.startswith(prefix) or line[len(prefix) :] not in {"PASS", "FAIL"}:
            raise ValueError(f"malformed semantic audit check {label!r}")
        checks[label] = line[len(prefix) :] == "PASS"
    issues = (
        []
        if sections["Issues"] == "NONE"
        else mdp.parse_prefixed_list(sections["Issues"])
    )
    accepted = decision == "ACCEPT" and all(checks.values()) and not issues
    if (decision == "ACCEPT") != accepted:
        raise ValueError("semantic audit decision disagrees with checks/issues")
    return {"decision": decision, "checks": checks, "issues": issues, "accepted": accepted}


def parse_bridge(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(
        markdown,
        [
            "Tool Verdict",
            "Checked Mathematical Statement",
            "Proof Gap Replaced",
            "Hypothesis-to-Tool Binding",
            "Tool-to-Conclusion Bridge",
            "Domain and Branch Closure",
            "Whole-Proof Rewrite Plan",
        ],
    )
    verdict = sections["Tool Verdict"]
    if verdict not in {
        "VERIFIED_SUPPORT",
        "COUNTEREXAMPLE_FOUND",
        "EXACT_SOLUTION_SET",
        "NO_USABLE_RESULT",
    }:
        raise ValueError("unknown tool verdict")
    for name in (
        "Hypothesis-to-Tool Binding",
        "Tool-to-Conclusion Bridge",
        "Domain and Branch Closure",
    ):
        if sections[name] != "NONE":
            mdp.parse_prefixed_list(sections[name])
    plan: list[str] = []
    current: list[str] = []
    expected_index = 1
    for line in sections["Whole-Proof Rewrite Plan"].splitlines():
        numbered = re.fullmatch(r"([1-9][0-9]*)\.\s+(.+)", line)
        if numbered is not None:
            if int(numbered.group(1)) != expected_index:
                raise ValueError("rewrite plan must be a sequential numbered list")
            if current:
                plan.append("\n".join(current).strip())
            current = [numbered.group(2).strip()]
            expected_index += 1
            continue
        if not current:
            raise ValueError("rewrite plan must begin with a numbered item")
        # CommonMark permits blank, indented, displayed-math, and paragraph
        # continuation lines inside a numbered item. Preserve them as part of
        # that item without inventing a new step.
        current.append(line.rstrip())
    if current:
        plan.append("\n".join(current).strip())
    if not plan:
        raise ValueError("empty whole-proof rewrite plan")
    return {"verdict": verdict, "sections": sections, "plan": plan}


BRIDGE_AUDIT_CHECKS = (
    "Tool verdict matches the returned exact result",
    "Formal inputs are connected to original hypotheses",
    "Returned facts bridge the detected gap with correct polarity",
    "The compression map is unfolded back into the proof",
    "The exact target is identified with the original theorem quantity",
    "Every cleared or cancelled factor is justified",
    "Decisive certificate data remains directly inspectable",
    "Domain, denominator, and branch obligations are closed",
    "Plan reconstructs the whole proof rather than a local patch",
)


def parse_bridge_audit(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(markdown, ["Decision", "Checks", "Issues"])
    decision = sections["Decision"]
    if decision not in {"ACCEPT", "REJECT"}:
        raise ValueError("bridge audit decision must be ACCEPT or REJECT")
    lines = sections["Checks"].splitlines()
    if len(lines) != len(BRIDGE_AUDIT_CHECKS):
        raise ValueError("wrong bridge audit check count")
    checks: dict[str, bool] = {}
    for label, line in zip(BRIDGE_AUDIT_CHECKS, lines):
        prefix = f"- {label}: "
        if not line.startswith(prefix) or line[len(prefix) :] not in {"PASS", "FAIL"}:
            raise ValueError(f"malformed bridge audit check {label!r}")
        checks[label] = line[len(prefix) :] == "PASS"
    issues = (
        []
        if sections["Issues"] == "NONE"
        else mdp.parse_prefixed_list(sections["Issues"])
    )
    accepted = decision == "ACCEPT" and all(checks.values()) and not issues
    if (decision == "ACCEPT") != accepted:
        raise ValueError("bridge audit decision disagrees with checks/issues")
    return {"decision": decision, "checks": checks, "issues": issues, "accepted": accepted}


PROOF_AUDIT_CHECKS = (
    "The original theorem is fully answered",
    "The detected load-bearing gap is actually bridged",
    "The exact result is used with the correct logical polarity",
    "All formal variables and equations are derived in the proof",
    "The formal target is explicitly translated back to the theorem quantity",
    "Every cleared or cancelled factor is justified",
    "Decisive exact certificate data remains directly inspectable",
    "All domain, denominator, equality, and branch cases are handled",
    "No process or tool meta-language appears",
)


def parse_proof_audit(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(markdown, ["Decision", "Checks", "Issues"])
    decision = sections["Decision"]
    if decision not in {"PASS", "FAIL"}:
        raise ValueError("proof audit decision must be PASS or FAIL")
    lines = sections["Checks"].splitlines()
    if len(lines) != len(PROOF_AUDIT_CHECKS):
        raise ValueError("wrong proof audit check count")
    checks: dict[str, bool] = {}
    for label, line in zip(PROOF_AUDIT_CHECKS, lines):
        prefix = f"- {label}: "
        if not line.startswith(prefix) or line[len(prefix) :] not in {"PASS", "FAIL"}:
            raise ValueError(f"malformed proof audit check {label!r}")
        checks[label] = line[len(prefix) :] == "PASS"
    issues = (
        []
        if sections["Issues"] == "NONE"
        else mdp.parse_prefixed_list(sections["Issues"])
    )
    passed = decision == "PASS" and all(checks.values()) and not issues
    if (decision == "PASS") != passed:
        raise ValueError("proof audit decision disagrees with checks/issues")
    return {"decision": decision, "checks": checks, "issues": issues, "passed": passed}
