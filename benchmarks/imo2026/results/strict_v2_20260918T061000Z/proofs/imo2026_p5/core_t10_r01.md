To determine all functions $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$ such that for all $x, y > 0$,
$$\sqrt{\frac{x^2 + f(y)^2}{2}} \ge \frac{f(x) + y}{2} \ge \sqrt{x f(y)},$$
we first test the candidate solution $f(x) = x + c$ for some constant $c \ge 0$. Substituting $f(x) = x + c$ into the given inequality:
$$\sqrt{\frac{x^2 + (y + c)^2}{2}} \ge \frac{x + c + y}{2} \ge \sqrt{x(y + c)}.$$
Let $A = x$ and $B = y + c$. Since $x, y > 0$ and $c \ge 0$, we have $A, B > 0$. The inequality becomes $\text{RMS}(A, B) \ge \text{AM}(A, B) \ge \text{GM}(A, B)$, which is the standard RMS-AM-GM inequality. Thus, $f(x) = x + c$ for any $c \ge 0$ is a solution.

To prove uniqueness, consider the case where $x = f(y)$. The given inequality becomes:
$$\sqrt{\frac{f(y)^2 + f(y)^2}{2}} \ge \frac{f(f(y)) + y}{2} \ge \sqrt{f(y) f(y)} \implies f(y) \ge \frac{f(f(y)) + y}{2} \ge f(y).$$
This forces $f(f(y)) - 2f(y) + y = 0$ for all $y > 0$. Let $g(x) = f(x) - x$. The recurrence $f(f(y)) = 2f(y) - y$ implies $g(f(y)) = f(f(y)) - f(y) = f(y) - y = g(y)$. For any $y_0 > 0$, the sequence $y_{n+1} = f(y_n)$ satisfies $y_n = y_0 + n g(y_0)$. Since $f: \mathbb{R}_{>0} \to \mathbb{R}_{>0}$, we must have $y_n > 0$ for all $n \in \mathbb{N}$, which implies $g(y_0) \ge 0$ for all $y_0 > 0$.

Squaring the given inequalities and substituting $f(x) = x + g(x)$:
1. $\frac{x^2 + (y + g(y))^2}{2} \ge \frac{(x + g(x) + y)^2}{4} \implies (x - y)^2 + 2y(2g(y) - g(x)) + 2g(y)^2 - g(x)^2 - 2xg(x) \ge 0$.
2. $\frac{(x + g(x) + y)^2}{4} \ge x(y + g(y)) \implies (x - y)^2 + g(x)^2 + 2xg(x) + 2yg(x) - 4xg(y) \ge 0$.

Suppose $g$ is not constant. Then there exist $x_0, y_0$ such that $g(x_0) = c_1$ and $g(y_0) = c_2$ with $c_1 \neq c_2$. Let $x_n = x_0 + n c_1$ and $y_m = y_0 + m c_2$. Then $g(x_n) = c_1$ and $g(y_m) = c_2$ for all $n, m \in \mathbb{N}$.

Case 1: $c_1, c_2 > 0$ and $c_1 < c_2$. Using Inequality 2:
$$(x_n - y_m)^2 + c_1^2 + 2x_n c_1 + 2y_m c_1 - 4x_n c_2 \ge 0.$$
Choose $n, m$ such that $|x_n - y_m|$ is bounded. If $c_1/c_2 = p/q$ for $p, q \in \mathbb{N}$, let $n=qk, m=pk$. Then $x_n - y_m = x_0 - y_0$. The linear terms are $2(qk)c_1^2 + 2(pk)c_2 c_1 - 4(qk)c_1 c_2 = 4k p c_2(c_1 - c_2)$. Since $c_1 < c_2$, this tends to $-\infty$ as $k \to \infty$, a contradiction. If $c_1/c_2$ is irrational, we can similarly find $n, m$ such that $|x_n - y_m| < 1$ and the linear terms $4n c_1(c_1 - c_2)$ dominate and tend to $-\infty$.

Case 2: $c_1, c_2 > 0$ and $c_1 > c_2$. Using Inequality 1:
$$(x_n - y_m)^2 + 2y_m(2c_2 - c_1) + 2c_2^2 - c_1^2 - 2x_n c_1 \ge 0.$$
Again, choose $n, m$ such that $|x_n - y_m|$ is bounded. With $m c_2 \approx n c_1$, the linear terms are $2n c_1(2c_2 - c_1) - 2n c_1^2 = 4n c_1(c_2 - c_1)$. Since $c_2 < c_1$, this tends to $-\infty$ as $n \to \infty$, a contradiction.

Case 3: $g$ takes a positive value $c_1 > 0$ and the value $0$. Let $S_0 = \{x : g(x) = 0\}$ and $S_{c_1} = \{x : g(x) = c_1\}$. If both are non-empty, Inequality 1 for $x \in S_{c_1}, y \in S_0$ becomes $(x - y)^2 \ge 2c_1(x + y) + c_1^2$. For a fixed $y \in S_0$, $x \in S_{c_1}$ must avoid the interval $(y + c_1 - \sqrt{4yc_1 + 2c_1^2}, y + c_1 + \sqrt{4yc_1 + 2c_1^2})$. The length of this interval is $L = 2\sqrt{4yc_1 + 2c_1^2} > 2\sqrt{2}c_1 > c_1$. Since $x_n = x_0 + n c_1$ has gaps of $c_1$ and $x_n \to \infty$, the sequence must eventually enter the interval unless all $x_n$ are to the right of it. Thus, $x_0 > y + c_1 + \sqrt{4yc_1 + 2c_1^2}$ for all $y \in S_0$, implying $S_0$ is bounded. 

Now use Inequality 2 for $x \in S_0, y \in S_{c_1}$: $(x - y)^2 \ge 4xc_1$. For a fixed $x \in S_0$, $y \in S_{c_1}$ must avoid $(x - \sqrt{4xc_1}, x + \sqrt{4xc_1})$. Since $y_n = y_0 + n c_1 \to \infty$, this requires $y_0 > x + \sqrt{4xc_1}$ for all $x \in S_0$. If $g$ takes any other value $c$, Case 1 or 2 applies. Thus $g(x) \in \{0, c_1\}$ for all $x$. This implies $S_0 \cup S_{c_1} = \mathbb{R}_{>0}$, so $S_0 = (0, b]$ and $S_{c_1} = (b, \infty)$ for some $b > 0$. However, for $x = b$ and $y = b + \epsilon$, Inequality 2 becomes $\epsilon^2 \ge 4bc_1$, which is false for sufficiently small $\epsilon$.

Thus, $g(x)$ must be a constant $c \ge 0$. The functions are $f(x) = x + c$ for any constant $c \ge 0$.