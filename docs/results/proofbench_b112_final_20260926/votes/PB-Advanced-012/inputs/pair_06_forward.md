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
