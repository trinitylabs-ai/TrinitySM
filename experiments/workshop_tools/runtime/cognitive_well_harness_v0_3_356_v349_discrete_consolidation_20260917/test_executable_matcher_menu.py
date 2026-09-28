"""Regression coverage for advertised operations that stopped before execution."""
import pytest

from . import proof_harness as h
from .test_proof_harness import sources, decisions
from .test_acquisition_reuse import saved


@pytest.mark.parametrize('allowed', [
    ('polynomial_ideal_membership', 'exact_geometry', 'rational_identity', 'real_root_classification'),
    ('real_root_classification',),
    ('exact_geometry',), ('rational_identity',), ('polynomial_ideal_membership',),
    ('uniform_partition_count',), ('symbolic_modular_order',),
])
def test_prompt_and_parser_share_only_executable_choices(tmp_path, allowed):
    problem, proof = sources(tmp_path)
    problem = h.acquisition.v0220.load_problem(problem)
    detection, _ = decisions(proof.read_text().strip())
    detection = h.acquisition.protocol.parse_detection(detection)
    excluded = tuple(op for op in h.EXECUTABLE_OPERATIONS if op not in allowed)
    assert h.matcher_operations(excluded) == allowed
    prompts = h.matcher_system(allowed) + h.matcher_prompt(problem, proof.read_text(), detection, allowed)
    all_operations = tuple(h.base.exact_tools.EXPOSED_OPERATIONS) + h.GEOMETRY_OPERATIONS + h.ROOT_OPERATIONS + h.DISCRETE_OPERATIONS
    for operation in all_operations:
        _, response = decisions(proof.read_text().strip(), operation=operation)
        if operation in allowed:
            assert operation in prompts
            assert h.base._parse_matcher(response, detection['desired_exact_fact'], allowed)['operation'] == operation
        else:
            assert operation not in prompts
            with pytest.raises(ValueError):
                h.base._parse_matcher(response, detection['desired_exact_fact'], allowed)


def test_exclusions_cannot_leave_an_empty_executable_menu():
    with pytest.raises(ValueError, match='cannot exclude all'):
        h.Config(excluded_operations=h.EXECUTABLE_OPERATIONS).validate()
    with pytest.raises(ValueError, match='unknown'):
        h.Config(excluded_operations=('invented_operation',)).validate()
    assert h.matcher_operations(('simplify_identity',)) == h.matcher_operations()


def test_detection_capabilities_follow_the_allowlist_and_are_task_independent():
    text = h.detection_capabilities(('uniform_partition_count',))
    assert 'binomial(N-1,K-1)' in text and 'phi(M)' not in text
    text = h.detection_capabilities(('symbolic_modular_order',))
    assert 'phi(M)' in text and 'binomial' not in text
    assert 'PB-' not in text and 'xy' not in text


@pytest.mark.parametrize('op', h.DISCRETE_OPERATIONS)
def test_immutable_claim_reference_binds_exact_upstream_text(op):
    claim = 'A condition with $u > v$ and punctuation.'
    response = '# Decision\n\nCALL_TOOL\n\n# Operation\n\n'+op+'\n\n# Immutable Claim\n\nDETECTED_CLAIM\n\n# Fit Rationale\n\nThe conditional evidence fits.'
    parsed = h.parse_matcher(response, claim, h.matcher_operations())
    assert parsed['claim'] == claim and parsed['claim_sha256'] == h.base.sha256_text(claim)
    assert parsed['operation'] == op
    with pytest.raises(ValueError):
        h.parse_matcher(response.replace('DETECTED_CLAIM', claim.replace('>', '<')), claim, h.matcher_operations())
    with pytest.raises(ValueError):
        h.parse_matcher(response.replace('DETECTED_CLAIM', 'OTHER_CLAIM'), claim, h.matcher_operations())
    with pytest.raises(ValueError):
        h.parse_matcher(response.replace(op, 'polynomial_ideal_membership'), claim, h.matcher_operations())


def test_old_advertised_menu_cannot_bypass_new_matcher(tmp_path, monkeypatch):
    problem, proof, old, _ = saved(tmp_path, monkeypatch)
    h.rewrite.write_record(old / '01_acquisition/manifest.json', {
        'allowed_matcher_operations': list(h.base.exact_tools.EXPOSED_OPERATIONS) + list(h.GEOMETRY_OPERATIONS)})
    with pytest.raises(ValueError, match='operation menu differs'):
        h.run(problem_file=problem, proof_file=proof, output=tmp_path / 'new', acquisition_from=old)
