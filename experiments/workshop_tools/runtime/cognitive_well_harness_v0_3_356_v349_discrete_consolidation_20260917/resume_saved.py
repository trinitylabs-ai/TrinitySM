"""Resume only certificate packaging and synthesis from a selected saved route.

This is a format-specific loader, not a problem-specific mathematical adapter.
It never invokes detection, matching, formalization, or Singular.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906 import pipeline as saved
from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906.resume_first_promoted_synthesis import _verify_prepared_route
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import TaskInputs
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import DETECTION_DOCUMENT, MATCHER_DOCUMENT

from .certificate import GenericCertificateContext
from . import pipeline


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _record_markdown(value: Any, prefix: str = "") -> str:
    """Lossless Markdown rendering of deterministic witness records, not model JSON."""
    if isinstance(value, dict):
        return "\n\n".join(_record_markdown(item, f"{prefix}.{key}".strip("."))
                            for key, item in value.items())
    if isinstance(value, list):
        return "\n\n".join(_record_markdown(item, f"{prefix}[{index}]")
                            for index, item in enumerate(value))
    return f"- {prefix}: `{value}`"


def load_context(selection_run: Path, formalization_root: Path | None = None):
    selection_root = selection_run.resolve()
    selection = _read(selection_root / "selection.json")
    selection_manifest = _read(selection_root / "manifest.json")
    label = str(selection["selected_label"])
    if label != selection_manifest["selected_label"] or not label.isalnum():
        raise ValueError("saved selected-label binding mismatch")
    exact_root = Path(selection_manifest["exact_run_root"]).resolve()
    exact_manifest = _read(exact_root / "manifest.json")
    formal_root = (formalization_root or Path(exact_manifest["resume_formalizations_root"])).resolve()
    formal_manifest = _read(formal_root / "manifest.json")
    problem = saved.v0220.load_problem(Path(exact_manifest["problem_file"]))
    proof_path = Path(exact_manifest["resolver1_proof"]).resolve()
    proof = proof_path.read_text(encoding="utf-8").strip()
    print("Reusing saved selection; reparsing frozen formalization bindings (no model calls).", flush=True)
    _, _, _, matcher, rows, binding = saved.load_resumed_formalizations(
        resume_root=formal_root, problem=problem, proof=proof,
        allowed_matcher_operations=tuple(formal_manifest["matcher_allowed_operations"]),
    )
    if selection["resume_binding_sha256"] != binding["binding_sha256"]:
        raise ValueError("saved selection no longer binds this formalization portfolio")
    row = next(item for item in rows if item["label"] == label)
    formalization = row["formalization"]
    formal_arm = formal_root / "03_guarded_formalizations" / label
    route_root = exact_root / "05_direct_laurent_routes" / label
    route_path = route_root / "route_state.json"
    if pipeline.base.sha256_file(route_path) != selection["selected_route_state_sha256"]:
        raise ValueError("saved selected exact route hash mismatch")

    audit_root = Path(selection_manifest["audit_root"]).resolve()
    audit_manifest = _read(audit_root / "manifest.json")
    audit_ledger = _read(audit_root / "ledger.json")
    audit_path = audit_root / label / "result.json"
    audit_text_path = audit_root / label / "audit.md"
    audit_result = _read(audit_path)
    audit = saved.parse_post_singular_audit(audit_text_path.read_text(encoding="utf-8").strip())
    if (audit_manifest.get("resume_binding_sha256") != binding["binding_sha256"]
            or audit_manifest.get("exact_result_supplied") is not False
            or audit_manifest.get("laurent_outcome_supplied") is not False
            or pipeline.base.sha256_file(audit_path) != selection["selected_audit_result_sha256"]
            or audit_result.get("state") != "accepted" or audit.get("accepted") is not True
            or audit_result.get("audit") != audit
            or label not in audit_ledger.get("accepted_labels", [])):
        raise ValueError("saved independent semantic acceptance failed to rebind")

    print("Checking the saved multiplier identity and lift bindings; no Singular search.", flush=True)
    evidence = _verify_prepared_route(route_root, _read(route_path), formalization)
    print("Saved certificate replay passed. Frozen synthesis inputs are ready.", flush=True)
    guard_program = formalization["guard_program"]
    guards = dict(guard_program["source_nonzero"])
    for division_label, division in guard_program["provenance_divisions"].items():
        guard_label = f"denominator_{division_label}"
        if guard_label in guards:
            raise ValueError("generated denominator label collides with a source guard")
        guards[guard_label] = division["denominator"]

    identity_path = route_root / "02_target_screen/derived_identity_certificate.json"
    lift_path = route_root / "03_laurent_lift/full_source_lift_certificate.json"
    artifacts = {
        "formal_request": formal_arm / "formalization.md",
        "formal_request_raw": formal_arm / "formalization_raw.md",
        "typed_guard_program": formal_arm / "guard_program.json",
        "exact_result": route_root / "04_exact_evidence.md",
        "original_problem": Path(problem.source_path),
        "original_proof": proof_path,
        "tool_detection": formal_root / "01_detection/detection.md",
        "tool_matcher": formal_root / "02_matcher/matcher.md",
        "selected_route": route_path,
        "selection": selection_root / "selection.json",
        "semantic_audit": audit_text_path,
        "semantic_audit_result": audit_path,
        "membership_identity": identity_path,
        "source_lift": lift_path,
    }
    # Bind every saved screen/lift artifact checked above to this replay snapshot.
    for subdir in ("02_target_screen", "03_laurent_lift"):
        for index, path in enumerate(sorted((route_root / subdir).rglob("*"))):
            if path.is_file():
                artifacts[f"saved_{subdir}_{index}"] = path
    frozen_hashes = {key: pipeline.base.sha256_file(path) for key, path in artifacts.items()}
    replay = {
        "schema": "cognitive-well-v0324-saved-laurent-certificate-replay-v1",
        "operation": matcher["operation"],
        "claim": str(matcher.get("claim") or formalization["bindings"]["target_meaning"]),
        "verified": True,
        "verdict": "VERIFIED_SUPPORT",
        "selected_label": label,
        "resume_binding_sha256": binding["binding_sha256"],
        "source_artifact_sha256": frozen_hashes,
        "original_generator_identity_reexpanded": True,
        "saved_lift_bindings_verified": True,
        "singular_search_rerun": False,
        "saved_exact_blind_semantic_audit_accepted": True,
    }

    def replay_exact():
        current = {key: pipeline.base.sha256_file(path) for key, path in artifacts.items()}
        if current != frozen_hashes:
            raise ValueError("saved artifact changed after successful certificate replay")
        return dict(replay)

    def replay_formal():
        parsed = saved.parse_guarded_formalization(artifacts["formal_request_raw"].read_text(encoding="utf-8").strip())
        if parsed["guard_program"] != guard_program:
            raise ValueError("typed guard program changed after loading")
        return parsed["arguments"]

    context = GenericCertificateContext(
        certificate_id=f"{problem.problem_id}_{label}".replace("-", "_"),
        theorem=problem.statement,
        arguments=formalization["arguments"], typed_guards=guards,
        replay_formal_request=replay_formal, replay_exact=replay_exact,
        formal_request_markdown=artifacts["formal_request"].read_text(encoding="utf-8").strip(),
        exact_result_markdown=evidence.strip(), source_artifacts=artifacts,
    )
    witness = "# Complete Saved Multiplier Identity\n\n" + _record_markdown(_read(identity_path))
    witness += "\n\n# Complete Saved Source Lift\n\n" + _record_markdown(_read(lift_path))
    task = TaskInputs(problem.problem_id, problem.statement, proof,
                      {"saved_exact_witness.md": witness,
                       DETECTION_DOCUMENT: artifacts["tool_detection"].read_text(encoding="utf-8").strip(),
                       MATCHER_DOCUMENT: artifacts["tool_matcher"].read_text(encoding="utf-8").strip(),
                       "accepted_formalization.md": context.formal_request_markdown})
    return task, context


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-run", type=Path, required=True)
    parser.add_argument("--formalization-root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--master-seed", type=int, required=True)
    parser.add_argument("--gemma-endpoint", default="http://127.0.0.1:8030/v1")
    parser.add_argument("--qwen-endpoint", default="http://127.0.0.1:8027/v1")
    parser.add_argument("--gemma-model", default=pipeline.base.DEFAULT_GEMMA_MODEL)
    parser.add_argument("--qwen-model", default=pipeline.base.DEFAULT_QWEN_MODEL)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    task, context = load_context(args.selection_run, args.formalization_root)
    if args.preflight_only:
        print(f"Preflight passed: {task.problem_id}, {len(context.arguments['symbols'])} variables, {len(context.arguments['generators'])} generators.", flush=True)
        return
    result = pipeline.run(
        task=task, context=context, output_dir=args.output_dir,
        gemma=pipeline.base.Role(args.gemma_endpoint, args.gemma_model, 0.2, "max"),
        qwen=pipeline.base.Role(args.qwen_endpoint, args.qwen_model, 0.1, None),
        master_seed=args.master_seed,
    )
    print(f"Proof synthesis completed: {result['terminal_proof']}", flush=True)


if __name__ == "__main__":
    main()
