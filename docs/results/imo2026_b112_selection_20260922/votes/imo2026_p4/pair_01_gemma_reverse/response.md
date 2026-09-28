# Proof comparison

## Proof A
Established theorem: If $\theta/180^\circ \notin \mathbb{Q}$, Shan-Yu can avoid $\theta$ indefinitely.
Claim gap: The proof fails to justify why $\theta \in \mathbb{Q} \cdot 180^\circ$ and $\theta < 120^\circ$ are sufficient for Mulan to win. Step 16 is a hand-wavy assertion that Mulan can force the state to a winning triple in a finite state space, without providing a mechanism or proof that such a sequence of moves exists and avoids cycles. Furthermore, the claim that $\theta \in \mathbb{Q} \cdot 180^\circ$ is sufficient is mathematically incorrect (e.g., $\theta = 40^\circ$ is a rational multiple of $180^\circ$ but is a win for Shan-Yu).
Qualifications and supplied repairs: NONE.
Decisive checks: The central derivation for sufficiency (Step 12-16) is a gap; it asserts a result about a finite state space without demonstrating the existence of a winning strategy. The claim $\theta \in \mathbb{Q} \cdot 180^\circ$ is falsified by the logic in Proof B.

## Proof B
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/k$ for some integer $k \ge 2$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- The sufficiency of $\theta = 180^\circ/k$ is verified: Mulan can force an angle in $W = \{n\theta\}$ in one step if $A > \theta$ (Step 6-7), and if $A, B, C \le \theta$, then $k \le 3$ (Step 8), with $k=3$ being an immediate win and $k=2$ being a win in one step (Step 10). Once an angle $n\theta$ is present, she can reduce $n$ until $n=1$ (Step 3).
- The necessity of $\theta = 180^\circ/k$ is verified: If $180^\circ$ is not a multiple of $\theta$, Shan-Yu can maintain a state where no angle is in $W$ (Step 13-21). The four cases analyzed in Steps 17-20 exhaustively show that Mulan cannot force both resulting triangles to have an angle in $W$ unless the current triangle already has an angle in $W$ or $180^\circ$ is a multiple of $\theta$.

## Decision
Winner: B
Reason: Proof B is complete and correct, identifying the precise condition $\theta = 180^\circ/k$ and providing a rigorous proof for both sufficiency and necessity. Proof A identifies an incorrect condition ($\theta \in \mathbb{Q} \cdot 180^\circ$ and $\theta < 120^\circ$) and fails to provide any substantive proof for the sufficiency of that condition, relying instead on vague assertions about finite state spaces.