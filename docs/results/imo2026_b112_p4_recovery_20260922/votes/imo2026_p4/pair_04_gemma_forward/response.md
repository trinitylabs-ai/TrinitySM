# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/k$ for some integer $k \ge 2$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- The "safe state" argument (lines 13-21) is verified: if $W = \{n\theta \mid n \in \mathbb{N}, n\theta < 180^\circ\}$ and the current triangle $T$ has no angle in $W$, then for any cut $\alpha$ of vertex $A$, Mulan can only force both resulting triangles $T_1$ and $T_2$ to have an angle in $W$ if $A \in W$, $B \in W$, $C \in W$, or $180^\circ$ is a multiple of $\theta$. Since none of these are true, Shan-Yu can always maintain the safe state by discarding the triangle that enters $W$.
- The "forcing into $W$" argument (lines 5-11) is verified: if $\theta = 180^\circ/k$, Mulan can force the game into $W$ in one step by picking $\alpha$ such that $B+\alpha = n\theta$, which is possible if $A > \theta$. The case $A, B, C \le \theta$ is correctly handled for $k=2, 3$ (for $k=3$, $\theta=60^\circ$, $A=B=C=60^\circ$ is in $W$; for $k=2$, $\theta=90^\circ$, $B < 90 < B+A$ is always true).
- The "winning from $W$" argument (line 3) is verified: if $T$ has an angle $n\theta \in W$, Mulan can force the game to a triangle with an angle $(n-1)\theta \in W$ or win immediately by cutting $n\theta$ into $\theta$ and $(n-1)\theta$.

## Proof B
Established theorem: Mulan can guarantee victory if $\theta \in \mathbb{Q} \cdot 180^\circ$ and $\theta < 120^\circ$. (Note: This is the claimed result, but the proof is incomplete).
Claim gap: The argument for $\theta < 120^\circ$ (lines 12-16) is a sketch and does not constitute a proof. It fails to demonstrate how Mulan can avoid cycles in the finite state space or how she can specifically force the state to a winning triple $(m, n_2, n_3)$.
Qualifications and supplied repairs: The argument for $\theta \ge 120^\circ$ (line 10) is a valid observation that Shan-Yu can avoid $\theta$ by starting with an equilateral triangle.
Decisive checks: The central claim that $\theta$ only needs to be a rational multiple of $180^\circ$ is falsified by the counterexample $\theta = 40^\circ$ (where $180/40 = 4.5$). In this case, $W = \{40^\circ, 80^\circ, 120^\circ\}$. For $T = (50^\circ, 60^\circ, 70^\circ)$, any cut $\alpha$ that puts $T_1$ in $W$ (e.g., $\alpha=40^\circ \implies T_1=(40, 60, 80)$) results in $T_2$ not being in $W$ (e.g., $T_2=(10, 70, 100)$), allowing Shan-Yu to maintain a safe state.

## Decision
Winner: A
Reason: Proof A provides a complete and rigorous derivation of the correct condition ($\theta = 180^\circ/k$). It correctly identifies the "safe state" (no angles being multiples of $\theta$) and proves that this state can be maintained by Shan-Yu unless $180^\circ$ is a multiple of $\theta$. Proof B reaches a different, incorrect conclusion and provides only a hand-wavy sketch for its primary claim.