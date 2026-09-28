# Problem

Find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$.

# Proof A

1: To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we rearrange the equation as:
2: \[ a(a - b) = b^3 + 1 = (b + 1)(b^2 - b + 1) \]
3: Since $a$ is a prime number, $a$ must divide the product $(b + 1)(b^2 - b + 1)$. By Euclid's Lemma, $a$ must divide either $b + 1$ or $b^2 - b + 1$.
4: 
5: **Case 1: $a$ divides $b + 1$**
6: Let $b + 1 = na$ for some positive integer $n$. Substituting this into the factored equation:
7: \[ a(a - b) = na(b^2 - b + 1) \implies a - b = n(b^2 - b + 1) \implies a = n(b^2 - b + 1) + b \]
8: Substituting $a = \frac{b + 1}{n}$ into this expression:
9: \[ \frac{b + 1}{n} = n(b^2 - b + 1) + b \implies b + 1 = n^2b^2 - n^2b + n^2 + nb \]
10: Rearranging this into a quadratic in $b$:
11: \[ n^2b^2 + (n - n^2 - 1)b + (n^2 - 1) = 0 \]
12: For $b$ to be an integer, the discriminant $D_n$ must be a perfect square:
13: \[ D_n = (n - n^2 - 1)^2 - 4n^2(n^2 - 1) = (n^2 - n + 1)^2 - 4n^4 + 4n^2 \]
14: \[ D_n = (n^4 + n^2 + 1 - 2n^3 + 2n^2 - 2n) - 4n^4 + 4n^2 = -3n^4 - 2n^3 + 7n^2 - 2n + 1 \]
15: If $n = 1$, $D_1 = -3 - 2 + 7 - 2 + 1 = 1$. The values for $b$ are $b = \frac{-(1 - 1 - 1) \pm 1}{2(1)^2} = \frac{1 \pm 1}{2}$, so $b = 1$ or $b = 0$, neither of which is prime.
16: If $n = 2$, $D_2 = -3(16) - 2(8) + 7(4) - 2(2) + 1 = -48 - 16 + 28 - 4 + 1 = -39 < 0$.
17: For $n \ge 2$, let $f(n) = -3n^4 - 2n^3 + 7n^2 - 2n + 1$. Its derivative $f'(n) = -12n^3 - 6n^2 + 14n - 2 = -2(6n^3 + 3n^2 - 7n + 1)$. For $n \ge 1$, the term $g(n) = 6n^3 + 3n^2 - 7n + 1$ is positive since $g(1) = 3$ and $g'(n) = 18n^2 + 6n - 7 > 0$. Thus $f'(n) < 0$ for $n \ge 1$, and since $f(2) < 0$, we have $D_n < 0$ for all $n \ge 2$.
18: Thus, Case 1 yields no solutions.
19: 
20: **Case 2: $a$ divides $b^2 - b + 1$**
21: Let $b^2 - b + 1 = ma$ for some positive integer $m$. Substituting this into the factored equation:
22: \[ a(a - b) = (b + 1)ma \implies a - b = m(b + 1) \implies a = (m + 1)b + m \]
23: Now substitute this expression for $a$ back into $b^2 - b + 1 = ma$:
24: \[ b^2 - b + 1 = m((m + 1)b + m) = (m^2 + m)b + m^2 \]
25: \[ b^2 - (m^2 + m + 1)b + (1 - m^2) = 0 \]
26: For $b$ to be an integer, the discriminant $D_m$ must be a perfect square:
27: \[ D_m = (m^2 + m + 1)^2 - 4(1 - m^2) = m^4 + 2m^3 + 3m^2 + 2m + 1 - 4 + 4m^2 = m^4 + 2m^3 + 7m^2 + 2m - 3 \]
28: We bound $D_m$ between two consecutive squares for $m \ge 3$:
29: 1. $(m^2 + m + 2)^2 = m^4 + 2m^3 + 5m^2 + 4m + 4$.
30:    $D_m - (m^2 + m + 2)^2 = 2m^2 - 2m - 7$. For $m \ge 3$, $2m^2 - 2m - 7 \ge 2(9) - 6 - 7 = 5 > 0$.
31: 2. $(m^2 + m + 3)^2 = m^4 + 2m^3 + 7m^2 + 6m + 9$.
32:    $(m^2 + m + 3)^2 - D_m = 4m + 12$, which is clearly positive for $m \ge 1$.
33: 
34: Since $(m^2 + m + 2)^2 < D_m < (m^2 + m + 3)^2$ for $m \ge 3$, $D_m$ cannot be a perfect square for $m \ge 3$. We only need to check $m = 1$ and $m = 2$:
35: - If $m = 1$, $D_1 = 1 + 2 + 7 + 2 - 3 = 9 = 3^2$.
36:   Then $b = \frac{(1+1+1) \pm 3}{2} = \frac{3 \pm 3}{2}$, so $b = 3$ or $b = 0$.
37:   Since $b$ must be prime, $b = 3$. Then $a = (1+1)3 + 1 = 7$, which is prime.
38: - If $m = 2$, $D_2 = 16 + 16 + 28 + 4 - 3 = 61$, which is not a perfect square.
39: 
40: Checking the solution $(7, 3)$: $7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$.
41: 
42: The only pair of primes $(a, b)$ that satisfies the equation is $(7, 3)$.

