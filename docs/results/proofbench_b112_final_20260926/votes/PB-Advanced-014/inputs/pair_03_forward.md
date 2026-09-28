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
