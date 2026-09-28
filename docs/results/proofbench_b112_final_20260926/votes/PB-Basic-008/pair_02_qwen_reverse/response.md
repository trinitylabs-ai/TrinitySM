# Proof comparison

## Proof A
Established theorem: The inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds for all positive reals $a,b,c$ with $a+b+c=1$. The proof establishes the stronger structural result that the auxiliary function $h(x) = \sqrt{x} + \frac{3\sqrt{3}}{2}(x^2 - x)$ is non-negative for all $x \in (0, 1)$, which directly implies the target inequality via summation.
Claim gap: NONE supported by checks. The algebraic reduction to $\sum h(a) \geq 0$ is rigorously equivalent to the original inequality under the constraint $a+b+c=1$. The calculus analysis of $h(x)$ is complete and verified.
Qualifications and supplied repairs: NONE. The proof is self-contained. The verification of the cubic factorization $N(u) = (u - 1/\sqrt{3})(6\sqrt{3}u^2 + 6u - \sqrt{3})$ and the subsequent root analysis confirms the monotonicity intervals and the non-negativity of $h(x)$ without requiring external lemmas.
Decisive checks: 
- Line 10-12: The rearrangement $\sum \sqrt{a} \geq 3\sqrt{3} \sum ab \iff \sum h(a) \geq 0$ is verified. The difference between the two sides simplifies to $\frac{3\sqrt{3}}{2}((\sum a)^2 - \sum a)$, which vanishes exactly when $\sum a = 1$.
- Line 15-27: The derivative $h'(x)$ and numerator $N(u)$ are correct. The root $u=1/\sqrt{3}$ is verified. The factorization is verified. The sign analysis of $N(u)$ correctly identifies $h(x)$ increases on $(0, u_0^2)$, decreases on $(u_0^2, 1/3)$, and increases on $(1/3, 1)$.
- Line 30: $h(1/3)=0$ is verified. Since $h(0)=0$ and $h(1/3)=0$ are the only zeros in the closure, and $h$ is positive between them (and after), $h(x) \geq 0$ holds for all $x \in (0,1)$.

## Proof B
Established theorem: The inequality holds for all positive reals $a,b,c$ with $a+b+c=1$. The proof establishes that the global minimum of the function $f(a,b,c)$ on the simplex is 0, attained at $a=b=c=1/3$.
Claim gap: NONE supported by checks. The Lagrange multiplier reduction to the symmetric case $a=b$ is justified by the strict convexity of the auxiliary function $h(x)$. The analysis of the single-variable function $k(a)$ and the boundary case $c=0$ is verified.
Qualifications and supplied repairs: NONE. The argument that $h(x)=\lambda$ has at most two solutions (due to $h$ being strictly decreasing then increasing) correctly implies at least two variables are equal at any critical point. The root counting argument for $k'(a)$ (at most 3 roots) is justified by the single inflection point of $g(a)$.
Decisive checks:
- Line 7-10: The Lagrange system and reduction to $h(a)=h(b)=h(c)$ are correct. The convexity of $h(x)$ (U-shaped) ensures at most two distinct values for $\{a,b,c\}$.
- Line 16-25: The derivative $k'(a)$ and second derivative $k''(a)$ are correct. The evaluation $k''(1/3) > 0$ confirms a local minimum. The argument that $k'(a)$ has exactly three roots (based on limits and convexity changes) is sound, implying the global minimum is at the critical point or boundaries.
- Line 28-35: The boundary analysis $c=0$ reduces to a single variable problem $q(x)$ which is concave, so the minimum is at endpoints. Both endpoints are positive.

## Decision
Winner: A
Reason: Both proofs are mathematically correct and complete. Proof A is preferred because it employs a more elegant and structurally insightful method: reducing the inequality to a sum of non-negative single-variable terms $\sum h(a) \geq 0$. This approach establishes a stronger result (that $h(x) \geq 0$ for all $x \in (0,1)$) and avoids the computational complexity and heuristic root-counting arguments required in Proof B's optimization approach. Proof A's explicit factorization of the derivative's numerator provides a more rigorous and transparent verification of the function's behavior than Proof B's reliance on convexity changes and intersection counts.