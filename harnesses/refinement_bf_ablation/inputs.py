"""Receipt-bound lazy-check inputs; never read grades or reference solutions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'harnesses/imo_proof_pipeline/releases/1.7.0'
CANDIDATES = ('t10_r01', 't10_r02', 't07_r01', 't07_r02')
SCHEMA = 'refinement-bf-inputs-v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}', value),
            'Expected a simple problem identifier')
    return value


def read(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    require(isinstance(value, dict), f'Expected JSON object: {path}')
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_hash(path):
    return hashlib.sha256(Path(path).read_text(encoding='utf-8').strip().encode()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def safe_file(path, root):
    path, root = Path(path).absolute(), Path(root).resolve()
    require(path.is_file() and not path.is_symlink(), f'Missing or symlink input: {path}')
    require(all(not p.is_symlink() for p in path.parents), f'Symlink input parent: {path}')
    require(path.resolve().is_relative_to(root), f'Input escapes source root: {path}')
    return path.resolve()


def load_sources(run_paths, requested):
    """Require four completed lazy-check producers in each selected native run."""
    require(requested and len(set(requested)) == len(requested), 'Select unique --problem-id values')
    requested = set(map(identifier, requested))
    hashes, problems = {}, []
    seen_roots = set()
    for raw in run_paths:
        root = Path(raw).absolute()
        require(root.is_dir() and not root.is_symlink()
                and all(not p.is_symlink() for p in root.parents), 'Invalid source run directory')
        root = root.resolve()
        require(root not in seen_roots, 'Duplicate source run')
        seen_roots.add(root)

        def tracked(path):
            path = safe_file(path, root)
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            require(str(path) not in hashes or hashes[str(path)] == sha, 'Source changed during inspection')
            hashes[str(path)] = sha
            return data

        def obj(path):
            value = json.loads(tracked(path))
            require(isinstance(value, dict), 'Expected source object')
            return value

        identity = obj(root / 'harness_release.json')
        require(identity.get('version') == '1.7.0'
                and identity.get('release_sha256') == digest(RELEASE / 'release.json'),
                'Source is not the pinned release 1.7.0')
        manifest = obj(root / 'manifest.json')
        require(manifest.get('schema') == 'v263_lazy_refined_to_v290_r1c2_queue_v1'
                and manifest.get('dry_run') is False, 'Expected an actual native generation run')
        rows = manifest.get('problems')
        require(isinstance(rows, list) and all(isinstance(r, dict) for r in rows), 'Invalid source problem list')
        ids = [identifier(r.get('problem_id')) for r in rows]
        require(len(set(ids)) == len(ids), 'Duplicate source problem')
        for row in rows:
            pid = row['problem_id']
            if pid not in requested:
                continue
            require(pid not in {p['problem']['problem_id'] for p in problems}, 'Problem occurs in multiple source runs')
            number, claim = row.get('problem_number'), row.get('problem')
            require(type(number) is int and number > 0 and isinstance(claim, str) and claim.strip(),
                    'Invalid source statement')
            statement = obj(root / 'inputs' / (pid + '.json'))
            require(statement == {'problem_id': pid, 'problem': claim}, 'Frozen statement differs from queue')
            phase = root / 'problems' / pid / '01_source' / f'p{number}/01_raw_lazy_enhanced_resolve'
            summary = obj(phase / 'summary.json')
            require(summary.get('state') == 'completed' and summary.get('terminal_checkpoint') == 'lazy_checked'
                    and summary.get('problem_id') == pid and summary.get('candidate_ids') == list(CANDIDATES),
                    'Experiment requires all four completed lazy-check candidates')
            normalized_path = phase / 'input/problem.json'
            normalized = obj(normalized_path)
            require(normalized.get('problem_id') == pid and normalized.get('problem_number') == number
                    and normalized.get('claim') == claim.strip(), 'Normalized statement differs from input')
            problem_sha = hashlib.sha256(claim.strip().encode()).hexdigest()
            source_cases_path = phase / 'phase_2_v096_cases.json'
            source_cases = obj(source_cases_path)
            frozen = obj(phase / 'phase_2_v096/manifest.json')
            require(Path(frozen.get('source_manifest_path', '')).resolve() == source_cases_path.resolve()
                    and frozen.get('source_manifest_sha256') == hashes[str(source_cases_path.resolve())],
                    'Frontend handoff manifest changed')
            banks = []
            for record in (source_cases, frozen):
                cases = record.get('cases')
                require(isinstance(cases, list) and len(cases) == 4
                        and all(isinstance(c, dict) for c in cases)
                        and {c.get('candidate_id') for c in cases} == set(CANDIDATES),
                        'Incomplete or duplicate frontend lanes')
                banks.append({c['candidate_id']: c for c in cases})
            candidates = []
            for cid in CANDIDATES:
                directory = phase / f'phase_1_raw_lazy/p{number}/candidates' / cid
                proof = directory / 'checked_proof.md'
                data = tracked(proof)
                require(data.decode('utf-8').strip(), 'Empty lazy-check proof')
                semantic_sha = text_hash(proof)
                receipt = obj(directory / 'result.json')
                for bound in [bank[cid] for bank in banks]:
                    require(bound.get('case_id') == f'{pid}.{cid}' and bound.get('problem_id') == pid
                            and Path(bound.get('proof_path', '')).resolve() == proof.resolve()
                            and Path(bound.get('problem_path', '')).resolve() == normalized_path.resolve(),
                            'Frontend case binding changed')
                require(banks[1][cid].get('proof_sha256') == semantic_sha
                        and banks[1][cid].get('problem_sha256') == problem_sha
                        and receipt.get('candidate_id') == cid
                        and Path(receipt.get('checked_proof_path', '')).resolve() == proof.resolve()
                        and receipt.get('checked_proof_sha256') == semantic_sha,
                        'Lazy-check proof differs from its completed producer')
                candidates.append({'candidate_id': cid, 'proof_path': str(proof.resolve()),
                                   'proof_file_sha256': hashlib.sha256(data).hexdigest(), 'proof_sha256': semantic_sha})
            problems.append({'problem': {'problem_id': pid, 'problem_number': number,
                                         'claim': claim.strip(), 'problem_sha256': problem_sha},
                             'candidates': candidates,
                             'provenance': {'source_run': str(root), 'checkpoint': 'lazy_checked',
                                            'source_seed_namespace': manifest.get('seed_namespace')}})
    require({p['problem']['problem_id'] for p in problems} == requested, 'Some selected problems were not found')
    verify_sources(hashes)
    return {'schema': SCHEMA, 'problems': sorted(problems, key=lambda p: p['problem']['problem_id']),
            'source_hashes': hashes, 'release_sha256': digest(RELEASE / 'release.json')}


def verify_sources(hashes):
    for name, expected in hashes.items():
        path = Path(name)
        require(path.is_file() and not path.is_symlink() and all(not p.is_symlink() for p in path.parents)
                and digest(path) == expected, f'Source changed: {path}')


def snapshot_inputs(bank, output):
    output = Path(output).resolve()
    require(not output.exists(), 'Input snapshot already exists')
    verify_sources(bank['source_hashes'])
    output.mkdir(parents=True)
    frozen = {**bank, 'problems': []}
    for row in bank['problems']:
        candidates = []
        for source in row['candidates']:
            target = output / row['problem']['problem_id'] / (source['candidate_id'] + '.md')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(source['proof_path']).read_bytes())
            require(digest(target) == source['proof_file_sha256'], 'Source drift while freezing inputs')
            candidates.append({**source, 'proof_path': str(target)})
        frozen['problems'].append({**row, 'candidates': candidates})
    verify_sources(bank['source_hashes'])
    path = output / 'manifest.json'
    write(path, frozen)
    verify_manifest(path)
    return path


def verify_manifest(path, expected_sha=None):
    path = Path(path).absolute()
    safe_file(path, path.parent)
    if expected_sha is not None:
        require(digest(path) == expected_sha, 'Input manifest hash changed')
    value = read(path)
    require(value.get('schema') == SCHEMA and value.get('release_sha256') == digest(RELEASE / 'release.json'),
            'Input manifest release/schema changed')
    require(isinstance(value.get('problems'), list) and value['problems'], 'Empty input bank')
    ids = []
    for row in value['problems']:
        problem = row['problem']
        require(set(problem) == {'problem_id', 'problem_number', 'claim', 'problem_sha256'},
                'Problem input contains unsupported fields')
        pid = identifier(problem['problem_id'])
        ids.append(pid)
        require(type(problem['problem_number']) is int and problem['problem_number'] > 0
                and isinstance(problem['claim'], str) and problem['claim'].strip()
                and hashlib.sha256(problem['claim'].strip().encode()).hexdigest() == problem['problem_sha256'],
                'Problem identity or hash changed')
        candidates = row['candidates']
        require(isinstance(candidates, list) and [c['candidate_id'] for c in candidates] == list(CANDIDATES),
                'Expected original four candidate lanes in canonical order')
        for candidate in candidates:
            require(set(candidate) == {'candidate_id', 'proof_path', 'proof_file_sha256', 'proof_sha256'},
                    'Candidate input contains unsupported fields')
            proof = safe_file(candidate['proof_path'], path.parent)
            require(proof == path.parent / pid / (candidate['candidate_id'] + '.md')
                    and digest(proof) == candidate['proof_file_sha256']
                    and text_hash(proof) == candidate['proof_sha256'] and proof.read_text().strip(),
                    'Input proof binding changed')
    require(len(ids) == len(set(ids)), 'Duplicate input problem')
    return value
