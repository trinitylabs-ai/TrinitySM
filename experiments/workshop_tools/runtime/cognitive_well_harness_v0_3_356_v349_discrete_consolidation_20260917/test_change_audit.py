import unittest

from . import change_audit, pipeline


class ChangeAuditTests(unittest.TestCase):
    def test_changes_are_complete_ordered_and_certificate_body_is_not_diffed(self):
        old = "Setup\nx=1\nMiddle\ny=2\nEnd"
        new = "Setup\nx=3\nMiddle\ny=2\nFROZEN_WITNESS\nEnd"
        rows = change_audit.detect(old, new, "FROZEN_WITNESS", "[CERT]")
        self.assertEqual([row["id"] for row in rows], ["C001", "C002"])
        self.assertEqual((rows[0]["old"], rows[0]["new"]), ("x=1", "x=3"))
        self.assertEqual(rows[1]["kind"], "insert")
        self.assertEqual(rows[1]["new"], "[CERT]")
        self.assertNotIn("FROZEN_WITNESS", change_audit.render(rows))
        self.assertEqual(rows, change_audit.detect(old, new, "FROZEN_WITNESS", "[CERT]"))

    def test_deletions_and_context_are_retained(self):
        rows = change_audit.detect("Setup\nneeded step\nEnd", "Setup\nEnd\nCERT", "CERT", "[BLOCK]")
        self.assertEqual(rows[0]["kind"], "delete")
        self.assertEqual(rows[0]["old"], "needed step")
        self.assertEqual(rows[0]["old_preceding"], "Setup")
        self.assertEqual(rows[0]["old_following"], "End")

    def audit(self, status="JUSTIFIED", decision="PASS", issue="NONE"):
        checks = "\n".join(f"- {label}: {decision}" for label in pipeline.base.protocol.PROOF_AUDIT_CHECKS)
        return f"# Decision\n\n{decision}\n\n# Checks\n\n{checks}\n\n# Change Review\n\n- C001: {status} | A mathematical explanation.\n\n# Issues\n\n{issue}"

    def test_complete_pass_and_fail_are_preserved(self):
        for status, decision, issue in (("JUSTIFIED", "PASS", "NONE"), ("INVALID", "FAIL", "- C001: Derivation is invalid.")):
            result = change_audit.parse(self.audit(status, decision, issue), [{"id": "C001"}], require_gap_closure=False)
            self.assertEqual(result["decision"], decision)
            self.assertEqual(result["change_reviews"]["C001"]["status"], status)

    def test_missing_unknown_duplicate_and_inconsistent_reviews_rejected(self):
        valid = self.audit()
        for text, rows in ((valid, [{"id": "C001"}, {"id": "C002"}]),
                (valid.replace("- C001:", "- C002:"), [{"id": "C001"}]),
                (valid.replace("# Issues", "- C001: JUSTIFIED | Duplicate.\n\n# Issues"), [{"id": "C001"}]),
                (self.audit("INVALID"), [{"id": "C001"}]),
                (self.audit("UNRESOLVED", "FAIL", "- No ID cited."), [{"id": "C001"}])):
            with self.subTest(text=text), self.assertRaises(ValueError):
                change_audit.parse(text, rows, require_gap_closure=False)


if __name__ == "__main__":
    unittest.main()
