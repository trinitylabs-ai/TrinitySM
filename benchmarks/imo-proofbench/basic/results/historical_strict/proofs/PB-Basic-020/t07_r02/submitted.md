To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we rearrange the equation as a quadratic in $a$:
\[a^2 - ab - (b^3 + 1) = 0.\]
Solving for $a$ using the quadratic formula, we obtain:
\[a = \frac{b \pm \sqrt{b^2 + 4(b^3 + 1)}}{2} = \frac{b \pm \sqrt{4b^3 + b^2 + 4}}{2}.\]
For $a$ to be an integer, the discriminant $D = 4b^3 + b^2 + 4$ must be a perfect square. We can also rewrite the original equation as:
\[a(a - b) = b^3 + 1 = (b + 1)(b^2 - b + 1).\]
Since $a$ is a prime number, it must divide the product $(b + 1)(b^2 - b + 1)$. By Euclid's Lemma, $a$ must divide either $b + 1$ or $b^2 - b + 1$.

**Case 1: $a$ divides $b^2 - b + 1$.**
Let $b^2 - b + 1 = na$ for some integer $n$. Then we have:
\[a - b = \frac{(b + 1)na}{a} = n(b + 1) \implies a = nb + n + b = (n + 1)b + n.\]
Substituting this expression for $a$ back into $b^2 - b + 1 = na$:
\[b^2 - b + 1 = n((n + 1)b + n) = (n^2 + n)b + n^2 \implies b^2 - (n^2 + n + 1)b + (1 - n^2) = 0.\]
For $b$ to be an integer, the discriminant of this quadratic in $b$ must be a perfect square:
\[D_b = (n^2 + n + 1)^2 - 4(1 - n^2) = n^4 + 2n^3 + 3n^2 + 2n + 1 - 4 + 4n^2 = n^4 + 2n^3 + 7n^2 + 2n - 3.\]
- If $n = 1$, $D_b = 1 + 2 + 7 + 2 - 3 = 9 = 3^2$. Then $b = \frac{3 \pm 3}{2}$, giving $b = 3$ or $b = 0$. Since $b$ is prime, $b = 3$. Then $a = (1 + 1)3 + 1 = 7$, which is prime. This gives the pair $(7, 3)$.
- If $n = 2$, $D_b = 16 + 16 + 28 + 4 - 3 = 61$, not a square.
- For $n \ge 3$, we compare $D_b$ with $(n^2 + n + 2)^2$ and $(n^2 + n + 3)^2$:
  $(n^2 + n + 2)^2 = n^4 + 2n^3 + 5n^2 + 4n + 4$. Then $D_b - (n^2 + n + 2)^2 = 2n^2 - 2n - 7$, which is positive for $n \ge 3$.
  $(n^2 + n + 3)^2 = n^4 + 2n^3 + 7n^2 + 6n + 9$. Then $(n^2 + n + 3)^2 - D_b = 4n + 12$, which is positive for $n \ge 1$.
  Thus, for $n \ge 3$, $(n^2 + n + 2)^2 < D_b < (n^2 + n + 3)^2$, so $D_b$ cannot be a square.
- For $n \le 0$, let $m = -n \ge 0$. $D_b = m^4 - 2m^3 + 7m^2 - 2m - 3$.
  - $m = 0 \implies D_b = -3$.
  - $m = 1 \implies D_b = 1$, giving $b = \frac{1 \pm 1}{2} \in \{0, 1\}$, not prime.
  - $m = 2 \implies D_b = 21$.
  - $m = 3 \implies D_b = 81$, giving $b = \frac{7 \pm 9}{2} \in \{-1, 8\}$, not prime.
  - For $m \ge 4$, we compare $D_b$ with $(m^2 - m + 3)^2$ and $(m^2 - m + 4)^2$:
    $(m^2 - m + 3)^2 = m^4 - 2m^3 + 7m^2 - 6m + 9$. Then $D_b - (m^2 - m + 3)^2 = 4m - 12 > 0$.
    $(m^2 - m + 4)^2 = m^4 - 2m^3 + 9m^2 - 8m + 16$. Then $(m^2 - m + 4)^2 - D_b = 2m^2 - 6m + 19$, which is always positive.
    Thus, $D_b$ cannot be a square for $m \ge 4$.

**Case 2: $a$ divides $b + 1$.**
Let $b + 1 = ma$ for some integer $m$. Then $a - b = m(b^2 - b + 1)$, so $a = m(b^2 - b + 1) + b$.
Substituting $a$ back into $b + 1 = ma$:
\[b + 1 = m(m(b^2 - b + 1) + b) = m^2b^2 - m^2b + m^2 + mb \implies m^2b^2 - (m^2 - m + 1)b + m^2 - 1 = 0.\]
The discriminant of this quadratic in $b$ is:
\[D = (m^2 - m + 1)^2 - 4m^2(m^2 - 1) = -3m^4 - 2m^3 + 7m^2 - 2m + 1.\]
- If $m = 1$, $D = 1$, giving $b \in \{0, 1\}$, not prime.
- If $m = -1$, $D = 9$, giving $b \in \{0, 3\}$. If $b = 3$, $a = -1(9 - 3 + 1) + 3 = -4$, not prime.
- If $m \ge 2$, $D = -3m^4 - 2m^3 + 7m^2 - 2m + 1 < 0$.
- If $m \le -2$, let $k = -m \ge 2$. $D = -3k^4 + 2k^3 + 7k^2 + 2k + 1$.
  - $k = 2 \implies D = -48 + 16 + 28 + 4 + 1 = 1$, giving $b = \frac{7 \pm 1}{8} \in \{1, 0.75\}$, not prime.
  - $k \ge 3 \implies D < 0$.

Thus, the only pair of primes $(a, b)$ that satisfies the equation is $(7, 3)$.

\(\square\)
