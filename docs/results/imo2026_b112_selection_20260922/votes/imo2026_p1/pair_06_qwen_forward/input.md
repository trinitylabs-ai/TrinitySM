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
