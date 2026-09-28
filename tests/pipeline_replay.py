"""Synthetic stage outputs for model-free pipeline regression tests.

These fixtures exercise orchestration, audit replay and proof bindings; they do
not measure mathematical quality or issue any model request.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 import pipeline, repair_boundary


def repair_fusion(brief: str = "Prove the missing implication rigorously.") -> str:
    return "\n".join(
        [
            "FUSION_REPAIR_NEEDED",
            "verdict: REPAIR_NEEDED",
            "reviewer_1_assessment: DEFECT_VALIDATED | The claimed implication is not proved.",
            "reviewer_2_assessment: NO_DEFECT_REPORTED | No separate defect was submitted.",
            "reviewer_3_assessment: NO_DEFECT_REPORTED | No separate defect was submitted.",
            'decisive_location: "Therefore the conclusion follows."',
            "failed_obligation: Establish the stated implication from the available premises.",
            "independent_validation: The conclusion does not follow from the displayed premises alone.",
            "impact_on_proof: The final conclusion depends on this implication.",
            "repair_scope: STRUCTURAL",
            f"resolver_brief: {brief}",
            "preservable_material: The definitions and preliminary identities.",
            "END_FUSION_REPAIR_NEEDED",
        ]
    )

def audit_markdown(verdict: str) -> str:
    invalid = "NONE" if verdict == "CERTIFIED" else "The proposed implication is false."
    missing = "NONE" if verdict == "CERTIFIED" else "A valid global bridge is missing."
    witness = "NONE" if verdict == "CERTIFIED" else "Take the stated finite witness."
    return f"""# Repair Brief Certification
verdict: {verdict}

## Atomic Checks
1. Claim, premises, and quantifiers were checked independently.

## First Invalid Step
{invalid}

## Missing Obligation
{missing}

## Counterexample or Failure Witness
{witness}

## Certification Summary
The brief is {verdict.lower()}.

# End Repair Brief Certification"""

def rewrite_markdown(brief: str) -> str:
    return f"""# Repair Brief Candidate

## Target Obligation
Prove the missing implication.

## Verified Premises
- The displayed premises were rechecked.

## Repair Brief
{brief}

## Derivation Checklist
- Close every quantified bridge.

## Forbidden Shortcuts
- Do not assume the conclusion.

## Completion Criterion
The missing implication is explicitly proved.

# End Repair Brief Candidate"""

def source_result(text: str | None = None) -> dict[str, Any]:
    final = text or repair_fusion()
    parsed = repair_boundary.stage.resolver.parse_fusion(final)
    assert parsed["valid"]
    return {
        "state": "completed",
        "final": final,
        "final_sha256": repair_boundary.sha256_text(final),
        "parsed": parsed,
    }

