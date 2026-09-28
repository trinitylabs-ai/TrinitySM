# Deterministic computations after tool matching

`matched_tools` implements two problem-independent operations. The upstream
caller selects one and supplies a formalized construction or scalar program.
The executor does not read theorem/proof/reference files, select a mathematical
claim, load a saved formula, or make model calls. The CLI reads only the explicit
argument file. It writes a fresh output directory and refuses overwrites.

| Selected operation | Appropriate detected gap | Supplied mathematical input |
| --- | --- | --- |
| `exact_geometry` | An unsupported point construction, incidence, circle power, second intersection, or fixed-locus assertion | Coordinates and parameters, actual construction definitions, premises, exact comparisons, requested outputs |
| `rational_identity` | An unresolved rational identity, linear equation, or parameter-independence assertion | Scalar definitions, unknown/moving parameter where relevant, premises, comparisons, requested outputs |

The detector should name the load-bearing missing or suspect fact and explain
its consequence for the proof. The matcher should select by mathematical
operations and supported domains. `CAPABILITIES` supplies generic descriptions;
`CONTRACT` supplies the complete argument contract. No problem ID or expected
answer is needed. The formalizer must justify its encoding and domain restrictions
from the source. The standalone API below retains its existing contract. The automatic v328 route
uses the separately documented geometry program compiler and certificate gate;
see GEOMETRY_PROGRAM.md and README.md.

## Entry points

```python
from cognitive_well_harness_v0_3_343_real_root_classification_20260916 import matched_tools

result = matched_tools.execute(
    operation="exact_geometry",
    arguments_markdown=arguments,
    timeout_seconds=60,
    memory_mb=2048,
)
```

Use `matched_tools.run(..., output=Path(...))` or
`proof_harness.run_matched_tool(..., output=Path(...))` to persist `arguments.md`,
`result.json`, and `result.md`. `matched_tools.replay(..., saved_result=result)`
re-executes the bound input and requires equality with the complete saved record.
Hashes or a saved success flag alone are not accepted as evidence. As with other
Python multiprocessing APIs, script callers should invoke execution under an
`if __name__ == "__main__":` guard.

```bash
/home/user/miniconda3/envs/math/bin/python -m \
  cognitive_well_harness_v0_3_343_real_root_classification_20260916.matched_tools \
  --operation exact_geometry --arguments /absolute/path/request.md \
  --output-dir /absolute/path/new_result --timeout-seconds 60 --memory-mb 2048
```

The math environment supplies SymPy. CPU execution uses a spawned process with
wall-time, CPU and address-space limits. Timeouts, unsupported derivations and
invalid constructions cannot produce affirmative evidence. No network is used.

## Typed Markdown program

Exactly one `exact-args` fence is accepted. `symbols` comes first, followed by
ordered `define`, `assume`, `check`, and `emit` fields. Definitions and assumptions
are optional; at least one check or output is required. All names are unique.
Use `symbols = NONE` for a concrete instance. Integers and exact rationals are
accepted; decimal floats, Python, JSON, arbitrary functions and file fields are
rejected. Symbol names have no mathematical interpretation.

This synthetic example derives a circle from a parameterized line and verifies
that each inverted point satisfies its equation:

```exact-args
symbols = t, k
define = S :: (point 2 3)
define = A :: (point 0 0)
define = B :: (point 1 0)
define = P :: (point t 0)
define = T :: (invert_point S k P)
define = locus :: (invert_line S k A B)
assume = nonzero_factor :: (ne k 0)
check = membership :: (eq (power locus T) 0)
emit = T
emit = locus
```

Scalar expressions: `add`, `mul`, `sub`, `div`, `neg`, `pow`, `rational`, `sqrt`
of a proven nonnegative exact constant, and `differentiate`. Comparisons: `eq`,
`ne`, `gt`, `ge`, `lt`, `le`, each with two scalar operands. Powers use integer
exponents from -16 to 32. Symbols denote real numbers. Assumptions are recorded
and evaluated but are not used as algebraic rewrite rules or as a constraint
solver. Exact constants can include surds; symbolic square-root branches are
unsupported.

