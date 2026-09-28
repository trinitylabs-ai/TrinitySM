"""Check the complete geometry AST before any symbolic construction.

Only types, operator arities and declaration order are inspected. Names have no
theorem-specific meaning, and no malformed mathematical expression is repaired.
"""

SIGNATURES = {
    'point': ('scalar scalar', 'point'),
    'vadd': ('point point', 'point'), 'vsub': ('point point', 'point'),
    'scale': ('scalar point', 'point'), 'midpoint': ('point point', 'point'),
    'dot': ('point point', 'scalar'), 'cross': ('point point', 'scalar'),
    'norm2': ('point', 'scalar'), 'x': ('point', 'scalar'), 'y': ('point', 'scalar'),
    'foot': ('point point point', 'point'),
    'line_intersection': ('point point point point', 'point'),
    'circle': ('point point point', 'circle'), 'center': ('circle', 'point'),
    'power': ('circle point', 'scalar'),
    'circle_center_radius': ('point scalar', 'circle'),
    'second_on_line': ('circle point point', 'point'),
    'second_on_circles': ('circle circle point', 'point'),
    'invert_point': ('point scalar point', 'point'),
    'invert_line': ('point scalar point point', 'circle'),
    'inside': ('point point point point', 'predicate'),
    'angle_equal': ('point point point point point point', 'predicate'),
    **{op: ('scalar scalar', 'scalar') for op in ('sub', 'div', 'rational', 'pow')},
    **{op: ('scalar scalar', 'predicate') for op in ('eq', 'ne', 'gt', 'ge', 'lt', 'le')},
    **{op: ('scalar', 'scalar') for op in ('neg', 'sqrt')},
}


def validate(program):
    env = dict.fromkeys(program['symbols'], 'scalar')
    symbolic = set(program['symbols'])

    def infer(node, label):
        def fail(message):
            raise ValueError('geometry type check [' + label + ']: ' + message)
        if type(node) is int:
            return 'scalar'
        if isinstance(node, str):
            if node not in env:
                fail('unknown or forward-referenced name: ' + node)
            return env[node]
        op, *args = node
        if op == 'norm':
            fail('unsupported ordinary norm: norm2 is squared length and is not interchangeable')
        if op == 'symbol' and len(args) == 1 and isinstance(args[0], str):
            return infer(args[0], label)
        if op in {'differentiate', 'linear_root', 'coefficient_root'}:
            count = 3 if op == 'coefficient_root' else 2
            if len(args) != count:
                fail(op + ' requires ' + str(count) + ' operands')
            names = args[1:] if op == 'differentiate' else args[:-1]
            if any(not isinstance(s, str) or s not in symbolic for s in names):
                fail(op + ' requires declared symbolic variables')
            expression = args[0] if op == 'differentiate' else args[-1]
            if infer(expression, label) != 'scalar':
                fail(op + ' requires a scalar expression')
            return 'scalar'
        if op in {'add', 'mul'}:
            if not 2 <= len(args) <= 64:
                fail(op + ' requires 2..64 scalar operands')
            expected, result = ['scalar'] * len(args), 'scalar'
        elif op in SIGNATURES:
            signature, result = SIGNATURES[op]
            expected = signature.split()
        else:
            fail('unsupported operation: ' + str(op))
        if len(args) != len(expected):
            fail(op + ' requires ' + str(len(expected)) + ' operands; got ' + str(len(args)))
        actual = [infer(arg, label) for arg in args]
        if op in {'eq', 'ne'} and actual == ['point', 'point']:
            return 'predicate'
        if actual != expected:
            hint = ('; symbols are scalar coordinates. Define each point with '
                    '(point x y) or a point construction; the total coordinate '
                    'count must stay within 16.'
                    if any(want == 'point' and got == 'scalar'
                           for want, got in zip(expected, actual)) else '')
            fail(op + ' expects ' + ', '.join(expected) + '; got ' + ', '.join(actual) + hint)
        return result

    for label, node in program['definitions']:
        kind = infer(node, label)
        if kind == 'predicate':
            raise ValueError('predicate used as definition: ' + label)
        env[label] = kind
        if isinstance(node, str) and node in symbolic:
            symbolic.add(label)
    for label, node, _ in program['premises']:
        if infer(node, label) != 'predicate':
            raise ValueError('source requires a comparison: ' + label)
    label, node = program['target']
    if infer(node, label) != 'predicate' or not isinstance(node, list) or node[0] != 'eq':
        raise ValueError('target must be an equality: ' + label)
