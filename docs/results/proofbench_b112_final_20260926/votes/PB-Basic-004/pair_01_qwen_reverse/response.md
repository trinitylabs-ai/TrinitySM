# Proof comparison

## Proof A
Established theorem: The unique strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE. The derivation and asymptotic analysis are mathematically complete.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Inverse Recurrence:** The derivation $20y_{n+2} + y_{n+1} - y_n = 0$ (Lines 14-15) is verified correct by substituting $y_n = g^{-n}(x)$ into the original equation and using $g(g(y_{n+2})) = y_n$.
- **Monotonicity:** The claim that $(y_n)$ is strictly monotonic because $g^{-1}$ is strictly increasing is verified. For any sequence $z_{n+1}=f(z_n)$ with $f$ strictly increasing, the sequence is necessarily monotonic.
- **Difference Analysis:** The algebraic factorization of $y_{n+1}-y_n$ (Lines 21-24) is correct. The limit argument correctly shows that if $D(x) \neq 0$, the difference alternates sign for large $n$, contradicting monotonicity. This forces $D(x)=0$ and yields $g(x)=5x$.

## Proof B
Established theorem: The unique strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE. The derivation and asymptotic analysis are mathematically complete.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Bi-infinite Orbit:** Extending the forward recurrence $x_{n+2} = x_{n+1} + 20x_n$ to all $n \in \mathbb{Z}$ is verified correct, as the functional equation holds for any $x_n$ in the domain, and surjectivity guarantees the orbit is defined for all integer indices.
- **Positivity Invariant:** The claim $x_n > 0$ for all $n$ when $x_0 > 0$ is verified. Since $g(0)=0$ and $g$ is strictly increasing, $g$ maps $(0,\infty)$ to $(0,\infty)$, and surjectivity ensures $g^{-1}$ does the same. Thus the entire orbit remains positive.
- **Asymptotic Dominance:** The analysis of $x_{-m}$ (Lines 21-26) correctly identifies $|-1/4| > |1/5|$, making $B(x_0)(-1/4)^m$ the dominant term. If $B(x_0) \neq 0$, $x_{-m}$ alternates sign for large $m$, directly contradicting the positivity invariant. This forces $B(x)=0$ and yields $g(x)=5x$.

## Decision
Winner: B
Reason: Both proofs are mathematically correct and complete. Proof B is preferred for its greater efficiency and structural clarity. By extending the forward recurrence to negative indices $n \in \mathbb{Z}$, Proof B avoids the need to derive a separate recurrence relation for the inverse function (as done in Proof A). Furthermore, Proof B's argument relies on the sign of the terms $x_{-m}$ themselves, which provides a more direct contradiction to the established positivity invariant than Proof A's analysis of the differences $y_{n+1} - y_n$. Both handle quantifiers and domains correctly, but Proof B's use of the bi-infinite orbit is a more standard and elegant technique for surjective functional equations.