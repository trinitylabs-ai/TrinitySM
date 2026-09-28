# Problem

Let $a,b,c$ be positive reals such that $a+b+c = 1$, prove that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$.

# Proof A

1: To prove the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a, b, c$ such that $a+b+c=1$, we define the function
2: \[ f(a,b,c) = \sqrt{a} + \sqrt{b} + \sqrt{c} - 3\sqrt{3}(ab+bc+ca) \]
3: and seek to show that $f(a,b,c) \geq 0$ subject to the constraint $a+b+c=1$.
4: 
5: **1. Analysis of Critical Points**
6: We use the method of Lagrange Multipliers. Let $g(a,b,c) = a+b+c-1 = 0$. At any local extremum in the interior of the domain, we must have $\nabla f = \lambda \nabla g$. This yields the system:
7: \[ \frac{1}{2\sqrt{a}} - 3\sqrt{3}(b+c) = \lambda, \quad \frac{1}{2\sqrt{b}} - 3\sqrt{3}(a+c) = \lambda, \quad \frac{1}{2\sqrt{c}} - 3\sqrt{3}(a+b) = \lambda \]
8: Using the constraint $a+b+c=1$, we can rewrite these as:
9: \[ \frac{1}{2\sqrt{a}} - 3\sqrt{3}(1-a) = \lambda, \quad \frac{1}{2\sqrt{b}} - 3\sqrt{3}(1-b) = \lambda, \quad \frac{1}{2\sqrt{c}} - 3\sqrt{3}(1-c) = \lambda \]
10: Let $h(x) = \frac{1}{2\sqrt{x}} + 3\sqrt{3}x - 3\sqrt{3}$. The condition for a critical point is $h(a) = h(b) = h(c) = \lambda$. The derivative $h'(x) = -\frac{1}{4x^{3/2}} + 3\sqrt{3}$ vanishes only at $x = (12\sqrt{3})^{-2/3}$. Since $h'(x) < 0$ for $x < (12\sqrt{3})^{-2/3}$ and $h'(x) > 0$ for $x > (12\sqrt{3})^{-2/3}$, the function $h(x)$ is strictly decreasing then strictly increasing. Thus, for any constant $\lambda$, the equation $h(x) = \lambda$ has at most two distinct solutions. This implies that at any critical point, at least two of the variables $a, b, c$ must be equal.
11: 
12: **2. Reduction to a Single Variable**
13: Due to the symmetry of $f$, we may assume $a=b$. Then $c = 1-2a$ for $a \in (0, 1/2)$. We define the function $k(a)$ as:
14: \[ k(a) = f(a,a,1-2a) = 2\sqrt{a} + \sqrt{1-2a} - 3\sqrt{3}(a^2 + 2a(1-2a)) = 2\sqrt{a} + \sqrt{1-2a} - 3\sqrt{3}(2a - 3a^2) \]
15: To find the minimum of $k(a)$, we compute the derivative:
16: \[ k'(a) = \frac{1}{\sqrt{a}} - \frac{1}{\sqrt{1-2a}} - 6\sqrt{3}(1-3a) \]
17: Note that $k'(1/3) = \sqrt{3} - \sqrt{3} - 6\sqrt{3}(0) = 0$. The second derivative is:
18: \[ k''(a) = -\frac{1}{2a^{3/2}} - \frac{1}{(1-2a)^{3/2}} + 18\sqrt{3} \]
19: At $a=1/3$, $k''(1/3) = -\frac{3\sqrt{3}}{2} - 3\sqrt{3} + 18\sqrt{3} = 13.5\sqrt{3} > 0$. Thus, $a=1/3$ is a local minimum, and $k(1/3) = 2/\sqrt{3} + 1/\sqrt{3} - 3\sqrt{3}(2/3 - 1/3) = \sqrt{3} - \sqrt{3} = 0$.
20: 
21: To check for other roots of $k'(a)$, let $g(a) = \frac{1}{\sqrt{a}} - \frac{1}{\sqrt{1-2a}}$ and $h(a) = 6\sqrt{3}(1-3a)$. The second derivative $g''(a) = \frac{3}{4a^{5/2}} - \frac{3}{(1-2a)^{5/2}}$ changes sign exactly once on $(0, 1/2)$. Thus $g(a)$ is convex then concave. A linear function $h(a)$ can intersect such a curve at most three times. Since $k'(0^+) = \infty$, $k'(1/3) = 0$, and $k'(1/2^-) = -\infty$, and since $k''(1/3) > 0$, $k'(a)$ must have exactly three roots: $a_1 < 1/3 < a_2$. This implies the absolute minimum of $k(a)$ on $[0, 1/2]$ is $\min(k(0), k(1/3), k(1/2))$.
22: - $k(0) = 1$
23: - $k(1/3) = 0$
24: - $k(1/2) = \sqrt{2} - \frac{3\sqrt{3}}{4} \approx 0.115 > 0$
25: Thus, $k(a) \geq 0$ for all $a \in [0, 1/2]$.
26: 
27: **3. Boundary Analysis**
28: The domain is the simplex $a+b+c=1, a,b,c \geq 0$. We have analyzed the interior critical points and the symmetric cases. We must now check the boundary edges where one variable is zero. Let $c=0$, then $a+b=1$. The function becomes:
29: \[ p(a) = \sqrt{a} + \sqrt{1-a} - 3\sqrt{3}a(1-a) \quad \text{for } a \in [0, 1] \]
30: Let $x = \sqrt{a} + \sqrt{1-a}$. Then $x^2 = 1 + 2\sqrt{a(1-a)}$, so $a(1-a) = \left(\frac{x^2-1}{2}\right)^2$. For $a \in [0, 1]$, $x$ ranges from $1$ (at $a=0, 1$) to $\sqrt{2}$ (at $a=1/2$). We define:
31: \[ q(x) = x - 3\sqrt{3}\left(\frac{x^2-1}{2}\right)^2 = x - \frac{3\sqrt{3}}{4}(x^2-1)^2 \]
32: The derivative is $q'(x) = 1 - 3\sqrt{3}x(x^2-1)$. Since $x(x^2-1)$ is strictly increasing on $[1, \sqrt{2}]$, $q'(x)$ is strictly decreasing. Thus $q(x)$ is concave on $[1, \sqrt{2}]$. The minimum of a concave function occurs at the endpoints:
33: - $q(1) = 1 - 0 = 1$
34: - $q(\sqrt{2}) = \sqrt{2} - \frac{3\sqrt{3}}{4} \approx 0.115 > 0$
35: Thus $p(a) > 0$ for all $a \in [0, 1]$.
36: 
37: Combining the interior analysis and the boundary analysis, we conclude that $f(a,b,c) \geq 0$ for all $a,b,c > 0$ with $a+b+c=1$. Equality holds if and only if $a=b=c=1/3$.

# Proof B

1: To prove that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a,b,c$ such that $a+b+c=1$, we proceed as follows:
2: 
3: First, we express the term $ab+bc+ca$ in terms of the given constraint $a+b+c=1$. We know that:
4: \[(a+b+c)^2 = a^2+b^2+c^2 + 2(ab+bc+ca) = 1\]
5: Thus, we have $ab+bc+ca = \frac{1 - (a^2+b^2+c^2)}{2}$. Substituting this into the target inequality, we seek to prove:
6: \[\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3} \left( \frac{1 - (a^2+b^2+c^2)}{2} \right)\]
7: Rearranging the terms to group variables, this is equivalent to:
8: \[\sqrt{a}+\sqrt{b}+\sqrt{c} + \frac{3\sqrt{3}}{2}(a^2+b^2+c^2) \geq \frac{3\sqrt{3}}{2}\]
9: Since $a+b+c=1$, we can write the constant on the right side as $\frac{3\sqrt{3}}{2}(a+b+c)$. The inequality then becomes:
10: \[\sum_{cyc} \left( \sqrt{a} + \frac{3\sqrt{3}}{2} a^2 \right) \geq \sum_{cyc} \frac{3\sqrt{3}}{2} a\]
11: This is equivalent to showing that:
12: \[\sum_{cyc} \left( \sqrt{a} + \frac{3\sqrt{3}}{2} a^2 - \frac{3\sqrt{3}}{2} a \right) \geq 0\]
13: Let $h(x) = \sqrt{x} + \frac{3\sqrt{3}}{2}(x^2 - x)$ for $x \in (0, 1)$. We aim to show that $h(x) \geq 0$ for all $x \in (0, 1)$.
14: The derivative of $h(x)$ is:
15: \[h'(x) = \frac{1}{2\sqrt{x}} + 3\sqrt{3}x - \frac{3\sqrt{3}}{2} = \frac{1 + 6\sqrt{3}x\sqrt{x} - 3\sqrt{3}\sqrt{x}}{2\sqrt{x}}\]
16: To find the critical points, we set the numerator to zero. Let $u = \sqrt{x}$, where $u \in (0, 1)$. We solve:
17: \[N(u) = 6\sqrt{3}u^3 - 3\sqrt{3}u + 1 = 0\]
18: Testing $u = \frac{1}{\sqrt{3}}$, we find $N\left(\frac{1}{\sqrt{3}}\right) = 6\sqrt{3}\left(\frac{1}{3\sqrt{3}}\right) - 3\sqrt{3}\left(\frac{1}{\sqrt{3}}\right) + 1 = 2 - 3 + 1 = 0$.
19: Since $u = \frac{1}{\sqrt{3}}$ is a root, we factor $N(u)$ as:
20: \[N(u) = \left(u - \frac{1}{\sqrt{3}}\right)(6\sqrt{3}u^2 + 6u - \sqrt{3})\]
21: The roots of the quadratic factor $6\sqrt{3}u^2 + 6u - \sqrt{3} = 0$ are:
22: \[u = \frac{-6 \pm \sqrt{36 - 4(6\sqrt{3})(-\sqrt{3})}}{12\sqrt{3}} = \frac{-6 \pm \sqrt{36 + 72}}{12\sqrt{3}} = \frac{-6 \pm \sqrt{108}}{12\sqrt{3}} = \frac{-6 \pm 6\sqrt{3}}{12\sqrt{3}} = \frac{-1 \pm \sqrt{3}}{2\sqrt{3}}\]
23: The only positive root is $u_0 = \frac{\sqrt{3}-1}{2\sqrt{3}}$.
24: Analyzing the sign of $N(u)$ for $u \in (0, 1)$:
25: - For $u \in (0, u_0)$, $N(u) > 0$ (since $N(0) = 1$), so $h(x)$ is increasing.
26: - For $u \in (u_0, 1/\sqrt{3})$, $N(u) < 0$, so $h(x)$ is decreasing.
27: - For $u \in (1/\sqrt{3}, 1)$, $N(u) > 0$, so $h(x)$ is increasing.
28: 
29: We evaluate $h(x)$ at the boundaries and the local minimum:
30: $h(0) = 0$ and $h(1/3) = \sqrt{1/3} + \frac{3\sqrt{3}}{2}(\frac{1}{9} - \frac{1}{3}) = \frac{1}{\sqrt{3}} + \frac{3\sqrt{3}}{2}(-\frac{2}{9}) = \frac{1}{\sqrt{3}} - \frac{\sqrt{3}}{3} = 0$.
31: Since $h(x)$ increases from $0$ to $h(u_0^2)$, then decreases to $h(1/3) = 0$, and then increases again, we conclude that $h(x) \geq 0$ for all $x \in (0, 1)$.
32: 
33: Summing the inequalities $h(a) \geq 0, h(b) \geq 0, h(c) \geq 0$, we obtain:
34: \[\sum \sqrt{a} + \frac{3\sqrt{3}}{2} \sum a^2 - \frac{3\sqrt{3}}{2} \sum a \geq 0\]
35: Substituting $\sum a = 1$ and $\sum a^2 = 1 - 2(ab+bc+ca)$:
36: \[\sum \sqrt{a} + \frac{3\sqrt{3}}{2}(1 - 2(ab+bc+ca)) - \frac{3\sqrt{3}}{2} \geq 0\]
37: \[\sum \sqrt{a} + \frac{3\sqrt{3}}{2} - 3\sqrt{3}(ab+bc+ca) - \frac{3\sqrt{3}}{2} \geq 0\]
38: \[\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)\]
39: Equality holds if and only if $a=b=c=1/3$.