class ScriptedCaller:
    def __init__(self, outputs: list[str]):
        self.outputs = list(outputs)
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(dict(kwargs))
        if not self.outputs:
            raise AssertionError("unexpected model call")
        text = self.outputs.pop(0).strip()
        parsed = kwargs["parser"](text)
        assert parsed["valid"], parsed
        destination = Path(kwargs["output_dir"])
        destination.mkdir(parents=True, exist_ok=True)
        token_policy = repair_boundary.token_policy_for(kwargs["model"])
        cap = repair_boundary.token_caps_for(kwargs["model"], token_policy)[0]
        attempt_dir = destination / f"attempt_01_cap_{cap}"
        attempt_dir.mkdir(parents=True, exist_ok=False)
        stage = f"{kwargs['stage_name']}_cap_{cap}"
        forced = {
            "canonical_artifacts_are_forced_response": True,
            "forced_text_sha256": repair_boundary.sha256_text(text),
            "model": kwargs["model"],
        }
        repair_boundary.write_json(
            attempt_dir / f"{stage}.raw_response.json",
            {"choices": [{"message": {"content": text}}]},
        )
        repair_boundary.write_json(
            attempt_dir / f"{stage}.metadata.json",
            {
                "finish_reason": "stop",
                "model": kwargs["model"],
                "stage": stage,
                "prompt_sha256": repair_boundary.sha256_text(
                    str(kwargs["system_prompt"])
                ),
                "user_prompt_sha256": repair_boundary.sha256_text(
                    str(kwargs["user_prompt"])
                ),
                "config": {
                    "max_tokens": cap,
                    "timeout_seconds": kwargs["model_timeout_sec"],
                    "seed": repair_boundary.stable_seed(
                        str(kwargs["seed_key"]), str(cap)
                    ),
                },
                "v0257_budget_forcing": forced,
            },
        )
        repair_boundary.write_json(
            attempt_dir / f"{stage}.budget_forcing.json",
            {
                **forced,
                "original_config": {
                    "max_tokens": cap,
                    "timeout_seconds": kwargs["model_timeout_sec"],
                    "seed": repair_boundary.stable_seed(
                        str(kwargs["seed_key"]), str(cap)
                    ),
                },
                "forced_config": {
                    "max_tokens": cap,
                    "timeout_seconds": kwargs["model_timeout_sec"],
                    "seed": repair_boundary.stable_seed(
                        str(kwargs["seed_key"]), str(cap)
                    ),
                },
            },
        )
        (attempt_dir / f"{stage}.prompt.txt").write_text(
            str(kwargs["system_prompt"]), encoding="utf-8"
        )
        (attempt_dir / f"{stage}.user_prompt.txt").write_text(
            str(kwargs["user_prompt"]), encoding="utf-8"
        )
        repair_boundary.write_json(
            attempt_dir / "validation.json",
            {
                "state": "accepted",
                "cap": cap,
                "text_sha256": repair_boundary.sha256_text(text),
                "request_timeout_sec": kwargs["model_timeout_sec"],
            },
        )
        final_path = destination / f"{kwargs['stage_name']}.final.md"
        final_path.write_text(text + "\n", encoding="utf-8")
        return {
            "text": text,
            "token_policy": token_policy,
            "parsed": parsed,
            "metadata": {
                "finish_reason": "stop",
                "v0257_budget_forcing": {
                    "canonical_artifacts_are_forced_response": True,
                    "forced_text_sha256": repair_boundary.sha256_text(text),
                },
            },
            "attempts": [{"state": "accepted", "cap": cap}],
            "attempt_dir": str(attempt_dir),
            "final_path": str(final_path),
            "final_sha256": repair_boundary.sha256_text(text),
        }

def write_forced_generation(
    *,
    destination: Path,
    stage_name: str,
    system_prompt: str,
    user_prompt: str,
    text: str,
    seed: int,
    cap: int = 32_768,
    timeout: int = 600,
    v079: bool = False,
    finish_reason: str = "stop",
) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    prompt_path = destination / f"{stage_name}.prompt.txt"
    user_prompt_path = destination / f"{stage_name}.user_prompt.txt"
    response_path = destination / f"{stage_name}.raw_response.json"
    metadata_path = destination / f"{stage_name}.metadata.json"
    budget_path = destination / f"{stage_name}.budget_forcing.json"
    prompt_path.write_text(system_prompt, encoding="utf-8")
    user_prompt_path.write_text(user_prompt, encoding="utf-8")
    pipeline.write_json(response_path, {"choices": [{"message": {"content": text}}]})
    config = {
        "max_tokens": cap,
        "temperature": 0.4,
        "top_p": 1.0,
        "top_k": -1,
        "seed": seed,
        "timeout_seconds": timeout,
    }
    forcing = {
        "stage": stage_name,
        "model": repair_boundary.GEMMA_MODEL,
        "canonical_artifacts_are_forced_response": True,
        "forced_text_sha256": repair_boundary.sha256_text(text.strip()),
    }
    metadata = {
        "stage": stage_name,
        "model": repair_boundary.GEMMA_MODEL,
        "finish_reason": finish_reason,
        "prompt_sha256": repair_boundary.sha256_text(system_prompt),
        "user_prompt_sha256": repair_boundary.sha256_text(user_prompt),
        "system_prompt_path": str(prompt_path.resolve()),
        "user_prompt_path": str(user_prompt_path.resolve()),
        "response_path": str(response_path.resolve()),
        "config": config,
        "v0257_budget_forcing": forcing,
    }
    pipeline.write_json(metadata_path, metadata)
    pipeline.write_json(
        budget_path,
        {**forcing, "original_config": config, "forced_config": config},
    )
    if v079:
        metadata = {
            **metadata,
            "v079_recovery_attempts": [
                {
                    "attempt": 0,
                    "stage": stage_name,
                    "finish_reason": "stop",
                    "empty": False,
                    "accepted": True,
                    "error": None,
                    "repetition_detection_preserved": True,
                }
            ],
        }
    return metadata

