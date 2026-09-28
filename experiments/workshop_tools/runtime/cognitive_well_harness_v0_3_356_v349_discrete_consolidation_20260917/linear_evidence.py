"""Generic exact piecewise-linear implication checks with rational witnesses.

No game, geometry, sequence, or problem-specific semantics are implemented here.
The caller must independently audit the model's source-to-formula connection.
"""
from __future__ import annotations

from fractions import Fraction
import re
import time

import z3

from .trig_formalization import expression

OPERATION = "check_linear_real_implication"
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,47}\Z")
CONTRACT = """Exactly one linear-args Markdown fence containing these lines:
variables = comma-separated real variable names, or NONE
define = unique_name :: expression
assume = unique_label :: Boolean expression
conclude = Boolean expression
Definitions are optional and ordered; assumptions follow them; conclusion is last.
Use 0..16 variables, at most 48 definitions and 48 assumptions.
Expressions: integers, exact finite decimals, (rational numerator denominator), declared names, or
prefix forms (add e e ...), (sub e e), (mul e e ...), (div e constant),
(neg e), (abs e), (min e e ...), (max e e ...), (ite condition e e),
(kth_largest rank e e ...). Rank is a literal 1-based integer; at most 16 items.
Multiplication allows at most one nonconstant factor; division requires a nonzero
rational constant. No variable products, variable denominators, trig, code, JSON,
or unsupported operators. Predicates: (eq e e), (ne e e), (lt e e), (le e e),
(gt e e), (ge e e), (and p p ...), (or p p ...), (not p), (implies p p).
Include all domain restrictions and legal-case constraints as assumptions.
The tool searches assumptions AND NOT conclusion. A rational witness refutes the
encoded implication. UNSAT establishes only that exact encoded implication,
not an unencoded general theorem. A concrete instance can refute a universal
claim, but proving an instance cannot establish that universal claim.
"""


def normalize(text):
    """Presentation aliases and exact decimal literals only; never repair math."""
    if len(text) > 40000:
        raise ValueError("linear input exceeds 40000 characters")
    match = re.fullmatch(r"```(linear-args|tool-args)[ \t]*\r?\n(.*?)\r?\n```", text.strip(), re.S)
    if match is None:
        raise ValueError("expected one linear-args fence (tool-args alias accepted)")
    changes = []
    if match[1] != "linear-args":
        changes.append({"kind":"fence_alias", "from":match[1], "to":"linear-args"})
    lines = match[2].replace("\r\n", "\n").splitlines()
    decimal = re.compile(r"[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+)\Z")
    for index, line in enumerate(lines):
        field, sep, body = line.partition(" = ")
        if not sep or field.strip() not in {"define", "assume", "conclude"}:
            continue
        prefix = field + sep
        if field.strip() != "conclude":
            label, sep, body = body.partition(" :: ")
            if not sep:
                continue
            prefix += label + sep
        def literal(token):
            raw = token[0]
            if not decimal.fullmatch(raw):
                return raw
            if len(raw) > 24:
                raise ValueError("decimal literal exceeds size limit")
            value = Fraction(raw)  # No float conversion or rounding.
            if max(abs(value.numerator), value.denominator) > 1000000:
                raise ValueError("decimal literal exceeds rational bounds")
            canonical = str(value.numerator) if value.denominator == 1 else f"(rational {value.numerator} {value.denominator})"
            changes.append({"kind":"exact_decimal", "line":index+1, "from":raw, "to":canonical})
            return canonical
        lines[index] = prefix + re.sub(r"[^()\s]+", literal, body)
    return "```linear-args\n" + "\n".join(lines) + "\n```", changes


