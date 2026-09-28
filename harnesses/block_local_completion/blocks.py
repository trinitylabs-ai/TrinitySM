"""Byte-bound paragraph blocks and atomic, locally authorized proof edits.

Model output never determines byte offsets or expands its own edit permission.
Each issue authorizes its named blocks plus one immediate neighbor on each side.
The same contracts apply independently to every freshly segmented proof snapshot.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = 'proof-block-bank-v1'
NEIGHBOR_COUNT = 1
_BLOCK = r'B[0-9]{4}'
_ISSUE = r'I[1-9][0-9]*'
_RESERVED = re.compile(r'</?(?:ISSUES|ISSUE|PATCHES|REPLACE)(?=[\s>])', re.IGNORECASE)
_ENV = re.compile(r'\\(begin|end)\s*\{([A-Za-z][A-Za-z0-9*_-]*)\}')
_VERBATIM = {'verbatim', 'verbatim*', 'lstlisting', 'minted'}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


class _Structure:
    def __init__(self):
        self.stack = []
        self.fence = None

    @property
    def protected(self):
        return bool(self.stack or self.fence)

    def _close(self, kind, value=''):
        _require(self.stack and self.stack[-1] == (kind, value),
                 f'Unmatched or crossed mathematical delimiter: {kind} {value}')
        self.stack.pop()

    def scan(self, line):
        if self.fence:
            char, count = self.fence
            if re.fullmatch(r'[ \t]*' + re.escape(char) + '{' + str(count) + r',}[ \t]*', line):
                self.fence = None
            return
        if not self.stack:
            fence = re.fullmatch(r'[ \t]*(`{3,}|~{3,})([^\r\n]*)', line)
            if fence:
                marker, info = fence.groups()
                # Backticks in a backtick fence's info string are ambiguous.
                _require(marker[0] != '`' or '`' not in info, 'Ambiguous code fence')
                self.fence = (marker[0], len(marker))
                return
        index = 0
        while index < len(line):
            if self.stack and self.stack[-1][0] == 'env' and self.stack[-1][1] in _VERBATIM:
                closing = '\\end{' + self.stack[-1][1] + '}'
                position = line.find(closing, index)
                if position < 0:
                    return
                self.stack.pop()
                index = position + len(closing)
                continue
            char = line[index]
            if char == '%':
                return  # An escaped percent is consumed by the backslash case.
            if char == '`':
                ticks = re.match(r'`+', line[index:]).group()
                ending = line.find(ticks, index + len(ticks))
                if ending >= 0:
                    index = ending + len(ticks)
                    continue
            if char == '\\':
                token = line[index:index + 2]
                if token in ('\\[', '\\('):
                    self.stack.append(('math', token))
                    index += 2
                    continue
                if token in ('\\]', '\\)'):
                    self._close('math', '\\[' if token == '\\]' else '\\(')
                    index += 2
                    continue
                environment = _ENV.match(line, index)
                if environment:
                    action, name = environment.groups()
                    if action == 'begin':
                        self.stack.append(('env', name))
                    else:
                        self._close('env', name)
                    index = environment.end()
                    continue
                _require(not re.match(r'\\(?:begin|end)(?=\s|\{|$)', line[index:]),
                         'Malformed LaTeX environment delimiter')
                index += min(2, len(line) - index)
                continue
            if char == '$':
                token = '$$' if line.startswith('$$', index) else '$'
                marker = ('math', token)
                if marker in self.stack:
                    self._close(*marker)
                else:
                    self.stack.append(marker)
                index += len(token)
                continue
            index += 1


def build_blocks(data: bytes) -> dict:
    """Split on blank physical lines outside balanced math/environments/fences.

    A block excludes its final line ending. Leading/trailing whitespace-only
    lines and paragraph separators remain unowned byte gaps. Internal newlines,
    including CRLF and blank lines inside a protected structure, remain intact.
    Unmatched structures or invalid UTF-8 fail before any editable bank exists.
    """
    _require(isinstance(data, bytes), 'Source proof must be bytes')
    text = data.decode('utf-8')
    _require(bool(text.strip()), 'Source proof is empty')
    state, blocks, offset = _Structure(), [], 0
    start, end = None, None

    def finish():
        nonlocal start, end
        if start is not None:
            _require(len(blocks) < 9999, 'Too many proof blocks')
            raw = data[start:end]
            blocks.append({'block_id': f'B{len(blocks) + 1:04d}', 'start': start, 'end': end,
                           'text': raw.decode('utf-8'), 'sha256': _sha(raw)})
            start = end = None

    for match in re.finditer(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$', text):
        raw_line = match.group()
        body = re.sub(r'(?:\r\n|\r|\n)$', '', raw_line)
        blank = not body.strip()
        if blank and not state.protected:
            finish()
        else:
            if start is None:
                start = offset
            state.scan(body)
            end = offset + len(body.encode('utf-8'))
        offset += len(raw_line.encode('utf-8'))
    _require(offset == len(data), 'Could not account for every source byte')
    _require(not state.protected, 'Unmatched math, environment, or fenced code in source proof')
    finish()
    _require(blocks, 'Source proof contains no content blocks')
    return {'schema': SCHEMA, 'segmentation': 'blank_lines_outside_balanced_structures-v1',
            'neighbor_count': NEIGHBOR_COUNT, 'source_sha256': _sha(data), 'source_size': len(data),
            'blocks': blocks}


def _validate_bank(bank):
    _require(isinstance(bank, dict) and bank.get('schema') == SCHEMA
             and bank.get('neighbor_count') == NEIGHBOR_COUNT, 'Unsupported proof block bank')
    _require(isinstance(bank.get('source_sha256'), str)
             and re.fullmatch('[0-9a-f]{64}', bank['source_sha256']), 'Invalid source hash')
    _require(type(bank.get('source_size')) is int and bank['source_size'] > 0, 'Invalid source size')
    blocks = bank.get('blocks')
    _require(isinstance(blocks, list) and blocks, 'Empty proof block bank')
    previous = 0
    for index, block in enumerate(blocks, 1):
        _require(isinstance(block, dict) and set(block) == {'block_id', 'start', 'end', 'text', 'sha256'}, 'Invalid block fields')
        _require(block['block_id'] == f'B{index:04d}' and isinstance(block['text'], str) and block['text'].strip(), 'Invalid block identity')
        _require(type(block['start']) is int and type(block['end']) is int
                 and previous <= block['start'] < block['end'] <= bank['source_size'], 'Invalid block byte range')
        encoded = block['text'].encode('utf-8')
        _require(len(encoded) == block['end'] - block['start'] and _sha(encoded) == block['sha256'], 'Block content hash mismatch')
        previous = block['end']
    return {block['block_id']: block for block in blocks}


def render_blocks(bank) -> str:
    _validate_bank(bank)
    pieces = [f'SOURCE_SHA256: {bank["source_sha256"]}']
    for block in bank['blocks']:
        _require(not re.search(r'</?BLOCK(?=[\s>])', block['text'], re.IGNORECASE), 'Reserved block delimiter in source text')
        pieces.append(f'<BLOCK id="{block["block_id"]}">\n{block["text"]}\n</BLOCK>')
    return '\n\n'.join(pieces)


def _document(text):
    _require(isinstance(text, str), 'Expected a text model response')
    return text[:-1] if text.endswith('\n') else text


def _ids(value, pattern, known=None):
    _require(isinstance(value, str) and re.fullmatch(pattern + '(?:,' + pattern + ')*', value), 'Malformed identifier list')
    ids = value.split(',')
    _require(len(ids) == len(set(ids)), 'Repeated identifier')
    if known is not None:
        _require(set(ids) <= set(known), 'Unknown block or issue identifier')
    return ids


def _allowed(targets, order):
    positions = {bid: index for index, bid in enumerate(order)}
    allowed = set()
    for target in targets:
        index = positions[target]
        allowed.update(order[max(0, index - 1):index + 2])
    return [bid for bid in order if bid in allowed]


def _validate_issues(issues, bank):
    blocks = _validate_bank(bank)
    order, seen = list(blocks), set()
    _require(isinstance(issues, list), 'Issues must be a list')
    for issue in issues:
        _require(isinstance(issue, dict) and set(issue) == {
            'issue_id', 'block_ids', 'description', 'allowed_block_ids', 'source_sha256'}, 'Invalid issue fields')
        _require(issue['source_sha256'] == bank['source_sha256'], 'Issue report belongs to a different proof snapshot')
        identifier = issue['issue_id']
        _require(isinstance(identifier, str) and re.fullmatch(_ISSUE, identifier) and identifier not in seen, 'Unknown or repeated issue ID')
        seen.add(identifier)
        targets = issue['block_ids']
        _require(isinstance(targets, list) and targets and all(isinstance(b, str) for b in targets), 'Empty or malformed issue blocks')
        _require(len(targets) == len(set(targets)) and set(targets) <= set(blocks), 'Unknown or repeated issue block')
        _require(targets == [bid for bid in order if bid in targets], 'Issue block IDs must be in source order')
        _require(isinstance(issue['description'], str) and issue['description'].strip()
                 and not _RESERVED.search(issue['description']), 'Empty or malformed issue description')
        _require(issue['allowed_block_ids'] == _allowed(targets, order), 'Issue neighborhood permission changed')
    return {issue['issue_id']: issue for issue in issues}


def parse_issues(text, bank) -> list:
    blocks = _validate_bank(bank)
    text = _document(text)
    if text == 'NO_ISSUES':
        return []
    _require(text.startswith('<ISSUES>\n') and text.endswith('\n</ISSUES>'), 'Expected one complete ISSUES envelope')
    body = text[len('<ISSUES>\n'):-len('\n</ISSUES>')]
    opener = re.compile(r'<ISSUE id="(' + _ISSUE + r')" blocks="(' + _BLOCK + '(?:,' + _BLOCK + r')*)">')
    cursor, result = 0, []
    while cursor < len(body):
        match = opener.match(body, cursor)
        _require(match is not None, 'Malformed ISSUE opening tag or external text')
        closing = body.find('</ISSUE>', match.end())
        _require(closing >= 0, 'Truncated ISSUE record')
        description = body[match.end():closing].strip()
        targets = _ids(match.group(2), _BLOCK, blocks)
        result.append({'issue_id': match.group(1), 'block_ids': targets, 'description': description,
                       'allowed_block_ids': _allowed(targets, list(blocks)), 'source_sha256': bank['source_sha256']})
        cursor = closing + len('</ISSUE>')
        if cursor < len(body):
            _require(body[cursor:cursor + 1] == '\n', 'ISSUE records must be separated by one LF')
            cursor += 1
            _require(cursor < len(body), 'Unexpected trailing text inside ISSUES')
    _require(result, 'Empty ISSUES envelope; use NO_ISSUES')
    _validate_issues(result, bank)
    return result


def _changed_window(original, replacement, start):
    """Smallest single byte window covering a replacement's actual changes."""
    if original == replacement:
        return None
    prefix = 0
    while prefix < min(len(original), len(replacement)) and original[prefix] == replacement[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(len(original) - prefix, len(replacement) - prefix) and original[-1 - suffix] == replacement[-1 - suffix]:
        suffix += 1
    return {'source_start': start + prefix, 'source_end': start + len(original) - suffix,
            'replacement_start': prefix, 'replacement_end': len(replacement) - suffix}


def parse_and_apply(text, bank, data, issues) -> dict:
    """Validate every edit first, then construct one new proof without file I/O."""
    _require(isinstance(data, bytes), 'Source proof must be bytes')
    _require(build_blocks(data) == bank, 'Stale source proof or altered block bank')
    blocks = _validate_bank(bank)
    known_issues = _validate_issues(issues, bank)
    text = _document(text)
    if text == 'CANNOT_REPAIR_LOCALLY':
        return {'status': 'cannot_repair_locally', 'proof_bytes': data, 'patches': [],
                'audit': {'source_sha256': _sha(data), 'result_sha256': _sha(data), 'changed': False,
                    'neighbor_count': NEIGHBOR_COUNT, 'issues': issues,
                    'unchanged_ranges': [{'start': 0, 'end': len(data), 'result_start': 0,
                                          'result_end': len(data), 'sha256': _sha(data)}]}}
    _require(known_issues, 'No issues authorize replacement blocks')
    _require(text.startswith('<PATCHES>\n') and text.endswith('\n</PATCHES>'), 'Expected one complete PATCHES envelope')
    body = text[len('<PATCHES>\n'):-len('\n</PATCHES>')]
    opener = re.compile(r'<REPLACE blocks="(' + _BLOCK + '(?:,' + _BLOCK + r')*)" issues="(' + _ISSUE + '(?:,' + _ISSUE + r')*)">\n')
    patches, used, assignment, cursor = [], set(), {}, 0
    order = list(blocks)
    while cursor < len(body):
        match = opener.match(body, cursor)
        _require(match is not None, 'Malformed REPLACE opening tag or missing framing LF')
        closing = body.find('\n</REPLACE>', match.end())
        _require(closing >= 0, 'Truncated REPLACE record or missing framing LF')
        replacement = body[match.end():closing]
        _require(replacement.strip() and not _RESERVED.search(replacement), 'Empty replacement or reserved protocol tag in proof text')
        block_ids = _ids(match.group(1), _BLOCK, blocks)
        issue_ids = _ids(match.group(2), _ISSUE, known_issues)
        _require(not used.intersection(issue_ids), 'Each issue must be covered exactly once')
        first, last = order.index(block_ids[0]), order.index(block_ids[-1])
        _require(block_ids == order[first:last + 1], 'Replacement blocks must be a contiguous range in source order')
        allowed = {bid for iid in issue_ids for bid in known_issues[iid]['allowed_block_ids']}
        _require(set(block_ids) <= allowed, 'Replacement exceeds its fixed one-neighbor issue permission')
        start, end = blocks[block_ids[0]]['start'], blocks[block_ids[-1]]['end']
        _require(not any(start < patch['end'] and patch['start'] < end for patch in patches), 'Overlapping replacements')
        raw = replacement.encode('utf-8')
        # Prevent separate patches from opening and closing a protected
        # structure around otherwise untouched intervening paragraphs.
        build_blocks(raw)
        patches.append({'block_ids': block_ids, 'issue_ids': issue_ids, 'start': start, 'end': end,
            'allowed_block_ids': [bid for bid in order if bid in allowed], 'replacement_text': replacement,
            'replacement_sha256': _sha(raw), 'original_sha256': _sha(data[start:end]),
            'changed': data[start:end] != raw, 'changed_byte_window': _changed_window(data[start:end], raw, start)})
        for iid in issue_ids:
            assignment[iid] = len(patches) - 1
        used.update(issue_ids)
        cursor = closing + len('\n</REPLACE>')
        if cursor < len(body):
            _require(body[cursor:cursor + 1] == '\n', 'REPLACE records must be separated by one LF')
            cursor += 1
            _require(cursor < len(body), 'Unexpected trailing text inside PATCHES')
    _require(patches and used == set(known_issues), 'Every reported issue must be covered exactly once')
    for i, issue in enumerate(issues):
        for other in issues[i + 1:]:
            if set(issue['block_ids']).intersection(other['block_ids']):
                _require(assignment[issue['issue_id']] == assignment[other['issue_id']],
                         'Issues sharing a target block must use one combined replacement')
    patches.sort(key=lambda patch: patch['start'])
    parts, unchanged, source_cursor, output_cursor = [], [], 0, 0
    for patch in patches:
        prefix = data[source_cursor:patch['start']]
        if prefix:
            unchanged.append({'start': source_cursor, 'end': patch['start'], 'result_start': output_cursor,
                              'result_end': output_cursor + len(prefix), 'sha256': _sha(prefix)})
            parts.append(prefix)
            output_cursor += len(prefix)
        replacement = patch['replacement_text'].encode('utf-8')
        patch['result_start'], patch['result_end'] = output_cursor, output_cursor + len(replacement)
        parts.append(replacement)
        output_cursor += len(replacement)
        source_cursor = patch['end']
    suffix = data[source_cursor:]
    if suffix:
        unchanged.append({'start': source_cursor, 'end': len(data), 'result_start': output_cursor,
                          'result_end': output_cursor + len(suffix), 'sha256': _sha(suffix)})
        parts.append(suffix)
    proof = b''.join(parts)
    # Local text edits must not leave unmatched structures that make the next
    # stage's independently bound segmentation ambiguous.
    build_blocks(proof)
    return {'status': 'patched', 'proof_bytes': proof, 'patches': patches,
            'audit': {'source_sha256': _sha(data), 'result_sha256': _sha(proof), 'changed': proof != data,
                'neighbor_count': NEIGHBOR_COUNT, 'issues': issues, 'unchanged_ranges': unchanged,
                'changed_replacements': sum(patch['changed'] for patch in patches),
                'changed_window_semantics': 'smallest single byte window per replacement; not a mathematical judgment'}}
