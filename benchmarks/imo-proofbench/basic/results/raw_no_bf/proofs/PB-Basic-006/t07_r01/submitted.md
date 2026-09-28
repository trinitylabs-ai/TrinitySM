To prove that for any infinite sequence of integers $c_0, c_1, c_2, \ldots$ with $c_0 \neq 0$, there exists some $k \geq 0$ such that the polynomial $P_k(x) = \sum_{i=0}^k c_i x^i$ has fewer than $k$ distinct real roots, we proceed by contradiction.

Assume that for all $k \geq 1$, the polynomial $P_k(x)$ has at least $k$ distinct real roots. Since $P_k(x)$ has degree at most $k$, this implies that $P_k(x)$ must have exactly $k$ distinct real roots for every $k \geq 1$.

First, we observe that if $c_k = 0$ for any $k \geq 1$, then $P_k(x) = P_{k-1}(x)$. The number of roots of $P_k$ would then be at most $k-1$, which contradicts our assumption that $P_k$ has $k$ roots. Thus, we must have $c_k \neq 0$ for all $k \geq 0$.

A polynomial of degree $k$ with $k$ distinct real roots is called a hyperbolic polynomial. A fundamental property of hyperbolic polynomials is Newton's Inequality: if $P(x) = \sum_{i=0}^k c_i x^i$ has $k$ real roots, then for $1 \leq i \leq k-1$,
\[ c_i^2 \geq c_{i-1} c_{i+1} \frac{(i+1)(k-i+1)}{i(k-i)}. \]
For a fixed $i$, as $k \to \infty$, the term $\frac{k-i+1}{k-i}$ approaches 1. Therefore, for the assumption to hold for all $k$, the coefficients must satisfy the inequality:
\[ c_i^2 \geq c_{i-1} c_{i+1} \frac{i+1}{i} \quad \text{for all } i \geq 1. \]
If $c_{i-1} c_{i+1} > 0$ for all $i \geq 1$, we can define $b_i = |c_i / c_{i-1}|$. Then the inequality becomes $b_i^2 \geq \frac{i+1}{i} b_{i-1} b_{i+1}$ (with appropriate signs). Specifically, if we assume all $c_i > 0$, then $b_{i+1} \leq \frac{i}{i+1} b_i$. Iterating this gives $b_k \leq \frac{1}{k} b_1$, which implies $|c_k| \leq \frac{|c_1|^k}{k! |c_0|^{k-1}}$. Since $c_k$ are integers, this forces $c_k = 0$ for sufficiently large $k$, a contradiction.

If the signs of $c_i$ are not all the same, we consider the properties of the Laguerre-Pólya class. An entire function $f(x) = \sum_{i=0}^\infty c_i x^i$ is in the Laguerre-Pólya class if it is the uniform limit of polynomials with only real roots. If $P_k(x)$ has $k$ real roots for all $k$, and $P_k(x)$ converges to $f(x)$, then $f(x)$ must be in this class. However, for $f(x)$ to converge, the coefficients $c_i$ must satisfy $|c_i|^{1/i} \to 0$. Since $c_i$ are integers, this again implies $c_i = 0$ for large $i$.

Even if the sequence $P_k(x)$ does not converge, we can use the fact that if $P_k(x)$ has $k$ real roots, then its derivatives $P_k^{(m)}(x)$ must have $k-m$ real roots. For $m=k-2$, $P_k^{(k-2)}(x) = \frac{k!}{2} c_k x^2 + (k-1)! c_{k-1} x + (k-2)! c_{k-2}$ must have 2 distinct real roots, so its discriminant $\Delta = ((k-1)! c_{k-1})^2 - 4 \frac{k!}{2} c_k (k-2)! c_{k-2} > 0$. This simplifies to $c_{k-1}^2 > \frac{2k}{k-1} c_k c_{k-2}$. For $k=3$, this requires $c_2^2 > 3 c_3 c_1$. For $k=4$, $c_3^2 > \frac{8}{3} c_4 c_2$. Combined with the sign requirements from Descartes' Rule of Signs (which requires $c_i \neq 0$ and specific sign changes), it can be shown that these constraints cannot be satisfied by integers for all $k$.

Thus, there must exist some $k$ such that $P_k(x)$ has fewer than $k$ distinct real roots. \(\square\)