def parse(text):
    text, _ = normalize(text)
    if len(text) > 40000:
        raise ValueError("linear input exceeds 40000 characters")
    match = re.fullmatch(r"```linear-args\s*\n(.*?)\n```", text.strip(), re.S)
    if match is None:
        raise ValueError("expected one linear-args fence")
    lines = [s.strip() for s in match[1].splitlines() if s.strip()]
    if not lines or not lines[0].startswith("variables = "):
        raise ValueError("first line must be variables = names, or NONE")
    raw = lines[0][12:]
    names = [] if raw == "NONE" else [s.strip() for s in raw.split(",")]
    if len(names) > 16 or len(names) != len(set(names)) or any(not IDENT.fullmatch(s) for s in names):
        raise ValueError("variables require at most 16 unique identifiers")
    result = {"variables": names, "definitions": [], "assumptions": [], "conclusion": None}
    known, labels = set(names), set()
    for index, line in enumerate(lines[1:], 2):
        key, sep, body = line.partition(" = ")
        if not sep or result["conclusion"] is not None:
            raise ValueError(f"line {index}: expected key = value, with conclusion last")
        if key in {"define", "assume"}:
            label, sep, value = body.partition(" :: ")
            if not sep or not IDENT.fullmatch(label):
                raise ValueError(f"line {index}: expected identifier :: expression")
            dest = "definitions" if key == "define" else "assumptions"
            if len(result[dest]) >= 48 or label in known | labels:
                raise ValueError(f"line {index}: duplicate name or size limit")
            if key == "define" and result["assumptions"]:
                raise ValueError("definitions must precede assumptions")
            result[dest].append({"label": label, "expression": expression(value, f"line {index}")})
            (known if key == "define" else labels).add(label)
        elif key == "conclude":
            result["conclusion"] = expression(body, f"line {index}")
        else:
            raise ValueError(f"line {index}: unknown field {key}")
    if result["conclusion"] is None:
        raise ValueError("one conclusion is required")
    build(result)  # Type/linearity checks only; no solver search during parsing.
    return result


class Expressions:
    def __init__(self, variables, witness=None):
        self.symbolic = witness is None
        self.env = {name: (z3.Real(name) if self.symbolic else Fraction(witness[name])) for name in variables}
        self.nodes = 0

    def number(self, value):
        return z3.RealVal(str(value)) if self.symbolic else Fraction(value)

    def boolean(self, value):
        return z3.is_bool(value) if self.symbolic else isinstance(value, bool)

    def decode(self, node, depth=0):
        self.nodes += 1
        if self.nodes > 8000 or depth > 48:
            raise ValueError("linear AST node/depth limit")
        if isinstance(node, int) and not isinstance(node, bool):
            if abs(node) > 1000000:
                raise ValueError("integer literal limit")
            return self.number(node)
        if isinstance(node, str):
            if node not in self.env:
                raise ValueError("unknown or forward-referenced name: " + node)
            return self.env[node]
        if not isinstance(node, list) or not node:
            raise ValueError("invalid linear expression")
        op, args = node[0], node[1:]
        if op == "symbol" and len(args) == 1:
            return self.decode(args[0], depth+1)
        if op == "rational" and len(args) == 2 and all(isinstance(v, int) and not isinstance(v, bool) for v in args):
            if args[1] == 0 or max(map(abs, args)) > 1000000:
                raise ValueError("invalid rational literal")
            return self.number(Fraction(*args))
        arities = {"add": (2,32), "mul": (2,32), "sub": (2,2), "div": (2,2), "neg": (1,1),
                   "abs": (1,1), "min": (2,16), "max": (2,16), "ite": (3,3),
                   "kth_largest": (2,17), "not": (1,1), "and": (2,32), "or": (2,32),
                   "implies": (2,2), **{s:(2,2) for s in ("eq","ne","lt","le","gt","ge")}}
        if op not in arities or not arities[op][0] <= len(args) <= arities[op][1]:
            raise ValueError("unsupported operator/arity: " + str(op))
        rank = None
        if op == "kth_largest":
            rank, args = args[0], args[1:]
            if not isinstance(rank, int) or isinstance(rank, bool) or not 1 <= rank <= len(args):
                raise ValueError("kth_largest rank must be a literal integer within the item count")
        values = [self.decode(a, depth+1) for a in args]
        if op in {"and", "or", "not", "implies"}:
            if not all(self.boolean(v) for v in values):
                raise ValueError("Boolean operands required")
            if self.symbolic:
                return {"and":z3.And,"or":z3.Or,"not":z3.Not,"implies":z3.Implies}[op](*values)
            return all(values) if op=="and" else any(values) if op=="or" else not values[0] if op=="not" else (not values[0] or values[1])
        if op == "ite":
            if not self.boolean(values[0]) or any(self.boolean(v) for v in values[1:]):
                raise ValueError("ite requires a Boolean condition and two real branches")
            return z3.If(*values) if self.symbolic else values[1] if values[0] else values[2]
        if any(self.boolean(v) for v in values):
            raise ValueError("real operands required")
        if op in {"eq","ne","lt","le","gt","ge"}:
            a,b=values
            return {"eq":lambda:a==b,"ne":lambda:a!=b,"lt":lambda:a<b,"le":lambda:a<=b,"gt":lambda:a>b,"ge":lambda:a>=b}[op]()
        if op == "mul" and self.symbolic:
            if sum(not z3.is_rational_value(z3.simplify(v)) for v in values) > 1:
                raise ValueError("multiplication must be linear: at most one nonconstant factor")
        if op == "div":
            denominator = z3.simplify(values[1]) if self.symbolic else values[1]
            if self.symbolic and not z3.is_rational_value(denominator):
                raise ValueError("division requires a nonzero rational constant")
            zero = denominator.numerator_as_long()==0 if self.symbolic else denominator==0
            if zero:
                raise ValueError("division by zero")
            return values[0]/denominator
        if op == "add": return sum(values, self.number(0))
        if op == "sub": return values[0]-values[1]
        if op == "neg": return -values[0]
        if op == "mul":
            result=self.number(1)
            for v in values: result*=v
            return result
        if op == "abs":
            return z3.If(values[0]>=0,values[0],-values[0]) if self.symbolic else abs(values[0])
        if op in {"min","max"}:
            result=values[0]
            for v in values[1:]:
                result=z3.If(result<=v if op=="min" else result>=v,result,v) if self.symbolic else (min(result,v) if op=="min" else max(result,v))
            return result
        if op == "kth_largest":
            if not self.symbolic: return sorted(values,reverse=True)[rank-1]
            for _ in values:
                for i in range(len(values)-1):
                    a,b=values[i:i+2]
                    values[i],values[i+1]=z3.If(a>=b,a,b),z3.If(a>=b,b,a)
            return values[rank-1]
        raise ValueError("unhandled expression")


