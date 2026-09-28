"""Hash-bound, statement-only inputs for independent selection."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

CANDIDATES = {'t10_r01', 't10_r02', 't07_r01', 't07_r02'}
STAGES = {'raw', 'lazy_checked', 'refinement_1', 'refinement_2', 'refinement_3'}
GROUPS = {'imo2026': 6, 'imo-proofbench/basic': 3, 'imo-proofbench/advanced': 3}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', value),
            'Use an ID of 1–128 letters, numbers, dots, underscores or hyphens')
    return value


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text_hash(text):
    return digest(text.strip().encode('utf-8'))


def _inside(path, base):
    path, base = Path(path).absolute(), Path(base).resolve()
    require(path.is_relative_to(base) and path.resolve().is_relative_to(base),
            f'Input path escapes its allowed directory: {path}')
    require(not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(base)),
            f'Symlink in input path: {path}')
    return path


class Reader:
    def __init__(self):
        self.sources = {}

    def data(self, path, base, expected=None):
        path = _inside(path, base)
        require(path.is_file(), f'Missing selection input: {path}')
        data = path.read_bytes()
        actual = digest(data)
        require(expected is None or actual == expected, f'Selection input hash mismatch: {path}')
        prior = self.sources.get(str(path))
        require(prior is None or prior == actual, f'Selection input changed while reading: {path}')
        self.sources[str(path)] = actual
        return data

    def json(self, path, base, expected=None):
        value = json.loads(self.data(path, base, expected))
        require(isinstance(value, dict), f'Expected JSON object: {path}')
        return value


def _statement(data, *, json_input, problem_id):
    text = data.decode('utf-8')
    if json_input:
        value = json.loads(text)
        require(isinstance(value, dict) and value.get('problem_id', problem_id) == problem_id,
                'Problem identity mismatch')
        # Never pass references, solutions, grades or other fields to the model.
        text = value.get('claim') or value.get('problem') or value.get('statement') or ''
    require(isinstance(text, str) and text.strip(), 'Empty problem statement')
    return text.strip()


def _finish(reader, *, run_id, problems, requested, **metadata):
    require(problems and len({p['problem_id'] for p in problems}) == len(problems),
            'Empty input or duplicate problem IDs')
    if requested:
        wanted = set(requested)
        require(len(wanted) == len(requested), 'Duplicate --problem-id')
        require(wanted <= {p['problem_id'] for p in problems}, 'Unknown requested problem ID')
        problems = [p for p in problems if p['problem_id'] in wanted]
    return {'schema': 'proof-selector-loaded-input-v1', 'run_id': run_id,
            'problems': problems, 'source_hashes': reader.sources, **metadata}


def load_manifest(path, requested=None):
    """Load a standalone, explicitly hash-bound bank of four proofs per problem.

    All input paths are relative to the manifest directory and remain inside it.
    No reference solution, score, or prior review is accepted as a model input.
    """
    path = Path(path).absolute()
    base = path.parent.resolve()
    # Resolve the directory (including macOS /tmp), but still reject a symlink
    # at the manifest itself and any path declared inside the bank.
    path = base / path.name
    reader = Reader()
    manifest = reader.json(path, base)
    require(manifest.get('schema') == 'proof-selector-input-v1', 'Unsupported selection input schema')
    run_id = identifier(manifest['run_id'])
    problems = []
    for item in manifest['problems']:
        pid = identifier(item['problem_id'])
        statement_path = base / item['problem_path']
        raw = reader.data(statement_path, base, item['problem_file_sha256'])
        problem = _statement(raw, json_input=statement_path.suffix == '.json', problem_id=pid)
        require(len(item['candidates']) == 4, f'Expected four candidates for {pid}')
        candidates = []
        for candidate in item['candidates']:
            cid = identifier(candidate['candidate_id'])
            proof_path = base / candidate['proof_path']
            proof_bytes = reader.data(proof_path, base, candidate['proof_file_sha256'])
            proof = proof_bytes.decode('utf-8')
            require(bool(proof.strip()), f'Empty proof: {pid}/{cid}')
            candidates.append({'candidate_id': cid, 'proof': proof,
                               'proof_path': str(proof_path.absolute()),
                               'proof_file_sha256': digest(proof_bytes),
                               'selected_stage': candidate.get('selected_stage', 'provided_final')})
        require(len({c['candidate_id'] for c in candidates}) == 4, 'Duplicate candidate IDs')
        problems.append({'problem_id': pid, 'problem': problem,
                         'problem_path': str(statement_path.absolute()),
                         'problem_sha256': text_hash(problem), 'candidates': candidates})
    return _finish(reader, run_id=run_id, problems=problems, requested=requested,
                   input_kind='standalone_manifest')


def load_suite(root, run_id, requested=None):
    """Read a completed sampled suite; no grader, reference loader or runtime import."""
    root = Path(root).resolve()
    identifier(run_id)
    reader = Reader()
    suite = root / '.workshop/runs' / run_id
    plan = reader.json(suite / 'plan.json', root)
    status = reader.json(suite / 'status.json', root)
    require(plan.get('schema') == 'workshop-sampled-suite-v1' and plan.get('run_id') == run_id,
            'Not the requested sampled suite')
    require(status.get('state') == 'completed', 'Finish the generation suite before selection')
    jobs, outcomes = plan['jobs'], status['outcomes']
    require(len(jobs) == 3 and {j['benchmark'] for j in jobs} == set(GROUPS),
            'Expected the complete 6+3+3 sampled suite')
    require(len(outcomes) == 3 and {j['benchmark'] for j in outcomes} == set(GROUPS)
            and all(j['returncode'] == 0 for j in outcomes), 'Incomplete suite outcomes')
    require(plan.get('problem_count') == 12 and plan.get('candidates_per_problem') == 4,
            'Expected 12 problems and four candidates per problem')
    problems = []
    for job in jobs:
        benchmark, ids = job['benchmark'], job['problem_ids']
        require(len(ids) == GROUPS[benchmark] and len(set(ids)) == len(ids), 'Invalid problem selection')
        for pid in ids:
            identifier(pid)
        base = root / 'benchmarks' / benchmark
        experiment = base / 'results' / run_id
        run = experiment / 'generation/run'
        catalog = reader.json(base / 'catalog.json', root, job['catalog_sha256'])
        catalog_rows = {r['problem_id']: r for r in catalog['generation_inputs']['files']}
        inputs = {r['problem_id']: r for r in job['inputs']}
        require(len(inputs) == len(job['inputs']) == len(ids) and set(inputs) == set(ids),
                'Suite statement selection is inconsistent')
        identity = reader.json(experiment / 'experiment.json', root)
        completion = reader.json(experiment / 'generation/completion.json', root)
        final = reader.json(run / 'final_results.json', root)
        require(identity.get('run_id') == run_id and identity.get('benchmark') == benchmark
                and identity.get('state') == 'completed', 'Incomplete generation experiment')
        require(completion.get('worker_exited') is True and completion.get('returncode') == 0,
                'Generation worker has not completed')
        require(final.get('state') in {'completed', 'completed_with_fallbacks'}
                and final.get('execution', {}).get('state') == 'completed'
                and final['execution'].get('returncode') == 0, 'Incomplete final-proof export')
        expected = {(pid, cid) for pid in ids for cid in CANDIDATES}
        lanes = final['lanes']
        require(len(lanes) == len(expected)
                and {(r['problem_id'], r['candidate_id']) for r in lanes} == expected,
                'Final-proof coverage differs from the plan')
        for pid in ids:
            item = inputs[pid]
            require(item == catalog_rows[pid], 'Statement metadata differs from catalog')
            statement_path = base / item['path']
            raw = reader.data(statement_path, base / 'problems', item['sha256'])
            problem = _statement(raw, json_input=True, problem_id=pid)
            candidates = []
            for row in (r for r in lanes if r['problem_id'] == pid):
                cid, stage = row['candidate_id'], row.get('selected_stage')
                require(row.get('proof_available') is True and stage in STAGES
                        and row.get('state') == ('completed' if stage == 'refinement_3'
                                                else 'completed_with_fallback'), 'Invalid final-lane state')
                proof_path = run / row['proof']
                raw_proof = reader.data(proof_path, run, row['sha256'])
                producer = reader.data(run / row['producer'], run)
                reader.json(run / row['completion_record'], run)
                proof = raw_proof.decode('utf-8')
                require(raw_proof == producer and bool(proof.strip())
                        and text_hash(proof) == row['proof_sha256'], 'Final proof differs from producer')
                candidates.append({'candidate_id': cid, 'proof': proof,
                                   'proof_path': str(proof_path), 'proof_file_sha256': digest(raw_proof),
                                   'selected_stage': stage})
            problems.append({'problem_id': pid, 'benchmark': benchmark, 'problem': problem,
                             'problem_path': str(statement_path), 'problem_sha256': text_hash(problem),
                             'candidates': candidates})
    return _finish(reader, run_id=run_id, problems=problems, requested=requested,
                   input_kind='completed_sampled_suite', sample_seed=plan.get('sample_seed'),
                   generation_seed=plan.get('generation_seed'))


def load_published_imo(root, requested=None):
    """Load the published IMO baseline bank, without opening any grading evidence.

    The snapshot supplies only lane identity, checkpoint, proof path and hash.
    Its scores, tool selections, references and grading records never enter the
    loaded problems or candidates. Validate the entire bank before filtering.
    """
    root = Path(root).resolve()
    reader = Reader()
    public = root / 'docs/public_release'
    snapshot = reader.json(public / 'score_snapshot.json', root)
    require(snapshot.get('schema') == 'public-release-evaluation-snapshot-v5',
            'Unsupported published proof snapshot schema')
    expected_ids = {f'imo2026_p{number}' for number in range(1, 7)}
    base = root / 'benchmarks/imo2026'
    catalog = reader.json(base / 'catalog.json', root)
    generation = catalog.get('generation_inputs', {})
    rows = generation.get('files', [])
    require(catalog.get('benchmark_id') == 'imo2026'
            and generation.get('statement_only') is True and generation.get('count') == 6
            and len(rows) == 6 and {row['problem_id'] for row in rows} == expected_ids,
            'Expected the six statement-only IMO 2026 catalog entries')
    statements = {row['problem_id']: row for row in rows}
    lanes = [row for row in snapshot['lanes'] if row.get('benchmark') == 'IMO 2026']
    require(len(lanes) == 24 and all(row.get('included') is True for row in lanes)
            and {(row['problem_id'], row['candidate']) for row in lanes}
            == {(pid, cid) for pid in expected_ids for cid in CANDIDATES},
            'Expected all 24 unique published IMO baseline lanes')
    checkpoints = {'raw': 'raw', 'lazy_checked': 'lazy_checked',
                   'R1-C1': 'refinement_1', 'R1-C2': 'refinement_2', 'R1-C3': 'refinement_3'}
    problems = []
    for pid in sorted(expected_ids):
        item = statements[pid]
        statement_path = base / item['path']
        problem = _statement(reader.data(statement_path, base / 'problems', item['sha256']),
                             json_input=True, problem_id=pid)
        candidates = []
        for row in sorted((row for row in lanes if row['problem_id'] == pid),
                          key=lambda row: row['candidate']):
            baseline = row.get('baseline')
            require(isinstance(baseline, dict) and baseline.get('checkpoint') in checkpoints,
                    'Invalid published baseline checkpoint')
            expected_hash = baseline.get('proof_sha256')
            require(isinstance(expected_hash, str) and re.fullmatch(r'[0-9a-f]{64}', expected_hash),
                    'Invalid published baseline proof hash')
            proof_path = public / baseline['proof']
            raw = reader.data(proof_path, public / 'evidence/proofs', expected_hash)
            proof = raw.decode('utf-8')
            require(bool(proof.strip()), f'Empty published proof: {pid}/{row["candidate"]}')
            candidates.append({'candidate_id': row['candidate'], 'proof': proof,
                               'proof_path': str(proof_path), 'proof_file_sha256': digest(raw),
                               'selected_stage': checkpoints[baseline['checkpoint']]})
        problems.append({'problem_id': pid, 'benchmark': 'imo2026', 'problem': problem,
                         'problem_path': str(statement_path), 'problem_sha256': text_hash(problem),
                         'candidates': candidates})
    return _finish(reader, run_id='published_imo2026_baseline', problems=problems,
                   requested=requested, input_kind='published_imo2026_baseline')


def verify_sources(inputs):
    for name, expected in inputs['source_hashes'].items():
        path = Path(name)
        require(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents))
                and digest(path.read_bytes()) == expected,
                f'Selection source changed: {path}')
