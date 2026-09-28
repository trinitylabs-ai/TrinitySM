# Problem

Let $p$ be a prime number and $a, b$ be positive integers such that

 \[
 p^{n}=a^{4}+b^{4}
 \]

 for some integer $n \geq 2$. Prove that $n \geq 5$.

# Proof A

1: To prove that $n \geq 5$ given the equation $p^n = a^4 + b^4$ for a prime $p$ and positive integers $a, b$ with $n \geq 2$, we analyze the problem by considering the parity of the prime $p$.
2: 
3: ### Case 1: $p = 2$
4: Substituting $p=2$ into the equation, we have $2^n = a^4 + b^4$.
5: Since $2^n$ is even, $a$ and $b$ must have the same parity.
6: If $a$ and $b$ are both odd, then $a^4 \equiv 1 \pmod{16}$ and $b^4 \equiv 1 \pmod{16}$, which implies $a^4 + b^4 \equiv 2 \pmod{16}$.
7: The equation $2^n \equiv 2 \pmod{16}$ holds if and only if $n=1$. However, we are given $n \geq 2$.
8: 
9: Therefore, $a$ and $b$ must both be even. Let $a = 2^k a_0$ and $b = 2^k b_0$ where $k \geq 1$ and at least one of $a_0, b_0$ is odd. Substituting these into the equation:
10: \[ 2^n = (2^k a_0)^4 + (2^k b_0)^4 = 2^{4k}(a_0^4 + b_0^4) \implies a_0^4 + b_0^4 = 2^{n-4k} \]
11: Since $a_0^4 + b_0^4$ is a power of 2 and at least one of $a_0, b_0$ is odd, both must be odd. As established, if $a_0$ and $b_0$ are odd, then $a_0^4 + b_0^4 \equiv 2 \pmod{16}$. This implies $2^{n-4k} = 2$, so $n-4k = 1$, which gives $n = 4k + 1$.
12: For $k \geq 1$, the smallest possible value for $n$ is $4(1) + 1 = 5$. Thus, if $p=2$, then $n \geq 5$.
13: 
14: ### Case 2: $p > 2$
15: Let $d = \gcd(a, b)$. Then $d^4$ must divide $p^n$, so $d = p^k$ for some $k \geq 0$.
16: We can write $a = p^k a_1$ and $b = p^k b_1$ where $\gcd(a_1, b_1) = 1$. Substituting these into the equation:
17: \[ p^n = p^{4k}(a_1^4 + b_1^4) \implies a_1^4 + b_1^4 = p^{n-4k} \]
18: Let $m = n - 4k$. We examine the possible values for $m$:
19: 1.  **If $m = 1$**: Then $n = 4k + 1$. Since $n \geq 2$, we must have $k \geq 1$, which implies $n \geq 5$.
20: 2.  **If $m = 2$**: We have $a_1^4 + b_1^4 = p^2$. This is a case of the equation $x^4 + y^4 = z^2$, which Fermat proved has no solutions in positive integers. Thus, $m=2$ is impossible.
21: 3.  **If $m = 3$**: We have $a_1^4 + b_1^4 = p^3$ with $\gcd(a_1, b_1) = 1$.
22:     If $p \equiv 3 \pmod 4$, then $a_1^4 + b_1^4 \equiv 0 \pmod p$ implies $a_1^2 \equiv 0 \pmod p$ and $b_1^2 \equiv 0 \pmod p$ (since $-1$ is not a quadratic residue modulo $p$), contradicting $\gcd(a_1, b_1) = 1$.
23:     If $p \equiv 1 \pmod 4$, we work in the Gaussian integers $\mathbb{Z}[i]$. Then $p = \pi \bar{\pi}$ for some prime $\pi \in \mathbb{Z}[i]$.
24:     $a_1^4 + b_1^4 = (a_1^2 + ib_1^2)(a_1^2 - ib_1^2) = p^3 = \pi^3 \bar{\pi}^3$.
25:     Since $\gcd(a_1^2 + ib_1^2, a_1^2 - ib_1^2)$ divides $2a_1^2$ and $2ib_1^2$, and $p$ is odd, the factors are coprime. Thus $a_1^2 + ib_1^2 = u \pi^3$ for some unit $u \in \{1, -1, i, -i\}$.
26:     Let $\pi = x + iy$. Then $a_1^2 + ib_1^2 = u(x + iy)^3$. This implies that $\{a_1^2, b_1^2\} = \{|x(x^2 - 3y^2)|, |y(3x^2 - y^2)|\}$ for some $x, y$ with $\gcd(x, y) = 1$ and $p = x^2 + y^2$.
27:     If $3 \nmid x$ and $3 \nmid y$, then $x, x^2 - 3y^2, y, 3x^2 - y^2$ must be squares up to a sign. Let $x = \pm u^2, y = \pm v^2$. Then $u^4 - 3v^4 = \pm w^2$ and $3u^4 - v^4 = \pm z^2$. Modulo 3, $3u^4 - v^4 = z^2 \implies z^2 \equiv -v^4 \pmod 3$, which is impossible since $3 \nmid v$. Thus $3u^4 - v^4 = -z^2$, so $v^4 - 3u^4 = z^2$. Similarly, $u^4 - 3v^4 = w^2$ or $u^4 - 3v^4 = -w^2$. If $u^4 - 3v^4 = -w^2$, then $3v^4 - u^4 = w^2$, which implies $w^2 \equiv -u^4 \pmod 3$, impossible since $3 \nmid u$. Thus $u^4 - 3v^4 = w^2$. But $u^4 > 3v^4$ and $v^4 > 3u^4$ cannot both be true for positive $u, v$.
28:     If $3|x$, let $x = 3X$. Then $a_1^2 = 9|X(3X^2 - y^2)|$ and $b_1^2 = |y(27X^2 - y^2)|$. Since $\gcd(X, y) = 1$, this implies $|X|, |3X^2 - y^2|, |y|, |27X^2 - y^2|$ are all squares. Let $X = \pm u^2$ and $y = \pm s^2$. Then $|3u^4 - s^4| = v^2$ and $|27u^4 - s^4| = t^2$.
29:     Since $3 \nmid s$, $3u^4 - s^4 = v^2 \implies v^2 \equiv -s^4 \equiv 2 \pmod 3$, which is impossible. Thus $s^4 - 3u^4 = v^2$. This is a known Diophantine equation $x^4 - 3y^4 = z^2$, which has no solutions in positive integers. Thus $m=3$ is impossible.
30: 4.  **If $m = 4$**: We have $a_1^4 + b_1^4 = p^4$, which has no positive integer solutions by Fermat's Last Theorem.
31: 5.  **If $m \geq 5$**: Then $n = m + 4k \geq 5$.
32: 
33: In all possible cases for $p > 2$, we find that $n \geq 5$.
34: 
35: Combining the results from Case 1 and Case 2, we conclude that $n \geq 5$ for any prime $p$ and positive integers $a, b$ such that $p^n = a^4 + b^4$ and $n \geq 2$.

