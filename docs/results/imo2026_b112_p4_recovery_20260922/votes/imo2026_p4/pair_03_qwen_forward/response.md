# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/n$ for some integer $n \ge 2$. The proof correctly establishes that if $\theta$ has this form, Mulan can force both resulting triangles to contain an angle in $W = \{k\theta \mid k\theta < 180^\circ\}$ in a single move, and subsequently reduce the multiplier until $\theta$ appears. If $\theta$ does not have this form, Shan-Yu can always preserve a triangle with no angles in $W$.
Claim gap: NONE. The argument covers all cases, handles the induction/reduction step correctly, and properly addresses Shan-Yu's optimal counterplay.
Qualifications and supplied repairs: NONE. The proof is self-contained and relies only on elementary geometry and properties of intervals.
Decisive checks: 
- Line 6 correctly identifies the valid range for $\psi$ as $(\alpha, 180^\circ-\beta)$ with length $\gamma$. This is verified via the exterior angle theorem and triangle sum.
- Line 17's claim that an interval of length $\gamma \ge \theta$ contains a multiple of $\theta$ is verified. The caveat "unless $\alpha$ is a multiple" correctly handles the boundary case where $\gamma = \theta$ and the interval is open; since $\alpha \notin W$, the multiple falls strictly inside.
- Lines 24-28 exhaustively check the four logical combinations for forcing both subtriangles into $W$ when $\theta \neq 180^\circ/n$. Each combination correctly reduces to a contradiction with the hypothesis that original angles are not in $W$.
- The induction step (Line 8) correctly notes that splitting $k\theta$ into $\theta$ and $(k-1)\theta$ guarantees the surviving triangle retains an angle in $W$ with a strictly smaller multiplier, ensuring termination.

## Proof B
Established theorem: Mulan can guarantee victory if and only if $\theta = 180^\circ/n$ for some integer $n \ge 2$. The proof uses an algebraic ansatz to set the third angles of the new triangles to multiples of $\theta$, derives necessary conditions on the cut, and shows an integer solution always exists when $\theta = 180^\circ/n$. The converse case mirrors A's logical exclusion.
Claim gap: NONE. The algebraic derivation is correct, and the existence of the required integer cut parameter is properly justified.
Qualifications and supplied repairs: NONE. The proof stands as written.
Decisive checks:
- Lines 6-9 correctly derive $(k_1+k_2)\theta = 180^\circ$ from the angle sum constraint. This algebraic step is verified.
- Lines 10-13 correctly translate positivity constraints on the split angles into the interval condition $k_1 \in (c/\theta, n - b/\theta)$ with length $a/\theta$.
- Line 14 correctly applies the fact that an open interval of length $>1$ contains an integer, and handles the $n=2$ boundary case explicitly.
- Lines 19-23 correctly show that if $\theta \neq 180^\circ/n$, forcing both subtriangles into $S$ implies an original angle is in $S$ or $180^\circ$ is a multiple of $\theta$, both contradictions.
- The strategy relies on a specific ansatz (making the third angles multiples), which is sufficient but slightly less geometrically direct than A's approach.

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct, arriving at the same necessary and sufficient condition with valid induction and case analysis. Proof A is preferred for its more direct geometric handling of the cut parameter $\psi$. A's interval argument (length $\gamma \ge \theta$) naturally leverages the triangle's largest angle and explicitly addresses the open-interval boundary condition, making the existence of a valid cut immediately transparent. Proof B's algebraic ansatz is valid but requires deriving and verifying a specific interval condition for the split angles, adding a layer of indirectness without increasing rigor. A's presentation of the four-case exclusion in the converse direction is also slightly more streamlined. The preference is based on mathematical clarity and directness of the central construction, not on correctness, as both are sound.