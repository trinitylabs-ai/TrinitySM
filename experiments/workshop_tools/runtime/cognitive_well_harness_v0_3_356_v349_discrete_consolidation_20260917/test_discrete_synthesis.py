"""Exercise real discrete synthesis, claim references and selected-certificate replay."""
import json
import pytest
from . import proof_harness as harness, discrete_workflow as workflow, discrete_resume
from .test_discrete_certificates import partition, modular
from .test_proof_harness import decisions
from .test_division_audit_repair import audit

THEOREM = 'Prove the stated counting or modular conclusion for the given source domain.'
PROOF = 'The result is asserted without justification.'

def inputs(tmp_path):
    source, proof = tmp_path/'source.json', tmp_path/'proof.md'
    source.write_text(json.dumps({'problem_id': 'synthetic', 'statement': THEOREM, 'reference_solution': 'HIDDEN_REFERENCE_SENTINEL'}))
    proof.write_text(PROOF)
    return source, proof

@pytest.mark.parametrize('accepted', [False, True])
@pytest.mark.parametrize('claim_reference', [False, True])
@pytest.mark.parametrize('operation', harness.DISCRETE_OPERATIONS)
def test_same_draft_audit_controls_exact_tool_and_full_synthesis(tmp_path, monkeypatch, accepted, claim_reference, operation):
    source, proof = inputs(tmp_path)
    root = tmp_path/'run'
    harness.run(problem_file=source, proof_file=proof, output=root)
    detection, matched = decisions(PROOF, operation=operation)
    desired = harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact']
    if claim_reference:
        matched = matched.replace(desired, 'DETECTED_CLAIM')
    for name, text in [('input/original_theorem.md', THEOREM), ('input/resolver1_proof.md', PROOF),
                       ('01_detection/detection.md', detection), ('02_matcher/matcher.md', matched)]:
        harness.base.write_text(root/'01_acquisition'/name, text)
    matcher = harness.parse_matcher(matched, harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact'], harness.matcher_operations())
    monkeypatch.setattr(workflow.certificate, 'validate_markdown_budget_forcing', lambda *a, **kw: None)
    events, synthesis_events, providers = [], [], []
    draft = partition(12, 4) if operation == 'uniform_partition_count' else modular()
    def calls(**kw):
        events.append(kw['stage'])
        assert 'HIDDEN_REFERENCE_SENTINEL' not in kw['user_prompt']
        if kw['stage'] == 'discrete_semantic_audit':
            assert 'Deterministic Discrete Compilation' in kw['user_prompt']
            assert 'root_count' not in kw['user_prompt'] and 'sign_cells' not in kw['user_prompt']
        answer = draft if kw['stage'] == 'discrete_formalization' else audit(accepted)
        return answer, kw['parser'](answer), {}
    actual_synthesis = workflow.appendix_synthesis.run
    core = workflow.appendix_synthesis.rewrite.pipeline.synthesis_pipeline
    monkeypatch.setattr(workflow.appendix_synthesis.rewrite.pipeline, '_verify_synthesis_budget_forcing', lambda **kw: [])
    def synthesis(**kw):
        provider = kw['provider']
        providers.append(provider)
        evidence = provider.materialize()
        assert evidence.verification['operation'] == operation
        def model_call(**request):
            synthesis_events.append(request['stage'])
            assert operation in request['user_prompt']
            if request['stage'].endswith('rewrite'):
                assert evidence.appendix_markdown not in request['user_prompt']
                answer = ('There are two stationary points, as follows from the exact derivative computation.\n\n'
                    '[[VERIFIED_EXACT_EVIDENCE]]\n\n'
                    'Differentiating the source function gives f\'(x)=3x^2-3, '
                    'which is three times the product of x minus one and x plus one. Both zeros '
                    'lie in the requested open interval. The derivative is positive between minus two '
                    'and minus one, negative between minus one and one, and positive between one and two. '
                    'The function is differentiable everywhere, so these derivative signs prove a local '
                    'maximum at minus one and a local minimum at one. There are no further stationary '
                    'points because the factored quadratic has no further real zeros. The endpoints '
                    'are excluded by the stated interval and are not stationary points in this classification. '
                    'Thus the earlier assertion of a unique stationary point is replaced by the complete list.')
            else:
                assert evidence.appendix_markdown in request['user_prompt']
                answer = '# Decision\n\nPASS\n\n# Checks\n\n'+'\n'.join('- '+n+': PASS' for n in core.protocol.PROOF_AUDIT_CHECKS)
                answer += '\n\n# Gap Closure\n\n'+'\n'.join('- '+n+': The exact derivative and its full root list establish the classification.' for n in core.tool_purpose.GAP_CLOSURE_LABELS)
                answer += '\n\n# Issues\n\nNONE'
            return answer, request['parser'](answer), {}
        kw['model_call'] = model_call
        return actual_synthesis(**kw)
    monkeypatch.setattr(workflow.appendix_synthesis, 'run', synthesis)
    if not accepted:
        monkeypatch.setattr(workflow, 'execute', lambda *a, **kw: pytest.fail('rejected semantic draft reached root solver'))
    def select(path, fn):
        harness.rewrite.write_record(root/'selection.json', {'request_path': str(path), 'state': 'running'})
        return fn()
    result = workflow.run_track(root, root/'02_formalizations/sample_01', config=harness.Config(cycles=1), seed=1,
        matcher=matcher, select=select, should_stop=lambda: False, caller=calls)
    assert result['state'] == 'completed', result.get('error', result)
    assert result['exact_verified'] == accepted
    assert (root/'02_formalizations/sample_01/cycles/cycle_01/formalization.md').read_text().strip() == draft.strip()
    assert events == ['discrete_formalization', 'discrete_semantic_audit']
    if accepted:
        assert synthesis_events == ['modular_exact_evidence_whole_proof_rewrite', 'modular_exact_evidence_whole_proof_audit']*2
        provider = providers[0]
        for name in ['draft', 'compilation', 'semantic_audit', 'certificate', 'matcher', 'theorem']:
            original = provider.paths[name].read_bytes()
            provider.paths[name].write_text('Changed after audit')
            with pytest.raises(ValueError, match='source drift'):
                provider.materialize()
            provider.paths[name].write_bytes(original)


    if accepted:
        harness.rewrite.write_record(tmp_path/'completion.json', {'worker_exited': True})
        saved = discrete_resume.run(source=root, problem_file=source, proof_file=proof,
            output=tmp_path/'resumed', execute_models=False)
        assert saved['state'] == 'prepared' and saved['resume']['source_selection_reused']
        assert saved['resume']['new_formalization_calls'] == 0
        from . import selected_resume
        consolidated = selected_resume.run(source=root, problem_file=source, proof_file=proof,
            output=tmp_path/'consolidated_resume', execute_models=False)
        assert consolidated['resume']['route'] == 'discrete'
        assert consolidated['resume']['synthesis_master_seed'] == saved['resume']['synthesis_master_seed']
        assert (tmp_path/'consolidated_resume/export/lemma.md').read_text().strip() == providers[0].bundle.markdown.strip()
        assert synthesis_events == ['modular_exact_evidence_whole_proof_rewrite', 'modular_exact_evidence_whole_proof_audit']*2
        proof.write_text('Another proof')
        with pytest.raises(ValueError, match='differs from source inputs'):
            discrete_resume.prepare(root, source, proof)
        with pytest.raises(ValueError, match='differs from source inputs'):
            selected_resume.prepare(root, source, proof)
