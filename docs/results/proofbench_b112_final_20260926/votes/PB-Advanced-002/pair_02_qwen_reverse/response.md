# Proof comparison

## Proof A
Established theorem: For any directed graph on $N=120$ vertices, the maximum size $M(f)$ of a set of distinct subsets pairwise related by forward iteration of $f$ is bounded by the maximum trajectory length of $f$, which is at most $N + g(N)$, where $g(N)$ is Landau's function. Since $120 + g(120) \ll 2^{70}$, the inequality $M(f) \le 2^{70}$ holds.
Claim gap: NONE. The reduction to trajectory length, the decomposition into pre-period and period, and the bounding of each component are all mathematically sound and sufficient to establish the requested inequality.
Qualifications and supplied repairs: NONE. The numerical approximation $g(120) \approx 2.23 \times 10^8$ is a significant underestimate (the true value is $\sim 10^{15}$), but this is harmless as the inequality $g(120) < 2^{70}$ remains robustly true. No substantive repair was needed.
Decisive checks: 
- **VERIFIED**: Line 15 correctly deduces that the pairwise lovely relationship condition ($f^{k_{ij}}(A_i) = A_j$ for $i<j$) forces all $A_j$ to lie on the unique forward trajectory of $A_1$, making $M(f)$ equal to the maximum number of distinct elements in any trajectory.
- **VERIFIED**: Lines 20-22 correctly identify that the period of the subset sequence divides the LCM of all cycle lengths reachable from $X$, bounded by $g(120)$, and the pre-period is bounded by the maximum distance to a cycle, $\le 120$.
- **Falsification check**: Consider a graph with disjoint cycles of lengths partitioning 120. The period is exactly the LCM of the partition, maximized by $g(120)$. The pre-period is 0. The trajectory length is $g(120) < 2^{70}$. The bound holds under all valid configurations.

## Proof B
Established theorem: Same as Proof A. Reduces $M(f)$ to the maximum trajectory length of a Boolean matrix power sequence, bounds pre-period by $N^2$ and period by $g(N)$, and concludes $M(f) \le 2^{70}$.
Claim gap: NONE. The conclusion is correct and the bounding strategy is valid.
Qualifications and supplied repairs: NONE. The approximation $g(120) \approx 3 \times 10^6$ is also an underestimate but does not affect the final inequality. The pre-period bound $P \le N^2$ is a safe overestimate (the true bound is $N$), which is acceptable.
Decisive checks:
- **VERIFIED**: Line 11 correctly identifies that the pairwise condition forces the sets to form a subsequence of a single trajectory.
- **DEMONSTRATED DEFECT (Non-load-bearing)**: Line 14 states "The period of an SCC is the greatest common divisor of its cycle lengths." This describes the index of imprimitivity (cyclic decomposition), not the period of the sequence $M^k$. The period of the sequence is the LCM of cycle lengths. However, the proof immediately corrects course by stating the maximum period is $g(N)$, which is the correct LCM-based bound. This terminology slip does not break the logical chain but reduces precision.
- **Falsification check**: Same as A. The matrix formulation correctly captures the dynamics, and the bounds $N^2 + g(N) \ll 2^{70}$ are valid.

## Decision
Winner: A
Reason: Both proofs correctly reduce the problem to bounding the trajectory length of $f$ and successfully apply Landau's function to bound the period, yielding a result far below $2^{70}$. Proof A is preferred because its explanation of the period mechanism is mathematically precise: it correctly identifies the period as the LCM of reachable cycle lengths and the pre-period as the maximum distance to a cycle. Proof B confuses the GCD of cycle lengths (index of imprimitivity) with the period of the sequence, requiring an implicit correction to reach the correct Landau bound. While both reach the correct conclusion, Proof A's derivation is cleaner and avoids the terminology error, making it the stronger justified solution.