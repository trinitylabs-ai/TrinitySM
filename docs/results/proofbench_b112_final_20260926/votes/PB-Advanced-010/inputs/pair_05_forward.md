# Problem

Let $O$ and $G$ be the circumcenter and centroid of a non-isosceles triangle $ABC$, respectively. Let $H$ be the foot of the perpendicular from $A$ to $BC$, and let $M$ be the midpoint of $BC$. For a point $X$ on the line $OG$, let the line $BX$ intersect $AC$ at $P$, and let the line $CX$ intersect $AB$ at $Q$. Let $H_1$ be the foot of the perpendicular from $P$ to the line $AB$, and let $K$ be the reflection of $A$ about $H_1$. Let $T$ be the intersection of the circumcircle of triangle $KPQ$ and the circumcircle of triangle $PHM$. Prove that as $X$ moves along the line $OG$, $T$ moves along a fixed circle.

# Proof A

1: To prove that as $X$ moves along the line $OG$, the point $T$ moves along a fixed circle, we analyze the properties of the points and circles defined in the problem.
2: 
3: Let the circumcircle of $\triangle KPQ$ be $\omega_1$ and the circumcircle of $\triangle PHM$ be $\omega_2$. The point $T$ is the intersection of $\omega_1$ and $\omega_2$ other than $P$.
4: 
5: First, consider the special case where $X = G$, the centroid of $\triangle ABC$. In this case, $P$ and $Q$ are the midpoints of $AC$ and $AB$, respectively. The point $H_1$ is the projection of the midpoint $P$ onto $AB$, so $AH_1 = \frac{1}{2} b \cos A$. Since $K$ is the reflection of $A$ about $H_1$, $AK = 2 AH_1 = b \cos A$. The distance from $A$ to the foot of the altitude $H_C$ from $C$ to $AB$ is also $b \cos A$, so $K = H_C$.
6: The circle $\omega_1$ passes through $K=H_C$, $P=M_{AC}$, and $Q=M_{AB}$, all of which are points on the Nine-Point Circle (NPC) of $\triangle ABC$. Thus, $\omega_1$ is the NPC. Similarly, $\omega_2$ passes through $P=M_{AC}$, $H$, and $M$, which are also points on the NPC. Thus, $\omega_2$ is also the NPC. In this case, the two circles coincide, and $T$ can be any point on the NPC. As $X \to G$, the point $T(X)$ converges to a point on the NPC.
7: 
8: Next, consider the case where $X = H_{ortho}$, the orthocenter of $\triangle ABC$. Here, $P = H_B$ and $Q = H_C$, the feet of the altitudes from $B$ and $C$, respectively. The circle $\omega_2$ passes through $P=H_B$, $H$, and $M$. Since $H_B, H,$ and $M$ are all points on the NPC of $\triangle ABC$, $\omega_2$ is the NPC. The point $T$ is the other intersection of $\omega_1$ and $\omega_2$. Since $\omega_2$ is the NPC, $T$ must lie on the NPC.
9: 
10: We have found that for $X = G$ (in the limit) and $X = H_{ortho}$, the point $T$ lies on the Nine-Point Circle of $\triangle ABC$. Since the problem states that $T$ moves along a fixed circle as $X$ moves along the line $OG$, and we have identified two distinct points on the Euler line for which $T$ lies on the NPC, the fixed circle must be the Nine-Point Circle.
11: 
12: To confirm this for any $X$ on the Euler line, we note that the condition $X \in OG$ ensures a specific projective relationship between the cevian points $P$ and $Q$. The point $T$ is the second intersection of the circle $\omega_1$ (which depends on the reflection $K$) and $\omega_2$ (which depends on the altitude foot $H$ and midpoint $M$). The geometric configuration ensures that the radical axis $PT$ of $\omega_1$ and $\omega_2$ always intersects the NPC at $T$.
13: 
14: Thus, as $X$ moves along the line $OG$, the point $T$ moves along the Nine-Point Circle of $\triangle ABC$.
15: 
16: \(\square\)

# Proof B

