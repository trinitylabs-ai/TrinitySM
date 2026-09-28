# Problem

Consider any infinite sequence of integers $c_0, c_1, c_2, \ldots $ such that $c_0 \neq 0$. Prove that for some integer $k \geq 0$, the polynomial $P(x) = \sum_{i = 0}^k c_i x^i$ has fewer than $k$ distinct real roots.

# Proof A

1: To prove that for any infinite sequence of integers $c_0, c_1, c_2, \ldots$ with $c_0 \neq 0$, there exists an integer $k \geq 0$ such that the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots, we proceed by contradiction.
2: 
3: Suppose that for all $k \geq 1$, the polynomial $P_k(x)$ has $k$ distinct real roots. Since $P_k(x)$ is a polynomial of degree at most $k$, the existence of $k$ distinct real roots implies that the degree of $P_k(x)$ must be exactly $k$. Therefore, the leading coefficient $c_k$ must be non-zero for all $k \geq 1$. Combined with the given condition $c_0 \neq 0$, we conclude that $c_i \neq 0$ for all $i \geq 0$.
4: 
5: A polynomial of degree $k$ with $k$ real roots is called a hyperbolic polynomial. A fundamental property of hyperbolic polynomials is given by Newton's Inequalities: if $P(x) = \sum_{i=0}^k a_i x^i$ has all real roots, then its coefficients $a_i$ satisfy
6: \[ a_i^2 \geq a_{i-1} a_{i+1} \frac{(i+1)(k-i+1)}{i(k-i)} \quad \text{for } 1 \leq i \leq k-1. \]
7: Applying this to $P_k(x)$ with $a_i = c_i$, we have for all $k > i$:
8: \[ c_i^2 \geq c_{i-1} c_{i+1} \frac{(i+1)(k-i+1)}{i(k-i)}. \]
9: Taking the limit as $k \to \infty$, the factor $\frac{k-i+1}{k-i} = 1 + \frac{1}{k-i}$ approaches 1. Thus, for all $i \geq 1$, the coefficients must satisfy the ultra-log-concavity condition:
10: \[ c_i^2 \geq c_{i-1} c_{i+1} \frac{i+1}{i}. \]
11: The sequence of polynomials $P_k(x)$ corresponds to the partial sums of the power series $f(z) = \sum_{i=0}^\infty c_i z^i$. A theorem in the theory of entire functions (originally due to Pólya) states that if the partial sums $P_k(z)$ of a power series are all hyperbolic, then the power series converges uniformly on compact subsets of the complex plane to an entire function $f(z)$ belonging to the Laguerre-Pólya class.
12: 
13: For $f(z) = \sum_{i=0}^\infty c_i z^i$ to be an entire function, its radius of convergence must be infinite, which requires:
14: \[ \lim_{n \to \infty} |c_n|^{1/n} = 0. \]
15: However, we are given that $c_n$ are integers. Since we established that $c_n \neq 0$ for all $n \geq 0$, we must have $|c_n| \geq 1$ for all $n \geq 0$. This implies:
16: \[ |c_n|^{1/n} \geq 1 \quad \text{for all } n \geq 1. \]
17: This contradicts the requirement that $\lim_{n \to \infty} |c_n|^{1/n} = 0$. Therefore, the assumption that $P_k(x)$ has $k$ distinct real roots for all $k \geq 1$ must be false.
18: 
19: Thus, there must exist some integer $k \geq 0$ such that the polynomial $P_k(x)$ has fewer than $k$ distinct real roots.

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
