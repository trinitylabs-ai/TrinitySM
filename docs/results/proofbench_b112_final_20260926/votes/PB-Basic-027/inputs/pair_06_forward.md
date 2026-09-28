# Problem

Given an acute triangle $ABC$, let $D$ and $E$ be the feet of
 the altitudes from $B$ to $AC$ and $C$ to $AB$, respectively.
 Let $E_{1}$ and $E_{2}$ be the reflections of $E$ with respect
 to $AC$ and $BC$, respectively. If $X$ (not equal to $C$) is an
 intersection point of the circumcircle of $\triangle CE_{1}E_{2}$
 and $AC$, and $O$ is the circumcenter of $\triangle CE_{1}E_{2}$,
 prove that $XO$ is perpendicular to $DE$.

# Proof A

1: To prove that $XO$ is perpendicular to $DE$, we use a coordinate geometry approach.
2: 
3: Let $C$ be the origin $(0, 0)$ and let the side $CA$ lie along the $x$-axis. Let $A = (a, 0)$. Since $\triangle ABC$ is acute, the foot of the altitude $D$ from $B$ to $AC$ lies between $A$ and $C$. Let $D = (d, 0)$ and $B = (d, b)$.
4: 
5: The side $AB$ passes through $(a, 0)$ and $(d, b)$. Its slope is $m_{AB} = \frac{b}{d-a}$. The altitude $CE$ is perpendicular to $AB$, so its slope is $m_{CE} = \frac{a-d}{b}$. The equation of line $CE$ is $y = \frac{a-d}{b}x$.
6: The point $E$ is the intersection of $AB$ and $CE$. The equation of $AB$ is $y = \frac{b}{d-a}(x-a)$. Setting the expressions for $y$ equal:
7: \[ \frac{a-d}{b}x = \frac{b}{d-a}(x-a) \implies -(a-d)^2 x = b^2(x-a) \implies x(b^2 + (a-d)^2) = b^2 a. \]
8: Let $AB^2 = b^2 + (a-d)^2$. Then $x_E = \frac{b^2 a}{AB^2}$ and $y_E = \frac{(a-d)ba}{AB^2}$.
9: 
10: $E_1$ is the reflection of $E$ across $AC$ (the $x$-axis), so $E_1 = (x_E, -y_E)$.
11: $E_2$ is the reflection of $E$ across $BC$. The line $BC$ passes through $(0,0)$ and $(d,b)$, so its slope is $m = b/d$. The reflection $P'(x',y')$ of $P(x,y)$ across $y=mx$ is given by $x' = \frac{1-m^2}{1+m^2}x + \frac{2m}{1+m^2}y$ and $y' = \frac{2m}{1+m^2}x - \frac{1-m^2}{1+m^2}y$.
12: With $m=b/d$, we have $\frac{1-m^2}{1+m^2} = \frac{d^2-b^2}{d^2+b^2}$ and $\frac{2m}{1+m^2} = \frac{2bd}{d^2+b^2}$. Thus,
13: \[ x_{E_2} = \frac{d^2-b^2}{d^2+b^2}x_E + \frac{2bd}{d^2+b^2}y_E, \quad y_{E_2} = \frac{2bd}{d^2+b^2}x_E - \frac{d^2-b^2}{d^2+b^2}y_E. \]
14: 
15: The center $O(x_O, y_O)$ of the circumcircle $\omega$ of $\triangle CE_1E_2$ satisfies $OC=OE_1=OE_2$. Since $C$ is the origin, $x_O^2 + y_O^2 = (x_O-x_E)^2 + (y_O+y_E)^2 = (x_O-x_{E_2})^2 + (y_O-y_{E_2})^2$.
16: This simplifies to:
17: 1) $2x_O x_E - 2y_O y_E = x_E^2 + y_E^2 = CE^2$
18: 2) $2x_O x_{E_2} + 2y_O y_{E_2} = x_{E_2}^2 + y_{E_2}^2 = CE^2$
19: Subtracting these gives $x_O(x_E - x_{E_2}) = y_O(y_E + y_{E_2})$.
20: Using $s = d^2+b^2$, we calculate:
21: \[ x_E - x_{E_2} = x_E - \frac{d^2-b^2}{s}x_E - \frac{2bd}{s}y_E = \frac{2b^2 x_E - 2bdy_E}{s}, \quad y_E + y_{E_2} = y_E + \frac{2bd}{s}x_E - \frac{d^2-b^2}{s}y_E = \frac{2b^2 y_E + 2bdx_E}{s}. \]
22: Thus, $\frac{x_O}{y_O} = \frac{2b^2 y_E + 2bdx_E}{2b^2 x_E - 2bdy_E} = \frac{by_E + dx_E}{bx_E - dy_E}$.
23: Substituting $x_E, y_E$:
24: \[ by_E + dx_E = \frac{b(a-d)ba + db^2 a}{AB^2} = \frac{b^2 a^2}{AB^2}, \quad bx_E - dy_E = \frac{b(b^2 a) - d(a-d)ba}{AB^2} = \frac{ba(b^2 - ad + d^2)}{AB^2}. \]
25: So, $\frac{x_O}{y_O} = \frac{ba}{b^2 + d^2 - ad}$.
26: 
27: The intersection $X$ of $\omega$ and $AC$ (the $x$-axis) is $(2x_O, 0)$.
28: The vector $\vec{XO} = (x_O - 2x_O, y_O - 0) = (-x_O, y_O)$.
29: The vector $\vec{DE} = (x_E - d, y_E)$.
30: $XO \perp DE \iff \vec{XO} \cdot \vec{DE} = -x_O(x_E - d) + y_O y_E = 0 \iff \frac{x_O}{y_O} = \frac{y_E}{x_E - d}$.
31: We have $\frac{y_E}{x_E - d} = \frac{(a-d)ba/AB^2}{b^2 a/AB^2 - d} = \frac{(a-d)ba}{b^2 a - d(b^2 + (a-d)^2)}$.
32: The denominator is $b^2 a - db^2 - da^2 + 2ad^2 - d^3$.
33: Checking the equality $\frac{x_O}{y_O} = \frac{y_E}{x_E - d}$ is equivalent to:
34: \[ (a-d)(b^2 + d^2 - ad) = b^2 a - db^2 - da^2 + 2ad^2 - d^3. \]
35: Expanding the left side:
36: \[ (a-d)(b^2 + d^2 - ad) = ab^2 + ad^2 - a^2 d - db^2 - d^3 + ad^2 = ab^2 - db^2 - a^2 d + 2ad^2 - d^3. \]
37: The expressions match. Thus, $XO \perp DE$. \(\square\)

