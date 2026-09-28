# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The recurrence $x_{n+2} - x_{n+1} - 20x_n = 0$ for $n \in \mathbb{Z}$ is correctly derived from $g(g(x)) = g(x) + 20x$ and the fact that $g$ is a homeomorphism (lines 4-6).
- The general solution $x_n = A(x_0) 5^n + B(x_0) (-4)^n$ is correct for the characteristic equation $r^2 - r - 20 = 0$ (lines 7-8).
- The monotonicity argument $\Delta A + \Delta B (-4/5)^n > 0$ for all $n \in \mathbb{Z}$ correctly forces $\Delta B = 0$ because as $n \to -\infty$, the term $\Delta B (-5/4)^m$ oscillates and grows in magnitude, eventually making the expression negative if $\Delta B \neq 0$ (lines 20-27).
- The conclusion $B(x) = C$ leads to $g(x) = 5x - 9C$, and substituting this into the original equation correctly forces $C = 0$ (lines 29-37).

## Proof B
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The initial value $g(0) = 0$ is correctly derived from $g(g(0)) = g(0)$ and injectivity (line 3).
- The recurrence for $y_n = g^{-n}(x)$, $20y_{n+2} + y_{n+1} - y_n = 0$, is correctly derived (lines 14-15).
- The characteristic roots $1/5$ and $-1/4$ are correct (lines 16-18).
- The monotonicity argument for $y_n$ correctly forces $D(x) = 0$ because $y_{n+1} - y_n = (-1/4)^n [-4/5 C(x) (-4/5)^n - 5/4 D(x)]$ would alternate sign for large $n$ if $D(x) \neq 0$ (lines 20-25).
- The final result $g^{-1}(x) = x/5 \implies g(x) = 5x$ is correct (lines 27-30).

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct. Proof A is slightly more direct as it handles the sequence for all $n \in \mathbb{Z}$ in one go and explicitly verifies the constant term $C$ by substituting the resulting linear form back into the original functional equation. Proof B is also excellent, but Proof A's approach to the monotonicity constraint is slightly more elegant.