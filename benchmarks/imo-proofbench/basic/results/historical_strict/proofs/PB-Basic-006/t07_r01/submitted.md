We proceed by contradiction. Suppose that for every integer $k \geq 1$, the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has at least $k$ distinct real roots.

Since $P_k(x)$ is a polynomial of degree at most $k$, the assumption that it has at least $k$ distinct real roots implies that it must have exactly $k$ distinct real roots. This further implies that the degree of $P_k(x)$ must be exactly $k$, so $c_k \neq 0$ for all $k \geq 1$. We are given $c_0 \neq 0$, so $c_k \neq 0$ for all $k \geq 0$.

Consider the power series $f(x) = \sum_{i=0}^\infty c_i x^i$. A known result in the theory of entire functions, established by Pólya and Schur, states that if the partial sums $P_k(x)$ of a power series are all real-rooted, then the power series defines an entire function. That is, the radius of convergence of $f(x)$ is infinite.

For a power series $f(x) = \sum_{i=0}^\infty c_i x^i$ to be an entire function, its coefficients must satisfy the condition:
\[ \lim_{i \to \infty} |c_i|^{1/i} = 0. \]
However, we are given that the coefficients $c_i$ are integers. For any non-zero integer $c_i$, we have $|c_i| \geq 1$, which implies that $|c_i|^{1/i} \geq 1$. 

If $c_i \neq 0$ for all $i \geq 0$, then the sequence $|c_i|^{1/i}$ is always greater than or equal to 1, and thus the limit $\lim_{i \to \infty} |c_i|^{1/i}$ cannot be 0. This contradicts the requirement that $f(x)$ is an entire function.

Therefore, the initial assumption must be false. There must exist some integer $k \geq 0$ such that the polynomial $P(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots.
