# Proof comparison

## Proof A
Established theorem: None. The submission claims Liu can guarantee $\frac{n+1}{2n+1}$ by marking $n$ points to create $n+1$ equal pieces of length $\frac{1}{n+1}$.
Claim gap: The proposed strategy is fundamentally insufficient. For $n=1$, Xiang can cut one half into $\epsilon$ and $\frac{1}{2}-\epsilon$, yielding pieces $\{\frac{1}{2}, \frac{1}{2}-\epsilon, \epsilon\}$. Liu receives $\frac{1}{2} + \epsilon$, which approaches $\frac{1}{2}$ and is strictly less than the claimed bound $\frac{2}{3}$. Additionally, Line 11 asserts $1/2 \ge \frac{n+1}{2n+1}$, which is arithmetically false for all $n \ge 1$.
Qualifications and supplied repairs: None. The strategy fails under optimal play, and the inequality is incorrect. No repairs were supplied.
Decisive checks: 
- **Line 11:** Claims $1/2 \ge \frac{n+1}{2n+1}$. For $n=1$, $1/2 \ge 2/3$ is false.
- **Line 12-16:** Claims $S_{odd}$ is minimized when pieces are equal. Counterexample for $n=1$: Equal pieces $\{1/3, 1/3, 1/3\}$ give $S_{odd} = 2/3$. Unequal pieces $\{0.5, 0.49, 0.01\}$ give $S_{odd} = 0.51$. Since $0.51 < 2/3$, the minimization claim is false.

## Proof B
Established theorem: Correctly identifies the optimal strategy for Liu: marking $n$ points to create $n$ pieces of length $\frac{2}{2n+1}$ and one piece of length $\frac{1}{2n+1}$. This construction guarantees Liu a total length of at least $\frac{n+1}{2n+1}$.
Claim gap: The justification for the upper bound on Xiang's share ($V_X$) is invalid. Line 10 claims $V_X$ (sum of even-indexed sorted pieces) is the *minimum* possible sum of minimums over all pairings. This is false; $V_X$ is actually the *maximum* possible sum of minimums. Consequently, the pairing construction in Lines 11-20 yields a lower bound for $V_X$, failing to establish the required upper bound. Line 22 relies on an unverified heuristic to close the argument.
Qualifications and supplied repairs: The strategy itself is correct and robust (verified independently for $n=1,2$), but the proof of its optimality contains a logical reversal in the pairing lemma. No substantive repairs were supplied; the strategy's validity stands independently of the flawed bounding argument.
Decisive checks: 
- **Line 10:** Claims $V_X = \min \sum \min(s, s')$. For pieces $\{10, 9, 8, 1\}$, $V_X = 9+1=10$. Pairing $(10, 1), (9, 8)$ gives sum of mins $1+8=9$. Since $9 < 10$, $V_X$ is not the minimum.
- **Strategy Verification:** For $n=1$, Liu's partition $\{2/3, 1/3\}$ forces the median of the final pieces to be exactly $1/3$ regardless of Xiang's cut, guaranteeing Liu $1 - 1/3 = 2/3$. This confirms the strategy is mathematically sound despite the proof error.

## Decision
Winner: B
Reason: Proof B identifies the correct winning strategy (unequal partition), whereas Proof A proposes a strategy (equal partition) that is demonstrably insufficient for $n=1$. While Proof B contains a significant logical error in its pairing argument (reversing the inequality direction for the sum of minimums), this is a technical flaw in the justification of a correct result. Proof A suffers from both a false arithmetic inequality ($1/2 \ge 2/3$) and a fundamentally incorrect strategy. Proof B is mathematically stronger because its core construction solves the problem, whereas Proof A's construction fails.