# Proof comparison

## Proof A
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- Fixed point analysis: $g(0)=0$ is correctly derived from $g(g(0))=g(0)+20(0)$ and the fact that $g(x)=x \implies x=0$ (lines 4-5).
- Monotonicity: $g(x)>x$ for $x>0$ is correctly derived by contradiction (line 8).
- Recurrence relation: The sequence $a_{n+1}=g(a_n)$ satisfies $a_{n+2}=a_{n+1}+20a_n$ with characteristic roots $5$ and $-4$ (lines 12-13).
- Bi-infinite orbit: For $x_0 > 0$, $x_n = g^{(n)}(x_0) > 0$ for all $n \in \mathbb{Z}$ (line 20).
- Asymptotic behavior: As $n \to -\infty$ ($n=-m$), $x_{-m} = A(1/5)^m + B(-1/4)^m$. For large $m$, the sign of $x_{-m}$ is determined by $B(-1/4)^m$. If $B \neq 0$, the sign alternates, contradicting $x_{-m} > 0$ (lines 21-26).
- Conclusion: $B(x)=0$ for all $x$, leading to $g(x)=5x$ (lines 27-30).

## Proof B
Established theorem: The only strictly increasing surjective function $g: \mathbb{R} \to \mathbb{R}$ such that $g(g(x)) = g(x) + 20x$ is $g(x) = 5x$.
Claim gap: NONE supported by my checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- Continuity: $g$ is correctly identified as continuous due to surjectivity and strict monotonicity (line 4).
- Recurrence relation: The sequence $x_{n+1}=g(x_n)$ satisfies $x_{n+2}=x_{n+1}+20x_n$ with characteristic roots $5$ and $-4$ (lines 8-11).
- Monotonicity: $x_n$ is correctly shown to be monotonic for all $n \in \mathbb{Z}$ (lines 18-21).
- Asymptotic behavior: The difference $\Delta_n = x_{n+1}-x_n = 4A 5^n - 5B (-4)^n$. As $n \to -\infty$ ($n=-m$), $\Delta_{-m} = \frac{1}{4^m} [4A(4/5)^m - 5B(-1)^{-m}]$. For large $m$, the sign of $\Delta_{-m}$ is determined by $-5B(-1)^{-m}$. If $B \neq 0$, the sign alternates, contradicting monotonicity (lines 24-28).
- Conclusion: $B(x_0)=0$ for all $x_0$, leading to $g(x)=5x$ (lines 31-33).

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct, employing the same central strategy of using a linear recurrence and analyzing the behavior of the orbit as $n \to -\infty$ to eliminate the root $-4$. Proof A is slightly stronger as it provides a more detailed initial analysis of the function's properties (fixed points and the relationship between $g(x)$ and $x$), which provides a more direct and intuitive justification for the sign of the orbit $x_n$ than Proof B's analysis of the difference $\Delta_n$.