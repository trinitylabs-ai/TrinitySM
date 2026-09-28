To find the angle $\gamma$ between the lines $MN$ and $OI$ in a triangle $XYZ$, let the side lengths opposite to vertices $X, Y, Z$ be $YZ = x$, $XZ = y$, and $XY = z$. Let the position vectors of the vertices be $\vec{X}, \vec{Y}, \vec{Z}$. For convenience, we set the origin at vertex $X$, so $\vec{X} = \vec{0}$. Let $\vec{y} = \vec{XY}$ and $\vec{z} = \vec{XZ}$. Then $|\vec{y}| = z$, $|\vec{z}| = y$, and $|\vec{y} - \vec{z}| = x$.

The points $M$ and $N$ are on the sides $XY$ and $XZ$ respectively such that $YM = ZN = YZ = x$. The point $M$ is on the line $XY$, and the distance $YM = x$. The position vector of $M$ is $\vec{M} = \vec{Y} + \frac{x}{z}(\vec{X} - \vec{Y}) = \vec{y} - \frac{x}{z}\vec{y} = \frac{z-x}{z}\vec{y}$. Similarly, the point $N$ is on the line $XZ$ such that $ZN = x$, so $\vec{N} = \vec{Z} + \frac{x}{y}(\vec{X} - \vec{Z}) = \vec{z} - \frac{x}{y}\vec{z} = \frac{y-x}{y}\vec{z}$.
The vector $\vec{MN}$ is given by:
\[ \vec{MN} = \vec{N} - \vec{M} = \frac{y-x}{y}\vec{z} - \frac{z-x}{z}\vec{y} \]
The incenter $I$ of triangle $XYZ$ is given by the formula:
\[ \vec{I} = \frac{x\vec{X} + y\vec{Y} + z\vec{Z}}{x+y+z} = \frac{y\vec{y} + z\vec{z}}{x+y+z} \]
We compute the dot product $\vec{MN} \cdot \vec{I}$:
\[ \vec{MN} \cdot \vec{I} = \left( \frac{y-x}{y}\vec{z} - \frac{z-x}{z}\vec{y} \right) \cdot \frac{y\vec{y} + z\vec{z}}{x+y+z} \]
\[ = \frac{1}{x+y+z} \left[ \frac{y-x}{y}(y\vec{z}\cdot\vec{y} + z|\vec{z}|^2) - \frac{z-x}{z}(y|\vec{y}|^2 + z\vec{y}\cdot\vec{z}) \right] \]
Since $|\vec{y}|^2 = z^2$ and $|\vec{z}|^2 = y^2$:
\[ = \frac{1}{x+y+z} \left[ (y-x)(\vec{z}\cdot\vec{y}) + z(y-x)y - (z-x)yz - (z-x)(\vec{y}\cdot\vec{z}) \right] \]
\[ = \frac{1}{x+y+z} \left[ (y-z)(\vec{z}\cdot\vec{y}) + zy^2 - xyz - yz^2 + xyz \right] = \frac{y-z}{x+y+z} \left[ \vec{z}\cdot\vec{y} + zy \right] \]
Using the law of cosines, $\vec{z}\cdot\vec{y} = yz \cos X = \frac{y^2+z^2-x^2}{2}$. Substituting this in:
\[ \vec{MN} \cdot \vec{I} = \frac{y-z}{x+y+z} \left( \frac{y^2+z^2-x^2+2yz}{2} \right) = \frac{y-z}{x+y+z} \frac{(y+z)^2-x^2}{2} = \frac{(y-z)(y+z-x)}{2} \]
Next, let $O$ be the circumcenter. The vector $\vec{O}$ satisfies the properties $\vec{O} \cdot \vec{y} = \frac{1}{2}|\vec{y}|^2 = \frac{1}{2}z^2$ and $\vec{O} \cdot \vec{z} = \frac{1}{2}|\vec{z}|^2 = \frac{1}{2}y^2$, as $O$ lies on the perpendicular bisectors of $XY$ and $XZ$. We compute $\vec{MN} \cdot \vec{O}$:
\[ \vec{MN} \cdot \vec{O} = \left( \frac{y-x}{y}\vec{z} - \frac{z-x}{z}\vec{y} \right) \cdot \vec{O} = \frac{y-x}{y}(\vec{z} \cdot \vec{O}) - \frac{z-x}{z}(\vec{y} \cdot \vec{O}) \]
\[ = \frac{y-x}{y} \frac{y^2}{2} - \frac{z-x}{z} \frac{z^2}{2} = \frac{y(y-x) - z(z-x)}{2} = \frac{y^2 - xy - z^2 + xz}{2} = \frac{(y-z)(y+z-x)}{2} \]
Comparing the two results, we find that $\vec{MN} \cdot \vec{I} = \vec{MN} \cdot \vec{O}$. Consequently:
\[ \vec{MN} \cdot \vec{OI} = \vec{MN} \cdot (\vec{I} - \vec{O}) = \vec{MN} \cdot \vec{I} - \vec{MN} \cdot \vec{O} = 0 \]
This proves that the line $MN$ is perpendicular to the line $OI$. Thus, the angle $\gamma$ between the lines is $90^\circ$. The requested value is:
\[ \frac{\gamma}{2} = \frac{90^\circ}{2} = 45^\circ \]

\(\square\)
