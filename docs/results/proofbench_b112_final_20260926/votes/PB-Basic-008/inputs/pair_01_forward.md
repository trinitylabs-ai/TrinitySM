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

1: To prove the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a,b,c$ such that $a+b+c=1$, we perform a change of variables.
2: 
3: ### 1. Change of Variables
4: Let $x = \sqrt{a}$, $y = \sqrt{b}$, and $z = \sqrt{c}$. Since $a,b,c > 0$, we have $x,y,z > 0$. The constraint $a+b+c=1$ becomes $x^2 + y^2 + z^2 = 1$. The inequality to be proved is:
5: \[ x + y + z \geq 3\sqrt{3}(x^2y^2 + y^2z^2 + z^2x^2) \]
6: 
7: ### 2. Optimization via Lagrange Multipliers
8: Define the function $f(x,y,z) = x + y + z - 3\sqrt{3}(x^2y^2 + y^2z^2 + z^2x^2)$ on the set $S = \{(x,y,z) \in \mathbb{R}^3 : x^2+y^2+z^2=1, x,y,z \geq 0\}$. To find the minimum of $f$, we use the method of Lagrange multipliers. Let $g(x,y,z) = x^2+y^2+z^2-1 = 0$. The critical points in the interior of $S$ satisfy $\nabla f = \lambda \nabla g$:
9: \[ \begin{cases} 1 - 6\sqrt{3}x(y^2+z^2) = 2\lambda x \\ 1 - 6\sqrt{3}y(x^2+z^2) = 2\lambda y \\ 1 - 6\sqrt{3}z(x^2+y^2) = 2\lambda z \end{cases} \]
10: Subtracting the first two equations:
11: \[ 6\sqrt{3}[y(x^2+z^2) - x(y^2+z^2)] = 2\lambda(x-y) \]
12: \[ 6\sqrt{3}[(x-y)(xy-z^2)] = 2\lambda(x-y) \]
13: \[ (x-y)[6\sqrt{3}(xy-z^2) - 2\lambda] = 0 \]
14: This implies that for any critical point, either $x=y$ or $2\lambda = 6\sqrt{3}(xy-z^2)$. If $x,y,z$ are all distinct, then $xy-z^2 = yz-x^2 = zx-y^2$. However, $xy-z^2 = yz-x^2$ implies $x^2-z^2 + y(x-z) = 0$, which factorizes as $(x-z)(x+y+z) = 0$. Since $x,y,z > 0$, we must have $x=z$, contradicting the assumption that they are distinct. Thus, at any interior critical point, at least two variables must be equal.
15: 
16: ### 3. Analysis of Cases
17: **Case 1: $x=y=z$.**
18: Substituting into $x^2+y^2+z^2=1$, we get $3x^2=1 \implies x=y=z=1/\sqrt{3}$.
19: \[ f\left(\frac{1}{\sqrt{3}}, \frac{1}{\sqrt{3}}, \frac{1}{\sqrt{3}}\right) = \frac{3}{\sqrt{3}} - 3\sqrt{3}\left(\frac{1}{9} + \frac{1}{9} + \frac{1}{9}\right) = \sqrt{3} - \sqrt{3} = 0 \]
20: 
21: **Case 2: $x=y$ and $z = \sqrt{1-2x^2}$.**
22: The function becomes $f(x) = 2x + \sqrt{1-2x^2} - 3\sqrt{3}(x^4 + 2x^2(1-2x^2)) = 2x + \sqrt{1-2x^2} - 3\sqrt{3}(2x^2-3x^4)$ for $x \in [0, 1/\sqrt{2}]$.
23: The derivative is $f'(x) = 2 - \frac{2x}{\sqrt{1-2x^2}} - 12\sqrt{3}x(1-3x^2)$.
24: The second derivative is $f''(x) = \frac{-2}{(1-2x^2)^{3/2}} - 12\sqrt{3}(1-9x^2)$.
25: Let $u = x^2 \in [0, 1/2]$. Then $f''(x) = 2[6\sqrt{3}(9u-1) - (1-2u)^{-3/2}]$.
26: Let $\psi(u) = 6\sqrt{3}(9u-1)$ and $\phi(u) = (1-2u)^{-3/2}$. Both are strictly increasing on $[0, 1/2)$.
27: $\psi(0)-\phi(0) = -6\sqrt{3}-1 < 0$, $\psi(1/3)-\phi(1/3) = 12\sqrt{3}-3\sqrt{3} = 9\sqrt{3} > 0$, and $\psi(1/2)-\phi(1/2) = 21\sqrt{3} - \infty = -\infty$.
28: Thus, $f''(x)$ has exactly two roots $x_1 \in (0, 1/\sqrt{3})$ and $x_2 \in (1/\sqrt{3}, 1/\sqrt{2})$.
29: $f'(x)$ decreases on $(0, x_1)$, increases on $(x_1, x_2)$, and decreases on $(x_2, 1/\sqrt{2})$.
30: Since $f'(0)=2$, $f'(1/\sqrt{3})=0$, and $f'(1/\sqrt{2})=-\infty$, $f'(x)$ has exactly three roots: one in $(0, x_1)$, $x=1/\sqrt{3}$, and one in $(x_2, 1/\sqrt{2})$.
31: The only local minimum is $f(1/\sqrt{3})=0$. Since $f(0)=1 > 0$ and $f(1/\sqrt{2}) = \sqrt{2} - \frac{3\sqrt{3}}{4} \approx 0.115 > 0$, the global minimum on this interval is $f(1/\sqrt{3})=0$.
32: 
33: **Case 3: Boundary $z=0$.**
34: If $z=0$, then $x^2+y^2=1$. Let $s = x+y \in [1, \sqrt{2}]$. Then $xy = \frac{s^2-1}{2}$.
35: The function is $g(s) = s - 3\sqrt{3}(\frac{s^2-1}{2})^2 = s - \frac{3\sqrt{3}}{4}(s^2-1)^2$.
36: $g''(s) = -3\sqrt{3}(3s^2-1)$. Since $s \geq 1$, $g''(s) < 0$, so $g$ is concave.
37: The minimum occurs at the endpoints: $g(1) = 1 > 0$ and $g(\sqrt{2}) = \sqrt{2} - \frac{3\sqrt{3}}{4} > 0$.
38: Thus, $f(x,y,0) > 0$.
39: 
40: ### Conclusion
41: The minimum value of $f(x,y,z)$ on $S$ is $0$, achieved at $x=y=z=1/\sqrt{3}$. Thus, $x+y+z \geq 3\sqrt{3}(x^2y^2+y^2z^2+z^2x^2)$. Substituting back $x=\sqrt{a}, y=\sqrt{b}, z=\sqrt{c}$, we obtain:
42: \[ \sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca) \]
43: Equality holds if and only if $a=b=c=1/3$.
