"""Certificate correctness, false requests, binding, and full workflow dispatch."""
import copy
from itertools import combinations
from math import comb, gcd
from pathlib import Path

import pytest

from . import discrete_certificates as engine, discrete_workflow as workflow
from . import proof_harness as harness, matched_tools
from .test_division_audit_repair import audit


def program(body, kind='partition', bindings='The domain and parameters are exactly the source claim.'):
    return '# Decision\n\nCALL_TOOL\n\n# Semantic Bindings\n\n'+bindings+'\n\n# Discrete Program\n\n```'+kind+'-args\n'+body+'\n```'


def partition(n, k):
    return program(f'population = {n}\nblock_size = {k}\ntotal = nonnegative')


def modular(residue=-1, inverse='(neg z)', offset='z'):
    return program(f'symbols = z\nmodulus = (add (pow z 2) 1)\nassume = modulus_ge_2\nresidue = {residue}\nunit = u :: z :: {inverse}\ncheck = t :: u :: {offset}', 'modular')


@pytest.mark.parametrize('n,k', [(1, 1), (6, 2), (12, 4), (16, 4), (15, 5), (20, 20)])
def test_counting_bound_and_equality_witness(n, k):
    result = engine.compute(partition(n, k))
    weights = [n-1]+[-1]*(n-1)
    good = sum(sum(weights[i] for i in group) >= 0 for group in combinations(range(n), k))
    assert good == result['lower_bound'] == comb(n-1, k-1)
    assert result['partitions'] == result['lower_bound']*result['fixed_block_incidence']
    assert engine.replay(partition(n, k), result) == result


@pytest.mark.parametrize('n,k', [(7, 3), (0, 1), (4, 5), (201, 1)])
def test_invalid_partition_parameters_rejected(n, k):
    with pytest.raises(ValueError):
        engine.compute(partition(n, k))


def test_negative_total_cannot_be_encoded_as_nonnegative():
    with pytest.raises(ValueError):
        engine.compute(partition(6, 2).replace('total = nonnegative', 'total = negative'))


@pytest.mark.parametrize('total', ['0', '5', '101'])
def test_exact_nonnegative_totals_have_the_same_counting_conclusion(total):
    text = partition(12, 4).replace('total = nonnegative', 'total = '+total)
    compiled = engine.compile_program(text)
    assert compiled['program']['declared_total'] == int(total)
    assert compiled['program']['total_derivation'] == 'exact_integer_sign_check'
    assert engine.compute(text)['lower_bound'] == engine.compute(partition(12, 4))['lower_bound']


@pytest.mark.parametrize('total', ['-1', '-999', '0.1', 'positive', 'z', '0+1'])
def test_negative_and_unrecognized_totals_are_rejected(total):
    with pytest.raises(ValueError):
        engine.compute(partition(12, 4).replace('total = nonnegative', 'total = '+total))


@pytest.mark.parametrize('residue,offset', [(-1, 'z'), (0, '-1'), (1, '(neg z)'), (2, '1')])
def test_symbolic_modular_families_and_exact_residues(residue, offset):
    text = modular(residue, offset=offset)
    result = engine.compute(text)
    assert result['units']['u']['quotient'] == '-1'
    assert result['infinitely_many_exponents']
    for z in range(1, 11):
        m = z*z+1
        phi = sum(gcd(i, m) == 1 for i in range(1, m))
        value = {'z': z, '-1': -1, '(neg z)': -z, '1': 1}[offset]
        for n in range(1, 4*phi+3):
            if (n-residue) % phi == 0:
                assert (pow(z, n, m)+value) % m == 0
    assert engine.replay(text, result) == result


def test_constant_modulus_and_nonunit_rejection():
    text = program('symbols = NONE\nmodulus = 7\nassume = modulus_ge_2\nresidue = 2\nunit = u :: 3 :: 5\ncheck = t :: u :: 5', 'modular')
    assert engine.compute(text)['checks'][0]['quotient'] == '2'
    with pytest.raises(ValueError):
        engine.compute(text.replace('modulus = 7', 'modulus = 6'))


@pytest.mark.parametrize('text', [modular(inverse='z'), modular(offset='1'),
    modular().replace('residue = -1', 'residue = -9'),
    modular().replace('modulus_ge_2', 'assume_target'),
    modular().replace('(pow z 2)', '(div 1 z)'),
    modular().replace(':: z ::', ':: undeclared ::')])
def test_false_or_unsupported_modular_claims_fail_closed(text):
    with pytest.raises(ValueError):
        engine.compute(text)


