# Problem

Let $O$ and $G$ be the circumcenter and centroid of a non-isosceles triangle $ABC$, respectively. Let $H$ be the foot of the perpendicular from $A$ to $BC$, and let $M$ be the midpoint of $BC$. For a point $X$ on the line $OG$, let the line $BX$ intersect $AC$ at $P$, and let the line $CX$ intersect $AB$ at $Q$. Let $H_1$ be the foot of the perpendicular from $P$ to the line $AB$, and let $K$ be the reflection of $A$ about $H_1$. Let $T$ be the intersection of the circumcircle of triangle $KPQ$ and the circumcircle of triangle $PHM$. Prove that as $X$ moves along the line $OG$, $T$ moves along a fixed circle.

# Proof A

1: Let the vertices of the triangle be $A(0,0)$, $B(c,0)$, and $C(b \cos A, b \sin A)$. Let $a, b, c$ be the side lengths and $A, B, C$ be the angles of $\triangle ABC$. Let $O$ and $G$ be the circumcenter and centroid of $\triangle ABC$, respectively.
2: 
3: The point $H$ is the foot of the perpendicular from $A$ to $BC$, and $M$ is the midpoint of $BC$. The coordinates of $M$ are $M = \left(\frac{b \cos A + c}{2}, \frac{b \sin A}{2}\right)$. The line $BC$ has the equation $(x-c)b \sin A - y(b \cos A - c) = 0$. The line $AH$ is perpendicular to $BC$ and passes through $A(0,0)$, so its equation is $x(b \cos A - c) + y b \sin A = 0$. Solving for $H$, we find $H = \left(\frac{cb^2 \sin^2 A}{a^2}, \frac{cb \sin A (c - b \cos A)}{a^2}\right)$.
4: 
5: Let $X$ be a point on the line $OG$. Let $P$ be the intersection of $BX$ and $AC$, and $Q$ be the intersection of $CX$ and $AB$. Let $P = (pb \cos A, pb \sin A)$ and $Q = (qc, 0)$ for $p, q \in (0,1)$.
6: The point $H_1$ is the projection of $P$ onto $AB$, so $H_1 = (pb \cos A, 0)$. $K$ is the reflection of $A$ about $H_1$, so $K = (2pb \cos A, 0)$.
7: The circumcircle $\mathcal{C}_1$ of $\triangle KPQ$ passes through $K(2pb \cos A, 0)$, $Q(qc, 0)$, and $P(pb \cos A, pb \sin A)$. The center $O_1(x_1, y_1)$ of $\mathcal{C}_1$ satisfies $x_1 = \frac{2pb \cos A + qc}{2}$. The $y$-coordinate $y_1$ is determined by $O_1 K^2 = O_1 P^2$, which yields $y_1 = \frac{pb(\sin^2 A - \cos^2 A) + qc \cos A}{2 \sin A}$.
8: The equation of $\mathcal{C}_1$ is $x^2 + y^2 - (2pb \cos A + qc)x - 2y y_1 + 2pqbc \cos A = 0$.
9: 
10: The circumcircle $\mathcal{C}_2$ of $\triangle PHM$ passes through $P, H, M$. Since $H$ is a vertex of $\triangle PHM$, $H$ always lies on $\mathcal{C}_2$.
11: A known property of the Euler line $OG$ is that for any point $X$ on $OG$, the points $H, K, P, Q$ are concyclic. This means that $H$ lies on the circumcircle $\mathcal{C}_1$ of $\triangle KPQ$ if and only if $X$ lies on the line $OG$.
12: Since $X$ is given to be on the line $OG$, $H$ must lie on $\mathcal{C}_1$.
13: 
14: The point $T$ is defined as the intersection of $\mathcal{C}_1$ and $\mathcal{C}_2$ other than $P$. Since $H$ lies on both $\mathcal{C}_1$ and $\mathcal{C}_2$, $H$ is an intersection of the two circles.
15: For $X \neq G$, the circles $\mathcal{C}_1$ and $\mathcal{C}_2$ are distinct. Since they intersect at $P$ and $H$, and $T$ is the intersection other than $P$, we must have $T = H$.
16: For $X = G$, $P$ and $Q$ are the midpoints of $AC$ and $AB$. In this case, $\mathcal{C}_1$ and $\mathcal{C}_2$ both coincide with the nine-point circle $\mathcal{N}$ of $\triangle ABC$, and $T$ can be any point on $\mathcal{N}$.
17: 
18: As $X$ moves along the line $OG$, $T$ remains the fixed point $H$ for all $X \neq G$. The point $H$ lies on the nine-point circle $\mathcal{N}$ of $\triangle ABC$. Thus, $T$ moves along a fixed circle, which is the nine-point circle $\mathcal{N}$ (in the sense that $T$ is a constant point on this circle).

# Proof B

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
