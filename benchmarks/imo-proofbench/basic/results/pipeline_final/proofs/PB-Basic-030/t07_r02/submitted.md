To prove that circles $(W_3)$ and $(W_4)$ are tangent, we analyze the positions of their centers and their radii using a vector-based approach.

**1. Setup and Definitions**
Let $ABCD$ be a trapezoid with legs $AB$ and $CD$. This implies the bases are $AD$ and $BC$, so $AD \parallel BC$. Let $L_1 = AB$ and $L_2 = CD$. Let $M_1$ and $M_2$ be the midpoints of $AB$ and $CD$, respectively.
For a circle passing through a chord of length $L$ with an inscribed angle $\theta$ corresponding to the arc opposite to the chord's side, the radius is $R = \frac{L}{2 \sin \theta}$ and the distance from the center to the chord is $h = \frac{L}{2} \cot \theta$.

Let $\vec{u_1}$ be the unit vector perpendicular to $AB$ pointing towards the side of $C$ and $D$, and $\vec{u_2}$ be the unit vector perpendicular to $CD$ pointing towards the side of $A$ and $B$.
The centers of the circles are:
- $O_1 = M_1 + h_1 \vec{u_1}$ where $h_1 = \frac{L_1}{2} \cot \alpha$
- $O_2 = M_2 + h_2 \vec{u_2}$ where $h_2 = \frac{L_2}{2} \cot \beta$
- $O_3 = M_1 + h_3 \vec{u_1}$ where $h_3 = \frac{L_1}{2} \cot \beta$
- $O_4 = M_2 + h_4 \vec{u_2}$ where $h_4 = \frac{L_2}{2} \cot \alpha$
The radii are $R_1 = \frac{L_1}{2 \sin \alpha}, R_2 = \frac{L_2}{2 \sin \beta}, R_3 = \frac{L_1}{2 \sin \beta}, R_4 = \frac{L_2}{2 \sin \alpha}$.

We justify the center positions. For $(W_1)$, the arc $AB$ on the side opposite to $C$ and $D$ has inscribed angle $\alpha$. Let $S_{CD}$ be the half-plane defined by $AB$ containing $C$ and $D$. The arc $AB$ lies in $S_{CD}^c$.
- If $\alpha < \pi/2$, the center $O_1$ and the arc lie on opposite sides of $AB$. Thus $O_1 \in S_{CD}$. Since $h_1 = \frac{L_1}{2} \cot \alpha > 0$ and $\vec{u_1}$ points into $S_{CD}$, $O_1 = M_1 + h_1 \vec{u_1}$ is correct.
- If $\alpha > \pi/2$, the center $O_1$ and the arc lie on the same side of $AB$. Thus $O_1 \in S_{CD}^c$. Since $h_1 = \frac{L_1}{2} \cot \alpha < 0$ and $\vec{u_1}$ points into $S_{CD}$, $O_1 = M_1 + h_1 \vec{u_1}$ correctly places $O_1$ in $S_{CD}^c$.
Thus, the formula $O_1 = M_1 + h_1 \vec{u_1}$ is universally correct. By symmetry, $O_2 = M_2 + h_2 \vec{u_2}$ is also correct.

**2. The Tangency Condition for $(W_1)$ and $(W_2)$**
Let $\vec{v} = M_2 - M_1$. The distance between centers $O_1$ and $O_2$ is:
$O_1O_2^2 = \|\vec{v} + h_2 \vec{u_2} - h_1 \vec{u_1}\|^2 = v^2 + h_1^2 + h_2^2 + 2h_2 (\vec{v} \cdot \vec{u_2}) - 2h_1 (\vec{v} \cdot \vec{u_1}) - 2h_1 h_2 (\vec{u_1} \cdot \vec{u_2})$.
Since $(W_1)$ and $(W_2)$ are tangent, $O_1O_2^2 = (R_1 \pm R_2)^2 = R_1^2 + R_2^2 \pm 2R_1 R_2$. Using $R_1^2 = h_1^2 + (L_1/2)^2$ and $R_2^2 = h_2^2 + (L_2/2)^2$, we obtain:
$v^2 + 2h_2 (\vec{v} \cdot \vec{u_2}) - 2h_1 (\vec{v} \cdot \vec{u_1}) - 2h_1 h_2 (\vec{u_1} \cdot \vec{u_2}) = \frac{L_1^2 + L_2^2}{4} \pm 2R_1 R_2$.

