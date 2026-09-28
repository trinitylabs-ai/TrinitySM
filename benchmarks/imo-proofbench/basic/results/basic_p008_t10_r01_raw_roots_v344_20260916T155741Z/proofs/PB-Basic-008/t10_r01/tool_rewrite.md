**Proof:**

Let $x = \sqrt{a}$, $y = \sqrt{b}$, and $z = \sqrt{c}$. Since $a, b, c > 0$, we have $x, y, z > 0$. The condition $a+b+c=1$ transforms into $x^2+y^2+z^2=1$. The inequality to be proved becomes
\[ x+y+z \geq 3\sqrt{3}(x^2y^2+y^2z^2+z^2x^2). \]
Define the continuous function $F(x,y,z) = x+y+z - 3\sqrt{3}(x^2y^2+y^2z^2+z^2x^2)$ on the compact set $S = \{(x,y,z) \in \mathbb{R}_{\geq 0}^3 : x^2+y^2+z^2=1\}$. By the Extreme Value Theorem, $F$ attains a global minimum on $S$. We will show this minimum is $0$.

First, consider the boundary of $S$, where at least one coordinate is zero. By symmetry, assume $z=0$. Then $x^2+y^2=1$ with $x,y \geq 0$. Let $u = x+y$. Since $x^2+y^2=1$, we have $u^2 = 1+2xy$, so $xy = \frac{u^2-1}{2}$. The range of $u$ is $[1, \sqrt{2}]$. On this boundary,
\[ F(x,y,0) = u - 3\sqrt{3}\left(\frac{u^2-1}{2}\right)^2 = u - \frac{3\sqrt{3}}{4}(u^2-1)^2. \]
Define $k(u) = u - \frac{3\sqrt{3}}{4}(u^2-1)^2$ for $u \in [1, \sqrt{2}]$. Its second derivative is $k''(u) = -\frac{3\sqrt{3}}{2}(3u^2-1)$, which is strictly negative for $u \geq 1$. Thus $k(u)$ is strictly concave on $[1, \sqrt{2}]$, and its minimum occurs at an endpoint. We compute $k(1) = 1$ and $k(\sqrt{2}) = \sqrt{2} - \frac{3\sqrt{3}}{4}$. Since $\sqrt{2} > \frac{3\sqrt{3}}{4}$ (equivalent to $32 > 27$), both endpoints are positive. Hence $F(x,y,z) > 0$ on the boundary of $S$. Consequently, the global minimum of $F$ on $S$ must occur in the interior, where $x,y,z > 0$.

In the interior, we use the method of Lagrange multipliers to find critical points of $F$ subject to $x^2+y^2+z^2=1$. The condition $\nabla F = \lambda \nabla G$ yields the system:
\[ \begin{cases} 1 - 6\sqrt{3}x(y^2+z^2) = 2\lambda x \\ 1 - 6\sqrt{3}y(x^2+z^2) = 2\lambda y \\ 1 - 6\sqrt{3}z(x^2+y^2) = 2\lambda z \end{cases} \]
Subtracting the second equation from the first gives:
\[ 6\sqrt{3}\big(y(x^2+z^2) - x(y^2+z^2)\big) = 2\lambda(x-y) \]
\[ 6\sqrt{3}\big(xy(x-y) - z^2(x-y)\big) = 2\lambda(x-y) \]
\[ (x-y)\big[6\sqrt{3}(xy-z^2) - 2\lambda\big] = 0. \]
Thus, for any pair of variables, either they are equal or $2\lambda = 6\sqrt{3}(xy-z^2)$. If $x,y,z$ were all distinct, we would have $xy-z^2 = yz-x^2 = zx-y^2$. From $xy-z^2 = yz-x^2$, we obtain $x^2-z^2 + y(x-z) = 0$, which factors as $(x-z)(x+y+z) = 0$. Since $x,y,z > 0$, we must have $x=z$, a contradiction. Therefore, at any interior critical point, at least two variables are equal. By symmetry, we may assume $x=y$.

