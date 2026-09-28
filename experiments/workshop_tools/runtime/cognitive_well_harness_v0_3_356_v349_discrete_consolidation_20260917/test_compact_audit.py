import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from . import compact_audit, pipeline, saved_witness


class CompactAuditTests(unittest.TestCase):
    def setUp(self):
        self.statement = ("## Algebraic lemma\n\nAssume the following equations and nonzero conditions, in the variables displayed:"
            "\n\nD1=x*x-1=0.\n\ng1=x+1 != 0.\n\nWe will prove that T=x-1=0.")
        self.evidence = self.statement + saved_witness.STATEMENT_END + "i^2=-1.\n\nINTERNAL_WITNESS_ONLY"
        self.verification = {"schema": "cognitive-well-v0324-lossless-saved-witness-presentation-v1",
            "verified": True, "horner_and_cse_reexpanded": True,
            "markdown_sha256": pipeline.base.sha256_text(self.evidence)}
        self.proof = "NEW_INPUT_CONNECTION\n\n" + self.evidence + "\n\nNEW_OUTPUT_CONNECTION"
        self.prefix = "# Original Theorem\n\nAn abstract theorem.\n\n# Untrusted Source Proof for Comparison Only\n\nORIGINAL_CALCULATION\n\n"
        self.prompt = self.prefix + compact_audit.REPLACEMENT_HEADING + self.proof

    def test_exact_statement_and_surrounding_proof_preserved(self):
        prompt, view, record = compact_audit.compact_prompt(user_prompt=self.prompt,
            proof=self.proof, evidence=self.evidence, verification=self.verification)
        self.assertEqual(view, "NEW_INPUT_CONNECTION\n\n" + self.statement + compact_audit.OMISSION + "\n\nNEW_OUTPUT_CONNECTION")
        self.assertTrue(prompt.startswith(self.prefix))
        self.assertTrue(prompt.endswith(view))
        self.assertNotIn("INTERNAL_WITNESS_ONLY", prompt)
        self.assertEqual(record["statement_characters"], len(self.statement))
        self.assertTrue(record["surrounding_proof_unchanged"])

    def test_unverified_or_changed_certificate_rejected(self):
        for changes in ({"verified": False}, {"schema": "unknown"},
                {"horner_and_cse_reexpanded": False}, {"markdown_sha256": "wrong"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                saved_witness.audit_statement(self.evidence, {**self.verification, **changes})

    def test_missing_or_ambiguous_boundary_rejected(self):
        for evidence in (self.statement, self.evidence + saved_witness.STATEMENT_END):
            with self.assertRaises(ValueError):
                saved_witness.audit_statement(evidence, {**self.verification,
                    "markdown_sha256": pipeline.base.sha256_text(evidence)})

    def test_changed_or_duplicate_submission_rejected(self):
        for proof in (self.proof.replace("NEW_OUTPUT_CONNECTION", "CHANGED"),
                self.proof + self.evidence, "no certificate"):
            with self.assertRaises(ValueError):
                compact_audit.compact_prompt(user_prompt=self.prompt, proof=proof,
                    evidence=self.evidence, verification=self.verification)

    def test_transport_directory_exists_and_errors_are_not_resampled(self):
        record = {"endpoint": "unused", "model": "unused", "config": {"max_tokens": 32768}}
        def transport(**kwargs):
            self.assertTrue(kwargs["output_dir"].is_dir())
            raise RuntimeError("synthetic transport failure")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(compact_audit, "prepare", return_value=("system", "user", "view", record, False)), \
                    patch.object(pipeline.mandatory_budget_forcing, "install"), \
                    patch.object(pipeline.base.transport, "run_openai_chat_generation", side_effect=transport) as call:
                result = compact_audit.run(root / "source", root / "output")
            self.assertEqual(call.call_count, 1)
            self.assertEqual(result["state"], "failed_closed")
            self.assertIn("synthetic transport failure", result["error"])


if __name__ == "__main__":
    unittest.main()
