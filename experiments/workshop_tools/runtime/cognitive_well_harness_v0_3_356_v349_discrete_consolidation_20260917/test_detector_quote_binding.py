"""Source binding must tolerate formatting without selecting different mathematics."""
import pytest

from .synthesis_core import tool_purpose as purpose
from .synthesis_core.contracts import EvidenceBundle, TaskInputs


def bind(source, quote):
    claim = 'Derive the displayed identity.'
    detection = f'''# Decision
CALL_TOOL
# Load-Bearing Gap
The displayed identity needs a derivation.
# Trigger Evidence
"{quote}"
# Evidence Task
CERTIFY_DERIVATION
# Desired Exact Fact
{claim}
# Downstream Obligation
Complete the proof.'''
    matcher = f'''# Decision
CALL_TOOL
# Operation
rational_identity
# Immutable Claim
{claim}
# Fit Rationale
The task is an exact algebraic identity.'''
    task = TaskInputs('synthetic', 'Prove the identity.', source,
        {purpose.DETECTION_DOCUMENT: detection, purpose.MATCHER_DOCUMENT: matcher})
    evidence = EvidenceBundle('synthetic', 'VERIFIED_SUPPORT', 'Lemma.', {},
        {'operation': 'rational_identity', 'claim': claim}, {})
    return purpose.explicit_update_source(task, evidence)


def selected(marked):
    return marked.split(purpose.EXPLICIT_BEGIN + '\n', 1)[1].split(
        '\n' + purpose.EXPLICIT_END, 1)[0]


@pytest.mark.parametrize('source,quote,span', [
    ('Before. The points $U$ and $V$ determine $UV$. After.',
     'The points U and V determine UV.', 'The points $U$ and $V$ determine $UV$.'),
    ('Before. The identity x+y=1 follows. After.',
     'The identity $x+y=1$ follows.', 'The identity x+y=1 follows.'),
    ('Before. $$\nx+y=1\n$$ After.', '$x+y=1$', '$$\nx+y=1\n$$'),
    ('Before. $x+y=1$ After.', '$$x+y=1$$', '$x+y=1$'),
    ('Before. The points $U$\n and $V$ determine $UV$. After.',
     'The points U and V determine UV.', 'The points $U$\n and $V$ determine $UV$.'),
    ('Before. λ = $x+y$. After.', 'λ = x+y.', 'λ = $x+y$.'),
])
def test_formatting_fallback_selects_original_bytes(source, quote, span):
    marked = bind(source, quote)
    assert selected(marked) == span
    assert marked.replace(purpose.EXPLICIT_BEGIN + '\n', '').replace(
        '\n' + purpose.EXPLICIT_END, '') == source


@pytest.mark.parametrize('source,quote', [
    ('The identity $x+y=1$ follows.', 'The identity x-y=1 follows.'),
    ('The point $U$ determines $V$.', 'The point U determines W.'),
    ('The identity $x+y=1$ follows. The identity $$x+y=1$$ follows.',
     'The identity x+y=1 follows.'),
    ('aaaa', 'aaa'),  # Overlapping exact occurrences remain ambiguous.
    ('Costs $5 and $7 today.', 'Costs 5 and 7 today.'),
    (r'Costs \$5 today.', 'Costs 5 today.'),
    ('The identity $x+y=1 follows.', 'The identity x+y=1 follows.'),
    ('Code `$x+y=1$` is literal.', 'Code `x+y=1` is literal.'),
    ('Code ```\n$x+y=1$\n``` is literal.', 'Code ```\nx+y=1\n``` is literal.'),
    ('Code ~~~\n$x+y=1$\n~~~ is literal.', 'Code ~~~\nx+y=1\n~~~ is literal.'),
    ('Let $x$y equal 1.', 'Let xy equal 1.'),
    ('The identity $x+y=1$ follows.', 'The identity x+y'),  # Partial math span.
    ('Nothing to match.', ''),
    ('The identity $x+y=1$$ follows.', 'The identity x+y=1 follows.'),
    ('The identity $$$x+y=1$$$ follows.', 'The identity x+y=1 follows.'),
])
def test_nonformatting_or_ambiguous_changes_fail_closed(source, quote):
    with pytest.raises(ValueError):
        bind(source, quote)


def test_existing_exact_match_has_priority_and_original_source_is_retained():
    source = 'Use x+y=1 here. Elsewhere use $x+y=1$.'
    assert selected(bind(source, 'Use x+y=1 here.')) == 'Use x+y=1 here.'
    assert selected(bind('A   fact\n follows.', 'A fact follows.')) == 'A   fact\n follows.'


def test_reserved_prompt_markers_are_rejected():
    with pytest.raises(ValueError, match='reserved markers'):
        bind(purpose.EXPLICIT_BEGIN + ' The identity follows.', 'The identity follows.')
