from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cognitive_well_harness_v0_3_274_generic_compression_portfolio_bridge_20260905 import (
    exact_tools,
)

from cognitive_well_harness_v0_3_282_unit_circle_laurent_elimination_20260905 import (
    integration,
)


def _sleeping_preprocess(**_: object) -> dict[str, object]:
    time.sleep(5)
    return {}


def _large_preprocess(*, output_dir: Path, **_: object) -> dict[str, object]:
    output_dir.mkdir(parents=True)
    payload = {"state": "prepared", "large": "x" * 2_000_000}
    (output_dir / "prepared.json").write_text(json.dumps(payload), encoding="utf-8")
    return payload


def _descendant_preprocess(*, output_dir: Path, **_: object) -> dict[str, object]:
    output_dir.mkdir(parents=True)
    child = subprocess.Popen(["sleep", "60"])
    (output_dir.parent / "descendant.pid").write_text(str(child.pid), encoding="utf-8")
    child.wait()
    return {}


class GenericLaurentIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.singular = (
            Path(__file__).resolve().parents[1]
            / ".tools/singular-4.2.1/singular"
        )
        if not self.singular.is_file():
            self.skipTest("local Singular binary is unavailable")
        x = {"symbol": "x"}
        y = {"symbol": "y"}
        r = {"symbol": "r"}
        self.arguments = {
            "symbols": ["r", "x", "y"],
            "generators": {
                "D1": {"sub": [{"add": [{"pow": [x, 2]}, {"pow": [y, 2]}]}, 1]},
                "D2": {"sub": [{"mul": [r, {"add": [x, y]}]}, 1]},
                "D3": {"sub": [{"mul": [r, {"sub": [x, y]}]}, 2]},
            },
            "target": {"sub": [{"mul": [r, {"add": [x, y]}]}, 1]},
        }
        self.guard_program = {
            "provenance_divisions": {
                "ratio": {"numerator": 1, "denominator": {"add": [x, y]}}
            },
            "source_nonzero": {},
        }

    def validation(self) -> dict[str, object]:
        return {
            "decision": "ACCEPT",
            "source_arguments_sha256": exact_tools.stable_hash(self.arguments),
            "candidate_arguments_sha256": exact_tools.stable_hash(self.arguments),
            "guard_program_sha256": exact_tools.stable_hash(self.guard_program),
        }

    def test_executes_without_preloaded_certificate_and_binds_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            result = integration.preprocess_and_execute(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                exact_transformation_validation=self.validation(),
                output_dir=root,
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
            )
            self.assertEqual(result["state"], "proved")
            self.assertFalse(result["preloaded_certificate_used"])
            self.assertEqual(result["model_calls"], 0)
            self.assertEqual(result["orientation_attempted_count"], 2)
            self.assertIn(
                "Exact candidate-target lift:",
                result["mathematical_certificate_appendix"],
            )
            self.assertIn(
                "Exact identity over `QQ(i)`:",
                integration.render_evidence(result),
            )
            lift = json.loads(
                (root / "full_source_lift_certificate.json").read_text()
            )
            self.assertTrue(lift["verified"])
            self.assertEqual(
                lift["source_arguments_sha256"],
                exact_tools.stable_hash(self.arguments),
            )
            for name, digest in result["artifact_sha256"].items():
                self.assertEqual(integration._sha256_file(root / name), digest)
            replay = integration.verify_exported_membership_identity(
                output_dir=root, result=result
            )
            self.assertTrue(replay["reexpansion_zero"])

    def test_membership_identity_replay_rejects_changed_multiplier_even_with_new_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            result = integration.preprocess_and_execute(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                exact_transformation_validation=self.validation(),
                output_dir=root,
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
            )
            identity_path = root / "derived_identity_certificate.json"
            identity = json.loads(identity_path.read_text())
            label = identity["generator_labels"][0]
            identity["source_multipliers"][label] = (
                f"({identity['source_multipliers'][label]}) + 1"
            )
            payload = dict(identity)
            payload.pop("certificate_sha256")
            identity["certificate_sha256"] = exact_tools.stable_hash(payload)
            identity_path.write_text(json.dumps(identity))
            result["derived_identity_certificate_sha256"] = identity[
                "certificate_sha256"
            ]
            with self.assertRaisesRegex(ValueError, "does not re-expand"):
                integration.verify_exported_membership_identity(
                    output_dir=root, result=result
                )

    def test_structural_preview_is_explicitly_unvalidated_and_nonpromotable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "preview"
            preview = integration.bounded_preview_only(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                output_dir=root,
                timeout_sec=10,
                memory_mb=1024,
            )
            self.assertEqual(preview["state"], "structural_preview_unvalidated")
            self.assertEqual(preview["source_equivalence_status"], "unchecked")
            self.assertFalse(preview["promotable"])
            self.assertIsNone(preview["exact_transformation_validation_sha256"])
            self.assertFalse((root / "full_source_lift_certificate.json").exists())
            self.assertEqual(
                preview["preview_file_sha256"],
                integration._sha256_file(root / "preview.json"),
            )

    def test_threaded_preview_matches_main_thread_without_child_exit_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            kwargs = dict(source_arguments=self.arguments, candidate_arguments=self.arguments,
                          guard_program=self.guard_program, timeout_sec=15, memory_mb=1024)
            main = integration.bounded_preview_only(output_dir=Path(temporary) / "main", **kwargs)
            with ThreadPoolExecutor(max_workers=1) as pool:
                threaded = pool.submit(integration.bounded_preview_only,
                    output_dir=Path(temporary) / "threaded", **kwargs).result(timeout=20)
            self.assertEqual(threaded["transform_sha256"], main["transform_sha256"])
            self.assertEqual(threaded["derived_profile"], main["derived_profile"])
            self.assertFalse(threaded["promotable"])

    def test_target_screen_proves_reduced_ideal_without_claiming_source_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preview = integration.bounded_preview_only(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                output_dir=root / "preview",
                timeout_sec=10,
                memory_mb=1024,
            )
            screen = integration.bounded_screen_preview_target(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                output_dir=root / "screen",
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
                expected_transform_sha256=preview["transform_sha256"],
                expected_derived_profile=preview["derived_profile"],
                expected_structural_preview_sha256=preview[
                    "preview_file_sha256"
                ],
            )
            self.assertEqual(screen["state"], "proved")
            self.assertEqual(screen["source_equivalence_status"], "unchecked")
            self.assertFalse(screen["promotable"])
            self.assertIsNone(screen["exact_transformation_validation_sha256"])
            replay = integration.verify_persisted_laurent_outcome(
                output_dir=root / "screen", result=screen
            )
            self.assertTrue(replay["affirmative"])

    def test_persisted_target_screen_does_not_recompute_laurent_transform(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preview = integration.bounded_preview_only(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                output_dir=root / "preview",
                timeout_sec=10,
                memory_mb=1024,
            )
            screen = integration.bounded_screen_persisted_preview_target(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                preview_output_dir=root / "preview",
                output_dir=root / "screen",
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
                expected_transform_sha256=preview["transform_sha256"],
                expected_derived_profile=preview["derived_profile"],
                expected_structural_preview_sha256=preview[
                    "preview_file_sha256"
                ],
            )
            self.assertEqual(screen["state"], "proved")
            self.assertTrue(screen["persisted_preview_verified"])
            self.assertFalse(screen["transform_recomputed_before_screen"])
            replay = integration.verify_persisted_laurent_outcome(
                output_dir=root / "screen", result=screen
            )
            self.assertTrue(replay["affirmative"])

    def test_pure_laurent_reduction_without_linear_elimination_is_certified(self) -> None:
        x = {"symbol": "x"}
        y = {"symbol": "y"}
        z = {"symbol": "z"}
        arguments = {
            "symbols": ["x", "y", "z"],
            "generators": {
                "D1": {"sub": [{"add": [{"pow": [x, 2]}, {"pow": [y, 2]}]}, 1]},
                "D2": z,
            },
            "target": z,
        }
        guard_program = {"provenance_divisions": {}, "source_nonzero": {}}
        validation = {
            "decision": "ACCEPT",
            "source_arguments_sha256": exact_tools.stable_hash(arguments),
            "candidate_arguments_sha256": exact_tools.stable_hash(arguments),
            "guard_program_sha256": exact_tools.stable_hash(guard_program),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "pure"
            result = integration.preprocess_and_execute(
                source_arguments=arguments,
                candidate_arguments=arguments,
                guard_program=guard_program,
                exact_transformation_validation=validation,
                output_dir=root,
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
            )
            transform = json.loads((root / "laurent_transform.json").read_text())
            lift = json.loads(
                (root / "full_source_lift_certificate.json").read_text()
            )
            self.assertEqual(transform["route_mode"], "laurent_only")
            self.assertFalse(lift["linear_elimination"]["performed"])
            self.assertEqual(lift["linear_elimination"]["variable"], None)
            self.assertEqual(result["state"], "proved")
            self.assertEqual(result["orientation_attempted_count"], 2)
            self.assertTrue(
                integration.verify_exported_membership_identity(
                    output_dir=root, result=result
                )["verified"]
            )

    def test_persisted_laurent_nonproof_replays_and_marker_tamper_rejects(self) -> None:
        x = {"symbol": "x"}
        y = {"symbol": "y"}
        z = {"symbol": "z"}
        arguments = {
            "symbols": ["x", "y", "z"],
            "generators": {
                "D1": {"sub": [{"add": [{"pow": [x, 2]}, {"pow": [y, 2]}]}, 1]},
                "D2": z,
            },
            "target": 1,
        }
        guards = {"provenance_divisions": {}, "source_nonzero": {}}
        validation = {
            "decision": "ACCEPT",
            "source_arguments_sha256": exact_tools.stable_hash(arguments),
            "candidate_arguments_sha256": exact_tools.stable_hash(arguments),
            "guard_program_sha256": exact_tools.stable_hash(guards),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "nonproof"
            result = integration.preprocess_and_execute(
                source_arguments=arguments,
                candidate_arguments=arguments,
                guard_program=guards,
                exact_transformation_validation=validation,
                output_dir=root,
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
            )
            replay = integration.verify_persisted_laurent_outcome(
                output_dir=root, result=result
            )
            self.assertTrue(replay["verified"])
            self.assertFalse(replay["affirmative"])
            self.assertEqual(replay["exact_status"], "NONZERO")

            exact_path = root / "exact_result.json"
            exact_result = json.loads(exact_path.read_text())
            exact_result["output"] += "\nRESULT_ORDINARY=PROVED\n"
            exact_result["output_sha256"] = integration.hashlib.sha256(
                exact_result["output"].encode()
            ).hexdigest()
            exact_path.write_text(json.dumps(exact_result))
            result["artifact_sha256"]["exact_result.json"] = integration._sha256_file(
                exact_path
            )
            with self.assertRaisesRegex(ValueError, "markers are not unique"):
                integration.verify_persisted_laurent_outcome(
                    output_dir=root, result=result
                )

    def test_certified_replay_must_match_structural_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            preview = integration.bounded_preview_only(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                output_dir=Path(temporary) / "preview",
                timeout_sec=10,
                memory_mb=1024,
            )
            certified = integration.bounded_preprocess_only(
                source_arguments=self.arguments,
                candidate_arguments=self.arguments,
                guard_program=self.guard_program,
                exact_transformation_validation=self.validation(),
                output_dir=Path(temporary) / "certified",
                timeout_sec=10,
                memory_mb=1024,
                expected_transform_sha256=preview["transform_sha256"],
                expected_derived_profile=preview["derived_profile"],
            )
            self.assertTrue(certified["matched_structural_preview"])
            with self.assertRaisesRegex(RuntimeError, "does not match structural preview"):
                integration.bounded_preprocess_only(
                    source_arguments=self.arguments,
                    candidate_arguments=self.arguments,
                    guard_program=self.guard_program,
                    exact_transformation_validation=self.validation(),
                    output_dir=Path(temporary) / "tampered",
                    timeout_sec=10,
                    memory_mb=1024,
                    expected_transform_sha256="0" * 64,
                    expected_derived_profile=preview["derived_profile"],
                )

    def test_rejects_tampered_validation_binding(self) -> None:
        validation = self.validation()
        validation["candidate_arguments_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "candidate_arguments_sha256"):
                integration.preprocess_and_execute(
                    source_arguments=self.arguments,
                    candidate_arguments=self.arguments,
                    guard_program=self.guard_program,
                    exact_transformation_validation=validation,
                    output_dir=Path(temporary) / "run",
                    singular_binary=self.singular,
                    timeout_sec=10,
                    memory_mb=1024,
                )

    def test_bounded_preprocess_timeout_fails_closed_without_partial_artifacts(self) -> None:
        from unittest import mock

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            with mock.patch.object(
                integration, "preprocess_only", _sleeping_preprocess
            ):
                with self.assertRaisesRegex(TimeoutError, "1-second"):
                    integration.bounded_preprocess_only(
                        source_arguments=self.arguments,
                        candidate_arguments=self.arguments,
                        guard_program=self.guard_program,
                        exact_transformation_validation=self.validation(),
                        output_dir=root,
                        timeout_sec=1,
                        memory_mb=1024,
                    )
            self.assertFalse(root.exists())

    def test_consistent_multi_generator_backend_exports_reexpanded_certificate(self) -> None:
        arguments = json.loads(json.dumps(self.arguments))
        arguments["generators"]["D4"] = {
            "add": [
                arguments["generators"]["D2"],
                arguments["generators"]["D3"],
            ]
        }
        arguments["target"] = arguments["generators"]["D4"]
        validation = {
            "decision": "ACCEPT",
            "source_arguments_sha256": exact_tools.stable_hash(arguments),
            "candidate_arguments_sha256": exact_tools.stable_hash(arguments),
            "guard_program_sha256": exact_tools.stable_hash(self.guard_program),
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = integration.preprocess_and_execute(
                source_arguments=arguments,
                candidate_arguments=arguments,
                guard_program=self.guard_program,
                exact_transformation_validation=validation,
                output_dir=Path(temporary) / "run",
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
            )
            exact_result = json.loads(
                (Path(temporary) / "run/exact_result.json").read_text()
            )
            self.assertTrue(result["backend_proved"], exact_result)
            self.assertEqual(result["state"], "proved")
            self.assertTrue(result["membership_certificate_exported"])
            self.assertTrue(result["membership_certificate_reexpanded"])
            self.assertEqual(result["evidence_status"], "verified")
            identity = json.loads(
                (Path(temporary) / "run/derived_identity_certificate.json").read_text()
            )
            self.assertTrue(identity["reexpansion_zero"])
            self.assertEqual(
                identity["generator_labels"],
                list(identity["source_multipliers"]),
            )
            self.assertEqual(list(Path(temporary).glob(".*.partial-*")), [])

    def test_inconsistent_derived_ideal_cannot_promote_vacuous_membership(self) -> None:
        arguments = json.loads(json.dumps(self.arguments))
        arguments["generators"]["D4"] = {
            "sub": [{"symbol": "x"}, {"symbol": "y"}]
        }
        arguments["target"] = arguments["generators"]["D4"]
        validation = {
            "decision": "ACCEPT",
            "source_arguments_sha256": exact_tools.stable_hash(arguments),
            "candidate_arguments_sha256": exact_tools.stable_hash(arguments),
            "guard_program_sha256": exact_tools.stable_hash(self.guard_program),
        }
        with tempfile.TemporaryDirectory() as temporary:
            result = integration.preprocess_and_execute(
                source_arguments=arguments,
                candidate_arguments=arguments,
                guard_program=self.guard_program,
                exact_transformation_validation=validation,
                output_dir=Path(temporary) / "run",
                singular_binary=self.singular,
                timeout_sec=10,
                memory_mb=1024,
            )
            self.assertFalse(result["backend_proved"])
            self.assertNotEqual(result["state"], "proved")
            self.assertFalse(result["membership_certificate_exported"])
            self.assertEqual(result["evidence_status"], "absent")

    def test_bounded_preprocess_child_error_fails_closed(self) -> None:
        validation = self.validation()
        validation["candidate_arguments_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            with self.assertRaisesRegex(RuntimeError, "failed closed"):
                integration.bounded_preprocess_only(
                    source_arguments=self.arguments,
                    candidate_arguments=self.arguments,
                    guard_program=self.guard_program,
                    exact_transformation_validation=validation,
                    output_dir=root,
                    timeout_sec=10,
                    memory_mb=1024,
                )
            self.assertFalse(root.exists())

    def test_bounded_worker_does_not_queue_large_result_payload(self) -> None:
        from unittest import mock

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            with mock.patch.object(integration, "preprocess_only", _large_preprocess):
                result = integration.bounded_preprocess_only(
                    source_arguments=self.arguments,
                    candidate_arguments=self.arguments,
                    guard_program=self.guard_program,
                    exact_transformation_validation=self.validation(),
                    output_dir=root,
                    timeout_sec=5,
                    memory_mb=1024,
                )
            self.assertEqual(len(result["large"]), 2_000_000)
            self.assertTrue((root / "prepared.json").is_file())

    def test_timeout_kills_worker_descendant_process_group(self) -> None:
        from unittest import mock

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            with mock.patch.object(
                integration, "preprocess_only", _descendant_preprocess
            ):
                with self.assertRaises(TimeoutError):
                    integration.bounded_preprocess_only(
                        source_arguments=self.arguments,
                        candidate_arguments=self.arguments,
                        guard_program=self.guard_program,
                        exact_transformation_validation=self.validation(),
                        output_dir=root,
                        timeout_sec=1,
                        memory_mb=1024,
                    )
            pid = int((Path(temporary) / "descendant.pid").read_text())
            for _ in range(20):
                if not Path(f"/proc/{pid}").exists():
                    break
                time.sleep(0.05)
            self.assertFalse(Path(f"/proc/{pid}").exists())
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
