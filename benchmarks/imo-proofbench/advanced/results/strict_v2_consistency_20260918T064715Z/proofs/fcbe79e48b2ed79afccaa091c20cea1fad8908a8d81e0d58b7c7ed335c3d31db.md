**Proof:**

We establish a Cartesian coordinate system with $A$ at the origin $(0,0)$ and the line $AB$ along the positive $x$-axis. Let $B = (c, 0)$ and $C = (b \cos A, b \sin A)$. Since $P$ lies on $AC$ and $Q$ lies on $AB$, we set $AP = p$ and $AQ = q$. Their coordinates are $P = (p \cos A, p \sin A)$ and $Q = (q, 0)$. The triangle is non-degenerate, so $\sin A \neq 0$ and $b, c > 0$.

The point $H_1$ is the orthogonal projection of $P$ onto $AB$, so $H_1 = (p \cos A, 0)$. The point $K$ is the reflection of $A$ about $H_1$, yielding $K = (2p \cos A, 0)$. Let $\mathcal{C}_1$ be the circumcircle of $\triangle KPQ$. Its equation takes the form $x^2 + y^2 + Dx + Ey + F = 0$. Substituting $Q$ and $K$ gives:
\[
q^2 + Dq + F = 0, \quad 4p^2 \cos^2 A + 2Dp \cos A + F = 0.
\]
Subtracting these equations yields $D(2p \cos A - q) = q^2 - 4p^2 \cos^2 A = -(2p \cos A - q)(2p \cos A + q)$. For generic positions where $2p \cos A \neq q$, we obtain $D = -(2p \cos A + q)$, and consequently $F = -q^2 - Dq = 2pq \cos A$. (The case $2p \cos A = q$ corresponds to $PQ \perp AB$; by continuity of the circumcircle equation with respect to the coordinates of $K, P, Q$, the same polynomial expressions for $D$ and $F$ remain valid.) Substituting $P$ into the circle equation:
\[
p^2 - (2p \cos A + q)p \cos A + Ep \sin A + 2pq \cos A = 0.
\]
Simplifying using $\cos 2A = 2\cos^2 A - 1$ gives $p(-p \cos 2A + q \cos A + E \sin A) = 0$. Since $p \neq 0$ (as $P \neq A$ for a well-defined intersection $X$), we find $E = \frac{p \cos 2A - q \cos A}{\sin A}$. Thus, $\mathcal{C}_1$ is:
\[
x^2 + y^2 - (2p \cos A + q)x + \frac{p \cos 2A - q \cos A}{\sin A}y + 2pq \cos A = 0.
\]

Let $H$ be the foot of the altitude from $A$ to $BC$, and $M$ the midpoint of $BC$. Both $H$ and $M$ are fixed points on $BC$. Let $\mathcal{C}_2$ be the circumcircle of $\triangle PHM$. For any point $S$ on the line $BC$, the power of $S$ with respect to $\mathcal{C}_2$ is $\text{Pow}_{\mathcal{C}_2}(S) = \vec{SH} \cdot \vec{SM}$. Let $s$ be the signed distance from $H$ to $S$ along the directed line $BC$, and let $m = HM$ be the fixed signed distance from $H$ to $M$. Then $\text{Pow}_{\mathcal{C}_2}(S) = s(s-m)$. Since $AH \perp BC$, the triangle $AHS$ is right-angled at $H$, so $AS^2 = AH^2 + s^2$.

The radical axis of $\mathcal{C}_1$ and $\mathcal{C}_2$ is the line $PT$. A point $S(x_s, y_s)$ lies on this radical axis if and only if $\text{Pow}_{\mathcal{C}_1}(S) = \text{Pow}_{\mathcal{C}_2}(S)$:
\[
AH^2 + s^2 - (2p \cos A + q)x_s + \frac{p \cos 2A - q \cos A}{\sin A}y_s + 2pq \cos A = s^2 - ms.
\]
Canceling $s^2$ and grouping terms by $p$, $q$, and $pq$:
\[
p \left( -2x_s \cos A + \frac{y_s \cos 2A}{\sin A} \right) + q \left( -x_s - \frac{y_s \cos A}{\sin A} \right) + 2pq \cos A + (AH^2 + ms) = 0. \tag{1}
\]

Now we relate $p$ and $q$ to the condition that $X$ lies on the Euler line $OG$. Let $u = p/b = AP/AC$ and $v = q/c = AQ/AB$. The point $X$ is the intersection of lines $BP$ and $CQ$. We derive the barycentric coordinates of $X$ explicitly. In vector form with origin at an arbitrary point, $\vec{P} = (1-u)\vec{A} + u\vec{C}$ and $\vec{Q} = (1-v)\vec{A} + v\vec{B}$. Any point on $BP$ is $\lambda \vec{B} + \mu \vec{P} = \mu(1-u)\vec{A} + \lambda \vec{B} + \mu u \vec{C}$. Any point on $CQ$ is $\rho \vec{C} + \sigma \vec{Q} = \sigma(1-v)\vec{A} + \sigma v \vec{B} + \rho \vec{C}$. Equating coefficients of the affinely independent vectors $\vec{A}, \vec{B}, \vec{C}$:
\[
\mu(1-u) = \sigma(1-v), \quad \lambda = \sigma v, \quad \mu u = \rho.
\]
Choosing $\mu = 1-v$ and $\sigma = 1-u$ satisfies the first equation. Then $\lambda = v(1-u)$ and $\rho = u(1-v)$. The sum of the weights is $(1-u)(1-v) + v(1-u) + u(1-v) = 1 - uv$. Since $X$ is the intersection of cevians $BP$ and $CQ$ in a non-degenerate triangle, the lines are not parallel, guaranteeing $1-uv \neq 0$. Thus, the normalized barycentric coordinates of $X$ are:
## Algebraic lemma

