"""Bounded, read-only diagnostics for model-authored Markdown formalizations.

This is not a second acceptance parser: the existing parser alone decides PASS.
No draft, AST, quotation, mathematical premise, or tool decision is repaired here.
"""
from __future__ import annotations

import hashlib
import re

from .division_experiment import formal

VERSION = "located_parser_feedback_v1"
MAX_ISSUES = 12
MAX_FEEDBACK_CHARACTERS = 6000
MAX_SCAN_CHARACTERS = 100000


def compact(text, limit=160):
    text=" ".join(str(text).split())
    return text if len(text)<=limit else text[:limit-3]+"..."


def diagnose(draft, error, *, inputs=None):
    """Collect independent syntax/source-copy errors without changing the draft."""
    rows=[]
    section="Document"
    fence=None
    sections={}
    for number,line in enumerate(draft[:MAX_SCAN_CHARACTERS].splitlines(),1):
        if line.startswith("```"):
            fence=None if fence is not None else line[3:].strip()
        if fence is None and line.startswith("# "):
            section=line[2:].strip()
        else:
            rows.append((number,section,line))
            sections.setdefault(section,[]).append((number,line))
    issues=[]
    total=0
    def add(number,field,code,offending,expected):
        nonlocal total
        total+=1
        if len(issues)<MAX_ISSUES:
            issues.append({"line":number,"field":compact(field,80),"code":code,
                           "offending":compact(offending),"expected":compact(expected,300)})

    symbol_rows=[(n,line.partition("=")[2].strip()) for n,sec,line in rows
                 if sec=="Tool Arguments" and re.match(r"symbols\s*=",line)]
    symbols=set()
    if len(symbol_rows)==1:
        number,value=symbol_rows[0]
        try:
            symbols=set(formal.mdp.parse_symbol_list(value))
        except ValueError as failure:
            add(number,"Tool Arguments / symbols","symbol_list",value,
                str(failure)+". Use bare identifiers separated by commas; no brackets, quotes or math delimiters. Preserve the intended symbol names.")

    def expression(number,field,value):
        try:
            node=formal.mdp.parse_sexpr(value)
            node=formal.protocol._normalize_expression_leaves(node,symbols,
                {"declared_symbol_leaves":0,"typed_integer_literals":0})
            formal.mdp.expression_ast(node)
        except (ValueError,RecursionError) as failure:
            message=str(failure)
            # A declared variable in operator position has one unambiguous typed
            # spelling. Suggest that spelling, never apply it to the candidate.
            match=re.search(r"unsupported expression form '([A-Za-z_][A-Za-z0-9_]*)' with arity 0",message)
            if match and match[1] in symbols and match[1] not in formal.protocol.EXPRESSION_HEADS:
                name=match[1]
                add(number,field,"symbol_as_call",f"({name})",
                    f"Use (symbol {name}), not ({name}). {name} is a declared variable, not an operator. Correct this spelling wherever it occurs; preserve every mathematical operation.")
                return
            balance=value.count("(")-value.count(")")
            if any(term in message for term in ("trailing expression tokens","closing parenthesis","unclosed expression")):
                depth=0
                offset=None
                for pos,char in enumerate(value):
                    depth+=(char=="(")-(char==")")
                    if depth<0:
                        offset=pos
                        break
                fragment=value[-150:] if offset is None else value[max(0,offset-65):offset]+" <<unexpected )>> "+value[offset+1:offset+65]
                add(number,field,"parentheses",fragment,
                    f"{message}; net opening-minus-closing count is {balance}. Supply exactly one balanced expression. Recheck grouping against your intended formula; do not discard operands or guess a new operator.")
            else:
                add(number,field,"expression_syntax",value,
                    message+". Grammar: (symbol name), integer, (rational p q), (sub left right), (neg expr), (pow expr nonnegative_integer); add/mul need at least two operands. Preserve the intended formula.")

    for number,sec,line in rows:
        if sec=="Domain Ledger" and line.strip() and line.strip()!="NONE":
            parts=line[2:].split(" :: ") if line.startswith("- ") else []
            if len(parts)!=6 or not all(parts):
                add(number,sec,"ledger_fields",line,
                    "Use six nonempty fields: - label :: KIND :: expression :: theorem or proof :: exact source excerpt :: justification.")
                continue
            label,kind,value,source,excerpt,_reason=parts
            field=f"Domain Ledger / {label}"
            source_file={"theorem":"theorem.md","proof":"source_proof.md"}.get(source)
            if source_file and inputs is not None and source_file in inputs:
                if " ".join(excerpt.split()) not in " ".join(inputs[source_file].split()):
                    add(number,field+" / excerpt","source_excerpt",excerpt,
                        f"Not a verbatim substring of Original {'Theorem' if source=='theorem' else 'Proof'}. Copy from that source preserving LaTeX spelling; no added quotation marks. Put derived claims in justification, not the quotation. No replacement source is selected for you.")
            if kind!="RETAINED":
                expression(number,field+" / expression",value)
        elif sec=="Tool Arguments":
            match=re.match(r"(generator|target)\s*=\s*(.*)$",line)
            if match:
                kind,value=match.groups()
                label,value=value.split(" :: ",1) if " :: " in value else (kind,value)
                expression(number,f"Tool Arguments / {kind} {label}",value)
        elif sec=="Guard Program":
            match=re.match(r"(provenance_division|source_nonzero)\s*=\s*(.*)$",line)
            if match:
                kind,value=match.groups()
                parts=value.split(" :: ")
                count=3 if kind=="provenance_division" else 2
                if len(parts)!=count:
                    add(number,sec,"guard_fields",line,"provenance_division = label :: numerator :: denominator; source_nonzero = label :: expression.")
                else:
                    for index,value in enumerate(parts[1:],1):
                        expression(number,f"Guard Program / {parts[0]} / expression {index}",value)
    for sec,language in (("Guard Program","guard-args"),("Tool Arguments","tool-args")):
        entries=sections.get(sec,[])
        body="\n".join(line for _,line in entries).strip()
        if not body or (sec=="Guard Program" and body=="NONE"):
            continue
        try:
            formal.mdp.fenced_body(f"# {sec}\n\n{body}",language,sec)
        except ValueError:
            add(entries[0][0],sec,"fence",body,
                f"Wrap the existing lines in exactly one fence opened with ```{language} and closed with ```. Do not omit existing guards to avoid the error.")
    feedback=["Parser rejected this exact draft. No semantic audit has run.",
              "First parser error: "+compact(error,650),
              "Located diagnostics (line numbers refer to the Saved Draft, not this prompt):"]
    for row in issues:
        entry=f"- Line {row['line']}, {row['field']}: {row['code']}. Found: {row['offending']}. Expected/action: {row['expected']}"
        if len("\n".join(feedback))+len(entry)>MAX_FEEDBACK_CHARACTERS-350:
            break
        feedback.append(entry)
    if not issues:
        feedback.append("No additional independent location could be established. Follow the original section/field contract and the first parser error; no replacement mathematical input is inferred.")
    if total>len(feedback)-3 or len(draft)>MAX_SCAN_CHARACTERS:
        feedback.append("Diagnostics are bounded and incomplete; additional errors may remain.")
    feedback.append("These are syntax/source-copy diagnostics only, not mathematical acceptance. Return the full corrected Markdown; preserve unaffected mathematics. The strict parser and a fresh semantic audit still decide eligibility.")
    return {"version":VERSION,"draft_sha256":hashlib.sha256(draft.encode()).hexdigest(),
            "first_error":str(error),"issues":issues,"issues_found":total,
            "read_only":True,"feedback":"\n".join(feedback)}
