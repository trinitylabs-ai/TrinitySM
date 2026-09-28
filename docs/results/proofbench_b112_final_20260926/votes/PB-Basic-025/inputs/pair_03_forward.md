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

1: Let the side lengths of triangle $XYZ$ be $YZ = x$, $XZ = y$, and $XY = z$. Let $O$ be the circumcenter and $I$ be the incenter of the triangle. We set the circumcenter $O$ as the origin of our coordinate system. Let the vectors from $O$ to the vertices $X, Y, Z$ be $\vec{X}, \vec{Y}, \vec{Z}$. Since $O$ is the circumcenter, $|\vec{X}| = |\vec{Y}| = |\vec{Z}| = R$, where $R$ is the circumradius.
2: 
3: The vector to the incenter $I$ is given by the formula:
4: \[ \vec{OI} = \frac{x\vec{X} + y\vec{Y} + z\vec{Z}}{x+y+z} \]
5: The points $M$ and $N$ lie on the sides $XY$ and $XZ$, respectively, such that $YM = ZN = YZ = x$. Consequently, the distances from $X$ are $XM = XY - YM = z - x$ and $XN = XZ - ZN = y - x$. We express the vectors $\vec{XM}$ and $\vec{XN}$ as:
6: \[ \vec{XM} = \frac{z-x}{z} \vec{XY} = \frac{z-x}{z} (\vec{Y} - \vec{X}), \quad \vec{XN} = \frac{y-x}{y} \vec{XZ} = \frac{y-x}{y} (\vec{Z} - \vec{X}) \]
7: The vector $\vec{MN}$ is then:
8: \[ \vec{MN} = \vec{XN} - \vec{XM} = \frac{y-x}{y} \vec{Z} - \frac{z-x}{z} \vec{Y} + \left( \frac{z-x}{z} - \frac{y-x}{y} \right) \vec{X} \]
9: Simplifying the coefficient of $\vec{X}$:
10: \[ \frac{z-x}{z} - \frac{y-x}{y} = \left(1 - \frac{x}{z}\right) - \left(1 - \frac{x}{y}\right) = \frac{x}{y} - \frac{x}{z} = \frac{x(z-y)}{yz} \]
11: Thus, we have:
12: \[ \vec{MN} = \frac{1}{yz} [ x(z-y)\vec{X} - y(z-x)\vec{Y} + z(y-x)\vec{Z} ] \]
13: To find the angle $\gamma$ between the lines $MN$ and $OI$, we compute the dot product $\vec{MN} \cdot \vec{OI}$:
14: \[ \vec{MN} \cdot \vec{OI} = \frac{1}{yz(x+y+z)} [ x(z-y)\vec{X} - y(z-x)\vec{Y} + z(y-x)\vec{Z} ] \cdot [ x\vec{X} + y\vec{Y} + z\vec{Z} ] \]
15: Let $S$ be the value of the dot product in the brackets. Using $\vec{X}^2 = \vec{Y}^2 = \vec{Z}^2 = R^2$:
16: \[ S = R^2 [ x^2(z-y) - y^2(z-x) + z^2(y-x) ] + [ xy(z-y) - xy(z-x) ] \vec{X} \cdot \vec{Y} + [ xz(z-y) + xz(y-x) ] \vec{X} \cdot \vec{Z} + [ -yz(z-x) + yz(y-x) ] \vec{Y} \cdot \vec{Z} \]
17: The first term simplifies to $R^2(x-y)(y-z)(z-x)$. The other coefficients simplify as follows:
18: \[ xy(z-y) - xy(z-x) = xy(x-y), \quad xz(z-y) + xz(y-x) = xz(z-x), \quad -yz(z-x) + yz(y-x) = yz(y-z) \]
19: Thus,
20: \[ S = R^2(x-y)(y-z)(z-x) + xy(x-y)\vec{X} \cdot \vec{Y} + xz(z-x)\vec{X} \cdot \vec{Z} + yz(y-z)\vec{Y} \cdot \vec{Z} \]
21: Using the property $\vec{X} \cdot \vec{Y} = R^2 \cos(2\angle Z)$, $\vec{Y} \cdot \vec{Z} = R^2 \cos(2\angle X)$, and $\vec{Z} \cdot \vec{X} = R^2 \cos(2\angle Y)$:
22: \[ S = R^2 [ (x-y)(y-z)(z-x) + xy(x-y)\cos(2\angle Z) + yz(y-z)\cos(2\angle X) + zx(z-x)\cos(2\angle Y) ] \]
23: Using $\cos(2\theta) = 1 - 2\sin^2 \theta$:
24: \[ \sum_{\text{cyc}} xy(x-y)\cos(2\angle Z) = \sum_{\text{cyc}} xy(x-y) - 2 \sum_{\text{cyc}} xy(x-y)\sin^2(\angle Z) \]
25: We observe that $\sum_{\text{cyc}} xy(x-y) = x^2y - xy^2 + y^2z - yz^2 + z^2x - zx^2 = -(x-y)(y-z)(z-x)$. This cancels the first term in $S$. Substituting $\sin(\angle Z) = \frac{z}{2R}$:
26: \[ S = -2R^2 \sum_{\text{cyc}} xy(x-y) \frac{z^2}{4R^2} = -\frac{xyz}{2} \sum_{\text{cyc}} z(x-y) = -\frac{xyz}{2} (zx - zy + xy - xz + yz - yx) = 0 \]
27: Since $\vec{MN} \cdot \vec{OI} = 0$, the lines $MN$ and $OI$ are perpendicular, so $\gamma = 90^\circ$. Therefore:
28: \[ \frac{\gamma}{2} = \frac{90^\circ}{2} = 45^\circ \]
