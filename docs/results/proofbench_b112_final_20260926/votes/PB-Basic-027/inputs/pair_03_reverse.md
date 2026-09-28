# Problem

Given an acute triangle $ABC$, let $D$ and $E$ be the feet of
 the altitudes from $B$ to $AC$ and $C$ to $AB$, respectively.
 Let $E_{1}$ and $E_{2}$ be the reflections of $E$ with respect
 to $AC$ and $BC$, respectively. If $X$ (not equal to $C$) is an
 intersection point of the circumcircle of $\triangle CE_{1}E_{2}$
 and $AC$, and $O$ is the circumcenter of $\triangle CE_{1}E_{2}$,
 prove that $XO$ is perpendicular to $DE$.

# Proof A

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

# Proof B

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
