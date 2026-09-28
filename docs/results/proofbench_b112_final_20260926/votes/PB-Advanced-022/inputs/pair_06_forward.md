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

1: Let the side lengths of triangle $ABC$ be $BC=a$, $AC=b$, and $AB=c$. Let $s = \frac{a+b+c}{2}$ be the semi-perimeter and $r$ be the inradius. Let $x=s-a$, $y=s-b$, and $z=s-c$. Then $a=y+z$, $b=x+z$, and $c=x+y$.
2: 
3: **1. Positions of $B'$ and $C'$**
4: The line $L_{B'}$ is parallel to $AC$ and tangent to the incircle. Since $AC$ is also tangent to the incircle, the distance between $L_{B'}$ and $AC$ is $2r$. Let $h_b$ be the altitude from $B$ to $AC$. Since $B'$ lies on $BC$ and $L_{B'}$ is parallel to $AC$, by similar triangles, we have:
5: $$\frac{BB'}{BC} = \frac{h_b - 2r}{h_b} = 1 - \frac{2r}{h_b}$$
6: Substituting $h_b = \frac{2\Delta}{b} = \frac{2rs}{b}$, we get $\frac{BB'}{a} = 1 - \frac{b}{s} = \frac{s-b}{s}$, so $BB' = \frac{a(s-b)}{s}$.
7: Similarly, for $C'$ on $BC$ such that the line $L_{C'}$ is parallel to $AB$ and tangent to the incircle, we have:
8: $$\frac{CC'}{BC} = 1 - \frac{2r}{h_c} = 1 - \frac{c}{s} = \frac{s-c}{s} \implies CC' = \frac{a(s-c)}{s}$$
9: 
10: **2. Calculation of $\angle B'KC'$**
11: Set $B$ as the origin $(0,0)$ and $C$ as $(a,0)$. Then $B' = (\frac{a(s-b)}{s}, 0)$ and $C' = (a - \frac{a(s-c)}{s}, 0) = (\frac{ac}{s}, 0)$.
12: $K$ is the midpoint of the arc $BC$ not containing $A$, so $K$ lies on the perpendicular bisector of $BC$ at $x = a/2$. The distance from $K$ to $BC$ is $h_K = \frac{a}{2} \tan(A/2)$.
13: Let $\beta = \angle B'KC'$. The vectors $\vec{KB'}$ and $\vec{KC'}$ are:
14: $$\vec{KB'} = \left(\frac{a(s-b)}{s} - \frac{a}{2}, h_K\right) = \left(\frac{a(s-2b)}{2s}, h_K\right), \quad \vec{KC'} = \left(\frac{ac}{s} - \frac{a}{2}, h_K\right) = \left(\frac{a(2c-s)}{2s}, h_K\right)$$
15: The dot product is $\vec{KB'} \cdot \vec{KC'} = \frac{a^2(s-2b)(2c-s)}{4s^2} + h_K^2$. Using $h_K^2 = \frac{a^2}{4} \frac{(s-b)(s-c)}{s(s-a)}$ and the variables $x, y, z$:
16: $$\vec{KB'} \cdot \vec{KC'} = \frac{(y+z)^2}{4s^2} \left[ (y-x-z)(x+y-z) + \frac{syz}{x} \right] = \frac{(y+z)^2}{4s^2 x} [x(y^2+z^2-yz-x^2) + y^2z+yz^2]$$
17: Let $P = xy^2+xz^2-xyz-x^3+y^2z+yz^2$. Then $\vec{KB'} \cdot \vec{KC'} = \frac{(y+z)^2 P}{4s^2 x}$.
18: The squared lengths are $|\vec{KB'}|^2 = \frac{(y+z)^2}{4s^2 x} Q$ and $|\vec{KC'}|^2 = \frac{(y+z)^2}{4s^2 x} R$, where $Q = x(y-x-z)^2 + syz$ and $R = x(x+y-z)^2 + syz$.
19: Thus, $\cos \beta = \frac{P}{\sqrt{QR}}$.
20: 
21: **3. Calculation of $\angle NIM$**
22: Let $\alpha = \angle NIM$. $N$ and $M$ are midpoints of $AB$ and $AC$. $NM = a/2$.
23: Using the distance from $I$ to the midpoints: $IN^2 = r^2 + \frac{(b-a)^2}{4}$ and $IM^2 = r^2 + \frac{(c-a)^2}{4}$.
24: By the Law of Cosines in $\triangle NIM$:
25: $$\cos \alpha = \frac{IN^2 + IM^2 - NM^2}{2 IN IM} = \frac{2r^2 + \frac{(b-a)^2 + (c-a)^2 - a^2}{4}}{2 IN IM}$$
26: Substituting $r^2 = \frac{xyz}{s}$ and the side lengths in terms of $x, y, z$:
27: Numerator $= \frac{2xyz}{s} + \frac{2x^2-2xy-2xz-2yz}{4} = \frac{x^3-xy^2-y^2z-yz^2-xz^2+xyz}{2s} = -\frac{P}{2s}$.
28: The denominator is $2 IN IM = 2 \sqrt{\frac{Q_{IN}}{4s} \frac{R_{IN}}{4s}} = \frac{\sqrt{Q_{IN} R_{IN}}}{2s}$, where $Q_{IN} = 4xyz + s(x-y)^2$ and $R_{IN} = 4xyz + s(x-z)^2$.
29: It can be verified algebraically that $Q_{IN} R_{IN} = QR$.
30: Thus, $\cos \alpha = \frac{-P/2s}{\sqrt{QR}/2s} = -\frac{P}{\sqrt{QR}}$.
31: 
32: **4. Conclusion**
33: Since $\cos \alpha = -\cos \beta$, it follows that $\alpha + \beta = 180^\circ$.
34: Therefore, $\angle NIM + \angle B'KC' = 180^\circ$.
