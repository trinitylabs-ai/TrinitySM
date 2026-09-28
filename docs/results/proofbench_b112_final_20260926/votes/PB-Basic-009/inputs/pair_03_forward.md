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
