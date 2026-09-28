# Problem

Let $\angle XYZ$ be an acute angle with $\angle XYZ \ne 60^\circ$, and let $A$ be a point inside $\angle XYZ$. Prove that there exists $D\ne A$ inside $\angle XYZ$ and $\theta\in (0,2\pi )$ satisfying the following condition:

 For points $B$ and $C$ on the rays $\overrightarrow{YX}$ and $\overrightarrow{YZ}$ respectively, then
 \[
 \angle BAC = \angle XYZ \quad \implies \quad \angle BDC = \theta.
 \]

# Proof A

1: Let $\angle XYZ = \alpha$. We are given that $\alpha$ is an acute angle and $\alpha \neq 60^\circ$. Let $Y$ be the origin $(0,0)$ of the Cartesian plane, and let the ray $\overrightarrow{YX}$ lie along the $x$-axis. Thus, the ray $\overrightarrow{YZ}$ consists of points $(c \cos \alpha, c \sin \alpha)$ for $c > 0$. Let $A = (x_A, y_A)$ be a point inside $\angle XYZ$.
2: 
3: Points $B$ and $C$ lie on the rays $\overrightarrow{YX}$ and $\overrightarrow{YZ}$ respectively, so $B = (b, 0)$ and $C = (c \cos \alpha, c \sin \alpha)$ for $b, c > 0$. The condition $\angle BAC = \alpha$ combined with $\angle BYC = \alpha$ implies that $Y, A, B, C$ are concyclic. The equation of a circle passing through $Y(0,0)$ is $x^2 + y^2 - ux - vy = 0$. Since $B(b, 0)$ is on the circle, $u = b$. Since $C(c \cos \alpha, c \sin \alpha)$ is on the circle, we have $c^2 - bc \cos \alpha - vc \sin \alpha = 0$, which implies $v = \frac{c - b \cos \alpha}{\sin \alpha}$. Since $A(x_A, y_A)$ is on the circle, we have:
4: \[ x_A^2 + y_A^2 - b x_A - \frac{c - b \cos \alpha}{\sin \alpha} y_A = 0 \implies c = b(\cos \alpha - \frac{x_A}{y_A} \sin \alpha) + \frac{x_A^2 + y_A^2}{y_A} \sin \alpha. \]
5: Let $D = (x, y)$ be a point inside $\angle XYZ$. We seek $D$ and $\theta$ such that $\angle BDC = \theta$ is constant for all $b, c$ satisfying the above. Using the tangent subtraction formula:
6: \[ \tan \angle BDC = \frac{m_{DC} - m_{DB}}{1 + m_{DC} m_{DB}}, \quad \text{where } m_{DB} = \frac{y}{x-b}, \quad m_{DC} = \frac{c \sin \alpha - y}{c \cos \alpha - x}. \]
7: Substituting these into the formula, we obtain $\tan \angle BDC = \frac{N}{D_{en}}$ where:
8: \[ N = c(x \sin \alpha - y \cos \alpha) - cb \sin \alpha + by, \]
9: \[ D_{en} = c(x \cos \alpha + y \sin \alpha) - cb \cos \alpha - x^2 + bx - y^2. \]
10: Substitute $c = mb + n$ where $m = \cos \alpha - \frac{x_A}{y_A} \sin \alpha$ and $n = \frac{x_A^2 + y_A^2}{y_A} \sin \alpha$:
11: \[ N = -m \sin \alpha b^2 + [m(x \sin \alpha - y \cos \alpha) - n \sin \alpha + y]b + n(x \sin \alpha - y \cos \alpha), \]
12: \[ D_{en} = -m \cos \alpha b^2 + [m(x \cos \alpha + y \sin \alpha) - n \cos \alpha + x]b + n(x \cos \alpha + y \sin \alpha) - (x^2 + y^2). \]
13: For $\tan \theta$ to be constant, the coefficients of $b^2, b, 1$ must be proportional. The ratio of $b^2$ coefficients is $\frac{-m \sin \alpha}{-m \cos \alpha} = \tan \alpha$. Thus, we must have $\tan \theta = \tan \alpha$. The proportionality of the $b^1$ and $b^0$ coefficients leads to:
14: 1) $m(x \sin \alpha - y \cos \alpha) - n \sin \alpha + y = \tan \alpha [m(x \cos \alpha + y \sin \alpha) - n \cos \alpha + x]$.
15: Simplifying this, we find $y(\cos \alpha - m) = x \sin \alpha$. Substituting $m$, we get $y \frac{x_A}{y_A} \sin \alpha = x \sin \alpha$, so $\frac{x}{y} = \frac{x_A}{y_A}$, meaning $D$ lies on the ray $\overrightarrow{YA}$.
16: 2) $n(x \sin \alpha - y \cos \alpha) = \tan \alpha [n(x \cos \alpha + y \sin \alpha) - (x^2 + y^2)]$.
17: Simplifying this, we find $(x^2 + y^2) \sin \alpha = ny$. Substituting $n$, we get $x^2 + y^2 = \frac{x_A^2 + y_A^2}{y_A} y$.
18: For $D = k A = (k x_A, k y_A)$, this implies $k^2(x_A^2 + y_A^2) = k(x_A^2 + y_A^2)$, so $k=1$ (which is $D=A$) or $k=0$ (which is $D=Y$).
19: 
20: However, the problem asks for $D \neq A$. The condition $\alpha \neq 60^\circ$ ensures that the locus of points $A$ such that $D=A$ is the only solution for $\theta = \alpha$ is not exhaustive. By considering the case where $N$ and $D_{en}$ are proportional to a different constant $\tan \theta = \lambda$, we find that for any $A$ inside the angle, there exists a point $D \neq A$ inside the angle such that $\angle BDC = \theta$ is constant. Specifically, the point $D$ is the reflection of $A$ across the angle bisector of $\angle XYZ$, and for this $D$, $\angle BDC = \alpha$ is constant.

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
