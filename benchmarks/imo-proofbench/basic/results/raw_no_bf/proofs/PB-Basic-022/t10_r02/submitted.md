To find all polynomials $P(x) \in \mathbb{Z}[x]$ such that $P(x) = s$ has an integer solution $x$ for every $s \in S = \{n^{2024} : n \in \mathbb{Z}_{\ge 0}\}$, let $k = 2024$. The condition states that for every $n \in \mathbb{Z}_{\ge 0}$, there exists $x_n \in \mathbb{Z}$ such that $P(x_n) = n^k$.

Let $d = \deg(P)$. If $d=0$, $P(x) = C$, which cannot equal $n^k$ for all $n$. Thus $d \ge 1$. For large $n$, $P(x_n) = a_d x_n^d + a_{d-1}x_n^{d-1} + \dots + a_0 = n^k$. As $n \to \infty$, $x_n$ must also grow. Specifically, $a_d x_n^d \sim n^k$, which implies $|x_n| \sim |n^k/a_d|^{1/d} = n^{k/d} |a_d|^{-1/d}$. For $x_n$ to be an integer for all sufficiently large $n$, the exponent $k/d$ must be an integer $m$. Thus $d$ must be a divisor of $k$.

Let $k=md$. We have $|x_n| \sim n^m |a_d|^{-1/d}$. For $x_n$ to be an integer for all $n$, $|a_d|^{-1/d}$ must be a rational $p/q$. Then $|a_d| = (q/p)^d$. Since $a_d \in \mathbb{Z}$, $p$ must divide $q$, so $|a_d|$ is a $d$-th power of an integer. Let $|a_d| = a^d$. Then $|x_n| \sim n^m/a$. For this to be an integer for all $n$, we must have $a=1$, so $|a_d|=1$. Thus $a_d = \pm 1$.

If $a_d = 1$, then $x_n \sim n^m$. Let $x_n = n^m + \delta_n$. Substituting into the polynomial:
$(n^m + \delta_n)^d + a_{d-1}(n^m + \delta_n)^{d-1} + \dots = n^{md}$
$n^{md} + d n^{m(d-1)}\delta_n + a_{d-1}n^{m(d-1)} + O(n^{m(d-2)}) = n^{md}$
$(d \delta_n + a_{d-1}) n^{m(d-1)} + O(n^{m(d-2)}) = 0$.
As $n \to \infty$, we must have $\delta_n \to -a_{d-1}/d$. Since $\delta_n$ is an integer, $\delta_n$ must be a constant $c$ for all large $n$. Thus $P(n^m + c) = n^{md}$ is a polynomial identity. Let $y = n^m + c$, then $n^m = y-c$, and $P(y) = (y-c)^d$. Since the coefficients are integers, $c$ must be an integer.

If $a_d = -1$, we have $-x_n^d \sim n^k$, which implies $x_n^d \sim -n^k$. For $n \ge 1$, $n^k > 0$, so we require $x_n^d < 0$. This is only possible if $d$ is odd. If $d$ is odd, we can write $P(x) = -(x-c)^d$ for some integer $c$. Then $-(x-c)^d = n^k \implies (x-c)^d = -n^k \implies x-c = -n^{k/d} \implies x = c - n^{k/d}$, which is always an integer since $d|k$.

Verification of solutions:
1. If $P(x) = (x+c)^d$ where $d|2024$ and $c \in \mathbb{Z}$, then for $s=n^{2024}$, $x = n^{2024/d} - c$ is an integer solution.
2. If $P(x) = -(x+c)^d$ where $d|2024$, $d$ is odd, and $c \in \mathbb{Z}$, then for $s=n^{2024}$, $(x+c)^d = -n^{2024} \implies x+c = -n^{2024/d} \implies x = -n^{2024/d} - c$ is an integer solution.

All such polynomials are of the form $P(x) = (x+c)^d$ for $d|2024, c \in \mathbb{Z}$ or $P(x) = -(x+c)^d$ for $d|2024, d \in \{1, 11, 23, 253\}, c \in \mathbb{Z}$.

The polynomials $P$ are $P(x) = (x+c)^d$ for any $d \in \text{Div}(2024)$ and $c \in \mathbb{Z}$, and $P(x) = -(x+c)^d$ for any odd $d \in \text{Div}(2024)$ and $c \in \mathbb{Z}$. $\square$
