# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- The derivation of the recurrence for $y_n = g^{-n}(x)$ is verified: $g(g(y_{n+2})) = g(y_{n+2}) + 20y_{n+2} \implies y_n = y_{n+1} + 20y_{n+2}$, which leads to the characteristic equation $20r^2 + r - 1 = 0$ with roots $1/5$ and $-1/4$ (lines 14-18).
- The monotonicity argument is verified: $y_{n+1} - y_n = (-1/4)^n [ -4/5 C(x) (-4/5)^n - 5/4 D(x) ]$. As $n \to \infty$, the bracket approaches $-5/4 D(x)$. If $D(x) \neq 0$, the sign of $y_{n+1} - y_n$ alternates for large $n$, contradicting the monotonicity of $g^{-1}$ (lines 20-25).
- The final result $g(x) = 5x$ is correctly derived from $D(x) = 0$ and $y_1 = g^{-1}(x) = x/5$ (lines 27-30).

## Proof B
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The derivation of the recurrence for $x_n = g^n(x)$ is verified: $x_{n+2} = x_{n+1} + 20x_n$, with characteristic roots $5$ and $-4$ (lines 7-11).
- The monotonicity argument for $n \to -\infty$ is verified: $\Delta_{-m} = \frac{1}{4^m} [ 4 A(x_0) (4/5)^m - 5 B(x_0) (-1)^{-m} ]$. As $m \to \infty$, the term $4 A(x_0) (4/5)^m$ vanishes, and the sign of $\Delta_{-m}$ is determined by $-5 B(x_0) (-1)^{-m}$, which alternates unless $B(x_0) = 0$ (lines 23-28).
- The final result $g(x) = 5x$ is correctly derived from $B(x_0) = 0$ and $x_1 = g(x_0) = 5 A(x_0) = 5x_0$ (lines 30-33).

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct. Proof B is slightly stronger as it provides a more comprehensive justification for the properties of $g$, including a proof of its continuity and a more detailed explanation of why the sequence $(x_n)$ must be monotonic for all $n \in \mathbb{Z}$.