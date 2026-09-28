The core argument is correct:

- The orbit \(a_{n+1}=g(a_n)\) is properly extended to all integers using bijectivity.
- The recurrence and its general solution are correct.
- Since \(g\) and \(g^{-1}\) are increasing, each orbit is monotone according to the sign of \(g(x)-x\).
- A nonzero coefficient of \((-4)^n\) forces alternating signs in consecutive differences as \(n\to-\infty\), contradicting monotonicity.
- The resulting candidate \(g(x)=5x\) is correctly verified.

There is, however, a calculation error. From
\[
a_{n+1}-a_n=4A5^n-5B(-4)^n,
\]
setting \(n=-m\) gives
\[
a_{-m+1}-a_{-m}=\frac{4A}{5^m}-\frac{5B}{(-4)^m},
\]
not the displayed expression involving \(20A\) and \(20B\). The intended dominance and sign-alternation argument remains valid after this local correction. Thus this is an almost complete solution with a minor computational error.

<points>6 out of 7</points>