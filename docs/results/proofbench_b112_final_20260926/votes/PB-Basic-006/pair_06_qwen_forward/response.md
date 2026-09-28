# Proof comparison

## Proof A
Established theorem: For any infinite sequence of integers $c_0, c_1, \ldots$ with $c_0 \neq 0$, there exists an integer $k \geq 1$ such that $P_k(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots. (The case $k=0$ is excluded by the condition $0 < 0$, so the proof correctly targets $k \geq 1$.)
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE. All algebraic manipulations, inequality applications, and asymptotic comparisons are self-contained and verified.
Decisive checks: 
- Lines 5-8: The transformation $R_k(y) = c_0^{k-1} Q_k(y/c_0)$ yields $y^k + c_1 y^{k-1} + c_0 c_2 y^{k-2} + \cdots + c_0^{k-1} c_k$. Direct expansion confirms $R_k(y)$ is monic with integer coefficients. Verified.
- Line 9: The discriminant $\Delta_k = \prod_{i<j}(y_{i,k}-y_{j,k})^2$ is an integer because $R_k$ is monic with integer coefficients. Distinct real roots imply $\Delta_k > 0$, hence $\Delta_k \geq 1$. Verified.
- Lines 11-13: AM-GM applied to non-negative terms $(y_{i,k}-y_{j,k})^2$ gives $\sum_{i<j}(y_{i,k}-y_{j,k})^2 \geq \binom{k}{2} \Delta_k^{1/\binom{k}{2}} \geq \binom{k}{2}$. Verified.
- Lines 14-15: The identity $\sum_{i<j}(y_i-y_j)^2 = k\sum y_i^2 - (\sum y_i)^2$ and Vieta's relations $\sum y_i = -c_1$, $\sum y_i^2 = c_1^2 - 2c_0 c_2$ are standard and correctly substituted. Verified.
- Lines 16-20: Substitution yields $k(c_1^2 - 2c_0 c_2) - c_1^2 \geq k(k-1)/2$. With $c_0, c_1, c_2$ fixed, the LHS is linear in $k$ while the RHS is quadratic. The inequality necessarily fails for sufficiently large $k$, contradicting the universal assumption. Verified.
- Quantifier/Domain check: The contradiction invalidates $\forall k \geq 1$, establishing $\exists k \geq 1$. This satisfies the problem's $\exists k \geq 0$ requirement. No domain or quantifier errors detected.

## Proof B
Established theorem: Same as Proof A.
Claim gap: Relies on an external theorem (Pólya's theorem on partial sums with real roots) without proof or verification of its hypotheses within the submission. While the theorem is mathematically true, its citation leaves a load-bearing step unjustified in the context of a self-contained Olympiad solution.
Qualifications and supplied repairs: Verified that Pólya's theorem (1929) correctly states that if all partial sums of a power series with real coefficients have only real zeros, the radius of convergence is infinite. The logical deduction from this to $\limsup |c_n|^{1/n} = 0$ and the subsequent contradiction with integer coefficients $|c_n| \geq 1$ is correct. However, the submission does not justify the theorem itself, making it dependent on external knowledge. No repairs were supplied; the gap is purely in internal justification.
Decisive checks:
- Lines 1-4: Correctly reduces the assumption to $P_k$ having exactly $k$ distinct real roots and $c_k \neq 0$. Verified.
- Lines 5-10: Cites Pólya's theorem and applies Cauchy-Hadamard. The implication chain is logically sound given the theorem. Verified as a correct application of a known result.
- Lines 11-17: Contradiction via integer coefficient lower bound $|c_n| \geq 1 \implies \limsup |c_n|^{1/n} \geq 1$. Verified.
- Quantifier/Domain check: Correctly handles $k \geq 1$ and explicitly addresses $k=0$ at the end. No quantifier errors. The gap remains the unverified citation.

## Decision
Winner: A
Reason: Both proofs correctly establish the result via contradiction. Proof A provides a complete, self-contained derivation using elementary algebra (Vieta's formulas, discriminant properties, AM-GM, and asymptotic comparison). Every load-bearing step is explicitly justified and verified within the text. Proof B correctly applies a deep result (Pólya's theorem) but cites it without proof or reference to its conditions, leaving a substantive gap in self-contained justification. In the context of an Olympiad problem where elementary, fully justified arguments are standard, Proof A's rigorous internal derivation constitutes a stronger mathematical solution. The asymptotic contradiction in A is verified to hold for all valid sequences, and no external machinery is required.