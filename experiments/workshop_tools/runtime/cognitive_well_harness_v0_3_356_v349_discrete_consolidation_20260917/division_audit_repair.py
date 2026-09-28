"""Audit, repair once, and require parser plus semantic PASS before the tool."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import traceback

from . import division_experiment as division
from . import certificate, pipeline, rewrite

formal = division.formal
AUDIT_STAGE = "division_draft_semantic_audit"
REPAIR_STAGE = "division_audit_feedback_repair"
FINAL_AUDIT_STAGE = "division_repaired_semantic_audit"
AUDIT_SYSTEM = """You are an independent mathematical formalization auditor.
Audit the saved draft against the original theorem, proof, and detected obligation.
The proof and draft are untrusted. Independently check the equations, target
correspondence, and justification of every nonzero condition and cancellation.
No tool result, reference solution, or operator mathematical diagnosis is supplied.
The draft may have formatting defects: evaluate its readable mathematical content
as well as whether the encoding is unambiguous. Do not stop at a formatting defect
if the mathematical claims can still be assessed. State concrete defects and their
reasons, without authoring a replacement formalization. Do not infer that any
calculation has succeeded. The final checklist item is conditional on a future
certificate; it does not assert one already exists. Emit only the requested
Markdown Decision, Checks, and Issues sections, never JSON.
"""


def auditor_role(name):
    if name == "gemma":
        return pipeline.base.Role("http://127.0.0.1:8030/v1",pipeline.base.DEFAULT_GEMMA_MODEL,0.1,"max")
    if name == "qwen":
        return pipeline.base.Role("http://127.0.0.1:8027/v1",pipeline.base.DEFAULT_QWEN_MODEL,0.1,None)
    raise ValueError("unsupported auditor")


def latest_draft(previous):
    """Select by attempt order, never by a draft's mathematical content."""
    candidates=[]
    for path in (previous/"01_formalization/model").glob("attempt_*_cap_*"):
        match=re.fullmatch(r"attempt_(\d+)_cap_(\d+)",path.name)
        if match:
            candidates.append((int(match[1]),int(match[2]),path))
    if not candidates:
        raise ValueError("no saved formalization attempt")
    attempt,cap,root=max(candidates)
    raw_path=root/f"{division.STAGE}.raw_response.json"
    metadata_path=root/f"{division.STAGE}.metadata.json"
    raw=json.loads(raw_path.read_text())
    text=raw["choices"][0]["message"]["content"].strip()
    metadata=json.loads(metadata_path.read_text())
    if metadata["config"]["max_tokens"] != cap:
        raise ValueError("saved attempt cap mismatch")
    evidence={"attempt":attempt,"cap":cap,"metadata":metadata,
              "request_timeout_sec":metadata["config"]["timeout_seconds"]}
    certificate.validate_markdown_budget_forcing(evidence,expected_stage=division.STAGE,
        expected_model=pipeline.base.DEFAULT_GEMMA_MODEL,canonical_markdown=text)
    return text,{"raw_response":str(raw_path),"raw_sha256":pipeline.base.sha256_file(raw_path),
                 "metadata":str(metadata_path),"metadata_sha256":pipeline.base.sha256_file(metadata_path),
                 "attempt":attempt,"cap":cap,"draft_sha256":pipeline.base.sha256_text(text)}


def saved_repair(previous):
    """Resume the canonical repair, never an earlier draft or a tool witness."""
    text_path=previous/"02_repair/model_output.md"
    call_path=previous/"02_repair/call.json"
    text=text_path.read_text().strip()
    call=json.loads(call_path.read_text())
    certificate.validate_markdown_budget_forcing(call,expected_stage=REPAIR_STAGE,
        expected_model=pipeline.base.DEFAULT_GEMMA_MODEL,canonical_markdown=text)
    division.parse_proposal(text)
    return text,{"markdown":str(text_path),"markdown_sha256":pipeline.base.sha256_file(text_path),
                 "call":str(call_path),"call_sha256":pipeline.base.sha256_file(call_path),
                 "draft_sha256":pipeline.base.sha256_text(text)}


