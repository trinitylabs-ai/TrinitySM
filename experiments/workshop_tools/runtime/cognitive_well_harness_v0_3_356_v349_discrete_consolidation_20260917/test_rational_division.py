import copy

import pytest
import sympy as sp

from . import rational_division as tool
from .division_experiment import parse_proposal
from cognitive_well_harness_v0_3_309_guarded_formalization_direct_laurent_20260906.test_harness import FORMALIZATION
from cognitive_well_harness_v0_3_275_generic_audited_ledger_compression_20260905.transformation_validation import _polynomial_ast


x,y,z=sp.symbols("x y z")


def request(equations,target,guards=()):
    names=["x","y","z"]
    ast=lambda e:_polynomial_ast(e,names)
    return {"arguments":{"symbols":names,
        "generators":{f"D{i+1}":ast(e) for i,e in enumerate(equations)},"target":ast(target)},
        "guard_program":{"provenance_divisions":{},
            "source_nonzero":{f"G{i+1}":ast(g) for i,g in enumerate(guards)}}}


@pytest.mark.parametrize("equations,target,guards,verdict",[
    ([x-y,y*y-z],x*x-z,(),"VERIFIED_SUPPORT"),
    ([x*y],x,(),"INCONCLUSIVE"),
    ([x*y],x,(y,),"VERIFIED_SUPPORT"),
    ([x*x-y*y],x-y,(),"INCONCLUSIVE"),
    ([x*x-y*y],(x*x-y*y)*(x+y),(),"VERIFIED_SUPPORT"),
    ([x*y-1],x*x*y*y-1,(y,),"VERIFIED_SUPPORT"),
])
def test_checked_substitution_and_division(equations,target,guards,verdict,monkeypatch):
    def forbidden(*args,**kwargs):
        raise AssertionError("Groebner search is outside this backend")
    monkeypatch.setattr(sp,"groebner",forbidden)
    req=request(equations,target,guards)
    result=tool.solve(req)
    assert result["verdict"]==verdict
    assert result["certificate_verified"]
    assert tool.replay(req,result["certificate"])["target_proved"]==(verdict=="VERIFIED_SUPPORT")
    assert result["groebner_calls"]==result["laurent_calls"]==result["singular_calls"]==0


def test_witness_tampering_fails():
    req=request([x*x-y*y],(x*x-y*y)*(x+y))
    certificate=tool.solve(req)["certificate"]
    bad=copy.deepcopy(certificate)
    bad["quotients"]["D1"]=0
    with pytest.raises(ValueError,match="re-expansion"):
        tool.replay(req,bad)
    bad=copy.deepcopy(certificate)
    bad["target_numerator"]=0
    with pytest.raises(ValueError,match="target normalization"):
        tool.replay(req,bad)


def test_pivot_tampering_fails():
    req=request([x*y-1],x*x*y*y-1,(y,))
    certificate=tool.solve(req)["certificate"]
    bad=copy.deepcopy(certificate)
    bad["substitutions"][0]["numerator"]=2
    with pytest.raises(ValueError,match="not implied"):
        tool.replay(req,bad)


def test_zero_guard_and_request_drift_fail():
    with pytest.raises(ValueError,match="zero"):
        tool.solve(request([x*y],x,(sp.Integer(0),)))
    req=request([x-y],x-y)
    cert=tool.solve(req)["certificate"]
    with pytest.raises(ValueError,match="binding"):
        tool.replay(request([x-y],x+y),cert)


@pytest.mark.parametrize("guard", [x*y, -3*x*y, x**2*y**3])
def test_substitution_retains_denominator_when_guard_cancellation_hides_it(guard):
    # x*y != 0 justifies y != 0, but substituting x=1/y can turn the
    # full product guard into 1 and erase that denominator from its numerator.
    equations = {"pivot": x*y-1, "other": x*x-z}
    assert tool.covered(y, [guard], [x,y,z])
    reduced, target, guards = tool.substitute(equations, x/y, [guard], x, 1/y, [x,y,z])
    assert reduced == {"other": 1-y*y*z}
    assert sp.cancel(target-1/y**2) == 0
    assert tool.covered(y, guards, [x,y,z])
    assert all(x not in g.free_symbols for g in guards)


def test_guard_preservation_survives_chained_substitution_and_certificate_replay():
    req = request([x*y-1, x*x-z], z*y*y-1, (x*y,))
    original = copy.deepcopy(req)
    result = tool.solve(req)
    assert req == original  # No invented or edited source guards.
    assert result["verdict"] == "VERIFIED_SUPPORT"
    assert [step["variable"] for step in result["certificate"]["substitutions"]] == ["x", "z"]
    assert tool.replay(req, result["certificate"])["target_proved"]
    bad = copy.deepcopy(result["certificate"])
    bad["substitutions"][0]["denominator"] = _polynomial_ast(z, ["x","y","z"])
    with pytest.raises(ValueError, match="unguarded denominator"):
        tool.replay(req, bad)


