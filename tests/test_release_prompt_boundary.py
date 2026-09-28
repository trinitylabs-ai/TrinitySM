"""Exercise the bundled generation prompt builders with external grading blocked."""
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('release', ['1.7.0', '1.8.0', '1.9.0', '1.10.0', '1.11.0', '1.12.0'])
def test_bundled_prompt_builders_exclude_external_grading_material(release):
    engine = ROOT / 'harnesses/imo_proof_pipeline/releases' / release / 'engine/source'
    # A fresh interpreter prevents an already-imported research checkout from
    # hiding a dependency on an evaluator or on an external grading file.
    program = r'''
import builtins, hashlib, importlib.abc, io, json, sys
from pathlib import Path
root = Path(sys.argv[1])
policies = [root / 'docs/public_release/grading' / name for name in
            ('strict_olympiad_policy.txt', 'imobench_b5_prompt.txt')]
texts = [p.read_text() for p in policies]
digests = [hashlib.sha256(p.read_bytes()).hexdigest() for p in policies]
blocked = 'scripts.run_v097_p145_gold_informed_calibrated_codex_scores_20260827'
class NoScorer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == blocked:
            raise AssertionError('generation imported external scorer')
sys.meta_path.insert(0, NoScorer())
def guarded(original):
    def opened(path, *a, **kw):
        if isinstance(path, (str, bytes, Path)):
            candidate = Path(path).resolve()
            assert candidate not in policies, 'generation read an external policy'
            assert 'docs/public_release/grading' not in str(candidate)
        return original(path, *a, **kw)
    return opened
builtins.open = guarded(builtins.open)
io.open = guarded(io.open)
from cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 import pipeline as p
assert blocked not in sys.modules
reviews = {role: {'final': role + ': synthetic review.', 'enhancement': None,
                  'result_path': role + '.json', 'result_sha256': 'c'*64,
                  'identity': {'proof_sha256': 'b'*64}, 'outcome': 'NO_DEFECT',
                  'final_sha256': 'd'*64}
           for role in ('reviewer_1', 'reviewer_2', 'reviewer_3')}
case = dict(proof_index=0, problem_number=1, problem_id='synthetic', candidate_id='lane',
            problem_path='problem.json', proof_path='proof.md', problem='If x=0, prove x*x=0.',
            proof='Multiply x=0 by x.', problem_sha256='a'*64, proof_sha256='b'*64,
            case_id='synthetic.lane', reviews=reviews)
# Even if an upstream caller adds these fields, the real task builder uses
# an allowlist; evaluation metadata must not become a model prompt.
case.update(grading_rubric=texts[0], grading_guidelines=texts[1], external_score=7,
            gold_reference='SYNTHETIC_FORBIDDEN_REFERENCE')
task = p.stage.build_fusion_task(case, endpoint='http://127.0.0.1:8030/v1', gpu=0,
                                 seed_namespace='synthetic')
prompts = [p.stage.fusion.SYSTEM_PROMPT, p.stage.resolver.SYSTEM_PROMPT,
           p.stage.fusion.fusion_user_prompt(**{k: task[k] for k in
             ('problem', 'proof', 'reviewer_1', 'reviewer_2', 'reviewer_3')}),
           p.stage.resolver.resolver_user_prompt(problem=task['problem'], proof=task['proof'],
                                                 fusion_record='Synthetic repair advice.')]
for prompt in [*prompts, json.dumps(task)]:
    for value in [*texts, *digests, 'SYNTHETIC_FORBIDDEN_REFERENCE', '{complete grading rubric}', 'FINAL_GRADE:']:
        assert value not in prompt, 'external grading material entered generation'
assert 'grading_rubric' not in task and 'external_score' not in task
assert Path(p.stage.fusion.__file__).resolve().is_relative_to(Path.cwd())
print('Bundled fusion/resolver boundary passed')
'''
    result = subprocess.run([sys.executable, '-B', '-c', program, str(ROOT)],
                            cwd=engine, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
