# Problem

IMO 2026 Problem 1. There are 2026 integers greater than 1 written on a blackboard, not necessarily different. In one move, Confucius chooses two integers m > 1 and n > 1 from different positions on the blackboard and replaces them by gcd(m,n) and lcm(m,n)/gcd(m,n). He continues making moves for as long as this is possible. (1) Prove that, regardless of Confucius's choices, after finitely many moves exactly one integer M on the blackboard is greater than 1. (2) Prove that the value of M does not depend on Confucius's choices. Here gcd(x,y) denotes the greatest common divisor of positive integers x,y, and lcm(x,y) denotes their least common multiple.

# Proof A

1: To prove the statements, we analyze the transformation of the integers on the blackboard through their prime factorizations.
2: 
3: ### Part 1: Termination of the Process
4: 
5: Let the integers on the blackboard be $a_1, a_2, \dots, a_n$ where $n=2026$. A move consists of choosing two integers $m, n > 1$ from different positions and replacing them with $g = \gcd(m, n)$ and $l = \frac{\text{lcm}(m, n)}{\gcd(m, n)}$.
6: 
7: Let $\Omega(x)$ denote the number of prime factors of $x$ counted with multiplicity (i.e., if $x = \prod p_i^{e_i}$, then $\Omega(x) = \sum e_i$). For any two positive integers $m$ and $n$, we have:
8: $$\Omega(m) + \Omega(n) = \sum_{p} (v_p(m) + v_p(n))$$
9: where $v_p(x)$ is the exponent of prime $p$ in the prime factorization of $x$. After a move, the new sum of $\Omega$ values for the two affected positions is:
10: $$\Omega(g) + \Omega(l) = \sum_{p} (v_p(\gcd(m, n)) + v_p(\text{lcm}(m, n)/\gcd(m, n)))$$
11: Using the identities $v_p(\gcd(m, n)) = \min(v_p(m), v_p(n))$ and $v_p(\text{lcm}(m, n)) = \max(v_p(m), v_p(n))$, we get:
12: $$\Omega(g) + \Omega(l) = \sum_{p} (\min(v_p(m), v_p(n)) + \max(v_p(m), v_p(n)) - \min(v_p(m), v_p(n))) = \sum_{p} \max(v_p(m), v_p(n)) = \Omega(\text{lcm}(m, n))$$
13: Since $\text{lcm}(m, n)$ divides $mn$, it follows that $\Omega(\text{lcm}(m, n)) \le \Omega(m) + \Omega(n)$. Let $S = \sum_{i=1}^n \Omega(a_i)$ be the total sum of prime exponents on the board. Let $k$ be the number of integers on the board greater than 1. We track the pair $(S, k)$ lexicographically:
14: 
15: 1.  **If $\gcd(m, n) > 1$**: Then $\Omega(\gcd(m, n)) \ge 1$. The sum $S$ decreases by $(\Omega(m) + \Omega(n)) - \Omega(\text{lcm}(m, n)) = \Omega(\gcd(m, n)) > 0$. Thus, $(S, k)$ strictly decreases.
16: 2.  **If $\gcd(m, n) = 1$**: Then $\Omega(\text{lcm}(m, n)) = \Omega(m) + \Omega(n)$, so $S$ remains constant. However, the new integers are $g = 1$ and $l = \text{lcm}(m, n)/1 = mn$. Since $m, n > 1$, we have $mn > 1$. Thus, we replace two integers greater than 1 with exactly one integer greater than 1, so $k$ decreases by 1. Thus, $(S, k)$ strictly decreases.
17: 
18: Since $S$ and $k$ are non-negative integers, this process must terminate. Termination occurs when no two integers are greater than 1, meaning $k \le 1$. Because $m, n > 1$, we have $\text{lcm}(m, n) > 1$, so $\Omega(\text{lcm}(m, n)) \ge 1$. This implies that the sum $S$ always remains at least 1 throughout the process. Consequently, the final state cannot have $k=0$ (which would imply $S=0$), so the process must terminate with exactly one integer $M > 1$.
19: 
20: ### Part 2: Invariance of $M$
21: 
22: For a fixed prime $p$, let the exponents of $p$ for the integers on the board be $x_1, x_2, \dots, x_n$. A move on $m, n$ replaces their exponents $(v_p(m), v_p(n))$ with:
23: $$v_p(g) = \min(v_p(m), v_p(n)) \quad \text{and} \quad v_p(l) = \max(v_p(m), v_p(n)) - \min(v_p(m), v_p(n)) = |v_p(m) - v_p(n)|$$
24: Consider the greatest common divisor of the exponents for a fixed prime $p$: $G_p = \gcd(x_1, x_2, \dots, x_n)$. Under a move, the $\gcd$ of the two affected exponents changes from $\gcd(v_p(m), v_p(n))$ to $\gcd(\min(v_p(m), v_p(n)), |v_p(m) - v_p(n)|)$. By the fundamental property of the Euclidean algorithm, $\gcd(a, b) = \gcd(a, b-a)$ for $b \ge a$, so:
25: $$\gcd(v_p(m), v_p(n)) = \gcd(\min(v_p(m), v_p(n)), |v_p(m) - v_p(n)|)$$
26: Since the $\gcd$ of the two affected exponents is preserved, the overall $\gcd$ of the set of exponents $G_p$ is invariant for every prime $p$ throughout the process. In the final state, only one integer $M$ is greater than 1, so the exponents are $(v_p(M), 0, \dots, 0)$. The $\gcd$ of these exponents is:
27: $$\gcd(v_p(M), 0, \dots, 0) = v_p(M)$$
28: Therefore, $v_p(M) = G_p = \gcd(v_p(a_1), \dots, v_p(a_n))$ for every prime $p$. This uniquely determines $M$ as:
29: $$M = \prod_{p} p^{\gcd(v_p(a_1), \dots, v_p(a_n))}$$
30: Since $M$ depends only on the initial integers $a_i$, its value is independent of Confucius's choices.

