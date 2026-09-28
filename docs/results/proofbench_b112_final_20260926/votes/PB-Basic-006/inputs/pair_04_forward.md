# Problem

Consider any infinite sequence of integers $c_0, c_1, c_2, \ldots $ such that $c_0 \neq 0$. Prove that for some integer $k \geq 0$, the polynomial $P(x) = \sum_{i = 0}^k c_i x^i$ has fewer than $k$ distinct real roots.

# Proof A

1: Assume for the sake of contradiction that for all $k \geq 1$, the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has at least $k$ distinct real roots. Since $\deg(P_k) \leq k$, $P_k(x)$ must have exactly $k$ distinct real roots for every $k \geq 1$. This implies that $c_k \neq 0$ for all $k \geq 0$, because if $c_k = 0$ for some $k \geq 1$, the degree of $P_k$ would be at most $k-1$, making it impossible to have $k$ distinct roots.
2: 
3: Newton's Inequality states that if a polynomial $\sum_{i=0}^n a_i x^i$ has only real roots, then its coefficients satisfy
4: \[ a_i^2 \geq a_{i-1} a_{i+1} \frac{(i+1)(n-i+1)}{i(n-i)} \quad \text{for } 1 \leq i \leq n-1. \]
5: Applying this to $P_k(x)$, we have for any fixed $i \geq 1$ and all $k > i$:
6: \[ c_i^2 \geq c_{i-1} c_{i+1} \frac{(i+1)(k-i+1)}{i(k-i)}. \]
7: As $k \to \infty$, the factor $\frac{k-i+1}{k-i} = 1 + \frac{1}{k-i}$ converges to $1$. Thus, for all $i \geq 1$, we must have
8: \[ c_i^2 \geq c_{i-1} c_{i+1} \frac{i+1}{i}. \]
9: Since the roots of $P_k(x)$ are distinct, the inequality is strict for all $k > i$, and thus $c_i^2 > c_{i-1} c_{i+1} \frac{i+1}{i}$ for all $i \geq 1$.
10: 
11: A sequence $c_0, c_1, \dots$ such that the polynomials $P_k(x) = \sum_{i=0}^k c_i x^i$ have only real roots for all $k$ is related to the theory of Pólya Frequency (PF) sequences. A sequence $a_n$ is called a PF sequence if the infinite Toeplitz matrix $T = (a_{i-j})_{i,j \geq 0}$ (where $a_k = 0$ for $k < 0$) is totally positive, meaning all its minors are non-negative. A known result in the study of the Laguerre-Pólya class of entire functions is that if all partial sums $P_k(x)$ of a power series $\sum c_n x^n$ are real-rooted, then the sequence $c_n$ must be a PF sequence up to a sign transformation of the form $c_n \to \sigma c_n$ or $c_n \to \sigma (-1)^n c_n$ for $\sigma \in \{1, -1\}$.
12: 
13: Since a PF sequence $a_n$ must satisfy $a_n \geq 0$ for all $n$, the original sequence $c_n$ must either eventually have a constant sign or eventually alternate in sign. Given that $c_n \neq 0$ for all $n$, this implies that there exists some $N$ such that for all $n > N$, the product $c_{n-1} c_{n+1}$ is strictly positive.
14: 
15: Let $d_n = |c_n|$. For $n > N$, the inequality $c_n^2 > c_{n-1} c_{n+1} \frac{n+1}{n}$ becomes
16: \[ d_n^2 > d_{n-1} d_{n+1} \frac{n+1}{n}. \]
17: Let $b_n = \frac{d_n}{d_{n-1}}$. The inequality simplifies to $b_n^2 > b_n b_{n+1} \frac{n+1}{n}$, which implies
18: \[ b_{n+1} < \frac{n}{n+1} b_n \quad \text{for all } n > N. \]
19: By induction, for $k > N$, we have
20: \[ b_k < \frac{N}{k} b_N. \]
21: Then for $k > N$, the absolute value of the $k$-th coefficient is
22: \[ d_k = d_N \prod_{j=N+1}^k b_j < d_N \prod_{j=N+1}^k \frac{N b_N}{j} = d_N \frac{(N b_N)^{k-N} N!}{k!}. \]
23: As $k \to \infty$, the term $\frac{(N b_N)^{k-N} N!}{k!}$ converges to $0$ because the factorial grows faster than any exponential. Thus, $d_k \to 0$ as $k \to \infty$. Since $d_k = |c_k|$ is the absolute value of an integer, $d_k$ must be $0$ for all sufficiently large $k$. This implies $c_k = 0$ for all sufficiently large $k$, which contradicts our earlier deduction that $c_k \neq 0$ for all $k \geq 0$.
24: 
25: Therefore, the assumption that $P_k(x)$ has at least $k$ distinct real roots for all $k \geq 1$ is false. There must exist some integer $k \geq 0$ such that $P(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots.

# Proof B

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
