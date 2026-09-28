from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from experiments.local_math_verifier import runtime as transport

from . import pipeline, repair_boundary


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


def accepting_fusion() -> str:
    return "\n".join(
        [
            "FUSION_ACCEPT_AS_WRITTEN",
            "verdict: ACCEPT_AS_WRITTEN",
            "reviewer_1_assessment: DEFECT_REJECTED | The submitted objection does not invalidate the proof.",
            "reviewer_2_assessment: NO_DEFECT_REPORTED | No attack survived.",
            "reviewer_3_assessment: NO_DEFECT_REPORTED | All obligations were closed.",
            "independent_acceptance_basis: Every implication follows from the stated premises.",
            "literal_completeness_check: No mathematical completion is required.",
            "END_FUSION_ACCEPT_AS_WRITTEN",
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


def acceptance_audit_markdown(verdict: str) -> str:
    invalid = "NONE" if verdict == "CERTIFIED" else "The global implication is unsupported."
    missing = "NONE" if verdict == "CERTIFIED" else "Prove the pointwise-to-global step."
    witness = "NONE" if verdict == "CERTIFIED" else "The displayed premises permit a nonconstant example."
    return f"""# Fusion Acceptance Certification
verdict: {verdict}

## Atomic Checks
1. The proof was reconstructed and every load-bearing implication was checked.

## First Invalid Step
{invalid}

## Missing Obligation
{missing}

## Counterexample or Failure Witness
{witness}

## Certification Summary
The accepting Fusion decision is {verdict.lower()}.

# End Fusion Acceptance Certification"""


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


def no_tool_nomination_markdown() -> str:
    return """# Decision

NO_TOOL

# Operation

none

# Immutable Claim

NONE

# Fit Rationale

No allowlisted exact operation captures the quantified implication.
"""


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


def task() -> dict[str, Any]:
    proof = "Let x be arbitrary. Therefore the conclusion follows."
    return {
        "problem": "Prove the asserted conclusion.",
        "proof": proof,
        "proof_sha256": repair_boundary.sha256_text(proof),
        "task_id": "imo2026_p5.t07_r01.fusion.t04",
        "endpoint": "http://gemma.invalid/v1",
        "reviewer_1": "FIRST_BREAK: The final implication may be unsupported.",
        "reviewer_2": "NO_ADVERSARIAL_BREAK: No separate attack survived.",
        "reviewer_3": "NO_UNCLOSED_OBLIGATION_FOUND: No other obligation was found.",
        "reviewer_sources": {
            "reviewer_1": {"outcome": "FIRST_BREAK"},
            "reviewer_2": {"outcome": "NO_ADVERSARIAL_BREAK"},
            "reviewer_3": {"outcome": "NO_UNCLOSED_OBLIGATION_FOUND"},
        },
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


def test_original_certified_is_byte_preserved(tmp_path: Path) -> None:
    caller = ScriptedCaller([audit_markdown("CERTIFIED")])
    original = source_result()
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=original,
        qwen_endpoint="http://qwen.invalid/v1",
        gemma_endpoint="http://gemma.invalid/v1",
        cycle_key="R1-C1",
        caller=caller,
    )
    assert effective["final"] == original["final"]
    record = effective["repair_brief_audit_rewrite"]
    assert record["certified_round"] == 0
    assert record["audit_count"] == 1
    assert record["rewrite_count"] == 0
    assert len(caller.calls) == 1


def test_rejected_original_rewrite_is_reaudited(tmp_path: Path) -> None:
    new_brief = "Use a quantified lemma and prove both directions before concluding."
    caller = ScriptedCaller(
        [audit_markdown("REJECTED"), rewrite_markdown(new_brief), audit_markdown("CERTIFIED")]
    )
    original = source_result()
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=original,
        qwen_endpoint="http://qwen.invalid/v1",
        gemma_endpoint="http://gemma.invalid/v1",
        cycle_key="R1-C2",
        caller=caller,
    )
    assert repair_boundary.brief_stage.extract_resolver_brief(effective["final"]) == new_brief
    repair_boundary.assert_only_resolver_brief_changed(original["final"], effective["final"])
    record = effective["repair_brief_audit_rewrite"]
    assert record["certified_round"] == 1
    assert record["audit_count"] == 2
    assert record["rewrite_count"] == 1
    assert [call["model"] for call in caller.calls] == [
        repair_boundary.QWEN_MODEL,
        repair_boundary.GEMMA_MODEL,
        repair_boundary.QWEN_MODEL,
    ]
    repair_boundary.verify_gate_producer_history(
        record,
        allowed_root=tmp_path / "lane",
        source_fusion=original["final"],
        effective_fusion=effective["final"],
        task=task(),
    )


def test_second_rewrite_requires_third_audit(tmp_path: Path) -> None:
    caller = ScriptedCaller(
        [
            audit_markdown("REJECTED"),
            rewrite_markdown("First replacement."),
            audit_markdown("REJECTED"),
            rewrite_markdown("Second replacement with every bridge proved."),
            audit_markdown("CERTIFIED"),
        ]
    )
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source_result(),
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C3",
        caller=caller,
    )
    record = effective["repair_brief_audit_rewrite"]
    assert record["certified_round"] == 2
    assert record["audit_count"] == 3
    assert record["rewrite_count"] == 2


