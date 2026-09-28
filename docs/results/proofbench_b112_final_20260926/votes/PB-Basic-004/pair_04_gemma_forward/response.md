# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The derivation of $g(0)=0$ in line 3 is correct: $g(g(0)) = g(0) + 20(0) \implies g(g(0)) = g(0)$, and since $g$ is strictly increasing, it is injective, so $g(0) = 0$.
- The recurrence $a_{n+2} = a_{n+1} + 20a_n$ and its general solution $a_n = A(x) 5^n + B(x) (-4)^n$ in lines 6-8 are correct.
- The inverse recurrence $20y_{n+2} + y_{n+1} - y_n = 0$ for $y_n = g^{-n}(x)$ and its general solution $y_n = C(x) (1/5)^n + D(x) (-1/4)^n$ in lines 15-19 are correct.
- The argument that $y_{n+1} - y_n$ alternates sign if $D(x) \neq 0$ in lines 20-25 is correct: $y_{n+1} - y_n = (-1/4)^n [ -\frac{4}{5} C(x) (-4/5)^n - \frac{5}{4} D(x) ]$. As $n \to \infty$, the term in brackets approaches $-5/4 D(x)$, meaning the sign of $y_{n+1} - y_n$ eventually alternates with $(-1/4)^n$, contradicting the monotonicity of $y_n$.
- The conclusion $D(x) = 0 \implies y_n = C(x) (1/5)^n \implies g^{-1}(x) = x/5 \implies g(x) = 5x$ in lines 27-30 is correct.

## Proof B
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The recurrence $x_{n+2} - x_{n+1} - 20x_n = 0$ and its general solution $x_n = A(x_0) 5^n + B(x_0) (-4)^n$ in lines 6-8 are correct.
- The use of monotonicity $x < y \implies x_n < y_n$ to derive $\Delta A + \Delta B (-4/5)^n > 0$ for all $n \in \mathbb{Z}$ in lines 20-24 is correct.
- The argument that $\Delta B = 0$ in lines 25-27 is correct: as $n \to -\infty$, let $n = -m$. The term $\Delta B (-5/4)^m$ oscillates in sign and grows in magnitude; if $\Delta B \neq 0$, the inequality $\Delta A + \Delta B (-5/4)^m > 0$ must be violated for some $m$.
- The derivation $B(x) = C \implies g(x) = 5x - 9C$ and the subsequent substitution into the functional equation $g(g(x)) = g(x) + 20x$ to find $C = 0$ in lines 30-36 are correct: $25x - 54C = 25x - 9C \implies 45C = 0 \implies C = 0$.

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct. Proof B is slightly more robust in its application of the "strictly increasing" property by comparing two arbitrary points $x$ and $y$ to show that $B(x)$ must be constant, whereas Proof A relies on the monotonicity of a sequence for a single $x$. While both are valid, Proof B's approach is a more direct and standard method for this class of functional equation.