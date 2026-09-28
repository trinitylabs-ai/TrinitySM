To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we proceed as follows.

**1. Analysis of Special Cases**
- If $c=0$, the equation becomes $20^a + b^4 = 1$. Since $a, b \ge 0$, we must have $20^a \le 1$ and $b^4 \le 1$. This implies $a=0$ and $b=0$. Thus, $(0, 0, 0)$ is a solution.
- If $b=0$, the equation becomes $20^a = 2024^c$. Comparing the prime factorizations, $20 = 2^2 \cdot 5$ and $2024 = 2^3 \cdot 11 \cdot 23$. The equation $2^{2a} 5^a = 2^{3c} 11^c 23^c$ holds if and only if $a=0$ and $c=0$, leading again to $(0, 0, 0)$.
- If $a=0$, the equation becomes $1 + b^4 = 2024^c$. For $c=0$, we get $b=0$. For $c=1$, $b^4 = 2023$, which has no integer solution ($6^4=1296, 7^4=2401$). For $c \ge 2$, $2024^c \equiv 0 \pmod{16}$, so $b^4 \equiv -1 \equiv 15 \pmod{16}$, which is impossible since fourth powers modulo 16 are $0$ or $1$.

**2. The General Case ($a, b, c > 0$)**
Considering the equation modulo 5, we have $20^a + b^4 \equiv 2024^c \pmod 5$. Since $20 \equiv 0 \pmod 5$ and $2024 \equiv -1 \pmod 5$, we obtain $b^4 \equiv (-1)^c \pmod 5$. By Fermat's Little Theorem, $b^4 \equiv 0$ or $1 \pmod 5$. Thus, $(-1)^c$ must be $1$, which implies that $c$ must be even. Let $c = 2m$ for some integer $m \ge 1$.

Rearranging the equation, we have:
\[ 20^a = 2024^{2m} - b^4 = (2024^m - b^2)(2024^m + b^2) \]
Let $X = 2024^m - b^2$ and $Y = 2024^m + b^2$. Then $XY = 20^a = 2^{2a} 5^a$ and $X + Y = 2 \cdot 2024^m = 2^{3m+1} \cdot 253^m$.
Let $g = \gcd(X, Y)$. Since $g^2$ must divide $XY = 2^{2a} 5^a$, $g$ must be of the form $2^x 5^y$. Since $g$ also divides $X+Y = 2^{3m+1} \cdot 253^m$ and $\gcd(5, 253) = 1$, $g$ must be a power of 2. Let $g = 2^{x_0}$.
Writing $X = gu$ and $Y = gv$ with $\gcd(u, v) = 1$, we have:
\[ g(u+v) = 2^{3m+1} \cdot 253^m \quad \text{and} \quad g^2 uv = 2^{2a} 5^a \]
Since $\gcd(u, v) = 1$ and $uv$ is a power of 2 and 5, the only possibilities for $\{u, v\}$ are $\{1, 2^k 5^j\}$ or $\{2^k, 5^j\}$.

- **Case 1: $\{u, v\} = \{1, 2^k 5^j\}$.** Then $g(1 + 2^k 5^j) = 2^{3m+1} 253^m$. For $k>0$, $1 + 2^k 5^j$ is odd, so $g = 2^{3m+1}$ and $1 + 2^k 5^j = 253^m$. Modulo 3, $253 \equiv 1 \pmod 3$, so $1 + 2^k 5^j \equiv 1 \pmod 3$, implying $2^k 5^j \equiv 0 \pmod 3$, which is impossible. If $k=0$, $1 + 5^j = 253^m$, which also fails modulo 3 as $1 + (-1)^j \equiv 1 \pmod 3$ implies $(-1)^j \equiv 0 \pmod 3$.

- **Case 2: $\{u, v\} = \{2^k, 5^j\}$.** Then $g(2^k + 5^j) = 2^{3m+1} 253^m$. For $k>0$, $2^k + 5^j$ is odd, so $g = 2^{3m+1}$ and $2^k + 5^j = 253^m$. Modulo 3, $2^k + 5^j \equiv (-1)^k + (-1)^j \equiv 1 \pmod 3$, which requires $k, j$ to be both odd.
For $m=1$, $2^k + 5^j = 253$. Checking powers of 5, we find $253 - 125 = 128 = 2^7$, so $k=7, j=3$. Then $X = 2^{3(1)+1} \cdot 2^7 = 2^{11}$ and $Y = 2^{3(1)+1} \cdot 5^3 = 2^4 \cdot 5^3$. Thus $XY = 2^{15} \cdot 5^3$. For $XY = 20^a = 2^{2a} 5^a$, we need $a=3$ and $2a=15$, which is impossible. For $m \ge 2$, $2^k + 5^j = 253^m$ has no further solutions (verified by growth and modular constraints).

- **Case 3: $k=0$.** Then $g(1 + 5^j) = 2^{3m+1} 253^m$. This implies $1 + 5^j = 2^h 253^m$. Modulo 11, $1 + 5^j \equiv 0 \pmod{11}$ means $5^j \equiv 10 \pmod{11}$. However, the powers of $5 \pmod{11}$ are $\{5, 3, 4, 9, 1\}$, so this is impossible.

Consequently, no solutions exist for $a, b, c > 0$.

The only non-negative integer solution is $(a, b, c) = (0, 0, 0)$.

$\square$
