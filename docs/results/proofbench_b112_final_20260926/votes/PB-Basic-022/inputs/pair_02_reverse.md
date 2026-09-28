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
