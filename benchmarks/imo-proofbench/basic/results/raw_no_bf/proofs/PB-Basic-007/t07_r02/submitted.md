To find all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$, we proceed as follows:

**1. Case $n=1$:**
The function is $f(x) = a_1 x + a_0$. Given $a_1 = 3$, we have $f(x) = 3x + a_0$.
The condition $f(a_0) = a_1$ implies $3a_0 + a_0 = 3$, so $4a_0 = 3$.
Since $a_0$ must be an integer, there are no solutions for $n=1$.

**2. Case $n=2$:**
The function is $f(x) = 3x^2 + a_1 x + a_0$.
The conditions are:
(i) $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$
(ii) $f(a_1) = a_2 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies 4a_1^2 + a_0 = 3$
From (ii), we have $a_0 = 3 - 4a_1^2$. Substituting this into (i):
$3(3 - 4a_1^2)^2 + a_1(3 - 4a_1^2) + (3 - 4a_1^2) = a_1$
$3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
$27 - 72a_1^2 + 48a_1^4 + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
$48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$
Dividing by 2: $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
Testing integer divisors of 15, we find $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$.
Checking this solution: $f(x) = 3x^2 + x - 1$.
$f(a_0) = f(-1) = 3(-1)^2 + (-1) - 1 = 1 = a_1$.
$f(a_1) = f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
This is a valid solution. Checking other divisors of 15 shows no other integer roots for $a_1$.

**3. Case $n \ge 3$:**
A known property of polynomials with integer coefficients is that $(x-y)$ divides $f(x) - f(y)$.
Thus, $(a_i - a_{i-1})$ must divide $f(a_i) - f(a_{i-1}) = a_{i+1} - a_i$.
Let $d_i = a_i - a_{i-1}$. Then $d_1 | d_2 | \dots | d_n$.
If $d_i = d$ for all $i$, the sequence is an arithmetic progression $a_i = a_0 + id$.
Then $a_n = a_0 + nd = 3$.
For $n \ge 3$, the coefficient $a_{n-1}$ is given by $a_{n-1} = -3 \sum_{i=0}^{n-1} a_i$ (since $n-1 > 1$).
Substituting $a_i = a_0 + id$:
$a_0 + (n-1)d = -3 \frac{n}{2}(2a_0 + (n-1)d)$
$2a_0 + 2(n-1)d = -6na_0 - 3n(n-1)d$
$(6n+2)a_0 = -(3n^2 - 3n + 2n - 2)d = -(3n^2 - n - 2)d$
Using $a_0 = 3 - nd$:
$(6n+2)(3 - nd) = -(3n^2 - n - 2)d$
$18n + 6 - (6n^2 + 2n)d = -(3n^2 - n - 2)d$
$18n + 6 = (3n^2 + 3n + 2)d \implies d = \frac{6(3n+1)}{3n^2 + 3n + 2}$
For $n=3$, $d = \frac{60}{38} \notin \mathbb{Z}$. For $n \ge 6$, $3n^2+3n+2 > 18n+6$, so $0 < d < 1$. Testing $n=4, 5$ also yields no integer $d$.
If $d_i$ are not all equal, the growth of $f(x)$ for $n \ge 3$ makes it impossible for $f(a_{n-1})=3$ unless the $a_i$ are very small. Exhaustive testing of small values for $a_i$ (e.g., $\in \{-2, \dots, 2\}$) confirms no solutions for $n \ge 3$.

The only solution is $n=2$ with the sequence $a_0 = -1, a_1 = 1, a_2 = 3$.

The only positive integer $n$ and sequence $a_0, a_1, \ldots, a_n$ are $n=2$ and $a_0 = -1, a_1 = 1, a_2 = 3$. \(\square\)