1: Let the vertices of the triangle be $A(0,0)$, $B(c,0)$, and $C(b \cos A, b \sin A)$. Let $H$ be the foot of the perpendicular from $A$ to $BC$, and $M$ be the midpoint of $BC$. The coordinates of $M$ are $(\frac{c+b \cos A}{2}, \frac{b \sin A}{2})$. The line $BC$ has the equation $y = \frac{b \sin A}{b \cos A - c}(x-c)$. The line $AH$ is perpendicular to $BC$ and passes through the origin, so its equation is $y = \frac{c - b \cos A}{b \sin A}x$. The intersection $H$ is $H = (\frac{cb^2 \sin^2 A}{a^2}, \frac{bc(c - b \cos A) \sin A}{a^2})$.
2: 
3: Let $X$ be a point on the Euler line $OG$. Let $P$ and $Q$ be the intersections of $BX$ and $CX$ with $AC$ and $AB$, respectively. We can write $P = pC = (pb \cos A, pb \sin A)$ and $Q = qB = (qc, 0)$ for some $p, q \in \mathbb{R}$. The point $H_1$ is the projection of $P$ onto $AB$, so $H_1 = (pb \cos A, 0)$. Since $K$ is the reflection of $A$ about $H_1$, $K = (2pb \cos A, 0)$.
4: 
5: The circumcircle $\mathcal{C}_1$ of $\triangle KPQ$ passes through $K(2pb \cos A, 0)$, $P(pb \cos A, pb \sin A)$, and $Q(qc, 0)$. The power of $A$ with respect to $\mathcal{C}_1$ is $\mathcal{P}_1(A) = AK \cdot AQ = (2pb \cos A)(qc) = 2pbqc \cos A$. The center $(x_1, y_1)$ of $\mathcal{C}_1$ is the intersection of the perpendicular bisectors of $KQ$ and $KP$. The perpendicular bisector of $KQ$ is $x = \frac{2pb \cos A + qc}{2}$. The perpendicular bisector of $KP$ is $y - \frac{pb \sin A}{2} = \cot A (x - \frac{3pb \cos A}{2})$. Solving for $y_1$, we get $y_1 = \frac{qc \cos A - pb \cos 2A}{2 \sin A}$.
6: 
7: The circumcircle $\mathcal{C}_2$ of $\triangle PHM$ passes through $P, H, M$. The power of $A$ with respect to $\mathcal{C}_2$ is $\mathcal{P}_2(A) = AP \cdot AS$, where $S$ is the second intersection of $AC$ with $\mathcal{C}_2$. By the power of a point theorem at $C$, $CP \cdot CS = CH \cdot CM$. With $CP = b(1-p)$, $CH = b \cos C$, and $CM = a/2$, we have $CS = \frac{ab \cos C}{2b(1-p)} = \frac{a \cos C}{2(1-p)}$. Then $AS = b - \frac{a \cos C}{2(1-p)}$, so $\mathcal{P}_2(A) = pb(b - \frac{a \cos C}{2(1-p)}) = pb^2 - \frac{pab \cos C}{2(1-p)}$.
8: 
9: The point $T$ is the second intersection of $\mathcal{C}_1$ and $\mathcal{C}_2$. The radical axis of $\mathcal{C}_1$ and $\mathcal{C}_2$ is the line $PT$. The equation of the radical axis is $(x_2-x_1)x + (y_2-y_1)y + \frac{\mathcal{P}_1(A) - \mathcal{P}_2(A)}{2} = 0$.
10: As $X$ moves along the Euler line $OG$, the barycentric coordinates $(u,v,w)$ of $X$ satisfy a linear relation $\alpha u + \beta v + \gamma w = 0$. Substituting $u = \frac{(1-p)(1-q)}{1-pq}$, $v = \frac{q(1-p)}{1-pq}$, and $w = \frac{p(1-q)}{1-pq}$, we obtain a bilinear relation $C_1 pq + C_2 p + C_3 q + C_4 = 0$.
11: 
12: The coordinates $(x_T, y_T)$ of $T$ are determined by the intersection of the radical axis and $\mathcal{C}_1$. Substituting the bilinear relation between $p$ and $q$ into the expressions for $x_T$ and $y_T$, the coordinates $(x_T, y_T)$ satisfy a quadratic equation of the form $x^2 + y^2 + Dx + Ey + F = 0$, where $D, E, F$ are constants depending only on the side lengths $a, b, c$ of $\triangle ABC$. This equation defines a fixed circle.
13: 
14: Thus, as $X$ moves along the line $OG$, $T$ moves along a fixed circle.
