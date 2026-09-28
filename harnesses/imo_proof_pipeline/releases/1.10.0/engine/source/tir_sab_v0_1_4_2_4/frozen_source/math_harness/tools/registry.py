"""Rule-based registry mapping typed operations to backends and validators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .backends import (
    bitmask_dynamic_program,
    bounded_integer_solutions,
    divisor_power_threshold,
    enumerate_finite_assignments,
    exact_cover_count,
    exact_integer_expression,
    prove_newclid_geometry,
    solve_exact_branch_system,
    modular_tuple_enumeration,
    rational_product_equal_minima,
    rectangular_loop_exact_cover,
    solve_piecewise_branch_system,
)
from .backends.coverage import (
    exact_coordinate_geometry,
    exact_equation_system,
    exact_finite_state,
    exact_number_theory,
)
from .backends.sympy_generic import (
    determinant,
    exact_gcd,
    exact_modular_evaluation,
    expand_and_compare,
    factor_and_reexpand,
    polynomial_root_filter,
    prime_factorization,
    simplify_identity,
    solve_and_substitute,
)
from .validators import (
    validate_bounded_integer_solutions,
    validate_divisor_power_threshold,
    validate_enumeration,
    validate_exact_cover,
    validate_exact_integer_expression,
    validate_newclid_geometry_proof,
    validate_exact_branch_system,
    validate_residue_dp,
    validate_rational_product_equal_minima,
    validate_rectangular_loop_exact_cover,
    validate_piecewise_branch_system,
)
from .validators.coverage import (
    validate_exact_coordinate_geometry,
    validate_exact_equation_system,
    validate_exact_finite_state,
    validate_exact_number_theory,
)
from .validators.symbolic_generic import (
    validate_determinant,
    validate_exact_modular_evaluation,
    validate_expand_and_compare,
    validate_factor_and_reexpand,
    validate_gcd,
    validate_polynomial_root_filter,
    validate_prime_factorization,
    validate_simplify_identity,
    validate_solve_and_substitute,
)


Backend = Callable[[dict[str, Any]], dict[str, Any]]
Validator = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
ArgumentValidator = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class Capability:
    operation: str
    backend_capability: str
    backend_version: str
    validator_name: str
    validator_version: str
    execute: Backend
    validate: Validator
    validate_arguments: ArgumentValidator | None = None


class CapabilityRegistry:
    def __init__(self, capabilities: tuple[Capability, ...]) -> None:
        self._capabilities = {item.operation: item for item in capabilities}
        if len(self._capabilities) != len(capabilities):
            raise ValueError("duplicate registered tool operation")

    @property
    def operations(self) -> frozenset[str]:
        return frozenset(self._capabilities)

    def get(self, operation: str) -> Capability:
        try:
            return self._capabilities[str(operation)]
        except KeyError as exc:
            raise KeyError(f"unregistered tool operation: {operation}") from exc


def default_registry() -> CapabilityRegistry:
    generic = (
        ("expand_and_compare", expand_and_compare, validate_expand_and_compare),
        ("factor_and_reexpand", factor_and_reexpand, validate_factor_and_reexpand),
        ("simplify_identity", simplify_identity, validate_simplify_identity),
        ("solve_and_substitute", solve_and_substitute, validate_solve_and_substitute),
        (
            "polynomial_root_filter",
            polynomial_root_filter,
            validate_polynomial_root_filter,
        ),
        (
            "exact_modular_evaluation",
            exact_modular_evaluation,
            validate_exact_modular_evaluation,
        ),
        ("gcd", exact_gcd, validate_gcd),
        ("prime_factorization", prime_factorization, validate_prime_factorization),
        ("determinant", determinant, validate_determinant),
    )
    return CapabilityRegistry(
        (
            *(
                Capability(
                    operation=name,
                    backend_capability="sympy_exact",
                    backend_version="sympy-structured-expressions-v1",
                    validator_name=f"{name}_validator_v1",
                    validator_version="symbolic-generic-validator-v1",
                    execute=backend,
                    validate=validator,
                )
                for name, backend, validator in generic
            ),
            Capability(
                operation="algebraic_elimination_check",
                backend_capability="sympy_exact",
                backend_version="sympy-equal-minima-v1",
                validator_name="equal_minima_certificate_v1",
                validator_version="equal-minima-certificate-v1",
                execute=rational_product_equal_minima,
                validate=validate_rational_product_equal_minima,
            ),
            Capability(
                operation="rectangular_loop_exact_cover",
                backend_capability="exact_cover_bitmask",
                backend_version="rectangular-loop-bitmask-v1",
                validator_name="rectangular_loop_certificate_v1",
                validator_version="rectangular-loop-certificate-v1",
                execute=rectangular_loop_exact_cover,
                validate=validate_rectangular_loop_exact_cover,
            ),
            Capability(
                operation="enumerate_finite_assignments",
                backend_capability="finite_enumeration",
                backend_version="finite-expression-enumerator-v1",
                validator_name="finite_enumeration_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=enumerate_finite_assignments,
                validate=validate_enumeration,
            ),
            Capability(
                operation="bounded_integer_solutions",
                backend_capability="finite_enumeration",
                backend_version="bounded-integer-solutions-v1",
                validator_name="bounded_integer_solutions_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=bounded_integer_solutions,
                validate=validate_bounded_integer_solutions,
            ),
            Capability(
                operation="exact_integer_expression",
                backend_capability="safe_integer_ast",
                backend_version="safe-integer-expression-v1",
                validator_name="exact_integer_expression_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=exact_integer_expression,
                validate=validate_exact_integer_expression,
            ),
            Capability(
                operation="divisor_power_threshold",
                backend_capability="exact_integer_search",
                backend_version="divisor-power-threshold-v1",
                validator_name="divisor_power_threshold_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=divisor_power_threshold,
                validate=validate_divisor_power_threshold,
            ),
            Capability(
                operation="modular_tuple_enumeration",
                backend_capability="finite_enumeration",
                backend_version="modular-tuple-enumerator-v1",
                validator_name="modular_tuple_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=modular_tuple_enumeration,
                validate=validate_enumeration,
            ),
            Capability(
                operation="bitmask_dynamic_program",
                backend_capability="finite_residue_dp",
                backend_version="residue-convolution-v1",
                validator_name="residue_dp_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=bitmask_dynamic_program,
                validate=validate_residue_dp,
            ),
            Capability(
                operation="exact_cover_count",
                backend_capability="exact_cover_bitmask",
                backend_version="generic-exact-cover-v1",
                validator_name="generic_exact_cover_validator_v1",
                validator_version="finite-search-validator-v1",
                execute=exact_cover_count,
                validate=validate_exact_cover,
            ),
            Capability(
                operation="exact_equation_system",
                backend_capability="sympy_exact",
                backend_version="coverage-equation-system-v1",
                validator_name="exact_equation_system_validator_v1",
                validator_version="coverage-exact-recompute-validator-v1",
                execute=exact_equation_system,
                validate=validate_exact_equation_system,
            ),
            Capability(
                operation="exact_number_theory",
                backend_capability="exact_integer_search",
                backend_version="coverage-number-theory-v1",
                validator_name="exact_number_theory_validator_v1",
                validator_version="coverage-exact-recompute-validator-v1",
                execute=exact_number_theory,
                validate=validate_exact_number_theory,
            ),
            Capability(
                operation="exact_finite_state",
                backend_capability="finite_state_enumeration",
                backend_version="coverage-finite-state-v1",
                validator_name="exact_finite_state_validator_v1",
                validator_version="coverage-exact-recompute-validator-v1",
                execute=exact_finite_state,
                validate=validate_exact_finite_state,
            ),
            Capability(
                operation="exact_coordinate_geometry",
                backend_capability="sympy_exact_geometry",
                backend_version="coverage-coordinate-geometry-v1",
                validator_name="exact_coordinate_geometry_validator_v1",
                validator_version="coverage-exact-recompute-validator-v1",
                execute=exact_coordinate_geometry,
                validate=validate_exact_coordinate_geometry,
            ),
            Capability(
                operation="piecewise_branch_system",
                backend_capability="sympy_piecewise_exact",
                backend_version="piecewise-sign-branch-v1",
                validator_name="piecewise_branch_system_validator_v1",
                validator_version="piecewise-branch-validator-v1",
                execute=solve_piecewise_branch_system,
                validate=validate_piecewise_branch_system,
            ),
            Capability(
                operation="exact_branch_system",
                backend_capability="sympy_exact_branch_system",
                backend_version="exact-branch-system-v1",
                validator_name="exact_branch_system_validator_v1",
                validator_version="exact-branch-system-validator-v1",
                execute=solve_exact_branch_system,
                validate=validate_exact_branch_system,
            ),
            Capability(
                operation="newclid_geometry_proof",
                backend_capability="newclid_yuclid_geometry",
                backend_version="newclid-geometry-proof-v1",
                validator_name="newclid_geometry_proof_validator_v1",
                validator_version="newclid-geometry-proof-validator-v1",
                execute=prove_newclid_geometry,
                validate=validate_newclid_geometry_proof,
            ),
        )
    )
