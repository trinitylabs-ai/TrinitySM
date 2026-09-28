# Problem

In $\triangle ABC$ the altitudes $BE$ and $CF$ intersect at $H$. A circle $(W)$ is
 externally tangent to the Euler circle $(E)$ of $\triangle ABC$ and also tangent
 to the sides $AB$ and $AC$ at $X$ and $Y$, respectively, with
 $(W)$ being closer to $A$ than the Euler circle. Let $I'$ be the
 incenter of $\triangle AEF$. Prove that $AXI'Y$ is a rhombus.

# Proof A

1: Let $\angle A = \alpha$. In $\triangle ABC$, let $BE$ and $CF$ be the altitudes. Since $\angle BFC = \angle BEC = 90^\circ$, the points $B, C, E, F$ are concyclic. Thus, $\angle AEF = \angle ABC$ and $\angle AFE = \angle ACB$. Consequently, $\triangle AEF \sim \triangle ABC$ with a similarity ratio $k = \frac{AE}{AB} = \cos \alpha$. For the points $E$ and $F$ to lie on the segments $AB$ and $AC$, we must have $\alpha < 90^\circ$.
2: 
3: Let $r$ be the inradius of $\triangle ABC$. The inradius of $\triangle AEF$ is $r_{AEF} = r \cos \alpha$. The distance from $A$ to the incenter $I'$ of $\triangle AEF$ is:
4: \[ AI' = \frac{r_{AEF}}{\sin(\alpha/2)} = \frac{r \cos \alpha}{\sin(\alpha/2)}. \]
5: The circle $(W)$ is tangent to $AB$ and $AC$ at $X$ and $Y$, so $AX = AY = r_W \cot(\alpha/2)$, where $r_W$ is the radius of $(W)$. Since $I'$ lies on the angle bisector of $\angle A$, the quadrilateral $AXI'Y$ is a kite. It is a rhombus if and only if $AX = XI'$. In $\triangle AXI'$, since $\angle XAI' = \alpha/2$, the condition $AX = XI'$ implies $\angle XI'A = \alpha/2$, which forces $\angle AXI' = 180^\circ - \alpha$. By the Law of Sines in $\triangle AXI'$:
6: \[ AX = \frac{AI' \sin(\alpha/2)}{\sin(180^\circ - \alpha)} = \frac{AI' \sin(\alpha/2)}{2 \sin(\alpha/2) \cos(\alpha/2)} = \frac{AI'}{2 \cos(\alpha/2)}. \]
7: Substituting the expressions for $AX$ and $AI'$:
8: \[ r_W \cot(\alpha/2) = \frac{r \cos \alpha}{2 \sin(\alpha/2) \cos(\alpha/2)} \implies r_W = \frac{r \cos \alpha}{2 \cos(\alpha/2) \cot(\alpha/2) \sin(\alpha/2)} = \frac{r \cos \alpha}{2 \cos^2(\alpha/2)} = \frac{r \cos \alpha}{1 + \cos \alpha}. \]
9: We now show that the circle $(W)$ described in the problem has this radius. Let $R$ be the circumradius of $\triangle ABC$. The Euler circle $(E)$ has radius $R_E = R/2$ and center $N$. By Feuerbach's Theorem, the incircle $(I)$ is internally tangent to $(E)$, so $NO_I = |R/2 - r|$. The circle $(W)$ is externally tangent to $(E)$, so $NO_W = R/2 + r_W$.
10: 
11: Let $A$ be the origin and the angle bisector of $\angle A$ be the x-axis. For any circle tangent to $AB$ and $AC$ with radius $\rho$, its center $O_\rho$ is at $AO_\rho = \rho/\sin(\alpha/2)$. Let $N = (d \cos \phi, d \sin \phi)$. Then:
12: \[ NO_\rho^2 = \left(d \cos \phi - \frac{\rho}{\sin(\alpha/2)}\right)^2 + (d \sin \phi)^2 = d^2 + \frac{\rho^2}{\sin^2(\alpha/2)} - \frac{2d\rho \cos \phi}{\sin(\alpha/2)}. \]
13: For $(W)$ and $(I)$, we have:
14: \[ (R/2 + r_W)^2 - (R/2 - r)^2 = \frac{r_W^2 - r^2}{\sin^2(\alpha/2)} - \frac{2d(r_W - r) \cos \phi}{\sin(\alpha/2)}. \]
15: Expanding the left side and dividing by $r_W - r$:
16: \[ \frac{R(r_W + r)}{r_W - r} + r_W + r = \frac{r_W + r}{\sin^2(\alpha/2)} - \frac{2d \cos \phi}{\sin(\alpha/2)}. \]
17: The circumcenter $O$ is at distance $R$ from $A$ at angle $\frac{B-C}{2}$ to the bisector, and the orthocenter $H$ is at distance $AH = 2R \cos \alpha$ at angle $\frac{C-B}{2}$. Since $N$ is the midpoint of $OH$:
18: \[ d \cos \phi = \frac{1}{2} \left( R \cos \frac{B-C}{2} + 2R \cos \alpha \cos \frac{C-B}{2} \right) = \frac{R}{2} \cos \frac{B-C}{2} (1 + 2 \cos \alpha). \]
19: Substituting $r_W = \frac{r \cos \alpha}{1 + \cos \alpha}$, we find $\frac{r_W + r}{r_W - r} = \frac{r \cos \alpha + r(1 + \cos \alpha)}{r \cos \alpha - r(1 + \cos \alpha)} = \frac{2 \cos \alpha + 1}{-1} = -(1 + 2 \cos \alpha)$. The equation becomes:
20: \[ -R(1 + 2 \cos \alpha) + r_W + r = \frac{r_W + r}{\sin^2(\alpha/2)} - \frac{2d \cos \phi}{\sin(\alpha/2)}. \]
21: Rearranging gives:
22: \[ -R(1 + 2 \cos \alpha) = (r_W + r) \cot^2(\alpha/2) - \frac{2d \cos \phi}{\sin(\alpha/2)}. \]
23: Using $r_W + r = \frac{r(1 + 2 \cos \alpha)}{1 + \cos \alpha}$ and $r = 4R \sin(\alpha/2) \sin(B/2) \sin(C/2)$:
24: \[ RHS = \frac{r(1 + 2 \cos \alpha)}{(1 + \cos \alpha)} \cot^2(\alpha/2) - \frac{R \cos \frac{B-C}{2} (1 + 2 \cos \alpha)}{\sin(\alpha/2)} = \frac{1 + 2 \cos \alpha}{\sin(\alpha/2)} \left[ \frac{r \cos^2(\alpha/2)}{(1 + \cos \alpha) \sin(\alpha/2)} - R \cos \frac{B-C}{2} \right]. \]
25: Since $1 + \cos \alpha = 2 \cos^2(\alpha/2)$, the term $\frac{r \cos^2(\alpha/2)}{(1 + \cos \alpha) \sin(\alpha/2)} = \frac{r}{2 \sin(\alpha/2)}$. Furthermore, $\frac{r}{2 \sin(\alpha/2)} = 2R \sin(B/2) \sin(C/2) = R(\cos \frac{B-C}{2} - \sin(\alpha/2))$. Thus:
26: \[ RHS = \frac{1 + 2 \cos \alpha}{\sin(\alpha/2)} \left[ R \cos \frac{B-C}{2} - R \sin(\alpha/2) - R \cos \frac{B-C}{2} \right] = -R(1 + 2 \cos \alpha). \]
27: The condition $NO_W = R/2 + r_W$ is satisfied. Since $(W)$ is closer to $A$ than the other circle tangent to $AB, AC$ and externally tangent to $(E)$, its radius must be the smaller root of the quadratic in $\rho$, which is $r_W = \frac{r \cos \alpha}{1 + \cos \alpha}$. Thus, $AXI'Y$ is a rhombus.

# Proof B

1: Let $R$ be the circumradius and $r$ be the inradius of $\triangle ABC$. Let $A, B, C$ denote the angles of the triangle. The Euler circle $(E)$ of $\triangle ABC$ has radius $R_E = R/2$ and its center $O_E$ is the midpoint of the segment $OH$, where $O$ is the circumcenter and $H$ is the orthocenter.
2: 
3: First, we determine the distance $AO_E$. Let $A$ be the origin and the angle bisector of $\angle A$ be the $x$-axis. The distance $AO = R$ and the distance $AH = 2R \cos A$. The angle between $AO$ and the bisector of $\angle A$ is $\frac{|B-C|}{2}$, and the angle between $AH$ and the bisector is also $\frac{|B-C|}{2}$, but they lie on opposite sides of the bisector. Thus, the coordinates are:
4: \[ O = \left( R \cos \frac{B-C}{2}, R \sin \frac{B-C}{2} \right), \quad H = \left( 2R \cos A \cos \frac{B-C}{2}, -2R \cos A \sin \frac{B-C}{2} \right) \]
5: The center $O_E$ is the midpoint of $OH$:
6: \[ O_E = \left( \frac{R(1 + 2 \cos A) \cos \frac{B-C}{2}}{2}, \frac{R(1 - 2 \cos A) \sin \frac{B-C}{2}}{2} \right) \]
7: The distance $AO_E^2$ is:
8: \[ AO_E^2 = \frac{R^2}{4} \left[ (1 + 2 \cos A)^2 \cos^2 \frac{B-C}{2} + (1 - 2 \cos A)^2 \sin^2 \frac{B-C}{2} \right] \]
9: \[ AO_E^2 = \frac{R^2}{4} \left[ 1 + 4 \cos^2 A + 4 \cos A (\cos^2 \frac{B-C}{2} - \sin^2 \frac{B-C}{2}) \right] = \frac{R^2}{4} [ 1 + 4 \cos^2 A + 4 \cos A \cos(B-C) ] \]
10: Using $\cos(B-C) = 2 \sin B \sin C - \cos A$, we have:
11: \[ AO_E^2 = \frac{R^2}{4} [ 1 + 4 \cos^2 A + 4 \cos A (2 \sin B \sin C - \cos A) ] = \frac{R^2}{4} + 2 R^2 \cos A \sin B \sin C \]
12: For the circle $(W)$ to be externally tangent to $(E)$ and closer to $A$ than $(E)$, $A$ must lie outside $(E)$, so $AO_E > R/2$. This implies $2 R^2 \cos A \sin B \sin C > 0$, which requires $\cos A > 0$. Thus, $\angle A$ must be acute.
13: 
14: In $\triangle AEF$, since $\angle AEB = \angle AFC = 90^\circ$, we have $AE = AB \cos A$ and $AF = AC \cos A$. Thus, $\triangle AEF \sim \triangle ABC$ with similarity ratio $\cos A$. The inradius of $\triangle AEF$ is $r' = r \cos A$. The distance from $A$ to the incenter $I'$ of $\triangle AEF$ is:
15: \[ AI' = \frac{r'}{\sin(A/2)} = \frac{r \cos A}{\sin(A/2)} \]
16: Let $r_W$ be the radius of circle $(W)$. Since $(W)$ is tangent to $AB$ and $AC$, its center $O_W$ lies on the bisector of $\angle A$, and $AO_W = \frac{r_W}{\sin(A/2)}$. The distance $AX = r_W \cot(A/2)$.
17: The condition for external tangency is $O_W O_E = r_W + R/2$. Let $x_E$ be the projection of $O_E$ onto the bisector of $\angle A$: $x_E = \frac{R(1 + 2 \cos A) \cos \frac{B-C}{2}}{2}$.
18: The tangency condition $(AO_W - x_E)^2 + y_E^2 = (r_W + R/2)^2$ simplifies to:
19: \[ AO_W^2 - 2 AO_W x_E + AO_E^2 = r_W^2 + r_W R + R^2/4 \]
20: Substituting $AO_W = \frac{r_W}{\sin(A/2)}$ and $AO_E^2 - R^2/4 = 2 R^2 \cos A \sin B \sin C$:
21: \[ r_W^2 \cot^2(A/2) - r_W \left( \frac{2 x_E}{\sin(A/2)} + R \right) + 2 R^2 \cos A \sin B \sin C = 0 \]
22: We verify that $r_{W1} = \frac{r \cos A}{1 + \cos A}$ is a root of this quadratic. Let $S = \sin(A/2)$, $C = \cos(A/2)$, and $k = \cos \frac{B-C}{2}$.
23: We have $r = 4R S \sin(B/2) \sin(C/2) = 2RS(k - S)$. Then $r_{W1} = \frac{2RS(k-S) \cos A}{2C^2} = \frac{RS(k-S) \cos A}{C^2}$.
24: The constant term is $c = 2 R^2 \cos A \sin B \sin C = R^2 \cos A (2k^2 - 1 + \cos A)$.
25: The linear coefficient is $b = \frac{R(1 + 2 \cos A) k}{S} + R = \frac{R}{S} [ (1 + 2 \cos A) k + S ]$.
26: Substituting $r_{W1}$ into the quadratic $a r_W^2 - b r_W + c = 0$ with $a = \cot^2(A/2)$:
27: \[ \frac{(k-S)^2 \cos A}{C^2} - \frac{(k-S) [(1 + 2 \cos A) k + S]}{C^2} + (2k^2 - 1 + \cos A) = 0 \]
28: Multiplying by $C^2$:
29: \[ (k-S)^2 \cos A - (k-S) [(1 + 2 \cos A) k + S] + C^2 (2k^2 - 1 + \cos A) = 0 \]
30: Expanding:
31: \[ (k^2 - 2kS + S^2) \cos A - [ (1 + 2 \cos A) k^2 + kS - (1 + 2 \cos A) kS - S^2 ] + C^2 (2k^2 - 1 + \cos A) \]
32: \[ = -k^2 (1 + \cos A) + S^2 (1 + \cos A) + C^2 (2k^2 - 1 + \cos A) \]
33: \[ = -2k^2 C^2 + 2S^2 C^2 + 2k^2 C^2 - C^2 + C^2 \cos A = C^2 [ 2S^2 - 1 + \cos A ] = 0 \]
34: Thus $r_{W1}$ is a root. To show it is the root corresponding to the circle closer to $A$, we show $r_{W1}$ is the smaller root by proving $r_{W1}^2 < c/a$.
35: \[ \frac{r_{W1}^2}{c/a} = \frac{r^2 \cos^2 A}{4 \cos^4(A/2)} \cdot \frac{1}{2 R^2 \cos A \sin B \sin C \tan^2(A/2)} = \frac{2 \sin^2(B/2) \sin^2(C/2) \cos A}{\cos^2(A/2) \sin B \sin C} \]
36: Using $\sin B = 2 \sin(B/2) \cos(B/2)$ and $\sin C = 2 \sin(C/2) \cos(C/2)$:
37: \[ \frac{r_{W1}^2}{c/a} = \frac{\tan(B/2) \tan(C/2) \cos A}{2 \cos^2(A/2)} = \frac{\tan(B/2) \tan(C/2) \cos A}{1 + \cos A} \]
38: Since $B/2 + C/2 = \pi/2 - A/2 < \pi/2$, we have $\tan(B/2) \tan(C/2) < 1$. Also $\frac{\cos A}{1 + \cos A} < 1$ for acute $A$. Thus $r_{W1}^2 < c/a$, and $r_{W1}$ is the smaller root.
39: Then:
40: \[ AX = r_{W1} \cot(A/2) = \frac{r \cos A}{2 \cos^2(A/2)} \frac{\cos(A/2)}{\sin(A/2)} = \frac{r \cos A}{\sin A} = r \cot A \]
41: For $AXI'Y$ to be a rhombus, we need $AX = AY = XI' = YI'$. We have $AX = AY$ as tangents from $A$. Since $I'$ lies on the angle bisector of $\angle A$, $XI' = YI'$. By the Law of Cosines in $\triangle AXI'$:
42: \[ XI'^2 = AX^2 + AI'^2 - 2 AX AI' \cos(A/2) \]
43: Substituting $AX = r \cot A$ and $AI' = \frac{r \cos A}{\sin(A/2)}$:
44: \[ XI'^2 = (r \cot A)^2 + \left( \frac{r \cos A}{\sin(A/2)} \right)^2 - 2 (r \cot A) \left( \frac{r \cos A}{\sin(A/2)} \right) \cos(A/2) \]
45: Using $\sin A = 2 \sin(A/2) \cos(A/2)$, the last term becomes:
46: \[ \frac{2 r \cos A}{\sin A} \frac{r \cos A \cos(A/2)}{\sin(A/2)} = \frac{2 r^2 \cos^2 A \cos(A/2)}{2 \sin(A/2) \cos(A/2) \sin(A/2)} = \frac{r^2 \cos^2 A}{\sin^2(A/2)} \]
47: Thus, $XI'^2 = r^2 \cot^2 A + \frac{r^2 \cos^2 A}{\sin^2(A/2)} - \frac{r^2 \cos^2 A}{\sin^2(A/2)} = r^2 \cot^2 A = AX^2$.
48: Hence $AX = AY = XI' = YI'$, and $AXI'Y$ is a rhombus.
