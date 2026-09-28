from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest import mock

from . import author_guided_replay as replay
from . import pipeline, rewrite
from . import test_harness as fixtures


def author_response(root, *, attempt=1, text=None):
    stage = pipeline.CERTIFICATE_AUTHOR_STAGE
    text = fixtures._proposal() if text is None else text
    cap = 32768 if attempt == 1 else 49152
    destination = root / f"attempt_{attempt:02d}_cap_{cap}"
    rewrite.write_record(destination / f"{stage}.raw_response.json", {"choices": [{"message": {"content": text}}]})
    forcing = fixtures._forcing(text=text, stage=stage, model=pipeline.base.DEFAULT_GEMMA_MODEL)
    rewrite.write_record(destination / f"{stage}.budget_forcing.json", forcing["metadata"]["v0257_budget_forcing"])
    return destination


class AuthorGuidedReplayTests(unittest.TestCase):
    def test_latest_notes_are_untrusted_not_a_certificate_program_acceptance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            author_response(root)
            text = fixtures._proposal().split("# Certificate Program")[0] + "# Certificate Program\n\nInvalid algebra."
            latest = author_response(root, attempt=2, text=text)
            semantics, record = replay.latest_author_semantics(root, task=fixtures._task(), model=pipeline.base.DEFAULT_GEMMA_MODEL)
            self.assertEqual(semantics, fixtures._program()["semantics"])
            self.assertEqual(Path(record["response_path"]).parent, latest)

    def test_notes_must_match_the_forced_response(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = author_response(root)
            stage = pipeline.CERTIFICATE_AUTHOR_STAGE
            rewrite.write_record(destination / f"{stage}.raw_response.json", {"choices": [{"message": {
                "content": fixtures._proposal().replace("D1 and D2 are exactly", "D1 and D2 are precisely")}}]})
            with self.assertRaisesRegex(ValueError, "canonical forced response"):
                replay.latest_author_semantics(root, task=fixtures._task(), model=pipeline.base.DEFAULT_GEMMA_MODEL)

    def test_malformed_latest_response_does_not_select_an_older_one(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            author_response(root)
            author_response(root, attempt=2, text="No required semantic sections.")
            with self.assertRaises(ValueError):
                replay.latest_author_semantics(root, task=fixtures._task(), model=pipeline.base.DEFAULT_GEMMA_MODEL)

    def test_rejected_author_algebra_never_replaces_the_saved_witness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task, context = fixtures._task(), fixtures._context(root / "context")
            rewrite.write_record(root / "context/result.json", {"state": "completed"})
            provider = mock.Mock(markdown="immutable checked mathematics", verification={
                "markdown_sha256": "frozen_witness", "target_label_latex": "T"})

            def author(**kwargs):
                self.assertEqual(kwargs["task"].source_proof, task.source_proof)
                self.assertEqual(kwargs["task"].additional_documents["saved_exact_witness.md"], provider.markdown)
                author_response(kwargs["output_dir"])
                raise ValueError("model algebra did not verify")

            def synthesize(**kwargs):
                self.assertIs(kwargs["adapter"].evidence_provider, provider)
                return {"terminal_proof": str(root / "output/proof.md"), "terminal_proof_sha256": "synthetic"}

            with mock.patch.object(replay, "load_current_context", return_value=(task, context, 14)), \
                    mock.patch.object(replay, "SavedWitnessProvider", return_value=provider), \
                    mock.patch.object(pipeline, "generate_provider", side_effect=author) as generation, \
                    mock.patch.object(pipeline.synthesis_pipeline, "run", side_effect=synthesize), \
                    mock.patch.object(pipeline, "_verify_synthesis_budget_forcing", return_value=[{"verified": True}]), \
                    mock.patch.object(pipeline, "_with_user_semantics", wraps=pipeline._with_user_semantics) as notes:
                result = replay.run(root / "context", root / "output", master_seed=1)
            self.assertEqual(result["state"], "completed")
            self.assertFalse(result["compact_author_algebra_verified"])
            self.assertFalse(result["model_authored_algebra_used"])
            self.assertEqual(generation.call_count, 1)
            self.assertEqual(notes.call_args.args[1], fixtures._program()["semantics"])


if __name__ == "__main__":
    unittest.main()
