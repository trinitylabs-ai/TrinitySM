# Problem

Given a trapezoid $ABCD$ with $AB,CD$ as the two legs. Circle $(W_{1})$ passes through $A,B$, and $(W_{2})$ passes through $C,D$ so that they are tangent to each other. The inscribed angle on circle $W_1$ corresponding to the arc AB on the side opposite to C and D is alpha, and the inscribed angle on circle $W_2$ corresponding to the arc CD on the side opposite to  A and B is beta. Construct $(W_{3})$ passing through $A,B$, $(W_{4})$ passing through $C,D$ such that the inscribed angle on circle W3 corresponding to the arc AB on the side opposite to C and D is $\beta$, and the inscribed angle on circle $W_4$ corresponding to the arc CD on the side opposite to  A and B is b $\alpha$. Prove that $(W_{3}),(W_{4})$ are tangent to each other.

# Proof A

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
