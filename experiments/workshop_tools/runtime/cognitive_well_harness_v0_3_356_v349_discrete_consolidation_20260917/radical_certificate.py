"""Generic, expansion-checked Rabinowitsch certificates over QQ(i).

A screen is never a certificate. The exported identity is
1 = sum(a_j*f_j) + b*(1-u*G) + c*(1-v*T), with G the guard product.
Substituting u=1/G and, by contradiction, v=1/T proves T=0.
"""
from __future__ import annotations

import hashlib

import sympy as sp

from . import backend_comparison as backends
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import laurent_elimination as laurent
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames


def system_payload(symbols,generators,target,guards):
    return {"symbols":[str(s) for s in symbols],
        "generators":{label:laurent._payload(value,symbols) for label,value in generators},
        "target":laurent._payload(target,symbols),
        "guards":{label:laurent._payload(value,symbols) for label,value in guards.items()}}


def augmented(system):
    symbols,generators,target,guards=backends.integration._decode_transform_payload(system)
    if any(value==0 for value in guards.values()):
        raise ValueError("zero cannot be a nonzero guard")
    namespace=FreshNames(symbols)
    u,v=namespace.take("guard_inverse"),namespace.take("target_inverse")
    equations=[value for _,value in generators]+[1-u*sp.prod(guards.values()),1-v*target]
    return symbols+[u,v],equations


def replay(system,certificate):
    if certificate.get("schema")!="guarded_radical_identity_v1":
        raise ValueError("unsupported radical certificate")
    if certificate.get("system_sha256")!=backends.division.exact_tools.stable_hash(system):
        raise ValueError("radical certificate input binding changed")
    symbols,equations=augmented(system)
    if certificate.get("symbols")!=[str(s) for s in symbols]:
        raise ValueError("radical certificate symbol order changed")
    payloads=certificate.get("multipliers",[])
    if len(payloads)!=len(equations):
        raise ValueError("radical certificate multiplier count changed")
    multipliers=[payload_polynomial(payload,symbols) for payload in payloads]
    identity=sp.Poly(-1,*symbols,domain=sp.QQ_I)
    for multiplier,equation in zip(multipliers,equations,strict=True):
        identity += multiplier * sp.Poly(equation,*symbols,domain=sp.QQ_I)
    if not identity.is_zero:
        raise ValueError("radical certificate failed exact re-expansion")
    return {"verified":True,"system_sha256":certificate["system_sha256"],
        "certificate_sha256":backends.division.exact_tools.stable_hash(certificate),
        "identity":"one_equals_source_and_inverse_equation_combination",
        "conditional_target_proved":True}


def payload_polynomial(payload,symbols):
    """Decode a sparse witness directly into exact QQ(i) polynomial arithmetic."""
    terms={}
    for row in payload["terms"]:
        powers=tuple(row["powers"])
        if len(powers)!=len(symbols) or any(type(power) is not int or power<0 for power in powers):
            raise ValueError("invalid saved polynomial powers")
        coefficient=row["coefficient"]
        value=(sp.Rational(coefficient["real_numerator"],coefficient["real_denominator"])
               +sp.I*sp.Rational(coefficient["imaginary_numerator"],coefficient["imaginary_denominator"]))
        terms[powers]=terms.get(powers,0)+value
    return sp.Poly.from_dict(terms,symbols,domain=sp.QQ_I)


