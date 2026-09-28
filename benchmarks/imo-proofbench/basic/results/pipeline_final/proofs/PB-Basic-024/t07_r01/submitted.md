To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we proceed as follows.

**1. Analysis of Special Cases**
- If $c=0$, the equation becomes $20^a + b^4 = 1$. Since $a, b \ge 0$, we must have $20^a \le 1$ and $b^4 \le 1$. This implies $a=0$ and $b=0$. Thus, $(0, 0, 0)$ is a solution.
- If $b=0$, the equation becomes $20^a = 2024^c$. Comparing the prime factorizations, $20 = 2^2 \cdot 5$ and $2024 = 2^3 \cdot 11 \cdot 23$. The equation $2^{2a} 5^a = 2^{3c} 11^c 23^c$ holds if and only if $a=0$ and $c=0$, leading again to $(0, 0, 0)$.
- If $a=0$, the equation becomes $1 + b^4 = 2024^c$. For $c=0$, we get $b=0$. For $c=1$, $b^4 = 2023$, which has no integer solution since $6^4 = 1296$ and $7^4 = 2401$. For $c \ge 2$, $2024^c \equiv 0 \pmod{16}$, so $b^4 \equiv -1 \equiv 15 \pmod{16}$. However, fourth powers modulo 16 are always $0$ or $1$, so no solution exists for $c \ge 2$.

**2. The General Case ($a, b, c > 0$)**
Considering the equation modulo 5, we have $20^a + b^4 \equiv 2024^c \pmod 5$. Since $20 \equiv 0 \pmod 5$ and $2024 \equiv -1 \pmod 5$, we obtain $b^4 \equiv (-1)^c \pmod 5$. By Fermat's Little Theorem, $b^4 \equiv 0$ or $1 \pmod 5$. If $b^4 \equiv 0 \pmod 5$, then $0 \equiv (-1)^c \pmod 5$, which is impossible. Thus, $b^4 \equiv 1 \pmod 5$, which implies $(-1)^c \equiv 1 \pmod 5$, so $c$ must be even. Let $c = 2m$ for some integer $m \ge 1$.

Rearranging the equation, we have:
\[ 20^a = 2024^{2m} - b^4 = (2024^m - b^2)(2024^m + b^2) \]
Let $X = 2024^m - b^2$ and $Y = 2024^m + b^2$. Then $XY = 20^a = 2^{2a} 5^a$ and $X + Y = 2 \cdot 2024^m = 2^{3m+1} \cdot 253^m$.
Let $g = \gcd(X, Y)$. Since $g$ must divide $XY = 2^{2a} 5^a$ and $X+Y = 2^{3m+1} \cdot 253^m$, and $\gcd(5, 253) = 1$, $g$ must be a power of 2. Since $a > 0$, $XY$ is even, and since $X+Y$ is even, $X$ and $Y$ must both be even. Thus, $g = 2^x$ for some $x \ge 1$.
Writing $X = gu$ and $Y = gv$ with $\gcd(u, v) = 1$, we have:
\[ g(u+v) = 2^{3m+1} \cdot 253^m \quad \text{and} \quad g^2 uv = 2^{2a} 5^a \]
Since $\gcd(u, v) = 1$ and $uv = 2^{2a-2x} 5^a$, the only possibilities for $\{u, v\}$ are $\{1, 2^{2a-2x} 5^a\}$ or $\{2^{2a-2x}, 5^a\}$.

- **Case 1: $\{u, v\} = \{1, 2^k 5^j\}$ where $k = 2a-2x$ and $j=a$.**
Then $g(1 + 2^k 5^j) = 2^{3m+1} 253^m$.
If $k > 0$, then $1 + 2^k 5^j$ is odd, so $g = 2^{3m+1}$ and $1 + 2^k 5^j = 253^m$. Modulo 3, $253 \equiv 1 \pmod 3$, so $1 + (-1)^k (-1)^j \equiv 1 \pmod 3$, which implies $(-1)^{k+j} \equiv 0 \pmod 3$, a contradiction.
If $k = 0$, then $1 + 5^j = 2^{3m+1-x} 253^m$. Since $m \ge 1$, $253^m$ is divisible by 11. Thus, $1 + 5^j \equiv 0 \pmod{11}$, or $5^j \equiv -1 \equiv 10 \pmod{11}$. However, the powers of $5 \pmod{11}$ are $\{5, 3, 4, 9, 1\}$, none of which are $10$. Thus, this case is impossible.

- **Case 2: $\{u, v\} = \{2^k, 5^j\}$ where $k = 2a-2x$ and $j=a$.**
Then $g(2^k + 5^j) = 2^{3m+1} 253^m$.
If $k > 0$, then $2^k + 5^j$ is odd, so $g = 2^{3m+1}$ and $2^k + 5^j = 253^m$. Modulo 3, we have $(-1)^k + (-1)^j \equiv 1^m \equiv 1 \pmod 3$. Since $k = 2(a-x)$ is even, we have $1 + (-1)^j \equiv 1 \pmod 3$, which implies $(-1)^j \equiv 0 \pmod 3$, a contradiction.
If $k = 0$, this reduces to Case 1.

Consequently, no solutions exist for $a, b, c > 0$.

The only non-negative integer solution is $(a, b, c) = (0, 0, 0)$.
