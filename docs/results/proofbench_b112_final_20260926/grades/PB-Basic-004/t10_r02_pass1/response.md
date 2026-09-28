The proof is complete and correct.

- It rigorously establishes \(g(0)=0\) and the sign preservation of \(g\) and \(g^{-1}\).
- Surjectivity and strict monotonicity ensure bijectivity, so bi-infinite iterates are valid.
- The recurrence
  \[
  x_{n+2}=x_{n+1}+20x_n
  \]
  is correctly solved as \(x_n=A5^n+B(-4)^n\).
- For negative iterates, the \((-4)^n\)-component becomes asymptotically dominant relative to the \(5^n\)-component and alternates in sign. Since every iterate of a nonzero starting point must retain its sign, this correctly forces \(B=0\).
- Consequently \(g(x)=5x\) for every \(x\), and the candidate is explicitly verified to be strictly increasing, surjective, and to satisfy the functional equation.

<points>7 out of 7</points>