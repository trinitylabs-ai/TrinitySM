The proposed solution is complete and correct.

- The substitutions \(x=0\) and \(y=0\) correctly yield
  \[
  f(f(y))=2f(y)+f(0),\qquad f(2x)+2f(0)=f(f(x)).
  \]
- Combining these gives \(f(2x)=2f(x)-f(0)\).
- Substitution into the original equation correctly establishes
  \[
  f(x+y)=f(x)+f(y)-f(0).
  \]
- Defining \(g(x)=f(x)-f(0)\) reduces this to additivity on \(\mathbb Z\), for which \(g(x)=ax\) with \(a\in\mathbb Z\).
- Substitution of \(f(x)=ax+b\) correctly produces \(a\in\{0,2\}\), with \(b=0\) when \(a=0\) and arbitrary \(b\in\mathbb Z\) when \(a=2\).
- Both resulting families are explicitly verified.

Thus all and only the solutions are \(f\equiv0\) and \(f(n)=2n+b\) for arbitrary \(b\in\mathbb Z\).

<points>7 out of 7</points>