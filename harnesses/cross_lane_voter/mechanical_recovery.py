"""Replayable mechanical repairs of comparison formats; no vote inference."""
import hashlib
import re
from functools import wraps

POLICY = 'unique-final-comparison-unanimous-explicit-winners-v1'
PREFIX_POLICY = 'explicit-winner-proof-prefix-v1'
CHECKS_POLICY = 'missing-checks-heading-existing-inline-line-citations-v2'
PROSE_CHECKS_POLICY = 'missing-checks-heading-existing-prose-line-citations-v3'


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def with_explicit_winner_prefix(parser):
    """Accept one literal Proof A/B alias around an otherwise unchanged parser.

    The public controller uses this when reading frozen 1.12.0 responses.
    No inference or saved response is changed, and no other recovery is added.
    """
    if getattr(parser, 'explicit_winner_prefix', False):
        return parser

    @wraps(parser)
    def parse(text):
        try:
            return parser(text)
        except ValueError as error:
            if str(error) != 'Expected exactly one unambiguous Winner: A or B':
                raise
        normalized, repair = recover_comparison(text, parser)
        parsed = parser(normalized)
        parsed['response_sha256'] = sha(text)
        parsed['mechanical_recovery'] = repair
        return parsed

    parse.explicit_winner_prefix = True
    return parse


def recover_comparison(text, strict_parse):
    """Apply one documented mechanical format recovery, without inferring votes."""
    try:
        strict_parse(text)
    except ValueError as error:
        if re.fullmatch(r'Missing Decisive checks in proof [ab]', str(error)):
            return restore_checks_label(text, strict_parse)
        if str(error) != 'Expected exactly one unambiguous Winner: A or B':
            return recover_final_comparison(text, strict_parse)
        original_error = str(error)
    else:
        return text, None
    pattern = r'^(?P<prefix>[ \t]*(?:[-*][ \t]*)?Winner[ \t]*:[ \t]*)Proof[ \t]+(?P<label>[AB])(?P<suffix>[ \t]*\.?[ \t]*\r?)$'
    matches = list(re.finditer(pattern, text, re.M | re.I))
    if len(matches) != 1:
        raise ValueError(original_error)
    match = matches[0]
    start, end = match.end('prefix'), match.start('label')
    normalized = text[:start] + text[end:]
    parsed = strict_parse(normalized)  # Reject any competing winner or missing field.
    return normalized, {
        'policy': PREFIX_POLICY, 'operation': 'remove_literal_Proof_prefix_from_single_explicit_winner',
        'original_error': original_error, 'original_response_sha256': sha(text),
        'normalized_response_sha256': sha(normalized), 'removed_start_char': start,
        'removed_end_char': end, 'removed_text': text[start:end],
        'winner_label': parsed['winner_label'], 'model_calls': 0, 'new_mathematical_text': False,
    }


def restore_checks_label(text, strict_parse):
    """Recover one omitted checks label from existing bullets or inline prose."""
    try:
        return restore_bulleted_checks_label(text, strict_parse)
    except ValueError:
        return restore_prose_checks_label(text, strict_parse)