def coefficient_table(payload,symbols,label,*,imaginary_unit="i"):
    """Print every coefficient/exponent; only a common monomial is extracted."""
    polynomial=payload_polynomial(payload,symbols)
    if polynomial.is_zero:
        return f"\\[{sp.latex(label)}=0.\\]"
    terms=polynomial.terms()
    minima=[min(powers[j] for powers,_ in terms) for j in range(len(symbols))]
    active=[j for j in range(len(symbols)) if any(powers[j]!=minima[j] for powers,_ in terms)]
    monomial=sp.prod(symbol**power for symbol,power in zip(symbols,minima,strict=True))
    rows=[]
    for powers,value in terms:
        real,imaginary=sp.expand(value).as_real_imag()
        rows.append(f"{real},{imaginary}|"+",".join(str(powers[j]-minima[j]) for j in active))
    # Independently parse the actual printed rows, including omitted constant
    # exponent columns, and compare to the saved multiplier exactly.
    recovered={}
    for row in rows:
        coefficient,powers=row.split("|")
        real,imaginary=map(sp.Rational,coefficient.split(","))
        offsets=list(map(int,powers.split(","))) if powers else []
        if len(offsets)!=len(active):
            raise ValueError("coefficient table arity changed")
        expanded=list(minima)
        for j,power in zip(active,offsets,strict=True):
            expanded[j]+=power
        recovered[tuple(expanded)]=real+sp.I*imaginary
    if sp.Poly.from_dict(recovered,symbols,domain=sp.QQ_I)!=polynomial:
        raise ValueError("coefficient table changed a saved multiplier")
    variables=", ".join(sp.latex(symbols[j]) for j in active) or "no variables"
    return (f"For \\({sp.latex(label)}\\), multiply the polynomial specified by the following table by "
            f"\\({sp.latex(monomial)}\\). The exponent columns, in order, are \\({variables}\\). "
            f"Each row `a,b|e1,...,ek` denotes coefficient \\(a+b{imaginary_unit}\\) times "
            "the product of those variables to the displayed exponents. Sum all rows; an empty "
            "exponent list denotes 1. All entries are exact rational numbers.\n\n```text\n"
            +"\n".join(rows)+"\n```")


def export(system,output,*,binary=backends.DEFAULT_BINARY,timeout=600,memory=4096):
    output.mkdir(parents=True,exist_ok=False)
    backends.write(output/"system.json",system)
    symbols,equations=augmented(system)
    program,aliases=backends.gaussian_backend._ordinary_program(symbols=symbols,
        generators=[(f"equation_{i}",value) for i,value in enumerate(equations)],target=sp.Integer(1))
    result=backends.gaussian_backend._run(program,binary,timeout,memory_mb=memory)
    result.update(program=program,program_sha256=hashlib.sha256(program.encode()).hexdigest(),
                  output_sha256=hashlib.sha256(result["output"].encode()).hexdigest())
    backends.write(output/"backend.json",result)
    markers=result.get("markers",{})
    if result["status"]=="TIMEOUT":
        return {"state":"certificate_timeout","verified":False}
    if result["status"]!="COMPLETED" or markers.get("RESULT_DONE")!="1":
        raise ValueError("radical certificate backend failed; inspect backend.json")
    if markers.get("RESULT_ORDINARY")!="PROVED":
        return {"state":"certificate_not_proved","verified":False}
    # The augmented ideal MUST be the unit ideal. Unlike an ordinary source
    # membership check, that is the desired contradiction, not an error.
    multipliers=[backends.gaussian_backend._parse_backend_polynomial(
        markers[f"RESULT_MULTIPLIER_{i}"],symbols,aliases) for i in range(1,len(equations)+1)]
    certificate={"schema":"guarded_radical_identity_v1",
        "system_sha256":backends.division.exact_tools.stable_hash(system),
        "symbols":[str(s) for s in symbols],
        "multipliers":[laurent._payload(value,symbols) for value in multipliers]}
    verification=replay(system,certificate)
    backends.write(output/"certificate.json",certificate)
    backends.write(output/"verification.json",verification)
    return {"state":"verified",**verification}


def consistency(system,*,binary=backends.DEFAULT_BINARY,timeout=600,memory=4096):
    symbols,generators,_,guards=backends.integration._decode_transform_payload(system)
    result=backends.guarded_radical_check(symbols,generators,sp.Integer(1),guards,binary,timeout,memory)
    marker=result.get("markers",{}).get("RESULT_RADICAL")
    return {"checked":result["status"]=="COMPLETED" and marker in {"PROVED","NOT_PROVED"},
        "consistent":result["status"]=="COMPLETED" and marker=="NOT_PROVED","backend":result}


