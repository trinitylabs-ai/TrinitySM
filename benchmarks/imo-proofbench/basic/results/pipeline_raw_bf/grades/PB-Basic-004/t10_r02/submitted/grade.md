The proposed solution is complete and rigorous.

- Strict increase and surjectivity imply bijectivity, so all positive and negative iterates are well-defined and strictly increasing.
- The recurrence
  \[
  a_{n+2}=a_{n+1}+20a_n
  \]
  and its solution
  \[
  a_n=A(x)5^n+B(x)(-4)^n
  \]
  are correct.
- The coefficients are correctly computed as
  \[
  A(x)=\frac{g(x)+4x}{9},\qquad B(x)=\frac{5x-g(x)}9.
  \]
- Comparing negative iterates for \(x>y\), and separately taking even and odd \(k\to\infty\), validly gives both \(\Delta B\ge0\) and \(\Delta B\le0\). Hence \(B\) is constant.
- The fixed-point argument correctly establishes \(g(0)=0\), so that constant is \(B(0)=0\).
- Therefore \(g(x)=5x\), and the submission explicitly verifies that this candidate satisfies every condition.

The briefly stated incorrect intermediate calculation for \(A(x)\) is immediately identified and corrected, so it does not affect the proof.

<points>7 out of 7</points>