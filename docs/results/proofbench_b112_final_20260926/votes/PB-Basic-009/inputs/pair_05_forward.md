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
