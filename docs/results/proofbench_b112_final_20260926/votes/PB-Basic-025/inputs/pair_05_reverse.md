# Problem

Given a triangle $XYZ$ with circumcenter $O$, the incircle of triangle
 $XYZ$ has center $I$. Let $M,N$ on the sides $XY,XZ$
 respectively such that $YM=ZN=YZ$. If $\gamma$ is the angle created
 by two lines $MN,OI$, what is $\frac{\gamma}{2}$ in terms of degree?

# Proof A

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
