# Problem

In $\triangle ABC$ the altitudes $BE$ and $CF$ intersect at $H$. A circle $(W)$ is
 externally tangent to the Euler circle $(E)$ of $\triangle ABC$ and also tangent
 to the sides $AB$ and $AC$ at $X$ and $Y$, respectively, with
 $(W)$ being closer to $A$ than the Euler circle. Let $I'$ be the
 incenter of $\triangle AEF$. Prove that $AXI'Y$ is a rhombus.

# Proof A

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
