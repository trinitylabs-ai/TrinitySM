# Problem

Let $a_1,a_2,...,a_{18}$ be 18 real numbers, not necessarily distinct, with average $m$. Let $A$ denote the number of triples $1 \le i < j < k \le 18$ for which $a_i + a_j + a_k \ge 3m$. What is the minimum possible value of $A$?

# Proof A

1: Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. Let $x_i = a_i - m$ for $i=1, \dots, 18$. The condition that the average of $a_i$ is $m$ implies that $\sum_{i=1}^{18} x_i = 0$. The condition $a_i + a_j + a_k \ge 3m$ is equivalent to $x_i + x_j + x_k \ge 0$. We wish to minimize the number of such triples $A$.
2: 
3: First, we show that $A=136$ is possible. Let $x_1 = x_2 = \dots = x_{17} = -1$ and $x_{18} = 17$. The sum is $\sum x_i = 17(-1) + 17 = 0$. A triple $(i, j, k)$ has $x_i + x_j + x_k \ge 0$ if and only if it contains $x_{18}$, because if it does not, the sum is $-1-1-1 = -3 < 0$. If it contains $x_{18}$, the sum is $17-1-1 = 15 \ge 0$. The number of such triples is $\binom{17}{2} = \frac{17 \cdot 16}{2} = 136$. Thus, the minimum possible value of $A$ is at most 136.
4: 
5: Next, we prove that $A \ge 136$ for any set of $x_i$ with $\sum x_i = 0$. Let $k$ be the number of positive elements among $x_1, \dots, x_{18}$.
6: If $k=0$, then all $x_i \le 0$. Since $\sum x_i = 0$, we must have $x_i = 0$ for all $i$. Then every triple has sum $0 \ge 0$, so $A = \binom{18}{3} = 816 \ge 136$.
7: If $k=1$, let $x_{18} = S > 0$ be the only positive element, and $x_1, \dots, x_{17} \le 0$. Then $S = \sum_{i=1}^{17} |x_i|$. For any $1 \le i < j \le 17$, the triple $\{x_i, x_j, x_{18}\}$ has sum $S - |x_i| - |x_j| = \sum_{m \in \{1, \dots, 17\} \setminus \{i,j\}} |x_m| \ge 0$. There are $\binom{17}{2} = 136$ such triples, so $A \ge 136$.
8: 
9: If $k \ge 2$, let the positive elements be $p_1, \dots, p_k$ and the non-positive elements be $n_1, \dots, n_{18-k}$. Let $S = \sum p_i = \sum |n_j|$.
10: To find a lower bound for $A$ for a fixed $k$, we consider the configuration where $k-1$ of the positive elements are very small ($\epsilon \to 0^+$) and the non-positive elements are equal. Let $p_1 = S - (k-1)\epsilon$ and $p_2 = \dots = p_k = \epsilon$, and $n_1 = \dots = n_{18-k} = -S/(18-k)$.
11: In this limiting configuration, the triples with sum $\ge 0$ are:
12: 1. Triples with three positive elements: $\binom{k}{3}$ triples.
13: 2. Triples with two positive elements: A triple $\{p_i, p_j, n_l\}$ has sum $\ge 0$ if it contains $p_1$, since $p_1 + p_j + n_l \approx S + 0 - S/(18-k) > 0$. If it does not contain $p_1$, the sum is $\approx 0 + 0 - S/(18-k) < 0$. There are $(k-1)(18-k)$ such triples.
14: 3. Triples with one positive element: A triple $\{p_i, n_j, n_l\}$ has sum $\ge 0$ if it contains $p_1$ and $S - 2S/(18-k) \ge 0$, which is true if $18-k \ge 2$. If it contains $p_i$ for $i \ge 2$, the sum is $\approx 0 - 2S/(18-k) < 0$. There are $\binom{18-k}{2}$ such triples.
15: 4. Triples with zero positive elements: These have sum $\approx -3S/(18-k) < 0$.
16: 
17: For $k \le 16$, the number of non-negative triples in this configuration is $A(k) = \binom{k}{3} + (k-1)(18-k) + \binom{18-k}{2}$.
18: Evaluating $A(k)$ for small $k$:
19: - $A(2) = 0 + 1(16) + \binom{16}{2} = 16 + 120 = 136$.
20: - $A(3) = 1 + 2(15) + \binom{15}{2} = 1 + 30 + 105 = 136$.
21: - $A(4) = 4 + 3(14) + \binom{14}{2} = 4 + 42 + 91 = 137$.
22: The function $f(k) = \frac{1}{6}k^3 - k^2 + \frac{11}{6}k + 135$ represents $A(k)$, and its derivative $f'(k) = \frac{1}{2}k^2 - 2k + \frac{11}{6}$ is positive for $k \ge 3$. Thus $A(k)$ is non-decreasing for $k \ge 3$. For $k > 16$, $A(k) \ge \binom{k}{3} \ge \binom{17}{3} = 680$.
23: In all cases, $A \ge 136$.
24: 
25: The minimum possible value of $A$ is 136.

# Proof B

