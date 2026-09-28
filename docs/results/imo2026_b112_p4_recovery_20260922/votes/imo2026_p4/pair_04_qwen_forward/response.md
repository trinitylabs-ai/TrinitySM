# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory if and only if $\theta = 180^\circ/k$ for some integer $k \ge 2$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Descent from $W$ (Lines 1-3):** VERIFIED. If a triangle has angle $n\theta$, cutting that vertex into $\theta$ and $(n-1)\theta$ yields one triangle with $\theta$ (immediate win) and one with $(n-1)\theta$. Shan-Yu must keep the latter, strictly decreasing the integer coefficient. Finite descent guarantees termination.
- **Forcing into $W$ (Lines 5-11):** VERIFIED. For $\theta = 180^\circ/k$, the condition $180^\circ \in \{n\theta\}$ allows Mulan to target $B+\alpha = n\theta$. Line 7 correctly notes an interval of length $A > \theta$ contains a multiple of $\theta$. Lines 8-10 correctly handle the boundary $A,B,C \le \theta$ by showing $k \le 3$ and verifying the interval $(B, B+A)$ still contains a multiple (specifically $90^\circ$ for $k=2$). The geometric angle relations $180^\circ - (B+\alpha) = (k-n)\theta$ are algebraically sound.
- **Avoidance Invariant (Lines 13-21):** VERIFIED. If $180^\circ$ is not a multiple of $\theta$, the four exhaustive conditions (Lines 17-20) for both child triangles to contain an angle in $W$ reduce to $A,B,C \in W$ or $180^\circ \in W$. Since Shan-Yu starts with $A,B,C \notin W$ and $180^\circ \notin W$, the invariant holds. This rigorously proves Shan-Yu's winning strategy for non-divisors.

## Proof B
Established theorem: Mulan loses for irrational $\theta$ and for $\theta \ge 120^\circ$. The claim that Mulan wins for all rational $\theta < 120^\circ$ is unsupported and false.
Claim gap: The proof fails to justify reachability in the reduced lattice game (Line 16), leading to an incorrect sufficient condition.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Irrational & $\theta \ge 120^\circ$ Cases (Lines 3-11):** VERIFIED. The density argument for irrational $\theta$ correctly shows Shan-Yu can avoid $\theta$. The equilateral triangle strategy for $\theta \ge 120^\circ$ correctly bounds all subsequent angles strictly below $120^\circ$, preventing $\theta$ from ever appearing.
- **Rational $\theta < 120^\circ$ Claim (Lines 12-16):** DEMONSTRATED DEFECT. The proof reduces the game to integers summing to $N = 180^\circ/\delta$ with target $m = \theta/\delta$, but asserts without proof that "Mulan can always choose a cut... to avoid cycles" and force the target. This is false. Counterexample: $\theta = 100^\circ$ ($\delta=20, N=9, m=5$). From state $(1,1,7)$, Mulan's possible cuts to create a 5 in $T_1$ require $a \in \{3,5\}$, while cuts to create a 5 in $T_2$ require $a \in \{2,4\}$. The sets are disjoint. Shan-Yu can always discard the winning triangle, forcing a cycle through states like $(4,1,4) \to (1,4,4)$ that permanently avoids 5. The finite state argument collapses because the target is not reachable from all states under optimal play.

## Decision
Winner: A
Reason: Proof A provides a complete, rigorously verified characterization ($\theta = 180^\circ/k$) using a correct descent argument, a verified interval-forcing lemma, and an airtight invariant for Shan-Yu's defense. Proof B correctly handles irrational $\theta$ and $\theta \ge 120^\circ$, but contains a fatal mathematical defect in Lines 12-16: it falsely claims Mulan wins for all rational $\theta < 120^\circ$ by hand-waving reachability in the reduced lattice game. The explicit counterexample $\theta = 100^\circ$ demonstrates that Shan-Yu can force a cycle avoiding $\theta$, invalidating Proof B's central claim. Proof A's logic is self-contained and correct.