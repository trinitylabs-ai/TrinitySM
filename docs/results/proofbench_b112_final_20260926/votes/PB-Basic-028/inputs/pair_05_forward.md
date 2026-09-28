# Problem

In $\triangle ABC$ the altitudes $BE$ and $CF$ intersect at $H$. A circle $(W)$ is
 externally tangent to the Euler circle $(E)$ of $\triangle ABC$ and also tangent
 to the sides $AB$ and $AC$ at $X$ and $Y$, respectively, with
 $(W)$ being closer to $A$ than the Euler circle. Let $I'$ be the
 incenter of $\triangle AEF$. Prove that $AXI'Y$ is a rhombus.

# Proof A

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

# Proof B

1: To prove that $AXI'Y$ is a rhombus, we first establish the necessary and sufficient conditions for this property. Since the circle $(W)$ is tangent to $AB$ at $X$ and to $AC$ at $Y$, we have $AX = AY$. The point $I'$ is the incenter of $\triangle AEF$, and since $E$ and $F$ lie on $AB$ and $AC$ respectively, $I'$ must lie on the angle bisector of $\angle A$. For $AXI'Y$ to be a rhombus, we must have $AX = XI' = YI'$. In $\triangle AXI'$, $\angle XAI' = A/2$. For $AX = XI'$, the triangle must be isosceles with $\angle AI'X = A/2$, which implies $\angle AXI' = 180^\circ - A$. By the Law of Sines in $\triangle AXI'$:
2: \[ \frac{AX}{\sin(A/2)} = \frac{AI'}{\sin(180^\circ - A)} = \frac{AI'}{\sin A} \implies AX = \frac{AI' \sin(A/2)}{2 \sin(A/2) \cos(A/2)} = \frac{AI'}{2 \cos(A/2)} \]
3: Thus, $AXI'Y$ is a rhombus if and only if $AI' = 2 AX \cos(A/2)$.
4: 
5: Let $R$ be the circumradius of $\triangle ABC$. The feet of the altitudes $E$ and $F$ define $\triangle AEF$, which is similar to $\triangle ABC$ with a ratio of $k = |\cos A|$. The distance from $A$ to the incenter $I$ of $\triangle ABC$ is $AI = 4R \sin(B/2) \sin(C/2)$. Thus, the distance to the incenter $I'$ of $\triangle AEF$ is:
6: \[ AI' = |\cos A| \cdot AI = 4R |\cos A| \sin(B/2) \sin(C/2) \]
7: If $\angle A$ is acute, the target length for $AX$ to form a rhombus is $x_0 = \frac{2R \cos A \sin(B/2) \sin(C/2)}{\cos(A/2)}$.
8: 
9: Now we determine the actual length $AX$ using the tangency of $(W)$. Let $r_W$ be the radius of $(W)$. Then $AX = r_W \cot(A/2)$. Let $O_W$ be the center of $(W)$ and $O_E$ be the center of the Euler circle $(E)$. The radius of $(E)$ is $R_E = R/2$. The center $O_E$ is the midpoint of $OH$, where $O$ is the circumcenter and $H$ is the orthocenter. Using vectors from $O$, $\vec{OH} = \vec{OA} + \vec{OB} + \vec{OC}$, so $\vec{AO_E} = \frac{1}{2}(\vec{OB} + \vec{OC} - \vec{OA})$. Then
10: \[ AO_E^2 = \frac{1}{4} |\vec{OB} + \vec{OC} - \vec{OA}|^2 = \frac{R^2}{4} (3 + 2\cos 2A - 2\cos 2B - 2\cos 2C) \]
11: Using $\cos 2B + \cos 2C = -2 \cos A \cos(B-C)$ and $\cos 2A = 2\cos^2 A - 1$, we have:
12: \[ AO_E^2 = \frac{R^2}{4}(1 + 4 \cos^2 A + 4 \cos A \cos(B-C)) \]
13: The projection of $\vec{AO_E}$ onto the angle bisector $\vec{u}$ is $d = \vec{AO_E} \cdot \vec{u} = \frac{1}{2}(\vec{OB} + \vec{OC} - \vec{OA}) \cdot \vec{u}$. Since $\vec{OB} \cdot \vec{u} = c \cos(A/2) - R \cos \frac{B-C}{2}$, $\vec{OC} \cdot \vec{u} = b \cos(A/2) - R \cos \frac{B-C}{2}$, and $\vec{OA} \cdot \vec{u} = -R \cos \frac{B-C}{2}$, we have:
14: \[ d = \frac{1}{2}( (b+c)\cos(A/2) - R \cos \frac{B-C}{2} ) = \frac{R}{2}(1 + 2 \cos A) \cos \frac{B-C}{2} \]
15: where we used $b+c = 4R \cos(A/2) \cos \frac{B-C}{2}$.
16: 
17: Since $(W)$ is externally tangent to $(E)$, $O_W O_E = r_W + R/2$. Using the Law of Cosines in $\triangle AO_W O_E$ with $AO_W = r_W / \sin(A/2)$:
18: \[ (r_W + R/2)^2 = AO_E^2 + \left(\frac{r_W}{\sin(A/2)}\right)^2 - 2 \frac{r_W}{\sin(A/2)} d \]
19: Substituting $x = AX = r_W \cot(A/2)$, we obtain the quadratic equation:
20: \[ x^2 - \left( R \tan(A/2) + \frac{2d}{\cos(A/2)} \right) x + R^2 (\cos^2 A + \cos A \cos(B-C)) = 0 \]
21: The roots of this quadratic are $x_0 = \frac{2R \cos A \sin(B/2) \sin(C/2)}{\cos(A/2)}$ and $x_1 = 4 R \cos(A/2) \cos(B/2) \cos(C/2)$.
22: 
23: We now show that the condition that $(W)$ is closer to $A$ than $(E)$ (meaning $AO_W < AO_E$) implies $\angle A$ is acute. If $\angle A \ge 90^\circ$, then $\cos A \le 0$, so $x_0 \le 0$. The only positive root for $AX$ is $x_1$. In this case:
24: \[ AO_W = \frac{x_1}{\cos(A/2)} = 4R \cos(B/2) \cos(C/2) = 2R \left( \cos \frac{B-C}{2} + \cos \frac{B+C}{2} \right) \]
25: Since $B+C = 180^\circ - A \le 90^\circ$, we have $\cos \frac{B+C}{2} \ge \cos 45^\circ = \frac{\sqrt{2}}{2}$. Because $\cos \frac{B-C}{2} > 0$, it follows that $AO_W > \sqrt{2}R$.
26: Conversely, for $\angle A \ge 90^\circ$, we have $\cos A \le 0$ and $\cos(B-C) > 0$, so $4 \cos A \cos(B-C) \le 0$. Thus:
27: \[ AO_E^2 = \frac{R^2}{4}(1 + 4 \cos^2 A + 4 \cos A \cos(B-C)) \le \frac{R^2}{4}(1 + 4 \cos^2 A) \le \frac{5R^2}{4} \]
28: which implies $AO_E \le \frac{\sqrt{5}}{2}R$. Since $\sqrt{2} \approx 1.414$ and $\frac{\sqrt{5}}{2} \approx 1.118$, we have $AO_W > AO_E$, contradicting the problem statement. Therefore, $\angle A$ must be acute.
29: 
30: For $\angle A < 90^\circ$, both $x_0$ and $x_1$ are positive. The condition $AO_W < AO_E$ is satisfied by the smaller root $x = x_0$. Thus, $AX = x_0 = \frac{2R \cos A \sin(B/2) \sin(C/2)}{\cos(A/2)}$. Consequently, we have:
31: \[ AX = \frac{4R \cos A \sin(B/2) \sin(C/2)}{2 \cos(A/2)} = \frac{AI'}{2 \cos(A/2)} \]
32: which is precisely the condition for $AXI'Y$ to be a rhombus. \(\square\)
