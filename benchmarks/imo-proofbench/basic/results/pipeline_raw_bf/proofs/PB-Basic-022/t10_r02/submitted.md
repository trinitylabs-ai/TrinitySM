To find all polynomials $P$ with integer coefficients such that the equation $P(x) = s$ has an integer solution $x$ for every $s \in S = \{n^{2024} : n \in \mathbb{Z}_{\ge 0}\}$, let $k = 2024$. The condition states that for every $n \in \mathbb{Z}_{\ge 0}$, there exists $x_n \in \mathbb{Z}$ such that $P(x_n) = n^k$.

Let $d$ be the degree of $P$. Since $S$ is an infinite set, $P$ must be non-constant, so $d \ge 1$. As $|x| \to \infty$, we have $P(x) \sim a_d x^d$, where $a_d$ is the leading coefficient. For large $n$, the condition $P(x_n) = n^k$ implies $a_d x_n^d \approx n^k$, so $|x_n| \approx |n^{k/d} a_d^{-1/d}|$.

If $k/d$ is not an integer, let $\alpha = k/d$. The $m$-th order difference of the sequence $x_n$ is defined as $\Delta x_n = x_{n+1} - x_n$ and $\Delta^m x_n = \Delta(\Delta^{m-1} x_n)$. For $m > \alpha$, the growth rate of $x_n$ implies that $\Delta^m x_n \to 0$ as $n \to \infty$. Since $x_n$ are integers, $\Delta^m x_n$ are also integers. A sequence of integers that converges to 0 must eventually be constant at 0. Thus, $\Delta^m x_n = 0$ for all $n > N$ for some $N$. This implies that $x_n$ is eventually a polynomial in $n$, say $x_n = Q(n)$ for $n > N$, where $Q \in \mathbb{Q}[x]$.

Since $P(Q(n)) = n^k$ for all $n > N$, the polynomial identity $P(Q(x)) = x^k$ holds for all $x$. According to the theory of polynomial composition (Ritt's Theorem), if $P(Q(x)) = x^k$, then $P$ and $Q$ must be of the form $P(x) = a(x-b)^d$ and $Q(x) = c x^{k/d} + b$ for some constants $a, b, c$. Since $P(x) \in \mathbb{Z}[x]$, $a$ must be an integer and $b$ must be rational. Since $Q(n) \in \mathbb{Z}$ for all $n > N$, $Q$ must be a numerical polynomial, and given its form, $c$ and $b$ must be rational.

Substituting $Q(x)$ into $P(x)$, we get $P(Q(x)) = a(cx^{k/d})^d = ac^d x^k = x^k$, which implies $ac^d = 1$. Since $a$ is an integer, $a$ must be $\pm 1$.
1. If $a = 1$, then $c^d = 1$, so $c = \pm 1$. Then $P(x) = (x-b)^d$. For $P$ to have integer coefficients, $b$ must be an integer.
2. If $a = -1$, then $c^d = -1$. This is only possible if $d$ is odd, in which case $c = -1$. Then $P(x) = -(x-b)^d$. Again, $b$ must be an integer for $P$ to have integer coefficients.

We now test these candidates $P(x) = \epsilon(x+b)^d$ where $d|k, b \in \mathbb{Z}, \epsilon \in \{1, -1\}$:
- If $P(x) = (x+b)^d$, the equation $(x+b)^d = n^k$ becomes $x+b = \pm n^{k/d}$ (since $d|k$, $n^{k/d}$ is an integer). This always has integer solutions $x = \pm n^{k/d} - b$.
- If $P(x) = -(x+b)^d$ and $d$ is even, the equation $-(x+b)^d = n^k$ has no real solution for $n=1$ since $-(x+b)^d \le 0 < 1$.
- If $P(x) = -(x+b)^d$ and $d$ is odd, the equation $-(x+b)^d = n^k$ becomes $(x+b)^d = -n^k$, which implies $x+b = -n^{k/d}$. This always has an integer solution $x = -n^{k/d} - b$.

Thus, the polynomials $P$ are those of the form $P(x) = (x+b)^d$ for any divisor $d$ of 2024 and $b \in \mathbb{Z}$, and $P(x) = -(x+b)^d$ for any odd divisor $d$ of 2024 and $b \in \mathbb{Z}$.

\(\square\)
