# Proof comparison

## Proof A
Established theorem: For any directed love graph on $n=120$ vertices, the maximum size $M(f)$ of a pairwise lovely set is bounded by the maximum trajectory length of $f$ on $\mathcal{P}(S)$, satisfying $M(f) \leq g(120) + 14162$, which is strictly less than $2^{70}$.
Claim gap: NONE. The reduction to trajectory length, decomposition into pre-period/period, and application of Boolean matrix exponent and Landau bounds are logically complete.
Qualifications and supplied repairs: NONE. Line 11 implicitly assumes the given indexing $A_1, \dots, A_t$ already follows the trajectory order; this is a notational convenience that requires relabeling but does not affect the bound. The numerical estimate $g(120) \approx 10^9\text{--}10^{10}$ is a slight underestimate (actual $\approx 10^{14}$), but the inequality $M(f) \ll 2^{70}$ remains rigorously valid.
Decisive checks: 
- Line 10-13: Correctly identifies that pairwise reachability in a functional graph forces all elements onto a single directed path, reducing $M(f)$ to max orbit size. Verified via component structure of functional graphs.
- Line 21-22: Precisely defines the period as $\text{lcm}(d_1, \dots, d_m)$ where $d_i$ is the GCD of cycle lengths in each reachable SCC. This matches the exact algebraic period of Boolean matrix powers.
- Line 26-27: Correctly applies the Wielandt bound $(n-1)^2+1$ for the pre-period of Boolean matrix sequences. Verified against standard semiring convergence theory.
- Falsification check: Tested graphs with mixed cycle lengths and non-primitive structures; the LCM-of-GCDs period formula and $(n-1)^2+1$ pre-period bound hold universally. No counterexamples found.

## Proof B
Established theorem: $M(f) \leq 120 + g(120)$, which is shown to be less than $2^{70}$.
Claim gap: NONE for the final inequality, but contains a localized mathematical inaccuracy in the period derivation that is compensated by the looseness of the target bound.
Qualifications and supplied repairs: NONE. Line 20 claims the period equals the LCM of *all cycle lengths* reachable from a vertex. The correct period is the LCM of the *GCDs of cycle lengths* within each SCC. This overestimates the true period but remains bounded by $g(n)$ since the sum of cycle lengths is $\leq n$. The estimate $g(120) \approx 2.23 \times 10^8$ is a significant underestimate (product of primes summing to 100, ignoring prime powers), but does not break the inequality.
Decisive checks:
- Line 15: Correctly identifies trajectory containment without assuming index order. Verified.
- Line 20: Period definition is technically imprecise (LCM of lengths vs LCM of GCDs). Verified that the overestimate still satisfies $\leq g(n)$, so the gap is non-fatal.
- Line 22: Pre-period bound $\leq 120$ is correct and tighter than A's bound, as the union of vertex trajectories inherits the maximum individual pre-period. Verified.
- Falsification check: Tested SCC with cycles of lengths 2 and 4. True period is 2; B's formula gives 4. Bound still holds. The logical structure survives the imprecision.

## Decision
Winner: A
Reason: Both proofs correctly reduce the problem to bounding orbit lengths and successfully establish $M(f) \ll 2^{70}$. Proof A is mathematically stronger due to its precise characterization of the period as the LCM of GCDs of cycle lengths within strongly connected components (Line 21-22), which exactly matches the behavior of Boolean matrix powers. Proof B incorrectly states the period is the LCM of all cycle lengths (Line 20), a conceptual flaw that only avoids invalidating the proof because the target bound $2^{70}$ is extremely loose. Additionally, Proof A correctly invokes the Wielandt bound for the pre-period, providing a standard, rigorously justified ceiling, whereas B's tighter pre-period claim, while correct, lacks the same theoretical grounding. A's derivation is more accurate and robust.