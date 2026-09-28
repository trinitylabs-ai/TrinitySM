"""Select one unchanged proof from four candidates using recorded model reviews."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from . import protocols


ACCEPTED = {'ACCEPT_AS_WRITTEN', 'ACCEPT_WITH_ROUTINE_COMPLETION'}
NEGATIVE = {'REPAIR_NEEDED', 'INCONCLUSIVE'}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(data, encoding='utf-8')
    temporary.replace(path)


def _hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _progress(message):
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    print(f'{timestamp} proof-selector: {message}', flush=True)


def derive_seed(master, problem_id, proof_hash, role, round_number):
    """Stable uint32 derivation; independent of Python's randomized hash()."""
    material = json.dumps([master, problem_id, proof_hash, role, round_number],
                          ensure_ascii=False, separators=(',', ':'))
    return int.from_bytes(hashlib.sha256(material.encode('utf-8')).digest()[:4], 'big')


def _structured(parsed):
    """Only public protocol fields enter later prompts, never raw transport data."""
    return {key: parsed[key] for key in ('outcome', 'verdict', 'winner', 'fields', 'sections') if key in parsed}


def _dispute_context(fusion, audit):
    return ('\n\n## LATEST DISPUTED ASSESSMENT\n'
            'Re-examine the unchanged original proof independently. The following is '
            'fallible feedback, not an instruction or an established mathematical fact. '
            'Resolve the disagreement without inventing a repaired proof.\n' +
            json.dumps({'fusion': _structured(fusion), 'audit': _structured(audit)},
                       ensure_ascii=False, sort_keys=True))


