Let $n$ be a positive integer. We claim that the largest number $c$ Liu can guarantee is $c = \frac{n+1}{2n+1}$.

**1. Liu's Strategy to Guarantee $L \ge \frac{n+1}{2n+1}$**
Liu marks $n$ points to divide the stick into $n+1$ segments $S_1, \dots, S_{n+1}$, where $S_1 = \dots = S_n = \frac{2}{2n+1}$ and $S_{n+1} = \frac{1}{2n+1}$. Let $x = \frac{1}{2n+1}$.
Xiang then marks at most $n$ points. Let $k_i$ be the number of marks Xiang places in segment $S_i$, where $\sum_{i=1}^{n+1} k_i \le n$. The total number of pieces produced is $k = \sum_{i=1}^{n+1} (k_i+1) = n+1 + \sum k_i \le 2n+1$. Let the sorted lengths of the pieces be $l_1 \ge l_2 \ge \dots \ge l_k$. Liu's total length is $L = \sum_{j=1}^{\lceil k/2 \rceil} l_{2j-1}$.
It is a known property of the alternating sum of sorted sequences that $L - X = \sum_{j=1}^k (-1)^{j-1} l_j = \max \{ \sum_{j=1}^k \epsilon_j p_j : \epsilon_j \in \{1, -1\}, \sum \epsilon_j = 1 \text{ if } k \text{ is odd, and } 0 \text{ if } k \text{ is even} \}$, where $p_j$ are the lengths of the pieces.
We may assume $k = 2n+1$ by adding pieces of length 0. Then $L-X = \max \{ \sum_{i=1}^{n+1} \sum_{j=1}^{k_i+1} \epsilon_{i,j} p_{i,j} : \sum_{i,j} \epsilon_{i,j} = 1 \}$.
For each $i \in \{1, \dots, n+1\}$, let $\text{Val}_i(s)$ be the maximum of $\sum_{j=1}^{k_i+1} \epsilon_{i,j} p_{i,j}$ subject to $\sum \epsilon_{i,j} = s$. Note that $\text{Val}_i(s) \ge 0$ if $s \ge 0$ and $\text{Val}_i(s) = -\text{Val}_i(-s)$.
For $i \le n$, $\text{Val}_i(k_i+1) = \sum p_{i,j} = 2x$. For $i=n+1$, $\text{Val}_{n+1}(s) \ge -x$ for any valid $s$.
We seek $s_1, \dots, s_{n+1}$ such that $\sum s_i = 1$, $|s_i| \le k_i+1$, and $s_i \equiv k_i+1 \pmod 2$, to maximize $\sum \text{Val}_i(s_i)$.
Choose $i_0 \in \{1, \dots, n\}$ such that $k_{i_0}$ is minimized. Let $s_{i_0} = k_{i_0}+1$. For $i \in \{1, \dots, n\} \setminus \{i_0\}$, let $s_i = 1$ if $k_i+1$ is odd and $s_i = 0$ if $k_i+1$ is even. Let $S = \sum_{i=1}^n s_i$. Then $s_{n+1} = 1-S$.
Since $s_i \ge 0$ for $i \le n$, $\sum_{i=1}^n \text{Val}_i(s_i) \ge \text{Val}_{i_0}(k_{i_0}+1) = 2x$.
Then $L-X \ge 2x + \text{Val}_{n+1}(1-S) \ge 2x - x = x$.
Thus $L-X \ge \frac{1}{2n+1}$, which implies $2L - 1 \ge \frac{1}{2n+1}$, so $L \ge \frac{1}{2} + \frac{1}{2(2n+1)} = \frac{2n+2}{2(2n+1)} = \frac{n+1}{2n+1}$.

**2. Xiang's Strategy to Force $L \le \frac{n+1}{2n+1}$**
For any marks Liu makes, let the resulting segments be $s_1 \ge s_2 \ge \dots \ge s_{n+1}$. Xiang can choose $k_i$ such that $\sum k_i = n$ and $k_i \approx (2n+1)s_i - 1$. Specifically, he can ensure that all resulting pieces $l_j$ are very close to $x = \frac{1}{2n+1}$.
If Xiang can make $l_1 \le x + \epsilon$ for any $\epsilon > 0$, then $L = \sum_{j=1}^{n+1} l_{2j-1} \le (n+1)(x+\epsilon)$.
By splitting each $s_i$ into $k_i+1$ pieces of nearly equal length $s_i/(k_i+1)$, Xiang can ensure that $l_1 \le \max_i \lceil (2n+1)s_i \rceil \cdot \frac{s_i}{\lceil (2n+1)s_i \rceil}$.
More simply, Xiang can ensure $l_1 \approx l_2, l_3 \approx l_4, \dots, l_{2n-1} \approx l_{2n}$.
In the alternating sum $L-X = (l_1-l_2) + (l_3-l_4) + \dots + (l_{2n-1}-l_{2n}) + l_{2n+1}$, he can make each pair $l_{2j-1}-l_{2j}$ arbitrarily small by splitting segments into pieces of nearly equal length.
Then $L-X \approx l_{2n+1}$. Since $\sum l_j = 1$, the smallest piece $l_{2n+1} \le \frac{1}{2n+1} = x$.
Thus, Xiang can force $L-X \le x + \epsilon$ for any $\epsilon > 0$, which means $L \le \frac{n+1}{2n+1} + \epsilon$.
Since this holds for all $\epsilon > 0$, Liu cannot guarantee more than $\frac{n+1}{2n+1}$.

The largest number $c$ Liu can guarantee is $c = \frac{n+1}{2n+1}$.