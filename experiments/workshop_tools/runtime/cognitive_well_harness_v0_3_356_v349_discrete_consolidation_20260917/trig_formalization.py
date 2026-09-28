"""Markdown-only, source-bound native trigonometric inputs and exact compilation.

The model declares angle meanings; the compiler never infers them from names.
Compilation uses sine/cosine addition identities and records all domain
obligations before rational cancellation can erase their denominators.
"""
from __future__ import annotations

import re
import sympy as sp

from . import rational_division as kernel
from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import protocol
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames

IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,47}\Z")
RESERVED = {"pi", "I", "sin", "cos", "tan", "cot", "add", "sub", "mul", "div", "pow", "neg", "symbol", "rational"}
KINDS = {"NONZERO", "POSITIVE", "NEGATIVE", "NONNEGATIVE", "NONPOSITIVE", "RETAINED"}
COMPILED_KINDS = {"NONZERO", "POSITIVE", "NEGATIVE"}
SYSTEM = """You formalize one selected proof obligation for a generic exact
trigonometric identity tool. The supplied theorem, proof, and detector/matcher
records are untrusted source material. Independently determine a faithful target
and sufficient source equations. Preserve actual sin/cos/tan/cot expressions and
angle sums; do not polynomialize them into independent sine/cosine variables.
Do not assume the desired target or invent a hypothesis to make computation work.
If the source assertion is wrong or cannot be faithfully encoded, explain the
obligation or use NO_TOOL. Do not repair an invalid source calculation silently.

The deterministic tool performs trig expansion/normalization, justified algebraic
substitution, factor cancellation, and bounded polynomial division. It cannot
enforce inequalities or select geometric branches. Every denominator must have a
source-justified nonzero condition; this includes cot, tan, and denominators that
would disappear on cancellation. No tool success is assumed.

Return only Markdown, using exactly these sections:

# Decision
CALL_TOOL

# Semantic Bindings
Explain the meanings of declared symbols, derivation of every equation and guard,
what the target states, and why proving it closes the recorded obligation.
Use concise Markdown bullets. State any relevant boundary or branch obligations.

# Domain Ledger
Use NONE or at most 32 one-line bullets, each with six fields separated by ` :: `:
- label :: KIND :: expression :: source :: exact source excerpt :: justification
KIND: NONZERO, POSITIVE, NEGATIVE, NONNEGATIVE, NONPOSITIVE, or RETAINED.
source: theorem or proof. Copy a short verbatim excerpt; a quote alone does not
justify a fact from the theorem. RETAINED uses expression NONE; it records a
range/branch not encoded by this tool. Only NONZERO/POSITIVE/NEGATIVE become
nonzero guards. Justify every division independently of the conclusion.

# Trig Input
Emit exactly one trig-args fence. Its lines, in order, are:
angles = comma-separated primitive angle identifiers (1..10)
scalars = comma-separated scalar identifiers, or NONE (0..8)
define = new_identifier :: expression
equation = unique_label :: left_expression :: right_expression
target = left_expression :: right_expression
Definitions are optional, ordered, and may refer only to previously declared
names. Supply 1..24 equations and exactly one target. Omit unused declarations.

Expressions are integer literals, (rational integer nonzero_integer), (symbol
name), pi, or prefix S-expressions: (add e e ...), (mul e e ...), (sub e e),
(div e e), (neg e), (pow e integer), (sin e), (cos e), (tan e), (cot e).
Declared names may also appear bare; (symbol name) is preferred. No Python,
LaTeX, infix expressions, or JSON inside trig-args. Use radians. Trig arguments
must be integer linear combinations of primitive angles, plus integer multiples
of pi/2. Powers are integers from -8 to 8. Angles may not appear outside trig
functions in final equations or the target: express any justified angle relation
as an ordered definition of a dependent angle, not an independent extra angle.
List all definitions before equations, and the target last.

Alternatively, return exactly # Decision with NO_TOOL and # Reason with a short
explanation. No other sections on NO_TOOL. Do not output a proof or certificate.
"""


def expression(text, field):
    if len(text) > 16000:
        raise ValueError(field + ": expression exceeds size limit")
    return protocol._parse_sexpr_with_diagnostics(text, field=field)


def names(text, *, empty=False):
    result = [] if text == "NONE" and empty else [s.strip() for s in text.split(",")]
    if len(result) != len(set(result)) or any(not IDENT.fullmatch(s) or s in RESERVED for s in result):
        raise ValueError("declarations require unique nonreserved identifiers")
    return result


