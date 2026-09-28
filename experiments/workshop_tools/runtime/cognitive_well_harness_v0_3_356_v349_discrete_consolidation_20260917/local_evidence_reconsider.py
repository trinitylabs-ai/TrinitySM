"""Resume only a timed-out reconsideration from its saved complete first response."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import traceback

from . import local_evidence_experiment as pilot

base=pilot.base
bf=pilot.rewrite.pipeline.mandatory_budget_forcing
STAGE="local_evidence_proof_rewrite"


def prepare(source,timeout):
    if not isinstance(timeout,int) or not 1<=timeout<=3600:
        raise ValueError("response timeout must be 1..3600 seconds")
    inputs,evidence_root,prompt=pilot.load_evidence(source)
    status=json.loads((source/"status.json").read_text())
    if status["state"]!="failed_closed" or status["stage"]!="proof_rewrite" or "TimeoutError" not in status.get("error",""):
        raise ValueError("source must be stopped after a rewrite transport timeout")
    matches=sorted((source/"rewrite/model").glob("attempt_*"))
    if not matches: raise ValueError("source has no rewrite attempt")
    root=matches[-1]
    if (root/f"{STAGE}.budget_forcing.json").exists():
        raise ValueError("cannot resample an already completed forced response")
    suffixes=(".prompt.txt",".user_prompt.txt",".raw_response.json",".metadata.json",".reasoning.txt")
    files={suffix:root/f"{STAGE}.pre_budget_forcing{suffix}" for suffix in suffixes}
    if any(not path.is_file() for path in files.values()):
        raise ValueError("saved complete primary response is missing")
    metadata=json.loads(files[".metadata.json"].read_text())
    raw=json.loads(files[".raw_response.json"].read_text())
    system=files[".prompt.txt"].read_text()
    user=files[".user_prompt.txt"].read_text()
    message=raw["choices"][0]["message"]
    text=str(message.get("content") or "").strip()
    reasoning=str(message.get("reasoning_content") or message.get("reasoning") or "").strip()
    if (metadata["stage"]!=STAGE or metadata["model"]!=status["rewriter"]["model"]
            or metadata["endpoint"]!=status["rewriter"]["endpoint"] or metadata["continuation"]
            or metadata["finish_reason"]!="stop" or raw["choices"][0]["finish_reason"]!="stop"
            or raw["id"]!=metadata["response_id"] or not text):
        raise ValueError("saved primary response provenance mismatch")
    if reasoning!=files[".reasoning.txt"].read_text().strip():
        raise ValueError("saved primary reasoning changed")
    if system!=pilot.REWRITE_SYSTEM or user.strip()!=prompt.strip():
        raise ValueError("saved rewrite prompts differ from the bound evidence")
    if metadata["prompt_sha256"]!=base.sha256_text(system) or metadata["user_prompt_sha256"]!=base.sha256_text(user):
        raise ValueError("saved prompt hash mismatch")
    original=bf.transport.HTTPGenerationConfig(**metadata["config"])
    request=bf.transport.openai_chat_request(model=metadata["model"],prompt=system,user_prompt=user,config=original)
    request_hash=base.sha256_text(json.dumps(request,ensure_ascii=False))
    if request_hash!=metadata["request_sha256"]:
        raise ValueError("saved generation parameters changed")
    if original.response_format is not None or original.structured_outputs is not None:
        raise ValueError("recovery requires Markdown output")
    primary={"text":text,"reasoning":reasoning,"metadata":metadata}
    return {"inputs":inputs,"evidence_root":evidence_root,"files":files,"primary":primary,
        "system":system,"user":user,"config":replace(original,timeout_seconds=timeout),
        "attempt":int(root.name.split("_")[1]),"cap":original.max_tokens,
        "role":base.Role(metadata["endpoint"],metadata["model"],original.temperature,original.reasoning_effort)}


def run(source,output,timeout=900,*,continuation=None,audit_caller=None):
    prepared=prepare(source,timeout)
    output.mkdir(parents=True,exist_ok=False)
    model_root=output/"rewrite/model"/f"attempt_{prepared['attempt']:02d}_cap_{prepared['cap']}"
    for suffix,path in prepared["files"].items():
        base.write_text(model_root/f"{STAGE}{suffix}",path.read_text())
    for name,value in prepared["inputs"].items(): base.write_text(output/"input"/name,value)
    gemma=base.Role("http://127.0.0.1:8030/v1",base.DEFAULT_GEMMA_MODEL,0.1,"max")
    status={"state":"running","stage":"rewrite_reconsideration","source_run":str(source),
        "rewriter":asdict(prepared["role"]),"request_timeout_sec":timeout,
        "generation_config":asdict(prepared["config"]),"primary_generation_reused":True,
        "fresh_formalization_calls":0,"fresh_semantic_audit_calls":0,"tool_invocations":0,
        "max_reconsideration_requests":1,"max_proof_audit_stages":1,"model_output":"Markdown",
        "source_primary_sha256":{suffix:base.sha256_file(path) for suffix,path in prepared["files"].items()},
        "strict_score":"NOT_RUN","whole_proof_independently_certified":False}
    pilot.write(output/"manifest.json",status);pilot.write(output/"status.json",status)
    continuation=continuation or bf._continue_primary
    try:
        forced=continuation(primary=prepared["primary"],reused_primary=True,
            kwargs={"endpoint":prepared["role"].endpoint,"model":prepared["role"].model,
                "prompt":prepared["system"],"user_prompt":prepared["user"],"output_dir":model_root,
                "stage":STAGE,"config":prepared["config"]})
        text=forced["text"].strip()
        record={"attempt":prepared["attempt"],"cap":prepared["cap"],"request_timeout_sec":timeout,
                "metadata":forced["metadata"],"saved_primary_reused":True}
        pilot.certificate.validate_markdown_budget_forcing(record,expected_stage=STAGE,
            expected_model=prepared["role"].model,canonical_markdown=text,expected_timeout_sec=timeout)
        if forced["metadata"].get("finish_reason")!="stop": raise ValueError("reconsideration did not finish normally")
        parts=pilot.parse_rewrite(text)
        base.write_text(output/"rewrite/output.md",text);pilot.write(output/"rewrite/call.json",record)
        audit_caller=audit_caller or pilot.rewrite.BudgetedCalls(output/"audit_model_budget.json",max_stages=1)
        def call(role,system,user,root,stage,parser,index):
            if stage==STAGE: return text,parts
            if len(system)+len(user)>80000: raise ValueError("proof audit prompt exceeds its bound")
            answer,parsed,call_record=audit_caller(role=role,system_prompt=system,user_prompt=user,
                destination=root/"model",stage=stage,master_seed=prepared["config"].seed+index,
                parser=parser,request_timeout_sec=timeout)
            pilot.certificate.validate_markdown_budget_forcing(call_record,expected_stage=stage,
                expected_model=role.model,canonical_markdown=answer,expected_timeout_sec=timeout)
            base.write_text(root/"output.md",answer);pilot.write(root/"call.json",call_record)
            return answer,parsed
        pilot.finish_rewrite(call,prepared["role"],gemma,prepared["user"],output,status)
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        base.write_text(output/"error.txt",traceback.format_exc())
    pilot.write(output/"status.json",status);pilot.write(output/"result.json",status)
    return status


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--request-timeout-sec",type=int,default=900)
    args=parser.parse_args()
    print(json.dumps(run(args.source_run.resolve(),args.output.resolve(),args.request_timeout_sec)),flush=True)


if __name__=="__main__": main()
