# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/n$ for some integer $n \geq 2$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- Lines 3-6 correctly derive the angle sets of the two resulting triangles and establish that the cut parameter $\psi = \angle BPC$ ranges over the open interval $(\alpha, 180^\circ-\beta)$ of length $\gamma$. This geometric setup precisely matches the problem's cut rule.
- Line 8 correctly establishes the finite termination strategy when an angle in $W = \{k\theta \mid k\theta < 180^\circ\}$ exists, using the decreasing multiplier invariant.
- Lines 15-17 rigorously handle the existence of a multiple of $\theta$ in the cut interval. The argument that an open interval of length $\gamma \geq \theta$ contains a multiple of $\theta$ unless its left endpoint is a multiple is correctly applied, and the hypothesis $\alpha \notin W$ explicitly closes the boundary case.
- Lines 24-28 exhaustively check the four logical combinations for forcing both subtriangles into $W$ when $\theta \neq 180^\circ/n$. Each combination correctly reduces to a contradiction via closure properties of $W$ under addition/subtraction, proving Shan-Yu can maintain the invariant "no angle in $W$".

## Proof B
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/k$ for some integer $k \geq 2$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Lines 3-4 correctly establish the finite termination strategy for angles in $W$.
- Lines 5-6 correctly parameterize the cut by $\alpha = \angle BAP \in (0, A)$ and derive the resulting angle sets. The identification of $B+\alpha$ and $180^\circ-B-\alpha$ as the critical angles is geometrically sound.
- Lines 7-10 correctly handle the interval $(B, B+A)$ of length $A$. The case split ($A > \theta$ vs. $A,B,C \leq \theta$) correctly covers all possibilities, and the $k \leq 3$ subcases are properly resolved.
- Lines 17-20 correctly eliminate the four combinations for forcing both subtriangles into $W$ when $\theta \neq 180^\circ/k$, using the same algebraic closure arguments as Proof A.

## Decision
Winner: A
Reason: Both submissions are mathematically correct and complete, establishing the same necessary and sufficient condition with valid strategies and impossibility proofs. Proof A is marginally stronger in its explicit geometric derivation: it carefully defines the cut parameter $\psi$, proves its exact open interval range $(\alpha, 180^\circ-\beta)$, and explicitly addresses the boundary condition for the existence of a multiple of $\theta$ within that interval (noting that $\alpha \notin W$ prevents the interval from sitting exactly between two multiples). Proof B's interval argument is correct but slightly glosses over the open-boundary nuance, relying on the strict inequality $A > \theta$ without explicitly ruling out the degenerate boundary case (though it is implicitly excluded). Proof A's case separation and step-by-step verification of the cut geometry provide a more rigorous justification of the decisive derivation.