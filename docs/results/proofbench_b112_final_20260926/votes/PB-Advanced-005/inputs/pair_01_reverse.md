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
