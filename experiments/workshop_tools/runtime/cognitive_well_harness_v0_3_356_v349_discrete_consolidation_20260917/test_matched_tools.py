"""Synthetic exact math, domain failures, replay, and runtime isolation."""
import ast
import copy
from pathlib import Path

import pytest

from . import matched_expression as language, matched_tools as tools


def request(body, symbols="NONE"):
    return f"```exact-args\nsymbols = {symbols}\n{body}\n```"


def compute(body, symbols="NONE", operation="exact_geometry"):
    return tools._compute(operation, request(body, symbols))


def test_projection_is_on_line_and_displacement_is_perpendicular_symbolically():
    result = compute("""define = A :: (point ax ay)
define = B :: (point bx by)
define = P :: (point px py)
define = H :: (foot P A B)
check = on_line :: (eq (cross (vsub H A) (vsub B A)) 0)
check = perpendicular :: (eq (dot (vsub P H) (vsub B A)) 0)
emit = H""", "ax, ay, bx, by, px, py")
    assert result["verdict"] == "CONDITIONAL_IDENTITY"
    assert all(row["truth"] is True for row in result["checks"])
    assert any("distinct" in row["reason"] for row in result["unresolved_conditions"])
    assert not result["theorem_proved"] and not result["source_semantics_verified"]


@pytest.mark.parametrize("dx,dy,scale", [(0, 0, 1), (8, -3, 2), (-4, 9, -3)])
def test_second_intersections_are_equivariant_under_translation_and_scaling(dx, dy, scale):
    def p(x, y):
        return f"(point {dx + scale*x} {dy + scale*y})"
    result = compute(f"""define = O :: {p(0, 0)}
define = V :: {p(3, 0)}
define = A :: {p(3, 4)}
define = expected :: {p(3, -4)}
define = first :: (circle_center_radius O {5*abs(scale)})
define = second :: (circle_center_radius V {4*abs(scale)})
define = X :: (second_on_circles first second A)
define = Y :: (second_on_line first A V)
check = equal_points :: (eq (norm2 (vsub X expected)) 0)
check = equal_methods :: (eq (norm2 (vsub X Y)) 0)
check = on_first :: (eq (power first X) 0)
check = on_second :: (eq (power second X) 0)
emit = X""")
    assert result["verdict"] == "IDENTITY_VERIFIED"


def test_exact_counterexample_requires_all_premises():
    body = """define = A :: (point 0 0)
define = B :: (point 3 0)
define = C :: (point 0 4)
define = P :: (point 1 1)
define = omega :: (circle A B C)
assume = inside_quadrant :: (gt (x P) 0)
check = asserted_membership :: (eq (power omega P) 0)
emit = omega"""
    result = compute(body)
    assert result["verdict"] == "COUNTEREXAMPLE"
    assert result["checks"][0]["residual"] == "-5"
    assert compute(body.replace("(gt (x P) 0)", "(lt (x P) 0)"))["verdict"] == "INCONSISTENT_PREMISES"


def test_symbolic_nonidentity_is_not_a_concrete_counterexample():
    result = compute("check = alleged :: (eq x 0)", "x", "rational_identity")
    assert result["verdict"] == "INCONCLUSIVE"
    assert not result["usable_evidence"]


def test_cancellation_retains_denominator_and_does_not_use_target_as_premise():
    result = compute("""define = y :: (div x x)
assume = target_as_premise :: (eq x 0)
check = identity :: (eq y 1)""", "x", "rational_identity")
    assert result["verdict"] == "CONDITIONAL_IDENTITY"
    assert any(row["residual"] == "x" and row["relation"] == "ne" for row in result["unresolved_conditions"])
    # No assertion that the symbolic premises/conditions are jointly consistent.
    assert not result["theorem_proved"]


def test_linear_root_and_parameter_independent_coefficient_root_are_derived():
    result = compute("""define = moving :: (linear_root q (sub (mul (add t 2) q) (add t 7)))
define = fixed :: (coefficient_root z t (add (mul (sub z 5) (pow t 2)) (sub (mul 2 z) 10)))
check = moving_equation :: (eq (sub (mul (add t 2) moving) (add t 7)) 0)
check = fixed_equation :: (eq (add (mul (sub fixed 5) (pow t 2)) (sub (mul 2 fixed) 10)) 0)
emit = moving
emit = fixed""", "t, q, z", "rational_identity")
    assert result["outputs"]["fixed"]["expression"] == "5"
    assert all(d["substitution_verified"] for d in result["derivations"])
    assert all(row["truth"] is True for row in result["checks"])
    assert any(row["residual"] == "t + 2" for row in result["unresolved_conditions"])


@pytest.mark.parametrize("expr", [
    "(linear_root x (sub (div (sub (pow x 2) 1) (sub x 1)) 2))",
    "(linear_root x precomputed)",
])
def test_root_at_canceled_pole_is_rejected_even_through_named_definition(expr):
    body = f"""define = precomputed :: (sub (div (sub (pow x 2) 1) (sub x 1)) 2)
define = candidate :: {expr}
emit = candidate"""
    with pytest.raises(language.InvalidInstance):
        compute(body, "x", "rational_identity")


@pytest.mark.parametrize("expr", [
    "(linear_root z (sub (pow z 2) 2))",
    "(coefficient_root z t (add (mul (sub z 3) t) (sub z 4)))",
    "(linear_root z 0)",
])
def test_nonlinear_or_inconsistent_coefficient_system_cannot_claim_a_solution(expr):
    with pytest.raises(language.DerivationUnavailable):
        compute(f"define = result :: {expr}\nemit = result", "z, t", "rational_identity")


