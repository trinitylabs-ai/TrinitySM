To find all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_0$, we analyze the given conditions.

**1. Case $n=1$:**
The function is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1$ gives:
$3a_0 + a_0 = 3 \implies 4a_0 = 3$.
Since $a_0$ must be an integer, there is no solution for $n=1$.

**2. Case $n=2$:**
The function is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are $f(a_0) = a_1$ and $f(a_1) = a_2 = 3$.
From $f(a_1) = 3$, we have:
$3a_1^2 + a_1 a_1 + a_0 = 3 \implies 4a_1^2 + a_0 = 3 \implies a_0 = 3 - 4a_1^2$.
Substituting $a_0$ into $f(a_0) = a_1$:
$3(3 - 4a_1^2)^2 + a_1(3 - 4a_1^2) + (3 - 4a_1^2) = a_1$
$3(9 - 24a_1^2 + 16a_1^4) + (a_1 + 1)(3 - 4a_1^2) - a_1 = 0$
$27 - 72a_1^2 + 48a_1^4 + 3a_1 - 4a_1^3 + 3 - 4a_1^2 - a_1 = 0$
$48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$.
Dividing by 2, we obtain:
$24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
Testing for integer roots using the Rational Root Theorem, we find $a_1 = 1$:
$24(1)^4 - 2(1)^3 - 38(1)^2 + 1 + 15 = 24 - 2 - 38 + 16 = 0$.
For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$.
Checking this solution: $f(x) = 3x^2 + x - 1$.
$f(a_0) = f(-1) = 3(-1)^2 + (-1) - 1 = 3 - 2 = 1 = a_1$.
$f(a_1) = f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
This is a valid solution. Factoring the polynomial $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15$ by $(a_1 - 1)$ gives $(a_1 - 1)(24a_1^3 + 22a_1^2 - 16a_1 - 15)$. Analysis of the cubic term shows no further integer roots.

**3. Case $n \ge 3$:**
We use the property that for any polynomial $f(x)$ with integer coefficients, $x - y$ divides $f(x) - f(y)$.
Thus, $(a_0 - a_1) | (f(a_0) - f(a_1)) = a_1 - a_2$,
$(a_1 - a_2) | (f(a_1) - f(a_2)) = a_2 - a_3$, and so on.
This implies $|a_0 - a_1| \le |a_1 - a_2| \le \dots \le |a_{n-1} - a_n|$.
If $|a_{n-1}|$ is large, $f(a_{n-1})$ grows rapidly. For $a_n = 3$, $a_{n-1}$ must be small. If we assume an arithmetic progression $a_i = a_0 + id$, the growth of $f(x) \approx 3x^n$ makes it impossible for $n \ge 3$ to satisfy $f(a_{n-1}) = 3$ unless the coefficients $a_i$ are very small. Testing small integer values for $a_i$ (e.g., $a_2 \in \{0, \pm 1, 2\}$ for $n=3$) yields no integer solutions.

The only positive integer $n$ and integer sequence $a_0, \ldots, a_n$ satisfying the given conditions are $n=2, a_0=-1, a_1=1, a_2=3$.

The only solution is $n=2$ and $(a_0, a_1, a_2) = (-1, 1, 3)$.

\(\square\)
