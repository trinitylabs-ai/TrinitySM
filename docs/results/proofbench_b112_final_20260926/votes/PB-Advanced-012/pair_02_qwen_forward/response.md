# Proof comparison

## Proof A
Established theorem: For any prime $p$ and positive integers $a, b$, if $p^n = a^4 + b^4$ with $n \geq 2$, then $n \geq 5$.
Claim gap: NONE supported by checks.
Qualifications and supplied repairs: NONE.
Decisive checks: 
- **Gaussian Factorization & Expansion (Lines 12-13):** The factorization $(a^2+ib^2)(a^2-ib^2)=p^3$ correctly yields coprime factors in $\mathbb{Z}[i]$ for odd $p$ (since $a,b$ have opposite parity, $1+i \nmid a^2+ib^2$). The expansion $a^2 = u(u^2-3v^2), b^2 = v(3u^2-v^2)$ is algebraically verified.
- **Modulo 8 Elimination (Lines 17-24):** The parity analysis for $u,v$ correctly covers all cases for $3 \nmid u,v$ and $3|u$. Checks like $y^2 \equiv 5 \pmod 8$ or $y^2 \equiv 7 \pmod 8$ are verified contradictions, as quadratic residues mod 8 are $\{0,1,4\}$.
- **Infinite Descent ($3|v$) (Lines 27-34):** The GCD analysis of $(x^2-z)(x^2+z)=3w^4$ exhaustively covers $g \in \{1,2,3,6\}$. The $g=2$ subcase correctly reduces to $x^2 - (m^2)^2 = 3(8N^2)^2$. The parameterization $x=p^2+3q^2, 8N^2=2pq, m^2=|p^2-3q^2|$ is a standard complete parameterization for $X^2-3Y^2=Z^2$. The deduction $4N^2=pq \implies p=u^2, q=v^2$ (using $\gcd(p,q)=1$) is verified. The descent $x = u^4+3v^4 > u$ is strictly valid for positive integers, and the alternative branch $m^2=3v^4-u^4$ is correctly ruled out by modulo 3 arithmetic. No silent repairs were needed.

## Proof B
Established theorem: For any prime $p$ and positive integers $a, b$, if $p^n = a^4 + b^4$ with $n \geq 2$, then $n \geq 5$, *conditional* on the non-existence of rational points on a specific intersection of quadrics.
Claim gap: The proof of the $n=3$ case for $p > 2$ contains a load-bearing gap in the $3|x$ subcase (Line 21). It asserts that the system $y^2-3k^2=\beta^2$ and $y^2-27k^2=\delta^2$ implies a rational point on $Y^2 = X(X-3)(X-27)$, and claims "A 2-descent shows the rank of this curve is 0" without justification. This is a non-trivial result in arithmetic geometry that is not established within the text.
Qualifications and supplied repairs: The auditor must accept the unverified claim that the elliptic curve $Y^2 = X(X-3)(X-27)$ has rank 0 and that its torsion points $(0,0), (3,0), (27,0)$ do not yield valid rational $X=(y/k)^2$. This constitutes a substantive missing justification.
Decisive checks: 
- **Case $3 \nmid x, 3 \nmid y$ (Line 17):** The sign analysis $\epsilon_1=1, \epsilon_2=-1$ via modulo 3 is correct. The sum $-2(x^2+y^2) = \beta^2+\delta^2$ correctly yields a contradiction. This portion is verified and elegant.
- **Case $3 | x$ (Line 21):** The reduction to $X, X-3, X-27$ being rational squares is algebraically correct. However, the appeal to the rank of the elliptic curve is an unsupported citation. Without a proof or reference, the argument fails to rule out rational solutions, leaving the $n=3$ case incomplete.

## Decision
Winner: A
Reason: Proof A provides a complete, self-contained elementary proof. It rigorously verifies all modular arithmetic checks, GCD cases, and the infinite descent step without relying on external unproven claims. Proof B, while elegant in its handling of the $3 \nmid x, y$ subcase, contains a load-bearing gap by citing the rank of a specific elliptic curve without justification. In a mathematical audit, an unverified appeal to advanced machinery is a defect compared to a fully justified elementary derivation. Proof A meets all obligations; Proof B does not.