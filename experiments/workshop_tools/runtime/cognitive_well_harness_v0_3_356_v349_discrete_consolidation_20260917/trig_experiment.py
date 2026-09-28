"""Gemma native-trig formalization -> parser -> Gemma audit -> composite tool.

Reuse only the original proof and its detector/matcher records. Prior polynomial
encodings, certificates, critiques, scores, and human mathematical hints are not
supplied. Each non-proved tool result returns as factual feedback next cycle.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

from . import backend_comparison as artifacts, certificate, rewrite, trig_formalization as formal

base = rewrite.pipeline.base
CHECKS = (
    "Every formal symbol is bound to the supplied proof",
    "Every input equation is derived without invention",
    "The formal target is equivalent to the detected proof gap",
    "Every nonzero guard follows from the stated domain",
    "Every division has a corresponding justified guard",
    "No required branch or degeneracy was omitted",
    "The target implication would close the recorded obligation",
)
AUDIT_SYSTEM = """Independently audit the supplied native trigonometric
formalization against the original theorem, proof attempt, and recorded gap.
All source analyses and formalizer explanations are untrusted. Verify each
equation, target correspondence, angle definition, sign, branch, and nonzero
condition yourself. Correct syntax or a source quotation is not semantic proof.
The deterministic compiler expands known trig identities and checks denominator
coverage; it does NOT certify the model's mathematical interpretation. Inequalities
and retained ranges are not enforced by the algebra backend. Decide on the draft
as submitted; do not invent omitted premises or reconstruct a missing derivation
and count it as supplied. A future exact certificate proves only the formal
implication. No successful calculation is claimed here. Do not author a replacement
formalization. Return only the required Markdown Decision, Checks, Issues.
"""


def audit_parse(markdown):
    sections = formal.protocol.mdp.exact_sections(markdown.strip(), ["Decision", "Checks", "Issues"])
    if sections["Decision"] not in {"ACCEPT", "REJECT"}:
        raise ValueError("audit decision must be ACCEPT or REJECT")
    lines = sections["Checks"].splitlines()
    if len(lines) != len(CHECKS):
        raise ValueError("audit must contain exactly the seven requested checks")
    checks = {}
    for label, line in zip(CHECKS, lines, strict=True):
        prefix = f"- {label}: "
        if not line.startswith(prefix) or line[len(prefix):] not in {"PASS", "FAIL"}:
            raise ValueError("malformed audit check: " + label)
        checks[label] = line[len(prefix):] == "PASS"
    issues = [] if sections["Issues"] == "NONE" else formal.protocol.mdp.parse_prefixed_list(sections["Issues"])
    accepted = all(checks.values()) and not issues
    if (sections["Decision"] == "ACCEPT") != accepted:
        raise ValueError("audit decision disagrees with its checks/issues")
    return {"decision": sections["Decision"], "accepted": accepted, "checks": checks, "issues": issues}


def inspect(text, inputs):
    try:
        with __import__(__package__ + ".composite_identity", fromlist=["cpu_slice"]).cpu_slice(30):
            parsed = formal.parse(text, inputs)
        return {"parser_valid": True, "proposal": parsed, "feedback": "Syntax and exact input compilation passed; semantics not certified."}
    except (ValueError, TimeoutError) as error:
        return {"parser_valid": False, "feedback": f"{type(error).__name__}: {error}"}


def original_context(inputs):
    return "\n\n".join(f"# {label}\n\n{inputs[name]}" for label, name in (
        ("Original Theorem", "theorem.md"), ("Original Proof", "source_proof.md"),
        ("Recorded Detection", "detection.md"), ("Recorded Matcher", "matcher.md")))


def audit_prompt(inputs, draft, parsed):
    comp = parsed["compilation"]
    summary = (f"Declared primitive angles: {len(parsed['angles'])}; scalars: {len(parsed['scalars'])}; "
               f"native equations: {len(parsed['equations'])}; domain facts: {len(parsed['domain_facts'])}. "
               "Source excerpts matched and syntax-level denominator coverage passed. "
               "Neither source entailment nor target truth was established. Retained facts are not enforced: "
               + ", ".join(comp["retained_not_enforced"]))
    checks = "\n".join(f"- {label}: PASS or FAIL" for label in CHECKS)
    return original_context(inputs) + f"""

