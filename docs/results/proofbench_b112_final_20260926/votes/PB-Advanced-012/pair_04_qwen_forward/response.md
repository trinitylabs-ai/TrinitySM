# Proof comparison

## Proof A
Established theorem: For any prime $p$ and positive integers $a,b$, if $p^n = a^4 + b^4$ with $n \geq 2$, then $n \geq 5$. The proof correctly eliminates even $n$ via Fermat's theorem on $x^4+y^4=z^2$, reduces to the coprime case $p^3 = A^4+B^4$, and exhaustively rules out $n=3$ using factorization in $\mathbb{Z}[i]$, modular obstructions, and infinite descent.
Claim gap: NONE supported by checks. All parity and divisibility subcases for $n=3$ are resolved with verified contradictions.
Qualifications and supplied repairs: NONE. The argument is self-contained. Minor notational imprecision in Line 26 (using $g$ for $\gcd(u,t)$ then stating $\gcd(u^2-t, u^2+t)=2$) does not affect the arithmetic contradiction $s^2 = 2m^2n^2$, which correctly forces a non-square prime factor.
Decisive checks: 
- Line 4: Correct application of Fermat's right triangle theorem to eliminate even $n$.
- Lines 12-15: Correct factorization in $\mathbb{Z}[i]$ and unit absorption. Coprimality and opposite parity ensure $\gcd(A^2+iB^2, A^2-iB^2)$ is a unit, justifying the cube extraction.
- Lines 23-27: Case 1 subcases correctly use mod 3 and mod 8 obstructions. The factorization $(u^2-t)(u^2+t)=3s^4$ is handled correctly; the assignment $\{2m^4, 6n^4\}$ yields $s^2=2m^2n^2$, a valid contradiction.
- Lines 32-40: The descent on $v^2+s^4=3u^4$ is rigorously verified. Mod 3 forces $3|v,s$, substitution yields $V_1^2+S^4=3U^4$, establishing a valid infinite descent to the trivial solution, contradicting $a,b>0$.
- Falsification check: No counterexample exists; the modular and descent steps cover all configurations for coprime $A,B$.

## Proof B
Established theorem: Rules out $p=2$ with $n<5$ via mod 16 analysis. Rules out $n=2$ and $n=4$ for odd $p$ using Pythagorean parametrization and FLT. Reduces $n=3$ to a system of Diophantine equations in $\mathbb{Z}[i]$ and correctly handles the $3 \nmid x,y$ subcase.
Claim gap: The resolution of the $3|x$ subcase for $n=3$ (Lines 20-21) relies on the unproven assertion that the elliptic curve $Y^2 = X(X-3)(X-27)$ has rank 0. This is stated as a fact ("A 2-descent shows...") without any computation, descent steps, or reference to Selmer groups. In a self-contained Olympiad proof, this is a load-bearing gap. The argument does not establish the non-existence of rational points beyond torsion, leaving the $n=3$ case incomplete.
Qualifications and supplied repairs: To close the gap, one would need to perform a full 2-descent on the curve or transform the system $y^2-3k^2=\beta^2, y^2-27k^2=\delta^2$ into an elementary infinite descent (as done in Proof A). The submission provides neither.
Decisive checks:
- Lines 4-7: Correct mod 16 analysis for $p=2$.
- Lines 12-13: Correct reduction of $n=2$ to $x^4+y^4=z^2$ via primitive Pythagorean triples.
- Lines 14-19: Correct expansion in $\mathbb{Z}[i]$ and sign determination via mod 3.
- Lines 20-21: The elliptic curve rank claim is the earliest load-bearing defect. While the curve likely has rank 0, the proof offers no verification. Without it, the contradiction for $3|x$ is unsupported. The symmetric $3|y$ case inherits the same gap.

## Decision
Winner: A
Reason: Proof A provides a complete, self-contained elementary argument. It correctly handles the parity of $n$, reduces to $n=3$, and exhaustively resolves all subcases using verified modular obstructions and a rigorous infinite descent on $v^2+s^4=3u^4$. Proof B correctly handles $p=2$, $n=2$, and $n=4$, but its treatment of $n=3$ halts at an unjustified appeal to the rank of an elliptic curve. While the rank claim is likely true, it is presented as a black-box assertion without descent steps or arithmetic verification, leaving the core obligation ($n \neq 3$) mathematically incomplete. Proof A's descent directly establishes the required contradiction with full justification, making it the stronger and valid solution.