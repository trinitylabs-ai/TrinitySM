To find the minimum possible value of $A$, the number of triples $1 \le i < j < k \le 18$ such that $a_i + a_j + a_k \ge 3m$, where $m$ is the average of $a_1, \dots, a_{18}$, we define $b_i = a_i - m$. The condition $a_i + a_j + a_k \ge 3m$ is equivalent to $b_i + b_j + b_k \ge 0$. We are given that the average of $a_i$ is $m$, so $\sum_{i=1}^{18} b_i = 0$.

Let $p$ be the number of positive $b_i$. If $p=0$, then all $b_i=0$, and $A = \binom{18}{3} = 816$.
Suppose $p \ge 1$. Let $b_1, \dots, b_{18-p}$ be the non-positive numbers and $b_{18-p+1}, \dots, b_{18}$ be the positive numbers. To minimize the number of triples with a non-negative sum, we can distribute the values such that one positive number is very large and the others are very small. Let $b_{18-p+1} = \dots = b_{17} = \epsilon$ for some small $\epsilon > 0$. Let $S = \sum_{i=1}^{18-p} |b_i|$. Then $b_{18} = S - (p-1)\epsilon$.

We analyze the triples $(i, j, k)$ with $b_i + b_j + b_k \ge 0$:
1.  **Triples including $b_{18}$**: The sum is $b_i + b_j + S - (p-1)\epsilon$.
    - If $18-p \ge 3$, let $b_1, \dots, b_{18-p} = -1$. Then $S = 18-p$. For any $i, j < 18$, $b_i + b_j \ge -2$. The sum is at least $(18-p) - 2 - (p-1)\epsilon = 16-p - (p-1)\epsilon$. This is positive for small $\epsilon$ if $p \le 15$. In this case, all $\binom{17}{2} = 136$ triples containing $b_{18}$ are non-negative.
2.  **Triples not including $b_{18}$**:
    - Triples consisting of three positive numbers: These are $\binom{p-1}{3}$ triples. Each sum is $3\epsilon > 0$.
    - Triples consisting of two positive numbers and one non-positive number: The sum is $2\epsilon + b_k \approx -1 < 0$ for small $\epsilon$.
    - Triples with one or zero positive numbers: These sums are $\le \epsilon - 2 < 0$.

For $p \le 15$, the total number of non-negative triples is $A = \binom{17}{2} + \binom{p-1}{3} = 136 + \binom{p-1}{3}$. This is minimized at $p=1, 2, 3$, giving $A = 136$.

We check other values of $p$:
- If $18-p = 2$ ($p=16$), then $b_1+b_2+b_{18} = -S + S - (p-1)\epsilon = -(p-1)\epsilon < 0$. Thus, only $\binom{17}{2} - 1 = 135$ triples containing $b_{18}$ are non-negative. However, we also have $\binom{15}{3}$ triples of positive numbers. $A = 135 + \binom{15}{3} = 135 + 455 = 590$.
- If $18-p = 1$ ($p=17$), then any triple containing $b_1$ has sum $b_1 + b_i + b_j = -S + b_i + b_j$. Since $b_i + b_j < S$ (as $S$ is the sum of all positive $b_k$), these are all negative. The non-negative triples are those not containing $b_1$, which is $\binom{17}{3} = 680$.

Comparing these cases, the minimum value is 136. An example reaching this is $b_1 = \dots = b_{17} = -1$ and $b_{18} = 17$, where only triples containing $b_{18}$ are non-negative, and there are $\binom{17}{2} = 136$ such triples.

The minimum possible value of $A$ is 136.

\(\square\)
