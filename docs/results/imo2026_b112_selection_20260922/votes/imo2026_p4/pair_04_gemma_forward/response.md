# Proof comparison

## Proof A
Established theorem: Mulan cannot guarantee victory if $\theta/180^\circ \notin \mathbb{Q}$ or if $\theta \ge 120^\circ$.
Claim gap: The claim that Mulan can guarantee victory for any $\theta \in \mathbb{Q} \cdot 180^\circ$ with $\theta < 120^\circ$ is not justified. The proof asserts that Mulan can force a win in a finite state space (lines 15-16) but fails to demonstrate that she can avoid cycles or force the state toward the winning condition.
Qualifications and supplied repairs: NONE.
Decisive checks: The claim that $\theta < 120^\circ$ is sufficient for any rational multiple of $180^\circ$ is falsified by $\theta = 40^\circ$. For $\theta = 40^\circ$, Shan-Yu can maintain the game in a loop of triangles such as $(60^\circ, 60^\circ, 60^\circ)$, $(20^\circ, 60^\circ, 100^\circ)$, and $(20^\circ, 20^\circ, 140^\circ)$, none of which contain an angle of $40^\circ$. For any cut Mulan makes, Shan-Yu can always choose a resulting triangle from this set, avoiding victory indefinitely.

## Proof B
Established theorem: Mulan can guarantee victory if and only if $\theta = \frac{180^\circ}{n}$ for some integer $n \ge 2$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Sufficiency: If $\theta = 180^\circ/n$, Mulan can force an angle in $S = \{k\theta \mid k \in \mathbb{N}, k\theta < 180^\circ\}$. The derivation in lines 5-14 correctly shows that if $T$ has no angle in $S$, Mulan can force a cut such that both resulting triangles have an angle in $S$. Once an angle $k\theta$ is present, she can iteratively reduce $k$ to 1 (line 1), forcing an angle of $\theta$.
- Necessity: If $\theta \neq 180^\circ/n$, the proof shows that if $T$ has no angle in $S$, any cut Mulan makes allows Shan-Yu to choose a triangle that also has no angle in $S$ (lines 16-24). The four cases analyzed in lines 19-23 exhaust all possibilities for both resulting triangles to have angles in $S$, proving that Shan-Yu can avoid $\theta$ indefinitely starting from $T = (60^\circ, 60^\circ, 60^\circ)$.
- Boundary case: The case $n=2$ ($\theta = 90^\circ$) is correctly handled in line 14.

## Decision
Winner: B
Reason: Proof B is mathematically complete and correct. It identifies the precise condition $\theta = 180^\circ/n$ and provides a rigorous proof for both sufficiency and necessity. Proof A's condition is too broad; it fails to account for the fact that Shan-Yu can force the game into a loop to avoid the specific angle $\theta$ for rational multiples of $180^\circ$ that are not of the form $180^\circ/n$.