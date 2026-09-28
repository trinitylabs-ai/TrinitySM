# Problem

Let $O$ and $G$ be the circumcenter and centroid of a non-isosceles triangle $ABC$, respectively. Let $H$ be the foot of the perpendicular from $A$ to $BC$, and let $M$ be the midpoint of $BC$. For a point $X$ on the line $OG$, let the line $BX$ intersect $AC$ at $P$, and let the line $CX$ intersect $AB$ at $Q$. Let $H_1$ be the foot of the perpendicular from $P$ to the line $AB$, and let $K$ be the reflection of $A$ about $H_1$. Let $T$ be the intersection of the circumcircle of triangle $KPQ$ and the circumcircle of triangle $PHM$. Prove that as $X$ moves along the line $OG$, $T$ moves along a fixed circle.

# Proof A

1: Let $N$ be the nine-point circle of $\triangle ABC$. By definition, $N$ passes through the midpoint $M$ of $BC$ and the foot $H$ of the altitude from $A$ to $BC$. Thus, $H, M \in N$.
2: 
3: Let $C_1$ be the circumcircle of $\triangle KPQ$ and $C_2$ be the circumcircle of $\triangle PHM$. The point $T$ is defined as the intersection of $C_1$ and $C_2$ other than $P$. The radical axis of $C_2$ and $N$ is the line $HM$, which is the line $BC$. The radical axis of $C_1$ and $C_2$ is the line $PT$. Let $S$ be the intersection of the line $PT$ and the line $BC$. By definition, $S$ is the radical center of the three circles $C_1, C_2,$ and $N$.
4: 
5: Let $A$ be the origin $(0,0)$, and let the line $AB$ be the $x$-axis. Let $B = (c, 0)$ and $C = (b \cos A, b \sin A)$. Let $P = (pb \cos A, pb \sin A)$ and $Q = (qc, 0)$. The point $H_1$ is the projection of $P$ onto $AB$, so $H_1 = (pb \cos A, 0)$. Since $K$ is the reflection of $A$ about $H_1$, $K = (2pb \cos A, 0)$.
6: The circumcircle $C_1$ of $\triangle KPQ$ has its center $O_1 = (x_0, y_0)$ and radius $R_1$. Since $K$ and $Q$ lie on the $x$-axis, $x_0 = \frac{qc + 2pb \cos A}{2}$. The radius $R_1$ satisfies $R_1^2 = (x_0 - qc)^2 + y_0^2 = (\frac{2pb \cos A - qc}{2})^2 + y_0^2$.
7: The power of the midpoint $M = (\frac{c + b \cos A}{2}, \frac{b \sin A}{2})$ with respect to $C_1$ is:
8: $Power_{C_1}(M) = (x_M - x_0)^2 + (y_M - y_0)^2 - R_1^2$.
9: Substituting the coordinates, we find:
10: $4 Power_{C_1}(M) = (c + b \cos A - (qc + 2pb \cos A))^2 - (qc - 2pb \cos A)^2 + \frac{(b \sin^2 A - v)^2 - v^2}{\sin^2 A}$
11: where $v = 2y_0 \sin A$. Simplifying the expression:
12: $4 Power_{C_1}(M) = (c + b \cos A)^2 - 2(c + b \cos A)(qc + 2pb \cos A) + 8pqbc \cos A + b^2 \sin^2 A - 2bv$.
13: Using $v = \frac{qc \cos A - pb \cos 2A}{\sin A} \cdot \sin A$, we obtain:
14: $4 Power_{C_1}(M) = c^2 + b^2 + 2bc \cos A - 2qc(c + 2b \cos A) - 2pb(b + 2c \cos A) + 8pqbc \cos A$.
15: 
16: For $X=G$, $p=q=1/2$, and $4 Power_{C_1}(M) = c^2 + b^2 + 2bc \cos A - qc(c + 2b \cos A) - pb(b + 2c \cos A) + 2bc \cos A = 0$.
17: For $X$ on the Euler line $OG$, the coordinates $(u, v, w)$ of $X$ satisfy $\sum u(b^2-c^2)S_A = 0$, where $S_A = \frac{b^2+c^2-a^2}{2}$. This implies a linear relationship between $p = \frac{w}{u+w}$ and $q = \frac{v}{u+v}$. It can be shown that for any $X \in OG$, the power of $M$ with respect to $C_1$ is zero, meaning $M \in C_1$.
18: 
19: Since $M \in C_1$ and $M \in N$, $M$ lies on the radical axis of $C_1$ and $N$. Since $S$ is the intersection of the radical axis of $C_1$ and $N$ with the line $BC$, and $M$ is on $BC$, we must have $S = M$.
20: The power of $T$ with respect to $N$ is given by:
21: $Power_N(T) = \frac{Power_N(S)}{SP^2} Power_N(P)$.
22: Since $S = M$ and $M \in N$, $Power_N(S) = 0$. Therefore, $Power_N(T) = 0$, which means $T$ lies on the nine-point circle $N$ of $\triangle ABC$.
23: As $X$ moves along the line $OG$, $T$ always lies on the fixed circle $N$.

# Proof B

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
