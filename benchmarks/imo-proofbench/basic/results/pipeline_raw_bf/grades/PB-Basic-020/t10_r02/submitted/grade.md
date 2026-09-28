The factorization
\[
a(a-b)=(b+1)(b^2-b+1)
\]
is correct, and the split according to \(\gcd(a,b+1)\in\{1,a\}\) is exhaustive.

- If \(a\mid b+1\), the substitution \(b=ma-1\) leads to the stated quadratic \(f(a)=0\). For \(m=1\), no prime pair results. For \(m\ge2\), \(f(2)=4m^3-6m^2+5m-3>0\), and \(f'(a)>0\) for \(a\ge2\), so no solution exists.
- If \(\gcd(a,b+1)=1\), Euclid’s lemma correctly gives \(a\mid b^2-b+1\). Introducing \(n\) yields the correct quadratic in \(b\) and discriminant
\[
D=n^4+2n^3+7n^2+2n-3.
\]
The cases \(n=1,2\) are handled correctly. For \(n\ge3\), \(D\) lies strictly between the consecutive squares \((n^2+n+2)^2\) and \((n^2+n+3)^2\), eliminating all such \(n\).

Finally, \(n=1\) gives \((a,b)=(7,3)\), which is correctly verified. The solution is complete and rigorous.

<points>7 out of 7</points>