# Problem

Two distinct positive integers \( a \) and \( b \) are written on a blackboard. At each step, you must choose one of the two operations — either adding 2 or multiplying by 3 — for each number separately, and apply the chosen operation to both numbers (possibly using different operations). You must apply an operation to both numbers every step. Find all pairs $(a, b)$ such that we can make the two numbers on the blackboard equal after a finite number of steps.

# Proof A

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

# Proof B

1: To determine all pairs of distinct positive integers $(a, b)$ such that they can be made equal after a finite number of steps using the operations $x \mapsto x+2$ and $x \mapsto 3x$, we analyze the properties of these operations.
2: 
3: **1. Parity Invariant**
4: Let $a_n$ and $b_n$ be the numbers on the blackboard after $n$ steps. The available operations are $x \mapsto x+2$ and $x \mapsto 3x$. Both operations preserve the parity of the number:
5: - $x+2 \equiv x \pmod 2$
6: - $3x \equiv x \pmod 2$
7: Therefore, $a_n \equiv a \pmod 2$ and $b_n \equiv b \pmod 2$ for all $n \ge 0$. For $a_n = b_n$ to be possible, we must have $a \equiv b \pmod 2$.
8: 
9: **2. The Case where $a$ and $b$ are Odd**
10: Suppose $a$ and $b$ are odd. Let $d_n = b_n - a_n$. The available transitions for $d_n$ are:
11: - $(a+2, b+2) \implies d_{n+1} = (b_n+2) - (a_n+2) = d_n$.
12: - $(3a, 3b) \implies d_{n+1} = 3b_n - 3a_n = 3d_n$.
13: - $(3a, b+2) \implies d_{n+1} = (b_n+2) - 3a_n = (b_n-a_n) - (2a_n-2) = d_n - 2(a_n-1)$.
14: - $(a+2, 3b) \implies d_{n+1} = 3b_n - (a_n+2) = 3(b_n-a_n) + (2a_n-2) = 3d_n + 2(a_n-1)$.
15: 
16: Let $J_n = 2(a_n-1)$. Since $a_n$ is odd, $a_n-1$ is even, so $J_n$ is always a multiple of 4. We analyze $d_n$ modulo 4:
17: - $d_{n+1} \equiv d_n \pmod 4$ if we use $(a+2, b+2)$ or $(3a, b+2)$.
18: - $d_{n+1} \equiv 3d_n \equiv -d_n \pmod 4$ if we use $(3a, 3b)$ or $(a+2, 3b)$.
19: 
20: If $d_0 = b - a \equiv 2 \pmod 4$, then $d_n$ will always be congruent to $2$ or $-2 \equiv 2 \pmod 4$. In this case, $d_n$ can never be 0. Thus, if $a$ and $b$ are odd, it is necessary that $a \equiv b \pmod 4$.
21: 
22: To show sufficiency, assume $a \equiv b \pmod 4$. Then $d_0$ is a multiple of 4.
23: 1. **Establish $d > 0$**: If $d_0 < 0$, apply $(a+2, b+2)$ repeatedly to increase $a_n$ until $J_n > -3d_0$. Then apply $(a+2, 3b)$ to obtain $d_1 = 3d_0 + J_n > 0$.
24: 2. **Growth Phase**: Use $(a+2, 3b)$ repeatedly. The evolution of the difference $d - J$ is $d_{n+1} - J_{n+1} = (3d_n + J_n) - (J_n + 4) = 3d_n - 4$. Since $d_n$ is a multiple of 4 and $d_n > 0$, we have $d_n \ge 4$, so $d_{n+1} - J_{n+1} \ge 8$. This ensures $d_n$ can be made arbitrarily large.
25: 3. **Matching and Elimination**: Once $d_n > J_n$, use $(a+2, b+2)$ to increase $a_m$ until $J_m = 2(a_m-1) = d_n$. This is possible because $J$ increases by 4 each step and $d_n \equiv J_n \equiv 0 \pmod 4$. Finally, apply $(3a, b+2)$ to obtain $d_{m+1} = d_n - J_m = 0$.
26: 
27: **3. The Case where $a$ and $b$ are Even**
28: Suppose $a$ and $b$ are even. Let $a = 2a'$ and $b = 2b'$. The operations $x \mapsto x+2$ and $x \mapsto 3x$ on $a, b$ are equivalent to $x \mapsto x+1$ and $x \mapsto 3x$ on $a', b'$.
29: Let $d'_n = b'_n - a'_n$ and $J'_n = 2a'_n - 1$. The transitions for $d'_n$ are:
30: - $(a'+1, b'+1) \implies d'_{n+1} = d'_n$.
31: - $(3a', 3b') \implies d'_{n+1} = 3d'_n$.
32: - $(3a', b'+1) \implies d'_{n+1} = (b'_n+1) - 3a'_n = d'_n - (2a'_n-1) = d'_n - J'_n$.
33: - $(a'+1, 3b') \implies d'_{n+1} = 3b'_n - (a'_n+1) = 3d'_n + (2a'_n-1) = 3d'_n + J'_n$.
34: 
35: We can make $d'_n = 0$ as follows:
36: 1. **Establish $d' > 0$**: If $d'_0 < 0$, use $(a'+1, b'+1)$ to make $J'_n > -3d'_0$, then apply $(a'+1, 3b')$ to get $d'_1 = 3d'_0 + J'_n > 0$.
37: 2. **Growth Phase**: If $d'_n$ is even, apply $(a'+1, 3b')$ to get $d'_{n+1} = 3d'_n + J'_n$, which is odd since $J'_n$ is always odd. Once $d'_n$ is odd, use $(a'+1, 3b')$ repeatedly. The difference $d'_{n+1} - J'_{n+1} = (3d'_n + J'_n) - (J'_n + 2) = 3d'_n - 2$. For $d'_n \ge 1$, this difference is at least 1 and grows rapidly.
38: 3. **Matching and Elimination**: Once $d'_n > J'_n$, use $(a'+1, b'+1)$ to increase $a'_m$ until $J'_m = 2a'_m - 1 = d'_n$. This is possible because $J'_m$ increases by 2 each step and $d'_n, J'_n$ are both odd. Finally, apply $(3a', b'+1)$ to obtain $d'_{m+1} = d'_n - J'_m = 0$.
39: 
40: **4. Synthesis**
41: The numbers can be made equal if and only if $a \equiv b \pmod 2$, and if $a, b$ are odd, $a \equiv b \pmod 4$. This is equivalent to saying $a \equiv b \pmod 2$, and if $a$ is odd, then $a \equiv b \pmod 4$.
42: 
43: The pairs $(a, b)$ are all pairs of distinct positive integers such that $a \equiv b \pmod 2$, and if $a, b$ are odd, $a \equiv b \pmod 4$.
