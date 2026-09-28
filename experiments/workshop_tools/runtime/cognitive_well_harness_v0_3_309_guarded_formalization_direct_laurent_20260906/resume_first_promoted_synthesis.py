from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    pipeline as base,
    protocol,
)
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import (
    integration as laurent,
)

from . import pipeline


def _verify_prepared_route(
    route_root: Path,
    route: Mapping[str, Any],
    formalization: Mapping[str, Any],
) -> str:
    if route.get("state") != "singular_proved":
        raise ValueError("selected route is not Singular-proved")
    screen = route.get("screen")
    prepared = route.get("prepared")
    if not isinstance(screen, Mapping) or not isinstance(prepared, Mapping):
        raise ValueError("selected route lacks screen or lift records")
    screen_replay = laurent.verify_persisted_laurent_outcome(
        output_dir=route_root / "02_target_screen", result=screen
    )
    if screen_replay.get("affirmative") is not True:
        raise ValueError("selected Singular target screen did not replay as PROVED")
    prepared_path = route_root / "03_laurent_lift/prepared.json"
    persisted = pipeline._read_json(prepared_path)
    returned = dict(prepared)
    prepared_sha = returned.pop("prepared_file_sha256", None)
    if persisted != returned or prepared_sha != pipeline._sha256_file(prepared_path):
        raise ValueError("selected prepared Laurent record changed")
    artifacts = persisted.get("artifact_sha256")
    if not isinstance(artifacts, Mapping):
        raise ValueError("selected lift artifact ledger is missing")
    lift_root = route_root / "03_laurent_lift"
    for relative, digest in artifacts.items():
        artifact = (lift_root / str(relative)).resolve()
        if lift_root.resolve() not in artifact.parents or not artifact.is_file():
            raise ValueError("selected lift artifact escaped its root")
        if pipeline._sha256_file(artifact) != digest:
            raise ValueError(f"selected lift artifact changed: {relative}")
    lift = pipeline._read_json(lift_root / "full_source_lift_certificate.json")
    lift_payload = dict(lift)
    lift_sha = lift_payload.pop("certificate_sha256", None)
    if pipeline.exact_tools.stable_hash(lift_payload) != lift_sha:
        raise ValueError("selected source-lift certificate internal hash changed")
    if lift_sha != persisted.get("full_source_lift_certificate_sha256"):
        raise ValueError("selected source-lift certificate binding changed")
    implication = lift.get("implication_replay")
    if lift.get("verified") is not True or not isinstance(implication, Mapping):
        raise ValueError("selected source-lift certificate is not verified")
    if not all(
        implication.get(key) is True
        for key in (
            "source_equations_to_derived_equations",
            "derived_target_to_source_target_under_recorded_nonzero_guards",
            "all_circle_pairs_substituted_simultaneously",
        )
    ):
        raise ValueError("selected source-lift implication replay is incomplete")
    arguments = formalization["arguments"]
    guards = formalization["guard_program"]
    if (
        persisted.get("source_arguments_sha256")
        != pipeline.exact_tools.stable_hash(arguments)
        or persisted.get("candidate_arguments_sha256")
        != pipeline.exact_tools.stable_hash(arguments)
        or persisted.get("guard_program_sha256")
        != pipeline.exact_tools.stable_hash(guards)
    ):
        raise ValueError("selected lift no longer binds the formalization")
    identity_replay = laurent.verify_exported_membership_identity(
        output_dir=route_root / "02_target_screen", result=screen
    )
    if identity_replay.get("verified") is not True:
        raise ValueError("selected multiplier identity did not replay")
    rendered = pipeline.render_exact_evidence(route_root, screen, prepared)
    persisted_evidence = (route_root / "04_exact_evidence.md").read_text(
        encoding="utf-8"
    )
    if rendered != persisted_evidence:
        raise ValueError("selected human-readable exact evidence changed")
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resume proof synthesis from the first fully promoted direct-Laurent route"
    )
    parser.add_argument("--problem-file", type=Path, required=True)
    parser.add_argument("--resolver1-proof", type=Path, required=True)
    parser.add_argument("--formalization-root", type=Path, required=True)
    parser.add_argument("--exact-run-root", type=Path, required=True)
    parser.add_argument("--audit-root", type=Path, required=True)
    parser.add_argument("--selected-label", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--gemma-model", default=base.DEFAULT_GEMMA_MODEL)
    parser.add_argument("--qwen-model", default=base.DEFAULT_QWEN_MODEL)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--model-timeout-sec", type=int, default=600)
    args = parser.parse_args()

    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    problem = pipeline.v0220.load_problem(args.problem_file)
    proof = args.resolver1_proof.resolve().read_text(encoding="utf-8").strip()
    allowed = base._matcher_operations(("simplify_identity",))
    detection_text, _, matcher_text, matcher, rows, resume_binding = (
        pipeline.load_resumed_formalizations(
            resume_root=args.formalization_root,
            problem=problem,
            proof=proof,
            allowed_matcher_operations=allowed,
        )
    )
    if matcher["operation"] != pipeline.exact_tools.IDEAL_OPERATION:
        raise ValueError("saved matcher operation is not polynomial ideal membership")
    labels = [label for label, _ in pipeline.FORMALIZATION_SCHEDULE]
    if args.selected_label not in labels:
        raise ValueError("selected label is outside the frozen schedule")
    selected_index = labels.index(args.selected_label)
    exact_root = args.exact_run_root.resolve()
    if not exact_root.is_dir():
        raise FileNotFoundError(exact_root)
    prior_outcomes: list[dict[str, Any]] = []
    for prior_label in labels[:selected_index]:
        route_root = exact_root / "05_direct_laurent_routes" / prior_label
        state = pipeline._read_json(route_root / "route_state.json")
        screen = state.get("screen")
        if not isinstance(screen, Mapping):
            raise ValueError(f"earlier route {prior_label} lacks an exact screen")
        replay = laurent.verify_persisted_laurent_outcome(
            output_dir=route_root / "02_target_screen", result=screen
        )
        if replay.get("affirmative") is True:
            raise ValueError(f"earlier route {prior_label} was already successful")
        prior_outcomes.append(
            {
                "label": prior_label,
                "state": state.get("state"),
                "screen_result_sha256": pipeline._sha256_file(
                    route_root / "02_target_screen/result.json"
                ),
                "affirmative": False,
            }
        )
    source_row = next(row for row in rows if row["label"] == args.selected_label)
    route_root = exact_root / "05_direct_laurent_routes" / args.selected_label
    route = pipeline._read_json(route_root / "route_state.json")
    event_text = _verify_prepared_route(
        route_root, route, source_row["formalization"]
    )

    audit_root = args.audit_root.resolve()
    audit_manifest = pipeline._read_json(audit_root / "manifest.json")
    audit_ledger = pipeline._read_json(audit_root / "ledger.json")
    if (
        audit_manifest.get("resume_binding_sha256") != resume_binding["binding_sha256"]
        or audit_manifest.get("exact_result_supplied") is not False
        or audit_manifest.get("laurent_outcome_supplied") is not False
    ):
        raise ValueError("saved Qwen audit portfolio is not exact-result-blind and bound")
    audit_result_path = audit_root / args.selected_label / "result.json"
    audit_result = pipeline._read_json(audit_result_path)
    audit_text = (audit_root / args.selected_label / "audit.md").read_text(
        encoding="utf-8"
    ).strip()
    reparsed_audit = pipeline.parse_post_singular_audit(audit_text)
    if (
        audit_result.get("state") != "accepted"
        or reparsed_audit.get("accepted") is not True
        or audit_result.get("audit") != reparsed_audit
        or args.selected_label not in audit_ledger.get("accepted_labels", [])
    ):
        raise ValueError("selected exact-result-blind Qwen audit did not reparse as ACCEPT")

    compiler = base.Role(
        endpoint=args.gemma_endpoint,
        model=args.gemma_model,
        temperature=0.4,
        reasoning_effort="max",
    )
    auditor = base.Role(
        endpoint=args.qwen_endpoint,
        model=args.qwen_model,
        temperature=0.2,
        reasoning_effort=None,
    )
    selection = {
        "schema": "cognitive-well-v0316-first-promoted-route-selection-v1",
        "policy": "first schedule route passing Singular, source lift, and Qwen audit",
        "selected_label": args.selected_label,
        "prior_exact_outcomes": prior_outcomes,
        "selected_route_state_sha256": pipeline._sha256_file(
            route_root / "route_state.json"
        ),
        "selected_audit_result_sha256": pipeline._sha256_file(audit_result_path),
        "resume_binding_sha256": resume_binding["binding_sha256"],
        "remaining_routes_discarded_without_evaluation": labels[selected_index + 1 :],
    }
    pipeline._write_json(destination / "selection.json", selection)
    manifest = {
        "schema": "cognitive-well-v0316-first-promoted-proof-synthesis-v1",
        "state": "running",
        "problem_id": problem.problem_id,
        "problem_file_sha256": pipeline._sha256_file(problem.source_path),
        "resolver1_proof_sha256": base.sha256_text(proof),
        "formalization_resume_binding_sha256": resume_binding["binding_sha256"],
        "exact_run_root": str(exact_root),
        "audit_root": str(audit_root),
        "selected_label": args.selected_label,
        "selection_sha256": pipeline._sha256_file(destination / "selection.json"),
        "roles": {"rewriter": asdict(compiler), "auditor": asdict(auditor)},
        "model_timeout_sec": args.model_timeout_sec,
        "manual_candidate_selection": False,
        "selection_policy_changed_by_user": True,
        "model_decisions_changed": False,
    }
    pipeline._write_json(destination / "manifest.json", manifest)

    compilation_text = str(source_row["formalization_text"])
    bridge_text = ""
    bridge: Mapping[str, Any] | None = None
    bridge_audit: Mapping[str, Any] | None = None
    prior_bridge_audit: Mapping[str, Any] | None = None
    for cycle in (1, 2, 3):
        bridge_text, bridge, _ = base._model_call(
            role=compiler,
            system_prompt=base.BRIDGE_SYSTEM,
            user_prompt=base.bridge_prompt(
                problem,
                proof,
                detection_text,
                compilation_text,
                audit_text,
                event_text,
                prior_bridge_audit,
            ),
            destination=destination / f"01_bridge/cycle_{cycle:02d}/model",
            stage="first_promoted_direct_laurent_bridge",
            master_seed=args.master_seed + cycle,
            parser=protocol.parse_bridge,
            request_timeout_sec=args.model_timeout_sec,
        )
        base.write_text(destination / f"01_bridge/cycle_{cycle:02d}/bridge.md", bridge_text)
        audit_bridge_text, bridge_audit, _ = base._model_call(
            role=auditor,
            system_prompt=base.BRIDGE_AUDITOR_SYSTEM,
            user_prompt=base.bridge_audit_prompt(
                problem, proof, compilation_text, event_text, bridge_text
            ),
            destination=destination / f"02_bridge_audit/cycle_{cycle:02d}/model",
            stage="first_promoted_direct_laurent_bridge_audit",
            master_seed=args.master_seed + cycle,
            parser=protocol.parse_bridge_audit,
            request_timeout_sec=args.model_timeout_sec,
        )
        base.write_text(
            destination / f"02_bridge_audit/cycle_{cycle:02d}/audit.md",
            audit_bridge_text,
        )
        if bridge_audit["accepted"]:
            break
        prior_bridge_audit = bridge_audit
    if not bridge or not bridge_audit or not bridge_audit["accepted"]:
        raise RuntimeError("first-promoted proof bridge remained rejected")
    if bridge["verdict"] == "NO_USABLE_RESULT":
        raise RuntimeError("first-promoted certificate produced no usable proof bridge")

    current_proof = proof
    proof_audit: Mapping[str, Any] | None = None
    prior_proof_audit: Mapping[str, Any] | None = None
    for cycle in (1, 2, 3):
        current_proof, _, _ = base._model_call(
            role=compiler,
            system_prompt=base.REWRITER_SYSTEM,
            user_prompt=base.rewrite_prompt(
                problem,
                proof,
                compilation_text,
                event_text,
                bridge_text,
                current_proof,
                prior_proof_audit,
            ),
            destination=destination / f"03_proof_rewrite/cycle_{cycle:02d}/model",
            stage="first_promoted_direct_laurent_whole_proof_rewrite",
            master_seed=args.master_seed + cycle,
            parser=base._terminal_proof,
            request_timeout_sec=args.model_timeout_sec,
        )
        base.write_text(
            destination / f"03_proof_rewrite/cycle_{cycle:02d}/terminal_proof.md",
            current_proof,
        )
        proof_audit_text, proof_audit, _ = base._model_call(
            role=auditor,
            system_prompt=base.PROOF_AUDITOR_SYSTEM,
            user_prompt=base.proof_audit_prompt(
                problem, compilation_text, event_text, bridge_text, current_proof
            ),
            destination=destination / f"04_proof_audit/cycle_{cycle:02d}/model",
            stage="first_promoted_direct_laurent_whole_proof_audit",
            master_seed=args.master_seed + cycle,
            parser=protocol.parse_proof_audit,
            request_timeout_sec=args.model_timeout_sec,
        )
        base.write_text(
            destination / f"04_proof_audit/cycle_{cycle:02d}/audit.md",
            proof_audit_text,
        )
        if proof_audit["passed"]:
            break
        prior_proof_audit = proof_audit
    if not proof_audit or not proof_audit["passed"]:
        raise RuntimeError("first-promoted whole proof remained rejected")
    terminal_path = destination / "terminal_proof.md"
    base.write_text(terminal_path, current_proof)
    result = {
        "schema": "cognitive-well-v0316-first-promoted-proof-result-v1",
        "state": "completed",
        "problem_id": problem.problem_id,
        "selected_label": args.selected_label,
        "singular_proved": True,
        "source_lift_verified": True,
        "semantic_audit_accepted": True,
        "bridge_audit_accepted": True,
        "proof_audit_passed": True,
        "terminal_proof": str(terminal_path),
        "terminal_proof_sha256": base.sha256_text(current_proof),
    }
    pipeline._write_json(destination / "result.json", result)
    pipeline._write_json(destination / "manifest.json", {**manifest, "state": "completed"})


if __name__ == "__main__":
    main()
