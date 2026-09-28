"""Normalize only explicit, unambiguous geometry field syntax.

This module receives one draft, never a theorem, proof, model or saved example.
It cannot repair source quotations, expressions, assumptions or targets.
Uniquely typed point names may be elaborated into fresh real coordinates.
"""
from __future__ import annotations

import hashlib
import re

from . import matched_expression as syntax, source_binding, geometry_declarations

POLICY = 'geometry-structural-syntax-v5'
IDENT = r'[A-Za-z][A-Za-z0-9_]{0,47}'
KEY = r'(?:symbols|define|premise|retain|target)'
SOURCE_ID = r'@source:S[0-9]{4}'
SOURCE_SLOT = rf'(?:{SOURCE_ID}|"{SOURCE_ID}"|\'{SOURCE_ID}\'|`{SOURCE_ID}`)'


def _references(node):
    if isinstance(node, list):
        return set().union(*(_references(child) for child in node[1:]))
    return {node} if isinstance(node, str) else set()


def _definition_order(lines):
    """Move pure definitions before premises, preserving dependency order.

    No sort is attempted for duplicate names, forward references, malformed
    records, or a misplaced target. Every complete field is retained verbatim.
    """
    try:
        rows = syntax.fields('```geometry-args\n' + ''.join(lines).rstrip('\r\n') + '\n```', fence='geometry-args')
        if not rows or rows[0][0] != 'symbols' or rows[-1][0] != 'target':
            return lines
        symbols = syntax.names(rows[0][1])
        if not 1 <= len(symbols) <= 16:
            return lines
        taken, declared = set(symbols), set(symbols)
        predicates = []
        for index, (key, body) in enumerate(rows[1:], 1):
            if key not in {'define', 'premise', 'retain', 'target'} or (key == 'target' and index != len(rows)-1):
                return lines
            parts = body.split(' :: ')
            arities = {'define': {2}, 'premise': {3, 4}, 'retain': {3, 4}, 'target': {2, 3}}
            if len(parts) not in arities[key] or not all(parts) or not syntax.IDENT.fullmatch(parts[0]) or parts[0] in taken:
                return lines
            taken.add(parts[0])
            if key == 'retain':
                continue
            node = syntax.expression(parts[1])
            if key == 'define':
                if not _references(node) <= declared:
                    return lines
                declared.add(parts[0])
            else:
                predicates.append(node)
        if any(not _references(node) <= declared for node in predicates):
            return lines
    except ValueError:
        return lines
    positions = [i for i, line in enumerate(lines) if line.strip()]
    phases = {'symbols': 0, 'define': 1, 'premise': 2, 'retain': 2, 'target': 3}
    ordered = sorted(zip(rows, positions), key=lambda item: phases[item[0][0]])
    result = lines.copy()
    for destination, (_, source) in zip(positions, ordered):
        # Keep the destination newline so moving the last definition cannot
        # merge it with another field when the fence body has no final newline.
        ending = '\r\n' if lines[destination].endswith('\r\n') else '\n' if lines[destination].endswith('\n') else ''
        result[destination] = lines[source].rstrip('\r\n') + ending
    return result


