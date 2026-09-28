# Generic formalizer program contract

Return exactly # Decision, # Semantic Bindings, # Geometry Program.
Decision is CALL_TOOL; alternatively return # Decision NO_TOOL and # Reason.
Semantic Bindings must derive coordinates/normalization, every premise, the
target correspondence and all domain conditions from the theorem. The submitted
proof is untrusted. Inventory every hypothesis: encode it or explicitly retain
it with an explanation of why a weaker algebraic implication suffices. Do not
assert the target, introduce extra assumptions, or assume a construction valid.

Geometry Program contains exactly one geometry-args fence. Its line grammar is:
symbols = comma-separated real coordinate/parameter names (1..16)
define = unique_name :: expression
premise = unique_label :: predicate :: source ID or exact theorem excerpt
retain = unique_label :: source ID or exact theorem excerpt :: explanation
target = unique_label :: (eq expression expression)

The symbols field lists free REAL SCALARS, not every named geometric object.
For free points use coordinate scalars and explicit point definitions, e.g.
symbols = ax, ay, bx, by
define = A :: (point ax ay)
define = B :: (point bx by)
define = M :: (midpoint A B)
Do not put A, B or M in that symbols list or define any name twice. Every point
argument must be a point expression or a previously defined point, not a scalar.
Keep the total number of free coordinate scalars within the 16-symbol limit.
Each free point consumes two coordinate scalars. Reuse actual constructions
instead of giving every constructed point independent coordinates. Do not drop
domain conditions or fix arbitrary coordinates merely to fit this budget.

A premise may append a fourth field containing an explanation. It is preserved
as untrusted audit context and never adds an equation, sign fact or guard.

A retain line may instead use four fields: label :: description :: source ::
explanation. The optional description is preserved as untrusted audit context.
Neither retain form adds an equation, sign fact or nonzero guard.
Use the literal separators, for example:
retain = condition :: @source:S0001 :: Explain why retaining this suffices.

Declare symbols first, then all definitions, then premises/retained hypotheses,
then exactly one target last. In every source slot, prefer an @source:S0001-style
ID from the Exact Source Spans supplied below. The compiler resolves that ID to
unchanged original theorem text; it does not infer that the premise follows.
Reuse a span for several premises when needed, explaining each correspondence.
Literal excerpts are also accepted: copy exact original text, including its
actual LaTeX spelling. Matching outer quotation marks are allowed. Do not
paraphrase a shared clause into separate quotations. Neither an ID nor an exact
quotation proves a premise; every correspondence still needs independent audit.
No JSON, Python, decimal floats or file paths in the Geometry Program.
Scalar expressions use integer literals, declared names, (add ...), (mul ...),
(sub x y), (div x y), (rational integer integer), (neg x), (pow x integer).
Geometry expressions: (point x y), (vadd P Q), (vsub P Q), (scale k P),
(dot P Q), (cross P Q), (norm2 P), (x P), (y P), (midpoint P Q),
(foot P A B), (line_intersection A B C D), (circle A B C), (center circle),
(power circle P). A point expression may be nested in any point operand.
Points and scalars are distinct types. eq and ne also accept two points, with
the exact meaning that their squared distance is zero or nonzero, respectively.
All ordered comparisons require scalar operands. Operators have exactly the
arities displayed here; extra operands or unknown operators are rejected.
norm2 is squared Euclidean length. Ordinary norm is unsupported; replacing it
with norm2 changes the value and is not a valid syntax repair.
Predicates: (eq x y), (gt x y), (ge x y), (lt x y), (le x y), (ne x y),
(inside P A B C) for STRICT interior of a nondegenerate triangle, and
(angle_equal A B C D E F) for the ordinary angles ABC and DEF.
Only equality is supported as a target. Rational premises require independently
proved original denominator conditions before their sign facts can be used.
The target must express the stated conclusion, with all parameters and their
dependencies justified. An arbitrary stronger claim or guessed object is not a
replacement for an existential or fixed-object conclusion. Retain the original
quantifiers and explain the correspondence in Semantic Bindings.
Use actual coordinate variables for freely located points and derive constructions
with the geometry operators. Avoid independent sine/cosine variables for Cartesian
constructions. Similarity normalization must be justified for the actual claim.
If nested rational constructions exceed the algebra budget, use a smaller,
equivalent encoding. Additional coordinate variables with source-justified
defining equalities are allowed within the 16-symbol limit; account for every
original domain and exceptional branch. Such equalities are unaudited premises,
not automatically trusted construction facts. Size-limit rejection supplies no
mathematical conclusion and never licenses dropping a hypothesis or guard.

The compiler derives dot/cross equations, interior consequences, construction
denominators and the polynomial numerator of the target. It searches bounded
positive sums/products, factors, affine functions on triangle interiors, and
linear-equation pivots for provable nonzero guards. Unsupported denominators
reject the draft. It never assumes a proposed guard merely to make algebra work.
Angle equality first tries a bounded exact calculation to establish the sign of
the cross-product product from strict source facts and proved nonzero conditions.
If that fails, it tries the existing individual-sign positivity search.
It factors polynomials over the rationals and solves sign parity relations,
then independently replays a positive-source product times a nonzero rational
square. This proves relative orientation without assuming either absolute sign.
Successful replay enables a relative signed cotangent equation, with both angle
cross products proved nonzero. If neither sign method succeeds, the compiler
uses a weaker squared-cosine equation and records the relaxation. Failure of a
certificate search is inconclusive. Source semantics still need model audit.


## Deterministic declaration recovery

Operator signatures may uniquely force a symbol to be a point. In that case the frontend lowers it to two fresh, unrestricted real coordinates and an explicit point definition. A redundant symbol declaration for a separately constructed point is removed only when its definition is unique, dependency order is valid and all uses have consistent types. Scalar rebindings, mixed types, unknown names, forward or self references, free circles and expansion beyond sixteen coordinates are rejected. Unconstrained names retain their scalar type. Mathematical expression tokens and source quotations are preserved.

Recovery is logged with exact before/after text, hashes and the generated coordinate map. The strict type checker validates the elaborated program, and compiler, audit and certificate replay all recompute the same normalization. No geometry premises or guards are manufactured. A missing separator between an explicitly quoted-and-ID-bound retained source and its quoted explanation can be restored; both the ID and quotation must still match the same source span.