def test_rejected_second_rewrite_allows_uncertified_synthesis(tmp_path: Path) -> None:
    caller = ScriptedCaller(
        [
            audit_markdown("REJECTED"),
            rewrite_markdown("First replacement."),
            audit_markdown("REJECTED"),
            rewrite_markdown("Second replacement."),
            audit_markdown("REJECTED"),
        ]
    )
    lane = tmp_path / "lane"
    effective = repair_boundary.audit_repair_and_reaudit(
            lane=lane,
            task=task(),
            source_result=source_result(),
            qwen_endpoint="qwen",
            gemma_endpoint="gemma",
            cycle_key="R1-C1",
            caller=caller,
    )
    record = json.loads(
        (lane / "fusion_repair_brief_audit_rewrite/result.json").read_text()
    )
    assert record["state"] == "completed"
    assert record["certification"] == "REJECTED"
    assert record["certified_round"] is None
    assert len(caller.calls) == 5
    assert "Second replacement." in effective["final"]
    repair_boundary.verify_gate_producer_history(
        record, allowed_root=lane, source_fusion=source_result()["final"],
        effective_fusion=effective["final"], task=task(),
    )
    bound = pipeline.bind_effective_fusion_task(
        {"fusion_result_path": "original.json"}, fusion_result=effective, cycle_key="R1-C1"
    )
    assert bound["fusion_decision_gate"]["state"] == "REJECTED"
    assert bound["fusion_decision_gate"]["synthesis_allowed"] is True
    tampered = dict(record, certification="CERTIFIED")
    with pytest.raises(ValueError):
        repair_boundary.verify_gate_producer_history(
            tampered, allowed_root=lane, source_fusion=source_result()["final"],
            effective_fusion=effective["final"], task=task(),
        )


def test_accepting_fusion_requires_audit_and_is_byte_preserved(tmp_path: Path) -> None:
    caller = ScriptedCaller([acceptance_audit_markdown("CERTIFIED")])
    original = source_result(accepting_fusion())
    effective = repair_boundary.audit_fusion_before_resolver(
        lane=tmp_path / "lane",
        task=task(),
        source_result=original,
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C1",
        caller=caller,
    )
    assert effective["final"] == original["final"]
    assert len(caller.calls) == 1
    assert caller.calls[0]["model"] == repair_boundary.QWEN_MODEL
    record = effective["fusion_acceptance_audit"]
    assert record["state"] == "completed"
    assert record["certified_acceptance_round"] == 0
    assert record["reconsideration_count"] == 0
    assert Path(effective["_v290_effective_result_path"]).is_file()


def test_rejected_acceptance_returns_to_fusion_then_brief_gate(
    tmp_path: Path,
) -> None:
    caller = ScriptedCaller(
        [
            acceptance_audit_markdown("REJECTED"),
            repair_fusion("Prove the global bridge using only revalidated premises."),
            audit_markdown("CERTIFIED"),
        ]
    )
    effective = repair_boundary.audit_fusion_before_resolver(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source_result(accepting_fusion()),
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C1",
        caller=caller,
    )
    assert effective["parsed"]["outcome"] == "REPAIR_NEEDED"
    assert effective["fusion_acceptance_audit"]["repair_brief_gate"]["state"] == "completed"
    assert [call["model"] for call in caller.calls] == [
        repair_boundary.QWEN_MODEL,
        repair_boundary.GEMMA_MODEL,
        repair_boundary.QWEN_MODEL,
    ]
    assert "INDEPENDENT REJECTION" in caller.calls[1]["user_prompt"]
    assert "Fusion Acceptance Certification" not in caller.calls[2]["user_prompt"]
    repair_boundary.verify_gate_producer_history(
        effective["fusion_acceptance_audit"],
        allowed_root=tmp_path / "lane",
        source_fusion=accepting_fusion(),
        effective_fusion=effective["final"],
        task=task(),
    )


def test_rejected_reconsidered_acceptances_fail_closed(tmp_path: Path) -> None:
    caller = ScriptedCaller(
        [
            acceptance_audit_markdown("REJECTED"),
            accepting_fusion(),
            acceptance_audit_markdown("REJECTED"),
            accepting_fusion(),
            acceptance_audit_markdown("REJECTED"),
        ]
    )
    lane = tmp_path / "lane"
    with pytest.raises(repair_boundary.FusionAcceptanceCertificationError):
        repair_boundary.audit_fusion_before_resolver(
            lane=lane,
            task=task(),
            source_result=source_result(accepting_fusion()),
            qwen_endpoint="qwen",
            gemma_endpoint="gemma",
            cycle_key="R1-C2",
            caller=caller,
        )
    record = json.loads((lane / "fusion_acceptance_audit/result.json").read_text())
    assert record["state"] == "failed_closed"
    assert record["certified_acceptance_round"] is None
    assert record["reconsideration_count"] == 2


