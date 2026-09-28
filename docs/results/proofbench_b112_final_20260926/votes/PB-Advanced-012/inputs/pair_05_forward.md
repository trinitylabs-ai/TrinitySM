# Problem

Let $p$ be a prime number and $a, b$ be positive integers such that

 \[
 p^{n}=a^{4}+b^{4}
 \]

 for some integer $n \geq 2$. Prove that $n \geq 5$.

# Proof A

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
