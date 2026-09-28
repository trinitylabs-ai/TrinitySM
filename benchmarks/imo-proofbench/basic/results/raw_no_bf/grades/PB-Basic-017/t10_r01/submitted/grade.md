The solution is complete and correct.

- The substitution \(k=n^2+n+1\) and \(x=3^k\) correctly gives
  \[
  A_n=x^{28}+x^{20}+1,\qquad x\ge 3.
  \]
- Evaluating exponents modulo \(3\) correctly shows that \(x^2+x+1\) divides \(x^{28}+x^{20}+1\). The subsequent decomposition rigorously confirms divisibility over \(\mathbb Z[x]\).
- The factor \(x^2+x+1\) is at least \(13\).
- Since
  \[
  x^{28}+x^{20}+1>x^2+x+1
  \]
  for \(x\ge3\), the integer cofactor \(Q(x)\) is also greater than \(1\).

Thus \(A_n\) is always a product of two integers greater than \(1\), so no non-negative integer \(n\) works.

<points>7 out of 7</points>