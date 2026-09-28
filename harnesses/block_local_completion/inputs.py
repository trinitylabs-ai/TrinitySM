"""Freeze raw drafts from native generation receipts without reading grades."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from harnesses.refinement_bf_ablation.inputs import (
    CANDIDATES, RELEASE, digest, identifier, read, require, safe_file,
    text_hash, verify_sources, write,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 'block-local-inputs-v1'

# Native September 14 receipts predate public-release repackaging. Preserve the
# exact original identity instead of rewriting receipts to the public digest.
HISTORICAL_SOURCE_RELEASES = {
    ('1.7.0', '56fd48b00ff2fa3fb22775b955db821911dea7a7090b4dec3f4fc0f2be8c3e8e'): {
        'backend': '0.3.290+goldfree.1',
        'freeze_sha256': 'f6d8f067d4c2a1709f64297ae7cf3470df9ddbab257c4d34d355d1cf0834d655',
        'frontend': '0.3.263',
        'release_id': 'imo-proof-pipeline-1.7.0-retry-450s-20260914',
    },
}


def load_sources(run_paths, requested=None):
    """Load four completed raw producers per selected IMO problem.

    Later lazy/refinement stages need not have completed. The raw proof must
    match its own cold-generation receipt, not a later checked/final proof.
    """
    require(run_paths, 'At least one --source-run is required')
    if requested is not None:
        require(requested and len(set(requested)) == len(requested), 'Select unique problem IDs')
        require(all(re.fullmatch(r'imo2026_p[1-6]', p) for p in requested), 'Select IMO 2026 problem IDs')
    wanted = set(requested) if requested is not None else None
    hashes, problems, roots = {}, [], set()
    for run_path in run_paths:
        root = Path(run_path).absolute()
        require(root.is_dir() and not any(p.is_symlink() for p in (root, *root.parents)),
                'Use a native, non-symlink generation/run directory')
        root = root.resolve()
        require(root not in roots, 'Duplicate source run')
        roots.add(root)

        def tracked(path):
            path = safe_file(path, root)
            data = path.read_bytes()
            observed = hashlib.sha256(data).hexdigest()
            require(str(path) not in hashes or hashes[str(path)] == observed, 'Source changed while reading')
            hashes[str(path)] = observed
            return data

        def obj(path):
            value = json.loads(tracked(path))
            require(isinstance(value, dict), 'Expected source JSON object')
            return value

        identity = obj(root / 'harness_release.json')
        version = identity.get('version')
        require(version in ('1.7.0', '1.8.0'), 'Source must be a pinned 1.7.0 or 1.8.0 native run')
        historical = HISTORICAL_SOURCE_RELEASES.get((version, identity.get('release_sha256')))
        current_identity = identity.get('release_sha256') == digest(RELEASE.parent / version / 'release.json')
        historical_identity = historical is not None and identity.get('upstream') == historical
        require(current_identity or historical_identity,
                'Source release identity changed')
        manifest = obj(root / 'manifest.json')
        require(manifest.get('schema') == 'v263_lazy_refined_to_v290_r1c2_queue_v1'
                and manifest.get('dry_run') is False, 'Expected a real native queue run')
        rows = manifest.get('problems')
        require(isinstance(rows, list) and rows, 'Empty source queue')
        ids = [identifier(row.get('problem_id')) for row in rows]
        require(len(ids) == len(set(ids)), 'Duplicate source problem')
        for row in rows:
            pid = row['problem_id']
            if wanted is not None and pid not in wanted:
                continue
            require(re.fullmatch(r'imo2026_p[1-6]', pid), 'This experiment grades IMO 2026 problems only')
            require(pid not in {p['problem']['problem_id'] for p in problems}, 'Problem occurs in multiple source runs')
            number, claim = row.get('problem_number'), row.get('problem')
            require(type(number) is int and number == int(pid[-1]) and isinstance(claim, str) and claim.strip(),
                    'Invalid statement or problem number')
            require(obj(root / 'inputs' / (pid + '.json')) == {'problem_id': pid, 'problem': claim},
                    'Frozen statement differs from native queue')
            phase = root / 'problems' / pid / '01_source' / f'p{number}/01_raw_lazy_enhanced_resolve'
            normalized = obj(phase / 'input/problem.json')
            require(normalized.get('problem_id') == pid and normalized.get('problem_number') == number
                    and normalized.get('claim') == claim.strip(), 'Normalized problem differs from native queue')
            raw_root = phase / 'phase_1_raw_lazy'
            raw_manifest = obj(raw_root / 'manifest.json')
            require(raw_manifest.get('schema') == 'cognitive-well-v097-raw-lazy-manifest-v1'
                    and raw_manifest.get('problem', {}).get('problem_id') == pid
                    and raw_manifest['problem'].get('problem_number') == number,
                    'Wrong raw-generation manifest')
            specs = raw_manifest.get('candidate_specs')
            require(isinstance(specs, list) and len(specs) == 4
                    and {s.get('candidate_id') for s in specs} == set(CANDIDATES), 'Incomplete raw portfolio')
            candidates, receipts = [], []
            for cid in CANDIDATES:
                spec = next(s for s in specs if s['candidate_id'] == cid)
                directory = raw_root / f'p{number}/candidates' / cid
                proof_path = directory / 'draft_proof.md'
                data = tracked(proof_path)
                proof = data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').strip()
                receipt = obj(directory / 'cold_result.json')
                require(proof and receipt.get('problem_id') == pid and receipt.get('problem_number') == number
                        and receipt.get('candidate_id') == cid and receipt.get('proof') == proof
                        and receipt.get('proof_sha256') == text_hash(proof_path)
                        and Path(receipt.get('proof_path', '')).resolve() == proof_path.resolve(),
                        'Raw proof differs from its producer receipt')
                require(isinstance(receipt.get('cold_generation'), dict)
                        and str(receipt['cold_generation'].get('text', '')).strip() == proof,
                        'Raw proof is not the saved cold-generation output')
                base = spec.get('seed')
                require(type(base) is int and 0 <= base <= 0xffffffff, 'Invalid source portfolio seed')
                expected_seed = int.from_bytes(hashlib.sha256(
                    f'v048:p{number}:{cid}:{base}:cold_draft'.encode()).digest()[:4], 'big') or 1
                require(receipt.get('seed') == expected_seed and receipt.get('base_portfolio_seed') == base
                        and receipt.get('temperature') == spec.get('temperature'), 'Raw generation settings changed')
                candidates.append({'candidate_id': cid, 'proof_path': str(proof_path.resolve()),
                    'proof_file_sha256': hashlib.sha256(data).hexdigest(), 'proof_sha256': text_hash(proof_path),
                    'selected_stage': 'raw'})
                receipts.append({'candidate_id': cid, 'receipt_path': str(directory / 'cold_result.json'),
                                 'raw_seed': expected_seed, 'temperature': receipt['temperature']})
            problems.append({'problem': {'problem_id': pid, 'problem_number': number, 'claim': claim.strip(),
                'problem_sha256': hashlib.sha256(claim.strip().encode()).hexdigest()}, 'candidates': candidates,
                'provenance': {'source_run': str(root), 'checkpoint': 'raw', 'source_release': identity,
                               'source_seed_namespace': manifest.get('seed_namespace'), 'producers': receipts}})
    require(problems and (wanted is None or {p['problem']['problem_id'] for p in problems} == wanted),
            'Some selected raw proofs were not found')
    verify_sources(hashes)
    return {'schema': SCHEMA, 'source_arm': 'raw', 'release_sha256': digest(RELEASE / 'release.json'),
            'source_hashes': hashes, 'problems': sorted(problems, key=lambda row: row['problem']['problem_id'])}


def snapshot(bank, output):
    output = Path(output).resolve()
    require(not output.exists(), 'Input snapshot already exists')
    verify_sources(bank['source_hashes'])
    output.mkdir(parents=True)
    frozen = {**bank, 'problems': []}
    for row in bank['problems']:
        candidates = []
        for candidate in row['candidates']:
            target = output / row['problem']['problem_id'] / (candidate['candidate_id'] + '.md')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(candidate['proof_path']).read_bytes())
            require(digest(target) == candidate['proof_file_sha256'], 'Raw proof changed while freezing')
            candidates.append({**candidate, 'proof_path': str(target)})
        frozen['problems'].append({**row, 'candidates': candidates})
    verify_sources(bank['source_hashes'])
    path = output / 'manifest.json'
    write(path, frozen)
    verify_manifest(path)
    return path


def verify_manifest(path, expected_sha=None):
    path = Path(path).absolute()
    safe_file(path, path.parent)
    require(expected_sha is None or digest(path) == expected_sha, 'Input manifest hash changed')
    bank = read(path)
    require(bank.get('schema') == SCHEMA and bank.get('source_arm') == 'raw'
            and bank.get('release_sha256') == digest(RELEASE / 'release.json'), 'Unsupported raw input bank')
    require(isinstance(bank.get('problems'), list) and bank['problems'], 'Empty raw input bank')
    ids = []
    for row in bank['problems']:
        p = row['problem']
        require(set(p) == {'problem_id', 'problem_number', 'claim', 'problem_sha256'}, 'Unexpected problem fields')
        pid = identifier(p['problem_id'])
        ids.append(pid)
        require(re.fullmatch(r'imo2026_p[1-6]', pid) and type(p['problem_number']) is int
                and p['problem_number'] == int(pid[-1]) and isinstance(p['claim'], str) and p['claim'].strip()
                and hashlib.sha256(p['claim'].strip().encode()).hexdigest() == p['problem_sha256'], 'Problem binding changed')
        require([c['candidate_id'] for c in row['candidates']] == list(CANDIDATES), 'Expected four original raw lanes')
        for candidate in row['candidates']:
            require(set(candidate) == {'candidate_id', 'proof_path', 'proof_file_sha256', 'proof_sha256', 'selected_stage'}
                    and candidate['selected_stage'] == 'raw', 'Only raw candidates are allowed')
            proof = safe_file(candidate['proof_path'], path.parent)
            require(proof == path.parent / pid / (candidate['candidate_id'] + '.md')
                    and digest(proof) == candidate['proof_file_sha256'] and text_hash(proof) == candidate['proof_sha256']
                    and proof.read_text(encoding='utf-8').strip(), 'Raw proof binding changed')
    require(len(ids) == len(set(ids)), 'Duplicate raw problem')
    return bank