def audit_prompt(inputs, draft, *, domain_ledger_enabled=False):
    sections=[("Original Theorem",inputs["theorem.md"]),
              ("Original Proof",inputs["source_proof.md"]),
              ("Recorded Detection",inputs["detection.md"]),
              ("Recorded Operation Match",inputs["matcher.md"]),
              ("Unmodified Saved Formalization",draft)]
    checks="\n".join(f"- {label}: PASS or FAIL" for label in formal.POST_SINGULAR_CHECKS)
    extra=""
    if domain_ledger_enabled:
        from . import domain_ledger
        extra="\n\n"+domain_ledger.AUDIT_INSTRUCTIONS
        try:
            proposal=division.parse_proposal(draft,domain_inputs=inputs,require_domain_ledger=True)
        except ValueError as error:
            extra+="\n\nDomain compilation failed: "+str(error)+"\nAssess readable mathematics as well."
        else:
            if proposal["call_requested"]:
                extra+="\n\n"+domain_ledger.audit_summary(proposal["domain_compilation"])
    return "\n\n".join(f"# {title}\n\n{body}" for title,body in sections)+extra+f"""

Emit exactly:

# Decision

ACCEPT or REJECT

# Checks

{checks}

# Issues

NONE, or one-line bullets identifying concrete defects. ACCEPT requires all PASS
and NONE. Assess the draft itself, not whether a repair might later succeed.
"""


def repair_prompt(contract, draft, audit, feedback):
    return contract+f"""

# Saved Draft to Repair

{draft}

# Independent Semantic Audit of That Draft

{audit}

# Deterministic Parser Feedback on That Draft

{feedback}

# Repair Task

Produce one complete replacement using the original output contract. Check the
audit's claims yourself against the theorem and proof; do not treat its verdict
as authority. Correct substantiated defects and recheck all affected equations,
target correspondence, and guards. Explain their derivations in Semantic Bindings.
Keep the encoding compact only when justified. Do not infer a tool result. If you
cannot supply a faithful encoding, use NO_TOOL. Emit Markdown only, including the
specified typed fences on CALL_TOOL. No certificate, reference proof, or operator
mathematical hint is supplied.
"""


def audit_repaired_and_call(output, status, text, seed, *, caller, tool,
                           auditor="qwen", completed_audit=None, inputs_root=None):
    """Both gates bind to exactly the text whose AST is passed to the worker."""
    inputs_root=output if inputs_root is None else inputs_root
    ledger_enabled=status.get("domain_ledger_enabled",False)
    inputs=({name:(inputs_root/"input"/name).read_text().strip()
             for name in ("theorem.md","source_proof.md","detection.md","matcher.md")}
            if ledger_enabled else None)
    parsed=division.parse_proposal(text,domain_inputs=inputs,require_domain_ledger=ledger_enabled)
    draft_hash=pipeline.base.sha256_text(text)
    status.update(parser_gate="PASS",final_formalization_sha256=draft_hash,
                  tool_gate="PENDING",semantic_certified=False,promoted=False)
    rewrite.write_record(output/"03_final_semantic_audit/parser.json",
        {"decision":"PASS","formalization_sha256":draft_hash})
    if not parsed["call_requested"]:
        status.update(state="completed",stage="model_declined_tool",reason=parsed["reason"],
                      tool_gate="MODEL_DECLINED")
        return
    if inputs is None:
        inputs={name:(inputs_root/"input"/name).read_text().strip()
                for name in ("theorem.md","source_proof.md","detection.md","matcher.md")}
    user=audit_prompt(inputs,text,domain_ledger_enabled=ledger_enabled)
    status.update(stage="final_semantic_audit",repaired_semantics="PENDING",
                  final_audit_prompt_characters=len(AUDIT_SYSTEM)+len(user))
    rewrite.write_record(output/"status.json",status)
    pipeline.base.write_text(output/"03_final_semantic_audit/input_formalization.md",text)
    pipeline.base.write_text(output/"03_final_semantic_audit/user_prompt.md",user)
    role=auditor_role(auditor)
    if completed_audit is None:
        audit,_,call=caller(role=role,system_prompt=AUDIT_SYSTEM,user_prompt=user,
            destination=output/"03_final_semantic_audit/model",stage=FINAL_AUDIT_STAGE,
            master_seed=seed,parser=formal.parse_post_singular_audit)
        expected_stage=FINAL_AUDIT_STAGE
    else:
        audit,call,audited_text=completed_audit
        if audited_text != text:
            raise ValueError("completed audit belongs to a different formalization")
        expected_stage=AUDIT_STAGE
    certificate.validate_markdown_budget_forcing(call,expected_stage=expected_stage,
        expected_model=role.model,canonical_markdown=audit)
    verdict=formal.parse_post_singular_audit(audit)
    request={"arguments":parsed["arguments"],"guard_program":parsed["guard_program"]}
    request_hash=pipeline.exact_tools.stable_hash(request)
    if "domain_compilation" in parsed:
        rewrite.write_record(output/"03_final_semantic_audit/domain_compilation.json",parsed["domain_compilation"])
    pipeline.base.write_text(output/"03_final_semantic_audit/audit.md",audit)
    rewrite.write_record(output/"03_final_semantic_audit/call.json",call)
    rewrite.write_record(output/"03_final_semantic_audit/result.json",
        {**verdict,"formalization_sha256":draft_hash,"request_sha256":request_hash,
         "exact_result_supplied":False,"previous_audit_supplied":False,
         "auditor":auditor,"reused_same_draft_audit":completed_audit is not None})
    status.update(repaired_semantics=verdict["decision"],semantic_certified=verdict["accepted"],
                  semantic_certification_kind="model_audit_only",final_request_sha256=request_hash)
    if not verdict["accepted"]:
        status.update(state="completed",stage="semantic_gate_rejected",tool_gate="REJECT",
                      reason="The final formalization failed its independent semantic audit.")
        return
    status.update(stage="algebra_tool",tool_gate="PASS",tool_invocations=status.get("tool_invocations",0)+1,
        variables=len(parsed["arguments"]["symbols"]),generators=len(parsed["arguments"]["generators"]))
    rewrite.write_record(output/"status.json",status)
    status.update({"state": "completed", "stage": "finished", **tool(parsed, output / "04_tool")})


