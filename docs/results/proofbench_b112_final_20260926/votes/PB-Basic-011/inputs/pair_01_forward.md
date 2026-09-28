# Problem

Let $A\subset \{1,2,\ldots,2000\}$, $|A|=1000$, such that $a$ does not divide $b$ for all distinct elements $a,b\in A$. For a set $X$ as above let us denote with $m_{X}$ the smallest element in $X$. Find $\min m_{A}$ (for all $A$ with the above properties).

# Proof A

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

# Proof B

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
