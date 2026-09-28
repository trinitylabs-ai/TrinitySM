# Problem

Let $a,b,c$ be positive reals such that $a+b+c = 1$, prove that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$.

# Proof A

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

# Proof B

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
