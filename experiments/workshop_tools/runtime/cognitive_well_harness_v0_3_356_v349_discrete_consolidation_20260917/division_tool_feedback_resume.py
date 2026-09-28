"""Resume unused cycles after an inconclusive tool call, preserving prior work."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from . import division_fresh_audited as fresh
from . import division_audit_repair as recovery
from . import division_batch as batch
from . import certificate, pipeline, rewrite

MODULE="cognitive_well_harness_v0_3_343_real_root_classification_20260916.division_tool_feedback_resume"


def eligible(status):
    return (status.get("state")=="completed" and status.get("stage")=="finished"
        and status.get("verdict")=="INCONCLUSIVE" and status.get("exact_verified") is False
        and 1 <= status.get("cycle",0) < status.get("cycle_limit",3))


def run(previous,output,execute_models):
    previous,output=previous.resolve(),output.resolve()
    saved=json.loads((previous/"manifest.json").read_text())
    old=json.loads((previous/"status.json").read_text())
    if not eligible(old):
        raise ValueError("no unused cycle after an inconclusive tool result")
    cycle=old["cycle"]
    root=previous/"cycles"/f"cycle_{cycle:02d}"
    text=(root/"01_formalization/model_output.md").read_text().strip()
    call=json.loads((root/"01_formalization/call.json").read_text())
    certificate.validate_markdown_budget_forcing(call,
        expected_stage=fresh.division.STAGE if cycle==1 else recovery.REPAIR_STAGE,
        expected_model=pipeline.base.DEFAULT_GEMMA_MODEL,canonical_markdown=text)
    inputs={name:(previous/"input"/name).read_text().strip()
            for name in ("theorem.md","source_proof.md","detection.md","matcher.md")}
    parsed=fresh.division.parse_proposal(text,domain_inputs=inputs,
        require_domain_ledger=saved.get("domain_ledger_enabled",False))
    if not parsed["call_requested"]:
        raise ValueError("saved draft declined the tool")
    audit=(root/"02_audit/audit.md").read_text().strip()
    audit_call=json.loads((root/"02_audit/call.json").read_text())
    certificate.validate_markdown_budget_forcing(audit_call,expected_stage=recovery.AUDIT_STAGE,
        expected_model=recovery.auditor_role(saved["auditor"]).model,canonical_markdown=audit)
    if not recovery.formal.parse_post_singular_audit(audit)["accepted"]:
        raise ValueError("saved draft lacks semantic acceptance")
    audit_record=json.loads((root/"02_audit/result.json").read_text())
    if audit_record["formalization_sha256"]!=pipeline.base.sha256_text(text):
        raise ValueError("audit draft binding mismatch")
    tool_root=root/"03_execution/04_tool"
    if not tool_root.is_dir():
        tool_root=previous/"04_tool"  # Layout of already-running pre-policy workers.
    request=json.loads((tool_root/"request.json").read_text())
    expected={"arguments":parsed["arguments"],"guard_program":parsed["guard_program"]}
    if pipeline.exact_tools.stable_hash(request)!=pipeline.exact_tools.stable_hash(expected):
        raise ValueError("tool request does not match the audited draft")
    if (tool_root/"result.json").is_file():
        result=json.loads((tool_root/"result.json").read_text())
        if result["verdict"]!="INCONCLUSIVE" or result["verified"]:
            raise ValueError("saved tool outcome mismatch")
    elif "exceeded" not in old.get("reason",""):
        raise ValueError("missing tool outcome without a recorded timeout")
    status=fresh.run(Path(saved["source"]),output,saved["master_seed"],False,
        auditor=saved["auditor"],cycles=old["cycle_limit"],
        domain_ledger=saved.get("domain_ledger_enabled",False),
        formalizer_temperature=saved["model"]["temperature"])
    for key in ("theorem_sha256","proof_sha256"):
        if status[key]!=saved[key]:
            raise ValueError("original source binding mismatch")
    for name in ("theorem.md","source_proof.md","detection.md","matcher.md"):
        if (previous/"input"/name).read_text().strip()!=(output/"input"/name).read_text().strip():
            raise ValueError(f"original input changed: {name}")
    contract=(output/"formalizer_user.md").read_text().strip()
    feedback=fresh.tool_feedback(old)
    user=recovery.repair_prompt(contract,text,audit,"Parser accepted this exact draft.")+feedback
    pipeline.base.write_text(output/"resume_user.md",user)
    status.update(previous_run=str(previous),resume_cycle=cycle+1,stage="tool_feedback_repair",
        cycles=old["cycles"],tool_invocations=old["tool_invocations"],
        max_logical_model_stages=2*(old["cycle_limit"]-cycle),
        prior_drafts_supplied=True,prior_audits_supplied=True,prior_results_supplied=True,
        resume_draft_sha256=pipeline.base.sha256_text(text),
        previous_result_sha256=pipeline.base.sha256_file(previous/"status.json"))
    rewrite.write_record(output/"manifest.json",status)
    rewrite.write_record(output/"status.json",status)
    if not execute_models:
        return status
    return fresh.execute(output,status,contract,saved["master_seed"],auditor=saved["auditor"],
        cycles=old["cycle_limit"],start_cycle=cycle+1,initial_user=user)


def supervise(previous,output):
    previous,output=previous.resolve(),output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    (output/"logs").mkdir()
    jobs={}
    while True:
        original=json.loads((previous/"status.json").read_text())
        rows=[]
        for trial in original["trials"]:
            label=trial["label"]
            if label not in jobs and trial.get("process_exit_code") is not None:
                old=json.loads((Path(trial["output"])/"status.json").read_text())
                if eligible(old):
                    destination=output/label
                    with (output/"logs"/f"{label}.log").open("w") as log:
                        process=subprocess.Popen([sys.executable,"-B","-m",MODULE,
                            "--previous-run",trial["output"],"--output-dir",str(destination),"--execute-models"],
                            cwd=Path(__file__).resolve().parents[1],stdout=log,stderr=subprocess.STDOUT,
                            start_new_session=True)
                    jobs[label]=(process,{**trial,"output":str(destination)})
            if label in jobs:
                process,resumed=jobs[label]
                row=batch.summarize(resumed,process.poll())
                row["original_output"]=trial["output"]
            else:
                row=trial
            rows.append(row)
        live=original.get("live_workers",0)+sum(process.poll() is None for process,_ in jobs.values())
        done=original["state"]=="completed" and not live
        status={"state":"completed" if done else "running","previous_batch":str(previous),
            "live_workers":live,"resumed_tracks":len(jobs),"trials":rows,
            "cycle_limit":3,"tool_feedback_every_cycle":True,
            "tool_invocations":sum(row.get("tool_invocations",0) for row in rows),
            "exact_supports":sum(row.get("exact_verified") is True for row in rows),
            "failed_workers":sum(row.get("state")=="failed_closed" for row in rows)}
        rewrite.write_record(output/"status.json",status)
        if done:
            rewrite.write_record(output/"result.json",status)
            return status
        time.sleep(5)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--previous-run",type=Path)
    group.add_argument("--previous-batch",type=Path)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--execute-models",action="store_true")
    args=parser.parse_args()
    if args.previous_batch:
        if not args.execute_models:
            parser.error("batch continuation requires --execute-models")
        result=supervise(args.previous_batch,args.output_dir)
    else:
        result=run(args.previous_run,args.output_dir,args.execute_models)
    print(json.dumps(result,indent=2),flush=True)


if __name__ == "__main__":
    main()