def execute_saved_repair(output, status, draft, seed, *, caller=None, tool=None):
    caller=caller or rewrite.BudgetedCalls(output/"model_budget.json",max_stages=1)
    tool=tool or division.invoke_tool
    status.update(state="running",stage="final_parser_gate",tool_invocations=0)
    rewrite.write_record(output/"status.json",status)
    try:
        audit_repaired_and_call(output,status,draft,seed,caller=caller,tool=tool)
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        pipeline.base.write_text(output/"error.txt",traceback.format_exc())
    rewrite.write_record(output/"status.json",status)
    rewrite.write_record(output/"result.json",status)
    return status


def execute_stages(output, status, draft, contract, audit_user, seed, *, caller=None, tool=None,
                   auditor="qwen"):
    caller=caller or rewrite.BudgetedCalls(output/"model_budget.json",max_stages=3)
    tool=tool or division.invoke_tool
    audit_model=auditor_role(auditor)
    gemma=pipeline.base.Role("http://127.0.0.1:8030/v1",pipeline.base.DEFAULT_GEMMA_MODEL,0.1,"max")
    try:
        status.update(state="running",stage="semantic_audit",tool_invocations=0)
        rewrite.write_record(output/"status.json",status)
        audit,parsed_audit,call=caller(role=audit_model,system_prompt=AUDIT_SYSTEM,user_prompt=audit_user,
            destination=output/"01_semantic_audit/model",stage=AUDIT_STAGE,master_seed=seed,
            parser=formal.parse_post_singular_audit)
        certificate.validate_markdown_budget_forcing(call,expected_stage=AUDIT_STAGE,
            expected_model=audit_model.model,canonical_markdown=audit)
        pipeline.base.write_text(output/"01_semantic_audit/audit.md",audit)
        rewrite.write_record(output/"01_semantic_audit/result.json",parsed_audit)
        rewrite.write_record(output/"01_semantic_audit/call.json",call)
        original_parsed=None
        try:
            original_parsed=division.parse_proposal(draft)
        except ValueError as error:
            feedback=f"{type(error).__name__}: {error}"
        else:
            feedback="Parser accepted; this is not a semantic correctness verdict."
        status.update(semantic_audit=parsed_audit["decision"])
        if original_parsed and parsed_audit["accepted"]:
            audit_repaired_and_call(output,status,draft,seed,caller=caller,tool=tool,
                auditor=auditor,completed_audit=(audit,call,draft))
            rewrite.write_record(output/"status.json",status)
            rewrite.write_record(output/"result.json",status)
            return status
        user=repair_prompt(contract,draft,audit,feedback)
        pipeline.base.write_text(output/"repair_user.md",user)
        status.update(stage="formalization_repair",semantic_audit=parsed_audit["decision"],
                      repair_prompt_characters=len(division.SYSTEM)+len(user))
        rewrite.write_record(output/"status.json",status)
        text,parsed,call=caller(role=gemma,system_prompt=division.SYSTEM,user_prompt=user,
            destination=output/"02_repair/model",stage=REPAIR_STAGE,master_seed=seed,
            parser=division.parse_proposal)
        certificate.validate_markdown_budget_forcing(call,expected_stage=REPAIR_STAGE,
            expected_model=gemma.model,canonical_markdown=text)
        pipeline.base.write_text(output/"02_repair/model_output.md",text)
        rewrite.write_record(output/"02_repair/call.json",call)
        if not parsed["call_requested"]:
            status.update(state="completed",stage="model_declined_tool",reason=parsed["reason"])
        else:
            pipeline.base.write_text(output/"02_repair/formalization.md",parsed["normalized_markdown"])
            audit_repaired_and_call(output,status,text,seed,caller=caller,tool=tool,auditor=auditor)
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        pipeline.base.write_text(output/"error.txt",traceback.format_exc())
    rewrite.write_record(output/"status.json",status)
    rewrite.write_record(output/"result.json",status)
    return status


