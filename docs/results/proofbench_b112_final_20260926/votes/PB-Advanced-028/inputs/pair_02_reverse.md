# Problem

Let $H$ be the orthocenter of acute triangle $ABC$, let $F$ be
 the foot of the altitude from $C$ to $AB$, and let $P$ be the reflection
 of $H$ across $BC$. Suppose that the circumcircle of triangle $AFP$
 intersects line $BC$ at two distinct points $X$ and $Y$. Prove
 that $C$ is the midpoint of $XY$.

# Proof A

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
