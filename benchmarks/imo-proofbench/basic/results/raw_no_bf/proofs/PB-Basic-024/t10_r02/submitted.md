To find all non-negative integers $a, b, c$ such that $20^a + b^4 = 2024^c$, we evaluate different cases for the variables.

**Case 1: $c = 0$**
The equation becomes $20^a + b^4 = 2024^0 = 1$. Since $a, b$ are non-negative integers, $20^a$ can be $1$ (if $a=0$) or $20^a \ge 20$ (if $a \ge 1$).
If $a=0$, $1 + b^4 = 1 \implies b = 0$. This gives the solution $(0, 0, 0)$.
If $a \ge 1$, there are no solutions.

**Case 2: $a = 0$**
The equation becomes $1 + b^4 = 2024^c$.
If $c=0$, we already found $(0, 0, 0)$.
If $c \ge 1$, modulo 5 gives $b^4 \equiv 2024^c - 1 \equiv (-1)^c - 1 \pmod 5$.
Since $b^4 \pmod 5 \in \{0, 1\}$, we must have $(-1)^c - 1 \in \{0, 1\}$.
If $c$ is odd, $b^4 \equiv -2 \equiv 3 \pmod 5$, impossible.
If $c$ is even, let $c=2k$ for $k \ge 1$. Then $b^4 = (2024^k)^2 - 1$, which means $(2024^k)^2 - b^4 = 1$.
The only two perfect squares that differ by 1 are 0 and 1, so $b=0$ and $2024^k = 1$, which implies $k=0$, contradicting $c \ge 1$.

**Case 3: $b = 0$**
The equation becomes $20^a = 2024^c$.
Factorizing both sides: $(2^2 \cdot 5)^a = (2^3 \cdot 11 \cdot 23)^c \implies 2^{2a} \cdot 5^a = 2^{3c} \cdot 11^c \cdot 23^c$.
By the Fundamental Theorem of Arithmetic, the prime exponents must match:
$a = 0 \implies 2a = 3c \implies c = 0$.
This leads back to the solution $(0, 0, 0)$.

**Case 4: $a, b, c > 0$**
Modulo 5, $0 + b^4 \equiv 2024^c \equiv (-1)^c \pmod 5$. For $b^4 \equiv 0$ or $1 \pmod 5$, we must have $c$ be even. Let $c=2k$ for $k \ge 1$.
The equation is $20^a = 2024^{2k} - b^4 = (2024^k - b^2)(2024^k + b^2)$.
Let $\alpha = 2024^k - b^2$ and $\beta = 2024^k + b^2$. Then $\alpha \beta = 20^a = 2^{2a} 5^a$.
This implies $\alpha$ and $\beta$ are of the form $2^x 5^y$. Let $\alpha = 2^{x_1} 5^{y_1}$ and $\beta = 2^{x_2} 5^{y_2}$.
Since $b > 0$, $\alpha < \beta$. We have $\alpha + \beta = 2 \cdot 2024^k = 2^{3k+1} \cdot 253^k$.
Thus $2^{x_1} 5^{y_1} + 2^{x_2} 5^{y_2} = 2^{3k+1} 253^k$.
Dividing by $2^{\min(x_1, x_2)}$:
1. If $x_1 < x_2$, $2^{x_1}(5^{y_1} + 2^{x_2-x_1} 5^{y_2}) = 2^{3k+1} 253^k$. Then $x_1 = 3k+1$ and $5^{y_1} + 2^{x_2-x_1} 5^{y_2} = 253^k$.
   - If $y_1, y_2 > 0$, $5$ divides $253^k$, impossible.
   - If $y_1 = 0$, then $1 + 2^{x_2-x_1} 5^{y_2} = 253^k \implies 2^{x_2-x_1} 5^{y_2} = 253^k - 1$. However, $253 \equiv 1 \pmod 3$, so $253^k - 1$ is always divisible by 3, but $2^{x_2-x_1} 5^{y_2}$ is not.
   - If $y_2 = 0$, then $5^{y_1} + 2^{x_2-x_1} = 253^k$. We have $y_1 = a$ and $x_1 + x_2 = 2a \implies x_2 - x_1 = 2a - (6k+2)$. Thus $5^a + 2^{2a-6k-2} = 253^k$.
     Modulo 3: $(-1)^a + (-1)^{2a-6k-2} \equiv 1^k \equiv 1 \pmod 3$.
     $(-1)^a + 1 \equiv 1 \pmod 3 \implies (-1)^a \equiv 0 \pmod 3$, which is impossible.
2. If $x_1 = x_2$, then $2^{x_1}(5^{y_1} + 5^{y_2}) = 2^{3k+1} 253^k$.
   This implies $x_1 = 3k+1$ and $5^{y_1} + 5^{y_2} = 253^k$.
   If $y_1, y_2 > 0$, $5 | 253^k$. If $y_1 = 0$, $1 + 5^{y_2} = 253^k$, which means $5^{y_2} = 253^k - 1$, again divisible by 3.

Thus, no solutions exist for $a, b, c > 0$.

The only non-negative integer solution is $(a, b, c) = (0, 0, 0)$.

\(\square\)
