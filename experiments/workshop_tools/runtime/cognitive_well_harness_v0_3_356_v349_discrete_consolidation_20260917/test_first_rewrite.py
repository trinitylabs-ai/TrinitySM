from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import EvidenceBundle, SynthesisAdapter
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import prompts, tool_purpose
from . import certificate, first_rewrite, pipeline
from . import test_harness as fixtures


def adapter_at(root):
    context = fixtures._context(root / "context")
    verified = certificate.verify_and_render(context=context, proposal_markdown=fixtures._proposal())
    evidence = EvidenceBundle("synthetic_verified", "VERIFIED_SUPPORT", verified["markdown"],
        verified["verification"], dict(fixtures.EXACT_REPLAY), context.source_artifacts)
    task = fixtures._task()
    claim = fixtures.EXACT_REPLAY["claim"]
    detection = f"# Decision\n\nCALL_TOOL\n\n# Load-Bearing Gap\n\nThe square identity needs a derivation.\n\n# Trigger Evidence\n\n{task.source_proof}\n\n# Evidence Task\n\nCERTIFY_DERIVATION\n\n# Desired Exact Fact\n\n{claim}\n\n# Downstream Obligation\n\nProve the requested square identity."
    matcher = f"# Decision\n\nCALL_TOOL\n\n# Operation\n\npolynomial_ideal_membership\n\n# Immutable Claim\n\n{claim}\n\n# Fit Rationale\n\nThe target is an algebraic consequence."
    task = replace(task, additional_documents={tool_purpose.DETECTION_DOCUMENT: detection,
        tool_purpose.MATCHER_DOCUMENT: matcher, "ignored.md": "DO_NOT_FEED_OLD_REVIEWS"})
    return SynthesisAdapter("synthetic_first_rewrite", task, SimpleNamespace(materialize=lambda: evidence),
        pipeline._generic_contract(fixtures._program()))


class Calls:
    def __init__(self, passed=True):
        self.passed = passed
        self.requests = []

    def __call__(self, **kwargs):
        self.requests.append(kwargs)
        Path(kwargs["destination"]).mkdir(parents=True, exist_ok=False)
        if kwargs["stage"].endswith("_audit"):
            text = fixtures._audit_markdown()
            if not self.passed:
                text = text.replace("\nPASS\n", "\nFAIL\n", 1).replace(": PASS", ": FAIL", 1)
                text = text.replace("\nNONE", "\n- Derive the missing connection.")
            reason = "The submitted equation x^2=1 closes this link." if self.passed else "MISSING: the link needs an explicit derivation."
            closure = "# Gap Closure\n\n" + "\n".join(f"- {label}: {reason}" for label in tool_purpose.GAP_CLOSURE_LABELS)
            text = text.replace("# Issues", closure + "\n\n# Issues")
        else:
            text = fixtures._proof_markdown()
        return text, kwargs["parser"](text), fixtures._forcing(text=text, stage=kwargs["stage"], model=kwargs["role"].model)


class FirstRewriteTests(unittest.TestCase):
    def test_profile_changes_only_cycle_limit_and_has_no_previous_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter = adapter_at(Path(directory))
            prepared, record = first_rewrite.prepare(adapter)
            self.assertIs(prepared.task, adapter.task)
            self.assertIs(prepared.evidence_provider, adapter.evidence_provider)
            self.assertEqual(prepared.contract, replace(adapter.contract, max_cycles=1))
            self.assertEqual(adapter.contract.max_cycles, 3)
            user = prompts.rewrite_prompt(task=prepared.task, evidence=prepared.evidence_provider.materialize(),
                contract=prepared.contract, previous_proof=None, prior_audit=None)
            self.assertEqual(record["first_rewrite_user_prompt_sha256"], pipeline.base.sha256_text(user))
            self.assertIn("# Previous Replacement Proof\n\nNONE", user)
            self.assertIn("# Prior Jury Issues\n\nNONE", user)
            self.assertNotIn("DO_NOT_FEED_OLD_REVIEWS", user)
            self.assertEqual(user.count(tool_purpose.EXPLICIT_BEGIN), 1)

    def test_default_profile_is_one_budget_forced_rewrite_and_one_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = adapter_at(root)
            calls = Calls()
            result = first_rewrite.run(adapter=adapter, output_dir=root / "run", master_seed=9,
                prior_model_stages=21, model_call=calls)
            self.assertEqual(result["state"], "completed")
            self.assertTrue(result["proof_audit_passed"])
            self.assertEqual(len(calls.requests), 2)
            self.assertEqual([call["role"].temperature for call in calls.requests], [0.2, 0.1])
            self.assertEqual(len(result["synthesis_budget_forcing"]), 1)
            self.assertTrue(Path(result["terminal_proof"]).is_file())
            self.assertFalse((root / "run/strict_score").exists())
            self.assertEqual(json.loads((root / "run/02_synthesis/contract.json").read_text())["max_cycles"], 1)
            self.assertIn("# Gap Closure", calls.requests[1]["system_prompt"])

    def test_rejection_retains_submission_without_promoting_or_retrying(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = Calls(passed=False)
            result = first_rewrite.run(adapter=adapter_at(root), output_dir=root / "run", master_seed=9, model_call=calls)
            self.assertEqual(result["state"], "failed_closed")
            self.assertFalse(result["proof_audit_passed"])
            self.assertEqual(len(calls.requests), 2)
            self.assertTrue(Path(result["submitted_proof"]).is_file())
            self.assertNotIn("terminal_proof", result)
            self.assertFalse((root / "run/02_synthesis/terminal_proof.md").exists())

    def test_missing_context_and_exhausted_budget_make_no_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = adapter_at(root)
            calls = Calls()
            for count in (23, -1, True):
                with self.assertRaisesRegex(ValueError, "24-stage"):
                    first_rewrite.run(adapter=adapter, output_dir=root / "run", master_seed=9,
                        prior_model_stages=count, model_call=calls)
            with self.assertRaisesRegex(ValueError, "requires recorded"):
                first_rewrite.prepare(replace(adapter, task=replace(adapter.task, additional_documents={})))
            self.assertFalse(calls.requests)
            self.assertFalse((root / "run").exists())

    def test_runtime_profile_has_no_benchmark_artifact_or_score_inputs(self):
        source = Path(first_rewrite.__file__).read_text()
        for text in ("imo2026_p2", "t07_r01", "B-C", "v0324r7", "score_from_summary", "legacy_problem_specific"):
            self.assertNotIn(text, source)


if __name__ == "__main__":
    unittest.main()
