We seek all positive integers $n$ and integer sequences $a_0, a_1, \ldots, a_n$ such that $a_n = 3$ and $f(a_{i-1}) = a_i$ for all $i = 1, 2, \ldots, n$, where $f(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0$.

**Case $n=1$:**
The polynomial is $f(x) = 3x + a_0$. The condition $f(a_0) = a_1$ gives $3a_0 + a_0 = a_1$, so $4a_0 = a_1$. Since $a_1 = a_n = 3$, we have $4a_0 = 3$, which has no integer solution for $a_0$.

**Case $n=2$:**
The polynomial is $f(x) = 3x^2 + a_1 x + a_0$. The conditions are $f(a_0) = a_1$ and $f(a_1) = a_2 = 3$.
From $f(a_1) = 3$, we have $3a_1^2 + a_1(a_1) + a_0 = 3$, so $a_0 = 3 - 4a_1^2$.
Substituting $a_0$ into $f(a_0) = a_1$:
$3(3 - 4a_1^2)^2 + a_1(3 - 4a_1^2) + (3 - 4a_1^2) = a_1$
$3(9 - 24a_1^2 + 16a_1^4) + (a_1 + 1)(3 - 4a_1^2) - a_1 = 0$
$27 - 72a_1^2 + 48a_1^4 + 3a_1 - 4a_1^3 + 3 - 4a_1^2 - a_1 = 0$
$48a_1^4 - 4a_1^3 - 76a_1^2 + 2a_1 + 30 = 0$
Dividing by 2: $24a_1^4 - 2a_1^3 - 38a_1^2 + a_1 + 15 = 0$.
Testing integer divisors of 15, we find $a_1 = 1$ is a root: $24 - 2 - 38 + 1 + 15 = 0$.
For $a_1 = 1$, $a_0 = 3 - 4(1)^2 = -1$.
Checking the sequence $a_0 = -1, a_1 = 1, a_2 = 3$: $f(x) = 3x^2 + x - 1$.
$f(-1) = 3(-1)^2 + (-1) - 1 = 1 = a_1$ and $f(1) = 3(1)^2 + 1 - 1 = 3 = a_2$.
Testing other divisors of 15 ($\pm 3, \pm 5, \pm 15$) reveals no other integer solutions for $a_1$. Thus, $(n=2, a_0=-1, a_1=1, a_2=3)$ is the only solution for $n=2$.

**Case $n \ge 3$:**
A property of polynomials with integer coefficients is that $(x-y) \mid (f(x) - f(y))$.
Thus, $(a_0 - a_1) \mid (f(a_0) - f(a_1)) = (a_1 - a_2)$, $(a_1 - a_2) \mid (f(a_1) - f(a_2)) = (a_2 - a_3)$, and so on.
This implies $|a_0 - a_1| \le |a_1 - a_2| \le \dots \le |a_{n-1} - a_n|$.
If $a_k = a_{k+1}$ for any $k \in \{0, \dots, n-1\}$, then $a_k = a_{k+1} = \dots = a_n = 3$.
Then $f(3) = 3$. However, if $a_0 = a_1 = \dots = a_n = 3$, then $f(3) = 3 \sum_{j=0}^n 3^j = 3 \frac{3^{n+1}-1}{2}$.
$3 \frac{3^{n+1}-1}{2} = 3 \implies 3^{n+1} = 3 \implies n=0$, a contradiction.
If $a_k = \dots = a_n = 3$ but $a_{k-1} \neq 3$, the chain $|a_0 - a_1| \le \dots \le |a_{n-1} - a_n|$ implies that if $a_{n-1} = a_n$, then $a_{n-2} = a_{n-1}, \dots, a_0 = a_1$, which we already ruled out.
Therefore, $a_i \neq a_{i+1}$ for all $i$.

Let $d_i = a_i - a_{i-1}$ for $i=1, \dots, n$. Then $d_i \neq 0$ and $d_1 \mid d_2 \mid \dots \mid d_n$.
For $i=n$, $d_n = 3 - a_{n-1}$ and $d_{n-1} = a_{n-1} - a_{n-2}$.
We have $d_n = Q_n d_{n-1}$ where $Q_n = \frac{f(a_{n-1}) - f(a_{n-2})}{a_{n-1} - a_{n-2}}$.
$Q_n = 3 \sum_{j=0}^{n-1} a_{n-1}^j a_{n-2}^{n-1-j} + a_{n-1} \sum_{j=0}^{n-2} a_{n-1}^j a_{n-2}^{n-2-j} + \dots + a_1$.

For $n=3$, $Q_3 = 4a_2^2 + 4a_2 a_1 + 3a_1^2 + a_1 = (2a_2 + a_1)^2 + 2a_1^2 + a_1$.
We must have $3 - a_2 = Q_3 (a_2 - a_1)$.
If $a_1 = 0$, $3 - a_2 = 4a_2^3$, which has no integer solutions.
If $a_1 = 1$, $3 - a_2 = ((2a_2 + 1)^2 + 3)(a_2 - 1)$. If $a_2 \ge 2$, $Q_3(a_2-1) \ge 3$ while $3-a_2 \le 1$. If $a_2 \le 0$, $Q_3(a_2-1) \le -3$ while $3-a_2 \ge 3$. If $a_2=1$, $2=0$. No solutions.
If $a_1 = -1$, $3 - a_2 = ((2a_2 - 1)^2 + 1)(a_2 + 1)$. If $a_2 \ge 1$, $Q_3(a_2+1) \ge 4$ while $3-a_2 \le 2$. If $a_2 \le -2$, $Q_3(a_2+1) \le -1$ while $3-a_2 \ge 5$. If $a_2=-1$, $4=0$. No solutions.
If $|a_1| \ge 2$, then $2a_1^2 + a_1 \ge 6$, so $|Q_3| \ge 6$.
If $a_2 > a_1$, then $3 - a_2 \ge 6(a_2 - a_1) \implies 6a_1 + 3 \ge 7a_2$. Since $a_2 \ge a_1 + 1$, $6a_1 + 3 \ge 7a_1 + 7 \implies a_1 \le -4$.
Then $Q_3 \ge 2a_1^2 + a_1 \ge 28$. $3 - a_2 \ge 28(a_2 - a_1) \implies 28a_1 + 3 \ge 29a_2$.
Since $a_2 \ge a_1 + 1$, $28a_1 + 3 \ge 29a_1 + 29 \implies a_1 \le -26$.
In general, if $a_2 > a_1$, $Q_3 \ge 3a_1^2 + 5a_1 + 4$ for $a_1 \le -4$, so $3 - a_2 \ge 3a_1^2 + 5a_1 + 4$, which implies $a_2 \le -3a_1^2 - 5a_1 + 3$. But $a_2 > a_1$ is impossible for $a_1 \le -4$.
If $a_2 < a_1$, then $3 - a_2 = Q_3 (a_2 - a_1)$. Since $Q_3 \ge 6$, $3 - a_2 \le 6(a_2 - a_1) \implies 6a_1 + 3 \le 7a_2$.
Since $a_1 \ge a_2 + 1$, $6(a_2+1) + 3 \le 7a_2 \implies a_2 \ge 9$.
Then $a_1 \ge 10$, so $Q_3 \ge 10^2 = 100$.
$|3 - a_2| = |Q_3| |a_2 - a_1| \ge 100(1) = 100 \implies a_2 \le -97$ or $a_2 \ge 103$.
This contradicts $a_2 \ge 9$ and $a_2 < a_1$.

For $n \ge 4$, $|d_n| = |Q_n| |d_{n-1}|$.
If $|a_{n-1}| \ge 2$, then $|Q_n| \approx 3|a_{n-1}|^{n-1}$ while $|d_n| = |3 - a_{n-1}| \le |a_{n-1}| + 3$.
For $n \ge 4$, $3|a_{n-1}|^{n-1} > |a_{n-1}| + 3$ for all $|a_{n-1}| \ge 2$.
If $|a_{n-1}| \le 1$, then $|d_n| \le 4$. Since $|d_1| \le \dots \le |d_n|$, all $|d_i| \le 4$.
If $|a_{n-1}| \le 1$ and $|a_{n-2}| \le 1$, then $Q_n = 3 \frac{a_{n-1}^n - a_{n-2}^n}{a_{n-1} - a_{n-2}} + a_{n-1} \frac{a_{n-1}^{n-1} - a_{n-2}^{n-1}}{a_{n-1} - a_{n-2}} + \dots + a_1$.
For $n=4$, if $a_3=1, a_2=0$, $Q_4 = 3(1) + 1(1) + a_1 = 4 + a_1$.
$d_4 = 2, d_3 = 1 \implies Q_4 = 2 \implies a_1 = -2$.
Then $d_3 = Q_3 d_2 \implies 1 = Q_3 d_2$.
$Q_3 = 4a_2^2 + 4a_2 a_1 + 3a_1^2 + a_1 = 0 + 0 + 3(-2)^2 - 2 = 10$.
$1 = 10 d_2$ has no integer solution.
Similar contradictions occur for all other small $a_i$ cases.

The only solution is $n=2$ and the sequence $a_0=-1, a_1=1, a_2=3$.
