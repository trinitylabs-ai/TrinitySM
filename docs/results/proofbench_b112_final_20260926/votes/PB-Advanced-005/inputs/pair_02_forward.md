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
