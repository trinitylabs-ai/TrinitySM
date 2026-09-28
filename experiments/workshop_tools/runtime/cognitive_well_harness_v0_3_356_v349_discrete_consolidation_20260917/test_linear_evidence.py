from fractions import Fraction

import pytest

from . import linear_evidence as linear, local_evidence_experiment as pilot


def program(conclusion, assumptions="assume = domain :: (ge x 0)", definitions="", variables="x"):
    return f"```linear-args\nvariables = {variables}\n{definitions}\n{assumptions}\nconclude = {conclusion}\n```"


def test_real_counterexample_is_independently_replayed():
    parsed=linear.parse(program("(ge x 1)"))
    result=linear.check(parsed)
    assert result["verdict"]=="COUNTEREXAMPLE" and result["rational_replay_verified"]
    assert 0 <= Fraction(result["witness"]["x"]) < 1
    assert result["global_theorem_proved"] is False


def test_exact_local_implication_and_nonvacuity():
    result=linear.check(linear.parse(program("(ge (add x 1) 1)")))
    assert result["verdict"]=="LOCAL_IMPLICATION_HOLDS"
    assert result["independently_checked_unsat_certificate"] is False
    bad=linear.parse(program("(ge x 1)","assume = contradiction :: (and (gt x 1) (lt x 0))"))
    assert linear.check(bad)["verdict"]=="INCONSISTENT_PREMISES"
    assert not linear.check(bad)["usable_evidence"]


@pytest.mark.parametrize("expr,expected", [
    ("(kth_largest 2 5 5 1)",5), ("(min -2 3)",-2), ("(max -2 3)",3),
    ("(abs -3)",3), ("(div 1 3)",Fraction(1,3)),
    ("(ite (lt 1 2) 7 9)",7), ("(mul 2 (add 3 4))",14),
])
def test_piecewise_linear_operations_exact(expr,expected):
    target=f"(rational {expected.numerator} {expected.denominator})" if isinstance(expected,Fraction) else str(expected)
    parsed=linear.parse(program(f"(eq answer {target})",assumptions="",definitions=f"define = answer :: {expr}",variables="NONE"))
    assert linear.check(parsed)["verdict"]=="LOCAL_IMPLICATION_HOLDS"
    decoder,_,goal=linear.build(parsed,{})
    assert decoder.env["answer"]==expected and goal is True


@pytest.mark.parametrize("body", [
    "(ge (mul x x) 0)", "(ge (div 1 x) 0)", "(eq (div x 0) 0)",
    "(eq (kth_largest 0 x 1) 0)", "(eq (kth_largest 3 x 1) 0)",
    "(eq (sin x) 0)", "(eq missing 0)", "(add x 1)",
    "(eq (rational 1 0) 0)", "(eq (mul x (max x 1)) 0)",
    "(and (ge x 0) 1)", "(eq (ite x 1 0) 0)",
])
def test_invalid_nonlinear_or_mistyped_inputs_fail(body):
    with pytest.raises(ValueError): linear.parse(program(body))


def test_strict_inequalities_and_order_statistics_replay():
    parsed=linear.parse(program("(ge rank 2)","assume = bounds :: (and (gt x 0) (lt x 1))",
                                "define = rank :: (kth_largest 2 x 2 1)"))
    result=linear.check(parsed)
    assert result["verdict"]=="COUNTEREXAMPLE"
    assert result["evaluated_definitions"]["rank"]=="1"


def test_normalization_exact_idempotent_and_no_comparison_changes():
    raw=program("(le x 0.125)","assume = domain :: (ge x -0.25)").replace("linear-args","tool-args")
    canonical,changes=linear.normalize(raw)
    assert "(le x (rational 1 8))" in canonical
    assert "(ge x (rational -1 4))" in canonical
    assert {r["kind"] for r in changes}=={"fence_alias","exact_decimal"}
    assert linear.normalize(canonical)==(canonical,[])
    assert linear.parse(raw)==linear.parse(canonical)
    assert linear.check(linear.parse(raw))["rational_replay_verified"]


@pytest.mark.parametrize("literal",["0.125", "-.125", "+.125", "1.000", ".5", "2."])
def test_decimal_values_exact(literal):
    value=Fraction(literal)
    parsed=linear.parse(program(f"(eq {literal} (rational {value.numerator} {value.denominator}))",assumptions="",variables="NONE"))
    assert linear.check(parsed)["verdict"]=="LOCAL_IMPLICATION_HOLDS"


