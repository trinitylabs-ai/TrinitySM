# Problem

Given an acute triangle $ABC$, let $D$ and $E$ be the feet of
 the altitudes from $B$ to $AC$ and $C$ to $AB$, respectively.
 Let $E_{1}$ and $E_{2}$ be the reflections of $E$ with respect
 to $AC$ and $BC$, respectively. If $X$ (not equal to $C$) is an
 intersection point of the circumcircle of $\triangle CE_{1}E_{2}$
 and $AC$, and $O$ is the circumcenter of $\triangle CE_{1}E_{2}$,
 prove that $XO$ is perpendicular to $DE$.

# Proof A

1: To prove that $XO$ is perpendicular to $DE$ in an acute triangle $ABC$, we employ coordinate geometry. Let $C$ be the origin $(0,0)$ and let the line $AC$ be the $x$-axis. Let the angles of $\triangle ABC$ be $A, B, C$ and its side lengths be $a, b, c$.
2: 
3: ### 1. Coordinates of the points
4: *   $C = (0, 0)$.
5: *   Since $AC$ is the $x$-axis, $A = (b, 0)$.
6: *   $B = (a \cos C, a \sin C)$.
7: *   $D$ is the foot of the altitude from $B$ to $AC$, so $D = (a \cos C, 0)$.
8: *   $E$ is the foot of the altitude from $C$ to $AB$. In the right triangle $\triangle AEC$, $\angle AEC = 90^\circ$, thus $\angle ECA = 90^\circ - A$. Let $r = CE$. From the law of sines in $\triangle ABC$, $r = a \sin B = b \sin A$. The coordinates of $E$ are:
9:     $E = (r \cos(90^\circ - A), r \sin(90^\circ - A)) = (r \sin A, r \cos A)$.
10: 
11: ### 2. Reflections $E_1$ and $E_2$
12: *   $E_1$ is the reflection of $E$ across $AC$ (the $x$-axis), so $E_1 = (r \sin A, -r \cos A)$.
13: *   $E_2$ is the reflection of $E$ across $BC$. The line $BC$ makes an angle $C$ with the $x$-axis. The angle of the segment $CE$ is $90^\circ - A$. The angle of the segment $CE_2$ is therefore $2C - (90^\circ - A) = 2C + A - 90^\circ$.
14:     $E_2 = (r \cos(2C + A - 90^\circ), r \sin(2C + A - 90^\circ)) = (r \sin(2C + A), -r \cos(2C + A))$.
15: 
16: ### 3. The circumcircle $\Gamma$ and its center $O$
17: The circle $\Gamma$ passes through $C(0,0)$, $E_1$, and $E_2$. Its equation is of the form $x^2 + y^2 - 2gx - 2fy = 0$, where the center is $O = (g, f)$. Since $E_1$ and $E_2$ lie on $\Gamma$:
18: 1.  $r^2 - 2gr \sin A + 2fr \cos A = 0 \implies 2g \sin A - 2f \cos A = r$
19: 2.  $r^2 - 2gr \sin(2C + A) + 2fr \cos(2C + A) = 0 \implies 2g \sin(2C + A) - 2f \cos(2C + A) = r$
20: 
21: Solving this system for $g$ and $f$:
22: Subtracting (1) from (2) gives $2g(\sin(2C+A) - \sin A) - 2f(\cos(2C+A) - \cos A) = 0$. Using sum-to-product identities:
23: $2g(2 \cos(C+A) \sin C) - 2f(-2 \sin(C+A) \sin C) = 0 \implies g \cos(C+A) + f \sin(C+A) = 0$.
24: Thus $f = -g \cot(C+A)$. Substituting this into (1):
25: $2g \sin A + 2g \cot(C+A) \cos A = r \implies 2g \frac{\sin A \sin(C+A) + \cos A \cos(C+A)}{\sin(C+A)} = r$.
26: $2g \frac{\cos(C+A-A)}{\sin(C+A)} = r \implies g = \frac{r \sin(C+A)}{2 \cos C}$.
27: Then $f = -\frac{r \sin(C+A)}{2 \cos C} \cdot \frac{\cos(C+A)}{\sin(C+A)} = -\frac{r \cos(C+A)}{2 \cos C}$.
28: 
29: ### 4. Point $X$ and vector $\vec{XO}$
30: $X$ is the intersection of $\Gamma$ and $AC$ ($y=0$) other than $C$. Substituting $y=0$ into the circle equation $x^2 + y^2 - 2gx - 2fy = 0$ yields $x^2 - 2gx = 0$, so $x = 2g$.
31: $X = (2g, 0)$.
32: The vector $\vec{XO} = O - X = (g - 2g, f - 0) = (-g, f) = \left( -\frac{r \sin(C+A)}{2 \cos C}, -\frac{r \cos(C+A)}{2 \cos C} \right)$.
33: 
34: ### 5. Vector $\vec{DE}$ and perpendicularity
35: $\vec{DE} = E - D = (r \sin A - a \cos C, r \cos A)$.
36: Since $r = a \sin B$ and $\cos C = -\cos(A+B) = \sin A \sin B - \cos A \cos B$:
37: $r \sin A - a \cos C = a \sin B \sin A - a(\sin A \sin B - \cos A \cos B) = a \cos A \cos B$.
38: Thus, $\vec{DE} = (a \cos A \cos B, a \sin B \cos A)$.
39: The dot product $\vec{XO} \cdot \vec{DE}$ is:
40: $\vec{XO} \cdot \vec{DE} = (-g)(a \cos A \cos B) + (f)(a \sin B \cos A)$
41: $= -\frac{r \sin(C+A)}{2 \cos C} a \cos A \cos B - \frac{r \cos(C+A)}{2 \cos C} a \sin B \cos A$
42: $= -\frac{ra \cos A}{2 \cos C} [ \sin(C+A) \cos B + \cos(C+A) \sin B ]$
43: $= -\frac{ra \cos A}{2 \cos C} \sin(C+A+B)$.
44: Since $A+B+C = 180^\circ$, $\sin(A+B+C) = 0$. Therefore, $\vec{XO} \cdot \vec{DE} = 0$, which proves that $XO \perp DE$.
45: 
46: \(\square\)

# Proof B

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
