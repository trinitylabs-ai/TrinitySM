# Problem

Given a triangle $XYZ$ with circumcenter $O$, the incircle of triangle
 $XYZ$ has center $I$. Let $M,N$ on the sides $XY,XZ$
 respectively such that $YM=ZN=YZ$. If $\gamma$ is the angle created
 by two lines $MN,OI$, what is $\frac{\gamma}{2}$ in terms of degree?

# Proof A

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

# Proof B

1: Let the vertices of the triangle be $X, Y, Z$ and the lengths of the sides opposite to them be $a=YZ, b=XZ, c=XY$. Let $O$ be the circumcenter and $I$ be the incenter of $\triangle XYZ$. We set the origin of our vector space at $O$. Let $\vec{x}, \vec{y}, \vec{z}$ be the vectors from $O$ to the vertices $X, Y, Z$, respectively. The circumradius is $R$, so $|\vec{x}| = |\vec{y}| = |\vec{z}| = R$.
2: 
3: The incenter $I$ is the barycentric combination of the vertices with weights $a, b, c$. Thus, the vector $\vec{OI}$ is given by:
4: $$\vec{OI} = \frac{a\vec{x} + b\vec{y} + c\vec{z}}{a+b+c}$$
5: Points $M$ and $N$ lie on the sides $XY$ and $XZ$, respectively, such that $YM = ZN = YZ = a$. Since $M$ is on the segment $XY$ and $YM=a$, the distance $XM = c-a$. The vector $\vec{M}$ is:
6: $$\vec{M} = \frac{XM \vec{y} + YM \vec{x}}{XY} = \frac{(c-a)\vec{y} + a\vec{x}}{c}$$
7: Similarly, since $N$ is on the segment $XZ$ and $ZN=a$, the distance $XN = b-a$. The vector $\vec{N}$ is:
8: $$\vec{N} = \frac{XN \vec{z} + ZN \vec{x}}{XZ} = \frac{(b-a)\vec{z} + a\vec{x}}{b}$$
9: The vector $\vec{MN}$ is given by:
10: $$\vec{MN} = \vec{N} - \vec{M} = \left(\frac{a}{b} - \frac{a}{c}\right)\vec{x} - \frac{c-a}{c}\vec{y} + \frac{b-a}{b}\vec{z} = \frac{a(c-b)}{bc}\vec{x} - \frac{c-a}{c}\vec{y} + \frac{b-a}{b}\vec{z}$$
11: To determine the angle $\gamma$ between the lines $MN$ and $OI$, we compute the dot product $\vec{OI} \cdot \vec{MN}$. Let $s = a+b+c$. Then:
12: $$s \cdot bc (\vec{OI} \cdot \vec{MN}) = (a\vec{x} + b\vec{y} + c\vec{z}) \cdot (a(c-b)\vec{x} - b(c-a)\vec{y} + c(b-a)\vec{z})$$
13: Expanding the dot product:
14: $$= a^2(c-b)R^2 - ab(c-a)(\vec{x}\cdot\vec{y}) + ac(b-a)(\vec{x}\cdot\vec{z}) + ab(c-b)(\vec{y}\cdot\vec{x}) - b^2(c-a)R^2 + bc(b-a)(\vec{y}\cdot\vec{z}) + ac(c-b)(\vec{z}\cdot\vec{x}) - bc(c-a)(\vec{z}\cdot\vec{y}) + c^2(b-a)R^2$$
15: Grouping the $R^2$ terms and the dot products $\vec{x}\cdot\vec{y}, \vec{x}\cdot\vec{z}, \vec{y}\cdot\vec{z}$:
16: $$= R^2 [a^2(c-b) - b^2(c-a) + c^2(b-a)] + ab(c-b - (c-a))(\vec{x}\cdot\vec{y}) + ac(b-a + c-b)(\vec{x}\cdot\vec{z}) + bc(b-a - (c-a))(\vec{y}\cdot\vec{z})$$
17: $$= R^2 [a^2(c-b) - b^2(c-a) + c^2(b-a)] + ab(a-b)(\vec{x}\cdot\vec{y}) + ac(c-a)(\vec{x}\cdot\vec{z}) + bc(b-c)(\vec{y}\cdot\vec{z})$$
18: Using the identities $2\vec{x}\cdot\vec{y} = 2R^2 - c^2$, $2\vec{x}\cdot\vec{z} = 2R^2 - b^2$, and $2\vec{y}\cdot\vec{z} = 2R^2 - a^2$:
19: $$= R^2 [a^2c - a^2b - b^2c + b^2a + c^2b - c^2a] + \frac{ab(a-b)}{2}(2R^2-c^2) + \frac{ac(c-a)}{2}(2R^2-b^2) + \frac{bc(b-c)}{2}(2R^2-a^2)$$
20: The coefficient of $R^2$ is:
21: $$a^2c - a^2b - b^2c + b^2a + c^2b - c^2a + a^2b - ab^2 + ac^2 - a^2c + b^2c - bc^2 = 0$$
22: The remaining terms are:
23: $$- \frac{1}{2} [ ab(a-b)c^2 + ac(c-a)b^2 + bc(b-c)a^2 ] = - \frac{abc}{2} [ c(a-b) + b(c-a) + a(b-c) ] = - \frac{abc}{2} [ 0 ] = 0$$
24: Since $\vec{OI} \cdot \vec{MN} = 0$, the lines $MN$ and $OI$ are perpendicular. Thus, $\gamma = 90^\circ$, and the value of $\frac{\gamma}{2}$ is $45^\circ$.
