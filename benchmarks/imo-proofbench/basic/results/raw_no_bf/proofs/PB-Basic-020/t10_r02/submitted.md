To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we begin by rearranging the equation:
\[ a^2 - ab = b^3 + 1 \]
The right side can be factored as a sum of cubes:
\[ a(a - b) = (b + 1)(b^2 - b + 1) \]
Since $a$ is a prime number, it must divide at least one of the factors on the right side. Thus, we have two cases: $a \mid (b + 1)$ or $a \mid (b^2 - b + 1)$.

**Case 1: $a \mid (b + 1)$**
Let $b + 1 = na$ for some positive integer $n$. Substituting this into the equation $a(a - b) = (b + 1)(b^2 - b + 1)$, we get:
\[ a(a - b) = na(b^2 - b + 1) \implies a - b = n(b^2 - b + 1) \]
Solving for $a$:
\[ a = n(b^2 - b + 1) + b \]
Substituting $a = \frac{b + 1}{n}$ into this expression:
\[ \frac{b + 1}{n} = n(b^2 - b + 1) + b \]
\[ b + 1 = n^2(b^2 - b + 1) + nb \]
\[ n^2 b^2 + (n - n^2)b + (n^2 - 1) = 0 \]
For $b$ to be a real number, the discriminant $D_b$ of this quadratic in $b$ must be non-negative:
\[ D_b = (n - n^2)^2 - 4n^2(n^2 - 1) = n^2(1 - n)^2 - 4n^2(n^2 - 1) = n^2(1 - 2n + n^2 - 4n^2 + 4) = n^2(-3n^2 - 2n + 5) \]
For $D_b \ge 0$, we require $-3n^2 - 2n + 5 \ge 0$. Solving $3n^2 + 2n - 5 = 0$ gives $n = \frac{-2 \pm \sqrt{4 + 60}}{6}$, so $n = 1$ or $n = -5/3$. Thus, we must have $-5/3 \le n \le 1$. Since $n$ is a positive integer, $n = 1$.
Plugging $n = 1$ into $b+1 = n^2(b^2-b+1) + nb$, we get $b+1 = b^2-b+1+b$, which simplifies to $b^2 = b$, meaning $b=0$ or $b=1$. Neither is a prime number.

**Case 2: $a \mid (b^2 - b + 1)$**
Let $b^2 - b + 1 = ma$ for some positive integer $m$. Substituting this into $a(a - b) = (b + 1)(b^2 - b + 1)$, we get:
\[ a(a - b) = (b + 1)ma \implies a - b = m(b + 1) \implies a = mb + m + b = (m + 1)b + m \]
Now substitute $a$ back into the relation $b^2 - b + 1 = ma$:
\[ b^2 - b + 1 = m((m + 1)b + m) = (m^2 + m)b + m^2 \]
\[ b^2 - (m^2 + m + 1)b + (1 - m^2) = 0 \]
For $b$ to be an integer, the discriminant $D$ must be a perfect square:
\[ D = (m^2 + m + 1)^2 - 4(1 - m^2) = m^4 + 2m^3 + 3m^2 + 2m + 1 - 4 + 4m^2 = m^4 + 2m^3 + 7m^2 + 2m - 3 \]
We compare $D$ with consecutive squares:
1. For $m=1$, $D = 1+2+7+2-3 = 9 = 3^2$. The quadratic in $b$ is $b^2 - 3b = 0$, giving $b=3$ (since $b$ is prime). Then $a = (1+1)3 + 1 = 7$, which is prime. $(7, 3)$ is a solution.
2. For $m=2$, $D = 16+16+28+4-3 = 61$, which is not a square.
3. For $m \ge 3$:
   Consider $(m^2 + m + 2)^2 = m^4 + 2m^3 + 5m^2 + 4m + 4$.
   $D - (m^2 + m + 2)^2 = 2m^2 - 2m - 7$. For $m=3$, $18-6-7 = 5 > 0$. For $m > 3$, $2m(m-1) - 7 > 0$.
   Consider $(m^2 + m + 3)^2 = m^4 + 2m^3 + 7m^2 + 6m + 9$.
   $(m^2 + m + 3)^2 - D = 4m + 12$, which is always positive for $m \ge 1$.
   Since $(m^2 + m + 2)^2 < D < (m^2 + m + 3)^2$ for all $m \ge 3$, $D$ cannot be a square.

Thus, the only solution is $(a, b) = (7, 3)$.

Checking: $7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$.

The only pair of primes is $(7, 3)$. \(\square\)
