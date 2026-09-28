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
