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
