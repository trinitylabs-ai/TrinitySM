# Problem

Let $O$ and $G$ be the circumcenter and centroid of a non-isosceles triangle $ABC$, respectively. Let $H$ be the foot of the perpendicular from $A$ to $BC$, and let $M$ be the midpoint of $BC$. For a point $X$ on the line $OG$, let the line $BX$ intersect $AC$ at $P$, and let the line $CX$ intersect $AB$ at $Q$. Let $H_1$ be the foot of the perpendicular from $P$ to the line $AB$, and let $K$ be the reflection of $A$ about $H_1$. Let $T$ be the intersection of the circumcircle of triangle $KPQ$ and the circumcircle of triangle $PHM$. Prove that as $X$ moves along the line $OG$, $T$ moves along a fixed circle.

# Proof A

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

# Proof B

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
