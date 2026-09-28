Return exactly # Decision, # Semantic Bindings, # Root Program.
Decision is CALL_TOOL, or use # Decision NO_TOOL and # Reason.
Bind the exact function/expression, variable, interval and domain to the matcher's
Immutable Claim and the original source. Never assume that an asserted root set
or critical-point count is correct. The tool COMPUTES the complete set.
Root Program contains exactly one root-args fence, with fields in this order:
```root-args
variable = one real identifier
define = unique_name :: expression
interval = (open lower upper)
mode = stationary_points
function = expression
```
Use plain field = value lines, with no enclosing operation-name wrapper.
Definitions are optional. Endpoints must be finite exact real algebraic constants.
Interval kinds: open, closed, left_open, right_open (the named side is open).
For stationary_points, supply the original function; the tool differentiates it
and classifies all stationary points by derivative signs. Alternatively use
mode = roots and expression = expression to classify all zeros and their left/
right signs. In roots mode signs are signs of the supplied expression, not of an
unspecified underlying function. Do not encode only one proposed solution.
Expressions: integer literals, declared names, (rational int int), (add ...),
(mul ...), (sub a b), (div a b), (neg a), (pow a integer), (sqrt a).
Constant algebraic square roots are supported. At most ONE distinct square root
depending on the variable is supported, with a rational-function radicand.
The variable radicand must be strictly positive throughout the requested interval.
All original denominators must be nonzero throughout that interval. Excluded
open endpoints may be singular. A domain with an interior singularity is rejected;
split it into separately justified intervals rather than silently discarding it.
No free parameters, trigonometric/transcendental functions, floats, Python or JSON.
Polynomial degree is bounded at 24; coefficient field degree at 8, with combined
degree at most 64. Resource exhaustion or unresolved exact signs is inconclusive.
All results concern the supplied expression and interval. Source correspondence
and the surrounding proof require independent audits; no theorem is certified by
the root computation alone.