| Geometry expression | Meaning |
| --- | --- |
| `(point x y)` | Point/vector with exact scalar coordinates |
| `(vadd P Q)`, `(vsub P Q)`, `(scale k P)` | Vector arithmetic |
| `(dot P Q)`, `(cross P Q)`, `(norm2 P)` | Dot product, signed determinant, squared norm |
| `(x P)`, `(y P)`, `(midpoint P Q)` | Coordinate extraction and midpoint |
| `(foot P A B)` | Perpendicular projection onto the line through distinct A, B |
| `(line_intersection A B C D)` | Unique intersection of the two lines |
| `(circle A B C)` | Circle through three noncollinear points |
| `(circle_center_radius O r)` | Circle with positive radius r |
| `(center circle)`, `(power circle P)` | Center and signed circle power |
| `(second_on_line circle P Q)` | Second intersection on line PQ, given P on the circle |
| `(second_on_circles first second P)` | Second common point, given common point P |
| `(invert_point S k P)` | `S + k*(P-S)/norm2(P-S)`, with k nonzero and P distinct from S |
| `(invert_line S k A B)` | Circle obtained by the same inversion of a line avoiding S |

Circles are returned as coefficients of `x^2+y^2+u*x+v*y+w=0`. The line-inversion
formula describes the containing circle; the inversion center is not the image
of a finite point of the original line. Membership does not establish surjectivity
onto the circle or the admissible arc of an original geometric configuration.

## Deriving values rather than supplying answers

`(linear_root q expression)` solves `expression = 0` when its rational numerator
is linear in declared unknown q. It chooses a nonzero linear pivot, computes the
candidate, and checks substitution in the numerator and the original domain.

`(coefficient_root z t expression)` treats t as a moving parameter and z as the
unknown to remain fixed. It equates **all** numerator coefficients in t to zero,
derives a candidate from a linear equation in z, then checks every coefficient.
An inconsistent set of coefficients or a nonlinear unknown gives INCONCLUSIVE.

```exact-args
symbols = t, q, z
define = moving :: (linear_root q (sub (mul (add t 2) q) (add t 7)))
define = fixed :: (coefficient_root z t (add (mul (sub z 5) (pow t 2)) (sub (mul 2 z) 10)))
emit = moving
emit = fixed
```

Every pivot, canceled denominator, and required domain condition is retained.
Root computations also test earlier recorded conditions after substituting the
derived root; canceled poles cannot become valid roots. Earlier definitions keep
their original conditions as well. The solver returns one checked candidate
under those conditions. It does not classify exceptional zero-pivot branches,
prove uniqueness, or solve arbitrary nonlinear systems.

## Meaning of a result

- `IDENTITY_VERIFIED`: every requested comparison evaluated true and every
  supplied premise and construction condition evaluated true.
- `CONDITIONAL_IDENTITY`: comparisons evaluated true, with displayed symbolic
  domain conditions or premises still requiring justification.
- `COMPUTED` / `CONDITIONAL_COMPUTATION`: requested values were computed, without
  a claim that a supplied theorem or target comparison was proved.
- `COUNTEREXAMPLE`: a concrete instance satisfies every supplied premise and
  construction condition and makes at least one requested comparison false.
- `INCONSISTENT_PREMISES` / `INVALID_INSTANCE`: a premise or construction
  condition is false; this is not a counterexample to the source theorem.
- `INCONCLUSIVE` / `INVALID_REQUEST` / `EXECUTION_ERROR`: no affirmative evidence.

Each comparison includes its exact residual and three-valued truth result.
Symbolic nonzero residuals are not automatically counterexamples. Joint
consistency of symbolic premises is not certified. Construction identities are
rechecked algebraically, rather than assumed as additional conditions. Tangency
is not interpreted as a distinct second intersection; coincident circles and
lines through the inversion center are rejected or left as explicit exclusions.

`theorem_proved` and `source_semantics_verified` always remain false. A semantic
audit and a complete mathematical argument are still required before using the
result in a proof. `usable_evidence` denotes a scoped computation result, not
permission to bypass the existing proof-synthesis evidence gate.

## Verification and isolation

`test_matched_tools.py` exercises symbolic projections, translated/scaled
intersections, exact counterexamples, canceled poles, coefficient derivations,
inverted loci, invalid domains, resource limits, input rejection, replay tampering,
and the explicit harness handoff. Runtime-module checks reject benchmark catalog
or fixture imports. Case-specific validation is stored outside this package and
is never read during tool execution. The frozen export is not modified.
