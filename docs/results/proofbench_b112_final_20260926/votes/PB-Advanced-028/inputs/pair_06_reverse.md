# Problem

Let $H$ be the orthocenter of acute triangle $ABC$, let $F$ be
 the foot of the altitude from $C$ to $AB$, and let $P$ be the reflection
 of $H$ across $BC$. Suppose that the circumcircle of triangle $AFP$
 intersects line $BC$ at two distinct points $X$ and $Y$. Prove
 that $C$ is the midpoint of $XY$.

# Proof A

1: To prove that $C$ is the midpoint of the chord $XY$, we use a coordinate geometry approach.
2: 
3: **1. Coordinate Setup**
4: Let $C$ be the origin $(0,0)$. Let the line $BC$ lie along the $x$-axis. Let the side lengths of $\triangle ABC$ be $a, b, c$ and the angles be $\alpha, \beta, \gamma$. Thus, $B = (a, 0)$ and $A = (b \cos \gamma, b \sin \gamma)$. Since the triangle is acute, $\cos \gamma > 0$.
5: 
6: **2. Coordinates of $H$ and $P$**
7: The altitude from $C$ to $AB$ is the line $CF$. The slope of $AB$ is $m_{AB} = \frac{b \sin \gamma}{b \cos \gamma - a}$. Since $CF \perp AB$, the slope of $CF$ is $m_{CF} = \frac{a - b \cos \gamma}{b \sin \gamma}$.
8: The orthocenter $H$ is the intersection of $CF$ and the altitude from $A$ to $BC$. The altitude from $A$ is the vertical line $x = b \cos \gamma$. Thus, the coordinates of $H$ are:
9: \[ H = \left( b \cos \gamma, m_{CF} \cdot b \cos \gamma \right) = \left( b \cos \gamma, \frac{(a - b \cos \gamma) \cos \gamma}{\sin \gamma} \right) \]
10: The point $P$ is the reflection of $H$ across the line $BC$ (the $x$-axis), so its coordinates are:
11: \[ P = \left( b \cos \gamma, \frac{(b \cos \gamma - a) \cos \gamma}{\sin \gamma} \right) \]
12: 
13: **3. The Center of the Circumcircle of $\triangle AFP$**
14: Let $O' = (x_0, y_0)$ be the center of the circumcircle of $\triangle AFP$. Since $A$ and $P$ share the same $x$-coordinate $b \cos \gamma$, the perpendicular bisector of $AP$ is the horizontal line $y = \frac{y_A + y_P}{2}$:
15: \[ y_0 = \frac{b \sin \gamma + \frac{b \cos^2 \gamma - a \cos \gamma}{\sin \gamma}}{2} = \frac{b \sin^2 \gamma + b \cos^2 \gamma - a \cos \gamma}{2 \sin \gamma} = \frac{b - a \cos \gamma}{2 \sin \gamma} \]
16: The center $O'$ must also satisfy $O'A^2 = O'F^2$. Let $F = (x_F, y_F)$.
17: \[ (x_0 - b \cos \gamma)^2 + (y_0 - b \sin \gamma)^2 = (x_0 - x_F)^2 + (y_0 - y_F)^2 \]
18: Expanding both sides:
19: \[ x_0^2 - 2x_0 b \cos \gamma + b^2 \cos^2 \gamma + y_0^2 - 2y_0 b \sin \gamma + b^2 \sin^2 \gamma = x_0^2 - 2x_0 x_F + x_F^2 + y_0^2 - 2y_0 y_F + y_F^2 \]
20: Rearranging for $x_0$:
21: \[ 2x_0(x_F - b \cos \gamma) = x_F^2 + y_F^2 - (b^2 \cos^2 \gamma + b^2 \sin^2 \gamma) + 2y_0 b \sin \gamma - 2y_0 y_F \]
22: Using $x_F^2 + y_F^2 = CF^2$, we have:
23: \[ 2x_0(x_F - b \cos \gamma) = CF^2 - b^2 + 2y_0(b \sin \gamma - y_F) \]
24: To show that $x_0 = 0$, we must verify the condition:
25: \[ b^2 - CF^2 = 2y_0(b \sin \gamma - y_F) \]
26: From the geometry of $\triangle ABC$, $CF = b \sin A = \frac{ab \sin \gamma}{c}$. Thus:
27: \[ b^2 - CF^2 = b^2 - \frac{a^2 b^2 \sin^2 \gamma}{c^2} = \frac{b^2(a^2+b^2-2ab \cos \gamma) - a^2 b^2 (1-\cos^2 \gamma)}{c^2} = \frac{(b^2 - ab \cos \gamma)^2}{c^2} \]
28: For the right side, $y_F$ is the $y$-coordinate of the projection of $C$ onto $AB$, given by $y_F = \frac{ab \sin \gamma (a - b \cos \gamma)}{c^2}$. Then:
29: \[ b \sin \gamma - y_F = b \sin \gamma \left( 1 - \frac{a(a - b \cos \gamma)}{c^2} \right) = b \sin \gamma \frac{c^2 - a^2 + ab \cos \gamma}{c^2} = b \sin \gamma \frac{b^2 - ab \cos \gamma}{c^2} \]
30: Substituting $y_0 = \frac{b - a \cos \gamma}{2 \sin \gamma}$:
31: \[ 2y_0(b \sin \gamma - y_F) = 2 \left( \frac{b - a \cos \gamma}{2 \sin \gamma} \right) \frac{b \sin \gamma (b^2 - ab \cos \gamma)}{c^2} = \frac{b(b - a \cos \gamma)(b^2 - ab \cos \gamma)}{c^2} = \frac{b^2(b - a \cos \gamma)^2}{c^2} \]
32: Since $\frac{(b^2 - ab \cos \gamma)^2}{c^2} = \frac{b^2(b - a \cos \gamma)^2}{c^2}$, the equation holds, and we conclude $x_0 = 0$.
33: 
34: **4. Final Proof**
35: The center $O'$ of the circumcircle of $\triangle AFP$ is $(0, y_0)$. The line $BC$ is the $x$-axis. The projection of $O'$ onto the line $BC$ is the point $(0,0)$, which is $C$. In any circle, the midpoint of a chord is the projection of the center of the circle onto the line containing the chord. Since $X$ and $Y$ are the intersections of the circle with the line $BC$, $C$ is the midpoint of $XY$.
36: 
37: (Note: The power of point $C$ is $P(C) = O'C^2 - R^2 = y_0^2 - (b^2 \cos^2 \gamma + (y_0 - b \sin \gamma)^2) = 2y_0 b \sin \gamma - b^2 = -ab \cos \gamma$. Since $\triangle ABC$ is acute, $P(C) < 0$, ensuring $C$ is inside the circle and $X, Y$ are distinct.) \(\square\)

# Proof B

1: To prove that $C$ is the midpoint of the segment $XY$, we employ a coordinate geometry approach.
2: 
3: **1. Coordinate System Setup**
4: Let the line $BC$ be the $x$-axis and the vertex $C$ be the origin $(0, 0)$. Let the coordinates of the vertices of the acute triangle $ABC$ be:
5: - $C = (0, 0)$
6: - $B = (a, 0)$
7: - $A = (b, c)$
8: Since the triangle is acute, we have $a, b, c > 0$ and $a > b$. The condition $a > b$ ensures that the altitude from $A$ to $BC$ falls inside the segment $BC$.
9: 
10: **2. Coordinates of the Orthocenter $H$ and its Reflection $P$**
11: The orthocenter $H$ is the intersection of the altitudes. The altitude from $A$ to $BC$ is the line $x = b$. The altitude from $B$ to $AC$ is perpendicular to $AC$ (which has slope $c/b$), so it has slope $-b/c$ and passes through $(a, 0)$. Its equation is:
12: \[ y = -\frac{b}{c}(x - a) \]
13: Substituting $x = b$, we find the $y$-coordinate of $H$:
14: \[ y_H = -\frac{b}{c}(b - a) = \frac{b(a - b)}{c} \]
15: Point $P$ is the reflection of $H$ across the line $BC$ (the $x$-axis), so:
16: \[ P = \left(b, -\frac{b(a - b)}{c}\right) \]
17: 
18: **3. Coordinates of the Foot of the Altitude $F$**
19: $F$ is the foot of the altitude from $C$ to $AB$. The slope of $AB$ is $\frac{c}{b - a}$. The line $CF$ is perpendicular to $AB$ and passes through the origin, so its slope is $k = \frac{a - b}{c}$.
20: The equation of line $CF$ is $y = kx$, and the equation of line $AB$ is $y = -\frac{1}{k}(x - a)$. Solving for their intersection $F$:
21: \[ kx = -\frac{1}{k}(x - a) \implies k^2 x = -x + a \implies x = \frac{a}{1 + k^2} \]
22: Thus, $F = \left(\frac{a}{1+k^2}, \frac{ak}{1+k^2}\right)$.
23: 
24: **4. The Circumcircle $\omega$ of $\triangle AFP$**
25: Let the center of $\omega$ be $O_\omega = (x_0, y_0)$. Since $A = (b, c)$ and $P = (b, -bk)$, the perpendicular bisector of $AP$ is the horizontal line:
26: \[ y_0 = \frac{c + (-bk)}{2} = \frac{c - bk}{2} \]
27: Since $O_\omega$ is equidistant from $A$ and $F$, we have $O_\omega A^2 = O_\omega F^2$:
28: \[ (x_0 - b)^2 + \left(c - \frac{c - bk}{2}\right)^2 = \left(x_0 - \frac{a}{1+k^2}\right)^2 + \left(\frac{ak}{1+k^2} - \frac{c - bk}{2}\right)^2 \]
29: Simplifying the $y$-term for $A$ as $\frac{c + bk}{2}$ and expanding:
30: \[ x_0^2 - 2x_0 b + b^2 + \frac{(c+bk)^2}{4} = x_0^2 - \frac{2x_0 a}{1+k^2} + \frac{a^2}{(1+k^2)^2} + \frac{a^2 k^2}{(1+k^2)^2} - \frac{ak(c - bk)}{1+k^2} + \frac{(c - bk)^2}{4} \]
31: Rearranging terms to isolate $x_0$:
32: \[ 2x_0 \left(\frac{a}{1+k^2} - b\right) = \frac{a^2(1+k^2)}{(1+k^2)^2} - \frac{ak(c - bk)}{1+k^2} + \frac{(c - bk)^2 - (c+bk)^2}{4} - b^2 \]
33: Using $\frac{(c-bk)^2 - (c+bk)^2}{4} = -cbk$, and multiplying by $(1+k^2)$:
34: \[ 2x_0 (a - b - bk^2) = a^2 - ak(c - bk) - (cbk + b^2)(1+k^2) = a^2 - akc + ak^2b - cbk - cbk^3 - b^2 - b^2k^2 \]
35: Substituting $k = \frac{a - b}{c}$:
36: \[ \text{RHS} = a^2 - a(a - b) + \frac{ab(a - b)^2}{c^2} - b(a - b) - \frac{b(a - b)^3}{c^2} - b^2 - \frac{b^2(a - b)^2}{c^2} \]
37: \[ = (a^2 - a^2 + ab - ab + b^2 - b^2) + \frac{(a - b)^2 [ab - b(a - b) - b^2]}{c^2} = 0 + \frac{(a - b)^2 [ab - ab + b^2 - b^2]}{c^2} = 0 \]
38: Thus, $2x_0(a - b - bk^2) = 0$. For an acute triangle, $a - b - bk^2 = \frac{(a - b)(c^2 - ab + b^2)}{c^2} \neq 0$ (since $c^2 - ab + b^2 = 0$ implies $\angle A = 90^\circ$). Therefore, $x_0 = 0$.
39: 
40: **5. Conclusion**
41: The $x$-coordinate of the center $O_\omega$ is $0$. The projection of the center of a circle onto a chord is the midpoint of that chord. Since the chord $XY$ lies on the $x$-axis (the line $BC$), its midpoint has the same $x$-coordinate as $O_\omega$, which is $0$. Thus, the midpoint of $XY$ is $(0, 0)$, which is vertex $C$.
42: 
43: \(\square\)
