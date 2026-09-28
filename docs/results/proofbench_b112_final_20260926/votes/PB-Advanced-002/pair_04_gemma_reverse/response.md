# Proof comparison

## Proof A
Established theorem: $M(f) \le 120 + g(120) \ll 2^{70}$, where $g(n)$ is Landau's function.
Claim gap: The pre-period $m_i \le 120$ is an underestimate; the pre-period of the sequence $f^k(\{i\})$ (corresponding to the entries of the Boolean adjacency matrix $M^k$) can be as large as $(n-1)^2 + 1$. Additionally, the claim that the period $p_i$ is the "least common multiple of the lengths of all cycles reachable from $i$" is mathematically incorrect; the period of the sequence $S_k$ is the LCM of the periods of the SCCs (where the period of an SCC is the GCD of its cycle lengths).
Qualifications and supplied repairs: None.
Decisive checks:
- Line 20: The claim $m_i \le 120$ is incorrect for general directed graphs. While the distance to a cycle is at most $n$, the sequence of sets $S_k$ only becomes periodic once the SCCs are "filled," which takes up to $(n-1)^2 + 1$ steps.
- Line 20: The claim that $p_i$ is the LCM of all cycle lengths is incorrect. The period of the sequence $S_k$ is the LCM of the periods of the SCCs. The LCM of all cycle lengths can be significantly larger than $g(n)$.

## Proof B
Established theorem: $M(f) \le 14162 + g(120) \ll 2^{70}$, where $g(n)$ is Landau's function.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: None.
Decisive checks:
- Lines 11-13: Correctly identifies that $A_1, \dots, A_t$ must be a subsequence of an orbit of $f$.
- Lines 21-23: Correctly identifies the period of the orbit as the LCM of the periods $d_i$ of the SCCs, where $d_i = \gcd(\text{cycle lengths in } C_i)$, and correctly bounds this by $g(n)$ since $\sum d_i \le \sum |C_i| = n$.
- Lines 26-27: Correctly bounds the pre-period using the Boolean matrix exponent (Wielandt bound), $m(X) \le (n-1)^2 + 1 = 14162$.
- Line 33: Correctly compares the sum $g(120) + 14162$ to $2^{70}$.

## Decision
Winner: B
Reason: Proof B is mathematically rigorous and correct. Proof A contains two significant errors: it incorrectly claims the pre-period is at most $n$ (it is $O(n^2)$) and incorrectly describes the period of the sequence as the LCM of all cycle lengths (it is the LCM of the GCDs of cycle lengths within each SCC). While both proofs reach the correct final bound because $2^{70}$ is so large, Proof B's derivations are accurate and consistent.