def test_inverting_a_line_derives_a_circle_containing_the_inverted_parameterized_point():
    result = compute("""define = S :: (point 2 3)
define = A :: (point 0 0)
define = B :: (point 1 0)
define = P :: (point t 0)
define = T :: (invert_point S k P)
define = locus :: (invert_line S k A B)
define = original :: (invert_point S k T)
check = on_circle :: (eq (power locus T) 0)
check = involution :: (eq (norm2 (vsub original P)) 0)
emit = locus""", "t, k")
    assert all(row["truth"] is True for row in result["checks"])
    assert all("t" not in result["outputs"]["locus"][key] for key in ("u", "v", "w"))
    assert any(row["residual"] == "k" and row["relation"] == "ne" for row in result["unresolved_conditions"])


@pytest.mark.parametrize("body", [
    "define = P :: (point 1 2)\ndefine = H :: (foot P P P)\nemit = H",
    "define = P :: (point 1 2)\ndefine = omega :: (circle P P P)\nemit = omega",
    "define = O :: (point 0 0)\ndefine = C :: (circle_center_radius O 1)\ndefine = P :: (point 1 0)\ndefine = Q :: (point 1 2)\ndefine = X :: (second_on_line C P Q)\nemit = X",
    "define = O :: (point 0 0)\ndefine = C :: (circle_center_radius O 1)\ndefine = P :: (point 1 0)\ndefine = X :: (second_on_circles C C P)\nemit = X",
    "define = O :: (point 0 0)\ndefine = C :: (circle_center_radius O 1)\ndefine = P :: (point 2 0)\ndefine = X :: (second_on_line C P O)\nemit = X",
    "define = O :: (point 0 0)\ndefine = A :: (point 1 0)\ndefine = C :: (invert_line O 2 O A)\nemit = C",
])
def test_degenerate_geometry_is_rejected(body):
    with pytest.raises(language.InvalidInstance):
        compute(body)


def test_positive_surd_arithmetic_is_exact():
    result = compute("""define = v :: (sqrt 7)
check = algebraic :: (eq (pow v 2) 7)
check = sign :: (gt v 0)""")
    assert result["verdict"] == "IDENTITY_VERIFIED"


@pytest.mark.parametrize("text", [
    '{"symbols": []}',
    request("define = P :: (point 0 1)\nemit = P", "x, x"),
    request("define = P :: (eval 1)\nemit = P"),
    request("define = P :: (point 0.5 1)\nemit = P"),
    request("define = x :: missing\nemit = x"),
    request("check = C :: (eq 0 0)\nemit = C"),
    request("reference_file = anything\ncheck = C :: (eq 0 0)"),
])
def test_closed_language_rejects_code_unknown_names_and_extra_metadata(text):
    with pytest.raises(ValueError):
        tools._compute("exact_geometry", text)


def test_bounded_public_executor_persistence_and_replay(tmp_path):
    text = request("check = false_claim :: (eq (mul 3 3) 8)")
    result = tools.run(operation="rational_identity", arguments_markdown=text, output=tmp_path / "fresh")
    assert result["verdict"] == "COUNTEREXAMPLE", result
    assert result["model_calls"] == 0
    assert tools.replay(operation="rational_identity", arguments_markdown=text, saved_result=result) == result
    tampered = copy.deepcopy(result)
    tampered["checks"][0]["residual"] = "0"
    with pytest.raises(ValueError, match="differs"):
        tools.replay(operation="rational_identity", arguments_markdown=text, saved_result=tampered)
    with pytest.raises(FileExistsError):
        tools.run(operation="rational_identity", arguments_markdown=text, output=tmp_path / "fresh")
    assert (tmp_path / "fresh" / "arguments.md").read_text() == text


def test_public_executor_invalid_inputs_and_limits():
    text = request("define = bad :: (div 1 0)\nemit = bad")
    assert tools.execute(operation="rational_identity", arguments_markdown=text)["verdict"] == "INVALID_INSTANCE"
    with pytest.raises(ValueError):
        tools.execute(operation="unknown", arguments_markdown=text)
    with pytest.raises(ValueError):
        tools.execute(operation="exact_geometry", arguments_markdown=text, timeout_seconds=True)


def test_resource_exhaustion_cannot_be_promoted_to_evidence():
    text = request("define = huge :: (pow (add a b c d e f g h) 32)\nemit = huge", "a, b, c, d, e, f, g, h")
    result = tools.execute(operation="rational_identity", arguments_markdown=text, timeout_seconds=1, memory_mb=512)
    assert result["verdict"] in {"INCONCLUSIVE", "EXECUTION_ERROR", "INVALID_REQUEST"}
    assert not result["usable_evidence"] and not result["theorem_proved"]


def test_harness_handoff_does_not_acquire_or_rewrite(tmp_path, monkeypatch):
    from . import proof_harness

    monkeypatch.setattr(proof_harness, "acquire", lambda **kw: pytest.fail("model acquisition invoked"))
    result = proof_harness.run_matched_tool(operation="rational_identity",
        arguments_markdown=request("check = identity :: (eq (add 2 2) 4)"), output=tmp_path / "handoff")
    assert result["verdict"] == "IDENTITY_VERIFIED"
    assert not result["theorem_proved"]


def test_runtime_modules_have_no_problem_catalog_or_reference_imports():
    for module in (language, tools):
        source = Path(module.__file__).read_text()
        for token in ("PB-Advanced", "r1_c2_tool_audit", "p9_bridge", "p10_bridge", "snapshots/", "benchmarks/"):
            assert token not in source
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [node.module or ""] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names]
                assert not any("benchmark" in name or "experiment" in name or "test_" in name for name in names)
