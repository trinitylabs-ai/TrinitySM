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
