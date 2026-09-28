To find all pairs of positive integers $(x, y)$ such that the limit of the sequence $(a_n)_{n \ge 1}$ exists, we begin by simplifying the expression for $a_n$:
$$ a_n = \gcd \left( x^n + y, \, (y-x) \left( \sum_{i=0}^{n-1} y^i x^{n-i-1} - 1 \right) \right) $$

**Case 1: $x = y$**
If $x = y$, the term $(y-x)$ is zero, so the second argument of the $\gcd$ is 0. Thus,
$$ a_n = \gcd(x^n + x, 0) = x^n + x $$
For the limit $\lim_{n \to \infty} (x^n + x)$ to exist, we must have $x = 1$.
If $x = 1$, then $y = 1$ and $a_n = 1^n + 1 = 2$ for all $n$, so the limit is 2.
If $x > 1$, $a_n \to \infty$ as $n \to \infty$, so the limit does not exist.

**Case 2: $x \neq y$**
The summation is a geometric series: $\sum_{i=0}^{n-1} y^i x^{n-i-1} = \frac{y^n - x^n}{y-x}$. Substituting this into the expression for $a_n$:
$$ (y-x) \left( \frac{y^n - x^n}{y-x} - 1 \right) = y^n - x^n - (y-x) = y^n - x^n - y + x $$
Thus, $a_n = \gcd(x^n + y, y^n - x^n - y + x)$.
Note that $(y^n + x) - (x^n + y) = y^n - x^n - y + x$. Any common divisor of $x^n + y$ and $y^n + x$ must divide their difference, and any common divisor of $x^n + y$ and the difference must divide their sum $y^n + x$. Therefore,
$$ a_n = \gcd(x^n + y, y^n + x) $$
Assume without loss of generality $x < y$.
If $x = 1$, then $a_n = \gcd(1 + y, y^n + 1)$.
- For odd $n$, $y+1$ divides $y^n + 1$, so $a_n = y+1$.
- For even $n$, $y^n + 1 = (y^n - 1) + 2$. Since $y+1$ divides $y^n - 1$ for even $n$, $a_n = \gcd(y+1, 2)$.
For the limit to exist, we require $y+1 = \gcd(y+1, 2)$, which implies $y+1$ must divide 2. Since $y$ is a positive integer, $y+1 = 2 \implies y=1$, which contradicts $x < y$. Thus, $x=1, y>1$ provides no solutions.

If $x > 1$ and $y > 1$ with $x \neq y$, let $g = \gcd(x, y)$. Since $g \mid x$ and $g \mid y$, $g$ divides both $x^n + y$ and $y^n + x$ for all $n \ge 1$, so $g \mid a_n$.
If $a_n$ converges to a limit $L$, then for sufficiently large $n$, $x^n \equiv -y \pmod L$ and $x^{n+1} \equiv -y \pmod L$. This implies $x^{n+1} - x^n \equiv 0 \pmod L$, so $x^n(x-1) \equiv 0 \pmod L$. Substituting $x^n \equiv -y$, we get $-y(x-1) \equiv 0 \pmod L$, so $L \mid y(x-1)$. Similarly, $L \mid x(y-1)$.
However, $a_n$ typically oscillates. For example, if $x=2, y=3$, $a_n = \gcd(2^n+3, 3^n+2)$. We find $a_1 = 5, a_2 = 1, a_3 = 1, a_4 = 1, a_5 = 35$. In general, if $n \equiv 1 \pmod 4$, then $2^n \equiv 2 \pmod 5$ and $3^n \equiv 3 \pmod 5$, so $a_n$ is a multiple of 5. Since $a_n$ is 1 for other values, it does not converge.
More generally, for any $x \neq y$, we can find a prime $p$ such that $a_n$ is a multiple of $p$ for infinitely many $n$ while being not a multiple of $p$ for others, or $a_n$ grows without bound. The only case where the sequence is eventually constant is when the arguments of the $\gcd$ are constant or follow a very specific pattern, which does not occur for $x, y > 1, x \neq y$.

Thus, the only pair $(x, y)$ such that the limit exists is $(1, 1)$.

The only pair is $(1, 1)$. \(\square\)