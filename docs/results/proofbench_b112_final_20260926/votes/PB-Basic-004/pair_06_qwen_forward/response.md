# Proof comparison

## Proof A
Established theorem: The unique strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Recurrence and General Solution (Lines 3-9):** Correctly derives the linear recurrence $x_{n+2} - x_{n+1} - 20x_n = 0$ and the general solution $x_n = A(x_0) 5^n + B(x_0) (-4)^n$ for all $n \in \mathbb{Z}$.
- **Monotonicity Constraint (Lines 20-27):** Correctly asserts that $x < y \implies x_n < y_n$ for all $n \in \mathbb{Z}$ (a valid property of strictly increasing bijections). The argument that $\Delta B$ must be zero to prevent the oscillating term $\Delta B (-5/4)^m$ from violating the inequality $\Delta A + \Delta B (-5/4)^m > 0$ as $m \to \infty$ is logically sound and correctly handles sign cases.
- **Forcing Constant to Zero (Lines 29-36):** Correctly substitutes the linear form $g(x) = 5x - 9C$ into the functional equation to algebraically determine $C=0$. All steps are verified.

## Proof B
Established theorem: The unique strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Continuity and Bijectivity (Lines 3-4):** Correctly proves that a strictly increasing surjective function on $\mathbb{R}$ must be continuous, establishing $g$ as a homeomorphism without relying on unproven terminology.
- **Sequence Monotonicity (Lines 18-21):** Rigorously derives that the orbit $(x_n)$ must be strictly monotonic for all $n \in \mathbb{Z}$ using forward induction and backward contradiction, rather than asserting order preservation.
- **Oscillation Argument (Lines 23-29):** Correctly analyzes the difference $\Delta_n = x_{n+1} - x_n$. The limit analysis as $n \to -\infty$ correctly identifies that the term $-5B(x_0)(-1/4)^m$ dominates and oscillates in sign unless $B(x_0) = 0$, which directly forces $B(x_0) = 0$ to maintain the constant sign required by monotonicity. All algebraic manipulations and limit justifications are verified.

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct. Proof B is preferred for its superior rigor in justifying the properties of the sequence $(x_n)$. Specifically, Proof B explicitly derives the monotonicity of the orbit for all $n \in \mathbb{Z}$ (Lines 18-21) and proves the continuity of $g$ (Lines 3-4), whereas Proof A asserts the preservation of order under iteration (Line 20) without derivation. Additionally, Proof B's direct elimination of the coefficient $B(x_0)$ via the difference term $\Delta_n$ is a more self-contained and elegant argument than Proof A's two-step process of proving $B(x)$ is constant and then solving for that constant.