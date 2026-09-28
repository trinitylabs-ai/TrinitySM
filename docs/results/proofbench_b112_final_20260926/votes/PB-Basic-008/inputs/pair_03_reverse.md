# Problem

Let $a,b,c$ be positive reals such that $a+b+c = 1$, prove that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$.

# Proof A

1: To prove that for positive reals $a, b, c$ such that $a+b+c=1$, the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ holds, we proceed as follows:
2: 
3: First, we use the algebraic identity for the sum of pairwise products:
4: \[ (a+b+c)^2 = a^2+b^2+c^2 + 2(ab+bc+ca). \]
5: Given that $a+b+c=1$, we can express the sum of pairwise products as:
6: \[ ab+bc+ca = \frac{1 - (a^2+b^2+c^2)}{2}. \]
7: Substituting this expression into the right-hand side of the inequality we wish to prove, we have:
8: \[ 3\sqrt{3}(ab+bc+ca) = 3\sqrt{3} \left( \frac{1 - (a^2+b^2+c^2)}{2} \right) = \frac{3\sqrt{3}}{2}(1 - \sum a^2). \]
9: The original inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ is therefore equivalent to:
10: \[ \sum \sqrt{a} \geq \frac{3\sqrt{3}}{2}(1 - \sum a^2). \]
11: Since $a+b+c=1$, we can write $1$ as $\sum a$. The inequality becomes:
12: \[ \sum \sqrt{a} \geq \frac{3\sqrt{3}}{2} \sum a - \frac{3\sqrt{3}}{2} \sum a^2, \]
13: which can be rearranged as:
14: \[ \sum \left( \sqrt{a} - \frac{3\sqrt{3}}{2} a + \frac{3\sqrt{3}}{2} a^2 \right) \geq 0. \]
15: Let $g(x) = \sqrt{x} - \frac{3\sqrt{3}}{2} x + \frac{3\sqrt{3}}{2} x^2$ for $x \in (0, 1)$. To prove the inequality, it suffices to show that $g(x) \geq 0$ for all $x \in (0, 1)$. We factor out $\sqrt{x}$ from the expression:
16: \[ g(x) = \sqrt{x} \left( 1 - \frac{3\sqrt{3}}{2} \sqrt{x} + \frac{3\sqrt{3}}{2} x^{3/2} \right). \]
17: Let $t = \sqrt{x}$. Since $x \in (0, 1)$, we have $t \in (0, 1)$. The term in the parentheses is:
18: \[ f(t) = 1 - \frac{3\sqrt{3}}{2} (t - t^3). \]
19: To find the maximum value of the function $h(t) = t - t^3$ on the interval $(0, 1)$, we compute its derivative:
20: \[ h'(t) = 1 - 3t^2. \]
21: Setting $h'(t) = 0$ yields $t = \frac{1}{\sqrt{3}}$. The maximum value of $h(t)$ on this interval is:
22: \[ h\left(\frac{1}{\sqrt{3}}\right) = \frac{1}{\sqrt{3}} - \left(\frac{1}{\sqrt{3}}\right)^3 = \frac{1}{\sqrt{3}} - \frac{1}{3\sqrt{3}} = \frac{2}{3\sqrt{3}}. \]
23: Using this maximum value, we find the minimum value of $f(t)$:
24: \[ f(t) = 1 - \frac{3\sqrt{3}}{2} h(t) \geq 1 - \frac{3\sqrt{3}}{2} \left( \frac{2}{3\sqrt{3}} \right) = 1 - 1 = 0. \]
25: Since $t = \sqrt{x} > 0$ and $f(\sqrt{x}) \geq 0$, it follows that $g(x) = \sqrt{x} f(\sqrt{x}) \geq 0$ for all $x \in (0, 1)$. Summing these values for $a, b, c$, we obtain:
26: \[ \sum g(a) = \sum \sqrt{a} - \frac{3\sqrt{3}}{2} \sum a + \frac{3\sqrt{3}}{2} \sum a^2 = \sum \sqrt{a} - \frac{3\sqrt{3}}{2}(1 - \sum a^2) \geq 0. \]
27: Thus, $\sum \sqrt{a} \geq 3\sqrt{3} \sum ab$. Equality holds if and only if $f(\sqrt{a}) = f(\sqrt{b}) = f(\sqrt{c}) = 0$, which implies $\sqrt{a} = \sqrt{b} = \sqrt{c} = \frac{1}{\sqrt{3}}$, or $a=b=c=1/3$.
28: 
29: \(\square\)

# Proof B

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
