To prove that the circles $(W_3)$ and $(W_4)$ are tangent to each other, we employ a vector-based approach to describe the centers and radii of the circles.

### 1. Setup and Coordinate System
Let the trapezoid $ABCD$ have parallel bases $AD$ and $BC$. Thus, $AB$ and $CD$ are the legs. Let $h$ be the height of the trapezoid. We set up a coordinate system such that the parallel bases lie on horizontal lines: $A = (x_A, h)$, $D = (x_D, h)$, $B = (x_B, 0)$, and $C = (x_C, 0)$.
Let $L_1 = AB$ and $L_2 = CD$ be the lengths of the legs. Let $M_1$ and $M_2$ be the midpoints of $AB$ and $CD$, respectively:
$M_1 = \left(\frac{x_A+x_B}{2}, \frac{h}{2}\right), \quad M_2 = \left(\frac{x_C+x_D}{2}, \frac{h}{2}\right)$.
The vector connecting the midpoints is $\vec{m} = \vec{M_1 M_2} = \left(\frac{x_C+x_D-x_A-x_B}{2}, 0\right)$.

### 2. Centers and Radii of the Circles
Let $\vec{n_1}$ be the unit normal vector to $AB$ pointing towards the interior of the trapezoid (towards the side containing $CD$), and $\vec{n_2}$ be the unit normal to $CD$ pointing towards the interior (towards the side containing $AB$).
The inscribed angle $\alpha$ on circle $(W_1)$ corresponding to the arc $AB$ on the side opposite to $C$ and $D$ implies that the distance from $M_1$ to the center $O_1$ is $\frac{L_1}{2} |\cot \alpha|$. The center $O_1$ lies on the side containing $C, D$ if $\alpha < 90^\circ$ and on the opposite side if $\alpha > 90^\circ$. Thus:
$O_1 = M_1 + \frac{L_1}{2} \cot \alpha \vec{n_1}, \quad R_1 = \frac{L_1}{2 \sin \alpha}$.
Similarly, for $(W_2)$ passing through $C, D$ with inscribed angle $\beta$:
$O_2 = M_2 + \frac{L_2}{2} \cot \beta \vec{n_2}, \quad R_2 = \frac{L_2}{2 \sin \beta}$.
For the constructed circles $(W_3)$ and $(W_4)$, the inscribed angles are swapped:
$O_3 = M_1 + \frac{L_1}{2} \cot \beta \vec{n_1}, \quad R_3 = \frac{L_1}{2 \sin \beta}$
$O_4 = M_2 + \frac{L_2}{2} \cot \alpha \vec{n_2}, \quad R_4 = \frac{L_2}{2 \sin \alpha}$.

### 3. The Tangency Condition
Two circles are tangent if the distance between their centers satisfies $|O_i - O_j|^2 = (R_i \pm R_j)^2 = R_i^2 + R_j^2 \pm 2R_i R_j$.
For $(W_1)$ and $(W_2)$, we have $O_1 - O_2 = (M_1 - M_2) + \frac{L_1}{2} \cot \alpha \vec{n_1} - \frac{L_2}{2} \cot \beta \vec{n_2} = -\vec{m} + \frac{L_1}{2} \cot \alpha \vec{n_1} - \frac{L_2}{2} \cot \beta \vec{n_2}$.
Expanding the square of the distance:
$|O_1 - O_2|^2 = m^2 + \frac{L_1^2}{4} \cot^2 \alpha + \frac{L_2^2}{4} \cot^2 \beta - 2\vec{m} \cdot \left(\frac{L_1}{2} \cot \alpha \vec{n_1} - \frac{L_2}{2} \cot \beta \vec{n_2}\right) - \frac{L_1 L_2}{2} \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2})$.
Using $R_1^2 = \frac{L_1^2}{4}(1 + \cot^2 \alpha)$ and $R_2^2 = \frac{L_2^2}{4}(1 + \cot^2 \beta)$, we have:
$|O_1 - O_2|^2 - (R_1^2 + R_2^2) = m^2 - \frac{L_1^2}{4} - \frac{L_2^2}{4} - L_1 \cot \alpha (\vec{m} \cdot \vec{n_1}) + L_2 \cot \beta (\vec{m} \cdot \vec{n_2}) - \frac{L_1 L_2}{2} \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2})$.
Similarly, for $(W_3)$ and $(W_4)$:
$|O_3 - O_4|^2 - (R_3^2 + R_4^2) = m^2 - \frac{L_1^2}{4} - \frac{L_2^2}{4} - L_1 \cot \beta (\vec{m} \cdot \vec{n_1}) + L_2 \cot \alpha (\vec{m} \cdot \vec{n_2}) - \frac{L_1 L_2}{2} \cot \beta \cot \alpha (\vec{n_1} \cdot \vec{n_2})$.

### 4. Proof of Equality
The difference between these two expressions is:
$\Delta = (|O_1 - O_2|^2 - (R_1^2 + R_2^2)) - (|O_3 - O_4|^2 - (R_3^2 + R_4^2)) = - (\cot \alpha - \cot \beta) [L_1 (\vec{m} \cdot \vec{n_1}) + L_2 (\vec{m} \cdot \vec{n_2})]$.
Let $m_x$ be the x-component of $\vec{m}$. The inward normal $\vec{n_1}$ to $AB$ is $\frac{\text{sgn}(m_x)}{L_1} (h, x_B-x_A)$ and the inward normal $\vec{n_2}$ to $CD$ is $\frac{\text{sgn}(m_x)}{L_2} (-h, x_D-x_C)$.
Then $L_1 (\vec{m} \cdot \vec{n_1}) = m_x \cdot \text{sgn}(m_x) \cdot h = |m_x| h$ and $L_2 (\vec{m} \cdot \vec{n_2}) = m_x \cdot \text{sgn}(m_x) \cdot (-h) = -|m_x| h$.
Thus $L_1 (\vec{m} \cdot \vec{n_1}) + L_2 (\vec{m} \cdot \vec{n_2}) = 0$, which means $\Delta = 0$.
Consequently, $|O_3 - O_4|^2 - (R_3^2 + R_4^2) = |O_1 - O_2|^2 - (R_1^2 + R_2^2)$.
Since $(W_1)$ and $(W_2)$ are tangent, $|O_1 - O_2|^2 - (R_1^2 + R_2^2) = \pm 2R_1 R_2$.
Substituting this into the equality, we obtain:
$|O_3 - O_4|^2 - (R_3^2 + R_4^2) = \pm 2R_1 R_2$.
Since $R_1 R_2 = \frac{L_1 L_2}{4 \sin \alpha \sin \beta}$ and $R_3 R_4 = \frac{L_1 L_2}{4 \sin \beta \sin \alpha}$, we have $R_1 R_2 = R_3 R_4$. It follows that:
$|O_3 - O_4|^2 = R_3^2 + R_4^2 \pm 2R_3 R_4 = (R_3 \pm R_4)^2$.
Therefore, $(W_3)$ and $(W_4)$ are tangent to each other.
