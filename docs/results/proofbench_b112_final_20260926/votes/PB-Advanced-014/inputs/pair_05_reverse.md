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
