# Appendix A — Exact root isolation and sign classification

The polynomial below is an elimination superset. Exact real-root isolation covers all its real roots. Each candidate is checked against the positive square-root branch. Original denominators and the radicand domain are checked before classification. On each remaining interval the continuous expression has no zero or pole, so its sign equals the exact sign at the recorded rational sample. In stationary-points mode the expression is the derivative of the supplied function; its sign changes determine the listed local extrema.

The expression classified is `(36*sqrt(3)*x**3*sqrt(1 - 2*x**2) - 12*sqrt(3)*x*sqrt(1 - 2*x**2) - 2*x + 2*sqrt(1 - 2*x**2))/sqrt(1 - 2*x**2)`.

It is the derivative of `9*sqrt(3)*x**4 - 6*sqrt(3)*x**2 + 2*x + sqrt(1 - 2*x**2)`.

The elimination polynomial is `7776*x**8 - 9072*x**6 + 288*sqrt(3)*x**5 + 3456*x**4 - 240*sqrt(3)*x**3 - 420*x**2 + 48*sqrt(3)*x - 4`, over `QQ<sqrt(3)>`.

A `CRootOf(P,k)` denotes the root of the indicated polynomial with zero-based index k in the exact root ordering. Each recorded rational isolating interval below contains exactly one root of its polynomial, checked by a Sturm root count.

| Candidate root | Rational isolating interval | Signs of A, B in A+B√R | Original branch |
| --- | --- | --- | --- |
| `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 4)` | `['49306969229/549755813888', '98613938459/1099511627776']` | [-1, 1] | accepted |
| `CRootOf(3*x**2 - 1, 1)` | `['634803334273/1099511627776', '317401667137/549755813888']` | [-1, 1] | accepted |
| `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 7)` | `['383690571915/549755813888', '767381143831/1099511627776']` | [-1, 1] | accepted |
| `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 5)` | `['122245063093/1099511627776', '61122531547/549755813888']` | [-1, -1] | rejected |
| `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 6)` | `['518360900275/1099511627776', '129590225069/274877906944']` | [-1, -1] | rejected |

Original-domain checks (each condition has no zero in the specified interval):

- `1 - 2*x**2 > 0`; exact sign 1 at rational sample `181/512`.
- `sqrt(2) != 0`; exact sign 1 at rational sample `181/512`.
- `sqrt(1 - 2*x**2) != 0`; exact sign 1 at rational sample `181/512`.

The accepted roots divide the interval into the following zero-free, pole-free open cells:

- Between `0` and `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 4)`, sample `11/256` has exact sign 1.
- Between `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 4)` and `CRootOf(3*x**2 - 1, 1)`, sample `85/256` has exact sign -1.
- Between `CRootOf(3*x**2 - 1, 1)` and `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 7)`, sample `163/256` has exact sign 1.
- Between `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 7)` and `sqrt(2)/2`, sample `45/64` has exact sign -1.

## Exact root-classification lemma

For the supplied expression `(36*sqrt(3)*x**3*sqrt(1 - 2*x**2) - 12*sqrt(3)*x*sqrt(1 - 2*x**2) - 2*x + 2*sqrt(1 - 2*x**2))/sqrt(1 - 2*x**2)` in `x`,
on interval `{"left":"0","right":"sqrt(2)/2","left_open":true,"right_open":true}`, the complete root count is **3**.

- `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 4)`: local_maximum; signs 1 → -1.
- `CRootOf(3*x**2 - 1, 1)`: local_minimum; signs -1 → 1.
- `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 7)`: local_maximum; signs 1 → -1.

These computations classify the supplied expression; the source correspondence and its use in the full proof are separately audited.