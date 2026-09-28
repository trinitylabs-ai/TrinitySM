import pytest

from . import exact_evidence


@pytest.mark.parametrize("decision", ["ACCEPT", "REJECT"])
def test_semantic_decision_is_not_confused_with_parser_validity(decision):
    checks = exact_evidence.v274_protocol.AUDIT_CHECKS
    lines = [f"- {label}: {'FAIL' if decision == 'REJECT' and i == 0 else 'PASS'}"
             for i, label in enumerate(checks)]
    issues = "NONE" if decision == "ACCEPT" else "- The target does not match the claim."
    text = f"# Decision\n\n{decision}\n\n# Checks\n\n" + "\n".join(lines) + f"\n\n# Issues\n\n{issues}"
    parsed = exact_evidence._parse_semantic_audit(text)
    assert parsed["valid"] is True
    assert parsed["accepted"] is (decision == "ACCEPT")
    assert parsed["decision"] == decision
    assert parsed["errors"] == []


def test_malformed_semantic_audit_still_raises():
    with pytest.raises(ValueError):
        exact_evidence._parse_semantic_audit("REJECT")
