# Proof comparison

## Proof A
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: The claim in line 20 that the sequence $y_n = g^{-n}(x)$ must be strictly monotonic for $x \neq 0$ is a routine consequence of $g^{-1}$ being strictly increasing and the fact that $g^{-1}(x) = x$ only if $x=0$ (which is derived from the functional equation).
Decisive checks: 
- The derivation of $g(0)=0$ (line 3) is verified.
- The linear recurrence for $a_n$ (line 6) and its general solution (line 8) are verified.
- The inverse recurrence $20y_{n+2} + y_{n+1} - y_n = 0$ (line 15) is verified: substituting $z = y_{n+2}$ into $g(g(z)) = g(z) + 20z$ yields $y_n = y_{n+1} + 20y_{n+2}$.
- The general solution $y_n = C(x)(1/5)^n + D(x)(-1/4)^n$ (line 19) is verified.
- The limit argument for $y_{n+1} - y_n$ (lines 21-25) is verified: $y_{n+1} - y_n = (-1/4)^n [-4/5 C(x) (-4/5)^n - 5/4 D(x)]$. If $D(x) \neq 0$, the term in the brackets approaches $-5/4 D(x)$, causing the difference to alternate sign for large $n$, contradicting monotonicity.

## Proof B
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: The claim in line 20 that $x_n > 0$ for all $n \in \mathbb{Z}$ given $x_0 > 0$ is a routine consequence of $g(0)=0$ and $g$ being strictly increasing.
Decisive checks:
- The derivation of $g(0)=0$ (line 5) and the property $g(x) > x$ for $x > 0$ (line 8) are verified.
- The linear recurrence $x_{n+2} = x_{n+1} + 20x_n$ (line 18) and its general solution (line 19) are verified.
- The bi-infinite orbit analysis (lines 21-26) is verified: $x_{-m} = B(x_0) (-1/4)^m [1 + \frac{A(x_0)}{B(x_0)} (-4/5)^m]$. As $m \to \infty$, the bracket approaches 1, meaning $x_{-m}$ alternates sign if $B(x_0) \neq 0$, contradicting $x_{-m} > 0$.
- The conclusion $B(x)=0 \implies g(x)=5x$ (line 30) is verified.

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct, employing the same core strategy of using linear recurrences and asymptotic behavior to eliminate the negative root. Proof B is slightly more polished in its organization and provides a more intuitive path by establishing $g(x) > x$ for $x > 0$ and using the sign of the sequence $x_n$ rather than the monotonicity of $y_n$.