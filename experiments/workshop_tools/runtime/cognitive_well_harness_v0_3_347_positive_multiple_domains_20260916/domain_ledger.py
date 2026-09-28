"""Source-bound Markdown domain facts; conservative nonzero compilation only.

Source quotation matching is deterministic. Entailment of a fact by that source,
and completeness of the domain inventory, remain the semantic auditor's job.
"""
from __future__ import annotations

import copy
import re

from . import pipeline
from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906 import pipeline as formal

VERSION = "source_bound_domain_ledger_v1_1"
KINDS = {"POSITIVE", "NEGATIVE", "NONZERO", "NONNEGATIVE", "NONPOSITIVE", "RETAINED"}
COMPILED_KINDS = {"POSITIVE", "NEGATIVE", "NONZERO"}
SOURCES = {"theorem": "theorem.md", "proof": "source_proof.md"}
CONTRACT = """# Domain Ledger

Insert this section between Semantic Bindings and Guard Program. Inventory the
source-grounded domain restrictions relevant to the encoding, not just the
denominators: signs, zeros, distinctness, ranges, and branches. Use Markdown bullets
with exactly six fields separated by ` :: `:

- label :: KIND :: expression :: source :: exact source excerpt :: justification

KIND is POSITIVE, NEGATIVE, NONZERO, NONNEGATIVE, NONPOSITIVE, or RETAINED.
For the first five, expression is a polynomial S-expression in declared symbols;
write each symbol leaf as (symbol name), not as a function call.
For RETAINED, expression is NONE and justification states the restriction and its
role (e.g. a range or branch the polynomial backend cannot directly represent).
source is theorem or proof; excerpt is an actual nonempty verbatim excerpt from
that source, without added quotation marks. Copy a short substring preserving its
LaTeX spelling; do not paraphrase the excerpt. Put explanations in justification.
A source excerpt is provenance, not
proof: justify the claimed implication independently from the theorem's hypotheses.
Use unique identifier labels, at most 32 bullets, excerpt <=512 characters and
justification <=1024 characters per bullet. These are ceilings, not quotas: list
each distinct fact once; never pad the ledger with repetitions. Use NONE only if no relevant domain
restrictions exist; explain this in Semantic Bindings.

The compiler emits nonzero guards only from POSITIVE, NEGATIVE, or NONZERO facts.
NONNEGATIVE, NONPOSITIVE, and RETAINED stay visible to the auditor but are NOT
enforced by this backend. Do not claim they were encoded. Where they matter,
explain why the algebraic implication on the enlarged domain is sufficient, or
choose a faithful encoding; never strengthen a weak inequality silently.
Every Guard Program denominator and source_nonzero must be covered by these
compiled nonzero facts (up to nonzero constants and polynomial factors). You may
leave Guard Program as NONE when the ledger supplies all needed nonzero guards
and no explicit division provenance is needed. Never add assumptions merely to
make the tool succeed. Emit all five sections in this order: Decision, Semantic
Bindings, Domain Ledger, Guard Program, Tool Arguments; NO_TOOL still uses only
Decision and Reason. Markdown only, no JSON.
"""
AUDIT_INSTRUCTIONS = """# Domain Coverage Audit

Check the Domain Ledger against the original hypotheses and symbol definitions,
independently of the author's claims. The compiler checks source excerpts and
simple implication rules, NOT whether an excerpt entails a fact or whether facts
are missing. Inventory relevant signs, zeros, distinctness, ranges, and branches;
check excluded boundary cases and every division. Reject invented or unjustified
guards. Check domain completeness under the domain/guard/branch checklist items.
The draft's proof source is untrusted even when quoted exactly. Facts marked
retained-only are not enforced by the algebra backend; verify the stated mapping
and sufficiency without silently using them as encoded hypotheses. Missing facts
may enlarge the algebraic domain; distinguish that from an invalid strengthening
of the original theorem. Do not infer that the tool has succeeded.
"""


def _space(text):
    return " ".join(text.split())


