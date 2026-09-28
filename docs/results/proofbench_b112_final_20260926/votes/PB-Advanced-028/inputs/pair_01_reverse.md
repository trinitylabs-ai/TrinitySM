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
