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
