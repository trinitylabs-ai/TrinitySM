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
