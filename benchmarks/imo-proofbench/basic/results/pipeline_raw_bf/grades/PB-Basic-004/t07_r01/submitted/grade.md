The proof is complete and correct.

- Strict increase and surjectivity imply bijectivity, so all positive and negative iterates are well-defined, with \(g^{-1}\) strictly increasing.
- The recurrence
  \[
  x_{n+2}=x_{n+1}+20x_n
  \]
  is correctly derived for every \(n\in\mathbb Z\), and its general solution
  \[
  x_n=A5^n+B(-4)^n
  \]
  is correct.
- The orbit is indeed monotone: the sign of \(x_{n+1}-x_n\) is constant over all integers \(n\), unless the orbit is constant.
- If \(B\ne0\), then for sufficiently negative \(n\), the bracket in
  \[
  x_{n+1}-x_n=(-4)^n\left(4A\left(\frac5{-4}\right)^n-5B\right)
  \]
  has a fixed nonzero sign, while \((-4)^n\) alternates in sign. Thus consecutive differences alternate in sign, contradicting monotonicity. Hence \(B=0\).
- This yields \(g(x)=5x\) for every \(x\), and the candidate is correctly checked for strict increase, surjectivity, and the functional equation.

<points>7 out of 7</points>