def compile_ledger(section, arguments, authored_guards, inputs):
    if inputs is None:
        raise ValueError("Domain Ledger requires the bound original theorem and proof")
    if len(section) > 20000:
        raise ValueError("Domain Ledger exceeds 20000 characters")
    lines = [] if section.strip() == "NONE" else section.strip().splitlines()
    if len(lines) > 32:
        raise ValueError("Domain Ledger exceeds 32 facts")
    # Report source-copy failures together, so a bounded repair need not discover
    # one mistyped quotation per model cycle. No semantic replacement is supplied.
    excerpt_errors=[]
    for line in lines:
        fields=line[2:].split(" :: ") if line.startswith("- ") else []
        if len(fields)==6 and fields[3] in SOURCES and fields[4]:
            if _space(fields[4]) not in _space(inputs[SOURCES[fields[3]]]):
                excerpt_errors.append(f"{fields[0]}: source excerpt not found in {fields[3]}")
    if excerpt_errors:
        raise ValueError("Domain Ledger "+"; ".join(excerpt_errors[:12])+
                         (f"; {len(excerpt_errors)-12} further excerpt mismatches" if len(excerpt_errors)>12 else ""))
    validated = formal.exact_tools.validate_ideal_arguments(arguments)
    symbolic = formal.exact_tools.require_sympy()
    facts, labels = [], set()
    normalization={"declared_symbol_leaves":0,"typed_integer_literals":0}
    ledger_program = {"provenance_divisions": {}, "source_nonzero": {}}
    for index, line in enumerate(lines, 1):
        fields = line[2:].split(" :: ") if line.startswith("- ") else []
        if len(fields) != 6 or not all(fields):
            raise ValueError(f"Domain Ledger line {index}: expected six nonempty bullet fields")
        label, kind, expression, source, excerpt, reason = fields
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", label) is None or label in labels:
            raise ValueError("Domain Ledger labels must be unique identifiers")
        labels.add(label)
        if kind not in KINDS or source not in SOURCES:
            raise ValueError(f"Domain Ledger {label}: unsupported kind or source")
        if len(excerpt) > 512 or len(reason) > 1024:
            raise ValueError(f"Domain Ledger {label}: excerpt or justification exceeds its limit")
        if _space(excerpt) not in _space(inputs[SOURCES[source]]):
            raise ValueError(f"Domain Ledger {label}: source excerpt not found in {source}")
        node = None
        if kind == "RETAINED":
            if expression != "NONE":
                raise ValueError(f"Domain Ledger {label}: RETAINED requires expression NONE")
        else:
            surface=formal.protocol._parse_sexpr_with_diagnostics(expression,field=f"domain fact {label}")
            surface=formal.protocol._normalize_expression_leaves(surface,set(arguments["symbols"]),normalization)
            node = formal.mdp.expression_ast(surface)
            expr = formal.exact_tools._expression(node, validated["symbol_map"])
            poly = symbolic.Poly(expr, *validated["symbol_map"].values(), domain=symbolic.QQ)
            if poly.total_degree() == 0:
                value = poly.as_expr()
                ok = {"POSITIVE": value > 0, "NEGATIVE": value < 0, "NONZERO": value != 0,
                      "NONNEGATIVE": value >= 0, "NONPOSITIVE": value <= 0}[kind]
                if not ok:
                    raise ValueError(f"Domain Ledger {label}: false constant domain fact")
        rule = f"{kind.lower()}_implies_nonzero" if kind in COMPILED_KINDS else "retained_only"
        facts.append({"label": label, "kind": kind, "expression": node, "source": source,
                      "excerpt": excerpt, "justification": reason, "rule": rule})
        if kind in COMPILED_KINDS:
            ledger_program["source_nonzero"][label] = node
    typed = formal.transformation_validation
    compiled_factors = typed.derive_guards(ledger_program, arguments)
    needed = typed.derive_guards(authored_guards, arguments)
    # Both lists are already monic, square-free canonical QQ factors.
    available = {symbolic.srepr(e) for e in compiled_factors["expressions"]}
    missing = [row for e, row in zip(needed["expressions"], needed["records"], strict=True)
               if symbolic.srepr(e) not in available]
    if missing:
        raise ValueError("Domain Ledger does not justify Guard Program factors: " +
                         "; ".join(f"{row['expression']} ({', '.join(row['sources'])})" for row in missing))
    program = copy.deepcopy(authored_guards)
    taken = set(program["source_nonzero"]) | set(program["provenance_divisions"])
    for index, (label, node) in enumerate(ledger_program["source_nonzero"].items(), 1):
        name = f"DL{index}"
        while name in taken:
            name += "_"
        taken.add(name)
        program["source_nonzero"][name] = node
    report = {"schema": VERSION, "source_bound": True, "facts": facts,"surface_normalization":normalization,
              "compiled_nonzero_facts": len(ledger_program["source_nonzero"]),
              "retained_only_facts": sum(f["rule"] == "retained_only" for f in facts),
              "source_sha256": {name: pipeline.base.sha256_text(inputs[name].strip())
                                for name in SOURCES.values()},
              "authored_guard_program": authored_guards,
              "compiled_guard_program_sha256": formal.exact_tools.stable_hash(program),
              "semantic_grounding": "MODEL_AUDIT_REQUIRED", "domain_completeness": "MODEL_AUDIT_REQUIRED"}
    return program, report


def audit_summary(report):
    lines = ["# Deterministic Domain Compilation", "",
             "Source excerpts matched. Semantic entailment and completeness are NOT machine-certified."]
    lines += [f"- {f['label']}: {f['kind']} -> {f['rule']}" for f in report["facts"]]
    return "\n".join(lines)
