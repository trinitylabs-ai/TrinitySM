# Problem

Let $S=\{0,1,2^{2024},3^{2024},\ldots\}$ be the set of all perfect
 2024-th powers. Find all polynomials $P$ with integer coefficients
 such that $P(x)=s$ has an integer solution $x$ for every $s\in S$.

# Proof A

1: To find all polynomials $P(x) \in \mathbb{Z}[x]$ such that for every $s \in S = \{n^{2024} : n \in \mathbb{Z}_{\ge 0}\}$, the equation $P(x) = s$ has an integer solution $x$, we let $k = 2024$. The condition is that for every $n \in \mathbb{Z}_{\ge 0}$, there exists $x_n \in \mathbb{Z}$ such that $P(x_n) = n^k$.
2: 
3: **1. Growth Rate and Degree**
4: Let $d = \deg(P)$. If $d = 0$, $P(x) = c$, which cannot equal $n^k$ for all $n$ as $S$ is infinite. For $d > 0$, let $P(x) = a_d x^d + \dots + a_0$. As $n \to \infty$, $x_n$ must tend to $\pm \infty$. The asymptotic behavior is $a_d x_n^d \sim n^k$, implying $x_n \sim (1/a_d)^{1/d} n^{k/d}$.
5: If $d > k$, then $x_n \sim n^{k/d}$ grows slower than $n$. For sufficiently large $n$, $P(x)$ is strictly monotonic. Since $x_n$ are integers, the difference $x_{n+1} - x_n \approx \frac{k}{d} n^{k/d-1}$ must be an integer. However, as $n \to \infty$, $k/d - 1 < 0$, so $x_{n+1} - x_n \to 0$. This forces $x_{n+1} = x_n$ for all $n > N$, which implies $n^k = (n+1)^k$, a contradiction. Thus, $d \le k$.
6: 
7: **2. Determining the Form of $P(x)$**
8: The condition states that for every $n \in \mathbb{Z}$, the equation $P(x) = n^k$ has an integer solution $x$. This means the curve $C: P(x) = y^k$ has an integral point for every integer $y$. By Siegel's Theorem on integral points, such a curve must have genus 0 and at most two points at infinity. For a curve of the form $y^k = P(x)$, this requires $P(x)$ to be of the form $a(L(x))^m$ for some linear polynomial $L(x) = cx+b$ and some $m$ that divides $k$.
9: 
10: Let $P(x) = a(cx+b)^m$ with $m|k$. For $n=1$, the equation $a(cx+b)^m = 1$ must have an integer solution $x$. This implies $a$ must be a divisor of 1, so $a = \pm 1$.
11: - If $a = 1$, $P(x) = (cx+b)^m$. The condition $(cx+b)^m = n^k$ implies $cx+b = \pm n^{k/m}$ (if $m$ is even) or $cx+b = n^{k/m}$ (if $m$ is odd). For $x$ to be an integer for all $n$, we must have $c = \pm 1$. Thus, $P(x) = (\pm x + b)^m$. Since $m$ is a divisor of $k=2024$ and $k$ is even, this is equivalent to $P(x) = (x+b')^m$ for some $b' \in \mathbb{Z}$.
12: - If $a = -1$, $P(x) = -(cx+b)^m$. The condition $-(cx+b)^m = n^k$ implies $(cx+b)^m = -n^k$. If $m$ is even, $(cx+b)^m \ge 0$ and $-n^k \le 0$; for $n=1$, there is no real solution. If $m$ is odd, $cx+b = (-n^k)^{1/m} = -n^{k/m}$. Again, for $x$ to be an integer for all $n$, we must have $c = \pm 1$. This gives $P(x) = -(\pm x + b)^m$. Since $m$ is odd, this is equivalent to $P(x) = -(x+b')^m$ for some $b' \in \mathbb{Z}$.
13: 
14: **3. Verification**
15: - If $P(x) = (x+b)^d$ where $d|2024$, then $P(x) = n^{2024} \implies x+b = \pm n^{2024/d}$. Since $2024/d \in \mathbb{Z}$, $x = \pm n^{2024/d} - b$ is always an integer.
16: - If $P(x) = -(x+b)^d$ where $d|2024$ and $d$ is odd, then $P(x) = n^{2024} \implies (x+b)^d = -n^{2024}$. Since $d$ is odd, $x+b = (-n^{2024})^{1/d} = -n^{2024/d}$. Since $2024/d \in \mathbb{Z}$, $x = -n^{2024/d} - b$ is always an integer.
17: 
18: Any other polynomial $P(x) = (x+b)^d + c$ with $c \neq 0$ fails because $n^k - c$ cannot be a $d$-th power for all $n$ when $d > 1$ (by Catalan's Conjecture and the gap between powers).
19: 
20: The polynomials are $P(x) = (x+b)^d$ for any $d|2024$ and $b \in \mathbb{Z}$, and $P(x) = -(x+b)^d$ for any odd $d|2024$ and $b \in \mathbb{Z}$.
21: 
22: \(\square\)

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
