The proposed solution is complete and rigorous.

- Setting \(x=0\) correctly gives \(f(f(y))=2f(y)+f(0)\).
- Substitution into the original equation is valid and leads to
  \[
  f(2x)+2f(y)=2f(x+y)+c.
  \]
- Setting \(y=0\) and substituting back correctly yields
  \[
  f(x+y)=f(x)+f(y)-c.
  \]
- Defining \(g(n)=f(n)-c\) reduces this to additivity on \(\mathbb Z\), from which \(g(n)=an\) for some \(a\in\mathbb Z\).
- Substitution of \(f(n)=an+c\) correctly forces either \(a=0,c=0\), or \(a=2\) with arbitrary \(c\in\mathbb Z\).
- Both resulting families are explicitly verified.

Thus all and only the solutions are \(f(n)=0\) and \(f(n)=2n+c\) for arbitrary \(c\in\mathbb Z\).

<points>7 out of 7</points>