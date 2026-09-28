"""Core saved-route eligibility tests, without model or exact-engine calls."""
from pathlib import Path
import tempfile
import unittest

from . import resume_proved_exact as resume, rewrite


class ExactResumeTests(unittest.TestCase):
    def test_only_proved_pre_audit_failures_are_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            root = source / "01_acquisition"
            labels = [label for label, _ in resume.acquisition.FORMALIZATION_SCHEDULE]
            for label in labels[:4]:
                route = root / "05_direct_laurent_routes" / label
                rewrite.write_record(route / "route_state.json", {"state": "exact_failed_closed", "screen": {"state": "proved"}})
                rewrite.write_record(route / "03_laurent_lift/prepared.json", {})
            # Never resample a semantic audit or resume a non-proof as proved.
            (root / "06_post_singular_audits" / labels[1]).mkdir(parents=True)
            rewrite.write_record(root / "05_direct_laurent_routes" / labels[2] / "route_state.json",
                {"state": "exact_failed_closed", "screen": {"state": "not_proved"}})
            rewrite.write_record(root / "05_direct_laurent_routes" / labels[3] / "route_state.json",
                {"state": "singular_proved", "screen": {"state": "proved"}})
            self.assertEqual(resume.eligible_routes(source), [labels[0]])

    def test_missing_lift_is_not_a_completed_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            label = resume.acquisition.FORMALIZATION_SCHEDULE[0][0]
            rewrite.write_record(source / "01_acquisition/05_direct_laurent_routes" / label / "route_state.json",
                {"state": "exact_failed_closed", "screen": {"state": "proved"}})
            self.assertEqual(resume.eligible_routes(source), [])


if __name__ == "__main__":
    unittest.main()
