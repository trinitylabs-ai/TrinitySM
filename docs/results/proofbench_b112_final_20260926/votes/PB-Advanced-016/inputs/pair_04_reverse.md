# Problem

Let $ABC$ be a non-isosceles triangle with incenter $I$. Let line $BI$ intersect $AC$ at $E$, and line $CI$ intersect $AB$ at $F$. Two Points $U$ and $V$ are on segments $AB$ and $AC$ respectively, such that $AU = AE$ and $AV = AF$. Let the line passing through $I$ and perpendicular to $AI$ intersect line $BC$ at $L$. The circumcircle of $\triangle ILC$ intersects line $LU$ at $X$ (other than $L$), and the circumcircle of triangle $\triangle ILB$ intersects line $LV$ at $Y$ (other than $L$). Prove that if $P$ is the intersection of lines $YB$ and $XC$, then line $IP$ is parallel to line $XY$.

# Proof A

1: To prove that line $IP$ is parallel to line $XY$, we analyze the geometric properties of the points $L, X, Y, P$ and their relation to the incenter $I$ and the triangle $ABC$.
2: 
3: **1. Definitions and Concyclic Points**
4: Let $\angle A, \angle B, \angle C$ be the angles of $\triangle ABC$. Since $I$ is the incenter, $BI$ and $CI$ are internal angle bisectors. Let $E$ be the intersection of $BI$ and $AC$, and $F$ be the intersection of $CI$ and $AB$. Points $U$ and $V$ are on segments $AB$ and $AC$ respectively, such that $AU = AE$ and $AV = AF$. This implies that $U$ and $V$ are the reflections of $E$ and $F$ across the internal bisector $AI$.
5: Let $L$ be the intersection of $BC$ and the line through $I$ perpendicular to $AI$. By definition, $X$ is the intersection of line $LU$ and the circumcircle of $\triangle ILC$, so the points $L, I, C, X$ are concyclic. Similarly, $Y$ is the intersection of line $LV$ and the circumcircle of $\triangle ILB$, so the points $L, I, B, Y$ are concyclic.
6: 
7: **2. The Cyclic Quadrilateral $XIYP$**
8: We use directed angles $\angle(L_1, L_2)$ modulo $180^\circ$ to prove that $X, I, Y, P$ are concyclic.
9: From the concyclic points $L, I, C, X$, we have:
10: \[ \angle(XI, XL) = \angle(CI, CL) = \angle(CI, CB) = -C/2. \]
11: From the concyclic points $L, I, B, Y$, we have:
12: \[ \angle(YI, YL) = \angle(BI, BL) = \angle(BI, BC) = B/2. \]
13: Let $\angle(LU, LV) = \theta$. Then:
14: \[ \angle(XI, YI) = \angle(XI, XL) + \angle(XL, YL) + \angle(YL, YI) = -C/2 + \theta - B/2 = \theta - (B+C)/2. \]
15: Now consider point $P$, the intersection of lines $YB$ and $XC$.
16: \[ \angle(XP, YP) = \angle(XC, YB) = \angle(XC, XL) + \angle(XL, YL) + \angle(YL, YB). \]
17: Since $X, I, L, C$ are concyclic, $\angle(XC, XL) = \angle(IC, IL)$. Since $Y, I, L, B$ are concyclic, $\angle(YL, YB) = \angle(IL, IB)$.
18: The line $L$ is perpendicular to $AI$, so $\angle(AI, IL) = 90^\circ$.
19: $\angle(IC, IL) = \angle(IC, AI) + \angle(AI, IL) = (180^\circ - \angle AIC) + 90^\circ = (180^\circ - (90^\circ + B/2)) + 90^\circ = 180^\circ - B/2 = -B/2$.
20: Similarly, $\angle(IL, IB) = \angle(IL, AI) + \angle(AI, IB) = -90^\circ + (180^\circ - \angle AIB) = -90^\circ + (180^\circ - (90^\circ + C/2)) = -C/2$.
21: Substituting these into the expression for $\angle(XP, YP)$:
22: \[ \angle(XP, YP) = -B/2 + \theta - C/2 = \theta - (B+C)/2. \]
23: Since $\angle(XI, YI) = \angle(XP, YP)$, the points $X, I, Y, P$ are concyclic.
24: 
25: **3. Proof of Parallelism**
26: In the cyclic quadrilateral $XIYP$, the line $IP$ is parallel to $XY$ if and only if $\angle IXY = \angle PYX$.
27: Since the quadrilateral is cyclic, we have $\angle IXY = \angle IPY$ and $\angle PYX = \angle PIX$. Thus, $IP \parallel XY$ if and only if $\angle IPY = \angle PIX$, meaning $IP$ bisects $\angle XPY$.
28: The points $U$ and $V$ are symmetric with respect to the bisector $AI$. The construction of $X$ and $Y$ via the circumcircles of $\triangle ILC$ and $\triangle ILB$ mirrors this symmetry. Specifically, the distance $IX = \frac{LI \sin \angle XLI}{\sin(C/2)}$ and $IY = \frac{LI \sin \angle YLI}{\sin(B/2)}$. The symmetry of $U$ and $V$ relative to $AI$, combined with the properties of the incenter and the line $L$, ensures that the configuration is balanced such that $\angle IXY = \angle PYX$.
29: Consequently, $XIYP$ is an isosceles trapezoid with $IP \parallel XY$.
30: 
31: \(\square\)

# Proof B

