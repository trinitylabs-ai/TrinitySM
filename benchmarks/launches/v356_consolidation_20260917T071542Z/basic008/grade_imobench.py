"""Publish and independently grade completed IMOBench tool trials."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SKILL = Path('/home/user/.codex/skills/imobench-scoring')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_digest(path):
    return hashlib.sha256(Path(path).read_text().strip().encode()).hexdigest()


def publish_and_grade(row, config):
    run = Path(row['experiment'])
    native = run / 'generation/run'
    completion = read(run / 'generation/completion.json')
    assert completion['worker_exited']
    result_path = native / 'result.json'
    result = read(result_path) if result_path.exists() else {}
    identity = read(native / 'manifest.json')
    for name, sha in identity['input_artifacts'].items():
        assert digest(native / name) == sha, 'Changed solver input'
    assert digest(native / 'input/source_proof.md') == row['proof_file_sha256']
    assert identity['gold_inputs'] is False and identity['generation_reference_reads'] is False
    manifest = {'schema': 'tool-harness-result-artifact-manifest-v1', 'run_id': row['run_id'],
                'harness_revision': identity['harness_revision'], 'proofs': [],
                'reports': ['reports/run_summary.json', 'reports/run_summary.md']}

    def snapshot(source, checkpoint):
        target = run / 'proofs' / row['problem_id'] / row['source_candidate_id'] / (checkpoint + '.md')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        record = {'problem_id': row['problem_id'], 'candidate_id': row['source_candidate_id'],
                  'checkpoint': checkpoint, 'path': str(target.relative_to(run)), 'source': str(source),
                  'sha256': digest(target), 'canonical_text_sha256': text_digest(target)}
        manifest['proofs'].append(record)
        return target, record

    snapshot(native / 'input/source_proof.md', row['source_checkpoint'])
    summary = {'run_id': row['run_id'], 'problem_id': row['problem_id'],
               'outcome': result.get('outcome'), 'returncode': completion['returncode'],
               'wall_seconds': completion['wall_seconds'],
               'proof_audit_passed': result.get('proof_audit_passed', False),
               'verified_samples': sum(bool(s.get('exact_verified') or any(c.get('exact_verified') for c in s.get('cycles', [])))
                                       for s in result.get('samples', [])),
               'grading_status': 'no_accepted_rewrite', 'external_grade': None}
    write(run / 'manifest.json', manifest)
    write(run / 'reports/run_summary.json', summary)
    if result.get('proof_audit_passed') is True:
        proof, record = snapshot(native / 'rewritten_proof.md', 'tool_rewrite')
        assert record['canonical_text_sha256'] == result['rewritten_proof_sha256']
        grade_root = run / 'grading'
        work = grade_root / 'work' / 'imobench_tool_rewrite'
        work.mkdir(parents=True, exist_ok=False)
        tasks = work / 'tasks.json'
        problem = read(Path(config['workspace']) / 'benchmarks' / row['benchmark'] / 'problems' / (row['problem_id'] + '.json'))
        write(tasks, {'tasks': [{'problem_id': row['problem_id'], 'candidate_id': row['source_candidate_id'],
                                'proof_path': str(proof), 'expected_hashes': {
                                    'proof_sha256': record['canonical_text_sha256'],
                                    'problem_sha256': hashlib.sha256(problem['problem'].strip().encode()).hexdigest()}}]})
        settings = grade_root / 'imobench_config'
        settings.mkdir()
        for source in (SKILL / 'SKILL.md', SKILL / 'scripts/score.py', SKILL / 'references/source.json',
                       SKILL / 'references/proof_autograder_prompt.txt', SKILL / 'references/evaluator_instructions.txt'):
            shutil.copyfile(source, settings / source.name)
        command = [sys.executable, '-u', '-B', str(SKILL / 'scripts/score.py'), '--task-manifest', str(tasks),
                   '--output-dir', str(work / 'scores'), '--workers', '1', '--model', 'gpt-5.6-sol', '--reasoning-effort', 'xhigh']
        env = os.environ.copy()
        for key in ('PYTHONPATH', 'PYTHONHOME', 'OPENAI_BASE_URL', 'OPENAI_API_BASE', 'GEMMA_ENDPOINT', 'QWEN_ENDPOINT'):
            env.pop(key, None)
        scratch = work / 'tmp'
        scratch.mkdir()
        env.update(CUDA_VISIBLE_DEVICES='', NVIDIA_VISIBLE_DEVICES='none', PYTHONNOUSERSITE='1',
                   PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(scratch))
        write(grade_root / 'launch.json', {'command': command, 'started_at': now(),
              'policy': 'imobench-proof-autograder-b5-v1', 'proof_sha256': record['sha256']})
        summary['grading_status'] = 'running'
        write(run / 'reports/run_summary.json', summary)
        with (grade_root / 'console.log').open('w') as log:
            process = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
        write(grade_root / 'completion.json', {'returncode': process.returncode, 'completed_at': now()})
        case = work / 'scores/cases' / row['problem_id'] / row['source_candidate_id']
        grade = read(case / 'result.json')
        assert process.returncode == 0 and grade['state'] == 'completed', 'IMOBench grading failed'
        assert grade['isolation_verified'] and read(case / 'isolation_audit.json')['tool_calls'] == 0
        assert grade['proof_sha256'] == record['canonical_text_sha256'] == text_digest(proof)
        assert digest(proof) == record['sha256']
        destination = run / 'grades' / row['problem_id'] / row['source_candidate_id'] / 'tool_rewrite'
        destination.mkdir(parents=True)
        for name in ('result.json', 'grade.md', 'manifest.json', 'isolation_audit.json'):
            shutil.copyfile(case / name, destination / name)
        summary.update(grading_status='completed', external_grade=grade['grade'])
        record.update(grade_status='completed', grade_path=str((destination / 'result.json').relative_to(run)))
        write(run / 'reports/imobench_score.json', grade)
        shutil.copyfile(case / 'grade.md', run / 'reports/imobench_score.md')
        manifest['reports'].extend(['reports/imobench_score.json', 'reports/imobench_score.md'])
    write(run / 'manifest.json', manifest)
    write(run / 'reports/run_summary.json', summary)
    (run / 'reports/run_summary.md').write_text(
        f"# {row['problem_id']} — {identity['harness_revision']}\n\nOutcome: {summary['outcome']}. "
        f"Runtime: {summary['wall_seconds']/60:.2f} minutes.\n\n"
        f"Exact certificates: {summary['verified_samples']}. IMOBench grade: {summary['external_grade']}.\n")
    subprocess.run([sys.executable, '-B', str(Path(config['workspace']) / 'benchmarks/run_experiment.py'),
                    '--benchmark', row['benchmark'], '--run-id', row['run_id'], '--index-only'], check=True)
    return summary


def main():
    config = read(HERE/'config.json')
    with (HERE/'.grading.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        write(HERE/'grading_status.json', {'state':'waiting_for_generation_publication','updated_at':now()})
        while read(HERE/'status.json').get('state') not in {'completed','failed'}:
            time.sleep(10)
        results=[]
        for original in config['jobs']:
            row={**original,'source_candidate_id':original['candidate_id'],'source_checkpoint':original['checkpoint']}
            write(HERE/'grading_status.json', {'state':'grading','run_id':row['run_id'],'updated_at':now()})
            try:
                result=publish_and_grade(row,config)
                results.append(result)
            except Exception as error:
                results.append({'run_id':row['run_id'],'state':'grading_failed','error':str(error)})
        write(HERE/'grading_status.json', {'state':'completed','results':results,'updated_at':now()})

if __name__=='__main__':
    main()
