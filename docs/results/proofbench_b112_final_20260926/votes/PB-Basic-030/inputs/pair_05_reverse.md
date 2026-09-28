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

1: To prove that the circles $(W_3)$ and $(W_4)$ are tangent to each other, we employ a coordinate geometry approach.
2: 
3: ### 1. Coordinate Setup
4: Let the trapezoid $ABCD$ have parallel bases $AD$ and $BC$. Let the height of the trapezoid be $h$. We set up a coordinate system such that the bases lie on the lines $y=h$ and $y=0$. Let the vertices be:
5: $A = (x_A, h), \quad D = (x_D, h), \quad B = (x_B, 0), \quad C = (x_C, 0)$.
6: The legs are $AB$ and $CD$. Let $L_1$ and $L_2$ be their lengths:
7: $L_1^2 = (x_B - x_A)^2 + h^2, \quad L_2^2 = (x_C - x_D)^2 + h^2$.
8: Let $X = x_B - x_A$ and $Y = x_C - x_D$.
9: 
10: ### 2. Centers and Radii of the Circles
11: For a circle passing through two points $P, Q$ with an inscribed angle $\theta$ corresponding to the arc $PQ$ on the side opposite to a point $R$, the radius is $R = \frac{PQ}{2 \sin \theta}$. The center $O$ is located at $M \pm \frac{\cot \theta}{2} \vec{n}$, where $M$ is the midpoint of $PQ$ and $\vec{n}$ is a vector perpendicular to $\vec{PQ}$ pointing toward the side of $R$.
12: 
13: For $(W_1)$ passing through $A, B$ with inscribed angle $\alpha$:
14: $R_1 = \frac{L_1}{2 \sin \alpha}, \quad M_1 = \left(\frac{x_A+x_B}{2}, \frac{h}{2}\right), \quad \vec{AB} = (X, -h), \quad \vec{n_1} = (h, X)$.
15: The center is $O_1 = M_1 + \frac{\cot \alpha}{2} \vec{n_1}$.
16: 
17: For $(W_2)$ passing through $C, D$ with inscribed angle $\beta$:
18: $R_2 = \frac{L_2}{2 \sin \beta}, \quad M_2 = \left(\frac{x_C+x_D}{2}, \frac{h}{2}\right), \quad \vec{DC} = (Y, -h), \quad \vec{n_2} = (h, Y)$.
19: The center is $O_2 = M_2 - \frac{\cot \beta}{2} \vec{n_2}$.
20: 
21: ### 3. The Tangency Condition
22: Let $u = \cot \alpha$ and $v = \cot \beta$. Then $R_1 = \frac{L_1}{2}\sqrt{1+u^2}$ and $R_2 = \frac{L_2}{2}\sqrt{1+v^2}$.
23: Let $\vec{S} = M_2 - M_1 = \left(\frac{x_C+x_D-x_A-x_B}{2}, 0\right)$.
24: The distance between centers $O_1$ and $O_2$ is:
25: $O_1 - O_2 = -\vec{S} + \frac{u}{2}\vec{n_1} + \frac{v}{2}\vec{n_2}$.
26: The circles $(W_1)$ and $(W_2)$ are tangent if $O_1O_2 = R_1 \pm R_2$, which is equivalent to $O_1O_2^2 - (R_1^2 + R_2^2) = \pm 2R_1R_2$.
27: Expanding the distance:
28: $4O_1O_2^2 = |-2\vec{S} + u\vec{n_1} + v\vec{n_2}|^2 = 4S^2 + u^2L_1^2 + v^2L_2^2 - 4\vec{S} \cdot (u\vec{n_1} + v\vec{n_2}) + 2uv(\vec{n_1} \cdot \vec{n_2})$.
29: Since $\vec{S} = (s, 0)$ and $\vec{n_1} = (h, X), \vec{n_2} = (h, Y)$, we have $\vec{S} \cdot \vec{n_1} = \vec{S} \cdot \vec{n_2} = sh$.
30: $4O_1O_2^2 = 4S^2 + u^2L_1^2 + v^2L_2^2 - 4sh(u+v) + 2uv(\vec{n_1} \cdot \vec{n_2})$.
31: Subtracting $4(R_1^2 + R_2^2) = L_1^2(1+u^2) + L_2^2(1+v^2)$:
32: $4(O_1O_2^2 - (R_1^2 + R_2^2)) = 4S^2 - 4sh(u+v) + 2uv(\vec{n_1} \cdot \vec{n_2}) - (L_1^2 + L_2^2)$.
33: Let $f(u, v) = 4S^2 - 4sh(u+v) + 2uv(\vec{n_1} \cdot \vec{n_2}) - (L_1^2 + L_2^2)$.
34: The tangency condition for $(W_1)$ and $(W_2)$ is $f(u, v) = \pm 8R_1R_2 = \pm 2L_1L_2\sqrt{1+u^2}\sqrt{1+v^2}$.
35: 
36: ### 4. Proof for $(W_3)$ and $(W_4)$
37: For $(W_3)$ and $(W_4)$, the inscribed angles are swapped: $\alpha \to \beta$ and $\beta \to \alpha$. This means $u \to v$ and $v \to u$.
38: The radius and center formulas for $(W_3, W_4)$ are:
39: $R_3 = \frac{L_1}{2}\sqrt{1+v^2}, \quad R_4 = \frac{L_2}{2}\sqrt{1+u^2}, \quad O_3 = M_1 + \frac{v}{2}\vec{n_1}, \quad O_4 = M_2 - \frac{u}{2}\vec{n_2}$.
40: The distance between centers $O_3$ and $O_4$ is:
41: $O_3 - O_4 = -\vec{S} + \frac{v}{2}\vec{n_1} + \frac{u}{2}\vec{n_2}$.
42: Thus, $4(O_3O_4^2 - (R_3^2 + R_4^2)) = f(v, u)$.
43: Observing the expression for $f(u, v)$:
44: 1. $(u+v)$ is symmetric.
45: 2. $uv(\vec{n_1} \cdot \vec{n_2})$ is symmetric.
46: Thus, $f(v, u) = f(u, v)$.
47: The tangency condition for $(W_3)$ and $(W_4)$ is $f(v, u) = \pm 8R_3R_4$.
48: $8R_3R_4 = 8 \left(\frac{L_1}{2}\sqrt{1+v^2}\right) \left(\frac{L_2}{2}\sqrt{1+u^2}\right) = 2L_1L_2\sqrt{1+v^2}\sqrt{1+u^2}$.
49: This is exactly the same as $8R_1R_2$. Since $f(u, v) = \pm 8R_1R_2$ from the tangency of $(W_1)$ and $(W_2)$, it follows that $f(v, u) = \pm 8R_3R_4$.
50: Therefore, $(W_3)$ and $(W_4)$ are tangent to each other.
