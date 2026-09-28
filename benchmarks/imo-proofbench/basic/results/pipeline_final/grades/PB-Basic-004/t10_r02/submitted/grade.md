The proposed solution is complete and correct.

- Strict increase and surjectivity imply that \(g\) is bijective, so all positive and negative iterates are well-defined and strictly increasing.
- Applying the functional equation to every iterate correctly gives
  \[
  a_{n+2}=a_{n+1}+20a_n,
  \]
  whose bilateral solution is
  \[
  a_n=A(x)5^n+B(x)(-4)^n.
  \]
- For \(x>y\), monotonicity of every negative iterate yields inequalities for both even and odd \(k\). Letting \(k\to\infty\) correctly gives simultaneously
  \[
  B(x)-B(y)\ge 0
  \quad\text{and}\quad
  B(x)-B(y)\le 0,
  \]
  so \(B(x)=B(y)\). Thus \(B\) is constant.
- The fixed-point argument correctly establishes \(g(0)=0\), hence \(B(0)=0\), so \(B\equiv0\).
- It follows that \(g(x)=5x\), and the submission explicitly verifies strict increase, surjectivity, and the functional equation.

There are no substantive gaps or errors.

<points>7 out of 7</points>