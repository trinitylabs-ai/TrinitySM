"""Root route reaches the actual rewrite/audit path only after semantic acceptance."""
import json
import pytest

from . import proof_harness as harness, root_workflow as workflow
from .test_root_classification import program, body
from .test_proof_harness import decisions
from .test_division_audit_repair import audit

THEOREM = 'Classify every stationary point of the function x cubed minus three x on the open interval from minus two to two.'
PROOF = 'There is only one stationary point, by differentiation.'
DRAFT = program(body('(sub (pow x 3) (mul 3 x))', variable='x', mode='stationary_points'),
    'The original function is x cubed minus three x. The interval is the stated open interval, with no excluded denominators.')


def inputs(tmp_path):
    source, proof = tmp_path/'source.json', tmp_path/'proof.md'
    source.write_text(json.dumps({'problem_id': 'synthetic', 'statement': THEOREM, 'reference_solution': 'HIDDEN_REFERENCE_SENTINEL'}))
    proof.write_text(PROOF)
    return source, proof


def test_matcher_dispatches_root_classification(tmp_path, monkeypatch):
    source, proof = inputs(tmp_path)
    detection, matched = decisions(PROOF, operation='real_root_classification')
    class Calls:
        def __init__(self, *a, **kw): pass
        def __call__(self, **kw):
            assert 'HIDDEN_REFERENCE_SENTINEL' not in kw['user_prompt']
            answer = detection if kw['stage'].endswith('gap_detection') else matched
            return answer, kw['parser'](answer), {}
    monkeypatch.setattr(harness.rewrite, 'BudgetedCalls', Calls)
    seen = []
    def track(*a, **kw):
        seen.append(kw['matcher']['operation'])
        return {'state': 'completed', 'exact_verified': False}
    monkeypatch.setattr(workflow, 'run_track', track)
    result = harness.run(problem_file=source, proof_file=proof, output=tmp_path/'run', execute_models=True,
        config=harness.Config(batch_size=1, workers=1, cycles=1))
    assert seen == ['real_root_classification']
    assert result['outcome'] == 'NO_CERTIFIED_REWRITE'


@pytest.mark.parametrize('accepted', [False, True])
@pytest.mark.parametrize('alternate_container', [False, True])
def test_same_draft_audit_controls_exact_tool_and_full_synthesis(tmp_path, monkeypatch, accepted, alternate_container):
    source, proof = inputs(tmp_path)
    root = tmp_path/'run'
    harness.run(problem_file=source, proof_file=proof, output=root)
    detection, matched = decisions(PROOF, operation='real_root_classification')
    for name, text in [('input/original_theorem.md', THEOREM), ('input/resolver1_proof.md', PROOF),
                       ('01_detection/detection.md', detection), ('02_matcher/matcher.md', matched)]:
        harness.base.write_text(root/'01_acquisition'/name, text)
    matcher = harness.base._parse_matcher(matched, harness.acquisition.protocol.parse_detection(detection)['desired_exact_fact'], harness.matcher_operations())
    monkeypatch.setattr(workflow.certificate, 'validate_markdown_budget_forcing', lambda *a, **kw: None)
    events, synthesis_events, providers = [], [], []
    draft = DRAFT.replace('```root-args', '```lisp') if alternate_container else DRAFT
    def calls(**kw):
        events.append(kw['stage'])
        assert 'HIDDEN_REFERENCE_SENTINEL' not in kw['user_prompt']
        if kw['stage'] == 'root_semantic_audit':
            assert 'Deterministic Root Compilation' in kw['user_prompt']
            assert 'root_count' not in kw['user_prompt'] and 'sign_cells' not in kw['user_prompt']
            if alternate_container:
                assert 'root-container-syntax-v1' in kw['user_prompt']
                assert draft in kw['user_prompt']
        answer = draft if kw['stage'] == 'root_formalization' else audit(accepted)
        return answer, kw['parser'](answer), {}
    actual_synthesis = workflow.appendix_synthesis.run
    core = workflow.appendix_synthesis.rewrite.pipeline.synthesis_pipeline
    monkeypatch.setattr(workflow.appendix_synthesis.rewrite.pipeline, '_verify_synthesis_budget_forcing', lambda **kw: [])
    def synthesis(**kw):
        provider = kw['provider']
        providers.append(provider)
        evidence = provider.materialize()
        assert evidence.verification['root_count'] == 2
        def model_call(**request):
            synthesis_events.append(request['stage'])
            assert 'real_root_classification' in request['user_prompt']
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
    result = workflow.run_track(root, root/'02_formalizations/sample_01', config=harness.Config(cycles=1), seed=1,
        matcher=matcher, select=lambda p, fn: fn(), should_stop=lambda: False, caller=calls)
    assert result['state'] == 'completed', result
    assert result['exact_verified'] == accepted
    assert (root/'02_formalizations/sample_01/cycles/cycle_01/formalization.md').read_text().strip() == draft.strip()
    assert events == ['root_formalization', 'root_semantic_audit']
    if accepted:
        assert synthesis_events == ['modular_exact_evidence_whole_proof_rewrite', 'modular_exact_evidence_whole_proof_audit']*2
        provider = providers[0]
        for name in ['draft', 'compilation', 'semantic_audit', 'certificate', 'matcher', 'theorem']:
            original = provider.paths[name].read_bytes()
            provider.paths[name].write_text('Changed after audit')
            with pytest.raises(ValueError, match='source drift'):
                provider.materialize()
            provider.paths[name].write_bytes(original)


def test_production_formalizer_cannot_skip_semantic_bindings():
    assert not workflow.inspect('```root-args\n'+body('z')+'\n```', THEOREM, harness.Config())['parser_valid']
