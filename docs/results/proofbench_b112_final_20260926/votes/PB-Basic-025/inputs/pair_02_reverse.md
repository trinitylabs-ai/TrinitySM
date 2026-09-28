# Problem

Given a triangle $XYZ$ with circumcenter $O$, the incircle of triangle
 $XYZ$ has center $I$. Let $M,N$ on the sides $XY,XZ$
 respectively such that $YM=ZN=YZ$. If $\gamma$ is the angle created
 by two lines $MN,OI$, what is $\frac{\gamma}{2}$ in terms of degree?

# Proof A

1: To find the angle $\gamma$ between the lines $MN$ and $OI$ in triangle $XYZ$, we employ a vector-based approach. Let the side lengths of the triangle be $YZ = a$, $XZ = b$, and $XY = c$. Let the circumcenter $O$ be the origin of our coordinate system. Thus, the vectors $\vec{X}, \vec{Y}, \vec{Z}$ from $O$ to the vertices satisfy $|\vec{X}| = |\vec{Y}| = |\vec{Z}| = R$, where $R$ is the circumradius.
2: 
3: The incenter $I$ of a triangle is the weighted average of its vertices:
4: \[ \vec{I} = \frac{a\vec{X} + b\vec{Y} + c\vec{Z}}{a+b+c} \]
5: Let $S = a+b+c$. Since $O$ is the origin, the vector $\vec{OI} = \vec{I}$.
6: 
7: Points $M$ and $N$ are on the sides $XY$ and $XZ$ respectively such that $YM = ZN = YZ = a$.
8: The point $M$ divides the segment $XY$ in the ratio $XM:MY = (c-a):a$. Thus:
9: \[ \vec{M} = \frac{a\vec{X} + (c-a)\vec{Y}}{c} = \frac{a}{c}\vec{X} + \left(1 - \frac{a}{c}\right)\vec{Y} \]
10: Similarly, the point $N$ divides the segment $XZ$ in the ratio $XN:NZ = (b-a):a$:
11: \[ \vec{N} = \frac{a\vec{X} + (b-a)\vec{Z}}{b} = \frac{a}{b}\vec{X} + \left(1 - \frac{a}{b}\right)\vec{Z} \]
12: The vector $\vec{MN}$ is given by:
13: \[ \vec{MN} = \vec{N} - \vec{M} = \left(\frac{a}{b} - \frac{a}{c}\right)\vec{X} - \left(1 - \frac{a}{c}\right)\vec{Y} + \left(1 - \frac{a}{b}\right)\vec{Z} \]
14: To determine the angle $\gamma$, we compute the dot product $\vec{MN} \cdot \vec{OI}$. Let $\vec{S} = a\vec{X} + b\vec{Y} + c\vec{Z} = S\vec{I}$. Then:
15: \[ \vec{MN} \cdot \vec{OI} = \frac{1}{S} \left[ \left(\frac{a}{b} - \frac{a}{c}\right)\vec{X} \cdot \vec{S} - \left(1 - \frac{a}{c}\right)\vec{Y} \cdot \vec{S} + \left(1 - \frac{a}{b}\right)\vec{Z} \cdot \vec{S} \right] \]
16: We evaluate the dot products $\vec{X} \cdot \vec{S}$, $\vec{Y} \cdot \vec{S}$, and $\vec{Z} \cdot \vec{S}$ using the identity $2\vec{A} \cdot \vec{B} = |\vec{A}|^2 + |\vec{B}|^2 - |\vec{A}-\vec{B}|^2$. For example, $2\vec{X} \cdot \vec{Y} = 2R^2 - c^2$.
17: \[ \vec{X} \cdot \vec{S} = aR^2 + b\left(R^2 - \frac{c^2}{2}\right) + c\left(R^2 - \frac{b^2}{2}\right) = SR^2 - \frac{bc(b+c)}{2} \]
18: \[ \vec{Y} \cdot \vec{S} = a\left(R^2 - \frac{c^2}{2}\right) + bR^2 + c\left(R^2 - \frac{a^2}{2}\right) = SR^2 - \frac{ac(a+c)}{2} \]
19: \[ \vec{Z} \cdot \vec{S} = a\left(R^2 - \frac{b^2}{2}\right) + b\left(R^2 - \frac{a^2}{2}\right) + cR^2 = SR^2 - \frac{ab(a+b)}{2} \]
20: Substituting these back into the expression for $\vec{MN} \cdot \vec{OI}$:
21: The coefficient of $SR^2$ is $\left(\frac{a}{b} - \frac{a}{c}\right) - \left(1 - \frac{a}{c}\right) + \left(1 - \frac{a}{b}\right) = 0$.
22: The remaining terms are:
23: \[ \vec{MN} \cdot \vec{OI} = \frac{1}{2S} \left[ -\left(\frac{a}{b} - \frac{a}{c}\right)bc(b+c) + \left(1 - \frac{a}{c}\right)ac(a+c) - \left(1 - \frac{a}{b}\right)ab(a+b) \right] \]
24: \[ = \frac{1}{2S} \left[ -a(c-b)(b+c) + a(c-a)(a+c) - a(b-a)(a+b) \right] \]
25: \[ = \frac{a}{2S} \left[ -(c^2 - b^2) + (c^2 - a^2) - (b^2 - a^2) \right] = \frac{a}{2S} [ -c^2 + b^2 + c^2 - a^2 - b^2 + a^2 ] = 0 \]
26: Since the dot product is zero, the line $MN$ is perpendicular to the line $OI$. Thus, $\gamma = 90^\circ$.
27: The value of $\frac{\gamma}{2}$ is therefore:
28: \[ \frac{90^\circ}{2} = 45^\circ \]
29: 
30: $\frac{\gamma}{2} = 45^\circ$ \(\square\)

