The solution is complete and logically sound.

- The factorization
  \[
  a(a-b)=(b+1)(b^2-b+1)
  \]
  is correct, and Euclid’s lemma gives an exhaustive case split.
- In Case 1, the substitution \(b+1=ma\) leads to the stated quadratic in \(a\). Its discriminant is computed correctly. It gives no prime solution for \(m=1\), and is negative for every \(m\ge2\).
- In Case 2, writing \(b^2-b+1=na\) correctly yields
  \[
  a=(n+1)b+n
  \]
  and the quadratic in \(b\). Its discriminant
  \[
  g(n)=n^4+2n^3+7n^2+2n-3
  \]
  is correct.
- The cases \(n=1,2\) are handled correctly. For \(n\ge3\), \(g(n)\) is rigorously placed strictly between the consecutive squares
  \[
  (n^2+n+2)^2\quad\text{and}\quad(n^2+n+3)^2,
  \]
  so it cannot be a square.
- The resulting pair \((7,3)\) is explicitly verified.

Thus all possibilities are exhausted and the unique solution is established.

<points>7 out of 7</points>