def install_refinement_replay(monkeypatch, brief_verdict="CERTIFIED"):
    original_stage_run = pipeline.stage.run
    gate_calls: list[tuple[str, str, str]] = []
    cycle_inputs: dict[int, dict[str, str]] = {}
    cycle_outputs: dict[int, dict[str, str]] = {}

    def fake_fusion_run(*, output_dir: Path, task: dict[str, Any]) -> dict[str, Any]:
        result = source_result(repair_fusion("Close the current cycle's exact gap."))
        result["task"] = {
            "problem_id": pipeline.PROBLEM_ID,
            "candidate_id": task["candidate_id"],
            "problem_sha256": repair_boundary.sha256_text(task["problem"]),
            "proof_sha256": task["proof_sha256"],
            "task_id": task["task_id"],
            "reviewer_sources": {
                role: {
                    "proof_sha256": task["proof_sha256"],
                    "final_sha256": repair_boundary.sha256_text(task[role]),
                }
                for role in ("reviewer_1", "reviewer_2", "reviewer_3")
            },
        }
        destination = Path(output_dir) / "fusion"
        destination.mkdir(parents=True, exist_ok=True)
        pipeline.write_json(destination / "result.json", result)
        return result

    def fake_gate(**kwargs: Any) -> dict[str, Any]:
        cycle_key = str(kwargs["cycle_key"])
        task_value = kwargs["task"]
        gate_calls.append((cycle_key, str(task_value["candidate_id"]), task_value["proof_sha256"]))
        return repair_boundary.audit_repair_and_reaudit(
            lane=Path(kwargs["lane"]),
            task=task_value,
            source_result=kwargs["source_result"],
            qwen_endpoint=str(kwargs["qwen_endpoint"]),
            gemma_endpoint=str(kwargs["gemma_endpoint"]),
            cycle_key=cycle_key,
            model_timeout_sec=int(kwargs["model_timeout_sec"]),
            caller=ScriptedCaller(
                [audit_markdown("CERTIFIED")] if brief_verdict == "CERTIFIED" else [
                    audit_markdown("REJECTED"), rewrite_markdown("First replacement."),
                    audit_markdown("REJECTED"), rewrite_markdown("Second replacement."),
                    audit_markdown("REJECTED"),
                ]
            ),
        )

    def fake_builder(**kwargs: Any) -> dict[str, Any]:
        fusion_result = kwargs["fusion_result"]
        case_dir = Path(kwargs["case_dir"])
        task_value = kwargs["fusion_task"]
        case = kwargs["case"]
        return {
            "fusion_result_path": str((case_dir / "fusion/result.json").resolve()),
            "fusion_record_sha256": repair_boundary.sha256_text(fusion_result["final"]),
            "problem_id": pipeline.PROBLEM_ID,
            "problem_sha256": pipeline.EXPECTED_PROBLEM_SHA256,
            "candidate_id": task_value["candidate_id"],
            "proof_sha256": task_value["proof_sha256"],
            "problem_path": str(Path(case["problem_path"]).resolve()),
            "proof_path": str(Path(case["proof_path"]).resolve()),
            "seed": 17,
        }

    def fake_r1_run(**kwargs: Any) -> dict[str, Any]:
        if kwargs.get("dry_run"):
            return original_stage_run(**kwargs)
        stage_dir = Path(kwargs["output_dir"])
        source = json.loads(Path(kwargs["cases_manifest"]).read_text())
        cycle = int(source["cycle"])
        cycle_inputs.setdefault(cycle, {})
        cycle_outputs.setdefault(cycle, {})
        rows = []
        for case in source["cases"]:
            candidate_id = str(case["candidate_id"])
            proof_path = Path(case["proof_path"])
            proof = proof_path.read_text(encoding="utf-8").strip()
            proof_hash = repair_boundary.sha256_text(proof)
            cycle_inputs[cycle][candidate_id] = proof_hash
            problem = str(
                json.loads(Path(case["problem_path"]).read_text())["claim"]
            ).strip()
            reviewer_values = {
                "reviewer_1": "FIRST_BREAK: The final implication may be unsupported.",
                "reviewer_2": "NO_ADVERSARIAL_BREAK: No separate attack survived.",
                "reviewer_3": "NO_UNCLOSED_OBLIGATION_FOUND: No other obligation was found.",
            }
            task_value = {
                "problem": problem,
                "proof": proof,
                "proof_sha256": proof_hash,
                "task_id": f"{pipeline.PROBLEM_ID}.{candidate_id}.fusion.t04",
                "candidate_id": candidate_id,
                **reviewer_values,
            }
            case_lane = stage_dir / "cases" / f"{pipeline.PROBLEM_ID}.{candidate_id}"
            case_lane.mkdir(parents=True, exist_ok=True)
            for role, value in reviewer_values.items():
                (case_lane / f"effective_{role}.txt").write_text(
                    value + "\n", encoding="utf-8"
                )
            fusion_result = pipeline.stage.fusion.run_task(
                output_dir=case_lane, task=task_value
            )
            resolver_task = pipeline.stage.build_resolver_task(
                case=case,
                fusion_task=task_value,
                fusion_result=fusion_result,
                case_dir=case_lane,
                seed_namespace="fake",
            )
            terminal = proof + f"\n\nCycle {cycle} terminal marker for {candidate_id}."
            terminal_path = case_lane / "resolver" / "resolved_proof.md"
            terminal_path.parent.mkdir(parents=True, exist_ok=True)
            terminal_path.write_text(terminal + "\n", encoding="utf-8")
            terminal_hash = repair_boundary.sha256_text(terminal)
            cycle_outputs[cycle][candidate_id] = terminal_hash
            resolver_result_path = case_lane / "resolver/result.json"
            resolver_final = "\n".join(
                [
                    "RESOLVED_PROOF",
                    "resolution_mode: STRUCTURAL_REWRITE",
                    "fusion_assessment: VALIDATED",
                    "change_summary: Applied the certified repair brief.",
                    "BEGIN_PROOF",
                    terminal,
                    "END_PROOF",
                    "END_RESOLVED_PROOF",
                ]
            )
            resolver_final_hash = repair_boundary.sha256_text(resolver_final)
            effective_fusion = str(fusion_result["final"])
            resolver_prompt = pipeline.stage.resolver.SYSTEM_PROMPT
            resolver_user_prompt = pipeline.stage.resolver.resolver_user_prompt(
                problem=problem, proof=proof, fusion_record=effective_fusion
            )
            resolver_generation = write_forced_generation(
                destination=case_lane / "resolver",
                stage_name="resolver",
                system_prompt=resolver_prompt,
                user_prompt=resolver_user_prompt,
                text=resolver_final,
                seed=17,
            )
            pipeline.write_json(
                resolver_result_path,
                {
                    "task": resolver_task,
                    "final": resolver_final,
                    "final_sha256": resolver_final_hash,
                    "parsed": pipeline.stage.resolver.parse_resolution(
                        resolver_final
                    ),
                    "identity": {
                        "system_prompt_sha256": repair_boundary.sha256_text(
                            resolver_prompt
                        ),
                        "user_prompt_sha256": repair_boundary.sha256_text(
                            resolver_user_prompt
                        ),
                        "max_output_tokens": 32_768,
                        "cap_recovery_max_output_tokens": 65_536,
                    },
                    "generation": resolver_generation,
                    "final_generation": resolver_generation,
                    "recovery": {"triggered": False},
                    "response_source": "live",
                },
            )
            handoff_path = case_lane / "resolver_trace_handoff/handoff.json"
            pipeline.write_json(
                handoff_path,
                {
                    "proof_path": str(terminal_path.resolve()),
                    "proof_sha256": terminal_hash,
                    "resolver_result_path": str(resolver_result_path.resolve()),
                    "resolver_result_sha256": pipeline.file_sha256(
                        resolver_result_path
                    ),
                    "resolver_outcome": "RESOLVED_PROOF",
                },
            )
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "resolver_trace_handoff": str(handoff_path.resolve()),
                    "resolver_outcome": "RESOLVED_PROOF",
                }
            )
        normalized_cases = []
        for case in source["cases"]:
            normalized = dict(case)
            normalized["proof_sha256"] = normalized["source_proof_sha256"]
            normalized_cases.append(normalized)
        pipeline.write_json(stage_dir / "manifest.json", {"cases": normalized_cases})
        summary = {"state": "completed", "rows": rows}
        pipeline.write_json(stage_dir / "summary.json", summary)
        return summary

    def forbidden_downstream(**kwargs: Any) -> None:
        raise AssertionError("Final refinement must be terminal: no extra model calls")

    monkeypatch.setattr(pipeline.stage.fusion, "run_task", fake_fusion_run)
    monkeypatch.setattr(pipeline.stage, "build_resolver_task", fake_builder)
    monkeypatch.setattr(
        pipeline.repair_boundary, "audit_fusion_before_resolver", fake_gate
    )
    monkeypatch.setattr(pipeline.stage, "run", fake_r1_run)
    monkeypatch.setattr(pipeline.v108.v098, "run", forbidden_downstream)
    monkeypatch.setattr(pipeline.v108, "run_direct_ungrouped_resolve", forbidden_downstream)
    monkeypatch.setattr(pipeline.v108.v105, "run", forbidden_downstream)

    return gate_calls, cycle_inputs, cycle_outputs


