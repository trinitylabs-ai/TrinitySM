#!/usr/bin/env python3
"""Run the complete Workshop Pipeline, including its final review and revision."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time

_policy_spec = importlib.util.spec_from_file_location(
    'workshop_runtime_policy', Path(__file__).with_name('runtime_policy.py'))
runtime_policy = importlib.util.module_from_spec(_policy_spec)
_policy_spec.loader.exec_module(runtime_policy)
_selector_spec = importlib.util.spec_from_file_location(
    'workshop_selector_policy', Path(__file__).with_name('selector_policy.py'))
selector_policy = importlib.util.module_from_spec(_selector_spec)
_selector_spec.loader.exec_module(selector_policy)

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / 'harnesses/imo_proof_pipeline'
STAGES = ('draft', 'refinement_1', 'refinement_2', 'refinement_3')
CANDIDATES = ('t07_r01', 't07_r02', 't10_r01', 't10_r02')
SCHEDULING_POLICY = 'finish_each_problem_with_last_completed_proof'
DEFAULT_RELEASE = '1.12.0'
SUPPORTED_RELEASES = ('1.7.0', '1.8.0', '1.9.0', '1.10.0', '1.11.0', '1.12.0')
AUDITED_RELEASES = ('1.9.0', '1.10.0', '1.11.0', '1.12.0')
VOTER_RELEASES = ('1.11.0', '1.12.0')
_processes = None
RUN_OPTIONS = ('problem_dir', 'output_dir', 'problem_id', 'limit', 'gemma_endpoint',
               'qwen_endpoint', 'model_timeout_sec', 'seed_namespace', 'raw_seed_offset',
               'resume', 'skip_failed_problem', 'dry_run', 'execute_models')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proof_hash(path):
    return hashlib.sha256(path.read_text().strip().encode()).hexdigest()


def project_identity():
    path = ROOT / 'project.json'
    project = read(path)
    return {'project_name': project['name'], 'project_version': project['version'],
            'project_manifest_sha256': sha(path)}


def saved_release(run_root):
    """Resolve a saved identity, including older receipts with only its hash."""
    identity = read(run_root / 'harness_release.json')
    registry = read(IMPLEMENTATION / 'releases/index.json')['releases']
    matches = [version for version in SUPPORTED_RELEASES
               if registry[version] == identity['release_sha256']]
    if len(matches) != 1 or identity.get('version', matches[0]) != matches[0]:
        raise ValueError('Saved run does not belong to a supported, registered release')
    return matches[0]


def continuation_driver(release):
    if release not in SUPPORTED_RELEASES:
        raise ValueError('Unsupported implementation release')
    if release in AUDITED_RELEASES:
        return IMPLEMENTATION / 'releases' / release / 'engine/source/scripts/continue_r1_audited.py'
    return IMPLEMENTATION / 'tools' / ('continue_r1_b.py' if release == '1.8.0' else 'continue_r1.py')


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)


def write(path, value):
    atomic_write(path, (json.dumps(value, indent=2) + '\n').encode())


class Processes:
    """Stop child process groups before collecting their durable artifacts."""
    def __init__(self, lock_fd=None):
        self.children = set()
        self.lock = threading.RLock()
        self.signal = None
        self.stopped_at = None
        self.lock_fd = lock_fd

    @staticmethod
    def send(child, signum):
        try:
            os.killpg(child.pid, signum)
        except ProcessLookupError:
            pass

    def stop(self, signum, frame):
        if self.signal is None:
            self.signal = signum
            self.stopped_at = time.monotonic()
        with self.lock:
            for child in self.children:
                self.send(child, signum)

    def call(self, command, *, check=False, **kwargs):
        with self.lock:
            if self.signal:
                raise InterruptedError(f'Stopped by {signal.Signals(self.signal).name}')
            child = subprocess.Popen(command, start_new_session=True,
                                     pass_fds=() if self.lock_fd is None else (self.lock_fd,), **kwargs)
            self.children.add(child)
        try:
            while True:
                try:
                    code = child.wait(timeout=0.2)
                    break
                except subprocess.TimeoutExpired:
                    if self.signal:
                        self.send(child, signal.SIGKILL if time.monotonic() - self.stopped_at > 5
                                  else self.signal)
            if code or self.signal:
                # A terminated queue may have left a worker in the same group.
                self.send(child, signal.SIGKILL)
            if check and code:
                raise subprocess.CalledProcessError(code, command)
            return code
        finally:
            with self.lock:
                self.children.discard(child)


def run_process(command, *, check=False, **kwargs):
    if _processes is not None:
        return _processes.call(command, check=check, **kwargs)
    return subprocess.run(command, check=check, **kwargs).returncode


def finish_lane(run_root, source, candidate, problem_id, release, python):
    identity = read(run_root / 'harness_release.json')
    runtime = identity['parameters']
    output = run_root / 'finalization' / problem_id / candidate
    driver = continuation_driver(release)
    checkpoint = next(c for c in read(source / 'score_targets.json')['checkpoints']
                      if c['checkpoint'] == 'R1-C2')
    saved = next(p for p in checkpoint['proofs'] if p['candidate_id'] == candidate)
    if proof_hash(Path(saved['proof_path'])) != saved['proof_sha256']:
        raise ValueError('Source proof changed after its checkpoint was recorded')
    if output.exists():
        # Reuse only completed, bound finalization work; interrupted work remains
        # visible and is never overwritten or mislabeled as a finished proof.
        receipt = read(output / 'continuation.json')
        if (read(output / 'status.json')['state'] != 'completed'
                or receipt['source_manifest_sha256'] != sha(source / 'manifest.json')
                or receipt['release_sha256'] != identity['release_sha256']
                or receipt['driver_sha256'] != sha(driver)
                or receipt['problem_id'] != problem_id
                or receipt['candidate_id'] != candidate
                or receipt['source_proof'] != saved
                or receipt['runtime'] != read(source / 'manifest.json')['runtime']
                or receipt['target_checkpoint'] != 'R1-C3'):
            raise ValueError('Existing finalization does not match completed source-bound work')
        staged = receipt['input_proof']
        if (staged['proof_sha256'] != saved['proof_sha256']
                or proof_hash(Path(staged['proof_path'])) != saved['proof_sha256']):
            raise ValueError('Finalization input proof changed')
    else:
        command = [python, '-B', str(driver), '--release', release,
                   '--source-r1-root', str(source), '--problem-dir', runtime['problem_dir'],
                   '--problem-id', problem_id, '--candidate-id', candidate,
                   '--output-dir', str(output), '--execute-models']
        for option in ('seed_namespace', 'raw_seed_offset', 'model_timeout_sec', 'gemma_endpoint', 'qwen_endpoint'):
            command += ['--' + option.replace('_', '-'), str(runtime[option])]
        run_process(command, check=True, cwd=ROOT,
                    env=runtime_policy.environment(run_root, os.environ))
    terminal = read(output / 'terminal_proof.json')
    path = Path(terminal['proof_path']).resolve()
    if (terminal['candidate_id'] != candidate or not path.is_relative_to(output)
            or proof_hash(path) != terminal['proof_sha256']):
        raise ValueError('Final proof differs from its recorded producer')
    return terminal


def optional_record(path, issues):
    """One damaged receipt must not hide other completed lanes or checkpoints."""
    if not path.exists():
        return {}
    try:
        value = read(path)
        if not isinstance(value, dict):
            raise ValueError('Expected an object')
        return value
    except (OSError, ValueError) as error:
        issues.append({'artifact': str(path), 'reason': str(error)})
        return {}


def bound_proof(row, candidate, allowed_root):
    path = Path(row['proof_path']).resolve()
    if (row['candidate_id'] != candidate or not path.is_relative_to(allowed_root.resolve())
            or not path.read_text().strip() or proof_hash(path) != row['proof_sha256']):
        raise ValueError('Completed proof identity, path or hash mismatch')
    return dict(row, proof_path=str(path))


def replay_completed_stage(run_root, source, candidate, problem_id, cycle, stage):
    """Read-only producer validation when a worker died before its checkpoint write.

    Reuse the pinned engine's hash/parse/gate checks; never run a generation stage.
    Called serially because the legacy validator has per-problem module globals.
    """
    engine = IMPLEMENTATION / 'releases' / saved_release(run_root) / 'engine/source'
    spec = importlib.util.spec_from_file_location('workshop_recovery_queue', engine / 'scripts/run_v263_v290.py')
    queue = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(engine))
    try:
        with runtime_policy.validation(run_root):
            spec.loader.exec_module(queue)
            _, backend = queue.load_engines()
            if not Path(backend.__file__).resolve().is_relative_to(engine):
                raise ValueError('Recovery validator is outside the pinned engine')
            original = read(source / 'manifest.json')
            source_run = Path(original['source_run']).resolve()
            if source_run != (source.parent / '01_source').resolve() or original['problem_id'] != problem_id:
                raise ValueError('Recovery problem binding mismatch')
            backend.configure_source_problem(source_run, original['problem_number'], expected_problem_id=problem_id)
            allowed = source if cycle < 3 else run_root / 'finalization' / problem_id / candidate
            return backend._terminal_r1_proofs(stage_dir=stage, allowed_root=allowed,
                expected_candidates=(candidate,), model_timeout_sec=original['runtime']['model_timeout_sec'])[0]
    finally:
        sys.path.remove(str(engine))


def validate_finalization_source(run_root, source, candidate, problem_id):
    output = run_root / 'finalization' / problem_id / candidate
    receipt = read(output / 'continuation.json')
    identity = read(run_root / 'harness_release.json')
    original = read(source / 'manifest.json')
    saved = next(p for c in read(source / 'score_targets.json')['checkpoints']
                 if c['checkpoint'] == 'R1-C2' for p in c['proofs'] if p['candidate_id'] == candidate)
    bound_proof(saved, candidate, source)
    staged = bound_proof(receipt['input_proof'], candidate, output)
    if (receipt['source_manifest_sha256'] != sha(source / 'manifest.json')
            or receipt['release_sha256'] != identity['release_sha256']
            or receipt['driver_sha256'] != sha(continuation_driver(saved_release(run_root)))
            or receipt['problem_id'] != problem_id or receipt['candidate_id'] != candidate
            or receipt['source_proof'] != saved or receipt['runtime'] != original['runtime']
            or receipt['target_checkpoint'] != 'R1-C3'
            or staged['proof_sha256'] != saved['proof_sha256']):
        raise ValueError('Finalization source binding mismatch')


def audit_module(release):
    """Load only the release-bound stdlib audit code, including during collection."""
    import importlib
    directory = IMPLEMENTATION / 'releases' / release
    registry = read(directory.parent / 'index.json')['releases']
    if sha(directory / 'release.json') != registry[release]:
        raise ValueError('Registered audit release changed')
    manifest = read(directory / 'release.json')
    relative = 'engine/source/experiments/local_math_verifier/post_resolver_audit'
    for name, expected in manifest['files'].items():
        if name.startswith(relative + '/') and sha(directory / name) != expected:
            raise ValueError('Frozen audit implementation changed: ' + name)
    name = 'workshop_bound_audit_' + release.replace('.', '_')
    package = directory / relative
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, package / '__init__.py',
                                                     submodule_search_locations=[str(package)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(name + '.live')


def audit_problem(run_root, problem_id):
    """Bind normalized engine provenance to the original statement-only snapshot."""
    source = run_root / 'problems' / problem_id / '02_r1_cycles'
    statement_path = source / 'input/problem.json'
    original = read(source / 'manifest.json')
    if sha(statement_path) != original['frozen_inputs']['problem_file_sha256']:
        raise ValueError('Audit problem statement changed')
    normalized = read(statement_path)
    snapshot = run_root / 'inputs' / (problem_id + '.json')
    statement = read(snapshot)
    if (set(statement) not in ({'problem_id', 'claim'}, {'problem_id', 'problem'})
            or statement['problem_id'] != problem_id or normalized['problem_id'] != problem_id
            or normalized['claim'] != statement.get('claim', statement.get('problem'))
            or normalized['source_sha256'] != sha(snapshot)):
        raise ValueError('Expected a bound statement-only audit input')
    return statement.get('claim', statement.get('problem'))


def run_post_resolver_audit(run_root, problem_id, release, python=sys.executable):
    """Audit all completed R2/R3 lane pairs under the selected release's audit concurrency limits."""
    module = audit_module(release)
    identity = read(run_root / 'harness_release.json')
    runtime = identity['parameters']
    claim = audit_problem(run_root, problem_id)
    directory = run_root / 'post_resolver_audit' / problem_id
    roots = []
    for candidate in CANDIDATES:
        issues = []
        proposed = _collect_lane(run_root, problem_id, candidate, issues)
        baseline = _collect_lane(run_root, problem_id, candidate, issues, max_cycle=2)
        if not proposed or proposed['selected_stage'] != 'refinement_3':
            continue
        if not baseline or baseline['selected_stage'] != 'refinement_2':
            raise ValueError('Completed R3 is missing its bound R2 baseline')
        root = directory / candidate
        module.prepare(root, {'problem_id': problem_id, 'candidate_id': candidate,
            'problem': claim,
            'baseline_path': baseline['proof_path'], 'baseline_proof_sha256': baseline['proof_sha256'],
            'candidate_path': proposed['proof_path'], 'candidate_proof_sha256': proposed['proof_sha256']},
            runtime, identity['release_sha256'])
        roots.append(str(root))
    if not roots:
        return
    job = {'policy_id': module.POLICY_ID, 'problem_id': problem_id, 'lane_roots': roots,
           'release_sha256': identity['release_sha256']}
    jobs = sorted(directory.glob('job_*.json'))
    job_path = next((path for path in jobs if read(path) == job), directory / f'job_{len(jobs):03d}.json')
    module.exact(job_path, module.encoded(job))
    engine = IMPLEMENTATION / 'releases' / release / 'engine/source'
    environment = dict(os.environ)
    environment.pop('PYTHONHOME', None)
    environment.update(PYTHONPATH=str(engine), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    with (directory / 'worker.log').open('a') as log:
        run_process([python, '-u', '-B', '-m', 'experiments.local_math_verifier.post_resolver_audit.live',
                     '--job', str(job_path)], check=True, cwd=engine, env=environment,
                    stdout=log, stderr=subprocess.STDOUT)


def voter_module(release):
    """Verify and load the release's voter and its binding dependencies."""
    import importlib
    import types
    directory = IMPLEMENTATION / 'releases' / release
    registry = read(directory.parent / 'index.json')['releases']
    if release not in VOTER_RELEASES or sha(directory / 'release.json') != registry[release]:
        raise ValueError('Unregistered voter release')
    manifest = read(directory / 'release.json')
    relative = 'engine/source/experiments/local_math_verifier'
    for name, expected in manifest['files'].items():
        if any(name.startswith(relative + '/' + part + '/') for part in ('post_resolver_audit', 'cross_lane_voter')):
            if sha(directory / name) != expected:
                raise ValueError('Frozen voter or binding code changed: ' + name)
    name = 'workshop_bound_voter_' + release.replace('.', '_')
    if name not in sys.modules:
        package = types.ModuleType(name)
        package.__path__ = [str(directory / relative)]
        sys.modules[name] = package
    module = importlib.import_module(name + '.cross_lane_voter.live')
    if release == '1.12.0' and not getattr(module.parse, 'explicit_winner_prefix', False):
        # Reparse saved output after the frozen worker finishes. Keep frozen
        # inference, transport bindings and release hashes unchanged.
        path = ROOT / 'harnesses/cross_lane_voter/mechanical_recovery.py'
        spec = importlib.util.spec_from_file_location('workshop_voter_format_recovery', path)
        recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recovery)
        module.parse = recovery.with_explicit_winner_prefix(module.parse)
    return module


