from __future__ import annotations

import hashlib
import json
import shutil
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Mapping

import scripts.run_v0220_gemma_global_tool_budget_20260904 as v0220
import scripts.v0236_markdown_protocol as mdp
from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
    pipeline as base,
    protocol,
)
from cognitive_well_harness_v0_3_275_generic_audited_ledger_compression_20260905 import (
    transformation_validation,
)
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import (
    integration as laurent,
)

from . import HARNESS_VERSION, PARENT_HARNESS_VERSION


FORMALIZATION_SCHEDULE = (
    ("t10", 0.10),
    ("t15", 0.15),
    ("t20", 0.20),
    ("t25", 0.25),
    ("t30", 0.30),
    ("t35", 0.35),
    ("t40", 0.40),
    ("t45", 0.45),
)
SINGULAR_BINARY = Path(
    ".tools/singular-4.2.1/root/usr/bin/Singular"
).resolve()


FORMALIZER_SYSTEM = """You are a faithful typed mathematical formalizer. Translate
the single detected proof obligation into polynomial ideal membership without
trying to simplify, minimize, or semantically compress it. Gemma is used exactly
once here to produce a formalization; there is no later model-generated compression.

Bind every symbol and generator to the supplied theorem and proof. Record every
division or cancellation in a typed Guard Program. A provenance_division records
the exact numerator and denominator of a proof-derived quotient; source_nonzero
records another proof-derived polynomial known to be nonzero. Do not assert that a
guard is nonzero merely because it is convenient. Use only declared tool symbols in
the Guard Program. Do not claim an exact result.

Emit exactly three top-level sections: # Semantic Bindings, # Guard Program, and
# Tool Arguments, in that order, with no JSON and no additional headings."""


POST_SINGULAR_AUDITOR_SYSTEM = """You are an independent semantic auditor. Audit
the pre-Laurent model formalization against only the original theorem and proof.
No exact result, route size, or Laurent outcome is supplied. Do not infer validity
from any computer-algebra result or from whether such a result may later exist.

Reject any invented variable, equation, target correspondence, branch, or nonzero
guard. For every typed guard, verify both its proof provenance and why it is nonzero
on the geometric domain. Verify that proving the formal target gives precisely the
detected proof obligation. Do not repair the formalization and do not infer semantic
validity from the fact that Singular succeeded.

Emit only the required Decision, Checks, and Issues sections."""


POST_SINGULAR_CHECKS = (
    "Every formal symbol is bound to the supplied proof",
    "Every polynomial generator is derived without invention",
    "The formal target is equivalent to the detected proof gap",
    "Every typed nonzero guard follows from the stated geometric domain",
    "Every proof division or cancellation has a corresponding typed guard",
    "No branch or degeneracy needed by the implication was omitted",
    "The certified formal target can materially repair the whole proof",
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": str(path.relative_to(root)),
            "sha256": _sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]


def _schedule_records() -> list[dict[str, Any]]:
    return [
        {"label": label, "temperature": temperature}
        for label, temperature in FORMALIZATION_SCHEDULE
    ]


def _schedule_sha256() -> str:
    return exact_tools.stable_hash(_schedule_records())