def test_repair_needed_enters_brief_gate_without_acceptance_audit(
    tmp_path: Path,
) -> None:
    caller = ScriptedCaller([audit_markdown("CERTIFIED")])
    effective = repair_boundary.audit_fusion_before_resolver(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source_result(),
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C3",
        caller=caller,
    )
    assert "repair_brief_audit_rewrite" in effective
    assert "fusion_acceptance_audit" not in effective
    assert len(caller.calls) == 1
    assert caller.calls[0]["stage_name"] == "audit_repair_brief"


def test_completed_gate_replays_bound_producer_and_rejects_model_tamper(
    tmp_path: Path,
) -> None:
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source_result(),
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C1",
        caller=ScriptedCaller([audit_markdown("CERTIFIED")]),
    )
    record = effective["repair_brief_audit_rewrite"]
    repair_boundary.verify_gate_producer_history(
        record,
        allowed_root=tmp_path / "lane",
        source_fusion=source_result()["final"],
        effective_fusion=effective["final"],
        task=task(),
    )
    record["history"][0]["producer"]["model"] = repair_boundary.GEMMA_MODEL
    with pytest.raises(ValueError, match="model identity"):
        repair_boundary.verify_gate_producer_history(
            record,
            allowed_root=tmp_path / "lane",
            source_fusion=source_result()["final"],
            effective_fusion=effective["final"],
            task=task(),
        )


def test_every_repair_audit_attempts_bound_optional_exact_evidence(
    tmp_path: Path,
) -> None:
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source_result(),
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C1",
        caller=ScriptedCaller(
            [no_tool_nomination_markdown(), audit_markdown("CERTIFIED")]
        ),
        enable_exact_evidence=True,
    )
    record = effective["repair_brief_audit_rewrite"]
    assert record["exact_evidence_enabled"] is True
    exact_binding = record["history"][0]["exact_evidence"]
    exact_record = json.loads(Path(exact_binding["result_path"]).read_text())
    assert exact_record["state"] == "no_tool"
    assert exact_record["usable_evidence"] is False
    repair_boundary.verify_gate_producer_history(
        record,
        allowed_root=tmp_path / "lane",
        source_fusion=source_result()["final"],
        effective_fusion=effective["final"],
        task=task(),
    )


def test_gate_replay_rejects_hash_chain_and_missing_metadata(
    tmp_path: Path,
) -> None:
    source = source_result()
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source,
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C1",
        caller=ScriptedCaller([audit_markdown("CERTIFIED")]),
    )
    record = effective["repair_brief_audit_rewrite"]
    changed = json.loads(json.dumps(record))
    changed["source_repair_brief_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source brief"):
        repair_boundary.verify_gate_producer_history(
            changed,
            allowed_root=tmp_path / "lane",
                source_fusion=source["final"],
                effective_fusion=effective["final"],
                task=task(),
        )

    producer = record["history"][0]["producer"]
    metadata_path = Path(producer["metadata_path"])
    metadata = json.loads(metadata_path.read_text())
    metadata.pop("model")
    pipeline.write_json(metadata_path, metadata)
    producer["metadata_file_sha256"] = pipeline.file_sha256(metadata_path)
    with pytest.raises(ValueError, match="metadata model"):
        repair_boundary.verify_gate_producer_history(
            record,
            allowed_root=tmp_path / "lane",
            source_fusion=source["final"],
            effective_fusion=effective["final"],
            task=task(),
        )


def test_gate_replay_rejects_coherent_prompt_substitution(tmp_path: Path) -> None:
    source = source_result()
    effective = repair_boundary.audit_repair_and_reaudit(
        lane=tmp_path / "lane",
        task=task(),
        source_result=source,
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C1",
        caller=ScriptedCaller([audit_markdown("CERTIFIED")]),
    )
    record = effective["repair_brief_audit_rewrite"]
    producer = record["history"][0]["producer"]
    prompt_path = Path(producer["prompt_path"])
    substituted = "An internally consistent but unauthorized system prompt."
    prompt_path.write_text(substituted, encoding="utf-8")
    producer["prompt_file_sha256"] = pipeline.file_sha256(prompt_path)
    metadata_path = Path(producer["metadata_path"])
    metadata = json.loads(metadata_path.read_text())
    metadata["prompt_sha256"] = repair_boundary.sha256_text(substituted)
    pipeline.write_json(metadata_path, metadata)
    producer["metadata_file_sha256"] = pipeline.file_sha256(metadata_path)
    with pytest.raises(ValueError, match="system prompt content"):
        repair_boundary.verify_gate_producer_history(
            record,
            allowed_root=tmp_path / "lane",
            source_fusion=source["final"],
            effective_fusion=effective["final"],
            task=task(),
        )


