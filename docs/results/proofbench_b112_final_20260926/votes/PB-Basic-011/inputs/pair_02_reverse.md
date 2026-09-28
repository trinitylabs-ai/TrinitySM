# Problem

Let $A\subset \{1,2,\ldots,2000\}$, $|A|=1000$, such that $a$ does not divide $b$ for all distinct elements $a,b\in A$. For a set $X$ as above let us denote with $m_{X}$ the smallest element in $X$. Find $\min m_{A}$ (for all $A$ with the above properties).

# Proof A

1: To find the minimum possible value of $m_A = \min(A)$ for a set $A \subset \{1, 2, \ldots, 2000\}$ with $|A| = 1000$ such that no element of $A$ divides another, we analyze the properties of antichains in the poset $(S, |)$ where $S = \{1, 2, \ldots, 2000\}$.
2: 
3: **1. Chain Cover and Dilworth's Theorem**
4: We can partition $S$ into chains by considering the odd parts of the numbers. For each odd $k \in \{1, 3, \ldots, 1999\}$, define the chain $C_k = \{k \cdot 2^j \in S \mid j \ge 0\}$. There are exactly 1000 such odd numbers, and these chains partition $S$. Since $|A| = 1000$ and $A$ is an antichain, by the pigeonhole principle, $A$ must contain exactly one element from each chain $C_k$. Let $x_k$ denote the element of $A$ in $C_k$, so $x_k = k \cdot 2^{j_k}$ for some integer $j_k \ge 0$.
5: 
6: **2. Condition for the Antichain Property**
7: For $A$ to be an antichain, no distinct $x_k, x_l \in A$ may satisfy $x_k \mid x_l$.
8: Suppose $k \mid l$ for odd $k, l$. Let $l = mk$ for some odd integer $m > 1$. The condition $x_k \nmid x_l$ means $k \cdot 2^{j_k} \nmid mk \cdot 2^{j_l}$, which simplifies to $2^{j_k} \nmid m \cdot 2^{j_l}$. Since $m$ is odd, this is equivalent to $j_k > j_l$.
9: Conversely, if $k \nmid l$, then $x_k \nmid x_l$ is automatically satisfied because the odd part of $x_k$ does not divide the odd part of $x_l$. Thus, $A$ is an antichain if and only if for all odd $k, l \in \{1, 3, \ldots, 1999\}$, $k \mid l \implies j_k > j_l$.
10: 
11: **3. Minimizing the Smallest Element**
12: We want to find the minimum possible value of $m_A = \min_{k \text{ odd}} (k \cdot 2^{j_k})$. To minimize this, we need to determine the minimum possible values for $j_k$.
13: The constraint $k \mid l \implies j_k > j_l$ implies that $j_k$ must be at least the length of the longest chain of odd multiples of $k$ in $S$. If $k = k_0 < k_1 < \ldots < k_p \le 1999$ is a chain of odd numbers where $k_i \mid k_{i+1}$, then $j_{k_0} > j_{k_1} > \ldots > j_{k_p} \ge 0$, so $j_{k_0} \ge p$.
14: The longest such chain is $k, 3k, 3^2k, \ldots, 3^p k \le 1999$, where $p = \lfloor \log_3(1999/k) \rfloor$.
15: Thus, for any valid $A$, we must have $j_k \ge \lfloor \log_3(1999/k) \rfloor$. This implies:
16: $$x_k = k \cdot 2^{j_k} \ge k \cdot 2^{\lfloor \log_3(1999/k) \rfloor}$$
17: 
18: **4. Evaluating the Lower Bound**
19: Let $f(k) = k \cdot 2^{\lfloor \log_3(1999/k) \rfloor}$. We seek the minimum of $f(k)$ for odd $k \in \{1, 3, \ldots, 1999\}$. We evaluate $f(k)$ over intervals where $p = \lfloor \log_3(1999/k) \rfloor$ is constant:
20: - For $p=6$: $1 \le k \le \lfloor 1999/3^6 \rfloor = 2$. The only odd $k$ is $1$, giving $f(1) = 1 \cdot 2^6 = 64$.
21: - For $p=5$: $3 \le k \le \lfloor 1999/3^5 \rfloor = 8$. Odd $k \in \{3, 5, 7\}$. The minimum is $f(3) = 3 \cdot 2^5 = 96$.
22: - For $p=4$: $9 \le k \le \lfloor 1999/3^4 \rfloor = 24$. Odd $k \in \{9, \ldots, 23\}$. The minimum is $f(9) = 9 \cdot 2^4 = 144$.
23: - For $p=3$: $25 \le k \le \lfloor 1999/3^3 \rfloor = 74$. Odd $k \in \{25, \ldots, 73\}$. The minimum is $f(25) = 25 \cdot 2^3 = 200$.
24: - For $p=2$: $75 \le k \le \lfloor 1999/3^2 \rfloor = 222$. Odd $k \in \{75, \ldots, 221\}$. The minimum is $f(75) = 75 \cdot 2^2 = 300$.
25: - For $p=1$: $223 \le k \le \lfloor 1999/3 \rfloor = 666$. Odd $k \in \{223, \ldots, 665\}$. The minimum is $f(223) = 223 \cdot 2^1 = 446$.
26: - For $p=0$: $667 \le k \le 1999$. Odd $k \in \{667, \ldots, 1999\}$. The minimum is $f(667) = 667 \cdot 2^0 = 667$.
27: 
28: The minimum value across all $k$ is $f(1) = 64$.
29: 
30: **5. Verification of Achievability**
31: We verify that the construction $j_k = \lfloor \log_3(1999/k) \rfloor$ for all odd $k$ yields a valid set $A$.
32: First, we check that $x_k \in \{1, \ldots, 2000\}$. Let $p = j_k$. Then $3^p \le 1999/k$. Since $2^p \le 3^p$ for all $p \ge 0$, we have $x_k = k \cdot 2^p \le k \cdot 3^p \le k \cdot (1999/k) = 1999 \le 2000$.
33: Second, we check the antichain condition. If $k \mid l$ for odd $k, l$ with $k \neq l$, then $l = mk$ for some odd $m \ge 3$. Then:
34: $$j_l = \lfloor \log_3(1999/mk) \rfloor = \lfloor \log_3(1999/k) - \log_3 m \rfloor \le \lfloor \log_3(1999/k) - 1 \rfloor = j_k - 1 < j_k$$
35: This satisfies the condition $j_k > j_l$, so $A$ is an antichain.
36: Thus, the minimum possible value of $m_A$ is 64.

