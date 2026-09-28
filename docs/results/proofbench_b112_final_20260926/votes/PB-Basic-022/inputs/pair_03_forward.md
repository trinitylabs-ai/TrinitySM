# Problem

Let $S=\{0,1,2^{2024},3^{2024},\ldots\}$ be the set of all perfect
 2024-th powers. Find all polynomials $P$ with integer coefficients
 such that $P(x)=s$ has an integer solution $x$ for every $s\in S$.

# Proof A

1: Let $k = 2024$ and $S = \{n^k : n \in \mathbb{Z}_{\ge 0}\}$. We seek all polynomials $P \in \mathbb{Z}[x]$ such that for every $s \in S$, the equation $P(x) = s$ has an integer solution $x$. This means that for every $n \in \mathbb{N}_0$, there exists $x_n \in \mathbb{Z}$ such that $P(x_n) = n^k$.
2: 
3: Let $d$ be the degree of $P$. If $d=0$, $P(x) = C$, which cannot equal $n^k$ for all $n$. Thus $d \ge 1$. Let $P(x) = a_d x^d + a_{d-1} x^{d-1} + \dots + a_0$ with $a_d \neq 0$. As $n \to \infty$, $n^k \to \infty$, which implies $|x_n| \to \infty$. For sufficiently large $n$, $P(x)$ is strictly monotonic for $|x| > R$, so $x_n$ is uniquely determined for $n > N$.
4: 
5: The solution $x_n$ to $P(x) = n^k$ has an asymptotic expansion as $n \to \infty$ of the form:
6: \[ x_n = c_m n^m + c_{m-1} n^{m-1} + \dots + c_0 + c_{-1} n^{-1} + \dots \]
7: where $m = k/d$. Let $\Delta$ be the forward difference operator $\Delta x_n = x_{n+1} - x_n$. It is a known property of the difference operator that for any $m \in \mathbb{R}$, $\Delta^{\lfloor m \rfloor + 1} n^m = O(n^{m - (\lfloor m \rfloor + 1)})$. Since $m - \lfloor m \rfloor - 1 < 0$, we have $\Delta^{\lfloor m \rfloor + 1} x_n \to 0$ as $n \to \infty$.
8: Because $x_n$ are integers, $\Delta^{\lfloor m \rfloor + 1} x_n$ must also be integers. A sequence of integers that converges to $0$ must eventually be $0$. Thus, $\Delta^{\lfloor m \rfloor + 1} x_n = 0$ for all $n > N_0$. This implies that $x_n$ is a polynomial $Q(n)$ for $n > N_0$.
9: Since $P(Q(n)) = n^k$ for all $n > N_0$, the polynomial identity $P(Q(x)) = x^k$ holds for all $x$.
10: 
11: Let $m = \deg Q$. Then $dm = k$. Let $r$ be a root of $P(x)$ in $\mathbb{C}$. Then $P(Q(x)) = x^k$ implies that $Q(x) - r$ must be a factor of $x^k$. Thus, $Q(x) - r = c_r x^m$ for some constant $c_r$.
12: If $P$ had two distinct roots $r_1$ and $r_2$, then $Q(x) = c_{r_1} x^m + r_1$ and $Q(x) = c_{r_2} x^m + r_2$. Subtracting these yields $(c_{r_1} - c_{r_2}) x^m = r_2 - r_1$. For this to hold for all $x$, we must have $c_{r_1} = c_{r_2}$ and $r_1 = r_2$, a contradiction. Thus, $P(x)$ has only one distinct root $r$, so $P(x) = a(x-r)^d$.
13: 
14: Since $P \in \mathbb{Z}[x]$, the leading coefficient $a$ must be an integer. Also, $P(x) = a(x^d - drx^{d-1} + \dots + r^d)$, so $adr \in \mathbb{Z}$, which implies $r \in \mathbb{Q}$. Let $r = p/q$ in lowest terms. Then $P(x) = a(x - p/q)^d = \frac{a}{q^d}(qx - p)^d$. For $P(x)$ to have integer coefficients and $\gcd(p,q)=1$, $q^d$ must divide $a$.
15: For $n=0$, $P(x_0) = 0$ implies $a(x_0 - r)^d = 0$, so $x_0 = r$. Since $x_0$ is an integer, $r$ must be an integer. Let $r = -b$ for some $b \in \mathbb{Z}$. Then $P(x) = a(x+b)^d$.
16: For $n=1$, $P(x_1) = 1$ implies $a(x_1+b)^d = 1$. Since $a$ and $x_1+b$ are integers, we must have $a = \pm 1$.
17: 
18: Case 1: $a = 1$.
19: $P(x) = (x+b)^d$. The equation $(x+b)^d = n^k$ has an integer solution $x = n^{k/d} - b$ for all $n \in \mathbb{N}_0$ if and only if $k/d$ is an integer. Thus $d$ must be a divisor of $k = 2024$.
20: 
21: Case 2: $a = -1$.
22: $P(x) = -(x+b)^d$. The equation $-(x+b)^d = n^k$ implies $(x+b)^d = -n^k$. If $d$ is even, there are no real solutions for $n \ge 1$. If $d$ is odd, $x+b = -n^{k/d}$, which has an integer solution $x = -n^{k/d} - b$ for all $n \in \mathbb{N}_0$ if and only if $k/d$ is an integer. Thus $d$ must be an odd divisor of $k = 2024$.
23: 
24: The polynomials are $P(x) = (x+b)^d$ for $d|2024, b \in \mathbb{Z}$ and $P(x) = -(x+b)^d$ for odd $d|2024, b \in \mathbb{Z}$.

