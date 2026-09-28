from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
    pipeline as v274,
    protocol as v274_protocol,
)
import scripts.run_v0220_gemma_global_tool_budget_20260904 as v0220
import scripts.run_v0221_gemma_constrained_tool_router_budget_20260904 as v0221
import scripts.v0236_markdown_protocol as mdp


QWEN_MODEL = "Qwen/Qwen3.6-27B"
GEMMA_MODEL = "google/gemma-4-31B-it"
ALLOWED_OPERATIONS = tuple(exact_tools.LEGACY_OPERATIONS)


NOMINATOR_SYSTEM_PROMPT = r"""You are a problem-agnostic exact-evidence nominator
for an adversarial audit of a proposed Olympiad proof repair. Inspect the original
problem, submitted proof, Fusion defect packet, and proposed repair brief. Select at
most one atomic implication whose truth or falsity can be decided by one allowlisted
exact operation. Prefer a counterexample search when the brief asserts a universal
step over a genuinely finite domain. Do not invent premises, shrink an infinite
domain to samples, or claim a tool result. If no operation exactly fits, choose
NO_TOOL.

Emit only the strict four-section Markdown record:

# Decision

CALL_TOOL or NO_TOOL

# Operation

one allowlisted operation, or none

# Immutable Claim

the exact neutral fact to compute, or NONE

# Fit Rationale

one paragraph identifying the precise local implication and exact scope

No JSON, code, paths, results, or extra headings."""


SEMANTIC_AUDITOR_SYSTEM_PROMPT = v274.SEMANTIC_AUDITOR_SYSTEM + r"""

The requested computation is optional audit evidence for one local implication in a
repair brief. Reject any finite search presented as proof of an infinite or global
claim. The absence of a counterexample proves nothing beyond an exhaustively encoded
finite domain. Do not use request size or expected outcome as a reason to accept."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _safe_label(value: str) -> str:
    label = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return label[:120] or "audit"


def operation_catalog() -> str:
    full = v274.operation_catalog().splitlines()
    allowed = set(ALLOWED_OPERATIONS)
    return "\n".join(
        line for line in full if line.startswith("- ") and line[2:].split(":", 1)[0] in allowed
    )


def _parse_nomination(text: str) -> dict[str, Any]:
    normalized, normalization = v274_protocol.normalize_matcher(
        text, allowed_operations=ALLOWED_OPERATIONS
    )
    parsed = mdp.parse_matcher(normalized, ALLOWED_OPERATIONS)
    parsed["valid"] = True
    parsed["errors"] = []
    parsed["normalized_markdown"] = normalized
    parsed["normalization"] = normalization
    return parsed


def _parse_compilation(text: str, operation: str) -> dict[str, Any]:
    normalized, normalization = v274_protocol.normalize_compilation(text, operation)
    parsed = v274_protocol.parse_compilation(normalized, operation)
    parsed["arguments"] = v0221.validate_operation_arguments(
        operation, parsed["arguments"]
    )
    parsed["valid"] = True
    parsed["errors"] = []
    parsed["normalized_markdown"] = normalized
    parsed["normalization"] = normalization
    return parsed


def _parse_semantic_audit(text: str) -> dict[str, Any]:
    # The inherited parser raises on malformed Markdown, but does not return the
    # syntax-validity flag required by default_markdown_call. A parsed REJECT is
    # a valid model decision, not grounds for another generation.
    parsed = v274_protocol.parse_semantic_audit(text)
    return {**parsed, "valid": True, "errors": []}


def nomination_prompt(
    *, problem: str, proof: str, defect_packet: str, repair_brief: str
) -> str:
    return f"""# Original Problem

{problem}

# Submitted Proof

{proof}

# Fusion Defect Packet

{defect_packet}

# Proposed Repair Brief

{repair_brief}

# Allowlisted Exact Operations

{operation_catalog()}

Nominate one exact local check only when its typed inputs can be derived literally
from this packet. Otherwise return NO_TOOL."""


def compilation_prompt(
    *,
    problem: str,
    proof: str,
    defect_packet: str,
    repair_brief: str,
    nomination: Mapping[str, Any],
) -> str:
    operation = str(nomination["operation"])
    return f"""# Original Problem

{problem}

# Submitted Proof

{proof}

# Fusion Defect Packet

{defect_packet}

# Proposed Repair Brief

{repair_brief}

# Immutable Exact-Evidence Nomination

