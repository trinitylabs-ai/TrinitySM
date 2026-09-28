# Proof comparison

## Proof A
Established theorem: Under the contradiction hypothesis that every $P_k(x)$ has exactly $k$ distinct real roots, Newton's inequalities correctly yield $c_i^2 > c_{i-1}c_{i+1}\frac{i+1}{i}$ for all $i \ge 1$. Conditional on the coefficients eventually satisfying $c_{i-1}c_{i+1} > 0$, the derived recurrence forces $|c_k| \to 0$, contradicting the integrality and non-vanishing of the sequence.
Claim gap: The argument critically depends on Step 11–13, which asserts that real-rootedness of all partial sums implies the coefficient sequence is a Pólya Frequency (PF) sequence up to sign transformation, thereby guaranteeing eventual sign consistency ($c_{n-1}c_{n+1} > 0$). This is a deep result from the theory of entire functions and total positivity. The submission cites it without proof, reference, or verification of its applicability to arbitrary integer sequences. Without this sign guarantee, the inequality $c_i^2 > c_{i-1}c_{i+1}\frac{i+1}{i}$ provides no decay bound when $c_{i-1}c_{i+1} \le 0$, leaving the contradiction unestablished.
Qualifications and supplied repairs: NONE. The PF sequence citation is treated as an unverified black box. No repair is supplied; the gap is substantive and load-bearing.
Decisive checks: 
- Lines 3–9: Newton's inequality application and strictness for distinct roots are VERIFIED. The limit $k \to \infty$ correctly yields $c_i^2 \ge c_{i-1}c_{i+1}\frac{i+1}{i}$.
- Lines 11–13: DEMONSTRATED defect. The claim that partial-sum real-rootedness forces eventual sign consistency is asserted without justification. In Olympiad contexts, this constitutes an unresolved gap. If $c_{i-1}c_{i+1} \le 0$ infinitely often, the decay argument in Lines 15–23 collapses.
- Lines 15–23: Algebraic manipulation of $d_n$ and $b_n$ is VERIFIED conditional on the sign assumption. The factorial decay conclusion is correct given the premise.

## Proof B
Established theorem: For any integer sequence with $c_0 \neq 0$, the assumption that $P_k(x)$ has $k$ distinct real roots for all $k \ge 1$ leads to a contradiction. The proof constructs a monic integer polynomial $R_k(y)$ whose roots are scaled reciprocals of $P_k$'s roots. Using the integrality of the discriminant, AM-GM, and Vieta's formulas, it derives $k(c_1^2 - 2c_0 c_2) - c_1^2 \ge \frac{k(k-1)}{2}$. Since the left side is linear in $k$ and the right side quadratic, the inequality fails for sufficiently large $k$, proving the existence of some $k$ with fewer than $k$ distinct real roots.
Claim gap: NONE. All steps are elementary, self-contained, and rigorously verified.
Qualifications and supplied repairs: NONE. The argument stands as written.
Decisive checks:
- Lines 5–8: Construction of $R_k(y)$ is VERIFIED. Substitution $y = c_0 x$ and scaling by $c_0^{k-1}$ correctly yields a monic polynomial with integer coefficients. Roots $y_{i,k} = c_0/r_{i,k}$ are distinct and real since $c_0 \neq 0$ and $r_{i,k}$ are distinct non-zero reals.
- Lines 9–13: Discriminant $\Delta_k$ of a monic integer polynomial is an integer. Distinct real roots imply $\Delta_k > 0$, hence $\Delta_k \ge 1$. AM-GM on the $\binom{k}{2}$ non-negative terms $(y_i - y_j)^2$ correctly yields $\sum_{i<j} (y_i - y_j)^2 \ge \binom{k}{2}$. VERIFIED.
- Lines 14–19: Identity $\sum_{i<j}(y_i-y_j)^2 = k\sum y_i^2 - (\sum y_i)^2$ is standard and VERIFIED. Vieta's formulas on $R_k(y)$ give $\sum y_i = -c_1$ and $\sum_{i<j} y_i y_j = c_0 c_2$, so $\sum y_i^2 = c_1^2 - 2c_0 c_2$. Substitution yields the linear-vs-quadratic inequality. VERIFIED.
- Lines 20–22: Asymptotic comparison is correct. For fixed integers $c_0, c_1, c_2$, the quadratic RHS dominates the linear LHS for large $k$, producing a contradiction. VERIFIED.

## Decision
Winner: B
Reason: Proof B provides a complete, self-contained, and elementary contradiction using discriminant integrality, AM-GM, and Vieta's formulas. Every algebraic step and inequality direction is verified, and the linear-vs-quadratic asymptotic mismatch rigorously forces the contradiction. Proof A correctly applies Newton's inequalities but relies on an unjustified, advanced citation (PF sequences/Laguerre-Pólya theory) to establish eventual sign consistency of the coefficients. Without this unverified claim, the decay argument fails, leaving a load-bearing gap. Proof B's approach is mathematically airtight and requires no external theory, making it decisively stronger.