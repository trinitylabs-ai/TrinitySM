"""Core controller tests: no model or algebra calls."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from . import experiment, recovery, rewrite


class PortfolioTests(unittest.TestCase):
    def portfolio(self, outcomes, **flags):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        proofs = []
        for index in range(len(outcomes)):
            path = root / f"source_{index}.md"
            path.write_text(f"distinct synthetic proof {index}", encoding="utf-8")
            proofs.append({"label": f"case_{index}", "path": str(path)})
        config = {"problem_file": proofs[0]["path"], "strict_skill_launcher": proofs[0]["path"],
                  "master_seed": 1, "pilot_score": 7, "portfolio_minimum_score": 6,
                  "proofs": proofs, **flags}
        config_path = root / "config.json"
        rewrite.write_record(config_path, config)
        commands = []

        def worker(command, *args, **kwargs):
            commands.append(command)
            target = Path(command[command.index("--output-dir") + 1])
            index = int(target.parent.name.split("_")[-1])
            target.mkdir(parents=True)
            if "--proof-file" in command:
                if outcomes[index] is None:
                    rewrite.write_record(target / "result.json", {"state": "failed_closed", "stage": "acquisition", "error": "rejected"})
                else:
                    proof = target / "terminal.md"
                    proof.write_text(f"synthetic terminal {index}", encoding="utf-8")
                    rewrite.write_record(target / "result.json", {"state": "completed", "fresh_detection": True,
                        "problem_id": "toy", "terminal_proof": str(proof), "terminal_proof_sha256": experiment.digest(proof)})
                if config.get("entrypoint") == "proof_harness":
                    from .proof_harness import SCHEMA
                    source = target / "input/source_proof.md"
                    source.parent.mkdir()
                    source.write_text(Path(proofs[index]["path"]).read_text())
                    rewrite.write_record(target / "manifest.json", {"schema": SCHEMA, "problem_id": "toy",
                        "preloaded_certificate": False, "input_artifacts": {"input/source_proof.md": experiment.digest(source)}})
                    result = experiment.read(target / "result.json")
                    result.update(schema=SCHEMA, proof_audit_passed=outcomes[index] is not None)
                    if outcomes[index] is not None:
                        result.update(outcome="REWRITTEN_AUDIT_PASS", rewritten_proof=str(proof),
                                      rewritten_proof_sha256=experiment.digest(proof))
                    rewrite.write_record(target / "result.json", result)
            else:
                proof = target.parent / "rewrite/terminal.md"
                rewrite.write_record(target / "summary.json", {"state": "completed", "policy_mode": "strict",
                    "rows": [{"problem_id": "toy", "proof_sha256": experiment.digest(proof), "score": outcomes[index]}]})
            return 0

        with mock.patch.object(experiment, "wait_process", side_effect=worker), mock.patch.object(recovery, "eligible_rejections", return_value=[]):
            result = experiment.run(config_path, root / "output")
            repeated = experiment.run(config_path, root / "output")
        self.assertEqual(result, repeated)
        return result, commands, config

    def test_disabled_gate_runs_all_three_and_resume_reuses_results(self):
        result, commands, _ = self.portfolio([4, 6, 5], pilot_gate_enabled=False)
        self.assertEqual(result["score_vector"], [4, 6, 5])
        self.assertEqual(result["state"], "completed")
        self.assertEqual(len(commands), 6)

    def test_terminal_rejection_is_not_scored_or_promoted_and_does_not_stop_next(self):
        result, commands, _ = self.portfolio([None, 6, 4], pilot_gate_enabled=False, continue_on_case_failure=True)
        self.assertEqual(result["score_vector"], [None, 6, 4])
        self.assertEqual(result["failed_cases"], ["case_0"])
        self.assertEqual(result["cases"][0]["state"], "failed_closed")
        self.assertEqual(len(commands), 5)

    def test_all_rejected_has_no_fake_score(self):
        result, commands, _ = self.portfolio([None, None, None], continue_on_case_failure=True)
        self.assertEqual(result["score_vector"], [None, None, None])
        self.assertIsNone(result["best_score"])
        self.assertEqual(result["state"], "needs_generic_refinement")
        self.assertEqual(len(commands), 3)

    def test_default_pilot_gate_and_boolean_validation_are_preserved(self):
        result, commands, config = self.portfolio([4, 7])
        self.assertEqual(result["stage"], "pilot_gate_not_met")
        self.assertEqual(len(commands), 2)
        for flag in ("pilot_gate_enabled", "continue_on_case_failure"):
            with self.assertRaisesRegex(ValueError, "boolean"):
                experiment.validate_config({**config, flag: "false"})

    def test_current_packaged_harness_runs_all_cases_and_preserves_resume(self):
        result, commands, _ = self.portfolio([None, 7, 4], entrypoint="proof_harness",
            pilot_gate_enabled=False, continue_on_case_failure=True)
        self.assertEqual(result["score_vector"], [None, 7, 4])
        self.assertEqual(len(commands), 5)
        for command in commands:
            if "--proof-file" in command:
                self.assertIn("--execute-models", command)
                self.assertTrue(command[command.index("-m") + 1].endswith(".proof_harness"))
            else:
                self.assertIn("--model-output-format", command)

    def test_unknown_entrypoint_rejected(self):
        _, _, config = self.portfolio([7])
        with self.assertRaisesRegex(ValueError, "entrypoint"):
            experiment.validate_config({**config, "entrypoint": "unrelated_worker"})


if __name__ == "__main__":
    unittest.main()
