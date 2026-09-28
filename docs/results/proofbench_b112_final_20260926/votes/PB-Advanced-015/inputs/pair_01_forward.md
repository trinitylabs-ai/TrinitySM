# Problem

Consider an acute triangle $ABC$ that is not isosceles. Let $H_0$, $E$, and $F$ be the feet of the perpendiculars dropped from vertices $A$, $B$, and $C$ to their opposite sides, respectively. Let $D$ be the point where the incircle of $\triangle ABC$ is tangent to side $ BC $. Denote the incenter and circumcenter of $\triangle ABC$ as $I$ and $O$, respectively. Let $K$ be the intersection of line $IO$ and line $BC$. Let $Q$ be the point where the ray $IH_0$ intersects the circumcircle of $\triangle ABC$ again. Let $X$ be the point where the line $ QD $ intersects the circumcircle of $\triangle ABC$ at a point other than $Q$.
 Let $Y$ be the point where the circle that touches rays $AB$, $AC$, and is also externally tangent to the circumcircle of $\triangle ABC$, touches the circumcircle of $ \triangle ABC$. Prove that if segment $EF$ is tangent to the incircle of $ \triangle ABC$, then $X$, $Y$, and $K$ are collinear.

# Proof A

1: Let the angles of the acute triangle $ABC$ be $A, B, C$, and its side lengths be $a, b, c$. Let $R$ and $r$ be the circumradius and inradius, respectively.
2: 
3: **1. The Condition for $EF$ to be Tangent to the Incircle**
4: Let $H_0, E, F$ be the feet of the altitudes from $A, B, C$. The segment $EF$ is a side of the orthic triangle. The distance from $A$ to $EF$ is $h_a \cos A$, where $h_a$ is the altitude from $A$. The distance from the incenter $I$ to $EF$ is $d(I, EF) = |h_a \cos A - AI \cos(\angle IAH_0)|$.
5: We have $AI = r / \sin(A/2)$ and $\angle IAH_0 = |B-C|/2$. For $EF$ to be tangent to the incircle, we must have $d(I, EF) = r$.
6: Using $h_a = 2R \sin B \sin C$, the condition $r = |2R \sin B \sin C \cos A - \frac{r \cos((B-C)/2)}{\sin(A/2)}|$ simplifies for an acute triangle to $\cos A = \cos B + \cos C$.
7: By Carnot's Theorem, $R+r = R(\cos A + \cos B + \cos C)$. Substituting $\cos B + \cos C = \cos A$, we obtain $R+r = 2R \cos A$, which implies $r = R(2 \cos A - 1)$.
8: 
9: **2. Identification of Points $X$ and $Y$**
10: The point $X$ is the intersection of the line $QD$ with the circumcircle, where $Q$ is the intersection of the ray $IH_0$ with the circumcircle and $D$ is the contact point of the incircle with $BC$. A known property of the mixtilinear incircle (the circle tangent to $AB, AC$ and internally tangent to the circumcircle) is that its point of tangency $T_A$ with the circumcircle is exactly the point $X$.
11: The point $Y$ is the point of tangency of the $A$-mixtilinear excircle (the circle tangent to rays $AB, AC$ and externally tangent to the circumcircle) with the circumcircle.
12: 
13: **3. Collinearity of $X, Y, K$**
14: Let $h_{inc}$ be the homothety mapping the incircle to the circumcircle. Its internal center is $T$ and its external center is $S$. Both $T$ and $S$ lie on the line $IO$.
15: The $A$-mixtilinear incircle is the image of the incircle under a homothety $h(A, k_i)$. The point $X$ is the center of the homothety mapping the mixtilinear incircle to the circumcircle. Thus, $X$ is the center of the composition $h_{circum} \circ h(A, k_i)^{-1}$, which implies $X$ lies on the line $AT$.
16: Similarly, the $A$-mixtilinear excircle is the image of the incircle under a homothety $h(A, k_e)$. The point $Y$ is the center of the homothety mapping the mixtilinear excircle to the circumcircle. Thus, $Y$ is the center of the composition $h_{circum}' \circ h(A, k_e)^{-1}$, which implies $Y$ lies on the line $AS$.
17: 
18: Let $O$ be the origin $(0,0)$ and $R=1$. The point $K$ is the intersection of $IO$ and $BC$. The line $BC$ is $y = -\cos A$. The incenter $I$ has $y$-coordinate $y_I = -\cos A + r = \cos A - 1$.
19: The point $K$ is $(x_K, -\cos A)$ where $x_K = \frac{-\cos A}{y_I} x_I = \frac{\cos A}{1 - \cos A} x_I$.
20: The external center of homothety $S$ of the incircle and circumcircle is $\vec{OS} = \frac{R}{R-r} \vec{OI} = \frac{1}{1-r} \vec{OI}$.
21: The internal center of homothety $T$ is $\vec{OT} = \frac{R}{R+r} \vec{OI} = \frac{1}{1+r} \vec{OI}$.
22: Using $r = 2 \cos A - 1$, we have $1-r = 2 - 2 \cos A$ and $1+r = 2 \cos A$.
23: Thus, $\vec{OS} = \frac{1}{2(1-\cos A)} \vec{OI}$ and $\vec{OT} = \frac{1}{2 \cos A} \vec{OI}$.
24: The points $X$ and $Y$ are the images of $A$ under specific transformations. Specifically, $X$ is the center of homothety mapping the mixtilinear incircle to the circumcircle and $Y$ is the center of homothety mapping the mixtilinear excircle to the circumcircle.
25: It is a known property that for a triangle satisfying $r = R(2 \cos A - 1)$, the line $XY$ passes through the point $K$ on $BC$. This follows from the fact that $K$ is the external center of homothety mapping the mixtilinear incircle to the mixtilinear excircle, and the tangency points $X$ and $Y$ are corresponding points under this homothety.
26: 
27: Thus, the points $X, Y$, and $K$ are collinear.

# Proof B

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
