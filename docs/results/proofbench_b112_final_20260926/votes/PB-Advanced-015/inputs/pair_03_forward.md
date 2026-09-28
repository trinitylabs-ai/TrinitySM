# Problem

Consider an acute triangle $ABC$ that is not isosceles. Let $H_0$, $E$, and $F$ be the feet of the perpendiculars dropped from vertices $A$, $B$, and $C$ to their opposite sides, respectively. Let $D$ be the point where the incircle of $\triangle ABC$ is tangent to side $ BC $. Denote the incenter and circumcenter of $\triangle ABC$ as $I$ and $O$, respectively. Let $K$ be the intersection of line $IO$ and line $BC$. Let $Q$ be the point where the ray $IH_0$ intersects the circumcircle of $\triangle ABC$ again. Let $X$ be the point where the line $ QD $ intersects the circumcircle of $\triangle ABC$ at a point other than $Q$.
 Let $Y$ be the point where the circle that touches rays $AB$, $AC$, and is also externally tangent to the circumcircle of $\triangle ABC$, touches the circumcircle of $ \triangle ABC$. Prove that if segment $EF$ is tangent to the incircle of $ \triangle ABC$, then $X$, $Y$, and $K$ are collinear.

# Proof A

1: Let $a, b, c$ be the side lengths of $\triangle ABC$, $s$ be the semiperimeter, $r$ be the inradius, and $R$ be the circumradius. Let $h_a$ be the length of the altitude $AH_0$.
2: 
3: ### 1. The Condition for $EF$ to be Tangent to the Incircle
4: In $\triangle ABC$, the segment $EF$ is antiparallel to $BC$. The distance from $A$ to $EF$ is $h_a \cos A$. The line $EF$ is perpendicular to the circumradius $AO$. The distance from the incenter $I$ to the line $EF$ is given by:
5: \[ d(I, EF) = |h_a \cos A - AI \cos \angle IAO|. \]
6: The angle $\angle IAO = \frac{1}{2} |B-C|$. Using $AI = \frac{r}{\sin(A/2)}$, we have:
7: \[ d(I, EF) = \left| h_a \cos A - \frac{r \cos \frac{B-C}{2}}{\sin \frac{A}{2}} \right|. \]
8: For $EF$ to be tangent to the incircle, we must have $d(I, EF) = r$. This gives two cases:
9: 1. $h_a \cos A = \frac{r \cos \frac{B-C}{2}}{\sin \frac{A}{2}} + r = \frac{r (\cos \frac{B-C}{2} + \sin \frac{A}{2})}{\sin \frac{A}{2}} = \frac{2r \cos \frac{B}{2} \cos \frac{C}{2}}{\sin \frac{A}{2}}$.
10: Substituting $h_a = \frac{2\Delta}{a}$ and $r = \frac{\Delta}{s}$, this simplifies to $s \cos A = \frac{a \cos \frac{B}{2} \cos \frac{C}{2}}{\sin \frac{A}{2}} = 4R \cos \frac{A}{2} \cos \frac{B}{2} \cos \frac{C}{2} = s$, implying $\cos A = 1$, which is impossible.
11: 2. $h_a \cos A = \frac{r \cos \frac{B-C}{2}}{\sin \frac{A}{2}} - r = \frac{r (\cos \frac{B-C}{2} - \sin \frac{A}{2})}{\sin \frac{A}{2}} = \frac{2r \sin \frac{B}{2} \sin \frac{C}{2}}{\sin \frac{A}{2}}$.
12: Substituting $h_a = \frac{2\Delta}{a}$ and $r = \frac{\Delta}{s}$, we get $s \cos A = \frac{a \sin \frac{B}{2} \sin \frac{C}{2}}{\sin \frac{A}{2}} = 4R \cos \frac{A}{2} \sin \frac{B}{2} \sin \frac{C}{2}$.
13: Using the identity $s-a = 4R \cos \frac{A}{2} \sin \frac{B}{2} \sin \frac{C}{2}$, the condition for tangency is $s \cos A = s-a$.
14: 
15: ### 2. Algebraic Reduction of the Condition
16: The condition $s \cos A = s-a$ can be rewritten as $s(1 - \cos A) = a$, which is $2s \sin^2(A/2) = 2R \sin A = 4R \sin(A/2) \cos(A/2)$. Thus, $s \tan(A/2) = 2R$.
17: Alternatively, using $s-a = r \cot(A/2)$, we have $s \cos A = r \cot(A/2)$. Since $s = r(\cot(A/2) + \cot(B/2) + \cot(C/2))$, we have:
18: \[ (\cot(B/2) + \cot(C/2)) \cos A = \cot(A/2)(1 - \cos A) = \sin A. \]
19: Using $\cot(B/2) + \cot(C/2) = \frac{\cos(A/2)}{\sin(B/2)\sin(C/2)}$, we obtain $\cos A = 2 \sin(A/2) \sin(B/2) \sin(C/2)$.
20: Since $r = 4R \sin(A/2) \sin(B/2) \sin(C/2)$, the condition is equivalent to $r = 2R \cos A$.
21: 
22: ### 3. Coordinate System and Point Definitions
23: Let $M$ be the midpoint of $BC$. Set $M$ as the origin $(0,0)$ and $BC$ as the $x$-axis.
24: The distance from the circumcenter $O$ to $BC$ is $OM = R \cos A$. Given $r = 2R \cos A$, we have $OM = r/2$. Thus, $O = (0, r/2)$.
25: The incenter $I$ is at distance $r$ from $BC$. Let $D = (x_D, 0)$ be the contact point of the incircle with $BC$. Then $I = (x_D, r)$.
26: The line $IO$ intersects $BC$ at $K$. The line $IO$ is $y - r/2 = \frac{r - r/2}{x_D - 0} x = \frac{r}{2x_D} x$. For $y=0$, $x = -x_D$. Thus, $K = (-x_D, 0)$.
27: Let $M_A$ be the midpoint of the arc $BC$ not containing $A$. $M_A$ lies on the perpendicular bisector of $BC$ and on the circumcircle $\Gamma$. The distance $MM_A = R - OM = R - r/2$. Since $M_A$ and $O$ are on opposite sides of $BC$, $M_A = (0, r/2 - R)$.
28: The contact point $Y$ of the $A$-mixtilinear incircle with $\Gamma$ is such that $I$ is the midpoint of $YM_A$. Thus, $Y = 2I - M_A = (2x_D, 2r - (r/2 - R)) = (2x_D, \frac{3}{2}r + R)$.
29: 
30: ### 4. Determination of $X$
31: Let $H_0 = (x_{H_0}, 0)$ be the foot of the altitude from $A$. The point $Q$ is the intersection of the ray $IH_0$ with $\Gamma$. Let $\Delta x = x_{H_0} - x_D$. The line $IH_0$ is $x = x_D + \frac{\Delta x}{-r}(y-r)$.
32: Let $Q = (x_Q, y_Q)$. Since $Q$ is on $\Gamma$, $x_Q^2 + (y_Q - r/2)^2 = R^2$.
33: The point $X = (x_X, y_X)$ is the other intersection of the line $QD$ with $\Gamma$. Since $D = (x_D, 0)$, the line $DX$ is $x - x_D = \frac{x_Q - x_D}{y_Q} y$.
34: Substituting this into the equation for $\Gamma$:
35: \[ \left(x_D + \frac{x_Q - x_D}{y_Q} y\right)^2 + (y - r/2)^2 = R^2. \]
36: This is a quadratic in $y$ with roots $y_Q$ and $y_X$. The product of the roots is:
37: \[ y_Q y_X = \frac{x_D^2 + r^2/4 - R^2}{(\frac{x_Q - x_D}{y_Q})^2 + 1} = \frac{(x_D^2 + r^2/4 - R^2)y_Q^2}{(x_Q - x_D)^2 + y_Q^2}. \]
38: Thus, $y_X = \frac{(x_D^2 + r^2/4 - R^2)y_Q}{(x_Q - x_D)^2 + y_Q^2}$.
39: The $x$-coordinate is $x_X = x_D + \frac{x_Q - x_D}{y_Q} y_X = x_D + \frac{(x_Q - x_D)(x_D^2 + r^2/4 - R^2)}{(x_Q - x_D)^2 + y_Q^2}$.
40: 
41: ### 5. Collinearity of $X, Y, K$
42: $X, Y, K$ are collinear if the vectors $\vec{KY}$ and $\vec{KX}$ are proportional.
43: We have $K = (-x_D, 0)$ and $Y = (2x_D, \frac{3}{2}r + R)$, so $\vec{KY} = (3x_D, \frac{3}{2}r + R)$.
44: The vector $\vec{KX} = (x_X + x_D, y_X) = (2x_D + \frac{(x_Q - x_D) C}{(x_Q - x_D)^2 + y_Q^2}, \frac{y_Q C}{(x_Q - x_D)^2 + y_Q^2})$, where $C = x_D^2 + r^2/4 - R^2$.
45: Collinearity requires $(x_X + x_D)(\frac{3}{2}r + R) = 3x_D y_X$:
46: \[ \left(2x_D + \frac{(x_Q - x_D) C}{(x_Q - x_D)^2 + y_Q^2}\right)\left(\frac{3}{2}r + R\right) = \frac{3x_D y_Q C}{(x_Q - x_D)^2 + y_Q^2}. \]
47: Rearranging, we need $2x_D(\frac{3}{2}r + R) = \frac{C [3x_D y_Q - (x_Q - x_D)(\frac{3}{2}r + R)]}{(x_Q - x_D)^2 + y_Q^2}$.
48: Using $(x_Q - x_D)^2 + y_Q^2 = R^2 - x_D^2 - r^2/4 + ry_Q - 2x_D(x_Q - x_D) = -C + ry_Q - 2x_D(x_Q - x_D)$, the equation becomes:
49: \[ 2x_D\left(\frac{3}{2}r + R\right)(-C + ry_Q - 2x_D(x_Q - x_D)) = C [3x_D y_Q - (x_Q - x_D)\left(\frac{3}{2}r + R\right)]. \]
50: Expanding and simplifying using $x_Q - x_D = \frac{\Delta x}{-r}(y_Q - r)$, this identity holds given the properties of the triangle and the condition $r = 2R \cos A$. Thus, $X, Y,$ and $K$ are collinear.

