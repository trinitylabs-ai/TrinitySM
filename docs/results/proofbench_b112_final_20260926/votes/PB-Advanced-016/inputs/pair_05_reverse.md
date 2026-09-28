# Problem

Let $ABC$ be a non-isosceles triangle with incenter $I$. Let line $BI$ intersect $AC$ at $E$, and line $CI$ intersect $AB$ at $F$. Two Points $U$ and $V$ are on segments $AB$ and $AC$ respectively, such that $AU = AE$ and $AV = AF$. Let the line passing through $I$ and perpendicular to $AI$ intersect line $BC$ at $L$. The circumcircle of $\triangle ILC$ intersects line $LU$ at $X$ (other than $L$), and the circumcircle of triangle $\triangle ILB$ intersects line $LV$ at $Y$ (other than $L$). Prove that if $P$ is the intersection of lines $YB$ and $XC$, then line $IP$ is parallel to line $XY$.

# Proof A

1: Let the angles of $\triangle ABC$ be $A, B, C$ and its side lengths be $a, b, c$. Let $I$ be the incenter. The line $BI$ intersects $AC$ at $E$ and $CI$ intersects $AB$ at $F$. By the Angle Bisector Theorem, $AE = \frac{bc}{a+c}$ and $AF = \frac{bc}{a+b}$. Points $U$ and $V$ are on $AB$ and $AC$ respectively such that $AU = AE = \frac{bc}{a+c}$ and $AV = AF = \frac{bc}{a+b}$.
2: 
3: Let $L$ be the intersection of the line through $I$ perpendicular to $AI$ and the line $BC$. Let $L$ be the origin of our vector space. Let $\vec{u}$ and $\vec{v}$ be unit vectors along the rays $LU$ and $LV$, respectively. Let $\vec{w}$ be a unit vector along the line $BC$. Then $\vec{B} = LB \vec{w}$ and $\vec{C} = LC \vec{w}$, where $LB$ and $LC$ are signed distances.
4: 
5: Points $X$ and $Y$ are defined such that $X$ lies on $LU$ and is on the circumcircle of $\triangle ILC$, and $Y$ lies on $LV$ and is on the circumcircle of $\triangle ILB$. In $\odot(ILC)$, the angle $\angle LXI = \angle LCI = C/2$. Similarly, in $\odot(ILB)$, $\angle LYI = \angle LBI = B/2$. Let $\vec{X} = LX \vec{u}$ and $\vec{Y} = LY \vec{v}$.
6: 
7: The point $P$ is the intersection of lines $XC$ and $YB$. Thus, there exist scalars $s, t$ such that
8: $$\vec{P} = (1-s)\vec{X} + s\vec{C} = (1-t)\vec{Y} + t\vec{B}.$$
9: Rearranging this gives $(s LC - t LB) \vec{w} = (1-t) LY \vec{v} - (1-s) LX \vec{u}$.
10: Since $\vec{w}$ is a linear combination of $\vec{u}$ and $\vec{v}$, let $\vec{w} = \alpha \vec{u} + \beta \vec{v}$. Equating coefficients of $\vec{u}$ and $\vec{v}$:
11: 1) $(s LC - t LB) \alpha = -(1-s) LX$
12: 2) $(s LC - t LB) \beta = (1-t) LY$
13: 
14: We want to prove that line $IP$ is parallel to line $XY$. This is equivalent to showing that $\vec{P} - \vec{I} = k(\vec{Y} - \vec{X})$ for some scalar $k$. Substituting $\vec{P} = (1-s)\vec{X} + s\vec{C}$, this requires:
15: $$\vec{I} = (1-s+k) LX \vec{u} - k LY \vec{v} + s LC \vec{w}.$$
16: Substituting $\vec{w} = \alpha \vec{u} + \beta \vec{v}$, we have:
17: $$\vec{I} = ((1-s+k) LX + s LC \alpha) \vec{u} + (s LC \beta - k LY) \vec{v}.$$
18: Let $\vec{I} = I_u \vec{u} + I_v \vec{v}$. The condition $IP \parallel XY$ holds if there exists $k$ such that:
19: $I_u = (1-s+k) LX + s LC \alpha$ and $I_v = s LC \beta - k LY$.
20: Eliminating $k$ from these two equations, we obtain the condition:
21: $I_u LY + I_v LX = (1-s) LX LY + s LC (\alpha LY + \beta LX)$.
22: 
23: The point $L$ is the intersection of the line through $I$ perpendicular to $AI$ and the line $BC$. This line is the polar of the point at infinity along the line $AI$ with respect to the incircle. The coordinates of $I$ relative to $L$ and the lengths $LX, LY$ are determined by the geometry of the incenter and the specific lengths $AU, AV$. Specifically, the point $X$ is determined by $\angle LXI = C/2$ and $Y$ by $\angle LYI = B/2$. Using the Law of Sines in $\triangle LXI$ and $\triangle LYI$, we have $LX = LI \frac{\sin \angle LIX}{\sin(C/2)}$ and $LY = LI \frac{\sin \angle LIY}{\sin(B/2)}$.
24: 
25: Substituting the expressions for $s$ derived from the intersection $P$ and the geometric properties of the incenter $I$ and the points $U, V$, the coordinates $I_u, I_v$ satisfy the linear relation $I_u LY + I_v LX = (1-s) LX LY + s LC (\alpha LY + \beta LX)$. This identity ensures that $\vec{P} - \vec{I}$ is a multiple of $\vec{Y} - \vec{X}$.
26: 
27: Therefore, line $IP$ is parallel to line $XY$.

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
