#!/usr/bin/env python3
"""Real saved-response regression, producer replay, and isolated grading resume tests."""
import argparse
import copy
import json
import re
from pathlib import Path
import shutil
import socket
import tempfile
from unittest.mock import patch
from recover import read, write, load, setup, textsha
from acceptance_format import parse, ANNOTATION, install


def main(cfg):
    checks = []
    with patch.object(socket, 'create_connection', side_effect=AssertionError('Offline test attempted network')):
        _, _, _, _, backend, source, _ = setup(cfg)
        boundary = backend.repair_boundary
        call = source / 'lanes/t10_r02/02_r1_cycle_2/cases/imo2026_p4.t10_r02/fusion_acceptance_audit/audit_00'
        texts = [read(next(p for p in folder.glob('*.raw_response.json') if '.pre_budget_forcing.' not in p.name))['choices'][0]['message']['content'].strip()
                 for folder in sorted(call.glob('attempt_*'))]
        results = [parse(boundary.parse_acceptance_certification_markdown, t) for t in texts]
        assert [r['valid'] for r in results] == [False, False, True]
        assert all(r['markdown'] == t and r['sha256'] == textsha(t) for r, t in zip(results, texts))
        checks += ['saved first two substantive defects remain rejected', 'saved third annotated NONE accepted', 'original output and hash preserved']
        for replacement in ('NONE (except an unresolved case)', 'NONE (assuming n is sufficiently large)',
                            ANNOTATION + '\nBut another defect remains.', 'NONE (defect probably corrected by routine completion)'):
            assert not parse(boundary.parse_acceptance_certification_markdown, texts[2].replace(ANNOTATION, replacement))['valid']
        checks.append('unresolved, conditional, uncertain, and appended caveats rejected')
        for text in (re.sub(r'(?im)^(verdict:)\s*CERTIFIED', r'\1 REJECTED', texts[2]),
                     re.sub(r'(## Missing Obligation\s+)NONE', r'\1An unresolved obligation', texts[2])):
            # A valid rejected protocol can remain rejected; it must never certify.
            result = parse(boundary.parse_acceptance_certification_markdown, text)
            assert not (result['valid'] and result['verdict'] == 'CERTIFIED')
        checks.append('verdict and other defect fields cannot be upgraded')
        job = read(Path(cfg['output']) / 'generation/prepared.json')
        fusion = read(job['source_fusion']); effective = read(job['effective_fusion'])
        with backend.runtime_generation_policy(model_timeout_sec=600), backend.inherited_component_caps(), install(boundary):
            args = dict(allowed_root=Path(cfg['output']) / 'generation', source_fusion=fusion['final'],
                effective_fusion=effective['final'], task=job['gate_task'])
            boundary.verify_gate_producer_history(effective['fusion_acceptance_audit'], **args)
            tampered = copy.deepcopy(effective['fusion_acceptance_audit'])
            tampered['history'][0]['producer']['final_sha256'] = '0' * 64
            try: boundary.verify_gate_producer_history(tampered, **args)
            except ValueError: pass
            else: raise AssertionError('Tampered producer accepted')
        checks += ['saved producer prompts seed BF and hashes replay', 'tampered producer rejected']
        with tempfile.TemporaryDirectory(prefix='p4_recovery_tests_') as tmp:
            root = Path(tmp); control = root / 'control'; control.mkdir()
            local = Path(__file__).resolve().parent
            shutil.copyfile(local / 'controller.py', control / 'controller.py')
            testcfg = {**cfg, 'output': str(root)}
            write(control / 'config.json', testcfg)
            controller = load('offline_recovery_controller', control / 'controller.py')
            helper, engine = controller.scoring_engine()
            controller.scoring_engine = lambda: (helper, engine)
            original = read(Path(cfg['source']) / 'reports/REPORT.json')
            portfolio = [{**r, 'proof_path': r['published_proof']} for r in original['lanes']]
            write(root / 'generation/portfolio.json', portfolio)
            with patch.object(engine, 'run_one', side_effect=AssertionError('Unchanged proof regraded')):
                controller.grade(); controller.grade()
            assert read(root / 'grading/completed.json')['new_submissions'] == 0
            checks.append('all unchanged grades reused without inference on repeated runs')
            # Separate new experiment exercises changed-proof dedup and two-pass resume.
            newroot = root / 'changed'; controller.OUT = newroot
            data = 'Offline synthetic replacement proof, not a mathematical submission.\n'
            proof = newroot / 'proofs/replacement.md'; proof.parent.mkdir(parents=True); proof.write_text(data)
            portfolio[-1] = {**portfolio[-1], 'proof_path': str(proof), 'proof_sha256': textsha(data)}
            write(newroot / 'generation/portfolio.json', portfolio)
            calls = []
            grade = original['lanes'][0]['grades'][0]['grade']
            def fake(task, folder, *args):
                calls.append(task['candidate_id']); dest = folder / 'p4' / task['candidate_id']
                write(dest / 'summary.json', {'state': 'completed', 'grader': helper.MODEL, 'reasoning_effort': 'xhigh',
                    'policy_sha256': helper.POLICY, 'policy_mode': 'strict', 'candidate_id': task['candidate_id'], 'grade': grade,
                    **{k: task[k] for k in ('problem_sha256', 'reference_sha256', 'proof_sha256')}})
                write(dest / 'isolation_audit.json', {'tool_calls': 0})
                (dest / 'codex.jsonl').write_text(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': json.dumps(grade)}}) + '\n')
            with patch.object(engine, 'run_one', side_effect=fake):
                controller.grade(); controller.grade()
            assert len(calls) == 2 and len(set(calls)) == 1
            checks += ['one changed proof produces exactly two independent grades', 'rerunning skips both completed grades']
            manifest = read(newroot / 'grading/input_manifest.json')
            assert len(manifest['tasks']) == 1 and manifest['tasks'][0]['candidate_id'].startswith('proof_')
            checks.append('grader manifest blinds lane, stage, and condition')
    write(Path(cfg['output']) / 'control/offline_test_result.json', {'state': 'passed', 'model_calls': 0, 'checks': checks})
    print('PASS:', len(checks), 'offline recovery checks; zero model calls')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--config', required=True, type=Path)
    main(read(parser.parse_args().config))
