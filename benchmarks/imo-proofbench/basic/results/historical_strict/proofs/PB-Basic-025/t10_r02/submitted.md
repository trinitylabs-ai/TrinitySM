To determine the angle $\gamma$ between the lines $MN$ and $OI$ in triangle $XYZ$, we use a vector-based approach with the circumcenter $O$ as the origin. Let the position vectors of the vertices be $\vec{X}, \vec{Y}, \vec{Z}$, with $|\vec{X}| = |\vec{Y}| = |\vec{Z}| = R$. Let the side lengths be $YZ=a$, $XZ=b$, and $XY=c$.

The incenter $I$ is given by the formula:
\[ \vec{OI} = \frac{a\vec{X} + b\vec{Y} + c\vec{Z}}{a+b+c} \]
Points $M$ and $N$ lie on the sides $XY$ and $XZ$ respectively such that $YM=ZN=YZ=a$.
Since $M$ is on $XY$ and $YM=a$, the distance $XM = c-a$. Thus, $M$ divides $XY$ in the ratio $XM:MY = (c-a):a$. The position vector of $M$ is:
\[ \vec{M} = \frac{a\vec{X} + (c-a)\vec{Y}}{c} = \frac{a}{c}\vec{X} + \left(1 - \frac{a}{c}\right)\vec{Y} \]
Similarly, since $N$ is on $XZ$ and $ZN=a$, the distance $XN = b-a$. The position vector of $N$ is:
\[ \vec{N} = \frac{a\vec{X} + (b-a)\vec{Z}}{b} = \frac{a}{b}\vec{X} + \left(1 - \frac{a}{b}\right)\vec{Z} \]
The vector $\vec{MN}$ is:
\[ \vec{MN} = \vec{N} - \vec{M} = \left(\frac{a}{b} - \frac{a}{c}\right)\vec{X} - \left(1 - \frac{a}{c}\right)\vec{Y} + \left(1 - \frac{a}{b}\right)\vec{Z} \]
Let $u = 1 - \frac{a}{b}$ and $v = 1 - \frac{a}{c}$. Then $\frac{a}{b} - \frac{a}{c} = v - u$. The vector $\vec{MN}$ is:
\[ \vec{MN} = (v-u)\vec{X} - v\vec{Y} + u\vec{Z} \]
We compute the dot product $\vec{MN} \cdot \vec{OI}$:
\[ (a+b+c) \vec{MN} \cdot \vec{OI} = [(v-u)\vec{X} - v\vec{Y} + u\vec{Z}] \cdot [a\vec{X} + b\vec{Y} + c\vec{Z}] \]
Using $\vec{X} \cdot \vec{X} = R^2$ and $\vec{X} \cdot \vec{Y} = R^2 - \frac{c^2}{2}$, $\vec{X} \cdot \vec{Z} = R^2 - \frac{b^2}{2}$, and $\vec{Y} \cdot \vec{Z} = R^2 - \frac{a^2}{2}$, the $R^2$ terms sum to:
\[ [(v-u)a + (v-u)b + (v-u)c - va - vb - vc + ua + ub + uc] R^2 = (v-u-v+u)(a+b+c)R^2 = 0 \]
The remaining terms are:
\[ -\frac{1}{2} [ (v-u)bc^2 + (v-u)cb^2 - v ac^2 - v ca^2 + u ab^2 + u ba^2 ] \]
Substituting $u = 1 - \frac{a}{b}$ and $v = 1 - \frac{a}{c}$, we evaluate each term:
- $(v-u)bc^2 = (\frac{a}{b} - \frac{a}{c})bc^2 = ac^2 - abc$
- $(v-u)cb^2 = (\frac{a}{b} - \frac{a}{c})cb^2 = abc - ab^2$
- $-v ac^2 = -(1 - \frac{a}{c})ac^2 = -ac^2 + a^2c$
- $-v ca^2 = -(1 - \frac{a}{c})ca^2 = -ca^2 + a^3$
- $u ab^2 = (1 - \frac{a}{b})ab^2 = ab^2 - a^2b$
- $u ba^2 = (1 - \frac{a}{b})ba^2 = ba^2 - a^3$

Summing these, the expression simplifies to:
\[ (ac^2 - abc) + (abc - ab^2) + (-ac^2 + a^2c) + (-ca^2 + a^3) + (ab^2 - a^2b) + (ba^2 - a^3) = 0 \]
Thus, $\vec{MN} \cdot \vec{OI} = 0$, meaning $MN \perp OI$. In all such triangles, $\gamma = 90^\circ$.

Thus, $\gamma = 90^\circ$, and $\frac{\gamma}{2} = 45^\circ$.

\(\square\)