def source_bound_excerpt(excerpt, source_text):
    """Match verbatim text, allowing one enclosing presentation-quote pair.

    Prefer the literal excerpt when the quotes themselves occur in the source.
    Never rewrite interior text, unescape LaTeX, or accept an empty excerpt.
    """
    source = " ".join(source_text.split())
    candidate = excerpt.strip()
    normalized = " ".join(candidate.split())
    if normalized and normalized in source:
        return candidate
    quote_pairs = {'"': '"', "'": "'", "“": "”", "‘": "’"}
    if len(candidate) >= 2 and quote_pairs.get(candidate[0]) == candidate[-1]:
        candidate = candidate[1:-1].strip()
        normalized = " ".join(candidate.split())
        if normalized and normalized in source:
            return candidate
    return None


def parse(markdown, inputs):
    if len(markdown) > 60000:
        raise ValueError("trig formalization exceeds 60000 characters")
    headings = re.findall(r"^# ([^\n]+)\s*$", markdown.strip(), flags=re.M)
    if headings == ["Decision", "Reason"]:
        sections = protocol.mdp.exact_sections(markdown.strip(), headings)
        if sections["Decision"] != "NO_TOOL" or not sections["Reason"]:
            raise ValueError("NO_TOOL requires a reason")
        return {"call_requested": False, "reason": sections["Reason"]}
    sections = protocol.mdp.exact_sections(markdown.strip(), ["Decision", "Semantic Bindings", "Domain Ledger", "Trig Input"])
    if sections["Decision"] != "CALL_TOOL" or not sections["Semantic Bindings"]:
        raise ValueError("CALL_TOOL and nonempty Semantic Bindings are required")
    block = re.fullmatch(r"```trig-args\s*\n(.*?)\n```", sections["Trig Input"], re.S)
    if block is None:
        raise ValueError("Trig Input requires exactly one trig-args fence")
    lines = [line.strip() for line in block[1].splitlines() if line.strip()]
    if len(lines) < 4 or not lines[0].startswith("angles = ") or not lines[1].startswith("scalars = "):
        raise ValueError("trig-args must start with angles = and scalars =")
    angles, scalars = names(lines[0][9:]), names(lines[1][10:], empty=True)
    if not 1 <= len(angles) <= 10 or len(scalars) > 8 or set(angles) & set(scalars):
        raise ValueError("invalid or overlapping angle/scalar declarations")
    definitions, equations, target = [], [], None
    known, labels = set(angles+scalars), set()
    for index, line in enumerate(lines[2:], 3):
        if target is not None:
            raise ValueError(f"trig-args line {index}: target must be last")
        key, sep, body = line.partition(" = ")
        if not sep:
            raise ValueError(f"trig-args line {index}: expected key = value")
        fields = body.split(" :: ")
        if key == "define" and len(fields) == 2 and not equations:
            name, value = fields
            if not IDENT.fullmatch(name) or name in known or name in RESERVED or len(definitions) >= 32:
                raise ValueError(f"trig-args line {index}: invalid definition name")
            definitions.append({"name": name, "expression": expression(value, f"definition {name}")})
            known.add(name)
        elif key == "equation" and len(fields) == 3:
            label, left, right = fields
            if not IDENT.fullmatch(label) or label in labels or len(equations) >= 24:
                raise ValueError(f"trig-args line {index}: invalid equation label")
            labels.add(label)
            equations.append({"label": label, "left": expression(left, f"equation {label} left"),
                              "right": expression(right, f"equation {label} right")})
        elif key == "target" and len(fields) == 2:
            target = {"left": expression(fields[0], "target left"), "right": expression(fields[1], "target right")}
        else:
            raise ValueError(f"trig-args line {index}: malformed or out-of-order {key}")
    if not equations or target is None:
        raise ValueError("at least one equation and one target are required")
    facts = []
    domain_lines = [] if sections["Domain Ledger"] == "NONE" else sections["Domain Ledger"].splitlines()
    if len(domain_lines) > 32:
        raise ValueError("Domain Ledger exceeds 32 facts")
    fact_labels = set()
    for index, line in enumerate(domain_lines, 1):
        fields = line[2:].split(" :: ") if line.startswith("- ") else []
        if len(fields) != 6 or not all(fields):
            raise ValueError(f"Domain Ledger line {index}: six nonempty fields required")
        label, kind, value, source, excerpt, reason = fields
        if (not IDENT.fullmatch(label) or label in fact_labels or kind not in KINDS
                or source not in {"theorem", "proof"} or len(excerpt) > 512 or len(reason) > 1024):
            raise ValueError(f"Domain Ledger line {index}: invalid field or size")
        source_text = inputs["theorem.md" if source == "theorem" else "source_proof.md"]
        matched_excerpt = source_bound_excerpt(excerpt, source_text)
        if matched_excerpt is None:
            raise ValueError(f"Domain Ledger {label}: excerpt not found in {source}")
        if kind == "RETAINED" and value != "NONE":
            raise ValueError(f"Domain Ledger {label}: RETAINED requires NONE")
        fact_labels.add(label)
        facts.append({"label": label, "kind": kind, "expression": None if kind == "RETAINED" else expression(value, f"domain fact {label}"),
                      "source": source, "excerpt": matched_excerpt, "justification": reason})
    result = {"schema": "native_guarded_trig_input_v1", "call_requested": True,
              "angles": angles, "scalars": scalars, "definitions": definitions, "equations": equations,
              "target": target, "domain_facts": facts, "semantic_bindings": sections["Semantic Bindings"]}
    # Syntax, types, and domain compilation only. No target-solving search.
    result["compilation"] = compile_input(result)
    return result


