To find all non-negative integers $a, b, c$ such that $20^{a}+b^{4}=2024^{c}$, we analyze the equation based on the values of $a, b, c$.

**Case 1: $a=0$**
The equation becomes $1+b^{4}=2024^{c}$.
If $c=0$, we have $1+b^{4}=1$, which implies $b=0$. This gives the solution $(a,b,c) = (0,0,0)$.
If $c=1$, we have $b^{4}=2023$. Since $6^4 = 1296$ and $7^4 = 2401$, there is no integer solution for $b$.
If $c > 1$, the equation $2024^c - b^4 = 1$ is a specific case of the equation $x^n - y^2 = 1$ (where $x=2024, n=c, y=b^2$). A theorem by Lebesgue (1850) states that $x^n - y^2 = 1$ has no solutions in positive integers for $n > 1$. Thus, there are no solutions for $c > 1, b > 0$. If $b=0$, $2024^c = 1$, so $c=0$.

**Case 2: $b=0$**
The equation becomes $20^a = 2024^c$.
Comparing prime factorizations: $2^{2a} \cdot 5^a = 2^{3c} \cdot 11^c \cdot 23^c$.
For the prime factors to match, the exponents of 5, 11, and 23 must be zero, implying $a=0$ and $c=0$. This leads back to the solution $(0,0,0)$.

**Case 3: $c=0$**
The equation becomes $20^a + b^4 = 1$.
Since $a, b$ are non-negative integers, $20^a \ge 1$ and $b^4 \ge 0$.
If $a=0$, then $1+b^4=1 \implies b=0$, giving $(0,0,0)$.
If $a > 0$, then $20^a \ge 20$, so $20^a+b^4 > 1$, which has no solutions.

**Case 4: $a, b, c > 0$**
Consider the equation modulo 5:
$20^a + b^4 = 2024^c \implies 0 + b^4 \equiv (-1)^c \pmod 5$.
The possible values of $b^4 \pmod 5$ are 0 (if $5|b$) and 1 (if $5 \nmid b$).
If $b^4 \equiv 0 \pmod 5$, then $0 \equiv (-1)^c \pmod 5$, which is impossible.
If $b^4 \equiv 1 \pmod 5$, then $1 \equiv (-1)^c \pmod 5$, which implies that $c$ must be even. Let $c=2k$ for some integer $k \ge 1$.
The equation becomes $20^a = 2024^{2k} - b^4$.
Factoring the right side as a difference of squares:
$20^a = (2024^k - b^2)(2024^k + b^2)$.
Since $20^a = (2^2 \cdot 5)^a$, the factors must be of the form $2^{x} 5^{y}$. Let:
$2024^k - b^2 = 2^{x_1} 5^{y_1}$ and $2024^k + b^2 = 2^{x_2} 5^{y_2}$.
Adding these two equations:
$2 \cdot 2024^k = 2^{x_1} 5^{y_1} + 2^{x_2} 5^{y_2} = 2^{x_1} 5^{y_1} (1 + 2^{x_2-x_1} 5^{y_2-y_1})$.
Substitute the prime factorization $2024 = 2^3 \cdot 11 \cdot 23$:
$2 \cdot (2^3 \cdot 11 \cdot 23)^k = 2^{3k+1} \cdot 11^k \cdot 23^k = 2^{x_1} 5^{y_1} (1 + 2^{x_2-x_1} 5^{y_2-y_1})$.
Since 5 does not divide the left side, we must have $y_1 = 0$.
Then $2^{3k+1} \cdot 11^k \cdot 23^k = 2^{x_1} (1 + 2^{x_2-x_1} 5^{y_2})$.
This implies $x_1 = 3k+1$ and $1 + 2^{x_2-x_1} 5^{y_2} = (11 \cdot 23)^k = 253^k$.
Let $X = x_2 - x_1$ and $Y = y_2$. The equation is $2^X 5^Y + 1 = 253^k$.
Taking this equation modulo 3:
$2^X 5^Y + 1 \equiv (-1)^X (-1)^Y + 1 = (-1)^{X+Y} + 1 \pmod 3$.
$253^k \equiv 1^k = 1 \pmod 3$.
Thus, $(-1)^{X+Y} + 1 \equiv 1 \pmod 3$, which implies $(-1)^{X+Y} \equiv 0 \pmod 3$.
This is impossible for any integers $X, Y$. Therefore, there are no solutions in this case.

The only solution is $(a,b,c) = (0,0,0)$.

\(\square\)