1: Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. Define $x_i = a_i - m$ for $i=1, \dots, 18$. Then $\sum_{i=1}^{18} x_i = 0$, and the condition $a_i + a_j + a_k \ge 3m$ is equivalent to $x_i + x_j + x_k \ge 0$. We wish to find the minimum possible value of $A$, the number of triples $1 \le i < j < k \le 18$ such that $x_i + x_j + x_k \ge 0$.
2: 
3: Assume without loss of generality that $x_1 \ge x_2 \ge \dots \ge x_{18}$. Let $p$ be the number of positive values among $x_1, \dots, x_{18}$. If $p=0$, then all $x_i \le 0$, and since their sum is 0, all $x_i = 0$, which gives $A = \binom{18}{3} = 816$. Thus, we assume $p \ge 1$. Let $q = 18-p$ be the number of non-positive values.
4: 
5: If $p=1$, then $x_1 > 0$ and $x_2, \dots, x_{18} \le 0$. Any triple not containing $x_1$ consists of three non-positive numbers, so $x_i + x_j + x_k \le 0$. For triples containing $x_1$, we have
6: \[ x_1 + x_j + x_k = \sum_{m=1}^{18} x_m - \sum_{m \neq 1, j, k} x_m = 0 - \sum_{m \neq 1, j, k} x_m. \]
7: Since all $x_m \le 0$ for $m \ge 2$, the sum $\sum_{m \neq 1, j, k} x_m$ is non-positive, meaning $x_1 + x_j + x_k \ge 0$ for all $2 \le j < k \le 18$. There are $\binom{17}{2} = 136$ such triples. By setting $x_1 = 17$ and $x_2 = \dots = x_{18} = -1$, we have $x_1 + x_j + x_k = 15 > 0$ and $x_i + x_j + x_k = -3 < 0$ for $i \ge 2$, yielding $A = 136$.
8: 
9: Now consider $p \ge 2$. Let $S = \sum_{i=1}^p x_i = -\sum_{j=p+1}^{18} x_j$. We decompose $A$ into $A = A_3 + A_2 + A_1 + A_0$, where $A_m$ is the number of triples containing exactly $m$ positive elements.
10: 1. $A_3 = \binom{p}{3}$ because any triple of positive numbers has a positive sum.
11: 2. $A_0$ is the number of triples of non-positive numbers. To minimize $A$, we can set $x_{p+1}, \dots, x_{18} < 0$ such that $x_i + x_j + x_k < 0$ for all $i, j, k > p$, so $A_0 = 0$.
12: 3. For $A_1$, let $f(x) = \sum_{p < j < k \le 18} \mathbb{I}(x + x_j + x_k \ge 0)$. Then $A_1 = \sum_{i=1}^p f(x_i)$.
13: 4. For $A_2$, let $g(x, y) = \sum_{k=p+1}^{18} \mathbb{I}(x + y + x_k \ge 0)$. Then $A_2 = \sum_{1 \le i < j \le p} g(x_i, x_j)$.
14: 
15: For a fixed set of non-positive values $x_{p+1}, \dots, x_{18}$, we want to minimize $A_1 + A_2$ subject to $\sum_{i=1}^p x_i = S$ and $x_i > 0$. The function $f(x)$ is a non-decreasing step function. For any $c \ge 0$, the sum $\mathbb{I}(x \ge c) + \mathbb{I}(S-x \ge c)$ is minimized when $x$ is at the boundary (near $0$ or $S$) provided $c$ is not in the range $(S/2, S)$. Since $\sum_{p < j < k \le 18} (-x_j - x_k) = (q-1)S$, the average value of the thresholds $c_{jk} = -x_j - x_k$ is $\frac{2S}{q}$, which is much smaller than $S/2$ for $q \ge 6$. Consequently, the sum $A_1 + A_2$ is minimized when the positive mass is concentrated on a single element, i.e., as $x_2, \dots, x_p \to 0^+$ and $x_1 \to S$.
16: 
17: In this limit:
18: - $A_1 = f(S) + (p-1)f(0) = \binom{q}{2} + 0 = \binom{q}{2}$, since $S + x_j + x_k = -\sum_{m \neq j, k, m > p} x_m \ge 0$.
19: - $A_2 = \sum_{j=2}^p g(S, 0) + \sum_{2 \le i < j \le p} g(0, 0) = (p-1)q + 0 = (p-1)q$, since $S + 0 + x_k = -\sum_{m \neq k, m > p} x_m \ge 0$.
20: - $A_3 = \binom{p}{3}$.
21: 
22: Thus, for a fixed $p$, the minimum value of $A$ is $h(p) = \binom{p}{3} + (p-1)(18-p) + \binom{18-p}{2}$.
23: Calculating $h(p)$ for small $p$:
24: - $h(1) = 0 + 0 + \binom{17}{2} = 136$.
25: - $h(2) = 0 + 1(16) + \binom{16}{2} = 16 + 120 = 136$.
26: - $h(3) = 1 + 2(15) + \binom{15}{2} = 1 + 30 + 105 = 136$.
27: - $h(4) = 4 + 3(14) + \binom{14}{2} = 4 + 42 + 91 = 137$.
28: 
29: The function $h(p) = \frac{p^3 - 6p^2 + 11p + 810}{6}$ is strictly increasing for $p \ge 3$. Comparing all cases, the minimum possible value of $A$ is 136.
