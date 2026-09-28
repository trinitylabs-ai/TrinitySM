The proposed solution is complete and correct.

- The substitutions \(x=0\) and \(y=0\) correctly yield
  \[
  f(f(y))=2f(y)+b,\qquad f(2x)=2f(x)-b.
  \]
- Substitution into the original equation correctly gives
  \[
  f(x+y)=f(x)+f(y)-b.
  \]
  Thus \(g(n)=f(n)-b\) is additive on \(\mathbb Z\), so rigorously \(g(n)=an\) for some \(a\in\mathbb Z\).
- Substituting \(f(n)=an+b\) gives the necessary conditions
  \[
  a(a-2)=0,\qquad b(a-2)=0,
  \]
  leading precisely to \(f\equiv0\) or \(f(n)=2n+b\) for arbitrary \(b\in\mathbb Z\).
- Both families are explicitly and correctly verified in the original equation.

There are no logical gaps or computational errors.

<points>7 out of 7</points>