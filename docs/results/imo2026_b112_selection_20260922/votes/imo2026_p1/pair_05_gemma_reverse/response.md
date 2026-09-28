# Proof comparison

## Proof A
Established theorem: (1) The process terminates with exactly one integer $M > 1$ on the blackboard. (2) The value of $M$ is $\prod_p p^{g_p}$, where $g_p = \gcd(v_p(a_1), \dots, v_p(a_{2026}))$, which is independent of the sequence of moves.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Termination: The proof uses a lexicographical potential function $(N, S)$, where $N$ is the number of integers greater than 1 and $S$ is the sum of the number of prime factors (with multiplicity). It correctly identifies that if $\gcd(m, n) > 1$, $S$ strictly decreases; if $\gcd(m, n) = 1$, $N$ strictly decreases. The argument that $N$ cannot drop from 2 to 0 is verified: $g=1$ and $h=1$ would imply $m=1$ and $n=1$, contradicting the premise $m, n > 1$ (lines 15-18).
- Invariance: The proof correctly identifies the operation on prime exponents as $(v_p(m), v_p(n)) \to (\min(v_p(m), v_p(n)), |v_p(m) - v_p(n)|)$. It uses the property $\gcd(a, b) = \gcd(\min(a, b), |a-b|)$ to establish that the $\gcd$ of the exponents for each prime $p$ is invariant. At termination, $N=1$ implies $v_p(M)$ is the only non-zero exponent, so $v_p(M) = \gcd(v_p(a_1), \dots, v_p(a_{2026}))$ (lines 22-32).

## Proof B
Established theorem: (1) The process terminates with exactly one integer $M > 1$ on the blackboard. (2) The value of $M$ is $\prod_p p^{G_p}$, where $G_p = \gcd(v_p(x_1), \dots, v_p(x_{2026}))$, which is independent of the sequence of moves.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Termination: The proof uses a lexicographical potential function $\Phi(S) = (P(S), N(S))$, where $P$ is the product of all integers and $N$ is the number of integers greater than 1. It correctly identifies that if $\gcd(m, n) > 1$, $P$ strictly decreases; if $\gcd(m, n) = 1$, $N$ strictly decreases. The argument that $N$ cannot drop from 2 to 0 is verified: $g=1$ and $L=1$ would imply $m=1$ and $n=1$, contradicting the premise $m, n > 1$ (lines 10-15).
- Invariance: The proof correctly identifies the operation on prime exponents as $(v_p(m), v_p(n)) \to (\min(v_p(m), v_p(n)), |v_p(m) - v_p(n)|)$. It uses the property $\gcd(a, b) = \gcd(\min(a, b), |a-b|)$ to establish that the $\gcd$ of the exponents for each prime $p$ is invariant. At termination, $N=1$ implies $v_p(M)$ is the only non-zero exponent, so $v_p(M) = \gcd(v_p(x_1), \dots, v_p(x_{2026}))$ (lines 20-31).

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct, employing the same invariant for the final value $M$ and similar lexicographical potential functions for termination. Proof B is slightly preferred for its more formal presentation and a more explicit derivation of the potential function's behavior.