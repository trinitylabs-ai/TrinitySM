from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import sympy as sp
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import integration
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.symbol_safety import FreshNames, parse_polynomial
from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905.test_integration import GenericLaurentIntegrationTests
from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906 import prompts
from . import experiment, pipeline, rewrite, saved_witness
from .certificate import GenericCertificateContext


class GenericSafetyTests(unittest.TestCase):
    def test_ambiguous_legacy_imaginary_name_is_rejected_not_reinterpreted(self):
        variable = sp.Symbol("I")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            parse_polynomial("I", [variable])
        self.assertEqual(parse_polynomial("I+1", [variable], complex_coefficients=False), variable + 1)

    def test_fresh_names_avoid_identifier_and_display_collisions(self):
        reserved = ["T", "a", "q", "R", "i", "g1", "n_1", "m_1", "unit_1", "w1"]
        fresh = FreshNames(reserved)
        allocated = [fresh.take(name) for name in ["T", "a", "q", "R", "i", "g_1", "n1", "m_1", "unit_1", "w1"]]
        self.assertFalse(set(map(str, allocated)) & set(reserved))
        self.assertFalse({sp.latex(item) for item in allocated} & {sp.latex(sp.Symbol(item)) for item in reserved})
        self.assertEqual(len({sp.latex(item) for item in allocated}), len(allocated))

    def test_compaction_avoids_visually_equivalent_source_names(self):
        x, y, w = sp.symbols("x y w_1")
        expressions = [sp.expand((x+y)**4 + w), sp.expand((x+y)**3 + 2*w)]
        definitions, compact = saved_witness._compact(expressions, [x, y, w])
        self.assertNotIn(sp.latex(w), {sp.latex(name) for name, _ in definitions})
        resolved = {}
        for name, value in definitions:
            resolved[name] = value.xreplace(resolved)
        self.assertTrue(all(sp.expand(before-after.xreplace(resolved)) == 0 for before, after in zip(expressions, compact)))

    def test_production_import_boundary_in_clean_process(self):
        completed = subprocess.run([sys.executable, "-B", "-c",
            f"from {rewrite.__package__}.rewrite import assert_generic_boundary; assert_generic_boundary()"],
            capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_runtime_packages_have_no_legacy_adapter_imports(self):
        root = Path(__file__).resolve().parents[1]
        prefixes = ("cognitive_well_harness_v0_3_324_", "cognitive_well_harness_v0_3_309_", "cognitive_well_harness_v0_3_287_")
        for directory in root.iterdir():
            if not directory.name.startswith(prefixes):
                continue
            for path in directory.rglob("*.py"):
                if path.name.startswith("test_"):
                    continue
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                    self.assertFalse(any("legacy_problem_specific" in name or "human_readable_t10" in name for name in names), str(path))

    def test_semantic_contract_system_is_independent_of_supplied_bindings(self):
        contract = rewrite.synthesis_contract({"formalization_map": "x is the supplied real number"}, "T_cert1")
        self.assertTrue(contract.semantic_conclusion_only)
        self.assertEqual(contract.conclusion_alternatives, ())
        other = rewrite.synthesis_contract({"source_basis": "UNTRUSTED_CASE_ASSERTION"}, "OTHER_TARGET")
        self.assertEqual(prompts.rewriter_system(contract), prompts.rewriter_system(other))
        self.assertNotIn("x is the supplied real number", prompts.rewriter_system(contract))
        self.assertNotIn("T_cert1", prompts.rewriter_system(contract))
        self.assertIn("derive every source equation", prompts.rewriter_system(contract))

    def test_legacy_contract_system_is_independent_of_semantics(self):
        first = pipeline._generic_contract({"semantics": {"required_conclusion": "alpha", "source_basis": "CASE_ONE"}})
        second = pipeline._generic_contract({"semantics": {"required_conclusion": "beta", "source_basis": "CASE_TWO"}}, conclusion_label="OTHER")
        self.assertEqual(prompts.rewriter_system(first), prompts.rewriter_system(second))
        self.assertNotIn("CASE_ONE", prompts.rewriter_system(first))

    def test_legacy_semantics_are_preserved_only_in_user_context(self):
        capture = mock.Mock(return_value="ok")
        call = pipeline._with_user_semantics(capture, {"source_basis": "UNTRUSTED_CASE_ASSERTION"})
        self.assertEqual(call(system_prompt="GENERIC", user_prompt="# Original Theorem\n\nsource\n\n# Exact-Evidence Verdict\n\nVERIFIED_SUPPORT"), "ok")
        self.assertEqual(capture.call_args.kwargs["system_prompt"], "GENERIC")
        user = capture.call_args.kwargs["user_prompt"]
        self.assertIn("UNTRUSTED_CASE_ASSERTION", user)
        self.assertIn("Untrusted Context", user)
        self.assertLess(user.index("source\n"), user.index("UNTRUSTED_CASE_ASSERTION"))
        with self.assertRaisesRegex(ValueError, "boundary"):
            call(system_prompt="GENERIC", user_prompt="missing boundary")

    def test_experiment_rejects_duplicate_proofs(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.md"
            path.write_text("same proof", encoding="utf-8")
            config = {"problem_file": str(path), "strict_skill_launcher": str(path), "master_seed": 1,
                "pilot_score": 7, "portfolio_minimum_score": 6,
                "proofs": [{"label": "a", "path": str(path)}, {"label": "b", "path": str(path)}]}
            with self.assertRaisesRegex(ValueError, "distinct"):
                experiment.validate_config(config)

    def test_strict_score_nested_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rewrite.write_record(root / "summary.json", {"state": "completed", "policy_mode": "strict",
                "rows": [{"grade": {"score": 6}}]})
            self.assertEqual(experiment.score_from_summary(root)[0], 6)

    def test_model_stage_budget_stops_without_extra_calls(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls = rewrite.BudgetedCalls(Path(temporary) / "budget.json", max_stages=1)
            kwargs = dict(stage="test", destination=Path(temporary) / "call", system_prompt="s", user_prompt="u")
            with mock.patch.object(pipeline, "_mandatory_budget_forced_model_call", return_value=("ok", {}, {"attempt": 1, "cap": 32768})) as call:
                calls(**kwargs)
                with self.assertRaisesRegex(RuntimeError, "budget"):
                    calls(**kwargs)
                self.assertEqual(call.call_count, 1)

    def test_repair_context_does_not_duplicate_immutable_certificate(self):
        from cognitive_well_harness_v0_3_287_modular_exact_proof_synthesis_20260906.contracts import TaskInputs, EvidenceBundle
        contract = rewrite.synthesis_contract({}, "T")
        block = "UNIQUE IMMUTABLE MATHEMATICS"
        evidence = EvidenceBundle("generic", "VERIFIED_SUPPORT", block, {"verified": True}, {}, {})
        text = prompts.rewrite_prompt(task=TaskInputs("toy", "theorem", "source", {}), evidence=evidence,
            contract=contract, previous_proof="before " + block + " after", prior_audit=None)
        self.assertEqual(text.count(block), 1)


class RenamedWitnessTests(unittest.TestCase):
    def test_complete_saved_witness_on_three_renamed_nonbenchmark_systems(self):
        fixture = GenericLaurentIntegrationTests()
        fixture.setUp()
        for replacements in ({"r": "a", "x": "T", "y": "unit_1"},
                             {"r": "R", "x": "i", "y": "w_1"},
                             {"r": "q", "x": "g1", "y": "m_1"}):
            with self.subTest(replacements=replacements), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                def rename(value):
                    if isinstance(value, str):
                        return replacements.get(value, value)
                    if isinstance(value, list):
                        return [rename(item) for item in value]
                    if isinstance(value, dict):
                        return {key: rename(item) for key, item in value.items()}
                    return value
                arguments, guards = rename(fixture.arguments), rename(fixture.guard_program)
                validation = {"decision": "ACCEPT", "source_arguments_sha256": pipeline.exact_tools.stable_hash(arguments),
                    "candidate_arguments_sha256": pipeline.exact_tools.stable_hash(arguments), "guard_program_sha256": pipeline.exact_tools.stable_hash(guards)}
                route = root / "exact"
                result = integration.preprocess_and_execute(source_arguments=arguments, candidate_arguments=arguments,
                    guard_program=guards, exact_transformation_validation=validation, output_dir=route,
                    singular_binary=fixture.singular, timeout_sec=10, memory_mb=1024)
                self.assertEqual(result["state"], "proved")
                self.assertTrue(integration.verify_exported_membership_identity(output_dir=route, result=result)["verified"])
                source, exact = root / "source.md", root / "exact.md"
                source.write_text("Frozen synthetic input", encoding="utf-8")
                exact.write_text("Frozen exact output", encoding="utf-8")
                context = GenericCertificateContext(certificate_id="renamed", theorem="A synthetic guarded consequence",
                    arguments=arguments, typed_guards={}, replay_formal_request=lambda: arguments,
                    replay_exact=lambda: {"schema": "synthetic-verified-replay-v1", "verified": True, "operation": "polynomial_ideal_membership", "claim": "synthetic implication", "verdict": "VERIFIED_SUPPORT"},
                    formal_request_markdown=source.read_text(), exact_result_markdown=exact.read_text(),
                    source_artifacts={"formal_request": source, "exact_result": exact,
                        "membership_identity": route / "derived_identity_certificate.json",
                        "source_lift": route / "full_source_lift_certificate.json"})
                provider = saved_witness.SavedWitnessProvider(context)
                self.assertTrue(provider.materialize().verification["verified"])
                displays = {sp.latex(sp.Symbol(name)) for name in arguments["symbols"]}
                aliases = provider.verification["presentation_names"]
                self.assertFalse(displays & {sp.latex(sp.Symbol(name)) for name in aliases.values()})
                provider.markdown += " changed"
                with self.assertRaisesRegex(ValueError, "presentation changed"):
                    provider.materialize()


if __name__ == "__main__":
    unittest.main()
