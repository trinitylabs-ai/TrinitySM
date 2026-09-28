To prove that $XO$ is perpendicular to $DE$, we establish a coordinate system. Let the vertex $C$ be the origin $(0, 0)$ and the side $AC$ lie along the $x$-axis. Let the angles of the acute triangle $ABC$ be $\alpha, \beta, \gamma$ and its side lengths be $a, b, c$.

Let $r = CE$. Since $CE$ is the altitude from $C$ to $AB$, we have $r = a \sin \beta$. The angle $\angle ACE = 90^\circ - \alpha$, so the coordinates of $E$ are:
$$E = (r \cos(90^\circ - \alpha), r \sin(90^\circ - \alpha)) = (r \sin \alpha, r \cos \alpha)$$
$E_1$ is the reflection of $E$ with respect to $AC$ (the $x$-axis), so:
$$E_1 = (r \sin \alpha, -r \cos \alpha)$$
$E_2$ is the reflection of $E$ with respect to $BC$. The line $BC$ makes an angle $\gamma$ with the $x$-axis. The angle of $CE$ is $90^\circ - \alpha$, so the angle of $CE_2$ is $\gamma + (\gamma - (90^\circ - \alpha)) = 2\gamma + \alpha - 90^\circ$. Thus:
$$E_2 = (r \cos(2\gamma + \alpha - 90^\circ), r \sin(2\gamma + \alpha - 90^\circ)) = (r \sin(2\gamma + \alpha), -r \cos(2\gamma + \alpha))$$
Let $O = (x_O, y_O)$ be the circumcenter of $\triangle CE_1E_2$. Since $C(0,0)$ is on the circle, the equation of the circumcircle is $x^2 + y^2 - 2x_O x - 2y_O y = 0$. Substituting the coordinates of $E_1$ and $E_2$:
1. $r^2 - 2x_O(r \sin \alpha) - 2y_O(-r \cos \alpha) = 0 \implies 2x_O \sin \alpha - 2y_O \cos \alpha = r$
2. $r^2 - 2x_O(r \sin(2\gamma + \alpha)) - 2y_O(-r \cos(2\gamma + \alpha)) = 0 \implies 2x_O \sin(2\gamma + \alpha) - 2y_O \cos(2\gamma + \alpha) = r$

Subtracting these equations gives:
$$2x_O (\sin(2\gamma + \alpha) - \sin \alpha) = 2y_O (\cos(2\gamma + \alpha) - \cos \alpha)$$
Using the sum-to-product identities $\sin A - \sin B = 2 \cos \frac{A+B}{2} \sin \frac{A-B}{2}$ and $\cos A - \cos B = -2 \sin \frac{A+B}{2} \sin \frac{A-B}{2}$:
$$2x_O (2 \cos(\gamma + \alpha) \sin \gamma) = 2y_O (-2 \sin(\gamma + \alpha) \sin \gamma)$$
$$x_O \cos(\gamma + \alpha) = -y_O \sin(\gamma + \alpha) \implies y_O = -x_O \cot(\gamma + \alpha)$$
Substituting this back into the first equation:
$$2x_O \sin \alpha + 2x_O \cot(\gamma + \alpha) \cos \alpha = r \implies 2x_O \frac{\sin \alpha \sin(\gamma + \alpha) + \cos \alpha \cos(\gamma + \alpha)}{\sin(\gamma + \alpha)} = r$$
$$2x_O \frac{\cos(\gamma + \alpha - \alpha)}{\sin(\gamma + \alpha)} = r \implies x_O = \frac{r \sin(\gamma + \alpha)}{2 \cos \gamma}, \quad y_O = -\frac{r \cos(\gamma + \alpha)}{2 \cos \gamma}$$
$X$ is the intersection of the circle and $AC$ (the $x$-axis) other than $C$. For $y=0$, $x^2 - 2x_O x = 0 \implies x = 2x_O$. Thus:
$$X = \left(\frac{r \sin(\gamma + \alpha)}{\cos \gamma}, 0\right)$$
The vector $\vec{XO} = O - X = (-x_O, y_O) = \left(-\frac{r \sin(\gamma + \alpha)}{2 \cos \gamma}, -\frac{r \cos(\gamma + \alpha)}{2 \cos \gamma}\right)$.
$D$ is the foot of the altitude from $B$ to $AC$, so $CD = a \cos \gamma$ and $D = (a \cos \gamma, 0)$.
The vector $\vec{DE} = E - D = (r \sin \alpha - a \cos \gamma, r \cos \alpha)$.
The dot product $\vec{XO} \cdot \vec{DE}$ is:
$$\vec{XO} \cdot \vec{DE} = -x_O(r \sin \alpha - a \cos \gamma) + y_O(r \cos \alpha)$$
$$= -\frac{r \sin(\gamma + \alpha)}{2 \cos \gamma} (r \sin \alpha - a \cos \gamma) - \frac{r \cos(\gamma + \alpha)}{2 \cos \gamma} (r \cos \alpha)$$
$$= -\frac{r}{2 \cos \gamma} [r (\sin(\gamma + \alpha) \sin \alpha + \cos(\gamma + \alpha) \cos \alpha) - a \sin(\gamma + \alpha) \cos \gamma]$$
$$= -\frac{r}{2 \cos \gamma} [r \cos \gamma - a \sin(\gamma + \alpha) \cos \gamma] = -\frac{r}{2} [r - a \sin(\gamma + \alpha)]$$
Since $r = a \sin \beta$ and $\sin \beta = \sin(180^\circ - (\alpha + \gamma)) = \sin(\alpha + \gamma)$, we have $r - a \sin(\gamma + \alpha) = 0$.
Thus, $\vec{XO} \cdot \vec{DE} = 0$, which proves that $XO \perp DE$.

\(\square\)
