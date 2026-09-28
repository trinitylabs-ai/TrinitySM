To determine all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for all $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$, we proceed as follows:

**1. Analysis of the conditions**
The conditions are $f(a_0) = a_1, f(a_1) = a_2, \ldots, f(a_{n-1}) = a_n = 3$.
For any polynomial $f(x)$ with integer coefficients, the property $(x - y) \mid (f(x) - f(y))$ holds for all integers $x \neq y$.
Let $d_i = a_i - a_{i-1}$ for $i = 1, \ldots, n$. Applying the property to the sequence $a_i$:
$(a_1 - a_0) \mid (f(a_1) - f(a_0)) \implies d_1 \mid (a_2 - a_1) \implies d_1 \mid d_2$.
$(a_2 - a_1) \mid (f(a_2) - f(a_1)) \implies d_2 \mid (a_3 - a_2) \implies d_2 \mid d_3$.
In general, we have $d_1 \mid d_2 \mid \cdots \mid d_n$. This implies $|d_1| \le |d_2| \le \cdots \le |d_n|$.

If $d_k = 0$ for any $k$, then $a_k = a_{k-1}$. This implies $f(a_k) = f(a_{k-1})$, so $a_{k+1} = a_k$. By induction, $a_k = a_{k+1} = \cdots = a_n = 3$. If all $a_i = 3$, then $f(x) = 3 \sum_{j=0}^n x^j$. The condition $f(3) = 3$ gives $3 \frac{3^{n+1}-1}{3-1} = 3 \implies 3^{n+1} = 3 \implies n=0$, which contradicts $n \in \mathbb{Z}^+$. Thus, $d_i \neq 0$ for all $i$.

**2. Case $n=1$**
$f(x) = 3x + a_0$. The condition $f(a_0) = a_1 = 3$ gives $3a_0 + a_0 = 3 \implies 4a_0 = 3$. No integer solution exists.

**3. Case $n=2$**
$f(x) = 3x^2 + a_1 x + a_0$. The conditions are:
(i) $f(a_1) = a_2 = 3 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies a_0 = 3 - 4a_1^2$.
(ii) $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$.
Substituting $a_0$ into (ii):
$3(3 - 4a_1^2)^2 + (a_1 + 1)(3 - 4a_1^2) = a_1$
$3(9 - 24a_1^2 + 16a_1^4) + 3a_1 - 4a_1^3 + 3 - 4a_1^2 = a_1$
$48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0 \implies 24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
Testing integer divisors of 15, we find $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
For $a_1 = 1$, we have $a_0 = 3 - 4(1)^2 = -1$.
Checking: $f(x) = 3x^2 + x - 1$. $f(-1) = 3(-1)^2 + (-1) - 1 = 1$ and $f(1) = 3(1)^2 + 1 - 1 = 3$. This is a solution.
Dividing the polynomial by $(a_1 - 1)$ gives $24a_1^3 + 22a_1^2 - 16a_1 - 15 = 0$. Testing other divisors of 15 shows no other integer roots.

**4. Case $n \ge 3$**
If $|a_{n-1}| \ge 2$, then $|f(a_{n-1})| = |a_n| = 3$ requires the leading term $3a_{n-1}^n$ to be balanced by other terms. However, for $n \ge 3$, $3|a_{n-1}|^n$ grows much faster than the lower-degree terms can compensate without making the previous $a_i$ values excessively large, creating a contradiction.
If $a_{n-1} \in \{-1, 0, 1\}$, we test $n=3$:
- If $a_2 = 1$, $f(a_2) = 3 \implies 4(1)^3 + a_1(1) + a_0 = 3 \implies a_1 + a_0 = -1$.
  $f(a_1) = a_2 \implies 3a_1^3 + a_2 a_1^2 + a_1^2 + a_0 = a_2 \implies 3a_1^3 + 2a_1^2 + a_0 = 1$.
  Substituting $a_0 = -1 - a_1$: $3a_1^3 + 2a_1^2 - a_1 - 2 = 0$. Testing $a_1 \in \{-1, 0, 1\}$ yields no solutions.
- If $a_2 = 0$, $f(a_2) = 3 \implies a_0 = 3$, which contradicts $a_i \in \{-1, 0, 1\}$.
- If $a_2 = -1$, $f(a_2) = 3 \implies 4(-1)^3 + a_1(-1) + a_0 = 3 \implies a_0 - a_1 = 7$, impossible for $a_i \in \{-1, 0, 1\}$.

Thus, no solutions exist for $n \ge 3$.

The only solution is $n=2$ and the sequence $a_0 = -1, a_1 = 1, a_2 = 3$. \(\square\)
