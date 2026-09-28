# Proof comparison

## Proof A
Established theorem: The submission claims Liu can guarantee $c = \frac{n+1}{2n+1}$ by marking $n$ points to create pieces of lengths $\frac{1}{2n+1}$ and $\frac{2}{2n+1}$. It correctly identifies the game structure and the target value.
Claim gap: The lower bound derivation contains load-bearing defects. It restricts Xiang's strategy to a single point distribution ($m_1=0, m_i=1$) without proving it is the worst case, makes an unjustified "without loss of generality" assumption on split sizes, and employs a flawed pairing argument with index errors. The upper bound is a non-rigorous sketch.
Qualifications and supplied repairs: NONE. The argument relies on unverified case restrictions and contains arithmetic/indexing errors in the pairing step that cannot be repaired without rewriting the core inequality proof.
Decisive checks: 
- Line 9: "Suppose Xiang distributes his $n$ points such that $m_1=0$ and $m_i=1$..." restricts the quantifier from $\forall$ distributions to a single configuration. This is a **DEMONSTRATED defect**; the proof fails to cover other distributions or justify why this is optimal for Xiang.
- Line 11: "Assume without loss of generality that $p_{i,1} \ge x \ge p_{i,2}$" is a **DEMONSTRATED defect**. Xiang can split a piece of length $2x$ into $1.9x$ and $0.1x$, violating this assumption. The proof does not handle this case.
- Lines 16-27: The pairing argument to bound $S_{Xiang}$ is **UNRESOLVED/FLAWED**. Line 27 claims $S_{Xiang} \le \sum (p_{i,1}^{(j)} + p_{i,2}^{(j)}) = 2kx$, but the indices and pairing logic are inconsistent and do not rigorously bound the sum of the even-ranked pieces. The derivation collapses under scrutiny.

## Proof B
Established theorem: Liu can guarantee $c = \frac{n+1}{2n+1}$ by marking $n$ points to create $n+1$ equal pieces of length $\frac{1}{n+1}$. The proof correctly establishes that for any refinement by Xiang, Liu's share is minimized when all final pieces are equal, yielding the bound.
Claim gap: NONE for the lower bound. The upper bound (Xiang's strategy) is sketched but follows standard competitive game arguments; the lower bound is the rigorous core and is fully justified.
Qualifications and supplied repairs: NONE. The majorization principle (sum of odd-ranked elements is minimized when all elements are equal) is a standard, verified fact in inequality theory. The constraint that equal pieces may not be exactly achievable as a refinement only strengthens the inequality $L \ge \frac{n+1}{2n+1}$, as any deviation from equality increases Liu's share.
Decisive checks:
- Lines 12-16: Correctly applies the principle that $\sum_{i \text{ odd}} l_{(i)}$ is minimized at equality. For $M=2n+1$ pieces, the minimum is $\frac{n+1}{2n+1}$. This is a **VERIFIED fact**. The argument correctly handles the quantifier scope over all possible refinements.
- Line 11: Correctly handles $m \le 2n$ by noting $L \ge 1/2 \ge \frac{n+1}{2n+1}$.
- The argument cleanly covers all possible numbers of pieces and distributions without restrictive assumptions or index errors.

## Decision
Winner: B
Reason: Proof B provides a mathematically sound lower bound using the majorization principle, correctly identifying that equal piece distribution minimizes Liu's alternating sum. This avoids the restrictive assumptions and indexing errors that fatally undermine Proof A's derivation (specifically lines 9, 11, and 16-27). While both proofs sketch the upper bound, Proof B's lower bound is complete and rigorous, whereas Proof A's central derivation contains demonstrated defects and unresolved gaps. Proof B's argument is structurally superior and correctly justifies the claimed guarantee.