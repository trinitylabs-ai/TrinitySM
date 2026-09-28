To find all non-negative integers $a, b, c$ such that $20^{a}+b^{4}=2024^{c}$, we analyze the equation using modular arithmetic and prime factorization.

**1. Trivial Cases**
- If $c=0$, the equation becomes $20^a + b^4 = 1$. Since $a, b$ are non-negative integers, $20^a \ge 1$ and $b^4 \ge 0$. This requires $20^a = 1$ and $b^4 = 0$, which implies $a=0$ and $b=0$. This gives the solution $(0, 0, 0)$.
- If $b=0$, the equation becomes $20^a = 2024^c$. Comparing prime factorizations, $20^a = (2^2 \cdot 5)^a = 2^{2a} \cdot 5^a$ and $2024^c = (2^3 \cdot 11 \cdot 23)^c = 2^{3c} \cdot 11^c \cdot 23^c$. For these to be equal, the exponents of the primes 11 and 23 must be zero, so $c=0$, which leads back to $a=0$.
- If $a=0$, the equation becomes $1 + b^4 = 2024^c$. If $c=0$, then $b=0$. If $c \ge 1$, then $b^4 = 2024^c - 1$. Modulo 8, $2024 \equiv 0 \pmod 8$, so $b^4 \equiv -1 \equiv 7 \pmod 8$. However, fourth powers modulo 8 are only $0$ or $1$. Thus, no solutions exist for $c \ge 1$.

**2. Case $a, b, c \ge 1$**
We consider the equation modulo 5. Since $20 \equiv 0 \pmod 5$, we have:
$b^4 \equiv 2024^c \equiv (-1)^c \pmod 5$.
The fourth powers modulo 5 are $0^4 \equiv 0$ and $x^4 \equiv 1$ for $x \not\equiv 0 \pmod 5$. Thus, $b^4 \in \{0, 1\} \pmod 5$. For $b^4 \equiv (-1)^c \pmod 5$ to hold, $b^4$ must be $1$ and $c$ must be even.
Let $c = 2m$ for some integer $m \ge 1$. The equation becomes:
$20^a = 2024^{2m} - b^4 = (2024^m - b^2)(2024^m + b^2)$.
Let $X = 2024^m - b^2$ and $Y = 2024^m + b^2$. Then $XY = 20^a = 2^{2a} 5^a$.
The greatest common divisor is $\gcd(X, Y) = \gcd(X, X+Y) = \gcd(X, 2 \cdot 2024^m)$. Since the only prime factors of $X$ are 2 and 5, and the prime factors of $2 \cdot 2024^m$ are 2, 11, and 23, we must have $\gcd(X, Y) = 2^k$ for some $k \ge 1$.
This implies that only one of $X$ or $Y$ can be divisible by 5. Thus, $X$ and $Y$ must be of the form $2^u 5^p$ and $2^v 5^q$ where $\{p, q\} = \{0, a\}$.
We have $X + Y = 2 \cdot 2024^m = 2^{3m+1} \cdot 253^m$.
Dividing by $2^{\min(u, v)}$, we get:
$5^p + 2^w 5^q = 2^K 253^m$, where $w = |u-v|$ and $K = 3m+1-\min(u, v)$. We analyze the possible values of $K$:

- If $K \ge 2$, then $5^p + 2^w 5^q \equiv 0 \pmod 4$. Since $5 \equiv 1 \pmod 4$, this becomes $1 + 2^w \cdot 1 \equiv 0 \pmod 4$. If $w=0$, we have $2 \equiv 0 \pmod 4$; if $w=1$, we have $3 \equiv 0 \pmod 4$; if $w \ge 2$, we have $1 \equiv 0 \pmod 4$. All are impossible.
- If $K = 1$, then $5^p + 2^w 5^q = 2 \cdot 253^m$. Modulo 4, we have $1 + 2^w \cdot 1 \equiv 2 \cdot 1^m \equiv 2 \pmod 4$, which implies $2^w \equiv 1 \pmod 4$, so $w=0$. If $w=0$, then $u=v$. Then $X+Y = 2^u(5^p + 5^q) = 2^u(1 + 5^a) = 2^{3m+1} 253^m$. Since $K=1$, we have $u = 3m$, so $1 + 5^a = 2 \cdot 253^m$. Modulo 11, $253 \equiv 0 \pmod{11}$, so $1 + 5^a \equiv 0 \pmod{11}$, which means $5^a \equiv -1 \equiv 10 \pmod{11}$. However, the powers of $5 \pmod{11}$ are $\{5, 3, 4, 9, 1\}$, so no solution exists.
- If $K = 0$, then $5^p + 2^w 5^q = 253^m$. Modulo 4, we have $1 + 2^w \cdot 1 \equiv 1^m \equiv 1 \pmod 4$, which implies $2^w \equiv 0 \pmod 4$, so $w \ge 2$.
Now consider this equation modulo 3. Since $5 \equiv -1 \pmod 3$ and $253 \equiv 1 \pmod 3$, we have:
$(-1)^p + 2^w (-1)^q \equiv 1^m \equiv 1 \pmod 3$.
Since $u+v = 2a$, we have $w = |u-v| = (u+v) - 2\min(u, v) = 2a - 2\min(u, v)$, which is always even.
Thus, $2^w \equiv (-1)^w \equiv 1 \pmod 3$, and the equation becomes:
$(-1)^p + (-1)^q \equiv 1 \pmod 3$.
Since $\{p, q\} = \{0, a\}$, we have $1 + (-1)^a \equiv 1 \pmod 3$, which implies $(-1)^a \equiv 0 \pmod 3$, which is impossible.

Thus, no solutions exist for $a, b, c \ge 1$.

The only non-negative integer solution is $(a, b, c) = (0, 0, 0)$.