# Proof B

1: To prove that $XO$ is perpendicular to $DE$ in an acute triangle $ABC$, we establish a coordinate system and calculate the slopes of the lines $DE$ and $XO$.
2: 
3: Let $C$ be the origin $(0, 0)$ and the side $CA$ lie on the $x$-axis. Let $a, b, c$ denote the side lengths $BC, CA, AB$ respectively, and let $A, B, C$ denote the angles of the triangle.
4: 
5: 1. **Coordinates of $D$ and $E$**:
6:    Since $C$ is the origin and $A$ lies on the $x$-axis, the coordinates of $A$ are $(b, 0)$. The vertex $B$ has coordinates $(a \cos C, a \sin C)$.
7:    $D$ is the foot of the altitude from $B$ to $AC$, so $D$ is the projection of $B$ onto the $x$-axis:
8:    \[ D = (a \cos C, 0) \]
9:    $E$ is the foot of the altitude from $C$ to $AB$. In $\triangle ACE$, $\angle AEC = 90^\circ$, so $CE = b \sin A$. The angle $\angle ACE = 180^\circ - 90^\circ - A = 90^\circ - A$. Thus, the coordinates of $E$ are:
10:    \[ E = (CE \cos(90^\circ - A), CE \sin(90^\circ - A)) = (b \sin A \sin A, b \sin A \cos A) = (b \sin^2 A, b \sin A \cos A) \]
11: 
12: 2. **Slope of $DE$**:
13:    The slope of the line $DE$ is given by:
14:    \[ m_{DE} = \frac{y_E - y_D}{x_E - x_D} = \frac{b \sin A \cos A - 0}{b \sin^2 A - a \cos C} \]
15:    Using the Law of Sines, $a = \frac{b \sin A}{\sin B}$. Substituting this into the expression for the denominator:
16:    \[ x_E - x_D = b \sin^2 A - \frac{b \sin A \cos C}{\sin B} = \frac{b \sin A (\sin A \sin B - \cos C)}{\sin B} \]
17:    Since $A + B + C = 180^\circ$, we have $\cos C = -\cos(A+B) = \sin A \sin B - \cos A \cos B$. Substituting this:
18:    \[ x_E - x_D = \frac{b \sin A (\sin A \sin B - (\sin A \sin B - \cos A \cos B))}{\sin B} = \frac{b \sin A \cos A \cos B}{\sin B} \]
19:    Now, we calculate the slope:
20:    \[ m_{DE} = \frac{b \sin A \cos A}{\frac{b \sin A \cos A \cos B}{\sin B}} = \frac{\sin B}{\cos B} = \tan B \]
21: 
22: 3. **Coordinates of $O$ and $X$**:
23:    Let $\theta = \angle ACE = 90^\circ - A$. The point $E$ has polar coordinates $(CE, \theta)$.
24:    $E_1$ is the reflection of $E$ across $AC$ (the $x$-axis), so its polar angle is $-\theta$.
25:    $E_2$ is the reflection of $E$ across $BC$. The line $BC$ has polar angle $C$, so the polar angle of $E_2$ is $2C - \theta$.
26:    The points $C, E_1, E_2$ lie on the circumcircle $\Gamma$ with center $O$. Since $CE_1 = CE = CE_2$, the triangle $CE_1 E_2$ is isosceles with $C$ as a vertex on the circle. The circumcenter $O$ must lie on the perpendicular bisectors of $CE_1$ and $CE_2$. The polar angle $\phi$ of the vector $\vec{CO}$ is the average of the polar angles of $E_1$ and $E_2$:
27:    \[ \phi = \frac{-\theta + (2C - \theta)}{2} = C - \theta \]
28:    Let $O = (x_O, y_O)$. The equation of $\Gamma$ (which passes through the origin $C$) is $x^2 + y^2 - 2x x_O - 2y y_O = 0$.
29:    $X$ is the intersection of $\Gamma$ and the $x$-axis ($y=0$) other than $C$:
30:    \[ x^2 - 2x x_O = 0 \implies x = 2x_O \implies X = (2x_O, 0) \]
31: 
32: 4. **Slope of $XO$**:
33:    The vector $\vec{XO} = (x_O - 2x_O, y_O - 0) = (-x_O, y_O)$. The slope of $XO$ is:
34:    \[ m_{XO} = \frac{y_O}{-x_O} = -\tan \phi = -\tan(C - \theta) \]
35:    Substituting $\theta = 90^\circ - A$:
36:    \[ m_{XO} = -\tan(C - (90^\circ - A)) = -\tan(C + A - 90^\circ) \]
37:    Using the identity $\tan(\psi - 90^\circ) = -\cot \psi$:
38:    \[ m_{XO} = -(-\cot(C + A)) = \cot(C + A) \]
39:    Since $A + B + C = 180^\circ$, $C + A = 180^\circ - B$. Thus:
40:    \[ m_{XO} = \cot(180^\circ - B) = -\cot B \]
41: 
42: 5. **Final Verification**:
43:    The product of the slopes is:
44:    \[ m_{DE} \cdot m_{XO} = (\tan B) \cdot (-\cot B) = -1 \]
45:    Since the product of the slopes is $-1$, the lines $XO$ and $DE$ are perpendicular.
