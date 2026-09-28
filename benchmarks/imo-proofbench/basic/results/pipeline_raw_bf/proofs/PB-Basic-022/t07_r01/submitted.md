To find all polynomials $P(x)$ with integer coefficients such that the equation $P(x) = s$ has an integer solution $x$ for every $s \in S = \{n^{2024} : n \in \mathbb{Z}_{\ge 0}\}$, we proceed as follows.

Let $k = 2024$. The condition is that for every $n \in \mathbb{Z}_{\ge 0}$, there exists an integer $x_n$ such that $P(x_n) = n^k$. Since $n^k$ takes infinitely many values, $P(x)$ must be a non-constant polynomial. Let $d = \deg P$. As $n \to \infty$, $n^k \to \infty$, so $P(x)$ must tend to infinity as $|x| \to \infty$. This implies that the leading coefficient $a_d$ of $P$ must be positive if $d$ is even.

For large $n$, the equation $a_d x_n^d \approx n^k$ implies $x_n \approx (1/a_d)^{1/d} n^{k/d}$. For $x_n$ to be an integer for all $n$, the exponent $k/d$ must be an integer. If $k/d$ were not an integer, the difference $x_{n+1} - x_n$ would grow as $n^{k/d-1}$ (if $k/d > 1$) or shrink to 0 (if $k/d < 1$), neither of which allows $x_n$ to remain an integer for all $n$ unless the growth is polynomial. Thus, $d$ must be a divisor of $k=2024$. Let $m = k/d$.

We now examine the form of $P(x)$. Suppose $P(x) = a_d x^d + a_{d-1} x^{d-1} + \dots + a_0$. For large $n$, we have:
$$x_n = \left(\frac{n^k}{a_d}\right)^{1/d} - \frac{a_{d-1}}{d a_d} + O(n^{m-2})$$
For $x_n$ to be an integer for all $n$, the term $(n^k/a_d)^{1/d} = a_d^{-1/d} n^m$ must have a constant fractional part for large $n$. Let $C = a_d^{-1/d}$. If $C$ is not an integer, $C n^m \pmod 1$ cannot be constant for all $n$. For instance, if $C = p/q$ in lowest terms, $p(n+1)^m \equiv p n^m \pmod q$ for all $n$, which implies $q|p$ for $n=0$, meaning $C$ is an integer. Since $a_d$ is an integer, $C = a_d^{-1/d} \in \mathbb{Z}$ implies $a_d = 1$ (if $d$ is even) or $a_d = \pm 1$ (if $d$ is odd).

If $a_d = 1$, then $x_n = n^m - \frac{a_{d-1}}{d} + O(n^{m-2})$. For $x_n$ to be an integer, $\frac{a_{d-1}}{d}$ must be an integer $b$, and the $O(n^{m-2})$ term must vanish for large $n$. This implies $P(x) = (x+b)^d$. Similarly, if $a_d = -1$ (which requires $d$ to be odd), we obtain $P(x) = (-x+b)^d$.

We verify these solutions:
If $P(x) = (ax+b)^d$ where $a \in \{1, -1\}$, $b \in \mathbb{Z}$, and $d|2024$, then $P(x) = n^{2024}$ becomes:
$$(ax+b)^d = n^{2024} \implies ax+b = \pm n^{2024/d}$$
Since $2024/d$ is an integer $m$, we have $ax = \pm n^m - b$. Since $a = \pm 1$, $x = a(\pm n^m - b)$ is always an integer.

If $d$ is even, $(ax+b)^d$ with $a=1$ and $a=-1$ are redundant because $(-x+b)^d = (x-b)^d$. If $d$ is odd, they are distinct. In both cases, the form $(\pm x + b)^d$ covers all solutions.

The polynomials $P$ are $P(x) = (x+b)^d$ and $P(x) = (-x+b)^d$ for all $b \in \mathbb{Z}$ and all positive divisors $d$ of 2024. $\square$
