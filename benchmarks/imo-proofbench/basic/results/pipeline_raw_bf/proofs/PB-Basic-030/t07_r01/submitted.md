To prove that the circles $(W_3)$ and $(W_4)$ are tangent to each other, we employ a vector-based approach to describe the centers and radii of the circles involved.

### 1. Setup and Coordinate System
Let the trapezoid $ABCD$ have parallel sides $AD$ and $BC$. Thus, $AB$ and $CD$ are the legs. Let $h$ be the height of the trapezoid. We set up a coordinate system such that the parallel bases lie on horizontal lines: $A = (x_A, h)$, $D = (x_D, h)$, $B = (x_B, 0)$, and $C = (x_C, 0)$.
Let $L_1 = AB$ and $L_2 = CD$ be the lengths of the legs. Let $M_1$ and $M_2$ be the midpoints of $AB$ and $CD$, respectively:
$M_1 = \left(\frac{x_A+x_B}{2}, \frac{h}{2}\right), \quad M_2 = \left(\frac{x_C+x_D}{2}, \frac{h}{2}\right)$.
The vector connecting the midpoints is $\vec{m} = \vec{M_1 M_2} = \left(\frac{x_C+x_D-x_A-x_B}{2}, 0\right)$.

### 2. Centers and Radii of the Circles
Let $\vec{n_1}$ be the unit normal vector to $AB$ pointing towards the interior of the trapezoid (towards $CD$), and $\vec{n_2}$ be the unit normal to $CD$ pointing towards the interior (towards $AB$).
The center $O_1$ of $(W_1)$ passes through $A$ and $B$. The inscribed angle $\alpha$ subtended by arc $AB$ on the side opposite to $C, D$ implies that the distance from $M_1$ to $O_1$ is $\frac{L_1}{2} \cot \alpha$. Thus:
$O_1 = M_1 + \frac{L_1}{2} \cot \alpha \vec{n_1}, \quad R_1 = \frac{L_1}{2 \sin \alpha}$.
Similarly, for $(W_2)$ passing through $C, D$ with inscribed angle $\beta$:
$O_2 = M_2 + \frac{L_2}{2} \cot \beta \vec{n_2}, \quad R_2 = \frac{L_2}{2 \sin \beta}$.
For the constructed circles $(W_3)$ and $(W_4)$, the inscribed angles are swapped:
$O_3 = M_1 + \frac{L_1}{2} \cot \beta \vec{n_1}, \quad R_3 = \frac{L_1}{2 \sin \beta}$
$O_4 = M_2 + \frac{L_2}{2} \cot \alpha \vec{n_2}, \quad R_4 = \frac{L_2}{2 \sin \alpha}$.

### 3. The Tangency Condition
Two circles are tangent if the distance between their centers satisfies $|O_i - O_j|^2 = (R_i \pm R_j)^2 = R_i^2 + R_j^2 \pm 2R_i R_j$.
Let $k_1 = L_1/2$ and $k_2 = L_2/2$. For $(W_1)$ and $(W_2)$:
$O_1 - O_2 = \vec{m} + k_1 \cot \alpha \vec{n_1} - k_2 \cot \beta \vec{n_2}$.
Expanding the square of the distance:
$|O_1 - O_2|^2 = m^2 + k_1^2 \cot^2 \alpha + k_2^2 \cot^2 \beta + 2k_1 \cot \alpha (\vec{m} \cdot \vec{n_1}) - 2k_2 \cot \beta (\vec{m} \cdot \vec{n_2}) - 2k_1 k_2 \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2})$.
Using $R_1^2 = k_1^2(1 + \cot^2 \alpha)$ and $R_2^2 = k_2^2(1 + \cot^2 \beta)$, we have:
$|O_1 - O_2|^2 - (R_1^2 + R_2^2) = m^2 - k_1^2 - k_2^2 + 2k_1 \cot \alpha (\vec{m} \cdot \vec{n_1}) - 2k_2 \cot \beta (\vec{m} \cdot \vec{n_2}) - 2k_1 k_2 \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2})$.
Similarly, for $(W_3)$ and $(W_4)$:
$|O_3 - O_4|^2 - (R_3^2 + R_4^2) = m^2 - k_1^2 - k_2^2 + 2k_1 \cot \beta (\vec{m} \cdot \vec{n_1}) - 2k_2 \cot \alpha (\vec{m} \cdot \vec{n_2}) - 2k_1 k_2 \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2})$.

### 4. Proof of Equality
The difference between these two expressions is:
$\Delta = 2(\cot \alpha - \cot \beta) [k_1 (\vec{m} \cdot \vec{n_1}) + k_2 (\vec{m} \cdot \vec{n_2})]$.
We calculate the dot products using $\vec{n_1} = \frac{(h, x_B-x_A)}{L_1}$ and $\vec{n_2} = \frac{(-h, x_D-x_C)}{L_2}$:
$k_1 (\vec{m} \cdot \vec{n_1}) = \frac{L_1}{2} \left( \frac{x_C+x_D-x_A-x_B}{2} \cdot \frac{h}{L_1} \right) = \frac{h(x_C+x_D-x_A-x_B)}{4}$.
$k_2 (\vec{m} \cdot \vec{n_2}) = \frac{L_2}{2} \left( \frac{x_C+x_D-x_A-x_B}{2} \cdot \frac{-h}{L_2} \right) = \frac{-h(x_C+x_D-x_A-x_B)}{4}$.
Thus, $k_1 (\vec{m} \cdot \vec{n_1}) + k_2 (\vec{m} \cdot \vec{n_2}) = 0$, which means $\Delta = 0$.
Consequently, $|O_3 - O_4|^2 - (R_3^2 + R_4^2) = |O_1 - O_2|^2 - (R_1^2 + R_2^2) = \pm 2R_1 R_2$.
Since $R_1 R_2 = \frac{k_1 k_2}{\sin \alpha \sin \beta} = R_3 R_4$, it follows that:
$|O_3 - O_4|^2 = R_3^2 + R_4^2 \pm 2R_3 R_4 = (R_3 \pm R_4)^2$.
Therefore, $(W_3)$ and $(W_4)$ are tangent to each other. $\square$