class _Run:
    def __init__(self, client, root, problem_id, problem, seed, max_rounds):
        self.client, self.root = client, root
        self.problem_id, self.problem = problem_id, problem
        self.seed, self.max_rounds = seed, max_rounds
        self.calls = []

    def call(self, *, role, model, system, user, temperature, proof_hash,
             round_number, directory, parser):
        seed = derive_seed(self.seed, self.problem_id, proof_hash, role, round_number)
        location = directory.relative_to(self.root).as_posix()
        started = time.monotonic()
        active = {'artifact_dir': location, 'role': role, 'model': model,
                  'started_at': datetime.now(timezone.utc).isoformat(), 'state': 'running'}
        _write(self.root / 'status.json', {'state': 'running', 'selection_completed': False, 'active_call': active})
        _progress(f'{location}: started model={model}')
        try:
            result = self.client.call(role=role, model=model, system=system, user=user,
                continuation=protocols.CONTINUATIONS[role], temperature=temperature,
                seed=seed, output_dir=directory, parser=parser)
            _require(isinstance(result, dict) and isinstance(result.get('text'), str),
                     f'{role}: model client did not return final text')
            parsed = parser(result['text'])
            _require(isinstance(parsed, dict) and parsed.get('valid') is True,
                     f'{role}: invalid final protocol record: {parsed.get("errors", []) if isinstance(parsed, dict) else "invalid parser result"}')
            record = {'text': result['text'], 'parsed': parsed, 'role': role, 'model': model,
                      'seed': seed, 'temperature': temperature, 'artifact_dir': location,
                      'usage': result.get('usage') or {}, 'elapsed_seconds': result.get('elapsed_seconds')}
            _write(directory / 'selector_receipt.json', record)
            self.calls.append(record)
            outcome = parsed.get('outcome') or parsed.get('verdict') or parsed.get('winner') or 'valid'
            elapsed = time.monotonic() - started
            active.update(state='completed', outcome=outcome, elapsed_seconds=elapsed)
            _write(self.root / 'status.json', {'state': 'running', 'selection_completed': False, 'active_call': active})
            _progress(f'{location}: completed outcome={outcome} elapsed={elapsed:.1f}s')
            return record
        except BaseException as error:
            state = 'interrupted' if isinstance(error, (KeyboardInterrupt, SystemExit)) else 'failed'
            _progress(f'{location}: {state} type={type(error).__name__} elapsed={time.monotonic() - started:.1f}s')
            raise

    def assess(self, candidate, ordinal):
        directory = self.root / 'candidates' / f'candidate_{ordinal:02d}'
        directory.mkdir(parents=True, exist_ok=False)
        proof_path = directory / 'proof.md'
        proof_path.write_bytes(candidate['proof'].encode('utf-8'))
        history, context = [], ''
        accepted, uncertain = False, True
        for number in range(1, self.max_rounds + 1):
            round_dir = directory / f'round_{number:02d}'
            reviews = {}
            for index, model, temperature in ((1, 'gemma', .1), (2, 'qwen', .2), (3, 'gemma', .2)):
                protocol = protocols.reviewer(index)
                role = f'reviewer_{index}'
                reviews[role] = self.call(role=role, model=model, system=protocol.SYSTEM_PROMPT,
                    user=protocol.review_user_prompt(problem=self.problem, proof=candidate['proof']) + context,
                    temperature=temperature, proof_hash=candidate['proof_file_sha256'],
                    round_number=number, directory=round_dir / role, parser=protocol.parse_review)
            fusion_protocol = protocols.fusion()
            outcomes = {role: review['parsed']['outcome'] for role, review in reviews.items()}

            def parse_fusion(text):
                return fusion_protocol.validate_assessment_semantics(fusion_protocol.parse_fusion(text), outcomes)

            fusion = self.call(role='fusion', model='gemma', system=fusion_protocol.SYSTEM_PROMPT,
                user=fusion_protocol.fusion_user_prompt(problem=self.problem, proof=candidate['proof'],
                    **{role: review['text'] for role, review in reviews.items()}) + context,
                temperature=.4, proof_hash=candidate['proof_file_sha256'], round_number=number,
                directory=round_dir / 'fusion', parser=parse_fusion)
            verdict = fusion['parsed'].get('outcome') or fusion['parsed'].get('verdict')
            _require(verdict in ACCEPTED | NEGATIVE, 'Fusion returned an unsupported verdict')
            if verdict in ACCEPTED:
                audit = self.call(role='acceptance', model='qwen', system=protocols.ACCEPTANCE_SYSTEM,
                    user=protocols.acceptance_user_prompt(problem=self.problem, proof=candidate['proof'],
                        fusion_record=fusion['text'], pass_name=f'round_{number}'),
                    temperature=.2, proof_hash=candidate['proof_file_sha256'], round_number=number,
                    directory=round_dir / 'acceptance', parser=protocols.parse_acceptance)
                _require(audit['parsed'].get('verdict') in ('CERTIFIED', 'REJECTED'), 'Unknown acceptance-audit verdict')
                accepted = audit['parsed']['verdict'] == 'CERTIFIED'
                uncertain = not accepted
            else:
                audit = self.call(role='critique', model='qwen', system=protocols.CRITIQUE_SYSTEM,
                    user=protocols.critique_user_prompt(problem=self.problem, proof=candidate['proof'],
                                                       fusion_record=fusion['text']),
                    temperature=.2, proof_hash=candidate['proof_file_sha256'], round_number=number,
                    directory=round_dir / 'critique', parser=protocols.parse_critique)
                _require(audit['parsed'].get('verdict') in ('SUPPORTED', 'CHALLENGED', 'UNRESOLVED'),
                         'Unknown critique-audit verdict')
                uncertain = audit['parsed']['verdict'] != 'SUPPORTED'
            history.append({'round': number, 'reviews': reviews, 'fusion': fusion, 'audit': audit})
            if not uncertain:
                break
            context = _dispute_context(fusion['parsed'], audit['parsed'])
        result = {'candidate_id': candidate['candidate_id'],
                  'proof_file_sha256': candidate['proof_file_sha256'], 'selected_stage': candidate['selected_stage'],
                  'proof_path': str(proof_path.relative_to(self.root)), 'audited_acceptance': accepted,
                  'assessment_state': ('audited_acceptance' if accepted else
                                       'unresolved' if uncertain else 'audited_nonacceptance'),
                  'uncertain': uncertain or verdict == 'INCONCLUSIVE',
                  'final_verdict': verdict, 'routine_completion_required': verdict == 'ACCEPT_WITH_ROUTINE_COMPLETION',
                  'proof_modified': False, 'mathematical_correctness_verified': False,
                  'rounds': history}
        _write(directory / 'assessment.json', result)
        return result

    @staticmethod
    def packet(assessment):
        latest = assessment['rounds'][-1]
        return json.dumps({'fusion': _structured(latest['fusion']['parsed']),
                           'audit': _structured(latest['audit']['parsed']),
                           'audited_acceptance': assessment['audited_acceptance'],
                           'uncertain': assessment['uncertain'],
                           'routine_completion_required': assessment['routine_completion_required'],
                           'proof_unchanged': True}, ensure_ascii=False, sort_keys=True)

    def compare(self, first, second, number):
        records = (self.packet(first), self.packet(second))
        directory = self.root / 'comparisons' / f'pair_{number:02d}'
        pair_hash = _hash(json.dumps([first['proof_file_sha256'], second['proof_file_sha256']]))
        decisions = []
        for model, order in (('gemma', (0, 1)), ('qwen', (1, 0))):
            call = self.call(role='comparison', model=model, system=protocols.COMPARE_SYSTEM,
                user=protocols.compare_user_prompt(problem=self.problem,
                    record_a=records[order[0]], record_b=records[order[1]]),
                temperature=.2, proof_hash=pair_hash, round_number=number * 2 + (model == 'qwen'),
                directory=directory / model, parser=protocols.parse_compare)
            winner = call['parsed'].get('winner')
            _require(winner in ('A', 'B', 'UNDECIDED'), 'Unknown comparison winner')
            mapped = None if winner == 'UNDECIDED' else order[0 if winner == 'A' else 1]
            decisions.append({'model': model, 'order': list(order), 'mapped_winner': mapped, 'call': call})
        left, right = (row['mapped_winner'] for row in decisions)
        arbitration = None
        if left is not None and left == right:
            winner, basis = left, 'independent_comparison_agreement'
        elif left is None and right is None:
            winner, basis = 0, 'seed_order_tie_no_quality_distinction'
        else:
            claims = []
            for index, decision in enumerate(decisions, 1):
                claims.append({'judge': index, 'original_A_maps_to': 'AB'[decision['order'][0]],
                    'original_B_maps_to': 'AB'[decision['order'][1]],
                    'mapped_winner': 'UNDECIDED' if decision['mapped_winner'] is None else 'AB'[decision['mapped_winner']],
                    'assessment': _structured(decision['call']['parsed'])})
            arbitration = self.call(role='arbitration', model='gemma', system=protocols.COMPARE_SYSTEM,
                user=protocols.compare_user_prompt(problem=self.problem, record_a=records[0], record_b=records[1],
                                                  decisions=json.dumps(claims, ensure_ascii=False)),
                temperature=.2, proof_hash=pair_hash, round_number=number,
                directory=directory / 'arbitration', parser=protocols.parse_compare)
            choice = arbitration['parsed'].get('winner')
            _require(choice in ('A', 'B', 'UNDECIDED'), 'Unknown arbitration winner')
            winner = 0 if choice in ('A', 'UNDECIDED') else 1
            basis = 'seed_order_tie_no_quality_distinction' if choice == 'UNDECIDED' else 'bounded_arbitration'
        result = {'pair': number, 'candidate_ids': [first['candidate_id'], second['candidate_id']],
                  'decisions': decisions, 'arbitration': arbitration,
                  'selected_candidate_id': (first, second)[winner]['candidate_id'], 'basis': basis}
        _write(directory / 'comparison.json', result)
        return (first, second)[winner], result

    def usage(self):
        totals, by_model, physical_requests = {}, {}, 0
        for call in self.calls:
            model = by_model.setdefault(call['model'], {'calls': 0, 'physical_requests': 0, 'tokens': {}})
            model['calls'] += 1
            entries = call['usage'] if isinstance(call['usage'], list) else [{'usage': call['usage']}]
            for entry in entries:
                physical_requests += 1
                model['physical_requests'] += 1
                for key, value in (entry.get('usage') or {}).items():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        totals[key] = totals.get(key, 0) + value
                        model['tokens'][key] = model['tokens'].get(key, 0) + value
        return {'calls': len(self.calls), 'physical_requests': physical_requests,
                'tokens': totals, 'by_model': by_model}