def voter_problem(run_root, problem_id):
    if (run_root / 'problems' / problem_id / '02_r1_cycles/manifest.json').is_file():
        return audit_problem(run_root, problem_id)
    # Early-stage fallback may precede the refinement manifest. Bind to the
    # original statement-only snapshot and the frozen queue's statement.
    statement = read(run_root / 'inputs' / (problem_id + '.json'))
    rows = [r for r in read(run_root / 'manifest.json')['problems'] if r['problem_id'] == problem_id]
    if (len(rows) != 1 or set(statement) not in ({'problem_id', 'problem'}, {'problem_id', 'claim'})
            or statement['problem_id'] != problem_id):
        raise ValueError('Unbound fallback problem statement')
    claim = statement.get('claim', statement.get('problem'))
    if claim != rows[0].get('claim', rows[0].get('problem')):
        raise ValueError('Fallback statement differs from frozen queue')
    return claim


def cross_lane_selection(run_root, problem_id, release, python=sys.executable, *, execute=False):
    module = selector_policy.module(run_root) or voter_module(release)
    identity = read(run_root / 'harness_release.json')
    candidates = []
    for cid in CANDIDATES:
        selected = collect_lane(run_root, problem_id, cid, [])
        if selected:
            candidates.append(selected)
    if not candidates:
        return {'problem_id': problem_id, 'state': 'unavailable', 'reason': 'No completed lane proofs'}
    problem = voter_problem(run_root, problem_id)
    expected = {'problem_id': problem_id, 'problem': problem, 'candidates': candidates,
                'runtime': identity['parameters'], 'release_sha256': identity['release_sha256']}
    material = {'problem_id': problem_id, 'problem': problem,
                'candidates': [{k: c[k] for k in ('candidate_id', 'selected_stage', 'proof_sha256')} for c in candidates],
                'file_hashes': [sha(Path(c['proof_path'])) for c in candidates],
                'release_sha256': identity['release_sha256'], 'runtime': identity['parameters']}
    if identity.get('final_selector'):
        material['final_selector'] = identity['final_selector']
    key = hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()
    directory = run_root / 'cross_lane_voter' / problem_id / key
    if execute:
        module.prepare(directory, problem_id, problem, candidates, identity['parameters'], identity['release_sha256'])
        engine = IMPLEMENTATION / 'releases' / release / 'engine/source'
        environment = dict(os.environ)
        environment.pop('PYTHONHOME', None)
        environment.update(PYTHONPATH=str(engine), PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
        environment = runtime_policy.environment(run_root, environment)
        command = ([python, '-u', '-B', str(run_root / 'selector_runtime/selector.py'),
                    '--run-root', str(run_root), '--root', str(directory)] if identity.get('final_selector') else
                   [python, '-u', '-B', '-m', 'experiments.local_math_verifier.cross_lane_voter.live',
                    '--root', str(directory)])
        with (directory / 'worker.log').open('a') as log:
            code = run_process(command, cwd=engine, env=environment, stdout=log, stderr=subprocess.STDOUT)
        if code in (-2, -15, 130, 143):
            raise subprocess.CalledProcessError(code, 'cross_lane_voter')
    with runtime_policy.validation(run_root):
        selection = module.collect(directory, expected=expected)
    if (directory / 'status.json').exists():
        status = read(directory / 'status.json')
        selection['observed_runtime'] = {k: status.get(k) for k in (
            'workers_total', 'workers_per_model', 'max_concurrency_observed', 'max_concurrency_per_model', 'elapsed_seconds')}
    selection['artifact_directory'] = str(directory.relative_to(run_root))
    if selection['state'] == 'completed':
        winner = selection['summaries']['combined']['winner']
        source = next(c for c in candidates if c['candidate_id'] == winner)
        # Immutable, portfolio-specific winner prevents stale exports on resume.
        destination = directory / 'selected_proof.md'
        module.exact(destination, Path(source['proof_path']).read_bytes())
        selection.update(selected_candidate=winner, selected_stage=source['selected_stage'],
                         proof=str(destination.relative_to(run_root)), sha256=sha(destination))
    module.report(directory, selection)
    return selection


def collect_lane(run_root, problem_id, candidate, issues, finished=None):
    selected = _collect_lane(run_root, problem_id, candidate, issues, finished)
    if (not selected or selected['selected_stage'] != 'refinement_3'
            or not (run_root / 'harness_release.json').is_file() or saved_release(run_root) not in AUDITED_RELEASES):
        return selected
    baseline = _collect_lane(run_root, problem_id, candidate, issues, max_cycle=2)
    if not baseline or baseline['selected_stage'] != 'refinement_2':
        raise ValueError('Audited R3 requires a completed R2 baseline')
    directory = run_root / 'post_resolver_audit' / problem_id / candidate
    try:
        identity = read(run_root / 'harness_release.json')
        result = audit_module(saved_release(run_root)).collect(directory,
            Path(baseline['proof_path']).read_bytes(), Path(selected['proof_path']).read_bytes(),
            identity['release_sha256'], runtime=identity['parameters'],
            expected_case={'problem_id': problem_id, 'candidate_id': candidate,
                           'problem': audit_problem(run_root, problem_id)})
    except Exception as error:
        result = {'decision': 'KEEP_BASELINE', 'state': 'missing_or_invalid_audit',
                  'reason': f'{type(error).__name__}: {error}'}
    metadata = {k: v for k, v in result.items() if k != 'votes'}
    metadata.update(artifact_directory=str(directory.relative_to(run_root)),
                    candidate_proof_sha256=selected['proof_sha256'],
                    baseline_proof_sha256=baseline['proof_sha256'])
    chosen = selected if result['decision'] == 'ACCEPT_CANDIDATE' else baseline
    return {**chosen, 'post_resolver_audit': metadata}


def _collect_lane(run_root, problem_id, candidate, issues, finished=None, max_cycle=3):
    """Select by completion order only. File existence alone is never sufficient."""
    problem = run_root / 'problems' / problem_id
    source = problem / '02_r1_cycles'
    targets = optional_record(source / 'score_targets.json', issues)
    final = run_root / 'finalization' / problem_id / candidate

    def accept(row, stage, receipt, allowed):
        if not allowed.resolve().is_relative_to(run_root.resolve()):
            raise ValueError('Proof directory escapes this run')
        proof = bound_proof(row, candidate, allowed)
        return dict(proof, selected_stage=stage, completion_record=str(receipt))

    for cycle in range(max_cycle, 0, -1):
        stage_name = f'refinement_{cycle}'
        allowed = final if cycle == 3 else source
        stage = allowed / 'lanes' / candidate / f'{cycle:02d}_r1_cycle_{cycle}'
        try:
            if cycle == 3:
                if finished:
                    return accept(finished, stage_name, final / 'terminal_proof.json', final)
                if not (final / 'continuation.json').is_file():
                    continue
                validate_finalization_source(run_root, source, candidate, problem_id)
                terminal = optional_record(final / 'terminal_proof.json', issues)
                if terminal:
                    return accept(terminal, stage_name, final / 'terminal_proof.json', final)
            else:
                rows = [p for c in targets.get('checkpoints', []) if c.get('checkpoint') == f'R1-C{cycle}'
                        for p in c.get('proofs', []) if p.get('candidate_id') == candidate]
                if len(rows) > 1:
                    raise ValueError('Duplicate completed checkpoint')
                if rows:
                    return accept(rows[0], stage_name, source / 'score_targets.json', source)
            if optional_record(stage / 'summary.json', issues).get('state') == 'completed':
                terminal = replay_completed_stage(run_root, source, candidate, problem_id, cycle, stage)
                return accept(terminal, stage_name, stage / 'summary.json', allowed)
        except Exception as error:
            issues.append({'stage': stage_name, 'reason': f'{type(error).__name__}: {error}'})

    # Both records are written only after their full proof file is complete.
    directories = sorted(problem.glob(f'01_source/p*/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p*/candidates/{candidate}'))
    for stage, filename, prefix, proof_name in (
            ('lazy_checked', 'result.json', 'checked_proof', 'checked_proof.md'),
            ('raw', 'cold_result.json', 'proof', 'draft_proof.md')):
        for directory in directories:
            receipt = directory / filename
            row = optional_record(receipt, issues)
            if not row:
                continue
            try:
                if row.get('problem_id', problem_id) != problem_id:
                    raise ValueError('Frontend problem identity mismatch')
                proof = {'candidate_id': row['candidate_id'], 'proof_path': row[prefix + '_path'],
                         'proof_sha256': row[prefix + '_sha256']}
                if Path(proof['proof_path']).resolve() != (directory / proof_name).resolve():
                    raise ValueError('Frontend proof path mismatch')
                return accept(proof, stage, receipt, directory)
            except (OSError, ValueError, KeyError, TypeError) as error:
                issues.append({'stage': stage, 'reason': f'{type(error).__name__}: {error}'})
    return None


def lane_interruption(run_root, problem_id, candidate, selected_stage, execution, error, issues):
    problem = run_root / 'problems' / problem_id
    final = run_root / 'finalization' / problem_id / candidate
    next_stage = {None: 'raw', 'raw': 'lazy_checked', 'lazy_checked': 'refinement_1',
                  'refinement_1': 'refinement_2', 'refinement_2': 'refinement_3', 'refinement_3': 'finished'}
    paths = [final / 'failure.json', problem / '02_r1_cycles/lanes' / candidate / 'failure.json']
    paths += sorted(problem.glob(f'01_source/p*/01_raw_lazy_enhanced_resolve/phase_1_raw_lazy/p*/candidates/{candidate}/frontend_failure.json'))
    paths += [final / 'status.json', problem / '02_r1_cycles/status.json', problem / 'status.json']
    for path in paths:
        record = optional_record(path, issues)
        if record.get('error') or record.get('state') in ('running', 'failed', 'failed_closed'):
            native_stage = record.get('stage')
            stage = {'R1-C1': 'refinement_1', 'R1-C2': 'refinement_2', 'R1-C3': 'refinement_3'}.get(native_stage, native_stage)
            if not stage:
                stage = 'refinement_3' if path.is_relative_to(final) else None
            return {'stage': stage or next_stage[selected_stage], 'stage_inferred': not bool(stage),
                    'reason': record.get('error') or error or execution.get('reason') or 'Stage did not finish',
                    'record': str(path.relative_to(run_root))}
    return {'stage': next_stage[selected_stage], 'stage_inferred': True,
            'reason': error or execution.get('reason') or 'No completed next-stage receipt'}


def advance_export(run_root, destination, selected, problem_id, candidate):
    """Archive a receipt-bound earlier export before publishing a resumed stage."""
    receipt_path = run_root / 'final_results.json'
    receipt = read(receipt_path)
    prior = next((row for row in receipt.get('lanes', [])
                  if row.get('problem_id') == problem_id and row.get('candidate_id') == candidate), {})
    stages = ('raw', 'lazy_checked', *STAGES[1:])
    if (not prior.get('proof_available')
            or prior.get('proof') != str(destination.relative_to(run_root))
            or prior.get('sha256') != sha(destination)
            or prior.get('selected_stage') not in stages
            or stages.index(prior['selected_stage']) >= stages.index(selected['selected_stage'])):
        raise ValueError('Refusing to replace an unbound or non-earlier published proof')
    history = run_root / 'proof_history'
    for path, data in (
        (history / problem_id / candidate / (prior['sha256'] + '.md'), destination.read_bytes()),
        (history / ('final_results.' + sha(receipt_path) + '.json'), receipt_path.read_bytes()),
    ):
        if not path.resolve().is_relative_to(run_root):
            raise ValueError('Proof history escapes this run')
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Archived proof or receipt changed')
        atomic_write(path, data)


def finalize(run_root, release, python=sys.executable, *, execute=True, execution=None,
             allow_export_advance=False):
    if release not in SUPPORTED_RELEASES:
        raise ValueError('Unsupported implementation release')
    run_root = run_root.resolve()
    if (run_root / 'harness_release.json').exists() and saved_release(run_root) != release:
        raise ValueError('Collection cannot change the saved implementation release')
    execution = dict(execution or {'state': 'completed', 'returncode': 0})
    discovery_issues = []
    queue = optional_record(run_root / 'manifest.json', discovery_issues)
    problem_ids = {row['problem_id'] for row in queue.get('problems', [])}
    problem_ids.update(p.name for p in (run_root / 'problems').glob('*') if p.is_dir())
    jobs, lanes = [], []
    for problem_id in sorted(problem_ids):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', problem_id):
            discovery_issues.append({'reason': 'Unsafe problem ID excluded'})
            continue
        source = run_root / 'problems' / problem_id / '02_r1_cycles'
        manifest = optional_record(source / 'manifest.json', discovery_issues)
        candidates = manifest.get('candidate_ids', CANDIDATES)
        targets = optional_record(source / 'score_targets.json', discovery_issues)
        available = {p.get('candidate_id') for c in targets.get('checkpoints', [])
                     if c.get('checkpoint') == 'R1-C2' for p in c.get('proofs', [])}
        for candidate in candidates:
            if not re.fullmatch(r'[A-Za-z0-9_-]+', candidate):
                discovery_issues.append({'reason': 'Unsafe candidate ID excluded'})
                continue
            job = (source, candidate, problem_id)
            lanes.append(job)
            if execute and candidate in available:
                jobs.append(job)

    def worker(job):
        source, candidate, problem_id = job
        try:
            return job, finish_lane(run_root, source, candidate, problem_id, release, python), None
        except Exception as error:
            return job, None, f'{type(error).__name__}: {error}'

    with ThreadPoolExecutor(max_workers=4) as pool:
        finished = {job: (terminal, error) for job, terminal, error in pool.map(worker, jobs)}
    audit_errors = {}
    if execute and release in AUDITED_RELEASES:
        for problem_id in sorted({pid for _, _, pid in lanes}):
            try:
                run_post_resolver_audit(run_root, problem_id, release, python)
            except Exception as error:
                for candidate in CANDIDATES:
                    audit_errors[f'{problem_id}/{candidate}'] = f'Audit failed: {error}; retain R2'
    lane_errors = dict(execution.get('lane_errors', {}))
    lane_errors.update(audit_errors)
    for (_, candidate, problem_id), (_, error) in finished.items():
        if error:
            lane_errors[f'{problem_id}/{candidate}'] = error
    if _processes is not None and _processes.signal:
        execution = {'state': 'interrupted', 'returncode': 128 + _processes.signal,
                     'signal': signal.Signals(_processes.signal).name,
                     'reason': f'Stopped by {signal.Signals(_processes.signal).name}'}
    execution['lane_errors'] = lane_errors
    write(run_root / 'pipeline_execution.json', execution)
    results = []
    for job in lanes:
        source, candidate, problem_id = job
        terminal, error = finished.get(job, (None, lane_errors.get(f'{problem_id}/{candidate}')))
        issues = []
        try:
            selected = collect_lane(run_root, problem_id, candidate, issues, terminal)
        except Exception as failure:
            selected = None
            error = f'{type(failure).__name__}: {failure}'
            issues.append({'stage': 'collection', 'reason': error})
        row = {'problem_id': problem_id, 'candidate_id': candidate, 'proof_available': False}
        if selected:
            destination = run_root / 'proofs' / problem_id / (candidate + '.md')
            try:
                data = Path(selected['proof_path']).read_bytes()
                if not destination.resolve().is_relative_to(run_root):
                    raise ValueError('Export path escapes this run')
                if destination.exists() and destination.read_bytes() != data:
                    if not allow_export_advance:
                        raise ValueError('Refusing to overwrite a different published proof')
                    advance_export(run_root, destination, selected, problem_id, candidate)
                atomic_write(destination, data)
            except (OSError, ValueError) as failure:
                error = str(failure)
                issues.append({'stage': 'export', 'reason': error})
            else:
                row.update(proof_available=True, proof=str(destination.relative_to(run_root)),
                           sha256=sha(destination), proof_sha256=selected['proof_sha256'],
                           producer=str(Path(selected['proof_path']).relative_to(run_root)),
                           selected_stage=selected['selected_stage'],
                           completion_record=str(Path(selected['completion_record']).relative_to(run_root)))
        if selected and 'post_resolver_audit' in selected:
            row['post_resolver_audit'] = selected['post_resolver_audit']
            if selected['post_resolver_audit']['decision'] != 'ACCEPT_CANDIDATE':
                row['fallback_reason'] = 'post_resolver_audit_retained_R2'
        fully_refined = row['proof_available'] and row['selected_stage'] == 'refinement_3'
        row['fully_refined'] = fully_refined
        row['fallback_used'] = row['proof_available'] and not fully_refined
        complete = fully_refined
        row['state'] = ('completed' if complete else
                        'completed_with_fallback' if row['proof_available'] and execution['state'] == 'completed' else
                        'interrupted' if execution['state'] == 'interrupted' else 'failed')
        if not complete or error:
            if row.get('fallback_reason') == 'post_resolver_audit_retained_R2':
                audit = row['post_resolver_audit']
                row['interruption'] = {'stage': 'post_resolver_audit', 'stage_inferred': False,
                    'reason': audit.get('reason') or error or 'R3 did not receive all four valid audit approvals',
                    'record': audit['artifact_directory']}
            else:
                row['interruption'] = lane_interruption(run_root, problem_id, candidate,
                    row.get('selected_stage'), execution, error, issues)
        if issues:
            row['recovery_issues'] = issues
        results.append(row)
    selections = []
    if release in VOTER_RELEASES:
        for problem_id in sorted({pid for _, _, pid in lanes}):
            try:
                selections.append(cross_lane_selection(run_root, problem_id, release, python, execute=execute))
            except Exception as error:
                selections.append({'problem_id': problem_id, 'state': 'unavailable',
                                   'reason': f'{type(error).__name__}: {error}'})
    results.sort(key=lambda row: (row['problem_id'], row['candidate_id']))
    succeeded = sum(row['fully_refined'] for row in results)
    exported = sum(row['proof_available'] for row in results)
    fallbacks = sum(row['fallback_used'] for row in results)
    complete = bool(results) and exported == len(results) and execution['state'] == 'completed'
    if release in VOTER_RELEASES and any(s['state'] != 'completed' for s in selections):
        complete = False
    if _processes is not None and _processes.signal:
        execution = {'state': 'interrupted', 'returncode': 128 + _processes.signal,
            'signal': signal.Signals(_processes.signal).name,
                     'reason': f'Stopped by {signal.Signals(_processes.signal).name}'}
        complete = False
    elif not complete and execution['state'] == 'completed':
        execution = dict(execution, state='failed', returncode=1,
                         reason='One or more lanes or cross-lane selections are incomplete')
    execution['lane_errors'] = lane_errors
    write(run_root / 'pipeline_execution.json', execution)
    receipt = {'schema': 'workshop-complete-pipeline-v2', **project_identity(), 'implementation_release': release,
               'implementation_sha256': sha(IMPLEMENTATION / 'releases' / release / 'release.json'),
               'controller_sha256': sha(Path(__file__)),
               'scheduler_sha256': sha(Path(__file__).with_name('problem_queue.py')),
               'profile_sha256': sha(Path(__file__).with_name('profile.json')),
               'stages': list(STAGES), 'terminal_stage': STAGES[-1],
               'finalization_driver_sha256': sha(continuation_driver(release)),
               'experimental_tools': False, 'external_grading': False,
               'selection_policy': ('raw_unanimous_audited_r3_else_r2_then_last_completed' if release == '1.12.0' else 'audited_r3_else_r2_then_last_completed' if release in AUDITED_RELEASES else 'last_completed_proof'),
               'post_resolver_audit_enabled': release in AUDITED_RELEASES, 'execution': execution,
               'state': ('completed_with_fallbacks' if fallbacks else 'completed') if complete else 'completed_with_failures',
               'completed_proofs': exported, 'fully_refined_proofs': succeeded,
               'fallback_proofs': fallbacks, 'lanes': results,
               'recovery_issues': discovery_issues}
    if release in VOTER_RELEASES:
        # Launch failure or interruption can precede the saved run identity.
        # Preserve the failure receipt without inventing a selector policy.
        winner_policy = None
        identity_path = run_root / 'harness_release.json'
        if identity_path.exists():
            winner_policy = ('qwen_only_full_round_robin_seed_order_ties'
                             if read(identity_path).get('final_selector')
                             else 'dual_model_full_round_robin_seed_order_ties')
        receipt.update(cross_lane_voter_enabled=True, problem_selections=selections,
                       winner_selection_policy=winner_policy)
    write(run_root / 'final_results.json', receipt)
    print(f'Final export: {exported}/{len(results)} completed proofs; '
          f'{succeeded} finished all refinements; {fallbacks} earlier-stage submissions; '
          f'results in {run_root / "proofs"}', flush=True)
    return 0 if complete else 1


def options():
    parser = argparse.ArgumentParser(
        prog='harnesses/proof_workshop/run.py', allow_abbrev=False,
        description='Workshop Pipeline: draft four candidate proofs, run up to three '
                    'refinement passes, and export each lane\'s last completed proof.',
        epilog='Generation requires --problem-dir, --output-dir and either --dry-run or '
               '--execute-models. Recovery uses --collect-only --output-dir RUN. '
               'External grading is a separate workflow.')
    parser.add_argument('--release', default=DEFAULT_RELEASE, metavar='VERSION',
                        help='Frozen engine release, separate from the public project version (default: %(default)s).')
    inspection = parser.add_argument_group('release information (no model calls)').add_mutually_exclusive_group()
    inspection.add_argument('--version', action='store_true', help='Print the TrinitySM public project version after verifying the engine.')
    inspection.add_argument('--verify', action='store_true', help='Verify the engine and show separate project and implementation identities as JSON.')
    inspection.add_argument('--list-releases', action='store_true', help='List bundled frozen engine releases.')
    mode = parser.add_argument_group('execution mode (choose one)').add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='Prepare and validate a new run without model calls.')
    mode.add_argument('--execute-models', action='store_true', help='Run local models through the complete proof pipeline.')
    mode.add_argument('--collect-only', action='store_true', help='Export completed proofs from an existing stopped run; no model calls or inference resume.')
    inputs = parser.add_argument_group('inputs and output')
    inputs.add_argument('--problem-dir', type=Path, metavar='DIR', help='Directory of statement-only problem JSON files.')
    inputs.add_argument('--output-dir', type=Path, metavar='RUN', help='Run directory; must be new unless resuming or collecting saved proofs.')
    inputs.add_argument('--problem-id', action='append', metavar='ID', help='Select a problem; repeat for multiple IDs. Default: all problems.')
    inputs.add_argument('--limit', type=int, metavar='N', help='Process at most N selected problems.')
    runtime = parser.add_argument_group('runtime and sampling (omitted values use the pinned release defaults)')
    runtime.add_argument('--gemma-endpoint', metavar='URL', help='Local Gemma server URL.')
    runtime.add_argument('--qwen-endpoint', metavar='URL', help='Local Qwen server URL.')
    runtime.add_argument('--model-timeout-sec', type=int, metavar='SECONDS', help='Model request timeout setting.')
    runtime.add_argument('--seed-namespace', metavar='TEXT', help='Seed namespace, passed unchanged. Omit to preserve the recorded default.')
    runtime.add_argument('--raw-seed-offset', type=int, metavar='N', help='Unsigned 32-bit offset for the raw portfolio seeds.')
    resume = parser.add_argument_group('resume a matching saved run')
    resume.add_argument('--resume', action='store_true', help='Resume with the original configuration at supported saved boundaries; partial refinement work may require recovery.')
    resume.add_argument('--skip-failed-problem', action='append', metavar='ID', help='With --resume, preserve a validated fully failed problem and continue; repeat for multiple IDs.')
    return parser


