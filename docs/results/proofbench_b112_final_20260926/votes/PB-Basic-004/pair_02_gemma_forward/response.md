# Proof comparison

## Proof A
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The fixed point analysis (lines 4-5) correctly establishes $g(0) = 0$.
- The monotonicity analysis (lines 7-9) correctly establishes $g(x) > x$ for $x > 0$ and $g(x) < x$ for $x < 0$.
- The linear recurrence $a_{n+2} = a_{n+1} + 20a_n$ (line 12) is correctly derived from the functional equation.
- The general solution $a_n = A(x) 5^n + B(x) (-4)^n$ (line 13) and the expressions for $A(x)$ and $B(x)$ (line 15) are correct.
- The bi-infinite orbit analysis (lines 18-27) correctly uses the fact that $x_n$ must maintain the sign of $x_0$ for all $n \in \mathbb{Z}$. Specifically, for $x_0 > 0$, $x_{-m} = B(x_0) (-1/4)^m [1 + \frac{A(x_0)}{B(x_0)} (-4/5)^m]$. As $m \to \infty$, the term in brackets approaches 1, so the sign of $x_{-m}$ is determined by $B(x_0) (-1/4)^m$. If $B(x_0) \neq 0$, the sign alternates, contradicting $x_n > 0$. Thus $B(x) = 0$ for all $x$.
- The final solution $g(x) = 5x$ is correctly verified (lines 31-34).

## Proof B
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The linear recurrence $x_{n+2} - x_{n+1} - 20x_n = 0$ (line 6) and its general solution (line 8) are correct.
- The expressions for $A(x)$ and $B(x)$ (line 16) are correct.
- The monotonicity argument (lines 20-27) correctly uses $x < y \implies x_n < y_n$ for all $n \in \mathbb{Z}$.
- The derivation $\Delta A + \Delta B (-4/5)^n > 0$ (line 24) is correct.
- The limit $n \to -\infty$ (line 26) correctly shows that if $\Delta B \neq 0$, the term $\Delta B (-5/4)^m$ will eventually dominate and make the expression negative, forcing $\Delta B = 0$.
- The conclusion $B(x) = C$ (line 27) and the subsequent substitution into the functional equation to force $C = 0$ (lines 30-36) are correct.
- The final solution $g(x) = 5x$ is correctly verified (line 42).

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct. Proof A is slightly more comprehensive, providing a detailed initial analysis of the fixed point $g(0)=0$ and the relationship between $g(x)$ and $x$ for $x \neq 0$, which provides a very clear justification for the sign of the orbit $x_n$ used in its final argument. Proof B is also excellent and uses a slightly different but equally valid monotonicity argument. Proof A's structure is marginally more detailed.