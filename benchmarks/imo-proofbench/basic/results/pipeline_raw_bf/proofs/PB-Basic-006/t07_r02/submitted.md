To prove that for any infinite sequence of integers $c_0, c_1, c_2, \ldots$ such that $c_0 \neq 0$, there exists some integer $k \geq 0$ such that the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots, we proceed by contradiction.

Assume that for all integers $k \geq 1$, the polynomial $P_k(x)$ has $k$ distinct real roots.

**1. Newton's Inequalities**
A fundamental property of polynomials with all real roots is given by Newton's Inequalities. If a polynomial $P(x) = \sum_{i=0}^k a_i x^i$ has all real roots, then its coefficients $a_i$ must satisfy:
\[ a_i^2 \geq a_{i-1} a_{i+1} \frac{(i+1)(k-i+1)}{i(k-i)} \quad \text{for } 1 \leq i \leq k-1. \]
Since we assume that $P_k(x)$ has $k$ distinct real roots for all $k \geq 1$, this inequality must hold for the coefficients $c_i$ for every $k > i$. Fixing $i$ and taking the limit as $k \to \infty$, the factor $\frac{k-i+1}{k-i}$ approaches $1$. Thus, we obtain the necessary condition:
\[ c_i^2 \geq c_{i-1} c_{i+1} \frac{i+1}{i} \quad \text{for all } i \geq 1. \]

**2. Convergence to an Entire Function**
The assumption that $P_k(x)$ has $k$ real roots for all $k$ is extremely restrictive. In the theory of entire functions, the Laguerre-Pólya class $\mathcal{LP}$ consists of functions that can be represented as the uniform limit on compact subsets of the complex plane of polynomials with only real roots.
If $P_k(x)$ has $k$ real roots for all $k$, the sequence of polynomials $P_k(x)$ must converge to a function $f(z) = \sum_{i=0}^\infty c_i z^i$ that is an entire function (i.e., its radius of convergence is infinite). If the radius of convergence were finite, the polynomials $P_k(x)$ could not maintain $k$ real roots as $k \to \infty$, because the growth of the coefficients would violate the conditions required for the roots to remain real.

**3. Integer Coefficients and Entire Functions**
Let $f(z) = \sum_{i=0}^\infty c_i z^i$ be an entire function. By the definition of the radius of convergence, we must have:
\[ \lim_{i \to \infty} |c_i|^{1/i} = 0. \]
However, the coefficients $c_i$ are given as integers. For any integer $c_i$, either $c_i = 0$ or $|c_i| \geq 1$. If $|c_i| \geq 1$, then $|c_i|^{1/i} \geq 1$.
The only way for the limit $\lim_{i \to \infty} |c_i|^{1/i} = 0$ to hold is if $c_i = 0$ for all sufficiently large $i$. That is, there must exist some integer $K$ such that $c_i = 0$ for all $i > K$.

**4. Final Contradiction**
If $c_i = 0$ for all $i > K$, then for any $k > K$, the polynomial $P_k(x)$ is identical to the polynomial $P_K(x)$:
\[ P_k(x) = \sum_{i=0}^k c_i x^i = \sum_{i=0}^K c_i x^i = P_K(x). \]
The number of distinct real roots of $P_k(x)$ is therefore equal to the number of distinct real roots of $P_K(x)$. Let $N(P)$ denote the number of distinct real roots. Then for $k > K$:
\[ N(P_k) = N(P_K) \leq K. \]
Since $k > K$, it follows that $N(P_k) \leq K < k$. This contradicts the assumption that $N(P_k) = k$ for all $k \geq 1$.

Therefore, there must exist some $k \geq 0$ such that $P_k(x)$ has fewer than $k$ distinct real roots. \(\square\)
