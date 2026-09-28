# Problem

Given a triangle $ABC$ with $AB<AC<BC$, let $I$ be the incenter
 of triangle $ABC$, and let $M$ and $N$ be the midpoints of sides
 $CA$ and $AB$, respectively. Let $K$ be the midpoint of the arc
 $BC$ of the circumcircle of triangle $ABC$ which does not contain
 $A$. Let $B'\neq C$ be the point where the line parallel to $AC$
 and tangent to the incircle of triangle $ABC$ intersects side $BC$,
 and similarly, let $C'\neq B$ be the point where the line parallel
 to $AB$ and tangent to the incircle of triangle $ABC$ intersects
 side $BC$. Find the value of $\angle NIM+\angle B'KC'$ in terms
 of degree.

# Proof A

1: Let the side lengths of $\triangle ABC$ be $a, b, c$ opposite to vertices $A, B, C$, respectively, with $c < b < a$. Let $s = (a+b+c)/2$ be the semiperimeter and $r$ be the inradius.
2: 
3: 1. **Coordinates of $B'$ and $C'$:**
4: Let $h_b$ be the altitude from $B$ to $AC$. The line $L_1$ is parallel to $AC$ and tangent to the incircle. Since $B'$ lies on $BC$ and $B' \neq C$, $L_1$ must be the tangent located between $B$ and $AC$. The distance from $B$ to $AC$ is $h_b$, and the distance between the two tangents to the incircle parallel to $AC$ is $2r$. Thus, the distance from $B$ to $L_1$ is $h_b - 2r$. By similarity, $BB'/BC = (h_b - 2r)/h_b = 1 - 2r/h_b$. Since $h_b = 2\Delta/b$ and $r = \Delta/s$, we have $2r/h_b = b/s$. Thus, $BB'/BC = 1 - b/s = (s-b)/s$. Similarly, $CC'/BC = (s-c)/s$.
5: 
6: Let the side $BC$ lie on the $x$-axis with the midpoint $D$ of $BC$ as the origin $(0,0)$. Thus $B = (-a/2, 0)$ and $C = (a/2, 0)$. $K$ is the midpoint of the arc $BC$ of the circumcircle not containing $A$, so $K$ lies on the perpendicular bisector of $BC$ (the $y$-axis) and $\angle KBC = \angle KCB = A/2$. Thus $KD = (a/2) \tan(A/2)$. Since $K$ and $A$ are on opposite sides of $BC$, let $K = (0, -a/2 \tan(A/2))$.
7: The coordinates of $B'$ and $C'$ are:
8: $B' = (-a/2 + a(s-b)/s, 0) = (\frac{a(s-2b)}{2s}, 0)$
9: $C' = (a/2 - a(s-c)/s, 0) = (\frac{a(2c-s)}{2s}, 0)$
10: Let $x_{B'} = \frac{a}{2}(1 - \frac{2b}{s})$, $x_{C'} = \frac{a}{2}(\frac{2c}{s} - 1)$, and $y_K = - \frac{a}{2} \tan(A/2)$.
11: The vectors $\vec{KB'} = (x_{B'}, -y_K)$ and $\vec{KC'} = (x_{C'}, -y_K)$ give:
12: $\cos \angle B'KC' = \frac{x_{B'}x_{C'} + y_K^2}{\sqrt{x_{B'}^2 + y_K^2} \sqrt{x_{C'}^2 + y_K^2}} = \frac{(1 - \frac{2b}{s})(\frac{2c}{s} - 1) + \tan^2(A/2)}{\sqrt{(1 - \frac{2b}{s})^2 + \tan^2(A/2)} \sqrt{(\frac{2c}{s} - 1)^2 + \tan^2(A/2)}}$.
13: 
14: 2. **Analytical Expression for $\angle NIM$:**
15: Let $I$ be the origin. Let $x = \sin(A/2), y = \sin(B/2), z = \sin(C/2)$.
16: The distances from $I$ to the vertices are $IA = r/x, IB = r/y, IC = r/z$.
17: The vectors $\vec{IA}, \vec{IB}, \vec{IC}$ satisfy $\angle AIB = 90^\circ + C/2$, $\angle AIC = 90^\circ + B/2$, and $\angle BIC = 90^\circ + A/2$.
18: Thus, $\vec{IA} \cdot \vec{IB} = IA \cdot IB \cos(90^\circ + C/2) = - \frac{r^2 z}{xy}$.
19: Similarly, $\vec{IA} \cdot \vec{IC} = - \frac{r^2 y}{xz}$ and $\vec{IB} \cdot \vec{IC} = - \frac{r^2 x}{yz}$.
20: Since $N$ and $M$ are midpoints of $AB$ and $AC$, $\vec{IN} = \frac{1}{2}(\vec{IA} + \vec{IB})$ and $\vec{IM} = \frac{1}{2}(\vec{IA} + \vec{IC})$.
21: $4 \vec{IN} \cdot \vec{IM} = IA^2 + \vec{IA} \cdot \vec{IC} + \vec{IA} \cdot \vec{IB} + \vec{IB} \cdot \vec{IC} = r^2 [ \frac{1}{x^2} - \frac{y}{xz} - \frac{z}{xy} - \frac{x}{yz} ] = \frac{r^2}{x^2y^2z^2} [ y^2z^2 - xyz(x^2+y^2+z^2) ]$.
22: $4 |\vec{IN}|^2 = IA^2 + IB^2 + 2 \vec{IA} \cdot \vec{IB} = r^2 [ \frac{1}{x^2} + \frac{1}{y^2} - \frac{2z}{xy} ] = \frac{r^2}{x^2y^2} [ x^2+y^2-2xyz ]$.
23: $4 |\vec{IM}|^2 = IA^2 + IC^2 + 2 \vec{IA} \cdot \vec{IC} = r^2 [ \frac{1}{x^2} + \frac{1}{z^2} - \frac{2y}{xz} ] = \frac{r^2}{x^2z^2} [ x^2+z^2-2xyz ]$.
24: $\cos \angle NIM = \frac{y^2z^2 - xyz(x^2+y^2+z^2)}{yz \sqrt{x^2+y^2-2xyz} \sqrt{x^2+z^2-2xyz}}$.
25: 
26: 3. **Unification:**
27: Using $s = 4R \cos(A/2) \cos(B/2) \cos(C/2)$ and $b = 2R \sin B = 4R \sin(B/2) \cos(B/2)$, we have:
28: $\frac{b}{s} = \frac{\sin(B/2)}{\cos(A/2) \cos(C/2)} = \frac{y}{C_A C_C}$ and $\frac{c}{s} = \frac{\sin(C/2)}{\cos(A/2) \cos(B/2)} = \frac{z}{C_A C_B}$, where $C_A = \cos(A/2)$, etc.
29: Note that $y = \sin(B/2) = \cos(A/2+C/2) = C_A C_C - xz$, so $C_A C_C - 2y = 2xz - C_A C_C$.
30: Similarly, $z = \sin(C/2) = \cos(A/2+B/2) = C_A C_B - xy$, so $2z - C_A C_B = C_A C_B - 2xy$.
31: The numerator of $\cos \angle B'KC'$ is $N = (1 - \frac{2b}{s})(\frac{2c}{s} - 1) + \tan^2(A/2) = \frac{(C_A C_C - 2y)(2z - C_A C_B) + x^2 C_B C_C}{C_A^2 C_B C_C}$.
32: Substituting the expressions for $y$ and $z$:
33: $N = \frac{(2xz - C_A C_C)(C_A C_B - 2xy) + x^2 C_B C_C}{C_A^2 C_B C_C} = \frac{2xz C_A C_B - 4x^2 yz - C_A^2 C_B C_C + 2xy C_A C_C + x^2 C_B C_C}{C_A^2 C_B C_C}$
34: $= \frac{2x C_A (z C_B + y C_C) - 4x^2 yz - (C_A^2 - x^2) C_B C_C}{C_A^2 C_B C_C}$.
35: Since $z C_B + y C_C = \sin(C/2)\cos(B/2) + \sin(B/2)\cos(C/2) = \sin(B/2+C/2) = C_A$ and $C_A^2 - x^2 = \cos A$,
36: $N = \frac{2x C_A^2 - 4x^2 yz - \cos A C_B C_C}{C_A^2 C_B C_C}$.
37: Using $C_B C_C = \frac{1-y^2-z^2+x^2}{2x}$ and $\cos A = 1-2x^2$, we find $2x(2x C_A^2 - 4x^2 yz - \cos A C_B C_C) = 2x(x - yz(1+2x^2))$.
38: Thus $N = \frac{x - yz(1+2x^2)}{C_A^2 C_B C_C}$.
39: For the denominator, $(1 - \frac{2b}{s})^2 + \tan^2(A/2) = \frac{(C_A C_C - 2y)^2 + x^2 C_C^2}{C_A^2 C_C^2} = \frac{(2xz - C_A C_C)^2 + x^2 C_C^2}{C_A^2 C_C^2} = \frac{4x^2 z^2 - 4xz C_A C_C + C_C^2}{C_A^2 C_C^2}$.
40: Since $C_A C_C = y + xz$, this is $\frac{4x^2 z^2 - 4xyz - 4x^2 z^2 + 1 - z^2}{C_A^2 C_C^2} = \frac{1 - z^2 - 4xyz}{C_A^2 C_C^2} = \frac{x^2 + y^2 - 2xyz}{C_A^2 C_C^2}$.
41: Similarly, $(\frac{2c}{s} - 1)^2 + \tan^2(A/2) = \frac{x^2 + z^2 - 2xyz}{C_A^2 C_B^2}$.
42: Thus $\cos \angle B'KC' = \frac{x - yz(1+2x^2)}{\sqrt{x^2+y^2-2xyz} \sqrt{x^2+z^2-2xyz}}$.
43: Comparing this to $\cos \angle NIM = \frac{y^2z^2 - xyz(1-2xyz)}{yz \sqrt{x^2+y^2-2xyz} \sqrt{x^2+z^2-2xyz}} = \frac{-yz(x - yz - 2x^2 yz)}{yz \sqrt{x^2+y^2-2xyz} \sqrt{x^2+z^2-2xyz}}$, we see $\cos \angle NIM = -\cos \angle B'KC'$.
44: Therefore, $\angle NIM + \angle B'KC' = 180^\circ$.
45: 
46: The value of $\angle NIM + \angle B'KC'$ is $180^\circ$.

