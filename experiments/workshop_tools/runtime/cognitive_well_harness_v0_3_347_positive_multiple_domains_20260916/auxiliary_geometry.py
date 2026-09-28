"""Bounded definitional extensions of rational expression graphs.

Fresh real variables abbreviate exact expressions over earlier variables. Their
defining equations and original domains are mandatory; no source premise or
nonzero fact is invented. This module never reads problem data or source names.
"""
import sympy as sp

from . import matched_expression as syntax

POLICY = 'checked-rational-definitional-extension-v1'
LIFT_OPERATION_THRESHOLD = 128
MAX_TOTAL_SYMBOLS = 16


class AuxiliaryMixin:
    def initialize_auxiliaries(self, reserved):
        self.algebra_symbols = list(self.env.values())
        self.auxiliary_reserved = set(reserved)
        self.auxiliary_rows = []
        self.auxiliary_equations = []
        self.auxiliary_cache = {}
        self.auxiliary_enabled = True
        self.auxiliary_budget_exhausted = False

    def _fresh_auxiliary_name(self, prefix):
        index = 1
        while prefix+str(index) in self.auxiliary_reserved:
            index += 1
        name = prefix+str(index)
        self.auxiliary_reserved.add(name)
        return name

    def _lift_scalar(self, value):
        if not value.free_symbols or sp.count_ops(value) <= LIFT_OPERATION_THRESHOLD:
            return value
        if value in self.auxiliary_cache:
            return self.auxiliary_cache[value]
        if len(self.algebra_symbols) >= MAX_TOTAL_SYMBOLS:
            self.auxiliary_budget_exhausted = True
            return value
        before = tuple(self.algebra_symbols)
        if not value.free_symbols <= set(before):
            raise ValueError('auxiliary definition contains an undeclared variable')
        numerator, denominator = sp.fraction(sp.cancel(value))
        numerator = sp.Poly(numerator, *before, domain=sp.QQ).as_expr()
        denominator = sp.Poly(denominator, *before, domain=sp.QQ).as_expr()
        if denominator == 0 or sp.cancel(value*denominator-numerator) != 0:
            raise ValueError('auxiliary definition identity replay failed')
        name = self._fresh_auxiliary_name('aux_value_')
        label = self._fresh_auxiliary_name('aux_equation_')
        symbol = sp.Symbol(name, real=True)
        equation = sp.expand(symbol*denominator-numerator)
        if symbol in value.free_symbols or sp.cancel(equation.subs(symbol,value)) != 0:
            raise ValueError('auxiliary defining equation replay failed')
        # This obligation is checked by the same source-bound nonzero prover as
        # every original construction/division; equations are not guard facts.
        self.require('ne', denominator, 'auxiliary definition denominator: '+name)
        self.algebra_symbols.append(symbol)
        self.auxiliary_equations.append((label,equation))
        self.auxiliary_rows.append({'symbol':name,'equation_label':label,
            'source_expression':str(value),'numerator':str(numerator),
            'denominator':str(denominator),'defining_equation':str(equation),
            'earlier_symbols':[str(s) for s in before],
            'identity_checked':True,'domain_obligation_required':True})
        self.auxiliary_cache[value] = symbol
        return symbol

    def bind_definition(self, value):
        if not self.auxiliary_enabled:
            return value
        if isinstance(value,syntax.Point):
            return syntax.Point(self._lift_scalar(value.x),self._lift_scalar(value.y))
        if isinstance(value,syntax.Circle):
            return syntax.Circle(self._lift_scalar(value.u),self._lift_scalar(value.v),self._lift_scalar(value.w))
        if isinstance(value,sp.Expr):
            return self._lift_scalar(value)
        return value

    def auxiliary_report(self):
        return {'policy':POLICY,'trigger':'expanded expression size limit',
                'lift_operation_threshold':LIFT_OPERATION_THRESHOLD,
                'max_total_symbols':MAX_TOTAL_SYMBOLS,
                'budget_exhausted':self.auxiliary_budget_exhausted,
                'definitions':self.auxiliary_rows,
                'equations_are_definitions_not_source_premises':True,
                'equations_excluded_from_guard_prover':True}
