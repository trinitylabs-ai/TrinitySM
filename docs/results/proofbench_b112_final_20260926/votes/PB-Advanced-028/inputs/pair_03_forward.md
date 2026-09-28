# Problem

Let $H$ be the orthocenter of acute triangle $ABC$, let $F$ be
 the foot of the altitude from $C$ to $AB$, and let $P$ be the reflection
 of $H$ across $BC$. Suppose that the circumcircle of triangle $AFP$
 intersects line $BC$ at two distinct points $X$ and $Y$. Prove
 that $C$ is the midpoint of $XY$.

# Proof A

1: Let the angles of triangle $ABC$ be $A, B, C$ and its side lengths be $a, b, c$. We set up a coordinate system with $C$ as the origin $(0,0)$ and the line $BC$ as the $x$-axis. Thus, the coordinates of the vertices are $C = (0,0)$, $B = (a, 0)$, and $A = (b \cos C, b \sin C)$.
2: 
3: The foot of the altitude from $C$ to $AB$ is $F$. The line $AB$ passes through $B(a,0)$ and $A(b \cos C, b \sin C)$, so its equation is $y - 0 = \frac{b \sin C}{b \cos C - a}(x - a)$. The line $CF$ is perpendicular to $AB$ and passes through the origin, so its equation is $y = \frac{a - b \cos C}{b \sin C}x$. The intersection $F = (x_F, y_F)$ is found by solving these equations:
4: \[ \frac{a - b \cos C}{b \sin C}x = \frac{b \sin C}{b \cos C - a}(x - a) \implies x(a - b \cos C)(b \cos C - a) = b^2 \sin^2 C (x - a) \]
5: \[ -x(a - b \cos C)^2 = b^2 \sin^2 C x - ab^2 \sin^2 C \implies x[b^2 \sin^2 C + (a - b \cos C)^2] = ab^2 \sin^2 C \]
6: Since $b^2 \sin^2 C + (a - b \cos C)^2 = b^2 \sin^2 C + a^2 - 2ab \cos C + b^2 \cos^2 C = a^2 + b^2 - 2ab \cos C = c^2$, we have:
7: \[ x_F = \frac{ab^2 \sin^2 C}{c^2}, \quad y_F = \frac{a - b \cos C}{b \sin C} \cdot \frac{ab^2 \sin^2 C}{c^2} = \frac{ab \sin C (a - b \cos C)}{c^2} \]
8: The distance $CF$ is the altitude $h_c = a \sin B = 2R \sin A \sin B$. Using $a - b \cos C = 2R \sin A - 2R \sin B \cos C = 2R \cos B \sin C$, we find $y_F = \frac{(2R \sin A)(2R \sin B) \sin C (2R \cos B \sin C)}{(2R \sin C)^2} = 2R \sin A \sin B \cos B$.
9: 
10: The orthocenter $H$ lies on the altitude $AD$ where $D = (b \cos C, 0)$. Thus $x_H = b \cos C$. Since $H$ also lies on $CF$, $y_H = \frac{a - b \cos C}{b \sin C}(b \cos C) = \frac{2R \cos B \sin C}{\sin C} \cos C = 2R \cos B \cos C$. $P$ is the reflection of $H$ across $BC$ (the $x$-axis), so $P = (b \cos C, -2R \cos B \cos C)$.
11: 
12: Let the circumcircle $\Gamma$ of $\triangle AFP$ have the equation $x^2 + y^2 + Dx + Ey + G = 0$. The intersection of $\Gamma$ with the line $BC$ ($y=0$) gives points $X$ and $Y$, which are the roots of $x^2 + Dx + G = 0$. $C$ is the midpoint of $XY$ if and only if $X+Y = 0$, which implies $D=0$.
13: The center of $\Gamma$ is $O_\Gamma = (-D/2, -E/2)$. $D=0$ if and only if $O_\Gamma$ lies on the $y$-axis. $O_\Gamma$ is the intersection of the perpendicular bisectors of $AP$ and $FP$. The perpendicular bisector of $AP$ is the horizontal line $y = \frac{y_A + y_P}{2}$, where $y_A = b \sin C$ and $y_P = -2R \cos B \cos C$. The perpendicular bisector of $FP$ is $x(x_P - x_F) + y(y_P - y_F) = \frac{x_P^2 + y_P^2 - x_F^2 - y_F^2}{2}$.
14: Substituting $x=0$ and $y = \frac{y_A + y_P}{2}$ into the latter, $D=0$ if and only if:
15: \[ (y_A + y_P)(y_P - y_F) = x_P^2 + y_P^2 - x_F^2 - y_F^2 \iff x_P^2 - (x_F^2 + y_F^2) - y_A y_P + y_F(y_A + y_P) = 0 \]
16: Substituting $x_P = 2R \sin B \cos C$, $x_F^2 + y_F^2 = CF^2 = (2R \sin A \sin B)^2$, $y_A = 2R \sin B \sin C$, $y_P = -2R \cos B \cos C$, and $y_F = 2R \sin A \sin B \cos B$:
17: \[ 4R^2 \sin^2 B \cos^2 C - 4R^2 \sin^2 A \sin^2 B - (2R \sin B \sin C)(-2R \cos B \cos C) + 2R \sin A \sin B \cos B (2R \sin B \sin C - 2R \cos B \cos C) = 0 \]
18: Dividing by $4R^2$:
19: \[ \sin^2 B (\cos^2 C - \sin^2 A) + \sin B \cos B \sin C \cos C + \sin A \sin B \cos B (\sin B \sin C - \cos B \cos C) = 0 \]
20: Using $\sin B \sin C - \cos B \cos C = -\cos(B+C) = \cos A$:
21: \[ \sin^2 B (\cos^2 C - \sin^2 A) + \frac{1}{4} \sin 2B \sin 2C + \frac{1}{4} \sin 2A \sin 2B = 0 \]
22: Using $\cos^2 C - \sin^2 A = \cos(C+A)\cos(C-A) = -\cos B \cos(C-A)$:
23: \[ \sin^2 B (-\cos B \cos(C-A)) + \sin B \cos B \sin C \cos C = \sin B \cos B [-\sin B \cos(C-A) + \frac{1}{2} \sin 2C] \]
24: Since $\sin B = \sin(A+C)$, we have $-\sin(A+C) \cos(C-A) + \frac{1}{2} \sin 2C = -\frac{1}{2}(\sin 2C + \sin 2A) + \frac{1}{2} \sin 2C = -\frac{1}{2} \sin 2A$.
25: The expression becomes $\sin B \cos B (-\frac{1}{2} \sin 2A) + \frac{1}{4} \sin 2A \sin 2B = -\frac{1}{4} \sin 2B \sin 2A + \frac{1}{4} \sin 2A \sin 2B = 0$.
26: This identity confirms $D=0$. Since the triangle is acute, the power of point $C$ is $G = -4R^2 \sin A \sin B \cos C < 0$, ensuring $X$ and $Y$ are distinct. Thus, $C$ is the midpoint of $XY$.

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
