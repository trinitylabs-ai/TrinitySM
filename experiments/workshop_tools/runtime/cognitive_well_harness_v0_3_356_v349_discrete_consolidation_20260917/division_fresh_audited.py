"""Fresh model formalization with a selectable, isolated semantic auditor."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import traceback

from . import division_experiment as division
from . import division_audit_repair as recovery
from . import certificate, pipeline, rewrite
from . import parser_feedback, shared_feedback


def inspect_draft(text, *, domain_inputs=None, require_domain_ledger=False):
    """Capture deterministic parser feedback for the joint audit/repair boundary."""
    try:
        parsed=division.parse_proposal(text,domain_inputs=domain_inputs,require_domain_ledger=require_domain_ledger)
    except ValueError as error:
        report=parser_feedback.diagnose(text,f"{type(error).__name__}: {error}",inputs=domain_inputs)
        return {"parser_valid":False,"parser_feedback":report["feedback"],"parser_diagnostics":report}
    return {"parser_valid":True,"proposal":parsed,
            "parser_feedback":"Parser accepted; semantics remain unaudited."}


def tool_feedback(result):
    """Small factual feedback; never send the potentially huge witness to a model."""
    if result.get("verdict") != "INCONCLUSIVE" or result.get("exact_verified") is True:
        raise ValueError("tool feedback requires an inconclusive outcome")
    sizes=lambda value: "unknown" if not value else f"{value['variables']} variables / {value['generators']} generators"
    return ("\n\n# Exact Tool Feedback on This Draft\n\n"
        f"The {result.get('feedback_backend', 'guarded substitution and polynomial-division tool')} returned INCONCLUSIVE, not a proof.\n"
        f"Source size: {sizes(result.get('source_size'))}. Reduced size: {sizes(result.get('reduced_size'))}.\n"
        f"Outcome detail: {result.get('reason','Polynomial division left a nonzero remainder.')}\n"
        "This is not a disproof and does not identify which equation, representation, or target is wrong. "
        "Reassess the encoding against the original theorem and proof; do not invent hypotheses or "
        "assert the desired conclusion as an input. The next version still needs parser and semantic checks.\n")


def parser_repair_prompt(contract,draft,feedback):
    """No audit verdict is invented or carried from an earlier draft."""
    return contract+f"""

# Saved Draft to Repair

{draft}

# Deterministic Parser Feedback on That Draft

{feedback}

# Parser Repair Task

