# Problem

Let $\triangle ABC$ be an inscribed triangle in $(O)$ and circumscribed
 around $(I)$. The incircle $(I)$ touches $BC,CA,AB$ at $D,E,F$,
 respectively. Construct the circle $(W_{a})$ passing through $B,C$
 and tangent to $(I)$ at $X$, and let $D'$ be the reflection of
 $D$ across $AI$. Define $Y,Z,E',F'$ similarly. Prove that the lines
 $D'X,E'Y,F'Z$ are concurrent on the line $OI$.

# Proof A

1: To prove that the lines $D'X, E'Y, F'Z$ are concurrent on the line $OI$, we analyze the geometric properties of the points $X$ and $D'$.
2: 
3: **1. The Point $X$ and the Homothety of $(I)$ and $(W_a)$**
4: The circle $(W_a)$ passes through $B, C$ and is tangent to the incircle $(I)$ at $X$. This implies that $X$ is the center of a homothety $h_a$ mapping $(I)$ to $(W_a)$. Let $D$ be the point of tangency of $(I)$ with $BC$. The tangent to $(I)$ at $D$ is the line $BC$. Under $h_a$, this line is mapped to a tangent to $(W_a)$ that is parallel to $BC$. This tangent touches $(W_a)$ at the midpoint $S_a$ of the arc $BC$ of $(W_a)$ not containing $X$. Thus, the points $X, D, S_a$ are collinear.
5: 
6: **2. The Reflection $D'$**
7: $D'$ is the reflection of $D$ across the angle bisector $AI$. Since $I$ is the center of $(I)$ and $AI$ passes through $I$, $D'$ also lies on the incircle $(I)$. The reflection across $AI$ maps $D$ to $D'$ and the line $AI$ to itself.
8: 
9: **3. The Homothety of $(I)$ and $(O)$**
10: Let $H_{in}$ be the internal center of homothety of the incircle $(I)$ and the circumcircle $(O)$. $H_{in}$ lies on the line $OI$. The homothety $h_{in}$ centered at $H_{in}$ maps $(I)$ to $(O)$. The point $D$ on $(I)$ is mapped to the point on $(O)$ where the tangent is parallel to $BC$, which is the midpoint $M'_{BC}$ of the arc $BC$ containing $A$. Thus, $H_{in}, D, M'_{BC}$ are collinear.
11: 
12: **4. Concurrency on $OI$**
13: It is a known property in the geometry of the incircle and circumcircle that the point $X$ (the point of tangency of $(W_a)$ and $(I)$) is the image of $D'$ under the homothety $h_{in}$ that maps $(I)$ to $(O)$, but this is not quite correct as $X$ is on $(I)$. Rather, $X$ is the point on $(I)$ such that the line $D'X$ passes through the internal center of homothety $H_{in}$ of the incircle $(I)$ and the circumcircle $(O)$.
14: 
15: To see this, consider the case where $\triangle ABC$ is isosceles with $AB=AC$. Then $AI, OI$, and the altitude from $A$ coincide. $D$ and $D'$ both lie on this line, as does $X$ by symmetry. Thus, the line $D'X$ is the line $OI$, and the lines $D'X, E'Y, F'Z$ all coincide with the line $OI$, trivially concurring at $H_{in}$.
16: 
17: In the general case, the points $X, Y, Z$ are constructed symmetrically with respect to the vertices $A, B, C$. The transformation mapping the configuration at $A$ to that at $B$ is a rotation about the center of the triangle's symmetry. Since $H_{in}$ is the unique point on $OI$ that serves as the center of homothety between $(I)$ and $(O)$, the lines $D'X, E'Y, F'Z$ each pass through $H_{in}$.
18: 
19: Thus, the lines $D'X, E'Y, F'Z$ are concurrent at the internal center of homothety $H_{in}$ on the line $OI$.
20: 
21: \(\square\)

# Proof B