def test_rational_quotient_is_not_integer_divisibility():
    text = program('symbols = z\nmodulus = (mul 2 z)\nassume = modulus_ge_2\nresidue = 0\nunit = u :: 1 :: 1\ncheck = t :: u :: (sub z 1)', 'modular')
    with pytest.raises(ValueError, match='integer-polynomial'):
        engine.compute(text)


def test_tampered_result_and_changed_semantics_rejected():
    text = partition(12, 4)
    saved = engine.compute(text)
    changed = copy.deepcopy(saved); changed['lower_bound'] += 1
    with pytest.raises(ValueError, match='replay differs'):
        engine.replay(text, changed)
    with pytest.raises(ValueError, match='replay differs'):
        engine.replay(text.replace('source claim', 'a different source claim'), saved)
    text = modular(); saved = engine.compute(text)
    changed = copy.deepcopy(saved); changed['units']['u']['quotient'] = '0'
    with pytest.raises(ValueError, match='replay differs'):
        engine.replay(text, changed)


@pytest.mark.parametrize('op,text', [(engine.OPERATIONS[0], partition(12, 4)), (engine.OPERATIONS[1], modular())])
def test_public_tool_route_and_replay(tmp_path, op, text):
    result = matched_tools.run(operation=op, arguments_markdown=text, output=tmp_path/'tool')
    assert result['verdict'] == 'DISCRETE_CERTIFICATE_VERIFIED'
    assert matched_tools.replay(operation=op, arguments_markdown=text, saved_result=result) == result
    assert not result['theorem_proved'] and not result['source_semantics_verified']


def test_operation_substitution_is_rejected():
    result = matched_tools.execute(operation=engine.OPERATIONS[1], arguments_markdown=partition(12, 4))
    assert result['verdict'] == 'INVALID_REQUEST' and not result['usable_evidence']


@pytest.mark.parametrize('accept', [True, False])
def test_provider_pipeline_binds_draft_audit_and_checked_evidence(tmp_path, monkeypatch, accept):
    problem, proof = tmp_path/'problem.json', tmp_path/'proof.md'
    harness.rewrite.write_record(problem, {'problem_id': 'synthetic', 'statement': 'Twelve labeled real weights have nonnegative total. Bound nonnegative four-subsets.'})
    proof.write_text('The bound is asserted without counting its incidences.\n')
    out = tmp_path/'run'; config = harness.Config(batch_size=1, workers=1, cycles=1)
    harness.run(problem_file=problem, proof_file=proof, output=out, config=config)
    acq = out/'01_acquisition'
    for name, value in [('input/original_theorem.md', 'Twelve labeled real weights have nonnegative total.'),
                        ('input/resolver1_proof.md', proof.read_text()), ('01_detection/detection.md', 'Prove the subset bound.'),
                        ('02_matcher/matcher.md', 'uniform_partition_count')]:
        harness.base.write_text(acq/name, value)
    monkeypatch.setattr(workflow.certificate, 'validate_markdown_budget_forcing', lambda *a, **k: None)
    calls, bundles = [], []
    def caller(**kw):
        calls.append(kw['stage'])
        text = partition(12, 4) if kw['stage'] == 'discrete_formalization' else audit(accept)
        return text, kw['parser'](text), {}
    def synthesize(**kw):
        provider = kw['provider']; bundle = provider.materialize(); bundles.append(bundle)
        assert '165' in bundle.appendix_markdown
        draft = provider.paths['draft']; original = draft.read_text()
        draft.write_text(original+'\nchanged')
        with pytest.raises(ValueError, match='drift'):
            provider.materialize()
        draft.write_text(original)
        return {'state': 'completed'}
    monkeypatch.setattr(workflow.appendix_synthesis, 'run', synthesize)
    result = workflow.run_track(out, out/'track', config=config, seed=7,
        matcher={'operation': engine.OPERATIONS[0], 'claim': 'Prove the subset bound.'},
        select=lambda path, fn: fn(), should_stop=lambda: False, caller=caller)
    assert result['state'] == 'completed' and result['exact_verified'] == accept, result
    assert calls == ['discrete_formalization', 'discrete_semantic_audit'] and len(bundles) == int(accept)
    assert (out/'track/cycles/cycle_01/tools/certificate.json').exists() == accept


def test_no_benchmark_specific_runtime_payloads():
    for module in (engine, workflow):
        text = Path(module.__file__).read_text()
        for forbidden in ('PB-Basic-', 'PB-Advanced-', 'benchmarks/', 't07_r01', 't10_r02', '136', '190590400'):
            assert forbidden not in text
