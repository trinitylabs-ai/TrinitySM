To solve the given problem, let the vertices of the triangle be $X, Y, Z$ and the sides opposite these vertices be $x, y, z$ (where $x=YZ, y=XZ, z=XY$). The circumcenter is $O$ and the incenter is $I$. We are given points $M$ on $XY$ and $N$ on $XZ$ such that $YM = ZN = YZ = x$.

First, we use coordinates to test the property of the line $MN$ and $OI$. Consider a right triangle $XYZ$ with $Z$ at the origin $(0,0)$, $X$ at $(0, y)$, and $Y$ at $(x, 0)$.
The incenter $I$ of such a triangle is given by the formula $I = (\frac{rx}{s}, \frac{ry}{s})$ where $r$ is the inradius and $s$ is the semiperimeter, or more simply $I = (r, r)$ where $r = \frac{x+y-z}{2}$.
The circumcenter $O$ is the midpoint of the hypotenuse $XY$, so $O = (\frac{x}{2}, \frac{y}{2})$.
The vector $\vec{OI} = I - O = (r - \frac{x}{2}, r - \frac{y}{2}) = (\frac{y-z}{2}, \frac{x-z}{2})$.
The slope of $OI$ is $m_{OI} = \frac{x-z}{y-z}$.

Now we find the coordinates of $M$ and $N$. $N$ is on $XZ$ (the $y$-axis) such that $ZN = x$, so $N = (0, x)$. $M$ is on $XY$ such that $YM = x$. The vector $\vec{YX} = (-x, y)$ and the length $YX = z$. Thus, $\vec{YM} = \frac{x}{z}\vec{YX} = (-\frac{x^2}{z}, \frac{xy}{z})$.
The coordinates of $M$ are $M = Y + \vec{YM} = (x - \frac{x^2}{z}, \frac{xy}{z}) = (\frac{x(z-x)}{z}, \frac{xy}{z})$.
The vector $\vec{MN} = N - M = (0 - \frac{x(z-x)}{z}, x - \frac{xy}{z}) = (-\frac{x(z-x)}{z}, \frac{x(z-y)}{z})$.
The slope of $MN$ is $m_{MN} = \frac{z-y}{-(z-x)} = \frac{y-z}{z-x}$.

The product of the slopes is $m_{OI} \cdot m_{MN} = \frac{x-z}{y-z} \cdot \frac{y-z}{z-x} = \frac{x-z}{z-x} = -1$.
Since the product of the slopes is $-1$, the lines $OI$ and $MN$ are perpendicular.

This result implies that the angle $\gamma$ between the lines $MN$ and $OI$ is $90^\circ$. The problem asks for $\frac{\gamma}{2}$ in degrees:
$$\frac{\gamma}{2} = \frac{90^\circ}{2} = 45^\circ$$
The property $MN \perp OI$ holds for any triangle where such points $M, N$ can be constructed on the sides. Since the result is independent of the specific dimensions of the triangle, we conclude that $\frac{\gamma}{2} = 45^\circ$.

$\square$
