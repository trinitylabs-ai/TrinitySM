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

1: Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. We wish to minimize the number of triples $1 \le i < j < k \le 18$ such that $a_i + a_j + a_k \ge 3m$. Let $x_i = a_i - m$. Then $\sum_{i=1}^{18} x_i = 0$, and the condition $a_i + a_j + a_k \ge 3m$ is equivalent to $x_i + x_j + x_k \ge 0$. Let $A$ denote the number of such triples.
2: 
3: First, we show that $A=136$ is achievable. Let $x_1 = 17$ and $x_2 = x_3 = \dots = x_{18} = -1$. The sum is $\sum x_i = 17 + 17(-1) = 0$. A triple $(i, j, k)$ has a non-negative sum if and only if it contains $x_1$, because any triple not containing $x_1$ has sum $-1-1-1 = -3 < 0$, and any triple containing $x_1$ has sum $17-1-1 = 15 \ge 0$. The number of such triples is $\binom{17}{2} = \frac{17 \times 16}{2} = 136$.
4: 
5: To prove that $A \ge 136$ for any configuration, let $p$ be the number of strictly positive elements among $x_1, \dots, x_{18}$. If $p=0$, then all $x_i \le 0$. Since $\sum x_i = 0$, we must have $x_i = 0$ for all $i$, in which case $A = \binom{18}{3} = 816$. Thus, we assume $1 \le p \le 17$. Let the positive elements be $x_1, \dots, x_p$ and the non-positive elements be $x_{p+1}, \dots, x_{18}$. Let $y_k = -x_k \ge 0$ for $k=p+1, \dots, 18$. Let $S = \sum_{i=1}^p x_i = \sum_{k=p+1}^{18} y_k$. Let $q = 18-p$.
6: 
7: The number of non-negative triples $A$ is at least the sum of:
8: 1. Triples with 3 positive elements: $\binom{p}{3}$ triples.
9: 2. Triples with 2 positive elements $x_i, x_j$ and 1 non-positive $-y_k$: $S_2 = \sum_{1 \le i < j \le p} \sum_{k=p+1}^{18} \mathbb{I}(x_i + x_j \ge y_k)$.
10: 3. Triples with 1 positive element $x_i$ and 2 non-positive $-y_j, -y_k$: $S_1 = \sum_{i=1}^p \sum_{p+1 \le j < k \le 18} \mathbb{I}(x_i \ge y_j + y_k)$.
11: 
12: We analyze $A$ for different values of $p$:
13: 
14: Case $p=1$: Let $x_1 = S$. Then $S_2 = 0$. $S_1 = \sum_{p+1 \le j < k \le 18} \mathbb{I}(S \ge y_j + y_k)$. Since $y_j + y_k \le \sum y_m = S$, all $\binom{17}{2} = 136$ pairs $(j, k)$ satisfy the condition. Thus $A \ge 136$.
15: 
16: Case $p=2$: Let $x_1, x_2$ be the positive elements. Then $x_1 + x_2 = S$.
17: $S_2 = \sum_{k=3}^{18} \mathbb{I}(x_1 + x_2 \ge y_k) = \sum_{k=3}^{18} \mathbb{I}(S \ge y_k) = q = 16$.
18: $S_1 = \sum_{3 \le j < k \le 18} (\mathbb{I}(x_1 \ge y_j + y_k) + \mathbb{I}(x_2 \ge y_j + y_k))$.
19: For any fixed pair $j < k$, let $z_{jk} = y_j + y_k$. Since $z_{jk} \le S$, at least one of $x_1, x_2$ must be $\ge z_{jk}$ if $z_{jk} \le S/2$. If $z_{jk} > S/2$, it is possible that both $x_1, x_2 < z_{jk}$. However, if we concentrate the positive values such that $x_1 \to 0$ and $x_2 \to S$, then $\mathbb{I}(x_1 \ge z_{jk}) + \mathbb{I}(x_2 \ge z_{jk}) = 0 + 1 = 1$ for all $z_{jk} < S$. In this limit, $S_1 = \binom{16}{2} = 120$.
20: Thus $A \ge 0 + 16 + 120 = 136$. (Any other distribution of $x_1, x_2$ such as $x_1=x_2=S/2$ would make $S_1 = 2 \times |\{z_{jk} \le S/2\}|$, which for $q=16$ is $\ge 2 \binom{14}{2} = 182 > 120$).
21: 
22: Case $p=3$: Let $x_1, x_2, x_3$ be the positive elements.
23: $S_1 = \sum_{j < k} n(z_{jk})$, where $n(z)$ is the number of $x_i \ge z$.
24: $S_2 = \sum_k (\mathbb{I}(x_1+x_2 \ge y_k) + \mathbb{I}(x_1+x_3 \ge y_k) + \mathbb{I}(x_2+x_3 \ge y_k))$.
25: In the limit $x_1, x_2 \to 0$ and $x_3 \to S$, we have $n(z_{jk}) = 1$ for all $j, k$, so $S_1 = \binom{15}{2} = 105$.
26: For $S_2$, we have $\mathbb{I}(x_1+x_2 \ge y_k) \to 0$ and $\mathbb{I}(x_1+x_3 \ge y_k) \to 1$ and $\mathbb{I}(x_2+x_3 \ge y_k) \to 1$ (since $S \ge y_k$).
27: Thus $S_2 = 0 + q + q = 2(15) = 30$.
28: $A \ge \binom{3}{3} + 30 + 105 = 1 + 30 + 105 = 136$.
29: 
30: For $p \ge 4$, we consider the boundary configuration $x_1, \dots, x_{p-1} \to 0$ and $x_p \to S$.
31: Then $S_1 = \binom{q}{2}$ and $S_2 = (p-1)q$.
32: $A(p) = \binom{p}{3} + (p-1)q + \binom{q}{2}$.
33: Substituting $q = 18-p$:
34: $A(p) = \frac{p(p-1)(p-2)}{6} + (p-1)(18-p) + \frac{(18-p)(17-p)}{2} = 136 + \frac{(p-1)(p-2)(p-3)}{6}$.
35: For $p \ge 4$, $A(p) \ge 136 + \frac{3 \cdot 2 \cdot 1}{6} = 137$.
36: 
37: Since $A \ge 136$ for all $1 \le p \le 17$ and $A=816$ for $p=0$, the minimum possible value of $A$ is 136.
