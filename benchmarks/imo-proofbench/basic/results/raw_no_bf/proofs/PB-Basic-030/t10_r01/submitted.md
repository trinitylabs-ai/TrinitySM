To prove that the circles $(W_3)$ and $(W_4)$ are tangent, we use a coordinate-based approach combined with the geometric properties of the trapezoid.

### 1. Geometric Setup and Definitions
Let $ABCD$ be a trapezoid with $AB$ and $CD$ as its legs. This implies that the bases $AD$ and $BC$ are parallel. Let $h$ be the height of the trapezoid. We set up a coordinate system where the line $BC$ is the $x$-axis and the line $AD$ is the line $y=h$.
The vertices are $A=(x_A, h)$, $B=(x_B, 0)$, $C=(x_C, 0)$, and $D=(x_D, h)$.
Let $M_1$ be the midpoint of $AB$ and $M_2$ be the midpoint of $CD$:
$M_1 = \left(\frac{x_A+x_B}{2}, \frac{h}{2}\right), \quad M_2 = \left(\frac{x_C+x_D}{2}, \frac{h}{2}\right)$.
Let $\vec{V} = M_1 - M_2 = \left(\frac{x_A+x_B-x_C-x_D}{2}, 0\right)$.

### 2. Centers of the Circles
For any circle passing through two points, its center lies on the perpendicular bisector of the segment connecting them. Let $L_1 = \frac{1}{2} AB$ and $L_2 = \frac{1}{2} CD$.
The unit normal $\vec{n}_1$ to $AB$ pointing toward the side of $C$ and $D$ is $\vec{n}_1 = \frac{1}{2L_1}(h, x_B-x_A)$.
The unit normal $\vec{n}_2$ to $CD$ pointing toward the side of $A$ and $B$ is $-\vec{n}_2 = \frac{1}{2L_2}(-h, x_D-x_C)$, or $\vec{n}_2 = \frac{1}{2L_2}(h, x_C-x_D)$.

Given the inscribed angles $\alpha$ and $\beta$, the distance from the centers to the chords are $d_1 = L_1 \cot \alpha$ and $d_2 = L_2 \cot \beta$.
The center $O_1$ of $(W_1)$ is $O_1 = M_1 + L_1 \cot \alpha \vec{n}_1$, and the center $O_2$ of $(W_2)$ is $O_2 = M_2 - L_2 \cot \beta \vec{n}_2$.
The radii are $R_1 = \frac{L_1}{\sin \alpha}$ and $R_2 = \frac{L_2}{\sin \beta}$.

### 3. Tangency Condition
Circles $(W_1)$ and $(W_2)$ are tangent if $|O_1 - O_2|^2 = (R_1 \pm R_2)^2$.
$O_1 - O_2 = \vec{V} + L_1 \cot \alpha \vec{n}_1 + L_2 \cot \beta \vec{n}_2$.
Expanding the square:
$|O_1 - O_2|^2 = V^2 + L_1^2 \cot^2 \alpha + L_2^2 \cot^2 \beta + 2\vec{V} \cdot (L_1 \cot \alpha \vec{n}_1 + L_2 \cot \beta \vec{n}_2) + 2 L_1 L_2 \cot \alpha \cot \beta (\vec{n}_1 \cdot \vec{n}_2)$.
Using $R_1^2 = L_1^2(1 + \cot^2 \alpha)$ and $R_2^2 = L_2^2(1 + \cot^2 \beta)$, the condition $|O_1 - O_2|^2 - (R_1 + R_2)^2 = 0$ becomes:
$V^2 - L_1^2 - L_2^2 + 2\vec{V} \cdot (L_1 \cot \alpha \vec{n}_1 + L_2 \cot \beta \vec{n}_2) + 2 L_1 L_2 (\cot \alpha \cot \beta (\vec{n}_1 \cdot \vec{n}_2) - \frac{1}{\sin \alpha \sin \beta}) = 0$.

### 4. Proving Tangency for $(W_3)$ and $(W_4)$
For $(W_3)$ and $(W_4)$, the roles of $\alpha$ and $\beta$ are swapped. The centers are:
$O_3 = M_1 + L_1 \cot \beta \vec{n}_1, \quad O_4 = M_2 - L_2 \cot \alpha \vec{n}_2$.
The distance $|O_3 - O_4|^2 - (R_3 + R_4)^2$ is:
$V^2 - L_1^2 - L_2^2 + 2\vec{V} \cdot (L_1 \cot \beta \vec{n}_1 + L_2 \cot \alpha \vec{n}_2) + 2 L_1 L_2 (\cot \beta \cot \alpha (\vec{n}_1 \cdot \vec{n}_2) - \frac{1}{\sin \beta \sin \alpha})$.
The difference between this expression and the one for $(W_1, W_2)$ is:
$2\vec{V} \cdot (L_1 (\cot \beta - \cot \alpha) \vec{n}_1 + L_2 (\cot \alpha - \cot \beta) \vec{n}_2) = 2(\cot \beta - \cot \alpha) \vec{V} \cdot (L_1 \vec{n}_1 - L_2 \vec{n}_2)$.
Calculating $L_1 \vec{n}_1 - L_2 \vec{n}_2$:
$L_1 \vec{n}_1 = \frac{1}{2}(h, x_B-x_A), \quad L_2 \vec{n}_2 = \frac{1}{2}(h, x_C-x_D)$.
$L_1 \vec{n}_1 - L_2 \vec{n}_2 = \left(0, \frac{x_B-x_A-x_C+x_D}{2}\right)$.
Since $\vec{V} = \left(\frac{x_A+x_B-x_C-x_D}{2}, 0\right)$, the dot product $\vec{V} \cdot (L_1 \vec{n}_1 - L_2 \vec{n}_2) = 0$.
Thus, $|O_3 - O_4|^2 - (R_3 + R_4)^2 = |O_1 - O_2|^2 - (R_1 + R_2)^2 = 0$.
Therefore, $(W_3)$ and $(W_4)$ are tangent. $\square$
