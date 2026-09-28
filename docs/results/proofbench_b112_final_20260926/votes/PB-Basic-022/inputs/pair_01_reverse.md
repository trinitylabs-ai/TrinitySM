# Problem

Let $S=\{0,1,2^{2024},3^{2024},\ldots\}$ be the set of all perfect
 2024-th powers. Find all polynomials $P$ with integer coefficients
 such that $P(x)=s$ has an integer solution $x$ for every $s\in S$.

# Proof A

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

# Proof B

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
