We seek all positive integers $n$ and integer sequences $a_0, a_1, \dots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for $i = 1, \dots, n$, where $f(x) = \sum_{k=0}^n a_k x^k$.

**1. Analysis of the sequence differences**
A fundamental property of polynomials with integer coefficients is that for any integers $x, y$, $x-y$ divides $f(x) - f(y)$. Applying this to the sequence $a_i$:
$a_1 - a_0$ divides $f(a_1) - f(a_0) = a_2 - a_1$.
$a_2 - a_1$ divides $f(a_2) - f(a_1) = a_3 - a_2$.
In general, $a_i - a_{i-1}$ divides $a_{i+1} - a_i$ for $i = 1, \dots, n-1$.
Let $d_i = a_i - a_{i-1}$. Then $d_1 \mid d_2 \mid \dots \mid d_n$.

**2. The case where some $d_k = 0$**
If $d_k = 0$ for some $k \in \{1, \dots, n\}$, then $a_{k-1} = a_k$. This implies $a_{k+1} = f(a_k) = f(a_{k-1}) = a_k$. By induction, $a_{k-1} = a_k = \dots = a_n = 3$.
If $a_0 = a_1 = \dots = a_n = 3$, then $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2} = 3$, which implies $3^{n+1} = 3$, so $n=0$, contradicting $n \ge 1$.
If $a_m \neq 3$ for some $m < k-1$, let $m$ be the largest such index. Then $a_m \neq 3$ and $a_{m+1} = \dots = a_n = 3$. Thus $f(a_m) = 3$ and $f(3) = 3$.
Then $f(x) - 3 = (x-3)(x-a_m) R(x)$ for some $R(x) \in \mathbb{Z}[x]$.
If $m > 0$, $f(a_{m-1}) = a_m$, so $(a_{m-1}-3)(a_{m-1}-a_m) R(a_{m-1}) = a_m - 3$.
This implies $(a_{m-1}-3)(a_{m-1}-a_m) \mid a_m - 3$.
If $a_m \neq 3$, then $|a_{m-1}-3| \cdot |a_{m-1}-a_m| \le |a_m - 3|$.
Testing $a_{m-1} = x$ and $a_m = y$, we find that for $|x-3| \ge 1$ and $|x-y| \ge 1$, the only integer solutions to $(x-3)(x-y) \mid y-3$ are $(x,y) = (2,1), (4,5), (5,7), (1,-1)$.
If $(a_{m-1}, a_m) = (2,1)$, then $f(a_{m-2}) = a_{m-1} = 2$. Using $f(x)-3 = (x-3)(x-1)R(x)$, we get $(a_{m-2}-3)(a_{m-2}-1)R(a_{m-2}) = 2-3 = -1$. This requires $(a_{m-2}-3)(a_{m-2}-1) = \pm 1$. The only integer solution is $a_{m-2}=2$, but then $a_{m-2}=a_{m-1}$, so $d_{m-1}=0$, which implies $a_{m-1}=3$, a contradiction.
Similar contradictions arise for the other pairs $(x,y)$. Thus, $d_i \neq 0$ for all $i$, and $|d_1| \le |d_2| \le \dots \le |d_n|$.

**3. Testing small values of $n$**
- For $n=1$: $f(x) = 3x + a_0$. $f(a_0) = a_1 = 3 \implies 4a_0 = 3$, no integer solution.
- For $n=2$: $f(x) = 3x^2 + a_1 x + a_0$.
  $f(a_1) = 3 \implies 3a_1^2 + a_1^2 + a_0 = 3 \implies a_0 = 3 - 4a_1^2$.
  $f(a_0) = a_1 \implies 3a_0^2 + a_1 a_0 + a_0 = a_1$.
  Substituting $a_0$: $3(3 - 4a_1^2)^2 + (a_1 + 1)(3 - 4a_1^2) = a_1 \implies 48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$.
  Dividing by 2: $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
  Testing divisors of 15, we find $a_1 = 1$ is the only integer root.
  For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$.
  Check: $f(x) = 3x^2 + x - 1$. $f(-1) = 3-1-1 = 1$ and $f(1) = 3+1-1 = 3$. This is a valid solution.

**4. Evaluating $n \ge 3$**
We have $f(a_{n-1}) = 3$. Expanding $f(a_{n-1}) = 4 a_{n-1}^n + \sum_{k=0}^{n-2} a_k a_{n-1}^k = 3$.
If $|a_{n-1}| \ge 2$, let $m = |a_{n-1}|$. Since $|d_k| \le |d_n| = |3 - a_{n-1}|$, we have $|a_k| \le 3 + (n-k)|3 - a_{n-1}|$.
For $a_{n-1} = 2$, $|d_n|=1$, so $|a_k| \le 3 + n - k$.
$f(2) = 4 \cdot 2^n + \sum_{k=0}^{n-2} a_k 2^k \ge 4 \cdot 2^n - \sum_{k=0}^{n-2} (3+n-k) 2^k = 2^n + n + 5 > 3$.
For $a_{n-1} \le -2$ or $a_{n-1} \ge 3$, the term $4 a_{n-1}^n$ dominates the sum for $n \ge 3$, and $|f(a_{n-1})| > 3$.
Thus, $a_{n-1} \in \{ -1, 0, 1 \}$.
- If $a_{n-1} = 1$, then $f(1) = 4 + \sum_{i=0}^{n-2} a_i = 3 \implies \sum_{i=0}^{n-2} a_i = -1$.
  $f(a_{n-2}) = 1$. Since $d_{n-1} \mid d_n=2$, $a_{n-2} \in \{ -1, 0, 2, 3 \}$.
  If $a_{n-2} = 3$, $f(3) = 1$, but $f(3) = 3 \cdot 3^n + 3^{n-1} + \dots + a_0 > 1$ for $n \ge 3$.
  If $a_{n-2} = 2$, $f(2) = 1$, but $f(2) > 3$.
  If $a_{n-2} = 0$, $a_0 = 1$. For $n=3$, $a_1=-2$, $f(1)=3 \neq a_1$.
  If $a_{n-2} = -1$, $f(-1) = 1$. For $n=3$, $a_0-a_1=3$ and $a_0+a_1=-1 \implies a_0=1, a_1=-2$. Then $f(1)=3 \neq a_1$.
- If $a_{n-1} = 0$, then $f(0) = a_0 = 3$. $f(3) = a_1$ and $f(a_1) = a_2 = 0$.
  For $n=3$, $f(3) = 81 + 3a_1 + 3 = a_1 \implies a_1 = -42$. Then $f(-42) = 3(-42)^3 - 42(-42) + 3 \neq 0$.
- If $a_{n-1} = -1$, then $f(-1) = 4(-1)^n + \sum_{k=0}^{n-2} a_k (-1)^k = 3$.
  For $n=3$, $a_0-a_1=5$. $f(a_1) = a_2 = -1 \implies 3a_1^3 - a_1^2 + a_1^2 + a_0 = 3a_1^3 + a_1 + 5 = -1 \implies 3a_1^3 + a_1 + 6 = 0$.
  Testing divisors of 6, we find no integer solutions for $a_1$.

The only solution is $n=2$ with the sequence $a_0 = -1, a_1 = 1, a_2 = 3$.

The only positive integer $n$ and integer sequence $a_0, \dots, a_n$ are $n=2$ and $a_0 = -1, a_1 = 1, a_2 = 3$.