def test_v098_loader_uses_resolver_bound_effective_fusion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    phase2 = tmp_path / "phase2"
    case_id = f"{pipeline.PROBLEM_ID}.t07_r01"
    case_dir = phase2 / "cases" / case_id
    source_path = case_dir / "fusion" / "result.json"
    effective_path = (
        case_dir
        / "fusion_repair_brief_audit_rewrite"
        / "effective_fusion_result.json"
    )
    resolver_path = case_dir / "resolver" / "result.json"
    source = source_result(repair_fusion("Old obligation."))
    effective = source_result(repair_fusion("Certified effective obligation."))
    pipeline.write_json(source_path, source)
    pipeline.write_json(effective_path, effective)
    pipeline.write_json(
        resolver_path,
        {
            "task": {
                "source_fusion_result_path": str(source_path.resolve()),
                "fusion_result_path": str(effective_path.resolve()),
                "fusion_record_sha256": repair_boundary.sha256_text(
                    effective["final"]
                ),
            }
        },
    )
    loaded = {
        "case_id": case_id,
        "resolver_result_path": str(resolver_path.resolve()),
        "source_fusion_result": str(source_path.resolve()),
        "source_fusion_final": source["final"],
        "obligations": [
            {"source": "reviewer_1", "text": "Keep review obligation."},
            {"source": "fusion", "text": "Old obligation."},
        ],
    }
    original = pipeline.v108.v098.load_case
    monkeypatch.setattr(
        pipeline.v108.v098, "load_case", lambda _phase2, _spec, _row: dict(loaded)
    )
    patched_input = pipeline.v108.v098.load_case
    with pipeline.effective_fusion_post_r1_loader():
        result = pipeline.v108.v098.load_case(phase2, {}, {})
    assert pipeline.v108.v098.load_case is patched_input
    assert result["source_fusion_result"] == str(effective_path.resolve())
    assert result["source_fusion_final"] == effective["final"]
    assert any(
        row.get("source") == "fusion"
        and "Certified effective obligation"
        in row.get("minimum_requirement", "")
        for row in result["obligations"]
    )
    assert all(
        "Old obligation" not in row.get("minimum_requirement", "")
        for row in result["obligations"]
    )
    monkeypatch.setattr(pipeline.v108.v098, "load_case", original)


def test_proof_hash_drift_is_rejected_before_calls(tmp_path: Path) -> None:
    invalid_task = task()
    invalid_task["proof_sha256"] = "0" * 64
    caller = ScriptedCaller([])
    with pytest.raises(ValueError, match="proof hash drift"):
        repair_boundary.audit_repair_and_reaudit(
            lane=tmp_path / "lane",
            task=invalid_task,
            source_result=source_result(),
            qwen_endpoint="qwen",
            gemma_endpoint="gemma",
            cycle_key="R1-C1",
            caller=caller,
        )
    assert not caller.calls


def test_only_resolver_brief_mutation_guard() -> None:
    original = repair_fusion("Old brief.")
    changed = original.replace("impact_on_proof: ", "impact_on_proof: altered ")
    with pytest.raises(RuntimeError, match="outside resolver_brief"):
        repair_boundary.assert_only_resolver_brief_changed(original, changed)


def test_default_markdown_call_retries_parser_with_compact_feedback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_generation(**kwargs: Any) -> dict[str, Any]:
        calls.append(dict(kwargs))
        cap = kwargs["config"].max_tokens
        output_dir = Path(kwargs["output_dir"])
        stage_name = kwargs["stage"]
        repair_boundary.write_json(
            output_dir / f"{stage_name}.budget_forcing.json",
            {
                "structured": False,
                "original_config": {"max_tokens": cap},
                "forced_config": {"max_tokens": cap},
                "canonical_artifacts_are_forced_response": True,
                "forced_text_sha256": repair_boundary.sha256_text(
                    "bad markdown" if len(calls) == 1 else audit_markdown("CERTIFIED")
                ),
            },
        )
        text = "bad markdown" if len(calls) == 1 else audit_markdown("CERTIFIED")
        return {
            "text": text,
            "metadata": {
                "finish_reason": "stop",
                "v0257_budget_forcing": {
                    "canonical_artifacts_are_forced_response": True,
                    "forced_text_sha256": repair_boundary.sha256_text(text),
                },
            },
        }

    monkeypatch.setattr(
        repair_boundary.transport, "run_openai_chat_generation", fake_generation
    )
    result = repair_boundary.default_markdown_call(
        endpoint="qwen",
        model=repair_boundary.QWEN_MODEL,
        system_prompt="system",
        user_prompt="user",
        output_dir=tmp_path / "call",
        stage_name="audit",
        temperature=0.2,
        seed_key="seed",
        reasoning_effort=None,
        parser=repair_boundary.brief_stage.parse_certification_markdown,
        model_timeout_sec=600,
    )
    assert len(calls) == 2
    assert calls[0]["config"].max_tokens == 49_152
    assert calls[1]["config"].max_tokens == 49_152
    assert "Compact parser feedback" not in calls[0]["user_prompt"]
    assert "Compact parser feedback" in calls[1]["user_prompt"]
    assert result["parsed"]["verdict"] == "CERTIFIED"


