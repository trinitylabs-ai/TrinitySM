# Proof comparison

## Proof A
Established theorem: The maximum size $M(f)$ of a pairwise lovely-related set equals the maximum number of distinct elements in any trajectory of $f$. The trajectory length is bounded by the sum of a pre-period ($\le 120$) and a period bounded by Landau's function $g(120)$, yielding $M(f) \le 120 + g(120) \ll 2^{70}$.
Claim gap: NONE for the final inequality, but contains a conceptual imprecision in the period derivation that does not invalidate the bound.
Qualifications and supplied repairs: NONE. The argument is self-contained. The overestimation of the period is noted as a conceptual looseness but requires no repair to satisfy the requested inequality.
Decisive checks: 
- Line 15 correctly deduces that the pairwise lovely relationship condition forces $\{A_1, \dots, A_t\}$ to be a subsequence of a single functional trajectory, reducing $M(f)$ to the maximum trajectory length.
- Line 20 claims the period equals the "least common multiple of the lengths of all cycles reachable from $i$". This is conceptually imprecise: the true period of a trajectory entering a strongly connected component (SCC) is the LCM of the *periods* of those SCCs, where each SCC's period is the *GCD* of its internal cycle lengths. Taking the LCM of all cycle lengths overestimates the period. However, since the sum of cycle lengths in any graph of $n$ vertices is $\le n$, this overestimate is still bounded by $g(n)$, so the upper bound remains valid.
- Lines 24-34: The numerical comparison $120 + g(120) \ll 2^{70}$ is verified. The estimate $g(120) \approx 2.23 \times 10^8$ is slightly conservative but safely below $10^{21}$.

## Proof B
Established theorem: $M(f)$ equals the maximum orbit size of $f$. Using Boolean matrix representation and SCC decomposition, the period is correctly identified as the LCM of SCC periods (each being the GCD of cycle lengths), bounded by $g(120)$. The pre-period is bounded by the Wielandt bound $(n-1)^2+1$. This yields $M(f) \le g(120) + 14162 \ll 2^{70}$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE. The argument relies on standard, correctly applied results from Boolean matrix theory and graph theory.
Decisive checks:
- Lines 11-13 correctly establish that the pairwise reachability condition implies a linear chain structure along a single orbit, justifying the reduction to maximum orbit size.
- Lines 21-22 precisely define the period of an SCC as the GCD of its cycle lengths and the total period as the LCM of these GCDs. This matches the exact graph-theoretic characterization of functional graph periods.
- Lines 26-27 correctly cite the Wielandt bound for the pre-period of Boolean matrix powers. While looser than the tight bound $n-1$, it is a rigorously justified upper bound that comfortably satisfies the inequality.
- Lines 32-33: The numerical comparison is accurate and sufficient.

## Decision
Winner: B
Reason: Both proofs correctly reduce the problem to bounding the maximum trajectory length and successfully establish $M(f) \le 2^{70}$. Proof B is mathematically stronger because it precisely characterizes the period as the LCM of SCC periods (where each SCC period is the GCD of cycle lengths), whereas Proof A loosely claims the period is the LCM of all cycle lengths. While A's overestimation does not break the upper bound, B's derivation is rigorously correct and aligns with standard graph-theoretic results. Additionally, B provides a formally cited bound for the pre-period and a more accurate range for $g(120)$, demonstrating greater precision in its algebraic and combinatorial justifications.