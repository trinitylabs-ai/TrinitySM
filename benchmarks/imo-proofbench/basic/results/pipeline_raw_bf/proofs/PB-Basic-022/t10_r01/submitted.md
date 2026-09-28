To find all polynomials $P(x)$ with integer coefficients such that $P(x) = s$ has an integer solution $x$ for every $s \in S = \{n^{2024} \mid n \in \mathbb{Z}_{\ge 0}\}$, let $k = 2024$. The condition is that for every $n \in \mathbb{Z}_{\ge 0}$, there exists an integer $x$ such that $P(x) = n^k$.

**1. Analysis of the Degree and Leading Coefficient**
Let $d$ be the degree of $P$. If $P(x) = C$ is a constant, then $C = n^k$ for all $n \in \mathbb{Z}_{\ge 0}$, which is impossible since $S$ is an infinite set. Thus $d \ge 1$.
For each $n$, let $x_n$ be an integer solution to $P(x_n) = n^k$. As $n \to \infty$, $x_n$ must also tend to infinity. If $P(x) = a_d x^d + a_{d-1} x^{d-1} + \dots + a_0$, then $a_d x_n^d \approx n^k$. This implies $|x_n| \approx |n|^{k/d} |a_d|^{-1/d}$.
For $x_n$ to be an integer for all $n$, the growth rate $|n|^{k/d}$ suggests that $k/d$ must be an integer. Let $m = k/d$. Then $x_n \approx |a_d|^{-1/d} n^m$. For $x_n$ to be an integer for all $n$, $|a_d|^{-1/d}$ must be a rational number. Since $a_d$ is an integer, this implies $a_d$ must be a perfect $d$-th power, say $a_d = a^d$ for some $a \in \mathbb{Z}$. Then $x_n \approx \frac{1}{a} n^m$. For $x_n$ to be an integer for all $n$, we must have $a = \pm 1$, so $a_d = (\pm 1)^d$. Thus, the leading coefficient of $P$ is $a_d = 1$ or $a_d = -1$.

**2. Determining the Form of $P(x)$**
Consider the case $d=k$. Then $x_n \approx \pm n$. Let $x_n = \pm n + \delta$. Substituting this into $P(x) = n^k$, the binomial expansion of $P(\pm n + \delta)$ must match $n^k$ for all $n$. This forces $P(x)$ to be of the form $(x+b)^k$ or $-(x+b)^k$.
If $d < k$ and $m = k/d$, then $x_n \approx \pm n^m$. Similarly, the requirement that $x_n$ is an integer for all $n$ implies that $P(x)$ must be of the form $a(x+b)^d$ for some $a \in \mathbb{Z}$ and $b \in \mathbb{Z}$.

**3. Testing the Form $P(x) = a(x+b)^d$**
We check which values of $a, b, d$ satisfy the condition $a(x+b)^d = n^k$ for all $n \in \mathbb{Z}_{\ge 0}$.
- For $n=0$, $a(x+b)^d = 0$ always has the solution $x = -b$.
- For $n=1$, $a(x+b)^d = 1$. Since $a, x, b$ are integers, this requires $a = \pm 1$.
    - If $a=1$, then $(x+b)^d = 1$, which has the solution $x = 1-b$.
    - If $a=-1$, then $-(x+b)^d = 1$, so $(x+b)^d = -1$. This requires $d$ to be odd, and has the solution $x = -1-b$.
- For $n=2$, we require $a(x+b)^d = 2^k$ to have an integer solution $x$.
    - If $a=1$, $(x+b)^d = 2^k \implies x+b = \pm 2^{k/d}$. This requires $d$ to be a divisor of $k$.
    - If $a=-1$, $-(x+b)^d = 2^k \implies (x+b)^d = -2^k$. Since $d$ must be odd (from the $n=1$ case), $x+b = -2^{k/d}$. This also requires $d$ to be a divisor of $k$.

**4. Final Verification**
- If $P(x) = (x+b)^d$ with $d|k$, then for any $n^k \in S$, $(x+b)^d = n^k \implies x+b = \pm n^{k/d}$ (if $d$ is even) or $x+b = n^{k/d}$ (if $d$ is odd). In both cases, $x$ is an integer.
- If $P(x) = -(x+b)^d$ with $d|k$ and $d$ odd, then for any $n^k \in S$, $-(x+b)^d = n^k \implies (x+b)^d = -n^k \implies x+b = -n^{k/d}$. Since $d|k$, $x = -n^{k/d} - b$ is an integer.
- If $P(x) = -(x+b)^d$ with $d$ even, then $P(x) \le 0$ for all $x$, so $P(x) = n^k$ has no solution for $n \ge 1$.

Thus, the polynomials are $P(x) = (x+b)^d$ where $d|2024, b \in \mathbb{Z}$, and $P(x) = -(x+b)^d$ where $d|2024, d$ is odd, $b \in \mathbb{Z}$.

The polynomials are $P(x) = (x+b)^d$ for $d|2024, b \in \mathbb{Z}$ and $P(x) = -(x+b)^d$ for odd $d|2024, b \in \mathbb{Z}$. \(\square\)