def test_runtime_policy_floors_cap_and_timeout_and_restores(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    observed: list[Any] = []

    def raw(**kwargs: Any) -> dict[str, Any]:
        observed.append(kwargs["config"])
        return {"text": "ok", "metadata": {"finish_reason": "stop"}}

    monkeypatch.setattr(pipeline.transport, "run_openai_chat_generation", raw)
    config = transport.HTTPGenerationConfig(
        max_tokens=4000,
        temperature=0.1,
        top_p=1.0,
        top_k=-1,
        seed=1,
        thinking_token_budget=None,
        reasoning_effort=None,
        timeout_seconds=14_400,
    )
    with pipeline.runtime_generation_policy(model_timeout_sec=600):
        pipeline.transport.run_openai_chat_generation(
            endpoint="x",
            model="m",
            prompt="p",
            user_prompt="u",
            output_dir=tmp_path,
            stage="s",
            config=config,
        )
    assert observed[0].max_tokens == 32_768
    assert observed[0].timeout_seconds == 600
    assert pipeline.transport.run_openai_chat_generation is raw


def test_inherited_component_caps_cover_reviewer1_and_restore() -> None:
    reviewer1_module = sys.modules[pipeline.stage.run_original_reviewer.__module__]
    reviewer2_module = pipeline.stage.reviewer_2
    original_r1 = reviewer1_module.REVIEWER_INITIAL_MAX_TOKENS
    original_r1_recovery = reviewer1_module.REVIEWER_RECOVERY_MAX_TOKENS
    original_r2 = reviewer2_module.MAX_OUTPUT_TOKENS
    with pipeline.inherited_component_caps():
        assert reviewer1_module.REVIEWER_INITIAL_MAX_TOKENS == 32_768
        assert reviewer1_module.REVIEWER_RECOVERY_MAX_TOKENS == (65_536, 65_536)
        assert reviewer2_module.MAX_OUTPUT_TOKENS == 49_152
        assert reviewer2_module.TERMINAL_RECOVERY_MAX_OUTPUT_TOKENS == 49_152
        assert reviewer2_module.RETRY_ON_OUTPUT_CAP is False
        assert reviewer2_module.CAP_RECOVERY_MAX_OUTPUT_TOKENS == 49_152
        assert reviewer2_module.FINAL_CAP_RECOVERY_MAX_OUTPUT_TOKENS == 65_536
    assert reviewer1_module.REVIEWER_INITIAL_MAX_TOKENS == original_r1
    assert reviewer1_module.REVIEWER_RECOVERY_MAX_TOKENS == original_r1_recovery
    assert reviewer2_module.MAX_OUTPUT_TOKENS == original_r2


def test_boundary_context_is_visible_to_fusion_worker_threads() -> None:
    with pipeline.mandatory_repair_boundary(
        qwen_endpoint="qwen",
        gemma_endpoint="gemma",
        cycle_key="R1-C2",
        model_timeout_sec=600,
    ):
        with ThreadPoolExecutor(max_workers=1) as pool:
            observed = pool.submit(pipeline._boundary_config).result()
    assert observed["cycle_key"] == "R1-C2"
    assert observed["model_timeout_sec"] == 600


def test_dry_run_real_frozen_inputs_has_all_checkpoints(tmp_path: Path) -> None:
    output_dir = tmp_path / "dry"
    result = pipeline.run_pipeline(output_dir=output_dir, dry_run=True)
    assert result["state"] == "dry_run_completed"
    assert result["model_calls_performed"] == 0
    assert [row["checkpoint"] for row in result["checkpoints"]] == [
        "baseline",
        "R1-C1",
        "R1-C2",
        "R1-C3",
    ]
    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert manifest["stage_order"] == ["R1-C1", "R1-C2", "R1-C3"]
    assert manifest["terminal_checkpoint"] == "R1-C3"
    assert manifest["pipeline_policy"] == pipeline.PIPELINE_POLICY
    assert "downstream" not in manifest
    assert manifest["repair_brief_boundary"]["mandatory_every_r1_cycle"] is True
    assert manifest["repair_brief_boundary"]["accepting_fusion_audit_mandatory"] is True
    assert manifest["repair_brief_boundary"]["rejected_acceptance_returns_to_fusion"] is True
    assert manifest["repair_brief_boundary"]["audit_original_then_every_rewrite"] is True
    assert manifest["model_inputs_exclude"] == [
        "reference_solution",
        "v0139_proof",
        "strict_score",
        "Codex_feedback",
        "human_repair_brief_audit",
    ]


def test_r1_resolver_replays_cap_merge_and_protocol_repair(tmp_path: Path) -> None:
    root = tmp_path / "run"
    case_dir = root / "r1" / "cases" / f"{pipeline.PROBLEM_ID}.t07_r01"
    problem = "Prove the asserted conclusion from the stated hypotheses."
    proof = "A submitted proof with a genuine missing implication."
    problem_path = root / "input/problem.json"
    proof_path = root / "input/proof.md"
    pipeline.write_json(problem_path, {"claim": problem})
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(proof + "\n", encoding="utf-8")
    fusion = repair_fusion("Close the missing implication exactly.")
    fusion_path = case_dir / "gate/effective_fusion_result.json"
    pipeline.write_json(fusion_path, {"final": fusion})
    seed = 314159
    user_prompt = pipeline.stage.resolver.resolver_user_prompt(
        problem=problem, proof=proof, fusion_record=fusion
    )
    system_prompt = pipeline.stage.resolver.SYSTEM_PROMPT
    producer_dir = case_dir / "resolver"
    primary_text = "RESOLVED_PROOF\nincomplete primary fragment"
    continuation_text = "continuation that still does not satisfy the protocol"
    primary = write_forced_generation(
        destination=producer_dir,
        stage_name="resolver",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        text=primary_text,
        seed=seed,
        cap=32_768,
        finish_reason="length",
    )
    continuation = write_forced_generation(
        destination=producer_dir,
        stage_name="resolver_cap_continuation",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        text=continuation_text,
        seed=(seed + 1_000_003) & 0xFFFFFFFF,
        cap=65_536,
    )
    merged = pipeline.stage.resolver.merge_continuation(
        primary_text, continuation_text
    )
    terminal_proof = (
        "Let the hypotheses hold. We establish the missing implication directly, "
        "then apply it to the arbitrary object and obtain the required conclusion."
    )
    final = "\n".join(
        [
            "RESOLVED_PROOF",
            "resolution_mode: LOCAL_REPAIR",
            "fusion_assessment: VALIDATED",
            "change_summary: Supplied the missing implication.",
            "BEGIN_PROOF",
            terminal_proof,
            "END_PROOF",
            "END_RESOLVED_PROOF",
        ]
    )
    protocol = write_forced_generation(
        destination=producer_dir,
        stage_name="resolver_protocol_repair",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        text=final,
        seed=(seed + 3_000_009) & 0xFFFFFFFF,
        cap=32_768,
    )
    task_value = {
        "problem_path": str(problem_path.resolve()),
        "problem_sha256": repair_boundary.sha256_text(problem),
        "proof_path": str(proof_path.resolve()),
        "proof_sha256": repair_boundary.sha256_text(proof),
        "fusion_result_path": str(fusion_path.resolve()),
        "fusion_record_sha256": repair_boundary.sha256_text(fusion),
        "seed": seed,
    }
    result_path = producer_dir / "result.json"
    pipeline.write_json(
        result_path,
        {
            "task": task_value,
            "identity": {
                "system_prompt_sha256": repair_boundary.sha256_text(system_prompt),
                "user_prompt_sha256": repair_boundary.sha256_text(user_prompt),
                "max_output_tokens": 32_768,
                "cap_recovery_max_output_tokens": 65_536,
            },
            "final": final,
            "final_sha256": repair_boundary.sha256_text(final),
            "parsed": pipeline.stage.resolver.parse_resolution(final),
            "generation": primary,
            "final_generation": protocol,
            "recovery": {
                "triggered": True,
                "primary_max_output_tokens": 32_768,
                "recovery_max_output_tokens": 65_536,
                "continuation_generation": continuation,
                "protocol_repair": {
                    "triggered": True,
                    "generation": protocol,
                    "initial_errors": pipeline.stage.resolver.parse_resolution(merged)[
                        "errors"
                    ],
                },
            },
            "response_source": "live",
        },
    )
    replayed, parsed = pipeline._verify_resolver_producer(
        resolver_result_path=result_path,
        case_dir=case_dir,
        allowed_root=root,
        model_timeout_sec=600,
    )
    assert replayed["final"] == final
    assert parsed["outcome"] == "RESOLVED_PROOF"


def test_live_calls_require_explicit_authorization(tmp_path: Path) -> None:
    with pytest.raises(PermissionError):
        pipeline.run_pipeline(output_dir=tmp_path / "live", dry_run=False)


def test_output_root_must_be_fresh(tmp_path: Path) -> None:
    output_dir = tmp_path / "existing"
    output_dir.mkdir()
    with pytest.raises(FileExistsError):
        pipeline.run_pipeline(output_dir=output_dir, dry_run=True)


def test_initialization_drift_persists_outer_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def bad_inputs(*, output_dir: Path, **_: Any) -> tuple[Path, list[dict[str, Any]]]:
        problem_path = output_dir / "input/problem.json"
        pipeline.write_json(problem_path, {"claim": "Wrong problem."})
        return problem_path, []

    monkeypatch.setattr(pipeline, "_initial_inputs", bad_inputs)
    output_dir = tmp_path / "bad_init"
    result = pipeline.run_pipeline(output_dir=output_dir, dry_run=True)
    assert result["state"] == "failed_closed"
    assert result["stage"] == "input_binding"
    assert json.loads((output_dir / "failure.json").read_text()) == result


def test_all_lanes_failed_persists_outer_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_r1(**_: Any) -> None:
        raise RuntimeError("mechanical lane failure")

    monkeypatch.setattr(pipeline.stage, "run", fail_r1)
    output_dir = tmp_path / "all_failed"
    result = pipeline.run_pipeline(
        output_dir=output_dir, authorize_model_calls=True
    )
    assert result["state"] == "failed_closed"
    failure = json.loads((output_dir / "failure.json").read_text())
    assert failure["stage"] == "all_lanes"
    assert set(failure["lane_failures"]) == set(pipeline.CANDIDATE_IDS)
    for candidate_id in pipeline.CANDIDATE_IDS:
        assert (output_dir / "lanes" / candidate_id / "failure.json").is_file()


def test_r3_unchanged_route_requires_exact_upstream_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "run"
    candidate_id = "t07_r01"
    case_id = f"{pipeline.PROBLEM_ID}.{candidate_id}"
    resolve_run = root / "lanes" / candidate_id / "05_resolver2"
    prior_gate = root / "lanes" / candidate_id / "04_gate"
    third_dir = root / "lanes" / candidate_id / "06_resolver3"
    source_path = resolve_run / "resolved_proof.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("The exact upstream proof.\n", encoding="utf-8")
    source_hash = repair_boundary.sha256_text(source_path.read_text().strip())
    promoted_path = (
        third_dir / "cases" / case_id / "promoted_unchanged/third_proof.md"
    )
    promoted_path.parent.mkdir(parents=True, exist_ok=True)
    promoted_path.write_bytes(source_path.read_bytes())
    promotion_path = promoted_path.parent / "promotion.json"
    pipeline.write_json(
        promotion_path,
        {
            "state": "completed",
            "source_proof_path": str(source_path.resolve()),
            "source_proof_sha256": source_hash,
            "third_proof_path": str(promoted_path.resolve()),
            "third_proof_sha256": source_hash,
            "model_call_count": 0,
        },
    )
    pipeline.write_json(
        third_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0105-iterated-ungrouped-resolve-manifest-v1",
            "source_resolve_runs": [str(resolve_run.resolve())],
            "prior_gate_run": str(prior_gate.resolve()),
            "models": {"gemma": repair_boundary.GEMMA_MODEL},
            "cases": [
                {
                    "case_id": case_id,
                    "problem_id": pipeline.PROBLEM_ID,
                    "candidate_id": candidate_id,
                    "second_proof_path": str(source_path.resolve()),
                    "second_proof_sha256": source_hash,
                }
            ],
        },
    )
    row = {
        "case_id": case_id,
        "candidate_id": candidate_id,
        "second_proof_path": str(source_path.resolve()),
        "second_proof_sha256": source_hash,
        "third_proof_path": str(promoted_path.resolve()),
        "third_proof_sha256": source_hash,
        "third_resolve_state": "promoted_unchanged_no_second_cycle",
    }
    pipeline.write_json(
        third_dir / "summary.json", {"state": "completed", "rows": [row]}
    )
    monkeypatch.setattr(
        pipeline.v108.v105,
        "load_cases",
        lambda **_: [{"candidate_id": candidate_id}],
    )
    expected = {
        "candidate_id": candidate_id,
        "proof_path": str(source_path.resolve()),
        "proof_sha256": source_hash,
    }
    checkpoint = pipeline._third_checkpoint(
        third_dir,
        allowed_root=root,
        expected_candidates=(candidate_id,),
        expected_sources=[expected],
        resolve_run=resolve_run,
        prior_gate_run=prior_gate,
        seed_namespace="test:r3",
        model_timeout_sec=600,
    )
    assert checkpoint["proofs"][0]["proof_sha256"] == source_hash

    promoted_path.write_text("A coherently rehashed replacement.\n", encoding="utf-8")
    changed_hash = repair_boundary.sha256_text(promoted_path.read_text().strip())
    row["third_proof_sha256"] = changed_hash
    pipeline.write_json(
        third_dir / "summary.json", {"state": "completed", "rows": [row]}
    )
    promotion = json.loads(promotion_path.read_text())
    promotion["third_proof_sha256"] = changed_hash
    pipeline.write_json(promotion_path, promotion)
    with pytest.raises(ValueError, match="unchanged route changed proof"):
        pipeline._third_checkpoint(
            third_dir,
            allowed_root=root,
            expected_candidates=(candidate_id,),
            expected_sources=[expected],
            resolve_run=resolve_run,
            prior_gate_run=prior_gate,
            seed_namespace="test:r3",
            model_timeout_sec=600,
        )


