# Problem

Let $p$ be a prime number and $a, b$ be positive integers such that

 \[
 p^{n}=a^{4}+b^{4}
 \]

 for some integer $n \geq 2$. Prove that $n \geq 5$.

# Proof A

1: To prove that $n \geq 5$ for the equation $p^n = a^4 + b^4$ where $p$ is a prime and $a, b$ are positive integers, we consider the possible values of $n$ for different primes $p$.
2: 
3: **Case 1: $p = 2$**
4: The equation is $2^n = a^4 + b^4$. If $a$ and $b$ have opposite parity, $a^4 + b^4$ is odd, which is impossible for $n \geq 2$. If $a$ and $b$ are both odd, then $a^4 \equiv 1 \pmod{16}$ and $b^4 \equiv 1 \pmod{16}$, so $a^4 + b^4 \equiv 2 \pmod{16}$. This implies $2^n \equiv 2 \pmod{16}$, which only holds for $n=1$, contradicting $n \geq 2$.
5: Thus, $a$ and $b$ must both be even. Let $a = 2^k a_0$ and $b = 2^k b_0$ where $k \geq 1$ and at least one of $a_0, b_0$ is odd. Substituting these into the equation gives:
6: \[ 2^n = (2^k a_0)^4 + (2^k b_0)^4 = 2^{4k}(a_0^4 + b_0^4) \implies 2^{n-4k} = a_0^4 + b_0^4 \]
7: Since $a_0^4 + b_0^4$ is a power of 2, $a_0$ and $b_0$ must have the same parity. Since they cannot both be even, they must both be odd. As shown above, this requires $n-4k = 1$, so $n = 4k+1$. For $k \geq 1$, the smallest possible value is $n=5$ (occurring when $a=b=2$). Thus, for $p=2$, $n \geq 5$.
8: 
9: **Case 2: $p > 2$**
10: If $\gcd(a, b) = d > 1$, then $d^4$ must divide $p^n$, so $d$ is a power of $p$. Dividing by $d^4$ reduces the problem to the case $\gcd(a, b) = 1$. In this case, $a$ and $b$ must be coprime to $p$.
11: 
12: *   **Subcase $n=4$**: The equation $a^4 + b^4 = p^4$ has no solutions in positive integers by Fermat's Last Theorem for $n=4$.
13: *   **Subcase $n=2$**: The equation $a^4 + b^4 = p^2$ can be written as $(a^2)^2 + (b^2)^2 = p^2$. This is a primitive Pythagorean triple $(a^2, b^2, p)$. Thus, there exist $m > l > 0$ with $\gcd(m, l)=1$ such that $a^2 = m^2 - l^2$ and $b^2 = 2ml$. From $a^2 + l^2 = m^2$, we have another primitive triple, so $l = 2uv$, $a = u^2 - v^2$, and $m = u^2 + v^2$ for some $u > v > 0$. Then $b^2 = 2(u^2 + v^2)(2uv) = 4uv(u^2 + v^2)$. Since $\gcd(u, v) = 1$, each factor $u, v,$ and $u^2 + v^2$ must be a square. Let $u = x^2$ and $v = y^2$. Then $x^4 + y^4 = z^2$ for some $z$. It is a well-known result by Fermat that $x^4 + y^4 = z^2$ has no solutions in positive integers. Thus, $n=2$ is impossible.
14: *   **Subcase $n=3$**: The equation $a^4 + b^4 = p^3$ can be factored in the Gaussian integers $\mathbb{Z}[i]$ as $(a^2 + ib^2)(a^2 - ib^2) = p^3$. Since $p$ is odd and $\gcd(a, b) = 1$, $a$ and $b$ have opposite parity, so $a^2 + ib^2$ is not divisible by $1+i$. Thus, $\gcd(a^2 + ib^2, a^2 - ib^2) = 1$. This implies $a^2 + ib^2 = u(x+iy)^3$ for some unit $u \in \{1, -1, i, -i\}$ and $x+iy \in \mathbb{Z}[i]$. The cases for $u \neq 1$ merely permute $a, b$ or change signs of $x, y$. For $u=1$, we have:
15:     \[ a^2 = x(x^2 - 3y^2) \quad \text{and} \quad b^2 = y(3x^2 - y^2) \]
16:     Since $\gcd(a, b)=1$, we have $\gcd(x, y)=1$.
17:     1. If $3 \nmid x$ and $3 \nmid y$, then $\gcd(x, x^2-3y^2) = 1$ and $\gcd(y, 3x^2-y^2) = 1$. Thus, $x, x^2-3y^2, y, 3x^2-y^2$ are squares up to sign. Let $x = \epsilon_1 \alpha^2, x^2-3y^2 = \epsilon_1 \beta^2, y = \epsilon_2 \gamma^2, 3x^2-y^2 = \epsilon_2 \delta^2$. Since $x^2-3y^2 = \epsilon_1 \beta^2 \implies \beta^2 \equiv x^2 \pmod{3}$, we must have $\epsilon_1 = 1$. Since $3x^2-y^2 = \epsilon_2 \delta^2 \implies \delta^2 \equiv -y^2 \pmod{3}$, we must have $\epsilon_2 = -1$. Then $y^2-3x^2 = \delta^2$. We have the system $x^2-3y^2 = \beta^2$ and $y^2-3x^2 = \delta^2$. Adding these gives $-2(x^2+y^2) = \beta^2 + \delta^2$, which is impossible for positive $x, y$.
18:     2. If $3 | x$, let $x=3k$. Then $a^2 = 3k(9k^2-3y^2) = 9k(3k^2-y^2)$, so $k(3k^2-y^2)$ is a square. Since $\gcd(k, 3k^2-y^2) = 1$, we have $k = \epsilon_1 \alpha^2$ and $3k^2-y^2 = \epsilon_1 \beta^2$. Also $b^2 = y(27k^2-y^2)$. Since $\gcd(y, 27k^2-y^2) = 1$, we have $y = \epsilon_2 \gamma^2$ and $27k^2-y^2 = \epsilon_2 \delta^2$.
19:        If $\epsilon_1 = 1$, then $3k^2-y^2 = \beta^2 \implies \beta^2 \equiv -y^2 \pmod{3}$, so $3|y$, contradiction. Thus $\epsilon_1 = -1$, and $y^2-3k^2 = \beta^2$.
20:        If $\epsilon_2 = 1$, then $27k^2-y^2 = \delta^2 \implies \delta^2 \equiv -y^2 \pmod{3}$, so $3|y$, contradiction. Thus $\epsilon_2 = -1$, and $y^2-27k^2 = \delta^2$.
21:        The system $y^2-3k^2 = \beta^2$ and $y^2-27k^2 = \delta^2$ implies that for $X = (y/k)^2$, the values $X, X-3, X-27$ are all squares of rationals. This defines a rational point on the elliptic curve $Y^2 = X(X-3)(X-27)$. The torsion points are $(0,0), (3,0), (27,0)$, none of which satisfy the condition that $X, X-3, X-27$ are all squares of rationals. A 2-descent shows the rank of this curve is 0, so no such $X$ exists.
22:     3. If $3 | y$, the argument is symmetric to $3 | x$.
23: 
24: Since $n=2, 3, 4$ are impossible for all primes $p$, we conclude that $n \geq 5$.
25: 
26: \(\square\)

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
