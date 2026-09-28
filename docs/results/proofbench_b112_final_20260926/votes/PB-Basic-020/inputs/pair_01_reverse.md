# Problem

Find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$.

# Proof A

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

# Proof B

1: To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we begin by rearranging the equation to isolate the terms involving $a$:
2: \[ a^2 - ab = b^3 + 1 \]
3: Factoring the right side as a sum of cubes, we have:
4: \[ a(a - b) = (b+1)(b^2 - b + 1) \]
5: Alternatively, we can rearrange the original equation as:
6: \[ a^2 - 1 = b^3 + ab \]
7: Factoring the left side and the right side:
8: \[ (a-1)(a+1) = b(b^2 + a) \]
9: Since $b$ is a prime number, by Euclid's Lemma, $b$ must divide at least one of the factors on the left side. This implies that $b \mid (a-1)$ or $b \mid (a+1)$. We analyze these two cases separately.
10: 
11: **Case 1: $b \mid (a-1)$**
12: Let $a-1 = nb$ for some integer $n \ge 1$. Then $a = nb + 1$. Substituting this into the original equation:
13: \[ (nb+1)^2 - (nb+1)b - b^3 = 1 \]
14: \[ n^2b^2 + 2nb + 1 - nb^2 - b - b^3 = 1 \]
15: \[ -b^3 + (n^2-n)b^2 + (2n-1)b = 0 \]
16: Since $b$ is a prime, $b \neq 0$, so we divide by $b$:
17: \[ -b^2 + (n^2-n)b + (2n-1) = 0 \implies b^2 + (n-n^2)b + (1-2n) = 0 \]
18: Using the quadratic formula to solve for $b$:
19: \[ b = \frac{(n^2-n) \pm \sqrt{(n-n^2)^2 - 4(1-2n)}}{2} = \frac{n^2-n \pm \sqrt{n^4 - 2n^3 + n^2 + 8n - 4}}{2} \]
20: For $b$ to be an integer, the discriminant $m^2 = n^4 - 2n^3 + n^2 + 8n - 4$ must be a perfect square.
21: - If $n=1$, $m^2 = 1-2+1+8-4 = 4 = 2^2$. Then $b = \frac{0 \pm 2}{2} = \pm 1$, which is not prime.
22: - If $n=2$, $m^2 = 16-16+4+16-4 = 16 = 4^2$. Then $b = \frac{2 \pm 4}{2}$, giving $b=3$ or $b=-1$. For $b=3$, we have $a = 2(3)+1 = 7$. Since both $a=7$ and $b=3$ are prime, $(7, 3)$ is a solution.
23: - If $n=3$, $m^2 = 81-54+9+24-4 = 56$, not a square.
24: - If $n=4$, $m^2 = 256-128+16+32-4 = 172$, not a square.
25: - If $n \ge 5$, we observe that $(n^2-n)^2 = n^4 - 2n^3 + n^2 < m^2$. Also, $(n^2-n+1)^2 = n^4 - 2n^3 + 3n^2 - 2n + 1$. The difference $(n^2-n+1)^2 - m^2 = 2n^2 - 10n + 5$ is positive for $n \ge 5$. Thus, $(n^2-n)^2 < m^2 < (n^2-n+1)^2$, meaning $m^2$ cannot be a perfect square.
26: 
27: **Case 2: $b \mid (a+1)$**
28: Let $a+1 = nb$ for some integer $n \ge 1$. Then $a = nb - 1$. Substituting this into the original equation:
29: \[ (nb-1)^2 - (nb-1)b - b^3 = 1 \]
30: \[ n^2b^2 - 2nb + 1 - nb^2 + b - b^3 = 1 \]
31: \[ -b^3 + (n^2-n)b^2 + (1-2n)b = 0 \]
32: Dividing by $b$:
33: \[ -b^2 + (n^2-n)b + (1-2n) = 0 \implies b^2 + (n-n^2)b + (2n-1) = 0 \]
34: Solving for $b$:
35: \[ b = \frac{(n^2-n) \pm \sqrt{(n-n^2)^2 - 4(2n-1)}}{2} = \frac{n^2-n \pm \sqrt{n^4 - 2n^3 + n^2 - 8n + 4}}{2} \]
36: Let $m^2 = n^4 - 2n^3 + n^2 - 8n + 4$.
37: - If $n=1$, $m^2 = 1-2+1-8+4 = -4$.
38: - If $n=2$, $m^2 = 16-16+4-16+4 = -8$.
39: - If $n=3$, $m^2 = 81-54+9-24+4 = 16 = 4^2$. Then $b = \frac{6 \pm 4}{2}$, giving $b=5$ or $b=1$. For $b=5$, we have $a = 3(5)-1 = 14$, which is not prime.
40: - If $n=4$, $m^2 = 256-128+16-32+4 = 116$, not a square.
41: - If $n \ge 5$, we observe that $m^2 < (n^2-n)^2$ because $m^2 - (n^2-n)^2 = -8n+4 < 0$. Also, $(n^2-n-1)^2 = n^4 - 2n^3 - n^2 + 2n + 1$. The difference $m^2 - (n^2-n-1)^2 = 2n^2 - 10n + 3$ is positive for $n \ge 5$. Thus, $(n^2-n-1)^2 < m^2 < (n^2-n)^2$, meaning $m^2$ cannot be a perfect square.
42: 
43: Checking the solution $(7, 3)$: $7^2 - 7(3) - 3^3 = 49 - 21 - 27 = 1$. This is correct.
44: 
45: The only pair of primes $(a, b)$ that satisfies the equation is $(7, 3)$.
46: 
47: \(\square\)
