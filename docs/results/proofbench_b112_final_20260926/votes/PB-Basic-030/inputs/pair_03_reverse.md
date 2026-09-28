# Problem

Given a trapezoid $ABCD$ with $AB,CD$ as the two legs. Circle $(W_{1})$ passes through $A,B$, and $(W_{2})$ passes through $C,D$ so that they are tangent to each other. The inscribed angle on circle $W_1$ corresponding to the arc AB on the side opposite to C and D is alpha, and the inscribed angle on circle $W_2$ corresponding to the arc CD on the side opposite to  A and B is beta. Construct $(W_{3})$ passing through $A,B$, $(W_{4})$ passing through $C,D$ such that the inscribed angle on circle W3 corresponding to the arc AB on the side opposite to C and D is $\beta$, and the inscribed angle on circle $W_4$ corresponding to the arc CD on the side opposite to  A and B is b $\alpha$. Prove that $(W_{3}),(W_{4})$ are tangent to each other.

# Proof A

1: Let $ABCD$ be a trapezoid with $AB$ and $CD$ as its legs, which implies that the bases $AD$ and $BC$ are parallel. Let $h$ be the height of the trapezoid. We set up a coordinate system such that $B = (a, 0)$, $C = (b, 0)$, $A = (0, h)$, and $D = (c, h)$. The lengths of the legs are $L_{AB} = \sqrt{a^2 + h^2}$ and $L_{CD} = \sqrt{(c-b)^2 + h^2}$.
2: 
3: Let $M_1 = \left(\frac{a}{2}, \frac{h}{2}\right)$ and $M_2 = \left(\frac{b+c}{2}, \frac{h}{2}\right)$ be the midpoints of $AB$ and $CD$, respectively. Let $\vec{n_1}$ be the unit normal to $AB$ pointing toward the side containing $C$ and $D$, and $\vec{n_2}$ be the unit normal to $CD$ pointing toward the side containing $A$ and $B$.
4: The vector $\vec{AB} = (a, -h)$, so a normal vector is $(h, a)$. The line $AB$ is given by $hx + ay - ah = 0$. For $C(b, 0)$, the expression is $h(b-a)$, and for $D(c, h)$, it is $hc$. Assuming $h > 0, c > 0, b > a$, these are positive, so $\vec{n_1} = \frac{1}{L_{AB}}(h, a)$ points toward $C$ and $D$.
5: The vector $\vec{CD} = (c-b, h)$, so a normal vector is $(-h, c-b)$. The line $CD$ is given by $-hx + (c-b)y + hb = 0$. For $A(0, h)$, the expression is $(c-b)h + hb = ch$, and for $B(a, 0)$, it is $-ha + hb = h(b-a)$. These are positive, so $\vec{n_2} = \frac{1}{L_{CD}}(-h, c-b)$ points toward $A$ and $B$.
6: 
7: The inscribed angle $\alpha$ on $(W_1)$ corresponding to arc $AB$ on the side opposite to $C, D$ implies that the center $O_1$ is located at $O_1 = M_1 + d_1 \vec{n_1}$ where $d_1 = \frac{L_{AB}}{2} \cot \alpha$. The radius is $R_1 = \frac{L_{AB}}{2 \sin \alpha}$. Similarly, for $(W_2)$, $O_2 = M_2 + d_2 \vec{n_2}$ where $d_2 = \frac{L_{CD}}{2} \cot \beta$ and $R_2 = \frac{L_{CD}}{2 \sin \beta}$.
8: For $(W_3)$ and $(W_4)$, the centers and radii are:
9: $O_3 = M_1 + d_3 \vec{n_1}$ with $d_3 = \frac{L_{AB}}{2} \cot \beta$ and $R_3 = \frac{L_{AB}}{2 \sin \beta}$.
10: $O_4 = M_2 + d_4 \vec{n_2}$ with $d_4 = \frac{L_{CD}}{2} \cot \alpha$ and $R_4 = \frac{L_{CD}}{2 \sin \alpha}$.
11: 
12: Let $\vec{m} = \vec{M_1 M_2} = \left(\frac{b+c-a}{2}, 0\right)$. The squared distance between $O_1$ and $O_2$ is:
13: \[ O_1 O_2^2 = |\vec{m} + d_2 \vec{n_2} - d_1 \vec{n_1}|^2 = m^2 + d_1^2 + d_2^2 + 2 d_2 (\vec{m} \cdot \vec{n_2}) - 2 d_1 (\vec{m} \cdot \vec{n_1}) - 2 d_1 d_2 (\vec{n_1} \cdot \vec{n_2}) \]
14: Similarly, for $O_3$ and $O_4$:
15: \[ O_3 O_4^2 = |\vec{m} + d_4 \vec{n_2} - d_3 \vec{n_1}|^2 = m^2 + d_3^2 + d_4^2 + 2 d_4 (\vec{m} \cdot \vec{n_2}) - 2 d_3 (\vec{m} \cdot \vec{n_1}) - 2 d_3 d_4 (\vec{n_1} \cdot \vec{n_2}) \]
16: Note that $d_1 d_2 = \frac{L_{AB} L_{CD}}{4} \cot \alpha \cot \beta = d_3 d_4$, so the term involving $(\vec{n_1} \cdot \vec{n_2})$ cancels when subtracting.
17: The linear terms are $2(d_2 - d_4)(\vec{m} \cdot \vec{n_2}) - 2(d_1 - d_3)(\vec{m} \cdot \vec{n_1})$.
18: We have $\vec{m} \cdot \vec{n_1} = \frac{b+c-a}{2} \frac{h}{L_{AB}}$ and $\vec{m} \cdot \vec{n_2} = \frac{b+c-a}{2} \frac{-h}{L_{CD}}$.
19: Substituting $d_i$:
20: \[ 2 \frac{L_{CD}}{2}(\cot \beta - \cot \alpha) \frac{-(b+c-a)h}{2 L_{CD}} - 2 \frac{L_{AB}}{2}(\cot \alpha - \cot \beta) \frac{(b+c-a)h}{2 L_{AB}} = \frac{-(b+c-a)h}{2} (\cot \beta - \cot \alpha + \cot \alpha - \cot \beta) = 0 \]
21: Thus, $O_1 O_2^2 - O_3 O_4^2 = (d_1^2 - d_3^2) + (d_2^2 - d_4^2) = \frac{L_{AB}^2}{4}(\cot^2 \alpha - \cot^2 \beta) + \frac{L_{CD}^2}{4}(\cot^2 \beta - \cot^2 \alpha) = \frac{1}{4}(L_{AB}^2 - L_{CD}^2)(\cot^2 \alpha - \cot^2 \beta)$.
22: 
23: Now consider the radii. Since $R_1 R_2 = \frac{L_{AB} L_{CD}}{4 \sin \alpha \sin \beta} = R_3 R_4$, the difference between the squared sums/differences of radii is:
24: \[ (R_1 \pm R_2)^2 - (R_3 \pm R_4)^2 = R_1^2 + R_2^2 - (R_3^2 + R_4^2) = \frac{L_{AB}^2}{4 \sin^2 \alpha} + \frac{L_{CD}^2}{4 \sin^2 \beta} - \frac{L_{AB}^2}{4 \sin^2 \beta} - \frac{L_{CD}^2}{4 \sin^2 \alpha} \]
25: \[ = \frac{L_{AB}^2}{4}(\csc^2 \alpha - \csc^2 \beta) + \frac{L_{CD}^2}{4}(\csc^2 \beta - \csc^2 \alpha) = \frac{1}{4}(L_{AB}^2 - L_{CD}^2)(\cot^2 \alpha - \cot^2 \beta) \]
26: We have shown that $O_1 O_2^2 - (R_1 \pm R_2)^2 = O_3 O_4^2 - (R_3 \pm R_4)^2$. Since $(W_1)$ and $(W_2)$ are tangent, $O_1 O_2^2 = (R_1 \pm R_2)^2$ for some choice of sign. It follows that $O_3 O_4^2 = (R_3 \pm R_4)^2$, meaning $(W_3)$ and $(W_4)$ are tangent.

