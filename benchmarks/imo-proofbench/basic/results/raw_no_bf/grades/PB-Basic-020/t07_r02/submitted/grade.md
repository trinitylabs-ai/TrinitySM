The Case 2 argument is correct: the resulting quadratic and discriminant are computed properly, all positive integers \(n\) are covered, and \(n=1\) yields \((a,b)=(7,3)\).

There is, however, an algebraic error in Case 1. From
\[
b+1=m\bigl(m(b^2-b+1)+b\bigr)
\]
the correct quadratic is
\[
m^2b^2-(m^2-m+1)b+(m^2-1)=0,
\]
not the one stated. Nevertheless, this is a locally repairable error: for \(m=1\), the corrected equation gives \(b(b-1)=0\), and for \(m\ge2\) its discriminant
\[
(m^2-m+1)^2-4m^2(m^2-1)
\]
is negative. Thus Case 1 still yields no prime \(b\), without changing the overall method or conclusion.

Accordingly, the solution is essentially complete but contains a minor calculation error.

<points>6 out of 7</points>