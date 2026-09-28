# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Recurrence & Roots:** The inverse recurrence $20y_{n+2} + y_{n+1} - y_n = 0$ (Step 15) is correctly derived by substituting $x = y_{n+2}$ into the original equation. The characteristic roots $1/5$ and $-1/4$ (Step 18) are correct.
- **Monotonicity & Asymptotics:** The claim that $y_n$ is strictly monotonic for $x \neq 0$ (Step 20) follows directly from $g^{-1}$ being strictly increasing. The difference $y_{n+1} - y_n$ is correctly factored in Step 24 as $(-1/4)^n [ -\frac{4}{5}C(-4/5)^n - \frac{5}{4}D ]$. Since $|-1/4| > |1/5|$, the $(-1/4)^n$ term dominates as $n \to \infty$. The bracket converges to $-5/4 D(x)$, so if $D(x) \neq 0$, the product alternates sign, contradicting monotonicity. This correctly forces $D(x) = 0$.
- **Conclusion:** $D(x)=0$ yields $y_n = x(1/5)^n$, giving $g^{-1}(x) = x/5 \implies g(x)=5x$. The verification is correct. Quantifiers are properly handled (fixed $x$, varying $n$, then universal in $x$).

## Proof B
Established theorem: The only strictly increasing, surjective function $g: \mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Continuity:** The proof of continuity (Step 4) is mathematically correct but superfluous, as the subsequent recurrence and monotonicity arguments rely only on order preservation, not topological properties.
- **Recurrence & Roots:** The forward recurrence $x_{n+2} = x_{n+1} + 20x_n$ (Step 8) and roots $5, -4$ are correct. The domain $n \in \mathbb{Z}$ is properly justified by bijectivity.
- **Monotonicity & Asymptotics:** The backward induction establishing monotonicity on $\mathbb{Z}$ (Steps 18-21) is rigorous. The difference $\Delta_{-m}$ is correctly analyzed as $m \to \infty$ (Steps 26-28). The factorization $\frac{1}{4^m}[4A(4/5)^m - 5B(-1)^{-m}]$ correctly identifies $(-1/4)^m$ as the dominant oscillating term. The conclusion $B(x_0)=0$ is sound.
- **Conclusion:** $B(x_0)=0$ yields $x_n = x_0 5^n$, giving $g(x_0)=5x_0$. Verification is correct. Quantifiers are properly handled.

## Decision
Winner: A
Reason: Both proofs are mathematically complete, correct, and rely on the same core mechanism (linear recurrence on orbits + monotonicity constraint eliminating the oscillating root). Proof A is preferred for its greater efficiency and cleaner asymptotic notation. Proof A's analysis of $y_{n+1}-y_n$ as $n \to \infty$ uses the standard base $(-1/4)^n$ and a transparent factorization (Step 24), whereas Proof B's analysis of $\Delta_{-m}$ as $m \to \infty$ requires handling negative exponents and $(-1)^{-m}$, which is algebraically equivalent but slightly more cumbersome. Additionally, Proof B includes a continuity proof (Step 4) that is correct but entirely unused in the subsequent deduction, making Proof A more direct and focused on the essential algebraic constraints.