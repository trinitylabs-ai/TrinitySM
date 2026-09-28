The reduction is correct:
\[
n(n+1)r-B(n,r)=\sum_{k=1}^n\lfloor 2kr\rfloor.
\]
Thus, with \(x=2r\), the condition becomes
\[
\sum_{k=1}^n\lfloor kx\rfloor\equiv0\pmod n.
\]

For integral \(x\), the submission correctly uses \(n=2\) to show that \(x\) must be even, and verifies that every positive even \(x\) works. Hence these give precisely positive integral \(r\).

For nonintegral \(x=I+f\), restricting to odd \(n\) correctly eliminates the integer-part contribution. The \(n=3\) condition yields exactly the alternatives \(f<1/3\) or \(f\ge2/3\).

The two stated inductions are terse but valid:

- From \(f<1/(2j+1)\), at the next odd modulus \(2j+3\), all earlier terms vanish and the final two terms have sum less than the modulus. Divisibility forces both to vanish, giving \(f<1/(2j+3)\), hence \(f=0\), a contradiction.
- From \(f\ge1-1/(2j+1)\), the next odd-modulus condition forces the two new floor terms to take their maximal values, yielding \(f\ge1-1/(2j+3)\). Thus \(f\ge1-1/n\) for arbitrarily large \(n\), contradicting \(f<1\).

Therefore all nonintegral \(x\) are excluded, and the final answer—positive integral \(r\)—is complete and correct.

<points>7 out of 7</points>