def test_r3_skipped_no_active_accepts_only_exact_upstream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "run"
    candidate_id = "t07_r02"
    case_id = f"{pipeline.PROBLEM_ID}.{candidate_id}"
    resolve_run = root / "lane/05_resolver2"
    prior_gate = root / "lane/04_gate"
    third_dir = root / "lane/06_resolver3"
    source_path = resolve_run / "resolved_proof.md"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("Exact R2 proof.\n", encoding="utf-8")
    source_hash = repair_boundary.sha256_text(source_path.read_text().strip())
    pipeline.write_json(
        third_dir / "manifest.json",
        {
            "schema": "cognitive-well-v0105-iterated-ungrouped-resolve-manifest-v1",
            "source_resolve_runs": [str(resolve_run.resolve())],
            "prior_gate_run": str(prior_gate.resolve()),
            "models": {"gemma": repair_boundary.GEMMA_MODEL},
            "cases": [
                {
                    "case_id": case_id,
                    "problem_id": pipeline.PROBLEM_ID,
                    "candidate_id": candidate_id,
                    "second_proof_path": str(source_path.resolve()),
                    "second_proof_sha256": source_hash,
                }
            ],
        },
    )
    ledger_path = third_dir / "cases" / case_id / "updated_obligation_ledger.json"
    pipeline.write_json(
        ledger_path, {"entries": [], "active_count": 0, "active_obligations": []}
    )
    pipeline.write_json(
        third_dir / "summary.json",
        {
            "state": "completed",
            "rows": [
                {
                    "case_id": case_id,
                    "candidate_id": candidate_id,
                    "second_proof_path": str(source_path.resolve()),
                    "second_proof_sha256": source_hash,
                    "third_proof_path": str(source_path.resolve()),
                    "third_proof_sha256": source_hash,
                    "third_resolve_state": "skipped_no_active_obligations",
                }
            ],
        },
    )
    monkeypatch.setattr(
        pipeline.v108.v105,
        "load_cases",
        lambda **_: [{"candidate_id": candidate_id}],
    )
    result = pipeline._third_checkpoint(
        third_dir,
        allowed_root=root,
        expected_candidates=(candidate_id,),
        expected_sources=[
            {
                "candidate_id": candidate_id,
                "proof_path": str(source_path.resolve()),
                "proof_sha256": source_hash,
            }
        ],
        resolve_run=resolve_run,
        prior_gate_run=prior_gate,
        seed_namespace="test:r3",
        model_timeout_sec=600,
    )
    assert result["proofs"][0]["proof_path"] == str(source_path.resolve())


