# Proof comparison

## Proof A
Established theorem: $M(f) \le 120 + g(120) \ll 2^{70}$, where $g(120)$ is the Landau function.
Claim gap: The justification for the period $p$ is mathematically incorrect and internally contradictory. The proof claims $p$ is the "least common multiple of the lengths of all cycles reachable from $i$," but then asserts $p \le g(120)$. The LCM of all cycle lengths in a directed graph with 120 nodes can be as large as $\text{lcm}(1, 2, \dots, 120) \approx e^{120}$, which far exceeds $2^{70}$. The actual period of the sequence $f^k(X)$ is the LCM of the periods of the strongly connected components (SCCs), where the period of an SCC is the GCD of its cycle lengths.
Qualifications and supplied repairs: The proof's value for $g(120) \approx 2.23 \times 10^8$ is an underestimate (the actual value is $\approx 2.6 \times 10^{10}$), though this does not affect the final inequality.
Decisive checks:
- The chain argument (lines 15-16) is verified: the condition that $A_i$ and $A_j$ have a lovely relationship for all $i < j$ forces the elements to lie on a single trajectory in the functional graph.
- The period claim (line 20) is falsified: for an SCC with cycles of length 2 and 3, the period of the sequence $S_k(i)$ is $\gcd(2, 3) = 1$, whereas the LCM of the cycle lengths is $\text{lcm}(2, 3) = 6$.
- The bound $p \le g(120)$ (line 24) is only true if $p$ is the LCM of the GCDs of cycle lengths in disjoint SCCs, not the LCM of all cycle lengths.

## Proof B
Established theorem: $M(f) \le 120^2 + g(120) \ll 2^{70}$, where $g(120)$ is the Landau function.
Claim gap: NONE.
Qualifications and supplied repairs: NONE.
Decisive checks:
- The chain argument (lines 12-14) is verified: the distinct elements must form a chain in the reachability preorder, implying they lie on a single orbit.
- The period analysis (lines 20-21) is verified: the period of the sequence $M^k v$ is the LCM of the periods of the SCCs, and the period of an SCC is the GCD of its cycle lengths. This correctly justifies $p \le g(N)$.
- The pre-period bound (line 24) is verified: the exponent of a Boolean matrix of size $N$ is at most $(N-1)^2 + 1$.
- The calculation of $g(120) \approx 2.6 \times 10^{10}$ (line 26) is verified using the partition $16+9+5+7+11+13+17+19+23 = 120$.
- The final bound (lines 29-31) is verified: $14400 + 2.6 \times 10^{10} \ll 10^{21} \approx 2^{70}$.

## Decision
Winner: B
Reason: Proof B is mathematically rigorous and correct. It accurately identifies the period of the sequence $f^k(A)$ as the LCM of the GCDs of cycle lengths within the strongly connected components of the love graph, which is the correct way to bound the period by the Landau function $g(120)$. Proof A, conversely, incorrectly claims the period is the LCM of all cycle lengths; if this were true, the period could exceed $2^{70}$, making Proof A's subsequent claim that $p \le g(120)$ both false and contradictory. Proof B also provides a more accurate value for $g(120)$.