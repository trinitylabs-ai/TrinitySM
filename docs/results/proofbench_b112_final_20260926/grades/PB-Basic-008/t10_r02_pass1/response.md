The algebraic reduction is correct:
\[
ab+bc+ca=\frac{1-(a^2+b^2+c^2)}2,
\]
so it suffices to prove
\[
\sum_{\rm cyc}\left(\sqrt a+\frac{3\sqrt3}{2}(a^2-a)\right)\ge 0.
\]

For
\[
h(x)=\sqrt{x}+\frac{3\sqrt3}{2}(x^2-x),
\]
the derivative and factorization are correctly computed:
\[
h'(x)=\frac{6\sqrt3u^3-3\sqrt3u+1}{2u},\qquad u=\sqrt x,
\]
and
\[
6\sqrt3u^3-3\sqrt3u+1
=\left(u-\frac1{\sqrt3}\right)(6\sqrt3u^2+6u-\sqrt3).
\]
The sign analysis establishes that \(h\) increases, then decreases to \(h(1/3)=0\), and subsequently increases. Together with the continuous extension \(h(0)=0\), this rigorously gives \(h(x)\ge0\) on \((0,1)\).

Summing \(h(a),h(b),h(c)\ge0\) yields exactly the desired inequality. Since the variables are positive and the only interior zero of \(h\) is \(1/3\), the equality characterization \(a=b=c=1/3\) is also correct.

<points>7 out of 7</points>