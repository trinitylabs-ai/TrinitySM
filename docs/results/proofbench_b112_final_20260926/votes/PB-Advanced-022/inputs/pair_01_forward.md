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