# Proof B

1: Let $k = 2024$. We seek all polynomials $P(x) \in \mathbb{Z}[x]$ such that for every $n \in \mathbb{Z}_{\ge 0}$, the equation $P(x) = n^k$ has an integer solution $x_n$.
2: 
3: **1. Establishing that $x_n$ is eventually a polynomial**
4: Let $d$ be the degree of $P(x)$. If $P$ is constant, $P(x) = C$, then $C = n^k$ for all $n \in \mathbb{Z}_{\ge 0}$, which is impossible. Thus $d \ge 1$. Let $P(x) = a_d x^d + a_{d-1} x^{d-1} + \dots + a_0$ with $a_d \neq 0$.
5: The equation $P(x) - n^k = 0$ defines $x$ as an algebraic function of $n$. According to the theory of Puiseux series, for sufficiently large $n$, the solutions $x(n)$ can be represented as series of the form:
6: $$x(n) = \sum_{j=0}^\infty c_j n^{r_j}$$
7: where $r_0 > r_1 > r_2 > \dots$ are decreasing rational numbers. Comparing the leading terms of $P(x) = n^k$, we have $a_d x^d \sim n^k$, so $x \sim (a_d^{-1})^{1/d} n^{k/d}$. Thus, the leading exponent is $r_0 = k/d$.
8: 
9: For large $n$, the solutions $x_{n,j}$ to $P(x) = n^k$ are distributed among $d$ branches. For a solution $x_n$ to be an integer, it must belong to a real branch. If $d$ is even, there are at most two real branches; if $d$ is odd, there is at most one. Let these real branches be $R_1(n), \dots, R_s(n)$ (where $s \le 2$). 
10: If $x_n$ eventually stays on one branch $R_i(n)$, then $x_n$ is represented by a Puiseux series. The forward difference operator $\Delta f(n) = f(n+1) - f(n)$ acts on $n^r$ such that $\Delta^m (n^r) \sim C n^{r-m}$. Thus, $\Delta^m x_n$ is also a Puiseux series whose leading term is proportional to $n^{r_0-m}$. By choosing an integer $m > r_0 = k/d$, we have $\lim_{n \to \infty} \Delta^m x_n = 0$.
11: If $x_n$ switches between different real branches $R_i(n)$ and $R_j(n)$ infinitely often, then $\Delta x_n$ would be approximately $R_i(n) - R_j(n) \sim n^{k/d}$, which does not converge to 0, nor do higher differences.
12: Since $x_n$ is an integer for all $n$, $\Delta^m x_n$ is also an integer. An integer sequence that converges to 0 must be eventually zero. Thus, there exists $N$ such that $\Delta^m x_n = 0$ for all $n \ge N$, which implies $x_n$ is eventually a polynomial $Q(n) \in \mathbb{Q}[n]$.
13: Consequently, the identity $P(Q(n)) = n^k$ holds for all $n \ge N$, and since both are polynomials, $P(Q(x)) = x^k$ for all $x$.
14: 
15: **2. Solving the Functional Equation $P(Q(x)) = x^k$**
16: Let $d = \deg P$ and $q = \deg Q$, so $dq = k$. Differentiating $P(Q(x)) = x^k$ gives:
17: $$P'(Q(x)) Q'(x) = k x^{k-1}$$
18: The only root of the right-hand side is $x = 0$. Thus, any root of $Q'(x)$ must be $0$. Since $\deg Q' = q-1$, we have $Q'(x) = c x^{q-1}$ for some constant $c$. Integrating gives:
19: $$Q(x) = \frac{c}{q} x^q + b$$
20: Substituting this into the derivative equation:
21: $$P'(Q(x)) \cdot c x^{q-1} = k x^{k-1} \implies P'(Q(x)) = \frac{k}{c} x^{k-q}$$
22: Let $z = Q(x) = \frac{c}{q} x^q + b$. Then $x^q = \frac{q}{c}(z-b)$. Substituting this into the expression for $P'(z)$:
23: $$P'(z) = \frac{k}{c} \left( \frac{q}{c}(z-b) \right)^{\frac{k-q}{q}} = \frac{k}{c} \left( \frac{q}{c} \right)^{d-1} (z-b)^{d-1}$$
24: Integrating $P'(z) = A(z-b)^{d-1}$ gives $P(z) = a_d(z-b)^d + C$.
25: Substituting $P$ and $Q$ back into $P(Q(x)) = x^k$:
26: $$a_d \left( \frac{c}{q} x^q + b - b \right)^d + C = a_d \left( \frac{c}{q} \right)^d x^{dq} + C = x^k$$
27: This implies $C = 0$ and $a_d (c/q)^d = 1$. Thus, $P(x) = a_d (x-b)^d$.
28: 
29: **3. Determining Integer Coefficients and Solutions**
30: Since $P(x) \in \mathbb{Z}[x]$, the leading coefficient $a_d$ must be an integer.
31: For $n=0$, $P(x_0) = a_d (x_0-b)^d = 0$, which implies $x_0 = b$. Since $x_0 \in \mathbb{Z}$, $b$ must be an integer.
32: For $n=1$, $P(x_1) = a_d (x_1-b)^d = 1$. Since $a_d, x_1, b \in \mathbb{Z}$, we must have $a_d = \pm 1$.
33: 
34: - **Case 1: $a_d = 1$.** $P(x) = (x-b)^d$. The equation $(x-b)^d = n^k$ must have an integer solution $x$ for all $n$. This requires $n^{k/d}$ to be an integer for all $n$, so $d$ must divide $k$. Let $m=d$. Then $m|2024$.
35: - **Case 2: $a_d = -1$.** $P(x) = -(x-b)^d$. The equation $-(x-b)^d = n^k$ must have an integer solution $x$ for all $n$. If $d$ is even, $-(x-b)^d \le 0$, so no solution exists for $n \ge 1$. If $d$ is odd, $(x-b)^d = -n^k$ implies $x-b = -n^{k/d}$. This requires $d$ to divide $k$. Let $m=d$. Then $m|2024$ and $m$ is odd.
36: 
37: Replacing $-b$ with $b$ (as $b$ is an arbitrary integer), the polynomials are:
38: $P(x) = (x+b)^m$ where $m|2024, b \in \mathbb{Z}$, and $P(x) = -(x+b)^m$ where $m|2024, m$ is odd, $b \in \mathbb{Z}$.
39: 
40: The set of all such polynomials is $\{P(x) = (x+b)^m : m|2024, b \in \mathbb{Z}\} \cup \{P(x) = -(x+b)^m : m|2024, m \text{ is odd}, b \in \mathbb{Z}\}$.
