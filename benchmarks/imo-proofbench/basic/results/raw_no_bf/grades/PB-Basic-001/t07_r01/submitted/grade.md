The proposed solution is complete and correct.

- Setting \(x=0\) correctly gives
  \[
  f(f(y))=2f(y)+f(0).
  \]
- Applying this identity to \(x+y\) correctly transforms the original equation into
  \[
  f(2x)+2f(y)=2f(x+y)+c,
  \]
  where \(c=f(0)\).
- Setting \(y=0\) yields \(f(2x)=2f(x)-c\). Substitution then gives
  \[
  f(x)+f(y)=f(x+y)+c.
  \]
- Thus \(g(x)=f(x)-c\) is additive on \(\mathbb Z\). Every additive integer-valued function on \(\mathbb Z\) has the form \(g(x)=ax\), with \(a=g(1)\in\mathbb Z\), so \(f(x)=ax+c\).
- Substitution into the original equation correctly forces
  \[
  a^2=2a,\qquad c(2-a)=0,
  \]
  giving either \(a=0,c=0\), hence \(f\equiv0\), or \(a=2\) with arbitrary \(c\in\mathbb Z\), hence \(f(x)=2x+c\).
- Both families are explicitly and correctly verified.

There are no substantive gaps or errors.

<points>7 out of 7</points>