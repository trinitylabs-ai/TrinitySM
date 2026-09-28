# Problem

Let $A\subset \{1,2,\ldots,2000\}$, $|A|=1000$, such that $a$ does not divide $b$ for all distinct elements $a,b\in A$. For a set $X$ as above let us denote with $m_{X}$ the smallest element in $X$. Find $\min m_{A}$ (for all $A$ with the above properties).

# Proof A

1: To find the minimum possible value of the smallest element $m_A$ for a set $A \subset \{1, 2, \ldots, 2000\}$ with $|A| = 1000$ such that no element of $A$ divides another, we proceed as follows:
2: 
3: **1. Representation of the Set $A$**
4: Every integer $x \in \{1, 2, \ldots, 2000\}$ can be uniquely written in the form $x = 2^k \cdot d$, where $d$ is an odd integer. The possible odd parts $d$ are the elements of the set $O = \{1, 3, \ldots, 1999\}$. There are exactly $\frac{1999-1}{2} + 1 = 1000$ such odd integers.
5: If two distinct elements $x, y \in A$ share the same odd part $d$, say $x = 2^{k_1}d$ and $y = 2^{k_2}d$ with $k_1 < k_2$, then $x$ would divide $y$, contradicting the property of $A$. Since $|A| = 1000$ and there are only 1000 distinct odd parts available, each odd integer $d \in O$ must be the odd part of exactly one element $x_d \in A$. Thus, we can write $x_d = 2^{k(d)} \cdot d$ for some function $k: O \to \{0, 1, 2, \ldots\}$.
6: 
7: **2. The Antichain Condition**
8: For $A$ to be an antichain under divisibility, for any two distinct odd integers $d, e \in O$, $x_d$ must not divide $x_e$. If $d$ divides $e$, then $x_d$ divides $x_e$ if and only if $2^{k(d)}d$ divides $2^{k(e)}e$. This occurs if and only if $k(d) \le k(e) + \nu_2(e/d)$. Since $d$ and $e$ are both odd, $e/d$ is odd, meaning $\nu_2(e/d) = 0$. Therefore, for $d|e$ and $d \neq e$, we must have $k(d) > k(e)$.
9: 
10: **3. Establishing a Lower Bound for $m_A$**
11: For any $d \in O$, let $h(d)$ be the length of the longest chain of odd integers $d = d_0, d_1, \ldots, d_{h(d)-1}$ in $O$ such that $d_i | d_{i+1}$ for all $i$. The longest such chain is constructed by multiplying by the smallest odd prime, 3. Thus, $h(d) = \lfloor \log_3(1999/d) \rfloor + 1$.
12: From the condition $k(d_i) > k(d_{i+1})$, we have a strictly decreasing sequence of non-negative integers $k(d_0) > k(d_1) > \dots > k(d_{h(d)-1}) \ge 0$. This implies $k(d) \ge h(d) - 1$. Consequently,
13: \[ x_d = 2^{k(d)} d \ge 2^{h(d)-1} d = 2^{\lfloor \log_3(1999/d) \rfloor} d. \]
14: Let $f(d) = 2^{\lfloor \log_3(1999/d) \rfloor} d$. We find the minimum of $f(d)$ across all $d \in O$:
15: - For $h(d) = 7$: $3^6 \cdot d \le 1999 \implies 729d \le 1999 \implies d=1$. $f(1) = 2^6 \cdot 1 = 64$.
16: - For $h(d) = 6$: $3^5 \cdot d \le 1999 \implies 243d \le 1999 \implies d \in \{3, 5, 7\}$. $f(3) = 2^5 \cdot 3 = 96$, $f(5) = 160$, $f(7) = 224$.
17: - For $h(d) = 5$: $3^4 \cdot d \le 1999 \implies 81d \le 1999 \implies d \le 24$. The smallest odd $d$ with $h(d)=5$ is $d=9$, giving $f(9) = 2^4 \cdot 9 = 144$.
18: - For $h(d) = 4$: $3^3 \cdot d \le 1999 \implies 27d \le 1999 \implies d \le 74$. The smallest odd $d$ with $h(d)=4$ is $d=25$, giving $f(25) = 2^3 \cdot 25 = 200$.
19: - For $h(d) = 3$: $3^2 \cdot d \le 1999 \implies 9d \le 1999 \implies d \le 222$. The smallest odd $d$ with $h(d)=3$ is $d=75$, giving $f(75) = 2^2 \cdot 75 = 300$.
20: - For $h(d) = 2$: $3 \cdot d \le 1999 \implies d \le 666$. The smallest odd $d$ with $h(d)=2$ is $d=223$, giving $f(223) = 2^1 \cdot 223 = 446$.
21: - For $h(d) = 1$: $d \ge 667$. $f(667) = 667$.
22: 
23: Thus, $m_A = \min_{d \in O} x_d \ge \min_{d \in O} f(d) = 64$.
24: 
25: **4. Construction for $m_A = 64$**
26: Define $k(d) = \lfloor \log_3(1999/d) \rfloor$. As shown above, if $d|e$ and $d \neq e$, then $e \ge 3d$, so $k(e) = \lfloor \log_3(1999/e) \rfloor \le \lfloor \log_3(1999/3d) \rfloor = k(d) - 1 < k(d)$. This ensures $A$ is an antichain. Furthermore, we previously verified that for all $d$, $x_d = 2^{k(d)}d \le 2000$. In this set, $m_A = f(1) = 64$.
27: 
28: The minimum value of $m_A$ is 64. \(\square\)

# Proof B

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
