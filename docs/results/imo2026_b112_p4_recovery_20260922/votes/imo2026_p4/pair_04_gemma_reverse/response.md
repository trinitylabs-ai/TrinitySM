# Proof comparison

## Proof A
Established theorem: Shan-Yu can guarantee a draw or win if $\theta/180^\circ \notin \mathbb{Q}$ or if $\theta \ge 120^\circ$.
Claim gap: The claim that Mulan can guarantee victory for all $\theta \in \mathbb{Q} \cdot 180^\circ$ with $\theta < 120^\circ$ is not justified and is mathematically incorrect. Specifically, the argument in lines 15-16 that Mulan can force a winning state in a finite state space of triples $(n_1, n_2, n_3)$ is hand-wavy and fails to account for Shan-Yu's ability to choose which triangle to keep.
Qualifications and supplied repairs: None.
Decisive checks:
- Line 3-7: The argument that Shan-Yu can avoid $\theta$ if $\theta/180^\circ \notin \mathbb{Q}$ is verified.
- Line 10: The argument that Shan-Yu can avoid $\theta \ge 120^\circ$ by starting with an equilateral triangle is verified.
- Line 16: The claim that Mulan can force a win for any $\theta = \frac{p}{q} 180^\circ < 120^\circ$ is a demonstrated defect. For example, if $\theta = 40^\circ$, Shan-Yu can maintain a state where no angle is a multiple of $40^\circ$ (e.g., starting with $(50^\circ, 60^\circ, 70^\circ)$), as shown in the audit.

## Proof B
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = 180^\circ/k$ for some integer $k \ge 2$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: None.
Decisive checks:
- Line 3: The reduction of a triangle with an angle $n\theta$ to one with angle $\theta$ is verified.
- Line 5-11: The proof that Mulan can force an angle in $W = \{n\theta\}$ if $\theta = 180^\circ/k$ is verified. The case analysis for $k=2$ and $k=3$ is correct.
- Line 13-21: The proof that Shan-Yu can avoid $W$ if $180^\circ$ is not a multiple of $\theta$ is verified. The four cases (lines 17-20) exhaustively prove that Mulan cannot force both resulting triangles to have an angle in $W$ if the current triangle has none.

## Decision
Winner: B
Reason: Proof B is complete and correct. It correctly identifies the winning condition as $\theta = 180^\circ/k$ and provides a rigorous strategy for both players. Proof A's conclusion is incorrect, as it claims Mulan wins for all rational multiples $\theta < 120^\circ$, and its justification for the final phase of the game is logically insufficient.