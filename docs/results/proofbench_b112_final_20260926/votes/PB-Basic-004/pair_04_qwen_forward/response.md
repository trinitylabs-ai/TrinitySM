# Proof comparison

## Proof A
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Recurrence & Inverse Setup (Lines 5-19):** The forward recurrence $a_{n+2}=a_{n+1}+20a_n$ and inverse recurrence $20y_{n+2}+y_{n+1}-y_n=0$ are correctly derived from the functional equation and the bijectivity of $g$. The characteristic roots $5,-4$ and $1/5,-1/4$ are correctly computed.
- **Oscillation Argument (Lines 20-25):** The proof correctly notes that $y_n=g^{-n}(x)$ must be strictly monotonic because $g^{-1}$ is strictly increasing. The difference $y_{n+1}-y_n$ is algebraically factored into $(-\frac{1}{4})^n$ times a bracketed term. The limit of the bracket as $n\to\infty$ is explicitly shown to be $-\frac{5}{4}D(x)$. If $D(x)\neq 0$, the bracket maintains a constant sign for large $n$, while $(-\frac{1}{4})^n$ alternates sign, forcing $y_{n+1}-y_n$ to alternate sign. This rigorously contradicts monotonicity, proving $D(x)=0$.
- **Conclusion (Lines 27-30):** $D(x)=0$ yields $y_n=x(1/5)^n$, giving $g^{-1}(x)=x/5$ and thus $g(x)=5x$. Verification confirms all hypotheses.

## Proof B
Established theorem: The only strictly increasing, surjective function $g:\mathbb{R} \to \mathbb{R}$ satisfying $g(g(x))=g(x)+20x$ is $g(x)=5x$.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Recurrence & Order Preservation (Lines 4-24):** The forward recurrence $x_{n+2}-x_{n+1}-20x_n=0$ is correctly established for $n\in\mathbb{Z}$. The proof correctly uses the strict monotonicity of $g$ to assert $x_n < y_n$ for all $n\in\mathbb{Z}$ when $x<y$, leading to $\Delta A + \Delta B(-4/5)^n > 0$.
- **Oscillation Argument (Lines 25-27):** Analyzing $n\to-\infty$ via $n=-m$, the inequality becomes $\Delta A + \Delta B(-5/4)^m > 0$. The proof correctly argues that if $\Delta B \neq 0$, the term $\Delta B(-5/4)^m$ oscillates with unbounded magnitude, eventually violating the inequality for a subsequence of $m$. This forces $\Delta B=0$, implying $B(x)$ is constant.
- **Conclusion (Lines 29-41):** $B(x)=C$ leads to $g(x)=5x-9C$. Substitution into the original equation forces $C=0$, yielding $g(x)=5x$. Verification confirms all hypotheses.

## Decision
Winner: A
Reason: Both proofs are mathematically complete and correct. Proof A is preferred because its oscillation argument (Lines 20-25) is more formally structured: it explicitly factors the difference term, computes the limit of the bracketed expression, and rigorously demonstrates the sign alternation contradiction. Proof B's argument (Lines 25-27) reaches the same conclusion but relies on slightly less formal phrasing ("large negative number") regarding the asymptotic behavior. Proof A's direct analysis of a single orbit's monotonicity is also marginally more self-contained than Proof B's comparison of two orbits.