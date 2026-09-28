The recurrence
\[
a_{n+2}=a_{n+1}+20a_n
\]
and its solution
\[
a_n=A(x)5^n+B(x)(-4)^n
\]
are correctly derived. The argument that \(A\) is strictly increasing is also valid when interpreted as comparing iterates arising from \(x<y\). The identity
\[
B(g(x))=-4B(x)
\]
is correct.

However, the crucial conclusion \(B\equiv0\) is not proved. In particular:

- The assertion \(g(x)\sim5x\) as \(x\to\infty\) is unsupported and essentially assumes the unwanted \(B\)-term is negligible.
- With \(\epsilon(x)=B(x)/x\), the correct identities are
  \[
  g(x)=x(5-9\epsilon(x)),\qquad
  \epsilon(g(x))=\frac{-4\epsilon(x)}{5-9\epsilon(x)},
  \]
  not the formulas stated.
- Even the claimed recurrence would not show that an iterate must attain exactly a value making \(g(x)=0\).
- Surjectivity is not used to extend the orbit to negative indices, which is the key mechanism needed to eliminate the \((-4)^n\) term.
- The fact \(g(0)=0\) is asserted but not proved.

Thus the candidate \(g(x)=5x\) is correctly checked, but uniqueness has a major gap. The correctly constructed recurrence meets the stated partial-credit criterion.

<points>1 out of 7</points>