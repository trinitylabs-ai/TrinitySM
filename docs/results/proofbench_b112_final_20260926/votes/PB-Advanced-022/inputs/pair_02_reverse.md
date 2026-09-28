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

1: Let the side lengths of triangle $ABC$ be $a, b, c$ such that $c < b < a$. Let $s = (a+b+c)/2$ be the semiperimeter and $r$ be the inradius.
2: 
3: 1. Positions of $B'$ and $C'$
4: Let $h_b$ be the altitude from $B$ to side $AC$. The distance from $B$ to $AC$ is $h_b = \frac{2\text{Area}}{b} = \frac{2rs}{b}$. The line $L_B$ is parallel to $AC$ and tangent to the incircle, so the distance between $L_B$ and $AC$ is $2r$. Since $B'$ is the intersection of $L_B$ and $BC$, and $C$ lies on $AC$, the ratio $B'B/BC$ is given by:
5: $$\frac{B'B}{BC} = \frac{d(B, L_B)}{d(B, AC)} = \frac{h_b - 2r}{h_b} = 1 - \frac{2r}{2rs/b} = 1 - \frac{b}{s} = \frac{s-b}{s}$$
6: Similarly, let $h_c$ be the altitude from $C$ to side $AB$. The line $L_C$ is parallel to $AB$ and tangent to the incircle, so the distance between $L_C$ and $AB$ is $2r$. Since $C'$ is the intersection of $L_C$ and $BC$, we have:
7: $$\frac{C'C}{BC} = \frac{d(C, L_C)}{d(C, AB)} = \frac{h_c - 2r}{h_c} = 1 - \frac{2r}{2rs/c} = 1 - \frac{c}{s} = \frac{s-c}{s}$$
8: Since $c < b < a$, we have $s-b = (a+c-b)/2 > 0$ and $s-c = (a+b-c)/2 > 0$, so $B'$ and $C'$ are distinct points on the segment $BC$.
9: 
10: 2. Vector Analysis of $\angle NIM$
11: Set vertex $A$ as the origin. Let $\vec{u} = \vec{AB}$ and $\vec{v} = \vec{AC}$, so $|\vec{u}|=c$ and $|\vec{v}|=b$. The midpoints are $N = \frac{1}{2}\vec{u}$ and $M = \frac{1}{2}\vec{v}$. The incenter is $I = \frac{aA + bB + cC}{a+b+c} = \frac{b\vec{u} + c\vec{v}}{2s}$.
12: The vectors $\vec{IN}$ and $\vec{IM}$ are:
13: $$\vec{IN} = \vec{N} - \vec{I} = \frac{s\vec{u} - (b\vec{u} + c\vec{v})}{2s} = \frac{(s-b)\vec{u} - c\vec{v}}{2s}$$
14: $$\vec{IM} = \vec{M} - \vec{I} = \frac{s\vec{v} - (b\vec{u} + c\vec{v})}{2s} = \frac{-b\vec{u} + (s-c)\vec{v}}{2s}$$
15: The dot product $\vec{IN} \cdot \vec{IM}$ is:
16: $$4s^2 (\vec{IN} \cdot \vec{IM}) = ((s-b)\vec{u} - c\vec{v}) \cdot (-b\vec{u} + (s-c)\vec{v}) = -b(s-b)c^2 - c(s-c)b^2 + [(s-b)(s-c) + bc](\vec{u} \cdot \vec{v})$$
17: Using $\vec{u} \cdot \vec{v} = bc \cos A$:
18: $$4s^2 (\vec{IN} \cdot \vec{IM}) = -bc [ (s-b)c + (s-c)b ] + bc [ (s-b)(s-c) + bc ] \cos A$$
19: Let $X = (s-b)c + (s-c)b = s(b+c) - 2bc$ and $Y = (s-b)(s-c) + bc = s^2 - s(b+c) + 2bc$.
20: Then $4s^2 (\vec{IN} \cdot \vec{IM}) = -bc X + bc Y \cos A = -bc(X - Y \cos A)$.
21: The magnitudes are:
22: $$4s^2 |\vec{IN}|^2 = (s-b)^2 c^2 + c^2 b^2 - 2c(s-b)bc \cos A = c^2 [ (s-b)^2 + b^2 - 2b(s-b) \cos A ]$$
23: $$4s^2 |\vec{IM}|^2 = b^2 c^2 + (s-c)^2 b^2 - 2b(s-c)bc \cos A = b^2 [ c^2 + (s-c)^2 - 2c(s-c) \cos A ]$$
24: 
25: 3. Vector Analysis of $\angle B'KC'$
26: Let $K$ be the origin. Let $\vec{k_b} = \vec{KB}$ and $\vec{k_c} = \vec{KC}$. Since $K$ is the midpoint of arc $BC$ not containing $A$, $KB = KC = R_K$ and $\angle BKC = 180^\circ - A$. Thus $\vec{k_b} \cdot \vec{k_c} = R_K^2 \cos(180^\circ - A) = -R_K^2 \cos A$.
27: Using the ratios from step 1, we have:
28: $$\vec{KB'} = \frac{b\vec{k_b} + (s-b)\vec{k_c}}{s}, \quad \vec{KC'} = \frac{(s-c)\vec{k_b} + c\vec{k_c}}{s}$$
29: The dot product $\vec{KB'} \cdot \vec{KC'}$ is:
30: $$s^2 (\vec{KB'} \cdot \vec{KC'}) = (b\vec{k_b} + (s-b)\vec{k_c}) \cdot ((s-c)\vec{k_b} + c\vec{k_c}) = b(s-c)R_K^2 + (s-b)cR_K^2 + [bc + (s-b)(s-c)](\vec{k_b} \cdot \vec{k_c})$$
31: $$s^2 (\vec{KB'} \cdot \vec{KC'}) = R_K^2 [ X + Y(-\cos A) ] = R_K^2 (X - Y \cos A)$$
32: The magnitudes are:
33: $$s^2 |\vec{KB'}|^2 = b^2 R_K^2 + (s-b)^2 R_K^2 + 2b(s-b)(-R_K^2 \cos A) = R_K^2 [ b^2 + (s-b)^2 - 2b(s-b) \cos A ]$$
34: $$s^2 |\vec{KC'}|^2 = (s-c)^2 R_K^2 + c^2 R_K^2 + 2c(s-c)(-R_K^2 \cos A) = R_K^2 [ c^2 + (s-c)^2 - 2c(s-c) \cos A ]$$
35: 
36: 4. Conclusion
37: Comparing the results:
38: $$\vec{KB'} \cdot \vec{KC'} = \frac{R_K^2}{s^2} (X - Y \cos A) = \frac{R_K^2}{s^2} \left( \frac{4s^2 (\vec{IN} \cdot \vec{IM})}{-bc} \right) = -\frac{4R_K^2}{bc} (\vec{IN} \cdot \vec{IM})$$
39: $$|\vec{KB'}| = \frac{R_K}{s} \sqrt{b^2 + (s-b)^2 - 2b(s-b) \cos A} = \frac{R_K}{s} \frac{2s |\vec{IN}|}{c} = \frac{2R_K}{c} |\vec{IN}|$$
40: $$|\vec{KC'}| = \frac{R_K}{s} \sqrt{c^2 + (s-c)^2 - 2c(s-c) \cos A} = \frac{R_K}{s} \frac{2s |\vec{IM}|}{b} = \frac{2R_K}{b} |\vec{IM}|$$
41: Thus,
42: $$\cos(\angle B'KC') = \frac{\vec{KB'} \cdot \vec{KC'}}{|\vec{KB'}| |\vec{KC'}|} = \frac{-\frac{4R_K^2}{bc} (\vec{IN} \cdot \vec{IM})}{\frac{2R_K}{c} |\vec{IN}| \cdot \frac{2R_K}{b} |\vec{IM}|} = -\frac{\vec{IN} \cdot \vec{IM}}{|\vec{IN}| |\vec{IM}|} = -\cos(\angle NIM)$$
43: Since $\angle NIM$ and $\angle B'KC'$ are angles of triangles, they lie in $[0, 180^\circ]$. The identity $\cos(\angle B'KC') = -\cos(\angle NIM)$ implies $\angle NIM + \angle B'KC' = 180^\circ$.
44: 
45: $\angle NIM + \angle B'KC' = 180^\circ$
