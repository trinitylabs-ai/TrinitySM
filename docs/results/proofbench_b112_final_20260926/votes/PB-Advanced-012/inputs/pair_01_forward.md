# Problem

Let $p$ be a prime number and $a, b$ be positive integers such that

 \[
 p^{n}=a^{4}+b^{4}
 \]

 for some integer $n \geq 2$. Prove that $n \geq 5$.

# Proof A

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

# Proof B

1: To prove that $n \geq 5$ for the equation $p^n = a^4 + b^4$, where $p$ is a prime and $a, b$ are positive integers, we analyze the constraints on $n \geq 2$.
2: 
3: **1. Parity of $n$**
4: If $n$ is even, let $n = 2k$ for some integer $k \geq 1$. The equation becomes $a^4 + b^4 = (p^k)^2$. According to Fermat's Theorem on the equation $x^4 + y^4 = z^2$, there are no solutions in positive integers. Thus, $n$ must be odd. Since $n \geq 2$, we have $n \in \{3, 5, 7, \dots\}$.
5: 
6: **2. The Case $n=3$**
7: Suppose $n=3$, so $p^3 = a^4 + b^4$. Let $d = \gcd(a, b)$. Then $a = dA$ and $b = dB$ with $\gcd(A, B) = 1$. The equation is:
8: \[ p^3 = d^4(A^4 + B^4) \]
9: Since $p$ is prime, $d$ must be a power of $p$. If $d = p^k$ for $k \geq 1$, then $d^4 \geq p^4$, implying $p^3 \geq p^4(A^4 + B^4)$, which is impossible since $A^4 + B^4 \geq 2$. Thus, $d = 1$, and we must have $p^3 = A^4 + B^4$ with $\gcd(A, B) = 1$.
10: 
11: If $p=2$, then $A^4 + B^4 = 8$, which implies $A=B=1$ (since $2^4 > 8$). However, $1^4 + 1^4 = 2 \neq 8$. Thus, $p$ must be an odd prime.
12: Since $p$ is odd, $A$ and $B$ must have opposite parity. Assume $A$ is odd and $B$ is even. We factor the equation in the Gaussian integers $\mathbb{Z}[i]$:
13: \[ (A^2 + iB^2)(A^2 - iB^2) = p^3 \]
14: The greatest common divisor $\delta = \gcd(A^2 + iB^2, A^2 - iB^2)$ divides $2A^2$ and $2iB^2$. Since $A^2 + iB^2$ is odd, $\delta$ must be a unit. Thus, $A^2 + iB^2$ is a cube (up to a unit) in $\mathbb{Z}[i]$. Since all units in $\mathbb{Z}[i]$ are cubes, we have:
15: \[ A^2 + iB^2 = (x + iy)^3 = (x^3 - 3xy^2) + i(3x^2y - y^3) \]
16: Equating real and imaginary parts:
17: 1) $A^2 = x(x^2 - 3y^2)$
18: 2) $B^2 = y(3x^2 - y^2)$
19: Given $\gcd(A, B) = 1$, we have $\gcd(x, y) = 1$. From (1), $\gcd(x, x^2 - 3y^2) = \gcd(x, 3)$.
20: 
21: **Case 1: $\gcd(x, 3) = 1$.**
22: Then $x = u^2$ and $x^2 - 3y^2 = v^2$. From (2), $B^2 = y(3u^4 - y^2)$. Since $\gcd(x, y) = 1$, $\gcd(y, 3u^4 - y^2) = \gcd(y, 3)$.
23: - If $\gcd(y, 3) = 1$, then $y$ and $3u^4 - y^2$ are both squares. Let $y = s^2$. Then $3u^4 - s^4 = t^2$. Modulo 3, this gives $t^2 \equiv -s^4 \equiv 2 \pmod 3$, which is impossible.
24: - If $\gcd(y, 3) = 3$, let $y = 3s^2$. Then $B^2 = 3s^2(3u^4 - 9s^4) = 9s^2(u^4 - 3s^4)$, so $u^4 - 3s^4 = t^2$.
25: We analyze $u^4 - 3s^4 = t^2$ with $\gcd(u, s) = 1$.
26: If $u$ is odd and $s$ is even, then $t$ is odd. $(u^2 - t)(u^2 + t) = 3s^4$. Let $\gcd(u, t) = g$. Then $g$ divides $3s^4$, and since $\gcd(u, s) = 1$, $g$ must be 1 or 3. If $g=3$, then $3|u$ and $3|t$, so $81U^4 - 9T^2 = 3s^4 \implies 27U^4 - 3T^2 = s^4$, implying $3|s$, contradicting $\gcd(u, s)=1$. If $g=1$, then $\gcd(u^2 - t, u^2 + t) = 2$. Thus $\{u^2 - t, u^2 + t\} = \{2m^4, 6n^4\}$ or $\{6m^4, 2n^4\}$. In either case, $s^4 = \frac{(u^2 - t)(u^2 + t)}{3} = 4m^4n^4$, so $s^2 = 2m^2n^2$, which is impossible for $m, n \neq 0$.
27: If $u$ is even and $s$ is odd, then $t$ is odd. $(u^2 - t)(u^2 + t) = 3s^4$. Since $u^2 - t$ is odd, $\gcd(u^2 - t, u^2 + t) = \gcd(u^2 - t, u^2)$. Any prime dividing this gcd must divide $u$ and $t$, and thus divide $3s^4$, so it must be 3. If $3 \nmid u$, then $\gcd(u^2 - t, u^2 + t) = 1$, so $\{u^2 - t, u^2 + t\} = \{m^4, 3n^4\}$ or $\{3m^4, n^4\}$. Then $2u^2 = m^4 + 3n^4$. Since $s$ is odd, $m$ and $n$ are odd, so $m^4 + 3n^4 \equiv 1 + 3 \equiv 4 \pmod 8$. However, $u$ even implies $2u^2 \equiv 0 \pmod 8$, a contradiction. If $3 | u$, then $3 | t$, and as before, this implies $3 | s$, contradicting $\gcd(u, s) = 1$.
28: 
29: **Case 2: $\gcd(x, 3) = 3$.**
30: Let $x = 3X$. Then $A^2 = 3X(9X^2 - 3y^2) = 9X(3X^2 - y^2)$. Thus $X = u^2$ and $3X^2 - y^2 = v^2$, so $3u^4 - y^2 = v^2$.
31: From (2), $B^2 = y(3(3u^2)^2 - y^2) = y(27u^4 - y^2)$. Since $\gcd(x, y) = 1$, $\gcd(y, 3) = 1$. Thus $y = s^2$ and $27u^4 - s^4 = t^2$.
32: From $3u^4 - y^2 = v^2$ and $y=s^2$, we have $v^2 + s^4 = 3u^4$.
33: Modulo 3, this implies $v^2 + s^4 \equiv 0 \pmod 3$, which requires $v \equiv 0 \pmod 3$ and $s \equiv 0 \pmod 3$.
34: Let $v = 3V$ and $s = 3S$. Substituting these into the equation:
35: $9V^2 + 81S^4 = 3u^4 \implies 3V^2 + 27S^4 = u^4$.
36: This implies $u^4 \equiv 0 \pmod 3$, so $u = 3U$.
37: $3V^2 + 27S^4 = 81U^4 \implies V^2 + 9S^4 = 27U^4$.
38: This implies $V^2 \equiv 0 \pmod 3$, so $V = 3V_1$.
39: $9V_1^2 + 9S^4 = 27U^4 \implies V_1^2 + S^4 = 3U^4$.
40: This is the same form as the equation $v^2 + s^4 = 3u^4$. By the method of infinite descent, the only solution is $u=s=v=0$, which contradicts $a, b$ being positive integers.
41: 
42: Since all cases for $n=3$ result in contradictions, $n \neq 3$. Given $n$ is odd and $n \geq 2$, we must have $n \geq 5$.
43: 
44: \(\square\)
