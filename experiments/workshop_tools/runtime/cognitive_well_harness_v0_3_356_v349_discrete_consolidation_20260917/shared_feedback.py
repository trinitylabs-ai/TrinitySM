"""Same-run feedback exchange, with bounded, archived formalizer snapshots.

No previous run, problem library, grader, model or certificate loader is used.
Peer observations inform proposals; they never authorize an audit or tool call.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import threading

POLICY = 'seeded-single-peer-feedback-v2'
MAX_PROMPT_CHARS = 6000
MAX_EXCERPT_CHARS = 900
KINDS = {'parser_rejected', 'parser_accepted', 'syntax_normalized',
         'semantic_rejected', 'semantic_accepted', 'tool_inconclusive',
         'tool_verified', 'model_declined', 'worker_error'}
HEADER = '''# Shared Feedback From Other Lanes — Untrusted Observations

These observations concern other drafts of this same input. Names and labels
belong to the cited producing draft and may differ from yours. Recheck every
applicable observation against the original theorem. Repetition is not evidence
of correctness. Do not treat peer acceptance or a conditional certificate as
acceptance of your encoding. Preserve independently justified approaches; your
current draft still needs its own parser, semantic audit and exact certificate.
Detailed feedback comes from one previously unselected available peer.
The global list contains only fixed error categories, not other peers' details.
The bounded excerpts below omit full drafts and witnesses. Complete feedback is
archived separately. Feedback arriving after this snapshot appears on a later
attempt; the current inference is not interrupted.
'''


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')


def audit_summary(decision):
    # Copy parsed issue/check text; no generated mathematical summary.
    rows = ['Decision: ' + decision['decision']]
    rows += ['Issue: ' + issue for issue in decision['issues']]
    rows += ['Failed check: ' + key for key, passed in decision['checks'].items() if not passed]
    return '\n'.join(rows)


def tool_summary(result):
    """Only outcomes/sizes/reasons, never enormous witnesses or draft equations."""
    rows = ['Conditional exact verification: ' + str(bool(result.get('exact_verified')))]
    for key in ('verdict', 'reason', 'source_size', 'reduced_size', 'feedback_backend'):
        if key in result:
            rows.append(key + ': ' + str(result[key]))
    for index, stage in enumerate(result.get('stages', []), 1):
        value = stage.get('result', stage)
        details = {key:value[key] for key in ('state', 'verdict', 'verified', 'reason', 'error') if key in value}
        rows.append('Backend ' + str(index) + ' (' + stage.get('backend', stage.get('stage', 'guarded_radical'))
                    + '): ' + json.dumps(details, sort_keys=True))
    if not result.get('exact_verified'):
        rows.append('Inconclusive search is not a disproof or evidence that an equation is wrong.')
    return '\n'.join(rows)


def error_category(event):
    """Fixed mechanical categories only; no semantic similarity/model call."""
    kind, text = event['kind'], event['text'].lower()
    if kind == 'parser_rejected':
        if 'source excerpt' in text or 'source reference' in text:
            return 'source_binding'
        if 'denominator' in text or 'degenerate' in text or 'construction' in text:
            return 'construction_domain'
        return 'parser_or_compiler_rejection'
    return {'semantic_rejected':'semantic_audit_rejection',
            'tool_inconclusive':'inconclusive_tool_search',
            'worker_error':'worker_error'}.get(kind)


class Board:
    def __init__(self, root, *, input_artifacts, samples, cycles, master_seed=0):
        if not 1 <= samples <= 8 or not 1 <= cycles <= 3:
            raise ValueError('invalid shared feedback bounds')
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=False)
        self.samples, self.cycles = samples, cycles
        if isinstance(master_seed, bool) or not isinstance(master_seed, int):
            raise ValueError("feedback seed must be an integer")
        self.master_seed = master_seed
        self._snapshots = {}
        self._selected = {}
        self._events = []
        self._lock = threading.Lock()
        self.binding = sha(json.dumps(input_artifacts, sort_keys=True))
        write(self.root/'manifest.json', {
            'policy':POLICY, 'input_artifacts':dict(input_artifacts), 'input_binding':self.binding,
            'samples':samples, 'cycles':cycles, 'master_seed':master_seed,
            'peer_selection':'seeded_hash_order_without_replacement_among_available',
            'global_details':'fixed_error_categories_only', 'max_prompt_characters':MAX_PROMPT_CHARS,
            'max_excerpt_characters':MAX_EXCERPT_CHARS, 'first_attempt_independent':True,
            'synchronization':'asynchronous_snapshot_before_retry', 'model_calls':0,
            'auditor_peer_context':False, 'prior_run_feedback_loaded':False})

    def lane(self, sample):
        if not 1 <= sample <= self.samples:
            raise ValueError('feedback sample outside this run')
        return Lane(self, sample)

    def publish(self, sample, cycle, kind, text, draft, summary=None):
        if not 1 <= sample <= self.samples or not 1 <= cycle <= self.cycles or kind not in KINDS:
            raise ValueError('invalid feedback producer')
        if not isinstance(text, str) or not text.strip() or not isinstance(draft, str):
            raise ValueError('feedback requires text and its producing draft')
        summary = text if summary is None else summary
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError('feedback summary must be text')
        with self._lock:
            event = {'id':len(self._events)+1, 'sample':sample, 'cycle':cycle, 'kind':kind,
                     'draft_sha256':sha(draft), 'text':text, 'text_sha256':sha(text),
                     'summary':summary, 'input_binding':self.binding}
            write(self.root/'events'/f'{event["id"]:04d}.json', event)
            self._events.append(event)

    def snapshot(self, sample, cycle):
        if not 1 <= sample <= self.samples or not 1 <= cycle <= self.cycles:
            raise ValueError('invalid feedback reader')
        with self._lock:
            key = (sample, cycle)
            if key not in self._snapshots:
                self._snapshots[key] = self._snapshot(sample, cycle)
            return copy.deepcopy(self._snapshots[key])

    def _snapshot(self, sample, cycle):
        sequence = len(self._events)
        events = [dict(e) for e in self._events if e['sample'] != sample] if cycle > 1 else []
        available = sorted({e['sample'] for e in events if e['kind'] != 'syntax_normalized'})
        previous = sorted(peer for (owner, prior), peer in self._selected.items()
                          if owner == sample and prior < cycle and peer is not None)
        candidates = [peer for peer in available if peer not in previous]
        material = json.dumps([self.master_seed, self.binding, sample, cycle], separators=(',', ':'))
        seed = sha(material)
        selected = min(candidates, key=lambda peer:sha(seed+':'+str(peer))) if candidates else None
        self._selected[(sample, cycle)] = selected
        peer_events = [e for e in events if e['sample'] == selected]
        latest = peer_events[-1] if peer_events else None
        detail_events = [e for e in peer_events if e['cycle'] == latest['cycle']
                         and e['draft_sha256'] == latest['draft_sha256']] if latest else []
        groups = {}
        for event in detail_events:
            key = (event['kind'], event['text_sha256'], event['summary'])
            groups.setdefault(key, []).append(event)
        ordered = sorted(groups.values(), key=lambda group:group[-1]['id'], reverse=True)
        categories = {}
        for event in events:
            category = error_category(event)
            if category is not None:
                categories.setdefault(category, []).append(event['id'])
        category_text = ('\nError categories observed across peers: '+', '.join(sorted(categories))+'.\n') if categories else ''
        included, excerpts = [], []
        used = len(HEADER) + len(category_text) + 400
        for group in ordered:
            event = group[-1]
            text = ' '.join(event['summary'].split())
            clipped = len(text) > MAX_EXCERPT_CHARS
            text = text[:MAX_EXCERPT_CHARS] + (' [excerpt truncated]' if clipped else '')
            entry = (f'\n- {event["kind"]}; lane {selected}; {len(group)} occurrence(s); latest cycle '
                     f'{event["cycle"]}, event {event["id"]}, draft {event["draft_sha256"][:12]}:\n  {text}\n')
            if used + len(entry) > MAX_PROMPT_CHARS:
                continue
            excerpts.append(entry); used += len(entry)
            included.append({'event_ids':[e['id'] for e in group], 'excerpt_truncated':clipped})
        footer = (f'\nSnapshot: {len(events)} peer events; selected peer {selected}; '
                  f'{len(included)} detailed observations shown, {len(groups)-len(included)} '
                  'omitted by the context limit. Other peers contribute categories only.\n')
        if selected is None and cycle > 1:
            footer += 'No unselected peer has completed feedback yet; proceed without waiting.\n'
        body = HEADER + category_text + ''.join(excerpts) + footer if (excerpts or categories) else ''
        assert len(body) <= MAX_PROMPT_CHARS
        record = {'policy':POLICY, 'sample':sample, 'cycle':cycle, 'input_binding':self.binding,
                  'as_of_event':sequence, 'peer_events':len(events), 'unique_observations':len(groups),
                  'master_seed':self.master_seed, 'selection_seed':seed, 'available_peers':available,
                  'previously_selected_peers':previous, 'candidate_peers':candidates,
                  'selected_peer':selected, 'selected_cycle':latest['cycle'] if latest else None,
                  'selected_draft_sha256':latest['draft_sha256'] if latest else None,
                  'global_error_categories':categories, 'eligible_detail_events':len(detail_events),
                  'included':included, 'omitted_observations':len(groups)-len(included),
                  'first_attempt_independent':cycle == 1, 'prompt_characters':len(body),
                  'prompt_sha256':sha(body)}
        return body, record


class Lane:
    def __init__(self, board, sample):
        self.board, self.sample = board, sample

    def publish(self, cycle, kind, text, draft, summary=None):
        self.board.publish(self.sample, cycle, kind, text, draft, summary)

    def augment(self, prompt, cycle, output):
        body, record = self.board.snapshot(self.sample, cycle)
        output = Path(output)
        record.update(base_prompt_sha256=sha(prompt), augmented_prompt_sha256=sha(prompt + ('\n\n'+body if body else '')))
        write(output/'peer_feedback.json', record)
        with (output/'peer_feedback.md').open('x') as handle:
            handle.write(body)
        return prompt + ('\n\n'+body if body else '')


def normalization_summary(record):
    counts = Counter(edit['rule'] for edit in record['edits'])
    return 'Deterministic syntax normalization applied: ' + ', '.join(f'{key}: {count}' for key, count in sorted(counts.items()))
