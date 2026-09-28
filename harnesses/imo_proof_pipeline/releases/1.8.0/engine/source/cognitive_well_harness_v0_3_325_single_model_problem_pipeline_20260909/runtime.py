"""One explicit model/endpoint; real unforced provenance, never fake BF events."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
import hashlib
import json
import sys
import threading

from experiments.local_math_verifier import runtime as transport

# Import this module BEFORE the historical harness installs transport wrappers.
# Historical wrappers rewrite callable module globals by identity. Keep the
# genuine transport inside a container so importing them cannot mutate it.
_PRISTINE_TRANSPORT = (transport.run_openai_chat_generation,)
SCHEMA = "single_model_unforced_v1"
CURRENT = None
_slots = threading.BoundedSemaphore(4)
_lock = threading.Lock()
_calls = []


@dataclass(frozen=True)
class Policy:
    model: str
    endpoint: str
    reasoning_effort: str = "xhigh"
    timeout_seconds: int = 14400
    output_root: Path | None = None


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n")
    temporary.replace(path)


def active():
    return CURRENT is not None


def effective_model(legacy_model):
    return CURRENT.model if active() else legacy_model


def validate_unforced(metadata,text):
    """Validate the declared alternative policy instead of relaxing BF checks."""
    if not active():
        raise ValueError("unforced producer requires an explicit active execution policy")
    config=metadata.get("config",{})
    event=metadata.get("single_model_policy",{})
    if (metadata.get("model")!=CURRENT.model or metadata.get("endpoint")!=CURRENT.endpoint
        or config.get("reasoning_effort")!=CURRENT.reasoning_effort
        or config.get("thinking_enabled") is not True
        or config.get("thinking_token_budget") is not None
        or config.get("response_format") is not None or config.get("structured_outputs") is not None
        or metadata.get("continuation") is not False
        or metadata.get("prior_generation_sha256") is not None
        or any("budget_forcing" in key for key in metadata)
        or event.get("schema")!=SCHEMA or event.get("budget_forcing") is not False
        or event.get("text_sha256")!=digest(text.strip())):
        raise ValueError("single-model unforced producer policy mismatch")
    return event


def governed(**kwargs):
    if not active():
        raise ValueError("single-model transport is not configured")
    kwargs=dict(kwargs)
    config=kwargs["config"]
    if config.response_format is not None or config.structured_outputs is not None:
        raise ValueError("single-model experiment forbids structured/JSON model outputs")
    if kwargs.get("prior_generation") or kwargs.get("continuation_instruction"):
        raise ValueError("same-trace continuation is disabled; use a fresh bounded parser repair")
    original_role=kwargs["model"]
    kwargs.update(model=CURRENT.model,endpoint=CURRENT.endpoint,
                  config=replace(config,reasoning_effort=CURRENT.reasoning_effort,
                                 thinking_enabled=True,thinking_token_budget=None,
                                 timeout_seconds=CURRENT.timeout_seconds))
    with _lock:
        row={"stage":kwargs["stage"],"output_dir":str(kwargs["output_dir"]),
             "legacy_role_model":original_role,"model":CURRENT.model,"endpoint":CURRENT.endpoint,
             "reasoning_effort":CURRENT.reasoning_effort,"budget_forcing":False,
             "max_tokens":kwargs["config"].max_tokens,"temperature":kwargs["config"].temperature,
             "seed":kwargs["config"].seed,"state":"running"}
        _calls.append(row)
        if CURRENT.output_root:
            write(CURRENT.output_root/"model_calls.json",{"policy":SCHEMA,"calls":_calls})
    try:
        with _slots:
            result=_PRISTINE_TRANSPORT[0](**kwargs)
        metadata=result["metadata"]
        if any("budget_forcing" in key for key in metadata) or metadata.get("continuation"):
            raise ValueError("unexpected forcing or continuation reached pristine transport")
        event={"schema":SCHEMA,"budget_forcing":False,"model":CURRENT.model,
               "endpoint":CURRENT.endpoint,"reasoning_effort":CURRENT.reasoning_effort,
               "text_sha256":digest(str(result.get("text","")).strip()),
               "stage":kwargs["stage"],"legacy_role_model":original_role}
        metadata["single_model_policy"]=event
        validate_unforced(metadata,str(result.get("text","")))
        root=Path(kwargs["output_dir"])
        write(root/f"{kwargs['stage']}.generation_policy.json",event)
        write(root/f"{kwargs['stage']}.metadata.json",metadata)
        with _lock:
            row.update(state="completed",response_id=metadata.get("response_id"),
                       usage=metadata.get("usage"),finish_reason=metadata.get("finish_reason"))
        return result
    except Exception as error:
        with _lock:
            row.update(state="failed",error=f"{type(error).__name__}: {error}")
        raise
    finally:
        with _lock:
            if CURRENT.output_root:
                write(CURRENT.output_root/"model_calls.json",{"policy":SCHEMA,"calls":_calls})


def install(policy):
    global CURRENT
    if _PRISTINE_TRANSPORT[0].__module__!="experiments.local_math_verifier.runtime":
        raise ValueError("single-model runtime was imported after a transport wrapper")
    if CURRENT is not None and CURRENT!=policy:
        raise ValueError("one execution policy per process")
    CURRENT=policy
    changed=[]
    for name,module in list(sys.modules.items()):
        if module is None or name==__name__ or not name.startswith(("cognitive_well_harness_","experiments.local_math_verifier")):
            continue
        for key,value in list(vars(module).items()):
            if key=="run_openai_chat_generation":
                setattr(module,key,governed)
                changed.append(name+"."+key)
    transport.run_openai_chat_generation=governed
    return changed
