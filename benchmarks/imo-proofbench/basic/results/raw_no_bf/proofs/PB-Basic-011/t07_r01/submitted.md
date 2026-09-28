To find the minimum possible value of $m_A = \min A$ for a set $A \subset \{1, 2, \ldots, 2000\}$ with $|A| = 1000$ such that no element in $A$ divides another, we proceed as follows:

1.  **Odd Part Decomposition:**
    Every integer $n \in \{1, 2, \ldots, 2000\}$ can be uniquely written as $n = 2^k \cdot o$, where $k \ge 0$ and $o$ is an odd integer. The possible odd parts $o$ are $\{1, 3, 5, \ldots, 1999\}$. There are exactly 1000 such odd parts.
    Since $|A| = 1000$ and no element in $A$ divides another, each element $a \in A$ must have a distinct odd part. If two elements $a, b \in A$ had the same odd part $o$, say $a = 2^{k_1} o$ and $b = 2^{k_2} o$ with $k_1 < k_2$, then $a$ would divide $b$, violating the condition.
    Thus, for each $o \in \{1, 3, \ldots, 1999\}$, there is exactly one $k_o \ge 0$ such that $a_o = 2^{k_o} \cdot o \in A$.

2.  **The Antichain Condition:**
    The condition that no $a \in A$ divides another $b \in A$ means that if $o_1$ and $o_2$ are odd parts and $o_1$ divides $o_2$, then $2^{k_{o_1}} o_1$ must not divide $2^{k_{o_2}} o_2$.
    If $o_1 | o_2$, then $o_2 = m \cdot o_1$ for some odd integer $m \ge 1$.
    $a_{o_1} \mid a_{o_2} \iff 2^{k_{o_1}} o_1 \mid 2^{k_{o_2}} m o_1 \iff 2^{k_{o_1}} \mid 2^{k_{o_2}} m$.
    Since $m$ is odd, this happens if and only if $k_{o_1} \le k_{o_2}$.
    Therefore, for $a_{o_1} \nmid a_{o_2}$ to hold for all $o_1 | o_2$ (with $o_1 \neq o_2$), we must have $k_{o_1} > k_{o_2}$.

3.  **Lower Bound on $m_A$:**
    For any odd part $o$, let $L(o)$ be the length of the longest chain of odd numbers in $\{1, 3, \ldots, 1999\}$ starting with $o$. The longest such chain is $o, 3o, 3^2 o, \ldots, 3^n o$, where $n$ is the largest integer such that $3^n o \le 1999$. Thus, $L(o) = \lfloor \log_3(1999/o) \rfloor$.
    From the condition $k_{o_1} > k_{o_2}$ for $o_1 | o_2$, we have $k_o > k_{3o} > k_{3^2 o} > \ldots > k_{3^n o} \ge 0$.
    This implies $k_o \ge n = L(o)$.
    Consequently, $a_o = 2^{k_o} \cdot o \ge 2^{L(o)} \cdot o$.
    The smallest element in $A$ is $m_A = \min_{o} (2^{k_o} \cdot o) \ge \min_{o} (2^{L(o)} \cdot o)$.

4.  **Calculating the Minimum:**
    We evaluate $f(o) = 2^{L(o)} \cdot o$ for $o \in \{1, 3, \ldots, 1999\}$. Let $n = L(o)$.
    - For $n=6$: $3^6 \le 1999/o < 3^7 \implies 729 \le 1999/o < 2187 \implies o=1$. $f(1) = 2^6 \cdot 1 = 64$.
    - For $n=5$: $3^5 \le 1999/o < 3^6 \implies 243 \le 1999/o < 729 \implies o \in \{3, 5, 7\}$. Min $f(3) = 2^5 \cdot 3 = 96$.
    - For $n=4$: $3^4 \le 1999/o < 3^5 \implies 81 \le 1999/o < 243 \implies o \in \{9, \ldots, 23\}$. Min $f(9) = 2^4 \cdot 9 = 144$.
    - For $n=3$: $3^3 \le 1999/o < 3^4 \implies 27 \le 1999/o < 81 \implies o \in \{25, \ldots, 73\}$. Min $f(25) = 2^3 \cdot 25 = 200$.
    - For $n=2$: $3^2 \le 1999/o < 3^3 \implies 9 \le 1999/o < 27 \implies o \in \{75, \ldots, 221\}$. Min $f(75) = 2^2 \cdot 75 = 300$.
    - For $n=1$: $3^1 \le 1999/o < 3^2 \implies 3 \le 1999/o < 9 \implies o \in \{223, \ldots, 665\}$. Min $f(223) = 2^1 \cdot 223 = 446$.
    - For $n=0$: $1 \le 1999/o < 3 \implies o \in \{667, \ldots, 1999\}$. Min $f(667) = 2^0 \cdot 667 = 667$.
    The minimum value of $f(o)$ is 64.

5.  **Construction:**
    By setting $k_o = L(o)$, we satisfy $k_{o_1} > k_{o_2}$ whenever $o_1 | o_2$. We also check that $a_o = 2^{L(o)} \cdot o \le 2000$:
    $2^{L(o)} \cdot o \le 2^{\log_3(1999/o)} \cdot o = o \cdot (1999/o)^{\log_3 2} = o^{1 - \log_3 2} \cdot 1999^{\log_3 2}$.
    Since $1 - \log_3 2 > 0$, this is maximized when $o$ is largest ($o=1999$), giving $2^0 \cdot 1999 = 1999 \le 2000$.
    Thus, $A = \{2^{L(o)} \cdot o \mid o \in \{1, 3, \ldots, 1999\}\}$ is a valid set with $m_A = 64$.

The minimum value of $m_A$ is 64. \(\square\)
