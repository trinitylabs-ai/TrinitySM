"""A real controller/worker process tree; synthetic disk artifacts, no models."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('interruption_pipeline', ROOT / 'harnesses/proof_workshop/pipeline.py')
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)
output = Path(sys.argv[1])
finalization = '--finalization' in sys.argv

if '--final-worker' in sys.argv:
    pipeline.write(output / 'ready.json', {'worker': os.getpid()})
    time.sleep(60)
elif '--worker' in sys.argv:
    candidate = pipeline.CANDIDATES[0]
    directory = output / f'problems/synthetic/01_source/p1/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p1/candidates/{candidate}'
    directory.mkdir(parents=True)
    proof = directory / 'draft_proof.md'
    proof.write_text('A completed synthetic draft.\n')
    pipeline.write(directory / 'cold_result.json', {
        'problem_id': 'synthetic', 'candidate_id': candidate,
        'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)})
    pipeline.write(output / 'manifest.json', {'problems': [{'problem_id': 'synthetic'}]})
    # This incomplete lazy output has no completion record and must be ignored.
    (directory / 'checked_proof.md').write_text('Incomplete lazy output')
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    pipeline.write(output / 'ready.json', {'worker': os.getpid(), 'descendant': child.pid})
    time.sleep(60)
else:
    original = pipeline.run_process

    def synthetic_core(command, **kwargs):
        if finalization:
            source = output / 'problems/synthetic/02_r1_cycles'
            candidate = pipeline.CANDIDATES[0]
            pipeline.write(source / 'manifest.json', {'problem_id': 'synthetic', 'candidate_ids': [candidate]})
            proof = source / 'completed.md'
            proof.write_text('A completed second refinement.\n')
            pipeline.write(source / 'score_targets.json', {'checkpoints': [{'checkpoint': 'R1-C2',
                'proofs': [{'candidate_id': candidate, 'proof_path': str(proof), 'proof_sha256': pipeline.proof_hash(proof)}]}]})
            return 0
        assert not kwargs.get('check'), 'Interrupted runs must not start a final refinement'
        return original([sys.executable, '-B', __file__, str(output), '--worker'], **kwargs)

    if finalization:
        def finish(*args):
            original([sys.executable, '-B', __file__, str(output), '--final-worker'], check=True)
            raise AssertionError('Signal should terminate the final refinement worker')
        pipeline.finish_lane = finish
    pipeline.run_process = synthetic_core
    raise SystemExit(pipeline.main(['--problem-dir', str(output.parent), '--output-dir', str(output), '--execute-models']))