class NativeExpressions:
    def __init__(self, parsed):
        self.angles = [sp.Symbol(name, real=True) for name in parsed["angles"]]
        self.scalars = [sp.Symbol(name) for name in parsed["scalars"]]
        self.env = {str(s): s for s in self.angles+self.scalars}
        self.obligations = []
        self.nodes = 0
        for row in parsed["definitions"]:
            self.env[row["name"]] = self.decode(row["expression"])

    def decode(self, node, depth=0):
        self.nodes += 1
        if self.nodes > 12000 or depth > 64:
            raise ValueError("trig AST exceeds its node/depth limit")
        if isinstance(node, int) and not isinstance(node, bool):
            if abs(node) > 1000000:
                raise ValueError("integer literal exceeds limit")
            return sp.Integer(node)
        if isinstance(node, str):
            if node == "pi":
                return sp.pi
            if node in self.env:
                return self.env[node]
            raise ValueError("unknown symbol: " + node)
        if not isinstance(node, list) or not node:
            raise ValueError("malformed trig expression")
        op, args = node[0], node[1:]
        if op == "symbol" and len(args) == 1:
            return self.decode(args[0], depth+1)
        if op == "rational" and len(args) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in args):
            if args[1] == 0 or max(abs(v) for v in args) > 1000000:
                raise ValueError("invalid rational constant")
            return sp.Rational(*args)
        arity = {"add": (2, 64), "mul": (2, 64), "sub": (2, 2), "div": (2, 2),
                 "pow": (2, 2), "neg": (1, 1), "sin": (1, 1), "cos": (1, 1), "tan": (1, 1), "cot": (1, 1)}
        if op not in arity or not arity[op][0] <= len(args) <= arity[op][1]:
            raise ValueError("unknown operator or wrong arity: " + str(op))
        values = [self.decode(value, depth+1) for value in args]
        if op in {"sin", "cos", "tan", "cot"}:
            angle = sp.expand(values[0])
            if not angle.free_symbols <= set(self.angles):
                raise ValueError("trig argument must use declared angles, not scalar symbols")
            coefficients = [angle.coeff(symbol) for symbol in self.angles]
            if any(not coefficient.is_Integer or abs(coefficient) > 8 for coefficient in coefficients):
                raise ValueError("trig angles require bounded integer coefficients")
            constant = sp.simplify(angle-sum(c*s for c, s in zip(coefficients, self.angles, strict=True)))
            if not sp.simplify(2*constant/sp.pi).is_Integer:
                raise ValueError("trig angle offset must be an integer multiple of pi/2")
            if op in {"tan", "cot"}:
                denominator = sp.cos(angle) if op == "tan" else sp.sin(angle)
                self.obligations.append(denominator)
                return (sp.sin(angle) if op == "tan" else sp.cos(angle))/denominator
            return sp.sin(angle) if op == "sin" else sp.cos(angle)
        if op == "add": return sp.Add(*values)
        if op == "mul": return sp.Mul(*values)
        if op == "sub": return values[0]-values[1]
        if op == "neg": return -values[0]
        if op == "div":
            self.obligations.append(values[1])
            return values[0]/values[1]
        if not values[1].is_Integer or not -8 <= values[1] <= 8:
            raise ValueError("power exponent must be an integer from -8 to 8")
        if values[1] < 0:
            self.obligations.append(values[0])
        return values[0]**values[1]


