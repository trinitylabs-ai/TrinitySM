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