# Proof B

1: To find the minimum possible value of $m_A$ (the smallest element of a set $A$), where $A \subset \{1, 2, \ldots, 2000\}$, $|A| = 1000$, and no element of $A$ divides another, we proceed as follows:
2: 
3: **1. Structural Analysis of the Set $A$**
4: The condition that no element in $A$ divides another means $A$ is an antichain under the divisibility relation. We partition the set $S = \{1, 2, \ldots, 2000\}$ into 1000 chains by grouping each number by its greatest odd divisor. Every $x \in S$ can be uniquely written as $x = 2^k \cdot d$, where $d \in \{1, 3, \ldots, 1999\}$ is an odd number. For each odd $d$, the set $C_d = \{2^k \cdot d \mid 2^k \cdot d \le 2000\}$ forms a chain under divisibility. Since there are exactly 1000 odd numbers in $S$, $S$ is covered by 1000 chains. By the Pigeonhole Principle, any antichain $A$ of size 1000 must contain exactly one element from each chain $C_d$.
5: 
6: **2. Establishing the Divisibility Constraint**
7: Let $x_d$ be the unique element of $A$ in the chain $C_d$. Thus, $x_d = 2^{k_d} \cdot d$ for some integer $k_d \ge 0$. For any two distinct odd numbers $d_1$ and $d_2$, if $d_1$ divides $d_2$, we must ensure $x_{d_1} \nmid x_{d_2}$ to satisfy the antichain property.
8: The condition $x_{d_1} \mid x_{d_2}$ is equivalent to:
9: $$2^{k_{d_1}} \cdot d_1 \mid 2^{k_{d_2}} \cdot d_2 \iff d_1 \mid d_2 \text{ and } k_{d_1} \le k_{d_2} + v_2(d_2/d_1)$$
10: Since $d_1$ and $d_2$ are odd, $d_2/d_1$ is also odd (if it is an integer), so $v_2(d_2/d_1) = 0$. Thus, if $d_1 \mid d_2$ and $d_1 \neq d_2$, we must have $k_{d_1} > k_{d_2}$ to prevent $x_{d_1}$ from dividing $x_{d_2}$.
11: 
12: **3. Determining the Minimum Value of $k_d$**
13: For any odd $d$, let $h(d)$ be the length of the longest chain of odd divisors starting from $d$ up to 1999. That is, $h(d) = \max \{ n \mid \exists \text{ odd } d = d_0 < d_1 < \ldots < d_n \le 1999 \text{ s.t. } d_i \mid d_{i+1} \}$.
14: From the constraint $k_{d_0} > k_{d_1} > \ldots > k_{d_n} \ge 0$, it follows that $k_{d_0} \ge n$. Thus, $k_d \ge h(d)$.
15: To maximize $n$, we use the smallest odd prime, 3. The longest chain is $d, 3d, 3^2d, \ldots, 3^n d$. The condition $3^n \cdot d \le 1999$ implies $n \le \log_3(1999/d)$, so $h(d) = \lfloor \log_3(1999/d) \rfloor$.
16: 
17: **4. Calculating the Minimum $m_A$**
18: The smallest element of $A$ is $m_A = \min_{d \in \{1, 3, \ldots, 1999\}} x_d$. Since $x_d = 2^{k_d} \cdot d \ge 2^{h(d)} \cdot d$, we have:
19: $$m_A \ge \min_{d \in \{1, 3, \ldots, 1999\}} (2^{h(d)} \cdot d)$$
20: We evaluate $f(d) = 2^{h(d)} \cdot d$ for the ranges of $d$ where $h(d)$ is constant:
21: - For $h=0$: $667 \le d \le 1999$, $\min f(d) = 2^0 \cdot 667 = 667$.
22: - For $h=1$: $223 \le d \le 665$, $\min f(d) = 2^1 \cdot 223 = 446$.
23: - For $h=2$: $75 \le d \le 221$, $\min f(d) = 2^2 \cdot 75 = 300$.
24: - For $h=3$: $25 \le d \le 73$, $\min f(d) = 2^3 \cdot 25 = 200$.
25: - For $h=4$: $9 \le d \le 23$, $\min f(d) = 2^4 \cdot 9 = 144$.
26: - For $h=5$: $3 \le d \le 7$, $\min f(d) = 2^5 \cdot 3 = 96$.
27: - For $h=6$: $d=1$, $f(1) = 2^6 \cdot 1 = 64$.
28: 
29: The minimum value is 64. We can construct such a set $A$ by setting $k_d = h(d)$, which yields $x_d = 2^{h(d)} \cdot d$. 
30: We verify that $x_d = 2^{h(d)} \cdot d \le 3^{h(d)} \cdot d \le 1999$, so $A \subset \{1, \ldots, 2000\}$. 
31: To verify $A$ is an antichain: if $d_1 \mid d_2$ and $d_1 \neq d_2$, then $h(d_1) \ge h(d_2) + 1$, so $k_{d_1} > k_{d_2}$, ensuring $x_{d_1} \nmid x_{d_2}$. Since $d_2 \nmid d_1$, $x_{d_2} \nmid x_{d_1}$. Thus, $A$ is a valid antichain.
32: 
33: Thus, the minimum value of $m_A$ is 64.
