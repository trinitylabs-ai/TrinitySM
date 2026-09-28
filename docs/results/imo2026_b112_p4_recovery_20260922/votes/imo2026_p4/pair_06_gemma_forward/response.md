# Proof comparison

## Proof A
Established theorem: If $\theta/180^\circ \notin \mathbb{Q}$, Shan-Yu can avoid $\theta$ indefinitely. If $\theta \ge 120^\circ$, Shan-Yu can avoid $\theta$ indefinitely.
Claim gap: The claim that $\theta \in \mathbb{Q} \cdot 180^\circ$ and $\theta < 120^\circ$ is sufficient for Mulan to win is not justified and is mathematically incorrect. For example, if $\theta = 72^\circ$, Shan-Yu can avoid $\theta$ by starting with an equilateral triangle and always choosing the resulting triangle that does not contain a multiple of $72^\circ$. The argument in lines 15-16 regarding the finite state space is a sketch that fails to prove reachability of the winning state or the absence of cycles.
Qualifications and supplied repairs: NONE.
Decisive checks: The central derivation for the rational case (lines 12-16) is incomplete. It asserts that Mulan can force the state to a winning triple in a finite state space but provides no mechanism for doing so. A counterexample to the final claim is $\theta = 72^\circ$: if $T = (60^\circ, 60^\circ, 60^\circ)$, any cut $\alpha = \alpha_1 + \alpha_2$ results in $T_1 = (\alpha_1, 60^\circ, 120^\circ - \alpha_1)$ and $T_2 = (\alpha_2, 60^\circ, 120^\circ - \alpha_2)$. For $T_1$ to have an angle in $S = \{72^\circ, 144^\circ\}$, we must have $\alpha_1 = 72^\circ$ (impossible) or $120^\circ - \alpha_1 = 72^\circ \implies \alpha_1 = 48^\circ$. If Mulan chooses $\alpha_1 = 48^\circ$, then $T_2 = (12^\circ, 60^\circ, 108^\circ)$, which has no angle in $S$. Shan-Yu can continue this strategy.

## Proof B
Established theorem: Mulan can guarantee victory in finitely many steps if and only if $\theta = \frac{180^\circ}{n}$ for some integer $n \ge 2$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: The proof correctly identifies the winning condition $\theta = 180^\circ/n$. The sufficiency is proven by showing that if no angle is in $S = \{k\theta\}$, Mulan can force both resulting triangles to have an angle in $S$ provided $a > \theta$ (lines 5-14). The case $n=2$ ($\theta = 90^\circ$) is explicitly and correctly handled in line 14. The necessity is proven by showing that if $\theta \neq 180^\circ/n$, Shan-Yu can always choose a resulting triangle that has no angle in $S$ (lines 16-24). The four cases in lines 20-23 exhaustively cover the conditions under which both resulting triangles would have angles in $S$, and each leads to a contradiction of the hypotheses ($\theta \neq 180^\circ/n$ and $T$ has no angle in $S$).

## Decision
Winner: B
Reason: Proof B is mathematically complete and correct, providing a rigorous proof for both the necessary and sufficient conditions. Proof A's final answer is incorrect, and its justification for the rational case is a hand-waving argument that fails to establish the result.