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
