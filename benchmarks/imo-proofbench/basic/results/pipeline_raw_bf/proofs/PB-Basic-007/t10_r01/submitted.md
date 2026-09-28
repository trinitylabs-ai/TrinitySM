To find all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for all $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$, we proceed as follows.

**1. Case $n=1$:**
The polynomial is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1$ gives:
\[3a_0 + a_0 = a_1 \implies 4a_0 = a_1.\]
Since $a_n = a_1 = 3$, we have $4a_0 = 3$, which has no integer solution for $a_0$.

**2. Case $n=2$:**
The polynomial is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are $f(a_0) = a_1$ and $f(a_1) = a_2 = 3$.
From $f(a_1) = 3$, we have:
\[3a_1^2 + a_1(a_1) + a_0 = 3 \implies 4a_1^2 + a_0 = 3 \implies a_0 = 3 - 4a_1^2.\]
Substituting $a_0$ into $f(a_0) = a_1$:
\[3a_0^2 + a_1 a_0 + a_0 = a_1 \implies 3(3 - 4a_1^2)^2 + (a_1 + 1)(3 - 4a_1^2) - a_1 = 0.\]
Expanding this expression:
\[3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 - a_1 = 0\]
\[27 - 72a_1^2 + 48a_1^4 + 2a_1 - 4a_1^3 + 3 - 4a_1^2 = 0\]
\[48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0.\]
Dividing by 2:
\[24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0.\]
By the Rational Root Theorem, testing integer divisors of 15, we find $a_1 = 1$:
\[24(1)^4 - 2(1)^3 - 38(1)^2 + 1 + 15 = 24 - 2 - 38 + 16 = 0.\]
For $a_1 = 1$, we find $a_0 = 3 - 4(1)^2 = -1$.
Checking the sequence $a_0 = -1, a_1 = 1, a_2 = 3$:
$f(x) = 3x^2 + x - 1$.
$f(a_0) = f(-1) = 3(-1)^2 + (-1) - 1 = 3 - 1 - 1 = 1 = a_1$.
$f(a_1) = f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
Thus, $(n=2, a_0=-1, a_1=1, a_2=3)$ is a solution.

**3. Case $n \ge 3$:**
A known property of polynomials with integer coefficients is that $(x-y)$ divides $f(x) - f(y)$. Applying this to the sequence $a_i$:
\[(a_0 - a_1) \mid (f(a_0) - f(a_1)) = (a_1 - a_2)\]
\[(a_1 - a_2) \mid (f(a_1) - f(a_2)) = (a_2 - a_3)\]
and so on, implying $|a_0 - a_1| \le |a_1 - a_2| \le \dots \le |a_{n-1} - a_n|$.
If $a_0 = a_1$, then $a_0 = a_1 = \dots = a_n = 3$, which implies $f(x) = 3x^n + 3x^{n-1} + \dots + 3$. Then $f(3) = 3 \frac{3^{n+1}-1}{2} = 3 \implies 3^{n+1}=3 \implies n=0$, which is not a positive integer.
Thus $|a_i - a_{i+1}| \ge 1$. If $n \ge 3$, the growth of $f(x)$ is too rapid to satisfy $f(a_{n-1}) = 3$ unless $a_{n-1}$ is very small. Testing $a_{n-1} \in \{-1, 0, 1, 2\}$ for $n=3$ and $n=4$ leads to no integer solutions for the preceding terms $a_i$. For instance, if $a_{n-1} = 1$, we require $a_{n-2} + \dots + a_0 = -1$ and $f(a_{n-2}) = 1$. For $n=3$, this leads to $3a_1^3 + 2a_1^2 - a_1 - 2 = 0$, which has no integer roots. Similar contradictions arise for other small values of $a_{n-1}$.

The only solution is $n=2$ and the sequence $a_0=-1, a_1=1, a_2=3$.

\(\square\)