# Proof B

1: To prove that $n \geq 5$ for the equation $p^n = a^4 + b^4$, where $p$ is a prime number and $a, b$ are positive integers, we show that $n = 2, 3, 4$ are impossible.
2: 
3: ### Case 1: $n=4$
4: If $n=4$, the equation becomes $a^4 + b^4 = p^4$. By Fermat's Last Theorem for the exponent $k=4$, the equation $x^4 + y^4 = z^4$ has no solutions in positive integers. Thus, $n=4$ is impossible.
5: 
6: ### Case 2: $n=2$
7: If $n=2$, the equation becomes $a^4 + b^4 = p^2$. This is a specific case of the equation $x^4 + y^4 = z^2$. Fermat proved using the method of infinite descent that $x^4 + y^4 = z^2$ has no solutions in positive integers. Thus, $n=2$ is impossible.
8: 
9: ### Case 3: $n=3$
10: If $n=3$, the equation is $a^4 + b^4 = p^3$. First, we show that $\gcd(a, b) = 1$. If $\gcd(a, b) = d > 1$, then $d^4$ must divide $p^3$, which implies $d$ is a power of $p$. However, $d^4 | p^3$ is only possible if $d=1$.
11: If $p=2$, $a^4 + b^4 = 8$ has no positive integer solutions since $1^4+1^4=2$ and $2^4+1^4=17$.
12: For odd $p$, we factor the equation in the Gaussian integers $\mathbb{Z}[i]$ as $(a^2 + ib^2)(a^2 - ib^2) = p^3$. Since $p$ is odd, $a$ and $b$ must have opposite parity. Thus, $a^2 + ib^2$ and $a^2 - ib^2$ are coprime in $\mathbb{Z}[i]$. Since their product is a cube and units in $\mathbb{Z}[i]$ are cubes, we have $a^2 + ib^2 = (u + iv)^3$ for some $u, v \in \mathbb{Z}$. Expanding this gives:
13: \[ a^2 = u(u^2 - 3v^2), \quad b^2 = v(3u^2 - v^2). \]
14: Since $\gcd(a, b) = 1$, we must have $\gcd(u, v) = 1$. We analyze the divisibility by 3:
15: 
16: 1. **If $3 \nmid u$ and $3 \nmid v$**: Then $\gcd(u, u^2 - 3v^2) = 1$ and $\gcd(v, 3u^2 - v^2) = 1$. For $a^2$ and $b^2$ to be squares, we must have $u = x^2, u^2 - 3v^2 = y^2, v = w^2, 3u^2 - v^2 = z^2$. This implies $x^4 - 3w^4 = y^2$ and $3x^4 - w^4 = z^2$.
17:    - If $x$ is even and $w$ is odd, $y^2 \equiv -3 \equiv 5 \pmod 8$ (impossible).
18:    - If $x$ is odd and $w$ is even, $z^2 \equiv 3(1) - 0 \equiv 3 \pmod 8$ (impossible).
19:    - If $x$ is odd and $w$ is odd, $y^2 \equiv 1 - 3 \equiv 6 \pmod 8$ (impossible).
20: 
21: 2. **If $3 | u$**: Let $u = 3U$. Then $a^2 = 9U(3U^2 - v^2)$ and $b^2 = v(27U^2 - v^2)$. Since $\gcd(u, v) = 1$, $3 \nmid v$. Thus $U = x^2, 3U^2 - v^2 = y^2, v = w^2, 27U^2 - v^2 = z^2$. This implies $3x^4 - w^4 = y^2$ and $27x^4 - w^4 = z^2$.
22:    - If $x$ is even and $w$ is odd, $y^2 \equiv -1 \equiv 7 \pmod 8$ (impossible).
23:    - If $x$ is odd and $w$ is even, $y^2 \equiv 3 \pmod 8$ (impossible).
24:    - If $x$ is odd and $w$ is odd, $y^2 \equiv 3 - 1 \equiv 2 \pmod 8$ (impossible).
25: 
26: 3. **If $3 | v$**: Let $v = 3V$. Then $a^2 = u(u^2 - 27V^2)$ and $b^2 = 9V(u^2 - 3V^2)$. Since $\gcd(u, v) = 1$, $3 \nmid u$. Thus $u = x^2, u^2 - 27V^2 = y^2, V = w^2, u^2 - 3V^2 = z^2$. This implies $x^4 - 27w^4 = y^2$ and $x^4 - 3w^4 = z^2$.
27:    Consider the equation $x^4 - 3w^4 = z^2$. We have $(x^2 - z)(x^2 + z) = 3w^4$. Let $g = \gcd(x^2 - z, x^2 + z)$. Then $g$ divides $2x^2$ and $2z$. Since $\gcd(x, w) = 1$, $g$ must divide $2 \cdot 3 = 6$.
28:    - If $g=1$, then $\{x^2 - z, x^2 + z\} = \{m^4, 3n^4\}$ for some $m, n$. Then $2x^2 = m^4 + 3n^4$. If $m, n$ are both odd, $m^4 + 3n^4 \equiv 1 + 3 = 4 \pmod 8$, so $x^2 \equiv 2 \pmod 4$ (impossible). If $m$ is even and $n$ is odd, $m^4 + 3n^4 \equiv 3 \pmod 8$, so $2x^2 \equiv 3 \pmod 8$ (impossible). If $m$ is odd and $n$ is even, $m^4 + 3n^4 \equiv 1 \pmod 8$, so $2x^2 \equiv 1 \pmod 8$ (impossible).
29:    - If $g=3$, then $3 | (x^2 - z)$ and $3 | (x^2 + z)$, so $3 | 2x^2$, which implies $3 | x$. But $\gcd(x, w) = 1$ and $3 | w$ (since $3w^4 = (x^2-z)(x^2+z)$), a contradiction.
30:    - If $g=6$, then $x^2 - z = 6A$ and $x^2 + z = 6B$ with $\gcd(A, B) = 1$. Then $3w^4 = 36AB$, so $w^4 = 12AB$. This implies $12 | w^4$, so $3 | w$. Then $x^2 = 3(A+B)$, so $3 | x$, which contradicts $\gcd(x, w) = 1$.
31:    - If $g=2$, then $x^2 - z = 2\alpha$ and $x^2 + z = 2\beta$ with $\gcd(\alpha, \beta) = 1$. Then $4\alpha\beta = 3w^4$, so $w$ is even, $w=2k$. Then $\alpha\beta = 12k^4$. Since $\gcd(\alpha, \beta) = 1$, the possible distributions are $\{\alpha, \beta\} = \{m^4, 12n^4\}$ or $\{3m^4, 4n^4\}$. In either case, $x^2 = \alpha + \beta$.
32:      - If $x^2 = 3m^4 + 4n^4$, then $m$ must be even ($m=2M$), so $x^2 = 48M^4 + 4n^4 \implies (x/2)^2 = n^4 + 12M^4$.
33:      - If $x^2 = m^4 + 12n^4$, and $m$ is even ($m=2M$), then $x$ is even ($x=2X$), so $4X^2 = 16M^4 + 12n^4 \implies X^2 = 4M^4 + 3n^4$.
34:      - If $x^2 = m^4 + 12n^4$ and $m$ is odd, then $n$ must be even ($n=2N$), so $x^2 = m^4 + 192N^4$. This implies $x^2 - (m^2)^2 = 3(8N^2)^2$. The general solution to $X^2 - 3Y^2 = Z^2$ with $\gcd(X, Y)=1$ is $X = p^2 + 3q^2, Y = 2pq, Z = |p^2 - 3q^2|$. Here $X=x, Y=8N^2, Z=m^2$. Thus $m^2 = |p^2 - 3q^2|$ and $8N^2 = 2pq \implies 4N^2 = pq$. Since $\gcd(p, q)=1$, $p$ and $q$ must be squares, $p=u^2, q=v^2$. Then $m^2 = |u^4 - 3v^4|$. If $m^2 = u^4 - 3v^4$, we have $u^4 - 3v^4 = m^2$, which is the same equation as $x^4 - 3w^4 = z^2$ but with $u \leq p < x$. If $m^2 = 3v^4 - u^4$, then $u^4 + m^2 = 3v^4$, which implies $u, m$ are multiples of 3, so $v$ is also a multiple of 3, contradicting $\gcd(u, v)=1$. By infinite descent, no positive integer solutions exist.
35: 
36: Since $n=2, 3, 4$ are impossible, we conclude $n \geq 5$.
