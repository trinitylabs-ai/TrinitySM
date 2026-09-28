"""Freeze statement and saved final-proof inputs from a published refinement archive."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from harnesses.refinement_bf_ablation.inputs import (
    CANDIDATES, RELEASE, digest, read, require, safe_file, text_hash, verify_sources, write,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE = ROOT / 'benchmarks/imo2026/results/refinement_bf_B6_selection_first_20260920_1426'
STAGES = {'raw', 'lazy_checked', 'refinement_1', 'refinement_2', 'refinement_3'}


def published_file(root, manifest, name):
    require(isinstance(name, str) and not Path(name).is_absolute(), 'Expected archive-relative path')
    path = safe_file(Path(root) / name, root)
    require(name in manifest['files'] and digest(path) == manifest['files'][name]['sha256'],
            f'Published file changed: {name}')
    return path


def load_archive(root, requested, *, source_arm='B'):
    """Read statement/proof bindings; no grade or reference files are opened.

    The comparison sidecar contains scores. Only its explicit IDs, stages, proof
    paths and hashes are extracted; none of its judgments enters model inputs.
    """
    require(source_arm in ('A', 'B'), 'Expected source arm A or B')
    root = Path(root).absolute()
    require(root.is_dir() and not any(p.is_symlink() for p in (root, *root.parents)), 'Invalid archive directory')
    root = root.resolve()
    manifest_path = safe_file(root / 'manifest.json', root)
    manifest = read(manifest_path)
    require(manifest.get('schema') == 'refinement-bf-publication-v1'
            and manifest.get('state') == 'completed_generation_and_grading'
            and manifest.get('selection_results_included') is False
            and manifest.get('post_selection_recovery_included') is False, 'Expected fixed pre-selection refinement archive')
    hashes = {str(manifest_path): digest(manifest_path)}
    def tracked(name):
        path = published_file(root, manifest, name)
        hashes[str(path)] = digest(path)
        return path
    comparison_path = tracked('comparison.json')
    comparison = read(comparison_path)
    require(comparison.get('state') == 'completed' and comparison.get('run_id') == manifest.get('run_id')
            and comparison.get('selection_results_included') is False
            and comparison.get('post_selection_recovery_included') is False, 'Comparison identity changed')
    rows = [r for r in comparison.get('lanes', []) if r.get('arm') == source_arm]
    expected = {(f'imo2026_p{p}', cid) for p in range(1, 7) for cid in CANDIDATES}
    require(len(rows) == 24 and {(r.get('problem_id'), r.get('candidate_id')) for r in rows} == expected,
            'Expected all 24 unique source-arm proofs')
    ids = sorted({r['problem_id'] for r in rows})
    selected = ids if requested is None else list(requested)
    require(selected and len(selected) == len(set(selected)) and set(selected) <= set(ids),
            'Select known, unique IMO problem IDs')
    generation = read(tracked('provenance/generation.json'))
    provenance = {r['problem_id']: r for r in generation.get('problems', [])}
    require(len(provenance) == 6 and set(provenance) == set(ids), 'Incomplete generation provenance')
    problems = []
    for pid in selected:
        require(re.fullmatch(r'imo2026_p[1-6]', pid), 'Invalid IMO problem ID')
        origin = provenance[pid]
        require(origin.get('release_identity', {}).get('release_sha256') == digest(RELEASE / 'release.json'),
                'Source release differs from the pinned implementation')
        if source_arm == 'B':
            require(origin.get('generation_state') in ('completed', 'completed_with_fallbacks'), 'B generation was not completed')
        statement = read(tracked(f'problems/{pid}.json'))
        require(statement.get('problem_id', pid) == pid, 'Problem identity changed')
        claim = statement.get('claim') or statement.get('problem')
        require(isinstance(claim, str) and claim.strip(), 'Missing statement')
        problem = {'problem_id': pid, 'problem_number': int(pid.rsplit('p', 1)[1]),
                   'claim': claim.strip(), 'problem_sha256': hashlib.sha256(claim.strip().encode()).hexdigest()}
        candidates = []
        for cid in CANDIDATES:
            row = next(r for r in rows if r['problem_id'] == pid and r['candidate_id'] == cid)
            stage = row.get('selected_stage')
            require(stage in STAGES, 'Unsupported source checkpoint')
            name = f'proofs/{source_arm}/{pid}/{cid}.md'
            require(row.get('proof_path') == name, 'Source proof path differs from lane')
            proof = tracked(name)
            require(proof.read_text(encoding='utf-8').strip() and digest(proof) == row.get('proof_file_sha256')
                    and text_hash(proof) == row.get('proof_sha256'), 'Source proof hash differs from lane')
            candidates.append({'candidate_id': cid, 'proof_path': str(proof),
                'proof_file_sha256': digest(proof), 'proof_sha256': text_hash(proof), 'selected_stage': stage})
        problems.append({'problem': problem, 'candidates': candidates})
    verify_sources(hashes)
    return {'schema': 'post-c3-inputs-v1', 'source_arm': source_arm, 'archive_root': str(root),
            'archive_manifest_sha256': hashes[str(manifest_path)], 'source_hashes': hashes,
            'release_sha256': digest(RELEASE / 'release.json'), 'problems': problems}


def snapshot(bank, output):
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
            require(digest(target) == source['proof_file_sha256'], 'Source changed while copying')
            candidates.append({**source, 'proof_path': str(target)})
        frozen['problems'].append({'problem': row['problem'], 'candidates': candidates})
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
    bank = read(path)
    require(bank.get('schema') == 'post-c3-inputs-v1' and bank.get('source_arm') in ('A', 'B')
            and bank.get('release_sha256') == digest(RELEASE / 'release.json'), 'Unsupported input manifest or release')
    require(isinstance(bank.get('archive_manifest_sha256'), str)
            and re.fullmatch('[0-9a-f]{64}', bank['archive_manifest_sha256']), 'Missing archive binding')
    require(isinstance(bank.get('problems'), list) and bank['problems'], 'Empty input bank')
    ids = []
    for row in bank['problems']:
        require(set(row) == {'problem', 'candidates'}, 'Unexpected problem fields')
        p = row['problem']
        require(set(p) == {'problem_id', 'problem_number', 'claim', 'problem_sha256'}, 'Expected statement-only problem')
        pid = p['problem_id']
        require(isinstance(pid, str) and re.fullmatch('imo2026_p[1-6]', pid), 'Invalid problem ID')
        require(type(p['problem_number']) is int and p['problem_number'] == int(pid[-1])
                and isinstance(p['claim'], str) and p['claim'].strip()
                and hashlib.sha256(p['claim'].strip().encode()).hexdigest() == p['problem_sha256'], 'Problem hash changed')
        ids.append(pid)
        candidates = row['candidates']
        require(isinstance(candidates, list) and [c['candidate_id'] for c in candidates] == list(CANDIDATES),
                'Expected four canonical candidates')
        for c in candidates:
            require(set(c) == {'candidate_id', 'proof_path', 'proof_file_sha256', 'proof_sha256', 'selected_stage'}
                    and c['selected_stage'] in STAGES, 'Invalid candidate fields or source checkpoint')
            proof = safe_file(c['proof_path'], path.parent)
            require(proof == path.parent / pid / (c['candidate_id'] + '.md') and proof.read_text(encoding='utf-8').strip()
                    and digest(proof) == c['proof_file_sha256'] and text_hash(proof) == c['proof_sha256'],
                    'Input proof binding changed')
    require(len(ids) == len(set(ids)), 'Duplicate problem IDs')
    return bank
