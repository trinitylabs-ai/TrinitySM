# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory if and only if $\theta = 180^\circ/k$ for some integer $k \ge 2$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Sufficiency (Steps 5-11):** The proof correctly models the cut from vertex $A$ with split angle $\alpha$, yielding triangles with angles $\{\alpha, B, 180^\circ-B-\alpha\}$ and $\{A-\alpha, C, B+\alpha\}$. It correctly identifies that choosing $\alpha$ such that $B+\alpha = n\theta$ places both triangles in $W$ (since $180^\circ-n\theta = (k-n)\theta \in W$). The interval condition $B < n\theta < B+A$ has length $A$. The proof correctly argues that if $A > \theta$, the interval length guarantees a multiple of $\theta$. If $A \le \theta$, it correctly reduces to the global constraint $A+B+C \le 3\theta \implies k \le 3$, handling $k=2$ and $k=3$ rigorously. The implicit choice of vertex ensures the strategy covers all triangle shapes.
- **Necessity (Steps 13-21):** The proof correctly establishes that to force progress, Mulan must make *both* resulting triangles contain an angle in $W$ (otherwise Shan-Yu discards the winning candidate). The algebraic enumeration of the four combinations of conditions correctly shows that satisfying both simultaneously implies an original angle is in $W$ or $180^\circ \in W$. Since the initial triangle avoids $W$ and $\theta \neq 180^\circ/k$ implies $180^\circ \notin W$, the defense is airtight.

## Proof B
Established theorem: If Mulan can guarantee victory, then $\theta = 180^\circ/n$ for some integer $n \ge 2$ (Necessary condition only). The sufficiency claim is not established.
Claim gap: The constructive proof for sufficiency contains a fatal geometric mismatch. Step 15 states Mulan cuts from the vertex with the smallest angle $\alpha$, but then analyzes the interval for the cut angle $\psi$ as $(\beta, \gamma+\beta)$ with length $\gamma$. Cutting from vertex $A$ (angle $\alpha$) to side $BC$ actually produces an interval $(\gamma, \gamma+\alpha)$ with length $\alpha$. 
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Falsification of Attack (Steps 13-18):** Consider $\theta = 60^\circ$ ($n=3$) and triangle angles $10^\circ, 10^\circ, 160^\circ$. The smallest angle is $\alpha = 10^\circ$. Proof B's strategy dictates cutting from this vertex. The actual interval for the angle at the cut point is $(160^\circ, 170^\circ)$, which contains no multiple of $60^\circ$. The proof incorrectly uses the interval $(\beta, \gamma+\beta) = (10^\circ, 170^\circ)$, which corresponds to cutting from the vertex with angle $\gamma$ (or $\beta$), not $\alpha$. This geometric error invalidates the claimed winning strategy for obtuse triangles with a small smallest angle.
- **Necessity (Steps 20-29):** The defense argument correctly mirrors Proof A's logic, showing that forcing both triangles into $W$ is impossible when $\theta \neq 180^\circ/n$. This part is mathematically sound.

## Decision
Winner: A
Reason: Proof A provides a complete, rigorous derivation for both directions of the equivalence. It correctly handles the geometry of the cut intervals, properly accounts for vertex selection, and accurately proves that Shan-Yu can maintain a "safe state" when $\theta$ is not a rational divisor of $180^\circ$. Proof B contains a decisive geometric defect in its sufficiency argument: it mismatches the chosen cut vertex (smallest angle) with the interval properties of a different vertex (largest angle), causing the proposed strategy to fail for valid counterexamples (e.g., $10^\circ, 10^\circ, 160^\circ$ with $\theta=60^\circ$). While Proof B's necessity argument is correct, the failure to prove sufficiency makes it mathematically incomplete.