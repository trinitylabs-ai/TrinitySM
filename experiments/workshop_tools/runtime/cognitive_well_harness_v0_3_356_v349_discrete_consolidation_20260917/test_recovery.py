from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from . import experiment, pipeline, protocol, recovery, rewrite, saved_witness


def audit_text(*, accepted, rationale=None):
    checks = "\n".join(f"- {label}: {'FAIL' if index == 3 and not accepted else 'PASS'}"
                       for index, label in enumerate(recovery.acquisition.POST_SINGULAR_CHECKS))
    text = f"# Decision\n\n{'ACCEPT' if accepted else 'REJECT'}\n\n# Checks\n\n{checks}\n\n# Issues\n\n"
    text += "NONE" if accepted else "- A division requires an unproved nonzero condition."
    if rationale is not None:
        text += "\n\n# Reassessment\n\n" + rationale
    return text


class RecoveryTests(unittest.TestCase):
    def test_mechanical_resume_cannot_resample_semantic_rejection_or_failed_synthesis(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            for stage in ("qwen_semantic_reassessment", "proof_synthesis"):
                rewrite.write_record(source / "result.json", {"state": "failed_closed", "stage": stage,
                    "reused_case_certificate": True})
                with self.assertRaisesRegex(ValueError, "stopped before synthesis"), mock.patch.object(rewrite, "synthesize_promoted") as synthesize:
                    recovery.resume_accepted_synthesis(source, root / "output", master_seed=1)
                synthesize.assert_not_called()
            self.assertFalse((root / "output").exists())

    def test_controller_resumes_rendering_once_without_new_audit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            proof = root / "source.md"
            pipeline.base.write_text(proof, "original proof")
            config = root / "config.json"
            rewrite.write_record(config, {"problem_file": str(proof), "strict_skill_launcher": str(proof),
                "master_seed": 4, "pilot_score": 7, "portfolio_minimum_score": 6,
                "proofs": [{"label": "first", "path": str(proof)}]})
            output = root / "portfolio"
            rewrite.write_record(output / "first/rewrite/result.json", {"state": "failed_closed"})
            rewrite.write_record(output / "first/semantic_recovery_01/result.json", {
                "state": "failed_closed", "stage": "verified_certificate_rendering", "reused_case_certificate": True})
            commands = []

            def worker(command, *args, **kwargs):
                commands.append(command)
                target = Path(command[command.index("--output-dir") + 1])
                if "--resume-accepted-synthesis" in command:
                    terminal = target / "terminal_proof.md"
                    pipeline.base.write_text(terminal, "completed synthetic proof")
                    rewrite.write_record(target / "result.json", {"state": "completed", "fresh_detection": True,
                        "problem_id": "toy", "terminal_proof": str(terminal),
                        "terminal_proof_sha256": pipeline.base.sha256_text("completed synthetic proof")})
                else:
                    rewrite.write_record(target / "summary.json", {"state": "completed", "policy_mode": "strict",
                        "rows": [{"problem_id": "toy", "proof_sha256": pipeline.base.sha256_text("completed synthetic proof"),
                            "grade": {"score": 7}}]})
                return 0

            with mock.patch.object(recovery, "eligible_rejections", return_value=["t10"]), mock.patch.object(experiment, "wait_process", side_effect=worker):
                result = experiment.run(config, output)
                repeated = experiment.run(config, output)
            self.assertEqual(result["score_vector"], [7])
            self.assertEqual(repeated["state"], "completed")
            self.assertEqual(len(commands), 2)
            self.assertIn("--resume-accepted-synthesis", commands[0])
            self.assertIn("--proof-task", commands[1])

    def test_fresh_exact_route_connects_to_verified_witness_provider(self):
        from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.test_integration import GenericLaurentIntegrationTests
        fixture = GenericLaurentIntegrationTests()
        fixture.setUp()
        arguments = fixture.arguments
        semantics = "\n".join(f"- {name}: the explicitly supplied synthetic equations and domain"
            for name in ("Source basis", "Target meaning", "Domain and branch conditions", "Formalization map", "Sufficiency argument", "Rewrite consequence"))
        guard = protocol._render_ast(fixture.guard_program["provenance_divisions"]["ratio"]["denominator"])
        generators = "\n".join(f"generator = {name} :: {protocol._render_ast(value)}" for name, value in arguments["generators"].items())
        formal = f"# Semantic Bindings\n\n{semantics}\n\n# Guard Program\n\n```guard-args\nprovenance_division = ratio :: 1 :: {guard}\n```\n\n# Tool Arguments\n\n```tool-args\noperation = polynomial_ideal_membership\nsymbols = {', '.join(arguments['symbols'])}\n{generators}\ntarget = {protocol._render_ast(arguments['target'])}\n```"
        parsed = recovery.acquisition.parse_guarded_formalization(formal)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            label = "t10repair1"
            formal_root = root / "03_guarded_formalizations" / label
            pipeline.base.write_text(formal_root / "formalization_raw.md", formal)
            pipeline.base.write_text(formal_root / "formalization.md", parsed["normalized_markdown"])
            problem = mock.Mock(problem_id="toy", statement="Assume the displayed synthetic equations and x+y nonzero; prove the target equation.")
            proof = "The target is exactly one of the explicit hypotheses."
            pipeline.base.write_text(root / "input/original_theorem.md", problem.statement)
            pipeline.base.write_text(root / "input/resolver1_proof.md", proof)
            detection = "# Decision\n\nCALL_TOOL\n\n# Load-Bearing Gap\n\nThe target is asserted.\n\n# Trigger Evidence\n\nThe target is exactly one of the explicit hypotheses.\n\n# Evidence Task\n\nCERTIFY_DERIVATION\n\n# Desired Exact Fact\n\nthe supplied target equation\n\n# Downstream Obligation\n\nProve the target equation."
            matcher = "# Decision\n\nCALL_TOOL\n\n# Operation\n\npolynomial_ideal_membership\n\n# Immutable Claim\n\nthe supplied target equation\n\n# Fit Rationale\n\nAn algebraic consequence of the supplied equations."
            pipeline.base.write_text(root / "01_detection/detection.md", detection)
            pipeline.base.write_text(root / "02_matcher/matcher.md", matcher)
            route_root = root / "05_direct_laurent_routes" / label
            route = recovery.certify(parsed, route_root, label)
            self.assertEqual(route["state"], "singular_proved")
            audit_root = root / "06_post_singular_audits" / label
            text = audit_text(accepted=True)
            pipeline.base.write_text(audit_root / "audit.md", text)
            rewrite.write_record(audit_root / "result.json", {"state": "accepted",
                "audit": recovery.acquisition.parse_post_singular_audit(text),
                "formalization_sha256": pipeline.base.sha256_text(parsed["normalized_markdown"]),
                "exact_result_supplied": False, "laurent_outcome_supplied": False})
            rewrite.write_record(root / "07_selection/selection.json", {"selected_label": label})
            task, context = rewrite.promoted_context(problem=problem, proof=proof, formalization=parsed,
                route=route, route_root=route_root, acquisition_root=root, audit_root=audit_root,
                matcher={"operation": "polynomial_ideal_membership", "claim": "the supplied target equation"})
            self.assertEqual(task.source_proof, proof)
            self.assertEqual(task.additional_documents["tool_detection.md"], detection)
            self.assertEqual(task.additional_documents["tool_matcher.md"], matcher)
            provider = saved_witness.SavedWitnessProvider(context)
            self.assertTrue(provider.materialize().verification["verified"])
            from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.tool_purpose import purpose_records
            self.assertEqual(purpose_records(task, provider.materialize()), (detection, matcher))
            pipeline.base.write_text(root / "01_detection/detection.md", "changed purpose")
            with self.assertRaisesRegex(ValueError, "drift"):
                provider.materialize()
            pipeline.base.write_text(root / "01_detection/detection.md", detection)
            pipeline.base.write_text(audit_root / "audit.md", "changed")
            with self.assertRaisesRegex(ValueError, "drift"):
                provider.materialize()

    def test_reassessment_keeps_strict_audit_checks(self):
        result = recovery.parse_reassessment(audit_text(accepted=False, rationale="The actual denominator needs the disputed nonzero condition."))
        self.assertFalse(result["audit"]["accepted"])
        self.assertIn("actual denominator", result["rationale"])
        accepted = recovery.parse_reassessment(audit_text(accepted=True, rationale="The disputed symbol is nonzero by the explicitly stated hypothesis x>0."))
        self.assertTrue(accepted["audit"]["accepted"])
        with self.assertRaises(ValueError):
            recovery.parse_reassessment(audit_text(accepted=True, rationale="NONE"))
        with self.assertRaises(ValueError):
            recovery.parse_reassessment(audit_text(accepted=False, rationale="A label was wrong.").replace("\nREJECT\n", "\nACCEPT\n"))

    def test_repair_prompt_contains_feedback_not_exact_results(self):
        problem = mock.Mock(statement="toy theorem")
        text = recovery.repair_prompt(problem, "toy proof", "immutable gap", "immutable operation", "typed input", "guard needs proof")
        self.assertIn("guard needs proof", text)
        self.assertIn("Do not change the detected", text)
        self.assertNotIn("PROVED", text)
        self.assertNotIn("7/7", text)

    def test_eligibility_rebinds_rejected_audit_to_formalization(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            root = source / "01_acquisition"
            arm = root / "03_guarded_formalizations/t10/formalization.md"
            pipeline.base.write_text(arm, "typed toy formalization")
            audit_root = root / "06_post_singular_audits/t10"
            text = audit_text(accepted=False)
            pipeline.base.write_text(audit_root / "audit.md", text)
            rewrite.write_record(audit_root / "result.json", {"state": "rejected",
                "audit": recovery.acquisition.parse_post_singular_audit(text),
                "formalization_sha256": pipeline.base.sha256_text("typed toy formalization"),
                "exact_result_supplied": False, "laurent_outcome_supplied": False})
            rewrite.write_record(root / "05_direct_laurent_routes/t10/route_state.json", {"state": "singular_proved"})
            self.assertEqual(recovery.eligible_rejections(source), ["t10"])
            arm.write_text("changed input", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "binding"):
                recovery.eligible_rejections(source)

    def test_controller_resumes_once_then_scores_without_repeating_detection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "proof.md"
            source.write_text("original proof", encoding="utf-8")
            config_path = root / "config.json"
            config = {"problem_file": str(source), "strict_skill_launcher": str(source), "master_seed": 4,
                "pilot_score": 7, "portfolio_minimum_score": 6, "proofs": [{"label": "first", "path": str(source)}]}
            rewrite.write_record(config_path, config)
            output = root / "portfolio"
            failed = output / "first/rewrite"
            rewrite.write_record(failed / "result.json", {"state": "failed_closed", "error": "semantic rejection"})
            commands = []

            def worker(command, *args, **kwargs):
                commands.append(command)
                target = Path(command[command.index("--output-dir") + 1])
                if "--source-run" in command:
                    proof = target / "proof.md"
                    pipeline.base.write_text(proof, "new standalone proof")
                    rewrite.write_record(target / "result.json", {"state": "completed", "fresh_detection": True,
                        "problem_id": "toy", "terminal_proof": str(proof),
                        "terminal_proof_sha256": pipeline.base.sha256_text("new standalone proof")})
                else:
                    rewrite.write_record(target / "summary.json", {"state": "completed", "policy_mode": "strict",
                        "rows": [{"problem_id": "toy", "proof_sha256": pipeline.base.sha256_text("new standalone proof"), "grade": {"score": 7}}]})
                return 0

            with mock.patch.object(recovery, "eligible_rejections", return_value=["t10"]), mock.patch.object(experiment, "wait_process", side_effect=worker):
                result = experiment.run(config_path, output)
                repeated = experiment.run(config_path, output)
            self.assertEqual(result["score_vector"], [7])
            self.assertEqual(repeated["state"], "completed")
            self.assertEqual(len(commands), 2)
            self.assertIn("--source-run", commands[0])
            self.assertIn("--proof-task", commands[1])
            self.assertNotIn("--proof-file", commands[0])

    def test_failed_recovery_is_not_sampled_again(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "proof.md"
            source.write_text("original proof", encoding="utf-8")
            config_path = root / "config.json"
            rewrite.write_record(config_path, {"problem_file": str(source), "strict_skill_launcher": str(source),
                "master_seed": 4, "pilot_score": 7, "portfolio_minimum_score": 6,
                "proofs": [{"label": "first", "path": str(source)}]})
            output = root / "portfolio"
            for directory in ("rewrite", "semantic_recovery_01"):
                rewrite.write_record(output / "first" / directory / "result.json", {"state": "failed_closed", "error": "still rejected"})
            with mock.patch.object(recovery, "eligible_rejections", return_value=["t10"]), mock.patch.object(experiment, "wait_process") as worker:
                result = experiment.run(config_path, output)
            self.assertEqual(result["state"], "needs_generic_refinement")
            worker.assert_not_called()


if __name__ == "__main__":
    unittest.main()
