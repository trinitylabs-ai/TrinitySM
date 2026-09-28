# Proof comparison

## Proof A
Established theorem: The unique strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Recurrence & Domain (Lines 4-8):** Correctly defines the two-sided sequence $x_n$ for $n \in \mathbb{Z}$ using surjectivity and strict monotonicity to guarantee $g^{-1}$ exists and preserves order. The linear recurrence $x_{n+2} - x_{n+1} - 20x_n = 0$ and its general solution $x_n = A(x_0)5^n + B(x_0)(-4)^n$ are algebraically verified.
- **Oscillation Argument (Lines 20-27):** Correctly translates strict monotonicity into $\Delta A + \Delta B(-4/5)^n > 0$ for all $n \in \mathbb{Z}$. The limit analysis as $n \to -\infty$ (setting $n=-m$) correctly identifies that if $\Delta B \neq 0$, the term $\Delta B(-5/4)^m$ dominates $\Delta A$ and alternates sign, inevitably violating the strict inequality for sufficiently large $m$. This rigorously forces $\Delta B = 0$, proving $B(x)$ is constant.
- **Constant Resolution (Lines 30-36):** Correctly substitutes $g(x) = 5x - 9C$ into the original functional equation, yielding $25x - 54C = 25x - 9C$, which uniquely determines $C=0$. The verification step confirms all hypotheses.

## Proof B
Established theorem: The unique strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: Minor gap in justifying strict monotonicity of the inverse sequence.
Qualifications and supplied repairs: Supplied the verification that $g(x)=x \implies x=0$ (via $g(g(x))=g(x)+20x \implies x=x+20x$), which is required to rule out the constant sequence case ($y_1=y_0$) and validate the claim that $(y_n)$ is strictly monotonic for $x \neq 0$ (Line 20).
Decisive checks:
- **Inverse Recurrence (Lines 14-19):** Correctly derives $20y_{n+2} + y_{n+1} - y_n = 0$ by substituting $x=y_{n+2}$ into the rearranged functional equation. The characteristic roots $1/5$ and $-1/4$ and the general solution $y_n = C(x)(1/5)^n + D(x)(-1/4)^n$ are algebraically verified.
- **Oscillation Argument (Lines 21-25):** Correctly factors the difference $y_{n+1}-y_n$ and shows that as $n \to \infty$, the bracketed term approaches $-5/4 D(x)$. If $D(x) \neq 0$, the bracket maintains a constant sign while $(-1/4)^n$ alternates, causing $y_{n+1}-y_n$ to alternate sign. This correctly contradicts the strict monotonicity of $(y_n)$, forcing $D(x)=0$.
- **Conclusion (Lines 27-30):** Correctly deduces $y_n = x(1/5)^n$, yielding $g^{-1}(x) = x/5$ and thus $g(x)=5x$. Verification confirms the solution.

## Decision
Winner: A
Reason: Both proofs are mathematically sound and correctly use recurrence relations and oscillation arguments to eliminate the $(-4)^n$ component. Proof A is preferred for its tighter logical structure: by analyzing the two-sided sequence $x_n$ ($n \in \mathbb{Z}$) and comparing distinct orbits ($x < y \implies x_n < y_n$), it directly leverages the definition of strict monotonicity without requiring a separate side-check to rule out fixed points. Proof B's assertion that the inverse sequence $(y_n)$ is strictly monotonic (Line 20) omits the trivial but necessary verification that $g(x)=x \implies x=0$, creating a minor gap that Proof A avoids entirely. Additionally, Proof A's unified recurrence framework is more elegant than Proof B's separate forward/backward derivations.