def restore_bulleted_checks_label(text, strict_parse):
    """Copy existing line-cited qualifications under one omitted checks heading.

    This is the published v2 rule, shared by recovery and evidence replay.
    Historical frozen v1 implementations are left byte-for-byte unchanged.
    """
    try:
        strict_parse(text)
    except ValueError as error:
        match = re.fullmatch(r'Missing Decisive checks in (proof [ab])', str(error))
        if not match:
            raise
        section = match[1]
    else:
        return text, None

    def require(ok, reason):
        if not ok:
            raise ValueError('Unsafe missing-checks recovery: ' + reason)

    require('```' not in text and '~~~' not in text, 'fenced content is ambiguous')
    heads = list(re.finditer(r'^#{1,4}\s+(Proof A|Proof B|Decision)\s*$', text, re.M | re.I))
    require([h[1].lower() for h in heads] == ['proof a', 'proof b', 'decision'],
            'expected one ordered pair of proof sections and one decision')
    index = next(i for i, h in enumerate(heads) if h[1].lower() == section)
    end = heads[index + 1].start()
    body = text[heads[index].end():end]
    require(not re.search(r'Decisive\s+checks', body, re.I), 'present-but-empty checks are not missing')
    field = re.search(r'^Qualifications and supplied repairs:[ \t]*\n(?P<evidence>.+)\Z',
                      body.strip(), re.M | re.S)
    require(field is not None, 'no separate existing qualifications evidence')
    evidence = field['evidence'].strip()
    bullets = [b.strip() for b in re.split(r'(?m)(?=^- )', evidence) if b.strip()]
    require(len(bullets) >= 2, 'need multiple explicit line-cited checks')
    for bullet in bullets:
        citations = list(re.finditer(r'\bLines?\s+([1-9]\d*)(?:[–-]([1-9]\d*))?(?![\w–-])',
                                     bullet, re.I))
        require(bullet.startswith('- ') and len(bullet) >= 80 and bool(citations),
                'every substantive bullet must already cite proof lines')
        require(all(m[2] is None or int(m[1]) <= int(m[2]) for m in citations),
                'line ranges must be ascending')
    addition = 'Decisive checks:\n' + evidence + '\n\n'
    normalized = text[:end] + addition + text[end:]
    parsed = strict_parse(normalized)
    return normalized, {
        'policy': CHECKS_POLICY, 'section': section,
        'source_field': 'Qualifications and supplied repairs',
        'operation': 'Copy all existing line-cited evidence verbatim under the omitted Decisive checks heading',
        'copied_evidence_sha256': sha(evidence), 'original_response_sha256': sha(text),
        'normalized_response_sha256': sha(normalized), 'winner_label': parsed['winner_label'],
        'model_calls': 0, 'new_mathematical_text': False,
    }


def restore_prose_checks_label(text, strict_parse):
    """Copy an existing substantive, line-cited paragraph without rewriting it.

    The inline field must cite at least two distinct proof locations. Preserve
    every qualification, self-correction and the original explicit preference.
    This checks format only; it does not certify the model's mathematics.
    """
    try:
        strict_parse(text)
    except ValueError as error:
        match = re.fullmatch(r'Missing Decisive checks in (proof [ab])', str(error))
        if not match:
            raise
        section = match[1]
    else:
        return text, None

    def require(ok, reason):
        if not ok:
            raise ValueError('Unsafe prose-checks recovery: ' + reason)

    require('```' not in text and '~~~' not in text, 'fenced content is ambiguous')
    heads = list(re.finditer(r'^#{1,4}\s+(Proof A|Proof B|Decision)\s*$', text, re.M | re.I))
    require([h[1].lower() for h in heads] == ['proof a', 'proof b', 'decision'],
            'expected one ordered pair of proof sections and one decision')
    index = next(i for i, h in enumerate(heads) if h[1].lower() == section)
    end = heads[index + 1].start()
    body = text[heads[index].end():end]
    require(not re.search(r'Decisive\s+checks', body, re.I), 'present-but-empty checks are not missing')
    for field in ('Established theorem', 'Claim gap', 'Qualifications and supplied repairs'):
        require(len(re.findall(r'^\s*' + field + r'\s*:', body, re.M | re.I)) == 1,
                'required proof fields must be unique')
    field = re.search(r'^Qualifications and supplied repairs:[ \t]+(?P<evidence>\S.+)\Z',
                      body.strip(), re.M | re.S)
    require(field is not None, 'expected existing inline qualifications prose')
    evidence = field['evidence'].strip()
    require(not re.search(r'(?m)^\s*(?:#{1,6}\s|[-*]\s|\d+[.)]\s)', evidence),
            'nested headings or lists are not inline prose')
    citations = list(re.finditer(r'\bLines?\s+([1-9]\d*)(?:[–-]([1-9]\d*))?(?![\w–-])',
                                 evidence, re.I))
    require(len(evidence) >= 160 and len({(m[1], m[2]) for m in citations}) >= 2,
            'need substantive prose with two distinct explicit line citations')
    require(all(m[2] is None or int(m[1]) <= int(m[2]) for m in citations),
            'line ranges must be ascending')
    addition = 'Decisive checks:\n' + evidence + '\n\n'
    normalized = text[:end] + addition + text[end:]
    parsed = strict_parse(normalized)
    return normalized, {
        'policy': PROSE_CHECKS_POLICY, 'section': section,
        'source_field': 'Qualifications and supplied repairs',
        'operation': 'Copy all existing line-cited prose verbatim under the omitted Decisive checks heading',
        'copied_evidence_sha256': sha(evidence), 'original_response_sha256': sha(text),
        'normalized_response_sha256': sha(normalized), 'winner_label': parsed['winner_label'],
        'inserted_start_char': end, 'inserted_end_char': end + len(addition),
        'model_calls': 0, 'new_mathematical_text': False,
    }