def test_guard_created_by_one_substitution_survives_the_next():
    # The source guard is only x!=0. The first step x=y*z creates a product
    # guard; the next y=1/z cancels it. The remaining equation still needs z!=0.
    req = request([x-y*z, y*z-1, y*y-z], x-1, (x,))
    result = tool.solve(req)
    assert result["verdict"] == "VERIFIED_SUPPORT"
    assert result["guard_propagation_policy"] == tool.GUARD_PROPAGATION
    assert [step["variable"] for step in result["certificate"]["substitutions"]] == ["x", "y"]
    assert tool.replay(req, result["certificate"])["target_proved"]


@pytest.mark.parametrize("guards", [[], [x]])
def test_substitution_cannot_invent_its_own_denominator_guard(guards):
    with pytest.raises(ValueError, match="unguarded substitution denominator"):
        tool.substitute({"pivot": x*y-1}, x, guards, x, 1/y, [x,y,z])


def test_guard_retention_does_not_admit_other_unguarded_denominators():
    with pytest.raises(ValueError, match="unguarded target normalization denominator"):
        tool.substitute({"pivot": x*y-1}, x/z, [x*y], x, 1/y, [x,y,z])
    with pytest.raises(ValueError, match="conflicts with an asserted nonzero guard"):
        tool.substitute({"pivot": x}, x, [x*y], x, sp.Integer(0), [x,y,z])
    with pytest.raises(ValueError, match="self-referential"):
        tool.substitute({"pivot": x*y-x}, x, [y], x, x/y, [x,y,z])


def test_independent_existing_denominator_guard_is_not_duplicated():
    _, _, guards = tool.substitute({"pivot": x*y-1}, x, [y], x, 1/y, [x,y,z])
    assert guards == [y]


def test_model_may_decline_and_cannot_emit_json():
    assert not parse_proposal("# Decision\n\nNO_TOOL\n\n# Reason\n\nNo sound encoding.")["call_requested"]
    with pytest.raises(ValueError):
        parse_proposal('{"decision":"CALL_TOOL"}')


@pytest.mark.parametrize("separator", ["\n", "\n\n", "\n\n\n", "\n \t\n"])
@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_decision_spacing_preserves_formal_ast_and_guards(separator, newline):
    canonical="# Decision\n\nCALL_TOOL\n\n"+FORMALIZATION
    variant="# Decision"+separator+"CALL_TOOL"+separator+FORMALIZATION
    variant="\n\n"+variant.replace("# Guard Program\n\n", "# Guard Program\n")+"\n\n"
    assert parse_proposal(variant.replace("\n",newline))==parse_proposal(canonical)


@pytest.mark.parametrize("text", [
    "# Decision\nNO_TOOL\n# Reason\nNo sound encoding.",
    "\r\n# Decision \t\r\n\r\nNO_TOOL \t\r\n\r\n# Reason\r\nNo sound encoding.\r\n",
])
def test_no_tool_spacing_keeps_model_decision(text):
    assert parse_proposal(text)=={"call_requested":False,"reason":"No sound encoding."}


@pytest.mark.parametrize("text", [
    "# Decision\nCALL_TOOL\nNO_TOOL\n\n"+FORMALIZATION,
    "# Decision\nCALL_TOOL because it helps\n\n"+FORMALIZATION,
    "# Decision\ncall_tool\n\n"+FORMALIZATION,
    "# Decision\nNO_TOOL\n\n"+FORMALIZATION,
    "# Decision\nCALL_TOOL\n# Reason\nNo sound encoding.",
    "# Decision\nNO_TOOL\n# Reason\n",
    "# Decision\nNO_TOOL\n# Reason\nReason.\n# Extra\nIgnored instructions.",
    "# Decision\nNO_TOOL\n# Decision\nNO_TOOL\n# Reason\nReason.",
    "Preface.\n# Decision\nNO_TOOL\n# Reason\nReason.",
    "# Reason\nReason.\n# Decision\nNO_TOOL",
    "# Decision\nCALL_TOOL\n\n"+FORMALIZATION.replace("# Guard Program", "# Unexpected"),
])
def test_ambiguous_or_malformed_decisions_still_fail(text):
    with pytest.raises(ValueError):
        parse_proposal(text)


def test_spacing_fix_does_not_synthesize_missing_guard_fence():
    malformed=FORMALIZATION.replace("```guard-args\n", "", 1)
    malformed=malformed.replace("\n```\n\n# Tool Arguments", "\n\n# Tool Arguments", 1)
    with pytest.raises(ValueError,match="guard-args fence"):
        parse_proposal("# Decision\nCALL_TOOL\n\n"+malformed)


def test_generated_witness_bound_does_not_relax_model_input_limit():
    ast={"add":[{"symbol":"x"}]*8000}
    with pytest.raises(ValueError,match="node limit"):
        tool.exact_tools._expression(ast,{"x":x})
    assert tool.exact_tools._expression(ast,{"x":x},max_ast_nodes=tool.MAX_WITNESS_AST_NODES)==8000*x
    with pytest.raises(ValueError,match="node limit"):
        tool.exact_tools._expression({"add":[{"symbol":"x"}]*70000},{"x":x},
                                    max_ast_nodes=tool.MAX_WITNESS_AST_NODES)