@pytest.mark.parametrize("literal",["1e-3","1/3","0.1foo","0..1","0.0000001","nan","0.1_2"])
def test_normalization_rejects_ambiguous_or_out_of_bounds_literals(literal):
    with pytest.raises(ValueError): linear.parse(program(f"(le x {literal})"))


INPUTS={"theorem.md":"Assess the stated claim.","original_proof.md":"A proposed argument.",
        "repair_brief.md":"Every nonnegative real number is at least one.",
        "resulting_proof.md":"Every nonnegative real number is at least one."}


def proposal():
    return "\n\n".join(("# Decision","CALL_TOOL","# Operation",linear.OPERATION,
        "# Claim",INPUTS["repair_brief.md"],"# Source","repair_brief","# Source Excerpt",'"'+INPUTS["repair_brief.md"]+'"',
        "# Semantic Bindings","x is the source's arbitrary nonnegative real number.",
        "# Tool Arguments",program("(ge x 1)")))


def audit(checks,accepted=True):
    decision,mark,issues=("ACCEPT","PASS","NONE") if accepted else ("REJECT","FAIL","- Missing source correspondence.")
    return f"# Decision\n\n{decision}\n\n# Checks\n\n"+"\n".join(f"- {s}: {mark}" for s in checks)+f"\n\n# Issues\n\n{issues}"


def test_parser_does_not_solve_and_retains_source_binding(monkeypatch):
    monkeypatch.setattr(linear,"check",lambda *a,**k:pytest.fail("parser ran target search"))
    assert pilot.inspect(proposal(),INPUTS)["parser_valid"]
    bad=proposal().replace('# Source Excerpt\n\n"Every nonnegative', '# Source Excerpt\n\n"Invented nonnegative')
    assert not pilot.inspect(bad,INPUTS)["parser_valid"]


def test_normalization_preserves_model_prose_and_exact_source_gate():
    raw=proposal().replace("# Claim\n\nEvery", "# Claim\n\nDecimal 0.5: Every").replace("linear-args","tool-args").replace("(ge x 1)","(ge x 1.25)")
    parsed=pilot.parse_proposal(raw,INPUTS)
    assert parsed["claim"].startswith("Decimal 0.5:")
    assert parsed["arguments"]["conclusion"]==["ge","x",["rational",5,4]]
    assert parsed["arguments"]["assumptions"][0]["expression"]==["ge","x",0]
    assert parsed["deterministic_normalization"]
    bad=raw.replace('# Source Excerpt\n\n"Every nonnegative', '# Source Excerpt\n\n"Every ... nonnegative')
    assert not pilot.inspect(bad,INPUTS)["parser_valid"]


@pytest.mark.parametrize("mode",["valid","changed_input","prior_audit","prior_tool","prior_pass","changed_draft"])
def test_saved_normalization_recovery_bounds(tmp_path,monkeypatch,mode):
    source=tmp_path/"source"; root=source/"cycles/cycle_03"
    hashes={name:pilot.base.sha256_text(value) for name,value in INPUTS.items()}
    pilot.write(source/"manifest.json",{"input_sha256":hashes})
    pilot.write(source/"status.json",{"state":"completed"})
    pilot.write(root/"parser.json",{"parser_valid":mode=="prior_pass"})
    pilot.base.write_text(root/"formalization.md",proposal())
    pilot.write(root/"formalizer/call.json",{})
    if mode=="prior_audit": pilot.base.write_text(root/"audit.md","REJECT")
    if mode=="prior_tool": (root/"tool").mkdir()
    supplied=dict(INPUTS)
    if mode=="changed_input": supplied["theorem.md"]+=" changed"
    def validate(*args,**kwargs):
        if mode=="changed_draft": raise ValueError("provenance changed")
    monkeypatch.setattr(pilot.certificate,"validate_markdown_budget_forcing",validate)
    if mode!="valid":
        with pytest.raises(ValueError): pilot.load_saved(source,3,supplied)
        return
    stages=[]
    def caller(**kwargs):
        stages.append(kwargs["stage"])
        assert kwargs["stage"]=="local_evidence_semantic_audit"
        text=audit(pilot.FORMAL_CHECKS,False)
        return text,kwargs["parser"](text),{}
    result=pilot.run(supplied,tmp_path/"resumed",1,caller=caller,saved=(source,3))
    assert result["state"]=="completed"
    assert stages==["local_evidence_semantic_audit"]
    assert result["fresh_formalization_calls"]==0 and result["tool_invocations"]==0


