#!/usr/bin/env python3
"""Record experiment identity/environment, then invoke the unchanged pinned solver.

No scoring calls. Artifact identities are external sidecar records, preserving
the exact native solver and grader files.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time

from environment_capture import capture, render_markdown, sha, write

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ('imo2026', 'imo-proofbench/basic', 'imo-proofbench/advanced')


def now():
    return datetime.now(timezone.utc).isoformat()


def destination(benchmark, run_id):
    if benchmark not in BENCHMARKS or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', run_id):
        raise ValueError('Use a known benchmark and a simple unique run ID (letters, numbers, underscore, dot, hyphen)')
    base = ROOT / 'benchmarks' / benchmark / 'results'
    path = base / run_id
    if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
        raise ValueError('Experiment path must remain inside its benchmark results directory')
    return path


def index_artifacts(experiment, generation_finished=False):
    experiment = Path(experiment)
    identity = json.loads((experiment / 'experiment.json').read_text())
    run_id = identity['run_id']
    excluded = {'artifact_index.jsonl', 'artifact_index.jsonl.tmp', '.experiment.lock'}
    records = []
    for current, directories, files in os.walk(experiment, followlinks=False):
        current = Path(current)
        directories[:] = [d for d in sorted(directories) if d not in ('.venv', '__pycache__', 'scratch', '.git')
                          and not (current / d).is_symlink()
                          and (generation_finished or current / d != experiment / 'generation/run')
                          and current / d != experiment / 'grading/work']
        for name in sorted(files):
            path = current / name
            if path.is_symlink() or name in excluded or name.endswith('.lock'):
                continue
            rel = str(path.relative_to(experiment))
            category = ('score' if rel.startswith('grades/') else
                        'proof' if rel.startswith('proofs/') or name.endswith('_proof.md') else
                        'verification' if any(s in name for s in ('validation', 'audit', 'review', 'verify')) else
                        'timing' if name.endswith('metadata.json') or 'timing' in name or name == 'completion.json' else 'provenance')
            # Read one coherent byte snapshot. Skip files still changing during publication.
            before = path.stat()
            data = path.read_bytes()
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                continue
            record = {'run_id': run_id, 'artifact_id': hashlib.sha256((run_id + '\0' + rel).encode()).hexdigest(),
                      'path': rel, 'kind': category, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
            if path.suffix == '.json' and category == 'timing':
                try:
                    metadata = json.loads(data)
                    record['timing'] = {k: metadata[k] for k in ('started_at', 'completed_at', 'latency_seconds',
                                         'elapsed_seconds', 'usage', 'model', 'stage') if k in metadata}
                except (ValueError, TypeError):
                    pass
            records.append(record)
    temp = experiment / 'artifact_index.jsonl.tmp'
    temp.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    temp.replace(experiment / 'artifact_index.jsonl')
    return len(records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark', choices=BENCHMARKS, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--release', default='1.0.0')
    p.add_argument('--solver-python', default='/home/user/miniconda3/envs/math/bin/python')
    p.add_argument('--grader-python')
    p.add_argument('--container-image')
    p.add_argument('--container-digest')
    p.add_argument('--problem-id', action='append')
    p.add_argument('--limit', type=int)
    p.add_argument('--seed-namespace', default='v263-v290:problem-only')
    p.add_argument('--raw-seed-offset', type=int, default=0)
    p.add_argument('--model-timeout-sec', type=int, default=600)
    p.add_argument('--gemma-port', type=int, default=8030)
    p.add_argument('--qwen-port', type=int, default=8027)
    p.add_argument('--continue-r1-from', type=Path,
                   help='Saved native R1 root; run one additional cycle in a fresh experiment.')
    p.add_argument('--candidate-id', help='Single saved candidate to continue.')
    p.add_argument('--then-v326', '--then-tool-harness', dest='then_v326', action='store_true',
                   help='Submit the new terminal proof to the selected tool harness after continuation.')
    p.add_argument('--tool-harness-version', choices=('0.3.326', '0.3.327', '0.3.328', '0.3.329', '0.3.330', '0.3.331', '0.3.332', '0.3.333', '0.3.334', '0.3.335', '0.3.336', '0.3.337', '0.3.338', '0.3.339', '0.3.340', '0.3.341', '0.3.342', '0.3.343', '0.3.344', '0.3.345', '0.3.346', '0.3.347', '0.3.348', '0.3.349', '0.3.350', '0.3.351', '0.3.352', '0.3.353'), default='0.3.326')
    p.add_argument('--tool-acquisition-from',type=Path,
                   help='Reuse bound detection and matching with tool harness 0.3.329.')
    p.add_argument('--resume-discrete-from', type=Path, help='Replay a selected discrete certificate and retry synthesis with v353')
    p.add_argument('--tool-detection-from', type=Path,
                   help='Reuse bound detection and rerun matching with tool harness 0.3.329.')
    p.add_argument('--tool-proof-file', type=Path,
                   help='Run the selected tool harness on one saved proof, without generating another R1 cycle.')
    p.add_argument('--resume-geometry-audit-from', type=Path,
                   help='Resume a size-blocked final geometry audit with v331 compact JSON.')
    p.add_argument('--resume-geometry-rewrite-from', type=Path,
                   help='Retry a quote-blocked geometry synthesis with v332 using its saved certificate.')
    p.add_argument('--v326-master-seed', type=int, default=20260915)
    p.add_argument('--replay-certificate-from', type=Path,
                   help='Saved audited 04_tool directory; replay its Laurent certificate without model calls.')
    p.add_argument('--certificate-timeout-sec', type=int, default=600)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--execute-models', action='store_true')
    mode.add_argument('--execute-tools', action='store_true')
    mode.add_argument('--index-only', action='store_true')
    args = p.parse_args()
    output = destination(args.benchmark, args.run_id)
    if args.index_only:
        completion = output / 'generation/completion.json'
        finished = completion.exists() and json.loads(completion.read_text()).get('worker_exited') is True
        print(json.dumps({'run_id': args.run_id, 'indexed': index_artifacts(output, finished)}))
        return
    if not re.fullmatch(r'\d+\.\d+\.\d+', args.release):
        p.error('Specify an explicit semantic release version')
    if args.tool_proof_file:
        if (args.continue_r1_from or args.candidate_id or args.then_v326
                or args.replay_certificate_from or args.limit is not None
                or len(args.problem_id or []) != 1 or args.execute_tools):
            p.error('Saved-proof tool runs need one problem and --execute-models or --dry-run only')
        if not args.tool_proof_file.is_file():
            p.error('Saved proof file does not exist')
    if args.resume_discrete_from and (not args.tool_proof_file or args.tool_harness_version != '0.3.353'
            or args.tool_acquisition_from or args.tool_detection_from
            or args.resume_geometry_audit_from or args.resume_geometry_rewrite_from):
        p.error('--resume-discrete-from requires a v353 saved-proof run without other reuse flags')
    if args.tool_acquisition_from and (not args.tool_proof_file or args.tool_harness_version not in ('0.3.329', '0.3.330', '0.3.331', '0.3.332', '0.3.333', '0.3.334', '0.3.335', '0.3.336', '0.3.337', '0.3.338', '0.3.339', '0.3.340', '0.3.341', '0.3.342', '0.3.343', '0.3.344', '0.3.345', '0.3.346', '0.3.347', '0.3.348', '0.3.349', '0.3.350', '0.3.351', '0.3.352', '0.3.353')):
        p.error('--tool-acquisition-from requires a saved-proof run with tool harness 0.3.329–0.3.353')
    if args.tool_detection_from and (not args.tool_proof_file or args.tool_harness_version not in ('0.3.329', '0.3.330', '0.3.331', '0.3.332', '0.3.333', '0.3.334', '0.3.335', '0.3.336', '0.3.337', '0.3.338', '0.3.339', '0.3.340', '0.3.341', '0.3.342', '0.3.343', '0.3.344', '0.3.345', '0.3.346', '0.3.347', '0.3.348', '0.3.349', '0.3.350', '0.3.351', '0.3.352', '0.3.353')):
        p.error('--tool-detection-from requires a saved-proof run with tool harness 0.3.329–0.3.353')
    if args.tool_detection_from and args.tool_acquisition_from:
        p.error('Choose detection-only reuse or complete acquisition reuse')
    if args.resume_geometry_audit_from and (not args.tool_proof_file
            or args.tool_harness_version != '0.3.331'
            or args.tool_acquisition_from or args.tool_detection_from):
        p.error('--resume-geometry-audit-from requires a v331 saved-proof run without acquisition reuse flags')
    if args.resume_geometry_rewrite_from and (not args.tool_proof_file
            or args.tool_harness_version != '0.3.332' or args.resume_geometry_audit_from
            or args.tool_acquisition_from or args.tool_detection_from):
        p.error('--resume-geometry-rewrite-from requires a v332 saved-proof run without other reuse flags')
    if args.replay_certificate_from:
        if args.continue_r1_from or args.candidate_id or args.then_v326 or args.limit is not None:
            p.error('Certificate replay cannot be combined with proof generation or a problem limit')
        if len(args.problem_id or []) != 1 or args.execute_models:
            p.error('Certificate replay needs one --problem-id and --execute-tools or --dry-run')
        if not 0 < args.certificate_timeout_sec <= 3600:
            p.error('Certificate timeout must be between 1 and 3600 seconds')
    elif args.execute_tools:
        p.error('--execute-tools requires --replay-certificate-from')
    if args.continue_r1_from:
        if not args.candidate_id or len(args.problem_id or []) != 1 or args.limit is not None:
            p.error('Continuation requires one --problem-id and --candidate-id, without --limit')
    elif args.candidate_id or args.then_v326:
        p.error('--candidate-id and --then-v326 require --continue-r1-from')
    launcher = ROOT / 'harnesses/imo_proof_pipeline/run.py'
    subprocess.run([args.solver_python, '-B', str(launcher), '--release', args.release, '--verify'], check=True)
    output.mkdir(parents=True, exist_ok=False)
    for directory in ('generation', 'proofs', 'grades', 'grading', 'reports', 'environment'):
        (output / directory).mkdir()
    # An exclusive experiment-level lock is independent of the solver queue lock.
    with (output / '.experiment.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        identity = {'schema': 'imo-experiment-v1', 'run_id': args.run_id, 'benchmark': args.benchmark,
                    'created_at': now(), 'harness_release': args.release,
                    'launcher_sha256': sha(__file__), 'state': 'preparing',
                    'generation_output': 'generation/run', 'grading_output': 'grading/work'}
        write(output / 'experiment.json', identity)
        inputs = ROOT / 'benchmarks' / args.benchmark / 'problems'
        argv = [args.solver_python, '-u', '-B', str(launcher), '--release', args.release,
                '--problem-dir', str(inputs), '--output-dir', str(output / 'generation/run'),
                '--seed-namespace', args.seed_namespace, '--raw-seed-offset', str(args.raw_seed_offset),
                '--model-timeout-sec', str(args.model_timeout_sec),
                '--gemma-endpoint', f'http://127.0.0.1:{args.gemma_port}/v1',
                '--qwen-endpoint', f'http://127.0.0.1:{args.qwen_port}/v1',
                '--dry-run' if args.dry_run else '--execute-models']
        for pid in args.problem_id or []:
            argv += ['--problem-id', pid]
        if args.limit is not None:
            argv += ['--limit', str(args.limit)]
        if args.continue_r1_from:
            driver = ROOT / 'harnesses/imo_proof_pipeline/tools/continue_r1.py'
            argv[3] = str(driver)
            argv += ['--source-r1-root', str(args.continue_r1_from.resolve()),
                     '--candidate-id', args.candidate_id]
            if args.then_v326:
                argv += ['--then-tool-harness', '--tool-harness-version', args.tool_harness_version,
                         '--v326-master-seed', str(args.v326_master_seed)]
            identity['continuation'] = {'source_r1_root': str(args.continue_r1_from.resolve()),
                'candidate_id': args.candidate_id, 'driver_sha256': sha(driver),
                'then_v326': args.then_v326, 'v326_master_seed': args.v326_master_seed,
                'tool_harness_version': args.tool_harness_version}
            write(output / 'experiment.json', identity)
        if args.replay_certificate_from:
            driver = ROOT / 'harnesses/imo_proof_pipeline/tools/replay_certificate.py'
            argv = [args.solver_python, '-u', '-B', str(driver), '--release', args.release,
                    '--problem-dir', str(inputs), '--problem-id', args.problem_id[0],
                    '--source-tool-dir', str(args.replay_certificate_from.resolve()),
                    '--output-dir', str(output / 'generation/run'),
                    '--timeout', str(args.certificate_timeout_sec),
                    '--dry-run' if args.dry_run else '--execute-tools']
            identity['certificate_replay'] = {
                'source_tool_dir': str(args.replay_certificate_from.resolve()),
                'timeout_seconds': args.certificate_timeout_sec, 'model_calls': 0,
                'driver_sha256': sha(driver)}
            write(output / 'experiment.json', identity)
        if args.tool_proof_file:
            packages = {
                '0.3.326': 'cognitive_well_harness_v0_3_326_generic_matched_geometry_tools_20260914',
                '0.3.327': 'cognitive_well_harness_v0_3_327_laurent_first_checked_tools_20260915',
                '0.3.328': 'cognitive_well_harness_v0_3_328_checked_geometry_compiler_20260915',
                '0.3.329': 'cognitive_well_harness_v0_3_329_deterministic_guard_closure_20260915',
                '0.3.330': 'cognitive_well_harness_v0_3_330_checked_sum_of_squares_20260915',
                '0.3.331': 'cognitive_well_harness_v0_3_331_compact_geometry_report_20260916',
                '0.3.332': 'cognitive_well_harness_v0_3_332_deterministic_quote_binding_20260916',
                '0.3.333': 'cognitive_well_harness_v0_3_333_certificate_budget_300s_20260916',
                '0.3.334': 'cognitive_well_harness_v0_3_334_executable_matcher_menu_20260916',
                '0.3.335': 'cognitive_well_harness_v0_3_335_structural_geometry_syntax_20260916',
                '0.3.336': 'cognitive_well_harness_v0_3_336_checked_rational_premises_20260916',
                '0.3.337': 'cognitive_well_harness_v0_3_337_retained_descriptions_20260916',
                '0.3.338': 'cognitive_well_harness_v0_3_338_auxiliary_geometry_20260916',
                '0.3.339': 'cognitive_well_harness_v0_3_339_generic_source_syntax_20260916',
                '0.3.340': 'cognitive_well_harness_v0_3_340_premise_annotations_20260916',
                '0.3.341': 'cognitive_well_harness_v0_3_341_typed_rational_geometry_20260916',
                '0.3.342': 'cognitive_well_harness_v0_3_342_selected_lemma_scope_20260916',
                '0.3.343': 'cognitive_well_harness_v0_3_343_real_root_classification_20260916',
                '0.3.344': 'cognitive_well_harness_v0_3_344_root_syntax_normalization_20260916',
                '0.3.345': 'cognitive_well_harness_v0_3_345_typed_point_declarations_20260916',
                '0.3.346': 'cognitive_well_harness_v0_3_346_exact_polynomial_export_20260916',
                '0.3.347': 'cognitive_well_harness_v0_3_347_positive_multiple_domains_20260916',
                '0.3.348': 'cognitive_well_harness_v0_3_348_domain_feedback_20260916',
                '0.3.349': 'cognitive_well_harness_v0_3_349_checked_real_branches_20260916',
                '0.3.350': 'cognitive_well_harness_v0_3_350_discrete_certificates_20260917',
                '0.3.351': 'cognitive_well_harness_v0_3_351_discrete_capability_contracts_20260917',
                '0.3.352': 'cognitive_well_harness_v0_3_352_exact_total_inputs_20260917',
                '0.3.353': 'cognitive_well_harness_v0_3_353_discrete_synthesis_binding_20260917',
            }
            package = packages[args.tool_harness_version]
            release_path = ROOT / package / 'release.json'
            tool_release = json.loads(release_path.read_text())
            for name, digest in tool_release['files_sha256'].items():
                path = ROOT / package / name
                if not path.resolve().is_relative_to(ROOT / package) or sha(path) != digest:
                    raise ValueError('Tool harness release integrity failure: ' + name)
            argv = [args.solver_python, '-u', '-B', '-m', package + '.proof_harness',
                    '--problem-file', str(inputs / (args.problem_id[0] + '.json')),
                    '--proof-file', str(args.tool_proof_file.resolve()),
                    '--output-dir', str(output / 'generation/run'),
                    '--master-seed', str(args.v326_master_seed),
                    '--gemma-endpoint', f'http://127.0.0.1:{args.gemma_port}/v1',
                    '--qwen-endpoint', f'http://127.0.0.1:{args.qwen_port}/v1']
            if args.execute_models:
                argv.append('--execute-models')
            if args.tool_acquisition_from:
                argv += ['--acquisition-from',str(args.tool_acquisition_from.resolve())]
            if args.tool_detection_from:
                argv += ['--detection-from', str(args.tool_detection_from.resolve())]
            identity['tool_harness'] = {'version': args.tool_harness_version,
                'release_sha256': sha(release_path),
                'proof_file': str(args.tool_proof_file.resolve()),
                'proof_file_sha256': sha(args.tool_proof_file)}
            if args.tool_acquisition_from:
                identity['tool_harness']['acquisition_from']=str(args.tool_acquisition_from.resolve())
            if args.tool_detection_from:
                identity['tool_harness']['detection_from']=str(args.tool_detection_from.resolve())
            if args.resume_geometry_audit_from:
                driver = ROOT / 'benchmarks/resume_geometry_audit.py'
                argv = [args.solver_python, '-u', '-B', str(driver),
                        '--source-run', str(args.resume_geometry_audit_from.resolve()),
                        '--problem-file', str(inputs / (args.problem_id[0] + '.json')),
                        '--proof-file', str(args.tool_proof_file.resolve()),
                        '--output-dir', str(output / 'generation/run')]
                if args.execute_models:
                    argv.append('--execute-models')
                identity['audit_resume'] = {
                    'source_run': str(args.resume_geometry_audit_from.resolve()),
                    'driver_sha256': sha(driver), 'scope': 'saved_final_proof_audit_only',
                    'prompt_change': 'compact compiler report JSON'}
            if args.resume_geometry_rewrite_from:
                driver = ROOT / 'benchmarks/resume_geometry_rewrite.py'
                argv = [args.solver_python, '-u', '-B', str(driver),
                        '--source-run', str(args.resume_geometry_rewrite_from.resolve()),
                        '--problem-file', str(inputs / (args.problem_id[0] + '.json')),
                        '--proof-file', str(args.tool_proof_file.resolve()),
                        '--output-dir', str(output / 'generation/run')]
                if args.execute_models:
                    argv.append('--execute-models')
                identity['rewrite_resume'] = {
                    'source_run': str(args.resume_geometry_rewrite_from.resolve()),
                    'driver_sha256': sha(driver), 'scope': 'saved_certificate_rewrite_and_audits',
                    'prompt_changes': ['deterministic paired-dollar quote binding', 'compact compiler report JSON']}
            if args.resume_discrete_from:
                argv = [args.solver_python, '-u', '-B', '-m', package + '.discrete_resume',
                        '--source-run', str(args.resume_discrete_from.resolve()),
                        '--problem-file', str(inputs / (args.problem_id[0] + '.json')),
                        '--proof-file', str(args.tool_proof_file.resolve()),
                        '--output-dir', str(output / 'generation/run')]
                if args.execute_models:
                    argv.append('--execute-models')
                identity['discrete_resume'] = {'source_run': str(args.resume_discrete_from.resolve()),
                    'scope': 'originally_selected_certificate_replay_and_synthesis'}
            write(output / 'experiment.json', identity)
        write(output / 'generation/launch.json', {'run_id': args.run_id, 'argv': argv, 'cwd': str(ROOT)})
        (output / 'generation/launch.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\ncd ' +
                                                     shlex.quote(str(ROOT)) + '\nexec ' + shlex.join(argv) + '\n')
        try:
            env = capture(output / 'environment/start', args.run_id, 'before_generation', args.solver_python,
                          args.grader_python, args.release, args.execute_models, args.gemma_port, args.qwen_port,
                          args.container_image, args.container_digest)
        except Exception as e:
            identity.update(state='snapshot_failed', error=f'{type(e).__name__}: {e}')
            write(output / 'experiment.json', identity)
            raise
        (output / 'ENVIRONMENT.md').write_text(render_markdown(env, 'environment/start/'))
        identity.update(state='running', snapshot_sha256=sha(output / 'environment/start/environment.json'))
        write(output / 'experiment.json', identity)
        start = time.monotonic()
        started_at = now()
        child = None
        def forward(signum, _frame):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signum)
        previous = {s: signal.signal(s, forward) for s in (signal.SIGINT, signal.SIGTERM)}
        returncode = None
        try:
            with (output / 'generation/console.log').open('w') as log:
                child = subprocess.Popen(argv, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                returncode = child.wait()
        finally:
            for s, handler in previous.items():
                signal.signal(s, handler)
            exited = child is not None and child.poll() is not None
            write(output / 'generation/completion.json', {'run_id': args.run_id, 'started_at': started_at,
                  'completed_at': now(), 'wall_seconds': time.monotonic() - start, 'worker_exited': exited,
                  'returncode': returncode, 'excludes_environment_capture_and_grading': True})
            identity.update(state='completed' if returncode == 0 else 'failed_or_interrupted')
            write(output / 'experiment.json', identity)
            index_artifacts(output, generation_finished=exited)
        raise SystemExit(returncode)


if __name__ == '__main__':
    main()
