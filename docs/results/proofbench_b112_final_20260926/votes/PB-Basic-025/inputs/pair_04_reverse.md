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
