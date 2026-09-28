The proposed solution is complete and correct.

- The substitutions \(x=0\) and \(y=0\) correctly yield
  \[
  f(f(y))=2f(y)+c,\qquad f(2x)=2f(x)-c.
  \]
- Substitution into the original equation correctly gives
  \[
  f(x+y)=f(x)+f(y)-c.
  \]
  Thus \(g(n)=f(n)-c\) is additive on \(\mathbb Z\), so \(g(n)=an\) for some \(a\in\mathbb Z\).
- Substituting \(f(n)=an+c\) back into the original equation correctly forces \(a=0,c=0\), or \(a=2\) with arbitrary \(c\in\mathbb Z\).
- Both resulting families are explicitly and correctly verified.

Therefore all solutions are \(f\equiv0\) and \(f(n)=2n+c\) for arbitrary \(c\in\mathbb Z\).

<points>7 out of 7</points>