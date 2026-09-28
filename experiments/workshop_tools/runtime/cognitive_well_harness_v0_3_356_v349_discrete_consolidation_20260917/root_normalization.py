"""Normalize an unambiguous root-program container without editing mathematics.

Only this one Markdown fence is accepted. No source documents, expressions from
other attempts, or model calls are used. The ordinary root parser still checks
every field, expression, domain and resource limit after normalization.
"""
import hashlib
import re

from . import matched_expression as syntax

POLICY = 'root-container-syntax-v1'
KEY = r'(?:variable|define|interval|mode|function|expression)'
WRAPPERS = {'(real_root_classification', '(root_args', '(root-args'}


def normalize(fence):
    if not isinstance(fence, str) or len(fence) > syntax.MAX_CHARS:
        raise ValueError('root program must be bounded Markdown text')
    original = fence.strip()
    match = re.fullmatch(r'```(root-args|lisp)?\r?\n(.*?)\r?\n```', original, re.S)
    if match is None or '```' in match[2]:
        raise ValueError('expected one root-args Markdown fence; only lisp or an unlabeled fence can be normalized')
    lines = match[2].splitlines()
    edits = []
    if match[1] != 'root-args':
        edits.append({'rule': 'fence_label', 'before': '```'+(match[1] or ''), 'after': '```root-args'})
    occupied = [i for i, line in enumerate(lines) if line.strip()]
    if occupied and lines[occupied[0]].strip() in WRAPPERS:
        first, last = occupied[0], occupied[-1]
        wrapped = '\n'.join(lines[first:last+1]).strip()
        depth = 0
        for offset, char in enumerate(wrapped):
            depth += (char == '(') - (char == ')')
            if depth <= 0 and offset != len(wrapped)-1:
                raise ValueError('root wrapper closes before the end of its fields')
        if first == last or depth != 0 or not wrapped.endswith(')'):
            raise ValueError('root wrapper must be completely balanced')
        # Remove the matched outer pair only. The closing parenthesis may share
        # the last field's line; its expression remains byte-for-byte intact.
        for i, replacement in [(first, ''), (last, lines[last].rstrip()[:-1])]:
            edits.append({'rule': 'outer_wrapper', 'line': i+2, 'before': lines[i], 'after': replacement})
            lines[i] = replacement
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        value = line.strip(' \t')
        # A known field and its explicit value determine the separator. Never
        # infer values, split expressions, reorder fields or balance parentheses.
        field = re.fullmatch('('+KEY+r')(?:[ \t]*=[ \t]*|[ \t]+)(\S.*)', value)
        if field is None:
            raise ValueError('expected a root field = value; unknown records and nested wrappers are not normalized')
        replacement = field[1]+' = '+field[2]
        if replacement != line:
            edits.append({'rule': 'field_separator_or_indent', 'line': i+2, 'before': line, 'after': replacement})
            lines[i] = replacement
    # Retain canonical input byte-for-byte, including its newline convention.
    normalized = '```root-args\n'+'\n'.join(lines)+'\n```' if edits else original
    syntax.fields(normalized, 'root-args')
    sha = lambda text: hashlib.sha256(text.encode()).hexdigest()
    return normalized, {'policy': POLICY, 'applied': bool(edits), 'edits': edits,
        'original_sha256': sha(original), 'normalized_sha256': sha(normalized),
        'normalized_program': normalized}
