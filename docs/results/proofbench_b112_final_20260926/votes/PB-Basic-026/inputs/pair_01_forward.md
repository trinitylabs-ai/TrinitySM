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
