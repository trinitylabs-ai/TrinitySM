# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Continuity:** Lines 3-4 correctly deduce that a strictly increasing surjective function on $\mathbb{R}$ must be continuous (jump discontinuities would violate surjectivity).
- **Recurrence & General Solution:** Lines 7-12 correctly derive the linear recurrence $x_{n+2} = x_{n+1} + 20x_n$ and its general solution $x_n = A 5^n + B (-4)^n$ for the orbit defined by $x_{n+1} = g(x_n)$.
- **Monotonicity of Orbit:** Lines 18-21 correctly establish that strict monotonicity of $g$ implies the orbit $(x_n)$ is monotonic for all $n \in \mathbb{Z}$. The backward induction step (showing $x_1 > x_0 \implies x_0 > x_{-1}$) is logically sound and correctly handles the domain $n \in \mathbb{Z}$.
- **Oscillation Argument:** Lines 23-28 correctly analyze the difference $\Delta_n = x_{n+1} - x_n$. As $n \to -\infty$, the term involving $(-4)^n$ dominates $5^n$ because $|1/4| > |1/5|$. The factor $(-1)^n$ causes $\Delta_n$ to oscillate in sign unless $B(x_0) = 0$. This forces $B(x_0) = 0$ for all $x_0$, leading directly to $g(x) = 5x$ without requiring a secondary substitution step.

## Proof B
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Recurrence & Coefficients:** Lines 4-17 correctly derive the recurrence, general solution, and explicit formulas for $A(x)$ and $B(x)$.
- **Order Preservation:** Lines 20-27 correctly argue that strict monotonicity implies $x_n < y_n$ for all $n \in \mathbb{Z}$ if $x < y$. The analysis of the difference $y_n - x_n$ shows that the oscillating term $(-4/5)^n$ (which grows in magnitude as $n \to -\infty$) must have a zero coefficient difference $\Delta B$, implying $B(x)$ is a constant function $C$.
- **Functional Equation Check:** Lines 30-36 correctly substitute $B(x) = C$ into the original functional equation to determine $C=0$, thereby completing the proof.

## Decision
Winner: A
Reason: Both proofs are mathematically correct and rigorous. Proof A is preferred because it utilizes a stronger necessary condition derived directly from the problem statement. Proof A establishes that the orbit $(x_n)$ for any single point must be monotonic. This condition directly contradicts the oscillatory nature of the general solution $A 5^n + B (-4)^n$ as $n \to -\infty$ unless $B=0$, allowing Proof A to eliminate the oscillating term immediately. Proof B relies on the weaker condition of order preservation between distinct orbits ($x_n < y_n$), which permits a common oscillating term (constant $B$) as long as it cancels out in the difference. Consequently, Proof B requires an additional step of substituting back into the functional equation to force the constant to zero, whereas Proof A's structural analysis of the orbit's monotonicity is sufficient to determine the function form directly. Additionally, Proof A explicitly justifies continuity, enhancing completeness.