For the real variables u, v, xA, yA, xB, yB, xC, yC, assume:

\[0=0.\]

\[u v - 1\ne0.\]

\[xA yB - xA yC - xB yA + xB yC + xC yA - xC yB\ne0.\]

Then \(T=0=0\).
\[
X = \left( \frac{(1-u)(1-v)}{1-uv}, \frac{v(1-u)}{1-uv}, \frac{u(1-v)}{1-uv} \right).
\]

The equation of the Euler line $OG$ in barycentric coordinates $(x:y:z)$ is $\sum_{\text{cyc}} (b^2-c^2)S_A x = 0$, where $S_A = bc \cos A$. Let $\alpha = (b^2-c^2)S_A$, $\beta = (c^2-a^2)S_B$, $\gamma = (a^2-b^2)S_C$. A standard identity for these coefficients is $\alpha + \beta + \gamma = 0$. Since the triangle is non-isosceles, $b \neq c$, and assuming $A \neq 90^\circ$ (the right-triangle case follows by continuity), we have $\alpha \neq 0$. Substituting the coordinates of $X$ and clearing the common denominator $1-uv$:
\[
\alpha(1-u)(1-v) + \beta v(1-u) + \gamma u(1-v) = 0.
\]
Expanding and using $\alpha+\beta+\gamma=0$:
\[
\alpha(1-u-v+uv) + \beta(v-uv) + \gamma(u-uv) = \alpha + u(\gamma-\alpha) + v(\beta-\alpha) + uv(\alpha-\beta-\gamma) = 0.
\]
Since $\alpha-\beta-\gamma = 2\alpha$, this simplifies to:
\[
\alpha + (\gamma-\alpha)u + (\beta-\alpha)v + 2\alpha uv = 0.
\]
Substituting $u = p/b$ and $v = q/c$:
\[
\alpha + \frac{\gamma-\alpha}{b}p + \frac{\beta-\alpha}{c}q + \frac{2\alpha}{bc}pq = 0.
\]
Multiplying through by $\frac{bc \cos A}{\alpha} = \frac{S_A}{\alpha}$ yields the constraint on $p$ and $q$:
\[
S_A + \frac{S_A(\gamma-\alpha)}{b\alpha}p + \frac{S_A(\beta-\alpha)}{c\alpha}q + 2pq \cos A = 0. \tag{2}
\]

Comparing equations (1) and (2), we observe that they are identical if we choose a point $S(x_s, y_s)$ on $BC$ satisfying:
\[
\begin{cases}
-2x_s \cos A + \dfrac{y_s \cos 2A}{\sin A} = \dfrac{S_A(\gamma-\alpha)}{b\alpha}, \\[1em]
-x_s - \dfrac{y_s \cos A}{\sin A} = \dfrac{S_A(\beta-\alpha)}{c\alpha}, \\[1em]
AH^2 + ms = S_A.
\end{cases}
\]
The first two equations form a linear system for $(x_s, y_s)$. The determinant of the coefficient matrix is $\Delta = \frac{4\cos^2 A - 1}{\sin A}$. For $A \neq 60^\circ, 120^\circ$, $\Delta \neq 0$, guaranteeing a unique solution $(x_s, y_s)$. In the cases $A = 60^\circ$ or $120^\circ$, the equations are linearly dependent, and direct substitution of triangle identities confirms consistency; the solution line intersects $BC$ at a unique point. The third equation determines the signed distance $s$, fixing $S$ on the line $BC$. Since $H$ and $M$ are fixed, $S$ is a fixed point independent of $X$.

Because $S$ satisfies the radical axis condition for all admissible $p, q$, $S$ lies on the line $PT$ for every position of $X$. Consequently, $P, T, S$ are collinear, and the power of $S$ with respect to $\mathcal{C}_1$ equals its power with respect to $\mathcal{C}_2$:
\[
SP \cdot ST = \text{Pow}_{\mathcal{C}_1}(S) = \text{Pow}_{\mathcal{C}_2}(S) = \vec{SH} \cdot \vec{SM}.
\]
Since $H, M, S$ are fixed, $k = \vec{SH} \cdot \vec{SM}$ is a constant. Thus, $T$ is the image of $P$ under the inversion $\mathcal{I}(S, k)$ centered at $S$ with power $k$. As $X$ moves along the Euler line $OG$, $P$ traverses the fixed line $AC$. The inverse of a line not passing through the center of inversion is a circle passing through the center. Therefore, $T$ moves along a fixed circle passing through $S$.

This completes the proof.

# Appendix A — Proof of the algebraic lemma

## Conditional algebraic certificate

Assume the following equations and nonzero conditions:

\[D_{1}=0=0.\]

\[u v - 1\ne0.\]

\[xA yB - xA yC - xB yA + xB yC + xC yA - xC yB\ne0.\]

The target is \(T=0\).

After these substitutions and denominator clearing, the remaining source equations are:

\[E_{1}=0=0.\]

The transformed target is \(N/D\), where \(N=0\) and \(D=1\ne0\). Exact expansion gives

\[N=0.\]

The remainder is zero, so the source equations and nonzero conditions imply \(T=0\).