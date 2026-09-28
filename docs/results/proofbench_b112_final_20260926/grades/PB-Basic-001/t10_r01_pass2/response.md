The proof is complete and rigorous:

- It correctly derives \(f(f(y))=2f(y)+f(0)\).
- Substitution yields \(f(2x)=2f(x)-f(0)\), leading to
  \[
  f(x+y)=f(x)+f(y)-f(0).
  \]
- Defining \(g(x)=f(x)-f(0)\) gives an additive function on \(\mathbb Z\), correctly implying \(g(x)=ax\) for some \(a\in\mathbb Z\).
- Substitution of \(f(x)=ax+c\) correctly forces either \(a=0,c=0\), or \(a=2\) with arbitrary \(c\in\mathbb Z\).
- Both resulting families are explicitly verified.

Thus all and only the solutions \(f\equiv0\) and \(f(x)=2x+c\) are obtained.

<points>7 out of 7</points>