def mock_frontend_calls(monkeypatch, frontend):
    """Keep real orchestration, manifests and handoff; replace only model stages."""
    calls = []

    def cold(**kwargs):
        spec, claim = kwargs["spec"], kwargs["problem"]
        calls.append(("cold", spec["candidate_id"]))
        return {"candidate_id": spec["candidate_id"], "problem_id": claim["problem_id"],
                "problem_number": claim["problem_number"], "proof": "Let x be a real number satisfying x=0. Multiplying the equality by x gives x*x=0*x. The product of any real number and zero is zero, so x*x=0, as required."}

    def check(**kwargs):
        row = kwargs["row"]
        calls.append(("check", row["candidate_id"]))
        return {**row, "has_lazy_issues": row["candidate_id"] == "t10_r01"}

    def refine(**kwargs):
        row = kwargs["row"]
        calls.append(("refine", row["candidate_id"]))
        path = kwargs["output_dir"] / "candidates" / row["candidate_id"] / "checked_proof.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "Let x be a real number and suppose that x=0. By multiplication of equal quantities by x, we have x*x=0*x. Since zero multiplied by a real number is zero, the right side is zero and hence x*x=0." if row["has_lazy_issues"] else row["proof"]
        path.write_text(text + "\n", encoding="utf-8")
        result = {**row, "checked_proof_path": str(path.resolve()),
                  "checked_proof_sha256": frontend.sha256_text(text),
                  "lazy_resolve_invoked": row["has_lazy_issues"]}
        pipeline.write_json(path.parent / "result.json", result)
        return result

    monkeypatch.setattr(frontend, "run_cold_candidate", cold)
    monkeypatch.setattr(frontend, "run_lazy_check", check)
    monkeypatch.setattr(frontend, "run_lazy_resolve", refine)
    # Any accidental non-dry-run downstream invocation fails before inference.
    monkeypatch.setattr(frontend.enhanced_pipeline, "run_fresh_reviews",
                        lambda **_: (_ for _ in ()).throw(AssertionError("frontend must not run reviews")))
    return calls
