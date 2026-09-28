"""Model formalization -> one bounded division-tool call; no later proof stages."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

from . import pipeline, certificate, rewrite
from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906 import pipeline as formal


STAGE = "model_guarded_division_formalization"
SYSTEM = """You are a mathematical formalizer with access to one exact algebra tool.
Read the original theorem, proof, and recorded gap. Decide whether to call the tool
and author all of its mathematical inputs yourself. The old proof and recorded gap
are untrusted: verify the equations you use from the original hypotheses.

The available backend takes polynomial equations, a polynomial target, and typed
nonzero conditions. Internally it substitutes variables from linear equations only
when their coefficients are provably nonzero from your guards; normalizes the
resulting rational expressions; and divides the target numerator by the remaining
polynomials. It returns quotients and an independently re-expanded certificate, or
INCONCLUSIVE. It does not construct a Groebner basis or use Laurent transformations.

Choose a small justified representation suited to substitutions and division. You
may derive rational parameters, eliminate definitions, and clear denominators, but
must explain every symbol, retained equation, target correspondence, and nonzero
condition. Size never licenses changing the claim or dropping needed hypotheses.
No representation, example solution, or successful certificate is provided.
Never assert the desired identity as an input equation or invent guards to force
success. The exact calculation cannot certify your semantic interpretation.