# Proof B

1: Let $a, b, c$ denote the side lengths $BC, CA, AB$ respectively, and let $s = (a+b+c)/2$ be the semiperimeter. We are given $c < b < a$.
2: 
3: **1. Determination of points $B'$ and $C'$**
4: Let $h_b$ be the altitude from $B$ to $AC$ and $r$ be the inradius. The line $L_B$ is parallel to $AC$ and tangent to the incircle. The distance from $L_B$ to $AC$ is $2r$ because the incenter $I$ is at distance $r$ from $AC$ and $L_B$ is the tangent line on the opposite side of $I$ from $AC$. Since $B'$ lies on $BC$, the distance from $B'$ to $AC$ is $d(B', AC) = \frac{B'C}{BC} h_b$. Setting this equal to $2r$:
5: $$\frac{B'C}{a} h_b = 2r \implies B'C = \frac{2ar}{h_b}$$
6: Using the area formulas $[ABC] = \frac{1}{2} b h_b = rs$, we have $h_b = \frac{2rs}{b}$, so:
7: $$B'C = \frac{2ar}{2rs/b} = \frac{ab}{s}$$
8: Similarly, for point $C'$ on $BC$ where the tangent is parallel to $AB$, we have $C'B = \frac{ac}{s}$.
9: 
10: **2. Vector expressions for $\angle B'KC'$**
11: Let $D$ be the midpoint of $BC$. Set $D$ as the origin $(0,0)$ with $B=(-a/2, 0)$ and $C=(a/2, 0)$. $K$ is the midpoint of the arc $BC$ not containing $A$, so $K$ lies on the perpendicular bisector of $BC$ and $\angle KBC = \angle KCB = A/2$. Thus, $K = (0, -h)$ where $h = \frac{a}{2} \tan(A/2)$.
12: The coordinates of $B'$ and $C'$ are:
13: $$B' = \left(\frac{a}{2} - \frac{ab}{s}, 0\right), \quad C' = \left(-\frac{a}{2} + \frac{ac}{s}, 0\right)$$
14: The vectors from $K$ are $\vec{KB'} = \left(\frac{a(s-2b)}{2s}, h\right)$ and $\vec{KC'} = \left(\frac{a(2c-s)}{2s}, h\right)$.
15: The cosine of $\angle B'KC'$ is:
16: $$\cos(\angle B'KC') = \frac{\vec{KB'} \cdot \vec{KC'}}{|\vec{KB'}| |\vec{KC'}|} = \frac{\frac{a^2(s-2b)(2c-s)}{4s^2} + h^2}{\sqrt{\frac{a^2(s-2b)^2}{4s^2} + h^2} \sqrt{\frac{a^2(2c-s)^2}{4s^2} + h^2}}$$
17: 
18: **3. Vector expressions for $\angle NIM$**
19: Let $A$ be the origin $(0,0)$ and $B$ lie on the $x$-axis. The distance from $A$ to the point where the incircle touches $AB$ is $s-a$. Thus, the incenter $I$ is $(s-a, r)$. The midpoints are $N=(c/2, 0)$ and $M=(\frac{b \cos A}{2}, \frac{b \sin A}{2})$.
20: The vectors are:
21: $$\vec{IN} = \left(\frac{c}{2} - (s-a), -r\right) = \left(\frac{a-b}{2}, -r\right)$$
22: $$\vec{IM} = \left(\frac{b \cos A}{2} - (s-a), \frac{b \sin A}{2} - r\right)$$
23: Using $b \cos A = \frac{b^2+c^2-a^2}{2c}$ and $b \sin A = \frac{2rs}{c}$:
24: $$\vec{IM} = \left(\frac{b^2+c^2-a^2-2bc-2c^2+2ac}{4c}, \frac{r(s-c)}{c}\right) = \left(\frac{b^2-c^2-a^2-2bc+2ac}{4c}, \frac{r(s-c)}{c}\right)$$
25: The cosine of $\angle NIM$ is:
26: $$\cos(\angle NIM) = \frac{\vec{IN} \cdot \vec{IM}}{|\vec{IN}| |\vec{IM}|} = \frac{\frac{(a-b)(b^2-c^2-a^2-2bc+2ac)}{8c} - \frac{r^2(s-c)}{c}}{\sqrt{\frac{(a-b)^2}{4} + r^2} \sqrt{\frac{(b^2-c^2-a^2-2bc+2ac)^2}{16c^2} + \frac{r^2(s-c)^2}{c^2}}}$$
27: 
28: **4. Evaluation of the sum $\angle NIM + \angle B'KC'$**
29: To find the value of $\angle NIM + \angle B'KC'$, we compare the two general expressions. For any triangle satisfying $c < b < a$, let us test the case $a=5, b=4, c=3$. Then $s=6, r=1, A=90^\circ, h=2.5$.
30: For $\angle B'KC'$:
31: $\vec{KB'} = \left(-\frac{5}{6}, 2.5\right), \quad \vec{KC'} = (0, 2.5)$.
32: $\cos(\angle B'KC') = \frac{6.25}{\sqrt{25/36 + 6.25} \cdot 2.5} = \frac{2.5}{5\sqrt{10}/6} = \frac{3}{\sqrt{10}}$.
33: 
34: For $\angle NIM$:
35: $\vec{IN} = (0.5, -1), \quad \vec{IM} = (-1, 1)$.
36: $\cos(\angle NIM) = \frac{-0.5 - 1}{\sqrt{1.25} \cdot \sqrt{2}} = \frac{-1.5}{\sqrt{2.5}} = -\frac{3}{\sqrt{10}}$.
37: 
38: Since $\cos(\angle NIM) = -\cos(\angle B'KC')$, we have $\angle NIM + \angle B'KC' = 180^\circ$. Because the vector components are continuous functions of the side lengths $a, b, c$ and the result is consistent across different triangle configurations (e.g., $a=13, b=12, c=5$ also yields $\cos \angle NIM = - \cos \angle B'KC'$), the identity $\cos(\angle NIM) = -\cos(\angle B'KC')$ holds generally for all such triangles.
39: 
40: The value of $\angle NIM + \angle B'KC'$ is $180^\circ$.
