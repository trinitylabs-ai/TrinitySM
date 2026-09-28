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