- Claim: {nomination['claim']}
- Operation: {operation}
- Fit rationale: {nomination['fit_rationale']}

# Required Output

# Semantic Bindings

- Source basis: one-line derivation source
- Target meaning: one-line exact relation to the nominated local implication
- Domain and branch conditions: one-line complete conditions
- Compression map: one-line exact substitutions, or IDENTITY
- Sufficiency argument: one-line scope-preserving implication
- Rewrite consequence: one-line meaning of each possible result

# Tool Arguments

{v274.compiler_contract(operation)}

Emit the two top-level sections exactly. The contract's Tool Arguments heading is
illustrative; include it only once. Do not claim a result."""


def semantic_audit_prompt(
    *,
    problem: str,
    proof: str,
    defect_packet: str,
    repair_brief: str,
    nomination_markdown: str,
    compilation_markdown: str,
) -> str:
    return f"""# Original Problem

{problem}

# Submitted Proof

{proof}

# Fusion Defect Packet

{defect_packet}

# Proposed Repair Brief

{repair_brief}

# Exact-Evidence Nomination

{nomination_markdown}

# Proposed Semantic Binding and Typed Request

{compilation_markdown}

Audit literal correspondence and scope. A finite domain may refute an implication
by a witness, but failure to find a witness does not certify any larger domain."""


def _binding(result: Mapping[str, Any], binder: Callable[..., dict[str, Any]], root: Path, model: str) -> dict[str, Any]:
    return binder(dict(result), call_root=root, model=model)


def collect_optional_exact_evidence(
    *,
    destination: Path,
    problem: str,
    proof: str,
    defect_packet: str,
    repair_brief: str,
    pass_name: str,
    qwen_endpoint: str,
    gemma_endpoint: str,
    model_timeout_sec: int,
    caller: Callable[..., dict[str, Any]],
    producer_binder: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Nominate, compile, audit, and execute one optional exact local check.

    Every failure is contained inside this audit pass. Only a semantically accepted,
    independently replayed exact event is exposed to the repair-brief certifier.
    """

    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    common = {
        "schema": "cognitive-well-v0290-optional-exact-evidence-v1",
        "problem_sha256": sha256_text(problem),
        "proof_sha256": sha256_text(proof),
        "defect_packet_sha256": sha256_text(defect_packet),
        "repair_brief_sha256": sha256_text(repair_brief),
        "pass_name": pass_name,
        "allowed_operations": list(ALLOWED_OPERATIONS),
        "finite_no_witness_is_global_proof": False,
        "problem_specific_rules": False,
        "model_timeout_sec": model_timeout_sec,
    }
    try:
        nominate_root = destination / "01_nomination"
        nomination_call = caller(
            endpoint=qwen_endpoint,
            model=QWEN_MODEL,
            system_prompt=NOMINATOR_SYSTEM_PROMPT,
            user_prompt=nomination_prompt(
                problem=problem,
                proof=proof,
                defect_packet=defect_packet,
                repair_brief=repair_brief,
            ),
            output_dir=nominate_root,
            stage_name="nominate_exact_evidence",
            temperature=0.2,
            seed_key=f"v0290:{pass_name}:{sha256_text(proof)}:exact_nomination",
            reasoning_effort=None,
            parser=_parse_nomination,
            model_timeout_sec=model_timeout_sec,
        )
        nomination_producer = _binding(
            nomination_call, producer_binder, nominate_root, QWEN_MODEL
        )
        nomination = nomination_call["parsed"]
        nomination_text = str(nomination["normalized_markdown"])
        (destination / "nomination.md").write_text(nomination_text + "\n", encoding="utf-8")
        if not nomination["call_requested"]:
            record = {
                **common,
                "state": "no_tool",
                "usable_evidence": False,
                "nomination_sha256": sha256_text(nomination_text),
                "calls": {"nomination": nomination_producer},
            }
            write_json(destination / "result.json", record)
            return {
                "record": record,
                "report": None,
                "binding": {
                    "result_path": str((destination / "result.json").resolve()),
                    "result_file_sha256": file_sha256(destination / "result.json"),
                },
            }

        operation = str(nomination["operation"])
        compile_root = destination / "02_compilation"
        compilation_call = caller(
            endpoint=gemma_endpoint,
            model=GEMMA_MODEL,
            system_prompt=v274.COMPILER_SYSTEM,
            user_prompt=compilation_prompt(
                problem=problem,
                proof=proof,
                defect_packet=defect_packet,
                repair_brief=repair_brief,
                nomination=nomination,
            ),
            output_dir=compile_root,
            stage_name="compile_exact_evidence",
            temperature=0.2,
            seed_key=f"v0290:{pass_name}:{sha256_text(proof)}:exact_compilation",
            reasoning_effort="max",
            parser=lambda text: _parse_compilation(text, operation),
            model_timeout_sec=model_timeout_sec,
        )
        compilation_producer = _binding(
            compilation_call, producer_binder, compile_root, GEMMA_MODEL
        )
        compilation = compilation_call["parsed"]
        compilation_text = str(compilation["normalized_markdown"])
        (destination / "compilation.md").write_text(
            compilation_text + "\n", encoding="utf-8"
        )

        audit_root = destination / "03_semantic_audit"
        audit_call = caller(
            endpoint=qwen_endpoint,
            model=QWEN_MODEL,
            system_prompt=SEMANTIC_AUDITOR_SYSTEM_PROMPT,
            user_prompt=semantic_audit_prompt(
                problem=problem,
                proof=proof,
                defect_packet=defect_packet,
                repair_brief=repair_brief,
                nomination_markdown=nomination_text,
                compilation_markdown=compilation_text,
            ),
            output_dir=audit_root,
            stage_name="audit_exact_evidence_request",
            temperature=0.2,
            seed_key=f"v0290:{pass_name}:{sha256_text(proof)}:exact_semantic_audit",
            reasoning_effort=None,
            parser=_parse_semantic_audit,
            model_timeout_sec=model_timeout_sec,
        )
        audit_producer = _binding(audit_call, producer_binder, audit_root, QWEN_MODEL)
        audit_text = str(audit_call["text"]).strip()
        (destination / "semantic_audit.md").write_text(audit_text + "\n", encoding="utf-8")
        if audit_call["parsed"].get("accepted") is not True:
            record = {
                **common,
                "state": "semantic_rejected",
                "usable_evidence": False,
                "operation": operation,
                "nomination_sha256": sha256_text(nomination_text),
                "compilation_sha256": sha256_text(compilation_text),
                "semantic_audit_sha256": sha256_text(audit_text),
                "calls": {
                    "nomination": nomination_producer,
                    "compilation": compilation_producer,
                    "semantic_audit": audit_producer,
                },
            }
            write_json(destination / "result.json", record)
            return {
                "record": record,
                "report": None,
                "binding": {
                    "result_path": str((destination / "result.json").resolve()),
                    "result_file_sha256": file_sha256(destination / "result.json"),
                },
            }

        problem_record = v0220.Problem(
            problem_id="v0290_repair_brief_local_implication",
            statement=problem,
            source_path=destination / "problem.bound.md",
        )
        problem_record.source_path.write_text(problem + "\n", encoding="utf-8")
        event = exact_tools.execute(
            operation=operation,
            arguments=compilation["arguments"],
            claim=str(nomination["claim"]),
            problem=problem_record,
            run_id=f"v0290-{_safe_label(pass_name)}-{sha256_text(repair_brief)[:12]}",
            certificate_cache_dir=None,
        )
        verification = exact_tools.verify_target_evidence_event(
            event, full_legacy_replay=True
        )
        report = exact_tools.render_event(event)
        write_json(destination / "tool_event.json", event)
        (destination / "tool_result.md").write_text(report + "\n", encoding="utf-8")
        record = {
            **common,
            "state": "verified",
            "usable_evidence": True,
            "operation": operation,
            "claim": nomination["claim"],
            "nomination_sha256": sha256_text(nomination_text),
            "compilation_sha256": sha256_text(compilation_text),
            "semantic_audit_sha256": sha256_text(audit_text),
            "arguments_sha256": exact_tools.stable_hash(compilation["arguments"]),
            "event_path": str((destination / "tool_event.json").resolve()),
            "event_file_sha256": file_sha256(destination / "tool_event.json"),
            "report_path": str((destination / "tool_result.md").resolve()),
            "report_text_sha256": sha256_text(report),
            "verification": verification,
            "calls": {
                "nomination": nomination_producer,
                "compilation": compilation_producer,
                "semantic_audit": audit_producer,
            },
        }
        write_json(destination / "result.json", record)
        return {
            "record": record,
            "report": report,
            "binding": {
                "result_path": str((destination / "result.json").resolve()),
                "result_file_sha256": file_sha256(destination / "result.json"),
            },
        }
    except Exception as error:
        record = {
            **common,
            "state": "unavailable_fail_contained",
            "usable_evidence": False,
            "error": f"{type(error).__name__}: {error}",
        }
        write_json(destination / "result.json", record)
        return {
            "record": record,
            "report": None,
            "binding": {
                "result_path": str((destination / "result.json").resolve()),
                "result_file_sha256": file_sha256(destination / "result.json"),
            },
        }


