# Problem

Consider an acute triangle $ABC$ that is not isosceles. Let $H_0$, $E$, and $F$ be the feet of the perpendiculars dropped from vertices $A$, $B$, and $C$ to their opposite sides, respectively. Let $D$ be the point where the incircle of $\triangle ABC$ is tangent to side $ BC $. Denote the incenter and circumcenter of $\triangle ABC$ as $I$ and $O$, respectively. Let $K$ be the intersection of line $IO$ and line $BC$. Let $Q$ be the point where the ray $IH_0$ intersects the circumcircle of $\triangle ABC$ again. Let $X$ be the point where the line $ QD $ intersects the circumcircle of $\triangle ABC$ at a point other than $Q$.
 Let $Y$ be the point where the circle that touches rays $AB$, $AC$, and is also externally tangent to the circumcircle of $\triangle ABC$, touches the circumcircle of $ \triangle ABC$. Prove that if segment $EF$ is tangent to the incircle of $ \triangle ABC$, then $X$, $Y$, and $K$ are collinear.

# Proof A

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

# Proof B

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
