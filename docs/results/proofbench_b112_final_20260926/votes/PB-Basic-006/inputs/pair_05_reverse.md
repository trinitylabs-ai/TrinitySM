# Problem

Consider any infinite sequence of integers $c_0, c_1, c_2, \ldots $ such that $c_0 \neq 0$. Prove that for some integer $k \geq 0$, the polynomial $P(x) = \sum_{i = 0}^k c_i x^i$ has fewer than $k$ distinct real roots.

# Proof A

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

# Proof B

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
