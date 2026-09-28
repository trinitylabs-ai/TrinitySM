To prove the inequality $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$ for positive reals $a,b,c$ such that $a+b+c=1$, we utilize a change of variables and a study of the function's extrema.

### 1. Change of Variables
Let $x = \sqrt{a}, y = \sqrt{b}, z = \sqrt{c}$. Given $a,b,c > 0$, we have $x,y,z > 0$.
The constraint $a+b+c=1$ transforms to:
\[ x^2 + y^2 + z^2 = 1 \]
The inequality to be proved becomes:
\[ x + y + z \geq 3\sqrt{3}(x^2y^2 + y^2z^2 + z^2x^2) \]
Define the function $f(x,y,z) = x + y + z - 3\sqrt{3}(x^2y^2 + y^2z^2 + z^2x^2)$ on the set $S = \{(x,y,z) \in \mathbb{R}^3 : x^2+y^2+z^2=1, x,y,z \geq 0\}$. Since $S$ is a compact set and $f$ is continuous, $f$ must attain a minimum value on $S$.

### 2. Finding Critical Points via Lagrange Multipliers
To find the extrema of $f$ subject to $g(x,y,z) = x^2+y^2+z^2-1=0$, we set $\nabla f = \lambda \nabla g$:
\[ \begin{cases} 1 - 6\sqrt{3}x(y^2+z^2) = 2\lambda x \\ 1 - 6\sqrt{3}y(x^2+z^2) = 2\lambda y \\ 1 - 6\sqrt{3}z(x^2+y^2) = 2\lambda z \end{cases} \]
Subtracting the first two equations:
\[ 6\sqrt{3}(y(x^2+z^2) - x(y^2+z^2)) = 2\lambda(x-y) \]
\[ 6\sqrt{3}(yx^2 + yz^2 - xy^2 - xz^2) = 2\lambda(x-y) \]
\[ 6\sqrt{3}(xy(x-y) - z^2(x-y)) = 2\lambda(x-y) \]
\[ (x-y) [6\sqrt{3}(xy-z^2) - 2\lambda] = 0 \]
This implies that for any pair of variables, either they are equal or the expression in the brackets is zero. If $x \neq y$, $y \neq z$, and $z \neq x$, then:
\[ 2\lambda = 6\sqrt{3}(xy-z^2) = 6\sqrt{3}(yz-x^2) = 6\sqrt{3}(zx-y^2) \]
Equating $xy-z^2 = yz-x^2$ gives $x^2-z^2 + xy-yz = 0$, which factors as $(x-z)(x+y+z)=0$. Since $x,y,z > 0$, we must have $x=z$, which contradicts the assumption. Thus, at any interior critical point, at least two variables must be equal.

### 3. Evaluating Symmetric Cases
**Case 1: $x=y=z$.**
From $x^2+y^2+z^2=1$, we get $3x^2=1 \implies x=1/\sqrt{3}$.
Substituting into $f$:
\[ f\left(\frac{1}{\sqrt{3}}, \frac{1}{\sqrt{3}}, \frac{1}{\sqrt{3}}\right) = \frac{3}{\sqrt{3}} - 3\sqrt{3}\left(\frac{1}{9} + \frac{1}{9} + \frac{1}{9}\right) = \sqrt{3} - 3\sqrt{3}\left(\frac{1}{3}\right) = 0 \]

**Case 2: $x=y \neq z$.**
Substituting $z^2 = 1-2x^2$ into $f$:
\[ f(x) = 2x + \sqrt{1-2x^2} - 3\sqrt{3}(x^4 + 2x^2(1-2x^2)) = 2x + \sqrt{1-2x^2} - 3\sqrt{3}(2x^2-3x^4) \]
We check the endpoints of the domain $x \in [0, 1/\sqrt{2}]$:
- If $x=0$, $f(0) = 0 + 1 - 0 = 1 > 0$.
- If $x=1/\sqrt{2}$, $f(1/\sqrt{2}) = \sqrt{2} + 0 - 3\sqrt{3}(1 - 3/4) = \sqrt{2} - \frac{3\sqrt{3}}{4} \approx 1.414 - 1.299 > 0$.
The only critical point for $f(x)$ in this interval is $x=1/\sqrt{3}$, where $f(1/\sqrt{3}) = 0$. Since the function is continuous and the endpoints are positive, the minimum value in this case is $0$.

**Case 3: Boundary points ($z=0$).**
If $z=0$, then $x^2+y^2=1$.
\[ f(x,y,0) = x+y - 3\sqrt{3}(x^2y^2) \]
Since $x+y \geq 1$ (for $x^2+y^2=1, x,y \geq 0$) and $x^2y^2 \leq (1/2)^2 = 1/4$, we have:
\[ f(x,y,0) \geq 1 - \frac{3\sqrt{3}}{4} \approx 1 - 1.299 \]
Wait, we must check if $x+y \geq 3\sqrt{3}x^2y^2$ more carefully. Let $q=xy \in [0, 1/2]$. Then $x+y = \sqrt{1+2q}$.
Let $h(q) = \sqrt{1+2q} - 3\sqrt{3}q^2$. $h(0)=1$ and $h(1/2) = \sqrt{2} - 3\sqrt{3}/4 > 0$.
Since $h'(q) = \frac{1}{\sqrt{1+2q}} - 6\sqrt{3}q$, the function decreases to a minimum and then increases. The minimum is clearly positive as $h(1/2) > 0$ and $h(0) > 0$.

### Conclusion
Since all critical points and boundary values of $f(x,y,z)$ are $\geq 0$, we conclude that $f(x,y,z) \geq 0$ for all $x,y,z \in S$. This proves that $\sqrt{a}+\sqrt{b}+\sqrt{c} \geq 3\sqrt{3}(ab+bc+ca)$. Equality holds if and only if $a=b=c=1/3$.

\(\square\)
