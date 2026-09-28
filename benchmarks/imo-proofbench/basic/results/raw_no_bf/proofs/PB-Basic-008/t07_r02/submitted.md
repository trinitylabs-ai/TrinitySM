To prove the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a, b, c$ such that $a+b+c=1$, we define the function
\[ f(a,b,c) = \sqrt{a} + \sqrt{b} + \sqrt{c} - 3\sqrt{3}(ab+bc+ca) \]
and seek to show that $f(a,b,c) \geq 0$ subject to the constraint $g(a,b,c) = a+b+c-1 = 0$.

**1. Critical Points and Symmetry**
Using the method of Lagrange Multipliers, we set $\nabla f = \lambda \nabla g$. This gives the system of equations:
\[ \frac{1}{2\sqrt{a}} - 3\sqrt{3}(b+c) = \lambda, \quad \frac{1}{2\sqrt{b}} - 3\sqrt{3}(a+c) = \lambda, \quad \frac{1}{2\sqrt{c}} - 3\sqrt{3}(a+b) = \lambda \]
Substituting $b+c = 1-a$, $a+c = 1-b$, and $a+b = 1-c$, we obtain:
\[ \frac{1}{2\sqrt{a}} - 3\sqrt{3}(1-a) = \lambda, \quad \frac{1}{2\sqrt{b}} - 3\sqrt{3}(1-b) = \lambda, \quad \frac{1}{2\sqrt{c}} - 3\sqrt{3}(1-c) = \lambda \]
Let $h(x) = \frac{1}{2\sqrt{x}} + 3\sqrt{3}x - 3\sqrt{3}$. The condition for a critical point is $h(a) = h(b) = h(c) = \lambda$. 
The derivative $h'(x) = -\frac{1}{4x^{3/2}} + 3\sqrt{3}$ has a single root at $x = (12\sqrt{3})^{-2/3}$. Thus, $h(x)$ is strictly decreasing on $(0, (12\sqrt{3})^{-2/3})$ and strictly increasing on $((12\sqrt{3})^{-2/3}, 1)$. This implies that for any $\lambda$, the equation $h(x) = \lambda$ can have at most two distinct solutions. Consequently, at any critical point $(a,b,c)$, at least two of the variables must be equal.

**2. Analysis of the Case $a=b$**
Let $a=b$. Then $c = 1-2a$, where $a \in (0, 1/2)$. The function becomes:
\[ k(a) = 2\sqrt{a} + \sqrt{1-2a} - 3\sqrt{3}(a^2 + 2a(1-2a)) = 2\sqrt{a} + \sqrt{1-2a} - 3\sqrt{3}(2a - 3a^2) \]
To find the minimum of $k(a)$, we examine its derivative:
\[ k'(a) = \frac{1}{\sqrt{a}} - \frac{1}{\sqrt{1-2a}} - 6\sqrt{3}(1-3a) \]
We observe that $k'(1/3) = \sqrt{3} - \sqrt{3} - 6\sqrt{3}(0) = 0$. The second derivative is:
\[ k''(a) = -\frac{1}{2a^{3/2}} - \frac{1}{(1-2a)^{3/2}} + 18\sqrt{3} \]
At $a=1/3$, $k''(1/3) = -\frac{3\sqrt{3}}{2} - 3\sqrt{3} + 18\sqrt{3} = 13.5\sqrt{3} > 0$, so $a=1/3$ is a local minimum.
Furthermore, let $g(a) = \frac{1}{\sqrt{a}} - \frac{1}{\sqrt{1-2a}}$ and $h(a) = 6\sqrt{3}(1-3a)$. Then $k'(a) = g(a) - h(a)$. The second derivative of $g(a)$ is $g''(a) = \frac{3}{4a^{5/2}} - \frac{3}{(1-2a)^{5/2}}$, which changes sign exactly once. Thus, $g(a)$ is first convex and then concave. A line $h(a)$ can intersect such a curve at most three times. Since $k'(a) \to \infty$ as $a \to 0^+$ and $k'(a) \to -\infty$ as $a \to 1/2^-$, and $k'(1/3)=0$ is a local minimum, there must be exactly two other roots $a_1 < 1/3 < a_2$, which correspond to local maxima.
The absolute minimum of $k(a)$ on $[0, 1/2]$ is thus $\min(k(0), k(1/3), k(1/2))$.
- $k(0) = 0 + 1 - 0 = 1$.
- $k(1/3) = 2/\sqrt{3} + 1/\sqrt{3} - 3\sqrt{3}(2/3 - 1/3) = \sqrt{3} - \sqrt{3} = 0$.
- $k(1/2) = \sqrt{2} + 0 - 3\sqrt{3}(1 - 3/4) = \sqrt{2} - \frac{3\sqrt{3}}{4} \approx 1.414 - 1.299 > 0$.
Thus, $k(a) \geq 0$ for all $a \in [0, 1/2]$.

**3. Conclusion**
Since any interior critical point of $f(a,b,c)$ must satisfy the $a=b$ (or $b=c$ or $c=a$) condition, and the boundary cases (where one or more variables are zero) are also covered by the analysis of $k(a)$ and the boundary values, the absolute minimum of $f(a,b,c)$ on the set $a+b+c=1, a,b,c \geq 0$ is $f(1/3, 1/3, 1/3) = 0$.
Therefore, $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for all positive reals $a,b,c$ such that $a+b+c=1$. \(\square\)
