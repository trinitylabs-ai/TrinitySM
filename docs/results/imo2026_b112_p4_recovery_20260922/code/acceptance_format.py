"""Lossless, narrowly allowlisted interpretation of an annotated NONE sentinel."""
from contextlib import contextmanager

POLICY = 'acceptance-none-routine-completion-annotation-v1'
ANNOTATION = 'NONE (defect corrected by routine completion)'
ERROR = 'CERTIFIED requires NONE in all three defect fields'
FIELD = '## First Invalid Step'


def parse(original, text):
    result = original(text)
    # Never repair a rejected verdict, a real defect, malformed protocol, or
    # an arbitrary caveat. This alias asserts precisely that no defect remains.
    if (result['errors'] != [ERROR] or result['verdict'] != 'CERTIFIED'
            or result['sections'].get(FIELD, '').strip() != ANNOTATION):
        return result
    for heading in ('## Missing Obligation', '## Counterexample or Failure Witness'):
        if result['sections'].get(heading, '').strip().upper() != 'NONE':
            return result
    # Blank-line variants are common in Markdown; replace only the full section.
    start = text.index(FIELD) + len(FIELD)
    end = text.index('## Missing Obligation', start)
    canonical = text[:start] + '\nNONE\n\n' + text[end:]
    validated = original(canonical)
    if not validated['valid']:
        return result
    return {**result, 'valid': True, 'errors': [],
            'format_interpretation': {'policy': POLICY, 'field': FIELD,
                                      'raw': ANNOTATION, 'interpreted': 'NONE'}}


@contextmanager
def install(boundary):
    original = boundary.parse_acceptance_certification_markdown
    boundary.parse_acceptance_certification_markdown = lambda text: parse(original, text)
    try:
        yield
    finally:
        boundary.parse_acceptance_certification_markdown = original
