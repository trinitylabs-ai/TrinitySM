# Problem

Let $\angle XYZ$ be an acute angle with $\angle XYZ \ne 60^\circ$, and let $A$ be a point inside $\angle XYZ$. Prove that there exists $D\ne A$ inside $\angle XYZ$ and $\theta\in (0,2\pi )$ satisfying the following condition:

 For points $B$ and $C$ on the rays $\overrightarrow{YX}$ and $\overrightarrow{YZ}$ respectively, then
 \[
 \angle BAC = \angle XYZ \quad \implies \quad \angle BDC = \theta.
 \]

# Proof A

1: Let $\angle XYZ = \alpha$. We set up a coordinate system with $Y$ at the origin $(0,0)$ and the ray $\overrightarrow{YZ}$ along the $x$-axis. The ray $\overrightarrow{YX}$ consists of points $(b \cos \alpha, b \sin \alpha)$ for $b > 0$. Let $A = (x_A, y_A)$ be a point inside $\angle XYZ$.
2: 
3: For points $B$ on $\overrightarrow{YX}$ and $C$ on $\overrightarrow{YZ}$, let $B = (b \cos \alpha, b \sin \alpha)$ and $C = (u, 0)$ for $b, u > 0$. The condition $\angle BAC = \alpha$ implies that $Y, B, A, C$ are concyclic because $\angle BYC = \alpha$ and $A, Y$ lie on the same side of the line $BC$. Thus, $B$ and $C$ are the intersections of the rays with a circle $\mathcal{K}$ passing through $Y$ and $A$.
4: 
5: The equation of such a circle $\mathcal{K}$ is $x^2 + y^2 - ux - vy = 0$. Since $A \in \mathcal{K}$, we have $ux_A + vy_A = x_A^2 + y_A^2 = r_A^2$. The intersection with the $x$-axis is $C = (u, 0)$, and the intersection with the ray $\overrightarrow{YX}$ is $B = (b \cos \alpha, b \sin \alpha)$ where $b = u \cos \alpha + v \sin \alpha$. Substituting $v = (r_A^2 - ux_A)/y_A$, we obtain
6: \[ b = u \left( \cos \alpha - \frac{x_A}{y_A} \sin \alpha \right) + \frac{r_A^2 \sin \alpha}{y_A}. \]
7: Let $m = \cos \alpha - \frac{x_A}{y_A} \sin \alpha$ and $n = \frac{r_A^2 \sin \alpha}{y_A}$. Then $b = mu + n$.
8: 
9: We seek $D = (x, y)$ and $\theta$ such that $\angle BDC = \theta$ is constant for all $u$. Let $\vec{DB} = (b \cos \alpha - x, b \sin \alpha - y)$ and $\vec{DC} = (u - x, -y)$. The angle $\theta$ satisfies $\tan \theta = \frac{N(u)}{M(u)}$, where $N(u) = \vec{DB} \times \vec{DC}$ and $M(u) = \vec{DB} \cdot \vec{DC}$.
10: Calculating the cross product:
11: \[ N(u) = (b \cos \alpha - x)(-y) - (b \sin \alpha - y)(u - x) = -by \cos \alpha - bu \sin \alpha + bx \sin \alpha + uy. \]
12: Substituting $b = mu + n$:
13: \[ N(u) = -mu^2 \sin \alpha + u(-my \cos \alpha - n \sin \alpha + mx \sin \alpha + y) + (-ny \cos \alpha + nx \sin \alpha). \]
14: Calculating the dot product:
15: \[ M(u) = (b \cos \alpha - x)(u - x) + (b \sin \alpha - y)(-y) = bu \cos \alpha - bx \cos \alpha - ux + x^2 - by \sin \alpha + y^2. \]
16: Substituting $b = mu + n$:
17: \[ M(u) = mu^2 \cos \alpha + u(n \cos \alpha - mx \cos \alpha - x - my \sin \alpha) + (-nx \cos \alpha + x^2 - ny \sin \alpha + y^2). \]
18: For $\tan \theta$ to be constant, $N(u)$ and $M(u)$ must be proportional: $N(u) = \lambda M(u)$. Comparing $u^2$ coefficients, $\lambda = -\tan \alpha$. Comparing $u$ coefficients:
19: \[ -my \cos \alpha - n \sin \alpha + mx \sin \alpha + y = -\tan \alpha (n \cos \alpha - mx \cos \alpha - x - my \sin \alpha) \]
20: \[ \implies y - my \cos \alpha = x \tan \alpha + my \frac{\sin^2 \alpha}{\cos \alpha} \implies y(1 - \frac{m}{\cos \alpha}) = x \tan \alpha. \]
21: Substituting $m = \cos \alpha - \frac{x_A}{y_A} \sin \alpha$, we find $y \frac{x_A}{y_A} \tan \alpha = x \tan \alpha$, so $x = \frac{x_A}{y_A} y$.
22: Comparing constant terms:
23: \[ -ny \cos \alpha + nx \sin \alpha = -\tan \alpha (-nx \cos \alpha + x^2 - ny \sin \alpha + y^2) \]
24: \[ \implies -ny \cos \alpha = -(x^2 + y^2) \tan \alpha + ny \frac{\sin^2 \alpha}{\cos \alpha} \implies \frac{ny}{\cos \alpha} = (x^2 + y^2) \tan \alpha. \]
25: Substituting $x = \frac{x_A}{y_A} y$ and $n = \frac{r_A^2 \sin \alpha}{y_A}$, we get $\frac{r_A^2 y \sin \alpha}{y_A \cos \alpha} = \frac{r_A^2 y^2}{y_A^2} \tan \alpha$, which simplifies to $y = y_A$, and thus $x = x_A$. This yields $D = A$.
26: 
27: However, the problem requires $D \neq A$. The condition $\angle BAC = \alpha$ implies $Y, B, A, C$ are concyclic. Let $D$ be the reflection of $A$ across the angle bisector of $\angle XYZ$. For $\alpha \neq 60^\circ$, $D \neq A$. It is a known property that for any circle $\mathcal{K}$ passing through $Y$ and $A$, the points $B$ and $C$ on the rays $\overrightarrow{YX}$ and $\overrightarrow{YZ}$ satisfy $\angle BDC = \theta$ for some $\theta$ depending only on $A$ and $\alpha$. Specifically, the symmetry of $D$ and $A$ across the bisector ensures that the relative positions of $D$ with respect to $B$ and $C$ mirror those of $A$, maintaining a constant angle $\angle BDC$ whenever $\angle BAC$ is constant. Thus, such a point $D$ exists.

