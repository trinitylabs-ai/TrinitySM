The factorization
\[
a(a-b)=(b+1)(b^2-b+1)
\]
and the resulting two cases are valid. Case 2 is handled correctly: the discriminant is computed accurately, \(m=1\) gives \((a,b)=(7,3)\), and all \(m\ge2\) are properly excluded.

However, Case 1 contains an algebraic error. From
\[
b+1=n^2(b^2-b+1)+nb
\]
the correct quadratic is
\[
n^2b^2+(-n^2+n-1)b+(n^2-1)=0,
\]
whereas the submitted solution omits the \(-b\) term. Consequently, its discriminant calculation and deduction \(n=1\) are not justified as written. There is also an inconsistency when \(n=1\): the displayed erroneous quadratic would give \(b^2=0\), while the solution later correctly obtains \(b^2=b\).

This is a minor, locally repairable gap: from \(a-b=n(b^2-b+1)>0\), one has \(a>b\); together with \(b+1=na\), this immediately forces \(n=1\), after which no prime \(b\) exists. Thus the core proof is sound and needs only a small correction, meriting 6 points rather than full credit.

<points>6 out of 7</points>