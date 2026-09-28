# Proof comparison

## Proof A
Established theorem: The process terminates after finitely many moves with exactly one integer $M > 1$ on the blackboard, and the value of $M$ is uniquely determined by the initial multiset of integers.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Termination:** The proof correctly defines a lexicographic potential function $(N, S)$ where $N$ counts integers $>1$ and $S$ sums prime factor multiplicities. The derivation $\Delta S = -f(\gcd(m,n))$ is algebraically sound. The case analysis correctly shows $(N, S)$ strictly decreases in all valid moves. The argument that $N$ cannot reach 0 (requiring $g=h=1 \implies m=n=1$, contradicting hypotheses) correctly establishes termination at $N=1$.
- **Invariance:** The proof correctly tracks prime exponents $v_p$ and identifies the transformation $(a,b) \to (\min(a,b), |a-b|)$. It correctly applies the Euclidean property $\gcd(\min(a,b), |a-b|) = \gcd(a,b)$ to show the GCD of the exponent multiset is invariant. The final state evaluation $\gcd(v_p(M), 0, \dots, 0) = v_p(M)$ correctly fixes $M$ independently of move choices.

## Proof B
Established theorem: The process terminates after finitely many moves with exactly one integer $M > 1$ on the blackboard, and the value of $M$ is uniquely determined by the initial multiset of integers.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks:
- **Termination:** The proof correctly defines a lexicographic potential function $(P, N)$ where $P$ is the product of all integers and $N$ counts integers $>1$. The derivation $P_{\text{new}} = P_{\text{old}} / \gcd(m,n)$ is direct and correct. The case analysis correctly shows $(P, N)$ strictly decreases. The proof explicitly notes that $N$ decreases by at most 1 per move (since at least one of $g, L$ remains $>1$), providing a clear and rigorous justification that the process must halt exactly at $N=1$.
- **Invariance:** The proof uses identical exponent tracking and GCD invariance logic as Proof A. The derivation is clear, correctly handles the absolute difference in exponents, and properly concludes $v_p(M) = \gcd(\text{initial exponents})$, fixing $M$ uniquely.

## Decision
Winner: B
Reason: Both proofs are mathematically complete and correct. Proof B is preferred for its slightly more transparent termination argument. Proof B's potential function $(P, N)$ leverages the multiplicative nature of the operation more naturally than Proof A's additive sum of prime factors, yielding a simpler derivation of the potential change. Furthermore, Proof B explicitly establishes that the count $N$ decreases by at most 1 per move, making the justification for halting at exactly $N=1$ (rather than $N=0$) more rigorous and easier to verify. Proof A's corresponding argument is correct but slightly compressed. The invariance sections are equivalent in both.