**3. Proving Tangency for $(W_3)$ and $(W_4)$**
Similarly, the distance between $O_3$ and $O_4$ is:
$O_3O_4^2 = v^2 + h_3^2 + h_4^2 + 2h_4 (\vec{v} \cdot \vec{u_2}) - 2h_3 (\vec{v} \cdot \vec{u_1}) - 2h_3 h_4 (\vec{u_1} \cdot \vec{u_2})$.
We compare $O_3O_4^2$ with $(R_3 \pm R_4)^2 = h_3^2 + h_4^2 + \frac{L_1^2 + L_2^2}{4} \pm 2R_3 R_4$.
The difference is:
$O_3O_4^2 - (R_3 \pm R_4)^2 = v^2 + 2h_4 (\vec{v} \cdot \vec{u_2}) - 2h_3 (\vec{v} \cdot \vec{u_1}) - 2h_3 h_4 (\vec{u_1} \cdot \vec{u_2}) - \frac{L_1^2 + L_2^2}{4} \mp 2R_3 R_4$.
Substituting the value of $\frac{L_1^2 + L_2^2}{4}$ from the $O_1O_2$ equation and noting $h_1 h_2 = h_3 h_4 = \frac{L_1 L_2}{4} \cot \alpha \cot \beta$ and $R_1 R_2 = R_3 R_4 = \frac{L_1 L_2}{4 \sin \alpha \sin \beta}$:
$O_3O_4^2 - (R_3 \pm R_4)^2 = 2(h_4 - h_2) (\vec{v} \cdot \vec{u_2}) - 2(h_3 - h_1) (\vec{v} \cdot \vec{u_1})$.
Substituting $h_4 - h_2 = \frac{L_2}{2}(\cot \alpha - \cot \beta)$ and $h_3 - h_1 = \frac{L_1}{2}(\cot \beta - \cot \alpha)$:
$O_3O_4^2 - (R_3 \pm R_4)^2 = L_2 (\cot \alpha - \cot \beta) (\vec{v} \cdot \vec{u_2}) - L_1 (\cot \beta - \cot \alpha) (\vec{v} \cdot \vec{u_1})$
$= (\cot \alpha - \cot \beta) [L_2 (\vec{v} \cdot \vec{u_2}) + L_1 (\vec{v} \cdot \vec{u_1})]$.

We now prove that $L_1 (\vec{v} \cdot \vec{u_1}) = - L_2 (\vec{v} \cdot \vec{u_2})$. Note that $\vec{v} = M_2 - M_1 = \frac{C+D-A-B}{2} = \frac{(C-B) + (D-A)}{2}$. Since $AD \parallel BC$, both $C-B$ and $D-A$ are parallel to the bases of the trapezoid, so $\vec{v}$ is also parallel to the bases. Let $\vec{w}$ be the unit vector in the direction of the bases. Then $\vec{v} = v \vec{w}$ for some scalar $v$.
The value $L_1 (\vec{w} \cdot \vec{u_1})$ is the projection of $L_1 \vec{w}$ onto the inward normal $\vec{u_1}$, which is the height $H$ of the trapezoid (up to a sign). Specifically, $L_1 (\vec{w} \cdot \vec{u_1}) = H$ if $\vec{w}$ is oriented such that the interior is to its "right" relative to the leg $AB$. Similarly, $L_2 (\vec{w} \cdot \vec{u_2}) = -H$ because $\vec{u_2}$ is the inward normal to the opposite leg $CD$, and the bases are traversed in the same direction $\vec{w}$. Thus $L_1 (\vec{v} \cdot \vec{u_1}) = v H$ and $L_2 (\vec{v} \cdot \vec{u_2}) = -v H$.

Consequently, the term in the brackets $L_2 (\vec{v} \cdot \vec{u_2}) + L_1 (\vec{v} \cdot \vec{u_1}) = -vH + vH = 0$.
Thus, $O_3O_4^2 = (R_3 \pm R_4)^2$, meaning $(W_3)$ and $(W_4)$ are tangent. \(\square\)
