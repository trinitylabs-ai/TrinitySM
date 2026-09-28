"""CPU-only diagnostic comparison on immutable saved division-tool requests.

Reuses existing Singular/Laurent implementations. No model calls, new assumptions,
proof rewriting, or automatic promotion. A reduced-target screen is not a proof
of the original formalization until its transformation certificate is replayed.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time

import sympy as sp

from . import rational_division as division
from . import gaussian_backend
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import integration

DEFAULT_ROUTES=("guarded_groebner","guarded_radical","laurent_singular")
ROUTES=(*DEFAULT_ROUTES,"laurent_guarded_radical")
DEFAULT_BINARY=Path(__file__).resolve().parents[1]/".tools/singular-4.2.1/root/usr/bin/Singular"


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,indent=2)+"\n")
    temporary.replace(path)


def guarded_membership_inputs(request):
    symbols,equations,target,guards=division.initial(request)
    # Preserve each authored polynomial. One Rabinowitsch equation encodes the
    # conjunction of its already-compiled nonzero guards, without new premises.
    names={str(symbol) for symbol in symbols}
    name="localization_inverse"
    while name in names:
        name+="_"
    auxiliary=sp.Symbol(name)
    label="localization_equation"
    while label in equations:
        label+="_"
    equations={**equations,label:1-auxiliary*sp.prod(guards)} if guards else equations
    return symbols+([auxiliary] if guards else []),list(equations.items()),target


def accepted_request(path):
    """Require parser and semantic acceptance bound to this exact saved request."""
    from . import division_experiment as experiment
    cycle=path.parents[2]
    sample=cycle.parents[1]
    final=cycle/"03_execution/03_final_semantic_audit"
    parser=json.loads((final/"parser.json").read_text())
    audit=json.loads((final/"result.json").read_text())
    if parser.get("decision")!="PASS" or audit.get("accepted") is not True or audit.get("decision")!="ACCEPT":
        raise ValueError("saved request lacks parser and semantic acceptance")
    text=(final/"input_formalization.md").read_text().strip()
    digest=experiment.pipeline.base.sha256_text(text)
    if parser.get("formalization_sha256")!=digest or audit.get("formalization_sha256")!=digest:
        raise ValueError("accepted draft binding changed")
    if not experiment.formal.parse_post_singular_audit((final/"audit.md").read_text().strip())["accepted"]:
        raise ValueError("saved semantic audit does not accept this draft")
    inputs={name:(sample/"input"/name).read_text().strip()
        for name in ("theorem.md","source_proof.md","detection.md","matcher.md")}
    ledger=json.loads((sample/"manifest.json").read_text()).get("domain_ledger_enabled",False)
    parsed=experiment.parse_proposal(text,domain_inputs=inputs,require_domain_ledger=ledger)
    request=json.loads(path.read_text())
    if not parsed["call_requested"] or {key:parsed[key] for key in ("arguments","guard_program")}!=request:
        raise ValueError("saved request differs from the accepted parsed draft")
    request_hash=division.exact_tools.stable_hash(request)
    if audit.get("request_sha256")!=request_hash:
        raise ValueError("accepted request binding changed")
    return request,{"parser":"PASS","semantic":"ACCEPT","auditor":audit.get("auditor"),
                    "formalization_sha256":digest,"request_sha256":request_hash}


def bound_preview(path,request):
    """Validate a persisted preview without claiming its mathematical lift."""
    preview=json.loads((path/"preview.json").read_text())
    expected={"source_arguments_sha256":division.exact_tools.stable_hash(request["arguments"]),
              "candidate_arguments_sha256":division.exact_tools.stable_hash(request["arguments"]),
              "guard_program_sha256":division.exact_tools.stable_hash(request["guard_program"])}
    if preview.get("state")!="structural_preview_unvalidated" or preview.get("promotable") is not False:
        raise ValueError("invalid saved preview state")
    if any(preview.get(key)!=value for key,value in expected.items()):
        raise ValueError("saved preview input binding changed")
    for name in ("laurent_transform.json","typed_guard_binding.json"):
        if hashlib.sha256((path/name).read_bytes()).hexdigest()!=preview["artifact_sha256"].get(name):
            raise ValueError("saved preview artifact binding changed")
    transform=json.loads((path/"laurent_transform.json").read_text())
    payload=dict(transform)
    digest=payload.pop("transform_sha256",None)
    if digest!=preview.get("transform_sha256") or digest!=division.exact_tools.stable_hash(payload):
        raise ValueError("saved transform binding changed")
    return preview,integration._decode_transform_payload(transform)


def guarded_radical_check(symbols,generators,target,guards,binary,timeout,memory):
    # Backend auxiliaries and coefficient names must never collide with inputs.
    aliases=[sp.Symbol(f"input_{i}") for i in range(len(symbols))]
    mapping=dict(zip(symbols,aliases,strict=True))
    return gaussian_backend.check(symbols=aliases,
        generators=[(label,expr.xreplace(mapping)) for label,expr in generators],
        target=target.xreplace(mapping),guards={label:expr.xreplace(mapping) for label,expr in guards.items()},
        binary=binary,timeout_sec=timeout,memory_mb=memory,radical=True)


def task(row,binary,timeout,memory):
    output=Path(row["output"])
    output.mkdir(parents=True,exist_ok=False)
    request=json.loads(Path(row["request_path"]).read_text())
    if division.exact_tools.stable_hash(request)!=row["request_sha256"]:
        raise ValueError("saved request changed after comparison was planned")
    write(output/"request.json",request)
    state={**row,"state":"running","model_calls":0,"promotable":False,"started":time.time()}
    write(output/"status.json",state)
    try:
        if row["route"]=="guarded_groebner":
            symbols,generators,target=guarded_membership_inputs(request)
            result=gaussian_backend.check(symbols=symbols,generators=generators,target=target,
                guards={},binary=binary,timeout_sec=timeout,memory_mb=memory,radical=False)
            write(output/"exact_result.json",result)
            state.update(status=result["status"],markers=result.get("markers",{}),
                         certificate_reexpanded=result.get("certificate_reexpanded",False),
                         scope="original_target_under_compiled_nonzero_guards")
        elif row["route"]=="guarded_radical":
            symbols,equations,target,guards=division.initial(request)
            result=guarded_radical_check(symbols,list(equations.items()),target,
                {f"guard_{i}":expr for i,expr in enumerate(guards)},binary,timeout,memory)
            write(output/"exact_result.json",result)
            state.update(status=result["status"],markers=result.get("markers",{}),
                         certificate_reexpanded=False,scope="guarded_radical_screen_only")
        elif row["route"] in ("laurent_singular","laurent_guarded_radical"):
            common=dict(source_arguments=request["arguments"],candidate_arguments=request["arguments"],
                        guard_program=request["guard_program"],timeout_sec=timeout,memory_mb=memory)
            cached=row.get("preview_path")
            if cached:
                preview_root=Path(cached)
                preview,_=bound_preview(preview_root,request)
            else:
                preview_root=output/"preview"
                preview=integration.bounded_preview_only(**common,output_dir=preview_root)
            state.update(preview_reused=bool(cached),preview_path=str(preview_root))
            write(output/"preview_result.json",preview)
            if preview.get("state")!="structural_preview_unvalidated":
                state.update(status=preview.get("state","NO_PREVIEW"),preview=preview)
            else:
                state.update(stage=row["route"]+"_target_screen",derived_profile=preview["derived_profile"])
                write(output/"status.json",state)
                if row["route"]=="laurent_guarded_radical":
                    bound,decoded=bound_preview(preview_root,request)
                    symbols,generators,target,guards=decoded
                    result=guarded_radical_check(symbols,generators,target,guards,binary,timeout,memory)
                    write(output/"exact_result.json",result)
                    state.update(status=result["status"],markers=result.get("markers",{}),
                        transformed_guard_count=len(guards),transform_sha256=bound["transform_sha256"],
                        certificate_reexpanded=False,source_consistency_checked=False,
                        scope="guarded_reduced_radical_screen_only_transform_lift_not_replayed")
                else:
                    result=integration.bounded_screen_persisted_preview_target(**common,
                        preview_output_dir=preview_root,output_dir=output/"screen",singular_binary=binary,
                        expected_transform_sha256=preview["transform_sha256"],
                        expected_derived_profile=preview["derived_profile"],
                        expected_structural_preview_sha256=hashlib.sha256((preview_root/"preview.json").read_bytes()).hexdigest())
                    write(output/"screen_result.json",result)
                    state.update(status=result.get("exact_status",result.get("state")),
                        certificate_reexpanded=result.get("membership_certificate_reexpanded",False),
                        scope="reduced_target_only_transform_lift_not_replayed")
        else:
            raise ValueError("unknown comparison route")
        state.update(state="completed")
    except Exception as error:
        state.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
    state.update(elapsed_seconds=round(time.time()-state["started"],3))
    write(output/"status.json",state)
    return state


def run(source,output,binary=DEFAULT_BINARY,timeout=600,memory=4096,workers=2,
        routes=DEFAULT_ROUTES,preview_source=None):
    source,output,binary=source.resolve(),output.resolve(),binary.resolve()
    if not binary.is_file() or not 1<=timeout<=600 or not 256<=memory<=8192 or not 1<=workers<=2:
        raise ValueError("invalid bounded backend comparison configuration")
    paths=sorted(source.glob("sample_*/cycles/cycle_*/03_execution/04_tool/request.json"))
    if not paths:
        raise ValueError("no saved tool requests")
    if not routes or len(set(routes))!=len(routes) or any(route not in ROUTES for route in routes):
        raise ValueError("invalid comparison routes")
    output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for path in paths:
        previous=json.loads(path.with_name("result.json").read_text())
        request,admission=accepted_request(path)
        if previous.get("verdict")!="INCONCLUSIVE":
            continue
        digest=division.exact_tools.stable_hash(request)
        if digest!=previous["certificate"]["request_sha256"]:
            raise ValueError("old division certificate binds a different request")
        identifier=path.parents[4].name+"_"+path.parents[2].name
        for route in routes:
            cached=(preview_source/identifier/"laurent_singular/preview") if preview_source else None
            if cached and (cached/"preview.json").is_file():
                bound_preview(cached,request)
            else:
                cached=None
            rows.append({"case":identifier,"route":route,"request_path":str(path),"request_sha256":digest,
                "admission":admission,"preview_path":str(cached.resolve()) if cached else None,
                "output":str(output/identifier/route),"state":"queued"})
    manifest={"source":str(source),"binary":str(binary),"timeout_per_step":timeout,"memory_mb_per_job":memory,
        "workers":workers,"model_calls":0,"mathematical_inputs_unchanged":True,"promotable":False,
        "routes":list(routes),"admission_requires":"parser_and_semantic_accept_same_request","jobs":rows}
    write(output/"manifest.json",manifest)
    write(output/"status.json",{**manifest,"state":"running","completed":0})
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(task,row,binary,timeout,memory):index for index,row in enumerate(rows)}
        for done,future in enumerate(as_completed(futures),1):
            index=futures[future]
            try:
                rows[index]=future.result()
            except Exception as error:
                rows[index]={**rows[index],"state":"failed_closed","error":str(error)}
            write(output/"status.json",{**manifest,"jobs":rows,"state":"running" if done<len(rows) else "completed","completed":done})
    return json.loads((output/"status.json").read_text())


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--timeout",type=int,default=600)
    parser.add_argument("--routes",nargs="+",choices=ROUTES,default=DEFAULT_ROUTES)
    parser.add_argument("--preview-source",type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.source,args.output,timeout=args.timeout,routes=args.routes,
        preview_source=args.preview_source)),flush=True)
