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

1: To find the minimum possible value of the smallest element $m_A$ for a set $A \subset \{1, 2, \dots, 2000\}$ with $|A| = 1000$ such that no element in $A$ divides another, we proceed as follows:
2: 
3: ### 1. Decomposition by Odd Parts
4: Every integer $n \in \{1, 2, \dots, 2000\}$ can be uniquely written in the form $n = 2^k \cdot o$, where $o$ is an odd integer. The set of all possible odd parts for integers in $\{1, 2, \dots, 2000\}$ is $O = \{1, 3, 5, \dots, 1999\}$. There are exactly 1000 such odd integers.
5: 
6: If $A$ is an antichain under divisibility with $|A| = 1000$, then $A$ must contain exactly one element for each odd part $o \in O$. Indeed, if $A$ contained two elements with the same odd part, say $a = 2^{k_1} o$ and $b = 2^{k_2} o$ with $k_1 < k_2$, then $a$ would divide $b$, which is forbidden. Thus, we can represent $A$ as:
7: $$A = \{2^{k_o} \cdot o : o \in O\}$$
8: where $k_o \ge 0$ for each $o \in O$.
9: 
10: ### 2. The Antichain Condition
11: The condition that no element in $A$ divides another implies that for any two distinct odd integers $o_1, o_2 \in O$, if $o_1$ divides $o_2$, then $2^{k_{o_1}} o_1$ cannot divide $2^{k_{o_2}} o_2$. 
12: Divisibility $2^{k_{o_1}} o_1 \mid 2^{k_{o_2}} o_2$ occurs if and only if $o_1 \mid o_2$ and $k_{o_1} \le k_{o_2}$. To prevent this, whenever $o_1 \mid o_2$ and $o_1 \neq o_2$, we must have $k_{o_1} > k_{o_2}$.
13: 
14: ### 3. Determining the Minimum Possible $m_A$
15: Let $L(o)$ be the length of the longest chain of odd integers in $O$ starting at $o$. To maximize the length of a chain $o = o_1 \mid o_2 \mid \dots \mid o_L$ where each $o_i \le 1999$, we want the ratios $o_{i+1}/o_i$ to be as small as possible. The smallest odd integer greater than 1 is 3. Thus, the longest chain is formed by successive multiplication by 3: $o, 3o, 3^2o, \dots, 3^{L-1}o \le 1999$. This implies $L(o) - 1 = \lfloor \log_3(1999/o) \rfloor$.
16: 
17: Based on the condition $k_{o_1} > k_{o_2} > \dots > k_{o_L} \ge 0$ for any chain $o_1 \mid o_2 \mid \dots \mid o_L$, it follows that $k_{o_1} \ge L(o)-1$.
18: Thus, for any element $a_o = 2^{k_o} \cdot o$ in $A$, we have $a_o \ge 2^{L(o)-1} \cdot o$.
19: The smallest element of the set is $m_A = \min_{o \in O} a_o$. To minimize $m_A$, we seek to minimize the bound $f(o) = 2^{L(o)-1} \cdot o$ over all $o \in O$.
20: 
21: Let $k = L(o)-1 = \lfloor \log_3(1999/o) \rfloor$. Then $k$ is an integer such that $3^k \le 1999/o < 3^{k+1}$, which implies $o > 1999/3^{k+1}$. For a fixed $k$, $f(o) = 2^k \cdot o$ is minimized when $o$ is the smallest odd integer greater than $1999/3^{k+1}$.
22: - If $k=6$, then $o > 1999/2187 \approx 0.91$, so $o \ge 1$. $f(o) \ge 2^6 \cdot 1 = 64$.
23: - If $k=5$, then $o > 1999/729 \approx 2.74$, so $o \ge 3$. $f(o) \ge 2^5 \cdot 3 = 96$.
24: - If $k=4$, then $o > 1999/243 \approx 8.22$, so $o \ge 9$. $f(o) \ge 2^4 \cdot 9 = 144$.
25: - If $k=3$, then $o > 1999/81 \approx 24.67$, so $o \ge 25$. $f(o) \ge 2^3 \cdot 25 = 200$.
26: - If $k=2$, then $o > 1999/27 \approx 74.03$, so $o \ge 75$. $f(o) \ge 2^2 \cdot 75 = 300$.
27: - If $k=1$, then $o > 1999/9 \approx 222.11$, so $o \ge 223$. $f(o) \ge 2^1 \cdot 223 = 446$.
28: - If $k=0$, then $o > 1999/3 \approx 666.33$, so $o \ge 667$. $f(o) \ge 2^0 \cdot 667 = 667$.
29: 
30: In all cases, $a_o \ge f(o) \ge 64$. Thus, $m_A \ge 64$ for any valid set $A$.
31: 
32: ### 4. Construction for $m_A = 64$
33: We can achieve $m_A = 64$ by setting $k_o = L(o) - 1$ for all $o \in O$. If $o_1 \mid o_2$ and $o_1 \neq o_2$, then $o_2 \ge 3o_1$, so $L(o_2) = \lfloor \log_3(1999/o_2) \rfloor + 1 \le \lfloor \log_3(1999/3o_1) \rfloor + 1 = L(o_1) - 1$. Thus $k_{o_2} \le k_{o_1} - 1$, ensuring $k_{o_1} > k_{o_2}$, which makes $A$ an antichain.
34: 
35: To ensure $A \subset \{1, \dots, 2000\}$, we verify that $a_o = 2^{L(o)-1} \cdot o \le 2000$. Let $k = L(o)-1$. By definition, $3^k \le 1999/o$. Then:
36: $$a_o = 2^k \cdot o \le 2^k \cdot \frac{1999}{3^k} = 1999 \cdot \left(\frac{2}{3}\right)^k \le 1999 \le 2000$$
37: The minimum element is $a_1 = 2^{L(1)-1} \cdot 1 = 2^6 \cdot 1 = 64$.
38: 
39: The minimum possible value of $m_A$ is 64.