# Proof B

1: To find the angle $\gamma$ between the lines $MN$ and $OI$, we analyze the geometry of triangle $XYZ$ using vector methods. Let the side lengths be $YZ = a$, $XZ = b$, and $XY = c$, and let the internal angles at vertices $X, Y, Z$ be $A, B, C$ respectively.
2: 
3: ### 1. Vector Representation of $MN$
4: Let vertex $X$ be the origin $(0,0)$. Let $\vec{u}$ and $\vec{v}$ be unit vectors along the sides $XY$ and $XZ$ respectively. The positions of the vertices are:
5: - $X = \vec{0}$
6: - $Y = c\vec{u}$
7: - $Z = b\vec{v}$
8: 
9: Points $M$ and $N$ lie on the sides $XY$ and $XZ$ such that $YM = ZN = YZ = a$. Their positions are:
10: - $\vec{XM} = (c-a)\vec{u}$
11: - $\vec{XN} = (b-a)\vec{v}$
12: 
13: The vector $\vec{MN}$ is given by:
14: $$\vec{MN} = \vec{XN} - \vec{XM} = (b-a)\vec{v} - (c-a)\vec{u}$$
15: 
16: ### 2. Vector Representation of $OI$
17: The incenter $I$ is given by the formula:
18: $$\vec{XI} = \frac{a\vec{X} + b\vec{Y} + c\vec{Z}}{a+b+c} = \frac{a(0) + b(c\vec{u}) + c(b\vec{v})}{a+b+c} = \frac{bc}{S}(\vec{u} + \vec{v})$$
19: where $S = a+b+c$.
20: 
21: The circumcenter $O$ is the point such that its projections onto $XY$ and $XZ$ are the midpoints of those sides. Let $\vec{XO} = p\vec{u} + q\vec{v}$. Then:
22: - $\vec{XO} \cdot \vec{u} = p + q\cos A = \frac{c}{2}$
23: - $\vec{XO} \cdot \vec{v} = p\cos A + q = \frac{b}{2}$
24: 
25: Solving for $p$ and $q$:
26: $$p = \frac{c - b\cos A}{2\sin^2 A}, \quad q = \frac{b - c\cos A}{2\sin^2 A}$$
27: The vector $\vec{OI}$ is:
28: $$\vec{OI} = \vec{XI} - \vec{XO} = \left( \frac{bc}{S} - p \right)\vec{u} + \left( \frac{bc}{S} - q \right)\vec{v}$$
29: 
30: ### 3. Evaluating the Angle $\gamma$
31: Let $C_u = \frac{bc}{S} - p$ and $C_v = \frac{bc}{S} - q$. The dot product $\vec{MN} \cdot \vec{OI}$ is:
32: $$\vec{MN} \cdot \vec{OI} = [(b-a)\vec{v} - (c-a)\vec{u}] \cdot [C_u\vec{u} + C_v\vec{v}] = (b-a)C_v - (c-a)C_u + \cos A [(b-a)C_u - (c-a)C_v]$$
33: Rearranging the terms:
34: $$\vec{MN} \cdot \vec{OI} = C_v(b-a - (c-a)\cos A) - C_u(c-a - (b-a)\cos A)$$
35: Substituting $C_u$ and $C_v$:
36: $$\vec{MN} \cdot \vec{OI} = \frac{bc}{S} [b-a - (c-a)\cos A - (c-a - (b-a)\cos A)] - [q(b-a - (c-a)\cos A) - p(c-a - (b-a)\cos A)]$$
37: $$\vec{MN} \cdot \vec{OI} = \frac{bc}{S} (b-c)(1+\cos A) - T$$
38: where $T = q(b-a - (c-a)\cos A) - p(c-a - (b-a)\cos A)$. Substituting $p$ and $q$:
39: $$2\sin^2 A \cdot T = (b-c\cos A)(b-a - c\cos A + a\cos A) - (c-b\cos A)(c-a - b\cos A + a\cos A)$$
40: Expanding the products:
41: $$2\sin^2 A \cdot T = (b^2 - ab - bc\cos A + ab\cos A - bc\cos A + ac\cos A + c^2\cos^2 A - ac\cos^2 A) - (c^2 - ac - bc\cos A + ac\cos A - bc\cos A + ab\cos A + b^2\cos^2 A - ab\cos^2 A)$$
42: $$2\sin^2 A \cdot T = b^2 - c^2 - ab + ac + (c^2-b^2)\cos^2 A + (ab-ac)\cos^2 A = (b^2-c^2)\sin^2 A - a(b-c)\sin^2 A$$
43: Thus, $T = \frac{(b-c)(b+c-a)}{2}$. Substituting $T$ back:
44: $$\vec{MN} \cdot \vec{OI} = (b-c) \left[ \frac{bc(1+\cos A)}{S} - \frac{b+c-a}{2} \right]$$
45: By the Law of Cosines, $a^2 = b^2+c^2-2bc\cos A$, so $2bc(1+\cos A) = 2bc + b^2+c^2-a^2 = (b+c)^2-a^2 = (b+c-a)(b+c+a) = (b+c-a)S$.
46: Therefore, $\frac{bc(1+\cos A)}{S} = \frac{b+c-a}{2}$, which implies $\vec{MN} \cdot \vec{OI} = 0$.
47: 
48: Since the dot product is zero, the lines $MN$ and $OI$ are perpendicular for any non-equilateral triangle. Thus, $\gamma = 90^\circ$.
49: $$\frac{\gamma}{2} = \frac{90^\circ}{2} = 45^\circ$$
