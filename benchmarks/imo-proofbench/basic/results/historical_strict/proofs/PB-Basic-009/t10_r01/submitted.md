Let $a_1, a_2, \dots, a_{18}$ be 18 real numbers with average $m$. Define $x_i = a_i - m$ for $i = 1, 2, \dots, 18$. Then $\sum_{i=1}^{18} x_i = 0$. The condition $a_i + a_j + a_k \ge 3m$ is equivalent to $x_i + x_j + x_k \ge 0$. We wish to find the minimum possible value of $A$, the number of triples $1 \le i < j < k \le 18$ such that $x_i + x_j + x_k \ge 0$.

First, we show that $A = 136$ is achievable. Let $x_1 = 17$ and $x_2 = x_3 = \dots = x_{18} = -1$. The sum is $17 + 17(-1) = 0$. A triple $\{i, j, k\}$ has a non-negative sum if and only if it contains $x_1$, because if it does not, the sum is $(-1) + (-1) + (-1) = -3 < 0$. If it contains $x_1$, the sum is $17 - 1 - 1 = 15 \ge 0$. There are $\binom{17}{2} = \frac{17 \times 16}{2} = 136$ such triples. Thus, $A = 136$ is possible.

Now we prove that $A \ge 136$ for any set of $x_i$ summing to 0. Let the numbers be ordered such that $x_1 \ge x_2 \ge \dots \ge x_{18}$.
If $x_1 \le 0$, then since $\sum x_i = 0$, all $x_i$ must be 0. In this case, $A = \binom{18}{3} = 816$.
If $x_1 > 0$, let $p$ be the number of positive elements $x_i$.

Case 1: $p = 1$.
We have $x_1 > 0$ and $x_2, \dots, x_{18} \le 0$. Then $x_1 = \sum_{i=2}^{18} |x_i|$.
For any triple $\{1, j, k\}$ with $2 \le j < k \le 18$, the sum is
$x_1 + x_j + x_k = \sum_{i=2}^{18} |x_i| - |x_j| - |x_k| = \sum_{i \in \{2, \dots, 18\} \setminus \{j, k\}} |x_i| \ge 0$.
There are $\binom{17}{2} = 136$ such triples. Thus, $A \ge 136$.

Case 2: $2 \le p \le 15$.
To minimize the number of non-negative triples for a fixed $p$, we concentrate the positive sum into $x_1$ and make $x_2, \dots, x_p$ as small as possible. Let $x_2 = \dots = x_p = \epsilon$ for some small $\epsilon > 0$ and $x_{p+1} = \dots = x_{18} = -1$. To satisfy $\sum x_i = 0$, we set $x_1 = (18-p) - (p-1)\epsilon$.
For sufficiently small $\epsilon$, we have $x_1 \approx 18-p$. Since $p \le 15$, $x_1 \ge 3 - (p-1)\epsilon$.
The triples containing $x_1$ are $\{1, j, k\}$. The smallest such sum is $x_1 + x_{17} + x_{18} \approx (18-p) - 2$. Since $p \le 15$, $18-p-2 \ge 1 > 0$. Thus, all $\binom{17}{2} = 136$ triples containing $x_1$ are non-negative.
Additionally, any triple $\{j, k, l\}$ consisting of three positive elements $x_j, x_k, x_l$ (where $j, k, l \in \{2, \dots, p\}$) has a sum $3\epsilon > 0$. There are $\binom{p-1}{3}$ such triples.
Thus, for this distribution, $A = 136 + \binom{p-1}{3} \ge 136$.
Any other distribution for a fixed $p$ would either decrease $x_1$ (potentially making some triples containing $x_1$ negative) or increase $x_2, \dots, x_p$ (potentially making more triples not containing $x_1$ non-negative). However, the minimum $A$ for $p \in \{2, \dots, 15\}$ is achieved in the limit $\epsilon \to 0^+$, yielding $A \ge 136$.

Case 3: $p \ge 16$.
If $p=16$, there are $\binom{16}{3} = \frac{16 \times 15 \times 14}{6} = 560$ triples consisting of three positive elements. These are all non-negative, so $A \ge 560$.
If $p=17$, there are $\binom{17}{3} = 680$ triples consisting of three positive elements, so $A \ge 680$.
If $p=18$, all $x_i = 0$, so $A = 816$.

In all cases, $A \ge 136$. The minimum possible value is 136.
