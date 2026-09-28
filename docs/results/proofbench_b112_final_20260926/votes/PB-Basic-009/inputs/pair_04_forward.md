# Problem

Let $a_1,a_2,...,a_{18}$ be 18 real numbers, not necessarily distinct, with average $m$. Let $A$ denote the number of triples $1 \le i < j < k \le 18$ for which $a_i + a_j + a_k \ge 3m$. What is the minimum possible value of $A$?

# Proof A

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
