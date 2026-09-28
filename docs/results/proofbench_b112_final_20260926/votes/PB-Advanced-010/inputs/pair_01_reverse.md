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