def render(system,certificate,*,namespace=None,target_label=None,source_labels=None,imaginary_unit="i",
           factor_first=False,table_multipliers=False):
    if table_multipliers and factor_first:
        raise ValueError("coefficient tables do not use polynomial factorization")
    verification=replay(system,certificate)
    source_symbols,generators,target,guards=backends.integration._decode_transform_payload(system)
    symbols,equations=augmented(system)
    from .saved_witness import _compact,_decode
    namespace=namespace or FreshNames(symbols)
    source_labels=source_labels or [namespace.take(f"E_{i}") for i in range(1,len(generators)+1)]
    target_label=target_label if target_label is not None else namespace.take("T")
    # A surrounding Laurent proof can already use the backend's auxiliary
    # names. Rename only the display variables, leaving the witness unchanged.
    u,v=namespace.take("guard_inverse"),namespace.take("target_inverse")
    renaming=dict(zip(symbols[-2:],[u,v],strict=True))
    display_symbols=symbols[:-2]+[u,v]
    equations=[value.xreplace(renaming) for value in equations]
    latex=lambda value: sp.latex(value,imaginary_unit=imaginary_unit)
    multiplier_labels=[namespace.take(f"A_{i}") for i in range(1,len(equations)+1)]
    if table_multipliers:
        definitions,compact=[],[]
    else:
        values=[_decode(payload,symbols).xreplace(renaming) for payload in certificate["multipliers"]]
        definitions,compact=_compact(values,display_symbols,namespace=namespace,factor_first=factor_first)
    lines=["## Algebraic lemma","Assume the following polynomial equations and nonzero conditions:"]
    lines.extend(f"\\[{latex(label)}={latex(value)}=0.\\]" for label,(_,value) in zip(source_labels,generators,strict=True))
    lines.extend(f"\\[{latex(value)}\\ne0.\\]" for value in guards.values())
    lines.append(f"We prove \\({latex(target_label)}={latex(target)}=0\\).")
    lines.append("Work over the complex numbers. Suppose, for a contradiction, that the target is nonzero, and define")
    lines.append(f"\\[{latex(u)}=1/({latex(sp.prod(guards.values()))}),\\qquad {latex(v)}=1/({latex(target)}).\\]")
    lines.append("These inverses exist under the displayed assumptions. Use these ordered polynomial abbreviations:")
    lines.extend(f"\\[{latex(label)}={latex(value)}.\\]" for label,value in definitions)
    if not table_multipliers:
        lines.extend(f"\\[{latex(label)}={latex(value)}.\\]" for label,value in zip(multiplier_labels,compact,strict=True))
    if table_multipliers:
        lines.extend(coefficient_table(payload,display_symbols,label,imaginary_unit=imaginary_unit)
            for payload,label in zip(certificate["multipliers"],multiplier_labels,strict=True))
    summands=[m*g for m,g in zip(multiplier_labels[:len(source_labels)],source_labels,strict=True)]
    summands.extend([multiplier_labels[-2]*equations[-2],multiplier_labels[-1]*equations[-1]])
    lines.append("Exact expansion gives the following identity. Each summand vanishes under the assumptions:")
    lines.append(f"\\[1={latex(sp.Add(*summands,evaluate=False))}=0.\\]")
    lines.append(f"This contradiction proves \\({latex(target_label)}=0\\).")
    markdown="\n\n".join(lines)
    if len(markdown)>(160_000 if table_multipliers else 120_000):
        raise ValueError("radical certificate exceeds the fixed presentation budget")
    return markdown,{**verification,"target_label_latex":latex(target_label),
                     "factor_first":factor_first,
                     "table_multipliers":table_multipliers,
                     "coefficient_tables_reparsed":table_multipliers,
                     "horner_and_cse_reexpanded":not table_multipliers,"abbreviation_count":len(definitions),
                     "markdown_characters":len(markdown),
                     "markdown_sha256":hashlib.sha256(markdown.encode()).hexdigest()}
