# Proof comparison

## Proof A
Established theorem: For any love relation on $N=120$ students, the maximum size $t$ of a pairwise lovely-related set is bounded by the maximum trajectory length of $f$, which is at most $N^2 + g(N)$. The submission concludes $M(f) \le 2^{70}$.
Claim gap: NONE. The logical reduction to trajectory length and the structural bound $N^2 + g(N)$ are correct. The final inequality holds despite a numerical inaccuracy in an intermediate estimate.
Qualifications and supplied repairs: The claim that $g(120) \approx 3 \times 10^6$ is factually incorrect; Landau's function $g(120)$ is approximately $5.35 \times 10^9$ (using the prime-power partition $16+9+5+7+11+13+17+19+23=120$). This underestimate does not break the proof because the target bound $2^{70} \approx 1.18 \times 10^{21}$ is orders of magnitude larger than the true value. No substantive repair is needed for the conclusion.
Decisive checks: 
- Lines 9-11: Correctly deduces that $\forall 1 \le i < j \le t, \exists k_{ij} \in \mathbb{N}, f^{k_{ij}}(A_i) = A_j$ forces $\{A_i\}$ to lie on a single trajectory of $f$, reducing $M(f)$ to the maximum number of distinct elements in $\{v, vM, vM^2, \dots\}$. Quantifier order and functional determinism are correctly handled.
- Lines 13-15: Correctly applies Boolean matrix periodicity theory: trajectory length $\le$ pre-period + period. Pre-period $\le N^2$ and period $\le g(N)$ are standard bounds for $N \times N$ Boolean matrices.
- Line 14: Verified defect in estimating $g(120)$. The value $3 \times 10^6$ is off by four orders of magnitude. Verified that the true value $\approx 5.35 \times 10^9$ still satisfies $N^2 + g(N) \ll 2^{70}$.

## Proof B
Established theorem: For any love relation on $N=120$ students, $M(f) \le N^2 + g(N)$. Correctly estimates $g(120) \approx 2.6 \times 10^{10}$ (order of magnitude accurate) and concludes $M(f) \le 2^{70}$.
Claim gap: NONE. The argument is complete and numerically consistent.
Qualifications and supplied repairs: NONE. The partition $16+9+5+7+11+13+17+19+23=120$ is verified, and the resulting product correctly places $g(120)$ in the $10^{10}$ range. The pre-period bound $N^2$ and period bound $g(N)$ are correctly applied.
Decisive checks:
- Lines 11-14: Correctly identifies the lovely relationship condition as a chain in the reachability preorder, which must be contained in a single orbit of $f$. Quantifier handling ($\forall i<j \implies$ chain ordering) is explicit and correct.
- Lines 20-22: Correctly bounds the period by the LCM of SCC cycle lengths, invoking Landau's function $g(N)$.
- Lines 26-28: Provides a valid prime-power partition summing to 120 and correctly computes the product magnitude ($\approx 10^{10}$). The comparison $14400 + 2.6 \times 10^{10} \ll 10^{21}$ is arithmetically sound and rigorously justifies the target inequality.

## Decision
Winner: B
Reason: Both proofs correctly reduce the problem to bounding the maximum trajectory length of a Boolean matrix function and correctly apply the pre-period + period bound ($N^2 + g(N)$). Proof B is superior because it accurately estimates Landau's function $g(120)$ (order $10^{10}$) using a verified prime-power partition, whereas Proof A incorrectly states $g(120) \approx 3 \times 10^6$, underestimating it by four orders of magnitude. Although Proof A's error does not invalidate the final inequality due to the extreme looseness of $2^{70}$, Proof B demonstrates greater mathematical precision and correctly justifies the intermediate numerical claim without relying on an inaccurate approximation.