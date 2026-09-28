# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory if and only if $\theta = 180^\circ/k$ for some integer $k \ge 2$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Sufficiency (Lines 1-11):** The proof correctly shows that if $\theta = 180^\circ/k$, Mulan can force the game into the set $W = \{n\theta\}$. The interval argument on line 7 is verified: an open interval of length $A > \theta$ must contain a multiple of $\theta$ because the spacing between consecutive multiples is exactly $\theta$. The case analysis for $A,B,C \le \theta$ correctly bounds $k \le 3$ and handles $k=2,3$ without exception.
- **Necessity (Lines 13-21):** The proof establishes an invariant: the current triangle has no angle in $W$. It exhaustively checks the four logical pairings required for *both* child triangles to contain an angle in $W$ after a cut. Lines 17-20 correctly show that these pairings imply $A \in W$, $B \in W$, $C \in W$, or $180^\circ \in W$. Since the initial triangle avoids $W$ and $180^\circ \notin W$ (equivalent to $\theta \neq 180^\circ/k$), at least one child triangle always lacks an angle in $W$. Shan-Yu can perpetually maintain this invariant, preventing Mulan from ever producing $\theta \in W$. The quantifier order ($\forall$ cuts, $\exists$ safe child) and domain restrictions are rigorously maintained.

## Proof B
Established theorem: Shan-Yu wins if $\theta/180^\circ \notin \mathbb{Q}$ or $\theta \ge 120^\circ$. The proof does not establish victory for Mulan when $\theta$ is a rational multiple of $180^\circ$ and $\theta < 120^\circ$.
Claim gap: The sufficiency argument for rational $\theta < 120^\circ$ (Lines 12-17) is fundamentally flawed. It conflates forcing angles into the group $G = \{k \cdot \gcd(\theta, 180^\circ)\}$ with forcing the winning angle $\theta$. It also fails to address the geometric constraint $\gamma < \theta$ required for its proposed cutting strategy, and provides no justification for why a finite state space guarantees Mulan can force the specific winning configuration against optimal play.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Necessity (Lines 3-11):** The arguments for irrational $\theta$ and $\theta \ge 120^\circ$ are verified. The density argument for irrationals and the max-angle bound for $\theta \ge 120^\circ$ correctly show Shan-Yu can avoid $\theta$.
- **Sufficiency (Lines 12-17):** Demonstrated defect. For $\theta = 72^\circ$, $G$ contains multiples of $36^\circ$, but the winning set is $W = \{72^\circ, 144^\circ\}$. Shan-Yu can maintain the invariant that no angle lies in $W$ while allowing angles in $G \setminus W$ (e.g., $36^\circ, 108^\circ$). Proof B's claim on line 16 that "Mulan can always choose a cut... to force the state to $(m, n_2, n_3)$" is an unsupported assertion about game determinacy in a finite state space. It ignores Shan-Yu's ability to select the child triangle that avoids $W$, which directly contradicts the claimed victory condition. The move on line 13 also explicitly requires $\gamma < \theta$, leaving the case where all angles $\ge \theta$ unresolved.

## Decision
Winner: A
Reason: Proof A provides a complete, rigorous characterization of the winning values, correctly proving both sufficiency and necessity via a verified invariant that accounts for all cut configurations and quantifier dependencies. Proof B contains a fatal mathematical defect in its sufficiency argument: it incorrectly claims Mulan wins for all rational $\theta < 120^\circ$ (e.g., $\theta = 72^\circ$) by confusing the larger group $G$ with the actual winning set $W$, and fails to justify how Mulan can force $\theta$ against Shan-Yu's optimal avoidance strategy. Proof A's invariant argument directly refutes Proof B's sufficiency claim, making A the only mathematically sound submission.