import copy
import json
import random

import pytest
import sympy as sp

from . import backend_comparison as backends
from . import gaussian_backend as backend
from . import polynomial_export as exporter
from . import radical_certificate as radical

x, y, z = sp.symbols("x y z")


def run(program):
    if not backends.DEFAULT_BINARY.is_file():
        pytest.skip("Singular unavailable")
    return backend._run(program, backends.DEFAULT_BINARY, 10, memory_mb=1024)


def test_old_fractional_power_spelling_reproduces_backend_error():
    result = run('ring R=(0,ii),(x),dp;\nminpoly=ii^2+1;\n'
                 'poly p=x^2/2;\nprint("RESULT_DONE=1");\nexit;\n')
    assert result["status"] == "ERROR"
    assert "expected `poly` ^ `int`" in result["output"]
    assert result["markers"] == {}  # A later success marker cannot hide errors.


def test_live_roundtrip_preserves_exact_coefficients_and_exponents():
    values = [sp.Integer(0), sp.Rational(-3, 7), sp.I / 3,
              x**2 / 2, -x**3 / 7, x**2 * y**3 / 11,
              (sp.Rational(2, 3) - sp.I / 7) * x**2 + sp.I * y / 13,
              z * x**2 / 2 + z * y**2 / 2 - x * y * z + 1,
              (x / 2 + y / 3)**4]
    rng = random.Random(346)
    for _ in range(24):
        values.append(sum(
            (sp.Rational(rng.randint(-13, 13), rng.randint(1, 11))
             + sp.I * sp.Rational(rng.randint(-9, 9), rng.randint(1, 7)))
            * x**rng.randrange(7) * y**rng.randrange(5) * z**rng.randrange(4)
            for _ in range(8)))
    lines = ['ring R=(0,ii),(x,y,z),dp;', 'minpoly=ii^2+1;']
    for index, value in enumerate(values):
        lines.extend([f'poly p{index}={exporter.expression(value)};',
                      f'print("RESULT_P{index}="+string(p{index}));'])
    lines.extend(['print("RESULT_DONE=1");', 'exit;'])
    result = run('\n'.join(lines) + '\n')
    assert result['status'] == 'COMPLETED', result['output']
    assert result['markers']['RESULT_DONE'] == '1'
    for index, value in enumerate(values):
        actual = backend._parse_backend_polynomial(
            result['markers'][f'RESULT_P{index}'], [x, y, z], [x, y, z])
        assert sp.Poly(actual - value, x, y, z, domain=sp.QQ_I).is_zero


@pytest.mark.parametrize('value', [1/x, sp.sqrt(x), sp.sin(x), sp.sqrt(2)*x,
                                  sp.Float('0.5')*x, sp.oo, sp.nan,
                                  sp.Symbol('ii'), sp.Symbol('x;exit'),
                                  sp.Symbol('x') + sp.Symbol('x', positive=True)])
def test_unsupported_or_ambiguous_input_rejected(value):
    with pytest.raises((ValueError, sp.PolynomialError, sp.CoercionFailed)):
        exporter.expression(value)


def test_ordinary_rational_membership_exports_and_replays():
    result = backend.check(symbols=[x, y], generators=[('g', x**2/2-y/3)],
        target=x**2-2*y/3, guards={}, binary=backends.DEFAULT_BINARY,
        timeout_sec=10, memory_mb=1024, radical=False)
    assert result['status'] == 'COMPLETED', result
    assert result['certificate_reexpanded'] is True
    assert result['membership_certificate']['reexpansion_zero'] is True


@pytest.mark.parametrize('target,guards,expected', [
    (x, {'y_nonzero': y}, True),
    (x, {}, False),
    (x**2/2, {'y_nonzero': y}, True),
])
def test_radical_rational_certificate_and_false_consequence(tmp_path, target, guards, expected):
    system = radical.system_payload([x, y], [('g', x**2*y/2)], target, guards)
    result = radical.export(system, tmp_path/'certificate', timeout=10, memory=1024)
    assert result['verified'] is expected, result
    if expected:
        certificate = json.loads((tmp_path/'certificate/certificate.json').read_text())
        assert radical.replay(system, certificate)['verified']
        tampered = copy.deepcopy(certificate)
        symbols, _ = radical.augmented(system)
        tampered['multipliers'] = [radical.laurent._payload(sp.Integer(0), symbols)
                                  for _ in certificate['multipliers']]
        with pytest.raises(ValueError, match='re-expansion'):
            radical.replay(system, tampered)


def test_radical_screen_handles_rational_coefficients():
    result = backends.guarded_radical_check([x, y], [('g', x**2*y/2)], x**2/3,
        {'y_nonzero': y}, backends.DEFAULT_BINARY, 10, 1024)
    assert result['status'] == 'COMPLETED', result
    assert result['markers']['RESULT_RADICAL'] == 'PROVED'


def test_principal_screen_handles_rational_coefficients():
    result = backend.check_principal_radical(symbols=[x, y],
        generator=('g', x**2*y/2), target=x**2/3, guards={'y_nonzero': y},
        binary=backends.DEFAULT_BINARY, timeout_sec=10, memory_mb=1024)
    assert result['status'] == 'COMPLETED', result
    assert result['markers']['RESULT_PRINCIPAL_RADICAL'] == 'PROVED'
