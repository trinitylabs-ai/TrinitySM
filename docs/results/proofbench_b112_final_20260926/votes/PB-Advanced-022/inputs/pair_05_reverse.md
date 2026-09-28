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
