# Problem

IMO 2026 Problem 1. There are 2026 integers greater than 1 written on a blackboard, not necessarily different. In one move, Confucius chooses two integers m > 1 and n > 1 from different positions on the blackboard and replaces them by gcd(m,n) and lcm(m,n)/gcd(m,n). He continues making moves for as long as this is possible. (1) Prove that, regardless of Confucius's choices, after finitely many moves exactly one integer M on the blackboard is greater than 1. (2) Prove that the value of M does not depend on Confucius's choices. Here gcd(x,y) denotes the greatest common divisor of positive integers x,y, and lcm(x,y) denotes their least common multiple.

# Proof A

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
