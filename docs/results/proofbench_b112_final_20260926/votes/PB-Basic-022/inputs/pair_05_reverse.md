# Problem

Let $S=\{0,1,2^{2024},3^{2024},\ldots\}$ be the set of all perfect
 2024-th powers. Find all polynomials $P$ with integer coefficients
 such that $P(x)=s$ has an integer solution $x$ for every $s\in S$.

# Proof A

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

# Proof B

1: To find all polynomials $P(x) \in \mathbb{Z}[x]$ such that the equation $P(x) = s$ has an integer solution $x$ for every $s \in S = \{n^{2024} \mid n \in \mathbb{Z}_{\ge 0}\}$, let $k = 2024$. The condition is that for every $n \in \mathbb{Z}_{\ge 0}$, there exists $x \in \mathbb{Z}$ such that $P(x) = n^k$.
2: 
3: 1. **Degree and Growth Analysis:**
4: Let $d$ be the degree of $P$. If $P$ is a constant $C$, then $C = n^k$ for all $n \in \mathbb{Z}_{\ge 0}$, which is impossible. Thus $d \ge 1$. For each $n \in \mathbb{Z}_{\ge 0}$, let $x_n$ be the largest integer such that $P(x_n) = n^k$. As $n \to \infty$, $n^k \to \infty$, so $|x_n|$ must also tend to infinity. Let $P(x) = a_d x^d + a_{d-1} x^{d-1} + \dots + a_0$. For $P(x)$ to take arbitrarily large positive values, we must have $a_d > 0$ if $d$ is even.
5: 
6: As $n \to \infty$, the largest real root of $P(x) = n^k$ behaves as $x \sim (n^k/a_d)^{1/d} = a_d^{-1/d} n^{k/d}$. Since $x_n$ is the largest integer solution, it must be close to this root. Specifically, we have:
7: $n^k = a_d x_n^d \left(1 + \frac{a_{d-1}}{a_d x_n} + O(x_n^{-2})\right)$
8: $x_n = \left(\frac{n^k}{a_d}\right)^{1/d} \left(1 + \frac{a_{d-1}}{a_d x_n} + O(x_n^{-2})\right)^{-1/d} = a_d^{-1/d} n^{k/d} \left(1 - \frac{a_{d-1}}{d a_d x_n} + O(x_n^{-2})\right)$
9: Since $x_n \sim a_d^{-1/d} n^{k/d}$, the term $\frac{a_{d-1}}{d a_d x_n} n^{k/d}$ converges to a constant. Thus, $x_n = a_d^{-1/d} n^{k/d} + C + O(n^{k/d-1})$ for some constant $C$.
10: 
11: Let $m = \lceil k/d \rceil$. The $m$-th order difference $\Delta^m x_n$ of a sequence behaving like $n^{k/d}$ tends to 0 as $n \to \infty$ if $k/d < m$, or is constant if $k/d = m$. Since $x_n$ are integers, $\Delta^m x_n$ are also integers. A sequence of integers tending to 0 must eventually be 0. Thus, $\Delta^m x_n$ is eventually constant, which implies that $x_n$ is a polynomial $Q(n)$ for $n \ge N$.
12: 
13: Since $x_n = Q(n)$ for $n \ge N$, the identity $P(Q(n)) = n^k$ holds for all $n \ge N$. Since both sides are polynomials, the identity $P(Q(x)) = x^k$ must hold for all $x$. Comparing degrees, we have $\deg(P) \cdot \deg(Q) = k$, so $d \cdot \deg(Q) = k$, which implies $d$ is a divisor of $k$ and $m = k/d$ is an integer.
14: 
15: 2. **Form of the Polynomial:**
16: We have the polynomial identity $P(Q(x)) = x^k$. Let $P(x) = a_d \prod_{i=1}^j (x-r_i)^{e_i}$ be the factorization of $P$ over $\mathbb{C}$. Then $a_d \prod_{i=1}^j (Q(x)-r_i)^{e_i} = x^k$. This implies that each factor $Q(x)-r_i$ must be a monomial of the form $c_i x^{m_i}$ for some $c_i \in \mathbb{C}$.
17: Thus, $Q(x) = c_i x^{m_i} + r_i$ for all $i=1, \dots, j$. If $j > 1$, then for any two distinct roots $r_1, r_2$, we have $c_1 x^{m_1} + r_1 = c_2 x^{m_2} + r_2$. This can only hold if $m_1 = m_2$ and $c_1 = c_2$, which implies $r_1 = r_2$, a contradiction. Therefore, $P(x)$ must have only one distinct root $r$.
18: 
19: Thus, $P(x) = a_d(x-r)^d$. Substituting this into $P(Q(x)) = x^k$, we get $a_d(Q(x)-r)^d = x^k$. This implies $Q(x)-r = c x^{k/d}$ for some constant $c$, and $a_d c^d = 1$.
20: Since $Q(n)$ is an integer for all $n \ge N$, we have $Q(n) = c n^{k/d} + r \in \mathbb{Z}$. Let $m = k/d$. Then $Q(n+1) - Q(n) = c((n+1)^m - n^m) \in \mathbb{Z}$ for all $n \ge N$. Let $c = p/q$ in lowest terms. Then $q$ must divide $p((n+1)^m - n^m)$ for all $n \ge N$, and since $\gcd(p,q)=1$, $q$ must divide $(n+1)^m - n^m$ for all $n \ge N$. For $n=q$, we have $(q+1)^m \equiv q^m \pmod{q}$, which simplifies to $1 \equiv 0 \pmod{q}$, forcing $q=1$. Thus $c$ is an integer.
21: Since $Q(n) = cn^m + r \in \mathbb{Z}$ and $cn^m \in \mathbb{Z}$, it follows that $r$ is also an integer.
22: The condition $a_d c^d = 1$ with $a_d, c \in \mathbb{Z}$ implies that $c^d = \pm 1$. This forces $a_d = \pm 1$ and $c = \pm 1$.
23: Let $b = -r$. Then $P(x) = a_d(x+b)^d$ where $a_d \in \{1, -1\}$ and $b \in \mathbb{Z}$.
24: 
25: 3. **Detailed Form Verification:**
26: We test the form $P(x) = a(x+b)^d$ where $d|k$ and $a \in \{1, -1\}, b \in \mathbb{Z}$.
27: - If $a=1$, $P(x) = (x+b)^d$. We need $(x+b)^d = n^k$ to have a solution $x \in \mathbb{Z}$ for all $n \in \mathbb{Z}_{\ge 0}$.
28:     - If $d$ is even, $x+b = \pm n^{k/d}$. Since $d|k$, $x = \pm n^{k/d} - b$ is always an integer.
29:     - If $d$ is odd, $x+b = n^{k/d}$. Since $d|k$, $x = n^{k/d} - b$ is always an integer.
30:     Thus, $P(x) = (x+b)^d$ works for any $d|k, b \in \mathbb{Z}$.
31: - If $a=-1$, $P(x) = -(x+b)^d$. We need $-(x+b)^d = n^k$, or $(x+b)^d = -n^k$.
32:     - If $d$ is even, $(x+b)^d \ge 0$, but $-n^k \le 0$. For $n \ge 1$, there is no solution.
33:     - If $d$ is odd, $x+b = (-n^k)^{1/d} = -n^{k/d}$. Since $d|k$, $x = -n^{k/d} - b$ is always an integer.
34:     Thus, $P(x) = -(x+b)^d$ works for any odd $d|k, b \in \mathbb{Z}$.
35: 
36: The polynomials are $P(x) = (x+b)^d$ for $d|2024, b \in \mathbb{Z}$ and $P(x) = -(x+b)^d$ for odd $d|2024, b \in \mathbb{Z}$.
