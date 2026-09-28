# Problem

Given a trapezoid $ABCD$ with $AB,CD$ as the two legs. Circle $(W_{1})$ passes through $A,B$, and $(W_{2})$ passes through $C,D$ so that they are tangent to each other. The inscribed angle on circle $W_1$ corresponding to the arc AB on the side opposite to C and D is alpha, and the inscribed angle on circle $W_2$ corresponding to the arc CD on the side opposite to  A and B is beta. Construct $(W_{3})$ passing through $A,B$, $(W_{4})$ passing through $C,D$ such that the inscribed angle on circle W3 corresponding to the arc AB on the side opposite to C and D is $\beta$, and the inscribed angle on circle $W_4$ corresponding to the arc CD on the side opposite to  A and B is b $\alpha$. Prove that $(W_{3}),(W_{4})$ are tangent to each other.

# Proof A

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

# Proof B

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