@pytest.mark.parametrize("mode", ["parser_failure","audit_reject","counterexample","inconclusive"])
def test_pilot_gates_no_manual_decision_changes(tmp_path,monkeypatch,mode):
    monkeypatch.setattr(pilot.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    calls=[]; executions=[]
    def caller(**kwargs):
        assert kwargs["request_timeout_sec"]==900
        stage=kwargs["stage"];calls.append(stage)
        if stage=="local_evidence_formalization": text="malformed" if mode=="parser_failure" else proposal()
        elif stage=="local_evidence_semantic_audit": text=audit(pilot.FORMAL_CHECKS,mode!="audit_reject")
        elif stage=="local_evidence_proof_rewrite":
            assert kwargs["role"].model=="Qwen/Qwen3.6-27B"
            assert "COUNTEREXAMPLE" in kwargs["user_prompt"]
            text="# Outcome\n\nREWRITTEN_PROOF\n\n# Repair Brief\n\nWithdraw the claim.\n\n# Proof\n\nZero is a nonnegative real number smaller than one."
        else: text=audit(pilot.PROOF_CHECKS)
        return text,kwargs["parser"](text),{}
    def tool(parsed,destination,inputs):
        executions.append(parsed)
        if mode=="inconclusive": return {"verdict":"INCONCLUSIVE","usable_evidence":False},"Tool inconclusive."
        return pilot.execute_tool(parsed,destination,inputs)
    result=pilot.run(INPUTS,tmp_path/"pilot",31,cycles=1,caller=caller,tool=tool)
    assert result["state"]=="completed",result
    assert result["request_timeout_sec"]==900
    assert len(calls)==(1 if mode=="parser_failure" else 4 if mode=="counterexample" else 2)
    assert len(executions)==(1 if mode in {"counterexample","inconclusive"} else 0)
    if mode=="counterexample":
        assert result["proof_audit"]=="ACCEPT" and result["whole_proof_independently_certified"] is False
    if mode=="parser_failure": assert result["cycles"][0]["semantic_audit"]=="SKIPPED_PARSER_FAIL"


@pytest.mark.parametrize("mode",["gemma","qwen","changed_witness","changed_audit","changed_input"])
def test_rewrite_only_reuses_verified_evidence(tmp_path,monkeypatch,mode):
    import json
    monkeypatch.setattr(pilot.certificate,"validate_markdown_budget_forcing",lambda *a,**k:None)
    source=tmp_path/"source"
    def initial(**kwargs):
        stage=kwargs["stage"]
        if stage=="local_evidence_proof_rewrite": raise TimeoutError("timed out")
        text=proposal() if stage=="local_evidence_formalization" else audit(pilot.FORMAL_CHECKS)
        return text,kwargs["parser"](text),{}
    assert pilot.run(INPUTS,source,3,cycles=1,caller=initial)["state"]=="failed_closed"
    if mode=="changed_witness":
        path=source/"cycles/cycle_01/tool/result.json"
        result=json.loads(path.read_text());result["witness"]["x"]="2";pilot.write(path,result)
    elif mode=="changed_audit":
        pilot.base.write_text(source/"cycles/cycle_01/audit.md",audit(pilot.FORMAL_CHECKS,False))
    elif mode=="changed_input": pilot.base.write_text(source/"input/theorem.md","Changed theorem.")
    if mode.startswith("changed"):
        with pytest.raises(ValueError): pilot.load_evidence(source)
        return
    monkeypatch.setattr(linear,"check",lambda *a,**k:pytest.fail("reran solver"))
    calls=[]
    def caller(**kwargs):
        calls.append(kwargs["stage"])
        assert kwargs["request_timeout_sec"]==900
        if kwargs["stage"]=="local_evidence_proof_rewrite":
            expected=pilot.base.DEFAULT_GEMMA_MODEL if mode=="gemma" else "Qwen/Qwen3.6-27B"
            assert kwargs["role"].model==expected
            text="# Outcome\n\nREWRITTEN_PROOF\n\n# Repair Brief\n\nWithdraw the claim.\n\n# Proof\n\nZero disproves the claim."
        else: text=audit(pilot.PROOF_CHECKS)
        return text,kwargs["parser"](text),{}
    result=pilot.rewrite_from_evidence(source,tmp_path/"rewrite_only",3,rewriter_name=mode,caller=caller)
    assert result["state"]=="completed",result
    assert result["tool_invocations"]==0 and result["fresh_formalization_calls"]==0
    assert calls==["local_evidence_proof_rewrite","local_evidence_rewritten_proof_audit"]
