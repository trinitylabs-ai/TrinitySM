# Problem

IMO 2026 Problem 1. There are 2026 integers greater than 1 written on a blackboard, not necessarily different. In one move, Confucius chooses two integers m > 1 and n > 1 from different positions on the blackboard and replaces them by gcd(m,n) and lcm(m,n)/gcd(m,n). He continues making moves for as long as this is possible. (1) Prove that, regardless of Confucius's choices, after finitely many moves exactly one integer M on the blackboard is greater than 1. (2) Prove that the value of M does not depend on Confucius's choices. Here gcd(x,y) denotes the greatest common divisor of positive integers x,y, and lcm(x,y) denotes their least common multiple.

# Proof A

1: To solve the problem, we analyze the operation performed by Confucius and its effect on the set of integers on the blackboard.
2: 
3: ### Part (1): Termination of the Process
4: 
5: Let $n = 2026$ be the number of integers on the blackboard. Let the integers at any given state be $a_1, a_2, \dots, a_n$. A move consists of choosing two integers $m, n > 1$ from different positions and replacing them with $g = \gcd(m, n)$ and $h = \frac{\text{lcm}(m, n)}{\gcd(m, n)}$.
6: 
7: Let $f(x)$ denote the total number of prime factors of $x$ counted with multiplicity (the additive prime-omega function). For any two positive integers $m$ and $n$, we have:
8: \[ f(g) + f(h) = \sum_p v_p(\gcd(m, n)) + \sum_p v_p\left(\frac{\text{lcm}(m, n)}{\gcd(m, n)}\right) \]
9: \[ = \sum_p \min(v_p(m), v_p(n)) + \sum_p (\max(v_p(m), v_p(n)) - \min(v_p(m), v_p(n))) \]
10: \[ = \sum_p \max(v_p(m), v_p(n)) \]
11: Let $S = \sum_{i=1}^n f(a_i)$ be the sum of the number of prime factors of all integers on the blackboard. The change in $S$ during a move is:
12: \[ \Delta S = (f(g) + f(h)) - (f(m) + f(n)) = \sum_p (\max(v_p(m), v_p(n)) - (v_p(m) + v_p(n))) \]
13: \[ = - \sum_p \min(v_p(m), v_p(n)) = -f(\gcd(m, n)) \]
14: Since $m, n > 1$, we consider the number of integers $N$ on the blackboard that are greater than 1.
15: 1. If $\gcd(m, n) > 1$, then $f(\gcd(m, n)) > 0$, so $S$ strictly decreases. If $m \neq n$, $g > 1$ and $h = \text{lcm}(m, n)/\gcd(m, n) > 1$, so $N$ remains unchanged. If $m = n$, then $h = 1$ and $N$ decreases by 1.
16: 2. If $\gcd(m, n) = 1$, then $S$ remains constant, but $g = 1$ and $h = mn > 1$, so $N$ decreases by 1.
17: 
18: In all cases, the pair $(N, S)$ decreases lexicographically. Since $N \ge 1$ (as $S$ only decreases when $\gcd(m, n) > 1$, and if $\gcd(m, n) = 1$, $S$ is invariant; the only way to reach $N=0$ is if a move results in $g=1$ and $h=1$, which implies $m=1$ and $n=1$, contradicting $m, n > 1$) and $S \ge 0$, the process must terminate. It terminates when $N < 2$, meaning exactly one integer $M > 1$ remains.
19: 
20: ### Part (2): Invariance of $M$
21: 
22: For a fixed prime $p$, let $x_i = v_p(a_i)$ be the exponent of $p$ in the prime factorization of $a_i$. When Confucius replaces $m, n$ with $g, h$, the exponents $(v_p(m), v_p(n))$ are replaced by:
23: \[ v_p(g) = \min(v_p(m), v_p(n)) \quad \text{and} \quad v_p(h) = |v_p(m) - v_p(n)| \]
24: A fundamental property of the greatest common divisor is that for any non-negative integers $a, b$:
25: \[ \gcd(a, b) = \gcd(\min(a, b), |a - b|) \]
26: Consequently, the $\gcd$ of the set of exponents $\{v_p(a_1), v_p(a_2), \dots, v_p(a_n)\}$ is invariant under the operation. Let $g_p = \gcd(v_p(a_1), \dots, v_p(a_n))$ be this invariant.
27: 
28: At the termination of the process, only one integer $M$ is greater than 1, and all other integers are 1. For any prime $p$, the exponents are $v_p(M)$ and $0, 0, \dots, 0$. The invariant $\gcd$ gives:
29: \[ g_p = \gcd(v_p(M), 0, \dots, 0) = v_p(M) \]
30: Thus, the exponent of every prime $p$ in the final integer $M$ is uniquely determined by the initial integers $a_i$:
31: \[ v_p(M) = \gcd(v_p(a_1), v_p(a_2), \dots, v_p(a_{2026})) \]
32: This implies that $M = \prod_p p^{g_p}$, which is independent of the sequence of moves chosen by Confucius. $\square$

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
