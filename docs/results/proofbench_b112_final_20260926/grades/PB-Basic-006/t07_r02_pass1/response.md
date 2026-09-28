The contradiction setup is correct: if every \(P_k\) had \(k\) distinct real roots, then \(c_k\neq0\) for every \(k\).

The cited Pólya theorem is applicable here. Its crucial conclusion can also be verified directly: if \(r_1,\dots,r_n\) are the roots of \(P_n\), then Vieta gives
\[
\sum_{j=1}^n\frac1{r_j^2}
=\left(\frac{c_1}{c_0}\right)^2-2\frac{c_2}{c_0},
\qquad
\prod_{j=1}^n\frac1{r_j^2}=\frac{c_n^2}{c_0^2}.
\]
AM-GM therefore implies \(|c_n|^{1/n}\to0\), confirming the asserted infinite radius of convergence. This contradicts \(|c_n|\ge1\) for nonzero integers \(c_n\).

The Newton-inequality discussion is valid but unnecessary. The final argument is logically complete.

<points>7 out of 7</points>