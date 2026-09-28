# Problem

Given a trapezoid $ABCD$ with $AB,CD$ as the two legs. Circle $(W_{1})$ passes through $A,B$, and $(W_{2})$ passes through $C,D$ so that they are tangent to each other. The inscribed angle on circle $W_1$ corresponding to the arc AB on the side opposite to C and D is alpha, and the inscribed angle on circle $W_2$ corresponding to the arc CD on the side opposite to  A and B is beta. Construct $(W_{3})$ passing through $A,B$, $(W_{4})$ passing through $C,D$ such that the inscribed angle on circle W3 corresponding to the arc AB on the side opposite to C and D is $\beta$, and the inscribed angle on circle $W_4$ corresponding to the arc CD on the side opposite to  A and B is b $\alpha$. Prove that $(W_{3}),(W_{4})$ are tangent to each other.

# Proof A

1: To prove that the circles $(W_3)$ and $(W_4)$ are tangent to each other, we employ a coordinate geometry approach to analyze the conditions for the tangency of the circles.
2: 
3: ### 1. Coordinate Setup and Circle Geometry
4: Let the trapezoid $ABCD$ have parallel bases $AD$ and $BC$, with $AB$ and $CD$ as the legs. We define the coordinates of the vertices as $A(0, h)$, $D(a, h)$, $B(b, 0)$, and $C(c, 0)$. The height of the trapezoid is $h$. Let $M_1$ and $M_2$ be the midpoints of the legs $AB$ and $CD$ respectively:
5: \[ M_1 = \left(\frac{b}{2}, \frac{h}{2}\right), \quad M_2 = \left(\frac{a+c}{2}, \frac{h}{2}\right) \]
6: Let $\vec{V} = M_1 - M_2 = \left(\frac{b-a-c}{2}, 0\right)$.
7: 
8: For circle $(W_1)$ passing through $A$ and $B$, let $\alpha$ be the inscribed angle corresponding to the arc $AB$ on the side opposite to $C$ and $D$. The radius of $(W_1)$ is $R_1 = \frac{AB}{2\sin\alpha}$. The distance from the midpoint $M_1$ to the center $O_1$ is $d_1 = \frac{AB}{2}\cot\alpha$. Let $\vec{n}_1$ be the unit normal vector to $AB$ pointing toward the interior of the trapezoid (the side containing $C$ and $D$):
9: \[ \vec{n}_1 = \frac{(h, b)}{\sqrt{h^2+b^2}} \]
10: The center is $O_1 = M_1 + d_1 \vec{n}_1$.
11: 
12: Similarly, for circle $(W_2)$ passing through $C$ and $D$ with inscribed angle $\beta$ corresponding to the arc $CD$ on the side opposite to $A$ and $B$, the radius is $R_2 = \frac{CD}{2\sin\beta}$. Let $\vec{n}_2$ be the unit normal vector to $CD$ pointing toward the interior of the trapezoid (the side containing $A$ and $B$):
13: \[ \vec{n}_2 = \frac{(-h, a-c)}{\sqrt{h^2+(a-c)^2}} \]
14: The distance from $M_2$ to $O_2$ is $d_2 = \frac{CD}{2}\cot\beta$. Thus, $O_2 = M_2 + d_2 \vec{n}_2$.
15: 
16: ### 2. Condition for Tangency of $(W_1)$ and $(W_2)$
17: Circles $(W_1)$ and $(W_2)$ are tangent if the distance between their centers $O_1O_2$ satisfies $O_1O_2 = R_1 + R_2$ (external tangency) or $O_1O_2 = |R_1 - R_2|$ (internal tangency). In either case, this is equivalent to:
18: \[ O_1O_2^2 - (R_1^2 + R_2^2) = \pm 2R_1R_2 \]
19: The vector between centers is $O_1 - O_2 = \vec{V} + d_1 \vec{n}_1 - d_2 \vec{n}_2$. Squaring the distance:
20: \[ O_1O_2^2 = V^2 + d_1^2 + d_2^2 + 2d_1(\vec{V} \cdot \vec{n}_1) - 2d_2(\vec{V} \cdot \vec{n}_2) - 2d_1d_2(\vec{n}_1 \cdot \vec{n}_2) \]
21: Since $R_1^2 = d_1^2 + (AB/2)^2$ and $R_2^2 = d_2^2 + (CD/2)^2$, the tangency condition becomes:
22: \[ L_1 = V^2 - \frac{AB^2+CD^2}{4} + 2d_1(\vec{V} \cdot \vec{n}_1) - 2d_2(\vec{V} \cdot \vec{n}_2) - 2d_1d_2(\vec{n}_1 \cdot \vec{n}_2) = \pm \frac{AB \cdot CD}{2\sin\alpha\sin\beta} \]
23: 
24: ### 3. Tangency of $(W_3)$ and $(W_4)$
25: Circles $(W_3)$ and $(W_4)$ are constructed by swapping $\alpha$ and $\beta$. Their centers are $O_3 = M_1 + d_3 \vec{n}_1$ and $O_4 = M_2 + d_4 \vec{n}_2$, where $d_3 = \frac{AB}{2}\cot\beta$ and $d_4 = \frac{CD}{2}\cot\alpha$. Their radii are $R_3 = \frac{AB}{2\sin\beta}$ and $R_4 = \frac{CD}{2\sin\alpha}$.
26: The tangency condition for $(W_3, W_4)$ is:
27: \[ L_3 = O_3O_4^2 - (R_3^2 + R_4^2) = \pm 2R_3R_4 \]
28: Note that $R_3R_4 = \frac{AB \cdot CD}{4\sin\beta\sin\alpha} = R_1R_2$. The left-hand side is:
29: \[ L_3 = V^2 - \frac{AB^2+CD^2}{4} + 2d_3(\vec{V} \cdot \vec{n}_1) - 2d_4(\vec{V} \cdot \vec{n}_2) - 2d_3d_4(\vec{n}_1 \cdot \vec{n}_2) \]
30: Comparing $L_3$ with $L_1$:
31: \[ L_1 - L_3 = 2(d_1 - d_3)(\vec{V} \cdot \vec{n}_1) - 2(d_2 - d_4)(\vec{V} \cdot \vec{n}_2) - 2(d_1d_2 - d_3d_4)(\vec{n}_1 \cdot \vec{n}_2) \]
32: Substituting $d_1, d_2, d_3, d_4$:
33: \[ d_1d_2 = \frac{AB \cdot CD}{4} \cot\alpha \cot\beta, \quad d_3d_4 = \frac{AB \cdot CD}{4} \cot\beta \cot\alpha \]
34: Thus $d_1d_2 - d_3d_4 = 0$. The difference becomes:
35: \[ L_1 - L_3 = AB(\cot\alpha - \cot\beta)(\vec{V} \cdot \vec{n}_1) - CD(\cot\beta - \cot\alpha)(\vec{V} \cdot \vec{n}_2) = (\cot\alpha - \cot\beta)[AB(\vec{V} \cdot \vec{n}_1) + CD(\vec{V} \cdot \vec{n}_2)] \]
36: Calculating the dot products:
37: \[ AB(\vec{V} \cdot \vec{n}_1) = \sqrt{h^2+b^2} \left[ \left(\frac{b-a-c}{2}, 0\right) \cdot \frac{(h, b)}{\sqrt{h^2+b^2}} \right] = \frac{h(b-a-c)}{2} \]
38: \[ CD(\vec{V} \cdot \vec{n}_2) = \sqrt{h^2+(a-c)^2} \left[ \left(\frac{b-a-c}{2}, 0\right) \cdot \frac{(-h, a-c)}{\sqrt{h^2+(a-c)^2}} \right] = \frac{-h(b-a-c)}{2} \]
39: Since $AB(\vec{V} \cdot \vec{n}_1) + CD(\vec{V} \cdot \vec{n}_2) = 0$, we have $L_1 = L_3$. Thus, the tangency condition for $(W_3, W_4)$ is identical to that of $(W_1, W_2)$. Since $(W_1, W_2)$ are tangent, $(W_3, W_4)$ must also be tangent.

# Proof B

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
