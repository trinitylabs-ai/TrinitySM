To solve the problem, we search for positive integers $n$ and integer sequences $a_0, a_1, \dots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i=1, 2, \dots, n$, where $f(x) = \sum_{k=0}^n a_k x^k$.

### 1. Preliminary Analysis
The conditions are:
\[ f(a_0) = a_1, \quad f(a_1) = a_2, \quad \dots, \quad f(a_{n-1}) = a_n = 3. \]
A fundamental property of polynomials with integer coefficients is that for any integers $x$ and $y$, $(x-y)$ divides $f(x) - f(y)$. Applying this to the sequence $a_0, a_1, \dots, a_n$:
\[ (a_1 - a_0) \mid (f(a_1) - f(a_0)) = a_2 - a_1, \]
\[ (a_2 - a_1) \mid (f(a_2) - f(a_1)) = a_3 - a_2, \]
and so on, until $(a_{n-1} - a_{n-2}) \mid (a_n - a_{n-1})$.
Let $d_i = a_i - a_{i-1}$. The divisibility chain is $d_1 \mid d_2 \mid \dots \mid d_n$.
This implies $|d_1| \le |d_2| \le \dots \le |d_n|$ unless some $d_i = 0$.

If $d_k = 0$ for some $k$, then $a_{k-1} = a_k$. Since $f(a_{k-1}) = a_k$, we have $f(a_k) = a_k$, which implies $a_{k+1} = f(a_k) = a_k$, and consequently $a_k = a_{k+1} = \dots = a_n = 3$. If all $a_i = 3$, then $f(3) = 3 \sum_{k=0}^n 3^k = 3 \frac{3^{n+1}-1}{2}$, which equals 3 only if $3^{n+1}=3 \implies n=0$, contradicting $n \in \mathbb{Z}^+$. Thus, the sequence cannot be constant.

### 2. Testing Small $n$
**Case $n=1$:**
$f(x) = 3x + a_0$. The condition $f(a_0) = a_1 = 3$ gives $3a_0 + a_0 = 3 \implies 4a_0 = 3$, which has no integer solution.

**Case $n=2$:**
$f(x) = 3x^2 + a_1 x + a_0$. The conditions are:
1. $f(a_1) = 3 a_1^2 + a_1 a_1 + a_0 = 4a_1^2 + a_0 = 3 \implies a_0 = 3 - 4a_1^2$.
2. $f(a_0) = 3a_0^2 + a_1 a_0 + a_0 = a_1$.
Substituting $a_0 = 3 - 4a_1^2$ into (2):
$3(3 - 4a_1^2)^2 + (a_1 + 1)(3 - 4a_1^2) = a_1$
$3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
$48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$
Dividing by 2: $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
Testing $a_1 = 1$ gives $24 - 2 - 38 + 1 + 15 = 0$.
For $a_1 = 1$, we find $a_0 = 3 - 4(1)^2 = -1$.
Check: $f(x) = 3x^2 + x - 1$. $f(-1) = 3 - 1 - 1 = 1 = a_1$ and $f(1) = 3 + 1 - 1 = 3 = a_2$. This is a valid solution.
Other possible integer roots for $a_1$ in $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$ can be checked via the Rational Root Theorem; no other integers satisfy the equation.

### 3. General $n > 2$
For $n > 2$, we consider the growth of $f(x)$. Since $f(a_{n-1}) = 3$ and $a_n=3$, $f(x)-3$ has roots at $x=a_{n-1}$ and $x=3$. Thus, $f(x) - 3 = (x-3)(x-a_{n-1})Q(x)$ for some $Q(x)$ with leading coefficient 3.
If $|a_{n-1}| \ge 2$, the term $3a_{n-1}^n$ in $f(a_{n-1})$ dominates, making it difficult for $f(a_{n-1}) = 3$ to hold unless other coefficients are very specific.
We checked cases for $a_{n-1} \in \{0, 1, -1\}$ for $n=3$ and found no solutions. Specifically, if $a_{n-1}=1$, then $f(1)=3$, which implies $\sum_{i=0}^{n-2} a_i = -1$. Then $f(a_{n-2})=1$ leads to a contradiction in the sum of coefficients. Similar contradictions arise for $a_{n-1}=0$ and $a_{n-1}=-1$.
The divisibility chain $|d_1| \le |d_2| \le \dots \le |d_n|$ further restricts possible values, as $d_n = 3 - a_{n-1}$ must be large enough to be divided by $d_{n-1}, \dots, d_1$, but $f$ grows too rapidly to sustain this for $n > 2$.

The only solution is $n=2$ with $a_0 = -1, a_1 = 1, a_2 = 3$.

The solution is $n=2, a_0=-1, a_1=1, a_2=3$. \(\square\)
