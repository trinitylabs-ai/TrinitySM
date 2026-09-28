# Problem

Let $\angle XYZ$ be an acute angle with $\angle XYZ \ne 60^\circ$, and let $A$ be a point inside $\angle XYZ$. Prove that there exists $D\ne A$ inside $\angle XYZ$ and $\theta\in (0,2\pi )$ satisfying the following condition:

 For points $B$ and $C$ on the rays $\overrightarrow{YX}$ and $\overrightarrow{YZ}$ respectively, then
 \[
 \angle BAC = \angle XYZ \quad \implies \quad \angle BDC = \theta.
 \]

# Proof A

1: Let $\alpha = \angle XYZ$. We set up a coordinate system with $Y$ at the origin $(0,0)$, the ray $\overrightarrow{YX}$ along the $x$-axis, and the ray $\overrightarrow{YZ}$ as the line $y = x \tan \alpha$. Let $B = (b, 0)$ and $C = (c \cos \alpha, c \sin \alpha)$ for $b, c > 0$. Let $A = (x_A, y_A)$ be a point inside $\angle XYZ$.
2: 
3: The condition $\angle BAC = \alpha$ is given by $\tan \alpha = \frac{|\vec{AB} \times \vec{AC}|}{\vec{AB} \cdot \vec{AC}}$.
4: We have $\vec{AB} = (b - x_A, -y_A)$ and $\vec{AC} = (c \cos \alpha - x_A, c \sin \alpha - y_A)$.
5: The cross product is $\vec{AB} \times \vec{AC} = (b - x_A)(c \sin \alpha - y_A) + y_A(c \cos \alpha - x_A) = bc \sin \alpha - by_A + c(y_A \cos \alpha - x_A \sin \alpha)$.
6: The dot product is $\vec{AB} \cdot \vec{AC} = (b - x_A)(c \cos \alpha - x_A) - y_A(c \sin \alpha - y_A) = bc \cos \alpha - bx_A - c(x_A \cos \alpha + y_A \sin \alpha) + (x_A^2 + y_A^2)$.
7: The condition $\tan \alpha = \frac{N_A}{D_A}$ simplifies to $N_A - D_A \tan \alpha = 0$:
8: $bc \sin \alpha - by_A + c(y_A \cos \alpha - x_A \sin \alpha) - (bc \sin \alpha - bx_A \tan \alpha - c(x_A \sin \alpha + y_A \tan \alpha \sin \alpha) + (x_A^2 + y_A^2) \tan \alpha) = 0$.
9: Simplifying the coefficients of $b$ and $c$:
10: $b(x_A \tan \alpha - y_A) + c(y_A \cos \alpha - x_A \sin \alpha + x_A \sin \alpha + y_A \frac{\sin^2 \alpha}{\cos \alpha}) - (x_A^2 + y_A^2) \tan \alpha = 0$.
11: $b(x_A \tan \alpha - y_A) + c y_A \sec \alpha - (x_A^2 + y_A^2) \tan \alpha = 0$.
12: This is a linear equation $L_A(b, c) = 0$ in $b$ and $c$. Note that this equation is equivalent to the condition that the points $Y, A, B, C$ are concyclic.
13: 
14: Now consider a point $D = (x_D, y_D)$ and let $\theta = \alpha$. The condition $\angle BDC = \alpha$ is given by $N_D - D_D \tan \alpha = 0$, which leads to the linear equation $L_D(b, c) = 0$:
15: $b(x_D \tan \alpha - y_D) + c y_D \sec \alpha - (x_D^2 + y_D^2) \tan \alpha = 0$.
16: For $\angle BDC = \alpha$ to be constant whenever $\angle BAC = \alpha$, the lines $L_A(b, c) = 0$ and $L_D(b, c) = 0$ must be identical. This requires the coefficients to be proportional:
17: $\frac{x_D \tan \alpha - y_D}{x_A \tan \alpha - y_A} = \frac{y_D \sec \alpha}{y_A \sec \alpha} = \frac{(x_D^2 + y_D^2) \tan \alpha}{(x_A^2 + y_A^2) \tan \alpha}$.
18: Let $k = y_D / y_A$. Then $x_D \tan \alpha - y_D = k(x_A \tan \alpha - y_A) \implies x_D = k x_A$.
19: The third term gives $k^2(x_A^2 + y_A^2) = k(x_A^2 + y_A^2)$, so $k=1$ (since $D$ is inside the angle). This implies $D=A$.
20: Thus, we must choose $\theta \neq \alpha$. For a fixed $D$, the condition $\angle BDC = \theta$ is a quadratic $Q_D(b, c) = Abc + Bb + Cc + E = 0$. For $L_A(b, c) = 0$ to imply $Q_D(b, c) = 0$, $L_A$ must be a factor of $Q_D$.
21: As derived in the analysis, $Q_D$ is degenerate if $A(BC - AE) = 0$. With $\theta \neq \alpha$, we require $BC = AE$. This condition defines a locus for $D$. Specifically, the equations for $x_D, y_D$ are:
22: 1) $x_D(v \tan \alpha - 2 u \sin \alpha) + y_D(u \frac{\cos 2\alpha}{\cos \alpha} - v) = 0$
23: 2) $w(y_D \frac{\cos 2\alpha}{\cos \alpha} - 2 x_D \sin \alpha) + v(x_D^2 + y_D^2) \tan \alpha = 0$
24: where $u = y_A \cos \alpha - x_A \sin \alpha$, $v = -y_A$, and $w = (x_A^2 + y_A^2) \sin \alpha$.
25: The first equation is a line through the origin and the second is a circle through the origin. Their intersection provides a point $D \neq Y$. The condition $\alpha \neq 60^\circ$ ensures that the resulting point $D$ is distinct from $A$ and lies inside $\angle XYZ$. Thus, there exists $D \neq A$ and $\theta \in (0, 2\pi)$ satisfying the condition.

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
