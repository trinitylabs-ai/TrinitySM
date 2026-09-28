To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we rewrite the equation as:
\[ a^2 - ab = b^3 + 1 \]
Factoring both sides, we obtain:
\[ a(a - b) = (b + 1)(b^2 - b + 1) \]
Since $a$ is prime, let $d = \gcd(a, b + 1)$. The only possible values for $d$ are $1$ and $a$.

**Case 1: $d = a$**
If $d = a$, then $a$ divides $b + 1$. Let $b + 1 = ma$ for some positive integer $m$. Substituting $b = ma - 1$ into the factored equation:
\[ a(a - (ma - 1)) = ma((ma - 1)^2 - (ma - 1) + 1) \]
\[ a(a - ma + 1) = ma(m^2a^2 - 2ma + 1 - ma + 1 + 1) \]
Since $a$ is prime, $a \neq 0$. Dividing both sides by $a$:
\[ a - ma + 1 = m(m^2a^2 - 3ma + 3) = m^3a^2 - 3m^2a + 3m \]
Rearranging this into a quadratic in $a$:
\[ m^3a^2 + (m - 3m^2 - 1)a + 3m - 1 = 0 \]
If $m = 1$, the equation becomes $a^2 - 3a + 2 = 0$, which factors as $(a - 1)(a - 2) = 0$. This gives $a = 1$ or $a = 2$. Since $a$ is prime, we must have $a = 2$. Then $b = ma - 1 = 1(2) - 1 = 1$, but $1$ is not a prime number.
If $m \ge 2$, let $f(a) = m^3a^2 + (m - 3m^2 - 1)a + 3m - 1$. For $a = 2$, $f(2) = 4m^3 - 6m^2 + 5m - 3$. For $m = 2$, $f(2) = 32 - 24 + 10 - 3 = 15$. Since $f'(a) = 2m^3a + m - 3m^2 - 1$, for $m \ge 2$ and $a \ge 2$, $f'(a) \ge 4m^3 - 3m^2 + m - 1$, which is positive for all $m \ge 2$. Thus, $f(a)$ is strictly increasing for $a \ge 2$, and $f(a) > 0$ for all $m \ge 2, a \ge 2$.
Thus, Case 1 yields no solutions.

**Case 2: $d = 1$**
If $\gcd(a, b + 1) = 1$, then from $a(a - b) = (b + 1)(b^2 - b + 1)$, it must be that $a$ divides $b^2 - b + 1$. Let $b^2 - b + 1 = na$ for some positive integer $n$. Then:
\[ a - b = \frac{(b + 1)(b^2 - b + 1)}{a} = n(b + 1) \implies a = (n + 1)b + n \]
Substituting this expression for $a$ back into $b^2 - b + 1 = na$:
\[ b^2 - b + 1 = n((n + 1)b + n) = (n^2 + n)b + n^2 \]
\[ b^2 - (n^2 + n + 1)b + (1 - n^2) = 0 \]
For $b$ to be an integer, the discriminant $D$ must be a perfect square:
\[ D = (n^2 + n + 1)^2 - 4(1 - n^2) = n^4 + 2n^3 + 3n^2 + 2n + 1 - 4 + 4n^2 = n^4 + 2n^3 + 7n^2 + 2n - 3 \]
We evaluate $D$ for small $n$:
- For $n = 1$, $D = 1 + 2 + 7 + 2 - 3 = 9 = 3^2$. Then $b^2 - 3b = 0$, so $b(b - 3) = 0$. Since $b$ is prime, $b = 3$. Then $a = (1 + 1)(3) + 1 = 7$. Checking: $7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$. This is a solution.
- For $n = 2$, $D = 16 + 16 + 28 + 4 - 3 = 61$, which is not a square.
- For $n \ge 3$, we compare $D$ to $(n^2 + n + 2)^2$ and $(n^2 + n + 3)^2$:
  \[ (n^2 + n + 2)^2 = n^4 + 2n^3 + 5n^2 + 4n + 4 \]
  \[ (n^2 + n + 3)^2 = n^4 + 2n^3 + 7n^2 + 6n + 9 \]
  The difference $D - (n^2 + n + 2)^2 = 2n^2 - 2n - 7$. For $n \ge 3$, $2n^2 - 2n - 7 \ge 18 - 6 - 7 = 5 > 0$.
  The difference $(n^2 + n + 3)^2 - D = 4n + 12 > 0$ for all $n > 0$.
  Therefore, for $n \ge 3$, $(n^2 + n + 2)^2 < D < (n^2 + n + 3)^2$, so $D$ cannot be a perfect square.

Thus, the only pair of primes $(a, b)$ that satisfies the equation is $(7, 3)$.

\(\square\)
