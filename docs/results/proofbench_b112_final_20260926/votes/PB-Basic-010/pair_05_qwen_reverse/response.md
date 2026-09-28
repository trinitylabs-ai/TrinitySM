# Proof comparison

## Proof A
Established theorem: For any partition of $\{1, 2, \ldots, 2022\}$ into two disjoint sets $A$ and $B$ of size $1011$, the sums $\sum_{(a, b) \in S_{AB}} (b - a)$ and $\sum_{(a, b) \in S_{BA}} (a - b)$ are strictly unequal.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: Lines 12–23 correctly combine the two sums into a single double sum over $A \times B$ and simplify to $n(\Sigma_B - \Sigma_A)$ using $|A|=|B|=n$. Lines 25–27 correctly compute the total sum $S = 1011 \times 2023$, verify it is odd, and derive a contradiction from $\Sigma_A = \Sigma_B \implies S = 2\Sigma_A$ (even). Verified facts: algebraic reduction, parity calculation, logical equivalence $L=R \iff \Sigma_A=\Sigma_B$. Demonstrated defects: none. Unresolved checks: none. Falsification check: attempted to construct a partition with $\Sigma_A = \Sigma_B$; parity constraint makes this impossible for any partition of the given set, confirming the universal implication.

## Proof B
Established theorem: Identical to Proof A; establishes the strict inequality of the two sums for all valid partitions.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: Lines 7–18 perform the same algebraic reduction to $n(\Sigma_B - \Sigma_A)$, with a slightly more explicit inner-sum expansion. Lines 21–25 replicate the parity contradiction argument exactly. Verified facts: double-sum expansion, parity of total sum, non-zero multiplier $n$. Demonstrated defects: none. Unresolved checks: none. Falsification check: identical to A; the odd total sum universally prevents $\Sigma_A = \Sigma_B$, so no counterexample exists under the problem's hypotheses.

## Decision
Winner: A
Reason: Both proofs are mathematically complete, correct, and structurally identical in their core strategy: reducing the difference of sums to $n(\Sigma_B - \Sigma_A)$ and using the odd parity of the total sum to prove $\Sigma_A \neq \Sigma_B$. Neither contains gaps, false claims, or unjustified leaps. The preference for A is weak and arbitrary, chosen only because its explicit statement of the partition properties of $S_{AB}$ and $S_{BA}$ (lines 10–11) provides a marginally clearer setup, though B's inner-sum expansion is equally valid. Since the mathematical content, rigor, and conclusions are indistinguishable, the decision follows the prompt's instruction to select one when proofs are equivalent.