def normalize(text):
    """Return losslessly recorded syntax edits; leave unsupported forms unchanged.

    The ordinary parser still checks the complete document, declaration order,
    unique names, field arities, expression grammar and exact source quotations.
    """
    if not isinstance(text, str):
        raise ValueError('geometry draft must be Markdown text')
    edits = []
    normalized = text
    headings = list(re.finditer(r'^# Geometry Program\r?\n', text, re.M))
    if len(headings) == 1:
        start = headings[0].end()
        section = text[start:]
        fence = re.fullmatch(r'(\s*```geometry-args\r?\n)(.*?)(\r?\n```\s*)', section, re.S)
        # Never normalize ambiguous containers or multiple fences.
        if fence and '```' not in fence[2] and len(section.strip()) <= syntax.MAX_CHARS:
            lines = fence[2].splitlines(keepends=True)
            first = True
            offset = start + fence.start(2)
            for index, line in enumerate(lines):
                ending = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
                raw = line[:-len(ending)] if ending else line
                value = raw.strip(' \t')
                replacement, rule = value, None
                if not value:
                    offset += len(line)
                    continue
                # A field key and a labeled :: body determine the missing separator.
                missing = re.fullmatch(r'(define|premise|retain|target)[ \t]+('+IDENT+r')([ \t]+::[ \t]+.+)', value)
                assignment = re.fullmatch(r'define[ \t]+('+IDENT+r')[ \t]+=[ \t]+(.+)', value)
                spacing = re.fullmatch('('+KEY+r')[ \t]*=[ \t]*(.+)', value)
                symbols = re.fullmatch(r'symbols[ \t]+('+IDENT+r'(?:[ \t]*,[ \t]*'+IDENT+r')*)', value)
                if first and symbols:
                    replacement = 'symbols = ' + symbols[1]
                    rule = 'missing_symbols_equals'
                elif missing:
                    replacement = missing[1] + ' = ' + missing[2] + missing[3]
                    rule = 'missing_field_equals'
                elif assignment:
                    replacement = 'define = ' + assignment[1] + ' :: ' + assignment[2]
                    rule = 'definition_assignment_separator'
                elif spacing:
                    replacement = spacing[1] + ' = ' + spacing[2]
                    rule = 'field_separator_whitespace'
                elif first and re.fullmatch(IDENT+r'(?:[ \t]*,[ \t]*'+IDENT+r')+', value):
                    # The mandatory first slot is symbols; use only the listed names.
                    # Duplicates and excessive counts remain ordinary parser errors.
                    replacement = 'symbols = ' + value
                    rule = 'bare_initial_symbol_list'
                first = False
                if rule is not None and replacement != raw:
                    edits.append({'line':text.count('\n',0,offset)+1,
                                  'rule':rule,'before':raw,'after':replacement})
                    lines[index] = replacement + ending
                missing_source = re.fullmatch(r'premise = ('+IDENT+r') :: (.+)[ \t]+('+SOURCE_SLOT+r')', replacement)
                if missing_source:
                    try:
                        node = syntax.expression(missing_source[2])
                    except ValueError:
                        node = None
                    if isinstance(node, list):
                        fixed = 'premise = '+missing_source[1]+' :: '+missing_source[2]+' :: '+missing_source[3]
                        edits.append({'line':text.count('\n',0,offset)+1,
                                      'rule':'missing_premise_source_separator',
                                      'before':lines[index].rstrip('\r\n'),'after':fixed})
                        lines[index] = fixed + ending
                # Preserve both explicitly supplied source components. Exact
                # quotation validation belongs to source_binding.resolve.
                current = lines[index].rstrip('\r\n')
                # Both quotation and ID must still bind to the same exact span.
                # Only the missing explanation separator is restored.
                quoted = r'"[^"\n]+"'
                retained = re.fullmatch(r'(retain = '+IDENT+r' :: )('+quoted+r' '+SOURCE_ID+r') ('+quoted+r')', current)
                if retained and source_binding.annotated_reference(retained[2]):
                    fixed = retained[1] + retained[2] + ' :: ' + retained[3]
                    edits.append({'line':text.count('\n',0,offset)+1,
                                  'rule':'missing_retain_explanation_separator',
                                  'before':current,'after':fixed})
                    lines[index] = fixed + ending
                    current = fixed
                annotated_fields = re.fullmatch(r'(premise = '+IDENT+r' :: .+?) :: (.+) :: (.+)', current)
                if annotated_fields:
                    joined = annotated_fields[2] + ' ' + annotated_fields[3]
                    if source_binding.annotated_reference(joined):
                        fixed = annotated_fields[1] + ' :: ' + joined
                        edits.append({'line':text.count('\n',0,offset)+1,
                                      'rule':'joined_explicit_source_annotation',
                                      'before':current,'after':fixed})
                        lines[index] = fixed + ending
                        current = fixed
                missing_annotated = re.fullmatch(r'(premise = '+IDENT+r' :: )(.+?)[ \t]+(@source:S[0-9]{4,}[ \t]+.+)', current)
                if missing_annotated and source_binding.annotated_reference(missing_annotated[3]):
                    try:
                        node = syntax.expression(missing_annotated[2])
                    except ValueError:
                        node = None
                    if isinstance(node, list):
                        fixed = missing_annotated[1] + missing_annotated[2] + ' :: ' + missing_annotated[3]
                        edits.append({'line':text.count('\n',0,offset)+1,
                                      'rule':'missing_annotated_source_separator',
                                      'before':current,'after':fixed})
                        lines[index] = fixed + ending
                offset += len(line)
            first_line = text.count('\n',0,start + fence.start(2)) + 1
            positions = [i for i, line in enumerate(lines) if line.strip()]
            targets = [i for i in positions if lines[i].startswith('target = ')]
            if len(targets) == 1 and targets[0] == positions[-1]:
                index = targets[0]
                before = lines[index].rstrip('\r\n')
                expression = before[len('target = '):]
                try:
                    node = syntax.expression(expression)
                except ValueError:
                    node = None
                if isinstance(node, list) and len(node) == 3 and node[0] == 'eq':
                    # The label is metadata only. Avoid every existing token;
                    # preserve the entire supplied expression byte for byte.
                    used = set(re.findall(IDENT, ''.join(lines)))
                    label = 'normalized_target'
                    suffix = 1
                    while label in used:
                        label = 'normalized_target_' + str(suffix)
                        suffix += 1
                    after = 'target = ' + label + ' :: ' + expression
                    edits.append({'line':first_line+index, 'rule':'missing_target_label',
                                  'before':before, 'after':after})
                    lines[index] = after + lines[index][len(before):]
            ordered = _definition_order(lines)
            for index, (before, after) in enumerate(zip(lines, ordered)):
                if before != after:
                    edits.append({'line':first_line+index,
                                  'rule':'stable_definition_order',
                                  'before':before.rstrip('\r\n'),'after':after.rstrip('\r\n')})
            lines = ordered
            lines, declarations = geometry_declarations.elaborate(lines)
            if declarations:
                edits.append({'line':first_line, **declarations})
            normalized = text[:start] + fence[1] + ''.join(lines) + fence[3]
    sha = lambda value:hashlib.sha256(value.encode()).hexdigest()
    return normalized, {'policy':POLICY,'applied':bool(edits),'edits':edits,
                        'raw_sha256':sha(text),'normalized_sha256':sha(normalized)}