def recover_final_comparison(text, strict_parse):
    """Return the original text or a verbatim final block plus provenance.

    Recovery is deliberately narrow: duplicated proof sections, an unfinished
    first comparison, and exactly one complete final comparison. Every explicit
    winner must be a valid A/B label and agree. Never choose by reason or grade.
    Transport completion and request/proof bindings remain the caller's job.
    """
    try:
        strict_parse(text)
    except ValueError as error:
        if not str(error).startswith('Duplicate Markdown section:'):
            raise
        original_error = str(error)
    else:
        return text, None

    def require(ok, reason):
        if not ok:
            raise ValueError('Unsafe duplicate-comparison recovery: ' + reason)

    require('```' not in text and '~~~' not in text, 'fenced content is ambiguous')
    heads = list(re.finditer(r'^# Proof comparison[ \t]*\r?$', text, re.M | re.I))
    require(len(heads) >= 2 and not text[:heads[0].start()].strip(),
            'expected explicit comparison blocks with no preamble')
    blocks = [text[h.start():heads[i+1].start() if i+1 < len(heads) else len(text)]
              for i, h in enumerate(heads)]
    # A preceding Decision could be a competing final answer even if malformed.
    for block in blocks[:-1]:
        plain = block.replace('**', '').replace('`', '')
        require(not re.search(r'^#{1,4}\s+Decision\s*$', plain, re.M | re.I),
                'a preceding comparison already has a Decision section')
        try:
            strict_parse(block)
        except ValueError:
            pass
        else:
            raise ValueError('Unsafe duplicate-comparison recovery: multiple complete comparisons')
    final = blocks[-1]
    parsed = strict_parse(final)
    cleaned = text.replace('**', '').replace('`', '')
    lines = re.findall(r'^[ \t]*(?:[-*][ \t]*)?Winner[ \t]*:[^\r\n]*', cleaned, re.M | re.I)
    require(bool(lines), 'missing explicit winner')
    labels = []
    for line in lines:
        match = re.fullmatch(r'[ \t]*(?:[-*][ \t]*)?Winner[ \t]*:[ \t]*([AB])[ \t]*\.?[ \t]*', line, re.I)
        require(match is not None, 'malformed or nonbinary winner')
        labels.append(match.group(1).upper())
    require(set(labels) == {parsed['winner_label']}, 'conflicting explicit winners')
    return final, {
        'policy': POLICY, 'operation': 'extract_verbatim_unique_complete_final_block',
        'original_error': original_error, 'original_response_sha256': sha(text),
        'normalized_response_sha256': sha(final), 'selected_start_char': heads[-1].start(),
        'selected_end_char': len(text), 'comparison_blocks': len(blocks),
        'explicit_winners': labels, 'winner_label': parsed['winner_label'],
        'model_calls': 0, 'new_mathematical_text': False,
    }
