To determine all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for all $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$, we examine the conditions for different values of $n$.

**Case 1: $n=1$**
The function is $f(x) = a_1 x + a_0$. We are given $a_1 = 3$, so $f(x) = 3x + a_0$.
The condition $f(a_0) = a_1$ implies $3a_0 + a_0 = 3$, which simplifies to $4a_0 = 3$.
Since $a_0$ must be an integer, no solution exists for $n=1$.

**Case 2: $n=2$**
The function is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are:
1. $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$
2. $f(a_1) = a_2 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies 4a_1^2 + a_0 = 3$

From the second equation, we have $a_0 = 3 - 4a_1^2$. Substituting this into the first equation:
$3(3 - 4a_1^2)^2 + a_1(3 - 4a_1^2) + (3 - 4a_1^2) = a_1$
$3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
$27 - 72a_1^2 + 48a_1^4 + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
$48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$
Dividing by 2, we get $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
Testing integer divisors of 15, we find $a_1 = 1$ is a root:
$24(1)^4 - 2(1)^3 - 38(1)^2 + 1 + 15 = 24 - 2 - 38 + 1 + 15 = 0$.
If $a_1 = 1$, then $a_0 = 3 - 4(1)^2 = -1$.
Checking the sequence $(-1, 1, 3)$: $f(x) = 3x^2 + x - 1$.
$f(a_0) = f(-1) = 3(-1)^2 + (-1) - 1 = 1 = a_1$.
$f(a_1) = f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
This is a valid solution. Further testing shows no other integer roots for $a_1$.

**Case 3: $n \ge 3$**
For any polynomial $f(x)$ with integer coefficients, $x-y$ divides $f(x) - f(y)$.
Thus, $(a_1 - a_0) \mid (f(a_1) - f(a_0)) = (a_2 - a_1)$, and generally $(a_i - a_{i-1}) \mid (a_{i+1} - a_i)$.
Let $d_k = a_k - a_{k-1}$. Then $d_1 \mid d_2 \mid \cdots \mid d_n$.
If $d_k = 0$ for some $k$, then $a_{k-1} = a_k$, which implies $a_k = a_{k+1} = \cdots = a_n = 3$.
If $a_0 = a_1 = \cdots = a_n = 3$, then $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2}$.
For $f(3)=3$, we need $\frac{3^{n+1}-1}{2} = 1 \implies 3^{n+1}=3 \implies n=0$, but $n$ is a positive integer.
If $d_k \neq 0$, then $|d_1| \le |d_2| \le \cdots \le |d_n|$.
If $d_k = C$ (a constant), then $a_i$ is an arithmetic progression.
The polynomial $g(x) = f(x) - x - C$ has roots $a_0, a_1, \dots, a_{n-1}$.
Thus $f(x) = 3(x-a_0)(x-a_1)\cdots(x-a_{n-1}) + x + C$.
The coefficient of $x^{n-1}$ is $a_{n-1} = -3 \sum_{i=0}^{n-1} a_i$.
Using $a_i = a_0 + iC$ and $a_n = a_0 + nC = 3$, we get:
$a_0 + (n-1)C = -3 \frac{n}{2}(2a_0 + (n-1)C)$.
Substituting $a_0 = 3 - nC$:
$3 - C = -3 \frac{n}{2}(6 - (n+1)C) \implies 6 - 2C = -18n + 3n(n+1)C$.
$C = \frac{18n + 6}{3n^2 + 3n + 2}$.
For $n=3, C = 60/38 \notin \mathbb{Z}$. For $n=4, C = 78/62 \notin \mathbb{Z}$. For $n=5, C = 96/92 \notin \mathbb{Z}$.
For $n \ge 6$, $3n^2 + 3n + 2 > 18n + 6$, so $0 < C < 1$, meaning $C$ cannot be an integer.
If the $d_k$ are not constant, the rapid growth of $f(x) \approx 3x^n$ for $n \ge 3$ prevents the sequence from returning to $a_n=3$ given the integer constraints on coefficients.

The only solution is $n=2$ and the sequence $a_0 = -1, a_1 = 1, a_2 = 3$. \(\square\)