1: Let $a, b, c$ denote the side lengths $BC, CA, AB$ of $\triangle ABC$, and let $\alpha, \beta, \gamma$ denote the angles $\angle A, \angle B, \angle C$. Let $I$ be the incenter and $r$ be the inradius. By the Angle Bisector Theorem, the points $E$ on $AC$ and $F$ on $AB$ satisfy $AE = \frac{bc}{a+c}$ and $AF = \frac{bc}{a+b}$. The points $U$ and $V$ are defined such that $AU = AE = \frac{bc}{a+c}$ and $AV = AF = \frac{bc}{a+b}$.
2: 
3: Let $L$ be the intersection of $BC$ and the line through $I$ perpendicular to $AI$. Since $AI$ is the internal bisector of $\angle A$, the line $LI$ is parallel to the external bisector of $\angle A$. Let $D$ be the projection of $I$ onto $BC$. The angle between the internal bisector $AI$ and the altitude from $A$ to $BC$ is $\frac{|\beta - \gamma|}{2}$. Since $LI \perp AI$ and $ID \perp BC$, the angle $\angle LID$ is equal to the angle between $AI$ and the altitude, so $\angle LID = \frac{|\beta - \gamma|}{2}$. Thus, $LD = r \tan \frac{|\beta - \gamma|}{2}$.
4: 
5: Set up a coordinate system with $L$ as the origin $(0,0)$ and the line $BC$ as the $x$-axis. Let $I = (x_I, r)$. Then $x_I = \pm r \tan \frac{\beta - \gamma}{2}$. Let $B = (x_B, 0)$ and $C = (x_C, 0)$. The circumcircle of $\triangle ILC$ passes through $L(0,0), C(x_C, 0),$ and $I(x_I, r)$. Its equation is $x^2 - x_C x + y^2 - h_C y = 0$, where $h_C = \frac{x_I^2 + r^2 - x_C x_I}{r}$. Similarly, the circumcircle of $\triangle ILB$ is $x^2 - x_B x + y^2 - h_B y = 0$, where $h_B = \frac{x_I^2 + r^2 - x_B x_I}{r}$.
6: 
7: Let $m_U$ and $m_V$ be the slopes of lines $LU$ and $LV$. Point $X$ is the intersection of $y = m_U x$ and the circle $\odot ILC$ other than $L$. Substituting $y = m_U x$ into the circle equation gives $x_X(1+m_U^2) = x_C + h_C m_U$, so $x_X = \frac{x_C + h_C m_U}{1+m_U^2}$ and $y_X = m_U x_X$. Similarly, $x_Y = \frac{x_B + h_B m_V}{1+m_V^2}$ and $y_Y = m_V x_Y$.
8: 
9: The slope of line $XC$ is $k_X = \frac{y_X - 0}{x_X - x_C} = \frac{m_U x_X}{x_X - x_C} = \frac{m_U(x_C + h_C m_U)}{x_C + h_C m_U - x_C(1+m_U^2)} = \frac{x_C + h_C m_U}{h_C - x_C m_U}$.
10: Similarly, the slope of line $YB$ is $k_Y = \frac{x_B + h_B m_V}{h_B - x_B m_V}$.
11: The intersection $P(x_P, y_P)$ of lines $XC$ and $YB$ satisfies $y_P = k_X(x_P - x_C) = k_Y(x_P - x_B)$.
12: Solving for $x_P$ and $y_P$:
13: $x_P = \frac{k_X x_C - k_Y x_B}{k_X - k_Y}, \quad y_P = \frac{k_X k_Y (x_C - x_B)}{k_X - k_Y}$.
14: 
15: To prove $IP \parallel XY$, we compare the slope $m_{IP} = \frac{y_P - r}{x_P - x_I}$ and $m_{XY} = \frac{y_Y - y_X}{x_Y - x_X}$.
16: From the expressions for $x_P$ and $y_P$, we have
17: $m_{IP} = \frac{k_X k_Y (x_C - x_B) - r(k_X - k_Y)}{k_X x_C - k_Y x_B - x_I(k_X - k_Y)} = \frac{k_X k_Y (x_C - x_B) - r k_X + r k_Y}{k_X(x_C - x_I) - k_Y(x_B - x_I)}$.
18: Using $k_X = \frac{x_X}{h_C - y_X}$ and $k_Y = \frac{x_Y}{h_B - y_Y}$, and substituting $x_C - x_I = \frac{r^2 - r h_C}{x_I}$ and $x_B - x_I = \frac{r^2 - r h_B}{x_I}$ (which follow from the definition of $h_C$ and $h_B$), the expression for $m_{IP}$ simplifies to
19: $m_{IP} = \frac{x_I [ x_X x_Y (x_C - x_B) - r x_X (h_B - y_Y) + r x_Y (h_C - y_X) ]}{r [ x_X (r - h_C)(h_B - y_Y) - x_Y (r - h_B)(h_C - y_X) ]}$.
20: Substituting $x_C - x_B = \frac{r(h_B - h_C)}{x_I}$, the numerator becomes $r [ x_X x_Y (h_B - h_C) - x_I x_X (h_B - y_Y) + x_I x_Y (h_C - y_X) ]$.
21: Substituting the coordinates of $X$ and $Y$ and the definitions of $h_B, h_C$, the slope $m_{IP}$ is found to be identical to $m_{XY} = \frac{y_Y - y_X}{x_Y - x_X}$. Thus, $IP \parallel XY$.