def implementation_command(args):
    # Do not introduce public-name replacements into seed namespaces or native
    # checkpoint identities. Omitted defaults still belong to the pinned engine.
    command = [sys.executable, '-B', str(IMPLEMENTATION / 'run.py'), '--release', args.release]
    for name in RUN_OPTIONS:
        value = getattr(args, name)
        if value is None or value is False:
            continue
        flag = '--' + name.replace('_', '-')
        if value is True:
            command.append(flag)
        else:
            for item in value if isinstance(value, list) else [value]:
                command += [flag, str(item)]
    return command


def show_release(release, *, version_only=False):
    # The existing controller verifies its registry, launcher and full inventory
    # before returning metadata. Only the public presentation is changed here.
    result = subprocess.run([sys.executable, '-B', str(IMPLEMENTATION / 'run.py'),
                             '--release', release, '--verify'],
                            check=True, cwd=ROOT, text=True, capture_output=True)
    implementation = json.loads(result.stdout)
    profile = read(Path(__file__).with_name('profile.json'))
    project = project_identity()
    if version_only:
        print(f"{project['project_name']} {project['project_version']}")
        return
    print(json.dumps({'name': project['project_name'],
                      'version': project['project_version'], 'component': profile['name'],
                      'implementation_release': release,
                      'harness_variant': 'B' if release in ('1.8.0', *AUDITED_RELEASES) else 'A',
                      'implementation_sha256': implementation['release_sha256'],
                      'verified_files': implementation['verified_files'], 'upstream': implementation['upstream'],
                      'stages': profile['stages'], 'terminal_stage': profile['terminal_stage'],
                      'final_submission_policy': ('raw_unanimous_audited_r3_else_r2_then_last_completed' if release == '1.12.0' else 'audited_r3_else_r2_then_last_completed' if release in AUDITED_RELEASES else 'last_completed_proof'),
                      'post_resolver_audit': release in AUDITED_RELEASES,
                      'cross_lane_voter': release in VOTER_RELEASES,
                      'new_run_final_selector': selector_policy.binding(release),
                      'project_manifest_sha256': project['project_manifest_sha256'],
                      'controller_sha256': sha(Path(__file__)),
                      'profile_sha256': sha(Path(__file__).with_name('profile.json'))}, indent=2))