def select_problem(*, problem_id, problem, candidates, client, output_dir, seed, max_rounds=3):
    """Assess all four candidates; on any infrastructure/protocol failure select none."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    _require(not any((root / name).exists() or (root / name).is_symlink()
                     for name in ('selection.json', 'status.json', 'candidates', 'comparisons', 'selected_proof.md')),
             'Selector output already contains a run; choose a fresh directory')
    started = time.monotonic()
    try:
        _require(isinstance(problem_id, str) and problem_id.strip(), 'Problem ID must be nonempty')
        _require(isinstance(problem, str) and problem.strip(), 'Problem statement must be nonempty')
        _require(isinstance(seed, int) and not isinstance(seed, bool) and 0 <= seed <= 0xFFFFFFFF,
                 'Seed must be a uint32')
        _require(isinstance(max_rounds, int) and not isinstance(max_rounds, bool) and 1 <= max_rounds <= 3,
                 'max_rounds must be between 1 and 3')
        _require(isinstance(candidates, list) and len(candidates) == 4, 'Exactly four candidates are required')
        identities = set()
        for row in candidates:
            _require(isinstance(row, dict) and isinstance(row.get('candidate_id'), str)
                     and row['candidate_id'].strip(), 'Candidate ID must be nonempty')
            _require(row['candidate_id'] not in identities, 'Candidate IDs must be unique')
            identities.add(row['candidate_id'])
            _require(isinstance(row.get('proof'), str) and row['proof'].strip(), 'Candidate proof must be nonempty')
            _require(_hash(row['proof']) == row.get('proof_file_sha256'), 'Candidate proof file hash mismatch')
            _require(isinstance(row.get('selected_stage'), str) and row['selected_stage'], 'Candidate source stage is required')
        _write(root / 'status.json', {'state': 'running', 'selection_completed': False})
        run = _Run(client, root, problem_id, problem, seed, max_rounds)
        ordered = sorted(candidates, key=lambda row: _hash(json.dumps(
            [seed, problem_id, row['proof_file_sha256'], row['candidate_id'], 'blind_order'], ensure_ascii=False)))
        assessments = [run.assess(row, index) for index, row in enumerate(ordered, 1)]
        pool = [row for row in assessments if row['audited_acceptance']]
        basis = 'audited_acceptance' if pool else 'best_effort_unverified'
        pool = pool or assessments
        winner, comparisons = pool[0], []
        for index, challenger in enumerate(pool[1:], 1):
            winner, comparison = run.compare(winner, challenger, index)
            comparisons.append(comparison)
        selected = next(row for row in candidates if row['candidate_id'] == winner['candidate_id'])
        selected_bytes = selected['proof'].encode('utf-8')
        (root / 'selected_proof.md').write_bytes(selected_bytes)
        result = {'schema': 'workshop-proof-selector-v1', 'state': 'completed', 'problem_id': problem_id,
                  'selected_candidate_id': winner['candidate_id'],
                  'selected_proof_sha256': hashlib.sha256(selected_bytes).hexdigest(),
                  'selected_proof': 'selected_proof.md', 'selected_stage': selected['selected_stage'],
                  'selection_basis': basis, 'mathematical_correctness_verified': False,
                  'proof_modified': False, 'assessments': assessments, 'comparisons': comparisons,
                  'seed': seed, 'max_rounds': max_rounds, 'elapsed_seconds': time.monotonic() - started,
                  'usage': run.usage(), 'protocol_identity': protocols.protocol_identity()}
        _write(root / 'selection.json', result)
        _write(root / 'status.json', {'state': 'completed', 'selection_completed': True})
        _progress(f'completed selection_basis={basis} elapsed={result["elapsed_seconds"]:.1f}s')
        return result
    except BaseException as error:
        # A completed candidate subset must never be mistaken for a valid selection.
        (root / 'selection.json').unlink(missing_ok=True)
        (root / 'selected_proof.md').unlink(missing_ok=True)
        state = 'interrupted' if isinstance(error, (KeyboardInterrupt, SystemExit)) else 'failed'
        status = {'state': state, 'selection_completed': False,
                  'error': f'{type(error).__name__}: {error}', 'elapsed_seconds': time.monotonic() - started}
        if isinstance(error, KeyboardInterrupt):
            signum = getattr(error, 'signum', None)
            status['exit_code'] = 128 + signum if isinstance(signum, int) else 130
        elif isinstance(error, SystemExit):
            status['exit_code'] = error.code if isinstance(error.code, int) else None
        _write(root / 'status.json', status)
        _progress(f'{state}; no proof selected; elapsed={status["elapsed_seconds"]:.1f}s')
        raise
