from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905.pipeline import (
    Role,
)

from . import pipeline


FORMALIZATION = """# Semantic Bindings

- Source basis: the displayed identities in the proof
- Target meaning: target zero is the detected equality
- Domain and branch conditions: x is real and x is nonzero
- Formalization map: x is the proof variable
- Sufficiency argument: the generator implies the target
- Rewrite consequence: a proved result closes the gap

# Guard Program

```guard-args
provenance_division = q1 :: (symbol x) :: (symbol x)
source_nonzero = nz1 :: (symbol x)
```

# Tool Arguments

```tool-args
operation = polynomial_ideal_membership
symbols = x
generator = D1 :: (sub (pow (symbol x) 2) 1)
target = (sub (pow (symbol x) 2) 1)
```"""


class HarnessTests(unittest.TestCase):
    def test_resume_reparses_all_v0312_formalizations(self) -> None:
        root = Path(
            "runs/v0312r1_p2_t07_r01_guarded_formalization_"
            "laurent600_singular300_20260906"
        ).resolve()
        if not root.is_dir():
            self.skipTest("preserved v0312 integration fixture is unavailable")
        problem = pipeline.v0220.load_problem(
            Path(
                "math_harness_inputs/imo2026_p4_p2_v0313_20260815/"
                "imo2026_p2.json"
            ).resolve()
        )
        proof = Path(
            "runs/v0257_v108_six_problem_bf_temp_transition_20260904/p2/"
            "01_raw_lazy_enhanced_resolve/phase_2_v096/cases/imo2026_p2.t07_r01/"
            "resolver/temperature_0_4/gpu0/p2/t07_r01/resolved_proof.md"
        ).resolve().read_text(encoding="utf-8").strip()
        allowed = pipeline.base._matcher_operations(("simplify_identity",))
        _, _, _, matcher, rows, binding = pipeline.load_resumed_formalizations(
            resume_root=root,
            problem=problem,
            proof=proof,
            allowed_matcher_operations=allowed,
        )
        self.assertEqual(matcher["operation"], pipeline.exact_tools.IDEAL_OPERATION)
        self.assertEqual([row["label"] for row in rows], [row[0] for row in pipeline.FORMALIZATION_SCHEDULE])
        self.assertTrue(all(row["state"] == "compiled" for row in rows))
        self.assertEqual(binding["compiled_count"], 8)
        self.assertFalse(binding["partial_laurent_artifacts_reused"])

    def test_guarded_formalization_parser_and_canonical_dedup(self) -> None:
        first = pipeline.parse_guarded_formalization(FORMALIZATION)
        second = pipeline.parse_guarded_formalization(FORMALIZATION.replace("D1", "D7"))
        rows = [
            {"label": "t10", "temperature": 0.1, "state": "compiled", "formalization": first},
            {"label": "t15", "temperature": 0.15, "state": "compiled", "formalization": second},
        ]
        result = pipeline.deduplicate_formalizations(rows)
        self.assertFalse(result["byte_equality_used"])
        self.assertEqual(result["unique_count"], 1)
        self.assertEqual(result["groups"][0]["representative"], "t10")
        self.assertEqual(result["groups"][0]["members"], ["t10", "t15"])

    def test_mechanical_guard_leaf_and_target_label_repairs(self) -> None:
        surface = FORMALIZATION.replace(
            "(symbol x) :: (symbol x)", "x :: x"
        ).replace(
            "source_nonzero = nz1 :: (symbol x)",
            "source_nonzero = nz1 :: x",
        ).replace(
            "target = (sub", "target = T :: (sub",
        )
        parsed = pipeline.parse_guarded_formalization(surface)
        normalization = parsed["surface_normalization"]
        self.assertEqual(
            normalization["guard_program"]["declared_symbol_leaves"], 3
        )
        self.assertTrue(normalization["target_label_removed"])
        self.assertEqual(len(parsed["derived_guard_records"]), 1)

    def test_post_singular_audit_is_strict(self) -> None:
        checks = "\n".join(
            f"- {label}: PASS" for label in pipeline.POST_SINGULAR_CHECKS
        )
        parsed = pipeline.parse_post_singular_audit(
            f"# Decision\n\nACCEPT\n\n# Checks\n\n{checks}\n\n# Issues\n\nNONE"
        )
        self.assertTrue(parsed["accepted"])

    def test_preflight_has_no_gemma_compression_stage(self) -> None:
        problem = Path(
            "math_harness_inputs/imo2026_p4_p2_v0313_20260815/imo2026_p2.json"
        ).resolve()
        proof = Path(
            "runs/v0257_v108_six_problem_bf_temp_transition_20260904/p2/"
            "01_raw_lazy_enhanced_resolve/phase_2_v096/cases/imo2026_p2.t07_r01/"
            "resolver/temperature_0_4/gpu0/p2/t07_r01/resolved_proof.md"
        ).resolve()
        role = Role("http://127.0.0.1:1/v1", "test", 0.1, None)
        with tempfile.TemporaryDirectory() as directory:
            preflight = pipeline.build_preflight(
                problem_file=problem,
                proof_file=proof,
                output_dir=Path(directory) / "run",
                detector=role,
                compiler=role,
                auditor=role,
                rewriter=role,
                master_seed=7,
                model_request_timeout_sec=600,
                laurent_preprocess_timeout_sec=600,
                singular_timeout_sec=600,
                exact_memory_mb=8192,
                singular_binary=pipeline.SINGULAR_BINARY,
                excluded_matcher_operations=("simplify_identity",),
                resume_formalizations_root=None,
            )
        self.assertFalse(preflight["gemma_compression_stage"])
        self.assertEqual(preflight["laurent_preprocess_timeout_sec"], 600)
        self.assertEqual(preflight["singular_timeout_sec"], 600)
        self.assertNotIn("simplify_identity", preflight["matcher_allowed_operations"])
        self.assertEqual(preflight["formalization_schedule_sha256"], pipeline._schedule_sha256())


if __name__ == "__main__":
    unittest.main()