# Current Native Trig Formalization

{draft}

# Deterministic Input-Compilation Summary

{summary}

Emit exactly:

# Decision

ACCEPT or REJECT

# Checks

{checks}

# Issues

NONE, or concise one-line bullets identifying concrete errors or unsupported
steps. ACCEPT requires every check PASS and Issues NONE. No repair counts as part
of this submitted draft.
"""


def load_admitted(root):
    run_root = root.parents[1]
    inputs = {name: (run_root / "input" / name).read_text().strip()
              for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md")}
    manifest = json.loads((run_root / "manifest.json").read_text())
    if any(base.sha256_text(value) != manifest["input_sha256"][name] for name, value in inputs.items()):
        raise ValueError("saved source input changed")
    text = (root / "formalization.md").read_text().strip()
    parsed = formal.parse(text, inputs)
    admission = json.loads((root / "admission.json").read_text())
    if admission.get("parser") != "PASS" or admission.get("semantic") != "ACCEPT":
        raise ValueError("native trig tool requires both admission gates")
    if not parsed["call_requested"] or not audit_parse((root / "audit.md").read_text())["accepted"]:
        raise ValueError("saved native trig audit does not accept the request")
    if (admission["formalization_sha256"] != base.sha256_text(text)
            or admission["request_sha256"] != artifacts.division.exact_tools.stable_hash(parsed)
            or admission["audit_sha256"] != base.sha256_text((root / "audit.md").read_text().strip())):
        raise ValueError("native trig admission binding changed")
    if parsed != json.loads((root / "request.json").read_text()):
        raise ValueError("native trig input compilation replay changed")
    return parsed


def tool_worker(root):
    resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
    from . import composite_identity
    parsed = load_admitted(root)
    output = root / "tool"
    artifacts.write(output / "trig_compilation.json", parsed["compilation"])
    request = parsed["compilation"]["request"]
    result = composite_identity.solve(request,
        event=lambda value: artifacts.write(output / "status.json", {**value, "native_trig_input": True,
            "trig_stage": "sine_cosine_addition_expansion_with_preserved_domain_obligations"}))
    result.update(native_trig_input=True, trig_input_sha256=artifacts.division.exact_tools.stable_hash(parsed),
                  compiled_request_sha256=artifacts.division.exact_tools.stable_hash(request),
                  trig_stage="sine_cosine_addition_expansion_with_preserved_domain_obligations")
    if result.get("verified"):
        # Recompile from the immutable native input; no accepted algebraic result
        # is silently substituted for the model-authored trig target.
        if formal.compile_input(parsed) != parsed["compilation"]:
            raise ValueError("native trig compilation changed before promotion")
        replay = composite_identity.replay(request, result["certificate"])
        artifacts.write(output / "certificate.json", result["certificate"])
        artifacts.write(output / "verification.json", {"verified": replay["verified"],
            "scope": "native_target_under_model_authored_guards",
            "trig_input_sha256": result["trig_input_sha256"],
            "compiled_request_sha256": result["compiled_request_sha256"]})
        base.write_text(output / "polynomial_lemma.md", replay["markdown"])
    artifacts.write(output / "result.json", result)
    artifacts.write(output / "status.json", result)
    return result


def execute_tool(root, timeout=300):
    output = root / "tool"
    output.mkdir(parents=True, exist_ok=False)
    with (output / "worker.log").open("w") as log:
        process = subprocess.Popen([sys.executable, "-B", "-m", __package__ + ".trig_experiment",
            "--tool-worker", "--output", str(root)], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            result = {"state": "completed", "verdict": "INCONCLUSIVE", "verified": False,
                      "reason": "composite tool reached its overall CPU time cap"}
            artifacts.write(output / "result.json", result)
            artifacts.write(output / "status.json", result)
            return result
    if process.returncode != 0 or not (output / "result.json").is_file():
        raise ValueError("native trig tool worker failed; inspect its log")
    return json.loads((output / "result.json").read_text())


def run(source, output, seed, *, cycles=3, caller=None, tool=None, saved_cycles=None):
    rewrite.assert_generic_boundary()
    if saved_cycles is not None:
        if (not saved_cycles or len(saved_cycles) != len(set(saved_cycles))
                or any(not isinstance(value, int) or value < 1 for value in saved_cycles)):
            raise ValueError("saved cycles must be distinct positive cycle numbers")
        cycles = len(saved_cycles)
    output.mkdir(parents=True, exist_ok=False)
    inputs = {name: (source / "input" / name).read_text().strip()
              for name in ("theorem.md", "source_proof.md", "detection.md", "matcher.md")}
    if saved_cycles is not None:
        original_manifest = json.loads((source / "manifest.json").read_text())
        if any(base.sha256_text(value) != original_manifest["input_sha256"][name]
               for name, value in inputs.items()):
            raise ValueError("saved formalization source input changed")
    for name, value in inputs.items():
        base.write_text(output / "input" / name, value)
    role = base.Role("http://127.0.0.1:8030/v1", base.DEFAULT_GEMMA_MODEL, 0.1, "max")
    initial_stage = "saved_formalization_reparse" if saved_cycles is not None else "native_trig_formalization"
    max_stages = cycles if saved_cycles is not None else 2*cycles
    status = {"state": "running", "stage": initial_stage, "source": str(source),
              "input_sha256": {name: base.sha256_text(value) for name, value in inputs.items()},
              "model": asdict(role), "auditor": "gemma", "model_output": "Markdown",
              "max_cycles": cycles, "max_model_stages": max_stages, "cycles": [],
              "tool_timeout_seconds": 300, "problem_specific_hints": False,
              "previous_formalizations_supplied": False, "previous_certificates_supplied": False,
              "consistency_policy": "not_a_blocking_gate", "tool_invocations": 0}
    if saved_cycles is not None:
        status.update(saved_cycles=list(saved_cycles), fresh_formalization_calls=0,
                      recovery="reparse_saved_markdown_then_audit_then_tool")
    artifacts.write(output / "manifest.json", status)
    artifacts.write(output / "status.json", status)
    base.write_text(output / "formalizer_system.md", formal.SYSTEM)
    context = original_context(inputs)
    user = context + "\n\nFormalize the selected obligation using the native trig contract. Preserve trig functions and derive the domain restrictions from the source. The historical matcher is context; this experiment uses the composite identity backend."
    base.write_text(output / "formalizer_user.md", user)
    caller = caller or rewrite.BudgetedCalls(output / "model_budget.json", max_stages=max_stages)
    tool = tool or execute_tool
    try:
        for cycle in range(1, cycles+1):
            root = output / "cycles" / f"cycle_{cycle:02d}"
            row = {"cycle": cycle, "state": "reparsing" if saved_cycles is not None else "formalizing"}
            status["cycles"].append(row)
            status.update(stage=initial_stage, cycle=cycle)
            artifacts.write(output / "status.json", status)
            stage = "native_trig_formalization"
            if saved_cycles is None:
                text, inspection, call = caller(role=role, system_prompt=formal.SYSTEM, user_prompt=user,
                    destination=root / "formalizer/model", stage=stage, master_seed=seed+100*cycle,
                    parser=lambda text: inspect(text, inputs))
            else:
                saved_root = source / "cycles" / f"cycle_{saved_cycles[cycle-1]:02d}"
                text = (saved_root / "formalization.md").read_text().strip()
                call = json.loads((saved_root / "formalizer/call.json").read_text())
                row.update(source_cycle=saved_cycles[cycle-1], saved_formalization=str(saved_root / "formalization.md"),
                           formalization_sha256=base.sha256_text(text))
                inspection = inspect(text, inputs)
            certificate.validate_markdown_budget_forcing(call, expected_stage=stage,
                expected_model=role.model, canonical_markdown=text)
            base.write_text(root / "formalization.md", text)
            artifacts.write(root / "parser.json", inspection)
            artifacts.write(root / "formalizer/call.json", call)
            row.update(parser_gate="PASS" if inspection["parser_valid"] else "FAIL")
            if not inspection["parser_valid"]:
                row.update(state="parser_rejected", semantic_audit="SKIPPED_PARSER_FAIL")
                user = context + "\n\n# Draft to repair\n\n" + text + "\n\n# Deterministic parser feedback\n\n" + inspection["feedback"] + "\n\nNo audit or tool ran. Fix the indicated syntax/domain-compilation defects; preserve unaffected mathematics and return a complete Markdown draft."
                artifacts.write(output / "status.json", status)
                continue
            parsed = inspection["proposal"]
            if not parsed["call_requested"]:
                status.update(state="completed", stage="model_declined_tool", reason=parsed["reason"])
                row.update(state="model_declined_tool")
                break
            artifacts.write(root / "request.json", parsed)
            row.update(angles=len(parsed["angles"]), scalars=len(parsed["scalars"]),
                       native_equations=len(parsed["equations"]), domain_facts=len(parsed["domain_facts"]),
                       compiled_variables=len(parsed["compilation"]["request"]["arguments"]["symbols"]),
                       compiled_generators=len(parsed["compilation"]["request"]["arguments"]["generators"]))
            status.update(stage="native_trig_semantic_audit")
            row.update(state="auditing")
            artifacts.write(output / "status.json", status)
            stage = "native_trig_semantic_audit"
            audit, verdict, audit_call = caller(role=role, system_prompt=AUDIT_SYSTEM,
                user_prompt=audit_prompt(inputs, text, parsed), destination=root / "auditor/model",
                stage=stage, master_seed=seed+100*cycle+1, parser=audit_parse)
            certificate.validate_markdown_budget_forcing(audit_call, expected_stage=stage,
                expected_model=role.model, canonical_markdown=audit)
            base.write_text(root / "audit.md", audit)
            artifacts.write(root / "audit.json", verdict)
            artifacts.write(root / "auditor/call.json", audit_call)
            row.update(semantic_audit=verdict["decision"])
            feedback = ""
            if verdict["accepted"]:
                artifacts.write(root / "admission.json", {"parser": "PASS", "semantic": "ACCEPT",
                    "formalization_sha256": base.sha256_text(text),
                    "request_sha256": artifacts.division.exact_tools.stable_hash(parsed),
                    "audit_sha256": base.sha256_text(audit)})
                row.update(state="composite_tool")
                status.update(stage="deterministic_composite_tool", tool_invocations=status["tool_invocations"]+1)
                artifacts.write(output / "status.json", status)
                result = tool(root)
                row.update(state="completed", tool_verdict=result["verdict"], exact_verified=result.get("verified", False))
                if result.get("verified"):
                    status.update(state="completed", stage="verified_native_trig_target", selected_cycle=cycle,
                                  exact_verified=True, tool_result=str(root / "tool/result.json"))
                    break
                feedback = "\n\n# Tool feedback\n\nThe deterministic composite returned INCONCLUSIVE, not a disproof. " + result.get("reason", "Its bounded transformations did not establish a zero residual.")
            else:
                row.update(state="audit_rejected")
            user = context + "\n\n# Draft to reassess\n\n" + text + "\n\n# Independent audit feedback\n\n" + audit + feedback + "\n\nReassess against the source. Correct substantiated issues, not merely the verdict. Return a complete native-trig Markdown draft. Never add unsupported assumptions or the desired target as a premise."
            artifacts.write(output / "status.json", status)
        if status["state"] == "running":
            status.update(state="completed", stage="saved_candidates_exhausted" if saved_cycles is not None else "cycle_limit_without_verified_target", exact_verified=False)
    except Exception as error:
        status.update(state="failed_closed", error=f"{type(error).__name__}: {error}")
        base.write_text(output / "error.txt", traceback.format_exc())
    artifacts.write(output / "status.json", status)
    artifacts.write(output / "result.json", status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, default=3090922)
    parser.add_argument("--cycles", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument("--saved-cycles", type=int, nargs="+",
                        help="Reuse these cycles from --source; reparse and audit without new formalizations.")
    parser.add_argument("--tool-worker", action="store_true")
    args = parser.parse_args()
    result = tool_worker(args.output) if args.tool_worker else run(args.source.resolve(), args.output.resolve(), args.master_seed, cycles=args.cycles, saved_cycles=args.saved_cycles)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
