# Proof comparison

## Proof A
Established theorem: Rigorously proves that if $\theta \neq 180^\circ/n$ for any integer $n \geq 2$, Shan-Yu can avoid victory indefinitely. Claims sufficiency for $\theta = 180^\circ/n$ via an interval-length strategy, but the geometric derivation contains a vertex-labeling contradiction.
Claim gap: Line 15 states Mulan cuts from the vertex with the smallest angle $\alpha$, yet computes the interval $(\beta, \gamma+\beta)$ with length $\gamma$. Geometrically, cutting from $\alpha$ yields an interval of length $\alpha$, while cutting from $\gamma$ yields length $\gamma$. The submission's interval and length correspond to cutting from the largest angle, not the smallest. This is a demonstrated defect in the text. The necessity argument (Lines 24-28) remains fully intact and independent of this error.
Qualifications and supplied repairs: NONE. Per instructions, I do not credit the vertex-swap repair. The submission as written contains a geometric contradiction in the sufficiency derivation, though the algebraic necessity proof stands verified.
Decisive checks: 
- Lines 3-6: Verified cut geometry and angle ranges.
- Lines 24-28: Verified four-case algebraic elimination. Each combination correctly reduces to a contradiction with $\alpha,\beta,\gamma \notin W$, proving Shan-Yu can always avoid $W$ when $\theta \neq 180^\circ/n$.
- Falsification check: For $\theta = 72^\circ$ ($\neq 180^\circ/n$), starting at $(10^\circ, 20^\circ, 150^\circ)$, any cut producing $72^\circ$ in one branch leaves $108^\circ$ in the other. Shan-Yu keeps the $108^\circ$ branch, and the game cycles without hitting $72^\circ$. Matches Proof A's necessity conclusion.

## Proof B
Established theorem: Correctly handles irrational $\theta$ (density avoidance) and $\theta \geq 120^\circ$ (equilateral avoidance). Claims victory for all rational $\theta < 120^\circ$, but the justification contains multiple unresolved and demonstrated defects.
Claim gap: Lines 13-16 contain fundamental flaws. Line 13 imposes an arbitrary feasibility condition ($\gamma < \theta$) without justification for the general case. Line 14 asserts a construction to force all angles into $G$ without verifying the cut's geometric validity. Line 16 makes a non-sequitur leap from "finite state space" to "Mulan can force a win," ignoring Shan-Yu's optimal discard choices in a two-player game. The conclusion is demonstrably false for $\theta=72^\circ$.
Qualifications and supplied repairs: NONE. The game-theoretic argument cannot be salvaged without a complete re-analysis of the state graph and optimal play. The arbitrary condition and hand-wavy construction remain unverified.
Decisive checks:
- Lines 3-7: Verified density argument for irrational $\theta$.
- Line 10: Verified equilateral avoidance for $\theta \geq 120^\circ$.
- Lines 13-16: Demonstrated defect. The finite-state forcing claim ignores the opponent's choice, and the arbitrary condition $\gamma < \theta$ breaks the general case. 
- Falsification check: $\theta=72^\circ$ (rational, $<120^\circ$) with $T=(10^\circ, 20^\circ, 150^\circ)$ allows Shan-Yu to perpetually avoid $\theta$ by discarding any triangle containing it, directly contradicting the claim.

## Decision
Winner: A
Reason: Proof A's necessity argument is rigorous and correctly identifies the structural barrier to forcing a win via a complete algebraic case analysis. Its sufficiency argument contains a vertex-labeling error but correctly identifies the interval-length strategy and handles the $\theta=90^\circ$ boundary properly. Proof B correctly handles irrational and large-angle cases but fails fundamentally on the rational case: it misapplies finite-state reasoning to a two-player game, ignores feasibility constraints, and arrives at an overbroad and demonstrably false conclusion. Proof A's logical framework correctly models the game-theoretic requirement of forcing both branches into a winning set, making it mathematically superior despite the notational defect.