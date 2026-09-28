# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE. The proof is complete and mathematically rigorous.
Qualifications and supplied repairs: NONE. All steps are justified within the submission.
Decisive checks:
- **Fixed Point & Sign Invariance (Lines 3-9):** Correctly derives $g(0)=0$ from the fixed-point equation $x=x+20x$. Uses strict monotonicity to prove $x>0 \implies g(x)>0$ and $x<0 \implies g(x)<0$. This establishes that the orbit $\{g^{(n)}(x_0)\}_{n\in\mathbb{Z}}$ remains strictly within $(0,\infty)$ for $x_0>0$ and $(-\infty,0)$ for $x_0<0$. The inverse function's monotonicity is correctly invoked to extend this to negative iterates.
- **Asymptotic Dominance & Sign Contradiction (Lines 18-27):** The recurrence solution $x_n = A(x_0)5^n + B(x_0)(-4)^n$ is correct. For $n \to -\infty$, let $n=-m$. The terms scale as $(1/5)^m$ and $(-1/4)^m$. Since $1/4 > 1/5$, the $(-4)^n$ term decays slower and dominates the asymptotic behavior. The proof correctly factors out $(-1/4)^m$ and observes that if $B(x_0) \neq 0$, the bracketed term approaches $B(x_0)$, making the sign of $x_{-m}$ alternate due to $(-1)^m$. This directly contradicts the established sign invariance of the orbit. Thus $B(x_0)=0$ is rigorously forced for all $x_0 \neq 0$, and $B(0)=0$ follows from $g(0)=0$.
- **Conclusion:** $B(x)\equiv 0 \implies g(x)=5x$. Verification is correct.

## Proof B
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE. The proof is complete and mathematically rigorous.
Qualifications and supplied repairs: NONE. All steps are justified within the submission.
Decisive checks:
- **Monotonicity of Iterates (Lines 4, 20):** Correctly states that $g$ being a strictly increasing bijection implies $g^{-1}$ is strictly increasing, so $x < y \implies x_n < y_n$ for all $n \in \mathbb{Z}$. This is a standard and correct property.
- **Difference Argument & Oscillation (Lines 21-27):** Correctly forms the difference inequality $\Delta A + \Delta B (-4/5)^n > 0$. For $n \to -\infty$, the term $(-4/5)^n = (-5/4)^{|n|}$ grows exponentially in magnitude and alternates sign. The proof correctly argues that if $\Delta B \neq 0$, the oscillating term will eventually dominate $\Delta A$ and violate the strict positivity of the difference. This forces $\Delta B = 0$ for all pairs $x<y$, proving $B(x)$ is a constant function $C$.
- **Algebraic Resolution (Lines 30-36):** Substitutes $g(x) = 5x - 9C$ back into the original functional equation. The algebra $25x - 54C = 25x - 9C \implies C=0$ is correct and necessary to eliminate the constant. Verification follows.

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct, relying on the same core insight: the $(-4)^n$ term dominates as $n \to -\infty$, and its oscillating sign must be eliminated. Proof A is preferred because its sign-preservation argument directly ties the coefficient $B(x)$ to the invariant sign of the orbit, yielding $B(x)=0$ immediately without requiring a secondary algebraic verification step. Proof B correctly forces $B(x)$ to be constant but must substitute the form back into the functional equation to determine that the constant is zero. Proof A's derivation is slightly more direct and self-contained, making its logical chain marginally tighter.