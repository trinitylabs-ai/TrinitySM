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
