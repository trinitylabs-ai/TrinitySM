# Proof comparison

## Proof A
Established theorem: Shan-Yu can guarantee a draw (avoid victory) if $\theta/180^\circ \notin \mathbb{Q}$ or if $\theta \ge 120^\circ$.
Claim gap: The proof that Mulan can guarantee victory for any $\theta \in \mathbb{Q} \cdot 180^\circ$ with $\theta < 120^\circ$ is incomplete. Step 16 claims that because the state space of triples $(n_1, n_2, n_3)$ is finite, Mulan can force the state to a winning one. This is a logical non-sequitur; the finiteness of a state space does not imply that a player can force a specific state in a game where the opponent chooses the transition.
Qualifications and supplied repairs: None.
Decisive checks:
- Step 3-7: Verified. If $\theta/180^\circ \notin \mathbb{Q}$, Shan-Yu can maintain a triangle with no angles in the group $S = \{n\theta + m 180^\circ\}$.
- Step 10: Verified. If $\theta \ge 120^\circ$, Shan-Yu can maintain all angles $< 120^\circ$ by starting with an equilateral triangle and always choosing the resulting triangle that preserves this property.
- Step 16: Demonstrated defect. The argument that Mulan can force a win in a finite state space is unsupported.

## Proof B
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/n$ for some integer $n \in \{2, 3, \dots\}$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: None.
Decisive checks:
- Step 8: Verified. If a triangle has an angle $\phi = k\theta$ for $k > 1$, Mulan can force an angle $\theta$ by cutting $\phi$ into $\theta$ and $(k-1)\theta$.
- Step 17: Verified. If $\theta = 180^\circ/n$, Mulan can force the game into the set $W = \{k\theta\}$ by picking a cut angle $\psi = k\theta$ in the interval $(\alpha, 180^\circ - \beta)$, which is possible since the interval length $\gamma \ge 60^\circ \ge \theta$ and $\alpha \notin W$.
- Step 24-28: Verified. If $\theta \neq 180^\circ/n$, Mulan cannot force both resulting triangles to have an angle in $W$ if the current triangle has none. This is proven by checking all four combinations of possible winning angles in $T_1$ and $T_2$, each leading to a contradiction of the hypothesis that $\alpha, \beta, \gamma \notin W$.

## Decision
Winner: B
Reason: Proof B is a complete and rigorous solution. It correctly identifies the winning condition $\theta = 180^\circ/n$ and provides a detailed proof for both sufficiency and necessity. Proof A's conclusion is incorrect (claiming all rational multiples of $180^\circ$ less than $120^\circ$ are winning), and its justification for the winning condition is a significant logical gap.