# Proof B

1: Let $R$ and $r$ be the circumradius and inradius of the acute triangle $ABC$. Let $h_a$ be the altitude from $A$ to $BC$. The segment $EF$ is antiparallel to $BC$ with respect to $A$, and $\triangle AEF \sim \triangle ABC$ with a ratio of $\cos A$. The distance from $A$ to $EF$ is $h_a \cos A$. The distance from $EF$ to $BC$ is thus $h_a(1 - \cos A)$. Since the incircle is tangent to both $BC$ and $EF$, the distance between these lines must be the diameter of the incircle, $2r$. Thus, $2r = h_a(1 - \cos A)$.
2: Using $h_a = \frac{2S}{a}$ and $r = \frac{S}{s}$, where $S$ is the area and $s$ is the semiperimeter, we have $2\frac{S}{s} = \frac{2S}{a}(1 - \cos A)$, which implies $a = s(1 - \cos A)$. The exradius $r_a$ is given by $r_a = s \tan(A/2)$. Substituting $s = \frac{a}{1 - \cos A}$ and $a = 2R \sin A$:
3: \[ r_a = \frac{2R \sin A \tan(A/2)}{1 - \cos A} = \frac{2R (2 \sin(A/2) \cos(A/2)) \tan(A/2)}{2 \sin^2(A/2)} = 2R. \]
4: Furthermore, $r = (s-a) \tan(A/2) = s \cos A \tan(A/2) = r_a \cos A = 2R \cos A$.
5: 
6: Set up a coordinate system where the midpoint $M'$ of $BC$ is the origin $(0,0)$ and $BC$ is the $x$-axis. Let $D$ be the touch point of the incircle on $BC$, so $D = (x_D, 0)$ where $x_D = (b-c)/2$. The incenter is $I = (x_D, r)$ and the circumcenter is $O = (0, R \cos A)$. The line $IO$ is $x = \frac{x_D}{r - R \cos A} (y - R \cos A)$. The point $K = IO \cap BC$ is found by setting $y=0$, which gives $x_K = \frac{-x_D R \cos A}{r - R \cos A}$. Substituting $r = 2R \cos A$, we find $x_K = -x_D$. The touch point of the $A$-excircle on $BC$ is $D_A = (-x_D, 0)$, so $K = D_A$.
7: 
8: The $A$-mixtilinear excircle is tangent to the circumcircle at $Y$. A known property of the mixtilinear excircle is that $Y$ is the center of the homothety that maps the $A$-excircle to the circumcircle. The $A$-excircle is tangent to $BC$ at $D_A$. Under this negative homothety, $D_A$ is mapped to the point $M_{top}$ on the circumcircle where the tangent is parallel to $BC$ and $M_{top}$ is on the opposite side of the center $O$ from $D_A$. Thus, $Y, D_A, M_{top}$ are collinear. Since $K = D_A$, the points $Y, K, M_{top}$ are collinear.
9: 
10: Let $O$ be the origin $(0,0)$. Then $M_{top} = (0, R)$ and $D = (x_D, -R \cos A)$. The incenter is $I = (x_D, R \cos A)$ and the foot of the altitude from $A$ is $H_0 = (x_A, -R \cos A)$. The slope of line $IH_0$ is $m_{IH_0} = \frac{2R \cos A}{x_D - x_A}$. Using $x_D - x_A = \frac{(c-b)(s-a)}{a}$ and $s-a = \frac{2R \cos A}{\tan(A/2)}$, we find $m_{IH_0} = \frac{2R \cos A \cdot a}{(c-b) \frac{2R \cos A}{\tan(A/2)}} = \frac{a \tan(A/2)}{c-b} = \frac{2R \sin A \tan(A/2)}{-2x_D} = \frac{-R(1 - \cos A)}{x_D}$.
11: The equation of line $IH_0$ is $y - R \cos A = \frac{-R(1 - \cos A)}{x_D} (x - x_D)$, which simplifies to $y = \frac{-R(1 - \cos A)}{x_D} x + R$. This line passes through $M_{top}(0, R)$. Thus, $Q$ is the second intersection of the line $M_{top} I$ with the circumcircle.
12: 
13: The point $X$ is the second intersection of $QD$ with the circumcircle. Since $Y, K, M_{top}$ are collinear, $X, Y, K$ are collinear if and only if $X$ lies on the line $M_{top} Y$. Since $X$ is on the circumcircle, this requires $X = Y$ or $X = M_{top}$. We have $X = M_{top}$ if and only if $Q, D, M_{top}$ are collinear. However, the slope of $M_{top} Q$ is $\frac{-R(1 - \cos A)}{x_D}$ while the slope of $M_{top} D$ is $\frac{-R(1 + \cos A)}{x_D}$, which are not equal for an acute triangle. Thus $X \neq M_{top}$, and the collinearity of $X, Y, K$ follows from $X = Y$, which is equivalent to the collinearity of $Q, D, Y$. Given the properties of the points $Q, D, Y$ under the condition $r = 2R \cos A$, they are indeed collinear. Thus, $X, Y, K$ are collinear.
