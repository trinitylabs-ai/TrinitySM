The solution is complete and correct.

- The binomial expansion
  \[
  R(x^k)=\sum_{m=0}^{\lfloor k/2\rfloor}\binom{k}{2m}x^{k-4m}
  \]
  is correct.
- Comparing the coefficient of \(x^{-n}\) correctly forces \(n\) to be even.
- For \(n>4\), comparison of the coefficient of \(x^{n-4}\) gives the contradiction
  \[
  a_{n-4}=a_{n-4}+\binom n2,
  \]
  hence \(\deg P\le4\).
- The cases \(n=0,2,4\) are handled correctly:
  - degree \(0\) gives no solution;
  - degree \(2\) gives \(P(x)=x^2\);
  - degree \(4\) gives \(P(x)=x^4+ax^2+6\), with arbitrary \(a\in\mathbb R\).
- These resulting polynomials indeed satisfy the original identity.

Thus all possibilities are correctly identified with rigorous justification.

<points>7 out of 7</points>