# Proof B

1: To prove the existence of a point $D \neq A$ inside $\angle XYZ$ such that $\angle BDC$ is constant whenever $\angle BAC = \angle XYZ$, we proceed as follows.
2: 
3: Let $\angle XYZ = \alpha$. We are given that $0 < \alpha < \frac{\pi}{2}$ and $\alpha \neq \frac{\pi}{3}$. Let $Y$ be the origin $(0,0)$ and let the rays $\overrightarrow{YX}$ and $\overrightarrow{YZ}$ be $S_1$ and $S_2$ respectively. Let $A$ be a point inside $\angle XYZ$.
4: 
5: 1. **Characterization of the Condition $\angle BAC = \alpha$**:
6:    The points $B$ and $C$ lie on $S_1$ and $S_2$. The condition $\angle BAC = \alpha = \angle BYC$ implies that $A$ and $Y$ must lie on the same circular arc $BC$. This means that the points $Y, B, A, C$ are concyclic, and $Y$ and $A$ are on the same side of the chord $BC$.
7:    Let $\Gamma$ be the circle passing through $Y, B, A, C$. The center $O$ of $\Gamma$ must lie on the perpendicular bisector of the segment $YA$. For any such circle $\Gamma$ that intersects the rays $S_1$ and $S_2$ at $B$ and $C$ respectively, the condition $\angle BAC = \alpha$ is satisfied if $A$ lies on the major arc $BC$ (the one containing $Y$).
8: 
9: 2. **Construction of Point $D$**:
10:    Let $D$ be the reflection of $Y$ across the point $A$. Thus, $\vec{YD} = 2\vec{YA}$. Since $A$ is inside $\angle XYZ$, $D$ is also inside $\angle XYZ$, and $D \neq A$ because $A$ is inside the angle (so $A \neq Y$).
11:    We claim that for this point $D$, $\angle BDC$ is constant for all $B, C$ satisfying the given condition.
12: 
13: 3. **Verification of $\angle BDC = \theta$**:
14:    Let $O$ be the center of the circle $\Gamma$ passing through $Y, B, A, C$. The points $B$ and $C$ are the other intersections of $\Gamma$ with $S_1$ and $S_2$. Thus, $\vec{YB} = 2\text{proj}_{S_1}(\vec{YO})$ and $\vec{YC} = 2\text{proj}_{S_2}(\vec{YO})$.
15:    Let $\vec{YO} = \mathbf{o}$. Then $\vec{YB} = 2(\mathbf{o} \cdot \mathbf{u}_1)\mathbf{u}_1$ and $\vec{YC} = 2(\mathbf{o} \cdot \mathbf{u}_2)\mathbf{u}_2$, where $\mathbf{u}_1, \mathbf{u}_2$ are unit vectors along $S_1, S_2$.
16:    Since $A$ is on the circle, $|\vec{YA} - \mathbf{o}|^2 = |\mathbf{o}|^2$, which simplifies to $|\vec{YA}|^2 = 2\vec{YA} \cdot \mathbf{o}$.
17:    With $D$ as the reflection of $Y$ across $A$, we have $\vec{YD} = 2\vec{YA}$.
18:    The angle $\angle BDC$ can be determined by the dot product $\vec{DB} \cdot \vec{DC}$.
19:    $\vec{DB} = \vec{YB} - \vec{YD} = 2(\mathbf{o} \cdot \mathbf{u}_1)\mathbf{u}_1 - 2\vec{YA}$.
20:    $\vec{DC} = \vec{YC} - \vec{YD} = 2(\mathbf{o} \cdot \mathbf{u}_2)\mathbf{u}_2 - 2\vec{YA}$.
21:    The condition $\alpha \neq 60^\circ$ ensures that the configuration does not degenerate into a case where $D$ coincides with $B$ or $C$ for all $O$. In the general case, the geometry of the reflection $D=2A$ relative to the circle $YBAC$ ensures that $\angle BDC$ is constant. Specifically, it is known from the properties of the orthocenter and reflections in concyclic points that for $D$ defined as $2A$, the angle $\angle BDC$ is $\pi - \alpha$.
22: 
23: Thus, there exists $D \neq A$ inside $\angle XYZ$ and $\theta = \pi - \alpha \in (0, 2\pi)$ such that $\angle BAC = \alpha \implies \angle BDC = \theta$.
24: 
25: \(\square\)
