# Problem

Find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$.

# Proof A

1: To find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$, we treat the equation as a quadratic in $a$:
2: \[ a^2 - ba - (b^3 + 1) = 0 \]
3: Applying the quadratic formula, we solve for $a$:
4: \[ a = \frac{b \pm \sqrt{b^2 + 4(b^3 + 1)}}{2} = \frac{b \pm \sqrt{4b^3 + b^2 + 4}}{2} \]
5: For $a$ to be an integer, the discriminant $D = 4b^3 + b^2 + 4$ must be a perfect square. Let $D = k^2$ for some integer $k \ge 0$.
6: Considering the equation $k^2 = 4b^3 + b^2 + 4$ modulo $b$, we have:
7: \[ k^2 \equiv 4 \pmod{b} \]
8: This implies $k \equiv 2 \pmod{b}$ or $k \equiv -2 \pmod{b}$. Thus, we can write $k = nb \pm 2$ for some integer $n$. Substituting this back into the equation for $k^2$:
9: \[ (nb \pm 2)^2 = 4b^3 + b^2 + 4 \]
10: \[ n^2b^2 \pm 4nb + 4 = 4b^3 + b^2 + 4 \]
11: \[ n^2b^2 \pm 4nb = 4b^3 + b^2 \]
12: Since $b$ is a prime, $b \neq 0$, so we divide by $b$:
13: \[ n^2b \pm 4n = 4b^2 + b \]
14: Rearranging the terms to isolate the multiple of $b$:
15: \[ b(n^2 - 4b - 1) = \mp 4n \]
16: This equation implies that $b$ must divide $4n$. Since $b$ is prime, this means either $b=2$ or $b$ divides $n$.
17: 
18: **Case 1: $b = 2$**
19: Substituting $b=2$ into the discriminant $D$:
20: \[ D = 4(2^3) + 2^2 + 4 = 32 + 4 + 4 = 40 \]
21: Since 40 is not a perfect square, there are no solutions for $b=2$.
22: 
23: **Case 2: $b$ divides $n$**
24: Let $n = mb$ for some integer $m$. Substituting this into $n^2b \pm 4n = 4b^2 + b$:
25: \[ (mb)^2b \pm 4(mb) = 4b^2 + b \]
26: \[ m^2b^3 \pm 4mb = 4b^2 + b \]
27: Dividing by $b$:
28: \[ m^2b^2 \pm 4m = 4b + 1 \]
29: We analyze the two possible signs:
30: 
31: Subcase 2.1: $m^2b^2 + 4m = 4b + 1$
32: Rearranging as a quadratic in $b$: $m^2b^2 - 4b + (4m - 1) = 0$.
33: Solving for $b$:
34: \[ b = \frac{4 \pm \sqrt{16 - 4m^2(4m - 1)}}{2m^2} = \frac{2 \pm \sqrt{4 - 4m^3 + m^2}}{m^2} \]
35: For $b$ to be a real number, we require $4 - 4m^3 + m^2 \ge 0$.
36: If $m=1$, $b = \frac{2 \pm \sqrt{1}}{1} \in \{3, 1\}$. Since $b$ is prime, $b=3$ is a candidate.
37: If $m \ge 2$, then $4m^3 - m^2 - 4 \ge 32 - 4 - 4 = 24 > 0$, so the discriminant is negative.
38: If $m=0$, the equation $m^2b^2 + 4m = 4b + 1$ becomes $0 = 4b + 1$, which has no prime solutions.
39: If $m < 0$, let $m = -p$ for $p > 0$. The equation $m^2b^2 + 4m = 4b + 1$ becomes $p^2b^2 - 4p = 4b + 1$, which is the case analyzed in Subcase 2.2.
40: 
41: Subcase 2.2: $m^2b^2 - 4m = 4b + 1$
42: Rearranging as a quadratic in $b$: $m^2b^2 - 4b - (4m + 1) = 0$.
43: Solving for $b$:
44: \[ b = \frac{4 \pm \sqrt{16 + 4m^2(4m + 1)}}{2m^2} = \frac{2 \pm \sqrt{4 + 4m^3 + m^2}}{m^2} \]
45: If $m=1$, $b = \frac{2 \pm \sqrt{9}}{1} \in \{5, -1\}$. Since $b$ is prime, $b=5$ is a candidate.
46: If $m=2$, $b = \frac{2 \pm \sqrt{40}}{4}$, which is not an integer.
47: If $m \ge 3$, we check if $b \ge 2$. For $b = \frac{2 + \sqrt{4m^3 + m^2 + 4}}{m^2} \ge 2$, we need:
48: \[ \sqrt{4m^3 + m^2 + 4} \ge 2m^2 - 2 \implies 4m^3 + m^2 + 4 \ge 4m^4 - 8m^2 + 4 \implies 4m^4 - 4m^3 - 9m^2 \le 0 \]
49: Dividing by $m^2$, we get $4m^2 - 4m - 9 \le 0$. The roots of $4m^2 - 4m - 9 = 0$ are $m = \frac{4 \pm \sqrt{160}}{8} = \frac{1 \pm \sqrt{10}}{2}$. Since $\sqrt{10} \approx 3.16$, the inequality holds for $m \le \frac{1 + 3.16}{2} \approx 2.08$. Thus, for $m \ge 3$, $b < 2$, so no prime solutions exist.
50: If $m=0$, the equation $m^2b^2 - 4m = 4b + 1$ becomes $0 = 4b + 1$, which has no prime solutions.
51: If $m < 0$, let $m = -p$ for $p > 0$. The equation $m^2b^2 - 4m = 4b + 1$ becomes $p^2b^2 + 4p = 4b + 1$, which is the case analyzed in Subcase 2.1.
52: 
53: **Testing the candidates $b=3$ and $b=5$:**
54: - For $b=3$:
55:   $a^2 - 3a - 3^3 = 1 \implies a^2 - 3a - 28 = 0 \implies (a-7)(a+4) = 0$.
56:   Since $a$ must be prime, $a=7$. The pair $(7, 3)$ is a solution.
57: - For $b=5$:
58:   $a^2 - 5a - 5^3 = 1 \implies a^2 - 5a - 126 = 0 \implies (a-14)(a+9) = 0$.
59:   Neither $14$ nor $-9$ is prime.
60: 
61: Thus, the only pair of primes $(a, b)$ that satisfies the equation is $(7, 3)$.

# Proof B

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
