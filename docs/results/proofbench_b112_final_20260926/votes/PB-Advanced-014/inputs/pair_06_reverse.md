# Problem

Two distinct positive integers \( a \) and \( b \) are written on a blackboard. At each step, you must choose one of the two operations — either adding 2 or multiplying by 3 — for each number separately, and apply the chosen operation to both numbers (possibly using different operations). You must apply an operation to both numbers every step. Find all pairs $(a, b)$ such that we can make the two numbers on the blackboard equal after a finite number of steps.

# Proof A

1: To determine all pairs of distinct positive integers $(a, b)$ such that they can be made equal through the given operations, we analyze the properties of the transformations $x \to x+2$ and $x \to 3x$.
2: 
3: **1. Parity Invariance**
4: Observe the operations modulo 2.
5: - For $x \to x+2$, $x+2 \equiv x \pmod 2$.
6: - For $x \to 3x$, $3x \equiv x \pmod 2$.
7: In both cases, the parity of the number is invariant. Thus, if the two numbers become equal after a finite number of steps, they must have had the same parity initially. This implies $a \equiv b \pmod 2$ is a necessary condition.
8: 
9: **2. Reachable Values**
10: Let $x_n$ be the value reached from $a$ after $n$ steps. Let $k$ be the number of times the multiplication operation was used. The value $x_n$ can be expressed as:
11: \[ x_n = 3^k a + 2 \sum_{j=0}^k c_j 3^j, \quad \text{where } \sum_{j=0}^k c_j = n-k \text{ and } c_j \ge 0. \]
12: Let $S = \sum_{j=0}^k c_j 3^j$. A value $Z$ is reachable from $a$ in $n$ steps if there exists $k \in \{0, \dots, n\}$ such that $Z = 3^k a + 2S$ and $S$ can be represented as a sum of $m = n-k$ powers of 3, each power being $\le 3^k$.
13: 
14: We now derive the conditions under which $S$ can be represented as a sum of $m$ powers of 3. Any positive integer $S$ has a unique base-3 representation $S = \sum_{i=0}^N d_i 3^i$ where $d_i \in \{0, 1, 2\}$. The number of terms in this sum is $s_3(S) = \sum d_i$. We can increase the number of terms by replacing any $3^i$ (for $i > 0$) with $3^{i-1} + 3^{i-1} + 3^{i-1}$, which increases the total count of terms by $3-1 = 2$. By repeating this process, $S$ can be represented as a sum of $m$ powers of 3 if and only if $s_3(S) \le m \le S$ and $m \equiv s_3(S) \pmod 2$. The maximum $m=S$ is reached when all terms are $3^0=1$.
15: 
16: For a fixed $k$ and $Z$, $S = (Z - 3^k a)/2$ is fixed. By choosing $Z$ to be sufficiently large, the condition $m \le S$ and the constraint that the powers are $\le 3^k$ (which is satisfied if $3^k \ge S$) can be easily met for a wide range of $m$. The only remaining constraint on $n$ is the parity:
17: \[ n-k \equiv s_3(S) \pmod 2 \implies n \equiv k + s_3(S) \pmod 2. \]
18: Since $s_3(S) \equiv S \pmod 2$ (because $3^j \equiv 1 \pmod 2$), the condition is $n \equiv k + S \pmod 2$.
19: 
20: **3. Condition for Equality**
21: Two numbers $a$ and $b$ can be made equal if there exist $n, k_1, k_2, S_1, S_2$ such that $Z = 3^{k_1} a + 2S_1 = 3^{k_2} b + 2S_2$ and:
22: \[ n \equiv k_1 + S_1 \equiv k_2 + S_2 \pmod 2. \]
23: This requires $k_1 + \frac{Z - 3^{k_1} a}{2} \equiv k_2 + \frac{Z - 3^{k_2} b}{2} \pmod 2$, which simplifies to:
24: \[ \frac{3^{k_2} b - 3^{k_1} a}{2} \equiv k_2 - k_1 \pmod 2 \iff 3^{k_2} b - 3^{k_1} a \equiv 2(k_2 - k_1) \pmod 4. \]
25: Using $3 \equiv -1 \pmod 4$, we test the parities of $k_1, k_2$:
26: - If $k_1 \equiv k_2 \pmod 2$, the condition is $(-1)^{k_2} b - (-1)^{k_1} a \equiv 0 \pmod 4$, which implies $a \equiv b \pmod 4$.
27: - If $k_1 \not\equiv k_2 \pmod 2$, the condition is $(-1)^{k_2} b - (-1)^{k_1} a \equiv 2 \pmod 4$, which implies $a + b \equiv 2 \pmod 4$.
28: 
29: **4. Final Synthesis**
30: - If $a, b$ are both even, they can be $(0,0), (2,2), (0,2),$ or $(2,0) \pmod 4$. The first two satisfy $a \equiv b \pmod 4$ and the latter two satisfy $a+b \equiv 2 \pmod 4$. Thus, all even pairs work.
31: - If $a, b$ are both odd, they can be $(1,1), (3,3),$ or $(1,3) \pmod 4$. $(1,1)$ and $(3,3)$ satisfy $a \equiv b \pmod 4$. For $(1,3)$, $a \equiv b \pmod 4$ is false and $a+b = 4 \equiv 0 \not\equiv 2 \pmod 4$. Thus, odd pairs work if and only if $a \equiv b \pmod 4$.
32: 
33: The pairs $(a, b)$ are those that have the same parity, and if they are odd, they must be congruent modulo 4. This is equivalent to saying $a \equiv b \pmod 4$ or both $a$ and $b$ are even.
34: 
35: \(\square\)

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
