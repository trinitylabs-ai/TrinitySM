# Problem

Consider any infinite sequence of integers $c_0, c_1, c_2, \ldots $ such that $c_0 \neq 0$. Prove that for some integer $k \geq 0$, the polynomial $P(x) = \sum_{i = 0}^k c_i x^i$ has fewer than $k$ distinct real roots.

# Proof A

1: To prove that for any infinite sequence of integers $c_0, c_1, c_2, \ldots$ with $c_0 \neq 0$, there exists some integer $k \geq 0$ such that the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots, we proceed by contradiction.
2: 
3: Assume that for every $k \geq 1$, the polynomial $P_k(x)$ has at least $k$ distinct real roots. Since $P_k(x)$ is a polynomial of degree at most $k$, it can have at most $k$ roots. Thus, the assumption implies that for all $k \geq 1$, $P_k(x)$ has exactly $k$ distinct real roots. This further implies that $c_k \neq 0$ for all $k \geq 1$, because if $c_k = 0$ for some $k$, then $P_k(x) = P_{k-1}(x)$, which has at most $k-1$ roots, contradicting the assumption that $P_k$ has $k$ roots.
4: 
5: For any $k \geq 2$, let $r_{1,k}, r_{2,k}, \ldots, r_{k,k}$ be the $k$ distinct real roots of $P_k(x)$. Since $c_0 \neq 0$, no root is zero. Let $\rho_{i,k} = 1/r_{i,k}$ be the roots of the reciprocal polynomial
6: \[ Q_k(x) = x^k P_k(1/x) = c_0 x^k + c_1 x^{k-1} + \dots + c_k. \]
7: The roots $\rho_{i,k}$ are also $k$ distinct real numbers. To obtain a monic polynomial with integer coefficients, we define the substitution $y = c_0 x$. The roots of the resulting polynomial $R_k(y)$ are $y_{i,k} = c_0 \rho_{i,k}$. Specifically,
8: \[ R_k(y) = c_0^{k-1} Q_k(y/c_0) = c_0^{k-1} \left[ c_0 \left(\frac{y}{c_0}\right)^k + c_1 \left(\frac{y}{c_0}\right)^{k-1} + \dots + c_k \right] = y^k + c_1 y^{k-1} + c_0 c_2 y^{k-2} + \dots + c_0^{k-1} c_k. \]
9: Since $c_i \in \mathbb{Z}$, $R_k(y)$ is a monic polynomial with integer coefficients. The discriminant $\Delta_k$ of $R_k(y)$ is given by $\Delta_k = \prod_{1 \le i < j \le k} (y_{i,k} - y_{j,k})^2$. Since the roots $y_{i,k}$ are distinct and real, $\Delta_k$ is a non-zero integer and $\Delta_k > 0$, which implies $\Delta_k \geq 1$.
10: 
11: By the Arithmetic Mean-Geometric Mean (AM-GM) inequality, we have:
12: \[ \frac{1}{\binom{k}{2}} \sum_{1 \le i < j \le k} (y_{i,k} - y_{j,k})^2 \ge \left( \prod_{1 \le i < j \le k} (y_{i,k} - y_{j,k})^2 \right)^{1/\binom{k}{2}} = \Delta_k^{1/\binom{k}{2}} \ge 1^{1/\binom{k}{2}} = 1. \]
13: Thus, $\sum_{i < j} (y_{i,k} - y_{j,k})^2 \geq \binom{k}{2} = \frac{k(k-1)}{2}$.
14: We utilize the identity $\sum_{i < j} (y_i - y_j)^2 = k \sum_{i=1}^k y_i^2 - (\sum_{i=1}^k y_i)^2$. From the coefficients of $R_k(y)$, Vieta's formulas give:
15: \[ \sum_{i=1}^k y_{i,k} = -c_1, \quad \sum_{i=1}^k y_{i,k}^2 = (-c_1)^2 - 2(c_0 c_2) = c_1^2 - 2c_0 c_2. \]
16: Substituting these into the inequality, we obtain:
17: \[ k(c_1^2 - 2c_0 c_2) - (-c_1)^2 \geq \frac{k(k-1)}{2}. \]
18: This simplifies to:
19: \[ k(c_1^2 - 2c_0 c_2) - c_1^2 \geq \frac{1}{2}k^2 - \frac{1}{2}k. \]
20: The left-hand side of this inequality is a linear function of $k$, while the right-hand side is a quadratic function of $k$. For any fixed integers $c_0, c_1, c_2$, as $k \to \infty$, the quadratic term $\frac{1}{2}k^2$ will eventually exceed the linear term $k(c_1^2 - 2c_0 c_2)$, making the inequality impossible for sufficiently large $k$.
21: 
22: This contradiction shows that the assumption that $P_k(x)$ has $k$ distinct real roots for all $k \geq 1$ must be false. Therefore, for some integer $k \geq 0$, the polynomial $P_k(x)$ has fewer than $k$ distinct real roots.

# Proof B

1: We proceed by contradiction. Assume that for every integer $k \geq 1$, the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has at least $k$ distinct real roots.
2: 
3: Since the degree of $P_k(x)$ is at most $k$, the assumption implies that $P_k(x)$ must have exactly $k$ distinct real roots. This further implies that $c_k \neq 0$ for all $k \geq 1$, because if $c_k = 0$, then $\deg(P_k) \leq k-1$, and a polynomial of degree at most $k-1$ cannot have $k$ distinct roots.
4: 
5: Consider the power series $f(z) = \sum_{n=0}^\infty c_n z^n$. A theorem by George Pólya states that if all the partial sums $P_k(z)$ of a power series have only real roots, then the power series converges for all $z \in \mathbb{C}$. In other words, $f(z)$ is an entire function.
6: 
7: For any entire function $f(z) = \sum_{n=0}^\infty c_n z^n$, the radius of convergence $R$ is infinite. According to the Cauchy-Hadamard theorem, the radius of convergence is given by
8: \[ \frac{1}{R} = \limsup_{n \to \infty} |c_n|^{1/n}. \]
9: Since $R = \infty$, it must be that
10: \[ \limsup_{n \to \infty} |c_n|^{1/n} = 0. \]
11: This implies that $\lim_{n \to \infty} |c_n|^{1/n} = 0$.
12: 
13: However, we have established that $c_n$ are integers and $c_n \neq 0$ for all $n \geq 1$. For any non-zero integer $c_n$, we have $|c_n| \geq 1$. Consequently,
14: \[ |c_n|^{1/n} \geq 1^{1/n} = 1 \]
15: for all $n \geq 1$. This implies that
16: \[ \limsup_{n \to \infty} |c_n|^{1/n} \geq 1, \]
17: which contradicts the requirement that the limit be 0.
18: 
19: Therefore, the assumption that $P_k(x)$ has at least $k$ distinct real roots for all $k \geq 1$ must be false. Thus, there exists some integer $k \geq 1$ such that $P_k(x)$ has fewer than $k$ distinct real roots. Since $c_0 \neq 0$, $P_0(x) = c_0$ has 0 distinct real roots, and the condition "fewer than $k$ distinct real roots" for $k=0$ would require $0 < 0$, which is impossible; hence the required $k$ must be at least 1.
