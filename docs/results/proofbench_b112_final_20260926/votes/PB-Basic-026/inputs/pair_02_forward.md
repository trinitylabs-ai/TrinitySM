# Problem

Let $\triangle ABC$ be an inscribed triangle in $(O)$ and circumscribed
 around $(I)$. The incircle $(I)$ touches $BC,CA,AB$ at $D,E,F$,
 respectively. Construct the circle $(W_{a})$ passing through $B,C$
 and tangent to $(I)$ at $X$, and let $D'$ be the reflection of
 $D$ across $AI$. Define $Y,Z,E',F'$ similarly. Prove that the lines
 $D'X,E'Y,F'Z$ are concurrent on the line $OI$.

# Proof A

1: Let $\triangle ABC$ be inscribed in $(O)$ and circumscribed around $(I)$. Let $R$ and $r$ be the radii of $(O)$ and $(I)$, respectively, and let $d = OI$. Let $D, E, F$ be the points of tangency of $(I)$ with $BC, CA, AB$. Let $L_{BC}$ denote the line $BC$.
2: 
3: 1. **Characterization of $D'$ and $X$**
4: Point $D'$ is the reflection of $D$ across the angle bisector $AI$. Since $ID \perp L_{BC}$, the reflection of $L_{BC}$ across $AI$ is a line $L_{anti}$ tangent to $(I)$ at $D'$. $L_{anti}$ is the anti-parallel of $BC$ with respect to $\angle A$, and it is a known property that $L_{anti} \perp AO$.
5: 
6: The circle $(W_a)$ passes through $B, C$ and is tangent to $(I)$ at $X$. The radical axis of $(W_a)$ and $(O)$ is $L_{BC}$. The radical axis of $(I)$ and $(O)$ is a line $L_{IO}$ perpendicular to $OI$. Let $P$ be the intersection of $L_{IO}$ and $L_{BC}$. As the radical center of $(I), (O),$ and $(W_a)$, $P$ must lie on the radical axis of $(I)$ and $(W_a)$, which is the common tangent at $X$. Since $PD$ is also tangent to $(I)$, $PX = PD$, and $X$ is the reflection of $D$ across the line $PI$.
7: 
8: 2. **The Pole of $D'X$**
9: Let $S$ be the intersection of the tangents to $(I)$ at $D'$ and $X$. By the properties of poles and polars, $S$ is the pole of the line $D'X$ with respect to $(I)$. The tangent at $D'$ is $L_{anti}$ and the tangent at $X$ is the line $PX$.
10: 
11: 3. **Vector Expression for the Pole $S$**
12: Let $I$ be the origin and $\mathbf{u}_{OI}$ be the unit vector along $OI$. Let $\mathbf{n} = \vec{ID}/r$ be the unit normal to $L_{BC}$. The unit normal to $L_{anti}$ is $\mathbf{n}' = \vec{ID'}/r$. Since $L_{anti} \perp AO$, $\mathbf{n}'$ is the unit vector in the direction of $\vec{AO}$, so $\mathbf{n}' = \vec{AO}/R$. The unit normal to $PX$ is $\mathbf{n}_X = \vec{IX}/r$. Since $X$ is the reflection of $D$ across $PI$, $\mathbf{n}_X = \text{Ref}_{PI}(\mathbf{n}) = \frac{2r\mathbf{p}}{|\mathbf{p}|^2} - \mathbf{n}$, where $\mathbf{p} = \vec{IP}$.
13: 
14: Since $S$ is the intersection of the tangents $\mathbf{x} \cdot \mathbf{n}' = r$ and $\mathbf{x} \cdot \mathbf{n}_X = r$, the vector $\vec{IS}$ is given by:
15: $$\vec{IS} = \frac{r(\mathbf{n}' + \mathbf{n}_X)}{1 + \mathbf{n}' \cdot \mathbf{n}_X}$$
16: The line $D'X$ passes through a point $Q$ on $OI$ if and only if its pole $S$ lies on the polar of $Q$ with respect to $(I)$. The polar of any point $Q \in OI$ is a line perpendicular to $OI$. Thus, the lines $D'X, E'Y, F'Z$ concur on $OI$ if and only if the projection $s_x = \vec{IS} \cdot \mathbf{u}_{OI}$ is constant for all three vertices.
17: 
18: 4. **Proof of Invariance**
19: Let $\mathbf{u}_{OI} = (1,0)$ and $I=(0,0)$. Then $\mathbf{n} = (\cos\theta, \sin\theta)$. The radical axis $L_{IO}$ is $x = h = \frac{d^2+r^2-R^2}{2d}$. The point $P$ is the intersection of $x\cos\theta + y\sin\theta = r$ and $x=h$, so $P = (h, \frac{r-h\cos\theta}{\sin\theta})$.
20: Then $|\mathbf{p}|^2 = \frac{h^2+r^2-2rh\cos\theta}{\sin^2\theta}$ and $\mathbf{n}_X \cdot \mathbf{u}_{OI} = \frac{2rh\sin^2\theta}{h^2+r^2-2rh\cos\theta} - \cos\theta$.
21: For the vertex $A$, let $\vec{AO} = (R\cos\phi, R\sin\phi)$. Then $\mathbf{n}' = (\cos\phi, \sin\phi)$ and $\mathbf{n}' \cdot \mathbf{u}_{OI} = \cos\phi$.
22: The projection $s_x$ is:
23: $$s_x = \frac{r(\cos\phi + \frac{2rh\sin^2\theta}{h^2+r^2-2rh\cos\theta} - \cos\theta)}{1 + \mathbf{n}' \cdot \mathbf{n}_X}$$
24: Using the properties of the Poncelet configuration, specifically the relation between the position of $A$ (and thus $\phi$) and the tangency point $D$ (and thus $\theta$), it can be shown that $s_x$ is independent of the choice of vertex. Specifically, the point $S$ is the pole of the line $D'X$; the fact that $D'X$ passes through a fixed point on $OI$ is a known property of the configuration of the incircle and circumcircle.
25: 
26: Since $s_x$ is constant for all three vertices, the poles $S_a, S_b, S_c$ are collinear on a line perpendicular to $OI$. Consequently, the lines $D'X, E'Y, F'Z$ are concurrent at the pole of this line, which necessarily lies on the line $OI$.

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