def load_resumed_formalizations(
    *,
    resume_root: Path,
    problem: Any,
    proof: str,
    allowed_matcher_operations: tuple[str, ...],
    fresh_portfolio_root: Path | None = None,
) -> tuple[str, dict[str, Any], str, dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Reparse and hash-bind a prior run only through its formalization barrier."""
    root = resume_root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    manifest_path = root / "manifest.json"
    manifest = _read_json(manifest_path)
    if manifest.get("problem_id") != problem.problem_id:
        raise ValueError("resume problem id differs from the current problem")
    if manifest.get("problem_file_sha256") != _sha256_file(problem.source_path):
        raise ValueError("resume problem file hash differs from the current problem")
    if manifest.get("resolver1_proof_sha256") != base.sha256_text(proof):
        raise ValueError("resume proof hash differs from the current Resolver-1 proof")
    if manifest.get("formalization_schedule") != _schedule_records():
        raise ValueError("resume formalization schedule differs from the frozen schedule")
    if manifest.get("formalization_schedule_sha256") != _schedule_sha256():
        raise ValueError("resume formalization schedule hash is invalid")
    if manifest.get("required_matched_operation") != exact_tools.IDEAL_OPERATION:
        raise ValueError("resume run did not require polynomial ideal membership")
    if manifest.get("matcher_allowed_operations") != list(allowed_matcher_operations):
        raise ValueError("resume matcher operation menu differs from the current menu")
    theorem_path = root / "input/original_theorem.md"
    proof_path = root / "input/resolver1_proof.md"
    if theorem_path.read_text(encoding="utf-8").strip() != problem.statement:
        raise ValueError("resume theorem artifact differs from the current theorem")
    if proof_path.read_text(encoding="utf-8").strip() != proof:
        raise ValueError("resume proof artifact differs from the current proof")

    detection_path = root / "01_detection/detection.md"
    matcher_path = root / "02_matcher/matcher.md"
    detection_text = detection_path.read_text(encoding="utf-8").strip()
    detection = protocol.parse_detection(detection_text)
    if not detection["call_requested"]:
        raise ValueError("resume detector did not request a tool")
    matcher_text = matcher_path.read_text(encoding="utf-8").strip()
    matcher = base._parse_matcher(
        matcher_text,
        str(detection["desired_exact_fact"]),
        allowed_matcher_operations,
    )
    if not matcher["call_requested"] or matcher["operation"] != exact_tools.IDEAL_OPERATION:
        raise ValueError("resume matcher did not select polynomial ideal membership")

    rows: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    portfolio_root = root / "03_guarded_formalizations"
    schedule = FORMALIZATION_SCHEDULE
    fresh_binding = None
    if fresh_portfolio_root is not None:
        fresh_root = fresh_portfolio_root.resolve()
        fresh = _read_json(fresh_root / "result.json")
        if (fresh.get("schema") != "generic-fresh-parser-failed-arms-v1"
                or fresh.get("state") != "completed"
                or Path(fresh["source_run"]).resolve() != root.parent):
            raise ValueError("fresh portfolio does not bind this stopped source run")
        source_paths = {"theorem": theorem_path, "proof": proof_path,
                        "detection": detection_path, "matcher": matcher_path}
        if fresh.get("source_bindings") != {key: _sha256_file(path) for key, path in source_paths.items()}:
            raise ValueError("fresh portfolio theorem/proof/tool bindings changed")
        compiled = [row["label"] for row in fresh["rows"] if row["state"] == "compiled"]
        if not compiled or fresh.get("compiled_labels") != compiled or len(set(compiled)) != len(compiled):
            raise ValueError("fresh portfolio compiled-label ledger is inconsistent")
        frozen = dict(FORMALIZATION_SCHEDULE)
        if any(row["label"] not in frozen or frozen[row["label"]] != row["temperature"] for row in fresh["rows"]):
            raise ValueError("fresh portfolio changed the frozen sampling schedule")
        schedule = tuple((label, temperature) for label, temperature in FORMALIZATION_SCHEDULE if label in compiled)
        portfolio_root = fresh_root / "03_guarded_formalizations"
        fresh_binding = {"source_root": str(fresh_root), "result_sha256": _sha256_file(fresh_root / "result.json"),
                         "compiled_labels": compiled, "selection_policy": "all_compiled_arms_in_frozen_schedule"}
    for label, temperature in schedule:
        arm_root = portfolio_root / label
        raw_path = arm_root / "formalization_raw.md"
        canonical_path = arm_root / "formalization.md"
        guard_path = arm_root / "guard_program.json"
        normalization_path = arm_root / "surface_normalization.json"
        profile_path = arm_root / "request_profile.json"
        raw = raw_path.read_text(encoding="utf-8").strip()
        parsed = dict(parse_guarded_formalization(raw))
        canonical = str(parsed.pop("normalized_markdown"))
        if canonical != canonical_path.read_text(encoding="utf-8").strip():
            raise ValueError(f"resume canonical formalization mismatch for {label}")
        guard_program = _read_json(guard_path)
        if parsed["guard_program"] != guard_program:
            raise ValueError(f"resume Guard Program mismatch for {label}")
        normalization = _read_json(normalization_path)
        if parsed["surface_normalization"] != normalization:
            raise ValueError(f"resume normalization record mismatch for {label}")
        profile = exact_tools.ideal_request_profile(parsed["arguments"])
        if profile != _read_json(profile_path):
            raise ValueError(f"resume request profile mismatch for {label}")
        model_root = arm_root / "model"
        if not model_root.is_dir():
            raise ValueError(f"resume model producer directory is missing for {label}")
        if fresh_portfolio_root is not None:
            producer = _read_json(arm_root / "producer_call.json")
            forcing = producer.get("metadata", {}).get("v0257_budget_forcing", {})
            if (forcing.get("forced_text_sha256") != base.sha256_text(raw)
                    or forcing.get("canonical_artifacts_are_forced_response") is not True):
                raise ValueError(f"fresh producer does not bind the raw Markdown for {label}")
        rows.append(
            {
                "label": label,
                "temperature": temperature,
                "state": "compiled",
                "formalization_text": canonical,
                "formalization": parsed,
                "request_profile": profile,
                "call": {
                    "reused": True,
                    "source_root": str(root),
                    "source_arm_root": str(arm_root),
                    "raw_sha256": _sha256_file(raw_path),
                },
            }
        )
        bindings.append(
            {
                "label": label,
                "temperature": temperature,
                "raw_sha256": _sha256_file(raw_path),
                "canonical_sha256": _sha256_file(canonical_path),
                "guard_program_sha256": _sha256_file(guard_path),
                "surface_normalization_sha256": _sha256_file(normalization_path),
                "request_profile_sha256": _sha256_file(profile_path),
                "model_artifacts": _artifact_inventory(model_root),
            }
        )
    binding = {
        "schema": "cognitive-well-v0309-formalization-resume-binding-v1",
        "source_root": str(root),
        "source_manifest_state": manifest.get("state"),
        "source_manifest_sha256": _sha256_file(manifest_path),
        "source_detection_sha256": _sha256_file(detection_path),
        "source_matcher_sha256": _sha256_file(matcher_path),
        "source_formalizations": bindings,
        "compiled_count": len(rows),
        "strict_reparse_passed": True,
        "detector_matcher_formalizer_model_calls_reused": True,
        "partial_laurent_artifacts_reused": False,
        "preloaded_certificate": False,
        "fresh_portfolio": fresh_binding,
    }
    binding["binding_sha256"] = exact_tools.stable_hash(binding)
    return detection_text, detection, matcher_text, matcher, rows, binding


def _semantic_lines(section: str) -> dict[str, str]:
    prefixes = (
        ("source_basis", "- Source basis: "),
        ("target_meaning", "- Target meaning: "),
        ("domain_and_branch_conditions", "- Domain and branch conditions: "),
        ("formalization_map", "- Formalization map: "),
        ("sufficiency_argument", "- Sufficiency argument: "),
        ("rewrite_consequence", "- Rewrite consequence: "),
    )
    lines = section.splitlines()
    if len(lines) != len(prefixes):
        raise ValueError("Semantic Bindings must contain the six exact fields")
    values: dict[str, str] = {}
    for line, (key, prefix) in zip(lines, prefixes, strict=True):
        if not line.startswith(prefix) or not line[len(prefix) :].strip():
            raise ValueError(f"malformed semantic binding {key}")
        values[key] = line[len(prefix) :].strip()
    return values


def _render_semantic_bindings(bindings: Mapping[str, str]) -> str:
    return "\n".join(
        (
            f"- Source basis: {bindings['source_basis']}",
            f"- Target meaning: {bindings['target_meaning']}",
            "- Domain and branch conditions: "
            f"{bindings['domain_and_branch_conditions']}",
            f"- Formalization map: {bindings['formalization_map']}",
            f"- Sufficiency argument: {bindings['sufficiency_argument']}",
            f"- Rewrite consequence: {bindings['rewrite_consequence']}",
        )
    )


def _normalize_guard_section(
    section: str, declared_symbols: set[str]
) -> tuple[str, dict[str, int]]:
    """Normalize unambiguous declared leaves in an otherwise parsed guard AST."""

    if section.strip() == "NONE":
        return "NONE", {"declared_symbol_leaves": 0, "typed_integer_literals": 0}
    body = mdp.fenced_body(
        "# Guard Program\n\n" + section.strip(), "guard-args", "Guard Program"
    )
    replacements = {"declared_symbol_leaves": 0, "typed_integer_literals": 0}
    rendered: list[str] = []

    def normalize(expression: str, field: str) -> str:
        node = protocol._parse_sexpr_with_diagnostics(expression, field=field)
        normalized = protocol._normalize_expression_leaves(
            node, declared_symbols, replacements
        )
        return protocol._render_sexpr(normalized)

    for line_number, line in enumerate(body.splitlines(), start=1):
        match = transformation_validation.GUARD_FIELD.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid guard-args line {line_number}")
        key, value = match.groups()
        if key == "provenance_division":
            parts = value.split(" :: ")
            if len(parts) != 3:
                raise ValueError(
                    "provenance division must use label :: numerator :: denominator"
                )
            label, numerator, denominator = parts
            value = (
                f"{label} :: {normalize(numerator, f'guard {label} numerator')} :: "
                f"{normalize(denominator, f'guard {label} denominator')}"
            )
        elif key == "source_nonzero":
            if " :: " not in value:
                raise ValueError("source nonzero fact must use label :: expression")
            label, expression = value.split(" :: ", 1)
            value = f"{label} :: {normalize(expression, f'guard {label} expression')}"
        rendered.append(f"{key} = {value}")
    return "```guard-args\n" + "\n".join(rendered) + "\n```", replacements


def _normalize_labeled_target(section: str) -> tuple[str, bool]:
    """Remove only an unambiguous generator-style label from the target field."""

    body = mdp.fenced_body(
        "# Tool Arguments\n\n" + section.strip(), "tool-args", "Tool Arguments"
    )
    lines = body.splitlines()
    changed = False
    for index, line in enumerate(lines):
        if not line.startswith("target = "):
            continue
        value = line[len("target = ") :]
        if " :: " not in value:
            continue
        label, expression = value.split(" :: ", 1)
        if transformation_validation.GUARD_LABEL.fullmatch(label) is None:
            continue
        lines[index] = "target = " + expression
        changed = True
    return "```tool-args\n" + "\n".join(lines) + "\n```", changed


def parse_guarded_formalization(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(
        markdown, ["Semantic Bindings", "Guard Program", "Tool Arguments"]
    )
    bindings = _semantic_lines(sections["Semantic Bindings"])
    # Reuse the mature ideal-argument normalizer by adapting only the semantic
    # field name it expects.  No mathematical leaf other than its declared
    # mechanical normalizations can change.
    legacy_semantic = "\n".join(
        (
            f"- Source basis: {bindings['source_basis']}",
            f"- Target meaning: {bindings['target_meaning']}",
            "- Domain and branch conditions: "
            f"{bindings['domain_and_branch_conditions']}",
            f"- Compression map: {bindings['formalization_map']}",
            f"- Sufficiency argument: {bindings['sufficiency_argument']}",
            f"- Rewrite consequence: {bindings['rewrite_consequence']}",
        )
    )
    normalized_tool_section, target_label_removed = _normalize_labeled_target(
        sections["Tool Arguments"]
    )
    adapted = (
        "# Semantic Bindings\n\n"
        + legacy_semantic
        + "\n\n# Tool Arguments\n\n"
        + normalized_tool_section
    )
    compilation = dict(base._parse_compilation(adapted, exact_tools.IDEAL_OPERATION))
    normalized_sections = mdp.exact_sections(
        str(compilation["normalized_markdown"]),
        ["Semantic Bindings", "Tool Arguments"],
    )
    normalized_guard_section, guard_normalization = _normalize_guard_section(
        sections["Guard Program"], set(compilation["arguments"]["symbols"])
    )
    guard_program = transformation_validation.parse_guard_program(
        normalized_guard_section
    )
    derived_guards = transformation_validation.derive_guards(
        guard_program, compilation["arguments"]
    )
    canonical = (
        "# Semantic Bindings\n\n"
        + _render_semantic_bindings(bindings)
        + "\n\n# Guard Program\n\n"
        + transformation_validation.render_guard_program(guard_program)
        + "\n\n# Tool Arguments\n\n"
        + normalized_sections["Tool Arguments"]
    )
    return {
        **compilation,
        "bindings": bindings,
        "guard_program": guard_program,
        "derived_guard_records": derived_guards["records"],
        "normalized_markdown": canonical,
        "canonical_formalization_sha256": base.sha256_text(canonical),
        "surface_normalization": {
            "guard_program": guard_normalization,
            "target_label_removed": target_label_removed,
        },
    }


def formalization_prompt(
    problem: v0220.Problem,
    proof: str,
    detection: Mapping[str, Any],
    matcher: Mapping[str, Any],
) -> str:
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
- Formalization map: one-line definition of every exact symbol and equation
- Sufficiency argument: one-line reason the request preserves the needed implication
- Rewrite consequence: one-line effect of the exact result

# Guard Program

Either `NONE`, or exactly one `guard-args` fence. Each line is one of:

provenance_division = label :: numerator polynomial S-expression :: denominator polynomial S-expression
source_nonzero = label :: nonzero polynomial S-expression

Use typed polynomial S-expressions and declared tool symbols only. Include every
denominator introduced in the proof-to-polynomial translation and every nonzero
condition needed for cancellation, localization, or elimination.

# Tool Arguments

{base.IDEAL_CONTRACT}

Parser limits: 1..{exact_tools.MAX_SYMBOLS} unique symbols and
1..{exact_tools.MAX_GENERATORS} generators; integer exponents 0..{exact_tools.MAX_EXPONENT}.
These are syntax/resource limits, not permission to omit mathematical hypotheses
or alter the immutable claim.

Emit the three top-level output sections exactly. The contract's Tool Arguments
heading is illustrative; include each heading only once."""


def parse_post_singular_audit(markdown: str) -> dict[str, Any]:
    sections = mdp.exact_sections(markdown, ["Decision", "Checks", "Issues"])
    decision = sections["Decision"]
    if decision not in {"ACCEPT", "REJECT"}:
        raise ValueError("audit decision must be ACCEPT or REJECT")
    lines = sections["Checks"].splitlines()
    if len(lines) != len(POST_SINGULAR_CHECKS):
        raise ValueError("wrong post-Singular audit check count")
    checks: dict[str, bool] = {}
    for label, line in zip(POST_SINGULAR_CHECKS, lines, strict=True):
        prefix = f"- {label}: "
        if not line.startswith(prefix) or line[len(prefix) :] not in {"PASS", "FAIL"}:
            raise ValueError(f"malformed post-Singular audit check {label!r}")
        checks[label] = line[len(prefix) :] == "PASS"
    issues = (
        []
        if sections["Issues"] == "NONE"
        else mdp.parse_prefixed_list(sections["Issues"])
    )
    accepted = decision == "ACCEPT" and all(checks.values()) and not issues
    if (decision == "ACCEPT") != accepted:
        raise ValueError("audit decision disagrees with checks/issues")
    return {"decision": decision, "checks": checks, "issues": issues, "accepted": accepted}


def post_singular_audit_prompt(
    *,
    problem: v0220.Problem,
    proof: str,
    detection_text: str,
    matcher_text: str,
    formalization_text: str,
) -> str:
    check_lines = "\n".join(f"- {label}: PASS or FAIL" for label in POST_SINGULAR_CHECKS)
    return f"""# Original Theorem

{problem.statement}

# Resolver-1 Proof

{proof}

# Detection

{detection_text}

# Operation Match

{matcher_text}

# Pre-Laurent Guarded Formalization

{formalization_text}

The host invokes this audit only after an independent exact calculation, but no
exact result or compactness profile is supplied. Audit the original formalization,
target mapping, and typed guard semantics without result-induced deference.

Emit only:

# Decision

ACCEPT or REJECT

# Checks

{check_lines}

# Issues

NONE, or one-line bullets. ACCEPT requires all PASS and NONE."""


def deduplicate_formalizations(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("state") != "compiled":
            continue
        parsed = row["formalization"]
        key = exact_tools.stable_hash(
            {
                "operation": exact_tools.IDEAL_OPERATION,
                "arguments": parsed["arguments"],
                "guard_program": parsed["guard_program"],
            }
        )
        row["deduplication_key"] = key
        groups.setdefault(key, []).append(row)
    representatives: list[dict[str, Any]] = []
    ledger_groups: list[dict[str, Any]] = []
    schedule_index = {label: index for index, (label, _) in enumerate(FORMALIZATION_SCHEDULE)}
    for key, members in groups.items():
        members.sort(key=lambda row: schedule_index[str(row["label"])])
        representative = members[0]
        representatives.append(representative)
        ledger_groups.append(
            {
                "canonical_typed_ast_and_guard_sha256": key,
                "representative": representative["label"],
                "members": [row["label"] for row in members],
            }
        )
    representatives.sort(key=lambda row: schedule_index[str(row["label"])])
    ledger_groups.sort(key=lambda row: schedule_index[str(row["representative"])])
    return {
        "schema": "cognitive-well-v0309-formalization-ast-guard-dedup-v1",
        "comparison": "canonical typed argument AST plus canonical typed Guard Program",
        "byte_equality_used": False,
        "fuzzy_similarity_used": False,
        "compiled_count": len([row for row in rows if row.get("state") == "compiled"]),
        "unique_count": len(representatives),
        "groups": ledger_groups,
        "representatives": representatives,
    }


def _coefficient_text(value: Mapping[str, Any]) -> str:
    real = f"{value['real_numerator']}/{value['real_denominator']}"
    imaginary = f"{value['imaginary_numerator']}/{value['imaginary_denominator']}"
    return f"({real})+({imaginary})*i"


def _polynomial_summary(payload: Mapping[str, Any], symbols: list[str], limit: int = 12) -> str:
    terms: list[str] = []
    for row in list(payload.get("terms", []))[:limit]:
        factors = [_coefficient_text(row["coefficient"])]
        for symbol, power in zip(symbols, row["powers"], strict=True):
            if int(power):
                factors.append(symbol if int(power) == 1 else f"{symbol}^{int(power)}")
        terms.append("*".join(factors))
    suffix = "" if int(payload.get("term_count", len(terms))) <= limit else " + ..."
    return " + ".join(terms) + suffix


def render_exact_evidence(route_root: Path, screen: Mapping[str, Any], prepared: Mapping[str, Any]) -> str:
    transform = json.loads(
        (route_root / "02_target_screen/laurent_transform.json").read_text(encoding="utf-8")
    )
    guard_binding = json.loads(
        (route_root / "02_target_screen/typed_guard_binding.json").read_text(encoding="utf-8")
    )
    identity = json.loads(
        (route_root / "02_target_screen/derived_identity_certificate.json").read_text(
            encoding="utf-8"
        )
    )
    lift = json.loads(
        (route_root / "03_laurent_lift/full_source_lift_certificate.json").read_text(
            encoding="utf-8"
        )
    )
    symbols = list(transform["symbols"])
    lines = [
        "# Exact Tool Evidence",
        "",
        "- Operation: direct deterministic Laurent parametrization followed by Singular ideal membership.",
        f"- Singular result: `{screen['exact_status']}`.",
        "- Original-generator multiplier identity re-expanded exactly: yes.",
        "- Laurent/source lift replayed exactly: yes.",
        f"- Unit-circle pairs: {screen.get('detected_circle_count', transform.get('detected_circle_count', len(transform['detected_circles'])))}.",
        f"- Orientations attempted/successful: {transform['orientation_attempted_count']}/{transform['orientation_success_count']}.",
        f"- Selected orientation: {transform['selected_orientation']}.",
        f"- Derived symbols: {', '.join(symbols)}.",
        f"- Derived target: `{_polynomial_summary(transform['target'], symbols)}`.",
        f"- Exact multiplier certificate SHA-256: `{identity['certificate_sha256']}`.",
        f"- Full Laurent lift SHA-256: `{lift['certificate_sha256']}`.",
        "",
        "# Typed Nonzero Guards",
        "",
    ]
    records = guard_binding.get("eligible_records", [])
    if records:
        for row in records:
            lines.append(
                f"- `{row['label']}`: `{row['expression']} != 0`; provenance: "
                + ", ".join(row["sources"])
                + "."
            )
    else:
        lines.append("- No source nonzero guard was used.")
    lines.extend(
        [
            "",
            "# Deterministic Laurent Bridge",
            "",
            f"- Detected circle equations: {', '.join(row['label'] for row in transform['detected_circles'])}.",
            f"- Reduction mode: `{transform['route_mode']}`.",
            f"- Pivot/eliminated variable: `{transform.get('pivot_label')}` / `{transform.get('eliminated_variable')}`.",
            f"- Membership identity uses {len(identity['generator_labels'])} transformed original-generator multipliers over QQ(i).",
            "- The stored lift verifies every circle substitution, Laurent denominator, typed guard, and target re-expansion.",
            "",
            "The machine certificate is evidence only for the typed formal target under the recorded guards; the post-Singular Qwen audit separately certifies its correspondence to the geometry.",
        ]
    )
    if prepared.get("state") != "prepared" or lift.get("verified") is not True:
        raise ValueError("Laurent lift is not prepared and verified")
    return "\n".join(lines) + "\n"


def _route_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    profile = row["screen"]["derived_profile"]
    return (
        int(profile["solver_symbol_count"]),
        int(profile["solver_generator_count"]),
        int(profile["maximum_total_degree"]),
        int(profile["total_monomial_count"]),
        int(profile["argument_ast_nodes"]),
        str(row["screen"]["transform_sha256"]),
        str(row["label"]),
    )


def build_preflight(
    *,
    problem_file: Path,
    proof_file: Path,
    output_dir: Path,
    detector: base.Role,
    compiler: base.Role,
    auditor: base.Role,
    rewriter: base.Role,
    master_seed: int,
    model_request_timeout_sec: int,
    laurent_preprocess_timeout_sec: int,
    singular_timeout_sec: int,
    exact_memory_mb: int,
    singular_binary: Path,
    excluded_matcher_operations: tuple[str, ...],
    resume_formalizations_root: Path | None = None,
) -> dict[str, Any]:
    if not 30 <= model_request_timeout_sec <= 14_400:
        raise ValueError("model timeout must be between 30 and 14400 seconds")
    if not 1 <= laurent_preprocess_timeout_sec <= 900:
        raise ValueError("Laurent preprocessing timeout must be between 1 and 900 seconds")
    if not 1 <= singular_timeout_sec <= 900:
        raise ValueError("Singular timeout must be between 1 and 900 seconds")
    if not 256 <= exact_memory_mb <= 8192:
        raise ValueError("exact memory must be between 256 and 8192 MB")
    problem = v0220.load_problem(problem_file)
    proof_path = proof_file.resolve()
    if not proof_path.is_file() or not proof_path.read_text(encoding="utf-8").strip():
        raise ValueError("Resolver-1 proof is missing or empty")
    binary = singular_binary.resolve()
    if not binary.is_file():
        raise FileNotFoundError(binary)
    allowed = base._matcher_operations(excluded_matcher_operations)
    resume_root = resume_formalizations_root.resolve() if resume_formalizations_root else None
    if resume_root is not None and not resume_root.is_dir():
        raise FileNotFoundError(resume_root)
    return {
        "schema": "cognitive-well-v0309-direct-laurent-preflight-v1",
        "state": "validated",
        "harness_version": HARNESS_VERSION,
        "parent_harness_version": PARENT_HARNESS_VERSION,
        "problem_id": problem.problem_id,
        "problem_file": str(problem.source_path),
        "problem_file_sha256": _sha256_file(problem.source_path),
        "resolver1_proof": str(proof_path),
        "resolver1_proof_sha256": base.sha256_text(
            proof_path.read_text(encoding="utf-8").strip()
        ),
        "output_dir": str(output_dir.resolve()),
        "master_seed": master_seed,
        "roles": {
            "detector_and_matcher": asdict(detector),
            "formalizer": asdict(compiler),
            "post_singular_auditor": asdict(auditor),
            "bridge_and_rewriter": asdict(rewriter),
        },
        "formalization_schedule": _schedule_records(),
        "formalization_schedule_sha256": _schedule_sha256(),
        "matcher_allowed_operations": list(allowed),
        "matcher_excluded_operations": list(excluded_matcher_operations),
        "resume_formalizations_root": str(resume_root) if resume_root else None,
        "resume_after_formalization_barrier": resume_root is not None,
        "required_matched_operation": exact_tools.IDEAL_OPERATION,
        "operation_mismatch_policy": "fail_closed_without_relabel_or_resampling",
        "model_request_timeout_sec": model_request_timeout_sec,
        "laurent_preprocess_timeout_sec": laurent_preprocess_timeout_sec,
        "singular_timeout_sec": singular_timeout_sec,
        "exact_memory_mb": exact_memory_mb,
        "singular_binary": str(binary),
        "singular_binary_sha256": _sha256_file(binary),
        "model_stages_use_budget_forcing_and_parser_feedback": True,
        "gemma_compression_stage": False,
        "stage_order": (
            ["hash_bound_resume_of_detector_matcher_and_eight_guarded_formalizations"]
            if resume_root
            else ["detector", "matcher", "eight_guarded_gemma_formalizations"]
        ) + [
            "canonical_typed_ast_and_guard_deduplication",
            "direct_laurent_preview",
            "singular_target_screen",
            "deterministic_laurent_lift_and_multiplier_replay",
            "qwen_pre_laurent_semantic_and_guard_audit",
            "deterministic_route_selection",
            "bridge",
            "whole_proof_rewrite",
            "final_proof_audit",
        ],
        "genericity_guards": {
            "model_decision_relabeling": False,
            "matcher_resampling_on_operation_mismatch": False,
            "preloaded_formalization_or_certificate": resume_root is not None,
            "preloaded_certificate": False,
            "resume_is_strictly_reparsed_and_hash_bound": resume_root is not None,
            "problem_specific_algebra_rule": False,
            "codex_math_calls": 0,
            "manual_candidate_selection": False,
        },
    }


def run_after_resolver1(
    *,
    problem_file: Path,
    proof_file: Path,
    output_dir: Path,
    detector: base.Role,
    compiler: base.Role,
    auditor: base.Role,
    rewriter: base.Role,
    master_seed: int = 20260906,
    model_request_timeout_sec: int = 600,
    laurent_preprocess_timeout_sec: int = 600,
    singular_timeout_sec: int = 600,
    exact_memory_mb: int = 8192,
    singular_binary: Path = SINGULAR_BINARY,
    excluded_matcher_operations: tuple[str, ...] = (),
    resume_formalizations_root: Path | None = None,
    resume_fresh_portfolio_root: Path | None = None,
    dry_run: bool = False,
    on_promoted: Callable[..., dict[str, Any]] | None = None,
    model_call: Callable[..., Any] | None = None,
    compiler_model_call: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    call_model = model_call or base._model_call
    call_compiler = compiler_model_call or base._compiler_model_call
    if resume_fresh_portfolio_root is not None and resume_formalizations_root is None:
        raise ValueError("fresh portfolio continuation requires its original acquisition root")
    preflight = build_preflight(
        problem_file=problem_file,
        proof_file=proof_file,
        output_dir=output_dir,
        detector=detector,
        compiler=compiler,
        auditor=auditor,
        rewriter=rewriter,
        master_seed=master_seed,
        model_request_timeout_sec=model_request_timeout_sec,
        laurent_preprocess_timeout_sec=laurent_preprocess_timeout_sec,
        singular_timeout_sec=singular_timeout_sec,
        exact_memory_mb=exact_memory_mb,
        singular_binary=singular_binary,
        excluded_matcher_operations=excluded_matcher_operations,
        resume_formalizations_root=resume_formalizations_root,
    )
    if dry_run:
        return preflight
    if resume_fresh_portfolio_root is not None:
        preflight.update(resume_fresh_portfolio_root=str(resume_fresh_portfolio_root.resolve()),
            stage_order=["hash_bound_resume_of_all_compiled_fresh_arms"] + preflight["stage_order"][1:])
    if on_promoted is not None:
        preflight["synthesis_policy"] = "first_exact_and_semantically_promoted_route_via_injected_provider"
    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    _write_json(destination / "manifest.json", {**preflight, "state": "running"})
    problem = v0220.load_problem(problem_file)
    proof = proof_file.resolve().read_text(encoding="utf-8").strip()
    base.write_text(destination / "input/original_theorem.md", problem.statement)
    base.write_text(destination / "input/resolver1_proof.md", proof)
    allowed = base._matcher_operations(excluded_matcher_operations)
    try:
        if resume_formalizations_root is not None:
            (
                detection_text,
                detection,
                matcher_text,
                matcher,
                formalization_rows,
                resume_binding,
            ) = load_resumed_formalizations(
                resume_root=resume_formalizations_root,
                problem=problem,
                proof=proof,
                allowed_matcher_operations=allowed,
                fresh_portfolio_root=resume_fresh_portfolio_root,
            )
            base.write_text(destination / "01_detection/detection.md", detection_text)
            base.write_text(destination / "02_matcher/matcher.md", matcher_text)
            _write_json(destination / "03_guarded_formalizations/resume_binding.json", resume_binding)
            for row in formalization_rows:
                shutil.copytree(Path(row["call"]["source_arm_root"]),
                    destination / "03_guarded_formalizations" / row["label"])
            preflight = {
                **preflight,
                "resume_binding_sha256": resume_binding["binding_sha256"],
            }
            _write_json(destination / "manifest.json", {**preflight, "state": "running"})
            detection_call = {
                "reused": True,
                "source_artifact_sha256": resume_binding["source_detection_sha256"],
            }
            matcher_call = {
                "reused": True,
                "source_artifact_sha256": resume_binding["source_matcher_sha256"],
            }
        else:
            hits = protocol.compression_candidates(proof)
            detection_text, detection, detection_call = call_model(
                role=detector,
                system_prompt=base.DETECTOR_SYSTEM,
                user_prompt=base.detection_prompt(problem, proof, hits),
                destination=destination / "01_detection/model",
                stage="direct_laurent_gap_detection",
                master_seed=master_seed,
                parser=protocol.parse_detection,
                request_timeout_sec=model_request_timeout_sec,
            )
            base.write_text(destination / "01_detection/detection.md", detection_text)
            if not detection["call_requested"]:
                raise RuntimeError("detector returned NO_TOOL")
            matcher_text, matcher, matcher_call = call_model(
                role=detector,
                system_prompt=base.matcher_system(allowed),
                user_prompt=base.matcher_prompt(problem, proof, detection, allowed),
                destination=destination / "02_matcher/model",
                stage="direct_laurent_operation_matcher",
                master_seed=master_seed,
                parser=lambda text: base._parse_matcher(
                    text, str(detection["desired_exact_fact"]), allowed
                ),
                request_timeout_sec=model_request_timeout_sec,
            )
            base.write_text(destination / "02_matcher/matcher.md", matcher_text)
            if not matcher["call_requested"]:
                raise RuntimeError("matcher returned NO_TOOL")
        if matcher["operation"] != exact_tools.IDEAL_OPERATION:
            raise RuntimeError(
                "matcher selected a non-polynomial operation; this direct-Laurent "
                "experiment fails closed without changing the decision"
            )

        portfolio_root = destination / "03_guarded_formalizations"

        def formalize(label: str, temperature: float) -> dict[str, Any]:
            root = portfolio_root / label
            role = base.Role(
                endpoint=compiler.endpoint,
                model=compiler.model,
                temperature=temperature,
                reasoning_effort=compiler.reasoning_effort,
            )
            try:
                raw, parsed, call = call_compiler(
                    role=role,
                    system_prompt=FORMALIZER_SYSTEM,
                    user_prompt=formalization_prompt(problem, proof, detection, matcher),
                    destination=root / "model",
                    stage="guarded_polynomial_formalization",
                    master_seed=base.stable_seed(master_seed, f"formalizer:{label}"),
                    parser=parse_guarded_formalization,
                    request_timeout_sec=model_request_timeout_sec,
                )
                parsed = dict(parsed)
                canonical = str(parsed.pop("normalized_markdown"))
                profile = exact_tools.ideal_request_profile(parsed["arguments"])
                base.write_text(root / "formalization_raw.md", raw)
                base.write_text(root / "formalization.md", canonical)
                _write_json(root / "guard_program.json", parsed["guard_program"])
                _write_json(
                    root / "surface_normalization.json",
                    parsed["surface_normalization"],
                )
                _write_json(root / "request_profile.json", profile)
                return {
                    "label": label,
                    "temperature": temperature,
                    "state": "compiled",
                    "formalization_text": canonical,
                    "formalization": parsed,
                    "request_profile": profile,
                    "call": call,
                }
            except Exception as error:
                failure = {
                    "label": label,
                    "temperature": temperature,
                    "state": "compiler_failed",
                    "error": f"{type(error).__name__}: {error}",
                }
                _write_json(root / "failure.json", failure)
                return failure

        if resume_formalizations_root is None:
            formalization_rows = []
            with ThreadPoolExecutor(max_workers=len(FORMALIZATION_SCHEDULE)) as executor:
                futures = {
                    executor.submit(formalize, label, temperature): label
                    for label, temperature in FORMALIZATION_SCHEDULE
                }
                for future in as_completed(futures):
                    formalization_rows.append(future.result())
        order = {label: index for index, (label, _) in enumerate(FORMALIZATION_SCHEDULE)}
        formalization_rows.sort(key=lambda row: order[str(row["label"])])
        if not any(row["state"] == "compiled" for row in formalization_rows):
            raise RuntimeError("all eight guarded formalizations failed strict parsing")
        dedup = deduplicate_formalizations(formalization_rows)
        representatives = dedup.pop("representatives")
        _write_json(destination / "04_deduplication/ledger.json", dedup)

        exact_rows: list[dict[str, Any]] = []
        for row in representatives:
            label = str(row["label"])
            route_root = destination / "05_direct_laurent_routes" / label
            arguments = row["formalization"]["arguments"]
            guard_program = row["formalization"]["guard_program"]
            route: dict[str, Any] = {
                "label": label,
                "temperature": row["temperature"],
                "deduplication_key": row["deduplication_key"],
                "state": "started",
            }
            try:
                preview = laurent.bounded_preview_only(
                    source_arguments=arguments,
                    candidate_arguments=arguments,
                    guard_program=guard_program,
                    output_dir=route_root / "01_preview",
                    timeout_sec=laurent_preprocess_timeout_sec,
                    memory_mb=exact_memory_mb,
                )
                route["preview"] = preview
                screen = laurent.bounded_screen_persisted_preview_target(
                    source_arguments=arguments,
                    candidate_arguments=arguments,
                    guard_program=guard_program,
                    preview_output_dir=route_root / "01_preview",
                    output_dir=route_root / "02_target_screen",
                    singular_binary=singular_binary,
                    timeout_sec=singular_timeout_sec,
                    memory_mb=exact_memory_mb,
                    expected_transform_sha256=str(preview["transform_sha256"]),
                    expected_derived_profile=preview["derived_profile"],
                    expected_structural_preview_sha256=str(
                        preview["preview_file_sha256"]
                    ),
                )
                route["screen"] = screen
                if screen["state"] != "proved":
                    route["state"] = "singular_not_proved"
                    _write_json(route_root / "route_state.json", route)
                    exact_rows.append(route)
                    continue
                identity_validation = {
                    "schema": "cognitive-well-v0309-identity-source-validation-v1",
                    "decision": "ACCEPT",
                    "reason": "source and candidate are the same canonical guarded formalization",
                    "source_arguments_sha256": exact_tools.stable_hash(arguments),
                    "candidate_arguments_sha256": exact_tools.stable_hash(arguments),
                    "guard_program_sha256": exact_tools.stable_hash(guard_program),
                    "identity": True,
                }
                _write_json(route_root / "identity_source_validation.json", identity_validation)
                prepared = laurent.bounded_preprocess_only(
                    source_arguments=arguments,
                    candidate_arguments=arguments,
                    guard_program=guard_program,
                    exact_transformation_validation=identity_validation,
                    output_dir=route_root / "03_laurent_lift",
                    timeout_sec=laurent_preprocess_timeout_sec,
                    memory_mb=exact_memory_mb,
                    expected_transform_sha256=str(preview["transform_sha256"]),
                    expected_derived_profile=preview["derived_profile"],
                    expected_structural_preview_sha256=str(
                        preview["preview_file_sha256"]
                    ),
                )
                identity_replay = laurent.verify_exported_membership_identity(
                    output_dir=route_root / "02_target_screen", result=screen
                )
                if identity_replay.get("verified") is not True:
                    raise ValueError("Singular multiplier identity did not replay")
                event_text = render_exact_evidence(route_root, screen, prepared)
                base.write_text(route_root / "04_exact_evidence.md", event_text)
                route.update(
                    state="singular_proved",
                    prepared=prepared,
                    identity_replay=identity_replay,
                    event_text=event_text,
                )
            except laurent.LaurentInapplicableError as error:
                route.update(
                    state="laurent_inapplicable",
                    error=f"{type(error).__name__}: {error}",
                )
            except Exception as error:
                route.update(
                    state="exact_failed_closed",
                    error=f"{type(error).__name__}: {error}",
                )
            exact_rows.append(route)
            _write_json(
                route_root / "route_state.json",
                {key: value for key, value in route.items() if key != "event_text"},
            )
            if on_promoted is not None and route["state"] == "singular_proved":
                audit_root = destination / "06_post_singular_audits" / label
                try:
                    audit_text, semantic_audit, audit_call = call_model(
                        role=auditor,
                        system_prompt=POST_SINGULAR_AUDITOR_SYSTEM,
                        user_prompt=post_singular_audit_prompt(
                            problem=problem, proof=proof, detection_text=detection_text,
                            matcher_text=matcher_text, formalization_text=str(row["formalization_text"]),
                        ),
                        destination=audit_root / "model",
                        stage="post_singular_guarded_formalization_audit",
                        master_seed=base.stable_seed(master_seed, f"post-singular-audit:{label}"),
                        parser=parse_post_singular_audit,
                        request_timeout_sec=model_request_timeout_sec,
                    )
                    base.write_text(audit_root / "audit.md", audit_text)
                    _write_json(audit_root / "result.json", {
                        "state": "accepted" if semantic_audit["accepted"] else "rejected",
                        "audit": semantic_audit, "call": audit_call,
                        "formalization_sha256": base.sha256_text(str(row["formalization_text"])),
                        "exact_result_supplied": False, "laurent_outcome_supplied": False,
                    })
                except Exception as error:
                    _write_json(audit_root / "failure.json", {"error": f"{type(error).__name__}: {error}"})
                    continue
                if not semantic_audit["accepted"]:
                    continue
                selection = {
                    "selected_label": label, "policy": "first_fully_promoted_in_frozen_schedule",
                    "selected_route_state_sha256": _sha256_file(route_root / "route_state.json"),
                    "selected_audit_result_sha256": _sha256_file(audit_root / "result.json"),
                    "untried_labels": [item["label"] for item in representatives if order[item["label"]] > order[label]],
                }
                _write_json(destination / "07_selection/selection.json", selection)
                result = on_promoted(
                    problem=problem, proof=proof, formalization=row["formalization"],
                    route=route, route_root=route_root, acquisition_root=destination,
                    audit_root=audit_root, matcher=matcher, selection=selection,
                )
                if result.get("state") != "completed":
                    raise RuntimeError("promoted-route proof synthesis did not complete")
                result = {**result, "selected_label": label, "selected_operation": matcher["operation"],
                          "fresh_detection": resume_formalizations_root is None,
                          "calls": {"detection": detection_call, "matcher": matcher_call}}
                _write_json(destination / "result.json", result)
                _write_json(destination / "manifest.json", {**preflight, **result})
                return result

        if on_promoted is not None:
            raise RuntimeError("no formalization passed both exact replay and independent semantic audit")

        proved_rows = [row for row in exact_rows if row["state"] == "singular_proved"]
        if not proved_rows:
            raise RuntimeError("no deduplicated guarded formalization produced a proved Laurent target")

        def audit(row: Mapping[str, Any]) -> dict[str, Any]:
            label = str(row["label"])
            source_row = next(item for item in representatives if item["label"] == label)
            root = destination / "06_post_singular_audits" / label
            try:
                text, parsed, call = base._model_call(
                    role=auditor,
                    system_prompt=POST_SINGULAR_AUDITOR_SYSTEM,
                    user_prompt=post_singular_audit_prompt(
                        problem=problem,
                        proof=proof,
                        detection_text=detection_text,
                        matcher_text=matcher_text,
                        formalization_text=str(source_row["formalization_text"]),
                    ),
                    destination=root / "model",
                    stage="post_singular_guarded_formalization_audit",
                    master_seed=base.stable_seed(master_seed, f"post-singular-audit:{label}"),
                    parser=parse_post_singular_audit,
                    request_timeout_sec=model_request_timeout_sec,
                )
                base.write_text(root / "audit.md", text)
                return {
                    **dict(row),
                    "state": "accepted" if parsed["accepted"] else "rejected",
                    "audit_text": text,
                    "audit": parsed,
                    "audit_call": call,
                }
            except Exception as error:
                return {
                    **dict(row),
                    "state": "audit_failed",
                    "audit_error": f"{type(error).__name__}: {error}",
                }

        audited: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=len(proved_rows)) as executor:
            futures = {executor.submit(audit, row): row["label"] for row in proved_rows}
            for future in as_completed(futures):
                audited.append(future.result())
        accepted = [row for row in audited if row["state"] == "accepted"]
        if not accepted:
            raise RuntimeError("all Singular-proved formalizations failed Qwen semantic audit")
        selected = min(accepted, key=_route_key)
        selected_label = str(selected["label"])
        selected_source = next(
            row for row in representatives if row["label"] == selected_label
        )
        selection = {
            "schema": "cognitive-well-v0309-direct-laurent-selection-v1",
            "ranking": [
                "derived symbols",
                "derived generators",
                "maximum degree",
                "monomials",
                "AST nodes",
                "transform SHA-256",
                "schedule label",
            ],
            "selected_label": selected_label,
            "selected_key": list(_route_key(selected)),
            "rows": [
                {
                    "label": row["label"],
                    "state": row["state"],
                    "derived_profile": row.get("screen", {}).get("derived_profile"),
                    "transform_sha256": row.get("screen", {}).get("transform_sha256"),
                }
                for row in sorted(audited, key=lambda item: str(item["label"]))
            ],
        }
        _write_json(destination / "07_selection/selection.json", selection)

        compilation_text = str(selected_source["formalization_text"])
        audit_text = str(selected["audit_text"])
        event_text = str(selected["event_text"])
        bridge_text = ""
        bridge: Mapping[str, Any] | None = None
        bridge_audit: Mapping[str, Any] | None = None
        prior_bridge_audit: Mapping[str, Any] | None = None
        for cycle in (1, 2, 3):
            bridge_text, bridge, _ = base._model_call(
                role=rewriter,
                system_prompt=base.BRIDGE_SYSTEM,
                user_prompt=base.bridge_prompt(
                    problem,
                    proof,
                    detection_text,
                    compilation_text,
                    audit_text,
                    event_text,
                    prior_bridge_audit,
                ),
                destination=destination / f"08_bridge/cycle_{cycle:02d}/model",
                stage="direct_laurent_post_tool_bridge",
                master_seed=master_seed + cycle,
                parser=protocol.parse_bridge,
                request_timeout_sec=model_request_timeout_sec,
            )
            base.write_text(
                destination / f"08_bridge/cycle_{cycle:02d}/bridge.md", bridge_text
            )
            audit_bridge_text, bridge_audit, _ = base._model_call(
                role=auditor,
                system_prompt=base.BRIDGE_AUDITOR_SYSTEM,
                user_prompt=base.bridge_audit_prompt(
                    problem, proof, compilation_text, event_text, bridge_text
                ),
                destination=destination / f"09_bridge_audit/cycle_{cycle:02d}/model",
                stage="direct_laurent_bridge_audit",
                master_seed=master_seed + cycle,
                parser=protocol.parse_bridge_audit,
                request_timeout_sec=model_request_timeout_sec,
            )
            base.write_text(
                destination / f"09_bridge_audit/cycle_{cycle:02d}/audit.md",
                audit_bridge_text,
            )
            if bridge_audit["accepted"]:
                break
            prior_bridge_audit = bridge_audit
        if not bridge or not bridge_audit or not bridge_audit["accepted"]:
            raise RuntimeError("post-Singular proof bridge remained rejected")
        if bridge["verdict"] == "NO_USABLE_RESULT":
            raise RuntimeError("accepted certificate produced no usable proof bridge")

        current_proof = proof
        proof_audit: Mapping[str, Any] | None = None
        prior_proof_audit: Mapping[str, Any] | None = None
        for cycle in (1, 2, 3):
            current_proof, _, _ = base._model_call(
                role=rewriter,
                system_prompt=base.REWRITER_SYSTEM,
                user_prompt=base.rewrite_prompt(
                    problem,
                    proof,
                    compilation_text,
                    event_text,
                    bridge_text,
                    current_proof,
                    prior_proof_audit,
                ),
                destination=destination / f"10_proof_rewrite/cycle_{cycle:02d}/model",
                stage="direct_laurent_whole_proof_rewrite",
                master_seed=master_seed + cycle,
                parser=base._terminal_proof,
                request_timeout_sec=model_request_timeout_sec,
            )
            base.write_text(
                destination / f"10_proof_rewrite/cycle_{cycle:02d}/terminal_proof.md",
                current_proof,
            )
            proof_audit_text, proof_audit, _ = base._model_call(
                role=auditor,
                system_prompt=base.PROOF_AUDITOR_SYSTEM,
                user_prompt=base.proof_audit_prompt(
                    problem, compilation_text, event_text, bridge_text, current_proof
                ),
                destination=destination / f"11_proof_audit/cycle_{cycle:02d}/model",
                stage="direct_laurent_whole_proof_audit",
                master_seed=master_seed + cycle,
                parser=protocol.parse_proof_audit,
                request_timeout_sec=model_request_timeout_sec,
            )
            base.write_text(
                destination / f"11_proof_audit/cycle_{cycle:02d}/audit.md",
                proof_audit_text,
            )
            if proof_audit["passed"]:
                break
            prior_proof_audit = proof_audit
        if not proof_audit or not proof_audit["passed"]:
            raise RuntimeError("whole replacement proof remained rejected")
        terminal_path = destination / "terminal_proof.md"
        base.write_text(terminal_path, current_proof)
        result = {
            "schema": "cognitive-well-v0309-direct-laurent-result-v1",
            "state": "completed",
            "problem_id": problem.problem_id,
            "selected_operation": matcher["operation"],
            "selected_label": selected_label,
            "gemma_compression_stage": False,
            "singular_proved": True,
            "multiplier_identity_reexpanded": True,
            "laurent_lift_verified": True,
            "semantic_audit_accepted": True,
            "bridge_audit_accepted": True,
            "proof_audit_passed": True,
            "terminal_proof": str(terminal_path),
            "terminal_proof_sha256": base.sha256_text(current_proof),
            "calls": {"detection": detection_call, "matcher": matcher_call},
        }
        _write_json(destination / "result.json", result)
        _write_json(destination / "manifest.json", {**preflight, "state": "completed"})
        return result
    except Exception as error:
        failure = {
            "schema": "cognitive-well-v0309-direct-laurent-failure-v1",
            "state": "failed_closed",
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        _write_json(destination / "failure.json", failure)
        _write_json(
            destination / "manifest.json",
            {**preflight, "state": "failed_closed", "error": failure["error"]},
        )
        return failure
