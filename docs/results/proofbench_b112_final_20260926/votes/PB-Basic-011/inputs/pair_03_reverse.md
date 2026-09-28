# Problem

Let $A\subset \{1,2,\ldots,2000\}$, $|A|=1000$, such that $a$ does not divide $b$ for all distinct elements $a,b\in A$. For a set $X$ as above let us denote with $m_{X}$ the smallest element in $X$. Find $\min m_{A}$ (for all $A$ with the above properties).

# Proof A

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
