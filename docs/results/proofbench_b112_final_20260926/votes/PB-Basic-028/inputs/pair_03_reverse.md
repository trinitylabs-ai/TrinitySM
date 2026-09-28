# Problem

In $\triangle ABC$ the altitudes $BE$ and $CF$ intersect at $H$. A circle $(W)$ is
 externally tangent to the Euler circle $(E)$ of $\triangle ABC$ and also tangent
 to the sides $AB$ and $AC$ at $X$ and $Y$, respectively, with
 $(W)$ being closer to $A$ than the Euler circle. Let $I'$ be the
 incenter of $\triangle AEF$. Prove that $AXI'Y$ is a rhombus.

# Proof A

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

# Proof B

1: Let $\angle A = 2\alpha$. Since the circle $(W)$ is tangent to the sides $AB$ and $AC$ at $X$ and $Y$, we have $AX = AY$. The center $O_W$ of $(W)$ lies on the internal angle bisector of $\angle A$, and the distance $AX$ is given by $AX = r_W \cot \alpha$, where $r_W$ is the radius of $(W)$. The incenter $I'$ of $\triangle AEF$ also lies on the angle bisector of $\angle A$. The quadrilateral $AXI'Y$ is a rhombus if and only if $AX = AY = XI' = I'Y$, which occurs if and only if $AI' = 2 AX \cos \alpha$. Substituting $AX$:
2: \[ AI' = 2 r_W \cot \alpha \cos \alpha = \frac{2 r_W \cos^2 \alpha}{\sin \alpha}. \]
3: In $\triangle ABE$ and $\triangle ACF$, since $\angle E = \angle F = 90^\circ$, we have $AE = AB \cos A$ and $AF = AC \cos A$. Thus, $\triangle AEF$ is similar to $\triangle ABC$ with a ratio of similarity $\cos A$. The inradius $r'$ of $\triangle AEF$ is therefore $r' = r \cos A$, where $r$ is the inradius of $\triangle ABC$. The distance from vertex $A$ to the incenter $I'$ is $AI' = \frac{r'}{\sin \alpha} = \frac{r \cos A}{\sin \alpha}$. Equating the two expressions for $AI'$:
4: \[ \frac{r \cos A}{\sin \alpha} = \frac{2 r_W \cos^2 \alpha}{\sin \alpha} \implies r_W = \frac{r \cos A}{2 \cos^2 \alpha} = \frac{r \cos A}{1 + \cos A}. \]
5: Next, we determine $r_W$ from the condition that $(W)$ is externally tangent to the Euler circle $(E)$. Let $R$ be the circumradius of $\triangle ABC$. The Euler circle $(E)$ has radius $R_E = R/2$ and center $O_E$. The external tangency condition is $O_W O_E = r_W + R/2$. Let $A$ be the origin and the angle bisector of $\angle A$ be the $x$-axis. Then $O_W = (\frac{r_W}{\sin \alpha}, 0)$. The center $O_E$ is the midpoint of the circumcenter $O$ and the orthocenter $H$, so $\vec{AO_E} = \frac{1}{2}(\vec{AO} + \vec{AH})$.
6: The distance $AO_E^2$ is given by:
7: \[ AO_E^2 = \frac{1}{4}(AO^2 + AH^2 + 2 \vec{AO} \cdot \vec{AH}) = \frac{1}{4}(R^2 + 4R^2 \cos^2 A + 4R^2 \cos A \cos(B-C)). \]
8: The projection of $\vec{AO_E}$ onto the angle bisector is:
9: \[ \vec{AO_E} \cdot \vec{u}_{bisector} = \frac{1}{2}(\vec{AO} \cdot \vec{u}_{bisector} + \vec{AH} \cdot \vec{u}_{bisector}) = \frac{1}{2}(R \cos \frac{B-C}{2} + 2R \cos A \cos \frac{B-C}{2}) = \frac{R}{2}(1 + 2 \cos A) \cos \frac{B-C}{2}. \]
10: Using the Law of Cosines in $\triangle AO_W O_E$:
11: \[ O_W O_E^2 = AO_W^2 + AO_E^2 - 2 AO_W (\vec{AO_E} \cdot \vec{u}_{bisector}). \]
12: Substituting the known values and the tangency condition $O_W O_E^2 = (r_W + R/2)^2$:
13: \[ (r_W + R/2)^2 = \frac{r_W^2}{\sin^2 \alpha} + \frac{R^2}{4}(1 + 4 \cos^2 A + 4 \cos A \cos(B-C)) - \frac{r_W R (1 + 2 \cos A) \cos \frac{B-C}{2}}{\sin \alpha}. \]
14: Expanding and simplifying, we obtain a quadratic equation for $r_W$:
15: \[ r_W^2 \cot^2 \alpha - r_W R \left(1 + \frac{(1 + 2 \cos A) \cos \frac{B-C}{2}}{\sin \alpha}\right) + R^2 \cos A (\cos A + \cos(B-C)) = 0. \]
16: We check if $r_W = \frac{r \cos A}{1 + \cos A}$ is a root. Using $r = 4R \sin \alpha \sin \frac{B}{2} \sin \frac{C}{2}$ and $1 + \cos A = 2 \cos^2 \alpha$, we have:
17: \[ r_W = \frac{4R \sin \alpha \sin \frac{B}{2} \sin \frac{C}{2} \cos A}{2 \cos^2 \alpha} = \frac{R \sin \alpha \cos A (\cos \frac{B-C}{2} - \sin \alpha)}{\cos^2 \alpha}. \]
18: Let $s = \sin \alpha$, $c = \cos \alpha$, $\Delta = \cos \frac{B-C}{2}$, and $K = \cos A$. Then $r_W = \frac{R s K (\Delta - s)}{c^2}$. Substituting this into the quadratic:
19: The term $r_W^2 \cot^2 \alpha - r_W R (1 + \frac{(1 + 2 K) \Delta}{s})$ simplifies to:
20: \[ \frac{R^2 K}{c^2} \left[ K(\Delta - s)^2 - (\Delta - s)(s + (1 + 2 K) \Delta) \right] = \frac{R^2 K}{c^2} (\Delta - s) [ K\Delta - Ks - s - \Delta - 2K\Delta ] \]
21: \[ = \frac{R^2 K}{c^2} (\Delta - s) [ -\Delta(K+1) - s(K+1) ] = -\frac{R^2 K (K+1)}{c^2} (\Delta^2 - s^2). \]
22: Since $K+1 = 1 + \cos A = 2c^2$, this is $-2 R^2 K (\Delta^2 - s^2)$.
23: The third term is $R^2 K (K + \cos(B-C)) = R^2 K (K + 2\Delta^2 - 1)$. Since $K = 1 - 2s^2$, this is $R^2 K (1 - 2s^2 + 2\Delta^2 - 1) = 2 R^2 K (\Delta^2 - s^2)$.
24: The sum is zero, confirming that $r_W = \frac{r \cos A}{1 + \cos A}$ is indeed a root. Since $(W)$ is closer to $A$ than $(E)$, it corresponds to the smaller root of the quadratic. Thus, $AXI'Y$ is a rhombus.