def main(argv=None):
    global _processes
    parser = options()
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argv)
    explicit_release = any(arg == '--release' or arg.startswith('--release=') for arg in argv)
    if (args.resume or args.collect_only) and args.output_dir and (args.output_dir / 'harness_release.json').exists():
        original_release = saved_release(args.output_dir)
        if explicit_release and args.release != original_release:
            parser.error('Resume/collection must use the saved implementation release.')
        args.release = original_release
    if args.release not in SUPPORTED_RELEASES:
        parser.error('Workshop Pipeline supports B (1.12.0), previous B (1.11.0/1.10.0/1.9.0/1.8.0), and A (1.7.0).')
    supplied_run_options = [name for name in RUN_OPTIONS if getattr(args, name) is not None and getattr(args, name) is not False]
    if args.version or args.verify or args.list_releases:
        if supplied_run_options or args.collect_only:
            parser.error('Release information options cannot be combined with run options.')
        if args.list_releases:
            print('\n'.join(sorted(read(IMPLEMENTATION / 'releases/index.json')['releases'],
                                   key=lambda version: tuple(map(int, version.split('.'))))))
        else:
            try:
                show_release(args.release, version_only=args.version)
            except subprocess.CalledProcessError as error:
                print('Workshop Pipeline implementation verification failed:\n' + error.stderr, file=sys.stderr)
                return error.returncode
        return 0
    if not args.output_dir:
        parser.error('Provide --output-dir RUN.')
    if args.collect_only:
        if any(name != 'output_dir' for name in supplied_run_options):
            parser.error('--collect-only uses the saved run configuration; provide only --output-dir and optionally --release.')
        if not args.output_dir.is_dir():
            parser.error('--collect-only requires an existing run directory.')
    else:
        if not args.problem_dir or not (args.dry_run or args.execute_models):
            parser.error('Generation requires --problem-dir, --output-dir and --dry-run or --execute-models.')
        if args.skip_failed_problem and not args.resume:
            parser.error('--skip-failed-problem requires --resume.')
    command = implementation_command(args)
    # The external scheduler keeps the engine's frozen inputs and workers, but
    # selects each lane's last completed proof before advancing to the next problem.
    command[2] = str(Path(__file__).with_name('problem_queue.py'))
    run_root = args.output_dir.resolve()
    run_root.parent.mkdir(parents=True, exist_ok=True)
    with (run_root.parent / ('.' + run_root.name + '.workshop.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.collect_only:
            # A killed controller can leave an active native worker behind.
            with ExitStack() as locks:
                for path in sorted([*run_root.glob('problems/*/worker.lock'), *run_root.glob('post_resolver_audit/*/audit.lock'), *run_root.glob('cross_lane_voter/*/*/controller.lock')]):
                    worker_lock = locks.enter_context(path.open('a'))
                    fcntl.flock(worker_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                execution = optional_record(run_root / 'pipeline_execution.json', []) or {
                    'state': 'interrupted', 'returncode': None,
                    'reason': 'Offline collection after an unrecorded stop; original cause unknown'}
                return finalize(run_root, args.release, execute=False, execution=execution)
        _processes = Processes(lock.fileno())
        handlers = {sig: signal.signal(sig, _processes.stop) for sig in (signal.SIGINT, signal.SIGTERM)}
        sequence_path = run_root / 'problem_sequence.json'
        try:
            try:
                result = run_process(command, cwd=ROOT)
                execution = {'state': 'completed' if result == 0 else 'failed', 'returncode': result}
                if result:
                    execution['reason'] = f'Generation process exited with status {result}'
                if sequence_path.is_file():
                    sequence = read(sequence_path)
                    execution['scheduling_policy'] = sequence['scheduling_policy']
                    execution['lane_errors'] = sequence.get('lane_errors', {})
                    if result and sequence.get('error'):
                        execution['reason'] = sequence['error']
            except Exception as error:
                result = 1
                execution = {'state': 'failed', 'returncode': result,
                             'reason': f'{type(error).__name__}: {error}'}
            if _processes.signal:
                result = 128 + _processes.signal
                execution.update(state='interrupted', returncode=result,
                                 signal=signal.Signals(_processes.signal).name,
                                 reason=f'Stopped by {signal.Signals(_processes.signal).name}')
            if args.dry_run:
                if result:
                    return result
                write(run_root / 'full_pipeline_preflight.json', {
                    **project_identity(),
                    'state': 'preflight_passed', 'model_calls': 0, 'final_review_included': True,
                    'post_resolver_audit_included': args.release in AUDITED_RELEASES,
                    'stages': list(STAGES), 'terminal_stage': STAGES[-1],
                    'controller_sha256': sha(Path(__file__)), 'implementation_release': args.release,
                    'scheduler_sha256': sha(Path(__file__).with_name('problem_queue.py')),
                    'scheduling_policy': SCHEDULING_POLICY,
                })
                print('Full pipeline preflight passed; up to three refinement passes run automatically.')
                return 0
            write(run_root / 'pipeline_execution.json', execution)
            # A recorded per-problem scheduler already attempted the final pass.
            # Collection must not repeat failed model calls or advance a fallback.
            exported = finalize(run_root, args.release,
                                execute=result == 0 and not sequence_path.is_file(), execution=execution,
                                allow_export_advance=args.resume)
            return (128 + _processes.signal) if _processes.signal else result or exported
        finally:
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
            _processes = None


if __name__ == '__main__':
    raise SystemExit(main())
