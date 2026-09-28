# Proof comparison

## Proof A
Established theorem: The unique strictly increasing surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Fixed Points & Sign (Lines 3-9):** Correctly establishes $g(0)=0$ and proves $g(x)>x$ for $x>0$ and $g(x)<x$ for $x<0$ using the functional equation and strict monotonicity. This correctly restricts the domain behavior needed for orbit analysis.
- **Recurrence & Coefficients (Lines 11-15):** Correctly derives the bi-infinite linear recurrence $x_{n+2}=x_{n+1}+20x_n$ with characteristic roots $5,-4$. The expressions for $A(x)$ and $B(x)$ are algebraically verified.
- **Asymptotic Dominance & Sign Constraint (Lines 17-27):** Correctly identifies that for $x_0>0$, the orbit must remain strictly positive for all $n\in\mathbb{Z}$ (forward by $g(x)>x$, backward by $g^{-1}(x)>0$). The limit analysis as $n\to-\infty$ correctly factors out the dominant term $B(-1/4)^m$ (since $|-1/4|>|1/5|$). The deduction that $B\neq0$ forces sign oscillation in $x_{-m}$, contradicting the positivity constraint, is mathematically rigorous. The symmetric case for $x_0<0$ is valid and correctly handled.

## Proof B
Established theorem: The unique strictly increasing surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Continuity & Bijection (Lines 3-4):** Correctly proves continuity from strict monotonicity and surjectivity, establishing the existence of $g^{-1}$ for bi-infinite orbits. Continuity is not strictly required for the algebraic argument but is correctly stated.
- **Recurrence & Coefficients (Lines 6-15):** Identical correct derivation to Proof A.
- **Monotonicity Justification (Lines 17-21):** The initial bold claim that strict monotonicity of $g$ implies monotonicity of the orbit is technically imprecise as a standalone statement, but the immediately following case analysis (Lines 19-21) correctly justifies it by induction and inverse mapping for $g(x_0)>x_0$, $g(x_0)<x_0$, and $g(x_0)=x_0$. This repairs the loose summary and establishes that $\Delta_n$ must maintain a constant sign.
- **Asymptotic Dominance & Difference Constraint (Lines 23-28):** Correctly computes $\Delta_n = 4A 5^n - 5B(-4)^n$. The factorization for $n=-m$ is algebraically verified. The argument that the $B$-term dominates as $m\to\infty$ and forces sign oscillation in $\Delta_{-m}$ (contradicting the constant-sign requirement) is rigorous and correctly forces $B=0$.

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct, relying on the same core mechanism: the dominance of the $(-4)^n$ term as $n\to-\infty$ forces the coefficient $B$ to vanish to prevent sign oscillation. Proof A is preferred for its tighter logical flow and more direct constraint choice. Proof A explicitly derives $g(x)>x$ for $x>0$ in Step 1, which cleanly justifies the positivity constraint on the orbit terms $x_n$ without requiring a separate case analysis. Proof B's initial claim about orbit monotonicity is slightly loose (though immediately corrected by cases), and analyzing the differences $\Delta_n$ adds a layer of algebraic complexity that is unnecessary when the sign of $x_n$ itself suffices. Proof A's premises are precise throughout, making it the stronger submission.