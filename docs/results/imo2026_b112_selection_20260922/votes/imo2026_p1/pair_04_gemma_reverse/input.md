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

1: Let the integers on the blackboard at any time be represented by the multiset $S = \{x_1, x_2, \dots, x_{2026}\}$. A move consists of choosing two integers $m, n \in S$ such that $m > 1$ and $n > 1$, and replacing them with $g = \gcd(m, n)$ and $L = \frac{\text{lcm}(m, n)}{\gcd(m, n)}$.
2: 
3: ### Part (1): Termination and Final State
4: 
5: To prove that the process terminates, we define a potential function $\Phi(S) = (P(S), N(S))$, where $P(S) = \prod_{i=1}^{2026} x_i$ is the product of all integers on the board and $N(S)$ is the number of integers $x_i > 1$. We order these pairs lexicographically.
6: 
7: In a move $(m, n) \to (g, L)$, the product $P$ changes as follows:
8: $$P_{new} = P_{old} \cdot \frac{g \cdot L}{m \cdot n} = P_{old} \cdot \frac{\gcd(m, n) \cdot \frac{\text{lcm}(m, n)}{\gcd(m, n)}}{m \cdot n} = P_{old} \cdot \frac{\text{lcm}(m, n)}{m \cdot n} = \frac{P_{old}}{\gcd(m, n)}$$
9: We consider two cases based on $\gcd(m, n)$:
10: 1. If $\gcd(m, n) > 1$, then $P_{new} < P_{old}$. Thus, $\Phi(S)$ strictly decreases.
11: 2. If $\gcd(m, n) = 1$, then $P_{new} = P_{old}$. In this case, $g = 1$ and $L = \text{lcm}(m, n) = mn$. Since $m, n > 1$, we have $L > 1$. The number of integers greater than 1, $N(S)$, decreases by exactly 1 because two integers greater than 1 ($m$ and $n$) are replaced by one integer greater than 1 ($L$) and one integer equal to 1 ($g$). Thus, $\Phi(S)$ strictly decreases.
12: 
13: Since $P(S)$ is a positive integer and $N(S)$ is a non-negative integer, the sequence of potential functions must terminate. Termination occurs when no more moves are possible, which happens if and only if $N(S) \le 1$.
14: 
15: We now show that the process ends with exactly one integer $M > 1$. Suppose the process is at a state where $N(S) \ge 2$. Let $m, n > 1$ be two such integers. The move replaces them with $g = \gcd(m, n)$ and $L = \text{lcm}(m, n)/\gcd(m, n)$. For $N(S)$ to decrease to 0, we would need $g=1$ and $L=1$. However, $L=1$ implies $\text{lcm}(m, n) = \gcd(m, n)$, which means $m=n$. If $m=n > 1$, then $g=m > 1$. If $m \neq n$, then $\text{lcm}(m, n) > \gcd(m, n)$, so $L > 1$. In all cases, at least one of $g$ or $L$ must be greater than 1. Thus, $N(S)$ can decrease by at most 1 in each move. Since we start with $N(S) = 2026$, the process must terminate at $N(S) = 1$.
16: 
17: ### Part (2): Invariance of the Final Value $M$
18: 
19: Let $p$ be any prime. For any integer $x \ge 1$, let $v_p(x)$ denote the exponent of $p$ in the prime factorization of $x$. Let the exponents of $p$ for the integers on the board be $e_1, e_2, \dots, e_{2026}$.
20: In a move $(m, n) \to (g, L)$, the exponents $v_p(m)$ and $v_p(n)$ are replaced by:
21: $$v_p(g) = v_p(\gcd(m, n)) = \min(v_p(m), v_p(n))$$
22: $$v_p(L) = v_p\left(\frac{\text{lcm}(m, n)}{\gcd(m, n)}\right) = v_p(\text{lcm}(m, n)) - v_p(\gcd(m, n)) = \max(v_p(m), v_p(n)) - \min(v_p(m), v_p(n)) = |v_p(m) - v_p(n)|$$
23: Let $a = v_p(m)$ and $b = v_p(n)$. The operation on the exponents is $(a, b) \to (\min(a, b), |a - b|)$. We observe that:
24: $$\gcd(\min(a, b), |a - b|) = \gcd(a, b)$$
25: This is a standard property of the greatest common divisor: if $a \le b$, then $\gcd(a, b-a) = \gcd(a, b)$. Therefore, for every prime $p$, the value $G_p = \gcd(v_p(x_1), v_p(x_2), \dots, v_p(x_{2026}))$ is invariant throughout the process.
26: 
27: When the process terminates, exactly one integer $M$ is greater than 1, and all other integers are 1. For any prime $p$, the exponents on the board are $(v_p(M), 0, 0, \dots, 0)$. The invariant $G_p$ must therefore satisfy:
28: $$G_p = \gcd(v_p(M), 0, \dots, 0) = v_p(M)$$
29: Thus, the final integer $M$ is uniquely determined by the initial values:
30: $$M = \prod_{p} p^{G_p} = \prod_{p} p^{\gcd(v_p(x_1), v_p(x_2), \dots, v_p(x_{2026}))}$$
31: This value depends only on the initial set of integers and not on the choices made by Confucius.
