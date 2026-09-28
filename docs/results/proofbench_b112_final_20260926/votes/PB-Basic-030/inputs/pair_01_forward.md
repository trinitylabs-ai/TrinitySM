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
