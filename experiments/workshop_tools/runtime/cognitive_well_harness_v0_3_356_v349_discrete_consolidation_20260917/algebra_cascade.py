"""One accepted formalization, sequential algebra backends, first verified exit.

The orchestrator does not author mathematics or reinterpret model decisions.
Backend screens cannot invoke proof rewriting without a request-bound verifier.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import copy

from . import backend_comparison as backends


@dataclass(frozen=True)
class Operations:
    division: Callable
    radical: Callable
    laurent: Callable
    verify: Callable
    rewrite: Callable


def execute(request,output,*,admission,operations):
    """Run exactly the requested cascade; callbacks are deterministic except rewrite.

    Backend callbacks receive independent copies of the same immutable source.
    Radical's third argument is None for the source, or a bound Laurent preview.
    Verification returns verified=true only with an original-source certificate.
    """
    digest=backends.division.exact_tools.stable_hash(request)
    if (admission.get("parser")!="PASS" or admission.get("semantic")!="ACCEPT"
        or admission.get("request_sha256")!=digest):
        raise ValueError("cascade requires parser and semantic acceptance of the same request")
    # Compile the typed input and guards before invoking any backend.
    backends.division.initial(request)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    backends.write(output/"request.json",request)
    status={"state":"running","request_sha256":digest,"admission":admission,
        "backend_order":["laurent","laurent_guarded_radical","guarded_radical","division"],
        "model_calls_between_backends":0,"stages":[],"exact_verified":False,
        "proof_rewrite_started":False,"verdict":"INCONCLUSIVE"}

    def record():
        backends.write(output/"status.json",status)

    def call(stage,function,*extra):
        status.update(stage=stage)
        record()
        mutable=copy.deepcopy(request)
        result=function(mutable,output/stage,*extra)
        if backends.division.exact_tools.stable_hash(mutable)!=digest:
            raise ValueError("backend mutated the accepted formalization")
        status["stages"].append({"stage":stage,"result":result})
        record()
        if result.get("state") in {"error","failed_closed"}:
            raise ValueError(f"{stage} reported a mechanical or integrity failure")
        return result

    def finish_candidate(stage,result,preview=None):
        if result.get("outcome")!="PROVED":
            return False
        status.update(stage=stage+"_verification")
        record()
        verification=operations.verify(copy.deepcopy(request),stage,result,preview,output/(stage+"_verification"))
        status["stages"].append({"stage":stage+"_verification","result":verification})
        if verification.get("verified") is not True:
            if verification.get("state") in {"error","failed_closed"}:
                raise ValueError("candidate certificate failed integrity verification")
            status["unverified_positive_seen"]=True
            record()
            return False
        if (verification.get("request_sha256")!=digest or verification.get("scope")!="original_target"
            or (preview is not None and verification.get("laurent_lift_verified") is not True)):
            raise ValueError("verified evidence does not bind the original target and its lift")
        status.update(exact_verified=True,verdict="VERIFIED_SUPPORT",selected_stage=stage,
                      stage="proof_rewrite",proof_rewrite_started=True)
        record()
        # Synchronous immediate handoff: no later backend or sample-selection wait.
        rewritten=operations.rewrite(copy.deepcopy(request),verification,output/"proof_rewrite")
        status.update(state="completed",stage="finished",rewrite_result=rewritten)
        record()
        backends.write(output/"result.json",status)
        return True

    try:
        preview=call("laurent",operations.laurent)
        if preview.get("outcome")=="REDUCED":
            if preview.get("request_sha256")!=digest:
                raise ValueError("Laurent preview binds a different formalization")
            last=call("laurent_guarded_radical",operations.radical,preview)
            if finish_candidate("laurent_guarded_radical",last,preview):
                return status
        elif preview.get("outcome") not in {"UNAVAILABLE","TIMEOUT","NOT_REDUCED"}:
            raise ValueError("unexpected Laurent reduction outcome")
        second=call("guarded_radical",operations.radical,None)
        if finish_candidate("guarded_radical",second):
            return status
        last=call("division",operations.division)
        if finish_candidate("division",last):
            return status
        status.update(state="completed",stage="certificate_pending" if status.get("unverified_positive_seen") else "inconclusive",
                      verdict="CERTIFICATION_REQUIRED" if status.get("unverified_positive_seen") else "INCONCLUSIVE")
    except Exception as error:
        status.update(state="failed_closed",error=f"{type(error).__name__}: {error}")
    record()
    backends.write(output/"result.json",status)
    return status
