"""Isolated deterministic execution of whitelisted mathematical operations."""

from __future__ import annotations

import hashlib
import inspect
import multiprocessing
import queue
import resource
import time
import traceback
from pathlib import Path
from typing import Any, Mapping

from .registry import Capability, CapabilityRegistry, default_registry
from .arguments import validate_operation_arguments
from .schemas import (
    EvidenceStatus,
    answers_equivalent,
    operation_hash,
    validate_evidence,
    validate_tool_plan,
)


def _source_hash(value: Any) -> str:
    try:
        path = Path(inspect.getsourcefile(value) or "")
        payload = path.read_bytes()
    except (OSError, TypeError):
        payload = inspect.getsource(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _execute_in_child(
    capability: Capability,
    arguments: dict[str, Any],
    memory_limit_mb: int,
    output: multiprocessing.queues.Queue,
) -> None:
    try:
        # A forked worker inherits the parent's mapped dataset/tokenizer pages.
        # Limit *additional* virtual memory rather than setting a ceiling below
        # memory that already exists at worker start.
        page_size = resource.getpagesize()
        with open("/proc/self/statm", "r", encoding="ascii") as handle:
            current_virtual_bytes = int(handle.read().split()[0]) * page_size
        memory_bytes = current_virtual_bytes + int(memory_limit_mb) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        output.put({"ok": True, "result": capability.execute(arguments)})
    except BaseException as exc:
        output.put(
            {
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(limit=8),
            }
        )


class ToolExecutor:
    """Execute only registered operations and emit validator-gated evidence."""

    def __init__(
        self,
        registry: CapabilityRegistry | None = None,
        *,
        max_timeout_sec: int = 120,
        max_memory_limit_mb: int = 2048,
    ) -> None:
        self.registry = registry or default_registry()
        self.max_timeout_sec = max_timeout_sec
        self.max_memory_limit_mb = max_memory_limit_mb

    def execute(self, plan_value: Mapping[str, Any], *, checked_claim: str) -> dict[str, Any]:
        plan = validate_tool_plan(
            plan_value,
            registered_operations=self.registry.operations,
            max_timeout_sec=self.max_timeout_sec,
            max_memory_limit_mb=self.max_memory_limit_mb,
        )
        capability = self.registry.get(plan["operation"])
        if plan["backend_capability"] != capability.backend_capability:
            raise ValueError(
                "tool plan backend_capability does not match the registered operation"
            )
        if plan["validator"] != capability.validator_name:
            raise ValueError(
                "tool plan validator does not match the registered operation"
            )
        plan["arguments"] = (
            capability.validate_arguments(dict(plan["arguments"]))
            if capability.validate_arguments is not None
            else validate_operation_arguments(plan["operation"], plan["arguments"])
        )
        op_hash = operation_hash(
            plan,
            backend_version=capability.backend_version,
            validator_version=capability.validator_version,
        )
        executor_hash = _source_hash(capability.execute)
        validator_hash = _source_hash(capability.validate)
        started = time.monotonic()
        result: dict[str, Any] | None = None
        failure: dict[str, Any] | None = None
        context = multiprocessing.get_context("fork")
        output = context.Queue(maxsize=1)
        process = context.Process(
            target=_execute_in_child,
            args=(
                capability,
                dict(plan["arguments"]),
                int(plan["memory_limit_mb"]),
                output,
            ),
        )
        process.start()
        process.join(float(plan["timeout_sec"]))
        if process.is_alive():
            process.terminate()
            process.join(5)
            failure = {
                "reason": "timeout",
                "timeout_sec": plan["timeout_sec"],
            }
        else:
            try:
                message = output.get_nowait()
            except queue.Empty:
                message = {
                    "ok": False,
                    "error_type": "MissingWorkerResult",
                    "error": f"worker exited with code {process.exitcode}",
                }
            if message.get("ok"):
                result = dict(message["result"])
            else:
                failure = {
                    "reason": "backend_error",
                    "error_type": message.get("error_type"),
                    "error": message.get("error"),
                }
        output.close()
        runtime = time.monotonic() - started

        if result is None:
            return validate_evidence(
                {
                    "run_id": plan["run_id"],
                    "problem_id": plan["problem_id"],
                    "claim_id": plan["claim_id"],
                    "status": EvidenceStatus.UNKNOWN.value,
                    "checked_claim": checked_claim,
                    "normalized_result": {},
                    "certificate": {"failure": failure},
                    "counterexample": None,
                    "backend": capability.backend_capability,
                    "backend_version": capability.backend_version,
                    "operation_hash": op_hash,
                    "executor_code_hash": executor_hash,
                    "validator_code_hash": validator_hash,
                    "runtime_sec": runtime,
                    "validation_status": "not_run",
                    "validator": capability.validator_name,
                    "validator_version": capability.validator_version,
                    "operation": plan["operation"],
                }
            )

        try:
            validation = capability.validate(dict(plan["arguments"]), result)
        except BaseException as exc:
            validation = {
                "passed": False,
                "details": {
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            }
        validation_passed = bool(validation.get("passed"))
        claimed_answer = plan["arguments"].get("claimed_answer")
        derived_answer = result.get("derived_answer")
        if not validation_passed:
            status = EvidenceStatus.UNKNOWN.value
            validation_status = "failed"
        elif (
            claimed_answer is not None
            and derived_answer is not None
            and not answers_equivalent(claimed_answer, derived_answer)
        ):
            status = EvidenceStatus.REFUTED.value
            validation_status = "passed"
        else:
            status = EvidenceStatus.VERIFIED.value
            validation_status = "passed"
        counterexample = result.get("counterexample")
        if status == EvidenceStatus.REFUTED.value and counterexample is None:
            counterexample = {
                "claimed_answer": str(claimed_answer),
                "derived_answer": str(derived_answer),
            }
        certificate = dict(result.get("certificate") or {})
        certificate["validator"] = validation
        evidence = {
            "run_id": plan["run_id"],
            "problem_id": plan["problem_id"],
            "claim_id": plan["claim_id"],
            "status": status,
            "checked_claim": result.get("checked_claim") or checked_claim,
            "normalized_result": result.get("normalized_result") or {},
            "certificate": certificate,
            "counterexample": counterexample,
            "backend": capability.backend_capability,
            "backend_version": capability.backend_version,
            "operation_hash": op_hash,
            "executor_code_hash": executor_hash,
            "validator_code_hash": validator_hash,
            "runtime_sec": runtime,
            "validation_status": validation_status,
            "validator": capability.validator_name,
            "validator_version": capability.validator_version,
            "operation": plan["operation"],
            "derived_answer": derived_answer,
        }
        return validate_evidence(evidence)
