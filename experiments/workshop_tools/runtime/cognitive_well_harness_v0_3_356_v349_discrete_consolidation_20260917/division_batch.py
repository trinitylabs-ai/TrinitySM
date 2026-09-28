"""Independent seeded fresh-audit trials; no cross-trial model context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from . import division_fresh_audited as fresh
from . import pipeline, rewrite

MODULE="cognitive_well_harness_v0_3_343_real_root_classification_20260916.division_fresh_audited"


def wait_for_batch(previous,output):
    """Serialize authorized comparison batches; never feed earlier math to models."""
    previous,output=previous.resolve(),output.resolve()
    if not (previous/"manifest.json").is_file():
        raise ValueError("prerequisite batch has no manifest")
    queue_path=output.with_name(output.name+".queue.json")
    record={"state":"waiting","after_batch":str(previous),"output":str(output),
            "prior_model_artifacts_supplied":False,"poll_seconds":5}
    rewrite.write_record(queue_path,record)
    while True:
        prior=json.loads((previous/"status.json").read_text())
        if prior.get("state")=="failed_closed" or prior.get("failed_workers",0):
            record.update(state="blocked",reason="Prerequisite has a mechanical failure; inspect before comparison.")
            rewrite.write_record(queue_path,record)
            raise RuntimeError(record["reason"])
        if prior.get("state")=="completed":
            record.update(state="ready",previous_result_sha256=pipeline.base.sha256_file(previous/"status.json"))
            rewrite.write_record(queue_path,record)
            return
        time.sleep(5)


def trials(output,seed,size):
    if size not in range(1,9):
        raise ValueError("batch size must be between 1 and 8")
    return [{"label":f"sample_{index:02d}","output":str(output/f"sample_{index:02d}"),
             "seed":pipeline.base.stable_seed(seed,f"fresh-audited-trial:{index}")}
            for index in range(1,size+1)]


def child_command(source,trial,auditor,cycles=3,*,domain_ledger=False):
    return [sys.executable,"-B","-m",MODULE,"--source-acquisition",str(source),
            "--output-dir",trial["output"],"--master-seed",str(trial["seed"]),
            "--auditor",auditor,"--cycles",str(cycles),"--execute-models"]+(["--domain-ledger"] if domain_ledger else [])+(
            ["--formalizer-temperature",str(trial["formalizer_temperature"])] if "formalizer_temperature" in trial else [])


def summarize(trial,returncode):
    root=Path(trial["output"])
    row={**{key:trial[key] for key in ("label","output","seed","formalizer_temperature") if key in trial},
         "state":"starting" if returncode is None else "failed_closed"}
    path=root/"status.json"
    if path.is_file():
        saved=json.loads(path.read_text())
        keys=("state","stage","initial_parser_gate","semantic_audit","repaired_semantics",
              "parser_gate","tool_gate","tool_invocations","variables","generators",
              "verdict","exact_verified","source_size","reduced_size","error","reason",
              "cycle","completed_cycles","cycles","audit_on_parser_failure","audit_calls_skipped","parser_feedback_version")
        row.update({key:saved[key] for key in keys if key in saved})
    row["formalization_saved"]=any(root.glob("cycles/cycle_*/01_formalization/model_output.md"))
    row["process_exit_code"]=returncode
    if returncode is not None and row["state"] not in {"completed","failed_closed"}:
        row.update(state="failed_closed",error=f"worker exited {returncode} without a terminal status")
    return row


def run(source,output,seed,size,execute_models,*,auditor="gemma",cycles=3,domain_ledger=False,formalizer_temperatures=None):
    source,output=source.resolve(),output.resolve()
    plan=trials(output,seed,size)
    if formalizer_temperatures is not None:
        if len(formalizer_temperatures)!=size:
            raise ValueError("temperature schedule must have exactly one entry per trial")
        for row,value in zip(plan,formalizer_temperatures,strict=True):
            row["formalizer_temperature"]=fresh.division.validate_temperature(value)
    # Shared source validation and prompt preflight; no model call here.
    status=fresh.run(source,output,seed,False,auditor=auditor,cycles=cycles,domain_ledger=domain_ledger)
    status.update(stage="batch",batch_size=size,max_concurrent_trials=size,
        max_logical_model_stages=2*cycles*size,max_logical_model_stages_per_trial=2*cycles,
        max_tool_invocations=cycles*size,max_tool_invocations_per_trial=cycles,
        trials=plan,independent_trial_contexts=True,
        formalizer_temperatures=formalizer_temperatures or [0.1]*size)
    rewrite.write_record(output/"manifest.json",status)
    rewrite.write_record(output/"status.json",status)
    if not execute_models:
        return status
    (output/"logs").mkdir()
    processes=[]
    for trial in plan:
        with (output/"logs"/f"{trial['label']}.log").open("w") as log:
            process=subprocess.Popen(child_command(source,trial,auditor,cycles,domain_ledger=domain_ledger),
                cwd=Path(__file__).resolve().parents[1],stdout=log,stderr=subprocess.STDOUT,
                start_new_session=True)
        processes.append(process)
    while True:
        codes=[process.poll() for process in processes]
        rows=[summarize(trial,code) for trial,code in zip(plan,codes,strict=True)]
        live=sum(code is None for code in codes)
        status.update(state="running" if live else "completed",trials=rows,live_workers=live,
            formalizations_saved=sum(row["formalization_saved"] for row in rows),
            parser_passes=sum(row.get("initial_parser_gate")=="PASS" for row in rows),
            cycle_parser_passes=sum(cycle.get("parser_gate")=="PASS" for row in rows for cycle in row.get("cycles",[])),
            formalization_versions=sum(cycle.get("parser_gate") in {"PASS","FAIL"} for row in rows for cycle in row.get("cycles",[])),
            audit_calls_skipped=sum(row.get("audit_calls_skipped",0) for row in rows),
            tool_gate_passes=sum(row.get("tool_gate")=="PASS" for row in rows),
            tool_invocations=sum(row.get("tool_invocations",0) for row in rows),
            exact_supports=sum(row.get("exact_verified") is True for row in rows),
            failed_workers=sum(row["state"]=="failed_closed" for row in rows))
        rewrite.write_record(output/"status.json",status)
        if not live:
            rewrite.write_record(output/"result.json",status)
            return status
        time.sleep(5)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-acquisition",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--master-seed",type=int,required=True)
    parser.add_argument("--batch-size",type=int,default=8)
    parser.add_argument("--auditor",choices=("gemma","qwen"),default="gemma")
    parser.add_argument("--execute-models",action="store_true")
    parser.add_argument("--cycles",type=int,default=3)
    parser.add_argument("--domain-ledger",action="store_true")
    parser.add_argument("--formalizer-temperatures",type=float,nargs="+")
    parser.add_argument("--after-batch",type=Path)
    args=parser.parse_args()
    if args.after_batch:
        if not args.execute_models:
            parser.error("--after-batch requires --execute-models")
        wait_for_batch(args.after_batch,args.output_dir)
    print(json.dumps(run(args.source_acquisition,args.output_dir,args.master_seed,args.batch_size,
        args.execute_models,auditor=args.auditor,cycles=args.cycles,domain_ledger=args.domain_ledger,
        formalizer_temperatures=args.formalizer_temperatures),indent=2),flush=True)


if __name__ == "__main__":
    main()
