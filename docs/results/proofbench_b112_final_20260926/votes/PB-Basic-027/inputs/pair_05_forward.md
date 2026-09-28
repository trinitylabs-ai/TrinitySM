# Problem

Given an acute triangle $ABC$, let $D$ and $E$ be the feet of
 the altitudes from $B$ to $AC$ and $C$ to $AB$, respectively.
 Let $E_{1}$ and $E_{2}$ be the reflections of $E$ with respect
 to $AC$ and $BC$, respectively. If $X$ (not equal to $C$) is an
 intersection point of the circumcircle of $\triangle CE_{1}E_{2}$
 and $AC$, and $O$ is the circumcenter of $\triangle CE_{1}E_{2}$,
 prove that $XO$ is perpendicular to $DE$.

# Proof A

1: To prove that $XO$ is perpendicular to $DE$, we establish a coordinate system with $C$ as the origin $(0,0)$ and the line $CA$ as the $x$-axis. Let $a, b, c$ denote the side lengths $BC, AC, AB$ and $\alpha, \beta, \gamma$ denote the angles at vertices $A, B, C$, respectively.
2: 
3: ### 1. Coordinates of the Points
4: Let $r_0$ be the length of the altitude $CE$. In $\triangle BCE$, since $\angle BEC = 90^\circ$ and $\angle CBE = \beta$, we have $r_0 = CE = a \sin \beta$. In $\triangle AEC$, since $\angle AEC = 90^\circ$ and $\angle EAC = \alpha$, we have $\angle ECA = 90^\circ - \alpha$. Let $\theta = 90^\circ - \alpha$.
5: The coordinates of $E$ are:
6: \[ E = (r_0 \cos \theta, r_0 \sin \theta) \]
7: Since $E_1$ is the reflection of $E$ across $AC$ (the $x$-axis), its coordinates are:
8: \[ E_1 = (r_0 \cos \theta, -r_0 \sin \theta) \]
9: The line $BC$ is at an angle $\gamma$ with the $x$-axis. The reflection $E_2$ of $E$ across $BC$ will have an angle relative to $C$ given by $2\gamma - \theta$. Thus:
10: \[ E_2 = (r_0 \cos(2\gamma - \theta), r_0 \sin(2\gamma - \theta)) \]
11: 
12: ### 2. The Circumcircle of $\triangle CE_1E_2$
13: Let the equation of the circumcircle $\omega$ of $\triangle CE_1E_2$ be $x^2 + y^2 - 2x_0 x - 2y_0 y = 0$, where $O = (x_0, y_0)$ is the center. Since $E_1$ and $E_2$ lie on $\omega$:
14: 1) $r_0^2 - 2x_0 r_0 \cos \theta + 2y_0 r_0 \sin \theta = 0 \implies x_0 \cos \theta - y_0 \sin \theta = \frac{r_0}{2}$
15: 2) $r_0^2 - 2x_0 r_0 \cos(2\gamma - \theta) - 2y_0 r_0 \sin(2\gamma - \theta) = 0 \implies x_0 \cos(2\gamma - \theta) + y_0 \sin(2\gamma - \theta) = \frac{r_0}{2}$
16: 
17: Equating the two expressions:
18: \[ x_0 (\cos \theta - \cos(2\gamma - \theta)) = y_0 (\sin(2\gamma - \theta) + \sin \theta) \]
19: Using the sum-to-product identities $\cos A - \cos B = -2 \sin \frac{A+B}{2} \sin \frac{A-B}{2}$ and $\sin A + \sin B = 2 \sin \frac{A+B}{2} \cos \frac{A-B}{2}$:
20: \[ -2x_0 \sin \gamma \sin(\theta - \gamma) = 2y_0 \sin \gamma \cos(\gamma - \theta) \]
21: Since the triangle is acute, $\sin \gamma \neq 0$, so:
22: \[ x_0 \sin(\gamma - \theta) = y_0 \cos(\gamma - \theta) \implies y_0 = x_0 \tan(\gamma - \theta) \]
23: Substituting $y_0 = x_0 \tan(\gamma - \theta)$ into equation (1):
24: \[ x_0 (\cos \theta - \tan(\gamma - \theta) \sin \theta) = \frac{r_0}{2} \implies x_0 \frac{\cos \theta \cos(\gamma - \theta) - \sin \theta \sin(\gamma - \theta)}{\cos(\gamma - \theta)} = \frac{r_0}{2} \]
25: Using the identity $\cos(A+B) = \cos A \cos B - \sin A \sin B$:
26: \[ x_0 \frac{\cos(\theta + \gamma - \theta)}{\cos(\gamma - \theta)} = \frac{r_0}{2} \implies x_0 \frac{\cos \gamma}{\cos(\gamma - \theta)} = \frac{r_0}{2} \]
27: Thus, the coordinates of $O$ are:
28: \[ x_0 = \frac{r_0 \cos(\gamma - \theta)}{2 \cos \gamma}, \quad y_0 = \frac{r_0 \sin(\gamma - \theta)}{2 \cos \gamma} \]
29: 
30: ### 3. Intersection Point $X$ and Vector $XO$
31: The point $X$ is the intersection of $\omega$ and the $x$-axis ($AC$). Setting $y=0$ in $x^2 + y^2 - 2x_0 x - 2y_0 y = 0$ gives $x(x - 2x_0) = 0$. Since $X \neq C$, we have $X = (2x_0, 0)$.
32: The vector $\vec{XO}$ is:
33: \[ \vec{XO} = O - X = (x_0 - 2x_0, y_0 - 0) = (-x_0, y_0) \]
34: 
35: ### 4. Perpendicularity of $XO$ and $DE$
36: The point $D$ is the foot of the altitude from $B$ to $AC$. Since $B = (a \cos \gamma, a \sin \gamma)$, we have $D = (a \cos \gamma, 0)$.
37: The vector $\vec{DE}$ is:
38: \[ \vec{DE} = E - D = (r_0 \cos \theta - a \cos \gamma, r_0 \sin \theta) \]
39: We compute the dot product $\vec{XO} \cdot \vec{DE}$:
40: \[ \vec{XO} \cdot \vec{DE} = -x_0(r_0 \cos \theta - a \cos \gamma) + y_0 r_0 \sin \theta = -r_0(x_0 \cos \theta - y_0 \sin \theta) + x_0 a \cos \gamma \]
41: Substituting $x_0 \cos \theta - y_0 \sin \theta = \frac{r_0}{2}$ and the expression for $x_0$:
42: \[ \vec{XO} \cdot \vec{DE} = -\frac{r_0^2}{2} + \left( \frac{r_0 \cos(\gamma - \theta)}{2 \cos \gamma} \right) a \cos \gamma = \frac{r_0}{2} (a \cos(\gamma - \theta) - r_0) \]
43: Substitute $\theta = 90^\circ - \alpha$:
44: \[ \cos(\gamma - \theta) = \cos(\gamma - (90^\circ - \alpha)) = \cos(\gamma + \alpha - 90^\circ) = \sin(\gamma + \alpha) \]
45: In any triangle, $\sin(\gamma + \alpha) = \sin(180^\circ - \beta) = \sin \beta$. Given $r_0 = a \sin \beta$, we have:
46: \[ \vec{XO} \cdot \vec{DE} = \frac{r_0}{2} (a \sin \beta - a \sin \beta) = 0 \]
47: Thus, $XO$ is perpendicular to $DE$.

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