@pytest.mark.parametrize("brief_verdict", ["CERTIFIED", "REJECTED"])
def test_live_orchestration_applies_boundary_to_all_four_in_every_r1_cycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, brief_verdict: str,
) -> None:
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
            "problem_sha256": pipeline.v264.EXPECTED_PROBLEM_SHA256,
            "candidate_id": task_value["candidate_id"],
            "proof_sha256": task_value["proof_sha256"],
            "problem_path": str(Path(case["problem_path"]).resolve()),
            "proof_path": str(Path(case["proof_path"]).resolve()),
            "seed": 17,
        }

    def fake_r1_run(**kwargs: Any) -> dict[str, Any]:
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
                "task_id": f"imo2026_p5.{candidate_id}.fusion.t04",
                "candidate_id": candidate_id,
                **reviewer_values,
            }
            case_lane = stage_dir / "cases" / f"imo2026_p5.{candidate_id}"
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
        raise AssertionError("R1-C3 must be terminal: no downstream model calls")

    monkeypatch.setattr(pipeline.stage.fusion, "run_task", fake_fusion_run)
    monkeypatch.setattr(pipeline.stage, "build_resolver_task", fake_builder)
    monkeypatch.setattr(
        pipeline.repair_boundary, "audit_fusion_before_resolver", fake_gate
    )
    monkeypatch.setattr(pipeline.stage, "run", fake_r1_run)
    monkeypatch.setattr(pipeline.v108.v098, "run", forbidden_downstream)
    monkeypatch.setattr(pipeline.v108, "run_direct_ungrouped_resolve", forbidden_downstream)
    monkeypatch.setattr(pipeline.v108.v105, "run", forbidden_downstream)

    result = pipeline.run_pipeline(
        output_dir=tmp_path / "live",
        authorize_model_calls=True,
    )
    assert result["state"] == "completed"
    assert len(gate_calls) == 12
    assert {cycle for cycle, _, _ in gate_calls} == {"R1-C1", "R1-C2", "R1-C3"}
    for cycle in (2, 3):
        assert cycle_inputs[cycle] == cycle_outputs[cycle - 1]

    assert result["completed_lane_count"] == 4
    assert result["terminal_checkpoint"] == "R1-C3"
    assert [row["checkpoint"] for row in result["checkpoints"]] == [
        "baseline", *pipeline.STAGE_ORDER,
    ]
    for candidate_id, lane in result["lanes"].items():
        assert lane["state"] == "completed"
        assert lane["current_proof"]["proof_sha256"] == cycle_outputs[3][candidate_id]
        assert [row["checkpoint"] for row in lane["checkpoints"]] == [
            "baseline", *pipeline.STAGE_ORDER,
        ]
        lane_root = tmp_path / "live/lanes" / candidate_id
        assert pipeline.read_object(lane_root / "status.json")["stage"] == "R1-C3"
        for name in ("04_post_r1_cycle3_audit_ledger", "05_resolver2", "06_resolver3"):
            assert not (lane_root / name).exists()
    targets = pipeline.read_object(tmp_path / "live/score_targets.json")
    assert targets["checkpoints"] == result["checkpoints"]