# Proof B

1: To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we rewrite the equation as:
2: \[a(a - b) = b^3 + 1 = (b + 1)(b^2 - b + 1)\]
3: Since $a$ is prime, $a$ must divide the product $(b + 1)(b^2 - b + 1)$. By Euclid's Lemma, $a$ must divide $b + 1$ or $a$ must divide $b^2 - b + 1$.
4: 
5: **Case 1: $a$ divides $b^2 - b + 1$**
6: Let $b^2 - b + 1 = ma$ for some integer $m$. Since $b$ is a prime, $b \ge 2$, so $b^2 - b + 1 > 0$. Since $a$ is a prime, $a > 0$, so $m$ must be a positive integer. Substituting $ma$ for $b^2 - b + 1$ in the original factored equation:
7: \[a(a - b) = (b + 1)ma\]
8: Dividing by $a$ (since $a \neq 0$):
9: \[a - b = m(b + 1) \implies a = (m + 1)b + m\]
10: Substitute this expression for $a$ back into $b^2 - b + 1 = ma$:
11: \[b^2 - b + 1 = m((m + 1)b + m) = (m^2 + m)b + m^2\]
12: Rearranging gives a quadratic equation in $b$:
13: \[b^2 - (m^2 + m + 1)b + (1 - m^2) = 0\]
14: The discriminant of this quadratic is:
15: \[D_m = (m^2 + m + 1)^2 - 4(1 - m^2) = m^4 + 2m^3 + 3m^2 + 2m + 1 - 4 + 4m^2 = m^4 + 2m^3 + 7m^2 + 2m - 3\]
16: We determine when $D_m$ is a perfect square for $m \in \mathbb{Z}^+$:
17: 1. If $m = 1$, $D_1 = 1 + 2 + 7 + 2 - 3 = 9 = 3^2$. The solutions for $b$ are $b = \frac{3 \pm 3}{2}$, so $b = 3$ or $b = 0$. Since $b$ must be prime, $b = 3$. Then $a = (1 + 1)3 + 1 = 7$, which is prime. This gives the pair $(7, 3)$.
18: 2. If $m = 2$, $D_2 = 16 + 16 + 28 + 4 - 3 = 61$, which is not a square.
19: 3. If $m \ge 3$, we compare $D_m$ to $(m^2 + m + 2)^2$ and $(m^2 + m + 3)^2$:
20:    - $D_m - (m^2 + m + 2)^2 = (m^4 + 2m^3 + 7m^2 + 2m - 3) - (m^4 + 2m^3 + 5m^2 + 4m + 4) = 2m^2 - 2m - 7$. For $m \ge 3$, $2m^2 - 2m - 7 \ge 18 - 6 - 7 = 5 > 0$.
21:    - $(m^2 + m + 3)^2 - D_m = (m^4 + 2m^3 + 7m^2 + 6m + 9) - (m^4 + 2m^3 + 7m^2 + 2m - 3) = 4m + 12 > 0$.
22:    Thus, for $m \ge 3$, $D_m$ lies strictly between two consecutive squares and cannot be a square.
23: 
24: **Case 2: $a$ divides $b + 1$**
25: Let $b + 1 = na$ for some integer $n$. Since $a, b$ are primes, $n$ must be a positive integer. Substituting $na$ for $b + 1$ in the original factored equation:
26: \[a(a - b) = na(b^2 - b + 1)\]
27: Dividing by $a$:
28: \[a - b = n(b^2 - b + 1) \implies a = nb^2 - nb + n + b\]
29: Substitute $a = \frac{b + 1}{n}$ into this expression:
30: \[\frac{b + 1}{n} = nb^2 - nb + n + b \implies b + 1 = n^2b^2 - n^2b + n^2 + nb\]
31: Rearranging gives a quadratic equation in $b$:
32: \[n^2b^2 - (n^2 - n + 1)b + (n^2 - 1) = 0\]
33: The discriminant of this quadratic is:
34: \[D_n = (n^2 - n + 1)^2 - 4n^2(n^2 - 1) = (n^4 + n^2 + 1 - 2n^3 + 2n^2 - 2n) - 4n^4 + 4n^2 = -3n^4 - 2n^3 + 7n^2 - 2n + 1\]
35: For $b$ to be a real number, we require $D_n \ge 0$.
36: - If $n = 1$, $D_1 = -3 - 2 + 7 - 2 + 1 = 1 = 1^2$. The solutions for $b$ are $b = \frac{(1-1+1) \pm 1}{2(1)^2} = \frac{1 \pm 1}{2}$, so $b = 1$ or $b = 0$, neither of which is prime.
37: - If $n \ge 2$, we have $D_n = n^2(-3n^2 - 2n + 7) - 2n + 1$. For $n = 2$, $-3n^2 - 2n + 7 = -12 - 4 + 7 = -9$. For $n > 2$, this expression is even more negative. Thus $D_n < 0$ for all $n \ge 2$.
38: 
39: Therefore, Case 2 yields no solutions.
40: 
41: The only pair of primes is $(7, 3)$.
42: Verification: $7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$.
