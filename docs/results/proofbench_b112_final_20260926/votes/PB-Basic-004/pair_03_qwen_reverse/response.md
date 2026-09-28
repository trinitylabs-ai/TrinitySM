# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Continuity & Bijectivity:** Correctly establishes that strict monotonicity + surjectivity implies continuity and bijectivity, justifying the existence of $g^{-1}$ and the bi-infinite orbit $x_n \in \mathbb{Z}$ (Lines 3-4).
- **Recurrence & General Solution:** Correctly derives $x_{n+2} = x_{n+1} + 20x_n$ and solves it as $x_n = A 5^n + B (-4)^n$ (Lines 7-12).
- **Monotonicity Constraint:** Correctly proves that $g(x_0) > x_0$ implies $x_{n+1} > x_n$ for all $n \in \mathbb{Z}$ via forward/backward induction using the strict monotonicity of $g$ and $g^{-1}$ (Lines 18-21). Covers $<$ and $=$ cases symmetrically.
- **Asymptotic Contradiction:** Correctly analyzes $\Delta_{-m} = x_{-m+1} - x_{-m}$ as $m \to \infty$. Identifies that the $(-4)^{-m}$ term dominates the $5^{-m}$ term ($0.25^m \gg 0.2^m$), causing $\Delta_{-m}$ to oscillate in sign unless $B=0$. This contradicts the constant sign required by monotonicity, forcing $B(x_0)=0$ (Lines 23-29).
- **Conclusion:** $B=0 \implies x_n = A 5^n \implies g(x_0) = 5x_0$. Verification confirms all conditions (Lines 31-38).

## Proof B
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Fixed Points & Sign Constraints:** Correctly derives $g(0)=0$ and proves $g(x) > x$ for $x > 0$ and $g(x) < x$ for $x < 0$ using the functional equation and monotonicity (Lines 3-9).
- **Recurrence & Explicit Coefficients:** Correctly derives the recurrence and explicitly solves for $A(x) = \frac{g(x)+4x}{9}$ and $B(x) = \frac{5x-g(x)}{9}$, clarifying the functional dependency (Lines 11-15).
- **Positivity Constraint:** Correctly argues that for $x_0 > 0$, the orbit $x_n$ remains strictly positive for all $n \in \mathbb{Z}$ because $g(0)=0$ and $g$ is strictly increasing, so $g$ and $g^{-1}$ map $(0,\infty)$ to itself (Lines 17-20).
- **Asymptotic Contradiction:** Correctly analyzes $x_{-m}$ as $m \to \infty$. Factors out the dominant $(-1/4)^m$ term, showing $x_{-m} \approx B(-1/4)^m$. If $B \neq 0$, the sign alternates, contradicting $x_{-m} > 0$. Forces $B(x_0)=0$ (Lines 21-27). Handles $x_0 < 0$ and $x_0 = 0$ explicitly.
- **Conclusion:** $B(x)=0 \forall x \implies g(x)=5x$. Verification confirms all conditions (Lines 29-34).

## Decision
Winner: B
Reason: Both proofs are mathematically complete, rigorous, and free of defects. Proof B is preferred for its superior structural clarity: it explicitly derives $g(0)=0$ and the sign properties $g(x) > x$ for $x > 0$, which grounds the contradiction in a concrete positivity constraint rather than the more abstract monotonicity of differences used in Proof A. Additionally, Proof B's explicit algebraic solution for the coefficients $A(x)$ and $B(x)$ in terms of $g(x)$ and $x$ (Line 15) makes the final deduction $g(x)=5x$ more transparent, and it explicitly handles the $x_0=0$ boundary case rather than subsuming it implicitly in a limit argument.