def build(parsed, witness=None):
    decoder = Expressions(parsed["variables"], witness)
    for row in parsed["definitions"]:
        decoder.env[row["label"]] = decoder.decode(row["expression"])
    assumptions = [decoder.decode(row["expression"]) for row in parsed["assumptions"]]
    conclusion = decoder.decode(parsed["conclusion"])
    if not all(decoder.boolean(v) for v in assumptions+[conclusion]):
        raise ValueError("assumptions and conclusion must be Boolean")
    return decoder, assumptions, conclusion


def check(parsed, timeout_ms=10000):
    started=time.monotonic()
    decoder, assumptions, conclusion=build(parsed)
    solver=z3.SolverFor("QF_LRA"); solver.set(timeout=timeout_ms)
    solver.add(*assumptions)
    consistent=solver.check()
    common={"operation":OPERATION,"semantics":"conditional_on_audited_encoding",
            "global_theorem_proved":False,"independently_checked_unsat_certificate":False}
    if consistent != z3.sat:
        return {**common,"verdict":"INCONSISTENT_PREMISES" if consistent==z3.unsat else "INCONCLUSIVE",
                "usable_evidence":False,"reason":str(consistent)}
    solver.add(z3.Not(conclusion))
    outcome=solver.check()
    if outcome==z3.sat:
        model=solver.model()
        witness={}
        for name in parsed["variables"]:
            value=model.eval(decoder.env[name],model_completion=True)
            if not z3.is_rational_value(value): raise ValueError("nonrational LRA witness")
            witness[name]=str(Fraction(value.numerator_as_long(),value.denominator_as_long()))
        replay, premises, goal=build(parsed,witness)
        if not all(premises) or goal is not False: raise ValueError("exact rational witness replay failed")
        return {**common,"verdict":"COUNTEREXAMPLE","usable_evidence":True,"witness":witness,
                "rational_replay_verified":True,"evaluated_definitions":{row["label"]:str(replay.env[row["label"]]) for row in parsed["definitions"]},
                "elapsed_seconds":round(time.monotonic()-started,3)}
    return {**common,"verdict":"LOCAL_IMPLICATION_HOLDS" if outcome==z3.unsat else "INCONCLUSIVE",
            "usable_evidence":outcome==z3.unsat,"solver_result":str(outcome),
            "elapsed_seconds":round(time.monotonic()-started,3)}
