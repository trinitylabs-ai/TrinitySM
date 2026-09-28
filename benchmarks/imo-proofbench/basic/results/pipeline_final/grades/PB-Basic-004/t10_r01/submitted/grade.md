The proof is complete and correct.

- Strict monotonicity and surjectivity imply that \(g\) is bijective with a strictly increasing inverse.
- The orbit \(a_{n+1}=g(a_n)\) satisfies the recurrence
  \[
  a_{n+2}=a_{n+1}+20a_n
  \]
  for all integers \(n\), yielding
  \[
  a_n=A(x)5^n+B(x)(-4)^n.
  \]
- If \(g(x)>x\), the entire two-sided orbit is strictly increasing; if \(g(x)<x\), it is strictly decreasing. This follows both forward using \(g\) and backward using \(g^{-1}\).
- For \(B(x)\ne0\), the differences \(a_{n+1}-a_n\) alternate in sign for sufficiently large negative \(n\), contradicting that monotonicity. Hence \(B(x)=0\) for every \(x\).
- Therefore \(g(x)=5x\), and the submission explicitly verifies strict increase, surjectivity, and the functional equation.

<points>7 out of 7</points>