No semantic audit was run on this draft because parsing failed. Produce one
complete replacement in the original Markdown contract. Fix the reported syntax
or source-binding defects, including every listed location. Preserve unaffected
formulas and bindings; do not redesign the algebra merely to fix notation.
Recheck your mathematical encoding against the
original theorem and proof. No semantic acceptance is implied. Do not invent
assumptions or a tool result. The replacement must pass parsing, then a fresh
semantic audit, before any tool call. Use NO_TOOL if a faithful encoding is not
available. Emit no JSON or executable code.
"""


def execute(output,status,contract,seed,*,auditor="gemma",cycles=3,caller=None,tool=None,
            start_cycle=1,initial_user=None,formalizer_system=None,should_stop=None,feedback=None):
    if cycles not in range(1,4):
        raise ValueError("cycles must be between 1 and 3")
    if not 1 <= start_cycle <= cycles:
        raise ValueError("invalid resume cycle")
    caller=caller or rewrite.BudgetedCalls(output/"model_budget.json",max_stages=2*(cycles-start_cycle+1))
    tool=tool or division.invoke_tool
    text=''
    try:
        status.setdefault("tool_invocations",0)
        status.setdefault("cycles",[])
        status.setdefault("audit_calls_skipped",0)
        status.update(state="running",stage="fresh_formalization",cycle_limit=cycles,
                      audit_on_parser_failure=False)
        temperature=division.validate_temperature(status.get("model",{}).get("temperature",0.1))
        role=pipeline.base.Role("http://127.0.0.1:8030/v1",pipeline.base.DEFAULT_GEMMA_MODEL,temperature,"max")
        audit_role=recovery.auditor_role(auditor)
        inputs={name:(output/"input"/name).read_text().strip()
                for name in ("theorem.md","source_proof.md","detection.md","matcher.md")}
        ledger_enabled=status.get("domain_ledger_enabled",False)
        user=contract if initial_user is None else initial_user
        for cycle in range(start_cycle,cycles+1):
            if should_stop and should_stop():
                status.update(state="completed",stage="superseded_by_verified_candidate")
                break
            cycle_seed=pipeline.base.stable_seed(seed,f"formalization-audit-cycle:{cycle}")
            stage=division.STAGE if cycle==1 else recovery.REPAIR_STAGE
            root=output/"cycles"/f"cycle_{cycle:02d}"
            row={"cycle":cycle,"state":"formalizing","seed":cycle_seed}
            status["cycles"].append(row)
            status.update(state="running",cycle=cycle,stage="fresh_formalization" if cycle==1 else "formalization_repair",
                          tool_gate="PENDING",semantic_certified=False,
                          parser_gate="PENDING",semantic_audit="NOT_RUN")
            for stale in ("verdict","exact_verified","reason","variables","generators",
                          "source_size","reduced_size","repaired_semantics"):
                status.pop(stale,None)
            rewrite.write_record(output/"status.json",status)
            text=''
            current_user=feedback.augment(user,cycle,root) if feedback else user
            text,inspection,call=caller(role=role,system_prompt=formalizer_system or division.SYSTEM,user_prompt=current_user,
                destination=root/"01_formalization/model",stage=stage,
                master_seed=cycle_seed,parser=lambda draft:inspect_draft(draft,domain_inputs=inputs,
                    require_domain_ledger=ledger_enabled))
            certificate.validate_markdown_budget_forcing(call,expected_stage=stage,
                expected_model=role.model,canonical_markdown=text)
            pipeline.base.write_text(root/"01_formalization/model_output.md",text)
            rewrite.write_record(root/"01_formalization/call.json",call)
            rewrite.write_record(root/"01_formalization/parser.json",inspection)
            if feedback:
                feedback.publish(cycle,'parser_accepted' if inspection['parser_valid'] else 'parser_rejected',
                    inspection['parser_feedback'],text)
            gate="PASS" if inspection["parser_valid"] else "FAIL"
            row.update(parser_gate=gate,formalization_sha256=pipeline.base.sha256_text(text))
            status.update(parser_gate=gate)
            if cycle==1:
                status.update(initial_parser_gate=gate)
            if should_stop and should_stop():
                status.update(state="completed",stage="superseded_by_verified_candidate")
                break
            if inspection["parser_valid"] and not inspection["proposal"]["call_requested"]:
                if feedback:feedback.publish(cycle,'model_declined',inspection['proposal']['reason'],text)
                row.update(state="model_declined_tool")
                status.update(state="completed",stage="model_declined_tool",
                              reason=inspection["proposal"]["reason"])
                break
            if not inspection["parser_valid"]:
                row.update(state="completed",semantic_audit="SKIPPED_PARSER_FAIL",audit_performed=False)
                status.update(semantic_audit="SKIPPED_PARSER_FAIL",completed_cycles=cycle,
                              tool_gate="PARSER_REJECT",stage="parser_rejected",
                              audit_calls_skipped=status["audit_calls_skipped"]+1)
                rewrite.write_record(root/"02_audit/skipped.json",{
                    "reason":"parser_failed","formalization_sha256":row["formalization_sha256"],
                    "model_calls":0,"parser_feedback":inspection["parser_feedback"]})
                if cycle==cycles:
                    status.update(state="completed",stage="cycle_limit_rejected",
                        reason="The final draft failed parsing; semantic audit and tool were skipped.")
                    break
                rewrite.write_record(output/"status.json",status)
                user=parser_repair_prompt(contract,text,inspection["parser_feedback"])
                continue
            if inspection["parser_valid"]:
                arguments=inspection["proposal"]["arguments"]
                row.update(variables=len(arguments["symbols"]),generators=len(arguments["generators"]))
                status.update(variables=row["variables"],generators=row["generators"])
                if "domain_compilation" in inspection["proposal"]:
                    report=inspection["proposal"]["domain_compilation"]
                    rewrite.write_record(root/"01_formalization/domain_compilation.json",report)
                    row.update(domain_facts=len(report["facts"]),compiled_nonzero_facts=report["compiled_nonzero_facts"],
                               retained_only_facts=report["retained_only_facts"])
            row.update(state="auditing",audit_performed=True)
            status.update(stage="semantic_audit",semantic_audit="PENDING")
            rewrite.write_record(output/"status.json",status)
            audit,_,audit_call=caller(role=audit_role,system_prompt=recovery.AUDIT_SYSTEM,
                user_prompt=recovery.audit_prompt(inputs,text,domain_ledger_enabled=ledger_enabled),destination=root/"02_audit/model",
                stage=recovery.AUDIT_STAGE,master_seed=cycle_seed,parser=recovery.formal.parse_post_singular_audit)
            certificate.validate_markdown_budget_forcing(audit_call,expected_stage=recovery.AUDIT_STAGE,
                expected_model=audit_role.model,canonical_markdown=audit)
            verdict=recovery.formal.parse_post_singular_audit(audit)
            pipeline.base.write_text(root/"02_audit/audit.md",audit)
            rewrite.write_record(root/"02_audit/call.json",audit_call)
            rewrite.write_record(root/"02_audit/result.json",{**verdict,
                "formalization_sha256":row["formalization_sha256"],"exact_result_supplied":False})
            if feedback:
                feedback.publish(cycle,'semantic_accepted' if verdict['accepted'] else 'semantic_rejected',
                    audit,text,shared_feedback.audit_summary(verdict))
            row.update(state="completed",semantic_audit=verdict["decision"])
            status.update(semantic_audit=verdict["decision"],completed_cycles=cycle)
            if should_stop and should_stop():
                status.update(state="completed",stage="superseded_by_verified_candidate")
                break
            if inspection["parser_valid"] and verdict["accepted"]:
                def reporting_tool(parsed,destination):
                    rewrite.write_record(output/"status.json",status)
                    return tool(parsed,destination)
                recovery.audit_repaired_and_call(root/"03_execution",status,text,cycle_seed,caller=caller,tool=reporting_tool,
                    auditor=auditor,completed_audit=(audit,audit_call,text),inputs_root=output)
                row.update(tool_verdict=status["verdict"],exact_verified=status["exact_verified"])
                if feedback:
                    feedback.publish(cycle,'tool_verified' if status['exact_verified'] else 'tool_inconclusive',
                        shared_feedback.tool_summary(status),text)
                if status["exact_verified"] or cycle==cycles:
                    break
                tool_message=tool_feedback(status)
                pipeline.base.write_text(root/"tool_feedback.md",tool_message)
                user=recovery.repair_prompt(contract,text,audit,inspection["parser_feedback"])+tool_message
                continue
            if cycle==cycles:
                status.update(state="completed",stage="cycle_limit_rejected",tool_gate="REJECT",
                    reason="No draft passed both parser and semantic audit within the cycle limit.")
                break
            user=recovery.repair_prompt(contract,text,audit,inspection["parser_feedback"])
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        if feedback and status.get('cycles'):
            feedback.publish(status['cycles'][-1]['cycle'],'worker_error',status['error'],text)
        pipeline.base.write_text(output/"error.txt",traceback.format_exc())
    rewrite.write_record(output/"status.json",status)
    rewrite.write_record(output/"result.json",status)
    return status


def run(source,output,seed,execute_models,*,auditor="gemma",cycles=3,domain_ledger=False,formalizer_temperature=0.1):
    if cycles not in range(1,4):
        raise ValueError("cycles must be between 1 and 3")
    output=output.resolve()
    status=division.run(source,output,seed,False,domain_ledger=domain_ledger,
        formalizer_temperature=formalizer_temperature)
    status.update(stage="fresh_formalization",auditor=auditor,
        auditor_model=asdict(recovery.auditor_role(auditor)),max_logical_model_stages=2*cycles,
        max_semantic_repair_stages=cycles-1,cycle_limit=cycles,fresh_formalization=True,
        max_tool_invocations=cycles,tool_feedback_every_cycle=True,
        audit_on_parser_failure=False,audit_calls_skipped=0,parser_feedback_version=parser_feedback.VERSION,
        prior_drafts_supplied=False,prior_audits_supplied=False,prior_results_supplied=False,
        audit_context="original_inputs_and_current_draft_only",
        semantic_audit="PENDING",tool_gate="PENDING",semantic_certified=False,promoted=False,
        tool_requires="parser_and_selected_auditor_accept_same_formalization",tool_invocations=0)
    rewrite.write_record(output/"manifest.json",status)
    rewrite.write_record(output/"status.json",status)
    if not execute_models:
        return status
    return execute(output,status,(output/"formalizer_user.md").read_text().strip(),seed,auditor=auditor,cycles=cycles)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-acquisition",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--master-seed",type=int,required=True)
    parser.add_argument("--auditor",choices=("gemma","qwen"),default="gemma")
    parser.add_argument("--execute-models",action="store_true")
    parser.add_argument("--cycles",type=int,default=3)
    parser.add_argument("--domain-ledger",action="store_true")
    parser.add_argument("--formalizer-temperature",type=float,default=0.1)
    args=parser.parse_args()
    print(json.dumps(run(args.source_acquisition,args.output_dir,args.master_seed,args.execute_models,
        auditor=args.auditor,cycles=args.cycles,domain_ledger=args.domain_ledger,
        formalizer_temperature=args.formalizer_temperature),indent=2),flush=True)


if __name__ == "__main__":
    main()