# Proof B

1: To solve the problem, we analyze the operation performed by Confucius on the set of integers $\{a_1, a_2, \dots, a_N\}$ where $N=2026$ and $a_i > 1$.
2: 
3: ### 1. Termination of the Process
4: Let $C$ be the number of integers on the blackboard that are greater than 1. A move consists of choosing two integers $m, n > 1$ from different positions and replacing them with $g = \gcd(m, n)$ and $l' = \frac{\text{lcm}(m, n)}{\gcd(m, n)}$. 
5: 
6: Let $\Omega(x)$ denote the total number of prime factors of $x$ counted with multiplicity (e.g., $\Omega(12) = \Omega(2^2 \cdot 3) = 3$). Consider the sum $S = \sum_{i=1}^N \Omega(a_i)$. For a chosen pair $(m, n)$, the new sum $S'$ is:
7: \[ S' = S - \Omega(m) - \Omega(n) + \Omega(g) + \Omega(l') \]
8: Since $\text{lcm}(m, n) = \frac{mn}{\gcd(m, n)}$, we have $l' = \frac{mn}{\gcd(m, n)^2}$. Thus, $\Omega(l') = \Omega(m) + \Omega(n) - 2\Omega(g)$. Substituting this into the expression for $S'$, we find:
9: \[ S' = S - \Omega(m) - \Omega(n) + \Omega(g) + (\Omega(m) + \Omega(n) - 2\Omega(g)) = S - \Omega(g) \]
10: Since $g = \gcd(m, n) \ge 1$, we have $\Omega(g) \ge 0$. We observe two cases:
11: - If $g > 1$, then $\Omega(g) \ge 1$, so $S$ strictly decreases.
12: - If $g = 1$, then $S$ remains constant, but the pair $(m, n)$ is replaced by $(1, mn)$. Since $m, n > 1$ and $g=1$, the product $mn > 1$, so the number of integers greater than 1, $C$, decreases by exactly 1.
13: 
14: The process terminates when no two integers $m, n > 1$ can be chosen, meaning $C \le 1$. Since $S$ is bounded below by 0 and $C$ is bounded below by 0, and the pair $(S, C)$ decreases lexicographically in every move, the process must terminate in finitely many moves.
15: 
16: ### 2. Invariance of the Final Value $M$
17: Let $v_p(x)$ denote the exponent of the prime $p$ in the prime factorization of $x$. For a chosen pair $m, n$, let $v_p(m) = x$ and $v_p(n) = y$. The new exponents for $p$ are:
18: \[ v_p(g) = v_p(\gcd(m, n)) = \min(x, y) \]
19: \[ v_p(l') = v_p\left(\frac{\text{lcm}(m, n)}{\gcd(m, n)}\right) = \max(x, y) - \min(x, y) = |x - y| \]
20: A fundamental property of the greatest common divisor is that $\gcd(x, y) = \gcd(\min(x, y), |x - y|)$ for any non-negative integers $x, y$. Consequently, for every prime $p$, the value $g_p = \gcd(v_p(a_1), v_p(a_2), \dots, v_p(a_N))$ is invariant under the move.
21: 
22: When the process terminates, we have $C \le 1$. If $C = 0$, then all $a_i = 1$, which implies $v_p(a_i) = 0$ for all $i, p$. However, we are given $a_i > 1$ initially, so there is at least one prime $p$ and index $i$ such that $v_p(a_i) > 0$. Thus, $g_p = \gcd(v_p(a_1), \dots, v_p(a_N))$ is the GCD of a set containing at least one positive integer, so $g_p \ge 1$ for at least one prime $p$. This implies that the final state must have exactly one integer $M > 1$.
23: 
24: In this final state, the exponents are $(0, 0, \dots, v_p(M), \dots, 0)$. The GCD of these exponents is simply $v_p(M)$. Since $g_p$ is invariant:
25: \[ v_p(M) = g_p = \gcd(v_p(a_1), v_p(a_2), \dots, v_p(a_N)) \]
26: This must hold for all primes $p$. Therefore, the final value $M$ is uniquely determined by the initial integers:
27: \[ M = \prod_p p^{\gcd(v_p(a_1), \dots, v_p(a_N))} \]
28: which is independent of Confucius's choices.
