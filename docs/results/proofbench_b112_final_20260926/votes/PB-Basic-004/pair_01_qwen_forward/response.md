# Proof comparison

## Proof A
Established theorem: The only strictly increasing surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Fixed Points & Sign Analysis (Lines 3-9):** Correctly deduces $g(0)=0$ and explicitly proves $g(x)>x$ for $x>0$ and $g(x)<x$ for $x<0$ via contradiction with the functional equation. This establishes strict sign invariance for orbits.
- **Bi-infinite Orbit & Limit (Lines 17-27):** Correctly extends the recurrence to $n \in \mathbb{Z}$ using surjectivity. The factorization $x_{-m} = B(x_0)(-1/4)^m[1 + \frac{A}{B}(-4/5)^m]$ is algebraically verified. The limit argument correctly shows that if $B(x_0) \neq 0$, the sign of $x_{-m}$ must alternate for large $m$, contradicting the established positivity of the orbit. This rigorously forces $B(x)=0$.
- **Verification (Lines 31-33):** Confirms $g(x)=5x$ satisfies all hypotheses.

## Proof B
Established theorem: The only strictly increasing surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Inverse Recurrence Derivation (Lines 14-19):** Correctly substitutes $z=y_{n+2}$ into the functional equation to derive $20y_{n+2}+y_{n+1}-y_n=0$. The characteristic roots $1/5, -1/4$ and general solution are algebraically verified.
- **Monotonicity & Difference Limit (Lines 20-26):** Asserts that $(y_n)$ is strictly monotonic for $x \neq 0$. This relies on the standard (but unstated) lemma that iterates of a strictly increasing function are monotonic. The difference expression $y_{n+1}-y_n = (-1/4)^n[-\frac{4}{5}C(-4/5)^n - \frac{5}{4}D]$ is correctly derived. The limit argument correctly shows that if $D(x) \neq 0$, the difference alternates sign for large $n$, contradicting monotonicity. This rigorously forces $D(x)=0$.
- **Verification (Lines 32-33):** Confirms $g(x)=5x$ satisfies all hypotheses.

## Decision
Winner: A
Reason: Both proofs are mathematically correct and use equivalent asymptotic arguments on the inverse orbit to eliminate the oscillating term. Proof A is preferred because it explicitly derives the sign inequality $g(x) > x$ for $x > 0$ (Lines 7-8), which provides a fully self-contained justification for why the orbit must remain strictly positive. Proof B relies on the general property that iterates of an increasing function are monotonic (Line 20) without stating or proving this lemma, making Proof A's handling of domain constraints and sign invariance slightly more rigorous and transparent.