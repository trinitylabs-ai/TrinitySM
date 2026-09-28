#!/usr/bin/env python3
"""Archive a completed sampled suite's intermediate artifacts for Git and paired studies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

import audit_release as audit

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {'imo2026': 6, 'imo-proofbench/basic': 3, 'imo-proofbench/advanced': 3}
CANDIDATES = {'t10_r01', 't10_r02', 't07_r01', 't07_r02'}
FINAL_STAGES = {'raw', 'lazy_checked', 'refinement_1', 'refinement_2', 'refinement_3'}
EARLY_STAGES = {'raw', 'lazy_checked'}
MAX_FILE_BYTES = 90 * 1024 * 1024
IMMUTABLE_JSON_FIELDS = {'content', 'reasoning_content', 'reasoning', 'text',
                         'system_prompt', 'user_prompt', 'prompt', 'proof', 'claim', 'problem',
                         'final', 'effective_final', 'fusion_record', 'analysis', 'checked_proof',
                         'parsed', 'parsed_response', 'response', 'messages', 'repair_brief',
                         'resolver_brief', 'reviewer_1', 'reviewer_2', 'reviewer_3'}
METADATA_FIELDS = {'path', 'paths', 'cwd', 'executable', 'solver_python', 'grader_python',
                   'version_file', 'source', 'destination', 'output', 'model', 'proofs',
                   'final_results', 'console_log', 'source_run', 'producer', 'completion_record',
                   'source_archive', 'resolver_trace_handoff', 'artifact', 'log', 'entrypoint',
                   'prefix', 'python', 'endpoint', 'source_fusion_result'}
METADATA_CONTAINERS = {'argv', 'command', 'cmd', 'environment', 'env', 'stage_dirs'}
OPAQUE_JSON_FIELDS = IMMUTABLE_JSON_FIELDS - {'problem', 'proof', 'reviewer_1', 'reviewer_2', 'reviewer_3'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def proof_digest(path):
    return digest(path.read_text(encoding='utf-8').strip().encode('utf-8'))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def child(path, parent):
    path, parent = Path(path).absolute(), parent.absolute()
    require(path.is_relative_to(parent) and path.resolve().is_relative_to(parent.resolve()),
            f'Path escapes expected directory: {path}')
    require(not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(parent)),
            f'Symlink cannot be archived as evidence: {path}')
    require(path.is_file(), f'Missing artifact: {path}')
    return path


def inspect_suite(run_id):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', run_id), 'Invalid run ID')
    suite = ROOT / '.workshop/runs' / run_id
    plan, status = read(suite / 'plan.json'), read(suite / 'status.json')
    require(plan.get('schema') == 'workshop-sampled-suite-v1' and plan['run_id'] == run_id,
            'Not a sampled-suite plan for this run')
    require(status.get('state') == 'completed', 'Suite is not completed; keep it running and archive after completion')
    jobs = plan['jobs']
    require(len(jobs) == 3 and {j['benchmark'] for j in jobs} == set(GROUPS), 'Expected all three benchmarks')
    outcomes = status['outcomes']
    require(len(outcomes) == 3 and {r['benchmark'] for r in outcomes} == set(GROUPS)
            and all(r['returncode'] == 0 for r in outcomes), 'Suite outcomes are incomplete or failed')
    require(plan['problem_count'] == 12 and plan['candidates_per_problem'] == 4, 'Expected 12 problems / 48 lanes')
    paired, unpaired, protected, checked = [], [], set(), {}

    def bound(path, parent, expected=None, text_hash=None):
        path = child(path, parent)
        actual = digest(path.read_bytes())
        require(expected is None or actual == expected, f'Artifact hash mismatch: {path}')
        require(text_hash is None or proof_digest(path) == text_hash, f'Proof text hash mismatch: {path}')
        checked[path] = actual
        return path

    roots = [(suite / name, Path('suite') / name) for name in ('plan.json', 'status.json')]
    for path, _ in roots:
        bound(path, suite)
    for job in jobs:
        benchmark = job['benchmark']
        ids = job['problem_ids']
        require(len(ids) == GROUPS[benchmark] and len(set(ids)) == len(ids)
                and all(re.fullmatch(r'[A-Za-z0-9_-]+', p) for p in ids), 'Invalid problem selection')
        experiment = ROOT / 'benchmarks' / benchmark / 'results' / run_id
        run = experiment / 'generation/run'
        identity = read(bound(experiment / 'experiment.json', experiment))
        completion = read(bound(experiment / 'generation/completion.json', experiment))
        require(identity.get('run_id') == run_id and identity.get('benchmark') == benchmark
                and identity.get('state') == 'completed', f'Experiment not complete: {benchmark}')
        require(completion.get('worker_exited') is True and completion.get('returncode') == 0,
                f'Worker not finished: {benchmark}')
        queue = read(bound(run / 'manifest.json', run))
        release = read(bound(run / 'harness_release.json', run))
        final = read(bound(run / 'final_results.json', run))
        require({p['problem_id'] for p in queue['problems']} == set(ids), 'Queue differs from suite selection')
        for settings in (queue, release['parameters']):
            require(settings['seed_namespace'] == plan['seed_namespace']
                    and settings.get('raw_seed_offset', 0) == plan['raw_seed_offset'], 'Generation seed mismatch')
        require(final.get('state') in ('completed', 'completed_with_fallbacks')
                and final['execution'].get('state') == 'completed'
                and final['execution'].get('returncode') == 0,
                f'Pipeline did not complete submission export: {benchmark}')
        lanes = final['lanes']
        expected = {(pid, candidate) for pid in ids for candidate in CANDIDATES}
        require(len(lanes) == len(expected) and {(r['problem_id'], r['candidate_id']) for r in lanes} == expected,
                f'Final lane identities differ from plan: {benchmark}')
        finals = {(r['problem_id'], r['candidate_id']): r for r in lanes}

        def archived(path):
            return (Path('artifacts') / benchmark / path.relative_to(experiment)).as_posix()

        for pid in ids:
            baseline = run / 'problems' / pid / '02_r1_cycles'
            inputs = {}
            baseline_manifest = baseline / 'manifest.json'
            if baseline_manifest.exists() or baseline_manifest.is_symlink():
                # A present receipt must validate; startup may stop before one is written.
                manifest_path = bound(baseline_manifest, baseline)
                manifest = read(manifest_path)
                require(manifest['problem_id'] == pid and set(manifest['candidate_ids']) == CANDIDATES,
                        'Initial portfolio identity mismatch')
                require(manifest['input_checkpoint'] == 'lazy_checked', 'Expected pre-Qwen input checkpoint')
                require(manifest['runtime']['seed_namespace'] == f"{plan['seed_namespace']}:{pid}:r1",
                        'Refinement seed namespace mismatch')
                frozen = manifest['frozen_inputs']
                problem = bound(Path(frozen['problem_path']), baseline / 'input', frozen['problem_file_sha256'])
                require(digest(str(read(problem)['claim']).strip().encode()) == frozen['problem_text_sha256'],
                        'Problem statement hash mismatch')
                protected.add(problem)
                rows = frozen['lanes']
                require(len(rows) == 4 and {r['candidate_id'] for r in rows} == CANDIDATES,
                        'Initial candidate set mismatch')
                inputs = {row['candidate_id']: row for row in rows}
            for candidate in sorted(CANDIDATES):
                final_row = finals[pid, candidate]
                stage = final_row.get('selected_stage')
                lane_state = 'completed' if stage == 'refinement_3' else 'completed_with_fallback'
                require(final_row.get('proof_available') and stage in FINAL_STAGES
                        and final_row.get('state') == lane_state, 'Incomplete or mislabeled final proof')
                proof = bound(run / final_row['proof'], run, final_row['sha256'], final_row['proof_sha256'])
                producer = bound(run / final_row['producer'], run, text_hash=final_row['proof_sha256'])
                require(proof.read_bytes() == producer.read_bytes(), 'Export differs from producer proof')
                bound(run / final_row['completion_record'], run)
                protected.update((proof, producer))
                submission = dict(benchmark=benchmark, problem_id=pid, candidate_id=candidate,
                    final_proof=archived(proof), final_sha256=final_row['sha256'],
                    final_proof_sha256=final_row['proof_sha256'], selected_stage=stage,
                    final_state=final_row['state'])
                row = inputs.get(candidate)
                if row is None or not row.get('proof_path'):
                    require(stage in EARLY_STAGES, f'No pre-Qwen input for refined final: {pid}/{candidate}')
                    require(row is None or row.get('source_failure'),
                            f'Missing pre-Qwen proof without a recorded source failure: {pid}/{candidate}')
                    if row and row.get('source_proof_path'):
                        original = bound(Path(row['source_proof_path']), run, text_hash=row['source_proof_sha256'])
                        protected.add(original)
                    unpaired.append(dict(submission, reason='pre_qwen_manifest_unavailable' if row is None
                                         else 'pre_qwen_input_unavailable_after_source_failure'))
                    continue
                initial = bound(Path(row['proof_path']), baseline / 'input', text_hash=row['proof_sha256'])
                original = bound(Path(row['source_proof_path']), run, text_hash=row['source_proof_sha256'])
                require(initial.read_bytes() == original.read_bytes(), 'Staged input differs from source proof')
                protected.update((initial, original))
                paired.append(dict(submission,
                    problem=archived(problem), baseline_manifest=archived(manifest_path),
                    checkpoint=row.get('source_checkpoint', 'lazy_checked'),
                    input_proof=archived(initial), input_sha256=digest(initial.read_bytes()),
                    input_proof_sha256=row['proof_sha256'], seed_namespace=manifest['runtime']['seed_namespace']))
        roots.append((experiment, Path('artifacts') / benchmark))
    return plan, roots, paired, unpaired, protected, checked


def exclusion(path):
    parts = path.parts
    if any(p in ('grading', 'grades', '__pycache__', '.pytest_cache') or p.startswith('.venv') for p in parts):
        return 'grading_or_local_cache'
    if any(audit.LOG_DIR.fullmatch(p) for p in parts[:-1]) or audit.LOG_FILE.fullmatch(path.name):
        return 'operational_log'
    if path.suffix in audit.WEIGHTS or path.suffix in ('.lock', '.pid', '.tmp', '.pyc'):
        return 'local_state_or_binary'
    if path.name.startswith('.env') or path.suffix in ('.pem', '.key'):
        return 'local_credentials'
    return None


def redact_string(value):
    value = value.replace(str(ROOT), '${SOURCE_REPO}')
    value = audit.PERSONAL_HOME.sub('/home/user', value)
    value = re.sub(r'/Users/[^/\s"\x27]+', '/Users/user', value)
    value = audit.EMAIL.sub('[REDACTED_EMAIL]', value)
    def address(match):
        try:
            ip = audit.ipaddress.ip_address(match.group())
        except ValueError:
            return match.group()
        return '[PRIVATE_IP]' if any(ip in network for network in audit.NETWORKS) else match.group()
    return audit.IPV4.sub(address, value)


def redact_json(value, metadata=False, runtime_record=False):
    if isinstance(value, str):
        return redact_string(value) if metadata else value
    if isinstance(value, list):
        return [redact_json(item, metadata, runtime_record) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key in OPAQUE_JSON_FIELDS or key in IMMUTABLE_JSON_FIELDS and isinstance(item, str):
                result[key] = item
            else:
                is_metadata = (metadata or runtime_record and key in ('error', 'worker_error', 'reason', 'lane_errors') or
                    key in METADATA_CONTAINERS or key == 'paths' or key.endswith('_paths') or
                    isinstance(item, str) and (key in METADATA_FIELDS or
                        key.endswith(('_path', '_paths', '_dir', '_root', '_endpoint'))))
                result[key] = redact_json(item, is_metadata, runtime_record)
        return result
    return value


def public_bytes(path, data, protected):
    text = data.decode('utf-8')
    require(not audit.TOKEN.search(text) and not audit.PRIVATE_KEY.search(text),
            f'Credential pattern found; artifact was not exported: {path.relative_to(ROOT)}')
    result = data
    if path not in protected:
        if path.suffix == '.json':
            original = json.loads(text)
            runtime_record = (path.parent.name == 'run' and path.parent.parent.name == 'generation'
                              and path.name in ('final_results.json', 'pipeline_execution.json',
                                                'problem_sequence.json', 'status.json'))
            updated = redact_json(original, runtime_record=runtime_record)
            if updated != original:
                result = (json.dumps(updated, ensure_ascii=False, indent=2) + '\n').encode()
        elif path.suffix == '.jsonl':
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
            updated = redact_json(rows)
            if updated != rows:
                result = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in updated).encode()
        elif path.name in ('launch.sh', 'launch_gemma.sh', 'launch_qwen.sh', 'ENVIRONMENT.md'):
            result = redact_string(text).encode()
    return result


def verify(directory):
    directory = directory.absolute()
    manifest = read(directory / 'archive_manifest.json')
    require(manifest.get('schema') == 'workshop-full-trace-archive-v1', 'Unknown archive schema')
    listed = set()
    for row in manifest['files']:
        path = child(directory / row['path'], directory)
        require(row['path'] not in listed, 'Duplicate archive path')
        listed.add(row['path'])
        require(digest(path.read_bytes()) == row['archived_sha256'], f'Archive hash mismatch: {row["path"]}')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() or p.is_symlink()}
    require(actual == listed | {'archive_manifest.json'}, 'Archive has missing or unexpected files')
    paired = manifest['paired_inputs']
    unpaired = manifest.get('unpaired_finals', [])
    finals = paired + unpaired
    identities = {(row['benchmark'], row['problem_id'], row['candidate_id']) for row in finals}
    require(len(finals) == 48 and len(identities) == 48, 'Archive must account for all 48 final submissions')
    for row in finals:
        require(row['selected_stage'] in FINAL_STAGES, 'Unknown final submission stage')
        for prefix in (('input', 'final') if 'input_proof' in row else ('final',)):
            path = child(directory / row[prefix + '_proof'], directory)
            require(digest(path.read_bytes()) == row[prefix + '_sha256']
                    and proof_digest(path) == row[prefix + '_proof_sha256'], 'Paired proof hash mismatch')
    require(all('input_proof' in row for row in paired), 'Paired input proof is missing')
    require(all('input_proof' not in row and row['selected_stage'] in EARLY_STAGES and row.get('reason')
                for row in unpaired), 'Unpaired final requires an early stage and a reason')
    print(f'Verified {len(listed)} artifacts, {len(finals)} final submissions, '
          f'{len(paired)} paired inputs and {len(unpaired)} unpaired finals.')
    return manifest


def archive(run_id, dry_run=False):
    plan, roots, paired, unpaired, protected, checked = inspect_suite(run_id)
    destination = ROOT / 'benchmarks/reports' / (run_id + '_full_trace')
    require(not destination.exists() and not destination.is_symlink(), f'Archive already exists: {destination}; use --verify')
    records, omitted, sources = [], [], []
    for source, prefix in roots:
        paths = sorted(source.rglob('*')) if source.is_dir() else [source]
        for path in paths:
            relative = prefix / path.relative_to(source) if source.is_dir() else prefix
            reason = exclusion(relative)
            if reason:
                if path.is_file() or path.is_symlink():
                    omitted.append(dict(source_path=path.relative_to(ROOT).as_posix(), reason=reason))
                continue
            require(not path.is_symlink(), f'Symlink requires an explicit real artifact: {path}')
            if not path.is_file():
                continue
            require(path.stat().st_size <= MAX_FILE_BYTES, f'Artifact exceeds Git export limit (90 MiB): {path}')
            sources.append((path, relative))
    if dry_run:
        size = sum(path.stat().st_size for path, _ in sources)
        print(f'Completion/size check: {len(sources)} artifacts, {len(paired)} paired lanes, '
              f'{len(unpaired)} unpaired finals, {size / 1024**2:.1f} MiB before metadata normalization.')
        print(f'Destination: {destination}\nNo files written; publication-content checks run during export.')
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.' + run_id + '_archive_', dir=ROOT / '.workshop'))
    references, _, reference_paths = audit.external_reference_identities()
    try:
        for path, relative in sources:
            before = path.stat()
            data = path.read_bytes()
            after = path.stat()
            source_hash = digest(data)
            require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), f'Artifact is changing: {path}')
            require(path not in checked or source_hash == checked[path], f'Validated artifact changed: {path}')
            result = public_bytes(path, data, protected)
            findings = audit.inspect(relative.as_posix(), result.decode('utf-8'))
            findings += audit.inspect_external_reference(path.relative_to(ROOT).as_posix(), data, references, reference_paths)
            require(not findings, f'Artifact requires review before publication: {path.relative_to(ROOT)} ({", ".join(findings)})')
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(result)
            records.append(dict(path=relative.as_posix(), source_path=path.relative_to(ROOT).as_posix(),
                source_sha256=source_hash, archived_sha256=digest(result), bytes=len(result),
                transformation='unchanged' if result == data else 'machine_metadata_normalized'))
        fully_refined = sum(row['selected_stage'] == 'refinement_3' for row in paired + unpaired)
        documentation = (
            '# Full intermediate trace for paired ablations\n\n'
            f'Source run: `{run_id}`. All 12 problems have finished with 48 submitted proofs; proofs are ungraded. '
            f'{fully_refined} submissions reached refinement 3; {48 - fully_refined} use an earlier completed stage.\n\n'
            'The archive retains statement/input/final proof bytes and all available non-log intermediate artifacts, '
            'including prompts, model-response content, reviews, fusion, audit, resolver, usage, timing and serving settings. '
            'The manifest lists every copied file, source/archive SHA-256 and exclusions. '
            'Some metadata paths, addresses and emails are normalized; embedded source hashes still describe ORIGINAL artifacts. '
            '`${SOURCE_REPO}` is the original repository root. This archive is not a native resume directory. '
            'Keep the original experiment folders on the server unchanged.\n\n'
            f'`paired_inputs` binds {len(paired)} exact pre-Qwen inputs to their submitted proofs. '
            f'`unpaired_finals` records {len(unpaired)} early submissions without a saved pre-Qwen input, with reasons; '
            'these cannot be included in a paired continuation without obtaining a common input first. '
            'A paired runner must stage new inputs and manifests, preserve recorded seeds/policies and rerun all affected downstream steps. '
            'Never present a fallback checkpoint as a completed lazy/expansion checkpoint.\n\n'
            'Current follow-up priorities are end-to-end mixed-model runs and generation-seed sensitivity '
            'on the same selected problems. Gemma-only and NVFP4 comparisons are deferred; the retained '
            'inputs preserve those options. No comparison or grading has been run by this exporter.\n')
        data = documentation.encode()
        (temporary / 'README.md').write_bytes(data)
        records.append(dict(path='README.md', archived_sha256=digest(data), bytes=len(data), transformation='generated'))
        manifest = dict(schema='workshop-full-trace-archive-v1', run_id=run_id,
            archived_at=datetime.now(timezone.utc).isoformat(), source_state='completed', external_grading=False,
            sample_seed=plan['sample_seed'], generation_seed=plan['generation_seed'],
            raw_seed_offset=plan['raw_seed_offset'], seed_namespace=plan['seed_namespace'],
            exporter_sha256=digest(Path(__file__).read_bytes()), paired_inputs=paired, unpaired_finals=unpaired,
            submitted_proofs=len(paired) + len(unpaired), fully_refined_proofs=fully_refined,
            files=records, excluded=omitted)
        (temporary / 'archive_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        verify(temporary)
        temporary.rename(destination)
        print(f'Archive: {destination}\n{sum(r["bytes"] for r in records) / 1024**2:.1f} MiB; no Git changes staged or committed.')
        return destination
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run-id')
    mode.add_argument('--verify', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='Validate completion/paired inputs and report size without exporting')
    args = parser.parse_args(argv)
    try:
        if args.verify:
            require(not args.dry_run, '--dry-run requires --run-id')
            verify(args.verify)
        else:
            archive(args.run_id, args.dry_run)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