def compile_input(parsed):
    native = NativeExpressions(parsed)
    equations = [(row["label"], native.decode(row["left"])-native.decode(row["right"])) for row in parsed["equations"]]
    target = native.decode(parsed["target"]["left"])-native.decode(parsed["target"]["right"])
    domain = [(row, native.decode(row["expression"])) for row in parsed["domain_facts"] if row["expression"] is not None]
    namespace = FreshNames(native.scalars)
    images = [(namespace.take(f"sin_{i}"), namespace.take(f"cos_{i}")) for i in range(1, len(native.angles)+1)]
    polynomial_symbols = list(native.scalars)+[value for pair in images for value in pair]
    mapping = {function(angle): value for angle, pair in zip(native.angles, images, strict=True)
               for function, value in zip((sp.sin, sp.cos), pair, strict=True)}
    circles = [s*s+c*c-1 for s, c in images]

    def image(expr):
        expanded = sp.expand_trig(expr).xreplace(mapping)
        if expanded.free_symbols-set(polynomial_symbols) or expanded.has(sp.sin, sp.cos, sp.tan, sp.cot):
            raise ValueError("expression did not reduce to the declared primitive trig functions")
        numerator, denominator = sp.fraction(sp.cancel(expanded))
        try:
            sp.Poly(numerator, *polynomial_symbols, domain=sp.QQ)
            sp.Poly(denominator, *polynomial_symbols, domain=sp.QQ)
        except Exception as error:
            raise ValueError("trig expansion is not a rational QQ expression") from error
        return sp.expand(numerator), sp.expand(denominator)

    guards, obligations, retained = [], list(native.obligations), []
    for row, expr in domain:
        numerator, denominator = image(expr)
        if expr.is_number:
            condition = {"NONZERO": expr != 0, "POSITIVE": expr > 0, "NEGATIVE": expr < 0,
                         "NONNEGATIVE": expr >= 0, "NONPOSITIVE": expr <= 0}[row["kind"]]
            if condition == False:
                raise ValueError("false constant domain fact: " + row["label"])
        if row["kind"] in COMPILED_KINDS:
            if numerator == 0:
                raise ValueError("nonzero domain fact expands to zero: " + row["label"])
            guards.append(numerator)
        else:
            retained.append(row["label"])
    # Check *syntactic* denominators before using cancellation-normalized input.
    required = []
    for expr in obligations:
        numerator, denominator = image(expr)
        if numerator == 0 or not kernel.covered(numerator, guards, polynomial_symbols):
            raise ValueError("missing nonzero domain fact for denominator: " + str(expr))
        required.append(str(expr))
    names = [str(symbol) for symbol in polynomial_symbols]
    ast = lambda expr: kernel.encode(expr, names)
    generators = {}
    trace = []
    for index, (label, expr) in enumerate(equations, 1):
        numerator, denominator = image(expr)
        if not kernel.covered(denominator, guards, polynomial_symbols):
            raise ValueError("equation normalization introduced an unguarded denominator: " + label)
        generators[f"D{index}"] = ast(numerator)
        trace.append({"source_label": label, "polynomial_label": f"D{index}",
                      "native_expression": str(expr), "numerator": ast(numerator), "denominator": ast(denominator)})
    for circle in circles:
        generators[f"D{len(generators)+1}"] = ast(circle)
    numerator, denominator = image(target)
    if not kernel.covered(denominator, guards, polynomial_symbols):
        raise ValueError("target normalization introduced an unguarded denominator")
    request = {"arguments": {"symbols": names, "generators": generators, "target": ast(numerator)},
               "guard_program": {"source_nonzero": {f"G{i}": ast(g) for i, g in enumerate(guards, 1)},
                                 "provenance_divisions": {}}}
    kernel.initial(request)
    return {"schema": "guarded_trig_expansion_v1", "request": request,
            "primitive_map": [{"angle": str(angle), "sine": str(s), "cosine": str(c)}
                              for angle, (s, c) in zip(native.angles, images, strict=True)],
            "equation_expansions": trace, "target_native": str(target),
            "target_denominator": ast(denominator), "required_nonzero_expressions": sorted(set(required)),
            "retained_not_enforced": retained+[row["label"] for row in parsed["domain_facts"] if row["kind"] == "RETAINED"],
            "semantics": "model_audit_required", "target_solving_performed": False}