Emit Markdown only, never JSON or executable code. For a tool call, begin with
# Decision followed by CALL_TOOL, then the formalization sections prescribed in
the user contract (including Domain Ledger when requested).
If you cannot obtain a faithful encoding, output exactly # Decision with NO_TOOL,
then # Reason with a short explanation. Do not guess a tool result.
"""


def parse_proposal(text, *, domain_inputs=None, require_domain_ledger=False):
    """Ignore section spacing, never infer or rewrite a model decision or math."""
    lines=[]
    headings=[]
    inside_fence=False
    for line in text.replace("\r\n", "\n").strip().splitlines():
        if line.startswith("```"):
            inside_fence=not inside_fence
        if not inside_fence and line.startswith("# "):
            line=line.rstrip(" \t")
            headings.append(line[2:])
        lines.append(line)
    call_headings=["Decision", "Semantic Bindings", "Guard Program", "Tool Arguments"]
    ledger_headings=["Decision", "Semantic Bindings", "Domain Ledger", "Guard Program", "Tool Arguments"]
    no_tool_headings=["Decision", "Reason"]
    if headings not in (call_headings, ledger_headings, no_tool_headings):
        raise ValueError("expected exactly the ordered Decision/formalization or Decision/Reason sections")
    sections=formal.mdp.exact_sections("\n".join(lines), headings)
    decision=sections["Decision"]
    if decision not in {"CALL_TOOL", "NO_TOOL"}:
        raise ValueError("Decision must contain exactly CALL_TOOL or NO_TOOL")
    if decision == "NO_TOOL":
        if headings != no_tool_headings:
            raise ValueError("NO_TOOL requires only Decision and Reason sections")
        return {"call_requested":False, "reason":sections["Reason"]}
    if headings not in (call_headings, ledger_headings):
        raise ValueError("CALL_TOOL requires the three formalization sections")
    if require_domain_ledger and headings != ledger_headings:
        raise ValueError("CALL_TOOL requires Domain Ledger between Semantic Bindings and Guard Program")
    # Only section boundaries are canonicalized; typed bodies retain their text.
    body="\n\n".join(f"# {heading}\n\n{sections[heading]}" for heading in call_headings[1:])
    parsed={"call_requested":True, **formal.parse_guarded_formalization(body)}
    if headings == ledger_headings:
        from . import domain_ledger
        program,report=domain_ledger.compile_ledger(sections["Domain Ledger"],parsed["arguments"],
            parsed["guard_program"],domain_inputs)
        parsed.update(guard_program=program,domain_compilation=report)
        parsed["derived_guard_records"]=formal.transformation_validation.derive_guards(
            program,parsed["arguments"])["records"]
        normalized=formal.mdp.exact_sections(parsed["normalized_markdown"],call_headings[1:])
        normalized["Domain Ledger"]=sections["Domain Ledger"]
        parsed["normalized_markdown"]="\n\n".join(f"# {h}\n\n{normalized[h]}" for h in ledger_headings[1:])
        parsed["canonical_formalization_sha256"]=pipeline.base.sha256_text(parsed["normalized_markdown"])
    return parsed


def invoke_tool(parsed, output, timeout=60):
    """One bounded worker invocation, shared by fresh and audit-repair tests."""
    output.mkdir(parents=True, exist_ok=False)
    request_path=output/"request.json"
    if "domain_compilation" in parsed:
        report=parsed["domain_compilation"]
        if not report["source_bound"] or report["compiled_guard_program_sha256"] != pipeline.exact_tools.stable_hash(parsed["guard_program"]):
            raise ValueError("compiled domain guard binding mismatch")
        rewrite.write_record(output/"domain_compilation.json",report)
    rewrite.write_record(request_path,{"arguments":parsed["arguments"],"guard_program":parsed["guard_program"]})
    with (output/"worker.log").open("w") as log:
        try:
            completed=subprocess.run([sys.executable,"-B","-m",
                "cognitive_well_harness_v0_3_343_real_root_classification_20260916.rational_division",
                "--request",str(request_path),"--output",str(output/"result.json")],
                cwd=Path(__file__).resolve().parents[1],stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"verdict":"INCONCLUSIVE","exact_verified":False,
                    "reason":f"algebra tool exceeded {timeout} seconds"}
    if completed.returncode:
        raise RuntimeError(f"algebra worker exited {completed.returncode}; inspect worker.log")
    result=json.loads((output/"result.json").read_text())
    pipeline.base.write_text(output/"certificate.md",result["markdown"])
    return {"verdict":result["verdict"],"exact_verified":result["verified"],
            "source_size":result["source_size"],"reduced_size":result["reduced_size"],
            "tool_elapsed_seconds":result["elapsed_seconds"]}


def validate_temperature(value):
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("formalizer temperature must be finite and between 0 and 1")
    return value


def run(source, output, seed, execute, *, domain_ledger=False, formalizer_temperature=0.1):
    validate_temperature(formalizer_temperature)
    source,output=source.resolve(),output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    saved=json.loads((source/"manifest.json").read_text())
    problem=formal.v0220.load_problem(Path(saved["problem_file"]))
    proof=Path(saved["resolver1_proof"]).read_text().strip()
    if pipeline.base.sha256_file(problem.source_path)!=saved["problem_file_sha256"] or pipeline.base.sha256_text(proof)!=saved["resolver1_proof_sha256"]:
        raise ValueError("original theorem/proof binding mismatch")
    if (source/"input/original_theorem.md").read_text().strip()!=problem.statement or (source/"input/resolver1_proof.md").read_text().strip()!=proof:
        raise ValueError("saved source text mismatch")
    detection_text=(source/"01_detection/detection.md").read_text().strip()
    matcher_text=(source/"02_matcher/matcher.md").read_text().strip()
    detection=formal.protocol.parse_detection(detection_text)
    matcher=pipeline.base._parse_matcher(matcher_text,detection["desired_exact_fact"])
    if not detection["call_requested"] or not matcher["call_requested"] or matcher["operation"]!=pipeline.exact_tools.IDEAL_OPERATION:
        raise ValueError("source does not record this algebraic consequence request")
    for name,text in {"theorem.md":problem.statement,"source_proof.md":proof,
                      "detection.md":detection_text,"matcher.md":matcher_text}.items():
        pipeline.base.write_text(output/"input"/name,text)
    user=formal.formalization_prompt(problem,proof,detection,matcher)
    user += "\n\nBegin with # Decision and CALL_TOOL before the three sections, or use the NO_TOOL format. The backend is guarded rational substitution and polynomial division only.\n"
    if domain_ledger:
        from .domain_ledger import CONTRACT, VERSION
        # Insert into the existing contract instead of appending a conflicting format.
        user=user.replace("# Guard Program\n",CONTRACT+"\n# Guard Program\n",1)
        user=user.replace("Emit the three top-level output sections exactly.","Emit the prescribed top-level sections exactly.")
        user=user.replace("before the three sections", "before the four sections (including Domain Ledger)")
    role=pipeline.base.Role("http://127.0.0.1:8030/v1",pipeline.base.DEFAULT_GEMMA_MODEL,formalizer_temperature,"max")
    status={"state":"prepared","stage":"formalization","problem_id":problem.problem_id,
            "source":str(source),"master_seed":seed,"model":asdict(role),
            "backend":"guarded_rational_substitution_polynomial_division_v1",
            "max_logical_model_stages":1,"token_caps":[32768,49152],"thinking_token_budget":16384,
            "mandatory_budget_forcing":True,"max_tool_invocations":1,"tool_timeout_seconds":60,
            "model_output":"Markdown","human_mathematical_hints":False,
            "semantic_audit":"NOT_RUN","proof_synthesis":"NOT_RUN","strict_scoring":"NOT_RUN",
            "domain_ledger_enabled":domain_ledger,
            "domain_ledger_version":VERSION if domain_ledger else None,
            "theorem_sha256":pipeline.base.sha256_text(problem.statement),
            "proof_sha256":pipeline.base.sha256_text(proof),"prompt_characters":len(SYSTEM)+len(user)}
    rewrite.write_record(output/"manifest.json",status)
    pipeline.base.write_text(output/"formalizer_system.md",SYSTEM)
    pipeline.base.write_text(output/"formalizer_user.md",user)
    if not execute:
        rewrite.write_record(output/"status.json",status)
        return status
    try:
        status.update(state="running")
        rewrite.write_record(output/"status.json",status)
        caller=rewrite.BudgetedCalls(output/"model_budget.json",max_stages=1)
        text,parsed,call=caller(role=role,system_prompt=SYSTEM,user_prompt=user,
            destination=output/"01_formalization/model",stage=STAGE,master_seed=seed,
            parser=lambda text:parse_proposal(text,domain_inputs={"theorem.md":problem.statement,"source_proof.md":proof},
                                             require_domain_ledger=domain_ledger))
        certificate.validate_markdown_budget_forcing(call,expected_stage=STAGE,
            expected_model=role.model,canonical_markdown=text)
        pipeline.base.write_text(output/"01_formalization/model_output.md",text)
        rewrite.write_record(output/"01_formalization/call.json",call)
        if not parsed["call_requested"]:
            status.update(state="completed",stage="model_declined_tool",reason=parsed["reason"],tool_invocations=0)
        else:
            pipeline.base.write_text(output/"01_formalization/formalization.md",parsed["normalized_markdown"])
            status.update(stage="algebra_tool",tool_invocations=1,
                variables=len(parsed["arguments"]["symbols"]),generators=len(parsed["arguments"]["generators"]))
            rewrite.write_record(output/"status.json",status)
            status.update(state="completed",stage="finished",**invoke_tool(parsed,output/"02_tool"))
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
        pipeline.base.write_text(output/"error.txt",traceback.format_exc())
    rewrite.write_record(output/"status.json",status)
    rewrite.write_record(output/"result.json",status)
    return status


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-acquisition",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--master-seed",type=int,required=True)
    parser.add_argument("--execute-models",action="store_true")
    args=parser.parse_args()
    print(json.dumps(run(args.source_acquisition,args.output_dir,args.master_seed,args.execute_models),indent=2),flush=True)


if __name__=="__main__":
    main()