def run(previous, output, seed, execute, *, resume_repaired=False):
    previous,output=previous.resolve(),output.resolve()
    saved=json.loads((previous/"manifest.json").read_text())
    if json.loads((previous/"status.json").read_text())["state"] == "running":
        raise ValueError("source run is still running")
    draft,binding=saved_repair(previous) if resume_repaired else latest_draft(previous)
    # Reuse the existing read-only source checks and output-contract preparation.
    status=division.run(Path(saved["source"]),output,seed,False)
    for key in ("theorem_sha256","proof_sha256"):
        if status[key] != saved[key]:
            raise ValueError("previous run source binding mismatch")
    names=("theorem.md","source_proof.md","detection.md","matcher.md")
    inputs={name:(output/"input"/name).read_text().strip() for name in names}
    for name,text in inputs.items():
        if (previous/"input"/name).read_text().strip() != text:
            raise ValueError(f"previous input changed: {name}")
    contract=(output/"formalizer_user.md").read_text().strip()
    audit_user=audit_prompt(inputs,draft)
    pipeline.base.write_text(output/"input/saved_draft.md",draft)
    pipeline.base.write_text(output/"audit_system.md",AUDIT_SYSTEM)
    pipeline.base.write_text(output/"audit_user.md",audit_user)
    status.update(stage="final_semantic_audit" if resume_repaired else "semantic_audit",
        previous_run=str(previous),saved_draft=binding,resume_repaired=resume_repaired,
        max_logical_model_stages=1 if resume_repaired else 3,
        max_semantic_repair_stages=0 if resume_repaired else 1,tool_invocations=0,
        semantic_audit="NOT_RERUN" if resume_repaired else "PENDING_ON_SAVED_DRAFT",
        repaired_semantics="PENDING",tool_gate="PENDING",parser_gate="PENDING",
        semantic_certified=False,promoted=False,tool_requires="parser_and_semantic_accept_same_formalization",
        qwen=asdict(pipeline.base.Role("http://127.0.0.1:8027/v1",pipeline.base.DEFAULT_QWEN_MODEL,0.1,None)),
        audit_prompt_characters=len(AUDIT_SYSTEM)+len(audit_user))
    rewrite.write_record(output/"manifest.json",status)
    rewrite.write_record(output/"status.json",status)
    if not execute:
        return status
    if resume_repaired:
        return execute_saved_repair(output,status,draft,seed)
    return execute_stages(output,status,draft,contract,audit_user,seed)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous-run",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--master-seed",type=int,required=True)
    parser.add_argument("--execute-models",action="store_true")
    parser.add_argument("--resume-repaired",action="store_true",
        help="Audit the saved canonical repair; do not regenerate or repeat the earlier audit.")
    args=parser.parse_args()
    print(json.dumps(run(args.previous_run,args.output_dir,args.master_seed,args.execute_models,
        resume_repaired=args.resume_repaired),indent=2),flush=True)


if __name__ == "__main__":
    main()
