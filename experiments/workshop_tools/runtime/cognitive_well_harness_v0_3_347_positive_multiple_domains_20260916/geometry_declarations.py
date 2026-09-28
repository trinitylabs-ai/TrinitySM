"""Elaborate unambiguous point uses into fresh, unrestricted real coordinates.

Only the geometry AST is inspected. No names have special geometric meaning;
no theorem, source proof, saved program, model, or algebra solver is consulted.
Conflicting types, rebinding scalars, forward references and budget overflows
leave the draft unchanged for the strict parser to reject.
"""
import re

from . import geometry_types, matched_expression as syntax


def elaborate(lines):
    try:
        return _elaborate(lines)
    except ValueError:
        return lines, None


def _elaborate(lines):
    rows = syntax.fields('```geometry-args\n' + ''.join(lines).rstrip('\r\n') + '\n```', fence='geometry-args')
    if (not rows or rows[0][0] != 'symbols' or rows[-1][0] != 'target'
            or sum(key == 'target' for key, _ in rows) != 1):
        raise ValueError('symbols first and target last required')
    symbols = syntax.names(rows[0][1])
    if not 1 <= len(symbols) <= 16:
        raise ValueError('symbol budget')
    labels, definitions, predicates = set(), [], []
    phase = 0
    for key, body in rows[1:]:
        phases = {'define': 0, 'premise': 1, 'retain': 1, 'target': 2}
        if key not in phases or phases[key] < phase:
            raise ValueError('unknown or misplaced field')
        phase = phases[key]
        parts = body.split(' :: ')
        arities = {'define': {2}, 'premise': {3, 4}, 'retain': {3, 4}, 'target': {2, 3}}
        if len(parts) not in arities[key] or not all(parts):
            raise ValueError('invalid field arity')
        label = parts[0]
        if not syntax.IDENT.fullmatch(label) or label in labels:
            raise ValueError('duplicate or invalid field label')
        labels.add(label)
        if key != 'define' and label in symbols:
            raise ValueError('metadata label collides with variable')
        if key == 'retain':
            continue
        node = syntax.expression(parts[1])
        if key == 'define':
            definitions.append((label, node))
        else:
            if key == 'target' and (not isinstance(node, list) or node[0] != 'eq'):
                raise ValueError('target must be equality')
            predicates.append(node)

    defined = {name for name, _ in definitions}
    free = set(symbols) - defined
    overlap = set(symbols) & defined
    parent = {name: name for name in free | defined}
    kinds = {}
    for kind in ('scalar', 'point', 'circle', 'predicate'):
        parent['@' + kind] = '@' + kind
        kinds['@' + kind] = kind

    def find(name):
        if name not in parent:
            raise ValueError('undeclared name')
        if parent[name] != name:
            parent[name] = find(parent[name])
        return parent[name]

    def unify(left, right):
        left, right = find(left), find(right)
        if left == right:
            return
        a, b = kinds.get(left), kinds.get(right)
        if a is not None and b is not None and a != b:
            raise ValueError('conflicting geometry types')
        parent[right] = left
        if a is not None or b is not None:
            kinds[left] = a or b

    available = set(free)
    comparable = []

    def infer(node):
        if type(node) is int:
            return '@scalar'
        if isinstance(node, str):
            if node not in available:
                raise ValueError('unknown or forward-referenced name')
            return node
        op, *args = node
        if op == 'symbol' and len(args) == 1 and isinstance(args[0], str):
            value = infer(args[0])
            unify(value, '@scalar')
            return '@scalar'
        if op in {'differentiate', 'linear_root', 'coefficient_root'}:
            count = 3 if op == 'coefficient_root' else 2
            if len(args) != count:
                raise ValueError('invalid symbolic operator arity')
            for arg in args:
                unify(infer(arg), '@scalar')
            return '@scalar'
        if op in {'eq', 'ne'}:
            if len(args) != 2:
                raise ValueError('comparison arity')
            left, right = map(infer, args)
            unify(left, right)
            comparable.append(left)
            return '@predicate'
        if op in {'add', 'mul'}:
            if not 2 <= len(args) <= 64:
                raise ValueError('scalar operation arity')
            expected, result = ['scalar'] * len(args), 'scalar'
        elif op in geometry_types.SIGNATURES:
            signature, result = geometry_types.SIGNATURES[op]
            expected = signature.split()
        else:
            raise ValueError('unsupported operator')
        if len(args) != len(expected):
            raise ValueError('operator arity')
        for arg, kind in zip(args, expected):
            unify(infer(arg), '@' + kind)
        return '@' + result

    for name, node in definitions:
        unify(name, infer(node))
        available.add(name)
    for node in predicates:
        unify(infer(node), '@predicate')

    def kind(name):
        # Unconstrained names retain the original real-scalar interpretation.
        return kinds.get(find(name), 'scalar')

    if any(kind(name) not in {'scalar', 'point'} for name in free):
        raise ValueError('cannot invent free circles or predicates')
    if any(kind(name) not in {'scalar', 'point'} for name in comparable):
        raise ValueError('invalid comparison type')
    if any(kind(name) == 'predicate' for name in defined):
        raise ValueError('predicate definition')
    if any(kind(name) != 'point' for name in overlap):
        raise ValueError('only redundant constructed-point declarations recover')
    points = [name for name in symbols if name in free and kind(name) == 'point']
    if not points and not overlap:
        return lines, None

    # Generated coordinate names cannot capture identifiers in expressions,
    # labels, retained prose, or source annotations within the program body.
    used = set(re.findall(r'[A-Za-z][A-Za-z0-9_]*', ''.join(lines)))
    coordinates = {}
    counter = 1

    def fresh():
        nonlocal counter
        while 'coordinate_' + str(counter) in used:
            counter += 1
        name = 'coordinate_' + str(counter)
        used.add(name)
        counter += 1
        return name

    lowered_symbols = []
    for name in symbols:
        if name in overlap:
            continue
        if name in points:
            coordinates[name] = [fresh(), fresh()]
            lowered_symbols.extend(coordinates[name])
        else:
            lowered_symbols.append(name)
    if not 1 <= len(lowered_symbols) <= 16:
        raise ValueError('coordinate budget exceeded')
    point_definitions = [(name, ['point', *coordinates[name]]) for name in points]
    # The unchanged strict checker independently validates the lowered AST.
    geometry_types.validate({'symbols': lowered_symbols,
                             'definitions': point_definitions + definitions,
                             'premises': [('check_' + str(i), node, '')
                                          for i, node in enumerate(predicates[:-1])],
                             'target': ('target_check', predicates[-1])})
    result = lines.copy()
    index = next(i for i, line in enumerate(lines) if line.strip())
    ending = '\r\n' if lines[index].endswith('\r\n') else '\n'
    additions = ['symbols = ' + ', '.join(lowered_symbols)]
    additions.extend('define = ' + name + ' :: (point ' + ' '.join(coordinates[name]) + ')'
                     for name in points)
    result[index:index + 1] = [line + ending for line in additions]
    return result, {'rule': 'typed_point_declarations',
                    'before': ''.join(lines), 'after': ''.join(result),
                    'character_count': len(''.join(lines)), 'point_coordinates': coordinates,
                    'redundant_point_declarations': [name for name in symbols if name in overlap],
                    'new_constraints': [], 'original_expressions_unchanged': True}
