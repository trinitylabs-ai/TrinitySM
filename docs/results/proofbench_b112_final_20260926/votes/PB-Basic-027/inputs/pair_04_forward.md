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
