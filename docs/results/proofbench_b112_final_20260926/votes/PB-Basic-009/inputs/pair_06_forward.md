# Problem

Let $a_1,a_2,...,a_{18}$ be 18 real numbers, not necessarily distinct, with average $m$. Let $A$ denote the number of triples $1 \le i < j < k \le 18$ for which $a_i + a_j + a_k \ge 3m$. What is the minimum possible value of $A$?

# Proof A

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

# Proof B

1: Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. Let $x_i = a_i - m$ for $i = 1, \dots, 18$. Then $\sum_{i=1}^{18} x_i = 0$, and the condition $a_i + a_j + a_k \ge 3m$ is equivalent to $x_i + x_j + x_k \ge 0$. Let $A$ be the number of such triples $1 \le i < j < k \le 18$.
2: 
3: First, we show that $A = 136$ is achievable. Let $x_1 = x_2 = \dots = x_{17} = -1$ and $x_{18} = 17$. The sum of any triple not containing $x_{18}$ is $-3 < 0$. The sum of any triple containing $x_{18}$ is $x_i + x_j + 17 = -1 - 1 + 17 = 15 \ge 0$ for $1 \le i < j \le 17$. There are $\binom{17}{2} = \frac{17 \times 16}{2} = 136$ such triples. Thus, $A = 136$ is possible.
4: 
5: To prove that $A \ge 136$ for any set of $x_i$ summing to 0, we consider the number of "bad" triples $B$, which are those with $x_i + x_j + x_k < 0$. Since there are $\binom{18}{3} = 816$ total triples, $A = 816 - B$. We aim to show that $B \le 680$.
6: 
7: Let $x_1 \le x_2 \le \dots \le x_{18}$. Let $k$ be the number of negative $x_i$. If $k=0$, then all $x_i = 0$ and $B=0$. If $k > 0$, let $y_i = -x_i > 0$ for $i=1, \dots, k$ and $z_j = x_j \ge 0$ for $j=k+1, \dots, 18$. The condition $\sum x_i = 0$ implies $\sum_{i=1}^k y_i = \sum_{j=k+1}^{18} z_j = S$.
8: 
9: A triple is bad if its sum is negative. The possible bad triples are:
10: 1. Three negative numbers: $\binom{k}{3}$ triples.
11: 2. Two negative numbers $y_i, y_j$ and one non-negative number $z_l$ such that $y_i + y_j > z_l$.
12: 3. One negative number $y_i$ and two non-negative numbers $z_j, z_l$ such that $y_i > z_j + z_l$.
13: 
14: To maximize $B$, we should make the non-negative values $z_l$ as small as possible. For a fixed $k$, $B$ is maximized when $z_{k+1} = z_{k+2} = \dots = z_{17} = 0$ and $z_{18} = S$. In this configuration:
15: - The $\binom{k}{3}$ triples of negative numbers are all bad.
16: - For $l \in \{k+1, \dots, 17\}$, $z_l = 0$, so all $\binom{k}{2} \times (17-k)$ triples $(i, j, l)$ are bad.
17: - For $l = 18$, $z_{18} = S$, so $y_i + y_j > S$ is impossible since $y_i + y_j \le S$.
18: - For $i \in \{1, \dots, k\}$ and $j, l \in \{k+1, \dots, 17\}$, $z_j + z_l = 0$, so all $k \times \binom{17-k}{2}$ triples $(i, j, l)$ are bad.
19: - For $i \in \{1, \dots, k\}$ and $j \in \{k+1, \dots, 17\}, l=18$, $z_j + z_{18} = S$, so $y_i > S$ is impossible.
20: 
21: Thus, for a fixed $k$, the maximum $B$ is:
22: $B(k) = \binom{k}{3} + \binom{k}{2}(17-k) + k\binom{17-k}{2}$
23: $B(k) = \frac{k(k-1)(k-2)}{6} + \frac{k(k-1)(17-k)}{2} + \frac{k(17-k)(16-k)}{2}$
24: $B(k) = \frac{k}{6} [ (k^2-3k+2) + 3(18k-k^2-17) + 3(k^2-33k+272) ]$
25: $B(k) = \frac{k}{6} [ k^2-3k+2 + 54k-3k^2-51 + 3k^2-99k+816 ]$
26: $B(k) = \frac{k}{6} [ k^2 - 48k + 767 ]$
27: 
28: Evaluating $B(k)$ for $k \in \{1, \dots, 17\}$:
29: - For $k=17$, $B(17) = \frac{17}{6}(289 - 816 + 767) = \frac{17}{6}(240) = 680$.
30: - For $k=16$, $B(16) = \frac{16}{6}(256 - 768 + 767) = \frac{16}{6}(255) = 680$.
31: - For $k=15$, $B(15) = \frac{15}{6}(225 - 720 + 767) = \frac{15}{6}(272) = 680$.
32: - For $k=14$, $B(14) = \frac{14}{6}(196 - 672 + 767) = \frac{14}{6}(291) = 679$.
33: As $k$ decreases further, $B(k)$ continues to decrease. The maximum value of $B$ is 680. Therefore, $A = 816 - B \ge 816 - 680 = 136$.
34: 
35: The minimum possible value of $A$ is 136.
