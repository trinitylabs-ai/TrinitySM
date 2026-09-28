# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Recurrence & Domain (Lines 4-8):** Correctly establishes that surjectivity and strict monotonicity imply $g$ is a bijection with a strictly increasing inverse, justifying the bi-infinite sequence $x_n \in \mathbb{R}$ for all $n \in \mathbb{Z}$. The linear recurrence $x_{n+2} - x_{n+1} - 20x_n = 0$ and its general solution $x_n = A(x)5^n + B(x)(-4)^n$ are correctly derived.
- **Monotonicity Constraint (Lines 20-27):** Correctly translates $x < y \implies x_n < y_n$ into $\Delta A + \Delta B (-4/5)^n > 0$ for all $n \in \mathbb{Z}$. The limit analysis as $n \to -\infty$ correctly identifies that if $\Delta B \neq 0$, the term $\Delta B (-5/4)^m$ grows unbounded in magnitude and oscillates in sign, inevitably violating the strict inequality for sufficiently large $m$. This rigorously forces $\Delta B = 0$ for all $x < y$, proving $B(x)$ is a global constant $C$.
- **Algebraic Resolution (Lines 30-36):** Correctly substitutes the affine form $g(x) = 5x - 9C$ into the original functional equation. The arithmetic $25x - 54C = 25x - 9C \implies 45C = 0$ is verified, forcing $C=0$.
- **Verification (Lines 41-42):** Correctly confirms $g(x)=5x$ satisfies all hypotheses.

## Proof B
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Fixed Point & Sign Analysis (Lines 3-9):** Correctly deduces $g(0)=0$ from the functional equation and monotonicity. The inequalities $g(x) > x$ for $x > 0$ and $g(x) < x$ for $x < 0$ are correctly proven by contradiction using the given equation.
- **Recurrence & Coefficients (Lines 11-15):** Correctly sets up the bi-infinite recurrence and solves for $A(x), B(x)$ identically to Proof A.
- **Orbit Sign Preservation (Lines 17-27):** Correctly argues that $x_0 > 0 \implies x_n > 0$ for all $n \in \mathbb{Z}$ using the established fixed point and monotonicity of $g^{-1}$. The asymptotic analysis of $x_{-m}$ correctly factors out the dominant term $B(-1/4)^m$ (since $|-1/4| > |1/5|$). The conclusion that $B(x_0) \neq 0$ would cause sign alternation in $x_{-m}$, contradicting the positivity of the orbit, is mathematically sound. Symmetric handling for $x_0 < 0$ and $x_0 = 0$ covers the domain.
- **Conclusion (Lines 29-34):** Correctly deduces $B(x)=0$ and verifies the solution.

## Decision
Winner: A
Reason: Both submissions are mathematically complete and correct, with no load-bearing defects. Proof A is preferred for its structural robustness and methodological elegance. Proof A employs the difference method (comparing two distinct orbits $x_n$ and $y_n$) to directly leverage the strict monotonicity hypothesis, cleanly separating the structural constraint (which forces $B(x)$ to be constant) from the algebraic constraint (which forces the constant to be zero). This approach is more general and does not require intermediate fixed-point analysis or sign-preservation arguments. Proof B is also rigorous but relies on establishing $g(0)=0$ and orbit sign properties first, making its argument slightly more specific to the particular roots and fixed point of this equation. Proof A's direct use of order preservation across the entire domain provides a marginally stronger and more transparent justification for the affine structure of $g$.