# Problem

Find all pairs of primes $(a, b)$ such that $a^2 - ab - b^3 = 1$.

# Proof A

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

# Proof B

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
