# Problem

Let $H$ be the orthocenter of acute triangle $ABC$, let $F$ be
 the foot of the altitude from $C$ to $AB$, and let $P$ be the reflection
 of $H$ across $BC$. Suppose that the circumcircle of triangle $AFP$
 intersects line $BC$ at two distinct points $X$ and $Y$. Prove
 that $C$ is the midpoint of $XY$.

# Proof A

1: To prove that $C$ is the midpoint of the segment $XY$, we use a coordinate geometry approach. Let the line $BC$ be the $x$-axis. We set the coordinates of the vertices of the triangle as $B = (x_B, 0)$, $C = (x_C, 0)$, and $A = (x_A, y_A)$. Since $\triangle ABC$ is acute, $y_A \neq 0$, and the $x$-coordinates $x_A, x_B, x_C$ are distinct.
2: 
3: Let $D$ be the foot of the altitude from $A$ to $BC$. Then $D = (x_A, 0)$. The orthocenter $H$ lies on $AD$, so $H = (x_A, y_H)$. The altitude from $B$ to $AC$ is perpendicular to the line $AC$, which has slope $m_{AC} = \frac{y_A}{x_A - x_C}$. Thus, the slope of $BH$ is $m_{BH} = -\frac{x_A - x_C}{y_A}$. The equation of line $BH$ is $y - 0 = -\frac{x_A - x_C}{y_A}(x - x_B)$. Since $H$ lies on this line and $x = x_A$, its $y$-coordinate is:
4: \[ y_H = -\frac{(x_A - x_C)(x_A - x_B)}{y_A} \]
5: Point $P$ is the reflection of $H$ across $BC$, so $P = (x_A, -y_H)$.
6: 
7: Let $k$ be the slope of $AB$, so $k = \frac{y_A}{x_A - x_B}$. Then $y_A = k(x_A - x_B)$ and $y_H = \frac{x_C - x_A}{k}$. The altitude from $C$ to $AB$ (line $CF$) is perpendicular to $AB$, so its slope is $-\frac{1}{k}$. The equation of $CF$ is $y = -\frac{1}{k}(x - x_C)$. The foot $F(x_F, y_F)$ is the intersection of $AB$ (equation $y = k(x - x_B)$) and $CF$. Equating the two gives $k(x_F - x_B) = -\frac{1}{k}(x_F - x_C)$, which yields:
8: \[ x_F = \frac{x_C + k^2 x_B}{k^2 + 1}, \quad y_F = \frac{k(x_C - x_B)}{k^2 + 1} \]
9: Let $\Gamma$ be the circumcircle of $\triangle AFP$ with center $O(x_O, y_O)$. Since $A(x_A, y_A)$ and $P(x_A, -y_H)$ are on $\Gamma$, the center $O$ must lie on the perpendicular bisector of $AP$, which is the horizontal line $y = \frac{y_A - y_H}{2}$. Thus $y_O = \frac{y_A - y_H}{2}$. Since $F$ and $A$ are also on $\Gamma$, we have $(x_F - x_O)^2 + (y_F - y_O)^2 = (x_A - x_O)^2 + (y_A - y_O)^2$. Expanding and simplifying gives:
10: \[ 2(x_A - x_F)x_O = (x_A - x_F)(x_A + x_F) + (y_A - y_O)^2 - (y_F - y_O)^2 \]
11: Using the identity $a^2 - b^2 = (a-b)(a+b)$, we have $(y_A - y_O)^2 - (y_F - y_O)^2 = (y_A - y_F)(y_A + y_F - 2y_O)$. Substituting $2y_O = y_A - y_H$, this becomes $(y_A - y_F)(y_F + y_H)$. Thus:
12: \[ 2(x_A - x_F)x_O = (x_A - x_F)(x_A + x_F) + (y_A - y_F)(y_F + y_H) \]
13: The intersection of $\Gamma$ with the line $BC$ (the $x$-axis) consists of points $X$ and $Y$. The $x$-coordinate of the midpoint of $XY$ is $x_O$. We want to prove $x_O = x_C$, which is equivalent to:
14: \[ (x_A - x_F)(2x_C - x_A - x_F) = (y_A - y_F)(y_F + y_H) \]
15: Using the derived coordinates:
16: \[ x_A - x_F = \frac{k^2(x_A - x_B) + x_A - x_C}{k^2 + 1}, \quad 2x_C - x_A - x_F = \frac{x_C(2k^2 + 1) - x_A(k^2 + 1) - k^2 x_B}{k^2 + 1} \]
17: \[ y_A - y_F = \frac{k[k^2(x_A - x_B) + x_A - x_C]}{k^2 + 1}, \quad y_F + y_H = \frac{x_C(2k^2 + 1) - x_A(k^2 + 1) - k^2 x_B}{k(k^2 + 1)} \]
18: Multiplying $(y_A - y_F)$ and $(y_F + y_H)$, we find:
19: \[ (y_A - y_F)(y_F + y_H) = \frac{[k^2(x_A - x_B) + x_A - x_C][x_C(2k^2 + 1) - x_A(k^2 + 1) - k^2 x_B]}{(k^2 + 1)^2} \]
20: This is exactly the product $(x_A - x_F)(2x_C - x_A - x_F)$. Thus, $x_O = x_C$, which proves that $C$ is the midpoint of $XY$. \(\square\)

# Proof B

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
