The proposed solution is complete and correct.

- Strict increase gives injectivity; together with surjectivity, \(g\) is bijective, so all positive and negative iterates are well-defined.
- Applying the functional equation to each iterate correctly yields
  \[
  x_{n+2}=x_{n+1}+20x_n,
  \]
  whose general solution is
  \[
  x_n=A5^n+B(-4)^n.
  \]
- The argument that every orbit is strictly increasing, strictly decreasing, or constant is valid, including for negative indices, because both \(g\) and \(g^{-1}\) are strictly increasing.
- Hence \(\Delta_n=x_{n+1}-x_n\) must have a constant sign (or vanish identically). As \(n=-m\to-\infty\), the \(B(-4)^n\) contribution dominates the \(A5^n\) contribution and alternates in sign. Therefore \(B=0\).
- Consequently \(g(x)=5x\) for every \(x\).
- The submission explicitly verifies strict increase, surjectivity, and the functional equation for this candidate.

The preliminary continuity argument is correct, though unnecessary.

<points>7 out of 7</points>