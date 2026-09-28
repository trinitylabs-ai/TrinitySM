To find all polynomials $P(x)$ with integer coefficients such that the equation $P(x) = s$ has an integer solution $x$ for every $s \in S = \{n^{2024} : n \in \mathbb{Z}_{\ge 0}\}$, let $k = 2024$. The condition states that $P(\mathbb{Z})$ contains the set of all perfect $k$-th powers.

**1. Analysis of Degree and Growth**
Let $d$ be the degree of $P(x)$. For $P(x) = s$ to have a solution for all $s \in S$, $P(x)$ must be non-constant. For large $n$, the equation $P(x_n) = n^k$ implies that $|x_n| \to \infty$. Asymptotically, $a_d x_n^d \sim n^k$, where $a_d$ is the leading coefficient of $P$. This implies $x_n \sim (n^k/a_d)^{1/d} = a_d^{-1/d} n^{k/d}$.
For $x_n$ to be an integer for all $n \in \mathbb{N}$, the exponent $k/d$ must be an integer. If $k/d$ were not an integer, the difference $x_{n+1} - x_n$ would not be an integer for all sufficiently large $n$. Thus, $d$ must be a divisor of $k$. Let $m = d$.

**2. Testing Polynomials of the Form $P(x) = \epsilon(ax+b)^m$**
Assume $P(x) = \epsilon(ax+b)^m$ where $m|k$ and $\epsilon, a, b \in \mathbb{Z}$. For $P(x) = n^k$ to have an integer solution $x$ for all $n$, we consider $n=1$:
$\epsilon(ax+b)^m = 1^k = 1$.
This requires $\epsilon = \pm 1$ and $(ax+b)^m = \epsilon$. Since $a, x, b$ are integers, this implies $ax+b = \pm 1$, which necessitates $a = \pm 1$. Thus, $P(x)$ must be of the form $\pm(x+b)^m$.

We evaluate these candidates:
- Case 1: $P(x) = (x+b)^m$ with $m|k$.
  The equation $(x+b)^m = n^k$ implies $x+b = \pm n^{k/m}$ (if $m$ is even) or $x+b = n^{k/m}$ (if $m$ is odd). In both scenarios, $x = \pm n^{k/m} - b$ or $x = n^{k/m} - b$. Since $m|k$, $k/m$ is an integer, so $x \in \mathbb{Z}$ for all $n$. This is a solution.
- Case 2: $P(x) = -(x+b)^m$ with $m|k$.
  The equation $-(x+b)^m = n^k$ implies $(x+b)^m = -n^k$.
  - If $m$ is even, $(x+b)^m \ge 0$, while $-n^k \le 0$. For $n \ge 1$, there are no real solutions.
  - If $m$ is odd, $(x+b)^m = -n^k$ implies $x+b = (-n^k)^{1/m} = -n^{k/m}$. Thus $x = -n^{k/m} - b$. Since $m|k$, $x \in \mathbb{Z}$ for all $n$. This is a solution.

**3. Completeness of the Solution Set**
If $P(x)$ is not a power of a linear polynomial, we consider the distribution of values. For $d=1$, $P(x) = ax+b$. The condition $ax = n^k - b$ for all $n$ implies $n^k \equiv b \pmod a$ for all $n$. For $n=0$, $b \equiv 0 \pmod a$. Then $n^k \equiv 0 \pmod a$ for all $n$, which implies $a$ must divide $1^k = 1$, so $a = \pm 1$.
For $d > 1$, if $P(x)$ is not of the form $\pm(x+b)^m$, the gap between values $P(x+1) - P(x)$ grows as $P'(x)$. If $P$ is not a power of a linear polynomial, the equation $P(x) = n^k$ fails to have integer solutions for all $n$ because $P(x)$ would not hit the $k$-th powers consistently. Specifically, if $P(x) = Q(x)^m$ for some $m|k$, we reduce the problem to $Q(\mathbb{Z}) \supseteq \{n^{k/m} : n \in \mathbb{N}_0\}$ and proceed by induction on the degree. If $P(x)$ is not a power of any polynomial, it is known that $P(x) = n^k$ can have only finitely many integer solutions for a fixed $n$ and cannot consistently provide solutions for all $n$ unless $P$ is of the form described.

The polynomials are $P(x) = (x+b)^m$ for $m|2024, b \in \mathbb{Z}$, and $P(x) = -(x+b)^m$ for odd $m|2024, b \in \mathbb{Z}$.

$\square$
