import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('recovery_worker', ROOT / 'scripts/recover_proofbench_votes.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validation = load('standalone_validation', ROOT / 'harnesses/cross_lane_voter/validation.py')
recover = worker.recovery.recover_final_comparison


def complete(winner='B'):
    fields = ('Established theorem: theorem\nClaim gap: NONE.\n'
              'Qualifications and supplied repairs: NONE.\nDecisive checks: supplied checks\n')
    return '# Proof comparison\n\n## Proof A\n' + fields + '\n## Proof B\n' + fields + '\n## Decision\nWinner: ' + winner + '\nReason: explicit reason\n'


def unfinished(winner='B'):
    return '# Proof comparison\n## Proof A\nUnfinished A\n## Proof B\nUnfinished B\nWinner: ' + winner + '\n'


class RecoveryTests(unittest.TestCase):
    def missing_checks(self, citations=('Lines 3-5', 'Line 7')):
        bullets = '\n'.join('- Existing evidence at ' + citation + ': ' +
            'the submitted argument establishes this implication from the stated hypotheses without extra assumptions.'
            for citation in citations)
        before, after = complete().split('## Proof B\n', 1)
        after = after.replace('Qualifications and supplied repairs: NONE.\nDecisive checks: supplied checks',
                              'Qualifications and supplied repairs:\n' + bullets)
        return before + '## Proof B\n' + after, bullets

    def test_missing_checks_copies_inline_citations_verbatim(self):
        text, evidence = self.missing_checks()
        normalized, receipt = worker.recovery.recover_comparison(text, validation.strict_parse)
        expected = text.replace('## Decision', 'Decisive checks:\n' + evidence + '\n\n## Decision')
        self.assertEqual(normalized, expected)
        self.assertEqual(receipt['policy'], worker.recovery.CHECKS_POLICY)
        self.assertEqual(receipt['copied_evidence_sha256'], worker.recovery.sha(evidence))
        self.assertEqual(receipt['normalized_response_sha256'], worker.recovery.sha(normalized))
        self.assertEqual(receipt['winner_label'], 'B')
        self.assertEqual(receipt['model_calls'], 0)
        self.assertFalse(receipt['new_mathematical_text'])

    def test_missing_checks_accepts_existing_prefix_citations_too(self):
        text, _ = self.missing_checks()
        text = text.replace('- Existing evidence at ', '- ')
        normalized, _ = worker.recovery.restore_checks_label(text, validation.strict_parse)
        self.assertEqual(validation.strict_parse(normalized)['winner_label'], 'B')

    def test_missing_checks_rejects_missing_or_invalid_citations(self):
        for citation in ('no citation', 'Line 0', 'Lines 8-2', 'Line 7-0', 'Line 7x'):
            with self.subTest(citation=citation), self.assertRaises(ValueError):
                text, _ = self.missing_checks((citation, 'Line 7'))
                worker.recovery.restore_checks_label(text, validation.strict_parse)

    def test_missing_checks_rejects_insufficient_evidence_or_ambiguous_framing(self):
        text, _ = self.missing_checks()
        variants = [self.missing_checks(('Line 7',))[0],
                    text.replace('- Existing evidence at Lines 3-5:', '- Line 3:')
                        .replace('the submitted argument establishes this implication from the stated hypotheses without extra assumptions.', 'short'),
                    text.replace('## Proof B', '## Proof A'),
                    '```\n' + text + '\n```',
                    text.replace('## Decision', 'Decisive checks:\n\n## Decision'),
                    text.replace('Winner: B', 'Winner: A\nWinner: B')]
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                worker.recovery.restore_checks_label(variant, validation.strict_parse)

    def test_explicit_proof_prefix_both_labels(self):
        for label in ('A', 'B'):
            text = complete(label).replace('Winner: ' + label, 'Winner: Proof ' + label)
            normalized, receipt = worker.recovery.recover_comparison(text, validation.strict_parse)
            self.assertEqual(normalized, complete(label))
            self.assertEqual(receipt['removed_text'], 'Proof ')
            self.assertEqual(receipt['winner_label'], label)

    def test_prefix_does_not_allow_extra_winner(self):
        text = complete().replace('Winner: B', 'Winner: Proof B\nWinner: A')
        with self.assertRaises(ValueError):
            worker.recovery.recover_comparison(text, validation.strict_parse)

    def test_prefix_does_not_allow_prose_or_nonbinary_choice(self):
        for label in ('A or B', 'B because it is better', 'C', ''):
            text = complete().replace('Winner: B', 'Winner: Proof ' + label)
            with self.subTest(label=label), self.assertRaises(ValueError):
                worker.recovery.recover_comparison(text, validation.strict_parse)

    def test_prefix_keeps_other_obligations_strict(self):
        text = complete().replace('Winner: B', 'Winner: Proof B').replace('Reason: explicit reason', '')
        with self.assertRaises(ValueError):
            worker.recovery.recover_comparison(text, validation.strict_parse)

    def test_valid_answer_unchanged(self):
        self.assertEqual(recover(complete(), validation.strict_parse), (complete(), None))

    def test_exact_final_block_and_hashes(self):
        text = unfinished() + complete()
        final, receipt = recover(text, validation.strict_parse)
        self.assertEqual(final, complete())
        self.assertEqual(text[receipt['selected_start_char']:receipt['selected_end_char']], final)
        self.assertEqual(receipt['explicit_winners'], ['B', 'B'])
        self.assertEqual(receipt['original_response_sha256'], worker.recovery.sha(text))

    def test_either_label_supported(self):
        final, receipt = recover(unfinished('A') + complete('A'), validation.strict_parse)
        self.assertEqual(receipt['winner_label'], 'A')

    def test_conflicting_winner_rejected(self):
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            recover(unfinished('A') + complete('B'), validation.strict_parse)

    def test_nonbinary_or_malformed_winners_rejected(self):
        for label in ('tie', '', 'A or B', 'B because it is better', 'C'):
            with self.subTest(label=label), self.assertRaises(ValueError):
                recover(unfinished(label) + complete(), validation.strict_parse)

    def test_two_complete_answers_rejected_even_if_agree(self):
        with self.assertRaises(ValueError):
            recover(complete() + complete(), validation.strict_parse)

    def test_incomplete_final_rejected(self):
        with self.assertRaises(ValueError):
            recover(unfinished() + complete().split('Reason:')[0], validation.strict_parse)

    def test_no_cherry_picking_earlier_answer(self):
        with self.assertRaises(ValueError):
            recover(complete() + unfinished(), validation.strict_parse)

    def test_fenced_quoted_answer_rejected(self):
        with self.assertRaises(ValueError):
            recover(unfinished() + '```markdown\n' + complete() + '```', validation.strict_parse)

    def test_no_invented_header_or_missing_field_repair(self):
        for text in (unfinished() + complete().replace('# Proof comparison\n', ''),
                     unfinished() + complete().replace('Claim gap: NONE.', '')):
            with self.assertRaises(ValueError):
                recover(text, validation.strict_parse)

    def test_crlf_preserves_original_bytes(self):
        text = (unfinished() + complete()).replace('\n', '\r\n')
        final, receipt = recover(text, validation.strict_parse)
        self.assertEqual(final, complete().replace('\n', '\r\n'))


class SavedTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pointer = Path('/tmp/proofbench_b112_twice_latest.txt')
        if not pointer.exists():
            raise unittest.SkipTest('Saved live-suite fixture not available on this machine')
        suite = Path(pointer.read_text().strip())
        cls.config = worker.read(suite / 'config.json')
        cls.api = worker.setup(cls.config)
        cls.job = next(j for j in cls.config['jobs'] if j['problem_id'] == 'PB-Basic-008')
        cls.root = next((Path(cls.job['output']) / 'generation/run/cross_lane_voter/PB-Basic-008').glob('*/audit_plan.json')).parent
        cls.task = next(t for t in worker.read(cls.root / 'audit_plan.json')['audits'] if t['case_id'] == 'pair_05_qwen_forward')

    def test_actual_saved_response_bound_and_replay_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            one = worker.saved_vote(self.root, self.task, Path(tmp), self.api)
            two = worker.saved_vote(self.root, self.task, Path(tmp), self.api)
        self.assertEqual(one, two)
        self.assertEqual(one[0]['selected_candidate'], 't07_r01')
        self.assertTrue(one[0]['binding_verified'])

    def test_truncated_transport_rejected(self):
        original = worker.read
        def changed(path):
            obj = original(path)
            if str(path).endswith('metadata.json'):
                obj['finish_reason'] = 'length'
            return obj
        with tempfile.TemporaryDirectory() as tmp, patch.object(worker, 'read', changed):
            with self.assertRaisesRegex(ValueError, 'finish normally'):
                worker.saved_vote(self.root, self.task, Path(tmp), self.api)

    def test_mismatched_response_id_rejected(self):
        original = worker.read
        def changed(path):
            obj = original(path)
            if str(path).endswith('raw_response.json'):
                obj['id'] = 'wrong-transport'
            return obj
        with tempfile.TemporaryDirectory() as tmp, patch.object(worker, 'read', changed):
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                worker.saved_vote(self.root, self.task, Path(tmp), self.api)

    def test_wrong_task_binding_rejected(self):
        task = copy.deepcopy(self.task)
        task['input_sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(ValueError, 'Task absent'):
            worker.saved_vote(self.root, task, Path(tmp), self.api)

    def test_full_round_robin_recomputed_offline(self):
        report = worker.recover_problem(self.config, self.job, self.api, False)
        self.assertEqual(report['summaries']['combined']['valid_calls'], 24)
        self.assertEqual(report['summaries']['combined']['votes'],
                         {'t07_r02': 1, 't10_r01': 3, 't10_r02': 8, 't07_r01': 12})
        self.assertEqual(report['summaries']['combined']['disagreeing_pairs'], 1)

    def test_basic009_saved_prefix_and_seed_tie_break(self):
        job = next(j for j in self.config['jobs'] if j['problem_id'] == 'PB-Basic-009')
        report = worker.recover_problem(self.config, job, self.api, False)
        self.assertEqual(report['winner'], 't10_r02')
        self.assertEqual(report['summaries']['combined']['votes'],
                         {'t10_r01': 1, 't07_r01': 7, 't10_r02': 8, 't07_r02': 8})
        self.assertEqual(report['summaries']['combined']['valid_calls'], 24)


if __name__ == '__main__':
    unittest.main()
