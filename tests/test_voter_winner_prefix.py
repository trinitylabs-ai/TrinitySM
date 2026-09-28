"""Read explicit Proof A/B winners without changing frozen inference artifacts."""
import importlib
from pathlib import Path

import pytest

from cross_lane_replay import response, sample
from test_public_reproduction import pipeline


def parsers():
    voter = pipeline.voter_module('1.12.0')
    frozen = importlib.import_module(voter.__package__ + '.validation').parse
    return voter, frozen


@pytest.mark.parametrize('label', ['A', 'B'])
def test_prefix_is_explicit_and_receipt_preserves_original_hash(label):
    voter, frozen = parsers()
    text = sample('Proof ' + label)
    with pytest.raises(ValueError, match='unambiguous Winner'):
        frozen(text)
    parsed = voter.parse(text)
    assert parsed['winner_label'] == label
    assert parsed['response_sha256'] == voter.digest(text.encode())
    repair = parsed['mechanical_recovery']
    assert repair['policy'] == 'explicit-winner-proof-prefix-v1'
    assert repair['model_calls'] == 0 and repair['new_mathematical_text'] is False
    assert repair['removed_text'] == 'Proof '
    start, end = repair['removed_start_char'], repair['removed_end_char']
    normalized = text[:start] + text[end:]
    assert normalized == sample(label)
    assert repair['original_response_sha256'] == voter.digest(text.encode())
    assert repair['normalized_response_sha256'] == voter.digest(normalized.encode())
    assert parsed['normalized_sha256'] == frozen(normalized)['normalized_sha256']
    assert voter.parse(sample(label)) == frozen(sample(label))
    assert pipeline.voter_module('1.12.0').parse is voter.parse


@pytest.mark.parametrize('text', [
    sample('Proof A or B'), sample('Proof C'), sample('Proof '),
    sample('Proof A because it is better'), sample('Proof A (preferred)'),
    sample('Proof A') + '\nWinner: B',
    sample('Proof A') + '\nWinner: Proof A',
    sample('Proof A').replace('Reason:', 'Explanation:'),
    sample('Proof A').replace('## Proof B', '## Proof A'),
    sample('Proof A').replace('Claim gap:', 'Unspecified gap:'),
])
def test_prefix_does_not_relax_ambiguity_or_other_required_fields(text):
    with pytest.raises(ValueError):
        parsers()[0].parse(text)


@pytest.mark.parametrize('label', ['A', 'B'])
def test_controller_recollects_23_of_24_without_inference_or_raw_edits(tmp_path, monkeypatch, label):
    voter, frozen = parsers()
    root = tmp_path / 'run'
    candidates = {}
    for cid in pipeline.CANDIDATES:
        proof = root / 'source_proofs' / (cid + '.md')
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text(f'Complete proof from {cid}.\n')
        candidates[cid] = dict(candidate_id=cid, selected_stage='refinement_2',
                               proof_path=str(proof), proof_sha256=pipeline.proof_hash(proof))
    runtime = dict(raw_seed_offset=0, seed_namespace=voter.DEFAULT_NAMESPACE, model_timeout_sec=600,
                   gemma_endpoint='http://127.0.0.1:8030/v1', qwen_endpoint='http://127.0.0.1:8027/v1')
    pipeline.write(root / 'harness_release.json', dict(parameters=runtime,
        release_sha256=pipeline.sha(pipeline.IMPLEMENTATION / 'releases/1.12.0/release.json')))
    monkeypatch.setattr(pipeline, 'collect_lane', lambda _root, _pid, cid, _issues: candidates[cid])
    monkeypatch.setattr(pipeline, 'voter_problem', lambda *_: 'Prove the claim.')
    calls, before = [], {}
    case_id = 'pair_06_gemma_reverse'

    def frozen_worker(command, **kwargs):
        assert command[command.index('-m') + 1].endswith('cross_lane_voter.live')
        directory = Path(command[-1])

        def call(**kw):
            calls.append(kw)
            winner = 'Proof ' + label if case_id in str(kw['output_dir']) else 'A'
            return response(kw, winner)

        # The actual child is frozen: reproduce its invalid cached vote, then
        # let the real public collection path re-read the original response.
        with monkeypatch.context() as child:
            child.setattr(voter, 'parse', frozen)
            old = voter.run(directory, call)
        assert old['state'] == 'incomplete'
        assert old['summaries']['combined']['valid_calls'] == 23
        before.update({p: p.read_bytes() for p in directory.rglob('*') if p.is_file()})
        return 2

    monkeypatch.setattr(pipeline, 'run_process', frozen_worker)
    selected = pipeline.cross_lane_selection(root, 'P1', '1.12.0', execute=True)
    assert len(calls) == 24
    assert selected['state'] == 'completed'
    assert selected['summaries']['combined']['valid_calls'] == 24
    assert sum(selected['summaries']['combined']['votes'].values()) == 24
    repaired = next(v for v in selected['vote_table'] if v['case_id'] == case_id)
    assert repaired['binding_verified'] and repaired['mechanical_recovery']['model_calls'] == 0
    assert repaired['selected_candidate'] == repaired['presentation_order'][0 if label == 'A' else 1]
    assert 'error' not in repaired
    assert (root / selected['proof']).read_bytes() == Path(
        candidates[selected['selected_candidate']]['proof_path']).read_bytes()
    # Only derived report files may change; saved failures, bindings, prompts,
    # raw responses, proof inputs and transport receipts remain byte-identical.
    for path, data in before.items():
        if path.name not in ('SELECTIONS.json', 'REPORT.md'):
            assert path.read_bytes() == data, path
    monkeypatch.setattr(pipeline, 'run_process', lambda *a, **kw: pytest.fail('Recollection called a model'))
    assert pipeline.cross_lane_selection(root, 'P1', '1.12.0', execute=False) == selected

    # A prefix is never a way around the original response/proof bindings.
    directory = root / selected['artifact_directory']
    call_path = directory / 'cases' / case_id / 'audit/call_result.json'
    call = pipeline.read(call_path)
    call['text'] = call['text'].replace('Proof ' + label, 'Proof ' + ('B' if label == 'A' else 'A'))
    pipeline.write(call_path, call)
    assert pipeline.cross_lane_selection(root, 'P1', '1.12.0', execute=False)['state'] == 'incomplete'


def test_older_frozen_release_keeps_original_parser():
    with pytest.raises(ValueError, match='unambiguous Winner'):
        pipeline.voter_module('1.11.0').parse(sample('Proof A'))
