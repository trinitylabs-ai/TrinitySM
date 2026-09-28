"""Saved brief + resulting proof -> model-authored local evidence -> rewrite.

The experiment contains no reference answers, operator-supplied witnesses, or
problem-specific mathematical rules. All model outputs are Markdown.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import traceback

from . import certificate, linear_evidence as linear, rewrite
from .composite_identity import cpu_slice
from .trig_formalization import source_bound_excerpt
from cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 import exact_evidence as legacy

base = rewrite.pipeline.base
write = rewrite.write_record
mdp = legacy.mdp
OPERATIONS = (linear.OPERATION, "expand_and_compare", "enumerate_finite_assignments")
INPUT_LABELS = (("theorem.md", "Original Problem"), ("original_proof.md", "Original Proof"),
                ("repair_brief.md", "Fusion Repair Brief (untrusted proposal)"),
                ("resulting_proof.md", "Resulting Proof (untrusted submission)"))
FORMAL_CHECKS = ("Source correspondence", "Premise justification", "Domain and legal cases",
                 "Conclusion and quantifier scope", "Tool fit", "Material relevance")
PROOF_CHECKS = ("Original task answered", "Tool evidence used within scope", "Source-to-tool connection justified",
                "Flagged defect resolved", "No new unsupported claims", "All proof steps correct")
SYSTEM = """You select and formalize one useful local tool check from a repair
brief or a resulting proof. All supplied analyses and proposed repairs are
untrusted. You—not the operator—choose the claim, operation, and mathematical
input. Do not assume any claimed answer is true. A check should materially test
a load-bearing claim, not merely repeat a definition. Encode domain restrictions,
legal cases, and quantifiers faithfully. You may test a concrete instance of a
universal claim to refute it; explain the specialization. A success on instances
cannot prove the general claim. Do not turn an infinite search into a finite
proof. Do not invent a target premise, additional hypothesis, or tool result.
No JSON or executable code. Emit exactly these Markdown sections:
# Decision
CALL_TOOL
# Operation
one offered operation
# Claim
The precise source claim to test, including whether this is a specialized case.
# Source
repair_brief or resulting_proof
# Source Excerpt
A short verbatim excerpt locating the claim in that source.
# Semantic Bindings
Use these six labeled Markdown bullets, explaining every symbol and premise:
- Source basis: Source connection and justification of the assumptions.
- Target meaning: The exact conclusion and its quantifier scope.
- Domain and branch conditions: All legal cases and domain restrictions.
- Compression map: Symbol meanings and transformations, or NONE if unused.
- Sufficiency argument: What each possible tool outcome establishes.
- Rewrite consequence: What the result would and would not change in the proof.
# Tool Arguments
The selected operation's Markdown arguments, following its contract.
Alternatively emit only # Decision with NO_TOOL and # Reason with an explanation.
"""
AUDIT_SYSTEM = """Independently check the model's proposed local computation
against the original problem, original proof, repair brief, and resulting proof.
Source assertions and other model explanations are not trusted. Check legal
inputs and every premise, source correspondence, specialized parameters,
quantifiers, and the consequence for the stated source claim. A concrete legal
counterexample may refute a universal claim; no counterexample within a restricted
encoding does not establish a larger claim. Do not substitute your own missing
premises or regard your repairs as part of the submitted request. No calculation
outcome is supplied. Return the required Markdown audit; do not rewrite the input.
"""
REWRITE_SYSTEM = """Improve the supplied repair brief and resulting proof using
the checked local tool evidence. The original problem is authoritative; both
proofs and the old repair brief are untrusted. Independently derive the needed
mathematics. Preserve correct parts and address the evidenced defect and its
dependencies. Show the connection from the original problem to the tool input
and derive the conclusion at exactly its established scope. A counterexample
refutes the tested claim, not the entire theorem; a local implication is not a
general solution. Do not treat a proposed formula as a required answer. Do not
hide remaining gaps behind a tool verdict. Write a self-contained human-readable
proof, with no artifact paths or opaque certificate references. Return Markdown:
# Outcome
REWRITTEN_PROOF or RESOLUTION_FAILED
# Repair Brief
A concise corrected advisory brief, at most 6000 characters.
# Proof
The complete rewritten proof. If unresolved, honestly explain the remaining gap
and return RESOLUTION_FAILED. No JSON or executable code.
"""


def context(inputs):
    return "\n\n".join(f"# {label}\n\n{inputs[name]}" for name,label in INPUT_LABELS)


def contracts():
    return (f"# Available Tools\n\n- {linear.OPERATION}: exact piecewise-linear real implication or counterexample check.\n"
            + legacy.v274.operation_catalog(OPERATIONS[1:])
            + f"\n\n## {linear.OPERATION}\n\n" + linear.CONTRACT
            + "\n\n" + "\n\n".join(f"## {op}\n\n{legacy.v274.compiler_contract(op)}" for op in OPERATIONS[1:]))


def parse_proposal(text, inputs):
    if len(text) > 60000:
        raise ValueError("proposal exceeds 60000 characters")
    headings = ["Decision","Operation","Claim","Source","Source Excerpt","Semantic Bindings","Tool Arguments"]
    if [s for s in text.splitlines() if s.startswith("# ")] == ["# Decision", "# Reason"]:
        sections=mdp.exact_sections(text,["Decision","Reason"])
        if sections["Decision"]!="NO_TOOL" or not sections["Reason"]: raise ValueError("invalid NO_TOOL")
        return {"call_requested":False,"reason":sections["Reason"]}
    sections=mdp.exact_sections(text,headings)
    if sections["Decision"]!="CALL_TOOL" or sections["Operation"] not in OPERATIONS:
        raise ValueError("invalid tool decision or operation")
    source=sections["Source"]
    if source not in {"repair_brief","resulting_proof"}:
        raise ValueError("Source must be repair_brief or resulting_proof")
    if not sections["Claim"] or not sections["Semantic Bindings"] or len(sections["Source Excerpt"])>1024:
        raise ValueError("nonempty claim/bindings and short source excerpt required")
    excerpt=source_bound_excerpt(sections["Source Excerpt"],inputs[source+".md"])
    if excerpt is None: raise ValueError("Source Excerpt not found in selected source")
    op=sections["Operation"]
    normalization=[]
    canonical=sections["Tool Arguments"]
    if op==linear.OPERATION:
        canonical,normalization=linear.normalize(canonical)
        args=linear.parse(canonical)
    else:
        args=legacy._parse_compilation(
            "# Semantic Bindings\n\n"+sections["Semantic Bindings"]+"\n\n# Tool Arguments\n\n"+canonical,op)["arguments"]
    return {"call_requested":True,"operation":op,"claim":sections["Claim"],"source":source,
            "source_excerpt":excerpt,"semantic_bindings":sections["Semantic Bindings"],"arguments":args,
            "canonical_tool_arguments":canonical,"deterministic_normalization":normalization}


def inspect(text,inputs):
    try:
        with cpu_slice(20): parsed=parse_proposal(text,inputs)
        return {"parser_valid":True,"proposal":parsed,"feedback":"Syntax/types/source excerpt passed; semantics not certified."}
    except (ValueError,TimeoutError) as error:
        return {"parser_valid":False,"feedback":f"{type(error).__name__}: {error}"}


def audit_contract(checks):
    return "\n\nReturn exactly:\n\n# Decision\n\nACCEPT or REJECT\n\n# Checks\n\n"+"\n".join(f"- {s}: PASS or FAIL" for s in checks)+"\n\n# Issues\n\nNONE, or one-line Markdown bullets. ACCEPT requires all PASS and no issues."


def parse_audit(text,checks):
    sections=mdp.exact_sections(text,["Decision","Checks","Issues"])
    if sections["Decision"] not in {"ACCEPT","REJECT"}: raise ValueError("invalid audit decision")
    lines=sections["Checks"].splitlines()
    if len(lines)!=len(checks): raise ValueError("incorrect audit check count")
    values={}
    for label,line in zip(checks,lines,strict=True):
        prefix=f"- {label}: "
        if not line.startswith(prefix) or line[len(prefix):] not in {"PASS","FAIL"}:
            raise ValueError("malformed audit check: "+label)
        values[label]=line[len(prefix):]=="PASS"
    issues=[] if sections["Issues"]=="NONE" else mdp.parse_prefixed_list(sections["Issues"])
    accepted=all(values.values()) and not issues
    if (sections["Decision"]=="ACCEPT")!=accepted: raise ValueError("audit decision disagrees with checks/issues")
    return {"decision":sections["Decision"],"accepted":accepted,"checks":values,"issues":issues}


def parse_rewrite(text):
    sections=mdp.exact_sections(text,["Outcome","Repair Brief","Proof"])
    if sections["Outcome"] not in {"REWRITTEN_PROOF","RESOLUTION_FAILED"}:
        raise ValueError("invalid rewrite outcome")
    if not sections["Repair Brief"] or not sections["Proof"] or len(sections["Repair Brief"])>6000 or len(text)>66000:
        raise ValueError("rewrite needs a concise brief and nonempty proof/explanation")
    return {"outcome":sections["Outcome"],"repair_brief":sections["Repair Brief"],"proof":sections["Proof"]}


def linear_report(parsed,result):
    lines=["# Local Tool Evidence",f"Verdict: {result['verdict']}","Claim: "+parsed["claim"],
           "Scope: only the supplied formal implication; no general theorem is certified.",
           "Solver UNSAT results do not include an independently checked proof certificate."]
    for label,value in result.get("witness",{}).items(): lines.append(f"- Witness {label} = {value}")
    for label,value in result.get("evaluated_definitions",{}).items(): lines.append(f"- Evaluated {label} = {value}")
    if result.get("rational_replay_verified"): lines.append("Every premise is true and the conclusion false under independent Fraction arithmetic replay.")
    return "\n\n".join(lines)


def normalized_context(parsed):
    return "\n\n# Deterministically Normalized Tool Arguments\n\n"+parsed["canonical_tool_arguments"]+"\n\nOnly presentation aliases and exact numeric spelling may differ; assumptions and comparisons are unchanged."


def finish_rewrite(call,rewriter,gemma,rewrite_input,output,status):
    rewritten,parts=call(rewriter,REWRITE_SYSTEM,rewrite_input,output/"rewrite","local_evidence_proof_rewrite",parse_rewrite,1000)
    base.write_text(output/"rewritten_repair_brief.md",parts["repair_brief"])
    status["rewrite_outcome"]=parts["outcome"]
    if parts["outcome"]=="RESOLUTION_FAILED":
        base.write_text(output/"unresolved.md",parts["proof"])
        status.update(state="completed",stage="rewrite_unresolved")
        return
    base.write_text(output/"rewritten_proof.md",parts["proof"])
    status.update(stage="rewritten_proof_audit");write(output/"status.json",status)
    final_audit,final=call(gemma,"Audit the rewritten proof as submitted. Check the original task, the evidenced defect, and all new mathematics independently. A correct local tool result does not certify the whole proof. Do not fill omitted gaps. Return only the required Markdown audit.",
        rewrite_input+"\n\n# New Repair Brief and Rewritten Proof\n\n"+rewritten+audit_contract(PROOF_CHECKS),
        output/"proof_auditor","local_evidence_rewritten_proof_audit",lambda t:parse_audit(t,PROOF_CHECKS),1001)
    base.write_text(output/"proof_audit.md",final_audit);write(output/"proof_audit.json",final)
    status.update(state="completed",stage="rewritten_proof_audited",proof_audit=final["decision"],
                  strict_score="NOT_RUN",whole_proof_independently_certified=False)


def execute_tool(parsed, destination, inputs):
    destination.mkdir(parents=True,exist_ok=False)
    write(destination/"request.json",parsed)
    if parsed["operation"]==linear.OPERATION:
        with cpu_slice(30): result=linear.check(parsed["arguments"])
        report=linear_report(parsed,result)
    else:
        problem_path=destination/"problem.bound.md"
        base.write_text(problem_path,inputs["theorem.md"])
        problem=legacy.v0220.Problem(problem_id="generic_local_evidence",statement=inputs["theorem.md"],source_path=problem_path)
        with cpu_slice(30):
            event=legacy.exact_tools.execute(operation=parsed["operation"],arguments=parsed["arguments"],
                claim=parsed["claim"],problem=problem,run_id=destination.name,certificate_cache_dir=None)
            verification=legacy.exact_tools.verify_target_evidence_event(event,full_legacy_replay=True)
        result={"verdict":event.get("verdict",event.get("status")),"usable_evidence":True,"event":event,"verification":verification}
        report=legacy.exact_tools.render_event(event)
    result["request_sha256"]=legacy.stable_hash(parsed)
    write(destination/"result.json",result)
    base.write_text(destination/"evidence.md",report)
    return result,report


def load_evidence(source):
    """Rebind a saved audited rational witness; do not rerun a model or solver."""
    manifest=json.loads((source/"manifest.json").read_text())
    source_status=json.loads((source/"status.json").read_text())
    cycle=source_status.get("selected_cycle")
    if not isinstance(cycle,int) or cycle<1: raise ValueError("no selected tool evidence")
    inputs={name:(source/"input"/name).read_text().strip() for name,_ in INPUT_LABELS}
    if any(base.sha256_text(value)!=manifest["input_sha256"][name] for name,value in inputs.items()):
        raise ValueError("saved input hashes changed")
    root=source/"cycles"/f"cycle_{cycle:02d}"
    text=(root/"formalization.md").read_text().strip()
    audit=(root/"audit.md").read_text().strip()
    for sub,stage,markdown in (("formalizer","local_evidence_formalization",text),("auditor","local_evidence_semantic_audit",audit)):
        certificate.validate_markdown_budget_forcing(json.loads((root/sub/"call.json").read_text()),
            expected_stage=stage,expected_model=base.DEFAULT_GEMMA_MODEL,canonical_markdown=markdown,
            expected_timeout_sec=manifest.get("request_timeout_sec",600))
    parsed=parse_proposal(text,inputs)
    decision=parse_audit(audit,FORMAL_CHECKS)
    if not decision["accepted"] or decision!=json.loads((root/"audit.json").read_text()):
        raise ValueError("saved semantic audit not accepted or changed")
    admission=json.loads((root/"admission.json").read_text())
    if admission!={"parser":"PASS","semantic":"ACCEPT","formalization_sha256":base.sha256_text(text),
                   "audit_sha256":base.sha256_text(audit),"request_sha256":legacy.stable_hash(parsed)}:
        raise ValueError("saved admission binding changed")
    if any(parsed!=json.loads((root/name).read_text()) for name in ("request.json","tool/request.json")):
        raise ValueError("saved tool request changed")
    result=json.loads((root/"tool/result.json").read_text())
    if (parsed["operation"]!=linear.OPERATION or result.get("operation")!=linear.OPERATION
            or result.get("verdict")!="COUNTEREXAMPLE" or result.get("rational_replay_verified") is not True
            or result.get("usable_evidence") is not True or result.get("request_sha256")!=legacy.stable_hash(parsed)
            or result.get("global_theorem_proved") is not False):
        raise ValueError("rewrite-only reuse requires a checked rational counterexample")
    with cpu_slice(20):
        replay,premises,conclusion=linear.build(parsed["arguments"],result["witness"])
    derived={row["label"]:str(replay.env[row["label"]]) for row in parsed["arguments"]["definitions"]}
    if not all(premises) or conclusion is not False or derived!=result["evaluated_definitions"]:
        raise ValueError("saved rational witness replay failed")
    report=linear_report(parsed,result)
    if report.strip()!=(root/"tool/evidence.md").read_text().strip():
        raise ValueError("saved tool report changed")
    prompt=context(inputs)+"\n\n# Audited Local Tool Request\n\n"+text+normalized_context(parsed)+"\n\n"+report
    old_prompt=source/"rewrite/model/attempt_01_cap_32768/local_evidence_proof_rewrite.user_prompt.txt"
    if old_prompt.is_file() and old_prompt.read_text().strip()!=prompt.strip():
        raise ValueError("rewrite prompt differs from original evidence-driven request")
    return inputs,root,prompt


def rewrite_from_evidence(source,output,seed,*,rewriter_name="gemma",request_timeout_sec=900,caller=None):
    rewrite.assert_generic_boundary()
    if rewriter_name not in {"gemma","qwen"}: raise ValueError("invalid rewrite model")
    if not isinstance(request_timeout_sec,int) or not 1<=request_timeout_sec<=3600: raise ValueError("invalid request timeout")
    inputs,root,prompt=load_evidence(source)
    output.mkdir(parents=True,exist_ok=False)
    for name,value in inputs.items(): base.write_text(output/"input"/name,value)
    for name in ("formalization.md","request.json","audit.md","audit.json","admission.json","tool/request.json","tool/result.json","tool/evidence.md"):
        base.write_text(output/"reused_evidence"/name,(root/name).read_text())
    gemma=base.Role("http://127.0.0.1:8030/v1",base.DEFAULT_GEMMA_MODEL,0.1,"max")
    role=gemma if rewriter_name=="gemma" else base.Role("http://127.0.0.1:8027/v1","Qwen/Qwen3.6-27B",0.1,None)
    status={"state":"running","stage":"proof_rewrite","source_run":str(source),"rewriter":asdict(role),
        "auditor":asdict(gemma),"request_timeout_sec":request_timeout_sec,"max_model_stages":2,
        "fresh_formalization_calls":0,"fresh_semantic_audit_calls":0,"tool_invocations":0,
        "saved_rational_witness_replayed":True,"rewrite_prompt_sha256":base.sha256_text(prompt),
        "model_output":"Markdown","strict_score":"NOT_RUN","whole_proof_independently_certified":False}
    write(output/"manifest.json",status);write(output/"status.json",status)
    caller=caller or rewrite.BudgetedCalls(output/"model_budget.json",max_stages=2)
    def call(role,system,user,root,stage,parser,index):
        if len(system)+len(user)>80000: raise ValueError("pilot prompt exceeds fixed 80000-character bound")
        text,parsed,record=caller(role=role,system_prompt=system,user_prompt=user,destination=root/"model",
            stage=stage,master_seed=seed+index,parser=parser,request_timeout_sec=request_timeout_sec)
        certificate.validate_markdown_budget_forcing(record,expected_stage=stage,expected_model=role.model,canonical_markdown=text,
            expected_timeout_sec=request_timeout_sec)
        base.write_text(root/"output.md",text);write(root/"call.json",record)
        return text,parsed
    try:
        finish_rewrite(call,role,gemma,prompt,output,status)
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        base.write_text(output/"error.txt",traceback.format_exc())
    write(output/"status.json",status);write(output/"result.json",status)
    return status


def finalize_saved_unresolved(source):
    """Finalize a complete forced RESOLUTION_FAILED response after bookkeeping failure."""
    status=json.loads((source/"status.json").read_text())
    if status["state"]!="failed_closed" or status["stage"]!="proof_rewrite":
        raise ValueError("source is not stopped during rewrite finalization")
    entries=json.loads((source/"model_budget.json").read_text())["calls"]
    matching=[row for row in entries if row["stage"]=="local_evidence_proof_rewrite" and row["state"]=="completed"]
    if len(matching)!=1: raise ValueError("no unique completed rewrite stage")
    row=matching[0];stage=row["stage"]
    root=source/"rewrite/model"/f"attempt_{row['attempt']:02d}_cap_{row['cap']}"
    metadata=json.loads((root/f"{stage}.metadata.json").read_text())
    raw=json.loads((root/f"{stage}.raw_response.json").read_text())
    text=raw["choices"][0]["message"]["content"].strip()
    record={"attempt":row["attempt"],"cap":row["cap"],"metadata":metadata,
            "request_timeout_sec":metadata["config"]["timeout_seconds"]}
    certificate.validate_markdown_budget_forcing(record,expected_stage=stage,expected_model=status["rewriter"]["model"],
        canonical_markdown=text,expected_timeout_sec=status["request_timeout_sec"])
    parts=parse_rewrite(text)
    if parts["outcome"]!="RESOLUTION_FAILED": raise ValueError("claimed proof still requires the full proof-audit stage")
    if raw["choices"][0]["finish_reason"]!="stop" or metadata["finish_reason"]!="stop":
        raise ValueError("saved rewrite is incomplete")
    write(source/"status_before_finalization_recovery.json",status)
    base.write_text(source/"rewrite/output.md",text);write(source/"rewrite/call.json",record)
    base.write_text(source/"rewritten_repair_brief.md",parts["repair_brief"])
    base.write_text(source/"unresolved.md",parts["proof"])
    status.update(state="completed",stage="rewrite_unresolved",rewrite_outcome="RESOLUTION_FAILED",
        finalization_recovery="saved_forced_response_no_new_model_calls",recovered_error=status.pop("error",None))
    write(source/"status.json",status);write(source/"result.json",status)
    return status


def load_saved(source,cycle,inputs):
    """Reuse one never-audited parser rejection; preserve model and input provenance."""
    if not isinstance(cycle,int) or cycle<1: raise ValueError("invalid saved cycle")
    manifest=json.loads((source/"manifest.json").read_text())
    status=json.loads((source/"status.json").read_text())
    if status["state"] not in {"completed","failed_closed"}:
        raise ValueError("source run must be terminal before recovery")
    if any(base.sha256_text(inputs[name])!=manifest["input_sha256"][name] for name,_ in INPUT_LABELS):
        raise ValueError("saved input hashes changed")
    root=source/"cycles"/f"cycle_{cycle:02d}"
    if (root/"audit.md").exists() or (root/"auditor").exists() or (root/"tool").exists():
        raise ValueError("normalization recovery cannot resample an audit or tool outcome")
    if json.loads((root/"parser.json").read_text())["parser_valid"]:
        raise ValueError("normalization recovery requires a prior parser rejection")
    text=(root/"formalization.md").read_text().strip()
    record=json.loads((root/"formalizer/call.json").read_text())
    certificate.validate_markdown_budget_forcing(record,expected_stage="local_evidence_formalization",
        expected_model=base.DEFAULT_GEMMA_MODEL,canonical_markdown=text,
        expected_timeout_sec=manifest.get("request_timeout_sec",600))
    return text,record


def run(inputs,output,seed,*,cycles=3,caller=None,tool=None,saved=None,request_timeout_sec=900):
    rewrite.assert_generic_boundary()
    if cycles not in (1,2,3): raise ValueError("at most three formalization cycles")
    if not isinstance(request_timeout_sec,int) or not 1 <= request_timeout_sec <= 3600:
        raise ValueError("request timeout must be 1..3600 seconds")
    if saved is not None:
        saved_text,saved_record=load_saved(saved[0],saved[1],inputs)
        cycles=1
    output.mkdir(parents=True,exist_ok=False)
    for name,_ in INPUT_LABELS: base.write_text(output/"input"/name,inputs[name])
    gemma=base.Role("http://127.0.0.1:8030/v1",base.DEFAULT_GEMMA_MODEL,0.1,"max")
    qwen=base.Role("http://127.0.0.1:8027/v1","Qwen/Qwen3.6-27B",0.1,None)
    status={"state":"running","stage":"formalization","cycles":[],"tool_invocations":0,
            "input_sha256":{name:base.sha256_text(inputs[name]) for name,_ in INPUT_LABELS},
            "formalizer":asdict(gemma),"auditor":asdict(gemma),"rewriter":asdict(qwen),
            "allowed_operations":list(OPERATIONS),"max_model_stages":3 if saved is not None else 2*cycles+2,
            "model_output":"Markdown","problem_specific_hints":False,"reference_answers_supplied":False,
            "strict_scores_supplied":False,"operator_witnesses_supplied":False,
            "request_timeout_sec":request_timeout_sec}
    if saved is not None:
        status.update(recovery="normalize_saved_parser_rejection",source_run=str(saved[0]),source_cycle=saved[1],
                      fresh_formalization_calls=0)
    write(output/"manifest.json",status)
    caller=caller or rewrite.BudgetedCalls(output/"model_budget.json",max_stages=status["max_model_stages"])
    tool=tool or execute_tool
    original=context(inputs)
    contract=original+"\n\n"+contracts()
    prompt=contract
    def call(role,system,user,root,stage,parser,index):
        if len(system)+len(user)>80000: raise ValueError("pilot prompt exceeds fixed 80000-character bound")
        text,parsed,record=caller(role=role,system_prompt=system,user_prompt=user,destination=root/"model",
            stage=stage,master_seed=seed+index,parser=parser,request_timeout_sec=request_timeout_sec)
        certificate.validate_markdown_budget_forcing(record,expected_stage=stage,expected_model=role.model,canonical_markdown=text,
            expected_timeout_sec=request_timeout_sec)
        base.write_text(root/"output.md",text);write(root/"call.json",record)
        return text,parsed
    try:
        for cycle in range(1,cycles+1):
            root=output/"cycles"/f"cycle_{cycle:02d}"
            row={"cycle":cycle,"state":"formalizing"};status["cycles"].append(row)
            status.update(stage="formalization",cycle=cycle);write(output/"status.json",status)
            if saved is None:
                text,inspection=call(gemma,SYSTEM,prompt,root/"formalizer","local_evidence_formalization",lambda t:inspect(t,inputs),cycle*100)
            else:
                text=saved_text
                inspection=inspect(text,inputs)
                write(root/"formalizer/call.json",saved_record)
            base.write_text(root/"formalization.md",text);write(root/"parser.json",inspection)
            row["parser_gate"]="PASS" if inspection["parser_valid"] else "FAIL"
            if not inspection["parser_valid"]:
                row.update(state="parser_rejected",semantic_audit="SKIPPED_PARSER_FAIL")
                prompt=contract+"\n\n# Draft to repair\n\n"+text+"\n\n# Deterministic Parser Feedback\n\n"+inspection["feedback"]+"\n\nNo audit or tool ran. Correct the syntax/type/source-binding error without inventing mathematics. Return a complete replacement."
                continue
            parsed=inspection["proposal"]
            if not parsed["call_requested"]:
                status.update(state="completed",stage="model_declined_tool",reason=parsed["reason"]);break
            row.update(state="auditing",operation=parsed["operation"],source=parsed["source"],claim=parsed["claim"])
            write(root/"request.json",parsed)
            base.write_text(root/"canonical_tool_arguments.md",parsed["canonical_tool_arguments"])
            write(root/"normalization.json",parsed["deterministic_normalization"])
            normalized_input=normalized_context(parsed)
            status.update(stage="semantic_audit");write(output/"status.json",status)
            audit,decision=call(gemma,AUDIT_SYSTEM,original+"\n\n# Proposed Local Check\n\n"+text+normalized_input+audit_contract(FORMAL_CHECKS),
                root/"auditor","local_evidence_semantic_audit",lambda t:parse_audit(t,FORMAL_CHECKS),cycle*100+1)
            base.write_text(root/"audit.md",audit);write(root/"audit.json",decision)
            row["semantic_audit"]=decision["decision"]
            if not decision["accepted"]:
                row.update(state="audit_rejected")
                prompt=contract+"\n\n# Draft to reassess\n\n"+text+"\n\n# Independent Audit Feedback\n\n"+audit+"\n\nReassess against the source and emit a complete replacement or NO_TOOL. Do not merely change the verdict."
                continue
            if parse_proposal(text,inputs)!=parsed: raise ValueError("tool input changed after audit")
            write(root/"admission.json",{"parser":"PASS","semantic":"ACCEPT","formalization_sha256":base.sha256_text(text),
                "audit_sha256":base.sha256_text(audit),"request_sha256":legacy.stable_hash(parsed)})
            status.update(stage="tool_execution",tool_invocations=status["tool_invocations"]+1);row.update(state="tool_execution")
            write(output/"status.json",status)
            result,report=tool(parsed,root/"tool",inputs)
            row.update(state="completed",tool_verdict=result["verdict"])
            if not result.get("usable_evidence"):
                prompt=contract+"\n\n# Draft to reassess\n\n"+text+"\n\n# Tool Feedback\n\n"+report+"\n\nReassess and return a complete new request or NO_TOOL. No general proof was established."
                continue
            status.update(stage="proof_rewrite",selected_cycle=cycle);write(output/"status.json",status)
            rewrite_input=original+"\n\n# Audited Local Tool Request\n\n"+text+normalized_input+"\n\n"+report
            finish_rewrite(call,qwen,gemma,rewrite_input,output,status)
            break
        if status["state"]=="running": status.update(state="completed",stage="formalization_cycles_exhausted")
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        base.write_text(output/"error.txt",traceback.format_exc())
    write(output/"status.json",status);write(output/"result.json",status)
    return status


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem-file",type=Path)
    parser.add_argument("--original-proof",type=Path)
    parser.add_argument("--repair-brief",type=Path)
    parser.add_argument("--resulting-proof",type=Path)
    parser.add_argument("--resume-run",type=Path)
    parser.add_argument("--saved-cycle",type=int)
    parser.add_argument("--rewrite-from-run",type=Path)
    parser.add_argument("--rewriter",choices=("gemma","qwen"),default="gemma")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--master-seed",type=int,required=True)
    parser.add_argument("--request-timeout-sec",type=int,default=900)
    args=parser.parse_args()
    if args.rewrite_from_run is not None:
        if any((args.resume_run,args.saved_cycle,args.problem_file,args.original_proof,args.repair_brief,args.resulting_proof)):
            parser.error("rewrite-from-run cannot be combined with source replacements or normalization recovery")
        print(json.dumps(rewrite_from_evidence(args.rewrite_from_run.resolve(),args.output.resolve(),args.master_seed,
            rewriter_name=args.rewriter,request_timeout_sec=args.request_timeout_sec)),flush=True)
        return
    if args.resume_run is not None:
        if args.saved_cycle is None or any((args.problem_file,args.original_proof,args.repair_brief,args.resulting_proof)):
            parser.error("resume requires saved-cycle and no replacement source paths")
        inputs={name:(args.resume_run/"input"/name).read_text().strip() for name,_ in INPUT_LABELS}
        saved=(args.resume_run.resolve(),args.saved_cycle)
    else:
        if args.saved_cycle is not None or not all((args.problem_file,args.original_proof,args.repair_brief,args.resulting_proof)):
            parser.error("fresh run requires all four source paths")
        problem=json.loads(args.problem_file.read_text())["claim"]
        inputs={"theorem.md":problem,"original_proof.md":args.original_proof.read_text().strip(),
                "repair_brief.md":args.repair_brief.read_text().strip(),"resulting_proof.md":args.resulting_proof.read_text().strip()}
        saved=None
    print(json.dumps(run(inputs,args.output.resolve(),args.master_seed,saved=saved,
        request_timeout_sec=args.request_timeout_sec)),flush=True)


if __name__=="__main__": main()
