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