# Proof B

1: Let the trapezoid $ABCD$ have parallel bases $AD$ and $BC$, and legs $AB$ and $CD$. Let $c_1 = AB$ and $c_2 = CD$, and let $u = c_1/2$ and $v = c_2/2$. We define a coordinate system such that $A = (x_A, h)$, $D = (x_D, h)$, $B = (x_B, 0)$, and $C = (x_C, 0)$, where $h$ is the height of the trapezoid.
2: 
3: The midpoints of the legs are $M_1 = \left(\frac{x_A+x_B}{2}, \frac{h}{2}\right)$ and $M_2 = \left(\frac{x_C+x_D}{2}, \frac{h}{2}\right)$. Let $\vec{M} = M_1 - M_2 = \left(\frac{x_A+x_B-x_C-x_D}{2}, 0\right)$.
4: Let $\vec{n_1}$ and $\vec{n_2}$ be unit vectors perpendicular to the legs $AB$ and $CD$, respectively, pointing inward toward the interior of the trapezoid. The vector $\vec{AB} = (x_B-x_A, -h)$, so the inward normal is $\vec{n_1} = \frac{1}{c_1}(h, x_B-x_A)$. The vector $\vec{CD} = (x_D-x_C, h)$, so the inward normal is $\vec{n_2} = \frac{1}{c_2}(-h, x_D-x_C)$.
5: 
6: For circle $(W_1)$, the inscribed angle $\alpha$ corresponds to the arc $AB$ on the side opposite to $C$ and $D$. This implies that the arc $AB$ not containing $C$ and $D$ has measure $2\alpha$. The center $O_1$ of $(W_1)$ must therefore lie on the side of the chord $AB$ that contains the interior of the trapezoid. The distance from $O_1$ to the midpoint $M_1$ is $d_1 = u \cot \alpha$, and the radius is $R_1 = u \csc \alpha$. Thus, $O_1 = M_1 + u \cot \alpha \vec{n_1}$. Similarly, for $(W_2)$, the inscribed angle $\beta$ corresponds to the arc $CD$ on the side opposite to $A$ and $B$, so $O_2 = M_2 + v \cot \beta \vec{n_2}$ and $R_2 = v \csc \beta$.
7: 
8: The condition that $(W_1)$ and $(W_2)$ are tangent is $|O_1 - O_2|^2 = (R_1 + \epsilon R_2)^2$ for some $\epsilon \in \{1, -1\}$ (where $\epsilon=1$ denotes external tangency and $\epsilon=-1$ denotes internal tangency):
9: \[ |\vec{M} + u \cot \alpha \vec{n_1} - v \cot \beta \vec{n_2}|^2 = (u \csc \alpha + \epsilon v \csc \beta)^2 \]
10: Expanding the left side:
11: \[ M^2 + u^2 \cot^2 \alpha + v^2 \cot^2 \beta + 2u \cot \alpha (\vec{M} \cdot \vec{n_1}) - 2v \cot \beta (\vec{M} \cdot \vec{n_2}) - 2uv \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2}) \]
12: Expanding the right side:
13: \[ u^2 \csc^2 \alpha + v^2 \csc^2 \beta + 2\epsilon uv \csc \alpha \csc \beta \]
14: Using the identity $\csc^2 \theta - \cot^2 \theta = 1$, the tangency condition simplifies to:
15: \[ M^2 + 2u \cot \alpha (\vec{M} \cdot \vec{n_1}) - 2v \cot \beta (\vec{M} \cdot \vec{n_2}) - 2uv \cot \alpha \cot \beta (\vec{n_1} \cdot \vec{n_2}) = u^2 + v^2 + \frac{2\epsilon uv}{\sin \alpha \sin \beta} \]
16: 
17: Now consider circles $(W_3)$ and $(W_4)$. By the problem statement, $(W_3)$ passes through $A, B$ with inscribed angle $\beta$, and $(W_4)$ passes through $C, D$ with inscribed angle $\alpha$. Their centers and radii are $O_3 = M_1 + u \cot \beta \vec{n_1}, R_3 = u \csc \beta$ and $O_4 = M_2 + v \cot \alpha \vec{n_2}, R_4 = v \csc \alpha$. They are tangent if there exists $\epsilon' \in \{1, -1\}$ such that:
18: \[ M^2 + 2u \cot \beta (\vec{M} \cdot \vec{n_1}) - 2v \cot \alpha (\vec{M} \cdot \vec{n_2}) - 2uv \cot \beta \cot \alpha (\vec{n_1} \cdot \vec{n_2}) = u^2 + v^2 + \frac{2\epsilon' uv}{\sin \beta \sin \alpha} \]
19: Let $L_1 = \vec{M} \cdot \vec{n_1}$ and $L_2 = \vec{M} \cdot \vec{n_2}$. The difference between the left-hand sides of the two tangency conditions is:
20: \[ 2u(\cot \alpha - \cot \beta) L_1 - 2v(\cot \beta - \cot \alpha) L_2 = 2(\cot \alpha - \cot \beta) [u L_1 + v L_2] \]
21: We evaluate the term in the bracket:
22: \[ u \vec{n_1} = \frac{1}{2}(h, x_B-x_A), \quad v \vec{n_2} = \frac{1}{2}(-h, x_D-x_C) \]
23: \[ u \vec{n_1} + v \vec{n_2} = \left(0, \frac{x_B-x_A + x_D-x_C}{2}\right) \]
24: Since $\vec{M} = (M_{1x} - M_{2x}, 0)$, the dot product is:
25: \[ \vec{M} \cdot (u \vec{n_1} + v \vec{n_2}) = (M_{1x} - M_{2x}) \cdot 0 + 0 \cdot \frac{x_B-x_A + x_D-x_C}{2} = 0 \]
26: Thus, $u L_1 + v L_2 = 0$, and the left-hand sides of the conditions for $(W_1, W_2)$ and $(W_3, W_4)$ are identical. This implies:
27: \[ \frac{2\epsilon uv}{\sin \alpha \sin \beta} = \frac{2\epsilon' uv}{\sin \beta \sin \alpha} \implies \epsilon = \epsilon' \]
28: Therefore, if $(W_1)$ and $(W_2)$ are tangent, then $(W_3)$ and $(W_4)$ must also be tangent (with the same type of tangency).
