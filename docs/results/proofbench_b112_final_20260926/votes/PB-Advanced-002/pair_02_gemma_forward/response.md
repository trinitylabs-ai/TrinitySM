# Proof comparison

## Proof A
Established theorem: $M(f) \le 2^{70}$ for any function $f: F \to F$ defined by a love relation on 120 students.
Claim gap: NONE supported by your checks.
Qualifications and supplied repairs: The numerical estimate $g(120) \approx 3 \times 10^6$ is an underestimate (the actual value is $\approx 2.23 \times 10^8$), but this does not affect the validity of the final inequality $M(f) \le 2^{70}$.
Decisive checks: 
- The reduction of the problem to the maximum number of distinct elements in a trajectory $f^k(X)$ is correct (lines 9-11).
- The identification of the period $C$ as the least common multiple of the periods of the strongly connected components (SCCs), where the period of an SCC is the greatest common divisor of its cycle lengths, is mathematically correct (line 14).
- The bound $C \le g(120)$ is correct because the sum of the periods of the SCCs is at most the sum of their sizes, which is $N=120$.
- The bound on the pre-period $P \le N^2$ is a standard result for Boolean matrices (line 15).
- The final calculation $P + C \ll 2^{70}$ is verified.

## Proof B
Established theorem: $M(f) \le 2^{70}$ for any function $f: F \to F$ defined by a love relation on 120 students.
Claim gap: The derivation of the period $p_i$ is conceptually flawed.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The reduction to the maximum number of distinct elements in a trajectory is correct (line 15).
- The claim that the period $p_i$ "corresponds to the least common multiple of the lengths of all cycles reachable from $i$" (line 20) is incorrect. The period of a strongly connected component is the gcd of its cycle lengths, not the lcm.
- If the period were actually the lcm of all cycle lengths, the bound $g(120)$ would not apply. The lcm of all cycle lengths in a graph with 120 vertices can be as large as $\text{lcm}(1, 2, \dots, 120) \approx 10^{52}$, which far exceeds $2^{70}$.
- Although the proof later uses the correct bound $g(120)$ (line 24), this bound does not follow from the previously stated (and incorrect) definition of the period.

## Decision
Winner: A
Reason: Proof A provides a mathematically sound derivation of the period of the function $f$, correctly identifying it as the lcm of the gcds of cycle lengths within strongly connected components. Proof B contains a significant conceptual error, claiming the period is the lcm of all cycle lengths; if this were true, the result $M(f) \le 2^{70}$ would be false, as the lcm of all cycle lengths in a 120-vertex graph can exceed $10^{50}$. Proof A's only minor flaw is a numerical underestimate of $g(120)$, which does not impact the correctness of the final bound.