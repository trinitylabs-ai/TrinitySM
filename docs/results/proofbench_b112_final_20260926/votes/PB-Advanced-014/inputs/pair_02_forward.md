# Problem

Two distinct positive integers \( a \) and \( b \) are written on a blackboard. At each step, you must choose one of the two operations — either adding 2 or multiplying by 3 — for each number separately, and apply the chosen operation to both numbers (possibly using different operations). You must apply an operation to both numbers every step. Find all pairs $(a, b)$ such that we can make the two numbers on the blackboard equal after a finite number of steps.

# Proof A

1: Let the two distinct positive integers be $a$ and $b$. The available operations are $f(x) = x+2$ and $g(x) = 3x$. In each step, we apply one of these operations to each number independently.
2: 
3: **1. Necessary Conditions**
4: First, observe that for any integer $x$, $f(x) = x+2 \equiv x \pmod 2$ and $g(x) = 3x \equiv x \pmod 2$. Thus, the parity of each number is invariant under both operations. For the two numbers to become equal, they must have the same parity. Thus, $a \equiv b \pmod 2$ is a necessary condition.
5: 
6: Next, consider the case where $a$ and $b$ are odd. We examine the operations modulo 4. For any odd integer $x$:
7: - If $x \equiv 1 \pmod 4$, then $f(x) = x+2 \equiv 3 \pmod 4$ and $g(x) = 3x \equiv 3 \pmod 4$.
8: - If $x \equiv 3 \pmod 4$, then $f(x) = x+2 \equiv 1 \pmod 4$ and $g(x) = 3x \equiv 1 \pmod 4$.
9: In both cases, any operation applied to an odd integer flips its residue modulo 4. After $n$ steps, the numbers $x_n$ and $y_n$ will satisfy $x_n \equiv a + 2n \pmod 4$ and $y_n \equiv b + 2n \pmod 4$. For $x_n = y_n$, we must have $x_n \equiv y_n \pmod 4$, which implies $a + 2n \equiv b + 2n \pmod 4$, simplifying to $a \equiv b \pmod 4$. Thus, $a \equiv b \pmod 4$ is a necessary condition for odd $a, b$.
10: 
11: **2. Sufficiency for Odd Integers**
12: Assume $a$ and $b$ are odd and $a \equiv b \pmod 4$. Let $a < b$ and let $d_n = y_n - x_n$ be the difference after $n$ steps. Since $a \equiv b \pmod 4$, $d_0 = b-a$ is a multiple of 4.
13: We aim to reach $d_n = 0$. Note that if $d_n$ is a multiple of 4 and $x_n$ is odd, then $d_{n+1}$ remains a multiple of 4 under any operation pair:
14: - $(f, f): d_{n+1} = (y_n+2) - (x_n+2) = d_n$.
15: - $(f, g): d_{n+1} = 3y_n - (x_n+2) = 3(x_n+d_n) - x_n - 2 = 2x_n + 3d_n - 2$. Since $x_n$ is odd, $2x_n - 2$ is a multiple of 4, so $d_{n+1} \equiv 0 \pmod 4$.
16: - $(g, f): d_{n+1} = (y_n+2) - 3x_n = (x_n+d_n+2) - 3x_n = d_n - 2x_n + 2$. Since $x_n$ is odd, $-2x_n + 2$ is a multiple of 4, so $d_{n+1} \equiv 0 \pmod 4$.
17: - $(g, g): d_{n+1} = 3y_n - 3x_n = 3d_n$.
18: 
19: We use the following strategy:
20: - If $d_n > 0$ and $x_n \le \frac{d_n}{2} + 1$, we apply the operation pair $(f, f)$ repeatedly until $x_m = \frac{d_n}{2} + 1$. Since $d_n$ is a multiple of 4, $\frac{d_n}{2} + 1$ is odd, so this is possible. Then, applying the operation pair $(g, f)$ gives $d_{m+1} = (y_m + 2) - 3x_m = (x_m + d_n + 2) - 3x_m = d_n - 2(x_m - 1) = d_n - 2(\frac{d_n}{2}) = 0$.
21: - If $d_n > 0$ and $x_n > \frac{d_n}{2} + 1$, we apply the operation pair $(f, g)$. The new difference is $d_{n+1} = 2x_n + 3d_n - 2$ and the new value of $x$ is $x_{n+1} = x_n + 2$. We check if $x_{n+1} \le \frac{d_{n+1}}{2} + 1$:
22:   $\frac{d_{n+1}}{2} + 1 = \frac{2x_n + 3d_n - 2}{2} + 1 = x_n + 1.5d_n$.
23:   Since $d_n \ge 4$, we have $x_n + 1.5d_n \ge x_n + 6 > x_n + 2 = x_{n+1}$.
24: Thus, we can always reach a state where $x_n \le \frac{d_n}{2} + 1$ and then reach $d=0$.
25: 
26: **3. Sufficiency for Even Integers**
27: Assume $a$ and $b$ are even. Let $a = 2a'$ and $b = 2b'$. The operations $x \to x+2$ and $x \to 3x$ on the blackboard correspond to $x' \to x'+1$ and $x' \to 3x'$ for the halved values. Let $a' < b'$ and $d'_n = b'_n - a'_n$.
28: We aim to reach $d'_n = 0$ using $f'(x) = x+1$ and $g'(x) = 3x$.
29: Note that applying the operation pair $(g', f')$ results in $d'_{n+1} = (b'_n + 1) - 3a'_n = d'_n - 2a'_n + 1$. If we can reach a state where $d'_n = 2a'_n - 1$, then $(g', f')$ makes $d'_{n+1} = 0$.
30: Let $h_n = d'_n - 2a'_n$. We want to reach $h_n = -1$.
31: - Operation $(f', f')$: $a' \to a'+1, d' \to d' \implies h_{n+1} = d'_n - 2(a'_n + 1) = h_n - 2$.
32: - Operation $(f', g')$: $a' \to a'+1, d' \to 3b'_n - (a'_n + 1) = 3(a'_n + d'_n) - a'_n - 1 = 3d'_n + 2a'_n - 1$.
33:   Then $h_{n+1} = (3d'_n + 2a'_n - 1) - 2(a'_n + 1) = 3d'_n - 3$.
34: 
35: If $h_n < 0$, applying $(f', g')$ gives $h_{n+1} = 3d'_n - 3$. Since $d'_n \ge 1$, $h_{n+1} \ge 0$.
36: Once $h_n \ge 0$:
37: - If $h_n$ is odd, we apply $(f', f')$ repeatedly to decrease $h$ by 2 until $h = -1$.
38: - If $h_n$ is even, we apply $(f', f')$ repeatedly until $h = 0$. Then we apply $(f', g')$ to get $h_{new} = 3d'_n - 3$. Since $h=0 \implies d'_n = 2a'_n$, we have $h_{new} = 6a'_n - 3$, which is odd. We then apply $(f', f')$ to reach $h = -1$.
39: Once $h = -1$, we apply $(g', f')$ to reach $d' = 0$.
40: 
41: **Conclusion**
42: The numbers can be made equal if and only if $a$ and $b$ are both even, or they are both odd and $a \equiv b \pmod 4$.

# Proof B

1: Let the two operations be $f_1(x) = x+2$ and $f_2(x) = 3x$. Let $a_n$ and $b_n$ be the values obtained from $a$ and $b$ after $n$ steps.
2: 
3: **1. Necessary Conditions**
4: Both operations preserve parity: $f_1(x) \equiv x \pmod 2$ and $f_2(x) \equiv x \pmod 2$. Thus, $a_n \equiv a \pmod 2$ and $b_n \equiv b \pmod 2$ for all $n$. For $a_n = b_n$ to be possible, we must have $a \equiv b \pmod 2$.
5: 
6: If $a$ and $b$ are odd, we examine the residues modulo 4.
7: - If $x \equiv 1 \pmod 4$, then $f_1(x) = x+2 \equiv 3 \pmod 4$ and $f_2(x) = 3x \equiv 3 \pmod 4$.
8: - If $x \equiv 3 \pmod 4$, then $f_1(x) = x+2 \equiv 1 \pmod 4$ and $f_2(x) = 3x \equiv 9 \equiv 1 \pmod 4$.
9: In both cases, every operation flips the residue modulo 4. After $n$ steps, $a_n \equiv a + 2n \pmod 4$ and $b_n \equiv b + 2n \pmod 4$. For $a_n = b_n$, we require $a + 2n \equiv b + 2n \pmod 4$, which implies $a \equiv b \pmod 4$.
10: Thus, the necessary conditions are $a \equiv b \pmod 2$, and if $a, b$ are odd, $a \equiv b \pmod 4$.
11: 
12: **2. Sufficiency**
13: Suppose $a$ and $b$ satisfy the necessary conditions. Let $k$ and $m$ be the number of times the operation $f_2$ is applied to $a$ and $b$ respectively over $n$ steps. Let $c_i$ be the number of additions of 2 performed after the $i$-th multiplication and before the $(i+1)$-th (with $c_0$ before the first and $c_k$ after the last). Then $\sum_{i=0}^k c_i = n-k$. The final value is:
14: \[ a_n = 3^k a + 2 \sum_{i=0}^k c_i 3^i \]
15: Similarly, $b_n = 3^m b + 2 \sum_{j=0}^m d_j 3^j$ where $\sum_{j=0}^m d_j = n-m$.
16: Let $S(K, M) = \{ \sum_{i=0}^K c_i 3^i \mid \sum c_i = M, c_i \in \mathbb{N}_0 \}$. An integer $V \in S(K, M)$ if and only if $M_{min}(V, K) \le M \le V$ and $M \equiv V \pmod 2$, where $M_{min}(V, K) = \lfloor V/3^K \rfloor + s_3(V \pmod{3^K})$ and $s_3(x)$ is the sum of digits of $x$ in base 3.
17: 
18: We seek $n, k, m$ and $C \in S(k, n-k), D \in S(m, n-m)$ such that $3^k a + 2C = 3^m b + 2D$.
19: Let $\Delta = \frac{3^m b - 3^k a}{2}$. We need $C - D = \Delta$ and $(n-k) - (n-m) = m-k$.
20: Let $M_b = n-m$ and $M_a = n-k$. We require $M_a - M_b = m-k$ and $C = D + \Delta$.
21: The conditions for $C \in S(k, M_a)$ and $D \in S(m, M_b)$ are:
22: 1. $M_{min}(D, m) \le M_b \le D$ and $M_b \equiv D \pmod 2$.
23: 2. $M_{min}(C, k) \le M_a \le C$ and $M_a \equiv C \pmod 2$.
24: 
25: Pick $k=1$ and $m$ such that $m-k \equiv \Delta \pmod 2$. This is equivalent to $2(m-k) \equiv 3^m b - 3^k a \pmod 4$, which simplifies to $2(m-1) \equiv (-1)^m b - (-1)^1 a \pmod 4$.
26: - If $a, b$ are even, let $a=2A, b=2B$. Then $2(m-1) \equiv (-1)^m 2B + 2A \pmod 4$, so $m-1 \equiv (-1)^m B + A \pmod 2$. This is always solvable for $m$ (if $m$ is even, $1 \equiv B+A \pmod 2$; if $m$ is odd, $0 \equiv A-B \pmod 2$).
27: - If $a, b$ are odd, then $2(m-1) \equiv (-1)^m b + a \pmod 4$. If $m$ is even, $-2 \equiv b+a \pmod 4$; if $m$ is odd, $0 \equiv -b+a \pmod 4$. Both are equivalent to $a \equiv b \pmod 4$.
28: 
29: With $k=1$ and $m$ chosen, let $D = M_b$ for some large $M_b$. Then $M_{min}(M_b, m) = \lfloor M_b/3^m \rfloor + s_3(M_b \pmod{3^m}) \le M_b$ is true for $M_b \ge 1$, and $M_b \equiv M_b \pmod 2$ is trivial.
30: Now let $C = M_b + \Delta$ and $M_a = M_b + m - 1$.
31: For $M_b$ sufficiently large:
32: - $M_a \le C \iff M_b + m - 1 \le M_b + \Delta \iff \Delta \ge m-1$. This is true for $m \ge 1$ since $\Delta = \frac{3^m b - 3a}{2}$ eventually grows exponentially.
33: - $M_a \equiv C \pmod 2 \iff M_b + m - 1 \equiv M_b + \Delta \pmod 2 \iff m-1 \equiv \Delta \pmod 2$, which we ensured.
34: - $M_{min}(C, 1) = \lfloor (M_b + \Delta)/3 \rfloor + s_3((M_b + \Delta) \pmod 3) \le \frac{M_b + \Delta}{3} + 2$.
35:   For large $M_b$, $\frac{M_b + \Delta}{3} + 2 \le M_b + m - 1$ is clearly true.
36: 
37: Thus, for sufficiently large $n = M_b + m$, we can make the two numbers equal.
38: 
39: **Conclusion**
40: The pairs $(a, b)$ are those where $a \equiv b \pmod 2$, and if $a, b$ are odd, $a \equiv b \pmod 4$.
