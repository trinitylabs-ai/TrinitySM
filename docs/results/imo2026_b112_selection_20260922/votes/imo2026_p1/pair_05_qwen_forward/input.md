# Problem

IMO 2026 Problem 1. There are 2026 integers greater than 1 written on a blackboard, not necessarily different. In one move, Confucius chooses two integers m > 1 and n > 1 from different positions on the blackboard and replaces them by gcd(m,n) and lcm(m,n)/gcd(m,n). He continues making moves for as long as this is possible. (1) Prove that, regardless of Confucius's choices, after finitely many moves exactly one integer M on the blackboard is greater than 1. (2) Prove that the value of M does not depend on Confucius's choices. Here gcd(x,y) denotes the greatest common divisor of positive integers x,y, and lcm(x,y) denotes their least common multiple.

# Proof A

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
