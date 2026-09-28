# Proof comparison

## Proof A
Established theorem: Mulan can guarantee victory if and only if $\theta = 180^\circ/n$ for some integer $n \in \{2, 3, 4, \dots\}$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: In line 15, the proof states Mulan cuts from the vertex with the smallest angle $\alpha$, but then defines the interval for $\psi$ as $(\beta, \gamma + \beta)$, which corresponds to cutting from the vertex with the largest angle $\gamma$. This is a minor wording inconsistency; the mathematical derivation using the interval $(\beta, \gamma + \beta)$ is correct and sufficient.
Decisive checks: 
- The central derivation for Case 2 (lines 23-28) is verified. If $T$ has no angles in $W = \{k\theta \mid k \in \mathbb{Z}^+, k\theta < 180^\circ\}$, Mulan cannot force both resulting triangles $T_1$ and $T_2$ to have an angle in $W$. This is proven by checking all four combinations of possible winning angles in $T_1$ and $T_2$, each leading to a contradiction of the premise that $\alpha, \beta, \gamma \notin W$ or that $\theta \neq 180^\circ/n$.
- The derivation for Case 1 (lines 13-18) is verified. If $\theta = 180^\circ/n$, the interval $(\beta, \beta + \gamma)$ has length $\gamma \geq 60^\circ$. Since $\theta \leq 90^\circ$, and $\beta \notin W$, the interval must contain a multiple of $\theta$ (for $n=2$, $90^\circ$ is always in the interval; for $n \geq 3$, $\gamma \geq \theta$ ensures a multiple exists).

## Proof B
Established theorem: If $\theta/180^\circ \notin \mathbb{Q}$, Shan-Yu can avoid $\theta$ indefinitely.
Claim gap: The claim that Mulan wins for all $\theta \in \mathbb{Q} \cdot 180^\circ$ with $\theta < 120^\circ$ is not justified and is mathematically incorrect.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- The argument in line 16 is a hand-wave, stating that Mulan can "force the state to a different triple in $G$" and "force the maximum angle to change until it equals $m\delta$" without providing a mechanism or proof of reachability.
- Falsification: For $\theta = 40^\circ$ (which is $\frac{2}{9} 180^\circ < 120^\circ$), Proof B claims Mulan wins. However, using the logic from Proof A, $W = \{40^\circ, 80^\circ, 120^\circ, 160^\circ\}$. If $T$ starts with no angles in $W$, any cut results in at least one triangle with no angles in $W$. Shan-Yu can thus avoid $\theta$ indefinitely, contradicting Proof B.

## Decision
Winner: A
Reason: Proof A provides a complete and rigorous solution, correctly identifying the condition $\theta = 180^\circ/n$. It logically proves both the sufficiency of this condition (by showing Mulan can force the game into a set of winning angles $W$) and its necessity (by showing that if $\theta \neq 180^\circ/n$, Shan-Yu can avoid $W$ entirely). Proof B incorrectly concludes that any rational multiple of $180^\circ$ less than $120^\circ$ is a winning value, a claim that is easily falsified.