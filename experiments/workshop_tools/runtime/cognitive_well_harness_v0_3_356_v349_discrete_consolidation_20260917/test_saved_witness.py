from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import sympy as sp

from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import integration
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import test_integration as fixtures
from . import pipeline, saved_witness
from .certificate import GenericCertificateContext


class UnitWitnessRenderingTests(unittest.TestCase):
    def _certificate(self, root):
        fixture = fixtures.GenericLaurentIntegrationTests()
        fixture.setUp()
        arguments = fixture.arguments
        # Both linear equations acquire a Laurent-unit factor in their pivot
        # coefficients. No source nonzero assumption is necessary or supplied.
        arguments["generators"]["D2"] = {"sub": [{"symbol": "r"}, {"symbol": "x"}]}
        arguments["generators"]["D3"] = {"sub": [{"symbol": "r"}, {"symbol": "y"}]}
        arguments["target"] = arguments["generators"]["D3"]
        guards = {"source_nonzero": {}, "provenance_divisions": {}}
        validation = {"decision": "ACCEPT",
            "source_arguments_sha256": pipeline.exact_tools.stable_hash(arguments),
            "candidate_arguments_sha256": pipeline.exact_tools.stable_hash(arguments),
            "guard_program_sha256": pipeline.exact_tools.stable_hash(guards)}
        result = integration.preprocess_and_execute(source_arguments=arguments,
            candidate_arguments=arguments, guard_program=guards,
            exact_transformation_validation=validation, output_dir=root,
            singular_binary=fixture.singular, timeout_sec=10, memory_mb=1024)
        self.assertEqual(result["state"], "proved")
        self.assertTrue(integration.verify_exported_membership_identity(output_dir=root, result=result)["verified"])
        lift_path = root / "full_source_lift_certificate.json"
        lift = json.loads(lift_path.read_text())
        self.assertTrue(lift["linear_elimination"]["performed"])
        self.assertEqual(json.loads((root / "typed_guard_binding.json").read_text())["eligible_records"], [])
        source = root / "source.md"
        pipeline.base.write_text(source, "Assume x^2+y^2=1, r=x, and r=y. Prove r=y.")
        exact = root / "exact.md"
        pipeline.base.write_text(exact, "Checked synthetic certificate")
        context = GenericCertificateContext(certificate_id="synthetic_unit_pivot",
            theorem=source.read_text(), arguments=arguments, typed_guards={},
            replay_formal_request=lambda: arguments,
            replay_exact=lambda: {"schema": "synthetic-verified-replay-v1", "verified": True, "operation": "polynomial_ideal_membership",
                "claim": "synthetic implication", "verdict": "VERIFIED_SUPPORT"},
            formal_request_markdown=source.read_text(), exact_result_markdown=exact.read_text(),
            source_artifacts={"formal_request": source, "exact_result": exact,
                "membership_identity": root / "derived_identity_certificate.json", "source_lift": lift_path})
        return context, lift

    def test_unit_inverse_witness_renders_without_source_guards(self):
        with tempfile.TemporaryDirectory() as temporary:
            context, lift = self._certificate(Path(temporary) / "exact")
            provider = saved_witness.SavedWitnessProvider(context)
            self.assertTrue(provider.materialize().verification["verified"])
            unit = sp.Symbol(lift["circle_identities"][0]["unit"])
            self.assertIn(f"{sp.latex(unit)}=(", provider.markdown)
            self.assertIn("inverse identities", provider.markdown)

    def test_missing_unit_inverse_witness_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            context, lift = self._certificate(Path(temporary) / "exact")
            lift["circle_identities"] = []
            pipeline.base.write_text(context.source_artifacts["source_lift"], json.dumps(lift))
            with self.assertRaisesRegex(ValueError, "pivot factor has no displayed nonzero witness"):
                saved_witness.render(context)

    def test_unit_name_and_saved_flag_do_not_replace_source_circle(self):
        with tempfile.TemporaryDirectory() as temporary:
            context, lift = self._certificate(Path(temporary) / "exact")
            lift["circle_identities"][0]["label"] = "D2"
            pipeline.base.write_text(context.source_artifacts["source_lift"], json.dumps(lift))
            with self.assertRaisesRegex(ValueError, "matching source circle"):
                saved_witness.render(context)


if __name__ == "__main__":
    unittest.main()