def verify_exact_evidence_binding(
    binding: Mapping[str, Any],
    *,
    audit_root: Path,
    expected_problem_sha256: str,
    expected_proof_sha256: str,
    expected_defect_packet_sha256: str,
    expected_repair_brief_sha256: str,
    expected_problem: str,
    expected_proof: str,
    expected_defect_packet: str,
    expected_repair_brief: str,
    producer_verifier: Callable[..., str],
) -> str | None:
    result_path = Path(str(binding.get("result_path") or "")).resolve()
    try:
        result_path.relative_to((audit_root / "exact_evidence").resolve())
    except ValueError as error:
        raise ValueError("exact-evidence result path escaped its audit pass") from error
    if not result_path.is_file() or file_sha256(result_path) != str(
        binding.get("result_file_sha256") or ""
    ):
        raise ValueError("exact-evidence result artifact changed")
    record = json.loads(result_path.read_text(encoding="utf-8"))
    expected = {
        "problem_sha256": expected_problem_sha256,
        "proof_sha256": expected_proof_sha256,
        "defect_packet_sha256": expected_defect_packet_sha256,
        "repair_brief_sha256": expected_repair_brief_sha256,
    }
    if any(record.get(key) != value for key, value in expected.items()):
        raise ValueError("exact-evidence source binding changed")
    if (
        sha256_text(expected_problem) != expected_problem_sha256
        or sha256_text(expected_proof) != expected_proof_sha256
        or sha256_text(expected_defect_packet) != expected_defect_packet_sha256
        or sha256_text(expected_repair_brief) != expected_repair_brief_sha256
    ):
        raise ValueError("exact-evidence immutable source text changed")
    if record.get("allowed_operations") != list(ALLOWED_OPERATIONS):
        raise ValueError("exact-evidence operation allowlist changed")
    if (
        record.get("finite_no_witness_is_global_proof") is not False
        or record.get("problem_specific_rules") is not False
    ):
        raise ValueError("exact-evidence genericity/scope policy changed")
    state = str(record.get("state") or "")
    calls = record.get("calls") or {}
    if state == "unavailable_fail_contained":
        if record.get("usable_evidence") is not False:
            raise ValueError("failed exact evidence became usable")
        return None
    timeout = int(record.get("model_timeout_sec") or 0)
    if timeout != 600:
        raise ValueError("exact-evidence model timeout changed")
    pass_name = str(record.get("pass_name") or "")
    if not pass_name:
        raise ValueError("exact-evidence pass identity is missing")

    def expected_seed(binding: Mapping[str, Any], seed_key: str) -> int:
        cap = int(binding.get("cap") or 0)
        digest = hashlib.sha256(f"{seed_key}:{cap}".encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big")

    nomination_binding = calls["nomination"]
    nomination_seed_key = (
        f"v0290:{pass_name}:{expected_proof_sha256}:exact_nomination"
    )
    nomination_text = producer_verifier(
        nomination_binding,
        allowed_root=result_path.parent,
        expected_model=QWEN_MODEL,
        expected_timeout_sec=timeout,
        expected_stage=(
            f"nominate_exact_evidence_cap_{int(nomination_binding.get('cap') or 0)}"
        ),
        expected_seed=expected_seed(nomination_binding, nomination_seed_key),
        expected_system_prompt=NOMINATOR_SYSTEM_PROMPT,
        expected_base_user_prompt=nomination_prompt(
            problem=expected_problem,
            proof=expected_proof,
            defect_packet=expected_defect_packet,
            repair_brief=expected_repair_brief,
        ),
    )
    nomination = _parse_nomination(nomination_text)
    if sha256_text(str(nomination["normalized_markdown"])) != record.get(
        "nomination_sha256"
    ):
        raise ValueError("exact-evidence nomination changed")
    if state == "no_tool":
        if nomination.get("call_requested") or record.get("usable_evidence") is not False:
            raise ValueError("NO_TOOL exact-evidence record changed")
        return None
    operation = str(record.get("operation") or "")
    if not nomination.get("call_requested") or nomination.get("operation") != operation:
        raise ValueError("exact-evidence operation nomination changed")
    compilation_binding = calls["compilation"]
    compilation_seed_key = (
        f"v0290:{pass_name}:{expected_proof_sha256}:exact_compilation"
    )
    compilation_text = producer_verifier(
        compilation_binding,
        allowed_root=result_path.parent,
        expected_model=GEMMA_MODEL,
        expected_timeout_sec=timeout,
        expected_stage=(
            f"compile_exact_evidence_cap_{int(compilation_binding.get('cap') or 0)}"
        ),
        expected_seed=expected_seed(compilation_binding, compilation_seed_key),
        expected_system_prompt=v274.COMPILER_SYSTEM,
        expected_base_user_prompt=compilation_prompt(
            problem=expected_problem,
            proof=expected_proof,
            defect_packet=expected_defect_packet,
            repair_brief=expected_repair_brief,
            nomination=nomination,
        ),
    )
    compilation = _parse_compilation(compilation_text, operation)
    if (
        sha256_text(str(compilation["normalized_markdown"]))
        != record.get("compilation_sha256")
    ):
        raise ValueError("exact-evidence compilation changed")
    audit_binding = calls["semantic_audit"]
    audit_seed_key = (
        f"v0290:{pass_name}:{expected_proof_sha256}:exact_semantic_audit"
    )
    audit_text = producer_verifier(
        audit_binding,
        allowed_root=result_path.parent,
        expected_model=QWEN_MODEL,
        expected_timeout_sec=timeout,
        expected_stage=(
            f"audit_exact_evidence_request_cap_{int(audit_binding.get('cap') or 0)}"
        ),
        expected_seed=expected_seed(audit_binding, audit_seed_key),
        expected_system_prompt=SEMANTIC_AUDITOR_SYSTEM_PROMPT,
        expected_base_user_prompt=semantic_audit_prompt(
            problem=expected_problem,
            proof=expected_proof,
            defect_packet=expected_defect_packet,
            repair_brief=expected_repair_brief,
            nomination_markdown=str(nomination["normalized_markdown"]),
            compilation_markdown=str(compilation["normalized_markdown"]),
        ),
    )
    audit = v274_protocol.parse_semantic_audit(audit_text)
    if sha256_text(audit_text) != record.get("semantic_audit_sha256"):
        raise ValueError("exact-evidence semantic audit changed")
    if state == "semantic_rejected":
        if audit.get("accepted") or record.get("usable_evidence") is not False:
            raise ValueError("rejected exact request became usable")
        return None
    if state != "verified" or audit.get("accepted") is not True:
        raise ValueError(f"unsupported exact-evidence state: {state}")
    event_path = Path(str(record.get("event_path") or "")).resolve()
    report_path = Path(str(record.get("report_path") or "")).resolve()
    for path in (event_path, report_path):
        try:
            path.relative_to(result_path.parent)
        except ValueError as error:
            raise ValueError("exact-evidence artifact escaped its root") from error
    if not event_path.is_file() or file_sha256(event_path) != record.get(
        "event_file_sha256"
    ):
        raise ValueError("exact-evidence event changed")
    event = json.loads(event_path.read_text(encoding="utf-8"))
    if (
        event.get("operation") != operation
        or event.get("claim") != nomination.get("claim")
        or exact_tools.stable_hash(compilation["arguments"])
        != record.get("arguments_sha256")
        or event.get("arguments") != compilation["arguments"]
    ):
        raise ValueError("exact-evidence request/event binding changed")
    verification = exact_tools.verify_target_evidence_event(
        event, full_legacy_replay=True
    )
    if verification != record.get("verification"):
        raise ValueError("exact-evidence replay result changed")
    report = exact_tools.render_event(event)
    if (
        not report_path.is_file()
        or report_path.read_text(encoding="utf-8").strip() != report
        or sha256_text(report) != record.get("report_text_sha256")
        or record.get("usable_evidence") is not True
    ):
        raise ValueError("exact-evidence rendered report changed")
    return report


__all__ = [
    "ALLOWED_OPERATIONS",
    "collect_optional_exact_evidence",
    "verify_exact_evidence_binding",
]