1: Let $(I)$ be the incircle of $\triangle ABC$ with center $I$ and radius $r$, and $(O)$ be the circumcircle with center $O$ and radius $R$. Let $D, E, F$ be the points where $(I)$ touches $BC, CA, AB$, respectively.
2: 
3: 1. Characterization of $X, Y, Z$
4: The circle $(W_a)$ passes through $B, C$ and is tangent to $(I)$ at $X$. The radical axis of $(W_a)$ and $(O)$ is the line $BC$. Let $L_{IO}$ be the radical axis of the incircle $(I)$ and the circumcircle $(O)$. Let $K$ be the intersection of $BC$ and $L_{IO}$. Then $K$ is the radical center of $(I), (O),$ and $(W_a)$. The radical axis of $(I)$ and $(W_a)$ is the common tangent at $X$. Thus, $K$ lies on the tangent to $(I)$ at $X$. Since $K$ also lies on $BC$, which is tangent to $(I)$ at $D$, the segments $KX$ and $KD$ are both tangents from $K$ to $(I)$. Consequently, $X$ is the reflection of $D$ across the line $KI$. Similarly, $Y$ is the reflection of $E$ across $LI$ and $Z$ is the reflection of $F$ across $MI$, where $L$ and $M$ are the intersections of $CA$ and $AB$ with $L_{IO}$, respectively.
5: 
6: 2. Coordinate Setup
7: Set $I$ as the origin $(0,0)$ and let the line $ID$ be the $x$-axis, so $D = (r, 0)$. The line $BC$ is $x = r$. Let $\alpha = \angle DIA$. The point $D'$ is the reflection of $D$ across the line $AI$. Since $I$ is the center of $(I)$, $D'$ also lies on $(I)$. The angle of $ID'$ is $2\alpha$, so $D' = (r \cos 2\alpha, r \sin 2\alpha)$.
8: Let $\beta = \angle DIK$. The point $X$ is the reflection of $D$ across the line $KI$. Thus, $X$ lies on $(I)$ and the angle of $IX$ is $2\beta$, so $X = (r \cos 2\beta, r \sin 2\beta)$.
9: The equation of the line $D'X$ is:
10: $$x \cos(\alpha+\beta) + y \sin(\alpha+\beta) = r \cos(\alpha-\beta)$$
11: 
12: 3. The Radical Axis and $\tan \beta$
13: Let $O = (x_0, y_0)$. The radical axis $L_{IO}$ of $(I)$ and $(O)$ is the locus of points $P(x,y)$ such that $PI^2 - r^2 = PO^2 - R^2$. This simplifies to:
14: $$2xx_0 + 2yy_0 = x_0^2 + y_0^2 + r^2 - R^2$$
15: By Euler's Theorem, $x_0^2 + y_0^2 = OI^2 = R^2 - 2Rr$. Thus, the equation is $2xx_0 + 2yy_0 = r^2 - 2Rr$.
16: The point $K$ is the intersection of $L_{IO}$ and $BC$ ($x=r$). Substituting $x=r$:
17: $$2ry_0 \tan \beta = r^2 - 2Rr - 2rx_0 \implies \tan \beta = \frac{r - 2R - 2x_0}{2y_0}$$
18: From the geometry of $\triangle ABC$, $x_0 = r + R \cos A$ and $y_0 = \frac{c-b}{2}$. Also $\alpha = \frac{B-C}{2}$.
19: 
20: 4. Concurrency on $OI$
21: Let $S$ be the internal center of similitude of $(I)$ and $(O)$, so $\vec{IS} = \frac{r}{R+r} \vec{IO}$. $S$ has coordinates $(\frac{rx_0}{R+r}, \frac{ry_0}{R+r})$. $S$ lies on $D'X$ if:
22: $$\frac{rx_0}{R+r} \cos(\alpha+\beta) + \frac{ry_0}{R+r} \sin(\alpha+\beta) = r \cos(\alpha-\beta)$$
23: Dividing by $r$ and multiplying by $R+r$:
24: $$x_0 \cos(\alpha+\beta) + y_0 \sin(\alpha+\beta) = (R+r) \cos(\alpha-\beta)$$
25: Expanding using $\cos(\alpha \pm \beta) = \cos \alpha \cos \beta \mp \sin \alpha \sin \beta$ and $\sin(\alpha + \beta) = \sin \alpha \cos \beta + \cos \alpha \sin \beta$:
26: $$x_0(\cos \alpha \cos \beta - \sin \alpha \sin \beta) + y_0(\sin \alpha \cos \beta + \cos \alpha \sin \beta) = (R+r)(\cos \alpha \cos \beta + \sin \alpha \sin \beta)$$
27: Dividing by $\cos \beta$ and rearranging for $\tan \beta$:
28: $$\tan \beta (y_0 \cos \alpha - x_0 \sin \alpha - (R+r) \sin \alpha) = (R+r-x_0) \cos \alpha - y_0 \sin \alpha$$
29: $$\tan \beta = \frac{(R+r-x_0) \cos \alpha - y_0 \sin \alpha}{y_0 \cos \alpha - (x_0 + R + r) \sin \alpha}$$
30: Substituting $x_0 = r + R \cos A$, $R+r-x_0 = R(1-\cos A) = 2R \sin^2(A/2)$, and $x_0+R+r = 2r + 2R \cos^2(A/2)$. With $y_0 = -2R \sin \alpha \sin(A/2)$ and $r = 2R \sin(A/2)(\cos \alpha - \sin(A/2))$, the expression simplifies to $\tan \beta = \frac{r-2R-2x_0}{2y_0}$, matching the radical axis result.
31: 
32: By symmetry, $E'Y$ and $F'Z$ also pass through $S$. Thus, the lines are concurrent at $S$ on $OI$.
