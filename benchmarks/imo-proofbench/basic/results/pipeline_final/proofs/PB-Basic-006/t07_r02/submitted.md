We proceed by contradiction. Assume that for all integers $k \geq 1$, the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has $k$ distinct real roots.

First, we establish that $c_k \neq 0$ for all $k \geq 0$. By the premise, $c_0 \neq 0$. For any $k \geq 1$, $P_k(x)$ is a polynomial of degree at most $k$. A polynomial of degree $d$ can have at most $d$ roots. Since $P_k(x)$ is assumed to have $k$ distinct real roots, its degree must be exactly $k$. Thus, the leading coefficient $c_k$ must be non-zero for all $k \geq 1$. Consequently, $c_i \neq 0$ for all $i \geq 0$.

Newton's Inequalities state that if a polynomial $\sum_{i=0}^k a_i x^i$ has only real roots, then its coefficients satisfy
\[ S_j^2 \geq S_{j-1} S_{j+1} \quad \text{for } 1 \leq j \leq k-1, \]
where $S_j = a_j / \binom{k}{j}$ are the normalized coefficients. If the roots are distinct, the inequality is strict: $S_j^2 > S_{j-1} S_{j+1}$.

Applying this to $P_k(x)$, we have $S_j = c_j / \binom{k}{j}$. Since $c_j \neq 0$ for all $j$, $S_j$ is never zero. The condition $S_j^2 > S_{j-1} S_{j+1}$ implies that $S_{j-1}$ and $S_{j+1}$ must have the same sign. Since $S_0 = c_0 / \binom{k}{0} = c_0$, all $S_j$ must either all have the same sign as $c_0$ or alternate signs. In either case, we have $|S_j|^2 > |S_{j-1}| |S_{j+1}|$ for $1 \leq j \leq k-1$.

Let $b_j = |S_j|$. The sequence $b_0, b_1, \ldots, b_k$ is strictly log-concave, meaning the ratios $r_j = b_j / b_{j-1}$ are strictly decreasing:
\[ r_1 > r_2 > \dots > r_k. \]
We calculate the first and last ratios:
\[ r_1 = \frac{b_1}{b_0} = \frac{|c_1| / \binom{k}{1}}{|c_0| / \binom{k}{0}} = \frac{|c_1|}{k |c_0|}, \]
\[ r_k = \frac{b_k}{b_{k-1}} = \frac{|c_k| / \binom{k}{k}}{|c_{k-1}| / \binom{k}{k-1}} = \frac{|c_k|}{ |c_{k-1}| / k} = \frac{k |c_k|}{|c_{k-1}|}. \]
The condition $r_1 > r_k$ implies:
\[ \frac{|c_1|}{k |c_0|} > \frac{k |c_k|}{|c_{k-1}|} \implies |c_k| < \frac{|c_1| |c_{k-1}|}{k^2 |c_0|}. \]
Since $c_k$ is a non-zero integer, $|c_k| \geq 1$. Applying the inequality $|c_k| < \frac{|c_1|}{k^2 |c_0|} |c_{k-1}|$ recursively for $k, k-1, \ldots, 2$:
\[ |c_k| < \frac{|c_1|}{k^2 |c_0|} \cdot \frac{|c_1|}{(k-1)^2 |c_0|} \cdot \dots \cdot \frac{|c_1|}{2^2 |c_0|} |c_1| = \frac{|c_1|^k}{(k!)^2 |c_0|^{k-1}}. \]
As $k \to \infty$, the term $\frac{|c_1|^k}{(k!)^2 |c_0|^{k-1}} = |c_0| \left( \frac{|c_1|}{|c_0|} \right)^k \frac{1}{(k!)^2}$ tends to $0$ for any fixed $c_0, c_1$. However, we established that $|c_k| \geq 1$ for all $k$. This is a contradiction.

Therefore, the initial assumption must be false. There must exist some integer $k \geq 1$ such that the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots.
