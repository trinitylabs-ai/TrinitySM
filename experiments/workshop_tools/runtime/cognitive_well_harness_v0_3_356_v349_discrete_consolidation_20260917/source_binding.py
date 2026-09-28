"""Exact provenance from this theorem only; no semantic retrieval or inference."""
from __future__ import annotations

import hashlib
import json
import re

POLICY = 'exact-source-spans-v2'
MAX_SPAN_CHARS = 1500
DELIMITERS = {'"':'"', "'":"'", '\u201c':'\u201d', '\u2018':'\u2019', '`':'`'}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def inventory(theorem):
    """Partition source lines into bounded exact spans, without interpreting them."""
    if not isinstance(theorem, str) or not theorem.strip():
        raise ValueError('source theorem must be nonempty text')
    spans = []
    offset = 0
    for line in theorem.splitlines(keepends=True):
        begin, end = offset, offset + len(line)
        offset = end
        while begin < end and theorem[begin].isspace():
            begin += 1
        while end > begin and theorem[end-1].isspace():
            end -= 1
        while begin < end:
            stop = min(end, begin + MAX_SPAN_CHARS)
            if stop < end:
                whitespace = [m.start() + begin for m in re.finditer(r'\s', theorem[begin:stop])]
                if whitespace:
                    stop = whitespace[-1]
            if stop == begin:
                stop = min(end, begin + MAX_SPAN_CHARS)
            excerpt = theorem[begin:stop]
            spans.append({'id':f'S{len(spans)+1:04d}', 'start':begin, 'end':stop,
                          'excerpt':excerpt, 'excerpt_sha256':sha(excerpt)})
            begin = stop
            while begin < end and theorem[begin].isspace():
                begin += 1
    return {'policy':POLICY, 'theorem_sha256':sha(theorem), 'spans':spans,
            'semantic_units':False, 'source_semantics_verified':False}


def render(record):
    rows = [json.dumps({'reference':'@source:'+span['id'], 'exact_text':span['excerpt']},
                       ensure_ascii=False) for span in record['spans']]
    return ('# Exact Source Spans\n\nUse a listed @source:S0001-style reference in each '
            'premise/retain source slot. These spans are exact source text, not interpreted '
            'hypotheses. The same span may support multiple premises; explain each '
            'correspondence in Semantic Bindings. A reference establishes provenance only.\n\n'
            '```source-spans\n'+'\n'.join(rows)+'\n```')


def _literal_match(excerpt, theorem):
    tokens = excerpt.split()
    if not tokens or len(excerpt) > MAX_SPAN_CHARS:
        return None
    # This is the existing whitespace-only exact comparison, with original offsets.
    if ' '.join(tokens) not in ' '.join(theorem.split()):
        return None
    return re.search(r'\s+'.join(re.escape(token) for token in tokens), theorem)


def annotated_reference(value):
    """Recognize an explicit ID and a delimited quote, without interpreting either."""
    for pattern in (r'(@source:S[0-9]{4,})\s+(.+)',
                    r'(.+)\s+(@source:S[0-9]{4,})'):
        match = re.fullmatch(pattern, value)
        if match is None:
            continue
        reference, quote = match.groups() if pattern.startswith('(@source') else match.groups()[::-1]
        if len(quote) >= 2 and DELIMITERS.get(quote[0]) == quote[-1] and quote[1:-1].strip():
            return reference, quote
    return None


def resolve(value, theorem, *, label):
    record = inventory(theorem)
    reference = re.fullmatch(r'@source:(S[0-9]{4,})', value)
    if reference is None and len(value) >= 2 and DELIMITERS.get(value[0]) == value[-1]:
        reference = re.fullmatch(r'@source:(S[0-9]{4,})', value[1:-1])
    span = None
    if reference:
        span = next((s for s in record['spans'] if s['id'] == reference[1]), None)
        if span is None:
            raise ValueError('unknown source reference: '+value+'; select an ID from Exact Source Spans')
        kind = 'source_id'
    else:
        match = _literal_match(value, theorem)
        kind = 'literal'
        if match is None and len(value) >= 2 and DELIMITERS.get(value[0]) == value[-1]:
            match = _literal_match(value[1:-1], theorem)
            kind = 'delimited_literal'
        if match is not None:
            span = {'start':match.start(), 'end':match.end(), 'excerpt':match[0],
                    'excerpt_sha256':sha(match[0])}
    if span is None:
        annotated = annotated_reference(value)
        if annotated:
            reference, quote = annotated
            full_text, reference_receipt = resolve(reference, theorem, label=label)
            # Both components must independently match the SAME declared span.
            # A valid ID cannot hide a paraphrase, invented quote, or other span.
            exact_text, quote_receipt = resolve(quote, full_text, label=label)
            if quote_receipt['resolution'] not in {'literal', 'delimited_literal'}:
                raise ValueError('source annotation must be an exact literal quotation')
            begin = reference_receipt['start'] + quote_receipt['start']
            end = reference_receipt['start'] + quote_receipt['end']
            return exact_text, {'label':label, 'submitted':value,
                'resolution':'source_id_with_exact_quote',
                'theorem_sha256':record['theorem_sha256'],
                'reference':reference, 'reference_span':reference_receipt,
                'quoted_literal':quote, 'start':begin, 'end':end,
                'excerpt':exact_text, 'excerpt_sha256':sha(exact_text)}
    if span is None:
        displayed = json.dumps(value[:240], ensure_ascii=False)
        raise ValueError('source excerpt not found: '+label+'; submitted '+displayed+
                         '. Use a listed @source:S0001-style ID, or copy exact original text. '
                         'Do not paraphrase or split a shared clause into invented quotations. '
                         'Source matching does not establish that the premise follows.')
    return span['excerpt'], {'label':label, 'submitted':value, 'resolution':kind,
                             'theorem_sha256':record['theorem_sha256'], **span}