Substituting $x=y$ into the constraint gives $2x^2+z^2=1$, so $z = \sqrt{1-2x^2}$. Since we are in the interior, $x,y,z > 0$, which implies $x \in (0, 1/\sqrt{2})$. The function $F$ reduces to a single-variable function $g(x)$:
\[ g(x) = 2x + \sqrt{1-2x^2} - 3\sqrt{3}\big(x^4 + 2x^2(1-2x^2)\big) = 2x + \sqrt{1-2x^2} - 3\sqrt{3}(2x^2-3x^4). \]
We analyze $g(x)$ on the closed interval $[0, 1/\sqrt{2}]$. For $x \in (0, 1/\sqrt{2})$, the radicand $1-2x^2$ is strictly positive, so $g$ is differentiable and its derivative is
\[ g'(x) = 2 - \frac{2x}{\sqrt{1-2x^2}} - 12\sqrt{3}x(1-3x^2). \]
To locate the critical points of $g$ in $(0, 1/\sqrt{2})$, we solve $g'(x)=0$. Multiplying by the strictly positive factor $\sqrt{1-2x^2}$ preserves the roots and sign changes, yielding the equivalent equation:
\[ \frac{36\sqrt{3}x^3\sqrt{1-2x^2} - 12\sqrt{3}x\sqrt{1-2x^2} - 2x + 2\sqrt{1-2x^2}}{\sqrt{1-2x^2}} = 0. \]
The numerator and denominator match the expression and domain in the certified lemma. Applying the exact root classification:
## Exact root-classification lemma

For the supplied expression `(36*sqrt(3)*x**3*sqrt(1 - 2*x**2) - 12*sqrt(3)*x*sqrt(1 - 2*x**2) - 2*x + 2*sqrt(1 - 2*x**2))/sqrt(1 - 2*x**2)` in `x`,
on interval `{"left":"0","right":"sqrt(2)/2","left_open":true,"right_open":true}`, the complete root count is **3**.

- `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 4)`: local_maximum; signs 1 → -1.
- `CRootOf(3*x**2 - 1, 1)`: local_minimum; signs -1 → 1.
- `CRootOf(419904*x**12 - 699840*x**10 + 431568*x**8 - 117072*x**6 + 12312*x**4 - 216*x**2 + 1, 7)`: local_maximum; signs 1 → -1.
According to Appendix A, the equation $g'(x)=0$ has exactly three solutions in $(0, 1/\sqrt{2})$. One solution is $x_0 = 1/\sqrt{3}$, which corresponds to a local minimum. The other two solutions correspond to local maxima. Since the denominator $\sqrt{1-2x^2}$ is strictly positive on the interval, the sign changes of the lemma's expression directly determine the nature of the critical points of $g(x)$. Thus, $x_0 = 1/\sqrt{3}$ is the unique local minimum of $g$ in the interior.

We evaluate $g(x)$ at the local minimum and the endpoints of the interval:
- At $x_0 = 1/\sqrt{3}$, we have $z = \sqrt{1-2/3} = 1/\sqrt{3}$, so $x=y=z$. Then
  \[ g(1/\sqrt{3}) = \frac{2}{\sqrt{3}} + \frac{1}{\sqrt{3}} - 3\sqrt{3}\left(\frac{2}{3} - \frac{3}{9}\right) = \sqrt{3} - 3\sqrt{3}\left(\frac{1}{3}\right) = 0. \]
- At the left endpoint $x=0$, $g(0) = 1$.
- At the right endpoint $x=1/\sqrt{2}$, $g(1/\sqrt{2}) = \sqrt{2} - \frac{3\sqrt{3}}{4} > 0$.

Since $x_0 = 1/\sqrt{3}$ is the unique local minimum in the interior of $(0, 1/\sqrt{2})$, the global minimum of $g(x)$ on $[0, 1/\sqrt{2}]$ is $\min\{g(0), g(1/\sqrt{2}), g(x_0)\} = 0$. Thus $g(x) \geq 0$ for all $x \in [0, 1/\sqrt{2}]$, with equality if and only if $x = 1/\sqrt{3}$.

This shows that $F(x,y,z) \geq 0$ for all interior critical points, and the minimum value is $0$, attained uniquely at $x=y=z=1/\sqrt{3}$. Combined with the boundary analysis showing $F > 0$ on the boundary, we conclude that $F(x,y,z) \geq 0$ for all $(x,y,z) \in S$. Translating back to $a,b,c$, we have
\[ \sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca), \]
with equality if and only if $a=b=c=1/3$. This completes the proof. $\square$

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
