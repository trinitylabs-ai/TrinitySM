"""Actual Fusion handoff -> full admitted tool process -> appendix proof rewrite.

Consumes the existing effective Fusion artifact *after* its mandatory decision/
repair-brief gate. It never runs reviews, Fusion or that gate again, and never
imports a problem-specific experiment configuration or a successful proof.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from cognitive_well_harness_v0_3_53_fusion_20260823.protocol import parse_fusion
from . import proof_harness as harness
from . import radical_resume_synthesis as saved


@dataclass(frozen=True)
class FusionInput:
    problem_id: str
    problem_path: Path
    proof_path: Path
    fusion: str
    outcome: str
    gate_disposition: str
    artifacts: dict[str, str]

    def validate(self):
        if any(harness.base.sha256_file(Path(path)) != digest for path, digest in self.artifacts.items()):
            raise ValueError("Fusion handoff artifact drift")


def verify_existing_gate(effective_path, result, problem, proof):
    """Reuse the existing generic gate-history verifier, with dynamic identities.

    The portfolio driver has problem-specific defaults; it is deliberately NOT
    imported. This boundary helper validates producer records using only inputs.
    Reviewer records and audit histories are verified, not sent to new models.
    """
    from cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 import repair_boundary as boundary
    task = result["task"]
    gate_key = "repair_brief_audit_rewrite" if "repair_brief_audit_rewrite" in result else "fusion_acceptance_audit"
    gate = result.get(gate_key)
    if not isinstance(gate, dict) or gate.get("state") != "completed":
        raise ValueError("a completed mandatory Fusion decision/repair-brief gate is required")
    if (gate.get("problem_sha256") != harness.base.sha256_text(problem)
            or gate.get("proof_sha256") != harness.base.sha256_text(proof)
            or gate.get("effective_fusion_sha256") != result["final_sha256"]):
        raise ValueError("Fusion gate binds different problem, proof or effective packet")
    root = effective_path.parent.parent
    candidates = []
    for path in sorted((root / "fusion").rglob("result.json")):
        item = saved.read(path)
        if harness.base.sha256_text(str(item.get("final", "")).strip()) == gate["source_fusion_sha256"]:
            candidates.append((path, item))
    if len(candidates) != 1:
        raise ValueError("expected one bound original Fusion artifact within this case")
    source_path, source = candidates[0]
    if source.get("task") != task:
        raise ValueError("effective Fusion changed its source task")
    bound = {"problem": problem, "proof": proof, "proof_sha256": task["proof_sha256"],
             "task_id": task["task_id"], "candidate_id": task["candidate_id"]}
    paths = [source_path]
    for role in ("reviewer_1", "reviewer_2", "reviewer_3"):
        path = root / f"effective_{role}.txt"
        text = path.read_text().strip()
        metadata = task.get("reviewer_sources", {}).get(role, {})
        if (harness.base.sha256_text(text) != metadata.get("final_sha256")
                or metadata.get("proof_sha256") != task["proof_sha256"]):
            raise ValueError("Fusion reviewer binding changed: " + role)
        bound[role] = text
        paths.append(path)
    boundary.verify_gate_producer_history(gate, allowed_root=root, task=bound,
        source_fusion=str(source["final"]), effective_fusion=str(result["final"]))
    disposition = (boundary.repair_brief_disposition(gate)
        if gate_key == "repair_brief_audit_rewrite" else "CERTIFIED")
    return disposition, paths


def load(effective_path):
    effective_path = effective_path.resolve()
    result = saved.read(effective_path)
    final = str(result.get("final", "")).strip()
    parsed = parse_fusion(final)
    if (not parsed.get("valid") or parsed != result.get("parsed")
            or harness.base.sha256_text(final) != result.get("final_sha256")):
        raise ValueError("effective Fusion packet/parser/hash mismatch")
    task = result.get("task", {})
    problem_path, proof_path = Path(task["problem_path"]).resolve(), Path(task["proof_path"]).resolve()
    problem = harness.acquisition.v0220.load_problem(problem_path, explicit_problem_id=task["problem_id"])
    proof = proof_path.read_text().strip()
    if (not proof or harness.base.sha256_text(problem.statement) != task.get("problem_sha256")
            or harness.base.sha256_text(proof) != task.get("proof_sha256")):
        raise ValueError("Fusion input problem/proof binding mismatch")
    disposition, paths = verify_existing_gate(effective_path, result, problem.statement, proof)
    paths += [effective_path, problem_path, proof_path]
    handoff = FusionInput(problem.problem_id, problem_path, proof_path, final, parsed["outcome"],
        disposition, {str(path): harness.base.sha256_file(path) for path in paths})
    handoff.validate()
    harness.rewrite.assert_generic_boundary()
    return handoff


def render_packet(handoff):
    """Render only the effective model-authored packet; preserve its prompt text."""
    return ("# Effective Fusion Packet\n\n"
        "This is advisory model-written repair guidance, not established mathematics. "
        "Address its obligations using the original problem and proof. Independently "
        "choose whether a tool is useful and which exact fact it should check. "
        "Do not use a Fusion assertion as an extra hypothesis or force a tool call. "
        "A checked local result still requires both connections to the complete proof.\n\n"
        "```text\n" + handoff.fusion + "\n```")


def run(*, fusion_result, output, seed, config=None, execute_models=False, fallback=None, detection_from=None):
    """One complete post-Fusion tool attempt, without repeating upstream work.

    `fallback` is an optional host-owned normal Resolver callback. It receives
    the unchanged handoff only if no checked tool-assisted rewrite was accepted.
    Integrity/mechanical failures do not silently fall through to that callback.
    """
    config = config or harness.Config()
    config.validate()
    handoff = load(fusion_result)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    # Only the effective model-written packet is additional model context.
    # Certification labels, failed audits, reviewer transcripts and scores stay out.
    packet = render_packet(handoff)
    packet_path = output / "input/fusion_packet.md"
    harness.base.write_text(packet_path, packet)
    record = {"schema": "generic-after-fusion-tool-rewrite-v1", "state": "running" if execute_models else "prepared",
        "problem_id": handoff.problem_id, "effective_fusion_result": str(fusion_result.resolve()),
        "fusion_outcome": handoff.outcome, "brief_gate_disposition": handoff.gate_disposition,
        "source_artifacts": handoff.artifacts, "fusion_packet_sha256": harness.base.sha256_text(packet),
        "upstream_model_calls": 0, "gate_reused_without_new_calls": True,
        "prior_certificate_supplied": False, "old_successful_proof_supplied": False,
        "stages": ["completed_fusion_gate_handoff", "gap_detection", "operation_matching",
                   "formalization_parser_semantic_feedback", "checked_algebra_cascade",
                   "checked_lemma_and_appendix", "proof_rewrite", "whole_proof_audit"],
        "tool_run": str(output / "tool_rewrite"), "model_output": "Markdown"}
    harness.rewrite.write_record(output / "manifest.json", record)
    harness.rewrite.write_record(output / "status.json", record)
    try:
        if handoff.outcome == "ACCEPT_AS_WRITTEN":
            # Preserve this model decision; do not invent a repair request.
            record.update(state="completed" if execute_models else "prepared",
                outcome="FUSION_ACCEPTED_UNCHANGED", needs_regular_resolver=False)
            harness.base.write_text(output / "unchanged_proof.md", handoff.proof_path.read_text().strip())
        else:
            result = harness.run(problem_file=handoff.problem_path, proof_file=handoff.proof_path,
                problem_id=handoff.problem_id, fusion_result=fusion_result, output=output / "tool_rewrite",
                seed=seed, config=config, execute_models=execute_models, detection_from=detection_from)
            handoff.validate()
            record.update(state=result["state"], result=result,
                needs_regular_resolver=execute_models and result.get("outcome") != "REWRITTEN_AUDIT_PASS"
                    and result["state"] != "failed_closed")
            if result.get("outcome") == "REWRITTEN_AUDIT_PASS":
                text = Path(result["rewritten_proof"]).read_text().strip()
                if harness.base.sha256_text(text) != result["rewritten_proof_sha256"]:
                    raise ValueError("post-Fusion output proof binding changed")
                harness.base.write_text(output / "rewritten_proof.md", text)
                record.update(outcome="REWRITTEN_AUDIT_PASS", rewritten_proof=str(output / "rewritten_proof.md"),
                              rewritten_proof_sha256=result["rewritten_proof_sha256"])
            elif record["needs_regular_resolver"] and fallback is not None:
                record["fallback_result"] = fallback(handoff)
                record["fallback_used"] = True
        handoff.validate()
    except Exception as error:
        record.update(state="failed_closed", needs_regular_resolver=False,
                      error=f"{type(error).__name__}: {error}")
    harness.rewrite.write_record(output / "status.json", record)
    if execute_models:
        harness.rewrite.write_record(output / "result.json", record)
    return record


def run_after_fusion_result(result, **kwargs):
    """In-process handoff immediately after the existing mandatory Fusion gate."""
    path = result.get("_v290_effective_result_path")
    if not path:
        raise ValueError("Fusion has not supplied its persisted effective gate result")
    persisted = saved.read(Path(path))
    if any(persisted.get(key) != result.get(key) for key in ("final", "final_sha256", "parsed", "task")):
        raise ValueError("in-memory Fusion result differs from its persisted handoff")
    return run(fusion_result=Path(path), **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fusion-result", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--formalizer-temperature", type=float, default=.1)
    parser.add_argument("--gemma-endpoint", default=harness.Config.gemma_endpoint)
    parser.add_argument("--qwen-endpoint", default=harness.Config.qwen_endpoint)
    parser.add_argument("--exclude-operation", action="append", default=[])
    parser.add_argument("--detection-from", type=Path, help="Bound tool-harness run whose detection should be reused")
    parser.add_argument("--execute-models", action="store_true")
    args = parser.parse_args()
    result = run(fusion_result=args.fusion_result, output=args.output_dir, seed=args.master_seed,
        config=harness.Config(batch_size=args.batch_size,
            workers=args.workers if args.workers is not None else args.batch_size,
            cycles=args.cycles, formalizer_temperature=args.formalizer_temperature,
            gemma_endpoint=args.gemma_endpoint, qwen_endpoint=args.qwen_endpoint,
            excluded_operations=tuple(args.exclude_operation)),
        execute_models=args.execute_models, detection_from=args.detection_from)
    print(f"{result['state']}: {result.get('outcome', 'see status.json')}")
    return int(result["state"] == "failed_closed")


if __name__ == "__main__":
    raise SystemExit(main())
